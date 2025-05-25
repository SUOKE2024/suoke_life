#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
通用服务工厂
提供服务实例的创建、配置和依赖注入
"""

import logging
from typing import Dict, Any, Type, TypeVar, Optional
from abc import ABC, abstractmethod

from ..dependency_injection import DIContainer
from ..decorators.performance_decorator import set_performance_monitor
from ..decorators.error_decorator import set_error_handler
from ..decorators.cache_decorator import set_cache_manager

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ServiceFactory(ABC):
    """
    服务工厂基类
    """
    
    def __init__(self, container: DIContainer):
        """
        初始化服务工厂
        
        Args:
            container: 依赖注入容器
        """
        self.container = container
        self._service_cache: Dict[str, Any] = {}
        self._initialized = False
    
    async def initialize(self):
        """初始化工厂"""
        if self._initialized:
            return
        
        try:
            # 初始化装饰器全局实例
            await self._setup_decorators()
            
            # 执行子类特定的初始化
            await self._initialize_factory()
            
            self._initialized = True
            logger.info(f"{self.__class__.__name__} 初始化完成")
            
        except Exception as e:
            logger.error(f"服务工厂初始化失败: {str(e)}")
            raise
    
    async def _setup_decorators(self):
        """设置装饰器全局实例"""
        try:
            # 设置缓存管理器
            cache_manager = await self.container.get('cache_manager')
            if cache_manager:
                set_cache_manager(cache_manager)
                logger.debug("缓存管理器装饰器已设置")
                
        except Exception as e:
            logger.warning(f"装饰器设置失败: {str(e)}")
    
    @abstractmethod
    async def _initialize_factory(self):
        """子类特定的初始化逻辑"""
        pass
    
    async def create_service(self, service_type: Type[T], 
                           config: Dict[str, Any] = None) -> T:
        """
        创建服务实例
        
        Args:
            service_type: 服务类型
            config: 服务配置
        
        Returns:
            服务实例
        """
        if not self._initialized:
            await self.initialize()
        
        service_name = service_type.__name__
        
        # 检查缓存
        if service_name in self._service_cache:
            logger.debug(f"从缓存获取服务: {service_name}")
            return self._service_cache[service_name]
        
        try:
            # 尝试从容器获取服务（使用映射的服务名称）
            mapped_service_name = self._get_mapped_service_name(service_name)
            if mapped_service_name:
                try:
                    service = await self.container.get(mapped_service_name)
                    if service:
                        self._service_cache[service_name] = service
                        logger.debug(f"从容器获取服务: {service_name} -> {mapped_service_name}")
                        return service
                except ValueError:
                    # 服务未注册，继续创建新实例
                    pass
            
            # 创建新的服务实例
            service = await self._create_service_instance(service_type, config)
            
            # 缓存服务实例
            self._service_cache[service_name] = service
            
            logger.info(f"创建服务实例: {service_name}")
            return service
            
        except Exception as e:
            logger.error(f"创建服务失败: {service_name}, 错误: {str(e)}")
            raise
    
    async def _create_service_instance(self, service_type: Type[T], 
                                     config: Dict[str, Any] = None) -> T:
        """
        创建服务实例的具体实现
        
        Args:
            service_type: 服务类型
            config: 服务配置
        
        Returns:
            服务实例
        """
        # 获取构造函数参数
        dependencies = await self._resolve_dependencies(service_type)
        
        # 合并配置
        if config:
            dependencies.update(config)
        
        # 创建实例
        instance = service_type(**dependencies)
        
        # 如果实例有初始化方法，调用它
        if hasattr(instance, 'initialize') and callable(getattr(instance, 'initialize')):
            await instance.initialize()
        
        return instance
    
    async def _resolve_dependencies(self, service_type: Type) -> Dict[str, Any]:
        """
        解析服务依赖
        
        Args:
            service_type: 服务类型
        
        Returns:
            依赖字典
        """
        dependencies = {}
        
        # 获取类型注解
        if hasattr(service_type, '__annotations__'):
            for param_name, param_type in service_type.__annotations__.items():
                if param_name == 'return':
                    continue
                
                try:
                    # 从容器获取依赖
                    dependency = await self.container.get(param_type)
                    if dependency:
                        dependencies[param_name] = dependency
                except Exception as e:
                    logger.warning(f"解析依赖失败: {param_name} -> {param_type}, 错误: {str(e)}")
        
        return dependencies
    
    def _get_mapped_service_name(self, service_name: str) -> Optional[str]:
        """
        获取映射的服务名称
        
        Args:
            service_name: 原始服务名称（通常是类名）
        
        Returns:
            映射后的服务名称或None
        """
        # 服务名称映射表
        service_mapping = {
            'BlindAssistanceServiceImpl': 'blind_assistance',
            'SignLanguageServiceImpl': 'sign_language',
            'ScreenReadingServiceImpl': 'screen_reading',
            'VoiceAssistanceServiceImpl': 'voice_assistance',
            'ContentConversionServiceImpl': 'content_conversion',
            'TranslationServiceImpl': 'translation',
            'SettingsServiceImpl': 'settings',
            'ModelManager': 'model_manager',
            'CacheManager': 'cache_manager',
            'HealthMonitor': 'health_monitor'
        }
        
        return service_mapping.get(service_name)
    
    async def get_service(self, service_name: str) -> Optional[Any]:
        """
        获取已创建的服务实例
        
        Args:
            service_name: 服务名称
        
        Returns:
            服务实例或None
        """
        return self._service_cache.get(service_name)
    
    async def destroy_service(self, service_name: str):
        """
        销毁服务实例
        
        Args:
            service_name: 服务名称
        """
        if service_name in self._service_cache:
            service = self._service_cache[service_name]
            
            # 如果服务有清理方法，调用它
            if hasattr(service, 'cleanup') and callable(getattr(service, 'cleanup')):
                try:
                    await service.cleanup()
                except Exception as e:
                    logger.warning(f"服务清理失败: {service_name}, 错误: {str(e)}")
            
            del self._service_cache[service_name]
            logger.info(f"销毁服务实例: {service_name}")
    
    async def cleanup(self):
        """清理工厂资源"""
        # 销毁所有服务实例
        service_names = list(self._service_cache.keys())
        for service_name in service_names:
            await self.destroy_service(service_name)
        
        self._service_cache.clear()
        self._initialized = False
        
        logger.info(f"{self.__class__.__name__} 清理完成")
    
    def get_service_count(self) -> int:
        """获取已创建的服务数量"""
        return len(self._service_cache)
    
    def get_service_names(self) -> list:
        """获取已创建的服务名称列表"""
        return list(self._service_cache.keys())


class SingletonServiceFactory(ServiceFactory):
    """
    单例服务工厂
    确保每个服务类型只创建一个实例
    """
    
    async def _initialize_factory(self):
        """单例工厂特定的初始化"""
        logger.debug("单例服务工厂初始化")
    
    async def create_service(self, service_type: Type[T], 
                           config: Dict[str, Any] = None) -> T:
        """
        创建单例服务实例
        """
        service_name = service_type.__name__
        
        # 单例模式：如果已存在则直接返回
        if service_name in self._service_cache:
            return self._service_cache[service_name]
        
        return await super().create_service(service_type, config)


class PrototypeServiceFactory(ServiceFactory):
    """
    原型服务工厂
    每次调用都创建新的实例
    """
    
    async def _initialize_factory(self):
        """原型工厂特定的初始化"""
        logger.debug("原型服务工厂初始化")
    
    async def create_service(self, service_type: Type[T], 
                           config: Dict[str, Any] = None) -> T:
        """
        创建原型服务实例（每次都是新实例）
        """
        # 原型模式：不使用缓存，每次都创建新实例
        try:
            service = await self._create_service_instance(service_type, config)
            logger.debug(f"创建原型服务实例: {service_type.__name__}")
            return service
        except Exception as e:
            logger.error(f"创建原型服务失败: {service_type.__name__}, 错误: {str(e)}")
            raise 
 