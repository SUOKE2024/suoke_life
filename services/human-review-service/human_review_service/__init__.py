"""
索克生活人工审核微服务
Suoke Life Human Review Service

一个专门用于医疗健康建议审核的独立微服务，确保AI生成的医疗建议的安全性、准确性和合规性。
"""

__version__ = "1.0.0"
__author__ = "Suoke Life Team"
__email__ = "dev@suokelife.com"
__description__ = "索克生活人工审核微服务 - 确保医疗健康建议的安全性和准确性"

from .core.models import ReviewTask, Reviewer, ReviewStatus, ReviewPriority, ReviewType
from .core.service import HumanReviewService
from .api.main import create_app

__all__ = [
    "ReviewTask",
    "Reviewer", 
    "ReviewStatus",
    "ReviewPriority",
    "ReviewType",
    "HumanReviewService",
    "create_app",
] 