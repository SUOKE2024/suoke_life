#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
用户存储库
负责管理用户数据的存储与检索
"""

import logging
import time
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class UserRepository:
    """用户存储库，管理用户数据"""
    
    def __init__(self, db_config):
        """
        初始化用户存储库
        
        Args:
            db_config: 数据库配置
        """
        self.db_config = db_config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.db_client = self._init_db_client()
        self.db = self.db_client[db_config.get('name', 'palpation_db')]
        
        # 获取集合名
        collections = db_config.get('collections', {})
        self.users_collection = self.db[collections.get('users', 'users')]
        self.health_records_collection = self.db['health_records']
        
        # 创建索引
        self._create_indexes()
        
        logger.info("用户存储库初始化完成")
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        获取用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户信息，不存在时返回None
        """
        try:
            user = self.users_collection.find_one({'user_id': user_id})
            return user
        except Exception as e:
            logger.exception(f"获取用户信息失败: {str(e)}")
            return None
    
    def get_users(self, user_ids: List[str]) -> List[Dict[str, Any]]:
        """
        批量获取用户信息
        
        Args:
            user_ids: 用户ID列表
            
        Returns:
            用户信息列表
        """
        try:
            users = list(self.users_collection.find({'user_id': {'$in': user_ids}}))
            return users
        except Exception as e:
            logger.exception(f"批量获取用户信息失败: {str(e)}")
            return []
    
    def create_user(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """
        创建用户
        
        Args:
            user_id: 用户ID
            user_data: 用户数据
            
        Returns:
            创建是否成功
        """
        try:
            # 添加创建时间
            if 'created_at' not in user_data:
                user_data['created_at'] = time.time()
            
            # 确保用户ID一致
            user_data['user_id'] = user_id
            
            # 存储用户数据
            result = self.users_collection.insert_one(user_data)
            
            return result.acknowledged
        except Exception as e:
            logger.exception(f"创建用户失败: {str(e)}")
            return False
    
    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            user_data: 新的用户数据
            
        Returns:
            更新是否成功
        """
        try:
            # 添加更新时间
            user_data['updated_at'] = time.time()
            
            # 更新用户数据
            result = self.users_collection.update_one(
                {'user_id': user_id},
                {'$set': user_data}
            )
            
            return result.acknowledged
        except Exception as e:
            logger.exception(f"更新用户信息失败: {str(e)}")
            return False
    
    def delete_user(self, user_id: str) -> bool:
        """
        删除用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            删除是否成功
        """
        try:
            result = self.users_collection.delete_one({'user_id': user_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.exception(f"删除用户失败: {str(e)}")
            return False
    
    def get_health_record(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        获取用户健康记录
        
        Args:
            user_id: 用户ID
            
        Returns:
            健康记录，不存在时返回None
        """
        try:
            record = self.health_records_collection.find_one({'user_id': user_id})
            return record
        except Exception as e:
            logger.exception(f"获取用户健康记录失败: {str(e)}")
            return None
    
    def create_health_record(self, user_id: str, record_data: Dict[str, Any]) -> bool:
        """
        创建用户健康记录
        
        Args:
            user_id: 用户ID
            record_data: 健康记录数据
            
        Returns:
            创建是否成功
        """
        try:
            # 添加创建时间
            if 'created_at' not in record_data:
                record_data['created_at'] = time.time()
            
            # 确保用户ID一致
            record_data['user_id'] = user_id
            
            # 存储健康记录数据
            result = self.health_records_collection.insert_one(record_data)
            
            return result.acknowledged
        except Exception as e:
            logger.exception(f"创建用户健康记录失败: {str(e)}")
            return False
    
    def update_health_record(self, user_id: str, record_data: Dict[str, Any]) -> bool:
        """
        更新用户健康记录
        
        Args:
            user_id: 用户ID
            record_data: 新的健康记录数据
            
        Returns:
            更新是否成功
        """
        try:
            # 添加更新时间
            record_data['updated_at'] = time.time()
            
            # 更新健康记录数据
            result = self.health_records_collection.update_one(
                {'user_id': user_id},
                {'$set': record_data}
            )
            
            return result.acknowledged
        except Exception as e:
            logger.exception(f"更新用户健康记录失败: {str(e)}")
            return False
    
    def add_health_event(self, user_id: str, event_data: Dict[str, Any]) -> bool:
        """
        添加健康事件到用户健康记录
        
        Args:
            user_id: 用户ID
            event_data: 健康事件数据
            
        Returns:
            添加是否成功
        """
        try:
            # 添加事件时间
            if 'timestamp' not in event_data:
                event_data['timestamp'] = time.time()
            
            # 添加事件到健康记录
            result = self.health_records_collection.update_one(
                {'user_id': user_id},
                {'$push': {'health_events': event_data}}
            )
            
            return result.acknowledged
        except Exception as e:
            logger.exception(f"添加健康事件失败: {str(e)}")
            return False
    
    def get_health_events(self, user_id: str, event_type: Optional[str] = None, 
                          start_time: Optional[float] = None, end_time: Optional[float] = None,
                          limit: int = 10, skip: int = 0) -> List[Dict[str, Any]]:
        """
        获取用户健康事件
        
        Args:
            user_id: 用户ID
            event_type: 事件类型，为None时返回所有类型
            start_time: 开始时间戳，为None时不限制开始时间
            end_time: 结束时间戳，为None时不限制结束时间
            limit: 返回的最大事件数
            skip: 跳过的事件数
            
        Returns:
            健康事件列表
        """
        try:
            # 构建查询条件
            query = {'user_id': user_id}
            event_filter = {}
            
            if event_type:
                event_filter['event_type'] = event_type
                
            time_filter = {}
            if start_time:
                time_filter['$gte'] = start_time
            if end_time:
                time_filter['$lte'] = end_time
                
            if time_filter:
                event_filter['timestamp'] = time_filter
            
            # 构建聚合管道
            pipeline = [
                {'$match': query},
                {'$unwind': '$health_events'},
            ]
            
            if event_filter:
                pipeline.append({'$match': {'health_events.' + k: v for k, v in event_filter.items()}})
                
            pipeline.extend([
                {'$sort': {'health_events.timestamp': -1}},
                {'$skip': skip},
                {'$limit': limit},
                {'$project': {'_id': 0, 'event': '$health_events'}}
            ])
            
            # 执行聚合查询
            result = list(self.health_records_collection.aggregate(pipeline))
            
            # 提取事件数据
            events = [doc['event'] for doc in result]
            
            return events
        except Exception as e:
            logger.exception(f"获取用户健康事件失败: {str(e)}")
            return []
    
    def ping(self):
        """
        检查数据库连接状态
        
        Returns:
            bool: 如果数据库连接正常则返回True
            
        Raises:
            Exception: 如果数据库连接失败则抛出异常
        """
        try:
            # 执行简单的命令检查连接状态
            self.db.command('ping')
            return True
        except Exception as e:
            self.logger.error(f"数据库连接检查失败: {e}")
            raise 