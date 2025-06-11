"""
索克生活认证服务

提供用户认证、授权和账户管理功能的微服务。
"""

from typing import Any, Dict, List, Optional, Union

__version__ = "1.0.0"
__author__ = "Song Xu"
__email__ = "song.xu@icloud.com"


class Settings:
    """认证服务设置类"""
    
    def __init__(self):
        self.jwt_secret = "suoke-life-secret-key"
        self.jwt_algorithm = "HS256"
        self.jwt_expire_hours = 24
        self.password_min_length = 8
        self.session_timeout = 30
    
    def get_jwt_config(self) -> Dict[str, Any]:
        """获取JWT配置"""
        return {
            "secret": self.jwt_secret,
            "algorithm": self.jwt_algorithm,
            "expire_hours": self.jwt_expire_hours
        }
    
    def get_password_config(self) -> Dict[str, Any]:
        """获取密码配置"""
        return {
            "min_length": self.password_min_length
        }


# 导出主要类
__all__ = ["Settings"]