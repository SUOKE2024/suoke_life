"""
认证服务包

提供用户认证、授权和会话管理功能
"""

from .config import DEFAULT_CONFIG, AuthConfig, get_auth_config

__version__ = "0.1.0"
__author__ = "索克生活团队"

# 导出主要类和函数
__all__ = ["AuthConfig", "get_auth_config", "DEFAULT_CONFIG"]
