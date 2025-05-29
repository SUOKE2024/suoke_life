"""
配置管理模块
提供环境变量读取和配置验证功能
"""

from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    """数据库配置"""

    url: str = Field(
        default="postgresql://palpation_user:password@localhost:5432/palpation_service"
    )
    pool_size: int = Field(default=10)
    max_overflow: int = Field(default=20)
    pool_timeout: int = Field(default=30)

    model_config = {"env_prefix": "DATABASE_"}


class RedisConfig(BaseSettings):
    """Redis配置"""

    url: str = Field(default="redis://localhost:6379/0")
    pool_size: int = Field(default=10)
    pool_timeout: int = Field(default=5)
    default_ttl: int = Field(default=3600)
    session_ttl: int = Field(default=7200)
    report_ttl: int = Field(default=86400)

    model_config = {"env_prefix": "REDIS_"}


class ServiceConfig(BaseSettings):
    """服务配置"""

    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    env: str = Field(default="development")
    debug: bool = Field(default=True)
    name: str = Field(default="palpation-service")
    version: str = Field(default="1.0.0")

    model_config = {"env_prefix": "SERVICE_"}


class LogConfig(BaseSettings):
    """日志配置"""

    level: str = Field(default="INFO")
    file: str | None = Field(default="logs/palpation_service.log")
    max_size: str = Field(default="100MB")
    backup_count: int = Field(default=5)
    structured: bool = Field(default=True)

    model_config = {"env_prefix": "LOG_"}


class AIModelConfig(BaseSettings):
    """AI模型配置"""

    path: str = Field(default="models/")
    enable_gpu: bool = Field(default=False)
    gpu_device_id: int = Field(default=0)
    batch_size: int = Field(default=32)
    timeout: int = Field(default=30)

    model_config = {"env_prefix": "MODEL_"}


class FusionConfig(BaseSettings):
    """多模态融合配置"""

    enabled_modalities: list[str] = Field(
        default=["pressure", "temperature", "texture", "vibration"]
    )
    algorithm: str = Field(default="attention_weighted")
    weights_pressure: float = Field(default=0.4)
    weights_temperature: float = Field(default=0.3)
    weights_texture: float = Field(default=0.2)
    weights_vibration: float = Field(default=0.1)

    @field_validator("enabled_modalities", mode="before")
    @classmethod
    def parse_modalities(cls, v):
        if isinstance(v, str):
            return [m.strip() for m in v.split(",")]
        return v

    @property
    def fusion_weights(self) -> dict[str, float]:
        """获取融合权重字典"""
        return {
            "pressure": self.weights_pressure,
            "temperature": self.weights_temperature,
            "texture": self.weights_texture,
            "vibration": self.weights_vibration,
        }

    model_config = {"env_prefix": "FUSION_"}


class MonitoringConfig(BaseSettings):
    """监控配置"""

    enable_metrics: bool = Field(default=True)
    metrics_port: int = Field(default=9090)
    retention_days: int = Field(default=30)
    health_check_interval: int = Field(default=30)

    model_config = {"env_prefix": "METRICS_"}


class SecurityConfig(BaseSettings):
    """安全配置"""

    jwt_secret_key: str = Field(default="your-super-secret-jwt-key-change-this-in-production")
    jwt_expiration_time: int = Field(default=3600)
    rate_limit_requests: int = Field(default=100)
    rate_limit_window: int = Field(default=60)
    cors_origins: str = Field(default="*")
    cors_methods: str = Field(default="GET,POST,PUT,DELETE,OPTIONS")
    cors_headers: str = Field(default="*")

    @property
    def cors_origins_list(self) -> list[str]:
        """获取CORS源列表"""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def cors_methods_list(self) -> list[str]:
        """获取CORS方法列表"""
        return [method.strip() for method in self.cors_methods.split(",")]

    @property
    def cors_headers_list(self) -> list[str]:
        """获取CORS头列表"""
        if self.cors_headers == "*":
            return ["*"]
        return [header.strip() for header in self.cors_headers.split(",")]


class ExternalServiceConfig(BaseSettings):
    """外部服务配置"""

    xiaoai_service_url: str = Field(default="http://localhost:8001")
    xiaoke_service_url: str = Field(default="http://localhost:8002")
    laoke_service_url: str = Field(default="http://localhost:8003")
    soer_service_url: str = Field(default="http://localhost:8004")
    message_queue_url: str = Field(default="redis://localhost:6379/1")
    storage_type: str = Field(default="local")
    storage_path: str = Field(default="data/storage/")


class DevelopmentConfig(BaseSettings):
    """开发配置"""

    testing: bool = Field(default=False)
    enable_profiling: bool = Field(default=False)
    enable_docs: bool = Field(default=True)
    enable_experimental_features: bool = Field(default=False)
    enable_ab_testing: bool = Field(default=False)
    enable_detailed_errors: bool = Field(default=True)
    enable_request_tracing: bool = Field(default=True)


class DeploymentConfig(BaseSettings):
    """部署配置"""

    workers: int = Field(default=1)
    threads: int = Field(default=4)
    request_timeout: int = Field(default=60)
    max_request_size: int = Field(default=10)


class Settings(BaseSettings):
    """主配置类"""

    # 子配置
    database: DatabaseConfig = DatabaseConfig()
    redis: RedisConfig = RedisConfig()
    service: ServiceConfig = ServiceConfig()
    log: LogConfig = LogConfig()
    ai_model: AIModelConfig = AIModelConfig()
    fusion: FusionConfig = FusionConfig()
    monitoring: MonitoringConfig = MonitoringConfig()
    security: SecurityConfig = SecurityConfig()
    external_service: ExternalServiceConfig = ExternalServiceConfig()
    development: DevelopmentConfig = DevelopmentConfig()
    deployment: DeploymentConfig = DeploymentConfig()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 初始化子配置
        self.database = DatabaseConfig()
        self.redis = RedisConfig()
        self.service = ServiceConfig()
        self.log = LogConfig()
        self.ai_model = AIModelConfig()
        self.fusion = FusionConfig()
        self.monitoring = MonitoringConfig()
        self.security = SecurityConfig()
        self.external_service = ExternalServiceConfig()
        self.development = DevelopmentConfig()
        self.deployment = DeploymentConfig()

    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.service.env.lower() in ["development", "dev"]

    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.service.env.lower() in ["production", "prod"]

    @property
    def is_testing(self) -> bool:
        """是否为测试环境"""
        return self.development.testing or self.service.env.lower() in ["testing", "test"]

    def get_log_config(self) -> dict[str, Any]:
        """获取日志配置字典"""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
                "structured": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": self.log.level,
                    "formatter": "structured" if self.log.structured else "default",
                    "stream": "ext://sys.stdout",
                },
                "file": (
                    {
                        "class": "logging.handlers.RotatingFileHandler",
                        "level": self.log.level,
                        "formatter": "structured" if self.log.structured else "default",
                        "filename": self.log.file,
                        "maxBytes": self._parse_size(self.log.max_size),
                        "backupCount": self.log.backup_count,
                        "encoding": "utf-8",
                    }
                    if self.log.file
                    else None
                ),
            },
            "loggers": {
                "": {
                    "level": self.log.level,
                    "handlers": ["console"] + (["file"] if self.log.file else []),
                    "propagate": False,
                },
                "uvicorn": {
                    "level": "INFO",
                    "handlers": ["console"] + (["file"] if self.log.file else []),
                    "propagate": False,
                },
                "sqlalchemy": {
                    "level": "WARNING",
                    "handlers": ["console"] + (["file"] if self.log.file else []),
                    "propagate": False,
                },
            },
        }

    def _parse_size(self, size_str: str) -> int:
        """解析大小字符串为字节数"""
        size_str = size_str.upper()
        if size_str.endswith("KB"):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith("MB"):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith("GB"):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": False}


@lru_cache
def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    return Settings()


# 全局配置实例
settings = get_settings()
