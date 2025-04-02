#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Redis客户端
=========
提供Redis连接和操作功能
"""

import time
import json
from typing import Dict, Any, List, Optional, Union
import redis
from loguru import logger

from ..config import REDIS_URL, REDIS_TTL


class RedisClient:
    """Redis客户端类，提供缓存和队列功能"""

    def __init__(self, url: str = REDIS_URL, default_ttl: int = REDIS_TTL, max_retries: int = 3) -> None:
        """
        初始化Redis客户端
        
        Args:
            url: Redis连接URL
            default_ttl: 默认的缓存过期时间（秒）
            max_retries: 连接重试次数
        """
        self.url = url
        self.default_ttl = default_ttl
        self.max_retries = max_retries
        self.client = None
        self._connect()

    def _connect(self) -> None:
        """建立与Redis的连接"""
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                logger.info(f"正在连接Redis: {self.url}")
                self.client = redis.from_url(self.url)
                # 验证连接
                self.client.ping()
                logger.info(f"Redis连接成功: {self.url}")
                return
            except redis.RedisError as e:
                retry_count += 1
                wait_time = 2 ** retry_count  # 指数退避
                logger.error(f"Redis连接失败 (重试 {retry_count}/{self.max_retries}): {str(e)}")
                if retry_count < self.max_retries:
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    logger.critical(f"Redis连接失败，已达最大重试次数: {self.max_retries}")
                    raise

    def is_connected(self) -> bool:
        """检查Redis连接状态"""
        if not self.client:
            return False
        try:
            self.client.ping()
            return True
        except:
            return False

    def get_client(self) -> redis.Redis:
        """获取Redis客户端实例"""
        if not self.is_connected():
            self._connect()
        return self.client

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        设置键值对
        
        Args:
            key: 键名
            value: 值（将自动序列化为JSON）
            ttl: 过期时间（秒），如果为None则使用默认值
            
        Returns:
            bool: 操作是否成功
        """
        if not self.is_connected():
            self._connect()
            
        if ttl is None:
            ttl = self.default_ttl
            
        try:
            if isinstance(value, (dict, list, tuple, set)):
                value = json.dumps(value)
            return self.client.set(key, value, ex=ttl)
        except redis.RedisError as e:
            logger.error(f"Redis set错误: {str(e)}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取键值
        
        Args:
            key: 键名
            default: 如果键不存在，返回的默认值
            
        Returns:
            Any: 键对应的值，如果键不存在则返回默认值
        """
        if not self.is_connected():
            self._connect()
            
        try:
            value = self.client.get(key)
            if value is None:
                return default
                
            # 尝试反序列化为JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except redis.RedisError as e:
            logger.error(f"Redis get错误: {str(e)}")
            return default

    def delete(self, key: str) -> bool:
        """
        删除键
        
        Args:
            key: 键名
            
        Returns:
            bool: 操作是否成功
        """
        if not self.is_connected():
            self._connect()
            
        try:
            return bool(self.client.delete(key))
        except redis.RedisError as e:
            logger.error(f"Redis delete错误: {str(e)}")
            return False

    def exists(self, key: str) -> bool:
        """
        检查键是否存在
        
        Args:
            key: 键名
            
        Returns:
            bool: 键是否存在
        """
        if not self.is_connected():
            self._connect()
            
        try:
            return bool(self.client.exists(key))
        except redis.RedisError as e:
            logger.error(f"Redis exists错误: {str(e)}")
            return False

    def ttl(self, key: str) -> int:
        """
        获取键的剩余生存时间
        
        Args:
            key: 键名
            
        Returns:
            int: 剩余生存时间（秒），-1表示永久，-2表示键不存在
        """
        if not self.is_connected():
            self._connect()
            
        try:
            return self.client.ttl(key)
        except redis.RedisError as e:
            logger.error(f"Redis ttl错误: {str(e)}")
            return -2

    def expire(self, key: str, ttl: int) -> bool:
        """
        设置键的生存时间
        
        Args:
            key: 键名
            ttl: 生存时间（秒）
            
        Returns:
            bool: 操作是否成功
        """
        if not self.is_connected():
            self._connect()
            
        try:
            return bool(self.client.expire(key, ttl))
        except redis.RedisError as e:
            logger.error(f"Redis expire错误: {str(e)}")
            return False

    def incr(self, key: str, amount: int = 1) -> int:
        """
        增加键的值
        
        Args:
            key: 键名
            amount: 增加的数量
            
        Returns:
            int: 增加后的值
        """
        if not self.is_connected():
            self._connect()
            
        try:
            return self.client.incr(key, amount)
        except redis.RedisError as e:
            logger.error(f"Redis incr错误: {str(e)}")
            return 0

    def hset(self, name: str, key: str, value: Any) -> bool:
        """
        设置哈希表中的字段值
        
        Args:
            name: 哈希表名
            key: 字段名
            value: 字段值（将自动序列化为JSON）
            
        Returns:
            bool: 操作是否成功
        """
        if not self.is_connected():
            self._connect()
            
        try:
            if isinstance(value, (dict, list, tuple, set)):
                value = json.dumps(value)
            return bool(self.client.hset(name, key, value))
        except redis.RedisError as e:
            logger.error(f"Redis hset错误: {str(e)}")
            return False

    def hget(self, name: str, key: str, default: Any = None) -> Any:
        """
        获取哈希表中的字段值
        
        Args:
            name: 哈希表名
            key: 字段名
            default: 如果字段不存在，返回的默认值
            
        Returns:
            Any: 字段值，如果字段不存在则返回默认值
        """
        if not self.is_connected():
            self._connect()
            
        try:
            value = self.client.hget(name, key)
            if value is None:
                return default
                
            # 尝试反序列化为JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except redis.RedisError as e:
            logger.error(f"Redis hget错误: {str(e)}")
            return default

    def hgetall(self, name: str) -> Dict[str, Any]:
        """
        获取哈希表中的所有字段和值
        
        Args:
            name: 哈希表名
            
        Returns:
            Dict[str, Any]: 哈希表中的所有字段和值
        """
        if not self.is_connected():
            self._connect()
            
        try:
            result = {}
            raw_data = self.client.hgetall(name)
            
            for key, value in raw_data.items():
                # 将bytes键转换为字符串
                if isinstance(key, bytes):
                    key = key.decode('utf-8')
                
                # 尝试反序列化值为JSON
                if isinstance(value, bytes):
                    value = value.decode('utf-8')
                    
                try:
                    value = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    pass
                    
                result[key] = value
                
            return result
        except redis.RedisError as e:
            logger.error(f"Redis hgetall错误: {str(e)}")
            return {}

    def hdel(self, name: str, key: str) -> bool:
        """
        删除哈希表中的字段
        
        Args:
            name: 哈希表名
            key: 字段名
            
        Returns:
            bool: 操作是否成功
        """
        if not self.is_connected():
            self._connect()
            
        try:
            return bool(self.client.hdel(name, key))
        except redis.RedisError as e:
            logger.error(f"Redis hdel错误: {str(e)}")
            return False

    def lpush(self, name: str, *values: Any) -> int:
        """
        将值推入列表的左侧
        
        Args:
            name: 列表名
            values: 要推入的值（将自动序列化为JSON）
            
        Returns:
            int: 推入后列表的长度
        """
        if not self.is_connected():
            self._connect()
            
        try:
            serialized_values = []
            for value in values:
                if isinstance(value, (dict, list, tuple, set)):
                    serialized_values.append(json.dumps(value))
                else:
                    serialized_values.append(value)
                    
            return self.client.lpush(name, *serialized_values)
        except redis.RedisError as e:
            logger.error(f"Redis lpush错误: {str(e)}")
            return 0

    def rpop(self, name: str) -> Any:
        """
        弹出列表最右侧的值
        
        Args:
            name: 列表名
            
        Returns:
            Any: 弹出的值，如果列表为空则返回None
        """
        if not self.is_connected():
            self._connect()
            
        try:
            value = self.client.rpop(name)
            if value is None:
                return None
                
            # 如果是bytes，转换为字符串
            if isinstance(value, bytes):
                value = value.decode('utf-8')
                
            # 尝试反序列化为JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except redis.RedisError as e:
            logger.error(f"Redis rpop错误: {str(e)}")
            return None

    def lrange(self, name: str, start: int, end: int) -> List[Any]:
        """
        获取列表的一个范围内的元素
        
        Args:
            name: 列表名
            start: 开始索引
            end: 结束索引
            
        Returns:
            List[Any]: 范围内的元素列表
        """
        if not self.is_connected():
            self._connect()
            
        try:
            result = []
            raw_data = self.client.lrange(name, start, end)
            
            for value in raw_data:
                # 如果是bytes，转换为字符串
                if isinstance(value, bytes):
                    value = value.decode('utf-8')
                    
                # 尝试反序列化为JSON
                try:
                    value = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    pass
                    
                result.append(value)
                
            return result
        except redis.RedisError as e:
            logger.error(f"Redis lrange错误: {str(e)}")
            return []

    def publish(self, channel: str, message: Any) -> int:
        """
        发布消息到频道
        
        Args:
            channel: 频道名
            message: 消息内容（将自动序列化为JSON）
            
        Returns:
            int: 接收到消息的客户端数量
        """
        if not self.is_connected():
            self._connect()
            
        try:
            if isinstance(message, (dict, list, tuple, set)):
                message = json.dumps(message)
            return self.client.publish(channel, message)
        except redis.RedisError as e:
            logger.error(f"Redis publish错误: {str(e)}")
            return 0

    def flushdb(self) -> bool:
        """
        清空当前数据库
        
        Returns:
            bool: 操作是否成功
        """
        if not self.is_connected():
            self._connect()
            
        try:
            self.client.flushdb()
            return True
        except redis.RedisError as e:
            logger.error(f"Redis flushdb错误: {str(e)}")
            return False

    def close(self) -> None:
        """关闭Redis连接"""
        if self.client:
            self.client.close()
            self.client = None
            logger.info("Redis连接已关闭")

    def __del__(self) -> None:
        """析构函数，确保连接被关闭"""
        self.close() 