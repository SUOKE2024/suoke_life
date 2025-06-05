"""
配置管理模块
"""

from pathlib import Path

import yaml
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置"""

    # 应用基础配置
    app_name: str = Field(default="integration-service", env="APP_NAME")
    app_version: str = Field(default="0.1.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8090, env="PORT")
    allowed_hosts: list[str] = Field(default=["*"], env="ALLOWED_HOSTS")

    # 数据库配置
    database_url: str = Field(
        default="postgresql://postgres:password@localhost:5432/integration_db",
        env="DATABASE_URL"
    )

    # Redis 配置
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_password: str | None = Field(default=None, env="REDIS_PASSWORD")

    # 安全配置
    secret_key: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # 日志配置
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        case_sensitive = False


def load_config_from_yaml(config_path: str = "config/config.yaml") -> dict:
    """从 YAML 文件加载配置"""
    config_file = Path(config_path)
    if config_file.exists():
        with open(config_file, encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}


# 全局配置实例
settings = Settings()
