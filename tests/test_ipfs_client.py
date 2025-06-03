"""
IPFS客户端测试模块

测试IPFS数据存储和检索功能。
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json

from suoke_blockchain_service.ipfs_client import IPFSClient
from suoke_blockchain_service.exceptions import IPFSError


class TestIPFSClient:
    """IPFS客户端测试类"""

    @pytest.fixture
    def ipfs_client(self):
        """创建IPFS客户端实例"""
        return IPFSClient()

    @pytest.mark.asyncio
    async def test_upload_data_success(self, ipfs_client):
        """测试成功上传数据"""
        test_data = {"test": "data", "number": 123}
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"Hash": "QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"}
            mock_post.return_value = mock_response
            
            result = await ipfs_client.upload_data(test_data)
            
            assert result == "QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"

    @pytest.mark.asyncio
    async def test_upload_data_failure(self, ipfs_client):
        """测试上传数据失败"""
        test_data = {"test": "data"}
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_post.return_value = mock_response
            
            with pytest.raises(IPFSError, match="IPFS上传失败"):
                await ipfs_client.upload_data(test_data)

    @pytest.mark.asyncio
    async def test_get_data_success(self, ipfs_client):
        """测试成功获取数据"""
        test_hash = "QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"
        expected_data = {"test": "data", "number": 123}
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = json.dumps(expected_data).encode()
            mock_post.return_value = mock_response
            
            result = await ipfs_client.get_data(test_hash)
            
            assert result == json.dumps(expected_data).encode()

    @pytest.mark.asyncio
    async def test_get_data_not_found(self, ipfs_client):
        """测试获取不存在的数据"""
        test_hash = "QmInvalidHash"
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.text = "Not Found"
            mock_post.return_value = mock_response
            
            with pytest.raises(IPFSError, match="IPFS数据获取失败"):
                await ipfs_client.get_data(test_hash)

    @pytest.mark.asyncio
    async def test_pin_data_success(self, ipfs_client):
        """测试成功固定数据"""
        test_hash = "QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"Pins": [test_hash]}
            mock_post.return_value = mock_response
            
            result = await ipfs_client.pin_data(test_hash)
            
            assert result is True

    @pytest.mark.asyncio
    async def test_unpin_data_success(self, ipfs_client):
        """测试成功取消固定数据"""
        test_hash = "QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"Pins": [test_hash]}
            mock_post.return_value = mock_response
            
            result = await ipfs_client.unpin_data(test_hash)
            
            assert result is True

    @pytest.mark.asyncio
    async def test_get_node_info_success(self, ipfs_client):
        """测试成功获取节点信息"""
        expected_info = {
            "ID": "QmNodeId",
            "PublicKey": "public_key",
            "Addresses": ["/ip4/127.0.0.1/tcp/4001"],
            "AgentVersion": "go-ipfs/0.12.0",
            "ProtocolVersion": "ipfs/0.1.0"
        }
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected_info
            mock_post.return_value = mock_response
            
            result = await ipfs_client.get_node_info()
            
            assert result == expected_info

    @pytest.mark.asyncio
    async def test_check_connection_success(self, ipfs_client):
        """测试连接检查成功"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"ID": "QmNodeId"}
            mock_post.return_value = mock_response
            
            result = await ipfs_client.check_connection()
            
            assert result is True

    @pytest.mark.asyncio
    async def test_check_connection_failure(self, ipfs_client):
        """测试连接检查失败"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.side_effect = Exception("Connection failed")
            
            result = await ipfs_client.check_connection()
            
            assert result is False

    @pytest.mark.asyncio
    async def test_upload_large_data(self, ipfs_client):
        """测试上传大数据"""
        # 创建大数据对象
        large_data = {"data": "x" * (1024 * 1024)}  # 1MB数据
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"Hash": "QmLargeDataHash"}
            mock_post.return_value = mock_response
            
            result = await ipfs_client.upload_data(large_data)
            
            assert result == "QmLargeDataHash"

    @pytest.mark.asyncio
    async def test_upload_binary_data(self, ipfs_client):
        """测试上传二进制数据"""
        binary_data = b"binary_test_data"
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"Hash": "QmBinaryDataHash"}
            mock_post.return_value = mock_response
            
            result = await ipfs_client.upload_binary_data(binary_data)
            
            assert result == "QmBinaryDataHash"

    @pytest.mark.asyncio
    async def test_get_data_stats(self, ipfs_client):
        """测试获取数据统计信息"""
        test_hash = "QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"
        expected_stats = {
            "Hash": test_hash,
            "Size": 1024,
            "CumulativeSize": 1024,
            "Blocks": 1,
            "Type": "file"
        }
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected_stats
            mock_post.return_value = mock_response
            
            result = await ipfs_client.get_data_stats(test_hash)
            
            assert result == expected_stats

    @pytest.mark.asyncio
    async def test_validate_hash(self, ipfs_client):
        """测试哈希验证"""
        # 有效的IPFS哈希
        valid_hash = "QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"
        assert ipfs_client._validate_hash(valid_hash) is True
        
        # 无效的哈希
        invalid_hashes = [
            "",
            "invalid_hash",
            "Qm",  # 太短
            "QmInvalidHashTooLong" * 10,  # 太长
            "123456789012345678901234567890123456789012345678"  # 不是base58
        ]
        
        for invalid_hash in invalid_hashes:
            assert ipfs_client._validate_hash(invalid_hash) is False

    @pytest.mark.asyncio
    async def test_timeout_handling(self, ipfs_client):
        """测试超时处理"""
        test_data = {"test": "data"}
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.side_effect = Exception("Timeout")
            
            with pytest.raises(IPFSError, match="IPFS操作超时或连接失败"):
                await ipfs_client.upload_data(test_data) 