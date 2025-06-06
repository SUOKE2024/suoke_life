#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
索克生活 - 统一数据库配置
Unified Database Configuration for Suoke Life
"""

from functools import lru_cache
from pydantic import BaseSettings, Field, field_validator
from typing import Dict, Any, Optional, List
import os
from pathlib import Path

class DatabaseConfig(BaseSettings):
    """统一数据库配置"""
    
    # 主数据库配置
    primary_host: str = Field(default="localhost", description="主数据库主机")
    primary_port: int = Field(default=5432, description="主数据库端口")
    primary_user: str = Field(default="postgres", description="主数据库用户")
    primary_password: str = Field(default="", description="主数据库密码")
    primary_database: str = Field(default="suoke_life", description="主数据库名称")
    
    # MongoDB配置
    mongodb_host: str = Field(default="localhost", description="MongoDB主机")
    mongodb_port: int = Field(default=27017, description="MongoDB端口")
    mongodb_user: str = Field(default="", description="MongoDB用户")
    mongodb_password: str = Field(default="", description="MongoDB密码")
    mongodb_database: str = Field(default="suoke_life_docs", description="MongoDB数据库名称")
    
    # Redis配置
    redis_host: str = Field(default="localhost", description="Redis主机")
    redis_port: int = Field(default=6379, description="Redis端口")
    redis_password: str = Field(default="", description="Redis密码")
    redis_db: int = Field(default=0, description="Redis数据库编号")
    
    # 连接池配置
    pool_size: int = Field(default=20, description="连接池大小")
    max_overflow: int = Field(default=30, description="最大溢出连接数")
    pool_timeout: int = Field(default=30, description="连接池超时时间")
    pool_recycle: int = Field(default=3600, description="连接回收时间")
    
    # 性能配置
    echo: bool = Field(default=False, description="是否输出SQL日志")
    echo_pool: bool = Field(default=False, description="是否输出连接池日志")
    query_timeout: int = Field(default=30, description="查询超时时间")
    slow_query_threshold: float = Field(default=1.0, description="慢查询阈值")
    
    # 备份配置
    backup_enabled: bool = Field(default=True, description="是否启用备份")
    backup_interval: int = Field(default=86400, description="备份间隔(秒)")
    backup_retention: int = Field(default=7, description="备份保留天数")
    backup_path: str = Field(default="backups", description="备份路径")
    
    # 迁移配置
    migration_enabled: bool = Field(default=True, description="是否启用迁移")
    migration_auto: bool = Field(default=False, description="是否自动迁移")
    migration_dir: str = Field(default="migrations", description="迁移目录")
    
    # 安全配置
    ssl_enabled: bool = Field(default=False, description="是否启用SSL")
    ssl_cert_path: str = Field(default="", description="SSL证书路径")
    ssl_key_path: str = Field(default="", description="SSL密钥路径")
    ssl_ca_path: str = Field(default="", description="SSL CA路径")
    
    class Config:
        env_prefix = "DB_"
        env_file = ".env"
        case_sensitive = False
    
    @field_validator('primary_port', 'mongodb_port', 'redis_port')
    @classmethod
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError("端口号必须在1-65535之间")
        return v
    
    @field_validator('pool_size', 'max_overflow')
    @classmethod
    def validate_pool_config(cls, v):
        if v < 1:
            raise ValueError("连接池配置必须大于0")
        return v
    
    @property
    def primary_url(self) -> str:
        """主数据库连接URL"""
        return f"postgresql+asyncpg://{self.primary_user}:{self.primary_password}@{self.primary_host}:{self.primary_port}/{self.primary_database}"
    
    @property
    def mongodb_url(self) -> str:
        """MongoDB连接URL"""
        if self.mongodb_user and self.mongodb_password:
            return f"mongodb://{self.mongodb_user}:{self.mongodb_password}@{self.mongodb_host}:{self.mongodb_port}/{self.mongodb_database}"
        return f"mongodb://{self.mongodb_host}:{self.mongodb_port}/{self.mongodb_database}"
    
    @property
    def redis_url(self) -> str:
        """Redis连接URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    def get_engine_config(self) -> Dict[str, Any]:
        """获取SQLAlchemy引擎配置"""
        config = {
            'echo': self.echo,
            'echo_pool': self.echo_pool,
            'pool_size': self.pool_size,
            'max_overflow': self.max_overflow,
            'pool_timeout': self.pool_timeout,
            'pool_recycle': self.pool_recycle,
        }
        
        if self.ssl_enabled:
            config['connect_args'] = {
                'sslmode': 'require',
                'sslcert': self.ssl_cert_path,
                'sslkey': self.ssl_key_path,
                'sslrootcert': self.ssl_ca_path,
            }
        
        return config
    
    def get_service_database_config(self, service_name: str) -> Dict[str, Any]:
        """获取特定服务的数据库配置"""
        return {
            'host': self.primary_host,
            'port': self.primary_port,
            'user': self.primary_user,
            'password': self.primary_password,
            'database': f"{self.primary_database}_{service_name}",
            'pool_size': self.pool_size,
            'max_overflow': self.max_overflow,
            'pool_timeout': self.pool_timeout,
            'pool_recycle': self.pool_recycle,
        }

class ServiceDatabaseMapping:
    """服务数据库映射配置"""
    
    SERVICES = {
        # 智能体服务
        'xiaoai_service': {
            'database': 'suoke_xiaoai',
            'description': '小艾智能体数据库',
            'tables': ['conversations', 'user_interactions', 'ai_responses']
        },
        'xiaoke_service': {
            'database': 'suoke_xiaoke',
            'description': '小克智能体数据库',
            'tables': ['health_data', 'analysis_results', 'recommendations']
        },
        'laoke_service': {
            'database': 'suoke_laoke',
            'description': '老克智能体数据库',
            'tables': ['tcm_diagnoses', 'prescriptions', 'treatment_plans']
        },
        'soer_service': {
            'database': 'suoke_soer',
            'description': '索儿智能体数据库',
            'tables': ['lifestyle_data', 'behavior_tracking', 'wellness_plans']
        },
        
        # 诊断服务
        'look_service': {
            'database': 'suoke_diagnosis_look',
            'description': '望诊服务数据库',
            'tables': ['visual_analysis', 'image_data', 'diagnosis_results']
        },
        'listen_service': {
            'database': 'suoke_diagnosis_listen',
            'description': '闻诊服务数据库',
            'tables': ['audio_analysis', 'voice_patterns', 'sound_diagnosis']
        },
        'inquiry_service': {
            'database': 'suoke_diagnosis_inquiry',
            'description': '问诊服务数据库',
            'tables': ['questionnaires', 'symptoms', 'medical_history']
        },
        'palpation_service': {
            'database': 'suoke_diagnosis_palpation',
            'description': '切诊服务数据库',
            'tables': ['pulse_data', 'touch_analysis', 'physical_examination']
        },
        'calculation_service': {
            'database': 'suoke_diagnosis_calculation',
            'description': '算诊服务数据库',
            'tables': ['calculation_results', 'algorithm_data', 'diagnostic_scores']
        },
        
        # 核心服务
        'user_service': {
            'database': 'suoke_users',
            'description': '用户服务数据库',
            'tables': ['users', 'profiles', 'authentication', 'permissions']
        },
        'health_data_service': {
            'database': 'suoke_health_data',
            'description': '健康数据服务数据库',
            'tables': ['health_records', 'vital_signs', 'medical_reports']
        },
        'blockchain_service': {
            'database': 'suoke_blockchain',
            'description': '区块链服务数据库',
            'tables': ['transactions', 'blocks', 'smart_contracts']
        },
        'auth_service': {
            'database': 'suoke_auth',
            'description': '认证服务数据库',
            'tables': ['tokens', 'sessions', 'oauth_clients']
        },
        'message_bus': {
            'database': 'suoke_messaging',
            'description': '消息总线数据库',
            'tables': ['messages', 'queues', 'subscriptions']
        }
    }
    
    @classmethod
    def get_all_databases(cls) -> List[str]:
        """获取所有数据库名称"""
        return [config['database'] for config in cls.SERVICES.values()]
    
    @classmethod
    def get_service_config(cls, service_name: str) -> Optional[Dict[str, Any]]:
        """获取服务配置"""
        return cls.SERVICES.get(service_name)

@lru_cache()
def get_database_config() -> DatabaseConfig:
    """获取数据库配置实例"""
    return DatabaseConfig()

def get_service_database_url(service_name: str) -> str:
    """获取服务数据库连接URL"""
    config = get_database_config()
    service_config = ServiceDatabaseMapping.get_service_config(service_name)
    
    if not service_config:
        raise ValueError(f"未知的服务: {service_name}")
    
    database_name = service_config['database']
    return f"postgresql+asyncpg://{config.primary_user}:{config.primary_password}@{config.primary_host}:{config.primary_port}/{database_name}"

# 导出配置
__all__ = [
    'DatabaseConfig',
    'ServiceDatabaseMapping',
    'get_database_config',
    'get_service_database_url'
] 