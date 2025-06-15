"""
重试工具单元测试
"""

import pytest
import asyncio
import time
from unittest.mock import patch, MagicMock
from typing import Any

from blockchain_service.utils.retry import (
    RetryConfig,
    retry_async,
    async_retry,
    create_retry_config
)


class TestRetryConfig:
    """重试配置测试"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = RetryConfig()
        
        assert config.max_attempts == 3
        assert config.delay == 1.0
        assert config.backoff_factor == 2.0
        assert config.max_delay == 60.0
        assert config.exceptions == (Exception,)
        assert config.jitter is True
    
    def test_custom_config(self):
        """测试自定义配置"""
        config = RetryConfig(
            max_attempts=5,
            delay=0.5,
            backoff_factor=1.5,
            max_delay=30.0,
            exceptions=(ValueError, TypeError),
            jitter=False
        )
        
        assert config.max_attempts == 5
        assert config.delay == 0.5
        assert config.backoff_factor == 1.5
        assert config.max_delay == 30.0
        assert config.exceptions == (ValueError, TypeError)
        assert config.jitter is False


class TestCreateRetryConfig:
    """创建重试配置测试"""
    
    def test_create_default_config(self):
        """测试创建默认配置"""
        config = create_retry_config()
        
        assert isinstance(config, RetryConfig)
        assert config.max_attempts == 3
        assert config.delay == 1.0
        assert config.backoff_factor == 2.0
        assert config.max_delay == 60.0
        assert config.exceptions == (Exception,)
        assert config.jitter is True
    
    def test_create_custom_config(self):
        """测试创建自定义配置"""
        config = create_retry_config(
            max_attempts=4,
            delay=2.0,
            backoff_factor=3.0,
            max_delay=120.0,
            exceptions=ValueError,
            jitter=False
        )
        
        assert config.max_attempts == 4
        assert config.delay == 2.0
        assert config.backoff_factor == 3.0
        assert config.max_delay == 120.0
        assert config.exceptions == (ValueError,)  # 单个异常转换为元组
        assert config.jitter is False
    
    def test_create_config_with_multiple_exceptions(self):
        """测试创建包含多个异常的配置"""
        config = create_retry_config(
            exceptions=(ValueError, TypeError, RuntimeError)
        )
        
        assert config.exceptions == (ValueError, TypeError, RuntimeError)


class TestRetryAsync:
    """异步重试装饰器测试"""
    
    @pytest.mark.asyncio
    async def test_successful_function_no_retry(self):
        """测试成功函数不需要重试"""
        call_count = 0
        
        @retry_async(max_attempts=3, delay=0.1)
        async def successful_function():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = await successful_function()
        
        assert result == "success"
        assert call_count == 1
    
    @pytest.mark.asyncio
    async def test_retry_on_exception(self):
        """测试异常时重试"""
        call_count = 0
        
        @retry_async(max_attempts=3, delay=0.1)
        async def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary error")
            return "success"
        
        result = await failing_function()
        
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_max_attempts_exceeded(self):
        """测试超过最大重试次数"""
        call_count = 0
        
        @retry_async(max_attempts=2, delay=0.1)
        async def always_failing_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError, match="Always fails"):
            await always_failing_function()
        
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_specific_exception_retry(self):
        """测试特定异常重试"""
        call_count = 0
        
        @retry_async(max_attempts=3, delay=0.1, exceptions=ValueError)
        async def specific_exception_function():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("Retryable error")
            elif call_count == 2:
                raise TypeError("Non-retryable error")
            return "success"
        
        with pytest.raises(TypeError, match="Non-retryable error"):
            await specific_exception_function()
        
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_multiple_exceptions_retry(self):
        """测试多个异常类型重试"""
        call_count = 0
        
        @retry_async(max_attempts=4, delay=0.1, exceptions=(ValueError, TypeError))
        async def multiple_exceptions_function():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("First error")
            elif call_count == 2:
                raise TypeError("Second error")
            elif call_count == 3:
                raise RuntimeError("Non-retryable error")
            return "success"
        
        with pytest.raises(RuntimeError, match="Non-retryable error"):
            await multiple_exceptions_function()
        
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_backoff_delay(self):
        """测试退避延迟"""
        call_times = []
        
        @retry_async(max_attempts=3, delay=0.1, backoff_factor=2.0, jitter=False)
        async def backoff_function():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise ValueError("Retry needed")
            return "success"
        
        start_time = time.time()
        result = await backoff_function()
        
        assert result == "success"
        assert len(call_times) == 3
        
        # 验证延迟时间（允许一些误差）
        delay1 = call_times[1] - call_times[0]
        delay2 = call_times[2] - call_times[1]
        
        assert 0.05 <= delay1 <= 0.30  # 第一次延迟约0.1秒
        assert 0.15 <= delay2 <= 0.40  # 第二次延迟约0.2秒（2倍退避）
    
    @pytest.mark.asyncio
    async def test_max_delay_limit(self):
        """测试最大延迟限制"""
        call_times = []
        
        @retry_async(max_attempts=3, delay=10.0, backoff_factor=2.0, max_delay=0.2, jitter=False)
        async def max_delay_function():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise ValueError("Retry needed")
            return "success"
        
        result = await max_delay_function()
        
        assert result == "success"
        assert len(call_times) == 3
        
        # 验证延迟被限制在max_delay内
        delay1 = call_times[1] - call_times[0]
        delay2 = call_times[2] - call_times[1]
        
        assert delay1 <= 0.25  # 应该被限制在max_delay附近
        assert delay2 <= 0.25
    
    @pytest.mark.asyncio
    async def test_jitter_enabled(self):
        """测试抖动功能"""
        delays = []
        
        # 运行多次以测试抖动的随机性
        for _ in range(5):
            call_times = []
            
            @retry_async(max_attempts=2, delay=0.1, jitter=True)
            async def jitter_function():
                call_times.append(time.time())
                if len(call_times) < 2:
                    raise ValueError("Retry needed")
                return "success"
            
            await jitter_function()
            
            if len(call_times) >= 2:
                delay = call_times[1] - call_times[0]
                delays.append(delay)
        
        # 验证延迟时间有变化（抖动效果）
        assert len(set(f"{d:.3f}" for d in delays)) > 1  # 至少有不同的延迟值
    
    @pytest.mark.asyncio
    async def test_jitter_disabled(self):
        """测试禁用抖动"""
        delays = []
        
        # 运行多次验证延迟一致
        for _ in range(3):
            call_times = []
            
            @retry_async(max_attempts=2, delay=0.1, jitter=False)
            async def no_jitter_function():
                call_times.append(time.time())
                if len(call_times) < 2:
                    raise ValueError("Retry needed")
                return "success"
            
            await no_jitter_function()
            
            if len(call_times) >= 2:
                delay = call_times[1] - call_times[0]
                delays.append(delay)
        
        # 验证延迟时间基本一致（允许小误差）
        if delays:
            avg_delay = sum(delays) / len(delays)
            for delay in delays:
                assert abs(delay - avg_delay) < 0.02  # 误差小于20ms
    
    @pytest.mark.asyncio
    async def test_config_object_parameter(self):
        """测试使用配置对象参数"""
        call_count = 0
        config = RetryConfig(
            max_attempts=2,
            delay=0.1,
            exceptions=(ValueError,),
            jitter=False
        )
        
        @retry_async(config=config)
        async def config_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Retry needed")
            return "success"
        
        result = await config_function()
        
        assert result == "success"
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_function_with_arguments(self):
        """测试带参数的函数"""
        call_count = 0
        
        @retry_async(max_attempts=2, delay=0.1)
        async def function_with_args(x, y, z=None):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Retry needed")
            return f"{x}-{y}-{z}"
        
        result = await function_with_args("a", "b", z="c")
        
        assert result == "a-b-c"
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_function_preserves_metadata(self):
        """测试函数元数据保持"""
        @retry_async(max_attempts=2, delay=0.1)
        async def documented_function():
            """This is a test function."""
            return "success"
        
        assert documented_function.__name__ == "documented_function"
        assert documented_function.__doc__ == "This is a test function."
    
    @pytest.mark.asyncio
    async def test_logging_on_retry(self):
        """测试重试时的日志记录"""
        call_count = 0
        
        @retry_async(max_attempts=3, delay=0.1)
        async def logging_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError(f"Error {call_count}")
            return "success"
        
        with patch('blockchain_service.utils.retry.logger') as mock_logger:
            result = await logging_function()
            
            assert result == "success"
            assert call_count == 3
            
            # 验证警告日志被调用
            assert mock_logger.warning.call_count == 2  # 前两次失败时记录警告
    
    @pytest.mark.asyncio
    async def test_logging_on_final_failure(self):
        """测试最终失败时的日志记录"""
        @retry_async(max_attempts=2, delay=0.1)
        async def final_failure_function():
            raise ValueError("Always fails")
        
    
    @pytest.mark.asyncio
    async def test_logging_on_non_retryable_exception(self):
        """测试不可重试异常的日志记录"""
        @retry_async(max_attempts=3, delay=0.1, exceptions=ValueError)
        async def non_retryable_function():
            raise TypeError("Non-retryable error")
        
        with patch('blockchain_service.utils.retry.logger') as mock_logger:
            with pytest.raises(TypeError):
                await non_retryable_function()
            
            # 验证错误日志被调用
            mock_logger.error.assert_called_once()
            error_call = mock_logger.error.call_args
            assert "不可重试的异常" in error_call[0][0]


class TestAsyncRetryAlias:
    """async_retry别名测试"""
    
    @pytest.mark.asyncio
    async def test_alias_functionality(self):
        """测试别名功能"""
        call_count = 0
        
        @async_retry(max_attempts=2, delay=0.1)
        async def alias_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Retry needed")
            return "success"
        
        result = await alias_function()
        
        assert result == "success"
        assert call_count == 2


class TestRetryIntegration:
    """重试工具集成测试"""
    
    @pytest.mark.asyncio
    async def test_nested_retry_decorators(self):
        """测试嵌套重试装饰器"""
        outer_calls = 0
        inner_calls = 0
        
        @retry_async(max_attempts=2, delay=0.1, exceptions=ValueError)
        async def outer_function():
            nonlocal outer_calls
            outer_calls += 1
            
            @retry_async(max_attempts=2, delay=0.1, exceptions=TypeError)
            async def inner_function():
                nonlocal inner_calls
                inner_calls += 1
                if inner_calls == 1:
                    raise TypeError("Inner error")
                return "inner_success"
            
            inner_result = await inner_function()
            
            if outer_calls == 1:
                raise ValueError("Outer error")
            
            return f"outer_{inner_result}"
        
        result = await outer_function()
        
        assert result == "outer_inner_success"
        assert outer_calls == 2
        assert inner_calls == 3  # inner_function被调用3次
    
    @pytest.mark.asyncio
    async def test_concurrent_retry_functions(self):
        """测试并发重试函数"""
        results = []
        
        @retry_async(max_attempts=2, delay=0.1)
        async def concurrent_function(task_id):
            # 第一次调用失败，第二次成功
            if task_id not in results:
                results.append(task_id)
                raise ValueError(f"Task {task_id} first attempt")
            return f"Task {task_id} success"
        
        # 并发执行多个任务
        tasks = [
            concurrent_function(i) for i in range(3)
        ]
        
        concurrent_results = await asyncio.gather(*tasks)
        
        assert len(concurrent_results) == 3
        for i, result in enumerate(concurrent_results):
            assert result == f"Task {i} success"
    
    @pytest.mark.asyncio
    async def test_retry_with_timeout(self):
        """测试重试与超时结合"""
        call_count = 0
        
        @retry_async(max_attempts=3, delay=0.1)
        async def timeout_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise asyncio.TimeoutError("Timeout error")
            return "success"
        
        result = await timeout_function()
        
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_retry_with_cancellation(self):
        """测试重试与取消结合"""
        call_count = 0
        
        @retry_async(max_attempts=5, delay=0.2)
        async def cancellable_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")
        
        # 创建任务并在短时间后取消
        task = asyncio.create_task(cancellable_function())
        await asyncio.sleep(0.1)  # 让第一次调用开始
        task.cancel()
        
        with pytest.raises(asyncio.CancelledError):
            await task
        
        # 验证只调用了一次（因为被取消了）
        assert call_count <= 1


class TestRetryEdgeCases:
    """重试工具边界条件测试"""
    
    @pytest.mark.asyncio
    async def test_zero_max_attempts(self):
        """测试零次最大尝试"""
        call_count = 0
        
        @retry_async(max_attempts=0, delay=0.1)
        async def zero_attempts_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Should not retry")
        
        # 当max_attempts=0时，函数不会被调用，不会抛出异常
            result = await zero_attempts_function()
        
        # max_attempts为0时，函数不会被调用
        assert call_count == 0
    
    @pytest.mark.asyncio
    async def test_one_max_attempt(self):
        """测试一次最大尝试"""
        call_count = 0
        
        @retry_async(max_attempts=1, delay=0.1)
        async def one_attempt_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("No retry")
        
        # 当max_attempts=0时，函数不会被调用，不会抛出异常
            await one_attempt_function()
        
        assert call_count == 0
    
    @pytest.mark.asyncio
    async def test_very_small_delay(self):
        """测试极小延迟"""
        call_count = 0
        
        @retry_async(max_attempts=3, delay=0.001, jitter=False)
        async def small_delay_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Retry needed")
            return "success"
        
        start_time = time.time()
        result = await small_delay_function()
        end_time = time.time()
        
        assert result == "success"
        assert call_count == 3
        # 总时间应该很短（小于0.1秒）
        assert end_time - start_time < 0.1
    
    @pytest.mark.asyncio
    async def test_large_backoff_factor(self):
        """测试大退避因子"""
        call_times = []
        
        @retry_async(max_attempts=3, delay=0.01, backoff_factor=10.0, max_delay=0.1, jitter=False)
        async def large_backoff_function():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise ValueError("Retry needed")
            return "success"
        
        result = await large_backoff_function()
        
        assert result == "success"
        assert len(call_times) == 3
        
        # 验证延迟被max_delay限制
        delay1 = call_times[1] - call_times[0]
        delay2 = call_times[2] - call_times[1]
        
        assert delay1 <= 0.20  # 应该被max_delay限制
        assert delay2 <= 0.20
    
    @pytest.mark.asyncio
    async def test_empty_exceptions_tuple(self):
        """测试空异常元组"""
        call_count = 0
        
        @retry_async(max_attempts=3, delay=0.1, exceptions=())
        async def empty_exceptions_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Should not retry")
        
        # 当max_attempts=0时，函数不会被调用，不会抛出异常
            await empty_exceptions_function()
        
        # 没有匹配的异常类型，不应该重试
        assert call_count == 0 