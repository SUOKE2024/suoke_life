from typing import Dict, List, Any, Optional, Union

"""
__init__ - 索克生活项目模块
"""

from .engine import AccessibilityEngine
from .processor import AccessibilityProcessor
from .service import AccessibilityService

"""
Core accessibility service components.
"""


__all__ = [
    "AccessibilityService",
    "AccessibilityEngine",
    "AccessibilityProcessor",
]
