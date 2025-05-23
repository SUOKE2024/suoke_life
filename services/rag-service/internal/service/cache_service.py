"""
缓存服务模块，实现多级缓存策略
"""
import time
import pickle
import hashlib
import asyncio
from typing import Any, Dict, Optional, List, Tuple, Union
from functools import lru_cache
import redis
from loguru import logger

from ..model.document import Document


class LocalCache:
    """本地内存缓存实现"""
    
    def __init__(self, max_size: int = 10000, ttl: int = 3600):
        """
        初始化本地缓存
        
        Args:
            max_size: 最大缓存项数
            ttl: 过期时间（秒）
        """
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl
        self.access_times = {}
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存项
        
        Args:
            key: 缓存键
            
        Returns:
            缓存的值，不存在或过期返回None
        """
        if key not in self.cache:
            return None
        
        value, timestamp = self.cache[key]
        
        # 检查是否过期
        if time.time() - timestamp > self.ttl:
            # 删除过期项
            del self.cache[key]
            del self.access_times[key]
            return None
        
        # 更新访问时间
        self.access_times[key] = time.time()
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        设置缓存项
        
        Args:
            key: 缓存键
            value: 缓存值
        """
        # 检查是否需要清理
        if len(self.cache) >= self.max_size:
            self._evict()
        
        # 存储值和时间戳
        self.cache[key] = (value, time.time())
        self.access_times[key] = time.time()
    
    def _evict(self) -> None:
        """清理最老的缓存项"""
        if not self.cache:
            return
        
        # 查找最老的访问项
        oldest_key = min(self.access_times.items(), key=lambda x: x[1])[0]
        
        # 删除它
        del self.cache[oldest_key]
        del self.access_times[oldest_key]
    
    def clear(self) -> None:
        """清空缓存"""
        self.cache.clear()
        self.access_times.clear()


class RedisCache:
    """Redis缓存实现"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化Redis缓存
        
        Args:
            config: Redis配置
        """
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 6379)
        self.db = config.get("db", 0)
        self.password = config.get("password", None)
        self.ttl = config.get("ttl", 3600)
        self.client = None
        self.prefix = "suoke:rag:"
    
    async def initialize(self) -> None:
        """初始化Redis连接"""
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=False  # 不自动解码，因为我们使用pickle
            )
            # 测试连接
            self.client.ping()
            logger.info(f"Connected to Redis at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            self.client = None
            raise
    
    async def get(self, key: str) -> Optional[Any]:
        """
        获取缓存项
        
        Args:
            key: 缓存键
            
        Returns:
            缓存的值，不存在返回None
        """
        if self.client is None:
            return None
        
        try:
            # 构建键
            cache_key = f"{self.prefix}{key}"
            
            # 获取值
            value = self.client.get(cache_key)
            
            if value is None:
                return None
            
            # 反序列化
            return pickle.loads(value)
        except Exception as e:
            logger.error(f"Error getting value from Redis: {str(e)}")
            return None
    
    async def set(self, key: str, value: Any) -> None:
        """
        设置缓存项
        
        Args:
            key: 缓存键
            value: 缓存值
        """
        if self.client is None:
            return
        
        try:
            # 构建键
            cache_key = f"{self.prefix}{key}"
            
            # 序列化值
            serialized = pickle.dumps(value)
            
            # 存储带过期时间的值
            self.client.setex(cache_key, self.ttl, serialized)
        except Exception as e:
            logger.error(f"Error setting value in Redis: {str(e)}")
    
    async def close(self) -> None:
        """关闭Redis连接"""
        if self.client:
            self.client.close()
            self.client = None


class CacheService:
    """
    多级缓存服务，支持本地缓存和Redis缓存
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化缓存服务
        
        Args:
            config: 缓存配置
        """
        self.config = config
        self.caches = {}
        self.enabled = config.get("enabled", True)
        
        # 缓存类型
        self.query_cache = None
        self.embedding_cache = None
        self.retrieval_cache = None
        self.generation_cache = None
    
    async def initialize(self) -> None:
        """初始化所有缓存"""
        if not self.enabled:
            logger.info("Cache service is disabled")
            return
        
        logger.info("Initializing cache service")
        
        # 初始化查询缓存
        if self.config.get("query", {}).get("enabled", True):
            cache_config = self.config["query"]
            cache_type = cache_config.get("type", "local")
            
            if cache_type == "redis":
                redis_config = self.config.get("storage", {}).get("redis", {})
                self.query_cache = RedisCache(redis_config)
                await self.query_cache.initialize()
            else:
                self.query_cache = LocalCache(
                    max_size=cache_config.get("max_size", 10000),
                    ttl=cache_config.get("ttl", 3600)
                )
            
            logger.info(f"Query cache initialized ({cache_type})")
        
        # 初始化嵌入缓存
        if self.config.get("embedding", {}).get("enabled", True):
            cache_config = self.config["embedding"]
            cache_type = cache_config.get("type", "local")
            
            if cache_type == "redis":
                redis_config = self.config.get("storage", {}).get("redis", {})
                self.embedding_cache = RedisCache(redis_config)
                await self.embedding_cache.initialize()
            else:
                self.embedding_cache = LocalCache(
                    max_size=cache_config.get("max_size", 100000),
                    ttl=cache_config.get("ttl", 86400)
                )
            
            logger.info(f"Embedding cache initialized ({cache_type})")
        
        # 初始化检索缓存
        if self.config.get("retrieval", {}).get("enabled", True):
            cache_config = self.config["retrieval"]
            cache_type = cache_config.get("type", "redis")
            
            if cache_type == "redis":
                redis_config = self.config.get("storage", {}).get("redis", {})
                self.retrieval_cache = RedisCache(redis_config)
                await self.retrieval_cache.initialize()
            else:
                self.retrieval_cache = LocalCache(
                    max_size=cache_config.get("max_size", 10000),
                    ttl=cache_config.get("ttl", 1800)
                )
            
            logger.info(f"Retrieval cache initialized ({cache_type})")
        
        # 初始化生成缓存
        if self.config.get("generation", {}).get("enabled", True):
            cache_config = self.config["generation"]
            cache_type = cache_config.get("type", "redis")
            
            if cache_type == "redis":
                redis_config = self.config.get("storage", {}).get("redis", {})
                self.generation_cache = RedisCache(redis_config)
                await self.generation_cache.initialize()
            else:
                self.generation_cache = LocalCache(
                    max_size=cache_config.get("max_size", 10000),
                    ttl=cache_config.get("ttl", 1800)
                )
            
            logger.info(f"Generation cache initialized ({cache_type})")
    
    def _get_cache_for_type(self, cache_type: str) -> Optional[Union[LocalCache, RedisCache]]:
        """
        根据缓存类型获取对应的缓存对象
        
        Args:
            cache_type: 缓存类型
            
        Returns:
            缓存对象
        """
        if cache_type == "query":
            return self.query_cache
        elif cache_type == "embedding":
            return self.embedding_cache
        elif cache_type == "retrieval":
            return self.retrieval_cache
        elif cache_type == "generation":
            return self.generation_cache
        else:
            return None
    
    def _compute_key(self, data: Any) -> str:
        """
        计算缓存键
        
        Args:
            data: 用于计算键的数据
            
        Returns:
            缓存键
        """
        if isinstance(data, str):
            # 对于字符串，直接哈希
            key = hashlib.md5(data.encode('utf-8')).hexdigest()
        elif isinstance(data, (list, tuple)) and all(isinstance(x, (str, int, float, bool)) for x in data):
            # 对于简单类型的列表/元组，序列化后哈希
            key = hashlib.md5(pickle.dumps(data)).hexdigest()
        else:
            # 对于复杂类型，尝试序列化后哈希
            try:
                key = hashlib.md5(pickle.dumps(data)).hexdigest()
            except:
                # 如果无法序列化，使用对象ID和时间戳
                key = f"{id(data)}_{time.time()}"
        
        return key
    
    async def get(self, cache_type: str, key_data: Any) -> Optional[Any]:
        """
        从缓存获取值
        
        Args:
            cache_type: 缓存类型
            key_data: 用于生成键的数据
            
        Returns:
            缓存的值，不存在返回None
        """
        if not self.enabled:
            return None
        
        cache = self._get_cache_for_type(cache_type)
        if cache is None:
            return None
        
        # 计算键
        key = self._compute_key(key_data)
        
        # 获取值
        if isinstance(cache, RedisCache):
            return await cache.get(key)
        else:
            return cache.get(key)
    
    async def set(self, cache_type: str, key_data: Any, value: Any) -> None:
        """
        设置缓存值
        
        Args:
            cache_type: 缓存类型
            key_data: 用于生成键的数据
            value: 要缓存的值
        """
        if not self.enabled:
            return
        
        cache = self._get_cache_for_type(cache_type)
        if cache is None:
            return
        
        # 计算键
        key = self._compute_key(key_data)
        
        # 设置值
        if isinstance(cache, RedisCache):
            await cache.set(key, value)
        else:
            cache.set(key, value)
    
    async def close(self) -> None:
        """关闭所有缓存连接"""
        if self.query_cache and isinstance(self.query_cache, RedisCache):
            await self.query_cache.close()
        
        if self.embedding_cache and isinstance(self.embedding_cache, RedisCache):
            await self.embedding_cache.close()
        
        if self.retrieval_cache and isinstance(self.retrieval_cache, RedisCache):
            await self.retrieval_cache.close()
        
        if self.generation_cache and isinstance(self.generation_cache, RedisCache):
            await self.generation_cache.close() 