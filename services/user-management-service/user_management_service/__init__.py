"""
索克生活用户管理服务
整合认证和用户管理功能的统一服务包
"""

__version__ = "1.0.0"
__author__ = "索克生活团队"
__description__ = "用户管理服务 - 整合认证和用户数据管理功能"

# 导出主要组件
from .auth_service import *
from .user_service import *

__all__ = [
    "__version__",
    "__author__", 
    "__description__"
] 