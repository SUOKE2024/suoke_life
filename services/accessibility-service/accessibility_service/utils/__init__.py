"""
__init__ - 索克生活项目模块
"""

from .dependency_manager import DependencyManager
from .platform_checker import PlatformChecker

"""
Utility functions and helpers for accessibility service.
"""


__all__ = [
    "PlatformChecker",
    "DependencyManager",
]
