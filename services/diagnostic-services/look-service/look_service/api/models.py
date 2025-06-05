"""
API模型定义

定义望诊服务的请求和响应模型
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class LookDiagnosisRequest(BaseModel):
    """望诊分析请求模型"""
    
    user_id: str = Field(..., description="用户ID")
    image_data: str = Field(..., description="图像数据（base64编码）")
    image_type: str = Field(default="face", description="图像类型：face, tongue, eye等")
    analysis_type: List[str] = Field(default=["complexion", "tongue"], description="分析类型列表")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="额外的元数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
                "image_type": "face",
                "analysis_type": ["complexion", "tongue"],
                "metadata": {
                    "timestamp": "2024-01-01T12:00:00Z",
                    "device": "mobile"
                }
            }
        }


class FHIRObservationResponse(BaseModel):
    """FHIR Observation格式的响应模型"""
    
    resourceType: str = Field(default="Observation", description="FHIR资源类型")
    id: str = Field(..., description="观察记录ID")
    status: str = Field(default="final", description="观察状态")
    category: List[Dict[str, Any]] = Field(..., description="观察分类")
    code: Dict[str, Any] = Field(..., description="观察代码")
    subject: Dict[str, str] = Field(..., description="观察对象")
    effectiveDateTime: str = Field(..., description="观察时间")
    valueCodeableConcept: Optional[Dict[str, Any]] = Field(default=None, description="观察值（编码概念）")
    component: Optional[List[Dict[str, Any]]] = Field(default=None, description="观察组件")
    interpretation: Optional[List[Dict[str, Any]]] = Field(default=None, description="解释")
    note: Optional[List[Dict[str, str]]] = Field(default=None, description="备注")
    
    class Config:
        json_schema_extra = {
            "example": {
                "resourceType": "Observation",
                "id": "look-obs-123",
                "status": "final",
                "category": [
                    {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                                "code": "survey",
                                "display": "Survey"
                            }
                        ]
                    }
                ],
                "code": {
                    "coding": [
                        {
                            "system": "http://suoke.life/fhir/CodeSystem/tcm-observation",
                            "code": "look-diagnosis",
                            "display": "中医望诊"
                        }
                    ]
                },
                "subject": {
                    "reference": "Patient/user123"
                },
                "effectiveDateTime": "2024-01-01T12:00:00Z",
                "component": [
                    {
                        "code": {
                            "coding": [
                                {
                                    "system": "http://suoke.life/fhir/CodeSystem/tcm-look",
                                    "code": "complexion",
                                    "display": "面色"
                                }
                            ]
                        },
                        "valueCodeableConcept": {
                            "coding": [
                                {
                                    "system": "http://suoke.life/fhir/CodeSystem/tcm-complexion",
                                    "code": "pale",
                                    "display": "面色苍白"
                                }
                            ]
                        }
                    }
                ]
            }
        }


class ComplexionAnalysis(BaseModel):
    """面色分析结果"""
    
    color_type: str = Field(..., description="面色类型")
    confidence: float = Field(..., description="置信度", ge=0.0, le=1.0)
    characteristics: List[str] = Field(default=[], description="特征描述")
    health_implications: List[str] = Field(default=[], description="健康含义")


class TongueAnalysis(BaseModel):
    """舌诊分析结果"""
    
    tongue_body: Dict[str, Any] = Field(..., description="舌体分析")
    tongue_coating: Dict[str, Any] = Field(..., description="舌苔分析")
    overall_assessment: str = Field(..., description="整体评估")
    confidence: float = Field(..., description="置信度", ge=0.0, le=1.0)


class EyeAnalysis(BaseModel):
    """眼诊分析结果"""
    
    eye_color: str = Field(..., description="眼色")
    eye_spirit: str = Field(..., description="眼神")
    abnormalities: List[str] = Field(default=[], description="异常表现")
    confidence: float = Field(..., description="置信度", ge=0.0, le=1.0)


class LookDiagnosisResult(BaseModel):
    """望诊分析结果"""
    
    analysis_id: str = Field(..., description="分析ID")
    user_id: str = Field(..., description="用户ID")
    timestamp: datetime = Field(..., description="分析时间")
    image_type: str = Field(..., description="图像类型")
    
    complexion: Optional[ComplexionAnalysis] = Field(default=None, description="面色分析")
    tongue: Optional[TongueAnalysis] = Field(default=None, description="舌诊分析")
    eye: Optional[EyeAnalysis] = Field(default=None, description="眼诊分析")
    
    overall_score: float = Field(..., description="整体评分", ge=0.0, le=100.0)
    health_status: str = Field(..., description="健康状态评估")
    recommendations: List[str] = Field(default=[], description="建议")
    
    class Config:
        json_schema_extra = {
            "example": {
                "analysis_id": "look-123",
                "user_id": "user123",
                "timestamp": "2024-01-01T12:00:00Z",
                "image_type": "face",
                "complexion": {
                    "color_type": "pale",
                    "confidence": 0.85,
                    "characteristics": ["面色苍白", "缺乏光泽"],
                    "health_implications": ["可能存在气血不足", "建议补气养血"]
                },
                "overall_score": 75.0,
                "health_status": "亚健康",
                "recommendations": ["注意休息", "加强营养", "适当运动"]
            }
        } 