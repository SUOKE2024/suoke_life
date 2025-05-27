#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
索克生活人工审核系统生产环境配置
Suoke Life Human Review System Production Configuration

生产环境的完整配置文件，包含数据库、安全、监控等设置
"""

import os
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    """数据库配置"""
    host: str = os.getenv('DB_HOST', 'localhost')
    port: int = int(os.getenv('DB_PORT', '5432'))
    database: str = os.getenv('DB_NAME', 'suoke_review')
    username: str = os.getenv('DB_USER', 'suoke_user')
    password: str = os.getenv('DB_PASSWORD', 'secure_password_123')
    pool_size: int = int(os.getenv('DB_POOL_SIZE', '20'))
    max_overflow: int = int(os.getenv('DB_MAX_OVERFLOW', '30'))
    pool_timeout: int = int(os.getenv('DB_POOL_TIMEOUT', '30'))
    pool_recycle: int = int(os.getenv('DB_POOL_RECYCLE', '3600'))
    
    @property
    def url(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class RedisConfig:
    """Redis配置"""
    host: str = os.getenv('REDIS_HOST', 'localhost')
    port: int = int(os.getenv('REDIS_PORT', '6379'))
    password: str = os.getenv('REDIS_PASSWORD', '')
    db: int = int(os.getenv('REDIS_DB', '0'))
    max_connections: int = int(os.getenv('REDIS_MAX_CONNECTIONS', '50'))
    
    @property
    def url(self) -> str:
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"


@dataclass
class SecurityConfig:
    """安全配置"""
    secret_key: str = os.getenv('SECRET_KEY', 'suoke-life-human-review-secret-key-2024')
    jwt_secret: str = os.getenv('JWT_SECRET', 'jwt-secret-for-suoke-review-system')
    jwt_expiration: int = int(os.getenv('JWT_EXPIRATION', '86400'))  # 24小时
    password_salt: str = os.getenv('PASSWORD_SALT', 'suoke-review-salt')
    encryption_key: str = os.getenv('ENCRYPTION_KEY', 'encryption-key-for-sensitive-data')
    
    # HTTPS配置
    ssl_cert_path: str = os.getenv('SSL_CERT_PATH', '/etc/ssl/certs/suoke.crt')
    ssl_key_path: str = os.getenv('SSL_KEY_PATH', '/etc/ssl/private/suoke.key')
    
    # CORS配置
    cors_origins: list = os.getenv('CORS_ORIGINS', 'https://suoke.life,https://review.suoke.life').split(',')
    
    # 审核员访问控制
    reviewer_ip_whitelist: list = os.getenv('REVIEWER_IP_WHITELIST', '').split(',') if os.getenv('REVIEWER_IP_WHITELIST') else []


@dataclass
class MonitoringConfig:
    """监控配置"""
    # Prometheus配置
    prometheus_host: str = os.getenv('PROMETHEUS_HOST', 'localhost')
    prometheus_port: int = int(os.getenv('PROMETHEUS_PORT', '9090'))
    metrics_port: int = int(os.getenv('METRICS_PORT', '8000'))
    
    # Grafana配置
    grafana_host: str = os.getenv('GRAFANA_HOST', 'localhost')
    grafana_port: int = int(os.getenv('GRAFANA_PORT', '3000'))
    
    # 日志配置
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
    log_file: str = os.getenv('LOG_FILE', '/var/log/suoke/review.log')
    log_max_size: str = os.getenv('LOG_MAX_SIZE', '100MB')
    log_backup_count: int = int(os.getenv('LOG_BACKUP_COUNT', '10'))
    
    # 告警配置
    alert_webhook_url: str = os.getenv('ALERT_WEBHOOK_URL', '')
    alert_email: str = os.getenv('ALERT_EMAIL', 'admin@suoke.life')


@dataclass
class A2AConfig:
    """A2A智能体配置"""
    # 智能体服务地址
    xiaoai_url: str = os.getenv('XIAOAI_URL', 'http://localhost:8001')
    xiaoke_url: str = os.getenv('XIAOKE_URL', 'http://localhost:8002')
    laoke_url: str = os.getenv('LAOKE_URL', 'http://localhost:8003')
    soer_url: str = os.getenv('SOER_URL', 'http://localhost:8004')
    
    # 审核智能体配置
    review_agent_host: str = os.getenv('REVIEW_AGENT_HOST', '0.0.0.0')
    review_agent_port: int = int(os.getenv('REVIEW_AGENT_PORT', '8080'))
    
    # 超时配置
    request_timeout: int = int(os.getenv('A2A_REQUEST_TIMEOUT', '30'))
    max_retries: int = int(os.getenv('A2A_MAX_RETRIES', '3'))


@dataclass
class ReviewConfig:
    """审核系统配置"""
    # 审核队列配置
    max_queue_size: int = int(os.getenv('MAX_QUEUE_SIZE', '1000'))
    default_priority: str = os.getenv('DEFAULT_PRIORITY', 'normal')
    
    # 审核时间配置
    urgent_review_time: int = int(os.getenv('URGENT_REVIEW_TIME', '15'))  # 分钟
    high_review_time: int = int(os.getenv('HIGH_REVIEW_TIME', '30'))
    normal_review_time: int = int(os.getenv('NORMAL_REVIEW_TIME', '60'))
    low_review_time: int = int(os.getenv('LOW_REVIEW_TIME', '120'))
    
    # 自动审核配置
    auto_approve_threshold: float = float(os.getenv('AUTO_APPROVE_THRESHOLD', '0.8'))
    auto_reject_threshold: float = float(os.getenv('AUTO_REJECT_THRESHOLD', '0.3'))
    
    # 质量控制配置
    quality_check_ratio: float = float(os.getenv('QUALITY_CHECK_RATIO', '0.1'))  # 10%抽检
    min_reviewer_score: float = float(os.getenv('MIN_REVIEWER_SCORE', '0.9'))


@dataclass
class WebConfig:
    """Web服务配置"""
    # Flask配置
    host: str = os.getenv('WEB_HOST', '0.0.0.0')
    port: int = int(os.getenv('WEB_PORT', '5001'))
    debug: bool = os.getenv('WEB_DEBUG', 'False').lower() == 'true'
    
    # SocketIO配置
    socketio_cors_origins: str = os.getenv('SOCKETIO_CORS_ORIGINS', '*')
    socketio_ping_timeout: int = int(os.getenv('SOCKETIO_PING_TIMEOUT', '60'))
    socketio_ping_interval: int = int(os.getenv('SOCKETIO_PING_INTERVAL', '25'))
    
    # 静态文件配置
    static_folder: str = os.getenv('STATIC_FOLDER', '/var/www/suoke/static')
    upload_folder: str = os.getenv('UPLOAD_FOLDER', '/var/www/suoke/uploads')
    max_content_length: int = int(os.getenv('MAX_CONTENT_LENGTH', '16777216'))  # 16MB


@dataclass
class EmailConfig:
    """邮件配置"""
    smtp_server: str = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port: int = int(os.getenv('SMTP_PORT', '587'))
    smtp_username: str = os.getenv('SMTP_USERNAME', 'noreply@suoke.life')
    smtp_password: str = os.getenv('SMTP_PASSWORD', '')
    use_tls: bool = os.getenv('SMTP_USE_TLS', 'True').lower() == 'true'
    
    # 邮件模板配置
    from_email: str = os.getenv('FROM_EMAIL', 'noreply@suoke.life')
    admin_email: str = os.getenv('ADMIN_EMAIL', 'admin@suoke.life')


class ProductionConfig:
    """生产环境配置类"""
    
    def __init__(self):
        self.database = DatabaseConfig()
        self.redis = RedisConfig()
        self.security = SecurityConfig()
        self.monitoring = MonitoringConfig()
        self.a2a = A2AConfig()
        self.review = ReviewConfig()
        self.web = WebConfig()
        self.email = EmailConfig()
        
        # 环境标识
        self.environment = os.getenv('ENVIRONMENT', 'production')
        self.version = os.getenv('APP_VERSION', '1.0.0')
        self.build_id = os.getenv('BUILD_ID', 'unknown')
        
        # 验证配置
        self._validate_config()
    
    def _validate_config(self):
        """验证配置的有效性"""
        errors = []
        
        # 验证必需的环境变量
        required_vars = [
            'DB_PASSWORD',
            'SECRET_KEY',
            'JWT_SECRET'
        ]
        
        for var in required_vars:
            if not os.getenv(var):
                errors.append(f"缺少必需的环境变量: {var}")
        
        # 验证数据库连接
        if not self.database.host or not self.database.database:
            errors.append("数据库配置不完整")
        
        # 验证安全配置
        if len(self.security.secret_key) < 32:
            errors.append("SECRET_KEY长度不足，建议至少32个字符")
        
        if errors:
            raise ValueError(f"配置验证失败: {'; '.join(errors)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'environment': self.environment,
            'version': self.version,
            'build_id': self.build_id,
            'database': {
                'host': self.database.host,
                'port': self.database.port,
                'database': self.database.database,
                'pool_size': self.database.pool_size
            },
            'redis': {
                'host': self.redis.host,
                'port': self.redis.port,
                'db': self.redis.db
            },
            'web': {
                'host': self.web.host,
                'port': self.web.port,
                'debug': self.web.debug
            },
            'review': {
                'max_queue_size': self.review.max_queue_size,
                'auto_approve_threshold': self.review.auto_approve_threshold
            }
        }
    
    def get_database_url(self) -> str:
        """获取数据库连接URL"""
        return self.database.url
    
    def get_redis_url(self) -> str:
        """获取Redis连接URL"""
        return self.redis.url
    
    def is_production(self) -> bool:
        """判断是否为生产环境"""
        return self.environment.lower() == 'production'
    
    def is_debug(self) -> bool:
        """判断是否为调试模式"""
        return self.web.debug and not self.is_production()


# 全局配置实例
config = ProductionConfig()


def get_config() -> ProductionConfig:
    """获取配置实例"""
    return config


def load_config_from_file(config_file: str) -> ProductionConfig:
    """从文件加载配置"""
    import json
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # 将配置数据设置为环境变量
        for key, value in config_data.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    env_key = f"{key.upper()}_{sub_key.upper()}"
                    os.environ[env_key] = str(sub_value)
            else:
                os.environ[key.upper()] = str(value)
        
        # 重新创建配置实例
        return ProductionConfig()
        
    except Exception as e:
        raise ValueError(f"加载配置文件失败: {e}")


# 配置验证函数
def validate_production_environment():
    """验证生产环境配置"""
    try:
        config = get_config()
        
        print("🔍 验证生产环境配置...")
        print(f"环境: {config.environment}")
        print(f"版本: {config.version}")
        print(f"构建ID: {config.build_id}")
        
        # 验证数据库连接
        print(f"数据库: {config.database.host}:{config.database.port}/{config.database.database}")
        
        # 验证Redis连接
        print(f"Redis: {config.redis.host}:{config.redis.port}/{config.redis.db}")
        
        # 验证Web服务
        print(f"Web服务: {config.web.host}:{config.web.port}")
        
        print("✅ 配置验证通过")
        return True
        
    except Exception as e:
        print(f"❌ 配置验证失败: {e}")
        return False


if __name__ == "__main__":
    # 验证配置
    if validate_production_environment():
        print("\n📋 当前配置:")
        import json
        print(json.dumps(config.to_dict(), indent=2, ensure_ascii=False))
    else:
        exit(1) 