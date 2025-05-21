#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置加载器
用于从YAML文件加载配置信息
"""

import os
from pathlib import Path
from typing import Dict, Optional, Union

import yaml
import structlog

logger = structlog.get_logger()


class ConfigLoader:
    """配置加载器类"""
    
    def __init__(self, config_path: str):
        """
        初始化配置加载器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = Path(config_path)
    
    def load(self) -> Dict:
        """
        加载配置
        
        Returns:
            配置字典
        
        Raises:
            FileNotFoundError: 配置文件不存在
            ValueError: 配置文件解析失败
        """
        if not self.config_path.exists():
            logger.error("Config file not found", path=str(self.config_path))
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                
            # 处理环境变量替换
            self._process_env_vars(config)
            
            return config
        except Exception as e:
            logger.error("Failed to load config", error=str(e), path=str(self.config_path))
            raise ValueError(f"Failed to load config: {e}")
    
    def _process_env_vars(self, config: Union[Dict, list, str]) -> None:
        """
        递归处理配置中的环境变量引用
        
        Args:
            config: 配置字典或列表或字符串
        """
        if isinstance(config, dict):
            for key, value in config.items():
                config[key] = self._process_env_vars_value(value)
        elif isinstance(config, list):
            for i, value in enumerate(config):
                config[i] = self._process_env_vars_value(value)
        
        return config
    
    def _process_env_vars_value(self, value: any) -> any:
        """
        处理单个配置值中的环境变量引用
        
        Args:
            value: 配置值
            
        Returns:
            处理后的配置值
        """
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            # 提取环境变量名称和默认值
            env_var = value[2:-1]
            if ":" in env_var:
                env_name, default = env_var.split(":", 1)
            else:
                env_name, default = env_var, None
            
            # 获取环境变量值
            env_value = os.environ.get(env_name, default)
            if env_value is None:
                logger.warning(f"Environment variable {env_name} not found and no default value provided")
            return env_value
        elif isinstance(value, dict):
            return self._process_env_vars(value)
        elif isinstance(value, list):
            return self._process_env_vars(value)
        else:
            return value 