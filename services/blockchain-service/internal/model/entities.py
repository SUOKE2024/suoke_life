#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据实体模型定义
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class DataType(str, Enum):
    """健康数据类型枚举"""
    INQUIRY = "inquiry"              # 问诊数据
    LISTEN = "listen"                # 闻诊数据
    LOOK = "look"                    # 望诊数据
    PALPATION = "palpation"          # 切诊数据
    VITAL_SIGNS = "vital_signs"      # 生命体征
    LABORATORY = "laboratory"        # 实验室检查
    MEDICATION = "medication"        # 用药记录
    NUTRITION = "nutrition"          # 营养记录
    ACTIVITY = "activity"            # 活动记录
    SLEEP = "sleep"                  # 睡眠记录
    SYNDROME = "syndrome"            # 证型记录
    PRESCRIPTION = "prescription"    # 处方记录
    HEALTH_PLAN = "health_plan"      # 健康计划


class AccessLevel(str, Enum):
    """数据访问级别"""
    READ = "read"                    # 只读
    WRITE = "write"                  # 读写
    FULL = "full"                    # 完全访问


class TransactionStatus(str, Enum):
    """交易状态"""
    PENDING = "pending"              # 待处理
    CONFIRMED = "confirmed"          # 已确认
    FAILED = "failed"                # 失败


class TransactionInfo(BaseModel):
    """交易信息"""
    transaction_id: str
    block_hash: Optional[str] = None
    block_number: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: TransactionStatus = TransactionStatus.PENDING
    gas_used: Optional[int] = None


class HealthDataRecord(BaseModel):
    """健康数据记录"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    data_type: DataType
    data_hash: str
    encrypted_data: Optional[bytes] = None
    metadata: Dict[str, str] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    transaction: Optional[TransactionInfo] = None


class ZkpVerification(BaseModel):
    """零知识证明验证记录"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    data_record_id: str
    user_id: str
    verifier_id: str
    circuit_type: str
    proof_hash: str
    is_valid: bool
    verification_time: datetime = Field(default_factory=datetime.utcnow)
    details: Dict[str, str] = {}


class AccessPolicy(BaseModel):
    """访问策略"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str                          # 数据所有者
    authorized_id: str                    # 被授权方
    data_types: List[DataType]            # 授权的数据类型
    access_level: AccessLevel             # 访问级别
    expiration_time: Optional[datetime] = None  # 过期时间
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    revoked: bool = False                 # 是否已撤销
    revocation_time: Optional[datetime] = None  # 撤销时间
    revocation_reason: Optional[str] = None  # 撤销原因
    policy_data: Dict[str, str] = {}      # 额外的策略数据


class BlockchainNode(BaseModel):
    """区块链节点状态"""
    node_id: str
    endpoint: str
    is_active: bool = True
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    current_block: int = 0
    sync_status: float = 0.0  # 同步百分比
    version: str = "0.1.0"
    network: str = "mainnet"
    role: str = "validator"    # validator, observer, etc.


class HealthDataCheckpoint(BaseModel):
    """健康数据检查点（用于数据完整性验证）"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    data_type: Optional[DataType] = None  # 如果为None，表示所有类型
    start_time: datetime
    end_time: datetime
    merkle_root: str            # Merkle树根哈希
    record_count: int           # 包含的记录数
    created_at: datetime = Field(default_factory=datetime.utcnow)
    transaction: Optional[TransactionInfo] = None
    metadata: Dict[str, str] = {} 