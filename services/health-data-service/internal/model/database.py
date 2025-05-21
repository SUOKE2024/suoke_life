#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据库模型定义
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = sa.Column(sa.String, unique=True, nullable=False)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    updated_at = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    health_data = sa.orm.relationship("HealthDataRecord", back_populates="user")
    tcm_constitutions = sa.orm.relationship("TCMConstitution", back_populates="user")
    health_insights = sa.orm.relationship("HealthInsight", back_populates="user")
    health_profiles = sa.orm.relationship("HealthProfile", back_populates="user")


class HealthDataRecord(Base):
    """健康数据记录表"""
    __tablename__ = "health_data_records"
    
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False)
    data_type = sa.Column(sa.String, nullable=False)
    timestamp = sa.Column(sa.DateTime, nullable=False)
    device_type = sa.Column(sa.String, nullable=False)
    device_id = sa.Column(sa.String, nullable=True)
    value = sa.Column(JSONB, nullable=False)  # 存储数值或JSON数据
    unit = sa.Column(sa.String, nullable=False)
    source = sa.Column(sa.String, nullable=False)
    metadata = sa.Column(JSONB, default={})
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    updated_at = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 索引
    __table_args__ = (
        sa.Index("idx_health_data_user_type_time", user_id, data_type, timestamp),
        sa.Index("idx_health_data_timestamp", timestamp),
    )
    
    # 关系
    user = sa.orm.relationship("User", back_populates="health_data")


class TCMConstitution(Base):
    """中医体质数据表"""
    __tablename__ = "tcm_constitutions"
    
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False)
    timestamp = sa.Column(sa.DateTime, nullable=False)
    primary_type = sa.Column(sa.String, nullable=False)
    secondary_types = sa.Column(JSONB, default=[])
    scores = sa.Column(JSONB, nullable=False)  # 各体质的得分
    analysis_basis = sa.Column(JSONB, nullable=False)  # 分析依据
    recommendations = sa.Column(JSONB, nullable=False)  # 调理建议
    created_by = sa.Column(sa.String, nullable=False)  # "ai", "tcm_doctor", "self_assessment"
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    updated_at = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 索引
    __table_args__ = (
        sa.Index("idx_tcm_constitution_user_time", user_id, timestamp),
    )
    
    # 关系
    user = sa.orm.relationship("User", back_populates="tcm_constitutions")


class HealthInsight(Base):
    """健康洞察表"""
    __tablename__ = "health_insights"
    
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False)
    timestamp = sa.Column(sa.DateTime, nullable=False)
    insight_type = sa.Column(sa.String, nullable=False)  # "trend", "anomaly", "correlation", "recommendation"
    data_type = sa.Column(sa.String, nullable=False)  # 对应HealthDataType
    time_range = sa.Column(JSONB, nullable=False)  # {"start": timestamp, "end": timestamp}
    description = sa.Column(sa.Text, nullable=False)
    details = sa.Column(JSONB, nullable=False)
    severity = sa.Column(sa.String, nullable=True)  # "info", "warning", "alert"
    relevance_score = sa.Column(sa.Float, nullable=False)  # 相关性/重要性分数
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    
    # 索引
    __table_args__ = (
        sa.Index("idx_health_insight_user_time", user_id, timestamp),
        sa.Index("idx_health_insight_type_severity", insight_type, severity),
    )
    
    # 关系
    user = sa.orm.relationship("User", back_populates="health_insights")


class HealthProfile(Base):
    """用户健康档案表"""
    __tablename__ = "health_profiles"
    
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False)
    timestamp = sa.Column(sa.DateTime, nullable=False)
    health_index = sa.Column(sa.Float, nullable=False)  # 综合健康指数
    metrics = sa.Column(JSONB, nullable=False)  # 各项指标评分
    tcm_constitution = sa.Column(JSONB, nullable=False)  # 中医体质信息
    recent_trends = sa.Column(JSONB, nullable=False)  # 近期趋势
    notable_insights = sa.Column(JSONB, nullable=False)  # 显著洞察
    recommendations = sa.Column(JSONB, nullable=False)  # 健康建议
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    updated_at = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 索引
    __table_args__ = (
        sa.Index("idx_health_profile_user_time", user_id, timestamp),
    )
    
    # 关系
    user = sa.orm.relationship("User", back_populates="health_profiles")


class ConsentRecord(Base):
    """用户同意记录表"""
    __tablename__ = "consent_records"
    
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False)
    consent_type = sa.Column(sa.String, nullable=False)  # "data_collection", "data_sharing", "research"
    granted_at = sa.Column(sa.DateTime, nullable=False)
    expires_at = sa.Column(sa.DateTime, nullable=True)
    revoked_at = sa.Column(sa.DateTime, nullable=True)
    details = sa.Column(JSONB, nullable=False)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    updated_at = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 索引
    __table_args__ = (
        sa.Index("idx_consent_user_type", user_id, consent_type),
    )


class DataExportRecord(Base):
    """数据导出记录表"""
    __tablename__ = "data_export_records"
    
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False)
    export_type = sa.Column(sa.String, nullable=False)  # "full", "partial", "analysis"
    format = sa.Column(sa.String, nullable=False)  # "json", "csv", "pdf"
    data_types = sa.Column(JSONB, nullable=False)  # 导出的数据类型列表
    time_range = sa.Column(JSONB, nullable=False)  # {"start": timestamp, "end": timestamp}
    request_ip = sa.Column(sa.String, nullable=True)
    request_user_agent = sa.Column(sa.String, nullable=True)
    file_size = sa.Column(sa.Integer, nullable=True)  # 文件大小(字节)
    status = sa.Column(sa.String, nullable=False)  # "pending", "complete", "failed"
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    completed_at = sa.Column(sa.DateTime, nullable=True)


class BlockchainRecord(Base):
    """区块链记录表"""
    __tablename__ = "blockchain_records"
    
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = sa.Column(UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False)
    record_type = sa.Column(sa.String, nullable=False)  # "health_data_hash", "consent", "proof"
    data_hash = sa.Column(sa.String, nullable=False)  # 数据哈希
    blockchain_id = sa.Column(sa.String, nullable=True)  # 区块链交易ID
    blockchain_status = sa.Column(sa.String, nullable=False)  # "pending", "confirmed", "failed"
    details = sa.Column(JSONB, nullable=False)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    updated_at = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 索引
    __table_args__ = (
        sa.Index("idx_blockchain_user_type", user_id, record_type),
        sa.Index("idx_blockchain_hash", data_hash),
    ) 