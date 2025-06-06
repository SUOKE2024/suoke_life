"""
config_manager - 索克生活项目模块
"""

from dataclasses import dataclass
from typing import Any
import json
import os
import threading
import time
import yaml

#!/usr/bin/env python3

"""
配置管理模块 - 提供统一的配置管理功能
"""




@dataclass
class ConfigSource:
    """配置来源信息"""
    type: str  # "file", "env", "default"
    path: str | None = None
    key: str | None = None


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_dir: str = "config", env: str = "development"):
        self.config_dir = config_dir
        self.env = env
        self.config = {}
        self.sources = {}
        self.watch_interval = 5.0
        self.watch_thread = None
        self.file_timestamps = {}
        self._lock = threading.RLock()

    def load_config(self):
        """加载配置"""
        with self._lock:
            self._load_default_config()
            self._load_file_config()
            self._load_env_config()

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        with self._lock:
            keys = key.split('.')
            value = self.config

            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default

            return value

    def set(self, key: str, value: Any, source: ConfigSource | None = None):
        """设置配置值"""
        with self._lock:
            keys = key.split('.')
            config = self.config

            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]

            config[keys[-1]] = value

            if source:
                self.sources[key] = source

    def _load_default_config(self):
        """加载默认配置"""
        default_config = {
            "service": {
                "name": "xiaoai-service",
                "version": "1.0.0",
                "port": 8001,
                "host": "0.0.0.0"
            },
            "database": {
                "url": "postgresql://localhost:5432/xiaoai",
                "pool_size": 10,
                "max_overflow": 20
            },
            "ai": {
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 2000
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }

        self._merge_config(default_config)

    def _load_file_config(self):
        """加载文件配置"""
        common_file = os.path.join(self.config_dir, "common.yaml")
        env_file = os.path.join(self.config_dir, f"{self.env}.yaml")

        for file_path in [common_file, env_file]:
            if os.path.exists(file_path):
                self._load_yaml_config(file_path)

    def _load_yaml_config(self, file_path: str):
        """加载YAML配置文件"""
        try:
            with open(file_path, encoding='utf-8') as f:
                config_data = yaml.safe_load(f)

            if config_data:
                self._merge_config(config_data)
                self.file_timestamps[file_path] = os.path.getmtime(file_path)

        except Exception as e:
            print(f"Failed to load config file {file_path}: {e}")

    def _load_env_config(self):
        """加载环境变量配置"""
        prefix = "XIAOAI_"

        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower().replace('_', '.')
                parsed_value = self._parse_env_value(value)

                self.set(config_key, parsed_value, ConfigSource(type="env", key=key))

    def _parse_env_value(self, value: str) -> Any:
        """解析环境变量值"""
        # 尝试解析为JSON
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass

        # 尝试解析为布尔值
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'

        # 尝试解析为数字
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            pass

        # 返回字符串
        return value

    def _merge_config(self, new_config: dict[str, Any]):
        """合并配置"""
        def merge_dict(target: dict[str, Any], source: dict[str, Any]):
            for key, value in source.items():
                if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                    merge_dict(target[key], value)
                else:
                    target[key] = value

        merge_dict(self.config, new_config)

    def start_watching(self):
        """开始监控配置文件变化"""
        if self.watch_thread is None or not self.watch_thread.is_alive():
            self.watch_thread = threading.Thread(target=self._watch_files, daemon=True)
            self.watch_thread.start()

    def _watch_files(self):
        """监控文件变化"""
        while True:
            try:
                for file_path, last_mtime in self.file_timestamps.items():
                    if os.path.exists(file_path):
                        current_mtime = os.path.getmtime(file_path)
                        if current_mtime > last_mtime:
                            print(f"Config file {file_path} changed, reloading...")
                            self._load_yaml_config(file_path)

                time.sleep(self.watch_interval)

            except Exception as e:
                print(f"Error watching config files: {e}")
                time.sleep(self.watch_interval)


# 全局配置管理器实例
_config_manager: ConfigManager | None = None
_config_lock = threading.Lock()


def get_config_manager(config_dir: str = "config", env: str = "development") -> ConfigManager:
    """获取配置管理器实例"""
    global _config_manager

    with _config_lock:
        if _config_manager is None:
            _config_manager = ConfigManager(config_dir=config_dir, env=env)
            _config_manager.load_config()

        return _config_manager


def get_config(key: str, default: Any = None) -> Any:
    """获取配置值的便捷函数"""
    return get_config_manager().get(key, default)


def set_config(key: str, value: Any):
    """设置配置值的便捷函数"""
    get_config_manager().set(key, value)
