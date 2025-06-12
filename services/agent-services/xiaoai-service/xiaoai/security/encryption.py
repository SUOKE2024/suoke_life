"""
数据加密模块

提供敏感数据加密和解密功能
"""

import base64
import hashlib
import logging
import secrets
from typing import Optional, bytes, str

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from ..config.settings import get_settings

logger = logging.getLogger(__name__)


class EncryptionManager:
    """加密管理器"""

    def __init__(self):
        self.settings = get_settings()
        self._fernet = None

    @property
    def fernet(self) -> Fernet:
        """获取Fernet实例"""
        if self._fernet is None:
            key = self._derive_key(self.settings.encryption_key)
            self._fernet = Fernet(key)
        return self._fernet

    def _derive_key(self, password: str) -> bytes:
        """从密码派生密钥"""
        password_bytes = password.encode()
        salt = b'xiaoai_salt_2024'  # 在生产环境中应该使用随机盐

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return key

    def encrypt(self, data: str) -> str:
        """加密数据"""
        try:
            if not data:
                return data

            encrypted_data = self.fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()

        except Exception as e:
            logger.error(f"数据加密失败: {e}")
            raise

    def decrypt(self, encrypted_data: str) -> str:
        """解密数据"""
        try:
            if not encrypted_data:
                return encrypted_data

            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.fernet.decrypt(encrypted_bytes)
            return decrypted_data.decode()

        except Exception as e:
            logger.error(f"数据解密失败: {e}")
            raise

    def hash_data(self, data: str) -> str:
        """数据哈希"""
        return hashlib.sha256(data.encode()).hexdigest()

    def generate_token(self, length: int = 32) -> str:
        """生成随机令牌"""
        return secrets.token_urlsafe(length)

    def mask_sensitive_data(self, data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
        """掩码敏感数据"""
        if not data or len(data) <= visible_chars:
            return mask_char * len(data) if data else ""

        return data[:visible_chars] + mask_char * (len(data) - visible_chars)


class HealthDataEncryption:
    """健康数据专用加密"""

    def __init__(self, encryption_manager: EncryptionManager):
        self.encryption_manager = encryption_manager

    def encrypt_medical_record(self, record: dict) -> dict:
        """加密医疗记录"""
        sensitive_fields = [
            'patient_name',
            'id_number',
            'phone',
            'address',
            'medical_history',
            'diagnosis',
            'symptoms',
        ]

        encrypted_record = record.copy()

        for field in sensitive_fields:
            if field in encrypted_record and encrypted_record[field]:
                encrypted_record[field] = self.encryption_manager.encrypt(
                    str(encrypted_record[field])
                )

        return encrypted_record

    def decrypt_medical_record(self, encrypted_record: dict) -> dict:
        """解密医疗记录"""
        sensitive_fields = [
            'patient_name',
            'id_number',
            'phone',
            'address',
            'medical_history',
            'diagnosis',
            'symptoms',
        ]

        decrypted_record = encrypted_record.copy()

        for field in sensitive_fields:
            if field in decrypted_record and decrypted_record[field]:
                try:
                    decrypted_record[field] = self.encryption_manager.decrypt(
                        decrypted_record[field]
                    )
                except Exception as e:
                    logger.warning(f"解密字段 {field} 失败: {e}")
                    decrypted_record[field] = "[解密失败]"

        return decrypted_record

    def anonymize_data(self, data: dict) -> dict:
        """数据匿名化"""
        anonymized = data.copy()

        # 移除直接标识符
        identifiers = ['patient_name', 'id_number', 'phone', 'address', 'email']
        for identifier in identifiers:
            if identifier in anonymized:
                del anonymized[identifier]

        # 对准标识符进行处理
        if 'birth_date' in anonymized:
            # 只保留年份
            birth_date = anonymized['birth_date']
            if isinstance(birth_date, str) and len(birth_date) >= 4:
                anonymized['birth_year'] = birth_date[:4]
            del anonymized['birth_date']

        if 'age' in anonymized:
            # 年龄分组
            age = anonymized['age']
            if isinstance(age, (int, float)):
                if age < 18:
                    anonymized['age_group'] = '未成年'
                elif age < 30:
                    anonymized['age_group'] = '青年'
                elif age < 50:
                    anonymized['age_group'] = '中年'
                else:
                    anonymized['age_group'] = '老年'
            del anonymized['age']

        return anonymized


# 全局加密管理器实例
encryption_manager = EncryptionManager()
health_data_encryption = HealthDataEncryption(encryption_manager)
