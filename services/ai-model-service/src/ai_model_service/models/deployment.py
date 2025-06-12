"""部署相关数据模型"""

from enum import Enum
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field


class DeploymentStatus(str, Enum):
    """部署状态枚举"""

    PENDING = "pending"
    DEPLOYING = "deploying"
    RUNNING = "running"
    FAILED = "failed"
    SCALING = "scaling"
    UPDATING = "updating"
    TERMINATING = "terminating"


class DeploymentInfo(BaseModel):
    """部署信息"""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
        protected_namespaces=(),
    )

    deployment_id: str = Field(..., description="部署唯一标识符")
    model_id: str = Field(..., description="模型标识符")
    status: DeploymentStatus = Field(..., description="部署状态")
    replicas: int = Field(..., ge=0, description="副本数量")
    ready_replicas: int = Field(..., ge=0, description="就绪副本数量")
    endpoint_url: str = Field(..., description="推理端点URL")
    created_at: float = Field(..., description="创建时间戳")
    updated_at: float = Field(..., description="更新时间戳")
    resource_usage: Dict[str, Any] = Field(
        default_factory=dict, description="资源使用情况"
    )
    performance_metrics: Dict[str, Any] = Field(
        default_factory=dict, description="性能指标"
    )

    @property
    def is_ready(self) -> bool:
        """检查部署是否就绪"""
        return self.status==DeploymentStatus.RUNNING and self.ready_replicas > 0

    @property
    def health_ratio(self) -> float:
        """计算健康副本比例"""
        if self.replicas==0:
            return 0.0
        return self.ready_replicas / self.replicas

    def __str__(self) -> str:
        return f"DeploymentInfo(id={self.deployment_id}, status={self.status}, replicas={self.ready_replicas}/{self.replicas})"

    def __repr__(self) -> str:
        return self.__str__()
