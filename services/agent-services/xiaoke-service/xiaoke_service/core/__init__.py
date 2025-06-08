from typing import Dict, List, Any, Optional, Union

"""
__init__ - 索克生活项目模块
"""

from xiaoke_service.core.config import settings
from xiaoke_service.core.exceptions import XiaokeServiceError
from xiaoke_service.core.logging import get_logger

"""
核心模块 - 包含配置、日志、异常等基础功能
"""


__all__ = [
    "XiaokeServiceError",
    "get_logger",
    "settings",
]
