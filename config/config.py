#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小艾智能体配置管理
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path

class Config:
    """配置管理类"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or "config/config.yaml"
        self.config_data = {}
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        try:
            config_path = Path(self.config_file)
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config_data = yaml.safe_load(f) or {}
            else:
                # 使用默认配置
                self.config_data = self.get_default_config()
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            self.config_data = self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "server": {
                "host": "localhost",
                "port": 8000,
                "debug": True
            },
            "database": {
                "type": "mongodb",
                "host": "localhost",
                "port": 27017,
                "name": "xiaoai_db"
            },
            "accessibility": {
                "enabled": True,
                "service_url": "http://localhost:50051",
                "timeout": 30
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self.config_data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split('.')
        config = self.config_data
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    @property
    def server_host(self) -> str:
        return self.get("server.host", "localhost")
    
    @property
    def server_port(self) -> int:
        return self.get("server.port", 8000)
    
    @property
    def database_url(self) -> str:
        host = self.get("database.host", "localhost")
        port = self.get("database.port", 27017)
        name = self.get("database.name", "xiaoai_db")
        return f"mongodb://{host}:{port}/{name}"
    
    @property
    def accessibility_enabled(self) -> bool:
        return self.get("accessibility.enabled", True)
    
    @property
    def accessibility_url(self) -> str:
        return self.get("accessibility.service_url", "http://localhost:50051")

# 全局配置实例
_config_instance: Optional[Config] = None

def get_config() -> Config:
    """获取全局配置实例"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance 