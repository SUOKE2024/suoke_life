#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理工具
"""

import os
import yaml
from typing import Dict, Any


def load_config(config_path: str) -> Dict[str, Any]:
    """
    加载配置文件并解析环境变量
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        解析后的配置字典
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    # 读取配置文件
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 递归解析环境变量
    config = _parse_env_vars(config)
    
    return config


def _parse_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    递归解析配置中的环境变量占位符 ${ENV_VAR}
    
    Args:
        config: 配置字典
        
    Returns:
        解析后的配置字典
    """
    if isinstance(config, dict):
        return {k: _parse_env_vars(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [_parse_env_vars(v) for v in config]
    elif isinstance(config, str) and config.startswith('${') and config.endswith('}'):
        # 提取环境变量名
        env_var = config[2:-1]
        # 获取环境变量值，如果不存在则保持原样
        return os.environ.get(env_var, config)
    else:
        return config


def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    合并两个配置字典，override_config的值会覆盖base_config
    
    Args:
        base_config: 基础配置
        override_config: 覆盖配置
        
    Returns:
        合并后的配置字典
    """
    result = base_config.copy()
    
    for key, value in override_config.items():
        # 如果两个配置都包含相同的键且都是字典，则递归合并
        if (
            key in result and 
            isinstance(result[key], dict) and 
            isinstance(value, dict)
        ):
            result[key] = merge_configs(result[key], value)
        else:
            # 否则直接覆盖或添加
            result[key] = value
            
    return result