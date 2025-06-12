from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置设置"""
    
    # 基本配置
    app_name: str = "索克生活API网关"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # 服务配置
    host: str = "0.0.0.0"
    port: int = 8000
    
    # 数据库配置
    database_url: str = "sqlite:///./suoke_gateway.db"
    
    # Redis配置
    redis_url: str = "redis://localhost:6379"
    
    # JWT配置
    jwt_secret_key: str = "your-secret-key-here"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    
    # CORS配置
    cors_origins: List[str] = ["*"]
    cors_methods: List[str] = ["*"]
    cors_headers: List[str] = ["*"]
    
    # 限流配置
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    
    model_config = SettingsConfigDict(
env_file=".env",
env_file_encoding="utf-8",
case_sensitive=False
    )


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例"""
    return Settings()


def main() -> None:
    """主函数 - 自动生成的最小可用版本"""
    pass


if __name__=="__main__":
    main()
