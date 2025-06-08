"""
test_grpc_server - 索克生活项目模块
"""

from grpc import aio
from suoke_blockchain_service import blockchain_pb2, blockchain_pb2_grpc
from suoke_blockchain_service.exceptions import ValidationError, NotFoundError
from suoke_blockchain_service.grpc_server import BlockchainServicer
from unittest.mock import AsyncMock, MagicMock, patch
import grpc
import pytest

"""
gRPC服务器测试模块

测试gRPC服务器的接口实现。
"""




class TestBlockchainServicer:
    """区块链gRPC服务器测试类"""

    @pytest.fixture
    def servicer(self):
        """创建gRPC服务器实例"""
        return BlockchainServicer()

    @pytest.fixture
    def mock_context(self):
        """创建模拟gRPC上下文"""
        context = MagicMock()
        context.set_code = MagicMock()
        context.set_details = MagicMock()
        return context

    @pytest.mark.asyncio
    async def test_store_health_data_success(self, servicer, mock_context):
        """测试成功存储健康数据"""
        request = blockchain_pb2.StoreHealthDataRequest(
            user_id="test-user-123",
            data='{"heart_rate": 72, "timestamp": "2024-01-01T00:00:00Z"}',
            data_type="heart_rate"
        )

        with patch.object(servicer.blockchain_service, 'store_health_data') as mock_store:
            mock_store.return_value = {
                "record_id": "record-123",
                "transaction_id": "tx-456",
                "transaction_hash": "0x1234567890abcdef",
                "status": "pending"
            }

            response = await servicer.StoreHealthData(request, mock_context)

            assert response.record_id == "record-123"
            assert response.transaction_id == "tx-456"
            assert response.transaction_hash == "0x1234567890abcdef"
            assert response.status == "pending"

    @pytest.mark.asyncio
    async def test_store_health_data_validation_error(self, servicer, mock_context):
        """测试存储健康数据验证错误"""
        request = blockchain_pb2.StoreHealthDataRequest(
            user_id="",  # 空用户ID
            data='{"heart_rate": 72}',
            data_type="heart_rate"
        )

        with patch.object(servicer.blockchain_service, 'store_health_data') as mock_store:
            mock_store.side_effect = ValidationError("用户ID不能为空")

            response = await servicer.StoreHealthData(request, mock_context)

            # 验证错误响应
            mock_context.set_code.assert_called_with(grpc.StatusCode.INVALID_ARGUMENT)
            mock_context.set_details.assert_called_with("用户ID不能为空")

    @pytest.mark.asyncio
    async def test_verify_health_data_success(self, servicer, mock_context):
        """测试成功验证健康数据"""
        request = blockchain_pb2.VerifyHealthDataRequest(
            record_id="record-123",
            user_id="test-user-123"
        )

        with patch.object(servicer.blockchain_service, 'verify_health_data') as mock_verify:
            mock_verify.return_value = {
                "blockchain_valid": True,
                "zkp_valid": True,
                "ipfs_valid": True,
                "overall_valid": True,
                "verification_details": {
                    "transaction_hash": "0x1234567890abcdef",
                    "block_number": 12345
                }
            }

            response = await servicer.VerifyHealthData(request, mock_context)

            assert response.blockchain_valid is True
            assert response.zkp_valid is True
            assert response.ipfs_valid is True
            assert response.overall_valid is True

    @pytest.mark.asyncio
    async def test_verify_health_data_not_found(self, servicer, mock_context):
        """测试验证不存在的健康数据"""
        request = blockchain_pb2.VerifyHealthDataRequest(
            record_id="nonexistent-record",
            user_id="test-user-123"
        )

        with patch.object(servicer.blockchain_service, 'verify_health_data') as mock_verify:
            mock_verify.side_effect = NotFoundError("健康数据记录不存在")

            response = await servicer.VerifyHealthData(request, mock_context)

            # 验证错误响应
            mock_context.set_code.assert_called_with(grpc.StatusCode.NOT_FOUND)
            mock_context.set_details.assert_called_with("健康数据记录不存在")

    @pytest.mark.asyncio
    async def test_grant_access_success(self, servicer, mock_context):
        """测试成功授权访问"""
        request = blockchain_pb2.GrantAccessRequest(
            owner_id="owner-123",
            grantee_id="grantee-456",
            record_id="record-789",
            access_level="read",
            expires_at=1234567890
        )

        with patch.object(servicer.blockchain_service, 'grant_access') as mock_grant:
            mock_grant.return_value = {
                "grant_id": "grant-123",
                "transaction_hash": "0x1234567890abcdef",
                "expires_at": "2024-01-01T00:00:00Z"
            }

            response = await servicer.GrantAccess(request, mock_context)

            assert response.grant_id == "grant-123"
            assert response.transaction_hash == "0x1234567890abcdef"
            assert response.expires_at == "2024-01-01T00:00:00Z"

    @pytest.mark.asyncio
    async def test_revoke_access_success(self, servicer, mock_context):
        """测试成功撤销访问"""
        request = blockchain_pb2.RevokeAccessRequest(
            owner_id="owner-123",
            grantee_id="grantee-456",
            record_id="record-789",
            reason="测试撤销"
        )

        with patch.object(servicer.blockchain_service, 'revoke_access') as mock_revoke:
            mock_revoke.return_value = {
                "grant_id": "grant-123",
                "revoked_at": "2024-01-01T00:00:00Z",
                "reason": "测试撤销"
            }

            response = await servicer.RevokeAccess(request, mock_context)

            assert response.grant_id == "grant-123"
            assert response.revoked_at == "2024-01-01T00:00:00Z"
            assert response.reason == "测试撤销"

    @pytest.mark.asyncio
    async def test_get_health_records_success(self, servicer, mock_context):
        """测试成功获取健康记录"""
        request = blockchain_pb2.GetHealthRecordsRequest(
            user_id="test-user-123",
            data_type="heart_rate",
            limit=10,
            offset=0
        )

        with patch.object(servicer.blockchain_service, 'get_health_records') as mock_get:
            mock_get.return_value = {
                "total_count": 2,
                "has_more": False,
                "records": [
                    {
                        "id": "record-1",
                        "data_type": "heart_rate",
                        "data_hash": "hash1",
                        "ipfs_hash": "QmTest1",
                        "created_at": "2024-01-01T00:00:00Z",
                        "has_zkp": True,
                        "transaction_status": "confirmed"
                    },
                    {
                        "id": "record-2",
                        "data_type": "heart_rate",
                        "data_hash": "hash2",
                        "ipfs_hash": "QmTest2",
                        "created_at": "2024-01-02T00:00:00Z",
                        "has_zkp": False,
                        "transaction_status": "pending"
                    }
                ]
            }

            response = await servicer.GetHealthRecords(request, mock_context)

            assert response.total_count == 2
            assert response.has_more is False
            assert len(response.records) == 2
            assert response.records[0].id == "record-1"
            assert response.records[0].has_zkp is True

    @pytest.mark.asyncio
    async def test_get_access_grants_success(self, servicer, mock_context):
        """测试成功获取访问授权"""
        request = blockchain_pb2.GetAccessGrantsRequest(
            user_id="test-user-123",
            as_owner=True,
            active_only=True
        )

        with patch.object(servicer.blockchain_service, 'get_access_grants') as mock_get:
            mock_get.return_value = [
                {
                    "id": "grant-1",
                    "grantee_id": "grantee-456",
                    "health_record_id": "record-789",
                    "access_level": "read",
                    "granted_at": "2024-01-01T00:00:00Z",
                    "expires_at": "2024-01-02T00:00:00Z",
                    "is_active": True
                }
            ]

            response = await servicer.GetAccessGrants(request, mock_context)

            assert len(response.grants) == 1
            grant = response.grants[0]
            assert grant.id == "grant-1"
            assert grant.grantee_id == "grantee-456"
            assert grant.access_level == "read"
            assert grant.is_active is True

    @pytest.mark.asyncio
    async def test_health_check_success(self, servicer, mock_context):
        """测试健康检查成功"""
        request = blockchain_pb2.HealthCheckRequest()

        with patch.object(servicer.blockchain_service, 'health_check') as mock_health:
            mock_health.return_value = {
                "status": "healthy",
                "timestamp": "2024-01-01T00:00:00Z",
                "version": "1.0.0",
                "components": {
                    "database": "healthy",
                    "blockchain": "healthy",
                    "ipfs": "healthy"
                }
            }

            response = await servicer.HealthCheck(request, mock_context)

            assert response.status == "healthy"
            assert response.version == "1.0.0"
            assert len(response.components) == 3

    @pytest.mark.asyncio
    async def test_internal_server_error(self, servicer, mock_context):
        """测试内部服务器错误"""
        request = blockchain_pb2.StoreHealthDataRequest(
            user_id="test-user-123",
            data='{"heart_rate": 72}',
            data_type="heart_rate"
        )

        with patch.object(servicer.blockchain_service, 'store_health_data') as mock_store:
            mock_store.side_effect = Exception("Internal error")

            response = await servicer.StoreHealthData(request, mock_context)

            # 验证内部错误响应
            mock_context.set_code.assert_called_with(grpc.StatusCode.INTERNAL)
            mock_context.set_details.assert_called_with("内部服务器错误")

    @pytest.mark.asyncio
    async def test_request_validation(self, servicer):
        """测试请求验证"""
        # 测试空请求
        empty_request = blockchain_pb2.StoreHealthDataRequest()

        result = servicer._validate_store_request(empty_request)
        assert result is False

        # 测试有效请求
        valid_request = blockchain_pb2.StoreHealthDataRequest(
            user_id="test-user-123",
            data='{"heart_rate": 72}',
            data_type="heart_rate"
        )

        result = servicer._validate_store_request(valid_request)
        assert result is True

    @pytest.mark.asyncio
    async def test_response_formatting(self, servicer):
        """测试响应格式化"""
        # 测试健康记录响应格式化
        record_data = {
            "id": "record-123",
            "data_type": "heart_rate",
            "data_hash": "hash123",
            "ipfs_hash": "QmTest",
            "created_at": "2024-01-01T00:00:00Z",
            "has_zkp": True,
            "transaction_status": "confirmed"
        }

        response = servicer._format_health_record_response(record_data)

        assert isinstance(response, blockchain_pb2.HealthRecord)
        assert response.id == "record-123"
        assert response.data_type == "heart_rate"
        assert response.has_zkp is True

    @pytest.mark.asyncio
    async def test_error_handling_middleware(self, servicer, mock_context):
        """测试错误处理中间件"""
        # 测试不同类型的异常处理
        test_cases = [
            (ValidationError("验证错误"), grpc.StatusCode.INVALID_ARGUMENT),
            (NotFoundError("未找到"), grpc.StatusCode.NOT_FOUND),
            (PermissionError("权限错误"), grpc.StatusCode.PERMISSION_DENIED),
            (Exception("未知错误"), grpc.StatusCode.INTERNAL)
        ]

        for exception, expected_code in test_cases:
            with patch.object(servicer.blockchain_service, 'store_health_data') as mock_store:
                mock_store.side_effect = exception

                request = blockchain_pb2.StoreHealthDataRequest(
                    user_id="test-user-123",
                    data='{"heart_rate": 72}',
                    data_type="heart_rate"
                )

                await servicer.StoreHealthData(request, mock_context)

                # 验证正确的错误码被设置
                mock_context.set_code.assert_called_with(expected_code) 