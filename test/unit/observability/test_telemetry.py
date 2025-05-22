#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
遥测模块单元测试
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import logging

from internal.observability.telemetry import (
    setup_telemetry,
    create_tracer,
    get_tracer,
    trace,
    record_exception,
    add_span_attributes
)


class TestTelemetry:
    """遥测模块测试"""
    
    def setup_method(self):
        """测试前设置"""
        # 清理可能的全局状态
        import sys
        if 'internal.observability.telemetry' in sys.modules:
            module = sys.modules['internal.observability.telemetry']
            if hasattr(module, '_tracer'):
                delattr(module, '_tracer')
    
    def test_setup_telemetry(self):
        """测试遥测设置"""
        with patch('opentelemetry.sdk.trace.TracerProvider') as mock_provider_cls, \
             patch('opentelemetry.sdk.trace.export.BatchSpanProcessor') as mock_processor_cls, \
             patch('opentelemetry.sdk.trace.export.ConsoleSpanExporter') as mock_console_exporter, \
             patch('opentelemetry.sdk.trace.export.OTLPSpanExporter') as mock_otlp_exporter, \
             patch('opentelemetry.trace.set_tracer_provider') as mock_set_provider:
            
            # 设置模拟返回值
            mock_provider = MagicMock()
            mock_provider_cls.return_value = mock_provider
            
            # 调用函数
            setup_telemetry(
                service_name="test-service",
                service_version="1.0.0",
                environment="test",
                otlp_endpoint="http://localhost:4317"
            )
            
            # 验证调用
            mock_provider_cls.assert_called_once()
            mock_processor_cls.assert_called()
            mock_set_provider.assert_called_once_with(mock_provider)
            mock_provider.add_span_processor.assert_called()
    
    def test_create_tracer(self):
        """测试创建追踪器"""
        with patch('opentelemetry.trace.get_tracer_provider') as mock_get_provider, \
             patch('opentelemetry.trace.get_tracer') as mock_get_tracer:
            
            # 设置模拟返回值
            mock_provider = MagicMock()
            mock_get_provider.return_value = mock_provider
            mock_tracer = MagicMock()
            mock_get_tracer.return_value = mock_tracer
            
            # 调用函数
            tracer = create_tracer("test-module")
            
            # 验证调用
            mock_get_provider.assert_called_once()
            mock_get_tracer.assert_called_once()
            assert tracer == mock_tracer
    
    def test_get_tracer(self):
        """测试获取追踪器 - 初次调用"""
        with patch('internal.observability.telemetry.create_tracer') as mock_create_tracer:
            # 设置模拟返回值
            mock_tracer = MagicMock()
            mock_create_tracer.return_value = mock_tracer
            
            # 调用函数
            tracer = get_tracer()
            
            # 验证调用
            mock_create_tracer.assert_called_once()
            assert tracer == mock_tracer
    
    def test_get_tracer_cached(self):
        """测试获取追踪器 - 缓存命中"""
        with patch('internal.observability.telemetry.create_tracer') as mock_create_tracer:
            # 设置模拟返回值
            mock_tracer = MagicMock()
            
            # 手动设置缓存
            import internal.observability.telemetry as telemetry
            telemetry._tracer = mock_tracer
            
            # 调用函数
            tracer = get_tracer()
            
            # 验证调用
            mock_create_tracer.assert_not_called()
            assert tracer == mock_tracer
    
    def test_trace_decorator(self):
        """测试追踪装饰器 - 同步函数"""
        with patch('internal.observability.telemetry.get_tracer') as mock_get_tracer:
            # 设置模拟返回值
            mock_tracer = MagicMock()
            mock_span = MagicMock()
            mock_context = MagicMock()
            mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span
            mock_get_tracer.return_value = mock_tracer
            
            # 创建被装饰函数
            @trace("test_operation")
            def test_function(a, b, c=3):
                return a + b + c
            
            # 调用函数
            result = test_function(1, 2, c=4)
            
            # 验证调用
            mock_get_tracer.assert_called_once()
            mock_tracer.start_as_current_span.assert_called_once_with("test_operation")
            mock_span.set_attribute.assert_called()
            assert result == 7  # 1 + 2 + 4
    
    @pytest.mark.asyncio
    async def test_trace_decorator_async(self):
        """测试追踪装饰器 - 异步函数"""
        with patch('internal.observability.telemetry.get_tracer') as mock_get_tracer:
            # 设置模拟返回值
            mock_tracer = MagicMock()
            mock_span = MagicMock()
            mock_context = MagicMock()
            mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span
            mock_get_tracer.return_value = mock_tracer
            
            # 创建被装饰函数
            @trace("test_async_operation")
            async def test_async_function(a, b):
                return a * b
            
            # 调用函数
            result = await test_async_function(5, 6)
            
            # 验证调用
            mock_get_tracer.assert_called_once()
            mock_tracer.start_as_current_span.assert_called_once_with("test_async_operation")
            mock_span.set_attribute.assert_called()
            assert result == 30  # 5 * 6
    
    def test_record_exception(self):
        """测试记录异常"""
        with patch('opentelemetry.trace.get_current_span') as mock_get_span:
            # 设置模拟返回值
            mock_span = MagicMock()
            mock_get_span.return_value = mock_span
            
            # 创建异常
            test_exception = ValueError("测试异常")
            
            # 调用函数
            record_exception(test_exception)
            
            # 验证调用
            mock_get_span.assert_called_once()
            mock_span.record_exception.assert_called_once_with(test_exception)
    
    def test_add_span_attributes(self):
        """测试添加Span属性"""
        with patch('opentelemetry.trace.get_current_span') as mock_get_span:
            # 设置模拟返回值
            mock_span = MagicMock()
            mock_get_span.return_value = mock_span
            
            # 调用函数
            add_span_attributes({"key1": "value1", "key2": 123})
            
            # 验证调用
            mock_get_span.assert_called_once()
            assert mock_span.set_attribute.call_count == 2 