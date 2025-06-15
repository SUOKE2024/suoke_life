#!/usr/bin/env python

"""
记忆辅助服务实现
为认知障碍用户提供记忆支持和认知辅助功能
"""

import asyncio
import json
import logging
import uuid
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

from ..decorators import error_handler, performance_monitor
from ..interfaces import ICacheManager, IMemoryAssistanceService, IModelManager

logger = logging.getLogger(__name__)


class MemoryType(Enum):
    """记忆类型"""

    SHORT_TERM = "short_term"  # 短期记忆
    LONG_TERM = "long_term"  # 长期记忆
    WORKING = "working"  # 工作记忆
    EPISODIC = "episodic"  # 情景记忆
    SEMANTIC = "semantic"  # 语义记忆
    PROCEDURAL = "procedural"  # 程序性记忆


class ReminderType(Enum):
    """提醒类型"""

    MEDICATION = "medication"  # 用药提醒
    APPOINTMENT = "appointment"  # 预约提醒
    TASK = "task"  # 任务提醒
    PERSON = "person"  # 人物提醒
    LOCATION = "location"  # 位置提醒
    EVENT = "event"  # 事件提醒
    ROUTINE = "routine"  # 日常提醒


class CognitiveLevel(Enum):
    """认知水平"""

    NORMAL = "normal"  # 正常
    MILD_IMPAIRMENT = "mild"  # 轻度障碍
    MODERATE_IMPAIRMENT = "moderate"  # 中度障碍
    SEVERE_IMPAIRMENT = "severe"  # 重度障碍


class AssistanceMode(Enum):
    """辅助模式"""

    PROACTIVE = "proactive"  # 主动提醒
    REACTIVE = "reactive"  # 被动响应
    ADAPTIVE = "adaptive"  # 自适应
    SCHEDULED = "scheduled"  # 定时提醒


class MemoryAssistanceServiceImpl(IMemoryAssistanceService):
    """
    记忆辅助服务实现类
    """

    def __init__(
        self,
        model_manager: IModelManager,
        cache_manager: ICacheManager,
        enabled: bool = True,
        max_concurrent_users: int = 100,
    ):
        """
        初始化记忆辅助服务

        Args:
            model_manager: AI模型管理器
            cache_manager: 缓存管理器
            enabled: 是否启用服务
            max_concurrent_users: 最大并发用户数
        """
        self.model_manager = model_manager
        self.cache_manager = cache_manager
        self.enabled = enabled
        self.max_concurrent_users = max_concurrent_users

        # 并发控制
        self._semaphore = asyncio.Semaphore(max_concurrent_users)

        # 服务状态
        self._initialized = False
        self._request_count = 0
        self._error_count = 0

        # 用户会话管理
        self._active_users = {}

        # AI模型
        self._memory_analysis_model = None
        self._cognitive_assessment_model = None
        self._reminder_optimization_model = None
        self._pattern_recognition_model = None

        # 记忆数据存储
        self._memory_database = {}

        # 提醒调度器
        self._reminder_scheduler = {}

        # 认知训练模块
        self._cognitive_exercises = {
            "attention": [
                {"name": "数字序列", "difficulty": 1, "type": "sequence"},
                {"name": "颜色匹配", "difficulty": 2, "type": "matching"},
                {"name": "空间定位", "difficulty": 3, "type": "spatial"},
            ],
            "memory": [
                {"name": "词汇记忆", "difficulty": 1, "type": "verbal"},
                {"name": "图像记忆", "difficulty": 2, "type": "visual"},
                {"name": "故事回忆", "difficulty": 3, "type": "narrative"},
            ],
            "executive": [
                {"name": "任务规划", "difficulty": 1, "type": "planning"},
                {"name": "问题解决", "difficulty": 2, "type": "problem_solving"},
                {"name": "决策制定", "difficulty": 3, "type": "decision_making"},
            ],
        }

        logger.info("记忆辅助服务初始化完成")

    async def initialize(self):
        """初始化服务"""
        if self._initialized:
            return

        try:
            if not self.enabled:
                logger.info("记忆辅助服务已禁用")
                return

            # 加载AI模型
            await self._load_memory_models()

            # 初始化提醒调度器
            await self._initialize_reminder_scheduler()

            # 启动后台任务
            await self._start_background_tasks()

            self._initialized = True
            logger.info("记忆辅助服务初始化成功")

        except Exception as e:
            logger.error(f"记忆辅助服务初始化失败: {e!s}")
            raise

    async def _load_memory_models(self):
        """加载记忆相关AI模型"""
        try:
            # 记忆分析模型
            self._memory_analysis_model = await self.model_manager.load_model(
                "memory_analysis", "cognitive_memory_analyzer"
            )

            # 认知评估模型
            self._cognitive_assessment_model = await self.model_manager.load_model(
                "cognitive_assessment", "neuropsychological_evaluator"
            )

            # 提醒优化模型
            self._reminder_optimization_model = await self.model_manager.load_model(
                "reminder_optimization", "adaptive_reminder_system"
            )

            # 模式识别模型
            self._pattern_recognition_model = await self.model_manager.load_model(
                "pattern_recognition", "behavioral_pattern_detector"
            )

            logger.info("记忆辅助AI模型加载完成")

        except Exception as e:
            logger.warning(f"记忆辅助模型加载失败: {e!s}")

    async def _initialize_reminder_scheduler(self):
        """初始化提醒调度器"""
        try:
            # 在实际实现中，这里应该初始化定时任务调度器
            # 例如：APScheduler、Celery等
            logger.info("提醒调度器初始化完成")

        except Exception as e:
            logger.warning(f"提醒调度器初始化失败: {e!s}")

    async def _start_background_tasks(self):
        """启动后台任务"""
        try:
            # 启动提醒检查任务
            asyncio.create_task(self._reminder_check_loop())

            # 启动记忆分析任务
            asyncio.create_task(self._memory_analysis_loop())

            # 启动认知评估任务
            asyncio.create_task(self._cognitive_assessment_loop())

            logger.info("记忆辅助后台任务启动完成")

        except Exception as e:
            logger.warning(f"启动后台任务失败: {e!s}")

    @performance_monitor
    @error_handler
    async def create_user_profile(
        self,
        user_id: str,
        cognitive_level: CognitiveLevel,
        memory_preferences: dict[str, Any],
        medical_info: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """
        创建用户认知档案

        Args:
            user_id: 用户ID
            cognitive_level: 认知水平
            memory_preferences: 记忆偏好设置
            medical_info: 医疗信息

        Returns:
            档案创建结果
        """
        async with self._semaphore:
            self._request_count += 1

            try:
                # 检查服务状态
                if not self._initialized:
                    await self.initialize()

                # 创建用户档案
                user_profile = {
                    "user_id": user_id,
                    "cognitive_level": cognitive_level.value,
                    "memory_preferences": memory_preferences,
                    "medical_info": medical_info or {},
                    "created_at": datetime.now(UTC).isoformat(),
                    "last_updated": datetime.now(UTC).isoformat(),
                    "assessment_history": [],
                    "memory_patterns": {},
                    "reminder_settings": {
                        "default_advance_time": 15,  # 分钟
                        "repeat_interval": 5,  # 分钟
                        "max_repeats": 3,
                        "preferred_modalities": ["visual", "audio"],
                        "quiet_hours": {"start": "22:00", "end": "08:00"},
                    },
                }

                # 保存用户档案
                await self._save_user_profile(user_profile)

                # 初始化用户记忆数据库
                await self._initialize_user_memory_database(user_id)

                # 添加到活跃用户
                self._active_users[user_id] = {
                    "profile": user_profile,
                    "session_start": datetime.now(UTC),
                    "last_activity": datetime.now(UTC),
                }

                logger.info(f"用户认知档案创建成功: {user_id}")

                return {
                    "success": True,
                    "user_id": user_id,
                    "cognitive_level": cognitive_level.value,
                    "message": "用户认知档案创建成功",
                }

            except Exception as e:
                self._error_count += 1
                logger.error(f"创建用户认知档案失败: {e!s}")
                return {
                    "success": False,
                    "error": str(e),
                    "message": f"创建用户认知档案失败: {e!s}",
                }

    async def _save_user_profile(self, profile: dict[str, Any]):
        """保存用户档案"""
        try:
            profile_key = f"memory_profile:{profile['user_id']}"
            await self.cache_manager.set(
                profile_key, json.dumps(profile), ttl=86400 * 365  # 保存1年
            )

        except Exception as e:
            logger.warning(f"保存用户档案失败: {e!s}")

    async def _initialize_user_memory_database(self, user_id: str):
        """初始化用户记忆数据库"""
        try:
            memory_db = {
                "user_id": user_id,
                "memories": {
                    MemoryType.SHORT_TERM.value: [],
                    MemoryType.LONG_TERM.value: [],
                    MemoryType.WORKING.value: [],
                    MemoryType.EPISODIC.value: [],
                    MemoryType.SEMANTIC.value: [],
                    MemoryType.PROCEDURAL.value: [],
                },
                "associations": {},
                "retrieval_patterns": {},
                "created_at": datetime.now(UTC).isoformat(),
            }

            memory_key = f"memory_database:{user_id}"
            await self.cache_manager.set(
                memory_key, json.dumps(memory_db), ttl=86400 * 365  # 保存1年
            )

            self._memory_database[user_id] = memory_db

        except Exception as e:
            logger.warning(f"初始化用户记忆数据库失败: {e!s}")

    @performance_monitor
    @error_handler
    async def store_memory(
        self,
        user_id: str,
        memory_content: dict[str, Any],
        memory_type: MemoryType,
        importance_level: int = 5,
    ) -> dict[str, Any]:
        """
        存储记忆信息

        Args:
            user_id: 用户ID
            memory_content: 记忆内容
            memory_type: 记忆类型
            importance_level: 重要性级别 (1-10)

        Returns:
            存储结果
        """
        try:
            # 获取用户记忆数据库
            memory_db = await self._get_user_memory_database(user_id)
            if not memory_db:
                return {"success": False, "message": "用户记忆数据库不存在"}

            # 创建记忆条目
            memory_entry = {
                "id": str(uuid.uuid4()),
                "content": memory_content,
                "type": memory_type.value,
                "importance": importance_level,
                "created_at": datetime.now(UTC).isoformat(),
                "last_accessed": datetime.now(UTC).isoformat(),
                "access_count": 0,
                "tags": memory_content.get("tags", []),
                "context": memory_content.get("context", {}),
                "associations": [],
            }

            # 分析记忆内容
            if self._memory_analysis_model:
                analysis_result = await self._analyze_memory_content(memory_entry)
                memory_entry["analysis"] = analysis_result

            # 存储记忆
            memory_db["memories"][memory_type.value].append(memory_entry)

            # 创建关联
            await self._create_memory_associations(user_id, memory_entry, memory_db)

            # 保存更新的记忆数据库
            await self._save_memory_database(user_id, memory_db)

            logger.info(f"记忆存储成功: 用户={user_id}, 类型={memory_type.value}")

            return {
                "success": True,
                "memory_id": memory_entry["id"],
                "user_id": user_id,
                "memory_type": memory_type.value,
                "message": "记忆存储成功",
            }

        except Exception as e:
            logger.error(f"存储记忆失败: {e!s}")
            return {
                "success": False,
                "error": str(e),
                "message": f"存储记忆失败: {e!s}",
            }

    async def _get_user_memory_database(self, user_id: str) -> dict[str, Any] | None:
        """获取用户记忆数据库"""
        try:
            if user_id in self._memory_database:
                return self._memory_database[user_id]

            memory_key = f"memory_database:{user_id}"
            memory_data = await self.cache_manager.get(memory_key)

            if memory_data:
                memory_db = json.loads(memory_data)
                self._memory_database[user_id] = memory_db
                return memory_db

            return None

        except Exception as e:
            logger.warning(f"获取用户记忆数据库失败: {e!s}")
            return None

    async def _analyze_memory_content(
        self, memory_entry: dict[str, Any]
    ) -> dict[str, Any]:
        """分析记忆内容"""
        try:
            # 在实际实现中，这里应该使用AI模型分析记忆内容
            # 提取关键词、情感、重要性等信息

            content = memory_entry["content"]

            analysis = {
                "keywords": [],
                "emotions": [],
                "entities": [],
                "topics": [],
                "complexity": 1,
                "memorability_score": 0.5,
            }

            # 简单的关键词提取
            if "text" in content:
                text = content["text"].lower()
                # 这里应该使用NLP模型进行更复杂的分析
                analysis["keywords"] = text.split()[:5]  # 简化处理

            return analysis

        except Exception as e:
            logger.warning(f"分析记忆内容失败: {e!s}")
            return {}

    async def _create_memory_associations(
        self, user_id: str, new_memory: dict[str, Any], memory_db: dict[str, Any]
    ):
        """创建记忆关联"""
        try:
            # 查找相似记忆
            similar_memories = await self._find_similar_memories(new_memory, memory_db)

            # 创建关联
            for similar_memory in similar_memories:
                association = {
                    "memory_id": similar_memory["id"],
                    "similarity_score": similar_memory["similarity"],
                    "association_type": "content_similarity",
                    "created_at": datetime.now(UTC).isoformat(),
                }
                new_memory["associations"].append(association)

            # 更新关联图
            if user_id not in memory_db["associations"]:
                memory_db["associations"][user_id] = {}

            memory_db["associations"][user_id][new_memory["id"]] = [
                assoc["memory_id"] for assoc in new_memory["associations"]
            ]

        except Exception as e:
            logger.warning(f"创建记忆关联失败: {e!s}")

    async def _find_similar_memories(
        self, new_memory: dict[str, Any], memory_db: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """查找相似记忆"""
        try:
            similar_memories = []

            # 遍历所有记忆类型
            for memory_type, memories in memory_db["memories"].items():
                for memory in memories:
                    similarity = await self._calculate_memory_similarity(
                        new_memory, memory
                    )
                    if similarity > 0.5:  # 相似度阈值
                        similar_memories.append(
                            {
                                "id": memory["id"],
                                "similarity": similarity,
                                "type": memory_type,
                            }
                        )

            # 按相似度排序
            similar_memories.sort(key=lambda x: x["similarity"], reverse=True)

            return similar_memories[:5]  # 返回最相似的5个

        except Exception as e:
            logger.warning(f"查找相似记忆失败: {e!s}")
            return []

    async def _calculate_memory_similarity(
        self, memory1: dict[str, Any], memory2: dict[str, Any]
    ) -> float:
        """计算记忆相似度"""
        try:
            # 简单的相似度计算
            # 在实际实现中，应该使用更复杂的语义相似度算法

            similarity = 0.0

            # 标签相似度
            tags1 = set(memory1.get("tags", []))
            tags2 = set(memory2.get("tags", []))
            if tags1 and tags2:
                tag_similarity = len(tags1.intersection(tags2)) / len(
                    tags1.union(tags2)
                )
                similarity += tag_similarity * 0.3

            # 内容相似度（简化）
            content1 = str(memory1.get("content", {}))
            content2 = str(memory2.get("content", {}))

            # 简单的词汇重叠计算
            words1 = set(content1.lower().split())
            words2 = set(content2.lower().split())
            if words1 and words2:
                word_similarity = len(words1.intersection(words2)) / len(
                    words1.union(words2)
                )
                similarity += word_similarity * 0.7

            return min(similarity, 1.0)

        except Exception as e:
            logger.warning(f"计算记忆相似度失败: {e!s}")
            return 0.0

    async def _save_memory_database(self, user_id: str, memory_db: dict[str, Any]):
        """保存记忆数据库"""
        try:
            memory_key = f"memory_database:{user_id}"
            await self.cache_manager.set(
                memory_key, json.dumps(memory_db), ttl=86400 * 365  # 保存1年
            )

            self._memory_database[user_id] = memory_db

        except Exception as e:
            logger.warning(f"保存记忆数据库失败: {e!s}")

    @performance_monitor
    @error_handler
    async def retrieve_memory(
        self, user_id: str, query: dict[str, Any], memory_types: list[MemoryType] = None
    ) -> dict[str, Any]:
        """
        检索记忆信息

        Args:
            user_id: 用户ID
            query: 查询条件
            memory_types: 记忆类型列表

        Returns:
            检索结果
        """
        try:
            # 获取用户记忆数据库
            memory_db = await self._get_user_memory_database(user_id)
            if not memory_db:
                return {"success": False, "message": "用户记忆数据库不存在"}

            # 确定搜索范围
            search_types = memory_types or list(MemoryType)

            # 执行记忆检索
            retrieved_memories = []

            for memory_type in search_types:
                type_memories = memory_db["memories"].get(memory_type.value, [])

                for memory in type_memories:
                    relevance_score = await self._calculate_query_relevance(
                        query, memory
                    )

                    if relevance_score > 0.3:  # 相关性阈值
                        # 更新访问信息
                        memory["last_accessed"] = datetime.now(UTC).isoformat()
                        memory["access_count"] += 1

                        retrieved_memories.append(
                            {
                                "memory": memory,
                                "relevance_score": relevance_score,
                                "memory_type": memory_type.value,
                            }
                        )

            # 按相关性排序
            retrieved_memories.sort(key=lambda x: x["relevance_score"], reverse=True)

            # 保存更新的访问信息
            await self._save_memory_database(user_id, memory_db)

            # 记录检索模式
            await self._record_retrieval_pattern(user_id, query, retrieved_memories)

            logger.info(
                f"记忆检索完成: 用户={user_id}, 找到{len(retrieved_memories)}条记忆"
            )

            return {
                "success": True,
                "user_id": user_id,
                "query": query,
                "retrieved_count": len(retrieved_memories),
                "memories": retrieved_memories[:10],  # 返回前10条
                "message": "记忆检索成功",
            }

        except Exception as e:
            logger.error(f"检索记忆失败: {e!s}")
            return {
                "success": False,
                "error": str(e),
                "message": f"检索记忆失败: {e!s}",
            }

    async def _calculate_query_relevance(
        self, query: dict[str, Any], memory: dict[str, Any]
    ) -> float:
        """计算查询相关性"""
        try:
            relevance = 0.0

            # 关键词匹配
            if "keywords" in query:
                query_keywords = set(query["keywords"])
                memory_keywords = set(memory.get("tags", []))

                if query_keywords and memory_keywords:
                    keyword_match = len(
                        query_keywords.intersection(memory_keywords)
                    ) / len(query_keywords)
                    relevance += keyword_match * 0.4

            # 内容匹配
            if "text" in query:
                query_text = query["text"].lower()
                memory_content = str(memory.get("content", {})).lower()

                # 简单的文本匹配
                query_words = set(query_text.split())
                memory_words = set(memory_content.split())

                if query_words and memory_words:
                    text_match = len(query_words.intersection(memory_words)) / len(
                        query_words
                    )
                    relevance += text_match * 0.4

            # 时间相关性
            if "time_range" in query:
                memory_time = datetime.fromisoformat(
                    memory["created_at"].replace("Z", "+00:00")
                )
                time_relevance = await self._calculate_time_relevance(
                    query["time_range"], memory_time
                )
                relevance += time_relevance * 0.2

            return min(relevance, 1.0)

        except Exception as e:
            logger.warning(f"计算查询相关性失败: {e!s}")
            return 0.0

    async def _calculate_time_relevance(
        self, time_range: dict[str, str], memory_time: datetime
    ) -> float:
        """计算时间相关性"""
        try:
            start_time = datetime.fromisoformat(
                time_range.get("start", "1970-01-01T00:00:00+00:00")
            )
            end_time = datetime.fromisoformat(
                time_range.get("end", "2099-12-31T23:59:59+00:00")
            )

            if start_time <= memory_time <= end_time:
                return 1.0
            else:
                return 0.0

        except Exception as e:
            logger.warning(f"计算时间相关性失败: {e!s}")
            return 0.0

    async def _record_retrieval_pattern(
        self, user_id: str, query: dict[str, Any], results: list[dict[str, Any]]
    ):
        """记录检索模式"""
        try:
            pattern_key = f"retrieval_patterns:{user_id}"

            pattern_entry = {
                "timestamp": datetime.now(UTC).isoformat(),
                "query": query,
                "result_count": len(results),
                "success": len(results) > 0,
            }

            # 获取现有模式
            existing_patterns = await self.cache_manager.get(pattern_key)
            if existing_patterns:
                patterns_list = json.loads(existing_patterns)
            else:
                patterns_list = []

            # 添加新模式
            patterns_list.append(pattern_entry)

            # 保持最近1000条记录
            if len(patterns_list) > 1000:
                patterns_list = patterns_list[-1000:]

            # 保存模式
            await self.cache_manager.set(
                pattern_key, json.dumps(patterns_list), ttl=86400 * 30  # 保存30天
            )

        except Exception as e:
            logger.warning(f"记录检索模式失败: {e!s}")

    @performance_monitor
    @error_handler
    async def create_reminder(
        self,
        user_id: str,
        reminder_type: ReminderType,
        content: dict[str, Any],
        schedule: dict[str, Any],
        settings: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """
        创建提醒

        Args:
            user_id: 用户ID
            reminder_type: 提醒类型
            content: 提醒内容
            schedule: 调度设置
            settings: 提醒设置

        Returns:
            创建结果
        """
        try:
            # 生成提醒ID
            reminder_id = str(uuid.uuid4())

            # 获取用户档案
            user_profile = await self._get_user_profile(user_id)
            if not user_profile:
                return {"success": False, "message": "用户档案不存在"}

            # 创建提醒条目
            reminder = {
                "id": reminder_id,
                "user_id": user_id,
                "type": reminder_type.value,
                "content": content,
                "schedule": schedule,
                "settings": settings or {},
                "created_at": datetime.now(UTC).isoformat(),
                "status": "active",
                "trigger_count": 0,
                "last_triggered": None,
                "next_trigger": await self._calculate_next_trigger(schedule),
            }

            # 优化提醒设置
            if self._reminder_optimization_model:
                optimized_settings = await self._optimize_reminder_settings(
                    user_profile, reminder
                )
                reminder["settings"].update(optimized_settings)

            # 保存提醒
            await self._save_reminder(reminder)

            # 添加到调度器
            await self._schedule_reminder(reminder)

            logger.info(f"提醒创建成功: 用户={user_id}, 类型={reminder_type.value}")

            return {
                "success": True,
                "reminder_id": reminder_id,
                "user_id": user_id,
                "reminder_type": reminder_type.value,
                "next_trigger": reminder["next_trigger"],
                "message": "提醒创建成功",
            }

        except Exception as e:
            logger.error(f"创建提醒失败: {e!s}")
            return {
                "success": False,
                "error": str(e),
                "message": f"创建提醒失败: {e!s}",
            }

    async def _get_user_profile(self, user_id: str) -> dict[str, Any] | None:
        """获取用户档案"""
        try:
            if user_id in self._active_users:
                return self._active_users[user_id]["profile"]

            profile_key = f"memory_profile:{user_id}"
            profile_data = await self.cache_manager.get(profile_key)

            if profile_data:
                return json.loads(profile_data)

            return None

        except Exception as e:
            logger.warning(f"获取用户档案失败: {e!s}")
            return None

    async def _calculate_next_trigger(self, schedule: dict[str, Any]) -> str:
        """计算下次触发时间"""
        try:
            schedule_type = schedule.get("type", "once")

            if schedule_type == "once":
                trigger_time = datetime.fromisoformat(schedule["datetime"])
            elif schedule_type == "daily":
                time_str = schedule["time"]  # "HH:MM"
                hour, minute = map(int, time_str.split(":"))

                now = datetime.now(UTC)
                trigger_time = now.replace(
                    hour=hour, minute=minute, second=0, microsecond=0
                )

                # 如果今天的时间已过，设置为明天
                if trigger_time <= now:
                    trigger_time += timedelta(days=1)

            elif schedule_type == "weekly":
                # 实现周期性提醒
                trigger_time = datetime.now(UTC) + timedelta(days=7)

            else:
                # 默认1小时后
                trigger_time = datetime.now(UTC) + timedelta(hours=1)

            return trigger_time.isoformat()

        except Exception as e:
            logger.warning(f"计算下次触发时间失败: {e!s}")
            return (datetime.now(UTC) + timedelta(hours=1)).isoformat()

    async def _optimize_reminder_settings(
        self, user_profile: dict[str, Any], reminder: dict[str, Any]
    ) -> dict[str, Any]:
        """优化提醒设置"""
        try:
            # 在实际实现中，这里应该使用AI模型优化提醒设置

            cognitive_level = user_profile.get("cognitive_level", "normal")
            reminder_settings = user_profile.get("reminder_settings", {})

            optimized = {}

            # 根据认知水平调整提醒频率
            if cognitive_level == "severe":
                optimized["advance_time"] = 30  # 提前30分钟
                optimized["repeat_interval"] = 3  # 每3分钟重复
                optimized["max_repeats"] = 5
            elif cognitive_level == "moderate":
                optimized["advance_time"] = 20
                optimized["repeat_interval"] = 5
                optimized["max_repeats"] = 3
            else:
                optimized["advance_time"] = reminder_settings.get(
                    "default_advance_time", 15
                )
                optimized["repeat_interval"] = reminder_settings.get(
                    "repeat_interval", 5
                )
                optimized["max_repeats"] = reminder_settings.get("max_repeats", 3)

            return optimized

        except Exception as e:
            logger.warning(f"优化提醒设置失败: {e!s}")
            return {}

    async def _save_reminder(self, reminder: dict[str, Any]):
        """保存提醒"""
        try:
            reminder_key = f"reminder:{reminder['id']}"
            await self.cache_manager.set(
                reminder_key, json.dumps(reminder), ttl=86400 * 30  # 保存30天
            )

            # 添加到用户提醒列表
            user_reminders_key = f"user_reminders:{reminder['user_id']}"
            existing_reminders = await self.cache_manager.get(user_reminders_key)

            if existing_reminders:
                reminders_list = json.loads(existing_reminders)
            else:
                reminders_list = []

            reminders_list.append(reminder["id"])

            await self.cache_manager.set(
                user_reminders_key, json.dumps(reminders_list), ttl=86400 * 30
            )

        except Exception as e:
            logger.warning(f"保存提醒失败: {e!s}")

    async def _schedule_reminder(self, reminder: dict[str, Any]):
        """调度提醒"""
        try:
            # 在实际实现中，这里应该将提醒添加到调度器
            # 例如：APScheduler、Celery等

            reminder_id = reminder["id"]
            self._reminder_scheduler[reminder_id] = reminder

            logger.info(f"提醒已调度: {reminder_id}")

        except Exception as e:
            logger.warning(f"调度提醒失败: {e!s}")

    async def _reminder_check_loop(self):
        """提醒检查循环"""
        while True:
            try:
                await asyncio.sleep(60)  # 每分钟检查一次

                current_time = datetime.now(UTC)

                # 检查所有调度的提醒
                for reminder_id, reminder in list(self._reminder_scheduler.items()):
                    next_trigger = datetime.fromisoformat(reminder["next_trigger"])

                    if current_time >= next_trigger:
                        await self._trigger_reminder(reminder)

                        # 更新下次触发时间
                        if reminder["schedule"].get("type") != "once":
                            reminder["next_trigger"] = (
                                await self._calculate_next_trigger(reminder["schedule"])
                            )
                        else:
                            # 一次性提醒，移除调度
                            del self._reminder_scheduler[reminder_id]

            except Exception as e:
                logger.error(f"提醒检查循环错误: {e!s}")
                await asyncio.sleep(60)

    async def _trigger_reminder(self, reminder: dict[str, Any]):
        """触发提醒"""
        try:
            reminder["trigger_count"] += 1
            reminder["last_triggered"] = datetime.now(UTC).isoformat()

            # 发送提醒通知
            await self._send_reminder_notification(reminder)

            # 保存更新的提醒
            await self._save_reminder(reminder)

            logger.info(f"提醒已触发: {reminder['id']}")

        except Exception as e:
            logger.error(f"触发提醒失败: {e!s}")

    async def _send_reminder_notification(self, reminder: dict[str, Any]):
        """发送提醒通知"""
        try:
            # 在实际实现中，这里应该通过各种渠道发送提醒
            # 例如：推送通知、短信、邮件、语音等

            user_id = reminder["user_id"]
            content = reminder["content"]

            notification = {
                "user_id": user_id,
                "type": "reminder",
                "title": content.get("title", "提醒"),
                "message": content.get("message", "您有一个提醒"),
                "reminder_id": reminder["id"],
                "timestamp": datetime.now(UTC).isoformat(),
            }

            logger.info(f"提醒通知已发送: {notification}")

        except Exception as e:
            logger.warning(f"发送提醒通知失败: {e!s}")

    async def _memory_analysis_loop(self):
        """记忆分析循环"""
        while True:
            try:
                await asyncio.sleep(3600)  # 每小时分析一次

                # 分析所有活跃用户的记忆模式
                for user_id in list(self._active_users.keys()):
                    await self._analyze_user_memory_patterns(user_id)

            except Exception as e:
                logger.error(f"记忆分析循环错误: {e!s}")
                await asyncio.sleep(3600)

    async def _analyze_user_memory_patterns(self, user_id: str):
        """分析用户记忆模式"""
        try:
            memory_db = await self._get_user_memory_database(user_id)
            if not memory_db:
                return

            # 在实际实现中，这里应该使用AI模型分析记忆模式
            # 例如：记忆衰减模式、检索偏好、遗忘曲线等

            patterns = {
                "most_accessed_type": "episodic",
                "average_retention_time": 7,  # 天
                "retrieval_success_rate": 0.75,
                "memory_consolidation_rate": 0.6,
            }

            # 保存分析结果
            patterns_key = f"memory_patterns:{user_id}"
            await self.cache_manager.set(
                patterns_key, json.dumps(patterns), ttl=86400 * 7  # 保存7天
            )

        except Exception as e:
            logger.warning(f"分析用户记忆模式失败: {e!s}")

    async def _cognitive_assessment_loop(self):
        """认知评估循环"""
        while True:
            try:
                await asyncio.sleep(86400)  # 每天评估一次

                # 对所有活跃用户进行认知评估
                for user_id in list(self._active_users.keys()):
                    await self._perform_cognitive_assessment(user_id)

            except Exception as e:
                logger.error(f"认知评估循环错误: {e!s}")
                await asyncio.sleep(86400)

    async def _perform_cognitive_assessment(self, user_id: str):
        """执行认知评估"""
        try:
            # 在实际实现中，这里应该使用AI模型进行认知评估

            assessment_result = {
                "user_id": user_id,
                "assessment_date": datetime.now(UTC).isoformat(),
                "cognitive_domains": {
                    "attention": 0.8,
                    "memory": 0.7,
                    "executive_function": 0.75,
                    "language": 0.85,
                    "visuospatial": 0.8,
                },
                "overall_score": 0.78,
                "recommendations": [
                    "增加记忆训练练习",
                    "调整提醒频率",
                    "加强注意力训练",
                ],
            }

            # 保存评估结果
            assessment_key = f"cognitive_assessment:{user_id}"
            await self.cache_manager.set(
                assessment_key,
                json.dumps(assessment_result),
                ttl=86400 * 30,  # 保存30天
            )

            logger.info(
                f"认知评估完成: 用户={user_id}, 总分={assessment_result['overall_score']}"
            )

        except Exception as e:
            logger.warning(f"执行认知评估失败: {e!s}")

    async def get_service_status(self) -> dict[str, Any]:
        """获取服务状态"""
        return {
            "service_name": "MemoryAssistanceService",
            "enabled": self.enabled,
            "initialized": self._initialized,
            "request_count": self._request_count,
            "error_count": self._error_count,
            "error_rate": self._error_count / max(self._request_count, 1),
            "active_users": len(self._active_users),
            "scheduled_reminders": len(self._reminder_scheduler),
            "memory_databases": len(self._memory_database),
            "supported_memory_types": [mtype.value for mtype in MemoryType],
            "supported_reminder_types": [rtype.value for rtype in ReminderType],
            "cognitive_levels": [level.value for level in CognitiveLevel],
            "models_loaded": {
                "memory_analysis": self._memory_analysis_model is not None,
                "cognitive_assessment": self._cognitive_assessment_model is not None,
                "reminder_optimization": self._reminder_optimization_model is not None,
                "pattern_recognition": self._pattern_recognition_model is not None,
            },
        }

    async def cleanup(self):
        """清理服务资源"""
        try:
            # 清理活跃用户
            self._active_users.clear()

            # 清理记忆数据库
            self._memory_database.clear()

            # 清理提醒调度器
            self._reminder_scheduler.clear()

            # 释放模型资源
            self._memory_analysis_model = None
            self._cognitive_assessment_model = None
            self._reminder_optimization_model = None
            self._pattern_recognition_model = None

            self._initialized = False
            logger.info("记忆辅助服务清理完成")

        except Exception as e:
            logger.error(f"记忆辅助服务清理失败: {e!s}")
