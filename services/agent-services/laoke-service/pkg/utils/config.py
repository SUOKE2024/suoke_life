#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
老克智能体服务 - 配置加载工具
提供从配置文件和环境变量加载配置的功能
"""

import os
import yaml
import logging
import threading
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = "config/config.yaml"
CONFIG_ENV_VAR = "LAOKE_CONFIG_PATH"
ENV_PREFIX = "LAOKE_"

class Config:
    """配置加载器，用于从YAML文件和环境变量加载配置"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls) -> 'Config':
        """单例模式实现"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Config, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        """初始化配置加载器"""
        # 单例模式下，避免重复初始化
        if self._initialized:
            return
        
        # 配置数据
        self.config_data = {}
        
        # 加载配置
        self._load_config()
        
        # 标记为已初始化
        self._initialized = True
        logger.info("配置加载器初始化完成")
    
    def _load_config(self):
        """从配置文件和环境变量加载配置"""
        # 1. 加载基础配置文件
        base_config = self._load_yaml_config(DEFAULT_CONFIG_PATH)
        self.config_data.update(base_config)
        
        # 2. 加载环境特定的配置文件
        env = os.environ.get(f"{ENV_PREFIX}ENV", "development").lower()
        env_config_path = f"config/config.{env}.yaml"
        env_config = self._load_yaml_config(env_config_path)
        self.config_data.update(env_config)
        
        # 3. 加载自定义配置文件（如果指定）
        custom_config_path = os.environ.get(CONFIG_ENV_VAR, None)
        if custom_config_path:
            custom_config = self._load_yaml_config(custom_config_path)
            self.config_data.update(custom_config)
        
        # 4. 从环境变量覆盖配置
        self._load_from_env()
        
        # 设置关键配置
        if "service" not in self.config_data:
            self.config_data["service"] = {}
        
        # 确保服务名称和环境设置正确
        self.config_data["service"]["name"] = self.config_data["service"].get("name", "laoke-service")
        self.config_data["service"]["env"] = env
        
        logger.info(f"已加载配置：服务={self.config_data['service']['name']}，环境={env}")
    
    def _load_yaml_config(self, config_path: str) -> Dict[str, Any]:
        """
        从YAML文件加载配置
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            Dict[str, Any]: 配置数据字典
        """
        config = {}
        try:
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as file:
                    config = yaml.safe_load(file) or {}
                logger.info(f"已加载配置文件: {config_path}")
            else:
                logger.warning(f"配置文件不存在: {config_path}")
        except Exception as e:
            logger.error(f"加载配置文件失败: {config_path}, 错误: {str(e)}")
        
        return config
    
    def _load_from_env(self):
        """从环境变量加载配置，覆盖文件配置"""
        for key, value in os.environ.items():
            # 只处理前缀为 LAOKE_ 的环境变量
            if key.startswith(ENV_PREFIX):
                config_key = key[len(ENV_PREFIX):].lower()
                
                # 将环境变量名格式转换为配置路径 (例如：LAOKE_DATABASE_HOST => database.host)
                config_path = config_key.replace("__", ".").replace("_", ".")
                
                # 设置配置值，处理基本的类型转换
                self._set_nested_value(config_path, self._convert_env_value(value))
    
    def _convert_env_value(self, value: str) -> Any:
        """
        转换环境变量值为适当的类型
        
        Args:
            value: 环境变量字符串值
            
        Returns:
            Any: 转换后的值
        """
        # 布尔值
        if value.lower() in ["true", "yes", "1", "on"]:
            return True
        elif value.lower() in ["false", "no", "0", "off"]:
            return False
        
        # 数字
        try:
            if "." in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # 列表 (逗号分隔)
        if "," in value:
            return [item.strip() for item in value.split(",")]
        
        # 默认为字符串
        return value
    
    def _set_nested_value(self, path: str, value: Any):
        """
        根据路径设置嵌套字典的值
        
        Args:
            path: 配置路径 (例如 "database.host")
            value: 要设置的值
        """
        parts = path.split(".")
        current = self.config_data
        
        # 遍历路径创建嵌套字典
        for i, part in enumerate(parts[:-1]):
            if part not in current:
                current[part] = {}
            elif not isinstance(current[part], dict):
                # 如果当前节点不是字典，则将其转换为字典
                current[part] = {}
            current = current[part]
        
        # 设置最终值
        current[parts[-1]] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键路径 (例如 "database.host")
            default: 默认值
            
        Returns:
            Any: 配置值，如果不存在则返回默认值
        """
        parts = key.split(".")
        current = self.config_data
        
        # 遍历路径查找配置
        for part in parts:
            if not isinstance(current, dict) or part not in current:
                return default
            current = current[part]
        
        return current
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        获取配置区域
        
        Args:
            section: 配置区域名称
            
        Returns:
            Dict[str, Any]: 配置区域字典
        """
        section_data = self.get(section, {})
        if not isinstance(section_data, dict):
            return {}
        return section_data
    
    def get_all(self) -> Dict[str, Any]:
        """
        获取所有配置
        
        Returns:
            Dict[str, Any]: 所有配置的字典
        """
        return self.config_data
    
    def get_list(self, key: str, default: Optional[List] = None) -> List:
        """
        获取列表类型的配置
        
        Args:
            key: 配置键路径
            default: 默认列表
            
        Returns:
            List: 配置列表
        """
        value = self.get(key, default)
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]
    
    def reload(self):
        """重新加载配置"""
        # 清空当前配置
        self.config_data = {}
        
        # 重新加载
        self._load_config()
        
        logger.info("配置已重新加载") 