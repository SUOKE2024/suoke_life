import redis
from redis.connection import ConnectionPool
from functools import lru_cache
import pickle
from typing import Any, Optional
from loguru import logger
import os
import time
import random

class CacheManager:
    def __init__(self, redis_host=None, redis_port=None, redis_password=None):
        """初始化缓存管理器"""
        # 优先使用环境变量
        self.redis_host = redis_host or os.environ.get('REDIS_HOST', 'localhost')
        self.redis_port = redis_port or int(os.environ.get('REDIS_PORT', 6379))
        self.redis_password = redis_password or os.environ.get('REDIS_PASSWORD', None)
        self.cache_ttl = int(os.environ.get('CACHE_TTL', 3600))
        self.max_retries = int(os.environ.get('REDIS_MAX_RETRIES', 3))
        
        # 创建连接池
        self.pool = ConnectionPool(
            host=self.redis_host,
            port=self.redis_port,
            password=self.redis_password,
            db=0,
            decode_responses=False,  # 用于存储二进制数据
            socket_timeout=5.0,      # 超时设置
            socket_connect_timeout=5.0,
            max_connections=10,      # 连接池大小
            retry_on_timeout=True,   # 超时重试
            health_check_interval=30 # 连接健康检查间隔
        )
        
        # 创建Redis客户端
        self.redis_client = redis.Redis(connection_pool=self.pool)
        
        # 健康状态
        self._healthy = True
        
    @lru_cache(maxsize=1000)
    def get_memory_cache(self, key: str) -> Optional[Any]:
        """从内存缓存获取数据"""
        return None  # 由LRU装饰器处理
        
    def get_redis_cache(self, key: str) -> Optional[Any]:
        """从Redis缓存获取数据，包含重试逻辑"""
        if not self._healthy:
            logger.warning("Redis连接不健康，跳过缓存读取")
            return None
            
        retries = 0
        while retries < self.max_retries:
            try:
                data = self.redis_client.get(key)
                if data:
                    return pickle.loads(data)
                return None
            except (redis.RedisError, pickle.PickleError) as e:
                retries += 1
                if retries >= self.max_retries:
                    logger.error(f"Redis缓存读取失败（已重试{retries}次）: {e}")
                    self._healthy = False
                    return None
                
                # 指数退避策略
                sleep_time = (2 ** retries) * 0.1 + (random.random() * 0.1)
                logger.warning(f"Redis缓存读取重试 {retries}/{self.max_retries}, 等待 {sleep_time:.2f}s")
                time.sleep(sleep_time)
        
        return None
        
    def set_redis_cache(self, key: str, value: Any, expire: int = None) -> bool:
        """设置Redis缓存，带重试逻辑"""
        if not self._healthy:
            logger.warning("Redis连接不健康，跳过缓存写入")
            return False
            
        if expire is None:
            expire = self.cache_ttl
            
        retries = 0
        while retries < self.max_retries:
            try:
                data = pickle.dumps(value)
                return self.redis_client.setex(key, expire, data)
            except (redis.RedisError, pickle.PickleError) as e:
                retries += 1
                if retries >= self.max_retries:
                    logger.error(f"Redis缓存写入失败（已重试{retries}次）: {e}")
                    self._healthy = False
                    return False
                
                # 指数退避策略
                sleep_time = (2 ** retries) * 0.1 + (random.random() * 0.1)
                logger.warning(f"Redis缓存写入重试 {retries}/{self.max_retries}, 等待 {sleep_time:.2f}s")
                time.sleep(sleep_time)
        
        return False
            
    def get(self, key: str) -> Optional[Any]:
        """获取缓存数据（多级缓存）"""
        # 1. 检查内存缓存
        value = self.get_memory_cache(key)
        if value is not None:
            logger.debug(f"内存缓存命中: {key}")
            return value
            
        # 2. 检查Redis缓存
        value = self.get_redis_cache(key)
        if value is not None:
            logger.debug(f"Redis缓存命中: {key}")
            # 更新内存缓存
            self.get_memory_cache.cache_clear()  # 清除特定key的缓存
            return value
            
        logger.debug(f"缓存未命中: {key}")
        return None
        
    def set(self, key: str, value: Any, expire: int = None) -> bool:
        """设置缓存数据"""
        # 设置Redis缓存
        redis_success = self.set_redis_cache(key, value, expire)
        
        if redis_success:
            # 更新内存缓存
            self.get_memory_cache.cache_clear()  # 清除特定key的缓存
            
        return redis_success
        
    def delete(self, key: str) -> bool:
        """删除缓存数据"""
        try:
            # 清除内存缓存
            self.get_memory_cache.cache_clear()
            # 清除Redis缓存
            return bool(self.redis_client.delete(key))
        except redis.RedisError as e:
            logger.error(f"Redis缓存删除错误: {e}")
            return False
            
    def clear_all(self) -> bool:
        """清除所有缓存"""
        try:
            # 清除内存缓存
            self.get_memory_cache.cache_clear()
            # 清除Redis缓存
            return self.redis_client.flushdb()
        except redis.RedisError as e:
            logger.error(f"Redis缓存清空错误: {e}")
            return False
            
    def check_health(self) -> bool:
        """检查Redis连接健康状态"""
        try:
            # 简单的ping测试
            self.redis_client.ping()
            self._healthy = True
            return True
        except redis.RedisError as e:
            logger.error(f"Redis健康检查失败: {e}")
            self._healthy = False
            return False
            
    def get_stats(self) -> dict:
        """获取缓存统计信息"""
        stats = {
            "status": "healthy" if self._healthy else "unhealthy",
            "memory_cache_size": self.get_memory_cache.cache_info().currsize,
            "memory_cache_maxsize": self.get_memory_cache.cache_info().maxsize,
            "memory_cache_hits": self.get_memory_cache.cache_info().hits,
            "memory_cache_misses": self.get_memory_cache.cache_info().misses,
        }
        
        # 如果Redis健康，添加更多统计信息
        if self._healthy:
            try:
                info = self.redis_client.info()
                stats.update({
                    "redis_used_memory": info.get("used_memory_human", "N/A"),
                    "redis_connected_clients": info.get("connected_clients", 0),
                    "redis_evicted_keys": info.get("evicted_keys", 0),
                    "redis_hits": info.get("keyspace_hits", 0),
                    "redis_misses": info.get("keyspace_misses", 0),
                })
            except redis.RedisError:
                pass
                
        return stats

# 创建缓存管理器实例
cache_manager = CacheManager()

# 特定业务缓存装饰器
def cache_embedding(expire: int = 3600):
    """向量嵌入缓存装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"embedding:{args[0]}"  # 使用文本作为键
            
            # 尝试获取缓存
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value
                
            # 计算新值
            result = func(*args, **kwargs)
            
            # 设置缓存
            cache_manager.set(cache_key, result, expire)
            
            return result
        return wrapper
    return decorator

def cache_rag_result(expire: int = 300):  # 5分钟缓存
    """RAG结果缓存装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 生成缓存键
            query = args[0] if args else kwargs.get('query', '')
            cache_key = f"rag_result:{query}"
            
            # 尝试获取缓存
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value
                
            # 计算新值
            result = func(*args, **kwargs)
            
            # 设置缓存
            cache_manager.set(cache_key, result, expire)
            
            return result
        return wrapper
    return decorator 