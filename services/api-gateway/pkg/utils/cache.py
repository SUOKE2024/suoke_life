"""
cache - 索克生活项目模块
"""

import json
import logging
import pickle
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

from fastapi import Request, Response

#! / usr / bin / env python
# - * - coding: utf - 8 - * -

"""
缓存管理模块，支持内存和Redis缓存
"""



logger = logging.getLogger(__name__)


@dataclass
class CacheKey:
    """缓存键"""
    path: str
    method: str
    query_params: Optional[Dict[str, str]] = None
    headers: Optional[Dict[str, str]] = None

    def __hash__(self) -> None:
"""TODO: 添加文档字符串"""
# 序列化并计算哈希
components = [
            self.path,
            self.method,
            json.dumps(self.query_params or {}, sort_keys = True),
            json.dumps(self.headers or {}, sort_keys = True)
]
return hash(';'.join(components))

    def to_string(self) -> str:
"""
将缓存键转换为字符串

Returns:
            str: 字符串表示
"""
components = [
            self.path,
            self.method,
            json.dumps(self.query_params or {}, sort_keys = True),
            json.dumps(self.headers or {}, sort_keys = True)
]
return ';'.join(components)


class CacheItem:
    """缓存项，存储响应内容和元数据"""

    def __init__(
self,
content: bytes,
status_code: int,
headers: Dict[str, str],
media_type: Optional[str] = None,
created_at: Optional[float] = None,
expires_at: Optional[float] = None
    ):
"""
初始化缓存项

Args:
            content: 响应内容
            status_code: 状态码
            headers: 响应头
            media_type: 媒体类型
            created_at: 创建时间戳
            expires_at: 过期时间戳
"""
self.content = content
self.status_code = status_code
self.headers = headers
self.media_type = media_type
self.created_at = created_at or time.time()
self.expires_at = expires_at

    def to_response(self) -> Response:
"""
转换为FastAPI响应对象

Returns:
            Response: 响应对象
"""
headers = dict(self.headers)
headers["X - Cache"] = "HIT"

return Response(
            content = self.content,
            status_code = self.status_code,
            headers = headers,
            media_type = self.media_type
)

    def is_expired(self, current_time: Optional[float] = None) -> bool:
"""
检查缓存项是否已过期

Args:
            current_time: 当前时间戳，如果为None则使用当前时间

Returns:
            bool: 是否已过期
"""
if self.expires_at is None:
            return False

now = current_time or time.time()
return now > self.expires_at

    def to_bytes(self) -> bytes:
"""
将缓存项序列化为字节

Returns:
            bytes: 序列化后的数据
"""
return pickle.dumps(self)

    @classmethod
    def from_bytes(cls, data: bytes) -> 'CacheItem':
"""
从字节反序列化缓存项

Args:
            data: 序列化数据

Returns:
            CacheItem: 反序列化后的缓存项
"""
return pickle.loads(data)


class CacheManager:
    """
    缓存管理器，支持内存和Redis缓存
    """

    def __init__(self, config):
"""
初始化缓存管理器

Args:
            config: 缓存配置
"""
self.config = config
self.memory_cache: Dict[str, CacheItem] = {}
self.lru_keys: List[str] = []  # 简单LRU实现
self.redis_client = None

# 如果使用Redis，初始化Redis客户端
if config.enabled and config.type=="redis" and config.redis_url:
            # 暂时不初始化Redis，仅使用内存缓存
            logger.warning("Redis缓存暂时禁用，使用内存缓存代替")
            # self._init_redis()

    async def _init_redis(self) -> None:
"""初始化Redis客户端 - 暂时禁用"""
# 只使用内存缓存进行测试
logger.info("Redis缓存已禁用，仅使用内存缓存")
self.redis_client = None

    def create_cache_key_from_request(self, request: Request, cache_headers: List[str] = None) -> CacheKey:
"""
从请求创建缓存键

Args:
            request: FastAPI请求对象
            cache_headers: 要包含在缓存键中的请求头列表

Returns:
            CacheKey: 缓存键
"""
# 提取查询参数
query_params = dict(request.query_params)

# 提取指定的请求头
headers = {}
if cache_headers:
            for header in cache_headers:
                header_value = request.headers.get(header.lower())
                if header_value:
                    headers[header.lower()] = header_value

return CacheKey(
            path = str(request.url.path),
            method = request.method,
            query_params = query_params,
            headers = headers
)

    def create_cache_item_from_response(self, response: Response, ttl: Optional[int] = None) -> CacheItem:
"""
从响应创建缓存项

Args:
            response: FastAPI响应对象
            ttl: 生存时间（秒）

Returns:
            CacheItem: 缓存项
"""
now = time.time()
expires_at = now + ttl if ttl else None

return CacheItem(
            content = response.body,
            status_code = response.status_code,
            headers = dict(response.headers),
            media_type = response.media_type,
            created_at = now,
            expires_at = expires_at
)

    async def get(self, key: CacheKey) -> Optional[CacheItem]:
"""
获取缓存项

Args:
            key: 缓存键

Returns:
            Optional[CacheItem]: 缓存项，如果不存在或已过期则返回None
"""
if not self.config.enabled:
            return None

key_str = key.to_string()

if self.config.type=="redis" and self.redis_client:
            return await self._get_from_redis(key_str)
else:
            return self._get_from_memory(key_str)

    def _get_from_memory(self, key_str: str) -> Optional[CacheItem]:
"""从内存缓存获取项"""
item = self.memory_cache.get(key_str)

if not item:
            return None

# 检查是否过期
if item.is_expired():
            del self.memory_cache[key_str]
            if key_str in self.lru_keys:
                self.lru_keys.remove(key_str)
            return None

# 更新LRU
if key_str in self.lru_keys:
            self.lru_keys.remove(key_str)
self.lru_keys.append(key_str)

return item

    async def _get_from_redis(self, key_str: str) -> Optional[CacheItem]:
"""
从Redis获取缓存项

Args:
            key_str: 缓存键字符串

Returns:
            Optional[CacheItem]: 缓存项，如果不存在则为None
"""
# 暂时禁用Redis缓存，返回None
return None

    async def set(self, key: CacheKey, item: CacheItem) -> bool:
"""
设置缓存项

Args:
            key: 缓存键
            item: 缓存项

Returns:
            bool: 是否成功
"""
if not self.config.enabled:
            return False

key_str = key.to_string()

if self.config.type=="redis" and self.redis_client:
            return await self._set_to_redis(key_str, item)
else:
            return self._set_to_memory(key_str, item)

    def _set_to_memory(self, key_str: str, item: CacheItem) -> bool:
"""
将缓存项写入内存

Args:
            key_str: 缓存键字符串
            item: 缓存项

Returns:
            bool: 操作是否成功
"""
# 清理过期缓存项
self._cleanup_expired()

# 检查缓存容量限制
if len(self.memory_cache) >=self.config.max_size:
            # 删除最旧的缓存项
            if self.lru_keys:
                oldest_key = self.lru_keys[0]  # 使用LRU列表中的第一个键
                del self.memory_cache[oldest_key]
                self.lru_keys.remove(oldest_key)
            elif self.memory_cache:
                # 备选方案：找出创建时间最早的项
                oldest_key = min(self.memory_cache.keys(),
                                key = lambda k: self.memory_cache[k].created_at)
                del self.memory_cache[oldest_key]

# 添加到内存缓存
self.memory_cache[key_str] = item

return True

    async def _set_to_redis(self, key_str: str, item: CacheItem) -> bool:
"""
设置缓存项到Redis

Args:
            key_str: 缓存键字符串
            item: 缓存项

Returns:
            bool: 是否成功
"""
# 暂时禁用Redis缓存，返回False
return False

    async def clear_all(self) -> None:
"""
清空所有缓存
"""
# 清空内存缓存
self.memory_cache.clear()
self.lru_keys.clear()

# 清空Redis缓存
if self.config.type=="redis" and self.redis_client:
            try:
                # 使用键模式匹配清除所有缓存项
                cursor = 0
                pattern = "api_gateway:cache: * "

                while True:
                    cursor, keys = await self.redis_client.scan(
                        cursor = cursor,
                        match = pattern,
                        count = 100
                    )

                    if keys:
                        await self.redis_client.delete( * keys)

                    if cursor==0:
                        break
            except Exception as e:
                logger.error(f"清空Redis缓存失败: {str(e)}", exc_info = True)

    async def close(self) -> None:
"""关闭缓存管理器（释放Redis连接等）"""
if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None

    def _cleanup_expired(self) -> None:
"""
清理内存中的过期缓存项
"""
current_time = time.time()
expired_keys = []

# 找出所有过期的键
for key, item in self.memory_cache.items():
            if item.expires_at and item.expires_at < current_time:
                expired_keys.append(key)

# 删除过期的项
for key in expired_keys:
            del self.memory_cache[key]