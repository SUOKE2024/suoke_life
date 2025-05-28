"""应用配置设置"""

import os
from functools import lru_cache
from typing import Any, Dict, List, Optional

from pydantic import Field, PostgresDsn, RedisDsn, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """数据库配置"""
    
    host: str = Field(default="localhost", description="数据库主机")
    port: int = Field(default=5432, description="数据库端口")
    name: str = Field(default="auth_db", description="数据库名称")
    user: str = Field(default="auth_user", description="数据库用户")
    password: str = Field(default="auth_password", description="数据库密码")
    pool_size: int = Field(default=10, description="连接池大小")
    max_overflow: int = Field(default=20, description="连接池最大溢出")
    echo: bool = Field(default=False, description="是否打印SQL")
    
    @property
    def url(self) -> str:
        """获取数据库连接URL"""
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
    max_connections: int = Field(default=10, description="最大连接数")
    
    @property
    def url(self) -> str:
        """获取Redis连接URL"""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"


class JWTSettings(BaseSettings):
    """JWT配置"""
    
    secret_key: str = Field(description="JWT密钥")
    algorithm: str = Field(default="HS256", description="JWT算法")
    access_token_expire_minutes: int = Field(default=60, description="访问令牌过期时间(分钟)")
    refresh_token_expire_days: int = Field(default=7, description="刷新令牌过期时间(天)")
    issuer: str = Field(default="suoke-auth-service", description="JWT发行者")
    audience: str = Field(default="suoke-life", description="JWT受众")


class SecuritySettings(BaseSettings):
    """安全配置"""
    
    password_min_length: int = Field(default=8, description="密码最小长度")
    password_require_uppercase: bool = Field(default=True, description="密码是否需要大写字母")
    password_require_lowercase: bool = Field(default=True, description="密码是否需要小写字母")
    password_require_numbers: bool = Field(default=True, description="密码是否需要数字")
    password_require_symbols: bool = Field(default=True, description="密码是否需要特殊字符")
    max_login_attempts: int = Field(default=5, description="最大登录尝试次数")
    lockout_duration_minutes: int = Field(default=30, description="账户锁定时间(分钟)")
    session_timeout_minutes: int = Field(default=60, description="会话超时时间(分钟)")
    mfa_issuer_name: str = Field(default="Suoke Life", description="MFA发行者名称")


class ServerSettings(BaseSettings):
    """服务器配置"""
    
    host: str = Field(default="0.0.0.0", description="服务器主机")
    port: int = Field(default=8000, description="服务器端口")
    workers: int = Field(default=1, description="工作进程数")
    reload: bool = Field(default=False, description="是否自动重载")
    log_level: str = Field(default="info", description="日志级别")


class Settings(BaseSettings):
    """应用主配置"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_nested_delimiter="__",
        extra="ignore"
    )
    
    # 应用信息
    app_name: str = Field(default="索克生活认证服务", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本")
    debug: bool = Field(default=False, description="调试模式")
    environment: str = Field(default="development", description="运行环境")
    
    # 子配置
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    jwt: JWTSettings = Field(default_factory=JWTSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    server: ServerSettings = Field(default_factory=ServerSettings)
    
    # CORS配置
    cors_origins: List[str] = Field(default=["*"], description="CORS允许的源")
    cors_methods: List[str] = Field(default=["*"], description="CORS允许的方法")
    cors_headers: List[str] = Field(default=["*"], description="CORS允许的头部")
    
    # 监控配置
    enable_metrics: bool = Field(default=True, description="是否启用指标收集")
    metrics_port: int = Field(default=9090, description="指标端口")
    
    # OAuth配置
    oauth_providers: Dict[str, Dict[str, Any]] = Field(
        default_factory=lambda: {
            "google": {
                "client_id": "",
                "client_secret": "",
                "redirect_uri": "",
            },
            "wechat": {
                "app_id": "",
                "app_secret": "",
                "redirect_uri": "",
            },
        },
        description="OAuth提供商配置"
    )
    
    @validator("environment")
    def validate_environment(cls, v: str) -> str:
        """验证环境配置"""
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
        return self.environment == "testing"


@lru_cache()
def get_settings() -> Settings:
    """获取应用配置单例"""
    return Settings() 