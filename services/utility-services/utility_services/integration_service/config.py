
"""
config - 索克生活项目模块
"""

from pathlib import Path

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings

"""
配置管理模块
"""




class Settings(BaseSettings):
    """应用配置"""

    # 应用基础配置
    app_name: str = Field(default = "integration - service", env = "APP_NAME")
    app_version: str = Field(default = "0.1.0", env = "APP_VERSION")
    debug: bool = Field(default = False, env = "DEBUG")
    host: str = Field(default = "0.0.0.0", env = "HOST")
    port: int = Field(default = 8090, env = "PORT")
    allowed_hosts: list[str] = Field(default = [" * "], env = "ALLOWED_HOSTS")

    # 数据库配置
    database_url: str = Field(
        default = "postgresql: / /postgres:password@localhost:5432 / integration_db",
        env = "DATABASE_URL"
    )

    # Redis 配置
    redis_host: str = Field(default = "localhost", env = "REDIS_HOST")
    redis_port: int = Field(default = 6379, env = "REDIS_PORT")
    redis_db: int = Field(default = 0, env = "REDIS_DB")
    redis_password: str | None = Field(default = None, env = "REDIS_PASSWORD")

    # 安全配置
    secret_key: str = Field(default = "your - secret - key - change - in - production", env = "SECRET_KEY")
    algorithm: str = Field(default = "HS256", env = "ALGORITHM")
    access_token_expire_minutes: int = Field(default = 30, env = "ACCESS_TOKEN_EXPIRE_MINUTES")

    # 日志配置
    log_level: str = Field(default = "INFO", env = "LOG_LEVEL")

    class Config:
        """TODO: 添加文档字符串"""
        env_file = ".env"
        case_sensitive = False


def load_config_from_yaml(config_path: str = "config / config.yaml") -> dict:
    """从 YAML 文件加载配置"""
    config_file = Path(config_path)
    if config_file.exists():
        with open(config_file, encoding = 'utf - 8') as f:
            return yaml.safe_load(f)
    return {}


# 全局配置实例
settings = Settings()

# 数据库连接池优化配置
DATABASE_POOL_CONFIG = {
    "pool_size": 20,           # 连接池大小
    "max_overflow": 30,        # 最大溢出连接数
    "pool_timeout": 30,        # 获取连接超时时间
    "pool_recycle": 3600,      # 连接回收时间
    "pool_pre_ping": True,     # 连接预检查
}
