#!/usr/bin/env python3
"""
安全模块

提供零知识证明、数据加密、哈希验证等安全功能。
"""

import hashlib
import hmac
import secrets
import json
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass, asdict
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import logging

from .config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class HealthDataProof:
    """健康数据零知识证明"""
    proof: Dict[str, Any]
    public_inputs: Dict[str, Any]
    verification_key: Dict[str, Any]
    timestamp: str
    data_hash: str
    proof_type: str
    validity: bool = True


@dataclass
class EncryptedData:
    """加密数据"""
    encrypted_data: str
    encryption_method: str
    key_id: str
    timestamp: str
    checksum: str


class CryptoManager:
    """加密管理器"""
    
    def __init__(self):
        self.settings = get_settings()
        self._symmetric_key = None
        self._private_key = None
        self._public_key = None
        self._initialize_keys()
    
    def _initialize_keys(self):
        """初始化加密密钥"""
        try:
            # 生成对称加密密钥
            if self.settings.security.encryption_key:
                key_bytes = self.settings.security.encryption_key.encode()
                # 使用PBKDF2派生密钥
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=b'health_data_salt',
                    iterations=100000,
                )
                key = base64.urlsafe_b64encode(kdf.derive(key_bytes))
                self._symmetric_key = Fernet(key)
            else:
                # 生成随机密钥
                key = Fernet.generate_key()
                self._symmetric_key = Fernet(key)
            
            # 生成RSA密钥对
            self._private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            self._public_key = self._private_key.public_key()
            
            logger.info("加密密钥初始化成功")
            
        except Exception as e:
            logger.error(f"加密密钥初始化失败: {e}")
            raise
    
    def encrypt_data(self, data: Dict[str, Any]) -> EncryptedData:
        """加密数据"""
        try:
            # 序列化数据
            data_json = json.dumps(data, ensure_ascii=False, sort_keys=True)
            data_bytes = data_json.encode('utf-8')
            
            # 对称加密
            encrypted_bytes = self._symmetric_key.encrypt(data_bytes)
            encrypted_data = base64.b64encode(encrypted_bytes).decode('utf-8')
            
            # 计算校验和
            checksum = hashlib.sha256(data_bytes).hexdigest()
            
            return EncryptedData(
                encrypted_data=encrypted_data,
                encryption_method="Fernet",
                key_id="default",
                timestamp=datetime.now().isoformat(),
                checksum=checksum
            )
            
        except Exception as e:
            logger.error(f"数据加密失败: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: EncryptedData) -> Dict[str, Any]:
        """解密数据"""
        try:
            # Base64解码
            encrypted_bytes = base64.b64decode(encrypted_data.encrypted_data.encode('utf-8'))
            
            # 对称解密
            decrypted_bytes = self._symmetric_key.decrypt(encrypted_bytes)
            
            # 验证校验和
            checksum = hashlib.sha256(decrypted_bytes).hexdigest()
            if checksum != encrypted_data.checksum:
                raise ValueError("数据校验和不匹配")
            
            # 反序列化
            data_json = decrypted_bytes.decode('utf-8')
            data = json.loads(data_json)
            
            return data
            
        except Exception as e:
            logger.error(f"数据解密失败: {e}")
            raise
    
    def sign_data(self, data: Dict[str, Any]) -> str:
        """数字签名"""
        try:
            # 序列化数据
            data_json = json.dumps(data, ensure_ascii=False, sort_keys=True)
            data_bytes = data_json.encode('utf-8')
            
            # RSA签名
            signature = self._private_key.sign(
                data_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return base64.b64encode(signature).decode('utf-8')
            
        except Exception as e:
            logger.error(f"数据签名失败: {e}")
            raise
    
    def verify_signature(self, data: Dict[str, Any], signature: str) -> bool:
        """验证数字签名"""
        try:
            # 序列化数据
            data_json = json.dumps(data, ensure_ascii=False, sort_keys=True)
            data_bytes = data_json.encode('utf-8')
            
            # Base64解码签名
            signature_bytes = base64.b64decode(signature.encode('utf-8'))
            
            # RSA验证
            self._public_key.verify(
                signature_bytes,
                data_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
            
        except Exception as e:
            logger.warning(f"数字签名验证失败: {e}")
            return False


class HashManager:
    """哈希管理器"""
    
    @staticmethod
    def calculate_hash(data: Dict[str, Any], algorithm: str = "sha256") -> str:
        """计算数据哈希"""
        try:
            # 序列化数据
            data_json = json.dumps(data, ensure_ascii=False, sort_keys=True)
            data_bytes = data_json.encode('utf-8')
            
            # 计算哈希
            if algorithm == "sha256":
                hash_obj = hashlib.sha256(data_bytes)
            elif algorithm == "sha512":
                hash_obj = hashlib.sha512(data_bytes)
            elif algorithm == "md5":
                hash_obj = hashlib.md5(data_bytes)
            else:
                raise ValueError(f"不支持的哈希算法: {algorithm}")
            
            return hash_obj.hexdigest()
            
        except Exception as e:
            logger.error(f"哈希计算失败: {e}")
            raise
    
    @staticmethod
    def verify_hash(data: Dict[str, Any], expected_hash: str, algorithm: str = "sha256") -> bool:
        """验证数据哈希"""
        try:
            calculated_hash = HashManager.calculate_hash(data, algorithm)
            return hmac.compare_digest(calculated_hash, expected_hash)
        except Exception as e:
            logger.error(f"哈希验证失败: {e}")
            return False


class ZKProofManager:
    """零知识证明管理器"""
    
    def __init__(self):
        self.crypto_manager = CryptoManager()
        self.hash_manager = HashManager()
    
    def generate_health_data_proof(
        self,
        data_type: str,
        health_data: Dict[str, Any],
        validation_params: Dict[str, Any]
    ) -> HealthDataProof:
        """生成健康数据零知识证明"""
        try:
            # 计算数据哈希
            data_hash = self.hash_manager.calculate_hash(health_data)
            
            # 生成证明（简化实现）
            proof = self._generate_proof(data_type, health_data, validation_params)
            
            # 生成公共输入
            public_inputs = self._extract_public_inputs(data_type, validation_params)
            
            # 生成验证密钥
            verification_key = self._generate_verification_key(data_type)
            
            return HealthDataProof(
                proof=proof,
                public_inputs=public_inputs,
                verification_key=verification_key,
                timestamp=datetime.now().isoformat(),
                data_hash=data_hash,
                proof_type=data_type,
                validity=True
            )
            
        except Exception as e:
            logger.error(f"零知识证明生成失败: {e}")
            raise
    
    def verify_health_data_proof(self, proof: HealthDataProof) -> bool:
        """验证健康数据零知识证明"""
        try:
            # 验证证明结构
            if not all([proof.proof, proof.public_inputs, proof.verification_key]):
                return False
            
            # 验证时间戳（可选）
            proof_time = datetime.fromisoformat(proof.timestamp)
            current_time = datetime.now()
            time_diff = (current_time - proof_time).total_seconds()
            
            # 证明有效期24小时
            if time_diff > 86400:
                logger.warning("零知识证明已过期")
                return False
            
            # 验证证明类型
            if proof.proof_type not in ["vital_signs", "lab_results", "tcm_look", "tcm_listen", "tcm_inquiry", "tcm_palpation", "tcm_calculation"]:
                return False
            
            # 验证证明内容（简化实现）
            return self._verify_proof_content(proof)
            
        except Exception as e:
            logger.error(f"零知识证明验证失败: {e}")
            return False
    
    def _generate_proof(
        self,
        data_type: str,
        health_data: Dict[str, Any],
        validation_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成证明内容"""
        # 简化的证明生成逻辑
        proof_data = {
            "data_type": data_type,
            "validation_result": self._validate_health_data(data_type, health_data, validation_params),
            "proof_id": secrets.token_hex(16),
            "algorithm": "simplified_zk",
            "version": "1.0"
        }
        
        # 添加数字签名
        signature = self.crypto_manager.sign_data(proof_data)
        proof_data["signature"] = signature
        
        return proof_data
    
    def _extract_public_inputs(self, data_type: str, validation_params: Dict[str, Any]) -> Dict[str, Any]:
        """提取公共输入"""
        public_inputs = {
            "data_type": data_type,
            "validation_criteria": validation_params,
            "timestamp": datetime.now().isoformat()
        }
        
        # 根据数据类型添加特定的公共输入
        if data_type == "vital_signs":
            public_inputs.update({
                "bp_range": validation_params.get("bp_range", [70, 200]),
                "hr_range": validation_params.get("hr_range", [40, 200])
            })
        elif data_type == "lab_results":
            public_inputs.update({
                "glucose_range": validation_params.get("glucose_range", [70, 200]),
                "cholesterol_range": validation_params.get("cholesterol_range", [100, 300])
            })
        
        return public_inputs
    
    def _generate_verification_key(self, data_type: str) -> Dict[str, Any]:
        """生成验证密钥"""
        return {
            "key_id": f"{data_type}_vk_{secrets.token_hex(8)}",
            "algorithm": "simplified_zk",
            "version": "1.0",
            "data_type": data_type,
            "created_at": datetime.now().isoformat()
        }
    
    def _validate_health_data(
        self,
        data_type: str,
        health_data: Dict[str, Any],
        validation_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """验证健康数据"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            if data_type == "vital_signs":
                validation_result = self._validate_vital_signs(health_data, validation_params)
            elif data_type == "lab_results":
                validation_result = self._validate_lab_results(health_data, validation_params)
            elif data_type.startswith("tcm_"):
                validation_result = self._validate_tcm_data(data_type, health_data, validation_params)
            
        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"验证过程出错: {str(e)}")
        
        return validation_result
    
    def _validate_vital_signs(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """验证生命体征数据"""
        result = {"valid": True, "errors": [], "warnings": []}
        
        # 血压验证
        if "systolic_bp" in data and "diastolic_bp" in data:
            systolic = data["systolic_bp"]
            diastolic = data["diastolic_bp"]
            
            if not (70 <= systolic <= 250):
                result["errors"].append("收缩压超出正常范围")
                result["valid"] = False
            
            if not (40 <= diastolic <= 150):
                result["errors"].append("舒张压超出正常范围")
                result["valid"] = False
            
            if systolic <= diastolic:
                result["errors"].append("收缩压必须大于舒张压")
                result["valid"] = False
        
        # 心率验证
        if "heart_rate" in data:
            hr = data["heart_rate"]
            if not (30 <= hr <= 220):
                result["errors"].append("心率超出正常范围")
                result["valid"] = False
        
        return result
    
    def _validate_lab_results(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """验证检验结果数据"""
        result = {"valid": True, "errors": [], "warnings": []}
        
        # 血糖验证
        if "glucose" in data:
            glucose = data["glucose"]
            if not (30 <= glucose <= 600):
                result["errors"].append("血糖值超出正常范围")
                result["valid"] = False
        
        # 胆固醇验证
        if "cholesterol_total" in data:
            cholesterol = data["cholesterol_total"]
            if not (100 <= cholesterol <= 500):
                result["warnings"].append("总胆固醇值需要关注")
        
        return result
    
    def _validate_tcm_data(self, data_type: str, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """验证中医数据"""
        result = {"valid": True, "errors": [], "warnings": []}
        
        # 基本数据完整性检查
        if not data:
            result["errors"].append("中医数据不能为空")
            result["valid"] = False
            return result
        
        # 根据诊断类型进行特定验证
        if data_type == "tcm_look":
            required_fields = ["face_color", "tongue_color"]
        elif data_type == "tcm_listen":
            required_fields = ["voice_strength", "breathing_sound"]
        elif data_type == "tcm_inquiry":
            required_fields = ["chief_complaint"]
        elif data_type == "tcm_palpation":
            required_fields = ["pulse_position", "pulse_rate"]
        elif data_type == "tcm_calculation":
            required_fields = ["birth_year", "birth_month"]
        else:
            required_fields = []
        
        # 检查必需字段
        for field in required_fields:
            if field not in data or not data[field]:
                result["warnings"].append(f"缺少重要字段: {field}")
        
        return result
    
    def _verify_proof_content(self, proof: HealthDataProof) -> bool:
        """验证证明内容"""
        try:
            # 验证数字签名
            proof_data = proof.proof.copy()
            signature = proof_data.pop("signature", None)
            
            if not signature:
                return False
            
            return self.crypto_manager.verify_signature(proof_data, signature)
            
        except Exception as e:
            logger.error(f"证明内容验证失败: {e}")
            return False


# 全局实例
crypto_manager = CryptoManager()
hash_manager = HashManager()
zk_proof_manager = ZKProofManager()


def get_crypto_manager() -> CryptoManager:
    """获取加密管理器"""
    return crypto_manager


def get_hash_manager() -> HashManager:
    """获取哈希管理器"""
    return hash_manager


def get_zk_proof_manager() -> ZKProofManager:
    """获取零知识证明管理器"""
    return zk_proof_manager


# 便捷函数
def encrypt_health_data(data: Dict[str, Any]) -> EncryptedData:
    """加密健康数据"""
    return crypto_manager.encrypt_data(data)


def decrypt_health_data(encrypted_data: EncryptedData) -> Dict[str, Any]:
    """解密健康数据"""
    return crypto_manager.decrypt_data(encrypted_data)


def calculate_data_hash(data: Dict[str, Any]) -> str:
    """计算数据哈希"""
    return hash_manager.calculate_hash(data)


def generate_health_proof(
    data_type: str,
    health_data: Dict[str, Any],
    validation_params: Dict[str, Any]
) -> HealthDataProof:
    """生成健康数据零知识证明"""
    return zk_proof_manager.generate_health_data_proof(data_type, health_data, validation_params)


def verify_health_proof(proof: HealthDataProof) -> bool:
    """验证健康数据零知识证明"""
    return zk_proof_manager.verify_health_data_proof(proof) 