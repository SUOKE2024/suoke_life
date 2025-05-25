#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
老克智能体服务 - 配置加载工具
提供从配置文件和环境变量加载配置的功能
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
from dataclasses import dataclass, field
import re
from functools import lru_cache

logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """数据库配置"""
    type: str = "postgres"
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = ""
    database: str = "laoke_service"
    pool_size: int = 10
    ssl_mode: str = "disable"
    
    @property
    def connection_string(self) -> str:
        """获取数据库连接字符串"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

@dataclass
class CacheConfig:
    """缓存配置"""
    type: str = "redis"
    host: str = "localhost"
    port: int = 6379
    password: str = ""
    db: int = 0
    pool_size: int = 10
    ttl: int = 3600
    
    @property
    def connection_string(self) -> str:
        """获取Redis连接字符串"""
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"

@dataclass
class ServerConfig:
    """服务器配置"""
    host: str = "0.0.0.0"
    port: int = 8080
    grpc_port: int = 50051
    metrics_port: int = 9091
    debug: bool = False
    timeout: int = 30
    cors_origins: List[str] = field(default_factory=lambda: ["*"])

@dataclass
class LoggingConfig:
    """日志配置"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = None
    max_size_mb: int = 100
    backup_count: int = 10
    console: bool = True

class Config:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        self._config_data: Dict[str, Any] = {}
        self._env_prefix = "LAOKE_"
        self._config_loaded = False
        
        # 确定配置文件路径
        if config_path:
            self._config_path = Path(config_path)
        else:
            self._config_path = self._find_config_file()
        
        # 加载配置
        self._load_config()
    
    def _find_config_file(self) -> Path:
        """查找配置文件"""
        # 优先级：环境变量 > 当前目录 > config目录
        env_path = os.getenv(f"{self._env_prefix}CONFIG_PATH")
        if env_path:
            return Path(env_path)
        
        # 查找可能的配置文件位置
        possible_paths = [
            Path("config.yaml"),
            Path("config/config.yaml"),
            Path("../config/config.yaml"),
            Path("../../config/config.yaml"),
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        # 如果都找不到，使用默认路径
        return Path("config/config.yaml")
    
    def _load_config(self) -> None:
        """加载配置文件"""
        try:
            if self._config_path.exists():
                with open(self._config_path, 'r', encoding='utf-8') as f:
                    self._config_data = yaml.safe_load(f) or {}
                logger.info(f"配置文件加载成功: {self._config_path}")
            else:
                logger.warning(f"配置文件不存在: {self._config_path}，使用默认配置")
                self._config_data = {}
            
            # 处理环境变量替换
            self._process_env_variables()
            self._config_loaded = True
            
        except Exception as e:
            logger.error(f"配置文件加载失败: {str(e)}")
            self._config_data = {}
    
    def _process_env_variables(self) -> None:
        """处理配置中的环境变量替换"""
        def replace_env_vars(obj: Any) -> Any:
            if isinstance(obj, str):
                # 匹配 ${VAR:default} 格式
                pattern = r'\$\{([^:}]+)(?::([^}]*))?\}'
                
                def replacer(match):
                    var_name = match.group(1)
                    default_value = match.group(2) if match.group(2) is not None else ""
                    return os.getenv(var_name, default_value)
                
                return re.sub(pattern, replacer, obj)
            elif isinstance(obj, dict):
                return {k: replace_env_vars(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_env_vars(item) for item in obj]
            else:
                return obj
        
        self._config_data = replace_env_vars(self._config_data)
    
    @lru_cache(maxsize=128)
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，支持点号分隔的嵌套键"""
        if not self._config_loaded:
            return default
        
        # 首先检查环境变量
        env_key = f"{self._env_prefix}{key.upper().replace('.', '_')}"
        env_value = os.getenv(env_key)
        if env_value is not None:
            return self._convert_env_value(env_value)
        
        # 然后从配置文件获取
        keys = key.split('.')
        value = self._config_data
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def _convert_env_value(self, value: str) -> Any:
        """转换环境变量值为适当的类型"""
        # 布尔值
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # 数字
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # 列表（逗号分隔）
        if ',' in value:
            return [item.strip() for item in value.split(',')]
        
        return value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """获取配置段"""
        return self.get(section, {})
    
    def get_database_config(self) -> DatabaseConfig:
        """获取数据库配置"""
        db_config = self.get_section('database')
        return DatabaseConfig(
            type=db_config.get('type', 'postgres'),
            host=db_config.get('host', 'localhost'),
            port=db_config.get('port', 5432),
            user=db_config.get('user', 'postgres'),
            password=db_config.get('password', ''),
            database=db_config.get('database', 'laoke_service'),
            pool_size=db_config.get('pool_size', 10),
            ssl_mode=db_config.get('ssl_mode', 'disable')
        )
    
    def get_cache_config(self) -> CacheConfig:
        """获取缓存配置"""
        cache_config = self.get_section('cache')
        return CacheConfig(
            type=cache_config.get('type', 'redis'),
            host=cache_config.get('host', 'localhost'),
            port=cache_config.get('port', 6379),
            password=cache_config.get('password', ''),
            db=cache_config.get('db', 0),
            pool_size=cache_config.get('pool_size', 10),
            ttl=cache_config.get('ttl', 3600)
        )
    
    def get_server_config(self) -> ServerConfig:
        """获取服务器配置"""
        server_config = self.get_section('server')
        return ServerConfig(
            host=server_config.get('host', '0.0.0.0'),
            port=server_config.get('port', 8080),
            grpc_port=server_config.get('grpc_port', 50051),
            metrics_port=server_config.get('metrics_port', 9091),
            debug=server_config.get('debug', False),
            timeout=server_config.get('timeout', 30),
            cors_origins=server_config.get('cors_origins', ['*'])
        )
    
    def get_logging_config(self) -> LoggingConfig:
        """获取日志配置"""
        logging_config = self.get_section('logging')
        return LoggingConfig(
            level=logging_config.get('level', 'INFO'),
            format=logging_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            file=logging_config.get('file'),
            max_size_mb=logging_config.get('max_size_mb', 100),
            backup_count=logging_config.get('backup_count', 10),
            console=logging_config.get('console', True)
        )
    
    def is_development(self) -> bool:
        """是否为开发环境"""
        env = self.get('environment', 'development')
        return env.lower() in ('development', 'dev')
    
    def is_production(self) -> bool:
        """是否为生产环境"""
        env = self.get('environment', 'development')
        return env.lower() in ('production', 'prod')
    
    def validate(self) -> List[str]:
        """验证配置的完整性"""
        errors = []
        
        # 检查必需的配置项
        required_configs = [
            'service.name',
            'service.version',
            'server.host',
            'server.port'
        ]
        
        for config_key in required_configs:
            if self.get(config_key) is None:
                errors.append(f"缺少必需的配置项: {config_key}")
        
        # 检查端口范围
        ports = ['server.port', 'server.grpc_port', 'server.metrics_port']
        for port_key in ports:
            port = self.get(port_key)
            if port and (not isinstance(port, int) or port < 1 or port > 65535):
                errors.append(f"端口配置无效: {port_key}={port}")
        
        # 检查日志级别
        log_level = self.get('logging.level', 'INFO')
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if log_level.upper() not in valid_levels:
            errors.append(f"日志级别无效: {log_level}")
        
        return errors
    
    def reload(self) -> None:
        """重新加载配置"""
        self.get.cache_clear()  # 清除缓存
        self._load_config()
        logger.info("配置已重新加载")

# 全局配置实例
_config: Optional[Config] = None

def get_config(config_path: Optional[str] = None) -> Config:
    """获取全局配置实例"""
    global _config
    if _config is None:
        _config = Config(config_path)
    return _config 