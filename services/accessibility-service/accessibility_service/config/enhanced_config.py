"""
enhanced_config - 索克生活项目模块
"""

from pydantic import BaseModel, Field, ValidationError
from typing import Any
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import asyncio
import json
import logging
import os
import yaml

#!/usr/bin/env python

"""
增强的配置管理器
支持配置验证、热重载、环境变量管理和类型检查
"""



logger = logging.getLogger(__name__)


class ServiceConfig(BaseModel):
    """服务配置模型"""
    name: str = Field(..., description="服务名称")
    version: str = Field(..., description="服务版本")
    host: str = Field(default="0.0.0.0", description="服务主机")
    port: int = Field(default=50051, ge=1, le=65535, description="服务端口")
    data_root: str = Field(..., description="数据根目录")

    class Meta:
        # 性能优化: 添加常用查询字段的索引
        indexes = [
            # 根据实际查询需求添加索引
            # models.Index(fields=['created_at']),
            # models.Index(fields=['user_id']),
            # models.Index(fields=['status']),
        ]
        # 数据库表选项
        db_table = 'serviceconfig'
        ordering = ['-created_at']

    class Meta:
        # 性能优化: 添加常用查询字段的索引
        indexes = [
            # 根据实际查询需求添加索引
            # models.Index(fields=['created_at']),
            # models.Index(fields=['user_id']),
            # models.Index(fields=['status']),
        ]
        # 数据库表选项
        db_table = 'loggingconfig'
        ordering = ['-created_at']

    class Meta:
        # 性能优化: 添加常用查询字段的索引
        indexes = [
            # 根据实际查询需求添加索引
            # models.Index(fields=['created_at']),
            # models.Index(fields=['user_id']),
            # models.Index(fields=['status']),
        ]
        # 数据库表选项
        db_table = 'databaseconfig'
        ordering = ['-created_at']


class ModelConfig(BaseModel):
    """模型配置模型"""
    scene_model: str = Field(..., description="场景识别模型")
    sign_language_model: str = Field(..., description="手语识别模型")
    speech_model: dict[str, str] = Field(..., description="语音模型配置")
    conversion_model: str = Field(..., description="内容转换模型")

    class Meta:
        # 性能优化: 添加常用查询字段的索引
        indexes = [
            # 根据实际查询需求添加索引
            # models.Index(fields=['created_at']),
            # models.Index(fields=['user_id']),
            # models.Index(fields=['status']),
        ]
        # 数据库表选项
        db_table = 'featureconfig'
        ordering = ['-created_at']

    class Meta:
        # 性能优化: 添加常用查询字段的索引
        indexes = [
            # 根据实际查询需求添加索引
            # models.Index(fields=['created_at']),
            # models.Index(fields=['user_id']),
            # models.Index(fields=['status']),
        ]
        # 数据库表选项
        db_table = 'cacheconfig'
        ordering = ['-created_at']

    class Meta:
        # 性能优化: 添加常用查询字段的索引
        indexes = [
            # 根据实际查询需求添加索引
            # models.Index(fields=['created_at']),
            # models.Index(fields=['user_id']),
            # models.Index(fields=['status']),
        ]
        # 数据库表选项
        db_table = 'modelmanagerconfig'
        ordering = ['-created_at']

    class Meta:
        # 性能优化: 添加常用查询字段的索引
        indexes = [
            # 根据实际查询需求添加索引
            # models.Index(fields=['created_at']),
            # models.Index(fields=['user_id']),
            # models.Index(fields=['status']),
        ]
        # 数据库表选项
        db_table = 'securityconfig'
        ordering = ['-created_at']

    class Meta:
        # 性能优化: 添加常用查询字段的索引
        indexes = [
            # 根据实际查询需求添加索引
            # models.Index(fields=['created_at']),
            # models.Index(fields=['user_id']),
            # models.Index(fields=['status']),
        ]
        # 数据库表选项
        db_table = 'accessibilityconfig'
        ordering = ['-created_at']


class LoggingConfig(BaseModel):
    """日志配置模型"""
    level: str = Field(default="INFO", description="日志级别")
    format: str = Field(..., description="日志格式")
    file: str | None = Field(None, description="日志文件路径")
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
    max_image_size: int | None = Field(None, ge=1, description="最大图像大小")
    confidence_threshold: float | None = Field(None, ge=0.0, le=1.0, description="置信度阈值")


class CacheConfig(BaseModel):
    """缓存配置模型"""
    memory_max_size_mb: int = Field(default=256, ge=1, description="内存缓存最大大小(MB)")
    memory_max_items: int = Field(default=10000, ge=1, description="内存缓存最大项目数")
    redis_enabled: bool = Field(default=False, description="是否启用Redis缓存")
    disk_enabled: bool = Field(default=False, description="是否启用磁盘缓存")
    disk_cache_dir: str = Field(default="/tmp/accessibility_cache", description="磁盘缓存目录")
    cleanup_interval_seconds: int = Field(default=300, ge=1, description="清理间隔(秒)")


class ModelManagerConfig(BaseModel):
    """模型管理器配置模型"""
    max_memory_mb: int = Field(default=4096, ge=1, description="最大内存使用(MB)")
    cleanup_interval_seconds: int = Field(default=300, ge=1, description="清理间隔(秒)")
    model_ttl_seconds: int = Field(default=1800, ge=1, description="模型TTL(秒)")


class SecurityConfig(BaseModel):
    """安全配置模型"""
    encryption_enabled: bool = Field(default=True, description="是否启用加密")
    jwt_secret: str = Field(..., description="JWT密钥")
    jwt_expiry_hours: int = Field(default=24, ge=1, description="JWT过期时间(小时)")
    rate_limit_per_minute: int = Field(default=100, ge=1, description="每分钟请求限制")


class AccessibilityConfig(BaseModel):
    """完整的无障碍服务配置模型"""
    service: ServiceConfig
    models: ModelConfig
    logging: LoggingConfig
    database: DatabaseConfig
    features: dict[str, FeatureConfig] = Field(default_factory=dict)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    model_manager: ModelManagerConfig = Field(default_factory=ModelManagerConfig)
    security: SecurityConfig

    class Config:
        extra = "allow"  # 允许额外字段


class ConfigFileHandler(FileSystemEventHandler):
    """配置文件变更处理器"""

    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.last_modified = {}

    def on_modified(self, event):
        if event.is_directory:
            return

        file_path = event.src_path
        if not file_path.endswith(('.yaml', '.yml', '.json')):
            return

        # 防止重复触发
        current_time = os.path.getmtime(file_path)
        if file_path in self.last_modified and current_time <= self.last_modified[file_path]:
            return

        self.last_modified[file_path] = current_time

        logger.info(f"配置文件变更: {file_path}")
        asyncio.create_task(self.config_manager.reload_config())


class EnhancedConfigManager:
    """增强的配置管理器"""

    def __init__(self, config_path: str = None, watch_changes: bool = True):
        self.config_path = config_path or self._find_config_file()
        self.watch_changes = watch_changes
        self._config: AccessibilityConfig | None = None
        self._raw_config: dict[str, Any] = {}
        self._observer: Observer | None = None
        self._reload_callbacks: list[callable] = []

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
            os.environ.get('ACCESSIBILITY_CONFIG_PATH'),
            'config/config.yaml',
            'config.yaml',
            '/etc/accessibility-service/config.yaml'
        ]

        for path in possible_paths:
            if path and os.path.exists(path):
                return path

        raise FileNotFoundError("未找到配置文件")

    def load_config(self):
        """加载配置"""
        try:
            logger.info(f"加载配置文件: {self.config_path}")

            # 读取原始配置
            self._raw_config = self._load_raw_config()

            # 应用环境变量覆盖
            self._apply_env_overrides()

            # 验证配置
            self._config = AccessibilityConfig(**self._raw_config)

            logger.info("配置加载成功")

        except Exception as e:
            logger.error(f"配置加载失败: {str(e)}")
            raise

    def _load_raw_config(self) -> dict[str, Any]:
        """加载原始配置"""
        with open(self.config_path, encoding='utf-8') as f:
            if self.config_path.endswith('.json'):
                return json.load(f)
            else:
                return yaml.safe_load(f)

    def _apply_env_overrides(self):
        """应用环境变量覆盖"""
        for key, value in os.environ.items():
            if not key.startswith(self.env_prefix):
                continue

            # 移除前缀并转换为配置路径
            config_key = key[len(self.env_prefix):].lower()
            config_path = config_key.split('_')

            # 应用覆盖
            self._set_nested_value(self._raw_config, config_path, self._parse_env_value(value))

    def _set_nested_value(self, config: dict[str, Any], path: list[str], value: Any):
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
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'

        # 尝试解析为数字
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass

        # 返回字符串
        return value

    def _start_file_watcher(self):
        """启动文件监控"""
        try:
            self._observer = Observer()
            handler = ConfigFileHandler(self)

            config_dir = os.path.dirname(os.path.abspath(self.config_path))
            self._observer.schedule(handler, config_dir, recursive=False)
            self._observer.start()

            logger.info(f"配置文件监控已启动: {config_dir}")

        except Exception as e:
            logger.warning(f"启动配置文件监控失败: {str(e)}")

    async def reload_config(self):
        """重新加载配置"""
        try:
            logger.info("重新加载配置")

            old_config = self._config
            self.load_config()

            # 通知回调函数
            for callback in self._reload_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(old_config, self._config)
                    else:
                        callback(old_config, self._config)
                except Exception as e:
                    logger.error(f"配置重载回调失败: {str(e)}")

            logger.info("配置重新加载完成")

        except Exception as e:
            logger.error(f"配置重新加载失败: {str(e)}")

    def add_reload_callback(self, callback: callable):
        """添加配置重载回调"""
        self._reload_callbacks.append(callback)

    def remove_reload_callback(self, callback: callable):
        """移除配置重载回调"""
        if callback in self._reload_callbacks:
            self._reload_callbacks.remove(callback)

    @property
    def config(self) -> AccessibilityConfig:
        """获取配置"""
        return self._config

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        try:
            keys = key.split('.')
            value = self._raw_config

            for k in keys:
                value = value[k]

            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any):
        """设置配置值（仅在内存中）"""
        keys = key.split('.')
        self._set_nested_value(self._raw_config, keys, value)

        # 重新验证配置
        try:
            self._config = AccessibilityConfig(**self._raw_config)
        except ValidationError as e:
            logger.error(f"配置验证失败: {str(e)}")
            raise

    def validate_config(self, config_dict: dict[str, Any]) -> bool:
        """验证配置"""
        try:
            AccessibilityConfig(**config_dict)
            return True
        except ValidationError as e:
            logger.error(f"配置验证失败: {str(e)}")
            return False

    def get_config_schema(self) -> dict[str, Any]:
        """获取配置模式"""
        return AccessibilityConfig.schema()

    def export_config(self, format: str = 'yaml') -> str:
        """导出配置"""
        if format.lower() == 'json':
            return json.dumps(self._raw_config, indent=2, ensure_ascii=False)
        else:
            return yaml.dump(self._raw_config, default_flow_style=False, allow_unicode=True)

    def save_config(self, path: str = None):
        """保存配置到文件"""
        save_path = path or self.config_path

        with open(save_path, 'w', encoding='utf-8') as f:
            if save_path.endswith('.json'):
                json.dump(self._raw_config, f, indent=2, ensure_ascii=False)
            else:
                yaml.dump(self._raw_config, f, default_flow_style=False, allow_unicode=True)

        logger.info(f"配置已保存到: {save_path}")

    def get_env_vars_info(self) -> list[dict[str, Any]]:
        """获取环境变量信息"""
        env_vars = []

        def extract_env_vars(obj, prefix=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_prefix = f"{prefix}_{key}".upper() if prefix else key.upper()
                    extract_env_vars(value, new_prefix)
            else:
                env_var_name = f"{self.env_prefix}{prefix}"
                env_vars.append({
                    'name': env_var_name,
                    'current_value': os.environ.get(env_var_name),
                    'config_path': prefix.lower().replace('_', '.'),
                    'type': type(obj).__name__
                })

        extract_env_vars(self._raw_config)
        return env_vars

    def cleanup(self):
        """清理资源"""
        if self._observer:
            self._observer.stop()
            self._observer.join()

        logger.info("配置管理器清理完成")


# 全局配置管理器实例
config_manager: EnhancedConfigManager | None = None


def get_config_manager() -> EnhancedConfigManager:
    """获取配置管理器实例"""
    global config_manager
    if config_manager is None:
        config_manager = EnhancedConfigManager()
    return config_manager


def get_config() -> AccessibilityConfig:
    """获取配置"""
    return get_config_manager().config


def reload_config():
    """重新加载配置"""
    return get_config_manager().reload_config()
