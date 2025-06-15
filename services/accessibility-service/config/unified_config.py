#!/usr/bin/env python

"""
统一配置管理器
合并了基础配置和增强配置的功能，提供完整的配置管理解决方案

功能特性：
- 基础配置加载和管理
- 配置验证和类型检查
- 热重载支持
- 环境变量覆盖
- 配置节属性访问
- 配置导出和保存
"""

import asyncio
import json
import logging
import os
from typing import Any, Callable, Dict, List, Optional, Union

import yaml
from pydantic import BaseModel, Field, ValidationError
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)


# ==================== Pydantic 配置模型 ====================


class ServiceConfig(BaseModel):
    """服务配置模型"""

    name: str = Field(..., description="服务名称")
    version: str = Field(..., description="服务版本")
    host: str = Field(default="0.0.0.0", description="服务主机")
    port: int = Field(default=50051, ge=1, le=65535, description="服务端口")
    data_root: str = Field(..., description="数据根目录")
    debug: bool = Field(default=False, description="调试模式")


class ModelConfig(BaseModel):
    """模型配置模型"""

    scene_model: str = Field(..., description="场景识别模型")
    sign_language_model: str = Field(..., description="手语识别模型")
    speech_model: Dict[str, str] = Field(..., description="语音模型配置")
    conversion_model: str = Field(..., description="内容转换模型")


class LoggingConfig(BaseModel):
    """日志配置模型"""

    level: str = Field(default="INFO", description="日志级别")
    format: str = Field(..., description="日志格式")
    file: Optional[str] = Field(None, description="日志文件路径")
    max_size_mb: int = Field(default=100, ge=1, description="日志文件最大大小(MB)")
    backup_count: int = Field(default=5, ge=1, description="日志文件备份数量")


class DatabaseConfig(BaseModel):
    """数据库配置模型"""

    host: str = Field(..., description="数据库主机")
    port: int = Field(default=5432, ge=1, le=65535, description="数据库端口")
    name: str = Field(..., description="数据库名称")
    user: str = Field(..., description="数据库用户")
    password: str = Field(..., description="数据库密码")
    pool_size: int = Field(default=10, ge=1, description="连接池大小")
    max_overflow: int = Field(default=20, ge=0, description="连接池最大溢出")


class FeatureConfig(BaseModel):
    """功能配置模型"""

    enabled: bool = Field(default=True, description="是否启用")
    max_image_size: Optional[int] = Field(None, ge=1, description="最大图像大小")
    confidence_threshold: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="置信度阈值"
    )
    supported_languages: Optional[List[str]] = Field(None, description="支持的语言")
    supported_dialects: Optional[List[str]] = Field(None, description="支持的方言")
    supported_formats: Optional[List[str]] = Field(None, description="支持的格式")


class CacheConfig(BaseModel):
    """缓存配置模型"""

    memory_max_size_mb: int = Field(
        default=256, ge=1, description="内存缓存最大大小(MB)"
    )
    memory_max_items: int = Field(default=10000, ge=1, description="内存缓存最大项目数")
    redis_enabled: bool = Field(default=False, description="是否启用Redis缓存")
    disk_enabled: bool = Field(default=False, description="是否启用磁盘缓存")
    disk_cache_dir: str = Field(
        default="/tmp/accessibility_cache", description="磁盘缓存目录"
    )
    cleanup_interval_seconds: int = Field(default=300, ge=1, description="清理间隔(秒)")


class SecurityConfig(BaseModel):
    """安全配置模型"""

    encryption_enabled: bool = Field(default=True, description="是否启用加密")
    jwt_secret: str = Field(..., description="JWT密钥")
    jwt_expiry_hours: int = Field(default=24, ge=1, description="JWT过期时间(小时)")
    rate_limit_per_minute: int = Field(default=100, ge=1, description="每分钟请求限制")


class PerformanceConfig(BaseModel):
    """性能配置模型"""

    max_memory_mb: int = Field(default=4096, ge=1, description="最大内存使用(MB)")
    cleanup_interval_seconds: int = Field(default=300, ge=1, description="清理间隔(秒)")
    model_ttl_seconds: int = Field(default=1800, ge=1, description="模型TTL(秒)")
    worker_threads: int = Field(default=4, ge=1, description="工作线程数")


class IntegrationConfig(BaseModel):
    """集成服务配置模型"""

    xiaoai_service: Dict[str, Any] = Field(
        default_factory=dict, description="小艾服务配置"
    )
    xiaoke_service: Dict[str, Any] = Field(
        default_factory=dict, description="小克服务配置"
    )
    laoke_service: Dict[str, Any] = Field(
        default_factory=dict, description="老克服务配置"
    )
    soer_service: Dict[str, Any] = Field(
        default_factory=dict, description="索儿服务配置"
    )


class AccessibilityConfig(BaseModel):
    """完整的无障碍服务配置模型"""

    service: ServiceConfig
    models: ModelConfig
    logging: LoggingConfig
    database: DatabaseConfig
    features: Dict[str, FeatureConfig] = Field(default_factory=dict)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    security: SecurityConfig
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    integration: IntegrationConfig = Field(default_factory=IntegrationConfig)

    class Config:
        extra = "allow"  # 允许额外字段


# ==================== 配置节类 ====================


class ConfigSection:
    """配置节，提供属性形式访问配置"""

    def __init__(self, section_data: Dict[str, Any]):
        """
        初始化配置节

        Args:
            section_data: 节配置数据
        """
        self._data = section_data or {}

    def __getattr__(self, name: str) -> Any:
        """
        通过属性访问配置项

        Args:
            name: 属性名

        Returns:
            配置值，如果值是字典则返回ConfigSection对象
        """
        if name in self._data:
            value = self._data[name]
            if isinstance(value, dict):
                return ConfigSection(value)
            return value
        raise AttributeError(f"配置未定义属性: {name}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项

        Args:
            key: 配置键
            default: 默认值

        Returns:
            配置值
        """
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        设置配置项

        Args:
            key: 配置键
            value: 配置值
        """
        self._data[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典

        Returns:
            字典形式的配置
        """
        return self._data.copy()

    def __contains__(self, key: str) -> bool:
        """检查是否包含指定键"""
        return key in self._data

    def __iter__(self):
        """迭代配置项"""
        return iter(self._data)

    def keys(self):
        """获取所有键"""
        return self._data.keys()

    def values(self):
        """获取所有值"""
        return self._data.values()

    def items(self):
        """获取所有键值对"""
        return self._data.items()


# ==================== 文件监控处理器 ====================


class ConfigFileHandler(FileSystemEventHandler):
    """配置文件变更处理器"""

    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.last_modified = {}

    def on_modified(self, event):
        if event.is_directory:
            return

        file_path = event.src_path
        if not file_path.endswith((".yaml", ".yml", ".json")):
            return

        # 防止重复触发
        current_time = os.path.getmtime(file_path)
        if (
            file_path in self.last_modified
            and current_time <= self.last_modified[file_path]
        ):
            return

        self.last_modified[file_path] = current_time

        logger.info(f"配置文件变更: {file_path}")
        asyncio.create_task(self.config_manager.reload_config())


# ==================== 统一配置管理器 ====================


class UnifiedConfigManager:
    """统一配置管理器"""

    def __init__(
        self,
        config_path: Optional[str] = None,
        watch_changes: bool = True,
        validate_config: bool = True,
    ):
        """
        初始化配置管理器

        Args:
            config_path: 配置文件路径
            watch_changes: 是否监控文件变更
            validate_config: 是否验证配置
        """
        self.config_path = config_path or self._find_config_file()
        self.watch_changes = watch_changes
        self.validate_config = validate_config

        # 配置数据
        self._raw_config: Dict[str, Any] = {}
        self._validated_config: Optional[AccessibilityConfig] = None

        # 配置节
        self._sections: Dict[str, ConfigSection] = {}

        # 文件监控
        self._observer: Optional[Observer] = None
        self._reload_callbacks: List[Callable] = []

        # 环境变量前缀
        self.env_prefix = "ACCESSIBILITY_"

        # 加载配置
        self.load_config()

        # 启动文件监控
        if self.watch_changes:
            self._start_file_watcher()

    def _find_config_file(self) -> str:
        """查找配置文件"""
        possible_paths = [
            os.environ.get("ACCESSIBILITY_CONFIG_PATH"),
            "config/config.yaml",
            "config.yaml",
            "/etc/accessibility-service/config.yaml",
        ]

        for path in possible_paths:
            if path and os.path.exists(path):
                return path

        # 如果没有找到配置文件，创建默认配置
        default_path = "config/config.yaml"
        self._create_default_config(default_path)
        return default_path

    def _create_default_config(self, path: str) -> None:
        """创建默认配置文件"""
        default_config = self._get_default_config()

        # 确保目录存在
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)

        logger.info(f"创建默认配置文件: {path}")

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "service": {
                "name": "accessibility-service",
                "version": "2.0.0",
                "host": "0.0.0.0",
                "port": 50051,
                "data_root": "/var/lib/accessibility-service",
                "debug": False,
            },
            "models": {
                "scene_model": "microsoft/beit-base-patch16-224-pt22k",
                "sign_language_model": "mediapipe/hands",
                "speech_model": {
                    "asr": "silero-models/silero-stt-model",
                    "tts": "silero-models/silero-tts-model",
                },
                "conversion_model": "google/flan-t5-base",
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "/var/log/accessibility-service/service.log",
                "max_size_mb": 100,
                "backup_count": 5,
            },
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "accessibility_db",
                "user": "accessibility_user",
                "password": os.getenv("DB_PASSWORD", "password"),
                "pool_size": 10,
                "max_overflow": 20,
            },
            "features": {
                "blind_assistance": {
                    "enabled": True,
                    "max_image_size": 1024,
                    "confidence_threshold": 0.7,
                },
                "sign_language": {
                    "enabled": True,
                    "supported_languages": ["zh-CN", "en-US"],
                },
                "screen_reading": {
                    "enabled": True,
                    "confidence_threshold": 0.6,
                },
                "voice_assistance": {
                    "enabled": True,
                    "supported_dialects": [
                        "mandarin",
                        "cantonese",
                        "sichuanese",
                        "shanghainese",
                        "hokkien",
                        "hakka",
                        "northeastern",
                        "northwestern",
                    ],
                },
                "content_conversion": {
                    "enabled": True,
                    "supported_formats": ["audio", "simplified", "braille"],
                },
            },
            "cache": {
                "memory_max_size_mb": 256,
                "memory_max_items": 10000,
                "redis_enabled": False,
                "disk_enabled": False,
                "disk_cache_dir": "/tmp/accessibility_cache",
                "cleanup_interval_seconds": 300,
            },
            "security": {
                "encryption_enabled": True,
                "jwt_secret": os.getenv("JWT_SECRET", "your-secret-key"),
                "jwt_expiry_hours": 24,
                "rate_limit_per_minute": 100,
            },
            "performance": {
                "max_memory_mb": 4096,
                "cleanup_interval_seconds": 300,
                "model_ttl_seconds": 1800,
                "worker_threads": 4,
            },
            "integration": {
                "xiaoai_service": {
                    "host": "xiaoai-service",
                    "port": 50052,
                    "timeout_ms": 5000,
                    "retry": 3,
                },
                "xiaoke_service": {
                    "host": "xiaoke-service",
                    "port": 50053,
                    "timeout_ms": 5000,
                    "retry": 3,
                },
                "laoke_service": {
                    "host": "laoke-service",
                    "port": 50054,
                    "timeout_ms": 5000,
                    "retry": 3,
                },
                "soer_service": {
                    "host": "soer-service",
                    "port": 50055,
                    "timeout_ms": 5000,
                    "retry": 3,
                },
            },
        }

    def load_config(self) -> None:
        """加载配置"""
        try:
            logger.info(f"加载配置文件: {self.config_path}")

            # 读取原始配置
            self._raw_config = self._load_raw_config()

            # 应用环境变量覆盖
            self._apply_env_overrides()

            # 验证配置
            if self.validate_config:
                self._validated_config = AccessibilityConfig(**self._raw_config)

            # 初始化配置节
            self._init_sections()

            logger.info("配置加载成功")

        except Exception as e:
            logger.error(f"配置加载失败: {e}")
            # 使用默认配置
            self._raw_config = self._get_default_config()
            self._init_sections()

    def _load_raw_config(self) -> Dict[str, Any]:
        """加载原始配置"""
        with open(self.config_path, "r", encoding="utf-8") as f:
            if self.config_path.endswith(".json"):
                return json.load(f)
            else:
                return yaml.safe_load(f)

    def _apply_env_overrides(self) -> None:
        """应用环境变量覆盖"""
        for key, value in os.environ.items():
            if key.startswith(self.env_prefix):
                config_key = key[len(self.env_prefix) :].lower()
                config_path = config_key.split("_")
                self._set_nested_value(
                    self._raw_config, config_path, self._parse_env_value(value)
                )

    def _set_nested_value(
        self, config: Dict[str, Any], path: List[str], value: Any
    ) -> None:
        """设置嵌套配置值"""
        current = config
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[path[-1]] = value

    def _parse_env_value(self, value: str) -> Any:
        """解析环境变量值"""
        # 尝试解析为JSON
        try:
            return json.loads(value)
        except json.JSONDecodeError:
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
        except ValueError:
            pass

        # 返回字符串
        return value

    def _init_sections(self) -> None:
        """初始化配置节"""
        self._sections = {
            "service": ConfigSection(self._raw_config.get("service", {})),
            "models": ConfigSection(self._raw_config.get("models", {})),
            "logging": ConfigSection(self._raw_config.get("logging", {})),
            "database": ConfigSection(self._raw_config.get("database", {})),
            "features": ConfigSection(self._raw_config.get("features", {})),
            "cache": ConfigSection(self._raw_config.get("cache", {})),
            "security": ConfigSection(self._raw_config.get("security", {})),
            "performance": ConfigSection(self._raw_config.get("performance", {})),
            "integration": ConfigSection(self._raw_config.get("integration", {})),
        }

    def _start_file_watcher(self) -> None:
        """启动文件监控"""
        try:
            self._observer = Observer()
            handler = ConfigFileHandler(self)
            watch_dir = os.path.dirname(self.config_path)
            self._observer.schedule(handler, watch_dir, recursive=False)
            self._observer.start()
            logger.info(f"启动配置文件监控: {watch_dir}")
        except Exception as e:
            logger.warning(f"无法启动文件监控: {e}")

    async def reload_config(self) -> None:
        """重新加载配置"""
        try:
            old_config = self._raw_config.copy()
            self.load_config()

            # 通知回调函数
            for callback in self._reload_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(old_config, self._raw_config)
                    else:
                        callback(old_config, self._raw_config)
                except Exception as e:
                    logger.error(f"配置重载回调失败: {e}")

            logger.info("配置重载完成")
        except Exception as e:
            logger.error(f"配置重载失败: {e}")

    def add_reload_callback(self, callback: Callable) -> None:
        """添加重载回调函数"""
        self._reload_callbacks.append(callback)

    def remove_reload_callback(self, callback: Callable) -> None:
        """移除重载回调函数"""
        if callback in self._reload_callbacks:
            self._reload_callbacks.remove(callback)

    # ==================== 属性访问 ====================

    @property
    def service(self) -> ConfigSection:
        """服务配置"""
        return self._sections["service"]

    @property
    def models(self) -> ConfigSection:
        """模型配置"""
        return self._sections["models"]

    @property
    def logging(self) -> ConfigSection:
        """日志配置"""
        return self._sections["logging"]

    @property
    def database(self) -> ConfigSection:
        """数据库配置"""
        return self._sections["database"]

    @property
    def features(self) -> ConfigSection:
        """功能配置"""
        return self._sections["features"]

    @property
    def cache(self) -> ConfigSection:
        """缓存配置"""
        return self._sections["cache"]

    @property
    def security(self) -> ConfigSection:
        """安全配置"""
        return self._sections["security"]

    @property
    def performance(self) -> ConfigSection:
        """性能配置"""
        return self._sections["performance"]

    @property
    def integration(self) -> ConfigSection:
        """集成配置"""
        return self._sections["integration"]

    @property
    def version(self) -> str:
        """服务版本"""
        return self.service.get("version", "2.0.0")

    @property
    def validated_config(self) -> Optional[AccessibilityConfig]:
        """验证后的配置"""
        return self._validated_config

    # ==================== 配置操作 ====================

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项

        Args:
            key: 配置键，支持点号分隔的嵌套键
            default: 默认值

        Returns:
            配置值
        """
        keys = key.split(".")
        current = self._raw_config

        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default

        return current

    def set(self, key: str, value: Any) -> None:
        """
        设置配置项

        Args:
            key: 配置键，支持点号分隔的嵌套键
            value: 配置值
        """
        keys = key.split(".")
        self._set_nested_value(self._raw_config, keys, value)

        # 重新初始化配置节
        self._init_sections()

    def save(self, path: Optional[str] = None) -> None:
        """
        保存配置到文件

        Args:
            path: 保存路径，默认为当前配置文件路径
        """
        save_path = path or self.config_path

        with open(save_path, "w", encoding="utf-8") as f:
            if save_path.endswith(".json"):
                json.dump(self._raw_config, f, indent=2, ensure_ascii=False)
            else:
                yaml.dump(
                    self._raw_config, f, default_flow_style=False, allow_unicode=True
                )

        logger.info(f"配置已保存到: {save_path}")

    def export_config(self, format: str = "yaml") -> str:
        """
        导出配置

        Args:
            format: 导出格式，支持 yaml 和 json

        Returns:
            配置字符串
        """
        if format.lower() == "json":
            return json.dumps(self._raw_config, indent=2, ensure_ascii=False)
        else:
            return yaml.dump(
                self._raw_config, default_flow_style=False, allow_unicode=True
            )

    def as_dict(self) -> Dict[str, Any]:
        """
        获取配置字典

        Returns:
            配置字典
        """
        return self._raw_config.copy()

    def validate(self) -> bool:
        """
        验证配置

        Returns:
            验证是否通过
        """
        try:
            AccessibilityConfig(**self._raw_config)
            return True
        except ValidationError as e:
            logger.error(f"配置验证失败: {e}")
            return False

    def get_validation_errors(self) -> Optional[List[str]]:
        """
        获取验证错误

        Returns:
            错误列表
        """
        try:
            AccessibilityConfig(**self._raw_config)
            return None
        except ValidationError as e:
            return [str(error) for error in e.errors()]

    def cleanup(self) -> None:
        """清理资源"""
        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._observer = None

        self._reload_callbacks.clear()
        logger.info("配置管理器资源已清理")


# ==================== 全局配置实例 ====================

_config_manager: Optional[UnifiedConfigManager] = None


def get_config_manager(
    config_path: Optional[str] = None,
    watch_changes: bool = True,
    validate_config: bool = True,
) -> UnifiedConfigManager:
    """
    获取全局配置管理器实例

    Args:
        config_path: 配置文件路径
        watch_changes: 是否监控文件变更
        validate_config: 是否验证配置

    Returns:
        配置管理器实例
    """
    global _config_manager

    if _config_manager is None:
        _config_manager = UnifiedConfigManager(
            config_path=config_path,
            watch_changes=watch_changes,
            validate_config=validate_config,
        )

    return _config_manager


def get_config() -> UnifiedConfigManager:
    """
    获取全局配置实例

    Returns:
        配置管理器实例
    """
    return get_config_manager()


def reload_config() -> None:
    """重新加载全局配置"""
    global _config_manager
    if _config_manager:
        asyncio.create_task(_config_manager.reload_config())


# 兼容性别名
config = get_config()
Config = UnifiedConfigManager
ConfigManager = UnifiedConfigManager
