"""
Pytest 配置和共享 fixtures

提供测试所需的通用配置和数据。
"""

import asyncio
import pytest
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

from blockchain_service.config.settings import Settings, get_settings
from blockchain_service.services.encryption_service import EncryptionService
from blockchain_service.services.blockchain_client import BlockchainClient
from blockchain_service.services.health_data_service import HealthDataService


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """创建事件循环用于异步测试"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings() -> Settings:
    """测试配置"""
    return Settings(
        app_name="Test Blockchain Service",
        app_version="1.0.0-test",
        debug=True,
        environment="test"
    )


@pytest.fixture
def encryption_service() -> EncryptionService:
    """加密服务实例"""
    return EncryptionService()


@pytest.fixture
def mock_blockchain_client() -> AsyncMock:
    """模拟区块链客户端"""
    client = AsyncMock(spec=BlockchainClient)
    client.is_connected.return_value = True
    client.initialize = AsyncMock()
    client.send_transaction = AsyncMock()
    client.call_contract_function = AsyncMock()
    client.get_balance = AsyncMock()
    return client


@pytest.fixture
def health_data_service() -> HealthDataService:
    """健康数据服务实例"""
    return HealthDataService()


@pytest.fixture
def sample_health_data() -> dict:
    """示例健康数据"""
    return {
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "data_type": "vital_signs",
        "data_content": {
            "heart_rate": 72,
            "blood_pressure": "120/80",
            "temperature": 36.5,
            "timestamp": "2024-01-01T00:00:00Z"
        },
        "metadata": {
            "device": "smart_watch",
            "location": "home",
            "quality_score": 0.95
        }
    }


@pytest.fixture
def sample_transaction_receipt() -> dict:
    """示例交易回执"""
    return {
        "transactionHash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        "blockNumber": 12345,
        "blockHash": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        "gasUsed": 21000,
        "status": 1,
        "logs": []
    }


@pytest.fixture
def mock_web3():
    """模拟 Web3 实例"""
    web3 = MagicMock()
    web3.is_connected.return_value = True
    web3.eth.chain_id = 1337
    web3.eth.get_balance.return_value = 1000000000000000000  # 1 ETH in wei
    web3.eth.block_number = 12345
    return web3


@pytest.fixture
async def async_mock_blockchain_client() -> AsyncGenerator[AsyncMock, None]:
    """异步模拟区块链客户端"""
    client = AsyncMock(spec=BlockchainClient)
    client.is_connected.return_value = True
    
    # 模拟初始化
    async def mock_initialize():
        client._is_connected = True
    
    client.initialize = mock_initialize
    
    yield client
    
    # 清理
    if hasattr(client, 'close'):
        await client.close()


@pytest.fixture
def mock_ipfs_client():
    """模拟 IPFS 客户端"""
    from blockchain_service.services.ipfs_client import IPFSClient
    
    client = AsyncMock(spec=IPFSClient)
    client.is_connected.return_value = True
    client.add_data = AsyncMock(return_value="QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG")
    client.get_data = AsyncMock(return_value=b"test data")
    client.pin_data = AsyncMock(return_value=True)
    
    return client