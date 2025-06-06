"""
test_cache - 索克生活项目模块
"""

from fastapi import Request, Response
from internal.model.config import CacheConfig
from pkg.utils.cache import CacheKey, CacheItem, CacheManager
from starlette.datastructures import Headers, QueryParams
from unittest.mock import AsyncMock, MagicMock, Mock, patch
import asyncio
import os
import pytest
import sys
import time

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
缓存模块单元测试
增强测试覆盖率，包括内存缓存和Redis缓存
"""



# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



@pytest.fixture
def memory_cache_config():
    """创建内存缓存配置"""
    return CacheConfig(
        enabled=True,
        type="memory",
        max_size=100,
        ttl=60
    )


@pytest.fixture
def redis_cache_config():
    """创建Redis缓存配置"""
    return CacheConfig(
        enabled=True,
        type="redis",
        redis_url="redis://localhost:6379/0",
        ttl=60,
        max_size=1000
    )


@pytest.fixture
def disabled_cache_config():
    """创建禁用的缓存配置"""
    return CacheConfig(
        enabled=False,
        type="memory"
    )


@pytest.fixture
def mock_request():
    """创建模拟请求"""
    request = Mock(spec=Request)
    request.url = Mock()
    request.url.path = "/api/test"
    request.method = "GET"
    request.query_params = QueryParams({"q": "test", "page": "1"})
    request.headers = Headers({"content-type": "application/json", "accept": "application/json"})
    return request


@pytest.fixture
def mock_response():
    """创建模拟响应"""
    response = Mock(spec=Response)
    response.status_code = 200
    response.body = b'{"message": "test"}'
    response.headers = {"content-type": "application/json", "content-length": "19"}
    response.media_type = "application/json"
    return response


class TestCacheKey:
    """缓存键测试类"""
    
    def test_cache_key_hash(self):
        """测试缓存键哈希方法"""
        key1 = CacheKey(
            path="/api/test",
            method="GET",
            query_params={"q": "test", "page": "1"},
            headers={"accept": "application/json"}
        )
        
        key2 = CacheKey(
            path="/api/test",
            method="GET",
            query_params={"q": "test", "page": "1"},
            headers={"accept": "application/json"}
        )
        
        key3 = CacheKey(
            path="/api/test",
            method="GET",
            query_params={"page": "1", "q": "test"},  # 顺序不同
            headers={"accept": "application/json"}
        )
        
        key4 = CacheKey(
            path="/api/test",
            method="POST",  # 不同的HTTP方法
            query_params={"q": "test", "page": "1"},
            headers={"accept": "application/json"}
        )
        
        # 相同键应该有相同哈希值
        assert hash(key1) == hash(key2)
        
        # 查询参数顺序不影响哈希值
        assert hash(key1) == hash(key3)
        
        # 不同的方法应该有不同的哈希值
        assert hash(key1) != hash(key4)
    
    def test_cache_key_to_string(self):
        """测试缓存键转字符串方法"""
        key = CacheKey(
            path="/api/test",
            method="GET",
            query_params={"q": "test", "page": "1"},
            headers={"accept": "application/json"}
        )
        
        key_str = key.to_string()
        
        assert "/api/test" in key_str
        assert "GET" in key_str
        assert "test" in key_str
        assert "page" in key_str
        assert "accept" in key_str
        assert "application/json" in key_str


class TestCacheItem:
    """缓存项测试类"""
    
    def test_cache_item_init(self):
        """测试缓存项初始化"""
        item = CacheItem(
            content=b'{"message": "test"}',
            status_code=200,
            headers={"content-type": "application/json"},
            media_type="application/json"
        )
        
        assert item.content == b'{"message": "test"}'
        assert item.status_code == 200
        assert item.headers == {"content-type": "application/json"}
        assert item.media_type == "application/json"
        assert item.created_at is not None
        assert item.expires_at is None
    
    def test_cache_item_to_response(self):
        """测试转换为响应对象"""
        item = CacheItem(
            content=b'{"message": "test"}',
            status_code=200,
            headers={"content-type": "application/json"},
            media_type="application/json"
        )
        
        response = item.to_response()
        
        assert response.body == b'{"message": "test"}'
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        assert response.headers["X-Cache"] == "HIT"
        assert response.media_type == "application/json"
    
    def test_cache_item_is_expired(self):
        """测试过期检查"""
        now = time.time()
        
        # 未过期的项
        future = now + 3600
        item1 = CacheItem(
            content=b'{"message": "test"}',
            status_code=200,
            headers={},
            expires_at=future
        )
        assert not item1.is_expired()
        assert not item1.is_expired(now)
        
        # 已过期的项
        past = now - 3600
        item2 = CacheItem(
            content=b'{"message": "test"}',
            status_code=200,
            headers={},
            expires_at=past
        )
        assert item2.is_expired()
        assert item2.is_expired(now)
        
        # 永不过期的项
        item3 = CacheItem(
            content=b'{"message": "test"}',
            status_code=200,
            headers={},
            expires_at=None
        )
        assert not item3.is_expired()
    
    def test_cache_item_serialization(self):
        """测试序列化和反序列化"""
        original = CacheItem(
            content=b'{"message": "test"}',
            status_code=200,
            headers={"content-type": "application/json"},
            media_type="application/json",
            expires_at=time.time() + 3600
        )
        
        # 序列化
        serialized = original.to_bytes()
        assert isinstance(serialized, bytes)
        
        # 反序列化
        deserialized = CacheItem.from_bytes(serialized)
        assert isinstance(deserialized, CacheItem)
        assert deserialized.content == original.content
        assert deserialized.status_code == original.status_code
        assert deserialized.headers == original.headers
        assert deserialized.media_type == original.media_type
        assert deserialized.expires_at == original.expires_at


class TestCacheManager:
    """缓存管理器测试类"""
    
    def test_create_cache_key_from_request(self, memory_cache_config, mock_request):
        """测试从请求创建缓存键"""
        manager = CacheManager(memory_cache_config)
        
        # 不包含头部的缓存键
        key1 = manager.create_cache_key_from_request(mock_request)
        assert key1.path == "/api/test"
        assert key1.method == "GET"
        assert key1.query_params == {"q": "test", "page": "1"}
        assert key1.headers == {}
        
        # 包含特定头部的缓存键
        key2 = manager.create_cache_key_from_request(mock_request, cache_headers=["accept", "content-type"])
        assert key2.path == "/api/test"
        assert key2.method == "GET"
        assert key2.query_params == {"q": "test", "page": "1"}
        assert key2.headers == {"accept": "application/json", "content-type": "application/json"}
    
    def test_create_cache_item_from_response(self, memory_cache_config, mock_response):
        """测试从响应创建缓存项"""
        manager = CacheManager(memory_cache_config)
        
        # 无TTL的缓存项
        item1 = manager.create_cache_item_from_response(mock_response)
        assert item1.content == mock_response.body
        assert item1.status_code == mock_response.status_code
        assert item1.headers == mock_response.headers
        assert item1.media_type == mock_response.media_type
        assert item1.created_at is not None
        assert item1.expires_at is None
        
        # 有TTL的缓存项
        now = time.time()
        item2 = manager.create_cache_item_from_response(mock_response, ttl=60)
        assert item2.content == mock_response.body
        assert item2.status_code == mock_response.status_code
        assert item2.expires_at is not None
        assert now + 59 < item2.expires_at < now + 61  # 考虑时间误差
    
    @pytest.mark.asyncio
    async     @cache(timeout=300)  # 5分钟缓存
def test_memory_cache_set_get(self, memory_cache_config, mock_request, mock_response):
        """测试内存缓存的存取"""
        manager = CacheManager(memory_cache_config)
        
        # 创建缓存键和项
        key = manager.create_cache_key_from_request(mock_request)
        item = manager.create_cache_item_from_response(mock_response)
        
        # 设置缓存
        result = await manager.set(key, item)
        assert result is True
        
        # 获取缓存
        cached = await manager.get(key)
        assert cached is not None
        assert cached.content == item.content
        assert cached.status_code == item.status_code
    
    @pytest.mark.asyncio
    async def test_disabled_cache(self, disabled_cache_config, mock_request, mock_response):
        """测试禁用缓存"""
        manager = CacheManager(disabled_cache_config)
        
        # 创建缓存键和项
        key = manager.create_cache_key_from_request(mock_request)
        item = manager.create_cache_item_from_response(mock_response)
        
        # 设置缓存应该没有效果
        success = await manager.set(key, item)
        assert not success
        
        # 获取缓存应该返回None
        cached = await manager.get(key)
        assert cached is None
    
    @pytest.mark.asyncio
    async def test_memory_cache_expiration(self, memory_cache_config, mock_request, mock_response):
        """测试内存缓存过期机制"""
        manager = CacheManager(memory_cache_config)
        
        # 创建即将过期的缓存项
        key = manager.create_cache_key_from_request(mock_request)
        item = CacheItem(
            content=mock_response.body,
            status_code=mock_response.status_code,
            headers=mock_response.headers,
            media_type=mock_response.media_type,
            expires_at=time.time() + 0.1  # 0.1秒后过期
        )
        
        # 设置缓存
        await manager.set(key, item)
        
        # 获取未过期的缓存
        cached1 = await manager.get(key)
        assert cached1 is not None
        
        # 等待缓存过期
        await asyncio.sleep(0.2)
        
        # 获取已过期的缓存
        cached2 = await manager.get(key)
        assert cached2 is None
    
    @pytest.mark.asyncio
    async def test_memory_cache_lru(self, memory_cache_config, mock_request, mock_response):
        """测试内存缓存LRU机制"""
        # 创建一个小容量缓存
        config = CacheConfig(
            enabled=True,
            type="memory",
            max_size=2,  # 只允许2个缓存项
            ttl=60
        )
        manager = CacheManager(config)
        
        # 创建三个不同的缓存键
        key1 = CacheKey(path="/api/test/1", method="GET")
        key2 = CacheKey(path="/api/test/2", method="GET")
        key3 = CacheKey(path="/api/test/3", method="GET")
        
        # 创建缓存项
        item = manager.create_cache_item_from_response(mock_response)
        
        # 设置三个缓存项
        await manager.set(key1, item)
        await manager.set(key2, item)
        await manager.set(key3, item)  # 这应该会淘汰LRU中最旧的项（key1）
        
        # 验证LRU机制
        cached1 = await manager.get(key1)
        cached2 = await manager.get(key2)
        cached3 = await manager.get(key3)
        
        assert cached1 is None  # 应该已被淘汰
        assert cached2 is not None
        assert cached3 is not None
    
    @pytest.mark.asyncio
    async def test_memory_cache_cleanup(self, memory_cache_config):
        """测试内存缓存清理过期项"""
        manager = CacheManager(memory_cache_config)
        
        # 创建一些过期和未过期的缓存项
        now = time.time()
        
        # 过期项
        key1 = CacheKey(path="/api/test/1", method="GET")
        item1 = CacheItem(
            content=b'{"id": 1}',
            status_code=200,
            headers={},
            expires_at=now - 10  # 10秒前过期
        )
        
        # 未过期项
        key2 = CacheKey(path="/api/test/2", method="GET")
        item2 = CacheItem(
            content=b'{"id": 2}',
            status_code=200,
            headers={},
            expires_at=now + 3600  # 1小时后过期
        )
        
        # 手动添加到内存缓存
        manager.memory_cache[key1.to_string()] = item1
        manager.memory_cache[key2.to_string()] = item2
        
        # 清理过期项
        manager._cleanup_expired()
        
        # 验证清理结果
        assert key1.to_string() not in manager.memory_cache
        assert key2.to_string() in manager.memory_cache
    
    @pytest.mark.asyncio
    async def test_clear_all(self, memory_cache_config, mock_request, mock_response):
        """测试清空所有缓存"""
        manager = CacheManager(memory_cache_config)
        
        # 添加几个缓存项
        key1 = CacheKey(path="/api/test/1", method="GET")
        key2 = CacheKey(path="/api/test/2", method="GET")
        item = manager.create_cache_item_from_response(mock_response)
        
        await manager.set(key1, item)
        await manager.set(key2, item)
        
        # 确认缓存项已添加
        assert await manager.get(key1) is not None
        assert await manager.get(key2) is not None
        
        # 清空所有缓存
        await manager.clear_all()
        
        # 确认缓存已清空
        assert await manager.get(key1) is None
        assert await manager.get(key2) is None
    
    @patch("aioredis.from_url")
    @pytest.mark.asyncio
    @pytest.mark.skipif(True, reason="需要安装aioredis模块才能运行此测试")
    async def test_redis_cache(self, mock_redis, redis_cache_config, mock_request, mock_response):
        """测试Redis缓存"""
        # 先模拟导入错误处理，而不是实际导入
        with patch("importlib.import_module") as mock_import:
            # 模拟 aioredis 导入成功
            mock_import.return_value = AsyncMock()
            
            # 模拟Redis客户端
            mock_redis_client = AsyncMock()
            mock_redis.return_value = mock_redis_client
            
            # 模拟Redis get返回None（缓存未命中）
            mock_redis_client.get.return_value = None
            
            # 创建Redis缓存管理器
            manager = CacheManager(redis_cache_config)
            await manager._init_redis()  # 手动初始化Redis
            
            # 验证Redis客户端已创建
            assert manager.redis_client is not None
            
            # 创建缓存键和项
            key = manager.create_cache_key_from_request(mock_request)
            item = manager.create_cache_item_from_response(mock_response, ttl=60)
            
            # 设置缓存
            await manager.set(key, item)
            
            # 验证Redis set被调用
            mock_redis_client.setex.assert_called_once()
            
            # 模拟Redis get返回序列化的缓存项
            mock_redis_client.get.return_value = item.to_bytes()
            
            # 获取缓存
            cached = await manager.get(key)
            assert cached is not None
            assert cached.content == item.content
            
            # 测试清空Redis缓存
            mock_redis_client.scan.return_value = (0, ["api_gateway:cache:key1", "api_gateway:cache:key2"])
            await manager.clear_all()
            mock_redis_client.delete.assert_called_once()
            
            # 测试关闭Redis连接
            await manager.close()
            mock_redis_client.close.assert_called_once()
    
    @patch("aioredis.from_url")
    @pytest.mark.asyncio
    @pytest.mark.skipif(True, reason="需要安装aioredis模块才能运行此测试")
    async def test_redis_error_handling(self, mock_redis, redis_cache_config):
        """测试Redis错误处理"""
        # 先模拟导入错误处理
        with patch("importlib.import_module") as mock_import:
            # 模拟 aioredis 导入失败
            mock_import.side_effect = ImportError("No module named 'aioredis'")
            
            # 创建Redis缓存管理器
            manager = CacheManager(redis_cache_config)
            await manager._init_redis()  # 手动初始化Redis
            
            # 验证Redis客户端创建失败
            assert manager.redis_client is None
            
            # 验证回退到内存缓存
            key = CacheKey(path="/api/test", method="GET")
            item = CacheItem(
                content=b'{"message": "test"}',
                status_code=200,
                headers={}
            )
            
            # 设置缓存应该使用内存缓存
            success = await manager.set(key, item)
            assert success is True
            
            # 获取缓存应该从内存缓存获取
            cached = await manager.get(key)
            assert cached is not None
            assert cached.content == item.content

    @patch("aioredis.from_url")
    @pytest.mark.asyncio
    @pytest.mark.skipif(True, reason="需要安装aioredis模块才能运行此测试")
    async def test_redis_connection_failure(self, mock_redis):
        """测试Redis连接失败场景"""
        # 模拟Redis连接异常
        mock_redis.side_effect = Exception("Failed to connect to Redis")
        
        # 创建Redis配置
        config = CacheConfig(
            enabled=True,
            type="redis",
            redis_url="redis://localhost:6379/0",
            ttl=60
        )
        
        # 创建缓存管理器 - 应该自动回退到内存缓存
        manager = CacheManager(config)
        await manager._init_redis()
        
        # 验证Redis客户端为None
        assert manager.redis_client is None
        
        # 测试回退到内存缓存
        key = CacheKey(path="/api/test", method="GET")
        item = CacheItem(
            content=b'{"test": true}',
            status_code=200,
            headers={}
        )
        
        # 设置缓存应该存储到内存中
        success = await manager.set(key, item)
        assert success is True
        
        # 获取缓存应该从内存中获取
        cached = await manager.get(key)
        assert cached is not None
        assert cached.content == item.content

    @patch("aioredis.from_url")
    @pytest.mark.asyncio
    @pytest.mark.skipif(True, reason="需要安装aioredis模块才能运行此测试")
    async def test_redis_serialization_errors(self, mock_redis):
        """测试Redis序列化错误场景"""
        # 模拟Redis客户端
        mock_redis_client = AsyncMock()
        mock_redis.return_value = mock_redis_client
        
        # 模拟Redis get返回损坏的数据
        mock_redis_client.get.return_value = b'corrupted data'
        
        # 创建Redis配置
        config = CacheConfig(
            enabled=True,
            type="redis",
            redis_url="redis://localhost:6379/0",
            ttl=60
        )
        
        # 创建缓存管理器
        manager = CacheManager(config)
        await manager._init_redis()
        
        # 尝试获取缓存，应该返回None而不是引发异常
        key = CacheKey(path="/api/test", method="GET")
        cached = await manager.get(key)
        assert cached is None
        
        # 验证Redis get被调用
        mock_redis_client.get.assert_called_once()

    @patch("aioredis.from_url")
    @pytest.mark.asyncio
    @pytest.mark.skipif(True, reason="需要安装aioredis模块才能运行此测试")
    async def test_redis_set_errors(self, mock_redis):
        """测试Redis写入错误场景"""
        # 模拟Redis客户端，set操作抛出异常
        mock_redis_client = AsyncMock()
        mock_redis_client.setex.side_effect = Exception("Redis write error")
        mock_redis.return_value = mock_redis_client
        
        # 创建Redis配置
        config = CacheConfig(
            enabled=True,
            type="redis",
            redis_url="redis://localhost:6379/0",
            ttl=60
        )
        
        # 创建缓存管理器
        manager = CacheManager(config)
        await manager._init_redis()
        
        # 测试写入错误处理
        key = CacheKey(path="/api/test", method="GET")
        item = CacheItem(
            content=b'{"test": true}',
            status_code=200,
            headers={},
            expires_at=time.time() + 60
        )
        
        # 设置缓存应该返回False表示失败
        success = await manager.set(key, item)
        assert success is False
        
        # 验证Redis setex被调用
        mock_redis_client.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_memory_cache_advanced_lru(self):
        """测试内存缓存高级LRU机制"""
        # 创建小容量缓存
        config = CacheConfig(
            enabled=True,
            type="memory",
            max_size=3,  # 只允许3个缓存项
            ttl=60
        )
        manager = CacheManager(config)
        
        # 创建多个缓存键和项
        keys = [
            CacheKey(path=f"/api/test/{i}", method="GET")
            for i in range(5)  # 创建5个键，超出容量
        ]
        
        items = [
            CacheItem(
                content=f'{{"id": {i}}}'.encode(),
                status_code=200,
                headers={}
            )
            for i in range(5)
        ]
        
        # 依次设置缓存项
        for i in range(5):
            await manager.set(keys[i], items[i])
        
        # 验证LRU机制 - 前两个应该被淘汰
        assert await manager.get(keys[0]) is None
        assert await manager.get(keys[1]) is None
        
        # 最新的三个应该存在
        for i in range(2, 5):
            cached = await manager.get(keys[i])
            assert cached is not None
            assert f'{{"id": {i}}}'.encode() == cached.content
        
        # 访问一个项，更新其LRU状态
        await manager.get(keys[2])
        
        # 添加一个新项，应该淘汰最久未使用的项（keys[3]）
        key_new = CacheKey(path="/api/test/new", method="GET")
        item_new = CacheItem(
            content=b'{"id": "new"}',
            status_code=200,
            headers={}
        )
        await manager.set(key_new, item_new)
        
        # 验证淘汰结果
        assert await manager.get(keys[3]) is None
        assert await manager.get(keys[2]) is not None  # 被访问过，应该保留
        assert await manager.get(keys[4]) is not None
        assert await manager.get(key_new) is not None

    @pytest.mark.asyncio
    async def test_memory_cache_cleanup_performance(self):
        """测试内存缓存清理性能和边缘情况"""
        config = CacheConfig(
            enabled=True,
            type="memory",
            max_size=100,
            ttl=1  # 设置为1秒，以便快速过期
        )
        manager = CacheManager(config)
        
        # 添加50个即将过期的项
        keys = []
        now = time.time()
        
        for i in range(50):
            key = CacheKey(path=f"/api/test/{i}", method="GET")
            keys.append(key)
            
            item = CacheItem(
                content=f'{{"id": {i}}}'.encode(),
                status_code=200,
                headers={},
                expires_at=now + 0.5  # 0.5秒后过期
            )
            
            await manager.set(key, item)
        
        # 验证所有项都已添加
        assert len(manager.memory_cache) == 50
        
        # 等待项过期
        await asyncio.sleep(1)
        
        # 设置一个新项触发清理
        new_key = CacheKey(path="/api/test/new", method="GET")
        new_item = CacheItem(
            content=b'{"id": "new"}',
            status_code=200,
            headers={}
        )
        await manager.set(new_key, new_item)
        
        # 验证过期项已被清理
        assert len(manager.memory_cache) == 1  # 只剩下新添加的项
        assert new_key.to_string() in manager.memory_cache
        
        # 验证所有老项都被清理了
        for key in keys:
            assert await manager.get(key) is None

    @pytest.mark.asyncio
    async def test_cache_item_serialization_edge_cases(self):
        """测试缓存项序列化边缘情况"""
        # 测试空内容
        item1 = CacheItem(
            content=b'',
            status_code=204,
            headers={}
        )
        serialized1 = item1.to_bytes()
        deserialized1 = CacheItem.from_bytes(serialized1)
        assert deserialized1.content == b''
        assert deserialized1.status_code == 204
        
        # 测试二进制非JSON内容
        binary_data = bytes([0, 1, 2, 3, 4, 255, 254, 253])
        item2 = CacheItem(
            content=binary_data,
            status_code=200,
            headers={"content-type": "application/octet-stream"},
            media_type="application/octet-stream"
        )
        serialized2 = item2.to_bytes()
        deserialized2 = CacheItem.from_bytes(serialized2)
        assert deserialized2.content == binary_data
        assert deserialized2.media_type == "application/octet-stream"
        
        # 测试大量header
        large_headers = {f"header-{i}": f"value-{i}" for i in range(100)}
        item3 = CacheItem(
            content=b'{"test": true}',
            status_code=200,
            headers=large_headers
        )
        serialized3 = item3.to_bytes()
        deserialized3 = CacheItem.from_bytes(serialized3)
        assert deserialized3.headers == large_headers
        
        # 测试过期边缘情况
        now = time.time()
        # 刚刚好过期的情况
        item4 = CacheItem(
            content=b'{"test": true}',
            status_code=200,
            headers={},
            expires_at=now
        )
        assert item4.is_expired(now + 0.001)
        assert not item4.is_expired(now - 0.001)
        
        # 永不过期的极端情况
        item5 = CacheItem(
            content=b'{"test": true}',
            status_code=200,
            headers={},
            expires_at=float('inf')  # 无穷大时间戳
        )
        assert not item5.is_expired()
        assert not item5.is_expired(time.time() + 1000000000)


if __name__ == "__main__":
    pytest.main(["-v", __file__]) 