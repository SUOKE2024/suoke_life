"""
配置测试模块

测试配置管理功能
"""

from pydantic import ValidationError
import pytest

from corn_maze_service.config.settings import Settings
from corn_maze_service.constants import (
    DEFAULT_GRPC_PORT,
    DEFAULT_HTTP_PORT,
    DEFAULT_MAX_WORKERS,
    DEFAULT_POOL_SIZE,
    TEST_GRPC_PORT,
)


class TestSettings:
    """测试设置类"""

    def test_default_settings(self):
        """测试默认设置"""
        settings = Settings()

        # 测试基本配置
        assert settings.app_name == "Corn Maze Service"
        assert settings.environment == "development"

        # 测试数据库配置
        assert settings.database.url == "sqlite:///./data/corn_maze.db"
        assert not settings.database.echo
        assert settings.database.pool_size == DEFAULT_POOL_SIZE

        # 测试 gRPC 配置
        assert settings.grpc.host == "0.0.0.0"
        assert settings.grpc.port == DEFAULT_GRPC_PORT
        assert settings.grpc.max_workers == DEFAULT_MAX_WORKERS

        # 测试 HTTP 配置
        assert settings.http.host == "0.0.0.0"
        assert settings.http.port == DEFAULT_HTTP_PORT
        assert not settings.http.reload

    def test_environment_override(self, monkeypatch):
        """测试环境变量覆盖"""
        # 设置环境变量
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("DATABASE__URL", "postgresql://test")
        monkeypatch.setenv("GRPC__PORT", str(TEST_GRPC_PORT))

        settings = Settings()

        assert settings.environment == "production"
        assert settings.database.url == "postgresql://test"
        assert settings.grpc.port == TEST_GRPC_PORT

    def test_validation(self):
        """测试配置验证"""
        # 测试无效环境
        with pytest.raises(ValueError):
            Settings(environment="invalid")

    def test_environment_validation(self):
        """测试环境验证"""
        # 有效环境
        for env in ["development", "testing", "staging", "production"]:
            settings = Settings(environment=env)
            assert settings.environment == env

    def test_log_level_validation(self):
        """测试日志级别验证"""
        # 有效日志级别
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            settings = Settings(monitoring={"log_level": level})
            assert settings.monitoring.log_level == level

        # 无效日志级别
        with pytest.raises(ValidationError):
            Settings(monitoring={"log_level": "INVALID"})

    def test_is_production(self):
        """测试生产环境检查"""
        settings = Settings(environment="production")
        assert settings.is_production()

        settings = Settings(environment="development")
        assert not settings.is_production()

    def test_is_development(self):
        """测试开发环境检查"""
        settings = Settings(environment="development")
        assert settings.is_development()

        settings = Settings(environment="production")
        assert not settings.is_development()

    def test_get_database_url(self):
        """测试获取数据库URL"""
        settings = Settings(database={"url": "postgresql://test"})
        assert settings.get_database_url() == "postgresql://test"

    def test_get_redis_url(self):
        """测试获取Redis URL"""
        settings = Settings(redis={"url": "redis://test:6379/1"})
        assert settings.get_redis_url() == "redis://test:6379/1"

    def test_log_config(self):
        """测试日志配置"""
        settings = Settings(monitoring={"log_level": "DEBUG"})
        log_config = settings.get_log_config()

        assert log_config["version"] == 1
        assert not log_config["disable_existing_loggers"]
        assert "formatters" in log_config
        assert "handlers" in log_config
        assert "loggers" in log_config

        # 检查日志级别
        assert log_config["root"]["level"] == "DEBUG"
        assert log_config["loggers"]["corn_maze_service"]["level"] == "DEBUG"
