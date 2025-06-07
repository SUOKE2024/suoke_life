#!/usr/bin/env python3
"""
config_loader - 索克生活项目模块
"""

import os
from pathlib import Path
from typing import Any

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

"""
配置加载器模块 - 提供配置文件加载和环境变量处理功能
"""

class ConfigLoader:
    """配置加载器"""

    def __init__(self, config_path: str | None = None):
        self.config_path = config_path
        self.config: dict[str, Any] = {}

        if config_path:
            self.load_config()

    def load_config(self) -> dict[str, Any]:
        """加载配置文件"""
        if not self.config_path:
            # 尝试查找默认配置文件
            possible_paths = [
                "config.yaml",
                "config.yml",
                "config/config.yaml",
                "config/config.yml"
            ]

            for path in possible_paths:
                if Path(path).exists():
                    self.config_path = path
                    break
            else:
                raise FileNotFoundError("No configuration file found")

        try:
            if not YAML_AVAILABLE:
                raise ImportError("PyYAML is required for YAML config files")

            with open(self.config_path, encoding='utf-8') as f:
                self.config = yaml.safe_load(f) or {}

        except Exception as e:
            print(f"Error loading config from {self.config_path}: {e}")
            self.config = {}

        # 处理环境变量
        self._process_env_vars(self.config)

        return self.config

    def _process_env_vars(self, config_dict: dict[str, Any], prefix: str = ""):
        """递归处理环境变量"""
        for key, value in config_dict.items():
            current_prefix = f"{prefix}_{key}".upper() if prefix else key.upper()

            if isinstance(value, dict):
                self._process_env_vars(value, current_prefix)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        self._process_env_vars(item, f"{current_prefix}_{i}")
            else:
                env_var = os.environ.get(current_prefix)
                if env_var is not None:
                    config_dict[key] = self._parse_env_value(env_var)

    def _parse_env_value(self, value: str) -> Any:
        """解析环境变量值"""
        # 尝试解析为布尔值
        if value.lower() in ("true", "false"):
            return value.lower() == "true"

        # 尝试解析为数字
        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            pass

        # 返回字符串
        return value

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split(".")
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value


# 全局配置实例
_config_instance: ConfigLoader | None = None


def get_config_loader(config_path: str | None = None) -> ConfigLoader:
    """获取配置加载器实例"""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigLoader(config_path)
    return _config_instance


def load_config(config_path: str | None = None) -> dict[str, Any]:
    """加载配置的便捷函数"""
    return get_config_loader(config_path).load_config()


def get_config(key: str, default: Any = None) -> Any:
    """获取配置值的便捷函数"""
    return get_config_loader().get(key, default)
