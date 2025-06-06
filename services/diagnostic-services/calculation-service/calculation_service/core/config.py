"""
config - 索克生活项目模块
"""

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings
from typing import List

"""
配置管理

管理算诊微服务的配置参数
"""



class Settings(BaseSettings):
    """应用配置"""
    
    # 基本配置
    SERVICE_NAME: str = Field(default="calculation-service", description="服务名称")
    VERSION: str = Field(default="1.0.0", description="版本号")
    DEBUG: bool = Field(default=False, description="调试模式")
    
    # 服务器配置
    HOST: str = Field(default="0.0.0.0", description="服务器地址")
    PORT: int = Field(default=8005, description="服务器端口")
    
    # 日志配置
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日志格式"
    )
    
    # 数据库配置
    DATABASE_URL: str = Field(
        default="postgresql://user:password@localhost/calculation_db",
        description="数据库连接URL"
    )
    REDIS_URL: str = Field(
        default="redis://localhost:6379",
        description="Redis连接URL"
    )
    MONGODB_URL: str = Field(
        default="mongodb://localhost:27017/calculation_db",
        description="MongoDB连接URL"
    )
    
    # 安全配置
    SECRET_KEY: str = Field(
        default="your-secret-key-here",
        description="密钥"
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["*"],
        description="允许的主机"
    )
    
    # 算诊配置
    TIMEZONE: str = Field(default="Asia/Shanghai", description="时区")
    ASTRONOMICAL_DATA_PATH: str = Field(
        default="/data/astronomical",
        description="天文数据路径"
    )
    
    # 机器学习配置
    MODEL_PATH: str = Field(default="/models", description="模型路径")
    MODEL_VERSION: str = Field(default="v1.0.0", description="模型版本")
    
    # 缓存配置
    CACHE_TTL: int = Field(default=3600, description="缓存过期时间(秒)")
    CACHE_PREFIX: str = Field(default="calc:", description="缓存前缀")
    
    # 限流配置
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, description="每分钟请求限制")
    RATE_LIMIT_PER_HOUR: int = Field(default=1000, description="每小时请求限制")
    
    # 监控配置
    ENABLE_METRICS: bool = Field(default=True, description="启用指标监控")
    METRICS_PORT: int = Field(default=9090, description="指标监控端口")
    
    # 外部服务配置
    USER_SERVICE_URL: str = Field(
        default="http://user-service:8001",
        description="用户服务URL"
    )
    HEALTH_DATA_SERVICE_URL: str = Field(
        default="http://health-data-service:8002",
        description="健康数据服务URL"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """获取配置实例"""
    return Settings()

# 创建全局配置实例
settings = get_settings()
# 数据库连接池优化配置
DATABASE_POOL_CONFIG = {
    "pool_size": 20,           # 连接池大小
    "max_overflow": 30,        # 最大溢出连接数
    "pool_timeout": 30,        # 获取连接超时时间
    "pool_recycle": 3600,      # 连接回收时间
    "pool_pre_ping": True,     # 连接预检查
}
