from typing import Dict, List, Any, Optional, Union

"""
__init__ - 索克生活项目模块
"""

from .delivery.grpc_server import AccessibilityServicer
from .service.app import AccessibilityApp, AccessibilityService

"""
内部模块包

包含无障碍服务的核心实现：
- delivery: API交付层
- service: 业务逻辑层
- model: 数据模型层
- repository: 数据访问层
- integration: 集成适配层
- platform: 平台适配层
- observability: 可观测性
- security: 安全模块
- resilience: 弹性恢复
"""

# 导出核心组件

__all__ = [
    "AccessibilityService",
    "AccessibilityApp",
    "AccessibilityServicer"
]
