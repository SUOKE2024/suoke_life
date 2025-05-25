#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理器

统一管理无障碍服务的所有配置，支持环境变量、配置文件和默认值。
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, field
from .modules.base_module import ModuleConfig

logger = logging.getLogger(__name__)


@dataclass
class ServiceConfig:
    """服务配置"""
    # 服务基础配置
    host: str = "0.0.0.0"
    port: int = 50051
    debug: bool = False
    log_level: str = "INFO"
    
    # 性能配置
    max_workers: int = 10
    request_timeout: int = 30
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    
    # 缓存配置
    cache_enabled: bool = True
    cache_ttl: int = 300
    redis_url: Optional[str] = None
    
    # 数据库配置
    database_url: Optional[str] = None
    
    # 安全配置
    enable_auth: bool = False
    jwt_secret: Optional[str] = None
    
    # 监控配置
    metrics_enabled: bool = True
    metrics_port: int = 8080
    health_check_interval: int = 30


@dataclass
class ModulesConfig:
    """模块配置"""
    blind_assistance: ModuleConfig = field(default_factory=lambda: ModuleConfig(
        enabled=True,
        model_path="microsoft/beit-base-patch16-224-pt22k",
        device="cpu"
    ))
    
    sign_language: ModuleConfig = field(default_factory=lambda: ModuleConfig(
        enabled=True,
        device="cpu"
    ))
    
    voice_assistance: ModuleConfig = field(default_factory=lambda: ModuleConfig(
        enabled=True,
        device="cpu"
    ))
    
    screen_reading: ModuleConfig = field(default_factory=lambda: ModuleConfig(
        enabled=True,
        device="cpu"
    ))
    
    content_conversion: ModuleConfig = field(default_factory=lambda: ModuleConfig(
        enabled=True,
        model_path="google/flan-t5-base",
        device="cpu"
    ))
    
    translation: ModuleConfig = field(default_factory=lambda: ModuleConfig(
        enabled=True,
        model_path="facebook/mbart-large-50-many-to-many-mmt",
        device="cpu"
    ))


@dataclass
class AccessibilityConfig:
    """完整的无障碍服务配置"""
    service: ServiceConfig = field(default_factory=ServiceConfig)
    modules: ModulesConfig = field(default_factory=ModulesConfig)
    features: Dict[str, Any] = field(default_factory=dict)
    models: Dict[str, str] = field(default_factory=dict)


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path or self._find_config_file()
        self._config = None
        self._load_config()
    
    def _find_config_file(self) -> Optional[str]:
        """查找配置文件"""
        possible_paths = [
            os.environ.get("ACCESSIBILITY_CONFIG"),
            "config/config.yaml",
            "config.yaml",
            "/etc/accessibility-service/config.yaml"
        ]
        
        for path in possible_paths:
            if path and Path(path).exists():
                return path
        
        return None
    
    def _load_config(self):
        """加载配置"""
        try:
            # 从默认值开始
            self._config = AccessibilityConfig()
            
            # 加载配置文件
            if self.config_path:
                self._load_from_file(self.config_path)
            
            # 应用环境变量覆盖
            self._apply_env_overrides()
            
            logger.info(f"配置加载完成，配置文件: {self.config_path or '使用默认配置'}")
            
        except Exception as e:
            logger.error(f"配置加载失败: {str(e)}")
            # 使用默认配置
            self._config = AccessibilityConfig()
    
    def _load_from_file(self, config_path: str):
        """从文件加载配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            if not config_data:
                return
            
            # 更新服务配置
            if 'service' in config_data:
                self._update_service_config(config_data['service'])
            
            # 更新模块配置
            if 'modules' in config_data:
                self._update_modules_config(config_data['modules'])
            
            # 更新特性配置
            if 'features' in config_data:
                self._config.features.update(config_data['features'])
            
            # 更新模型配置
            if 'models' in config_data:
                self._config.models.update(config_data['models'])
                
        except Exception as e:
            logger.error(f"配置文件加载失败: {str(e)}")
    
    def _update_service_config(self, service_data: Dict[str, Any]):
        """更新服务配置"""
        for key, value in service_data.items():
            if hasattr(self._config.service, key):
                setattr(self._config.service, key, value)
    
    def _update_modules_config(self, modules_data: Dict[str, Any]):
        """更新模块配置"""
        for module_name, module_data in modules_data.items():
            if hasattr(self._config.modules, module_name):
                module_config = getattr(self._config.modules, module_name)
                for key, value in module_data.items():
                    if hasattr(module_config, key):
                        setattr(module_config, key, value)
    
    def _apply_env_overrides(self):
        """应用环境变量覆盖"""
        # 服务配置环境变量
        env_mappings = {
            'ACCESSIBILITY_HOST': ('service', 'host'),
            'ACCESSIBILITY_PORT': ('service', 'port', int),
            'ACCESSIBILITY_DEBUG': ('service', 'debug', self._str_to_bool),
            'ACCESSIBILITY_LOG_LEVEL': ('service', 'log_level'),
            'ACCESSIBILITY_MAX_WORKERS': ('service', 'max_workers', int),
            'ACCESSIBILITY_CACHE_ENABLED': ('service', 'cache_enabled', self._str_to_bool),
            'ACCESSIBILITY_REDIS_URL': ('service', 'redis_url'),
            'ACCESSIBILITY_DATABASE_URL': ('service', 'database_url'),
            'ACCESSIBILITY_JWT_SECRET': ('service', 'jwt_secret'),
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.environ.get(env_var)
            if value is not None:
                self._set_config_value(config_path, value)
        
        # 模块配置环境变量
        module_env_mappings = {
            'BLIND_ASSISTANCE_ENABLED': ('modules', 'blind_assistance', 'enabled', self._str_to_bool),
            'BLIND_ASSISTANCE_DEVICE': ('modules', 'blind_assistance', 'device'),
            'SIGN_LANGUAGE_ENABLED': ('modules', 'sign_language', 'enabled', self._str_to_bool),
            'VOICE_ASSISTANCE_ENABLED': ('modules', 'voice_assistance', 'enabled', self._str_to_bool),
            'TRANSLATION_ENABLED': ('modules', 'translation', 'enabled', self._str_to_bool),
        }
        
        for env_var, config_path in module_env_mappings.items():
            value = os.environ.get(env_var)
            if value is not None:
                self._set_config_value(config_path, value)
    
    def _set_config_value(self, config_path: tuple, value: str):
        """设置配置值"""
        try:
            obj = self._config
            
            # 导航到目标对象
            for key in config_path[:-2]:
                obj = getattr(obj, key)
            
            # 获取转换函数（如果有）
            converter = config_path[-1] if len(config_path) > 2 and callable(config_path[-1]) else str
            
            # 设置值
            attr_name = config_path[-2] if len(config_path) > 2 and callable(config_path[-1]) else config_path[-1]
            converted_value = converter(value)
            setattr(obj, attr_name, converted_value)
            
        except Exception as e:
            logger.warning(f"设置配置值失败 {config_path}: {str(e)}")
    
    def _str_to_bool(self, value: str) -> bool:
        """字符串转布尔值"""
        return value.lower() in ('true', '1', 'yes', 'on', 'enabled')
    
    def get_config(self) -> AccessibilityConfig:
        """获取配置"""
        return self._config
    
    def get_service_config(self) -> ServiceConfig:
        """获取服务配置"""
        return self._config.service
    
    def get_module_config(self, module_name: str) -> Optional[ModuleConfig]:
        """获取模块配置"""
        return getattr(self._config.modules, module_name, None)
    
    def get_feature_config(self, feature_name: str) -> Dict[str, Any]:
        """获取特性配置"""
        return self._config.features.get(feature_name, {})
    
    def get_model_path(self, model_name: str) -> Optional[str]:
        """获取模型路径"""
        return self._config.models.get(model_name)
    
    def reload_config(self):
        """重新加载配置"""
        logger.info("重新加载配置")
        self._load_config()
    
    def validate_config(self) -> Dict[str, Any]:
        """验证配置"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            # 验证服务配置
            service_config = self._config.service
            
            if service_config.port < 1 or service_config.port > 65535:
                validation_result["errors"].append("端口号必须在1-65535之间")
            
            if service_config.max_workers < 1:
                validation_result["errors"].append("最大工作线程数必须大于0")
            
            if service_config.request_timeout < 1:
                validation_result["errors"].append("请求超时时间必须大于0")
            
            # 验证模块配置
            modules_config = self._config.modules
            enabled_modules = []
            
            for module_name in ['blind_assistance', 'sign_language', 'voice_assistance', 
                              'screen_reading', 'content_conversion', 'translation']:
                module_config = getattr(modules_config, module_name)
                if module_config.enabled:
                    enabled_modules.append(module_name)
            
            if not enabled_modules:
                validation_result["warnings"].append("没有启用任何模块")
            
            # 检查设备配置
            for module_name in enabled_modules:
                module_config = getattr(modules_config, module_name)
                if module_config.device not in ['cpu', 'cuda', 'mps']:
                    validation_result["warnings"].append(
                        f"{module_name}模块的设备配置'{module_config.device}'可能不受支持"
                    )
            
            validation_result["valid"] = len(validation_result["errors"]) == 0
            
        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"配置验证失败: {str(e)}")
        
        return validation_result
    
    def to_dict(self) -> Dict[str, Any]:
        """将配置转换为字典"""
        def dataclass_to_dict(obj):
            if hasattr(obj, '__dataclass_fields__'):
                return {
                    field_name: dataclass_to_dict(getattr(obj, field_name))
                    for field_name in obj.__dataclass_fields__
                }
            elif isinstance(obj, dict):
                return {k: dataclass_to_dict(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [dataclass_to_dict(item) for item in obj]
            else:
                return obj
        
        return dataclass_to_dict(self._config)


# 全局配置管理器实例
_config_manager = None


def get_config_manager(config_path: Optional[str] = None) -> ConfigManager:
    """获取配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_path)
    return _config_manager


def get_config() -> AccessibilityConfig:
    """获取配置"""
    return get_config_manager().get_config() 