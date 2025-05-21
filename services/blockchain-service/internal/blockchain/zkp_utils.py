#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
零知识证明工具模块

该模块提供零知识证明的生成、验证与处理功能。
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union

import numpy as np
from eth_account import Account
from eth_typing import HexStr
from hexbytes import HexBytes
from web3 import Web3

from internal.model.config import AppConfig
from internal.model.entities import DataType


class ZKPUtils:
    """零知识证明工具类，提供零知识证明的生成、验证和处理功能"""

    def __init__(self, config: AppConfig):
        """
        初始化零知识证明工具
        
        Args:
            config: 应用配置对象
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # 加载验证器配置
        self._load_verifier_configs()
        
        self.logger.info(f"零知识证明工具初始化成功: 已加载 {len(self.verifier_configs)} 个验证器配置")
    
    def _load_verifier_configs(self):
        """加载验证器配置"""
        try:
            self.verifier_configs = {}
            verifier_dir = Path(self.config.zkp.verifier_configs_dir)
            
            # 读取所有验证器配置文件
            for config_file in verifier_dir.glob("*.json"):
                try:
                    with config_file.open("r") as f:
                        verifier_config = json.load(f)
                        verifier_name = config_file.stem
                        self.verifier_configs[verifier_name] = verifier_config
                except Exception as e:
                    self.logger.error(f"加载验证器配置失败 ({config_file}): {str(e)}")
                    continue
            
        except Exception as e:
            self.logger.error(f"加载验证器配置目录失败: {str(e)}")
            self.verifier_configs = {}
    
    def get_verifier_type(self, data_type: DataType) -> str:
        """
        根据数据类型获取验证器类型
        
        Args:
            data_type: 数据类型
            
        Returns:
            验证器类型名称
        """
        # 数据类型到验证器类型的映射
        verifier_mapping = {
            DataType.INQUIRY: "inquiry_verifier",
            DataType.LISTEN: "listen_verifier",
            DataType.LOOK: "look_verifier",
            DataType.PALPATION: "palpation_verifier",
            DataType.VITAL_SIGNS: "vital_signs_verifier",
            DataType.LABORATORY: "lab_verifier",
            DataType.MEDICATION: "medication_verifier",
            DataType.NUTRITION: "nutrition_verifier",
            DataType.ACTIVITY: "activity_verifier",
            DataType.SLEEP: "sleep_verifier",
            DataType.SYNDROME: "syndrome_verifier",
            DataType.PRESCRIPTION: "prescription_verifier",
            DataType.HEALTH_PLAN: "health_plan_verifier"
        }
        
        return verifier_mapping.get(data_type, "generic_verifier")
    
    async def generate_proof(
        self,
        data_type: DataType,
        user_id: str,
        private_inputs: Dict[str, Any],
        public_inputs: Dict[str, Any] = None
    ) -> Tuple[bytes, bytes, Dict[str, Any]]:
        """
        生成零知识证明
        
        Args:
            data_type: 数据类型
            user_id: 用户ID
            private_inputs: 私有输入数据
            public_inputs: 公共输入数据
            
        Returns:
            (证明数据, 公共输入数据, 证明元数据)
        """
        try:
            # 确定验证器类型
            verifier_type = self.get_verifier_type(data_type)
            
            # 检查验证器配置是否存在
            if verifier_type not in self.verifier_configs:
                raise ValueError(f"未找到验证器配置: {verifier_type}")
            
            # 获取验证器配置
            verifier_config = self.verifier_configs[verifier_type]
            
            # 预处理输入数据
            processed_private_inputs = self._preprocess_inputs(private_inputs, verifier_config.get("private_inputs_schema", {}))
            processed_public_inputs = self._preprocess_inputs(public_inputs or {}, verifier_config.get("public_inputs_schema", {}))
            
            # 生成证明 (通常会调用外部ZKP库，这里使用模拟实现)
            proof, public_bytes = self._mock_generate_proof(verifier_type, processed_private_inputs, processed_public_inputs)
            
            # 创建证明元数据
            metadata = {
                "verifier_type": verifier_type,
                "data_type": data_type.value,
                "user_id": user_id,
                "proof_version": verifier_config.get("version", "1.0"),
                "timestamp": self._current_timestamp()
            }
            
            self.logger.info(f"生成零知识证明成功: user_id={user_id}, data_type={data_type.value}, verifier={verifier_type}")
            return proof, public_bytes, metadata
            
        except Exception as e:
            self.logger.error(f"生成零知识证明失败: {str(e)}")
            raise
    
    def _preprocess_inputs(self, inputs: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据模式预处理输入数据
        
        Args:
            inputs: 输入数据
            schema: 输入模式
            
        Returns:
            预处理后的输入数据
        """
        # 实际项目中，这里会根据模式对输入进行验证、转换和预处理
        # 此处为简化实现
        processed = {}
        
        for field, field_schema in schema.items():
            if field in inputs:
                field_type = field_schema.get("type", "string")
                value = inputs[field]
                
                # 类型转换
                if field_type == "number" and isinstance(value, str):
                    try:
                        processed[field] = float(value)
                    except ValueError:
                        processed[field] = 0.0
                elif field_type == "integer" and not isinstance(value, int):
                    try:
                        processed[field] = int(float(value))
                    except (ValueError, TypeError):
                        processed[field] = 0
                elif field_type == "boolean" and not isinstance(value, bool):
                    processed[field] = bool(value)
                else:
                    processed[field] = value
            elif field_schema.get("required", False):
                # 使用默认值
                default_value = field_schema.get("default", None)
                if default_value is not None:
                    processed[field] = default_value
                else:
                    raise ValueError(f"缺少必需字段: {field}")
        
        return processed
    
    def _mock_generate_proof(
        self,
        verifier_type: str,
        private_inputs: Dict[str, Any],
        public_inputs: Dict[str, Any]
    ) -> Tuple[bytes, bytes]:
        """
        模拟生成零知识证明（实际项目中应替换为真实的ZKP库实现）
        
        Args:
            verifier_type: 验证器类型
            private_inputs: 私有输入
            public_inputs: 公共输入
            
        Returns:
            (证明数据, 公共输入数据)
        """
        # 注意：这是一个模拟实现，实际项目中应使用真实的ZKP库
        # 例如snarkjs, circom, zokrates等
        
        # 将输入序列化为JSON
        private_json = json.dumps(private_inputs, sort_keys=True).encode()
        public_json = json.dumps(public_inputs, sort_keys=True).encode()
        
        # 生成一个确定性但唯一的哈希作为"证明"
        # 在实际项目中，这里应该是调用ZKP库生成的真实证明
        import hashlib
        combined = private_json + b":" + public_json + bytes(verifier_type, 'utf-8')
        proof_hash = hashlib.sha256(combined).digest()
        
        # 创建模拟证明和公共输入
        mock_proof = bytearray(proof_hash)
        mock_proof.extend(os.urandom(116))  # 扩展到128字节
        
        mock_public_inputs = bytearray(hashlib.sha256(public_json).digest())
        mock_public_inputs.extend(os.urandom(32))  # 扩展到64字节
        
        return bytes(mock_proof), bytes(mock_public_inputs)
    
    async def verify_proof(
        self,
        proof: bytes,
        public_inputs: bytes,
        data_type: DataType,
        verifier_id: str = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        本地验证证明（链下验证）
        
        Args:
            proof: 证明数据
            public_inputs: 公共输入数据
            data_type: 数据类型
            verifier_id: 验证者ID
            
        Returns:
            (验证是否通过, 验证详情)
        """
        try:
            # 确定验证器类型
            verifier_type = self.get_verifier_type(data_type)
            
            # 在实际项目中，这里应该调用ZKP库进行本地验证
            # 此处为模拟实现
            verification_result = self._mock_verify_proof(proof, public_inputs, verifier_type)
            
            # 创建验证详情
            verification_details = {
                "verified_locally": verification_result,
                "verifier_type": verifier_type,
                "data_type": data_type.value,
                "timestamp": self._current_timestamp(),
                "proof_size": len(proof),
                "public_inputs_size": len(public_inputs)
            }
            
            if verifier_id:
                verification_details["verifier_id"] = verifier_id
            
            self.logger.info(f"本地验证零知识证明: data_type={data_type.value}, result={verification_result}")
            return verification_result, verification_details
            
        except Exception as e:
            self.logger.error(f"本地验证零知识证明失败: {str(e)}")
            return False, {"error": str(e)}
    
    def _mock_verify_proof(self, proof: bytes, public_inputs: bytes, verifier_type: str) -> bool:
        """
        模拟验证零知识证明（实际项目中应替换为真实的ZKP库实现）
        
        Args:
            proof: 证明数据
            public_inputs: 公共输入数据
            verifier_type: 验证器类型
            
        Returns:
            验证是否通过
        """
        # 注意：这是一个模拟实现，实际项目中应使用真实的ZKP库
        # 在实际应用中，这里应该调用如snarkjs.verify()等函数
        
        # 检查证明和公共输入的长度
        if len(proof) < 32 or len(public_inputs) < 32:
            return False
        
        # 简单实现：检查证明的前32字节是否为有效哈希
        # 在真实应用中，这里应该执行完整的零知识证明验证
        try:
            # 模拟验证逻辑：检查证明是否有特定格式
            # 实际验证应使用适当的椭圆曲线算法和验证程序
            return proof[0] != 0 and proof[1] != 0
        except Exception:
            return False
    
    def prepare_proof_for_contract(
        self,
        proof: bytes,
        public_inputs: bytes
    ) -> Tuple[List[int], List[int]]:
        """
        准备证明数据用于智能合约验证
        
        Args:
            proof: 证明数据
            public_inputs: 公共输入数据
            
        Returns:
            (合约格式的证明数据, 合约格式的公共输入)
        """
        # 在实际项目中，这里应该将证明和公共输入转换为适合合约处理的格式
        # 例如，从字节数组转换为大整数数组
        
        # 将字节数组转换为大整数数组
        proof_ints = self._bytes_to_ints(proof)
        public_inputs_ints = self._bytes_to_ints(public_inputs)
        
        return proof_ints, public_inputs_ints
    
    def _bytes_to_ints(self, data: bytes, chunk_size: int = 32) -> List[int]:
        """
        将字节数组转换为大整数数组
        
        Args:
            data: 字节数据
            chunk_size: 每个整数的字节大小
            
        Returns:
            大整数数组
        """
        result = []
        
        # 将数据分块并转换为整数
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i+chunk_size]
            if len(chunk) < chunk_size:
                # 如果最后一块不足chunk_size字节，填充0
                chunk = chunk + bytes(chunk_size - len(chunk))
            
            # 转换为整数
            value = int.from_bytes(chunk, byteorder='big')
            result.append(value)
        
        return result
    
    def _current_timestamp(self) -> int:
        """获取当前时间戳"""
        import time
        return int(time.time())
    
    def create_zero_knowledge_proof_request(
        self,
        data_type: DataType,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        创建零知识证明请求
        
        Args:
            data_type: 数据类型
            requirements: 证明要求
            
        Returns:
            证明请求配置
        """
        verifier_type = self.get_verifier_type(data_type)
        
        # 创建证明请求
        request = {
            "verifier_type": verifier_type,
            "data_type": data_type.value,
            "requirements": requirements,
            "timestamp": self._current_timestamp(),
            "format_version": "1.0"
        }
        
        return request 