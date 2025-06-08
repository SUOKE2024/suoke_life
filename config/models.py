#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
索克生活 - 统一数据库模型定义
Unified Database Models for Suoke Life
"""

from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, Boolean, DateTime, 
    JSON, Enum, ForeignKey, Index, UniqueConstraint, CheckConstraint,
    DECIMAL, Float, LargeBinary
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum as PyEnum
import uuid

Base = declarative_base()

# 枚举定义
class UserStatus(PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"

class ServiceStatus(PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"

class DiagnosisStatus(PyEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class HealthDataType(PyEnum):
    VITAL_SIGNS = "vital_signs"
    MEDICAL_REPORT = "medical_report"
    DIAGNOSIS_RESULT = "diagnosis_result"
    PRESCRIPTION = "prescription"

# 基础模型类
class BaseModel:
    """基础模型类"""
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(BigInteger, nullable=True)
    updated_by = Column(BigInteger, nullable=True)

# 用户相关模型
class User(Base, BaseModel):
    """用户表"""
    __tablename__ = 'users'

    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    salt = Column(String(255), nullable=False)

    # 个人信息
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    gender = Column(Enum('male', 'female', 'other', name='gender_enum'), nullable=True)
    birth_date = Column(DateTime, nullable=True)
    avatar_url = Column(String(500), nullable=True)

    # 状态信息
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    login_count = Column(Integer, default=0, nullable=False)

    # 设置信息
    timezone = Column(String(50), default='Asia/Shanghai', nullable=False)
    language = Column(String(10), default='zh-CN', nullable=False)
    preferences = Column(JSON, nullable=True)

    # 索引
    __table_args__ = (
        Index('idx_users_username', 'username'),
        Index('idx_users_email', 'email'),
        Index('idx_users_phone', 'phone'),
        Index('idx_users_status', 'status'),
        Index('idx_users_created_at', 'created_at'),
    )

class UserProfile(Base, BaseModel):
    """用户档案表"""
    __tablename__ = 'user_profiles'

    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False, unique=True)

    # 健康信息
    height = Column(Float, nullable=True)  # 身高(cm)
    weight = Column(Float, nullable=True)  # 体重(kg)
    blood_type = Column(String(10), nullable=True)  # 血型
    allergies = Column(Text, nullable=True)  # 过敏史
    medical_history = Column(Text, nullable=True)  # 病史
    family_history = Column(Text, nullable=True)  # 家族史

    # 生活习惯
    smoking_status = Column(Enum('never', 'former', 'current', name='smoking_enum'), nullable=True)
    drinking_status = Column(Enum('never', 'occasional', 'regular', name='drinking_enum'), nullable=True)
    exercise_frequency = Column(String(50), nullable=True)
    sleep_hours = Column(Float, nullable=True)

    # 中医体质
    tcm_constitution = Column(String(100), nullable=True)
    tcm_constitution_score = Column(JSON, nullable=True)

    # 关联关系
    user = relationship("User", backref="profile")

    __table_args__ = (
        Index('idx_user_profiles_user_id', 'user_id'),
    )

# 健康数据模型
class HealthRecord(Base, BaseModel):
    """健康记录表"""
    __tablename__ = 'health_records'

    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    record_type = Column(Enum(HealthDataType), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    data = Column(JSON, nullable=False)

    # 元数据
    source = Column(String(100), nullable=True)  # 数据来源
    device_id = Column(String(100), nullable=True)  # 设备ID
    measured_at = Column(DateTime, nullable=False)

    # 关联关系
    user = relationship("User", backref="health_records")

    __table_args__ = (
        Index('idx_health_records_user_id', 'user_id'),
        Index('idx_health_records_type', 'record_type'),
        Index('idx_health_records_measured_at', 'measured_at'),
    )

# 智能体相关模型
class AgentConversation(Base, BaseModel):
    """智能体对话表"""
    __tablename__ = 'agent_conversations'

    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    agent_name = Column(String(50), nullable=False)  # xiaoai, xiaoke, laoke, soer
    session_id = Column(String(100), nullable=False)

    # 对话内容
    user_message = Column(Text, nullable=False)
    agent_response = Column(Text, nullable=False)
    context = Column(JSON, nullable=True)

    # 评价信息
    user_rating = Column(Integer, nullable=True)  # 1-5星评价
    feedback = Column(Text, nullable=True)

    # 关联关系
    user = relationship("User", backref="conversations")

    __table_args__ = (
        Index('idx_conversations_user_id', 'user_id'),
        Index('idx_conversations_agent', 'agent_name'),
        Index('idx_conversations_session', 'session_id'),
        Index('idx_conversations_created_at', 'created_at'),
    )

# 诊断相关模型
class DiagnosisSession(Base, BaseModel):
    """诊断会话表"""
    __tablename__ = 'diagnosis_sessions'

    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    session_id = Column(String(100), nullable=False, unique=True)
    diagnosis_type = Column(String(50), nullable=False)  # look, listen, inquiry, palpation, calculation

    # 状态信息
    status = Column(Enum(DiagnosisStatus), default=DiagnosisStatus.PENDING, nullable=False)
    progress = Column(Float, default=0.0, nullable=False)  # 进度百分比

    # 诊断数据
    input_data = Column(JSON, nullable=True)
    result_data = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=True)

    # 时间信息
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # 关联关系
    user = relationship("User", backref="diagnosis_sessions")

    __table_args__ = (
        Index('idx_diagnosis_sessions_user_id', 'user_id'),
        Index('idx_diagnosis_sessions_type', 'diagnosis_type'),
        Index('idx_diagnosis_sessions_status', 'status'),
        Index('idx_diagnosis_sessions_session_id', 'session_id'),
    )

# 区块链相关模型
class BlockchainTransaction(Base, BaseModel):
    """区块链交易表"""
    __tablename__ = 'blockchain_transactions'

    transaction_hash = Column(String(255), nullable=False, unique=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)

    # 交易信息
    transaction_type = Column(String(50), nullable=False)
    data_hash = Column(String(255), nullable=False)
    block_number = Column(BigInteger, nullable=True)
    gas_used = Column(BigInteger, nullable=True)

    # 状态信息
    status = Column(String(20), default='pending', nullable=False)
    confirmed_at = Column(DateTime, nullable=True)

    # 关联关系
    user = relationship("User", backref="blockchain_transactions")

    __table_args__ = (
        Index('idx_blockchain_tx_hash', 'transaction_hash'),
        Index('idx_blockchain_user_id', 'user_id'),
        Index('idx_blockchain_type', 'transaction_type'),
        Index('idx_blockchain_status', 'status'),
    )

# 系统配置模型
class SystemConfig(Base, BaseModel):
    """系统配置表"""
    __tablename__ = 'system_config'

    config_key = Column(String(255), nullable=False, unique=True)
    config_value = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    config_type = Column(String(50), default='string', nullable=False)
    is_encrypted = Column(Boolean, default=False, nullable=False)

    __table_args__ = (
        Index('idx_system_config_key', 'config_key'),
    )

class ServiceRegistry(Base, BaseModel):
    """服务注册表"""
    __tablename__ = 'service_registry'

    service_name = Column(String(255), nullable=False)
    service_version = Column(String(50), nullable=False)
    service_url = Column(String(500), nullable=False)
    health_check_url = Column(String(500), nullable=True)

    # 状态信息
    status = Column(Enum(ServiceStatus), default=ServiceStatus.ACTIVE, nullable=False)
    last_health_check = Column(DateTime, nullable=True)
    metadata = Column(JSON, nullable=True)

    __table_args__ = (
        Index('idx_service_registry_name', 'service_name'),
        Index('idx_service_registry_status', 'status'),
        UniqueConstraint('service_name', 'service_version', name='uq_service_version'),
    )

# 审计日志模型
class AuditLog(Base, BaseModel):
    """审计日志表"""
    __tablename__ = 'audit_logs'

    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=True)
    service_name = Column(String(255), nullable=True)
    action = Column(String(255), nullable=False)
    resource_type = Column(String(255), nullable=True)
    resource_id = Column(String(255), nullable=True)

    # 详细信息
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # 关联关系
    user = relationship("User", backref="audit_logs")

    __table_args__ = (
        Index('idx_audit_logs_user_id', 'user_id'),
        Index('idx_audit_logs_service', 'service_name'),
        Index('idx_audit_logs_action', 'action'),
        Index('idx_audit_logs_created_at', 'created_at'),
    )

# 消息队列模型
class MessageQueue(Base, BaseModel):
    """消息队列表"""
    __tablename__ = 'message_queue'

    queue_name = Column(String(255), nullable=False)
    message_id = Column(String(100), nullable=False, unique=True)

    # 消息内容
    payload = Column(JSON, nullable=False)
    headers = Column(JSON, nullable=True)

    # 状态信息
    status = Column(String(20), default='pending', nullable=False)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)

    # 时间信息
    scheduled_at = Column(DateTime, default=func.now(), nullable=False)
    processed_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index('idx_message_queue_name', 'queue_name'),
        Index('idx_message_queue_status', 'status'),
        Index('idx_message_queue_scheduled', 'scheduled_at'),
    )

# 导出所有模型
__all__ = [
    'Base',
    'User',
    'UserProfile', 
    'HealthRecord',
    'AgentConversation',
    'DiagnosisSession',
    'BlockchainTransaction',
    'SystemConfig',
    'ServiceRegistry',
    'AuditLog',
    'MessageQueue',
    'UserStatus',
    'ServiceStatus',
    'DiagnosisStatus',
    'HealthDataType'
] 