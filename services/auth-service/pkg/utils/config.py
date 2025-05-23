#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置加载工具

提供配置文件加载、环境变量解析和配置值获取功能。
"""
import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """配置类，用于读取和访问配置"""
    
    def __init__(self, config_dict: Dict[str, Any]):
        self._config = config_dict
    
    def __getattr__(self, key: str) -> Any:
        """允许通过点号访问配置项"""
        if key in self._config:
            value = self._config[key]
            if isinstance(value, dict):
                return Config(value)
            return value
        return None


def load_config(config_path: Optional[str] = None) -> Config:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径，默认为None（使用项目默认配置文件）
    
    Returns:
        Config: 配置对象
    """
    if config_path is None:
        # 使用默认配置文件路径
        config_path = os.environ.get(
            "CONFIG_PATH", 
            str(Path(__file__).parent.parent.parent / "config" / "default.yaml")
        )
    
    # 读取配置文件
    with open(config_path, "r") as f:
        config_dict = yaml.safe_load(f)
    
    # 解析环境变量
    process_env_vars(config_dict)
    
    return Config(config_dict)


def process_env_vars(config_dict: Dict[str, Any]) -> None:
    """
    处理配置中的环境变量占位符
    
    Args:
        config_dict: 配置字典
    """
    for key, value in config_dict.items():
        if isinstance(value, dict):
            process_env_vars(value)
        elif isinstance(value, str) and "${" in value and "}" in value:
            config_dict[key] = resolve_env_var(value)


def resolve_env_var(value: str) -> Any:
    """
    解析包含环境变量的字符串
    
    Args:
        value: 包含环境变量占位符的字符串，格式：${ENV_VAR:default_value}
    
    Returns:
        Any: 解析后的值
    """
    if not (value.startswith("${") and value.endswith("}")):
        return value
    
    # 提取环境变量名和默认值
    env_var = value[2:-1]  # 去掉${}
    if ":" in env_var:
        env_name, default = env_var.split(":", 1)
    else:
        env_name, default = env_var, ""
    
    # 获取环境变量值，如果不存在则使用默认值
    return os.environ.get(env_name, default) 