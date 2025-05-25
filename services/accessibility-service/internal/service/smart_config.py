#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能配置管理系统 - 动态配置管理和智能优化
包含配置验证、热重载、版本管理、自动优化等功能
"""

import logging
import time
import asyncio
import json
import yaml
import os
import hashlib
import threading
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
from pathlib import Path
import copy
import jsonschema
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)


class ConfigType(Enum):
    """配置类型枚举"""
    SYSTEM = "system"
    SERVICE = "service"
    AI_MODEL = "ai_model"
    SENSOR = "sensor"
    USER_PREFERENCE = "user_preference"
    SECURITY = "security"
    PERFORMANCE = "performance"
    ACCESSIBILITY = "accessibility"


class ConfigSource(Enum):
    """配置源枚举"""
    FILE = "file"
    DATABASE = "database"
    ENVIRONMENT = "environment"
    REMOTE_API = "remote_api"
    USER_INPUT = "user_input"
    AUTO_GENERATED = "auto_generated"


class ValidationLevel(Enum):
    """验证级别枚举"""
    STRICT = "strict"      # 严格验证，任何错误都拒绝
    MODERATE = "moderate"  # 中等验证，警告但允许
    LENIENT = "lenient"    # 宽松验证，仅记录错误


@dataclass
class ConfigItem:
    """配置项"""
    key: str
    value: Any
    config_type: ConfigType
    source: ConfigSource
    timestamp: float
    version: int = 1
    description: str = ""
    schema: Optional[Dict[str, Any]] = None
    is_sensitive: bool = False
    requires_restart: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConfigChange:
    """配置变更记录"""
    change_id: str
    config_key: str
    old_value: Any
    new_value: Any
    change_type: str  # "create", "update", "delete"
    timestamp: float
    source: ConfigSource
    user_id: Optional[str] = None
    reason: str = ""
    rollback_available: bool = True


@dataclass
class ConfigValidationResult:
    """配置验证结果"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


class ConfigValidator:
    """配置验证器"""
    
    def __init__(self):
        self.schemas = {}  # config_type -> schema
        self.custom_validators = {}  # config_key -> validator function
        self.validation_rules = {}  # config_type -> rules
        
        # 初始化默认模式
        self._initialize_default_schemas()
    
    def _initialize_default_schemas(self):
        """初始化默认配置模式"""
        
        # 系统配置模式
        self.schemas[ConfigType.SYSTEM] = {
            "type": "object",
            "properties": {
                "log_level": {
                    "type": "string",
                    "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
                },
                "max_workers": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100
                },
                "timeout": {
                    "type": "number",
                    "minimum": 0.1,
                    "maximum": 300.0
                },
                "enabled": {
                    "type": "boolean"
                }
            }
        }
        
        # 服务配置模式
        self.schemas[ConfigType.SERVICE] = {
            "type": "object",
            "properties": {
                "host": {
                    "type": "string",
                    "pattern": r"^[a-zA-Z0-9.-]+$"
                },
                "port": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 65535
                },
                "ssl_enabled": {
                    "type": "boolean"
                },
                "max_connections": {
                    "type": "integer",
                    "minimum": 1
                }
            }
        }
        
        # AI模型配置模式
        self.schemas[ConfigType.AI_MODEL] = {
            "type": "object",
            "properties": {
                "model_name": {
                    "type": "string",
                    "minLength": 1
                },
                "model_path": {
                    "type": "string"
                },
                "batch_size": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 1000
                },
                "learning_rate": {
                    "type": "number",
                    "minimum": 0.0001,
                    "maximum": 1.0
                },
                "temperature": {
                    "type": "number",
                    "minimum": 0.1,
                    "maximum": 2.0
                }
            }
        }
        
        # 传感器配置模式
        self.schemas[ConfigType.SENSOR] = {
            "type": "object",
            "properties": {
                "sensor_id": {
                    "type": "string",
                    "pattern": r"^[a-zA-Z0-9_-]+$"
                },
                "sampling_rate": {
                    "type": "number",
                    "minimum": 0.1,
                    "maximum": 1000.0
                },
                "threshold": {
                    "type": "number"
                },
                "calibration": {
                    "type": "object",
                    "properties": {
                        "offset": {"type": "number"},
                        "scale": {"type": "number", "minimum": 0.001}
                    }
                }
            }
        }
    
    def register_schema(self, config_type: ConfigType, schema: Dict[str, Any]):
        """注册配置模式"""
        self.schemas[config_type] = schema
        logger.info(f"注册配置模式: {config_type.value}")
    
    def register_custom_validator(self, config_key: str, validator: Callable[[Any], ConfigValidationResult]):
        """注册自定义验证器"""
        self.custom_validators[config_key] = validator
        logger.info(f"注册自定义验证器: {config_key}")
    
    def validate_config(self, config_item: ConfigItem, 
                       validation_level: ValidationLevel = ValidationLevel.MODERATE) -> ConfigValidationResult:
        """验证配置项"""
        result = ConfigValidationResult(is_valid=True)
        
        try:
            # 1. 模式验证
            if config_item.config_type in self.schemas:
                schema = self.schemas[config_item.config_type]
                try:
                    jsonschema.validate(config_item.value, schema)
                except jsonschema.ValidationError as e:
                    error_msg = f"模式验证失败: {e.message}"
                    if validation_level == ValidationLevel.STRICT:
                        result.is_valid = False
                        result.errors.append(error_msg)
                    else:
                        result.warnings.append(error_msg)
            
            # 2. 自定义验证器
            if config_item.key in self.custom_validators:
                custom_result = self.custom_validators[config_item.key](config_item.value)
                result.errors.extend(custom_result.errors)
                result.warnings.extend(custom_result.warnings)
                result.suggestions.extend(custom_result.suggestions)
                
                if custom_result.errors and validation_level == ValidationLevel.STRICT:
                    result.is_valid = False
            
            # 3. 业务逻辑验证
            business_result = self._validate_business_logic(config_item)
            result.errors.extend(business_result.errors)
            result.warnings.extend(business_result.warnings)
            result.suggestions.extend(business_result.suggestions)
            
            if business_result.errors and validation_level == ValidationLevel.STRICT:
                result.is_valid = False
            
            # 4. 安全验证
            if config_item.is_sensitive:
                security_result = self._validate_security(config_item)
                result.errors.extend(security_result.errors)
                result.warnings.extend(security_result.warnings)
                
                if security_result.errors:
                    result.is_valid = False  # 安全问题总是严格处理
            
        except Exception as e:
            result.is_valid = False
            result.errors.append(f"验证过程异常: {str(e)}")
        
        return result
    
    def _validate_business_logic(self, config_item: ConfigItem) -> ConfigValidationResult:
        """业务逻辑验证"""
        result = ConfigValidationResult(is_valid=True)
        
        # 根据配置类型进行特定验证
        if config_item.config_type == ConfigType.SYSTEM:
            if config_item.key == "max_workers":
                if isinstance(config_item.value, int) and config_item.value > 50:
                    result.warnings.append("工作线程数过多可能影响性能")
                    result.suggestions.append("建议设置为CPU核心数的2-4倍")
        
        elif config_item.config_type == ConfigType.AI_MODEL:
            if config_item.key == "batch_size":
                if isinstance(config_item.value, int) and config_item.value > 100:
                    result.warnings.append("批处理大小过大可能导致内存不足")
        
        elif config_item.config_type == ConfigType.SENSOR:
            if config_item.key == "sampling_rate":
                if isinstance(config_item.value, (int, float)) and config_item.value > 100:
                    result.warnings.append("采样率过高可能影响系统性能")
        
        return result
    
    def _validate_security(self, config_item: ConfigItem) -> ConfigValidationResult:
        """安全验证"""
        result = ConfigValidationResult(is_valid=True)
        
        if isinstance(config_item.value, str):
            # 检查是否包含明文密码
            if any(keyword in config_item.key.lower() for keyword in ['password', 'secret', 'key', 'token']):
                if len(config_item.value) < 8:
                    result.errors.append("密码长度不足8位")
                
                if config_item.value.isalnum() and config_item.value.islower():
                    result.warnings.append("密码复杂度不足，建议包含大小写字母、数字和特殊字符")
        
        return result


class ConfigFileWatcher(FileSystemEventHandler):
    """配置文件监控器"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.last_modified = {}
    
    def on_modified(self, event):
        """文件修改事件"""
        if event.is_directory:
            return
        
        file_path = event.src_path
        current_time = time.time()
        
        # 防止重复触发
        if file_path in self.last_modified:
            if current_time - self.last_modified[file_path] < 1.0:  # 1秒内的重复事件忽略
                return
        
        self.last_modified[file_path] = current_time
        
        # 异步处理文件变更
        asyncio.create_task(self.config_manager.reload_config_file(file_path))


class ConfigOptimizer:
    """配置优化器"""
    
    def __init__(self):
        self.optimization_rules = {}
        self.performance_history = deque(maxlen=1000)
        self.optimization_history = deque(maxlen=100)
        
        # 初始化优化规则
        self._initialize_optimization_rules()
    
    def _initialize_optimization_rules(self):
        """初始化优化规则"""
        
        # 性能优化规则
        self.optimization_rules["performance"] = {
            "max_workers": {
                "condition": lambda value, metrics: metrics.get("cpu_usage", 0) > 80,
                "action": lambda value: max(1, value - 1),
                "description": "CPU使用率过高时减少工作线程"
            },
            "batch_size": {
                "condition": lambda value, metrics: metrics.get("memory_usage", 0) > 85,
                "action": lambda value: max(1, int(value * 0.8)),
                "description": "内存使用率过高时减少批处理大小"
            },
            "timeout": {
                "condition": lambda value, metrics: metrics.get("response_time", 0) > value * 0.8,
                "action": lambda value: min(300, value * 1.2),
                "description": "响应时间接近超时时增加超时时间"
            }
        }
        
        # 质量优化规则
        self.optimization_rules["quality"] = {
            "sampling_rate": {
                "condition": lambda value, metrics: metrics.get("data_quality", 1.0) < 0.8,
                "action": lambda value: min(1000, value * 1.1),
                "description": "数据质量低时增加采样率"
            }
        }
    
    def suggest_optimizations(self, current_configs: Dict[str, ConfigItem], 
                            performance_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """建议配置优化"""
        suggestions = []
        
        for category, rules in self.optimization_rules.items():
            for config_key, rule in rules.items():
                # 查找匹配的配置项
                matching_configs = [
                    config for config in current_configs.values()
                    if config.key.endswith(config_key) or config_key in config.key
                ]
                
                for config in matching_configs:
                    try:
                        # 检查优化条件
                        if rule["condition"](config.value, performance_metrics):
                            new_value = rule["action"](config.value)
                            
                            if new_value != config.value:
                                suggestions.append({
                                    "config_key": config.key,
                                    "current_value": config.value,
                                    "suggested_value": new_value,
                                    "reason": rule["description"],
                                    "category": category,
                                    "confidence": self._calculate_confidence(config, performance_metrics)
                                })
                    
                    except Exception as e:
                        logger.error(f"优化建议生成失败: {str(e)}")
        
        return suggestions
    
    def _calculate_confidence(self, config: ConfigItem, metrics: Dict[str, Any]) -> float:
        """计算优化建议的置信度"""
        # 基于历史数据和当前指标计算置信度
        base_confidence = 0.7
        
        # 根据配置项的历史变更频率调整
        if hasattr(self, 'change_frequency'):
            freq = self.change_frequency.get(config.key, 0)
            if freq > 5:  # 频繁变更的配置降低置信度
                base_confidence *= 0.8
        
        # 根据性能指标的稳定性调整
        if len(self.performance_history) > 10:
            recent_metrics = list(self.performance_history)[-10:]
            stability = self._calculate_stability(recent_metrics)
            base_confidence *= stability
        
        return min(1.0, max(0.1, base_confidence))
    
    def _calculate_stability(self, metrics_history: List[Dict[str, Any]]) -> float:
        """计算指标稳定性"""
        if not metrics_history:
            return 0.5
        
        # 计算关键指标的变异系数
        key_metrics = ['cpu_usage', 'memory_usage', 'response_time']
        stability_scores = []
        
        for metric in key_metrics:
            values = [m.get(metric, 0) for m in metrics_history if metric in m]
            if len(values) > 1:
                mean_val = sum(values) / len(values)
                if mean_val > 0:
                    std_val = (sum((x - mean_val) ** 2 for x in values) / len(values)) ** 0.5
                    cv = std_val / mean_val  # 变异系数
                    stability = max(0, 1 - cv)  # 变异系数越小，稳定性越高
                    stability_scores.append(stability)
        
        return sum(stability_scores) / len(stability_scores) if stability_scores else 0.5


class SmartConfigManager:
    """智能配置管理器主类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化智能配置管理器
        
        Args:
            config: 服务配置
        """
        self.config = config
        self.enabled = config.get("smart_config", {}).get("enabled", True)
        
        # 核心组件
        self.validator = ConfigValidator()
        self.optimizer = ConfigOptimizer()
        
        # 配置存储
        self.configs = {}  # key -> ConfigItem
        self.config_history = defaultdict(deque)  # key -> deque of ConfigChange
        self.config_versions = defaultdict(int)  # key -> version
        
        # 文件监控
        self.file_observer = Observer()
        self.file_watcher = ConfigFileWatcher(self)
        self.watched_files = set()
        
        # 配置路径
        self.config_dir = Path(config.get("smart_config", {}).get("config_dir", "config"))
        self.backup_dir = Path(config.get("smart_config", {}).get("backup_dir", "config/backups"))
        
        # 确保目录存在
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置选项
        self.auto_reload = config.get("smart_config", {}).get("auto_reload", True)
        self.auto_backup = config.get("smart_config", {}).get("auto_backup", True)
        self.validation_level = ValidationLevel(
            config.get("smart_config", {}).get("validation_level", "moderate")
        )
        
        # 回调函数
        self.change_callbacks = defaultdict(list)  # config_key -> list of callbacks
        self.global_callbacks = []  # 全局变更回调
        
        # 统计信息
        self.stats = {
            "configs_loaded": 0,
            "configs_updated": 0,
            "validation_errors": 0,
            "auto_optimizations": 0,
            "hot_reloads": 0,
            "rollbacks": 0
        }
        
        # 控制标志
        self.is_running = False
        self._optimization_task = None
        
        logger.info(f"智能配置管理器初始化完成 - 启用: {self.enabled}")
    
    async def start(self):
        """启动配置管理器"""
        if not self.enabled or self.is_running:
            return
        
        logger.info("启动智能配置管理器...")
        
        # 加载初始配置
        await self.load_all_configs()
        
        # 启动文件监控
        if self.auto_reload:
            self._start_file_watching()
        
        # 启动自动优化任务
        self._optimization_task = asyncio.create_task(self._optimization_loop())
        
        self.is_running = True
        logger.info("智能配置管理器已启动")
    
    async def load_all_configs(self):
        """加载所有配置文件"""
        try:
            # 加载YAML配置文件
            for config_file in self.config_dir.glob("*.yaml"):
                await self.load_config_file(str(config_file))
            
            # 加载JSON配置文件
            for config_file in self.config_dir.glob("*.json"):
                await self.load_config_file(str(config_file))
            
            logger.info(f"加载了 {len(self.configs)} 个配置项")
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
    
    async def load_config_file(self, file_path: str):
        """加载单个配置文件"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.warning(f"配置文件不存在: {file_path}")
                return
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() == '.yaml':
                    data = yaml.safe_load(f)
                elif file_path.suffix.lower() == '.json':
                    data = json.load(f)
                else:
                    logger.warning(f"不支持的配置文件格式: {file_path}")
                    return
            
            # 解析配置项
            if isinstance(data, dict):
                await self._parse_config_data(data, file_path)
            
            self.stats["configs_loaded"] += 1
            logger.info(f"加载配置文件: {file_path}")
            
        except Exception as e:
            logger.error(f"加载配置文件失败 {file_path}: {str(e)}")
    
    async def _parse_config_data(self, data: Dict[str, Any], source_file: Path):
        """解析配置数据"""
        for key, value in data.items():
            # 确定配置类型
            config_type = self._determine_config_type(key, value)
            
            # 创建配置项
            config_item = ConfigItem(
                key=key,
                value=value,
                config_type=config_type,
                source=ConfigSource.FILE,
                timestamp=time.time(),
                version=self.config_versions[key] + 1,
                metadata={"source_file": str(source_file)}
            )
            
            # 验证配置
            validation_result = self.validator.validate_config(config_item, self.validation_level)
            
            if validation_result.is_valid or self.validation_level != ValidationLevel.STRICT:
                await self.set_config(key, value, config_type, ConfigSource.FILE, validate=False)
                
                if validation_result.warnings:
                    logger.warning(f"配置 {key} 验证警告: {validation_result.warnings}")
            else:
                self.stats["validation_errors"] += 1
                logger.error(f"配置 {key} 验证失败: {validation_result.errors}")
    
    def _determine_config_type(self, key: str, value: Any) -> ConfigType:
        """确定配置类型"""
        key_lower = key.lower()
        
        if any(keyword in key_lower for keyword in ['system', 'global', 'core']):
            return ConfigType.SYSTEM
        elif any(keyword in key_lower for keyword in ['service', 'server', 'api']):
            return ConfigType.SERVICE
        elif any(keyword in key_lower for keyword in ['model', 'ai', 'ml', 'neural']):
            return ConfigType.AI_MODEL
        elif any(keyword in key_lower for keyword in ['sensor', 'device', 'hardware']):
            return ConfigType.SENSOR
        elif any(keyword in key_lower for keyword in ['user', 'preference', 'setting']):
            return ConfigType.USER_PREFERENCE
        elif any(keyword in key_lower for keyword in ['security', 'auth', 'ssl', 'tls']):
            return ConfigType.SECURITY
        elif any(keyword in key_lower for keyword in ['performance', 'perf', 'optimization']):
            return ConfigType.PERFORMANCE
        elif any(keyword in key_lower for keyword in ['accessibility', 'a11y', 'access']):
            return ConfigType.ACCESSIBILITY
        else:
            return ConfigType.SYSTEM  # 默认类型
    
    def _start_file_watching(self):
        """启动文件监控"""
        try:
            self.file_observer.schedule(
                self.file_watcher,
                str(self.config_dir),
                recursive=True
            )
            self.file_observer.start()
            logger.info(f"启动配置文件监控: {self.config_dir}")
        except Exception as e:
            logger.error(f"启动文件监控失败: {str(e)}")
    
    async def reload_config_file(self, file_path: str):
        """重新加载配置文件"""
        try:
            logger.info(f"热重载配置文件: {file_path}")
            await self.load_config_file(file_path)
            self.stats["hot_reloads"] += 1
        except Exception as e:
            logger.error(f"热重载配置文件失败: {str(e)}")
    
    async def set_config(self, key: str, value: Any, 
                        config_type: ConfigType = ConfigType.SYSTEM,
                        source: ConfigSource = ConfigSource.USER_INPUT,
                        validate: bool = True,
                        user_id: Optional[str] = None,
                        reason: str = "") -> bool:
        """设置配置项"""
        try:
            # 创建新配置项
            new_config = ConfigItem(
                key=key,
                value=value,
                config_type=config_type,
                source=source,
                timestamp=time.time(),
                version=self.config_versions[key] + 1
            )
            
            # 验证配置
            if validate:
                validation_result = self.validator.validate_config(new_config, self.validation_level)
                
                if not validation_result.is_valid and self.validation_level == ValidationLevel.STRICT:
                    logger.error(f"配置验证失败: {validation_result.errors}")
                    return False
                
                if validation_result.warnings:
                    logger.warning(f"配置验证警告: {validation_result.warnings}")
            
            # 备份旧配置
            old_config = self.configs.get(key)
            if old_config and self.auto_backup:
                await self._backup_config(old_config)
            
            # 记录变更
            change = ConfigChange(
                change_id=f"change_{int(time.time())}_{key}",
                config_key=key,
                old_value=old_config.value if old_config else None,
                new_value=value,
                change_type="update" if old_config else "create",
                timestamp=time.time(),
                source=source,
                user_id=user_id,
                reason=reason
            )
            
            # 更新配置
            self.configs[key] = new_config
            self.config_versions[key] = new_config.version
            self.config_history[key].append(change)
            
            # 保持历史记录大小
            if len(self.config_history[key]) > 100:
                self.config_history[key].popleft()
            
            # 触发回调
            await self._trigger_callbacks(key, old_config, new_config)
            
            self.stats["configs_updated"] += 1
            logger.info(f"配置已更新: {key} = {value}")
            
            return True
            
        except Exception as e:
            logger.error(f"设置配置失败: {str(e)}")
            return False
    
    async def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        config_item = self.configs.get(key)
        return config_item.value if config_item else default
    
    async def get_config_item(self, key: str) -> Optional[ConfigItem]:
        """获取配置项"""
        return self.configs.get(key)
    
    async def delete_config(self, key: str, user_id: Optional[str] = None, reason: str = "") -> bool:
        """删除配置项"""
        try:
            if key not in self.configs:
                return False
            
            old_config = self.configs[key]
            
            # 备份配置
            if self.auto_backup:
                await self._backup_config(old_config)
            
            # 记录变更
            change = ConfigChange(
                change_id=f"change_{int(time.time())}_{key}",
                config_key=key,
                old_value=old_config.value,
                new_value=None,
                change_type="delete",
                timestamp=time.time(),
                source=ConfigSource.USER_INPUT,
                user_id=user_id,
                reason=reason
            )
            
            # 删除配置
            del self.configs[key]
            self.config_history[key].append(change)
            
            # 触发回调
            await self._trigger_callbacks(key, old_config, None)
            
            logger.info(f"配置已删除: {key}")
            return True
            
        except Exception as e:
            logger.error(f"删除配置失败: {str(e)}")
            return False
    
    async def _backup_config(self, config_item: ConfigItem):
        """备份配置项"""
        try:
            backup_data = {
                "key": config_item.key,
                "value": config_item.value,
                "config_type": config_item.config_type.value,
                "source": config_item.source.value,
                "timestamp": config_item.timestamp,
                "version": config_item.version,
                "metadata": config_item.metadata
            }
            
            backup_file = self.backup_dir / f"{config_item.key}_{int(config_item.timestamp)}.json"
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"备份配置失败: {str(e)}")
    
    async def rollback_config(self, key: str, target_version: Optional[int] = None) -> bool:
        """回滚配置"""
        try:
            if key not in self.config_history:
                return False
            
            history = list(self.config_history[key])
            
            if target_version is None:
                # 回滚到上一个版本
                if len(history) < 2:
                    return False
                target_change = history[-2]  # 倒数第二个变更
            else:
                # 回滚到指定版本
                target_change = None
                for change in reversed(history):
                    if hasattr(change, 'version') and change.version == target_version:
                        target_change = change
                        break
                
                if not target_change:
                    return False
            
            # 执行回滚
            if target_change.change_type == "delete":
                # 如果目标是删除操作，则删除当前配置
                return await self.delete_config(key, reason="rollback")
            else:
                # 恢复到目标值
                success = await self.set_config(
                    key=key,
                    value=target_change.old_value,
                    source=ConfigSource.AUTO_GENERATED,
                    reason=f"rollback to version {target_version or 'previous'}"
                )
                
                if success:
                    self.stats["rollbacks"] += 1
                
                return success
            
        except Exception as e:
            logger.error(f"回滚配置失败: {str(e)}")
            return False
    
    def register_change_callback(self, config_key: str, callback: Callable):
        """注册配置变更回调"""
        self.change_callbacks[config_key].append(callback)
        logger.info(f"注册配置变更回调: {config_key}")
    
    def register_global_callback(self, callback: Callable):
        """注册全局配置变更回调"""
        self.global_callbacks.append(callback)
        logger.info("注册全局配置变更回调")
    
    async def _trigger_callbacks(self, key: str, old_config: Optional[ConfigItem], new_config: Optional[ConfigItem]):
        """触发配置变更回调"""
        try:
            # 触发特定配置的回调
            for callback in self.change_callbacks.get(key, []):
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(key, old_config, new_config)
                    else:
                        callback(key, old_config, new_config)
                except Exception as e:
                    logger.error(f"配置回调执行失败: {str(e)}")
            
            # 触发全局回调
            for callback in self.global_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(key, old_config, new_config)
                    else:
                        callback(key, old_config, new_config)
                except Exception as e:
                    logger.error(f"全局配置回调执行失败: {str(e)}")
                    
        except Exception as e:
            logger.error(f"触发配置回调失败: {str(e)}")
    
    async def _optimization_loop(self):
        """自动优化循环"""
        while self.is_running:
            try:
                await asyncio.sleep(300)  # 5分钟检查一次
                
                # 获取性能指标（这里需要从其他模块获取）
                performance_metrics = await self._get_performance_metrics()
                
                # 获取优化建议
                suggestions = self.optimizer.suggest_optimizations(self.configs, performance_metrics)
                
                # 应用高置信度的优化建议
                for suggestion in suggestions:
                    if suggestion["confidence"] > 0.8:  # 高置信度自动应用
                        success = await self.set_config(
                            key=suggestion["config_key"],
                            value=suggestion["suggested_value"],
                            source=ConfigSource.AUTO_GENERATED,
                            reason=f"auto_optimization: {suggestion['reason']}"
                        )
                        
                        if success:
                            self.stats["auto_optimizations"] += 1
                            logger.info(f"自动优化配置: {suggestion['config_key']} -> {suggestion['suggested_value']}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"自动优化循环错误: {str(e)}")
    
    async def _get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        # 这里应该从系统监控模块获取实际指标
        # 暂时返回模拟数据
        return {
            "cpu_usage": 45.0,
            "memory_usage": 60.0,
            "response_time": 0.15,
            "data_quality": 0.95
        }
    
    def get_config_summary(self) -> Dict[str, Any]:
        """获取配置摘要"""
        summary = {
            "total_configs": len(self.configs),
            "config_types": {},
            "config_sources": {},
            "recent_changes": []
        }
        
        # 统计配置类型
        for config in self.configs.values():
            config_type = config.config_type.value
            summary["config_types"][config_type] = summary["config_types"].get(config_type, 0) + 1
        
        # 统计配置源
        for config in self.configs.values():
            source = config.source.value
            summary["config_sources"][source] = summary["config_sources"].get(source, 0) + 1
        
        # 最近变更
        all_changes = []
        for changes in self.config_history.values():
            all_changes.extend(changes)
        
        # 按时间排序，取最近10个
        all_changes.sort(key=lambda x: x.timestamp, reverse=True)
        summary["recent_changes"] = [
            {
                "config_key": change.config_key,
                "change_type": change.change_type,
                "timestamp": change.timestamp,
                "source": change.source.value
            }
            for change in all_changes[:10]
        ]
        
        return summary
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "enabled": self.enabled,
            "is_running": self.is_running,
            "watched_files": len(self.watched_files),
            "total_configs": len(self.configs),
            "total_history_entries": sum(len(h) for h in self.config_history.values()),
            **self.stats
        }
    
    async def export_configs(self, file_path: str, config_types: Optional[List[ConfigType]] = None) -> bool:
        """导出配置"""
        try:
            export_data = {}
            
            for key, config in self.configs.items():
                if config_types is None or config.config_type in config_types:
                    export_data[key] = {
                        "value": config.value,
                        "config_type": config.config_type.value,
                        "source": config.source.value,
                        "timestamp": config.timestamp,
                        "version": config.version,
                        "description": config.description,
                        "metadata": config.metadata
                    }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                if file_path.endswith('.yaml'):
                    yaml.dump(export_data, f, default_flow_style=False, allow_unicode=True)
                else:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"配置已导出到: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"导出配置失败: {str(e)}")
            return False
    
    async def import_configs(self, file_path: str, overwrite: bool = False) -> bool:
        """导入配置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.endswith('.yaml'):
                    import_data = yaml.safe_load(f)
                else:
                    import_data = json.load(f)
            
            imported_count = 0
            
            for key, config_data in import_data.items():
                if key in self.configs and not overwrite:
                    logger.warning(f"配置已存在，跳过: {key}")
                    continue
                
                config_type = ConfigType(config_data.get("config_type", "system"))
                
                success = await self.set_config(
                    key=key,
                    value=config_data["value"],
                    config_type=config_type,
                    source=ConfigSource.FILE,
                    reason="import"
                )
                
                if success:
                    imported_count += 1
            
            logger.info(f"成功导入 {imported_count} 个配置项")
            return True
            
        except Exception as e:
            logger.error(f"导入配置失败: {str(e)}")
            return False
    
    async def shutdown(self):
        """关闭配置管理器"""
        logger.info("正在关闭智能配置管理器...")
        
        self.is_running = False
        
        # 停止文件监控
        if self.file_observer.is_alive():
            self.file_observer.stop()
            self.file_observer.join()
        
        # 取消优化任务
        if self._optimization_task:
            self._optimization_task.cancel()
            try:
                await self._optimization_task
            except asyncio.CancelledError:
                pass
        
        logger.info("智能配置管理器已关闭") 