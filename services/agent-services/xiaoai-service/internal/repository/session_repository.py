#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会话存储库
负责存储和检索用户会话数据
"""

import logging
import time
import json
from typing import Dict, List, Any, Optional
import motor.motor_asyncio
from bson.objectid import ObjectId

from pkg.utils.config_loader import get_config
from pkg.utils.metrics import track_db_metrics, get_metrics_collector

logger = logging.getLogger(__name__)

class SessionRepository:
    """会话存储库，负责存储和检索用户会话数据"""
    
    def __init__(self):
        """初始化会话存储库"""
        self.config = get_config()
        self.metrics = get_metrics_collector()
        
        # 获取MongoDB配置
        mongodb_config = self.config.get_section('database.mongodb')
        self.mongodb_uri = mongodb_config.get('uri', 'mongodb://localhost:27017/xiaoai_db')
        self.session_collection_name = mongodb_config.get_nested('collections', 'session_data', default='session_data')
        
        # 获取会话配置
        conversation_config = self.config.get_section('conversation')
        self.session_timeout = conversation_config.get('session_timeout_minutes', 30) * 60  # 转换为秒
        
        # 连接MongoDB
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(self.mongodb_uri)
            db_name = self.mongodb_uri.split('/')[-1]
            self.db = self.client[db_name]
            self.session_collection = self.db[self.session_collection_name]
            
            # 创建索引
            self._create_indexes()
            
            logger.info("会话存储库初始化成功")
        except Exception as e:
            logger.error("连接MongoDB失败: %s", str(e))
            # 在实际环境中可能需要更强的错误处理策略
            self.client = None
            self.db = None
            self.session_collection = None
    
    async def _create_indexes(self):
        """创建必要的索引"""
        if self.session_collection:
            try:
                # 为会话ID创建唯一索引
                await self.session_collection.create_index("session_id", unique=True)
                # 为用户ID创建索引，加快用户会话查询
                await self.session_collection.create_index("user_id")
                # 为最后活跃时间创建索引，用于会话清理
                await self.session_collection.create_index("last_active")
                
                logger.info("会话存储库索引创建成功")
            except Exception as e:
                logger.error("创建索引失败: %s", str(e))
    
    @track_db_metrics(db_type="mongodb", operation="query")
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取会话数据
        
        Args:
            session_id: 会话ID
            
        Returns:
            Optional[Dict[str, Any]]: 会话数据，如果不存在则返回None
        """
        if not self.session_collection:
            logger.error("MongoDB未连接，无法获取会话")
            return None
        
        try:
            # 查询会话
            doc = await self.session_collection.find_one({'session_id': session_id})
            
            if doc:
                # 转换ObjectId为字符串
                doc['_id'] = str(doc['_id'])
                logger.debug("找到会话，会话ID: %s", session_id)
                return doc
            
            logger.debug("未找到会话，会话ID: %s", session_id)
            return None
            
        except Exception as e:
            logger.error("获取会话失败，会话ID: %s, 错误: %s", session_id, str(e))
            return None
    
    @track_db_metrics(db_type="mongodb", operation="query")
    async def get_user_sessions(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取用户的所有会话
        
        Args:
            user_id: 用户ID
            limit: 返回结果数量限制
            
        Returns:
            List[Dict[str, Any]]: 会话数据列表
        """
        if not self.session_collection:
            logger.error("MongoDB未连接，无法获取用户会话")
            return []
        
        try:
            # 查询会话并排序
            cursor = self.session_collection.find({'user_id': user_id})
            cursor = cursor.sort('last_active', -1).limit(limit)
            
            results = []
            async for doc in cursor:
                # 转换ObjectId为字符串
                doc['_id'] = str(doc['_id'])
                results.append(doc)
            
            logger.info("获取用户会话成功，用户ID: %s, 会话数: %d", user_id, len(results))
            return results
            
        except Exception as e:
            logger.error("获取用户会话失败，用户ID: %s, 错误: %s", user_id, str(e))
            return []
    
    @track_db_metrics(db_type="mongodb", operation="insert_update")
    async def save_session(self, session_data: Dict[str, Any]) -> bool:
        """
        保存会话数据
        
        Args:
            session_data: 会话数据
            
        Returns:
            bool: 是否保存成功
        """
        if not self.session_collection:
            logger.error("MongoDB未连接，无法保存会话")
            return False
        
        try:
            session_id = session_data.get('session_id')
            if not session_id:
                logger.error("会话数据缺少session_id")
                return False
            
            # 更新最后活跃时间
            session_data['last_active'] = int(time.time())
            
            # 使用upsert以支持新增和更新
            result = await self.session_collection.update_one(
                {'session_id': session_id},
                {'$set': session_data},
                upsert=True
            )
            
            if result.modified_count > 0 or result.upserted_id is not None:
                logger.debug("会话保存成功，会话ID: %s", session_id)
                return True
            
            logger.warning("会话保存可能未生效，会话ID: %s", session_id)
            return False
            
        except Exception as e:
            logger.error("保存会话失败，错误: %s", str(e))
            return False
    
    @track_db_metrics(db_type="mongodb", operation="update")
    async def update_session_metadata(self, session_id: str, metadata: Dict[str, Any]) -> bool:
        """
        更新会话元数据
        
        Args:
            session_id: 会话ID
            metadata: 要更新的元数据
            
        Returns:
            bool: 是否更新成功
        """
        if not self.session_collection:
            logger.error("MongoDB未连接，无法更新会话元数据")
            return False
        
        try:
            # 更新元数据和最后活跃时间
            result = await self.session_collection.update_one(
                {'session_id': session_id},
                {
                    '$set': {
                        'metadata': metadata,
                        'last_active': int(time.time())
                    }
                }
            )
            
            if result.matched_count > 0:
                logger.debug("会话元数据更新成功，会话ID: %s", session_id)
                return True
            
            logger.warning("未找到要更新的会话，会话ID: %s", session_id)
            return False
            
        except Exception as e:
            logger.error("更新会话元数据失败，会话ID: %s, 错误: %s", session_id, str(e))
            return False
    
    @track_db_metrics(db_type="mongodb", operation="delete")
    async def delete_session(self, session_id: str) -> bool:
        """
        删除会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            bool: 是否删除成功
        """
        if not self.session_collection:
            logger.error("MongoDB未连接，无法删除会话")
            return False
        
        try:
            # 执行删除
            result = await self.session_collection.delete_one({'session_id': session_id})
            
            if result.deleted_count > 0:
                logger.info("会话删除成功，会话ID: %s", session_id)
                return True
            
            logger.warning("未找到要删除的会话，会话ID: %s", session_id)
            return False
            
        except Exception as e:
            logger.error("删除会话失败，会话ID: %s, 错误: %s", session_id, str(e))
            return False
    
    @track_db_metrics(db_type="mongodb", operation="delete")
    async def clean_inactive_sessions(self, max_age_seconds: int = None) -> int:
        """
        清理不活跃的会话
        
        Args:
            max_age_seconds: 会话最大不活跃时长(秒)，默认使用配置的超时时间
            
        Returns:
            int: 清理的会话数量
        """
        if not self.session_collection:
            logger.error("MongoDB未连接，无法清理会话")
            return 0
        
        try:
            # 使用配置的超时时间或指定的最大年龄
            max_age = max_age_seconds or self.session_timeout
            # 计算截止时间
            cutoff_time = int(time.time()) - max_age
            
            # 执行删除
            result = await self.session_collection.delete_many(
                {'last_active': {'$lt': cutoff_time}}
            )
            
            deleted_count = result.deleted_count
            logger.info("清理过期会话成功，删除会话数: %d", deleted_count)
            return deleted_count
            
        except Exception as e:
            logger.error("清理过期会话失败，错误: %s", str(e))
            return 0
    
    @track_db_metrics(db_type="mongodb", operation="count")
    async def count_active_sessions(self, max_age_seconds: int = None) -> int:
        """
        计算活跃会话数量
        
        Args:
            max_age_seconds: 会话最大不活跃时长(秒)，默认使用配置的超时时间
            
        Returns:
            int: 活跃会话数量
        """
        if not self.session_collection:
            logger.error("MongoDB未连接，无法计数活跃会话")
            return 0
        
        try:
            # 使用配置的超时时间或指定的最大年龄
            max_age = max_age_seconds or self.session_timeout
            # 计算截止时间
            cutoff_time = int(time.time()) - max_age
            
            # 执行计数
            count = await self.session_collection.count_documents(
                {'last_active': {'$gte': cutoff_time}}
            )
            
            return count
            
        except Exception as e:
            logger.error("计数活跃会话失败，错误: %s", str(e))
            return 0 