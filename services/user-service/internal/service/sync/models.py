"""
同步服务数据模型
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from .enums import EntityType, SyncDirection, OperationType


class SyncConflict:
    """数据同步冲突记录"""
    
    def __init__(self, entity_type: EntityType, entity_id: str, 
                field: str, local_value: Any, remote_value: Any,
                local_updated_at: Optional[datetime] = None,
                remote_updated_at: Optional[datetime] = None):
        """
        初始化同步冲突
        
        Args:
            entity_type: 实体类型
            entity_id: 实体ID
            field: 冲突字段
            local_value: 本地值
            remote_value: 远程值
            local_updated_at: 本地更新时间
            remote_updated_at: 远程更新时间
        """
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.field = field
        self.local_value = local_value
        self.remote_value = remote_value
        self.local_updated_at = local_updated_at
        self.remote_updated_at = remote_updated_at
        self.resolution = None  # 'local', 'remote', 'merged'
        self.merged_value = None


class SyncResult:
    """同步结果"""
    
    def __init__(self, success: bool, entity_type: EntityType, 
                entity_id: str, direction: SyncDirection):
        """
        初始化同步结果
        
        Args:
            success: 是否成功
            entity_type: 实体类型
            entity_id: 实体ID
            direction: 同步方向
        """
        self.success = success
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.direction = direction
        self.conflicts: List[SyncConflict] = []
        self.error_message: Optional[str] = None
        self.timestamp = datetime.utcnow()


class SyncMetadata:
    """同步元数据"""
    
    def __init__(self, entity_type: EntityType, entity_id: str):
        """
        初始化同步元数据
        
        Args:
            entity_type: 实体类型
            entity_id: 实体ID
        """
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.last_sync_time = datetime.utcnow()
        self.local_hash: Optional[str] = None
        self.remote_hash: Optional[str] = None
        self.sync_status = "synced"  # synced, pending, conflict


class OfflineOperation:
    """离线操作记录"""
    
    def __init__(self, 
                operation_id: str,
                operation_type: OperationType,
                entity_type: EntityType,
                entity_id: str,
                data: Dict[str, Any],
                timestamp: datetime = None):
        """
        初始化离线操作
        
        Args:
            operation_id: 操作ID
            operation_type: 操作类型
            entity_type: 实体类型
            entity_id: 实体ID
            data: 操作数据
            timestamp: 操作时间戳
        """
        self.operation_id = operation_id
        self.operation_type = operation_type
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.data = data
        self.timestamp = timestamp or datetime.utcnow()
        self.synced = False
        self.retry_count = 0
        self.last_error: Optional[str] = None