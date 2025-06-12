from typing import Any, Dict, List, Optional, Union

"""
__init__ - 索克生活项目模块
"""

from .accessibility import *
from .analysis import *
from .response import *
from .user import *

"""
Data models for accessibility service.
"""


__all__ = [
    # Accessibility models
    "AccessibilityRequest",
    "AccessibilityResponse",
    "AccessibilityAnalysis",
    "AccessibilityRecommendation",
    # User models
    "User",
    "UserProfile",
    "UserPreferences",
    # Analysis models
    "VisualAnalysis",
    "AudioAnalysis",
    "MotorAnalysis",
    "CognitiveAnalysis",
    # Response models
    "ServiceResponse",
    "ErrorResponse",
    "SuccessResponse",
]
