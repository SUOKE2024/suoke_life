"""
依赖注入容器
提供服务依赖管理和生命周期控制
"""
import asyncio
import logging
from functools import wraps
import inspect

logger = logging.getLogger(__name__)

T = TypeVar('T')

class ServiceLifetime:
    """服务生命周期枚举"""
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"

class ServiceDescriptor:
    """服务描述符"""
    def __init__(
        self,
        service_type: Type,
        implementation: Union[Type, Callable],
        lifetime: str = ServiceLifetime.TRANSIENT,
        factory: Optional[Callable] = None
    ):
        self.service_type = service_type
        self.implementation = implementation
        self.lifetime = lifetime
        self.factory = factory
        self.instance = None

class Container:
    """依赖注入容器"""
    
    def __init__(self):
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._singletons: Dict[Type, Any] = {}
        self._scoped_instances: Dict[Type, Any] = {}
        self._building = set()  # 防止循环依赖
    
    def register_singleton(self, service_type: Type[T], implementation: Union[Type[T], T]) -> 'Container':
        """注册单例服务"""
        if isinstance(implementation, type):
            descriptor = ServiceDescriptor(service_type, implementation, ServiceLifetime.SINGLETON)
        else:
            descriptor = ServiceDescriptor(service_type, implementation, ServiceLifetime.SINGLETON)
            descriptor.instance = implementation
            self._singletons[service_type] = implementation
        
        self._services[service_type] = descriptor
        logger.debug(f"注册单例服务: {service_type.__name__}")
        return self
    
    def register_transient(self, service_type: Type[T], implementation: Type[T]) -> 'Container':
        """注册瞬态服务"""
        descriptor = ServiceDescriptor(service_type, implementation, ServiceLifetime.TRANSIENT)
        self._services[service_type] = descriptor
        logger.debug(f"注册瞬态服务: {service_type.__name__}")
        return self
    
    def register_scoped(self, service_type: Type[T], implementation: Type[T]) -> 'Container':
        """注册作用域服务"""
        descriptor = ServiceDescriptor(service_type, implementation, ServiceLifetime.SCOPED)
        self._services[service_type] = descriptor
        logger.debug(f"注册作用域服务: {service_type.__name__}")
        return self
    
    def register_factory(self, service_type: Type[T], factory: Callable[..., T]) -> 'Container':
        """注册工厂方法"""
        descriptor = ServiceDescriptor(service_type, factory, ServiceLifetime.TRANSIENT, factory)
        self._services[service_type] = descriptor
        logger.debug(f"注册工厂服务: {service_type.__name__}")
        return self
    
    async def get_service(self, service_type: Type[T]) -> T:
        """获取服务实例"""
        if service_type in self._building:
            raise ValueError(f"检测到循环依赖: {service_type.__name__}")
        
        if service_type not in self._services:
            raise ValueError(f"服务未注册: {service_type.__name__}")
        
        descriptor = self._services[service_type]
        
        # 单例模式
        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            if service_type in self._singletons:
                return self._singletons[service_type]
            
            instance = await self._create_instance(descriptor)
            self._singletons[service_type] = instance
            return instance
        
        # 作用域模式
        elif descriptor.lifetime == ServiceLifetime.SCOPED:
            if service_type in self._scoped_instances:
                return self._scoped_instances[service_type]
            
            instance = await self._create_instance(descriptor)
            self._scoped_instances[service_type] = instance
            return instance
        
        # 瞬态模式
        else:
            return await self._create_instance(descriptor)
    
    async def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
        """创建服务实例"""
        self._building.add(descriptor.service_type)
        
        try:
            if descriptor.factory:
                # 使用工厂方法
                instance = await self._invoke_factory(descriptor.factory)
            elif descriptor.instance is not None:
                # 已有实例
                instance = descriptor.instance
            else:
                # 创建新实例
                instance = await self._create_new_instance(descriptor.implementation)
            
            return instance
        finally:
            self._building.discard(descriptor.service_type)
    
    async def _create_new_instance(self, implementation: Type) -> Any:
        """创建新的服务实例"""
        # 获取构造函数参数
        sig = inspect.signature(implementation.__init__)
        params = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            if param.annotation != inspect.Parameter.empty:
                # 递归解析依赖
                dependency = await self.get_service(param.annotation)
                params[param_name] = dependency
            elif param.default != inspect.Parameter.empty:
                # 使用默认值
                params[param_name] = param.default
            else:
                raise ValueError(f"无法解析参数 {param_name} 在 {implementation.__name__}")
        
        return implementation(**params)
    
    async def _invoke_factory(self, factory: Callable) -> Any:
        """调用工厂方法"""
        sig = inspect.signature(factory)
        params = {}
        
        for param_name, param in sig.parameters.items():
            if param.annotation != inspect.Parameter.empty:
                dependency = await self.get_service(param.annotation)
                params[param_name] = dependency
            elif param.default != inspect.Parameter.empty:
                params[param_name] = param.default
        
        result = factory(**params)
        
        # 如果是协程，等待结果
        if asyncio.iscoroutine(result):
            result = await result
        
        return result
    
    def clear_scoped(self):
        """清除作用域服务实例"""
        self._scoped_instances.clear()
        logger.debug("清除作用域服务实例")
    
    async def dispose(self):
        """释放容器资源"""
        # 释放单例服务
        for service_type, instance in self._singletons.items():
            if hasattr(instance, 'dispose'):
                try:
                    if asyncio.iscoroutinefunction(instance.dispose):
                        await instance.dispose()
                    else:
                        instance.dispose()
                except Exception as e:
                    logger.error(f"释放服务 {service_type.__name__} 时出错: {e}")
        
        # 释放作用域服务
        for service_type, instance in self._scoped_instances.items():
            if hasattr(instance, 'dispose'):
                try:
                    if asyncio.iscoroutinefunction(instance.dispose):
                        await instance.dispose()
                    else:
                        instance.dispose()
                except Exception as e:
                    logger.error(f"释放作用域服务 {service_type.__name__} 时出错: {e}")
        
        self._singletons.clear()
        self._scoped_instances.clear()
        logger.info("容器已释放")

# 全局容器实例
_container = Container()

def get_container() -> Container:
    """获取全局容器实例"""
    return _container

def inject(service_type: Type[T]) -> T:
    """依赖注入装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            container = get_container()
            service = await container.get_service(service_type)
            return await func(service, *args, **kwargs)
        return wrapper
    return decorator

def configure_services(container: Container) -> Container:
    """配置服务注册"""
    # 这个函数将在应用启动时被调用
    # 用于注册所有服务依赖
    return container 