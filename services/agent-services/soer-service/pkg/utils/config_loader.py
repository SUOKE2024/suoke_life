#!/usr/bin/env python3
"""
配置加载工具
负责从配置文件加载服务配置
"""

import logging
import os
from typing import Any

import yaml

logger = logging.getLogger(__name__)

# 默认配置
DEFAULT_CONFIG = {
    "service": {
        "name": "soer_service",
        "version": "1.0.0",
        "description": "索儿智能体服务"
    },
    "server": {
        "host": "0.0.0.0",
        "grpc_port": 50054,
        "rest_port": 8054,
        "max_workers": 10
    },
    "grpc": {
        "max_message_length": 10485760,  # 10MB
        "port": 50054
    },
    "rest": {
        "port": 8054
    },
    "metrics": {
        "enabled": True,
        "prometheus": {
            "enabled": True,
            "port": 9098
        }
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": "logs/soer-service.log"
    },
    "models": {
        "health_plan": {
            "type": "chat",
            "model_id": "gpt-4o-mini",
            "endpoint": "https://api.openai.com/v1/chat/completions",
            "max_tokens": 2048,
            "temperature": 0.4
        },
        "lifestyle": {
            "type": "chat",
            "model_id": "gpt-4o-mini",
            "endpoint": "https://api.openai.com/v1/chat/completions",
            "max_tokens": 2048,
            "temperature": 0.5
        },
        "emotional": {
            "type": "chat",
            "model_id": "gpt-4o-mini",
            "endpoint": "https://api.openai.com/v1/chat/completions",
            "max_tokens": 1536,
            "temperature": 0.4
        }
    },
    "database": {
        "type": "postgresql",
        "host": "localhost",
        "port": 5432,
        "database": "soer_service",
        "user": "soer_user",
        "password": "",
        "pool_size": 10,
        "max_overflow": 5
    },
    "cache": {
        "type": "redis",
        "host": "localhost",
        "port": 6379,
        "db": 0,
        "password": "",
        "prefix": "soer:"
    },
    "security": {
        "api_key_header": "X-API-Key",
        "token_header": "Authorization",
        "token_type": "Bearer"
    }
}

# 全局配置对象
_config = None

def load_config(config_path: str) -> dict[str, Any]:
    """
    从文件加载配置

    Args:
        config_path: 配置文件路径

    Returns:
        Dict[str, Any]: 配置字典
    """
    global _config

    # 如果配置已加载，返回缓存的配置
    if _config is not None:
        return _config

    # 初始化为默认配置
    config = DEFAULT_CONFIG.copy()

    # 检查配置文件是否存在
    if not os.path.exists(config_path):
        logger.warning(f"配置文件不存在: {config_path}，使用默认配置")
        _config = config
        return config

    # 尝试加载配置文件
    try:
        with open(config_path, encoding='utf-8') as f:
            file_config = yaml.safe_load(f)

        if file_config:
            # 递归合并配置
            _merge_config(config, file_config)

        logger.info(f"成功加载配置文件: {config_path}")
    except Exception as e:
        logger.error(f"加载配置文件失败: {str(e)}")

    # 加载环境变量覆盖
    _load_env_overrides(config)

    # 缓存配置
    _config = config
    return config

def get_config() -> dict[str, Any]:
    """
    获取当前配置

    Returns:
        Dict[str, Any]: 配置字典
    """
    global _config
    if _config is None:
        # 尝试加载默认配置文件
        return load_config('config/config.yaml')
    return _config

def _merge_config(base: dict[str, Any], override: dict[str, Any]) -> None:
    """
    递归合并配置字典

    Args:
        base: 基础配置
        override: 覆盖配置
    """
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _merge_config(base[key], value)
        else:
            base[key] = value

def _load_env_overrides(config: dict[str, Any]) -> None:
    """
    从环境变量加载配置覆盖

    Args:
        config: 配置字典
    """
    # 处理常见配置项的环境变量覆盖
    env_mappings = {
        "SOER_GRPC_PORT": ("grpc", "port", int),
        "SOER_REST_PORT": ("rest", "port", int),
        "SOER_DB_HOST": ("database", "host", str),
        "SOER_DB_PORT": ("database", "port", int),
        "SOER_DB_NAME": ("database", "database", str),
        "SOER_DB_USER": ("database", "user", str),
        "SOER_DB_PASSWORD": ("database", "password", str),
        "SOER_REDIS_HOST": ("cache", "host", str),
        "SOER_REDIS_PORT": ("cache", "port", int),
        "SOER_REDIS_PASSWORD": ("cache", "password", str),
        "SOER_LOG_LEVEL": ("logging", "level", str),
        "SOER_METRICS_ENABLED": ("metrics", "enabled", lambda v: v.lower() == "true"),
        "SOER_OPENAI_API_KEY": ("models", "api_key", str)
    }

    for env_var, (section, key, converter) in env_mappings.items():
        if env_var in os.environ:
            try:
                value = converter(os.environ[env_var])

                # 支持嵌套部分
                if isinstance(section, str):
                    if section not in config:
                        config[section] = {}
                    config[section][key] = value
                else:
                    # 处理多级嵌套
                    current = config
                    for s in section[:-1]:
                        if s not in current:
                            current[s] = {}
                        current = current[s]
                    current[section[-1]][key] = value

                logger.debug(f"从环境变量加载配置: {env_var} -> {section}.{key} = {value}")
            except Exception as e:
                logger.warning(f"处理环境变量配置失败 {env_var}: {str(e)}")

def reload_config(config_path: str = None) -> dict[str, Any]:
    """
    重新加载配置

    Args:
        config_path: 配置文件路径，如果为None则使用之前的路径

    Returns:
        Dict[str, Any]: 更新后的配置字典
    """
    global _config

    # 重置配置
    _config = None

    # 使用提供的路径或默认路径
    path = config_path or 'config/config.yaml'
    return load_config(path)

def get_config_value(path: str, default: Any = None) -> Any:
    """
    获取配置项的值

    Args:
        path: 配置项路径，使用点分隔，如"server.grpc_port"
        default: 如果配置项不存在，返回的默认值

    Returns:
        Any: 配置项的值
    """
    config = get_config()
    keys = path.split('.')

    current = config
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default

    return current
