"""
应用配置设置模块

使用 Pydantic Settings 进行类型安全的配置管理
"""

import os
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类"""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # 基本配置
    app_name: str = Field(default="索儿智能体服务", description="应用名称")
    debug: bool = Field(default=False, description="调试模式")
    environment: str = Field(default="development", description="运行环境")

    # 服务器配置
    host: str = Field(default="0.0.0.0", description="服务器主机")
    port: int = Field(default=8003, description="服务器端口")
    allowed_hosts: list[str] = Field(default=["*"], description="允许的主机列表")

    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日志格式",
    )

    # 数据库配置
    mongodb_url: str = Field(
        default="mongodb://localhost:27017", description="MongoDB 连接 URL"
    )
    mongodb_database: str = Field(
        default="soer_service", description="MongoDB 数据库名"
    )

    # Redis 配置
    redis_url: str = Field(
        default="redis://localhost:6379/0", description="Redis 连接 URL"
    )

    # PostgreSQL 配置 (可选)
    postgres_url: str | None = Field(default=None, description="PostgreSQL 连接 URL")

    # AI 服务配置
    openai_api_key: str | None = Field(default=None, description="OpenAI API 密钥")
    openai_base_url: str = Field(
        default="https://api.openai.com/v1", description="OpenAI API 基础 URL"
    )

    anthropic_api_key: str | None = Field(
        default=None, description="Anthropic API 密钥"
    )

    # 安全配置
    secret_key: str = Field(
        default="your-secret-key-change-in-production", description="应用密钥"
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT 算法")
    jwt_expire_minutes: int = Field(default=30, description="JWT 过期时间（分钟）")

    # 监控配置
    enable_metrics: bool = Field(default=True, description="启用指标收集")
    metrics_port: int = Field(default=9090, description="指标服务端口")

    # 健康检查配置
    health_check_interval: int = Field(default=30, description="健康检查间隔（秒）")

    # 营养分析配置
    nutrition_api_key: str | None = Field(default=None, description="营养数据 API 密钥")

    # 文件存储配置
    upload_dir: str = Field(default="./uploads", description="文件上传目录")
    max_file_size: int = Field(
        default=10 * 1024 * 1024, description="最大文件大小（字节）"  # 10MB
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """验证日志级别"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"日志级别必须是 {valid_levels} 之一")
        return v.upper()

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """验证运行环境"""
        valid_envs = ["development", "testing", "staging", "production"]
        if v.lower() not in valid_envs:
            raise ValueError(f"运行环境必须是 {valid_envs} 之一")
        return v.lower()

    @field_validator("upload_dir")
    @classmethod
    def create_upload_dir(cls, v: str) -> str:
        """创建上传目录"""
        os.makedirs(v, exist_ok=True)
        return v

    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.environment == "development"


@lru_cache
def get_settings() -> Settings:
    """获取应用配置实例（单例模式）"""
    return Settings()
