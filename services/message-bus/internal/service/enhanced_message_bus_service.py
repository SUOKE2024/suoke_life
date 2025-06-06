"""
enhanced_message_bus_service - 索克生活项目模块
"""

            import psutil
from ...pkg.utils.distributed_storage import (
from ...pkg.utils.enhanced_metrics import (
from ...pkg.utils.message_processor import (
from ...pkg.utils.security_manager import (
from ...pkg.utils.smart_router import (
from collections import defaultdict
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Callable, Union
import asyncio
import json
import logging
import time
import uuid

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
增强的消息总线服务
集成所有优化组件，提供完整的消息总线功能
"""


    MessageProcessorFactory, ProcessorConfig, MessageEnvelope, MessagePriority, CompressionType
)
    RouterFactory, RoutingConfig, RoutingStrategy, RouteEndpoint
)
    StorageManagerFactory, StorageConfig
)
    MetricsFactory, MetricConfig
)
    SecurityManagerFactory, SecurityConfig, User
)

logger = logging.getLogger(__name__)


class MessageBusState(Enum):
    """消息总线状态"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


class ServiceMode(Enum):
    """服务模式"""
    STANDALONE = "standalone"
    CLUSTER = "cluster"
    EDGE = "edge"


@dataclass
class MessageBusConfig:
    """消息总线配置"""
    # 基础配置
    service_name: str = "enhanced-message-bus"
    service_version: str = "1.0.0"
    service_mode: ServiceMode = ServiceMode.STANDALONE
    
    # 网络配置
    host: str = "0.0.0.0"
    port: int = 8080
    grpc_port: int = 50051
    max_connections: int = 1000
    
    # 性能配置
    max_message_size: int = 10 * 1024 * 1024  # 10MB
    batch_size: int = 100
    flush_interval: float = 1.0
    worker_threads: int = 4
    
    # 可靠性配置
    enable_persistence: bool = True
    enable_replication: bool = True
    enable_compression: bool = True
    enable_encryption: bool = True
    
    # 监控配置
    enable_metrics: bool = True
    enable_tracing: bool = True
    enable_health_check: bool = True
    
    # 组件配置
    processor_config: Optional[ProcessorConfig] = None
    router_config: Optional[RoutingConfig] = None
    storage_config: Optional[StorageConfig] = None
    metrics_config: Optional[MetricConfig] = None
    security_config: Optional[SecurityConfig] = None
    
    # 集群配置
    cluster_nodes: List[str] = field(default_factory=list)
    node_id: Optional[str] = None
    discovery_service: Optional[str] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if self.node_id is None:
            self.node_id = str(uuid.uuid4())
        
        # 初始化组件配置
        if self.processor_config is None:
            self.processor_config = ProcessorConfig()
        
        if self.router_config is None:
            self.router_config = RoutingConfig()
        
        if self.storage_config is None:
            self.storage_config = StorageConfig()
        
        if self.metrics_config is None:
            self.metrics_config = MetricConfig()
        
        if self.security_config is None:
            self.security_config = SecurityConfig()


@dataclass
class MessageContext:
    """消息上下文"""
    message_id: str
    topic: str
    user: Optional[User] = None
    source_node: Optional[str] = None
    target_nodes: List[str] = field(default_factory=list)
    routing_strategy: Optional[RoutingStrategy] = None
    priority: MessagePriority = MessagePriority.NORMAL
    compression: CompressionType = CompressionType.NONE
    encryption_enabled: bool = False
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'message_id': self.message_id,
            'topic': self.topic,
            'user_id': self.user.id if self.user else None,
            'source_node': self.source_node,
            'target_nodes': self.target_nodes,
            'routing_strategy': self.routing_strategy.value if self.routing_strategy else None,
            'priority': self.priority.value,
            'compression': self.compression.value,
            'encryption_enabled': self.encryption_enabled,
            'timestamp': self.timestamp,
            'metadata': self.metadata
        }


class MessageHandler:
    """消息处理器接口"""
    
    async def handle_message(self, envelope: MessageEnvelope, context: MessageContext) -> bool:
        """处理消息"""
        raise NotImplementedError
    
    async def handle_error(self, envelope: MessageEnvelope, context: MessageContext, error: Exception):
        """处理错误"""
        logger.error(f"消息处理错误: {error}")


class TopicManager:
    """主题管理器"""
    
    def __init__(self):
        self.topics: Dict[str, Dict[str, Any]] = {}
        self.subscribers: Dict[str, Set[str]] = defaultdict(set)
        self.handlers: Dict[str, List[MessageHandler]] = defaultdict(list)
        self.message_counts: Dict[str, int] = defaultdict(int)
        self._lock = asyncio.Lock()
    
    def create_topic(self, topic: str, config: Dict[str, Any] = None) -> bool:
        """创建主题"""
        config = config or {}
        
        if topic in self.topics:
            return False
        
        self.topics[topic] = {
            'name': topic,
            'config': config,
            'created_at': time.time(),
            'message_count': 0,
            'subscriber_count': 0
        }
        
        logger.info(f"创建主题: {topic}")
        return True
    
    def delete_topic(self, topic: str) -> bool:
        """删除主题"""
        if topic not in self.topics:
            return False
        
        # 清理相关数据
        self.topics.pop(topic, None)
        self.subscribers.pop(topic, None)
        self.handlers.pop(topic, None)
        self.message_counts.pop(topic, None)
        
        logger.info(f"删除主题: {topic}")
        return True
    
    def subscribe(self, topic: str, subscriber_id: str, handler: Optional[MessageHandler] = None) -> bool:
        """订阅主题"""
        if topic not in self.topics:
            return False
        
        self.subscribers[topic].add(subscriber_id)
        
        if handler:
            self.handlers[topic].append(handler)
        
        # 更新订阅者数量
        self.topics[topic]['subscriber_count'] = len(self.subscribers[topic])
        
        logger.info(f"订阅主题: {topic}, 订阅者: {subscriber_id}")
        return True
    
    def unsubscribe(self, topic: str, subscriber_id: str) -> bool:
        """取消订阅"""
        if topic not in self.topics:
            return False
        
        self.subscribers[topic].discard(subscriber_id)
        
        # 更新订阅者数量
        self.topics[topic]['subscriber_count'] = len(self.subscribers[topic])
        
        logger.info(f"取消订阅主题: {topic}, 订阅者: {subscriber_id}")
        return True
    
    def get_topic_info(self, topic: str) -> Optional[Dict[str, Any]]:
        """获取主题信息"""
        return self.topics.get(topic)
    
    def list_topics(self) -> List[Dict[str, Any]]:
        """列出所有主题"""
        return list(self.topics.values())
    
    def get_subscribers(self, topic: str) -> Set[str]:
        """获取主题订阅者"""
        return self.subscribers.get(topic, set())
    
    def get_handlers(self, topic: str) -> List[MessageHandler]:
        """获取主题处理器"""
        return self.handlers.get(topic, [])
    
    def increment_message_count(self, topic: str):
        """增加消息计数"""
        if topic in self.topics:
            self.message_counts[topic] += 1
            self.topics[topic]['message_count'] = self.message_counts[topic]


class HealthChecker:
    """健康检查器"""
    
    def __init__(self, message_bus: 'EnhancedMessageBusService'):
        self.message_bus = message_bus
        self.last_check_time = 0
        self.health_status = {}
    
    async def check_health(self) -> Dict[str, Any]:
        """检查服务健康状态"""
        current_time = time.time()
        
        health_status = {
            'service': {
                'name': self.message_bus.config.service_name,
                'version': self.message_bus.config.service_version,
                'state': self.message_bus.state.value,
                'uptime': current_time - self.message_bus.start_time if hasattr(self.message_bus, 'start_time') else 0,
                'node_id': self.message_bus.config.node_id
            },
            'components': {},
            'metrics': {},
            'timestamp': current_time
        }
        
        # 检查各组件健康状态
        if self.message_bus.processor:
            health_status['components']['processor'] = await self._check_processor_health()
        
        if self.message_bus.router:
            health_status['components']['router'] = await self._check_router_health()
        
        if self.message_bus.storage_manager:
            health_status['components']['storage'] = await self._check_storage_health()
        
        if self.message_bus.metrics_collector:
            health_status['components']['metrics'] = await self._check_metrics_health()
        
        if self.message_bus.security_manager:
            health_status['components']['security'] = await self._check_security_health()
        
        # 收集健康指标
        health_status['metrics'] = await self._collect_health_metrics()
        
        self.health_status = health_status
        self.last_check_time = current_time
        
        return health_status
    
    async def _check_processor_health(self) -> Dict[str, Any]:
        """检查处理器健康状态"""
        try:
            stats = self.message_bus.processor.get_stats()
            queue_sizes = self.message_bus.processor.get_queue_sizes()
            
            return {
                'status': 'healthy',
                'processed_messages': stats.total_processed,
                'failed_messages': stats.total_failed,
                'avg_processing_time': stats.avg_processing_time,
                'queue_sizes': queue_sizes
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    async def _check_router_health(self) -> Dict[str, Any]:
        """检查路由器健康状态"""
        try:
            stats = self.message_bus.router.get_routing_stats()
            
            return {
                'status': 'healthy',
                'total_endpoints': stats.get('total_endpoints', 0),
                'active_endpoints': stats.get('active_endpoints', 0),
                'routing_stats': stats.get('routing_stats', {}),
                'circuit_breaker_stats': stats.get('circuit_breaker_stats', {})
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    async def _check_storage_health(self) -> Dict[str, Any]:
        """检查存储健康状态"""
        try:
            stats = self.message_bus.storage_manager.get_storage_stats()
            
            return {
                'status': 'healthy',
                'cluster_health': stats.get('cluster_health', {}),
                'storage_metrics': stats.get('storage_metrics', {}),
                'topic_count': stats.get('cluster_health', {}).get('total_topics', 0)
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    async def _check_metrics_health(self) -> Dict[str, Any]:
        """检查监控健康状态"""
        try:
            summary = self.message_bus.metrics_collector.get_metrics_summary()
            
            return {
                'status': 'healthy',
                'message_metrics': summary.get('message_metrics', {}),
                'system_metrics': summary.get('system_metrics', {}),
                'alerts': summary.get('alerts', {})
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    async def _check_security_health(self) -> Dict[str, Any]:
        """检查安全健康状态"""
        try:
            stats = self.message_bus.security_manager.get_security_stats()
            
            return {
                'status': 'healthy',
                'users': stats.get('users', {}),
                'api_keys': stats.get('api_keys', {}),
                'audit_events': stats.get('audit_events', {}),
                'encryption': stats.get('encryption', {})
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    async def _collect_health_metrics(self) -> Dict[str, Any]:
        """收集健康指标"""
        try:
            
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'network_connections': len(psutil.net_connections()),
                'process_count': len(psutil.pids())
            }
        except ImportError:
            return {
                'cpu_percent': 0,
                'memory_percent': 0,
                'disk_percent': 0,
                'network_connections': 0,
                'process_count': 0
            }


class EnhancedMessageBusService:
    """
    增强的消息总线服务
    集成所有优化组件，提供完整的消息总线功能
    """
    
    def __init__(self, config: MessageBusConfig):
        self.config = config
        self.state = MessageBusState.STOPPED
        self.start_time = 0
        
        # 核心组件
        self.processor = None
        self.router = None
        self.storage_manager = None
        self.metrics_collector = None
        self.security_manager = None
        
        # 管理组件
        self.topic_manager = TopicManager()
        self.health_checker = HealthChecker(self)
        
        # 后台任务
        self._background_tasks: List[asyncio.Task] = []
        
        # 初始化组件
        self._init_components()
    
    def _init_components(self):
        """初始化组件"""
        try:
            # 创建消息处理器
            self.processor = MessageProcessorFactory.create_high_performance_processor(
                self.config.processor_config
            )
            
            # 创建智能路由器
            self.router = RouterFactory.create_smart_router(
                self.config.router_config
            )
            
            # 创建分布式存储管理器
            self.storage_manager = StorageManagerFactory.create_distributed_storage_manager(
                self.config.storage_config
            )
            
            # 创建监控系统
            if self.config.enable_metrics:
                self.metrics_collector = MetricsFactory.create_enhanced_metrics_collector(
                    self.config.metrics_config
                )
            
            # 创建安全管理器
            self.security_manager = SecurityManagerFactory.create_security_manager(
                self.config.security_config
            )
            
            logger.info("消息总线组件初始化完成")
            
        except Exception as e:
            logger.error(f"组件初始化失败: {e}")
            self.state = MessageBusState.ERROR
            raise
    
    async def start(self):
        """启动消息总线服务"""
        if self.state != MessageBusState.STOPPED:
            logger.warning(f"服务已在运行状态: {self.state}")
            return
        
        try:
            self.state = MessageBusState.STARTING
            self.start_time = time.time()
            
            logger.info("启动增强消息总线服务...")
            
            # 启动核心组件
            await self._start_components()
            
            # 启动后台任务
            await self._start_background_tasks()
            
            self.state = MessageBusState.RUNNING
            logger.info("增强消息总线服务启动完成")
            
        except Exception as e:
            self.state = MessageBusState.ERROR
            logger.error(f"服务启动失败: {e}")
            raise
    
    async def stop(self):
        """停止消息总线服务"""
        if self.state not in [MessageBusState.RUNNING, MessageBusState.ERROR]:
            return
        
        try:
            self.state = MessageBusState.STOPPING
            logger.info("停止增强消息总线服务...")
            
            # 停止后台任务
            await self._stop_background_tasks()
            
            # 停止核心组件
            await self._stop_components()
            
            self.state = MessageBusState.STOPPED
            logger.info("增强消息总线服务已停止")
            
        except Exception as e:
            logger.error(f"服务停止失败: {e}")
            self.state = MessageBusState.ERROR
            raise
    
    async def _start_components(self):
        """启动组件"""
        components = [
            ("处理器", self.processor),
            ("路由器", self.router),
            ("存储管理器", self.storage_manager),
            ("监控系统", self.metrics_collector),
            ("安全管理器", self.security_manager)
        ]
        
        for name, component in components:
            if component:
                try:
                    await component.start()
                    logger.info(f"{name}启动成功")
                except Exception as e:
                    logger.error(f"{name}启动失败: {e}")
                    raise
    
    async def _stop_components(self):
        """停止组件"""
        components = [
            ("安全管理器", self.security_manager),
            ("监控系统", self.metrics_collector),
            ("存储管理器", self.storage_manager),
            ("路由器", self.router),
            ("处理器", self.processor)
        ]
        
        for name, component in components:
            if component:
                try:
                    await component.stop()
                    logger.info(f"{name}停止成功")
                except Exception as e:
                    logger.error(f"{name}停止失败: {e}")
    
    async def _start_background_tasks(self):
        """启动后台任务"""
        if self.config.enable_health_check:
            task = asyncio.create_task(self._health_check_loop())
            self._background_tasks.append(task)
        
        if self.config.enable_metrics:
            task = asyncio.create_task(self._stats_report_loop())
            self._background_tasks.append(task)
        
        # 清理任务
        task = asyncio.create_task(self._cleanup_loop())
        self._background_tasks.append(task)
    
    async def _stop_background_tasks(self):
        """停止后台任务"""
        for task in self._background_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self._background_tasks.clear()
    
    async def _health_check_loop(self):
        """健康检查循环"""
        while self.state == MessageBusState.RUNNING:
            try:
                await asyncio.sleep(30)  # 每30秒检查一次
                health_status = await self.health_checker.check_health()
                
                # 记录健康状态到监控系统
                if self.metrics_collector:
                    for component, status in health_status.get('components', {}).items():
                        is_healthy = status.get('status') == 'healthy'
                        self.metrics_collector.record_metric(f'component_health_{component}', 1 if is_healthy else 0)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"健康检查出错: {e}")
    
    async def _stats_report_loop(self):
        """统计报告循环"""
        while self.state == MessageBusState.RUNNING:
            try:
                await asyncio.sleep(60)  # 每分钟报告一次
                await self._report_stats()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"统计报告出错: {e}")
    
    async def _cleanup_loop(self):
        """清理循环"""
        while self.state == MessageBusState.RUNNING:
            try:
                await asyncio.sleep(300)  # 每5分钟清理一次
                await self._cleanup_resources()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"清理任务出错: {e}")
    
    async def _report_stats(self):
        """报告统计信息"""
        try:
            if self.metrics_collector:
                summary = self.metrics_collector.get_metrics_summary()
                logger.info(f"服务统计: {summary}")
        except Exception as e:
            logger.error(f"统计报告失败: {e}")
    
    async def _cleanup_resources(self):
        """清理资源"""
        try:
            # 这里可以添加资源清理逻辑
            pass
        except Exception as e:
            logger.error(f"资源清理失败: {e}")
    
    async def publish_message(self, topic: str, payload: bytes, 
                            context: Optional[MessageContext] = None,
                            user: Optional[User] = None) -> str:
        """发布消息"""
        if self.state != MessageBusState.RUNNING:
            raise RuntimeError(f"服务未运行: {self.state}")
        
        # 创建消息上下文
        if context is None:
            context = MessageContext(
                message_id=str(uuid.uuid4()),
                topic=topic,
                user=user,
                source_node=self.config.node_id
            )
        
        # 安全检查
        if user and self.security_manager:
            # 认证检查
            if not user.is_active:
                raise PermissionError("用户已被停用")
            
            # 授权检查
            if not self.security_manager.authorize(user, f"topic:{topic}", "write"):
                raise PermissionError("没有写入权限")
            
            # 消息大小验证
            if not self.security_manager.validate_message_size(payload):
                raise ValueError("消息大小超过限制")
        
        try:
            # 创建消息信封
            envelope = MessageEnvelope(
                id=context.message_id,
                topic=topic,
                payload=payload,
                attributes=context.metadata,
                priority=context.priority,
                timestamp=context.timestamp
            )
            
            # 加密消息（如果启用）
            if self.config.enable_encryption and user and self.security_manager:
                encrypted_data = self.security_manager.encrypt_message(payload, user)
                envelope.payload = json.dumps(encrypted_data).encode()
                envelope.attributes['encrypted'] = 'true'
                context.encryption_enabled = True
            
            # 压缩消息（如果启用）
            if self.config.enable_compression and context.compression != CompressionType.NONE:
                envelope.compression_type = context.compression
                envelope.compressed = True
            
            # 提交到处理器
            success = await self.processor.submit_message(envelope)
            
            if success:
                # 存储消息
                if self.config.enable_persistence and self.storage_manager:
                    await self.storage_manager.store_message(topic, envelope)
                
                # 更新主题统计
                self.topic_manager.increment_message_count(topic)
                
                # 记录指标
                if self.metrics_collector:
                    self.metrics_collector.record_message_published(
                        topic, len(payload), success=True
                    )
                
                # 审计日志
                if self.security_manager:
                    self.security_manager.audit_logger.log_event(
                        self.security_manager.audit_logger.AuditEventType.MESSAGE_PUBLISH,
                        user.id if user else None,
                        f"topic:{topic}",
                        "publish",
                        "success",
                        details=context.to_dict()
                    )
                
                logger.debug(f"消息发布成功: {context.message_id} -> {topic}")
                return context.message_id
            else:
                raise RuntimeError("消息提交失败")
        
        except Exception as e:
            # 记录失败指标
            if self.metrics_collector:
                self.metrics_collector.record_message_published(
                    topic, len(payload), success=False
                )
            
            # 审计日志
            if self.security_manager and user:
                self.security_manager.audit_logger.log_event(
                    self.security_manager.audit_logger.AuditEventType.MESSAGE_PUBLISH,
                    user.id,
                    f"topic:{topic}",
                    "publish",
                    "failure",
                    details={'error': str(e)}
                )
            
            logger.error(f"消息发布失败: {e}")
            raise
    
    async def consume_messages(self, topic: str, subscriber_id: str,
                             handler: Optional[MessageHandler] = None,
                             user: Optional[User] = None) -> List[MessageEnvelope]:
        """消费消息"""
        if self.state != MessageBusState.RUNNING:
            raise RuntimeError(f"服务未运行: {self.state}")
        
        # 安全检查
        if user and self.security_manager:
            if not self.security_manager.authorize(user, f"topic:{topic}", "read"):
                raise PermissionError("没有读取权限")
        
        try:
            # 订阅主题
            if not self.topic_manager.subscribe(topic, subscriber_id, handler):
                # 如果主题不存在，尝试创建
                if not self.topic_manager.create_topic(topic):
                    raise ValueError(f"主题不存在且创建失败: {topic}")
                self.topic_manager.subscribe(topic, subscriber_id, handler)
            
            # 这里应该实现实际的消息消费逻辑
            # 由于这是一个框架，具体的消费逻辑会根据实际的消息存储实现
            messages = []
            
            # 记录指标
            if self.metrics_collector:
                processing_time = 0.1  # 模拟处理时间
                self.metrics_collector.record_message_consumed(
                    topic, processing_time, success=True
                )
            
            # 审计日志
            if self.security_manager and user:
                self.security_manager.audit_logger.log_event(
                    self.security_manager.audit_logger.AuditEventType.MESSAGE_CONSUME,
                    user.id,
                    f"topic:{topic}",
                    "consume",
                    "success",
                    details={'subscriber_id': subscriber_id, 'message_count': len(messages)}
                )
            
            return messages
        
        except Exception as e:
            # 记录失败指标
            if self.metrics_collector:
                self.metrics_collector.record_message_consumed(
                    topic, 0, success=False
                )
            
            logger.error(f"消息消费失败: {e}")
            raise
    
    async def create_topic(self, topic: str, config: Dict[str, Any] = None,
                          user: Optional[User] = None) -> bool:
        """创建主题"""
        if self.state != MessageBusState.RUNNING:
            raise RuntimeError(f"服务未运行: {self.state}")
        
        # 安全检查
        if user and self.security_manager:
            if not self.security_manager.authorize(user, f"topic:{topic}", "manage"):
                raise PermissionError("没有管理权限")
        
        try:
            # 在本地创建主题
            success = self.topic_manager.create_topic(topic, config)
            
            # 在存储层创建主题
            if success and self.storage_manager:
                await self.storage_manager.create_topic(topic)
            
            return success
        
        except Exception as e:
            logger.error(f"创建主题失败: {e}")
            raise
    
    async def delete_topic(self, topic: str, user: Optional[User] = None) -> bool:
        """删除主题"""
        if self.state != MessageBusState.RUNNING:
            raise RuntimeError(f"服务未运行: {self.state}")
        
        # 安全检查
        if user and self.security_manager:
            if not self.security_manager.authorize(user, f"topic:{topic}", "manage"):
                raise PermissionError("没有管理权限")
        
        try:
            # 在存储层删除主题
            if self.storage_manager:
                await self.storage_manager.delete_topic(topic)
            
            # 在本地删除主题
            success = self.topic_manager.delete_topic(topic)
            
            return success
        
        except Exception as e:
            logger.error(f"删除主题失败: {e}")
            raise
    
    def get_service_info(self) -> Dict[str, Any]:
        """获取服务信息"""
        return {
            'service': {
                'name': self.config.service_name,
                'version': self.config.service_version,
                'mode': self.config.service_mode.value,
                'state': self.state.value,
                'node_id': self.config.node_id,
                'uptime': time.time() - self.start_time if self.start_time > 0 else 0
            },
            'config': {
                'max_message_size': self.config.max_message_size,
                'batch_size': self.config.batch_size,
                'worker_threads': self.config.worker_threads,
                'enable_persistence': self.config.enable_persistence,
                'enable_replication': self.config.enable_replication,
                'enable_compression': self.config.enable_compression,
                'enable_encryption': self.config.enable_encryption
            },
            'topics': self.topic_manager.list_topics(),
            'components': {
                'processor': self.processor is not None,
                'router': self.router is not None,
                'storage_manager': self.storage_manager is not None,
                'metrics_collector': self.metrics_collector is not None,
                'security_manager': self.security_manager is not None
            }
        }
    
    async def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        return await self.health_checker.check_health()
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        if self.metrics_collector:
            return self.metrics_collector.get_metrics_summary()
        return {}
    
    def get_security_stats(self) -> Dict[str, Any]:
        """获取安全统计"""
        if self.security_manager:
            return self.security_manager.get_security_stats()
        return {}
    
    @asynccontextmanager
    async def message_transaction(self, user: Optional[User] = None):
        """消息事务上下文管理器"""
        transaction_id = str(uuid.uuid4())
        
        try:
            logger.debug(f"开始消息事务: {transaction_id}")
            yield transaction_id
            logger.debug(f"提交消息事务: {transaction_id}")
        except Exception as e:
            logger.error(f"回滚消息事务: {transaction_id}, 错误: {e}")
            raise
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.stop()


class MessageBusServiceFactory:
    """消息总线服务工厂"""
    
    @staticmethod
    def create_enhanced_message_bus_service(
        config: Optional[MessageBusConfig] = None
    ) -> EnhancedMessageBusService:
        """创建增强消息总线服务"""
        if config is None:
            config = MessageBusConfig()
        
        return EnhancedMessageBusService(config)
    
    @staticmethod
    def create_from_dict(config_dict: Dict[str, Any]) -> EnhancedMessageBusService:
        """从字典创建服务"""
        # 这里可以实现从字典配置创建服务的逻辑
        config = MessageBusConfig()
        return EnhancedMessageBusService(config)
    
    @staticmethod
    def create_from_file(config_file: str) -> EnhancedMessageBusService:
        """从配置文件创建服务"""
        # 这里可以实现从配置文件创建服务的逻辑
        config = MessageBusConfig()
        return EnhancedMessageBusService(config) 