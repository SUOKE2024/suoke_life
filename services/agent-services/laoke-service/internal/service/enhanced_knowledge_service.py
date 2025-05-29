#!/usr/bin/env python3
"""
增强版知识管理服务
集成断路器、限流、追踪、缓存等优化组件
专注于知识内容管理、学习路径推荐和社区内容管理
"""

import asyncio
import hashlib
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

# 导入通用组件
from services.common.governance.circuit_breaker import (
    CircuitBreakerConfig,
    get_circuit_breaker,
)
from services.common.governance.rate_limiter import (
    RateLimitConfig,
    get_rate_limiter,
)
from services.common.observability.tracing import SpanKind, get_tracer, trace

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """内容类型"""
    ARTICLE = "article"
    VIDEO = "video"
    AUDIO = "audio"
    COURSE = "course"
    QUIZ = "quiz"

class DifficultyLevel(Enum):
    """难度级别"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class LearningStyle(Enum):
    """学习风格"""
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING = "reading"

@dataclass
class KnowledgeRequest:
    """知识请求"""
    user_id: str
    topic: str
    content_type: ContentType | None = None
    difficulty_level: DifficultyLevel | None = None
    learning_style: LearningStyle | None = None
    keywords: list[str] | None = None
    max_results: int = 10

@dataclass
class LearningPathRequest:
    """学习路径请求"""
    user_id: str
    learning_goals: list[str]
    current_level: DifficultyLevel
    preferred_content_types: list[ContentType]
    time_commitment: str  # daily, weekly, monthly
    duration_weeks: int = 12

@dataclass
class CommunityContentRequest:
    """社区内容请求"""
    user_id: str
    content_type: str = "all"  # all, posts, discussions, questions
    category: str | None = None
    sort_by: str = "latest"  # latest, popular, trending
    limit: int = 20

@dataclass
class KnowledgeResult:
    """知识搜索结果"""
    request_id: str
    user_id: str
    matched_content: list[dict[str, Any]]
    recommendations: list[dict[str, Any]]
    related_topics: list[str]
    learning_suggestions: list[str]
    processing_time: float
    timestamp: float

@dataclass
class LearningPathResult:
    """学习路径结果"""
    request_id: str
    user_id: str
    path_id: str
    path_name: str
    modules: list[dict[str, Any]]
    estimated_duration: str
    progress_tracking: dict[str, Any]
    milestones: list[dict[str, Any]]
    processing_time: float
    timestamp: float

@dataclass
class CommunityContentResult:
    """社区内容结果"""
    request_id: str
    user_id: str
    content_items: list[dict[str, Any]]
    trending_topics: list[str]
    recommended_users: list[dict[str, Any]]
    engagement_stats: dict[str, Any]
    processing_time: float
    timestamp: float

class EnhancedKnowledgeService:
    """增强版知识管理服务"""

    def __init__(self):
        self.service_name = "laoke-knowledge"
        self.tracer = get_tracer(self.service_name)

        # 初始化断路器配置
        self._init_circuit_breakers()

        # 初始化限流器配置
        self._init_rate_limiters()

        # 缓存
        self.knowledge_cache = {}
        self.learning_path_cache = {}
        self.community_cache = {}
        self.cache_ttl = 900  # 15分钟缓存

        # 统计信息
        self.stats = {
            'total_requests': 0,
            'knowledge_requests': 0,
            'learning_path_requests': 0,
            'community_requests': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'average_processing_time': 0.0
        }

        logger.info("增强版知识管理服务初始化完成")

    def _init_circuit_breakers(self):
        """初始化断路器配置"""
        self.circuit_breaker_configs = {
            'knowledge_db': CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=60.0,
                timeout=8.0
            ),
            'search_engine': CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=45.0,
                timeout=10.0
            ),
            'recommendation_engine': CircuitBreakerConfig(
                failure_threshold=4,
                recovery_timeout=90.0,
                timeout=12.0
            ),
            'content_analysis': CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=120.0,
                timeout=15.0
            )
        }

    def _init_rate_limiters(self):
        """初始化限流器配置"""
        self.rate_limit_configs = {
            'knowledge_search': RateLimitConfig(rate=30.0, burst=60),
            'learning_path': RateLimitConfig(rate=10.0, burst=20),
            'community_content': RateLimitConfig(rate=25.0, burst=50),
            'content_creation': RateLimitConfig(rate=5.0, burst=10)
        }

    @trace(service_name="laoke-knowledge", kind=SpanKind.SERVER)
    async def search_knowledge(self, request: KnowledgeRequest) -> KnowledgeResult:
        """
        搜索知识内容

        Args:
            request: 知识搜索请求

        Returns:
            KnowledgeResult: 知识搜索结果
        """
        start_time = time.time()
        self.stats['total_requests'] += 1
        self.stats['knowledge_requests'] += 1

        try:
            # 限流检查
            limiter = await get_rate_limiter(
                f"{self.service_name}_knowledge_search",
                config=self.rate_limit_configs['knowledge_search']
            )

            if not await limiter.try_acquire():
                raise Exception("知识搜索请求频率过高，请稍后重试")

            # 检查缓存
            cache_key = self._generate_knowledge_cache_key(request)
            cached_result = await self._get_from_cache(cache_key, self.knowledge_cache)
            if cached_result:
                self.stats['cache_hits'] += 1
                return cached_result

            self.stats['cache_misses'] += 1

            # 执行知识搜索
            result = await self._perform_knowledge_search(request)

            # 缓存结果
            await self._cache_result(cache_key, result, self.knowledge_cache)

            # 更新统计
            processing_time = time.time() - start_time
            self.stats['successful_operations'] += 1
            self._update_average_processing_time(processing_time)

            return result

        except Exception as e:
            self.stats['failed_operations'] += 1
            logger.error(f"知识搜索失败: {e}")
            raise

    @trace(operation_name="perform_knowledge_search")
    async def _perform_knowledge_search(self, request: KnowledgeRequest) -> KnowledgeResult:
        """执行知识搜索逻辑"""
        request_id = f"know_{int(time.time() * 1000)}"

        # 并行执行搜索任务
        tasks = []

        # 内容搜索
        tasks.append(self._search_content(request))

        # 推荐内容
        tasks.append(self._recommend_content(request))

        # 相关主题分析
        tasks.append(self._analyze_related_topics(request))

        # 学习建议生成
        tasks.append(self._generate_learning_suggestions(request))

        # 等待所有任务完成
        results = await asyncio.gather(*tasks, return_exceptions=True)

        matched_content = results[0] if not isinstance(results[0], Exception) else []
        recommendations = results[1] if not isinstance(results[1], Exception) else []
        related_topics = results[2] if not isinstance(results[2], Exception) else []
        learning_suggestions = results[3] if not isinstance(results[3], Exception) else []

        return KnowledgeResult(
            request_id=request_id,
            user_id=request.user_id,
            matched_content=matched_content,
            recommendations=recommendations,
            related_topics=related_topics,
            learning_suggestions=learning_suggestions,
            processing_time=time.time() - time.time(),
            timestamp=time.time()
        )

    @trace(operation_name="search_content")
    async def _search_content(self, request: KnowledgeRequest) -> list[dict[str, Any]]:
        """搜索内容"""
        # 使用断路器保护搜索引擎
        breaker = await get_circuit_breaker(
            f"{self.service_name}_search_engine",
            self.circuit_breaker_configs['search_engine']
        )

        async with breaker.protect():
            # 模拟搜索引擎调用
            await asyncio.sleep(0.15)

            # 根据主题和内容类型搜索
            content_library = {
                "中医基础": [
                    {
                        'id': 'tcm_001',
                        'title': '中医基础理论入门',
                        'type': ContentType.ARTICLE.value,
                        'difficulty': DifficultyLevel.BEGINNER.value,
                        'duration': '30分钟',
                        'rating': 4.8,
                        'description': '系统介绍中医基础理论，包括阴阳五行、脏腑经络等'
                    },
                    {
                        'id': 'tcm_002',
                        'title': '中医诊断学视频课程',
                        'type': ContentType.VIDEO.value,
                        'difficulty': DifficultyLevel.INTERMEDIATE.value,
                        'duration': '2小时',
                        'rating': 4.9,
                        'description': '详细讲解中医四诊方法：望、闻、问、切'
                    }
                ],
                "养生保健": [
                    {
                        'id': 'health_001',
                        'title': '四季养生指南',
                        'type': ContentType.COURSE.value,
                        'difficulty': DifficultyLevel.BEGINNER.value,
                        'duration': '1小时',
                        'rating': 4.7,
                        'description': '根据四季变化调整生活方式和饮食习惯'
                    }
                ]
            }

            return content_library.get(request.topic, [])

    @trace(operation_name="generate_learning_path")
    async def generate_learning_path(self, request: LearningPathRequest) -> LearningPathResult:
        """
        生成个性化学习路径

        Args:
            request: 学习路径请求

        Returns:
            LearningPathResult: 学习路径结果
        """
        start_time = time.time()
        self.stats['total_requests'] += 1
        self.stats['learning_path_requests'] += 1

        try:
            # 限流检查
            limiter = await get_rate_limiter(
                f"{self.service_name}_learning_path",
                config=self.rate_limit_configs['learning_path']
            )

            if not await limiter.try_acquire():
                raise Exception("学习路径生成请求频率过高，请稍后重试")

            # 检查缓存
            cache_key = self._generate_learning_path_cache_key(request)
            cached_result = await self._get_from_cache(cache_key, self.learning_path_cache)
            if cached_result:
                self.stats['cache_hits'] += 1
                return cached_result

            self.stats['cache_misses'] += 1

            # 生成学习路径
            result = await self._perform_learning_path_generation(request)

            # 缓存结果
            await self._cache_result(cache_key, result, self.learning_path_cache)

            # 更新统计
            processing_time = time.time() - start_time
            self.stats['successful_operations'] += 1
            self._update_average_processing_time(processing_time)

            return result

        except Exception as e:
            self.stats['failed_operations'] += 1
            logger.error(f"学习路径生成失败: {e}")
            raise

    @trace(operation_name="perform_learning_path_generation")
    async def _perform_learning_path_generation(self, request: LearningPathRequest) -> LearningPathResult:
        """执行学习路径生成逻辑"""
        request_id = f"path_{int(time.time() * 1000)}"
        path_id = f"lp_{request.user_id}_{int(time.time())}"

        # 并行执行路径生成任务
        tasks = []

        # 模块规划
        tasks.append(self._plan_learning_modules(request))

        # 里程碑设置
        tasks.append(self._set_milestones(request))

        # 进度跟踪配置
        tasks.append(self._configure_progress_tracking(request))

        # 等待所有任务完成
        results = await asyncio.gather(*tasks, return_exceptions=True)

        modules = results[0] if not isinstance(results[0], Exception) else []
        milestones = results[1] if not isinstance(results[1], Exception) else []
        progress_tracking = results[2] if not isinstance(results[2], Exception) else {}

        # 生成路径名称
        path_name = f"{request.learning_goals[0]}学习路径" if request.learning_goals else "个性化学习路径"

        return LearningPathResult(
            request_id=request_id,
            user_id=request.user_id,
            path_id=path_id,
            path_name=path_name,
            modules=modules,
            estimated_duration=f"{request.duration_weeks}周",
            progress_tracking=progress_tracking,
            milestones=milestones,
            processing_time=time.time() - time.time(),
            timestamp=time.time()
        )

    @trace(operation_name="get_community_content")
    async def get_community_content(self, request: CommunityContentRequest) -> CommunityContentResult:
        """
        获取社区内容

        Args:
            request: 社区内容请求

        Returns:
            CommunityContentResult: 社区内容结果
        """
        start_time = time.time()
        self.stats['total_requests'] += 1
        self.stats['community_requests'] += 1

        try:
            # 限流检查
            limiter = await get_rate_limiter(
                f"{self.service_name}_community_content",
                config=self.rate_limit_configs['community_content']
            )

            if not await limiter.try_acquire():
                raise Exception("社区内容请求频率过高，请稍后重试")

            # 检查缓存
            cache_key = self._generate_community_cache_key(request)
            cached_result = await self._get_from_cache(cache_key, self.community_cache)
            if cached_result:
                self.stats['cache_hits'] += 1
                return cached_result

            self.stats['cache_misses'] += 1

            # 获取社区内容
            result = await self._perform_community_content_retrieval(request)

            # 缓存结果（社区内容缓存时间较短）
            await self._cache_result(cache_key, result, self.community_cache, ttl=300)

            # 更新统计
            processing_time = time.time() - start_time
            self.stats['successful_operations'] += 1
            self._update_average_processing_time(processing_time)

            return result

        except Exception as e:
            self.stats['failed_operations'] += 1
            logger.error(f"社区内容获取失败: {e}")
            raise

    async def _recommend_content(self, request: KnowledgeRequest) -> list[dict[str, Any]]:
        """推荐内容"""
        # 使用推荐引擎断路器
        breaker = await get_circuit_breaker(
            f"{self.service_name}_recommendation_engine",
            self.circuit_breaker_configs['recommendation_engine']
        )

        async with breaker.protect():
            await asyncio.sleep(0.12)

            # 基于用户偏好和学习历史推荐
            recommendations = [
                {
                    'id': 'rec_001',
                    'title': '推荐：中医体质辨识',
                    'type': ContentType.QUIZ.value,
                    'reason': '基于您的学习历史推荐',
                    'relevance_score': 0.92
                },
                {
                    'id': 'rec_002',
                    'title': '推荐：经络穴位图解',
                    'type': ContentType.VIDEO.value,
                    'reason': '与您当前学习内容相关',
                    'relevance_score': 0.88
                }
            ]

            return recommendations

    async def _analyze_related_topics(self, request: KnowledgeRequest) -> list[str]:
        """分析相关主题"""
        await asyncio.sleep(0.08)

        topic_relations = {
            "中医基础": ["阴阳五行", "脏腑理论", "经络学说", "病因病机"],
            "养生保健": ["四季养生", "饮食调养", "运动养生", "情志调摄"],
            "针灸推拿": ["经络穴位", "针法灸法", "推拿手法", "适应症"]
        }

        return topic_relations.get(request.topic, ["相关主题待补充"])

    async def _generate_learning_suggestions(self, request: KnowledgeRequest) -> list[str]:
        """生成学习建议"""
        await asyncio.sleep(0.06)

        suggestions = [
            f"建议从{request.difficulty_level.value if request.difficulty_level else '基础'}级别开始学习",
            "结合理论学习和实践操作，提高学习效果",
            "定期复习已学内容，巩固知识点",
            "参与社区讨论，与其他学习者交流经验"
        ]

        return suggestions

    async def _plan_learning_modules(self, request: LearningPathRequest) -> list[dict[str, Any]]:
        """规划学习模块"""
        await asyncio.sleep(0.1)

        modules = []
        weeks_per_module = max(1, request.duration_weeks // len(request.learning_goals))

        for i, goal in enumerate(request.learning_goals):
            modules.append({
                'module_id': f"mod_{i+1:02d}",
                'title': f"模块{i+1}: {goal}",
                'duration_weeks': weeks_per_module,
                'content_types': [ct.value for ct in request.preferred_content_types],
                'learning_objectives': [f"掌握{goal}的基本概念", f"理解{goal}的应用场景"],
                'assessment_method': 'quiz_and_practice'
            })

        return modules

    async def _set_milestones(self, request: LearningPathRequest) -> list[dict[str, Any]]:
        """设置学习里程碑"""
        await asyncio.sleep(0.05)

        milestones = []
        milestone_weeks = [request.duration_weeks // 4, request.duration_weeks // 2,
                          3 * request.duration_weeks // 4, request.duration_weeks]

        for i, week in enumerate(milestone_weeks):
            milestones.append({
                'milestone_id': f"ms_{i+1}",
                'title': f"里程碑{i+1}",
                'target_week': week,
                'description': f"完成{25*(i+1)}%的学习目标",
                'reward': f"获得{i+1}级学习徽章"
            })

        return milestones

    async def _configure_progress_tracking(self, request: LearningPathRequest) -> dict[str, Any]:
        """配置进度跟踪"""
        await asyncio.sleep(0.03)

        return {
            'tracking_method': 'automatic_and_manual',
            'progress_indicators': ['completion_rate', 'quiz_scores', 'time_spent'],
            'reporting_frequency': request.time_commitment,
            'adaptive_adjustment': True,
            'social_features': ['progress_sharing', 'peer_comparison']
        }

    async def _perform_community_content_retrieval(self, request: CommunityContentRequest) -> CommunityContentResult:
        """执行社区内容检索"""
        request_id = f"comm_{int(time.time() * 1000)}"

        # 并行执行社区内容获取任务
        tasks = []

        # 获取内容项
        tasks.append(self._get_content_items(request))

        # 获取热门话题
        tasks.append(self._get_trending_topics(request))

        # 推荐用户
        tasks.append(self._recommend_users(request))

        # 参与度统计
        tasks.append(self._get_engagement_stats(request))

        # 等待所有任务完成
        results = await asyncio.gather(*tasks, return_exceptions=True)

        content_items = results[0] if not isinstance(results[0], Exception) else []
        trending_topics = results[1] if not isinstance(results[1], Exception) else []
        recommended_users = results[2] if not isinstance(results[2], Exception) else []
        engagement_stats = results[3] if not isinstance(results[3], Exception) else {}

        return CommunityContentResult(
            request_id=request_id,
            user_id=request.user_id,
            content_items=content_items,
            trending_topics=trending_topics,
            recommended_users=recommended_users,
            engagement_stats=engagement_stats,
            processing_time=time.time() - time.time(),
            timestamp=time.time()
        )

    async def _get_content_items(self, request: CommunityContentRequest) -> list[dict[str, Any]]:
        """获取社区内容项"""
        await asyncio.sleep(0.1)

        # 模拟社区内容
        content_items = [
            {
                'id': 'post_001',
                'type': 'discussion',
                'title': '中医体质调理心得分享',
                'author': '养生达人',
                'content_preview': '最近通过中医体质辨识，发现自己是阳虚体质...',
                'likes': 156,
                'comments': 23,
                'created_at': '2024-12-19T10:30:00Z',
                'category': '体质调理'
            },
            {
                'id': 'post_002',
                'type': 'question',
                'title': '关于针灸治疗失眠的问题',
                'author': '新手学员',
                'content_preview': '请问针灸治疗失眠一般需要多长时间见效？',
                'likes': 45,
                'comments': 12,
                'created_at': '2024-12-19T09:15:00Z',
                'category': '针灸治疗'
            }
        ]

        return content_items[:request.limit]

    async def _get_trending_topics(self, request: CommunityContentRequest) -> list[str]:
        """获取热门话题"""
        await asyncio.sleep(0.05)
        return ["冬季养生", "体质调理", "针灸疗法", "食疗养生", "情志调摄"]

    async def _recommend_users(self, request: CommunityContentRequest) -> list[dict[str, Any]]:
        """推荐用户"""
        await asyncio.sleep(0.08)
        return [
            {
                'user_id': 'user_001',
                'username': '中医老师',
                'expertise': ['中医基础', '针灸'],
                'followers': 1250,
                'posts': 89
            },
            {
                'user_id': 'user_002',
                'username': '养生专家',
                'expertise': ['养生保健', '食疗'],
                'followers': 980,
                'posts': 156
            }
        ]

    async def _get_engagement_stats(self, request: CommunityContentRequest) -> dict[str, Any]:
        """获取参与度统计"""
        await asyncio.sleep(0.03)
        return {
            'total_posts': 1250,
            'active_users': 450,
            'daily_interactions': 2800,
            'popular_categories': ['体质调理', '养生保健', '针灸推拿']
        }

    def _generate_cache_key(self, prefix: str, data: Any) -> str:
        """生成缓存键"""
        content = f"{prefix}_{str(data)}"
        return hashlib.md5(content.encode()).hexdigest()

    def _generate_knowledge_cache_key(self, request: KnowledgeRequest) -> str:
        """生成知识缓存键"""
        return self._generate_cache_key("knowledge", request)

    def _generate_learning_path_cache_key(self, request: LearningPathRequest) -> str:
        """生成学习路径缓存键"""
        return self._generate_cache_key("learning_path", request)

    def _generate_community_cache_key(self, request: CommunityContentRequest) -> str:
        """生成社区缓存键"""
        return self._generate_cache_key("community", request)

    async def _get_from_cache(self, cache_key: str, cache_dict: dict) -> Any | None:
        """从缓存获取结果"""
        if cache_key in cache_dict:
            cached_data = cache_dict[cache_key]

            # 检查缓存是否过期
            if time.time() - cached_data['timestamp'] < self.cache_ttl:
                return cached_data['result']
            else:
                # 清理过期缓存
                del cache_dict[cache_key]

        return None

    async def _cache_result(self, cache_key: str, result: Any, cache_dict: dict, ttl: int = None):
        """缓存结果"""
        cache_dict[cache_key] = {
            'result': result,
            'timestamp': time.time()
        }

        # 简单的缓存清理策略
        if len(cache_dict) > 1000:
            oldest_key = min(
                cache_dict.keys(),
                key=lambda k: cache_dict[k]['timestamp']
            )
            del cache_dict[oldest_key]

    def _update_average_processing_time(self, processing_time: float):
        """更新平均处理时间"""
        total_successful = self.stats['successful_operations']
        if total_successful == 1:
            self.stats['average_processing_time'] = processing_time
        else:
            current_avg = self.stats['average_processing_time']
            self.stats['average_processing_time'] = (
                (current_avg * (total_successful - 1) + processing_time) / total_successful
            )

    def get_health_status(self) -> dict[str, Any]:
        """获取服务健康状态"""
        return {
            'service': self.service_name,
            'status': 'healthy',
            'stats': self.stats,
            'cache_sizes': {
                'knowledge_cache': len(self.knowledge_cache),
                'learning_path_cache': len(self.learning_path_cache),
                'community_cache': len(self.community_cache)
            },
            'uptime': time.time()
        }

    async def cleanup(self):
        """清理资源"""
        self.knowledge_cache.clear()
        self.learning_path_cache.clear()
        self.community_cache.clear()
        logger.info("知识管理服务清理完成")

# 全局服务实例
_knowledge_service = None

async def get_knowledge_service() -> EnhancedKnowledgeService:
    """获取知识管理服务实例"""
    global _knowledge_service
    if _knowledge_service is None:
        _knowledge_service = EnhancedKnowledgeService()
    return _knowledge_service
