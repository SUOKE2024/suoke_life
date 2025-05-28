"""
配置模块测试

测试现代化的配置管理功能。
"""

import pytest
from pydantic import ValidationError

from suoke_blockchain_service.config import Settings


def test_settings_creation():
    """测试设置创建"""
    settings = Settings()
    
    # 验证基本属性
    assert settings.app_name == "SuoKe Blockchain Service"
    assert settings.app_version == "0.1.0"
    assert settings.debug is False
    assert settings.environment == "development"


def test_database_settings():
    """测试数据库设置"""
    settings = Settings()
    
    # 验证数据库配置
    assert settings.database.host == "localhost"
    assert settings.database.port == 5432
    assert settings.database.user == "postgres"
    assert settings.database.database == "blockchain_service"
    assert settings.database.pool_size == 10


def test_redis_settings():
    """测试 Redis 设置"""
    settings = Settings()
    
    # 验证 Redis 配置
    assert settings.redis.host == "localhost"
    assert settings.redis.port == 6379
    assert settings.redis.database == 0
    assert settings.redis.max_connections == 20


def test_blockchain_settings():
    """测试区块链设置"""
    settings = Settings()
    
    # 验证区块链配置
    assert settings.blockchain.eth_node_url == "http://localhost:8545"
    assert settings.blockchain.chain_id == 1337
    assert settings.blockchain.gas_limit == 6000000


def test_grpc_settings():
    """测试 gRPC 设置"""
    settings = Settings()
    
    # 验证 gRPC 配置
    assert settings.grpc.host == "0.0.0.0"
    assert settings.grpc.port == 50055
    assert settings.grpc.max_workers == 10


def test_security_settings():
    """测试安全设置"""
    settings = Settings()
    
    # 验证安全配置
    assert len(settings.security.jwt_secret_key) > 0
    assert settings.security.jwt_algorithm == "HS256"
    assert settings.security.jwt_expire_minutes == 30


def test_monitoring_settings():
    """测试监控设置"""
    settings = Settings()
    
    # 验证监控配置
    assert settings.monitoring.enable_metrics is True
    assert settings.monitoring.enable_tracing is True
    assert settings.monitoring.log_level == "INFO"


def test_invalid_port():
    """测试无效端口配置"""
    with pytest.raises(ValidationError):
        Settings(database__port=99999)  # 端口超出范围


def test_invalid_log_level():
    """测试无效日志级别"""
    with pytest.raises(ValidationError):
        Settings(monitoring__log_level="INVALID")


def test_environment_override():
    """测试环境变量覆盖"""
    import os
    
    # 临时设置环境变量
    os.environ["APP_NAME"] = "Test Service"
    os.environ["DEBUG"] = "true"
    
    try:
        settings = Settings()
        assert settings.app_name == "Test Service"
        assert settings.debug is True
    finally:
        # 清理环境变量
        os.environ.pop("APP_NAME", None)
        os.environ.pop("DEBUG", None) 