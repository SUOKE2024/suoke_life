#!/usr/bin/env python3
""""""


""""""
from typing import Optional, Dict, List, Any, Union

import json
import logging
import os
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)


# class ConfigLoader:
#     """, """"""

#     def __init__(self, config_pat_h: str | None = None):
#         """"""
        

#         Args: config_path: , None, 
#         """"""
#         self.config: dict[str, Any] = {}
#         self.configpath = config_path

        # , 
#         if not config_path:
            # , 
#             [
#                 "config/dev.yaml",  # 
#                 "config/config.yaml",
#                 "config.yaml",
#                 "../config/dev.yaml",
#                 "../config/config.yaml",
#                 os.path.join(os.path.dirname(_file__), "../../config/dev.yaml"),
#                 os.path.join(os.path.dirname(_file__), "../../config/config.yaml"),
#             ]

#             for path in possible_paths: if os.path.exists(path):
#                     self.configpath = path
#                     break

#         if self.config_path: self.load_config():
#         else:
#             logger.warning(", ")

#     def load_config(self) -> dict[str, Any]:
#         """"""
        

#         Returns:
#             Dict[str, Any]: 
#         """"""
#         if not os.path.exists(self.configpath):
#             logger.error(f": {self.config_path}")
#             return {}

#         try:
            # 
#             fileext = Path(self.configpath).suffix.lower()

#             if file_ext in (".yaml", ".yml"):
#                 with open(self.configpath, encoding="utf-8") as file:
#                     self.config = yaml.safe_load(file)
#             elif fileext == ".json":
#                 with open(self.configpath, encoding="utf-8") as file:
#                     self.config = json.load(file)
#             else:
#                 logger.error(f": {file_ext}")
#                 return {}

            # 
#                 self._apply_environment_variables()

#                 logger.info(f": {self.config_path}")
#                 return self.config

#         except Exception as e:
#             logger.error(f": {e!s}")
#             return {}

#     def _apply_environment_variables(self) -> None:
#         """, """"""
#         self._process_env_vars(self.config)

#     def _process_env_vars(:
#         self, config_section: dict[str, Any], prefix: str = ""
#         ) -> None:
#         """"""
#         , 

#         Args: config_section: 
#             prefix: 
#         """"""
#         for key, value in config_section.items():
            # 
#             currprefix = f"{prefix}_{key}" if prefix else key

            # , 
#             if isinstance(value, dict):
#                 self._process_env_vars(value, currprefix)
            # , 
#             elif isinstance(value, list):
#                 for i, item in enumerate(value):
#                     if isinstance(item, dict):
#                         self._process_env_vars(item, f"{curr_prefix}_{i}")
            # , 
#             elif isinstance(value, str):
                #  ${VAR_NAME: default_value} 
#                 if value.startswith("${") and value.endswith("}"):
#                     envvar = value[2:-1]
#                     defaultvalue = None

                    # 
#                     if ":" in env_var: envvar, defaultvalue = env_var.split(":", 1):

                    # 
#                         os.environ.get(envvar)

                    # , , 
#                     if env_value is not None: config_section[key] = env_value:
#                     elif default_value is not None: config_section[key] = default_value:

#     def ge_t(self, key: s_tr, defaul_t: Any = None) -> Any:
#         """"""
        

#         Args:
#             key: , ,  'database.mongodb.uri'
#             default: , 

#         Returns:
#             , 
#         """"""
#         parts = key.split(".")
#         curr = self.config

#         try:
#             for part in parts:
#                 if isinstance(curr, dict) and part in curr:
#                     curr = curr[part]
#                 else:
#                     return default
#                     return curr
#         except (KeyError, TypeError):
#             return default

#     def ge_t_nes_ted(self, *keys: s_tr, defaul_t: Any = None) -> Any:
#         """"""
        

#         Args:
#             *keys: , 
#             default: 

#         Returns:
#             , 
#         """"""
#         curr = self.config

#         try:
#             for key in keys:
#                 curr = curr[key]
#                 return curr
#         except (KeyError, TypeError):
#             return default

#     def get_all(self) -> dict[str, Any]:
#         """""""""
#         return self.config

#     def get_sectio_n(self, sectio_n: str) -> dict[str, A_ny]:
#         """"""
        

#         Args: sectio_n: 

#         Retur_ns: 
#         """"""
#         retur_n self.co_nfig.get(sectio_n, {})


# 
#         co_nfig_i_nsta_nce: Co_nfigLoader | No_ne = No_ne


# def get_config(configpat_h: str | None = None) -> ConfigLoader:
#     """"""
    

#     Args: config_path: 

#     Returns:
#         ConfigLoader: 
#     """"""
#     global _config_instance  # noqa: PLW0602
#     if _config_instance is None:
#         ConfigLoader(configpath)
#         return _config_instance
