"""
索克生活事件驱动架构配置管理
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class EventPriority(Enum):
    """事件优先级"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class RetryPolicy(Enum):
    """重试策略"""

    NO_RETRY = "no_retry"
    LINEAR_BACKOFF = "linear_backoff"
    EXPONENTIAL_BACKOFF = "exponential_backoff"


@dataclass
class RedisConfig:
    """Redis配置"""

    url: str = field(
        default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379/0")
    )
    max_connections: int = field(
        default_factory=lambda: int(os.getenv("REDIS_MAX_CONNECTIONS", "20"))
    )
    retry_on_timeout: bool = True
    socket_keepalive: bool = True
    health_check_interval: int = 30


@dataclass
class DatabaseConfig:
    """数据库配置"""

    url: str = field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL", "postgresql://suoke:suoke123@localhost:5432/suoke_db"
        )
    )
    min_pool_size: int = field(
        default_factory=lambda: int(os.getenv("DB_MIN_POOL_SIZE", "5"))
    )
    max_pool_size: int = field(
        default_factory=lambda: int(os.getenv("DB_MAX_POOL_SIZE", "20"))
    )
    command_timeout: int = field(
        default_factory=lambda: int(os.getenv("DB_COMMAND_TIMEOUT", "60"))
    )


@dataclass
class EventBusConfig:
    """事件总线配置"""

    service_name: str = field(
        default_factory=lambda: os.getenv("SERVICE_NAME", "suoke-event-bus")
    )
    max_event_size: int = field(
        default_factory=lambda: int(os.getenv("MAX_EVENT_SIZE", "1048576"))
    )  # 1MB
    batch_size: int = field(
        default_factory=lambda: int(os.getenv("EVENT_BATCH_SIZE", "100"))
    )
    flush_interval: int = field(
        default_factory=lambda: int(os.getenv("EVENT_FLUSH_INTERVAL", "5"))
    )  # 秒
    enable_metrics: bool = field(
        default_factory=lambda: os.getenv("ENABLE_METRICS", "true").lower() == "true"
    )
    metrics_port: int = field(
        default_factory=lambda: int(os.getenv("METRICS_PORT", "8000"))
    )


@dataclass
class EventStoreConfig:
    """事件存储配置"""

    retention_days: int = field(
        default_factory=lambda: int(os.getenv("EVENT_RETENTION_DAYS", "90"))
    )
    cleanup_interval_hours: int = field(
        default_factory=lambda: int(os.getenv("CLEANUP_INTERVAL_HOURS", "24"))
    )
    enable_snapshots: bool = field(
        default_factory=lambda: os.getenv("ENABLE_SNAPSHOTS", "true").lower() == "true"
    )
    snapshot_interval: int = field(
        default_factory=lambda: int(os.getenv("SNAPSHOT_INTERVAL", "100"))
    )  # 每100个事件


@dataclass
class CacheConfig:
    """缓存配置"""

    default_ttl: int = field(
        default_factory=lambda: int(os.getenv("CACHE_DEFAULT_TTL", "3600"))
    )  # 1小时
    max_memory_usage: str = field(
        default_factory=lambda: os.getenv("CACHE_MAX_MEMORY", "512mb")
    )
    eviction_policy: str = field(
        default_factory=lambda: os.getenv("CACHE_EVICTION_POLICY", "allkeys-lru")
    )

    # 不同数据类型的缓存策略
    cache_strategies: Dict[str, Dict[str, Any]] = field(
        default_factory=lambda: {
            "vital_signs": {"ttl": 300, "strategy": "latest"},  # 5分钟
            "diagnostic_results": {"ttl": 3600, "strategy": "versioned"},  # 1小时
            "tcm_data": {"ttl": 1800, "strategy": "latest"},  # 30分钟
            "user_profile": {"ttl": 7200, "strategy": "versioned"},  # 2小时
            "aggregated_stats": {"ttl": 1800, "strategy": "computed"},  # 30分钟
            "alerts": {"ttl": 600, "strategy": "latest"},  # 10分钟
        }
    )


@dataclass
class AgentConfig:
    """智能体配置"""

    # 智能体超时设置
    timeouts: Dict[str, int] = field(
        default_factory=lambda: {
            "look": 300,  # 望诊 5分钟
            "listen": 300,  # 闻诊 5分钟
            "inquiry": 600,  # 问诊 10分钟
            "palpation": 300,  # 切诊 5分钟
            "syndrome_differentiation": 180,  # 辨证论治 3分钟
        }
    )

    # 智能体优先级
    priorities: Dict[str, int] = field(
        default_factory=lambda: {
            "xiaoai": 1,  # 望诊优先级最高
            "xiaoke": 2,  # 闻诊
            "laoke": 3,  # 问诊
            "soer": 4,  # 切诊
        }
    )

    # 并发设置
    max_concurrent_sessions: int = field(
        default_factory=lambda: int(os.getenv("MAX_CONCURRENT_SESSIONS", "10"))
    )
    enable_parallel_diagnosis: bool = field(
        default_factory=lambda: os.getenv("ENABLE_PARALLEL_DIAGNOSIS", "false").lower()
        == "true"
    )

    # 重试设置
    max_retries: int = field(
        default_factory=lambda: int(os.getenv("AGENT_MAX_RETRIES", "3"))
    )
    retry_delay: int = field(
        default_factory=lambda: int(os.getenv("AGENT_RETRY_DELAY", "5"))
    )  # 秒


@dataclass
class HealthDataConfig:
    """健康数据配置"""

    # 数据质量阈值
    quality_thresholds: Dict[str, Dict[str, float]] = field(
        default_factory=lambda: {
            "heart_rate": {"min": 40, "max": 200},
            "blood_pressure_systolic": {"min": 70, "max": 250},
            "blood_pressure_diastolic": {"min": 40, "max": 150},
            "temperature": {"min": 35.0, "max": 42.0},
            "oxygen_saturation": {"min": 70, "max": 100},
        }
    )

    # 异常检测规则
    anomaly_rules: Dict[str, Any] = field(
        default_factory=lambda: {
            "heart_rate_high": 100,
            "heart_rate_low": 60,
            "blood_pressure_high": {"systolic": 140, "diastolic": 90},
            "blood_pressure_low": {"systolic": 90, "diastolic": 60},
            "fever_threshold": 37.5,
            "oxygen_low": 95,
        }
    )

    # 数据同步设置
    sync_interval: int = field(
        default_factory=lambda: int(os.getenv("DATA_SYNC_INTERVAL", "60"))
    )  # 秒
    batch_sync_size: int = field(
        default_factory=lambda: int(os.getenv("BATCH_SYNC_SIZE", "100"))
    )
    enable_real_time_sync: bool = field(
        default_factory=lambda: os.getenv("ENABLE_REAL_TIME_SYNC", "true").lower()
        == "true"
    )


@dataclass
class SecurityConfig:
    """安全配置"""

    enable_encryption: bool = field(
        default_factory=lambda: os.getenv("ENABLE_ENCRYPTION", "true").lower() == "true"
    )
    encryption_key: str = field(default_factory=lambda: os.getenv("ENCRYPTION_KEY", ""))
    enable_audit_log: bool = field(
        default_factory=lambda: os.getenv("ENABLE_AUDIT_LOG", "true").lower() == "true"
    )
    max_event_age_hours: int = field(
        default_factory=lambda: int(os.getenv("MAX_EVENT_AGE_HOURS", "24"))
    )

    # 访问控制
    allowed_sources: List[str] = field(
        default_factory=lambda: (
            os.getenv("ALLOWED_SOURCES", "").split(",")
            if os.getenv("ALLOWED_SOURCES")
            else []
        )
    )
    rate_limit_per_minute: int = field(
        default_factory=lambda: int(os.getenv("RATE_LIMIT_PER_MINUTE", "1000"))
    )


@dataclass
class MonitoringConfig:
    """监控配置"""

    enable_health_checks: bool = field(
        default_factory=lambda: os.getenv("ENABLE_HEALTH_CHECKS", "true").lower()
        == "true"
    )
    health_check_interval: int = field(
        default_factory=lambda: int(os.getenv("HEALTH_CHECK_INTERVAL", "30"))
    )  # 秒

    enable_performance_monitoring: bool = field(
        default_factory=lambda: os.getenv(
            "ENABLE_PERFORMANCE_MONITORING", "true"
        ).lower()
        == "true"
    )
    performance_sample_rate: float = field(
        default_factory=lambda: float(os.getenv("PERFORMANCE_SAMPLE_RATE", "0.1"))
    )

    # 告警阈值
    alert_thresholds: Dict[str, Any] = field(
        default_factory=lambda: {
            "event_processing_delay_ms": 5000,  # 5秒
            "failed_event_rate": 0.05,  # 5%
            "memory_usage_percent": 80,  # 80%
            "cpu_usage_percent": 80,  # 80%
            "disk_usage_percent": 90,  # 90%
        }
    )


@dataclass
class SuokeEventConfig:
    """索克生活事件驱动架构总配置"""

    redis: RedisConfig = field(default_factory=RedisConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    event_bus: EventBusConfig = field(default_factory=EventBusConfig)
    event_store: EventStoreConfig = field(default_factory=EventStoreConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    agents: AgentConfig = field(default_factory=AgentConfig)
    health_data: HealthDataConfig = field(default_factory=HealthDataConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)

    # 环境设置
    environment: str = field(
        default_factory=lambda: os.getenv("ENVIRONMENT", "development")
    )
    debug: bool = field(
        default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true"
    )
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))


# 全局配置实例
_global_config: SuokeEventConfig = None


def get_config() -> SuokeEventConfig:
    """获取全局配置"""
    global _global_config
    if _global_config is None:
        _global_config = SuokeEventConfig()
    return _global_config


def load_config_from_file(config_file: str) -> SuokeEventConfig:
    """从文件加载配置"""
    import json

    import yaml

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            if config_file.endswith(".json"):
                json.load(f)
            elif config_file.endswith((".yml", ".yaml")):
                yaml.safe_load(f)
            else:
                raise ValueError(f"不支持的配置文件格式: {config_file}")

        # 这里可以添加配置数据到dataclass的转换逻辑
        # 暂时返回默认配置
        return SuokeEventConfig()

    except Exception as e:
        print(f"加载配置文件失败: {e}")
        return SuokeEventConfig()


def validate_config(config: SuokeEventConfig) -> List[str]:
    """验证配置"""
    errors = []

    # 验证Redis配置
    if not config.redis.url:
        errors.append("Redis URL不能为空")

    # 验证数据库配置
    if not config.database.url:
        errors.append("数据库URL不能为空")

    # 验证事件总线配置
    if config.event_bus.max_event_size <= 0:
        errors.append("最大事件大小必须大于0")

    # 验证智能体配置
    if config.agents.max_concurrent_sessions <= 0:
        errors.append("最大并发会话数必须大于0")

    # 验证安全配置
    if config.security.enable_encryption and not config.security.encryption_key:
        errors.append("启用加密时必须提供加密密钥")

    return errors


# 配置预设
class ConfigPresets:
    """配置预设"""

    @staticmethod
    def development() -> SuokeEventConfig:
        """开发环境配置"""
        config = SuokeEventConfig()
        config.environment = "development"
        config.debug = True
        config.log_level = "DEBUG"
        config.event_store.retention_days = 7  # 开发环境只保留7天
        config.security.enable_encryption = False  # 开发环境关闭加密
        return config

    @staticmethod
    def testing() -> SuokeEventConfig:
        """测试环境配置"""
        config = SuokeEventConfig()
        config.environment = "testing"
        config.debug = True
        config.log_level = "DEBUG"
        config.event_store.retention_days = 1  # 测试环境只保留1天
        config.cache.default_ttl = 60  # 测试环境缓存时间短
        return config

    @staticmethod
    def production() -> SuokeEventConfig:
        """生产环境配置"""
        config = SuokeEventConfig()
        config.environment = "production"
        config.debug = False
        config.log_level = "INFO"
        config.security.enable_encryption = True
        config.security.enable_audit_log = True
        config.monitoring.enable_performance_monitoring = True
        return config


# 使用示例
if __name__ == "__main__":
    # 获取默认配置
    config = get_config()
    print(f"环境: {config.environment}")
    print(f"Redis URL: {config.redis.url}")
    print(f"数据库 URL: {config.database.url}")

    # 验证配置
    errors = validate_config(config)
    if errors:
        print("配置错误:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("配置验证通过")
