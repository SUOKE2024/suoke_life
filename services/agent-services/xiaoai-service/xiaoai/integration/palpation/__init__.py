"""
切诊服务集成模块
"""

from .client import PalpationServiceClient
from .models import PalpationRequest, PalpationResponse

__all__ = [
    "PalpationServiceClient",
    "PalpationRequest",
    "PalpationResponse"
]