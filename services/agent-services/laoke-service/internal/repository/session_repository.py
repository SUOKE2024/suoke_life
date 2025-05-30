#!/usr/bin/env python

"""
老克智能体服务 - 会话存储库
提供用户与智能体的会话管理和持久化
"""

import logging
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import motor.motor_asyncio
from pymongo.errors import PyMongoError

from pkg.utils.config import Config
from pkg.utils.metrics import get_metrics_collector

logger = logging.getLogger(__name__)
metrics = get_metrics_collector()

class SessionRepository:
    """会话存储库，提供用户与智能体的会话管理和持久化"""

    def __init__(self):
        """初始化会话存储库"""
        self.config = Config()
        self.db_config = self.config.get_section("database.mongodb")

        # 连接到MongoDB
        self.client = motor.motor_asyncio.AsyncIOMotorClient(self.db_config.get("uri"))
        self.db = self.client[self.db_config.get("database", "laoke_db")]

        # 集合
        self.sessions = self.db.sessions
        self.messages = self.db.messages

        logger.info("会话存储库已初始化")

    async def init_indexes(self):
        """初始化数据库索引"""
        try:
            # 会话集合索引
            await self.sessions.create_index("user_id")
            await self.sessions.create_index("created_at")
            await self.sessions.create_index("updated_at")
            await self.sessions.create_index([("session_id", 1)], unique=True)

            # 消息集合索引
            await self.messages.create_index("session_id")
            await self.messages.create_index("created_at")
            await self.messages.create_index([("message_id", 1)], unique=True)

            logger.info("会话存储库索引已初始化")
        except PyMongoError as e:
            logger.error(f"初始化会话存储库索引失败: {str(e)}")
            raise

    @metrics.measure_execution_time("session_repo_create_session")
    async def create_session(self, user_id: str, metadata: dict[str, Any] | None = None) -> str:
        """
        创建新的会话

        Args:
            user_id: 用户ID
            metadata: 会话元数据

        Returns:
            str: 创建的会话ID
        """
        try:
            session_id = str(uuid.uuid4())
            now = datetime.now(UTC).isoformat()

            session_data = {
                "session_id": session_id,
                "user_id": user_id,
                "created_at": now,
                "updated_at": now,
                "metadata": metadata or {},
                "status": "active",
                "message_count": 0
            }

            await self.sessions.insert_one(session_data)
            logger.debug(f"创建会话: session_id={session_id}, user_id={user_id}")

            return session_id
        except PyMongoError as e:
            logger.error(f"创建会话失败: {str(e)}")
            metrics.increment_counter("session_repo_errors", {"method": "create_session"})
            raise

    @metrics.measure_execution_time("session_repo_find_by_id")
    async def find_by_id(self, session_id: str) -> dict[str, Any] | None:
        """
        根据ID查找会话

        Args:
            session_id: 会话ID

        Returns:
            Optional[Dict[str, Any]]: 会话信息，未找到时返回None
        """
        try:
            session = await self.sessions.find_one({"session_id": session_id})

            if session:
                # 处理ObjectId
                if "_id" in session:
                    session["id"] = str(session.pop("_id"))

                return session

            return None
        except PyMongoError as e:
            logger.error(f"查找会话失败: {str(e)}")
            metrics.increment_counter("session_repo_errors", {"method": "find_by_id"})
            return None

    @metrics.measure_execution_time("session_repo_find_by_user_id")
    async def find_by_user_id(self, user_id: str, limit: int = 10, offset: int = 0) -> list[dict[str, Any]]:
        """
        根据用户ID查找会话列表

        Args:
            user_id: 用户ID
            limit: 返回记录数量限制
            offset: 分页偏移量

        Returns:
            List[Dict[str, Any]]: 会话列表
        """
        try:
            cursor = self.sessions.find({"user_id": user_id}) \
                .sort("updated_at", -1) \
                .skip(offset) \
                .limit(limit)

            sessions = await cursor.to_list(length=limit)

            # 处理ObjectId
            for session in sessions:
                if "_id" in session:
                    session["id"] = str(session.pop("_id"))

            return sessions
        except PyMongoError as e:
            logger.error(f"根据用户ID查找会话失败: {str(e)}")
            metrics.increment_counter("session_repo_errors", {"method": "find_by_user_id"})
            return []

    @metrics.measure_execution_time("session_repo_update_session")
    async def update_session(self, session_id: str, update_data: dict[str, Any]) -> bool:
        """
        更新会话信息

        Args:
            session_id: 会话ID
            update_data: 更新的字段数据

        Returns:
            bool: 是否更新成功
        """
        try:
            # 总是更新updated_at字段
            update_data["updated_at"] = datetime.now(UTC).isoformat()

            result = await self.sessions.update_one(
                {"session_id": session_id},
                {"$set": update_data}
            )

            return result.matched_count > 0
        except PyMongoError as e:
            logger.error(f"更新会话失败: {str(e)}")
            metrics.increment_counter("session_repo_errors", {"method": "update_session"})
            return False

    @metrics.measure_execution_time("session_repo_end_session")
    async def end_session(self, session_id: str) -> bool:
        """
        结束会话

        Args:
            session_id: 会话ID

        Returns:
            bool: 是否成功结束会话
        """
        try:
            update_data = {
                "status": "ended",
                "ended_at": datetime.now(UTC).isoformat(),
                "updated_at": datetime.now(UTC).isoformat()
            }

            result = await self.sessions.update_one(
                {"session_id": session_id, "status": "active"},
                {"$set": update_data}
            )

            return result.matched_count > 0
        except PyMongoError as e:
            logger.error(f"结束会话失败: {str(e)}")
            metrics.increment_counter("session_repo_errors", {"method": "end_session"})
            return False

    @metrics.measure_execution_time("session_repo_save_message")
    async def save_message(self,
                          session_id: str,
                          role: str,
                          content: str,
                          metadata: dict[str, Any] | None = None) -> str | None:
        """
        保存会话消息

        Args:
            session_id: 会话ID
            role: 消息角色(user/agent)
            content: 消息内容
            metadata: 消息元数据

        Returns:
            Optional[str]: 消息ID，失败时返回None
        """
        try:
            # 检查会话是否存在
            session = await self.find_by_id(session_id)
            if not session:
                logger.warning(f"保存消息失败: 会话不存在 session_id={session_id}")
                return None

            # 只有活跃会话才能添加消息
            if session.get("status") != "active":
                logger.warning(f"保存消息失败: 会话已结束 session_id={session_id}")
                return None

            # 创建消息
            message_id = str(uuid.uuid4())
            now = datetime.now(UTC).isoformat()

            message_data = {
                "message_id": message_id,
                "session_id": session_id,
                "role": role,
                "content": content,
                "metadata": metadata or {},
                "created_at": now
            }

            # 保存消息
            await self.messages.insert_one(message_data)

            # 更新会话
            await self.sessions.update_one(
                {"session_id": session_id},
                {
                    "$set": {"updated_at": now},
                    "$inc": {"message_count": 1}
                }
            )

            logger.debug(f"保存消息: message_id={message_id}, session_id={session_id}, role={role}")

            return message_id
        except PyMongoError as e:
            logger.error(f"保存消息失败: {str(e)}")
            metrics.increment_counter("session_repo_errors", {"method": "save_message"})
            return None

    @metrics.measure_execution_time("session_repo_get_messages")
    async def get_messages(self,
                          session_id: str,
                          limit: int = 50,
                          before_id: str | None = None) -> list[dict[str, Any]]:
        """
        获取会话消息列表

        Args:
            session_id: 会话ID
            limit: 返回记录数量限制
            before_id: 获取指定消息ID之前的消息

        Returns:
            List[Dict[str, Any]]: 消息列表
        """
        try:
            # 构建查询条件
            query = {"session_id": session_id}

            # 如果指定了before_id，获取该消息之前的消息
            if before_id:
                # 首先获取指定消息的创建时间
                before_message = await self.messages.find_one({"message_id": before_id})
                if before_message:
                    query["created_at"] = {"$lt": before_message["created_at"]}

            # 执行查询
            cursor = self.messages.find(query) \
                .sort("created_at", -1) \
                .limit(limit)

            messages = await cursor.to_list(length=limit)

            # 处理ObjectId并按时间正序返回
            for message in messages:
                if "_id" in message:
                    message["id"] = str(message.pop("_id"))

            # 按时间正序排列
            messages.sort(key=lambda x: x["created_at"])

            return messages
        except PyMongoError as e:
            logger.error(f"获取会话消息失败: {str(e)}")
            metrics.increment_counter("session_repo_errors", {"method": "get_messages"})
            return []

    @metrics.measure_execution_time("session_repo_get_latest_messages")
    async def get_latest_messages(self, session_id: str, count: int = 10) -> list[dict[str, Any]]:
        """
        获取最新的会话消息

        Args:
            session_id: 会话ID
            count: 获取消息数量

        Returns:
            List[Dict[str, Any]]: 消息列表
        """
        try:
            cursor = self.messages.find({"session_id": session_id}) \
                .sort("created_at", -1) \
                .limit(count)

            messages = await cursor.to_list(length=count)

            # 处理ObjectId并按时间正序返回
            for message in messages:
                if "_id" in message:
                    message["id"] = str(message.pop("_id"))

            # 按时间正序排列
            messages.sort(key=lambda x: x["created_at"])

            return messages
        except PyMongoError as e:
            logger.error(f"获取最新会话消息失败: {str(e)}")
            metrics.increment_counter("session_repo_errors", {"method": "get_latest_messages"})
            return []

    @metrics.measure_execution_time("session_repo_get_session_summary")
    async def get_session_summary(self, session_id: str) -> dict[str, Any] | None:
        """
        获取会话摘要

        Args:
            session_id: 会话ID

        Returns:
            Optional[Dict[str, Any]]: 会话摘要信息
        """
        try:
            # 获取会话信息
            session = await self.find_by_id(session_id)
            if not session:
                return None

            # 获取最后一条消息
            last_message = None
            cursor = self.messages.find({"session_id": session_id}) \
                .sort("created_at", -1) \
                .limit(1)

            messages = await cursor.to_list(length=1)
            if messages:
                last_message = messages[0]
                if "_id" in last_message:
                    last_message["id"] = str(last_message.pop("_id"))

            # 构建摘要
            summary = {
                "session_id": session["session_id"],
                "user_id": session["user_id"],
                "created_at": session["created_at"],
                "updated_at": session["updated_at"],
                "status": session["status"],
                "message_count": session["message_count"],
                "metadata": session["metadata"],
                "last_message": last_message
            }

            return summary
        except PyMongoError as e:
            logger.error(f"获取会话摘要失败: {str(e)}")
            metrics.increment_counter("session_repo_errors", {"method": "get_session_summary"})
            return None

    @metrics.measure_execution_time("session_repo_delete_expired_sessions")
    async def delete_expired_sessions(self, days: int = 90) -> int:
        """
        删除过期会话

        Args:
            days: 会话保留天数

        Returns:
            int: 删除的会话数量
        """
        try:
            # 计算过期时间
            expire_time = (datetime.now(UTC) - timedelta(days=days)).isoformat()

            # 查找过期会话
            cursor = self.sessions.find({"updated_at": {"$lt": expire_time}})
            expired_sessions = await cursor.to_list(length=None)

            deleted_count = 0

            # 删除过期会话及其消息
            for session in expired_sessions:
                session_id = session["session_id"]

                # 删除会话消息
                message_result = await self.messages.delete_many({"session_id": session_id})

                # 删除会话
                session_result = await self.sessions.delete_one({"session_id": session_id})

                if session_result.deleted_count > 0:
                    deleted_count += 1
                    logger.info(f"删除过期会话: session_id={session_id}, 消息数量={message_result.deleted_count}")

            return deleted_count
        except PyMongoError as e:
            logger.error(f"删除过期会话失败: {str(e)}")
            metrics.increment_counter("session_repo_errors", {"method": "delete_expired_sessions"})
            return 0
