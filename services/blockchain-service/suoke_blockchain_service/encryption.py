"""
encryption - 索克生活项目模块
"""

from .exceptions import EncryptionError
from .logging import get_logger
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Tuple
import base64
import os

"""
加密服务模块

提供数据加密和解密功能。
"""



logger = get_logger(__name__)

class EncryptionService:
    """加密服务"""

    def __init__(self):
        self.salt = os.urandom(16)

    async def encrypt_data(self, data: str, password: str = None) -> Tuple[bytes, str]:
        """加密数据"""
        try:
            # 生成密钥
            if password is None:
                key = Fernet.generate_key()
                password = base64.urlsafe_b64encode(key).decode()
            else:
                key = self._derive_key(password.encode())

            # 加密数据
            fernet = Fernet(key)
            encrypted_data = fernet.encrypt(data.encode('utf-8'))

            logger.info("数据加密成功", data_size=len(data))
            return encrypted_data, password

        except Exception as e:
            logger.error("数据加密失败", error=str(e))
            raise EncryptionError(f"数据加密失败: {str(e)}")

    async def decrypt_data(self, encrypted_data: bytes, password: str) -> str:
        """解密数据"""
        try:
            # 派生密钥
            key = self._derive_key(password.encode())

            # 解密数据
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_data)

            logger.info("数据解密成功")
            return decrypted_data.decode('utf-8')

        except Exception as e:
            logger.error("数据解密失败", error=str(e))
            raise EncryptionError(f"数据解密失败: {str(e)}")

    def _derive_key(self, password: bytes) -> bytes:
        """从密码派生密钥"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key 