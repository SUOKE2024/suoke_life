"""
算诊服务配置设置
索克生活 - 传统中医算诊微服务配置
"""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 基本配置
    APP_NAME: str = "calculation-service"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # 服务配置
    HOST: str = "0.0.0.0"
    PORT: int = 8003

    # CORS配置
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "http://localhost:19006",  # Expo开发服务器
    ]

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # 算法配置
    ENABLE_CACHE: bool = True
    CACHE_TTL: int = 3600  # 缓存时间（秒）
    CACHE_MAX_SIZE: int = 1000  # 最大缓存条目数

    # 限流配置
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_MAX_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # 数据配置
    DATA_PATH: str = "./data"

    # 安全配置
    SECRET_KEY: str = "suoke-calculation-service-secret-key-2024"

    # 数据库配置（可选）
    DATABASE_URL: str | None = None
    REDIS_URL: str | None = None

    # 监控配置
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090

    # 算诊特定配置
    TIMEZONE: str = "Asia/Shanghai"
    DEFAULT_LOCATION: str = "北京"  # 默认地理位置
    ENABLE_ASTRONOMICAL_CALC: bool = True  # 启用天文计算

    # 算法精度配置
    CALCULATION_PRECISION: int = 6  # 计算精度（小数位数）
    ENABLE_ADVANCED_ALGORITHMS: bool = True  # 启用高级算法

    class Config:
        """Pydantic配置"""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    return Settings()
