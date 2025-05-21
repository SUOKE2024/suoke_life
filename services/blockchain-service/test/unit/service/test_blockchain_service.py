#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BlockchainService 单元测试
"""

import asyncio
import os
import sys
import time
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from internal.model.config import AppConfig, BlockchainConfig, BlockchainNodeConfig, ContractsConfig, WalletConfig
from internal.model.entities import DataType, TransactionStatus
from internal.service.blockchain_service import BlockchainService


class TestBlockchainService(unittest.TestCase):
    """BlockchainService 单元测试类"""

    def setUp(self):
        """测试前的准备工作"""
        # 创建模拟配置
        node_config = BlockchainNodeConfig(
            endpoint="http://localhost:8545",
            chain_id=1337
        )
        
        contracts_config = ContractsConfig(
            health_data="0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f",
            zkp_verifier="0x9FBDa871d559710256a2502A2517b794B482Db40",
            access_control="0x2C4E8f2D746113d0696cE89B35F0d8bF88E0AEcA"
        )
        
        wallet_config = WalletConfig(
            keystore_path="config/keystore",
            gas_limit=3000000,
            gas_price_strategy="medium"
        )
        
        blockchain_config = BlockchainConfig(
            network_type="ethereum",
            node=node_config,
            contracts=contracts_config,
            wallet=wallet_config
        )
        
        self.config = MagicMock(spec=AppConfig)
        self.config.blockchain = blockchain_config
        
        # 创建 Web3 模拟对象
        self.web3_mock = MagicMock()
        self.web3_mock.is_connected.return_value = True
        self.web3_mock.eth.block_number = 12345
        
        # 使用 mock Web3 创建 BlockchainService 实例
        with patch('internal.service.blockchain_service.Web3', autospec=True) as web3_cls_mock:
            web3_cls_mock.HTTPProvider.return_value = MagicMock()
            web3_cls_mock.return_value = self.web3_mock
            self.service = BlockchainService(self.config)
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.service)
        self.assertEqual(self.service.config, self.config)
    
    async def async_store_health_data(self):
        """存储健康数据的异步测试方法"""
        user_id = "test_user"
        data_type = DataType.VITAL_SIGNS
        data_hash = b"0123456789abcdef0123456789abcdef"
        metadata = {"source": "test", "device": "unit_test"}
        
        success, message, record = await self.service.store_health_data(
            user_id=user_id,
            data_type=data_type,
            data_hash=data_hash,
            metadata=metadata
        )
        
        self.assertTrue(success)
        self.assertIn("成功", message)
        self.assertIsNotNone(record)
        self.assertEqual(record.user_id, user_id)
        self.assertEqual(record.data_type, data_type)
        self.assertEqual(record.data_hash, data_hash.hex())
        self.assertEqual(record.metadata, metadata)
        self.assertIsNotNone(record.transaction)
        self.assertEqual(record.transaction.status, TransactionStatus.CONFIRMED)
        
        return record
    
    def test_store_health_data(self):
        """测试存储健康数据"""
        loop = asyncio.get_event_loop()
        record = loop.run_until_complete(self.async_store_health_data())
        self.assertIsNotNone(record)
    
    async def async_verify_health_data(self):
        """验证健康数据的异步测试方法"""
        # 先存储数据
        record = await self.async_store_health_data()
        
        # 然后验证
        transaction_id = record.transaction.transaction_id
        data_hash = bytes.fromhex(record.data_hash)
        
        valid, message, verification_time = await self.service.verify_health_data(
            transaction_id=transaction_id,
            data_hash=data_hash
        )
        
        self.assertTrue(valid)
        self.assertIn("成功", message)
        self.assertIsInstance(verification_time, datetime)
        
        return valid
    
    def test_verify_health_data(self):
        """测试验证健康数据"""
        loop = asyncio.get_event_loop()
        valid = loop.run_until_complete(self.async_verify_health_data())
        self.assertTrue(valid)
    
    async def async_verify_with_zkp(self):
        """测试零知识证明验证的异步方法"""
        user_id = "test_user"
        verifier_id = "test_verifier"
        data_type = DataType.VITAL_SIGNS
        proof = b"test_proof_data"
        public_inputs = b"test_public_inputs"
        
        valid, message, details = await self.service.verify_with_zkp(
            user_id=user_id,
            verifier_id=verifier_id,
            data_type=data_type,
            proof=proof,
            public_inputs=public_inputs
        )
        
        self.assertTrue(valid)
        self.assertIn("成功", message)
        self.assertIsNotNone(details)
        self.assertIn("verification_time", details)
        self.assertIn("proof_size", details)
        
        return valid
    
    def test_verify_with_zkp(self):
        """测试零知识证明验证"""
        loop = asyncio.get_event_loop()
        valid = loop.run_until_complete(self.async_verify_with_zkp())
        self.assertTrue(valid)
    
    async def async_authorize_access(self):
        """测试授权访问的异步方法"""
        user_id = "test_user"
        authorized_id = "test_doctor"
        data_types = [DataType.VITAL_SIGNS, DataType.MEDICATION]
        expiration_time = datetime.now() + timedelta(days=7)
        access_policies = {"read_only": "true", "purpose": "medical"}
        
        success, message, authorization_id = await self.service.authorize_access(
            user_id=user_id,
            authorized_id=authorized_id,
            data_types=data_types,
            expiration_time=expiration_time,
            access_policies=access_policies
        )
        
        self.assertTrue(success)
        self.assertIn("成功", message)
        self.assertIsNotNone(authorization_id)
        
        return authorization_id
    
    def test_authorize_access(self):
        """测试授权访问"""
        loop = asyncio.get_event_loop()
        authorization_id = loop.run_until_complete(self.async_authorize_access())
        self.assertIsNotNone(authorization_id)
    
    async def async_revoke_access(self):
        """测试撤销访问的异步方法"""
        # 先授权
        authorization_id = await self.async_authorize_access()
        
        # 然后撤销
        user_id = "test_user"
        revocation_reason = "不再需要访问"
        
        success, message = await self.service.revoke_access(
            authorization_id=authorization_id,
            user_id=user_id,
            revocation_reason=revocation_reason
        )
        
        self.assertTrue(success)
        self.assertIn("成功", message)
        
        return success
    
    def test_revoke_access(self):
        """测试撤销访问"""
        loop = asyncio.get_event_loop()
        success = loop.run_until_complete(self.async_revoke_access())
        self.assertTrue(success)
    
    async def async_get_blockchain_status(self):
        """测试获取区块链状态的异步方法"""
        # 设置 mock 区块数据
        latest_block = MagicMock()
        latest_block.timestamp = int(time.time())
        self.web3_mock.eth.get_block.return_value = latest_block
        
        # 设置 mock 节点版本信息
        self.web3_mock.net.version = "1"
        self.web3_mock.net.peer_count = 5
        
        status, success = await self.service.get_blockchain_status(include_node_info=True)
        
        self.assertTrue(success)
        self.assertIsNotNone(status)
        self.assertEqual(status["current_block_height"], 12345)
        self.assertIn("connected_nodes", status)
        self.assertIn("consensus_status", status)
        self.assertIn("sync_percentage", status)
        self.assertIn("last_block_timestamp", status)
        self.assertIn("node_info", status)
        
        return status
    
    def test_get_blockchain_status(self):
        """测试获取区块链状态"""
        loop = asyncio.get_event_loop()
        status = loop.run_until_complete(self.async_get_blockchain_status())
        self.assertIsNotNone(status)
    
    async def async_get_health_data_records(self):
        """测试获取健康数据记录的异步方法"""
        user_id = "test_user"
        
        records, total_count = await self.service.get_health_data_records(
            user_id=user_id,
            data_type=DataType.VITAL_SIGNS,
            page=1,
            page_size=10
        )
        
        self.assertIsNotNone(records)
        self.assertEqual(len(records), 0)  # 模拟实现返回空列表
        self.assertEqual(total_count, 0)
        
        return records
    
    def test_get_health_data_records(self):
        """测试获取健康数据记录"""
        loop = asyncio.get_event_loop()
        records = loop.run_until_complete(self.async_get_health_data_records())
        self.assertIsNotNone(records)


if __name__ == "__main__":
    unittest.main() 