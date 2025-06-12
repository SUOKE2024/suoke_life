"""
settings - 索克生活项目模块
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import BaseSettings, Field, validator

"""
应用配置管理
使用Pydantic Settings进行配置管理
"""

class DatabaseSettings(BaseSettings):
    """数据库配置"""

    # SQLite配置
    sqlite_url: str = Field(
        default = "sqlite + aiosqlite:/// . / data / user_service.db",
        env = "DATABASE_SQLITE_URL"
    )

    # PostgreSQL配置
    postgres_host: str = Field(default = "localhost", env = "POSTGRES_HOST")
    postgres_port: int = Field(default = 5432, env = "POSTGRES_PORT")
    postgres_user: str = Field(default = "postgres", env = "POSTGRES_USER")
    postgres_password: str = Field(default = "", env = "POSTGRES_PASSWORD")
    postgres_db: str = Field(default = "user_service", env = "POSTGRES_DB")

    # 连接池配置
    pool_size: int = Field(default = 10, env = "DB_POOL_SIZE")
    max_overflow: int = Field(default = 20, env = "DB_MAX_OVERFLOW")
    pool_timeout: int = Field(default = 30, env = "DB_POOL_TIMEOUT")
    pool_recycle: int = Field(default = 3600, env = "DB_POOL_RECYCLE")

    # 是否使用PostgreSQL
    use_postgres: bool = Field(default = False, env = "USE_POSTGRES")

    @property
    def database_url(self) -> str:
        """获取数据库连接URL"""
        if self.use_postgres:
            return (
                f"postgresql + asyncpg: //{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port} / {self.postgres_db}"
            )
        return self.sqlite_url

    class Config:
        """TODO: 添加文档字符串"""
        env_prefix = "DB_"

class RedisSettings(BaseSettings):
    """Redis配置"""

    host: str = Field(default = "localhost", env = "REDIS_HOST")
    port: int = Field(default = 6379, env = "REDIS_PORT")
    password: Optional[str] = Field(default = None, env = "REDIS_PASSWORD")
    db: int = Field(default = 0, env = "REDIS_DB")
    max_connections: int = Field(default = 10, env = "REDIS_MAX_CONNECTIONS")

    # 连接配置
    socket_timeout: float = Field(default = 5.0, env = "REDIS_SOCKET_TIMEOUT")
    socket_connect_timeout: float = Field(default = 5.0, env = "REDIS_SOCKET_CONNECT_TIMEOUT")
    retry_on_timeout: bool = Field(default = True, env = "REDIS_RETRY_ON_TIMEOUT")

    # 是否启用Redis
    enabled: bool = Field(default = True, env = "REDIS_ENABLED")

    @property
    def redis_url(self) -> str:
        """获取Redis连接URL"""
        auth = f":{self.password}@" if self.password else ""
        return f"redis: //{auth}{self.host}:{self.port} / {self.db}"

    class Config:
        """TODO: 添加文档字符串"""
        env_prefix = "REDIS_"

class SecuritySettings(BaseSettings):
    """安全配置"""

    # JWT配置
    jwt_secret_key: str = Field(
        default = "your - secret - key - change - in - production",
        env = "JWT_SECRET_KEY"
    )
    jwt_algorithm: str = Field(default = "HS256", env = "JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default = 60, env = "ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default = 7, env = "REFRESH_TOKEN_EXPIRE_DAYS")

    # 密码配置
    password_min_length: int = Field(default = 8, env = "PASSWORD_MIN_LENGTH")
    password_require_uppercase: bool = Field(default = True, env = "PASSWORD_REQUIRE_UPPERCASE")
    password_require_lowercase: bool = Field(default = True, env = "PASSWORD_REQUIRE_LOWERCASE")
    password_require_numbers: bool = Field(default = True, env = "PASSWORD_REQUIRE_NUMBERS")
    password_require_special: bool = Field(default = False, env = "PASSWORD_REQUIRE_SPECIAL")

    # API密钥配置
    api_key_length: int = Field(default = 32, env = "API_KEY_LENGTH")

    # 限流配置
    rate_limit_enabled: bool = Field(default = True, env = "RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default = 100, env = "RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default = 60, env = "RATE_LIMIT_WINDOW")

    @validator("jwt_secret_key")
    def validate_jwt_secret(cls, v):
        """TODO: 添加文档字符串"""
        if len(v) < 32:
            raise ValueError("JWT secret key must be at least 32 characters long")
        return v

    class Config:
        """TODO: 添加文档字符串"""
        env_prefix = "SECURITY_"

class LoggingSettings(BaseSettings):
    """日志配置"""

    level: str = Field(default = "INFO", env = "LOG_LEVEL")
    format: str = Field(
        default = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env = "LOG_FORMAT"
    )

    # 文件日志配置
    file_enabled: bool = Field(default = True, env = "LOG_FILE_ENABLED")
    file_path: str = Field(default = "logs / user_service.log", env = "LOG_FILE_PATH")
    file_max_size: int = Field(default = 10485760, env = "LOG_FILE_MAX_SIZE")  # 10MB
    file_backup_count: int = Field(default = 5, env = "LOG_FILE_BACKUP_COUNT")

    # 结构化日志
    structured: bool = Field(default = True, env = "LOG_STRUCTURED")

    class Config:
        """TODO: 添加文档字符串"""
        env_prefix = "LOG_"

class MonitoringSettings(BaseSettings):
    """监控配置"""

    # Prometheus配置
    prometheus_enabled: bool = Field(default = True, env = "PROMETHEUS_ENABLED")
    prometheus_port: int = Field(default = 8001, env = "PROMETHEUS_PORT")

    # 健康检查配置
    health_check_enabled: bool = Field(default = True, env = "HEALTH_CHECK_ENABLED")
    health_check_interval: int = Field(default = 30, env = "HEALTH_CHECK_INTERVAL")

    # 性能监控
    performance_monitoring: bool = Field(default = True, env = "PERFORMANCE_MONITORING")
    slow_query_threshold: float = Field(default = 1.0, env = "SLOW_QUERY_THRESHOLD")

    class Config:
        """TODO: 添加文档字符串"""
        env_prefix = "MONITORING_"

class CacheSettings(BaseSettings):
    """缓存配置"""

    # 缓存后端类型
    backend: str = Field(default = "redis", env = "CACHE_BACKEND")  # redis 或 memory

    # 缓存TTL配置（秒）
    user_ttl: int = Field(default = 300, env = "CACHE_USER_TTL")
    health_ttl: int = Field(default = 600, env = "CACHE_HEALTH_TTL")
    device_ttl: int = Field(default = 300, env = "CACHE_DEVICE_TTL")

    # 内存缓存配置
    memory_max_size: int = Field(default = 1000, env = "CACHE_MEMORY_MAX_SIZE")

    # 缓存键前缀
    key_prefix: str = Field(default = "user_service", env = "CACHE_KEY_PREFIX")

    class Config:
        """TODO: 添加文档字符串"""
        env_prefix = "CACHE_"

class AppSettings(BaseSettings):
    """应用配置"""

    # 应用基本信息
    name: str = Field(default = "User Service", env = "APP_NAME")
    version: str = Field(default = "1.0.0", env = "APP_VERSION")
    description: str = Field(default = "索克生活用户服务", env = "APP_DESCRIPTION")

    # 服务器配置
    host: str = Field(default = "0.0.0.0", env = "APP_HOST")
    port: int = Field(default = 8000, env = "APP_PORT")
    workers: int = Field(default = 1, env = "APP_WORKERS")

    # 环境配置
    environment: str = Field(default = "development", env = "ENVIRONMENT")
    debug: bool = Field(default = False, env = "DEBUG")

    # CORS配置
    cors_origins: List[str] = Field(
        default = ["http: //localhost:3000", "http: //localhost:8080"],
        env = "CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(default = True, env = "CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: List[str] = Field(
        default = ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        env = "CORS_ALLOW_METHODS"
    )
    cors_allow_headers: List[str] = Field(
        default = [" * "],
        env = "CORS_ALLOW_HEADERS"
    )

    # API配置
    api_prefix: str = Field(default = " / api / v1", env = "API_PREFIX")
    docs_url: Optional[str] = Field(default = " / docs", env = "DOCS_URL")
    redoc_url: Optional[str] = Field(default = " / redoc", env = "REDOC_URL")

    @validator("environment")
    def validate_environment(cls, v):
        """TODO: 添加文档字符串"""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v

    @property
    def is_development(self) -> bool:
        """TODO: 添加文档字符串"""
        return self.environment=="development"

    @property
    def is_production(self) -> bool:
        """TODO: 添加文档字符串"""
        return self.environment=="production"

    class Config:
        """TODO: 添加文档字符串"""
        env_prefix = "APP_"

class Settings(BaseSettings):
    """主配置类"""

    app: AppSettings = AppSettings()
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    security: SecuritySettings = SecuritySettings()
    logging: LoggingSettings = LoggingSettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    cache: CacheSettings = CacheSettings()

    class Config:
        """TODO: 添加文档字符串"""
        env_file = ".env"
        env_file_encoding = "utf - 8"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    return Settings()

# 全局配置实例
settings = get_settings()