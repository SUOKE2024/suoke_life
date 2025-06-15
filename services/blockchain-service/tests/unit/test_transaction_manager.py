"""
交易管理器单元测试
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timedelta

from blockchain_service.services.transaction_manager import (
    TransactionManager, 
    TransactionStatus, 
    TransactionInfo
)
from blockchain_service.core.exceptions import NetworkError, ValidationError


class TestTransactionManager:
    """交易管理器测试"""
    
    @pytest.fixture
    def mock_web3(self):
        """模拟Web3实例"""
        web3 = MagicMock()
        web3.eth.chain_id = 1
        web3.eth.get_block_number.return_value = 12345
        web3.eth.gas_price = 20000000000
        web3.eth.accounts = ["0x742d35Cc6634C0532925a3b8D4C9db96C4b4Db93"]
        return web3
    
    @pytest.fixture
    def transaction_manager(self, mock_web3):
        """交易管理器实例"""
        return TransactionManager(mock_web3)
    
    @pytest.fixture
    def sample_transaction(self):
        """示例交易数据"""
        return {
            "to_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4Db93",
            "value": 1000000000000000000,  # 1 ETH
            "gas": 21000,
            "gas_price": 20000000000,
            "nonce": 1
        }
    
    def test_initialization(self, mock_web3):
        """测试初始化"""
        manager = TransactionManager(mock_web3)
        
        assert manager.web3 is mock_web3
        assert manager.pending_transactions == {}
        assert manager.transaction_callbacks == {}
        assert manager._monitoring_task is None
    
    @pytest.mark.asyncio
    async def test_start_monitoring(self, transaction_manager):
        """测试启动监控"""
        await transaction_manager.start_monitoring()
        
        assert transaction_manager._monitoring_task is not None
        assert not transaction_manager._monitoring_task.done()
        
        # 清理
        await transaction_manager.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_start_monitoring_already_running(self, transaction_manager):
        """测试重复启动监控"""
        await transaction_manager.start_monitoring()
        first_task = transaction_manager._monitoring_task
        
        # 再次启动应该不会创建新任务
        await transaction_manager.start_monitoring()
        assert transaction_manager._monitoring_task is first_task
        
        # 清理
        await transaction_manager.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_stop_monitoring(self, transaction_manager):
        """测试停止监控"""
        # 先启动监控
        await transaction_manager.start_monitoring()
        assert transaction_manager._monitoring_task is not None
        
        # 停止监控
        await transaction_manager.stop_monitoring()
        
        # 验证监控任务已停止
        assert transaction_manager._monitoring_task.cancelled() or transaction_manager._monitoring_task.done()
    
    @pytest.mark.asyncio
    async def test_stop_monitoring_not_running(self, transaction_manager):
        """测试停止未运行的监控"""
        # 直接停止监控应该不会出错
        await transaction_manager.stop_monitoring()
        assert transaction_manager._monitoring_task is None
    
    @pytest.mark.asyncio
    async def test_send_transaction_success(self, transaction_manager, mock_web3, sample_transaction):
        """测试成功发送交易"""
        expected_tx_hash = "0x1234567890abcdef"
        mock_web3.eth.get_transaction_count.return_value = 1
        mock_web3.eth.send_transaction.return_value = MagicMock(hex=lambda: expected_tx_hash)
        
        tx_hash = await transaction_manager.send_transaction(**sample_transaction)
        
        assert tx_hash == expected_tx_hash
        assert tx_hash in transaction_manager.pending_transactions
        
        # 验证交易信息
        tx_info = transaction_manager.pending_transactions[tx_hash]
        assert tx_info.hash == tx_hash
        assert tx_info.status == TransactionStatus.PENDING
        assert tx_info.to_address == sample_transaction["to_address"]
        assert tx_info.value == sample_transaction["value"]
    
    @pytest.mark.asyncio
    async def test_send_transaction_with_from_address(self, transaction_manager, mock_web3, sample_transaction):
        """测试带发送地址的交易"""
        expected_tx_hash = "0x1234567890abcdef"
        
        mock_web3.eth.get_transaction_count.return_value = 1
        mock_web3.eth.send_transaction.return_value = MagicMock(hex=lambda: expected_tx_hash)
        
        tx_hash = await transaction_manager.send_transaction(**sample_transaction)
        
        assert tx_hash == expected_tx_hash
        tx_info = transaction_manager.pending_transactions[tx_hash]
        # 验证from_address是从web3.eth.accounts[0]获取的
        assert tx_info.from_address == mock_web3.eth.accounts[0]
    
    @pytest.mark.asyncio
    async def test_send_transaction_auto_nonce(self, transaction_manager, mock_web3, sample_transaction):
        """测试自动获取nonce"""
        expected_tx_hash = "0x1234567890abcdef"
        expected_nonce = 5
        
        mock_web3.eth.get_transaction_count.return_value = expected_nonce
        mock_web3.eth.send_transaction.return_value = MagicMock(hex=lambda: expected_tx_hash)
        
        # 不提供nonce
        del sample_transaction["nonce"]
        tx_hash = await transaction_manager.send_transaction(**sample_transaction)
        
        assert tx_hash == expected_tx_hash
        tx_info = transaction_manager.pending_transactions[tx_hash]
        assert tx_info.nonce == expected_nonce
    
    @pytest.mark.asyncio
    async def test_send_transaction_failure(self, transaction_manager, mock_web3, sample_transaction):
        """测试发送交易失败"""
        mock_web3.eth.get_transaction_count.return_value = 1
        mock_web3.eth.send_transaction.side_effect = Exception("Network error")
        
        with pytest.raises(NetworkError, match="Failed to send transaction"):
            await transaction_manager.send_transaction(**sample_transaction)
    
    @pytest.mark.asyncio
    async def test_send_transaction_invalid_address(self, transaction_manager, mock_web3, sample_transaction):
        """测试无效地址"""
        sample_transaction["to_address"] = "invalid_address"
        
        with pytest.raises(NetworkError, match="Failed to send transaction"):
            await transaction_manager.send_transaction(**sample_transaction)
    
    @pytest.mark.asyncio
    async def test_get_transaction_receipt_success(self, transaction_manager, mock_web3):
        """测试成功获取交易收据"""
        tx_hash = "0x1234567890abcdef"
        mock_receipt = MagicMock()
        mock_receipt.status = 1
        mock_receipt.blockNumber = 12345
        mock_receipt.blockHash = MagicMock()
        mock_receipt.blockHash.hex.return_value = "0xabcdef"
        mock_receipt.transactionIndex = 0
        mock_receipt.gasUsed = 21000
        
        mock_web3.eth.get_transaction_receipt.return_value = mock_receipt
        
        receipt = await transaction_manager.get_transaction_receipt(tx_hash)
        
        assert receipt is mock_receipt
        mock_web3.eth.get_transaction_receipt.assert_called_once_with(tx_hash)
    
    @pytest.mark.asyncio
    async def test_get_transaction_receipt_not_found(self, transaction_manager, mock_web3):
        """测试获取不存在的交易收据"""
        tx_hash = "0x1234567890abcdef"
        mock_web3.eth.get_transaction_receipt.return_value = None
        
        receipt = await transaction_manager.get_transaction_receipt(tx_hash)
        
        assert receipt is None
    
    @pytest.mark.asyncio
    async def test_get_transaction_receipt_error(self, transaction_manager, mock_web3):
        """测试获取交易收据时发生错误"""
        tx_hash = "0x1234567890abcdef"
        mock_web3.eth.get_transaction_receipt.side_effect = Exception("Network error")
        
        receipt = await transaction_manager.get_transaction_receipt(tx_hash)
        
        assert receipt is None
    
    @pytest.mark.asyncio
    async def test_wait_for_confirmation_success(self, transaction_manager, mock_web3):
        """测试等待交易确认成功"""
        tx_hash = "0x1234567890abcdef"
        
        # 创建待确认交易
        tx_info = TransactionInfo(
            hash=tx_hash,
            from_address="0x123",
            to_address="0x456",
            value=1000,
            gas=21000,
            gas_price=20000000000,
            nonce=1,
            status=TransactionStatus.PENDING
        )
        transaction_manager.pending_transactions[tx_hash] = tx_info
        
        # 模拟交易收据
        mock_receipt = MagicMock()
        mock_receipt.status = 1
        mock_receipt.blockNumber = 12345
        mock_receipt.blockHash = MagicMock()
        mock_receipt.blockHash.hex.return_value = "0xabcdef"
        mock_receipt.transactionIndex = 0
        mock_receipt.gasUsed = 21000
        
        # 设置区块号，确保有足够的确认数
        mock_web3.eth.block_number = 12347  # 12347 - 12345 + 1 = 3 confirmations
        mock_web3.eth.get_transaction_receipt.return_value = mock_receipt
        
        result = await transaction_manager.wait_for_confirmation(tx_hash, timeout=5)
        
        assert result.status == TransactionStatus.CONFIRMED
        assert result.block_number == 12345
        assert tx_hash not in transaction_manager.pending_transactions
    
    @pytest.mark.asyncio
    async def test_wait_for_confirmation_failed_transaction(self, transaction_manager, mock_web3):
        """测试等待失败的交易确认"""
        tx_hash = "0x1234567890abcdef"
        
        # 创建待确认交易
        tx_info = TransactionInfo(
            hash=tx_hash,
            from_address="0x123",
            to_address="0x456",
            value=1000,
            gas=21000,
            gas_price=20000000000,
            nonce=1,
            status=TransactionStatus.PENDING
        )
        transaction_manager.pending_transactions[tx_hash] = tx_info
        
        # 模拟失败的交易收据
        mock_receipt = MagicMock()
        mock_receipt.status = 0  # 失败状态
        mock_receipt.blockNumber = 12345
        mock_receipt.blockHash = MagicMock()
        mock_receipt.blockHash.hex.return_value = "0xabcdef"
        mock_receipt.transactionIndex = 0
        mock_receipt.gasUsed = 21000
        
        # 设置区块号，确保有足够的确认数
        mock_web3.eth.block_number = 12347  # 12347 - 12345 + 1 = 3 confirmations
        mock_web3.eth.get_transaction_receipt.return_value = mock_receipt
        
        result = await transaction_manager.wait_for_confirmation(tx_hash, timeout=5)
        
        assert result.status == TransactionStatus.FAILED
        assert result.block_number == 12345
        assert tx_hash not in transaction_manager.pending_transactions
    
    @pytest.mark.asyncio
    async def test_wait_for_confirmation_timeout(self, transaction_manager, mock_web3):
        """测试等待交易确认超时"""
        tx_hash = "0x1234567890abcdef"
        
        # 创建待确认交易
        tx_info = TransactionInfo(
            hash=tx_hash,
            from_address="0x123",
            to_address="0x456",
            value=1000,
            gas=21000,
            gas_price=20000000000,
            nonce=1,
            status=TransactionStatus.PENDING
        )
        transaction_manager.pending_transactions[tx_hash] = tx_info
        
        # 模拟没有收据（交易未确认）
        mock_web3.eth.get_transaction_receipt.return_value = None
        
        result = await transaction_manager.wait_for_confirmation(tx_hash, timeout=1)
        
        assert result.status == TransactionStatus.TIMEOUT
        assert tx_hash not in transaction_manager.pending_transactions
    
    @pytest.mark.asyncio
    async def test_wait_for_confirmation_not_found(self, transaction_manager):
        """测试等待不存在的交易确认"""
        tx_hash = "0x1234567890abcdef"
        
        with pytest.raises(NetworkError, match="Transaction confirmation timeout"):
            await transaction_manager.wait_for_confirmation(tx_hash, timeout=1)
    
    @pytest.mark.asyncio
    async def test_wait_for_confirmation_with_error(self, transaction_manager, mock_web3):
        """测试等待确认时发生错误"""
        tx_hash = "0x1234567890abcdef"
        
        # 创建待确认交易
        tx_info = TransactionInfo(
            hash=tx_hash,
            from_address="0x123",
            to_address="0x456",
            value=1000,
            gas=21000,
            gas_price=20000000000,
            nonce=1,
            status=TransactionStatus.PENDING
        )
        transaction_manager.pending_transactions[tx_hash] = tx_info
        
        # 模拟网络错误
        mock_web3.eth.get_transaction_receipt.side_effect = Exception("Network error")
        
        result = await transaction_manager.wait_for_confirmation(tx_hash, timeout=1)
        
        assert result.status == TransactionStatus.TIMEOUT
    
    def test_add_transaction_callback(self, transaction_manager):
        """测试添加交易回调"""
        tx_hash = "0x1234567890abcdef"
        callback = MagicMock()
        
        transaction_manager.add_transaction_callback(tx_hash, callback)
        
        assert tx_hash in transaction_manager.transaction_callbacks
        assert callback in transaction_manager.transaction_callbacks[tx_hash]
    
    def test_add_multiple_transaction_callbacks(self, transaction_manager):
        """测试添加多个交易回调"""
        tx_hash = "0x1234567890abcdef"
        callback1 = MagicMock()
        callback2 = MagicMock()
        
        transaction_manager.add_transaction_callback(tx_hash, callback1)
        transaction_manager.add_transaction_callback(tx_hash, callback2)
        
        assert len(transaction_manager.transaction_callbacks[tx_hash]) == 2
        assert callback1 in transaction_manager.transaction_callbacks[tx_hash]
        assert callback2 in transaction_manager.transaction_callbacks[tx_hash]
    
    @pytest.mark.asyncio
    async def test_execute_callbacks_sync(self, transaction_manager):
        """测试执行同步回调"""
        tx_hash = "0x1234567890abcdef"
        callback = MagicMock()
        tx_info = MagicMock()
        
        transaction_manager.transaction_callbacks[tx_hash] = [callback]
        
        await transaction_manager._execute_callbacks(tx_hash, tx_info)
        
        callback.assert_called_once_with(tx_info)
        assert tx_hash not in transaction_manager.transaction_callbacks
    
    @pytest.mark.asyncio
    async def test_execute_callbacks_async(self, transaction_manager):
        """测试执行异步回调"""
        tx_hash = "0x1234567890abcdef"
        callback = AsyncMock()
        tx_info = MagicMock()
        
        transaction_manager.transaction_callbacks[tx_hash] = [callback]
        
        await transaction_manager._execute_callbacks(tx_hash, tx_info)
        
        callback.assert_called_once_with(tx_info)
        assert tx_hash not in transaction_manager.transaction_callbacks
    
    @pytest.mark.asyncio
    async def test_execute_callbacks_with_error(self, transaction_manager):
        """测试执行回调时发生错误"""
        tx_hash = "0x1234567890abcdef"
        callback = MagicMock(side_effect=Exception("Callback error"))
        tx_info = MagicMock()
        
        transaction_manager.transaction_callbacks[tx_hash] = [callback]
        
        # 应该不会抛出异常
        await transaction_manager._execute_callbacks(tx_hash, tx_info)
        
        # 回调列表应该被清理
        assert tx_hash not in transaction_manager.transaction_callbacks
    
    @pytest.mark.asyncio
    async def test_monitor_transactions_timeout(self, transaction_manager):
        """测试监控交易超时"""
        tx_hash = "0x1234567890abcdef"
        
        # 创建一个过期的交易
        old_time = datetime.utcnow() - timedelta(minutes=15)
        tx_info = TransactionInfo(
            hash=tx_hash,
            from_address="0x123",
            to_address="0x456",
            value=1000,
            gas=21000,
            gas_price=20000000000,
            nonce=1,
            status=TransactionStatus.PENDING
        )
        tx_info.created_at = old_time
        transaction_manager.pending_transactions[tx_hash] = tx_info
        
        # 添加回调来验证超时处理
        callback = MagicMock()
        transaction_manager.transaction_callbacks[tx_hash] = [callback]
        
        # 运行一次监控循环
        await transaction_manager._monitor_transactions_once()
        
        # 验证交易被标记为超时
        callback.assert_called_once()
        called_tx_info = callback.call_args[0][0]
        assert called_tx_info.status == TransactionStatus.TIMEOUT
        assert tx_hash not in transaction_manager.pending_transactions
    
    @pytest.mark.asyncio
    async def test_monitor_transactions_confirmed(self, transaction_manager, mock_web3):
        """测试监控交易确认"""
        tx_hash = "0x1234567890abcdef"
        
        # 创建待确认交易
        tx_info = TransactionInfo(
            hash=tx_hash,
            from_address="0x123",
            to_address="0x456",
            value=1000,
            gas=21000,
            gas_price=20000000000,
            nonce=1,
            status=TransactionStatus.PENDING
        )
        transaction_manager.pending_transactions[tx_hash] = tx_info
        
        # 模拟交易收据
        mock_receipt = MagicMock()
        mock_receipt.status = 1
        mock_receipt.blockNumber = 12345
        mock_receipt.blockHash = MagicMock()
        mock_receipt.blockHash.hex.return_value = "0xabcdef"
        mock_receipt.transactionIndex = 0
        mock_receipt.gasUsed = 21000
        
        mock_web3.eth.get_transaction_receipt.return_value = mock_receipt
        
        # 添加回调
        callback = MagicMock()
        transaction_manager.transaction_callbacks[tx_hash] = [callback]
        
        # 运行一次监控循环
        await transaction_manager._monitor_transactions_once()
        
        # 验证交易被确认
        callback.assert_called_once()
        called_tx_info = callback.call_args[0][0]
        assert called_tx_info.status == TransactionStatus.CONFIRMED
        assert called_tx_info.block_number == 12345
        assert tx_hash not in transaction_manager.pending_transactions
    
    @pytest.mark.asyncio
    async def test_monitor_transactions_failed(self, transaction_manager, mock_web3):
        """测试监控失败的交易"""
        tx_hash = "0x1234567890abcdef"
        
        # 创建待确认交易
        tx_info = TransactionInfo(
            hash=tx_hash,
            from_address="0x123",
            to_address="0x456",
            value=1000,
            gas=21000,
            gas_price=20000000000,
            nonce=1,
            status=TransactionStatus.PENDING
        )
        transaction_manager.pending_transactions[tx_hash] = tx_info
        
        # 模拟失败的交易收据
        mock_receipt = MagicMock()
        mock_receipt.status = 0  # 失败状态
        mock_receipt.blockNumber = 12345
        mock_receipt.blockHash = MagicMock()
        mock_receipt.blockHash.hex.return_value = "0xabcdef"
        mock_receipt.transactionIndex = 0
        mock_receipt.gasUsed = 21000
        
        mock_web3.eth.get_transaction_receipt.return_value = mock_receipt
        
        # 添加回调
        callback = MagicMock()
        transaction_manager.transaction_callbacks[tx_hash] = [callback]
        
        # 运行一次监控循环
        await transaction_manager._monitor_transactions_once()
        
        # 验证交易被标记为失败
        callback.assert_called_once()
        called_tx_info = callback.call_args[0][0]
        assert called_tx_info.status == TransactionStatus.FAILED
        assert tx_hash not in transaction_manager.pending_transactions
    
    @pytest.mark.asyncio
    async def test_monitor_transactions_with_error(self, transaction_manager, mock_web3):
        """测试监控交易时发生错误"""
        tx_hash = "0x1234567890abcdef"
        
        # 创建待确认交易
        tx_info = TransactionInfo(
            hash=tx_hash,
            from_address="0x123",
            to_address="0x456",
            value=1000,
            gas=21000,
            gas_price=20000000000,
            nonce=1,
            status=TransactionStatus.PENDING
        )
        transaction_manager.pending_transactions[tx_hash] = tx_info
        
        # 模拟网络错误
        mock_web3.eth.get_transaction_receipt.side_effect = Exception("Network error")
        
        # 运行一次监控循环，应该不会抛出异常
        await transaction_manager._monitor_transactions_once()
        
        # 交易应该仍在待确认列表中
        assert tx_hash in transaction_manager.pending_transactions
    
    def test_get_pending_transactions(self, transaction_manager):
        """测试获取待确认交易列表"""
        # 添加一些待确认交易
        tx_info1 = TransactionInfo(
            hash="0x123",
            from_address="0x123",
            to_address="0x456",
            value=1000,
            gas=21000,
            gas_price=20000000000,
            nonce=1,
            status=TransactionStatus.PENDING
        )
        tx_info2 = TransactionInfo(
            hash="0x456",
            from_address="0x123",
            to_address="0x789",
            value=2000,
            gas=21000,
            gas_price=20000000000,
            nonce=2,
            status=TransactionStatus.PENDING
        )
        
        transaction_manager.pending_transactions["0x123"] = tx_info1
        transaction_manager.pending_transactions["0x456"] = tx_info2
        
        pending_txs = transaction_manager.get_pending_transactions()
        
        assert len(pending_txs) == 2
        assert tx_info1 in pending_txs
        assert tx_info2 in pending_txs
    
    def test_get_transaction_info(self, transaction_manager):
        """测试获取交易信息"""
        tx_hash = "0x1234567890abcdef"
        tx_info = TransactionInfo(
            hash=tx_hash,
            from_address="0x123",
            to_address="0x456",
            value=1000,
            gas=21000,
            gas_price=20000000000,
            nonce=1,
            status=TransactionStatus.PENDING
        )
        
        transaction_manager.pending_transactions[tx_hash] = tx_info
        
        result = transaction_manager.get_transaction_info(tx_hash)
        assert result is tx_info
    
    def test_get_transaction_info_not_found(self, transaction_manager):
        """测试获取不存在的交易信息"""
        result = transaction_manager.get_transaction_info("0x1234567890abcdef")
        assert result is None


class TestTransactionStatus:
    """交易状态测试"""
    
    def test_transaction_status_values(self):
        """测试交易状态枚举值"""
        assert TransactionStatus.PENDING.value == "pending"
        assert TransactionStatus.CONFIRMED.value == "confirmed"
        assert TransactionStatus.FAILED.value == "failed"
        assert TransactionStatus.TIMEOUT.value == "timeout"


class TestTransactionInfo:
    """交易信息测试"""
    
    def test_transaction_info_creation(self):
        """测试交易信息创建"""
        tx_info = TransactionInfo(
            hash="0x1234567890abcdef",
            from_address="0x123",
            to_address="0x456",
            value=1000,
            gas=21000,
            gas_price=20000000000,
            nonce=1,
            status=TransactionStatus.PENDING
        )
        
        assert tx_info.hash == "0x1234567890abcdef"
        assert tx_info.from_address == "0x123"
        assert tx_info.to_address == "0x456"
        assert tx_info.value == 1000
        assert tx_info.gas == 21000
        assert tx_info.gas_price == 20000000000
        assert tx_info.nonce == 1
        assert tx_info.status == TransactionStatus.PENDING
        assert tx_info.block_number is None
        assert tx_info.block_hash is None
        assert tx_info.transaction_index is None
        assert tx_info.gas_used is None
        assert tx_info.created_at is not None
        assert tx_info.confirmed_at is None
    
    def test_transaction_info_with_optional_fields(self):
        """测试带可选字段的交易信息"""
        confirmed_time = datetime.utcnow()
        
        tx_info = TransactionInfo(
            hash="0x1234567890abcdef",
            from_address="0x123",
            to_address="0x456",
            value=1000,
            gas=21000,
            gas_price=20000000000,
            nonce=1,
            status=TransactionStatus.CONFIRMED,
            block_number=12345,
            block_hash="0xabcdef",
            transaction_index=0,
            gas_used=21000,
            confirmed_at=confirmed_time
        )
        
        assert tx_info.block_number == 12345
        assert tx_info.block_hash == "0xabcdef"
        assert tx_info.transaction_index == 0
        assert tx_info.gas_used == 21000
        assert tx_info.confirmed_at == confirmed_time


class TestTransactionManagerIntegration:
    """交易管理器集成测试"""
    
    @pytest.fixture
    def mock_web3(self):
        """模拟Web3实例"""
        web3 = MagicMock()
        web3.eth.chain_id = 1
        web3.eth.get_block_number.return_value = 12345
        web3.eth.gas_price = 20000000000
        web3.eth.accounts = ["0x742d35Cc6634C0532925a3b8D4C9db96C4b4Db93"]
        return web3
    
    @pytest.fixture
    def transaction_manager(self, mock_web3):
        """交易管理器实例"""
        return TransactionManager(mock_web3)
    
    @pytest.mark.asyncio
    async def test_full_transaction_lifecycle(self, transaction_manager, mock_web3):
        """测试完整的交易生命周期"""
        # 1. 发送交易
        tx_hash = "0x1234567890abcdef"
        mock_web3.eth.get_transaction_count.return_value = 1
        mock_web3.eth.send_transaction.return_value = MagicMock(hex=lambda: tx_hash)
        
        result_hash = await transaction_manager.send_transaction(
            to_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4Db93",
            value=1000000000000000000,
            gas=21000,
            gas_price=20000000000
        )
        
        assert result_hash == tx_hash
        assert tx_hash in transaction_manager.pending_transactions
        
        # 2. 添加回调
        callback_called = False
        callback_tx_info = None
        
        def transaction_callback(tx_info):
            nonlocal callback_called, callback_tx_info
            callback_called = True
            callback_tx_info = tx_info
        
        transaction_manager.add_transaction_callback(tx_hash, transaction_callback)
        
        # 3. 模拟交易确认
        mock_receipt = MagicMock()
        mock_receipt.status = 1
        mock_receipt.blockNumber = 12345
        mock_receipt.blockHash = MagicMock()
        mock_receipt.blockHash.hex.return_value = "0xabcdef"
        mock_receipt.transactionIndex = 0
        mock_receipt.gasUsed = 21000
        
        # 设置区块号，确保有足够的确认数
        mock_web3.eth.block_number = 12347  # 12347 - 12345 + 1 = 3 confirmations
        mock_web3.eth.get_transaction_receipt.return_value = mock_receipt
        
        # 4. 等待确认
        confirmed_tx_info = await transaction_manager.wait_for_confirmation(tx_hash, timeout=5)
        
        # 5. 验证结果
        assert confirmed_tx_info.status == TransactionStatus.CONFIRMED
        assert confirmed_tx_info.block_number == 12345
        assert confirmed_tx_info.gas_used == 21000
        assert tx_hash not in transaction_manager.pending_transactions
        
        # 6. 验证回调被调用
        assert callback_called
        assert callback_tx_info.status == TransactionStatus.CONFIRMED
    
    @pytest.mark.asyncio
    async def test_monitoring_integration(self, transaction_manager, mock_web3):
        """测试监控集成"""
        # 启动监控
        await transaction_manager.start_monitoring()
        
        # 发送交易
        tx_hash = "0x1234567890abcdef"
        mock_web3.eth.get_transaction_count.return_value = 1
        mock_web3.eth.send_transaction.return_value = MagicMock(hex=lambda: tx_hash)
        
        await transaction_manager.send_transaction(
            to_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4Db93",
            value=1000000000000000000,
            gas=21000,
            gas_price=20000000000
        )
        
        # 添加回调
        callback_called = False
        
        def transaction_callback(tx_info):
            nonlocal callback_called
            callback_called = True
        
        transaction_manager.add_transaction_callback(tx_hash, transaction_callback)
        
        # 模拟交易确认
        mock_receipt = MagicMock()
        mock_receipt.status = 1
        mock_receipt.blockNumber = 12345
        mock_receipt.blockHash = MagicMock()
        mock_receipt.blockHash.hex.return_value = "0xabcdef"
        mock_receipt.transactionIndex = 0
        mock_receipt.gasUsed = 21000
        
        mock_web3.eth.get_transaction_receipt.return_value = mock_receipt
        
        # 运行一次监控循环
        await transaction_manager._monitor_transactions_once()
        
        # 验证交易被处理
        assert callback_called
        assert tx_hash not in transaction_manager.pending_transactions
        
        # 停止监控
        await transaction_manager.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_multiple_transactions_monitoring(self, transaction_manager, mock_web3):
        """测试多个交易的监控"""
        # 创建多个交易
        tx_hashes = ["0x123", "0x456", "0x789"]
        
        for i, tx_hash in enumerate(tx_hashes):
            tx_info = TransactionInfo(
                hash=tx_hash,
                from_address="0x123",
                to_address="0x456",
                value=1000 * (i + 1),
                gas=21000,
                gas_price=20000000000,
                nonce=i + 1,
                status=TransactionStatus.PENDING
            )
            transaction_manager.pending_transactions[tx_hash] = tx_info
        
        # 模拟不同的交易状态
        def mock_get_receipt(tx_hash):
            if tx_hash == "0x123":
                # 确认的交易
                receipt = MagicMock()
                receipt.status = 1
                receipt.blockNumber = 12345
                receipt.blockHash = MagicMock()
                receipt.blockHash.hex.return_value = "0xabcdef"
                receipt.transactionIndex = 0
                receipt.gasUsed = 21000
                return receipt
            elif tx_hash == "0x456":
                # 失败的交易
                receipt = MagicMock()
                receipt.status = 0
                receipt.blockNumber = 12346
                receipt.blockHash = MagicMock()
                receipt.blockHash.hex.return_value = "0xfedcba"
                receipt.transactionIndex = 1
                receipt.gasUsed = 21000
                return receipt
            else:
                # 未确认的交易
                return None
        
        mock_web3.eth.get_transaction_receipt.side_effect = mock_get_receipt
        
        # 添加回调
        callback_results = {}
        
        def create_callback(tx_hash):
            def callback(tx_info):
                callback_results[tx_hash] = tx_info.status
            return callback
        
        for tx_hash in tx_hashes:
            transaction_manager.add_transaction_callback(tx_hash, create_callback(tx_hash))
        
        # 运行一次监控循环
        await transaction_manager._monitor_transactions_once()
        
        # 验证结果
        assert callback_results["0x123"] == TransactionStatus.CONFIRMED
        assert callback_results["0x456"] == TransactionStatus.FAILED
        assert "0x789" not in callback_results  # 未确认的交易不应该有回调
        
        # 验证待确认交易列表
        assert "0x123" not in transaction_manager.pending_transactions
        assert "0x456" not in transaction_manager.pending_transactions
        assert "0x789" in transaction_manager.pending_transactions 