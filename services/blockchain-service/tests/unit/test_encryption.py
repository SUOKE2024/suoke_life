"""
加密服务单元测试
"""

import pytest
from cryptography.fernet import InvalidToken

from blockchain_service.services.encryption_service import EncryptionService
from blockchain_service.core.exceptions import CryptographyError


class TestEncryptionService:
    """加密服务测试"""
    
    @pytest.mark.asyncio
    async def test_encrypt_decrypt_string(self, encryption_service):
        """测试字符串加密解密"""
        original_data = "Hello, World!"
        
        # 加密
        encrypted_data, password = await encryption_service.encrypt_data(original_data)
        assert encrypted_data != original_data.encode()
        assert isinstance(encrypted_data, bytes)
        assert isinstance(password, str)
        
        # 解密
        decrypted_data = await encryption_service.decrypt_data(encrypted_data, password)
        assert decrypted_data == original_data
    
    @pytest.mark.asyncio
    async def test_encrypt_decrypt_with_password(self, encryption_service):
        """测试使用指定密码加密解密"""
        original_data = "Test data with password"
        password = "my_secret_password"
        
        # 加密
        encrypted_data, returned_password = await encryption_service.encrypt_data(original_data, password)
        assert encrypted_data != original_data.encode()
        assert returned_password == password
        
        # 解密
        decrypted_data = await encryption_service.decrypt_data(encrypted_data, password)
        assert decrypted_data == original_data
    
    @pytest.mark.asyncio
    async def test_encrypt_empty_data(self, encryption_service):
        """测试空数据加密"""
        # 空字符串应该可以加密
        empty_data = ""
        encrypted_data, password = await encryption_service.encrypt_data(empty_data)
        decrypted_data = await encryption_service.decrypt_data(encrypted_data, password)
        assert decrypted_data == empty_data
    
    @pytest.mark.asyncio
    async def test_decrypt_invalid_token(self, encryption_service):
        """测试解密无效令牌"""
        invalid_data = b"invalid_encrypted_data"
        password = "test_password"
        
        with pytest.raises(CryptographyError, match="数据解密失败"):
            await encryption_service.decrypt_data(invalid_data, password)
    
    def test_generate_key(self, encryption_service):
        """测试密钥生成"""
        key1 = encryption_service.generate_key()
        key2 = encryption_service.generate_key()
        
        assert key1 != key2
        assert isinstance(key1, str)
        assert isinstance(key2, str)
        assert len(key1) > 0
        assert len(key2) > 0
    
    @pytest.mark.asyncio
    async def test_different_instances_different_salts(self):
        """测试不同实例使用不同盐值"""
        service1 = EncryptionService()
        service2 = EncryptionService()
        
        # 不同实例应该有不同的盐值
        assert service1.get_salt() != service2.get_salt()
        
        data = "test data"
        password = "same_password"
        
        encrypted1, _ = await service1.encrypt_data(data, password)
        encrypted2, _ = await service2.encrypt_data(data, password)
        
        # 相同密码但不同盐值应该产生不同的加密结果
        assert encrypted1 != encrypted2
        
        # 各自解密应该成功
        decrypted1 = await service1.decrypt_data(encrypted1, password)
        decrypted2 = await service2.decrypt_data(encrypted2, password)
        
        assert decrypted1 == data
        assert decrypted2 == data
    
    @pytest.mark.asyncio
    async def test_encrypt_large_data(self, encryption_service):
        """测试大数据加密"""
        # 创建大量数据
        large_data = "x" * 10000
        
        encrypted_data, password = await encryption_service.encrypt_data(large_data)
        decrypted_data = await encryption_service.decrypt_data(encrypted_data, password)
        
        assert decrypted_data == large_data
    
    @pytest.mark.asyncio
    async def test_encrypt_unicode_data(self, encryption_service):
        """测试Unicode数据加密"""
        unicode_data = "测试数据 🔐 Тест данные"
        
        encrypted_data, password = await encryption_service.encrypt_data(unicode_data)
        decrypted_data = await encryption_service.decrypt_data(encrypted_data, password)
        
        assert decrypted_data == unicode_data
    
    def test_get_salt(self, encryption_service):
        """测试获取盐值"""
        salt = encryption_service.get_salt()
        assert isinstance(salt, bytes)
        assert len(salt) == 16  # 默认盐值长度
    
    @pytest.mark.asyncio
    async def test_custom_salt(self):
        """测试自定义盐值"""
        custom_salt = b"custom_salt_1234"
        service = EncryptionService(salt=custom_salt)
        
        assert service.get_salt() == custom_salt
        
        # 使用自定义盐值加密解密
        data = "test with custom salt"
        password = "test_password"
        
        encrypted_data, _ = await service.encrypt_data(data, password)
        decrypted_data = await service.decrypt_data(encrypted_data, password)
        
        assert decrypted_data == data