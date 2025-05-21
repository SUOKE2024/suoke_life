#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置加载器模块，负责加载配置文件
"""

import logging
import os
from typing import Dict, Any, Optional

import yaml

logger = logging.getLogger(__name__)


class ConfigLoader:
    """配置加载器类，负责加载配置文件"""

    def __init__(self, config_path: str):
        """
        初始化配置加载器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        
    def load(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            Dict[str, Any]: 配置信息
        """
        try:
            if not os.path.exists(self.config_path):
                logger.error(f"配置文件不存在: {self.config_path}")
                return {}
                
            with open(self.config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                
            # 处理环境变量替换
            config = self._process_env_vars(config)
            
            logger.info(f"已加载配置文件: {self.config_path}")
            return config
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            return {}
            
    def _process_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理配置中的环境变量占位符
        
        Args:
            config: 原始配置
            
        Returns:
            Dict[str, Any]: 处理后的配置
        """
        if isinstance(config, dict):
            return {k: self._process_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._process_env_vars(item) for item in config]
        elif isinstance(config, str):
            # 替换 {{ ENV_VAR }} 格式的环境变量
            if config.startswith('{{') and config.endswith('}}'):
                env_var = config.strip('{} ').strip()
                env_value = os.environ.get(env_var)
                if env_value is not None:
                    logger.debug(f"替换环境变量: {env_var}")
                    return env_value
                else:
                    logger.warning(f"环境变量不存在: {env_var}")
            return config
        else:
            return config
            
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点号分隔的路径，如 'server.port'
            default: 默认值
            
        Returns:
            Any: 配置值，如果不存在则返回默认值
        """
        config = self.load()
        keys = key.split('.')
        
        # 逐层查找配置值
        current = config
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
                
        return current
        
    @staticmethod
    def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并配置，override_config会覆盖base_config中的同名配置
        
        Args:
            base_config: 基础配置
            override_config: 覆盖配置
            
        Returns:
            Dict[str, Any]: 合并后的配置
        """
        merged = base_config.copy()
        
        for key, value in override_config.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                # 递归合并嵌套字典
                merged[key] = ConfigLoader.merge_configs(merged[key], value)
            else:
                # 直接覆盖或添加新值
                merged[key] = value
                
        return merged 