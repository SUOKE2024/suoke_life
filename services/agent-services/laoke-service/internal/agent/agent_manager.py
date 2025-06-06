"""
agent_manager - 索克生活项目模块
"""

            import psutil
from .model_factory import ModelFactory
from contextlib import asynccontextmanager
from dataclasses import asdict, dataclass
from enum import Enum
from pkg.utils.cache import CacheManager
from pkg.utils.config import Config
from pkg.utils.metrics import MetricsCollector
from pkg.utils.rate_limiter import RateLimiter
from pkg.utils.validator import RequestValidator
from typing import Any
import asyncio
import logging
import time
import uuid
import weakref

#!/usr/bin/env python3
"""
智能体管理器
负责老克智能体的核心逻辑，包括中医知识传播、社群管理和教育内容生成
"""




logger = logging.getLogger(__name__)

class RequestType(Enum):
    """请求类型枚举"""
    KNOWLEDGE_QUERY = "knowledge_query"
    CONTENT_CREATION = "content_creation"
    COMMUNITY_MANAGEMENT = "community_management"
    LEARNING_PATH = "learning_path"
    GENERAL_INQUIRY = "general_inquiry"

@dataclass
class SessionData:
    """会话数据"""
    session_id: str
    user_id: str
    created_at: float
    last_activity: float
    message_count: int = 0
    context: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.context is None:
            self.context = {}

@dataclass
class AgentResponse:
    """智能体响应"""
    request_id: str
    success: bool
    content: str
    confidence: float = 0.0
    metadata: dict[str, Any] | None = None
    error: str | None = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}

class AgentManager:
    """老克智能体管理器，负责中医知识传播平台的核心功能"""

    def __init__(self,
                 session_repository: Any = None,
                 knowledge_repository: Any = None,
                 config: Config | None = None,
                 metrics: MetricsCollector | None = None,
                 cache: CacheManager | None = None) -> None:
        """
        初始化智能体管理器

        Args:
            session_repository: 会话存储库
            knowledge_repository: 知识库存储库
            config: 配置管理器
            metrics: 指标收集器
            cache: 缓存管理器
        """
        self.config = config or Config()
        self.metrics = metrics or MetricsCollector()
        self.cache = cache or CacheManager()

        # 设置依赖组件
        self.session_repository = session_repository
        self.knowledge_repository = knowledge_repository

        # 加载配置
        self._load_configuration()

        # 初始化组件
        self.model_factory = ModelFactory(self.config)
        self.rate_limiter = RateLimiter(self.config)
        self.validator = RequestValidator()

        # 活跃会话管理 - 使用弱引用避免内存泄漏
        self._active_sessions: weakref.WeakValueDictionary[str, SessionData] = weakref.WeakValueDictionary()
        self._session_cleanup_task: asyncio.Task[None] | None = None

        # 启动后台任务
        self._start_background_tasks()

        logger.info("老克智能体管理器初始化完成，主模型: %s, 备用模型: %s",
                   self.primary_model, self.fallback_model)

    def _load_configuration(self) -> None:
        """加载配置"""
        # 加载模型配置
        self.llm_config = self.config.get_section('agent.models.llm')
        self.primary_model = self.llm_config.get('primary_model', 'gpt-4o-mini')
        self.fallback_model = self.llm_config.get('fallback_model', 'llama-3-8b')

        # 加载会话配置
        self.conversation_config = self.config.get_section('agent.conversation')
        self.system_prompt = self.conversation_config.get('system_prompt', '')
        self.max_history_turns = self.conversation_config.get('max_history_turns', 20)
        self.max_tokens_per_message = self.conversation_config.get('max_tokens_per_message', 4096)

        # 会话管理配置
        self.session_timeout = self.config.get('agent.session_timeout', 3600)  # 1小时
        self.max_concurrent_sessions = self.config.get('agent.max_concurrent_sessions', 1000)
        self.cleanup_interval = self.config.get('agent.cleanup_interval', 300)  # 5分钟

    def _start_background_tasks(self) -> None:
        """启动后台任务"""
        # 启动会话清理任务
        self._session_cleanup_task = asyncio.create_task(self._session_cleanup_loop())

    async def _session_cleanup_loop(self) -> None:
        """会话清理循环"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_expired_sessions()
                self._update_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"会话清理任务异常: {str(e)}")

    async def _cleanup_expired_sessions(self) -> None:
        """清理过期会话"""
        current_time = time.time()
        expired_sessions = []

        for session_id, session_data in list(self._active_sessions.items()):
            if current_time - session_data.last_activity > self.session_timeout:
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            self._active_sessions.pop(session_id, None)

        if expired_sessions:
            logger.info(f"清理了 {len(expired_sessions)} 个过期会话")

    def _update_metrics(self) -> None:
        """更新指标"""
        self.metrics.set_gauge('active_sessions', len(self._active_sessions))
        self.metrics.set_gauge('memory_usage', self._get_memory_usage())

    def _get_memory_usage(self) -> float:
        """获取内存使用量（MB）"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0

    @asynccontextmanager
    async     @cache(timeout=300)  # 5分钟缓存
def _get_session(self, user_id: str, session_id: str | None = None):
        """获取或创建会话的上下文管理器"""
        if not session_id:
            session_id = str(uuid.uuid4())

        # 检查并发会话限制
        if len(self._active_sessions) >= self.max_concurrent_sessions:
            raise ValueError("达到最大并发会话数限制")

        # 获取或创建会话
        if session_id in self._active_sessions:
            session_data = self._active_sessions[session_id]
            session_data.last_activity = time.time()
        else:
            session_data = SessionData(
                session_id=session_id,
                user_id=user_id,
                created_at=time.time(),
                last_activity=time.time()
            )
            self._active_sessions[session_id] = session_data

        try:
            yield session_data
        finally:
            # 更新会话活动时间
            session_data.last_activity = time.time()
            session_data.message_count += 1

    async def process_request(self,
                            user_id: str,
                            request_data: dict[str, Any],
                            session_id: str | None = None) -> AgentResponse:
        """
        处理用户关于中医知识、学习和社群的请求

        Args:
            user_id: 用户ID
            request_data: 请求数据，包含请求类型和相关信息
            session_id: 会话ID，如果为None则创建新会话

        Returns:
            AgentResponse: 处理结果
        """
        request_id = str(uuid.uuid4())
        start_time = time.time()

        try:
            # 验证请求
            validation_result = self.validator.validate_request(request_data)
            if not validation_result.is_valid:
                return AgentResponse(
                    request_id=request_id,
                    success=False,
                    content="",
                    error=f"请求验证失败: {validation_result.error_message}"
                )

            # 速率限制检查
            if not await self.rate_limiter.check_rate_limit(user_id):
                return AgentResponse(
                    request_id=request_id,
                    success=False,
                    content="",
                    error="请求频率过高，请稍后重试"
                )

            # 获取请求类型
            request_type = RequestType(request_data.get('type', 'general_inquiry'))

            # 记录请求指标
            self.metrics.increment_counter(f'requests.{request_type.value}')

            # 使用会话上下文管理器
            async with self._get_session(user_id, session_id) as session_data:
                # 根据请求类型分发处理
                if request_type == RequestType.KNOWLEDGE_QUERY:
                    response = await self._process_knowledge_query(request_data, session_data)
                elif request_type == RequestType.CONTENT_CREATION:
                    response = await self._generate_educational_content(request_data, session_data)
                elif request_type == RequestType.COMMUNITY_MANAGEMENT:
                    response = await self._handle_community_request(request_data, session_data)
                elif request_type == RequestType.LEARNING_PATH:
                    response = await self._create_learning_path(request_data, session_data)
                else:
                    response = await self._process_general_inquiry(request_data, session_data)

                # 设置响应元数据
                response.metadata.update({
                    'session_id': session_data.session_id,
                    'processing_time': time.time() - start_time,
                    'timestamp': int(time.time())
                })

                # 记录成功指标
                self.metrics.increment_counter('requests.success')
                self.metrics.record_histogram('request_duration', time.time() - start_time)

                return response

        except Exception as e:
            logger.error("请求处理失败，用户ID: %s, 错误: %s", user_id, str(e))

            # 记录错误指标
            self.metrics.increment_counter('requests.error')

            return AgentResponse(
                request_id=request_id,
                success=False,
                content="",
                error=str(e),
                metadata={
                    'session_id': session_id,
                    'processing_time': time.time() - start_time,
                    'timestamp': int(time.time())
                }
            )

    async def _process_knowledge_query(self,
                                     request_data: dict[str, Any],
                                     session_data: SessionData) -> AgentResponse:
        """处理中医知识查询"""
        query = request_data.get('query', '')
        knowledge_type = request_data.get('knowledge_type', 'general')

        # 检查缓存
        cache_key = f"knowledge_query:{hash(query)}:{knowledge_type}"
        cached_response = await self.cache.get(cache_key)
        if cached_response:
            logger.debug(f"从缓存返回知识查询结果: {query[:50]}...")
            return AgentResponse(**cached_response)

        # 构建提示
        prompt = self._build_knowledge_query_prompt(query, knowledge_type, session_data)

        # 调用LLM生成响应
        try:
            response_text, response_meta = await self.model_factory.generate_chat_completion(
                model=self.primary_model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=self.max_tokens_per_message
            )

            response = AgentResponse(
                request_id=str(uuid.uuid4()),
                success=True,
                content=response_text,
                confidence=response_meta.get('confidence', 0.9),
                metadata={
                    'model': response_meta.get('model', self.primary_model),
                    'query': query,
                    'knowledge_type': knowledge_type
                }
            )

            # 缓存响应
            await self.cache.set(cache_key, asdict(response), ttl=3600)

            return response

        except Exception as e:
            logger.error(f"知识查询处理失败: {str(e)}")
            raise

    def _build_knowledge_query_prompt(self,
                                    query: str,
                                    knowledge_type: str,
                                    session_data: SessionData) -> str:
        """构建知识查询提示"""
        context = session_data.context.get('previous_topics', [])
        context_str = ""
        if context:
            context_str = f"\n\n相关上下文：{', '.join(context[-3:])}"

        return f"""作为老克，请针对以下中医知识查询提供专业且易于理解的回答:

查询: {query}
知识类型: {knowledge_type}{context_str}

请提供:
1. 核心概念解释
2. 历史渊源和发展
3. 现代应用和意义
4. 相关经典文献参考
5. 进一步学习建议

请确保回答准确、专业且易于理解。"""

    async def _generate_educational_content(self,
                                          request_data: dict[str, Any],
                                          session_data: SessionData) -> AgentResponse:
        """生成教育内容"""
        topic = request_data.get('topic', '')
        content_type = request_data.get('content_type', 'article')
        target_audience = request_data.get('target_audience', 'beginner')

        # 构建提示
        prompt = f"""作为老克，请为以下中医主题创建教育内容:

主题: {topic}
内容类型: {content_type}
目标受众: {target_audience}

请提供包含以下要素的结构化内容:
1. 标题和引言
2. 核心知识点（3-5个）
3. 实践应用示例
4. 常见误区澄清
5. 进一步学习资源
6. 互动问题（如适用）

请确保内容适合目标受众的理解水平。"""

        try:
            response_text, response_meta = await self.model_factory.generate_chat_completion(
                model=self.primary_model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=self.max_tokens_per_message
            )

            return AgentResponse(
                request_id=str(uuid.uuid4()),
                success=True,
                content=response_text,
                confidence=response_meta.get('confidence', 0.8),
                metadata={
                    'model': response_meta.get('model', self.primary_model),
                    'topic': topic,
                    'content_type': content_type,
                    'target_audience': target_audience
                }
            )

        except Exception as e:
            logger.error(f"教育内容生成失败: {str(e)}")
            raise

    async def _handle_community_request(self,
                                      request_data: dict[str, Any],
                                      session_data: SessionData) -> AgentResponse:
        """处理社区请求"""
        action = request_data.get('action', '')
        content = request_data.get('content', '')

        # 根据不同的社区操作处理
        if action == 'moderate_content':
            return await self._moderate_content(content, session_data)
        elif action == 'generate_discussion':
            return await self._generate_discussion_topic(content, session_data)
        elif action == 'answer_question':
            return await self._answer_community_question(content, session_data)
        else:
            raise ValueError(f"不支持的社区操作: {action}")

    async def _moderate_content(self, content: str, session_data: SessionData) -> AgentResponse:
        """内容审核"""
        # 实现内容审核逻辑
        prompt = f"""作为老克，请审核以下社区内容是否符合中医知识传播的标准:

内容: {content}

请评估:
1. 内容的准确性
2. 是否包含有害信息
3. 是否符合社区规范
4. 改进建议

请给出审核结果和建议。"""

        try:
            response_text, response_meta = await self.model_factory.generate_chat_completion(
                model=self.primary_model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1024
            )

            return AgentResponse(
                request_id=str(uuid.uuid4()),
                success=True,
                content=response_text,
                confidence=response_meta.get('confidence', 0.9),
                metadata={
                    'action': 'moderate_content',
                    'model': response_meta.get('model', self.primary_model)
                }
            )

        except Exception as e:
            logger.error(f"内容审核失败: {str(e)}")
            raise

    async def _generate_discussion_topic(self, theme: str, session_data: SessionData) -> AgentResponse:
        """生成讨论话题"""
        # 实现讨论话题生成逻辑
        prompt = f"""作为老克，请为以下主题生成有趣的社区讨论话题:

主题: {theme}

请生成:
1. 3-5个讨论问题
2. 每个问题的背景说明
3. 预期的讨论方向
4. 相关的学习资源

确保话题能够激发社区成员的参与和学习兴趣。"""

        try:
            response_text, response_meta = await self.model_factory.generate_chat_completion(
                model=self.primary_model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2048
            )

            return AgentResponse(
                request_id=str(uuid.uuid4()),
                success=True,
                content=response_text,
                confidence=response_meta.get('confidence', 0.8),
                metadata={
                    'action': 'generate_discussion',
                    'theme': theme,
                    'model': response_meta.get('model', self.primary_model)
                }
            )

        except Exception as e:
            logger.error(f"讨论话题生成失败: {str(e)}")
            raise

    async def _answer_community_question(self, question: str, session_data: SessionData) -> AgentResponse:
        """回答社区问题"""
        # 实现社区问题回答逻辑
        prompt = f"""作为老克，请回答以下社区成员的问题:

问题: {question}

请提供:
1. 详细的专业回答
2. 相关的理论依据
3. 实践建议
4. 注意事项
5. 进一步学习的方向

确保回答准确、实用且易于理解。"""

        try:
            response_text, response_meta = await self.model_factory.generate_chat_completion(
                model=self.primary_model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=2048
            )

            return AgentResponse(
                request_id=str(uuid.uuid4()),
                success=True,
                content=response_text,
                confidence=response_meta.get('confidence', 0.9),
                metadata={
                    'action': 'answer_question',
                    'question': question,
                    'model': response_meta.get('model', self.primary_model)
                }
            )

        except Exception as e:
            logger.error(f"社区问题回答失败: {str(e)}")
            raise

    async def _create_learning_path(self,
                                  request_data: dict[str, Any],
                                  session_data: SessionData) -> AgentResponse:
        """创建学习路径"""
        user_level = request_data.get('user_level', 'beginner')
        interests = request_data.get('interests', [])
        goals = request_data.get('goals', [])

        prompt = f"""作为老克，请为用户创建个性化的中医学习路径:

用户水平: {user_level}
兴趣领域: {', '.join(interests)}
学习目标: {', '.join(goals)}

请提供:
1. 学习路径概述
2. 分阶段学习计划（至少3个阶段）
3. 每个阶段的具体内容和时间安排
4. 推荐的学习资源
5. 评估和检验方法
6. 进阶建议

确保学习路径循序渐进，适合用户的水平和目标。"""

        try:
            response_text, response_meta = await self.model_factory.generate_chat_completion(
                model=self.primary_model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=3072
            )

            return AgentResponse(
                request_id=str(uuid.uuid4()),
                success=True,
                content=response_text,
                confidence=response_meta.get('confidence', 0.8),
                metadata={
                    'user_level': user_level,
                    'interests': interests,
                    'goals': goals,
                    'model': response_meta.get('model', self.primary_model)
                }
            )

        except Exception as e:
            logger.error(f"学习路径创建失败: {str(e)}")
            raise

    async def _process_general_inquiry(self,
                                     request_data: dict[str, Any],
                                     session_data: SessionData) -> AgentResponse:
        """处理一般询问"""
        message = request_data.get('message', '')

        # 构建对话历史
        conversation_history = self._build_conversation_history(session_data)

        messages = [
            {"role": "system", "content": self.system_prompt}
        ] + conversation_history + [
            {"role": "user", "content": message}
        ]

        try:
            response_text, response_meta = await self.model_factory.generate_chat_completion(
                model=self.primary_model,
                messages=messages,
                temperature=0.6,
                max_tokens=self.max_tokens_per_message
            )

            # 更新会话上下文
            self._update_session_context(session_data, message, response_text)

            return AgentResponse(
                request_id=str(uuid.uuid4()),
                success=True,
                content=response_text,
                confidence=response_meta.get('confidence', 0.7),
                metadata={
                    'model': response_meta.get('model', self.primary_model),
                    'conversation_turns': session_data.message_count
                }
            )

        except Exception as e:
            logger.error(f"一般询问处理失败: {str(e)}")
            raise

    def _build_conversation_history(self, session_data: SessionData) -> list[dict[str, str]]:
        """构建对话历史"""
        history = session_data.context.get('conversation_history', [])
        # 限制历史长度
        if len(history) > self.max_history_turns * 2:
            history = history[-(self.max_history_turns * 2):]
        return history

    def _update_session_context(self, session_data: SessionData, user_message: str, agent_response: str) -> None:
        """更新会话上下文"""
        if 'conversation_history' not in session_data.context:
            session_data.context['conversation_history'] = []

        session_data.context['conversation_history'].extend([
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": agent_response}
        ])

        # 提取话题关键词
        if 'previous_topics' not in session_data.context:
            session_data.context['previous_topics'] = []

        # 简单的关键词提取（实际应用中可以使用更复杂的NLP技术）
        keywords = self._extract_keywords(user_message)
        session_data.context['previous_topics'].extend(keywords)

        # 限制话题数量
        if len(session_data.context['previous_topics']) > 10:
            session_data.context['previous_topics'] = session_data.context['previous_topics'][-10:]

    def _extract_keywords(self, text: str) -> list[str]:
        """提取关键词（简单实现）"""
        # 中医相关关键词
        tcm_keywords = [
            '中医', '中药', '针灸', '推拿', '气血', '阴阳', '五行', '经络', '穴位',
            '脏腑', '辨证', '论治', '养生', '保健', '食疗', '药膳', '方剂'
        ]

        keywords = []
        for keyword in tcm_keywords:
            if keyword in text:
                keywords.append(keyword)

        return keywords[:3]  # 最多返回3个关键词

    async def get_session_info(self, session_id: str) -> dict[str, Any] | None:
        """获取会话信息"""
        if session_id in self._active_sessions:
            session_data = self._active_sessions[session_id]
            return {
                'session_id': session_data.session_id,
                'user_id': session_data.user_id,
                'created_at': session_data.created_at,
                'last_activity': session_data.last_activity,
                'message_count': session_data.message_count,
                'is_active': time.time() - session_data.last_activity < self.session_timeout
            }
        return None

    async def close_session(self, session_id: str) -> bool:
        """关闭会话"""
        if session_id in self._active_sessions:
            del self._active_sessions[session_id]
            logger.info(f"会话已关闭: {session_id}")
            return True
        return False

    async def close(self) -> None:
        """关闭智能体管理器"""
        try:
            # 取消后台任务
            if self._session_cleanup_task:
                self._session_cleanup_task.cancel()
                try:
                    await self._session_cleanup_task
                except asyncio.CancelledError:
                    pass

            # 清理所有会话
            self._active_sessions.clear()

            # 关闭模型工厂
            if hasattr(self.model_factory, 'close'):
                await self.model_factory.close()

            logger.info("智能体管理器已关闭")

        except Exception as e:
            logger.error(f"智能体管理器关闭失败: {str(e)}")
            raise
