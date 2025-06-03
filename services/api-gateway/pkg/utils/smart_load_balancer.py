#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能负载均衡器
支持多种负载均衡算法、健康检查和自适应权重调整
"""

import asyncio
import logging
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

import aiohttp

logger = logging.getLogger(__name__)

class LoadBalancerAlgorithm(Enum):
    """负载均衡算法"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_LEAST_CONNECTIONS = "weighted_least_connections"
    RANDOM = "random"
    WEIGHTED_RANDOM = "weighted_random"
    IP_HASH = "ip_hash"
    CONSISTENT_HASH = "consistent_hash"
    RESPONSE_TIME = "response_time"

@dataclass
class EndpointConfig:
    """端点配置"""
    host: str
    port: int
    weight: int = 1
    max_connections: int = 100
    use_tls: bool = False
    health_check_path: str = "/health"
    health_check_interval: int = 30
    health_check_timeout: int = 5
    health_check_retries: int = 3

@dataclass
class EndpointStats:
    """端点统计信息"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    active_connections: int = 0
    average_response_time: float = 0.0
    last_response_time: float = 0.0
    health_check_failures: int = 0
    last_health_check: float = 0.0
    is_healthy: bool = True
    weight_factor: float = 1.0  # 动态权重因子

@dataclass
class LoadBalancerConfig:
    """负载均衡器配置"""
    algorithm: LoadBalancerAlgorithm = LoadBalancerAlgorithm.ROUND_ROBIN
    health_check_enabled: bool = True
    health_check_interval: int = 30
    adaptive_weights: bool = True
    weight_adjustment_interval: int = 60
    max_weight_factor: float = 2.0
    min_weight_factor: float = 0.1

class LoadBalancerStrategy(ABC):
    """负载均衡策略抽象基类"""
    
    @abstractmethod
    def select_endpoint(
        self, 
        endpoints: List[EndpointConfig], 
        endpoint_stats: Dict[str, EndpointStats],
        client_ip: Optional[str] = None
    ) -> Optional[EndpointConfig]:
        """选择端点"""
        pass

class RoundRobinStrategy(LoadBalancerStrategy):
    """轮询策略"""
    
    def __init__(self):
        self._current_index = 0
    
    def select_endpoint(
        self, 
        endpoints: List[EndpointConfig], 
        endpoint_stats: Dict[str, EndpointStats],
        client_ip: Optional[str] = None
    ) -> Optional[EndpointConfig]:
        """选择端点"""
        healthy_endpoints = [
            ep for ep in endpoints 
            if endpoint_stats.get(f"{ep.host}:{ep.port}", EndpointStats()).is_healthy
        ]
        
        if not healthy_endpoints:
            return None
        
        endpoint = healthy_endpoints[self._current_index % len(healthy_endpoints)]
        self._current_index += 1
        return endpoint

class WeightedRoundRobinStrategy(LoadBalancerStrategy):
    """加权轮询策略"""
    
    def __init__(self):
        self._current_weights: Dict[str, int] = {}
    
    def select_endpoint(
        self, 
        endpoints: List[EndpointConfig], 
        endpoint_stats: Dict[str, EndpointStats],
        client_ip: Optional[str] = None
    ) -> Optional[EndpointConfig]:
        """选择端点"""
        healthy_endpoints = [
            ep for ep in endpoints 
            if endpoint_stats.get(f"{ep.host}:{ep.port}", EndpointStats()).is_healthy
        ]
        
        if not healthy_endpoints:
            return None
        
        # 计算有效权重
        total_weight = 0
        for endpoint in healthy_endpoints:
            key = f"{endpoint.host}:{endpoint.port}"
            stats = endpoint_stats.get(key, EndpointStats())
            effective_weight = int(endpoint.weight * stats.weight_factor)
            
            if key not in self._current_weights:
                self._current_weights[key] = 0
            
            self._current_weights[key] += effective_weight
            total_weight += effective_weight
        
        # 选择权重最高的端点
        selected_endpoint = None
        max_weight = -1
        
        for endpoint in healthy_endpoints:
            key = f"{endpoint.host}:{endpoint.port}"
            if self._current_weights[key] > max_weight:
                max_weight = self._current_weights[key]
                selected_endpoint = endpoint
        
        # 减少选中端点的权重
        if selected_endpoint:
            key = f"{selected_endpoint.host}:{selected_endpoint.port}"
            self._current_weights[key] -= total_weight
        
        return selected_endpoint

class LeastConnectionsStrategy(LoadBalancerStrategy):
    """最少连接策略"""
    
    def select_endpoint(
        self, 
        endpoints: List[EndpointConfig], 
        endpoint_stats: Dict[str, EndpointStats],
        client_ip: Optional[str] = None
    ) -> Optional[EndpointConfig]:
        """选择端点"""
        healthy_endpoints = [
            ep for ep in endpoints 
            if endpoint_stats.get(f"{ep.host}:{ep.port}", EndpointStats()).is_healthy
        ]
        
        if not healthy_endpoints:
            return None
        
        # 选择连接数最少的端点
        min_connections = float('inf')
        selected_endpoint = None
        
        for endpoint in healthy_endpoints:
            key = f"{endpoint.host}:{endpoint.port}"
            stats = endpoint_stats.get(key, EndpointStats())
            
            if stats.active_connections < min_connections:
                min_connections = stats.active_connections
                selected_endpoint = endpoint
        
        return selected_endpoint

class WeightedLeastConnectionsStrategy(LoadBalancerStrategy):
    """加权最少连接策略"""
    
    def select_endpoint(
        self, 
        endpoints: List[EndpointConfig], 
        endpoint_stats: Dict[str, EndpointStats],
        client_ip: Optional[str] = None
    ) -> Optional[EndpointConfig]:
        """选择端点"""
        healthy_endpoints = [
            ep for ep in endpoints 
            if endpoint_stats.get(f"{ep.host}:{ep.port}", EndpointStats()).is_healthy
        ]
        
        if not healthy_endpoints:
            return None
        
        # 选择连接数/权重比最小的端点
        min_ratio = float('inf')
        selected_endpoint = None
        
        for endpoint in healthy_endpoints:
            key = f"{endpoint.host}:{endpoint.port}"
            stats = endpoint_stats.get(key, EndpointStats())
            effective_weight = endpoint.weight * stats.weight_factor
            
            if effective_weight > 0:
                ratio = stats.active_connections / effective_weight
                if ratio < min_ratio:
                    min_ratio = ratio
                    selected_endpoint = endpoint
        
        return selected_endpoint

class RandomStrategy(LoadBalancerStrategy):
    """随机策略"""
    
    def select_endpoint(
        self, 
        endpoints: List[EndpointConfig], 
        endpoint_stats: Dict[str, EndpointStats],
        client_ip: Optional[str] = None
    ) -> Optional[EndpointConfig]:
        """选择端点"""
        healthy_endpoints = [
            ep for ep in endpoints 
            if endpoint_stats.get(f"{ep.host}:{ep.port}", EndpointStats()).is_healthy
        ]
        
        if not healthy_endpoints:
            return None
        
        return random.choice(healthy_endpoints)

class WeightedRandomStrategy(LoadBalancerStrategy):
    """加权随机策略"""
    
    def select_endpoint(
        self, 
        endpoints: List[EndpointConfig], 
        endpoint_stats: Dict[str, EndpointStats],
        client_ip: Optional[str] = None
    ) -> Optional[EndpointConfig]:
        """选择端点"""
        healthy_endpoints = [
            ep for ep in endpoints 
            if endpoint_stats.get(f"{ep.host}:{ep.port}", EndpointStats()).is_healthy
        ]
        
        if not healthy_endpoints:
            return None
        
        # 计算权重总和
        total_weight = 0
        weights = []
        
        for endpoint in healthy_endpoints:
            key = f"{endpoint.host}:{endpoint.port}"
            stats = endpoint_stats.get(key, EndpointStats())
            effective_weight = endpoint.weight * stats.weight_factor
            weights.append(effective_weight)
            total_weight += effective_weight
        
        if total_weight == 0:
            return random.choice(healthy_endpoints)
        
        # 随机选择
        rand_value = random.uniform(0, total_weight)
        current_weight = 0
        
        for i, weight in enumerate(weights):
            current_weight += weight
            if rand_value <= current_weight:
                return healthy_endpoints[i]
        
        return healthy_endpoints[-1]

class IPHashStrategy(LoadBalancerStrategy):
    """IP哈希策略"""
    
    def select_endpoint(
        self, 
        endpoints: List[EndpointConfig], 
        endpoint_stats: Dict[str, EndpointStats],
        client_ip: Optional[str] = None
    ) -> Optional[EndpointConfig]:
        """选择端点"""
        healthy_endpoints = [
            ep for ep in endpoints 
            if endpoint_stats.get(f"{ep.host}:{ep.port}", EndpointStats()).is_healthy
        ]
        
        if not healthy_endpoints:
            return None
        
        if not client_ip:
            return random.choice(healthy_endpoints)
        
        # 使用IP哈希选择端点
        hash_value = hash(client_ip)
        index = hash_value % len(healthy_endpoints)
        return healthy_endpoints[index]

class ResponseTimeStrategy(LoadBalancerStrategy):
    """响应时间策略"""
    
    def select_endpoint(
        self, 
        endpoints: List[EndpointConfig], 
        endpoint_stats: Dict[str, EndpointStats],
        client_ip: Optional[str] = None
    ) -> Optional[EndpointConfig]:
        """选择端点"""
        healthy_endpoints = [
            ep for ep in endpoints 
            if endpoint_stats.get(f"{ep.host}:{ep.port}", EndpointStats()).is_healthy
        ]
        
        if not healthy_endpoints:
            return None
        
        # 选择平均响应时间最短的端点
        min_response_time = float('inf')
        selected_endpoint = None
        
        for endpoint in healthy_endpoints:
            key = f"{endpoint.host}:{endpoint.port}"
            stats = endpoint_stats.get(key, EndpointStats())
            
            # 如果没有响应时间数据，给予较高优先级
            response_time = stats.average_response_time if stats.average_response_time > 0 else 0.001
            
            if response_time < min_response_time:
                min_response_time = response_time
                selected_endpoint = endpoint
        
        return selected_endpoint

class SmartLoadBalancer:
    """
    智能负载均衡器
    支持多种负载均衡算法、健康检查和自适应权重调整
    """
    
    def __init__(self, config: LoadBalancerConfig):
        self.config = config
        self.endpoints: List[EndpointConfig] = []
        self.endpoint_stats: Dict[str, EndpointStats] = {}
        self._strategies = self._init_strategies()
        self._current_strategy = self._strategies[config.algorithm]
        self._health_check_task: Optional[asyncio.Task] = None
        self._weight_adjustment_task: Optional[asyncio.Task] = None
        self._session: Optional[aiohttp.ClientSession] = None
    
    def _init_strategies(self) -> Dict[LoadBalancerAlgorithm, LoadBalancerStrategy]:
        """初始化负载均衡策略"""
        return {
            LoadBalancerAlgorithm.ROUND_ROBIN: RoundRobinStrategy(),
            LoadBalancerAlgorithm.WEIGHTED_ROUND_ROBIN: WeightedRoundRobinStrategy(),
            LoadBalancerAlgorithm.LEAST_CONNECTIONS: LeastConnectionsStrategy(),
            LoadBalancerAlgorithm.WEIGHTED_LEAST_CONNECTIONS: WeightedLeastConnectionsStrategy(),
            LoadBalancerAlgorithm.RANDOM: RandomStrategy(),
            LoadBalancerAlgorithm.WEIGHTED_RANDOM: WeightedRandomStrategy(),
            LoadBalancerAlgorithm.IP_HASH: IPHashStrategy(),
            LoadBalancerAlgorithm.RESPONSE_TIME: ResponseTimeStrategy(),
        }
    
    async def start(self):
        """启动负载均衡器"""
        # 创建HTTP会话
        timeout = aiohttp.ClientTimeout(total=30)
        self._session = aiohttp.ClientSession(timeout=timeout)
        
        # 启动健康检查
        if self.config.health_check_enabled:
            self._health_check_task = asyncio.create_task(self._health_check_loop())
        
        # 启动权重调整
        if self.config.adaptive_weights:
            self._weight_adjustment_task = asyncio.create_task(self._weight_adjustment_loop())
        
        logger.info(f"智能负载均衡器已启动，算法: {self.config.algorithm.value}")
    
    async def stop(self):
        """停止负载均衡器"""
        # 停止任务
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        if self._weight_adjustment_task:
            self._weight_adjustment_task.cancel()
            try:
                await self._weight_adjustment_task
            except asyncio.CancelledError:
                pass
        
        # 关闭HTTP会话
        if self._session:
            await self._session.close()
            self._session = None
        
        logger.info("智能负载均衡器已停止")
    
    def add_endpoint(self, endpoint: EndpointConfig):
        """添加端点"""
        self.endpoints.append(endpoint)
        key = f"{endpoint.host}:{endpoint.port}"
        self.endpoint_stats[key] = EndpointStats()
        logger.info(f"添加端点: {key}")
    
    def remove_endpoint(self, host: str, port: int):
        """移除端点"""
        key = f"{host}:{port}"
        self.endpoints = [ep for ep in self.endpoints if f"{ep.host}:{ep.port}" != key]
        self.endpoint_stats.pop(key, None)
        logger.info(f"移除端点: {key}")
    
    def select_endpoint(self, client_ip: Optional[str] = None) -> Optional[EndpointConfig]:
        """选择端点"""
        return self._current_strategy.select_endpoint(
            self.endpoints, 
            self.endpoint_stats, 
            client_ip
        )
    
    def record_request_start(self, endpoint: EndpointConfig):
        """记录请求开始"""
        key = f"{endpoint.host}:{endpoint.port}"
        stats = self.endpoint_stats.get(key)
        if stats:
            stats.active_connections += 1
            stats.total_requests += 1
    
    def record_request_end(self, endpoint: EndpointConfig, success: bool, response_time: float):
        """记录请求结束"""
        key = f"{endpoint.host}:{endpoint.port}"
        stats = self.endpoint_stats.get(key)
        if stats:
            stats.active_connections = max(0, stats.active_connections - 1)
            stats.last_response_time = response_time
            
            if success:
                stats.successful_requests += 1
            else:
                stats.failed_requests += 1
            
            # 更新平均响应时间（指数移动平均）
            if stats.average_response_time == 0:
                stats.average_response_time = response_time
            else:
                alpha = 0.1  # 平滑因子
                stats.average_response_time = (
                    alpha * response_time + 
                    (1 - alpha) * stats.average_response_time
                )
    
    async def _health_check_loop(self):
        """健康检查循环"""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"健康检查出错: {e}")
    
    async def _perform_health_checks(self):
        """执行健康检查"""
        if not self._session:
            return
        
        tasks = []
        for endpoint in self.endpoints:
            task = asyncio.create_task(self._check_endpoint_health(endpoint))
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_endpoint_health(self, endpoint: EndpointConfig):
        """检查端点健康状态"""
        key = f"{endpoint.host}:{endpoint.port}"
        stats = self.endpoint_stats.get(key)
        if not stats:
            return
        
        protocol = "https" if endpoint.use_tls else "http"
        url = f"{protocol}://{endpoint.host}:{endpoint.port}{endpoint.health_check_path}"
        
        try:
            async with self._session.get(url, timeout=aiohttp.ClientTimeout(total=endpoint.health_check_timeout)) as response:
                if response.status == 200:
                    stats.is_healthy = True
                    stats.health_check_failures = 0
                    logger.debug(f"端点健康检查成功: {key}")
                else:
                    stats.health_check_failures += 1
                    if stats.health_check_failures >= endpoint.health_check_retries:
                        stats.is_healthy = False
                        logger.warning(f"端点健康检查失败: {key}, 状态码: {response.status}")
        except Exception as e:
            stats.health_check_failures += 1
            if stats.health_check_failures >= endpoint.health_check_retries:
                stats.is_healthy = False
                logger.warning(f"端点健康检查异常: {key}, 错误: {e}")
        
        stats.last_health_check = time.time()
    
    async def _weight_adjustment_loop(self):
        """权重调整循环"""
        while True:
            try:
                await asyncio.sleep(self.config.weight_adjustment_interval)
                self._adjust_weights()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"权重调整出错: {e}")
    
    def _adjust_weights(self):
        """调整权重"""
        if not self.endpoint_stats:
            return
        
        # 计算所有端点的平均响应时间和成功率
        total_response_time = 0
        total_success_rate = 0
        healthy_count = 0
        
        for stats in self.endpoint_stats.values():
            if stats.is_healthy and stats.total_requests > 0:
                total_response_time += stats.average_response_time
                success_rate = stats.successful_requests / stats.total_requests
                total_success_rate += success_rate
                healthy_count += 1
        
        if healthy_count == 0:
            return
        
        avg_response_time = total_response_time / healthy_count
        avg_success_rate = total_success_rate / healthy_count
        
        # 调整每个端点的权重因子
        for key, stats in self.endpoint_stats.items():
            if not stats.is_healthy or stats.total_requests == 0:
                continue
            
            success_rate = stats.successful_requests / stats.total_requests
            
            # 基于响应时间和成功率计算权重因子
            response_time_factor = avg_response_time / max(stats.average_response_time, 0.001)
            success_rate_factor = success_rate / max(avg_success_rate, 0.001)
            
            # 综合权重因子
            weight_factor = (response_time_factor + success_rate_factor) / 2
            
            # 限制权重因子范围
            weight_factor = max(self.config.min_weight_factor, 
                              min(self.config.max_weight_factor, weight_factor))
            
            stats.weight_factor = weight_factor
            
            logger.debug(f"调整端点权重: {key}, 权重因子: {weight_factor:.2f}")
    
    def get_stats(self) -> Dict[str, Dict]:
        """获取负载均衡器统计信息"""
        return {
            "algorithm": self.config.algorithm.value,
            "total_endpoints": len(self.endpoints),
            "healthy_endpoints": sum(1 for stats in self.endpoint_stats.values() if stats.is_healthy),
            "endpoint_stats": {
                key: {
                    "total_requests": stats.total_requests,
                    "successful_requests": stats.successful_requests,
                    "failed_requests": stats.failed_requests,
                    "active_connections": stats.active_connections,
                    "average_response_time": stats.average_response_time,
                    "is_healthy": stats.is_healthy,
                    "weight_factor": stats.weight_factor,
                }
                for key, stats in self.endpoint_stats.items()
            }
        }
    
    def set_algorithm(self, algorithm: LoadBalancerAlgorithm):
        """设置负载均衡算法"""
        if algorithm in self._strategies:
            self.config.algorithm = algorithm
            self._current_strategy = self._strategies[algorithm]
            logger.info(f"负载均衡算法已切换为: {algorithm.value}")
        else:
            logger.error(f"不支持的负载均衡算法: {algorithm}")

# 负载均衡器工厂
class LoadBalancerFactory:
    """负载均衡器工厂"""
    
    @staticmethod
    def create_load_balancer(
        algorithm: LoadBalancerAlgorithm = LoadBalancerAlgorithm.ROUND_ROBIN,
        **kwargs
    ) -> SmartLoadBalancer:
        """创建负载均衡器"""
        config = LoadBalancerConfig(algorithm=algorithm, **kwargs)
        return SmartLoadBalancer(config) 