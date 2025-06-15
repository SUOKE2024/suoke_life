"""
应用配置管理

基于Pydantic Settings的现代配置管理系统。
"""
import os
from functools import lru_cache
from typing import List, Optional, Dict, Any
from pathlib import Path

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类"""
    
    # 基础配置
    environment: str = Field(default="development", description="运行环境")
    debug: bool = Field(default=True, description="调试模式")
    
    # 服务配置
    host: str = Field(default="127.0.0.1", description="服务主机")
    port: int = Field(default=8000, description="服务端口")
    workers: int = Field(default=1, description="工作进程数")
    
    # 数据库配置
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:password@localhost:5432/suoke_auth",
        description="数据库连接URL"
    )
    database_pool_size: int = Field(default=10, description="数据库连接池大小")
    database_max_overflow: int = Field(default=20, description="数据库连接池最大溢出")
    
    # 数据库连接池配置
    db_pool_min_size: int = Field(default=5, description="数据库连接池最小连接数")
    db_pool_max_size: int = Field(default=20, description="数据库连接池最大连接数")
    db_pool_max_queries: int = Field(default=50000, description="每个连接最大查询数")
    db_pool_max_inactive_time: float = Field(default=300.0, description="连接最大空闲时间（秒）")
    db_command_timeout: float = Field(default=30.0, description="数据库命令超时时间（秒）")
    
    # 速率限制配置
    rate_limit_enabled: bool = Field(default=True, description="是否启用速率限制")
    rate_limit_storage: str = Field(default="redis", description="速率限制存储类型")
    rate_limit_redis_url: Optional[str] = Field(default=None, description="速率限制Redis URL")
    
    # Redis缓存配置
    redis_enabled: bool = Field(default=True, description="是否启用Redis缓存")
    redis_url: Optional[str] = Field(default=None, description="Redis连接URL")
    redis_host: str = Field(default="localhost", description="Redis主机")
    redis_port: int = Field(default=6379, description="Redis端口")
    redis_db: int = Field(default=0, description="Redis数据库编号")
    redis_password: Optional[str] = Field(default=None, description="Redis密码")
    redis_max_connections: int = Field(default=20, description="Redis最大连接数")
    redis_socket_timeout: float = Field(default=5.0, description="Redis套接字超时")
    redis_socket_connect_timeout: float = Field(default=5.0, description="Redis连接超时")
    
    # 查询优化配置
    query_cache_enabled: bool = Field(default=True, description="是否启用查询缓存")
    query_cache_ttl: int = Field(default=300, description="查询缓存TTL（秒）")
    slow_query_threshold: float = Field(default=1.0, description="慢查询阈值（秒）")
    
    # 异步任务配置
    task_manager_enabled: bool = Field(default=True, description="是否启用任务管理器")
    task_queue_max_workers: int = Field(default=5, description="任务队列最大工作器数")
    task_default_timeout: float = Field(default=300.0, description="任务默认超时时间")
    task_max_retries: int = Field(default=3, description="任务最大重试次数")
    
    # 性能监控配置
    monitoring_enabled: bool = Field(default=True, description="是否启用性能监控")
    monitoring_interval: int = Field(default=30, description="监控检查间隔（秒）")
    
    # 邮件服务配置（用于异步任务）
    smtp_host: Optional[str] = Field(default=None, description="SMTP服务器主机")
    smtp_port: int = Field(default=587, description="SMTP服务器端口")
    smtp_username: Optional[str] = Field(default=None, description="SMTP用户名")
    smtp_password: Optional[str] = Field(default=None, description="SMTP密码")
    smtp_use_tls: bool = Field(default=True, description="是否使用TLS")
    smtp_from_email: Optional[str] = Field(default=None, description="发件人邮箱")
    
    # 邮件配置
    mail_from: str = Field(default="noreply@suokelife.com", description="发件人邮箱")
    mail_from_name: str = Field(default="索克生活", description="发件人名称")
    
    # 短信配置
    twilio_account_sid: str = Field(default="", description="Twilio账户SID")
    twilio_auth_token: str = Field(default="", description="Twilio认证令牌")
    twilio_phone_number: str = Field(default="", description="Twilio电话号码")
    
    # CORS配置
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="CORS允许的源"
    )
    cors_allow_credentials: bool = Field(default=True, description="CORS允许凭证")
    
    # JWT配置
    jwt_secret_key: str = Field(default="your-secret-key-change-in-production", description="JWT密钥")
    jwt_algorithm: str = Field(default="RS256", description="JWT算法")
    jwt_access_token_expire_minutes: int = Field(default=30, description="访问令牌过期时间（分钟）")
    jwt_refresh_token_expire_days: int = Field(default=7, description="刷新令牌过期时间（天）")
    jwt_private_key_path: Optional[str] = Field(default=None, description="JWT私钥文件路径")
    jwt_public_key_path: Optional[str] = Field(default=None, description="JWT公钥文件路径")
    jwt_private_key: Optional[str] = Field(default=None, description="JWT私钥内容")
    jwt_public_key: Optional[str] = Field(default=None, description="JWT公钥内容")
    
    # 密码策略配置
    password_min_length: int = Field(default=8, description="密码最小长度")
    password_require_uppercase: bool = Field(default=True, description="密码是否需要大写字母")
    password_require_lowercase: bool = Field(default=True, description="密码是否需要小写字母")
    password_require_numbers: bool = Field(default=True, description="密码是否需要数字")
    password_require_special: bool = Field(default=True, description="密码是否需要特殊字符")
    
    # 数据库详细配置
    db_host: str = Field(default="localhost", description="数据库主机")
    db_port: int = Field(default=5432, description="数据库端口")
    db_name: str = Field(default="suoke_auth", description="数据库名称")
    db_username: str = Field(default="postgres", description="数据库用户名")
    db_password: str = Field(default="password", description="数据库密码")
    db_pool_size: int = Field(default=10, description="数据库连接池大小")
    db_max_overflow: int = Field(default=20, description="数据库连接池最大溢出")
    
    # 安全配置
    rate_limit_requests: int = Field(default=100, description="速率限制请求数")
    rate_limit_window: int = Field(default=60, description="速率限制时间窗口（秒）")
    max_login_attempts: int = Field(default=5, description="最大登录尝试次数")
    account_lockout_duration: int = Field(default=300, description="账户锁定时长（秒）")
    
    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日志格式"
    )
    
    # 监控配置
    enable_metrics: bool = Field(default=True, description="启用指标收集")
    metrics_port: int = Field(default=9090, description="指标端口")
    
    # 缓存配置
    cache_ttl: int = Field(default=300, description="缓存TTL（秒）")
    cache_max_size: int = Field(default=1000, description="缓存最大大小")
    
    # 前端配置
    frontend_url: str = Field(default="http://localhost:3000", description="前端应用URL")
    
    # 服务发现配置
    service_discovery_enabled: bool = Field(default=True, description="是否启用服务发现")
    service_name: str = Field(default="auth-service", description="服务名称")
    service_version: str = Field(default="1.0.0", description="服务版本")
    service_health_check_url: str = Field(default="/health", description="健康检查URL")
    service_health_check_interval: int = Field(default=30, description="健康检查间隔（秒）")
    
    # gRPC配置
    grpc_enabled: bool = Field(default=True, description="是否启用gRPC")
    grpc_port: int = Field(default=50051, description="gRPC端口")
    grpc_max_workers: int = Field(default=10, description="gRPC最大工作器数")
    grpc_max_connections: int = Field(default=5, description="gRPC客户端最大连接数")
    grpc_keepalive_time: int = Field(default=30, description="gRPC保活时间（秒）")
    grpc_keepalive_timeout: int = Field(default=5, description="gRPC保活超时（秒）")
    
    # 高可用配置
    ha_enabled: bool = Field(default=True, description="是否启用高可用")
    ha_node_role: str = Field(default="secondary", description="节点角色: primary, secondary, witness")
    ha_node_priority: int = Field(default=1, description="节点优先级")
    ha_cluster_name: str = Field(default="auth-service-cluster", description="集群名称")
    ha_heartbeat_interval: int = Field(default=10, description="心跳间隔（秒）")
    ha_election_timeout: int = Field(default=30, description="选举超时（秒）")
    ha_failover_timeout: int = Field(default=60, description="故障转移超时（秒）")
    
    # 负载均衡配置
    load_balance_strategy: str = Field(default="round_robin", description="负载均衡策略")
    
    # 性能测试配置
    performance_test_enabled: bool = Field(default=False, description="是否启用性能测试")
    performance_test_concurrent_users: int = Field(default=10, description="性能测试并发用户数")
    performance_test_duration: int = Field(default=60, description="性能测试持续时间（秒）")
    performance_test_base_url: str = Field(default="http://localhost:8000", description="性能测试基础URL")
    
    # 服务器配置
    server_port: int = Field(default=8000, description="服务器端口")
    server_host: str = Field(default="0.0.0.0", description="服务器主机")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @validator("environment")
    def validate_environment(cls, v):
        """验证环境配置"""
        allowed = ["development", "testing", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"环境必须是以下之一: {allowed}")
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v):
        """验证日志级别"""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"日志级别必须是以下之一: {allowed}")
        return v.upper()
    
    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.environment == "production"
    
    @property
    def is_testing(self) -> bool:
        """是否为测试环境"""
        return self.environment == "testing"


# 全局配置实例
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """重新加载配置"""
    global _settings
    _settings = Settings()
    return _settings


@lru_cache()
def get_settings_cached() -> Settings:
    """获取配置实例（单例模式）"""
    return Settings() 