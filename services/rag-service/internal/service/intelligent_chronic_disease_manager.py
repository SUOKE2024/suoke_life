#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能慢病管理引擎 - 实现慢性疾病的全生命周期智能管理
结合现代慢病管理理念和中医"治未病"思想，为慢性疾病患者提供个性化的综合管理方案
"""

from typing import Dict, List, Any, Optional, Tuple, Union, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta, date
from loguru import logger
import warnings
warnings.filterwarnings('ignore')

from ..observability.metrics import MetricsCollector
from ..observability.tracing import trace_operation, SpanKind

class ChronicDiseaseType(str, Enum):
    """慢性疾病类型"""
    DIABETES = "diabetes"                       # 糖尿病
    HYPERTENSION = "hypertension"               # 高血压
    CARDIOVASCULAR = "cardiovascular"           # 心血管疾病
    COPD = "copd"                              # 慢性阻塞性肺疾病
    ASTHMA = "asthma"                          # 哮喘
    ARTHRITIS = "arthritis"                     # 关节炎
    OSTEOPOROSIS = "osteoporosis"               # 骨质疏松
    CHRONIC_KIDNEY = "chronic_kidney"           # 慢性肾病
    THYROID_DISORDER = "thyroid_disorder"       # 甲状腺疾病
    DEPRESSION = "depression"                   # 抑郁症
    ANXIETY = "anxiety"                         # 焦虑症
    CHRONIC_PAIN = "chronic_pain"               # 慢性疼痛
    OBESITY = "obesity"                         # 肥胖症
    METABOLIC_SYNDROME = "metabolic_syndrome"   # 代谢综合征

class DiseaseStage(str, Enum):
    """疾病分期"""
    EARLY = "early"                # 早期
    MILD = "mild"                  # 轻度
    MODERATE = "moderate"          # 中度
    SEVERE = "severe"              # 重度
    ADVANCED = "advanced"          # 晚期
    REMISSION = "remission"        # 缓解期
    EXACERBATION = "exacerbation"  # 急性加重期

class ManagementGoal(str, Enum):
    """管理目标"""
    CONTROL = "control"                    # 控制病情
    PREVENT_COMPLICATIONS = "prevent_complications"  # 预防并发症
    IMPROVE_QUALITY = "improve_quality"    # 改善生活质量
    SLOW_PROGRESSION = "slow_progression"  # 延缓进展
    SYMPTOM_RELIEF = "symptom_relief"      # 症状缓解
    FUNCTIONAL_IMPROVEMENT = "functional_improvement"  # 功能改善

class InterventionType(str, Enum):
    """干预类型"""
    MEDICATION = "medication"              # 药物治疗
    LIFESTYLE = "lifestyle"                # 生活方式
    DIET = "diet"                         # 饮食管理
    EXERCISE = "exercise"                 # 运动治疗
    MONITORING = "monitoring"             # 监测管理
    EDUCATION = "education"               # 健康教育
    PSYCHOLOGICAL = "psychological"        # 心理支持
    TCM = "tcm"                          # 中医治疗
    REHABILITATION = "rehabilitation"      # 康复治疗

class AlertLevel(str, Enum):
    """预警级别"""
    LOW = "low"                    # 低风险
    MEDIUM = "medium"              # 中风险
    HIGH = "high"                  # 高风险
    CRITICAL = "critical"          # 危急

@dataclass
class ChronicDisease:
    """慢性疾病信息"""
    disease_id: str
    user_id: str
    disease_type: ChronicDiseaseType
    diagnosis_date: datetime
    current_stage: DiseaseStage
    severity_score: float                   # 严重程度评分 (0.0-10.0)
    
    # 诊断信息
    icd_code: Optional[str] = None
    diagnostic_criteria: List[str] = field(default_factory=list)
    comorbidities: List[str] = field(default_factory=list)
    
    # 症状信息
    primary_symptoms: List[str] = field(default_factory=list)
    secondary_symptoms: List[str] = field(default_factory=list)
    symptom_severity: Dict[str, float] = field(default_factory=dict)
    
    # 生物标志物
    biomarkers: Dict[str, float] = field(default_factory=dict)
    target_ranges: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    
    # 并发症风险
    complication_risks: Dict[str, float] = field(default_factory=dict)
    
    # 预后信息
    prognosis: str = ""
    life_expectancy_impact: Optional[float] = None
    
    # 更新时间
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class ManagementPlan:
    """慢病管理计划"""
    plan_id: str
    user_id: str
    disease_id: str
    plan_name: str
    description: str
    
    # 管理目标
    primary_goals: List[ManagementGoal] = field(default_factory=list)
    target_metrics: Dict[str, float] = field(default_factory=dict)
    
    # 药物治疗方案
    medication_regimen: Dict[str, Any] = field(default_factory=dict)
    
    # 生活方式干预
    lifestyle_interventions: List[Dict[str, Any]] = field(default_factory=list)
    
    # 饮食管理
    dietary_plan: Dict[str, Any] = field(default_factory=dict)
    
    # 运动处方
    exercise_prescription: Dict[str, Any] = field(default_factory=dict)
    
    # 监测计划
    monitoring_schedule: List[Dict[str, Any]] = field(default_factory=list)
    
    # 健康教育
    education_modules: List[str] = field(default_factory=list)
    
    # 心理支持
    psychological_support: Dict[str, Any] = field(default_factory=dict)
    
    # 中医治疗
    tcm_interventions: List[Dict[str, Any]] = field(default_factory=list)
    
    # 康复计划
    rehabilitation_plan: Dict[str, Any] = field(default_factory=dict)
    
    # 应急预案
    emergency_protocols: List[Dict[str, Any]] = field(default_factory=list)
    
    # 计划周期
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    review_frequency: int = 30  # 复查频率（天）
    
    # 状态
    status: str = "active"
    created_by: str = "system"
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class MonitoringData:
    """监测数据"""
    user_id: str
    disease_id: str
    measurement_date: datetime
    data_type: str                          # 数据类型
    
    # 生理指标
    vital_signs: Dict[str, float] = field(default_factory=dict)
    
    # 实验室检查
    lab_results: Dict[str, float] = field(default_factory=dict)
    
    # 症状评分
    symptom_scores: Dict[str, float] = field(default_factory=dict)
    
    # 生活质量评分
    quality_of_life_score: Optional[float] = None
    
    # 功能状态评分
    functional_status_score: Optional[float] = None
    
    # 依从性评分
    adherence_score: Optional[float] = None
    
    # 自我管理能力评分
    self_management_score: Optional[float] = None
    
    # 数据来源
    data_source: str = "manual"  # manual, device, lab, etc.
    
    # 数据质量
    data_quality_score: float = 1.0
    
    # 备注
    notes: Optional[str] = None

@dataclass
class RiskAlert:
    """风险预警"""
    alert_id: str
    user_id: str
    disease_id: str
    alert_date: datetime
    alert_level: AlertLevel
    alert_type: str                         # 预警类型
    
    # 预警内容
    title: str
    description: str
    risk_factors: List[str] = field(default_factory=list)
    
    # 触发条件
    trigger_conditions: Dict[str, Any] = field(default_factory=dict)
    
    # 建议措施
    recommended_actions: List[str] = field(default_factory=list)
    
    # 紧急程度
    urgency: str = "normal"  # low, normal, high, urgent
    
    # 处理状态
    status: str = "active"  # active, acknowledged, resolved
    
    # 处理记录
    resolution_notes: Optional[str] = None
    resolved_date: Optional[datetime] = None
    resolved_by: Optional[str] = None

@dataclass
class TreatmentOutcome:
    """治疗效果"""
    user_id: str
    disease_id: str
    plan_id: str
    evaluation_date: datetime
    
    # 目标达成情况
    goal_achievement: Dict[str, bool] = field(default_factory=dict)
    
    # 指标改善情况
    metric_improvements: Dict[str, float] = field(default_factory=dict)
    
    # 症状改善
    symptom_improvements: Dict[str, float] = field(default_factory=dict)
    
    # 生活质量改善
    quality_of_life_improvement: Optional[float] = None
    
    # 功能状态改善
    functional_improvement: Optional[float] = None
    
    # 并发症发生情况
    complications_occurred: List[str] = field(default_factory=list)
    
    # 不良反应
    adverse_events: List[str] = field(default_factory=list)
    
    # 依从性评估
    adherence_assessment: Dict[str, float] = field(default_factory=dict)
    
    # 满意度评分
    satisfaction_score: Optional[float] = None
    
    # 成本效益
    cost_effectiveness: Optional[float] = None
    
    # 下一步建议
    next_steps: List[str] = field(default_factory=list)

class ChronicDiseaseAnalyzer:
    """慢性疾病分析器"""
    
    def __init__(self):
        self.disease_knowledge_base = self._load_disease_knowledge_base()
        self.risk_models = self._load_risk_models()
        self.treatment_guidelines = self._load_treatment_guidelines()
        self.tcm_protocols = self._load_tcm_protocols()
    
    def _load_disease_knowledge_base(self) -> Dict[str, Any]:
        """加载疾病知识库"""
        return {
            ChronicDiseaseType.DIABETES: {
                "name": "糖尿病",
                "description": "以高血糖为特征的代谢性疾病",
                "diagnostic_criteria": [
                    "空腹血糖≥7.0mmol/L",
                    "餐后2小时血糖≥11.1mmol/L",
                    "糖化血红蛋白≥6.5%",
                    "随机血糖≥11.1mmol/L伴典型症状"
                ],
                "key_biomarkers": {
                    "fasting_glucose": {"normal": (3.9, 6.1), "target": (4.4, 7.0)},
                    "hba1c": {"normal": (4.0, 6.0), "target": (6.0, 7.0)},
                    "postprandial_glucose": {"normal": (3.9, 7.8), "target": (4.4, 10.0)}
                },
                "complications": [
                    "糖尿病肾病", "糖尿病视网膜病变", "糖尿病神经病变",
                    "心血管疾病", "糖尿病足", "酮症酸中毒"
                ],
                "risk_factors": [
                    "年龄≥45岁", "超重或肥胖", "家族史", "高血压",
                    "血脂异常", "妊娠糖尿病史", "多囊卵巢综合征"
                ]
            },
            ChronicDiseaseType.HYPERTENSION: {
                "name": "高血压",
                "description": "以动脉血压持续升高为特征的心血管疾病",
                "diagnostic_criteria": [
                    "收缩压≥140mmHg",
                    "舒张压≥90mmHg",
                    "非同日三次测量均超过正常值"
                ],
                "key_biomarkers": {
                    "systolic_bp": {"normal": (90, 120), "target": (90, 140)},
                    "diastolic_bp": {"normal": (60, 80), "target": (60, 90)},
                    "mean_arterial_pressure": {"normal": (70, 93), "target": (70, 107)}
                },
                "complications": [
                    "心肌梗死", "心力衰竭", "脑卒中", "肾功能不全",
                    "视网膜病变", "主动脉夹层"
                ],
                "risk_factors": [
                    "年龄", "性别", "家族史", "吸烟", "饮酒",
                    "高盐饮食", "肥胖", "缺乏运动", "精神压力"
                ]
            },
            # 可以继续添加其他疾病...
        }
    
    def _load_risk_models(self) -> Dict[str, Any]:
        """加载风险预测模型"""
        return {
            "diabetes_complications": {
                "model_type": "random_forest",
                "features": [
                    "hba1c", "duration", "age", "bmi", "blood_pressure",
                    "cholesterol", "smoking", "family_history"
                ],
                "risk_thresholds": {
                    "low": 0.2,
                    "medium": 0.4,
                    "high": 0.7,
                    "critical": 0.9
                }
            },
            "cardiovascular_events": {
                "model_type": "gradient_boosting",
                "features": [
                    "age", "gender", "systolic_bp", "cholesterol",
                    "smoking", "diabetes", "family_history"
                ],
                "risk_thresholds": {
                    "low": 0.1,
                    "medium": 0.2,
                    "high": 0.3,
                    "critical": 0.5
                }
            }
        }
    
    def _load_treatment_guidelines(self) -> Dict[str, Any]:
        """加载治疗指南"""
        return {
            ChronicDiseaseType.DIABETES: {
                "first_line_medications": [
                    "二甲双胍", "SGLT-2抑制剂", "GLP-1受体激动剂"
                ],
                "lifestyle_interventions": [
                    "饮食控制", "规律运动", "体重管理", "戒烟限酒"
                ],
                "monitoring_frequency": {
                    "hba1c": "3个月",
                    "血糖": "每日",
                    "血压": "每次就诊",
                    "血脂": "年度"
                },
                "target_goals": {
                    "hba1c": 7.0,
                    "fasting_glucose": 7.0,
                    "postprandial_glucose": 10.0,
                    "blood_pressure": "130/80"
                }
            },
            ChronicDiseaseType.HYPERTENSION: {
                "first_line_medications": [
                    "ACE抑制剂", "ARB", "钙通道阻滞剂", "利尿剂"
                ],
                "lifestyle_interventions": [
                    "低盐饮食", "减重", "规律运动", "限制饮酒", "戒烟"
                ],
                "monitoring_frequency": {
                    "血压": "每日",
                    "心电图": "年度",
                    "肾功能": "半年",
                    "眼底": "年度"
                },
                "target_goals": {
                    "systolic_bp": 130,
                    "diastolic_bp": 80,
                    "cardiovascular_risk": 0.1
                }
            }
        }
    
    def _load_tcm_protocols(self) -> Dict[str, Any]:
        """加载中医治疗方案"""
        return {
            ChronicDiseaseType.DIABETES: {
                "syndrome_patterns": {
                    "阴虚热盛": {
                        "symptoms": ["口渴多饮", "消瘦", "尿频", "五心烦热"],
                        "tongue": "红舌少苔",
                        "pulse": "细数",
                        "formula": "玉女煎加减",
                        "herbs": ["生地黄", "麦冬", "知母", "石膏", "牛膝"]
                    },
                    "气阴两虚": {
                        "symptoms": ["乏力", "气短", "口干", "自汗"],
                        "tongue": "淡红舌少苔",
                        "pulse": "细弱",
                        "formula": "生脉散合玉液汤",
                        "herbs": ["人参", "麦冬", "五味子", "天花粉", "葛根"]
                    }
                },
                "acupuncture_points": [
                    "胰俞", "脾俞", "肾俞", "足三里", "三阴交", "太溪"
                ],
                "dietary_therapy": {
                    "recommended": ["苦瓜", "冬瓜", "黄瓜", "菠菜", "芹菜"],
                    "avoided": ["甜食", "油腻", "辛辣", "烟酒"]
                }
            },
            ChronicDiseaseType.HYPERTENSION: {
                "syndrome_patterns": {
                    "肝阳上亢": {
                        "symptoms": ["头痛", "眩晕", "急躁易怒", "面红目赤"],
                        "tongue": "红舌黄苔",
                        "pulse": "弦数",
                        "formula": "天麻钩藤饮",
                        "herbs": ["天麻", "钩藤", "石决明", "栀子", "黄芩"]
                    },
                    "痰湿壅盛": {
                        "symptoms": ["头重如裹", "胸闷", "恶心", "肢体沉重"],
                        "tongue": "胖大舌苔腻",
                        "pulse": "滑",
                        "formula": "半夏白术天麻汤",
                        "herbs": ["半夏", "白术", "天麻", "陈皮", "茯苓"]
                    }
                },
                "acupuncture_points": [
                    "百会", "风池", "太冲", "三阴交", "足三里", "曲池"
                ],
                "dietary_therapy": {
                    "recommended": ["芹菜", "海带", "黑木耳", "山楂", "荷叶"],
                    "avoided": ["高盐", "高脂", "辛辣", "浓茶", "咖啡"]
                }
            }
        }
    
    @trace_operation("chronic_disease_analyzer.analyze_disease_progression", SpanKind.INTERNAL)
    async def analyze_disease_progression(
        self,
        disease: ChronicDisease,
        monitoring_history: List[MonitoringData]
    ) -> Dict[str, Any]:
        """分析疾病进展"""
        try:
            # 计算疾病进展趋势
            progression_trend = await self._calculate_progression_trend(disease, monitoring_history)
            
            # 评估当前疾病状态
            current_status = await self._assess_current_status(disease, monitoring_history)
            
            # 预测未来风险
            future_risks = await self._predict_future_risks(disease, monitoring_history)
            
            # 识别恶化因素
            deterioration_factors = await self._identify_deterioration_factors(disease, monitoring_history)
            
            # 生成进展报告
            progression_report = {
                "disease_id": disease.disease_id,
                "analysis_date": datetime.now(),
                "progression_trend": progression_trend,
                "current_status": current_status,
                "future_risks": future_risks,
                "deterioration_factors": deterioration_factors,
                "recommendations": await self._generate_progression_recommendations(
                    disease, progression_trend, current_status, future_risks
                )
            }
            
            return progression_report
            
        except Exception as e:
            logger.error(f"分析疾病进展失败: {e}")
            raise
    
    async def _calculate_progression_trend(
        self,
        disease: ChronicDisease,
        monitoring_history: List[MonitoringData]
    ) -> Dict[str, Any]:
        """计算疾病进展趋势"""
        if not monitoring_history:
            return {"trend": "insufficient_data", "confidence": 0.0}
        
        # 按时间排序
        sorted_data = sorted(monitoring_history, key=lambda x: x.measurement_date)
        
        # 提取关键指标
        key_metrics = self._get_key_metrics_for_disease(disease.disease_type)
        trends = {}
        
        for metric in key_metrics:
            values = []
            dates = []
            
            for data in sorted_data:
                if metric in data.vital_signs:
                    values.append(data.vital_signs[metric])
                    dates.append(data.measurement_date)
                elif metric in data.lab_results:
                    values.append(data.lab_results[metric])
                    dates.append(data.measurement_date)
            
            if len(values) >= 3:
                # 计算趋势
                trend_analysis = self._analyze_metric_trend(values, dates)
                trends[metric] = trend_analysis
        
        # 综合评估整体趋势
        overall_trend = self._calculate_overall_trend(trends)
        
        return {
            "overall_trend": overall_trend,
            "metric_trends": trends,
            "trend_confidence": self._calculate_trend_confidence(trends),
            "analysis_period": {
                "start_date": sorted_data[0].measurement_date,
                "end_date": sorted_data[-1].measurement_date,
                "data_points": len(sorted_data)
            }
        }
    
    def _get_key_metrics_for_disease(self, disease_type: ChronicDiseaseType) -> List[str]:
        """获取疾病的关键指标"""
        metric_mapping = {
            ChronicDiseaseType.DIABETES: ["fasting_glucose", "hba1c", "postprandial_glucose"],
            ChronicDiseaseType.HYPERTENSION: ["systolic_bp", "diastolic_bp"],
            ChronicDiseaseType.CARDIOVASCULAR: ["cholesterol", "ldl", "hdl", "triglycerides"],
            # 可以继续添加其他疾病的关键指标
        }
        return metric_mapping.get(disease_type, [])
    
    def _analyze_metric_trend(self, values: List[float], dates: List[datetime]) -> Dict[str, Any]:
        """分析单个指标的趋势"""
        # 简单的线性回归分析
        x = np.array([(d - dates[0]).days for d in dates])
        y = np.array(values)
        
        # 计算斜率
        slope = np.polyfit(x, y, 1)[0]
        
        # 计算变化率
        change_rate = (values[-1] - values[0]) / values[0] * 100 if values[0] != 0 else 0
        
        # 判断趋势方向
        if abs(slope) < 0.01:
            direction = "stable"
        elif slope > 0:
            direction = "increasing"
        else:
            direction = "decreasing"
        
        return {
            "direction": direction,
            "slope": slope,
            "change_rate": change_rate,
            "current_value": values[-1],
            "baseline_value": values[0],
            "volatility": np.std(values)
        }
    
    def _calculate_overall_trend(self, metric_trends: Dict[str, Any]) -> str:
        """计算整体趋势"""
        if not metric_trends:
            return "insufficient_data"
        
        improving_count = 0
        worsening_count = 0
        stable_count = 0
        
        for trend in metric_trends.values():
            direction = trend.get("direction", "stable")
            if direction == "improving":
                improving_count += 1
            elif direction == "worsening":
                worsening_count += 1
            else:
                stable_count += 1
        
        total_metrics = len(metric_trends)
        
        if improving_count > total_metrics * 0.6:
            return "improving"
        elif worsening_count > total_metrics * 0.6:
            return "worsening"
        elif stable_count > total_metrics * 0.6:
            return "stable"
        else:
            return "mixed"
    
    def _calculate_trend_confidence(self, metric_trends: Dict[str, Any]) -> float:
        """计算趋势置信度"""
        if not metric_trends:
            return 0.0
        
        confidence_scores = []
        for trend in metric_trends.values():
            # 基于数据点数量和变异性计算置信度
            volatility = trend.get("volatility", 1.0)
            confidence = max(0.0, min(1.0, 1.0 - volatility / 10.0))
            confidence_scores.append(confidence)
        
        return np.mean(confidence_scores)

class ManagementPlanGenerator:
    """管理计划生成器"""
    
    def __init__(self):
        self.treatment_templates = self._load_treatment_templates()
        self.intervention_library = self._load_intervention_library()
        self.monitoring_protocols = self._load_monitoring_protocols()
    
    def _load_treatment_templates(self) -> Dict[str, Any]:
        """加载治疗模板"""
        return {
            ChronicDiseaseType.DIABETES: {
                "mild": {
                    "primary_goals": [ManagementGoal.CONTROL, ManagementGoal.PREVENT_COMPLICATIONS],
                    "medication_approach": "lifestyle_first",
                    "monitoring_frequency": "monthly",
                    "education_priority": "high"
                },
                "moderate": {
                    "primary_goals": [ManagementGoal.CONTROL, ManagementGoal.SLOW_PROGRESSION],
                    "medication_approach": "combination_therapy",
                    "monitoring_frequency": "bi_weekly",
                    "education_priority": "high"
                },
                "severe": {
                    "primary_goals": [ManagementGoal.CONTROL, ManagementGoal.PREVENT_COMPLICATIONS],
                    "medication_approach": "intensive_therapy",
                    "monitoring_frequency": "weekly",
                    "education_priority": "critical"
                }
            }
        }
    
    def _load_intervention_library(self) -> Dict[str, Any]:
        """加载干预措施库"""
        return {
            InterventionType.LIFESTYLE: {
                "smoking_cessation": {
                    "name": "戒烟计划",
                    "description": "系统性戒烟干预方案",
                    "components": ["行为疗法", "药物辅助", "心理支持"],
                    "duration": 90,
                    "success_rate": 0.3
                },
                "weight_management": {
                    "name": "体重管理",
                    "description": "科学减重和体重维持方案",
                    "components": ["饮食控制", "运动计划", "行为改变"],
                    "duration": 180,
                    "success_rate": 0.6
                }
            },
            InterventionType.DIET: {
                "diabetes_diet": {
                    "name": "糖尿病饮食",
                    "description": "糖尿病专用饮食方案",
                    "principles": ["控制总热量", "均衡营养", "定时定量"],
                    "restrictions": ["限制简单糖", "控制脂肪", "增加纤维"],
                    "meal_planning": True
                },
                "dash_diet": {
                    "name": "DASH饮食",
                    "description": "降压饮食方案",
                    "principles": ["低钠", "高钾", "高纤维"],
                    "food_groups": ["蔬菜", "水果", "全谷物", "低脂乳制品"],
                    "sodium_limit": 2300  # mg/day
                }
            }
        }
    
    def _load_monitoring_protocols(self) -> Dict[str, Any]:
        """加载监测方案"""
        return {
            ChronicDiseaseType.DIABETES: {
                "daily": ["血糖", "血压", "体重"],
                "weekly": ["症状评估", "足部检查"],
                "monthly": ["糖化血红蛋白", "血脂", "肾功能"],
                "quarterly": ["眼底检查", "神经病变筛查"],
                "annually": ["心电图", "胸片", "全面体检"]
            },
            ChronicDiseaseType.HYPERTENSION: {
                "daily": ["血压", "体重"],
                "weekly": ["症状评估"],
                "monthly": ["血压记录分析"],
                "quarterly": ["血脂", "肾功能", "心电图"],
                "annually": ["眼底检查", "超声心动图", "动脉硬化检查"]
            }
        }
    
    @trace_operation("management_plan_generator.generate_plan", SpanKind.INTERNAL)
    async def generate_management_plan(
        self,
        disease: ChronicDisease,
        user_preferences: Dict[str, Any] = None,
        current_treatments: List[Dict[str, Any]] = None
    ) -> ManagementPlan:
        """生成管理计划"""
        try:
            # 确定管理目标
            primary_goals = await self._determine_management_goals(disease)
            
            # 生成药物治疗方案
            medication_regimen = await self._generate_medication_regimen(disease, current_treatments)
            
            # 生成生活方式干预
            lifestyle_interventions = await self._generate_lifestyle_interventions(disease, user_preferences)
            
            # 生成饮食计划
            dietary_plan = await self._generate_dietary_plan(disease, user_preferences)
            
            # 生成运动处方
            exercise_prescription = await self._generate_exercise_prescription(disease, user_preferences)
            
            # 生成监测计划
            monitoring_schedule = await self._generate_monitoring_schedule(disease)
            
            # 生成健康教育模块
            education_modules = await self._generate_education_modules(disease)
            
            # 生成心理支持方案
            psychological_support = await self._generate_psychological_support(disease)
            
            # 生成中医干预方案
            tcm_interventions = await self._generate_tcm_interventions(disease)
            
            # 生成康复计划
            rehabilitation_plan = await self._generate_rehabilitation_plan(disease)
            
            # 生成应急预案
            emergency_protocols = await self._generate_emergency_protocols(disease)
            
            # 创建管理计划
            plan = ManagementPlan(
                plan_id=f"plan_{disease.user_id}_{disease.disease_id}_{datetime.now().strftime('%Y%m%d')}",
                user_id=disease.user_id,
                disease_id=disease.disease_id,
                plan_name=f"{disease.disease_type.value}管理计划",
                description=f"针对{disease.disease_type.value}的个性化综合管理方案",
                primary_goals=primary_goals,
                target_metrics=await self._determine_target_metrics(disease),
                medication_regimen=medication_regimen,
                lifestyle_interventions=lifestyle_interventions,
                dietary_plan=dietary_plan,
                exercise_prescription=exercise_prescription,
                monitoring_schedule=monitoring_schedule,
                education_modules=education_modules,
                psychological_support=psychological_support,
                tcm_interventions=tcm_interventions,
                rehabilitation_plan=rehabilitation_plan,
                emergency_protocols=emergency_protocols,
                review_frequency=await self._determine_review_frequency(disease)
            )
            
            return plan
            
        except Exception as e:
            logger.error(f"生成管理计划失败: {e}")
            raise
    
    async def _determine_management_goals(self, disease: ChronicDisease) -> List[ManagementGoal]:
        """确定管理目标"""
        goals = [ManagementGoal.CONTROL]  # 基本目标
        
        # 根据疾病阶段添加目标
        if disease.current_stage in [DiseaseStage.EARLY, DiseaseStage.MILD]:
            goals.append(ManagementGoal.PREVENT_COMPLICATIONS)
        elif disease.current_stage in [DiseaseStage.MODERATE, DiseaseStage.SEVERE]:
            goals.extend([ManagementGoal.SLOW_PROGRESSION, ManagementGoal.IMPROVE_QUALITY])
        elif disease.current_stage == DiseaseStage.ADVANCED:
            goals.extend([ManagementGoal.SYMPTOM_RELIEF, ManagementGoal.IMPROVE_QUALITY])
        
        # 根据症状添加目标
        if disease.primary_symptoms:
            goals.append(ManagementGoal.SYMPTOM_RELIEF)
        
        # 根据并发症风险添加目标
        if disease.complication_risks:
            goals.append(ManagementGoal.PREVENT_COMPLICATIONS)
        
        return list(set(goals))  # 去重
    
    async def _generate_medication_regimen(
        self,
        disease: ChronicDisease,
        current_treatments: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """生成药物治疗方案"""
        regimen = {
            "current_medications": current_treatments or [],
            "recommended_changes": [],
            "new_medications": [],
            "medication_schedule": {},
            "monitoring_requirements": [],
            "drug_interactions": [],
            "contraindications": []
        }
        
        # 根据疾病类型和阶段推荐药物
        if disease.disease_type == ChronicDiseaseType.DIABETES:
            if disease.current_stage == DiseaseStage.MILD:
                regimen["new_medications"].append({
                    "name": "二甲双胍",
                    "dosage": "500mg",
                    "frequency": "每日两次",
                    "timing": "餐后服用",
                    "duration": "长期",
                    "monitoring": ["肾功能", "维生素B12"]
                })
            elif disease.current_stage in [DiseaseStage.MODERATE, DiseaseStage.SEVERE]:
                regimen["new_medications"].extend([
                    {
                        "name": "二甲双胍",
                        "dosage": "1000mg",
                        "frequency": "每日两次",
                        "timing": "餐后服用"
                    },
                    {
                        "name": "SGLT-2抑制剂",
                        "dosage": "10mg",
                        "frequency": "每日一次",
                        "timing": "晨起服用"
                    }
                ])
        
        elif disease.disease_type == ChronicDiseaseType.HYPERTENSION:
            if disease.current_stage == DiseaseStage.MILD:
                regimen["new_medications"].append({
                    "name": "ACE抑制剂",
                    "dosage": "5mg",
                    "frequency": "每日一次",
                    "timing": "晨起服用",
                    "monitoring": ["血压", "肾功能", "血钾"]
                })
        
        return regimen
    
    async def _generate_lifestyle_interventions(
        self,
        disease: ChronicDisease,
        user_preferences: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """生成生活方式干预"""
        interventions = []
        
        # 通用干预措施
        interventions.append({
            "type": "sleep_hygiene",
            "name": "睡眠卫生",
            "description": "改善睡眠质量和睡眠习惯",
            "recommendations": [
                "保持规律作息",
                "睡前避免电子设备",
                "创造舒适睡眠环境",
                "避免睡前大量进食"
            ],
            "target": "每晚7-8小时优质睡眠"
        })
        
        interventions.append({
            "type": "stress_management",
            "name": "压力管理",
            "description": "学习有效的压力应对技巧",
            "recommendations": [
                "深呼吸练习",
                "冥想或正念练习",
                "时间管理",
                "社交支持"
            ],
            "target": "降低慢性压力水平"
        })
        
        # 疾病特异性干预
        if disease.disease_type == ChronicDiseaseType.DIABETES:
            interventions.append({
                "type": "blood_glucose_monitoring",
                "name": "血糖监测",
                "description": "规律监测血糖变化",
                "recommendations": [
                    "每日测量空腹血糖",
                    "餐后2小时血糖监测",
                    "记录血糖日志",
                    "识别血糖波动模式"
                ],
                "target": "血糖控制在目标范围内"
            })
        
        elif disease.disease_type == ChronicDiseaseType.HYPERTENSION:
            interventions.append({
                "type": "blood_pressure_monitoring",
                "name": "血压监测",
                "description": "规律监测血压变化",
                "recommendations": [
                    "每日定时测量血压",
                    "记录血压日志",
                    "识别血压波动规律",
                    "正确的测量技巧"
                ],
                "target": "血压控制在130/80mmHg以下"
            })
        
        return interventions
    
    async def _generate_dietary_plan(
        self,
        disease: ChronicDisease,
        user_preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """生成饮食计划"""
        plan = {
            "general_principles": [],
            "specific_recommendations": {},
            "meal_planning": {},
            "nutritional_targets": {},
            "foods_to_limit": [],
            "foods_to_encourage": [],
            "meal_timing": {},
            "portion_control": {}
        }
        
        if disease.disease_type == ChronicDiseaseType.DIABETES:
            plan.update({
                "general_principles": [
                    "控制总热量摄入",
                    "均衡营养搭配",
                    "定时定量进餐",
                    "选择低血糖指数食物"
                ],
                "nutritional_targets": {
                    "carbohydrate": "45-65%总热量",
                    "protein": "15-20%总热量",
                    "fat": "20-35%总热量",
                    "fiber": "25-35g/天",
                    "sodium": "<2300mg/天"
                },
                "foods_to_encourage": [
                    "全谷物", "蔬菜", "水果", "瘦肉", "鱼类",
                    "豆类", "坚果", "低脂乳制品"
                ],
                "foods_to_limit": [
                    "精制糖", "甜饮料", "高脂肪食物",
                    "加工食品", "高钠食物"
                ],
                "meal_timing": {
                    "breakfast": "7:00-8:00",
                    "lunch": "12:00-13:00",
                    "dinner": "18:00-19:00",
                    "snacks": "适量健康零食"
                }
            })
        
        elif disease.disease_type == ChronicDiseaseType.HYPERTENSION:
            plan.update({
                "general_principles": [
                    "低钠饮食",
                    "增加钾摄入",
                    "控制体重",
                    "限制饮酒"
                ],
                "nutritional_targets": {
                    "sodium": "<1500mg/天",
                    "potassium": "3500-4700mg/天",
                    "calcium": "1000-1200mg/天",
                    "magnesium": "400-420mg/天"
                },
                "foods_to_encourage": [
                    "蔬菜", "水果", "全谷物", "低脂乳制品",
                    "瘦肉", "鱼类", "豆类", "坚果"
                ],
                "foods_to_limit": [
                    "高钠食物", "加工食品", "腌制食品",
                    "快餐", "含糖饮料"
                ]
            })
        
        return plan
    
    async def _generate_exercise_prescription(
        self,
        disease: ChronicDisease,
        user_preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """生成运动处方"""
        prescription = {
            "exercise_goals": [],
            "aerobic_exercise": {},
            "resistance_training": {},
            "flexibility_training": {},
            "balance_training": {},
            "exercise_schedule": {},
            "safety_considerations": [],
            "progression_plan": {}
        }
        
        # 通用运动目标
        prescription["exercise_goals"] = [
            "改善心肺功能",
            "增强肌肉力量",
            "提高柔韧性",
            "控制体重",
            "改善血糖/血压控制"
        ]
        
        if disease.disease_type == ChronicDiseaseType.DIABETES:
            prescription.update({
                "aerobic_exercise": {
                    "type": "中等强度有氧运动",
                    "examples": ["快走", "游泳", "骑车", "跳舞"],
                    "frequency": "每周5天",
                    "duration": "30-60分钟",
                    "intensity": "50-70%最大心率"
                },
                "resistance_training": {
                    "type": "阻力训练",
                    "examples": ["举重", "弹力带", "体重训练"],
                    "frequency": "每周2-3次",
                    "duration": "20-30分钟",
                    "intensity": "中等强度"
                },
                "safety_considerations": [
                    "运动前检查血糖",
                    "携带快速糖源",
                    "避免空腹运动",
                    "注意足部保护",
                    "逐渐增加运动强度"
                ]
            })
        
        elif disease.disease_type == ChronicDiseaseType.HYPERTENSION:
            prescription.update({
                "aerobic_exercise": {
                    "type": "有氧运动为主",
                    "examples": ["快走", "慢跑", "游泳", "骑车"],
                    "frequency": "每周5-7天",
                    "duration": "30-45分钟",
                    "intensity": "40-60%最大心率"
                },
                "resistance_training": {
                    "type": "轻到中等强度阻力训练",
                    "frequency": "每周2-3次",
                    "duration": "20-30分钟",
                    "intensity": "轻到中等强度"
                },
                "safety_considerations": [
                    "运动前测量血压",
                    "避免憋气动作",
                    "避免头部低于心脏的动作",
                    "逐渐热身和放松",
                    "监测运动中血压反应"
                ]
            })
        
        return prescription
    
    async def _generate_monitoring_schedule(self, disease: ChronicDisease) -> List[Dict[str, Any]]:
        """生成监测计划"""
        schedule = []
        
        protocols = self.monitoring_protocols.get(disease.disease_type, {})
        
        for frequency, tests in protocols.items():
            for test in tests:
                schedule.append({
                    "test_name": test,
                    "frequency": frequency,
                    "importance": "high" if frequency in ["daily", "weekly"] else "medium",
                    "target_values": self._get_target_values(disease.disease_type, test),
                    "instructions": self._get_test_instructions(test)
                })
        
        return schedule
    
    def _get_target_values(self, disease_type: ChronicDiseaseType, test_name: str) -> Dict[str, Any]:
        """获取检查项目的目标值"""
        targets = {
            ChronicDiseaseType.DIABETES: {
                "血糖": {"fasting": "<7.0mmol/L", "postprandial": "<10.0mmol/L"},
                "糖化血红蛋白": {"target": "<7.0%"},
                "血压": {"target": "<130/80mmHg"},
                "血脂": {"ldl": "<2.6mmol/L", "hdl": ">1.0mmol/L"}
            },
            ChronicDiseaseType.HYPERTENSION: {
                "血压": {"target": "<130/80mmHg"},
                "血脂": {"ldl": "<3.4mmol/L", "hdl": ">1.0mmol/L"},
                "肾功能": {"creatinine": "正常范围", "urea": "正常范围"}
            }
        }
        
        return targets.get(disease_type, {}).get(test_name, {})
    
    def _get_test_instructions(self, test_name: str) -> List[str]:
        """获取检查说明"""
        instructions = {
            "血糖": ["空腹8-12小时", "避免剧烈运动", "正常饮水"],
            "血压": ["静坐5分钟后测量", "避免咖啡因", "使用合适袖带"],
            "体重": ["晨起空腹测量", "穿轻便衣物", "同一时间测量"]
        }
        
        return instructions.get(test_name, ["按医嘱执行"])
    
    async def _generate_education_modules(self, disease: ChronicDisease) -> List[str]:
        """生成健康教育模块"""
        modules = [
            "疾病基础知识",
            "自我监测技能",
            "药物管理",
            "饮食营养",
            "运动指导",
            "并发症预防",
            "应急处理"
        ]
        
        # 根据疾病类型添加特定模块
        if disease.disease_type == ChronicDiseaseType.DIABETES:
            modules.extend([
                "血糖监测技巧",
                "胰岛素注射",
                "低血糖处理",
                "足部护理",
                "眼部保健"
            ])
        
        elif disease.disease_type == ChronicDiseaseType.HYPERTENSION:
            modules.extend([
                "血压测量技巧",
                "钠盐控制",
                "压力管理",
                "心血管保护"
            ])
        
        return modules
    
    async def _generate_psychological_support(self, disease: ChronicDisease) -> Dict[str, Any]:
        """生成心理支持方案"""
        return {
            "assessment": {
                "depression_screening": "PHQ-9量表",
                "anxiety_screening": "GAD-7量表",
                "quality_of_life": "SF-36量表",
                "disease_acceptance": "疾病接受度评估"
            },
            "interventions": [
                {
                    "type": "认知行为疗法",
                    "description": "帮助改变负面思维模式",
                    "frequency": "每周1次",
                    "duration": "8-12周"
                },
                {
                    "type": "支持小组",
                    "description": "与其他患者分享经验",
                    "frequency": "每月2次",
                    "duration": "持续"
                },
                {
                    "type": "正念训练",
                    "description": "减轻压力和焦虑",
                    "frequency": "每日练习",
                    "duration": "15-20分钟"
                }
            ],
            "resources": [
                "心理健康热线",
                "在线支持社区",
                "心理健康应用",
                "专业心理咨询师"
            ]
        }
    
    async def _generate_tcm_interventions(self, disease: ChronicDisease) -> List[Dict[str, Any]]:
        """生成中医干预方案"""
        interventions = []
        
        tcm_data = self._load_tcm_protocols().get(disease.disease_type, {})
        
        if tcm_data:
            # 中药治疗
            if "syndrome_patterns" in tcm_data:
                interventions.append({
                    "type": "中药治疗",
                    "description": "基于辨证论治的中药方剂",
                    "syndrome_patterns": tcm_data["syndrome_patterns"],
                    "frequency": "每日2次",
                    "duration": "4-8周",
                    "monitoring": "定期复诊调方"
                })
            
            # 针灸治疗
            if "acupuncture_points" in tcm_data:
                interventions.append({
                    "type": "针灸治疗",
                    "description": "针刺相关穴位调理脏腑功能",
                    "acupoints": tcm_data["acupuncture_points"],
                    "frequency": "每周2-3次",
                    "duration": "4-6周",
                    "course": "10-15次为一疗程"
                })
            
            # 食疗
            if "dietary_therapy" in tcm_data:
                interventions.append({
                    "type": "中医食疗",
                    "description": "药食同源的饮食调理",
                    "recommended_foods": tcm_data["dietary_therapy"].get("recommended", []),
                    "foods_to_avoid": tcm_data["dietary_therapy"].get("avoided", []),
                    "frequency": "日常饮食",
                    "principles": "寓医于食，调理体质"
                })
        
        # 通用中医养生方法
        interventions.extend([
            {
                "type": "八段锦",
                "description": "传统养生功法",
                "frequency": "每日1次",
                "duration": "20-30分钟",
                "benefits": "调和气血，强身健体"
            },
            {
                "type": "太极拳",
                "description": "柔和的运动养生",
                "frequency": "每日1次",
                "duration": "30-45分钟",
                "benefits": "平衡阴阳，宁心安神"
            }
        ])
        
        return interventions
    
    async def _generate_rehabilitation_plan(self, disease: ChronicDisease) -> Dict[str, Any]:
        """生成康复计划"""
        plan = {
            "assessment": {
                "functional_capacity": "功能能力评估",
                "quality_of_life": "生活质量评估",
                "disability_level": "残疾程度评估"
            },
            "goals": [
                "改善功能状态",
                "提高生活质量",
                "增强自理能力",
                "预防功能退化"
            ],
            "interventions": [],
            "timeline": "12-24周",
            "outcome_measures": [
                "功能独立性评分",
                "生活质量量表",
                "运动能力测试"
            ]
        }
        
        # 根据疾病类型添加特定康复内容
        if disease.disease_type == ChronicDiseaseType.CARDIOVASCULAR:
            plan["interventions"].extend([
                {
                    "type": "心脏康复",
                    "description": "分阶段心脏康复训练",
                    "phases": ["急性期", "亚急性期", "维持期"],
                    "components": ["运动训练", "健康教育", "心理支持"]
                }
            ])
        
        elif disease.disease_type == ChronicDiseaseType.ARTHRITIS:
            plan["interventions"].extend([
                {
                    "type": "关节康复",
                    "description": "关节功能训练和疼痛管理",
                    "components": ["关节活动度训练", "肌力训练", "疼痛管理"]
                }
            ])
        
        return plan
    
    async def _generate_emergency_protocols(self, disease: ChronicDisease) -> List[Dict[str, Any]]:
        """生成应急预案"""
        protocols = []
        
        if disease.disease_type == ChronicDiseaseType.DIABETES:
            protocols.extend([
                {
                    "condition": "低血糖",
                    "symptoms": ["出汗", "心悸", "饥饿感", "头晕", "意识模糊"],
                    "immediate_actions": [
                        "立即测量血糖",
                        "服用15g快速糖源",
                        "15分钟后复测血糖",
                        "如仍低于4.0mmol/L，重复治疗"
                    ],
                    "when_to_seek_help": "意识不清或无法自行处理时",
                    "prevention": "规律进餐，调整药物剂量"
                },
                {
                    "condition": "高血糖",
                    "symptoms": ["多饮", "多尿", "乏力", "视物模糊"],
                    "immediate_actions": [
                        "测量血糖和酮体",
                        "增加水分摄入",
                        "联系医生调整治疗",
                        "监测症状变化"
                    ],
                    "when_to_seek_help": "血糖>16.7mmol/L或出现酮症",
                    "prevention": "按时服药，监测血糖"
                }
            ])
        
        elif disease.disease_type == ChronicDiseaseType.HYPERTENSION:
            protocols.append({
                "condition": "高血压急症",
                "symptoms": ["剧烈头痛", "视物模糊", "胸痛", "呼吸困难"],
                "immediate_actions": [
                    "立即测量血压",
                    "保持安静休息",
                    "服用急救药物",
                    "准备就医"
                ],
                "when_to_seek_help": "收缩压>180mmHg或出现器官损害症状",
                "prevention": "规律服药，监测血压"
            })
        
        return protocols
    
    async def _determine_target_metrics(self, disease: ChronicDisease) -> Dict[str, float]:
        """确定目标指标"""
        targets = {}
        
        if disease.disease_type == ChronicDiseaseType.DIABETES:
            targets.update({
                "hba1c": 7.0,
                "fasting_glucose": 7.0,
                "postprandial_glucose": 10.0,
                "systolic_bp": 130,
                "diastolic_bp": 80,
                "ldl_cholesterol": 2.6
            })
        
        elif disease.disease_type == ChronicDiseaseType.HYPERTENSION:
            targets.update({
                "systolic_bp": 130,
                "diastolic_bp": 80,
                "ldl_cholesterol": 3.4,
                "bmi": 25.0
            })
        
        return targets
    
    async def _determine_review_frequency(self, disease: ChronicDisease) -> int:
        """确定复查频率（天）"""
        frequency_mapping = {
            DiseaseStage.EARLY: 90,
            DiseaseStage.MILD: 60,
            DiseaseStage.MODERATE: 30,
            DiseaseStage.SEVERE: 14,
            DiseaseStage.ADVANCED: 7
        }
        
        return frequency_mapping.get(disease.current_stage, 30)

class IntelligentChronicDiseaseManager:
    """智能慢病管理引擎"""
    
    def __init__(self, config: Dict[str, Any], metrics_collector: Optional[MetricsCollector] = None):
        self.config = config
        self.metrics_collector = metrics_collector or MetricsCollector()
        
        # 核心组件
        self.disease_analyzer = None
        self.plan_generator = None
        
        # 数据存储
        self.diseases = {}  # user_id -> List[ChronicDisease]
        self.management_plans = {}  # user_id -> List[ManagementPlan]
        self.monitoring_data = {}  # user_id -> List[MonitoringData]
        self.risk_alerts = {}  # user_id -> List[RiskAlert]
        self.treatment_outcomes = {}  # user_id -> List[TreatmentOutcome]
        
        # 配置
        self.alert_thresholds = {}
        self.risk_models = {}
        
        logger.info("智能慢病管理引擎初始化完成")
    
    async def initialize(self):
        """初始化引擎"""
        try:
            await self._load_configuration()
            await self._initialize_components()
            logger.info("智能慢病管理引擎初始化成功")
        except Exception as e:
            logger.error(f"智能慢病管理引擎初始化失败: {e}")
            raise
    
    async def _load_configuration(self):
        """加载配置"""
        self.alert_thresholds = self.config.get("alert_thresholds", {})
        self.risk_models = self.config.get("risk_models", {})
    
    async def _initialize_components(self):
        """初始化组件"""
        self.disease_analyzer = ChronicDiseaseAnalyzer()
        self.plan_generator = ManagementPlanGenerator()
    
    @trace_operation("chronic_disease_manager.register_disease", SpanKind.INTERNAL)
    async def register_chronic_disease(
        self,
        user_id: str,
        disease_data: Dict[str, Any]
    ) -> ChronicDisease:
        """注册慢性疾病"""
        try:
            # 创建疾病对象
            disease = ChronicDisease(
                disease_id=f"disease_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                user_id=user_id,
                disease_type=ChronicDiseaseType(disease_data["disease_type"]),
                diagnosis_date=datetime.fromisoformat(disease_data["diagnosis_date"]),
                current_stage=DiseaseStage(disease_data.get("current_stage", "mild")),
                severity_score=disease_data.get("severity_score", 5.0),
                icd_code=disease_data.get("icd_code"),
                diagnostic_criteria=disease_data.get("diagnostic_criteria", []),
                comorbidities=disease_data.get("comorbidities", []),
                primary_symptoms=disease_data.get("primary_symptoms", []),
                secondary_symptoms=disease_data.get("secondary_symptoms", []),
                symptom_severity=disease_data.get("symptom_severity", {}),
                biomarkers=disease_data.get("biomarkers", {}),
                target_ranges=disease_data.get("target_ranges", {}),
                complication_risks=disease_data.get("complication_risks", {}),
                prognosis=disease_data.get("prognosis", ""),
                life_expectancy_impact=disease_data.get("life_expectancy_impact")
            )
            
            # 存储疾病信息
            if user_id not in self.diseases:
                self.diseases[user_id] = []
            self.diseases[user_id].append(disease)
            
            # 记录指标
            self.metrics_collector.increment_counter(
                "chronic_disease_registered",
                {"disease_type": disease.disease_type.value}
            )
            
            logger.info(f"用户 {user_id} 注册慢性疾病: {disease.disease_type.value}")
            return disease
            
        except Exception as e:
            logger.error(f"注册慢性疾病失败: {e}")
            raise
    
    @trace_operation("chronic_disease_manager.generate_management_plan", SpanKind.INTERNAL)
    async def generate_management_plan(
        self,
        user_id: str,
        disease_id: str,
        user_preferences: Dict[str, Any] = None
    ) -> ManagementPlan:
        """生成管理计划"""
        try:
            # 获取疾病信息
            disease = self._get_disease_by_id(user_id, disease_id)
            if not disease:
                raise ValueError(f"未找到疾病ID: {disease_id}")
            
            # 获取当前治疗方案
            current_treatments = self._get_current_treatments(user_id, disease_id)
            
            # 生成管理计划
            plan = await self.plan_generator.generate_management_plan(
                disease, user_preferences, current_treatments
            )
            
            # 存储管理计划
            if user_id not in self.management_plans:
                self.management_plans[user_id] = []
            self.management_plans[user_id].append(plan)
            
            # 记录指标
            self.metrics_collector.increment_counter(
                "management_plan_generated",
                {"disease_type": disease.disease_type.value}
            )
            
            logger.info(f"为用户 {user_id} 生成管理计划: {plan.plan_id}")
            return plan
            
        except Exception as e:
            logger.error(f"生成管理计划失败: {e}")
            raise
    
    @trace_operation("chronic_disease_manager.record_monitoring_data", SpanKind.INTERNAL)
    async def record_monitoring_data(
        self,
        user_id: str,
        disease_id: str,
        monitoring_data: Dict[str, Any]
    ) -> MonitoringData:
        """记录监测数据"""
        try:
            # 创建监测数据对象
            data = MonitoringData(
                user_id=user_id,
                disease_id=disease_id,
                measurement_date=datetime.fromisoformat(
                    monitoring_data.get("measurement_date", datetime.now().isoformat())
                ),
                data_type=monitoring_data.get("data_type", "routine"),
                vital_signs=monitoring_data.get("vital_signs", {}),
                lab_results=monitoring_data.get("lab_results", {}),
                symptom_scores=monitoring_data.get("symptom_scores", {}),
                quality_of_life_score=monitoring_data.get("quality_of_life_score"),
                functional_status_score=monitoring_data.get("functional_status_score"),
                adherence_score=monitoring_data.get("adherence_score"),
                self_management_score=monitoring_data.get("self_management_score"),
                data_source=monitoring_data.get("data_source", "manual"),
                data_quality_score=monitoring_data.get("data_quality_score", 1.0),
                notes=monitoring_data.get("notes")
            )
            
            # 存储监测数据
            if user_id not in self.monitoring_data:
                self.monitoring_data[user_id] = []
            self.monitoring_data[user_id].append(data)
            
            # 检查是否需要生成预警
            await self._check_for_alerts(user_id, disease_id, data)
            
            # 记录指标
            self.metrics_collector.increment_counter(
                "monitoring_data_recorded",
                {"data_type": data.data_type}
            )
            
            logger.info(f"记录用户 {user_id} 监测数据")
            return data
            
        except Exception as e:
            logger.error(f"记录监测数据失败: {e}")
            raise
    
    async def _check_for_alerts(
        self,
        user_id: str,
        disease_id: str,
        monitoring_data: MonitoringData
    ):
        """检查是否需要生成预警"""
        try:
            disease = self._get_disease_by_id(user_id, disease_id)
            if not disease:
                return
            
            alerts = []
            
            # 检查生理指标异常
            for metric, value in monitoring_data.vital_signs.items():
                alert = await self._check_vital_sign_alert(disease, metric, value)
                if alert:
                    alerts.append(alert)
            
            # 检查实验室结果异常
            for metric, value in monitoring_data.lab_results.items():
                alert = await self._check_lab_result_alert(disease, metric, value)
                if alert:
                    alerts.append(alert)
            
            # 检查症状恶化
            for symptom, score in monitoring_data.symptom_scores.items():
                alert = await self._check_symptom_alert(disease, symptom, score)
                if alert:
                    alerts.append(alert)
            
            # 存储预警
            for alert_data in alerts:
                alert = RiskAlert(
                    alert_id=f"alert_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    user_id=user_id,
                    disease_id=disease_id,
                    alert_date=datetime.now(),
                    **alert_data
                )
                
                if user_id not in self.risk_alerts:
                    self.risk_alerts[user_id] = []
                self.risk_alerts[user_id].append(alert)
                
                logger.warning(f"生成风险预警: {alert.title}")
        
        except Exception as e:
            logger.error(f"检查预警失败: {e}")
    
    async def _check_vital_sign_alert(
        self,
        disease: ChronicDisease,
        metric: str,
        value: float
    ) -> Optional[Dict[str, Any]]:
        """检查生理指标预警"""
        thresholds = self.alert_thresholds.get(disease.disease_type.value, {}).get(metric, {})
        
        if not thresholds:
            return None
        
        if value >= thresholds.get("critical_high", float('inf')):
            return {
                "alert_level": AlertLevel.CRITICAL,
                "alert_type": "vital_sign_critical",
                "title": f"{metric}严重异常",
                "description": f"{metric}值为{value}，超过危急阈值",
                "risk_factors": [f"{metric}过高"],
                "recommended_actions": ["立即就医", "紧急处理"],
                "urgency": "urgent"
            }
        elif value >= thresholds.get("high", float('inf')):
            return {
                "alert_level": AlertLevel.HIGH,
                "alert_type": "vital_sign_high",
                "title": f"{metric}偏高",
                "description": f"{metric}值为{value}，超过正常范围",
                "risk_factors": [f"{metric}升高"],
                "recommended_actions": ["调整治疗方案", "增加监测频率"],
                "urgency": "high"
            }
        elif value <= thresholds.get("critical_low", float('-inf')):
            return {
                "alert_level": AlertLevel.CRITICAL,
                "alert_type": "vital_sign_critical",
                "title": f"{metric}严重偏低",
                "description": f"{metric}值为{value}，低于危急阈值",
                "risk_factors": [f"{metric}过低"],
                "recommended_actions": ["立即就医", "紧急处理"],
                "urgency": "urgent"
            }
        elif value <= thresholds.get("low", float('-inf')):
            return {
                "alert_level": AlertLevel.MEDIUM,
                "alert_type": "vital_sign_low",
                "title": f"{metric}偏低",
                "description": f"{metric}值为{value}，低于正常范围",
                "risk_factors": [f"{metric}降低"],
                "recommended_actions": ["调整治疗方案", "增加监测频率"],
                "urgency": "normal"
            }
        
        return None
    
    async def _check_lab_result_alert(
        self,
        disease: ChronicDisease,
        metric: str,
        value: float
    ) -> Optional[Dict[str, Any]]:
        """检查实验室结果预警"""
        # 类似于生理指标检查，但针对实验室结果
        return await self._check_vital_sign_alert(disease, metric, value)
    
    async def _check_symptom_alert(
        self,
        disease: ChronicDisease,
        symptom: str,
        score: float
    ) -> Optional[Dict[str, Any]]:
        """检查症状预警"""
        if score >= 8.0:  # 假设症状评分0-10分
            return {
                "alert_level": AlertLevel.HIGH,
                "alert_type": "symptom_severe",
                "title": f"{symptom}症状严重",
                "description": f"{symptom}评分为{score}，症状较重",
                "risk_factors": [f"{symptom}加重"],
                "recommended_actions": ["症状管理", "医生咨询"],
                "urgency": "high"
            }
        elif score >= 6.0:
            return {
                "alert_level": AlertLevel.MEDIUM,
                "alert_type": "symptom_moderate",
                "title": f"{symptom}症状加重",
                "description": f"{symptom}评分为{score}，需要关注",
                "risk_factors": [f"{symptom}恶化"],
                "recommended_actions": ["调整治疗", "密切观察"],
                "urgency": "normal"
            }
        
        return None
    
    def _get_disease_by_id(self, user_id: str, disease_id: str) -> Optional[ChronicDisease]:
        """根据ID获取疾病信息"""
        user_diseases = self.diseases.get(user_id, [])
        for disease in user_diseases:
            if disease.disease_id == disease_id:
                return disease
        return None
    
    def _get_current_treatments(self, user_id: str, disease_id: str) -> List[Dict[str, Any]]:
        """获取当前治疗方案"""
        user_plans = self.management_plans.get(user_id, [])
        current_treatments = []
        
        for plan in user_plans:
            if plan.disease_id == disease_id and plan.status == "active":
                current_treatments.extend(plan.medication_regimen.get("current_medications", []))
        
        return current_treatments
    
    async def get_disease_summary(self, user_id: str) -> Dict[str, Any]:
        """获取疾病管理摘要"""
        try:
            user_diseases = self.diseases.get(user_id, [])
            user_plans = self.management_plans.get(user_id, [])
            user_monitoring = self.monitoring_data.get(user_id, [])
            user_alerts = self.risk_alerts.get(user_id, [])
            user_outcomes = self.treatment_outcomes.get(user_id, [])
            
            # 计算统计信息
            active_diseases = len(user_diseases)
            active_plans = len([p for p in user_plans if p.status == "active"])
            recent_monitoring = len([m for m in user_monitoring 
                                   if (datetime.now() - m.measurement_date).days <= 30])
            active_alerts = len([a for a in user_alerts if a.status == "active"])
            
            # 分析疾病控制状态
            disease_control = await self._analyze_disease_control(user_id)
            
            # 生成摘要建议
            summary_recommendations = await self._generate_summary_recommendations(
                user_diseases, user_plans, user_monitoring, user_alerts
            )
            
            # 计算下一步行动
            next_actions = self._get_next_actions(user_diseases, user_plans, user_alerts)
            
            summary = {
                "user_id": user_id,
                "summary_date": datetime.now(),
                "statistics": {
                    "active_diseases": active_diseases,
                    "active_management_plans": active_plans,
                    "recent_monitoring_records": recent_monitoring,
                    "active_alerts": active_alerts
                },
                "disease_control": disease_control,
                "recent_trends": await self._analyze_recent_trends(user_id),
                "risk_assessment": await self._assess_overall_risk(user_id),
                "treatment_effectiveness": await self._evaluate_treatment_effectiveness(user_id),
                "recommendations": summary_recommendations,
                "next_actions": next_actions,
                "upcoming_appointments": await self._get_upcoming_appointments(user_id)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"获取疾病管理摘要失败: {e}")
            raise
    
    async def _analyze_disease_control(self, user_id: str) -> Dict[str, Any]:
        """分析疾病控制状态"""
        user_diseases = self.diseases.get(user_id, [])
        user_monitoring = self.monitoring_data.get(user_id, [])
        
        control_status = {}
        
        for disease in user_diseases:
            # 获取最近的监测数据
            recent_data = [m for m in user_monitoring 
                          if m.disease_id == disease.disease_id and 
                          (datetime.now() - m.measurement_date).days <= 30]
            
            if recent_data:
                # 分析控制状态
                latest_data = max(recent_data, key=lambda x: x.measurement_date)
                control_score = await self._calculate_control_score(disease, latest_data)
                
                control_status[disease.disease_type.value] = {
                    "control_score": control_score,
                    "status": self._interpret_control_score(control_score),
                    "last_assessment": latest_data.measurement_date,
                    "key_metrics": self._get_key_control_metrics(disease, latest_data)
                }
            else:
                control_status[disease.disease_type.value] = {
                    "control_score": 0.0,
                    "status": "insufficient_data",
                    "last_assessment": None,
                    "key_metrics": {}
                }
        
        return control_status
    
    async def _calculate_control_score(
        self,
        disease: ChronicDisease,
        monitoring_data: MonitoringData
    ) -> float:
        """计算疾病控制评分"""
        score = 0.0
        total_weight = 0.0
        
        # 根据疾病类型定义关键指标和权重
        if disease.disease_type == ChronicDiseaseType.DIABETES:
            metrics = {
                "fasting_glucose": {"target": 7.0, "weight": 0.3},
                "hba1c": {"target": 7.0, "weight": 0.4},
                "systolic_bp": {"target": 130, "weight": 0.2},
                "diastolic_bp": {"target": 80, "weight": 0.1}
            }
        elif disease.disease_type == ChronicDiseaseType.HYPERTENSION:
            metrics = {
                "systolic_bp": {"target": 130, "weight": 0.5},
                "diastolic_bp": {"target": 80, "weight": 0.5}
            }
        else:
            return 0.5  # 默认中等控制
        
        # 计算各指标的控制评分
        for metric, config in metrics.items():
            value = None
            if metric in monitoring_data.vital_signs:
                value = monitoring_data.vital_signs[metric]
            elif metric in monitoring_data.lab_results:
                value = monitoring_data.lab_results[metric]
            
            if value is not None:
                target = config["target"]
                weight = config["weight"]
                
                # 计算偏离程度
                deviation = abs(value - target) / target
                metric_score = max(0.0, 1.0 - deviation)
                
                score += metric_score * weight
                total_weight += weight
        
        return score / total_weight if total_weight > 0 else 0.0
    
    def _interpret_control_score(self, score: float) -> str:
        """解释控制评分"""
        if score >= 0.8:
            return "excellent"
        elif score >= 0.6:
            return "good"
        elif score >= 0.4:
            return "fair"
        elif score >= 0.2:
            return "poor"
        else:
            return "very_poor"
    
    def _get_key_control_metrics(
        self,
        disease: ChronicDisease,
        monitoring_data: MonitoringData
    ) -> Dict[str, Any]:
        """获取关键控制指标"""
        metrics = {}
        
        if disease.disease_type == ChronicDiseaseType.DIABETES:
            if "fasting_glucose" in monitoring_data.lab_results:
                metrics["fasting_glucose"] = {
                    "value": monitoring_data.lab_results["fasting_glucose"],
                    "target": 7.0,
                    "unit": "mmol/L"
                }
            if "hba1c" in monitoring_data.lab_results:
                metrics["hba1c"] = {
                    "value": monitoring_data.lab_results["hba1c"],
                    "target": 7.0,
                    "unit": "%"
                }
        
        elif disease.disease_type == ChronicDiseaseType.HYPERTENSION:
            if "systolic_bp" in monitoring_data.vital_signs:
                metrics["systolic_bp"] = {
                    "value": monitoring_data.vital_signs["systolic_bp"],
                    "target": 130,
                    "unit": "mmHg"
                }
            if "diastolic_bp" in monitoring_data.vital_signs:
                metrics["diastolic_bp"] = {
                    "value": monitoring_data.vital_signs["diastolic_bp"],
                    "target": 80,
                    "unit": "mmHg"
                }
        
        return metrics
    
    async def _analyze_recent_trends(self, user_id: str) -> Dict[str, Any]:
        """分析最近趋势"""
        user_monitoring = self.monitoring_data.get(user_id, [])
        
        # 获取最近30天的数据
        recent_data = [m for m in user_monitoring 
                      if (datetime.now() - m.measurement_date).days <= 30]
        
        if len(recent_data) < 3:
            return {"status": "insufficient_data"}
        
        # 按疾病分组分析趋势
        trends_by_disease = {}
        
        for disease_id in set(m.disease_id for m in recent_data):
            disease_data = [m for m in recent_data if m.disease_id == disease_id]
            disease_data.sort(key=lambda x: x.measurement_date)
            
            # 分析关键指标趋势
            trends = await self._analyze_metric_trends(disease_data)
            trends_by_disease[disease_id] = trends
        
        return {
            "status": "analyzed",
            "analysis_period": "30_days",
            "data_points": len(recent_data),
            "trends_by_disease": trends_by_disease
        }
    
    async def _analyze_metric_trends(self, monitoring_data: List[MonitoringData]) -> Dict[str, Any]:
        """分析指标趋势"""
        trends = {}
        
        # 提取所有指标
        all_metrics = set()
        for data in monitoring_data:
            all_metrics.update(data.vital_signs.keys())
            all_metrics.update(data.lab_results.keys())
        
        # 分析每个指标的趋势
        for metric in all_metrics:
            values = []
            dates = []
            
            for data in monitoring_data:
                value = None
                if metric in data.vital_signs:
                    value = data.vital_signs[metric]
                elif metric in data.lab_results:
                    value = data.lab_results[metric]
                
                if value is not None:
                    values.append(value)
                    dates.append(data.measurement_date)
            
            if len(values) >= 3:
                trend_analysis = self._calculate_trend_direction(values, dates)
                trends[metric] = trend_analysis
        
        return trends
    
    def _calculate_trend_direction(self, values: List[float], dates: List[datetime]) -> Dict[str, Any]:
        """计算趋势方向"""
        # 简单的线性回归分析
        x = np.array([(d - dates[0]).days for d in dates])
        y = np.array(values)
        
        # 计算斜率
        slope = np.polyfit(x, y, 1)[0]
        
        # 计算变化率
        change_rate = (values[-1] - values[0]) / values[0] * 100 if values[0] != 0 else 0
        
        # 判断趋势方向
        if abs(slope) < 0.01:
            direction = "stable"
        elif slope > 0:
            direction = "increasing"
        else:
            direction = "decreasing"
        
        return {
            "direction": direction,
            "slope": slope,
            "change_rate": change_rate,
            "current_value": values[-1],
            "baseline_value": values[0],
            "volatility": np.std(values),
            "data_points": len(values)
        }
    
    async def _assess_overall_risk(self, user_id: str) -> Dict[str, Any]:
        """评估整体风险"""
        user_diseases = self.diseases.get(user_id, [])
        user_alerts = self.risk_alerts.get(user_id, [])
        
        # 计算风险评分
        risk_score = 0.0
        risk_factors = []
        
        # 基于疾病数量和严重程度
        for disease in user_diseases:
            disease_risk = disease.severity_score / 10.0
            risk_score += disease_risk
            
            if disease.severity_score >= 7.0:
                risk_factors.append(f"{disease.disease_type.value}严重")
        
        # 基于活跃预警
        active_alerts = [a for a in user_alerts if a.status == "active"]
        critical_alerts = [a for a in active_alerts if a.alert_level == AlertLevel.CRITICAL]
        high_alerts = [a for a in active_alerts if a.alert_level == AlertLevel.HIGH]
        
        risk_score += len(critical_alerts) * 0.3
        risk_score += len(high_alerts) * 0.2
        
        if critical_alerts:
            risk_factors.append("存在危急预警")
        if len(high_alerts) >= 2:
            risk_factors.append("多个高风险预警")
        
        # 标准化风险评分
        risk_score = min(1.0, risk_score)
        
        # 确定风险等级
        if risk_score >= 0.8:
            risk_level = "very_high"
        elif risk_score >= 0.6:
            risk_level = "high"
        elif risk_score >= 0.4:
            risk_level = "moderate"
        elif risk_score >= 0.2:
            risk_level = "low"
        else:
            risk_level = "very_low"
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "active_alerts": len(active_alerts),
            "critical_alerts": len(critical_alerts),
            "assessment_date": datetime.now()
        }
    
    async def _evaluate_treatment_effectiveness(self, user_id: str) -> Dict[str, Any]:
        """评估治疗效果"""
        user_outcomes = self.treatment_outcomes.get(user_id, [])
        
        if not user_outcomes:
            return {"status": "no_data"}
        
        # 计算平均改善率
        total_improvement = 0.0
        improvement_count = 0
        
        for outcome in user_outcomes:
            for metric, improvement in outcome.metric_improvements.items():
                total_improvement += improvement
                improvement_count += 1
        
        average_improvement = total_improvement / improvement_count if improvement_count > 0 else 0.0
        
        # 计算目标达成率
        total_goals = 0
        achieved_goals = 0
        
        for outcome in user_outcomes:
            for goal, achieved in outcome.goal_achievement.items():
                total_goals += 1
                if achieved:
                    achieved_goals += 1
        
        achievement_rate = achieved_goals / total_goals if total_goals > 0 else 0.0
        
        # 评估整体效果
        if achievement_rate >= 0.8 and average_improvement >= 0.2:
            effectiveness = "excellent"
        elif achievement_rate >= 0.6 and average_improvement >= 0.1:
            effectiveness = "good"
        elif achievement_rate >= 0.4 or average_improvement >= 0.05:
            effectiveness = "fair"
        else:
            effectiveness = "poor"
        
        return {
            "effectiveness": effectiveness,
            "achievement_rate": achievement_rate,
            "average_improvement": average_improvement,
            "total_evaluations": len(user_outcomes),
            "last_evaluation": max(user_outcomes, key=lambda x: x.evaluation_date).evaluation_date
        }
    
    async def _generate_summary_recommendations(
        self,
        diseases: List[ChronicDisease],
        plans: List[ManagementPlan],
        monitoring_data: List[MonitoringData],
        alerts: List[RiskAlert]
    ) -> List[str]:
        """生成摘要建议"""
        recommendations = []
        
        # 基于活跃预警的建议
        active_alerts = [a for a in alerts if a.status == "active"]
        critical_alerts = [a for a in active_alerts if a.alert_level == AlertLevel.CRITICAL]
        
        if critical_alerts:
            recommendations.append("存在危急预警，建议立即就医处理")
        
        # 基于监测频率的建议
        recent_monitoring = [m for m in monitoring_data 
                           if (datetime.now() - m.measurement_date).days <= 7]
        
        if len(recent_monitoring) == 0:
            recommendations.append("近期缺乏监测数据，建议加强自我监测")
        
        # 基于疾病控制的建议
        for disease in diseases:
            if disease.severity_score >= 7.0:
                recommendations.append(f"{disease.disease_type.value}病情较重，建议密切监测和积极治疗")
        
        # 基于治疗依从性的建议
        if monitoring_data:
            latest_data = max(monitoring_data, key=lambda x: x.measurement_date)
            if latest_data.adherence_score and latest_data.adherence_score < 0.8:
                recommendations.append("治疗依从性有待提高，建议加强健康教育和支持")
        
        return recommendations
    
    def _get_next_actions(
        self,
        diseases: List[ChronicDisease],
        plans: List[ManagementPlan],
        alerts: List[RiskAlert]
    ) -> List[str]:
        """获取下一步行动"""
        actions = []
        
        # 基于预警的行动
        active_alerts = [a for a in alerts if a.status == "active"]
        for alert in active_alerts:
            if alert.alert_level == AlertLevel.CRITICAL:
                actions.extend(alert.recommended_actions)
        
        # 基于管理计划的行动
        for plan in plans:
            if plan.status == "active":
                # 检查是否需要复查
                days_since_start = (datetime.now() - plan.start_date).days
                if days_since_start >= plan.review_frequency:
                    actions.append(f"复查{plan.plan_name}")
        
        # 基于疾病状态的行动
        for disease in diseases:
            if disease.current_stage == DiseaseStage.SEVERE:
                actions.append(f"加强{disease.disease_type.value}监测和治疗")
        
        return list(set(actions))  # 去重
    
    async def _get_upcoming_appointments(self, user_id: str) -> List[Dict[str, Any]]:
        """获取即将到来的预约"""
        appointments = []
        
        user_plans = self.management_plans.get(user_id, [])
        
        for plan in user_plans:
            if plan.status == "active":
                # 计算下次复查时间
                next_review = plan.start_date + timedelta(days=plan.review_frequency)
                
                if next_review > datetime.now():
                    appointments.append({
                        "type": "复查",
                        "plan_name": plan.plan_name,
                        "scheduled_date": next_review,
                        "description": f"{plan.plan_name}定期复查"
                    })
                
                # 检查监测计划中的预约
                for schedule_item in plan.monitoring_schedule:
                    if schedule_item.get("frequency") == "monthly":
                        # 计算下次监测时间
                        next_monitoring = datetime.now() + timedelta(days=30)
                        appointments.append({
                            "type": "监测",
                            "test_name": schedule_item.get("test_name"),
                            "scheduled_date": next_monitoring,
                            "description": f"{schedule_item.get('test_name')}定期监测"
                        })
        
        # 按时间排序
        appointments.sort(key=lambda x: x["scheduled_date"])
        
        return appointments[:5]  # 返回最近的5个预约
    
    async def get_management_statistics(self) -> Dict[str, Any]:
        """获取管理统计信息"""
        try:
            total_users = len(self.diseases)
            total_diseases = sum(len(diseases) for diseases in self.diseases.values())
            total_plans = sum(len(plans) for plans in self.management_plans.values())
            total_monitoring = sum(len(data) for data in self.monitoring_data.values())
            total_alerts = sum(len(alerts) for alerts in self.risk_alerts.values())
            
            # 疾病类型分布
            disease_distribution = {}
            for diseases in self.diseases.values():
                for disease in diseases:
                    disease_type = disease.disease_type.value
                    disease_distribution[disease_type] = disease_distribution.get(disease_type, 0) + 1
            
            # 预警级别分布
            alert_distribution = {}
            for alerts in self.risk_alerts.values():
                for alert in alerts:
                    if alert.status == "active":
                        level = alert.alert_level.value
                        alert_distribution[level] = alert_distribution.get(level, 0) + 1
            
            # 计算平均控制评分
            control_scores = []
            for user_id in self.diseases.keys():
                disease_control = await self._analyze_disease_control(user_id)
                for control_info in disease_control.values():
                    if control_info["control_score"] > 0:
                        control_scores.append(control_info["control_score"])
            
            average_control_score = np.mean(control_scores) if control_scores else 0.0
            
            statistics = {
                "overview": {
                    "total_users": total_users,
                    "total_diseases": total_diseases,
                    "total_management_plans": total_plans,
                    "total_monitoring_records": total_monitoring,
                    "total_alerts": total_alerts
                },
                "disease_distribution": disease_distribution,
                "alert_distribution": alert_distribution,
                "performance_metrics": {
                    "average_control_score": average_control_score,
                    "users_with_excellent_control": len([s for s in control_scores if s >= 0.8]),
                    "users_with_poor_control": len([s for s in control_scores if s < 0.4])
                },
                "system_health": {
                    "data_quality_score": await self._calculate_data_quality_score(),
                    "alert_response_rate": await self._calculate_alert_response_rate(),
                    "plan_adherence_rate": await self._calculate_plan_adherence_rate()
                },
                "generated_at": datetime.now()
            }
            
            return statistics
            
        except Exception as e:
            logger.error(f"获取管理统计信息失败: {e}")
            raise
    
    async def _calculate_data_quality_score(self) -> float:
        """计算数据质量评分"""
        all_monitoring_data = []
        for data_list in self.monitoring_data.values():
            all_monitoring_data.extend(data_list)
        
        if not all_monitoring_data:
            return 0.0
        
        quality_scores = [data.data_quality_score for data in all_monitoring_data]
        return np.mean(quality_scores)
    
    async def _calculate_alert_response_rate(self) -> float:
        """计算预警响应率"""
        all_alerts = []
        for alerts in self.risk_alerts.values():
            all_alerts.extend(alerts)
        
        if not all_alerts:
            return 0.0
        
        resolved_alerts = len([a for a in all_alerts if a.status == "resolved"])
        return resolved_alerts / len(all_alerts)
    
    async def _calculate_plan_adherence_rate(self) -> float:
        """计算计划依从率"""
        all_monitoring_data = []
        for data_list in self.monitoring_data.values():
            all_monitoring_data.extend(data_list)
        
        if not all_monitoring_data:
            return 0.0
        
        adherence_scores = [data.adherence_score for data in all_monitoring_data 
                          if data.adherence_score is not None]
        
        if not adherence_scores:
            return 0.0
        
        return np.mean(adherence_scores)

def initialize_chronic_disease_manager(
    config: Dict[str, Any],
    metrics_collector: Optional[MetricsCollector] = None
) -> IntelligentChronicDiseaseManager:
    """初始化智能慢病管理引擎"""
    try:
        manager = IntelligentChronicDiseaseManager(config, metrics_collector)
        logger.info("智能慢病管理引擎创建成功")
        return manager
    except Exception as e:
        logger.error(f"创建智能慢病管理引擎失败: {e}")
        raise

# 全局实例
_chronic_disease_manager = None

def get_chronic_disease_manager() -> Optional[IntelligentChronicDiseaseManager]:
    """获取智能慢病管理引擎实例"""
    return _chronic_disease_manager 