"""
config - 索克生活项目模块
"""

        import yaml
from functools import lru_cache
from pathlib import Path
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any
import os

"""
配置管理模块

使用 Pydantic Settings 进行类型安全的配置管理
"""




class DatabaseConfig(BaseModel):
    """数据库配置"""

    # PostgreSQL 配置
    postgres_host: str = Field(default="localhost", description="PostgreSQL 主机地址")
    postgres_port: int = Field(default=5432, description="PostgreSQL 端口")
    postgres_user: str = Field(default="laoke", description="PostgreSQL 用户名")
    postgres_password: str = Field(default="change_me_in_production", description="PostgreSQL 密码")
    postgres_db: str = Field(default="laoke_service", description="PostgreSQL 数据库名")
    postgres_pool_size: int = Field(default=10, description="连接池大小")
    postgres_max_overflow: int = Field(default=20, description="连接池最大溢出")

    # Redis 配置
    redis_host: str = Field(default="localhost", description="Redis 主机地址")
    redis_port: int = Field(default=6379, description="Redis 端口")
    redis_password: str | None = Field(default=None, description="Redis 密码")
    redis_db: int = Field(default=0, description="Redis 数据库编号")
    redis_pool_size: int = Field(default=10, description="Redis 连接池大小")

    @property
    def postgres_url(self) -> str:
        """获取 PostgreSQL 连接 URL"""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        """获取 Redis 连接 URL"""
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"


class ServerConfig(BaseModel):
    """服务器配置"""

    host: str = Field(default="0.0.0.0", description="服务器监听地址")
    port: int = Field(default=8080, description="HTTP 服务端口")
    grpc_port: int = Field(default=50051, description="gRPC 服务端口")
    metrics_port: int = Field(default=9091, description="监控指标端口")

    # 性能配置
    workers: int = Field(default=1, description="工作进程数")
    max_connections: int = Field(default=1000, description="最大连接数")
    keepalive_timeout: int = Field(default=5, description="Keep-alive 超时时间")

    # 安全配置
    cors_origins: list[str] = Field(default=["*"], description="CORS 允许的源")
    cors_methods: list[str] = Field(default=["*"], description="CORS 允许的方法")
    cors_headers: list[str] = Field(default=["*"], description="CORS 允许的头部")


class AIConfig(BaseModel):
    """AI 配置"""

    # OpenAI 配置
    openai_api_key: str | None = Field(default=None, description="OpenAI API 密钥")
    openai_base_url: str | None = Field(default=None, description="OpenAI API 基础 URL")
    openai_model: str = Field(default="gpt-4", description="默认 OpenAI 模型")

    # Anthropic 配置
    anthropic_api_key: str | None = Field(default=None, description="Anthropic API 密钥")
    anthropic_model: str = Field(default="claude-3-sonnet-20240229", description="默认 Anthropic 模型")

    # 本地模型配置
    local_model_path: Path | None = Field(default=None, description="本地模型路径")
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", description="嵌入模型")

    # 向量数据库配置
    vector_db_type: str = Field(default="chromadb", description="向量数据库类型")
    vector_db_path: Path = Field(default=Path("./data/vectordb"), description="向量数据库路径")


class LoggingConfig(BaseModel):
    """日志配置"""

    level: str = Field(default="INFO", description="日志级别")
    format: str = Field(
        default="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
        description="日志格式"
    )
    rotation: str = Field(default="1 day", description="日志轮转")
    retention: str = Field(default="30 days", description="日志保留时间")
    compression: str = Field(default="gz", description="日志压缩格式")

    # 结构化日志
    structured: bool = Field(default=True, description="是否使用结构化日志")
    json_format: bool = Field(default=False, description="是否使用 JSON 格式")

    # 日志文件路径
    file_path: Path | None = Field(default=None, description="日志文件路径")


class MonitoringConfig(BaseModel):
    """监控配置"""

    # Prometheus 配置
    prometheus_enabled: bool = Field(default=True, description="是否启用 Prometheus")
    prometheus_path: str = Field(default="/metrics", description="Prometheus 指标路径")

    # OpenTelemetry 配置
    otel_enabled: bool = Field(default=False, description="是否启用 OpenTelemetry")
    otel_endpoint: str | None = Field(default=None, description="OpenTelemetry 端点")
    otel_service_name: str = Field(default="laoke-service", description="服务名称")

    # Sentry 配置
    sentry_dsn: str | None = Field(default=None, description="Sentry DSN")
    sentry_environment: str = Field(default="development", description="Sentry 环境")


class SecurityConfig(BaseModel):
    """安全配置"""

    # JWT 配置
    jwt_secret_key: str = Field(default="dev_jwt_secret_change_in_production", description="JWT 密钥")
    jwt_algorithm: str = Field(default="HS256", description="JWT 算法")
    jwt_expire_minutes: int = Field(default=30, description="JWT 过期时间（分钟）")

    # API 密钥配置
    api_keys: list[str] = Field(default=[], description="API 密钥列表")

    # 加密配置
    encryption_key: str | None = Field(default=None, description="数据加密密钥")


class Settings(BaseSettings):
    """应用程序设置"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    # 基础配置
    app_name: str = Field(default="老克智能体服务", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本")
    environment: str = Field(default="development", description="运行环境")
    debug: bool = Field(default=False, description="调试模式")

    # 配置文件路径
    config_path: Path | None = Field(default=None, description="配置文件路径")

    # 子配置
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)

    @validator("environment")
    def validate_environment(cls, v: str) -> str:
        """验证环境配置"""
        allowed_envs = {"development", "staging", "production", "testing"}
        if v.lower() not in allowed_envs:
            raise ValueError(f"Environment must be one of {allowed_envs}")
        return v.lower()

    @validator("config_path", pre=True)
    def validate_config_path(cls, v: str | Path | None) -> Path | None:
        """验证配置文件路径"""
        if v is None:
            return None
        path = Path(v)
        if not path.exists():
            raise ValueError(f"Config file not found: {path}")
        return path

    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.environment == "production"

    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.environment == "development"

    def is_testing(self) -> bool:
        """是否为测试环境"""
        return self.environment == "testing"

    def get_log_level(self) -> str:
        """获取日志级别"""
        if self.debug:
            return "DEBUG"
        return self.logging.level

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return self.model_dump()

    @classmethod
    def from_file(cls, config_path: str | Path) -> "Settings":
        """从配置文件加载设置"""

        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path, encoding="utf-8") as f:
            config_data = yaml.safe_load(f)

        return cls(**config_data)


@lru_cache
def get_settings() -> Settings:
    """获取应用设置（单例模式）"""
    # 从环境变量获取配置文件路径
    config_path = os.getenv("LAOKE_CONFIG_PATH")

    if config_path and Path(config_path).exists():
        return Settings.from_file(config_path)

    return Settings()


# 全局设置实例
settings = get_settings()
