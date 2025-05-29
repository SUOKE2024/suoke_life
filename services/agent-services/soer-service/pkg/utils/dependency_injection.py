"""
依赖注入容器
提供统一的依赖管理和生命周期控制
"""
import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from contextlib import asynccontextmanager
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar('T')

class ServiceLifecycle(ABC):
    """服务生命周期接口"""

    @abstractmethod
    async def start(self) -> None:
        """启动服务"""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """停止服务"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """健康检查"""
        pass

class DependencyContainer:
    """依赖注入容器"""

    def __init__(self):
        self._services: dict[str, Any] = {}
        self._factories: dict[str, Callable] = {}
        self._singletons: dict[str, Any] = {}
        self._lifecycle_services: dict[str, ServiceLifecycle] = {}
        self._started = False

    def register_singleton(self, name: str, instance: Any) -> None:
        """注册单例服务"""
        self._singletons[name] = instance
        if isinstance(instance, ServiceLifecycle):
            self._lifecycle_services[name] = instance
        logger.debug(f"注册单例服务: {name}")

    def register_factory(self, name: str, factory: Callable) -> None:
        """注册工厂函数"""
        self._factories[name] = factory
        logger.debug(f"注册工厂函数: {name}")

    def register_transient(self, name: str, cls: type[T], *args, **kwargs) -> None:
        """注册瞬态服务"""
        def factory():
            return cls(*args, **kwargs)
        self.register_factory(name, factory)

    def get(self, name: str) -> Any:
        """获取服务实例"""
        # 优先返回单例
        if name in self._singletons:
            return self._singletons[name]

        # 使用工厂创建实例
        if name in self._factories:
            instance = self._factories[name]()
            return instance

        raise ValueError(f"服务未注册: {name}")

    def get_typed(self, name: str, expected_type: type[T]) -> T:
        """获取指定类型的服务实例"""
        instance = self.get(name)
        if not isinstance(instance, expected_type):
            raise TypeError(f"服务 {name} 类型不匹配，期望 {expected_type}，实际 {type(instance)}")
        return instance

    async def start_all(self) -> None:
        """启动所有生命周期服务"""
        if self._started:
            return

        logger.info("启动依赖容器中的所有服务...")

        for name, service in self._lifecycle_services.items():
            try:
                await service.start()
                logger.info(f"服务 {name} 启动成功")
            except Exception as e:
                logger.error(f"服务 {name} 启动失败: {e}")
                raise

        self._started = True
        logger.info("所有服务启动完成")

    async def stop_all(self) -> None:
        """停止所有生命周期服务"""
        if not self._started:
            return

        logger.info("停止依赖容器中的所有服务...")

        # 反向停止服务
        for name, service in reversed(list(self._lifecycle_services.items())):
            try:
                await service.stop()
                logger.info(f"服务 {name} 停止成功")
            except Exception as e:
                logger.error(f"服务 {name} 停止失败: {e}")

        self._started = False
        logger.info("所有服务停止完成")

    async def health_check_all(self) -> dict[str, bool]:
        """检查所有服务健康状态"""
        results = {}

        for name, service in self._lifecycle_services.items():
            try:
                results[name] = await service.health_check()
            except Exception as e:
                logger.error(f"服务 {name} 健康检查失败: {e}")
                results[name] = False

        return results

    @asynccontextmanager
    async def lifespan(self):
        """生命周期上下文管理器"""
        try:
            await self.start_all()
            yield self
        finally:
            await self.stop_all()

# 全局容器实例
_container: DependencyContainer | None = None

def get_container() -> DependencyContainer:
    """获取全局依赖容器"""
    global _container
    if _container is None:
        _container = DependencyContainer()
    return _container

def setup_container(container: DependencyContainer) -> None:
    """设置全局依赖容器"""
    global _container
    _container = container
