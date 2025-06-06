"""
encryption - 索克生活项目模块
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import bcrypt
import hashlib
import secrets

#!/usr/bin/env python3
"""
通用安全组件 - 加密和密码处理
"""




class EncryptionService:
    """加密服务"""

    def __init__(self, master_key: str | None = None):
        """
        初始化加密服务

        Args:
            master_key: 主密钥，如果不提供则自动生成
        """
        if master_key:
            self.master_key = master_key.encode()
        else:
            self.master_key = Fernet.generate_key()

        self.cipher = Fernet(self.master_key)

    def encrypt(self, data: str) -> str:
        """
        加密数据

        Args:
            data: 要加密的数据

        Returns:
            str: 加密后的数据（base64编码）
        """
        encrypted = self.cipher.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """
        解密数据

        Args:
            encrypted_data: 加密的数据（base64编码）

        Returns:
            str: 解密后的数据
        """
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = self.cipher.decrypt(encrypted_bytes)
        return decrypted.decode()

    @staticmethod
    def generate_key() -> str:
        """生成新的加密密钥"""
        return Fernet.generate_key().decode()

    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        """
        从密码派生密钥

        Args:
            password: 密码
            salt: 盐值

        Returns:
            bytes: 派生的密钥
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key


def hash_password(password: str) -> str:
    """
    哈希密码

    Args:
        password: 明文密码

    Returns:
        str: 哈希后的密码
    """
    # 使用bcrypt进行密码哈希
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """
    验证密码

    Args:
        password: 明文密码
        hashed_password: 哈希后的密码

    Returns:
        bool: 密码是否匹配
    """
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def generate_secure_token(length: int = 32) -> str:
    """
    生成安全令牌

    Args:
        length: 令牌长度

    Returns:
        str: 安全令牌
    """
    return secrets.token_urlsafe(length)


def generate_api_key() -> str:
    """生成API密钥"""
    return f"sk_{secrets.token_urlsafe(32)}"


def hash_data(data: str, algorithm: str = "sha256") -> str:
    """
    哈希数据

    Args:
        data: 要哈希的数据
        algorithm: 哈希算法

    Returns:
        str: 哈希值（十六进制）
    """
    if algorithm == "sha256":
        return hashlib.sha256(data.encode()).hexdigest()
    elif algorithm == "sha512":
        return hashlib.sha512(data.encode()).hexdigest()
    elif algorithm == "md5":
        return hashlib.md5(data.encode()).hexdigest()
    else:
        raise ValueError(f"不支持的哈希算法: {algorithm}")


def validate_password_strength(password: str) -> tuple[bool, list[str]]:
    """
    验证密码强度

    Args:
        password: 密码

    Returns:
        tuple: (是否符合要求, 不符合的原因列表)
    """
    errors = []

    if len(password) < 8:
        errors.append("密码长度至少8个字符")

    if not any(c.isupper() for c in password):
        errors.append("密码必须包含至少一个大写字母")

    if not any(c.islower() for c in password):
        errors.append("密码必须包含至少一个小写字母")

    if not any(c.isdigit() for c in password):
        errors.append("密码必须包含至少一个数字")

    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        errors.append("密码必须包含至少一个特殊字符")

    return len(errors) == 0, errors


# 全局加密服务实例
_encryption_service = None


def get_encryption_service(master_key: str | None = None) -> EncryptionService:
    """获取加密服务实例"""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService(master_key)
    return _encryption_service


# 便捷函数
def encrypt_data(data: str) -> str:
    """加密数据"""
    return get_encryption_service().encrypt(data)


def decrypt_data(encrypted_data: str) -> str:
    """解密数据"""
    return get_encryption_service().decrypt(encrypted_data)
