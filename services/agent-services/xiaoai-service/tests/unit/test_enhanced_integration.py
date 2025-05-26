#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版服务集成测试
验证断路器、限流、追踪等功能
"""

import asyncio
import pytest
import time
from typing import List

# 添加项目根目录到Python路径
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# 导入被测试的组件
try:
    from xiaoai.resilience.circuit_breaker import (
        CircuitBreakerConfig, get_circuit_breaker, CircuitBreakerOpenError
    )
    from xiaoai.resilience.rate_limiter import (
        RateLimitConfig, get_rate_limiter, RateLimitExceededError
    )
    from xiaoai.observability.tracing import get_tracer, SpanKind
    from xiaoai.service.enhanced_diagnosis_service import (
        get_diagnosis_service, DiagnosisRequest
    )
except ImportError as e:
    # 如果导入失败，创建模拟类
    print(f"导入失败，使用模拟类: {e}")
    
    class CircuitBreakerConfig:
        def __init__(self, **kwargs):
            pass
    
    class CircuitBreakerOpenError(Exception):
        pass
    
    class RateLimitConfig:
        def __init__(self, **kwargs):
            pass
    
    class RateLimitExceededError(Exception):
        pass
    
    class DiagnosisRequest:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    async def get_circuit_breaker(name, config):
        return None
    
    async def get_rate_limiter(name, type_name, config):
        return None
    
    async def get_diagnosis_service():
        return None
    
    def get_tracer(name):
        return None

class TestEnhancedDiagnosisService:
    """增强版诊断服务测试"""
    
    @pytest.mark.asyncio
    async def test_basic_diagnosis(self):
        """测试基本诊断功能"""
        service = await get_diagnosis_service()
        
        request = DiagnosisRequest(
            user_id="test_user_001",
            symptoms=["头痛", "发热", "咳嗽"],
            vital_signs={"temperature": 38.5, "heart_rate": 90}
        )
        
        result = await service.diagnose(request)
        
        assert result.user_id == "test_user_001"
        assert result.primary_diagnosis is not None
        assert len(result.differential_diagnoses) > 0
        assert 0 <= result.confidence_score <= 1
        assert len(result.recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_cache_functionality(self):
        """测试缓存功能"""
        service = await get_diagnosis_service()
        
        request = DiagnosisRequest(
            user_id="test_user_002",
            symptoms=["头痛", "发热"]
        )
        
        # 第一次请求
        start_time = time.time()
        result1 = await service.diagnose(request)
        first_duration = time.time() - start_time
        
        # 第二次相同请求（应该命中缓存）
        start_time = time.time()
        result2 = await service.diagnose(request)
        second_duration = time.time() - start_time
        
        # 验证缓存命中
        assert result1.diagnosis_id == result2.diagnosis_id
        assert second_duration < first_duration  # 缓存应该更快
        assert service.stats['cache_hits'] > 0
    
    @pytest.mark.asyncio
    async def test_emergency_priority(self):
        """测试紧急优先级处理"""
        service = await get_diagnosis_service()
        
        emergency_request = DiagnosisRequest(
            user_id="test_user_003",
            symptoms=["胸痛", "呼吸困难"],
            priority="emergency"
        )
        
        result = await service.diagnose(emergency_request)
        
        assert result.user_id == "test_user_003"
        assert result.follow_up_required is True
    
    @pytest.mark.asyncio
    async def test_parallel_processing(self):
        """测试并行处理能力"""
        service = await get_diagnosis_service()
        
        # 创建多个并发请求
        requests = [
            DiagnosisRequest(
                user_id=f"test_user_{i:03d}",
                symptoms=["症状1", "症状2"],
                vital_signs={"temperature": 37.0 + i * 0.1}
            )
            for i in range(10)
        ]
        
        # 并发执行
        start_time = time.time()
        results = await asyncio.gather(*[
            service.diagnose(req) for req in requests
        ])
        total_time = time.time() - start_time
        
        # 验证结果
        assert len(results) == 10
        assert all(result.user_id.startswith("test_user_") for result in results)
        
        # 并发处理应该比串行处理快
        assert total_time < 2.0  # 假设串行需要更长时间

class TestCircuitBreaker:
    """断路器测试"""
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_normal_operation(self):
        """测试断路器正常操作"""
        config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=1.0,
            timeout=0.5
        )
        
        breaker = await get_circuit_breaker("test_normal", config)
        
        # 正常操作
        async with breaker.protect():
            await asyncio.sleep(0.1)
        
        assert breaker.state.value == "closed"
        assert breaker.failure_count == 0
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_failure_handling(self):
        """测试断路器故障处理"""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            recovery_timeout=1.0,
            timeout=0.5
        )
        
        breaker = await get_circuit_breaker("test_failure", config)
        
        # 模拟失败
        for i in range(3):
            try:
                async with breaker.protect():
                    raise Exception(f"模拟失败 {i}")
            except Exception:
                pass
        
        # 断路器应该打开
        assert breaker.state.value == "open"
        
        # 下一次调用应该快速失败
        with pytest.raises(CircuitBreakerOpenError):
            async with breaker.protect():
                pass

class TestRateLimiter:
    """限流器测试"""
    
    @pytest.mark.asyncio
    async def test_token_bucket_rate_limiter(self):
        """测试令牌桶限流器"""
        config = RateLimitConfig(rate=5.0, burst=10)
        limiter = await get_rate_limiter("test_token_bucket", "token_bucket", config)
        
        # 快速消耗令牌
        success_count = 0
        for i in range(15):
            if await limiter.try_acquire():
                success_count += 1
        
        # 应该有一些请求被限流
        assert success_count <= 10  # 不应该超过突发容量
        assert limiter.get_stats()['rejected_requests'] > 0
    
    @pytest.mark.asyncio
    async def test_rate_limiter_recovery(self):
        """测试限流器恢复"""
        config = RateLimitConfig(rate=10.0, burst=5)
        limiter = await get_rate_limiter("test_recovery", "token_bucket", config)
        
        # 消耗所有令牌
        for i in range(5):
            await limiter.try_acquire()
        
        # 等待令牌恢复
        await asyncio.sleep(0.6)  # 等待令牌补充
        
        # 应该能够再次获取令牌
        assert await limiter.try_acquire() is True

class TestTracing:
    """追踪测试"""
    
    @pytest.mark.asyncio
    async def test_basic_tracing(self):
        """测试基本追踪功能"""
        tracer = get_tracer("test_service")
        
        async with tracer.trace("test_operation") as span:
            span.set_tag("test.key", "test.value")
            span.add_event("test_event", {"event_data": "test"})
            await asyncio.sleep(0.1)
        
        # 验证span信息
        finished_spans = tracer.get_finished_spans()
        assert len(finished_spans) > 0
        
        span = finished_spans[-1]
        assert span.operation_name == "test_operation"
        assert span.tags["test.key"] == "test.value"
        assert len(span.events) > 0
        assert span.duration is not None
    
    @pytest.mark.asyncio
    async def test_nested_tracing(self):
        """测试嵌套追踪"""
        tracer = get_tracer("test_service")
        
        async with tracer.trace("parent_operation") as parent_span:
            async with tracer.trace(
                "child_operation", 
                parent_context=parent_span.context
            ) as child_span:
                child_span.set_tag("child.tag", "child.value")
                await asyncio.sleep(0.05)
        
        finished_spans = tracer.get_finished_spans()
        
        # 找到父子span
        parent_spans = [s for s in finished_spans if s.operation_name == "parent_operation"]
        child_spans = [s for s in finished_spans if s.operation_name == "child_operation"]
        
        assert len(parent_spans) > 0
        assert len(child_spans) > 0
        
        parent_span = parent_spans[-1]
        child_span = child_spans[-1]
        
        # 验证父子关系
        assert child_span.context.parent_span_id == parent_span.context.span_id
        assert child_span.context.trace_id == parent_span.context.trace_id

class TestIntegration:
    """集成测试"""
    
    @pytest.mark.asyncio
    async def test_full_diagnosis_flow(self):
        """测试完整诊断流程"""
        service = await get_diagnosis_service()
        
        # 创建复杂的诊断请求
        request = DiagnosisRequest(
            user_id="integration_test_user",
            symptoms=["头痛", "发热", "咳嗽", "乏力"],
            medical_history={
                "allergies": ["青霉素"],
                "chronic_conditions": ["高血压"],
                "medications": ["降压药"]
            },
            vital_signs={
                "temperature": 38.2,
                "heart_rate": 95,
                "systolic_bp": 145,
                "diastolic_bp": 90
            },
            images=["chest_xray.jpg"],
            priority="urgent"
        )
        
        # 执行诊断
        result = await service.diagnose(request)
        
        # 验证结果完整性
        assert result.user_id == "integration_test_user"
        assert result.diagnosis_id is not None
        assert result.primary_diagnosis is not None
        assert len(result.differential_diagnoses) > 0
        assert 0 <= result.confidence_score <= 1
        assert len(result.recommendations) > 0
        assert result.timestamp > 0
        
        # 验证服务统计
        stats = service.get_health_status()
        assert stats['status'] == 'healthy'
        assert stats['stats']['total_requests'] > 0
        assert stats['stats']['successful_diagnoses'] > 0
    
    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self):
        """测试错误处理和恢复"""
        service = await get_diagnosis_service()
        
        # 测试无效请求
        invalid_request = DiagnosisRequest(
            user_id="",  # 无效用户ID
            symptoms=[]  # 空症状列表
        )
        
        # 应该能够处理无效请求而不崩溃
        try:
            await service.diagnose(invalid_request)
        except Exception as e:
            # 预期会有异常，但服务应该保持稳定
            assert service.stats['failed_diagnoses'] > 0
        
        # 验证服务仍然可以处理正常请求
        valid_request = DiagnosisRequest(
            user_id="recovery_test_user",
            symptoms=["头痛"]
        )
        
        result = await service.diagnose(valid_request)
        assert result.user_id == "recovery_test_user"

# 运行测试的辅助函数
async def run_performance_test():
    """性能测试"""
    service = await get_diagnosis_service()
    
    # 创建大量并发请求
    requests = [
        DiagnosisRequest(
            user_id=f"perf_test_user_{i:04d}",
            symptoms=["症状1", "症状2", "症状3"],
            vital_signs={"temperature": 37.0 + (i % 10) * 0.1}
        )
        for i in range(100)
    ]
    
    start_time = time.time()
    
    # 分批处理以避免过载
    batch_size = 10
    results = []
    
    for i in range(0, len(requests), batch_size):
        batch = requests[i:i + batch_size]
        batch_results = await asyncio.gather(*[
            service.diagnose(req) for req in batch
        ])
        results.extend(batch_results)
        
        # 短暂休息以模拟真实场景
        await asyncio.sleep(0.1)
    
    total_time = time.time() - start_time
    
    print(f"性能测试结果:")
    print(f"  总请求数: {len(requests)}")
    print(f"  总耗时: {total_time:.2f}秒")
    print(f"  平均响应时间: {total_time / len(requests):.3f}秒")
    print(f"  QPS: {len(requests) / total_time:.2f}")
    
    # 验证结果
    assert len(results) == len(requests)
    assert all(result.user_id.startswith("perf_test_user_") for result in results)
    
    # 打印服务统计
    stats = service.get_health_status()
    print(f"  服务统计: {stats['stats']}")

if __name__ == "__main__":
    # 运行性能测试
    asyncio.run(run_performance_test()) 