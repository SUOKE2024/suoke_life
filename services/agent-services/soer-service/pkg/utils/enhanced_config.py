"""
增强的配置管理系统
支持环境变量替换、配置验证、热重载等功能
"""
import os
import yaml
import json
import logging
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
from pydantic import BaseModel, Field, field_validator
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import asyncio
from threading import Lock

logger = logging.getLogger(__name__)

class DatabaseConfig(BaseModel):
    """数据库配置"""
    type: str = "postgresql"
    host: str = "localhost"
    port: int = 5432
    name: str
    user: str
    password: str
    pool_size: int = 10
    timeout: int = 30
    
    @field_validator('port')
    @classmethod
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError('端口号必须在1-65535之间')
        return v

class CacheConfig(BaseModel):
    """缓存配置"""
    type: str = "redis"
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    ttl: int = 300
    
    @field_validator('port')
    @classmethod
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError('端口号必须在1-65535之间')
        return v

class GrpcConfig(BaseModel):
    """gRPC配置"""
    port: int = 50054
    max_workers: int = 10
    max_message_length: int = 104857600
    enable_reflection: bool = True
    
    @field_validator('max_workers')
    @classmethod
    def validate_max_workers(cls, v):
        if v < 1:
            raise ValueError('最大工作线程数必须大于0')
        return v

class RestConfig(BaseModel):
    """REST API配置"""
    port: int = 8054
    cors_origins: List[str] = ["*"]
    api_prefix: str = "/api/v1"
    
    @field_validator('port')
    @classmethod
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError('端口号必须在1-65535之间')
        return v

class ModelConfig(BaseModel):
    """模型配置"""
    primary_model: str = "gpt-4o-mini"
    fallback_model: str = "llama-3-8b"
    api_base: Optional[str] = None
    api_key: Optional[str] = None
    timeout: int = 60
    max_tokens: int = 4096
    top_p: float = 0.9
    temperature: float = 0.7
    
    @field_validator('timeout')
    @classmethod
    def validate_timeout(cls, v):
        if v < 1:
            raise ValueError('超时时间必须大于0')
        return v
    
    @field_validator('top_p')
    @classmethod
    def validate_top_p(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('top_p必须在0-1之间')
        return v
    
    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v):
        if not 0 <= v <= 2:
            raise ValueError('temperature必须在0-2之间')
        return v

class ServiceConfig(BaseModel):
    """服务配置"""
    name: str = "soer-service"
    version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False

class LoggingConfig(BaseModel):
    """日志配置"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = None
    rotate: bool = True
    max_size: int = 100
    backups: int = 5

class MetricsConfig(BaseModel):
    """指标配置"""
    enabled: bool = True
    type: str = "prometheus"
    port: int = 9098
    path: str = "/metrics"

class TracingConfig(BaseModel):
    """追踪配置"""
    enabled: bool = True
    type: str = "jaeger"
    service_name: str = "soer-service"
    host: str = "jaeger"
    port: int = 6831

class ConversationConfig(BaseModel):
    """会话配置"""
    system_prompt: str = ""
    max_history_turns: int = 20
    idle_timeout: int = 1800

class SoerServiceConfig(BaseModel):
    """索儿服务完整配置"""
    service: ServiceConfig = ServiceConfig()
    database: DatabaseConfig
    cache: CacheConfig = CacheConfig()
    grpc: GrpcConfig = GrpcConfig()
    rest: RestConfig = RestConfig()
    models: Dict[str, ModelConfig] = {"llm": ModelConfig()}
    logging: LoggingConfig = LoggingConfig()
    metrics: MetricsConfig = MetricsConfig()
    tracing: TracingConfig = TracingConfig()
    conversation: ConversationConfig = ConversationConfig()

class ConfigFileHandler(FileSystemEventHandler):
    """配置文件变更处理器"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
    
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(('.yaml', '.yml')):
            logger.info(f"配置文件变更: {event.src_path}")
            asyncio.create_task(self.config_manager.reload_config())

class EnhancedConfigManager:
    """增强的配置管理器"""
    
    def __init__(self, config_path: str, watch_changes: bool = False):
        self.config_path = Path(config_path)
        self.watch_changes = watch_changes
        self._config: Optional[SoerServiceConfig] = None
        self._lock = Lock()
        self._observer: Optional[Observer] = None
        self._change_callbacks: List[callable] = []
    
    def add_change_callback(self, callback: callable) -> None:
        """添加配置变更回调"""
        self._change_callbacks.append(callback)
    
    def _substitute_env_vars(self, data: Any) -> Any:
        """递归替换环境变量"""
        if isinstance(data, dict):
            return {k: self._substitute_env_vars(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._substitute_env_vars(item) for item in data]
        elif isinstance(data, str):
            # 替换 ${VAR_NAME} 格式的环境变量
            if data.startswith('${') and data.endswith('}'):
                var_name = data[2:-1]
                return os.getenv(var_name, data)
            return data
        else:
            return data
    
    def load_config(self) -> SoerServiceConfig:
        """加载配置"""
        with self._lock:
            try:
                if not self.config_path.exists():
                    raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
                
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    raw_data = yaml.safe_load(f)
                
                # 替换环境变量
                processed_data = self._substitute_env_vars(raw_data)
                
                # 验证配置
                self._config = SoerServiceConfig(**processed_data)
                
                logger.info(f"配置加载成功: {self.config_path}")
                return self._config
                
            except Exception as e:
                logger.error(f"配置加载失败: {e}")
                raise
    
    async def reload_config(self) -> None:
        """重新加载配置"""
        try:
            old_config = self._config
            new_config = self.load_config()
            
            # 通知配置变更
            for callback in self._change_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(old_config, new_config)
                    else:
                        callback(old_config, new_config)
                except Exception as e:
                    logger.error(f"配置变更回调执行失败: {e}")
            
            logger.info("配置重新加载完成")
            
        except Exception as e:
            logger.error(f"配置重新加载失败: {e}")
    
    def start_watching(self) -> None:
        """开始监控配置文件变更"""
        if not self.watch_changes or self._observer:
            return
        
        self._observer = Observer()
        handler = ConfigFileHandler(self)
        self._observer.schedule(handler, str(self.config_path.parent), recursive=False)
        self._observer.start()
        logger.info(f"开始监控配置文件变更: {self.config_path.parent}")
    
    def stop_watching(self) -> None:
        """停止监控配置文件变更"""
        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._observer = None
            logger.info("停止监控配置文件变更")
    
    def get_config(self) -> SoerServiceConfig:
        """获取当前配置"""
        if self._config is None:
            self.load_config()
        return self._config
    
    def get_section(self, section: str) -> Any:
        """获取配置节"""
        config = self.get_config()
        return getattr(config, section, None)
    
    def __enter__(self):
        self.load_config()
        self.start_watching()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_watching()

# 全局配置管理器实例
_config_manager: Optional[EnhancedConfigManager] = None

def setup_config_manager(config_path: str, watch_changes: bool = False) -> EnhancedConfigManager:
    """设置全局配置管理器"""
    global _config_manager
    _config_manager = EnhancedConfigManager(config_path, watch_changes)
    return _config_manager

def get_config_manager() -> EnhancedConfigManager:
    """获取全局配置管理器"""
    if _config_manager is None:
        raise RuntimeError("配置管理器未初始化，请先调用 setup_config_manager")
    return _config_manager

def get_config() -> SoerServiceConfig:
    """获取当前配置"""
    return get_config_manager().get_config()

def get_config_section(section: str) -> Any:
    """获取配置节"""
    return get_config_manager().get_section(section) 