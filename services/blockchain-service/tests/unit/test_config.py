"""
配置模块单元测试
"""

import os
import pytest
from unittest.mock import patch

from blockchain_service.config.settings import Settings, get_settings


class TestSettings:
    """设置类测试"""
    
    def test_default_settings(self):
        """测试默认设置"""
        settings = Settings()
        
        assert settings.app_name == "SuoKe Blockchain Service"
        assert settings.app_version == "1.0.0"
        assert settings.debug is False
        assert settings.environment == "development"
    
    def test_environment_override(self):
        """测试环境变量覆盖"""
        with patch.dict(os.environ, {
            'APP_NAME': 'Test Service',
            'DEBUG': 'true',
            'ENVIRONMENT': 'test'
        }):
            settings = Settings()
            
            assert settings.app_name == "Test Service"
            assert settings.debug is True
            assert settings.environment == "test"
    
    def test_database_config(self):
        """测试数据库配置"""
        settings = Settings()
        
        assert settings.database.host == "localhost"
        assert settings.database.port == 5432
        assert settings.database.database == "blockchain_service"
        assert settings.database.user is not None
        assert len(settings.database.user) > 0
        assert settings.database.password == ""
    
    def test_redis_config(self):
        """测试 Redis 配置"""
        settings = Settings()
        
        assert settings.redis.host == "localhost"
        assert settings.redis.port == 6379
        assert settings.redis.database == 0
        assert settings.redis.password is None
    
    def test_blockchain_config(self):
        """测试区块链配置"""
        settings = Settings()
        
        assert settings.blockchain.eth_node_url == "http://localhost:8545"
        assert settings.blockchain.chain_id == 1337
        assert settings.blockchain.gas_limit == 6000000
        assert settings.blockchain.gas_price == 20000000000
    
    def test_security_config(self):
        """测试安全配置"""
        settings = Settings()
        
        assert settings.security.jwt_secret_key == "your-secret-key-change-in-production"
        assert settings.security.jwt_algorithm == "HS256"
        assert settings.security.jwt_expiration_hours == 24
    
    def test_ipfs_config(self):
        """测试 IPFS 配置"""
        settings = Settings()
        
        assert settings.ipfs.node_url == "http://localhost:5001"
        assert settings.ipfs.timeout == 30
        assert settings.ipfs.chunk_size == 1024 * 1024
    
    def test_monitoring_config(self):
        """测试监控配置"""
        settings = Settings()
        
        assert settings.monitoring.enable_metrics is True
        assert settings.monitoring.metrics_port == 9090
        assert settings.monitoring.log_level == "INFO"


class TestGetSettings:
    """获取设置函数测试"""
    
    def test_get_settings_singleton(self):
        """测试设置单例模式"""
        settings1 = get_settings()
        settings2 = get_settings()
        
        assert settings1 is settings2
    
    def test_get_settings_cache_clear(self):
        """测试设置缓存清理"""
        settings1 = get_settings()
        
        # 清理缓存
        get_settings.cache_clear()
        
        settings2 = get_settings()
        
        # 应该是不同的实例
        assert settings1 is not settings2
        # 但配置应该相同
        assert settings1.app_name == settings2.app_name