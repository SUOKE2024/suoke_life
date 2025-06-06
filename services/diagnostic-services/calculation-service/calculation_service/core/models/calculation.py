"""
calculation - 索克生活项目模块
"""

from .base import CalculationBaseModel
from .patient import BaziModel, WuxingModel
from datetime import date, time
from enum import Enum
from pydantic import Field
from typing import Dict, List, Optional

"""
算诊计算数据模型

定义五运六气、八卦分析、子午流注等算诊方法的数据结构
"""





class WuyunType(str, Enum):
    """五运类型"""
    WOOD_EXCESS = "木运太过"
    WOOD_DEFICIENT = "木运不及"
    FIRE_EXCESS = "火运太过"
    FIRE_DEFICIENT = "火运不及"
    EARTH_EXCESS = "土运太过"
    EARTH_DEFICIENT = "土运不及"
    METAL_EXCESS = "金运太过"
    METAL_DEFICIENT = "金运不及"
    WATER_EXCESS = "水运太过"
    WATER_DEFICIENT = "水运不及"


class LiuqiType(str, Enum):
    """六气类型"""
    JUEYIN_FENGMU = "厥阴风木"
    SHAOYIN_JUNHUO = "少阴君火"
    SHAOYANG_XIANGHUO = "少阳相火"
    TAIYIN_SHITU = "太阴湿土"
    YANGMING_ZAOJIN = "阳明燥金"
    TAIYANG_HANSHUI = "太阳寒水"


class BaguaType(str, Enum):
    """八卦类型"""
    QIAN = "乾卦"
    KUN = "坤卦"
    ZHEN = "震卦"
    XUN = "巽卦"
    KAN = "坎卦"
    LI = "离卦"
    GEN = "艮卦"
    DUI = "兑卦"


class MeridianType(str, Enum):
    """经络类型"""
    LUNG = "肺经"
    LARGE_INTESTINE = "大肠经"
    STOMACH = "胃经"
    SPLEEN = "脾经"
    HEART = "心经"
    SMALL_INTESTINE = "小肠经"
    BLADDER = "膀胱经"
    KIDNEY = "肾经"
    PERICARDIUM = "心包经"
    TRIPLE_HEATER = "三焦经"
    GALLBLADDER = "胆经"
    LIVER = "肝经"


class WuyunLiuqiModel(CalculationBaseModel):
    """五运六气分析模型"""
    
    analysis_type: str = Field(default="wuyun_liuqi", description="分析类型")
    
    # 基本信息
    year: int = Field(description="分析年份")
    ganzhi: str = Field(description="年份干支")
    
    # 五运分析
    wuyun: Dict = Field(description="五运分析结果")
    
    # 六气分析
    liuqi: Dict = Field(description="六气分析结果")
    
    # 气候影响
    climate_influence: str = Field(description="气候影响")
    
    # 易发疾病
    diseases_prone: List[str] = Field(description="易发疾病")
    
    # 预防建议
    prevention_advice: List[str] = Field(description="预防建议")


class BaguaAnalysisModel(CalculationBaseModel):
    """八卦分析模型"""
    
    analysis_type: str = Field(default="bagua_analysis", description="分析类型")
    
    # 主卦
    primary_gua: BaguaType = Field(description="主卦")
    
    # 变卦
    changing_gua: Optional[BaguaType] = Field(default=None, description="变卦")
    
    # 脏腑对应
    organ_correspondence: str = Field(description="脏腑对应")
    
    # 体质类型
    constitution_type: str = Field(description="体质类型")
    
    # 性格特征
    characteristics: List[str] = Field(description="性格特征")
    
    # 健康建议
    health_advice: List[str] = Field(description="健康建议")
    
    # 病位分析
    disease_location: Optional[str] = Field(default=None, description="病位分析")


class ZiwuLiuzhuModel(CalculationBaseModel):
    """子午流注分析模型"""
    
    analysis_type: str = Field(default="ziwu_liuzhu", description="分析类型")
    
    # 分析日期
    analysis_date: date = Field(description="分析日期")
    
    # 病症
    condition: str = Field(description="病症")
    
    # 治疗类型
    treatment_type: str = Field(description="治疗类型")
    
    # 最佳治疗时间
    optimal_treatment_times: List[Dict] = Field(description="最佳治疗时间")
    
    # 当日经络流注
    daily_meridian_flow: List[Dict] = Field(description="当日经络流注")
    
    # 治疗建议
    treatment_advice: List[str] = Field(description="治疗建议")


class ConstitutionAnalysisModel(CalculationBaseModel):
    """体质分析模型"""
    
    analysis_type: str = Field(default="constitution_analysis", description="分析类型")
    
    # 八字信息
    bazi: BaziModel = Field(description="八字信息")
    
    # 五行分析
    wuxing_analysis: WuxingModel = Field(description="五行分析")
    
    # 体质类型
    constitution_type: str = Field(description="体质类型")
    
    # 体质特征
    characteristics: List[str] = Field(description="体质特征")
    
    # 健康风险
    health_risks: List[str] = Field(description="健康风险")
    
    # 饮食建议
    dietary_advice: List[str] = Field(description="饮食建议")
    
    # 生活方式建议
    lifestyle_advice: List[str] = Field(description="生活方式建议")
    
    # 运动建议
    exercise_advice: List[str] = Field(description="运动建议")
    
    # 情志调养
    emotional_advice: List[str] = Field(description="情志调养")


class ComprehensiveAnalysisModel(CalculationBaseModel):
    """综合算诊分析模型"""
    
    analysis_type: str = Field(default="comprehensive_analysis", description="分析类型")
    
    # 五运六气分析
    wuyun_liuqi: Optional[WuyunLiuqiModel] = Field(default=None, description="五运六气分析")
    
    # 八卦分析
    bagua_analysis: Optional[BaguaAnalysisModel] = Field(default=None, description="八卦分析")
    
    # 子午流注分析
    ziwu_liuzhu: Optional[ZiwuLiuzhuModel] = Field(default=None, description="子午流注分析")
    
    # 体质分析
    constitution_analysis: Optional[ConstitutionAnalysisModel] = Field(default=None, description="体质分析")
    
    # 综合评估
    comprehensive_assessment: str = Field(description="综合评估")
    
    # 主要健康风险
    primary_health_risks: List[str] = Field(description="主要健康风险")
    
    # 综合建议
    comprehensive_recommendations: List[str] = Field(description="综合建议")
    
    # 优先级建议
    priority_recommendations: List[Dict] = Field(description="优先级建议")
    
    # 随访建议
    follow_up_advice: Optional[str] = Field(default=None, description="随访建议")


class CalculationRequestModel(CalculationBaseModel):
    """算诊请求模型"""
    
    # 请求类型
    request_type: str = Field(description="请求类型")
    
    # 患者信息
    patient_info: Dict = Field(description="患者信息")
    
    # 分析参数
    analysis_parameters: Optional[Dict] = Field(default=None, description="分析参数")
    
    # 请求选项
    options: Optional[Dict] = Field(default=None, description="请求选项")


class CalculationResponseModel(CalculationBaseModel):
    """算诊响应模型"""
    
    # 请求ID
    request_id: str = Field(description="请求ID")
    
    # 分析结果
    analysis_result: Dict = Field(description="分析结果")
    
    # 处理状态
    status: str = Field(description="处理状态")
    
    # 错误信息
    error_message: Optional[str] = Field(default=None, description="错误信息")
    
    # 处理时间
    processing_time_ms: Optional[int] = Field(default=None, description="处理时间(毫秒)") 