"""
__init__ - 索克生活项目模块
"""

from .disaster_recovery import DisasterRecoveryService

"""
弹性恢复模块

提供系统弹性和容错能力：
- 故障恢复
- 熔断器
- 重试机制
- 降级策略
"""


__all__ = [
    "DisasterRecoveryService"
]
