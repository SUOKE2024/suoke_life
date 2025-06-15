"""
健康相关模型
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class HealthData(BaseModel):
    """健康数据模型"""
    user_id: str = Field(..., description="用户ID")
    data_type: str = Field(..., description="数据类型")
    value: float = Field(..., description="数值")
    unit: str = Field(..., description="单位")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    source: Optional[str] = Field(default=None, description="数据来源")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="元数据")


class HealthAnalysis(BaseModel):
    """健康分析模型"""
    user_id: str = Field(..., description="用户ID")
    analysis_type: str = Field(..., description="分析类型")
    results: Dict[str, Any] = Field(..., description="分析结果")
    recommendations: List[str] = Field(default_factory=list, description="建议")
    risk_factors: Optional[List[str]] = Field(default=None, description="风险因素")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")


class HealthRecommendation(BaseModel):
    """健康建议模型"""
    user_id: str = Field(..., description="用户ID")
    category: str = Field(..., description="建议类别")
    title: str = Field(..., description="建议标题")
    description: str = Field(..., description="建议描述")
    priority: int = Field(ge=1, le=5, description="优先级")
    evidence: Optional[str] = Field(default=None, description="依据")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
