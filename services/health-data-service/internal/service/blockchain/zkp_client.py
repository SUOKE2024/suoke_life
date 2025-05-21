#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
零知识证明(ZKP)客户端
提供健康数据的隐私保护和选择性披露功能
"""

import hashlib
import json
import logging
import os
from typing import Dict, List, Any, Optional, Tuple
import uuid

import grpc
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives import serialization

# 导入区块链服务客户端
from .blockchain_client import BlockchainClient

logger = logging.getLogger(__name__)


class ZKPClient:
    """零知识证明客户端"""

    def __init__(self, blockchain_client: BlockchainClient = None):
        """初始化ZKP客户端
        
        Args:
            blockchain_client: 区块链客户端，用于存储证明
        """
        self.blockchain_client = blockchain_client or BlockchainClient()
        self._init_keys()
        
    def _init_keys(self):
        """初始化密钥对"""
        # 在生产环境中，这些密钥应该从安全的配置中读取
        try:
            key_dir = os.path.join(os.path.dirname(__file__), "../../../config/keys")
            os.makedirs(key_dir, exist_ok=True)
            
            private_key_path = os.path.join(key_dir, "zkp_private_key.pem")
            public_key_path = os.path.join(key_dir, "zkp_public_key.pem")
            
            if os.path.exists(private_key_path) and os.path.exists(public_key_path):
                # 从文件加载密钥
                with open(private_key_path, "rb") as f:
                    self.private_key = serialization.load_pem_private_key(
                        f.read(),
                        password=None
                    )
                    
                with open(public_key_path, "rb") as f:
                    self.public_key = serialization.load_pem_public_key(
                        f.read()
                    )
            else:
                # 生成新密钥对
                self.private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048
                )
                self.public_key = self.private_key.public_key()
                
                # 保存密钥到文件
                with open(private_key_path, "wb") as f:
                    f.write(self.private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption()
                    ))
                    
                with open(public_key_path, "wb") as f:
                    f.write(self.public_key.public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    ))
        except Exception as e:
            logger.error(f"初始化ZKP密钥对失败: {e}")
            # 生成临时密钥对，但不保存
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            self.public_key = self.private_key.public_key()

    def generate_health_data_proof(self, 
                                  user_id: str, 
                                  data: Dict[str, Any]) -> Dict[str, Any]:
        """生成健康数据证明
        
        Args:
            user_id: 用户ID
            data: 需要证明的健康数据
            
        Returns:
            Dict: 包含证明和验证信息的字典
        """
        # 创建健康数据的哈希
        data_hash = self._hash_data(data)
        
        # 使用私钥签名
        signature = self._sign_data(data_hash)
        
        # 生成证明ID
        proof_id = str(uuid.uuid4())
        
        # 创建证明对象
        proof = {
            "id": proof_id,
            "user_id": user_id,
            "data_hash": data_hash,
            "signature": signature,
            "public_key": self._serialize_public_key(),
            "timestamp": self._get_timestamp(),
            "metadata": {
                "data_type": data.get("data_type", ""),
                "scope": "health_data"
            }
        }
        
        # 将证明存储在区块链上
        try:
            tx_id = self.blockchain_client.store_proof(
                proof_id=proof_id,
                user_id=user_id,
                data_hash=data_hash,
                signature=signature
            )
            proof["blockchain_tx_id"] = tx_id
        except Exception as e:
            logger.error(f"存储证明到区块链失败: {e}")
            proof["blockchain_tx_id"] = None
        
        return proof
    
    def verify_health_data_proof(self, 
                                proof: Dict[str, Any], 
                                data: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """验证健康数据证明
        
        Args:
            proof: 证明对象
            data: 可选，需要验证的健康数据，如果不提供则只验证证明的完整性
            
        Returns:
            Tuple[bool, str]: (验证结果, 验证信息)
        """
        try:
            # 验证证明格式
            required_fields = ["id", "user_id", "data_hash", "signature", "public_key"]
            if not all(field in proof for field in required_fields):
                return False, "证明格式不正确，缺少必要字段"
            
            # 如果提供了数据，验证数据哈希
            if data is not None:
                computed_hash = self._hash_data(data)
                if computed_hash != proof["data_hash"]:
                    return False, "数据哈希不匹配，数据可能已被篡改"
            
            # 验证签名
            public_key = self._deserialize_public_key(proof["public_key"])
            is_valid = self._verify_signature(
                public_key=public_key,
                data_hash=proof["data_hash"],
                signature=proof["signature"]
            )
            
            if not is_valid:
                return False, "签名验证失败，证明无效"
            
            # 验证区块链上的证明
            if "blockchain_tx_id" in proof and proof["blockchain_tx_id"]:
                try:
                    is_valid_on_chain = self.blockchain_client.verify_proof(
                        proof_id=proof["id"],
                        user_id=proof["user_id"],
                        data_hash=proof["data_hash"]
                    )
                    if not is_valid_on_chain:
                        return False, "区块链验证失败，证明可能未存储在链上或数据不匹配"
                except Exception as e:
                    logger.warning(f"区块链验证异常: {e}")
                    return True, "签名验证成功，但区块链验证失败，请检查区块链服务"
            
            return True, "证明验证成功"
        except Exception as e:
            logger.error(f"验证证明时发生错误: {e}")
            return False, f"验证过程出错: {str(e)}"
    
    def generate_selective_disclosure_proof(self, 
                                          user_id: str, 
                                          data: Dict[str, Any],
                                          disclosed_fields: List[str]) -> Dict[str, Any]:
        """生成选择性披露证明
        
        允许用户只披露健康数据中的特定字段，同时证明其他未披露字段的存在性
        
        Args:
            user_id: 用户ID
            data: 完整的健康数据
            disclosed_fields: 要披露的字段列表
            
        Returns:
            Dict: 证明对象
        """
        # 分离披露和未披露的字段
        disclosed_data = {k: data[k] for k in disclosed_fields if k in data}
        undisclosed_fields = [k for k in data if k not in disclosed_fields]
        
        # 为未披露字段生成承诺（哈希）
        undisclosed_commitments = {}
        for field in undisclosed_fields:
            if field in data:
                field_data = {field: data[field]}
                field_hash = self._hash_data(field_data)
                undisclosed_commitments[field] = field_hash
        
        # 生成完整数据的哈希作为参考
        full_data_hash = self._hash_data(data)
        
        # 生成证明
        proof_id = str(uuid.uuid4())
        selective_proof = {
            "id": proof_id,
            "user_id": user_id,
            "disclosed_data": disclosed_data,
            "undisclosed_commitments": undisclosed_commitments,
            "full_data_hash": full_data_hash,
            "signature": self._sign_data(full_data_hash),
            "public_key": self._serialize_public_key(),
            "timestamp": self._get_timestamp(),
            "metadata": {
                "disclosed_fields": disclosed_fields,
                "scope": "selective_disclosure"
            }
        }
        
        # 存储到区块链
        try:
            tx_id = self.blockchain_client.store_selective_disclosure(
                proof_id=proof_id,
                user_id=user_id,
                full_data_hash=full_data_hash,
                disclosed_fields=disclosed_fields
            )
            selective_proof["blockchain_tx_id"] = tx_id
        except Exception as e:
            logger.error(f"存储选择性披露证明到区块链失败: {e}")
            selective_proof["blockchain_tx_id"] = None
            
        return selective_proof
    
    def verify_selective_disclosure(self, proof: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """验证选择性披露证明
        
        Args:
            proof: 选择性披露证明
            
        Returns:
            Tuple[bool, str, Dict]: (验证结果, 验证信息, 已披露的数据)
        """
        try:
            required_fields = ["id", "user_id", "disclosed_data", "undisclosed_commitments", 
                              "full_data_hash", "signature", "public_key"]
            if not all(field in proof for field in required_fields):
                return False, "证明格式不正确，缺少必要字段", {}
            
            # 验证签名
            public_key = self._deserialize_public_key(proof["public_key"])
            is_valid = self._verify_signature(
                public_key=public_key,
                data_hash=proof["full_data_hash"],
                signature=proof["signature"]
            )
            
            if not is_valid:
                return False, "签名验证失败，证明无效", {}
            
            # 验证区块链上的证明（如果有）
            if "blockchain_tx_id" in proof and proof["blockchain_tx_id"]:
                try:
                    is_valid_on_chain = self.blockchain_client.verify_selective_disclosure(
                        proof_id=proof["id"],
                        user_id=proof["user_id"],
                        full_data_hash=proof["full_data_hash"]
                    )
                    if not is_valid_on_chain:
                        return False, "区块链验证失败，证明可能未存储在链上或数据不匹配", {}
                except Exception as e:
                    logger.warning(f"区块链验证异常: {e}")
            
            return True, "选择性披露验证成功", proof["disclosed_data"]
        except Exception as e:
            logger.error(f"验证选择性披露证明时发生错误: {e}")
            return False, f"验证过程出错: {str(e)}", {}
    
    def _hash_data(self, data: Dict[str, Any]) -> str:
        """计算数据的哈希值
        
        Args:
            data: 要哈希的数据
            
        Returns:
            str: 哈希值的十六进制表示
        """
        # 确保数据序列化的一致性
        serialized_data = json.dumps(data, sort_keys=True)
        hash_object = hashlib.sha256(serialized_data.encode())
        return hash_object.hexdigest()
    
    def _sign_data(self, data_hash: str) -> str:
        """使用私钥对数据哈希进行签名
        
        Args:
            data_hash: 数据哈希
            
        Returns:
            str: 签名的Base64编码
        """
        signature = self.private_key.sign(
            data_hash.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature.hex()
    
    def _verify_signature(self, public_key: RSAPublicKey, data_hash: str, signature: str) -> bool:
        """验证签名
        
        Args:
            public_key: 公钥
            data_hash: 数据哈希
            signature: 签名的十六进制表示
            
        Returns:
            bool: 验证结果
        """
        try:
            signature_bytes = bytes.fromhex(signature)
            public_key.verify(
                signature_bytes,
                data_hash.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
    
    def _serialize_public_key(self) -> str:
        """序列化公钥为PEM格式字符串
        
        Returns:
            str: PEM格式的公钥
        """
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode()
    
    def _deserialize_public_key(self, pem_key: str) -> RSAPublicKey:
        """从PEM格式字符串反序列化公钥
        
        Args:
            pem_key: PEM格式的公钥
            
        Returns:
            RSAPublicKey: 公钥对象
        """
        public_key = serialization.load_pem_public_key(
            pem_key.encode()
        )
        return public_key
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳
        
        Returns:
            str: ISO 8601格式的时间戳
        """
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z" 