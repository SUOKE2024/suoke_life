"""
models - 索克生活项目模块
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Table, MetaData, Float, JSON, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

"""
数据库模型定义模块

该模块定义了PostgreSQL数据库的SQLAlchemy ORM模型。
"""


Base = declarative_base()
metadata = MetaData()

# 用户表
users = Table(
    'users', 
    metadata,
    Column('user_id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column('username', String(50), unique=True, nullable=False),
    Column('email', String(100), unique=True, nullable=False),
    Column('password_hash', String(255), nullable=False),
    Column('phone', String(20), nullable=True),
    Column('full_name', String(100), nullable=True),
    Column('created_at', DateTime, default=datetime.utcnow),
    Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
    Column('status', String(20), default='active'),
    Column('metadata', JSONB, default={}),
    Column('roles', JSONB, default=["user"]),
    Column('preferences', JSONB, default={}),
)

# 健康摘要表
health_summaries = Table(
    'health_summaries',
    metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.user_id'), primary_key=True),
    Column('health_score', Integer, default=60),
    Column('dominant_constitution', String(50), nullable=True),
    Column('constitution_scores', JSONB, default={}),
    Column('recent_metrics', JSONB, default=[]),
    Column('last_assessment_date', DateTime, nullable=True),
)

# 设备表
devices = Table(
    'devices',
    metadata,
    Column('binding_id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False),
    Column('device_id', String(100), nullable=False),
    Column('device_type', String(50), nullable=False),
    Column('device_name', String(100), nullable=True),
    Column('binding_time', DateTime, default=datetime.utcnow),
    Column('is_active', Boolean, default=True),
    Column('last_active_time', DateTime, default=datetime.utcnow),
    Column('device_metadata', JSONB, default={}),
)

# 用户角色关联表（多对多）
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', String, ForeignKey('users.id')),
    Column('role', String(50))
)

# 用户地址关联表（一对多）
class UserAddress(Base):
    __tablename__ = 'user_addresses'
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    province = Column(String(50), nullable=False)
    city = Column(String(50), nullable=False)
    district = Column(String(50))
    street = Column(String(200))
    postal_code = Column(String(20))
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

# 创建索引
# SQLAlchemy会自动为外键创建索引，但为了优化某些查询，可以显式创建额外的索引
Index = lambda *args, **kwargs: None  # 这里只是声明，实际创建会由SQLAlchemy处理

# 为设备ID创建索引
Index('idx_devices_device_id', devices.c.device_id)

# 创建设备ID和用户ID的联合唯一索引，确保一个设备只能绑定到一个用户
Index('idx_user_device', devices.c.user_id, devices.c.device_id, unique=True)

# ORM模型类
class User(Base):
    """用户ORM模型"""
    __table__ = users

class HealthSummary(Base):
    """健康摘要ORM模型"""
    __table__ = health_summaries

class Device(Base):
    """设备ORM模型"""
    __table__ = devices

class User(Base):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), unique=True)
    full_name = Column(String(100))
    password_hash = Column(String(128), nullable=False)
    gender = Column(String(20))
    birth_date = Column(DateTime)
    avatar_url = Column(String(200))
    status = Column(String(20), default='active', nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    last_login_at = Column(DateTime)
    preferences = Column(JSON, default={})
    metadata = Column(JSON, default={})
    settings = Column(JSON, default={})
    agent_assignments = Column(JSON, default={})
    
    # 关联
    devices = relationship("UserDevice", back_populates="user", cascade="all, delete-orphan")
    health_summary = relationship("UserHealthSummary", back_populates="user", uselist=False, cascade="all, delete-orphan")
    addresses = relationship("UserAddress", cascade="all, delete-orphan")
    audit_logs = relationship("UserAuditLog", back_populates="user", cascade="all, delete-orphan")

class UserDevice(Base):
    __tablename__ = 'user_devices'
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    device_id = Column(String(100), nullable=False)
    device_type = Column(String(50), nullable=False)
    device_name = Column(String(100))
    platform = Column(String(50))
    os_version = Column(String(50))
    app_version = Column(String(50))
    push_token = Column(String(200))
    binding_time = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    last_active_time = Column(DateTime, nullable=False)
    device_metadata = Column(JSON, default={})
    
    # 关联
    user = relationship("User", back_populates="devices")
    
    __table_args__ = (
        # 用户和设备ID的唯一约束，确保一个设备只能被一个用户绑定
        {'unique_constraint': ['user_id', 'device_id']},
    )

class UserHealthSummary(Base):
    __tablename__ = 'user_health_summaries'
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, unique=True)
    health_score = Column(Integer, default=60)
    dominant_constitution = Column(String(50))
    constitution_scores = Column(JSON, default={})
    height = Column(Float)
    weight = Column(Float)
    bmi = Column(Float)
    blood_type = Column(String(20))
    allergies = Column(JSON, default=[])
    chronic_conditions = Column(JSON, default=[])
    medications = Column(JSON, default=[])
    family_history = Column(JSON, default={})
    last_assessment_date = Column(DateTime)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    
    # 关联
    user = relationship("User", back_populates="health_summary")
    metrics = relationship("HealthMetric", back_populates="health_summary", cascade="all, delete-orphan")

class HealthMetric(Base):
    __tablename__ = 'health_metrics'
    
    id = Column(String, primary_key=True)
    health_summary_id = Column(String, ForeignKey('user_health_summaries.id'), nullable=False)
    metric_name = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(50), default='')
    timestamp = Column(DateTime, nullable=False)
    source = Column(String(100))
    confidence = Column(Float)
    created_at = Column(DateTime, nullable=False)
    
    # 关联
    health_summary = relationship("UserHealthSummary", back_populates="metrics")

class UserAuditLog(Base):
    __tablename__ = 'user_audit_logs'
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    action = Column(String(100), nullable=False) # login, update_profile, change_password, etc.
    action_time = Column(DateTime, nullable=False)
    ip_address = Column(String(50))
    user_agent = Column(String(200))
    request_id = Column(String(50))
    changes = Column(JSON, default={})
    details = Column(Text)
    metadata = Column(JSON, default={})
    
    # 关联
    user = relationship("User", back_populates="audit_logs")

class OperationLog(Base):
    __tablename__ = 'operation_logs'
    
    id = Column(String, primary_key=True)
    service = Column(String(50), nullable=False, default='user-service')
    operation = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False) # success, failure
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    duration_ms = Column(Integer)
    user_id = Column(String(100))
    request_id = Column(String(50))
    ip_address = Column(String(50))
    endpoint = Column(String(200))
    method = Column(String(20))
    request_data = Column(JSON)
    response_data = Column(JSON)
    error_message = Column(Text)
    stack_trace = Column(Text)
    metadata = Column(JSON, default={})