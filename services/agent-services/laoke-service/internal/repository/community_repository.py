#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
老克智能体服务 - 社区内容存储库
提供社区内容的存储和检索功能
"""

import uuid
import logging
import asyncio
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Tuple

import motor.motor_asyncio
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError

from pkg.utils.config import Config
from pkg.utils.metrics import get_metrics_collector

logger = logging.getLogger(__name__)
metrics = get_metrics_collector()

class CommunityRepository:
    """社区内容存储库，提供社区内容的CRUD操作"""
    
    def __init__(self):
        """初始化社区内容存储库"""
        self.config = Config()
        self.db_config = self.config.get_section("database.mongodb")
        
        # 连接到MongoDB
        self.client = motor.motor_asyncio.AsyncIOMotorClient(self.db_config.get("uri"))
        self.db = self.client[self.db_config.get("database", "laoke_db")]
        
        # 集合
        self.posts = self.db.posts
        self.likes = self.db.likes
        self.tags = self.db.tags
        self.categories = self.db.categories
        
        logger.info("社区内容存储库已初始化")
    
    async def init_indexes(self):
        """初始化数据库索引"""
        try:
            # 帖子集合索引
            await self.posts.create_index("author_id")
            await self.posts.create_index("category")
            await self.posts.create_index("tags")
            await self.posts.create_index("created_at")
            await self.posts.create_index("is_featured")
            await self.posts.create_index([("title", "text"), ("content", "text")])
            
            # 点赞集合索引
            await self.likes.create_index([("post_id", 1), ("user_id", 1)], unique=True)
            
            logger.info("社区内容存储库索引已初始化")
        except PyMongoError as e:
            logger.error(f"初始化社区内容存储库索引失败: {str(e)}")
            raise
    
    @metrics.measure_execution_time("community_repo_find_featured_posts")
    async def find_featured_posts(self, limit: int = 5, offset: int = 0) -> List[Dict[str, Any]]:
        """
        获取精选社区帖子
        
        Args:
            limit: 返回记录数量限制
            offset: 分页偏移量
            
        Returns:
            List[Dict[str, Any]]: 精选帖子列表
        """
        try:
            cursor = self.posts.find({"is_featured": True}) \
                .sort("created_at", -1) \
                .skip(offset) \
                .limit(limit)
            
            posts = await cursor.to_list(length=limit)
            
            # 处理ObjectId
            for post in posts:
                post["id"] = str(post.pop("_id"))
            
            return posts
        except PyMongoError as e:
            logger.error(f"获取精选社区帖子失败: {str(e)}")
            metrics.increment_counter("community_repo_errors", {"method": "find_featured_posts"})
            return []
    
    @metrics.measure_execution_time("community_repo_find_posts")
    async def find_posts(self, 
                        category: Optional[str] = None, 
                        tags: Optional[List[str]] = None,
                        author_id: Optional[str] = None,
                        limit: int = 10, 
                        offset: int = 0,
                        sort_by: str = "created_at",
                        sort_order: str = "desc") -> List[Dict[str, Any]]:
        """
        获取社区帖子列表
        
        Args:
            category: 过滤的分类名称
            tags: 过滤的标签列表
            author_id: 筛选特定作者的帖子
            limit: 返回记录数量限制
            offset: 分页偏移量
            sort_by: 排序字段
            sort_order: 排序顺序 (asc 或 desc)
            
        Returns:
            List[Dict[str, Any]]: 社区帖子列表
        """
        try:
            # 构建查询条件
            query = {}
            if category:
                query["category"] = category
            if tags:
                query["tags"] = {"$in": tags}
            if author_id:
                query["author_id"] = author_id
            
            # 排序方向
            sort_direction = 1 if sort_order.lower() == "asc" else -1
            
            # 执行查询
            cursor = self.posts.find(query) \
                .sort(sort_by, sort_direction) \
                .skip(offset) \
                .limit(limit)
            
            posts = await cursor.to_list(length=limit)
            
            # 处理ObjectId
            for post in posts:
                post["id"] = str(post.pop("_id"))
            
            return posts
        except PyMongoError as e:
            logger.error(f"获取社区帖子失败: {str(e)}")
            metrics.increment_counter("community_repo_errors", {"method": "find_posts"})
            return []
    
    @metrics.measure_execution_time("community_repo_find_post_by_id")
    async def find_post_by_id(self, post_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ID获取社区帖子详情
        
        Args:
            post_id: 帖子ID
            
        Returns:
            Optional[Dict[str, Any]]: 帖子详情，未找到时返回None
        """
        try:
            # 尝试转换为ObjectId
            try:
                post_id_obj = ObjectId(post_id)
                query = {"_id": post_id_obj}
            except:
                # 如果不是有效的ObjectId，尝试使用字符串ID
                query = {"id": post_id}
            
            # 执行查询
            post = await self.posts.find_one(query)
            
            if post:
                # 处理ObjectId
                post["id"] = str(post.pop("_id"))
                return post
            
            return None
        except PyMongoError as e:
            logger.error(f"根据ID获取社区帖子失败: {str(e)}")
            metrics.increment_counter("community_repo_errors", {"method": "find_post_by_id"})
            return None
    
    @metrics.measure_execution_time("community_repo_search_posts")
    async def search_posts(self, search_text: str, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """
        搜索社区帖子
        
        Args:
            search_text: 搜索文本
            limit: 返回记录数量限制
            offset: 分页偏移量
            
        Returns:
            List[Dict[str, Any]]: 符合搜索条件的帖子列表
        """
        try:
            # 执行全文搜索
            cursor = self.posts.find(
                {"$text": {"$search": search_text}}
            ) \
                .sort([("score", {"$meta": "textScore"}), ("created_at", -1)]) \
                .skip(offset) \
                .limit(limit)
            
            posts = await cursor.to_list(length=limit)
            
            # 处理ObjectId
            for post in posts:
                post["id"] = str(post.pop("_id"))
            
            return posts
        except PyMongoError as e:
            logger.error(f"搜索社区帖子失败: {str(e)}")
            metrics.increment_counter("community_repo_errors", {"method": "search_posts"})
            return []
    
    @metrics.measure_execution_time("community_repo_create_post")
    async def create_post(self, post_data: Dict[str, Any]) -> Optional[str]:
        """
        创建社区帖子
        
        Args:
            post_data: 帖子数据
            
        Returns:
            Optional[str]: 创建的帖子ID，失败时返回None
        """
        try:
            # 确保数据中没有"_id"字段
            if "_id" in post_data:
                del post_data["_id"]
            
            # 插入帖子
            result = await self.posts.insert_one(post_data)
            
            if result.inserted_id:
                # 更新标签使用计数
                if "tags" in post_data and post_data["tags"]:
                    await self._update_tags_count(post_data["tags"])
                
                # 更新分类
                if "category" in post_data and post_data["category"]:
                    await self._ensure_category_exists(post_data["category"])
                
                return str(result.inserted_id)
            
            return None
        except PyMongoError as e:
            logger.error(f"创建社区帖子失败: {str(e)}")
            metrics.increment_counter("community_repo_errors", {"method": "create_post"})
            return None
    
    @metrics.measure_execution_time("community_repo_update_post")
    async def update_post(self, post_id: str, update_data: Dict[str, Any]) -> bool:
        """
        更新社区帖子
        
        Args:
            post_id: 帖子ID
            update_data: 更新的字段数据
            
        Returns:
            bool: 是否更新成功
        """
        try:
            # 尝试转换为ObjectId
            try:
                post_id_obj = ObjectId(post_id)
                query = {"_id": post_id_obj}
            except:
                # 如果不是有效的ObjectId，尝试使用字符串ID
                query = {"id": post_id}
            
            # 获取旧的帖子信息，用于标签更新
            old_post = None
            if "tags" in update_data:
                old_post = await self.posts.find_one(query)
            
            # 更新帖子
            result = await self.posts.update_one(query, {"$set": update_data})
            
            if result.matched_count > 0:
                # 处理标签变更
                if old_post and "tags" in update_data:
                    old_tags = old_post.get("tags", [])
                    new_tags = update_data["tags"]
                    
                    # 增加新标签计数
                    new_tags_to_add = [tag for tag in new_tags if tag not in old_tags]
                    if new_tags_to_add:
                        await self._update_tags_count(new_tags_to_add)
                    
                    # 减少移除标签计数
                    removed_tags = [tag for tag in old_tags if tag not in new_tags]
                    if removed_tags:
                        await self._update_tags_count(removed_tags, increment=-1)
                
                # 更新分类
                if "category" in update_data and update_data["category"]:
                    await self._ensure_category_exists(update_data["category"])
                
                return True
            
            return False
        except PyMongoError as e:
            logger.error(f"更新社区帖子失败: {str(e)}")
            metrics.increment_counter("community_repo_errors", {"method": "update_post"})
            return False
    
    @metrics.measure_execution_time("community_repo_delete_post")
    async def delete_post(self, post_id: str) -> bool:
        """
        删除社区帖子
        
        Args:
            post_id: 帖子ID
            
        Returns:
            bool: 是否删除成功
        """
        try:
            # 尝试转换为ObjectId
            try:
                post_id_obj = ObjectId(post_id)
                query = {"_id": post_id_obj}
            except:
                # 如果不是有效的ObjectId，尝试使用字符串ID
                query = {"id": post_id}
            
            # 获取帖子信息，用于标签更新
            post = await self.posts.find_one(query)
            
            if post:
                # 删除帖子
                result = await self.posts.delete_one(query)
                
                if result.deleted_count > 0:
                    # 减少标签使用计数
                    if "tags" in post and post["tags"]:
                        await self._update_tags_count(post["tags"], increment=-1)
                    
                    # 删除相关点赞记录
                    await self.likes.delete_many({"post_id": post_id})
                    
                    return True
            
            return False
        except PyMongoError as e:
            logger.error(f"删除社区帖子失败: {str(e)}")
            metrics.increment_counter("community_repo_errors", {"method": "delete_post"})
            return False
    
    @metrics.measure_execution_time("community_repo_add_comment")
    async def add_comment(self, post_id: str, comment_data: Dict[str, Any]) -> bool:
        """
        添加评论到社区帖子
        
        Args:
            post_id: 帖子ID
            comment_data: 评论数据
            
        Returns:
            bool: 是否添加成功
        """
        try:
            # 尝试转换为ObjectId
            try:
                post_id_obj = ObjectId(post_id)
                query = {"_id": post_id_obj}
            except:
                # 如果不是有效的ObjectId，尝试使用字符串ID
                query = {"id": post_id}
            
            # 添加评论
            result = await self.posts.update_one(
                query,
                {"$push": {"comments": comment_data}}
            )
            
            return result.matched_count > 0
        except PyMongoError as e:
            logger.error(f"添加评论到社区帖子失败: {str(e)}")
            metrics.increment_counter("community_repo_errors", {"method": "add_comment"})
            return False
    
    @metrics.measure_execution_time("community_repo_add_like")
    async def add_like(self, post_id: str, user_id: str) -> bool:
        """
        给帖子点赞
        
        Args:
            post_id: 帖子ID
            user_id: 用户ID
            
        Returns:
            bool: 是否点赞成功
        """
        try:
            # 记录点赞
            result = await self.likes.update_one(
                {"post_id": post_id, "user_id": user_id},
                {"$set": {"created_at": datetime.now(timezone.utc).isoformat()}},
                upsert=True
            )
            
            return result.acknowledged
        except PyMongoError as e:
            logger.error(f"给帖子点赞失败: {str(e)}")
            metrics.increment_counter("community_repo_errors", {"method": "add_like"})
            return False
    
    @metrics.measure_execution_time("community_repo_check_user_liked")
    async def check_user_liked(self, post_id: str, user_id: str) -> bool:
        """
        检查用户是否已点赞帖子
        
        Args:
            post_id: 帖子ID
            user_id: 用户ID
            
        Returns:
            bool: 用户是否已点赞
        """
        try:
            # 查询点赞记录
            like = await self.likes.find_one({"post_id": post_id, "user_id": user_id})
            return like is not None
        except PyMongoError as e:
            logger.error(f"检查用户点赞状态失败: {str(e)}")
            metrics.increment_counter("community_repo_errors", {"method": "check_user_liked"})
            return False
    
    @metrics.measure_execution_time("community_repo_get_categories")
    async def get_categories(self) -> List[str]:
        """
        获取所有社区帖子分类
        
        Returns:
            List[str]: 分类列表
        """
        try:
            # 获取所有分类
            cursor = self.categories.find().sort("name", 1)
            categories_docs = await cursor.to_list(length=100)
            
            return [doc["name"] for doc in categories_docs]
        except PyMongoError as e:
            logger.error(f"获取社区帖子分类失败: {str(e)}")
            metrics.increment_counter("community_repo_errors", {"method": "get_categories"})
            return []
    
    @metrics.measure_execution_time("community_repo_get_popular_tags")
    async def get_popular_tags(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取热门标签
        
        Args:
            limit: 返回标签数量
            
        Returns:
            List[Dict[str, Any]]: 标签列表，包含标签名和使用计数
        """
        try:
            # 获取热门标签
            cursor = self.tags.find().sort("count", -1).limit(limit)
            tags = await cursor.to_list(length=limit)
            
            # 处理ObjectId
            for tag in tags:
                if "_id" in tag:
                    tag["id"] = str(tag.pop("_id"))
            
            return tags
        except PyMongoError as e:
            logger.error(f"获取热门标签失败: {str(e)}")
            metrics.increment_counter("community_repo_errors", {"method": "get_popular_tags"})
            return []
    
    async def _update_tags_count(self, tags: List[str], increment: int = 1) -> None:
        """
        更新标签使用计数
        
        Args:
            tags: 标签列表
            increment: 增量值，1表示增加，-1表示减少
        """
        try:
            for tag in tags:
                if increment > 0:
                    # 增加标签计数或创建新标签
                    await self.tags.update_one(
                        {"name": tag},
                        {"$inc": {"count": increment}, "$setOnInsert": {"created_at": datetime.now(timezone.utc).isoformat()}},
                        upsert=True
                    )
                else:
                    # 减少标签计数
                    await self.tags.update_one(
                        {"name": tag, "count": {"$gt": 0}},
                        {"$inc": {"count": increment}}
                    )
                    
                    # 删除计数为0的标签
                    await self.tags.delete_many({"count": {"$lte": 0}})
        except PyMongoError as e:
            logger.error(f"更新标签使用计数失败: {str(e)}")
    
    async def _ensure_category_exists(self, category: str) -> None:
        """
        确保分类存在
        
        Args:
            category: 分类名称
        """
        try:
            await self.categories.update_one(
                {"name": category},
                {"$setOnInsert": {"created_at": datetime.now(timezone.utc).isoformat()}},
                upsert=True
            )
        except PyMongoError as e:
            logger.error(f"确保分类存在失败: {str(e)}")

# 创建单例实例
community_repository = CommunityRepository() 