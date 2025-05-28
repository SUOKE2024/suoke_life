"""
核心模块 - 包含配置、日志、异常等基础功能
"""

from xiaoke_service.core.config import settings
from xiaoke_service.core.exceptions import XiaokeServiceError
from xiaoke_service.core.logging import get_logger

__all__ = [
    "XiaokeServiceError",
    "get_logger",
    "settings",
]
