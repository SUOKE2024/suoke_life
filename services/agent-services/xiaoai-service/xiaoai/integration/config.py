"""
集成服务配置模块

提供服务配置和设置管理
"""

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class ServiceConfig:
    """服务配置"""

    host: str = "localhost"
    port: int = 8000
    timeout: int = 30
    max_retries: int = 3


@dataclass
class ExternalServices:
    """外部服务配置"""

    def __post_init__(self):
        if not hasattr(self, 'look_service'):
            self.look_service = ServiceConfig(port=8001)
        if not hasattr(self, 'listen_service'):
            self.listen_service = ServiceConfig(port=8002)
        if not hasattr(self, 'inquiry_service'):
            self.inquiry_service = ServiceConfig(port=8003)
        if not hasattr(self, 'palpation_service'):
            self.palpation_service = ServiceConfig(port=8004)
        if not hasattr(self, 'calculation_service'):
            self.calculation_service = ServiceConfig(port=8005)


@dataclass
class Settings:
    """应用设置"""

    debug: bool = False
    log_level: str = "INFO"

    def __post_init__(self):
        if not hasattr(self, 'external_services'):
            self.external_services = ExternalServices()


# 全局设置实例
_settings = Settings()


def get_settings() -> Settings:
    """获取设置实例"""
    return _settings


def update_settings(**kwargs) -> None:
    """更新设置"""
    global _settings
    for key, value in kwargs.items():
        if hasattr(_settings, key):
            setattr(_settings, key, value)
