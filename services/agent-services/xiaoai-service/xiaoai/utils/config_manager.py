#!/usr/bin/env python3
"""
配置管理模块 - 提供配置文件加载和监控功能
"""

import threading
import time
from pathlib import Path
from typing import Any

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_dir: str = "config", watch_interval: float = 1.0):
        self.config_dir = Path(config_dir)
        self.watch_interval = watch_interval
        self.config_data: dict[str, Any] = {}
        self.file_timestamps: dict[str, float] = {}
        self.watch_thread: threading.Thread | None = None
        self._lock = threading.Lock()

    def load_config(self, config_name: str) -> dict[str, Any]:
        """加载配置文件"""
        config_file = self.config_dir / f"{config_name}.yaml"

        if not config_file.exists():
            return {}

        return self._load_yaml_config(str(config_file))

    def _load_yaml_config(self, file_path: str) -> dict[str, Any]:
        """加载YAML配置文件"""
        if not YAML_AVAILABLE:
            return {}

        try:
            with open(file_path, encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}

            with self._lock:
                self.config_data[file_path] = config
                self.file_timestamps[file_path] = Path(file_path).stat().st_mtime

            return config
        except Exception as e:
            print(f"Error loading config {file_path}: {e}")
            return {}

    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        with self._lock:
            for config in self.config_data.values():
                if key in config:
                    return config[key]
        return default

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
                    if Path(file_path).exists():
                        current_mtime = Path(file_path).stat().st_mtime
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


def get_config_manager() -> ConfigManager:
    """获取配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        with _config_lock:
            if _config_manager is None:
                _config_manager = ConfigManager()
    return _config_manager


def load_config(config_name: str) -> dict[str, Any]:
    """加载配置的便捷函数"""
    return get_config_manager().load_config(config_name)


def get_config(key: str, default: Any = None) -> Any:
    """获取配置值的便捷函数"""
    return get_config_manager().get_config(key, default)
