"""
config - 索克生活项目模块
"""

from pathlib import Path
from typing import Any, Dict, Optional
import logging
import os
import yaml

#!/usr/bin/env python3

"""
配置加载工具
"""



# 初始化日志
logger = logging.getLogger(__name__)


class ConfigManager:
    """配置管理器"""

    def __init__(self):
        """初始化配置管理器"""
        self._config: Dict[str, Any] = {}
        self._loaded = False

    def get_config(self) -> dict[str, Any]:
        """
        获取当前配置，如果配置未加载则加载配置

        Returns:
            Dict: 配置字典
        """
        if not self._loaded:
            self.load_config()
        return self._config

    def load_config(self, config_file: Optional[str] = None) -> Dict[str, Any]:
        """
        加载配置文件

        Args:
            config_file: 配置文件路径，如果为None则使用默认配置

        Returns:
            Dict: 配置字典
        """
        # 默认配置
        default_config = {
            "app": {
                "name": "Corn Maze Service",
                "version": "1.0.0",
                "environment": "development"
            },
            "server": {
                "host": "0.0.0.0",
                "port": 8080,
                "workers": 4
            },
            "db": {
                "type": "sqlite",
                "path": "./data/corn_maze.db",
                "pool_size": 10
            },
            "logging": {
                "level": "INFO",
                "file": "./logs/app.log",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "cache": {
                "type": "memory",
                "ttl": 3600
            }
        }

        self._config = default_config

        # 如果指定了配置文件，则加载并合并
        if config_file:
            file_config = self._load_config_from_file(config_file)
            self._config = self._merge_configs(self._config, file_config)

        # 应用环境变量覆盖
        self._config = self._apply_env_overrides(self._config)

        # 验证配置
        self._validate_config(self._config)

        # 确保必要的目录存在
        self._ensure_directories(self._config)

        self._loaded = True
        return self._config

    def _load_config_from_file(self, file_path: str) -> dict[str, Any]:
        """从YAML文件加载配置"""
        try:
            config_path = Path(file_path)
            if not config_path.exists():
                logger.warning(f"配置文件不存在: {file_path}")
                return {}

            with config_path.open(encoding="utf-8") as f:
                config = yaml.safe_load(f)
                logger.info(f"从文件加载配置: {file_path}")
                return config or {}

        except Exception as e:
            logger.error(f"加载配置文件失败: {e!s}")
            return {}

    def _merge_configs(self, base_config: dict[str, Any], override_config: dict[str, Any]) -> dict[str, Any]:
        """合并配置字典"""
        result = base_config.copy()

        for key, value in override_config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value

        return result

    def _apply_env_overrides(self, config: dict[str, Any]) -> dict[str, Any]:
        """应用环境变量覆盖"""
        # 定义环境变量映射
        env_mappings = {
            "APP_NAME": ["app", "name"],
            "APP_VERSION": ["app", "version"],
            "ENVIRONMENT": ["app", "environment"],
            "SERVER_HOST": ["server", "host"],
            "SERVER_PORT": ["server", "port"],
            "SERVER_WORKERS": ["server", "workers"],
            "DB_TYPE": ["db", "type"],
            "DB_PATH": ["db", "path"],
            "DB_POOL_SIZE": ["db", "pool_size"],
            "LOG_LEVEL": ["logging", "level"],
            "LOG_FILE": ["logging", "file"],
            "CACHE_TYPE": ["cache", "type"],
            "CACHE_TTL": ["cache", "ttl"]
        }

        result = config.copy()

        for env_var, config_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # 导航到配置路径
                current = result
                for key in config_path[:-1]:
                    if key not in current:
                        current[key] = {}
                    current = current[key]

                # 设置值（尝试转换类型）
                final_key = config_path[-1]
                try:
                    # 尝试转换为整数
                    if env_value.isdigit():
                        current[final_key] = int(env_value)
                    # 尝试转换为浮点数
                    elif "." in env_value and env_value.replace(".", "").isdigit():
                        current[final_key] = float(env_value)
                    # 尝试转换为布尔值
                    elif env_value.lower() in ("true", "false"):
                        current[final_key] = env_value.lower() == "true"
                    else:
                        current[final_key] = env_value

                    logger.debug(f"应用环境变量覆盖: {env_var} -> {'.'.join(config_path)} = {env_value}")

                except Exception as e:
                    logger.warning(f"环境变量类型转换失败: {env_var} = {env_value}, 错误: {e!s}")
                    current[final_key] = env_value

        return result

    def _validate_config(self, config: dict[str, Any]) -> None:
        """验证配置"""
        # 端口范围常量
        MIN_PORT = 1
        MAX_PORT = 65535

        required_keys = [
            ["app", "name"],
            ["server", "host"],
            ["server", "port"],
            ["db", "type"]
        ]

        for key_path in required_keys:
            current = config
            for key in key_path:
                if key not in current:
                    raise ValueError(f"缺少必需的配置项: {'.'.join(key_path)}")
                current = current[key]

        # 验证端口范围
        port = config.get("server", {}).get("port", 0)
        if not (MIN_PORT <= port <= MAX_PORT):
            raise ValueError(f"无效的端口号: {port}")

        logger.info("配置验证通过")

    def _ensure_directories(self, config: dict[str, Any]) -> None:
        """确保必要的目录存在"""
        # 确保数据库目录存在
        if "db" in config and "path" in config["db"]:
            db_path = Path(config["db"]["path"])
            db_path.parent.mkdir(parents=True, exist_ok=True)

        # 确保日志目录存在
        if "logging" in config and "file" in config["logging"]:
            log_file = config["logging"]["file"]
            if log_file:
                log_path = Path(log_file)
                log_path.parent.mkdir(parents=True, exist_ok=True)

    def get_value(self, key: str, default: Any = None) -> Any:
        """
        获取配置值

        Args:
            key: 配置键，支持点符号路径，如 'db.path'
            default: 默认值

        Returns:
            Any: 配置值
        """
        config = self.get_config()
        keys = key.split(".")

        current = config
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default

        return current


# 配置管理器单例
class ConfigManagerSingleton:
    """配置管理器单例"""

    _instance: ConfigManager | None = None

    @classmethod
    def get_instance(cls) -> ConfigManager:
        """获取配置管理器实例"""
        if cls._instance is None:
            cls._instance = ConfigManager()
        return cls._instance


# 向后兼容的函数接口
def get_config() -> dict[str, Any]:
    """获取当前配置（向后兼容）"""
    return ConfigManagerSingleton.get_instance().get_config()


def load_config(config_file: Optional[str] = None) -> Dict[str, Any]:
    """加载配置文件（向后兼容）"""
    return ConfigManagerSingleton.get_instance().load_config(config_file)


def get_value(key: str, default: Any = None) -> Any:
    """获取配置值（向后兼容）"""
    return ConfigManagerSingleton.get_instance().get_value(key, default)


# 保留原有的独立函数以供直接使用
def load_config_from_file(file_path: str) -> dict[str, Any]:
    """从YAML文件加载配置"""
    return ConfigManagerSingleton.get_instance()._load_config_from_file(file_path)


def merge_configs(base_config: dict[str, Any], override_config: dict[str, Any]) -> dict[str, Any]:
    """合并配置字典"""
    return ConfigManagerSingleton.get_instance()._merge_configs(base_config, override_config)


def apply_env_overrides(config: dict[str, Any]) -> dict[str, Any]:
    """应用环境变量覆盖"""
    return ConfigManagerSingleton.get_instance()._apply_env_overrides(config)


def validate_config(config: dict[str, Any]) -> None:
    """验证配置"""
    return ConfigManagerSingleton.get_instance()._validate_config(config)


def ensure_directories(config: dict[str, Any]) -> None:
    """确保必要的目录存在"""
    return ConfigManagerSingleton.get_instance()._ensure_directories(config)
