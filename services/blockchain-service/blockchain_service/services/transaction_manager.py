"""
交易管理器

提供区块链交易的创建、发送、监控和管理功能。
"""

import asyncio
import contextlib
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from eth_account import Account
from web3 import Web3
from web3.types import TxReceipt

from ..config.settings import get_settings
from ..core.exceptions import NetworkError, ValidationError
from ..utils.logger import get_logger
from ..utils.retry import async_retry

logger = get_logger(__name__)


class TransactionStatus(Enum):
    """交易状态枚举"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class TransactionInfo:
    """交易信息"""
    hash: str
    from_address: str
    to_address: str
    value: int
    gas: int
    gas_price: int
    nonce: int
    status: TransactionStatus
    block_number: int | None = None
    block_hash: str | None = None
    transaction_index: int | None = None
    gas_used: int | None = None
    created_at: datetime = None
    confirmed_at: datetime | None = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class TransactionManager:
    """交易管理器"""

    def __init__(self, web3: Web3):
        """
        初始化交易管理器

        Args:
            web3: Web3 实例
        """
        self.web3 = web3
        self.settings = get_settings()
        self.pending_transactions: dict[str, TransactionInfo] = {}
        self.transaction_callbacks: dict[str, list[Callable]] = {}
        self._monitoring_task: asyncio.Task | None = None

    async def start_monitoring(self):
        """启动交易监控"""
        if self._monitoring_task is None or self._monitoring_task.done():
            self._monitoring_task = asyncio.create_task(self._monitor_transactions())
            logger.info("交易监控已启动")

    async def stop_monitoring(self):
        """停止交易监控"""
        if self._monitoring_task and not self._monitoring_task.done():
            self._monitoring_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._monitoring_task
            logger.info("交易监控已停止")

    async def send_transaction(
        self,
        to_address: str,
        value: int = 0,
        data: bytes = b'',
        private_key: str | None = None,
        gas: int | None = None,
        gas_price: int | None = None,
        nonce: int | None = None
    ) -> str:
        """
        发送交易

        Args:
            to_address: 接收地址
            value: 转账金额（wei）
            data: 交易数据
            private_key: 发送方私钥
            gas: Gas 限制
            gas_price: Gas 价格
            nonce: 交易序号

        Returns:
            交易哈希

        Raises:
            NetworkError: 网络错误
            ValidationError: 参数验证错误
        """
        try:
            # 验证地址
            if not Web3.is_address(to_address):
                raise ValidationError(f"Invalid to_address: {to_address}")

            # 获取发送账户
            if private_key:
                account = Account.from_key(private_key)
                from_address = account.address
            else:
                from_address = self.web3.eth.accounts[0]

            # 获取交易参数
            if nonce is None:
                nonce = self.web3.eth.get_transaction_count(from_address)

            if gas is None:
                gas = self.settings.blockchain.gas_limit

            if gas_price is None:
                gas_price = self.settings.blockchain.gas_price

            # 构建交易
            transaction = {
                'to': to_address,
                'value': value,
                'gas': gas,
                'gasPrice': gas_price,
                'nonce': nonce,
                'data': data
            }

            # 签名并发送交易
            if private_key:
                signed_txn = self.web3.eth.account.sign_transaction(transaction, private_key)
                tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            else:
                transaction['from'] = from_address
                tx_hash = self.web3.eth.send_transaction(transaction)

            tx_hash_hex = tx_hash.hex()

            # 创建交易信息
            tx_info = TransactionInfo(
                hash=tx_hash_hex,
                from_address=from_address,
                to_address=to_address,
                value=value,
                gas=gas,
                gas_price=gas_price,
                nonce=nonce,
                status=TransactionStatus.PENDING
            )

            # 添加到待确认列表
            self.pending_transactions[tx_hash_hex] = tx_info

            logger.info(f"交易发送成功: {tx_hash_hex}")
            return tx_hash_hex

        except Exception as e:
            logger.error(f"发送交易失败: {str(e)}")
            raise NetworkError(f"Failed to send transaction: {str(e)}")

    @async_retry(max_attempts=3, delay=1.0)
    async def get_transaction_receipt(self, tx_hash: str) -> TxReceipt | None:
        """
        获取交易回执

        Args:
            tx_hash: 交易哈希

        Returns:
            交易回执或None
        """
        try:
            receipt = self.web3.eth.get_transaction_receipt(tx_hash)
            return receipt
        except Exception as e:
            logger.debug(f"获取交易回执失败: {tx_hash}, 错误: {str(e)}")
            return None

    async def wait_for_confirmation(
        self,
        tx_hash: str,
        timeout: int = 300,
        confirmations: int = 1
    ) -> TransactionInfo:
        """
        等待交易确认

        Args:
            tx_hash: 交易哈希
            timeout: 超时时间（秒）
            confirmations: 确认数

        Returns:
            交易信息

        Raises:
            NetworkError: 网络错误或超时
        """
        start_time = datetime.utcnow()
        timeout_delta = timedelta(seconds=timeout)

        while datetime.utcnow() - start_time < timeout_delta:
            try:
                receipt = await self.get_transaction_receipt(tx_hash)

                if receipt:
                    current_block = self.web3.eth.block_number
                    confirmations_count = current_block - receipt.blockNumber + 1

                    if confirmations_count >= confirmations:
                        # 更新交易信息
                        if tx_hash in self.pending_transactions:
                            tx_info = self.pending_transactions[tx_hash]
                            tx_info.status = TransactionStatus.CONFIRMED if receipt.status == 1 else TransactionStatus.FAILED
                            tx_info.block_number = receipt.blockNumber
                            tx_info.block_hash = receipt.blockHash.hex()
                            tx_info.transaction_index = receipt.transactionIndex
                            tx_info.gas_used = receipt.gasUsed
                            tx_info.confirmed_at = datetime.utcnow()

                            # 从待确认列表中移除
                            del self.pending_transactions[tx_hash]

                            # 执行回调
                            await self._execute_callbacks(tx_hash, tx_info)

                            return tx_info
                        else:
                            # 创建新的交易信息
                            tx = self.web3.eth.get_transaction(tx_hash)
                            tx_info = TransactionInfo(
                                hash=tx_hash,
                                from_address=tx['from'],
                                to_address=tx['to'],
                                value=tx['value'],
                                gas=tx['gas'],
                                gas_price=tx['gasPrice'],
                                nonce=tx['nonce'],
                                status=TransactionStatus.CONFIRMED if receipt.status == 1 else TransactionStatus.FAILED,
                                block_number=receipt.blockNumber,
                                block_hash=receipt.blockHash.hex(),
                                transaction_index=receipt.transactionIndex,
                                gas_used=receipt.gasUsed,
                                confirmed_at=datetime.utcnow()
                            )

                            return tx_info

                # 等待一段时间后重试
                await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"等待交易确认时出错: {tx_hash}, 错误: {str(e)}")
                await asyncio.sleep(2)

        # 超时处理
        if tx_hash in self.pending_transactions:
            tx_info = self.pending_transactions[tx_hash]
            tx_info.status = TransactionStatus.TIMEOUT
            del self.pending_transactions[tx_hash]

            await self._execute_callbacks(tx_hash, tx_info)
            return tx_info

        raise NetworkError(f"Transaction confirmation timeout: {tx_hash}")

    def add_transaction_callback(self, tx_hash: str, callback: Callable[[TransactionInfo], None]):
        """
        添加交易回调函数

        Args:
            tx_hash: 交易哈希
            callback: 回调函数
        """
        if tx_hash not in self.transaction_callbacks:
            self.transaction_callbacks[tx_hash] = []

        self.transaction_callbacks[tx_hash].append(callback)

    async def _execute_callbacks(self, tx_hash: str, tx_info: TransactionInfo):
        """执行交易回调"""
        if tx_hash in self.transaction_callbacks:
            callbacks = self.transaction_callbacks[tx_hash]

            for callback in callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(tx_info)
                    else:
                        callback(tx_info)
                except Exception as e:
                    logger.error(f"执行交易回调失败: {tx_hash}, 错误: {str(e)}")

            # 清理回调
            del self.transaction_callbacks[tx_hash]

    async def _monitor_transactions(self):
        """监控待确认交易"""
        while True:
            try:
                await self._monitor_transactions_once()
                # 等待下次检查
                await asyncio.sleep(5)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"交易监控出错: {str(e)}")
                await asyncio.sleep(5)

    async def _monitor_transactions_once(self):
        """执行一次交易监控检查"""
        # 复制待确认交易列表以避免并发修改
        pending_txs = list(self.pending_transactions.items())

        for tx_hash, tx_info in pending_txs:
            try:
                # 检查交易是否超时
                if datetime.utcnow() - tx_info.created_at > timedelta(minutes=10):
                    tx_info.status = TransactionStatus.TIMEOUT
                    del self.pending_transactions[tx_hash]
                    await self._execute_callbacks(tx_hash, tx_info)
                    continue

                # 检查交易状态
                receipt = await self.get_transaction_receipt(tx_hash)
                if receipt:
                    tx_info.status = TransactionStatus.CONFIRMED if receipt.status == 1 else TransactionStatus.FAILED
                    tx_info.block_number = receipt.blockNumber
                    tx_info.block_hash = receipt.blockHash.hex()
                    tx_info.transaction_index = receipt.transactionIndex
                    tx_info.gas_used = receipt.gasUsed
                    tx_info.confirmed_at = datetime.utcnow()

                    del self.pending_transactions[tx_hash]
                    await self._execute_callbacks(tx_hash, tx_info)

            except Exception as e:
                logger.error(f"监控交易时出错: {tx_hash}, 错误: {str(e)}")

    def get_pending_transactions(self) -> list[TransactionInfo]:
        """获取待确认交易列表"""
        return list(self.pending_transactions.values())

    def get_transaction_info(self, tx_hash: str) -> TransactionInfo | None:
        """获取交易信息"""
        return self.pending_transactions.get(tx_hash)
