"""
问诊服务集成模块

提供与问诊服务的集成功能
"""

from .client import InquiryServiceClient
from .models import InquiryRequest, InquiryResponse

__all__ = [
    "InquiryServiceClient",
    "InquiryRequest",
    "InquiryResponse"
]