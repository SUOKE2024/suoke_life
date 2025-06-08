"""
test_ipfs_simple - 索克生活项目模块
"""

from suoke_blockchain_service.exceptions import IPFSError
from suoke_blockchain_service.ipfs_client import IPFSClient
from unittest.mock import patch, MagicMock, AsyncMock
import pytest

"""
IPFS客户端测试模块

测试IPFS数据存储和检索功能。
"""




class TestIPFSClient:
    """IPFS客户端测试类"""

    @pytest.fixture
    def ipfs_client(self):
        """创建IPFS客户端实例"""
        return IPFSClient()

    @pytest.mark.asyncio
    async def test_upload_data_success(self, ipfs_client):
        """测试成功上传数据"""
        test_data = b"test data for upload"

        with patch.object(ipfs_client, '_upload_to_ipfs', return_value="QmTest123") as mock_upload:
            result = await ipfs_client.upload_data(test_data)

            assert result == "QmTest123"
            mock_upload.assert_called_once_with(test_data)

    @pytest.mark.asyncio
    async def test_get_data_success(self, ipfs_client):
        """测试成功获取数据"""
        test_hash = "QmTest123"
        expected_data = b"test data"

        with patch.object(ipfs_client, '_get_from_ipfs', return_value=expected_data) as mock_get:
            result = await ipfs_client.get_data(test_hash)

            assert result == expected_data
            mock_get.assert_called_once_with(test_hash)

    @pytest.mark.asyncio
    async def test_upload_empty_data(self, ipfs_client):
        """测试上传空数据"""
        with pytest.raises(IPFSError, match="数据不能为空"):
            await ipfs_client.upload_data(b"")

    @pytest.mark.asyncio
    async def test_get_invalid_hash(self, ipfs_client):
        """测试获取无效哈希的数据"""
        with pytest.raises(IPFSError, match="无效的IPFS哈希"):
            await ipfs_client.get_data("invalid_hash")

    @pytest.mark.asyncio
    async def test_upload_large_data(self, ipfs_client):
        """测试上传大数据"""
        # 创建超过最大限制的数据
        large_data = b"x" * (100 * 1024 * 1024 + 1)  # 100MB + 1 byte

        with pytest.raises(IPFSError, match="数据大小超过限制"):
            await ipfs_client.upload_data(large_data)

    @pytest.mark.asyncio
    async def test_connection_error(self, ipfs_client):
        """测试连接错误"""
        test_data = b"test data"

        with patch.object(ipfs_client, '_upload_to_ipfs', side_effect=Exception("Connection failed")):
            with pytest.raises(IPFSError, match="IPFS上传失败"):
                await ipfs_client.upload_data(test_data)

    def test_validate_hash_valid(self, ipfs_client):
        """测试验证有效哈希"""
        valid_hash = "QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"
        assert ipfs_client._validate_hash(valid_hash) is True

    def test_validate_hash_invalid(self, ipfs_client):
        """测试验证无效哈希"""
        invalid_hash = "invalid_hash"
        assert ipfs_client._validate_hash(invalid_hash) is False 