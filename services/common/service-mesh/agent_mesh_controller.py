#!/usr/bin/env python3
"""
智能体服务网格控制器
实现智能体间的动态服务发现、负载均衡、智能路由和熔断保护
"""

import asyncio
import json
import logging
import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import uuid4
import hashlib

import aioredis
import aiohttp

from ..service_registry.agent_discovery import (
    AgentType, CapabilityType, AgentServiceInfo, AgentServiceRegistry, get_agent_registry
)

logger = logging.getLogger(__name__)


class LoadBalancingStrategy(Enum):
    """负载均衡策略"""
    ROUND_ROBIN = "round_robin"           # 轮询
    WEIGHTED_ROUND_ROBIN = "weighted_rr"  # 加权轮询
    LEAST_CONNECTIONS = "least_conn"      # 最少连接
    LEAST_RESPONSE_TIME = "least_rt"      # 最短响应时间
    CONSISTENT_HASH = "consistent_hash"   # 一致性哈希
    CAPABILITY_BASED = "capability_based" # 基于能力的路由
    INTELLIGENT = "intelligent"           # 智能路由


class CircuitBreakerState(Enum):
    """熔断器状态"""
    CLOSED = "closed"       # 关闭（正常）
    OPEN = "open"          # 开启（熔断）
    HALF_OPEN = "half_open" # 半开（试探）


class HealthStatus(Enum):
    """健康状态"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ServiceMetrics:
    """服务指标"""
    service_id: str
    request_count: int = 0
    success_count: int = 0
    error_count: int = 0
    total_response_time: float = 0.0
    active_connections: int = 0
    last_request_time: Optional[datetime] = None
    last_error_time: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.request_count == 0:
            return 1.0
        return self.success_count / self.request_count
    
    @property
    def error_rate(self) -> float:
        """错误率"""
        if self.request_count == 0:
            return 0.0
        return self.error_count / self.request_count
    
    @property
    def average_response_time(self) -> float:
        """平均响应时间"""
        if self.success_count == 0:
            return 0.0
        return self.total_response_time / self.success_count


@dataclass
class CircuitBreaker:
    """熔断器"""
    service_id: str
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = 0
    failure_threshold: int = 5
    timeout_duration: int = 60  # 秒
    half_open_max_calls: int = 3
    half_open_calls: int = 0
    last_failure_time: Optional[datetime] = None
    state_change_time: datetime = field(default_factory=datetime.now)
    
    def should_allow_request(self) -> bool:
        """是否允许请求"""
        now = datetime.now()
        
        if self.state == CircuitBreakerState.CLOSED:
            return True
        elif self.state == CircuitBreakerState.OPEN:
            # 检查是否可以转为半开状态
            if (now - self.state_change_time).total_seconds() >= self.timeout_duration:
                self.state = CircuitBreakerState.HALF_OPEN
                self.half_open_calls = 0
                self.state_change_time = now
                return True
            return False
        elif self.state == CircuitBreakerState.HALF_OPEN:
            return self.half_open_calls < self.half_open_max_calls
        
        return False
    
    def record_success(self):
        """记录成功"""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.half_open_calls += 1
            if self.half_open_calls >= self.half_open_max_calls:
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
                self.state_change_time = datetime.now()
        elif self.state == CircuitBreakerState.CLOSED:
            self.failure_count = 0
    
    def record_failure(self):
        """记录失败"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == CircuitBreakerState.CLOSED:
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitBreakerState.OPEN
                self.state_change_time = datetime.now()
        elif self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.OPEN
            self.state_change_time = datetime.now()


@dataclass
class RoutingRule:
    """路由规则"""
    rule_id: str
    agent_type: Optional[AgentType] = None
    capability_type: Optional[CapabilityType] = None
    source_pattern: Optional[str] = None
    target_services: List[str] = field(default_factory=list)
    weight_distribution: Dict[str, float] = field(default_factory=dict)
    conditions: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    enabled: bool = True


@dataclass
class RequestContext:
    """请求上下文"""
    request_id: str
    source_service: str
    target_capability: CapabilityType
    agent_type: Optional[AgentType] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class AgentMeshController:
    """智能体服务网格控制器"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis: Optional[aioredis.Redis] = None
        self.service_registry: Optional[AgentServiceRegistry] = None
        
        # 负载均衡器
        self.load_balancing_strategy = LoadBalancingStrategy.INTELLIGENT
        self.round_robin_counters: Dict[str, int] = {}
        
        # 服务指标
        self.service_metrics: Dict[str, ServiceMetrics] = {}
        
        # 熔断器
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # 路由规则
        self.routing_rules: List[RoutingRule] = []
        
        # 健康检查
        self.health_check_interval = 15  # 秒
        self.health_status: Dict[str, HealthStatus] = {}
        
        self._running = False
    
    async def initialize(self):
        """初始化服务网格控制器"""
        try:
            self.redis = aioredis.from_url(self.redis_url)
            await self.redis.ping()
            
            self.service_registry = await get_agent_registry()
            
            # 加载路由规则
            await self._load_routing_rules()
            
            logger.info("智能体服务网格控制器初始化成功")
            
            # 启动后台任务
            self._running = True
            asyncio.create_task(self._health_checker())
            asyncio.create_task(self._metrics_collector())
            asyncio.create_task(self._circuit_breaker_monitor())
            
        except Exception as e:
            logger.error(f"智能体服务网格控制器初始化失败: {e}")
            raise
    
    async def route_request(
        self,
        context: RequestContext
    ) -> Optional[AgentServiceInfo]:
        """路由请求到最佳服务"""
        try:
            # 获取候选服务
            candidate_services = await self._get_candidate_services(context)
            
            if not candidate_services:
                logger.warning(f"未找到候选服务: {context.target_capability.value}")
                return None
            
            # 过滤不健康的服务
            healthy_services = await self._filter_healthy_services(candidate_services)
            
            if not healthy_services:
                logger.warning(f"所有候选服务都不健康: {context.target_capability.value}")
                return None
            
            # 应用路由规则
            filtered_services = await self._apply_routing_rules(healthy_services, context)
            
            # 负载均衡选择
            selected_service = await self._select_service(filtered_services, context)
            
            if selected_service:
                # 记录路由决策
                await self._record_routing_decision(context, selected_service)
                
                logger.debug(f"路由请求成功: {context.request_id} -> {selected_service.service_id}")
            
            return selected_service
            
        except Exception as e:
            logger.error(f"路由请求失败: {e}")
            return None
    
    async def record_request_result(
        self,
        service_id: str,
        success: bool,
        response_time: float,
        error_message: Optional[str] = None
    ):
        """记录请求结果"""
        try:
            # 更新服务指标
            if service_id not in self.service_metrics:
                self.service_metrics[service_id] = ServiceMetrics(service_id=service_id)
            
            metrics = self.service_metrics[service_id]
            metrics.request_count += 1
            metrics.last_request_time = datetime.now()
            
            if success:
                metrics.success_count += 1
                metrics.total_response_time += response_time
                
                # 熔断器记录成功
                if service_id in self.circuit_breakers:
                    self.circuit_breakers[service_id].record_success()
            else:
                metrics.error_count += 1
                metrics.last_error_time = datetime.now()
                
                # 熔断器记录失败
                if service_id not in self.circuit_breakers:
                    self.circuit_breakers[service_id] = CircuitBreaker(service_id=service_id)
                
                self.circuit_breakers[service_id].record_failure()
                
                logger.warning(f"服务请求失败: {service_id} - {error_message}")
            
            # 存储指标到Redis
            await self._store_metrics(service_id, metrics)
            
        except Exception as e:
            logger.error(f"记录请求结果失败: {e}")
    
    async def add_routing_rule(self, rule: RoutingRule):
        """添加路由规则"""
        try:
            # 检查规则是否已存在
            existing_rule = next(
                (r for r in self.routing_rules if r.rule_id == rule.rule_id),
                None
            )
            
            if existing_rule:
                # 更新现有规则
                self.routing_rules.remove(existing_rule)
            
            self.routing_rules.append(rule)
            
            # 按优先级排序
            self.routing_rules.sort(key=lambda r: r.priority, reverse=True)
            
            # 存储到Redis
            await self._store_routing_rules()
            
            logger.info(f"路由规则已添加: {rule.rule_id}")
            
        except Exception as e:
            logger.error(f"添加路由规则失败: {e}")
            raise
    
    async def remove_routing_rule(self, rule_id: str) -> bool:
        """移除路由规则"""
        try:
            rule = next(
                (r for r in self.routing_rules if r.rule_id == rule_id),
                None
            )
            
            if rule:
                self.routing_rules.remove(rule)
                await self._store_routing_rules()
                logger.info(f"路由规则已移除: {rule_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"移除路由规则失败: {e}")
            return False
    
    async def get_service_metrics(self, service_id: str) -> Optional[ServiceMetrics]:
        """获取服务指标"""
        return self.service_metrics.get(service_id)
    
    async def get_all_metrics(self) -> Dict[str, ServiceMetrics]:
        """获取所有服务指标"""
        return self.service_metrics.copy()
    
    async def get_circuit_breaker_status(self, service_id: str) -> Optional[CircuitBreaker]:
        """获取熔断器状态"""
        return self.circuit_breakers.get(service_id)
    
    async def reset_circuit_breaker(self, service_id: str) -> bool:
        """重置熔断器"""
        try:
            if service_id in self.circuit_breakers:
                cb = self.circuit_breakers[service_id]
                cb.state = CircuitBreakerState.CLOSED
                cb.failure_count = 0
                cb.half_open_calls = 0
                cb.state_change_time = datetime.now()
                
                logger.info(f"熔断器已重置: {service_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"重置熔断器失败: {e}")
            return False
    
    async def _get_candidate_services(
        self,
        context: RequestContext
    ) -> List[AgentServiceInfo]:
        """获取候选服务"""
        try:
            # 根据能力类型获取服务
            services = await self.service_registry.get_services_by_capability(
                context.target_capability
            )
            
            # 如果指定了智能体类型，进一步过滤
            if context.agent_type:
                services = [s for s in services if s.agent_type == context.agent_type]
            
            return services
            
        except Exception as e:
            logger.error(f"获取候选服务失败: {e}")
            return []
    
    async def _filter_healthy_services(
        self,
        services: List[AgentServiceInfo]
    ) -> List[AgentServiceInfo]:
        """过滤健康的服务"""
        healthy_services = []
        
        for service in services:
            # 检查熔断器状态
            if service.service_id in self.circuit_breakers:
                cb = self.circuit_breakers[service.service_id]
                if not cb.should_allow_request():
                    continue
            
            # 检查健康状态
            health_status = self.health_status.get(service.service_id, HealthStatus.UNKNOWN)
            if health_status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]:
                healthy_services.append(service)
        
        return healthy_services
    
    async def _apply_routing_rules(
        self,
        services: List[AgentServiceInfo],
        context: RequestContext
    ) -> List[AgentServiceInfo]:
        """应用路由规则"""
        try:
            # 如果没有路由规则，返回所有服务
            if not self.routing_rules:
                return services
            
            # 查找匹配的路由规则
            matching_rule = None
            for rule in self.routing_rules:
                if not rule.enabled:
                    continue
                
                # 检查智能体类型匹配
                if rule.agent_type and rule.agent_type != context.agent_type:
                    continue
                
                # 检查能力类型匹配
                if rule.capability_type and rule.capability_type != context.target_capability:
                    continue
                
                # 检查源服务匹配
                if rule.source_pattern and not self._match_pattern(
                    context.source_service, rule.source_pattern
                ):
                    continue
                
                # 检查其他条件
                if not self._check_rule_conditions(rule, context):
                    continue
                
                matching_rule = rule
                break
            
            # 如果找到匹配的规则，应用规则
            if matching_rule and matching_rule.target_services:
                target_service_ids = set(matching_rule.target_services)
                filtered_services = [
                    s for s in services if s.service_id in target_service_ids
                ]
                return filtered_services
            
            return services
            
        except Exception as e:
            logger.error(f"应用路由规则失败: {e}")
            return services
    
    async def _select_service(
        self,
        services: List[AgentServiceInfo],
        context: RequestContext
    ) -> Optional[AgentServiceInfo]:
        """选择服务"""
        if not services:
            return None
        
        if len(services) == 1:
            return services[0]
        
        try:
            if self.load_balancing_strategy == LoadBalancingStrategy.ROUND_ROBIN:
                return await self._round_robin_select(services, context)
            elif self.load_balancing_strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
                return await self._weighted_round_robin_select(services, context)
            elif self.load_balancing_strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
                return await self._least_connections_select(services, context)
            elif self.load_balancing_strategy == LoadBalancingStrategy.LEAST_RESPONSE_TIME:
                return await self._least_response_time_select(services, context)
            elif self.load_balancing_strategy == LoadBalancingStrategy.CONSISTENT_HASH:
                return await self._consistent_hash_select(services, context)
            elif self.load_balancing_strategy == LoadBalancingStrategy.CAPABILITY_BASED:
                return await self._capability_based_select(services, context)
            elif self.load_balancing_strategy == LoadBalancingStrategy.INTELLIGENT:
                return await self._intelligent_select(services, context)
            else:
                # 默认轮询
                return await self._round_robin_select(services, context)
                
        except Exception as e:
            logger.error(f"选择服务失败: {e}")
            return services[0]  # 返回第一个服务作为后备
    
    async def _round_robin_select(
        self,
        services: List[AgentServiceInfo],
        context: RequestContext
    ) -> AgentServiceInfo:
        """轮询选择"""
        key = f"rr:{context.target_capability.value}"
        
        if key not in self.round_robin_counters:
            self.round_robin_counters[key] = 0
        
        index = self.round_robin_counters[key] % len(services)
        self.round_robin_counters[key] += 1
        
        return services[index]
    
    async def _weighted_round_robin_select(
        self,
        services: List[AgentServiceInfo],
        context: RequestContext
    ) -> AgentServiceInfo:
        """加权轮询选择"""
        # 根据服务性能计算权重
        weights = []
        for service in services:
            metrics = self.service_metrics.get(service.service_id)
            if metrics:
                # 基于成功率和响应时间计算权重
                weight = metrics.success_rate * (1.0 / max(metrics.average_response_time, 1.0))
            else:
                weight = 1.0
            weights.append(weight)
        
        # 加权随机选择
        total_weight = sum(weights)
        if total_weight == 0:
            return services[0]
        
        rand_val = random.uniform(0, total_weight)
        current_weight = 0
        
        for i, weight in enumerate(weights):
            current_weight += weight
            if rand_val <= current_weight:
                return services[i]
        
        return services[-1]
    
    async def _least_connections_select(
        self,
        services: List[AgentServiceInfo],
        context: RequestContext
    ) -> AgentServiceInfo:
        """最少连接选择"""
        min_connections = float('inf')
        selected_service = services[0]
        
        for service in services:
            metrics = self.service_metrics.get(service.service_id)
            connections = metrics.active_connections if metrics else 0
            
            if connections < min_connections:
                min_connections = connections
                selected_service = service
        
        return selected_service
    
    async def _least_response_time_select(
        self,
        services: List[AgentServiceInfo],
        context: RequestContext
    ) -> AgentServiceInfo:
        """最短响应时间选择"""
        min_response_time = float('inf')
        selected_service = services[0]
        
        for service in services:
            metrics = self.service_metrics.get(service.service_id)
            response_time = metrics.average_response_time if metrics else 0.0
            
            if response_time < min_response_time:
                min_response_time = response_time
                selected_service = service
        
        return selected_service
    
    async def _consistent_hash_select(
        self,
        services: List[AgentServiceInfo],
        context: RequestContext
    ) -> AgentServiceInfo:
        """一致性哈希选择"""
        # 使用用户ID或会话ID作为哈希键
        hash_key = context.user_id or context.session_id or context.request_id
        
        # 计算哈希值
        hash_value = int(hashlib.md5(hash_key.encode()).hexdigest(), 16)
        
        # 选择服务
        index = hash_value % len(services)
        return services[index]
    
    async def _capability_based_select(
        self,
        services: List[AgentServiceInfo],
        context: RequestContext
    ) -> AgentServiceInfo:
        """基于能力的选择"""
        best_score = -1
        selected_service = services[0]
        
        for service in services:
            # 查找匹配的能力
            matching_capability = None
            for capability in service.capabilities:
                if capability.capability_type == context.target_capability:
                    matching_capability = capability
                    break
            
            if matching_capability:
                # 计算能力评分
                score = (
                    matching_capability.confidence_level * 0.4 +
                    matching_capability.success_rate * 0.4 +
                    (1.0 / max(matching_capability.processing_time_ms, 1)) * 0.2
                )
                
                if score > best_score:
                    best_score = score
                    selected_service = service
        
        return selected_service
    
    async def _intelligent_select(
        self,
        services: List[AgentServiceInfo],
        context: RequestContext
    ) -> AgentServiceInfo:
        """智能选择（综合多种因素）"""
        scores = []
        
        for service in services:
            score = 0.0
            
            # 能力匹配度 (40%)
            capability_score = await self._calculate_capability_score(service, context)
            score += capability_score * 0.4
            
            # 负载情况 (30%)
            load_score = await self._calculate_load_score(service)
            score += load_score * 0.3
            
            # 历史性能 (30%)
            performance_score = await self._calculate_performance_score(service)
            score += performance_score * 0.3
            
            scores.append((service, score))
        
        # 选择得分最高的服务
        best_service = max(scores, key=lambda x: x[1])
        return best_service[0]
    
    async def _calculate_capability_score(
        self,
        service: AgentServiceInfo,
        context: RequestContext
    ) -> float:
        """计算能力评分"""
        for capability in service.capabilities:
            if capability.capability_type == context.target_capability:
                return (
                    capability.confidence_level * 0.5 +
                    capability.success_rate * 0.3 +
                    (1.0 / max(capability.processing_time_ms, 1)) * 0.2
                )
        return 0.0
    
    async def _calculate_load_score(self, service: AgentServiceInfo) -> float:
        """计算负载评分"""
        metrics = self.service_metrics.get(service.service_id)
        if not metrics:
            return 1.0
        
        # 基于活跃连接数和负载因子计算
        load_factor = service.load_factor
        connection_factor = min(metrics.active_connections / 100.0, 1.0)
        
        return 1.0 - (load_factor * 0.6 + connection_factor * 0.4)
    
    async def _calculate_performance_score(self, service: AgentServiceInfo) -> float:
        """计算性能评分"""
        metrics = self.service_metrics.get(service.service_id)
        if not metrics:
            return 0.5
        
        # 基于成功率和响应时间计算
        success_rate_score = metrics.success_rate
        response_time_score = 1.0 / max(metrics.average_response_time / 1000.0, 1.0)
        
        return (success_rate_score * 0.7 + response_time_score * 0.3)
    
    def _match_pattern(self, text: str, pattern: str) -> bool:
        """模式匹配"""
        # 简单的通配符匹配
        if pattern == "*":
            return True
        
        if "*" in pattern:
            parts = pattern.split("*")
            if len(parts) == 2:
                prefix, suffix = parts
                return text.startswith(prefix) and text.endswith(suffix)
        
        return text == pattern
    
    def _check_rule_conditions(self, rule: RoutingRule, context: RequestContext) -> bool:
        """检查规则条件"""
        for key, expected_value in rule.conditions.items():
            if key == "user_id":
                if context.user_id != expected_value:
                    return False
            elif key == "time_range":
                # 检查时间范围
                current_hour = datetime.now().hour
                start_hour, end_hour = expected_value
                if not (start_hour <= current_hour <= end_hour):
                    return False
            # 可以添加更多条件检查
        
        return True
    
    async def _record_routing_decision(
        self,
        context: RequestContext,
        selected_service: AgentServiceInfo
    ):
        """记录路由决策"""
        try:
            decision_data = {
                "request_id": context.request_id,
                "source_service": context.source_service,
                "target_capability": context.target_capability.value,
                "selected_service": selected_service.service_id,
                "agent_type": selected_service.agent_type.value,
                "timestamp": datetime.now().isoformat(),
                "strategy": self.load_balancing_strategy.value
            }
            
            await self.redis.setex(
                f"routing_decision:{context.request_id}",
                3600,  # 1小时TTL
                json.dumps(decision_data)
            )
            
        except Exception as e:
            logger.error(f"记录路由决策失败: {e}")
    
    async def _load_routing_rules(self):
        """加载路由规则"""
        try:
            rules_data = await self.redis.get("mesh_routing_rules")
            if rules_data:
                rules_list = json.loads(rules_data)
                
                for rule_data in rules_list:
                    rule = RoutingRule(
                        rule_id=rule_data["rule_id"],
                        agent_type=AgentType(rule_data["agent_type"]) if rule_data.get("agent_type") else None,
                        capability_type=CapabilityType(rule_data["capability_type"]) if rule_data.get("capability_type") else None,
                        source_pattern=rule_data.get("source_pattern"),
                        target_services=rule_data.get("target_services", []),
                        weight_distribution=rule_data.get("weight_distribution", {}),
                        conditions=rule_data.get("conditions", {}),
                        priority=rule_data.get("priority", 0),
                        enabled=rule_data.get("enabled", True)
                    )
                    self.routing_rules.append(rule)
                
                # 按优先级排序
                self.routing_rules.sort(key=lambda r: r.priority, reverse=True)
                
                logger.info(f"加载了 {len(self.routing_rules)} 个路由规则")
            
        except Exception as e:
            logger.error(f"加载路由规则失败: {e}")
    
    async def _store_routing_rules(self):
        """存储路由规则"""
        try:
            rules_list = []
            for rule in self.routing_rules:
                rule_data = {
                    "rule_id": rule.rule_id,
                    "agent_type": rule.agent_type.value if rule.agent_type else None,
                    "capability_type": rule.capability_type.value if rule.capability_type else None,
                    "source_pattern": rule.source_pattern,
                    "target_services": rule.target_services,
                    "weight_distribution": rule.weight_distribution,
                    "conditions": rule.conditions,
                    "priority": rule.priority,
                    "enabled": rule.enabled
                }
                rules_list.append(rule_data)
            
            await self.redis.setex(
                "mesh_routing_rules",
                24 * 3600,  # 24小时TTL
                json.dumps(rules_list)
            )
            
        except Exception as e:
            logger.error(f"存储路由规则失败: {e}")
    
    async def _store_metrics(self, service_id: str, metrics: ServiceMetrics):
        """存储服务指标"""
        try:
            metrics_data = {
                "service_id": metrics.service_id,
                "request_count": metrics.request_count,
                "success_count": metrics.success_count,
                "error_count": metrics.error_count,
                "total_response_time": metrics.total_response_time,
                "active_connections": metrics.active_connections,
                "last_request_time": metrics.last_request_time.isoformat() if metrics.last_request_time else None,
                "last_error_time": metrics.last_error_time.isoformat() if metrics.last_error_time else None
            }
            
            await self.redis.setex(
                f"service_metrics:{service_id}",
                3600,  # 1小时TTL
                json.dumps(metrics_data)
            )
            
        except Exception as e:
            logger.error(f"存储服务指标失败: {e}")
    
    async def _health_checker(self):
        """健康检查后台任务"""
        while self._running:
            try:
                if self.service_registry:
                    services = await self.service_registry.discover_services()
                    
                    for service in services:
                        health_status = await self._check_service_health(service)
                        self.health_status[service.service_id] = health_status
                
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"健康检查异常: {e}")
                await asyncio.sleep(5)
    
    async def _check_service_health(self, service: AgentServiceInfo) -> HealthStatus:
        """检查服务健康状态"""
        try:
            # 检查服务心跳
            if service.last_heartbeat:
                time_since_heartbeat = (datetime.now() - service.last_heartbeat).total_seconds()
                if time_since_heartbeat > 90:  # 90秒无心跳认为不健康
                    return HealthStatus.UNHEALTHY
            
            # 检查服务指标
            metrics = self.service_metrics.get(service.service_id)
            if metrics:
                # 基于错误率判断健康状态
                if metrics.error_rate > 0.5:  # 错误率超过50%
                    return HealthStatus.UNHEALTHY
                elif metrics.error_rate > 0.2:  # 错误率超过20%
                    return HealthStatus.DEGRADED
            
            # 尝试健康检查请求
            health_check_result = await self._perform_health_check(service)
            if health_check_result:
                return HealthStatus.HEALTHY
            else:
                return HealthStatus.DEGRADED
            
        except Exception as e:
            logger.error(f"检查服务健康状态失败: {e}")
            return HealthStatus.UNKNOWN
    
    async def _perform_health_check(self, service: AgentServiceInfo) -> bool:
        """执行健康检查"""
        try:
            async with aiohttp.ClientSession() as session:
                health_url = f"http://{service.host}:{service.port}/health"
                
                async with session.get(
                    health_url,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    return response.status == 200
                    
        except Exception:
            return False
    
    async def _metrics_collector(self):
        """指标收集器后台任务"""
        while self._running:
            try:
                # 定期清理过期指标
                current_time = datetime.now()
                
                for service_id, metrics in list(self.service_metrics.items()):
                    if (metrics.last_request_time and 
                        (current_time - metrics.last_request_time).total_seconds() > 3600):
                        # 1小时无请求的服务，清理指标
                        del self.service_metrics[service_id]
                
                await asyncio.sleep(300)  # 每5分钟清理一次
                
            except Exception as e:
                logger.error(f"指标收集器异常: {e}")
                await asyncio.sleep(30)
    
    async def _circuit_breaker_monitor(self):
        """熔断器监控后台任务"""
        while self._running:
            try:
                # 监控熔断器状态变化
                for service_id, cb in self.circuit_breakers.items():
                    if cb.state == CircuitBreakerState.OPEN:
                        # 检查是否可以转为半开状态
                        cb.should_allow_request()
                
                await asyncio.sleep(10)  # 每10秒检查一次
                
            except Exception as e:
                logger.error(f"熔断器监控异常: {e}")
                await asyncio.sleep(5)
    
    async def close(self):
        """关闭服务网格控制器"""
        self._running = False
        if self.redis:
            await self.redis.close()


# 全局服务网格控制器实例
_agent_mesh_controller: Optional[AgentMeshController] = None


async def get_agent_mesh_controller() -> AgentMeshController:
    """获取全局智能体服务网格控制器"""
    global _agent_mesh_controller
    if _agent_mesh_controller is None:
        _agent_mesh_controller = AgentMeshController()
        await _agent_mesh_controller.initialize()
    return _agent_mesh_controller


async def route_agent_request(
    source_service: str,
    target_capability: CapabilityType,
    agent_type: Optional[AgentType] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Optional[AgentServiceInfo]:
    """路由智能体请求的便捷函数"""
    controller = await get_agent_mesh_controller()
    
    context = RequestContext(
        request_id=str(uuid4()),
        source_service=source_service,
        target_capability=target_capability,
        agent_type=agent_type,
        user_id=user_id,
        session_id=session_id,
        metadata=metadata or {}
    )
    
    return await controller.route_request(context)