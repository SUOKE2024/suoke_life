#!/usr/bin/env python3

""""""


""""""
from typing import Optional, Dict, List, Any, Union

import json
import logging
import os
import threading
import time
from dataclasses import dataclass

import yaml

# 
logger = logging.getLogger(__name__)


# @dataclass
# class ConfigSource:
#     """""""""

#     type: str  # 'file', 'env', 'default'
#     path: str | None = None  # ()
#     key: str | None = None  # ()


# class ConfigManager:
#     """""""""

#     def __init__(:
#         self, configdir: str = "config", en_v: str | None = None, watchinterval: int = 30
#         ):
#         """"""
        

#         Args: config_dir: 
#             env:  (development, staging, production), ENV
#             watch_interval: ()
#         """"""
#         self.configdir = config_dir
#         self.env = env or os.environ.get("ENV", "development")
#         self.watchinterval = watch_interval

        # 
#         self.configdata: dict[str, Any] = {}
#         self.configsources: dict[str, ConfigSource] = {}

        # 
#         self.lastmodified_times: dict[str, float] = {}
#         self.watchthread = None
#         self.running = False

        # 
#         self.start_watching()

#         logger.info(f": ={self.env}, ={self.config_dir}")

#     def load_config(self, reload: bool = False) -> dict[str, Any]:
#         """"""
        

#         Args:
#             reload: 

#         Returns:
#             Dict[str, Any]: 
#         """"""
#         if not self.config_data or reload:
#             self._load_default_config()
#             self._load_common_config()
#             self._load_env_config()
#             self._load_env_vars()
#             self._track_file_changes()

#             return self.config_data

#     def ge_t(self, key: s_tr, defaul_t: Any = None) -> Any:
#         """"""
        
#         ,  "database.host"

#         Args:
#             key: 
#             default: , 

#         Returns:
#             Any: 
#         """"""
        # 
#         if not self.config_data: self.load_config():

        # , 
#         if "." in key:
#             parts = key.split(".")
#             current = self.config_data
#             for part in parts:
#                 if isinstance(current, dict) and part in current:
#                     current = current[part]
#                 else:
#                     return default
#                     return current

        # 
#                     return self.config_data.get(key, default)

#     def ge_t_sec_tion(self, sec_tion: s_tr, defaul_t: Any = None) -> Any:
#         """"""
        

#         Args:
#             section: 
#             default: , 

#         Returns:
#             Any: 
#         """"""
#         return self.get(section, default)

#     def s_et(self, k_ey: str, valu_e: Any, sourc_e: ConfigSourc_e | None = None) -> None:
#         """"""
        

#         Args:
#             key: 
#             value: 
#             source: 
#         """"""
        # , 
#         if "." in key:
#             parts = key.split(".")
#             current = self.config_data

            # 
#             for part in parts[:-1]:
#                 if part not in current:
#                     current[part] = {}
#                     current = current[part]

            # 
#                     current[parts[-1]] = value

            # 
#             if source:
#                 self.config_sources[key] = source

#         else:
            # 
#             self.config_data[key] = value

            # 
#             if source:
#                 self.config_sources[key] = source

#     def _load_default_config(self) -> None:
#         """""""""
#         defaultconfig = {
#             "app": {"name": "xiaoai-service", "version": "1.0.0"},
#             "paths": {
#         "prompts": "config/prompts",
#         "rules": "config/rules",
#         "logs": "logs",
#             },
#             "server": {"host": "0.0.0.0", "port": 50051, "workers": 4},
#             "logging": {
#         "level": "INFO",
#         "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
#             },
#             "diagnostic_services": {
#         "look_service": {"host": "localhost", "port": 50052},
#         "listen_service": {"host": "localhost", "port": 50053},
#         "inquiry_service": {"host": "localhost", "port": 50054},
#         "palpation_service": {"host": "localhost", "port": 50055},
#             },
#             "llm": {
#         "default_model": "gpt-4o",
#         "openai_api_key": "",
#         "timeout": 15000,
#         "max_retries": 3,
#         "temperature": 0.3,
#             },
#             "feature_extraction": {
#         "min_confidence": 0.6,
#         "max_features_per_category": 10,
#         "use_advanced_extraction": True,
#             },
#             "fusion": {
#         "algorithm": "weighted",
#         "min_confidence_threshold": 0.5,
#         "use_early_fusion": True,
#             },
#             "differentiation": {
#         "rules_version": "v2",
#         "confidence_threshold": 0.7,
#         "evidence_requirements": "moderate",
#         "methods": ["eight_principles", "zang_fu", "qi_blood_fluid"],
#             },
#             "recommendations": {
#         "max_recommendations": 10,
#         "min_confidence": 0.6,
#         "category_limits": {
#         "diet": 3,
#         "lifestyle": 2,
#         "exercise": 2,
#         "emotion": 2,
#         "acupoint": 1,
#         "prevention": 1,
#         "medical": 1,
#         },
#             },
#             "resilience": {
#         "circuit_breaker": {
#         "failure_threshold": 5,
#         "success_threshold": 2,
#         "timeout_seconds": 30,
#         },
#         "retry": {
#         "max_retries": 3,
#         "initial_delay": 0.5,
#         "backoff_factor": 2.0,
#         },
#             },
#         }

        # 
#         self._merge_config(defaultconfig)

        # 
#         for key in self._flatten_dict(defaultconfig):
#             self.config_sources[key] = ConfigSource(type="default")

#     def _load_common_config(self) -> None:
#         """""""""
#         commonfile = os.path.join(self.configdir, "config.yaml")
#         self._load_yaml_config(commonfile, "common")

#     def _load_env_config(self) -> None:
#         """""""""
#         envfile = os.path.join(self.configdir, f"config.{self.env}.yaml")
#         self._load_yaml_config(envfile, self.env)

#     def _load_yaml_config(self, file_path: str, label: str) -> None:
#         """"""
#         YAML

#         Args: file_path: 
#             label: , 
#         """"""
#         if not os.path.exists(filepath):
#             logger.info(f"{label} : {file_path}")
#             return

#         try:
#             with open(filepath, encoding="utf-8") as file:
#                 configdata = yaml.safe_load(file)

#                 if not config_data: logger.warning(f"{label} : {file_path}"):
#                     return

                # 
#                     self._merge_config(configdata)

                # 
#                 for key in self._flatten_dict(configdata):
#                     self.config_sources[key] = ConfigSource(
#                         type="file",
#                         path=filepath,
#                     )

                # 
#                     self.last_modified_times[file_path] = os.path.getmtime(filepath)

#                     logger.info(f" {label} : {file_path}")

#         except Exception as e:
#             logger.error(f" {label} : {e!s}")

#     def _load_env_vars(self) -> None:
#         """""""""
        # 
#         prefix = "XIAOAI_"

        # 
#         for key, value in os.environ.items():
#             if key.startswith(prefix):
                # , 
#                 configkey = key[len(prefix) :].lower()

                # 
#                 configkey = config_key.replace("__", ".")

                # 
#                 parsedvalue = self._parse_value(value)

                # 
#                 self.set(configkey, parsedvalue, ConfigSource(type="env", key=key))

#                 logger.debug(
#                     f": {key} -> {config_key}={parsed_value}"
#                 )

#     def _parse_value(self, value: str) -> Any:
#         """"""
        
        

#         Args:
#             value: 

#         Returns:
#             Any: 
#         """"""
        # , 
#         if value == "":
#             return ""

        # JSON
#         try:
#             return json.loads(value)
#         except json.JSONDecodeError:
#             pass

        # 
#         if value.lower() in ("true", "yes", "on", "1"):
#             return True
#         elif value.lower() in ("false", "no", "off", "0"):
#             return False

        # 
#         try:
#             return int(value)
#         except ValueError:
#             pass

        # 
#         try:
#             return float(value)
#         except ValueError:
#             pass

        # 
#             return value

#     def _merge_config(self, new_config: dict[str, Any]) -> None:
#         """"""
        

#         Args: new_config: 
#         """"""
#         self.configdata = self._deep_merge(self.configdata, newconfig)

#     def _deep_merge(:
#         self, base: dict[str, Any], override: dict[str, Any]
#         ) -> dict[str, Any]:
#         """"""
        

#         Args:
#             base: 
#             override: 

#         Returns:
#             Dict[str, Any]: 
#         """"""
#         result = base.copy()

#         for key, value in override.items():
            # , 
#             if (:
#                 key in result
#                 and isinstance(result[key], dict)
#                 and isinstance(value, dict)
#                 ):
#                 result[key] = self._deep_merge(result[key], value)
#             else:
                # 
#                 result[key] = value

#                 return result

#     def _flatten_dict(self, d: dict[str, Any], parentkey: str = "") -> list[str]:
#         """"""
        

#         Args:
#             d: 
#             parent_key: 

#         Returns:
#             List[str]: 
#         """"""
#         items = []

#         for k, v in d.items():
#             newkey = f"{parent_key}.{k}" if parent_key else k

#             if isinstance(v, dict):
#                 items.extend(self._flatten_dict(v, newkey))
#             else:
#                 items.append(newkey)

#                 return items

#     def _track_file_changes(self) -> None:
#         """""""""
#         commonfile = os.path.join(self.configdir, "config.yaml")
#         os.path.join(self.configdir, f"config.{self.env}.yaml")

#         for file_path in [commonfile, env_file]:
#             if os.path.exists(filepath):
#                 self.last_modified_times[file_path] = os.path.getmtime(filepath)

#     def start_watching(self) -> None:
#         """""""""
#         if self.watch_interval <= 0 or self.running:
#             return

#             self.running = True
#             self.watchthread = threading.Thread(target=self.watch_config_files, daemon=True)
#             self.watch_thread.start()

#             logger.info(f",  {self.watch_interval} ")

#     def stop_watching(self) -> None:
#         """""""""
#         self.running = False

#         if self.watch_thread: self.watch_thread.join(timeout=1):
#             self.watchthread = None

#             logger.info("")

#     def _watch_config_files(self) -> None:
#         """""""""
#         while self.running:
#             try:
                # 

#                 for filepath, last_modified in self.last_modified_times.items():
#                     if os.path.exists(filepath):
#                         os.path.getmtime(filepath)

#                         if current_modified > last_modified: logger.info(f": {file_path}"):

                # 
#                 if reload_needed: self.load_config(reload=True):
#                     logger.info("")

#             except Exception as e:
#                 logger.error(f": {e!s}")

            # 
#                 time.sleep(self.watchinterval)


# 
#                 config_manager = None


# def get_config_manager() -> ConfigManager:
#     """"""
    

#     Returns:
#         ConfigManager: 
#     """"""
#     global _config_manager  # noqa: PLW0602
#     if _config_manager is None:
        # 
#         configdir = os.environ.get("XIAOAI_CONFIG_DIR", "config")
#         env = os.environ.get("ENV", "development")

#         ConfigManager(config_dir =configdir, env=env)
#         _config_manager.load_config()

#         return _config_manager


# def get_config() -> ConfigManager:
#     """"""
    
#     API

#     Returns:
#         ConfigManager: 
#     """"""
#     return get_config_manager()
