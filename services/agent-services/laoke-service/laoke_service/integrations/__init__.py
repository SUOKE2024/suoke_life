"""
老克智能体服务 - 集成模块

本模块包含与外部服务的集成功能，包括：
- 无障碍服务集成
- 第三方API集成
- 数据库集成
- 缓存集成
"""

from .accessibility import AccessibilityClient, TTSRequest, STTRequest, AccessibilityProfile

__all__ = [
    "AccessibilityClient",
    "TTSRequest", 
    "STTRequest",
    "AccessibilityProfile"
]
