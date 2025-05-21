#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class DatabaseConfig:
    """数据库配置"""
    host: str
    port: int
    user: str
    password: str
    dbname: str
    max_connections: int = 10
    min_connections: int = 1
    connection_timeout: int = 10


@dataclass
class GrpcServerConfig:
    """gRPC服务器配置"""
    port: int
    workers: int = 10
    max_message_length: int = 100 * 1024 * 1024  # 100MB
    max_concurrent_streams: int = 100
    enable_reflection: bool = True


@dataclass
class RestServerConfig:
    """REST服务器配置"""
    port: int
    workers: int = 4
    enable_cors: bool = True
    cors_allowed_origins: List[str] = field(default_factory=lambda: ["*"])
    enable_swagger: bool = True


@dataclass
class ServerConfig:
    """服务器配置"""
    name: str
    version: str
    grpc: GrpcServerConfig
    rest: RestServerConfig


@dataclass
class KafkaConfig:
    """Kafka配置"""
    broker: str
    topics: Dict[str, str] = field(default_factory=dict)
    consumer_group: str = "medical-service"
    auto_commit: bool = True
    auto_commit_interval_ms: int = 5000


@dataclass
class ServiceConfig:
    """外部服务配置"""
    host: str
    port: int
    timeout: int = 10


@dataclass
class ServicesConfig:
    """所有外部服务配置"""
    health_data: ServiceConfig
    med_knowledge: ServiceConfig
    inquiry: ServiceConfig
    listen: ServiceConfig
    look: ServiceConfig
    palpation: ServiceConfig
    rag: ServiceConfig


@dataclass
class ObservabilityConfig:
    """可观测性配置"""
    log_level: str = "info"
    log_format: str = "json"
    enable_tracing: bool = True
    jaeger_endpoint: Optional[str] = None
    enable_metrics: bool = True
    metrics_port: int = 9090


@dataclass
class SecurityConfig:
    """安全配置"""
    jwt_secret: Optional[str] = None
    jwt_algorithm: str = "HS256"
    jwt_expiration_seconds: int = 3600 * 24  # 1天
    enable_api_key: bool = False
    api_keys: List[str] = field(default_factory=list)


@dataclass
class Config:
    """应用程序配置"""
    server: ServerConfig
    database: DatabaseConfig
    services: ServicesConfig
    kafka: Optional[KafkaConfig] = None
    observability: ObservabilityConfig = field(default_factory=ObservabilityConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """从字典创建配置对象"""
        # 处理服务器配置
        server_data = data.get('server', {})
        grpc_data = server_data.get('grpc', {})
        rest_data = server_data.get('rest', {})
        
        grpc_config = GrpcServerConfig(
            port=grpc_data.get('port', 50051),
            workers=grpc_data.get('workers', 10),
            max_message_length=grpc_data.get('max_message_length', 100 * 1024 * 1024),
            max_concurrent_streams=grpc_data.get('max_concurrent_streams', 100),
            enable_reflection=grpc_data.get('enable_reflection', True)
        )
        
        rest_config = RestServerConfig(
            port=rest_data.get('port', 8080),
            workers=rest_data.get('workers', 4),
            enable_cors=rest_data.get('enable_cors', True),
            cors_allowed_origins=rest_data.get('cors_allowed_origins', ["*"]),
            enable_swagger=rest_data.get('enable_swagger', True)
        )
        
        server_config = ServerConfig(
            name=server_data.get('name', 'medical-service'),
            version=server_data.get('version', '0.1.0'),
            grpc=grpc_config,
            rest=rest_config
        )
        
        # 处理数据库配置
        db_data = data.get('database', {})
        database_config = DatabaseConfig(
            host=db_data.get('host', 'localhost'),
            port=db_data.get('port', 5432),
            user=db_data.get('user', 'postgres'),
            password=db_data.get('password', 'postgres'),
            dbname=db_data.get('dbname', 'medical_service'),
            max_connections=db_data.get('max_connections', 10),
            min_connections=db_data.get('min_connections', 1),
            connection_timeout=db_data.get('connection_timeout', 10)
        )
        
        # 处理服务配置
        services_data = data.get('services', {})
        services_config = ServicesConfig(
            health_data=ServiceConfig(**services_data.get('health_data', {'host': 'localhost', 'port': 50051})),
            med_knowledge=ServiceConfig(**services_data.get('med_knowledge', {'host': 'localhost', 'port': 50052})),
            inquiry=ServiceConfig(**services_data.get('inquiry', {'host': 'localhost', 'port': 50053})),
            listen=ServiceConfig(**services_data.get('listen', {'host': 'localhost', 'port': 50054})),
            look=ServiceConfig(**services_data.get('look', {'host': 'localhost', 'port': 50055})),
            palpation=ServiceConfig(**services_data.get('palpation', {'host': 'localhost', 'port': 50056})),
            rag=ServiceConfig(**services_data.get('rag', {'host': 'localhost', 'port': 50057}))
        )
        
        # 处理Kafka配置
        kafka_data = data.get('kafka')
        kafka_config = None
        if kafka_data:
            kafka_config = KafkaConfig(
                broker=kafka_data.get('broker', 'localhost:9092'),
                topics=kafka_data.get('topics', {}),
                consumer_group=kafka_data.get('consumer_group', 'medical-service'),
                auto_commit=kafka_data.get('auto_commit', True),
                auto_commit_interval_ms=kafka_data.get('auto_commit_interval_ms', 5000)
            )
        
        # 处理可观测性配置
        observability_data = data.get('observability', {})
        observability_config = ObservabilityConfig(
            log_level=observability_data.get('log_level', 'info'),
            log_format=observability_data.get('log_format', 'json'),
            enable_tracing=observability_data.get('enable_tracing', True),
            jaeger_endpoint=observability_data.get('jaeger_endpoint'),
            enable_metrics=observability_data.get('enable_metrics', True),
            metrics_port=observability_data.get('metrics_port', 9090)
        )
        
        # 处理安全配置
        security_data = data.get('security', {})
        security_config = SecurityConfig(
            jwt_secret=security_data.get('jwt_secret'),
            jwt_algorithm=security_data.get('jwt_algorithm', 'HS256'),
            jwt_expiration_seconds=security_data.get('jwt_expiration_seconds', 3600 * 24),
            enable_api_key=security_data.get('enable_api_key', False),
            api_keys=security_data.get('api_keys', [])
        )
        
        return cls(
            server=server_config,
            database=database_config,
            services=services_config,
            kafka=kafka_config,
            observability=observability_config,
            security=security_config
        ) 