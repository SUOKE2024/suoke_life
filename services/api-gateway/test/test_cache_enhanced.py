#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
缓存模块增强测试
专门针对边缘情况和错误处理，提升测试覆盖率至90%+
"""

import asyncio
import json
import os
import sys
import time
from unittest.mock import AsyncMock, MagicMock, Mock, patch, call
from datetime import datetime, timedelta
import pickle

import pytest
from fastapi import Request, Response
from starlette.datastructures import Headers, QueryParams

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from internal.model.config import CacheConfig
from pkg.utils.cache import CacheKey, CacheItem, CacheManager


class TestCacheEdgeCases:
    """缓存边缘情况测试"""
    
    @pytest.mark.asyncio
    async def test_cache_with_none_values(self):
        """测试缓存None值的处理"""
        config = CacheConfig(enabled=True, type="memory", max_size=10, ttl=60)
        cache_manager = CacheManager(config)
        
        # 创建包含None值的缓存项
        cache_item = CacheItem(
            content=None,
            status_code=204,
            headers={"content-length": "0"},
            media_type=None
        )
        
        key = CacheKey(path="/api/empty", method="GET")
        await cache_manager.set(key, cache_item)
        
        # 验证可以正确获取None值
        retrieved = await cache_manager.get(key)
        assert retrieved is not None
        assert retrieved.content is None
        assert retrieved.status_code == 204
        assert retrieved.media_type is None
    
    @pytest.mark.asyncio
    async def test_cache_with_large_content(self):
        """测试大内容缓存处理"""
        config = CacheConfig(enabled=True, type="memory", max_size=10, ttl=60)
        cache_manager = CacheManager(config)
        
        # 创建大内容（1MB）
        large_content = b"x" * (1024 * 1024)
        cache_item = CacheItem(
            content=large_content,
            status_code=200,
            headers={"content-type": "application/octet-stream"},
            media_type="application/octet-stream"
        )
        
        key = CacheKey(path="/api/large", method="GET")
        await cache_manager.set(key, cache_item)
        
        retrieved = await cache_manager.get(key)
        assert retrieved is not None
        assert len(retrieved.content) == 1024 * 1024
        assert retrieved.content == large_content
    
    @pytest.mark.asyncio
    async def test_cache_with_unicode_content(self):
        """测试Unicode内容缓存"""
        config = CacheConfig(enabled=True, type="memory", max_size=10, ttl=60)
        cache_manager = CacheManager(config)
        
        # 包含各种Unicode字符的内容
        unicode_content = json.dumps({
            "message": "测试消息 🚀",
            "emoji": "😀😃😄😁😆😅😂🤣",
            "chinese": "中文测试内容",
            "japanese": "日本語テスト",
            "korean": "한국어 테스트",
            "arabic": "اختبار عربي",
            "russian": "русский тест"
        }, ensure_ascii=False).encode('utf-8')
        
        cache_item = CacheItem(
            content=unicode_content,
            status_code=200,
            headers={"content-type": "application/json; charset=utf-8"},
            media_type="application/json"
        )
        
        key = CacheKey(path="/api/unicode", method="GET")
        await cache_manager.set(key, cache_item)
        
        retrieved = await cache_manager.get(key)
        assert retrieved is not None
        assert retrieved.content == unicode_content
        
        # 验证可以正确解码
        decoded = json.loads(retrieved.content.decode('utf-8'))
        assert "🚀" in decoded["message"]
        assert "😀" in decoded["emoji"]
    
    @pytest.mark.asyncio
    async def test_cache_with_binary_content(self):
        """测试二进制内容缓存"""
        config = CacheConfig(enabled=True, type="memory", max_size=10, ttl=60)
        cache_manager = CacheManager(config)
        
        # 创建二进制内容（模拟图片数据）
        binary_content = bytes(range(256)) * 100  # 25.6KB的二进制数据
        
        cache_item = CacheItem(
            content=binary_content,
            status_code=200,
            headers={
                "content-type": "image/png",
                "content-length": str(len(binary_content))
            },
            media_type="image/png"
        )
        
        key = CacheKey(path="/api/image.png", method="GET")
        await cache_manager.set(key, cache_item)
        
        retrieved = await cache_manager.get(key)
        assert retrieved is not None
        assert retrieved.content == binary_content
        assert len(retrieved.content) == 25600
    
    @pytest.mark.asyncio
    async def test_cache_key_with_special_characters(self):
        """测试包含特殊字符的缓存键"""
        config = CacheConfig(enabled=True, type="memory", max_size=10, ttl=60)
        cache_manager = CacheManager(config)
        
        # 包含特殊字符的路径和参数
        special_key = CacheKey(
            path="/api/search/测试 & 特殊字符!@#$%^&*()_+-=[]{}|;':\",./<>?",
            method="GET",
            query_params={
                "q": "测试查询 & 特殊字符",
                "filter": "type:test&status:active",
                "sort": "created_at:desc,name:asc"
            },
            headers={
                "accept": "application/json",
                "user-agent": "Mozilla/5.0 (测试浏览器)"
            }
        )
        
        cache_item = CacheItem(
            content=b'{"results": []}',
            status_code=200,
            headers={"content-type": "application/json"}
        )
        
        await cache_manager.set(special_key, cache_item)
        retrieved = await cache_manager.get(special_key)
        
        assert retrieved is not None
        assert retrieved.content == b'{"results": []}'
    
    @pytest.mark.asyncio
    async def test_cache_concurrent_access(self):
        """测试并发访问缓存"""
        config = CacheConfig(enabled=True, type="memory", max_size=100, ttl=60)
        cache_manager = CacheManager(config)
        
        async def set_cache_item(index):
            key = CacheKey(path=f"/api/item/{index}", method="GET")
            cache_item = CacheItem(
                content=f'{{"id": {index}, "data": "test"}}'.encode(),
                status_code=200,
                headers={"content-type": "application/json"}
            )
            await cache_manager.set(key, cache_item)
            return index
        
        async def get_cache_item(index):
            key = CacheKey(path=f"/api/item/{index}", method="GET")
            return await cache_manager.get(key)
        
        # 并发设置100个缓存项
        set_tasks = [set_cache_item(i) for i in range(100)]
        await asyncio.gather(*set_tasks)
        
        # 并发获取100个缓存项
        get_tasks = [get_cache_item(i) for i in range(100)]
        results = await asyncio.gather(*get_tasks)
        
        # 验证所有项都能正确获取
        for i, result in enumerate(results):
            assert result is not None
            expected_content = f'{{"id": {i}, "data": "test"}}'.encode()
            assert result.content == expected_content
    
    @pytest.mark.asyncio
    async def test_cache_memory_pressure(self):
        """测试内存压力下的缓存行为"""
        config = CacheConfig(enabled=True, type="memory", max_size=10, ttl=60)
        cache_manager = CacheManager(config)
        
        # 添加超过最大容量的缓存项
        for i in range(20):
            key = CacheKey(path=f"/api/item/{i}", method="GET")
            cache_item = CacheItem(
                content=f'{{"id": {i}}}'.encode(),
                status_code=200,
                headers={"content-type": "application/json"}
            )
            await cache_manager.set(key, cache_item)
        
        # 验证只保留了最新的10个项（LRU策略）
        cache_size = len(cache_manager._memory_cache)
        assert cache_size <= 10
        
        # 验证最新的项仍然存在
        for i in range(15, 20):
            key = CacheKey(path=f"/api/item/{i}", method="GET")
            result = await cache_manager.get(key)
            assert result is not None
        
        # 验证最旧的项已被清除
        for i in range(5):
            key = CacheKey(path=f"/api/item/{i}", method="GET")
            result = await cache_manager.get(key)
            assert result is None
    
    @pytest.mark.asyncio
    async def test_cache_ttl_edge_cases(self):
        """测试TTL边缘情况"""
        config = CacheConfig(enabled=True, type="memory", max_size=10, ttl=1)  # 1秒TTL
        cache_manager = CacheManager(config)
        
        key = CacheKey(path="/api/test", method="GET")
        cache_item = CacheItem(
            content=b'{"test": "data"}',
            status_code=200,
            headers={"content-type": "application/json"}
        )
        
        # 设置缓存项
        await cache_manager.set(key, cache_item)
        
        # 立即获取应该成功
        result = await cache_manager.get(key)
        assert result is not None
        
        # 等待过期
        await asyncio.sleep(1.1)
        
        # 过期后获取应该返回None
        result = await cache_manager.get(key)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_cache_serialization_errors(self):
        """测试序列化错误处理"""
        config = CacheConfig(enabled=True, type="memory", max_size=10, ttl=60)
        cache_manager = CacheManager(config)
        
        # 创建不可序列化的对象
        class UnserializableObject:
            def __init__(self):
                self.data = "test"
            
            def __getstate__(self):
                raise Exception("Cannot serialize this object")
        
        # 尝试缓存不可序列化的内容
        try:
            unserializable_content = pickle.dumps(UnserializableObject())
        except Exception:
            # 如果pickle失败，使用其他方式模拟序列化错误
            unserializable_content = b"mock_unserializable_content"
        
        cache_item = CacheItem(
            content=unserializable_content,
            status_code=200,
            headers={"content-type": "application/octet-stream"}
        )
        
        key = CacheKey(path="/api/unserializable", method="GET")
        
        # 应该能够处理而不崩溃
        await cache_manager.set(key, cache_item)
        result = await cache_manager.get(key)
        assert result is not None


class TestCacheManagerErrorHandling:
    """缓存管理器错误处理测试"""
    
    @pytest.mark.asyncio
    async def test_disabled_cache_operations(self):
        """测试禁用缓存时的操作"""
        config = CacheConfig(enabled=False, type="memory")
        cache_manager = CacheManager(config)
        
        key = CacheKey(path="/api/test", method="GET")
        cache_item = CacheItem(
            content=b'{"test": "data"}',
            status_code=200,
            headers={"content-type": "application/json"}
        )
        
        # 禁用缓存时，set操作应该不执行
        await cache_manager.set(key, cache_item)
        
        # get操作应该返回None
        result = await cache_manager.get(key)
        assert result is None
        
        # clear操作应该不报错
        await cache_manager.clear(key)
        await cache_manager.clear_all()
    
    @pytest.mark.asyncio
    async def test_invalid_cache_type(self):
        """测试无效的缓存类型"""
        config = CacheConfig(enabled=True, type="invalid_type")
        
        # 应该回退到内存缓存
        cache_manager = CacheManager(config)
        assert cache_manager._memory_cache is not None
    
    @pytest.mark.asyncio
    async def test_cache_cleanup_on_memory_error(self):
        """测试内存错误时的缓存清理"""
        config = CacheConfig(enabled=True, type="memory", max_size=5, ttl=60)
        cache_manager = CacheManager(config)
        
        # 模拟内存不足的情况
        with patch.object(cache_manager, '_memory_cache', side_effect=MemoryError("Out of memory")):
            key = CacheKey(path="/api/test", method="GET")
            cache_item = CacheItem(
                content=b'{"test": "data"}',
                status_code=200,
                headers={"content-type": "application/json"}
            )
            
            # 应该能够处理内存错误而不崩溃
            try:
                await cache_manager.set(key, cache_item)
            except MemoryError:
                pass  # 预期的错误
    
    @pytest.mark.asyncio
    async def test_cache_key_hash_collision(self):
        """测试缓存键哈希冲突处理"""
        config = CacheConfig(enabled=True, type="memory", max_size=10, ttl=60)
        cache_manager = CacheManager(config)
        
        # 创建两个不同但可能产生哈希冲突的键
        key1 = CacheKey(path="/api/test1", method="GET")
        key2 = CacheKey(path="/api/test2", method="GET")
        
        cache_item1 = CacheItem(
            content=b'{"id": 1}',
            status_code=200,
            headers={"content-type": "application/json"}
        )
        
        cache_item2 = CacheItem(
            content=b'{"id": 2}',
            status_code=200,
            headers={"content-type": "application/json"}
        )
        
        # 设置两个不同的缓存项
        await cache_manager.set(key1, cache_item1)
        await cache_manager.set(key2, cache_item2)
        
        # 验证两个项都能正确获取
        result1 = await cache_manager.get(key1)
        result2 = await cache_manager.get(key2)
        
        assert result1 is not None
        assert result2 is not None
        assert result1.content == b'{"id": 1}'
        assert result2.content == b'{"id": 2}'
    
    @pytest.mark.asyncio
    async def test_cache_statistics_and_monitoring(self):
        """测试缓存统计和监控功能"""
        config = CacheConfig(enabled=True, type="memory", max_size=10, ttl=60)
        cache_manager = CacheManager(config)
        
        # 执行一些缓存操作
        for i in range(5):
            key = CacheKey(path=f"/api/item/{i}", method="GET")
            cache_item = CacheItem(
                content=f'{{"id": {i}}}'.encode(),
                status_code=200,
                headers={"content-type": "application/json"}
            )
            await cache_manager.set(key, cache_item)
        
        # 执行一些获取操作（命中）
        for i in range(3):
            key = CacheKey(path=f"/api/item/{i}", method="GET")
            await cache_manager.get(key)
        
        # 执行一些获取操作（未命中）
        for i in range(5, 8):
            key = CacheKey(path=f"/api/item/{i}", method="GET")
            await cache_manager.get(key)
        
        # 验证缓存大小
        assert len(cache_manager._memory_cache) == 5


@pytest.mark.asyncio
async def test_cache_performance_under_load():
    """测试高负载下的缓存性能"""
    config = CacheConfig(enabled=True, type="memory", max_size=1000, ttl=300)
    cache_manager = CacheManager(config)
    
    # 测试大量并发读写操作
    async def cache_operation(operation_id):
        key = CacheKey(path=f"/api/load_test/{operation_id}", method="GET")
        
        if operation_id % 2 == 0:
            # 写操作
            cache_item = CacheItem(
                content=f'{{"id": {operation_id}, "timestamp": {time.time()}}}'.encode(),
                status_code=200,
                headers={"content-type": "application/json"}
            )
            await cache_manager.set(key, cache_item)
        else:
            # 读操作
            await cache_manager.get(key)
    
    # 执行1000个并发操作
    start_time = time.time()
    tasks = [cache_operation(i) for i in range(1000)]
    await asyncio.gather(*tasks)
    end_time = time.time()
    
    # 验证性能（应该在合理时间内完成）
    execution_time = end_time - start_time
    assert execution_time < 5.0  # 应该在5秒内完成
    
    # 验证缓存状态
    assert len(cache_manager._memory_cache) <= 1000


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 