"""
settings - 索克生活项目模块
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any, List
import json
import logging
import os
import yaml

"""
配置管理系统

支持环境变量、配置文件、动态配置等多种配置方式，
提供类型安全的配置访问和验证。
"""


logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """数据库配置"""
    host: str = "localhost"
    port: int = 5432
    database: str = "suoke_diagnosis"
    username: str = "postgres"
    password: str = ""
    echo_sql: bool = False
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600

@dataclass
class RedisConfig:
    """Redis配置"""
    host: str = "localhost"
    port: int = 6379
    password: str = ""
    database: int = 0
    max_connections: int = 20
    socket_timeout: int = 5
    socket_connect_timeout: int = 5

@dataclass
class AIModelConfig:
    """AI模型配置"""
    model_path: str = "/models"
    device: str = "cpu"  # cpu, cuda, mps
    batch_size: int = 1
    max_sequence_length: int = 512
    confidence_threshold: float = 0.7
    enable_gpu: bool = False
    model_cache_size: int = 3

@dataclass
class VisionConfig:
    """视觉分析配置"""
    face_model_path: str = "/models/face_analysis.onnx"
    tongue_model_path: str = "/models/tongue_analysis.onnx"
    eye_model_path: str = "/models/eye_analysis.onnx"
    image_size: tuple = (224, 224)
    preprocessing_enabled: bool = True
    augmentation_enabled: bool = False
    confidence_threshold: float = 0.75

@dataclass
class AudioConfig:
    """音频分析配置"""
    voice_model_path: str = "/models/voice_analysis.onnx"
    breathing_model_path: str = "/models/breathing_analysis.onnx"
    sample_rate: int = 16000
    chunk_size: int = 1024
    max_duration: int = 300  # 秒
    noise_reduction: bool = True
    confidence_threshold: float = 0.7

@dataclass
class NLPConfig:
    """自然语言处理配置"""
    model_name: str = "bert-base-chinese"
    tokenizer_path: str = "/models/tokenizer"
    max_length: int = 512
    batch_size: int = 8
    enable_cache: bool = True
    cache_size: int = 1000

@dataclass
class SensorConfig:
    """传感器配置"""
    pulse_sensor_port: str = "/dev/ttyUSB0"
    pressure_sensor_port: str = "/dev/ttyUSB1"
    sampling_rate: int = 1000  # Hz
    buffer_size: int = 10000
    calibration_enabled: bool = True
    noise_filter: bool = True

@dataclass
class SecurityConfig:
    """安全配置"""
    secret_key: str = "your-secret-key-here"
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600  # 秒
    password_min_length: int = 8
    max_login_attempts: int = 5
    session_timeout: int = 1800  # 秒
    enable_encryption: bool = True

@dataclass
class LoggingConfig:
    """日志配置"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str = "/logs/diagnosis.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_console: bool = True
    enable_file: bool = True

@dataclass
class MonitoringConfig:
    """监控配置"""
    enable_metrics: bool = True
    metrics_port: int = 9090
    health_check_interval: int = 30  # 秒
    performance_sampling_rate: float = 0.1
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "cpu_usage": 80.0,
        "memory_usage": 85.0,
        "response_time": 5.0,
        "error_rate": 0.05
    })

@dataclass
class CacheConfig:
    """缓存配置"""
    default_ttl: int = 3600  # 秒
    max_size: int = 10000
    cleanup_interval: int = 300  # 秒
    enable_compression: bool = True
    compression_threshold: int = 1024  # 字节

@dataclass
class APIConfig:
    """API配置"""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    timeout: int = 30
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    rate_limit: int = 100  # 每分钟请求数

@dataclass
class DiagnosisConfig:
    """诊断配置"""
    enable_comprehensive_diagnosis: bool = True
    min_confidence_score: float = 0.6
    max_session_duration: int = 3600  # 秒
    auto_save_interval: int = 300  # 秒
    enable_ai_assistance: bool = True
    syndrome_patterns: List[str] = field(default_factory=lambda: [
        "气虚证", "血虚证", "阴虚证", "阳虚证", 
        "气滞证", "血瘀证", "痰湿证"
    ])

@dataclass
class Settings:
    """主配置类"""
    # 环境配置
    environment: str = "development"
    debug: bool = False
    testing: bool = False
    
    # 服务配置
    service_name: str = "diagnostic-services"
    service_version: str = "1.0.0"
    
    # 子配置
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    ai_model: AIModelConfig = field(default_factory=AIModelConfig)
    vision: VisionConfig = field(default_factory=VisionConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    nlp: NLPConfig = field(default_factory=NLPConfig)
    sensor: SensorConfig = field(default_factory=SensorConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    api: APIConfig = field(default_factory=APIConfig)
    diagnosis: DiagnosisConfig = field(default_factory=DiagnosisConfig)
    
    def __post_init__(self):
        """初始化后处理"""
        self._load_from_environment()
        self._load_from_file()
        self._validate_config()
    
    def _load_from_environment(self):
        """从环境变量加载配置"""
        # 基础配置
        self.environment = os.getenv("ENVIRONMENT", self.environment)
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.testing = os.getenv("TESTING", "false").lower() == "true"
        
        # 数据库配置
        self.database.host = os.getenv("DB_HOST", self.database.host)
        self.database.port = int(os.getenv("DB_PORT", self.database.port))
        self.database.database = os.getenv("DB_NAME", self.database.database)
        self.database.username = os.getenv("DB_USER", self.database.username)
        self.database.password = os.getenv("DB_PASSWORD", self.database.password)
        
        # Redis配置
        self.redis.host = os.getenv("REDIS_HOST", self.redis.host)
        self.redis.port = int(os.getenv("REDIS_PORT", self.redis.port))
        self.redis.password = os.getenv("REDIS_PASSWORD", self.redis.password)
        
        # API配置
        self.api.host = os.getenv("API_HOST", self.api.host)
        self.api.port = int(os.getenv("API_PORT", self.api.port))
        
        # 安全配置
        self.security.secret_key = os.getenv("SECRET_KEY", self.security.secret_key)
        
        # AI模型配置
        self.ai_model.device = os.getenv("AI_DEVICE", self.ai_model.device)
        self.ai_model.model_path = os.getenv("MODEL_PATH", self.ai_model.model_path)
    
    def _load_from_file(self):
        """从配置文件加载配置"""
        config_files = [
            "config.yaml",
            "config.yml", 
            "config.json",
            f"config.{self.environment}.yaml",
            f"config.{self.environment}.yml",
            f"config.{self.environment}.json"
        ]
        
        for config_file in config_files:
            config_path = Path(config_file)
            if config_path.exists():
                try:
                    self._load_config_file(config_path)
                    logger.info(f"已加载配置文件: {config_file}")
                    break
                except Exception as e:
                    logger.warning(f"加载配置文件失败 {config_file}: {e}")
    
    def _load_config_file(self, config_path: Path):
        """加载具体的配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            if config_path.suffix in ['.yaml', '.yml']:
                config_data = yaml.safe_load(f)
            elif config_path.suffix == '.json':
                config_data = json.load(f)
            else:
                return
        
        # 递归更新配置
        self._update_config(config_data)
    
    def _update_config(self, config_data: Dict[str, Any], prefix: str = ""):
        """递归更新配置"""
        for key, value in config_data.items():
            if isinstance(value, dict):
                # 处理嵌套配置
                if hasattr(self, key):
                    sub_config = getattr(self, key)
                    if hasattr(sub_config, '__dict__'):
                        for sub_key, sub_value in value.items():
                            if hasattr(sub_config, sub_key):
                                setattr(sub_config, sub_key, sub_value)
            else:
                # 处理简单配置
                if hasattr(self, key):
                    setattr(self, key, value)
    
    def _validate_config(self):
        """验证配置"""
        # 验证必需的配置
        required_configs = [
            (self.database.host, "数据库主机"),
            (self.database.database, "数据库名称"),
            (self.database.username, "数据库用户名"),
            (self.security.secret_key, "安全密钥")
        ]
        
        for config_value, config_name in required_configs:
            if not config_value:
                raise ValueError(f"缺少必需的配置: {config_name}")
        
        # 验证端口范围
        if not (1 <= self.database.port <= 65535):
            raise ValueError(f"数据库端口无效: {self.database.port}")
        
        if not (1 <= self.redis.port <= 65535):
            raise ValueError(f"Redis端口无效: {self.redis.port}")
        
        if not (1 <= self.api.port <= 65535):
            raise ValueError(f"API端口无效: {self.api.port}")
        
        # 验证阈值范围
        if not (0.0 <= self.diagnosis.min_confidence_score <= 1.0):
            raise ValueError(f"置信度阈值无效: {self.diagnosis.min_confidence_score}")
        
        # 验证路径
        model_path = Path(self.ai_model.model_path)
        if not model_path.exists():
            logger.warning(f"模型路径不存在: {self.ai_model.model_path}")
    
    def get_database_url(self) -> str:
        """获取数据库连接URL"""
        return (
            f"postgresql://{self.database.username}:{self.database.password}"
            f"@{self.database.host}:{self.database.port}/{self.database.database}"
        )
    
    def get_redis_url(self) -> str:
        """获取Redis连接URL"""
        auth_part = f":{self.redis.password}@" if self.redis.password else ""
        return f"redis://{auth_part}{self.redis.host}:{self.redis.port}/{self.redis.database}"
    
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.environment.lower() == "production"
    
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.environment.lower() == "development"
    
    def is_testing(self) -> bool:
        """是否为测试环境"""
        return self.testing or self.environment.lower() == "testing"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {}
        for key, value in self.__dict__.items():
            if hasattr(value, '__dict__'):
                result[key] = value.__dict__
            else:
                result[key] = value
        return result
    
    def save_to_file(self, file_path: str):
        """保存配置到文件"""
        config_data = self.to_dict()
        
        file_path = Path(file_path)
        with open(file_path, 'w', encoding='utf-8') as f:
            if file_path.suffix in ['.yaml', '.yml']:
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
            elif file_path.suffix == '.json':
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            else:
                raise ValueError(f"不支持的文件格式: {file_path.suffix}")

class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self._settings = None
        self._watchers = []
    
    def get_settings(self) -> Settings:
        """获取配置实例"""
        if self._settings is None:
            self._settings = Settings()
        return self._settings
    
    def reload_settings(self):
        """重新加载配置"""
        self._settings = Settings()
        self._notify_watchers()
    
    def add_watcher(self, callback):
        """添加配置变更监听器"""
        self._watchers.append(callback)
    
    def remove_watcher(self, callback):
        """移除配置变更监听器"""
        if callback in self._watchers:
            self._watchers.remove(callback)
    
    def _notify_watchers(self):
        """通知配置变更监听器"""
        for watcher in self._watchers:
            try:
                watcher(self._settings)
            except Exception as e:
                logger.error(f"配置变更通知失败: {e}")
    
    def update_config(self, config_path: str, config_data: Dict[str, Any]):
        """动态更新配置"""
        try:
            # 解析配置路径
            path_parts = config_path.split('.')
            current = self._settings
            
            # 导航到目标配置对象
            for part in path_parts[:-1]:
                current = getattr(current, part)
            
            # 更新配置值
            setattr(current, path_parts[-1], config_data)
            
            # 通知监听器
            self._notify_watchers()
            
            logger.info(f"配置已更新: {config_path}")
            
        except Exception as e:
            logger.error(f"配置更新失败: {e}")
            raise
    
    def get_config_value(self, config_path: str, default: Any = None) -> Any:
        """获取配置值"""
        try:
            path_parts = config_path.split('.')
            current = self._settings
            
            for part in path_parts:
                current = getattr(current, part)
            
            return current
            
        except AttributeError:
            return default

# 全局配置管理器实例
_config_manager = ConfigManager()

def get_settings() -> Settings:
    """获取全局配置实例"""
    return _config_manager.get_settings()

def get_config_manager() -> ConfigManager:
    """获取配置管理器实例"""
    return _config_manager

def reload_config():
    """重新加载配置"""
    _config_manager.reload_settings()

# 配置验证装饰器
def validate_config(config_class):
    """配置验证装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            settings = get_settings()
            # 这里可以添加具体的验证逻辑
            return func(*args, **kwargs)
        return wrapper
    return decorator 