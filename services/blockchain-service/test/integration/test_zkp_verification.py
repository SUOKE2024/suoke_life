#!/usr/bin/env python3

"""
零知识证明验证集成测试
"""

import asyncio
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from internal.blockchain.zkp_utils import ZKPUtils
from internal.model.config import load_config
from internal.model.entities import DataType
from internal.service.blockchain_service import BlockchainService


class TestZKPVerificationIntegration(unittest.TestCase):
    """零知识证明验证集成测试类"""

    @classmethod
    def setUpClass(cls):
        """测试类设置，只运行一次"""
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.config_path = os.path.join(cls.temp_dir.name, "config.yaml")

        # 创建配置文件
        cls._create_test_config(cls.config_path)

        # 模拟验证器配置目录
        cls.verifier_configs_dir = os.path.join(cls.temp_dir.name, "verifiers")
        os.makedirs(cls.verifier_configs_dir, exist_ok=True)

        # 创建验证器配置
        cls._create_verifier_configs(cls.verifier_configs_dir)

        # 模拟合约ABI目录
        cls.contracts_dir = os.path.join(cls.temp_dir.name, "contracts")
        os.makedirs(cls.contracts_dir, exist_ok=True)

        # 创建合约ABI文件
        cls._create_contract_abis(cls.contracts_dir)

        # 加载配置
        cls.config = load_config(cls.config_path)

        # 应用配置覆盖
        cls.config.zkp.verifier_configs_dir = cls.verifier_configs_dir
        cls.config.blockchain.contracts.artifacts_dir = cls.contracts_dir

    @classmethod
    def tearDownClass(cls):
        """测试类清理，只运行一次"""
        cls.temp_dir.cleanup()

    @classmethod
    def _create_test_config(cls, config_path):
        """创建测试配置文件"""
        config = {
            "server": {
                "port": 50055,
                "max_workers": 10,
                "max_message_length": 100 * 1024 * 1024  # 100MB
            },
            "blockchain": {
                "network_type": "ethereum",
                "node": {
                    "endpoint": "http://localhost:8545",
                    "chain_id": 1337,
                    "is_poa": True
                },
                "wallet": {
                    "use_keystore_file": False,
                    "private_key": "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
                    "gas_limit": 5000000
                },
                "contracts": {
                    "health_data": "0x1234567890123456789012345678901234567890",
                    "zkp_verifier": "0x2345678901234567890123456789012345678901",
                    "access_control": "0x3456789012345678901234567890123456789012",
                    "factory": "0x4567890123456789012345678901234567890123",
                    "artifacts_dir": cls.temp_dir.name + "/contracts"
                },
                "events": {
                    "poll_interval": 5
                }
            },
            "zkp": {
                "verifier_configs_dir": cls.temp_dir.name + "/verifiers"
            },
            "logging": {
                "level": "DEBUG",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": cls.temp_dir.name + "/blockchain-service.log"
            }
        }

        # 写入配置文件
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

    @classmethod
    def _create_verifier_configs(cls, verifier_dir):
        """创建验证器配置文件"""
        verifiers = {
            "vital_signs_verifier": {
                "version": "1.0",
                "private_inputs_schema": {
                    "blood_pressure_systolic": {"type": "integer", "required": True},
                    "blood_pressure_diastolic": {"type": "integer", "required": True},
                    "heart_rate": {"type": "integer", "required": True},
                    "temperature": {"type": "number", "required": True},
                    "timestamp": {"type": "integer", "required": True}
                },
                "public_inputs_schema": {
                    "blood_pressure_normal": {"type": "boolean", "required": True},
                    "heart_rate_range": {"type": "string", "required": True},
                    "fever": {"type": "boolean", "required": True}
                }
            },
            "inquiry_verifier": {
                "version": "1.0",
                "private_inputs_schema": {
                    "symptoms": {"type": "array", "required": True},
                    "duration_days": {"type": "integer", "required": True},
                    "medical_history": {"type": "object", "required": False}
                },
                "public_inputs_schema": {
                    "has_fever": {"type": "boolean", "required": True},
                    "symptom_count": {"type": "integer", "required": True},
                    "severity": {"type": "string", "required": True}
                }
            }
        }

        # 写入验证器配置文件
        for name, config in verifiers.items():
            with open(os.path.join(verifier_dir, f"{name}.json"), "w") as f:
                json.dump(config, f, indent=2)

    @classmethod
    def _create_contract_abis(cls, contracts_dir):
        """创建合约ABI文件"""
        # 健康数据合约ABI
        health_data_abi = {
            "abi": [
                {
                    "inputs": [
                        {"name": "userId", "type": "string"},
                        {"name": "dataType", "type": "string"},
                        {"name": "dataHash", "type": "bytes32"},
                        {"name": "metadata", "type": "string"}
                    ],
                    "name": "storeHealthData",
                    "outputs": [{"name": "success", "type": "bool"}],
                    "stateMutability": "nonpayable",
                    "type": "function"
                }
            ]
        }

        # ZKP验证器合约ABI
        zkp_verifier_abi = {
            "abi": [
                {
                    "inputs": [
                        {"name": "userId", "type": "string"},
                        {"name": "verifierId", "type": "string"},
                        {"name": "verifierType", "type": "uint256"},
                        {"name": "proof", "type": "uint256[]"},
                        {"name": "publicInputs", "type": "uint256[]"},
                        {"name": "extraData", "type": "string"}
                    ],
                    "name": "verifyProof",
                    "outputs": [{"name": "success", "type": "bool"}],
                    "stateMutability": "nonpayable",
                    "type": "function"
                }
            ]
        }

        # 访问控制合约ABI
        access_control_abi = {
            "abi": [
                {
                    "inputs": [
                        {"name": "userId", "type": "string"},
                        {"name": "authorizedId", "type": "string"},
                        {"name": "dataTypes", "type": "string[]"},
                        {"name": "accessLevel", "type": "uint8"},
                        {"name": "expirationTime", "type": "uint256"},
                        {"name": "policyData", "type": "string"}
                    ],
                    "name": "grantAccess",
                    "outputs": [{"name": "authorizationId", "type": "bytes32"}],
                    "stateMutability": "nonpayable",
                    "type": "function"
                }
            ]
        }

        # 合约工厂ABI
        factory_abi = {
            "abi": [
                {
                    "inputs": [
                        {"name": "healthDataAddress", "type": "address"},
                        {"name": "zkpVerifierAddress", "type": "address"},
                        {"name": "accessControlAddress", "type": "address"}
                    ],
                    "name": "setContractAddresses",
                    "outputs": [],
                    "stateMutability": "nonpayable",
                    "type": "function"
                }
            ]
        }

        # 写入合约ABI文件
        with open(os.path.join(contracts_dir, "HealthDataStorage.json"), "w") as f:
            json.dump(health_data_abi, f, indent=2)

        with open(os.path.join(contracts_dir, "ZKPVerifier.json"), "w") as f:
            json.dump(zkp_verifier_abi, f, indent=2)

        with open(os.path.join(contracts_dir, "AccessControl.json"), "w") as f:
            json.dump(access_control_abi, f, indent=2)

        with open(os.path.join(contracts_dir, "SuoKeLifeContractFactory.json"), "w") as f:
            json.dump(factory_abi, f, indent=2)

    def setUp(self):
        """测试前的准备工作"""
        # 创建测试用的ZKP工具
        self.zkp_utils = ZKPUtils(self.config)

        # 模拟Web3和区块链客户端
        self.web3_mock = MagicMock()
        self.blockchain_client_mock = MagicMock()
        self.blockchain_client_mock.get_web3.return_value = self.web3_mock
        self.blockchain_client_mock.get_account.return_value = MagicMock()

        # 模拟合约工厂
        self.contract_factory_mock = MagicMock()

        # 创建BlockchainService实例
        with patch("internal.blockchain.blockchain_client.BlockchainClient", return_value=self.blockchain_client_mock), \
             patch("internal.blockchain.contract_factory.ContractFactory", return_value=self.contract_factory_mock), \
             patch("internal.blockchain.zkp_utils.ZKPUtils", return_value=self.zkp_utils):
            self.service = BlockchainService(self.config)

    def test_generate_health_proof(self):
        """测试生成健康数据证明"""
        async def run_test():
            # 设置测试数据
            user_id = "test_user"
            data_type = DataType.VITAL_SIGNS
            private_data = {
                "blood_pressure_systolic": 120,
                "blood_pressure_diastolic": 80,
                "heart_rate": 72,
                "temperature": 36.5,
                "timestamp": 1636000000
            }
            public_attributes = {
                "blood_pressure_normal": True,
                "heart_rate_range": "normal",
                "fever": False
            }

            # 调用服务方法
            success, message, proof_details = await self.service.generate_health_proof(
                user_id, data_type, private_data, public_attributes
            )

            # 验证结果
            self.assertTrue(success)
            self.assertEqual(message, "健康证明生成成功")
            self.assertIsInstance(proof_details, dict)
            self.assertIn("proof", proof_details)
            self.assertIn("public_inputs", proof_details)
            self.assertIn("metadata", proof_details)

            # 验证生成的证明可以被解码
            self.assertIsInstance(bytes.fromhex(proof_details["proof"]), bytes)
            self.assertIsInstance(bytes.fromhex(proof_details["public_inputs"]), bytes)

            return proof_details

        # 运行测试
        proof_details = asyncio.run(run_test())
        return proof_details

    def test_verify_health_proof(self):
        """测试验证健康数据证明"""
        async def run_test():
            # 首先生成证明
            proof_details = await asyncio.create_task(self.test_generate_health_proof())

            # 准备验证参数
            user_id = "test_user"
            verifier_id = "test_verifier"
            data_type = DataType.VITAL_SIGNS
            proof = bytes.fromhex(proof_details["proof"])
            public_inputs = bytes.fromhex(proof_details["public_inputs"])

            # 配置模拟
            self.blockchain_client_mock.send_transaction.return_value = ("0xtx123", MagicMock())
            self.blockchain_client_mock.get_transaction_details.return_value = {"receipt": {"status": 1}}

            # 调用验证方法
            valid, message, details = await self.service.verify_with_zkp(
                user_id, verifier_id, data_type, proof, public_inputs
            )

            # 验证结果
            self.assertTrue(valid)
            self.assertEqual(message, "零知识证明验证成功")
            self.assertIsInstance(details, dict)
            self.assertIn("transaction_id", details)
            self.assertIn("onchain_status", details)

            return details

        # 运行测试
        asyncio.run(run_test())

    def test_local_vs_onchain_verification(self):
        """测试本地验证与链上验证的一致性"""
        async def run_test():
            # 首先生成证明
            proof_details = await asyncio.create_task(self.test_generate_health_proof())

            # 准备验证参数
            user_id = "test_user"
            verifier_id = "test_verifier"
            data_type = DataType.VITAL_SIGNS
            proof = bytes.fromhex(proof_details["proof"])
            public_inputs = bytes.fromhex(proof_details["public_inputs"])

            # 本地验证
            local_valid, local_details = await self.zkp_utils.verify_proof(
                proof, public_inputs, data_type, verifier_id
            )

            # 配置模拟
            self.blockchain_client_mock.send_transaction.return_value = ("0xtx123", MagicMock())
            self.blockchain_client_mock.get_transaction_details.return_value = {"receipt": {"status": 1}}

            # 链上验证
            onchain_valid, _, onchain_details = await self.service.verify_with_zkp(
                user_id, verifier_id, data_type, proof, public_inputs
            )

            # 验证结果一致性
            self.assertEqual(local_valid, onchain_valid)
            self.assertEqual(local_details["verified_locally"], True)
            self.assertEqual(onchain_details["onchain_status"], "success")

        # 运行测试
        asyncio.run(run_test())

    def test_verify_proof_failure(self):
        """测试验证失败情况"""
        async def run_test():
            # 设置测试数据
            user_id = "test_user"
            verifier_id = "test_verifier"
            data_type = DataType.VITAL_SIGNS

            # 创建无效的证明(全0)
            invalid_proof = b"\x00" * 128
            invalid_public_inputs = b"\x00" * 64

            # 本地验证应该失败
            local_valid, local_details = await self.zkp_utils.verify_proof(
                invalid_proof, invalid_public_inputs, data_type, verifier_id
            )

            # 验证本地验证失败
            self.assertFalse(local_valid)

            # 配置模拟，链上也会失败
            mock_transaction = MagicMock()
            mock_transaction.status = "FAILED"
            self.blockchain_client_mock.send_transaction.return_value = ("0xtx123", mock_transaction)

            # 链上验证
            onchain_valid, message, onchain_details = await self.service.verify_with_zkp(
                user_id, verifier_id, data_type, invalid_proof, invalid_public_inputs
            )

            # 验证链上验证也应该失败
            self.assertFalse(onchain_valid)
            self.assertIn("失败", message)

        # 运行测试
        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
