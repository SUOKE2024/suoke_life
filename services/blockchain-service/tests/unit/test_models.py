"""
数据模型单元测试
"""

import pytest
from datetime import datetime, UTC
from uuid import uuid4

from blockchain_service.models.base import Base
from blockchain_service.models.health_data import HealthDataRecord, HealthDataMetadata, DataType, DataStatus
from blockchain_service.models.blockchain import BlockchainTransaction, ContractEvent, TransactionStatus, ContractType
from blockchain_service.models.user import UserProfile, AccessPermission, UserRole, PermissionType


class TestHealthDataModels:
    """健康数据模型测试"""
    
    def test_health_data_record_creation(self):
        """测试健康数据记录创建"""
        user_id = str(uuid4())
        data_content = {"heart_rate": 72, "blood_pressure": "120/80"}
        
        record = HealthDataRecord(
            user_id=user_id,
            data_type=DataType.VITAL_SIGNS,
            title="生命体征数据",
            data_content=data_content
        )
        
        assert record.user_id == user_id
        assert record.data_type == DataType.VITAL_SIGNS
        assert record.title == "生命体征数据"
        assert record.data_content == data_content
        # 在没有数据库会话的情况下，默认值不会自动设置
        # 但我们可以验证字段存在
        assert hasattr(record, 'id')
        assert hasattr(record, 'status')
        assert hasattr(record, 'is_encrypted')
        assert hasattr(record, 'is_verified')
    
    def test_health_data_metadata_creation(self):
        """测试健康数据元数据创建"""
        record_id = str(uuid4())
        
        metadata = HealthDataMetadata(
            data_record_id=record_id,
            source_system="mobile_app",
            source_device="iPhone 13",
            quality_score=0.95
        )
        
        assert metadata.data_record_id == record_id
        assert metadata.source_system == "mobile_app"
        assert metadata.source_device == "iPhone 13"
        assert metadata.quality_score == 0.95
        assert hasattr(metadata, 'id')


class TestBlockchainModels:
    """区块链模型测试"""
    
    def test_blockchain_transaction_creation(self):
        """测试区块链交易创建"""
        tx_hash = "0x1234567890abcdef"
        
        transaction = BlockchainTransaction(
            transaction_hash=tx_hash,
            from_address="0x123",
            to_address="0x456",
            gas_limit=21000,
            gas_used=21000,
            gas_price=20000000000,
            block_number=12345,
            operation_type="store_data",
            status=TransactionStatus.CONFIRMED
        )
        
        assert transaction.transaction_hash == tx_hash
        assert transaction.from_address == "0x123"
        assert transaction.to_address == "0x456"
        assert transaction.gas_limit == 21000
        assert transaction.gas_used == 21000
        assert transaction.gas_price == 20000000000
        assert transaction.block_number == 12345
        assert transaction.operation_type == "store_data"
        assert transaction.status == TransactionStatus.CONFIRMED
        assert hasattr(transaction, 'id')
    
    def test_contract_event_creation(self):
        """测试合约事件创建"""
        tx_hash = "0x1234567890abcdef"
        
        event = ContractEvent(
            transaction_hash=tx_hash,
            contract_address="0x789",
            contract_type=ContractType.HEALTH_DATA_STORAGE,
            event_name="Transfer",
            event_signature="0xabcdef",
            event_data={"from": "0x123", "to": "0x456", "value": 1000},
            block_number=12345,
            log_index=0
        )
        
        assert event.transaction_hash == tx_hash
        assert event.contract_address == "0x789"
        assert event.contract_type == ContractType.HEALTH_DATA_STORAGE
        assert event.event_name == "Transfer"
        assert event.event_signature == "0xabcdef"
        assert event.event_data["from"] == "0x123"
        assert event.block_number == 12345
        assert event.log_index == 0
        assert hasattr(event, 'id')


class TestUserModels:
    """用户模型测试"""
    
    def test_user_profile_creation(self):
        """测试用户档案创建"""
        user_id = str(uuid4())
        
        profile = UserProfile(
            user_id=user_id,
            username="test_user",
            wallet_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4Db93",
            public_key="0x04...",
            privacy_settings={"language": "zh-CN", "notifications": True},
            is_active=True
        )
        
        assert profile.user_id == user_id
        assert profile.username == "test_user"
        assert profile.wallet_address == "0x742d35Cc6634C0532925a3b8D4C9db96C4b4Db93"
        assert profile.public_key == "0x04..."
        assert profile.privacy_settings["language"] == "zh-CN"
        assert profile.is_active is True
        assert hasattr(profile, 'role')
        assert hasattr(profile, 'id')
    
    def test_access_permission_creation(self):
        """测试访问权限创建"""
        grantor_id = str(uuid4())
        grantee_id = str(uuid4())
        resource_id = str(uuid4())
        
        permission = AccessPermission(
            grantor_id=grantor_id,
            grantee_id=grantee_id,
            permission_type=PermissionType.READ,
            resource_type="health_data",
            resource_id=resource_id,
            permissions=["read", "view"],
            valid_until=datetime.now(UTC),
            is_active=True
        )
        
        assert permission.grantor_id == grantor_id
        assert permission.grantee_id == grantee_id
        assert permission.permission_type == PermissionType.READ
        assert permission.resource_type == "health_data"
        assert permission.resource_id == resource_id
        assert permission.permissions == ["read", "view"]
        assert permission.valid_until is not None
        assert permission.is_active is True
        assert hasattr(permission, 'id')


class TestBaseModel:
    """基础模型测试"""
    
    def test_base_model_properties(self):
        """测试基础模型属性"""
        # 由于Base是抽象类，我们使用具体的模型来测试
        user_id = str(uuid4())
        
        profile = UserProfile(
            user_id=user_id,
            username="test_user",
            wallet_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4Db93"
        )
        
        # 测试基础属性
        assert hasattr(profile, 'id')
        assert hasattr(profile, 'created_at')
        assert hasattr(profile, 'updated_at')
        
        # 测试ID字段存在
        assert hasattr(profile, 'id')


class TestModelRelationships:
    """模型关系测试"""
    
    def test_health_data_record_metadata_relationship(self):
        """测试健康数据记录和元数据的关系"""
        user_id = str(uuid4())
        
        # 创建健康数据记录
        record = HealthDataRecord(
            user_id=user_id,
            data_type=DataType.VITAL_SIGNS,
            title="生命体征",
            data_content={"heart_rate": 72}
        )
        
        # 创建关联的元数据
        metadata = HealthDataMetadata(
            data_record_id=str(record.id),
            source_system="mobile_app",
            source_device="iPhone 13",
            quality_score=0.95
        )
        
        # 验证关系
        assert metadata.data_record_id == str(record.id)
    
    def test_user_profile_permissions_relationship(self):
        """测试用户档案和权限的关系"""
        grantor_id = str(uuid4())
        grantee_id = str(uuid4())
        resource_id = str(uuid4())
        
        # 创建用户档案
        profile = UserProfile(
            user_id=grantor_id,
            username="grantor_user",
            wallet_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4Db93"
        )
        
        # 创建访问权限
        permission = AccessPermission(
            grantor_id=grantor_id,
            grantee_id=grantee_id,
            permission_type=PermissionType.READ,
            resource_type="health_data",
            resource_id=resource_id,
            permissions=["read"],
            valid_until=datetime.now(UTC),
            is_active=True
        )
        
        # 验证关系
        assert permission.grantor_id == profile.user_id


class TestModelValidation:
    """模型验证测试"""
    
    def test_health_data_record_validation(self):
        """测试健康数据记录验证"""
        user_id = str(uuid4())
        
        # 测试有效数据
        record = HealthDataRecord(
            user_id=user_id,
            data_type=DataType.VITAL_SIGNS,
            title="生命体征",
            data_content={"heart_rate": 72}
        )
        
        assert record.user_id == user_id
        assert record.data_type == DataType.VITAL_SIGNS
        assert record.title == "生命体征"
        assert record.data_content == {"heart_rate": 72}
    
    def test_blockchain_transaction_validation(self):
        """测试区块链交易验证"""
        # 测试有效交易
        transaction = BlockchainTransaction(
            transaction_hash="0x1234567890abcdef",
            from_address="0x123",
            to_address="0x456",
            gas_limit=21000,
            gas_used=21000,
            gas_price=20000000000,
            block_number=12345,
            operation_type="store_data",
            status=TransactionStatus.CONFIRMED
        )
        
        assert transaction.transaction_hash == "0x1234567890abcdef"
        assert transaction.from_address == "0x123"
        assert transaction.to_address == "0x456"
        assert transaction.gas_limit == 21000
        assert transaction.gas_used == 21000
        assert transaction.gas_price == 20000000000
        assert transaction.block_number == 12345
        assert transaction.operation_type == "store_data"
        assert transaction.status == TransactionStatus.CONFIRMED
    
    def test_user_profile_validation(self):
        """测试用户档案验证"""
        user_id = str(uuid4())
        
        # 测试有效用户档案
        profile = UserProfile(
            user_id=user_id,
            username="valid_user",
            wallet_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4Db93",
            role=UserRole.PATIENT,
            is_active=True
        )
        
        assert profile.user_id == user_id
        assert profile.username == "valid_user"
        assert profile.wallet_address == "0x742d35Cc6634C0532925a3b8D4C9db96C4b4Db93"
        assert profile.role == UserRole.PATIENT
        assert profile.is_active is True 