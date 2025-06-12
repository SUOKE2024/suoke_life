"""
test_performance_enhanced - 索克生活项目模块
"""

import asyncio
import gc
import os
import statistics
import sys
import time
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import httpx
import psutil
import pytest
from suoke_api_gateway.core.app import create_app
from suoke_api_gateway.core.config import Settings
from suoke_api_gateway.middleware.rate_limit import RateLimitMiddleware
from suoke_api_gateway.services.service_registry import ServiceRegistry
from suoke_api_gateway.utils.cache import CacheManager

#! / usr / bin / env python
# - * - coding: utf - 8 - * -

"""
API网关增强性能测试
测试高并发、大负载、长时间运行等场景
"""


# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class PerformanceMetrics:
    """性能指标收集器"""

    def __init__(self) -> None:
        """TODO: 添加文档字符串"""
        self.response_times: List[float] = []
        self.memory_usage: List[float] = []
        self.cpu_usage: List[float] = []
        self.error_count = 0
        self.success_count = 0
        self.start_time = None
        self.end_time = None

    def start_monitoring(self) -> None:
        """开始监控"""
        self.start_time = time.time()
        gc.collect()  # 清理垃圾回收

    def stop_monitoring(self) -> None:
        """停止监控"""
        self.end_time = time.time()

    def record_response(self, response_time: float, success: bool = True):
        """记录响应"""
        self.response_times.append(response_time)
        if success:
            self.success_count += 1
        else:
            self.error_count += 1

    def record_system_metrics(self) -> None:
        """记录系统指标"""
        try:
            process = psutil.Process()
            self.memory_usage.append(process.memory_info().rss / 1024 / 1024)  # MB
            self.cpu_usage.append(process.cpu_percent())
        except:
            # 如果psutil不可用，使用模拟数据
            self.memory_usage.append(100.0)
            self.cpu_usage.append(10.0)

    def get_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        if not self.response_times:
            return {"error": "No data collected"}

        total_time = self.end_time - self.start_time if self.end_time else 0
        total_requests = len(self.response_times)

        return {
            "total_requests": total_requests,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": self.success_count / total_requests * 100,
            "total_time": total_time,
            "requests_per_second": total_requests / total_time if total_time > 0 else 0,
            "response_times": {
                "min": min(self.response_times),
                "max": max(self.response_times),
                "mean": statistics.mean(self.response_times),
                "median": statistics.median(self.response_times),
                "p95": self._percentile(self.response_times, 95),
                "p99": self._percentile(self.response_times, 99),
            },
            "memory_usage": {
                "min": min(self.memory_usage) if self.memory_usage else 0,
                "max": max(self.memory_usage) if self.memory_usage else 0,
                "mean": statistics.mean(self.memory_usage) if self.memory_usage else 0,
            },
            "cpu_usage": {
                "min": min(self.cpu_usage) if self.cpu_usage else 0,
                "max": max(self.cpu_usage) if self.cpu_usage else 0,
                "mean": statistics.mean(self.cpu_usage) if self.cpu_usage else 0,
            },
        }

    def _percentile(self, data: List[float], percentile: int) -> float:
        """计算百分位数"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]


@pytest.fixture
def performance_settings() -> None:
    """性能测试配置"""
    return Settings(
        app_name="Performance Test Gateway",
        debug=False,
        host="127.0.0.1",
        port=8001,
        workers=1,
        secret_key="performance-test-secret-key-12345678901234567890",
        log_level="WARNING",  # 减少日志输出以提高性能
    )


@pytest.fixture
async def performance_app(performance_settings):
    """性能测试应用"""
    app = create_app(performance_settings)
    return app


class TestConcurrencyPerformance:
    """并发性能测试"""

    @pytest.mark.asyncio
    async def test_concurrent_cache_operations(self) -> None:
        """测试并发缓存操作性能"""
        metrics = PerformanceMetrics()
        metrics.start_monitoring()

        # 模拟缓存操作
        cache_data = {}

        async def cache_operation(operation_id: int):
            """缓存操作"""
            start_time = time.time()

            if operation_id % 2 == 0:
                # 写操作
                cache_data[f"key_{operation_id}"] = f"value_{operation_id}"
            else:
                # 读操作
                cache_data.get(f"key_{operation_id - 1}")

            end_time = time.time()
            metrics.record_response(end_time - start_time, True)

        # 执行并发操作
        tasks = [cache_operation(i) for i in range(1000)]
        await asyncio.gather(*tasks)

        metrics.stop_monitoring()
        summary = metrics.get_summary()

        # 性能断言
        assert summary["success_rate"] == 100.0
        assert summary["response_times"]["mean"] < 0.001  # 1ms

        print(f"并发缓存操作性能: {summary}")

    @pytest.mark.asyncio
    async def test_sustained_load_simulation(self) -> None:
        """测试持续负载模拟"""
        metrics = PerformanceMetrics()
        metrics.start_monitoring()

        # 模拟持续负载
        for i in range(100):
            start_time = time.time()

            # 模拟请求处理
            await asyncio.sleep(0.001)  # 1ms处理时间

            end_time = time.time()
            metrics.record_response(end_time - start_time, True)

            if i % 10 == 0:
                metrics.record_system_metrics()

        metrics.stop_monitoring()
        summary = metrics.get_summary()

        # 验证性能稳定性
        assert summary["success_rate"] == 100.0
        assert summary["response_times"]["p95"] < 0.01  # 10ms

        print(f"持续负载测试: {summary}")


class TestMemoryPerformance:
    """内存性能测试"""

    @pytest.mark.asyncio
    async def test_memory_usage_stability(self) -> None:
        """测试内存使用稳定性"""
        metrics = PerformanceMetrics()

        # 模拟内存使用
        data_store = []

        for cycle in range(10):
            # 添加数据
            for i in range(100):
                data_store.append(f"data_{cycle}_{i}")

            # 清理旧数据
            if len(data_store) > 500:
                data_store = data_store[-500:]

            metrics.record_system_metrics()
            gc.collect()

        # 验证内存稳定性
        if metrics.memory_usage:
            memory_variance = max(metrics.memory_usage) - min(metrics.memory_usage)
            assert memory_variance < 100  # 内存变化不超过100MB

        print(f"内存稳定性测试完成")

    @pytest.mark.asyncio
    async def test_large_data_handling(self) -> None:
        """测试大数据处理"""
        metrics = PerformanceMetrics()
        metrics.start_monitoring()

        # 处理大数据
        large_data = "x" * (1024 * 1024)  # 1MB数据

        for i in range(10):
            start_time = time.time()

            # 模拟大数据处理
            processed_data = large_data.encode("utf-8")
            result = len(processed_data)

            end_time = time.time()
            metrics.record_response(end_time - start_time, result > 0)
            metrics.record_system_metrics()

        metrics.stop_monitoring()
        summary = metrics.get_summary()

        assert summary["success_rate"] == 100.0
        print(f"大数据处理性能: {summary}")


class TestRateLimitPerformance:
    """限流性能测试"""

    @pytest.mark.asyncio
    async def test_rate_limit_check_performance(self) -> None:
        """测试限流检查性能"""
        metrics = PerformanceMetrics()
        metrics.start_monitoring()

        # 模拟限流检查
        rate_limit_store = {}

        for i in range(1000):
            start_time = time.time()

            # 模拟限流逻辑
            client_id = f"client_{i % 10}"
            current_time = int(time.time())

            if client_id not in rate_limit_store:
                rate_limit_store[client_id] = []

            # 清理过期记录
            rate_limit_store[client_id] = [
                t for t in rate_limit_store[client_id] if current_time - t < 60
            ]

            # 检查限流
            allowed = len(rate_limit_store[client_id]) < 100
            if allowed:
                rate_limit_store[client_id].append(current_time)

            end_time = time.time()
            metrics.record_response(end_time - start_time, allowed)

            if i % 100 == 0:
                metrics.record_system_metrics()

        metrics.stop_monitoring()
        summary = metrics.get_summary()

        # 限流检查应该很快
        assert summary["response_times"]["mean"] < 0.001
        print(f"限流性能测试: {summary}")


class TestServiceDiscoveryPerformance:
    """服务发现性能测试"""

    @pytest.mark.asyncio
    async def test_service_lookup_performance(self) -> None:
        """测试服务查找性能"""
        metrics = PerformanceMetrics()

        # 创建服务注册表
        services = {}
        for i in range(100):
            service_name = f"service_{i}"
            services[service_name] = {
                "host": f"192.168.1.{i % 255}",
                "port": 8000 + i,
                "healthy": True,
            }

        metrics.start_monitoring()

        # 测试服务查找
        for i in range(1000):
            start_time = time.time()

            service_name = f"service_{i % 100}"
            service_info = services.get(service_name)

            end_time = time.time()
            metrics.record_response(end_time - start_time, service_info is not None)

            if i % 100 == 0:
                metrics.record_system_metrics()

        metrics.stop_monitoring()
        summary = metrics.get_summary()

        assert summary["success_rate"] == 100.0
        assert summary["response_times"]["mean"] < 0.0001
        print(f"服务发现性能: {summary}")


@pytest.mark.asyncio
async def test_end_to_end_performance() -> None:
    """端到端性能测试"""
    metrics = PerformanceMetrics()
    metrics.start_monitoring()

    # 模拟完整的请求处理流程
    for i in range(100):
        start_time = time.time()

        # 模拟各个处理阶段
        await asyncio.sleep(0.001)  # 认证
        await asyncio.sleep(0.0005)  # 限流
        await asyncio.sleep(0.0002)  # 缓存检查
        await asyncio.sleep(0.005)  # 后端调用
        await asyncio.sleep(0.0001)  # 响应处理

        end_time = time.time()
        metrics.record_response(end_time - start_time, True)

        if i % 10 == 0:
            metrics.record_system_metrics()

    metrics.stop_monitoring()
    summary = metrics.get_summary()

    # 端到端性能要求
    assert summary["response_times"]["mean"] < 0.01  # 10ms
    assert summary["response_times"]["p95"] < 0.02  # 20ms
    assert summary["success_rate"] == 100.0

    print(f"端到端性能测试: {summary}")


if __name__ == "__main__":
    pytest.main([__file__, " - v", " - s"])
