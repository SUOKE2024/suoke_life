"""
区块链客户端模块

提供与以太坊区块链的集成功能，包括智能合约交互、交易处理等。
"""

import asyncio
import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

import aiofiles
from eth_account import Account
from eth_utils import is_address, to_checksum_address
from web3 import Web3
from web3.contract import Contract
from web3.exceptions import TransactionNotFound

from ..config.settings import get_settings
from ..core.exceptions import ContractError, NetworkError, ValidationError
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TransactionReceipt:
    """交易回执"""
    transaction_hash: str
    block_number: int
    block_hash: str
    gas_used: int
    status: int
    contract_address: str | None = None
    logs: list[dict[str, Any]] | None = None


@dataclass
class ContractInfo:
    """合约信息"""
    name: str
    address: str
    abi: list[dict[str, Any]]
    contract: Contract


class BlockchainClient:
    """区块链客户端"""

    def __init__(self) -> None:
        """初始化区块链客户端"""
        self.settings = get_settings()
        self.w3: Web3 | None = None
        self.contracts: dict[str, ContractInfo] = {}
        self.account: Account | None = None
        self._is_connected = False

    async def initialize(self) -> None:
        """初始化区块链客户端"""
        try:
            logger.info("初始化区块链客户端", extra={
                "node_url": self.settings.blockchain.eth_node_url
            })

            # 连接到以太坊节点
            self.w3 = Web3(Web3.HTTPProvider(self.settings.blockchain.eth_node_url))

            # 检查连接
            if not self.w3.is_connected():
                raise NetworkError("无法连接到以太坊节点")

            # 验证链ID
            chain_id = self.w3.eth.chain_id
            if chain_id != self.settings.blockchain.chain_id:
                logger.warning("链ID不匹配", extra={
                    "expected": self.settings.blockchain.chain_id,
                    "actual": chain_id
                })

            # 设置账户
            if self.settings.blockchain.deployer_private_key:
                self.account = Account.from_key(self.settings.blockchain.deployer_private_key)
                logger.info("账户已设置", extra={"address": self.account.address})

            # 加载智能合约
            await self._load_contracts()

            self._is_connected = True
            logger.info("区块链客户端初始化完成")

        except Exception as e:
            logger.error("区块链客户端初始化失败", extra={"error": str(e)})
            raise NetworkError(f"区块链客户端初始化失败: {str(e)}")

    async def _load_contracts(self) -> None:
        """加载智能合约"""
        contracts_config = [
            {
                "name": "HealthDataStorage",
                "address": self.settings.blockchain.health_data_storage_address,
                "abi_file": "contracts/HealthDataStorage.json"
            },
            {
                "name": "ZKPVerifier",
                "address": self.settings.blockchain.zkp_verifier_address,
                "abi_file": "contracts/ZKPVerifier.json"
            },
            {
                "name": "AccessControl",
                "address": self.settings.blockchain.access_control_address,
                "abi_file": "contracts/AccessControl.json"
            }
        ]

        for contract_config in contracts_config:
            if contract_config["address"]:
                try:
                    await self._load_contract(
                        contract_config["name"],
                        contract_config["address"],
                        contract_config["abi_file"]
                    )
                except Exception as e:
                    logger.warning("加载合约失败", extra={
                        "contract": contract_config["name"],
                        "error": str(e)
                    })

    async def _load_contract(self, name: str, address: str, abi_file: str) -> None:
        """加载单个智能合约"""
        try:
            # 读取ABI文件
            abi = await self._read_contract_abi(abi_file)

            # 验证地址
            if not is_address(address):
                raise ValidationError(f"无效的合约地址: {address}")

            checksum_address = to_checksum_address(address)

            # 创建合约实例
            contract = self.w3.eth.contract(
                address=checksum_address,
                abi=abi
            )

            # 存储合约信息
            self.contracts[name] = ContractInfo(
                name=name,
                address=checksum_address,
                abi=abi,
                contract=contract
            )

            logger.info("合约加载成功", extra={
                "name": name,
                "address": checksum_address
            })

        except Exception as e:
            logger.error("加载合约失败", extra={
                "name": name,
                "address": address,
                "error": str(e)
            })
            raise ContractError(f"加载合约失败: {str(e)}")

    async def _read_contract_abi(self, abi_file: str) -> list[dict[str, Any]]:
        """读取合约ABI文件"""
        try:
            # 构建文件路径
            base_path = Path(__file__).parent.parent.parent
            abi_path = base_path / abi_file

            if not abi_path.exists():
                raise FileNotFoundError(f"ABI文件不存在: {abi_path}")

            # 异步读取文件
            async with aiofiles.open(abi_path, encoding='utf-8') as f:
                content = await f.read()
                abi_data = json.loads(content)

            # 提取ABI（支持不同的文件格式）
            if isinstance(abi_data, list):
                return abi_data
            elif isinstance(abi_data, dict) and 'abi' in abi_data:
                return abi_data['abi']
            else:
                raise ValueError("无效的ABI文件格式")

        except Exception as e:
            logger.error("读取ABI文件失败", extra={
                "file": abi_file,
                "error": str(e)
            })
            raise ContractError(f"读取ABI文件失败: {str(e)}")

    async def send_transaction(
        self,
        contract_name: str,
        function_name: str,
        *args,
        **kwargs
    ) -> TransactionReceipt:
        """发送交易"""
        if not self._is_connected:
            raise NetworkError("区块链客户端未连接")

        if not self.account:
            raise ValidationError("未设置账户")

        if contract_name not in self.contracts:
            raise ContractError(f"合约未找到: {contract_name}")

        try:
            contract = self.contracts[contract_name].contract
            function = getattr(contract.functions, function_name)

            # 构建交易
            transaction = function(*args).build_transaction({
                'from': self.account.address,
                'gas': self.settings.blockchain.gas_limit,
                'gasPrice': self.settings.blockchain.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                **kwargs
            })

            # 签名交易
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction,
                private_key=self.account.key
            )

            # 发送交易
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

            logger.info("交易已发送", extra={
                "tx_hash": tx_hash.hex(),
                "contract": contract_name,
                "function": function_name
            })

            # 等待交易确认
            receipt = await self._wait_for_transaction_receipt(tx_hash)

            return TransactionReceipt(
                transaction_hash=receipt['transactionHash'].hex(),
                block_number=receipt['blockNumber'],
                block_hash=receipt['blockHash'].hex(),
                gas_used=receipt['gasUsed'],
                status=receipt['status'],
                contract_address=receipt.get('contractAddress'),
                logs=receipt.get('logs', [])
            )

        except Exception as e:
            logger.error("发送交易失败", extra={
                "contract": contract_name,
                "function": function_name,
                "error": str(e)
            })
            raise NetworkError(f"发送交易失败: {str(e)}")

    async def _wait_for_transaction_receipt(self, tx_hash) -> dict[str, Any]:
        """等待交易确认"""
        timeout = self.settings.blockchain.transaction_timeout
        start_time = asyncio.get_event_loop().time()

        while True:
            try:
                receipt = self.w3.eth.get_transaction_receipt(tx_hash)

                # 检查确认数
                current_block = self.w3.eth.block_number
                confirmations = current_block - receipt['blockNumber']

                if confirmations >= self.settings.blockchain.confirmation_blocks:
                    return receipt

            except TransactionNotFound:
                pass

            # 检查超时
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise NetworkError(f"交易确认超时: {tx_hash.hex()}")

            await asyncio.sleep(1)

    async def call_contract_function(
        self,
        contract_name: str,
        function_name: str,
        *args,
        **kwargs
    ) -> Any:
        """调用合约只读函数"""
        if not self._is_connected:
            raise NetworkError("区块链客户端未连接")

        if contract_name not in self.contracts:
            raise ContractError(f"合约未找到: {contract_name}")

        try:
            contract = self.contracts[contract_name].contract
            function = getattr(contract.functions, function_name)
            result = function(*args).call(**kwargs)

            logger.debug("合约函数调用成功", extra={
                "contract": contract_name,
                "function": function_name
            })

            return result

        except Exception as e:
            logger.error("合约函数调用失败", extra={
                "contract": contract_name,
                "function": function_name,
                "error": str(e)
            })
            raise ContractError(f"合约函数调用失败: {str(e)}")

    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._is_connected and self.w3 and self.w3.is_connected()

    async def get_balance(self, address: str) -> Decimal:
        """获取地址余额"""
        if not self._is_connected:
            raise NetworkError("区块链客户端未连接")

        try:
            balance_wei = self.w3.eth.get_balance(address)
            balance_eth = self.w3.from_wei(balance_wei, 'ether')
            return Decimal(str(balance_eth))

        except Exception as e:
            logger.error("获取余额失败", extra={
                "address": address,
                "error": str(e)
            })
            raise NetworkError(f"获取余额失败: {str(e)}")

    async def close(self) -> None:
        """关闭连接"""
        self._is_connected = False
        self.w3 = None
        self.contracts.clear()
        logger.info("区块链客户端已关闭")


# 全局客户端实例
_blockchain_client: BlockchainClient | None = None


async def get_blockchain_client() -> BlockchainClient:
    """获取区块链客户端实例"""
    global _blockchain_client

    if _blockchain_client is None:
        _blockchain_client = BlockchainClient()
        await _blockchain_client.initialize()

    return _blockchain_client
