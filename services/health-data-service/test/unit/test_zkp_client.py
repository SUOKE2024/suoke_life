#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
零知识证明客户端模块的单元测试
"""

import unittest
from unittest.mock import MagicMock, patch
import json
import os
import tempfile
import uuid
from datetime import datetime

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# 导入被测试的模块
from internal.service.blockchain.zkp_client import ZKPClient
from internal.service.blockchain.blockchain_client import BlockchainClient


class TestZKPClient(unittest.TestCase):
    """零知识证明客户端测试类"""

    def setUp(self):
        """测试前的准备工作"""
        # 模拟区块链客户端
        self.mock_blockchain_client = MagicMock(spec=BlockchainClient)
        self.mock_blockchain_client.store_proof.return_value = "test_tx_id"
        self.mock_blockchain_client.verify_proof.return_value = True
        self.mock_blockchain_client.store_selective_disclosure.return_value = "test_selective_tx_id"
        self.mock_blockchain_client.verify_selective_disclosure.return_value = True
        
        # 使用临时目录存储测试密钥
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # 创建测试密钥
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()
        
        # 保存测试密钥
        self.private_key_path = os.path.join(self.temp_dir.name, "zkp_private_key.pem")
        self.public_key_path = os.path.join(self.temp_dir.name, "zkp_public_key.pem")
        
        with open(self.private_key_path, "wb") as f:
            f.write(self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        with open(self.public_key_path, "wb") as f:
            f.write(self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))
        
        # 创建测试数据
        self.test_user_id = str(uuid.uuid4())
        self.test_health_data = {
            "data_type": "heart_rate",
            "value": 75,
            "unit": "bpm",
            "timestamp": datetime.utcnow().isoformat(),
            "device_type": "apple_health"
        }
        
        # 需要打补丁的路径
        self.os_path_dirname_patcher = patch("os.path.dirname")
        self.mock_dirname = self.os_path_dirname_patcher.start()
        self.mock_dirname.return_value = self.temp_dir.name
    
    def tearDown(self):
        """测试后的清理工作"""
        self.os_path_dirname_patcher.stop()
        self.temp_dir.cleanup()
    
    def test_init_keys(self):
        """测试密钥初始化功能"""
        zkp_client = ZKPClient(blockchain_client=self.mock_blockchain_client)
        
        # 验证密钥已正确加载
        self.assertIsNotNone(zkp_client.private_key)
        self.assertIsNotNone(zkp_client.public_key)
    
    def test_hash_data(self):
        """测试数据哈希功能"""
        zkp_client = ZKPClient(blockchain_client=self.mock_blockchain_client)
        
        hash1 = zkp_client._hash_data(self.test_health_data)
        
        # 验证哈希不为空
        self.assertIsNotNone(hash1)
        self.assertTrue(isinstance(hash1, str))
        self.assertEqual(len(hash1), 64)  # SHA-256哈希的十六进制长度
        
        # 验证相同数据产生相同哈希
        hash2 = zkp_client._hash_data(self.test_health_data)
        self.assertEqual(hash1, hash2)
        
        # 验证不同数据产生不同哈希
        modified_data = self.test_health_data.copy()
        modified_data["value"] = 76
        hash3 = zkp_client._hash_data(modified_data)
        self.assertNotEqual(hash1, hash3)
    
    def test_sign_and_verify(self):
        """测试签名和验证功能"""
        zkp_client = ZKPClient(blockchain_client=self.mock_blockchain_client)
        
        # 计算数据哈希
        data_hash = zkp_client._hash_data(self.test_health_data)
        
        # 签名
        signature = zkp_client._sign_data(data_hash)
        self.assertIsNotNone(signature)
        
        # 验证签名
        is_valid = zkp_client._verify_signature(
            zkp_client.public_key,
            data_hash,
            signature
        )
        self.assertTrue(is_valid)
        
        # 验证错误的签名
        is_valid = zkp_client._verify_signature(
            zkp_client.public_key,
            "wrong_hash",
            signature
        )
        self.assertFalse(is_valid)
    
    def test_generate_health_data_proof(self):
        """测试健康数据证明生成功能"""
        zkp_client = ZKPClient(blockchain_client=self.mock_blockchain_client)
        
        proof = zkp_client.generate_health_data_proof(
            user_id=self.test_user_id,
            data=self.test_health_data
        )
        
        # 验证证明包含所有必要字段
        self.assertIn("id", proof)
        self.assertIn("user_id", proof)
        self.assertIn("data_hash", proof)
        self.assertIn("signature", proof)
        self.assertIn("public_key", proof)
        self.assertIn("timestamp", proof)
        self.assertIn("metadata", proof)
        self.assertIn("blockchain_tx_id", proof)
        
        # 验证用户ID正确
        self.assertEqual(proof["user_id"], self.test_user_id)
        
        # 验证区块链交易ID正确
        self.assertEqual(proof["blockchain_tx_id"], "test_tx_id")
        
        # 验证blockchain_client.store_proof被正确调用
        self.mock_blockchain_client.store_proof.assert_called_once_with(
            proof_id=proof["id"],
            user_id=self.test_user_id,
            data_hash=proof["data_hash"],
            signature=proof["signature"]
        )
    
    def test_verify_health_data_proof(self):
        """测试健康数据证明验证功能"""
        zkp_client = ZKPClient(blockchain_client=self.mock_blockchain_client)
        
        # 生成证明
        proof = zkp_client.generate_health_data_proof(
            user_id=self.test_user_id,
            data=self.test_health_data
        )
        
        # 验证证明（不提供数据）
        is_valid, message = zkp_client.verify_health_data_proof(proof)
        self.assertTrue(is_valid)
        self.assertEqual(message, "证明验证成功")
        
        # 验证证明（提供原始数据）
        is_valid, message = zkp_client.verify_health_data_proof(proof, self.test_health_data)
        self.assertTrue(is_valid)
        
        # 验证证明（提供篡改的数据）
        modified_data = self.test_health_data.copy()
        modified_data["value"] = 76
        is_valid, message = zkp_client.verify_health_data_proof(proof, modified_data)
        self.assertFalse(is_valid)
        self.assertIn("数据哈希不匹配", message)
        
        # 验证区块链验证失败的情况
        self.mock_blockchain_client.verify_proof.return_value = False
        is_valid, message = zkp_client.verify_health_data_proof(proof)
        self.assertFalse(is_valid)
        self.assertIn("区块链验证失败", message)
    
    def test_generate_selective_disclosure_proof(self):
        """测试选择性披露证明生成功能"""
        zkp_client = ZKPClient(blockchain_client=self.mock_blockchain_client)
        
        # 定义要披露的字段
        disclosed_fields = ["data_type", "unit"]
        
        proof = zkp_client.generate_selective_disclosure_proof(
            user_id=self.test_user_id,
            data=self.test_health_data,
            disclosed_fields=disclosed_fields
        )
        
        # 验证证明包含所有必要字段
        self.assertIn("id", proof)
        self.assertIn("user_id", proof)
        self.assertIn("disclosed_data", proof)
        self.assertIn("undisclosed_commitments", proof)
        self.assertIn("full_data_hash", proof)
        self.assertIn("signature", proof)
        self.assertIn("public_key", proof)
        self.assertIn("timestamp", proof)
        self.assertIn("metadata", proof)
        
        # 验证披露的数据仅包含指定字段
        self.assertEqual(len(proof["disclosed_data"]), len(disclosed_fields))
        for field in disclosed_fields:
            self.assertIn(field, proof["disclosed_data"])
            self.assertEqual(proof["disclosed_data"][field], self.test_health_data[field])
        
        # 验证未披露字段的承诺
        undisclosed_fields = [k for k in self.test_health_data if k not in disclosed_fields]
        for field in undisclosed_fields:
            self.assertIn(field, proof["undisclosed_commitments"])
        
        # 验证blockchain_client.store_selective_disclosure被正确调用
        self.mock_blockchain_client.store_selective_disclosure.assert_called_once_with(
            proof_id=proof["id"],
            user_id=self.test_user_id,
            full_data_hash=proof["full_data_hash"],
            disclosed_fields=disclosed_fields
        )
    
    def test_verify_selective_disclosure(self):
        """测试选择性披露证明验证功能"""
        zkp_client = ZKPClient(blockchain_client=self.mock_blockchain_client)
        
        # 定义要披露的字段
        disclosed_fields = ["data_type", "unit"]
        
        # 生成证明
        proof = zkp_client.generate_selective_disclosure_proof(
            user_id=self.test_user_id,
            data=self.test_health_data,
            disclosed_fields=disclosed_fields
        )
        
        # 验证证明
        is_valid, message, disclosed_data = zkp_client.verify_selective_disclosure(proof)
        self.assertTrue(is_valid)
        self.assertEqual(message, "选择性披露验证成功")
        
        # 验证披露的数据
        self.assertEqual(len(disclosed_data), len(disclosed_fields))
        for field in disclosed_fields:
            self.assertIn(field, disclosed_data)
            self.assertEqual(disclosed_data[field], self.test_health_data[field])
        
        # 验证区块链验证失败的情况
        self.mock_blockchain_client.verify_selective_disclosure.return_value = False
        is_valid, message, disclosed_data = zkp_client.verify_selective_disclosure(proof)
        self.assertFalse(is_valid)
        self.assertIn("区块链验证失败", message)


if __name__ == "__main__":
    unittest.main() 