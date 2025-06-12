"""
望诊服务数据模型

定义与望诊服务交互的数据结构
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class ImageType(str, Enum):
    """图像类型"""
    FACE = "face"           # 面部图像
    TONGUE = "tongue"       # 舌诊图像
    BODY = "body"          # 体态图像
    SKIN = "skin"          # 皮肤图像
    EYE = "eye"            # 眼部图像


class LookAnalysisRequest(BaseModel):
    """望诊分析请求"""
    user_id: str = Field(description="用户ID")
    session_id: str = Field(description="会话ID")
    image_data: bytes = Field(description="图像数据")
    image_type: ImageType = Field(description="图像类型")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class FacialFeatures(BaseModel):
    """面部特征"""
    complexion: str = Field(description="面色")
    expression: str = Field(description="神情")
    facial_shape: str = Field(description="面型")
    eye_condition: str = Field(description="眼部状态")
    lip_condition: str = Field(description="唇部状态")
    confidence: float = Field(ge=0.0, le=1.0, description="置信度")


class TongueFeatures(BaseModel):
    """舌诊特征"""
    tongue_color: str = Field(description="舌色")
    tongue_coating: str = Field(description="苔色")
    tongue_texture: str = Field(description="舌质")
    tongue_shape: str = Field(description="舌形")
    tongue_moisture: str = Field(description="润燥")
    confidence: float = Field(ge=0.0, le=1.0, description="置信度")


class BodyPosture(BaseModel):
    """体态特征"""
    posture: str = Field(description="体态")
    body_shape: str = Field(description="体型")
    movement: str = Field(description="动作")
    gait: Optional[str] = Field(default=None, description="步态")
    confidence: float = Field(ge=0.0, le=1.0, description="置信度")


class SkinCondition(BaseModel):
    """皮肤状态"""
    skin_color: str = Field(description="肤色")
    skin_texture: str = Field(description="肌理")
    moisture: str = Field(description="润燥")
    elasticity: str = Field(description="弹性")
    lesions: List[str] = Field(default_factory=list, description="皮损")
    confidence: float = Field(ge=0.0, le=1.0, description="置信度")


class LookAnalysisResponse(BaseModel):
    """望诊分析响应"""
    confidence: float = Field(ge=0.0, le=1.0, description="总体置信度")
    image_type: ImageType = Field(description="图像类型")
    
    # 不同类型的分析结果
    facial_features: Optional[FacialFeatures] = Field(default=None, description="面部特征")
    tongue_features: Optional[TongueFeatures] = Field(default=None, description="舌诊特征")
    body_posture: Optional[BodyPosture] = Field(default=None, description="体态特征")
    skin_condition: Optional[SkinCondition] = Field(default=None, description="皮肤状态")
    
    # 通用分析结果
    features: Dict[str, Any] = Field(default_factory=dict, description="提取的特征")
    analysis_results: Dict[str, Any] = Field(default_factory=dict, description="分析结果")
    recommendations: List[str] = Field(default_factory=list, description="建议")
    
    # 元数据
    processing_time: float = Field(description="处理时间(秒)")
    model_version: str = Field(description="模型版本")
    timestamp: str = Field(description="分析时间戳")


# 新的简化模型，用于重构后的客户端
class LookRequest(BaseModel):
    """望诊请求（简化版）"""
    image_data: bytes = Field(description="图像数据")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class LookResponse(BaseModel):
    """望诊响应（简化版）"""
    confidence: float = Field(ge=0.0, le=1.0, description="置信度")
    features: Dict[str, Any] = Field(default_factory=dict, description="提取的特征")
    analysis_results: Dict[str, Any] = Field(default_factory=dict, description="分析结果")
    recommendations: List[str] = Field(default_factory=list, description="建议")
    processing_time: Optional[float] = Field(default=None, description="处理时间(秒)")
    timestamp: Optional[str] = Field(default=None, description="分析时间戳") 