from typing import Dict, List, Any, Optional, Union

"""
__init__ - 索克生活项目模块
"""

from xiaoke_service.core.config import settings
from xiaoke_service.core.logging import get_logger

"""
小克智能体服务 - 索克生活健康管理平台的核心AI智能体

小克专注于中医辨证论治和个性化健康管理, 结合现代AI技术
为用户提供智能化的健康咨询和管理服务。
"""

__version__ = "1.0.0"
__author__ = "Suoke Life Team"
__email__ = "dev@suoke.life"


__all__ = [
    "__author__",
    "__email__",
    "__version__",
    "get_logger",
    "settings",
]
