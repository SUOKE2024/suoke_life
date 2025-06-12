from typing import Any, Dict, List, Optional, Union

"""
__init__ - 索克生活项目模块
"""

from .core.config import settings
from .core.logging import get_logger

"""
Look Service - 索克生活望诊微服务

基于计算机视觉的中医望诊智能分析系统，提供面部、舌诊、眼诊等多种望诊功能。
"""

__version__ = "1.0.0"
__author__ = "Suoke Life Team"
__email__ = "dev@suoke.life"


__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "settings",
    "get_logger",
]
