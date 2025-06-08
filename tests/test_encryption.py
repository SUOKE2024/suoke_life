"""
test_encryption - 索克生活项目模块
"""

from suoke_blockchain_service.encryption import EncryptionService
from suoke_blockchain_service.exceptions import EncryptionError
from unittest.mock import patch, MagicMock
import pytest

"""
加密服务测试模块

测试数据加密和解密功能。
"""




class TestEncryptionService:
    """加密服务测试类"""

    @pytest.fixture
    def encryption_service(self):
        """创建加密服务实例"""
        return EncryptionService()

    @pytest.mark.asyncio
    async def test_encrypt_data_success(self, encryption_service):
        """测试成功加密数据"""
        test_data = "这是测试数据"

        encrypted_data, encryption_key = await encryption_service.encrypt_data(test_data)

        assert isinstance(encrypted_data, bytes)
        assert isinstance(encryption_key, str)
        assert len(encrypted_data) > 0
        assert len(encryption_key) > 0

    @pytest.mark.asyncio
    async def test_decrypt_data_success(self, encryption_service):
        """测试成功解密数据"""
        test_data = "这是测试数据"

        # 先加密
        encrypted_data, encryption_key = await encryption_service.encrypt_data(test_data)

        # 再解密
        decrypted_data = await encryption_service.decrypt_data(encrypted_data, encryption_key)

        assert decrypted_data == test_data

    @pytest.mark.asyncio
    async def test_encrypt_empty_data(self, encryption_service):
        """测试加密空数据"""
        with pytest.raises(EncryptionError, match="数据不能为空"):
            await encryption_service.encrypt_data("")

    @pytest.mark.asyncio
    async def test_decrypt_with_wrong_key(self, encryption_service):
        """测试使用错误密钥解密"""
        test_data = "这是测试数据"

        # 加密数据
        encrypted_data, _ = await encryption_service.encrypt_data(test_data)

        # 使用错误的密钥解密
        wrong_key = "wrong_key"
        with pytest.raises(EncryptionError, match="解密失败"):
            await encryption_service.decrypt_data(encrypted_data, wrong_key)

    @pytest.mark.asyncio
    async def test_decrypt_invalid_data(self, encryption_service):
        """测试解密无效数据"""
        invalid_data = b"invalid_encrypted_data"
        encryption_key = "test_key"

        with pytest.raises(EncryptionError, match="解密失败"):
            await encryption_service.decrypt_data(invalid_data, encryption_key)

    @pytest.mark.asyncio
    async def test_generate_key(self, encryption_service):
        """测试生成加密密钥"""
        key1 = encryption_service._generate_key()
        key2 = encryption_service._generate_key()

        assert isinstance(key1, str)
        assert isinstance(key2, str)
        assert len(key1) > 0
        assert len(key2) > 0
        assert key1 != key2  # 每次生成的密钥应该不同

    @pytest.mark.asyncio
    async def test_derive_key_from_password(self, encryption_service):
        """测试从密码派生密钥"""
        password = "test_password"
        salt = b"test_salt_16byte"

        key1 = encryption_service._derive_key_from_password(password, salt)
        key2 = encryption_service._derive_key_from_password(password, salt)

        assert key1 == key2  # 相同密码和盐应该生成相同密钥
        assert len(key1) == 32  # AES-256需要32字节密钥

    @pytest.mark.asyncio
    async def test_encrypt_large_data(self, encryption_service):
        """测试加密大数据"""
        # 创建1MB的测试数据
        large_data = "x" * (1024 * 1024)

        encrypted_data, encryption_key = await encryption_service.encrypt_data(large_data)
        decrypted_data = await encryption_service.decrypt_data(encrypted_data, encryption_key)

        assert decrypted_data == large_data

    @pytest.mark.asyncio
    async def test_encrypt_unicode_data(self, encryption_service):
        """测试加密Unicode数据"""
        unicode_data = "测试数据 🔒 encryption test 中文"

        encrypted_data, encryption_key = await encryption_service.encrypt_data(unicode_data)
        decrypted_data = await encryption_service.decrypt_data(encrypted_data, encryption_key)

        assert decrypted_data == unicode_data

    @pytest.mark.asyncio
    async def test_encryption_deterministic(self, encryption_service):
        """测试加密的确定性（相同数据每次加密结果应该不同）"""
        test_data = "这是测试数据"

        encrypted1, key1 = await encryption_service.encrypt_data(test_data)
        encrypted2, key2 = await encryption_service.encrypt_data(test_data)

        # 每次加密应该产生不同的结果（因为使用随机IV）
        assert encrypted1 != encrypted2
        assert key1 != key2

        # 但解密后应该得到相同的原始数据
        decrypted1 = await encryption_service.decrypt_data(encrypted1, key1)
        decrypted2 = await encryption_service.decrypt_data(encrypted2, key2)

        assert decrypted1 == test_data
        assert decrypted2 == test_data 