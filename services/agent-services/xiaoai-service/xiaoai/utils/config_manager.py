#!/usr/bin/env python3

"""
配置管理模块
支持环境变量覆盖、配置热更新和不同环境的配置
"""

import json
import logging
import os
import threading
import time
from dataclasses import dataclass
from typing import Any

import yaml

# 设置日志
logger = logging.getLogger(__name__)


@dataclass
class ConfigSource:
    """配置源信息"""
    type: str  # 'file', 'env', 'default'
    path: str | None = None  # 文件路径(如果是文件类型)
    key: str | None = None  # 环境变量键(如果是环境变量类型)


class ConfigManager:
    """增强的配置管理器"""

    def __init__(self,
                 configdir: str = "config",
                 env: str | None = None,
                 watchinterval: int = 30):
        """
        初始化配置管理器

        Args:
            config_dir: 配置文件目录
            env: 环境标识 (development, staging, production等), 默认从ENV环境变量获取
            watch_interval: 配置文件监视间隔(秒)
        """
        self.configdir = config_dir
        self.env = env or os.environ.get("ENV", "development")
        self.watchinterval = watch_interval

        # 配置数据和来源跟踪
        self.configdata: dict[str, Any] = {}
        self.configsources: dict[str, ConfigSource] = {}

        # 文件监视和重新加载
        self.lastmodified_times: dict[str, float] = {}
        self.watchthread = None
        self.running = False

        # 启动配置监视线程
        self.start_watching()

        logger.info(f"配置管理器初始化: 环境={self.env}, 配置目录={self.config_dir}")

    def load_config(self, reload: bool = False) -> dict[str, Any]:
        """
        加载所有配置

        Args:
            reload: 是否强制重新加载

        Returns:
            Dict[str, Any]: 加载的配置数据
        """
        if not self.config_data or reload:
            self._load_default_config()
            self._load_common_config()
            self._load_env_config()
            self._load_env_vars()
            self._track_file_changes()

        return self.config_data

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        支持点符号访问嵌套配置, 如 "database.host"

        Args:
            key: 配置键
            default: 默认值, 如果找不到键则返回

        Returns:
            Any: 配置值
        """
        # 确保配置已加载
        if not self.config_data:
            self.load_config()

        # 解析键, 支持点符号访问
        if "." in key:
            parts = key.split(".")
            current = self.config_data
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return default
            return current

        # 直接访问
        return self.config_data.get(key, default)

    def get_section(self, section: str, default: Any = None) -> Any:
        """
        获取配置区块

        Args:
            section: 配置区块名
            default: 默认值, 如果找不到区块则返回

        Returns:
            Any: 配置区块
        """
        return self.get(section, default)

    def set(self, key: str, value: Any, source: ConfigSource | None = None) -> None:
        """
        设置配置值

        Args:
            key: 配置键
            value: 配置值
            source: 配置来源信息
        """
        # 解析键, 支持点符号访问
        if "." in key:
            parts = key.split(".")
            current = self.config_data

            # 导航到最后一级父节点
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]

            # 设置值
            current[parts[-1]] = value

            # 跟踪来源
            if source:
                self.config_sources[key] = source

        else:
            # 直接设置
            self.config_data[key] = value

            # 跟踪来源
            if source:
                self.config_sources[key] = source

    def _load_default_config(self) -> None:
        """加载默认配置"""
        defaultconfig = {
            "app": {
                "name": "xiaoai-service",
                "version": "1.0.0"
            },
            "paths": {
                "prompts": "config/prompts",
                "rules": "config/rules",
                "logs": "logs"
            },
            "server": {
                "host": "0.0.0.0",
                "port": 50051,
                "workers": 4
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            },
            "diagnostic_services": {
                "look_service": {
                    "host": "localhost",
                    "port": 50052
                },
                "listen_service": {
                    "host": "localhost",
                    "port": 50053
                },
                "inquiry_service": {
                    "host": "localhost",
                    "port": 50054
                },
                "palpation_service": {
                    "host": "localhost",
                    "port": 50055
                }
            },
            "llm": {
                "default_model": "gpt-4o",
                "openai_api_key": "",
                "timeout": 15000,
                "max_retries": 3,
                "temperature": 0.3
            },
            "feature_extraction": {
                "min_confidence": 0.6,
                "max_features_per_category": 10,
                "use_advanced_extraction": True
            },
            "fusion": {
                "algorithm": "weighted",
                "min_confidence_threshold": 0.5,
                "use_early_fusion": True
            },
            "differentiation": {
                "rules_version": "v2",
                "confidence_threshold": 0.7,
                "evidence_requirements": "moderate",
                "methods": [
                    "eight_principles",
                    "zang_fu",
                    "qi_blood_fluid"
                ]
            },
            "recommendations": {
                "max_recommendations": 10,
                "min_confidence": 0.6,
                "category_limits": {
                    "diet": 3,
                    "lifestyle": 2,
                    "exercise": 2,
                    "emotion": 2,
                    "acupoint": 1,
                    "prevention": 1,
                    "medical": 1
                }
            },
            "resilience": {
                "circuit_breaker": {
                    "failure_threshold": 5,
                    "success_threshold": 2,
                    "timeout_seconds": 30
                },
                "retry": {
                    "max_retries": 3,
                    "initial_delay": 0.5,
                    "backoff_factor": 2.0
                }
            }
        }

        # 合并到配置数据中
        self._merge_config(defaultconfig)

        # 跟踪来源
        for key in self._flatten_dict(defaultconfig):
            self.config_sources[key] = ConfigSource(type="default")

    def _load_common_config(self) -> None:
        """加载通用配置文件"""
        commonfile = os.path.join(self.configdir, "config.yaml")
        self._load_yaml_config(commonfile, "common")

    def _load_env_config(self) -> None:
        """加载环境特定配置文件"""
        envfile = os.path.join(self.configdir, f"config.{self.env}.yaml")
        self._load_yaml_config(envfile, self.env)

    def _load_yaml_config(self, file_path: str, label: str) -> None:
        """
        从YAML文件加载配置

        Args:
            file_path: 配置文件路径
            label: 配置标签, 用于日志
        """
        if not os.path.exists(filepath):
            logger.info(f"{label} 配置文件不存在: {file_path}")
            return

        try:
            with open(filepath, encoding='utf-8') as file:
                configdata = yaml.safe_load(file)

                if not config_data:
                    logger.warning(f"{label} 配置文件为空: {file_path}")
                    return

                # 合并配置
                self._merge_config(configdata)

                # 跟踪来源
                for key in self._flatten_dict(configdata):
                    self.config_sources[key] = ConfigSource(
                        type="file",
                        path=filepath,
                    )

                # 记录最后修改时间
                self.last_modified_times[file_path] = os.path.getmtime(filepath)

                logger.info(f"已加载 {label} 配置文件: {file_path}")

        except Exception as e:
            logger.error(f"加载 {label} 配置文件异常: {e!s}")

    def _load_env_vars(self) -> None:
        """加载环境变量配置"""
        # 环境变量前缀
        prefix = "XIAOAI_"

        # 查找所有以前缀开头的环境变量
        for key, value in os.environ.items():
            if key.startswith(prefix):
                # 移除前缀, 转换为配置键
                configkey = key[len(prefix):].lower()

                # 将双下划线转换为点符号
                configkey = config_key.replace("__", ".")

                # 尝试解析值
                parsedvalue = self._parse_value(value)

                # 设置配置
                self.set(configkey, parsedvalue, ConfigSource(type="env", key=key))

                logger.debug(f"从环境变量加载配置: {key} -> {config_key}={parsed_value}")

    def _parse_value(self, value: str) -> Any:
        """
        解析配置值
        尝试将字符串转换为适当的数据类型

        Args:
            value: 要解析的字符串值

        Returns:
            Any: 解析后的值
        """
        # 如果是空字符串, 返回空字符串
        if value == "":
            return ""

        # 尝试作为JSON解析
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass

        # 尝试作为布尔值解析
        if value.lower() in ("true", "yes", "on", "1"):
            return True
        elif value.lower() in ("false", "no", "off", "0"):
            return False

        # 尝试作为整数解析
        try:
            return int(value)
        except ValueError:
            pass

        # 尝试作为浮点数解析
        try:
            return float(value)
        except ValueError:
            pass

        # 默认作为字符串返回
        return value

    def _merge_config(self, new_config: dict[str, Any]) -> None:
        """
        合并配置数据

        Args:
            new_config: 要合并的新配置
        """
        self.configdata = self._deep_merge(self.configdata, newconfig)

    def _deep_merge(self, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        """
        深度合并两个字典

        Args:
            base: 基础字典
            override: 覆盖字典

        Returns:
            Dict[str, Any]: 合并后的字典
        """
        result = base.copy()

        for key, value in override.items():
            # 如果两者都是字典, 递归合并
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                # 否则直接覆盖
                result[key] = value

        return result

    def _flatten_dict(self, d: dict[str, Any], parentkey: str = "") -> list[str]:
        """
        将嵌套字典扁平化为点符号键列表

        Args:
            d: 要扁平化的字典
            parent_key: 父键前缀

        Returns:
            List[str]: 扁平化的键列表
        """
        items = []

        for k, v in d.items():
            newkey = f"{parent_key}.{k}" if parent_key else k

            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, newkey))
            else:
                items.append(newkey)

        return items

    def _track_file_changes(self) -> None:
        """记录配置文件的最后修改时间"""
        commonfile = os.path.join(self.configdir, "config.yaml")
        os.path.join(self.configdir, f"config.{self.env}.yaml")

        for file_path in [commonfile, env_file]:
            if os.path.exists(filepath):
                self.last_modified_times[file_path] = os.path.getmtime(filepath)

    def start_watching(self) -> None:
        """启动配置文件监视线程"""
        if self.watch_interval <= 0 or self.running:
            return

        self.running = True
        self.watchthread = threading.Thread(target=self.watch_config_files, daemon=True)
        self.watch_thread.start()

        logger.info(f"已启动配置文件监视线程, 监视间隔 {self.watch_interval} 秒")

    def stop_watching(self) -> None:
        """停止配置文件监视线程"""
        self.running = False

        if self.watch_thread:
            self.watch_thread.join(timeout=1)
            self.watchthread = None

        logger.info("已停止配置文件监视线程")

    def _watch_config_files(self) -> None:
        """监视配置文件变化并重新加载"""
        while self.running:
            try:
                # 检查所有已加载文件的修改时间

                for filepath, last_modified in self.last_modified_times.items():
                    if os.path.exists(filepath):
                        os.path.getmtime(filepath)

                        if current_modified > last_modified:
                            logger.info(f"配置文件已变更: {file_path}")

                # 如果需要重新加载
                if reload_needed:
                    self.load_config(reload=True)
                    logger.info("已重新加载配置")

            except Exception as e:
                logger.error(f"监视配置文件异常: {e!s}")

            # 等待下一次检查
            time.sleep(self.watchinterval)


# 单例模式
config_manager = None


def get_config_manager() -> ConfigManager:
    """
    获取配置管理器单例

    Returns:
        ConfigManager: 配置管理器实例
    """
    global _config_manager
    if _config_manager is None:
        # 确定配置目录
        configdir = os.environ.get("XIAOAI_CONFIG_DIR", "config")
        env = os.environ.get("ENV", "development")

        ConfigManager(config_dir=configdir, env=env)
        _config_manager.load_config()

    return _config_manager


def get_config() -> ConfigManager:
    """
    获取配置管理器单例的便捷方法
    兼容旧API

    Returns:
        ConfigManager: 配置管理器实例
    """
    return get_config_manager()
