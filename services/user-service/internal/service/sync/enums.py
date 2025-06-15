"""
同步服务枚举定义
"""
from enum import Enum


class SyncDirection(str, Enum):
    """同步方向枚举"""
    LOCAL_TO_REMOTE = "local_to_remote"  # 本地到远程
    REMOTE_TO_LOCAL = "remote_to_local"  # 远程到本地
    BIDIRECTIONAL = "bidirectional"      # 双向同步


class EntityType(str, Enum):
    """实体类型枚举"""
    USER = "user"
    HEALTH_SUMMARY = "health_summary"
    DEVICE = "device"


class ConflictResolutionStrategy(str, Enum):
    """冲突解决策略枚举"""
    LOCAL_WINS = "local_wins"    # 本地数据优先
    REMOTE_WINS = "remote_wins"  # 远程数据优先
    NEWEST_WINS = "newest_wins"  # 最新修改优先
    MANUAL = "manual"            # 手动解决


class OperationType(str, Enum):
    """操作类型枚举"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete" 