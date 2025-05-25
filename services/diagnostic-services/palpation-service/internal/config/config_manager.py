#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置管理模块
提供配置文件加载、环境变量支持、配置验证、热重载和配置版本管理功能
支持多种配置格式（YAML、JSON、TOML）和配置继承
"""

import os
import json
import logging
import asyncio
import hashlib
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from datetime import datetime
from pathlib import Path
import yaml
import toml
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import jsonschema
from jsonschema import validate, ValidationError
import copy
import threading
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class ConfigFormat(Enum):
    """配置格式枚举"""
    YAML = "yaml"
    JSON = "json"
    TOML = "toml"
    ENV = "env"

class ConfigSource(Enum):
    """配置源枚举"""
    FILE = "file"
    ENVIRONMENT = "environment"
    REMOTE = "remote"
    DATABASE = "database"

@dataclass
class ConfigChange:
    """配置变更记录"""
    path: str
    old_value: Any
    new_value: Any
    timestamp: datetime
    source: str
    user: Optional[str] = None

@dataclass
class ConfigValidationRule:
    """配置验证规则"""
    path: str
    rule_type: str              # required, type, range, regex, custom
    rule_value: Any
    error_message: str = ""

@dataclass
class ConfigProfile:
    """配置档案"""
    name: str
    description: str
    config: Dict[str, Any]
    created_at: datetime
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)

class ConfigFileHandler(FileSystemEventHandler):
    """配置文件监控处理器"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.last_modified = {}
    
    def on_modified(self, event):
        """文件修改事件处理"""
        if event.is_directory:
            return
        
        file_path = event.src_path
        
        # 防止重复触发
        current_time = datetime.now()
        if file_path in self.last_modified:
            if (current_time - self.last_modified[file_path]).total_seconds() < 1:
                return
        
        self.last_modified[file_path] = current_time
        
        # 异步重新加载配置
        asyncio.create_task(self.config_manager._reload_config_file(file_path))

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: str = "config"):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置文件目录
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置存储
        self.config = {}
        self.config_sources = {}
        self.config_history = []
        self.config_profiles = {}
        
        # 验证规则
        self.validation_rules = []
        self.schema = None
        
        # 监控相关
        self.observer = None
        self.file_handler = None
        self.watch_enabled = False
        
        # 回调函数
        self.change_callbacks = []
        
        # 线程安全
        self.lock = threading.RLock()
        
        # 线程池
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # 默认配置
        self._load_default_config()
        
        logger.info("配置管理器初始化完成")
    
    def _load_default_config(self):
        """加载默认配置"""
        default_config = {
            "service": {
                "name": "palpation-service",
                "version": "1.0.0",
                "host": "0.0.0.0",
                "port": 8000,
                "debug": False
            },
            "database": {
                "type": "sqlite",
                "path": "data/palpation.db",
                "pool_size": 10,
                "timeout": 30
            },
            "cache": {
                "enabled": True,
                "type": "memory",
                "max_size": 1000,
                "ttl": 3600
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "logs/palpation.log",
                "max_size": "10MB",
                "backup_count": 5
            },
            "devices": {
                "pulse_sensor": {
                    "enabled": True,
                    "port": "/dev/ttyUSB0",
                    "baudrate": 9600,
                    "timeout": 5
                },
                "pressure_sensor": {
                    "enabled": True,
                    "port": "/dev/ttyUSB1",
                    "baudrate": 9600,
                    "timeout": 5
                }
            },
            "ai": {
                "model_path": "models/tcm_analyzer.pkl",
                "confidence_threshold": 0.8,
                "max_inference_time": 10
            },
            "monitoring": {
                "enabled": True,
                "metrics_interval": 60,
                "alert_thresholds": {
                    "cpu_usage": 80,
                    "memory_usage": 85,
                    "disk_usage": 90
                }
            }
        }
        
        with self.lock:
            self.config = default_config
            self.config_sources = {
                key: ConfigSource.FILE for key in self._flatten_dict(default_config).keys()
            }
    
    def load_config_file(self, file_path: Union[str, Path], merge: bool = True) -> bool:
        """
        加载配置文件
        
        Args:
            file_path: 配置文件路径
            merge: 是否合并到现有配置
            
        Returns:
            是否加载成功
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.warning(f"配置文件不存在: {file_path}")
                return False
            
            # 根据文件扩展名确定格式
            format_map = {
                '.yaml': ConfigFormat.YAML,
                '.yml': ConfigFormat.YAML,
                '.json': ConfigFormat.JSON,
                '.toml': ConfigFormat.TOML
            }
            
            config_format = format_map.get(file_path.suffix.lower())
            if not config_format:
                logger.error(f"不支持的配置文件格式: {file_path.suffix}")
                return False
            
            # 读取配置内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析配置
            if config_format == ConfigFormat.YAML:
                file_config = yaml.safe_load(content)
            elif config_format == ConfigFormat.JSON:
                file_config = json.loads(content)
            elif config_format == ConfigFormat.TOML:
                file_config = toml.loads(content)
            else:
                logger.error(f"未实现的配置格式: {config_format}")
                return False
            
            if file_config is None:
                file_config = {}
            
            # 验证配置
            if not self._validate_config(file_config):
                logger.error(f"配置验证失败: {file_path}")
                return False
            
            # 合并或替换配置
            with self.lock:
                old_config = copy.deepcopy(self.config)
                
                if merge:
                    self._merge_config(self.config, file_config)
                else:
                    self.config = file_config
                
                # 更新配置源
                flat_config = self._flatten_dict(file_config)
                for key in flat_config.keys():
                    self.config_sources[key] = ConfigSource.FILE
                
                # 记录变更
                self._record_config_changes(old_config, self.config, str(file_path))
                
                # 触发回调
                self._trigger_change_callbacks(old_config, self.config)
            
            logger.info(f"配置文件加载成功: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {file_path}, {e}")
            return False
    
    def load_environment_config(self, prefix: str = "PALPATION_") -> bool:
        """
        从环境变量加载配置
        
        Args:
            prefix: 环境变量前缀
            
        Returns:
            是否加载成功
        """
        try:
            env_config = {}
            
            for key, value in os.environ.items():
                if key.startswith(prefix):
                    # 移除前缀并转换为小写
                    config_key = key[len(prefix):].lower()
                    
                    # 将下划线分隔的键转换为嵌套字典
                    keys = config_key.split('_')
                    current = env_config
                    
                    for k in keys[:-1]:
                        if k not in current:
                            current[k] = {}
                        current = current[k]
                    
                    # 尝试转换值类型
                    current[keys[-1]] = self._convert_env_value(value)
            
            if not env_config:
                logger.info("未找到环境变量配置")
                return True
            
            # 验证配置
            if not self._validate_config(env_config):
                logger.error("环境变量配置验证失败")
                return False
            
            # 合并配置
            with self.lock:
                old_config = copy.deepcopy(self.config)
                self._merge_config(self.config, env_config)
                
                # 更新配置源
                flat_config = self._flatten_dict(env_config)
                for key in flat_config.keys():
                    self.config_sources[key] = ConfigSource.ENVIRONMENT
                
                # 记录变更
                self._record_config_changes(old_config, self.config, "environment")
                
                # 触发回调
                self._trigger_change_callbacks(old_config, self.config)
            
            logger.info(f"环境变量配置加载成功，共 {len(env_config)} 项")
            return True
            
        except Exception as e:
            logger.error(f"加载环境变量配置失败: {e}")
            return False
    
    def _convert_env_value(self, value: str) -> Any:
        """转换环境变量值类型"""
        # 布尔值
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # 整数
        try:
            return int(value)
        except ValueError:
            pass
        
        # 浮点数
        try:
            return float(value)
        except ValueError:
            pass
        
        # JSON
        if value.startswith(('{', '[', '"')):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass
        
        # 字符串
        return value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点分隔的嵌套键
            default: 默认值
            
        Returns:
            配置值
        """
        with self.lock:
            try:
                keys = key.split('.')
                value = self.config
                
                for k in keys:
                    if isinstance(value, dict) and k in value:
                        value = value[k]
                    else:
                        return default
                
                return value
                
            except Exception as e:
                logger.error(f"获取配置失败: {key}, {e}")
                return default
    
    def set(self, key: str, value: Any, source: str = "manual") -> bool:
        """
        设置配置值
        
        Args:
            key: 配置键
            value: 配置值
            source: 配置源
            
        Returns:
            是否设置成功
        """
        try:
            with self.lock:
                old_config = copy.deepcopy(self.config)
                
                # 设置值
                keys = key.split('.')
                current = self.config
                
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
                
                current[keys[-1]] = value
                
                # 更新配置源
                self.config_sources[key] = ConfigSource.FILE
                
                # 验证配置
                if not self._validate_config(self.config):
                    # 回滚
                    self.config = old_config
                    logger.error(f"配置验证失败，已回滚: {key}")
                    return False
                
                # 记录变更
                self._record_config_changes(old_config, self.config, source)
                
                # 触发回调
                self._trigger_change_callbacks(old_config, self.config)
            
            logger.info(f"配置设置成功: {key} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"设置配置失败: {key}, {e}")
            return False
    
    def delete(self, key: str, source: str = "manual") -> bool:
        """
        删除配置项
        
        Args:
            key: 配置键
            source: 配置源
            
        Returns:
            是否删除成功
        """
        try:
            with self.lock:
                old_config = copy.deepcopy(self.config)
                
                # 删除值
                keys = key.split('.')
                current = self.config
                
                for k in keys[:-1]:
                    if k not in current:
                        return False
                    current = current[k]
                
                if keys[-1] not in current:
                    return False
                
                del current[keys[-1]]
                
                # 删除配置源记录
                self.config_sources.pop(key, None)
                
                # 记录变更
                self._record_config_changes(old_config, self.config, source)
                
                # 触发回调
                self._trigger_change_callbacks(old_config, self.config)
            
            logger.info(f"配置删除成功: {key}")
            return True
            
        except Exception as e:
            logger.error(f"删除配置失败: {key}, {e}")
            return False
    
    def save_config_file(self, file_path: Union[str, Path], format: ConfigFormat = ConfigFormat.YAML) -> bool:
        """
        保存配置到文件
        
        Args:
            file_path: 文件路径
            format: 配置格式
            
        Returns:
            是否保存成功
        """
        try:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with self.lock:
                config_copy = copy.deepcopy(self.config)
            
            # 根据格式保存
            with open(file_path, 'w', encoding='utf-8') as f:
                if format == ConfigFormat.YAML:
                    yaml.dump(config_copy, f, default_flow_style=False, allow_unicode=True)
                elif format == ConfigFormat.JSON:
                    json.dump(config_copy, f, indent=2, ensure_ascii=False)
                elif format == ConfigFormat.TOML:
                    toml.dump(config_copy, f)
                else:
                    logger.error(f"不支持的保存格式: {format}")
                    return False
            
            logger.info(f"配置保存成功: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存配置失败: {file_path}, {e}")
            return False
    
    def add_validation_rule(self, rule: ConfigValidationRule):
        """添加验证规则"""
        self.validation_rules.append(rule)
    
    def set_schema(self, schema: Dict[str, Any]):
        """设置JSON Schema"""
        self.schema = schema
    
    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置"""
        try:
            # JSON Schema验证
            if self.schema:
                validate(instance=config, schema=self.schema)
            
            # 自定义规则验证
            for rule in self.validation_rules:
                if not self._validate_rule(config, rule):
                    logger.error(f"配置验证失败: {rule.path}, {rule.error_message}")
                    return False
            
            return True
            
        except ValidationError as e:
            logger.error(f"配置Schema验证失败: {e.message}")
            return False
        except Exception as e:
            logger.error(f"配置验证错误: {e}")
            return False
    
    def _validate_rule(self, config: Dict[str, Any], rule: ConfigValidationRule) -> bool:
        """验证单个规则"""
        try:
            value = self._get_nested_value(config, rule.path)
            
            if rule.rule_type == "required":
                return value is not None
            elif rule.rule_type == "type":
                return isinstance(value, rule.rule_value)
            elif rule.rule_type == "range":
                min_val, max_val = rule.rule_value
                return min_val <= value <= max_val
            elif rule.rule_type == "regex":
                import re
                return re.match(rule.rule_value, str(value)) is not None
            elif rule.rule_type == "custom":
                return rule.rule_value(value)
            
            return True
            
        except Exception:
            return False
    
    def _get_nested_value(self, config: Dict[str, Any], path: str) -> Any:
        """获取嵌套值"""
        keys = path.split('.')
        value = config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value
    
    def _merge_config(self, target: Dict[str, Any], source: Dict[str, Any]):
        """合并配置"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_config(target[key], value)
            else:
                target[key] = value
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """扁平化字典"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    def _record_config_changes(self, old_config: Dict[str, Any], new_config: Dict[str, Any], source: str):
        """记录配置变更"""
        old_flat = self._flatten_dict(old_config)
        new_flat = self._flatten_dict(new_config)
        
        # 找出变更
        all_keys = set(old_flat.keys()) | set(new_flat.keys())
        
        for key in all_keys:
            old_value = old_flat.get(key)
            new_value = new_flat.get(key)
            
            if old_value != new_value:
                change = ConfigChange(
                    path=key,
                    old_value=old_value,
                    new_value=new_value,
                    timestamp=datetime.now(),
                    source=source
                )
                
                self.config_history.append(change)
                
                # 限制历史记录数量
                if len(self.config_history) > 1000:
                    self.config_history = self.config_history[-500:]
    
    def _trigger_change_callbacks(self, old_config: Dict[str, Any], new_config: Dict[str, Any]):
        """触发变更回调"""
        for callback in self.change_callbacks:
            try:
                callback(old_config, new_config)
            except Exception as e:
                logger.error(f"配置变更回调错误: {e}")
    
    def add_change_callback(self, callback: Callable[[Dict[str, Any], Dict[str, Any]], None]):
        """添加配置变更回调"""
        self.change_callbacks.append(callback)
    
    def remove_change_callback(self, callback: Callable[[Dict[str, Any], Dict[str, Any]], None]):
        """移除配置变更回调"""
        if callback in self.change_callbacks:
            self.change_callbacks.remove(callback)
    
    def enable_file_watching(self, watch_patterns: List[str] = None):
        """启用文件监控"""
        if self.watch_enabled:
            return
        
        try:
            if watch_patterns is None:
                watch_patterns = ["*.yaml", "*.yml", "*.json", "*.toml"]
            
            self.file_handler = ConfigFileHandler(self)
            self.observer = Observer()
            
            # 监控配置目录
            self.observer.schedule(
                self.file_handler,
                str(self.config_dir),
                recursive=True
            )
            
            self.observer.start()
            self.watch_enabled = True
            
            logger.info("配置文件监控已启用")
            
        except Exception as e:
            logger.error(f"启用文件监控失败: {e}")
    
    def disable_file_watching(self):
        """禁用文件监控"""
        if not self.watch_enabled:
            return
        
        try:
            if self.observer:
                self.observer.stop()
                self.observer.join()
                self.observer = None
            
            self.file_handler = None
            self.watch_enabled = False
            
            logger.info("配置文件监控已禁用")
            
        except Exception as e:
            logger.error(f"禁用文件监控失败: {e}")
    
    async def _reload_config_file(self, file_path: str):
        """重新加载配置文件"""
        try:
            logger.info(f"检测到配置文件变更，重新加载: {file_path}")
            
            # 延迟一点时间，确保文件写入完成
            await asyncio.sleep(0.5)
            
            success = self.load_config_file(file_path, merge=True)
            if success:
                logger.info(f"配置文件重新加载成功: {file_path}")
            else:
                logger.error(f"配置文件重新加载失败: {file_path}")
                
        except Exception as e:
            logger.error(f"重新加载配置文件错误: {file_path}, {e}")
    
    def create_profile(self, name: str, description: str = "", tags: List[str] = None) -> bool:
        """
        创建配置档案
        
        Args:
            name: 档案名称
            description: 档案描述
            tags: 标签列表
            
        Returns:
            是否创建成功
        """
        try:
            if tags is None:
                tags = []
            
            with self.lock:
                profile = ConfigProfile(
                    name=name,
                    description=description,
                    config=copy.deepcopy(self.config),
                    created_at=datetime.now(),
                    tags=tags
                )
                
                self.config_profiles[name] = profile
            
            logger.info(f"配置档案创建成功: {name}")
            return True
            
        except Exception as e:
            logger.error(f"创建配置档案失败: {name}, {e}")
            return False
    
    def load_profile(self, name: str) -> bool:
        """
        加载配置档案
        
        Args:
            name: 档案名称
            
        Returns:
            是否加载成功
        """
        try:
            if name not in self.config_profiles:
                logger.error(f"配置档案不存在: {name}")
                return False
            
            profile = self.config_profiles[name]
            
            with self.lock:
                old_config = copy.deepcopy(self.config)
                self.config = copy.deepcopy(profile.config)
                
                # 记录变更
                self._record_config_changes(old_config, self.config, f"profile:{name}")
                
                # 触发回调
                self._trigger_change_callbacks(old_config, self.config)
            
            logger.info(f"配置档案加载成功: {name}")
            return True
            
        except Exception as e:
            logger.error(f"加载配置档案失败: {name}, {e}")
            return False
    
    def delete_profile(self, name: str) -> bool:
        """
        删除配置档案
        
        Args:
            name: 档案名称
            
        Returns:
            是否删除成功
        """
        try:
            if name not in self.config_profiles:
                logger.error(f"配置档案不存在: {name}")
                return False
            
            del self.config_profiles[name]
            
            logger.info(f"配置档案删除成功: {name}")
            return True
            
        except Exception as e:
            logger.error(f"删除配置档案失败: {name}, {e}")
            return False
    
    def list_profiles(self) -> List[ConfigProfile]:
        """列出所有配置档案"""
        with self.lock:
            return list(self.config_profiles.values())
    
    def get_config_history(self, limit: int = 100) -> List[ConfigChange]:
        """获取配置变更历史"""
        with self.lock:
            return self.config_history[-limit:]
    
    def get_config_sources(self) -> Dict[str, ConfigSource]:
        """获取配置源信息"""
        with self.lock:
            return self.config_sources.copy()
    
    def export_config(self, include_sources: bool = False) -> Dict[str, Any]:
        """
        导出配置
        
        Args:
            include_sources: 是否包含配置源信息
            
        Returns:
            配置字典
        """
        with self.lock:
            result = {
                'config': copy.deepcopy(self.config),
                'timestamp': datetime.now().isoformat(),
                'version': self.get('service.version', '1.0.0')
            }
            
            if include_sources:
                result['sources'] = {
                    key: source.value for key, source in self.config_sources.items()
                }
            
            return result
    
    def import_config(self, config_data: Dict[str, Any], merge: bool = True) -> bool:
        """
        导入配置
        
        Args:
            config_data: 配置数据
            merge: 是否合并
            
        Returns:
            是否导入成功
        """
        try:
            if 'config' not in config_data:
                logger.error("导入数据中缺少config字段")
                return False
            
            import_config = config_data['config']
            
            # 验证配置
            if not self._validate_config(import_config):
                logger.error("导入配置验证失败")
                return False
            
            with self.lock:
                old_config = copy.deepcopy(self.config)
                
                if merge:
                    self._merge_config(self.config, import_config)
                else:
                    self.config = import_config
                
                # 记录变更
                self._record_config_changes(old_config, self.config, "import")
                
                # 触发回调
                self._trigger_change_callbacks(old_config, self.config)
            
            logger.info("配置导入成功")
            return True
            
        except Exception as e:
            logger.error(f"导入配置失败: {e}")
            return False
    
    def get_config_hash(self) -> str:
        """获取配置哈希值"""
        with self.lock:
            config_str = json.dumps(self.config, sort_keys=True)
            return hashlib.md5(config_str.encode()).hexdigest()
    
    def reload_all_configs(self) -> bool:
        """重新加载所有配置"""
        try:
            # 重新加载默认配置
            self._load_default_config()
            
            # 重新加载配置文件
            config_files = []
            for pattern in ["*.yaml", "*.yml", "*.json", "*.toml"]:
                config_files.extend(self.config_dir.glob(pattern))
            
            for config_file in config_files:
                self.load_config_file(config_file, merge=True)
            
            # 重新加载环境变量
            self.load_environment_config()
            
            logger.info("所有配置重新加载完成")
            return True
            
        except Exception as e:
            logger.error(f"重新加载配置失败: {e}")
            return False
    
    def cleanup(self):
        """清理资源"""
        # 禁用文件监控
        self.disable_file_watching()
        
        # 关闭线程池
        self.executor.shutdown(wait=True)
        
        # 清理回调
        self.change_callbacks.clear()
        
        logger.info("配置管理器资源清理完成") 