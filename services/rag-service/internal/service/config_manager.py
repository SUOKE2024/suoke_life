"""
config_manager - 索克生活项目模块
"""

            import configparser
        import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from loguru import logger
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable, Type
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import asyncio
import json
import os
import toml
import yaml

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理系统 - 支持动态配置更新、环境变量、配置验证和热重载
"""


class ConfigFormat(Enum):
    """配置文件格式"""
    JSON = "json"
    YAML = "yaml"
    TOML = "toml"
    ENV = "env"
    INI = "ini"

class ConfigSource(Enum):
    """配置源"""
    FILE = "file"               # 文件
    ENVIRONMENT = "environment" # 环境变量
    REDIS = "redis"            # Redis
    DATABASE = "database"       # 数据库
    CONSUL = "consul"          # Consul
    ETCD = "etcd"              # etcd
    KUBERNETES = "kubernetes"   # Kubernetes ConfigMap

class ConfigPriority(Enum):
    """配置优先级"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class ConfigItem:
    """配置项"""
    key: str
    value: Any
    source: ConfigSource
    priority: ConfigPriority = ConfigPriority.MEDIUM
    description: str = ""
    data_type: str = "str"
    required: bool = False
    default_value: Any = None
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)
    version: str = "1.0"
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConfigChangeEvent:
    """配置变更事件"""
    key: str
    old_value: Any
    new_value: Any
    source: ConfigSource
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None
    reason: Optional[str] = None

class ConfigValidator:
    """配置验证器"""
    
    @staticmethod
    def validate_type(value: Any, expected_type: str) -> bool:
        """验证数据类型"""
        type_mapping = {
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict
        }
        
        expected_python_type = type_mapping.get(expected_type)
        if expected_python_type is None:
            return True
        
        return isinstance(value, expected_python_type)
    
    @staticmethod
    def validate_range(value: Union[int, float], min_val: Optional[Union[int, float]] = None, 
                      max_val: Optional[Union[int, float]] = None) -> bool:
        """验证数值范围"""
        if min_val is not None and value < min_val:
            return False
        if max_val is not None and value > max_val:
            return False
        return True
    
    @staticmethod
    def validate_length(value: Union[str, list, dict], min_len: Optional[int] = None,
                       max_len: Optional[int] = None) -> bool:
        """验证长度"""
        length = len(value)
        if min_len is not None and length < min_len:
            return False
        if max_len is not None and length > max_len:
            return False
        return True
    
    @staticmethod
    def validate_pattern(value: str, pattern: str) -> bool:
        """验证正则表达式模式"""
        try:
            return bool(re.match(pattern, value))
        except re.error:
            return False
    
    @staticmethod
    def validate_enum(value: Any, allowed_values: List[Any]) -> bool:
        """验证枚举值"""
        return value in allowed_values

class ConfigFileWatcher(FileSystemEventHandler):
    """配置文件监控器"""
    
    def __init__(self, config_manager: 'ConfigManager'):
        self.config_manager = config_manager
        self.last_modified = {}
    
    def on_modified(self, event):
        """文件修改事件"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # 检查是否是配置文件
        if file_path.suffix.lower() in ['.json', '.yaml', '.yml', '.toml', '.env', '.ini']:
            # 防止重复触发
            current_time = datetime.now()
            last_time = self.last_modified.get(str(file_path))
            
            if last_time and (current_time - last_time).total_seconds() < 1:
                return
            
            self.last_modified[str(file_path)] = current_time
            
            # 异步重新加载配置
            asyncio.create_task(self.config_manager._reload_config_file(file_path))

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化配置管理器
        
        Args:
            config: 基础配置信息
        """
        self.base_config = config
        
        # 配置存储
        self.config_items: Dict[str, ConfigItem] = {}
        
        # 配置源
        self.config_sources: Dict[ConfigSource, Dict[str, Any]] = {}
        
        # Redis连接
        self.redis_client = None
        
        # 文件监控器
        self.file_observer = None
        self.watched_files: Set[Path] = set()
        
        # 变更回调
        self.change_callbacks: List[Callable[[ConfigChangeEvent], None]] = []
        
        # 配置缓存
        self.config_cache: Dict[str, Any] = {}
        self.cache_ttl = 300  # 5分钟缓存
        self.cache_timestamps: Dict[str, datetime] = {}
        
        # 配置历史
        self.config_history: List[ConfigChangeEvent] = []
        self.max_history_size = 1000
        
        # 配置模板
        self.config_templates: Dict[str, Dict[str, Any]] = {}
        
        # 环境配置
        self.environment = os.getenv('ENVIRONMENT', 'development')
        
        # 加密密钥
        self.encryption_key = config.get('encryption_key')
        
        # 配置锁
        self.config_lock = asyncio.Lock()
        
        # 统计信息
        self.stats = {
            "total_configs": 0,
            "configs_by_source": {},
            "configs_by_priority": {},
            "reload_count": 0,
            "validation_errors": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
    
    async def initialize(self):
        """初始化配置管理器"""
        logger.info("Initializing config manager")
        
        # 初始化Redis
        await self._init_redis()
        
        # 加载配置模板
        await self._load_config_templates()
        
        # 加载配置源
        await self._load_config_sources()
        
        # 启动文件监控
        await self._start_file_watcher()
        
        # 启动后台任务
        asyncio.create_task(self._config_sync_loop())
        asyncio.create_task(self._cache_cleanup_loop())
        asyncio.create_task(self._health_check_loop())
        
        logger.info("Config manager initialized successfully")
    
    async def _init_redis(self):
        """初始化Redis"""
        redis_config = self.base_config.get('redis', {})
        if redis_config:
            self.redis_client = redis.Redis(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                db=redis_config.get('db', 3),
                decode_responses=True
            )
    
    async def _load_config_templates(self):
        """加载配置模板"""
        templates_dir = Path(self.base_config.get('templates_dir', './config/templates'))
        
        if templates_dir.exists():
            for template_file in templates_dir.glob('*.yaml'):
                try:
                    with open(template_file, 'r', encoding='utf-8') as f:
                        template_data = yaml.safe_load(f)
                    
                    template_name = template_file.stem
                    self.config_templates[template_name] = template_data
                    
                    logger.info(f"Loaded config template: {template_name}")
                    
                except Exception as e:
                    logger.error(f"Error loading template {template_file}: {e}")
    
    async def _load_config_sources(self):
        """加载配置源"""
        sources_config = self.base_config.get('sources', {})
        
        # 加载文件配置
        file_sources = sources_config.get('files', [])
        for file_config in file_sources:
            await self._load_file_source(file_config)
        
        # 加载环境变量配置
        if sources_config.get('environment', {}).get('enabled', True):
            await self._load_environment_source()
        
        # 加载Redis配置
        if sources_config.get('redis', {}).get('enabled', False):
            await self._load_redis_source()
        
        # 加载其他配置源
        # TODO: 实现Consul、etcd、Kubernetes等配置源
    
    async def _load_file_source(self, file_config: Dict[str, Any]):
        """加载文件配置源"""
        file_path = Path(file_config['path'])
        
        if not file_path.exists():
            logger.warning(f"Config file not found: {file_path}")
            return
        
        try:
            # 检测文件格式
            file_format = self._detect_file_format(file_path)
            
            # 读取文件内容
            content = await self._read_config_file(file_path, file_format)
            
            # 解析配置项
            priority = ConfigPriority(file_config.get('priority', ConfigPriority.MEDIUM.value))
            prefix = file_config.get('prefix', '')
            
            await self._parse_config_content(
                content, 
                ConfigSource.FILE, 
                priority, 
                prefix,
                metadata={'file_path': str(file_path), 'format': file_format.value}
            )
            
            # 添加到监控列表
            self.watched_files.add(file_path)
            
            logger.info(f"Loaded config file: {file_path}")
            
        except Exception as e:
            logger.error(f"Error loading config file {file_path}: {e}")
    
    async def _load_environment_source(self):
        """加载环境变量配置源"""
        env_prefix = self.base_config.get('sources', {}).get('environment', {}).get('prefix', 'SUOKE_')
        
        for key, value in os.environ.items():
            if key.startswith(env_prefix):
                config_key = key[len(env_prefix):].lower().replace('_', '.')
                
                # 尝试转换数据类型
                parsed_value = self._parse_env_value(value)
                
                config_item = ConfigItem(
                    key=config_key,
                    value=parsed_value,
                    source=ConfigSource.ENVIRONMENT,
                    priority=ConfigPriority.HIGH,
                    data_type=type(parsed_value).__name__,
                    metadata={'env_key': key}
                )
                
                await self._set_config_item(config_item)
        
        logger.info(f"Loaded environment variables with prefix: {env_prefix}")
    
    async def _load_redis_source(self):
        """加载Redis配置源"""
        if not self.redis_client:
            return
        
        try:
            redis_prefix = self.base_config.get('sources', {}).get('redis', {}).get('prefix', 'config:')
            
            # 获取所有配置键
            keys = await self.redis_client.keys(f"{redis_prefix}*")
            
            for key in keys:
                config_key = key[len(redis_prefix):]
                value_str = await self.redis_client.get(key)
                
                if value_str:
                    try:
                        # 尝试解析JSON
                        value = json.loads(value_str)
                    except json.JSONDecodeError:
                        value = value_str
                    
                    config_item = ConfigItem(
                        key=config_key,
                        value=value,
                        source=ConfigSource.REDIS,
                        priority=ConfigPriority.HIGH,
                        data_type=type(value).__name__,
                        metadata={'redis_key': key}
                    )
                    
                    await self._set_config_item(config_item)
            
            logger.info(f"Loaded Redis configs with prefix: {redis_prefix}")
            
        except Exception as e:
            logger.error(f"Error loading Redis configs: {e}")
    
    def _detect_file_format(self, file_path: Path) -> ConfigFormat:
        """检测文件格式"""
        suffix = file_path.suffix.lower()
        
        format_mapping = {
            '.json': ConfigFormat.JSON,
            '.yaml': ConfigFormat.YAML,
            '.yml': ConfigFormat.YAML,
            '.toml': ConfigFormat.TOML,
            '.env': ConfigFormat.ENV,
            '.ini': ConfigFormat.INI
        }
        
        return format_mapping.get(suffix, ConfigFormat.JSON)
    
    async def _read_config_file(self, file_path: Path, file_format: ConfigFormat) -> Dict[str, Any]:
        """读取配置文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if file_format == ConfigFormat.JSON:
            return json.loads(content)
        elif file_format == ConfigFormat.YAML:
            return yaml.safe_load(content)
        elif file_format == ConfigFormat.TOML:
            return toml.loads(content)
        elif file_format == ConfigFormat.ENV:
            return self._parse_env_file(content)
        elif file_format == ConfigFormat.INI:
            parser = configparser.ConfigParser()
            parser.read_string(content)
            return {section: dict(parser[section]) for section in parser.sections()}
        else:
            raise ValueError(f"Unsupported config format: {file_format}")
    
    def _parse_env_file(self, content: str) -> Dict[str, Any]:
        """解析.env文件"""
        config = {}
        
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    config[key] = self._parse_env_value(value)
        
        return config
    
    def _parse_env_value(self, value: str) -> Any:
        """解析环境变量值"""
        # 尝试解析为布尔值
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # 尝试解析为整数
        try:
            return int(value)
        except ValueError:
            pass
        
        # 尝试解析为浮点数
        try:
            return float(value)
        except ValueError:
            pass
        
        # 尝试解析为JSON
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass
        
        # 返回字符串
        return value
    
    async def _parse_config_content(
        self,
        content: Dict[str, Any],
        source: ConfigSource,
        priority: ConfigPriority,
        prefix: str = '',
        metadata: Optional[Dict[str, Any]] = None
    ):
        """解析配置内容"""
        def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
            """扁平化字典"""
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key, sep=sep).items())
                else:
                    items.append((new_key, v))
            return dict(items)
        
        # 扁平化配置
        flat_config = flatten_dict(content)
        
        for key, value in flat_config.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            config_item = ConfigItem(
                key=full_key,
                value=value,
                source=source,
                priority=priority,
                data_type=type(value).__name__,
                metadata=metadata or {}
            )
            
            await self._set_config_item(config_item)
    
    async def _set_config_item(self, config_item: ConfigItem):
        """设置配置项"""
        async with self.config_lock:
            existing_item = self.config_items.get(config_item.key)
            
            # 检查优先级
            if existing_item and existing_item.priority.value > config_item.priority.value:
                logger.debug(f"Skipping config {config_item.key} due to lower priority")
                return
            
            # 验证配置项
            if not await self._validate_config_item(config_item):
                self.stats["validation_errors"] += 1
                logger.error(f"Validation failed for config: {config_item.key}")
                return
            
            # 记录变更事件
            old_value = existing_item.value if existing_item else None
            if old_value != config_item.value:
                change_event = ConfigChangeEvent(
                    key=config_item.key,
                    old_value=old_value,
                    new_value=config_item.value,
                    source=config_item.source
                )
                
                await self._record_change_event(change_event)
                await self._notify_change_callbacks(change_event)
            
            # 更新配置项
            self.config_items[config_item.key] = config_item
            
            # 清除缓存
            if config_item.key in self.config_cache:
                del self.config_cache[config_item.key]
                del self.cache_timestamps[config_item.key]
            
            # 更新统计信息
            self.stats["total_configs"] = len(self.config_items)
            self.stats["configs_by_source"][config_item.source.value] = \
                self.stats["configs_by_source"].get(config_item.source.value, 0) + 1
            self.stats["configs_by_priority"][config_item.priority.value] = \
                self.stats["configs_by_priority"].get(config_item.priority.value, 0) + 1
    
    async def _validate_config_item(self, config_item: ConfigItem) -> bool:
        """验证配置项"""
        # 类型验证
        if not ConfigValidator.validate_type(config_item.value, config_item.data_type):
            logger.error(f"Type validation failed for {config_item.key}: expected {config_item.data_type}")
            return False
        
        # 自定义验证规则
        validation_rules = config_item.validation_rules
        
        if 'min' in validation_rules or 'max' in validation_rules:
            if not ConfigValidator.validate_range(
                config_item.value,
                validation_rules.get('min'),
                validation_rules.get('max')
            ):
                logger.error(f"Range validation failed for {config_item.key}")
                return False
        
        if 'min_length' in validation_rules or 'max_length' in validation_rules:
            if not ConfigValidator.validate_length(
                config_item.value,
                validation_rules.get('min_length'),
                validation_rules.get('max_length')
            ):
                logger.error(f"Length validation failed for {config_item.key}")
                return False
        
        if 'pattern' in validation_rules:
            if not ConfigValidator.validate_pattern(config_item.value, validation_rules['pattern']):
                logger.error(f"Pattern validation failed for {config_item.key}")
                return False
        
        if 'enum' in validation_rules:
            if not ConfigValidator.validate_enum(config_item.value, validation_rules['enum']):
                logger.error(f"Enum validation failed for {config_item.key}")
                return False
        
        return True
    
    async def _record_change_event(self, change_event: ConfigChangeEvent):
        """记录变更事件"""
        self.config_history.append(change_event)
        
        # 限制历史记录大小
        if len(self.config_history) > self.max_history_size:
            self.config_history = self.config_history[-self.max_history_size:]
        
        # 保存到Redis
        if self.redis_client:
            try:
                event_data = {
                    "key": change_event.key,
                    "old_value": change_event.old_value,
                    "new_value": change_event.new_value,
                    "source": change_event.source.value,
                    "timestamp": change_event.timestamp.isoformat(),
                    "user_id": change_event.user_id,
                    "reason": change_event.reason
                }
                
                await self.redis_client.lpush(
                    "config_history",
                    json.dumps(event_data)
                )
                
                # 限制Redis中的历史记录
                await self.redis_client.ltrim("config_history", 0, self.max_history_size - 1)
                
            except Exception as e:
                logger.error(f"Error saving change event to Redis: {e}")
    
    async def _notify_change_callbacks(self, change_event: ConfigChangeEvent):
        """通知变更回调"""
        for callback in self.change_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(change_event)
                else:
                    callback(change_event)
            except Exception as e:
                logger.error(f"Error in config change callback: {e}")
    
    async def _start_file_watcher(self):
        """启动文件监控"""
        if not self.watched_files:
            return
        
        self.file_observer = Observer()
        
        # 监控所有配置文件的目录
        watched_dirs = set()
        for file_path in self.watched_files:
            watched_dirs.add(file_path.parent)
        
        for watch_dir in watched_dirs:
            if watch_dir.exists():
                event_handler = ConfigFileWatcher(self)
                self.file_observer.schedule(event_handler, str(watch_dir), recursive=False)
        
        self.file_observer.start()
        logger.info(f"Started file watcher for {len(watched_dirs)} directories")
    
    async def _reload_config_file(self, file_path: Path):
        """重新加载配置文件"""
        logger.info(f"Reloading config file: {file_path}")
        
        try:
            # 查找对应的文件配置
            sources_config = self.base_config.get('sources', {})
            file_sources = sources_config.get('files', [])
            
            for file_config in file_sources:
                if Path(file_config['path']) == file_path:
                    await self._load_file_source(file_config)
                    self.stats["reload_count"] += 1
                    break
            
        except Exception as e:
            logger.error(f"Error reloading config file {file_path}: {e}")
    
    async def get_config(self, key: str, default: Any = None, use_cache: bool = True) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键
            default: 默认值
            use_cache: 是否使用缓存
            
        Returns:
            配置值
        """
        # 检查缓存
        if use_cache and key in self.config_cache:
            cache_time = self.cache_timestamps.get(key)
            if cache_time and (datetime.now() - cache_time).total_seconds() < self.cache_ttl:
                self.stats["cache_hits"] += 1
                return self.config_cache[key]
        
        self.stats["cache_misses"] += 1
        
        # 获取配置项
        config_item = self.config_items.get(key)
        if config_item is None:
            return default
        
        value = config_item.value
        
        # 更新缓存
        if use_cache:
            self.config_cache[key] = value
            self.cache_timestamps[key] = datetime.now()
        
        return value
    
    async def set_config(
        self,
        key: str,
        value: Any,
        source: ConfigSource = ConfigSource.REDIS,
        priority: ConfigPriority = ConfigPriority.HIGH,
        user_id: Optional[str] = None,
        reason: Optional[str] = None
    ) -> bool:
        """
        设置配置值
        
        Args:
            key: 配置键
            value: 配置值
            source: 配置源
            priority: 优先级
            user_id: 用户ID
            reason: 变更原因
            
        Returns:
            是否成功
        """
        try:
            config_item = ConfigItem(
                key=key,
                value=value,
                source=source,
                priority=priority,
                data_type=type(value).__name__
            )
            
            await self._set_config_item(config_item)
            
            # 如果是Redis源，同步到Redis
            if source == ConfigSource.REDIS and self.redis_client:
                redis_prefix = self.base_config.get('sources', {}).get('redis', {}).get('prefix', 'config:')
                redis_key = f"{redis_prefix}{key}"
                
                if isinstance(value, (dict, list)):
                    value_str = json.dumps(value)
                else:
                    value_str = str(value)
                
                await self.redis_client.set(redis_key, value_str)
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting config {key}: {e}")
            return False
    
    async def delete_config(self, key: str, user_id: Optional[str] = None) -> bool:
        """
        删除配置
        
        Args:
            key: 配置键
            user_id: 用户ID
            
        Returns:
            是否成功
        """
        try:
            if key not in self.config_items:
                return False
            
            config_item = self.config_items[key]
            
            # 记录变更事件
            change_event = ConfigChangeEvent(
                key=key,
                old_value=config_item.value,
                new_value=None,
                source=config_item.source,
                user_id=user_id,
                reason="删除配置"
            )
            
            await self._record_change_event(change_event)
            await self._notify_change_callbacks(change_event)
            
            # 删除配置项
            del self.config_items[key]
            
            # 清除缓存
            if key in self.config_cache:
                del self.config_cache[key]
                del self.cache_timestamps[key]
            
            # 如果是Redis源，从Redis删除
            if config_item.source == ConfigSource.REDIS and self.redis_client:
                redis_prefix = self.base_config.get('sources', {}).get('redis', {}).get('prefix', 'config:')
                redis_key = f"{redis_prefix}{key}"
                await self.redis_client.delete(redis_key)
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting config {key}: {e}")
            return False
    
    async def get_configs_by_prefix(self, prefix: str) -> Dict[str, Any]:
        """
        根据前缀获取配置
        
        Args:
            prefix: 配置前缀
            
        Returns:
            配置字典
        """
        configs = {}
        
        for key, config_item in self.config_items.items():
            if key.startswith(prefix):
                configs[key] = config_item.value
        
        return configs
    
    async def get_configs_by_source(self, source: ConfigSource) -> Dict[str, Any]:
        """
        根据配置源获取配置
        
        Args:
            source: 配置源
            
        Returns:
            配置字典
        """
        configs = {}
        
        for key, config_item in self.config_items.items():
            if config_item.source == source:
                configs[key] = config_item.value
        
        return configs
    
    async def get_config_info(self, key: str) -> Optional[ConfigItem]:
        """
        获取配置项详细信息
        
        Args:
            key: 配置键
            
        Returns:
            配置项信息
        """
        return self.config_items.get(key)
    
    async def list_all_configs(self) -> Dict[str, ConfigItem]:
        """
        列出所有配置
        
        Returns:
            所有配置项
        """
        return self.config_items.copy()
    
    async def search_configs(self, query: str) -> Dict[str, ConfigItem]:
        """
        搜索配置
        
        Args:
            query: 搜索查询
            
        Returns:
            匹配的配置项
        """
        results = {}
        query_lower = query.lower()
        
        for key, config_item in self.config_items.items():
            if (query_lower in key.lower() or 
                query_lower in str(config_item.value).lower() or
                query_lower in config_item.description.lower()):
                results[key] = config_item
        
        return results
    
    async def get_config_history(self, key: Optional[str] = None, limit: int = 100) -> List[ConfigChangeEvent]:
        """
        获取配置变更历史
        
        Args:
            key: 配置键（可选）
            limit: 限制数量
            
        Returns:
            变更历史
        """
        if key:
            # 过滤特定键的历史
            filtered_history = [event for event in self.config_history if event.key == key]
            return filtered_history[-limit:]
        else:
            return self.config_history[-limit:]
    
    async def export_configs(self, format: ConfigFormat = ConfigFormat.JSON) -> str:
        """
        导出配置
        
        Args:
            format: 导出格式
            
        Returns:
            配置内容
        """
        configs = {key: item.value for key, item in self.config_items.items()}
        
        if format == ConfigFormat.JSON:
            return json.dumps(configs, indent=2, ensure_ascii=False)
        elif format == ConfigFormat.YAML:
            return yaml.dump(configs, default_flow_style=False, allow_unicode=True)
        elif format == ConfigFormat.TOML:
            return toml.dumps(configs)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    async def import_configs(
        self,
        content: str,
        format: ConfigFormat,
        source: ConfigSource = ConfigSource.REDIS,
        priority: ConfigPriority = ConfigPriority.MEDIUM,
        user_id: Optional[str] = None
    ) -> bool:
        """
        导入配置
        
        Args:
            content: 配置内容
            format: 配置格式
            source: 配置源
            priority: 优先级
            user_id: 用户ID
            
        Returns:
            是否成功
        """
        try:
            # 解析配置内容
            if format == ConfigFormat.JSON:
                configs = json.loads(content)
            elif format == ConfigFormat.YAML:
                configs = yaml.safe_load(content)
            elif format == ConfigFormat.TOML:
                configs = toml.loads(content)
            else:
                raise ValueError(f"Unsupported import format: {format}")
            
            # 导入配置项
            for key, value in configs.items():
                await self.set_config(key, value, source, priority, user_id, "批量导入")
            
            return True
            
        except Exception as e:
            logger.error(f"Error importing configs: {e}")
            return False
    
    async def validate_all_configs(self) -> Dict[str, List[str]]:
        """
        验证所有配置
        
        Returns:
            验证错误信息
        """
        validation_errors = {}
        
        for key, config_item in self.config_items.items():
            errors = []
            
            # 类型验证
            if not ConfigValidator.validate_type(config_item.value, config_item.data_type):
                errors.append(f"Type validation failed: expected {config_item.data_type}")
            
            # 其他验证规则
            validation_rules = config_item.validation_rules
            
            if 'min' in validation_rules or 'max' in validation_rules:
                if not ConfigValidator.validate_range(
                    config_item.value,
                    validation_rules.get('min'),
                    validation_rules.get('max')
                ):
                    errors.append("Range validation failed")
            
            if errors:
                validation_errors[key] = errors
        
        return validation_errors
    
    def add_change_callback(self, callback: Callable[[ConfigChangeEvent], None]):
        """
        添加配置变更回调
        
        Args:
            callback: 回调函数
        """
        self.change_callbacks.append(callback)
    
    def remove_change_callback(self, callback: Callable[[ConfigChangeEvent], None]):
        """
        移除配置变更回调
        
        Args:
            callback: 回调函数
        """
        if callback in self.change_callbacks:
            self.change_callbacks.remove(callback)
    
    async def _config_sync_loop(self):
        """配置同步循环"""
        while True:
            try:
                # 定期从Redis同步配置
                if self.redis_client:
                    await self._load_redis_source()
                
                await asyncio.sleep(60)  # 每分钟同步一次
                
            except Exception as e:
                logger.error(f"Error in config sync loop: {e}")
                await asyncio.sleep(60)
    
    async def _cache_cleanup_loop(self):
        """缓存清理循环"""
        while True:
            try:
                now = datetime.now()
                expired_keys = []
                
                for key, timestamp in self.cache_timestamps.items():
                    if (now - timestamp).total_seconds() > self.cache_ttl:
                        expired_keys.append(key)
                
                for key in expired_keys:
                    if key in self.config_cache:
                        del self.config_cache[key]
                    if key in self.cache_timestamps:
                        del self.cache_timestamps[key]
                
                if expired_keys:
                    logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
                
                await asyncio.sleep(300)  # 每5分钟清理一次
                
            except Exception as e:
                logger.error(f"Error in cache cleanup loop: {e}")
                await asyncio.sleep(300)
    
    async def _health_check_loop(self):
        """健康检查循环"""
        while True:
            try:
                # 检查Redis连接
                if self.redis_client:
                    await self.redis_client.ping()
                
                # 检查文件监控器
                if self.file_observer and not self.file_observer.is_alive():
                    logger.warning("File observer is not running, restarting...")
                    await self._start_file_watcher()
                
                await asyncio.sleep(30)  # 每30秒检查一次
                
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(30)
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            统计信息
        """
        return {
            "total_configs": self.stats["total_configs"],
            "configs_by_source": self.stats["configs_by_source"],
            "configs_by_priority": self.stats["configs_by_priority"],
            "reload_count": self.stats["reload_count"],
            "validation_errors": self.stats["validation_errors"],
            "cache_hits": self.stats["cache_hits"],
            "cache_misses": self.stats["cache_misses"],
            "cache_hit_rate": (
                self.stats["cache_hits"] / (self.stats["cache_hits"] + self.stats["cache_misses"])
                if (self.stats["cache_hits"] + self.stats["cache_misses"]) > 0 else 0
            ),
            "watched_files": len(self.watched_files),
            "change_callbacks": len(self.change_callbacks),
            "config_history_size": len(self.config_history),
            "timestamp": datetime.now().isoformat()
        }
    
    async def close(self):
        """关闭配置管理器"""
        logger.info("Closing config manager")
        
        # 停止文件监控器
        if self.file_observer:
            self.file_observer.stop()
            self.file_observer.join()
        
        # 关闭Redis连接
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("Config manager closed") 
# 数据库连接池优化配置
DATABASE_POOL_CONFIG = {
    "pool_size": 20,           # 连接池大小
    "max_overflow": 30,        # 最大溢出连接数
    "pool_timeout": 30,        # 获取连接超时时间
    "pool_recycle": 3600,      # 连接回收时间
    "pool_pre_ping": True,     # 连接预检查
}
