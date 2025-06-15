"""
索克生活触诊服务包
基于AI的中医触诊智能分析微服务
"""

__version__ = "1.0.0"
__author__ = "Suoke Life Team"
__email__ = "dev@suoke.life"

from .main import app, main
from .config import get_settings

__all__ = [
    "app",
    "main", 
    "get_settings",
    "__version__"
]
