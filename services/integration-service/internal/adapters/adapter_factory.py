"""
Adapter Factory for Platform Adapters
"""

from typing import Dict, Type
import logging

from .base import BaseAdapter
from .google_fit import GoogleFitAdapter
from .apple_health import AppleHealthAdapter
from .fitbit import FitbitAdapter
from .xiaomi import XiaomiAdapter
from .huawei import HuaweiAdapter
from .wechat import WeChatAdapter
from .alipay import AlipayAdapter
from ..model.user_integration import PlatformType
from ..service.config import get_settings


class AdapterFactory:
    """平台适配器工厂"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.settings = get_settings()
        self._adapters: Dict[PlatformType, BaseAdapter] = {}
        self._adapter_classes: Dict[PlatformType, Type[BaseAdapter]] = {
            PlatformType.APPLE_HEALTH: AppleHealthAdapter,
            PlatformType.GOOGLE_FIT: GoogleFitAdapter,
            PlatformType.FITBIT: FitbitAdapter,
            PlatformType.XIAOMI: XiaomiAdapter,
            PlatformType.HUAWEI: HuaweiAdapter,
            PlatformType.WECHAT: WeChatAdapter,
            PlatformType.ALIPAY: AlipayAdapter,
        }
    
    def get_adapter(self, platform: PlatformType) -> BaseAdapter:
        """获取平台适配器实例"""
        if platform not in self._adapters:
            self._adapters[platform] = self._create_adapter(platform)
        
        return self._adapters[platform]
    
    def _create_adapter(self, platform: PlatformType) -> BaseAdapter:
        """创建平台适配器实例"""
        if platform not in self._adapter_classes:
            raise ValueError(f"不支持的平台类型: {platform.value}")
        
        # 获取平台配置
        platform_config = self.settings.get_platform_config(platform.value)
        
        if not platform_config.get("enabled", False):
            raise ValueError(f"平台 {platform.value} 未启用")
        
        # 创建适配器实例
        adapter_class = self._adapter_classes[platform]
        adapter = adapter_class(platform_config, self.logger)
        
        self.logger.info(f"创建 {platform.value} 适配器成功")
        
        return adapter
    
    def get_supported_platforms(self) -> list[PlatformType]:
        """获取支持的平台列表"""
        enabled_platforms = []
        
        for platform in self._adapter_classes.keys():
            platform_config = self.settings.get_platform_config(platform.value)
            if platform_config.get("enabled", False):
                enabled_platforms.append(platform)
        
        return enabled_platforms
    
    def get_platform_info(self, platform: PlatformType) -> Dict[str, any]:
        """获取平台信息"""
        try:
            adapter = self.get_adapter(platform)
            return adapter.get_platform_info()
        except Exception as e:
            self.logger.error(f"获取平台信息失败: {platform.value}", error=str(e))
            return {
                "platform": platform.value,
                "enabled": False,
                "error": str(e)
            }
    
    def get_all_platforms_info(self) -> Dict[str, Dict[str, any]]:
        """获取所有平台信息"""
        platforms_info = {}
        
        for platform in PlatformType:
            platforms_info[platform.value] = self.get_platform_info(platform)
        
        return platforms_info 