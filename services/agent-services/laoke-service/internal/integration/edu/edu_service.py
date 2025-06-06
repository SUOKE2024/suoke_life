"""
edu_service - 索克生活项目模块
"""

from pkg.utils.cache import AsyncCacheClient
from pkg.utils.config import Config
from pkg.utils.metrics import timed_and_counted_function
from typing import Any
import httpx
import json
import logging
import time

#!/usr/bin/env python

"""
教育服务集成模块
负责与外部教育服务和资源的集成
"""




# 获取日志记录器
logger = logging.getLogger(__name__)

# 配置
config = Config()


class EducationService:
    """
    教育服务集成
    提供课程推荐、学习路径生成和教育内容获取功能
    """

    def __init__(self, cache_client: AsyncCacheClient | None = None):
        """
        初始化教育服务

        参数:
            cache_client: 缓存客户端（可选）
        """
        self.config = config

        # 获取教育服务配置
        self.edu_api_url = self.config.get("integration.edu.api_url", "")
        self.edu_api_key = self.config.get("integration.edu.api_key", "")
        self.request_timeout = self.config.get("integration.edu.timeout", 10)

        # 缓存设置
        self.cache_ttl = self.config.get("integration.edu.cache_ttl", 3600)  # 默认1小时缓存
        self.cache_enabled = self.config.get("integration.edu.cache_enabled", True)
        self.cache_client = cache_client
        self.cache_prefix = "edu_service:"

        # 课程类型和难度级别配置
        self.course_types = self.config.get("integration.edu.course_types",
                                          ["tcm_basic", "tcm_advanced", "health_living",
                                           "nutrition", "exercise", "meditation"])
        self.difficulty_levels = self.config.get("integration.edu.difficulty_levels",
                                               ["beginner", "intermediate", "advanced", "expert"])

    async def _get_from_cache(self, key: str) -> Any | None:
        """
        从缓存获取数据

        参数:
            key: 缓存键

        返回:
            缓存的数据，如果不存在则为None
        """
        if not self.cache_enabled or not self.cache_client:
            return None

        cache_key = f"{self.cache_prefix}{key}"
        try:
            cached_data = await self.cache_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"从缓存获取数据失败: {str(e)}")

        return None

    async def _save_to_cache(self, key: str, data: Any, ttl: int | None = None) -> bool:
        """
        保存数据到缓存

        参数:
            key: 缓存键
            data: 要缓存的数据
            ttl: 缓存生存时间（秒）

        返回:
            是否成功保存
        """
        if not self.cache_enabled or not self.cache_client:
            return False

        cache_key = f"{self.cache_prefix}{key}"
        ttl = ttl or self.cache_ttl

        try:
            await self.cache_client.set(cache_key, json.dumps(data), ttl)
            return True
        except Exception as e:
            logger.warning(f"保存数据到缓存失败: {str(e)}")
            return False

    async def _make_api_request(self, endpoint: str, method: str = "GET", params: dict | None = None,
                               data: dict | None = None) -> dict:
        """
        发送API请求

        参数:
            endpoint: API端点
            method: HTTP方法
            params: 查询参数
            data: 请求数据

        返回:
            API响应数据
        """
        url = f"{self.edu_api_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.edu_api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        async with httpx.AsyncClient(timeout=self.request_timeout) as client:
            try:
                if method.upper() == "GET":
                    response = await client.get(url, params=params, headers=headers)
                elif method.upper() == "POST":
                    response = await client.post(url, json=data, headers=headers)
                else:
                    raise ValueError(f"不支持的HTTP方法: {method}")

                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"教育服务API返回错误状态码: {e.response.status_code} - {e.response.text}")
                raise
            except httpx.RequestError as e:
                logger.error(f"请求教育服务API失败: {str(e)}")
                raise

    @timed_and_counted_function("edu_get_course_recommendations")
    async def get_course_recommendations(self, user_id: str, interests: list[str],
                                      prev_courses: list[str] | None = None,
                                      limit: int = 5) -> list[dict]:
        """
        获取课程推荐

        参数:
            user_id: 用户ID
            interests: 用户兴趣列表
            prev_courses: 之前完成的课程ID列表
            limit: 返回结果限制

        返回:
            推荐课程列表
        """
        # 尝试从缓存获取
        cache_key = f"course_rec:{user_id}:{'-'.join(sorted(interests))}:{limit}"
        cached_data = await self._get_from_cache(cache_key)
        if cached_data:
            return cached_data

        # 构建请求参数
        params = {
            "user_id": user_id,
            "interests": interests,
            "limit": limit
        }

        if prev_courses:
            params["prev_courses"] = prev_courses

        # 发送API请求
        try:
            response_data = await self._make_api_request("/v1/courses/recommendations",
                                                      method="GET", params=params)
            courses = response_data.get("courses", [])

            # 保存到缓存（较短时间，因为推荐可能会变）
            await self._save_to_cache(cache_key, courses, ttl=1800)  # 30分钟缓存

            return courses
        except Exception as e:
            logger.error(f"获取课程推荐失败: {str(e)}")
            # 如果API请求失败但有缓存，返回缓存版本
            if cached_data:
                logger.info("返回缓存的课程推荐")
                return cached_data
            # 否则返回空列表
            return []

    @timed_and_counted_function("edu_generate_learning_path")
    async def generate_learning_path(self, user_id: str, goal: str,
                                  current_level: str = "beginner",
                                  time_frame: str | None = None) -> dict:
        """
        生成学习路径

        参数:
            user_id: 用户ID
            goal: 学习目标
            current_level: 当前水平
            time_frame: 时间框架（如"3-months", "6-months"等）

        返回:
            学习路径信息
        """
        # 验证current_level
        if current_level not in self.difficulty_levels:
            current_level = "beginner"

        # 构建请求体
        request_data = {
            "user_id": user_id,
            "goal": goal,
            "current_level": current_level
        }

        if time_frame:
            request_data["time_frame"] = time_frame

        # 尝试从缓存获取
        cache_key = f"learning_path:{user_id}:{goal}:{current_level}:{time_frame}"
        cached_data = await self._get_from_cache(cache_key)
        if cached_data:
            return cached_data

        # 发送API请求
        try:
            response_data = await self._make_api_request("/v1/learning/path/generate",
                                                      method="POST", data=request_data)

            # 保存到缓存（较长时间，因为学习路径不会频繁变化）
            await self._save_to_cache(cache_key, response_data, ttl=86400)  # 24小时缓存

            return response_data
        except Exception as e:
            logger.error(f"生成学习路径失败: {str(e)}")
            # 如果API请求失败但有缓存，返回缓存版本
            if cached_data:
                logger.info("返回缓存的学习路径")
                return cached_data
            # 否则返回空字典
            return {
                "path_id": None,
                "modules": [],
                "estimated_duration": None,
                "difficulty": current_level
            }

    @timed_and_counted_function("edu_get_course_details")
    async def get_course_details(self, course_id: str) -> dict:
        """
        获取课程详情

        参数:
            course_id: 课程ID

        返回:
            课程详细信息
        """
        # 尝试从缓存获取
        cache_key = f"course:{course_id}"
        cached_data = await self._get_from_cache(cache_key)
        if cached_data:
            return cached_data

        # 发送API请求
        try:
            response_data = await self._make_api_request(f"/v1/courses/{course_id}", method="GET")

            # 保存到缓存（较长时间，因为课程内容不会频繁变化）
            await self._save_to_cache(cache_key, response_data, ttl=86400)  # 24小时缓存

            return response_data
        except Exception as e:
            logger.error(f"获取课程详情失败: {str(e)}")
            # 如果API请求失败但有缓存，返回缓存版本
            if cached_data:
                logger.info("返回缓存的课程详情")
                return cached_data
            # 否则返回空字典
            return {}

    @timed_and_counted_function("edu_search_courses")
    async def search_courses(self, query: str, course_type: str | None = None,
                          difficulty: str | None = None, limit: int = 10) -> list[dict]:
        """
        搜索课程

        参数:
            query: 搜索查询
            course_type: 课程类型
            difficulty: 难度级别
            limit: 返回结果限制

        返回:
            符合条件的课程列表
        """
        # 验证课程类型和难度
        if course_type and course_type not in self.course_types:
            course_type = None
        if difficulty and difficulty not in self.difficulty_levels:
            difficulty = None

        # 构建请求参数
        params = {
            "q": query,
            "limit": limit
        }

        if course_type:
            params["type"] = course_type
        if difficulty:
            params["difficulty"] = difficulty

        # 尝试从缓存获取
        cache_key = f"course_search:{query}:{course_type}:{difficulty}:{limit}"
        cached_data = await self._get_from_cache(cache_key)
        if cached_data:
            return cached_data

        # 发送API请求
        try:
            response_data = await self._make_api_request("/v1/courses/search", method="GET", params=params)
            courses = response_data.get("results", [])

            # 保存到缓存（较短时间，因为搜索结果可能会变化）
            await self._save_to_cache(cache_key, courses, ttl=3600)  # 1小时缓存

            return courses
        except Exception as e:
            logger.error(f"搜索课程失败: {str(e)}")
            # 如果API请求失败但有缓存，返回缓存版本
            if cached_data:
                logger.info("返回缓存的搜索结果")
                return cached_data
            # 否则返回空列表
            return []

    @timed_and_counted_function("edu_get_educational_content")
    async def get_educational_content(self, content_type: str, topic: str,
                                   format_type: str = "article") -> dict:
        """
        获取教育内容

        参数:
            content_type: 内容类型（如"tcm", "nutrition", "exercise"等）
            topic: 主题
            format_type: 格式类型（"article", "video", "interactive"）

        返回:
            教育内容
        """
        # 构建请求参数
        params = {
            "content_type": content_type,
            "topic": topic,
            "format": format_type
        }

        # 尝试从缓存获取
        cache_key = f"edu_content:{content_type}:{topic}:{format_type}"
        cached_data = await self._get_from_cache(cache_key)
        if cached_data:
            return cached_data

        # 发送API请求
        try:
            response_data = await self._make_api_request("/v1/content/educational",
                                                      method="GET", params=params)

            # 保存到缓存
            await self._save_to_cache(cache_key, response_data, ttl=86400)  # 24小时缓存

            return response_data
        except Exception as e:
            logger.error(f"获取教育内容失败: {str(e)}")
            # 如果API请求失败但有缓存，返回缓存版本
            if cached_data:
                logger.info("返回缓存的教育内容")
                return cached_data
            # 否则返回空字典
            return {
                "title": None,
                "content": None,
                "format": format_type,
                "type": content_type,
                "topic": topic
            }

    @timed_and_counted_function("edu_track_learning_progress")
    async def track_learning_progress(self, user_id: str, course_id: str,
                                   progress: float, completed: bool = False) -> bool:
        """
        跟踪学习进度

        参数:
            user_id: 用户ID
            course_id: 课程ID
            progress: 进度百分比（0-100）
            completed: 是否已完成

        返回:
            是否成功更新
        """
        # 构建请求体
        request_data = {
            "user_id": user_id,
            "course_id": course_id,
            "progress": progress,
            "completed": completed,
            "timestamp": int(time.time())
        }

        # 发送API请求
        try:
            await self._make_api_request("/v1/learning/progress/track",
                                      method="POST", data=request_data)
            return True
        except Exception as e:
            logger.error(f"跟踪学习进度失败: {str(e)}")
            return False

    @timed_and_counted_function("edu_get_learning_statistics")
    async def get_learning_statistics(self, user_id: str) -> dict:
        """
        获取学习统计信息

        参数:
            user_id: 用户ID

        返回:
            学习统计信息
        """
        # 尝试从缓存获取
        cache_key = f"learning_stats:{user_id}"
        cached_data = await self._get_from_cache(cache_key)
        if cached_data:
            return cached_data

        # 发送API请求
        try:
            response_data = await self._make_api_request(f"/v1/learning/statistics/{user_id}",
                                                     method="GET")

            # 保存到缓存（较短时间，因为统计信息会变化）
            await self._save_to_cache(cache_key, response_data, ttl=900)  # 15分钟缓存

            return response_data
        except Exception as e:
            logger.error(f"获取学习统计信息失败: {str(e)}")
            # 如果API请求失败但有缓存，返回缓存版本
            if cached_data:
                logger.info("返回缓存的学习统计信息")
                return cached_data
            # 否则返回空字典
            return {
                "courses_started": 0,
                "courses_completed": 0,
                "total_learning_time": 0,
                "average_completion_rate": 0,
                "learning_streak": 0,
                "last_active": None
            }
