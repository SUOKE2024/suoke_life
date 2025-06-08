"""
test_service - 索克生活项目模块
"""

from datetime import datetime, timedelta
from suoke_blockchain_service.exceptions import ValidationError, NotFoundError, BlockchainServiceError
from suoke_blockchain_service.models import DataType, TransactionStatus, AccessLevel
from suoke_blockchain_service.service import BlockchainService
from typing import Dict, Any
from unittest.mock import AsyncMock, MagicMock, patch
import json
import pytest
import uuid

"""
区块链服务测试模块

测试区块链服务的核心业务逻辑。
"""





class TestBlockchainService:
    """区块链服务测试类"""

    @pytest.fixture
    def blockchain_service(self):
        """创建区块链服务实例"""
        return BlockchainService()

    @pytest.fixture
    def sample_user_id(self):
        """示例用户ID"""
        return str(uuid.uuid4())

    @pytest.fixture
    def sample_health_data(self):
        """示例健康数据"""
        return {
            "user_id": "test-user-123",
            "timestamp": datetime.now().isoformat(),
            "data_type": "heart_rate",
            "measurements": {
                "heart_rate": 72,
                "blood_pressure": {"systolic": 120, "diastolic": 80}
            },
            "device_info": {
                "device_id": "smartwatch-001",
                "manufacturer": "HealthTech"
            }
        }

    @pytest.mark.asyncio
    async def test_store_health_data_success(self, blockchain_service, sample_user_id, sample_health_data):
        """测试成功存储健康数据"""
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db, \
            patch('suoke_blockchain_service.service.get_blockchain_client') as mock_blockchain:

            # Mock数据库会话
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session

            # Mock区块链客户端
            mock_client = AsyncMock()
            mock_client.store_health_data.return_value = "0x1234567890abcdef"
            mock_blockchain.return_value = mock_client

            # Mock加密和IPFS服务
            blockchain_service.encryption_service.encrypt_data = AsyncMock(
                return_value=(b"encrypted_data", "encryption_key")
            )
            blockchain_service.ipfs_client.upload_data = AsyncMock(
                return_value="QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"
            )
            blockchain_service.zk_proof_generator.generate_proof = AsyncMock(
                return_value={"proof": {"a": [1, 2]}, "public_inputs": [1, 2, 3]}
            )

            result = await blockchain_service.store_health_data(
                user_id=sample_user_id,
                data=sample_health_data,
                data_type="heart_rate"
            )

            assert "record_id" in result
            assert "transaction_id" in result
            assert "transaction_hash" in result
            assert result["status"] == "pending"

    @pytest.mark.asyncio
    async def test_store_health_data_validation_error(self, blockchain_service):
        """测试存储健康数据验证错误"""
        # 测试完整的store_health_data方法，它会包装ValidationError为BlockchainServiceError
        with pytest.raises(BlockchainServiceError, match="存储健康数据失败.*用户ID不能为空"):
            await blockchain_service.store_health_data(
                user_id="",
                data={"test": "data"},
                data_type="heart_rate"
            )

    @pytest.mark.asyncio
    async def test_verify_health_data_success(self, blockchain_service, sample_user_id):
        """测试成功验证健康数据"""
        record_id = str(uuid.uuid4())

        with patch('suoke_blockchain_service.service.get_db_session') as mock_db, \
            patch('suoke_blockchain_service.service.get_blockchain_client') as mock_blockchain:

            # Mock健康数据记录
            mock_record = MagicMock()
            mock_record.id = record_id
            mock_record.user_id = sample_user_id
            mock_record.data_hash = "test_hash"
            mock_record.ipfs_hash = "QmTest"
            mock_record.encrypted_data = b"encrypted_data"
            mock_record.zkp_proof = {"proof": {"a": [1, 2]}}
            mock_record.public_inputs = [1, 2, 3]
            mock_record.verification_key = {"alpha": [1, 2]}
            mock_record.record_metadata = {"zkp_circuit": "health_data_heart_rate"}
            mock_record.transaction = MagicMock()
            mock_record.transaction.transaction_hash = "0x1234567890abcdef"

            # Mock数据库查询
            mock_session = AsyncMock()
            mock_result = AsyncMock()
            mock_result.scalar_one_or_none.return_value = mock_record
            mock_session.execute.return_value = mock_result
            mock_db.return_value.__aenter__.return_value = mock_session

            # Mock区块链验证
            mock_client = AsyncMock()
            mock_client.verify_health_data.return_value = True
            mock_blockchain.return_value = mock_client

            # Mock ZK证明验证和IPFS验证
            blockchain_service.zk_proof_verifier.verify_proof = AsyncMock(return_value=True)
            blockchain_service.ipfs_client.get_data = AsyncMock(return_value=b"encrypted_data")

            result = await blockchain_service.verify_health_data(
                record_id=record_id,
                user_id=sample_user_id
            )

            assert result["blockchain_valid"] is True
            assert result["zkp_valid"] is True
            assert result["ipfs_valid"] is True
            assert result["overall_valid"] is True

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

            # 执行测试并验证异常 - verify_health_data会包装NotFoundError为BlockchainServiceError
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

            # Mock健康数据记录
            mock_health_record = MagicMock()
            mock_health_record.id = record_id
            mock_health_record.user_id = sample_user_id

            # Mock数据库查询
            mock_session = AsyncMock()
            mock_result = AsyncMock()
            mock_result.scalar_one_or_none.side_effect = [mock_health_record, None]  # 记录存在，授权不存在
            mock_session.execute.return_value = mock_result
            mock_db.return_value.__aenter__.return_value = mock_session

            # Mock区块链客户端
            mock_client = AsyncMock()
            mock_client.grant_access.return_value = "0x1234567890abcdef"
            mock_blockchain.return_value = mock_client

            result = await blockchain_service.grant_access(
                owner_id=sample_user_id,
                grantee_id=grantee_id,
                record_id=record_id,
                access_level="read",
                expires_at=datetime.now() + timedelta(hours=24)
            )

            assert "grant_id" in result
            assert "transaction_hash" in result
            assert result["expires_at"] is not None

    @pytest.mark.asyncio
    async def test_revoke_access_success(self, blockchain_service, sample_user_id):
        """测试成功撤销访问"""
        record_id = str(uuid.uuid4())
        grantee_id = str(uuid.uuid4())

        with patch('suoke_blockchain_service.service.get_db_session') as mock_db, \
            patch('suoke_blockchain_service.service.get_blockchain_client') as mock_blockchain:

            # Mock访问授权记录
            mock_grant = MagicMock()
            mock_grant.id = str(uuid.uuid4())
            mock_grant.owner_id = sample_user_id
            mock_grant.grantee_id = grantee_id
            mock_grant.health_record_id = record_id
            mock_grant.is_active = True

            # Mock数据库查询
            mock_session = AsyncMock()
            mock_result = AsyncMock()
            mock_result.scalar_one_or_none.return_value = mock_grant
            mock_session.execute.return_value = mock_result
            mock_db.return_value.__aenter__.return_value = mock_session

            # Mock区块链客户端
            mock_client = AsyncMock()
            mock_client.revoke_access.return_value = "0x1234567890abcdef"
            mock_blockchain.return_value = mock_client

            result = await blockchain_service.revoke_access(
                owner_id=sample_user_id,
                grantee_id=grantee_id,
                record_id=record_id,
                reason="测试撤销"
            )

            assert "grant_id" in result
            assert "revoked_at" in result
            assert result["reason"] == "测试撤销"

    @pytest.mark.asyncio
    async def test_get_health_records_success(self, blockchain_service, sample_user_id):
        """测试成功获取健康记录"""
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db:
            # Mock健康记录
            mock_record1 = MagicMock()
            mock_record1.id = str(uuid.uuid4())
            mock_record1.data_type = DataType.heart_rate
            mock_record1.data_hash = "hash1"
            mock_record1.ipfs_hash = "QmTest1"
            mock_record1.created_at = datetime.now()
            mock_record1.zkp_proof = {"proof": {"a": [1, 2]}}
            mock_record1.record_metadata = {"original_size": 123}
            mock_record1.transaction = MagicMock()
            mock_record1.transaction.transaction_hash = "0x1234567890abcdef"
            mock_record1.transaction.status = TransactionStatus.confirmed

            mock_record2 = MagicMock()
            mock_record2.id = str(uuid.uuid4())
            mock_record2.data_type = DataType.heart_rate
            mock_record2.data_hash = "hash2"
            mock_record2.ipfs_hash = "QmTest2"
            mock_record2.created_at = datetime.now()
            mock_record2.zkp_proof = None
            mock_record2.record_metadata = {"original_size": 456}
            mock_record2.transaction = None

            # Mock数据库查询
            mock_session = AsyncMock()
            mock_result = AsyncMock()
            mock_result.scalars.return_value.all.return_value = [mock_record1, mock_record2]
            mock_session.execute.return_value = mock_result
            mock_db.return_value.__aenter__.return_value = mock_session

            result = await blockchain_service.get_health_records(
                user_id=sample_user_id,
                data_type="heart_rate",
                limit=10,
                offset=0
            )

            assert result["total_count"] == 2
            assert len(result["records"]) == 2
            assert result["has_more"] is False

            # 验证记录内容
            record1 = result["records"][0]
            assert record1["id"] == mock_record1.id
            assert record1["data_type"] == "heart_rate"
            assert record1["has_zkp"] is True
            assert record1["transaction_status"] == "confirmed"

    @pytest.mark.asyncio
    async def test_get_access_grants_as_owner(self, blockchain_service, sample_user_id):
        """测试作为所有者获取访问授权"""
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db:
            # Mock访问授权记录
            mock_grant = MagicMock()
            mock_grant.id = str(uuid.uuid4())
            mock_grant.grantee_id = str(uuid.uuid4())
            mock_grant.access_level = AccessLevel.read
            mock_grant.permissions = {"read_data": True}
            mock_grant.granted_at = datetime.now()
            mock_grant.expires_at = datetime.now() + timedelta(hours=24)
            mock_grant.is_active = True
            mock_grant.revoked_at = None
            mock_grant.revocation_reason = None

            # Mock关联的健康记录
            mock_grant.health_record = MagicMock()
            mock_grant.health_record.id = str(uuid.uuid4())
            mock_grant.health_record.data_type = DataType.heart_rate
            mock_grant.health_record.created_at = datetime.now()

            # Mock数据库查询
            mock_session = AsyncMock()
            mock_result = AsyncMock()
            mock_result.scalars.return_value.all.return_value = [mock_grant]
            mock_session.execute.return_value = mock_result
            mock_db.return_value.__aenter__.return_value = mock_session

            result = await blockchain_service.get_access_grants(
                user_id=sample_user_id,
                as_owner=True,
                active_only=True
            )

            assert len(result) == 1
            grant = result[0]
            assert grant["grantee_id"] == mock_grant.grantee_id
            assert grant["access_level"] == "read"
            assert grant["is_active"] is True

    @pytest.mark.asyncio
    async def test_validate_store_request_success(self, blockchain_service):
        """测试存储请求验证成功"""
        # 正常情况不应该抛出异常
        blockchain_service._validate_store_request(
            user_id="test-user-123",
            data={"test": "data"},
            data_type="heart_rate"
        )

    @pytest.mark.asyncio
    async def test_validate_store_request_failures(self, blockchain_service):
        """测试存储请求验证失败情况"""
        # 测试空用户ID
        with pytest.raises(ValidationError, match="用户ID不能为空"):
            blockchain_service._validate_store_request("", {"test": "data"}, "heart_rate")

        # 测试空数据
        with pytest.raises(ValidationError, match="数据不能为空"):
            blockchain_service._validate_store_request("user123", {}, "heart_rate")

        # 测试空数据类型
        with pytest.raises(ValidationError, match="数据类型不能为空"):
            blockchain_service._validate_store_request("user123", {"test": "data"}, "")

    @pytest.mark.asyncio
    async def test_generate_data_hash(self, blockchain_service):
        """测试数据哈希生成"""
        data = {"test": "data", "number": 123}
        hash1 = blockchain_service._generate_data_hash(data)
        hash2 = blockchain_service._generate_data_hash(data)

        # 相同数据应该生成相同哈希
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256哈希长度

        # 不同数据应该生成不同哈希
        different_data = {"test": "different", "number": 456}
        hash3 = blockchain_service._generate_data_hash(different_data)
        assert hash1 != hash3

    @pytest.mark.asyncio
    async def test_create_audit_log(self, blockchain_service, sample_user_id):
        """测试创建审计日志"""
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db:
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session

            await blockchain_service._create_audit_log(
                session=mock_session,
                user_id=sample_user_id,
                action="test_action",
                resource_type="test_resource",
                resource_id="test_id",
                old_values={"old": "value"},
                new_values={"new": "value"},
                audit_metadata={"meta": "data"}
            )

            # 验证session.add被调用
            mock_session.add.assert_called_once() 