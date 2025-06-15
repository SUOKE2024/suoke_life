#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能消息路由器
支持基于内容的路由、负载均衡、故障转移和路由规则引擎
"""

import asyncio
import json
import logging
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable
from collections import defaultdict, deque
import hashlib
import random

from .message_processor import MessageEnvelope, MessagePriority

logger = logging.getLogger(__name__)


class RoutingStrategy(Enum):
    """路由策略"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    CONTENT_BASED = "content_based"
    HASH_BASED = "hash_based"
    PRIORITY_BASED = "priority_based"
    GEOGRAPHIC = "geographic"
    RANDOM = "random"


class RouteStatus(Enum):
    """路由状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"


@dataclass
class RouteEndpoint:
    """路由端点"""
    id: str
    name: str
    address: str
    port: int
    weight: int = 1
    max_connections: int = 100
    current_connections: int = 0
    status: RouteStatus = RouteStatus.ACTIVE
    health_score: float = 1.0
    last_health_check: float = 0.0
    response_time: float = 0.0
    error_rate: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_load_factor(self) -> float:
        """获取负载因子"""
        if self.max_connections == 0:
            return 0.0
        return self.current_connections / self.max_connections
    
    def is_available(self) -> bool:
        """检查端点是否可用"""
        return (
            self.status == RouteStatus.ACTIVE and
            self.health_score > 0.5 and
            self.current_connections < self.max_connections
        )


@dataclass
class RoutingRule:
    """路由规则"""
    id: str
    name: str
    priority: int = 0
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    actions: List[Dict[str, Any]] = field(default_factory=list)
    enabled: bool = True
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    
    def matches(self, message: MessageEnvelope, context: Dict[str, Any] = None) -> bool:
        """检查消息是否匹配规则"""
        if not self.enabled:
            return False
        
        context = context or {}
        
        for condition in self.conditions:
            if not self._evaluate_condition(condition, message, context):
                return False
        
        return True
    
    def _evaluate_condition(self, condition: Dict[str, Any], message: MessageEnvelope, context: Dict[str, Any]) -> bool:
        """评估单个条件"""
        condition_type = condition.get('type')
        
        if condition_type == 'topic':
            pattern = condition.get('pattern', '')
            return re.match(pattern, message.topic) is not None
        
        elif condition_type == 'attribute':
            attr_name = condition.get('name')
            attr_value = condition.get('value')
            operator = condition.get('operator', 'equals')
            
            message_value = message.attributes.get(attr_name)
            if message_value is None:
                return False
            
            if operator == 'equals':
                return message_value == attr_value
            elif operator == 'contains':
                return attr_value in message_value
            elif operator == 'regex':
                return re.match(attr_value, message_value) is not None
            elif operator == 'in':
                return message_value in attr_value
        
        elif condition_type == 'priority':
            target_priority = MessagePriority(condition.get('value'))
            operator = condition.get('operator', 'equals')
            
            if operator == 'equals':
                return message.priority == target_priority
            elif operator == 'gte':
                return message.priority.value >= target_priority.value
            elif operator == 'lte':
                return message.priority.value <= target_priority.value
        
        elif condition_type == 'size':
            size_limit = condition.get('value', 0)
            operator = condition.get('operator', 'lte')
            message_size = len(message.payload)
            
            if operator == 'lte':
                return message_size <= size_limit
            elif operator == 'gte':
                return message_size >= size_limit
            elif operator == 'equals':
                return message_size == size_limit
        
        elif condition_type == 'time':
            time_condition = condition.get('value')
            current_time = time.time()
            
            if 'start' in time_condition and 'end' in time_condition:
                return time_condition['start'] <= current_time <= time_condition['end']
        
        elif condition_type == 'context':
            context_key = condition.get('key')
            context_value = condition.get('value')
            operator = condition.get('operator', 'equals')
            
            actual_value = context.get(context_key)
            if actual_value is None:
                return False
            
            if operator == 'equals':
                return actual_value == context_value
            elif operator == 'contains':
                return context_value in str(actual_value)
        
        return False


@dataclass
class RoutingConfig:
    """路由配置"""
    default_strategy: RoutingStrategy = RoutingStrategy.ROUND_ROBIN
    health_check_enabled: bool = True
    health_check_interval: float = 30.0
    health_check_timeout: float = 5.0
    failover_enabled: bool = True
    circuit_breaker_enabled: bool = True
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: float = 60.0
    load_balancing_enabled: bool = True
    sticky_sessions: bool = False
    session_timeout: float = 300.0
    metrics_enabled: bool = True


class RoutingStrategy(ABC):
    """路由策略抽象基类"""
    
    @abstractmethod
    def select_endpoint(
        self, 
        endpoints: List[RouteEndpoint], 
        message: MessageEnvelope,
        context: Dict[str, Any] = None
    ) -> Optional[RouteEndpoint]:
        """选择路由端点"""
        pass


class RoundRobinStrategy(RoutingStrategy):
    """轮询路由策略"""
    
    def __init__(self):
        self._current_index = 0
    
    def select_endpoint(
        self, 
        endpoints: List[RouteEndpoint], 
        message: MessageEnvelope,
        context: Dict[str, Any] = None
    ) -> Optional[RouteEndpoint]:
        """选择路由端点"""
        available_endpoints = [ep for ep in endpoints if ep.is_available()]
        
        if not available_endpoints:
            return None
        
        endpoint = available_endpoints[self._current_index % len(available_endpoints)]
        self._current_index += 1
        return endpoint


class WeightedRoundRobinStrategy(RoutingStrategy):
    """加权轮询路由策略"""
    
    def __init__(self):
        self._current_weights: Dict[str, int] = {}
    
    def select_endpoint(
        self, 
        endpoints: List[RouteEndpoint], 
        message: MessageEnvelope,
        context: Dict[str, Any] = None
    ) -> Optional[RouteEndpoint]:
        """选择路由端点"""
        available_endpoints = [ep for ep in endpoints if ep.is_available()]
        
        if not available_endpoints:
            return None
        
        # 计算有效权重
        total_weight = 0
        for endpoint in available_endpoints:
            if endpoint.id not in self._current_weights:
                self._current_weights[endpoint.id] = 0
            
            effective_weight = int(endpoint.weight * endpoint.health_score)
            self._current_weights[endpoint.id] += effective_weight
            total_weight += effective_weight
        
        # 选择权重最高的端点
        selected_endpoint = None
        max_weight = -1
        
        for endpoint in available_endpoints:
            if self._current_weights[endpoint.id] > max_weight:
                max_weight = self._current_weights[endpoint.id]
                selected_endpoint = endpoint
        
        # 减少选中端点的权重
        if selected_endpoint:
            self._current_weights[selected_endpoint.id] -= total_weight
        
        return selected_endpoint


class LeastConnectionsStrategy(RoutingStrategy):
    """最少连接路由策略"""
    
    def select_endpoint(
        self, 
        endpoints: List[RouteEndpoint], 
        message: MessageEnvelope,
        context: Dict[str, Any] = None
    ) -> Optional[RouteEndpoint]:
        """选择路由端点"""
        available_endpoints = [ep for ep in endpoints if ep.is_available()]
        
        if not available_endpoints:
            return None
        
        # 选择连接数最少的端点
        return min(available_endpoints, key=lambda ep: ep.current_connections)


class ContentBasedStrategy(RoutingStrategy):
    """基于内容的路由策略"""
    
    def __init__(self, routing_rules: List[RoutingRule]):
        self.routing_rules = sorted(routing_rules, key=lambda r: r.priority, reverse=True)
    
    def select_endpoint(
        self, 
        endpoints: List[RouteEndpoint], 
        message: MessageEnvelope,
        context: Dict[str, Any] = None
    ) -> Optional[RouteEndpoint]:
        """选择路由端点"""
        context = context or {}
        
        # 根据路由规则选择端点
        for rule in self.routing_rules:
            if rule.matches(message, context):
                target_endpoints = self._get_target_endpoints(rule, endpoints)
                if target_endpoints:
                    # 使用轮询策略从匹配的端点中选择
                    available_endpoints = [ep for ep in target_endpoints if ep.is_available()]
                    if available_endpoints:
                        return random.choice(available_endpoints)
        
        # 如果没有匹配的规则，使用默认策略
        available_endpoints = [ep for ep in endpoints if ep.is_available()]
        return random.choice(available_endpoints) if available_endpoints else None
    
    def _get_target_endpoints(self, rule: RoutingRule, endpoints: List[RouteEndpoint]) -> List[RouteEndpoint]:
        """根据规则获取目标端点"""
        target_endpoints = []
        
        for action in rule.actions:
            if action.get('type') == 'route_to':
                endpoint_ids = action.get('endpoints', [])
                for endpoint in endpoints:
                    if endpoint.id in endpoint_ids:
                        target_endpoints.append(endpoint)
        
        return target_endpoints


class HashBasedStrategy(RoutingStrategy):
    """基于哈希的路由策略"""
    
    def __init__(self, hash_key: str = 'topic'):
        self.hash_key = hash_key
    
    def select_endpoint(
        self, 
        endpoints: List[RouteEndpoint], 
        message: MessageEnvelope,
        context: Dict[str, Any] = None
    ) -> Optional[RouteEndpoint]:
        """选择路由端点"""
        available_endpoints = [ep for ep in endpoints if ep.is_available()]
        
        if not available_endpoints:
            return None
        
        # 根据哈希键计算哈希值
        if self.hash_key == 'topic':
            hash_value = hashlib.md5(message.topic.encode()).hexdigest()
        elif self.hash_key == 'message_id':
            hash_value = hashlib.md5(message.id.encode()).hexdigest()
        else:
            # 使用属性作为哈希键
            attr_value = message.attributes.get(self.hash_key, '')
            hash_value = hashlib.md5(attr_value.encode()).hexdigest()
        
        # 选择端点
        index = int(hash_value, 16) % len(available_endpoints)
        return available_endpoints[index]


class PriorityBasedStrategy(RoutingStrategy):
    """基于优先级的路由策略"""
    
    def select_endpoint(
        self, 
        endpoints: List[RouteEndpoint], 
        message: MessageEnvelope,
        context: Dict[str, Any] = None
    ) -> Optional[RouteEndpoint]:
        """选择路由端点"""
        available_endpoints = [ep for ep in endpoints if ep.is_available()]
        
        if not available_endpoints:
            return None
        
        # 根据消息优先级选择端点
        if message.priority == MessagePriority.CRITICAL:
            # 关键消息选择健康分数最高的端点
            return max(available_endpoints, key=lambda ep: ep.health_score)
        elif message.priority == MessagePriority.HIGH:
            # 高优先级消息选择负载最低的端点
            return min(available_endpoints, key=lambda ep: ep.get_load_factor())
        else:
            # 普通消息使用轮询
            return random.choice(available_endpoints)


class SmartMessageRouter:
    """
    智能消息路由器
    支持多种路由策略、健康检查、故障转移和负载均衡
    """
    
    def __init__(self, config: RoutingConfig):
        self.config = config
        self.endpoints: Dict[str, RouteEndpoint] = {}
        self.routing_rules: List[RoutingRule] = []
        self.strategies: Dict[RoutingStrategy, RoutingStrategy] = {}
        
        # 初始化路由策略
        self._init_strategies()
        
        # 会话管理
        self.sessions: Dict[str, str] = {}  # session_id -> endpoint_id
        self.session_timestamps: Dict[str, float] = {}
        
        # 熔断器状态
        self.circuit_breakers: Dict[str, Dict] = {}  # endpoint_id -> circuit_breaker_state
        
        # 统计信息
        self.routing_stats: Dict[str, int] = defaultdict(int)
        self.endpoint_stats: Dict[str, Dict] = defaultdict(dict)
        
        # 运行状态
        self._running = False
        self._health_check_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
    
    def _init_strategies(self):
        """初始化路由策略"""
        self.strategies = {
            RoutingStrategy.ROUND_ROBIN: RoundRobinStrategy(),
            RoutingStrategy.WEIGHTED_ROUND_ROBIN: WeightedRoundRobinStrategy(),
            RoutingStrategy.LEAST_CONNECTIONS: LeastConnectionsStrategy(),
            RoutingStrategy.CONTENT_BASED: ContentBasedStrategy(self.routing_rules),
            RoutingStrategy.HASH_BASED: HashBasedStrategy(),
            RoutingStrategy.PRIORITY_BASED: PriorityBasedStrategy(),
        }
    
    async def start(self):
        """启动路由器"""
        if self._running:
            return
        
        self._running = True
        
        # 启动健康检查
        if self.config.health_check_enabled:
            self._health_check_task = asyncio.create_task(self._health_check_loop())
        
        # 启动清理任务
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info("智能消息路由器已启动")
    
    async def stop(self):
        """停止路由器"""
        if not self._running:
            return
        
        self._running = False
        
        # 停止健康检查
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        # 停止清理任务
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        logger.info("智能消息路由器已停止")
    
    def add_endpoint(self, endpoint: RouteEndpoint):
        """添加路由端点"""
        self.endpoints[endpoint.id] = endpoint
        self.circuit_breakers[endpoint.id] = {
            'state': 'closed',
            'failure_count': 0,
            'last_failure_time': 0,
            'next_attempt_time': 0
        }
        logger.info(f"添加路由端点: {endpoint.name} ({endpoint.address}:{endpoint.port})")
    
    def remove_endpoint(self, endpoint_id: str):
        """移除路由端点"""
        if endpoint_id in self.endpoints:
            endpoint = self.endpoints.pop(endpoint_id)
            self.circuit_breakers.pop(endpoint_id, None)
            logger.info(f"移除路由端点: {endpoint.name}")
    
    def add_routing_rule(self, rule: RoutingRule):
        """添加路由规则"""
        self.routing_rules.append(rule)
        self.routing_rules.sort(key=lambda r: r.priority, reverse=True)
        
        # 更新基于内容的路由策略
        self.strategies[RoutingStrategy.CONTENT_BASED] = ContentBasedStrategy(self.routing_rules)
        
        logger.info(f"添加路由规则: {rule.name}")
    
    def remove_routing_rule(self, rule_id: str):
        """移除路由规则"""
        self.routing_rules = [r for r in self.routing_rules if r.id != rule_id]
        
        # 更新基于内容的路由策略
        self.strategies[RoutingStrategy.CONTENT_BASED] = ContentBasedStrategy(self.routing_rules)
        
        logger.info(f"移除路由规则: {rule_id}")
    
    async def route_message(
        self, 
        message: MessageEnvelope, 
        strategy: Optional[RoutingStrategy] = None,
        context: Dict[str, Any] = None
    ) -> Optional[RouteEndpoint]:
        """路由消息到合适的端点"""
        if not self.endpoints:
            logger.warning("没有可用的路由端点")
            return None
        
        strategy = strategy or self.config.default_strategy
        context = context or {}
        
        # 检查粘性会话
        if self.config.sticky_sessions:
            session_id = context.get('session_id')
            if session_id and session_id in self.sessions:
                endpoint_id = self.sessions[session_id]
                endpoint = self.endpoints.get(endpoint_id)
                if endpoint and endpoint.is_available():
                    self._update_session_timestamp(session_id)
                    return endpoint
        
        # 使用路由策略选择端点
        routing_strategy = self.strategies.get(strategy)
        if not routing_strategy:
            logger.error(f"不支持的路由策略: {strategy}")
            return None
        
        available_endpoints = [
            ep for ep in self.endpoints.values() 
            if ep.is_available() and self._is_circuit_breaker_closed(ep.id)
        ]
        
        if not available_endpoints:
            # 尝试故障转移
            if self.config.failover_enabled:
                return await self._failover_route(message, context)
            return None
        
        selected_endpoint = routing_strategy.select_endpoint(available_endpoints, message, context)
        
        if selected_endpoint:
            # 更新统计信息
            self.routing_stats[f"strategy_{strategy.value}"] += 1
            self.routing_stats[f"endpoint_{selected_endpoint.id}"] += 1
            
            # 更新粘性会话
            if self.config.sticky_sessions:
                session_id = context.get('session_id')
                if session_id:
                    self.sessions[session_id] = selected_endpoint.id
                    self._update_session_timestamp(session_id)
            
            # 增加连接计数
            selected_endpoint.current_connections += 1
        
        return selected_endpoint
    
    async def _failover_route(self, message: MessageEnvelope, context: Dict[str, Any]) -> Optional[RouteEndpoint]:
        """故障转移路由"""
        # 尝试使用降级的端点
        degraded_endpoints = [
            ep for ep in self.endpoints.values() 
            if ep.status == RouteStatus.DEGRADED and ep.health_score > 0.3
        ]
        
        if degraded_endpoints:
            # 选择健康分数最高的降级端点
            return max(degraded_endpoints, key=lambda ep: ep.health_score)
        
        # 尝试打开熔断器
        for endpoint_id, cb_state in self.circuit_breakers.items():
            if cb_state['state'] == 'open' and time.time() >= cb_state['next_attempt_time']:
                endpoint = self.endpoints.get(endpoint_id)
                if endpoint:
                    cb_state['state'] = 'half_open'
                    logger.info(f"熔断器半开: {endpoint.name}")
                    return endpoint
        
        return None
    
    def release_endpoint(self, endpoint: RouteEndpoint, success: bool, response_time: float = 0.0):
        """释放端点连接"""
        if endpoint.id in self.endpoints:
            # 减少连接计数
            endpoint.current_connections = max(0, endpoint.current_connections - 1)
            
            # 更新响应时间
            if response_time > 0:
                if endpoint.response_time == 0:
                    endpoint.response_time = response_time
                else:
                    # 指数移动平均
                    alpha = 0.1
                    endpoint.response_time = alpha * response_time + (1 - alpha) * endpoint.response_time
            
            # 更新熔断器状态
            self._update_circuit_breaker(endpoint.id, success)
            
            # 更新统计信息
            if success:
                self.routing_stats[f"success_{endpoint.id}"] += 1
            else:
                self.routing_stats[f"failure_{endpoint.id}"] += 1
    
    def _update_circuit_breaker(self, endpoint_id: str, success: bool):
        """更新熔断器状态"""
        if not self.config.circuit_breaker_enabled:
            return
        
        cb_state = self.circuit_breakers.get(endpoint_id)
        if not cb_state:
            return
        
        current_time = time.time()
        
        if success:
            if cb_state['state'] == 'half_open':
                # 半开状态下成功，关闭熔断器
                cb_state['state'] = 'closed'
                cb_state['failure_count'] = 0
                logger.info(f"熔断器关闭: {endpoint_id}")
            elif cb_state['state'] == 'closed':
                # 重置失败计数
                cb_state['failure_count'] = max(0, cb_state['failure_count'] - 1)
        else:
            cb_state['failure_count'] += 1
            cb_state['last_failure_time'] = current_time
            
            if cb_state['failure_count'] >= self.config.circuit_breaker_threshold:
                if cb_state['state'] != 'open':
                    # 打开熔断器
                    cb_state['state'] = 'open'
                    cb_state['next_attempt_time'] = current_time + self.config.circuit_breaker_timeout
                    logger.warning(f"熔断器打开: {endpoint_id}")
    
    def _is_circuit_breaker_closed(self, endpoint_id: str) -> bool:
        """检查熔断器是否关闭"""
        if not self.config.circuit_breaker_enabled:
            return True
        
        cb_state = self.circuit_breakers.get(endpoint_id)
        if not cb_state:
            return True
        
        return cb_state['state'] in ['closed', 'half_open']
    
    def _update_session_timestamp(self, session_id: str):
        """更新会话时间戳"""
        self.session_timestamps[session_id] = time.time()
    
    async def _health_check_loop(self):
        """健康检查循环"""
        while self._running:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"健康检查出错: {e}")
    
    async def _perform_health_checks(self):
        """执行健康检查"""
        tasks = []
        for endpoint in self.endpoints.values():
            task = asyncio.create_task(self._check_endpoint_health(endpoint))
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_endpoint_health(self, endpoint: RouteEndpoint):
        """检查端点健康状态"""
        try:
            # 这里应该实现实际的健康检查逻辑
            # 例如发送HTTP请求或TCP连接测试
            
            # 模拟健康检查
            start_time = time.time()
            
            # 实际的健康检查逻辑应该在这里实现
            # 例如：
            # async with aiohttp.ClientSession() as session:
            #     async with session.get(f"http://{endpoint.address}:{endpoint.port}/health") as response:
            #         if response.status == 200:
            #             endpoint.health_score = 1.0
            #         else:
            #             endpoint.health_score = 0.5
            
            # 模拟检查结果
            check_time = time.time() - start_time
            
            # 根据响应时间调整健康分数
            if check_time < 0.1:
                endpoint.health_score = min(1.0, endpoint.health_score + 0.1)
            elif check_time > 1.0:
                endpoint.health_score = max(0.0, endpoint.health_score - 0.2)
            
            endpoint.last_health_check = time.time()
            
        except Exception as e:
            logger.error(f"端点 {endpoint.name} 健康检查失败: {e}")
            endpoint.health_score = max(0.0, endpoint.health_score - 0.3)
            if endpoint.health_score < 0.3:
                endpoint.status = RouteStatus.DEGRADED
    
    async def _cleanup_loop(self):
        """清理循环"""
        while self._running:
            try:
                await asyncio.sleep(60)  # 每分钟清理一次
                await self._cleanup_sessions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"清理任务出错: {e}")
    
    async def _cleanup_sessions(self):
        """清理过期会话"""
        if not self.config.sticky_sessions:
            return
        
        current_time = time.time()
        expired_sessions = []
        
        for session_id, timestamp in self.session_timestamps.items():
            if current_time - timestamp > self.config.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.sessions.pop(session_id, None)
            self.session_timestamps.pop(session_id, None)
        
        if expired_sessions:
            logger.info(f"清理了 {len(expired_sessions)} 个过期会话")
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """获取路由统计信息"""
        return {
            'total_endpoints': len(self.endpoints),
            'active_endpoints': sum(1 for ep in self.endpoints.values() if ep.status == RouteStatus.ACTIVE),
            'routing_stats': dict(self.routing_stats),
            'circuit_breaker_stats': {
                endpoint_id: cb_state['state']
                for endpoint_id, cb_state in self.circuit_breakers.items()
            },
            'session_count': len(self.sessions) if self.config.sticky_sessions else 0,
            'endpoint_health': {
                endpoint_id: {
                    'health_score': ep.health_score,
                    'current_connections': ep.current_connections,
                    'load_factor': ep.get_load_factor(),
                    'status': ep.status.value
                }
                for endpoint_id, ep in self.endpoints.items()
            }
        }
    
    def get_endpoint_by_id(self, endpoint_id: str) -> Optional[RouteEndpoint]:
        """根据ID获取端点"""
        return self.endpoints.get(endpoint_id)
    
    def update_endpoint_status(self, endpoint_id: str, status: RouteStatus):
        """更新端点状态"""
        endpoint = self.endpoints.get(endpoint_id)
        if endpoint:
            endpoint.status = status
            logger.info(f"端点 {endpoint.name} 状态更新为: {status.value}")


# 路由器工厂
class RouterFactory:
    """路由器工厂"""
    
    @staticmethod
    def create_smart_router(config: Optional[RoutingConfig] = None) -> SmartMessageRouter:
        """创建智能路由器"""
        if config is None:
            config = RoutingConfig()
        
        return SmartMessageRouter(config) 