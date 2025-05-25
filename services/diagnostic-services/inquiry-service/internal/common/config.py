#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理模块
"""

import os
import yaml
import logging
from typing import Any, Dict, Optional, Union
from pathlib import Path
from dataclasses import dataclass, field

from .exceptions import ConfigurationError


@dataclass
class ServerConfig:
    """服务器配置"""
    host: str = "0.0.0.0"
    port: int = 50052
    max_workers: int = 10
    enable_reflection: bool = True
    enable_health_check: bool = True


@dataclass
class CacheConfig:
    """缓存配置"""
    type: str = "memory"  # memory, redis
    memory: Dict[str, Any] = field(default_factory=lambda: {
        "max_size": 1000,
        "default_ttl": 3600
    })
    redis: Dict[str, Any] = field(default_factory=lambda: {
        "url": "redis://localhost:6379/0",
        "default_ttl": 3600,
        "key_prefix": "inquiry:"
    })


@dataclass
class MetricsConfig:
    """指标配置"""
    enable_prometheus: bool = False
    prometheus_port: int = 8000
    retention_hours: int = 24
    max_points_per_metric: int = 1000


@dataclass
class LoggingConfig:
    """日志配置"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_structured_logging: bool = False


@dataclass
class TCMKnowledgeConfig:
    """中医知识库配置"""
    data_path: str = "data/tcm_knowledge"
    auto_create_sample_data: bool = True
    cache_ttl: int = 3600
    enable_fuzzy_matching: bool = True


@dataclass
class SymptomExtractionConfig:
    """症状提取配置"""
    model_path: str = ""
    min_confidence: float = 0.6
    batch_size: int = 16
    enable_negation_detection: bool = True
    max_symptoms_per_text: int = 30
    max_text_length: int = 10000


@dataclass
class HealthRiskAssessmentConfig:
    """健康风险评估配置"""
    min_confidence: float = 0.5
    enable_body_constitution_analysis: bool = True
    risk_threshold_immediate: float = 0.7
    risk_threshold_long_term: float = 0.5


@dataclass
class DatabaseConfig:
    """数据库配置"""
    type: str = "sqlite"  # sqlite, postgresql, mysql
    sqlite: Dict[str, Any] = field(default_factory=lambda: {
        "path": "data/inquiry.db"
    })
    postgresql: Dict[str, Any] = field(default_factory=lambda: {
        "host": "localhost",
        "port": 5432,
        "database": "inquiry",
        "username": "inquiry_user",
        "password": "inquiry_pass"
    })


@dataclass
class SecurityConfig:
    """安全配置"""
    enable_authentication: bool = False
    enable_authorization: bool = False
    jwt_secret: str = "your-secret-key"
    jwt_expiration_hours: int = 24
    rate_limit_requests_per_minute: int = 100


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._find_config_file()
        self._config_data: Dict[str, Any] = {}
        self._logger = logging.getLogger(self.__class__.__name__)
        
        # 加载配置
        self._load_config()
        
        # 创建配置对象
        self.server = self._create_server_config()
        self.cache = self._create_cache_config()
        self.metrics = self._create_metrics_config()
        self.logging = self._create_logging_config()
        self.tcm_knowledge = self._create_tcm_knowledge_config()
        self.symptom_extraction = self._create_symptom_extraction_config()
        self.health_risk_assessment = self._create_health_risk_assessment_config()
        self.database = self._create_database_config()
        self.security = self._create_security_config()
        
        self._logger.info(f"配置管理器初始化完成，配置文件: {self.config_path}")
    
    def _find_config_file(self) -> str:
        """查找配置文件"""
        possible_paths = [
            "config/config.yaml",
            "config/config.yml",
            "config.yaml",
            "config.yml",
            os.path.join(os.path.dirname(__file__), "../../../config/config.yaml"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # 如果没有找到配置文件，返回默认路径
        return "config/config.yaml"
    
    def _load_config(self) -> None:
        """加载配置文件"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as file:
                    self._config_data = yaml.safe_load(file) or {}
                self._logger.info(f"配置文件加载成功: {self.config_path}")
            else:
                self._logger.warning(f"配置文件不存在: {self.config_path}，使用默认配置")
                self._config_data = {}
        except Exception as e:
            self._logger.error(f"加载配置文件失败: {str(e)}")
            raise ConfigurationError(f"加载配置文件失败: {str(e)}")
        
        # 从环境变量覆盖配置
        self._load_from_environment()
    
    def _load_from_environment(self) -> None:
        """从环境变量加载配置"""
        env_mappings = {
            "INQUIRY_SERVER_HOST": ("server", "host"),
            "INQUIRY_SERVER_PORT": ("server", "port"),
            "INQUIRY_CACHE_TYPE": ("cache", "type"),
            "INQUIRY_REDIS_URL": ("cache", "redis", "url"),
            "INQUIRY_LOG_LEVEL": ("logging", "level"),
            "INQUIRY_ENABLE_PROMETHEUS": ("metrics", "enable_prometheus"),
            "INQUIRY_PROMETHEUS_PORT": ("metrics", "prometheus_port"),
            "INQUIRY_TCM_DATA_PATH": ("tcm_knowledge", "data_path"),
            "INQUIRY_MIN_CONFIDENCE": ("symptom_extraction", "min_confidence"),
            "INQUIRY_DB_TYPE": ("database", "type"),
            "INQUIRY_DB_PATH": ("database", "sqlite", "path"),
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                self._set_nested_config(config_path, value)
    
    def _set_nested_config(self, path: tuple, value: str) -> None:
        """设置嵌套配置值"""
        current = self._config_data
        
        # 确保路径存在
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # 设置值，尝试转换类型
        final_key = path[-1]
        try:
            # 尝试转换为数字
            if value.isdigit():
                current[final_key] = int(value)
            elif value.replace('.', '').isdigit():
                current[final_key] = float(value)
            elif value.lower() in ('true', 'false'):
                current[final_key] = value.lower() == 'true'
            else:
                current[final_key] = value
        except (ValueError, AttributeError):
            current[final_key] = value
    
    def _get_config_section(self, section: str, default: Optional[Dict] = None) -> Dict[str, Any]:
        """获取配置段"""
        return self._config_data.get(section, default or {})
    
    def _create_server_config(self) -> ServerConfig:
        """创建服务器配置"""
        config = self._get_config_section("server")
        return ServerConfig(
            host=config.get("host", "0.0.0.0"),
            port=config.get("port", 50052),
            max_workers=config.get("max_workers", 10),
            enable_reflection=config.get("enable_reflection", True),
            enable_health_check=config.get("enable_health_check", True)
        )
    
    def _create_cache_config(self) -> CacheConfig:
        """创建缓存配置"""
        config = self._get_config_section("cache")
        return CacheConfig(
            type=config.get("type", "memory"),
            memory=config.get("memory", {
                "max_size": 1000,
                "default_ttl": 3600
            }),
            redis=config.get("redis", {
                "url": "redis://localhost:6379/0",
                "default_ttl": 3600,
                "key_prefix": "inquiry:"
            })
        )
    
    def _create_metrics_config(self) -> MetricsConfig:
        """创建指标配置"""
        config = self._get_config_section("metrics")
        return MetricsConfig(
            enable_prometheus=config.get("enable_prometheus", False),
            prometheus_port=config.get("prometheus_port", 8000),
            retention_hours=config.get("retention_hours", 24),
            max_points_per_metric=config.get("max_points_per_metric", 1000)
        )
    
    def _create_logging_config(self) -> LoggingConfig:
        """创建日志配置"""
        config = self._get_config_section("logging")
        return LoggingConfig(
            level=config.get("level", "INFO"),
            format=config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            file_path=config.get("file_path"),
            max_file_size=config.get("max_file_size", 10 * 1024 * 1024),
            backup_count=config.get("backup_count", 5),
            enable_structured_logging=config.get("enable_structured_logging", False)
        )
    
    def _create_tcm_knowledge_config(self) -> TCMKnowledgeConfig:
        """创建中医知识库配置"""
        config = self._get_config_section("tcm_knowledge")
        return TCMKnowledgeConfig(
            data_path=config.get("data_path", "data/tcm_knowledge"),
            auto_create_sample_data=config.get("auto_create_sample_data", True),
            cache_ttl=config.get("cache_ttl", 3600),
            enable_fuzzy_matching=config.get("enable_fuzzy_matching", True)
        )
    
    def _create_symptom_extraction_config(self) -> SymptomExtractionConfig:
        """创建症状提取配置"""
        config = self._get_config_section("symptom_extraction")
        return SymptomExtractionConfig(
            model_path=config.get("model_path", ""),
            min_confidence=config.get("min_confidence", 0.6),
            batch_size=config.get("batch_size", 16),
            enable_negation_detection=config.get("enable_negation_detection", True),
            max_symptoms_per_text=config.get("max_symptoms_per_text", 30),
            max_text_length=config.get("max_text_length", 10000)
        )
    
    def _create_health_risk_assessment_config(self) -> HealthRiskAssessmentConfig:
        """创建健康风险评估配置"""
        config = self._get_config_section("health_risk_assessment")
        return HealthRiskAssessmentConfig(
            min_confidence=config.get("min_confidence", 0.5),
            enable_body_constitution_analysis=config.get("enable_body_constitution_analysis", True),
            risk_threshold_immediate=config.get("risk_threshold_immediate", 0.7),
            risk_threshold_long_term=config.get("risk_threshold_long_term", 0.5)
        )
    
    def _create_database_config(self) -> DatabaseConfig:
        """创建数据库配置"""
        config = self._get_config_section("database")
        return DatabaseConfig(
            type=config.get("type", "sqlite"),
            sqlite=config.get("sqlite", {"path": "data/inquiry.db"}),
            postgresql=config.get("postgresql", {
                "host": "localhost",
                "port": 5432,
                "database": "inquiry",
                "username": "inquiry_user",
                "password": "inquiry_pass"
            })
        )
    
    def _create_security_config(self) -> SecurityConfig:
        """创建安全配置"""
        config = self._get_config_section("security")
        return SecurityConfig(
            enable_authentication=config.get("enable_authentication", False),
            enable_authorization=config.get("enable_authorization", False),
            jwt_secret=config.get("jwt_secret", "your-secret-key"),
            jwt_expiration_hours=config.get("jwt_expiration_hours", 24),
            rate_limit_requests_per_minute=config.get("rate_limit_requests_per_minute", 100)
        )
    
    def get_raw_config(self) -> Dict[str, Any]:
        """获取原始配置数据"""
        return self._config_data.copy()
    
    def get_config_value(self, key_path: str, default: Any = None) -> Any:
        """获取配置值，支持点号分隔的路径"""
        keys = key_path.split('.')
        current = self._config_data
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    def set_config_value(self, key_path: str, value: Any) -> None:
        """设置配置值，支持点号分隔的路径"""
        keys = key_path.split('.')
        current = self._config_data
        
        # 确保路径存在
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def reload_config(self) -> None:
        """重新加载配置"""
        self._load_config()
        
        # 重新创建配置对象
        self.server = self._create_server_config()
        self.cache = self._create_cache_config()
        self.metrics = self._create_metrics_config()
        self.logging = self._create_logging_config()
        self.tcm_knowledge = self._create_tcm_knowledge_config()
        self.symptom_extraction = self._create_symptom_extraction_config()
        self.health_risk_assessment = self._create_health_risk_assessment_config()
        self.database = self._create_database_config()
        self.security = self._create_security_config()
        
        self._logger.info("配置已重新加载")
    
    def save_config(self, path: Optional[str] = None) -> None:
        """保存配置到文件"""
        save_path = path or self.config_path
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'w', encoding='utf-8') as file:
                yaml.dump(self._config_data, file, default_flow_style=False, allow_unicode=True)
            
            self._logger.info(f"配置已保存到: {save_path}")
        except Exception as e:
            self._logger.error(f"保存配置失败: {str(e)}")
            raise ConfigurationError(f"保存配置失败: {str(e)}")
    
    def validate_config(self) -> List[str]:
        """验证配置，返回错误列表"""
        errors = []
        
        # 验证服务器配置
        if not (1 <= self.server.port <= 65535):
            errors.append(f"无效的服务器端口: {self.server.port}")
        
        if self.server.max_workers < 1:
            errors.append(f"无效的最大工作线程数: {self.server.max_workers}")
        
        # 验证缓存配置
        if self.cache.type not in ("memory", "redis"):
            errors.append(f"不支持的缓存类型: {self.cache.type}")
        
        # 验证指标配置
        if not (1 <= self.metrics.prometheus_port <= 65535):
            errors.append(f"无效的Prometheus端口: {self.metrics.prometheus_port}")
        
        # 验证症状提取配置
        if not (0.0 <= self.symptom_extraction.min_confidence <= 1.0):
            errors.append(f"无效的最小置信度: {self.symptom_extraction.min_confidence}")
        
        # 验证健康风险评估配置
        if not (0.0 <= self.health_risk_assessment.min_confidence <= 1.0):
            errors.append(f"无效的风险评估最小置信度: {self.health_risk_assessment.min_confidence}")
        
        return errors 