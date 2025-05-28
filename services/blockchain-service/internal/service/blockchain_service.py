#!/usr/bin/env python3

"""
区块链服务实现模块

该模块实现了区块链服务的核心功能，包括：
- 健康数据存储到区块链
- 健康数据验证
- 零知识证明验证
- 授权管理
- 区块链状态监控
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import wraps
import json
import logging
import os
import time
from typing import Any

from eth_account import Account
from eth_account.signers.local import LocalAccount
from hexbytes import HexBytes
from web3 import Web3
from web3.middleware import construct_sign_and_send_raw_middleware

from internal.blockchain.blockchain_client import BlockchainClient
from internal.blockchain.contract_factory import ContractFactory
from internal.blockchain.zkp_utils import ZKPUtils
from internal.model.config import AppConfig
from internal.model.entities import (
    AccessLevel,
    AuthorizationRecord,
    DataType,
    HealthDataRecord,
    TransactionStatus,
    VerificationRecord,
)
from internal.repository.blockchain_repository import BlockchainRepository
from internal.service.base_service import BaseService


class BlockchainService(BaseService):
    """区块链服务实现类，提供健康数据的区块链存储、验证和访问控制功能"""

    def __init__(self, config: AppConfig):
        """
        初始化区块链服务
        
        Args:
            config: 应用配置对象
        """
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        self.config = config

        # 初始化区块链客户端
        self.blockchain_client = BlockchainClient(config)

        # 初始化合约工厂
        self.contract_factory = ContractFactory(
            config,
            self.blockchain_client.get_web3(),
            self.blockchain_client.get_account()
        )

        # 初始化ZKP工具
        self.zkp_utils = ZKPUtils(config)

        # 初始化线程池
        self.executor = ThreadPoolExecutor(max_workers=config.server.max_workers)

        # 初始化存储库
        self.repository = BlockchainRepository(config)

        # 初始化Web3, 合约和账户
        self.web3 = self.blockchain_client.get_web3()
        self.account = self.blockchain_client.get_account()

        # 初始化合约实例
        self._init_contracts()

        self.logger.info(f"区块链服务初始化完成: 连接状态={self.web3.is_connected()}, 网络ID={self.web3.net.version}, 当前区块高度={self.web3.eth.block_number}")

    def _load_account(self):
        """加载账户并设置签名中间件"""
        try:
            # 从文件加载账户密钥
            keystore_path = self.config.blockchain.wallet.keystore_path
            with open(f"{keystore_path}/private_key.json") as f:
                encrypted_key = json.load(f)

            with open(f"{keystore_path}/password.txt") as f:
                password = f.read().strip()

            self.account: LocalAccount = Account.from_key(
                Web3.to_hex(HexBytes(encrypted_key["private_key"]))
            )

            # 设置签名中间件
            self.web3.middleware_onion.add(
                construct_sign_and_send_raw_middleware(self.account)
            )

            self.logger.info(f"加载账户成功: {self.account.address}")
        except Exception as e:
            self.logger.error(f"加载账户失败: {e!s}")
            raise

    def _init_contracts(self):
        """初始化智能合约实例"""
        try:
            # 设置合约ABI目录
            contracts_dir = self.config.blockchain.contracts.artifacts_dir

            # 检查ABI目录是否存在
            if not os.path.exists(contracts_dir):
                self.logger.error(f"合约ABI目录不存在: {contracts_dir}")
                raise FileNotFoundError(f"合约ABI目录不存在: {contracts_dir}")

            # 加载合约ABI
            try:
                with open(f"{contracts_dir}/HealthDataStorage.json") as f:
                    health_data_abi = json.load(f)

                with open(f"{contracts_dir}/ZKPVerifier.json") as f:
                    zkp_verifier_abi = json.load(f)

                with open(f"{contracts_dir}/AccessControl.json") as f:
                    access_control_abi = json.load(f)

                with open(f"{contracts_dir}/SuoKeLifeContractFactory.json") as f:
                    factory_abi = json.load(f)
            except FileNotFoundError as e:
                self.logger.error(f"合约ABI文件不存在: {e!s}")
                raise
            except json.JSONDecodeError as e:
                self.logger.error(f"解析合约ABI文件失败: {e!s}")
                raise

            # 创建合约实例
            contracts_config = self.config.blockchain.contracts

            self.health_data_contract = self.web3.eth.contract(
                address=Web3.to_checksum_address(contracts_config.health_data),
                abi=health_data_abi["abi"]
            )

            self.zkp_verifier_contract = self.web3.eth.contract(
                address=Web3.to_checksum_address(contracts_config.zkp_verifier),
                abi=zkp_verifier_abi["abi"]
            )

            self.access_control_contract = self.web3.eth.contract(
                address=Web3.to_checksum_address(contracts_config.access_control),
                abi=access_control_abi["abi"]
            )

            if hasattr(contracts_config, "factory") and contracts_config.factory:
                self.factory_contract = self.web3.eth.contract(
                    address=Web3.to_checksum_address(contracts_config.factory),
                    abi=factory_abi["abi"]
                )

            self.logger.info("智能合约初始化完成")
        except Exception as e:
            self.logger.error(f"智能合约初始化失败: {e!s}")
            raise

    @wraps(asyncio.coroutine)
    def _with_retry(max_tries=5, backoff_factor=1.5):
        """
        重试装饰器，用于自动重试失败的操作
        
        Args:
            max_tries: 最大重试次数
            backoff_factor: 退避因子
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                retries = 0
                while retries < max_tries:
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        retries += 1
                        if retries >= max_tries:
                            raise

                        # 计算等待时间
                        wait_time = backoff_factor ** retries
                        cls = args[0].__class__.__name__ if args else ""
                        func_name = func.__name__
                        cls_logger = args[0].logger if args and hasattr(args[0], "logger") else logging.getLogger(__name__)

                        cls_logger.warning(f"{cls}.{func_name} 操作失败，第 {retries} 次重试，等待 {wait_time:.2f} 秒: {e!s}")
                        await asyncio.sleep(wait_time)
            return wrapper
        return decorator

    @_with_retry(max_tries=3, backoff_factor=2.0)
    async def store_health_data(
        self,
        user_id: str,
        data_type: DataType,
        data_hash: bytes,
        metadata: dict[str, str] = None,
        encrypted_data: bytes = None
    ) -> tuple[bool, str, HealthDataRecord | None]:
        """
        将健康数据存储到区块链
        
        Args:
            user_id: 用户ID
            data_type: 数据类型
            data_hash: 数据哈希
            metadata: 元数据
            encrypted_data: 加密后的数据（可选）
            
        Returns:
            (成功标志, 消息, 数据记录)
        """
        try:
            if not user_id or not data_type or not data_hash:
                return False, "参数无效: 用户ID、数据类型和数据哈希不能为空", None

            # 确保元数据是字典
            if metadata is None:
                metadata = {}

            # 转换为十六进制字符串
            data_hash_hex = data_hash.hex()

            # 获取当前时间戳
            timestamp = int(time.time())

            # 准备交易数据
            nonce = self.web3.eth.get_transaction_count(self.account.address)

            # 调用合约函数
            tx_data = self.health_data_contract.functions.storeHealthData(
                user_id,
                data_type.value,
                Web3.to_bytes(hexstr=data_hash_hex),
                json.dumps(metadata)
            ).build_transaction({
                "chainId": self.config.blockchain.node.chain_id,
                "gas": self.config.blockchain.wallet.gas_limit,
                "gasPrice": self.web3.eth.gas_price,
                "nonce": nonce,
            })

            # 使用区块链客户端发送交易
            tx_hash, transaction = await self.blockchain_client.send_transaction(
                to_address=self.health_data_contract.address,
                data=HexBytes(tx_data.get("data", "")),
                gas_limit=tx_data.get("gas"),
                nonce=nonce
            )

            # 如果交易失败，则返回错误
            if transaction.status == TransactionStatus.FAILED:
                self.logger.error(f"健康数据存储失败: {tx_hash}")
                return False, "健康数据存储失败: 交易执行失败", None

            # 创建健康数据记录
            record = HealthDataRecord(
                user_id=user_id,
                data_type=data_type,
                data_hash=data_hash_hex,
                metadata=metadata,
                transaction=transaction,
                encrypted_data=encrypted_data.hex() if encrypted_data else None
            )

            # 保存到数据库
            await self.repository.save_health_data_record(record)

            self.logger.info(f"健康数据存储成功: user_id={user_id}, data_type={data_type.value}, tx_id={tx_hash}")
            return True, "健康数据存储成功", record

        except Exception as e:
            self.logger.error(f"健康数据存储失败: {e!s}")
            return False, f"健康数据存储失败: {e!s}", None

    async def verify_health_data(
        self,
        transaction_id: str,
        data_hash: bytes
    ) -> tuple[bool, str, datetime | None]:
        """
        验证健康数据的完整性
        
        Args:
            transaction_id: 交易ID
            data_hash: 数据哈希
            
        Returns:
            (验证是否通过, 消息, 验证时间)
        """
        try:
            if not transaction_id or not data_hash:
                return False, "参数无效: 交易ID和数据哈希不能为空", None

            # 转换为十六进制字符串
            data_hash_hex = data_hash.hex()

            # 调用合约函数验证数据
            result = self.health_data_contract.functions.verifyHealthData(
                Web3.to_bytes(hexstr=transaction_id) if not transaction_id.startswith("0x") else Web3.to_bytes(hexstr=transaction_id),
                Web3.to_bytes(hexstr=data_hash_hex)
            ).call()

            valid = result[0]
            timestamp = result[1]

            verification_time = datetime.fromtimestamp(timestamp) if timestamp > 0 else datetime.now()

            # 记录验证结果
            if valid:
                self.logger.info(f"健康数据验证成功: transaction_id={transaction_id}")
                message = "健康数据验证成功，数据完整性已确认"
            else:
                self.logger.warning(f"健康数据验证失败: transaction_id={transaction_id}")
                message = "健康数据验证失败，数据可能已被篡改"

            return valid, message, verification_time

        except Exception as e:
            self.logger.error(f"健康数据验证异常: {e!s}")
            return False, f"健康数据验证异常: {e!s}", datetime.now()

    @_with_retry(max_tries=3, backoff_factor=2.0)
    async def verify_with_zkp(
        self,
        user_id: str,
        verifier_id: str,
        data_type: DataType,
        proof: bytes,
        public_inputs: bytes
    ) -> tuple[bool, str, dict[str, Any]]:
        """
        使用零知识证明验证健康数据的特定属性
        
        Args:
            user_id: 用户ID
            verifier_id: 验证者ID
            data_type: 数据类型
            proof: 零知识证明数据
            public_inputs: 公共输入数据
            
        Returns:
            (验证是否通过, 消息, 验证详情)
        """
        try:
            if not user_id or not verifier_id or not proof or not public_inputs:
                return False, "参数无效: 用户ID、验证者ID、证明和公共输入不能为空", {}

            # 先进行本地验证 (链下验证)
            local_valid, verification_details = await self.zkp_utils.verify_proof(
                proof, public_inputs, data_type, verifier_id
            )

            if not local_valid:
                self.logger.warning(f"零知识证明本地验证失败: user_id={user_id}")
                return False, "零知识证明本地验证失败", verification_details

            # 准备合约验证所需的格式
            proof_ints, public_inputs_ints = self.zkp_utils.prepare_proof_for_contract(proof, public_inputs)

            # 确定验证器类型
            verifier_type = self._determine_verifier_type(data_type)

            # 调用合约函数验证ZKP
            tx_data = self.zkp_verifier_contract.functions.verifyProof(
                user_id,
                verifier_id,
                verifier_type,
                proof_ints,
                public_inputs_ints,
                json.dumps({"data_type": data_type.value})
            ).build_transaction({
                "chainId": self.config.blockchain.node.chain_id,
                "gas": self.config.blockchain.wallet.gas_limit,
                "gasPrice": self.web3.eth.gas_price,
                "nonce": self.web3.eth.get_transaction_count(self.account.address),
            })

            # 使用区块链客户端发送交易
            tx_hash, transaction = await self.blockchain_client.send_transaction(
                to_address=self.zkp_verifier_contract.address,
                data=HexBytes(tx_data.get("data", "")),
                gas_limit=tx_data.get("gas")
            )

            # 如果交易失败，则直接返回错误
            if transaction.status == TransactionStatus.FAILED:
                self.logger.error(f"零知识证明验证失败: 交易执行失败, tx_hash={tx_hash}")
                verification_details["onchain_status"] = "failed"
                verification_details["transaction_id"] = tx_hash
                return False, "零知识证明链上验证失败", verification_details

            # 获取交易详情以检查事件
            tx_details = await self.blockchain_client.get_transaction_details(tx_hash)

            # 解析事件日志获取验证结果 (简化实现)
            valid = True  # 在实际应用中应从事件日志中提取
            verification_id = tx_hash

            # 创建验证记录
            verification_time = datetime.now()
            verification_record = VerificationRecord(
                verification_id=verification_id,
                user_id=user_id,
                verifier_id=verifier_id,
                data_type=data_type,
                verified=valid,
                timestamp=int(verification_time.timestamp()),
                transaction_id=tx_hash
            )

            # 保存到数据库
            await self.repository.save_verification_record(verification_record)

            # 更新验证详情
            verification_details.update({
                "verification_id": verification_id,
                "transaction_id": tx_hash,
                "onchain_status": "success",
                "block_number": transaction.block_number,
                "gas_used": transaction.gas_used
            })

            self.logger.info(f"零知识证明验证成功: user_id={user_id}, verification_id={verification_id}")
            return True, "零知识证明验证成功", verification_details

        except Exception as e:
            self.logger.error(f"零知识证明验证异常: {e!s}")
            return False, f"零知识证明验证异常: {e!s}", {"error": str(e)}

    def _determine_verifier_type(self, data_type: DataType) -> int:
        """根据数据类型确定验证器类型"""
        verifier_types = {
            DataType.INQUIRY: 1,     # 问诊数据
            DataType.LISTEN: 2,      # 闻诊数据
            DataType.LOOK: 3,        # 望诊数据
            DataType.PALPATION: 4,   # 切诊数据
            DataType.VITAL_SIGNS: 5, # 生命体征
            DataType.LABORATORY: 6,  # 实验室检查
            DataType.MEDICATION: 7,  # 用药记录
            DataType.NUTRITION: 8,   # 营养记录
            DataType.ACTIVITY: 9,    # 活动记录
            DataType.SLEEP: 10,      # 睡眠记录
            DataType.SYNDROME: 11,   # 证型记录
            DataType.PRESCRIPTION: 12, # 处方记录
            DataType.HEALTH_PLAN: 13   # 健康计划
        }
        return verifier_types.get(data_type, 0)

    async def authorize_access(
        self,
        user_id: str,
        authorized_id: str,
        data_types: list[DataType],
        expiration_time: datetime,
        access_policies: dict[str, str] = None
    ) -> tuple[bool, str, str | None]:
        """
        授权其他用户或服务访问健康数据
        
        Args:
            user_id: 数据所有者ID
            authorized_id: 被授权方ID
            data_types: 授权的数据类型列表
            expiration_time: 授权过期时间
            access_policies: 访问策略
            
        Returns:
            (成功标志, 消息, 授权ID)
        """
        try:
            if not user_id or not authorized_id or not data_types:
                return False, "参数无效: 用户ID、被授权方ID和数据类型不能为空", None

            # 确保访问策略是字典
            if access_policies is None:
                access_policies = {}

            # 确定访问级别
            access_level = self._determine_access_level(access_policies)

            # 转换数据类型为字符串列表
            data_type_values = [dt.value for dt in data_types]

            # 转换过期时间为时间戳
            expiration_timestamp = int(expiration_time.timestamp()) if expiration_time else 0

            # 调用合约函数授权访问
            tx_data = self.access_control_contract.functions.grantAccess(
                user_id,
                authorized_id,
                data_type_values,
                access_level.value,
                expiration_timestamp,
                json.dumps(access_policies)
            ).build_transaction({
                "chainId": self.config.blockchain.node.chain_id,
                "gas": self.config.blockchain.wallet.gas_limit,
                "gasPrice": self.web3.eth.gas_price,
                "nonce": self.web3.eth.get_transaction_count(self.account.address),
            })

            # 签名并发送交易
            signed_tx = self.web3.eth.account.sign_transaction(tx_data, self.account.key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)

            # 等待交易确认
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

            # 处理事件日志获取授权ID
            event_logs = self.access_control_contract.events.AccessGranted().process_receipt(receipt)
            if event_logs and len(event_logs) > 0:
                authorization_id = event_logs[0]["args"]["authorizationId"].hex()
            else:
                authorization_id = tx_hash.hex()

            # 创建授权记录
            auth_record = AuthorizationRecord(
                authorization_id=authorization_id,
                user_id=user_id,
                authorized_id=authorized_id,
                data_types=data_type_values,
                access_level=access_level,
                issued_at=int(time.time()),
                expiration_time=expiration_timestamp,
                is_active=True,
                policy_data=access_policies
            )

            # 保存到数据库
            await self.repository.save_authorization_record(auth_record)

            self.logger.info(f"授权访问成功: user_id={user_id}, authorized_id={authorized_id}, authorization_id={authorization_id}")
            return True, "授权访问成功", authorization_id

        except Exception as e:
            self.logger.error(f"授权访问失败: {e!s}")
            return False, f"授权访问失败: {e!s}", None

    def _determine_access_level(self, access_policies: dict[str, str]) -> AccessLevel:
        """根据访问策略确定访问级别"""
        if access_policies.get("full_access", "").lower() == "true":
            return AccessLevel.FULL
        elif access_policies.get("write_access", "").lower() == "true":
            return AccessLevel.WRITE
        else:
            return AccessLevel.READ

    async def revoke_access(
        self,
        authorization_id: str,
        user_id: str,
        revocation_reason: str = None
    ) -> tuple[bool, str]:
        """
        撤销先前授予的健康数据访问权限
        
        Args:
            authorization_id: 授权ID
            user_id: 数据所有者ID
            revocation_reason: 撤销原因
            
        Returns:
            (成功标志, 消息)
        """
        try:
            if not authorization_id or not user_id:
                return False, "参数无效: 授权ID和用户ID不能为空"

            # 如果没有提供撤销原因，使用默认值
            if not revocation_reason:
                revocation_reason = "用户主动撤销"

            # 调用合约函数撤销访问
            tx_data = self.access_control_contract.functions.revokeAccess(
                Web3.to_bytes(hexstr=authorization_id) if not authorization_id.startswith("0x") else Web3.to_bytes(hexstr=authorization_id),
                user_id,
                revocation_reason
            ).build_transaction({
                "chainId": self.config.blockchain.node.chain_id,
                "gas": self.config.blockchain.wallet.gas_limit,
                "gasPrice": self.web3.eth.gas_price,
                "nonce": self.web3.eth.get_transaction_count(self.account.address),
            })

            # 签名并发送交易
            signed_tx = self.web3.eth.account.sign_transaction(tx_data, self.account.key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)

            # 等待交易确认
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

            # 更新数据库中的授权记录
            await self.repository.update_authorization_status(authorization_id, False)

            if receipt.status == 1:
                self.logger.info(f"撤销访问成功: authorization_id={authorization_id}, user_id={user_id}")
                return True, "撤销访问成功"
            else:
                self.logger.warning(f"撤销访问失败: authorization_id={authorization_id}, user_id={user_id}")
                return False, "撤销访问失败，交易执行出错"

        except Exception as e:
            self.logger.error(f"撤销访问异常: {e!s}")
            return False, f"撤销访问异常: {e!s}"

    async def get_health_data_records(
        self,
        user_id: str,
        data_type: DataType = None,
        start_time: datetime = None,
        end_time: datetime = None,
        page: int = 1,
        page_size: int = 10
    ) -> tuple[list[HealthDataRecord], int]:
        """
        获取用户的健康数据记录
        
        Args:
            user_id: 用户ID
            data_type: 数据类型（可选）
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）
            page: 分页页码
            page_size: 每页大小
            
        Returns:
            (健康数据记录列表, 总记录数)
        """
        try:
            if not user_id:
                return [], 0

            # 转换时间为时间戳
            start_timestamp = int(start_time.timestamp()) if start_time else None
            end_timestamp = int(end_time.timestamp()) if end_time else None

            # 从数据库获取记录
            records, total_count = await self.repository.get_health_data_records(
                user_id=user_id,
                data_type=data_type.value if data_type else None,
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
                page=page,
                page_size=page_size
            )

            self.logger.info(f"获取健康数据记录成功: user_id={user_id}, count={len(records)}, total={total_count}")
            return records, total_count

        except Exception as e:
            self.logger.error(f"获取健康数据记录失败: {e!s}")
            return [], 0

    async def get_blockchain_status(
        self,
        include_node_info: bool = False
    ) -> tuple[dict[str, Any], bool]:
        """
        获取区块链网络和节点的状态信息
        
        Args:
            include_node_info: 是否包含节点详细信息
            
        Returns:
            (状态信息字典, 成功标志)
        """
        try:
            status = {}

            # 获取基本状态信息
            status["current_block_height"] = self.web3.eth.block_number
            status["connected_nodes"] = self.web3.net.peer_count

            # 获取最新区块
            latest_block = self.web3.eth.get_block("latest")
            status["last_block_timestamp"] = latest_block.timestamp

            # 检查同步状态
            sync_status = self.web3.eth.syncing
            if sync_status:
                status["consensus_status"] = "syncing"
                current_block = sync_status.currentBlock
                highest_block = sync_status.highestBlock
                status["sync_percentage"] = (current_block / highest_block) * 100 if highest_block > 0 else 0
            else:
                status["consensus_status"] = "in_sync"
                status["sync_percentage"] = 100.0

            # 获取节点详细信息
            if include_node_info:
                node_info = {}
                node_info["node_version"] = self.web3.clientVersion
                node_info["network_id"] = self.web3.net.version
                node_info["gas_price"] = self.web3.eth.gas_price
                node_info["chain_id"] = self.web3.eth.chain_id

                # 获取合约地址
                node_info["health_data_contract"] = self.health_data_contract.address
                node_info["zkp_verifier_contract"] = self.zkp_verifier_contract.address
                node_info["access_control_contract"] = self.access_control_contract.address

                status["node_info"] = node_info

            self.logger.info(f"获取区块链状态成功: block_height={status['current_block_height']}")
            return status, True

        except Exception as e:
            self.logger.error(f"获取区块链状态失败: {e!s}")
            # 返回最基本的错误信息
            return {"error": str(e)}, False

    async def generate_health_proof(
        self,
        user_id: str,
        data_type: DataType,
        private_data: dict[str, Any],
        public_attributes: dict[str, Any]
    ) -> tuple[bool, str, dict[str, Any]]:
        """
        生成健康数据证明
        
        Args:
            user_id: 用户ID
            data_type: 数据类型
            private_data: 私有健康数据
            public_attributes: 需要证明的公共属性
            
        Returns:
            (成功标志, 消息, 证明详情)
        """
        try:
            # 生成零知识证明
            proof, public_inputs, metadata = await self.zkp_utils.generate_proof(
                data_type, user_id, private_data, public_attributes
            )

            # 存储证明元数据
            proof_record = {
                "user_id": user_id,
                "data_type": data_type.value,
                "metadata": metadata,
                "timestamp": int(time.time()),
                "public_attributes": public_attributes
            }

            # 返回证明详情
            proof_details = {
                "proof": proof.hex(),
                "public_inputs": public_inputs.hex(),
                "metadata": metadata,
                "data_type": data_type.value
            }

            self.logger.info(f"健康证明生成成功: user_id={user_id}, data_type={data_type.value}")
            return True, "健康证明生成成功", proof_details

        except Exception as e:
            self.logger.error(f"健康证明生成失败: {e!s}")
            return False, f"健康证明生成失败: {e!s}", {}

    async def get_transaction_status(self, tx_hash: str) -> dict[str, Any]:
        """
        获取交易状态
        
        Args:
            tx_hash: 交易哈希
            
        Returns:
            交易状态详情
        """
        try:
            # 使用区块链客户端获取交易详情
            tx_details = await self.blockchain_client.get_transaction_details(tx_hash)

            # 格式化返回结果
            status = {
                "hash": tx_hash,
                "status": "confirmed" if tx_details.get("receipt", {}).get("status") == 1 else
                          "pending" if tx_details.get("receipt", {}).get("status") == "pending" else
                          "failed",
                "block_number": tx_details.get("receipt", {}).get("blockNumber"),
                "timestamp": int(time.time()),
                "gas_used": tx_details.get("receipt", {}).get("gasUsed")
            }

            return status
        except Exception as e:
            self.logger.error(f"获取交易状态失败: {e!s}")
            return {
                "hash": tx_hash,
                "status": "unknown",
                "error": str(e),
                "timestamp": int(time.time())
            }

    async def deploy_contract_suite(self) -> tuple[bool, str, dict[str, str]]:
        """
        部署完整的合约套件
        
        Returns:
            (成功标志, 消息, 合约地址映射)
        """
        try:
            # 部署合约套件
            contracts = await self.contract_factory.deploy_contract_suite()

            # 保存合约地址到配置
            contracts_config = self.config.blockchain.contracts
            contracts_config.health_data = contracts["HealthDataStorage"]
            contracts_config.zkp_verifier = contracts["ZKPVerifier"]
            contracts_config.access_control = contracts["AccessControl"]
            contracts_config.factory = contracts["SuoKeLifeContractFactory"]

            # 重新初始化合约实例
            self._init_contracts()

            self.logger.info(f"合约套件部署成功: {contracts}")
            return True, "合约套件部署成功", contracts

        except Exception as e:
            self.logger.error(f"合约套件部署失败: {e!s}")
            return False, f"合约套件部署失败: {e!s}", {}

    async def verify_contract_addresses(self) -> tuple[bool, str, dict[str, bool]]:
        """
        验证所有合约地址是否有效
        
        Returns:
            (所有合约是否有效, 消息, 各合约验证结果)
        """
        try:
            verification_results = {}

            # 验证健康数据合约
            health_data_valid, _ = await self.contract_factory.verify_contract_bytecode(
                "HealthDataStorage",
                self.health_data_contract.address
            )
            verification_results["HealthDataStorage"] = health_data_valid

            # 验证ZKP验证器合约
            zkp_verifier_valid, _ = await self.contract_factory.verify_contract_bytecode(
                "ZKPVerifier",
                self.zkp_verifier_contract.address
            )
            verification_results["ZKPVerifier"] = zkp_verifier_valid

            # 验证访问控制合约
            access_control_valid, _ = await self.contract_factory.verify_contract_bytecode(
                "AccessControl",
                self.access_control_contract.address
            )
            verification_results["AccessControl"] = access_control_valid

            # 验证工厂合约 (如果存在)
            factory_valid = True
            if hasattr(self, "factory_contract"):
                factory_valid, _ = await self.contract_factory.verify_contract_bytecode(
                    "SuoKeLifeContractFactory",
                    self.factory_contract.address
                )
            verification_results["SuoKeLifeContractFactory"] = factory_valid

            # 判断所有合约是否都有效
            all_valid = all(verification_results.values())

            message = "所有合约地址有效" if all_valid else "部分合约地址无效"
            self.logger.info(f"合约地址验证结果: {message}, {verification_results}")

            return all_valid, message, verification_results

        except Exception as e:
            self.logger.error(f"验证合约地址失败: {e!s}")
            return False, f"验证合约地址失败: {e!s}", {}
