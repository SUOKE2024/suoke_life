#!/usr/bin/env python3

"""
零知识证明工具单元测试
"""

import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock

from internal.blockchain.zkp_utils import ZKPUtils
from internal.model.config import AppConfig
from internal.model.entities import DataType


class TestZKPUtils(unittest.TestCase):
    """零知识证明工具测试类"""

    def setUp(self):
        """测试前的准备工作"""
        # 创建临时目录存放验证器配置
        self.temp_dir = tempfile.TemporaryDirectory()

        # 创建模拟配置
        self.config = MagicMock(spec=AppConfig)
        self.config.zkp = MagicMock()
        self.config.zkp.verifier_configs_dir = self.temp_dir.name

        # 创建样例验证器配置
        self._create_sample_verifier_configs()

        # 初始化ZKP工具
        self.zkp_utils = ZKPUtils(self.config)

    def tearDown(self):
        """测试后的清理工作"""
        self.temp_dir.cleanup()

    def _create_sample_verifier_configs(self):
        """创建样例验证器配置文件"""
        verifiers = {
            "inquiry_verifier": {
                "version": "1.0",
                "private_inputs_schema": {
                    "symptoms": {"type": "array", "required": True},
                    "medical_history": {"type": "object", "required": False}
                },
                "public_inputs_schema": {
                    "symptom_count": {"type": "integer", "required": True},
                    "has_chronic_disease": {"type": "boolean", "required": True}
                }
            },
            "listen_verifier": {
                "version": "1.0",
                "private_inputs_schema": {
                    "voice_features": {"type": "array", "required": True},
                    "voice_duration": {"type": "number", "required": True}
                },
                "public_inputs_schema": {
                    "voice_quality": {"type": "string", "required": True},
                    "has_breathing_issues": {"type": "boolean", "required": True}
                }
            }
        }

        # 写入验证器配置文件
        for name, config in verifiers.items():
            with open(os.path.join(self.temp_dir.name, f"{name}.json"), "w") as f:
                json.dump(config, f)

    def test_load_verifier_configs(self):
        """测试验证器配置加载"""
        # 验证是否加载了正确数量的验证器配置
        self.assertEqual(len(self.zkp_utils.verifier_configs), 2)
        self.assertIn("inquiry_verifier", self.zkp_utils.verifier_configs)
        self.assertIn("listen_verifier", self.zkp_utils.verifier_configs)

        # 验证配置内容是否正确
        inquiry_config = self.zkp_utils.verifier_configs["inquiry_verifier"]
        self.assertEqual(inquiry_config["version"], "1.0")
        self.assertIn("private_inputs_schema", inquiry_config)
        self.assertIn("public_inputs_schema", inquiry_config)

    def test_get_verifier_type(self):
        """测试根据数据类型获取验证器类型"""
        # 测试已知映射
        self.assertEqual(self.zkp_utils.get_verifier_type(DataType.INQUIRY), "inquiry_verifier")
        self.assertEqual(self.zkp_utils.get_verifier_type(DataType.LISTEN), "listen_verifier")
        self.assertEqual(self.zkp_utils.get_verifier_type(DataType.LOOK), "look_verifier")

        # 测试默认验证器
        self.assertEqual(self.zkp_utils.get_verifier_type(None), "generic_verifier")

    def test_preprocess_inputs(self):
        """测试输入预处理"""
        # 测试类型转换
        schema = {
            "int_field": {"type": "integer", "required": True},
            "float_field": {"type": "number", "required": True},
            "bool_field": {"type": "boolean", "required": True},
            "str_field": {"type": "string", "required": True},
            "optional_field": {"type": "string", "required": False},
            "default_field": {"type": "number", "required": True, "default": 42}
        }

        inputs = {
            "int_field": "123",
            "float_field": "3.14",
            "bool_field": 1,
            "str_field": "test"
        }

        processed = self.zkp_utils._preprocess_inputs(inputs, schema)

        self.assertEqual(processed["int_field"], 123)
        self.assertEqual(processed["float_field"], 3.14)
        self.assertEqual(processed["bool_field"], True)
        self.assertEqual(processed["str_field"], "test")
        self.assertEqual(processed["default_field"], 42)
        self.assertNotIn("optional_field", processed)

        # 测试缺少必需字段
        with self.assertRaises(ValueError):
            self.zkp_utils._preprocess_inputs({}, {"required_field": {"type": "string", "required": True}})

    async def test_generate_proof(self):
        """测试生成零知识证明"""
        # 准备测试数据
        user_id = "test_user"
        data_type = DataType.INQUIRY
        private_inputs = {
            "symptoms": ["fever", "cough"],
            "medical_history": {"allergies": ["pollen"]}
        }
        public_inputs = {
            "symptom_count": 2,
            "has_chronic_disease": False
        }

        # 调用方法
        proof, public_bytes, metadata = await self.zkp_utils.generate_proof(
            data_type, user_id, private_inputs, public_inputs
        )

        # 验证结果
        self.assertIsInstance(proof, bytes)
        self.assertIsInstance(public_bytes, bytes)
        self.assertIsInstance(metadata, dict)

        # 验证元数据内容
        self.assertEqual(metadata["verifier_type"], "inquiry_verifier")
        self.assertEqual(metadata["data_type"], data_type.value)
        self.assertEqual(metadata["user_id"], user_id)
        self.assertEqual(metadata["proof_version"], "1.0")
        self.assertIn("timestamp", metadata)

        # 验证证明大小
        self.assertEqual(len(proof), 128)  # 模拟实现中的大小

    async def test_verify_proof(self):
        """测试验证零知识证明"""
        # 准备测试数据
        user_id = "test_user"
        verifier_id = "test_verifier"
        data_type = DataType.INQUIRY
        private_inputs = {
            "symptoms": ["fever", "cough"],
            "medical_history": {"allergies": ["pollen"]}
        }
        public_inputs = {
            "symptom_count": 2,
            "has_chronic_disease": False
        }

        # 生成证明
        proof, public_bytes, _ = await self.zkp_utils.generate_proof(
            data_type, user_id, private_inputs, public_inputs
        )

        # 验证证明
        valid, details = await self.zkp_utils.verify_proof(
            proof, public_bytes, data_type, verifier_id
        )

        # 验证结果
        self.assertTrue(valid)
        self.assertIsInstance(details, dict)

        # 验证详情内容
        self.assertTrue(details["verified_locally"])
        self.assertEqual(details["verifier_type"], "inquiry_verifier")
        self.assertEqual(details["data_type"], data_type.value)
        self.assertEqual(details["verifier_id"], verifier_id)
        self.assertIn("timestamp", details)
        self.assertEqual(details["proof_size"], len(proof))
        self.assertEqual(details["public_inputs_size"], len(public_bytes))

        # 测试无效的证明
        invalid_proof = b"\x00" * 128
        valid, details = await self.zkp_utils.verify_proof(
            invalid_proof, public_bytes, data_type, verifier_id
        )

        # 验证拒绝无效证明
        self.assertFalse(valid)

    def test_bytes_to_ints(self):
        """测试字节数组转整数数组"""
        # 测试空数组
        self.assertEqual(self.zkp_utils._bytes_to_ints(b""), [])

        # 测试单个整数
        data = b"\x00\x01\x02\x03" + b"\x00" * 28
        result = self.zkp_utils._bytes_to_ints(data, 32)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], 0x010203)

        # 测试多个整数
        data = b"\x01\x02\x03\x04" * 8
        result = self.zkp_utils._bytes_to_ints(data, 4)
        self.assertEqual(len(result), 8)
        self.assertEqual(result[0], 0x01020304)

        # 测试不完整的最后一块
        data = b"\x01\x02\x03" * 5
        result = self.zkp_utils._bytes_to_ints(data, 4)
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0], 0x01020301)
        self.assertEqual(result[3], (0x01020300))  # 最后一块填充了0

    def test_prepare_proof_for_contract(self):
        """测试准备合约格式的证明数据"""
        # 准备测试数据
        proof = b"\x01\x02\x03\x04" * 32
        public_inputs = b"\x05\x06\x07\x08" * 16

        # 调用方法
        proof_ints, public_inputs_ints = self.zkp_utils.prepare_proof_for_contract(
            proof, public_inputs
        )

        # 验证结果
        self.assertIsInstance(proof_ints, list)
        self.assertIsInstance(public_inputs_ints, list)

        # 验证数组大小
        self.assertEqual(len(proof_ints), 4)  # 32字节的块
        self.assertEqual(len(public_inputs_ints), 2)  # 16字节的块


if __name__ == "__main__":
    unittest.main()
