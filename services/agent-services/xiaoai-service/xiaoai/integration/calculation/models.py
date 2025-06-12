"""
算诊服务集成数据模型

定义与算诊服务交互的数据结构，包含完整的中医算诊方法
"""

from datetime import datetime, date, time
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class CalculationType(str, Enum):
    """算诊类型"""
    CONSTITUTION = "constitution"           # 体质分析
    ZIWU_LIUZHU = "ziwu_liuzhu"           # 子午流注
    WUYUN_LIUQI = "wuyun_liuqi"           # 五运六气
    BAGUA = "bagua"                       # 八卦分析
    COMPREHENSIVE = "comprehensive"        # 综合算诊


class Gender(str, Enum):
    """性别"""
    MALE = "male"
    FEMALE = "female"


class PatientInfo(BaseModel):
    """患者信息"""
    birth_date: date = Field(description="出生日期")
    birth_time: Optional[time] = Field(default=None, description="出生时间")
    gender: Gender = Field(description="性别")
    birth_place: Optional[str] = Field(default=None, description="出生地点")
    current_location: Optional[str] = Field(default=None, description="当前位置")


class CalculationRequest(BaseModel):
    """算诊请求"""
    user_id: str = Field(description="用户ID")
    session_id: str = Field(description="会话ID")
    calculation_type: CalculationType = Field(description="算诊类型")
    patient_info: PatientInfo = Field(description="患者信息")
    analysis_parameters: Optional[Dict[str, Any]] = Field(default=None, description="分析参数")
    options: Optional[Dict[str, Any]] = Field(default=None, description="请求选项")
    # 向后兼容
    diagnosis_data: Optional[Dict[str, Any]] = Field(default=None, description="诊断数据（兼容）")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class ConstitutionType(str, Enum):
    """体质类型"""
    PING_HE = "平和质"           # 平和质
    QI_XU = "气虚质"             # 气虚质
    YANG_XU = "阳虚质"           # 阳虚质
    YIN_XU = "阴虚质"            # 阴虚质
    TAN_SHI = "痰湿质"           # 痰湿质
    SHI_RE = "湿热质"            # 湿热质
    XUE_YU = "血瘀质"            # 血瘀质
    QI_YU = "气郁质"             # 气郁质
    TE_BIN = "特禀质"            # 特禀质


class ConstitutionAnalysis(BaseModel):
    """体质分析结果"""
    primary_constitution: ConstitutionType = Field(description="主要体质")
    constitution_score: float = Field(description="体质得分", ge=0, le=100)
    secondary_constitutions: List[Dict[str, float]] = Field(description="次要体质")
    constitution_description: str = Field(description="体质描述")
    health_tendencies: List[str] = Field(description="健康倾向")
    recommendations: List[str] = Field(description="调理建议")
    confidence: float = Field(description="置信度", ge=0, le=1)


class MeridianInfo(BaseModel):
    """经络信息"""
    name: str = Field(description="经络名称")
    element: str = Field(description="五行属性")
    organ: str = Field(description="对应脏腑")
    peak_time: str = Field(description="旺时")
    low_time: str = Field(description="衰时")


class ZiwuLiuzhuAnalysis(BaseModel):
    """子午流注分析结果"""
    current_meridian: MeridianInfo = Field(description="当前主导经络")
    optimal_treatment_times: List[Dict[str, str]] = Field(description="最佳治疗时间")
    meridian_schedule: Dict[str, MeridianInfo] = Field(description="十二时辰经络流注")
    health_guidance: List[str] = Field(description="养生指导")
    acupoint_recommendations: List[Dict[str, Any]] = Field(description="穴位建议")
    confidence: float = Field(description="置信度", ge=0, le=1)


class WuyunLiuqiAnalysis(BaseModel):
    """五运六气分析结果"""
    current_year_qi: str = Field(description="当年运气")
    seasonal_influence: str = Field(description="季节影响")
    health_predictions: List[str] = Field(description="健康预测")
    prevention_advice: List[str] = Field(description="预防建议")
    favorable_periods: List[Dict[str, str]] = Field(description="有利时期")
    unfavorable_periods: List[Dict[str, str]] = Field(description="不利时期")
    confidence: float = Field(description="置信度", ge=0, le=1)


class BaguaAnalysis(BaseModel):
    """八卦分析结果"""
    life_gua: str = Field(description="本命卦")
    current_gua: str = Field(description="当前卦象")
    health_implications: List[str] = Field(description="健康含义")
    auspicious_directions: List[str] = Field(description="吉利方位")
    favorable_colors: List[str] = Field(description="有利颜色")
    lifestyle_suggestions: List[str] = Field(description="生活建议")
    confidence: float = Field(description="置信度", ge=0, le=1)


class ComprehensiveAnalysis(BaseModel):
    """综合算诊分析结果"""
    constitution_analysis: ConstitutionAnalysis = Field(description="体质分析")
    ziwu_analysis: ZiwuLiuzhuAnalysis = Field(description="子午流注分析")
    wuyun_analysis: Optional[WuyunLiuqiAnalysis] = Field(default=None, description="五运六气分析")
    bagua_analysis: Optional[BaguaAnalysis] = Field(default=None, description="八卦分析")

    # 综合评估
    overall_assessment: str = Field(description="综合评估")
    primary_health_risks: List[str] = Field(description="主要健康风险")
    comprehensive_recommendations: List[str] = Field(description="综合建议")
    priority_actions: List[Dict[str, Any]] = Field(description="优先行动")
    follow_up_advice: Optional[str] = Field(default=None, description="随访建议")

    # 元数据
    analysis_timestamp: datetime = Field(description="分析时间")
    overall_confidence: float = Field(description="整体置信度", ge=0, le=1)


class CalculationResponse(BaseModel):
    """算诊响应"""
    request_id: str = Field(description="请求ID")
    user_id: str = Field(description="用户ID")
    session_id: str = Field(description="会话ID")
    calculation_type: CalculationType = Field(description="算诊类型")

    # 分析结果
    constitution_analysis: Optional[ConstitutionAnalysis] = Field(default=None, description="体质分析")
    ziwu_analysis: Optional[ZiwuLiuzhuAnalysis] = Field(default=None, description="子午流注分析")
    wuyun_analysis: Optional[WuyunLiuqiAnalysis] = Field(default=None, description="五运六气分析")
    bagua_analysis: Optional[BaguaAnalysis] = Field(default=None, description="八卦分析")
    comprehensive_analysis: Optional[ComprehensiveAnalysis] = Field(default=None, description="综合分析")

    # 向后兼容字段
    confidence: float = Field(ge=0.0, le=1.0, description="置信度")
    calculation_results: Dict[str, Any] = Field(default_factory=dict, description="计算结果")
    analysis_results: Dict[str, Any] = Field(default_factory=dict, description="分析结果")
    recommendations: List[str] = Field(default_factory=list, description="建议")
    processing_time: Optional[float] = Field(default=None, description="处理时间(秒)")
    
    # 状态信息
    status: str = Field(description="处理状态")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    processing_time_ms: int = Field(description="处理时间(毫秒)")
    timestamp: datetime = Field(description="响应时间")


class CalculationError(BaseModel):
    """算诊错误"""
    error_code: str = Field(description="错误代码")
    error_message: str = Field(description="错误信息")
    details: Optional[Dict[str, Any]] = Field(default=None, description="错误详情")
    timestamp: datetime = Field(description="错误时间")