"""
依赖注入容器
统一管理所有服务组件的依赖关系和生命周期
"""

import asyncio
import inspect
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar

import structlog

from ..agent.decision_engine import DecisionEngine
from ..agent.learning_module import LearningModule
from ..agent.xiaoke_agent import XiaokeAgent
from ..service.food_agriculture_service import FoodAgricultureService
from ..service.medical_resource_coordinator import MedicalResourceCoordinator
from ..service.personalized_medical_service import PersonalizedMedicalService
from ..service.quality_control_service import QualityControlService
from ..service.resource_management_service import ResourceManagementService
from ..service.resource_scheduling_service import ResourceSchedulingService
from ..service.tcm_knowledge_service import TCMKnowledgeService
from ..service.wellness_tourism_service import WellnessTourismService
from .cache_manager import SmartCacheManager
from .config_manager import ConfigManager
from .performance_monitor import PerformanceMonitor

logger = structlog.get_logger(__name__)

T = TypeVar("T")

class ServiceLifecycle(ABC):
    """服务生命周期接口"""

    @abstractmethod
    async def initialize(self) -> None:
        """初始化服务"""
        pass

    @abstractmethod
    async def start(self) -> None:
        """启动服务"""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """停止服务"""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """清理资源"""
        pass

@dataclass
class ServiceDefinition:
    """服务定义"""

    service_type: Type
    factory: Optional[Callable] = None
    singleton: bool = True
    dependencies: List[str] = None
    lifecycle: bool = True

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

class DependencyInjectionContainer:
    """依赖注入容器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

        # 服务注册表
        self.services: Dict[str, ServiceDefinition] = {}
        self.instances: Dict[str, Any] = {}
        self.singletons: Dict[str, Any] = {}

        # 生命周期管理
        self.lifecycle_services: List[ServiceLifecycle] = []
        self.initialization_order: List[str] = []

        # 状态管理
        self.is_initialized = False
        self.is_started = False

        logger.info("依赖注入容器初始化完成")

    def register(
        self,
        name: str,
        service_type: Type[T],
        factory: Optional[Callable[..., T]] = None,
        singleton: bool = True,
        dependencies: List[str] = None,
        lifecycle: bool = True,
    ) -> "DependencyInjectionContainer":
        """注册服务"""
        self.services[name] = ServiceDefinition(
            service_type=service_type,
            factory=factory,
            singleton=singleton,
            dependencies=dependencies or [],
            lifecycle=lifecycle,
        )

        logger.debug(f"注册服务: {name} -> {service_type.__name__}")
        return self

    def register_singleton(
        self, name: str, instance: Any
    ) -> "DependencyInjectionContainer":
        """注册单例实例"""
        self.singletons[name] = instance
        logger.debug(f"注册单例: {name} -> {type(instance).__name__}")
        return self

    async def get(self, name: str) -> Any:
        """获取服务实例"""
        # 检查单例缓存
        if name in self.singletons:
            return self.singletons[name]

        # 检查实例缓存
        if name in self.instances:
            return self.instances[name]

        # 检查服务定义
        if name not in self.services:
            raise ValueError(f"服务未注册: {name}")

        service_def = self.services[name]

        # 创建实例
        instance = await self._create_instance(name, service_def)

        # 缓存实例
        if service_def.singleton:
            self.singletons[name] = instance
        else:
            self.instances[name] = instance

        return instance

    async def _create_instance(self, name: str, service_def: ServiceDefinition) -> Any:
        """创建服务实例"""
        try:
            # 解析依赖
            dependencies = {}
            for dep_name in service_def.dependencies:
                dependencies[dep_name] = await self.get(dep_name)

            # 创建实例
            if service_def.factory:
                # 使用工厂函数
                if asyncio.iscoroutinefunction(service_def.factory):
                    instance = await service_def.factory(**dependencies)
                else:
                    instance = service_def.factory(**dependencies)
            else:
                # 使用构造函数
                # 检查构造函数参数
                sig = inspect.signature(service_def.service_type.__init__)
                init_params = {}

                for param_name, param in sig.parameters.items():
                    if param_name == "self":
                        continue

                    if param_name in dependencies:
                        init_params[param_name] = dependencies[param_name]
                    elif param_name == "config":
                        init_params["config"] = self.config.get(name, {})
                    elif param.default is not param.empty:
                        # 有默认值，跳过
                        continue
                    else:
                        logger.warning(f"服务 {name} 缺少依赖参数: {param_name}")

                instance = service_def.service_type(**init_params)

            # 生命周期管理
            if service_def.lifecycle and isinstance(instance, ServiceLifecycle):
                self.lifecycle_services.append(instance)

            logger.debug(f"创建服务实例: {name} -> {type(instance).__name__}")
            return instance

        except Exception as e:
            logger.error(f"创建服务实例失败 {name}: {e}")
            raise

    async def initialize_all(self):
        """初始化所有服务"""
        if self.is_initialized:
            return

        try:
            # 确定初始化顺序
            self._determine_initialization_order()

            # 按顺序初始化服务
            for service_name in self.initialization_order:
                await self.get(service_name)

            # 初始化生命周期服务
            for service in self.lifecycle_services:
                await service.initialize()

            self.is_initialized = True
            logger.info("所有服务初始化完成")

        except Exception as e:
            logger.error(f"服务初始化失败: {e}")
            raise

    async def start_all(self):
        """启动所有服务"""
        if not self.is_initialized:
            await self.initialize_all()

        if self.is_started:
            return

        try:
            # 启动生命周期服务
            for service in self.lifecycle_services:
                await service.start()

            self.is_started = True
            logger.info("所有服务启动完成")

        except Exception as e:
            logger.error(f"服务启动失败: {e}")
            raise

    async def stop_all(self):
        """停止所有服务"""
        if not self.is_started:
            return

        try:
            # 反向停止生命周期服务
            for service in reversed(self.lifecycle_services):
                await service.stop()

            self.is_started = False
            logger.info("所有服务停止完成")

        except Exception as e:
            logger.error(f"服务停止失败: {e}")
            raise

    async def cleanup_all(self):
        """清理所有服务"""
        try:
            # 清理生命周期服务
            for service in reversed(self.lifecycle_services):
                await service.cleanup()

            # 清理缓存
            self.instances.clear()
            self.singletons.clear()
            self.lifecycle_services.clear()

            self.is_initialized = False
            self.is_started = False

            logger.info("所有服务清理完成")

        except Exception as e:
            logger.error(f"服务清理失败: {e}")
            raise

    def _determine_initialization_order(self):
        """确定初始化顺序（拓扑排序）"""
        # 简化实现：按依赖关系排序
        visited = set()
        temp_visited = set()
        order = []

        def visit(service_name: str):
            if service_name in temp_visited:
                raise ValueError(f"检测到循环依赖: {service_name}")

            if service_name in visited:
                return

            temp_visited.add(service_name)

            if service_name in self.services:
                for dep in self.services[service_name].dependencies:
                    visit(dep)

            temp_visited.remove(service_name)
            visited.add(service_name)
            order.append(service_name)

        for service_name in self.services:
            if service_name not in visited:
                visit(service_name)

        self.initialization_order = order
        logger.debug(f"服务初始化顺序: {order}")

    def get_service_info(self) -> Dict[str, Any]:
        """获取服务信息"""
        return {
            "registered_services": list(self.services.keys()),
            "singletons": list(self.singletons.keys()),
            "instances": list(self.instances.keys()),
            "lifecycle_services": len(self.lifecycle_services),
            "initialization_order": self.initialization_order,
            "is_initialized": self.is_initialized,
            "is_started": self.is_started,
        }

def init_container(config: Dict[str, Any]) -> DependencyInjectionContainer:
    """初始化依赖注入容器"""
    container = DependencyInjectionContainer(config)

    # 注册基础设施服务
    container.register("config_manager", ConfigManager, singleton=True, lifecycle=True)

    container.register(
        "performance_monitor",
        PerformanceMonitor,
        factory=lambda: PerformanceMonitor(config.get("performance", {})),
        singleton=True,
        lifecycle=True,
    )

    container.register(
        "cache_manager",
        SmartCacheManager,
        factory=lambda: SmartCacheManager(config.get("cache", {})),
        singleton=True,
        lifecycle=True,
    )

    # 注册智能体服务
    container.register(
        "learning_module",
        LearningModule,
        dependencies=["config_manager"],
        singleton=True,
        lifecycle=True,
    )

    container.register(
        "decision_engine",
        DecisionEngine,
        dependencies=["config_manager", "learning_module"],
        singleton=True,
        lifecycle=True,
    )

    container.register(
        "xiaoke_agent",
        XiaokeAgent,
        dependencies=["config_manager", "decision_engine", "learning_module"],
        singleton=True,
        lifecycle=True,
    )

    # 注册业务服务
    container.register(
        "resource_management_service",
        ResourceManagementService,
        dependencies=["config_manager", "cache_manager"],
        singleton=True,
        lifecycle=True,
    )

    container.register(
        "resource_scheduling_service",
        ResourceSchedulingService,
        dependencies=["config_manager", "cache_manager", "performance_monitor"],
        singleton=True,
        lifecycle=True,
    )

    container.register(
        "personalized_medical_service",
        PersonalizedMedicalService,
        dependencies=["config_manager", "xiaoke_agent", "cache_manager"],
        singleton=True,
        lifecycle=True,
    )

    container.register(
        "quality_control_service",
        QualityControlService,
        dependencies=["config_manager", "performance_monitor"],
        singleton=True,
        lifecycle=True,
    )

    container.register(
        "tcm_knowledge_service",
        TCMKnowledgeService,
        dependencies=["config_manager", "xiaoke_agent", "cache_manager"],
        singleton=True,
        lifecycle=True,
    )

    container.register(
        "food_agriculture_service",
        FoodAgricultureService,
        dependencies=["config_manager", "xiaoke_agent", "cache_manager"],
        singleton=True,
        lifecycle=True,
    )

    container.register(
        "wellness_tourism_service",
        WellnessTourismService,
        dependencies=["config_manager", "cache_manager"],
        singleton=True,
        lifecycle=True,
    )

    # 注册协调器服务
    container.register(
        "medical_resource_coordinator",
        MedicalResourceCoordinator,
        dependencies=[
            "config_manager",
            "resource_management_service",
            "resource_scheduling_service",
            "personalized_medical_service",
            "quality_control_service",
            "xiaoke_agent",
        ],
        singleton=True,
        lifecycle=True,
    )

    logger.info("依赖注入容器配置完成")
    return container

# 全局容器实例
_container: Optional[DependencyInjectionContainer] = None

def get_container() -> DependencyInjectionContainer:
    """获取全局容器实例"""
    if _container is None:
        raise RuntimeError("容器未初始化，请先调用 init_container")
    return _container

async def init_global_container(config: Dict[str, Any]) -> DependencyInjectionContainer:
    """初始化全局容器"""
    global _container
    _container = init_container(config)
    await _container.initialize_all()
    return _container
