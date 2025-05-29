"""
Utility functions and helpers for accessibility service.
"""

from .dependency_manager import DependencyManager
from .platform_checker import PlatformChecker

__all__ = [
    "PlatformChecker",
    "DependencyManager",
]
