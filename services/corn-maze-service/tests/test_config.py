"""
配置模块测试
"""

from pydantic import ValidationError
import pytest

from corn_maze_service.config import Settings


class TestSettings:
    """设置类测试"""

    def test_default_settings(self):
        """测试默认设置"""
        settings = Settings()

        assert settings.app_name == "Corn Maze Service"
        assert settings.app_version == "0.2.0"
        assert settings.environment == "development"
        assert not settings.debug

        # 测试数据库配置
        assert settings.database.url == "sqlite:///./data/corn_maze.db"
        assert not settings.database.echo
        assert settings.database.pool_size == 10

        # 测试 gRPC 配置
        assert settings.grpc.host == "0.0.0.0"
        assert settings.grpc.port == 50057
        assert settings.grpc.max_workers == 10

        # 测试 HTTP 配置
        assert settings.http.host == "0.0.0.0"
        assert settings.http.port == 51057
        assert not settings.http.reload

    def test_environment_validation(self):
        """测试环境验证"""
        # 有效环境
        for env in ["development", "testing", "staging", "production"]:
            settings = Settings(environment=env)
            assert settings.environment == env

        # 无效环境
        with pytest.raises(ValidationError):
            Settings(environment="invalid")

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
