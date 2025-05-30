#!/usr/bin/env python3
"""
配置加载器
负责加载和管理小克智能体服务的配置
"""

import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class ConfigLoader:
    """配置加载器, 负责加载和管理服务配置"""

    _instance = None

    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """初始化配置加载器"""
        if self._initialized:
            return

        # 配置存储
        self.config = {}

        # 环境变量
        self.env = Path.cwd().joinpath(".env").read_text(encoding="utf-8").strip() if Path.cwd().joinpath(".env").exists() else "development"

        # 加载配置
        self._load_config()

        self._initialized = True

        logger.info(f"配置加载器初始化完成, 当前环境: {self.env}")

    def _load_config(self):
        """加载配置文件"""
        try:
            # 基础配置路径
            base_path = Path(__file__).parent.parent.parent / "config"

            # 加载默认配置
            default_config_path = base_path / "default.yaml"
            if default_config_path.exists():
                with default_config_path.open(encoding="utf-8") as f:
                    self.config = yaml.safe_load(f) or {}
                logger.info(f"已加载默认配置: {default_config_path}")

            # 加载环境特定配置
            env_config_path = base_path / f"{self.env}.yaml"
            if env_config_path.exists():
                with env_config_path.open(encoding="utf-8") as f:
                    env_config = yaml.safe_load(f) or {}

                # 合并配置
                self._merge_configs(self.config, env_config)
                logger.info(f"已加载环境配置: {env_config_path}")

            # 加载本地配置
            local_config_path = base_path / "local.yaml"
            if local_config_path.exists():
                with local_config_path.open(encoding="utf-8") as f:
                    local_config = yaml.safe_load(f) or {}

                # 合并配置
                self._merge_configs(self.config, local_config)
                logger.info(f"已加载本地配置: {local_config_path}")

        except Exception as e:
            logger.error(f"加载配置失败: {e!s}")
            raise

    def _merge_configs(self, base: dict, override: dict):
        """递归合并配置, 重写项覆盖基本配置"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_configs(base[key], value)
            else:
                base[key] = value

    def get(self, key: str, default=None) -> Any:
        """
        获取配置项

        Args:
            key: 配置键, 支持点号分隔的嵌套路径, 如 'server.host'
            default: 如果配置不存在, 返回的默认值

        Returns:
            Any: 配置值或默认值
        """
        try:
            # 处理嵌套路径
            parts = key.split(".")
            value = self.config

            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return default

            return value
        except Exception:
            return default

    def get_section(self, section: str) -> dict[str, Any]:
        """
        获取配置节

        Args:
            section: 配置节名称, 支持点号分隔的嵌套路径

        Returns:
            Dict[str, Any]: 配置节或空字典
        """
        return self.get(section, {})

    def get_all(self) -> dict[str, Any]:
        """
        获取所有配置

        Returns:
            Dict[str, Any]: 所有配置
        """
        return self.config.copy()

    def reload(self):
        """重新加载配置"""
        self._load_config()
        logger.info("配置已重新加载")


def get_config() -> ConfigLoader:
    """
    获取配置加载器实例

    Returns:
        ConfigLoader: 配置加载器实例
    """
    return ConfigLoader()
