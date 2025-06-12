"""
望诊服务集成模块

提供与望诊服务的集成功能，包括：
- 面部识别和分析
- 舌诊图像分析
- 体态评估
- 皮肤状态检测
"""

from .client import LookServiceClient
from .models import LookRequest, LookResponse

__all__ = ["LookServiceClient", "LookRequest", "LookResponse"]
