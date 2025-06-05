"""
全面测试覆盖率提升

补充边界条件、异常情况和未测试代码路径的测试用例。
"""

import pytest
import json
import uuid
import hashlib
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch, call
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from suoke_blockchain_service.service import BlockchainService
from suoke_blockchain_service.models import DataType, AccessLevel, TransactionStatus
from suoke_blockchain_service.exceptions import (
    ValidationError, NotFoundError, BlockchainServiceError, 
    PermissionError, IntegrationError
)
from suoke_blockchain_service.encryption import EncryptionService
from suoke_blockchain_service.zk_integration import ZKProofGenerator, ZKProofVerifier
from suoke_blockchain_service.ipfs_client import IPFSClient
from suoke_blockchain_service.blockchain_client import get_blockchain_client


@pytest.fixture
def blockchain_service():
    """创建区块链服务实例"""
    service = BlockchainService()
    service.encryption_service = AsyncMock()
    service.zk_proof_generator = AsyncMock()
    service.zk_proof_verifier = AsyncMock()
    service.ipfs_client = AsyncMock()
    return service


class TestBlockchainServiceEdgeCases:
    """区块链服务边界条件测试"""

    @pytest.mark.asyncio
    async def test_store_health_data_encryption_failure(self, blockchain_service):
        """测试加密失败的情况"""
        blockchain_service.encryption_service.encrypt_data.side_effect = Exception("加密失败")
        
        with pytest.raises(BlockchainServiceError, match="存储健康数据失败"):
            await blockchain_service.store_health_data(
                user_id="user123",
                data={"heart_rate": 72},
                data_type="heart_rate"
            )

    @pytest.mark.asyncio
    async def test_store_health_data_ipfs_failure(self, blockchain_service):
        """测试IPFS上传失败的情况"""
        blockchain_service.encryption_service.encrypt_data.return_value = (b"encrypted", "key")
        blockchain_service.ipfs_client.upload_data.side_effect = Exception("IPFS上传失败")
        
        with pytest.raises(BlockchainServiceError, match="存储健康数据失败"):
            await blockchain_service.store_health_data(
                user_id="user123",
                data={"heart_rate": 72},
                data_type="heart_rate"
            )

    @pytest.mark.asyncio
    async def test_store_health_data_zkp_failure(self, blockchain_service):
        """测试零知识证明生成失败的情况"""
        blockchain_service.encryption_service.encrypt_data.return_value = (b"encrypted", "key")
        blockchain_service.ipfs_client.upload_data.return_value = "QmHash"
        blockchain_service.zk_proof_generator.generate_proof.side_effect = Exception("ZKP生成失败")
        
        with pytest.raises(BlockchainServiceError, match="存储健康数据失败.*ZKP生成失败"):
            await blockchain_service.store_health_data(
                user_id="user123",
                data={"heart_rate": 72},
                data_type="heart_rate"
            )

    @pytest.mark.asyncio
    async def test_store_health_data_database_failure(self, blockchain_service):
        """测试数据库操作失败的情况"""
        blockchain_service.encryption_service.encrypt_data.return_value = (b"encrypted", "key")
        blockchain_service.ipfs_client.upload_data.return_value = "QmHash"
        blockchain_service.zk_proof_generator.generate_proof.return_value = {"proof": "test"}
        
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db:
            mock_session = AsyncMock()
            mock_session.commit.side_effect = SQLAlchemyError("数据库错误")
            mock_db.return_value.__aenter__.return_value = mock_session
            
            with pytest.raises(BlockchainServiceError, match="存储健康数据失败.*数据库错误"):
                await blockchain_service.store_health_data(
                    user_id="user123",
                    data={"heart_rate": 72},
                    data_type="heart_rate"
                )

    @pytest.mark.asyncio
    async def test_store_health_data_blockchain_failure(self, blockchain_service):
        """测试区块链交易失败的情况"""
        blockchain_service.encryption_service.encrypt_data.return_value = (b"encrypted", "key")
        blockchain_service.ipfs_client.upload_data.return_value = "QmHash"
        blockchain_service.zk_proof_generator.generate_proof.return_value = {"proof": "test"}
        
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db, \
             patch('suoke_blockchain_service.service.get_blockchain_client') as mock_blockchain:
            
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_client = AsyncMock()
            mock_client.store_health_data.side_effect = Exception("区块链交易失败")
            mock_blockchain.return_value = mock_client
            
            with pytest.raises(BlockchainServiceError, match="存储健康数据失败.*区块链交易失败"):
                await blockchain_service.store_health_data(
                    user_id="user123",
                    data={"heart_rate": 72},
                    data_type="heart_rate"
                )

    @pytest.mark.asyncio
    async def test_verify_health_data_blockchain_verification_failure(self, blockchain_service):
        """测试区块链验证失败的情况"""
        record_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db, \
             patch('suoke_blockchain_service.service.get_blockchain_client') as mock_blockchain:
            
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_health_record = MagicMock()
            mock_health_record.id = record_id
            mock_health_record.user_id = user_id
            mock_health_record.data_hash = "test_hash"
            mock_health_record.zkp_proof = {"proof": "test"}
            mock_health_record.public_inputs = [1, 2, 3]
            mock_health_record.verification_key = {"key": "test"}
            mock_health_record.ipfs_hash = "QmTestHash"
            mock_health_record.encrypted_data = b"encrypted_data"
            mock_health_record.record_metadata = {"zkp_circuit": "test_circuit"}
            mock_health_record.transaction = MagicMock()
            mock_health_record.transaction.transaction_hash = "0x123456789"
            
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_health_record
            mock_session.execute.return_value = mock_result

            mock_client = AsyncMock()
            mock_client.verify_health_data.return_value = False
            mock_blockchain.return_value = mock_client

            blockchain_service.zk_proof_verifier.verify_proof.return_value = True
            blockchain_service.ipfs_client.get_data.return_value = b"encrypted_data"

            result = await blockchain_service.verify_health_data(
                record_id=record_id,
                user_id=user_id
            )

            assert result["overall_valid"] is False
            assert result["blockchain_valid"] is False

    @pytest.mark.asyncio
    async def test_verify_health_data_zkp_verification_failure(self, blockchain_service):
        """测试零知识证明验证失败的情况"""
        record_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db, \
             patch('suoke_blockchain_service.service.get_blockchain_client') as mock_blockchain:
            
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_health_record = MagicMock()
            mock_health_record.id = record_id
            mock_health_record.user_id = user_id
            mock_health_record.data_hash = "test_hash"
            mock_health_record.zkp_proof = {"proof": "test"}
            mock_health_record.public_inputs = [1, 2, 3]
            mock_health_record.verification_key = {"key": "test"}
            mock_health_record.ipfs_hash = "QmTestHash"
            mock_health_record.encrypted_data = b"encrypted_data"
            mock_health_record.record_metadata = {"zkp_circuit": "test_circuit"}
            mock_health_record.transaction = MagicMock()
            mock_health_record.transaction.transaction_hash = "0x123456789"
            
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_health_record
            mock_session.execute.return_value = mock_result

            mock_client = AsyncMock()
            mock_client.verify_health_data.return_value = True
            mock_blockchain.return_value = mock_client

            blockchain_service.zk_proof_verifier.verify_proof.return_value = False
            blockchain_service.ipfs_client.get_data.return_value = b"encrypted_data"

            result = await blockchain_service.verify_health_data(
                record_id=record_id,
                user_id=user_id
            )

            assert result["overall_valid"] is False
            assert result["blockchain_valid"] is True
            assert result["zkp_valid"] is False
            assert result["ipfs_valid"] is True

    @pytest.mark.asyncio
    async def test_verify_health_data_ipfs_verification_failure(self, blockchain_service):
        """测试IPFS验证失败的情况"""
        record_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db, \
             patch('suoke_blockchain_service.service.get_blockchain_client') as mock_blockchain:
            
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_health_record = MagicMock()
            mock_health_record.id = record_id
            mock_health_record.user_id = user_id
            mock_health_record.data_hash = "test_hash"
            mock_health_record.zkp_proof = {"proof": "test"}
            mock_health_record.public_inputs = [1, 2, 3]
            mock_health_record.verification_key = {"key": "test"}
            mock_health_record.ipfs_hash = "QmTestHash"
            mock_health_record.encrypted_data = b"encrypted_data"
            mock_health_record.record_metadata = {"zkp_circuit": "test_circuit"}
            mock_health_record.transaction = MagicMock()
            mock_health_record.transaction.transaction_hash = "0x123456789"
            
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_health_record
            mock_session.execute.return_value = mock_result

            mock_client = AsyncMock()
            mock_client.verify_health_data.return_value = True
            mock_blockchain.return_value = mock_client
            blockchain_service.zk_proof_verifier.verify_proof.return_value = True

            blockchain_service.ipfs_client.get_data.return_value = b"different_data"

            result = await blockchain_service.verify_health_data(
                record_id=record_id,
                user_id=user_id
            )

            assert result["overall_valid"] is False
            assert result["blockchain_valid"] is True
            assert result["zkp_valid"] is True
            assert result["ipfs_valid"] is False

    @pytest.mark.asyncio
    async def test_grant_access_record_not_found(self, blockchain_service):
        """测试授权访问时记录不存在的情况"""
        owner_id = str(uuid.uuid4())
        grantee_id = str(uuid.uuid4())
        record_id = str(uuid.uuid4())
        
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db:
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result
            
            with pytest.raises(BlockchainServiceError, match="授权访问失败.*健康数据记录不存在"):
                await blockchain_service.grant_access(
                    owner_id=owner_id,
                    grantee_id=grantee_id,
                    record_id=record_id,
                    access_level="read"
                )

    @pytest.mark.asyncio
    async def test_grant_access_permission_denied(self, blockchain_service):
        """测试授权访问时权限不足的情况"""
        owner_id = str(uuid.uuid4())
        grantee_id = str(uuid.uuid4())
        record_id = str(uuid.uuid4())
        different_user_id = str(uuid.uuid4())
        
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db:
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_health_record = MagicMock()
            mock_health_record.id = record_id
            mock_health_record.user_id = different_user_id
            mock_health_record.data_hash = "test_hash"
            
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_health_record
            mock_session.execute.return_value = mock_result
            
            with pytest.raises(BlockchainServiceError, match="授权访问失败.*只有数据所有者可以授权访问"):
                await blockchain_service.grant_access(
                    owner_id=owner_id,
                    grantee_id=grantee_id,
                    record_id=record_id,
                    access_level="read"
                )

    @pytest.mark.asyncio
    async def test_grant_access_duplicate_grant(self, blockchain_service):
        """测试重复授权的情况"""
        owner_id = str(uuid.uuid4())
        grantee_id = str(uuid.uuid4())
        record_id = str(uuid.uuid4())
        
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db:
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_health_record = MagicMock()
            mock_health_record.id = record_id
            mock_health_record.user_id = owner_id
            mock_health_record.data_hash = "test_hash"
            
            mock_existing_grant = MagicMock()
            mock_existing_grant.is_active = True
            
            mock_session.execute.side_effect = [
                MagicMock(scalar_one_or_none=MagicMock(return_value=mock_health_record)),
                MagicMock(scalar_one_or_none=MagicMock(return_value=mock_existing_grant))
            ]
            
            with pytest.raises(BlockchainServiceError, match="授权访问失败.*已存在活跃的访问授权"):
                await blockchain_service.grant_access(
                    owner_id=owner_id,
                    grantee_id=grantee_id,
                    record_id=record_id,
                    access_level="read"
                )

    @pytest.mark.asyncio
    async def test_revoke_access_grant_not_found(self, blockchain_service):
        """测试撤销不存在的授权"""
        owner_id = str(uuid.uuid4())
        grantee_id = str(uuid.uuid4())
        record_id = str(uuid.uuid4())
        
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db:
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result
            
            with pytest.raises(BlockchainServiceError, match="撤销访问失败.*访问授权不存在"):
                await blockchain_service.revoke_access(
                    owner_id=owner_id,
                    grantee_id=grantee_id,
                    record_id=record_id
                )

    @pytest.mark.asyncio
    async def test_revoke_access_already_revoked(self, blockchain_service):
        """测试撤销已撤销的授权"""
        owner_id = str(uuid.uuid4())
        grantee_id = str(uuid.uuid4())
        record_id = str(uuid.uuid4())
        
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db:
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_grant = MagicMock()
            mock_grant.is_active = False
            mock_grant.revoked_at = datetime.utcnow()
            
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_grant
            mock_session.execute.return_value = mock_result
            
            with pytest.raises(BlockchainServiceError, match="撤销访问失败.*访问授权已被撤销"):
                await blockchain_service.revoke_access(
                    owner_id=owner_id,
                    grantee_id=grantee_id,
                    record_id=record_id
                )

    @pytest.mark.asyncio
    async def test_get_health_records_with_data_type_filter(self, blockchain_service):
        """测试按数据类型过滤获取健康记录"""
        user_id = str(uuid.uuid4())
        
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db:
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_record = MagicMock()
            mock_record.id = str(uuid.uuid4())
            mock_record.data_type = DataType.HEART_RATE
            mock_record.data_hash = "hash1"
            mock_record.ipfs_hash = "QmHash1"
            mock_record.created_at = datetime.utcnow()
            mock_record.zkp_proof = {"proof": "test"}
            mock_record.record_metadata = {}
            mock_record.transaction = MagicMock()
            mock_record.transaction.transaction_hash = "0x111"
            mock_record.transaction.status = TransactionStatus.CONFIRMED
            
            mock_records = [mock_record]
            
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = mock_records
            mock_session.execute.return_value = mock_result

            result = await blockchain_service.get_health_records(
                user_id=user_id,
                data_type="heart_rate",
                limit=10,
                offset=0
            )

            assert len(result["records"]) == 1
            assert result["records"][0]["data_type"] == "heart_rate"

    @pytest.mark.asyncio
    async def test_get_health_records_pagination(self, blockchain_service):
        """测试健康记录分页功能"""
        user_id = str(uuid.uuid4())
        
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db:
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_records = []
            for i in range(5):
                mock_record = MagicMock()
                mock_record.id = str(uuid.uuid4())
                mock_record.data_type = DataType.HEART_RATE
                mock_record.data_hash = f"hash{i}"
                mock_record.ipfs_hash = f"QmHash{i}"
                mock_record.created_at = datetime.utcnow()
                mock_record.zkp_proof = {"proof": f"test{i}"}
                mock_record.record_metadata = {}
                mock_record.transaction = MagicMock()
                mock_record.transaction.transaction_hash = f"0x{i}"
                mock_record.transaction.status = TransactionStatus.CONFIRMED
                mock_records.append(mock_record)
            
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = mock_records
            mock_session.execute.return_value = mock_result

            result = await blockchain_service.get_health_records(
                user_id=user_id,
                limit=3,
                offset=2
            )

            assert len(result["records"]) == 5
            assert result["limit"] == 3
            assert result["offset"] == 2
            assert result["has_more"] is True

    @pytest.mark.asyncio
    async def test_get_access_grants_as_grantee(self, blockchain_service):
        """测试获取作为被授权者的访问授权"""
        user_id = str(uuid.uuid4())
        
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db:
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_grant = MagicMock()
            mock_grant.id = str(uuid.uuid4())
            mock_grant.owner_id = str(uuid.uuid4())
            mock_grant.grantee_id = user_id
            mock_grant.health_record_id = str(uuid.uuid4())
            mock_grant.access_level = AccessLevel.READ
            mock_grant.permissions = {"read": True}
            mock_grant.granted_at = datetime.utcnow()
            mock_grant.expires_at = None
            mock_grant.is_active = True
            mock_grant.revoked_at = None
            mock_grant.revocation_reason = None
            mock_grant.transaction = MagicMock()
            mock_grant.transaction.transaction_hash = "0x333"
            mock_grant.health_record = MagicMock()
            mock_grant.health_record.data_type = DataType.BLOOD_PRESSURE
            mock_grant.health_record.created_at = datetime.utcnow()
            
            mock_grants = [mock_grant]
            
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = mock_grants
            mock_session.execute.return_value = mock_result

            result = await blockchain_service.get_access_grants(
                user_id=user_id,
                as_owner=False,
                active_only=True
            )

            assert len(result) == 1
            grant_data = result[0]
            assert grant_data["grantee_id"] == user_id
            assert grant_data["access_level"] == "read"
            assert grant_data["is_active"] is True

    def test_validate_store_request_edge_cases(self, blockchain_service):
        """测试存储请求验证的边界情况"""
        with pytest.raises(ValidationError, match="用户ID不能为空"):
            blockchain_service._validate_store_request(None, {"test": "data"}, "heart_rate")
        
        with pytest.raises(ValidationError, match="数据不能为空"):
            blockchain_service._validate_store_request("user123", None, "heart_rate")
        
        with pytest.raises(ValidationError, match="数据类型不能为空"):
            blockchain_service._validate_store_request("user123", {"test": "data"}, None)

    def test_generate_data_hash_edge_cases(self, blockchain_service):
        """测试数据哈希生成的边界情况"""
        hash1 = blockchain_service._generate_data_hash({})
        assert len(hash1) == 64
        
        data_with_none = {"key1": "value1", "key2": None}
        hash2 = blockchain_service._generate_data_hash(data_with_none)
        assert len(hash2) == 64
        
        nested_data = {"level1": {"level2": {"value": "test"}}}
        hash3 = blockchain_service._generate_data_hash(nested_data)
        assert len(hash3) == 64

    @pytest.mark.asyncio
    async def test_create_audit_log_with_error(self, blockchain_service):
        """测试创建包含错误信息的审计日志"""
        mock_session = AsyncMock()
        
        await blockchain_service._create_audit_log(
            session=mock_session,
            user_id="user123",
            action="failed_action",
            resource_type="test_resource",
            resource_id="test_id",
            success=False,
            error_message="操作失败",
            audit_metadata={"error_code": "E001"}
        )
        
        mock_session.add.assert_called_once()
        
        added_object = mock_session.add.call_args[0][0]
        assert added_object.success is False
        assert added_object.error_message == "操作失败"
        assert added_object.audit_metadata == {"error_code": "E001"}

    @pytest.mark.asyncio
    async def test_create_audit_log_with_old_and_new_values(self, blockchain_service):
        """测试创建包含新旧值的审计日志"""
        mock_session = AsyncMock()
        
        old_values = {"status": "pending"}
        new_values = {"status": "confirmed"}
        
        await blockchain_service._create_audit_log(
            session=mock_session,
            user_id="user123",
            action="update_status",
            resource_type="transaction",
            resource_id="tx123",
            old_values=old_values,
            new_values=new_values
        )
        
        added_object = mock_session.add.call_args[0][0]
        assert added_object.old_values == old_values
        assert added_object.new_values == new_values


class TestBlockchainServiceIntegration:
    """区块链服务集成测试"""

    @pytest.mark.asyncio
    async def test_full_data_lifecycle(self, blockchain_service):
        """测试完整的数据生命周期"""
        user_id = str(uuid.uuid4())
        grantee_id = str(uuid.uuid4())
        health_data = {"heart_rate": 72, "timestamp": "2024-01-01T10:00:00Z"}
        
        blockchain_service.encryption_service.encrypt_data.return_value = (b"encrypted_data", "encryption_key")
        blockchain_service.ipfs_client.upload_data.return_value = "QmTestHash"
        blockchain_service.zk_proof_generator.generate_proof.return_value = {
            "proof": {"a": [1, 2], "b": [3, 4], "c": [5, 6]},
            "public_inputs": [1, 2, 3],
            "verification_key": {"alpha": [1, 2]}
        }
        blockchain_service.zk_proof_verifier.verify_proof.return_value = True
        blockchain_service.ipfs_client.get_data.return_value = b"encrypted_data"
        
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db, \
             patch('suoke_blockchain_service.service.get_blockchain_client') as mock_blockchain:
            
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_client = AsyncMock()
            mock_client.store_health_data.return_value = "0x123456789"
            mock_client.verify_health_data.return_value = True
            mock_client.grant_access.return_value = "0x987654321"
            mock_client.revoke_access.return_value = "0x111222333"
            mock_blockchain.return_value = mock_client
            
            store_result = await blockchain_service.store_health_data(
                user_id=user_id,
                data=health_data,
                data_type="heart_rate"
            )
            
            assert store_result["status"] == "pending"
            record_id = store_result["record_id"]
            
            mock_health_record = MagicMock()
            mock_health_record.id = record_id
            mock_health_record.user_id = user_id
            mock_health_record.data_hash = store_result["data_hash"]
            mock_health_record.zkp_proof = store_result["zkp_proof"]
            mock_health_record.public_inputs = [1, 2, 3]
            mock_health_record.verification_key = {"alpha": [1, 2]}
            mock_health_record.ipfs_hash = "QmTestHash"
            mock_health_record.encrypted_data = b"encrypted_data"
            mock_health_record.record_metadata = {"zkp_circuit": "health_data_heart_rate"}
            mock_health_record.transaction = MagicMock()
            mock_health_record.transaction.transaction_hash = "0x123456789"
            
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_health_record
            mock_session.execute.return_value = mock_result
            
            verify_result = await blockchain_service.verify_health_data(
                record_id=record_id,
                user_id=user_id
            )
            
            assert verify_result["overall_valid"] is True
            
            mock_session.execute.side_effect = [
                MagicMock(scalar_one_or_none=MagicMock(return_value=mock_health_record)),
                MagicMock(scalar_one_or_none=MagicMock(return_value=None))
            ]
            
            grant_result = await blockchain_service.grant_access(
                owner_id=user_id,
                grantee_id=grantee_id,
                record_id=record_id,
                access_level="read"
            )
            
            assert grant_result["status"] == "pending"
            grant_id = grant_result["grant_id"]
            
            mock_grant = MagicMock()
            mock_grant.id = grant_id
            mock_grant.owner_id = user_id
            mock_grant.grantee_id = grantee_id
            mock_grant.health_record_id = record_id
            mock_grant.is_active = True
            mock_grant.revoked_at = None
            
            mock_session.execute.return_value = MagicMock(
                scalar_one_or_none=MagicMock(return_value=mock_grant)
            )
            
            revoke_result = await blockchain_service.revoke_access(
                owner_id=user_id,
                grantee_id=grantee_id,
                record_id=record_id,
                reason="测试完成"
            )
            
            assert revoke_result["status"] == "pending"
            assert revoke_result["reason"] == "测试完成"
            
            assert mock_client.store_health_data.called
            assert mock_client.verify_health_data.called
            assert mock_client.grant_access.called
            assert mock_client.revoke_access.called


class TestBlockchainServicePerformance:
    """区块链服务性能测试"""

    @pytest.mark.asyncio
    async def test_concurrent_store_operations(self, blockchain_service):
        """测试并发存储操作"""
        import asyncio
        
        blockchain_service.encryption_service.encrypt_data.return_value = (b"encrypted", "key")
        blockchain_service.ipfs_client.upload_data.return_value = "QmHash"
        blockchain_service.zk_proof_generator.generate_proof.return_value = {"proof": "test"}
        
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db, \
             patch('suoke_blockchain_service.service.get_blockchain_client') as mock_blockchain:
            
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_client = AsyncMock()
            mock_client.store_health_data.return_value = "0x123456789"
            mock_blockchain.return_value = mock_client
            
            tasks = []
            for i in range(10):
                task = blockchain_service.store_health_data(
                    user_id=f"user{i}",
                    data={"heart_rate": 70 + i},
                    data_type="heart_rate"
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    pytest.fail(f"并发操作失败: {result}")
                assert result["status"] == "pending"

    @pytest.mark.asyncio
    async def test_large_data_handling(self, blockchain_service):
        """测试大数据处理"""
        large_data = {
            "measurements": [{"value": i, "timestamp": f"2024-01-01T{i:02d}:00:00Z"} for i in range(1000)],
            "metadata": {"description": "大量测量数据" * 100}
        }
        
        blockchain_service.encryption_service.encrypt_data.return_value = (b"encrypted_large_data", "key")
        blockchain_service.ipfs_client.upload_data.return_value = "QmLargeHash"
        blockchain_service.zk_proof_generator.generate_proof.return_value = {"proof": "large_proof"}
        
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db, \
             patch('suoke_blockchain_service.service.get_blockchain_client') as mock_blockchain:
            
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_client = AsyncMock()
            mock_client.store_health_data.return_value = "0x123456789"
            mock_blockchain.return_value = mock_client
            
            result = await blockchain_service.store_health_data(
                user_id="user123",
                data=large_data,
                data_type="comprehensive"
            )
            
            assert result["status"] == "pending"
            assert blockchain_service.encryption_service.encrypt_data.called
            assert blockchain_service.ipfs_client.upload_data.called 