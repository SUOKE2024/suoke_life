"""
区块链客户端单元测试
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from decimal import Decimal
from pathlib import Path

from blockchain_service.services.blockchain_client import (
    BlockchainClient, 
    TransactionReceipt, 
    ContractInfo,
    get_blockchain_client
)
from blockchain_service.core.exceptions import ContractError, NetworkError, ValidationError


class TestBlockchainClient:
    """区块链客户端测试"""
    
    @pytest.fixture
    def blockchain_client(self):
        """区块链客户端实例"""
        return BlockchainClient()
    
    @pytest.fixture
    def mock_web3(self):
        """模拟Web3实例"""
        web3 = MagicMock()
        web3.is_connected.return_value = True
        web3.eth.chain_id = 1337
        web3.eth.get_balance.return_value = 1000000000000000000  # 1 ETH in wei
        web3.eth.get_transaction_count.return_value = 1
        web3.eth.send_transaction.return_value = "0xtxhash123"
        web3.from_wei.return_value = 1.0
        web3.eth.wait_for_transaction_receipt.return_value = {
            'transactionHash': '0xtxhash123',
            'blockNumber': 12345,
            'blockHash': '0xblockhash123',
            'gasUsed': 21000,
            'status': 1,
            'contractAddress': None,
            'logs': []
        }
        return web3
    
    def test_initialization(self, blockchain_client):
        """测试初始化"""
        assert blockchain_client.w3 is None
        assert blockchain_client.contracts == {}
        assert blockchain_client.account is None
        assert blockchain_client._is_connected is False
        assert blockchain_client.settings is not None
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, blockchain_client, mock_web3):
        """测试成功初始化"""
        with patch('blockchain_service.services.blockchain_client.Web3') as mock_web3_class:
            mock_web3_class.return_value = mock_web3
            
            with patch('blockchain_service.services.blockchain_client.Account') as mock_account:
                mock_account.from_key.return_value.address = "0x123456789"
                
                with patch.object(blockchain_client, '_load_contracts') as mock_load:
                    mock_load.return_value = None
                    
                    await blockchain_client.initialize()
                    
                    assert blockchain_client.w3 == mock_web3
                    assert blockchain_client._is_connected is True
                    mock_web3.is_connected.assert_called_once()
                    mock_load.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_initialize_connection_failure(self, blockchain_client):
        """测试连接失败"""
        with patch('blockchain_service.services.blockchain_client.Web3') as mock_web3_class:
            mock_web3 = MagicMock()
            mock_web3.is_connected.return_value = False
            mock_web3_class.return_value = mock_web3
            
            with pytest.raises(NetworkError, match="无法连接到以太坊节点"):
                await blockchain_client.initialize()
    
    @pytest.mark.asyncio
    async def test_initialize_chain_id_mismatch(self, blockchain_client, mock_web3):
        """测试链ID不匹配"""
        mock_web3.eth.chain_id = 9999  # 不匹配的链ID
        
        with patch('blockchain_service.services.blockchain_client.Web3') as mock_web3_class:
            mock_web3_class.return_value = mock_web3
            
            with patch.object(blockchain_client, '_load_contracts') as mock_load:
                mock_load.return_value = None
                
                await blockchain_client.initialize()
                
                # 应该仍然成功初始化，但会有警告
                assert blockchain_client._is_connected is True
    
    @pytest.mark.asyncio
    async def test_load_contracts_success(self, blockchain_client, mock_web3):
        """测试成功加载合约"""
        blockchain_client.w3 = mock_web3
        
        mock_abi = [{"name": "test", "type": "function"}]
        
        with patch.object(blockchain_client, '_read_contract_abi') as mock_read_abi:
            mock_read_abi.return_value = mock_abi
            
            with patch('blockchain_service.services.blockchain_client.is_address') as mock_is_address:
                mock_is_address.return_value = True
                
                with patch('blockchain_service.services.blockchain_client.to_checksum_address') as mock_checksum:
                    mock_checksum.return_value = "0x123456789"
                    
                    mock_contract = MagicMock()
                    mock_web3.eth.contract.return_value = mock_contract
                    
                    # 设置合约地址
                    blockchain_client.settings.blockchain.health_data_storage_address = "0x123456789"
                    blockchain_client.settings.blockchain.zkp_verifier_address = None
                    blockchain_client.settings.blockchain.access_control_address = None
                    
                    await blockchain_client._load_contracts()
                    
                    # 验证只加载了有地址的合约
                    assert "HealthDataStorage" in blockchain_client.contracts
                    assert "ZKPVerifier" not in blockchain_client.contracts
                    assert "AccessControl" not in blockchain_client.contracts
    
    @pytest.mark.asyncio
    async def test_load_contract_success(self, blockchain_client, mock_web3):
        """测试成功加载单个合约"""
        blockchain_client.w3 = mock_web3
        
        mock_abi = [{"name": "test", "type": "function"}]
        
        with patch.object(blockchain_client, '_read_contract_abi') as mock_read_abi:
            mock_read_abi.return_value = mock_abi
            
            with patch('blockchain_service.services.blockchain_client.is_address') as mock_is_address:
                mock_is_address.return_value = True
                
                with patch('blockchain_service.services.blockchain_client.to_checksum_address') as mock_checksum:
                    mock_checksum.return_value = "0x123456789"
                    
                    mock_contract = MagicMock()
                    mock_web3.eth.contract.return_value = mock_contract
                    
                    # 模拟日志记录以避免字段冲突
                    with patch('blockchain_service.services.blockchain_client.logger') as mock_logger:
                        await blockchain_client._load_contract(
                            "TestContract",
                            "0x123456789",
                            "test.json"
                        )
                        
                        assert "TestContract" in blockchain_client.contracts
                        contract_info = blockchain_client.contracts["TestContract"]
                        assert contract_info.name == "TestContract"
                        assert contract_info.address == "0x123456789"
                        assert contract_info.abi == mock_abi
                        assert contract_info.contract == mock_contract
    
    @pytest.mark.asyncio
    async def test_load_contract_invalid_address(self, blockchain_client, mock_web3):
        """测试加载合约时地址无效"""
        blockchain_client.w3 = mock_web3
        
        with patch.object(blockchain_client, '_read_contract_abi') as mock_read_abi:
            mock_read_abi.return_value = []
            
            with patch('blockchain_service.services.blockchain_client.is_address') as mock_is_address:
                mock_is_address.return_value = False
                
                # 模拟日志记录以避免字段冲突
                with patch('blockchain_service.services.blockchain_client.logger') as mock_logger:
                    with pytest.raises(ContractError, match="加载合约失败"):
                        await blockchain_client._load_contract(
                            "TestContract",
                            "invalid_address",
                            "test.json"
                        )
    
    @pytest.mark.asyncio
    async def test_read_contract_abi_list_format(self, blockchain_client):
        """测试读取ABI文件（列表格式）"""
        mock_abi = [{"name": "test", "type": "function"}]
        mock_content = json.dumps(mock_abi)
        
        # 创建异步上下文管理器模拟
        mock_file = AsyncMock()
        mock_file.read.return_value = mock_content
        
        with patch('aiofiles.open', return_value=mock_file) as mock_open_func:
            mock_open_func.return_value.__aenter__.return_value = mock_file
            
            with patch('pathlib.Path.exists') as mock_exists:
                mock_exists.return_value = True
                
                result = await blockchain_client._read_contract_abi("test.json")
                assert result == mock_abi
    
    @pytest.mark.asyncio
    async def test_read_contract_abi_dict_format(self, blockchain_client):
        """测试读取ABI文件（字典格式）"""
        mock_abi = [{"name": "test", "type": "function"}]
        mock_data = {"abi": mock_abi, "bytecode": "0x123"}
        mock_content = json.dumps(mock_data)
        
        # 创建异步上下文管理器模拟
        mock_file = AsyncMock()
        mock_file.read.return_value = mock_content
        
        with patch('aiofiles.open', return_value=mock_file) as mock_open_func:
            mock_open_func.return_value.__aenter__.return_value = mock_file
            
            with patch('pathlib.Path.exists') as mock_exists:
                mock_exists.return_value = True
                
                result = await blockchain_client._read_contract_abi("test.json")
                assert result == mock_abi
    
    @pytest.mark.asyncio
    async def test_read_contract_abi_file_not_found(self, blockchain_client):
        """测试ABI文件不存在"""
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = False
            
            with pytest.raises(ContractError, match="读取ABI文件失败"):
                await blockchain_client._read_contract_abi("nonexistent.json")
    
    @pytest.mark.asyncio
    async def test_send_transaction_success(self, blockchain_client, mock_web3):
        """测试成功发送交易"""
        blockchain_client.w3 = mock_web3
        blockchain_client._is_connected = True
        
        # 设置模拟合约
        mock_contract = MagicMock()
        mock_function = MagicMock()
        mock_function.return_value.build_transaction.return_value = {
            'to': '0x123456789',
            'data': '0xfunction_data',
            'gas': 100000,
            'gasPrice': 20000000000,
            'nonce': 1
        }
        mock_contract.functions.test_function = mock_function
        
        contract_info = ContractInfo(
            name="TestContract",
            address="0x123456789",
            abi=[],
            contract=mock_contract
        )
        blockchain_client.contracts["TestContract"] = contract_info
        
        # 设置账户
        mock_account = MagicMock()
        mock_account.address = "0xsender123"
        blockchain_client.account = mock_account
        
        # 模拟交易哈希对象
        mock_tx_hash = MagicMock()
        mock_tx_hash.hex.return_value = "0xtxhash123"
        mock_web3.eth.send_raw_transaction.return_value = mock_tx_hash
        
        with patch.object(blockchain_client, '_wait_for_transaction_receipt') as mock_wait:
            # 模拟回执中的哈希对象
            mock_receipt_hash = MagicMock()
            mock_receipt_hash.hex.return_value = "0xtxhash123"
            mock_block_hash = MagicMock()
            mock_block_hash.hex.return_value = "0xblockhash123"
            
            mock_wait.return_value = {
                'transactionHash': mock_receipt_hash,
                'blockNumber': 12345,
                'blockHash': mock_block_hash,
                'gasUsed': 21000,
                'status': 1,
                'contractAddress': None,
                'logs': []
            }
            
            receipt = await blockchain_client.send_transaction(
                "TestContract",
                "test_function",
                "arg1",
                "arg2"
            )
            
            assert isinstance(receipt, TransactionReceipt)
            assert receipt.transaction_hash == "0xtxhash123"
            assert receipt.block_number == 12345
            assert receipt.gas_used == 21000
            assert receipt.status == 1
    
    @pytest.mark.asyncio
    async def test_send_transaction_not_connected(self, blockchain_client):
        """测试未连接时发送交易"""
        blockchain_client._is_connected = False
        
        with pytest.raises(NetworkError, match="区块链客户端未连接"):
            await blockchain_client.send_transaction(
                "TestContract",
                "test_function"
            )
    
    @pytest.mark.asyncio
    async def test_send_transaction_contract_not_found(self, blockchain_client):
        """测试合约不存在"""
        blockchain_client._is_connected = True
        
        # 设置账户以通过账户检查
        mock_account = MagicMock()
        mock_account.address = "0xsender123"
        blockchain_client.account = mock_account
        
        with pytest.raises(ContractError, match="合约未找到"):
            await blockchain_client.send_transaction(
                "NonexistentContract",
                "test_function"
            )
    
    @pytest.mark.asyncio
    async def test_call_contract_function_success(self, blockchain_client, mock_web3):
        """测试成功调用合约函数"""
        blockchain_client.w3 = mock_web3
        blockchain_client._is_connected = True
        
        # 设置模拟合约
        mock_contract = MagicMock()
        mock_function = MagicMock()
        mock_function.return_value.call.return_value = "function_result"
        mock_contract.functions.test_function = mock_function
        
        contract_info = ContractInfo(
            name="TestContract",
            address="0x123456789",
            abi=[],
            contract=mock_contract
        )
        blockchain_client.contracts["TestContract"] = contract_info
        
        result = await blockchain_client.call_contract_function(
            "TestContract",
            "test_function",
            "arg1",
            "arg2"
        )
        
        assert result == "function_result"
        mock_function.assert_called_once_with("arg1", "arg2")
    
    @pytest.mark.asyncio
    async def test_call_contract_function_not_connected(self, blockchain_client):
        """测试未连接时调用合约函数"""
        blockchain_client._is_connected = False
        
        with pytest.raises(NetworkError, match="区块链客户端未连接"):
            await blockchain_client.call_contract_function(
                "TestContract",
                "test_function"
            )
    
    def test_is_connected(self, blockchain_client):
        """测试连接状态检查"""
        assert blockchain_client.is_connected() is False
        
        # 设置连接状态和模拟Web3
        blockchain_client._is_connected = True
        mock_web3 = MagicMock()
        mock_web3.is_connected.return_value = True
        blockchain_client.w3 = mock_web3
        
        assert blockchain_client.is_connected() is True
    
    @pytest.mark.asyncio
    async def test_get_balance_success(self, blockchain_client, mock_web3):
        """测试成功获取余额"""
        blockchain_client.w3 = mock_web3
        blockchain_client._is_connected = True
        
        # 模拟from_wei返回正确的格式
        mock_web3.from_wei.return_value = 1.0
        
        balance = await blockchain_client.get_balance("0x123456789")
        
        assert isinstance(balance, Decimal)
        assert balance == Decimal("1.0")  # 1 ETH
    
    @pytest.mark.asyncio
    async def test_get_balance_invalid_address(self, blockchain_client, mock_web3):
        """测试获取余额时地址无效"""
        blockchain_client.w3 = mock_web3
        blockchain_client._is_connected = True
        
        # 模拟get_balance抛出异常
        mock_web3.eth.get_balance.side_effect = ValueError("Invalid address")
        
        with pytest.raises(NetworkError, match="获取余额失败"):
            await blockchain_client.get_balance("invalid_address")
    
    @pytest.mark.asyncio
    async def test_get_balance_not_connected(self, blockchain_client):
        """测试未连接时获取余额"""
        blockchain_client._is_connected = False
        
        with pytest.raises(NetworkError, match="区块链客户端未连接"):
            await blockchain_client.get_balance("0x123456789")
    
    @pytest.mark.asyncio
    async def test_close(self, blockchain_client):
        """测试关闭连接"""
        blockchain_client._is_connected = True
        
        await blockchain_client.close()
        
        assert blockchain_client._is_connected is False
        assert blockchain_client.w3 is None
        assert blockchain_client.contracts == {}
    
    @pytest.mark.asyncio
    async def test_wait_for_transaction_receipt_success(self, blockchain_client, mock_web3):
        """测试等待交易回执成功"""
        blockchain_client.w3 = mock_web3
        
        # 模拟交易回执和区块号
        mock_receipt = {
            'transactionHash': '0xtxhash123',
            'blockNumber': 12345,
            'blockHash': '0xblockhash123',
            'gasUsed': 21000,
            'status': 1,
            'contractAddress': None,
            'logs': []
        }
        mock_web3.eth.get_transaction_receipt.return_value = mock_receipt
        mock_web3.eth.block_number = 12350  # 5个确认
        
        receipt = await blockchain_client._wait_for_transaction_receipt("0xtxhash123")
        
        assert receipt['transactionHash'] == '0xtxhash123'
        assert receipt['status'] == 1
    
    @pytest.mark.asyncio
    async def test_wait_for_transaction_receipt_timeout(self, blockchain_client, mock_web3):
        """测试等待交易回执超时"""
        blockchain_client.w3 = mock_web3
        
        # 模拟超时情况 - 设置很短的超时时间
        blockchain_client.settings.blockchain.transaction_timeout = 0.1
        
        from web3.exceptions import TransactionNotFound
        mock_web3.eth.get_transaction_receipt.side_effect = TransactionNotFound("Transaction not found")
        
        mock_tx_hash = MagicMock()
        mock_tx_hash.hex.return_value = "0xtxhash123"
        
        with pytest.raises(NetworkError, match="交易确认超时"):
            await blockchain_client._wait_for_transaction_receipt(mock_tx_hash)


class TestTransactionReceipt:
    """交易回执测试"""
    
    def test_transaction_receipt_creation(self):
        """测试交易回执创建"""
        receipt = TransactionReceipt(
            transaction_hash="0xtxhash123",
            block_number=12345,
            block_hash="0xblockhash123",
            gas_used=21000,
            status=1,
            contract_address="0xcontract123",
            logs=[{"event": "Transfer"}]
        )
        
        assert receipt.transaction_hash == "0xtxhash123"
        assert receipt.block_number == 12345
        assert receipt.block_hash == "0xblockhash123"
        assert receipt.gas_used == 21000
        assert receipt.status == 1
        assert receipt.contract_address == "0xcontract123"
        assert receipt.logs == [{"event": "Transfer"}]


class TestContractInfo:
    """合约信息测试"""
    
    def test_contract_info_creation(self):
        """测试合约信息创建"""
        mock_contract = MagicMock()
        
        contract_info = ContractInfo(
            name="TestContract",
            address="0x123456789",
            abi=[{"name": "test"}],
            contract=mock_contract
        )
        
        assert contract_info.name == "TestContract"
        assert contract_info.address == "0x123456789"
        assert contract_info.abi == [{"name": "test"}]
        assert contract_info.contract == mock_contract


class TestGetBlockchainClient:
    """获取区块链客户端测试"""
    
    @pytest.mark.asyncio
    async def test_get_blockchain_client(self):
        """测试获取区块链客户端"""
        # 重置全局客户端实例
        import blockchain_service.services.blockchain_client as bc_module
        bc_module._blockchain_client = None
        
        with patch.object(BlockchainClient, 'initialize') as mock_init:
            mock_init.return_value = None
            
            client = await get_blockchain_client()
            
            assert isinstance(client, BlockchainClient)
            mock_init.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_blockchain_client_cached(self):
        """测试获取缓存的区块链客户端"""
        # 重置全局客户端实例
        import blockchain_service.services.blockchain_client as bc_module
        bc_module._blockchain_client = None
        
        with patch.object(BlockchainClient, 'initialize') as mock_init:
            mock_init.return_value = None
            
            # 第一次调用
            client1 = await get_blockchain_client()
            # 第二次调用应该返回相同的实例
            client2 = await get_blockchain_client()
            
            assert client1 is client2
            # initialize只应该被调用一次
            mock_init.assert_called_once()


class TestBlockchainClientIntegration:
    """区块链客户端集成测试"""
    
    @pytest.fixture
    def blockchain_client(self):
        """区块链客户端实例"""
        return BlockchainClient()
    
    @pytest.mark.asyncio
    async def test_full_workflow(self, blockchain_client):
        """测试完整工作流程"""
        mock_web3 = MagicMock()
        mock_web3.is_connected.return_value = True
        mock_web3.eth.chain_id = 1337
        mock_web3.eth.get_balance.return_value = 1000000000000000000
        mock_web3.eth.send_transaction.return_value = "0xtxhash123"
        mock_web3.from_wei.return_value = 1.0
        mock_web3.eth.wait_for_transaction_receipt.return_value = {
            'transactionHash': '0xtxhash123',
            'blockNumber': 12345,
            'blockHash': '0xblockhash123',
            'gasUsed': 21000,
            'status': 1,
            'contractAddress': None,
            'logs': []
        }
        
        with patch('blockchain_service.services.blockchain_client.Web3') as mock_web3_class:
            mock_web3_class.return_value = mock_web3
            
            with patch.object(blockchain_client, '_load_contracts') as mock_load:
                mock_load.return_value = None
                
                # 1. 初始化
                await blockchain_client.initialize()
                assert blockchain_client.is_connected() is True
                
                # 2. 设置模拟合约
                mock_contract = MagicMock()
                mock_function = MagicMock()
                mock_function.return_value.call.return_value = "test_result"
                mock_contract.functions.getValue = mock_function
                
                contract_info = ContractInfo(
                    name="TestContract",
                    address="0x123456789",
                    abi=[],
                    contract=mock_contract
                )
                blockchain_client.contracts["TestContract"] = contract_info
                
                # 3. 调用合约函数
                result = await blockchain_client.call_contract_function(
                    "TestContract",
                    "getValue"
                )
                assert result == "test_result"
                
                # 4. 获取余额
                mock_web3.from_wei.return_value = 1.0
                balance = await blockchain_client.get_balance("0x123456789")
                assert balance == Decimal("1.0")
                
                # 5. 关闭连接
                await blockchain_client.close()
                assert blockchain_client.is_connected() is False


class TestBlockchainClientErrorHandling:
    """区块链客户端错误处理测试"""
    
    @pytest.fixture
    def blockchain_client(self):
        """区块链客户端实例"""
        return BlockchainClient()
    
    @pytest.mark.asyncio
    async def test_initialize_web3_error(self, blockchain_client):
        """测试Web3初始化错误"""
        with patch('blockchain_service.services.blockchain_client.Web3') as mock_web3_class:
            mock_web3_class.side_effect = Exception("Web3 error")
            
            with pytest.raises(NetworkError, match="区块链客户端初始化失败"):
                await blockchain_client.initialize()
    
    @pytest.mark.asyncio
    async def test_send_transaction_build_error(self, blockchain_client, mock_web3):
        """测试构建交易错误"""
        blockchain_client.w3 = mock_web3
        blockchain_client._is_connected = True
        
        # 设置模拟合约
        mock_contract = MagicMock()
        mock_function = MagicMock()
        mock_function.return_value.build_transaction.side_effect = Exception("Build error")
        mock_contract.functions.test_function = mock_function
        
        contract_info = ContractInfo(
            name="TestContract",
            address="0x123456789",
            abi=[],
            contract=mock_contract
        )
        blockchain_client.contracts["TestContract"] = contract_info
        
        # 设置账户以通过账户检查
        mock_account = MagicMock()
        mock_account.address = "0xsender123"
        blockchain_client.account = mock_account
        
        with pytest.raises(NetworkError, match="发送交易失败"):
            await blockchain_client.send_transaction(
                "TestContract",
                "test_function"
            )
    
    @pytest.mark.asyncio
    async def test_call_contract_function_error(self, blockchain_client, mock_web3):
        """测试调用合约函数错误"""
        blockchain_client.w3 = mock_web3
        blockchain_client._is_connected = True
        
        # 设置模拟合约
        mock_contract = MagicMock()
        mock_contract.functions.test_function.side_effect = Exception("Function error")
        
        contract_info = ContractInfo(
            name="TestContract",
            address="0x123456789",
            abi=[],
            contract=mock_contract
        )
        blockchain_client.contracts["TestContract"] = contract_info
        
        with pytest.raises(ContractError, match="合约函数调用失败"):
            await blockchain_client.call_contract_function(
                "TestContract",
                "test_function"
            )