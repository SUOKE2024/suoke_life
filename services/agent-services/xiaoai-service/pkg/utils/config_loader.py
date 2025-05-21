#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置加载器工具
用于加载服务的配置信息
"""

import os
import yaml
import json
import logging
from typing import Any, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class ConfigLoader:
    """配置加载器类，负责加载和提供配置信息"""
    
    def __init__(self, config_path: str = None):
        """
        初始化配置加载器
        
        Args:
            config_path: 配置文件路径，如果为None，则尝试从默认位置加载
        """
        self.config: Dict[str, Any] = {}
        self.config_path = config_path
        
        # 如果未指定配置路径，尝试从默认位置加载
        if not config_path:
            # 尝试常见的配置文件位置
            possible_paths = [
                "config/config.yaml",
                "config.yaml",
                "../config/config.yaml",
                os.path.join(os.path.dirname(__file__), "../../config/config.yaml")
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    self.config_path = path
                    break
        
        if self.config_path:
            self.load_config()
        else:
            logger.warning("未找到配置文件，将使用默认配置或环境变量")
    
    def load_config(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            Dict[str, Any]: 已加载的配置字典
        """
        if not os.path.exists(self.config_path):
            logger.error(f"配置文件不存在: {self.config_path}")
            return {}
        
        try:
            # 根据文件扩展名决定如何解析
            file_ext = Path(self.config_path).suffix.lower()
            
            if file_ext in ('.yaml', '.yml'):
                with open(self.config_path, 'r', encoding='utf-8') as file:
                    self.config = yaml.safe_load(file)
            elif file_ext == '.json':
                with open(self.config_path, 'r', encoding='utf-8') as file:
                    self.config = json.load(file)
            else:
                logger.error(f"不支持的配置文件格式: {file_ext}")
                return {}
            
            # 应用环境变量覆盖
            self._apply_environment_variables()
            
            logger.info(f"成功加载配置文件: {self.config_path}")
            return self.config
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            return {}
    
    def _apply_environment_variables(self) -> None:
        """应用环境变量，允许通过环境变量覆盖配置"""
        self._process_env_vars(self.config)
    
    def _process_env_vars(self, config_section: Dict[str, Any], prefix: str = '') -> None:
        """
        递归处理配置部分，替换环境变量引用
        
        Args:
            config_section: 配置部分
            prefix: 环境变量前缀
        """
        for key, value in config_section.items():
            # 组合当前键的完整路径
            curr_prefix = f"{prefix}_{key}" if prefix else key
            
            # 如果值是字典，递归处理
            if isinstance(value, dict):
                self._process_env_vars(value, curr_prefix)
            # 如果值是列表，遍历处理
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        self._process_env_vars(item, f"{curr_prefix}_{i}")
            # 如果值是字符串，查找并替换环境变量引用
            elif isinstance(value, str):
                # 查找 ${VAR_NAME:default_value} 格式
                if value.startswith('${') and value.endswith('}'):
                    env_var = value[2:-1]
                    default_value = None
                    
                    # 检查是否有默认值
                    if ':' in env_var:
                        env_var, default_value = env_var.split(':', 1)
                    
                    # 尝试从环境变量获取值
                    env_value = os.environ.get(env_var)
                    
                    # 如果环境变量存在，使用它，否则使用默认值
                    if env_value is not None:
                        config_section[key] = env_value
                    elif default_value is not None:
                        config_section[key] = default_value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取指定配置的值
        
        Args:
            key: 配置键，支持点分隔符访问嵌套配置，如 'database.mongodb.uri'
            default: 如果配置不存在，返回的默认值
            
        Returns:
            配置的值，或默认值
        """
        parts = key.split('.')
        curr = self.config
        
        try:
            for part in parts:
                if isinstance(curr, dict) and part in curr:
                    curr = curr[part]
                else:
                    return default
            return curr
        except (KeyError, TypeError):
            return default
    
    def get_nested(self, *keys: str, default: Any = None) -> Any:
        """
        获取嵌套的配置值
        
        Args:
            *keys: 键序列，用于导航嵌套配置
            default: 默认值
            
        Returns:
            嵌套的配置值，或默认值
        """
        curr = self.config
        
        try:
            for key in keys:
                curr = curr[key]
            return curr
        except (KeyError, TypeError):
            return default
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self.config
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        获取配置的特定部分
        
        Args:
            section: 配置部分名称
            
        Returns:
            指定部分的配置字典
        """
        return self.config.get(section, {})

# 创建单例实例
_config_instance: Optional[ConfigLoader] = None

def get_config(config_path: str = None) -> ConfigLoader:
    """
    获取配置加载器的单例实例
    
    Args:
        config_path: 可选的配置文件路径
        
    Returns:
        ConfigLoader: 配置加载器实例
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigLoader(config_path)
    return _config_instance 