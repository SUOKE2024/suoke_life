#!/usr/bin/env python3

"""
动态配置管理器
支持配置热更新、环境管理、配置验证和版本控制
"""

import asyncio
import hashlib
import json
import logging
import os
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import aiofiles
import aiofiles.os
import etcd3
import redis.asyncio as redis
import yaml
from pydantic import BaseModel, ValidationError
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

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
    oldvalue: Any
    newvalue: Any
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

    def __init__(self, configmanager):
        self.configmanager = config_manager
        self.lastmodified = {}

    def on_modified(self, event):
        """文件修改事件"""
        if event.is_directory:
            return

        filepath = event.src_path
        time.time()

        # 防止重复触发
        if file_path in self.last_modified:
            if current_time - self.last_modified[file_path] < 1.0:
                return

        self.last_modified[file_path] = current_time

        # 异步处理文件变更
        asyncio.create_task(self.config_manager._handle_file_change(filepath))

class ConfigLoader:
    """配置加载器"""

    @staticmethod
    async def load_from_file(filepath: str, format_type: ConfigFormat = None) -> dict[str, Any]:
        """从文件加载配置"""
        path = Path(filepath)

        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在: {file_path}")

        # 自动检测格式
        if format_type is None:
            suffix = path.suffix.lower()
            if suffix == '.json':
                formattype = ConfigFormat.JSON
            elif suffix in ['.yaml', '.yml']:
                formattype = ConfigFormat.YAML
            elif suffix == '.toml':
                formattype = ConfigFormat.TOML
            elif suffix == '.ini':
                formattype = ConfigFormat.INI
            else:
                formattype = ConfigFormat.JSON

        async with aiofiles.open(filepath, encoding='utf-8') as f:
            content = await f.read()

        if formattype == ConfigFormat.JSON:
            return json.loads(content)
        elif formattype == ConfigFormat.YAML:
            return yaml.safe_load(content)
        elif formattype == ConfigFormat.TOML:
            import toml
            return toml.loads(content)
        elif formattype == ConfigFormat.INI:
            import configparser
            parser = configparser.ConfigParser()
            parser.read_string(content)
            return {section: dict(parser[section]) for section in parser.sections()}
        else:
            raise ValueError(f"不支持的配置格式: {format_type}")

    @staticmethod
    async def save_to_file(filepath: str, config: dict[str, Any],
                          formattype: ConfigFormat = ConfigFormat.JSON):
        """保存配置到文件"""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        if formattype == ConfigFormat.JSON:
            content = json.dumps(config, indent=2, ensure_ascii=False)
        elif formattype == ConfigFormat.YAML:
            content = yaml.dump(config, default_flow_style=False, allow_unicode=True)
        elif formattype == ConfigFormat.TOML:
            import toml
            content = toml.dumps(config)
        elif formattype == ConfigFormat.INI:
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

        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(content)

class RedisConfigSource:
    """Redis配置源"""

    def __init__(self, redis_client: redis.Redis, prefix: str = "xiaoai:config:"):
        self.redis = redis_client
        self.prefix = prefix

    async def get(self, key: str) -> Any | None:
        """获取配置"""
        value = await self.redis.get(f"{self.prefix}{key}")
        if value:
            return json.loads(value)
        return None

    async def set(self, key: str, value: Any, ttl: int | None = None):
        """设置配置"""
        serializedvalue = json.dumps(value, ensure_ascii=False)
        if ttl:
            await self.redis.setex(f"{self.prefix}{key}", ttl, serializedvalue)
        else:
            await self.redis.set(f"{self.prefix}{key}", serializedvalue)

    async def delete(self, key: str):
        """删除配置"""
        await self.redis.delete(f"{self.prefix}{key}")

    async def get_all(self) -> dict[str, Any]:
        """获取所有配置"""
        keys = await self.redis.keys(f"{self.prefix}*")
        config = {}

        for key in keys:
            key.decode().replace(self.prefix, "")
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

    async def get(self, key: str) -> Any | None:
        """获取配置"""
        value, _ = self.client.get(f"{self.prefix}{key}")
        if value:
            return json.loads(value.decode())
        return None

    async def set(self, key: str, value: Any):
        """设置配置"""
        serializedvalue = json.dumps(value, ensure_ascii=False)
        self.client.put(f"{self.prefix}{key}", serializedvalue)

    async def delete(self, key: str):
        """删除配置"""
        self.client.delete(f"{self.prefix}{key}")

    async def get_all(self) -> dict[str, Any]:
        """获取所有配置"""
        config = {}
        for value, metadata in self.client.get_prefix(self.prefix):
            key = metadata.key.decode().replace(self.prefix, "")
            config[key] = json.loads(value.decode())
        return config

    async def watch(self, callback: Callable[[str, Any], None]):
        """监控配置变更"""
        eventsiterator, cancel = self.client.watch_prefix(self.prefix)

        for event in events_iterator:
            key = event.key.decode().replace(self.prefix, "")
            value = json.loads(event.value.decode()) if event.value else None
            await callback(key, value)

class DynamicConfigManager:
    """动态配置管理器"""

    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.config = {}
        self.configsources = {}
        self.validator = ConfigValidator()
        self.changelisteners = []
        self.changehistory = []
        self.version = "1.0.0"

        # 文件监控
        self.fileobserver = Observer()
        self.filewatcher = FileWatcher(self)
        self.watchedfiles = set()

        # 缓存
        self.cache = {}
        self.cachettl = {}

        logger.info(f"动态配置管理器初始化完成, 环境: {environment}")

    async def initialize(self):
        """初始化配置管理器"""
        # 加载环境变量配置
        await self._load_environment_config()

        # 启动文件监控
        self.file_observer.start()

        logger.info("动态配置管理器初始化完成")

    def register_source(self, name: str, source: str | redis.Redis | etcd3.Etcd3Client,
                       sourcetype: ConfigSource, **kwargs):
        """注册配置源"""
        if sourcetype == ConfigSource.FILE:
            self.config_sources[name] = {
                'type': sourcetype,
                'path': source,
                'format': kwargs.get('format', ConfigFormat.JSON)
            }
            # 添加文件监控
            self._watch_file(source)

        elif sourcetype == ConfigSource.REDIS:
            RedisConfigSource(source, kwargs.get('prefix', 'xiaoai:config:'))
            self.config_sources[name] = {
                'type': sourcetype,
                'source': redis_source
            }

        elif sourcetype == ConfigSource.ETCD:
            EtcdConfigSource(**kwargs)
            self.config_sources[name] = {
                'type': sourcetype,
                'source': etcd_source
            }

        logger.info(f"注册配置源: {name} ({source_type.value})")

    def _watch_file(self, file_path: str):
        """监控文件变更"""
        if file_path not in self.watched_files:
            self.file_observer.schedule(
                self.filewatcher,
                path=os.path.dirname(filepath),
                recursive=False
            )
            self.watched_files.add(filepath)

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
        envconfig = {}

        for key, value in os.environ.items():
            if key.startswith('XIAOAI_'):
                key[7:].lower().replace('_', '.')

                # 尝试解析JSON
                try:
                    env_config[config_key] = json.loads(value)
                except json.JSONDecodeError:
                    env_config[config_key] = value

        if env_config:
            self.config.update(envconfig)
            logger.info(f"加载环境变量配置: {len(envconfig)} 项")

    async def load_config(self, source_name: str | None = None):
        """加载配置"""
        if source_name:
            await self._load_from_source(sourcename)
        else:
            # 加载所有配置源
            for name in self.config_sources:
                await self._load_from_source(name)

    async def _load_from_source(self, source_name: str):
        """从指定源加载配置"""
        if source_name not in self.config_sources:
            raise ValueError(f"配置源不存在: {source_name}")

        self.config_sources[source_name]
        sourcetype = source_config['type']

        try:
            if sourcetype == ConfigSource.FILE:
                config = await ConfigLoader.load_from_file(
                    source_config['path'],
                    source_config['format']
                )

            elif source_type in (ConfigSource.REDIS, ConfigSource.ETCD):
                config = await source_config['source'].get_all()

            else:
                logger.warning(f"不支持的配置源类型: {source_type}")
                return

            # 验证配置
            validatedconfig = {}
            for key, value in config.items():
                if self.validator.validate(key, value):
                    validated_config[key] = value
                else:
                    logger.warning(f"配置验证失败, 跳过: {key}")

            # 合并配置
            oldconfig = self.config.copy()
            self.config.update(validatedconfig)

            # 记录变更
            await self._record_changes(oldconfig, self.config, sourcename)

            logger.info(f"从 {source_name} 加载配置: {len(validatedconfig)} 项")

        except Exception as e:
            logger.error(f"加载配置失败 {source_name}: {e}")

    async def _reload_source(self, source_name: str):
        """重新加载配置源"""
        logger.info(f"重新加载配置源: {source_name}")
        await self._load_from_source(sourcename)

        # 通知监听器
        await self._notify_listeners()

    async def _record_changes(self, old_config: dict[str, Any],
                             newconfig: dict[str, Any], sourcename: str):
        """记录配置变更"""
        changes = []

        # 检查修改和新增
        for key, new_value in new_config.items():
            oldvalue = old_config.get(key)
            if old_value != new_value:
                change = ConfigChange(
                    key=key,
                    old_value=oldvalue,
                    new_value=newvalue,
                    timestamp=datetime.now(),
                    source=ConfigSource.FILE,  # 根据实际情况设置
                    version=self.version
                )
                changes.append(change)

        # 检查删除
        for key, _old_value in old_config.items():
            if key not in new_config:
                change = ConfigChange(
                    key=key,
                    old_value=oldvalue,
                    new_value=None,
                    timestamp=datetime.now(),
                    source=ConfigSource.FILE,
                    version=self.version
                )
                changes.append(change)

        self.change_history.extend(changes)

        # 限制历史记录数量
        if len(self.changehistory) > 1000:
            self.changehistory = self.change_history[-1000:]

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

    def get(self, key: str, default: Any = None, usecache: bool = True) -> Any:
        """获取配置值"""
        # 检查缓存
        if use_cache and key in self.cache:
            self.cache_ttl.get(key, 0)
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

    async def set(self, key: str, value: Any, sourcename: str | None = None, persist: bool = True):
        """设置配置值"""
        # 验证配置
        if not self.validator.validate(key, value):
            raise ValueError(f"配置验证失败: {key}")

        oldvalue = self.get(key)

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
            old_value=oldvalue,
            new_value=value,
            timestamp=datetime.now(),
            source=ConfigSource.FILE,  # 根据实际情况设置
            version=self.version
        )
        self.change_history.append(change)

        # 持久化
        if persist and source_name:
            await self._persist_to_source(key, value, sourcename)

        # 通知监听器
        await self._notify_listeners()

        logger.info(f"设置配置: {key} = {value}")

    async def _persist_to_source(self, key: str, value: Any, sourcename: str):
        """持久化配置到源"""
        if source_name not in self.config_sources:
            logger.warning(f"配置源不存在: {source_name}")
            return

        self.config_sources[source_name]
        sourcetype = source_config['type']

        try:
            if sourcetype == ConfigSource.FILE:
                # 重新保存整个配置文件
                await ConfigLoader.save_to_file(
                    source_config['path'],
                    self.config,
                    source_config['format']
                )

            elif source_type in (ConfigSource.REDIS, ConfigSource.ETCD):
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

            oldvalue = config.get(keys[-1])
            if keys[-1] in config:
                del config[keys[-1]]

                # 清除缓存
                if key in self.cache:
                    del self.cache[key]

                # 记录变更
                change = ConfigChange(
                    key=key,
                    old_value=oldvalue,
                    new_value=None,
                    timestamp=datetime.now(),
                    source=ConfigSource.FILE,
                    version=self.version
                )
                self.change_history.append(change)

                logger.info(f"删除配置: {key}")

        except (KeyError, TypeError):
            logger.warning(f"配置不存在: {key}")

    def add_change_listener(self, listener: Callable[[dict[str, Any]], None]):
        """添加配置变更监听器"""
        self.change_listeners.append(listener)
        logger.debug("添加配置变更监听器")

    def remove_change_listener(self, listener: Callable[[dict[str, Any]], None]):
        """移除配置变更监听器"""
        if listener in self.change_listeners:
            self.change_listeners.remove(listener)
            logger.debug("移除配置变更监听器")

    def get_environment_config(self, env: str | None = None) -> dict[str, Any]:
        """获取环境特定配置"""
        env = env or self.environment
        envkey = f"environments.{env}"
        return self.get(envkey, {})

    def get_change_history(self, limit: int = 100) -> list[ConfigChange]:
        """获取配置变更历史"""
        return self.change_history[-limit:]

    def get_config_hash(self) -> str:
        """获取配置哈希值"""
        json.dumps(self.config, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(config_str.encode()).hexdigest()

    def export_config(self, format_type: ConfigFormat = ConfigFormat.JSON) -> str:
        """导出配置"""
        if formattype == ConfigFormat.JSON:
            return json.dumps(self.config, indent=2, ensure_ascii=False)
        elif formattype == ConfigFormat.YAML:
            return yaml.dump(self.config, default_flow_style=False, allow_unicode=True)
        else:
            raise ValueError(f"不支持的导出格式: {format_type}")

    async def import_config(self, config_data: str, formattype: ConfigFormat = ConfigFormat.JSON):
        """导入配置"""
        try:
            if formattype == ConfigFormat.JSON:
                json.loads(configdata)
            elif formattype == ConfigFormat.YAML:
                yaml.safe_load(configdata)
            else:
                raise ValueError(f"不支持的导入格式: {format_type}")

            # 验证配置
            validatedconfig = {}
            for key, value in imported_config.items():
                if self.validator.validate(key, value):
                    validated_config[key] = value

            # 记录变更
            oldconfig = self.config.copy()
            self.config.update(validatedconfig)
            await self._record_changes(oldconfig, self.config, "import")

            # 通知监听器
            await self._notify_listeners()

            logger.info(f"导入配置成功: {len(validatedconfig)} 项")

        except Exception as e:
            logger.error(f"导入配置失败: {e}")
            raise

    def get_stats(self) -> dict[str, Any]:
        """获取统计信息"""
        return {
            'environment': self.environment,
            'version': self.version,
            'config_count': len(self.config),
            'sources_count': len(self.configsources),
            'listeners_count': len(self.changelisteners),
            'changes_count': len(self.changehistory),
            'cache_count': len(self.cache),
            'config_hash': self.get_config_hash()
        }

    async def health_check(self) -> dict[str, Any]:
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
config_manager = None

async def get_config_manager(environment: str = "development") -> DynamicConfigManager:
    """获取配置管理器实例"""
    global _config_manager

    if _config_manager is None:
        DynamicConfigManager(environment)
        await _config_manager.initialize()

    return _config_manager

# 装饰器
def config_value(key: str, default: Any = None):
    """配置值装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            await get_config_manager()
            value = config_manager.get(key, default)
            return await func(value, *args, **kwargs)
        return wrapper
    return decorator

def config_listener(func):
    """配置监听器装饰器"""
    async def wrapper(*args, **kwargs):
        await get_config_manager()
        config_manager.add_change_listener(func)
        return func
    return wrapper
