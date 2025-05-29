"""
Platform Adapters for Third-party Health Platforms
"""

from .adapter_factory import AdapterFactory
from .alipay import AlipayAdapter
from .apple_health import AppleHealthAdapter
from .base import AdapterError, AuthenticationError, BaseAdapter, DataSyncError
from .fitbit import FitbitAdapter
from .google_fit import GoogleFitAdapter
from .huawei import HuaweiAdapter
from .wechat import WeChatAdapter
from .xiaomi import XiaomiAdapter

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
