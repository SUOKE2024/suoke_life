"""
加密服务模块

提供数据加密和解密功能，支持多种加密算法。
"""

import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from ..core.exceptions import CryptographyError
from ..utils.logger import get_logger

logger = get_logger(__name__)


class EncryptionService:
    """加密服务"""

    def __init__(self, salt: bytes | None = None) -> None:
        """初始化加密服务

        Args:
            salt: 可选的盐值，如果不提供则生成随机盐值
        """
        self.salt = salt or os.urandom(16)

    async def encrypt_data(self, data: str, password: str | None = None) -> tuple[bytes, str]:
        """加密数据

        Args:
            data: 要加密的数据
            password: 可选的密码，如果不提供则生成随机密钥

        Returns:
            加密后的数据和密码的元组

        Raises:
            CryptographyError: 加密失败时抛出
        """
        try:
            # 生成密钥
            if password is None:
                key = Fernet.generate_key()
                password = key.decode()
            else:
                key = self._derive_key(password.encode())

            # 加密数据
            fernet = Fernet(key)
            encrypted_data = fernet.encrypt(data.encode('utf-8'))

            logger.info("数据加密成功", extra={"data_size": len(data)})
            return encrypted_data, password

        except Exception as e:
            logger.error("数据加密失败", extra={"error": str(e)})
            raise CryptographyError(f"数据加密失败: {str(e)}")

    async def decrypt_data(self, encrypted_data: bytes, password: str) -> str:
        """解密数据

        Args:
            encrypted_data: 加密的数据
            password: 解密密码

        Returns:
            解密后的数据

        Raises:
            CryptographyError: 解密失败时抛出
        """
        try:
            # 如果密码看起来像Fernet密钥，直接使用
            if len(password) == 44 and password.endswith('='):
                key = password.encode()
            else:
                # 否则派生密钥
                key = self._derive_key(password.encode())

            # 解密数据
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_data)

            logger.info("数据解密成功")
            return decrypted_data.decode('utf-8')

        except Exception as e:
            logger.error("数据解密失败", extra={"error": str(e)})
            raise CryptographyError(f"数据解密失败: {str(e)}")

    def _derive_key(self, password: bytes) -> bytes:
        """从密码派生密钥

        Args:
            password: 密码字节

        Returns:
            派生的密钥
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key

    def generate_key(self) -> str:
        """生成新的加密密钥

        Returns:
            Base64编码的密钥字符串
        """
        key = Fernet.generate_key()
        return base64.urlsafe_b64encode(key).decode()

    def get_salt(self) -> bytes:
        """获取当前使用的盐值

        Returns:
            盐值字节
        """
        return self.salt
