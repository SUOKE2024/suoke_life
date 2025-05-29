#!/usr/bin/env python

"""
无障碍服务配置模块
"""

import logging
import os
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class ConfigSection:
    """配置节，提供属性形式访问配置"""

    def __init__(self, section_data: dict[str, Any]):
        """
        初始化配置节

        Args:
            section_data: 节配置数据
        """
        self._data = section_data or {}

    def __getattr__(self, name):
        """
        通过属性访问配置项

        Args:
            name: 属性名

        Returns:
            配置值，如果值是字典则返回ConfigSection对象
        """
        if name in self._data:
            value = self._data[name]
            if isinstance(value, dict):
                return ConfigSection(value)
            return value
        raise AttributeError(f"配置未定义属性: {name}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项

        Args:
            key: 配置键
            default: 默认值

        Returns:
            配置值
        """
        return self._data.get(key, default)

    def to_dict(self) -> dict[str, Any]:
        """
        转换为字典

        Returns:
            字典形式的配置
        """
        return self._data.copy()


class Config:
    """配置类，负责加载和管理服务配置"""

    def __init__(self, config_path: str | None = None):
        """
        初始化配置

        Args:
            config_path: 配置文件路径，如果为None则使用环境变量或默认路径
        """
        self.config_data = {}
        self.config_path = config_path or os.environ.get(
            "ACCESSIBILITY_CONFIG_PATH",
            os.path.join(os.path.dirname(__file__), "config.yaml")
        )
        self.load_config()
        self._init_section_properties()

    def load_config(self) -> None:
        """从配置文件加载配置"""
        try:
            with open(self.config_path, encoding='utf-8') as f:
                self.config_data = yaml.safe_load(f)
            logger.info(f"成功从 {self.config_path} 加载配置")
        except Exception as e:
            logger.warning(f"无法加载配置文件: {str(e)}，将使用默认配置")
            self._set_default_config()

    def _init_section_properties(self):
        """初始化节属性"""
        # 为主要配置节创建属性
        self._service = ConfigSection(self.config_data.get("service", {}))
        self._models = ConfigSection(self.config_data.get("models", {}))
        self._logging = ConfigSection(self.config_data.get("logging", {}))
        self._database = ConfigSection(self.config_data.get("database", {}))
        self._features = ConfigSection(self.config_data.get("features", {}))
        self._integration = ConfigSection(self.config_data.get("integration", {}))

        # 新增服务配置节
        self._edge_computing = ConfigSection(self.config_data.get("edge_computing", {}))
        self._background_collection = ConfigSection(self.config_data.get("background_collection", {}))
        self._agent_coordination = ConfigSection(self.config_data.get("agent_coordination", {}))
        self._observability = ConfigSection(self.config_data.get("observability", {}))
        self._security = ConfigSection(self.config_data.get("security", {}))
        self._resilience = ConfigSection(self.config_data.get("resilience", {}))

    def _set_default_config(self) -> None:
        """设置默认配置"""
        self.config_data = {
            "service": {
                "name": "accessibility-service",
                "version": "0.2.0",
                "host": "0.0.0.0",
                "port": 50051,
                "data_root": "/var/lib/accessibility-service"
            },
            "models": {
                "scene_model": "microsoft/beit-base-patch16-224-pt22k",
                "sign_language_model": "mediapipe/hands",
                "speech_model": {
                    "asr": "silero-models/silero-stt-model",
                    "tts": "silero-models/silero-tts-model"
                },
                "conversion_model": "google/flan-t5-base"
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "/var/log/accessibility-service/service.log"
            },
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "accessibility_db",
                "user": "accessibility_user",
                "password": "password"  # 实际环境中应使用环境变量或安全存储
            },
            "features": {
                "blind_assistance": {
                    "enabled": True,
                    "max_image_size": 1024,
                    "confidence_threshold": 0.7
                },
                "sign_language": {
                    "enabled": True,
                    "supported_languages": ["zh-CN", "en-US"]
                },
                "screen_reading": {
                    "enabled": True,
                    "element_detection_threshold": 0.6
                },
                "voice_assistance": {
                    "enabled": True,
                    "supported_dialects": [
                        "mandarin", "cantonese", "sichuanese", "shanghainese",
                        "hokkien", "hakka", "northeastern", "northwestern"
                    ]
                },
                "content_conversion": {
                    "enabled": True,
                    "supported_formats": ["audio", "simplified", "braille"]
                }
            },
            "integration": {
                "xiaoai_service": {
                    "host": "xiaoai-service",
                    "port": 50052,
                    "timeout_ms": 5000,
                    "retry": 3
                },
                "xiaoke_service": {
                    "host": "xiaoke-service",
                    "port": 50053,
                    "timeout_ms": 5000,
                    "retry": 3
                },
                "laoke_service": {
                    "host": "laoke-service",
                    "port": 50054,
                    "timeout_ms": 5000,
                    "retry": 3
                },
                "soer_service": {
                    "host": "soer-service",
                    "port": 50055,
                    "timeout_ms": 5000,
                    "retry": 3
                }
            },
            # 默认新服务配置
            "edge_computing": {
                "enabled": True,
                "models": {},
                "offline_mode": {
                    "enabled": True,
                    "features": [],
                    "max_cache_size_mb": 200
                }
            },
            "background_collection": {
                "enabled": False,
                "collection_types": {},
                "consent": {
                    "require_explicit": True,
                    "default_expiry_days": 365
                },
                "battery_optimization": {
                    "low_power_mode": {
                        "enabled": True
                    }
                }
            },
            "agent_coordination": {
                "event_bus": {
                    "type": "memory"
                }
            },
            "observability": {
                "metrics": {
                    "provider": "memory",
                    "interval_seconds": 60
                },
                "tracing": {
                    "provider": "memory",
                    "service_name": "accessibility-service"
                },
                "logging": {
                    "provider": "stdout",
                    "structured": True
                }
            },
            "security": {
                "encryption": {
                    "data_at_rest": {
                        "algorithm": "AES-256-GCM"
                    }
                },
                "access_control": {
                    "authorization": {
                        "rbac_enabled": False,
                        "default_deny": False
                    }
                }
            },
            "resilience": {
                "backup": {
                    "enabled": False
                }
            }
        }

    def __getattr__(self, name):
        """
        通过属性访问配置项

        Args:
            name: 属性名

        Returns:
            配置节或属性值
        """
        # 先检查是否有对应的配置节属性
        section_attr = f"_{name}"
        # 使用对象字典直接检查，避免触发递归
        if section_attr in self.__dict__:
            return self.__dict__[section_attr]

        # 如果是直接在配置数据中的键
        if name in self.config_data:
            value = self.config_data[name]
            if isinstance(value, dict):
                return ConfigSection(value)
            return value

        # 检查是否是嵌套配置路径
        if "." in name:
            parts = name.split(".", 1)  # 只拆分第一个点
            root_name, remainder = parts

            # 尝试获取根配置节
            try:
                root_section = self.__getattr__(root_name)
                if isinstance(root_section, ConfigSection):
                    try:
                        return getattr(root_section, remainder)
                    except AttributeError:
                        pass
            except AttributeError:
                pass

        raise AttributeError(f"配置未定义属性: {name}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项

        Args:
            key: 配置键路径，使用点号分隔，例如 "service.port"
            default: 默认值，如果指定键不存在则返回此值

        Returns:
            配置项值
        """
        keys = key.split('.')
        value = self.config_data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        设置配置项

        Args:
            key: 配置键路径，使用点号分隔，例如 "service.port"
            value: 配置值
        """
        keys = key.split('.')
        config = self.config_data

        for _i, k in enumerate(keys[:-1]):
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

        # 更新配置节属性
        self._init_section_properties()

    def save(self) -> None:
        """保存配置到文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config_data, f, default_flow_style=False, sort_keys=False)
            logger.info(f"配置已保存到 {self.config_path}")
        except Exception as e:
            logger.error(f"保存配置失败: {str(e)}")

    def as_dict(self) -> dict[str, Any]:
        """将配置转换为字典

        Returns:
            Dict[str, Any]: 配置字典
        """
        config_dict = {}

        for key, value in self.config_data.items():
            if isinstance(value, dict):
                # 递归处理嵌套字典
                config_dict[key] = self._dict_to_nested_dict(value)
            else:
                config_dict[key] = value

        return config_dict

    def _dict_to_nested_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        """递归将嵌套字典中的值处理为字典

        Args:
            data: 字典数据

        Returns:
            Dict[str, Any]: 处理后的字典
        """
        result = {}

        for key, value in data.items():
            if isinstance(value, dict):
                # 递归处理嵌套字典
                result[key] = self._dict_to_nested_dict(value)
            else:
                result[key] = value

        return result

    # 属性访问器
    @property
    def service(self) -> ConfigSection:
        """服务配置节"""
        return self._service

    @property
    def models(self) -> ConfigSection:
        """模型配置节"""
        return self._models

    @property
    def logging(self) -> ConfigSection:
        """日志配置节"""
        return self._logging

    @property
    def database(self) -> ConfigSection:
        """数据库配置节"""
        return self._database

    @property
    def features(self) -> ConfigSection:
        """功能特性配置节"""
        return self._features

    @property
    def integration(self) -> ConfigSection:
        """集成配置节"""
        return self._integration

    # 新增服务属性访问器
    @property
    def edge_computing(self) -> ConfigSection:
        """边缘计算配置节"""
        return self._edge_computing

    @property
    def background_collection(self) -> ConfigSection:
        """后台数据采集配置节"""
        return self._background_collection

    @property
    def agent_coordination(self) -> ConfigSection:
        """智能体协作配置节"""
        return self._agent_coordination

    @property
    def observability(self) -> ConfigSection:
        """可观测性配置节"""
        return self._observability

    @property
    def security(self) -> ConfigSection:
        """安全配置节"""
        return self._security

    @property
    def resilience(self) -> ConfigSection:
        """容灾与弹性配置节"""
        return self._resilience


# 单例实例
config = Config()
