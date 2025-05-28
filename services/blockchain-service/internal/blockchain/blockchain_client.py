#!/usr/bin/env python3

"""
区块链客户端模块

该模块提供与区块链网络交互的低级操作，如交易发送、事件监听等。
"""

import asyncio
from collections.abc import Callable
import json
import logging
import time
from typing import Any

from eth_account import Account
from eth_account.signers.local import LocalAccount
from hexbytes import HexBytes
from web3 import Web3
from web3.exceptions import BlockNotFound, ContractLogicError, TransactionNotFound
from web3.middleware import construct_sign_and_send_raw_middleware, geth_poa_middleware

from internal.model.config import AppConfig
from internal.model.entities import Transaction, TransactionStatus


class BlockchainClient:
    """区块链客户端类，提供与区块链交互的底层功能"""

    def __init__(self, config: AppConfig):
        """
        初始化区块链客户端
        
        Args:
            config: 应用配置对象
        """
        self.logger = logging.getLogger(__name__)
        self.config = config

        # 初始化Web3
        self._init_web3()

        # 加载账户
        self._load_account()

        # 事件处理器映射
        self.event_handlers: dict[str, list[Callable]] = {}

        self.logger.info(f"区块链客户端初始化成功: 连接状态={self.web3.is_connected()}, 网络ID={self.web3.net.version}")

    def _init_web3(self):
        """初始化Web3连接"""
        try:
            provider_url = self.config.blockchain.node.endpoint

            if provider_url.startswith("http"):
                provider = Web3.HTTPProvider(provider_url, request_kwargs={"timeout": 30})
                self.web3 = Web3(provider)
            elif provider_url.startswith("ws"):
                provider = Web3.WebsocketProvider(provider_url)
                self.web3 = Web3(provider)
            else:
                raise ValueError(f"不支持的提供者URL: {provider_url}")

            # 添加POA中间件(如果需要)
            if self.config.blockchain.node.is_poa:
                self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)

            # 检查连接
            if not self.web3.is_connected():
                raise ConnectionError(f"无法连接到区块链节点: {provider_url}")

            self.logger.info(f"Web3连接初始化成功: 端点={provider_url}")
        except Exception as e:
            self.logger.error(f"初始化Web3连接失败: {e!s}")
            raise

    def _load_account(self):
        """加载账户并设置签名中间件"""
        try:
            # 从配置加载账户
            if self.config.blockchain.wallet.use_keystore_file:
                # 从文件加载账户密钥
                keystore_path = self.config.blockchain.wallet.keystore_path

                with open(f"{keystore_path}/private_key.json") as f:
                    encrypted_key = json.load(f)

                with open(f"{keystore_path}/password.txt") as f:
                    password = f.read().strip()

                self.account: LocalAccount = Account.from_key(
                    Web3.to_hex(HexBytes(encrypted_key["private_key"]))
                )
            else:
                # 直接从配置加载私钥
                private_key = self.config.blockchain.wallet.private_key
                self.account: LocalAccount = Account.from_key(private_key)

            # 设置签名中间件
            self.web3.middleware_onion.add(
                construct_sign_and_send_raw_middleware(self.account)
            )

            self.logger.info(f"加载账户成功: {self.account.address}")
        except Exception as e:
            self.logger.error(f"加载账户失败: {e!s}")
            raise

    async def send_transaction(
        self,
        to_address: str,
        data: HexBytes = None,
        value: int = 0,
        gas_limit: int = None,
        gas_price_multiplier: float = 1.0,
        nonce: int = None
    ) -> tuple[str, Transaction]:
        """
        发送交易到区块链
        
        Args:
            to_address: 接收者地址
            data: 交易数据
            value: 发送的以太币数量(单位: wei)
            gas_limit: 燃料限制
            gas_price_multiplier: 燃料价格乘数
            nonce: 交易nonce，如果为None则自动获取
            
        Returns:
            (交易哈希, 交易记录)
        """
        try:
            # 准备交易参数
            tx_params = {
                "from": self.account.address,
                "to": Web3.to_checksum_address(to_address),
                "chainId": self.config.blockchain.node.chain_id,
                "gasPrice": int(self.web3.eth.gas_price * gas_price_multiplier),
                "value": value
            }

            # 设置交易数据
            if data:
                tx_params["data"] = data

            # 设置nonce
            if nonce is None:
                tx_params["nonce"] = self.web3.eth.get_transaction_count(self.account.address)
            else:
                tx_params["nonce"] = nonce

            # 设置燃料限制
            if gas_limit:
                tx_params["gas"] = gas_limit
            else:
                # 自动估算燃料限制
                gas_estimate = self.web3.eth.estimate_gas(tx_params)
                tx_params["gas"] = int(gas_estimate * 1.1)  # 添加10%的缓冲

            # 签名并发送交易
            signed_tx = self.account.sign_transaction(tx_params)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)

            # 等待交易确认
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

            # 创建交易记录
            transaction = Transaction(
                transaction_id=tx_hash.hex(),
                block_hash=tx_receipt.blockHash.hex() if tx_receipt.blockHash else None,
                block_number=tx_receipt.blockNumber if tx_receipt.blockNumber else None,
                status=TransactionStatus.CONFIRMED if tx_receipt.status else TransactionStatus.FAILED,
                timestamp=int(time.time()),
                gas_used=tx_receipt.gasUsed
            )

            self.logger.info(f"交易发送成功: hash={tx_hash.hex()}, status={transaction.status.value}")
            return tx_hash.hex(), transaction

        except Exception as e:
            self.logger.error(f"发送交易失败: {e!s}")
            # 创建失败的交易记录
            transaction = Transaction(
                transaction_id="0x0",
                status=TransactionStatus.FAILED,
                timestamp=int(time.time()),
                gas_used=0
            )
            raise

    async def get_transaction_details(self, tx_hash: str) -> dict[str, Any]:
        """
        获取交易详细信息
        
        Args:
            tx_hash: 交易哈希
            
        Returns:
            交易详细信息字典
        """
        try:
            # 获取交易信息
            tx = self.web3.eth.get_transaction(tx_hash)

            # 获取交易收据
            try:
                receipt = self.web3.eth.get_transaction_receipt(tx_hash)
                receipt_data = {
                    "blockHash": receipt.blockHash.hex() if receipt.blockHash else None,
                    "blockNumber": receipt.blockNumber,
                    "contractAddress": receipt.contractAddress if receipt.contractAddress else None,
                    "cumulativeGasUsed": receipt.cumulativeGasUsed,
                    "effectiveGasPrice": receipt.effectiveGasPrice,
                    "gasUsed": receipt.gasUsed,
                    "status": receipt.status,
                    "logs": [log.args for log in receipt.logs] if hasattr(receipt, "logs") else []
                }
            except TransactionNotFound:
                receipt_data = {"status": "pending"}

            # 构建详细信息
            details = {
                "hash": tx_hash,
                "from": tx["from"],
                "to": tx["to"],
                "value": tx["value"],
                "gas": tx["gas"],
                "gasPrice": tx["gasPrice"],
                "nonce": tx["nonce"],
                "data": tx["input"],
                "receipt": receipt_data
            }

            return details

        except TransactionNotFound:
            self.logger.warning(f"交易未找到: {tx_hash}")
            return {"hash": tx_hash, "status": "not_found"}
        except Exception as e:
            self.logger.error(f"获取交易详情失败: {e!s}")
            raise

    async def get_block_by_number(self, block_number: int) -> dict[str, Any]:
        """
        根据区块号获取区块信息
        
        Args:
            block_number: 区块号
            
        Returns:
            区块信息字典
        """
        try:
            block = self.web3.eth.get_block(block_number, full_transactions=True)

            # 构建区块信息
            block_info = {
                "number": block.number,
                "hash": block.hash.hex(),
                "parentHash": block.parentHash.hex(),
                "timestamp": block.timestamp,
                "gasUsed": block.gasUsed,
                "gasLimit": block.gasLimit,
                "transactions": [tx.hash.hex() for tx in block.transactions]
            }

            return block_info

        except BlockNotFound:
            self.logger.warning(f"区块未找到: {block_number}")
            return {"number": block_number, "status": "not_found"}
        except Exception as e:
            self.logger.error(f"获取区块信息失败: {e!s}")
            raise

    async def get_balance(self, address: str = None) -> int:
        """
        获取账户余额
        
        Args:
            address: 账户地址，如果为None则使用当前账户
            
        Returns:
            账户余额(单位: wei)
        """
        try:
            if address is None:
                address = self.account.address

            balance = self.web3.eth.get_balance(Web3.to_checksum_address(address))
            return balance

        except Exception as e:
            self.logger.error(f"获取账户余额失败: {e!s}")
            raise

    async def register_event_handler(self, event_name: str, handler: Callable):
        """
        注册事件处理器
        
        Args:
            event_name: 事件名称
            handler: 事件处理函数
        """
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []

        self.event_handlers[event_name].append(handler)
        self.logger.info(f"注册事件处理器成功: {event_name}")

    async def start_event_listener(self, contract, event_name: str, from_block: int = 0, filters: dict = None):
        """
        启动事件监听器
        
        Args:
            contract: 合约实例
            event_name: 事件名称
            from_block: 开始区块
            filters: 事件过滤条件
        """
        try:
            # 获取事件对象
            event = getattr(contract.events, event_name)

            # 创建事件过滤器
            event_filter = event.create_filter(
                fromBlock=from_block,
                toBlock="latest",
                argument_filters=filters
            )

            # 启动事件监听循环
            asyncio.create_task(self._poll_events(event_filter, event_name))

            self.logger.info(f"启动事件监听器: {event_name}, from_block={from_block}")

        except Exception as e:
            self.logger.error(f"启动事件监听器失败: {e!s}")
            raise

    async def _poll_events(self, event_filter, event_name: str):
        """
        轮询事件
        
        Args:
            event_filter: 事件过滤器
            event_name: 事件名称
        """
        poll_interval = self.config.blockchain.events.poll_interval

        while True:
            try:
                # 获取新事件
                for event in event_filter.get_new_entries():
                    # 处理事件
                    if event_name in self.event_handlers:
                        for handler in self.event_handlers[event_name]:
                            try:
                                asyncio.create_task(handler(event))
                            except Exception as e:
                                self.logger.error(f"事件处理器异常: {e!s}")

                # 等待下次轮询
                await asyncio.sleep(poll_interval)

            except Exception as e:
                self.logger.error(f"轮询事件异常: {e!s}")
                await asyncio.sleep(poll_interval * 2)  # 出错后等待更长时间

    async def get_latest_block_number(self) -> int:
        """
        获取最新区块号
        
        Returns:
            最新区块号
        """
        try:
            return self.web3.eth.block_number
        except Exception as e:
            self.logger.error(f"获取最新区块号失败: {e!s}")
            raise

    async def is_contract(self, address: str) -> bool:
        """
        检查地址是否为合约
        
        Args:
            address: 检查的地址
            
        Returns:
            是否为合约地址
        """
        try:
            code = self.web3.eth.get_code(Web3.to_checksum_address(address))
            return code != HexBytes("0x")
        except Exception as e:
            self.logger.error(f"检查合约地址失败: {e!s}")
            return False

    async def estimate_gas(self, tx_params: dict[str, Any]) -> int:
        """
        估算交易所需燃料
        
        Args:
            tx_params: 交易参数
            
        Returns:
            燃料估算值
        """
        try:
            gas_estimate = self.web3.eth.estimate_gas(tx_params)
            return gas_estimate
        except ContractLogicError as e:
            self.logger.error(f"合约逻辑错误，燃料估算失败: {e!s}")
            raise
        except Exception as e:
            self.logger.error(f"估算燃料失败: {e!s}")
            raise

    def get_web3(self) -> Web3:
        """获取Web3实例"""
        return self.web3

    def get_account(self) -> LocalAccount:
        """获取账户实例"""
        return self.account
