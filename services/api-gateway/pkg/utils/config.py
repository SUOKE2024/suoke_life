#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置加载工具，用于解析YAML配置文件并转换为配置对象
"""

import logging
import os
from typing import Any, Dict, Optional, Union

import yaml

from internal.model.config import GatewayConfig


logger = logging.getLogger(__name__)


def _read_yaml_file(file_path: str) -> Dict[str, Any]:
    """
    读取YAML配置文件
    
    Args:
        file_path: YAML文件路径
        
    Returns:
        Dict[str, Any]: 配置字典
        
    Raises:
        FileNotFoundError: 配置文件不存在
        yaml.YAMLError: YAML解析错误
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        logger.error(f"配置文件不存在: {file_path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"YAML解析错误: {e}")
        raise


def _merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    递归合并两个配置字典，override会覆盖base中的值
    
    Args:
        base: 基础配置
        override: 覆盖配置
        
    Returns:
        Dict[str, Any]: 合并后的配置
    """
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge_configs(result[key], value)
        else:
            result[key] = value
            
    return result


def load_config(config_path: str, env_prefix: str = "APIGATEWAY_") -> GatewayConfig:
    """
    加载配置，支持从文件和环境变量加载
    
    Args:
        config_path: 配置文件路径
        env_prefix: 环境变量前缀，用于识别哪些环境变量应该被加载
        
    Returns:
        GatewayConfig: 配置对象
        
    Raises:
        FileNotFoundError: 配置文件不存在
        yaml.YAMLError: YAML解析错误
        ValueError: 配置验证错误
    """
    # 加载配置文件
    config_dict = {}
    if os.path.exists(config_path):
        config_dict = _read_yaml_file(config_path)
    else:
        logger.warning(f"配置文件不存在，使用默认配置: {config_path}")
        
    # 加载环境变量配置
    env_config = _load_from_env(env_prefix)
    
    # 合并配置
    merged_config = _merge_configs(config_dict, env_config)
    
    # 转换为配置对象
    try:
        return GatewayConfig(**merged_config)
    except Exception as e:
        logger.error(f"配置验证错误: {e}")
        raise ValueError(f"配置验证错误: {e}") from e


def _load_from_env(prefix: str) -> Dict[str, Any]:
    """
    从环境变量加载配置
    
    环境变量格式: {prefix}_{配置路径}
    例如: APIGATEWAY_SERVER_REST_PORT=8080
    
    Args:
        prefix: 环境变量前缀
        
    Returns:
        Dict[str, Any]: 环境变量配置
    """
    result = {}
    prefix = prefix.upper()
    
    for key, value in os.environ.items():
        if key.startswith(prefix):
            path = key[len(prefix):].lower().split("_")
            
            # 处理值类型
            typed_value = _parse_env_value(value)
            
            # 构建嵌套字典
            current = result
            for part in path[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
                
            current[path[-1]] = typed_value
            
    return result


def _parse_env_value(value: str) -> Union[str, int, float, bool, list]:
    """
    解析环境变量值为适当的类型
    
    Args:
        value: 环境变量值
        
    Returns:
        Union[str, int, float, bool, list]: 转换后的值
    """
    # 布尔值处理
    if value.lower() in ("true", "yes", "1"):
        return True
    if value.lower() in ("false", "no", "0"):
        return False
    
    # 数字处理
    try:
        if "." in value:
            return float(value)
        else:
            return int(value)
    except ValueError:
        pass
    
    # 列表处理 (逗号分隔)
    if "," in value:
        return [item.strip() for item in value.split(",")]
    
    # 默认为字符串
    return value 