"""
settings - 索克生活项目模块
"""

    from pydantic import BaseModel, Field, validator
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import json
import logging
import os
import yaml

"""
消息总线服务配置模块

提供配置加载、验证和访问功能
"""


# 尝试导入pydantic，如果没有则使用基本的字典配置
try:
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    BaseModel = object
    Field = lambda *args, **kwargs: None  # 空函数

logger = logging.getLogger(__name__)

# 配置路径
CONFIG_DIR = Path(__file__).parent
DEFAULT_CONFIG_PATH = CONFIG_DIR / "default.yaml"
ENV_CONFIG_PATH_VAR = "CONFIG_PATH"
ENV_VAR_PREFIX = "MB_"  # 环境变量前缀，例如MB_KAFKA_BOOTSTRAP_SERVERS

if PYDANTIC_AVAILABLE:
    class LoggingConfig(BaseModel):
        """日志配置"""
        level: str = "INFO"
        format: str = "standard"  # standard或json
        log_file: Optional[str] = None

    class ServerConfig(BaseModel):
        """服务器配置"""
        host: str = "0.0.0.0"
        port: int = 50051
        max_workers: int = 10
        
    class KafkaConfig(BaseModel):
        """Kafka配置"""
        bootstrap_servers: List[str]
        security_protocol: str = "PLAINTEXT"
        sasl_mechanism: Optional[str] = None
        sasl_plain_username: Optional[str] = None
        sasl_plain_password: Optional[str] = None
        
    class RedisConfig(BaseModel):
        """Redis配置"""
        host: str = "localhost"
        port: int = 6379
        db: int = 0
        password: Optional[str] = None
        ssl: bool = False
        
    class MetricsConfig(BaseModel):
        """指标配置"""
        enabled: bool = True
        port: int = 9090
        
    class Settings(BaseModel):
        """应用程序配置"""
        environment: str = "development"
        debug: bool = False
        enable_auth: bool = False
        max_message_size_bytes: int = 4 * 1024 * 1024  # 4MB
        
        server: ServerConfig
        kafka: KafkaConfig
        redis: Optional[RedisConfig] = None
        metrics: MetricsConfig
        logging: LoggingConfig
        
        class Config:
            """Pydantic配置"""
            env_prefix = ENV_VAR_PREFIX
            
        @validator("environment")
        def validate_environment(cls, v):
            """验证环境名称"""
            allowed = ["development", "testing", "staging", "production"]
            if v not in allowed:
                raise ValueError(f"环境必须是以下之一: {', '.join(allowed)}")
            return 
    class Meta:
        # 性能优化: 添加常用查询字段的索引
        indexes = [
            # 根据实际查询需求添加索引
            # models.Index(fields=['created_at']),
            # models.Index(fields=['user_id']),
            # models.Index(fields=['status']),
        ]
        # 数据库表选项
        db_table = 'loggingconfig'
        ordering = ['-created_at']
v
else:
    # 非Pydantic备用配置类
    class Settings:
        """简单字典式配置"""
        def __init__(self, config_dict: Dict[str, Any]):
            """从字典初始化配置"""
            self._config = config_dict
            
            # 为常用属性设置字段
            self.environment = config_dict.get("environment", "development")
            self.debug = config_dict.get("debug", False)
            self.enable_auth = config_dict.get("enable_auth", False)
            self.max_message_size_bytes = config_dict.get("max_message_size_bytes", 4 * 1024 * 1024)
            
            # 子配置
            self.server = DictWrapper(config_dict.get("server", {}))
            self.kafka = DictWrapper(config_dict.get("kafka", {}))
            self.redis = DictWrapper(config_dict.get("redis", {})) if "redis" in config_dict else None
            self.metrics = DictWrapper(config_dict.get("metrics", {}))
            self.logging = DictWrapper(config_dict.get("logging", {}))
            
    class DictWrapper:
        """字典包装器，允许通过属性访问"""
        def __init__(self, data: Dict[str, Any]):
            """从字典初始化"""
            self._data = data
            
            # 设置属性
            for key, value in data.items():
                setattr(self, key, value)
                
            @cache(timeout=300)  # 5分钟缓存
def get(self, key, default=None):
            """获取键值，如果不存在则返回默认值"""
            return self._data.get(key, default)

def load_yaml_config(filepath: Path) -> Dict[str, Any]:
    """加载YAML配置文件"""
    try:
        with open(filepath, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"加载配置文件出错: {filepath} - {str(e)}")
        return {}

def load_env_vars(prefix: str = ENV_VAR_PREFIX) -> Dict[str, Any]:
    """从环境变量加载配置"""
    config = {}
    
    for key, value in os.environ.items():
        # 只处理带前缀的环境变量
        if key.startswith(prefix):
            # 移除前缀并转换为小写
            key = key[len(prefix):].lower()
            
            # 处理嵌套键，格式如MB_SERVER_HOST
            parts = key.split("_")
            
            # 尝试转换为合适的类型
            try:
                # 尝试解析为JSON
                if value.startswith("{") or value.startswith("["):
                    value = json.loads(value)
                # 尝试转换布尔值
                elif value.lower() in ("true", "yes", "1"):
                    value = True
                elif value.lower() in ("false", "no", "0"):
                    value = False
                # 尝试转换为数字
                elif value.isdigit():
                    value = int(value)
                elif value.replace(".", "", 1).isdigit() and value.count(".") == 1:
                    value = float(value)
            except json.JSONDecodeError:
                # 如果不是有效的JSON，保持为字符串
                pass
            
            # 构建嵌套字典
            current = config
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    # 最后一部分是值
                    current[part] = value
                else:
                    # 确保中间嵌套存在
                    if part not in current:
                        current[part] = {}
                    current = current[part]
    
    return config

def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """深度合并两个字典，override中的值覆盖base中的值"""
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # 递归合并嵌套字典
            result[key] = deep_merge(result[key], value)
        else:
            # 直接覆盖或添加新键
            result[key] = value
            
    return result

def mask_sensitive_values(config: Dict[str, Any], mask: str = "******") -> Dict[str, Any]:
    """遮盖敏感配置值"""
    # 敏感字段关键词列表
    sensitive_keywords = [
        "password", "secret", "key", "token", "credential", "sasl_plain_password"
    ]
    
    result = {}
    
    for key, value in config.items():
        if isinstance(value, dict):
            # 递归处理嵌套字典
            result[key] = mask_sensitive_values(value, mask)
        elif any(keyword in key.lower() for keyword in sensitive_keywords) and value:
            # 遮盖敏感值
            result[key] = mask
        else:
            # 保持原值
            result[key] = value
            
    return result

def load_settings() -> Settings:
    """加载和合并配置"""
    # 加载默认配置
    config = load_yaml_config(DEFAULT_CONFIG_PATH)
    
    # 加载环境特定配置(如果存在)
    env = os.environ.get("APP_ENV", "development")
    env_config_path = CONFIG_DIR / f"{env}.yaml"
    if env_config_path.exists():
        env_config = load_yaml_config(env_config_path)
        config = deep_merge(config, env_config)
    
    # 检查自定义配置路径
    custom_config_path = os.environ.get(ENV_CONFIG_PATH_VAR)
    if custom_config_path:
        custom_path = Path(custom_config_path)
        if custom_path.exists():
            custom_config = load_yaml_config(custom_path)
            config = deep_merge(config, custom_config)
        else:
            logger.warning(f"指定的配置路径不存在: {custom_config_path}")
    
    # 加载环境变量
    env_config = load_env_vars()
    config = deep_merge(config, env_config)
    
    # 确保必要的配置存在
    if "environment" not in config:
        config["environment"] = env
    
    # 打印配置（遮盖敏感信息）
    if logger.isEnabledFor(logging.DEBUG):
        masked_config = mask_sensitive_values(config)
        logger.debug(f"加载的配置: {json.dumps(masked_config, indent=2)}")
    
    # 创建配置对象
    if PYDANTIC_AVAILABLE:
        return Settings(**config)
    else:
        return Settings(config)

# 导出配置对象
settings = load_settings() 