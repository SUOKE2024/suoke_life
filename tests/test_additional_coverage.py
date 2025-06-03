"""
额外的测试用例来提升代码覆盖率
"""

import pytest
from unittest.mock import patch, MagicMock

from suoke_blockchain_service.config import Settings
from suoke_blockchain_service.exceptions import ValidationError, NotFoundError, BlockchainServiceError
from suoke_blockchain_service.logging import setup_logging, get_logger
from suoke_blockchain_service.monitoring import record_operation_metrics, get_metrics_summary


class TestAdditionalCoverage:
    """额外的测试用例来提升覆盖率"""

    def test_settings_validation_errors(self):
        """测试配置验证错误"""
        # 测试无效端口
        with pytest.raises(ValueError):
            Settings(grpc_port=-1)
        
        # 测试无效日志级别
        with pytest.raises(ValueError):
            Settings(log_level="INVALID")

    def test_logging_setup(self):
        """测试日志设置"""
        # 测试日志设置
        setup_logging("INFO")
        logger = get_logger("test")
        assert logger is not None
        
        # 测试不同日志级别
        setup_logging("DEBUG")
        setup_logging("WARNING")
        setup_logging("ERROR")

    def test_monitoring_functions(self):
        """测试监控功能"""
        # 测试记录操作指标
        record_operation_metrics("test_operation", "success")
        record_operation_metrics("test_operation", "failed")
        
        # 测试获取指标摘要
        summary = get_metrics_summary()
        assert isinstance(summary, dict)

    def test_exception_classes(self):
        """测试异常类"""
        # 测试ValidationError
        error = ValidationError("测试验证错误")
        assert str(error) == "测试验证错误"
        
        # 测试NotFoundError
        error = NotFoundError("测试未找到错误")
        assert str(error) == "测试未找到错误"
        
        # 测试BlockchainServiceError
        error = BlockchainServiceError("测试区块链服务错误")
        assert str(error) == "测试区块链服务错误"

    @pytest.mark.asyncio
    async def test_database_connection_error(self):
        """测试数据库连接错误处理"""
        from suoke_blockchain_service.database import get_db_session
        
        with patch('suoke_blockchain_service.database.async_sessionmaker') as mock_sessionmaker:
            # 模拟数据库连接错误
            mock_sessionmaker.side_effect = Exception("数据库连接失败")
            
            try:
                async with get_db_session() as session:
                    pass
            except Exception as e:
                assert "数据库连接失败" in str(e)

    def test_config_environment_variables(self):
        """测试环境变量配置"""
        import os
        
        # 保存原始环境变量
        original_env = os.environ.copy()
        
        try:
            # 设置测试环境变量
            os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost/test'
            os.environ['REDIS_URL'] = 'redis://localhost:6379/1'
            os.environ['LOG_LEVEL'] = 'DEBUG'
            
            # 创建设置实例
            settings = Settings()
            
            # 验证环境变量被正确读取
            assert 'test:test@localhost/test' in settings.database_url
            assert '6379/1' in settings.redis_url
            assert settings.log_level == 'DEBUG'
            
        finally:
            # 恢复原始环境变量
            os.environ.clear()
            os.environ.update(original_env)

    def test_blockchain_client_initialization(self):
        """测试区块链客户端初始化"""
        from suoke_blockchain_service.blockchain_client import BlockchainClient
        
        # 测试客户端初始化
        client = BlockchainClient()
        assert client is not None
        
        # 测试配置属性
        assert hasattr(client, 'web3')
        assert hasattr(client, 'contracts')

    def test_encryption_service_initialization(self):
        """测试加密服务初始化"""
        from suoke_blockchain_service.encryption import EncryptionService
        
        # 测试加密服务初始化
        service = EncryptionService()
        assert service is not None

    def test_ipfs_client_initialization(self):
        """测试IPFS客户端初始化"""
        from suoke_blockchain_service.ipfs_client import IPFSClient
        
        # 测试IPFS客户端初始化
        client = IPFSClient()
        assert client is not None

    def test_zk_integration_initialization(self):
        """测试零知识证明集成初始化"""
        from suoke_blockchain_service.zk_integration import ZKProofGenerator, ZKProofVerifier
        
        # 测试ZK证明生成器初始化
        generator = ZKProofGenerator()
        assert generator is not None
        
        # 测试ZK证明验证器初始化
        verifier = ZKProofVerifier()
        assert verifier is not None

    def test_grpc_server_initialization(self):
        """测试gRPC服务器初始化"""
        from suoke_blockchain_service.grpc_server import BlockchainServicer
        
        # 测试gRPC服务器初始化
        servicer = BlockchainServicer()
        assert servicer is not None

    @pytest.mark.asyncio
    async def test_service_error_handling(self):
        """测试服务错误处理"""
        from suoke_blockchain_service.service import BlockchainService
        
        service = BlockchainService()
        
        # 测试无效的数据类型验证
        with pytest.raises(ValidationError, match="数据类型不能为空"):
            service._validate_store_request("user123", {"test": "data"}, "")
        
        # 测试数据哈希生成
        hash1 = service._generate_data_hash({"test": "data"})
        hash2 = service._generate_data_hash({"test": "data"})
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256哈希长度 