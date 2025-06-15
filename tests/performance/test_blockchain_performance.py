"""
区块链服务性能测试套件

测试各个组件的性能指标，包括响应时间、吞吐量、内存使用等。
"""

import asyncio
import time
import psutil
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any
import json
from datetime import datetime

from blockchain_service.services.blockchain_client import BlockchainClient
from blockchain_service.services.ipfs_client import IPFSClient
from blockchain_service.services.zkp_service import ZKPService
from blockchain_service.services.encryption_service import EncryptionService


class PerformanceMetrics:
    """性能指标收集器"""
    
    def __init__(self):
        self.metrics = {}
        self.start_time = None
        self.start_memory = None
    
    def start_measurement(self, test_name: str):
        """开始性能测量"""
        self.start_time = time.time()
        process = psutil.Process()
        self.start_memory = process.memory_info().rss / 1024 / 1024  # MB
        
    def end_measurement(self, test_name: str, operations_count: int = 1):
        """结束性能测量并记录指标"""
        end_time = time.time()
        process = psutil.Process()
        end_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        duration = end_time - self.start_time
        throughput = operations_count / duration if duration > 0 else 0
        
        self.metrics[test_name] = {
            'duration_seconds': duration,
            'throughput_ops_per_second': throughput,
            'memory_usage_mb': end_memory - self.start_memory,
            'operations_count': operations_count,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取所有性能指标"""
        return self.metrics
    
    def save_to_file(self, filename: str):
        """保存指标到文件"""
        with open(filename, 'w') as f:
            json.dump(self.metrics, f, indent=2)


@pytest.fixture
def performance_metrics():
    """性能指标收集器fixture"""
    return PerformanceMetrics()


class TestBlockchainClientPerformance:
    """区块链客户端性能测试"""
    
    @pytest.mark.asyncio
    async def test_connection_performance(self, performance_metrics):
        """测试连接性能"""
        with patch('web3.Web3') as mock_web3:
            mock_web3.return_value.is_connected.return_value = True
            mock_web3.return_value.eth.chain_id = 1
            
            performance_metrics.start_measurement('blockchain_connection')
            
            # 测试多次连接
            connection_count = 20
            for _ in range(connection_count):
                client = BlockchainClient("http://localhost:8545")
                await client.initialize()
            
            performance_metrics.end_measurement('blockchain_connection', connection_count)
            
            metrics = performance_metrics.get_metrics()['blockchain_connection']
            
            # 性能断言
            assert metrics['duration_seconds'] < 5.0
            assert metrics['throughput_ops_per_second'] > 4
            print(f"连接性能测试: {metrics['throughput_ops_per_second']:.2f} 连接/秒")
    
    @pytest.mark.asyncio
    async def test_balance_query_performance(self, performance_metrics):
        """测试余额查询性能"""
        with patch('web3.Web3') as mock_web3:
            mock_instance = mock_web3.return_value
            mock_instance.is_connected.return_value = True
            mock_instance.eth.chain_id = 1
            mock_instance.eth.get_balance.return_value = 1000000000000000000
            
            client = BlockchainClient("http://localhost:8545")
            await client.initialize()
            
            performance_metrics.start_measurement('balance_queries')
            
            # 测试批量余额查询
            query_count = 100
            tasks = []
            for i in range(query_count):
                task = client.get_balance('0x' + f'{i:040x}')
                tasks.append(task)
            
            await asyncio.gather(*tasks)
            
            performance_metrics.end_measurement('balance_queries', query_count)
            
            metrics = performance_metrics.get_metrics()['balance_queries']
            
            # 性能断言
            assert metrics['duration_seconds'] < 3.0
            assert metrics['throughput_ops_per_second'] > 30


class TestIPFSPerformance:
    """IPFS性能测试"""
    
    @pytest.mark.asyncio
    async def test_file_upload_performance(self, performance_metrics):
        """测试文件上传性能"""
        with patch('ipfshttpclient.connect') as mock_connect:
            mock_client = AsyncMock()
            mock_client.add.return_value = {'Hash': 'QmTest123'}
            mock_connect.return_value = mock_client
            
            ipfs_client = IPFSClient("http://localhost:5001")
            await ipfs_client.initialize()
            
            performance_metrics.start_measurement('ipfs_file_upload')
            
            # 测试多个文件上传
            upload_count = 30
            test_data = b"test data " * 100  # 约900B的测试数据
            
            for i in range(upload_count):
                await ipfs_client.store_data(test_data)
            
            performance_metrics.end_measurement('ipfs_file_upload', upload_count)
            
            metrics = performance_metrics.get_metrics()['ipfs_file_upload']
            
            # 性能断言
            assert metrics['duration_seconds'] < 5.0
            assert metrics['throughput_ops_per_second'] > 6


class TestZKPPerformance:
    """零知识证明性能测试"""
    
    @pytest.mark.asyncio
    async def test_proof_generation_performance(self, performance_metrics):
        """测试证明生成性能"""
        zkp_service = ZKPService()
        
        performance_metrics.start_measurement('zkp_proof_generation')
        
        # 测试多个证明生成
        proof_count = 10
        for i in range(proof_count):
            await zkp_service.generate_proof(f"test_data_{i}", f"secret_{i}")
        
        performance_metrics.end_measurement('zkp_proof_generation', proof_count)
        
        metrics = performance_metrics.get_metrics()['zkp_proof_generation']
        
        # 性能断言
        assert metrics['duration_seconds'] < 5.0
        assert metrics['throughput_ops_per_second'] > 2


class TestEncryptionPerformance:
    """加密服务性能测试"""
    
    @pytest.mark.asyncio
    async def test_encryption_performance(self, performance_metrics):
        """测试加密性能"""
        encryption_service = EncryptionService()
        
        performance_metrics.start_measurement('encryption_operations')
        
        # 测试加密操作
        encryption_count = 50
        test_data = "sensitive data " * 10  # 约150字节数据
        
        encrypted_data_list = []
        for i in range(encryption_count):
            encrypted = await encryption_service.encrypt(test_data)
            encrypted_data_list.append(encrypted)
        
        # 测试解密
        for encrypted in encrypted_data_list:
            decrypted = await encryption_service.decrypt(encrypted)
            assert decrypted == test_data
        
        performance_metrics.end_measurement('encryption_operations', encryption_count * 2)
        
        metrics = performance_metrics.get_metrics()['encryption_operations']
        
        # 性能断言
        assert metrics['duration_seconds'] < 5.0
        assert metrics['throughput_ops_per_second'] > 20


@pytest.mark.asyncio
async def test_simple_performance_benchmark(performance_metrics):
    """简单性能基准测试"""
    
    with patch('web3.Web3') as mock_web3:
        mock_web3_instance = mock_web3.return_value
        mock_web3_instance.is_connected.return_value = True
        mock_web3_instance.eth.chain_id = 1
        mock_web3_instance.eth.get_balance.return_value = 1000000000000000000
        
        performance_metrics.start_measurement('simple_benchmark')
        
        # 初始化服务
        blockchain_client = BlockchainClient("http://localhost:8545")
        await blockchain_client.initialize()
        
        # 执行一些操作
        tasks = []
        for i in range(10):
            task = blockchain_client.get_balance('0x' + '1' * 40)
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        performance_metrics.end_measurement('simple_benchmark', 10)
        
        metrics = performance_metrics.get_metrics()['simple_benchmark']
        
        # 性能断言
        assert metrics['duration_seconds'] < 3.0
        assert metrics['throughput_ops_per_second'] > 3
        
        print(f"简单基准测试完成:")
        print(f"  - 总耗时: {metrics['duration_seconds']:.2f}秒")
        print(f"  - 吞吐量: {metrics['throughput_ops_per_second']:.2f}操作/秒")
        print(f"  - 内存使用: {metrics['memory_usage_mb']:.2f}MB")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])