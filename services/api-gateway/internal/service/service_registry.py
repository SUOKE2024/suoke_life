#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
服务注册表，管理和发现所有微服务
支持静态配置、Consul和Kubernetes服务发现
"""

import asyncio
import logging
import random
from typing import Dict, List, Optional, Tuple

import aiohttp
import consul.aio
from kubernetes_asyncio import client, config

from internal.model.config import GatewayConfig, ServiceConfig, ServiceEndpointConfig


logger = logging.getLogger(__name__)


class ServiceRegistry:
    """服务注册表，管理后端微服务信息和健康状态"""
    
    def __init__(self, config: GatewayConfig):
        """
        初始化服务注册表
        
        Args:
            config: 网关配置
        """
        self.config = config
        self.services: Dict[str, ServiceConfig] = {}
        self.healthy_endpoints: Dict[str, List[ServiceEndpointConfig]] = {}
        self._refresh_task = None
        self._health_check_tasks = {}
        self._session = None
        self._consul_client = None
        self._k8s_client = None
    
    async def start(self):
        """启动服务发现和健康检查"""
        self._session = aiohttp.ClientSession()
        
        # 初始化Consul客户端
        if self.config.service_discovery.type == "consul":
            self._consul_client = consul.aio.Consul(
                host=self.config.service_discovery.consul_host or "consul",
                port=self.config.service_discovery.consul_port
            )
        
        # 初始化Kubernetes客户端
        if self.config.service_discovery.type == "kubernetes":
            try:
                # 尝试在集群内加载配置
                await config.load_incluster_config()
            except config.config_exception.ConfigException:
                # 如果失败，则尝试从本地加载
                await config.load_kube_config()
            
            self._k8s_client = client.CoreV1Api()
        
        await self._load_services()
        
        # 启动定期刷新任务
        self._refresh_task = asyncio.create_task(self._periodic_refresh())
        
        logger.info(f"服务注册表已启动，发现 {len(self.services)} 个服务")
    
    async def stop(self):
        """停止服务发现和健康检查"""
        if self._refresh_task:
            self._refresh_task.cancel()
            try:
                await self._refresh_task
            except asyncio.CancelledError:
                pass
            
        # 取消所有健康检查任务
        for task in self._health_check_tasks.values():
            task.cancel()
            
        # 等待所有任务完成
        if self._health_check_tasks:
            await asyncio.gather(*self._health_check_tasks.values(), return_exceptions=True)
        
        # 关闭Consul客户端
        if self._consul_client:
            await self._consul_client.close()
            
        # 关闭HTTP会话
        if self._session:
            await self._session.close()
            
        logger.info("服务注册表已停止")
    
    async def _load_services(self):
        """根据配置加载服务信息"""
        discovery_type = self.config.service_discovery.type
        
        if discovery_type == "static":
            await self._load_static_services()
        elif discovery_type == "consul":
            await self._load_consul_services()
        elif discovery_type == "kubernetes":
            await self._load_kubernetes_services()
        else:
            logger.error(f"不支持的服务发现类型: {discovery_type}")
            raise ValueError(f"不支持的服务发现类型: {discovery_type}")
    
    async def _load_static_services(self):
        """从静态配置加载服务"""
        self.services = self.config.service_discovery.services
        
        # 初始化健康端点列表
        self.healthy_endpoints = {}
        for service_name, service in self.services.items():
            # 开始健康检查
            self._health_check_tasks[service_name] = asyncio.create_task(
                self._check_service_health(service_name, service)
            )
            
            # 初始时假设所有端点都是健康的
            self.healthy_endpoints[service_name] = service.endpoints
    
    async def _load_consul_services(self):
        """从Consul加载服务信息"""
        if not self._consul_client:
            logger.error("Consul客户端未初始化")
            return
        
        try:
            # 从Consul获取所有服务
            _, services = await self._consul_client.catalog.services()
            
            # 清除旧的健康检查任务
            for task in self._health_check_tasks.values():
                task.cancel()
            self._health_check_tasks = {}
            
            # 更新服务列表
            self.services = {}
            self.healthy_endpoints = {}
            
            # 处理每个服务
            for service_name in services:
                # 跳过consul服务
                if service_name == "consul":
                    continue
                
                # 获取服务实例
                _, instances = await self._consul_client.catalog.service(service_name)
                
                if not instances:
                    continue
                
                # 创建端点列表
                endpoints = []
                for instance in instances:
                    endpoint = ServiceEndpointConfig(
                        host=instance["ServiceAddress"] or instance["Address"],
                        port=instance["ServicePort"],
                        use_tls=False,  # 可以根据标签或元数据设置
                        health_check=self.config.service_discovery.default_health_check
                    )
                    endpoints.append(endpoint)
                
                # 创建服务配置
                service_config = ServiceConfig(
                    name=service_name,
                    endpoints=endpoints,
                    load_balancer="round-robin",  # 默认负载均衡策略
                    circuit_breaker=True,
                    timeout=30
                )
                
                self.services[service_name] = service_config
                
                # 创建健康检查任务
                self._health_check_tasks[service_name] = asyncio.create_task(
                    self._check_service_health(service_name, service_config)
                )
            
            logger.info(f"从Consul加载了 {len(self.services)} 个服务")
            
        except Exception as e:
            logger.error(f"从Consul加载服务失败: {str(e)}", exc_info=True)
    
    async def _load_kubernetes_services(self):
        """从Kubernetes加载服务信息"""
        if not self._k8s_client:
            logger.error("Kubernetes客户端未初始化")
            return
        
        try:
            # 获取指定命名空间中的所有服务
            namespace = self.config.service_discovery.kubernetes_namespace
            label_selector = self.config.service_discovery.kubernetes_label_selector
            
            services = await self._k8s_client.list_namespaced_service(
                namespace=namespace,
                label_selector=label_selector
            )
            
            # 清除旧的健康检查任务
            for task in self._health_check_tasks.values():
                task.cancel()
            self._health_check_tasks = {}
            
            # 更新服务列表
            self.services = {}
            self.healthy_endpoints = {}
            
            # 处理每个服务
            for svc in services.items:
                service_name = svc.metadata.name
                
                # 获取服务端点
                endpoints = await self._k8s_client.read_namespaced_endpoints(
                    name=service_name,
                    namespace=namespace
                )
                
                # 创建端点列表
                service_endpoints = []
                
                if endpoints.subsets:
                    for subset in endpoints.subsets:
                        if not subset.addresses:
                            continue
                            
                        for address in subset.addresses:
                            for port in subset.ports:
                                endpoint = ServiceEndpointConfig(
                                    host=address.ip,
                                    port=port.port,
                                    use_tls=False,  # 可以从注解中确定
                                    health_check=self.config.service_discovery.default_health_check
                                )
                                service_endpoints.append(endpoint)
                
                if not service_endpoints:
                    # 如果没有端点，使用服务的ClusterIP和端口
                    for port in svc.spec.ports:
                        endpoint = ServiceEndpointConfig(
                            host=svc.spec.cluster_ip,
                            port=port.port,
                            use_tls=False,
                            health_check=self.config.service_discovery.default_health_check
                        )
                        service_endpoints.append(endpoint)
                
                # 创建服务配置
                service_config = ServiceConfig(
                    name=service_name,
                    endpoints=service_endpoints,
                    load_balancer="round-robin",  # 默认负载均衡策略
                    circuit_breaker=True,
                    timeout=30
                )
                
                self.services[service_name] = service_config
                
                # 创建健康检查任务
                self._health_check_tasks[service_name] = asyncio.create_task(
                    self._check_service_health(service_name, service_config)
                )
            
            logger.info(f"从Kubernetes加载了 {len(self.services)} 个服务")
            
        except Exception as e:
            logger.error(f"从Kubernetes加载服务失败: {str(e)}", exc_info=True)
    
    async def _periodic_refresh(self):
        """周期性刷新服务列表和健康状态"""
        try:
            while True:
                await asyncio.sleep(self.config.service_discovery.refresh_interval)
                await self._load_services()
                logger.debug(f"服务列表已刷新，共 {len(self.services)} 个服务")
        except asyncio.CancelledError:
            logger.debug("服务刷新任务已取消")
            raise
        except Exception as e:
            logger.error(f"服务刷新出错: {e}", exc_info=True)
    
    async def _check_service_health(self, service_name: str, service: ServiceConfig):
        """
        周期性检查服务健康状态
        
        Args:
            service_name: 服务名称
            service: 服务配置
        """
        try:
            # 初始化健康端点列表
            self.healthy_endpoints[service_name] = []
            
            while True:
                healthy_endpoints = []
                
                for endpoint in service.endpoints:
                    if not endpoint.health_check.enabled:
                        # 如果未启用健康检查，默认认为端点健康
                        healthy_endpoints.append(endpoint)
                        continue
                    
                    is_healthy = await self._check_endpoint_health(service_name, endpoint)
                    if is_healthy:
                        healthy_endpoints.append(endpoint)
                
                # 更新健康端点列表
                self.healthy_endpoints[service_name] = healthy_endpoints
                
                # 如果没有健康端点，记录警告
                if not healthy_endpoints:
                    logger.warning(f"服务 {service_name} 没有健康端点可用")
                else:
                    logger.debug(f"服务 {service_name} 有 {len(healthy_endpoints)} 个健康端点")
                
                # 等待下一次检查
                health_check_interval = service.endpoints[0].health_check.interval if service.endpoints else 10
                await asyncio.sleep(health_check_interval)
                
        except asyncio.CancelledError:
            logger.debug(f"服务 {service_name} 健康检查任务已取消")
            raise
        except Exception as e:
            logger.error(f"服务 {service_name} 健康检查出错: {str(e)}", exc_info=True)
    
    async def _check_endpoint_health(self, service_name: str, endpoint: ServiceEndpointConfig) -> bool:
        """
        检查单个端点的健康状态
        
        Args:
            service_name: 服务名称
            endpoint: 服务端点配置
            
        Returns:
            bool: 端点是否健康
        """
        health_check = endpoint.health_check
        health_url = f"http{'s' if endpoint.use_tls else ''}://{endpoint.host}:{endpoint.port}{health_check.path}"
        
        for retry in range(health_check.retries + 1):
            try:
                async with self._session.get(
                    health_url, 
                    timeout=health_check.timeout,
                    ssl=None if not endpoint.use_tls else True
                ) as response:
                    if 200 <= response.status < 300:
                        return True
                    logger.debug(f"服务 {service_name} 健康检查失败，状态码: {response.status}")
            except Exception as e:
                logger.debug(f"服务 {service_name} 健康检查异常: {e}")
            
            # 最后一次重试
            if retry == health_check.retries:
                break
                
            # 等待下一次重试
            await asyncio.sleep(1)
        
        return False
    
    def get_service(self, service_name: str) -> Optional[ServiceConfig]:
        """
        获取服务配置
        
        Args:
            service_name: 服务名称
            
        Returns:
            Optional[ServiceConfig]: 服务配置，如不存在则返回None
        """
        return self.services.get(service_name)
    
    def get_endpoint(self, service_name: str) -> Optional[Tuple[str, int]]:
        """
        获取服务端点，使用配置的负载均衡策略
        
        Args:
            service_name: 服务名称
            
        Returns:
            Optional[Tuple[str, int]]: 主机和端口元组，如不存在则返回None
        """
        if service_name not in self.services:
            logger.warning(f"服务不存在: {service_name}")
            return None
        
        healthy_endpoints = self.healthy_endpoints.get(service_name, [])
        if not healthy_endpoints:
            logger.warning(f"服务 {service_name} 没有健康端点可用")
            return None
        
        service = self.services[service_name]
        lb_strategy = service.load_balancer
        
        if lb_strategy == "round-robin":
            # 简单的轮询策略，实际应用中可能需要一个计数器
            endpoint = healthy_endpoints[0]  # 使用第一个端点，实际应该轮询
            # 将第一个端点移动到列表末尾，实现轮询
            self.healthy_endpoints[service_name] = healthy_endpoints[1:] + [healthy_endpoints[0]]
        elif lb_strategy == "random":
            # 随机选择
            endpoint = random.choice(healthy_endpoints)
        elif lb_strategy == "least-conn":
            # 实际中，这里需要跟踪每个端点的连接数
            # 但此处简化为随机选择
            endpoint = random.choice(healthy_endpoints)
        else:
            # 默认使用第一个
            logger.warning(f"不支持的负载均衡策略: {lb_strategy}，使用第一个端点")
            endpoint = healthy_endpoints[0]
        
        return endpoint.host, endpoint.port 