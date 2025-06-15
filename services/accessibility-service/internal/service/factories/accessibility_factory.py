#!/usr/bin/env python

"""
无障碍服务工厂
专门用于创建和配置无障碍相关的服务实例
"""

import logging
from typing import Any

from ..dependency_injection import DIContainer
from .service_factory import SingletonServiceFactory

logger = logging.getLogger(__name__)


class AccessibilityServiceFactory(SingletonServiceFactory):
    """
    无障碍服务工厂
    负责创建和管理所有无障碍相关的服务
    """

    def __init__(self, container: DIContainer):
        """
        初始化无障碍服务工厂

        Args:
            container: 依赖注入容器
        """
        super().__init__(container)
        self._service_configs: dict[str, dict[str, Any]] = {}

    async def _initialize_factory(self):
        """无障碍服务工厂特定的初始化"""
        logger.info("初始化无障碍服务工厂")

        # 加载服务配置
        await self._load_service_configs()

        # 预创建核心服务（暂时禁用以避免递归问题）
        # await self._precreate_core_services()

    async def _load_service_configs(self):
        """加载服务配置"""
        try:
            # 从配置管理器获取配置
            config_manager = await self.container.get("config_manager")
            if not config_manager:
                # 尝试备用名称
                config_manager = await self.container.get("IConfigManager")
            if config_manager:
                # 导盲服务配置
                self._service_configs["BlindAssistanceServiceImpl"] = {
                    "enabled": config_manager.get(
                        "services.blind_assistance.enabled", True
                    ),
                    "model_config": config_manager.get(
                        "services.blind_assistance.model", {}
                    ),
                    "cache_ttl": config_manager.get(
                        "services.blind_assistance.cache_ttl", 3600
                    ),
                    "max_concurrent_requests": config_manager.get(
                        "services.blind_assistance.max_concurrent", 10
                    ),
                }

                # 手语识别服务配置
                self._service_configs["SignLanguageServiceImpl"] = {
                    "enabled": config_manager.get(
                        "services.sign_language.enabled", True
                    ),
                    "model_config": config_manager.get(
                        "services.sign_language.model", {}
                    ),
                    "cache_ttl": config_manager.get(
                        "services.sign_language.cache_ttl", 1800
                    ),
                    "max_concurrent_requests": config_manager.get(
                        "services.sign_language.max_concurrent", 5
                    ),
                }

                # 屏幕阅读服务配置
                self._service_configs["ScreenReadingServiceImpl"] = {
                    "enabled": config_manager.get(
                        "services.screen_reading.enabled", True
                    ),
                    "voice_config": config_manager.get(
                        "services.screen_reading.voice", {}
                    ),
                    "cache_ttl": config_manager.get(
                        "services.screen_reading.cache_ttl", 600
                    ),
                    "max_concurrent_requests": config_manager.get(
                        "services.screen_reading.max_concurrent", 15
                    ),
                }

                # 语音辅助服务配置
                self._service_configs["VoiceAssistanceServiceImpl"] = {
                    "enabled": config_manager.get(
                        "services.voice_assistance.enabled", True
                    ),
                    "model_config": config_manager.get(
                        "services.voice_assistance.model", {}
                    ),
                    "cache_ttl": config_manager.get(
                        "services.voice_assistance.cache_ttl", 1200
                    ),
                    "max_concurrent_requests": config_manager.get(
                        "services.voice_assistance.max_concurrent", 8
                    ),
                }

                # 内容转换服务配置
                self._service_configs["ContentConversionServiceImpl"] = {
                    "enabled": config_manager.get(
                        "services.content_conversion.enabled", True
                    ),
                    "conversion_config": config_manager.get(
                        "services.content_conversion.config", {}
                    ),
                    "cache_ttl": config_manager.get(
                        "services.content_conversion.cache_ttl", 7200
                    ),
                    "max_concurrent_requests": config_manager.get(
                        "services.content_conversion.max_concurrent", 12
                    ),
                }

                logger.info("服务配置加载完成")
            else:
                logger.warning("配置管理器不可用，使用默认配置")
                self._load_default_configs()

        except Exception as e:
            logger.error(f"加载服务配置失败: {e!s}")
            self._load_default_configs()

    def _load_default_configs(self):
        """加载默认配置"""
        default_config = {
            "enabled": True,
            "cache_ttl": 3600,
            "max_concurrent_requests": 10,
        }

        service_names = [
            "BlindAssistanceServiceImpl",
            "SignLanguageServiceImpl",
            "ScreenReadingServiceImpl",
            "VoiceAssistanceServiceImpl",
            "ContentConversionServiceImpl",
        ]

        for service_name in service_names:
            self._service_configs[service_name] = default_config.copy()

        logger.info("默认服务配置加载完成")

    async def _precreate_core_services(self):
        """预创建核心服务"""
        try:
            # 预创建基础服务（这些服务启动时就需要）
            core_services = ["BlindAssistanceServiceImpl", "VoiceAssistanceServiceImpl"]

            for service_name in core_services:
                if self._service_configs.get(service_name, {}).get("enabled", True):
                    try:
                        # 动态导入服务类
                        service_class = await self._get_service_class(service_name)
                        if service_class:
                            await self.create_service(
                                service_class, self._service_configs[service_name]
                            )
                            logger.info(f"预创建核心服务: {service_name}")
                    except Exception as e:
                        logger.warning(f"预创建服务失败: {service_name}, 错误: {e!s}")

        except Exception as e:
            logger.error(f"预创建核心服务失败: {e!s}")

    async def _get_service_class(self, service_name: str):
        """
        动态获取服务类

        Args:
            service_name: 服务名称

        Returns:
            服务类或None
        """
        try:
            # 根据服务名称导入对应的实现类
            if service_name == "BlindAssistanceServiceImpl":
                from ..implementations.blind_assistance_impl import (
                    BlindAssistanceServiceImpl,
                )

                return BlindAssistanceServiceImpl
            elif service_name == "SignLanguageServiceImpl":
                from ..implementations.sign_language_impl import SignLanguageServiceImpl

                return SignLanguageServiceImpl
            elif service_name == "ScreenReadingServiceImpl":
                from ..implementations.screen_reading_impl import (
                    ScreenReadingServiceImpl,
                )

                return ScreenReadingServiceImpl
            elif service_name == "VoiceAssistanceServiceImpl":
                from ..implementations.voice_assistance_impl import (
                    VoiceAssistanceServiceImpl,
                )

                return VoiceAssistanceServiceImpl
            elif service_name == "ContentConversionServiceImpl":
                from ..implementations.content_conversion_impl import (
                    ContentConversionServiceImpl,
                )

                return ContentConversionServiceImpl
            else:
                logger.warning(f"未知的服务名称: {service_name}")
                return None

        except ImportError as e:
            logger.error(f"导入服务类失败: {service_name}, 错误: {e!s}")
            return None

    async def create_blind_assistance_service(self, config: dict[str, Any] = None):
        """
        创建导盲服务

        Args:
            config: 服务配置

        Returns:
            导盲服务实例
        """
        service_class = await self._get_service_class("BlindAssistanceServiceImpl")
        if not service_class:
            raise ValueError("无法获取导盲服务类")

        service_config = self._service_configs.get("BlindAssistanceServiceImpl", {})
        if config:
            service_config.update(config)

        return await self.create_service(service_class, service_config)

    async def create_sign_language_service(self, config: dict[str, Any] = None):
        """
        创建手语识别服务

        Args:
            config: 服务配置

        Returns:
            手语识别服务实例
        """
        service_class = await self._get_service_class("SignLanguageServiceImpl")
        if not service_class:
            raise ValueError("无法获取手语识别服务类")

        service_config = self._service_configs.get("SignLanguageServiceImpl", {})
        if config:
            service_config.update(config)

        return await self.create_service(service_class, service_config)

    async def create_screen_reading_service(self, config: dict[str, Any] = None):
        """
        创建屏幕阅读服务

        Args:
            config: 服务配置

        Returns:
            屏幕阅读服务实例
        """
        service_class = await self._get_service_class("ScreenReadingServiceImpl")
        if not service_class:
            raise ValueError("无法获取屏幕阅读服务类")

        service_config = self._service_configs.get("ScreenReadingServiceImpl", {})
        if config:
            service_config.update(config)

        return await self.create_service(service_class, service_config)

    async def create_voice_assistance_service(self, config: dict[str, Any] = None):
        """
        创建语音辅助服务

        Args:
            config: 服务配置

        Returns:
            语音辅助服务实例
        """
        service_class = await self._get_service_class("VoiceAssistanceServiceImpl")
        if not service_class:
            raise ValueError("无法获取语音辅助服务类")

        service_config = self._service_configs.get("VoiceAssistanceServiceImpl", {})
        if config:
            service_config.update(config)

        return await self.create_service(service_class, service_config)

    async def create_content_conversion_service(self, config: dict[str, Any] = None):
        """
        创建内容转换服务

        Args:
            config: 服务配置

        Returns:
            内容转换服务实例
        """
        service_class = await self._get_service_class("ContentConversionServiceImpl")
        if not service_class:
            raise ValueError("无法获取内容转换服务类")

        service_config = self._service_configs.get("ContentConversionServiceImpl", {})
        if config:
            service_config.update(config)

        return await self.create_service(service_class, service_config)

    async def get_service_status(self) -> dict[str, dict[str, Any]]:
        """
        获取所有服务的状态

        Returns:
            服务状态字典
        """
        status = {}

        for service_name in self._service_configs.keys():
            service = await self.get_service(service_name)
            status[service_name] = {
                "enabled": self._service_configs[service_name].get("enabled", False),
                "created": service is not None,
                "config": self._service_configs[service_name],
            }

            # 如果服务已创建，获取更详细的状态
            if service and hasattr(service, "get_status"):
                try:
                    service_status = await service.get_status()
                    status[service_name]["status"] = service_status
                except Exception as e:
                    status[service_name]["status_error"] = str(e)

        return status

    async def reload_service_config(self, service_name: str):
        """
        重新加载服务配置

        Args:
            service_name: 服务名称
        """
        try:
            # 销毁现有服务实例
            await self.destroy_service(service_name)

            # 重新加载配置
            await self._load_service_configs()

            # 如果服务启用，重新创建
            if self._service_configs.get(service_name, {}).get("enabled", True):
                service_class = await self._get_service_class(service_name)
                if service_class:
                    await self.create_service(
                        service_class, self._service_configs[service_name]
                    )
                    logger.info(f"重新加载服务配置: {service_name}")

        except Exception as e:
            logger.error(f"重新加载服务配置失败: {service_name}, 错误: {e!s}")
            raise
