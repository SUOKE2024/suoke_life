#!/usr/bin/env python3
"""
健康数据服务配置模块

提供应用程序的配置管理，支持环境变量和配置文件。
"""

import os
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
    # 兼容性处理
    from pydantic import BaseSettings
    
    class SettingsConfigDict:
        def __init__(self, **kwargs):
            pass

from pydantic import Field, field_validator


class DatabaseSettings(BaseSettings):
    """数据库配置"""

    host: str = Field(default="localhost", description="数据库主机")
    port: int = Field(default=5432, description="数据库端口")
    name: str = Field(default="health_data", description="数据库名称")
    user: str = Field(default="postgres", description="数据库用户")
    password: str = Field(default="", description="数据库密码")

    # 连接池配置
    pool_size: int = Field(default=10, description="连接池大小")
    max_overflow: int = Field(default=20, description="最大溢出连接数")
    pool_timeout: int = Field(default=30, description="连接池超时时间")
    pool_recycle: int = Field(default=3600, description="连接回收时间")

    @property
    def url(self) -> str:
        """获取异步数据库连接URL"""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    @property
    def sync_url(self) -> str:
        """获取同步数据库连接URL"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class RedisSettings(BaseSettings):
    """Redis配置"""

    host: str = Field(default="localhost", description="Redis主机")
    port: int = Field(default=6379, description="Redis端口")
    db: int = Field(default=0, description="Redis数据库")
    password: Optional[str] = Field(default=None, description="Redis密码")

    # 连接池配置
    max_connections: int = Field(default=100, description="最大连接数")
    retry_on_timeout: bool = Field(default=True, description="超时重试")

    @property
    def url(self) -> str:
        """获取Redis连接URL"""
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"


class APISettings(BaseSettings):
    """API配置"""

    title: str = Field(default="健康数据服务API", description="API标题")
    description: str = Field(
        default="索克生活健康数据管理和分析服务", description="API描述"
    )
    version: str = Field(default="0.1.0", description="API版本")

    # 服务器配置
    host: str = Field(default="0.0.0.0", description="服务器主机")
    port: int = Field(default=8000, description="服务器端口")
    workers: int = Field(default=1, description="工作进程数")

    # CORS配置
    cors_origins: List[str] = Field(default=["*"], description="CORS允许的源")
    cors_methods: List[str] = Field(default=["*"], description="CORS允许的方法")
    cors_headers: List[str] = Field(default=["*"], description="CORS允许的头部")

    # 限流配置
    rate_limit_requests: int = Field(default=100, description="每分钟请求限制")
    rate_limit_window: int = Field(default=60, description="限流窗口时间(秒)")


class SecuritySettings(BaseSettings):
    """安全配置"""

    secret_key: str = Field(
        default="development_secret_key_32_characters_long_minimum_for_jwt_signing",
        description="JWT密钥",
    )
    algorithm: str = Field(default="HS256", description="JWT算法")
    access_token_expire_minutes: int = Field(
        default=30, description="访问令牌过期时间(分钟)"
    )
    refresh_token_expire_days: int = Field(
        default=7, description="刷新令牌过期时间(天)"
    )

    # 密码配置
    password_min_length: int = Field(default=8, description="密码最小长度")
    password_require_uppercase: bool = Field(
        default=True, description="密码需要大写字母"
    )
    password_require_lowercase: bool = Field(
        default=True, description="密码需要小写字母"
    )
    password_require_numbers: bool = Field(default=True, description="密码需要数字")
    password_require_symbols: bool = Field(default=False, description="密码需要符号")

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        return v


class LoggingSettings(BaseSettings):
    """日志配置"""

    level: str = Field(default="INFO", description="日志级别")
    format: str = Field(
        default="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
        description="日志格式",
    )

    # 文件日志配置
    file_enabled: bool = Field(default=True, description="启用文件日志")
    file_path: str = Field(
        default="logs/health_data_service.log", description="日志文件路径"
    )
    file_rotation: str = Field(default="1 day", description="日志轮转")
    file_retention: str = Field(default="30 days", description="日志保留时间")

    # 结构化日志
    json_logs: bool = Field(default=False, description="JSON格式日志")


class MonitoringSettings(BaseSettings):
    """监控配置"""

    # Prometheus配置
    prometheus_enabled: bool = Field(default=True, description="启用Prometheus监控")
    prometheus_port: int = Field(default=9090, description="Prometheus端口")

    # 健康检查配置
    health_check_enabled: bool = Field(default=True, description="启用健康检查")
    health_check_interval: int = Field(default=30, description="健康检查间隔(秒)")

    # OpenTelemetry配置
    otel_enabled: bool = Field(default=False, description="启用OpenTelemetry")
    otel_endpoint: Optional[str] = Field(default=None, description="OTEL端点")
    otel_service_name: str = Field(
        default="health-data-service", description="服务名称"
    )


class MLSettings(BaseSettings):
    """机器学习配置"""

    # 模型配置
    model_cache_size: int = Field(default=10, description="模型缓存大小")
    model_timeout: int = Field(default=30, description="模型推理超时时间(秒)")

    # ONNX配置
    onnx_providers: List[str] = Field(
        default=["CPUExecutionProvider"], description="ONNX执行提供者"
    )
    onnx_session_options: Dict[str, Any] = Field(
        default_factory=dict, description="ONNX会话选项"
    )


class Settings(BaseSettings):
    """主配置类"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
    )

    # 环境配置
    environment: str = Field(default="development", description="运行环境")
    debug: bool = Field(default=False, description="调试模式")
    testing: bool = Field(default=False, description="测试模式")

    # 子配置
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    api: APISettings = Field(default_factory=APISettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    ml: MLSettings = Field(default_factory=MLSettings)

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = ["development", "testing", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
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
        return self.testing or self.environment == "testing"

    # 兼容性属性
    @property
    def ALLOWED_HOSTS(self) -> List[str]:  # noqa: N802
        """允许的主机列表"""
        return self.api.cors_origins

    @property
    def HOST(self) -> str:  # noqa: N802
        """服务器主机"""
        return self.api.host

    @property
    def PORT(self) -> int:  # noqa: N802
        """服务器端口"""
        return self.api.port

    @property
    def DEBUG(self) -> bool:  # noqa: N802
        """调试模式"""
        return self.debug


# 全局设置实例
settings = Settings()
