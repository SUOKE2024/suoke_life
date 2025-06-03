"""
数据模型定义

定义区块链服务相关的数据库模型。
"""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum as PyEnum

from sqlalchemy import (
    Column, String, Integer, DateTime, Boolean, Text, JSON, 
    ForeignKey, Index, BigInteger, LargeBinary, Enum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

class TransactionStatus(PyEnum):
    """交易状态枚举"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class DataType(PyEnum):
    """健康数据类型枚举"""
    HEART_RATE = "heart_rate"
    BLOOD_PRESSURE = "blood_pressure"
    WEIGHT = "weight"
    TEMPERATURE = "temperature"
    DIAGNOSIS = "diagnosis"
    PRESCRIPTION = "prescription"
    LAB_RESULT = "lab_result"
    IMAGING = "imaging"
    COMPREHENSIVE = "comprehensive"

class AccessLevel(PyEnum):
    """访问级别枚举"""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    EMERGENCY = "emergency"

class BlockchainTransaction(Base):
    """区块链交易记录"""
    __tablename__ = "blockchain_transactions"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    transaction_hash = Column(String(66), unique=True, index=True)
    block_number = Column(BigInteger, index=True)
    block_hash = Column(String(66), index=True)
    contract_address = Column(String(42))
    function_name = Column(String(100))
    gas_used = Column(BigInteger)
    gas_price = Column(BigInteger)
    transaction_fee = Column(BigInteger)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING, index=True)
    data_hash = Column(String(64), index=True)
    tx_metadata = Column(JSON)
    created_at = Column(DateTime, default=func.now(), index=True)
    confirmed_at = Column(DateTime)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关系
    health_records = relationship("HealthDataRecord", back_populates="transaction")
    access_grants = relationship("AccessGrant", back_populates="transaction")

    __table_args__ = (
        Index('idx_user_status', 'user_id', 'status'),
        Index('idx_created_status', 'created_at', 'status'),
    )

class HealthDataRecord(Base):
    """健康数据记录"""
    __tablename__ = "health_data_records"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    transaction_id = Column(String(36), ForeignKey("blockchain_transactions.id"), index=True)
    data_type = Column(Enum(DataType), nullable=False, index=True)
    data_hash = Column(String(64), nullable=False, unique=True, index=True)
    encrypted_data = Column(LargeBinary)
    encryption_key_hash = Column(String(64))
    ipfs_hash = Column(String(100))
    zkp_proof = Column(JSON)
    public_inputs = Column(JSON)
    verification_key = Column(JSON)
    record_metadata = Column(JSON)
    created_at = Column(DateTime, default=func.now(), index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关系
    transaction = relationship("BlockchainTransaction", back_populates="health_records")
    access_grants = relationship("AccessGrant", back_populates="health_record")

    __table_args__ = (
        Index('idx_user_type', 'user_id', 'data_type'),
        Index('idx_user_created', 'user_id', 'created_at'),
    )

class AccessGrant(Base):
    """访问授权记录"""
    __tablename__ = "access_grants"

    id = Column(String(36), primary_key=True)
    owner_id = Column(String(36), nullable=False, index=True)
    grantee_id = Column(String(36), nullable=False, index=True)
    health_record_id = Column(String(36), ForeignKey("health_data_records.id"), index=True)
    transaction_id = Column(String(36), ForeignKey("blockchain_transactions.id"), index=True)
    access_level = Column(Enum(AccessLevel), nullable=False)
    permissions = Column(JSON)  # 详细权限配置
    granted_at = Column(DateTime, default=func.now(), index=True)
    expires_at = Column(DateTime, index=True)
    revoked_at = Column(DateTime)
    revocation_reason = Column(Text)
    is_active = Column(Boolean, default=True, index=True)
    grant_metadata = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关系
    health_record = relationship("HealthDataRecord", back_populates="access_grants")
    transaction = relationship("BlockchainTransaction", back_populates="access_grants")

    __table_args__ = (
        Index('idx_owner_grantee', 'owner_id', 'grantee_id'),
        Index('idx_grantee_active', 'grantee_id', 'is_active'),
        Index('idx_expires_active', 'expires_at', 'is_active'),
    )

class SmartContract(Base):
    """智能合约记录"""
    __tablename__ = "smart_contracts"

    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    contract_address = Column(String(42), unique=True, nullable=False, index=True)
    abi = Column(JSON, nullable=False)
    bytecode = Column(Text)
    deployment_transaction = Column(String(66))
    deployment_block = Column(BigInteger)
    version = Column(String(20))
    is_active = Column(Boolean, default=True, index=True)
    contract_metadata = Column(JSON)
    deployed_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class ZKProofRegistry(Base):
    """零知识证明注册表"""
    __tablename__ = "zk_proof_registry"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    data_hash = Column(String(64), nullable=False, unique=True, index=True)
    proof_type = Column(String(50), nullable=False)
    proof_data = Column(JSON, nullable=False)
    public_inputs = Column(JSON)
    verification_key = Column(JSON)
    circuit_id = Column(String(100))
    is_verified = Column(Boolean, default=False, index=True)
    verified_at = Column(DateTime)
    verification_transaction = Column(String(66))
    proof_metadata = Column(JSON)
    created_at = Column(DateTime, default=func.now(), index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_user_type', 'user_id', 'proof_type'),
        Index('idx_verified_created', 'is_verified', 'created_at'),
    )

class BlockchainNode(Base):
    """区块链节点状态"""
    __tablename__ = "blockchain_nodes"

    id = Column(String(36), primary_key=True)
    node_url = Column(String(255), nullable=False, unique=True)
    chain_id = Column(Integer, nullable=False)
    network_name = Column(String(50))
    is_active = Column(Boolean, default=True, index=True)
    last_block_number = Column(BigInteger)
    last_sync_at = Column(DateTime)
    sync_status = Column(String(20))  # syncing, synced, error
    latency_ms = Column(Integer)
    error_count = Column(Integer, default=0)
    node_metadata = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class AuditLog(Base):
    """审计日志"""
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), index=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), index=True)
    resource_id = Column(String(36), index=True)
    old_values = Column(JSON)
    new_values = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    success = Column(Boolean, default=True, index=True)
    error_message = Column(Text)
    audit_metadata = Column(JSON)
    created_at = Column(DateTime, default=func.now(), index=True)

    __table_args__ = (
        Index('idx_user_action', 'user_id', 'action'),
        Index('idx_resource', 'resource_type', 'resource_id'),
        Index('idx_created_success', 'created_at', 'success'),
    ) 