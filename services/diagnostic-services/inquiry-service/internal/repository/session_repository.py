"""
会话存储库模块 - 处理会话数据的持久化存储
"""

from datetime import datetime, timedelta
import json
import logging
from typing import Any
import uuid

import aioredis
from sqlalchemy import and_, delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from ..models.session_models import InquirySession, SessionMessage, SessionSummary

logger = logging.getLogger(__name__)


class SessionRepository:
    """会话存储库"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化会话存储库
        
        Args:
            config: 配置信息
        """
        self.config = config
        self.db_config = config.get("database", {})
        self.cache_config = config.get("cache", {})

        # 数据库配置
        self.db_url = self.db_config.get("url", "postgresql+asyncpg://user:pass@localhost/inquiry_db")
        self.db_pool_size = self.db_config.get("pool_size", 10)
        self.db_max_overflow = self.db_config.get("max_overflow", 20)

        # 缓存配置
        self.cache_enabled = self.cache_config.get("enabled", True)
        self.cache_url = self.cache_config.get("url", "redis://localhost:6379/0")
        self.cache_ttl = self.cache_config.get("session_ttl_seconds", 3600)

        # 初始化数据库引擎
        self.engine = None
        self.async_session = None

        # 初始化Redis客户端
        self.redis_client = None

        logger.info("会话存储库初始化完成")

    async def initialize(self) -> None:
        """初始化存储库连接"""
        try:
            # 初始化数据库连接
            self.engine = create_async_engine(
                self.db_url,
                pool_size=self.db_pool_size,
                max_overflow=self.db_max_overflow,
                echo=False
            )

            self.async_session = sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )

            # 初始化Redis连接
            if self.cache_enabled:
                self.redis_client = await aioredis.from_url(
                    self.cache_url,
                    encoding="utf-8",
                    decode_responses=True
                )

            logger.info("存储库连接初始化成功")

        except Exception as e:
            logger.error(f"存储库连接初始化失败: {e}")
            raise

    async def close(self) -> None:
        """关闭存储库连接"""
        try:
            if self.redis_client:
                await self.redis_client.close()

            if self.engine:
                await self.engine.dispose()

            logger.info("存储库连接已关闭")

        except Exception as e:
            logger.error(f"关闭存储库连接失败: {e}")

    async def create_session(self, session_data: dict[str, Any]) -> str:
        """
        创建新的问诊会话
        
        Args:
            session_data: 会话数据
            
        Returns:
            str: 会话ID
        """
        try:
            session_id = str(uuid.uuid4())

            # 创建会话对象
            session = InquirySession(
                session_id=session_id,
                user_id=session_data.get("user_id"),
                agent_id=session_data.get("agent_id", "xiaoai"),
                status="active",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                metadata=session_data.get("metadata", {})
            )

            # 保存到数据库
            async with self.async_session() as db_session:
                db_session.add(session)
                await db_session.commit()

            # 缓存会话信息
            if self.cache_enabled:
                await self._cache_session(session_id, session_data)

            logger.info(f"创建会话成功: {session_id}")
            return session_id

        except Exception as e:
            logger.error(f"创建会话失败: {e}")
            raise

    async def get_session(self, session_id: str) -> dict[str, Any] | None:
        """
        获取会话信息
        
        Args:
            session_id: 会话ID
            
        Returns:
            Optional[Dict]: 会话信息
        """
        try:
            # 先从缓存获取
            if self.cache_enabled:
                cached_session = await self._get_cached_session(session_id)
                if cached_session:
                    return cached_session

            # 从数据库获取
            async with self.async_session() as db_session:
                result = await db_session.execute(
                    select(InquirySession).where(InquirySession.session_id == session_id)
                )
                session = result.scalar_one_or_none()

                if session:
                    session_data = {
                        "session_id": session.session_id,
                        "user_id": session.user_id,
                        "agent_id": session.agent_id,
                        "status": session.status,
                        "created_at": session.created_at.isoformat(),
                        "updated_at": session.updated_at.isoformat(),
                        "metadata": session.metadata or {}
                    }

                    # 更新缓存
                    if self.cache_enabled:
                        await self._cache_session(session_id, session_data)

                    return session_data

            return None

        except Exception as e:
            logger.error(f"获取会话失败: {e}")
            return None

    async def update_session(self, session_id: str, updates: dict[str, Any]) -> bool:
        """
        更新会话信息
        
        Args:
            session_id: 会话ID
            updates: 更新数据
            
        Returns:
            bool: 更新是否成功
        """
        try:
            # 更新数据库
            async with self.async_session() as db_session:
                result = await db_session.execute(
                    update(InquirySession)
                    .where(InquirySession.session_id == session_id)
                    .values(
                        status=updates.get("status"),
                        updated_at=datetime.utcnow(),
                        metadata=updates.get("metadata")
                    )
                )

                if result.rowcount > 0:
                    await db_session.commit()

                    # 清除缓存
                    if self.cache_enabled:
                        await self._clear_session_cache(session_id)

                    logger.info(f"更新会话成功: {session_id}")
                    return True

            return False

        except Exception as e:
            logger.error(f"更新会话失败: {e}")
            return False

    async def delete_session(self, session_id: str) -> bool:
        """
        删除会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            bool: 删除是否成功
        """
        try:
            async with self.async_session() as db_session:
                # 删除会话消息
                await db_session.execute(
                    delete(SessionMessage).where(SessionMessage.session_id == session_id)
                )

                # 删除会话总结
                await db_session.execute(
                    delete(SessionSummary).where(SessionSummary.session_id == session_id)
                )

                # 删除会话
                result = await db_session.execute(
                    delete(InquirySession).where(InquirySession.session_id == session_id)
                )

                if result.rowcount > 0:
                    await db_session.commit()

                    # 清除缓存
                    if self.cache_enabled:
                        await self._clear_session_cache(session_id)

                    logger.info(f"删除会话成功: {session_id}")
                    return True

            return False

        except Exception as e:
            logger.error(f"删除会话失败: {e}")
            return False

    async def add_message(self, session_id: str, message_data: dict[str, Any]) -> str:
        """
        添加会话消息
        
        Args:
            session_id: 会话ID
            message_data: 消息数据
            
        Returns:
            str: 消息ID
        """
        try:
            message_id = str(uuid.uuid4())

            message = SessionMessage(
                message_id=message_id,
                session_id=session_id,
                role=message_data.get("role", "user"),
                content=message_data.get("content", ""),
                timestamp=datetime.utcnow(),
                metadata=message_data.get("metadata", {})
            )

            async with self.async_session() as db_session:
                db_session.add(message)
                await db_session.commit()

            # 清除会话缓存以确保一致性
            if self.cache_enabled:
                await self._clear_session_cache(session_id)

            logger.debug(f"添加消息成功: {message_id}")
            return message_id

        except Exception as e:
            logger.error(f"添加消息失败: {e}")
            raise

    async def get_session_messages(self, session_id: str, limit: int = 50) -> list[dict[str, Any]]:
        """
        获取会话消息
        
        Args:
            session_id: 会话ID
            limit: 消息数量限制
            
        Returns:
            List[Dict]: 消息列表
        """
        try:
            async with self.async_session() as db_session:
                result = await db_session.execute(
                    select(SessionMessage)
                    .where(SessionMessage.session_id == session_id)
                    .order_by(SessionMessage.timestamp.desc())
                    .limit(limit)
                )

                messages = result.scalars().all()

                return [
                    {
                        "message_id": msg.message_id,
                        "session_id": msg.session_id,
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat(),
                        "metadata": msg.metadata or {}
                    }
                    for msg in reversed(messages)  # 按时间正序返回
                ]

        except Exception as e:
            logger.error(f"获取会话消息失败: {e}")
            return []

    async def save_session_summary(self, session_id: str, summary_data: dict[str, Any]) -> str:
        """
        保存会话总结
        
        Args:
            session_id: 会话ID
            summary_data: 总结数据
            
        Returns:
            str: 总结ID
        """
        try:
            summary_id = str(uuid.uuid4())

            summary = SessionSummary(
                summary_id=summary_id,
                session_id=session_id,
                summary_text=summary_data.get("summary_text", ""),
                extracted_symptoms=summary_data.get("extracted_symptoms", []),
                tcm_patterns=summary_data.get("tcm_patterns", []),
                health_risks=summary_data.get("health_risks", []),
                recommendations=summary_data.get("recommendations", []),
                created_at=datetime.utcnow(),
                metadata=summary_data.get("metadata", {})
            )

            async with self.async_session() as db_session:
                db_session.add(summary)
                await db_session.commit()

            logger.info(f"保存会话总结成功: {summary_id}")
            return summary_id

        except Exception as e:
            logger.error(f"保存会话总结失败: {e}")
            raise

    async def get_session_summary(self, session_id: str) -> dict[str, Any] | None:
        """
        获取会话总结
        
        Args:
            session_id: 会话ID
            
        Returns:
            Optional[Dict]: 会话总结
        """
        try:
            async with self.async_session() as db_session:
                result = await db_session.execute(
                    select(SessionSummary).where(SessionSummary.session_id == session_id)
                )

                summary = result.scalar_one_or_none()

                if summary:
                    return {
                        "summary_id": summary.summary_id,
                        "session_id": summary.session_id,
                        "summary_text": summary.summary_text,
                        "extracted_symptoms": summary.extracted_symptoms or [],
                        "tcm_patterns": summary.tcm_patterns or [],
                        "health_risks": summary.health_risks or [],
                        "recommendations": summary.recommendations or [],
                        "created_at": summary.created_at.isoformat(),
                        "metadata": summary.metadata or {}
                    }

            return None

        except Exception as e:
            logger.error(f"获取会话总结失败: {e}")
            return None

    async def get_user_sessions(self, user_id: str, limit: int = 20) -> list[dict[str, Any]]:
        """
        获取用户的会话列表
        
        Args:
            user_id: 用户ID
            limit: 数量限制
            
        Returns:
            List[Dict]: 会话列表
        """
        try:
            async with self.async_session() as db_session:
                result = await db_session.execute(
                    select(InquirySession)
                    .where(InquirySession.user_id == user_id)
                    .order_by(InquirySession.created_at.desc())
                    .limit(limit)
                )

                sessions = result.scalars().all()

                return [
                    {
                        "session_id": session.session_id,
                        "user_id": session.user_id,
                        "agent_id": session.agent_id,
                        "status": session.status,
                        "created_at": session.created_at.isoformat(),
                        "updated_at": session.updated_at.isoformat(),
                        "metadata": session.metadata or {}
                    }
                    for session in sessions
                ]

        except Exception as e:
            logger.error(f"获取用户会话列表失败: {e}")
            return []

    async def cleanup_expired_sessions(self, expiry_hours: int = 24) -> int:
        """
        清理过期会话
        
        Args:
            expiry_hours: 过期时间（小时）
            
        Returns:
            int: 清理的会话数量
        """
        try:
            expiry_time = datetime.utcnow() - timedelta(hours=expiry_hours)

            async with self.async_session() as db_session:
                # 获取过期会话ID
                result = await db_session.execute(
                    select(InquirySession.session_id)
                    .where(
                        and_(
                            InquirySession.updated_at < expiry_time,
                            InquirySession.status.in_(["completed", "abandoned"])
                        )
                    )
                )

                expired_session_ids = [row[0] for row in result.fetchall()]

                if expired_session_ids:
                    # 删除相关数据
                    await db_session.execute(
                        delete(SessionMessage).where(
                            SessionMessage.session_id.in_(expired_session_ids)
                        )
                    )

                    await db_session.execute(
                        delete(SessionSummary).where(
                            SessionSummary.session_id.in_(expired_session_ids)
                        )
                    )

                    await db_session.execute(
                        delete(InquirySession).where(
                            InquirySession.session_id.in_(expired_session_ids)
                        )
                    )

                    await db_session.commit()

                    # 清理缓存
                    if self.cache_enabled:
                        for session_id in expired_session_ids:
                            await self._clear_session_cache(session_id)

                    logger.info(f"清理过期会话: {len(expired_session_ids)}个")
                    return len(expired_session_ids)

            return 0

        except Exception as e:
            logger.error(f"清理过期会话失败: {e}")
            return 0

    # 缓存相关方法
    async def _cache_session(self, session_id: str, session_data: dict[str, Any]) -> None:
        """缓存会话数据"""
        if not self.redis_client:
            return

        try:
            cache_key = f"session:{session_id}"
            await self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(session_data, default=str)
            )
        except Exception as e:
            logger.warning(f"缓存会话数据失败: {e}")

    async def _get_cached_session(self, session_id: str) -> dict[str, Any] | None:
        """获取缓存的会话数据"""
        if not self.redis_client:
            return None

        try:
            cache_key = f"session:{session_id}"
            cached_data = await self.redis_client.get(cache_key)

            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"获取缓存会话数据失败: {e}")

        return None

    async def _clear_session_cache(self, session_id: str) -> None:
        """清除会话缓存"""
        if not self.redis_client:
            return

        try:
            cache_key = f"session:{session_id}"
            await self.redis_client.delete(cache_key)
        except Exception as e:
            logger.warning(f"清除会话缓存失败: {e}")

    async def get_session_statistics(self, user_id: str | None = None) -> dict[str, Any]:
        """
        获取会话统计信息
        
        Args:
            user_id: 用户ID（可选）
            
        Returns:
            Dict: 统计信息
        """
        try:
            async with self.async_session() as db_session:
                # 基础查询
                base_query = select(InquirySession)
                if user_id:
                    base_query = base_query.where(InquirySession.user_id == user_id)

                # 总会话数
                total_result = await db_session.execute(base_query)
                total_sessions = len(total_result.scalars().all())

                # 活跃会话数
                active_result = await db_session.execute(
                    base_query.where(InquirySession.status == "active")
                )
                active_sessions = len(active_result.scalars().all())

                # 已完成会话数
                completed_result = await db_session.execute(
                    base_query.where(InquirySession.status == "completed")
                )
                completed_sessions = len(completed_result.scalars().all())

                return {
                    "total_sessions": total_sessions,
                    "active_sessions": active_sessions,
                    "completed_sessions": completed_sessions,
                    "abandoned_sessions": total_sessions - active_sessions - completed_sessions,
                    "completion_rate": completed_sessions / total_sessions if total_sessions > 0 else 0
                }

        except Exception as e:
            logger.error(f"获取会话统计信息失败: {e}")
            return {
                "total_sessions": 0,
                "active_sessions": 0,
                "completed_sessions": 0,
                "abandoned_sessions": 0,
                "completion_rate": 0
            }
