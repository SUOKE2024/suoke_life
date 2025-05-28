"""
索克生活区块链服务

健康数据的区块链存储、验证和访问控制服务。
"""

__version__ = "0.1.0"
__author__ = "SuoKe Life Team"
__email__ = "dev@suokelife.com"

from .config import settings
from .main import create_app

__all__ = ["__version__", "create_app", "settings"]
