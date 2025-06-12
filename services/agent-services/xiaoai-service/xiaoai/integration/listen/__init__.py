"""
闻诊服务集成模块

提供与闻诊服务的集成功能，包括：
- 语音分析和识别
- 呼吸音检测
- 心音分析
- 咳嗽识别
"""

from .client import ListenServiceClient
from .models import ListenRequest, ListenResponse

__all__ = [
    "ListenServiceClient",
    "ListenRequest",
    "ListenResponse"
]