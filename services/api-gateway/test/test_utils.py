#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
工具模块测试
"""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from suoke_api_gateway.core.config import Settings
from suoke_api_gateway.utils.cache import CacheManager, CacheStats
from suoke_api_gateway.utils.circuit_breaker import (
    CircuitBreaker, CircuitBreakerError, CircuitState,
    circuit_breaker, circuit_breaker_manager
)
from suoke_api_gateway.utils.retry import (
    RetryManager, RetryError, ExponentialBackoffStrategy,
    FixedDelayStrategy, retry
)


class TestCacheManager:
    """缓存管理器测试"""
    
    @pytest.fixture
    def settings(self):
        """创建测试设置"""
        return Settings(
            redis_host="localhost",
            redis_port=6379,
            redis_db=1,
        )
    
    @pytest.fixture
    async def cache_manager(self, settings):
        """创建缓存管理器"""
        manager = CacheManager(settings)
        
        # 模拟Redis连接
        with patch('redis.asyncio.from_url') as mock_redis:
            mock_client = AsyncMock()
            mock_redis.return_value = mock_client
            mock_client.ping.return_value = True
            
            await manager.initialize()
            yield manager
            await manager.cleanup()
    
    @pytest.mark.asyncio
    async def test_cache_set_get(self, cache_manager):
        """测试缓存设置和获取"""
        # 模拟Redis操作
        cache_manager.redis_client.get.return_value = '"test_value"'
        cache_manager.redis_client.setex.return_value = True
        
        # 设置缓存
        result = await cache_manager.set("test_key", "test_value", 60)
        assert result is True
        
        # 获取缓存
        value = await cache_manager.get("test_key")
        assert value == "test_value"
    
    @pytest.mark.asyncio
    async def test_cache_miss(self, cache_manager):
        """测试缓存未命中"""
        cache_manager.redis_client.get.return_value = None
        
        value = await cache_manager.get("nonexistent_key")
        assert value is None
        assert cache_manager.miss_count == 1
    
    @pytest.mark.asyncio
    async def test_cache_delete(self, cache_manager):
        """测试缓存删除"""
        cache_manager.redis_client.delete.return_value = 1
        
        result = await cache_manager.delete("test_key")
        assert result is True
    
    @pytest.mark.asyncio
    async def test_cache_exists(self, cache_manager):
        """测试缓存存在检查"""
        cache_manager.redis_client.exists.return_value = 1
        
        result = await cache_manager.exists("test_key")
        assert result is True
    
    @pytest.mark.asyncio
    async def test_get_or_set(self, cache_manager):
        """测试获取或设置模式"""
        # 第一次调用返回None（缓存未命中）
        # 第二次调用返回值（缓存命中）
        cache_manager.redis_client.get.side_effect = [None, '"factory_value"']
        cache_manager.redis_client.setex.return_value = True
        
        async def factory_func():
            return "factory_value"
        
        value = await cache_manager.get_or_set("test_key", factory_func, 60)
        assert value == "factory_value"
    
    @pytest.mark.asyncio
    async def test_increment(self, cache_manager):
        """测试计数器递增"""
        cache_manager.redis_client.incrby.return_value = 5
        
        result = await cache_manager.increment("counter_key", 2)
        assert result == 5
    
    @pytest.mark.asyncio
    async def test_get_stats(self, cache_manager):
        """测试获取统计信息"""
        cache_manager.redis_client.info.return_value = {
            "used_memory": 1024,
            "expired_keys": 10,
        }
        cache_manager.redis_client.keys.return_value = ["key1", "key2", "key3"]
        
        cache_manager.hit_count = 100
        cache_manager.miss_count = 20
        
        stats = await cache_manager.get_stats()
        assert isinstance(stats, CacheStats)
        assert stats.total_keys == 3
        assert stats.hit_count == 100
        assert stats.miss_count == 20
        assert stats.hit_rate == 83.33333333333334  # 100/(100+20)*100


class TestCircuitBreaker:
    """熔断器测试"""
    
    def test_circuit_breaker_closed_state(self):
        """测试熔断器关闭状态"""
        breaker = CircuitBreaker(failure_threshold=3)
        assert breaker.state == CircuitState.CLOSED
    
    @pytest.mark.asyncio
    async def test_successful_call(self):
        """测试成功调用"""
        breaker = CircuitBreaker()
        
        async def success_func():
            return "success"
        
        result = await breaker.call(success_func)
        assert result == "success"
        assert breaker.total_successes == 1
        assert breaker.failure_count == 0
    
    @pytest.mark.asyncio
    async def test_failed_call(self):
        """测试失败调用"""
        breaker = CircuitBreaker(failure_threshold=2)
        
        async def fail_func():
            raise Exception("Test error")
        
        # 第一次失败
        with pytest.raises(Exception):
            await breaker.call(fail_func)
        
        assert breaker.failure_count == 1
        assert breaker.state == CircuitState.CLOSED
        
        # 第二次失败，应该触发熔断器开启
        with pytest.raises(Exception):
            await breaker.call(fail_func)
        
        assert breaker.failure_count == 2
        assert breaker.state == CircuitState.OPEN
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_open_state(self):
        """测试熔断器开启状态"""
        breaker = CircuitBreaker(failure_threshold=1)
        
        async def fail_func():
            raise Exception("Test error")
        
        # 触发熔断器开启
        with pytest.raises(Exception):
            await breaker.call(fail_func)
        
        assert breaker.state == CircuitState.OPEN
        
        # 在开启状态下调用应该抛出熔断器异常
        with pytest.raises(CircuitBreakerError):
            await breaker.call(fail_func)
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_half_open_recovery(self):
        """测试熔断器半开状态恢复"""
        breaker = CircuitBreaker(
            failure_threshold=1,
            recovery_timeout=0.1,  # 0.1秒恢复时间
            success_threshold=2,
        )
        
        async def fail_func():
            raise Exception("Test error")
        
        async def success_func():
            return "success"
        
        # 触发熔断器开启
        with pytest.raises(Exception):
            await breaker.call(fail_func)
        
        assert breaker.state == CircuitState.OPEN
        
        # 等待恢复时间
        await asyncio.sleep(0.2)
        
        # 第一次成功调用应该进入半开状态
        result = await breaker.call(success_func)
        assert result == "success"
        assert breaker.state == CircuitState.HALF_OPEN
        
        # 第二次成功调用应该恢复到关闭状态
        result = await breaker.call(success_func)
        assert result == "success"
        assert breaker.state == CircuitState.CLOSED
    
    def test_circuit_breaker_stats(self):
        """测试熔断器统计信息"""
        breaker = CircuitBreaker()
        stats = breaker.get_stats()
        
        assert stats["state"] == "closed"
        assert stats["total_requests"] == 0
        assert stats["failure_rate"] == 0
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_decorator(self):
        """测试熔断器装饰器"""
        @circuit_breaker("test_service", failure_threshold=2)
        async def test_func(should_fail=False):
            if should_fail:
                raise Exception("Test error")
            return "success"
        
        # 成功调用
        result = await test_func()
        assert result == "success"
        
        # 失败调用
        with pytest.raises(Exception):
            await test_func(should_fail=True)
        
        with pytest.raises(Exception):
            await test_func(should_fail=True)
        
        # 熔断器应该开启
        breaker = circuit_breaker_manager.get_circuit_breaker("test_service")
        assert breaker.state == CircuitState.OPEN


class TestRetryManager:
    """重试管理器测试"""
    
    @pytest.mark.asyncio
    async def test_successful_retry(self):
        """测试成功重试"""
        retry_manager = RetryManager(max_attempts=3)
        
        call_count = 0
        
        async def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary error")
            return "success"
        
        result = await retry_manager.execute(flaky_func)
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_retry_exhausted(self):
        """测试重试次数耗尽"""
        retry_manager = RetryManager(max_attempts=2)
        
        async def always_fail():
            raise Exception("Permanent error")
        
        with pytest.raises(RetryError):
            await retry_manager.execute(always_fail)
    
    @pytest.mark.asyncio
    async def test_retry_with_timeout(self):
        """测试带超时的重试"""
        retry_manager = RetryManager(max_attempts=5, timeout=0.1)
        
        async def slow_func():
            await asyncio.sleep(0.2)
            return "success"
        
        with pytest.raises(RetryError):
            await retry_manager.execute(slow_func)
    
    def test_exponential_backoff_strategy(self):
        """测试指数退避策略"""
        strategy = ExponentialBackoffStrategy(
            initial_delay=1.0,
            multiplier=2.0,
            max_delay=10.0,
        )
        
        assert strategy.get_delay(1) == 1.0
        assert strategy.get_delay(2) == 2.0
        assert strategy.get_delay(3) == 4.0
        assert strategy.get_delay(5) == 10.0  # 受max_delay限制
    
    def test_fixed_delay_strategy(self):
        """测试固定延迟策略"""
        strategy = FixedDelayStrategy(2.0)
        
        assert strategy.get_delay(1) == 2.0
        assert strategy.get_delay(5) == 2.0
    
    @pytest.mark.asyncio
    async def test_retry_decorator(self):
        """测试重试装饰器"""
        call_count = 0
        
        @retry(max_attempts=3)
        async def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary error")
            return "success"
        
        result = await flaky_func()
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_retry_stop_on_exception(self):
        """测试特定异常停止重试"""
        class PermanentError(Exception):
            pass
        
        retry_manager = RetryManager(
            max_attempts=5,
            stop_on=[PermanentError],
        )
        
        async def func_with_permanent_error():
            raise PermanentError("Should not retry")
        
        with pytest.raises(PermanentError):
            await retry_manager.execute(func_with_permanent_error)


if __name__ == "__main__":
    pytest.main(["-v", "test_utils.py"]) 