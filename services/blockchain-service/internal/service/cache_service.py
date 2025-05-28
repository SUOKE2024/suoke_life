#!/usr/bin/env python3

"""
缓存服务模块

该模块提供Redis缓存功能，用于缓存常用的区块链查询结果，提高系统性能。
"""

from datetime import datetime
import hashlib
import logging
import pickle
import time
from typing import Any

import redis

from internal.model.config import AppConfig


class CacheService:
    """Redis缓存服务类"""

    def __init__(self, config: AppConfig):
        """
        初始化缓存服务
        
        Args:
            config: 应用配置对象
        """
        self.logger = logging.getLogger(__name__)
        self.config = config

        # 初始化Redis连接
        self._init_redis()

        # 缓存键前缀
        self.key_prefix = "blockchain_service"

        # 默认TTL设置
        self.default_ttl = config.cache.ttl_seconds

        # 缓存统计
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }

        self.logger.info("缓存服务初始化完成")

    def _init_redis(self):
        """初始化Redis连接"""
        try:
            cache_config = self.config.cache

            # 创建Redis连接池
            self.redis_pool = redis.ConnectionPool(
                host=cache_config.host,
                port=cache_config.port,
                db=cache_config.db,
                password=cache_config.password,
                max_connections=20,
                retry_on_timeout=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )

            # 创建Redis客户端
            self.redis_client = redis.Redis(connection_pool=self.redis_pool)

            # 测试连接
            self.redis_client.ping()

            self.logger.info(f"Redis连接初始化成功: {cache_config.host}:{cache_config.port}")
        except Exception as e:
            self.logger.error(f"Redis连接初始化失败: {e!s}")
            # 创建一个空的缓存客户端，禁用缓存功能
            self.redis_client = None

    def _generate_cache_key(self, key_type: str, identifier: str, **kwargs) -> str:
        """
        生成缓存键
        
        Args:
            key_type: 键类型
            identifier: 标识符
            **kwargs: 额外参数
            
        Returns:
            缓存键
        """
        # 创建参数字符串
        params_str = ""
        if kwargs:
            sorted_params = sorted(kwargs.items())
            params_str = "_" + "_".join([f"{k}:{v}" for k, v in sorted_params])

        # 生成缓存键
        cache_key = f"{self.key_prefix}:{key_type}:{identifier}{params_str}"

        # 如果键太长，使用哈希
        if len(cache_key) > 250:
            hash_suffix = hashlib.md5(cache_key.encode()).hexdigest()[:8]
            cache_key = f"{self.key_prefix}:{key_type}:{hash_suffix}"

        return cache_key

    def get(self, key_type: str, identifier: str, **kwargs) -> Any | None:
        """
        从缓存获取数据
        
        Args:
            key_type: 键类型
            identifier: 标识符
            **kwargs: 额外参数
            
        Returns:
            缓存的数据，如果不存在则返回None
        """
        if not self.redis_client:
            return None

        try:
            cache_key = self._generate_cache_key(key_type, identifier, **kwargs)

            # 从Redis获取数据
            cached_data = self.redis_client.get(cache_key)

            if cached_data:
                self.cache_stats["hits"] += 1
                # 反序列化数据
                return pickle.loads(cached_data)
            else:
                self.cache_stats["misses"] += 1
                return None

        except Exception as e:
            self.logger.warning(f"缓存获取失败: {e!s}")
            self.cache_stats["misses"] += 1
            return None

    def set(
        self,
        key_type: str,
        identifier: str,
        data: Any,
        ttl: int | None = None,
        **kwargs
    ) -> bool:
        """
        设置缓存数据
        
        Args:
            key_type: 键类型
            identifier: 标识符
            data: 要缓存的数据
            ttl: 过期时间（秒），如果为None则使用默认TTL
            **kwargs: 额外参数
            
        Returns:
            是否设置成功
        """
        if not self.redis_client:
            return False

        try:
            cache_key = self._generate_cache_key(key_type, identifier, **kwargs)

            # 序列化数据
            serialized_data = pickle.dumps(data)

            # 设置TTL
            if ttl is None:
                ttl = self.default_ttl

            # 存储到Redis
            result = self.redis_client.setex(cache_key, ttl, serialized_data)

            if result:
                self.cache_stats["sets"] += 1
                return True
            else:
                return False

        except Exception as e:
            self.logger.warning(f"缓存设置失败: {e!s}")
            return False

    def delete(self, key_type: str, identifier: str, **kwargs) -> bool:
        """
        删除缓存数据
        
        Args:
            key_type: 键类型
            identifier: 标识符
            **kwargs: 额外参数
            
        Returns:
            是否删除成功
        """
        if not self.redis_client:
            return False

        try:
            cache_key = self._generate_cache_key(key_type, identifier, **kwargs)

            result = self.redis_client.delete(cache_key)

            if result:
                self.cache_stats["deletes"] += 1
                return True
            else:
                return False

        except Exception as e:
            self.logger.warning(f"缓存删除失败: {e!s}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """
        根据模式删除缓存键
        
        Args:
            pattern: 键模式
            
        Returns:
            删除的键数量
        """
        if not self.redis_client:
            return 0

        try:
            # 查找匹配的键
            keys = self.redis_client.keys(f"{self.key_prefix}:{pattern}")

            if keys:
                # 批量删除
                deleted_count = self.redis_client.delete(*keys)
                self.cache_stats["deletes"] += deleted_count
                return deleted_count
            else:
                return 0

        except Exception as e:
            self.logger.warning(f"批量删除缓存失败: {e!s}")
            return 0

    def exists(self, key_type: str, identifier: str, **kwargs) -> bool:
        """
        检查缓存键是否存在
        
        Args:
            key_type: 键类型
            identifier: 标识符
            **kwargs: 额外参数
            
        Returns:
            是否存在
        """
        if not self.redis_client:
            return False

        try:
            cache_key = self._generate_cache_key(key_type, identifier, **kwargs)
            return bool(self.redis_client.exists(cache_key))
        except Exception as e:
            self.logger.warning(f"缓存存在性检查失败: {e!s}")
            return False

    def get_ttl(self, key_type: str, identifier: str, **kwargs) -> int:
        """
        获取缓存键的剩余TTL
        
        Args:
            key_type: 键类型
            identifier: 标识符
            **kwargs: 额外参数
            
        Returns:
            剩余TTL（秒），-1表示永不过期，-2表示键不存在
        """
        if not self.redis_client:
            return -2

        try:
            cache_key = self._generate_cache_key(key_type, identifier, **kwargs)
            return self.redis_client.ttl(cache_key)
        except Exception as e:
            self.logger.warning(f"获取TTL失败: {e!s}")
            return -2

    def increment(self, key_type: str, identifier: str, amount: int = 1, **kwargs) -> int | None:
        """
        递增缓存值
        
        Args:
            key_type: 键类型
            identifier: 标识符
            amount: 递增量
            **kwargs: 额外参数
            
        Returns:
            递增后的值
        """
        if not self.redis_client:
            return None

        try:
            cache_key = self._generate_cache_key(key_type, identifier, **kwargs)
            return self.redis_client.incrby(cache_key, amount)
        except Exception as e:
            self.logger.warning(f"缓存递增失败: {e!s}")
            return None

    def get_stats(self) -> dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            缓存统计信息
        """
        stats = self.cache_stats.copy()

        # 计算命中率
        total_requests = stats["hits"] + stats["misses"]
        if total_requests > 0:
            stats["hit_rate"] = stats["hits"] / total_requests
        else:
            stats["hit_rate"] = 0.0

        # 添加Redis信息
        if self.redis_client:
            try:
                redis_info = self.redis_client.info()
                stats["redis_info"] = {
                    "connected_clients": redis_info.get("connected_clients", 0),
                    "used_memory": redis_info.get("used_memory", 0),
                    "used_memory_human": redis_info.get("used_memory_human", "0B"),
                    "keyspace_hits": redis_info.get("keyspace_hits", 0),
                    "keyspace_misses": redis_info.get("keyspace_misses", 0)
                }
            except Exception as e:
                self.logger.warning(f"获取Redis信息失败: {e!s}")
                stats["redis_info"] = {}
        else:
            stats["redis_info"] = {"status": "disabled"}

        return stats

    def clear_all(self) -> bool:
        """
        清空所有缓存
        
        Returns:
            是否清空成功
        """
        if not self.redis_client:
            return False

        try:
            # 删除所有以前缀开头的键
            keys = self.redis_client.keys(f"{self.key_prefix}:*")
            if keys:
                deleted_count = self.redis_client.delete(*keys)
                self.cache_stats["deletes"] += deleted_count
                self.logger.info(f"清空缓存完成，删除了 {deleted_count} 个键")
                return True
            else:
                self.logger.info("没有找到需要清空的缓存键")
                return True
        except Exception as e:
            self.logger.error(f"清空缓存失败: {e!s}")
            return False

    def health_check(self) -> dict[str, Any]:
        """
        健康检查
        
        Returns:
            健康检查结果
        """
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "redis_connected": False,
            "error": None
        }

        if not self.redis_client:
            health_status["status"] = "disabled"
            health_status["error"] = "Redis client not initialized"
            return health_status

        try:
            # 测试Redis连接
            response = self.redis_client.ping()
            if response:
                health_status["redis_connected"] = True

                # 测试基本操作
                test_key = f"{self.key_prefix}:health_check"
                test_value = f"test_{int(time.time())}"

                # 设置测试值
                self.redis_client.setex(test_key, 10, test_value)

                # 获取测试值
                retrieved_value = self.redis_client.get(test_key)

                if retrieved_value and retrieved_value.decode() == test_value:
                    health_status["status"] = "healthy"
                    # 清理测试键
                    self.redis_client.delete(test_key)
                else:
                    health_status["status"] = "unhealthy"
                    health_status["error"] = "Redis read/write test failed"
            else:
                health_status["status"] = "unhealthy"
                health_status["error"] = "Redis ping failed"

        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)

        return health_status


# 缓存键类型常量
class CacheKeyTypes:
    """缓存键类型常量"""

    HEALTH_DATA_RECORD = "health_data_record"
    USER_TRANSACTIONS = "user_transactions"
    VERIFICATION_RESULT = "verification_result"
    BLOCKCHAIN_STATUS = "blockchain_status"
    CONTRACT_CALL_RESULT = "contract_call_result"
    TRANSACTION_STATUS = "transaction_status"
    ZKP_VERIFICATION = "zkp_verification"
    ACCESS_AUTHORIZATION = "access_authorization"
    BATCH_OPERATION_RESULT = "batch_operation_result"
    GAS_ESTIMATION = "gas_estimation"


# 缓存装饰器
def cached(key_type: str, ttl: int | None = None, use_kwargs: bool = True):
    """
    缓存装饰器
    
    Args:
        key_type: 缓存键类型
        ttl: 过期时间（秒）
        use_kwargs: 是否使用函数参数作为缓存键的一部分
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            # 检查是否有缓存服务
            if not hasattr(self, "cache_service") or not self.cache_service:
                return func(self, *args, **kwargs)

            # 生成缓存标识符
            if args:
                identifier = str(args[0])  # 使用第一个参数作为标识符
            else:
                identifier = "default"

            # 生成缓存键参数
            cache_kwargs = {}
            if use_kwargs:
                cache_kwargs.update(kwargs)

            # 尝试从缓存获取
            cached_result = self.cache_service.get(key_type, identifier, **cache_kwargs)
            if cached_result is not None:
                return cached_result

            # 执行函数
            result = func(self, *args, **kwargs)

            # 缓存结果
            self.cache_service.set(key_type, identifier, result, ttl, **cache_kwargs)

            return result

        return wrapper
    return decorator
