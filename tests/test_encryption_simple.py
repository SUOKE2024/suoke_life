"""
加密服务测试模块

测试数据加密和解密功能。
"""

import pytest
from unittest.mock import patch, MagicMock

from suoke_blockchain_service.encryption import EncryptionService
from suoke_blockchain_service.exceptions import EncryptionError


class TestEncryptionService:
    """加密服务测试类"""

    @pytest.fixture
    def encryption_service(self):
        """创建加密服务实例"""
        return EncryptionService()

    @pytest.mark.asyncio
    async def test_encrypt_data_success(self, encryption_service):
        """测试成功加密数据"""
        test_data = "test data for encryption"
        
        encrypted_data, encryption_key = await encryption_service.encrypt_data(test_data)
        
        assert encrypted_data is not None
        assert encryption_key is not None
        assert len(encryption_key) > 0

    @pytest.mark.asyncio
    async def test_decrypt_data_success(self, encryption_service):
        """测试成功解密数据"""
        test_data = "test data for decryption"
        
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
    async def test_decrypt_invalid_key(self, encryption_service):
        """测试使用无效密钥解密"""
        test_data = "test data"
        encrypted_data, _ = await encryption_service.encrypt_data(test_data)
        
        with pytest.raises(EncryptionError, match="解密失败"):
            await encryption_service.decrypt_data(encrypted_data, "invalid_key")

    @pytest.mark.asyncio
    async def test_generate_key(self, encryption_service):
        """测试生成加密密钥"""
        key1 = encryption_service.generate_key()
        key2 = encryption_service.generate_key()
        
        assert key1 != key2
        assert len(key1) > 0
        assert len(key2) > 0 