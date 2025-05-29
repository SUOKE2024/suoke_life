"""
配置管理模块

使用 Pydantic Settings 进行类型安全的配置管理。
"""

from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import BaseSettings, Field, validator
from pydantic_settings import BaseSettings as PydanticBaseSettings


class DatabaseSettings(BaseSettings):
    """数据库配置"""

    url: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/inquiry_service",
        description="数据库连接URL",
    )
    pool_size: int = Field(default=10, description="连接池大小")
    max_overflow: int = Field(default=20, description="连接池最大溢出")
    pool_timeout: int = Field(default=30, description="连接池超时时间(秒)")
    pool_recycle: int = Field(default=3600, description="连接回收时间(秒)")
    echo: bool = Field(default=False, description="是否打印SQL语句")

    class Config:
        env_prefix = "DB_"


class RedisSettings(BaseSettings):
    """Redis配置"""

    url: str = Field(default="redis://localhost:6379/0", description="Redis连接URL")
    max_connections: int = Field(default=20, description="最大连接数")
    retry_on_timeout: bool = Field(default=True, description="超时重试")
    socket_timeout: int = Field(default=5, description="Socket超时时间(秒)")
    socket_connect_timeout: int = Field(default=5, description="连接超时时间(秒)")

    class Config:
        env_prefix = "REDIS_"


class GRPCSettings(BaseSettings):
    """gRPC服务配置"""

    host: str = Field(default="0.0.0.0", description="服务监听地址")
    port: int = Field(default=50052, description="服务监听端口")
    max_workers: int = Field(default=10, description="最大工作线程数")
    max_receive_message_length: int = Field(
        default=4 * 1024 * 1024, description="最大接收消息长度"
    )
    max_send_message_length: int = Field(
        default=4 * 1024 * 1024, description="最大发送消息长度"
    )
    compression: str = Field(default="gzip", description="压缩算法")

    class Config:
        env_prefix = "GRPC_"


class LoggingSettings(BaseSettings):
    """日志配置"""

    level: str = Field(default="INFO", description="日志级别")
    format: str = Field(
        default="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>",
        description="日志格式",
    )
    rotation: str = Field(default="1 day", description="日志轮转")
    retention: str = Field(default="30 days", description="日志保留时间")
    compression: str = Field(default="zip", description="日志压缩格式")
    serialize: bool = Field(default=False, description="是否序列化为JSON")

    class Config:
        env_prefix = "LOG_"


class AISettings(BaseSettings):
    """AI服务配置"""

    openai_api_key: str | None = Field(default=None, description="OpenAI API密钥")
    openai_base_url: str = Field(
        default="https://api.openai.com/v1", description="OpenAI API基础URL"
    )
    anthropic_api_key: str | None = Field(default=None, description="Anthropic API密钥")
    default_model: str = Field(default="gpt-4", description="默认AI模型")
    max_tokens: int = Field(default=2048, description="最大token数")
    temperature: float = Field(default=0.7, description="生成温度")
    timeout: int = Field(default=30, description="请求超时时间(秒)")

    class Config:
        env_prefix = "AI_"


class TCMSettings(BaseSettings):
    """中医知识库配置"""

    data_path: Path = Field(
        default=Path("data/tcm_knowledge"), description="知识库数据路径"
    )
    auto_create_sample_data: bool = Field(
        default=True, description="是否自动创建示例数据"
    )
    cache_ttl: int = Field(default=3600, description="缓存TTL(秒)")
    min_confidence: float = Field(default=0.6, description="最小置信度阈值")

    class Config:
        env_prefix = "TCM_"

    @validator("data_path", pre=True)
    def validate_data_path(cls, v: Any) -> Path:
        if isinstance(v, str):
            return Path(v)
        return v


class MonitoringSettings(BaseSettings):
    """监控配置"""

    enable_metrics: bool = Field(default=True, description="是否启用指标收集")
    metrics_port: int = Field(default=8080, description="指标服务端口")
    enable_tracing: bool = Field(default=False, description="是否启用链路追踪")
    jaeger_endpoint: str | None = Field(default=None, description="Jaeger端点")
    sentry_dsn: str | None = Field(default=None, description="Sentry DSN")

    class Config:
        env_prefix = "MONITORING_"


class Settings(PydanticBaseSettings):
    """主配置类"""

    # 基础配置
    app_name: str = Field(default="inquiry-service", description="应用名称")
    version: str = Field(default="1.0.0", description="应用版本")
    debug: bool = Field(default=False, description="调试模式")
    environment: str = Field(default="development", description="运行环境")

    # 子配置
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    grpc: GRPCSettings = Field(default_factory=GRPCSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    ai: AISettings = Field(default_factory=AISettings)
    tcm: TCMSettings = Field(default_factory=TCMSettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)

    # 安全配置
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="应用密钥",
    )
    allowed_hosts: list[str] = Field(default=["*"], description="允许的主机")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"

    @validator("environment")
    def validate_environment(cls, v: str) -> str:
        allowed_envs = ["development", "testing", "staging", "production"]
        if v not in allowed_envs:
            raise ValueError(f"Environment must be one of {allowed_envs}")
        return v

    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.environment == "production"

    @property
    def is_testing(self) -> bool:
        """是否为测试环境"""
        return self.environment == "testing"

    def get_database_url(self) -> str:
        """获取数据库连接URL"""
        return self.database.url

    def get_redis_url(self) -> str:
        """获取Redis连接URL"""
        return self.redis.url

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return self.dict()


@lru_cache
def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    return Settings()


def get_config_file_path() -> Path:
    """获取配置文件路径"""
    config_dir = Path(__file__).parent.parent.parent / "config"
    return config_dir / "config.yaml"


def load_config_from_file(config_path: Path | None = None) -> dict[str, Any]:
    """从文件加载配置"""
    import yaml

    if config_path is None:
        config_path = get_config_file_path()

    if not config_path.exists():
        return {}

    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


# 导出配置实例
settings = get_settings()
