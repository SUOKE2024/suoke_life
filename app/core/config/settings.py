from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用配置
    APP_NAME: str = "索克生活"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_PORT: int = 8000
    
    # 数据库配置
    DB_CONNECTION: str = "mysql"
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_DATABASE: str = "suoke"
    DB_USERNAME: str = "suoke"
    DB_PASSWORD: str = "Ht123!@#"
    
    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    # JWT配置
    JWT_SECRET_KEY: str = "your-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_PATH: str = "logs"
    
    class Config:
        """配置类设置"""
        env_file = os.path.join(os.path.dirname(__file__), ".env")
        case_sensitive = True 