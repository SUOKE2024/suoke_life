"""
config_manager - 索克生活项目模块
"""

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any
from watchdog.events import FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer
import json
import logging
import os
import threading
import time
import yaml

#! / usr / bin / env python3
"""
配置管理器
提供配置加载、合并、验证和热更新功能
"""



logger = logging.getLogger(__name__)


class ConfigFormat(Enum):
    """配置格式"""

    JSON = "json"
    YAML = "yaml"
    ENV = "env"
    PROPERTIES = "properties"


class ConfigSource(Enum):
    """配置来源"""

    FILE = "file"
    ENV = "env"
    CONFIG_CENTER = "config_center"
    MEMORY = "memory"


@dataclass
class ConfigItem:
    """配置项"""

    key: str
    value: Any
    source: ConfigSource
    format: ConfigFormat
    version: int = 1
    timestamp: float = None

    def __post_init__(self) -> None:
        """TODO: 添加文档字符串"""
        if self.timestamp is None:
            self.timestamp = time.time()


class ConfigWatcher(FileSystemEventHandler):
    """配置文件监视器"""

    def __init__(self, config_manager: "ConfigManager"):
        """TODO: 添加文档字符串"""
        self.config_manager = config_manager
        self.callbacks: list[Callable] = []

    def on_modified(self, event):
        """文件修改事件"""
        if isinstance(event, FileModifiedEvent) and not event.is_directory:
            logger.info(f"配置文件已修改: {event.src_path}")

            # 重新加载配置
            try:
                self.config_manager.reload()

                # 触发回调
                for callback in self.callbacks:
                    try:
                        callback(event.src_path)
                    except Exception as e:
                        logger.error(f"配置变更回调失败: {e}")

            except Exception as e:
                logger.error(f"重新加载配置失败: {e}")

    def add_callback(self, callback: Callable):
        """添加配置变更回调"""
        self.callbacks.append(callback)

    def remove_callback(self, callback: Callable):
        """移除配置变更回调"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)


class ConfigManager:
    """配置管理器"""

    def __init__(
        self,
        service_name: str,
        config_dir: str = "config",
        enable_hot_reload: bool = True,
        enable_env_override: bool = True,
        env_prefix: str = "",
    ):
        self.service_name = service_name
        self.config_dir = Path(config_dir)
        self.enable_hot_reload = enable_hot_reload
        self.enable_env_override = enable_env_override
        self.env_prefix = env_prefix or service_name.upper()

        # 配置存储
        self._config: dict[str, ConfigItem] = {}
        self._lock = threading.RLock()

        # 文件监视器
        self.watcher = ConfigWatcher(self)
        self.observer = None

        # 配置版本
        self.version = 0

        # 初始化加载配置
        self.load()

        # 启动文件监视
        if enable_hot_reload:
            self.start_watching()

    def load(self) -> None:
        """加载所有配置"""
        with self._lock:
            # 清空现有配置
            self._config.clear()

            # 1. 加载文件配置
            self._load_file_configs()

            # 2. 加载环境变量
            if self.enable_env_override:
                self._load_env_configs()

            # 增加版本号
            self.version += 1

            logger.info(f"配置加载完成，版本: {self.version}")

    def reload(self) -> None:
        """重新加载配置"""
        logger.info("重新加载配置...")
        self.load()

    def _load_file_configs(self) -> None:
        """加载文件配置"""
        if not self.config_dir.exists():
            logger.warning(f"配置目录不存在: {self.config_dir}")
            return

        # 支持的配置文件扩展名
        extensions = {
            ".json": ConfigFormat.JSON,
            ".yaml": ConfigFormat.YAML,
            ".yml": ConfigFormat.YAML,
            ".properties": ConfigFormat.PROPERTIES,
        }

        # 遍历配置文件
        for file_path in self.config_dir.rglob(" * "):
            if file_path.is_file() and file_path.suffix in extensions:
                try:
                    format_type = extensions[file_path.suffix]
                    config_data = self._load_file(file_path, format_type)

                    # 将配置数据扁平化并存储
                    self._flatten_and_store(
                        config_data,
                        ConfigSource.FILE,
                        format_type,
                        prefix = file_path.stem,
                    )

                except Exception as e:
                    logger.error(f"加载配置文件失败 {file_path}: {e}")

    def _load_file(self, file_path: Path, format_type: ConfigFormat) -> dict[str, Any]:
        """加载单个配置文件"""
        with open(file_path, encoding = "utf - 8") as f:
            if format_type == ConfigFormat.JSON:
                return json.load(f)
            elif format_type == ConfigFormat.YAML:
                return yaml.safe_load(f)
            elif format_type == ConfigFormat.PROPERTIES:
                return self._parse_properties(f.read())
            else:
                raise ValueError(f"不支持的配置格式: {format_type}")

    def _parse_properties(self, content: str) -> dict[str, Any]:
        """解析properties格式"""
        result = {}
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith("#") and " = " in line:
                key, value = line.split(" = ", 1)
                result[key.strip()] = value.strip()
        return result

    def _load_env_configs(self) -> None:
        """加载环境变量配置"""
        prefix = f"{self.env_prefix}_"

        for key, value in os.environ.items():
            if key.startswith(prefix):
                # 移除前缀并转换为小写
                config_key = key[len(prefix) :].lower().replace("_", ".")

                # 尝试解析值
                parsed_value = self._parse_env_value(value)

                # 存储配置
                self._config[config_key] = ConfigItem(
                    key = config_key,
                    value = parsed_value,
                    source = ConfigSource.ENV,
                    format = ConfigFormat.ENV,
                    version = self.version,
                )

    def _parse_env_value(self, value: str) -> Any:
        """解析环境变量值"""
        # 尝试解析为JSON
        try:
            return json.loads(value)
        except:
            pass

        # 尝试解析为布尔值
        if value.lower() in ("true", "false"):
            return value.lower() == "true"

        # 尝试解析为数字
        try:
            if "." in value:
                return float(value)
            else:
                return int(value)
        except:
            pass

        # 返回原始字符串
        return value

    def _flatten_and_store(
        self,
        data: dict[str, Any],
        source: ConfigSource,
        format_type: ConfigFormat,
        prefix: str = "",
    ):
        """扁平化并存储配置"""

        def flatten(obj, parent_key = ""):
            """TODO: 添加文档字符串"""
            items = []

            if isinstance(obj, dict):
                for k, v in obj.items():
                    new_key = f"{parent_key}.{k}" if parent_key else k
                    if isinstance(v, dict):
                        items.extend(flatten(v, new_key))
                    else:
                        items.append((new_key, v))
            else:
                items.append((parent_key, obj))

            return items

        # 扁平化配置
        flat_items = flatten(data, prefix)

        # 存储配置项
        for key, value in flat_items:
            self._config[key] = ConfigItem(
                key = key,
                value = value,
                source = source,
                format = format_type,
                version = self.version,
            )

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        with self._lock:
            item = self._config.get(key)
            if item:
                return item.value
            return default

    def get_int(self, key: str, default: int = 0) -> int:
        """获取整数配置"""
        value = self.get(key, default)
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def get_float(self, key: str, default: float = 0.0) -> float:
        """获取浮点数配置"""
        value = self.get(key, default)
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def get_bool(self, key: str, default: bool = False) -> bool:
        """获取布尔配置"""
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "yes", "1", "on")
        return bool(value)

    def get_list(self, key: str, default: list | None = None) -> list:
        """获取列表配置"""
        value = self.get(key, default or [])
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [v.strip() for v in value.split(",")]
        return default or []

    def get_dict(self, key_prefix: str) -> dict[str, Any]:
        """获取字典配置（通过前缀）"""
        result = {}
        prefix = f"{key_prefix}."

        with self._lock:
            for key, item in self._config.items():
                if key.startswith(prefix):
                    sub_key = key[len(prefix) :]
                    result[sub_key] = item.value

        return result

    def set(self, key: str, value: Any, persist: bool = False):
        """设置配置值"""
        with self._lock:
            self._config[key] = ConfigItem(
                key = key,
                value = value,
                source = ConfigSource.MEMORY,
                format = ConfigFormat.JSON,
                version = self.version,
            )

            if persist:
                # TODO: 实现持久化逻辑
                pass

    def exists(self, key: str) -> bool:
        """检查配置是否存在"""
        return key in self._config

    def get_all(self) -> dict[str, Any]:
        """获取所有配置"""
        with self._lock:
            return {key: item.value for key, item in self._config.items()}

    def get_by_source(self, source: ConfigSource) -> dict[str, Any]:
        """根据来源获取配置"""
        with self._lock:
            return {
                key: item.value
                for key, item in self._config.items()
                if item.source == source
            }

    def start_watching(self) -> None:
        """启动文件监视"""
        if self.observer is None:
            self.observer = Observer()
            self.observer.schedule(self.watcher, str(self.config_dir), recursive = True)
            self.observer.start()
            logger.info(f"启动配置文件监视: {self.config_dir}")

    def stop_watching(self) -> None:
        """停止文件监视"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            logger.info("停止配置文件监视")

    def add_change_callback(self, callback: Callable):
        """添加配置变更回调"""
        self.watcher.add_callback(callback)

    def remove_change_callback(self, callback: Callable):
        """移除配置变更回调"""
        self.watcher.remove_callback(callback)


# 全局配置管理器注册表
_managers: dict[str, ConfigManager] = {}


def get_config_manager(service_name: str, **kwargs) -> ConfigManager:
    """获取或创建配置管理器"""
    if service_name not in _managers:
        _managers[service_name] = ConfigManager(service_name, **kwargs)

    return _managers[service_name]


# 便捷装饰器
def config(key: str, default: Any = None):
    """
    配置注入装饰器

    自动注入配置值到函数参数
    """

    def decorator(func: Callable):
        """TODO: 添加文档字符串"""
        def wrapper( *args, **kwargs):
            """TODO: 添加文档字符串"""
            # 获取服务名（从模块名推断）
            service_name = func.__module__.split(".")[0]
            manager = get_config_manager(service_name)

            # 注入配置值
            config_value = manager.get(key, default)
            kwargs[key.replace(".", "_")] = config_value

            return func( *args, **kwargs)

        return wrapper

    return decorator
