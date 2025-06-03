#!/usr/bin/env python

"""
用户存储库模块，负责用户数据的存储和查询
"""

import asyncio
import logging
import time
from typing import Any

import pymongo

logger = logging.getLogger(__name__)

class UserRepository:
    """用户存储库类，负责用户数据的存储和查询"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化用户存储库

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
        self.users_collection = None

        # 初始化数据库连接
        self._init_db_connection()

        logger.info("用户存储库初始化完成")

    def _init_db_connection(self):
        """初始化数据库连接"""
        try:
            # 检查是否使用内存模式
            if self.db_type == "memory":
                logger.info("使用内存数据库模式")
                self.users = {}
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
            self.users_collection = self.db.users

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
            # 创建用户ID索引
            await self.users_collection.create_index("id", unique=True)

            # 创建创建时间索引
            await self.users_collection.create_index("created_at")

            logger.info("已创建数据库索引")

        except Exception as e:
            logger.error(f"创建索引失败: {e!s}")
            raise

    async def create_user(self, user_data: dict) -> bool:
        """
        创建新用户

        Args:
            user_data: 用户数据

        Returns:
            bool: 创建是否成功
        """
        try:
            # 确保必要字段存在
            if "id" not in user_data:
                logger.error("创建用户失败: 缺少ID字段")
                return False

            # 确保创建时间字段存在
            if "created_at" not in user_data:
                user_data["created_at"] = time.time()

            # 使用内存模式
            if self.db_type == "memory":
                user_id = user_data["id"]
                if user_id in self.users:
                    logger.error(f"创建用户失败: 用户ID已存在: {user_id}")
                    return False
                self.users[user_id] = user_data
                logger.info(f"已创建用户: {user_id} (内存模式)")
                return True

            # 插入数据
            await self.users_collection.insert_one(user_data)
            logger.info(f"已创建用户: {user_data['id']}")
            return True

        except pymongo.errors.DuplicateKeyError:
            logger.error(f"创建用户失败: 用户ID已存在: {user_data.get('id')}")
            return False
        except Exception as e:
            logger.error(f"创建用户失败: {e!s}")
            return False

    async def get_user_by_id(self, user_id: str) -> dict | None:
        """
        根据ID获取用户

        Args:
            user_id: 用户ID

        Returns:
            Optional[Dict]: 用户数据，不存在则返回None
        """
        try:
            # 使用内存模式
            if self.db_type == "memory":
                return self.users.get(user_id)

            user = await self.users_collection.find_one({"id": user_id})
            return user

        except Exception as e:
            logger.error(f"获取用户失败: {e!s}")
            return None

    async def update_user(self, user_id: str, user_data: dict) -> bool:
        """
        更新用户数据

        Args:
            user_id: 用户ID
            user_data: 更新后的用户数据

        Returns:
            bool: 更新是否成功
        """
        try:
            # 添加更新时间
            user_data["updated_at"] = time.time()

            # 使用内存模式
            if self.db_type == "memory":
                if user_id not in self.users:
                    logger.warning(f"更新用户失败: 未找到用户 {user_id} (内存模式)")
                    return False
                self.users[user_id] = user_data
                logger.info(f"已更新用户: {user_id} (内存模式)")
                return True

            result = await self.users_collection.replace_one({"id": user_id}, user_data)

            if result.matched_count > 0:
                logger.info(f"已更新用户: {user_id}")
                return True
            else:
                logger.warning(f"更新用户失败: 未找到用户 {user_id}")
                return False

        except Exception as e:
            logger.error(f"更新用户失败: {e!s}")
            return False

    async def update_user_health_profile(
        self, user_id: str, health_profile: dict
    ) -> bool:
        """
        更新用户健康档案

        Args:
            user_id: 用户ID
            health_profile: 健康档案数据

        Returns:
            bool: 更新是否成功
        """
        try:
            result = await self.users_collection.update_one(
                {"id": user_id},
                {"$set": {"health_profile": health_profile, "updated_at": time.time()}},
            )

            if result.matched_count > 0:
                logger.info(f"已更新用户健康档案: {user_id}")
                return True
            else:
                logger.warning(f"更新用户健康档案失败: 未找到用户 {user_id}")
                return False

        except Exception as e:
            logger.error(f"更新用户健康档案失败: {e!s}")
            return False

    async def add_symptoms_to_history(self, user_id: str, symptoms: list[dict]) -> bool:
        """
        添加症状到用户历史记录

        Args:
            user_id: 用户ID
            symptoms: 症状列表

        Returns:
            bool: 添加是否成功
        """
        try:
            # 为每个症状添加时间戳
            for symptom in symptoms:
                if "recorded_at" not in symptom:
                    symptom["recorded_at"] = time.time()

            result = await self.users_collection.update_one(
                {"id": user_id},
                {
                    "$push": {"symptom_history": {"$each": symptoms}},
                    "$set": {"updated_at": time.time()},
                },
            )

            if result.matched_count > 0:
                logger.info(
                    f"已添加症状到用户历史: {user_id}, 症状数量: {len(symptoms)}"
                )
                return True
            else:
                logger.warning(f"添加症状到用户历史失败: 未找到用户 {user_id}")
                return False

        except Exception as e:
            logger.error(f"添加症状到用户历史失败: {e!s}")
            return False

    async def add_tcm_patterns_to_history(
        self, user_id: str, patterns: list[dict]
    ) -> bool:
        """
        添加中医证型到用户历史记录

        Args:
            user_id: 用户ID
            patterns: 证型列表

        Returns:
            bool: 添加是否成功
        """
        try:
            # 为每个证型添加时间戳
            for pattern in patterns:
                if "recorded_at" not in pattern:
                    pattern["recorded_at"] = time.time()

            result = await self.users_collection.update_one(
                {"id": user_id},
                {
                    "$push": {"tcm_pattern_history": {"$each": patterns}},
                    "$set": {"updated_at": time.time()},
                },
            )

            if result.matched_count > 0:
                logger.info(
                    f"已添加证型到用户历史: {user_id}, 证型数量: {len(patterns)}"
                )
                return True
            else:
                logger.warning(f"添加证型到用户历史失败: 未找到用户 {user_id}")
                return False

        except Exception as e:
            logger.error(f"添加证型到用户历史失败: {e!s}")
            return False

    async def get_user_symptom_history(
        self, user_id: str, limit: int = 50
    ) -> list[dict]:
        """
        获取用户症状历史

        Args:
            user_id: 用户ID
            limit: 返回的最大数量

        Returns:
            List[Dict]: 症状历史列表
        """
        try:
            user = await self.users_collection.find_one(
                {"id": user_id}, {"symptom_history": {"$slice": -limit}}
            )

            if user and "symptom_history" in user:
                return user["symptom_history"]
            else:
                return []

        except Exception as e:
            logger.error(f"获取用户症状历史失败: {e!s}")
            return []

    async def get_user_tcm_pattern_history(
        self, user_id: str, limit: int = 20
    ) -> list[dict]:
        """
        获取用户证型历史

        Args:
            user_id: 用户ID
            limit: 返回的最大数量

        Returns:
            List[Dict]: 证型历史列表
        """
        try:
            user = await self.users_collection.find_one(
                {"id": user_id}, {"tcm_pattern_history": {"$slice": -limit}}
            )

            if user and "tcm_pattern_history" in user:
                return user["tcm_pattern_history"]
            else:
                return []

        except Exception as e:
            logger.error(f"获取用户证型历史失败: {e!s}")
            return []

    async def update_user_constitution(
        self, user_id: str, constitution_type: str
    ) -> bool:
        """
        更新用户体质类型

        Args:
            user_id: 用户ID
            constitution_type: 体质类型

        Returns:
            bool: 更新是否成功
        """
        try:
            result = await self.users_collection.update_one(
                {"id": user_id},
                {
                    "$set": {
                        "health_profile.constitution_type": constitution_type,
                        "updated_at": time.time(),
                    }
                },
            )

            if result.matched_count > 0:
                logger.info(f"已更新用户体质类型: {user_id} -> {constitution_type}")
                return True
            else:
                logger.warning(f"更新用户体质类型失败: 未找到用户 {user_id}")
                return False

        except Exception as e:
            logger.error(f"更新用户体质类型失败: {e!s}")
            return False

    async def search_users(self, query: dict, limit: int = 20) -> list[dict]:
        """
        搜索用户

        Args:
            query: 查询条件
            limit: 返回的最大数量

        Returns:
            List[Dict]: 用户列表
        """
        try:
            cursor = self.users_collection.find(query).limit(limit)
            users = await cursor.to_list(length=limit)
            return users

        except Exception as e:
            logger.error(f"搜索用户失败: {e!s}")
            return []

    async def delete_user(self, user_id: str) -> bool:
        """
        删除用户

        Args:
            user_id: 用户ID

        Returns:
            bool: 删除是否成功
        """
        try:
            result = await self.users_collection.delete_one({"id": user_id})

            if result.deleted_count > 0:
                logger.info(f"已删除用户: {user_id}")
                return True
            else:
                logger.warning(f"删除用户失败: 未找到用户 {user_id}")
                return False

        except Exception as e:
            logger.error(f"删除用户失败: {e!s}")
            return False
