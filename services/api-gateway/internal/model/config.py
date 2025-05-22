#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API网关配置模型
"""

from typing import Dict, List, Optional, Set, Union

from pydantic import BaseModel, Field, field_validator


class RouteConfig(BaseModel):
    """
    路由配置
    """
    name: str
    prefix: str
    service: str
    methods: List[str] = Field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "PATCH"])
    strip_prefix: bool = True
    rewrite_path: Optional[str] = None
    timeout: float = 30.0
    retry: int = 0
    auth_required: bool = True


class ServiceEndpointConfig(BaseModel):
    """
    服务端点配置
    """
    host: str
    port: int


class ServiceHealthCheckConfig(BaseModel):
    """
    服务健康检查配置
    """
    path: str = "/health"
    interval: int = 30  # 秒
    timeout: int = 5  # 秒
    retries: int = 3
    healthy_threshold: int = 2
    unhealthy_threshold: int = 3


class ServiceConfig(BaseModel):
    """
    服务配置
    """
    name: str
    version: str = "v1"
    endpoints: List[ServiceEndpointConfig]
    health_check: Optional[ServiceHealthCheckConfig] = None


class ServiceDiscoveryConfig(BaseModel):
    """
    服务发现配置
    """
    type: str = "static"  # static, consul, kubernetes
    refresh_interval: int = 30  # 秒
    
    # 静态服务列表
    services: Dict[str, ServiceConfig] = Field(default_factory=dict)
    
    # Consul配置
    consul_host: Optional[str] = None
    consul_port: int = 8500
    
    # Kubernetes配置
    kubernetes_namespace: str = "default"
    kubernetes_label_selector: str = "app=suoke"
    
    # 默认健康检查配置
    default_health_check: ServiceHealthCheckConfig = Field(default_factory=ServiceHealthCheckConfig)


class JwtConfig(BaseModel):
    """
    JWT配置
    """
    secret_key: str
    algorithm: str = "HS256"
    expire_minutes: int = 30
    refresh_expire_minutes: int = 10080  # 7天


class AuthConfig(BaseModel):
    """
    认证配置
    """
    enabled: bool = True
    public_paths: List[str] = Field(default_factory=list)
    jwt: JwtConfig


class RateLimitConfig(BaseModel):
    """
    速率限制配置
    """
    enabled: bool = False
    max_requests: int = 100  # 最大请求数
    reset_interval: int = 60  # 重置间隔（秒）
    by_endpoint: bool = False  # 是否按端点限制


class CorsConfig(BaseModel):
    """
    CORS配置
    """
    enabled: bool = True
    allow_origins: List[str] = Field(default_factory=lambda: ["*"])
    allow_methods: List[str] = Field(default_factory=lambda: ["*"])
    allow_headers: List[str] = Field(default_factory=lambda: ["*"])
    allow_credentials: bool = False
    max_age: int = 600  # 10分钟


class CacheConfig(BaseModel):
    """
    缓存配置
    """
    enabled: bool = False
    type: str = "memory"  # memory, redis
    ttl: int = 60  # 秒
    max_size: int = 1000  # 内存缓存最大条目数
    redis_url: Optional[str] = None  # Redis连接URL
    include_headers: List[str] = Field(default_factory=list)  # 要包含在缓存键中的请求头


class CircuitBreakerConfig(BaseModel):
    """
    熔断器配置
    """
    enabled: bool = False
    failure_threshold: int = 5  # 触发熔断的失败次数
    recovery_timeout: int = 30  # 恢复尝试的超时时间（秒）
    half_open_success: int = 2  # 半开状态下成功请求的数量


class RetryConfig(BaseModel):
    """
    重试配置
    """
    enabled: bool = False
    max_retries: int = 3
    retry_delay: float = 0.5  # 重试延迟（秒）
    retry_status_codes: List[int] = Field(default_factory=lambda: [500, 502, 503, 504])


class LoadBalancerConfig(BaseModel):
    """
    负载均衡配置
    """
    strategy: str = "round_robin"  # round_robin, random, least_connections, ip_hash
    sticky_session: bool = False
    health_check_enabled: bool = True


class LoggingConfig(BaseModel):
    """
    日志配置
    """
    level: str = "INFO"
    format: str = "json"  # json, text
    output: str = "stdout"  # stdout, file
    file_path: Optional[str] = None
    max_file_size: int = 10  # MB
    backup_count: int = 5


class ObservabilityConfig(BaseModel):
    """
    可观测性配置
    """
    tracing_enabled: bool = False
    tracing_exporter: str = "jaeger"
    tracing_endpoint: Optional[str] = None
    metrics_enabled: bool = True
    metrics_endpoint: str = "/metrics"
    health_endpoint: str = "/health"


class MiddlewareConfig(BaseModel):
    """
    中间件配置
    """
    auth: Optional[AuthConfig] = None
    rate_limit: Optional[RateLimitConfig] = None
    cors: Optional[CorsConfig] = None
    trusted_hosts: Optional[List[str]] = None


class RestServerConfig(BaseModel):
    """REST服务器配置"""
    host: str = "0.0.0.0"
    port: int = 8080


class GrpcServerConfig(BaseModel):
    """gRPC服务器配置"""
    host: str = "0.0.0.0"
    port: int = 50050


class ServerConfig(BaseModel):
    """
    服务器配置
    """
    rest: RestServerConfig = Field(default_factory=RestServerConfig)
    grpc: GrpcServerConfig = Field(default_factory=GrpcServerConfig)
    production: bool = False
    debug: bool = True


class GatewayConfig(BaseModel):
    """
    API网关主配置
    """
    app_name: str = "suoke-api-gateway"
    server: ServerConfig = Field(default_factory=ServerConfig)
    
    # 路由配置
    routes: List[RouteConfig] = Field(default_factory=list)
    
    # 服务发现
    service_discovery: ServiceDiscoveryConfig = Field(default_factory=ServiceDiscoveryConfig)
    
    # 中间件
    middleware: MiddlewareConfig = Field(default_factory=MiddlewareConfig)
    
    # 缓存
    cache: CacheConfig = Field(default_factory=CacheConfig)
    
    # 熔断器
    circuit_breaker: CircuitBreakerConfig = Field(default_factory=CircuitBreakerConfig)
    
    # 重试
    retry: RetryConfig = Field(default_factory=RetryConfig)
    
    # 负载均衡
    load_balancer: LoadBalancerConfig = Field(default_factory=LoadBalancerConfig)
    
    # 日志
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    
    # 可观测性
    observability: ObservabilityConfig = Field(default_factory=ObservabilityConfig)
    
    @field_validator("middleware", mode="before")
    @classmethod
    def set_default_middleware(cls, v):
        if v is None:
            return MiddlewareConfig()
        return v