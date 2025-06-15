"""
健康数据模型

定义健康数据相关的数据库模型。
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, Boolean, Enum, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class DataType(PyEnum):
    """数据类型枚举"""
    VITAL_SIGNS = "vital_signs"
    LAB_RESULTS = "lab_results"
    MEDICAL_IMAGES = "medical_images"
    PRESCRIPTIONS = "prescriptions"
    DIAGNOSIS = "diagnosis"
    TREATMENT_PLAN = "treatment_plan"
    LIFESTYLE = "lifestyle"
    SYMPTOMS = "symptoms"


class DataStatus(PyEnum):
    """数据状态枚举"""
    PENDING = "pending"
    VERIFIED = "verified"
    STORED = "stored"
    ARCHIVED = "archived"
    DELETED = "deleted"


class HealthDataRecord(Base):
    """健康数据记录"""

    __tablename__ = "health_data_records"

    # 主键
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        comment="记录ID"
    )

    # 用户信息
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        comment="用户ID"
    )

    # 数据基本信息
    data_type: Mapped[DataType] = mapped_column(
        Enum(DataType),
        nullable=False,
        comment="数据类型"
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="数据标题"
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        comment="数据描述"
    )

    # 数据内容
    data_content: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        comment="数据内容"
    )

    # 区块链相关
    blockchain_hash: Mapped[str | None] = mapped_column(
        String(66),  # 0x + 64 hex chars
        comment="区块链哈希"
    )

    ipfs_hash: Mapped[str | None] = mapped_column(
        String(64),
        comment="IPFS哈希"
    )

    # 状态和元数据
    status: Mapped[DataStatus] = mapped_column(
        Enum(DataStatus),
        default=DataStatus.PENDING,
        comment="数据状态"
    )

    is_encrypted: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="是否加密"
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="是否已验证"
    )

    # 访问控制
    access_level: Mapped[int] = mapped_column(
        Integer,
        default=1,
        comment="访问级别"
    )

    # 元数据
    data_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        comment="元数据"
    )


class HealthDataMetadata(Base):
    """健康数据元数据"""

    __tablename__ = "health_data_metadata"

    # 主键
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        comment="元数据ID"
    )

    # 关联的数据记录
    data_record_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        comment="数据记录ID"
    )

    # 数据来源
    source_system: Mapped[str | None] = mapped_column(
        String(100),
        comment="来源系统"
    )

    source_device: Mapped[str | None] = mapped_column(
        String(100),
        comment="来源设备"
    )

    # 数据质量
    quality_score: Mapped[float | None] = mapped_column(
        comment="数据质量评分"
    )

    confidence_level: Mapped[float | None] = mapped_column(
        comment="置信度"
    )

    # 时间信息
    measurement_time: Mapped[datetime | None] = mapped_column(
        comment="测量时间"
    )

    # 地理位置
    location_data: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        comment="位置数据"
    )

    # 标签和分类
    tags: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        comment="标签"
    )

    # 隐私设置
    privacy_settings: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        comment="隐私设置"
    )
