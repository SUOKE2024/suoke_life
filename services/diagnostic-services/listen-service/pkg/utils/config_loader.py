"""
优化的配置加载器模块
支持多环境配置、配置验证、热重载、中医特色配置
"""
import os
import yaml
import json
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import threading
import time

logger = logging.getLogger(__name__)

@dataclass
class ConfigValidationError(Exception):
    """配置验证错误"""
    field: str
    message: str
    value: Any = None

class ConfigValidator:
    """配置验证器"""
    
    @staticmethod
    def validate_server_config(config: Dict[str, Any]) -> List[str]:
        """验证服务器配置"""
        errors = []
        
        server_config = config.get("server", {})
        
        # 验证端口
        port = server_config.get("port")
        if not isinstance(port, int) or port < 1 or port > 65535:
            errors.append("server.port must be an integer between 1 and 65535")
        
        # 验证主机地址
        host = server_config.get("host")
        if not isinstance(host, str) or not host:
            errors.append("server.host must be a non-empty string")
        
        # 验证工作线程数
        max_workers = server_config.get("max_workers")
        if not isinstance(max_workers, int) or max_workers < 1:
            errors.append("server.max_workers must be a positive integer")
        
        return errors
    
    @staticmethod
    def validate_audio_config(config: Dict[str, Any]) -> List[str]:
        """验证音频处理配置"""
        errors = []
        
        audio_config = config.get("audio_processing", {})
        
        # 验证采样率
        sample_rate = audio_config.get("default_sample_rate")
        if not isinstance(sample_rate, int) or sample_rate < 8000:
            errors.append("audio_processing.default_sample_rate must be at least 8000")
        
        # 验证支持的格式
        formats = audio_config.get("supported_formats")
        if not isinstance(formats, list) or not formats:
            errors.append("audio_processing.supported_formats must be a non-empty list")
        
        # 验证文件大小限制
        max_size = audio_config.get("max_file_size")
        if not isinstance(max_size, (int, float)) or max_size <= 0:
            errors.append("audio_processing.max_file_size must be a positive number")
        
        return errors
    
    @staticmethod
    def validate_tcm_config(config: Dict[str, Any]) -> List[str]:
        """验证中医配置"""
        errors = []
        
        tcm_config = config.get("tcm_features", {})
        
        if not tcm_config.get("enabled", True):
            return errors  # 如果未启用，跳过验证
        
        # 验证五脏六腑映射
        organ_mapping = tcm_config.get("organ_sound_mapping", {})
        required_organs = ["heart", "liver", "spleen", "lung", "kidney"]
        for organ in required_organs:
            if organ not in organ_mapping:
                errors.append(f"tcm_features.organ_sound_mapping.{organ} is required")
        
        # 验证五志情绪映射
        emotion_mapping = tcm_config.get("emotion_features", {})
        required_emotions = ["joy", "anger", "worry", "thought", "fear"]
        for emotion in required_emotions:
            if emotion not in emotion_mapping:
                errors.append(f"tcm_features.emotion_features.{emotion} is required")
        
        return errors
    
    @staticmethod
    def validate_database_config(config: Dict[str, Any]) -> List[str]:
        """验证数据库配置"""
        errors = []
        
        db_config = config.get("database", {})
        
        # 验证MongoDB配置
        mongodb_config = db_config.get("mongodb", {})
        if not mongodb_config.get("host"):
            errors.append("database.mongodb.host is required")
        
        port = mongodb_config.get("port")
        if not isinstance(port, int) or port < 1 or port > 65535:
            errors.append("database.mongodb.port must be a valid port number")
        
        return errors
    
    @classmethod
    def validate_config(cls, config: Dict[str, Any]) -> List[str]:
        """验证完整配置"""
        all_errors = []
        
        all_errors.extend(cls.validate_server_config(config))
        all_errors.extend(cls.validate_audio_config(config))
        all_errors.extend(cls.validate_tcm_config(config))
        all_errors.extend(cls.validate_database_config(config))
        
        return all_errors

class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.config = {}
        self.last_modified = None
        self.watchers = []
        self._lock = threading.Lock()
        
        # 默认配置路径
        self.default_paths = [
            "config/config.yaml",
            "config/config_optimized.yaml",
            "config.yaml",
            "config.yml"
        ]
        
        # 环境变量前缀
        self.env_prefix = "LISTEN_SERVICE_"
        
    def _find_config_file(self) -> Optional[Path]:
        """查找配置文件"""
        if self.config_path:
            path = Path(self.config_path)
            if path.exists():
                return path
            else:
                logger.warning(f"指定的配置文件不存在: {self.config_path}")
        
        # 查找默认配置文件
        for default_path in self.default_paths:
            path = Path(default_path)
            if path.exists():
                logger.info(f"找到配置文件: {path}")
                return path
        
        logger.warning("未找到配置文件，将使用默认配置")
        return None
    
    def _load_yaml_file(self, file_path: Path) -> Dict[str, Any]:
        """加载YAML配置文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                logger.info(f"成功加载配置文件: {file_path}")
                return config or {}
        except yaml.YAMLError as e:
            logger.error(f"YAML解析错误: {e}")
            raise
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            raise
    
    def _apply_environment_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """应用环境变量覆盖"""
        for key, value in os.environ.items():
            if key.startswith(self.env_prefix):
                # 移除前缀并转换为配置键
                config_key = key[len(self.env_prefix):].lower()
                
                # 支持嵌套键（用下划线分隔）
                keys = config_key.split('_')
                
                # 尝试转换值类型
                try:
                    # 尝试解析为JSON
                    parsed_value = json.loads(value)
                except json.JSONDecodeError:
                    # 如果不是JSON，保持字符串
                    parsed_value = value
                
                # 设置嵌套配置
                current = config
                for key_part in keys[:-1]:
                    if key_part not in current:
                        current[key_part] = {}
                    current = current[key_part]
                
                current[keys[-1]] = parsed_value
                logger.debug(f"环境变量覆盖: {config_key} = {parsed_value}")
        
        return config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "server": {
                "host": "0.0.0.0",
                "port": 50052,
                "max_workers": 16,
                "max_concurrent_rpcs": 200,
                "enable_reflection": True,
                "grace_period": 10
            },
            "audio_processing": {
                "default_sample_rate": 16000,
                "default_channels": 1,
                "supported_formats": ["wav", "mp3", "flac", "m4a"],
                "max_duration": 600,
                "min_duration": 0.3,
                "max_file_size": 100,
                "chunk_size": 8192,
                "enable_gpu": True,
                "batch_processing": True,
                "cache_enabled": True,
                "max_concurrent_tasks": 8,
                "noise_reduction": True,
                "normalize_volume": True,
                "vad_enabled": True,
                "vad_threshold": 0.3,
                "temp_dir": "/tmp/listen_service"
            },
            "tcm_features": {
                "enabled": True,
                "organ_sound_mapping": {
                    "heart": ["高亢", "急促", "断续"],
                    "liver": ["弦急", "高亢", "怒声"],
                    "spleen": ["低沉", "缓慢", "思虑"],
                    "lung": ["清亮", "悲伤", "短促"],
                    "kidney": ["低沉", "恐惧", "微弱"]
                },
                "emotion_features": {
                    "joy": ["笑声", "高音", "快节奏"],
                    "anger": ["怒吼", "粗糙", "急促"],
                    "worry": ["叹息", "低沉", "缓慢"],
                    "thought": ["沉思", "平稳", "规律"],
                    "fear": ["颤抖", "微弱", "不稳"]
                }
            },
            "database": {
                "mongodb": {
                    "host": "localhost",
                    "port": 27017,
                    "database": "listen_service",
                    "max_pool_size": 50,
                    "min_pool_size": 5
                }
            },
            "cache": {
                "redis": {
                    "host": "localhost",
                    "port": 6379,
                    "db": 0,
                    "max_connections": 50
                }
            },
            "monitoring": {
                "prometheus": {
                    "enabled": True,
                    "host": "0.0.0.0",
                    "port": 9090
                },
                "health_check": {
                    "enabled": True,
                    "interval": 30,
                    "timeout": 10
                },
                "metrics_interval": 30,
                "alert_check_interval": 60,
                "logging": {
                    "level": "INFO",
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    "file": "listen_service.log",
                    "max_size": "100MB",
                    "backup_count": 5
                }
            },
            "development": {
                "debug_mode": False,
                "structured_logging": True,
                "profile_enabled": False
            }
        }
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置"""
        with self._lock:
            # 从默认配置开始
            config = self._get_default_config()
            
            # 查找并加载配置文件
            config_file = self._find_config_file()
            if config_file:
                try:
                    file_config = self._load_yaml_file(config_file)
                    # 深度合并配置
                    config = self._deep_merge(config, file_config)
                    
                    # 记录文件修改时间
                    self.last_modified = config_file.stat().st_mtime
                    self.config_path = str(config_file)
                    
                except Exception as e:
                    logger.error(f"加载配置文件失败，使用默认配置: {e}")
            
            # 应用环境变量覆盖
            config = self._apply_environment_overrides(config)
            
            # 验证配置
            validation_errors = ConfigValidator.validate_config(config)
            if validation_errors:
                logger.error("配置验证失败:")
                for error in validation_errors:
                    logger.error(f"  - {error}")
                raise ConfigValidationError("config", "配置验证失败", validation_errors)
            
            self.config = config
            logger.info("配置加载完成")
            
            # 通知观察者
            self._notify_watchers()
            
            return config
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """深度合并字典"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        if not self.config:
            return self.load_config()
        return self.config
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值（支持点分隔的嵌套键）"""
        config = self.get_config()
        keys = key.split('.')
        
        current = config
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        
        return current
    
    def reload_config(self) -> Dict[str, Any]:
        """重新加载配置"""
        logger.info("重新加载配置...")
        return self.load_config()
    
    def watch_config(self, callback):
        """添加配置变化监听器"""
        self.watchers.append(callback)
    
    def _notify_watchers(self):
        """通知配置变化观察者"""
        for watcher in self.watchers:
            try:
                watcher(self.config)
            except Exception as e:
                logger.error(f"配置变化通知失败: {e}")
    
    def start_file_watcher(self, check_interval: int = 30):
        """启动文件变化监控"""
        if not self.config_path:
            logger.warning("未指定配置文件路径，无法启动文件监控")
            return
        
        def watch_file():
            while True:
                try:
                    if self.config_path and Path(self.config_path).exists():
                        current_mtime = Path(self.config_path).stat().st_mtime
                        if self.last_modified and current_mtime > self.last_modified:
                            logger.info("检测到配置文件变化，重新加载...")
                            self.reload_config()
                    
                    time.sleep(check_interval)
                except Exception as e:
                    logger.error(f"文件监控错误: {e}")
                    time.sleep(check_interval)
        
        watcher_thread = threading.Thread(target=watch_file, daemon=True)
        watcher_thread.start()
        logger.info(f"配置文件监控已启动，检查间隔: {check_interval}秒")

# 全局配置加载器实例
_config_loader = None

def get_config_loader(config_path: Optional[str] = None) -> ConfigLoader:
    """获取全局配置加载器实例"""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader(config_path)
    return _config_loader

def get_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """获取配置（便捷函数）"""
    loader = get_config_loader(config_path)
    return loader.get_config()

def reload_config() -> Dict[str, Any]:
    """重新加载配置（便捷函数）"""
    global _config_loader
    if _config_loader:
        return _config_loader.reload_config()
    else:
        return get_config()

def get_config_value(key: str, default: Any = None) -> Any:
    """获取配置值（便捷函数）"""
    loader = get_config_loader()
    return loader.get(key, default) 