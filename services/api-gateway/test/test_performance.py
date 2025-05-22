#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API网关性能测试
"""

import asyncio
import os
import sys
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Tuple

import pytest
import requests
from fastapi import FastAPI
from fastapi.testclient import TestClient

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from internal.model.config import GatewayConfig, RouteConfig, CacheConfig, RateLimitConfig
from internal.delivery.rest.routes import setup_routes
from internal.service.service_registry import ServiceRegistry


class PerformanceTest:
    """性能测试基类"""
    
    def __init__(self, client: TestClient, endpoint: str, concurrent_users: int = 10, request_count: int = 100):
        """
        初始化性能测试
        
        Args:
            client: 测试客户端
            endpoint: 测试端点
            concurrent_users: 并发用户数
            request_count: 请求总数
        """
        self.client = client
        self.endpoint = endpoint
        self.concurrent_users = concurrent_users
        self.request_count = request_count
        self.response_times = []
        self.success_count = 0
        self.error_count = 0
        self.status_codes = {}
    
    def make_request(self) -> float:
        """
        发送单个请求并测量响应时间
        
        Returns:
            响应时间（秒）
        """
        start_time = time.time()
        
        try:
            response = self.client.get(self.endpoint)
            elapsed = time.time() - start_time
            
            # 记录结果
            self.response_times.append(elapsed)
            
            # 记录状态码
            status_code = response.status_code
            self.status_codes[status_code] = self.status_codes.get(status_code, 0) + 1
            
            # 判断成功/失败
            if 200 <= status_code < 300:
                self.success_count += 1
            else:
                self.error_count += 1
                
            return elapsed
        except Exception as e:
            elapsed = time.time() - start_time
            self.response_times.append(elapsed)
            self.error_count += 1
            return elapsed
    
    def run(self) -> Dict[str, Any]:
        """
        运行性能测试
        
        Returns:
            测试结果统计
        """
        start_time = time.time()
        
        # 使用线程池模拟并发用户
        with ThreadPoolExecutor(max_workers=self.concurrent_users) as executor:
            # 提交所有请求
            futures = [executor.submit(self.make_request) for _ in range(self.request_count)]
            
            # 等待所有请求完成
            for future in futures:
                future.result()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 计算统计数据
        if self.response_times:
            avg_response_time = statistics.mean(self.response_times)
            min_response_time = min(self.response_times)
            max_response_time = max(self.response_times)
            p50_response_time = statistics.median(self.response_times)
            p95_response_time = sorted(self.response_times)[int(len(self.response_times) * 0.95)]
            p99_response_time = sorted(self.response_times)[int(len(self.response_times) * 0.99)]
        else:
            avg_response_time = min_response_time = max_response_time = 0
            p50_response_time = p95_response_time = p99_response_time = 0
        
        # 计算请求吞吐量（每秒请求数）
        throughput = self.request_count / total_time if total_time > 0 else 0
        
        # 计算成功率
        success_rate = (self.success_count / self.request_count) * 100 if self.request_count > 0 else 0
        
        # 返回结果统计
        return {
            "endpoint": self.endpoint,
            "concurrent_users": self.concurrent_users,
            "request_count": self.request_count,
            "total_time": total_time,
            "throughput": throughput,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": success_rate,
            "status_codes": self.status_codes,
            "avg_response_time": avg_response_time,
            "min_response_time": min_response_time,
            "max_response_time": max_response_time,
            "p50_response_time": p50_response_time,
            "p95_response_time": p95_response_time,
            "p99_response_time": p99_response_time
        }


class TestGatewayPerformance:
    """API网关性能测试类"""
    
    @pytest.fixture
    def app(self):
        """创建测试FastAPI应用"""
        return FastAPI()
    
    @pytest.fixture
    def config(self):
        """创建网关配置"""
        return GatewayConfig(
            routes=[
                RouteConfig(
                    name="test-service",
                    prefix="/api/test/",
                    service="test-service",
                    methods=["GET", "POST"],
                    auth_required=False
                )
            ],
            cache=CacheConfig(
                enabled=True,
                ttl=60,
                max_size=1000
            ),
            middleware=GatewayConfig().middleware.copy(
                update={
                    "rate_limit": RateLimitConfig(
                        enabled=True,
                        max_requests=100,
                        reset_interval=60
                    )
                }
            )
        )
    
    @pytest.fixture
    def service_registry(self):
        """创建服务注册表"""
        registry = MagicMock(spec=ServiceRegistry)
        registry.get_endpoint.return_value = ("localhost", 8000)
        return registry
    
    @pytest.fixture
    def client(self, app, config, service_registry):
        """创建测试客户端"""
        from internal.delivery.rest.routes import setup_routes
        
        # 设置路由
        setup_routes(app, config)
        
        # 添加mock服务端点
        @app.get("/api/test/user/{user_id}")
        def get_user(user_id: str):
            # 模拟服务处理时间
            time.sleep(0.01)  # 10ms
            return {"user_id": user_id, "name": f"User {user_id}"}
        
        @app.get("/health")
        def health_check():
            return {"status": "ok"}
        
        # 设置应用状态
        app.state.registry = service_registry
        app.state.config = config
        
        return TestClient(app)
    
    @pytest.mark.skip(reason="性能测试通常在本地或CI环境中单独运行，而不是随单元测试一起运行")
    def test_health_endpoint_performance(self, client):
        """测试健康检查端点性能"""
        test = PerformanceTest(
            client=client,
            endpoint="/health",
            concurrent_users=10,
            request_count=1000
        )
        
        results = test.run()
        
        # 打印结果
        print("\n健康检查端点性能测试结果:")
        print(f"并发用户数: {results['concurrent_users']}")
        print(f"请求总数: {results['request_count']}")
        print(f"总执行时间: {results['total_time']:.2f}秒")
        print(f"吞吐量: {results['throughput']:.2f}请求/秒")
        print(f"成功率: {results['success_rate']:.2f}%")
        print(f"平均响应时间: {results['avg_response_time'] * 1000:.2f}ms")
        print(f"最小响应时间: {results['min_response_time'] * 1000:.2f}ms")
        print(f"最大响应时间: {results['max_response_time'] * 1000:.2f}ms")
        print(f"50%响应时间: {results['p50_response_time'] * 1000:.2f}ms")
        print(f"95%响应时间: {results['p95_response_time'] * 1000:.2f}ms")
        print(f"99%响应时间: {results['p99_response_time'] * 1000:.2f}ms")
        print(f"状态码分布: {results['status_codes']}")
        
        # 验证基本性能指标
        assert results['success_rate'] > 95, "成功率应高于95%"
        assert results['avg_response_time'] < 0.1, "平均响应时间应小于100ms"
        assert results['p95_response_time'] < 0.2, "95%响应时间应小于200ms"
    
    @pytest.mark.skip(reason="性能测试通常在本地或CI环境中单独运行，而不是随单元测试一起运行")
    def test_api_endpoint_performance(self, client):
        """测试API端点性能"""
        test = PerformanceTest(
            client=client,
            endpoint="/api/test/user/123",
            concurrent_users=10,
            request_count=100
        )
        
        results = test.run()
        
        # 打印结果
        print("\nAPI端点性能测试结果:")
        print(f"并发用户数: {results['concurrent_users']}")
        print(f"请求总数: {results['request_count']}")
        print(f"总执行时间: {results['total_time']:.2f}秒")
        print(f"吞吐量: {results['throughput']:.2f}请求/秒")
        print(f"成功率: {results['success_rate']:.2f}%")
        print(f"平均响应时间: {results['avg_response_time'] * 1000:.2f}ms")
        print(f"最小响应时间: {results['min_response_time'] * 1000:.2f}ms")
        print(f"最大响应时间: {results['max_response_time'] * 1000:.2f}ms")
        print(f"50%响应时间: {results['p50_response_time'] * 1000:.2f}ms")
        print(f"95%响应时间: {results['p95_response_time'] * 1000:.2f}ms")
        print(f"99%响应时间: {results['p99_response_time'] * 1000:.2f}ms")
        print(f"状态码分布: {results['status_codes']}")
        
        # 验证基本性能指标
        assert results['success_rate'] > 95, "成功率应高于95%"
        assert results['avg_response_time'] < 0.1, "平均响应时间应小于100ms"
        assert results['p95_response_time'] < 0.2, "95%响应时间应小于200ms"
    
    @pytest.mark.skip(reason="性能测试通常在本地或CI环境中单独运行，而不是随单元测试一起运行")
    def test_rate_limit_performance(self, client):
        """测试限流性能"""
        # 配置较低的限流阈值
        client.app.state.config.middleware.rate_limit.max_requests = 10
        client.app.state.config.middleware.rate_limit.reset_interval = 60
        
        # 执行超过限制的请求
        test = PerformanceTest(
            client=client,
            endpoint="/api/test/user/123",
            concurrent_users=5,
            request_count=30
        )
        
        results = test.run()
        
        # 打印结果
        print("\n限流性能测试结果:")
        print(f"并发用户数: {results['concurrent_users']}")
        print(f"请求总数: {results['request_count']}")
        print(f"总执行时间: {results['total_time']:.2f}秒")
        print(f"吞吐量: {results['throughput']:.2f}请求/秒")
        print(f"成功率: {results['success_rate']:.2f}%")
        print(f"平均响应时间: {results['avg_response_time'] * 1000:.2f}ms")
        print(f"状态码分布: {results['status_codes']}")
        
        # 检查是否有429(Too Many Requests)状态码
        assert 429 in results['status_codes'], "应有429状态码(Too Many Requests)"
        assert results['status_codes'].get(429, 0) > 0, "应有一些被限流的请求"
    
    @pytest.mark.skip(reason="性能测试通常在本地或CI环境中单独运行，而不是随单元测试一起运行")
    def test_cache_performance(self, client, monkeypatch):
        """测试缓存性能影响"""
        # 先禁用缓存进行测试
        client.app.state.config.cache.enabled = False
        
        # 执行不带缓存的请求
        test_no_cache = PerformanceTest(
            client=client,
            endpoint="/api/test/user/123",
            concurrent_users=5,
            request_count=50
        )
        
        results_no_cache = test_no_cache.run()
        
        # 启用缓存
        client.app.state.config.cache.enabled = True
        
        # 执行带缓存的请求
        test_with_cache = PerformanceTest(
            client=client,
            endpoint="/api/test/user/123",
            concurrent_users=5,
            request_count=50
        )
        
        results_with_cache = test_with_cache.run()
        
        # 比较结果
        print("\n缓存性能对比测试结果:")
        print(f"不带缓存平均响应时间: {results_no_cache['avg_response_time'] * 1000:.2f}ms")
        print(f"带缓存平均响应时间: {results_with_cache['avg_response_time'] * 1000:.2f}ms")
        print(f"不带缓存吞吐量: {results_no_cache['throughput']:.2f}请求/秒")
        print(f"带缓存吞吐量: {results_with_cache['throughput']:.2f}请求/秒")
        
        # 理论上，缓存应该提高性能
        assert results_with_cache['avg_response_time'] <= results_no_cache['avg_response_time'], "缓存应减少平均响应时间"
        assert results_with_cache['throughput'] >= results_no_cache['throughput'], "缓存应提高吞吐量"


if __name__ == "__main__":
    from unittest.mock import MagicMock
    
    # 设置环境以运行单个性能测试
    app = FastAPI()
    config = GatewayConfig(
        routes=[
            RouteConfig(
                name="test-service",
                prefix="/api/test/",
                service="test-service",
                methods=["GET", "POST"],
                auth_required=False
            )
        ],
        cache=CacheConfig(
            enabled=True,
            ttl=60,
            max_size=1000
        )
    )
    
    # 设置路由
    setup_routes(app, config)
    
    # 添加mock服务端点
    @app.get("/api/test/user/{user_id}")
    def get_user(user_id: str):
        # 模拟服务处理时间
        time.sleep(0.01)  # 10ms
        return {"user_id": user_id, "name": f"User {user_id}"}
    
    @app.get("/health")
    def health_check():
        return {"status": "ok"}
    
    # 设置应用状态
    registry = MagicMock(spec=ServiceRegistry)
    registry.get_endpoint.return_value = ("localhost", 8000)
    app.state.registry = registry
    app.state.config = config
    
    client = TestClient(app)
    
    # 运行性能测试
    test = PerformanceTest(
        client=client,
        endpoint="/health",
        concurrent_users=10,
        request_count=1000
    )
    
    results = test.run()
    
    # 打印结果
    print("\n性能测试结果:")
    print(f"并发用户数: {results['concurrent_users']}")
    print(f"请求总数: {results['request_count']}")
    print(f"总执行时间: {results['total_time']:.2f}秒")
    print(f"吞吐量: {results['throughput']:.2f}请求/秒")
    print(f"成功率: {results['success_rate']:.2f}%")
    print(f"平均响应时间: {results['avg_response_time'] * 1000:.2f}ms")
    print(f"最小响应时间: {results['min_response_time'] * 1000:.2f}ms")
    print(f"最大响应时间: {results['max_response_time'] * 1000:.2f}ms")
    print(f"50%响应时间: {results['p50_response_time'] * 1000:.2f}ms")
    print(f"95%响应时间: {results['p95_response_time'] * 1000:.2f}ms")
    print(f"99%响应时间: {results['p99_response_time'] * 1000:.2f}ms")
    print(f"状态码分布: {results['status_codes']}") 