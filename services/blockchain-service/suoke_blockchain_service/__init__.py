from typing import Dict, List, Any, Optional, Union

"""
__init__ - 索克生活项目模块
"""

from .config import settings
from .main import create_app

"""
索克生活区块链服务

健康数据的区块链存储、验证和访问控制服务。
"""

__version__ = "0.1.0"
__author__ = "SuoKe Life Team"
__email__ = "dev@suokelife.com"


__all__ = ["__version__", "create_app", "settings"]
