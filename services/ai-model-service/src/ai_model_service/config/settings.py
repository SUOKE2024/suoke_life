"""应用设置配置"""

from functools import lru_cache
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class KubernetesConfig(BaseModel):
    """Kubernetes配置"""

    namespace: str = Field(default="suoke-life", description="Kubernetes命名空间")
    config_path: Optional[str] = Field(default=None, description="kubeconfig文件路径")
    in_cluster: bool = Field(default=False, description="是否在集群内运行")
    timeout: int = Field(default=60, description="API超时时间(秒)")


class ModelRegistryConfig(BaseModel):
    """模型注册表配置"""

    url: str = Field(default="registry.suoke.life", description="模型注册表URL")
    username: Optional[str] = Field(default=None, description="用户名")
    password: Optional[str] = Field(default=None, description="密码")
    namespace: str = Field(default="suoke", description="镜像命名空间")


class MonitoringConfig(BaseModel):
    """监控配置"""

    enabled: bool = Field(default=True, description="是否启用监控")
    metrics_port: int = Field(default=9090, description="指标端口")
    health_check_interval: int = Field(default=30, description="健康检查间隔(秒)")
    log_level: str = Field(default="INFO", description="日志级别")
    json_logs: bool = Field(default=False, description="是否使用JSON格式日志")


class SecurityConfig(BaseModel):
    """安全配置"""

    enable_auth: bool = Field(default=True, description="是否启用认证")
    jwt_secret: Optional[str] = Field(default=None, description="JWT密钥")
    api_key: Optional[str] = Field(default=None, description="API密钥")
    allowed_origins: list[str] = Field(
        default_factory=lambda: ["*"], description="允许的CORS源"
    )


class Settings(BaseSettings):
    """应用设置"""

    # 基本设置
    app_name: str = Field(default="AI Model Service", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本")
    debug: bool = Field(default=False, description="调试模式")

    # 服务设置
    host: str = Field(default="0.0.0.0", description="服务主机")
    port: int = Field(default=8080, description="服务端口")
    workers: int = Field(default=1, description="工作进程数")

    # 组件配置
    kubernetes: KubernetesConfig = Field(default_factory=KubernetesConfig)
    model_registry: ModelRegistryConfig = Field(default_factory=ModelRegistryConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)

    # 模型默认配置
    default_model_resources: Dict[str, Any] = Field(
        default_factory=lambda: {"cpu": "1", "memory": "2Gi", "nvidia.com/gpu": "0"},
        description="默认模型资源配置",
    )

    default_scaling_config: Dict[str, Any] = Field(
        default_factory=lambda: {
            "min_replicas": 1,
            "max_replicas": 5,
            "target_cpu_utilization": 70,
        },
        description="默认扩缩容配置",
    )

    # 推理设置
    inference_timeout: int = Field(default=30, description="推理超时时间(秒)")
    max_batch_size: int = Field(default=32, description="最大批处理大小")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """获取应用设置单例

    Returns:
        应用设置实例
    """
    return Settings()
