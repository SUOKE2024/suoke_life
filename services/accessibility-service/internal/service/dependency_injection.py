#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
依赖注入容器实现
"""

import logging
from typing import Dict, Any, Type, TypeVar, Optional, Callable
from dataclasses import dataclass
import asyncio
import inspect

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class ServiceDefinition:
    """服务定义"""
    service_type: Type
    implementation: Type
    singleton: bool = True
    factory: Optional[Callable] = None
    dependencies: Optional[Dict[str, str]] = None


class DIContainer:
    """依赖注入容器"""
    
    def __init__(self):
        self._services: Dict[str, ServiceDefinition] = {}
        self._instances: Dict[str, Any] = {}
        self._lock = asyncio.Lock()
    
    def register(self, 
                service_name: str,
                service_type: Type[T],
                implementation: Type[T] = None,
                singleton: bool = True,
                factory: Callable = None,
                dependencies: Dict[str, str] = None) -> 'DIContainer':
        """
        注册服务
        
        Args:
            service_name: 服务名称
            service_type: 服务接口类型
            implementation: 服务实现类型
            singleton: 是否单例
            factory: 工厂函数
            dependencies: 依赖映射
        """
        if implementation is None and factory is None:
            implementation = service_type
        
        self._services[service_name] = ServiceDefinition(
            service_type=service_type,
            implementation=implementation,
            singleton=singleton,
            factory=factory,
            dependencies=dependencies or {}
        )
        
        logger.debug(f"注册服务: {service_name} -> {implementation or factory}")
        return self
    
    async def get(self, service_name: str) -> Any:
        """获取服务实例"""
        async with self._lock:
            # 如果是单例且已存在实例，直接返回
            if service_name in self._instances:
                return self._instances[service_name]
            
            if service_name not in self._services:
                raise ValueError(f"服务未注册: {service_name}")
            
            service_def = self._services[service_name]
            instance = await self._create_instance(service_def)
            
            # 如果是单例，缓存实例
            if service_def.singleton:
                self._instances[service_name] = instance
            
            return instance
    
    async def _create_instance(self, service_def: ServiceDefinition) -> Any:
        """创建服务实例"""
        try:
            # 使用工厂函数创建
            if service_def.factory:
                if asyncio.iscoroutinefunction(service_def.factory):
                    return await service_def.factory()
                else:
                    return service_def.factory()
            
            # 解析构造函数依赖
            constructor = service_def.implementation.__init__
            sig = inspect.signature(constructor)
            
            kwargs = {}
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                
                # 检查是否有显式依赖映射
                if param_name in service_def.dependencies:
                    dependency_name = service_def.dependencies[param_name]
                    kwargs[param_name] = await self.get(dependency_name)
                # 尝试根据类型注解自动解析
                elif param.annotation != inspect.Parameter.empty:
                    dependency_name = self._find_service_by_type(param.annotation)
                    if dependency_name:
                        kwargs[param_name] = await self.get(dependency_name)
                # 检查是否有默认值
                elif param.default != inspect.Parameter.empty:
                    continue
                else:
                    logger.warning(f"无法解析依赖: {param_name} in {service_def.implementation}")
            
            return service_def.implementation(**kwargs)
            
        except Exception as e:
            logger.error(f"创建服务实例失败: {service_def.implementation}, 错误: {str(e)}")
            raise
    
    def _find_service_by_type(self, service_type: Type) -> Optional[str]:
        """根据类型查找服务名称"""
        for name, service_def in self._services.items():
            if service_def.service_type == service_type:
                return name
        return None
    
    async def initialize_all(self):
        """初始化所有单例服务"""
        logger.info("开始初始化所有单例服务")
        
        for service_name, service_def in self._services.items():
            if service_def.singleton:
                try:
                    await self.get(service_name)
                    logger.debug(f"初始化服务成功: {service_name}")
                except Exception as e:
                    logger.error(f"初始化服务失败: {service_name}, 错误: {str(e)}")
                    raise
        
        logger.info("所有单例服务初始化完成")
    
    async def shutdown(self):
        """关闭容器，清理资源"""
        logger.info("开始关闭依赖注入容器")
        
        for service_name, instance in self._instances.items():
            try:
                # 如果服务有cleanup方法，调用它
                if hasattr(instance, 'cleanup') and callable(getattr(instance, 'cleanup')):
                    if asyncio.iscoroutinefunction(instance.cleanup):
                        await instance.cleanup()
                    else:
                        instance.cleanup()
                    logger.debug(f"清理服务: {service_name}")
            except Exception as e:
                logger.error(f"清理服务失败: {service_name}, 错误: {str(e)}")
        
        self._instances.clear()
        logger.info("依赖注入容器关闭完成")
    
    def get_service_info(self) -> Dict[str, Dict[str, Any]]:
        """获取服务信息"""
        info = {}
        for name, service_def in self._services.items():
            info[name] = {
                'service_type': service_def.service_type.__name__,
                'implementation': service_def.implementation.__name__ if service_def.implementation else 'Factory',
                'singleton': service_def.singleton,
                'initialized': name in self._instances,
                'dependencies': service_def.dependencies
            }
        return info


# 全局容器实例
container = DIContainer()


def inject(service_name: str):
    """依赖注入装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            service = await container.get(service_name)
            return await func(service, *args, **kwargs)
        return wrapper
    return decorator


async def setup_container(config: Dict[str, Any]) -> DIContainer:
    """设置依赖注入容器"""
    from .model_manager import ModelManager
    from .cache_manager import CacheManager
    from .health_monitor import HealthMonitor
    from .implementations.blind_assistance_impl import BlindAssistanceServiceImpl
    from .implementations.sign_language_impl import SignLanguageServiceImpl
    from .implementations.screen_reading_impl import ScreenReadingServiceImpl
    from .implementations.voice_assistance_impl import VoiceAssistanceServiceImpl
    from .implementations.content_conversion_impl import ContentConversionServiceImpl
    from .implementations.translation_impl import TranslationServiceImpl
    from .implementations.settings_impl import SettingsServiceImpl
    from .interfaces import (
        IModelManager, ICacheManager, IHealthMonitor,
        IBlindAssistanceService, ISignLanguageService, IScreenReadingService,
        IVoiceAssistanceService, IContentConversionService, ITranslationService,
        ISettingsService
    )
    
    # 注册基础服务
    container.register('config', dict, factory=lambda: config)
    container.register('model_manager', IModelManager, ModelManager)
    container.register('cache_manager', ICacheManager, CacheManager)
    container.register('health_monitor', IHealthMonitor, HealthMonitor)
    
    # 注册业务服务
    container.register('blind_assistance', IBlindAssistanceService, BlindAssistanceServiceImpl)
    container.register('sign_language', ISignLanguageService, SignLanguageServiceImpl)
    container.register('screen_reading', IScreenReadingService, ScreenReadingServiceImpl)
    container.register('voice_assistance', IVoiceAssistanceService, VoiceAssistanceServiceImpl)
    container.register('content_conversion', IContentConversionService, ContentConversionServiceImpl)
    container.register('translation', ITranslationService, TranslationServiceImpl)
    container.register('settings', ISettingsService, SettingsServiceImpl)
    
    # 初始化所有服务
    await container.initialize_all()
    
    return container 