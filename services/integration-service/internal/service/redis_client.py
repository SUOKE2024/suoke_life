"""
Redis Client Service
"""

import json
import logging
from typing import Any, Optional, Dict, List
import aioredis
from aioredis import Redis

from .config import get_settings

logger = logging.getLogger(__name__)

# 全局Redis客户端
redis_client: Optional[Redis] = None


async def init_redis():
    """初始化Redis连接"""
    global redis_client
    
    settings = get_settings()
    
    # 构建Redis URL
    redis_url = f"redis://"
    if settings.redis.password:
        redis_url += f":{settings.redis.password}@"
    redis_url += f"{settings.redis.host}:{settings.redis.port}/{settings.redis.db}"
    
    # 创建Redis连接
    redis_client = aioredis.from_url(
        redis_url,
        max_connections=settings.redis.max_connections,
        socket_timeout=settings.redis.socket_timeout,
        socket_connect_timeout=settings.redis.socket_connect_timeout,
        decode_responses=True
    )
    
    # 测试连接
    await redis_client.ping()
    logger.info("Redis连接初始化完成")


async def close_redis():
    """关闭Redis连接"""
    global redis_client
    
    if redis_client:
        await redis_client.close()
        logger.info("Redis连接已关闭")


class RedisService:
    """Redis服务类"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.settings = get_settings()
    
    async def get_client(self) -> Redis:
        """获取Redis客户端"""
        if not redis_client:
            raise RuntimeError("Redis未初始化")
        return redis_client
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置键值"""
        try:
            client = await self.get_client()
            
            # 序列化值
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            elif not isinstance(value, str):
                value = str(value)
            
            # 设置TTL
            if ttl is None:
                ttl = self.settings.cache.default_ttl
            
            await client.setex(key, ttl, value)
            return True
        except Exception as e:
            self.logger.error(f"Redis设置失败 {key}: {str(e)}")
            return False
    
    async def get(self, key: str, default: Any = None) -> Any:
        """获取键值"""
        try:
            client = await self.get_client()
            value = await client.get(key)
            
            if value is None:
                return default
            
            # 尝试反序列化JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
                
        except Exception as e:
            self.logger.error(f"Redis获取失败 {key}: {str(e)}")
            return default
    
    async def delete(self, key: str) -> bool:
        """删除键"""
        try:
            client = await self.get_client()
            result = await client.delete(key)
            return result > 0
        except Exception as e:
            self.logger.error(f"Redis删除失败 {key}: {str(e)}")
            return False
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            client = await self.get_client()
            result = await client.exists(key)
            return result > 0
        except Exception as e:
            self.logger.error(f"Redis检查存在失败 {key}: {str(e)}")
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """设置键过期时间"""
        try:
            client = await self.get_client()
            result = await client.expire(key, ttl)
            return result
        except Exception as e:
            self.logger.error(f"Redis设置过期时间失败 {key}: {str(e)}")
            return False
    
    async def ttl(self, key: str) -> int:
        """获取键剩余过期时间"""
        try:
            client = await self.get_client()
            return await client.ttl(key)
        except Exception as e:
            self.logger.error(f"Redis获取TTL失败 {key}: {str(e)}")
            return -1
    
    async def hset(self, name: str, mapping: Dict[str, Any]) -> bool:
        """设置哈希表"""
        try:
            client = await self.get_client()
            
            # 序列化值
            serialized_mapping = {}
            for k, v in mapping.items():
                if isinstance(v, (dict, list)):
                    serialized_mapping[k] = json.dumps(v, ensure_ascii=False)
                else:
                    serialized_mapping[k] = str(v)
            
            await client.hset(name, mapping=serialized_mapping)
            return True
        except Exception as e:
            self.logger.error(f"Redis哈希设置失败 {name}: {str(e)}")
            return False
    
    async def hget(self, name: str, key: str, default: Any = None) -> Any:
        """获取哈希表字段值"""
        try:
            client = await self.get_client()
            value = await client.hget(name, key)
            
            if value is None:
                return default
            
            # 尝试反序列化JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
                
        except Exception as e:
            self.logger.error(f"Redis哈希获取失败 {name}.{key}: {str(e)}")
            return default
    
    async def hgetall(self, name: str) -> Dict[str, Any]:
        """获取哈希表所有字段"""
        try:
            client = await self.get_client()
            data = await client.hgetall(name)
            
            # 反序列化值
            result = {}
            for k, v in data.items():
                try:
                    result[k] = json.loads(v)
                except (json.JSONDecodeError, TypeError):
                    result[k] = v
            
            return result
        except Exception as e:
            self.logger.error(f"Redis哈希获取全部失败 {name}: {str(e)}")
            return {}
    
    async def hdel(self, name: str, *keys: str) -> int:
        """删除哈希表字段"""
        try:
            client = await self.get_client()
            return await client.hdel(name, *keys)
        except Exception as e:
            self.logger.error(f"Redis哈希删除失败 {name}: {str(e)}")
            return 0
    
    async def sadd(self, name: str, *values: Any) -> int:
        """添加集合成员"""
        try:
            client = await self.get_client()
            # 序列化值
            serialized_values = []
            for v in values:
                if isinstance(v, (dict, list)):
                    serialized_values.append(json.dumps(v, ensure_ascii=False))
                else:
                    serialized_values.append(str(v))
            
            return await client.sadd(name, *serialized_values)
        except Exception as e:
            self.logger.error(f"Redis集合添加失败 {name}: {str(e)}")
            return 0
    
    async def smembers(self, name: str) -> List[Any]:
        """获取集合所有成员"""
        try:
            client = await self.get_client()
            members = await client.smembers(name)
            
            # 反序列化值
            result = []
            for member in members:
                try:
                    result.append(json.loads(member))
                except (json.JSONDecodeError, TypeError):
                    result.append(member)
            
            return result
        except Exception as e:
            self.logger.error(f"Redis集合获取失败 {name}: {str(e)}")
            return []
    
    async def srem(self, name: str, *values: Any) -> int:
        """删除集合成员"""
        try:
            client = await self.get_client()
            # 序列化值
            serialized_values = []
            for v in values:
                if isinstance(v, (dict, list)):
                    serialized_values.append(json.dumps(v, ensure_ascii=False))
                else:
                    serialized_values.append(str(v))
            
            return await client.srem(name, *serialized_values)
        except Exception as e:
            self.logger.error(f"Redis集合删除失败 {name}: {str(e)}")
            return 0
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            client = await self.get_client()
            await client.ping()
            return True
        except Exception as e:
            self.logger.error(f"Redis健康检查失败: {str(e)}")
            return False
    
    # 缓存键生成器
    def get_user_integration_key(self, user_id: str) -> str:
        """用户集成缓存键"""
        return f"user_integration:{user_id}"
    
    def get_platform_auth_key(self, user_id: str, platform: str) -> str:
        """平台认证缓存键"""
        return f"platform_auth:{user_id}:{platform}"
    
    def get_health_data_key(self, user_id: str, data_type: str, date: str) -> str:
        """健康数据缓存键"""
        return f"health_data:{user_id}:{data_type}:{date}"
    
    def get_sync_status_key(self, integration_id: int) -> str:
        """同步状态缓存键"""
        return f"sync_status:{integration_id}"


# 全局Redis服务实例
redis_service = RedisService() 