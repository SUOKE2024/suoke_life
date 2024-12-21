from .settings import Settings
import os

class TestSettings(Settings):
    """测试环境配置类"""
    
    # 应用配置
    APP_ENV: str = "testing"
    APP_DEBUG: bool = True
    
    # 测试数据库配置
    DB_DATABASE: str = "suoke_test"
    
    # 测试JWT配置
    JWT_SECRET_KEY: str = "test_secret_key"
    
    # 测试日志配置
    LOG_LEVEL: str = "DEBUG"
    LOG_PATH: str = "tests/logs"
    
    class Config:
        """配置类设置"""
        env_file = os.path.join(os.path.dirname(__file__), "test.env")
        case_sensitive = True 