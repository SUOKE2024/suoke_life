"""
cache - 索克生活项目模块
"""

import json
import logging
from typing import Any, Optional

import redis.asyncio as redis
from redis.asyncio import Redis
from user_service.config import get_settings

"""缓存管理"""



logger = logging.getLogger(__name__)

# 全局Redis连接
redis_client: Optional[Redis] = None


async def init_cache() -> None:
    """初始化缓存连接"""
    global redis_client

    settings = get_settings()

    try:
        # 创建Redis连接
        redis_client = redis.from_url(
            settings.redis.url,
            max_connections = settings.redis.max_connections,
            retry_on_timeout = True,
            socket_timeout = 5,
            decode_responses = True
        )

        # 测试连接
        await redis_client.ping()
        logger.info("缓存连接初始化成功")

    except Exception as e:
        logger.error(f"缓存连接初始化失败: {e}")
        raise


async def close_cache() -> None:
    """关闭缓存连接"""
    global redis_client

    if redis_client:
        try:
            await redis_client.close()
            logger.info("缓存连接已关闭")
        except Exception as e:
            logger.error(f"关闭缓存连接时出错: {e}")


def get_cache_client() -> Redis:
    """获取缓存客户端"""
    if not redis_client:
        raise RuntimeError("缓存未初始化")
    return redis_client


class CacheManager:
    """缓存管理器"""

    def __init__(self) -> None:
        """TODO: 添加文档字符串"""
        self.settings = get_settings()
        self.default_ttl = self.settings.cache.default_ttl

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            client = get_cache_client()
            value = await client.get(key)

            if value is None:
                return None

            # 尝试解析JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value

        except Exception as e:
            logger.error(f"获取缓存失败 {key}: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """设置缓存值"""
        try:
            client = get_cache_client()

            # 序列化值
            if isinstance(value, (dict, list, tuple)):
                serialized_value = json.dumps(value, ensure_ascii = False)
            else:
                serialized_value = str(value)

            # 设置TTL
            expire_time = ttl or self.default_ttl

            await client.setex(key, expire_time, serialized_value)
            return True

        except Exception as e:
            logger.error(f"设置缓存失败 {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            client = get_cache_client()
            result = await client.delete(key)
            return result > 0

        except Exception as e:
            logger.error(f"删除缓存失败 {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        try:
            client = get_cache_client()
            result = await client.exists(key)
            return result > 0

        except Exception as e:
            logger.error(f"检查缓存存在性失败 {key}: {e}")
            return False

    async def expire(self, key: str, ttl: int) -> bool:
        """设置缓存过期时间"""
        try:
            client = get_cache_client()
            result = await client.expire(key, ttl)
            return result

        except Exception as e:
            logger.error(f"设置缓存过期时间失败 {key}: {e}")
            return False

    async def ttl(self, key: str) -> int:
        """获取缓存剩余时间"""
        try:
            client = get_cache_client()
            return await client.ttl(key)

        except Exception as e:
            logger.error(f"获取缓存TTL失败 {key}: {e}")
            return - 1

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """递增缓存值"""
        try:
            client = get_cache_client()
            return await client.incrby(key, amount)

        except Exception as e:
            logger.error(f"递增缓存失败 {key}: {e}")
            return None

    async def decrement(self, key: str, amount: int = 1) -> Optional[int]:
        """递减缓存值"""
        try:
            client = get_cache_client()
            return await client.decrby(key, amount)

        except Exception as e:
            logger.error(f"递减缓存失败 {key}: {e}")
            return None

    async def get_many(self, keys: list[str]) -> dict[str, Any]:
        """批量获取缓存"""
        try:
            client = get_cache_client()
            values = await client.mget(keys)

            result = {}
            for key, value in zip(keys, values):
                if value is not None:
                    try:
                        result[key] = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        result[key] = value
                else:
                    result[key] = None

            return result

        except Exception as e:
            logger.error(f"批量获取缓存失败: {e}")
            return {}

    async def set_many(
        self,
        mapping: dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """批量设置缓存"""
        try:
            client = get_cache_client()

            # 序列化所有值
            serialized_mapping = {}
            for key, value in mapping.items():
                if isinstance(value, (dict, list, tuple)):
                    serialized_mapping[key] = json.dumps(value, ensure_ascii = False)
                else:
                    serialized_mapping[key] = str(value)

            # 批量设置
            await client.mset(serialized_mapping)

            # 设置过期时间
            if ttl:
                expire_time = ttl or self.default_ttl
                for key in mapping.keys():
                    await client.expire(key, expire_time)

            return True

        except Exception as e:
            logger.error(f"批量设置缓存失败: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """按模式删除缓存"""
        try:
            client = get_cache_client()
            keys = await client.keys(pattern)

            if keys:
                return await client.delete( * keys)
            return 0

        except Exception as e:
            logger.error(f"按模式删除缓存失败 {pattern}: {e}")
            return 0

    def get_user_cache_key(self, user_id: str, suffix: str = "") -> str:
        """生成用户缓存键"""
        if suffix:
            return f"user:{user_id}:{suffix}"
        return f"user:{user_id}"

    def get_session_cache_key(self, session_id: str) -> str:
        """生成会话缓存键"""
        return f"session:{session_id}"

    def get_device_cache_key(self, device_id: str) -> str:
        """生成设备缓存键"""
        return f"device:{device_id}"


# 全局缓存管理器实例
cache_manager = CacheManager()