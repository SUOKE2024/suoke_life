#!/usr/bin/env python3

"""
配置加载工具
"""

import logging
import os
import sys
from typing import Any

import yaml

# 初始化日志
logger = logging.getLogger(__name__)

# 默认配置
DEFAULT_CONFIG = {
    "app": {
        "name": "corn-maze-service",
        "version": "1.0.0"
    },
    "grpc": {
        "port": 50057,
        "max_workers": 10,
        "max_concurrent_rpcs": 100,
        "max_message_length": 1024 * 1024 * 10  # 10MB
    },
    "metrics": {
        "enabled": True,
        "port": 51057
    },
    "health": {
        "enabled": True,
        "port": 51058
    },
    "db": {
        "path": "data/maze.db",
        "pool_size": 10,
        "timeout": 30,
        "journal_mode": "WAL"
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": "logs/corn-maze-service.log",
        "max_size": 10485760,  # 10MB
        "backup_count": 5,
        "stdout": True
    }
}

# 加载的当前配置
_current_config = {}


def get_config() -> dict[str, Any]:
    """
    获取当前配置，如果配置未加载则加载配置
    
    Returns:
        Dict: 配置字典
    """
    global _current_config

    if not _current_config:
        _current_config = load_config()

    return _current_config


def load_config() -> dict[str, Any]:
    """
    从不同来源加载配置，优先级从高到低：
    1. 环境变量
    2. 命令行参数
    3. 配置文件
    4. 默认配置
    
    Returns:
        Dict: 配置字典
    """
    config = DEFAULT_CONFIG.copy()

    # 从配置文件加载
    config_file = os.environ.get("CONFIG_FILE", "config/config.yaml")
    config.update(_load_from_file(config_file))

    # 从环境变量加载
    config.update(_load_from_env())

    # 从命令行参数加载
    config.update(_load_from_args())

    # 解析特殊值
    _parse_special_values(config)

    logger.info(f"配置加载完成: {config}")
    return config


def _load_from_file(file_path: str) -> dict[str, Any]:
    """从YAML文件加载配置"""
    try:
        if not os.path.exists(file_path):
            logger.warning(f"配置文件不存在: {file_path}")
            return {}

        with open(file_path, encoding="utf-8") as f:
            config = yaml.safe_load(f)
            logger.info(f"从文件加载配置: {file_path}")
            return config or {}
    except Exception as e:
        logger.error(f"加载配置文件失败: {e!s}")
        return {}


def _load_from_env() -> dict[str, Any]:
    """从环境变量加载配置"""
    env_config = {}

    # 映射环境变量到配置项
    mappings = {
        "GRPC_PORT": "grpc.port",
        "GRPC_MAX_WORKERS": "grpc.max_workers",
        "METRICS_ENABLED": "metrics.enabled",
        "METRICS_PORT": "metrics.port",
        "HEALTH_ENABLED": "health.enabled",
        "HEALTH_PORT": "health.port",
        "DB_PATH": "db.path",
        "DB_POOL_SIZE": "db.pool_size",
        "DB_TIMEOUT": "db.timeout",
        "LOGGING_LEVEL": "logging.level",
        "LOGGING_FILE": "logging.file"
    }

    for env_name, config_path in mappings.items():
        env_value = os.environ.get(env_name)
        if env_value is not None:
            # 设置嵌套路径的值
            keys = config_path.split(".")
            current = env_config
            for key in keys[:-1]:
                current = current.setdefault(key, {})

            # 转换值的类型
            value = env_value
            if env_value.lower() in ("true", "false"):
                value = env_value.lower() == "true"
            elif env_value.isdigit():
                value = int(env_value)

            current[keys[-1]] = value

    return env_config


def _load_from_args() -> dict[str, Any]:
    """从命令行参数加载配置"""
    args_config = {}

    # 解析命令行参数
    # 格式: --key=value 或 --key value
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]

        # 处理 --key=value 格式
        if arg.startswith("--") and "=" in arg:
            key, value = arg[2:].split("=", 1)
            args_config[key] = _parse_value(value)
            i += 1

        # 处理 --key value 格式
        elif arg.startswith("--") and i + 1 < len(args) and not args[i+1].startswith("--"):
            key = arg[2:]
            value = args[i+1]
            args_config[key] = _parse_value(value)
            i += 2

        # 处理 --flag 格式（布尔标志）
        elif arg.startswith("--"):
            key = arg[2:]
            args_config[key] = True
            i += 1

        else:
            i += 1

    return args_config


def _parse_value(value: str) -> Any:
    """解析字符串值为适当的类型"""
    if value.lower() in ("true", "false"):
        return value.lower() == "true"

    if value.isdigit():
        return int(value)

    try:
        return float(value)
    except ValueError:
        return value


def _parse_special_values(config: dict[str, Any]) -> None:
    """解析配置中的特殊值"""
    # 确保数据目录存在
    if "db" in config and "path" in config["db"]:
        db_path = config["db"]["path"]
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # 确保日志目录存在
    if "logging" in config and "file" in config["logging"]:
        log_file = config["logging"]["file"]
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)


def get_value(key: str, default: Any = None) -> Any:
    """
    获取配置值
    
    Args:
        key: 配置键，支持点符号路径，如 'db.path'
        default: 默认值
        
    Returns:
        Any: 配置值
    """
    config = get_config()
    keys = key.split(".")

    current = config
    for k in keys:
        if isinstance(current, dict) and k in current:
            current = current[k]
        else:
            return default

    return current
