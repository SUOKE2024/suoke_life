"""数据模型定义"""

from .config import ModelConfig, ModelType
from .deployment import DeploymentInfo, DeploymentStatus
from .inference import InferenceRequest, InferenceResult

__all__ = [
    "ModelConfig",
    "ModelType",
    "DeploymentInfo",
    "DeploymentStatus",
    "InferenceRequest",
    "InferenceResult",
]
