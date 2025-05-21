#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置管理模块

负责加载、验证和提供服务配置。支持从环境变量、配置文件等多种来源加载配置。
"""

import os
import json
import yaml
from typing import Any, Dict, Optional
from pathlib import Path

from pkg.utils.exceptions import ConfigurationError

# 默认配置路径
DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.yaml")


class Config:
    """配置管理类，负责加载和提供服务配置"""
    
    _instance = None
    
    def __new__(cls, config_path: str = None):
        """单例模式实现，确保全局只有一个配置实例"""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config_path: str = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        # 避免重复初始化
        if self._initialized:
            return
            
        self._config_path = config_path or os.environ.get("CONFIG_PATH", DEFAULT_CONFIG_PATH)
        self._config = {}
        self._env_prefix = "LOOK_SERVICE_"
        self._load_config()
        self._override_from_env()
        self._validate_config()
        self._initialized = True
    
    def _load_config(self) -> None:
        """
        从配置文件加载配置
        
        Raises:
            ConfigurationError: 当配置文件不存在或格式错误时
        """
        try:
            config_path = Path(self._config_path)
            if not config_path.exists():
                raise ConfigurationError(f"配置文件不存在: {self._config_path}")
                
            if config_path.suffix in ['.yaml', '.yml']:
                with open(config_path, 'r', encoding='utf-8') as f:
                    self._config = yaml.safe_load(f)
            elif config_path.suffix == '.json':
                with open(config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            else:
                raise ConfigurationError(f"不支持的配置文件格式: {config_path.suffix}")
                
        except (yaml.YAMLError, json.JSONDecodeError) as e:
            raise ConfigurationError(f"配置文件格式错误: {str(e)}")
        except Exception as e:
            raise ConfigurationError(f"加载配置文件失败: {str(e)}")
    
    def _override_from_env(self) -> None:
        """从环境变量覆盖配置值"""
        for env_name, env_value in os.environ.items():
            if env_name.startswith(self._env_prefix):
                # 移除前缀并转换为小写
                config_key = env_name[len(self._env_prefix):].lower()
                # 将点分隔的键转换为嵌套字典访问
                keys = config_key.split('_')
                self._set_nested_config(keys, env_value)
    
    def _set_nested_config(self, keys: list, value: str) -> None:
        """
        设置嵌套配置值
        
        Args:
            keys: 嵌套键列表
            value: 配置值
        """
        # 尝试转换值类型
        try:
            # 尝试作为JSON解析
            parsed_value = json.loads(value)
        except json.JSONDecodeError:
            # 如果不是有效的JSON，保留原始字符串
            parsed_value = value
            
        # 递归设置嵌套配置
        current = self._config
        for i, key in enumerate(keys):
            if i == len(keys) - 1:
                # 最后一个键，设置值
                current[key] = parsed_value
            else:
                # 确保中间节点存在
                if key not in current or not isinstance(current[key], dict):
                    current[key] = {}
                current = current[key]
    
    def _validate_config(self) -> None:
        """
        验证配置的有效性
        
        Raises:
            ConfigurationError: 当必要配置缺失或无效时
        """
        required_keys = [
            "server.host",
            "server.port",
            "server.debug",
            "logging.level",
            "database.uri",
            "models.face_analysis.path",
            "models.body_analysis.path"
        ]
        
        for key_path in required_keys:
            keys = key_path.split('.')
            value = self.get(key_path)
            if value is None:
                raise ConfigurationError(f"缺少必要配置: {key_path}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key_path: 以点分隔的配置键路径，如 'server.port'
            default: 当配置不存在时返回的默认值
            
        Returns:
            配置值或默认值
        """
        keys = key_path.split('.')
        value = self._config
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_all(self) -> Dict[str, Any]:
        """
        获取所有配置
        
        Returns:
            包含所有配置的字典
        """
        return self._config.copy()
    
    def set(self, key_path: str, value: Any) -> None:
        """
        设置配置值
        
        Args:
            key_path: 以点分隔的配置键路径
            value: 配置值
        """
        keys = key_path.split('.')
        self._set_nested_config(keys, value)


# 全局配置实例
config = Config()


def get_config() -> Config:
    """
    获取全局配置实例
    
    Returns:
        配置实例
    """
    return config 