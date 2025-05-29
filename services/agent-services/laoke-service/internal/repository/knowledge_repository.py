#!/usr/bin/env python

"""
老克智能体服务 - 知识存储库
提供知识文章和学习路径的存储和检索功能
"""

import logging
from datetime import UTC, datetime
from typing import Any

import motor.motor_asyncio
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError

from pkg.utils.config import Config
from pkg.utils.metrics import get_metrics_collector

logger = logging.getLogger(__name__)
metrics = get_metrics_collector()

class KnowledgeRepository:
    """知识存储库，提供知识文章和学习路径的存储和检索功能"""

    def __init__(self):
        """初始化知识存储库"""
        self.config = Config()
        self.db_config = self.config.get_section("database.mongodb")

        # 连接到MongoDB
        self.client = motor.motor_asyncio.AsyncIOMotorClient(self.db_config.get("uri"))
        self.db = self.client[self.db_config.get("database", "laoke_db")]

        # 集合
        self.articles = self.db.knowledge_articles
        self.learning_paths = self.db.learning_paths
        self.user_progress = self.db.user_learning_progress
        self.categories = self.db.knowledge_categories
        self.view_counts = self.db.article_view_counts

        logger.info("知识存储库已初始化")

    async def init_indexes(self):
        """初始化数据库索引"""
        try:
            # 文章集合索引
            await self.articles.create_index("author_id")
            await self.articles.create_index("category")
            await self.articles.create_index("tags")
            await self.articles.create_index("difficulty")
            await self.articles.create_index("created_at")
            await self.articles.create_index([("title", "text"), ("content", "text")])

            # 学习路径集合索引
            await self.learning_paths.create_index("category")
            await self.learning_paths.create_index("level")
            await self.learning_paths.create_index("created_at")
            await self.learning_paths.create_index([("title", "text"), ("description", "text")])

            # 用户进度集合索引
            await self.user_progress.create_index([("user_id", 1), ("path_id", 1)], unique=True)
            await self.user_progress.create_index("path_id")
            await self.user_progress.create_index("last_activity_at")

            # 浏览计数索引
            await self.view_counts.create_index([("article_id", 1)], unique=True)

            logger.info("知识存储库索引已初始化")
        except PyMongoError as e:
            logger.error(f"初始化知识存储库索引失败: {str(e)}")
            raise

    @metrics.measure_execution_time("knowledge_repo_create_article")
    async def create_article(self, article_data: dict[str, Any]) -> str | None:
        """
        创建知识文章

        Args:
            article_data: 文章数据

        Returns:
            Optional[str]: 创建的文章ID，失败时返回None
        """
        try:
            # 确保数据中没有"_id"字段
            if "_id" in article_data:
                del article_data["_id"]

            # 设置创建时间和初始值
            if "created_at" not in article_data:
                article_data["created_at"] = datetime.now(UTC).isoformat()
            if "rating" not in article_data:
                article_data["rating"] = 0
            if "rating_count" not in article_data:
                article_data["rating_count"] = 0

            # 插入文章
            result = await self.articles.insert_one(article_data)

            # 初始化浏览计数
            article_id = str(result.inserted_id)
            await self.view_counts.insert_one({
                "article_id": article_id,
                "count": 0,
                "last_updated": datetime.now(UTC).isoformat()
            })

            # 更新分类
            if "category" in article_data and article_data["category"]:
                await self._ensure_category_exists(article_data["category"])

            return article_id
        except PyMongoError as e:
            logger.error(f"创建知识文章失败: {str(e)}")
            metrics.increment_counter("knowledge_repo_errors", {"method": "create_article"})
            return None

    @metrics.measure_execution_time("knowledge_repo_find_article_by_id")
    async def find_article_by_id(self, article_id: str) -> dict[str, Any] | None:
        """
        根据ID查找知识文章

        Args:
            article_id: 文章ID

        Returns:
            Optional[Dict[str, Any]]: 文章详情，未找到时返回None
        """
        try:
            # 尝试转换为ObjectId
            article_id_obj = ObjectId(article_id)
            article = await self.articles.find_one({"_id": article_id_obj})
        except (ValueError, TypeError):
            # 如果不是有效的ObjectId，尝试使用字符串ID
            article = await self.articles.find_one({"id": article_id})

        if article:
            # 处理ObjectId
            article["id"] = str(article.pop("_id"))

            # 获取浏览量
            try:
                view_count_doc = await self.view_counts.find_one({"article_id": article["id"]})
                article["view_count"] = view_count_doc["count"] if view_count_doc else 0
            except (KeyError, TypeError):
                article["view_count"] = 0

            return article

        return None

    @metrics.measure_execution_time("knowledge_repo_find_articles")
    async def find_articles(self,
                          category: str | None = None,
                          tags: list[str] | None = None,
                          difficulty: str | None = None,
                          limit: int = 10,
                          offset: int = 0,
                          sort_by: str = "created_at",
                          sort_order: str = "desc") -> list[dict[str, Any]]:
        """
        查找知识文章列表

        Args:
            category: 过滤的分类名称
            tags: 过滤的标签列表
            difficulty: 难度级别
            limit: 返回记录数量限制
            offset: 分页偏移量
            sort_by: 排序字段
            sort_order: 排序顺序 (asc 或 desc)

        Returns:
            List[Dict[str, Any]]: 文章列表
        """
        try:
            # 构建查询条件
            query = {}
            if category:
                query["category"] = category
            if tags:
                query["tags"] = {"$in": tags}
            if difficulty:
                query["difficulty"] = difficulty

            # 排序方向
            sort_direction = 1 if sort_order.lower() == "asc" else -1

            # 执行查询
            cursor = self.articles.find(query) \
                .sort(sort_by, sort_direction) \
                .skip(offset) \
                .limit(limit)

            articles = await cursor.to_list(length=limit)

            # 处理ObjectId
            for article in articles:
                article["id"] = str(article.pop("_id"))

            # 获取浏览次数
            article_ids = [article["id"] for article in articles]
            view_counts = {}

            if article_ids:
                view_cursor = self.view_counts.find({"article_id": {"$in": article_ids}})
                view_docs = await view_cursor.to_list(length=None)
                view_counts = {doc["article_id"]: doc["count"] for doc in view_docs}

            # 添加浏览次数
            for article in articles:
                article["view_count"] = view_counts.get(article["id"], 0)

            return articles
        except PyMongoError as e:
            logger.error(f"查找知识文章列表失败: {str(e)}")
            metrics.increment_counter("knowledge_repo_errors", {"method": "find_articles"})
            return []

    @metrics.measure_execution_time("knowledge_repo_search_articles")
    async def search_articles(self, query: str, limit: int = 10, offset: int = 0) -> list[dict[str, Any]]:
        """
        搜索知识文章

        Args:
            query: 搜索关键词
            limit: 返回记录数量限制
            offset: 分页偏移量

        Returns:
            List[Dict[str, Any]]: 搜索结果
        """
        try:
            # 执行全文搜索
            cursor = self.articles.find(
                {"$text": {"$search": query}},
                {"score": {"$meta": "textScore"}}
            ) \
                .sort([("score", {"$meta": "textScore"}), ("created_at", -1)]) \
                .skip(offset) \
                .limit(limit)

            articles = await cursor.to_list(length=limit)

            # 处理ObjectId
            for article in articles:
                article["id"] = str(article.pop("_id"))

            # 获取浏览次数
            article_ids = [article["id"] for article in articles]
            view_counts = {}

            if article_ids:
                view_cursor = self.view_counts.find({"article_id": {"$in": article_ids}})
                view_docs = await view_cursor.to_list(length=None)
                view_counts = {doc["article_id"]: doc["count"] for doc in view_docs}

            # 添加浏览次数
            for article in articles:
                article["view_count"] = view_counts.get(article["id"], 0)

            return articles
        except PyMongoError as e:
            logger.error(f"搜索知识文章失败: {str(e)}")
            metrics.increment_counter("knowledge_repo_errors", {"method": "search_articles"})
            return []

    @metrics.measure_execution_time("knowledge_repo_find_related_articles")
    async def find_related_articles(self,
                                article_id: str,
                                tags: list[str],
                                category: str,
                                limit: int = 5) -> list[dict[str, Any]]:
        """
        查找相关文章

        Args:
            article_id: 当前文章ID
            tags: 当前文章标签
            category: 当前文章分类
            limit: 返回记录数量限制

        Returns:
            List[Dict[str, Any]]: 相关文章列表
        """
        try:
            # 构建查询条件 - 排除当前文章
            # 尝试使用ObjectId
            try:
                article_id_obj = ObjectId(article_id)
                query = {"_id": {"$ne": article_id_obj}}
            except (ValueError, TypeError):
                # 如果不是有效的ObjectId，尝试使用字符串ID
                query = {"id": {"$ne": article_id}}

            # 优先匹配相同标签和分类
            if tags and category:
                # 加权搜索 - 标签匹配更多的文章得分更高
                pipeline = [
                    {"$match": query},
                    {"$addFields": {
                        "matchedTags": {"$size": {"$setIntersection": [tags, {"$ifNull": ["$tags", []]}]}},
                        "categoryMatch": {"$cond": [{"$eq": ["$category", category]}, 3, 0]}
                    }},
                    {"$addFields": {
                        "score": {"$add": ["$matchedTags", "$categoryMatch"]}
                    }},
                    {"$match": {"score": {"$gt": 0}}},  # 至少要有一个标签匹配或分类匹配
                    {"$sort": {"score": -1, "created_at": -1}},
                    {"$limit": limit}
                ]

                cursor = self.articles.aggregate(pipeline)
                articles = await cursor.to_list(length=limit)
            else:
                # 如果没有标签和分类，返回最新文章
                cursor = self.articles.find(query) \
                    .sort("created_at", -1) \
                    .limit(limit)
                articles = await cursor.to_list(length=limit)

            # 处理ObjectId
            for article in articles:
                if "_id" in article:
                    article["id"] = str(article.pop("_id"))

            # 获取浏览次数
            article_ids = [article["id"] for article in articles]
            view_counts = {}

            if article_ids:
                view_cursor = self.view_counts.find({"article_id": {"$in": article_ids}})
                view_docs = await view_cursor.to_list(length=None)
                view_counts = {doc["article_id"]: doc["count"] for doc in view_docs}

            # 添加浏览次数
            for article in articles:
                article["view_count"] = view_counts.get(article["id"], 0)

            return articles
        except PyMongoError as e:
            logger.error(f"查找相关文章失败: {str(e)}")
            metrics.increment_counter("knowledge_repo_errors", {"method": "find_related_articles"})
            return []

    @metrics.measure_execution_time("knowledge_repo_update_article")
    async def update_article(self, article_id: str, update_data: dict[str, Any]) -> bool:
        """
        更新知识文章

        Args:
            article_id: 文章ID
            update_data: 更新的字段数据

        Returns:
            bool: 是否更新成功
        """
        try:
            # 尝试使用ObjectId
            try:
                article_id_obj = ObjectId(article_id)
                result = await self.articles.update_one(
                    {"_id": article_id_obj},
                    {"$set": update_data}
                )
            except (ValueError, TypeError):
                # 如果不是有效的ObjectId，尝试使用字符串ID
                result = await self.articles.update_one(
                    {"id": article_id},
                    {"$set": update_data}
                )

            # 更新分类
            if "category" in update_data and update_data["category"]:
                await self._ensure_category_exists(update_data["category"])

            return result.matched_count > 0
        except PyMongoError as e:
            logger.error(f"更新知识文章失败: {str(e)}")
            metrics.increment_counter("knowledge_repo_errors", {"method": "update_article"})
            return False

    @metrics.measure_execution_time("knowledge_repo_delete_article")
    async def delete_article(self, article_id: str) -> bool:
        """
        删除知识文章

        Args:
            article_id: 文章ID

        Returns:
            bool: 是否删除成功
        """
        try:
            # 尝试使用ObjectId
            try:
                article_id_obj = ObjectId(article_id)
                result = await self.articles.delete_one({"_id": article_id_obj})
            except (ValueError, TypeError):
                # 如果不是有效的ObjectId，尝试使用字符串ID
                result = await self.articles.delete_one({"id": article_id})

            # 删除浏览计数
            await self.view_counts.delete_one({"article_id": article_id})

            return result.deleted_count > 0
        except PyMongoError as e:
            logger.error(f"删除知识文章失败: {str(e)}")
            metrics.increment_counter("knowledge_repo_errors", {"method": "delete_article"})
            return False

    @metrics.measure_execution_time("knowledge_repo_increment_article_view_count")
    async def increment_article_view_count(self, article_id: str) -> bool:
        """
        增加文章浏览次数

        Args:
            article_id: 文章ID

        Returns:
            bool: 是否增加成功
        """
        try:
            # 更新浏览计数
            result = await self.view_counts.update_one(
                {"article_id": article_id},
                {
                    "$inc": {"count": 1},
                    "$set": {"last_updated": datetime.now(UTC).isoformat()}
                },
                upsert=True
            )

            return result.acknowledged
        except PyMongoError as e:
            logger.error(f"增加文章浏览次数失败: {str(e)}")
            metrics.increment_counter("knowledge_repo_errors", {"method": "increment_article_view_count"})
            return False

    @metrics.measure_execution_time("knowledge_repo_create_learning_path")
    async def create_learning_path(self, path_data: dict[str, Any]) -> str | None:
        """
        创建学习路径

        Args:
            path_data: 学习路径数据

        Returns:
            Optional[str]: 创建的学习路径ID，失败时返回None
        """
        try:
            # 确保数据中没有"_id"字段
            if "_id" in path_data:
                del path_data["_id"]

            # 设置创建时间和初始值
            if "created_at" not in path_data:
                path_data["created_at"] = datetime.now(UTC).isoformat()
            if "enrolled_users" not in path_data:
                path_data["enrolled_users"] = 0
            if "completion_rate" not in path_data:
                path_data["completion_rate"] = 0

            # 插入学习路径
            result = await self.learning_paths.insert_one(path_data)

            # 更新分类
            if "category" in path_data and path_data["category"]:
                await self._ensure_category_exists(path_data["category"])

            return str(result.inserted_id)
        except PyMongoError as e:
            logger.error(f"创建学习路径失败: {str(e)}")
            metrics.increment_counter("knowledge_repo_errors", {"method": "create_learning_path"})
            return None

    @metrics.measure_execution_time("knowledge_repo_find_learning_path_by_id")
    async def find_learning_path_by_id(self, path_id: str) -> dict[str, Any] | None:
        """
        根据ID查找学习路径

        Args:
            path_id: 学习路径ID

        Returns:
            Optional[Dict[str, Any]]: 学习路径详情，未找到时返回None
        """
        try:
            # 尝试使用ObjectId
            try:
                path_id_obj = ObjectId(path_id)
                path = await self.learning_paths.find_one({"_id": path_id_obj})
            except (ValueError, TypeError):
                # 如果不是有效的ObjectId，尝试使用字符串ID
                path = await self.learning_paths.find_one({"id": path_id})

            if path:
                # 处理ObjectId
                path["id"] = str(path.pop("_id"))
                return path

            return None
        except PyMongoError as e:
            logger.error(f"查找学习路径失败: {str(e)}")
            metrics.increment_counter("knowledge_repo_errors", {"method": "find_learning_path_by_id"})
            return None

    @metrics.measure_execution_time("knowledge_repo_find_learning_paths")
    async def find_learning_paths(self,
                                category: str | None = None,
                                level: str | None = None,
                                limit: int = 10,
                                offset: int = 0) -> list[dict[str, Any]]:
        """
        查找学习路径列表

        Args:
            category: 过滤的分类名称
            level: 难度级别
            limit: 返回记录数量限制
            offset: 分页偏移量

        Returns:
            List[Dict[str, Any]]: 学习路径列表
        """
        try:
            # 构建查询条件
            query = {}
            if category:
                query["category"] = category
            if level:
                query["level"] = level

            # 执行查询
            cursor = self.learning_paths.find(query) \
                .sort("created_at", -1) \
                .skip(offset) \
                .limit(limit)

            paths = await cursor.to_list(length=limit)

            # 处理ObjectId
            for path in paths:
                path["id"] = str(path.pop("_id"))

            return paths
        except PyMongoError as e:
            logger.error(f"查找学习路径列表失败: {str(e)}")
            metrics.increment_counter("knowledge_repo_errors", {"method": "find_learning_paths"})
            return []

    @metrics.measure_execution_time("knowledge_repo_update_learning_path")
    async def update_learning_path(self, path_id: str, update_data: dict[str, Any]) -> bool:
        """
        更新学习路径

        Args:
            path_id: 学习路径ID
            update_data: 更新的字段数据

        Returns:
            bool: 是否更新成功
        """
        try:
            # 尝试使用ObjectId
            try:
                path_id_obj = ObjectId(path_id)
                result = await self.learning_paths.update_one(
                    {"_id": path_id_obj},
                    {"$set": update_data}
                )
            except (ValueError, TypeError):
                # 如果不是有效的ObjectId，尝试使用字符串ID
                result = await self.learning_paths.update_one(
                    {"id": path_id},
                    {"$set": update_data}
                )

            # 更新分类
            if "category" in update_data and update_data["category"]:
                await self._ensure_category_exists(update_data["category"])

            return result.matched_count > 0
        except PyMongoError as e:
            logger.error(f"更新学习路径失败: {str(e)}")
            metrics.increment_counter("knowledge_repo_errors", {"method": "update_learning_path"})
            return False

    @metrics.measure_execution_time("knowledge_repo_delete_learning_path")
    async def delete_learning_path(self, path_id: str) -> bool:
        """
        删除学习路径

        Args:
            path_id: 学习路径ID

        Returns:
            bool: 是否删除成功
        """
        try:
            # 尝试使用ObjectId
            try:
                path_id_obj = ObjectId(path_id)
                result = await self.learning_paths.delete_one({"_id": path_id_obj})
            except (ValueError, TypeError):
                # 如果不是有效的ObjectId，尝试使用字符串ID
                result = await self.learning_paths.delete_one({"id": path_id})

            # 删除相关的用户进度记录
            await self.user_progress.delete_many({"path_id": path_id})

            return result.deleted_count > 0
        except PyMongoError as e:
            logger.error(f"删除学习路径失败: {str(e)}")
            metrics.increment_counter("knowledge_repo_errors", {"method": "delete_learning_path"})
            return False

    @metrics.measure_execution_time("knowledge_repo_get_user_learning_progress")
    async def get_user_learning_progress(self, user_id: str, path_id: str) -> dict[str, Any]:
        """
        获取用户学习进度

        Args:
            user_id: 用户ID
            path_id: 学习路径ID

        Returns:
            Dict[str, Any]: 用户学习进度，未找到时返回初始进度
        """
        try:
            # 查询用户进度
            progress = await self.user_progress.find_one({"user_id": user_id, "path_id": path_id})

            if progress:
                # 处理ObjectId
                if "_id" in progress:
                    progress["id"] = str(progress.pop("_id"))

                return progress

            # 未找到进度，返回初始进度
            return {
                "user_id": user_id,
                "path_id": path_id,
                "completed_modules": [],
                "current_module_id": None,
                "progress_percentage": 0,
                "started_at": None,
                "last_activity_at": None
            }
        except PyMongoError as e:
            logger.error(f"获取用户学习进度失败: {str(e)}")
            metrics.increment_counter("knowledge_repo_errors", {"method": "get_user_learning_progress"})
            return {
                "user_id": user_id,
                "path_id": path_id,
                "completed_modules": [],
                "current_module_id": None,
                "progress_percentage": 0,
                "started_at": None,
                "last_activity_at": None
            }

    @metrics.measure_execution_time("knowledge_repo_update_user_learning_progress")
    async def update_user_learning_progress(self, user_id: str, path_id: str, progress_data: dict[str, Any]) -> bool:
        """
        更新用户学习进度

        Args:
            user_id: 用户ID
            path_id: 学习路径ID
            progress_data: 进度数据

        Returns:
            bool: 是否更新成功
        """
        try:
            # 确保user_id和path_id存在于数据中
            progress_data["user_id"] = user_id
            progress_data["path_id"] = path_id

            # 更新进度
            result = await self.user_progress.update_one(
                {"user_id": user_id, "path_id": path_id},
                {"$set": progress_data},
                upsert=True
            )

            return result.acknowledged
        except PyMongoError as e:
            logger.error(f"更新用户学习进度失败: {str(e)}")
            metrics.increment_counter("knowledge_repo_errors", {"method": "update_user_learning_progress"})
            return False

    @metrics.measure_execution_time("knowledge_repo_get_all_user_progress_for_path")
    async def get_all_user_progress_for_path(self, path_id: str) -> list[dict[str, Any]]:
        """
        获取学习路径的所有用户进度

        Args:
            path_id: 学习路径ID

        Returns:
            List[Dict[str, Any]]: 用户进度列表
        """
        try:
            # 查询所有用户进度
            cursor = self.user_progress.find({"path_id": path_id})
            progress_list = await cursor.to_list(length=None)

            # 处理ObjectId
            for progress in progress_list:
                if "_id" in progress:
                    progress["id"] = str(progress.pop("_id"))

            return progress_list
        except PyMongoError as e:
            logger.error(f"获取学习路径的所有用户进度失败: {str(e)}")
            metrics.increment_counter("knowledge_repo_errors", {"method": "get_all_user_progress_for_path"})
            return []

    @metrics.measure_execution_time("knowledge_repo_get_categories")
    async def get_categories(self) -> list[dict[str, Any]]:
        """
        获取知识分类列表

        Returns:
            List[Dict[str, Any]]: 分类列表
        """
        try:
            # 查询所有分类
            cursor = self.categories.find().sort("name", 1)
            categories = await cursor.to_list(length=None)

            # 处理ObjectId
            for category in categories:
                if "_id" in category:
                    category["id"] = str(category.pop("_id"))

            return categories
        except PyMongoError as e:
            logger.error(f"获取知识分类列表失败: {str(e)}")
            metrics.increment_counter("knowledge_repo_errors", {"method": "get_categories"})
            return []

    async def _ensure_category_exists(self, category_name: str) -> None:
        """
        确保分类存在

        Args:
            category_name: 分类名称
        """
        try:
            # 更新或创建分类
            await self.categories.update_one(
                {"name": category_name},
                {"$setOnInsert": {
                    "created_at": datetime.now(UTC).isoformat(),
                    "description": ""
                }},
                upsert=True
            )
        except PyMongoError as e:
            logger.error(f"确保分类存在失败: {str(e)}")
            # 不返回错误，避免影响主要功能

# 创建单例实例
knowledge_repository = KnowledgeRepository()
