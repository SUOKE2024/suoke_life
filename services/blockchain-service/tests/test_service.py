"""
区块链服务测试

测试区块链服务的核心功能。
"""

import pytest
import json
import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from suoke_blockchain_service.service import BlockchainService
from suoke_blockchain_service.models import DataType, AccessLevel, TransactionStatus
from suoke_blockchain_service.exceptions import (
    ValidationError, NotFoundError, BlockchainServiceError
)

@pytest.fixture
def blockchain_service():
    """创建区块链服务实例"""
    service = BlockchainService()
    # Mock外部依赖
    service.encryption_service = AsyncMock()
    service.zk_proof_generator = AsyncMock()
    service.zk_proof_verifier = AsyncMock()
    service.ipfs_client = AsyncMock()
    return service

@pytest.fixture
def sample_health_data():
    """示例健康数据"""
    return {
        "heart_rate": 72,
        "blood_pressure": {"systolic": 120, "diastolic": 80},
        "temperature": 36.5,
        "timestamp": "2024-01-01T10:00:00Z",
        "notes": "正常体检数据"
    }

@pytest.fixture
def sample_user_id():
    """示例用户ID"""
    return str(uuid.uuid4())

class TestBlockchainService:
    """区块链服务测试类"""

    @pytest.mark.asyncio
    async def test_store_health_data_success(self, blockchain_service, sample_health_data, sample_user_id):
        """测试成功存储健康数据"""
        # 设置Mock返回值
        blockchain_service.encryption_service.encrypt_data.return_value = (b"encrypted_data", "encryption_key")
        blockchain_service.ipfs_client.upload_data.return_value = "QmTestHash"
        blockchain_service.zk_proof_generator.generate_proof.return_value = {
            "proof": {"a": [1, 2], "b": [3, 4], "c": [5, 6]},
            "public_inputs": [1, 2, 3],
            "verification_key": {"alpha": [1, 2]}
        }

        with patch('suoke_blockchain_service.service.get_db_session') as mock_db, \
             patch('suoke_blockchain_service.service.get_blockchain_client') as mock_blockchain:
            
            # Mock数据库会话
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            # Mock区块链客户端
            mock_client = AsyncMock()
            mock_client.store_health_data.return_value = "0x123456789"
            mock_blockchain.return_value = mock_client

            # 执行测试
            result = await blockchain_service.store_health_data(
                user_id=sample_user_id,
                data=sample_health_data,
                data_type="heart_rate"
            )

            # 验证结果
            assert result["status"] == "pending"
            assert "record_id" in result
            assert "transaction_hash" in result
            assert result["transaction_hash"] == "0x123456789"
            
            # 验证调用
            blockchain_service.encryption_service.encrypt_data.assert_called_once()
            blockchain_service.ipfs_client.upload_data.assert_called_once()
            blockchain_service.zk_proof_generator.generate_proof.assert_called_once()
            mock_client.store_health_data.assert_called_once()

    @pytest.mark.asyncio
    async def test_store_health_data_validation_error(self, blockchain_service):
        """测试存储健康数据验证错误"""
        with pytest.raises(BlockchainServiceError, match="存储健康数据失败.*用户ID不能为空"):
            await blockchain_service.store_health_data(
                user_id="",
                data={"test": "data"},
                data_type="heart_rate"
            )

        with pytest.raises(BlockchainServiceError, match="存储健康数据失败.*数据不能为空"):
            await blockchain_service.store_health_data(
                user_id="user123",
                data={},
                data_type="heart_rate"
            )

        with pytest.raises(BlockchainServiceError, match="存储健康数据失败.*无效的数据类型"):
            await blockchain_service.store_health_data(
                user_id="user123",
                data={"test": "data"},
                data_type="invalid_type"
            )

    @pytest.mark.asyncio
    async def test_verify_health_data_success(self, blockchain_service, sample_user_id):
        """测试成功验证健康数据"""
        record_id = str(uuid.uuid4())
        
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db, \
             patch('suoke_blockchain_service.service.get_blockchain_client') as mock_blockchain:
            
            # Mock数据库查询结果
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_health_record = MagicMock()
            mock_health_record.id = record_id
            mock_health_record.user_id = sample_user_id
            mock_health_record.data_hash = "test_hash"
            mock_health_record.zkp_proof = {"proof": "test"}
            mock_health_record.public_inputs = [1, 2, 3]
            mock_health_record.verification_key = {"key": "test"}
            mock_health_record.ipfs_hash = "QmTestHash"
            mock_health_record.encrypted_data = b"encrypted_data"
            mock_health_record.metadata = {"zkp_circuit": "test_circuit"}
            mock_health_record.transaction = MagicMock()
            mock_health_record.transaction.transaction_hash = "0x123456789"
            
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_health_record
            mock_session.execute.return_value = mock_result

            # Mock区块链客户端
            mock_client = AsyncMock()
            mock_client.verify_health_data.return_value = True
            mock_blockchain.return_value = mock_client

            # Mock ZK验证
            blockchain_service.zk_proof_verifier.verify_proof.return_value = True
            
            # Mock IPFS验证
            blockchain_service.ipfs_client.get_data.return_value = b"encrypted_data"

            # 执行测试
            result = await blockchain_service.verify_health_data(
                record_id=record_id,
                user_id=sample_user_id
            )

            # 验证结果
            assert result["overall_valid"] is True
            assert result["blockchain_valid"] is True
            assert result["zkp_valid"] is True
            assert result["ipfs_valid"] is True
            assert result["record_id"] == record_id

    @pytest.mark.asyncio
    async def test_verify_health_data_not_found(self, blockchain_service, sample_user_id):
        """测试验证不存在的健康数据"""
        record_id = str(uuid.uuid4())
        
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db:
            # Mock数据库查询结果为空
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result

            # 执行测试并验证异常
            with pytest.raises(BlockchainServiceError, match="验证健康数据失败.*健康数据记录不存在"):
                await blockchain_service.verify_health_data(
                    record_id=record_id,
                    user_id=sample_user_id
                )

    @pytest.mark.asyncio
    async def test_grant_access_success(self, blockchain_service, sample_user_id):
        """测试成功授权访问"""
        record_id = str(uuid.uuid4())
        grantee_id = str(uuid.uuid4())
        
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db, \
             patch('suoke_blockchain_service.service.get_blockchain_client') as mock_blockchain:
            
            # Mock数据库操作
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            # Mock健康记录存在
            mock_health_record = MagicMock()
            mock_health_record.id = record_id
            mock_health_record.user_id = sample_user_id
            
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.side_effect = [mock_health_record, None]  # 记录存在，授权不存在
            mock_session.execute.return_value = mock_result

            # Mock区块链客户端
            mock_client = AsyncMock()
            mock_client.grant_access.return_value = "0x987654321"
            mock_blockchain.return_value = mock_client

            # 执行测试
            result = await blockchain_service.grant_access(
                owner_id=sample_user_id,
                grantee_id=grantee_id,
                record_id=record_id,
                access_level="read"
            )

            # 验证结果
            assert result["status"] == "pending"
            assert "grant_id" in result
            assert result["transaction_hash"] == "0x987654321"
            assert result["access_level"] == "read"

    @pytest.mark.asyncio
    async def test_revoke_access_success(self, blockchain_service, sample_user_id):
        """测试成功撤销访问"""
        record_id = str(uuid.uuid4())
        grantee_id = str(uuid.uuid4())
        
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db, \
             patch('suoke_blockchain_service.service.get_blockchain_client') as mock_blockchain:
            
            # Mock数据库操作
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            # Mock现有授权
            mock_grant = MagicMock()
            mock_grant.id = str(uuid.uuid4())
            mock_grant.is_active = True
            
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_grant
            mock_session.execute.return_value = mock_result

            # Mock区块链客户端
            mock_client = AsyncMock()
            mock_client.revoke_access.return_value = "0x111222333"
            mock_blockchain.return_value = mock_client

            # 执行测试
            result = await blockchain_service.revoke_access(
                owner_id=sample_user_id,
                grantee_id=grantee_id,
                record_id=record_id,
                reason="测试撤销"
            )

            # 验证结果
            assert result["status"] == "pending"
            assert result["grant_id"] == mock_grant.id
            assert result["transaction_hash"] == "0x111222333"
            assert result["reason"] == "测试撤销"
            
            # 验证授权被撤销
            assert mock_grant.is_active is False
            assert mock_grant.revocation_reason == "测试撤销"

    @pytest.mark.asyncio
    async def test_get_health_records_success(self, blockchain_service, sample_user_id):
        """测试成功获取健康记录"""
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db:
            # Mock数据库操作
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            # Mock健康记录
            mock_record1 = MagicMock()
            mock_record1.id = str(uuid.uuid4())
            mock_record1.data_type = DataType.HEART_RATE
            mock_record1.data_hash = "hash1"
            mock_record1.ipfs_hash = "QmHash1"
            mock_record1.created_at = datetime.utcnow()
            mock_record1.zkp_proof = {"proof": "test"}
            mock_record1.metadata = {}
            mock_record1.transaction = MagicMock()
            mock_record1.transaction.transaction_hash = "0x111"
            mock_record1.transaction.status = TransactionStatus.CONFIRMED
            
            mock_record2 = MagicMock()
            mock_record2.id = str(uuid.uuid4())
            mock_record2.data_type = DataType.BLOOD_PRESSURE
            mock_record2.data_hash = "hash2"
            mock_record2.ipfs_hash = "QmHash2"
            mock_record2.created_at = datetime.utcnow()
            mock_record2.zkp_proof = None
            mock_record2.metadata = {}
            mock_record2.transaction = None
            
            mock_records = [mock_record1, mock_record2]
            
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = mock_records
            mock_session.execute.return_value = mock_result

            # 执行测试
            result = await blockchain_service.get_health_records(
                user_id=sample_user_id,
                limit=10,
                offset=0
            )

            # 验证结果
            assert len(result["records"]) == 2
            assert result["total_count"] == 2
            assert result["limit"] == 10
            assert result["offset"] == 0
            assert result["has_more"] is False
            
            # 验证记录内容
            record1_data = result["records"][0]
            assert record1_data["id"] == mock_record1.id
            assert record1_data["data_type"] == "heart_rate"
            assert record1_data["has_zkp"] is True
            assert record1_data["transaction_hash"] == "0x111"

    @pytest.mark.asyncio
    async def test_get_access_grants_as_owner(self, blockchain_service, sample_user_id):
        """测试获取作为所有者的访问授权"""
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db:
            # Mock数据库操作
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            # Mock访问授权
            mock_grant = MagicMock()
            mock_grant.id = str(uuid.uuid4())
            mock_grant.owner_id = sample_user_id
            mock_grant.grantee_id = str(uuid.uuid4())
            mock_grant.health_record_id = str(uuid.uuid4())
            mock_grant.access_level = AccessLevel.READ
            mock_grant.permissions = {"read": True}
            mock_grant.granted_at = datetime.utcnow()
            mock_grant.expires_at = None
            mock_grant.is_active = True
            mock_grant.revoked_at = None
            mock_grant.revocation_reason = None
            mock_grant.transaction = MagicMock()
            mock_grant.transaction.transaction_hash = "0x222"
            mock_grant.health_record = MagicMock()
            mock_grant.health_record.data_type = DataType.HEART_RATE
            mock_grant.health_record.created_at = datetime.utcnow()
            
            mock_grants = [mock_grant]
            
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = mock_grants
            mock_session.execute.return_value = mock_result

            # 执行测试
            result = await blockchain_service.get_access_grants(
                user_id=sample_user_id,
                as_owner=True,
                active_only=True
            )

            # 验证结果
            assert len(result) == 1
            grant_data = result[0]
            assert grant_data["id"] == mock_grant.id
            assert grant_data["owner_id"] == sample_user_id
            assert grant_data["access_level"] == "read"
            assert grant_data["is_active"] is True
            assert grant_data["transaction_hash"] == "0x222"

    def test_validate_store_request_success(self, blockchain_service, sample_health_data, sample_user_id):
        """测试存储请求验证成功"""
        # 应该不抛出异常
        blockchain_service._validate_store_request(
            user_id=sample_user_id,
            data=sample_health_data,
            data_type="heart_rate"
        )

    def test_validate_store_request_failures(self, blockchain_service, sample_health_data):
        """测试存储请求验证失败的情况"""
        # 空用户ID
        with pytest.raises(ValidationError, match="用户ID不能为空"):
            blockchain_service._validate_store_request("", sample_health_data, "heart_rate")
        
        # 空数据
        with pytest.raises(ValidationError, match="数据不能为空"):
            blockchain_service._validate_store_request("user123", {}, "heart_rate")
        
        # 空数据类型
        with pytest.raises(ValidationError, match="数据类型不能为空"):
            blockchain_service._validate_store_request("user123", sample_health_data, "")
        
        # 无效数据类型
        with pytest.raises(ValidationError, match="无效的数据类型"):
            blockchain_service._validate_store_request("user123", sample_health_data, "invalid_type")

    def test_generate_data_hash(self, blockchain_service, sample_health_data):
        """测试数据哈希生成"""
        hash1 = blockchain_service._generate_data_hash(sample_health_data)
        hash2 = blockchain_service._generate_data_hash(sample_health_data)
        
        # 相同数据应该生成相同哈希
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256哈希长度
        
        # 不同数据应该生成不同哈希
        different_data = {**sample_health_data, "heart_rate": 80}
        hash3 = blockchain_service._generate_data_hash(different_data)
        assert hash1 != hash3

    @pytest.mark.asyncio
    async def test_create_audit_log(self, blockchain_service, sample_user_id):
        """测试创建审计日志"""
        mock_session = AsyncMock()
        
        await blockchain_service._create_audit_log(
            session=mock_session,
            user_id=sample_user_id,
            action="test_action",
            resource_type="test_resource",
            resource_id="test_id",
            new_values={"test": "value"}
        )
        
        # 验证session.add被调用
        mock_session.add.assert_called_once()
        
        # 验证添加的对象类型
        added_object = mock_session.add.call_args[0][0]
        assert added_object.user_id == sample_user_id
        assert added_object.action == "test_action"
        assert added_object.resource_type == "test_resource"
        assert added_object.resource_id == "test_id"
        assert added_object.new_values == {"test": "value"}
        assert added_object.success is True 