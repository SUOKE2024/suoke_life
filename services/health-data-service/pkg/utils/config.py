#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置加载工具
"""

import os
import yaml
import json
from typing import Dict, Any, Optional
from loguru import logger


def load_config(config_path: str) -> Optional[Dict[str, Any]]:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典，如果加载失败则返回None
    """
    logger.info(f"加载配置文件: {config_path}")
    
    if not os.path.exists(config_path):
        logger.error(f"配置文件不存在: {config_path}")
        return None
    
    try:
        # 根据文件扩展名选择加载方式
        file_ext = os.path.splitext(config_path)[1].lower()
        
        if file_ext in ['.yaml', '.yml']:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
        elif file_ext == '.json':
            with open(config_path, 'r', encoding='utf-8') as file:
                config = json.load(file)
        else:
            logger.error(f"不支持的配置文件格式: {file_ext}")
            return None
        
        # 处理环境变量替换
        config = _process_env_vars(config)
        
        return config
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        return None


def _process_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    递归处理配置中的环境变量
    
    Args:
        config: 配置字典
        
    Returns:
        处理后的配置字典
    """
    if isinstance(config, dict):
        return {key: _process_env_vars(value) for key, value in config.items()}
    elif isinstance(config, list):
        return [_process_env_vars(item) for item in config]
    elif isinstance(config, str) and config.startswith('${') and config.endswith('}'):
        # 提取环境变量名称
        env_var = config[2:-1]
        
        # 检查是否指定了默认值，格式为 ${ENV_VAR:default_value}
        default_value = None
        if ':' in env_var:
            env_var, default_value = env_var.split(':', 1)
        
        # 获取环境变量值
        value = os.environ.get(env_var)
        if value is None:
            if default_value is not None:
                logger.debug(f"环境变量 {env_var} 未设置，使用默认值: {default_value}")
                return default_value
            else:
                logger.warning(f"环境变量 {env_var} 未设置且没有默认值")
                return config
        
        return value
    else:
        return config


def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    合并配置
    
    Args:
        base_config: 基础配置
        override_config: 覆盖配置
        
    Returns:
        合并后的配置
    """
    result = base_config.copy()
    
    for key, value in override_config.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    
    return result