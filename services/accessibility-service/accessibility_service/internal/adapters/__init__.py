"""
Platform Adapters for Third-party Health Platforms
"""

from .base import BaseAdapter, AdapterError, AuthenticationError, DataSyncError
from .apple_health import AppleHealthAdapter
from .google_fit import GoogleFitAdapter
from .fitbit import FitbitAdapter
from .xiaomi import XiaomiAdapter
from .huawei import HuaweiAdapter
from .wechat import WeChatAdapter
from .alipay import AlipayAdapter
from .adapter_factory import AdapterFactory

__all__ = [
    "BaseAdapter",
    "AdapterError",
    "AuthenticationError", 
    "DataSyncError",
    "AppleHealthAdapter",
    "GoogleFitAdapter",
    "FitbitAdapter",
    "XiaomiAdapter",
    "HuaweiAdapter",
    "WeChatAdapter",
    "AlipayAdapter",
    "AdapterFactory",
] 