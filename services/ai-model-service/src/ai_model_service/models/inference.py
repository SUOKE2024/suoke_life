"""推理相关数据模型"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class InferenceRequest(BaseModel):
    """推理请求"""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
        protected_namespaces=(),
    )

    request_id: str = Field(..., description="请求唯一标识符")
    model_id: str = Field(..., description="模型标识符")
    input_data: Any = Field(..., description="输入数据")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="推理参数")
    timeout: int = Field(default=30, ge=1, le=300, description="超时时间(秒)")
    priority: str = Field(
        default="normal", description="优先级", examples=["low", "normal", "high"]
    )

    def __str__(self) -> str:
        return f"InferenceRequest(id={self.request_id}, model={self.model_id}, priority={self.priority})"

    def __repr__(self) -> str:
        return self.__str__()


class InferenceResult(BaseModel):
    """推理结果"""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
        protected_namespaces=(),
    )

    request_id: str = Field(..., description="请求标识符")
    model_id: str = Field(..., description="模型标识符")
    result: Any = Field(..., description="推理结果")
    confidence: float = Field(..., ge=0.0, le=1.0, description="置信度")
    processing_time: float = Field(..., ge=0.0, description="处理时间(毫秒)")
    model_version: str = Field(..., description="模型版本")
    resource_usage: Dict[str, Any] = Field(
        default_factory=dict, description="资源使用情况"
    )
    error_message: Optional[str] = Field(default=None, description="错误信息")

    @property
    def is_success(self) -> bool:
        """检查推理是否成功"""
        return self.error_message is None

    def __str__(self) -> str:
        status = "success" if self.is_success else "failed"
        return f"InferenceResult(id={self.request_id}, status={status}, time={self.processing_time:.2f}ms)"

    def __repr__(self) -> str:
        return self.__str__()
