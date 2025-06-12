"""
切诊服务数据模型

定义与切诊服务交互的数据结构
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PalpationRequest(BaseModel):
    """切诊请求"""

    pulse_data: Dict[str, Any] = Field(description="脉象数据")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class PalpationResponse(BaseModel):
    """切诊响应"""

    confidence: float = Field(ge=0.0, le=1.0, description="置信度")
    pulse_analysis: Dict[str, Any] = Field(default_factory=dict, description="脉象分析")
    analysis_results: Dict[str, Any] = Field(default_factory=dict, description="分析结果")
    recommendations: List[str] = Field(default_factory=list, description="建议")
    processing_time: Optional[float] = Field(default=None, description="处理时间(秒)")
    timestamp: Optional[str] = Field(default=None, description="分析时间戳")
