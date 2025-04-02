"""
检索相关的模型定义
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field


class BaseQuery(BaseModel):
    """基础查询模型"""
    query: str = Field(..., description="用户查询文本")
    limit: int = Field(10, description="返回结果的最大数量", ge=1, le=50)


class PrecisionMedicineQuery(BaseQuery):
    """精准医学查询模型"""
    study_type: Optional[str] = Field(None, description="研究类型")
    confidence_level: Optional[str] = Field(None, description="证据置信度级别")
    genes: Optional[List[str]] = Field(None, description="相关基因")
    diseases: Optional[List[str]] = Field(None, description="相关疾病")


class MultimodalHealthQuery(BaseQuery):
    """多模态健康数据查询模型"""
    modality_type: Optional[str] = Field(None, description="模态类型")
    features: Optional[List[str]] = Field(None, description="特征类型")
    metrics: Optional[List[str]] = Field(None, description="度量指标")


class EnvironmentalHealthQuery(BaseQuery):
    """环境健康查询模型"""
    factor_type: Optional[str] = Field(None, description="环境因素类型")
    exposure_routes: Optional[List[str]] = Field(None, description="暴露途径")
    temporal_pattern: Optional[str] = Field(None, description="时间模式")
    location: Optional[str] = Field(None, description="地理位置")


class MentalHealthQuery(BaseQuery):
    """心理健康查询模型"""
    psychology_domain: Optional[str] = Field(None, description="心理学领域")
    age_groups: Optional[List[str]] = Field(None, description="适用年龄组")
    techniques: Optional[List[str]] = Field(None, description="相关技术或方法")


class TCMQuery(BaseQuery):
    """中医养生特色查询模型"""
    constitution_type: Optional[str] = Field(None, description="体质类型")
    season: Optional[str] = Field(None, description="节气或季节")
    source_type: Optional[str] = Field(None, description="文献类型")
    keywords: Optional[List[str]] = Field(None, description="中医关键词")


class RetrievalResult(BaseModel):
    """检索结果项模型"""
    id: str
    title: str
    content: str
    summary: Optional[str] = None
    categories: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    similarity_score: Optional[float] = None
    final_score: Optional[float] = None
    node_type: Optional[str] = None
    # 其他可能的字段会在响应中动态包含


class RetrievalResponse(BaseModel):
    """检索响应模型"""
    results: List[Dict[str, Any]]
    count: int
    query: str
    domain: str