from typing import Dict, List, Any, Optional, Union

"""
__init__ - 索克生活项目模块
"""

from .health_aggregator import HealthAggregator, ServiceHealth
from .health_checker import HealthChecker, HealthCheckResult, HealthStatus
from .health_monitor import AlertLevel, HealthAlert, HealthMonitor

"""
健康检查组件
提供微服务健康状态监控和检查功能
"""


__all__ = [
    "AlertLevel",
    "HealthAggregator",
    "HealthAlert",
    "HealthCheckResult",
    "HealthChecker",
    "HealthMonitor",
    "HealthStatus",
    "ServiceHealth",
]
