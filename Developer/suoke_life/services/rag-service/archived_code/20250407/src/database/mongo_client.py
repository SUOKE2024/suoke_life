#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MongoDB客户端
===========
提供MongoDB连接和操作功能
"""

import time
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

import pymongo
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, OperationFailure
from loguru import logger

from ..config import MONGODB_URI, MONGODB_DB, MONGODB_COLLECTION


class MongoDBClient:
    """MongoDB客户端类，提供数据库连接和操作"""

    def __init__(self, uri: str = MONGODB_URI, db_name: str = MONGODB_DB, 
                 collection_name: str = MONGODB_COLLECTION, max_retries: int = 3) -> None:
        """
        初始化MongoDB客户端
        
        Args:
            uri: MongoDB连接URI
            db_name: 数据库名称
            collection_name: 集合名称
            max_retries: 连接重试次数
        """
        self.uri = uri
        self.db_name = db_name
        self.collection_name = collection_name
        self.max_retries = max_retries
        self.client = None
        self.db = None
        self.collection = None
        self._connect()

    def _connect(self) -> None:
        """建立与MongoDB的连接"""
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                logger.info(f"正在连接MongoDB: {self.uri}")
                self.client = pymongo.MongoClient(self.uri)
                # 验证连接
                self.client.admin.command('ping')
                self.db = self.client[self.db_name]
                self.collection = self.db[self.collection_name]
                logger.info(f"MongoDB连接成功: {self.uri}, 数据库: {self.db_name}, 集合: {self.collection_name}")
                return
            except (ConnectionFailure, OperationFailure) as e:
                retry_count += 1
                wait_time = 2 ** retry_count  # 指数退避
                logger.error(f"MongoDB连接失败 (重试 {retry_count}/{self.max_retries}): {str(e)}")
                if retry_count < self.max_retries:
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    logger.critical(f"MongoDB连接失败，已达最大重试次数: {self.max_retries}")
                    raise

    def is_connected(self) -> bool:
        """检查MongoDB连接状态"""
        if not self.client:
            return False
        try:
            self.client.admin.command('ping')
            return True
        except:
            return False

    def get_db(self) -> Database:
        """获取数据库对象"""
        if not self.is_connected():
            self._connect()
        return self.db

    def get_collection(self, collection_name: Optional[str] = None) -> Collection:
        """
        获取集合对象
        
        Args:
            collection_name: 可选的集合名称，如果未提供则使用默认集合
            
        Returns:
            pymongo.collection.Collection: MongoDB集合对象
        """
        if not self.is_connected():
            self._connect()
        
        if collection_name:
            return self.db[collection_name]
        return self.collection

    def create_index(self, keys: Union[str, List[tuple]], unique: bool = False) -> str:
        """
        创建索引
        
        Args:
            keys: 索引字段，可以是单个字符串或字段元组列表
            unique: 是否是唯一索引
            
        Returns:
            str: 创建的索引名称
        """
        if not self.is_connected():
            self._connect()
        return self.collection.create_index(keys, unique=unique)

    def insert_one(self, document: Dict[str, Any]) -> str:
        """
        插入单个文档
        
        Args:
            document: 要插入的文档
            
        Returns:
            str: 插入的文档ID
        """
        if not self.is_connected():
            self._connect()
            
        # 添加时间戳
        if 'created_at' not in document:
            document['created_at'] = datetime.now()
        if 'updated_at' not in document:
            document['updated_at'] = document['created_at']
            
        result = self.collection.insert_one(document)
        return str(result.inserted_id)

    def insert_many(self, documents: List[Dict[str, Any]]) -> List[str]:
        """
        插入多个文档
        
        Args:
            documents: 要插入的文档列表
            
        Returns:
            List[str]: 插入的文档ID列表
        """
        if not self.is_connected():
            self._connect()
            
        # 添加时间戳
        now = datetime.now()
        for doc in documents:
            if 'created_at' not in doc:
                doc['created_at'] = now
            if 'updated_at' not in doc:
                doc['updated_at'] = doc['created_at']
                
        result = self.collection.insert_many(documents)
        return [str(id) for id in result.inserted_ids]

    def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        查找单个文档
        
        Args:
            query: 查询条件
            
        Returns:
            Optional[Dict[str, Any]]: 查询结果，如果没有找到则返回None
        """
        if not self.is_connected():
            self._connect()
        return self.collection.find_one(query)

    def find(self, query: Dict[str, Any], limit: int = 0, sort: List[tuple] = None) -> List[Dict[str, Any]]:
        """
        查找多个文档
        
        Args:
            query: 查询条件
            limit: 返回结果的最大数量，0表示不限制
            sort: 排序字段和方向的元组列表
            
        Returns:
            List[Dict[str, Any]]: 查询结果列表
        """
        if not self.is_connected():
            self._connect()
            
        cursor = self.collection.find(query)
        
        if sort:
            cursor = cursor.sort(sort)
        
        if limit > 0:
            cursor = cursor.limit(limit)
            
        return list(cursor)

    def update_one(self, query: Dict[str, Any], update: Dict[str, Any], upsert: bool = False) -> int:
        """
        更新单个文档
        
        Args:
            query: 查询条件
            update: 更新操作
            upsert: 如果为True，当没有找到匹配文档时创建新文档
            
        Returns:
            int: 更新的文档数量
        """
        if not self.is_connected():
            self._connect()
            
        # 如果不是原子操作，则自动添加更新时间
        if '$set' in update:
            update['$set']['updated_at'] = datetime.now()
        else:
            update['$set'] = {'updated_at': datetime.now()}
            
        result = self.collection.update_one(query, update, upsert=upsert)
        return result.modified_count

    def update_many(self, query: Dict[str, Any], update: Dict[str, Any]) -> int:
        """
        更新多个文档
        
        Args:
            query: 查询条件
            update: 更新操作
            
        Returns:
            int: 更新的文档数量
        """
        if not self.is_connected():
            self._connect()
            
        # 添加更新时间
        if '$set' in update:
            update['$set']['updated_at'] = datetime.now()
        else:
            update['$set'] = {'updated_at': datetime.now()}
            
        result = self.collection.update_many(query, update)
        return result.modified_count

    def delete_one(self, query: Dict[str, Any]) -> int:
        """
        删除单个文档
        
        Args:
            query: 查询条件
            
        Returns:
            int: 删除的文档数量
        """
        if not self.is_connected():
            self._connect()
        result = self.collection.delete_one(query)
        return result.deleted_count

    def delete_many(self, query: Dict[str, Any]) -> int:
        """
        删除多个文档
        
        Args:
            query: 查询条件
            
        Returns:
            int: 删除的文档数量
        """
        if not self.is_connected():
            self._connect()
        result = self.collection.delete_many(query)
        return result.deleted_count

    def count(self, query: Dict[str, Any]) -> int:
        """
        计算匹配文档的数量
        
        Args:
            query: 查询条件
            
        Returns:
            int: 匹配的文档数量
        """
        if not self.is_connected():
            self._connect()
        return self.collection.count_documents(query)

    def close(self) -> None:
        """关闭MongoDB连接"""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            self.collection = None
            logger.info("MongoDB连接已关闭")

    def __del__(self) -> None:
        """析构函数，确保连接被关闭"""
        self.close() 