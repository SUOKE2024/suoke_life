"""
配置管理模块

使用 pydantic-settings 进行类型安全的配置管理，
支持环境变量、配置文件等多种配置源。
"""

from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """数据库配置"""

    # PostgreSQL 配置
    postgres_host: str = Field(default="localhost", description="PostgreSQL主机")
    postgres_port: int = Field(default=5432, description="PostgreSQL端口")
    postgres_user: str = Field(default="xiaoke", description="PostgreSQL用户名")
    postgres_password: str = Field(default="", description="PostgreSQL密码")
    postgres_db: str = Field(default="xiaoke_db", description="PostgreSQL数据库名")

    # MongoDB 配置
    mongodb_url: str = Field(
        default="mongodb://localhost:27017", description="MongoDB连接URL"
    )
    mongodb_db: str = Field(default="xiaoke_knowledge", description="MongoDB数据库名")

    # Redis 配置
    redis_url: str = Field(
        default="redis://localhost:6379/0", description="Redis连接URL"
    )

    @property
    def postgres_url(self) -> str:
        """构建 PostgreSQL 连接URL"""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


class AISettings(BaseSettings):
    """AI相关配置"""

    # OpenAI 配置
    openai_api_key: str | None = Field(default=None, description="OpenAI API密钥")
    openai_base_url: str = Field(
        default="https://api.openai.com/v1", description="OpenAI API基础URL"
    )
    openai_model: str = Field(default="gpt-4", description="默认OpenAI模型")

    # Anthropic 配置
    anthropic_api_key: str | None = Field(default=None, description="Anthropic API密钥")

    # 本地模型配置
    local_model_path: Path | None = Field(default=None, description="本地模型路径")

    # 向量数据库配置
    vector_db_type: str = Field(default="chromadb", description="向量数据库类型")
    vector_db_path: Path = Field(
        default=Path("./data/vector_db"), description="向量数据库存储路径"
    )

    # 中医知识库配置
    tcm_knowledge_enabled: bool = Field(default=True, description="是否启用中医知识库")
    tcm_model_path: Path | None = Field(default=None, description="中医专用模型路径")


class SecuritySettings(BaseSettings):
    """安全配置"""

    secret_key: str = Field(
        default="your-secret-key-change-in-production", description="JWT密钥"
    )
    algorithm: str = Field(default="HS256", description="JWT算法")
    access_token_expire_minutes: int = Field(
        default=30, description="访问令牌过期时间(分钟)"
    )
    refresh_token_expire_days: int = Field(
        default=7, description="刷新令牌过期时间(天)"
    )

    # CORS 配置
    cors_origins: list[str] = Field(
        default=["http://localhost:3000"], description="允许的CORS源"
    )
    cors_credentials: bool = Field(default=True, description="是否允许凭据")
    cors_methods: list[str] = Field(
        default=["GET", "POST", "PUT", "DELETE"], description="允许的HTTP方法"
    )
    cors_headers: list[str] = Field(default=["*"], description="允许的HTTP头")


class MonitoringSettings(BaseSettings):
    """监控配置"""

    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_format: str = Field(default="json", description="日志格式")
    log_file: Path | None = Field(default=None, description="日志文件路径")

    # 指标配置
    metrics_enabled: bool = Field(default=True, description="是否启用指标收集")
    metrics_port: int = Field(default=8001, description="指标服务端口")

    # 链路追踪配置
    tracing_enabled: bool = Field(default=False, description="是否启用链路追踪")
    jaeger_endpoint: str | None = Field(default=None, description="Jaeger端点")

    # 健康检查配置
    health_check_interval: int = Field(default=30, description="健康检查间隔(秒)")


class ServiceSettings(BaseSettings):
    """服务配置"""

    # 基本信息
    service_name: str = Field(default="xiaoke-service", description="服务名称")
    service_version: str = Field(default="1.0.0", description="服务版本")
    environment: str = Field(default="development", description="运行环境")
    debug: bool = Field(default=False, description="是否开启调试模式")

    # 服务器配置
    host: str = Field(default="0.0.0.0", description="服务器主机")
    port: int = Field(default=8000, description="服务器端口")
    workers: int = Field(default=1, description="工作进程数")

    # API配置
    api_prefix: str = Field(default="/api/v1", description="API前缀")
    docs_url: str = Field(default="/docs", description="文档URL")
    redoc_url: str = Field(default="/redoc", description="ReDoc URL")

    # 限流配置
    rate_limit_enabled: bool = Field(default=True, description="是否启用限流")
    rate_limit_requests: int = Field(default=100, description="限流请求数")
    rate_limit_window: int = Field(default=60, description="限流时间窗口(秒)")

    @validator("environment")
    def validate_environment(cls, v: str) -> str:
        """验证环境配置"""
        allowed = {"development", "testing", "staging", "production"}
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v


class Settings(BaseSettings):
    """主配置类"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    # 子配置
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    ai: AISettings = Field(default_factory=AISettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    service: ServiceSettings = Field(default_factory=ServiceSettings)

    def model_dump_json(self, **kwargs: Any) -> str:
        """序列化配置为JSON，隐藏敏感信息"""
        data = self.model_dump(**kwargs)

        # 隐藏敏感信息
        sensitive_keys = {
            "postgres_password",
            "secret_key",
            "openai_api_key",
            "anthropic_api_key",
        }

        def hide_sensitive(obj: Any) -> Any:
            if isinstance(obj, dict):
                return {
                    k: "***" if k in sensitive_keys else hide_sensitive(v)
                    for k, v in obj.items()
                }
            return obj

        return hide_sensitive(data)


@lru_cache
def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    return Settings()


# 全局配置实例
settings = get_settings()
