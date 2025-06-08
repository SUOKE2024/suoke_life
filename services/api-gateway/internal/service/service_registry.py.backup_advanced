"""
service_registry - 索克生活项目模块
"""

from internal.model.config import GatewayConfig, ServiceConfig, ServiceEndpointConfig
from kubernetes_asyncio import client, config
from typing import Dict, List, Optional, Tuple
import logging

#! / usr / bin / env python
# - * - coding: utf - 8 - * -

"""
服务注册表，管理和发现所有微服务
支持静态配置、Consul和Kubernetes服务发现
"""


# 导入自定义修补模块


logger = logging.getLogger(__name__)

class ServiceRegistry:
    """服务注册表基类"""

    def __init__(self, config):
        """
        初始化服务注册表

        Args:
            config: 服务发现配置
        """
        self.config = config
        self.services = {}
        self.healthy_endpoints = {}  # 健康端点缓存

        # 从配置中加载服务（如果有）
        if hasattr(config, "services") and config.services:
            self.services = config.services

            # 初始化健康端点信息
            for service_name, service in self.services.items():
                if service.endpoints:
                    self.healthy_endpoints[service_name] = [(endpoint.host, endpoint.port)
                                                        for endpoint in service.endpoints]

    def get_endpoint(self, service_name: str) - > Optional[Tuple[str, int]]:
        """
        获取服务端点

        Args:
            service_name: 服务名称

        Returns:
            元组 (host, port) 或 None
        """
        if service_name not in self.services:
            return None

        service = self.services[service_name]

        if not service.endpoints:
            return None

        # 实现简单的轮询负载均衡
        endpoint = service.endpoints[0]

        # 循环端点列表
        service.endpoints.append(service.endpoints.pop(0))

        return (endpoint.host, endpoint.port)

    def get_all_services(self) - > Dict[str, ServiceConfig]:
        """
        获取所有服务

        Returns:
            服务字典
        """
        return self.services

    def get_service(self, service_name: str) - > Optional[ServiceConfig]:
        """
        获取服务配置

        Args:
            service_name: 服务名称

        Returns:
            服务配置或None
        """
        return self.services.get(service_name)

    async def refresh_services(self) - > None:
        """
        刷新服务列表
        """
        # 在子类中实现
        pass

class ConsulServiceRegistry(ServiceRegistry):
    """基于Consul的服务注册表"""

    def __init__(self, config):
        """
        初始化Consul服务注册表

        Args:
            config: 服务发现配置
        """
        super().__init__(config)
        self.consul_host = config.consul_host
        self.consul_port = config.consul_port
        self.consul_client = consul.aio.Consul(
            host = self.consul_host,
            port = self.consul_port
        )

    async def refresh_services(self) - > None:
        """
        从Consul刷新服务列表
        """
        try:
            # 获取所有服务
            index, services = await self.consul_client.catalog.services()

            # 清空当前服务列表
            self.services = {}

            # 获取每个服务的详情
            for service_name in services:
                # 跳过consul服务
                if service_name == "consul":
                    continue

                # 获取服务实例
                index, service_instances = await self.consul_client.catalog.service(service_name)

                if not service_instances:
                    continue

                # 创建端点列表
                endpoints = []

                for instance in service_instances:
                    host = instance.get("ServiceAddress") or instance.get("Address")
                    port = instance.get("ServicePort")

                    if host and port:
                        endpoints.append(ServiceEndpointConfig(
                            host = host,
                            port = port
                        ))

                # 获取服务标签
                tags = service_instances[0].get("ServiceTags", [])
                version = next((tag for tag in tags if tag.startswith("v")), "v1")

                # 添加到服务列表
                self.services[service_name] = ServiceConfig(
                    name = service_name,
                    version = version,
                    endpoints = endpoints
                )

                # 更新健康端点
                if endpoints:
                    self.healthy_endpoints[service_name] = [(endpoint.host, endpoint.port)
                                                        for endpoint in endpoints]

            logger.info(f"从Consul刷新了 {len(self.services)} 个服务")

        except Exception as e:
            logger.error(f"从Consul刷新服务失败: {str(e)}")

class KubernetesServiceRegistry(ServiceRegistry):
    """基于Kubernetes的服务注册表"""

    def __init__(self, config):
        """
        初始化Kubernetes服务注册表

        Args:
            config: 服务发现配置
        """
        super().__init__(config)
        self.namespace = config.kubernetes_namespace
        self.label_selector = config.kubernetes_label_selector
        self.api_client = None

    async def _init_client(self) - > None:
        """
        初始化Kubernetes客户端
        """
        if self.api_client is None:
            try:
                # 加载配置 - 使用正确的导入路径
                await k8s_config.load_kube_config()
                self.api_client = client.CoreV1Api()
            except Exception as e:
                logger.error(f"初始化Kubernetes客户端失败: {str(e)}")

    async def refresh_services(self) - > None:
        """
        从Kubernetes刷新服务列表
        """
        try:
            # 初始化客户端
            await self._init_client()

            if not self.api_client:
                return

            # 获取所有Endpoints
            endpoints = await self.api_client.list_namespaced_endpoints(
                namespace = self.namespace,
                label_selector = self.label_selector
            )

            # 清空当前服务列表
            self.services = {}

            # 处理每个Endpoint
            for endpoint in endpoints.items:
                service_name = endpoint.metadata.name

                # 创建端点列表
                service_endpoints = []

                # 处理子集
                for subset in endpoint.subsets:
                    # 获取地址
                    addresses = subset.addresses or []

                    # 获取端口
                    ports = subset.ports or []

                    # 创建端点
                    for address in addresses:
                        for port in ports:
                            host = address.ip
                            port_number = port.port

                            service_endpoints.append(ServiceEndpointConfig(
                                host = host,
                                port = port_number
                            ))

                # 如果有端点，添加到服务列表
                if service_endpoints:
                    self.services[service_name] = ServiceConfig(
                        name = service_name,
                        version = "v1",  # 默认版本
                        endpoints = service_endpoints
                    )

                    # 更新健康端点
                    self.healthy_endpoints[service_name] = [(endpoint_item.host, endpoint_item.port)
                                                        for endpoint_item in service_endpoints]

            logger.info(f"从Kubernetes刷新了 {len(self.services)} 个服务")

        except Exception as e:
            logger.error(f"从Kubernetes刷新服务失败: {str(e)}")

def create_service_registry(config):
    """
    创建服务注册表

    Args:
        config: 服务发现配置

    Returns:
        服务注册表实例
    """
    discovery_type = config.type.lower()

    if discovery_type == "consul":
        return ConsulServiceRegistry(config)
    elif discovery_type == "kubernetes":
        return KubernetesServiceRegistry(config)
    else:
        # 默认使用静态配置
        return ServiceRegistry(config)