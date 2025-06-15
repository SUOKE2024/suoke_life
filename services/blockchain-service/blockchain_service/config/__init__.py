"""
配置模块

提供类型安全的配置管理功能。
"""

from .settings import Settings, get_settings

__all__ = [
    "Settings",
    "get_settings",
]
