"""
索克生活区块链服务

健康数据的区块链存储、验证和访问控制服务。
提供零知识证明、数据完整性验证和隐私保护功能。
"""

from typing import Any, Dict, List, Optional, Union

__version__ = "1.0.0"
__author__ = "SuoKe Life Team"
__email__ = "dev@suoke.life"

# 导出主要组件
from .config.settings import Settings, get_settings
from .core.exceptions import (
    BlockchainServiceError,
    ConfigurationError,
    NetworkError,
    StorageError,
    ValidationError,
)

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    # 异常类
    "BlockchainServiceError",
    "ConfigurationError",
    "ValidationError",
    "NetworkError",
    "StorageError",
    # 配置
    "Settings",
    "get_settings",
]
