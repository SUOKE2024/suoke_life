"""
索克生活平台通用组件库

为索克生活健康管理平台的四个智能体（小艾、小克、老克、索儿）
提供统一的基础设施支持和通用组件。

主要功能模块：
- 服务治理：断路器、限流、重试策略
- 可观测性：监控、日志、分布式追踪
- 安全组件：认证、授权、加密
- 消息队列：Kafka、RabbitMQ统一接口
- 配置管理：动态配置、配置中心
- 健康检查：服务健康监控和聚合
- 性能优化：缓存、异步处理、数据库优化
- 服务网格：Istio、Linkerd、Envoy支持
- 测试框架：统一的测试工具集
"""

from typing import Any, Dict, List, Optional
import logging

# 版本信息
__version__ = "1.0.0"
__author__ = "索克生活技术团队"
__email__ = "tech@suoke.life"

# 核心组件导入
try:
    # 服务治理
    from ..governance import (
        CircuitBreaker,
        RateLimiter,
    )
    
    # 负载均衡器
    from ..load_balancer import LoadBalancer
    
    # 可观测性
    from ..observability import (
        MetricsCollector,
        LogAggregator,
        TracingManager,
    )
    
    # 安全组件
    from ..security import (
        EncryptionManager,
        JWTManager,
        OAuth2Provider,
        APIKeyManager,
    )
    
    # 健康检查
    from ..health import (
        HealthChecker,
        HealthMonitor,
        HealthAggregator,
        HealthStatus,
    )
    
    # 配置管理
    from ..config import (
        ConfigManager,
        ConfigCenter,
    )
    
    # 消息队列
    from ..messaging import (
        MessageQueue,
        KafkaClient,
        RabbitMQClient,
    )
    
    # 性能优化
    from ..performance import (
        AsyncOptimizer,
        CacheOptimizer,
        DBOptimizer,
    )
    
    # 测试框架
    from ..testing import (
        TestFramework,
        get_test_framework,
    )
    
    _components_available = True
    
except ImportError as e:
    logging.warning(f"部分组件导入失败: {e}")
    _components_available = False


class SuokeCommonComponents:
    """索克生活通用组件管理器"""
    
    def __init__(self):
        self._initialized_components: Dict[str, Any] = {}
        self._config: Dict[str, Any] = {}
    
    async def initialize(self, config: Optional[Dict[str, Any]] = None):
        """初始化所有组件"""
        self._config = config or {}
        
        # 即使部分组件导入失败，也尝试初始化可用的组件
        try:
            await self._init_health_components()
        except Exception as e:
            logging.warning(f"健康检查组件初始化失败: {e}")
        
        try:
            await self._init_observability_components()
        except Exception as e:
            logging.warning(f"可观测性组件初始化失败: {e}")
        
        try:
            await self._init_governance_components()
        except Exception as e:
            logging.warning(f"服务治理组件初始化失败: {e}")
        
        try:
            await self._init_security_components()
        except Exception as e:
            logging.warning(f"安全组件初始化失败: {e}")
        
        try:
            await self._init_messaging_components()
        except Exception as e:
            logging.warning(f"消息队列组件初始化失败: {e}")
        
        logging.info(f"索克生活通用组件初始化完成，已初始化 {len(self._initialized_components)} 个组件")
    
    async def _init_health_components(self):
        """初始化健康检查组件"""
        health_config = self._config.get("health", {})
        
        self._initialized_components["health_checker"] = HealthChecker()
        self._initialized_components["health_monitor"] = HealthMonitor()
        self._initialized_components["health_aggregator"] = HealthAggregator()
        
        # 初始化健康聚合器
        await self._initialized_components["health_aggregator"].initialize(health_config)
    
    async def _init_observability_components(self):
        """初始化可观测性组件"""
        observability_config = self._config.get("observability", {})
        
        # 初始化指标收集器
        metrics_config = observability_config.get("metrics", {})
        self._initialized_components["metrics_collector"] = MetricsCollector()
        await self._initialized_components["metrics_collector"].initialize(metrics_config)
        
        # 初始化日志聚合器
        logging_config = observability_config.get("logging", {})
        self._initialized_components["log_aggregator"] = LogAggregator()
        await self._initialized_components["log_aggregator"].initialize(logging_config)
        
        # 初始化追踪管理器
        tracing_config = observability_config.get("tracing", {})
        self._initialized_components["tracing_manager"] = TracingManager()
        await self._initialized_components["tracing_manager"].initialize(tracing_config)
    
    async def _init_governance_components(self):
        """初始化服务治理组件"""
        governance_config = self._config.get("governance", {})
        
        # 初始化断路器
        circuit_breaker_config = governance_config.get("circuit_breaker", {})
        self._initialized_components["circuit_breaker"] = CircuitBreaker()
        
        # 初始化限流器
        rate_limiter_config = governance_config.get("rate_limiter", {})
        self._initialized_components["rate_limiter"] = RateLimiter()
        
        # 初始化负载均衡器
        load_balancer_config = governance_config.get("load_balancer", {})
        self._initialized_components["load_balancer"] = LoadBalancer()
    
    async def _init_security_components(self):
        """初始化安全组件"""
        security_config = self._config.get("security", {})
        
        # 初始化加密管理器
        encryption_config = security_config.get("encryption", {})
        self._initialized_components["encryption_manager"] = EncryptionManager()
        
        # 初始化JWT管理器
        jwt_config = security_config.get("jwt", {})
        self._initialized_components["jwt_manager"] = JWTManager()
    
    async def _init_messaging_components(self):
        """初始化消息队列组件"""
        messaging_config = self._config.get("messaging", {})
        
        # 根据配置初始化相应的消息队列客户端
        if "kafka" in messaging_config:
            kafka_config = messaging_config["kafka"]
            self._initialized_components["kafka_client"] = KafkaClient()
            await self._initialized_components["kafka_client"].initialize(kafka_config)
        
        if "rabbitmq" in messaging_config:
            rabbitmq_config = messaging_config["rabbitmq"]
            self._initialized_components["rabbitmq_client"] = RabbitMQClient()
            await self._initialized_components["rabbitmq_client"].initialize(rabbitmq_config)
    
    def get_component(self, component_name: str) -> Any:
        """获取已初始化的组件"""
        if component_name not in self._initialized_components:
            raise ValueError(f"组件 {component_name} 未初始化")
        return self._initialized_components[component_name]
    
    def list_components(self) -> List[str]:
        """列出所有已初始化的组件"""
        return list(self._initialized_components.keys())
    
    async def shutdown(self):
        """关闭所有组件"""
        for component_name, component in self._initialized_components.items():
            try:
                if hasattr(component, 'shutdown'):
                    await component.shutdown()
                elif hasattr(component, 'close'):
                    await component.close()
            except Exception as e:
                logging.error(f"关闭组件 {component_name} 时出错: {e}")
        
        self._initialized_components.clear()
        logging.info("索克生活通用组件已关闭")


# 全局组件管理器实例
_global_components: Optional[SuokeCommonComponents] = None


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
    
    if _global_components is not None:
        await _global_components.shutdown()
        _global_components = None


# 便捷函数
async def get_health_checker() -> "HealthChecker":
    """获取健康检查器"""
    components = await get_components()
    return components.get_component("health_checker")


async def get_metrics_collector() -> "MetricsCollector":
    """获取指标收集器"""
    components = await get_components()
    return components.get_component("metrics_collector")


async def get_circuit_breaker() -> "CircuitBreaker":
    """获取断路器"""
    components = await get_components()
    return components.get_component("circuit_breaker")


# 导出的公共接口
__all__ = [
    # 版本信息
    "__version__",
    "__author__",
    "__email__",
    
    # 核心类
    "SuokeCommonComponents",
    
    # 全局函数
    "get_components",
    "shutdown_components",
    
    # 便捷函数
    "get_health_checker",
    "get_metrics_collector", 
    "get_circuit_breaker",
    
    # 组件类（如果可用）
]

# 如果组件可用，添加到导出列表
if _components_available:
    __all__.extend([
        # 服务治理
        "CircuitBreaker",
        "LoadBalancer", 
        "RateLimiter",
        "RetryPolicy",
        "ServiceRegistry",
        
        # 可观测性
        "MetricsCollector",
        "LogAggregator",
        "TracingManager",
        
        # 安全组件
        "EncryptionManager",
        "JWTManager",
        "OAuth2Provider",
        "APIKeyManager",
        
        # 健康检查
        "HealthChecker",
        "HealthMonitor",
        "HealthAggregator",
        "HealthStatus",
        
        # 配置管理
        "ConfigManager",
        "ConfigCenter",
        
        # 消息队列
        "MessageQueue",
        "KafkaClient",
        "RabbitMQClient",
        
        # 性能优化
        "AsyncOptimizer",
        "CacheOptimizer", 
        "DBOptimizer",
        
        # 测试框架
        "TestFramework",
        "get_test_framework",
    ])


def main() -> None:
    """主函数 - 用于测试和演示"""
    import asyncio
    
    async def demo():
        """演示组件使用"""
        try:
            # 初始化组件
            components = await get_components({
                "health": {"check_interval": 30},
                "observability": {
                    "metrics": {"port": 8080},
                    "logging": {"level": "INFO"}
                }
            })
            
            # 列出组件
            print("已初始化的组件:")
            for component_name in components.list_components():
                print(f"  - {component_name}")
            
            # 获取健康检查器
            health_checker = await get_health_checker()
            print(f"健康检查器: {health_checker}")
            
            # 关闭组件
            await shutdown_components()
            print("组件已关闭")
            
        except Exception as e:
            print(f"演示过程中出错: {e}")
    
    asyncio.run(demo())


if __name__=="__main__":
    main()
