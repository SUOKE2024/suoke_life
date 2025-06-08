"""
test_blockchain_client - 索克生活项目模块
"""

from suoke_blockchain_service.blockchain_client import BlockchainClient
from suoke_blockchain_service.exceptions import BlockchainError
from unittest.mock import AsyncMock, MagicMock, patch
from web3.exceptions import Web3Exception
import pytest

"""
区块链客户端测试模块

测试区块链客户端的Web3集成功能。
"""




class TestBlockchainClient:
    """区块链客户端测试类"""

    @pytest.fixture
    def blockchain_client(self):
        """创建区块链客户端实例"""
        with patch('suoke_blockchain_service.blockchain_client.Web3') as mock_web3:
            mock_web3.return_value.is_connected.return_value = True
            client = BlockchainClient()
            return client

    @pytest.mark.asyncio
    async def test_init_success(self):
        """测试成功初始化"""
        with patch('suoke_blockchain_service.blockchain_client.Web3') as mock_web3:
            mock_web3.return_value.is_connected.return_value = True

            client = BlockchainClient()
            assert client.w3 is not None
            assert client.is_connected() is True

    @pytest.mark.asyncio
    async def test_store_health_data_success(self, blockchain_client):
        """测试成功存储健康数据"""
        # Mock合约实例
        mock_contract = MagicMock()
        mock_function = MagicMock()
        mock_contract.functions.storeHealthData.return_value = mock_function

        # Mock交易构建和发送
        mock_function.build_transaction.return_value = {
            'to': '0x1234567890123456789012345678901234567890',
            'data': '0xabcdef',
            'gas': 100000,
            'gasPrice': 20000000000,
            'nonce': 1
        }

        blockchain_client.health_data_storage_contract = mock_contract
        blockchain_client.w3.eth.get_transaction_count = MagicMock(return_value=1)
        blockchain_client.w3.eth.send_raw_transaction = MagicMock(return_value=b'tx_hash')
        blockchain_client.w3.to_hex = MagicMock(return_value='0x1234567890abcdef')

        # Mock私钥签名
        with patch('suoke_blockchain_service.blockchain_client.Account') as mock_account:
            mock_account.sign_transaction.return_value.rawTransaction = b'signed_tx'

            result = await blockchain_client.store_health_data(
                data_hash="test_hash",
                data_type="heart_rate",
                ipfs_hash="QmTest",
                encryption_key_hash="key_hash"
            )

            assert result == '0x1234567890abcdef'