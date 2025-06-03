"""
数据模型测试模块

测试SQLAlchemy数据模型的定义和关系。
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from suoke_blockchain_service.models import (
    Base, BlockchainTransaction, HealthDataRecord, AccessGrant,
    ZKProofRegistry, SmartContract, BlockchainNode, AuditLog,
    TransactionStatus, DataType, AccessLevel
)


class TestModels:
    """数据模型测试类"""

    @pytest.fixture(scope="class")
    def engine(self):
        """创建内存数据库引擎"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        return engine

    @pytest.fixture
    def session(self, engine):
        """创建数据库会话"""
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()

    def test_blockchain_transaction_model(self, session):
        """测试区块链交易模型"""
        transaction = BlockchainTransaction(
            id="tx-123",
            user_id="user-456",
            status=TransactionStatus.PENDING,
            data_hash="hash123",
            gas_limit=100000,
            gas_price=20000000000,
            tx_metadata={"test": "data"}
        )
        
        session.add(transaction)
        session.commit()
        
        # 查询验证
        retrieved = session.query(BlockchainTransaction).filter_by(id="tx-123").first()
        assert retrieved is not None
        assert retrieved.user_id == "user-456"
        assert retrieved.status == TransactionStatus.PENDING
        assert retrieved.data_hash == "hash123"
        assert retrieved.tx_metadata["test"] == "data"

    def test_health_data_record_model(self, session):
        """测试健康数据记录模型"""
        # 先创建交易
        transaction = BlockchainTransaction(
            id="tx-123",
            user_id="user-456",
            status=TransactionStatus.CONFIRMED,
            data_hash="hash123"
        )
        session.add(transaction)
        
        # 创建健康数据记录
        health_record = HealthDataRecord(
            id="record-123",
            user_id="user-456",
            transaction_id="tx-123",
            data_type=DataType.heart_rate,
            data_hash="hash123",
            encrypted_data=b"encrypted_data",
            encryption_key_hash="key_hash",
            ipfs_hash="QmTest",
            zkp_proof={"proof": {"a": [1, 2]}},
            public_inputs=[1, 2, 3],
            verification_key={"alpha": [1, 2]},
            record_metadata={"original_size": 100}
        )
        
        session.add(health_record)
        session.commit()
        
        # 查询验证
        retrieved = session.query(HealthDataRecord).filter_by(id="record-123").first()
        assert retrieved is not None
        assert retrieved.user_id == "user-456"
        assert retrieved.data_type == DataType.heart_rate
        assert retrieved.encrypted_data == b"encrypted_data"
        assert retrieved.zkp_proof["proof"]["a"] == [1, 2]
        assert retrieved.transaction.id == "tx-123"

    def test_access_grant_model(self, session):
        """测试访问授权模型"""
        # 先创建健康数据记录
        transaction = BlockchainTransaction(
            id="tx-123",
            user_id="user-456",
            status=TransactionStatus.CONFIRMED,
            data_hash="hash123"
        )
        session.add(transaction)
        
        health_record = HealthDataRecord(
            id="record-123",
            user_id="user-456",
            transaction_id="tx-123",
            data_type=DataType.heart_rate,
            data_hash="hash123",
            encrypted_data=b"encrypted_data"
        )
        session.add(health_record)
        
        # 创建访问授权
        access_grant = AccessGrant(
            id="grant-123",
            owner_id="user-456",
            grantee_id="user-789",
            health_record_id="record-123",
            access_level=AccessLevel.read,
            permissions={"read_data": True},
            expires_at=datetime.utcnow() + timedelta(hours=24),
            is_active=True
        )
        
        session.add(access_grant)
        session.commit()
        
        # 查询验证
        retrieved = session.query(AccessGrant).filter_by(id="grant-123").first()
        assert retrieved is not None
        assert retrieved.owner_id == "user-456"
        assert retrieved.grantee_id == "user-789"
        assert retrieved.access_level == AccessLevel.read
        assert retrieved.permissions["read_data"] is True
        assert retrieved.is_active is True
        assert retrieved.health_record.id == "record-123"

    def test_zk_proof_registry_model(self, session):
        """测试零知识证明注册表模型"""
        zk_registry = ZKProofRegistry(
            id="zk-123",
            user_id="user-456",
            data_hash="hash123",
            proof_type="health_data_heart_rate",
            proof_data={"proof": {"a": [1, 2]}},
            public_inputs=[1, 2, 3],
            verification_key={"alpha": [1, 2]},
            circuit_id="circuit-123",
            is_verified=True
        )
        
        session.add(zk_registry)
        session.commit()
        
        # 查询验证
        retrieved = session.query(ZKProofRegistry).filter_by(id="zk-123").first()
        assert retrieved is not None
        assert retrieved.user_id == "user-456"
        assert retrieved.proof_type == "health_data_heart_rate"
        assert retrieved.is_verified is True
        assert retrieved.proof_data["proof"]["a"] == [1, 2]

    def test_smart_contract_model(self, session):
        """测试智能合约模型"""
        contract = SmartContract(
            id="contract-123",
            name="HealthDataStorage",
            address="0x1234567890123456789012345678901234567890",
            abi={"abi": "definition"},
            bytecode="0xabcdef",
            version="1.0.0",
            is_deployed=True,
            deployment_tx_hash="0x1234567890abcdef"
        )
        
        session.add(contract)
        session.commit()
        
        # 查询验证
        retrieved = session.query(SmartContract).filter_by(id="contract-123").first()
        assert retrieved is not None
        assert retrieved.name == "HealthDataStorage"
        assert retrieved.is_deployed is True
        assert retrieved.version == "1.0.0"

    def test_blockchain_node_model(self, session):
        """测试区块链节点模型"""
        node = BlockchainNode(
            id="node-123",
            name="MainNode",
            endpoint="http://localhost:8545",
            chain_id=1,
            is_active=True,
            last_block_number=12345,
            sync_status="synced"
        )
        
        session.add(node)
        session.commit()
        
        # 查询验证
        retrieved = session.query(BlockchainNode).filter_by(id="node-123").first()
        assert retrieved is not None
        assert retrieved.name == "MainNode"
        assert retrieved.is_active is True
        assert retrieved.last_block_number == 12345

    def test_audit_log_model(self, session):
        """测试审计日志模型"""
        audit_log = AuditLog(
            id="audit-123",
            user_id="user-456",
            action="store_health_data",
            resource_type="health_data",
            resource_id="record-123",
            old_values={"status": "draft"},
            new_values={"status": "confirmed"},
            audit_metadata={"ip": "127.0.0.1"}
        )
        
        session.add(audit_log)
        session.commit()
        
        # 查询验证
        retrieved = session.query(AuditLog).filter_by(id="audit-123").first()
        assert retrieved is not None
        assert retrieved.action == "store_health_data"
        assert retrieved.resource_type == "health_data"
        assert retrieved.old_values["status"] == "draft"
        assert retrieved.new_values["status"] == "confirmed"

    def test_enum_values(self):
        """测试枚举值"""
        # 测试TransactionStatus枚举
        assert TransactionStatus.PENDING.value == "pending"
        assert TransactionStatus.CONFIRMED.value == "confirmed"
        assert TransactionStatus.FAILED.value == "failed"
        
        # 测试DataType枚举
        assert DataType.heart_rate.value == "heart_rate"
        assert DataType.blood_pressure.value == "blood_pressure"
        assert DataType.temperature.value == "temperature"
        
        # 测试AccessLevel枚举
        assert AccessLevel.read.value == "read"
        assert AccessLevel.write.value == "write"
        assert AccessLevel.admin.value == "admin"

    def test_model_relationships(self, session):
        """测试模型关系"""
        # 创建交易
        transaction = BlockchainTransaction(
            id="tx-123",
            user_id="user-456",
            status=TransactionStatus.CONFIRMED,
            data_hash="hash123"
        )
        session.add(transaction)
        
        # 创建健康数据记录
        health_record = HealthDataRecord(
            id="record-123",
            user_id="user-456",
            transaction_id="tx-123",
            data_type=DataType.heart_rate,
            data_hash="hash123",
            encrypted_data=b"encrypted_data"
        )
        session.add(health_record)
        
        # 创建访问授权
        access_grant = AccessGrant(
            id="grant-123",
            owner_id="user-456",
            grantee_id="user-789",
            health_record_id="record-123",
            access_level=AccessLevel.read,
            is_active=True
        )
        session.add(access_grant)
        
        session.commit()
        
        # 测试关系
        retrieved_record = session.query(HealthDataRecord).filter_by(id="record-123").first()
        assert retrieved_record.transaction.id == "tx-123"
        assert len(retrieved_record.access_grants) == 1
        assert retrieved_record.access_grants[0].grantee_id == "user-789"
        
        retrieved_grant = session.query(AccessGrant).filter_by(id="grant-123").first()
        assert retrieved_grant.health_record.id == "record-123"

    def test_model_validation(self, session):
        """测试模型验证"""
        # 测试必填字段
        with pytest.raises(Exception):
            # 缺少必填字段的交易
            transaction = BlockchainTransaction()
            session.add(transaction)
            session.commit()

    def test_model_defaults(self, session):
        """测试模型默认值"""
        transaction = BlockchainTransaction(
            id="tx-123",
            user_id="user-456",
            status=TransactionStatus.PENDING,
            data_hash="hash123"
        )
        session.add(transaction)
        session.commit()
        
        # 验证默认值
        retrieved = session.query(BlockchainTransaction).filter_by(id="tx-123").first()
        assert retrieved.created_at is not None
        assert retrieved.updated_at is not None
        assert retrieved.gas_limit == 21000  # 默认值
        assert retrieved.gas_price == 20000000000  # 默认值 