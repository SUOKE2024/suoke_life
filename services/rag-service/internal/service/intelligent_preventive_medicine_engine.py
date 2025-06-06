"""
intelligent_preventive_medicine_engine - 索克生活项目模块
"""

from ..observability.metrics import MetricsCollector
from ..observability.tracing import trace_operation, SpanKind
from dataclasses import dataclass, field
from datetime import datetime, timedelta, date
from enum import Enum
from loguru import logger
from typing import Dict, List, Any, Optional, Tuple, Union, Set, Callable
import warnings

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能预防医学引擎 - 实现"治未病"核心理念的预防医学服务
结合现代预防医学和中医"治未病"理论，为用户提供个性化的疾病预防和健康维护方案
"""

warnings.filterwarnings('ignore')


class RiskLevel(str, Enum):
    """风险等级"""
    VERY_LOW = "very_low"          # 极低风险
    LOW = "low"                    # 低风险
    MODERATE = "moderate"          # 中等风险
    HIGH = "high"                  # 高风险
    VERY_HIGH = "very_high"        # 极高风险

class DiseaseCategory(str, Enum):
    """疾病类别"""
    CARDIOVASCULAR = "cardiovascular"           # 心血管疾病
    DIABETES = "diabetes"                       # 糖尿病
    CANCER = "cancer"                          # 癌症
    RESPIRATORY = "respiratory"                 # 呼吸系统疾病
    NEUROLOGICAL = "neurological"               # 神经系统疾病
    DIGESTIVE = "digestive"                     # 消化系统疾病
    MUSCULOSKELETAL = "musculoskeletal"         # 肌肉骨骼疾病
    MENTAL_HEALTH = "mental_health"             # 精神健康
    INFECTIOUS = "infectious"                   # 感染性疾病
    AUTOIMMUNE = "autoimmune"                   # 自身免疫疾病

class PreventionStrategy(str, Enum):
    """预防策略"""
    PRIMARY = "primary"            # 一级预防（病因预防）
    SECONDARY = "secondary"        # 二级预防（早期发现）
    TERTIARY = "tertiary"          # 三级预防（康复预防）

class ScreeningType(str, Enum):
    """筛查类型"""
    BLOOD_TEST = "blood_test"                   # 血液检查
    IMAGING = "imaging"                         # 影像检查
    PHYSICAL_EXAM = "physical_exam"             # 体格检查
    GENETIC_TEST = "genetic_test"               # 基因检测
    BIOMARKER = "biomarker"                     # 生物标志物
    FUNCTIONAL_TEST = "functional_test"         # 功能检查
    PSYCHOLOGICAL_ASSESSMENT = "psychological"   # 心理评估

class VaccineType(str, Enum):
    """疫苗类型"""
    ROUTINE = "routine"            # 常规疫苗
    TRAVEL = "travel"              # 旅行疫苗
    OCCUPATIONAL = "occupational"  # 职业疫苗
    HIGH_RISK = "high_risk"        # 高危人群疫苗
    SEASONAL = "seasonal"          # 季节性疫苗

class TCMConstitution(str, Enum):
    """中医体质类型"""
    BALANCED = "balanced"                       # 平和质
    QI_DEFICIENCY = "qi_deficiency"             # 气虚质
    YANG_DEFICIENCY = "yang_deficiency"         # 阳虚质
    YIN_DEFICIENCY = "yin_deficiency"           # 阴虚质
    PHLEGM_DAMPNESS = "phlegm_dampness"         # 痰湿质
    DAMP_HEAT = "damp_heat"                     # 湿热质
    BLOOD_STASIS = "blood_stasis"               # 血瘀质
    QI_STAGNATION = "qi_stagnation"             # 气郁质
    SPECIAL_DIATHESIS = "special_diathesis"     # 特禀质

@dataclass
class RiskFactor:
    """风险因素"""
    factor_id: str
    name: str
    category: str                               # 风险因素类别
    value: Union[float, str, bool]              # 风险因素值
    weight: float                               # 权重
    modifiable: bool                            # 是否可改变
    evidence_level: str                         # 证据等级
    source: str                                 # 数据来源
    last_updated: datetime
    notes: Optional[str] = None

@dataclass
class DiseaseRiskAssessment:
    """疾病风险评估"""
    user_id: str
    disease_name: str
    disease_category: DiseaseCategory
    assessment_date: datetime
    risk_level: RiskLevel
    risk_score: float                           # 风险评分 (0.0-1.0)
    contributing_factors: List[RiskFactor] = field(default_factory=list)
    protective_factors: List[RiskFactor] = field(default_factory=list)
    genetic_risk: float = 0.0                   # 遗传风险
    lifestyle_risk: float = 0.0                 # 生活方式风险
    environmental_risk: float = 0.0             # 环境风险
    age_risk: float = 0.0                       # 年龄风险
    tcm_constitution_risk: float = 0.0          # 中医体质风险
    confidence_interval: Tuple[float, float] = (0.0, 0.0)
    time_horizon: int = 10                      # 预测时间范围（年）
    recommendations: List[str] = field(default_factory=list)
    next_assessment_date: Optional[datetime] = None

@dataclass
class PreventionPlan:
    """预防计划"""
    plan_id: str
    user_id: str
    name: str
    description: str
    target_diseases: List[str]
    prevention_strategies: List[PreventionStrategy]
    start_date: datetime
    end_date: Optional[datetime] = None
    
    # 生活方式干预
    lifestyle_interventions: List[Dict[str, Any]] = field(default_factory=list)
    
    # 营养干预
    nutrition_interventions: List[Dict[str, Any]] = field(default_factory=list)
    
    # 运动干预
    exercise_interventions: List[Dict[str, Any]] = field(default_factory=list)
    
    # 中医预防措施
    tcm_interventions: List[Dict[str, Any]] = field(default_factory=list)
    
    # 筛查计划
    screening_schedule: List[Dict[str, Any]] = field(default_factory=list)
    
    # 疫苗计划
    vaccination_schedule: List[Dict[str, Any]] = field(default_factory=list)
    
    # 环境改善措施
    environmental_measures: List[Dict[str, Any]] = field(default_factory=list)
    
    # 进度指标
    progress_metrics: List[str] = field(default_factory=list)
    
    # 成功标准
    success_criteria: List[str] = field(default_factory=list)
    
    status: str = "active"
    created_by: str = "system"
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class ScreeningRecommendation:
    """筛查建议"""
    user_id: str
    screening_name: str
    screening_type: ScreeningType
    target_condition: str
    recommended_date: datetime
    frequency: str                              # 筛查频率
    priority: str                               # 优先级
    age_range: Tuple[int, int]                  # 适用年龄范围
    risk_factors: List[str] = field(default_factory=list)
    preparation_instructions: List[str] = field(default_factory=list)
    expected_results: str = ""
    follow_up_actions: List[str] = field(default_factory=list)
    cost_estimate: Optional[float] = None
    insurance_coverage: Optional[str] = None
    provider_recommendations: List[str] = field(default_factory=list)

@dataclass
class VaccinationRecommendation:
    """疫苗接种建议"""
    user_id: str
    vaccine_name: str
    vaccine_type: VaccineType
    target_diseases: List[str]
    recommended_date: datetime
    doses_required: int
    interval_between_doses: Optional[int] = None  # 间隔天数
    age_range: Tuple[int, int]
    risk_groups: List[str] = field(default_factory=list)
    contraindications: List[str] = field(default_factory=list)
    side_effects: List[str] = field(default_factory=list)
    effectiveness: float = 0.0                  # 有效性 (0.0-1.0)
    duration_of_protection: Optional[int] = None  # 保护期（年）
    booster_required: bool = False
    travel_requirement: bool = False
    priority: str = "routine"

@dataclass
class EnvironmentalRiskAssessment:
    """环境风险评估"""
    user_id: str
    assessment_date: datetime
    location: str
    
    # 空气质量
    air_quality_index: Optional[float] = None
    pm25_level: Optional[float] = None
    pm10_level: Optional[float] = None
    ozone_level: Optional[float] = None
    
    # 水质
    water_quality_score: Optional[float] = None
    contaminant_levels: Dict[str, float] = field(default_factory=dict)
    
    # 噪音污染
    noise_level: Optional[float] = None
    
    # 职业暴露
    occupational_hazards: List[str] = field(default_factory=list)
    chemical_exposures: List[str] = field(default_factory=list)
    
    # 生活环境
    housing_conditions: Dict[str, Any] = field(default_factory=dict)
    neighborhood_safety: str = ""
    
    # 风险评估
    overall_risk_score: float = 0.0
    high_risk_factors: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

@dataclass
class FamilyHealthHistory:
    """家族健康史"""
    user_id: str
    relative_type: str                          # 亲属关系
    relative_id: Optional[str] = None
    diseases: List[str] = field(default_factory=list)
    age_of_onset: Dict[str, int] = field(default_factory=dict)
    cause_of_death: Optional[str] = None
    age_at_death: Optional[int] = None
    genetic_test_results: Dict[str, Any] = field(default_factory=dict)
    lifestyle_factors: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class PreventionOutcome:
    """预防效果"""
    user_id: str
    plan_id: str
    measurement_date: datetime
    
    # 健康指标改善
    health_metrics_improvement: Dict[str, float] = field(default_factory=dict)
    
    # 风险降低
    risk_reduction: Dict[str, float] = field(default_factory=dict)
    
    # 生活质量改善
    quality_of_life_score: Optional[float] = None
    
    # 依从性
    adherence_rate: float = 0.0                 # 依从率 (0.0-1.0)
    
    # 成本效益
    cost_savings: Optional[float] = None
    
    # 满意度
    satisfaction_score: Optional[float] = None
    
    # 副作用或不良反应
    adverse_events: List[str] = field(default_factory=list)
    
    # 下一步建议
    next_steps: List[str] = field(default_factory=list)

class RiskPredictor:
    """风险预测器"""
    
    def __init__(self):
        self.models = {}
        self.risk_databases = self._load_risk_databases()
        self.tcm_constitution_risks = self._load_tcm_constitution_risks()
        
    def _load_risk_databases(self) -> Dict[str, Any]:
        """加载风险数据库"""
        return {
            "cardiovascular": {
                "framingham_risk_factors": [
                    "age", "gender", "total_cholesterol", "hdl_cholesterol",
                    "systolic_bp", "smoking", "diabetes"
                ],
                "weights": {
                    "age": 0.15, "gender": 0.1, "total_cholesterol": 0.12,
                    "hdl_cholesterol": -0.08, "systolic_bp": 0.13,
                    "smoking": 0.18, "diabetes": 0.2
                },
                "baseline_risk": 0.05
            },
            "diabetes": {
                "risk_factors": [
                    "age", "bmi", "family_history", "gestational_diabetes",
                    "hypertension", "physical_activity", "diet_quality"
                ],
                "weights": {
                    "age": 0.12, "bmi": 0.25, "family_history": 0.2,
                    "gestational_diabetes": 0.15, "hypertension": 0.1,
                    "physical_activity": -0.1, "diet_quality": -0.08
                },
                "baseline_risk": 0.08
            },
            "cancer": {
                "breast_cancer": {
                    "risk_factors": [
                        "age", "family_history", "brca_mutations", "reproductive_history",
                        "hormone_use", "alcohol_consumption", "physical_activity"
                    ],
                    "weights": {
                        "age": 0.2, "family_history": 0.25, "brca_mutations": 0.4,
                        "reproductive_history": 0.1, "hormone_use": 0.15,
                        "alcohol_consumption": 0.08, "physical_activity": -0.05
                    }
                },
                "lung_cancer": {
                    "risk_factors": [
                        "smoking_history", "age", "family_history", "occupational_exposure",
                        "air_pollution", "radon_exposure"
                    ],
                    "weights": {
                        "smoking_history": 0.6, "age": 0.15, "family_history": 0.1,
                        "occupational_exposure": 0.08, "air_pollution": 0.05,
                        "radon_exposure": 0.02
                    }
                }
            }
        }
    
    def _load_tcm_constitution_risks(self) -> Dict[str, Any]:
        """加载中医体质疾病易感性数据"""
        return {
            TCMConstitution.QI_DEFICIENCY: {
                "susceptible_diseases": [
                    "respiratory_infections", "fatigue_syndrome", "digestive_disorders"
                ],
                "risk_multipliers": {
                    "respiratory": 1.5, "digestive": 1.3, "cardiovascular": 1.2
                }
            },
            TCMConstitution.YANG_DEFICIENCY: {
                "susceptible_diseases": [
                    "hypothyroidism", "chronic_fatigue", "digestive_disorders", "depression"
                ],
                "risk_multipliers": {
                    "endocrine": 1.6, "mental_health": 1.4, "digestive": 1.3
                }
            },
            TCMConstitution.YIN_DEFICIENCY: {
                "susceptible_diseases": [
                    "diabetes", "hypertension", "insomnia", "anxiety"
                ],
                "risk_multipliers": {
                    "diabetes": 1.5, "cardiovascular": 1.4, "mental_health": 1.3
                }
            },
            TCMConstitution.PHLEGM_DAMPNESS: {
                "susceptible_diseases": [
                    "obesity", "diabetes", "hyperlipidemia", "metabolic_syndrome"
                ],
                "risk_multipliers": {
                    "diabetes": 1.8, "cardiovascular": 1.6, "metabolic": 1.7
                }
            },
            TCMConstitution.DAMP_HEAT: {
                "susceptible_diseases": [
                    "hypertension", "skin_disorders", "liver_disorders"
                ],
                "risk_multipliers": {
                    "cardiovascular": 1.4, "dermatological": 1.6, "hepatic": 1.5
                }
            },
            TCMConstitution.BLOOD_STASIS: {
                "susceptible_diseases": [
                    "cardiovascular_disease", "stroke", "thrombosis"
                ],
                "risk_multipliers": {
                    "cardiovascular": 1.8, "neurological": 1.5, "vascular": 1.7
                }
            },
            TCMConstitution.QI_STAGNATION: {
                "susceptible_diseases": [
                    "depression", "anxiety", "digestive_disorders", "menstrual_disorders"
                ],
                "risk_multipliers": {
                    "mental_health": 1.6, "digestive": 1.3, "reproductive": 1.4
                }
            },
            TCMConstitution.SPECIAL_DIATHESIS: {
                "susceptible_diseases": [
                    "allergies", "asthma", "autoimmune_disorders"
                ],
                "risk_multipliers": {
                    "allergic": 2.0, "respiratory": 1.7, "autoimmune": 1.8
                }
            }
        }
    
    @trace_operation("risk_predictor.assess_disease_risk", SpanKind.INTERNAL)
    async def assess_disease_risk(
        self,
        user_id: str,
        disease_name: str,
        user_data: Dict[str, Any],
        family_history: Optional[FamilyHealthHistory] = None,
        environmental_data: Optional[EnvironmentalRiskAssessment] = None
    ) -> DiseaseRiskAssessment:
        """评估疾病风险"""
        
        try:
            # 获取疾病类别
            disease_category = self._get_disease_category(disease_name)
            
            # 计算各类风险
            genetic_risk = await self._calculate_genetic_risk(disease_name, family_history)
            lifestyle_risk = await self._calculate_lifestyle_risk(disease_name, user_data)
            environmental_risk = await self._calculate_environmental_risk(disease_name, environmental_data)
            age_risk = self._calculate_age_risk(disease_name, user_data.get("age", 0))
            tcm_risk = await self._calculate_tcm_constitution_risk(disease_name, user_data)
            
            # 综合风险评分
            risk_score = await self._calculate_composite_risk(
                genetic_risk, lifestyle_risk, environmental_risk, age_risk, tcm_risk
            )
            
            # 确定风险等级
            risk_level = self._determine_risk_level(risk_score)
            
            # 识别风险因素和保护因素
            contributing_factors = await self._identify_risk_factors(disease_name, user_data)
            protective_factors = await self._identify_protective_factors(disease_name, user_data)
            
            # 生成建议
            recommendations = await self._generate_risk_recommendations(
                disease_name, risk_level, contributing_factors
            )
            
            # 计算置信区间
            confidence_interval = self._calculate_confidence_interval(risk_score, user_data)
            
            return DiseaseRiskAssessment(
                user_id=user_id,
                disease_name=disease_name,
                disease_category=disease_category,
                assessment_date=datetime.now(),
                risk_level=risk_level,
                risk_score=risk_score,
                contributing_factors=contributing_factors,
                protective_factors=protective_factors,
                genetic_risk=genetic_risk,
                lifestyle_risk=lifestyle_risk,
                environmental_risk=environmental_risk,
                age_risk=age_risk,
                tcm_constitution_risk=tcm_risk,
                confidence_interval=confidence_interval,
                recommendations=recommendations,
                next_assessment_date=self._calculate_next_assessment_date(risk_level)
            )
            
        except Exception as e:
            logger.error(f"疾病风险评估失败: {e}")
            raise
    
    def _get_disease_category(self, disease_name: str) -> DiseaseCategory:
        """获取疾病类别"""
        disease_mapping = {
            "hypertension": DiseaseCategory.CARDIOVASCULAR,
            "diabetes": DiseaseCategory.DIABETES,
            "breast_cancer": DiseaseCategory.CANCER,
            "lung_cancer": DiseaseCategory.CANCER,
            "depression": DiseaseCategory.MENTAL_HEALTH,
            "asthma": DiseaseCategory.RESPIRATORY,
            "stroke": DiseaseCategory.NEUROLOGICAL,
            "arthritis": DiseaseCategory.MUSCULOSKELETAL
        }
        return disease_mapping.get(disease_name, DiseaseCategory.CARDIOVASCULAR)
    
    async def _calculate_genetic_risk(
        self,
        disease_name: str,
        family_history: Optional[FamilyHealthHistory]
    ) -> float:
        """计算遗传风险"""
        if not family_history:
            return 0.1  # 基础遗传风险
        
        genetic_risk = 0.1
        
        # 家族史风险
        if disease_name in family_history.diseases:
            genetic_risk += 0.3
            
            # 发病年龄影响
            if disease_name in family_history.age_of_onset:
                onset_age = family_history.age_of_onset[disease_name]
                if onset_age < 50:
                    genetic_risk += 0.2
                elif onset_age < 65:
                    genetic_risk += 0.1
        
        # 基因检测结果
        if family_history.genetic_test_results:
            for gene, result in family_history.genetic_test_results.items():
                if result.get("pathogenic", False):
                    genetic_risk += 0.4
                elif result.get("likely_pathogenic", False):
                    genetic_risk += 0.2
        
        return min(genetic_risk, 1.0)
    
    async def _calculate_lifestyle_risk(self, disease_name: str, user_data: Dict[str, Any]) -> float:
        """计算生活方式风险"""
        lifestyle_risk = 0.0
        
        # 吸烟
        if user_data.get("smoking_status") == "current":
            lifestyle_risk += 0.3
        elif user_data.get("smoking_status") == "former":
            lifestyle_risk += 0.1
        
        # BMI
        bmi = user_data.get("bmi", 22)
        if bmi >= 30:
            lifestyle_risk += 0.2
        elif bmi >= 25:
            lifestyle_risk += 0.1
        
        # 运动
        exercise_minutes = user_data.get("weekly_exercise_minutes", 150)
        if exercise_minutes < 75:
            lifestyle_risk += 0.15
        elif exercise_minutes < 150:
            lifestyle_risk += 0.05
        
        # 饮酒
        alcohol_units = user_data.get("weekly_alcohol_units", 0)
        if alcohol_units > 14:
            lifestyle_risk += 0.1
        
        # 饮食质量
        diet_score = user_data.get("diet_quality_score", 7)
        if diet_score < 5:
            lifestyle_risk += 0.15
        elif diet_score < 7:
            lifestyle_risk += 0.05
        
        return min(lifestyle_risk, 1.0)
    
    async def _calculate_environmental_risk(
        self,
        disease_name: str,
        environmental_data: Optional[EnvironmentalRiskAssessment]
    ) -> float:
        """计算环境风险"""
        if not environmental_data:
            return 0.05  # 基础环境风险
        
        env_risk = 0.05
        
        # 空气质量
        if environmental_data.air_quality_index:
            aqi = environmental_data.air_quality_index
            if aqi > 150:
                env_risk += 0.2
            elif aqi > 100:
                env_risk += 0.1
            elif aqi > 50:
                env_risk += 0.05
        
        # 职业暴露
        if environmental_data.occupational_hazards:
            env_risk += len(environmental_data.occupational_hazards) * 0.05
        
        # 化学暴露
        if environmental_data.chemical_exposures:
            env_risk += len(environmental_data.chemical_exposures) * 0.03
        
        return min(env_risk, 1.0)
    
    def _calculate_age_risk(self, disease_name: str, age: int) -> float:
        """计算年龄风险"""
        age_risk_curves = {
            "cardiovascular": lambda a: max(0, (a - 40) / 40),
            "diabetes": lambda a: max(0, (a - 35) / 45),
            "cancer": lambda a: max(0, (a - 30) / 50),
            "osteoporosis": lambda a: max(0, (a - 50) / 30)
        }
        
        disease_category = self._get_disease_category(disease_name).value
        risk_func = age_risk_curves.get(disease_category, lambda a: max(0, (a - 40) / 40))
        
        return min(risk_func(age), 1.0)
    
    async def _calculate_tcm_constitution_risk(self, disease_name: str, user_data: Dict[str, Any]) -> float:
        """计算中医体质风险"""
        constitution = user_data.get("tcm_constitution")
        if not constitution:
            return 0.0
        
        constitution_data = self.tcm_constitution_risks.get(constitution, {})
        disease_category = self._get_disease_category(disease_name).value
        
        risk_multiplier = constitution_data.get("risk_multipliers", {}).get(disease_category, 1.0)
        base_risk = 0.1
        
        return min(base_risk * risk_multiplier, 1.0)
    
    async def _calculate_composite_risk(
        self,
        genetic_risk: float,
        lifestyle_risk: float,
        environmental_risk: float,
        age_risk: float,
        tcm_risk: float
    ) -> float:
        """计算综合风险"""
        # 使用加权平均
        weights = {
            "genetic": 0.25,
            "lifestyle": 0.35,
            "environmental": 0.15,
            "age": 0.15,
            "tcm": 0.10
        }
        
        composite_risk = (
            genetic_risk * weights["genetic"] +
            lifestyle_risk * weights["lifestyle"] +
            environmental_risk * weights["environmental"] +
            age_risk * weights["age"] +
            tcm_risk * weights["tcm"]
        )
        
        return min(composite_risk, 1.0)
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """确定风险等级"""
        if risk_score < 0.1:
            return RiskLevel.VERY_LOW
        elif risk_score < 0.25:
            return RiskLevel.LOW
        elif risk_score < 0.5:
            return RiskLevel.MODERATE
        elif risk_score < 0.75:
            return RiskLevel.HIGH
        else:
            return RiskLevel.VERY_HIGH
    
    async def _identify_risk_factors(self, disease_name: str, user_data: Dict[str, Any]) -> List[RiskFactor]:
        """识别风险因素"""
        risk_factors = []
        
        # 年龄
        age = user_data.get("age", 0)
        if age > 50:
            risk_factors.append(RiskFactor(
                factor_id="age",
                name="年龄",
                category="demographic",
                value=age,
                weight=0.15,
                modifiable=False,
                evidence_level="high",
                source="user_profile",
                last_updated=datetime.now()
            ))
        
        # 吸烟
        if user_data.get("smoking_status") == "current":
            risk_factors.append(RiskFactor(
                factor_id="smoking",
                name="吸烟",
                category="lifestyle",
                value=True,
                weight=0.25,
                modifiable=True,
                evidence_level="high",
                source="user_profile",
                last_updated=datetime.now()
            ))
        
        # BMI
        bmi = user_data.get("bmi", 22)
        if bmi >= 25:
            risk_factors.append(RiskFactor(
                factor_id="obesity",
                name="超重/肥胖",
                category="lifestyle",
                value=bmi,
                weight=0.2,
                modifiable=True,
                evidence_level="high",
                source="health_metrics",
                last_updated=datetime.now()
            ))
        
        return risk_factors
    
    async def _identify_protective_factors(self, disease_name: str, user_data: Dict[str, Any]) -> List[RiskFactor]:
        """识别保护因素"""
        protective_factors = []
        
        # 规律运动
        exercise_minutes = user_data.get("weekly_exercise_minutes", 0)
        if exercise_minutes >= 150:
            protective_factors.append(RiskFactor(
                factor_id="regular_exercise",
                name="规律运动",
                category="lifestyle",
                value=exercise_minutes,
                weight=-0.15,
                modifiable=True,
                evidence_level="high",
                source="activity_tracker",
                last_updated=datetime.now()
            ))
        
        # 健康饮食
        diet_score = user_data.get("diet_quality_score", 5)
        if diet_score >= 8:
            protective_factors.append(RiskFactor(
                factor_id="healthy_diet",
                name="健康饮食",
                category="lifestyle",
                value=diet_score,
                weight=-0.1,
                modifiable=True,
                evidence_level="high",
                source="nutrition_tracker",
                last_updated=datetime.now()
            ))
        
        return protective_factors
    
    async def _generate_risk_recommendations(
        self,
        disease_name: str,
        risk_level: RiskLevel,
        risk_factors: List[RiskFactor]
    ) -> List[str]:
        """生成风险建议"""
        recommendations = []
        
        if risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            recommendations.append("建议尽快咨询专科医生进行详细评估")
            recommendations.append("考虑进行相关筛查检查")
        
        # 基于风险因素的建议
        for factor in risk_factors:
            if factor.modifiable:
                if factor.factor_id == "smoking":
                    recommendations.append("强烈建议戒烟，可寻求专业戒烟帮助")
                elif factor.factor_id == "obesity":
                    recommendations.append("建议通过合理饮食和运动控制体重")
                elif factor.factor_id == "sedentary":
                    recommendations.append("增加体育活动，每周至少150分钟中等强度运动")
        
        # 通用预防建议
        recommendations.extend([
            "保持健康的生活方式",
            "定期进行健康检查",
            "保持良好的心理状态",
            "遵循医生的预防建议"
        ])
        
        return recommendations
    
    def _calculate_confidence_interval(self, risk_score: float, user_data: Dict[str, Any]) -> Tuple[float, float]:
        """计算置信区间"""
        # 简化的置信区间计算
        margin_of_error = 0.1  # 10%的误差范围
        lower_bound = max(0.0, risk_score - margin_of_error)
        upper_bound = min(1.0, risk_score + margin_of_error)
        return (lower_bound, upper_bound)
    
    def _calculate_next_assessment_date(self, risk_level: RiskLevel) -> datetime:
        """计算下次评估日期"""
        intervals = {
            RiskLevel.VERY_LOW: 365 * 2,  # 2年
            RiskLevel.LOW: 365,           # 1年
            RiskLevel.MODERATE: 180,      # 6个月
            RiskLevel.HIGH: 90,           # 3个月
            RiskLevel.VERY_HIGH: 30       # 1个月
        }
        
        days = intervals.get(risk_level, 365)
        return datetime.now() + timedelta(days=days)

class PreventionPlanGenerator:
    """预防计划生成器"""
    
    def __init__(self):
        self.intervention_templates = self._load_intervention_templates()
        self.tcm_prevention_methods = self._load_tcm_prevention_methods()
    
    def _load_intervention_templates(self) -> Dict[str, Any]:
        """加载干预模板"""
        return {
            "cardiovascular_prevention": {
                "lifestyle_interventions": [
                    {
                        "type": "smoking_cessation",
                        "description": "戒烟计划",
                        "duration_weeks": 12,
                        "activities": ["尼古丁替代疗法", "行为咨询", "支持小组"]
                    },
                    {
                        "type": "weight_management",
                        "description": "体重管理",
                        "duration_weeks": 24,
                        "activities": ["饮食调整", "运动计划", "行为改变"]
                    }
                ],
                "nutrition_interventions": [
                    {
                        "type": "dash_diet",
                        "description": "DASH饮食",
                        "guidelines": ["增加蔬果摄入", "减少钠摄入", "选择全谷物"]
                    }
                ],
                "exercise_interventions": [
                    {
                        "type": "aerobic_exercise",
                        "description": "有氧运动",
                        "frequency": "每周5次",
                        "duration": "30分钟",
                        "intensity": "中等强度"
                    }
                ]
            },
            "diabetes_prevention": {
                "lifestyle_interventions": [
                    {
                        "type": "weight_loss",
                        "description": "减重计划",
                        "target": "减重5-10%",
                        "duration_weeks": 16
                    }
                ],
                "nutrition_interventions": [
                    {
                        "type": "low_glycemic_diet",
                        "description": "低血糖指数饮食",
                        "guidelines": ["选择低GI食物", "控制碳水化合物", "增加纤维摄入"]
                    }
                ]
            }
        }
    
    def _load_tcm_prevention_methods(self) -> Dict[str, Any]:
        """加载中医预防方法"""
        return {
            "constitution_based": {
                TCMConstitution.QI_DEFICIENCY: {
                    "dietary_therapy": ["黄芪粥", "人参茶", "山药汤"],
                    "exercise": ["太极拳", "八段锦", "散步"],
                    "acupoints": ["足三里", "气海", "关元"],
                    "lifestyle": ["规律作息", "避免过劳", "保持心情愉快"]
                },
                TCMConstitution.YANG_DEFICIENCY: {
                    "dietary_therapy": ["当归生姜羊肉汤", "肉桂茶", "核桃粥"],
                    "exercise": ["慢跑", "游泳", "瑜伽"],
                    "acupoints": ["命门", "肾俞", "关元"],
                    "lifestyle": ["保暖", "早睡早起", "适度运动"]
                },
                TCMConstitution.YIN_DEFICIENCY: {
                    "dietary_therapy": ["银耳莲子汤", "枸杞茶", "百合粥"],
                    "exercise": ["瑜伽", "太极拳", "散步"],
                    "acupoints": ["三阴交", "太溪", "照海"],
                    "lifestyle": ["避免熬夜", "保持情绪稳定", "适度休息"]
                }
            },
            "seasonal_prevention": {
                "spring": {
                    "principles": ["养肝", "疏肝理气"],
                    "foods": ["春笋", "韭菜", "菠菜"],
                    "activities": ["踏青", "放风筝", "春游"]
                },
                "summer": {
                    "principles": ["养心", "清热解暑"],
                    "foods": ["绿豆", "西瓜", "苦瓜"],
                    "activities": ["游泳", "早晚散步", "避免暴晒"]
                },
                "autumn": {
                    "principles": ["养肺", "润燥"],
                    "foods": ["梨", "百合", "银耳"],
                    "activities": ["登山", "深呼吸", "保持室内湿度"]
                },
                "winter": {
                    "principles": ["养肾", "温阳"],
                    "foods": ["羊肉", "核桃", "黑芝麻"],
                    "activities": ["室内运动", "保暖", "早睡晚起"]
                }
            }
        }
    
    @trace_operation("prevention_plan_generator.generate_plan", SpanKind.INTERNAL)
    async def generate_prevention_plan(
        self,
        user_id: str,
        risk_assessments: List[DiseaseRiskAssessment],
        user_preferences: Dict[str, Any] = None,
        tcm_constitution: Optional[TCMConstitution] = None
    ) -> PreventionPlan:
        """生成预防计划"""
        
        try:
            # 确定目标疾病
            target_diseases = [assessment.disease_name for assessment in risk_assessments 
                             if assessment.risk_level in [RiskLevel.MODERATE, RiskLevel.HIGH, RiskLevel.VERY_HIGH]]
            
            # 生成计划名称和描述
            plan_name = f"个性化预防计划 - {user_id}"
            plan_description = f"基于风险评估的综合预防方案，目标疾病：{', '.join(target_diseases)}"
            
            # 生成各类干预措施
            lifestyle_interventions = await self._generate_lifestyle_interventions(risk_assessments, user_preferences)
            nutrition_interventions = await self._generate_nutrition_interventions(risk_assessments, user_preferences)
            exercise_interventions = await self._generate_exercise_interventions(risk_assessments, user_preferences)
            tcm_interventions = await self._generate_tcm_interventions(risk_assessments, tcm_constitution)
            screening_schedule = await self._generate_screening_schedule(risk_assessments)
            vaccination_schedule = await self._generate_vaccination_schedule(risk_assessments)
            environmental_measures = await self._generate_environmental_measures(risk_assessments)
            
            # 生成进度指标和成功标准
            progress_metrics = self._generate_progress_metrics(target_diseases)
            success_criteria = self._generate_success_criteria(risk_assessments)
            
            return PreventionPlan(
                plan_id=f"prevention_plan_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                user_id=user_id,
                name=plan_name,
                description=plan_description,
                target_diseases=target_diseases,
                prevention_strategies=[PreventionStrategy.PRIMARY, PreventionStrategy.SECONDARY],
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=365),
                lifestyle_interventions=lifestyle_interventions,
                nutrition_interventions=nutrition_interventions,
                exercise_interventions=exercise_interventions,
                tcm_interventions=tcm_interventions,
                screening_schedule=screening_schedule,
                vaccination_schedule=vaccination_schedule,
                environmental_measures=environmental_measures,
                progress_metrics=progress_metrics,
                success_criteria=success_criteria
            )
            
        except Exception as e:
            logger.error(f"预防计划生成失败: {e}")
            raise
    
    async def _generate_lifestyle_interventions(
        self,
        risk_assessments: List[DiseaseRiskAssessment],
        user_preferences: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """生成生活方式干预"""
        interventions = []
        
        # 分析风险因素
        all_risk_factors = []
        for assessment in risk_assessments:
            all_risk_factors.extend(assessment.contributing_factors)
        
        # 戒烟干预
        if any(factor.factor_id == "smoking" for factor in all_risk_factors):
            interventions.append({
                "type": "smoking_cessation",
                "name": "戒烟计划",
                "description": "系统性戒烟支持计划",
                "duration_weeks": 12,
                "phases": [
                    {"week": 1, "goal": "制定戒烟日期", "activities": ["评估吸烟模式", "选择戒烟方法"]},
                    {"week": 2, "goal": "开始戒烟", "activities": ["使用尼古丁替代品", "避免触发因素"]},
                    {"week": 4, "goal": "维持戒烟", "activities": ["应对戒断症状", "寻求支持"]},
                    {"week": 12, "goal": "巩固成果", "activities": ["预防复吸", "建立新习惯"]}
                ],
                "success_metrics": ["戒烟天数", "戒断症状评分", "肺功能改善"]
            })
        
        # 体重管理干预
        if any(factor.factor_id == "obesity" for factor in all_risk_factors):
            interventions.append({
                "type": "weight_management",
                "name": "体重管理计划",
                "description": "科学减重和体重维持计划",
                "duration_weeks": 24,
                "target_weight_loss": "5-10%",
                "strategies": ["饮食控制", "运动增加", "行为改变", "心理支持"],
                "success_metrics": ["体重变化", "BMI改善", "腰围减少"]
            })
        
        # 压力管理干预
        interventions.append({
            "type": "stress_management",
            "name": "压力管理训练",
            "description": "学习有效的压力应对技巧",
            "duration_weeks": 8,
            "techniques": ["深呼吸练习", "渐进性肌肉放松", "正念冥想", "认知重构"],
            "success_metrics": ["压力水平评分", "睡眠质量", "情绪状态"]
        })
        
        return interventions
    
    async def _generate_nutrition_interventions(
        self,
        risk_assessments: List[DiseaseRiskAssessment],
        user_preferences: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """生成营养干预"""
        interventions = []
        
        # 心血管疾病预防饮食
        if any("cardiovascular" in assessment.disease_category.value for assessment in risk_assessments):
            interventions.append({
                "type": "heart_healthy_diet",
                "name": "心脏健康饮食",
                "description": "DASH饮食模式",
                "guidelines": [
                    "每天5-9份蔬果",
                    "选择全谷物",
                    "限制钠摄入(<2300mg/天)",
                    "增加钾摄入",
                    "选择瘦肉和鱼类",
                    "限制饱和脂肪"
                ],
                "meal_planning": True,
                "monitoring": ["血压", "血脂", "体重"]
            })
        
        # 糖尿病预防饮食
        if any("diabetes" in assessment.disease_name for assessment in risk_assessments):
            interventions.append({
                "type": "diabetes_prevention_diet",
                "name": "糖尿病预防饮食",
                "description": "低血糖指数饮食",
                "guidelines": [
                    "选择低GI食物",
                    "控制碳水化合物摄入",
                    "增加膳食纤维",
                    "规律进餐时间",
                    "控制份量",
                    "限制添加糖"
                ],
                "carb_counting": True,
                "monitoring": ["血糖", "糖化血红蛋白", "体重"]
            })
        
        return interventions
    
    async def _generate_exercise_interventions(
        self,
        risk_assessments: List[DiseaseRiskAssessment],
        user_preferences: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """生成运动干预"""
        interventions = []
        
        # 有氧运动计划
        interventions.append({
            "type": "aerobic_exercise",
            "name": "有氧运动计划",
            "description": "提高心肺功能的有氧运动",
            "frequency": "每周5次",
            "duration": "30-60分钟",
            "intensity": "中等强度",
            "activities": ["快走", "慢跑", "游泳", "骑自行车", "跳舞"],
            "progression": {
                "week_1_4": "30分钟，中低强度",
                "week_5_8": "45分钟，中等强度",
                "week_9_12": "60分钟，中等强度"
            },
            "monitoring": ["心率", "运动时长", "主观疲劳感"]
        })
        
        # 力量训练计划
        interventions.append({
            "type": "strength_training",
            "name": "力量训练计划",
            "description": "增强肌肉力量和骨密度",
            "frequency": "每周2-3次",
            "duration": "45分钟",
            "exercises": [
                {"name": "深蹲", "sets": 3, "reps": "10-15"},
                {"name": "俯卧撑", "sets": 3, "reps": "8-12"},
                {"name": "哑铃划船", "sets": 3, "reps": "10-12"},
                {"name": "平板支撑", "sets": 3, "duration": "30-60秒"}
            ],
            "progression": "每2周增加重量或次数",
            "monitoring": ["力量测试", "肌肉量", "骨密度"]
        })
        
        return interventions
    
    async def _generate_tcm_interventions(
        self,
        risk_assessments: List[DiseaseRiskAssessment],
        tcm_constitution: Optional[TCMConstitution] = None
    ) -> List[Dict[str, Any]]:
        """生成中医干预措施"""
        interventions = []
        
        if tcm_constitution:
            constitution_methods = self.tcm_prevention_methods["constitution_based"].get(tcm_constitution, {})
            
            # 食疗干预
            if constitution_methods.get("dietary_therapy"):
                interventions.append({
                    "type": "tcm_dietary_therapy",
                    "name": "中医食疗",
                    "description": f"针对{tcm_constitution.value}体质的食疗方案",
                    "recipes": constitution_methods["dietary_therapy"],
                    "principles": ["药食同源", "因人制宜", "四季调养"],
                    "frequency": "每日1-2次",
                    "duration": "长期坚持"
                })
            
            # 运动养生
            if constitution_methods.get("exercise"):
                interventions.append({
                    "type": "tcm_exercise",
                    "name": "中医运动养生",
                    "description": f"适合{tcm_constitution.value}体质的运动方式",
                    "exercises": constitution_methods["exercise"],
                    "principles": ["动静结合", "循序渐进", "持之以恒"],
                    "frequency": "每日30分钟",
                    "best_time": "早晨或傍晚"
                })
            
            # 穴位保健
            if constitution_methods.get("acupoints"):
                interventions.append({
                    "type": "acupoint_massage",
                    "name": "穴位按摩保健",
                    "description": f"针对{tcm_constitution.value}体质的穴位保健",
                    "acupoints": constitution_methods["acupoints"],
                    "techniques": ["按压", "揉动", "推拿"],
                    "frequency": "每日2次",
                    "duration": "每穴位3-5分钟"
                })
        
        # 季节性养生
        current_season = self._get_current_season()
        seasonal_methods = self.tcm_prevention_methods["seasonal_prevention"].get(current_season, {})
        
        if seasonal_methods:
            interventions.append({
                "type": "seasonal_health_preservation",
                "name": f"{current_season}季养生",
                "description": f"基于中医理论的{current_season}季养生方案",
                "principles": seasonal_methods.get("principles", []),
                "recommended_foods": seasonal_methods.get("foods", []),
                "activities": seasonal_methods.get("activities", []),
                "duration": "整个季节"
            })
        
        return interventions
    
    def _get_current_season(self) -> str:
        """获取当前季节"""
        month = datetime.now().month
        if month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        elif month in [9, 10, 11]:
            return "autumn"
        else:
            return "winter"
    
    async def _generate_screening_schedule(self, risk_assessments: List[DiseaseRiskAssessment]) -> List[Dict[str, Any]]:
        """生成筛查计划"""
        schedule = []
        
        for assessment in risk_assessments:
            if assessment.risk_level in [RiskLevel.MODERATE, RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
                if "cardiovascular" in assessment.disease_category.value:
                    schedule.append({
                        "type": "cardiovascular_screening",
                        "tests": ["血压测量", "血脂检查", "心电图", "超声心动图"],
                        "frequency": "每6个月" if assessment.risk_level == RiskLevel.HIGH else "每年",
                        "next_date": datetime.now() + timedelta(days=180 if assessment.risk_level == RiskLevel.HIGH else 365)
                    })
                
                if "diabetes" in assessment.disease_name:
                    schedule.append({
                        "type": "diabetes_screening",
                        "tests": ["空腹血糖", "糖化血红蛋白", "口服糖耐量试验"],
                        "frequency": "每3个月" if assessment.risk_level == RiskLevel.HIGH else "每6个月",
                        "next_date": datetime.now() + timedelta(days=90 if assessment.risk_level == RiskLevel.HIGH else 180)
                    })
        
        return schedule
    
    async def _generate_vaccination_schedule(self, risk_assessments: List[DiseaseRiskAssessment]) -> List[Dict[str, Any]]:
        """生成疫苗接种计划"""
        schedule = []
        
        # 基础疫苗
        schedule.append({
            "vaccine": "流感疫苗",
            "type": "seasonal",
            "frequency": "每年",
            "next_date": datetime.now() + timedelta(days=365),
            "priority": "high"
        })
        
        # 根据风险评估添加特定疫苗
        for assessment in risk_assessments:
            if "respiratory" in assessment.disease_category.value:
                schedule.append({
                    "vaccine": "肺炎疫苗",
                    "type": "high_risk",
                    "frequency": "5年一次",
                    "next_date": datetime.now() + timedelta(days=30),
                    "priority": "medium"
                })
        
        return schedule
    
    async def _generate_environmental_measures(self, risk_assessments: List[DiseaseRiskAssessment]) -> List[Dict[str, Any]]:
        """生成环境改善措施"""
        measures = []
        
        # 空气质量改善
        measures.append({
            "type": "air_quality_improvement",
            "name": "空气质量改善",
            "actions": [
                "使用空气净化器",
                "定期通风换气",
                "避免在污染严重时户外运动",
                "室内种植净化空气的植物"
            ],
            "monitoring": "空气质量指数"
        })
        
        # 居住环境优化
        measures.append({
            "type": "home_environment_optimization",
            "name": "居住环境优化",
            "actions": [
                "保持室内清洁",
                "控制室内湿度",
                "减少化学清洁剂使用",
                "确保充足的自然光照"
            ],
            "monitoring": "室内环境质量"
        })
        
        return measures
    
    def _generate_progress_metrics(self, target_diseases: List[str]) -> List[str]:
        """生成进度指标"""
        metrics = [
            "体重变化",
            "血压变化",
            "血脂水平",
            "血糖水平",
            "运动频率和强度",
            "饮食质量评分",
            "睡眠质量",
            "压力水平",
            "生活质量评分"
        ]
        
        # 根据目标疾病添加特定指标
        for disease in target_diseases:
            if "cardiovascular" in disease:
                metrics.extend(["心率变异性", "动脉硬化指数"])
            elif "diabetes" in disease:
                metrics.extend(["糖化血红蛋白", "胰岛素敏感性"])
        
        return list(set(metrics))  # 去重
    
    def _generate_success_criteria(self, risk_assessments: List[DiseaseRiskAssessment]) -> List[str]:
        """生成成功标准"""
        criteria = []
        
        for assessment in risk_assessments:
            if assessment.risk_level == RiskLevel.HIGH:
                criteria.append(f"{assessment.disease_name}风险降低至中等水平")
            elif assessment.risk_level == RiskLevel.MODERATE:
                criteria.append(f"{assessment.disease_name}风险降低至低水平")
        
        # 通用成功标准
        criteria.extend([
            "体重维持在健康范围内",
            "血压控制在正常范围",
            "血脂水平改善",
            "运动习惯建立并维持",
            "饮食质量显著改善",
            "生活质量评分提高20%以上"
        ])
        
        return criteria

class IntelligentPreventiveMedicineEngine:
    """智能预防医学引擎"""
    
    def __init__(self, config: Dict[str, Any], metrics_collector: Optional[MetricsCollector] = None):
        self.config = config
        self.metrics_collector = metrics_collector
        
        # 核心组件
        self.risk_predictor = None
        self.prevention_plan_generator = None
        
        # 数据存储
        self.risk_assessments = {}
        self.prevention_plans = {}
        self.screening_recommendations = {}
        self.vaccination_recommendations = {}
        self.environmental_assessments = {}
        self.family_histories = {}
        self.prevention_outcomes = {}
        
        # 配置
        self.risk_thresholds = {}
        self.screening_guidelines = {}
        self.vaccination_schedules = {}
        
        logger.info("智能预防医学引擎初始化完成")
    
    async def initialize(self):
        """初始化引擎"""
        try:
            await self._load_configuration()
            await self._initialize_components()
            logger.info("智能预防医学引擎初始化成功")
        except Exception as e:
            logger.error(f"智能预防医学引擎初始化失败: {e}")
            raise
    
    async def _load_configuration(self):
        """加载配置"""
        self.risk_thresholds = self.config.get("risk_thresholds", {})
        self.screening_guidelines = self.config.get("screening_guidelines", {})
        self.vaccination_schedules = self.config.get("vaccination_schedules", {})
    
    async def _initialize_components(self):
        """初始化组件"""
        self.risk_predictor = RiskPredictor()
        self.prevention_plan_generator = PreventionPlanGenerator()
    
    @trace_operation("preventive_medicine_engine.assess_disease_risk", SpanKind.INTERNAL)
    async def assess_disease_risk(
        self,
        user_id: str,
        disease_name: str,
        user_data: Dict[str, Any]
    ) -> DiseaseRiskAssessment:
        """评估疾病风险"""
        
        try:
            # 获取家族史和环境数据
            family_history = self.family_histories.get(user_id)
            environmental_data = self.environmental_assessments.get(user_id)
            
            # 进行风险评估
            assessment = await self.risk_predictor.assess_disease_risk(
                user_id=user_id,
                disease_name=disease_name,
                user_data=user_data,
                family_history=family_history,
                environmental_data=environmental_data
            )
            
            # 存储评估结果
            if user_id not in self.risk_assessments:
                self.risk_assessments[user_id] = {}
            self.risk_assessments[user_id][disease_name] = assessment
            
            # 记录指标
            if self.metrics_collector:
                self.metrics_collector.increment_counter(
                    "disease_risk_assessments_total",
                    {"disease": disease_name, "risk_level": assessment.risk_level.value}
                )
            
            logger.info(f"用户 {user_id} 的 {disease_name} 风险评估完成，风险等级: {assessment.risk_level.value}")
            return assessment
            
        except Exception as e:
            logger.error(f"疾病风险评估失败: {e}")
            if self.metrics_collector:
                self.metrics_collector.increment_counter("disease_risk_assessment_errors_total")
            raise
    
    @trace_operation("preventive_medicine_engine.generate_prevention_plan", SpanKind.INTERNAL)
    async def generate_prevention_plan(
        self,
        user_id: str,
        user_preferences: Dict[str, Any] = None
    ) -> PreventionPlan:
        """生成预防计划"""
        
        try:
            # 获取用户的风险评估结果
            user_assessments = self.risk_assessments.get(user_id, {})
            if not user_assessments:
                raise ValueError(f"用户 {user_id} 没有风险评估数据")
            
            assessments_list = list(user_assessments.values())
            
            # 获取中医体质信息
            tcm_constitution = user_preferences.get("tcm_constitution") if user_preferences else None
            
            # 生成预防计划
            plan = await self.prevention_plan_generator.generate_prevention_plan(
                user_id=user_id,
                risk_assessments=assessments_list,
                user_preferences=user_preferences,
                tcm_constitution=tcm_constitution
            )
            
            # 存储预防计划
            self.prevention_plans[user_id] = plan
            
            # 记录指标
            if self.metrics_collector:
                self.metrics_collector.increment_counter(
                    "prevention_plans_generated_total",
                    {"user_id": user_id}
                )
            
            logger.info(f"用户 {user_id} 的预防计划生成完成")
            return plan
            
        except Exception as e:
            logger.error(f"预防计划生成失败: {e}")
            if self.metrics_collector:
                self.metrics_collector.increment_counter("prevention_plan_generation_errors_total")
            raise
    
    async def update_family_history(self, user_id: str, family_history: FamilyHealthHistory):
        """更新家族健康史"""
        self.family_histories[user_id] = family_history
        logger.info(f"用户 {user_id} 的家族健康史已更新")
    
    async def update_environmental_assessment(self, user_id: str, environmental_data: EnvironmentalRiskAssessment):
        """更新环境风险评估"""
        self.environmental_assessments[user_id] = environmental_data
        logger.info(f"用户 {user_id} 的环境风险评估已更新")
    
    async def track_prevention_outcome(self, user_id: str, outcome: PreventionOutcome):
        """跟踪预防效果"""
        if user_id not in self.prevention_outcomes:
            self.prevention_outcomes[user_id] = []
        self.prevention_outcomes[user_id].append(outcome)
        
        # 记录指标
        if self.metrics_collector:
            self.metrics_collector.histogram(
                "prevention_adherence_rate",
                outcome.adherence_rate,
                {"user_id": user_id}
            )
        
        logger.info(f"用户 {user_id} 的预防效果已记录")
    
    async def get_prevention_summary(self, user_id: str) -> Dict[str, Any]:
        """获取预防医学总结"""
        
        try:
            # 获取风险评估
            risk_assessments = self.risk_assessments.get(user_id, {})
            
            # 获取预防计划
            prevention_plan = self.prevention_plans.get(user_id)
            
            # 获取预防效果
            outcomes = self.prevention_outcomes.get(user_id, [])
            
            # 计算总体风险水平
            overall_risk = self._calculate_overall_risk(list(risk_assessments.values()))
            
            # 计算预防效果
            prevention_effectiveness = self._calculate_prevention_effectiveness(outcomes)
            
            # 生成建议
            recommendations = await self._generate_summary_recommendations(
                risk_assessments, prevention_plan, outcomes
            )
            
            return {
                "user_id": user_id,
                "summary_date": datetime.now().isoformat(),
                "overall_risk_level": overall_risk,
                "risk_assessments": {
                    disease: {
                        "risk_level": assessment.risk_level.value,
                        "risk_score": assessment.risk_score,
                        "last_assessment": assessment.assessment_date.isoformat()
                    }
                    for disease, assessment in risk_assessments.items()
                },
                "prevention_plan": {
                    "plan_id": prevention_plan.plan_id if prevention_plan else None,
                    "target_diseases": prevention_plan.target_diseases if prevention_plan else [],
                    "status": prevention_plan.status if prevention_plan else None
                } if prevention_plan else None,
                "prevention_effectiveness": prevention_effectiveness,
                "recommendations": recommendations,
                "next_actions": self._get_next_actions(risk_assessments, prevention_plan)
            }
            
        except Exception as e:
            logger.error(f"获取预防医学总结失败: {e}")
            raise
    
    def _calculate_overall_risk(self, assessments: List[DiseaseRiskAssessment]) -> str:
        """计算总体风险水平"""
        if not assessments:
            return "unknown"
        
        risk_scores = [assessment.risk_score for assessment in assessments]
        avg_risk = sum(risk_scores) / len(risk_scores)
        
        if avg_risk < 0.2:
            return "low"
        elif avg_risk < 0.5:
            return "moderate"
        else:
            return "high"
    
    def _calculate_prevention_effectiveness(self, outcomes: List[PreventionOutcome]) -> Dict[str, Any]:
        """计算预防效果"""
        if not outcomes:
            return {"status": "no_data"}
        
        latest_outcome = outcomes[-1]
        
        return {
            "adherence_rate": latest_outcome.adherence_rate,
            "quality_of_life_score": latest_outcome.quality_of_life_score,
            "risk_reduction": latest_outcome.risk_reduction,
            "satisfaction_score": latest_outcome.satisfaction_score,
            "measurement_date": latest_outcome.measurement_date.isoformat()
        }
    
    async def _generate_summary_recommendations(
        self,
        risk_assessments: Dict[str, DiseaseRiskAssessment],
        prevention_plan: Optional[PreventionPlan],
        outcomes: List[PreventionOutcome]
    ) -> List[str]:
        """生成总结建议"""
        recommendations = []
        
        # 基于风险评估的建议
        high_risk_diseases = [
            disease for disease, assessment in risk_assessments.items()
            if assessment.risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]
        ]
        
        if high_risk_diseases:
            recommendations.append(f"高风险疾病 {', '.join(high_risk_diseases)} 需要重点关注和干预")
        
        # 基于预防计划的建议
        if prevention_plan and prevention_plan.status == "active":
            recommendations.append("继续执行当前预防计划，定期评估效果")
        elif not prevention_plan:
            recommendations.append("建议制定个性化预防计划")
        
        # 基于预防效果的建议
        if outcomes:
            latest_outcome = outcomes[-1]
            if latest_outcome.adherence_rate < 0.7:
                recommendations.append("提高预防措施的依从性，寻求专业指导")
            if latest_outcome.quality_of_life_score and latest_outcome.quality_of_life_score < 7:
                recommendations.append("关注生活质量改善，调整预防策略")
        
        return recommendations
    
    def _get_next_actions(
        self,
        risk_assessments: Dict[str, DiseaseRiskAssessment],
        prevention_plan: Optional[PreventionPlan]
    ) -> List[str]:
        """获取下一步行动"""
        actions = []
        
        # 检查是否需要更新风险评估
        for disease, assessment in risk_assessments.items():
            if assessment.next_assessment_date and assessment.next_assessment_date <= datetime.now():
                actions.append(f"更新 {disease} 风险评估")
        
        # 检查预防计划状态
        if prevention_plan:
            if prevention_plan.end_date and prevention_plan.end_date <= datetime.now():
                actions.append("更新预防计划")
        
        # 通用行动
        actions.extend([
            "定期监测健康指标",
            "保持健康的生活方式",
            "按时进行健康筛查"
        ])
        
        return actions
    
    async def get_prevention_statistics(self) -> Dict[str, Any]:
        """获取预防医学统计信息"""
        
        try:
            total_users = len(self.risk_assessments)
            total_assessments = sum(len(assessments) for assessments in self.risk_assessments.values())
            total_plans = len(self.prevention_plans)
            
            # 风险分布统计
            risk_distribution = {}
            for assessments in self.risk_assessments.values():
                for assessment in assessments.values():
                    risk_level = assessment.risk_level.value
                    risk_distribution[risk_level] = risk_distribution.get(risk_level, 0) + 1
            
            # 疾病类别统计
            disease_stats = {}
            for assessments in self.risk_assessments.values():
                for disease, assessment in assessments.items():
                    disease_stats[disease] = disease_stats.get(disease, 0) + 1
            
            # 预防效果统计
            effectiveness_stats = {}
            if self.prevention_outcomes:
                all_outcomes = []
                for outcomes in self.prevention_outcomes.values():
                    all_outcomes.extend(outcomes)
                
                if all_outcomes:
                    avg_adherence = sum(o.adherence_rate for o in all_outcomes) / len(all_outcomes)
                    avg_satisfaction = sum(o.satisfaction_score for o in all_outcomes if o.satisfaction_score) / len([o for o in all_outcomes if o.satisfaction_score])
                    
                    effectiveness_stats = {
                        "average_adherence_rate": avg_adherence,
                        "average_satisfaction_score": avg_satisfaction,
                        "total_outcomes_tracked": len(all_outcomes)
                    }
            
            return {
                "total_users": total_users,
                "total_risk_assessments": total_assessments,
                "total_prevention_plans": total_plans,
                "risk_level_distribution": risk_distribution,
                "disease_statistics": disease_stats,
                "prevention_effectiveness": effectiveness_stats,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取预防医学统计信息失败: {e}")
            raise

def initialize_preventive_medicine_engine(
    config: Dict[str, Any],
    metrics_collector: Optional[MetricsCollector] = None
) -> IntelligentPreventiveMedicineEngine:
    """初始化智能预防医学引擎"""
    engine = IntelligentPreventiveMedicineEngine(config, metrics_collector)
    return engine

# 全局引擎实例
_preventive_medicine_engine: Optional[IntelligentPreventiveMedicineEngine] = None

def get_preventive_medicine_engine() -> Optional[IntelligentPreventiveMedicineEngine]:
    """获取智能预防医学引擎实例"""
    return _preventive_medicine_engine 