#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据库模型定义 - 优化版
支持SQLite和PostgreSQL
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import sqlite, postgresql
from sqlalchemy.types import TypeDecorator, String, Text
import json

Base = declarative_base()


class JSONType(TypeDecorator):
    """跨数据库的JSON类型"""
    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(postgresql.JSONB())
        else:
            return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if value is not None:
            if dialect.name == 'postgresql':
                return value
            else:
                return json.dumps(value, ensure_ascii=False)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            if dialect.name == 'postgresql':
                return value
            else:
                return json.loads(value)
        return value


class UUIDType(TypeDecorator):
    """跨数据库的UUID类型"""
    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(postgresql.UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is not None:
            if dialect.name == 'postgresql':
                return value
            else:
                return str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            if dialect.name == 'postgresql':
                return value
            else:
                return uuid.UUID(value)
        return value


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = sa.Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    external_id = sa.Column(sa.String(255), unique=True, nullable=False, index=True)
    email = sa.Column(sa.String(255), unique=True, nullable=True, index=True)
    phone = sa.Column(sa.String(20), unique=True, nullable=True, index=True)
    status = sa.Column(sa.String(20), nullable=False, default="active", index=True)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_active_at = sa.Column(sa.DateTime, nullable=True, index=True)
    
    # 索引
    __table_args__ = (
        sa.Index("idx_users_status_created", status, created_at),
        sa.Index("idx_users_last_active", last_active_at),
        sa.CheckConstraint("status IN ('active', 'inactive', 'suspended')", name="check_user_status"),
    )
    
    # 关系
    health_data = sa.orm.relationship("HealthDataRecord", back_populates="user", cascade="all, delete-orphan")
    tcm_constitutions = sa.orm.relationship("TCMConstitution", back_populates="user", cascade="all, delete-orphan")
    health_insights = sa.orm.relationship("HealthInsight", back_populates="user", cascade="all, delete-orphan")
    health_profiles = sa.orm.relationship("HealthProfile", back_populates="user", cascade="all, delete-orphan")


class HealthDataRecord(Base):
    """健康数据记录表"""
    __tablename__ = "health_data_records"
    
    id = sa.Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    user_id = sa.Column(UUIDType(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    data_type = sa.Column(sa.String(50), nullable=False, index=True)
    timestamp = sa.Column(sa.DateTime, nullable=False, index=True)
    device_type = sa.Column(sa.String(50), nullable=False, index=True)
    device_id = sa.Column(sa.String(100), nullable=True, index=True)
    value = sa.Column(JSONType, nullable=False)  # 存储数值或JSON数据
    unit = sa.Column(sa.String(20), nullable=False)
    source = sa.Column(sa.String(50), nullable=False, index=True)
    metadata = sa.Column(JSONType, default={})
    quality_score = sa.Column(sa.Float, nullable=True, index=True)  # 数据质量评分
    is_validated = sa.Column(sa.Boolean, default=False, nullable=False, index=True)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 复合索引优化查询性能
    __table_args__ = (
        sa.Index("idx_health_data_user_type_time", user_id, data_type, timestamp.desc()),
        sa.Index("idx_health_data_user_time", user_id, timestamp.desc()),
        sa.Index("idx_health_data_type_time", data_type, timestamp.desc()),
        sa.Index("idx_health_data_device_time", device_type, timestamp.desc()),
        sa.Index("idx_health_data_source_time", source, timestamp.desc()),
        sa.Index("idx_health_data_quality", quality_score.desc()),
        sa.Index("idx_health_data_validated", is_validated, timestamp.desc()),
        sa.CheckConstraint("quality_score >= 0 AND quality_score <= 1", name="check_quality_score"),
    )
    
    # 关系
    user = sa.orm.relationship("User", back_populates="health_data")


class TCMConstitution(Base):
    """中医体质数据表"""
    __tablename__ = "tcm_constitutions"
    
    id = sa.Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    user_id = sa.Column(UUIDType(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = sa.Column(sa.DateTime, nullable=False, index=True)
    primary_type = sa.Column(sa.String(50), nullable=False, index=True)
    secondary_types = sa.Column(JSONType, default=[])
    scores = sa.Column(JSONType, nullable=False)  # 各体质的得分
    analysis_basis = sa.Column(JSONType, nullable=False)  # 分析依据
    recommendations = sa.Column(JSONType, nullable=False)  # 调理建议
    confidence_score = sa.Column(sa.Float, nullable=False, index=True)  # 分析置信度
    created_by = sa.Column(sa.String(50), nullable=False, index=True)  # "ai", "tcm_doctor", "self_assessment"
    version = sa.Column(sa.String(20), nullable=False, default="1.0")  # 分析模型版本
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 索引
    __table_args__ = (
        sa.Index("idx_tcm_constitution_user_time", user_id, timestamp.desc()),
        sa.Index("idx_tcm_constitution_type_time", primary_type, timestamp.desc()),
        sa.Index("idx_tcm_constitution_confidence", confidence_score.desc()),
        sa.Index("idx_tcm_constitution_created_by", created_by, timestamp.desc()),
        sa.CheckConstraint("confidence_score >= 0 AND confidence_score <= 1", name="check_confidence_score"),
        sa.CheckConstraint("created_by IN ('ai', 'tcm_doctor', 'self_assessment')", name="check_created_by"),
    )
    
    # 关系
    user = sa.orm.relationship("User", back_populates="tcm_constitutions")


class HealthInsight(Base):
    """健康洞察表"""
    __tablename__ = "health_insights"
    
    id = sa.Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    user_id = sa.Column(UUIDType(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = sa.Column(sa.DateTime, nullable=False, index=True)
    insight_type = sa.Column(sa.String(50), nullable=False, index=True)  # "trend", "anomaly", "correlation", "recommendation"
    data_type = sa.Column(sa.String(50), nullable=False, index=True)  # 对应HealthDataType
    time_range = sa.Column(JSONType, nullable=False)  # {"start": timestamp, "end": timestamp}
    title = sa.Column(sa.String(200), nullable=False)  # 洞察标题
    description = sa.Column(sa.Text, nullable=False)
    details = sa.Column(JSONType, nullable=False)
    severity = sa.Column(sa.String(20), nullable=False, default="info", index=True)  # "info", "warning", "alert", "critical"
    relevance_score = sa.Column(sa.Float, nullable=False, index=True)  # 相关性/重要性分数
    is_read = sa.Column(sa.Boolean, default=False, nullable=False, index=True)
    is_archived = sa.Column(sa.Boolean, default=False, nullable=False, index=True)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # 索引
    __table_args__ = (
        sa.Index("idx_health_insight_user_time", user_id, timestamp.desc()),
        sa.Index("idx_health_insight_type_severity", insight_type, severity, timestamp.desc()),
        sa.Index("idx_health_insight_relevance", relevance_score.desc()),
        sa.Index("idx_health_insight_unread", user_id, is_read, timestamp.desc()),
        sa.Index("idx_health_insight_active", user_id, is_archived, timestamp.desc()),
        sa.CheckConstraint("severity IN ('info', 'warning', 'alert', 'critical')", name="check_severity"),
        sa.CheckConstraint("relevance_score >= 0 AND relevance_score <= 1", name="check_relevance_score"),
    )
    
    # 关系
    user = sa.orm.relationship("User", back_populates="health_insights")


class HealthProfile(Base):
    """用户健康档案表"""
    __tablename__ = "health_profiles"
    
    id = sa.Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    user_id = sa.Column(UUIDType(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = sa.Column(sa.DateTime, nullable=False, index=True)
    health_index = sa.Column(sa.Float, nullable=False, index=True)  # 综合健康指数
    metrics = sa.Column(JSONType, nullable=False)  # 各项指标评分
    tcm_constitution = sa.Column(JSONType, nullable=False)  # 中医体质信息
    recent_trends = sa.Column(JSONType, nullable=False)  # 近期趋势
    notable_insights = sa.Column(JSONType, nullable=False)  # 显著洞察
    recommendations = sa.Column(JSONType, nullable=False)  # 健康建议
    data_completeness = sa.Column(sa.Float, nullable=False, index=True)  # 数据完整性评分
    is_current = sa.Column(sa.Boolean, default=True, nullable=False, index=True)  # 是否为当前档案
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 索引
    __table_args__ = (
        sa.Index("idx_health_profile_user_time", user_id, timestamp.desc()),
        sa.Index("idx_health_profile_health_index", health_index.desc()),
        sa.Index("idx_health_profile_current", user_id, is_current),
        sa.Index("idx_health_profile_completeness", data_completeness.desc()),
        sa.CheckConstraint("health_index >= 0 AND health_index <= 100", name="check_health_index"),
        sa.CheckConstraint("data_completeness >= 0 AND data_completeness <= 1", name="check_data_completeness"),
    )
    
    # 关系
    user = sa.orm.relationship("User", back_populates="health_profiles")


class ConsentRecord(Base):
    """用户同意记录表"""
    __tablename__ = "consent_records"
    
    id = sa.Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    user_id = sa.Column(UUIDType(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    consent_type = sa.Column(sa.String(50), nullable=False, index=True)  # "data_collection", "data_sharing", "research"
    granted_at = sa.Column(sa.DateTime, nullable=False, index=True)
    expires_at = sa.Column(sa.DateTime, nullable=True, index=True)
    revoked_at = sa.Column(sa.DateTime, nullable=True, index=True)
    details = sa.Column(JSONType, nullable=False)
    version = sa.Column(sa.String(20), nullable=False, default="1.0")  # 同意书版本
    ip_address = sa.Column(sa.String(45), nullable=True)  # 支持IPv6
    user_agent = sa.Column(sa.String(500), nullable=True)
    is_active = sa.Column(sa.Boolean, default=True, nullable=False, index=True)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 索引
    __table_args__ = (
        sa.Index("idx_consent_user_type", user_id, consent_type),
        sa.Index("idx_consent_active", user_id, is_active, granted_at.desc()),
        sa.Index("idx_consent_expires", expires_at),
        sa.Index("idx_consent_revoked", revoked_at),
        sa.CheckConstraint("consent_type IN ('data_collection', 'data_sharing', 'research', 'marketing')", name="check_consent_type"),
    )


class DataExportRecord(Base):
    """数据导出记录表"""
    __tablename__ = "data_export_records"
    
    id = sa.Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    user_id = sa.Column(UUIDType(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    export_type = sa.Column(sa.String(50), nullable=False, index=True)  # "full", "partial", "analysis"
    format = sa.Column(sa.String(20), nullable=False, index=True)  # "json", "csv", "pdf"
    data_types = sa.Column(JSONType, nullable=False)  # 导出的数据类型列表
    time_range = sa.Column(JSONType, nullable=False)  # {"start": timestamp, "end": timestamp}
    request_ip = sa.Column(sa.String(45), nullable=True)
    request_user_agent = sa.Column(sa.String(500), nullable=True)
    file_size = sa.Column(sa.BigInteger, nullable=True, index=True)  # 文件大小(字节)
    file_path = sa.Column(sa.String(500), nullable=True)  # 文件路径
    download_count = sa.Column(sa.Integer, default=0, nullable=False)
    status = sa.Column(sa.String(20), nullable=False, default="pending", index=True)  # "pending", "processing", "complete", "failed", "expired"
    error_message = sa.Column(sa.Text, nullable=True)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False, index=True)
    completed_at = sa.Column(sa.DateTime, nullable=True, index=True)
    expires_at = sa.Column(sa.DateTime, nullable=True, index=True)
    
    # 索引
    __table_args__ = (
        sa.Index("idx_export_user_status", user_id, status, created_at.desc()),
        sa.Index("idx_export_status_created", status, created_at.desc()),
        sa.Index("idx_export_expires", expires_at),
        sa.CheckConstraint("status IN ('pending', 'processing', 'complete', 'failed', 'expired')", name="check_export_status"),
        sa.CheckConstraint("format IN ('json', 'csv', 'pdf', 'xml')", name="check_export_format"),
    )


class BlockchainRecord(Base):
    """区块链记录表"""
    __tablename__ = "blockchain_records"
    
    id = sa.Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    user_id = sa.Column(UUIDType(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    record_type = sa.Column(sa.String(50), nullable=False, index=True)  # "health_data_hash", "consent", "proof"
    data_hash = sa.Column(sa.String(128), nullable=False, index=True)  # 数据哈希
    blockchain_id = sa.Column(sa.String(128), nullable=True, index=True)  # 区块链交易ID
    blockchain_status = sa.Column(sa.String(20), nullable=False, default="pending", index=True)  # "pending", "confirmed", "failed"
    block_number = sa.Column(sa.BigInteger, nullable=True, index=True)
    gas_used = sa.Column(sa.BigInteger, nullable=True)
    details = sa.Column(JSONType, nullable=False)
    retry_count = sa.Column(sa.Integer, default=0, nullable=False)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    confirmed_at = sa.Column(sa.DateTime, nullable=True, index=True)
    
    # 索引
    __table_args__ = (
        sa.Index("idx_blockchain_user_type", user_id, record_type),
        sa.Index("idx_blockchain_hash", data_hash),
        sa.Index("idx_blockchain_status_created", blockchain_status, created_at.desc()),
        sa.Index("idx_blockchain_block", block_number),
        sa.CheckConstraint("blockchain_status IN ('pending', 'confirmed', 'failed')", name="check_blockchain_status"),
        sa.CheckConstraint("retry_count >= 0", name="check_retry_count"),
    )


class SystemMetrics(Base):
    """系统指标表"""
    __tablename__ = "system_metrics"
    
    id = sa.Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    metric_name = sa.Column(sa.String(100), nullable=False, index=True)
    metric_value = sa.Column(sa.Float, nullable=False)
    metric_unit = sa.Column(sa.String(20), nullable=True)
    tags = sa.Column(JSONType, default={})  # 标签，用于分组和过滤
    timestamp = sa.Column(sa.DateTime, nullable=False, index=True)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False)
    
    # 索引
    __table_args__ = (
        sa.Index("idx_metrics_name_time", metric_name, timestamp.desc()),
        sa.Index("idx_metrics_timestamp", timestamp.desc()),
    )


class AuditLog(Base):
    """审计日志表"""
    __tablename__ = "audit_logs"
    
    id = sa.Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    user_id = sa.Column(UUIDType(), nullable=True, index=True)  # 可能是系统操作
    action = sa.Column(sa.String(100), nullable=False, index=True)
    resource_type = sa.Column(sa.String(50), nullable=False, index=True)
    resource_id = sa.Column(sa.String(100), nullable=True, index=True)
    details = sa.Column(JSONType, nullable=False)
    ip_address = sa.Column(sa.String(45), nullable=True)
    user_agent = sa.Column(sa.String(500), nullable=True)
    timestamp = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # 索引
    __table_args__ = (
        sa.Index("idx_audit_user_time", user_id, timestamp.desc()),
        sa.Index("idx_audit_action_time", action, timestamp.desc()),
        sa.Index("idx_audit_resource", resource_type, resource_id),
        sa.Index("idx_audit_timestamp", timestamp.desc()),
    ) 