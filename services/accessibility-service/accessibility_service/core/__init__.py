"""
Core accessibility service components.
"""

from .engine import AccessibilityEngine
from .processor import AccessibilityProcessor
from .service import AccessibilityService

__all__ = [
    "AccessibilityService",
    "AccessibilityEngine",
    "AccessibilityProcessor",
]
