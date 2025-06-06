"""
enhanced_agent_manager - 索克生活项目模块
"""

        import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta
from internal.agent.model_factory import ModelFactory
from internal.repository.knowledge_repository import KnowledgeRepository
from internal.repository.session_repository import SessionRepository
from pkg.utils.connection_pool import RedisConnectionPool, get_pool_manager
from pkg.utils.dependency_injection import ServiceLifecycle, get_container
from pkg.utils.enhanced_config import get_config, get_config_section
from pkg.utils.error_handling import (
from pkg.utils.metrics import get_metrics_collector
from typing import Any
import asyncio
import json
import logging
import os
import uuid

#!/usr/bin/env python3
"""
增强的索尔智能体管理器
集成依赖注入、错误处理、缓存等优化功能
"""

    BusinessLogicException,
    ErrorContext,
    RetryConfig,
    ValidationException,
    get_error_handler,
    retry_async,
)

logger = logging.getLogger(__name__)

@dataclass
class ConversationContext:
    """会话上下文"""
    user_id: str
    session_id: str
    message_type: str
    context: dict[str, Any]
    timestamp: datetime
    request_id: str

class EnhancedAgentManager(ServiceLifecycle):
    """增强的索尔智能体管理器"""

    def __init__(self):
        """初始化智能体管理器"""
        logger.info("初始化增强的索尔智能体管理器")

        # 基础组件
        self.container = get_container()
        self.error_handler = get_error_handler()
        self.metrics = get_metrics_collector()

        # 配置
        self.config = get_config()
        self.conversation_config = get_config_section('conversation')
        self.system_prompt = self.conversation_config.system_prompt
        self.max_history_turns = self.conversation_config.max_history_turns
        self.idle_timeout = self.conversation_config.idle_timeout

        # 核心组件（将在start方法中初始化）
        self.session_repository: SessionRepository | None = None
        self.knowledge_repository: KnowledgeRepository | None = None
        self.model_factory: ModelFactory | None = None
        self.cache: RedisConnectionPool | None = None

        # 提示词模板
        self.prompt_templates: dict[str, str] = {}

        # 活跃会话状态
        self.active_sessions: dict[str, dict[str, Any]] = {}

        # 清理任务
        self._cleanup_task: asyncio.Task | None = None

        logger.info("增强的索尔智能体管理器初始化完成")

    async def start(self) -> None:
        """启动服务"""
        try:
            # 从容器获取依赖
            self.session_repository = self.container.get('session_repository')
            self.knowledge_repository = self.container.get('knowledge_repository')
            self.model_factory = self.container.get('model_factory')

            # 获取缓存连接池
            pool_manager = get_pool_manager()
            self.cache = pool_manager.get_pool('redis')

            # 加载提示词模板
            await self._load_prompt_templates()

            # 启动定期清理任务
            self._cleanup_task = asyncio.create_task(self._schedule_session_cleanup())

            logger.info("增强的索尔智能体管理器启动成功")

        except Exception as e:
            logger.error(f"智能体管理器启动失败: {e}")
            await self.error_handler.handle_error(e)
            raise

    async def stop(self) -> None:
        """停止服务"""
        try:
            # 取消清理任务
            if self._cleanup_task:
                self._cleanup_task.cancel()
                try:
                    await self._cleanup_task
                except asyncio.CancelledError:
                    pass

            # 清理活跃会话
            self.active_sessions.clear()

            logger.info("增强的索尔智能体管理器停止成功")

        except Exception as e:
            logger.error(f"智能体管理器停止失败: {e}")
            await self.error_handler.handle_error(e)

    async def health_check(self) -> bool:
        """健康检查"""
        try:
            # 检查核心组件
            if not all([
                self.session_repository,
                self.knowledge_repository,
                self.model_factory,
                self.cache
            ]):
                return False

            # 检查缓存连接
            if not await self.cache.health_check():
                return False

            return True

        except Exception as e:
            logger.error(f"智能体管理器健康检查失败: {e}")
            return False

    async def _load_prompt_templates(self) -> None:
        """加载提示词模板"""
        try:
            templates_dir = os.path.join("config", "prompts")

            if os.path.exists(templates_dir):
                for filename in os.listdir(templates_dir):
                    if filename.endswith((".txt", ".prompt")):
                        template_name = os.path.splitext(filename)[0]
                        file_path = os.path.join(templates_dir, filename)

                        with open(file_path, encoding="utf-8") as f:
                            self.prompt_templates[template_name] = f.read()

                logger.info(f"已加载{len(self.prompt_templates)}个提示词模板")
            else:
                logger.warning(f"提示词模板目录不存在: {templates_dir}")

        except Exception as e:
            logger.error(f"加载提示词模板失败: {e}")
            await self.error_handler.handle_error(e)

    async def _schedule_session_cleanup(self) -> None:
        """定期清理过期会话"""
        while True:
            try:
                await asyncio.sleep(3600)  # 每小时执行一次

                # 清理内存中的过期会话
                expired_count = await self._cleanup_expired_sessions(max_age_minutes=60)
                logger.info(f"清理了{expired_count}个过期会话")

                # 清理数据库中的过期会话
                if self.session_repository:
                    db_expired_count = await self.session_repository.delete_expired_sessions(days=90)
                    logger.info(f"清理了{db_expired_count}个数据库过期会话")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"会话清理任务异常: {e}")
                await self.error_handler.handle_error(e)

    @retry_async(RetryConfig(max_attempts=3, base_delay=1.0))
    async def process_user_input(
        self,
        user_id: str,
        input_data: dict[str, Any],
        session_id: str | None = None
    ) -> dict[str, Any]:
        """
        处理用户输入

        Args:
            user_id: 用户ID
            input_data: 用户输入数据
            session_id: 会话ID，可选

        Returns:
            Dict[str, Any]: 处理结果
        """
        request_id = str(uuid.uuid4())

        # 创建错误上下文
        error_context = ErrorContext(
            user_id=user_id,
            session_id=session_id,
            request_id=request_id,
            operation="process_user_input"
        )

        try:
            # 验证输入
            await self._validate_input(input_data)

            # 确保会话ID存在
            if not session_id:
                session_id = await self.session_repository.create_session(user_id)
                logger.info(f"为用户{user_id}创建新会话: {session_id}")

            # 记录请求指标
            self.metrics.increment_counter("soer_requests", {"user_id": user_id})

            # 创建会话上下文
            context = ConversationContext(
                user_id=user_id,
                session_id=session_id,
                message_type=input_data.get("type", "text"),
                context=input_data.get("context", {}),
                timestamp=datetime.now(),
                request_id=request_id
            )

            # 检查缓存
            cached_response = await self._get_cached_response(context, input_data)
            if cached_response:
                logger.info(f"返回缓存响应: {request_id}")
                return cached_response

            # 获取用户消息
            user_message = input_data.get("message", "")

            # 获取会话历史
            session_messages = await self.session_repository.get_latest_messages(
                session_id, self.max_history_turns
            )

            # 保存用户消息
            message_metadata = {
                "type": context.message_type,
                "context": context.context,
                "request_id": request_id
            }
            await self.session_repository.save_message(
                session_id, "user", user_message, message_metadata
            )

            # 处理不同类型的用户输入
            response = await self._route_message(context, user_message, session_messages)

            # 保存系统响应
            await self._save_agent_response(context, response)

            # 缓存响应
            await self._cache_response(context, input_data, response)

            # 更新会话信息
            await self._update_session_info(context, response)

            # 记录成功指标
            self.metrics.increment_counter("soer_requests_success", {"user_id": user_id})

            return {
                "session_id": session_id,
                "request_id": request_id,
                "message": response.get("message", ""),
                "type": response.get("type", "text"),
                "suggestions": response.get("suggestions", []),
                "references": response.get("references", []),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            # 记录失败指标
            self.metrics.increment_counter("soer_requests_error", {"user_id": user_id})

            # 处理错误
            await self.error_handler.handle_error(e, error_context)

            # 保存错误消息
            error_message = "抱歉，我现在无法处理您的请求。请稍后再试。"
            if session_id:
                await self.session_repository.save_message(
                    session_id, "agent", error_message,
                    {"error": str(e), "request_id": request_id}
                )

            return {
                "session_id": session_id,
                "request_id": request_id,
                "message": error_message,
                "type": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def _validate_input(self, input_data: dict[str, Any]) -> None:
        """验证输入数据"""
        if not isinstance(input_data, dict):
            raise ValidationException("输入数据必须是字典格式")

        message = input_data.get("message", "")
        if not message or not isinstance(message, str):
            raise ValidationException("消息内容不能为空且必须是字符串")

        if len(message) > 10000:  # 限制消息长度
            raise ValidationException("消息长度不能超过10000字符")

        message_type = input_data.get("type", "text")
        valid_types = ["text", "health_plan_request", "lifestyle_advice", "health_query"]
        if message_type not in valid_types:
            raise ValidationException(f"不支持的消息类型: {message_type}")

    async def _get_cached_response(
        self,
        context: ConversationContext,
        input_data: dict[str, Any]
    ) -> dict[str, Any] | None:
        """获取缓存的响应"""
        try:
            # 生成缓存键
            cache_key = self._generate_cache_key(context.user_id, input_data)

            # 从缓存获取
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                return json.loads(cached_data)

            return None

        except Exception as e:
            logger.warning(f"获取缓存响应失败: {e}")
            return None

    async def _cache_response(
        self,
        context: ConversationContext,
        input_data: dict[str, Any],
        response: dict[str, Any]
    ) -> None:
        """缓存响应"""
        try:
            # 只缓存特定类型的响应
            if response.get("type") in ["health_plan", "lifestyle_advice"]:
                cache_key = self._generate_cache_key(context.user_id, input_data)
                cache_data = json.dumps(response, ensure_ascii=False)

                # 缓存1小时
                await self.cache.set(cache_key, cache_data, ttl=3600)

        except Exception as e:
            logger.warning(f"缓存响应失败: {e}")

    def _generate_cache_key(self, user_id: str, input_data: dict[str, Any]) -> str:
        """生成缓存键"""
        message = input_data.get("message", "")
        message_type = input_data.get("type", "text")

        # 使用消息内容的哈希作为缓存键的一部分
        message_hash = hashlib.md5(message.encode()).hexdigest()

        return f"soer:response:{user_id}:{message_type}:{message_hash}"

    async def _route_message(
        self,
        context: ConversationContext,
        user_message: str,
        session_messages: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """路由消息到相应的处理器"""
        try:
            if context.message_type == "health_plan_request":
                return await self._generate_health_plan(context, user_message, session_messages)
            elif context.message_type == "lifestyle_advice":
                return await self._generate_lifestyle_advice(context, user_message, session_messages)
            elif context.message_type == "health_query":
                return await self._answer_health_query(context, user_message, session_messages)
            else:
                # 默认对话处理
                return await self._handle_general_conversation(context, user_message, session_messages)

        except Exception as e:
            logger.error(f"消息路由失败: {e}")
            raise BusinessLogicException(f"消息处理失败: {e}")

    async def _generate_health_plan(
        self,
        context: ConversationContext,
        user_message: str,
        session_messages: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """生成健康计划"""
        # 这里是简化的实现，实际应该调用模型工厂
        return {
            "message": f"为用户{context.user_id}生成的健康计划：基于您的需求，建议您...",
            "type": "health_plan",
            "suggestions": ["多喝水", "适量运动", "规律作息"],
            "references": []
        }

    async def _generate_lifestyle_advice(
        self,
        context: ConversationContext,
        user_message: str,
        session_messages: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """生成生活方式建议"""
        return {
            "message": f"生活方式建议：{user_message}",
            "type": "lifestyle_advice",
            "suggestions": ["保持积极心态", "均衡饮食"],
            "references": []
        }

    async def _answer_health_query(
        self,
        context: ConversationContext,
        user_message: str,
        session_messages: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """回答健康咨询"""
        return {
            "message": f"关于您的健康咨询：{user_message}",
            "type": "health_query",
            "suggestions": [],
            "references": []
        }

    async def _handle_general_conversation(
        self,
        context: ConversationContext,
        user_message: str,
        session_messages: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """处理一般对话"""
        return {
            "message": f"您好！我是索儿，很高兴为您服务。关于「{user_message}」，我来为您解答...",
            "type": "text",
            "suggestions": [],
            "references": []
        }

    async def _save_agent_response(
        self,
        context: ConversationContext,
        response: dict[str, Any]
    ) -> None:
        """保存智能体响应"""
        agent_message = response.get("message", "")
        agent_metadata = {
            "type": response.get("type", "text"),
            "request_id": context.request_id,
            "suggestions": response.get("suggestions", []),
            "references": response.get("references", [])
        }

        await self.session_repository.save_message(
            context.session_id, "agent", agent_message, agent_metadata
        )

    async def _update_session_info(
        self,
        context: ConversationContext,
        response: dict[str, Any]
    ) -> None:
        """更新会话信息"""
        session_update = {
            "last_activity": context.timestamp.isoformat(),
            "message_count": 1  # 这里应该从数据库获取实际计数
        }

        await self.session_repository.update_session(context.session_id, session_update)

    async def _cleanup_expired_sessions(self, max_age_minutes: int = 60) -> int:
        """清理过期会话"""
        expired_count = 0
        cutoff_time = datetime.now() - timedelta(minutes=max_age_minutes)

        expired_sessions = []
        for session_id, session_data in self.active_sessions.items():
            last_activity = session_data.get("last_activity")
            if last_activity and last_activity < cutoff_time:
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            del self.active_sessions[session_id]
            expired_count += 1

        return expired_count

    def get_active_sessions(self) -> dict[str, dict[str, Any]]:
        """获取活跃会话"""
        return self.active_sessions.copy()

    async def get_session_stats(self) -> dict[str, Any]:
        """获取会话统计信息"""
        return {
            "active_sessions": len(self.active_sessions),
            "total_sessions": await self.session_repository.get_session_count() if self.session_repository else 0,
            "avg_session_duration": 0,  # 这里应该计算实际的平均会话时长
            "timestamp": datetime.now().isoformat()
        }
