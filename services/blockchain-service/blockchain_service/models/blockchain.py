"""
区块链相关模型

定义区块链交易和合约事件的数据库模型。
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, BigInteger, Boolean, Enum, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class TransactionStatus(PyEnum):
    """交易状态枚举"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    REVERTED = "reverted"


class ContractType(PyEnum):
    """合约类型枚举"""
    HEALTH_DATA_STORAGE = "health_data_storage"
    ZKP_VERIFIER = "zkp_verifier"
    ACCESS_CONTROL = "access_control"


class BlockchainTransaction(Base):
    """区块链交易记录"""

    __tablename__ = "blockchain_transactions"

    # 主键
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        comment="交易记录ID"
    )

    # 交易基本信息
    transaction_hash: Mapped[str] = mapped_column(
        String(66),  # 0x + 64 hex chars
        unique=True,
        nullable=False,
        comment="交易哈希"
    )

    block_number: Mapped[int | None] = mapped_column(
        BigInteger,
        comment="区块号"
    )

    block_hash: Mapped[str | None] = mapped_column(
        String(66),
        comment="区块哈希"
    )

    # 交易详情
    from_address: Mapped[str] = mapped_column(
        String(42),  # 0x + 40 hex chars
        nullable=False,
        comment="发送地址"
    )

    to_address: Mapped[str | None] = mapped_column(
        String(42),
        comment="接收地址"
    )

    contract_address: Mapped[str | None] = mapped_column(
        String(42),
        comment="合约地址"
    )

    # Gas 信息
    gas_limit: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="Gas限制"
    )

    gas_used: Mapped[int | None] = mapped_column(
        BigInteger,
        comment="已使用Gas"
    )

    gas_price: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="Gas价格"
    )

    # 交易状态
    status: Mapped[TransactionStatus] = mapped_column(
        Enum(TransactionStatus),
        default=TransactionStatus.PENDING,
        comment="交易状态"
    )

    # 业务信息
    user_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        comment="关联用户ID"
    )

    data_record_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        comment="关联数据记录ID"
    )

    operation_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="操作类型"
    )

    # 交易数据
    input_data: Mapped[str | None] = mapped_column(
        Text,
        comment="输入数据"
    )

    # 确认信息
    confirmation_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="确认次数"
    )

    confirmed_at: Mapped[datetime | None] = mapped_column(
        comment="确认时间"
    )

    # 错误信息
    error_message: Mapped[str | None] = mapped_column(
        Text,
        comment="错误信息"
    )

    # 元数据
    transaction_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        comment="交易元数据"
    )


class ContractEvent(Base):
    """智能合约事件"""

    __tablename__ = "contract_events"

    # 主键
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        comment="事件ID"
    )

    # 事件基本信息
    transaction_hash: Mapped[str] = mapped_column(
        String(66),
        nullable=False,
        comment="交易哈希"
    )

    block_number: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="区块号"
    )

    log_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="日志索引"
    )

    # 合约信息
    contract_address: Mapped[str] = mapped_column(
        String(42),
        nullable=False,
        comment="合约地址"
    )

    contract_type: Mapped[ContractType] = mapped_column(
        Enum(ContractType),
        nullable=False,
        comment="合约类型"
    )

    # 事件详情
    event_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="事件名称"
    )

    event_signature: Mapped[str] = mapped_column(
        String(66),
        nullable=False,
        comment="事件签名"
    )

    # 事件数据
    event_data: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        comment="事件数据"
    )

    # 业务关联
    user_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        comment="关联用户ID"
    )

    data_record_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        comment="关联数据记录ID"
    )

    # 处理状态
    is_processed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="是否已处理"
    )

    processed_at: Mapped[datetime | None] = mapped_column(
        comment="处理时间"
    )

    # 元数据
    event_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        comment="事件元数据"
    )
