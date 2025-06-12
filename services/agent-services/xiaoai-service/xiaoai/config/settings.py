"""
小艾智能体服务配置管理

提供统一的配置管理功能，支持环境变量、配置文件等多种配置源
"""

from functools import lru_cache
import os
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseModel):
    """数据库配置"""

    host: str = Field(default="localhost", description="数据库主机")
    port: int = Field(default=5432, description="数据库端口")
    name: str = Field(default="xiaoai_db", description="数据库名称")
    user: str = Field(default="xiaoai", description="数据库用户")
    password: str = Field(default="", description="数据库密码")
    pool_size: int = Field(default=10, description="连接池大小")
    max_overflow: int = Field(default=20, description="最大溢出连接数")
    pool_timeout: int = Field(default=30, description="连接池超时")
    pool_recycle: int = Field(default=3600, description="连接回收时间")


class RedisConfig(BaseModel):
    """Redis配置"""

    host: str = Field(default="localhost", description="Redis主机")
    port: int = Field(default=6379, description="Redis端口")
    db: int = Field(default=0, description="Redis数据库")
    password: Optional[str] = Field(default=None, description="Redis密码")
    max_connections: int = Field(default=100, description="最大连接数")
    socket_timeout: int = Field(default=5, description="Socket超时")


class ExternalServiceConfig(BaseModel):
    """外部服务配置"""

    host: str = Field(description="服务主机")
    port: int = Field(description="服务端口")
    timeout: int = Field(default=30, description="请求超时")
    max_retries: int = Field(default=3, description="最大重试次数")


class ExternalServicesConfig(BaseModel):
    """外部服务集合配置"""

    look_service: ExternalServiceConfig = Field(
        default_factory=lambda: ExternalServiceConfig(
            host="localhost", port=8001, timeout=30, max_retries=3
        )
    )
    listen_service: ExternalServiceConfig = Field(
        default_factory=lambda: ExternalServiceConfig(
            host="localhost", port=8002, timeout=30, max_retries=3
        )
    )
    inquiry_service: ExternalServiceConfig = Field(
        default_factory=lambda: ExternalServiceConfig(
            host="localhost", port=8003, timeout=60, max_retries=3
        )
    )
    palpation_service: ExternalServiceConfig = Field(
        default_factory=lambda: ExternalServiceConfig(
            host="localhost", port=8004, timeout=30, max_retries=3
        )
    )
    calculation_service: ExternalServiceConfig = Field(
        default_factory=lambda: ExternalServiceConfig(
            host="localhost", port=8005, timeout=45, max_retries=3
        )
    )


class AIModelConfig(BaseModel):
    """AI模型配置"""

    cache_size: str = Field(default="2GB", description="模型缓存大小")
    model_timeout: int = Field(default=30, description="模型推理超时")
    batch_size: int = Field(default=32, description="批处理大小")
    enable_gpu: bool = Field(default=True, description="启用GPU")
    device: str = Field(default="auto", description="计算设备")


class MonitoringConfig(BaseModel):
    """监控配置"""

    enable_metrics: bool = Field(default=True, description="启用指标收集")
    metrics_port: int = Field(default=9090, description="指标端口")
    health_check_interval: int = Field(default=30, description="健康检查间隔")
    prometheus_enabled: bool = Field(default=True, description="启用Prometheus")


class AccessibilityConfig(BaseModel):
    """无障碍配置"""

    enable_tts: bool = Field(default=True, description="启用文本转语音")
    enable_stt: bool = Field(default=True, description="启用语音转文本")
    enable_gesture: bool = Field(default=True, description="启用手势控制")
    voice_cache_size: str = Field(default="500MB", description="语音缓存大小")


class SecurityConfig(BaseModel):
    """安全配置"""

    secret_key: str = Field(description="应用密钥")
    jwt_algorithm: str = Field(default="HS256", description="JWT算法")
    jwt_expire_minutes: int = Field(default=30, description="JWT过期时间(分钟)")
    encryption_key: Optional[str] = Field(default=None, description="加密密钥")


class Settings(BaseSettings):
    """应用设置"""

    # 基本配置
    app_name: str = Field(default="xiaoai-service", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本")
    environment: str = Field(default="development", description="运行环境")
    debug: bool = Field(default=False, description="调试模式")
    log_level: str = Field(default="INFO", description="日志级别")

    # 服务器配置
    host: str = Field(default="0.0.0.0", description="服务主机")
    port: int = Field(default=8000, description="服务端口")
    workers: int = Field(default=4, description="工作进程数")
    max_connections: int = Field(default=1000, description="最大连接数")
    keepalive_timeout: int = Field(default=65, description="保持连接超时")

    # 组件配置
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    external_services: ExternalServicesConfig = Field(default_factory=ExternalServicesConfig)
    ai_models: AIModelConfig = Field(default_factory=AIModelConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    accessibility: AccessibilityConfig = Field(default_factory=AccessibilityConfig)
    security: SecurityConfig = Field(
        default_factory=lambda: SecurityConfig(secret_key="change-this-in-production")
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"
        case_sensitive = False

        # 环境变量前缀
        env_prefix = ""

        # 字段别名映射
        fields = {
            "database": {"env": "DATABASE"},
            "redis": {"env": "REDIS"},
            "external_services": {"env": "EXTERNAL_SERVICES"},
        }


@lru_cache()
def get_settings() -> Settings:
    """获取应用设置单例

    Returns:
        应用设置实例
    """
    return Settings()


# 导出配置实例
settings = get_settings()
