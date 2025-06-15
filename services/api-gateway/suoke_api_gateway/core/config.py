#!/usr/bin/env python3
"""
索克生活 API 网关配置管理

提供配置加载、验证和管理功能
"""

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisConfig(BaseModel):
    """Redis 配置"""
    host: str = Field(default="localhost", description="Redis 主机地址")
    port: int = Field(default=6379, description="Redis 端口")
    db: int = Field(default=0, description="Redis 数据库编号")
    password: Optional[str] = Field(default=None, description="Redis 密码")
    max_connections: int = Field(default=100, description="最大连接数")
    socket_timeout: float = Field(default=5.0, description="套接字超时时间")
    socket_connect_timeout: float = Field(default=5.0, description="连接超时时间")
    retry_on_timeout: bool = Field(default=True, description="超时重试")
    
    @property
    def url(self) -> str:
        """获取 Redis URL"""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"


class JWTConfig(BaseModel):
    """JWT 配置"""
    secret_key: str = Field(description="JWT 签名密钥")
    algorithm: str = Field(default="HS256", description="JWT 算法")
    access_token_expire_minutes: int = Field(default=30, description="访问令牌过期时间（分钟）")
    refresh_token_expire_days: int = Field(default=7, description="刷新令牌过期时间（天）")
    
    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("JWT 密钥长度至少 32 个字符")
        return v


class RateLimitConfig(BaseModel):
    """限流配置"""
    enabled: bool = Field(default=True, description="是否启用限流")
    default_rate: str = Field(default="100/minute", description="默认限流速率")
    burst_size: int = Field(default=10, description="突发请求大小")
    storage_url: Optional[str] = Field(default=None, description="存储 URL")
    
    @field_validator("default_rate")
    @classmethod
    def validate_rate(cls, v: str) -> str:
        # 验证速率格式，如 "100/minute", "10/second"
        if "/" not in v:
            raise ValueError("限流速率格式错误，应为 'number/unit'")
        return v


class CORSConfig(BaseModel):
    """CORS 配置"""
    enabled: bool = Field(default=True, description="是否启用 CORS")
    allow_origins: List[str] = Field(default=["*"], description="允许的源")
    allow_methods: List[str] = Field(default=["*"], description="允许的方法")
    allow_headers: List[str] = Field(default=["*"], description="允许的头部")
    allow_credentials: bool = Field(default=True, description="允许凭证")
    expose_headers: List[str] = Field(default=[], description="暴露的头部")
    max_age: int = Field(default=600, description="预检请求缓存时间")


class SecurityConfig(BaseModel):
    """安全配置"""
    trusted_hosts: List[str] = Field(default=["*"], description="信任的主机")
    allowed_hosts: List[str] = Field(default=["*"], description="允许的主机")
    secure_headers: bool = Field(default=True, description="安全头部")
    content_security_policy: Optional[str] = Field(default=None, description="内容安全策略")
    

class TracingConfig(BaseModel):
    """链路追踪配置"""
    enabled: bool = Field(default=True, description="是否启用追踪")
    service_name: str = Field(default="suoke-api-gateway", description="服务名称")
    jaeger_endpoint: Optional[str] = Field(default=None, description="Jaeger 端点")
    otlp_endpoint: Optional[str] = Field(default=None, description="OTLP 端点")
    sample_rate: float = Field(default=1.0, description="采样率")
    
    @field_validator("sample_rate")
    @classmethod
    def validate_sample_rate(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("采样率必须在 0.0 到 1.0 之间")
        return v


class MetricsConfig(BaseModel):
    """指标配置"""
    enabled: bool = Field(default=True, description="是否启用指标")
    prometheus_enabled: bool = Field(default=True, description="Prometheus 指标")
    custom_metrics: bool = Field(default=True, description="自定义指标")
    

class CacheConfig(BaseModel):
    """缓存配置"""
    enabled: bool = Field(default=True, description="是否启用缓存")
    default_ttl: int = Field(default=300, description="默认 TTL（秒）")
    max_size: int = Field(default=1000, description="最大缓存条目数")
    

class LoadBalancerConfig(BaseModel):
    """负载均衡配置"""
    strategy: str = Field(default="round_robin", description="负载均衡策略")
    health_check_interval: int = Field(default=30, description="健康检查间隔（秒）")
    health_check_timeout: int = Field(default=5, description="健康检查超时（秒）")
    max_retries: int = Field(default=3, description="最大重试次数")
    
    @field_validator("strategy")
    @classmethod
    def validate_strategy(cls, v: str) -> str:
        allowed = ["round_robin", "weighted_round_robin", "least_connections", "random"]
        if v not in allowed:
            raise ValueError(f"负载均衡策略必须是 {allowed} 之一")
        return v


class ServiceConfig(BaseModel):
    """服务配置"""
    name: str = Field(description="服务名称")
    url: str = Field(description="服务 URL")
    weight: int = Field(default=1, description="权重")
    timeout: float = Field(default=30.0, description="超时时间")
    health_check_path: str = Field(default="/health", description="健康检查路径")
    

class Settings(BaseSettings):
    """应用配置"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="GATEWAY_",
        case_sensitive=False,
        extra="ignore",
    )
    
    # 基础配置
    app_name: str = Field(default="索克生活 API 网关", description="应用名称")
    app_version: str = Field(default="0.1.0", description="应用版本")
    environment: str = Field(default="development", description="运行环境")
    debug: bool = Field(default=False, description="调试模式")
    
    # 服务器配置
    host: str = Field(default="0.0.0.0", description="监听地址")
    port: int = Field(default=8000, description="监听端口")
    workers: int = Field(default=1, description="工作进程数")
    
    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_format: str = Field(default="json", description="日志格式")
    log_file: Optional[str] = Field(default=None, description="日志文件路径")
    
    # 数据库配置
    redis: RedisConfig = Field(default_factory=RedisConfig, description="Redis 配置")
    
    # 安全配置
    jwt: JWTConfig = Field(description="JWT 配置")
    security: SecurityConfig = Field(default_factory=SecurityConfig, description="安全配置")
    
    # 中间件配置
    cors: CORSConfig = Field(default_factory=CORSConfig, description="CORS 配置")
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig, description="限流配置")
    
    # 功能配置
    tracing: TracingConfig = Field(default_factory=TracingConfig, description="追踪配置")
    metrics: MetricsConfig = Field(default_factory=MetricsConfig, description="指标配置")
    cache: CacheConfig = Field(default_factory=CacheConfig, description="缓存配置")
    load_balancer: LoadBalancerConfig = Field(default_factory=LoadBalancerConfig, description="负载均衡配置")
    
    # 服务配置
    services: List[ServiceConfig] = Field(default_factory=list, description="后端服务配置")
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"环境必须是 {allowed} 之一")
        return v
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"日志级别必须是 {allowed} 之一")
        return v.upper()
    
    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.environment == "production"
    
    def get_redis_url(self) -> str:
        """获取 Redis URL"""
        return self.redis.url


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（单例）"""
    # 设置默认 JWT 密钥
    jwt_secret = os.getenv("GATEWAY_JWT_SECRET_KEY", "your-super-secret-jwt-key-change-in-production-32-chars-min")
    
    return Settings(
        jwt=JWTConfig(secret_key=jwt_secret)
    )


def create_settings_from_file(config_path: Path) -> Settings:
    """从配置文件创建配置实例"""
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    # 读取配置文件
    with open(config_path, "r", encoding="utf-8") as f:
        if config_path.suffix.lower() in [".yaml", ".yml"]:
            config_data = yaml.safe_load(f)
        elif config_path.suffix.lower() == ".json":
            config_data = json.load(f)
        else:
            raise ValueError(f"不支持的配置文件格式: {config_path.suffix}")
    
    # 创建配置实例
    return Settings(**config_data)


def create_default_config() -> Dict[str, Any]:
    """创建默认配置字典"""
    return {
        "app_name": "索克生活 API 网关",
        "app_version": "0.1.0",
        "environment": "development",
        "debug": True,
        "host": "0.0.0.0",
        "port": 8000,
        "workers": 1,
        "log_level": "INFO",
        "log_format": "json",
        "redis": {
            "host": "localhost",
            "port": 6379,
            "db": 0,
            "max_connections": 100,
        },
        "jwt": {
            "secret_key": "your-super-secret-jwt-key-change-in-production-32-chars-min",
            "algorithm": "HS256",
            "access_token_expire_minutes": 30,
        },
        "cors": {
            "enabled": True,
            "allow_origins": ["*"],
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        },
        "rate_limit": {
            "enabled": True,
            "default_rate": "100/minute",
        },
        "tracing": {
            "enabled": True,
            "service_name": "suoke-api-gateway",
        },
        "metrics": {
            "enabled": True,
            "prometheus_enabled": True,
        },
        "cache": {
            "enabled": True,
            "default_ttl": 300,
        },
        "load_balancer": {
            "strategy": "round_robin",
            "health_check_interval": 30,
        },
        "services": [
            {
                "name": "xiaoai-service",
                "url": "http://xiaoai-service:8001",
                "weight": 1,
            },
            {
                "name": "xiaoke-service",
                "url": "http://xiaoke-service:8002",
                "weight": 1,
            },
            {
                "name": "laoke-service",
                "url": "http://laoke-service:8003",
                "weight": 1,
            },
            {
                "name": "soer-service",
                "url": "http://soer-service:8004",
                "weight": 1,
            },
        ],
    }


def save_config_to_file(config: Dict[str, Any], file_path: Path) -> None:
    """保存配置到文件"""
    with open(file_path, "w", encoding="utf-8") as f:
        if file_path.suffix.lower() in [".yaml", ".yml"]:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        elif file_path.suffix.lower() == ".json":
            json.dump(config, f, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"不支持的配置文件格式: {file_path.suffix}")


def validate_config(config_data: Dict[str, Any]) -> bool:
    """验证配置数据"""
    try:
        Settings(**config_data)
        return True
    except Exception:
        return False
