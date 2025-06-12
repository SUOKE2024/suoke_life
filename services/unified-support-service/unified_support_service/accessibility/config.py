"""
config - 索克生活项目模块
"""

from typing import Optional

from pydantic_settings import BaseSettings

"""
accessibility - service 配置管理
"""


class Settings(BaseSettings):
    """应用配置"""

    # 服务配置
    service_name: str = "accessibility - service"
    service_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    # 数据库配置
    database_url: Optional[str] = None

    # Redis配置
    redis_url: str = "redis: / /localhost:6379 / 0"

    # API配置
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # 安全配置
    secret_key: str = "your - secret - key - here"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30

    # 监控配置
    enable_metrics: bool = True
    metrics_port: int = 9090

    class Config:
        """TODO: 添加文档字符串"""

        env_file = ".env"
        case_sensitive = False


# 全局配置实例
settings = Settings()
