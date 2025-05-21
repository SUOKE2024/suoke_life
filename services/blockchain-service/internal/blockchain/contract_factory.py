#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能合约工厂模块

该模块负责智能合约的编译、部署和升级，提供对智能合约的生命周期管理。
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3 import Web3
from web3.exceptions import ContractLogicError
from web3.middleware import construct_sign_and_send_raw_middleware

from internal.model.config import AppConfig


class ContractFactory:
    """智能合约工厂类，负责智能合约的编译、部署和升级"""

    def __init__(self, config: AppConfig, web3: Web3, account: LocalAccount):
        """
        初始化合约工厂
        
        Args:
            config: 应用配置对象
            web3: Web3实例
            account: 账户实例
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.web3 = web3
        self.account = account
        
        # 智能合约ABI和字节码缓存
        self.contract_artifacts: Dict[str, Dict[str, Any]] = {}
        
        # 加载合约构件
        self._load_contract_artifacts()
    
    def _load_contract_artifacts(self):
        """加载智能合约ABI和字节码"""
        try:
            contracts_dir = Path(self.config.blockchain.contracts.artifacts_dir)
            
            for contract_file in contracts_dir.glob("*.json"):
                contract_name = contract_file.stem
                with contract_file.open("r") as f:
                    artifact = json.load(f)
                    self.contract_artifacts[contract_name] = artifact
            
            self.logger.info(f"已加载 {len(self.contract_artifacts)} 个智能合约构件")
        except Exception as e:
            self.logger.error(f"加载智能合约构件失败: {str(e)}")
            raise
    
    def get_contract(self, contract_name: str, address: str) -> web3.eth.Contract:
        """
        获取智能合约实例
        
        Args:
            contract_name: 合约名称
            address: 合约地址
            
        Returns:
            合约实例
        """
        if contract_name not in self.contract_artifacts:
            raise ValueError(f"合约不存在: {contract_name}")
        
        abi = self.contract_artifacts[contract_name]["abi"]
        return self.web3.eth.contract(
            address=Web3.to_checksum_address(address),
            abi=abi
        )
    
    async def deploy_contract(
        self, 
        contract_name: str, 
        constructor_args: List = None,
        gas_limit: int = None,
        gas_price_multiplier: float = 1.0
    ) -> Tuple[str, Dict[str, Any]]:
        """
        部署智能合约
        
        Args:
            contract_name: 合约名称
            constructor_args: 构造函数参数列表
            gas_limit: 燃料限制，如果为None则使用配置中的默认值
            gas_price_multiplier: 燃料价格乘数，用于调整燃料价格
            
        Returns:
            (合约地址, 部署信息)
        """
        try:
            if contract_name not in self.contract_artifacts:
                raise ValueError(f"合约不存在: {contract_name}")
            
            if constructor_args is None:
                constructor_args = []
            
            # 获取合约ABI和字节码
            contract_data = self.contract_artifacts[contract_name]
            abi = contract_data["abi"]
            bytecode = contract_data["bytecode"]
            
            # 创建合约构造函数
            contract = self.web3.eth.contract(abi=abi, bytecode=bytecode)
            
            # 准备部署交易
            tx_params = {
                'from': self.account.address,
                'nonce': self.web3.eth.get_transaction_count(self.account.address),
                'gasPrice': int(self.web3.eth.gas_price * gas_price_multiplier),
                'chainId': self.config.blockchain.node.chain_id,
            }
            
            # 设置燃料限制
            if gas_limit:
                tx_params['gas'] = gas_limit
            else:
                tx_params['gas'] = self.config.blockchain.wallet.gas_limit
            
            # 构建部署交易
            constructor = contract.constructor(*constructor_args)
            tx_data = constructor.build_transaction(tx_params)
            
            # 签名并发送交易
            signed_tx = self.account.sign_transaction(tx_data)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # 等待交易确认
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
            contract_address = tx_receipt.contractAddress
            
            # 构建部署信息
            deployment_info = {
                "contract_name": contract_name,
                "contract_address": contract_address,
                "transaction_hash": tx_receipt.transactionHash.hex(),
                "block_number": tx_receipt.blockNumber,
                "gas_used": tx_receipt.gasUsed,
                "status": "success" if tx_receipt.status == 1 else "failed",
                "constructor_args": constructor_args
            }
            
            self.logger.info(f"合约 {contract_name} 部署成功: {contract_address}")
            return contract_address, deployment_info
            
        except Exception as e:
            self.logger.error(f"部署合约 {contract_name} 失败: {str(e)}")
            raise
    
    async def upgrade_contract(
        self,
        proxy_address: str,
        new_implementation_name: str,
        upgrade_method: str = "upgradeTo",
        gas_limit: int = None,
        gas_price_multiplier: float = 1.0
    ) -> Tuple[str, Dict[str, Any]]:
        """
        升级可升级合约的实现
        
        Args:
            proxy_address: 代理合约地址
            new_implementation_name: 新实现合约名称
            upgrade_method: 升级方法名称
            gas_limit: 燃料限制
            gas_price_multiplier: 燃料价格乘数
            
        Returns:
            (交易哈希, 升级信息)
        """
        try:
            # 首先部署新的实现合约
            new_impl_address, deploy_info = await self.deploy_contract(
                contract_name=new_implementation_name,
                gas_limit=gas_limit,
                gas_price_multiplier=gas_price_multiplier
            )
            
            # 获取代理合约实例
            proxy_contract = self.web3.eth.contract(
                address=Web3.to_checksum_address(proxy_address),
                abi=self.contract_artifacts["TransparentUpgradeableProxy"]["abi"]
            )
            
            # 准备升级交易
            tx_params = {
                'from': self.account.address,
                'nonce': self.web3.eth.get_transaction_count(self.account.address),
                'gasPrice': int(self.web3.eth.gas_price * gas_price_multiplier),
                'chainId': self.config.blockchain.node.chain_id,
            }
            
            # 设置燃料限制
            if gas_limit:
                tx_params['gas'] = gas_limit
            else:
                tx_params['gas'] = self.config.blockchain.wallet.gas_limit
            
            # 构建升级交易
            tx_data = getattr(proxy_contract.functions, upgrade_method)(new_impl_address).build_transaction(tx_params)
            
            # 签名并发送交易
            signed_tx = self.account.sign_transaction(tx_data)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # 等待交易确认
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
            
            # 构建升级信息
            upgrade_info = {
                "proxy_address": proxy_address,
                "new_implementation": new_impl_address,
                "transaction_hash": tx_receipt.transactionHash.hex(),
                "block_number": tx_receipt.blockNumber,
                "gas_used": tx_receipt.gasUsed,
                "status": "success" if tx_receipt.status == 1 else "failed",
                "upgrade_method": upgrade_method
            }
            
            self.logger.info(f"合约升级成功: 代理={proxy_address}, 新实现={new_impl_address}")
            return tx_receipt.transactionHash.hex(), upgrade_info
            
        except Exception as e:
            self.logger.error(f"升级合约失败: {str(e)}")
            raise
    
    async def verify_contract_bytecode(self, contract_name: str, deployed_address: str) -> Tuple[bool, str]:
        """
        验证已部署合约的字节码是否与本地匹配
        
        Args:
            contract_name: 合约名称
            deployed_address: 已部署合约地址
            
        Returns:
            (是否匹配, 消息)
        """
        try:
            if contract_name not in self.contract_artifacts:
                return False, f"合约不存在: {contract_name}"
            
            # 获取本地字节码
            local_bytecode = self.contract_artifacts[contract_name]["bytecode"]
            
            # 获取链上字节码
            chain_bytecode = self.web3.eth.get_code(Web3.to_checksum_address(deployed_address)).hex()
            
            # 字节码比较 (忽略元数据部分)
            # 注意: 部署后的字节码可能包含元数据哈希和构造函数输入
            if local_bytecode in chain_bytecode:
                return True, "合约字节码验证成功"
            else:
                return False, "合约字节码不匹配，可能不是预期的合约或版本"
            
        except Exception as e:
            self.logger.error(f"验证合约字节码失败: {str(e)}")
            return False, f"验证失败: {str(e)}"
    
    async def deploy_contract_suite(self) -> Dict[str, str]:
        """
        部署完整合约套件
        
        Returns:
            合约名称到地址的映射
        """
        try:
            contracts = {}
            
            # 部署访问控制合约
            access_control_address, _ = await self.deploy_contract("AccessControl")
            contracts["AccessControl"] = access_control_address
            
            # 部署ZKP验证合约
            zkp_verifier_address, _ = await self.deploy_contract("ZKPVerifier")
            contracts["ZKPVerifier"] = zkp_verifier_address
            
            # 部署健康数据存储合约
            health_data_address, _ = await self.deploy_contract(
                "HealthDataStorage", 
                constructor_args=[access_control_address]
            )
            contracts["HealthDataStorage"] = health_data_address
            
            # 部署合约工厂
            factory_address, _ = await self.deploy_contract(
                "SuoKeLifeContractFactory",
                constructor_args=[
                    health_data_address,
                    zkp_verifier_address,
                    access_control_address
                ]
            )
            contracts["SuoKeLifeContractFactory"] = factory_address
            
            self.logger.info(f"合约套件部署完成: {contracts}")
            return contracts
            
        except Exception as e:
            self.logger.error(f"部署合约套件失败: {str(e)}")
            raise 