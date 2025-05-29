"""
核心模块 - 包含基础类型、异常、配置等核心组件
"""

from inquiry_service.core.config import Settings, get_settings
from inquiry_service.core.exceptions import InquiryServiceError
from inquiry_service.core.logging import setup_logging

__all__ = [
    "InquiryServiceError",
    "Settings",
    "get_settings",
    "setup_logging",
]
