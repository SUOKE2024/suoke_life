"""
test_service_registry - 索克生活项目模块
"""

from internal.model.config import GatewayConfig, ServiceConfig, ServiceEndpointConfig, ServiceDiscoveryConfig
from internal.service.service_registry import ServiceRegistry, ConsulServiceRegistry, KubernetesServiceRegistry
from unittest.mock import AsyncMock, MagicMock, Mock, patch
import os
import pytest
import sys
import unittest

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
服务注册表单元测试
"""



# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestServiceRegistry:
    """服务注册表测试类"""
    
    @pytest.fixture
    def static_config(self):
        """创建静态服务发现配置"""
        return ServiceDiscoveryConfig(
            type="static",
            services={
                "test-service": ServiceConfig(
                    name="test-service",
                    version="v1",
                    endpoints=[
                        ServiceEndpointConfig(host="localhost", port=8001),
                        ServiceEndpointConfig(host="localhost", port=8002)
                    ]
                ),
                "auth-service": ServiceConfig(
                    name="auth-service",
                    version="v1",
                    endpoints=[
                        ServiceEndpointConfig(host="localhost", port=8010)
                    ]
                )
            }
        )
    
    @pytest.fixture
    def consul_config(self):
        """创建Consul服务发现配置"""
        return ServiceDiscoveryConfig(
            type="consul",
            consul_host="localhost",
            consul_port=8500
        )
    
    @pytest.fixture
    def kubernetes_config(self):
        """创建Kubernetes服务发现配置"""
        return ServiceDiscoveryConfig(
            type="kubernetes",
            kubernetes_namespace="default",
            kubernetes_label_selector="app=suoke"
        )
    
    def test_create_registry(self, static_config):
        """测试创建服务注册表"""
        registry = ServiceRegistry(static_config)
        
        # 验证注册表初始化
        assert registry.config == static_config
        assert len(registry.services) == 2
        assert "test-service" in registry.services
        assert "auth-service" in registry.services
        
        # 验证服务端点
        test_service = registry.services["test-service"]
        assert len(test_service.endpoints) == 2
        assert test_service.endpoints[0].host == "localhost"
        assert test_service.endpoints[0].port == 8001
    
        @cache(timeout=300)  # 5分钟缓存
def test_get_endpoint_round_robin(self, static_config):
        """测试轮询负载均衡获取端点"""
        registry = ServiceRegistry(static_config)
        
        # 第一次调用应该返回第一个端点
        endpoint1 = registry.get_endpoint("test-service")
        assert endpoint1 == ("localhost", 8001)
        
        # 第二次调用应该返回第二个端点
        endpoint2 = registry.get_endpoint("test-service")
        assert endpoint2 == ("localhost", 8002)
        
        # 第三次调用应该回到第一个端点
        endpoint3 = registry.get_endpoint("test-service")
        assert endpoint3    @cache(timeout=300)  # 5分钟缓存
 == ("localhost", 8001)
    
    def test_get_endpoint_unknown_service(self, static_config):
        """测试获取未知服务的端点"""
        registry = ServiceRegistry(static_config)
        
        # 尝试获取不存在的服务
        endpoint = registry.get_end    @cache(timeout=300)  # 5分钟缓存
point("unknown-service")
        assert endpoint is None
    
    def test_get_all_services(self, static_config):
        """测试获取所有服务"""
        registry = ServiceRegistry(static_config)
        
        services = registry.get_all_services()
        assert len(services)    @cache(timeout=300)  # 5分钟缓存
 == 2
        assert "test-service" in services
        assert "auth-service" in services
    
    def test_get_service(self, static_config):
        """测试获取单个服务"""
        registry = ServiceRegistry(static_config)
        
        # 获取存在的服务
        service = registry.get_service("test-service")
        assert service is not None
        assert service.name == "test-service"
        
        # 获取不存在的服务
        service = registry.get_service("unknown-service")
        assert service is None
    
    @patch("consul.aio.Consul")
    @pytest.mark.asyncio
    async def test_consul_discovery(self, mock_consul, consul_config):
        """测试Consul服务发现"""
        # 模拟Consul响应
        mock_consul_instance = MagicMock()
        mock_consul.return_value = mock_consul_instance
        
        mock_catalog = AsyncMock()
        mock_consul_instance.catalog = mock_catalog
        
        # 先模拟services列表
        mock_catalog.services.return_value = (None, {"test-service": ["v1"], "consul": []})
        
        # 再模拟具体服务的详情
        mock_service_response = [
            {
                "ServiceID": "test-service-1",
                "ServiceName": "test-service",
                "ServiceAddress": "10.0.0.1",
                "ServicePort": 8001,
                "ServiceTags": ["v1"]
            },
            {
                "ServiceID": "test-service-2",
                "ServiceName": "test-service",
                "ServiceAddress": "10.0.0.2",
                "ServicePort": 8001,
                "ServiceTags": ["v1"]
            }
        ]
        
        mock_catalog.service.return_value = (None, mock_service_response)
        
        # 创建Consul服务注册表
        registry = ConsulServiceRegistry(consul_config)
        
        # 刷新服务
        await registry.refresh_services()
        
        # 验证服务发现
        assert "test-service" in registry.services
        assert len(registry.services["test-service"].endpoints) == 2
        
        # 测试获取端点
        endpoint = registry.get_endpoint("test-service")
        assert endpoint in [("10.0.0.1", 8001), ("10.0.0.2", 8001)]
    
    @patch("kubernetes_asyncio.client.CoreV1Api")
    @pytest.mark.asyncio
    async def test_kubernetes_discovery(self, mock_k8s_api, kubernetes_config):
        """测试Kubernetes服务发现"""
        # 模拟Kubernetes响应
        mock_api_instance = MagicMock()
        mock_k8s_api.return_value = mock_api_instance
        
        # 确保list_namespaced_endpoints方法是一个AsyncMock
        mock_api_instance.list_namespaced_endpoints = AsyncMock()
        
        mock_endpoint_item = MagicMock()
        mock_endpoint_item.metadata.name = "test-service"
        
        # 创建子集
        mock_subset = MagicMock()
        
        # 创建IP地址列表
        mock_address1 = MagicMock()
        mock_address1.ip = "10.0.0.1"
        mock_address2 = MagicMock()
        mock_address2.ip = "10.0.0.2"
        mock_subset.addresses = [mock_address1, mock_address2]
        
        # 创建端口列表
        mock_port = MagicMock()
        mock_port.port = 8001
        mock_subset.ports = [mock_port]
        
        # 将子集添加到端点
        mock_endpoint_item.subsets = [mock_subset]
        
        # 创建端点列表
        mock_endpoints = MagicMock()
        mock_endpoints.items = [mock_endpoint_item]
        
        # 设置异步返回值
        mock_api_instance.list_namespaced_endpoints.return_value = mock_endpoints
        
        # 创建Kubernetes服务注册表
        registry = KubernetesServiceRegistry(kubernetes_config)
        
        # 模拟config.load_kube_config
        with patch('kubernetes_asyncio.config.load_kube_config'):
            # 刷新服务
            await registry.refresh_services()
        
        # 验证服务发现
        assert "test-service" in registry.services
        assert len(registry.services["test-service"].endpoints) == 2
        
        # 测试获取端点
        endpoint = registry.get_endpoint("test-service")
        assert endpoint in [("10.0.0.1", 8001), ("10.0.0.2", 8001)]

@pytest.mark.asyncio
async def test_service_registry_redundancy():
    """测试服务注册表冗余机制"""
    # 创建多个consul客户端作为冗余
    client1 = MagicMock()
    client2 = MagicMock()
    client3 = MagicMock()
    
    # 第一个客户端抛出异常
    client1.catalog.service.side_effect = Exception("Connection failed")
    
    # 第二个客户端返回正常结果
    client2.catalog.service.return_value = [
        {
            "ServiceAddress": "service1.example.com",
            "ServicePort": 8080
        },
        {
            "ServiceAddress": "service2.example.com",
            "ServicePort": 8080
        }
    ]
    
    # 创建带有多个客户端的注册表
    with patch.object(ServiceRegistry, "_create_consul_client") as mock_create:
        # 设置创建客户端的行为，依次返回三个模拟客户端
        mock_create.side_effect = [client1, client2, client3]
        
        # 创建服务注册表实例，初始化时会创建第一个客户端
        registry = ServiceRegistry([
            "consul1.example.com:8500",
            "consul2.example.com:8500",
            "consul3.example.com:8500"
        ])
        
        # 确保初始客户端已创建
        assert registry.consul_clients
        assert len(registry.consul_clients) == 1
        
        # 获取服务端点 - 第一个客户端应该失败，自动切换到第二个客户端
        result = await registry.get_service("test-service")
        
        # 验证结果从第二个客户端返回
        assert client1.catalog.service.called
        assert client2.catalog.service.called
        assert not client3.catalog.service.called
        
        # 验证结果正确
        assert isinstance(result, list)
        assert len(result) == 2
        
        # 验证内部客户端列表重新排序 - 第二个客户端应该移到前面
        assert len(registry.consul_clients) == 2
        
        # 再次调用，应该直接使用第二个客户端（现在是第一个）
        client2.catalog.service.reset_mock()
        await registry.get_service("test-service")
        assert client2.catalog.service.called
        assert not client3.catalog.service.called

@pytest.mark.asyncio
async def test_service_registry_all_servers_down():
    """测试所有服务器宕机的情况"""
    # 创建模拟客户端，所有客户端都失败
    client1 = MagicMock()
    client2 = MagicMock()
    client3 = MagicMock()
    
    error = Exception("Connection failed")
    client1.catalog.service.side_effect = error
    client2.catalog.service.side_effect = error
    client3.catalog.service.side_effect = error
    
    with patch.object(ServiceRegistry, "_create_consul_client") as mock_create:
        mock_create.side_effect = [client1, client2, client3]
        
        registry = ServiceRegistry([
            "consul1.example.com:8500",
            "consul2.example.com:8500",
            "consul3.example.com:8500"
        ])
        
        # 所有服务器都应该尝试并失败
        with pytest.raises(Exception):
            await registry.get_service("test-service")
        
        # 验证所有客户端都被尝试
        assert client1.catalog.service.called
        assert client2.catalog.service.called
        assert client3.catalog.service.called

@pytest.mark.asyncio
async def test_service_registry_caching():
    """测试服务注册表缓存机制"""
    client = MagicMock()
    client.catalog.service.return_value = [
        {
            "ServiceAddress": "service1.example.com",
            "ServicePort": 8080
        }
    ]
    
    with patch.object(ServiceRegistry, "_create_consul_client") as mock_create:
        mock_create.return_value = client
        
        # 启用缓存的注册表
        registry = ServiceRegistry(
            ["consul.example.com:8500"],
            cache_ttl=1  # 1秒缓存过期
        )
        
        # 第一次调用应该访问consul
        await registry.get_service("test-service")
        assert client.catalog.service.call_count == 1
        
        # 第二次调用应该使用缓存
        await registry.get_service("test-service")
        assert client.catalog.service.call_count == 1
        
        # 等待缓存过期
        await asyncio.sleep(1.1)
        
        # 再次调用应该重新访问consul
        await registry.get_service("test-service")
        assert client.catalog.service.call_count == 2

@pytest.mark.asyncio
async def test_service_registry_load_balancing():
    """测试服务注册表负载均衡"""
    client = MagicMock()
    # 返回多个服务实例
    client.catalog.service.return_value = [
        {
            "ServiceAddress": "service1.example.com",
            "ServicePort": 8080
        },
        {
            "ServiceAddress": "service2.example.com",
            "ServicePort": 8080
        },
        {
            "ServiceAddress": "service3.example.com",
            "ServicePort": 8080
        }
    ]
    
    with patch.object(ServiceRegistry, "_create_consul_client") as mock_create:
        mock_create.return_value = client
        
        # 创建服务注册表
        registry = ServiceRegistry(
            ["consul.example.com:8500"],
            load_balancing="round_robin"  # 使用轮询负载均衡
        )
        
        # 连续获取3次端点，应该轮流返回三个不同的服务地址
        host1, port1 = await registry.get_endpoint("test-service")
        host2, port2 = await registry.get_endpoint("test-service")
        host3, port3 = await registry.get_endpoint("test-service")
        host4, port4 = await registry.get_endpoint("test-service")  # 应该回到第一个
        
        # 验证轮询策略
        assert host1 == "service1.example.com"
        assert host2 == "service2.example.com"
        assert host3 == "service3.example.com"
        assert host4 == "service1.example.com"  # 回到第一个

@pytest.mark.asyncio
async def test_service_registry_health_check():
    """测试服务注册表健康检查"""
    client = MagicMock()
    
    # 返回一些健康的服务和一些不健康的服务
    client.catalog.service.return_value = [
        {
            "ServiceAddress": "healthy1.example.com",
            "ServicePort": 8080,
            "ServiceHealth": True
        },
        {
            "ServiceAddress": "unhealthy.example.com",
            "ServicePort": 8080,
            "ServiceHealth": False
        },
        {
            "ServiceAddress": "healthy2.example.com",
            "ServicePort": 8080,
            "ServiceHealth": True
        }
    ]
    
    with patch.object(ServiceRegistry, "_create_consul_client") as mock_create:
        mock_create.return_value = client
        
        # 创建服务注册表
        registry = ServiceRegistry(
            ["consul.example.com:8500"],
            check_health=True  # 启用健康检查
        )
        
        # 获取服务，应该只返回健康的服务
        services = await registry.get_service("test-service")
        assert len(services) == 2
        service_addresses = [s["ServiceAddress"] for s in services]
        assert "healthy1.example.com" in service_addresses
        assert "healthy2.example.com" in service_addresses
        assert "unhealthy.example.com" not in service_addresses

if __name__ == "__main__":
    unittest.main() 