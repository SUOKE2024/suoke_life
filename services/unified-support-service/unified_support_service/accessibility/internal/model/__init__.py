from typing import Any, Dict, List, Optional, Union

"""
__init__ - 索克生活项目模块
"""

from .base import BaseModel
from .health_data import ActivityData, HealthData, HeartRateData, SleepData
from .sync_record import SyncRecord, SyncStatus
from .user_integration import PlatformAuth, UserIntegration

"""
数据模型层

定义无障碍服务的数据模型和结构：
- 用户配置模型
- 服务请求 / 响应模型
- 数据传输对象
"""

# 这里可以导入具体的模型类
# from .user_config import UserConfig
# from .service_request import ServiceRequest


__all__ = [
    # "UserConfig",
    # "ServiceRequest",
    "BaseModel",
    "UserIntegration",
    "PlatformAuth",
    "HealthData",
    "ActivityData",
    "SleepData",
    "HeartRateData",
    "SyncRecord",
    "SyncStatus",
]
