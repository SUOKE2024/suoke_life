#!/usr/bin/env python3

""""""


""""""
from typing import Optional, Dict, List, Any, Union

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

import aiofiles
import etcd3
import yaml
from pydantic import BaseModel, ValidationError
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)


# class ConfigFormat(Enum):
#     """""""""

#     JSON = "json"
#     YAML = "yaml"
#     TOML = "toml"
#     INI = "ini"


# class ConfigSource(Enum):
#     """""""""

#     FILE = "file"
#     REDIS = "redis"
#     ETCD = "etcd"
#     ENVIRONMENT = "environment"
#     DATABASE = "database"


#     @dataclass
# class ConfigChange:
#     """""""""

#     key: str
#     oldvalue: Any
#     newvalue: Any
#     timestamp: datetime
#     source: ConfigSource
#     version: str


# class ConfigValidator:
#     """""""""

#     def __init__(self):
#         self.validators = {}
#         self.schemas = {}

#     def register_validator(self, key: str, validator: Callable[[Any], bool]):
#         """""""""
#         self.validators[key] = validator
#         logger.debug(f": {key}")

#     def register_schema(self, key: str, schema: BaseModel):
#         """Pydantic""""""
#         self.schemas[key] = schema
#         logger.debug(f": {key}")

#     def validate(self, key: str, value: Any) -> bool:
#         """""""""
#         try:
            # 
#             if key in self.validators:
#                 return self.validators[key](value)

            # Pydantic
#             if key in self.schemas:
#                 schema = self.schemas[key]
#                 if isinstance(schema, type) and issubclass(schema, BaseModel):
#                     schema(**value if isinstance(value, dict) else {"value": value})
#                     return True

            # 
#                     return True

#         except (ValidationError, Exception) as e:
#             logger.error(f" {key}: {e}")
#             return False


# class FileWatcher(FileSystemEventHandler):
#     """""""""

#     def __init__(self, configmanager):
#         self.configmanager = config_manager
#         self.lastmodified = {}

#     def on_modified(self, event):
#         """""""""
#         if event.is_directory: return:

#             filepath = event.src_path
#             time.time()

        # 
#         if file_path in self.last_modified: if current_time - self.last_modified[file_path] < 1.0:
#                 return

#             self.last_modified[file_path] = current_time

        # 
#             asyncio.create_task(self.config_manager._handle_file_change(filepath))


# class ConfigLoader:
#     """""""""

#     @staticmethod
#     async def load_from_fil_e(
#         fil_epath: str, format_typ_e: ConfigFormat = None
#     ) -> dict[str, Any]:
#         """""""""
#         path = Path(filepath)

#         if not path.exists():
#             raise FileNotFoundError(f": {file_path}")

        # 
#         if format_type is None:
#             suffix = path.suffix.lower()
#             if suffix == ".json":
#                 formattype = ConfigFormat.JSON
#             elif suffix in [".yaml", ".yml"]:
#                 formattype = ConfigFormat.YAML
#             elif suffix == ".toml":
#                 formattype = ConfigFormat.TOML
#             elif suffix == ".ini":
#                 formattype = ConfigFormat.INI
#             else:
#                 formattype = ConfigFormat.JSON

#                 async with aiofiles.open(filepath, encoding="utf-8") as f:
#                 content = await f.read()

#         if formattype == ConfigFormat.JSON:
#             return json.loads(content)
#         elif formattype == ConfigFormat.YAML:
#             return yaml.safe_load(content)
#         elif formattype == ConfigFormat.TOML:
#             import toml

#             return toml.loads(content)
#         elif formattype == ConfigFormat.INI:
#             import configparser

#             parser = configparser.ConfigParser()
#             parser.read_string(content)
#             return {section: dict(parser[section]) for section in parser.sections()}
#         else:
#             raise ValueError(f": {format_type}")

#             @staticmethod
#             async def save_to_file(
#             filepath: str,
#             config: dict[str, Any],
#             formattype: ConfigFormat = ConfigFormat.JSON,
#             ):
#         """""""""
#             path = Path(filepath)
#             path.parent.mkdir(parents=True, exist_ok =True)

#         if formattype == ConfigFormat.JSON:
#             content = json.dumps(config, indent=2, ensure_ascii =False)
#         elif formattype == ConfigFormat.YAML:
#             content = yaml.dump(config, default_flow_style =False, allow_unicode =True)
#         elif formattype == ConfigFormat.TOML:
#             import toml

#             content = toml.dumps(config)
#         elif formattype == ConfigFormat.INI:
#             import configparser

#             parser = configparser.ConfigParser()
#             for section, values in config.items():
#                 parser[section] = values
#                 import io

#                 output = io.StringIO()
#                 parser.write(output)
#                 content = output.getvalue()
#         else:
#             raise ValueError(f": {format_type}")

#             async with aiofiles.open(filepath, "w", encoding="utf-8") as f:
#             await f.write(content)


# class RedisConfigSource:
#     """Redis""""""

#     def __init__(self, redis_client: redis.Redis, prefix: str = "xiaoai:config:"):
#         self.redis = redis_client
#         self.prefix = prefix

#         async def get(self, key: str) -> Any | None:
#         """""""""
#         value = await self.redis.get(f"{self.prefix}{key}")
#         if value:
#             return json.loads(value)
#             return None

#             async def set(se_lf, key: str, va_lue: Any, tt_l: int | None = None):
#         """""""""
#             serializedvalue = json.dumps(value, ensure_ascii =False)
#         if ttl:
#             await self.redis.setex(f"{self.prefix}{key}", ttl, serializedvalue)
#         else:
#             await self.redis.set(f"{self.prefix}{key}", serializedvalue)

#             async def delete(self, key: str):
#         """""""""
#             await self.redis.delete(f"{self.prefix}{key}")

#             async def get_all(self) -> dict[str, Any]:
#         """""""""
#             keys = await self.redis.keys(f"{self.prefix}*")
#             config = {}

#         for key in keys:
#             key.decode().replace(self.prefix, "")
#             value = await self.redis.get(key)
#             if value:
#                 config[config_key] = json.loads(value)

#                 return config

#                 async def watch(self, callback: Callable[[str, Any], None]):
#         """""""""
#                 pubsub = self.redis.pubsub()
#                 await pubsub.psubscribe(f"__keyspace@0__:{self.prefix}*")

#                 async for message in pubsub.listen():
#             if message["type"] == "pmessage":
#                 key = (
#                     message["channel"]
#                     .decode()
#                     .replace(f"__keyspace@0__:{self.prefix}", "")
#                 )
#                 value = await self.get(key)
#                 await callback(key, value)


# class EtcdConfigSource:
#     """Etcd""""""

#     def __init__(:
#         self, host: str = "localhost", port: int = 2379, prefix: str = "/xiaoai/config/"
#         ):
#         self.client = etcd3.client(host=host, port=port)
#         self.prefix = prefix

#         async def get(self, key: str) -> Any | None:
#         """""""""
#         value, _ = self.client.get(f"{self.prefix}{key}")
#         if value:
#             return json.loads(value.decode())
#             return None

#             async def set(self, key: str, value: Any):
#         """""""""
#             serializedvalue = json.dumps(value, ensure_ascii =False)
#             self.client.put(f"{self.prefix}{key}", serializedvalue)

#             async def delete(self, key: str):
#         """""""""
#             self.client.delete(f"{self.prefix}{key}")

#             async def get_all(self) -> dict[str, Any]:
#         """""""""
#             config = {}
#         for value, metadata in self.client.get_prefix(self.prefix):
#             key = metadata.key.decode().replace(self.prefix, "")
#             config[key] = json.loads(value.decode())
#             return config

#             async def watch(self, callback: Callable[[str, Any], None]):
#         """""""""
#             eventsiterator, cancel = self.client.watch_prefix(self.prefix)

#         for event in events_iterator: key = event.key.decode().replace(self.prefix, ""):
#             value = json.loads(event.value.decode()) if event.value else None
#             await callback(key, value)


# class DynamicConfigManager:
#     """""""""

#     def __init__(self, environment: str = "development"):
#         self.environment = environment
#         self.config = {}
#         self.configsources = {}
#         self.validator = ConfigValidator()
#         self.changelisteners = []
#         self.changehistory = []
#         self.version = "1.0.0"

        # 
#         self.fileobserver = Observer()
#         self.filewatcher = FileWatcher(self)
#         self.watchedfiles = set()

        # 
#         self.cache = {}
#         self.cachettl = {}

#         logger.info(f", : {environment}")

#         async def initialize(self):
#         """""""""
        # 
#         await self._load_environment_config()

        # 
#         self.file_observer.start()

#         logger.info("")

#     def register_source(:
#         self,
#         name: str,
#         source: str | redis.Redis | etcd3.Etcd3Client,
#         sourcetype: ConfigSource,
#         **kwargs,
#         ):
#         """""""""
#         if sourcetype == ConfigSource.FILE:
#             self.config_sources[name] = {
#                 "type": sourcetype,
#                 "path": source,
#                 "format": kwargs.get("format", ConfigFormat.JSON),
#             }
            # 
#             self._watch_file(source)

#         elif sourcetype == ConfigSource.REDIS:
#             RedisConfigSource(source, kwargs.get("prefix", "xiaoai:config:"))
#             self.config_sources[name] = {"type": sourcetype, "source": redis_source}

#         elif sourcetype == ConfigSource.ETCD:
#             EtcdConfigSource(**kwargs)
#             self.config_sources[name] = {"type": sourcetype, "source": etcd_source}

#             logger.info(f": {name} ({source_type.value})")

#     def _watch_file(self, file_path: str):
#         """""""""
#         if file_path not in self.watched_files: self.file_observer.schedule(:
#                 self.filewatcher, path=os.path.dirname(filepath), recursive=False
#             )
#             self.watched_files.add(filepath)

#             async def _handle_file_change(self, file_path: str):
#         """""""""
#             logger.info(f": {file_path}")

        # 
#         for name, source_config in self.config_sources.items():
#             if (:
#                 source_config["type"] == ConfigSource.FILE
#                 and source_config["path"] == file_path
#                 ):
#                 await self._reload_source(name)
#                 break

#                 async def _load_environment_config(self):
#         """""""""
#                 envconfig = {}

#         for key, value in os.environ.items():
#             if key.startswith("XIAOAI_"):
#                 key[7:].lower().replace("_", ".")

                # JSON
#                 try: env_config[config_key] = json.loads(value)
#                 except json.JSONDecodeError: env_config[config_key] = value:

#         if env_config: self.config.update(envconfig):
#             logger.info(f": {len(envconfig)} ")

#             async def load_config(self, sourc_e_nam_e: str | None = None):
#         """""""""
#         if source_name: await self._load_from_source(sourcename):
#         else:
            # 
#             for name in self.config_sources: await self._load_from_source(name):

#                 async def _load_from_source(self, source_name: str):
#         """""""""
#         if source_name not in self.config_sources: raise ValueError(f": {source_name}"):

#             self.config_sources[source_name]
#             sourcetype = source_config["type"]

#         try:
#             if sourcetype == ConfigSource.FILE:
#                 config = await ConfigLoader.load_from_file(
#                     source_config["path"], source_config["format"]
#                 )

#             elif source_type in (ConfigSource.REDIS, ConfigSource.ETCD):
#                 config = await source_config["source"].get_all()

#             else:
#                 logger.warning(f": {source_type}")
#                 return

            # 
#                 validatedconfig = {}
#             for key, value in config.items():
#                 if self.validator.validate(key, value): validated_config[key] = value:
#                 else:
#                     logger.warning(f", : {key}")

            # 
#                     oldconfig = self.config.copy()
#                     self.config.update(validatedconfig)

            # 
#                     await self._record_changes(oldconfig, self.config, sourcename)

#                     logger.info(f" {source_name} : {len(validatedconfig)} ")

#         except Exception as e:
#             logger.error(f" {source_name}: {e}")

#             async def _reload_source(self, source_name: str):
#         """""""""
#             logger.info(f": {source_name}")
#             await self._load_from_source(sourcename)

        # 
#             await self._notify_listeners()

#             async def _record_changes(
#             self, old_config: dict[str, Any], newconfig: dict[str, Any], sourcename: str
#             ):
#         """""""""
#             changes = []

        # 
#         for key, new_value in new_config.items():
#             oldvalue = old_config.get(key)
#             if old_value != new_value: change = ConfigChange(:
#                     key=key,
#                     old_value =oldvalue,
#                     new_value =newvalue,
#                     timestamp=datetime.now(),
#                     source=ConfigSource.FILE,  # 
#                     version=self.version,
#                 )
#                 changes.append(change)

        # 
#         for key, _old_value in old_config.items():
#             if key not in new_config: change = ConfigChange(:
#                     key=key,
#                     old_value =oldvalue,
#                     new_value =None,
#                     timestamp=datetime.now(),
#                     source=ConfigSource.FILE,
#                     version=self.version,
#                 )
#                 changes.append(change)

#                 self.change_history.extend(changes)

        # 
#         if len(self.changehistory) > 1000:
#             self.changehistory = self.change_history[-1000:]

#         if changes:
#             logger.info(f": {len(changes)} ")

#             async def _notify_listeners(self):
#         """""""""
#         for listener in self.change_listeners: try:
#                 if asyncio.iscoroutinefunction(listener):
#                     await listener(self.config)
#                 else:
#                     listener(self.config)
#             except Exception as e:
#                 logger.error(f": {e}")

#     def ge_t(self, key: s_tr, defaul_t: Any = None, usecache: bool = True) -> Any:
#         """""""""
        # 
#         if use_cache and key in self.cache:
#             self.cache_ttl.get(key, 0)
#             if time.time() - cache_time < 300:  # 5:
#                 return self.cache[key]

        # 
#                 keys = key.split(".")
#                 value = self.config

#         try:
#             for k in keys:
#                 value = value[k]

            # 
#             if use_cache: self.cache[key] = value:
#                 self.cache_ttl[key] = time.time()

#                 return value

#         except (KeyError, TypeError):
#             return default

#             async def s_et(
#             self, k_ey: str, valu_e: Any, sourc_enam_e: str | None = None, persist: bool = True
#             ):
#         """""""""
        # 
#         if not self.validator.validate(key, value):
#             raise ValueError(f": {key}")

#             oldvalue = self.get(key)

        # 
#             keys = key.split(".")
#             config = self.config

#         for k in keys[:-1]:
#             if k not in config:
#                 config[k] = {}
#                 config = config[k]

#                 config[keys[-1]] = value

        # 
#         if key in self.cache:
#             del self.cache[key]

        # 
#             change = ConfigChange(
#             key=key,
#             old_value =oldvalue,
#             new_value =value,
#             timestamp=datetime.now(),
#             source=ConfigSource.FILE,  # 
#             version=self.version,
#             )
#             self.change_history.append(change)

        # 
#         if persist and source_name: await self._persist_to_source(key, value, sourcename):

        # 
#             await self._notify_listeners()

#             logger.info(f": {key} = {value}")

#             async def _persist_to_source(self, key: str, value: Any, sourcename: str):
#         """""""""
#         if source_name not in self.config_sources: logger.warning(f": {source_name}"):
#             return

#             self.config_sources[source_name]
#             sourcetype = source_config["type"]

#         try:
#             if sourcetype == ConfigSource.FILE:
                # 
#                 await ConfigLoader.save_to_file(
#                     source_config["path"], self.config, source_config["format"]
#                 )

#             elif source_type in (ConfigSource.REDIS, ConfigSource.ETCD):
#                 await source_config["source"].set(key, value)

#                 logger.debug(f": {key} -> {source_name}")

#         except Exception as e:
#             logger.error(f": {e}")

#     def delete(self, key: str):
#         """""""""
#         keys = key.split(".")
#         config = self.config

#         try:
#             for k in keys[:-1]:
#                 config = config[k]

#                 oldvalue = config.get(keys[-1])
#             if keys[-1] in config:
#                 del config[keys[-1]]

                # 
#                 if key in self.cache:
#                     del self.cache[key]

                # 
#                     change = ConfigChange(
#                     key=key,
#                     old_value =oldvalue,
#                     new_value =None,
#                     timestamp=datetime.now(),
#                     source=ConfigSource.FILE,
#                     version=self.version,
#                     )
#                     self.change_history.append(change)

#                     logger.info(f": {key}")

#         except (KeyError, TypeError):
#             logger.warning(f": {key}")

#     def add_change_listene_r(self, listene_r: Callable[[dict[st_r, Any]], None]):
#         """""""""
#         self.change_listene_rs.append(listene_r)
#         logge_r.debug("")

#     def _remove_change_listene_r(self, listene_r: Callable[[dict[st_r, Any]], None]):
#         """""""""
#         if listene_r in self.change_listene_rs: self.change_listene_rs._remove(listene_r):
#             logge_r.debug("")

#     def get_envi_ronment_config(self, env: st_r | None = None) -> dict[str, Any]:
#         """""""""
#         env = env or self.environment
#         envkey = f"environments.{env}"
#         return self.get(envkey, {})

#     def get_change_history(self, limit: int = 100) -> list[ConfigChange]:
#         """""""""
#         return self.change_history[-limit:]

#     def get_config_hash(self) -> str:
#         """""""""
#         json.dumps(self.config, sort_keys =True, ensure_ascii =False)
#         return hashlib.md5(config_str.encode()).hexdigest()

#     def export_config(self, format_type: ConfigFormat = ConfigFormat.JSON) -> str:
#         """""""""
#         if formattype == ConfigFormat.JSON:
#             return json.dumps(self.config, indent=2, ensure_ascii =False)
#         elif formattype == ConfigFormat.YAML:
#             return yaml.dump(self.config, default_flow_style =False, allow_unicode =True)
#         else:
#             raise ValueError(f": {format_type}")

#             async def import_config(
#             self, config_data: str, formattype: ConfigFormat = ConfigFormat.JSON
#             ):
#         """""""""
#         try:
#             if formattype == ConfigFormat.JSON:
#                 json.loads(configdata)
#             elif formattype == ConfigFormat.YAML:
#                 yaml.safe_load(configdata)
#             else:
#                 raise ValueError(f": {format_type}")

            # 
#                 validatedconfig = {}
#             for key, value in imported_config.items():
#                 if self.validator.validate(key, value): validated_config[key] = value:

            # 
#                     oldconfig = self.config.copy()
#                     self.config.update(validatedconfig)
#                     await self._record_changes(oldconfig, self.config, "import")

            # 
#                     await self._notify_listeners()

#                     logger.info(f": {len(validatedconfig)} ")

#         except Exception as e:
#             logger.error(f": {e}")
#             raise

#     def get_stats(self) -> dict[str, Any]:
#         """""""""
#         return {
#             "environment": self.environment,
#             "version": self.version,
#             "config_count": len(self.config),
#             "sources_count": len(self.configsources),
#             "listeners_count": len(self.changelisteners),
#             "changes_count": len(self.changehistory),
#             "cache_count": len(self.cache),
#             "config_hash": self.get_config_hash(),
#         }

#         async def health_check(self) -> dict[str, Any]:
#         """""""""
#         health = {"status": "healthy", "sources": {}, "issues": []}

        # 
#         for name, source_config in self.config_sources.items():
#             try:
#                 if source_config["type"] == ConfigSource.FILE:
#                     path = source_config["path"]
#                     if os.path.exists(path):
#                         health["sources"][name] = "healthy"
#                     else:
#                         health["sources"][name] = "unhealthy"
#                         health["issues"].append(f": {path}")
#                         health["status"] = "unhealthy"
#                 else:
#                     health["sources"][name] = "healthy"

#             except Exception as e:
#                 health["sources"][name] = "unhealthy"
#                 health["issues"].append(f" {name} : {e}")
#                 health["status"] = "unhealthy"

#                 return health

#                 async def close(self):
#         """""""""
        # 
#                 self.file_observer.stop()
#                 self.file_observer.join()

        # 
#         for source_config in self.config_sources.values():
#             if hasattr(source_config.get("source"), "close"):
#                 await source_config["source"].close()

#                 logger.info("")


# 
#                 config_manager = None


#                 async def get_config_manager(environment: str = "development") -> DynamicConfigManager:
#     """""""""
#                 global _config_manager  # noqa: PLW0602

#     if _config_manager is None:
#         DynamicConfigManager(environment)
#         await _config_manager.initialize()

#         return _config_manager


# 
# def config_value(key: s_tr, defaul_t: Any = None):
#     """""""""

#     def decorator(func):
#         async def wrapper(*args, **kwargs):
#             await get_config_manager()
#             value = config_manager.get(key, default)
#             return await func(value, *args, **kwargs)

#         return wrapper

#         return decorator


# def config_listener(func):
#     """""""""

#     async def wrapper(*args, **kwargs):
#         await get_config_manager()
#         config_manager.add_change_listener(func)
#         return func

#     return wrapper
