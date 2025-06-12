from typing import Any, Dict, List, Optional, Union

"""
__init__ - 索克生活项目模块
"""

from inquiry_service.core.config import Settings, get_settings
from inquiry_service.core.exceptions import InquiryServiceError
from inquiry_service.core.logging import setup_logging

"""
核心模块 - 包含基础类型、异常、配置等核心组件
"""


__all__ = [
    "InquiryServiceError",
    "Settings",
    "get_settings",
    "setup_logging",
]
