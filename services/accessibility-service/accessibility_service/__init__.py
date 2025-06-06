"""
__init__ - 索克生活项目模块
"""

from .core import AccessibilityService
from .models import *
from .services import *

"""
Accessibility Service Package

AI-powered accessibility service for Suoke Life platform.
Provides comprehensive accessibility features including:
- Visual accessibility analysis
- Audio accessibility processing
- Motor accessibility assistance
- Cognitive accessibility support
- Multi-modal accessibility integration
"""

__version__ = "1.0.0"
__author__ = "Suoke Life Team"
__email__ = "dev@suokelife.com"

# Import main components

__all__ = [
    "AccessibilityService",
    "__version__",
    "__author__",
    "__email__",
]
