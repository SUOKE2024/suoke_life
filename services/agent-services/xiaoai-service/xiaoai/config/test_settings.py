"""
测试用简化配置

用于重构验证测试的配置
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ServiceConfig:
    """服务配置"""
    host: str = "localhost"
    port: int = 8000


@dataclass
class ExternalServices:
    """外部服务配置"""
    look_service: ServiceConfig = field(default_factory=lambda: ServiceConfig(port=8001))
    listen_service: ServiceConfig = field(default_factory=lambda: ServiceConfig(port=8002))
    inquiry_service: ServiceConfig = field(default_factory=lambda: ServiceConfig(port=8003))
    palpation_service: ServiceConfig = field(default_factory=lambda: ServiceConfig(port=8004))
    calculation_service: ServiceConfig = field(default_factory=lambda: ServiceConfig(port=8005))


@dataclass
class TestSettings:
    """测试设置"""
    external_services: ExternalServices = field(default_factory=ExternalServices)


_test_settings: Optional[TestSettings] = None


def get_settings() -> TestSettings:
    """获取测试设置"""
    global _test_settings
    if _test_settings is None:
        _test_settings = TestSettings()
    return _test_settings