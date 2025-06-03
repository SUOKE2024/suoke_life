#!/usr/bin/env python3
"""
微服务治理体系统一配置和监控
整合服务注册发现、协同决策总线、区块链消息总线和服务网格
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Callable
from uuid import uuid4

import aioredis

from ..service_registry.agent_discovery import (
    AgentType, AgentServiceRegistry, get_agent_registry
)
from ...agent_services.collaborative_decision_bus import (
    CollaborativeDecisionBus, get_decision_bus
)
from ...message_bus.blockchain_integration import (
    BlockchainMessageBus, get_blockchain_message_bus
)
from ..service_mesh.agent_mesh_controller import (
    AgentMeshController, get_agent_mesh_controller
)

logger = logging.getLogger(__name__)

class GovernanceLevel(Enum):
    """治理级别"""
    BASIC = "basic"           # 基础治理
    STANDARD = "standard"     # 标准治理
    ADVANCED = "advanced"     # 高级治理
    ENTERPRISE = "enterprise" # 企业级治理

class ServiceTier(Enum):
    """服务等级"""
    CRITICAL = "critical"     # 关键服务
    IMPORTANT = "important"   # 重要服务
    STANDARD = "standard"     # 标准服务
    DEVELOPMENT = "development" # 开发服务

class AlertLevel(Enum):
    """告警级别"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"

@dataclass
class GovernanceConfig:
    """治理配置"""
    governance_level: GovernanceLevel
    enable_service_discovery: bool = True
    enable_collaborative_decision: bool = True
    enable_blockchain_integration: bool = True
    enable_service_mesh: bool = True
    enable_monitoring: bool = True
    enable_alerting: bool = True
    enable_auto_scaling: bool = False
    enable_circuit_breaker: bool = True
    enable_rate_limiting: bool = True
    enable_security_policies: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ServiceGovernancePolicy:
    """服务治理策略"""
    service_name: str
    agent_type: AgentType
    service_tier: ServiceTier
    max_instances: int = 10
    min_instances: int = 1
    cpu_threshold: float = 80.0
    memory_threshold: float = 80.0
    error_rate_threshold: float = 5.0
    response_time_threshold: float = 5000.0  # 毫秒
    circuit_breaker_enabled: bool = True
    rate_limit_rps: int = 1000
    health_check_interval: int = 30
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GovernanceMetrics:
    """治理指标"""
    timestamp: datetime
    total_services: int
    healthy_services: int
    unhealthy_services: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    active_decisions: int
    completed_decisions: int
    blockchain_transactions: int
    circuit_breaker_open: int
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GovernanceAlert:
    """治理告警"""
    alert_id: str
    level: AlertLevel
    service_name: str
    agent_type: AgentType
    message: str
    details: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolved_at: Optional[datetime] = None

class MicroserviceGovernance:
    """微服务治理体系"""
    
    def __init__(
        self,
        config: GovernanceConfig,
        redis_url: str = "redis://localhost:6379"
    ):
        self.config = config
        self.redis_url = redis_url
        self.redis: Optional[aioredis.Redis] = None
        
        # 核心组件
        self.service_registry: Optional[AgentServiceRegistry] = None
        self.decision_bus: Optional[CollaborativeDecisionBus] = None
        self.message_bus: Optional[BlockchainMessageBus] = None
        self.mesh_controller: Optional[AgentMeshController] = None
        
        # 治理策略
        self.governance_policies: Dict[str, ServiceGovernancePolicy] = {}
        
        # 监控数据
        self.metrics_history: List[GovernanceMetrics] = []
        self.active_alerts: Dict[str, GovernanceAlert] = {}
        
        # 事件处理器
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        self._running = False
    
    async def initialize(self):
        """初始化微服务治理体系"""
        try:
            self.redis = aioredis.from_url(self.redis_url)
            await self.redis.ping()
            
            # 初始化核心组件
            if self.config.enable_service_discovery:
                self.service_registry = await get_agent_registry()
                logger.info("服务注册发现组件已启用")
            
            if self.config.enable_collaborative_decision:
                self.decision_bus = await get_decision_bus()
                logger.info("协同决策总线已启用")
            
            if self.config.enable_blockchain_integration:
                self.message_bus = await get_blockchain_message_bus()
                logger.info("区块链消息总线已启用")
            
            if self.config.enable_service_mesh:
                self.mesh_controller = await get_agent_mesh_controller()
                logger.info("服务网格控制器已启用")
            
            # 加载治理策略
            await self._load_governance_policies()
            
            logger.info(f"微服务治理体系初始化成功 (级别: {self.config.governance_level.value})")
            
            # 启动后台任务
            self._running = True
            if self.config.enable_monitoring:
                asyncio.create_task(self._metrics_collector())
                asyncio.create_task(self._health_monitor())
            
            if self.config.enable_alerting:
                asyncio.create_task(self._alert_manager())
            
            if self.config.enable_auto_scaling:
                asyncio.create_task(self._auto_scaler())
            
            asyncio.create_task(self._event_processor())
            
        except Exception as e:
            logger.error(f"微服务治理体系初始化失败: {e}")
            raise
    
    async def register_service_policy(self, policy: ServiceGovernancePolicy):
        """注册服务治理策略"""
        try:
            self.governance_policies[policy.service_name] = policy
            
            # 存储到Redis
            await self._store_governance_policy(policy)
            
            # 应用策略
            await self._apply_governance_policy(policy)
            
            logger.info(f"服务治理策略已注册: {policy.service_name}")
            
        except Exception as e:
            logger.error(f"注册服务治理策略失败: {e}")
            raise
    
    async def get_governance_metrics(self) -> GovernanceMetrics:
        """获取治理指标"""
        try:
            # 收集各组件指标
            total_services = 0
            healthy_services = 0
            unhealthy_services = 0
            
            if self.service_registry:
                services = await self.service_registry.discover_services()
                total_services = len(services)
                
                for service in services:
                    if service.status.value == "healthy":
                        healthy_services += 1
                    else:
                        unhealthy_services += 1
            
            # 收集请求指标
            total_requests = 0
            successful_requests = 0
            failed_requests = 0
            average_response_time = 0.0
            
            if self.mesh_controller:
                all_metrics = await self.mesh_controller.get_all_metrics()
                for metrics in all_metrics.values():
                    total_requests += metrics.request_count
                    successful_requests += metrics.success_count
                    failed_requests += metrics.error_count
                    
                if successful_requests > 0:
                    total_response_time = sum(
                        m.total_response_time for m in all_metrics.values()
                    )
                    average_response_time = total_response_time / successful_requests
            
            # 收集决策指标
            active_decisions = 0
            completed_decisions = 0
            
            if self.decision_bus:
                active_decisions = len(self.decision_bus.active_decisions)
                completed_decisions = len(self.decision_bus.decision_results)
            
            # 收集区块链指标
            blockchain_transactions = 0
            # TODO: 从区块链消息总线获取交易数量
            
            # 收集熔断器指标
            circuit_breaker_open = 0
            if self.mesh_controller:
                for cb in self.mesh_controller.circuit_breakers.values():
                    if cb.state.value == "open":
                        circuit_breaker_open += 1
            
            metrics = GovernanceMetrics(
                timestamp=datetime.now(),
                total_services=total_services,
                healthy_services=healthy_services,
                unhealthy_services=unhealthy_services,
                total_requests=total_requests,
                successful_requests=successful_requests,
                failed_requests=failed_requests,
                average_response_time=average_response_time,
                active_decisions=active_decisions,
                completed_decisions=completed_decisions,
                blockchain_transactions=blockchain_transactions,
                circuit_breaker_open=circuit_breaker_open
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"获取治理指标失败: {e}")
            return GovernanceMetrics(
                timestamp=datetime.now(),
                total_services=0,
                healthy_services=0,
                unhealthy_services=0,
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                average_response_time=0.0,
                active_decisions=0,
                completed_decisions=0,
                blockchain_transactions=0,
                circuit_breaker_open=0
            )
    
    async def create_alert(
        self,
        level: AlertLevel,
        service_name: str,
        agent_type: AgentType,
        message: str,
        details: Dict[str, Any]
    ) -> str:
        """创建告警"""
        try:
            alert_id = str(uuid4())
            alert = GovernanceAlert(
                alert_id=alert_id,
                level=level,
                service_name=service_name,
                agent_type=agent_type,
                message=message,
                details=details
            )
            
            self.active_alerts[alert_id] = alert
            
            # 存储到Redis
            await self._store_alert(alert)
            
            # 发布告警事件
            await self._publish_alert_event(alert)
            
            logger.warning(f"创建告警: {level.value} - {message}")
            
            return alert_id
            
        except Exception as e:
            logger.error(f"创建告警失败: {e}")
            raise
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """解决告警"""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.resolved = True
                alert.resolved_at = datetime.now()
                
                # 更新Redis
                await self._store_alert(alert)
                
                # 发布告警解决事件
                await self._publish_alert_event(alert, "alert_resolved")
                
                logger.info(f"告警已解决: {alert_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"解决告警失败: {e}")
            return False
    
    async def get_active_alerts(self) -> List[GovernanceAlert]:
        """获取活跃告警"""
        return [alert for alert in self.active_alerts.values() if not alert.resolved]
    
    async def get_service_health_status(self) -> Dict[str, Dict[str, Any]]:
        """获取服务健康状态"""
        try:
            health_status = {}
            
            if self.service_registry:
                services = await self.service_registry.discover_services()
                
                for service in services:
                    status_info = {
                        "service_id": service.service_id,
                        "agent_type": service.agent_type.value,
                        "status": service.status.value,
                        "last_heartbeat": service.last_heartbeat.isoformat(),
                        "capabilities": len(service.capabilities)
                    }
                    
                    # 添加指标信息
                    if self.mesh_controller:
                        metrics = await self.mesh_controller.get_service_metrics(service.service_id)
                        if metrics:
                            status_info.update({
                                "request_count": metrics.request_count,
                                "success_rate": metrics.success_rate,
                                "average_response_time": metrics.average_response_time,
                                "active_connections": metrics.active_connections
                            })
                    
                    health_status[service.service_name] = status_info
            
            return health_status
            
        except Exception as e:
            logger.error(f"获取服务健康状态失败: {e}")
            return {}
    
    async def _load_governance_policies(self):
        """加载治理策略"""
        try:
            # 从Redis加载策略
            policies_data = await self.redis.get("governance_policies")
            if policies_data:
                policies_list = json.loads(policies_data)
                
                for policy_data in policies_list:
                    policy = ServiceGovernancePolicy(
                        service_name=policy_data["service_name"],
                        agent_type=AgentType(policy_data["agent_type"]),
                        service_tier=ServiceTier(policy_data["service_tier"]),
                        max_instances=policy_data.get("max_instances", 10),
                        min_instances=policy_data.get("min_instances", 1),
                        cpu_threshold=policy_data.get("cpu_threshold", 80.0),
                        memory_threshold=policy_data.get("memory_threshold", 80.0),
                        error_rate_threshold=policy_data.get("error_rate_threshold", 5.0),
                        response_time_threshold=policy_data.get("response_time_threshold", 5000.0),
                        circuit_breaker_enabled=policy_data.get("circuit_breaker_enabled", True),
                        rate_limit_rps=policy_data.get("rate_limit_rps", 1000),
                        health_check_interval=policy_data.get("health_check_interval", 30),
                        metadata=policy_data.get("metadata", {})
                    )
                    
                    self.governance_policies[policy.service_name] = policy
                
                logger.info(f"加载了 {len(self.governance_policies)} 个治理策略")
            
        except Exception as e:
            logger.error(f"加载治理策略失败: {e}")
    
    async def _store_governance_policy(self, policy: ServiceGovernancePolicy):
        """存储治理策略"""
        try:
            # 更新策略列表
            policies_list = []
            for p in self.governance_policies.values():
                policy_data = {
                    "service_name": p.service_name,
                    "agent_type": p.agent_type.value,
                    "service_tier": p.service_tier.value,
                    "max_instances": p.max_instances,
                    "min_instances": p.min_instances,
                    "cpu_threshold": p.cpu_threshold,
                    "memory_threshold": p.memory_threshold,
                    "error_rate_threshold": p.error_rate_threshold,
                    "response_time_threshold": p.response_time_threshold,
                    "circuit_breaker_enabled": p.circuit_breaker_enabled,
                    "rate_limit_rps": p.rate_limit_rps,
                    "health_check_interval": p.health_check_interval,
                    "metadata": p.metadata
                }
                policies_list.append(policy_data)
            
            await self.redis.setex(
                "governance_policies",
                24 * 3600,  # 24小时TTL
                json.dumps(policies_list)
            )
            
        except Exception as e:
            logger.error(f"存储治理策略失败: {e}")
    
    async def _apply_governance_policy(self, policy: ServiceGovernancePolicy):
        """应用治理策略"""
        try:
            # 这里可以根据策略配置相应的治理规则
            # 例如：配置熔断器、限流器、健康检查等
            
            logger.info(f"应用治理策略: {policy.service_name}")
            
        except Exception as e:
            logger.error(f"应用治理策略失败: {e}")
    
    async def _store_alert(self, alert: GovernanceAlert):
        """存储告警"""
        try:
            alert_data = {
                "alert_id": alert.alert_id,
                "level": alert.level.value,
                "service_name": alert.service_name,
                "agent_type": alert.agent_type.value,
                "message": alert.message,
                "details": alert.details,
                "timestamp": alert.timestamp.isoformat(),
                "resolved": alert.resolved,
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None
            }
            
            key = f"governance_alert:{alert.alert_id}"
            await self.redis.setex(key, 7 * 24 * 3600, json.dumps(alert_data))  # 7天TTL
            
        except Exception as e:
            logger.error(f"存储告警失败: {e}")
    
    async def _publish_alert_event(self, alert: GovernanceAlert, event_type: str = "alert_created"):
        """发布告警事件"""
        try:
            event_data = {
                "event_type": event_type,
                "alert_id": alert.alert_id,
                "level": alert.level.value,
                "service_name": alert.service_name,
                "agent_type": alert.agent_type.value,
                "message": alert.message,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.redis.publish("governance_alert_events", json.dumps(event_data))
            
        except Exception as e:
            logger.error(f"发布告警事件失败: {e}")
    
    async def _metrics_collector(self):
        """指标收集器后台任务"""
        while self._running:
            try:
                # 收集治理指标
                metrics = await self.get_governance_metrics()
                self.metrics_history.append(metrics)
                
                # 保持历史记录在合理范围内
                if len(self.metrics_history) > 1000:
                    self.metrics_history = self.metrics_history[-1000:]
                
                # 存储指标到Redis
                await self._store_metrics(metrics)
                
                await asyncio.sleep(60)  # 每分钟收集一次
                
            except Exception as e:
                logger.error(f"指标收集器异常: {e}")
                await asyncio.sleep(10)
    
    async def _health_monitor(self):
        """健康监控后台任务"""
        while self._running:
            try:
                # 检查服务健康状态
                if self.service_registry:
                    services = await self.service_registry.discover_services()
                    
                    for service in services:
                        # 检查服务是否符合治理策略
                        policy = self.governance_policies.get(service.service_name)
                        if policy:
                            await self._check_service_against_policy(service, policy)
                
                await asyncio.sleep(30)  # 每30秒检查一次
                
            except Exception as e:
                logger.error(f"健康监控异常: {e}")
                await asyncio.sleep(10)
    
    async def _alert_manager(self):
        """告警管理器后台任务"""
        while self._running:
            try:
                # 检查告警是否需要自动解决
                current_time = datetime.now()
                
                for alert in list(self.active_alerts.values()):
                    if not alert.resolved:
                        # 检查告警是否超时（例如：1小时后自动解决某些告警）
                        if (current_time - alert.timestamp > timedelta(hours=1) and 
                            alert.level == AlertLevel.INFO):
                            await self.resolve_alert(alert.alert_id)
                
                await asyncio.sleep(300)  # 每5分钟检查一次
                
            except Exception as e:
                logger.error(f"告警管理器异常: {e}")
                await asyncio.sleep(10)
    
    async def _auto_scaler(self):
        """自动扩缩容后台任务"""
        while self._running:
            try:
                # 根据负载情况自动扩缩容
                # 这里是简化实现，实际需要与容器编排系统集成
                
                await asyncio.sleep(120)  # 每2分钟检查一次
                
            except Exception as e:
                logger.error(f"自动扩缩容异常: {e}")
                await asyncio.sleep(30)
    
    async def _event_processor(self):
        """事件处理器后台任务"""
        while self._running:
            try:
                # 处理各种治理事件
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"事件处理器异常: {e}")
                await asyncio.sleep(5)
    
    async def _check_service_against_policy(
        self,
        service: Any,
        policy: ServiceGovernancePolicy
    ):
        """检查服务是否符合治理策略"""
        try:
            # 检查错误率
            if self.mesh_controller:
                metrics = await self.mesh_controller.get_service_metrics(service.service_id)
                if metrics:
                    if metrics.error_rate * 100 > policy.error_rate_threshold:
                        await self.create_alert(
                            AlertLevel.WARNING,
                            service.service_name,
                            service.agent_type,
                            f"错误率过高: {metrics.error_rate * 100:.2f}%",
                            {"error_rate": metrics.error_rate, "threshold": policy.error_rate_threshold}
                        )
                    
                    if metrics.average_response_time > policy.response_time_threshold:
                        await self.create_alert(
                            AlertLevel.WARNING,
                            service.service_name,
                            service.agent_type,
                            f"响应时间过长: {metrics.average_response_time:.2f}ms",
                            {"response_time": metrics.average_response_time, "threshold": policy.response_time_threshold}
                        )
            
        except Exception as e:
            logger.error(f"检查服务策略失败: {e}")
    
    async def _store_metrics(self, metrics: GovernanceMetrics):
        """存储指标"""
        try:
            metrics_data = {
                "timestamp": metrics.timestamp.isoformat(),
                "total_services": metrics.total_services,
                "healthy_services": metrics.healthy_services,
                "unhealthy_services": metrics.unhealthy_services,
                "total_requests": metrics.total_requests,
                "successful_requests": metrics.successful_requests,
                "failed_requests": metrics.failed_requests,
                "average_response_time": metrics.average_response_time,
                "active_decisions": metrics.active_decisions,
                "completed_decisions": metrics.completed_decisions,
                "blockchain_transactions": metrics.blockchain_transactions,
                "circuit_breaker_open": metrics.circuit_breaker_open,
                "metadata": metrics.metadata
            }
            
            # 使用时间戳作为键
            key = f"governance_metrics:{int(metrics.timestamp.timestamp())}"
            await self.redis.setex(key, 24 * 3600, json.dumps(metrics_data))  # 24小时TTL
            
        except Exception as e:
            logger.error(f"存储指标失败: {e}")
    
    async def close(self):
        """关闭微服务治理体系"""
        self._running = False
        
        if self.service_registry:
            await self.service_registry.close()
        
        if self.decision_bus:
            await self.decision_bus.close()
        
        if self.message_bus:
            await self.message_bus.close()
        
        if self.mesh_controller:
            await self.mesh_controller.close()
        
        if self.redis:
            await self.redis.close()

# 全局治理体系实例
_governance: Optional[MicroserviceGovernance] = None

async def get_microservice_governance(
    governance_level: GovernanceLevel = GovernanceLevel.STANDARD
) -> MicroserviceGovernance:
    """获取全局微服务治理体系"""
    global _governance
    if _governance is None:
        config = GovernanceConfig(governance_level=governance_level)
        _governance = MicroserviceGovernance(config)
        await _governance.initialize()
    return _governance

async def initialize_suoke_governance() -> MicroserviceGovernance:
    """初始化索克生活微服务治理体系"""
    governance = await get_microservice_governance(GovernanceLevel.ENTERPRISE)
    
    # 注册四智能体的治理策略
    agent_policies = [
        ServiceGovernancePolicy(
            service_name="xiaoai-service",
            agent_type=AgentType.XIAOAI,
            service_tier=ServiceTier.CRITICAL,
            max_instances=5,
            min_instances=2,
            cpu_threshold=70.0,
            memory_threshold=75.0,
            error_rate_threshold=3.0,
            response_time_threshold=3000.0
        ),
        ServiceGovernancePolicy(
            service_name="xiaoke-service",
            agent_type=AgentType.XIAOKE,
            service_tier=ServiceTier.CRITICAL,
            max_instances=5,
            min_instances=2,
            cpu_threshold=70.0,
            memory_threshold=75.0,
            error_rate_threshold=3.0,
            response_time_threshold=3000.0
        ),
        ServiceGovernancePolicy(
            service_name="laoke-service",
            agent_type=AgentType.LAOKE,
            service_tier=ServiceTier.CRITICAL,
            max_instances=3,
            min_instances=1,
            cpu_threshold=75.0,
            memory_threshold=80.0,
            error_rate_threshold=2.0,
            response_time_threshold=5000.0
        ),
        ServiceGovernancePolicy(
            service_name="soer-service",
            agent_type=AgentType.SOER,
            service_tier=ServiceTier.IMPORTANT,
            max_instances=3,
            min_instances=1,
            cpu_threshold=80.0,
            memory_threshold=80.0,
            error_rate_threshold=5.0,
            response_time_threshold=4000.0
        )
    ]
    
    for policy in agent_policies:
        await governance.register_service_policy(policy)
    
    logger.info("索克生活微服务治理体系初始化完成")
    return governance 