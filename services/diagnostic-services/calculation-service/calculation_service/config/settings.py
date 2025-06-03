"""
算诊服务配置设置
"""

from typing import List
from functools import lru_cache
from pydantic import BaseSettings

class Settings(BaseSettings):
    """应用配置"""
    
    # 基本配置
    APP_NAME: str = "calculation-service"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 服务配置
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    
    # CORS配置
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080"
    ]
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 算法配置
    ENABLE_CACHE: bool = True
    CACHE_TTL: int = 3600  # 缓存时间（秒）
    
    # 数据配置
    DATA_PATH: str = "./data"
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    return Settings() 