"""核心模块 - 包含配置、日志、异常等基础组件"""

from health_data_service.core.config import settings
from health_data_service.core.logging import get_logger

__all__ = [
    "settings",
    "get_logger",
]
