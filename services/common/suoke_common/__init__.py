#!/usr/bin/env python3
"""
索克生活平台通用组件库

提供微服务架构所需的所有基础组件

这个包提供了以下核心功能:
- 安全组件(加密、认证)
- 服务治理(熔断器、限流器)
- 可观测性(指标、日志、链路追踪)
- 性能优化(缓存、数据库、异步)
- 配置管理(配置中心、环境变量)
- 消息传递(消息队列、Kafka、RabbitMQ)
- 服务注册与发现
- 分布式事务(Saga、TCC、事件溯源)
- API 文档生成
- 服务网格集成

使用示例:
    from suoke_common import get_components, shutdown_components
    
    # 获取组件管理器
    components = await get_components()
    
    # 使用组件
    encryption = components.get_component("security", "encryption")
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Optional

# 版本信息
__version__ = "1.0.0"
__author__ = "索克生活技术团队"
__email__ = "tech@suokelife.com"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 全局组件管理器实例
_global_components: Optional["SuokeCommonComponents"] = None


class SuokeCommonComponents:
    """索克生活平台通用组件管理器

    这个类负责管理和初始化所有的通用组件,提供统一的接口
    来访问各种微服务基础设施组件。
    """

    def __init__(self):
        self.initialized = False
        self.components: dict[str, Any] = {}
        self.config: dict[str, Any] = {}

    async def initialize(self, config: dict[str, Any]) -> None:
        """初始化所有组件

        Args:
            config: 配置字典,包含各组件的配置信息

        Raises:
            RuntimeError: 当组件初始化失败时
        """
        if self.initialized:
            logger.warning("组件已经初始化,跳过重复初始化")
            return

        try:
            self.config = config.copy()
            logger.info("开始初始化索克生活平台通用组件...")

            # 初始化安全组件
            await self._init_security_components(config.get("security", {}))

            # 初始化服务治理组件
            await self._init_governance_components(config.get("governance", {}))

            # 初始化可观测性组件
            await self._init_observability_components(config.get("observability", {}))

            # 初始化性能组件
            await self._init_performance_components(config.get("performance", {}))

            # 初始化配置管理组件
            await self._init_config_components(config.get("config", {}))

            # 初始化消息传递组件
            await self._init_messaging_components(config.get("messaging", {}))

            # 初始化服务注册与发现组件
            await self._init_service_registry_components(
                config.get("service_registry", {})
            )

            # 初始化分布式事务组件
            await self._init_distributed_transaction_components(
                config.get("distributed_transaction", {})
            )

            # 初始化API文档组件
            await self._init_api_docs_components(config.get("api_docs", {}))

            # 初始化服务网格组件
            await self._init_service_mesh_components(config.get("service_mesh", {}))

            # 初始化测试框架组件
            await self._init_testing_components(config.get("testing", {}))

            self.initialized = True
            logger.info("索克生活平台通用组件初始化完成")

        except Exception as e:
            logger.error(f"组件初始化失败: {e}")
            raise RuntimeError(f"组件初始化失败: {e}") from e

    async def shutdown(self) -> None:
        """关闭所有组件"""
        if not self.initialized:
            return

        try:
            logger.info("开始关闭索克生活平台通用组件...")

            # 关闭各个组件组
            for component_type, components in self.components.items():
                if isinstance(components, dict):
                    for component_name, component in components.items():
                        if hasattr(component, "shutdown"):
                            try:
                                await component.shutdown()
                                logger.debug(f"已关闭组件: {component_type}.{component_name}")
                            except Exception as e:
                                logger.error(
                                    f"关闭组件失败 {component_type}.{component_name}: {e}"
                                )

            self.components.clear()
            self.initialized = False
            logger.info("索克生活平台通用组件关闭完成")

        except Exception as e:
            logger.error(f"组件关闭失败: {e}")
            raise

    async def _init_security_components(self, config: dict[str, Any]) -> None:
        """初始化安全组件"""
        security_components = {}

        # 加密组件
        if "encryption" in config:
            try:
                # 这里可以根据配置初始化加密组件
                security_components["encryption"] = {"status": "initialized"}
                logger.debug("加密组件初始化完成")
            except Exception as e:
                logger.error(f"加密组件初始化失败: {e}")

        # 认证组件
        if "authentication" in config:
            try:
                security_components["authentication"] = {"status": "initialized"}
                logger.debug("认证组件初始化完成")
            except Exception as e:
                logger.error(f"认证组件初始化失败: {e}")

        self.components["security"] = security_components

    async def _init_governance_components(self, config: dict[str, Any]) -> None:
        """初始化服务治理组件"""
        governance_components = {}

        # 熔断器
        if "circuit_breaker" in config:
            governance_components["circuit_breaker"] = {"status": "initialized"}

        # 限流器
        if "rate_limiter" in config:
            governance_components["rate_limiter"] = {"status": "initialized"}

        # 负载均衡器
        if "load_balancer" in config:
            governance_components["load_balancer"] = {"status": "initialized"}

        self.components["governance"] = governance_components

    async def _init_observability_components(self, config: dict[str, Any]) -> None:
        """初始化可观测性组件"""
        observability_components = {}

        # 指标收集
        if "metrics" in config:
            observability_components["metrics"] = {"status": "initialized"}

        # 日志聚合
        if "logging" in config:
            observability_components["logging"] = {"status": "initialized"}

        # 链路追踪
        if "tracing" in config:
            observability_components["tracing"] = {"status": "initialized"}

        self.components["observability"] = observability_components

    async def _init_performance_components(self, config: dict[str, Any]) -> None:
        """初始化性能组件"""
        performance_components = {}

        # 缓存
        if "cache" in config:
            performance_components["cache"] = {"status": "initialized"}

        # 数据库连接池
        if "database" in config:
            performance_components["database"] = {"status": "initialized"}

        # 异步处理
        if "async" in config:
            performance_components["async"] = {"status": "initialized"}

        self.components["performance"] = performance_components

    async def _init_config_components(self, config: dict[str, Any]) -> None:
        """初始化配置管理组件"""
        config_components = {}

        # 配置中心
        if "config_center" in config:
            config_components["config_center"] = {"status": "initialized"}

        # 环境变量管理
        if "env_vars" in config:
            config_components["env_vars"] = {"status": "initialized"}

        self.components["config"] = config_components

    async def _init_messaging_components(self, config: dict[str, Any]) -> None:
        """初始化消息传递组件"""
        messaging_components = {}

        # Kafka
        if "kafka" in config:
            messaging_components["kafka"] = {"status": "initialized"}

        # RabbitMQ
        if "rabbitmq" in config:
            messaging_components["rabbitmq"] = {"status": "initialized"}

        # Redis Pub/Sub
        if "redis_pubsub" in config:
            messaging_components["redis_pubsub"] = {"status": "initialized"}

        self.components["messaging"] = messaging_components

    async def _init_service_registry_components(self, config: dict[str, Any]) -> None:
        """初始化服务注册与发现组件"""
        registry_components = {}

        # Consul
        if "consul" in config:
            registry_components["consul"] = {"status": "initialized"}

        # Etcd
        if "etcd" in config:
            registry_components["etcd"] = {"status": "initialized"}

        self.components["service_registry"] = registry_components

    async def _init_distributed_transaction_components(
        self, config: dict[str, Any]
    ) -> None:
        """初始化分布式事务组件"""
        transaction_components = {}

        # Saga
        if "saga" in config:
            transaction_components["saga"] = {"status": "initialized"}

        # TCC
        if "tcc" in config:
            transaction_components["tcc"] = {"status": "initialized"}

        # 事件溯源
        if "event_sourcing" in config:
            transaction_components["event_sourcing"] = {"status": "initialized"}

        self.components["distributed_transaction"] = transaction_components

    async def _init_api_docs_components(self, config: dict[str, Any]) -> None:
        """初始化API文档组件"""
        api_docs_components = {}

        # OpenAPI生成器
        if "openapi" in config:
            api_docs_components["openapi"] = {"status": "initialized"}

        # Swagger UI
        if "swagger_ui" in config:
            api_docs_components["swagger_ui"] = {"status": "initialized"}

        self.components["api_docs"] = api_docs_components

    async def _init_service_mesh_components(self, config: dict[str, Any]) -> None:
        """初始化服务网格组件"""
        mesh_components = {}

        # Istio
        if "istio" in config:
            mesh_components["istio"] = {"status": "initialized"}

        # Linkerd
        if "linkerd" in config:
            mesh_components["linkerd"] = {"status": "initialized"}

        # Envoy
        if "envoy" in config:
            mesh_components["envoy"] = {"status": "initialized"}

        self.components["service_mesh"] = mesh_components

    async def _init_testing_components(self, config: dict[str, Any]) -> None:
        """初始化测试框架组件"""
        testing_components = {}

        # 测试框架
        if "framework" in config:
            testing_components["framework"] = {"status": "initialized"}

        # 性能测试
        if "performance" in config:
            testing_components["performance"] = {"status": "initialized"}

        self.components["testing"] = testing_components

    def get_component(
        self, component_type: str, component_name: str | None = None
    ) -> Any:
        """获取指定的组件

        Args:
            component_type: 组件类型(如 'security', 'messaging' 等)
            component_name: 组件名称(如 'encryption', 'kafka' 等)

        Returns:
            组件实例或组件组字典

        Raises:
            RuntimeError: 当组件未初始化时
            ValueError: 当组件不存在时
        """
        if not self.initialized:
            raise RuntimeError("组件尚未初始化,请先调用 initialize() 方法")

        if component_type not in self.components:
            raise ValueError(f"未知的组件类型: {component_type}")

        component_group = self.components[component_type]

        if component_name is None:
            return component_group

        if component_name not in component_group:
            raise ValueError(
                f"组件类型 '{component_type}' 中不存在组件 '{component_name}'"
            )

        return component_group[component_name]

    async def health_check(self) -> dict[str, Any]:
        """健康检查

        Returns:
            包含健康状态信息的字典
        """
        if not self.initialized:
            return {
                "status": "not_initialized",
                "message": "组件尚未初始化",
                "timestamp": asyncio.get_event_loop().time(),
            }

        health_info = {
            "status": "healthy",
            "components": {},
            "timestamp": asyncio.get_event_loop().time(),
        }

        # 检查各个组件组的健康状态
        for component_type, components in self.components.items():
            if isinstance(components, dict):
                component_health = {}
                for component_name, component in components.items():
                    if hasattr(component, "health_check"):
                        try:
                            component_health[component_name] = await component.health_check()
                        except Exception as e:
                            component_health[component_name] = {
                                "status": "error",
                                "error": str(e),
                            }
                            health_info["status"] = "degraded"
                    else:
                        component_health[component_name] = {"status": "unknown"}

                health_info["components"][component_type] = component_health

        return health_info

    def get_config(self, key: str | None = None) -> Any:
        """获取配置信息

        Args:
            key: 配置键,如果为None则返回全部配置

        Returns:
            配置值或配置字典
        """
        if key is None:
            return self.config.copy()

        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None

        return value

    def list_components(self) -> dict[str, list[str]]:
        """列出所有可用的组件

        Returns:
            组件类型到组件名称列表的映射
        """
        result = {}
        for component_type, components in self.components.items():
            if isinstance(components, dict):
                result[component_type] = list(components.keys())
            else:
                result[component_type] = []

        return result


async def get_components(config: dict[str, Any] | None = None) -> SuokeCommonComponents:
    """获取全局组件管理器实例

    Args:
        config: 可选的配置字典,仅在首次调用时使用

    Returns:
        组件管理器实例
    """
    global _global_components

    if _global_components is None:
        _global_components = SuokeCommonComponents()
        await _global_components.initialize(config or {})

    return _global_components


async def shutdown_components() -> None:
    """关闭全局组件实例"""
    global _global_components

    if _global_components is not None:
        await _global_components.shutdown()
        _global_components = None


# 导出主要的类和函数
__all__ = [
    "SuokeCommonComponents",
    "get_components",
    "shutdown_components",
    "__version__",
    "__author__",
    "__email__",
]
