#!/usr/bin/env python

"""
产品存储库
负责农产品、食品和健康产品数据的存储和检索
"""

import logging
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from pkg.utils.config_loader import get_config

logger = logging.getLogger(__name__)

class ProductRepository:
    """产品存储库"""

    def __init__(self):
        """初始化产品存储库"""
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

        # 产品集合
        self.products_collection = self.mongo_db["products"]

        # 产品溯源集合
        self.trace_collection = self.mongo_db["product_traces"]

        # 产品评价集合
        self.reviews_collection = self.mongo_db["product_reviews"]

        logger.info("产品存储库初始化完成")

    async def get_product_by_id(self, product_id: str) -> dict[str, Any] | None:
        """
        根据ID获取产品

        Args:
            product_id: 产品ID

        Returns:
            Optional[Dict[str, Any]]: 产品信息
        """
        try:
            # 查询条件
            query = {"_id": product_id}

            # 执行查询
            product = await self.products_collection.find_one(query)

            # 处理结果
            if product:
                product["id"] = str(product.pop("_id"))
                return product

            return None

        except Exception as e:
            logger.error(f"查询产品失败: {e!s}", exc_info=True)
            return None

    async def create_product(self, product_data: dict[str, Any]) -> str:
        """
        创建产品

        Args:
            product_data: 产品数据

        Returns:
            str: 产品ID
        """
        try:
            # 生成产品ID（如果没有提供）
            if "id" not in product_data:
                product_data["_id"] = str(uuid.uuid4())
            else:
                product_data["_id"] = product_data.pop("id")

            # 添加创建时间和更新时间
            current_time = datetime.now().isoformat()
            product_data["created_at"] = current_time
            product_data["updated_at"] = current_time

            # 插入数据
            result = await self.products_collection.insert_one(product_data)

            # 返回产品ID
            return str(result.inserted_id)

        except Exception as e:
            logger.error(f"创建产品失败: {e!s}", exc_info=True)
            raise

    async def update_product(
        self, product_id: str, product_data: dict[str, Any]
    ) -> bool:
        """
        更新产品

        Args:
            product_id: 产品ID
            product_data: 更新的产品数据

        Returns:
            bool: 更新是否成功
        """
        try:
            # 更新时间
            product_data["updated_at"] = datetime.now().isoformat()

            # 执行更新
            result = await self.products_collection.update_one(
                {"_id": product_id}, {"$set": product_data}
            )

            # 判断是否成功
            return result.modified_count > 0

        except Exception as e:
            logger.error(f"更新产品失败: {e!s}", exc_info=True)
            return False

    async def delete_product(self, product_id: str) -> bool:
        """
        删除产品

        Args:
            product_id: 产品ID

        Returns:
            bool: 删除是否成功
        """
        try:
            # 执行删除
            result = await self.products_collection.delete_one({"_id": product_id})

            # 判断是否成功
            return result.deleted_count > 0

        except Exception as e:
            logger.error(f"删除产品失败: {e!s}", exc_info=True)
            return False

    async def get_products_by_category(
        self, category: str, page: int = 1, page_size: int = 20
    ) -> dict[str, Any]:
        """
        根据分类获取产品列表

        Args:
            category: 产品分类
            page: 页码
            page_size: 每页大小

        Returns:
            Dict[str, Any]: 产品列表和分页信息
        """
        try:
            # 查询条件
            query = {"categories": category}

            # 计算跳过的文档数
            skip = (page - 1) * page_size

            # 执行查询
            cursor = (
                self.products_collection.find(query)
                .sort("created_at", -1)
                .skip(skip)
                .limit(page_size)
            )

            # 获取结果
            products = await cursor.to_list(length=page_size)

            # 查询总数
            total_count = await self.products_collection.count_documents(query)

            # 计算总页数
            total_pages = (total_count + page_size - 1) // page_size

            # 处理结果
            for product in products:
                product["id"] = str(product.pop("_id"))

            # 构建响应
            return {
                "products": products,
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages,
            }

        except Exception as e:
            logger.error(f"查询分类产品失败: {e!s}", exc_info=True)
            return {
                "products": [],
                "page": page,
                "page_size": page_size,
                "total_count": 0,
                "total_pages": 0,
            }

    async def get_seasonal_products(
        self, season: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        获取季节性产品

        Args:
            season: 季节
            limit: 最大结果数

        Returns:
            List[Dict[str, Any]]: 季节性产品列表
        """
        try:
            # 查询条件
            query = {"$or": [{"seasons": season}, {"seasons": "ALL"}]}

            # 执行查询
            cursor = (
                self.products_collection.find(query).sort("rating", -1).limit(limit)
            )

            # 获取结果
            products = await cursor.to_list(length=limit)

            # 处理结果
            for product in products:
                product["id"] = str(product.pop("_id"))

                # 添加季节匹配度作为排序分数
                if season in product.get("seasons", []):
                    product["score"] = 0.9
                else:
                    product["score"] = 0.6

            return products

        except Exception as e:
            logger.error(f"查询季节性产品失败: {e!s}", exc_info=True)
            return []

    async def get_trace_records(
        self, product_id: str, batch_id: str
    ) -> list[dict[str, Any]]:
        """
        获取产品溯源记录

        Args:
            product_id: 产品ID
            batch_id: 批次ID

        Returns:
            List[Dict[str, Any]]: 溯源记录列表
        """
        try:
            # 查询条件
            query = {"product_id": product_id, "batch_id": batch_id}

            # 执行查询
            cursor = self.trace_collection.find(query).sort("timestamp", 1)

            # 获取结果
            trace_records = await cursor.to_list(length=100)

            # 处理结果
            for record in trace_records:
                record["id"] = str(record.pop("_id"))

            return trace_records

        except Exception as e:
            logger.error(f"查询溯源记录失败: {e!s}", exc_info=True)
            return []

    async def add_trace_record(self, trace_data: dict[str, Any]) -> str:
        """
        添加溯源记录

        Args:
            trace_data: 溯源记录数据

        Returns:
            str: 记录ID
        """
        try:
            # 生成记录ID（如果没有提供）
            if "id" not in trace_data:
                trace_data["_id"] = str(uuid.uuid4())
            else:
                trace_data["_id"] = trace_data.pop("id")

            # 添加创建时间
            trace_data["created_at"] = datetime.now().isoformat()

            # 插入数据
            result = await self.trace_collection.insert_one(trace_data)

            # 返回记录ID
            return str(result.inserted_id)

        except Exception as e:
            logger.error(f"添加溯源记录失败: {e!s}", exc_info=True)
            raise

    async def search_products(
        self, query_text: str, page: int = 1, page_size: int = 20
    ) -> dict[str, Any]:
        """
        搜索产品

        Args:
            query_text: 搜索文本
            page: 页码
            page_size: 每页大小

        Returns:
            Dict[str, Any]: 搜索结果，包含产品列表和分页信息
        """
        try:
            # 构建查询条件（模糊搜索名称和描述）
            query = {
                "$or": [
                    {"name": {"$regex": query_text, "$options": "i"}},
                    {"description": {"$regex": query_text, "$options": "i"}},
                    {"tags": {"$regex": query_text, "$options": "i"}},
                ]
            }

            # 计算跳过的文档数
            skip = (page - 1) * page_size

            # 执行查询
            cursor = self.products_collection.find(query).skip(skip).limit(page_size)

            # 获取结果
            products = await cursor.to_list(length=page_size)

            # 查询总数
            total_count = await self.products_collection.count_documents(query)

            # 计算总页数
            total_pages = (total_count + page_size - 1) // page_size

            # 处理结果
            for product in products:
                product["id"] = str(product.pop("_id"))

            # 构建响应
            return {
                "products": products,
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages,
            }

        except Exception as e:
            logger.error(f"搜索产品失败: {e!s}", exc_info=True)
            return {
                "products": [],
                "page": page,
                "page_size": page_size,
                "total_count": 0,
                "total_pages": 0,
            }

    async def get_recommendation_candidates(
        self, constitution_type: str, season: str, limit: int = 30
    ) -> list[dict[str, Any]]:
        """
        获取推荐候选产品

        Args:
            constitution_type: 体质类型
            season: 季节
            limit: 最大结果数

        Returns:
            List[Dict[str, Any]]: 候选产品列表
        """
        try:
            # 构建查询条件
            query = {
                "$or": [
                    {f"constitution_benefits.{constitution_type}": {"$exists": True}},
                    {"seasons": season},
                    {"seasons": "ALL"},
                ]
            }

            # 执行查询
            cursor = self.products_collection.find(query).limit(limit)

            # 获取结果
            products = await cursor.to_list(length=limit)

            # 处理结果
            for product in products:
                product["id"] = str(product.pop("_id"))

            return products

        except Exception as e:
            logger.error(f"获取推荐产品候选失败: {e!s}", exc_info=True)
            return []
