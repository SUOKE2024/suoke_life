#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
索儿智能体服务 - 知识存储库
提供健康知识、生活方式和个性化建议的存储和检索
"""

import uuid
import logging
import asyncio
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Tuple, Set

import motor.motor_asyncio
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError

from pkg.utils.config_loader import get_config
from pkg.utils.metrics import get_metrics_collector

logger = logging.getLogger(__name__)
metrics = get_metrics_collector()

class KnowledgeRepository:
    """知识存储库，提供健康知识、生活方式和个性化建议的存储和检索"""
    
    def __init__(self):
        """初始化知识存储库"""
        self.config = get_config()
        self.db_config = self.config.get_section("database.mongodb")
        
        # 连接到MongoDB
        self.client = motor.motor_asyncio.AsyncIOMotorClient(self.db_config.get("uri"))
        self.db = self.client[self.db_config.get("database", "soer_db")]
        
        # 集合
        self.health_knowledge = self.db.health_knowledge
        self.lifestyle_recommendations = self.db.lifestyle_recommendations
        self.user_preferences = self.db.user_preferences
        self.user_insights = self.db.user_insights  # 存储关于用户的长期洞察
        
        logger.info("知识存储库已初始化")
    
    async def init_indexes(self):
        """初始化数据库索引"""
        try:
            # 健康知识索引
            await self.health_knowledge.create_index("category")
            await self.health_knowledge.create_index("tags")
            await self.health_knowledge.create_index([("title", "text"), ("content", "text")])
            
            # 生活方式建议索引
            await self.lifestyle_recommendations.create_index("category")
            await self.lifestyle_recommendations.create_index("tags")
            await self.lifestyle_recommendations.create_index("difficulty_level")
            await self.lifestyle_recommendations.create_index([("title", "text"), ("content", "text")])
            
            # 用户偏好索引
            await self.user_preferences.create_index([("user_id", 1)], unique=True)
            
            # 用户洞察索引
            await self.user_insights.create_index("user_id")
            await self.user_insights.create_index("category")
            await self.user_insights.create_index("created_at")
            await self.user_insights.create_index("confidence")
            
            logger.info("知识存储库索引已初始化")
        except PyMongoError as e:
            logger.error(f"初始化知识存储库索引失败: {str(e)}")
            raise
    
    @metrics.measure_execution_time("knowledge_repo_create_health_knowledge")
    async def create_health_knowledge(self, knowledge_data: Dict[str, Any]) -> Optional[str]:
        """
        创建健康知识条目
        
        Args:
            knowledge_data: 知识数据
            
        Returns:
            Optional[str]: 创建的知识条目ID，失败时返回None
        """
        try:
            # 确保数据中没有"_id"字段
            if "_id" in knowledge_data:
                del knowledge_data["_id"]
            
            # 设置创建时间
            if "created_at" not in knowledge_data:
                knowledge_data["created_at"] = datetime.now(timezone.utc).isoformat()
            
            # 插入知识条目
            result = await self.health_knowledge.insert_one(knowledge_data)
            
            return str(result.inserted_id)
        except PyMongoError as e:
            logger.error(f"创建健康知识条目失败: {str(e)}")
            metrics.increment_counter("knowledge_repo_errors", {"method": "create_health_knowledge"})
            return None
    
    @metrics.measure_execution_time("knowledge_repo_find_health_knowledge")
    async def find_health_knowledge(self,
                                 category: Optional[str] = None,
                                 tags: Optional[List[str]] = None,
                                 limit: int = 10,
                                 offset: int = 0,
                                 sort_by: str = "created_at",
                                 sort_order: str = "desc") -> List[Dict[str, Any]]:
        """
        查找健康知识条目
        
        Args:
            category: 分类
            tags: 标签列表
            limit: 返回条目数量限制
            offset: 分页偏移量
            sort_by: 排序字段
            sort_order: 排序顺序 (asc 或 desc)
            
        Returns:
            List[Dict[str, Any]]: 知识条目列表
        """
        try:
            # 构建查询条件
            query = {}
            if category:
                query["category"] = category
            if tags:
                query["tags"] = {"$in": tags}
            
            # 排序方向
            sort_direction = 1 if sort_order.lower() == "asc" else -1
            
            # 执行查询
            cursor = self.health_knowledge.find(query) \
                .sort(sort_by, sort_direction) \
                .skip(offset) \
                .limit(limit)
            
            knowledge_items = await cursor.to_list(length=limit)
            
            # 处理ObjectId
            for item in knowledge_items:
                item["id"] = str(item.pop("_id"))
            
            return knowledge_items
        except PyMongoError as e:
            logger.error(f"查找健康知识条目失败: {str(e)}")
            metrics.increment_counter("knowledge_repo_errors", {"method": "find_health_knowledge"})
            return []
    
    @metrics.measure_execution_time("knowledge_repo_search_health_knowledge")
    async def search_health_knowledge(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        搜索健康知识
        
        Args:
            query: 搜索关键词
            limit: 返回条目数量限制
            
        Returns:
            List[Dict[str, Any]]: 搜索结果
        """
        try:
            # 执行全文搜索
            cursor = self.health_knowledge.find(
                {"$text": {"$search": query}},
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]).limit(limit)
            
            results = await cursor.to_list(length=limit)
            
            # 处理ObjectId
            for item in results:
                item["id"] = str(item.pop("_id"))
            
            return results
        except PyMongoError as e:
            logger.error(f"搜索健康知识失败: {str(e)}")
            metrics.increment_counter("knowledge_repo_errors", {"method": "search_health_knowledge"})
            return []
    
    @metrics.measure_execution_time("knowledge_repo_create_lifestyle_recommendation")
    async def create_lifestyle_recommendation(self, recommendation_data: Dict[str, Any]) -> Optional[str]:
        """
        创建生活方式建议
        
        Args:
            recommendation_data: 建议数据
            
        Returns:
            Optional[str]: 创建的建议ID，失败时返回None
        """
        try:
            # 确保数据中没有"_id"字段
            if "_id" in recommendation_data:
                del recommendation_data["_id"]
            
            # 设置创建时间
            if "created_at" not in recommendation_data:
                recommendation_data["created_at"] = datetime.now(timezone.utc).isoformat()
            
            # 插入建议
            result = await self.lifestyle_recommendations.insert_one(recommendation_data)
            
            return str(result.inserted_id)
        except PyMongoError as e:
            logger.error(f"创建生活方式建议失败: {str(e)}")
            metrics.increment_counter("knowledge_repo_errors", {"method": "create_lifestyle_recommendation"})
            return None
    
    @metrics.measure_execution_time("knowledge_repo_find_lifestyle_recommendations")
    async def find_lifestyle_recommendations(self,
                                          category: Optional[str] = None,
                                          tags: Optional[List[str]] = None,
                                          difficulty_level: Optional[str] = None,
                                          limit: int = 10,
                                          offset: int = 0) -> List[Dict[str, Any]]:
        """
        查找生活方式建议
        
        Args:
            category: 分类
            tags: 标签列表
            difficulty_level: 难度级别
            limit: 返回条目数量限制
            offset: 分页偏移量
            
        Returns:
            List[Dict[str, Any]]: 建议列表
        """
        try:
            # 构建查询条件
            query = {}
            if category:
                query["category"] = category
            if tags:
                query["tags"] = {"$in": tags}
            if difficulty_level:
                query["difficulty_level"] = difficulty_level
            
            # 执行查询
            cursor = self.lifestyle_recommendations.find(query) \
                .sort("created_at", -1) \
                .skip(offset) \
                .limit(limit)
            
            recommendations = await cursor.to_list(length=limit)
            
            # 处理ObjectId
            for item in recommendations:
                item["id"] = str(item.pop("_id"))
            
            return recommendations
        except PyMongoError as e:
            logger.error(f"查找生活方式建议失败: {str(e)}")
            metrics.increment_counter("knowledge_repo_errors", {"method": "find_lifestyle_recommendations"})
            return []
    
    @metrics.measure_execution_time("knowledge_repo_get_user_preferences")
    async def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        获取用户偏好
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[Dict[str, Any]]: 用户偏好，不存在时返回None
        """
        try:
            preferences = await self.user_preferences.find_one({"user_id": user_id})
            
            if preferences:
                # 处理ObjectId
                preferences["id"] = str(preferences.pop("_id"))
                
                return preferences
            
            return None
        except PyMongoError as e:
            logger.error(f"获取用户偏好失败: {str(e)}")
            metrics.increment_counter("knowledge_repo_errors", {"method": "get_user_preferences"})
            return None
    
    @metrics.measure_execution_time("knowledge_repo_update_user_preferences")
    async def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """
        更新用户偏好
        
        Args:
            user_id: 用户ID
            preferences: 偏好数据
            
        Returns:
            bool: 是否更新成功
        """
        try:
            # 确保user_id字段存在
            preferences["user_id"] = user_id
            preferences["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            # 使用upsert确保创建或更新
            result = await self.user_preferences.update_one(
                {"user_id": user_id},
                {"$set": preferences},
                upsert=True
            )
            
            return result.modified_count > 0 or result.upserted_id is not None
        except PyMongoError as e:
            logger.error(f"更新用户偏好失败: {str(e)}")
            metrics.increment_counter("knowledge_repo_errors", {"method": "update_user_preferences"})
            return False
    
    @metrics.measure_execution_time("knowledge_repo_add_user_insight")
    async def add_user_insight(self, user_id: str, insight_data: Dict[str, Any]) -> Optional[str]:
        """
        添加用户洞察
        
        Args:
            user_id: 用户ID
            insight_data: 洞察数据
            
        Returns:
            Optional[str]: 创建的洞察ID，失败时返回None
        """
        try:
            # 确保数据中没有"_id"字段
            if "_id" in insight_data:
                del insight_data["_id"]
            
            # 设置基本字段
            insight_data["user_id"] = user_id
            insight_data["created_at"] = datetime.now(timezone.utc).isoformat()
            insight_data["insight_id"] = str(uuid.uuid4())
            
            # 设置默认值
            if "confidence" not in insight_data:
                insight_data["confidence"] = 0.7  # 默认置信度
            if "importance" not in insight_data:
                insight_data["importance"] = 5  # 默认重要性 (1-10)
            
            # 插入洞察
            result = await self.user_insights.insert_one(insight_data)
            
            return insight_data["insight_id"]
        except PyMongoError as e:
            logger.error(f"添加用户洞察失败: {str(e)}")
            metrics.increment_counter("knowledge_repo_errors", {"method": "add_user_insight"})
            return None
    
    @metrics.measure_execution_time("knowledge_repo_get_user_insights")
    async def get_user_insights(self, 
                             user_id: str, 
                             category: Optional[str] = None,
                             min_confidence: float = 0.5,
                             limit: int = 10,
                             offset: int = 0) -> List[Dict[str, Any]]:
        """
        获取用户洞察
        
        Args:
            user_id: 用户ID
            category: 洞察类别（可选）
            min_confidence: 最小置信度
            limit: 返回条目数量限制
            offset: 分页偏移量
            
        Returns:
            List[Dict[str, Any]]: 用户洞察列表
        """
        try:
            # 构建查询条件
            query = {
                "user_id": user_id,
                "confidence": {"$gte": min_confidence}
            }
            
            if category:
                query["category"] = category
            
            # 执行查询
            cursor = self.user_insights.find(query) \
                .sort([("importance", -1), ("created_at", -1)]) \
                .skip(offset) \
                .limit(limit)
            
            insights = await cursor.to_list(length=limit)
            
            # 处理ObjectId
            for item in insights:
                item["id"] = str(item.pop("_id"))
            
            return insights
        except PyMongoError as e:
            logger.error(f"获取用户洞察失败: {str(e)}")
            metrics.increment_counter("knowledge_repo_errors", {"method": "get_user_insights"})
            return []
    
    @metrics.measure_execution_time("knowledge_repo_update_insight_confidence")
    async def update_insight_confidence(self, insight_id: str, confidence_delta: float) -> bool:
        """
        更新洞察置信度
        
        Args:
            insight_id: 洞察ID
            confidence_delta: 置信度变化值 (-1.0 到 1.0)
            
        Returns:
            bool: 是否更新成功
        """
        try:
            # 获取当前洞察
            insight = await self.user_insights.find_one({"insight_id": insight_id})
            if not insight:
                return False
            
            current_confidence = insight.get("confidence", 0.5)
            
            # 计算新置信度，确保在0-1范围内
            new_confidence = max(0.0, min(1.0, current_confidence + confidence_delta))
            
            # 更新置信度
            result = await self.user_insights.update_one(
                {"insight_id": insight_id},
                {"$set": {
                    "confidence": new_confidence,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            
            return result.modified_count > 0
        except PyMongoError as e:
            logger.error(f"更新洞察置信度失败: {str(e)}")
            metrics.increment_counter("knowledge_repo_errors", {"method": "update_insight_confidence"})
            return False
    
    @metrics.measure_execution_time("knowledge_repo_get_personalized_recommendations")
    async def get_personalized_recommendations(self, 
                                           user_id: str, 
                                           limit: int = 5) -> List[Dict[str, Any]]:
        """
        获取个性化建议
        结合用户偏好和洞察，生成个性化的健康及生活方式建议
        
        Args:
            user_id: 用户ID
            limit: 返回建议数量
            
        Returns:
            List[Dict[str, Any]]: 个性化建议列表
        """
        try:
            # 获取用户偏好
            preferences = await self.get_user_preferences(user_id)
            if not preferences:
                # 如果没有偏好数据，返回通用建议
                return await self.find_lifestyle_recommendations(limit=limit)
            
            # 获取用户洞察
            insights = await self.get_user_insights(
                user_id=user_id, 
                min_confidence=0.7,
                limit=10
            )
            
            # 提取用户健康兴趣和关注点
            health_interests = preferences.get("health_interests", [])
            difficulty_level = preferences.get("preferred_difficulty", "medium")
            
            # 从洞察中提取推荐标签
            insight_tags = set()
            for insight in insights:
                tags = insight.get("tags", [])
                insight_tags.update(tags)
            
            # 构建查询条件
            query = {
                "$or": [
                    {"tags": {"$in": list(insight_tags)}},
                    {"category": {"$in": health_interests}}
                ]
            }
            
            if difficulty_level:
                query["difficulty_level"] = difficulty_level
            
            # 执行查询
            cursor = self.lifestyle_recommendations.find(query) \
                .sort("created_at", -1) \
                .limit(limit)
            
            recommendations = await cursor.to_list(length=limit)
            
            # 处理ObjectId
            for item in recommendations:
                item["id"] = str(item.pop("_id"))
            
            # 如果结果不足，补充通用建议
            if len(recommendations) < limit:
                additional_limit = limit - len(recommendations)
                existing_ids = {item["id"] for item in recommendations}
                
                # 获取额外的建议
                additional_cursor = self.lifestyle_recommendations.find(
                    {"_id": {"$nin": [ObjectId(id) for id in existing_ids]}}
                ).sort("created_at", -1).limit(additional_limit)
                
                additional_recommendations = await additional_cursor.to_list(length=additional_limit)
                
                # 处理ObjectId
                for item in additional_recommendations:
                    item["id"] = str(item.pop("_id"))
                
                recommendations.extend(additional_recommendations)
            
            return recommendations
        except PyMongoError as e:
            logger.error(f"获取个性化建议失败: {str(e)}")
            metrics.increment_counter("knowledge_repo_errors", {"method": "get_personalized_recommendations"})
            return [] 