"""
session_repository - 索克生活项目模块
"""

    import motor.motor_asyncio
from typing import Any
import asyncio
import logging
import pymongo
import time

#!/usr/bin/env python

"""
会话存储库模块，负责会话数据的存储和查询
"""


try:
except ImportError:
    motor = None

logger = logging.getLogger(__name__)

class SessionRepository:
    """会话存储库类，负责会话数据的存储和查询"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化会话存储库

        Args:
            config: 配置信息
        """
        self.config = config
        self.db_config = config.get("database", {})

        # 数据库连接配置
        self.db_type = self.db_config.get("type", "mongodb")
        self.db_host = self.db_config.get("host", "localhost")
        self.db_port = self.db_config.get("port", 27017)
        self.db_name = self.db_config.get("name", "inquiry_db")
        self.db_user = self.db_config.get("user", "")
        self.db_password = self.db_config.get("password", "")
        self.auth_source = self.db_config.get("auth_source", "admin")

        # 数据库客户端
        self.client = None
        self.db = None
        self.sessions_collection = None

        # 初始化数据库连接
        self._init_db_connection()

        logger.info("会话存储库初始化完成")

    def _init_db_connection(self):
        """初始化数据库连接"""
        try:
            # 检查是否使用内存模式或motor不可用
            if self.db_type == "memory" or motor is None:
                if motor is None:
                    logger.warning("motor库未安装，自动切换到内存模式")
                else:
                    logger.info("使用内存数据库模式")
                self.sessions = {}
                self.db_type = "memory"  # 确保后续逻辑使用内存模式
                return

            # 创建MongoDB连接
            connection_str = "mongodb://"

            # 添加用户名密码
            if self.db_user and self.db_password:
                connection_str += f"{self.db_user}:{self.db_password}@"

            connection_str += f"{self.db_host}:{self.db_port}/{self.db_name}"

            # 添加认证源
            if self.db_user and self.db_password:
                connection_str += f"?authSource={self.auth_source}"

            # 创建异步客户端
            self.client = motor.motor_asyncio.AsyncIOMotorClient(connection_str)
            self.db = self.client[self.db_name]
            self.sessions_collection = self.db.sessions

            # 创建索引
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self._create_indexes())

            logger.info(
                f"已连接到MongoDB: {self.db_host}:{self.db_port}/{self.db_name}"
            )

        except Exception as e:
            logger.error(f"连接数据库失败: {e!s}")
            raise

    async def _create_indexes(self):
        """创建数据库索引"""
        if self.db_type == "memory":
            return

        try:
            # 创建会话ID索引
            await self.sessions_collection.create_index("id", unique=True)

            # 创建用户ID索引
            await self.sessions_collection.create_index("user_id")

            # 创建创建时间索引
            await self.sessions_collection.create_index("created_at")

            # 创建状态索引
            await self.sessions_collection.create_index("status")

            logger.info("已创建数据库索引")

        except Exception as e:
            logger.error(f"创建索引失败: {e!s}")
            raise

    async def create_session(self, session_data: dict) -> bool:
        """
        创建新会话

        Args:
            session_data: 会话数据

        Returns:
            bool: 创建是否成功
        """
        try:
            # 确保必要字段存在
            if "id" not in session_data:
                logger.error("创建会话失败: 缺少ID字段")
                return False

            # 使用内存模式
            if self.db_type == "memory":
                session_id = session_data["id"]
                if session_id in self.sessions:
                    logger.error(f"创建会话失败: 会话ID已存在: {session_id}")
                    return False
                self.sessions[session_id] = session_data
                logger.info(f"已创建会话: {session_id} (内存模式)")
                return True

            # 插入数据
            await self.sessions_collection.insert_one(session_data)
            logger.info(f"已创建会话: {session_data['id']}")
            return True

        except pymongo.errors.DuplicateKeyError:
            logger.error(f"创建会话失败: 会话ID已存在: {session_data.get('id')}")
            return False
        except Exception as e:
            logger.error(f"创建会话失败: {e!s}")
            return False

    async def get_session_by_id(self, session_id: str) -> dict | None:
        """
        根据ID获取会话

        Args:
            session_id: 会话ID

        Returns:
            Optional[Dict]: 会话数据，不存在则返回None
        """
        try:
            # 使用内存模式
            if self.db_type == "memory":
                return self.sessions.get(session_id)

            session = await self.sessions_collection.find_one({"id": session_id})
            return session

        except Exception as e:
            logger.error(f"获取会话失败: {e!s}")
            return None

    async def update_session(self, session_id: str, session_data: dict) -> bool:
        """
        更新会话数据

        Args:
            session_id: 会话ID
            session_data: 更新后的会话数据

        Returns:
            bool: 更新是否成功
        """
        try:
            # 使用内存模式
            if self.db_type == "memory":
                if session_id not in self.sessions:
                    logger.warning(f"更新会话失败: 未找到会话 {session_id} (内存模式)")
                    return False
                self.sessions[session_id] = session_data
                logger.info(f"已更新会话: {session_id} (内存模式)")
                return True

            result = await self.sessions_collection.replace_one(
                {"id": session_id}, session_data
            )

            if result.matched_count > 0:
                logger.info(f"已更新会话: {session_id}")
                return True
            else:
                logger.warning(f"更新会话失败: 未找到会话 {session_id}")
                return False

        except Exception as e:
            logger.error(f"更新会话失败: {e!s}")
            return False

    async def update_session_status(self, session_id: str, status: str) -> bool:
        """
        更新会话状态

        Args:
            session_id: 会话ID
            status: 新状态

        Returns:
            bool: 更新是否成功
        """
        try:
            # 使用内存模式
            if self.db_type == "memory":
                if session_id not in self.sessions:
                    logger.warning(
                        f"更新会话状态失败: 未找到会话 {session_id} (内存模式)"
                    )
                    return False
                self.sessions[session_id]["status"] = status
                self.sessions[session_id]["last_modified"] = time.time()
                logger.info(f"已更新会话状态: {session_id} -> {status} (内存模式)")
                return True

            result = await self.sessions_collection.update_one(
                {"id": session_id},
                {"$set": {"status": status, "last_modified": time.time()}},
            )

            if result.matched_count > 0:
                logger.info(f"已更新会话状态: {session_id} -> {status}")
                return True
            else:
                logger.warning(f"更新会话状态失败: 未找到会话 {session_id}")
                return False

        except Exception as e:
            logger.error(f"更新会话状态失败: {e!s}")
            return False

    async def get_sessions_by_user_id(
        self,
        user_id: str,
        limit: int = 10,
        offset: int = 0,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> list[dict]:
        """
        获取用户的会话列表

        Args:
            user_id: 用户ID
            limit: 返回的最大数量
            offset: 偏移量
            sort_by: 排序字段
            sort_order: 排序顺序 ('asc' 或 'desc')

        Returns:
            List[Dict]: 会话列表
        """
        try:
            # 构建排序
            sort_direction = (
                pymongo.DESCENDING
                if sort_order.lower() == "desc"
                else pymongo.ASCENDING
            )

            # 查询
            cursor = (
                self.sessions_collection.find({"user_id": user_id})
                .sort(sort_by, sort_direction)
                .skip(offset)
                .limit(limit)
            )

            # 转换为列表
            sessions = await cursor.to_list(length=limit)

            return sessions

        except Exception as e:
            logger.error(f"获取用户会话列表失败: {e!s}")
            return []

    async def count_sessions_by_user_id(self, user_id: str) -> int:
        """
        计算用户的会话数量

        Args:
            user_id: 用户ID

        Returns:
            int: 会话数量
        """
        try:
            count = await self.sessions_collection.count_documents({"user_id": user_id})
            return count

        except Exception as e:
            logger.error(f"计算用户会话数量失败: {e!s}")
            return 0

    async def get_active_sessions(self, limit: int = 100) -> list[dict]:
        """
        获取活跃会话列表

        Args:
            limit: 返回的最大数量

        Returns:
            List[Dict]: 活跃会话列表
        """
        try:
            # 计算活跃时间阈值（1小时内有交互）
            active_threshold = time.time() - 3600

            # 查询
            cursor = (
                self.sessions_collection.find(
                    {"status": "active", "last_interaction": {"$gt": active_threshold}}
                )
                .sort("last_interaction", pymongo.DESCENDING)
                .limit(limit)
            )

            # 转换为列表
            sessions = await cursor.to_list(length=limit)

            return sessions

        except Exception as e:
            logger.error(f"获取活跃会话列表失败: {e!s}")
            return []

    async def delete_session(self, session_id: str) -> bool:
        """
        删除会话

        Args:
            session_id: 会话ID

        Returns:
            bool: 删除是否成功
        """
        try:
            result = await self.sessions_collection.delete_one({"id": session_id})

            if result.deleted_count > 0:
                logger.info(f"已删除会话: {session_id}")
                return True
            else:
                logger.warning(f"删除会话失败: 未找到会话 {session_id}")
                return False

        except Exception as e:
            logger.error(f"删除会话失败: {e!s}")
            return False

    async def clean_expired_sessions(self, expiry_days: int = 30) -> int:
        """
        清理过期会话

        Args:
            expiry_days: 过期天数

        Returns:
            int: 清理的会话数量
        """
        try:
            # 计算过期时间
            expiry_time = time.time() - (expiry_days * 24 * 3600)

            # 删除过期会话
            result = await self.sessions_collection.delete_many(
                {
                    "created_at": {"$lt": expiry_time},
                    "status": {"$in": ["expired", "completed"]},
                }
            )

            cleaned_count = result.deleted_count
            logger.info(f"已清理 {cleaned_count} 个过期会话")

            return cleaned_count

        except Exception as e:
            logger.error(f"清理过期会话失败: {e!s}")
            return 0
