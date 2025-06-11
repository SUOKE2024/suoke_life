from typing import Any, Dict, List, Optional, Union

"""
__init__ - 索克生活项目模块
"""

"""
索克生活API网关

提供微服务架构的API网关功能
"""

__version__ = "0.1.0"
__author__ = "索克生活团队"

# 简化导入，避免复杂依赖
try:
    from .core.app import create_app
    from .core.config import Settings, get_settings
except ImportError as e:
    print(f"警告: 部分模块导入失败: {e}")
    
    def create_app():
        """应用创建占位符"""
        from fastapi import FastAPI
        return FastAPI(title="索克生活API网关", version=__version__)
    
    class Settings:
        """配置占位符"""
        pass
    
    def get_settings():
        """配置获取占位符"""
        return Settings()

__all__ = ["create_app", "Settings", "get_settings"]
