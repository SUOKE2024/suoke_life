#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
服务模块测试
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from suoke_api_gateway.core.config import Settings
from suoke_api_gateway.models.gateway import ServiceInstance
from suoke_api_gateway.services.load_balancer import (
    LoadBalancer, RoundRobinStrategy, WeightedRoundRobinStrategy,
    LeastConnectionsStrategy, RandomStrategy
)
from suoke_api_gateway.services.proxy import ProxyService
from suoke_api_gateway.services.service_registry import ServiceRegistry

class TestServiceRegistry:
    """服务注册中心测试"""
    
    @pytest.fixture
    def settings(self):
        """创建测试设置"""
        return Settings()
    
    @pytest.fixture
    def service_registry(self, settings):
        """创建服务注册中心"""
        return ServiceRegistry(settings)
    
    def test_register_service(self, service_registry):
        """测试服务注册"""
        instance = ServiceInstance(
            id="test-service-1",
            name="test-service",
            host="localhost",
            port=8080,
            healthy=True,
            weight=1,
        )
        
        service_registry.register_service(instance)
        
        services = service_registry.get_all_services()
        assert "test-service" in services
        assert len(services["test-service"]) == 1
        assert services["test-service"][0].id == "test-service-1"
    
    def test_deregister_service(self, service_registry):
        """测试服务注销"""
        instance = ServiceInstance(
            id="test-service-1",
            name="test-service",
            host="localhost",
            port=8080,
            healthy=True,
            weight=1,
        )
        
        service_registry.register_service(instance)
        result = service_registry.deregister_service("test-service", "test-service-1")
        
        assert result is True
        services = service_registry.get_all_services()
        assert "test-service" not in services or len(services["test-service"]) == 0
    
    def test_get_service_instance(self, service_registry):
        """测试获取服务实例"""
        instance1 = ServiceInstance(
            id="test-service-1",
            name="test-service",
            host="localhost",
            port=8080,
            healthy=True,
            weight=1,
        )
        
        instance2 = ServiceInstance(
            id="test-service-2",
            name="test-service",
            host="localhost",
            port=8081,
            healthy=False,
            weight=1,
        )
        
        service_registry.register_service(instance1)
        service_registry.register_service(instance2)
        
        # 应该返回健康的实例
        selected = service_registry.get_service_instance("test-service")
        assert selected is not None
        assert selected.healthy is True
        assert selected.id == "test-service-1"
    
    def test_get_service_health(self, service_registry):
        """测试获取服务健康状态"""
        instance1 = ServiceInstance(
            id="test-service-1",
            name="test-service",
            host="localhost",
            port=8080,
            healthy=True,
            weight=1,
        )
        
        instance2 = ServiceInstance(
            id="test-service-2",
            name="test-service",
            host="localhost",
            port=8081,
            healthy=False,
            weight=1,
        )
        
        service_registry.register_service(instance1)
        service_registry.register_service(instance2)
        
        health = service_registry.get_service_health("test-service")
        assert health["status"] == "degraded"  # 部分实例不健康
        assert health["healthy_instances"] == 1
        assert health["total_instances"] == 2
        assert health["health_ratio"] == 0.5

class TestLoadBalancer:
    """负载均衡器测试"""
    
    @pytest.fixture
    def instances(self):
        """创建测试实例"""
        return [
            ServiceInstance(
                id="service-1",
                name="test-service",
                host="localhost",
                port=8080,
                healthy=True,
                weight=1,
            ),
            ServiceInstance(
                id="service-2",
                name="test-service",
                host="localhost",
                port=8081,
                healthy=True,
                weight=2,
            ),
            ServiceInstance(
                id="service-3",
                name="test-service",
                host="localhost",
                port=8082,
                healthy=True,
                weight=1,
            ),
        ]
    
    def test_round_robin_strategy(self, instances):
        """测试轮询策略"""
        strategy = RoundRobinStrategy()
        balancer = LoadBalancer(strategy)
        
        # 第一轮
        selected1 = balancer.select_instance(instances)
        selected2 = balancer.select_instance(instances)
        selected3 = balancer.select_instance(instances)
        
        # 第二轮应该重复
        selected4 = balancer.select_instance(instances)
        
        assert selected1.id == "service-1"
        assert selected2.id == "service-2"
        assert selected3.id == "service-3"
        assert selected4.id == "service-1"
    
    def test_weighted_round_robin_strategy(self, instances):
        """测试加权轮询策略"""
        strategy = WeightedRoundRobinStrategy()
        balancer = LoadBalancer(strategy)
        
        # 收集多次选择结果
        selections = []
        for _ in range(12):  # 权重总和为4，选择12次应该有3轮
            selected = balancer.select_instance(instances)
            selections.append(selected.id)
        
        # 验证权重分布
        count_service_1 = selections.count("service-1")
        count_service_2 = selections.count("service-2")
        count_service_3 = selections.count("service-3")
        
        # service-2的权重是2，应该被选择更多次
        assert count_service_2 > count_service_1
        assert count_service_2 > count_service_3
    
    def test_random_strategy(self, instances):
        """测试随机策略"""
        strategy = RandomStrategy()
        balancer = LoadBalancer(strategy)
        
        # 多次选择，验证都是有效实例
        for _ in range(10):
            selected = balancer.select_instance(instances)
            assert selected in instances
    
    def test_least_connections_strategy(self, instances):
        """测试最少连接策略"""
        strategy = LeastConnectionsStrategy()
        balancer = LoadBalancer(strategy)
        
        # 初始状态，所有实例连接数为0，应该选择第一个
        selected1 = balancer.select_instance(instances)
        assert selected1.id == "service-1"
        
        # 增加第一个实例的连接数
        balancer.add_connection(selected1)
        
        # 下次选择应该是连接数最少的
        selected2 = balancer.select_instance(instances)
        assert selected2.id in ["service-2", "service-3"]
    
    def test_filter_healthy_instances(self, instances):
        """测试过滤健康实例"""
        # 设置一个实例为不健康
        instances[1].healthy = False
        
        strategy = RoundRobinStrategy()
        balancer = LoadBalancer(strategy)
        
        # 多次选择，不应该选择到不健康的实例
        for _ in range(10):
            selected = balancer.select_instance(instances)
            assert selected.healthy is True
            assert selected.id != "service-2"

class TestProxyService:
    """代理服务测试"""
    
    @pytest.fixture
    def settings(self):
        """创建测试设置"""
        return Settings()
    
    @pytest.fixture
    async def proxy_service(self, settings):
        """创建代理服务"""
        service = ProxyService(settings)
        await service.initialize()
        yield service
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_proxy_request_success(self, proxy_service):
        """测试成功的代理请求"""
        target_instance = ServiceInstance(
            id="target-service-1",
            name="target-service",
            host="httpbin.org",
            port=80,
            healthy=True,
            weight=1,
        )
        
        with patch('aiohttp.ClientSession.request') as mock_request:
            # 模拟成功响应
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.headers = {"Content-Type": "application/json"}
            mock_response.read.return_value = b'{"success": true}'
            mock_request.return_value.__aenter__.return_value = mock_response
            
            response = await proxy_service.proxy_request(
                target_instance=target_instance,
                method="GET",
                path="/get",
                headers={"User-Agent": "test"},
                body=b"",
            )
            
            assert response.status_code == 200
            assert response.headers["Content-Type"] == "application/json"
            assert response.body == b'{"success": true}'
    
    @pytest.mark.asyncio
    async def test_proxy_request_timeout(self, proxy_service):
        """测试代理请求超时"""
        target_instance = ServiceInstance(
            id="target-service-1",
            name="target-service",
            host="httpbin.org",
            port=80,
            healthy=True,
            weight=1,
        )
        
        with patch('aiohttp.ClientSession.request') as mock_request:
            # 模拟超时
            mock_request.side_effect = asyncio.TimeoutError()
            
            response = await proxy_service.proxy_request(
                target_instance=target_instance,
                method="GET",
                path="/delay/10",
                headers={},
                body=b"",
            )
            
            assert response.status_code == 504  # Gateway Timeout
    
    @pytest.mark.asyncio
    async def test_proxy_request_connection_error(self, proxy_service):
        """测试代理请求连接错误"""
        target_instance = ServiceInstance(
            id="target-service-1",
            name="target-service",
            host="nonexistent.example.com",
            port=80,
            healthy=True,
            weight=1,
        )
        
        with patch('aiohttp.ClientSession.request') as mock_request:
            # 模拟连接错误
            mock_request.side_effect = aiohttp.ClientConnectorError(
                connection_key=None,
                os_error=OSError("Connection refused"),
            )
            
            response = await proxy_service.proxy_request(
                target_instance=target_instance,
                method="GET",
                path="/test",
                headers={},
                body=b"",
            )
            
            assert response.status_code == 502  # Bad Gateway

if __name__ == "__main__":
    pytest.main(["-v", "test_services.py"]) 