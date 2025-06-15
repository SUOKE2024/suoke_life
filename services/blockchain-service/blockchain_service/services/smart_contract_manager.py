"""
智能合约管理器

提供智能合约的部署、交互和管理功能。
"""

import json
from typing import Any

from eth_account import Account
from web3 import Web3
from web3.contract import Contract

from ..config.settings import get_settings
from ..core.exceptions import ContractError
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SmartContractManager:
    """智能合约管理器"""

    def __init__(self, web3: Web3):
        """
        初始化智能合约管理器

        Args:
            web3: Web3 实例
        """
        self.web3 = web3
        self.settings = get_settings()
        self.contracts: dict[str, Contract] = {}
        self.contract_addresses: dict[str, str] = {}

    async def deploy_contract(
        self,
        contract_name: str,
        contract_source: str,
        constructor_args: list[Any] | None = None,
        private_key: str | None = None
    ) -> str:
        """
        部署智能合约

        Args:
            contract_name: 合约名称
            contract_source: 合约源代码或ABI
            constructor_args: 构造函数参数
            private_key: 部署账户私钥

        Returns:
            合约地址

        Raises:
            ContractError: 合约部署失败
        """
        try:
            logger.info(f"开始部署合约: {contract_name}")

            # 编译合约（这里简化处理，实际应该使用solc编译）
            contract_abi, contract_bytecode = self._compile_contract(contract_source)

            # 创建合约实例
            contract = self.web3.eth.contract(
                abi=contract_abi,
                bytecode=contract_bytecode
            )

            # 获取部署账户
            if private_key:
                account = Account.from_key(private_key)
                deployer_address = account.address
            else:
                deployer_address = self.web3.eth.accounts[0]

            # 构建部署交易
            constructor_args = constructor_args or []
            transaction = contract.constructor(*constructor_args).build_transaction({
                'from': deployer_address,
                'gas': self.settings.blockchain.gas_limit,
                'gasPrice': self.settings.blockchain.gas_price,
                'nonce': self.web3.eth.get_transaction_count(deployer_address)
            })

            # 签名并发送交易
            if private_key:
                signed_txn = self.web3.eth.account.sign_transaction(transaction, private_key)
                tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            else:
                tx_hash = self.web3.eth.send_transaction(transaction)

            # 等待交易确认
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)

            if receipt.status != 1:
                raise ContractError(f"合约部署失败: {contract_name}")

            contract_address = receipt.contractAddress
            logger.info(f"合约部署成功: {contract_name} at {contract_address}")

            # 保存合约信息
            self.contract_addresses[contract_name] = contract_address
            self.contracts[contract_name] = self.web3.eth.contract(
                address=contract_address,
                abi=contract_abi
            )

            return contract_address

        except Exception as e:
            logger.error(f"部署合约失败: {contract_name}, 错误: {str(e)}")
            raise ContractError(f"Failed to deploy contract {contract_name}: {str(e)}")

    def load_contract(self, contract_name: str, address: str, abi: list[dict]) -> Contract:
        """
        加载已部署的合约

        Args:
            contract_name: 合约名称
            address: 合约地址
            abi: 合约ABI

        Returns:
            合约实例
        """
        try:
            contract = self.web3.eth.contract(address=address, abi=abi)
            self.contracts[contract_name] = contract
            self.contract_addresses[contract_name] = address

            logger.info(f"加载合约成功: {contract_name} at {address}")
            return contract

        except Exception as e:
            logger.error(f"加载合约失败: {contract_name}, 错误: {str(e)}")
            raise ContractError(f"Failed to load contract {contract_name}: {str(e)}")

    async def call_contract_function(
        self,
        contract_name: str,
        function_name: str,
        *args,
        **kwargs
    ) -> Any:
        """
        调用合约只读函数

        Args:
            contract_name: 合约名称
            function_name: 函数名称
            *args: 函数参数
            **kwargs: 额外参数

        Returns:
            函数返回值
        """
        try:
            if contract_name not in self.contracts:
                raise ContractError(f"Contract {contract_name} not loaded")

            contract = self.contracts[contract_name]
            function = getattr(contract.functions, function_name)

            result = function(*args).call()
            logger.debug(f"调用合约函数成功: {contract_name}.{function_name}")

            return result

        except Exception as e:
            logger.error(f"调用合约函数失败: {contract_name}.{function_name}, 错误: {str(e)}")
            raise ContractError(f"Failed to call function {function_name}: {str(e)}")

    async def send_contract_transaction(
        self,
        contract_name: str,
        function_name: str,
        *args,
        private_key: str | None = None,
        **kwargs
    ) -> str:
        """
        发送合约交易

        Args:
            contract_name: 合约名称
            function_name: 函数名称
            *args: 函数参数
            private_key: 发送方私钥
            **kwargs: 额外参数

        Returns:
            交易哈希
        """
        try:
            if contract_name not in self.contracts:
                raise ContractError(f"Contract {contract_name} not loaded")

            contract = self.contracts[contract_name]
            function = getattr(contract.functions, function_name)

            # 获取发送账户
            if private_key:
                account = Account.from_key(private_key)
                sender_address = account.address
            else:
                sender_address = self.web3.eth.accounts[0]

            # 构建交易
            transaction = function(*args).build_transaction({
                'from': sender_address,
                'gas': kwargs.get('gas', self.settings.blockchain.gas_limit),
                'gasPrice': kwargs.get('gasPrice', self.settings.blockchain.gas_price),
                'nonce': self.web3.eth.get_transaction_count(sender_address)
            })

            # 签名并发送交易
            if private_key:
                signed_txn = self.web3.eth.account.sign_transaction(transaction, private_key)
                tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            else:
                tx_hash = self.web3.eth.send_transaction(transaction)

            # 处理交易哈希格式
            if hasattr(tx_hash, 'hex'):
                tx_hash_str = tx_hash.hex()
            else:
                tx_hash_str = str(tx_hash)
            
            logger.info(f"发送合约交易成功: {contract_name}.{function_name}, tx: {tx_hash_str}")
            return tx_hash_str

        except Exception as e:
            logger.error(f"发送合约交易失败: {contract_name}.{function_name}, 错误: {str(e)}")
            raise ContractError(f"Failed to send transaction {function_name}: {str(e)}")

    def get_contract_events(
        self,
        contract_name: str,
        event_name: str,
        from_block: int = 0,
        to_block: str = 'latest'
    ) -> list[dict]:
        """
        获取合约事件

        Args:
            contract_name: 合约名称
            event_name: 事件名称
            from_block: 起始区块
            to_block: 结束区块

        Returns:
            事件列表
        """
        try:
            if contract_name not in self.contracts:
                raise ContractError(f"Contract {contract_name} not loaded")

            contract = self.contracts[contract_name]
            event_filter = getattr(contract.events, event_name).create_filter(
                fromBlock=from_block,
                toBlock=to_block
            )

            events = event_filter.get_all_entries()
            logger.debug(f"获取合约事件成功: {contract_name}.{event_name}, 数量: {len(events)}")

            return [dict(event) for event in events]

        except Exception as e:
            logger.error(f"获取合约事件失败: {contract_name}.{event_name}, 错误: {str(e)}")
            raise ContractError(f"Failed to get events {event_name}: {str(e)}")

    def get_contract_info(self, contract_name: str) -> dict[str, Any]:
        """
        获取合约信息

        Args:
            contract_name: 合约名称

        Returns:
            合约信息
        """
        if contract_name not in self.contracts:
            raise ContractError(f"Contract {contract_name} not loaded")

        contract = self.contracts[contract_name]
        address = self.contract_addresses[contract_name]

        return {
            "name": contract_name,
            "address": address,
            "abi": contract.abi,
            "functions": list(contract.all_functions()),
            "events": list(contract.events)
        }

    def _compile_contract(self, contract_source: str) -> tuple[list[dict], str]:
        """
        编译合约（简化实现）

        Args:
            contract_source: 合约源代码或ABI文件路径

        Returns:
            (ABI, 字节码)
        """
        # 这里是简化实现，实际应该使用 py-solc-x 或其他编译器
        if contract_source.endswith('.json'):
            # 假设是已编译的合约文件
            with open(contract_source) as f:
                contract_data = json.load(f)
                return contract_data['abi'], contract_data['bytecode']
        else:
            # 简化的ABI和字节码（用于演示）
            demo_abi = [
                {
                    "inputs": [],
                    "name": "store",
                    "outputs": [],
                    "stateMutability": "nonpayable",
                    "type": "function"
                }
            ]
            demo_bytecode = "0x608060405234801561001057600080fd5b50"
            return demo_abi, demo_bytecode
