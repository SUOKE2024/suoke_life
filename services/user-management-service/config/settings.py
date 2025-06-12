"""
索克生活用户管理服务配置
整合认证和用户管理的统一配置
"""

from functools import lru_cache
from typing import Dict, List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings as PydanticBaseSettings


class DatabaseSettings(PydanticBaseSettings):
    """数据库配置"""

    # PostgreSQL配置
    host: str = Field(default="localhost", env="DB_HOST")
    port: int = Field(default=5432, env="DB_PORT")
    username: str = Field(default="suoke_user", env="DB_USERNAME")
    password: str = Field(default="suoke_password", env="DB_PASSWORD")
    database: str = Field(default="suoke_user_management", env="DB_DATABASE")

    # 连接池配置
    pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    pool_timeout: int = Field(default=30, env="DB_POOL_TIMEOUT")
    pool_recycle: int = Field(default=3600, env="DB_POOL_RECYCLE")

    # SSL配置
    ssl_mode: str = Field(default="prefer", env="DB_SSL_MODE")

    @property
    def url(self) -> str:
        """数据库连接URL"""
        return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

    @property
    def sync_url(self) -> str:
        """同步数据库连接URL"""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


class RedisSettings(PydanticBaseSettings):
    """Redis配置"""

    host: str = Field(default="localhost", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    database: int = Field(default=0, env="REDIS_DATABASE")

    # 连接池配置
    max_connections: int = Field(default=20, env="REDIS_MAX_CONNECTIONS")
    retry_on_timeout: bool = Field(default=True, env="REDIS_RETRY_ON_TIMEOUT")
    socket_timeout: int = Field(default=5, env="REDIS_SOCKET_TIMEOUT")

    @property
    def url(self) -> str:
        """Redis连接URL"""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.database}"
        return f"redis://{self.host}:{self.port}/{self.database}"


class AuthSettings(PydanticBaseSettings):
    """认证配置"""

    # JWT配置
    secret_key: str = Field(
        default="your-secret-key-change-in-production", env="JWT_SECRET_KEY"
    )
    algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    refresh_token_expire_days: int = Field(
        default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS"
    )

    # 密码配置
    password_min_length: int = Field(default=8, env="PASSWORD_MIN_LENGTH")
    password_require_uppercase: bool = Field(
        default=True, env="PASSWORD_REQUIRE_UPPERCASE"
    )
    password_require_lowercase: bool = Field(
        default=True, env="PASSWORD_REQUIRE_LOWERCASE"
    )
    password_require_numbers: bool = Field(default=True, env="PASSWORD_REQUIRE_NUMBERS")
    password_require_special: bool = Field(default=True, env="PASSWORD_REQUIRE_SPECIAL")

    # 登录安全配置
    max_login_attempts: int = Field(default=5, env="MAX_LOGIN_ATTEMPTS")
    lockout_duration_minutes: int = Field(default=15, env="LOCKOUT_DURATION_MINUTES")

    # MFA配置
    mfa_issuer: str = Field(default="索克生活", env="MFA_ISSUER")
    mfa_enabled: bool = Field(default=False, env="MFA_ENABLED")

    # OAuth配置
    oauth_providers: Dict[str, Dict[str, str]] = Field(
        default={
            "google": {"client_id": "", "client_secret": "", "redirect_uri": ""},
            "wechat": {"app_id": "", "app_secret": "", "redirect_uri": ""},
        },
        env="OAUTH_PROVIDERS",
    )


class ServerSettings(PydanticBaseSettings):
    """服务器配置"""

    host: str = Field(default="0.0.0.0", env="SERVER_HOST")
    port: int = Field(default=8000, env="SERVER_PORT")
    workers: int = Field(default=1, env="SERVER_WORKERS")
    log_level: str = Field(default="info", env="SERVER_LOG_LEVEL")
    reload: bool = Field(default=False, env="SERVER_RELOAD")

    # CORS配置
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"], env="CORS_ORIGINS"
    )
    cors_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"], env="CORS_METHODS"
    )
    cors_headers: List[str] = Field(default=["*"], env="CORS_HEADERS")


class CacheSettings(PydanticBaseSettings):
    """缓存配置"""

    # 用户缓存配置
    user_cache_ttl: int = Field(default=3600, env="USER_CACHE_TTL")  # 1小时
    session_cache_ttl: int = Field(default=1800, env="SESSION_CACHE_TTL")  # 30分钟

    # 限流配置
    rate_limit_enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")  # 秒


class MonitoringSettings(PydanticBaseSettings):
    """监控配置"""

    # 健康检查配置
    health_check_enabled: bool = Field(default=True, env="HEALTH_CHECK_ENABLED")
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")

    # 指标配置
    metrics_enabled: bool = Field(default=True, env="METRICS_ENABLED")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")

    # 日志配置
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT"
    )

    # Sentry配置
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    sentry_environment: str = Field(default="development", env="SENTRY_ENVIRONMENT")


class Settings(PydanticBaseSettings):
    """主配置类"""

    # 基本配置
    app_name: str = Field(default="索克生活用户管理服务", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")

    # 子配置
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    auth: AuthSettings = AuthSettings()
    server: ServerSettings = ServerSettings()
    cache: CacheSettings = CacheSettings()
    monitoring: MonitoringSettings = MonitoringSettings()

    # API配置
    api_prefix: str = Field(default="/api/v1", env="API_PREFIX")
    docs_url: str = Field(default="/docs", env="DOCS_URL")
    redoc_url: str = Field(default="/redoc", env="REDOC_URL")

    @validator("environment")
    def validate_environment(cls, v):
        """验证环境配置"""
        allowed_envs = ["development", "testing", "staging", "production"]
        if v not in allowed_envs:
            raise ValueError(f"环境必须是以下之一: {allowed_envs}")
        return v

    @validator("debug")
    def validate_debug(cls, v, values):
        """验证调试模式"""
        if values.get("environment") == "production" and v:
            raise ValueError("生产环境不能启用调试模式")
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    return Settings()


# 导出配置实例
settings = get_settings()

# 导出所有配置类
__all__ = [
    "Settings",
    "DatabaseSettings",
    "RedisSettings",
    "AuthSettings",
    "ServerSettings",
    "CacheSettings",
    "MonitoringSettings",
    "get_settings",
    "settings",
]
