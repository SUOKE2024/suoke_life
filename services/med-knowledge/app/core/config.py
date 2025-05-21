import os
from functools import lru_cache
from typing import Any, Dict, List, Optional

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings


class ServerSettings(BaseSettings):
    port: int = 8080
    host: str = "0.0.0.0"
    timeout: int = 30  # 请求超时时间（秒）
    debug: bool = False  # 开发环境开启调试模式
    max_request_size: int = 10485760  # 10MB
    allowed_origins: List[str] = ["*"]


class DatabaseSettings(BaseSettings):
    uri: str = Field(..., env="NEO4J_URI")
    username: str = Field(..., env="NEO4J_USERNAME")
    password: str = Field(..., env="NEO4J_PASSWORD")
    max_connections: int = 50
    connection_timeout: int = 5  # 连接超时时间（秒）
    retry_max_attempts: int = 3
    retry_backoff: str = "exponential"  # 指数退避策略


class LoggingSettings(BaseSettings):
    level: str = "info"  # debug, info, warning, error, critical
    format: str = "json"  # json, text
    output: str = "stdout"  # stdout, file
    file_path: str = "/var/log/med-knowledge/app.log"


class JwtSettings(BaseSettings):
    secret: str = Field(..., env="JWT_SECRET")
    expiry: int = 86400  # 24小时过期（秒）


class ApiKeySettings(BaseSettings):
    name: str
    key: str
    roles: List[str]


class SecuritySettings(BaseSettings):
    jwt: JwtSettings
    api_keys: List[ApiKeySettings] = []


class RedisSettings(BaseSettings):
    enabled: bool = True
    host: str = "redis"
    port: int = 6379
    password: str = ""
    db: int = 0
    ttl: int = 3600  # 默认缓存过期时间（秒）


class CacheSettings(BaseSettings):
    redis: RedisSettings


class JaegerSettings(BaseSettings):
    host: str = "jaeger"
    port: int = 6831
    service_name: str = "med-knowledge"


class TracingSettings(BaseSettings):
    enabled: bool = True
    jaeger: JaegerSettings


class PrometheusSettings(BaseSettings):
    port: int = 9090
    path: str = "/metrics"


class MetricsSettings(BaseSettings):
    enabled: bool = True
    prometheus: PrometheusSettings


class DataSourceSettings(BaseSettings):
    name: str
    path: str


class ScheduleSettings(BaseSettings):
    enabled: bool = False
    cron: str = "0 0 * * 0"  # 每周日0点运行


class DataImportSettings(BaseSettings):
    sources: List[DataSourceSettings] = []
    schedule: ScheduleSettings


class ServiceSettings(BaseSettings):
    host: str
    port: int
    timeout: int


class ServiceDependencies(BaseSettings):
    rag: ServiceSettings
    xiaoai: ServiceSettings


class Settings(BaseSettings):
    server: ServerSettings
    database: DatabaseSettings
    logging: LoggingSettings
    security: Optional[SecuritySettings] = None
    cache: Optional[CacheSettings] = None
    tracing: Optional[TracingSettings] = None
    metrics: Optional[MetricsSettings] = None
    data_import: Optional[DataImportSettings] = None
    services: Optional[ServiceDependencies] = None


@lru_cache()
def load_config(config_path: str = None) -> Settings:
    """加载配置文件"""
    if not config_path:
        config_path = os.environ.get("CONFIG_PATH", "config/config.yaml")

    with open(config_path, "r") as f:
        config_data = yaml.safe_load(f)

    # 从环境变量覆盖敏感配置
    if "database" in config_data:
        if os.environ.get("NEO4J_URI"):
            config_data["database"]["neo4j"]["uri"] = os.environ.get("NEO4J_URI")
        if os.environ.get("NEO4J_USERNAME"):
            config_data["database"]["neo4j"]["username"] = os.environ.get("NEO4J_USERNAME")
        if os.environ.get("NEO4J_PASSWORD"):
            config_data["database"]["neo4j"]["password"] = os.environ.get("NEO4J_PASSWORD")

    if "security" in config_data and "jwt" in config_data["security"]:
        if os.environ.get("JWT_SECRET"):
            config_data["security"]["jwt"]["secret"] = os.environ.get("JWT_SECRET")

    return Settings(**config_data)


@lru_cache()
def get_settings() -> Settings:
    """获取应用配置单例"""
    return load_config()