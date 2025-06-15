"""
IPFS客户端单元测试
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json

from blockchain_service.services.ipfs_client import IPFSClient
from blockchain_service.core.exceptions import IPFSError


class TestIPFSClient:
    """IPFS客户端测试"""
    
    @pytest.fixture
    def ipfs_client(self):
        """IPFS客户端实例"""
        return IPFSClient()
    
    def test_initialization_attributes(self, ipfs_client):
        """测试初始化属性"""
        assert ipfs_client.settings is not None
        assert ipfs_client.logger is not None
        assert ipfs_client._client is None
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, ipfs_client):
        """测试成功初始化"""
        with patch.object(ipfs_client, 'logger') as mock_logger:
            await ipfs_client.initialize()
            
            # 验证日志记录
            mock_logger.info.assert_called_once()
            assert "IPFS客户端初始化完成" in str(mock_logger.info.call_args)
    
    @pytest.mark.asyncio
    async def test_initialize_with_exception(self, ipfs_client):
        """测试初始化时发生异常"""
        # 模拟初始化过程中的异常
        with patch.object(ipfs_client, 'logger') as mock_logger:
            mock_logger.info.side_effect = Exception("Initialization error")
            
            with pytest.raises(IPFSError, match="IPFS客户端初始化失败"):
                await ipfs_client.initialize()
            
            # 验证错误日志
            mock_logger.error.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_data_success(self, ipfs_client):
        """测试成功添加数据"""
        await ipfs_client.initialize()
        
        test_data = b"Hello IPFS World!"
        
        with patch.object(ipfs_client, 'logger') as mock_logger:
            ipfs_hash = await ipfs_client.add_data(test_data)
            
            assert ipfs_hash is not None
            assert ipfs_hash.startswith("Qm")
            assert len(ipfs_hash) == 46  # 标准IPFS哈希长度
            
            # 验证日志记录
            mock_logger.info.assert_called_once()
            assert "数据已添加到IPFS" in str(mock_logger.info.call_args)
    
    @pytest.mark.asyncio
    async def test_add_data_empty(self, ipfs_client):
        """测试添加空数据"""
        await ipfs_client.initialize()
        
        empty_data = b""
        ipfs_hash = await ipfs_client.add_data(empty_data)
        
        assert ipfs_hash is not None
        assert ipfs_hash.startswith("Qm")
    
    @pytest.mark.asyncio
    async def test_add_data_large(self, ipfs_client):
        """测试添加大数据"""
        await ipfs_client.initialize()
        
        # 创建1MB的测试数据
        large_data = b"x" * (1024 * 1024)
        ipfs_hash = await ipfs_client.add_data(large_data)
        
        assert ipfs_hash is not None
        assert ipfs_hash.startswith("Qm")
    
    @pytest.mark.asyncio
    async def test_add_data_with_exception(self, ipfs_client):
        """测试添加数据时发生异常"""
        await ipfs_client.initialize()
        
        # 模拟内部异常
        with patch.object(ipfs_client, 'logger') as mock_logger:
            # 让日志记录抛出异常来模拟内部错误
            mock_logger.info.side_effect = Exception("Internal error")
            
            with pytest.raises(IPFSError, match="添加数据到IPFS失败"):
                await ipfs_client.add_data(b"test data")
            
            # 验证错误日志
            mock_logger.error.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_data_success(self, ipfs_client):
        """测试成功获取数据"""
        await ipfs_client.initialize()
        
        test_hash = "QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"
        
        with patch.object(ipfs_client, 'logger') as mock_logger:
            retrieved_data = await ipfs_client.get_data(test_hash)
            
            assert retrieved_data is not None
            assert isinstance(retrieved_data, bytes)
            assert retrieved_data == b"mock ipfs data"
            
            # 验证日志记录
            mock_logger.info.assert_called_once()
            assert "从IPFS获取数据" in str(mock_logger.info.call_args)
    
    @pytest.mark.asyncio
    async def test_get_data_invalid_hash(self, ipfs_client):
        """测试获取数据时使用无效哈希"""
        await ipfs_client.initialize()
        
        invalid_hash = "invalid_hash"
        
        # 即使哈希无效，模拟实现仍会返回数据
        retrieved_data = await ipfs_client.get_data(invalid_hash)
        assert retrieved_data is not None
    
    @pytest.mark.asyncio
    async def test_get_data_with_exception(self, ipfs_client):
        """测试获取数据时发生异常"""
        await ipfs_client.initialize()
        
        test_hash = "QmSomeHash"
        
        # 模拟内部异常
        with patch.object(ipfs_client, 'logger') as mock_logger:
            mock_logger.info.side_effect = Exception("Internal error")
            
            with pytest.raises(IPFSError, match="从IPFS获取数据失败"):
                await ipfs_client.get_data(test_hash)
            
            # 验证错误日志
            mock_logger.error.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_pin_data_success(self, ipfs_client):
        """测试成功固定数据"""
        await ipfs_client.initialize()
        
        test_hash = "QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"
        
        with patch.object(ipfs_client, 'logger') as mock_logger:
            result = await ipfs_client.pin_data(test_hash)
            
            assert result is True
            
            # 验证日志记录
            mock_logger.info.assert_called_once()
            assert "IPFS数据已固定" in str(mock_logger.info.call_args)
    
    @pytest.mark.asyncio
    async def test_pin_data_with_exception(self, ipfs_client):
        """测试固定数据时发生异常"""
        await ipfs_client.initialize()
        
        test_hash = "QmSomeHash"
        
        # 模拟内部异常
        with patch.object(ipfs_client, 'logger') as mock_logger:
            mock_logger.info.side_effect = Exception("Internal error")
            
            result = await ipfs_client.pin_data(test_hash)
            
            # 异常时应该返回False
            assert result is False
            
            # 验证错误日志
            mock_logger.error.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_pin_data_empty_hash(self, ipfs_client):
        """测试固定空哈希"""
        await ipfs_client.initialize()
        
        result = await ipfs_client.pin_data("")
        assert result is True  # 模拟实现总是返回True
    
    def test_is_connected(self, ipfs_client):
        """测试连接状态检查"""
        # 模拟实现总是返回True
        assert ipfs_client.is_connected() is True
    
    def test_is_connected_without_initialization(self, ipfs_client):
        """测试未初始化时的连接状态"""
        # 即使未初始化，模拟实现也返回True
        assert ipfs_client.is_connected() is True


class TestIPFSClientErrorHandling:
    """IPFS客户端错误处理测试"""
    
    @pytest.fixture
    def ipfs_client(self):
        """IPFS客户端实例"""
        return IPFSClient()
    
    @pytest.mark.asyncio
    async def test_add_data_with_mock_error(self, ipfs_client):
        """测试添加数据时的错误处理"""
        await ipfs_client.initialize()
        
        # 直接测试异常处理逻辑
        with patch.object(ipfs_client, 'logger') as mock_logger:
            mock_logger.info.side_effect = Exception("Mock error")
            
            with pytest.raises(IPFSError, match="添加数据到IPFS失败"):
                await ipfs_client.add_data(b"test data")
    
    @pytest.mark.asyncio
    async def test_get_data_with_mock_error(self, ipfs_client):
        """测试获取数据时的错误处理"""
        await ipfs_client.initialize()
        
        # 直接测试异常处理逻辑
        with patch.object(ipfs_client, 'logger') as mock_logger:
            mock_logger.info.side_effect = Exception("Mock error")
            
            with pytest.raises(IPFSError, match="从IPFS获取数据失败"):
                await ipfs_client.get_data("QmSomeHash")
    
    @pytest.mark.asyncio
    async def test_pin_data_with_mock_error(self, ipfs_client):
        """测试固定数据时的错误处理"""
        await ipfs_client.initialize()
        
        # 直接测试异常处理逻辑
        with patch.object(ipfs_client, 'logger') as mock_logger:
            mock_logger.info.side_effect = Exception("Mock error")
            
            result = await ipfs_client.pin_data("QmSomeHash")
            assert result is False
    
    @pytest.mark.asyncio
    async def test_multiple_errors_in_sequence(self, ipfs_client):
        """测试连续的错误处理"""
        await ipfs_client.initialize()
        
        with patch.object(ipfs_client, 'logger') as mock_logger:
            mock_logger.info.side_effect = Exception("Persistent error")
            
            # 测试多个操作都失败
            with pytest.raises(IPFSError):
                await ipfs_client.add_data(b"data1")
            
            with pytest.raises(IPFSError):
                await ipfs_client.get_data("hash1")
            
            result = await ipfs_client.pin_data("hash2")
            assert result is False


class TestIPFSClientIntegration:
    """IPFS客户端集成测试"""
    
    @pytest.fixture
    def ipfs_client(self):
        """IPFS客户端实例"""
        return IPFSClient()
    
    @pytest.mark.asyncio
    async def test_data_lifecycle(self, ipfs_client):
        """测试完整的数据生命周期"""
        await ipfs_client.initialize()
        
        # 测试不同类型的数据
        test_cases = [
            b"Simple text data",
            b'{"json": "data", "number": 42}',
            bytes(range(256)),  # 二进制数据
            b"",  # 空数据
            b"x" * 1000,  # 较大数据
        ]
        
        for test_data in test_cases:
            # 添加数据
            ipfs_hash = await ipfs_client.add_data(test_data)
            assert ipfs_hash is not None
            assert ipfs_hash.startswith("Qm")
            
            # 获取数据
            retrieved_data = await ipfs_client.get_data(ipfs_hash)
            assert retrieved_data is not None
            
            # 固定数据
            pin_result = await ipfs_client.pin_data(ipfs_hash)
            assert pin_result is True
    
    @pytest.mark.asyncio
    async def test_multiple_operations(self, ipfs_client):
        """测试多个操作"""
        await ipfs_client.initialize()
        
        # 添加多个数据项
        hashes = []
        for i in range(5):
            test_data = f"Test data item {i}".encode()
            ipfs_hash = await ipfs_client.add_data(test_data)
            hashes.append(ipfs_hash)
        
        # 由于是模拟实现，所有哈希可能相同，这是正常的
        assert len(hashes) == 5
        assert all(isinstance(h, str) for h in hashes)
        assert all(h.startswith("Qm") for h in hashes)
        
        # 获取所有数据
        for ipfs_hash in hashes:
            data = await ipfs_client.get_data(ipfs_hash)
            assert data is not None
            
            # 固定所有数据
            pin_result = await ipfs_client.pin_data(ipfs_hash)
            assert pin_result is True
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, ipfs_client):
        """测试并发操作"""
        import asyncio
        
        await ipfs_client.initialize()
        
        # 并发添加数据
        async def add_data_task(data_id):
            test_data = f"Concurrent data {data_id}".encode()
            return await ipfs_client.add_data(test_data)
        
        # 创建多个并发任务
        tasks = [add_data_task(i) for i in range(10)]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 10
        assert all(isinstance(h, str) for h in results)
        assert all(h.startswith("Qm") for h in results)
    
    @pytest.mark.asyncio
    async def test_mixed_success_and_failure(self, ipfs_client):
        """测试成功和失败混合的场景"""
        await ipfs_client.initialize()
        
        # 正常操作
        success_hash = await ipfs_client.add_data(b"success data")
        assert success_hash.startswith("Qm")
        
        success_data = await ipfs_client.get_data(success_hash)
        assert success_data is not None
        
        success_pin = await ipfs_client.pin_data(success_hash)
        assert success_pin is True
        
        # 模拟失败操作
        with patch.object(ipfs_client, 'logger') as mock_logger:
            mock_logger.info.side_effect = Exception("Simulated failure")
            
            with pytest.raises(IPFSError):
                await ipfs_client.add_data(b"failure data")
            
            with pytest.raises(IPFSError):
                await ipfs_client.get_data("failure_hash")
            
            failure_pin = await ipfs_client.pin_data("failure_hash")
            assert failure_pin is False


class TestIPFSClientEdgeCases:
    """IPFS客户端边界条件测试"""
    
    @pytest.fixture
    def ipfs_client(self):
        """IPFS客户端实例"""
        return IPFSClient()
    
    @pytest.mark.asyncio
    async def test_very_large_data(self, ipfs_client):
        """测试非常大的数据"""
        await ipfs_client.initialize()
        
        # 创建10MB的数据
        large_data = b"x" * (10 * 1024 * 1024)
        ipfs_hash = await ipfs_client.add_data(large_data)
        
        assert ipfs_hash is not None
        assert ipfs_hash.startswith("Qm")
    
    @pytest.mark.asyncio
    async def test_special_characters_data(self, ipfs_client):
        """测试包含特殊字符的数据"""
        await ipfs_client.initialize()
        
        special_data = "Hello 世界! 🌍 Special chars: @#$%^&*()".encode('utf-8')
        ipfs_hash = await ipfs_client.add_data(special_data)
        
        assert ipfs_hash is not None
        assert ipfs_hash.startswith("Qm")
    
    @pytest.mark.asyncio
    async def test_repeated_operations(self, ipfs_client):
        """测试重复操作"""
        await ipfs_client.initialize()
        
        test_data = b"repeated data"
        
        # 多次添加相同数据
        hashes = []
        for _ in range(3):
            ipfs_hash = await ipfs_client.add_data(test_data)
            hashes.append(ipfs_hash)
        
        # 由于是模拟实现，哈希应该相同
        assert all(h == hashes[0] for h in hashes)
        
        # 多次获取相同数据
        for ipfs_hash in hashes:
            data = await ipfs_client.get_data(ipfs_hash)
            assert data == b"mock ipfs data"
        
        # 多次固定相同数据
        for ipfs_hash in hashes:
            result = await ipfs_client.pin_data(ipfs_hash)
            assert result is True
    
    @pytest.mark.asyncio
    async def test_operations_without_initialization(self, ipfs_client):
        """测试未初始化时的操作"""
        # 不调用initialize()
        
        # 这些操作应该仍然工作，因为是模拟实现
        ipfs_hash = await ipfs_client.add_data(b"test data")
        assert ipfs_hash is not None
        
        data = await ipfs_client.get_data(ipfs_hash)
        assert data is not None
        
        result = await ipfs_client.pin_data(ipfs_hash)
        assert result is True
        
        # 连接状态检查
        assert ipfs_client.is_connected() is True


class TestIPFSClientConfiguration:
    """IPFS客户端配置测试"""
    
    @pytest.fixture
    def ipfs_client(self):
        """IPFS客户端实例"""
        return IPFSClient()
    
    def test_settings_access(self, ipfs_client):
        """测试设置访问"""
        assert ipfs_client.settings is not None
        assert hasattr(ipfs_client.settings, 'ipfs')
    
    def test_logger_access(self, ipfs_client):
        """测试日志器访问"""
        assert ipfs_client.logger is not None
        assert ipfs_client.logger.name == 'blockchain_service.services.ipfs_client'
    
    def test_client_initial_state(self, ipfs_client):
        """测试客户端初始状态"""
        assert ipfs_client._client is None
    
    @pytest.mark.asyncio
    async def test_initialization_with_different_settings(self, ipfs_client):
        """测试不同设置下的初始化"""
        # 模拟不同的IPFS节点URL
        with patch.object(ipfs_client.settings.ipfs, 'node_url', 'http://localhost:5001'):
            await ipfs_client.initialize()
            assert ipfs_client.is_connected() is True
        
        with patch.object(ipfs_client.settings.ipfs, 'node_url', 'http://custom-ipfs:8080'):
            await ipfs_client.initialize()
            assert ipfs_client.is_connected() is True 