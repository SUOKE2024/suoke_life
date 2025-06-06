"""
config - 索克生活项目模块
"""

            import json
from functools import lru_cache
from pydantic import Field, validator
from pydantic_settings import BaseSettings
from typing import Any
import os
import yaml




class ServerSettings(BaseSettings):
    """服务器配置"""

    port: int = Field(default=8080, env="PORT")
    host: str = Field(default="0.0.0.0", env="HOST")
    timeout: int = Field(default=30, env="SERVER_TIMEOUT")
    debug: bool = Field(default=False, env="DEBUG")
    max_request_size: int = Field(default=10485760, env="MAX_REQUEST_SIZE")  # 10MB
    allowed_origins: list[str] = Field(default=["*"], env="ALLOWED_ORIGINS")

    @validator("allowed_origins", pre=True)
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


class DatabaseSettings(BaseSettings):
    """数据库配置"""

    uri: str = Field(..., env="NEO4J_URI")
    username: str = Field(..., env="NEO4J_USERNAME")
    password: str = Field(..., env="NEO4J_PASSWORD")
    max_connections: int = Field(default=50, env="NEO4J_MAX_CONNECTIONS")
    connection_timeout: int = Field(default=5, env="NEO4J_CONNECTION_TIMEOUT")
    retry_max_attempts: int = Field(default=3, env="NEO4J_RETRY_MAX_ATTEMPTS")
    retry_backoff: str = Field(default="exponential", env="NEO4J_RETRY_BACKOFF")


class LoggingSettings(BaseSettings):
    """日志配置"""

    level: str = Field(default="info", env="LOG_LEVEL")
    format: str = Field(default="json", env="LOG_FORMAT")
    output: str = Field(default="stdout", env="LOG_OUTPUT")
    file_path: str = Field(default="/var/log/med-knowledge/app.log", env="LOG_FILE_PATH")

    @validator("level")
    def validate_log_level(cls, v):
        valid_levels = ["debug", "info", "warning", "error", "critical"]
        if v.lower() not in valid_levels:
            raise ValueError(f"日志级别必须是: {valid_levels}")
        return v.lower()


class JwtSettings(BaseSettings):
    """JWT配置"""

    secret: str = Field(..., env="JWT_SECRET")
    expiry: int = Field(default=86400, env="JWT_EXPIRY")  # 24小时
    algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")


class ApiKeySettings(BaseSettings):
    """API密钥配置"""

    name: str
    key: str
    roles: list[str] = []


class SecuritySettings(BaseSettings):
    """安全配置"""

    enabled: bool = Field(default=False, env="SECURITY_ENABLED")
    jwt: JwtSettings | None = None
    api_keys: list[ApiKeySettings] = []


class RedisSettings(BaseSettings):
    """Redis配置"""

    enabled: bool = Field(default=True, env="REDIS_ENABLED")
    host: str = Field(default="redis", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    password: str = Field(default="", env="REDIS_PASSWORD")
    db: int = Field(default=0, env="REDIS_DB")
    ttl: int = Field(default=3600, env="REDIS_TTL")  # 默认缓存过期时间(秒)
    max_connections: int = Field(default=20, env="REDIS_MAX_CONNECTIONS")


class CacheSettings(BaseSettings):
    """缓存配置"""

    redis: RedisSettings = RedisSettings()


class JaegerSettings(BaseSettings):
    """Jaeger配置"""

    host: str = Field(default="jaeger", env="JAEGER_HOST")
    port: int = Field(default=6831, env="JAEGER_PORT")
    service_name: str = Field(default="med-knowledge", env="JAEGER_SERVICE_NAME")


class TracingSettings(BaseSettings):
    """追踪配置"""

    enabled: bool = Field(default=True, env="TRACING_ENABLED")
    jaeger: JaegerSettings = JaegerSettings()


class PrometheusSettings(BaseSettings):
    """Prometheus配置"""

    port: int = Field(default=9090, env="PROMETHEUS_PORT")
    path: str = Field(default="/metrics", env="PROMETHEUS_PATH")


class MetricsSettings(BaseSettings):
    """监控配置"""

    enabled: bool = Field(default=True, env="METRICS_ENABLED")
    prometheus: PrometheusSettings = PrometheusSettings()


class DataSourceSettings(BaseSettings):
    """数据源配置"""

    name: str
    path: str
    enabled: bool = True


class ScheduleSettings(BaseSettings):
    """调度配置"""

    enabled: bool = Field(default=False, env="DATA_IMPORT_SCHEDULE_ENABLED")
    cron: str = Field(default="0 0 * * 0", env="DATA_IMPORT_CRON")  # 每周日0点运行


class DataImportSettings(BaseSettings):
    """数据导入配置"""

    sources: list[DataSourceSettings] = []
    schedule: ScheduleSettings = ScheduleSettings()


class ServiceSettings(BaseSettings):
    """外部服务配置"""

    host: str
    port: int
    timeout: int = 30
    enabled: bool = True


class ServiceDependencies(BaseSettings):
    """服务依赖配置"""

    rag: ServiceSettings | None = None
    xiaoai: ServiceSettings | None = None
    auth: ServiceSettings | None = None


class RateLimitSettings(BaseSettings):
    """限流配置"""

    enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    default_limit: str = Field(default="100/minute", env="RATE_LIMIT_DEFAULT")
    per_user_limit: str = Field(default="1000/hour", env="RATE_LIMIT_PER_USER")


class Settings(BaseSettings):
    """主配置类"""

    # 环境配置
    environment: str = Field(default="production", env="ENVIRONMENT")

    # 核心配置
    server: ServerSettings = ServerSettings()
    database: DatabaseSettings
    logging: LoggingSettings = LoggingSettings()

    # 可选配置
    security: SecuritySettings | None = None
    cache: CacheSettings | None = None
    tracing: TracingSettings | None = None
    metrics: MetricsSettings | None = None
    data_import: DataImportSettings | None = None
    services: ServiceDependencies | None = None
    rate_limit: RateLimitSettings | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def load_config_from_file(config_path: str) -> dict[str, Any]:
    """从文件加载配置"""
    if not os.path.exists(config_path):
        return {}

    with open(config_path, encoding="utf-8") as f:
        if config_path.endswith((".yaml", ".yml")):
            return yaml.safe_load(f) or {}
        elif config_path.endswith(".json"):

            return json.load(f)

    return {}


def merge_configs(base_config: dict[str, Any], override_config: dict[str, Any]) -> dict[str, Any]:
    """合并配置"""
    result = base_config.copy()

    for key, value in override_config.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value

    return result


@lru_cache
def get_settings() -> Settings:
    """获取应用配置单例"""
    # 基础配置
    config_data = {}

    # 从配置文件加载
    config_path = os.environ.get("CONFIG_PATH", "config/config.yaml")
    if os.path.exists(config_path):
        file_config = load_config_from_file(config_path)
        config_data = merge_configs(config_data, file_config)

    # 环境特定配置
    environment = os.environ.get("ENVIRONMENT", "production")
    env_config_path = f"config/config.{environment}.yaml"
    if os.path.exists(env_config_path):
        env_config = load_config_from_file(env_config_path)
        config_data = merge_configs(config_data, env_config)

    # 从环境变量覆盖敏感配置
    env_overrides = {}

    # 数据库配置
    if os.environ.get("NEO4J_URI"):
        env_overrides.setdefault("database", {})["uri"] = os.environ.get("NEO4J_URI")
    if os.environ.get("NEO4J_USERNAME"):
        env_overrides.setdefault("database", {})["username"] = os.environ.get("NEO4J_USERNAME")
    if os.environ.get("NEO4J_PASSWORD"):
        env_overrides.setdefault("database", {})["password"] = os.environ.get("NEO4J_PASSWORD")

    # 安全配置
    if os.environ.get("JWT_SECRET"):
        env_overrides.setdefault("security", {}).setdefault("jwt", {})["secret"] = os.environ.get(
            "JWT_SECRET"
        )

    # Redis配置
    if os.environ.get("REDIS_HOST"):
        env_overrides.setdefault("cache", {}).setdefault("redis", {})["host"] = os.environ.get(
            "REDIS_HOST"
        )
    if os.environ.get("REDIS_PASSWORD"):
        env_overrides.setdefault("cache", {}).setdefault("redis", {})["password"] = os.environ.get(
            "REDIS_PASSWORD"
        )

    # 合并环境变量覆盖
    if env_overrides:
        config_data = merge_configs(config_data, env_overrides)

    # 设置默认值
    if "cache" not in config_data:
        config_data["cache"] = {"redis": {"enabled": True}}

    if "metrics" not in config_data:
        config_data["metrics"] = {"enabled": True}

    if "rate_limit" not in config_data:
        config_data["rate_limit"] = {"enabled": True}

    try:
        return Settings(**config_data)
    except Exception as e:
        # 如果配置验证失败,使用最小配置
        print(f"配置验证失败: {e}")
        print("使用最小配置启动服务")

        minimal_config = {
            "database": {
                "uri": os.environ.get("NEO4J_URI", "bolt://localhost:7687"),
                "username": os.environ.get("NEO4J_USERNAME", "neo4j"),
                "password": os.environ.get("NEO4J_PASSWORD", "password"),
            }
        }

        return Settings(**minimal_config)


def get_config_summary() -> dict[str, Any]:
    """获取配置摘要(隐藏敏感信息)"""
    settings = get_settings()

    summary = {
        "environment": settings.environment,
        "server": {
            "host": settings.server.host,
            "port": settings.server.port,
            "debug": settings.server.debug,
        },
        "database": {
            "uri": (
                settings.database.uri.replace(settings.database.password, "***")
                if settings.database.password
                else settings.database.uri
            ),
            "max_connections": settings.database.max_connections,
        },
        "logging": {"level": settings.logging.level, "format": settings.logging.format},
    }

    if settings.cache:
        summary["cache"] = {
            "enabled": settings.cache.redis.enabled,
            "host": settings.cache.redis.host,
            "port": settings.cache.redis.port,
        }

    if settings.metrics:
        summary["metrics"] = {"enabled": settings.metrics.enabled}

    if settings.security:
        summary["security"] = {
            "enabled": settings.security.enabled,
            "jwt_configured": bool(settings.security.jwt),
            "api_keys_count": len(settings.security.api_keys) if settings.security.api_keys else 0,
        }

    return summary
