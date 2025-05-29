"""
配置管理
Configuration Management

使用 Pydantic Settings 管理应用配置和环境变量
"""

import os
from functools import lru_cache
from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """数据库配置"""

    model_config = SettingsConfigDict(env_prefix="DATABASE_")

    url: str = Field(
        default="postgresql://postgres:password@localhost:5432/human_review",
        description="数据库连接URL",
    )
    test_url: str = Field(
        default="sqlite+aiosqlite:///./test_human_review.db",
        description="测试数据库连接URL",
    )
    pool_size: int = Field(default=20, description="连接池大小")
    max_overflow: int = Field(default=30, description="连接池最大溢出")
    pool_timeout: int = Field(default=30, description="连接池超时时间")
    pool_recycle: int = Field(default=3600, description="连接回收时间")
    echo: bool = Field(default=False, description="是否打印SQL语句")


class RedisSettings(BaseSettings):
    """Redis配置"""

    model_config = SettingsConfigDict(env_prefix="REDIS_")

    url: str = Field(default="redis://localhost:6379/0", description="Redis连接URL")
    pool_size: int = Field(default=10, description="连接池大小")
    timeout: int = Field(default=5, description="连接超时时间")
    retry_on_timeout: bool = Field(default=True, description="超时重试")
    decode_responses: bool = Field(default=True, description="解码响应")


class SecuritySettings(BaseSettings):
    """安全配置"""

    model_config = SettingsConfigDict(env_prefix="SECURITY_")

    secret_key: str = Field(
        default="your-secret-key-change-in-production", description="JWT密钥"
    )
    algorithm: str = Field(default="HS256", description="JWT算法")
    access_token_expire_minutes: int = Field(
        default=30, description="访问令牌过期时间（分钟）"
    )
    refresh_token_expire_days: int = Field(
        default=7, description="刷新令牌过期时间（天）"
    )

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        return v


class ReviewSettings(BaseSettings):
    """审核配置"""

    model_config = SettingsConfigDict(env_prefix="REVIEW_")

    max_concurrent_reviews: int = Field(default=10, description="最大并发审核数")
    default_review_timeout: int = Field(
        default=1800, description="默认审核超时时间（秒）"
    )
    auto_assign_reviews: bool = Field(default=True, description="是否自动分配审核")
    priority_weights: Dict[str, float] = Field(
        default={
            "critical": 10.0,
            "urgent": 5.0,
            "high": 2.0,
            "normal": 1.0,
            "low": 0.5,
        },
        description="优先级权重",
    )
    risk_thresholds: Dict[str, float] = Field(
        default={"low": 0.3, "medium": 0.6, "high": 0.8, "critical": 0.9},
        description="风险阈值",
    )
    auto_approve_types: List[str] = Field(
        default=["general_advice"], description="可自动通过的审核类型"
    )
    mandatory_review_types: List[str] = Field(
        default=["medical_diagnosis", "emergency_response"],
        description="必须人工审核的类型",
    )


class MonitoringSettings(BaseSettings):
    """监控配置"""

    model_config = SettingsConfigDict(env_prefix="MONITORING_")

    prometheus_enabled: bool = Field(default=True, description="启用Prometheus")
    prometheus_port: int = Field(default=9090, description="Prometheus端口")
    health_check_interval: int = Field(default=30, description="健康检查间隔（秒）")
    metrics_retention_days: int = Field(default=30, description="指标保留天数")
    log_level: str = Field(default="INFO", description="日志级别")
    log_format: str = Field(default="json", description="日志格式（json/text）")


class CelerySettings(BaseSettings):
    """Celery配置"""

    model_config = SettingsConfigDict(env_prefix="CELERY_")

    broker_url: str = Field(
        default="redis://localhost:6379/1", description="消息代理URL"
    )
    result_backend: str = Field(
        default="redis://localhost:6379/2", description="结果后端URL"
    )
    task_serializer: str = Field(default="json", description="任务序列化器")
    result_serializer: str = Field(default="json", description="结果序列化器")
    accept_content: List[str] = Field(default=["json"], description="接受的内容类型")
    timezone: str = Field(default="Asia/Shanghai", description="时区")
    enable_utc: bool = Field(default=True, description="启用UTC")

    # 任务路由
    task_routes: Dict[str, Dict[str, str]] = Field(
        default={
            "human_review_service.tasks.review_assignment": {"queue": "review"},
            "human_review_service.tasks.notification": {"queue": "notification"},
            "human_review_service.tasks.statistics": {"queue": "statistics"},
        },
        description="任务路由配置",
    )

    # 工作进程配置
    worker_concurrency: int = Field(default=4, description="工作进程并发数")
    worker_prefetch_multiplier: int = Field(default=1, description="工作进程预取倍数")
    task_acks_late: bool = Field(default=True, description="延迟确认任务")
    worker_disable_rate_limits: bool = Field(default=False, description="禁用速率限制")


class Settings(BaseSettings):
    """主配置类"""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # 基本配置
    app_name: str = Field(default="Human Review Service", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本")
    debug: bool = Field(default=False, description="调试模式")
    environment: str = Field(default="development", description="运行环境")

    # 服务配置
    host: str = Field(default="0.0.0.0", description="服务主机")
    port: int = Field(default=8000, description="服务端口")
    workers: int = Field(default=1, description="工作进程数")

    # API配置
    api_v1_prefix: str = Field(default="/api/v1", description="API v1前缀")
    docs_url: str = Field(default="/docs", description="文档URL")
    redoc_url: str = Field(default="/redoc", description="ReDoc URL")
    openapi_url: str = Field(default="/openapi.json", description="OpenAPI URL")

    # CORS配置
    cors_origins: List[str] = Field(default=["*"], description="CORS允许的源")
    cors_methods: List[str] = Field(default=["*"], description="CORS允许的方法")
    cors_headers: List[str] = Field(default=["*"], description="CORS允许的头部")

    # 子配置
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    review: ReviewSettings = Field(default_factory=ReviewSettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    celery: CelerySettings = Field(default_factory=CelerySettings)

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed_envs = ["development", "testing", "staging", "production"]
        if v not in allowed_envs:
            raise ValueError(f"Environment must be one of {allowed_envs}")
        return v

    @field_validator("workers")
    @classmethod
    def validate_workers(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Workers must be at least 1")
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

    @property
    def test_database_url(self) -> str:
        """获取测试数据库URL"""
        return self.database.test_url


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（缓存）"""
    return Settings()


# 全局配置实例
settings = get_settings()


def get_database_url() -> str:
    """获取数据库URL"""
    return settings.database.url


def get_redis_url() -> str:
    """获取Redis URL"""
    return settings.redis.url


def get_celery_config() -> Dict[str, Any]:
    """获取Celery配置"""
    return {
        "broker_url": settings.celery.broker_url,
        "result_backend": settings.celery.result_backend,
        "task_serializer": settings.celery.task_serializer,
        "result_serializer": settings.celery.result_serializer,
        "accept_content": settings.celery.accept_content,
        "timezone": settings.celery.timezone,
        "enable_utc": settings.celery.enable_utc,
        "task_routes": settings.celery.task_routes,
        "worker_concurrency": settings.celery.worker_concurrency,
        "worker_prefetch_multiplier": settings.celery.worker_prefetch_multiplier,
        "task_acks_late": settings.celery.task_acks_late,
        "worker_disable_rate_limits": settings.celery.worker_disable_rate_limits,
    }


def get_cors_config() -> Dict[str, Any]:
    """获取CORS配置"""
    return {
        "allow_origins": settings.cors_origins,
        "allow_methods": settings.cors_methods,
        "allow_headers": settings.cors_headers,
        "allow_credentials": True,
    }
