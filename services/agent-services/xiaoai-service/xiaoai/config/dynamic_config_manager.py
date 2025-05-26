#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
动态配置管理器
支持配置热更新、环境管理、配置验证和版本控制
"""

import asyncio
import json
import yaml
import os
import time
import logging
import hashlib
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
from pathlib import Path
import aiofiles
import aiofiles.os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import redis.asyncio as redis
from pydantic import BaseModel, ValidationError
import etcd3

logger = logging.getLogger(__name__)

class ConfigFormat(Enum):
    """配置格式"""
    JSON = "json"
    YAML = "yaml"
    TOML = "toml"
    INI = "ini"

class ConfigSource(Enum):
    """配置源"""
    FILE = "file"
    REDIS = "redis"
    ETCD = "etcd"
    ENVIRONMENT = "environment"
    DATABASE = "database"

@dataclass
class ConfigChange:
    """配置变更"""
    key: str
    old_value: Any
    new_value: Any
    timestamp: datetime
    source: ConfigSource
    version: str

class ConfigValidator:
    """配置验证器"""
    
    def __init__(self):
        self.validators = {}
        self.schemas = {}
    
    def register_validator(self, key: str, validator: Callable[[Any], bool]):
        """注册验证器"""
        self.validators[key] = validator
        logger.debug(f"注册配置验证器: {key}")
    
    def register_schema(self, key: str, schema: BaseModel):
        """注册Pydantic模式"""
        self.schemas[key] = schema
        logger.debug(f"注册配置模式: {key}")
    
    def validate(self, key: str, value: Any) -> bool:
        """验证配置值"""
        try:
            # 使用自定义验证器
            if key in self.validators:
                return self.validators[key](value)
            
            # 使用Pydantic模式
            if key in self.schemas:
                schema = self.schemas[key]
                if isinstance(schema, type) and issubclass(schema, BaseModel):
                    schema(**value if isinstance(value, dict) else {"value": value})
                return True
            
            # 默认通过
            return True
        
        except (ValidationError, Exception) as e:
            logger.error(f"配置验证失败 {key}: {e}")
            return False

class FileWatcher(FileSystemEventHandler):
    """文件监控器"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.last_modified = {}
    
    def on_modified(self, event):
        """文件修改事件"""
        if event.is_directory:
            return
        
        file_path = event.src_path
        current_time = time.time()
        
        # 防止重复触发
        if file_path in self.last_modified:
            if current_time - self.last_modified[file_path] < 1.0:
                return
        
        self.last_modified[file_path] = current_time
        
        # 异步处理文件变更
        asyncio.create_task(self.config_manager._handle_file_change(file_path))

class ConfigLoader:
    """配置加载器"""
    
    @staticmethod
    async def load_from_file(file_path: str, format_type: ConfigFormat = None) -> Dict[str, Any]:
        """从文件加载配置"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在: {file_path}")
        
        # 自动检测格式
        if format_type is None:
            suffix = path.suffix.lower()
            if suffix == '.json':
                format_type = ConfigFormat.JSON
            elif suffix in ['.yaml', '.yml']:
                format_type = ConfigFormat.YAML
            elif suffix == '.toml':
                format_type = ConfigFormat.TOML
            elif suffix == '.ini':
                format_type = ConfigFormat.INI
            else:
                format_type = ConfigFormat.JSON
        
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
        
        if format_type == ConfigFormat.JSON:
            return json.loads(content)
        elif format_type == ConfigFormat.YAML:
            return yaml.safe_load(content)
        elif format_type == ConfigFormat.TOML:
            import toml
            return toml.loads(content)
        elif format_type == ConfigFormat.INI:
            import configparser
            parser = configparser.ConfigParser()
            parser.read_string(content)
            return {section: dict(parser[section]) for section in parser.sections()}
        else:
            raise ValueError(f"不支持的配置格式: {format_type}")
    
    @staticmethod
    async def save_to_file(file_path: str, config: Dict[str, Any], 
                          format_type: ConfigFormat = ConfigFormat.JSON):
        """保存配置到文件"""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if format_type == ConfigFormat.JSON:
            content = json.dumps(config, indent=2, ensure_ascii=False)
        elif format_type == ConfigFormat.YAML:
            content = yaml.dump(config, default_flow_style=False, allow_unicode=True)
        elif format_type == ConfigFormat.TOML:
            import toml
            content = toml.dumps(config)
        elif format_type == ConfigFormat.INI:
            import configparser
            parser = configparser.ConfigParser()
            for section, values in config.items():
                parser[section] = values
            import io
            output = io.StringIO()
            parser.write(output)
            content = output.getvalue()
        else:
            raise ValueError(f"不支持的配置格式: {format_type}")
        
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(content)

class RedisConfigSource:
    """Redis配置源"""
    
    def __init__(self, redis_client: redis.Redis, prefix: str = "xiaoai:config:"):
        self.redis = redis_client
        self.prefix = prefix
    
    async def get(self, key: str) -> Optional[Any]:
        """获取配置"""
        value = await self.redis.get(f"{self.prefix}{key}")
        if value:
            return json.loads(value)
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """设置配置"""
        serialized_value = json.dumps(value, ensure_ascii=False)
        if ttl:
            await self.redis.setex(f"{self.prefix}{key}", ttl, serialized_value)
        else:
            await self.redis.set(f"{self.prefix}{key}", serialized_value)
    
    async def delete(self, key: str):
        """删除配置"""
        await self.redis.delete(f"{self.prefix}{key}")
    
    async def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        keys = await self.redis.keys(f"{self.prefix}*")
        config = {}
        
        for key in keys:
            config_key = key.decode().replace(self.prefix, "")
            value = await self.redis.get(key)
            if value:
                config[config_key] = json.loads(value)
        
        return config
    
    async def watch(self, callback: Callable[[str, Any], None]):
        """监控配置变更"""
        pubsub = self.redis.pubsub()
        await pubsub.psubscribe(f"__keyspace@0__:{self.prefix}*")
        
        async for message in pubsub.listen():
            if message['type'] == 'pmessage':
                key = message['channel'].decode().replace(f"__keyspace@0__:{self.prefix}", "")
                value = await self.get(key)
                await callback(key, value)

class EtcdConfigSource:
    """Etcd配置源"""
    
    def __init__(self, host: str = 'localhost', port: int = 2379, prefix: str = "/xiaoai/config/"):
        self.client = etcd3.client(host=host, port=port)
        self.prefix = prefix
    
    async def get(self, key: str) -> Optional[Any]:
        """获取配置"""
        value, _ = self.client.get(f"{self.prefix}{key}")
        if value:
            return json.loads(value.decode())
        return None
    
    async def set(self, key: str, value: Any):
        """设置配置"""
        serialized_value = json.dumps(value, ensure_ascii=False)
        self.client.put(f"{self.prefix}{key}", serialized_value)
    
    async def delete(self, key: str):
        """删除配置"""
        self.client.delete(f"{self.prefix}{key}")
    
    async def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        config = {}
        for value, metadata in self.client.get_prefix(self.prefix):
            key = metadata.key.decode().replace(self.prefix, "")
            config[key] = json.loads(value.decode())
        return config
    
    async def watch(self, callback: Callable[[str, Any], None]):
        """监控配置变更"""
        events_iterator, cancel = self.client.watch_prefix(self.prefix)
        
        for event in events_iterator:
            key = event.key.decode().replace(self.prefix, "")
            if event.value:
                value = json.loads(event.value.decode())
            else:
                value = None
            await callback(key, value)

class DynamicConfigManager:
    """动态配置管理器"""
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.config = {}
        self.config_sources = {}
        self.validator = ConfigValidator()
        self.change_listeners = []
        self.change_history = []
        self.version = "1.0.0"
        
        # 文件监控
        self.file_observer = Observer()
        self.file_watcher = FileWatcher(self)
        self.watched_files = set()
        
        # 缓存
        self.cache = {}
        self.cache_ttl = {}
        
        logger.info(f"动态配置管理器初始化完成，环境: {environment}")
    
    async def initialize(self):
        """初始化配置管理器"""
        # 加载环境变量配置
        await self._load_environment_config()
        
        # 启动文件监控
        self.file_observer.start()
        
        logger.info("动态配置管理器初始化完成")
    
    def register_source(self, name: str, source: Union[str, redis.Redis, etcd3.Etcd3Client], 
                       source_type: ConfigSource, **kwargs):
        """注册配置源"""
        if source_type == ConfigSource.FILE:
            self.config_sources[name] = {
                'type': source_type,
                'path': source,
                'format': kwargs.get('format', ConfigFormat.JSON)
            }
            # 添加文件监控
            self._watch_file(source)
        
        elif source_type == ConfigSource.REDIS:
            redis_source = RedisConfigSource(source, kwargs.get('prefix', 'xiaoai:config:'))
            self.config_sources[name] = {
                'type': source_type,
                'source': redis_source
            }
        
        elif source_type == ConfigSource.ETCD:
            etcd_source = EtcdConfigSource(**kwargs)
            self.config_sources[name] = {
                'type': source_type,
                'source': etcd_source
            }
        
        logger.info(f"注册配置源: {name} ({source_type.value})")
    
    def _watch_file(self, file_path: str):
        """监控文件变更"""
        if file_path not in self.watched_files:
            self.file_observer.schedule(
                self.file_watcher,
                path=os.path.dirname(file_path),
                recursive=False
            )
            self.watched_files.add(file_path)
    
    async def _handle_file_change(self, file_path: str):
        """处理文件变更"""
        logger.info(f"检测到文件变更: {file_path}")
        
        # 找到对应的配置源
        for name, source_config in self.config_sources.items():
            if source_config['type'] == ConfigSource.FILE and source_config['path'] == file_path:
                await self._reload_source(name)
                break
    
    async def _load_environment_config(self):
        """加载环境变量配置"""
        env_config = {}
        
        for key, value in os.environ.items():
            if key.startswith('XIAOAI_'):
                config_key = key[7:].lower().replace('_', '.')
                
                # 尝试解析JSON
                try:
                    env_config[config_key] = json.loads(value)
                except json.JSONDecodeError:
                    env_config[config_key] = value
        
        if env_config:
            self.config.update(env_config)
            logger.info(f"加载环境变量配置: {len(env_config)} 项")
    
    async def load_config(self, source_name: str = None):
        """加载配置"""
        if source_name:
            await self._load_from_source(source_name)
        else:
            # 加载所有配置源
            for name in self.config_sources:
                await self._load_from_source(name)
    
    async def _load_from_source(self, source_name: str):
        """从指定源加载配置"""
        if source_name not in self.config_sources:
            raise ValueError(f"配置源不存在: {source_name}")
        
        source_config = self.config_sources[source_name]
        source_type = source_config['type']
        
        try:
            if source_type == ConfigSource.FILE:
                config = await ConfigLoader.load_from_file(
                    source_config['path'],
                    source_config['format']
                )
            
            elif source_type == ConfigSource.REDIS:
                config = await source_config['source'].get_all()
            
            elif source_type == ConfigSource.ETCD:
                config = await source_config['source'].get_all()
            
            else:
                logger.warning(f"不支持的配置源类型: {source_type}")
                return
            
            # 验证配置
            validated_config = {}
            for key, value in config.items():
                if self.validator.validate(key, value):
                    validated_config[key] = value
                else:
                    logger.warning(f"配置验证失败，跳过: {key}")
            
            # 合并配置
            old_config = self.config.copy()
            self.config.update(validated_config)
            
            # 记录变更
            await self._record_changes(old_config, self.config, source_name)
            
            logger.info(f"从 {source_name} 加载配置: {len(validated_config)} 项")
        
        except Exception as e:
            logger.error(f"加载配置失败 {source_name}: {e}")
    
    async def _reload_source(self, source_name: str):
        """重新加载配置源"""
        logger.info(f"重新加载配置源: {source_name}")
        await self._load_from_source(source_name)
        
        # 通知监听器
        await self._notify_listeners()
    
    async def _record_changes(self, old_config: Dict[str, Any], 
                             new_config: Dict[str, Any], source_name: str):
        """记录配置变更"""
        changes = []
        
        # 检查修改和新增
        for key, new_value in new_config.items():
            old_value = old_config.get(key)
            if old_value != new_value:
                change = ConfigChange(
                    key=key,
                    old_value=old_value,
                    new_value=new_value,
                    timestamp=datetime.now(),
                    source=ConfigSource.FILE,  # 根据实际情况设置
                    version=self.version
                )
                changes.append(change)
        
        # 检查删除
        for key, old_value in old_config.items():
            if key not in new_config:
                change = ConfigChange(
                    key=key,
                    old_value=old_value,
                    new_value=None,
                    timestamp=datetime.now(),
                    source=ConfigSource.FILE,
                    version=self.version
                )
                changes.append(change)
        
        self.change_history.extend(changes)
        
        # 限制历史记录数量
        if len(self.change_history) > 1000:
            self.change_history = self.change_history[-1000:]
        
        if changes:
            logger.info(f"记录配置变更: {len(changes)} 项")
    
    async def _notify_listeners(self):
        """通知配置变更监听器"""
        for listener in self.change_listeners:
            try:
                if asyncio.iscoroutinefunction(listener):
                    await listener(self.config)
                else:
                    listener(self.config)
            except Exception as e:
                logger.error(f"通知配置监听器失败: {e}")
    
    def get(self, key: str, default: Any = None, use_cache: bool = True) -> Any:
        """获取配置值"""
        # 检查缓存
        if use_cache and key in self.cache:
            cache_time = self.cache_ttl.get(key, 0)
            if time.time() - cache_time < 300:  # 5分钟缓存
                return self.cache[key]
        
        # 支持点号分隔的嵌套键
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            
            # 缓存结果
            if use_cache:
                self.cache[key] = value
                self.cache_ttl[key] = time.time()
            
            return value
        
        except (KeyError, TypeError):
            return default
    
    async def set(self, key: str, value: Any, source_name: str = None, persist: bool = True):
        """设置配置值"""
        # 验证配置
        if not self.validator.validate(key, value):
            raise ValueError(f"配置验证失败: {key}")
        
        old_value = self.get(key)
        
        # 设置到内存配置
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        
        # 清除缓存
        if key in self.cache:
            del self.cache[key]
        
        # 记录变更
        change = ConfigChange(
            key=key,
            old_value=old_value,
            new_value=value,
            timestamp=datetime.now(),
            source=ConfigSource.FILE,  # 根据实际情况设置
            version=self.version
        )
        self.change_history.append(change)
        
        # 持久化
        if persist and source_name:
            await self._persist_to_source(key, value, source_name)
        
        # 通知监听器
        await self._notify_listeners()
        
        logger.info(f"设置配置: {key} = {value}")
    
    async def _persist_to_source(self, key: str, value: Any, source_name: str):
        """持久化配置到源"""
        if source_name not in self.config_sources:
            logger.warning(f"配置源不存在: {source_name}")
            return
        
        source_config = self.config_sources[source_name]
        source_type = source_config['type']
        
        try:
            if source_type == ConfigSource.FILE:
                # 重新保存整个配置文件
                await ConfigLoader.save_to_file(
                    source_config['path'],
                    self.config,
                    source_config['format']
                )
            
            elif source_type == ConfigSource.REDIS:
                await source_config['source'].set(key, value)
            
            elif source_type == ConfigSource.ETCD:
                await source_config['source'].set(key, value)
            
            logger.debug(f"配置持久化成功: {key} -> {source_name}")
        
        except Exception as e:
            logger.error(f"配置持久化失败: {e}")
    
    def delete(self, key: str):
        """删除配置"""
        keys = key.split('.')
        config = self.config
        
        try:
            for k in keys[:-1]:
                config = config[k]
            
            old_value = config.get(keys[-1])
            if keys[-1] in config:
                del config[keys[-1]]
                
                # 清除缓存
                if key in self.cache:
                    del self.cache[key]
                
                # 记录变更
                change = ConfigChange(
                    key=key,
                    old_value=old_value,
                    new_value=None,
                    timestamp=datetime.now(),
                    source=ConfigSource.FILE,
                    version=self.version
                )
                self.change_history.append(change)
                
                logger.info(f"删除配置: {key}")
        
        except (KeyError, TypeError):
            logger.warning(f"配置不存在: {key}")
    
    def add_change_listener(self, listener: Callable[[Dict[str, Any]], None]):
        """添加配置变更监听器"""
        self.change_listeners.append(listener)
        logger.debug("添加配置变更监听器")
    
    def remove_change_listener(self, listener: Callable[[Dict[str, Any]], None]):
        """移除配置变更监听器"""
        if listener in self.change_listeners:
            self.change_listeners.remove(listener)
            logger.debug("移除配置变更监听器")
    
    def get_environment_config(self, env: str = None) -> Dict[str, Any]:
        """获取环境特定配置"""
        env = env or self.environment
        env_key = f"environments.{env}"
        return self.get(env_key, {})
    
    def get_change_history(self, limit: int = 100) -> List[ConfigChange]:
        """获取配置变更历史"""
        return self.change_history[-limit:]
    
    def get_config_hash(self) -> str:
        """获取配置哈希值"""
        config_str = json.dumps(self.config, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(config_str.encode()).hexdigest()
    
    def export_config(self, format_type: ConfigFormat = ConfigFormat.JSON) -> str:
        """导出配置"""
        if format_type == ConfigFormat.JSON:
            return json.dumps(self.config, indent=2, ensure_ascii=False)
        elif format_type == ConfigFormat.YAML:
            return yaml.dump(self.config, default_flow_style=False, allow_unicode=True)
        else:
            raise ValueError(f"不支持的导出格式: {format_type}")
    
    async def import_config(self, config_data: str, format_type: ConfigFormat = ConfigFormat.JSON):
        """导入配置"""
        try:
            if format_type == ConfigFormat.JSON:
                imported_config = json.loads(config_data)
            elif format_type == ConfigFormat.YAML:
                imported_config = yaml.safe_load(config_data)
            else:
                raise ValueError(f"不支持的导入格式: {format_type}")
            
            # 验证配置
            validated_config = {}
            for key, value in imported_config.items():
                if self.validator.validate(key, value):
                    validated_config[key] = value
            
            # 记录变更
            old_config = self.config.copy()
            self.config.update(validated_config)
            await self._record_changes(old_config, self.config, "import")
            
            # 通知监听器
            await self._notify_listeners()
            
            logger.info(f"导入配置成功: {len(validated_config)} 项")
        
        except Exception as e:
            logger.error(f"导入配置失败: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            'environment': self.environment,
            'version': self.version,
            'config_count': len(self.config),
            'sources_count': len(self.config_sources),
            'listeners_count': len(self.change_listeners),
            'changes_count': len(self.change_history),
            'cache_count': len(self.cache),
            'config_hash': self.get_config_hash()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        health = {
            'status': 'healthy',
            'sources': {},
            'issues': []
        }
        
        # 检查配置源
        for name, source_config in self.config_sources.items():
            try:
                if source_config['type'] == ConfigSource.FILE:
                    path = source_config['path']
                    if os.path.exists(path):
                        health['sources'][name] = 'healthy'
                    else:
                        health['sources'][name] = 'unhealthy'
                        health['issues'].append(f"配置文件不存在: {path}")
                        health['status'] = 'unhealthy'
                else:
                    health['sources'][name] = 'healthy'
            
            except Exception as e:
                health['sources'][name] = 'unhealthy'
                health['issues'].append(f"配置源 {name} 检查失败: {e}")
                health['status'] = 'unhealthy'
        
        return health
    
    async def close(self):
        """关闭配置管理器"""
        # 停止文件监控
        self.file_observer.stop()
        self.file_observer.join()
        
        # 关闭配置源连接
        for source_config in self.config_sources.values():
            if hasattr(source_config.get('source'), 'close'):
                await source_config['source'].close()
        
        logger.info("动态配置管理器已关闭")

# 全局配置管理器实例
_config_manager = None

async def get_config_manager(environment: str = "development") -> DynamicConfigManager:
    """获取配置管理器实例"""
    global _config_manager
    
    if _config_manager is None:
        _config_manager = DynamicConfigManager(environment)
        await _config_manager.initialize()
    
    return _config_manager

# 装饰器
def config_value(key: str, default: Any = None):
    """配置值装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            config_manager = await get_config_manager()
            value = config_manager.get(key, default)
            return await func(value, *args, **kwargs)
        return wrapper
    return decorator

def config_listener(func):
    """配置监听器装饰器"""
    async def wrapper(*args, **kwargs):
        config_manager = await get_config_manager()
        config_manager.add_change_listener(func)
        return func
    return wrapper 