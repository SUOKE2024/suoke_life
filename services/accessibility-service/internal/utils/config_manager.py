"""
统一配置管理系统
提供灵活的配置加载、验证和热更新机制
"""

import json
import logging
import os
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class ConfigSource(Enum):
    """配置源类型"""

    FILE = "file"
    ENVIRONMENT = "environment"
    DATABASE = "database"
    REMOTE = "remote"


@dataclass
class ConfigItem:
    """配置项"""

    key: str
    value: Any
    source: ConfigSource
    required: bool = False
    validator: Callable[[Any], bool] | None = None
    description: str = ""
    last_updated: float = field(default_factory=time.time)

    def validate(self) -> bool:
        """验证配置值"""
        if self.validator:
            return self.validator(self.value)
        return True


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_dir: str | None = None):
        self.config_dir = (
            Path(config_dir)
            if config_dir
            else Path(__file__).parent.parent.parent / "config"
        )
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self._configs: dict[str, ConfigItem] = {}
        self._lock = threading.RLock()
        self._watchers: list[Callable[[str, Any, Any], None]] = []

        # 默认配置文件
        self.default_config_file = self.config_dir / "default.yaml"
        self.user_config_file = self.config_dir / "config.yaml"
        self.env_config_file = self.config_dir / "env.yaml"

        # 加载配置
        self._load_all_configs()

    def _load_all_configs(self) -> None:
        """加载所有配置"""
        # 1. 加载默认配置
        self._load_default_config()

        # 2. 加载用户配置文件
        if self.user_config_file.exists():
            self._load_config_file(self.user_config_file)

        # 3. 加载环境特定配置
        env = os.environ.get("SUOKE_ENV", "development")
        env_file = self.config_dir / f"{env}.yaml"
        if env_file.exists():
            self._load_config_file(env_file)

        # 4. 加载环境变量
        self._load_environment_variables()

    def _load_default_config(self) -> None:
        """加载默认配置"""
        default_configs = {
            # 服务配置
            "service.name": "suoke-accessibility-service",
            "service.version": "1.0.0",
            "service.host": "0.0.0.0",
            "service.port": 8080,
            "service.debug": False,
            # 数据库配置
            "database.host": "localhost",
            "database.port": 5432,
            "database.name": "suoke_accessibility",
            "database.username": "postgres",
            "database.pool_size": 10,
            "database.timeout": 30,
            # 缓存配置
            "cache.default_ttl": 300,
            "cache.max_size": 1000,
            "cache.max_memory_mb": 100,
            "cache.cleanup_interval": 60,
            # 日志配置
            "logging.level": "INFO",
            "logging.format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "logging.file": "logs/accessibility-service.log",
            "logging.max_size_mb": 10,
            "logging.backup_count": 5,
            # 健康检查配置
            "health_check.timeout": 1.5,
            "health_check.interval": 30,
            "health_check.retries": 3,
            # 性能监控配置
            "monitoring.enabled": True,
            "monitoring.interval": 10,
            "monitoring.metrics_retention_hours": 24,
            # AI模型配置
            "ai.model_cache_size": 50,
            "ai.model_timeout": 30,
            "ai.max_concurrent_requests": 10,
            # 安全配置
            "security.encryption_enabled": True,
            "security.token_expiry_hours": 24,
            "security.max_login_attempts": 5,
        }

        for key, value in default_configs.items():
            self._set_config_item(key, value, ConfigSource.FILE, required=False)

    def _load_config_file(self, file_path: Path):
        """加载配置文件"""
        try:
            with open(file_path, encoding="utf-8") as f:
                if file_path.suffix.lower() in [".yaml", ".yml"]:
                    data = yaml.safe_load(f)
                elif file_path.suffix.lower() == ".json":
                    data = json.load(f)
                else:
                    logger.warning(f"不支持的配置文件格式: {file_path}")
                    return

            self._load_nested_dict(data, ConfigSource.FILE)
            logger.info(f"配置文件已加载: {file_path}")

        except Exception as e:
            logger.error(f"加载配置文件失败 {file_path}: {e}")

    def _load_nested_dict(
        self, data: dict[str, Any], source: ConfigSource, prefix: str = ""
    ):
        """加载嵌套字典配置"""
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict):
                self._load_nested_dict(value, source, full_key)
            else:
                self._set_config_item(full_key, value, source)

    def _load_environment_variables(self) -> None:
        """加载环境变量"""
        for key, value in os.environ.items():
            if key.startswith("SUOKE_"):
                # 转换环境变量名为配置键
                config_key = key[6:].lower().replace("_", ".")

                # 尝试转换类型
                converted_value = self._convert_env_value(value)
                self._set_config_item(
                    config_key, converted_value, ConfigSource.ENVIRONMENT
                )

    def _convert_env_value(self, value: str) -> Any:
        """转换环境变量值类型"""
        # 布尔值
        if value.lower() in ("true", "false"):
            return value.lower() == "true"

        # 整数
        try:
            return int(value)
        except ValueError:
            pass

        # 浮点数
        try:
            return float(value)
        except ValueError:
            pass

        # JSON
        if value.startswith("{") or value.startswith("["):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass

        # 字符串
        return value

    def _set_config_item(
        self, key: str, value: Any, source: ConfigSource, required: bool = False
    ):
        """设置配置项"""
        with self._lock:
            old_value = self._configs.get(key)
            old_val = old_value.value if old_value else None

            self._configs[key] = ConfigItem(
                key=key,
                value=value,
                source=source,
                required=required,
                last_updated=time.time(),
            )

            # 通知观察者
            for watcher in self._watchers:
                try:
                    watcher(key, old_val, value)
                except Exception as e:
                    logger.error(f"配置观察者执行失败: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        with self._lock:
            config_item = self._configs.get(key)
            if config_item:
                return config_item.value
            return default

    def set(
        self, key: str, value: Any, source: ConfigSource = ConfigSource.REMOTE
    ) -> bool:
        """设置配置值"""
        try:
            self._set_config_item(key, value, source)
            return True
        except Exception as e:
            logger.error(f"设置配置失败 {key}: {e}")
            return False

    def get_int(self, key: str, default: int = 0) -> int:
        """获取整数配置"""
        value = self.get(key, default)
        try:
            return int(value)
        except (ValueError, TypeError):
            logger.warning(f"配置 {key} 不是有效的整数: {value}")
            return default

    def get_float(self, key: str, default: float = 0.0) -> float:
        """获取浮点数配置"""
        value = self.get(key, default)
        try:
            return float(value)
        except (ValueError, TypeError):
            logger.warning(f"配置 {key} 不是有效的浮点数: {value}")
            return default

    def get_bool(self, key: str, default: bool = False) -> bool:
        """获取布尔配置"""
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes", "on")
        return bool(value)

    def get_list(self, key: str, default: list[Any] = None) -> list[Any]:
        """获取列表配置"""
        value = self.get(key, default or [])
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            # 尝试解析逗号分隔的字符串
            return [item.strip() for item in value.split(",") if item.strip()]
        return default or []

    def get_dict(self, key: str, default: dict[str, Any] = None) -> dict[str, Any]:
        """获取字典配置"""
        value = self.get(key, default or {})
        if isinstance(value, dict):
            return value
        return default or {}

    def get_all(self, prefix: str = "") -> dict[str, Any]:
        """获取所有配置或指定前缀的配置"""
        with self._lock:
            if not prefix:
                return {key: item.value for key, item in self._configs.items()}

            result = {}
            for key, item in self._configs.items():
                if key.startswith(prefix):
                    # 移除前缀
                    clean_key = key[len(prefix) :].lstrip(".")
                    result[clean_key] = item.value
            return result

    def reload(self) -> bool:
        """重新加载配置"""
        try:
            old_configs = self._configs.copy()
            self._configs.clear()
            self._load_all_configs()

            logger.info("配置已重新加载")
            return True
        except Exception as e:
            logger.error(f"重新加载配置失败: {e}")
            # 恢复旧配置
            self._configs = old_configs
            return False

    def save_to_file(self, file_path: str | None = None) -> bool:
        """保存配置到文件"""
        if file_path is None:
            file_path = self.user_config_file
        else:
            file_path = Path(file_path)

        try:
            # 构建嵌套字典
            config_dict = {}
            with self._lock:
                for key, item in self._configs.items():
                    if item.source == ConfigSource.FILE:
                        self._set_nested_value(config_dict, key, item.value)

            # 保存到文件
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)

            logger.info(f"配置已保存到: {file_path}")
            return True
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            return False

    def _set_nested_value(self, dict_obj: dict[str, Any], key: str, value: Any):
        """在嵌套字典中设置值"""
        keys = key.split(".")
        current = dict_obj

        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value

    def add_watcher(self, watcher: Callable[[str, Any, Any], None]):
        """添加配置变更观察者"""
        self._watchers.append(watcher)

    def remove_watcher(self, watcher: Callable[[str, Any, Any], None]):
        """移除配置变更观察者"""
        if watcher in self._watchers:
            self._watchers.remove(watcher)

    def validate_all(self) -> dict[str, bool]:
        """验证所有配置"""
        results = {}
        with self._lock:
            for key, item in self._configs.items():
                try:
                    results[key] = item.validate()
                except Exception as e:
                    logger.error(f"验证配置 {key} 失败: {e}")
                    results[key] = False
        return results

    def get_config_info(self, key: str) -> dict[str, Any] | None:
        """获取配置项详细信息"""
        with self._lock:
            item = self._configs.get(key)
            if item:
                return {
                    "key": item.key,
                    "value": item.value,
                    "source": item.source.value,
                    "required": item.required,
                    "description": item.description,
                    "last_updated": item.last_updated,
                }
        return None


# 全局配置管理器实例
config_manager = ConfigManager()


# 便捷函数
def get_config(key: str, default: Any = None) -> Any:
    """获取配置值的便捷函数"""
    return config_manager.get(key, default)


def set_config(key: str, value: Any) -> bool:
    """设置配置值的便捷函数"""
    return config_manager.set(key, value)


def reload_config() -> bool:
    """重新加载配置的便捷函数"""
    return config_manager.reload()


# 常用配置获取函数
def get_service_config() -> dict[str, Any]:
    """获取服务配置"""
    return config_manager.get_all("service")


def get_database_config() -> dict[str, Any]:
    """获取数据库配置"""
    return config_manager.get_all("database")


def get_cache_config() -> dict[str, Any]:
    """获取缓存配置"""
    return config_manager.get_all("cache")


def get_logging_config() -> dict[str, Any]:
    """获取日志配置"""
    return config_manager.get_all("logging")
