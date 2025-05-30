"""
增强的配置管理模块
支持动态配置、环境变量、配置验证、热重载等功能
"""

import asyncio
import hashlib
import json
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, Union

import structlog
import yaml
from pydantic import BaseModel, Field, ValidationError
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

logger = structlog.get_logger(__name__)


class ConfigFormat(Enum):
    """配置文件格式"""

    YAML = "yaml"
    JSON = "json"
    ENV = "env"
    TOML = "toml"


class ConfigSource(Enum):
    """配置源"""

    FILE = "file"
    ENVIRONMENT = "environment"
    REMOTE = "remote"
    DATABASE = "database"


@dataclass
class ConfigChange:
    """配置变更"""

    key: str
    old_value: Any
    new_value: Any
    source: ConfigSource
    timestamp: datetime = field(default_factory=datetime.now)


class ConfigValidator(ABC):
    """配置验证器抽象基类"""

    @abstractmethod
    def validate(self, config: Dict[str, Any]) -> bool:
        """验证配置"""
        pass

    @abstractmethod
    def get_errors(self) -> List[str]:
        """获取验证错误"""
        pass


class PydanticConfigValidator(ConfigValidator):
    """基于Pydantic的配置验证器"""

    def __init__(self, model_class: Type[BaseModel]):
        self.model_class = model_class
        self.errors: List[str] = []

    def validate(self, config: Dict[str, Any]) -> bool:
        """验证配置"""
        try:
            self.model_class(**config)
            self.errors = []
            return True
        except ValidationError as e:
            self.errors = [str(error) for error in e.errors()]
            return False

    def get_errors(self) -> List[str]:
        """获取验证错误"""
        return self.errors


class ServiceConfig(BaseModel):
    """服务配置模型"""

    name: str = Field(..., description="服务名称")
    version: str = Field(..., description="服务版本")
    host: str = Field(default="0.0.0.0", description="服务主机")
    port: int = Field(default=9084, ge=1, le=65535, description="服务端口")
    debug: bool = Field(default=False, description="调试模式")
    workers: int = Field(default=4, ge=1, description="工作进程数")


class DatabaseConfig(BaseModel):
    """数据库配置模型"""

    host: str = Field(..., description="数据库主机")
    port: int = Field(..., ge=1, le=65535, description="数据库端口")
    database: str = Field(..., description="数据库名称")
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    pool_size: int = Field(default=20, ge=1, description="连接池大小")
    max_overflow: int = Field(default=30, ge=0, description="最大溢出连接数")
    pool_timeout: int = Field(default=30, ge=1, description="连接池超时")


class XiaokeAgentConfig(BaseModel):
    """小克智能体配置模型"""

    agent_id: str = Field(..., description="智能体ID")
    name: str = Field(..., description="智能体名称")
    version: str = Field(..., description="智能体版本")
    capabilities: List[str] = Field(..., description="智能体能力")
    learning_rate: float = Field(default=0.01, ge=0.0, le=1.0, description="学习率")
    memory_size: int = Field(default=10000, ge=1, description="记忆容量")


class MedicalResourceConfig(BaseModel):
    """医疗资源服务完整配置模型"""

    service: ServiceConfig
    database: Dict[str, DatabaseConfig]
    xiaoke_agent: XiaokeAgentConfig
    tcm_knowledge: Dict[str, Any] = Field(default_factory=dict)
    food_agriculture: Dict[str, Any] = Field(default_factory=dict)
    wellness_tourism: Dict[str, Any] = Field(default_factory=dict)
    resource_scheduler: Dict[str, Any] = Field(default_factory=dict)
    logging: Dict[str, Any] = Field(default_factory=dict)
    cors: Dict[str, Any] = Field(default_factory=dict)
    monitoring: Dict[str, Any] = Field(default_factory=dict)


class ConfigFileWatcher(FileSystemEventHandler):
    """配置文件监控器"""

    def __init__(self, config_manager: "ConfigManager"):
        self.config_manager = config_manager
        self.last_modified = {}

    def on_modified(self, event):
        """文件修改事件处理"""
        if event.is_directory:
            return

        file_path = event.src_path

        # 检查是否是配置文件
        if not self._is_config_file(file_path):
            return

        # 防止重复触发
        current_time = datetime.now()
        if file_path in self.last_modified:
            time_diff = (current_time - self.last_modified[file_path]).total_seconds()
            if time_diff < 1:  # 1秒内的重复事件忽略
                return

        self.last_modified[file_path] = current_time

        # 异步重载配置
        asyncio.create_task(self.config_manager.reload_config(file_path))

    def _is_config_file(self, file_path: str) -> bool:
        """检查是否是配置文件"""
        config_extensions = [".yaml", ".yml", ".json", ".toml"]
        return any(file_path.endswith(ext) for ext in config_extensions)


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_paths: List[str], watch_files: bool = True):
        self.config_paths = config_paths
        self.watch_files = watch_files

        # 配置存储
        self.config: Dict[str, Any] = {}
        self.config_sources: Dict[str, ConfigSource] = {}
        self.config_checksums: Dict[str, str] = {}

        # 验证器
        self.validators: List[ConfigValidator] = []

        # 变更监听器
        self.change_listeners: List[Callable[[ConfigChange], None]] = []

        # 文件监控
        self.file_observer: Optional[Observer] = None
        self.file_watcher: Optional[ConfigFileWatcher] = None

        # 环境变量前缀
        self.env_prefix = "MEDICAL_RESOURCE_"

        # 默认配置
        self.default_config = self._get_default_config()

        logger.info("配置管理器初始化完成")

    async def initialize(self):
        """初始化配置管理器"""
        # 加载默认配置
        self.config = self.default_config.copy()

        # 加载配置文件
        for config_path in self.config_paths:
            await self._load_config_file(config_path)

        # 加载环境变量
        self._load_environment_variables()

        # 验证配置
        await self._validate_config()

        # 启动文件监控
        if self.watch_files:
            await self._start_file_watching()

        logger.info("配置管理器初始化完成")

    async def _load_config_file(self, config_path: str):
        """加载配置文件"""
        try:
            path = Path(config_path)
            if not path.exists():
                logger.warning(f"配置文件不存在: {config_path}")
                return

            # 读取文件内容
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            # 计算校验和
            checksum = hashlib.md5(content.encode()).hexdigest()

            # 检查是否有变化
            if config_path in self.config_checksums:
                if self.config_checksums[config_path] == checksum:
                    return  # 没有变化，跳过

            # 解析配置
            if path.suffix.lower() in [".yaml", ".yml"]:
                file_config = yaml.safe_load(content)
            elif path.suffix.lower() == ".json":
                file_config = json.loads(content)
            else:
                logger.warning(f"不支持的配置文件格式: {config_path}")
                return

            # 合并配置
            old_config = self.config.copy()
            self._merge_config(self.config, file_config)

            # 记录变更
            self._record_changes(old_config, self.config, ConfigSource.FILE)

            # 更新校验和
            self.config_checksums[config_path] = checksum
            self.config_sources[config_path] = ConfigSource.FILE

            logger.info(f"成功加载配置文件: {config_path}")

        except Exception as e:
            logger.error(f"加载配置文件失败 {config_path}: {e}")
            raise

    def _load_environment_variables(self):
        """加载环境变量"""
        old_config = self.config.copy()

        for key, value in os.environ.items():
            if key.startswith(self.env_prefix):
                # 移除前缀并转换为小写
                config_key = key[len(self.env_prefix) :].lower()

                # 转换嵌套键（例如：DATABASE_HOST -> database.host）
                config_path = config_key.split("_")

                # 尝试类型转换
                converted_value = self._convert_env_value(value)

                # 设置配置值
                self._set_nested_config(self.config, config_path, converted_value)

                self.config_sources[config_key] = ConfigSource.ENVIRONMENT

        # 记录变更
        self._record_changes(old_config, self.config, ConfigSource.ENVIRONMENT)

    def _convert_env_value(self, value: str) -> Any:
        """转换环境变量值"""
        # 布尔值
        if value.lower() in ["true", "false"]:
            return value.lower() == "true"

        # 数字
        try:
            if "." in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass

        # JSON
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass

        # 字符串
        return value

    def _set_nested_config(self, config: Dict[str, Any], path: List[str], value: Any):
        """设置嵌套配置值"""
        current = config
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[path[-1]] = value

    def _merge_config(self, target: Dict[str, Any], source: Dict[str, Any]):
        """合并配置"""
        for key, value in source.items():
            if (
                key in target
                and isinstance(target[key], dict)
                and isinstance(value, dict)
            ):
                self._merge_config(target[key], value)
            else:
                target[key] = value

    def _record_changes(
        self,
        old_config: Dict[str, Any],
        new_config: Dict[str, Any],
        source: ConfigSource,
    ):
        """记录配置变更"""
        changes = self._find_config_changes(old_config, new_config, source)

        for change in changes:
            # 通知监听器
            for listener in self.change_listeners:
                try:
                    listener(change)
                except Exception as e:
                    logger.error(f"配置变更监听器执行失败: {e}")

    def _find_config_changes(
        self,
        old_config: Dict[str, Any],
        new_config: Dict[str, Any],
        source: ConfigSource,
        prefix: str = "",
    ) -> List[ConfigChange]:
        """查找配置变更"""
        changes = []

        # 检查新增和修改的键
        for key, new_value in new_config.items():
            full_key = f"{prefix}.{key}" if prefix else key

            if key not in old_config:
                # 新增的键
                changes.append(
                    ConfigChange(
                        key=full_key, old_value=None, new_value=new_value, source=source
                    )
                )
            elif old_config[key] != new_value:
                if isinstance(old_config[key], dict) and isinstance(new_value, dict):
                    # 递归检查嵌套字典
                    changes.extend(
                        self._find_config_changes(
                            old_config[key], new_value, source, full_key
                        )
                    )
                else:
                    # 修改的键
                    changes.append(
                        ConfigChange(
                            key=full_key,
                            old_value=old_config[key],
                            new_value=new_value,
                            source=source,
                        )
                    )

        # 检查删除的键
        for key, old_value in old_config.items():
            if key not in new_config:
                full_key = f"{prefix}.{key}" if prefix else key
                changes.append(
                    ConfigChange(
                        key=full_key, old_value=old_value, new_value=None, source=source
                    )
                )

        return changes

    async def _validate_config(self):
        """验证配置"""
        for validator in self.validators:
            if not validator.validate(self.config):
                errors = validator.get_errors()
                error_msg = f"配置验证失败: {'; '.join(errors)}"
                logger.error(error_msg)
                raise ValueError(error_msg)

        logger.info("配置验证通过")

    async def _start_file_watching(self):
        """启动文件监控"""
        if not self.config_paths:
            return

        self.file_watcher = ConfigFileWatcher(self)
        self.file_observer = Observer()

        # 监控配置文件目录
        watched_dirs = set()
        for config_path in self.config_paths:
            config_dir = Path(config_path).parent
            if config_dir not in watched_dirs:
                self.file_observer.schedule(
                    self.file_watcher, str(config_dir), recursive=False
                )
                watched_dirs.add(config_dir)

        self.file_observer.start()
        logger.info("配置文件监控已启动")

    async def reload_config(self, config_path: Optional[str] = None):
        """重新加载配置"""
        try:
            logger.info(f"重新加载配置: {config_path or 'all'}")

            if config_path:
                # 重新加载指定文件
                await self._load_config_file(config_path)
            else:
                # 重新加载所有配置
                for path in self.config_paths:
                    await self._load_config_file(path)

            # 重新加载环境变量
            self._load_environment_variables()

            # 重新验证配置
            await self._validate_config()

            logger.info("配置重新加载完成")

        except Exception as e:
            logger.error(f"配置重新加载失败: {e}")
            raise

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split(".")
        current = self.config

        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default

        return current

    def set(self, key: str, value: Any, source: ConfigSource = ConfigSource.REMOTE):
        """设置配置值"""
        keys = key.split(".")
        current = self.config

        # 记录旧值
        old_value = self.get(key)

        # 设置新值
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value

        # 记录变更
        change = ConfigChange(
            key=key, old_value=old_value, new_value=value, source=source
        )

        # 通知监听器
        for listener in self.change_listeners:
            try:
                listener(change)
            except Exception as e:
                logger.error(f"配置变更监听器执行失败: {e}")

    def add_validator(self, validator: ConfigValidator):
        """添加配置验证器"""
        self.validators.append(validator)

    def add_change_listener(self, listener: Callable[[ConfigChange], None]):
        """添加配置变更监听器"""
        self.change_listeners.append(listener)

    def get_config_dict(self) -> Dict[str, Any]:
        """获取完整配置字典"""
        return self.config.copy()

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "service": {
                "name": "medical-resource-service",
                "version": "1.0.0",
                "host": "0.0.0.0",
                "port": 9084,
                "debug": False,
                "workers": 4,
            },
            "database": {
                "postgres": {
                    "host": "localhost",
                    "port": 5432,
                    "database": "medical_resources",
                    "username": "postgres",
                    "password": "password",
                    "pool_size": 20,
                    "max_overflow": 30,
                    "pool_timeout": 30,
                },
                "redis": {
                    "host": "localhost",
                    "port": 6379,
                    "database": 0,
                    "max_connections": 20,
                },
                "mongodb": {
                    "host": "localhost",
                    "port": 27017,
                    "database": "medical_analytics",
                },
            },
            "xiaoke_agent": {
                "agent_id": "xiaoke_001",
                "name": "小克",
                "version": "1.0.0",
                "capabilities": [
                    "medical_resource_management",
                    "tcm_knowledge",
                    "food_agriculture",
                    "wellness_tourism",
                ],
                "learning_rate": 0.01,
                "memory_size": 10000,
            },
            "tcm_knowledge": {
                "knowledge_base_path": "/data/tcm_knowledge",
                "enable_learning": True,
                "update_interval": 3600,
            },
            "food_agriculture": {
                "food_database_path": "/data/food_agriculture",
                "enable_seasonal_updates": True,
                "nutrition_api_enabled": True,
            },
            "wellness_tourism": {
                "wellness_database_path": "/data/wellness_tourism",
                "enable_weather_integration": True,
                "booking_api_enabled": False,
            },
            "resource_scheduler": {
                "scheduler_algorithm": "constitution_based",
                "max_queue_size": 1000,
                "scheduling_interval": 60,
                "enable_load_balancing": True,
            },
            "logging": {
                "level": "INFO",
                "file_path": "logs/medical-resource-service.log",
                "format": "text",
                "max_size": "100MB",
                "backup_count": 5,
            },
            "cors": {
                "allow_origins": ["*"],
                "allow_credentials": True,
                "allow_methods": ["*"],
                "allow_headers": ["*"],
            },
            "monitoring": {
                "metrics": {"enabled": True, "port": 9090, "path": "/metrics"},
                "health_check": {"enabled": True, "path": "/health"},
            },
            "cache": {
                "memory": {"enabled": True, "max_size": 1000, "strategy": "lru"},
                "redis": {
                    "enabled": True,
                    "url": "redis://localhost:6379",
                    "prefix": "medical_resource",
                },
                "default_ttl": 3600,
            },
            "performance": {
                "metrics": {
                    "enabled": True,
                    "collection_interval": 30,
                    "retention_period": 3600,
                },
                "alerts": {
                    "enabled": True,
                    "thresholds": {
                        "cpu_percent": 80.0,
                        "memory_percent": 85.0,
                        "response_time_avg": 5.0,
                    },
                },
            },
        }

    async def close(self):
        """关闭配置管理器"""
        if self.file_observer:
            self.file_observer.stop()
            self.file_observer.join()

        logger.info("配置管理器已关闭")


# 全局配置管理器实例
_config_manager: Optional[ConfigManager] = None


async def init_config_manager(
    config_paths: List[str], watch_files: bool = True
) -> ConfigManager:
    """初始化全局配置管理器"""
    global _config_manager

    _config_manager = ConfigManager(config_paths, watch_files)

    # 添加默认验证器
    _config_manager.add_validator(PydanticConfigValidator(MedicalResourceConfig))

    await _config_manager.initialize()
    return _config_manager


def get_config_manager() -> ConfigManager:
    """获取全局配置管理器"""
    if _config_manager is None:
        raise RuntimeError("配置管理器未初始化，请先调用 init_config_manager")
    return _config_manager


def get_config(key: str, default: Any = None) -> Any:
    """获取配置值的便捷函数"""
    return get_config_manager().get(key, default)
