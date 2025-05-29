"""
算诊微服务

传统中医算诊（五诊）微服务，提供五运六气、八卦体质、子午流注等算诊功能
"""

__version__ = "1.0.0"
__author__ = "Suoke Life Team"
__description__ = "Traditional Chinese Medicine Calculation Service"

# 基础配置
from .core.config import settings

__all__ = [
    "__version__",
    "__author__", 
    "__description__",
    "settings",
] 