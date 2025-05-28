#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
小克智能体服务 - 会话存储库
提供用户与小克智能体的会话管理和持久化
"""

import uuid
import logging
import asyncio
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Tuple

import motor.motor_asyncio
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError

from pkg.utils.config_loader import get_config
from pkg.utils.metrics import get_metrics_collector

logger = logging.getLogger(__name__)
metrics = get_metrics_collector()


class SessionRepository:
    """会话存储库，提供用户与小克智能体的会话管理和持久化"""

    def __init__(self):
        """初始化会话存储库"""
        self.config = get_config()
        self.db_config = self.config.get_section("database.mongodb")

        # 连接到MongoDB
        self.client = motor.motor_asyncio.AsyncIOMotorClient(self.db_config.get("uri"))
        self.db = self.client[self.db_config.get("database", "xiaoke_db")]

        # 集合
        self.sessions = self.db.sessions
        self.messages = self.db.messages
        self.memory_anchors = self.db.memory_anchors  # 记忆锚点，用于长期记忆标记
        self.dialogue_records = (
            self.db.dialogue_records
        )  # 对话记录，包含更丰富的上下文信息

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

            # 记忆锚点索引
            await self.memory_anchors.create_index("user_id")
            await self.memory_anchors.create_index("topic")
            await self.memory_anchors.create_index("created_at")

            # 对话记录索引
            await self.dialogue_records.create_index("user_id")
            await self.dialogue_records.create_index("session_id")
            await self.dialogue_records.create_index("created_at")

            logger.info("会话存储库索引已初始化")
        except PyMongoError as e:
            logger.error(f"初始化会话存储库索引失败: {str(e)}")
            raise

    @metrics.measure_execution_time("session_repo_create_session")
    async def create_session(
        self, user_id: str, metadata: Optional[Dict[str, Any]] = None
    ) -> str:
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
            now = datetime.now(timezone.utc).isoformat()

            session_data = {
                "session_id": session_id,
                "user_id": user_id,
                "created_at": now,
                "updated_at": now,
                "metadata": metadata or {},
                "status": "active",
                "message_count": 0,
                "tags": [],
                "context": {},  # 会话上下文数据
                "diagnosis_state": {},  # 诊断状态信息
            }

            await self.sessions.insert_one(session_data)
            logger.debug(f"创建会话: session_id={session_id}, user_id={user_id}")

            return session_id
        except PyMongoError as e:
            logger.error(f"创建会话失败: {str(e)}")
            metrics.increment_counter(
                "session_repo_errors", {"method": "create_session"}
            )
            raise

    @metrics.measure_execution_time("session_repo_find_by_id")
    async def find_by_id(self, session_id: str) -> Optional[Dict[str, Any]]:
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
    async def find_by_user_id(
        self, user_id: str, limit: int = 10, offset: int = 0
    ) -> List[Dict[str, Any]]:
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
            cursor = (
                self.sessions.find({"user_id": user_id})
                .sort("updated_at", -1)
                .skip(offset)
                .limit(limit)
            )

            sessions = await cursor.to_list(length=limit)

            # 处理ObjectId
            for session in sessions:
                if "_id" in session:
                    session["id"] = str(session.pop("_id"))

            return sessions
        except PyMongoError as e:
            logger.error(f"根据用户ID查找会话失败: {str(e)}")
            metrics.increment_counter(
                "session_repo_errors", {"method": "find_by_user_id"}
            )
            return []

    @metrics.measure_execution_time("session_repo_update_session")
    async def update_session(
        self, session_id: str, update_data: Dict[str, Any]
    ) -> bool:
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
            update_data["updated_at"] = datetime.now(timezone.utc).isoformat()

            result = await self.sessions.update_one(
                {"session_id": session_id}, {"$set": update_data}
            )

            return result.matched_count > 0
        except PyMongoError as e:
            logger.error(f"更新会话失败: {str(e)}")
            metrics.increment_counter(
                "session_repo_errors", {"method": "update_session"}
            )
            return False

    @metrics.measure_execution_time("session_repo_update_diagnosis_state")
    async def update_diagnosis_state(
        self, session_id: str, diagnosis_state: Dict[str, Any]
    ) -> bool:
        """
        更新诊断状态

        Args:
            session_id: 会话ID
            diagnosis_state: 诊断状态数据

        Returns:
            bool: 是否更新成功
        """
        try:
            # 添加更新时间
            diagnosis_state["updated_at"] = datetime.now(timezone.utc).isoformat()

            result = await self.sessions.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "diagnosis_state": diagnosis_state,
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                    }
                },
            )

            return result.matched_count > 0
        except PyMongoError as e:
            logger.error(f"更新诊断状态失败: {str(e)}")
            metrics.increment_counter(
                "session_repo_errors", {"method": "update_diagnosis_state"}
            )
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
                "ended_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }

            result = await self.sessions.update_one(
                {"session_id": session_id, "status": "active"}, {"$set": update_data}
            )

            return result.matched_count > 0
        except PyMongoError as e:
            logger.error(f"结束会话失败: {str(e)}")
            metrics.increment_counter("session_repo_errors", {"method": "end_session"})
            return False

    @metrics.measure_execution_time("session_repo_save_message")
    async def save_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
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
            now = datetime.now(timezone.utc).isoformat()

            message_data = {
                "message_id": message_id,
                "session_id": session_id,
                "role": role,
                "content": content,
                "created_at": now,
                "metadata": metadata or {},
                "importance": metadata.get("importance", 0)
                if metadata
                else 0,  # 消息重要性评分
                "topics": metadata.get("topics", [])
                if metadata
                else [],  # 消息主题标签
                "diagnosis_step": metadata.get("diagnosis_step", "")
                if metadata
                else "",  # 诊断步骤
            }

            await self.messages.insert_one(message_data)

            # 更新会话消息计数
            await self.sessions.update_one(
                {"session_id": session_id},
                {"$inc": {"message_count": 1}, "$set": {"updated_at": now}},
            )

            # 提取重要记忆
            if role == "agent" and metadata and metadata.get("is_memory_anchor", False):
                await self._create_memory_anchor(
                    user_id=session["user_id"],
                    content=content,
                    topic=metadata.get("topic", "general"),
                    context=metadata.get("context", {}),
                )

            # 如果是诊断相关消息，更新对话记录集合
            if metadata and metadata.get("diagnosis_related", False):
                await self._update_dialogue_record(
                    user_id=session["user_id"],
                    session_id=session_id,
                    message_id=message_id,
                    role=role,
                    content=content,
                    diagnosis_step=metadata.get("diagnosis_step", ""),
                    symptoms=metadata.get("symptoms", []),
                    diagnosis_data=metadata.get("diagnosis_data", {}),
                )

            return message_id
        except PyMongoError as e:
            logger.error(f"保存消息失败: {str(e)}")
            metrics.increment_counter("session_repo_errors", {"method": "save_message"})
            return None

    @metrics.measure_execution_time("session_repo_get_messages")
    async def get_messages(
        self, session_id: str, limit: int = 50, before_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        获取会话消息

        Args:
            session_id: 会话ID
            limit: 返回消息数量限制
            before_id: 在此消息ID之前的消息

        Returns:
            List[Dict[str, Any]]: 消息列表
        """
        try:
            query = {"session_id": session_id}

            # 如果指定了before_id，获取消息创建时间
            if before_id:
                before_message = await self.messages.find_one({"message_id": before_id})
                if before_message:
                    query["created_at"] = {"$lt": before_message["created_at"]}

            # 查询消息
            cursor = self.messages.find(query).sort("created_at", -1).limit(limit)

            messages = await cursor.to_list(length=limit)

            # 处理ObjectId
            for message in messages:
                if "_id" in message:
                    message["id"] = str(message.pop("_id"))

            # 返回按时间正序排列的消息
            return list(reversed(messages))
        except PyMongoError as e:
            logger.error(f"获取会话消息失败: {str(e)}")
            metrics.increment_counter("session_repo_errors", {"method": "get_messages"})
            return []

    @metrics.measure_execution_time("session_repo_get_latest_messages")
    async def get_latest_messages(
        self, session_id: str, count: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取最新的消息

        Args:
            session_id: 会话ID
            count: 消息数量

        Returns:
            List[Dict[str, Any]]: 最新消息列表
        """
        try:
            cursor = (
                self.messages.find({"session_id": session_id})
                .sort("created_at", -1)
                .limit(count)
            )

            messages = await cursor.to_list(length=count)

            # 处理ObjectId
            for message in messages:
                if "_id" in message:
                    message["id"] = str(message.pop("_id"))

            # 返回按时间正序排列的消息
            return list(reversed(messages))
        except PyMongoError as e:
            logger.error(f"获取最新消息失败: {str(e)}")
            metrics.increment_counter(
                "session_repo_errors", {"method": "get_latest_messages"}
            )
            return []

    @metrics.measure_execution_time("session_repo_get_diagnosis_messages")
    async def get_diagnosis_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """
        获取诊断相关的消息

        Args:
            session_id: 会话ID

        Returns:
            List[Dict[str, Any]]: 诊断相关消息列表
        """
        try:
            query = {"session_id": session_id, "metadata.diagnosis_related": True}

            cursor = self.messages.find(query).sort("created_at", 1)
            messages = await cursor.to_list(length=100)  # 设置一个较大的上限

            # 处理ObjectId
            for message in messages:
                if "_id" in message:
                    message["id"] = str(message.pop("_id"))

            return messages
        except PyMongoError as e:
            logger.error(f"获取诊断消息失败: {str(e)}")
            metrics.increment_counter(
                "session_repo_errors", {"method": "get_diagnosis_messages"}
            )
            return []

    @metrics.measure_execution_time("session_repo_get_session_summary")
    async def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取会话摘要信息

        Args:
            session_id: 会话ID

        Returns:
            Optional[Dict[str, Any]]: 会话摘要
        """
        try:
            # 获取会话
            session = await self.find_by_id(session_id)
            if not session:
                return None

            # 获取最新消息
            latest_messages = await self.get_latest_messages(session_id, 1)

            # 获取诊断状态
            diagnosis_state = session.get("diagnosis_state", {})

            # 构建摘要
            summary = {
                "session_id": session["session_id"],
                "user_id": session["user_id"],
                "status": session["status"],
                "created_at": session["created_at"],
                "updated_at": session["updated_at"],
                "message_count": session["message_count"],
                "diagnosis_state": diagnosis_state,
                "last_message": latest_messages[0]["content"]
                if latest_messages
                else None,
                "last_message_time": latest_messages[0]["created_at"]
                if latest_messages
                else None,
                "tags": session.get("tags", []),
            }

            return summary
        except PyMongoError as e:
            logger.error(f"获取会话摘要失败: {str(e)}")
            metrics.increment_counter(
                "session_repo_errors", {"method": "get_session_summary"}
            )
            return None

    @metrics.measure_execution_time("session_repo_create_memory_anchor")
    async def _create_memory_anchor(
        self, user_id: str, content: str, topic: str, context: Dict[str, Any]
    ) -> Optional[str]:
        """
        创建记忆锚点（重要的长期记忆）

        Args:
            user_id: 用户ID
            content: 记忆内容
            topic: 记忆主题
            context: 记忆上下文

        Returns:
            Optional[str]: 记忆锚点ID
        """
        try:
            anchor_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc).isoformat()

            anchor_data = {
                "anchor_id": anchor_id,
                "user_id": user_id,
                "content": content,
                "topic": topic,
                "context": context,
                "created_at": now,
                "last_accessed": now,
                "access_count": 0,
                "importance": context.get("importance", 5),  # 1-10的重要性评分
            }

            await self.memory_anchors.insert_one(anchor_data)
            logger.debug(
                f"创建记忆锚点: anchor_id={anchor_id}, user_id={user_id}, topic={topic}"
            )
            return anchor_id
        except PyMongoError as e:
            logger.error(f"创建记忆锚点失败: {str(e)}")
            metrics.increment_counter(
                "session_repo_errors", {"method": "create_memory_anchor"}
            )
            return None

    @metrics.measure_execution_time("session_repo_update_dialogue_record")
    async def _update_dialogue_record(
        self,
        user_id: str,
        session_id: str,
        message_id: str,
        role: str,
        content: str,
        diagnosis_step: str,
        symptoms: List[str],
        diagnosis_data: Dict[str, Any],
    ) -> Optional[str]:
        """
        更新对话记录集合，用于追踪诊断过程

        Args:
            user_id: 用户ID
            session_id: 会话ID
            message_id: 消息ID
            role: 消息角色
            content: 消息内容
            diagnosis_step: 诊断步骤
            symptoms: 症状列表
            diagnosis_data: 诊断数据

        Returns:
            Optional[str]: 记录ID
        """
        try:
            record_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc).isoformat()

            # 查找是否存在现有记录
            existing_record = await self.dialogue_records.find_one(
                {"user_id": user_id, "session_id": session_id}
            )

            # 构建新的记录或更新现有记录
            if existing_record:
                # 更新现有记录
                record_id = existing_record["record_id"]

                # 添加新的对话
                dialogue_entry = {
                    "message_id": message_id,
                    "role": role,
                    "content": content,
                    "timestamp": now,
                    "diagnosis_step": diagnosis_step,
                    "symptoms": symptoms,
                }

                # 更新诊断数据
                merged_diagnosis_data = existing_record.get("diagnosis_data", {})
                if diagnosis_data:
                    for key, value in diagnosis_data.items():
                        merged_diagnosis_data[key] = value

                # 执行更新
                await self.dialogue_records.update_one(
                    {"record_id": record_id},
                    {
                        "$push": {"dialogue": dialogue_entry},
                        "$set": {
                            "updated_at": now,
                            "current_step": diagnosis_step,
                            "diagnosis_data": merged_diagnosis_data,
                        },
                    },
                )
            else:
                # 创建新记录
                record_data = {
                    "record_id": record_id,
                    "user_id": user_id,
                    "session_id": session_id,
                    "created_at": now,
                    "updated_at": now,
                    "current_step": diagnosis_step,
                    "diagnosis_data": diagnosis_data,
                    "dialogue": [
                        {
                            "message_id": message_id,
                            "role": role,
                            "content": content,
                            "timestamp": now,
                            "diagnosis_step": diagnosis_step,
                            "symptoms": symptoms,
                        }
                    ],
                }

                await self.dialogue_records.insert_one(record_data)

            logger.debug(
                f"更新对话记录: record_id={record_id}, user_id={user_id}, step={diagnosis_step}"
            )
            return record_id
        except PyMongoError as e:
            logger.error(f"更新对话记录失败: {str(e)}")
            metrics.increment_counter(
                "session_repo_errors", {"method": "update_dialogue_record"}
            )
            return None

    @metrics.measure_execution_time("session_repo_get_memory_anchors")
    async def get_memory_anchors(
        self, user_id: str, topic: Optional[str] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取用户的记忆锚点

        Args:
            user_id: 用户ID
            topic: 记忆主题（可选）
            limit: 返回记录数量限制

        Returns:
            List[Dict[str, Any]]: 记忆锚点列表
        """
        try:
            query = {"user_id": user_id}
            if topic:
                query["topic"] = topic

            cursor = self.memory_anchors.find(query).sort("importance", -1).limit(limit)

            anchors = await cursor.to_list(length=limit)

            # 处理ObjectId
            for anchor in anchors:
                if "_id" in anchor:
                    anchor["id"] = str(anchor.pop("_id"))

                # 更新访问统计
                await self.memory_anchors.update_one(
                    {"anchor_id": anchor["anchor_id"]},
                    {
                        "$inc": {"access_count": 1},
                        "$set": {
                            "last_accessed": datetime.now(timezone.utc).isoformat()
                        },
                    },
                )

            return anchors
        except PyMongoError as e:
            logger.error(f"获取记忆锚点失败: {str(e)}")
            metrics.increment_counter(
                "session_repo_errors", {"method": "get_memory_anchors"}
            )
            return []

    @metrics.measure_execution_time("session_repo_get_dialogue_record")
    async def get_dialogue_record(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取会话的对话记录

        Args:
            session_id: 会话ID

        Returns:
            Optional[Dict[str, Any]]: 对话记录
        """
        try:
            record = await self.dialogue_records.find_one({"session_id": session_id})

            if record:
                # 处理ObjectId
                if "_id" in record:
                    record["id"] = str(record.pop("_id"))

                return record

            return None
        except PyMongoError as e:
            logger.error(f"获取对话记录失败: {str(e)}")
            metrics.increment_counter(
                "session_repo_errors", {"method": "get_dialogue_record"}
            )
            return None

    @metrics.measure_execution_time("session_repo_get_user_dialogue_records")
    async def get_user_dialogue_records(
        self, user_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取用户的所有对话记录

        Args:
            user_id: 用户ID
            limit: 返回记录数量限制

        Returns:
            List[Dict[str, Any]]: 对话记录列表
        """
        try:
            cursor = (
                self.dialogue_records.find({"user_id": user_id})
                .sort("updated_at", -1)
                .limit(limit)
            )

            records = await cursor.to_list(length=limit)

            # 处理ObjectId
            for record in records:
                if "_id" in record:
                    record["id"] = str(record.pop("_id"))

            return records
        except PyMongoError as e:
            logger.error(f"获取用户对话记录失败: {str(e)}")
            metrics.increment_counter(
                "session_repo_errors", {"method": "get_user_dialogue_records"}
            )
            return []

    @metrics.measure_execution_time("session_repo_delete_expired_sessions")
    async def delete_expired_sessions(self, days: int = 90) -> int:
        """
        删除过期的会话

        Args:
            days: 过期天数

        Returns:
            int: 删除的会话数量
        """
        try:
            expire_date = (
                datetime.now(timezone.utc) - timedelta(days=days)
            ).isoformat()

            # 删除过期会话关联的消息
            expired_sessions = self.sessions.find({"updated_at": {"$lt": expire_date}})
            session_ids = [session["session_id"] async for session in expired_sessions]

            if session_ids:
                await self.messages.delete_many({"session_id": {"$in": session_ids}})
                await self.dialogue_records.delete_many(
                    {"session_id": {"$in": session_ids}}
                )

            # 删除过期会话
            result = await self.sessions.delete_many(
                {"updated_at": {"$lt": expire_date}}
            )
            deleted_count = result.deleted_count

            logger.info(f"删除过期会话: {deleted_count}个")
            return deleted_count
        except PyMongoError as e:
            logger.error(f"删除过期会话失败: {str(e)}")
            metrics.increment_counter(
                "session_repo_errors", {"method": "delete_expired_sessions"}
            )
            return 0
