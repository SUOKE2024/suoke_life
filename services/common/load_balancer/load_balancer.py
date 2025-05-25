"""
负载均衡器核心组件
提供多种负载均衡策略和算法
"""

import asyncio
import time
import logging
import hashlib
import random
from typing import Dict, List, Any, Optional, Protocol, Union
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class LoadBalancingStrategy(Enum):
    """负载均衡策略枚举"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    IP_HASH = "ip_hash"
    RANDOM = "random"
    CONSISTENT_HASH = "consistent_hash"

@dataclass
class ServiceEndpoint:
    """服务端点"""
    host: str
    port: int
    weight: int = 1
    max_connections: int = 100
    current_connections: int = 0
    healthy: bool = True
    last_health_check: float = field(default_factory=time.time)
    response_time: float = 0.0
    failure_count: int = 0
    
    @property
    def address(self) -> str:
        """获取地址"""
        return f"{self.host}:{self.port}"
    
    @property
    def url(self) -> str:
        """获取URL"""
        return f"http://{self.host}:{self.port}"
    
    def is_available(self) -> bool:
        """检查端点是否可用"""
        return (
            self.healthy and 
            self.current_connections < self.max_connections
        )
    
    def increment_connections(self):
        """增加连接数"""
        self.current_connections += 1
    
    def decrement_connections(self):
        """减少连接数"""
        if self.current_connections > 0:
            self.current_connections -= 1
    
    def record_success(self, response_time: float):
        """记录成功请求"""
        self.response_time = response_time
        self.failure_count = 0
    
    def record_failure(self):
        """记录失败请求"""
        self.failure_count += 1

class LoadBalancingAlgorithm(ABC):
    """负载均衡算法抽象基类"""
    
    @abstractmethod
    async def select_endpoint(
        self, 
        endpoints: List[ServiceEndpoint], 
        client_info: Optional[Dict[str, Any]] = None
    ) -> Optional[ServiceEndpoint]:
        """选择服务端点"""
        pass
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]):
        """初始化算法"""
        pass

class LoadBalancer:
    """负载均衡器"""
    
    def __init__(self):
        self.endpoints: Dict[str, List[ServiceEndpoint]] = {}
        self.algorithms: Dict[LoadBalancingStrategy, LoadBalancingAlgorithm] = {}
        self.default_strategy = LoadBalancingStrategy.ROUND_ROBIN
        self.config = {}
        self.initialized = False
        
    async def initialize(self, config: Dict[str, Any]):
        """初始化负载均衡器"""
        self.config = config
        self.default_strategy = LoadBalancingStrategy(
            config.get('default_strategy', 'round_robin')
        )
        
        # 初始化算法
        await self._initialize_algorithms()
        
        # 加载服务端点
        await self._load_endpoints(config.get('endpoints', {}))
        
        self.initialized = True
        logger.info("负载均衡器初始化完成")
    
    async def _initialize_algorithms(self):
        """初始化负载均衡算法"""
        from .algorithms import (
            RoundRobinBalancer,
            WeightedRoundRobinBalancer,
            LeastConnectionsBalancer,
            IPHashBalancer,
            RandomBalancer,
            ConsistentHashBalancer
        )
        
        algorithms = {
            LoadBalancingStrategy.ROUND_ROBIN: RoundRobinBalancer(),
            LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN: WeightedRoundRobinBalancer(),
            LoadBalancingStrategy.LEAST_CONNECTIONS: LeastConnectionsBalancer(),
            LoadBalancingStrategy.IP_HASH: IPHashBalancer(),
            LoadBalancingStrategy.RANDOM: RandomBalancer(),
            LoadBalancingStrategy.CONSISTENT_HASH: ConsistentHashBalancer()
        }
        
        for strategy, algorithm in algorithms.items():
            await algorithm.initialize(self.config.get(strategy.value, {}))
            self.algorithms[strategy] = algorithm
    
    async def _load_endpoints(self, endpoints_config: Dict[str, Any]):
        """加载服务端点配置"""
        for service_name, service_config in endpoints_config.items():
            endpoints = []
            for endpoint_config in service_config.get('endpoints', []):
                endpoint = ServiceEndpoint(
                    host=endpoint_config['host'],
                    port=endpoint_config['port'],
                    weight=endpoint_config.get('weight', 1),
                    max_connections=endpoint_config.get('max_connections', 100)
                )
                endpoints.append(endpoint)
            
            self.endpoints[service_name] = endpoints
            logger.info(f"加载服务 {service_name} 的 {len(endpoints)} 个端点")
    
    async def select_endpoint(
        self,
        service_name: str,
        strategy: Optional[LoadBalancingStrategy] = None,
        client_info: Optional[Dict[str, Any]] = None
    ) -> Optional[ServiceEndpoint]:
        """选择服务端点"""
        if not self.initialized:
            raise RuntimeError("负载均衡器未初始化")
        
        if service_name not in self.endpoints:
            logger.warning(f"未找到服务: {service_name}")
            return None
        
        endpoints = [ep for ep in self.endpoints[service_name] if ep.is_available()]
        if not endpoints:
            logger.warning(f"服务 {service_name} 没有可用端点")
            return None
        
        strategy = strategy or self.default_strategy
        algorithm = self.algorithms.get(strategy)
        
        if not algorithm:
            logger.error(f"未找到负载均衡算法: {strategy}")
            return None
        
        selected_endpoint = await algorithm.select_endpoint(endpoints, client_info)
        
        if selected_endpoint:
            selected_endpoint.increment_connections()
            logger.debug(f"选择端点: {selected_endpoint.address} (策略: {strategy.value})")
        
        return selected_endpoint
    
    async def release_endpoint(self, endpoint: ServiceEndpoint):
        """释放服务端点"""
        endpoint.decrement_connections()
        logger.debug(f"释放端点: {endpoint.address}")
    
    async def add_endpoint(self, service_name: str, endpoint: ServiceEndpoint):
        """添加服务端点"""
        if service_name not in self.endpoints:
            self.endpoints[service_name] = []
        
        self.endpoints[service_name].append(endpoint)
        logger.info(f"添加端点 {endpoint.address} 到服务 {service_name}")
    
    async def remove_endpoint(self, service_name: str, endpoint_address: str):
        """移除服务端点"""
        if service_name in self.endpoints:
            self.endpoints[service_name] = [
                ep for ep in self.endpoints[service_name] 
                if ep.address != endpoint_address
            ]
            logger.info(f"从服务 {service_name} 移除端点 {endpoint_address}")
    
    async def update_endpoint_health(
        self, 
        service_name: str, 
        endpoint_address: str, 
        healthy: bool
    ):
        """更新端点健康状态"""
        if service_name in self.endpoints:
            for endpoint in self.endpoints[service_name]:
                if endpoint.address == endpoint_address:
                    endpoint.healthy = healthy
                    endpoint.last_health_check = time.time()
                    logger.info(f"更新端点 {endpoint_address} 健康状态: {healthy}")
                    break
    
    async def get_service_stats(self, service_name: str) -> Dict[str, Any]:
        """获取服务统计信息"""
        if service_name not in self.endpoints:
            return {}
        
        endpoints = self.endpoints[service_name]
        total_endpoints = len(endpoints)
        healthy_endpoints = len([ep for ep in endpoints if ep.healthy])
        available_endpoints = len([ep for ep in endpoints if ep.is_available()])
        total_connections = sum(ep.current_connections for ep in endpoints)
        
        return {
            'service_name': service_name,
            'total_endpoints': total_endpoints,
            'healthy_endpoints': healthy_endpoints,
            'available_endpoints': available_endpoints,
            'total_connections': total_connections,
            'endpoints': [
                {
                    'address': ep.address,
                    'healthy': ep.healthy,
                    'connections': ep.current_connections,
                    'max_connections': ep.max_connections,
                    'weight': ep.weight,
                    'response_time': ep.response_time,
                    'failure_count': ep.failure_count
                }
                for ep in endpoints
            ]
        }
    
    async def get_all_stats(self) -> Dict[str, Any]:
        """获取所有服务统计信息"""
        stats = {}
        for service_name in self.endpoints:
            stats[service_name] = await self.get_service_stats(service_name)
        
        return {
            'services': stats,
            'total_services': len(self.endpoints),
            'default_strategy': self.default_strategy.value,
            'available_strategies': [strategy.value for strategy in self.algorithms.keys()]
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        total_services = len(self.endpoints)
        healthy_services = 0
        total_endpoints = 0
        healthy_endpoints = 0
        
        for service_name, endpoints in self.endpoints.items():
            service_healthy = any(ep.healthy for ep in endpoints)
            if service_healthy:
                healthy_services += 1
            
            total_endpoints += len(endpoints)
            healthy_endpoints += len([ep for ep in endpoints if ep.healthy])
        
        status = "healthy" if healthy_services == total_services else "degraded"
        if healthy_services == 0:
            status = "unhealthy"
        
        return {
            'status': status,
            'total_services': total_services,
            'healthy_services': healthy_services,
            'total_endpoints': total_endpoints,
            'healthy_endpoints': healthy_endpoints,
            'timestamp': time.time()
        }
    
    async def shutdown(self):
        """关闭负载均衡器"""
        self.endpoints.clear()
        self.algorithms.clear()
        self.initialized = False
        logger.info("负载均衡器已关闭") 