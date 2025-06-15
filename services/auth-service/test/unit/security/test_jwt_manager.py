#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JWT密钥管理器单元测试
"""
import pytest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from internal.security.jwt_manager import JWTKeyManager, get_jwt_key_manager, reload_jwt_keys


class TestJWTKeyManager:
    """JWT密钥管理器测试类"""
    
    @pytest.fixture
    def mock_settings(self):
        """模拟配置"""
        settings = MagicMock()
        settings.jwt_private_key_path = None
        settings.jwt_public_key_path = None
        settings.jwt_private_key = None
        settings.jwt_public_key = None
        settings.jwt_algorithm = "RS256"
        settings.jwt_secret_key = "test_secret"
        return settings
    
    @pytest.fixture
    def sample_rsa_keys(self):
        """生成示例RSA密钥对"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        public_key = private_key.public_key()
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return {
            'private_key': private_key,
            'public_key': public_key,
            'private_pem': private_pem,
            'public_pem': public_pem
        }
    
    def test_init_with_file_paths(self, mock_settings, sample_rsa_keys):
        """测试从文件路径初始化"""
        mock_settings.jwt_private_key_path = "/path/to/private.pem"
        mock_settings.jwt_public_key_path = "/path/to/public.pem"
        
        with patch('internal.security.jwt_manager.get_settings', return_value=mock_settings), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', mock_open()) as mock_file:
            
            # 设置文件读取返回值
            mock_file.return_value.read.side_effect = [
                sample_rsa_keys['private_pem'],
                sample_rsa_keys['public_pem']
            ]
            
            manager = JWTKeyManager()
            
            assert manager._private_key is not None
            assert manager._public_key is not None
            assert mock_file.call_count == 2
    
    def test_init_with_config_content(self, mock_settings, sample_rsa_keys):
        """测试从配置内容初始化"""
        mock_settings.jwt_private_key = sample_rsa_keys['private_pem'].decode()
        mock_settings.jwt_public_key = sample_rsa_keys['public_pem'].decode()
        
        with patch('internal.security.jwt_manager.get_settings', return_value=mock_settings):
            manager = JWTKeyManager()
            
            assert manager._private_key is not None
            assert manager._public_key is not None
    
    def test_init_generate_new_keys(self, mock_settings):
        """测试生成新密钥对"""
        with patch('internal.security.jwt_manager.get_settings', return_value=mock_settings):
            manager = JWTKeyManager()
            
            assert manager._private_key is not None
            assert manager._public_key is not None
            assert manager._private_key_pem is not None
            assert manager._public_key_pem is not None
    
    def test_get_private_key_rs256(self, mock_settings, sample_rsa_keys):
        """测试获取RS256私钥"""
        mock_settings.jwt_algorithm = "RS256"
        mock_settings.jwt_private_key = sample_rsa_keys['private_pem'].decode()
        mock_settings.jwt_public_key = sample_rsa_keys['public_pem'].decode()
        
        with patch('internal.security.jwt_manager.get_settings', return_value=mock_settings):
            manager = JWTKeyManager()
            private_key = manager.get_private_key()
            
            assert isinstance(private_key, rsa.RSAPrivateKey)
    
    def test_get_private_key_hs256(self, mock_settings):
        """测试获取HS256密钥"""
        mock_settings.jwt_algorithm = "HS256"
        mock_settings.jwt_secret_key = "test_secret_key"
        
        with patch('internal.security.jwt_manager.get_settings', return_value=mock_settings):
            manager = JWTKeyManager()
            private_key = manager.get_private_key()
            
            assert private_key == "test_secret_key"
    
    def test_get_public_key_rs256(self, mock_settings, sample_rsa_keys):
        """测试获取RS256公钥"""
        mock_settings.jwt_algorithm = "RS256"
        mock_settings.jwt_private_key = sample_rsa_keys['private_pem'].decode()
        mock_settings.jwt_public_key = sample_rsa_keys['public_pem'].decode()
        
        with patch('internal.security.jwt_manager.get_settings', return_value=mock_settings):
            manager = JWTKeyManager()
            public_key = manager.get_public_key()
            
            assert isinstance(public_key, rsa.RSAPublicKey)
    
    def test_get_public_key_hs256(self, mock_settings):
        """测试获取HS256密钥"""
        mock_settings.jwt_algorithm = "HS256"
        mock_settings.jwt_secret_key = "test_secret_key"
        
        with patch('internal.security.jwt_manager.get_settings', return_value=mock_settings):
            manager = JWTKeyManager()
            public_key = manager.get_public_key()
            
            assert public_key == "test_secret_key"
    
    def test_get_private_key_pem(self, mock_settings, sample_rsa_keys):
        """测试获取PEM格式私钥"""
        mock_settings.jwt_private_key = sample_rsa_keys['private_pem'].decode()
        mock_settings.jwt_public_key = sample_rsa_keys['public_pem'].decode()
        
        with patch('internal.security.jwt_manager.get_settings', return_value=mock_settings):
            manager = JWTKeyManager()
            private_pem = manager.get_private_key_pem()
            
            assert private_pem is not None
            assert "BEGIN PRIVATE KEY" in private_pem
    
    def test_get_public_key_pem(self, mock_settings, sample_rsa_keys):
        """测试获取PEM格式公钥"""
        mock_settings.jwt_private_key = sample_rsa_keys['private_pem'].decode()
        mock_settings.jwt_public_key = sample_rsa_keys['public_pem'].decode()
        
        with patch('internal.security.jwt_manager.get_settings', return_value=mock_settings):
            manager = JWTKeyManager()
            public_pem = manager.get_public_key_pem()
            
            assert public_pem is not None
            assert "BEGIN PUBLIC KEY" in public_pem
    
    def test_save_keys_to_files(self, mock_settings):
        """测试保存密钥到文件"""
        with patch('internal.security.jwt_manager.get_settings', return_value=mock_settings), \
             patch('builtins.open', mock_open()) as mock_file:
            
            manager = JWTKeyManager()
            manager.save_keys_to_files("/path/to/private.pem", "/path/to/public.pem")
            
            assert mock_file.call_count == 2
    
    def test_load_keys_file_not_exists(self, mock_settings):
        """测试加载不存在的密钥文件"""
        mock_settings.jwt_private_key_path = "/nonexistent/private.pem"
        mock_settings.jwt_public_key_path = "/nonexistent/public.pem"
        
        with patch('internal.security.jwt_manager.get_settings', return_value=mock_settings), \
             patch('pathlib.Path.exists', return_value=False):
            
            # 应该回退到生成新密钥对
            manager = JWTKeyManager()
            
            assert manager._private_key is not None
            assert manager._public_key is not None
    
    def test_load_keys_invalid_format(self, mock_settings):
        """测试加载无效格式的密钥文件"""
        mock_settings.jwt_private_key_path = "/path/to/private.pem"
        mock_settings.jwt_public_key_path = "/path/to/public.pem"
        
        with patch('internal.security.jwt_manager.get_settings', return_value=mock_settings), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', mock_open()) as mock_file:
            
            # 设置无效的密钥内容
            mock_file.return_value.read.return_value = b"invalid key content"
            
            # 应该回退到生成新密钥对
            manager = JWTKeyManager()
            
            assert manager._private_key is not None
            assert manager._public_key is not None


class TestJWTKeyManagerSingleton:
    """JWT密钥管理器单例测试"""
    
    def test_get_jwt_key_manager_singleton(self):
        """测试单例模式"""
        with patch('internal.security.jwt_manager.JWTKeyManager') as mock_manager_class:
            mock_instance = MagicMock()
            mock_manager_class.return_value = mock_instance
            
            # 第一次调用
            manager1 = get_jwt_key_manager()
            
            # 第二次调用
            manager2 = get_jwt_key_manager()
            
            # 应该返回同一个实例
            assert manager1 is manager2
            assert mock_manager_class.call_count == 1
    
    def test_reload_jwt_keys(self):
        """测试重新加载密钥"""
        with patch('internal.security.jwt_manager.JWTKeyManager') as mock_manager_class:
            mock_instance1 = MagicMock()
            mock_instance2 = MagicMock()
            mock_manager_class.side_effect = [mock_instance1, mock_instance2]
            
            # 第一次获取
            manager1 = get_jwt_key_manager()
            
            # 重新加载
            reload_jwt_keys()
            
            # 再次获取，应该是新实例
            manager2 = get_jwt_key_manager()
            
            assert manager1 is not manager2
            assert mock_manager_class.call_count == 2


class TestJWTKeyManagerErrorHandling:
    """JWT密钥管理器错误处理测试"""
    
    def test_file_permission_error(self, mock_settings):
        """测试文件权限错误"""
        mock_settings.jwt_private_key_path = "/path/to/private.pem"
        mock_settings.jwt_public_key_path = "/path/to/public.pem"
        
        with patch('internal.security.jwt_manager.get_settings', return_value=mock_settings), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', side_effect=PermissionError("Permission denied")):
            
            # 应该回退到生成新密钥对
            manager = JWTKeyManager()
            
            assert manager._private_key is not None
            assert manager._public_key is not None
    
    def test_save_keys_permission_error(self, mock_settings):
        """测试保存密钥权限错误"""
        with patch('internal.security.jwt_manager.get_settings', return_value=mock_settings), \
             patch('builtins.open', side_effect=PermissionError("Permission denied")):
            
            manager = JWTKeyManager()
            
            with pytest.raises(PermissionError):
                manager.save_keys_to_files("/path/to/private.pem", "/path/to/public.pem")
    
    def test_key_generation_error(self, mock_settings):
        """测试密钥生成错误"""
        with patch('internal.security.jwt_manager.get_settings', return_value=mock_settings), \
             patch('cryptography.hazmat.primitives.asymmetric.rsa.generate_private_key', 
                   side_effect=Exception("Key generation failed")):
            
            with pytest.raises(Exception):
                JWTKeyManager() 