"""
索克生活统一支持服务

整合人工审核服务和无障碍服务，提供统一的支持功能接口。
"""

from unified_support_service.human_review import HumanReviewService
from unified_support_service.accessibility import AccessibilityService
from unified_support_service.common.service_manager import UnifiedSupportService

__version__ = "1.0.0"
__author__ = "Suoke Life Team"

__all__ = [
    "HumanReviewService",
    "AccessibilityService", 
    "UnifiedSupportService"
]
