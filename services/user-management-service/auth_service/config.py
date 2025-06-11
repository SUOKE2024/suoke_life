"""
认证服务配置模块

提供认证服务的配置管理功能
"""

import os
from typing import Any, Dict, Optional

__version__ = "0.1.0"
__author__ = "索克生活团队"

# 导出主要类和函数
__all__ = [
    "AuthConfig",
    "get_auth_config",
    "DEFAULT_CONFIG"
]


class AuthConfig:
    """认证配置类"""
    
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        self.config = config_dict or self._load_default_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置"""
        return {
            "jwt": {
                "secret_key": os.getenv("JWT_SECRET_KEY", "suoke-life-secret-key"),
                "algorithm": "HS256",
                "expire_hours": 24,
                "refresh_expire_days": 7
            },
            "password": {
                "min_length": 8,
                "require_uppercase": True,
                "require_lowercase": True,
                "require_numbers": True,
                "require_special_chars": False,
                "salt": "suoke_life_salt"
            },
            "session": {
                "timeout_minutes": 30,
                "max_concurrent_sessions": 5,
                "remember_me_days": 30
            },
            "rate_limiting": {
                "login_attempts_per_minute": 5,
                "password_reset_attempts_per_hour": 3,
                "registration_attempts_per_hour": 10
            },
            "security": {
                "enable_2fa": False,
                "enable_captcha": False,
                "enable_email_verification": True,
                "enable_phone_verification": False
            },
            "database": {
                "connection_string": os.getenv("AUTH_DB_URL", "sqlite:///auth.db"),
                "pool_size": 10,
                "max_overflow": 20,
                "pool_timeout": 30
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "auth_service.log",
                "max_bytes": 10485760,  # 10MB
                "backup_count": 5
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split(".")
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        keys = key.split(".")
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def update(self, config_dict: Dict[str, Any]) -> None:
        """更新配置"""
        self._deep_update(self.config, config_dict)
    
    def _deep_update(self, base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> None:
        """深度更新字典"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.config.copy()
    
    def validate(self) -> bool:
        """验证配置"""
        required_keys = [
            "jwt.secret_key",
            "jwt.algorithm",
            "password.min_length",
            "database.connection_string"
        ]
        
        for key in required_keys:
            if self.get(key) is None:
                raise ValueError(f"缺少必需的配置项: {key}")
        
        # 验证JWT密钥长度
        secret_key = self.get("jwt.secret_key")
        if len(secret_key) < 32:
            raise ValueError("JWT密钥长度至少需要32个字符")
        
        # 验证密码最小长度
        min_length = self.get("password.min_length")
        if min_length < 6:
            raise ValueError("密码最小长度不能少于6个字符")
        
        return True


# 默认配置实例
DEFAULT_CONFIG = AuthConfig()

# 全局配置实例
_auth_config = None


def get_auth_config() -> AuthConfig:
    """获取认证配置实例"""
    global _auth_config
    if _auth_config is None:
        _auth_config = AuthConfig()
    return _auth_config


def load_config_from_file(file_path: str) -> AuthConfig:
    """从文件加载配置"""
    import json
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        return AuthConfig(config_dict)
    except FileNotFoundError:
        raise FileNotFoundError(f"配置文件未找到: {file_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"配置文件格式错误: {e}")


def load_config_from_env() -> AuthConfig:
    """从环境变量加载配置"""
    config = AuthConfig()
    
    # JWT配置
    if os.getenv("JWT_SECRET_KEY"):
        config.set("jwt.secret_key", os.getenv("JWT_SECRET_KEY"))
    if os.getenv("JWT_ALGORITHM"):
        config.set("jwt.algorithm", os.getenv("JWT_ALGORITHM"))
    if os.getenv("JWT_EXPIRE_HOURS"):
        config.set("jwt.expire_hours", int(os.getenv("JWT_EXPIRE_HOURS")))
    
    # 数据库配置
    if os.getenv("AUTH_DB_URL"):
        config.set("database.connection_string", os.getenv("AUTH_DB_URL"))
    
    # 日志配置
    if os.getenv("LOG_LEVEL"):
        config.set("logging.level", os.getenv("LOG_LEVEL"))
    
    return config


def main() -> None:
    """主函数"""
    config = get_auth_config()
    print("认证服务配置:")
    print(f"JWT算法: {config.get('jwt.algorithm')}")
    print(f"密码最小长度: {config.get('password.min_length')}")
    print(f"会话超时: {config.get('session.timeout_minutes')}分钟")


if __name__ == "__main__":
    main() 