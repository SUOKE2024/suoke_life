from typing import Any, Dict, List, Optional, Union

"""
__init__ - 索克生活项目模块
"""

from .audio import AudioAccessibilityService
from .cognitive import CognitiveAccessibilityService
from .integration import IntegrationService
from .motor import MotorAccessibilityService
from .visual import VisualAccessibilityService

"""
Service layer components for accessibility functionality.
"""


__all__ = [
    "VisualAccessibilityService",
    "AudioAccessibilityService",
    "MotorAccessibilityService",
    "CognitiveAccessibilityService",
    "IntegrationService",
]
