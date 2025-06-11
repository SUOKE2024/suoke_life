"""
AI Model Service - 索克生活AI模型云端部署和管理服务

专门负责大型AI模型的Kubernetes部署、版本管理、扩缩容和推理服务。
"""

__version__ = "1.0.0"
__author__ = "索克生活团队"
__email__ = "dev@suoke.life"

from .core.manager import CloudModelManager
from .models.config import ModelConfig, ModelType
from .models.deployment import DeploymentInfo, DeploymentStatus
from .models.inference import InferenceRequest, InferenceResult

__all__ = [
    "CloudModelManager",
    "ModelConfig",
    "ModelType",
    "DeploymentInfo",
    "DeploymentStatus",
    "InferenceRequest",
    "InferenceResult",
]
