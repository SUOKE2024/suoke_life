"""
resource_repository - 索克生活项目模块
"""

from datetime import datetime
from pkg.utils.config_loader import get_config
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import Any
import logging
import uuid

#!/usr/bin/env python

"""
资源存储库
负责医疗资源数据的存储和检索
"""




logger = logging.getLogger(__name__)

class ResourceRepository:
    """医疗资源存储库"""

    def __init__(self):
        """初始化资源存储库"""
        self.config = get_config()
        self.db_config = self.config.get_section("database")

        # 初始化PostgreSQL连接
        postgres_config = self.db_config.get("postgres", {})
        postgres_url = f"postgresql+asyncpg://{postgres_config.get('user')}:{postgres_config.get('password')}@{postgres_config.get('host')}:{postgres_config.get('port')}/{postgres_config.get('database')}"

        self.engine = create_async_engine(postgres_url)
        self.async_session = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

        # 初始化MongoDB连接
        mongodb_config = self.db_config.get("mongodb", {})
        mongodb_uri = mongodb_config.get("uri")
        mongodb_db = mongodb_config.get("database")

        self.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(mongodb_uri)
        self.mongo_db = self.mongo_client[mongodb_db]
        self.resources_collection = self.mongo_db["medical_resources"]

        logger.info("资源存储库初始化完成")

    async def get_resources_by_type(self, resource_type: str) -> list[dict[str, Any]]:
        """
        根据资源类型获取医疗资源列表

        Args:
            resource_type: 资源类型

        Returns:
            List[Dict[str, Any]]: 资源列表
        """
        try:
            # 查询条件
            query = {"resource_type": resource_type}

            # 执行查询
            cursor = self.resources_collection.find(query)

            # 获取结果
            resources = await cursor.to_list(length=100)

            # 处理结果
            for resource in resources:
                # MongoDB的_id不可序列化，转换为字符串
                resource["id"] = str(resource.pop("_id"))

            logger.debug(f"查询到 {len(resources)} 个 {resource_type} 类型的资源")
            return resources

        except Exception as e:
            logger.error(f"查询资源失败: {e!s}", exc_info=True)
            return []

    async def get_resource_by_id(self, resource_id: str) -> dict[str, Any] | None:
        """
        根据ID获取医疗资源

        Args:
            resource_id: 资源ID

        Returns:
            Optional[Dict[str, Any]]: 资源信息
        """
        try:
            # 查询条件
            query = {"_id": resource_id}

            # 执行查询
            resource = await self.resources_collection.find_one(query)

            # 处理结果
            if resource:
                resource["id"] = str(resource.pop("_id"))
                return resource

            return None

        except Exception as e:
            logger.error(f"查询资源失败: {e!s}", exc_info=True)
            return None

    async def create_resource(self, resource_data: dict[str, Any]) -> str:
        """
        创建医疗资源

        Args:
            resource_data: 资源数据

        Returns:
            str: 资源ID
        """
        try:
            # 生成资源ID（如果没有提供）
            if "id" not in resource_data:
                resource_data["_id"] = str(uuid.uuid4())
            else:
                resource_data["_id"] = resource_data.pop("id")

            # 添加创建时间和更新时间
            current_time = datetime.now().isoformat()
            resource_data["created_at"] = current_time
            resource_data["updated_at"] = current_time

            # 插入数据
            result = await self.resources_collection.insert_one(resource_data)

            # 返回资源ID
            return str(result.inserted_id)

        except Exception as e:
            logger.error(f"创建资源失败: {e!s}", exc_info=True)
            raise

    async def update_resource(
        self, resource_id: str, resource_data: dict[str, Any]
    ) -> bool:
        """
        更新医疗资源

        Args:
            resource_id: 资源ID
            resource_data: 更新的资源数据

        Returns:
            bool: 更新是否成功
        """
        try:
            # 更新时间
            resource_data["updated_at"] = datetime.now().isoformat()

            # 执行更新
            result = await self.resources_collection.update_one(
                {"_id": resource_id}, {"$set": resource_data}
            )

            # 判断是否成功
            return result.modified_count > 0

        except Exception as e:
            logger.error(f"更新资源失败: {e!s}", exc_info=True)
            return False

    async def delete_resource(self, resource_id: str) -> bool:
        """
        删除医疗资源

        Args:
            resource_id: 资源ID

        Returns:
            bool: 删除是否成功
        """
        try:
            # 执行删除
            result = await self.resources_collection.delete_one({"_id": resource_id})

            # 判断是否成功
            return result.deleted_count > 0

        except Exception as e:
            logger.error(f"删除资源失败: {e!s}", exc_info=True)
            return False

    async def search_resources(
        self, query: dict[str, Any], page: int = 1, page_size: int = 20
    ) -> dict[str, Any]:
        """
        搜索医疗资源

        Args:
            query: 查询条件
            page: 页码
            page_size: 每页大小

        Returns:
            Dict[str, Any]: 搜索结果，包含资源列表和分页信息
        """
        try:
            # 计算跳过的文档数
            skip = (page - 1) * page_size

            # 执行查询
            cursor = self.resources_collection.find(query).skip(skip).limit(page_size)

            # 获取结果
            resources = await cursor.to_list(length=page_size)

            # 查询总数
            total_count = await self.resources_collection.count_documents(query)

            # 计算总页数
            total_pages = (total_count + page_size - 1) // page_size

            # 处理结果
            for resource in resources:
                resource["id"] = str(resource.pop("_id"))

            # 构建响应
            return {
                "resources": resources,
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages,
            }

        except Exception as e:
            logger.error(f"搜索资源失败: {e!s}", exc_info=True)
            return {
                "resources": [],
                "page": page,
                "page_size": page_size,
                "total_count": 0,
                "total_pages": 0,
            }

    async def get_available_resources_by_time(
        self, resource_type: str, time_slot: str
    ) -> list[dict[str, Any]]:
        """
        获取指定时间段可用的医疗资源

        Args:
            resource_type: 资源类型
            time_slot: 时间段

        Returns:
            List[Dict[str, Any]]: 可用资源列表
        """
        try:
            # 查询条件
            query = {
                "resource_type": resource_type,
                "available_times": {"$elemMatch": {"$regex": f"^{time_slot}"}},
            }

            # 执行查询
            cursor = self.resources_collection.find(query)

            # 获取结果
            resources = await cursor.to_list(length=100)

            # 处理结果
            for resource in resources:
                resource["id"] = str(resource.pop("_id"))

            return resources

        except Exception as e:
            logger.error(f"查询可用资源失败: {e!s}", exc_info=True)
            return []
