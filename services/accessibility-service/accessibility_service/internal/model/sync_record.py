"""
同步记录模型

用于跟踪数据同步状态和记录
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from .base import BaseDBModel


class SyncStatus(Enum):
    """同步状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class SyncRecord(BaseDBModel):
    """同步记录模型"""
    sync_id: str
    user_id: str
    source_platform: str
    target_platform: str
    data_type: str
    status: SyncStatus = SyncStatus.PENDING

    # 同步详情
    total_records: int = 0
    synced_records: int = 0
    failed_records: int = 0

    # 时间信息
    started_at: datetime | None = None
    completed_at: datetime | None = None

    # 错误信息
    error_message: str | None = None
    error_details: dict[str, Any] | None = field(default_factory=dict)

    # 同步配置
    sync_config: dict[str, Any] | None = field(default_factory=dict)

    def start_sync(self):
        """开始同步"""
        self.status = SyncStatus.IN_PROGRESS
        self.started_at = datetime.now()
        self.update_timestamp()

    def complete_sync(self, success: bool = True):
        """完成同步"""
        self.status = SyncStatus.SUCCESS if success else SyncStatus.FAILED
        self.completed_at = datetime.now()
        self.update_timestamp()

    def update_progress(self, synced: int, failed: int = 0):
        """更新同步进度"""
        self.synced_records = synced
        self.failed_records = failed
        self.update_timestamp()

    def set_error(self, message: str, details: dict[str, Any] | None = None):
        """设置错误信息"""
        self.status = SyncStatus.FAILED
        self.error_message = message
        if details:
            self.error_details = details
        self.completed_at = datetime.now()
        self.update_timestamp()

    @property
    def progress_percentage(self) -> float:
        """计算同步进度百分比"""
        if self.total_records == 0:
            return 0.0
        return (self.synced_records / self.total_records) * 100

    @property
    def is_completed(self) -> bool:
        """检查是否已完成"""
        return self.status in [SyncStatus.SUCCESS, SyncStatus.FAILED, SyncStatus.CANCELLED]

    @property
    def duration_seconds(self) -> float | None:
        """计算同步持续时间（秒）"""
        if not self.started_at:
            return None

        end_time = self.completed_at or datetime.now()
        return (end_time - self.started_at).total_seconds()
