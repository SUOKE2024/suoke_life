"""模型配置相关数据模型"""

from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field


class ModelType(str, Enum):
    """模型类型枚举"""

    LLM = "llm"
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    TCM_DIAGNOSIS = "tcm_diagnosis"
    MULTIMODAL = "multimodal"
    KNOWLEDGE_GRAPH = "knowledge_graph"


class ModelConfig(BaseModel):
    """云端模型配置"""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
        protected_namespaces=(),
    )

    model_id: str = Field(..., description="模型唯一标识符")
    name: str = Field(..., description="模型名称")
    version: str = Field(..., description="模型版本")
    model_type: ModelType = Field(..., description="模型类型")
    framework: str = Field(
        ...,
        description="AI框架",
        examples=["pytorch", "tensorflow", "huggingface", "onnx"],
    )
    repository_url: str = Field(..., description="模型仓库URL")
    docker_image: str = Field(..., description="Docker镜像地址")
    resource_requirements: Dict[str, Any] = Field(..., description="资源需求配置")
    scaling_config: Dict[str, Any] = Field(..., description="扩缩容配置")
    health_check: Dict[str, Any] = Field(..., description="健康检查配置")
    environment_variables: Dict[str, str] = Field(
        default_factory=dict, description="环境变量"
    )
    capabilities: List[str] = Field(default_factory=list, description="模型能力列表")

    def __str__(self) -> str:
        return (
            f"ModelConfig(id={self.model_id}, name={self.name}, version={self.version})"
        )

    def __repr__(self) -> str:
        return self.__str__()
