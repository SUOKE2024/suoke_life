"""
索克生活平台通用组件库
提供微服务架构所需的所有基础组件
"""

from typing import Dict, Any, Optional
import asyncio
import logging
from pathlib import Path

# 版本信息
__version__ = "1.0.0"
__author__ = "索克生活技术团队"

# 组件导入
from .security import encryption, auth
from .governance import circuit_breaker, rate_limiter
from .observability import metrics, logging as obs_logging, tracing
from .performance import cache_optimization, db_optimization, async_optimization
from .config import config_manager, config_center
from .messaging import message_queue, kafka_client, rabbitmq_client
from .service_registry import service_registry
from .distributed_transaction import saga_manager, tcc_coordinator, event_sourcing
from .api_docs import openapi_generator, doc_decorators, swagger_ui
from .service_mesh import mesh_manager, istio_client, linkerd_client, envoy_config
from .testing import test_framework

logger = logging.getLogger(__name__)

class SuokeCommonComponents:
    """索克生活平台通用组件管理器"""
    
    def __init__(self):
        self.components = {}
        self.initialized = False
        
    async def initialize(self, config: Optional[Dict[str, Any]] = None):
        """初始化所有组件"""
        if self.initialized:
            return
            
        config = config or {}
        logger.info("开始初始化索克生活平台通用组件...")
        
        try:
            # 初始化配置管理
            self.components['config'] = await self._init_config(config.get('config', {}))
            
            # 初始化安全组件
            self.components['security'] = await self._init_security(config.get('security', {}))
            
            # 初始化消息组件
            self.components['messaging'] = await self._init_messaging(config.get('messaging', {}))
            
            # 初始化服务治理
            self.components['governance'] = await self._init_governance(config.get('governance', {}))
            
            # 初始化可观测性
            self.components['observability'] = await self._init_observability(config.get('observability', {}))
            
            # 初始化性能优化
            self.components['performance'] = await self._init_performance(config.get('performance', {}))
            
            # 初始化服务注册
            self.components['service_registry'] = await self._init_service_registry(config.get('service_registry', {}))
            
            # 初始化分布式事务
            self.components['distributed_transaction'] = await self._init_distributed_transaction(config.get('distributed_transaction', {}))
            
            # 初始化API文档
            self.components['api_docs'] = await self._init_api_docs(config.get('api_docs', {}))
            
            # 初始化服务网格
            self.components['service_mesh'] = await self._init_service_mesh(config.get('service_mesh', {}))
            
            # 初始化测试框架
            self.components['testing'] = await self._init_testing(config.get('testing', {}))
            
            self.initialized = True
            logger.info("索克生活平台通用组件初始化完成")
            
        except Exception as e:
            logger.error(f"组件初始化失败: {e}")
            raise
    
    async def _init_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """初始化配置管理组件"""
        from .config.config_manager import ConfigManager
        from .config.config_center import ConfigCenter
        
        config_mgr = ConfigManager()
        config_center = ConfigCenter()
        
        await config_mgr.initialize(config)
        await config_center.initialize(config)
        
        return {
            'manager': config_mgr,
            'center': config_center
        }
    
    async def _init_security(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """初始化安全组件"""
        from .security.encryption import EncryptionManager
        from .security.auth import AuthManager
        
        encryption_mgr = EncryptionManager()
        auth_mgr = AuthManager()
        
        await encryption_mgr.initialize(config.get('encryption', {}))
        await auth_mgr.initialize(config.get('auth', {}))
        
        return {
            'encryption': encryption_mgr,
            'auth': auth_mgr
        }
    

    
    async def _init_messaging(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """初始化消息组件"""
        from .messaging.message_queue import MessageQueue
        from .messaging.kafka_client import KafkaClient
        from .messaging.rabbitmq_client import RabbitMQClient
        
        message_queue = MessageQueue()
        kafka_client = KafkaClient()
        rabbitmq_client = RabbitMQClient()
        
        await message_queue.initialize(config.get('queue', {}))
        await kafka_client.initialize(config.get('kafka', {}))
        await rabbitmq_client.initialize(config.get('rabbitmq', {}))
        
        return {
            'queue': message_queue,
            'kafka': kafka_client,
            'rabbitmq': rabbitmq_client
        }
    
    async def _init_governance(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """初始化服务治理组件"""
        from .governance.circuit_breaker import CircuitBreaker
        from .governance.rate_limiter import RateLimiter
        
        circuit_breaker = CircuitBreaker()
        rate_limiter = RateLimiter()
        
        await circuit_breaker.initialize(config.get('circuit_breaker', {}))
        await rate_limiter.initialize(config.get('rate_limiter', {}))
        
        return {
            'circuit_breaker': circuit_breaker,
            'rate_limiter': rate_limiter
        }
    
    async def _init_observability(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """初始化可观测性组件"""
        from .observability.metrics import MetricsCollector
        from .observability.logging import LoggingManager
        from .observability.tracing import TracingManager
        
        metrics = MetricsCollector()
        logging_mgr = LoggingManager()
        tracing = TracingManager()
        
        await metrics.initialize(config.get('metrics', {}))
        await logging_mgr.initialize(config.get('logging', {}))
        await tracing.initialize(config.get('tracing', {}))
        
        return {
            'metrics': metrics,
            'logging': logging_mgr,
            'tracing': tracing
        }
    
    async def _init_performance(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """初始化性能优化组件"""
        from .performance.cache_optimization import CacheOptimizer
        from .performance.db_optimization import DatabaseOptimizer
        from .performance.async_optimization import AsyncOptimizer
        
        cache_optimizer = CacheOptimizer()
        db_optimizer = DatabaseOptimizer()
        async_optimizer = AsyncOptimizer()
        
        await cache_optimizer.initialize(config.get('cache', {}))
        await db_optimizer.initialize(config.get('database', {}))
        await async_optimizer.initialize(config.get('async', {}))
        
        return {
            'cache': cache_optimizer,
            'database': db_optimizer,
            'async': async_optimizer
        }
    
    async def _init_service_registry(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """初始化服务注册组件"""
        from .service_registry.service_registry import ServiceRegistry
        
        service_registry = ServiceRegistry()
        await service_registry.initialize(config)
        
        return {
            'registry': service_registry
        }
    
    async def _init_distributed_transaction(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """初始化分布式事务组件"""
        from .distributed_transaction.saga_manager import SagaManager
        from .distributed_transaction.tcc_coordinator import TCCCoordinator
        from .distributed_transaction.event_sourcing import EventSourcing
        
        saga_manager = SagaManager()
        tcc_coordinator = TCCCoordinator()
        event_sourcing = EventSourcing()
        
        await saga_manager.initialize(config.get('saga', {}))
        await tcc_coordinator.initialize(config.get('tcc', {}))
        await event_sourcing.initialize(config.get('event_sourcing', {}))
        
        return {
            'saga': saga_manager,
            'tcc': tcc_coordinator,
            'event_sourcing': event_sourcing
        }
    
    async def _init_api_docs(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """初始化API文档组件"""
        from .api_docs.openapi_generator import OpenAPIGenerator
        from .api_docs.swagger_ui import SwaggerUI
        
        openapi_gen = OpenAPIGenerator()
        swagger_ui = SwaggerUI()
        
        await openapi_gen.initialize(config.get('openapi', {}))
        await swagger_ui.initialize(config.get('swagger', {}))
        
        return {
            'openapi': openapi_gen,
            'swagger': swagger_ui
        }
    
    async def _init_service_mesh(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """初始化服务网格组件"""
        from .service_mesh.mesh_manager import ServiceMeshManager
        from .service_mesh.istio_client import IstioClient
        from .service_mesh.linkerd_client import LinkerdClient
        from .service_mesh.envoy_config import EnvoyConfig
        
        mesh_manager = ServiceMeshManager()
        istio_client = IstioClient()
        linkerd_client = LinkerdClient()
        envoy_config = EnvoyConfig()
        
        await mesh_manager.initialize(config.get('manager', {}))
        await istio_client.initialize(config.get('istio', {}))
        await linkerd_client.initialize(config.get('linkerd', {}))
        await envoy_config.initialize(config.get('envoy', {}))
        
        return {
            'manager': mesh_manager,
            'istio': istio_client,
            'linkerd': linkerd_client,
            'envoy': envoy_config
        }
    
    async def _init_testing(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """初始化测试框架组件"""
        from .testing.test_framework import TestFramework
        
        test_framework = TestFramework()
        await test_framework.initialize(config)
        
        return {
            'framework': test_framework
        }
    
    def get_component(self, component_type: str, component_name: str = None):
        """获取指定组件"""
        if not self.initialized:
            raise RuntimeError("组件未初始化，请先调用 initialize()")
        
        if component_type not in self.components:
            raise ValueError(f"未知的组件类型: {component_type}")
        
        component = self.components[component_type]
        
        if component_name:
            if isinstance(component, dict) and component_name in component:
                return component[component_name]
            else:
                raise ValueError(f"组件 {component_type} 中未找到 {component_name}")
        
        return component
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        health_status = {
            'status': 'healthy',
            'components': {},
            'timestamp': asyncio.get_event_loop().time()
        }
        
        for component_type, component in self.components.items():
            try:
                if hasattr(component, 'health_check'):
                    status = await component.health_check()
                    health_status['components'][component_type] = status
                else:
                    health_status['components'][component_type] = {'status': 'unknown'}
            except Exception as e:
                health_status['components'][component_type] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                health_status['status'] = 'degraded'
        
        return health_status
    
    async def shutdown(self):
        """关闭所有组件"""
        logger.info("开始关闭索克生活平台通用组件...")
        
        for component_type, component in self.components.items():
            try:
                if hasattr(component, 'shutdown'):
                    await component.shutdown()
                logger.info(f"组件 {component_type} 已关闭")
            except Exception as e:
                logger.error(f"关闭组件 {component_type} 失败: {e}")
        
        self.components.clear()
        self.initialized = False
        logger.info("索克生活平台通用组件已全部关闭")

# 全局组件管理器实例
_global_components = None

async def get_components(config: Optional[Dict[str, Any]] = None) -> SuokeCommonComponents:
    """获取全局组件管理器实例"""
    global _global_components
    
    if _global_components is None:
        _global_components = SuokeCommonComponents()
        await _global_components.initialize(config)
    
    return _global_components

async def shutdown_components():
    """关闭全局组件管理器"""
    global _global_components
    
    if _global_components:
        await _global_components.shutdown()
        _global_components = None

# 便捷函数
async def get_security_component(component_name: str = None):
    """获取安全组件"""
    components = await get_components()
    return components.get_component('security', component_name)



async def get_messaging_component(component_name: str = None):
    """获取消息组件"""
    components = await get_components()
    return components.get_component('messaging', component_name)

async def get_governance_component(component_name: str = None):
    """获取服务治理组件"""
    components = await get_components()
    return components.get_component('governance', component_name)

async def get_observability_component(component_name: str = None):
    """获取可观测性组件"""
    components = await get_components()
    return components.get_component('observability', component_name)

async def get_performance_component(component_name: str = None):
    """获取性能优化组件"""
    components = await get_components()
    return components.get_component('performance', component_name)

# 导出主要接口
__all__ = [
    'SuokeCommonComponents',
    'get_components',
    'shutdown_components',
    'get_security_component',
    'get_messaging_component',
    'get_governance_component',
    'get_observability_component',
    'get_performance_component',
    '__version__',
    '__author__'
] 