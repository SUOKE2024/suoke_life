#!/usr/bin/env python3

"""
配置加载和模型模块
"""

import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, validator
import yaml


class ServerConfig(BaseModel):
    """服务器配置"""
    port: int = 50055
    max_workers: int = 10
    max_message_length: int = 10485760


class LoggingConfig(BaseModel):
    """日志配置"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: str | None = None
    max_size_mb: int = 100
    backup_count: int = 5


class BlockchainNodeConfig(BaseModel):
    """区块链节点配置"""
    endpoint: str
    chain_id: int = 1


class ContractsConfig(BaseModel):
    """智能合约配置"""
    health_data: str
    zkp_verifier: str
    access_control: str


class WalletConfig(BaseModel):
    """钱包配置"""
    keystore_path: str
    gas_limit: int = 3000000
    gas_price_strategy: str = "medium"


class BlockchainConfig(BaseModel):
    """区块链配置"""
    network_type: str
    node: BlockchainNodeConfig
    contracts: ContractsConfig
    wallet: WalletConfig


class DatabaseConfig(BaseModel):
    """数据库配置"""
    driver: str
    host: str
    port: int
    username: str
    password: str
    database: str
    pool_size: int = 20
    max_overflow: int = 10
    pool_timeout: int = 30

    @validator("password")
    def validate_env_vars(cls, v):
        """替换环境变量"""
        if v.startswith("${") and v.endswith("}"):
            env_var = v[2:-1]
            v = os.environ.get(env_var, "")
        return v


class JwtConfig(BaseModel):
    """JWT配置"""
    public_key_path: str
    private_key_path: str
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 30


class SecurityConfig(BaseModel):
    """安全配置"""
    encryption_key_path: str
    jwt: JwtConfig


class ZkpConfig(BaseModel):
    """零知识证明配置"""
    proving_key_path: str
    verification_key_path: str
    supported_circuits: list[str]


class ServiceConfig(BaseModel):
    """服务集成配置"""
    endpoint: str
    timeout_seconds: int = 5


class MessageBusConfig(BaseModel):
    """消息总线配置"""
    host: str
    port: int
    username: str
    password: str
    exchange: str
    routing_key: str

    @validator("password")
    def validate_env_vars(cls, v):
        """替换环境变量"""
        if v.startswith("${") and v.endswith("}"):
            env_var = v[2:-1]
            v = os.environ.get(env_var, "")
        return v


class IntegrationsConfig(BaseModel):
    """服务集成配置"""
    user_service: ServiceConfig
    message_bus: MessageBusConfig


class PrometheusConfig(BaseModel):
    """Prometheus配置"""
    enabled: bool = True
    port: int = 9090


class TracingConfig(BaseModel):
    """分布式追踪配置"""
    enabled: bool = True
    jaeger_endpoint: str
    service_name: str
    sample_rate: float = 0.1


class MonitoringConfig(BaseModel):
    """监控配置"""
    prometheus: PrometheusConfig
    tracing: TracingConfig


class CacheConfig(BaseModel):
    """缓存配置"""
    type: str
    host: str
    port: int
    db: int = 0
    password: str
    ttl_seconds: int = 300

    @validator("password")
    def validate_env_vars(cls, v):
        """替换环境变量"""
        if v.startswith("${") and v.endswith("}"):
            env_var = v[2:-1]
            v = os.environ.get(env_var, "")
        return v


class AppConfig(BaseModel):
    """应用配置"""
    server: ServerConfig
    logging: LoggingConfig
    blockchain: BlockchainConfig
    database: DatabaseConfig
    security: SecurityConfig
    zkp: ZkpConfig
    integrations: IntegrationsConfig
    monitoring: MonitoringConfig
    cache: CacheConfig


def load_config(config_path: str | Path) -> AppConfig:
    """
    从YAML文件加载配置
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        应用配置对象
    """
    with open(config_path) as f:
        config_dict = yaml.safe_load(f)

    # 递归解析环境变量
    _resolve_env_vars(config_dict)

    return AppConfig(**config_dict)


def _resolve_env_vars(config_dict: dict[str, Any]) -> None:
    """
    递归解析配置中的环境变量
    
    Args:
        config_dict: 配置字典
    """
    for key, value in config_dict.items():
        if isinstance(value, dict):
            _resolve_env_vars(value)
        elif isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            config_dict[key] = os.environ.get(env_var, "")
