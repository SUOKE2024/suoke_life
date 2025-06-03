#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能用药管理引擎 - 实现药物治疗的智能化管理
结合现代药物治疗学和中医用药理论，为用户提供安全、有效的个性化用药管理方案
"""

from typing import Dict, List, Any, Optional, Tuple, Union, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta, time
from loguru import logger
import warnings
warnings.filterwarnings('ignore')

from ..observability.metrics import MetricsCollector
from ..observability.tracing import trace_operation, SpanKind

class MedicationType(str, Enum):
    """药物类型"""
    WESTERN_MEDICINE = "western_medicine"       # 西药
    CHINESE_MEDICINE = "chinese_medicine"       # 中药
    HERBAL_FORMULA = "herbal_formula"          # 中药方剂
    SUPPLEMENT = "supplement"                   # 营养补充剂
    VACCINE = "vaccine"                        # 疫苗
    BIOLOGICAL = "biological"                  # 生物制剂

class MedicationForm(str, Enum):
    """药物剂型"""
    TABLET = "tablet"                          # 片剂
    CAPSULE = "capsule"                        # 胶囊
    LIQUID = "liquid"                          # 液体
    INJECTION = "injection"                    # 注射剂
    TOPICAL = "topical"                        # 外用药
    INHALER = "inhaler"                        # 吸入剂
    PATCH = "patch"                           # 贴剂
    POWDER = "powder"                         # 散剂
    DECOCTION = "decoction"                   # 汤剂

class AdministrationRoute(str, Enum):
    """给药途径"""
    ORAL = "oral"                             # 口服
    INTRAVENOUS = "intravenous"               # 静脉注射
    INTRAMUSCULAR = "intramuscular"           # 肌肉注射
    SUBCUTANEOUS = "subcutaneous"             # 皮下注射
    TOPICAL = "topical"                       # 外用
    INHALATION = "inhalation"                 # 吸入
    RECTAL = "rectal"                         # 直肠给药
    SUBLINGUAL = "sublingual"                 # 舌下含服

class MedicationStatus(str, Enum):
    """用药状态"""
    ACTIVE = "active"                         # 正在使用
    PAUSED = "paused"                         # 暂停使用
    DISCONTINUED = "discontinued"             # 已停用
    COMPLETED = "completed"                   # 已完成疗程

class InteractionSeverity(str, Enum):
    """相互作用严重程度"""
    MINOR = "minor"                           # 轻微
    MODERATE = "moderate"                     # 中等
    MAJOR = "major"                          # 严重
    CONTRAINDICATED = "contraindicated"      # 禁忌

class AdherenceLevel(str, Enum):
    """依从性水平"""
    EXCELLENT = "excellent"                   # 优秀 (>95%)
    GOOD = "good"                            # 良好 (85-95%)
    FAIR = "fair"                            # 一般 (70-85%)
    POOR = "poor"                            # 差 (<70%)

@dataclass
class Medication:
    """药物信息"""
    medication_id: str
    name: str                                 # 药物名称
    generic_name: str                         # 通用名
    brand_names: List[str] = field(default_factory=list)  # 商品名
    medication_type: MedicationType
    medication_form: MedicationForm
    
    # 药物成分
    active_ingredients: List[str] = field(default_factory=list)
    strength: str = ""                        # 规格强度
    
    # 适应症和禁忌症
    indications: List[str] = field(default_factory=list)
    contraindications: List[str] = field(default_factory=list)
    
    # 药物分类
    therapeutic_class: str = ""               # 治疗分类
    pharmacological_class: str = ""           # 药理分类
    
    # 药代动力学
    half_life: Optional[float] = None         # 半衰期（小时）
    onset_time: Optional[float] = None        # 起效时间（小时）
    duration: Optional[float] = None          # 作用持续时间（小时）
    
    # 副作用
    common_side_effects: List[str] = field(default_factory=list)
    serious_side_effects: List[str] = field(default_factory=list)
    
    # 特殊人群用药
    pregnancy_category: Optional[str] = None   # 妊娠分级
    lactation_safety: Optional[str] = None     # 哺乳期安全性
    pediatric_use: bool = False               # 儿童用药
    geriatric_considerations: List[str] = field(default_factory=list)
    
    # 监测要求
    monitoring_parameters: List[str] = field(default_factory=list)
    
    # 中医属性（针对中药）
    tcm_properties: Dict[str, Any] = field(default_factory=dict)
    
    # 更新时间
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class Prescription:
    """处方信息"""
    prescription_id: str
    user_id: str
    medication_id: str
    prescriber_id: str                        # 开方医生ID
    prescription_date: datetime
    
    # 用药指示
    dosage: str                               # 剂量
    frequency: str                            # 频次
    administration_route: AdministrationRoute
    administration_time: List[time] = field(default_factory=list)  # 服药时间
    
    # 疗程信息
    duration_days: Optional[int] = None       # 疗程天数
    total_quantity: Optional[float] = None    # 总量
    refills_allowed: int = 0                  # 允许重复配药次数
    
    # 特殊说明
    special_instructions: List[str] = field(default_factory=list)
    food_instructions: str = ""               # 与食物关系
    
    # 适应症
    indication: str = ""                      # 用药适应症
    diagnosis_code: Optional[str] = None      # 诊断代码
    
    # 状态
    status: MedicationStatus = MedicationStatus.ACTIVE
    
    # 开始和结束时间
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    
    # 中医处方特殊信息
    tcm_syndrome: Optional[str] = None        # 中医证型
    preparation_method: Optional[str] = None  # 制备方法
    
    # 更新时间
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class MedicationAdherence:
    """用药依从性记录"""
    user_id: str
    prescription_id: str
    date: date
    
    # 计划用药
    scheduled_doses: int                      # 计划服药次数
    
    # 实际用药
    taken_doses: int                          # 实际服药次数
    missed_doses: int                         # 漏服次数
    extra_doses: int = 0                      # 多服次数
    
    # 服药时间
    actual_times: List[datetime] = field(default_factory=list)
    
    # 依从性评分
    adherence_score: float = 0.0              # 依从性评分 (0.0-1.0)
    
    # 漏服原因
    missed_reasons: List[str] = field(default_factory=list)
    
    # 副作用记录
    side_effects: List[str] = field(default_factory=list)
    side_effect_severity: Dict[str, int] = field(default_factory=dict)  # 1-10分
    
    # 备注
    notes: Optional[str] = None

@dataclass
class DrugInteraction:
    """药物相互作用"""
    interaction_id: str
    medication1_id: str
    medication2_id: str
    
    # 相互作用信息
    interaction_type: str                     # 相互作用类型
    severity: InteractionSeverity
    mechanism: str                            # 作用机制
    
    # 临床意义
    clinical_significance: str
    management_strategy: str                  # 管理策略
    
    # 监测建议
    monitoring_recommendations: List[str] = field(default_factory=list)
    
    # 证据等级
    evidence_level: str = ""                  # 证据等级
    
    # 参考文献
    references: List[str] = field(default_factory=list)

@dataclass
class MedicationAlert:
    """用药预警"""
    alert_id: str
    user_id: str
    alert_type: str                           # 预警类型
    severity: str                             # 严重程度
    
    # 预警内容
    title: str
    description: str
    
    # 相关药物
    related_medications: List[str] = field(default_factory=list)
    
    # 建议措施
    recommendations: List[str] = field(default_factory=list)
    
    # 时间信息
    created_date: datetime = field(default_factory=datetime.now)
    acknowledged_date: Optional[datetime] = None
    resolved_date: Optional[datetime] = None
    
    # 状态
    status: str = "active"                    # active, acknowledged, resolved

@dataclass
class MedicationReview:
    """用药审查"""
    review_id: str
    user_id: str
    reviewer_id: str                          # 审查者ID
    review_date: datetime
    
    # 审查内容
    medications_reviewed: List[str] = field(default_factory=list)
    
    # 发现的问题
    identified_issues: List[Dict[str, Any]] = field(default_factory=list)
    
    # 建议调整
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    
    # 审查结果
    overall_assessment: str = ""
    risk_level: str = "low"                   # low, medium, high
    
    # 下次审查时间
    next_review_date: Optional[datetime] = None

class MedicationDatabase:
    """药物数据库"""
    
    def __init__(self):
        self.medications = self._load_medication_database()
        self.interactions = self._load_interaction_database()
        self.contraindications = self._load_contraindication_database()
        self.dosing_guidelines = self._load_dosing_guidelines()
    
    def _load_medication_database(self) -> Dict[str, Medication]:
        """加载药物数据库"""
        medications = {}
        
        # 常用西药
        medications["metformin"] = Medication(
            medication_id="metformin",
            name="二甲双胍",
            generic_name="Metformin",
            brand_names=["格华止", "美迪康"],
            medication_type=MedicationType.WESTERN_MEDICINE,
            medication_form=MedicationForm.TABLET,
            active_ingredients=["二甲双胍盐酸盐"],
            strength="500mg",
            indications=["2型糖尿病", "多囊卵巢综合征"],
            contraindications=["严重肾功能不全", "严重肝功能不全", "心力衰竭"],
            therapeutic_class="降糖药",
            pharmacological_class="双胍类",
            half_life=6.2,
            onset_time=1.0,
            duration=12.0,
            common_side_effects=["胃肠道反应", "恶心", "腹泻"],
            serious_side_effects=["乳酸性酸中毒"],
            pregnancy_category="B",
            monitoring_parameters=["肾功能", "维生素B12", "血糖"]
        )
        
        medications["lisinopril"] = Medication(
            medication_id="lisinopril",
            name="赖诺普利",
            generic_name="Lisinopril",
            brand_names=["捷赐瑞", "力平之"],
            medication_type=MedicationType.WESTERN_MEDICINE,
            medication_form=MedicationForm.TABLET,
            active_ingredients=["赖诺普利"],
            strength="10mg",
            indications=["高血压", "心力衰竭", "心肌梗死后"],
            contraindications=["妊娠", "血管性水肿史", "双侧肾动脉狭窄"],
            therapeutic_class="降压药",
            pharmacological_class="ACE抑制剂",
            half_life=12.0,
            onset_time=1.0,
            duration=24.0,
            common_side_effects=["干咳", "头晕", "高钾血症"],
            serious_side_effects=["血管性水肿", "严重低血压"],
            pregnancy_category="D",
            monitoring_parameters=["血压", "肾功能", "血钾"]
        )
        
        # 常用中药
        medications["ginseng"] = Medication(
            medication_id="ginseng",
            name="人参",
            generic_name="Ginseng",
            medication_type=MedicationType.CHINESE_MEDICINE,
            medication_form=MedicationForm.POWDER,
            active_ingredients=["人参皂苷"],
            indications=["气虚", "脾肺气虚", "心神不安"],
            contraindications=["实热证", "高血压急性期"],
            therapeutic_class="补气药",
            common_side_effects=["失眠", "血压升高"],
            tcm_properties={
                "nature": "温",
                "flavor": "甘、微苦",
                "meridian": "脾、肺、心",
                "functions": ["大补元气", "复脉固脱", "补脾益肺", "生津安神"]
            }
        )
        
        medications["huangqi"] = Medication(
            medication_id="huangqi",
            name="黄芪",
            generic_name="Astragalus",
            medication_type=MedicationType.CHINESE_MEDICINE,
            medication_form=MedicationForm.POWDER,
            active_ingredients=["黄芪多糖", "黄芪皂苷"],
            indications=["气虚乏力", "脾虚泄泻", "中气下陷"],
            contraindications=["表实邪盛", "气滞湿阻"],
            therapeutic_class="补气药",
            tcm_properties={
                "nature": "微温",
                "flavor": "甘",
                "meridian": "脾、肺",
                "functions": ["补气升阳", "固表止汗", "利水消肿", "托疮生肌"]
            }
        )
        
        return medications
    
    def _load_interaction_database(self) -> List[DrugInteraction]:
        """加载药物相互作用数据库"""
        interactions = []
        
        # 西药相互作用
        interactions.append(DrugInteraction(
            interaction_id="metformin_lisinopril",
            medication1_id="metformin",
            medication2_id="lisinopril",
            interaction_type="药效学相互作用",
            severity=InteractionSeverity.MINOR,
            mechanism="ACE抑制剂可能增强二甲双胍的降糖效果",
            clinical_significance="通常无临床意义，但需监测血糖",
            management_strategy="监测血糖，必要时调整剂量",
            monitoring_recommendations=["血糖监测", "肾功能监测"],
            evidence_level="C"
        ))
        
        # 中西药相互作用
        interactions.append(DrugInteraction(
            interaction_id="ginseng_warfarin",
            medication1_id="ginseng",
            medication2_id="warfarin",
            interaction_type="药代动力学相互作用",
            severity=InteractionSeverity.MODERATE,
            mechanism="人参可能影响华法林的代谢",
            clinical_significance="可能影响抗凝效果",
            management_strategy="避免同时使用或密切监测凝血功能",
            monitoring_recommendations=["INR监测", "凝血功能检查"],
            evidence_level="B"
        ))
        
        return interactions
    
    def _load_contraindication_database(self) -> Dict[str, List[str]]:
        """加载禁忌症数据库"""
        return {
            "pregnancy": ["ACE抑制剂", "ARB", "他汀类", "华法林"],
            "lactation": ["阿司匹林", "氯霉素", "四环素"],
            "kidney_disease": ["二甲双胍", "NSAIDs", "造影剂"],
            "liver_disease": ["对乙酰氨基酚", "他汀类", "抗真菌药"],
            "heart_failure": ["NSAIDs", "钙通道阻滞剂", "抗心律失常药"]
        }
    
    def _load_dosing_guidelines(self) -> Dict[str, Dict[str, Any]]:
        """加载用药指南"""
        return {
            "diabetes": {
                "first_line": ["二甲双胍"],
                "second_line": ["SGLT-2抑制剂", "GLP-1受体激动剂"],
                "combination_therapy": ["二甲双胍 + SGLT-2抑制剂"],
                "target_hba1c": 7.0
            },
            "hypertension": {
                "first_line": ["ACE抑制剂", "ARB", "钙通道阻滞剂", "利尿剂"],
                "combination_therapy": ["ACE抑制剂 + 利尿剂"],
                "target_bp": "130/80"
            }
        }

class MedicationAnalyzer:
    """用药分析器"""
    
    def __init__(self):
        self.medication_db = MedicationDatabase()
        self.interaction_checker = InteractionChecker()
        self.adherence_analyzer = AdherenceAnalyzer()
    
    @trace_operation("medication_analyzer.analyze_prescription", SpanKind.INTERNAL)
    async def analyze_prescription(
        self,
        prescription: Prescription,
        user_profile: Dict[str, Any],
        current_medications: List[Prescription] = None
    ) -> Dict[str, Any]:
        """分析处方"""
        try:
            analysis_result = {
                "prescription_id": prescription.prescription_id,
                "analysis_date": datetime.now(),
                "safety_assessment": {},
                "efficacy_assessment": {},
                "interaction_check": {},
                "contraindication_check": {},
                "dosing_assessment": {},
                "monitoring_recommendations": [],
                "alerts": [],
                "overall_risk": "low"
            }
            
            # 安全性评估
            analysis_result["safety_assessment"] = await self._assess_safety(
                prescription, user_profile
            )
            
            # 有效性评估
            analysis_result["efficacy_assessment"] = await self._assess_efficacy(
                prescription, user_profile
            )
            
            # 相互作用检查
            if current_medications:
                analysis_result["interaction_check"] = await self._check_interactions(
                    prescription, current_medications
                )
            
            # 禁忌症检查
            analysis_result["contraindication_check"] = await self._check_contraindications(
                prescription, user_profile
            )
            
            # 剂量评估
            analysis_result["dosing_assessment"] = await self._assess_dosing(
                prescription, user_profile
            )
            
            # 监测建议
            analysis_result["monitoring_recommendations"] = await self._generate_monitoring_recommendations(
                prescription, user_profile
            )
            
            # 生成预警
            analysis_result["alerts"] = await self._generate_alerts(
                prescription, analysis_result
            )
            
            # 计算整体风险
            analysis_result["overall_risk"] = await self._calculate_overall_risk(
                analysis_result
            )
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"分析处方失败: {e}")
            raise
    
    async def _assess_safety(
        self,
        prescription: Prescription,
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """评估用药安全性"""
        medication = self.medication_db.medications.get(prescription.medication_id)
        if not medication:
            return {"status": "medication_not_found"}
        
        safety_issues = []
        risk_factors = []
        
        # 检查年龄相关风险
        age = user_profile.get("age", 0)
        if age >= 65:
            if medication.geriatric_considerations:
                safety_issues.extend(medication.geriatric_considerations)
                risk_factors.append("老年患者用药")
        
        if age < 18 and not medication.pediatric_use:
            safety_issues.append("儿童用药安全性未确立")
            risk_factors.append("儿童用药")
        
        # 检查妊娠和哺乳期
        if user_profile.get("pregnancy", False):
            if medication.pregnancy_category in ["D", "X"]:
                safety_issues.append(f"妊娠期用药风险等级: {medication.pregnancy_category}")
                risk_factors.append("妊娠期用药")
        
        if user_profile.get("lactation", False):
            if medication.lactation_safety == "contraindicated":
                safety_issues.append("哺乳期禁用")
                risk_factors.append("哺乳期用药")
        
        # 检查过敏史
        allergies = user_profile.get("allergies", [])
        for allergy in allergies:
            if allergy in medication.active_ingredients:
                safety_issues.append(f"对{allergy}过敏")
                risk_factors.append("药物过敏")
        
        # 计算安全性评分
        safety_score = 1.0 - (len(safety_issues) * 0.2)
        safety_score = max(0.0, safety_score)
        
        return {
            "safety_score": safety_score,
            "safety_issues": safety_issues,
            "risk_factors": risk_factors,
            "recommendations": await self._generate_safety_recommendations(safety_issues)
        }
    
    async def _assess_efficacy(
        self,
        prescription: Prescription,
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """评估用药有效性"""
        medication = self.medication_db.medications.get(prescription.medication_id)
        if not medication:
            return {"status": "medication_not_found"}
        
        # 检查适应症匹配
        indication_match = prescription.indication in medication.indications
        
        # 检查剂量合理性
        dosing_appropriate = await self._check_dosing_appropriateness(
            prescription, user_profile
        )
        
        # 检查给药途径
        route_appropriate = True  # 简化处理
        
        # 计算有效性评分
        efficacy_score = 0.0
        if indication_match:
            efficacy_score += 0.4
        if dosing_appropriate:
            efficacy_score += 0.4
        if route_appropriate:
            efficacy_score += 0.2
        
        return {
            "efficacy_score": efficacy_score,
            "indication_match": indication_match,
            "dosing_appropriate": dosing_appropriate,
            "route_appropriate": route_appropriate,
            "expected_onset": medication.onset_time,
            "expected_duration": medication.duration
        }
    
    async def _check_interactions(
        self,
        new_prescription: Prescription,
        current_medications: List[Prescription]
    ) -> Dict[str, Any]:
        """检查药物相互作用"""
        interactions = []
        
        for current_med in current_medications:
            if current_med.status != MedicationStatus.ACTIVE:
                continue
            
            # 查找相互作用
            interaction = self._find_interaction(
                new_prescription.medication_id,
                current_med.medication_id
            )
            
            if interaction:
                interactions.append({
                    "medication1": new_prescription.medication_id,
                    "medication2": current_med.medication_id,
                    "severity": interaction.severity.value,
                    "mechanism": interaction.mechanism,
                    "clinical_significance": interaction.clinical_significance,
                    "management": interaction.management_strategy
                })
        
        # 计算相互作用风险
        risk_level = "low"
        if any(i["severity"] == "contraindicated" for i in interactions):
            risk_level = "critical"
        elif any(i["severity"] == "major" for i in interactions):
            risk_level = "high"
        elif any(i["severity"] == "moderate" for i in interactions):
            risk_level = "medium"
        
        return {
            "interactions_found": len(interactions),
            "interactions": interactions,
            "risk_level": risk_level
        }
    
    def _find_interaction(self, med1_id: str, med2_id: str) -> Optional[DrugInteraction]:
        """查找药物相互作用"""
        for interaction in self.medication_db.interactions:
            if ((interaction.medication1_id == med1_id and interaction.medication2_id == med2_id) or
                (interaction.medication1_id == med2_id and interaction.medication2_id == med1_id)):
                return interaction
        return None
    
    async def _check_contraindications(
        self,
        prescription: Prescription,
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """检查禁忌症"""
        medication = self.medication_db.medications.get(prescription.medication_id)
        if not medication:
            return {"status": "medication_not_found"}
        
        contraindications_found = []
        
        # 检查疾病禁忌症
        medical_conditions = user_profile.get("medical_conditions", [])
        for condition in medical_conditions:
            if condition in medication.contraindications:
                contraindications_found.append({
                    "type": "disease",
                    "condition": condition,
                    "severity": "absolute"
                })
        
        # 检查特殊人群禁忌症
        contraindications = self.medication_db.contraindications
        
        if user_profile.get("pregnancy", False):
            if medication.name in contraindications.get("pregnancy", []):
                contraindications_found.append({
                    "type": "pregnancy",
                    "condition": "妊娠期",
                    "severity": "absolute"
                })
        
        if user_profile.get("kidney_disease", False):
            if medication.name in contraindications.get("kidney_disease", []):
                contraindications_found.append({
                    "type": "organ_dysfunction",
                    "condition": "肾功能不全",
                    "severity": "absolute"
                })
        
        return {
            "contraindications_found": len(contraindications_found),
            "contraindications": contraindications_found,
            "risk_level": "high" if contraindications_found else "low"
        }
    
    async def _assess_dosing(
        self,
        prescription: Prescription,
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """评估剂量"""
        # 简化的剂量评估
        age = user_profile.get("age", 30)
        weight = user_profile.get("weight", 70)
        kidney_function = user_profile.get("kidney_function", "normal")
        liver_function = user_profile.get("liver_function", "normal")
        
        dosing_issues = []
        
        # 年龄相关剂量调整
        if age >= 65:
            dosing_issues.append("老年患者可能需要减量")
        
        # 肾功能相关剂量调整
        if kidney_function in ["mild_impairment", "moderate_impairment", "severe_impairment"]:
            dosing_issues.append("肾功能不全需要调整剂量")
        
        # 肝功能相关剂量调整
        if liver_function in ["mild_impairment", "moderate_impairment", "severe_impairment"]:
            dosing_issues.append("肝功能不全需要调整剂量")
        
        return {
            "dosing_appropriate": len(dosing_issues) == 0,
            "dosing_issues": dosing_issues,
            "recommended_adjustments": await self._generate_dosing_adjustments(
                prescription, user_profile, dosing_issues
            )
        }
    
    async def _check_dosing_appropriateness(
        self,
        prescription: Prescription,
        user_profile: Dict[str, Any]
    ) -> bool:
        """检查剂量合理性"""
        # 简化处理，实际应该根据具体药物和患者情况判断
        return True
    
    async def _generate_monitoring_recommendations(
        self,
        prescription: Prescription,
        user_profile: Dict[str, Any]
    ) -> List[str]:
        """生成监测建议"""
        medication = self.medication_db.medications.get(prescription.medication_id)
        if not medication:
            return []
        
        recommendations = []
        
        # 基于药物的监测参数
        for parameter in medication.monitoring_parameters:
            recommendations.append(f"定期监测{parameter}")
        
        # 基于副作用的监测
        if "肝毒性" in medication.serious_side_effects:
            recommendations.append("定期检查肝功能")
        
        if "肾毒性" in medication.serious_side_effects:
            recommendations.append("定期检查肾功能")
        
        # 基于患者特征的监测
        age = user_profile.get("age", 30)
        if age >= 65:
            recommendations.append("老年患者需要更频繁的监测")
        
        return recommendations
    
    async def _generate_alerts(
        self,
        prescription: Prescription,
        analysis_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """生成预警"""
        alerts = []
        
        # 安全性预警
        safety_score = analysis_result["safety_assessment"].get("safety_score", 1.0)
        if safety_score < 0.5:
            alerts.append({
                "type": "safety",
                "severity": "high",
                "message": "用药安全性风险较高",
                "recommendations": analysis_result["safety_assessment"].get("recommendations", [])
            })
        
        # 相互作用预警
        interaction_risk = analysis_result["interaction_check"].get("risk_level", "low")
        if interaction_risk in ["high", "critical"]:
            alerts.append({
                "type": "interaction",
                "severity": interaction_risk,
                "message": "存在重要药物相互作用",
                "interactions": analysis_result["interaction_check"].get("interactions", [])
            })
        
        # 禁忌症预警
        contraindications = analysis_result["contraindication_check"].get("contraindications", [])
        if contraindications:
            alerts.append({
                "type": "contraindication",
                "severity": "critical",
                "message": "存在用药禁忌症",
                "contraindications": contraindications
            })
        
        return alerts
    
    async def _calculate_overall_risk(self, analysis_result: Dict[str, Any]) -> str:
        """计算整体风险"""
        risk_factors = []
        
        # 安全性风险
        safety_score = analysis_result["safety_assessment"].get("safety_score", 1.0)
        if safety_score < 0.3:
            risk_factors.append("high_safety_risk")
        elif safety_score < 0.7:
            risk_factors.append("moderate_safety_risk")
        
        # 相互作用风险
        interaction_risk = analysis_result["interaction_check"].get("risk_level", "low")
        if interaction_risk in ["high", "critical"]:
            risk_factors.append("interaction_risk")
        
        # 禁忌症风险
        contraindications = analysis_result["contraindication_check"].get("contraindications", [])
        if contraindications:
            risk_factors.append("contraindication_risk")
        
        # 确定整体风险等级
        if "contraindication_risk" in risk_factors or "high_safety_risk" in risk_factors:
            return "critical"
        elif "interaction_risk" in risk_factors or "moderate_safety_risk" in risk_factors:
            return "high"
        elif risk_factors:
            return "medium"
        else:
            return "low"
    
    async def _generate_safety_recommendations(self, safety_issues: List[str]) -> List[str]:
        """生成安全性建议"""
        recommendations = []
        
        for issue in safety_issues:
            if "过敏" in issue:
                recommendations.append("避免使用该药物，寻找替代方案")
            elif "妊娠期" in issue:
                recommendations.append("评估获益风险比，考虑替代治疗")
            elif "老年" in issue:
                recommendations.append("从低剂量开始，密切监测")
        
        return recommendations
    
    async def _generate_dosing_adjustments(
        self,
        prescription: Prescription,
        user_profile: Dict[str, Any],
        dosing_issues: List[str]
    ) -> List[str]:
        """生成剂量调整建议"""
        adjustments = []
        
        for issue in dosing_issues:
            if "老年" in issue:
                adjustments.append("建议减量25-50%")
            elif "肾功能" in issue:
                adjustments.append("根据肌酐清除率调整剂量")
            elif "肝功能" in issue:
                adjustments.append("肝功能不全时减量或延长给药间隔")
        
        return adjustments

class InteractionChecker:
    """相互作用检查器"""
    
    def __init__(self):
        self.interaction_rules = self._load_interaction_rules()
    
    def _load_interaction_rules(self) -> Dict[str, Any]:
        """加载相互作用规则"""
        return {
            "cyp450_inhibitors": {
                "strong": ["酮康唑", "伊曲康唑", "克拉霉素"],
                "moderate": ["氟康唑", "红霉素", "西咪替丁"],
                "weak": ["奥美拉唑", "雷尼替丁"]
            },
            "cyp450_inducers": {
                "strong": ["利福平", "卡马西平", "苯妥英"],
                "moderate": ["苯巴比妥", "奥卡西平"],
                "weak": ["莫达非尼"]
            },
            "protein_binding": {
                "high": ["华法林", "苯妥英", "地高辛"],
                "moderate": ["阿司匹林", "布洛芬"]
            }
        }
    
    async def check_cyp450_interactions(
        self,
        medications: List[str]
    ) -> List[Dict[str, Any]]:
        """检查CYP450相互作用"""
        interactions = []
        
        inhibitors = []
        inducers = []
        substrates = []
        
        # 分类药物
        for med in medications:
            if med in self.interaction_rules["cyp450_inhibitors"]["strong"]:
                inhibitors.append({"name": med, "strength": "strong"})
            elif med in self.interaction_rules["cyp450_inducers"]["strong"]:
                inducers.append({"name": med, "strength": "strong"})
            # 可以继续添加其他分类
        
        # 检查相互作用
        for inhibitor in inhibitors:
            for substrate in substrates:
                interactions.append({
                    "type": "cyp450_inhibition",
                    "inhibitor": inhibitor["name"],
                    "substrate": substrate["name"],
                    "severity": "major" if inhibitor["strength"] == "strong" else "moderate",
                    "mechanism": f"{inhibitor['name']}抑制{substrate['name']}的代谢"
                })
        
        return interactions

class AdherenceAnalyzer:
    """依从性分析器"""
    
    def __init__(self):
        self.adherence_thresholds = {
            "excellent": 0.95,
            "good": 0.85,
            "fair": 0.70,
            "poor": 0.0
        }
    
    async def calculate_adherence_score(
        self,
        adherence_records: List[MedicationAdherence]
    ) -> Dict[str, Any]:
        """计算依从性评分"""
        if not adherence_records:
            return {"status": "no_data"}
        
        total_scheduled = sum(record.scheduled_doses for record in adherence_records)
        total_taken = sum(record.taken_doses for record in adherence_records)
        
        if total_scheduled == 0:
            return {"status": "invalid_data"}
        
        adherence_rate = total_taken / total_scheduled
        
        # 确定依从性等级
        adherence_level = AdherenceLevel.POOR
        for level, threshold in sorted(self.adherence_thresholds.items(), 
                                     key=lambda x: x[1], reverse=True):
            if adherence_rate >= threshold:
                adherence_level = AdherenceLevel(level)
                break
        
        # 分析漏服模式
        missed_patterns = await self._analyze_missed_patterns(adherence_records)
        
        # 分析漏服原因
        missed_reasons = await self._analyze_missed_reasons(adherence_records)
        
        return {
            "adherence_rate": adherence_rate,
            "adherence_level": adherence_level.value,
            "total_scheduled": total_scheduled,
            "total_taken": total_taken,
            "total_missed": total_scheduled - total_taken,
            "missed_patterns": missed_patterns,
            "missed_reasons": missed_reasons,
            "recommendations": await self._generate_adherence_recommendations(
                adherence_level, missed_patterns, missed_reasons
            )
        }
    
    async def _analyze_missed_patterns(
        self,
        adherence_records: List[MedicationAdherence]
    ) -> Dict[str, Any]:
        """分析漏服模式"""
        patterns = {
            "weekend_effect": False,
            "morning_doses_missed": 0,
            "evening_doses_missed": 0,
            "consecutive_missed_days": 0,
            "irregular_pattern": False
        }
        
        # 简化的模式分析
        weekend_missed = 0
        weekday_missed = 0
        
        for record in adherence_records:
            if record.date.weekday() >= 5:  # 周末
                weekend_missed += record.missed_doses
            else:  # 工作日
                weekday_missed += record.missed_doses
        
        if weekend_missed > weekday_missed * 1.5:
            patterns["weekend_effect"] = True
        
        return patterns
    
    async def _analyze_missed_reasons(
        self,
        adherence_records: List[MedicationAdherence]
    ) -> Dict[str, int]:
        """分析漏服原因"""
        reason_counts = {}
        
        for record in adherence_records:
            for reason in record.missed_reasons:
                reason_counts[reason] = reason_counts.get(reason, 0) + 1
        
        return reason_counts
    
    async def _generate_adherence_recommendations(
        self,
        adherence_level: AdherenceLevel,
        missed_patterns: Dict[str, Any],
        missed_reasons: Dict[str, int]
    ) -> List[str]:
        """生成依从性改善建议"""
        recommendations = []
        
        if adherence_level == AdherenceLevel.POOR:
            recommendations.append("建议与医生讨论治疗方案的调整")
            recommendations.append("考虑使用用药提醒工具")
        
        if missed_patterns.get("weekend_effect"):
            recommendations.append("周末设置特别的用药提醒")
        
        # 基于漏服原因的建议
        top_reason = max(missed_reasons.items(), key=lambda x: x[1])[0] if missed_reasons else None
        
        if top_reason == "忘记":
            recommendations.append("使用手机APP或闹钟设置用药提醒")
        elif top_reason == "副作用":
            recommendations.append("与医生讨论副作用管理策略")
        elif top_reason == "费用":
            recommendations.append("咨询医生是否有更经济的替代方案")
        
        return recommendations

class MedicationScheduler:
    """用药调度器"""
    
    def __init__(self):
        self.scheduling_rules = self._load_scheduling_rules()
    
    def _load_scheduling_rules(self) -> Dict[str, Any]:
        """加载调度规则"""
        return {
            "meal_timing": {
                "before_meals": -30,  # 餐前30分钟
                "with_meals": 0,      # 餐时
                "after_meals": 30     # 餐后30分钟
            },
            "sleep_timing": {
                "bedtime": "22:00",
                "wake_time": "07:00"
            },
            "interaction_spacing": {
                "minimum_interval": 2,  # 小时
                "maximum_daily_doses": 4
            }
        }
    
    async def generate_medication_schedule(
        self,
        prescriptions: List[Prescription],
        user_preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """生成用药时间表"""
        try:
            schedule = {
                "daily_schedule": {},
                "weekly_schedule": {},
                "special_instructions": [],
                "conflicts": [],
                "optimization_suggestions": []
            }
            
            # 获取用户偏好
            meal_times = user_preferences.get("meal_times", {
                "breakfast": "08:00",
                "lunch": "12:00",
                "dinner": "18:00"
            })
            
            wake_time = user_preferences.get("wake_time", "07:00")
            sleep_time = user_preferences.get("sleep_time", "22:00")
            
            # 为每个处方安排时间
            for prescription in prescriptions:
                if prescription.status != MedicationStatus.ACTIVE:
                    continue
                
                medication_schedule = await self._schedule_single_medication(
                    prescription, meal_times, wake_time, sleep_time
                )
                
                # 合并到总时间表
                await self._merge_schedule(schedule, medication_schedule, prescription)
            
            # 检查冲突
            schedule["conflicts"] = await self._check_scheduling_conflicts(schedule)
            
            # 生成优化建议
            schedule["optimization_suggestions"] = await self._generate_optimization_suggestions(
                schedule, prescriptions
            )
            
            return schedule
            
        except Exception as e:
            logger.error(f"生成用药时间表失败: {e}")
            raise
    
    async def _schedule_single_medication(
        self,
        prescription: Prescription,
        meal_times: Dict[str, str],
        wake_time: str,
        sleep_time: str
    ) -> Dict[str, Any]:
        """为单个药物安排时间"""
        medication_schedule = {
            "medication_id": prescription.medication_id,
            "times": [],
            "food_instructions": prescription.food_instructions,
            "special_notes": prescription.special_instructions
        }
        
        # 解析频次
        frequency = prescription.frequency
        times_per_day = self._parse_frequency(frequency)
        
        # 根据与食物的关系安排时间
        if "餐前" in prescription.food_instructions:
            base_times = [
                self._adjust_time(meal_times["breakfast"], -30),
                self._adjust_time(meal_times["lunch"], -30),
                self._adjust_time(meal_times["dinner"], -30)
            ]
        elif "餐后" in prescription.food_instructions:
            base_times = [
                self._adjust_time(meal_times["breakfast"], 30),
                self._adjust_time(meal_times["lunch"], 30),
                self._adjust_time(meal_times["dinner"], 30)
            ]
        elif "餐时" in prescription.food_instructions:
            base_times = [
                meal_times["breakfast"],
                meal_times["lunch"],
                meal_times["dinner"]
            ]
        else:
            # 均匀分布
            base_times = self._distribute_evenly(times_per_day, wake_time, sleep_time)
        
        # 选择合适的时间点
        medication_schedule["times"] = base_times[:times_per_day]
        
        return medication_schedule
    
    def _parse_frequency(self, frequency: str) -> int:
        """解析用药频次"""
        frequency_mapping = {
            "每日一次": 1,
            "每日两次": 2,
            "每日三次": 3,
            "每日四次": 4,
            "每8小时一次": 3,
            "每12小时一次": 2,
            "每6小时一次": 4,
            "bid": 2,
            "tid": 3,
            "qid": 4,
            "qd": 1
        }
        
        return frequency_mapping.get(frequency, 1)
    
    def _adjust_time(self, base_time: str, minutes: int) -> str:
        """调整时间"""
        from datetime import datetime, timedelta
        
        time_obj = datetime.strptime(base_time, "%H:%M")
        adjusted_time = time_obj + timedelta(minutes=minutes)
        return adjusted_time.strftime("%H:%M")
    
    def _distribute_evenly(self, count: int, wake_time: str, sleep_time: str) -> List[str]:
        """均匀分布时间"""
        from datetime import datetime, timedelta
        
        wake = datetime.strptime(wake_time, "%H:%M")
        sleep = datetime.strptime(sleep_time, "%H:%M")
        
        if sleep < wake:  # 跨天
            sleep += timedelta(days=1)
        
        total_minutes = (sleep - wake).total_seconds() / 60
        interval_minutes = total_minutes / count
        
        times = []
        for i in range(count):
            time_point = wake + timedelta(minutes=i * interval_minutes)
            times.append(time_point.strftime("%H:%M"))
        
        return times
    
    async def _merge_schedule(
        self,
        main_schedule: Dict[str, Any],
        medication_schedule: Dict[str, Any],
        prescription: Prescription
    ):
        """合并时间表"""
        for time_str in medication_schedule["times"]:
            if time_str not in main_schedule["daily_schedule"]:
                main_schedule["daily_schedule"][time_str] = []
            
            main_schedule["daily_schedule"][time_str].append({
                "prescription_id": prescription.prescription_id,
                "medication_id": prescription.medication_id,
                "dosage": prescription.dosage,
                "food_instructions": prescription.food_instructions,
                "special_instructions": prescription.special_instructions
            })
    
    async def _check_scheduling_conflicts(self, schedule: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检查调度冲突"""
        conflicts = []
        
        for time_str, medications in schedule["daily_schedule"].items():
            if len(medications) > 3:  # 同一时间超过3种药物
                conflicts.append({
                    "type": "too_many_medications",
                    "time": time_str,
                    "count": len(medications),
                    "message": f"{time_str}需要服用{len(medications)}种药物，可能影响依从性"
                })
            
            # 检查食物要求冲突
            food_requirements = set()
            for med in medications:
                if med["food_instructions"]:
                    food_requirements.add(med["food_instructions"])
            
            if len(food_requirements) > 1:
                conflicts.append({
                    "type": "food_instruction_conflict",
                    "time": time_str,
                    "requirements": list(food_requirements),
                    "message": f"{time_str}的药物有不同的食物要求"
                })
        
        return conflicts
    
    async def _generate_optimization_suggestions(
        self,
        schedule: Dict[str, Any],
        prescriptions: List[Prescription]
    ) -> List[str]:
        """生成优化建议"""
        suggestions = []
        
        # 检查是否可以合并用药时间
        time_points = list(schedule["daily_schedule"].keys())
        if len(time_points) > 4:
            suggestions.append("考虑使用长效制剂减少用药频次")
        
        # 检查是否有复杂的用药方案
        complex_prescriptions = [p for p in prescriptions 
                               if len(p.special_instructions) > 2]
        if complex_prescriptions:
            suggestions.append("建议简化复杂的用药方案")
        
        # 检查冲突
        if schedule["conflicts"]:
            suggestions.append("建议调整用药时间以避免冲突")
        
        return suggestions

class IntelligentMedicationManager:
    """智能用药管理引擎"""
    
    def __init__(self, config: Dict[str, Any], metrics_collector: Optional[MetricsCollector] = None):
        self.config = config
        self.metrics_collector = metrics_collector or MetricsCollector()
        
        # 核心组件
        self.medication_analyzer = None
        self.medication_scheduler = None
        
        # 数据存储
        self.prescriptions = {}  # user_id -> List[Prescription]
        self.adherence_records = {}  # user_id -> List[MedicationAdherence]
        self.medication_alerts = {}  # user_id -> List[MedicationAlert]
        self.medication_reviews = {}  # user_id -> List[MedicationReview]
        
        logger.info("智能用药管理引擎初始化完成")
    
    async def initialize(self):
        """初始化引擎"""
        try:
            await self._load_configuration()
            await self._initialize_components()
            logger.info("智能用药管理引擎初始化成功")
        except Exception as e:
            logger.error(f"智能用药管理引擎初始化失败: {e}")
            raise
    
    async def _load_configuration(self):
        """加载配置"""
        pass
    
    async def _initialize_components(self):
        """初始化组件"""
        self.medication_analyzer = MedicationAnalyzer()
        self.medication_scheduler = MedicationScheduler()
    
    @trace_operation("medication_manager.add_prescription", SpanKind.INTERNAL)
    async def add_prescription(
        self,
        user_id: str,
        prescription_data: Dict[str, Any]
    ) -> Prescription:
        """添加处方"""
        try:
            # 创建处方对象
            prescription = Prescription(
                prescription_id=f"rx_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                user_id=user_id,
                medication_id=prescription_data["medication_id"],
                prescriber_id=prescription_data.get("prescriber_id", "system"),
                prescription_date=datetime.fromisoformat(
                    prescription_data.get("prescription_date", datetime.now().isoformat())
                ),
                dosage=prescription_data["dosage"],
                frequency=prescription_data["frequency"],
                administration_route=AdministrationRoute(
                    prescription_data.get("administration_route", "oral")
                ),
                administration_time=[
                    datetime.strptime(t, "%H:%M").time() 
                    for t in prescription_data.get("administration_time", [])
                ],
                duration_days=prescription_data.get("duration_days"),
                total_quantity=prescription_data.get("total_quantity"),
                refills_allowed=prescription_data.get("refills_allowed", 0),
                special_instructions=prescription_data.get("special_instructions", []),
                food_instructions=prescription_data.get("food_instructions", ""),
                indication=prescription_data.get("indication", ""),
                diagnosis_code=prescription_data.get("diagnosis_code"),
                tcm_syndrome=prescription_data.get("tcm_syndrome"),
                preparation_method=prescription_data.get("preparation_method")
            )
            
            # 存储处方
            if user_id not in self.prescriptions:
                self.prescriptions[user_id] = []
            self.prescriptions[user_id].append(prescription)
            
            # 分析处方
            user_profile = await self._get_user_profile(user_id)
            current_medications = [p for p in self.prescriptions[user_id] 
                                 if p.status == MedicationStatus.ACTIVE and p.prescription_id != prescription.prescription_id]
            
            analysis_result = await self.medication_analyzer.analyze_prescription(
                prescription, user_profile, current_medications
            )
            
            # 生成预警
            await self._process_prescription_alerts(user_id, prescription, analysis_result)
            
            # 记录指标
            self.metrics_collector.increment_counter(
                "prescription_added",
                {"medication_type": prescription_data.get("medication_type", "unknown")}
            )
            
            logger.info(f"为用户 {user_id} 添加处方: {prescription.prescription_id}")
            return prescription
            
        except Exception as e:
            logger.error(f"添加处方失败: {e}")
            raise
    
    async def _get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """获取用户档案"""
        # 这里应该从用户服务获取用户信息
        # 暂时返回模拟数据
        return {
            "age": 45,
            "weight": 70,
            "height": 170,
            "gender": "male",
            "pregnancy": False,
            "lactation": False,
            "allergies": [],
            "medical_conditions": [],
            "kidney_function": "normal",
            "liver_function": "normal"
        }
    
    async def _process_prescription_alerts(
        self,
        user_id: str,
        prescription: Prescription,
        analysis_result: Dict[str, Any]
    ):
        """处理处方预警"""
        alerts = analysis_result.get("alerts", [])
        
        for alert_data in alerts:
            alert = MedicationAlert(
                alert_id=f"alert_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                user_id=user_id,
                alert_type=alert_data["type"],
                severity=alert_data["severity"],
                title=alert_data["message"],
                description=alert_data.get("description", ""),
                related_medications=[prescription.medication_id],
                recommendations=alert_data.get("recommendations", [])
            )
            
            if user_id not in self.medication_alerts:
                self.medication_alerts[user_id] = []
            self.medication_alerts[user_id].append(alert)
            
            logger.warning(f"生成用药预警: {alert.title}")
    
    @trace_operation("medication_manager.record_adherence", SpanKind.INTERNAL)
    async def record_medication_adherence(
        self,
        user_id: str,
        adherence_data: Dict[str, Any]
    ) -> MedicationAdherence:
        """记录用药依从性"""
        try:
            # 创建依从性记录
            adherence = MedicationAdherence(
                user_id=user_id,
                prescription_id=adherence_data["prescription_id"],
                date=datetime.fromisoformat(adherence_data["date"]).date(),
                scheduled_doses=adherence_data["scheduled_doses"],
                taken_doses=adherence_data["taken_doses"],
                missed_doses=adherence_data.get("missed_doses", 0),
                extra_doses=adherence_data.get("extra_doses", 0),
                actual_times=[
                    datetime.fromisoformat(t) for t in adherence_data.get("actual_times", [])
                ],
                missed_reasons=adherence_data.get("missed_reasons", []),
                side_effects=adherence_data.get("side_effects", []),
                side_effect_severity=adherence_data.get("side_effect_severity", {}),
                notes=adherence_data.get("notes")
            )
            
            # 计算依从性评分
            if adherence.scheduled_doses > 0:
                adherence.adherence_score = adherence.taken_doses / adherence.scheduled_doses
            
            # 存储记录
            if user_id not in self.adherence_records:
                self.adherence_records[user_id] = []
            self.adherence_records[user_id].append(adherence)
            
            # 检查依从性问题
            await self._check_adherence_issues(user_id, adherence)
            
            # 记录指标
            self.metrics_collector.record_gauge(
                "medication_adherence_score",
                adherence.adherence_score,
                {"user_id": user_id}
            )
            
            logger.info(f"记录用户 {user_id} 用药依从性")
            return adherence
            
        except Exception as e:
            logger.error(f"记录用药依从性失败: {e}")
            raise
    
    async def _check_adherence_issues(self, user_id: str, adherence: MedicationAdherence):
        """检查依从性问题"""
        if adherence.adherence_score < 0.8:  # 依从性低于80%
            alert = MedicationAlert(
                alert_id=f"adherence_alert_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                user_id=user_id,
                alert_type="poor_adherence",
                severity="medium",
                title="用药依从性较差",
                description=f"依从性评分: {adherence.adherence_score:.2%}",
                related_medications=[adherence.prescription_id],
                recommendations=[
                    "设置用药提醒",
                    "与医生讨论治疗方案",
                    "了解漏服原因并制定改善计划"
                ]
            )
            
            if user_id not in self.medication_alerts:
                self.medication_alerts[user_id] = []
            self.medication_alerts[user_id].append(alert)
    
    @trace_operation("medication_manager.generate_schedule", SpanKind.INTERNAL)
    async def generate_medication_schedule(
        self,
        user_id: str,
        user_preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """生成用药时间表"""
        try:
            # 获取活跃处方
            user_prescriptions = self.prescriptions.get(user_id, [])
            active_prescriptions = [p for p in user_prescriptions 
                                  if p.status == MedicationStatus.ACTIVE]
            
            if not active_prescriptions:
                return {"status": "no_active_prescriptions"}
            
            # 生成时间表
            schedule = await self.medication_scheduler.generate_medication_schedule(
                active_prescriptions, user_preferences
            )
            
            # 记录指标
            self.metrics_collector.increment_counter(
                "medication_schedule_generated",
                {"user_id": user_id, "prescription_count": len(active_prescriptions)}
            )
            
            logger.info(f"为用户 {user_id} 生成用药时间表")
            return schedule
            
        except Exception as e:
            logger.error(f"生成用药时间表失败: {e}")
            raise
    
    async def get_medication_summary(self, user_id: str) -> Dict[str, Any]:
        """获取用药摘要"""
        try:
            user_prescriptions = self.prescriptions.get(user_id, [])
            user_adherence = self.adherence_records.get(user_id, [])
            user_alerts = self.medication_alerts.get(user_id, [])
            
            # 统计信息
            active_prescriptions = [p for p in user_prescriptions 
                                  if p.status == MedicationStatus.ACTIVE]
            
            # 计算平均依从性
            recent_adherence = [a for a in user_adherence 
                              if (datetime.now().date() - a.date).days <= 30]
            
            avg_adherence = 0.0
            if recent_adherence:
                avg_adherence = sum(a.adherence_score for a in recent_adherence) / len(recent_adherence)
            
            # 活跃预警
            active_alerts = [a for a in user_alerts if a.status == "active"]
            
            # 药物类型分布
            medication_types = {}
            for prescription in active_prescriptions:
                # 这里需要从药物数据库获取类型信息
                med_type = "unknown"  # 简化处理
                medication_types[med_type] = medication_types.get(med_type, 0) + 1
            
            # 生成建议
            recommendations = await self._generate_medication_recommendations(
                user_id, active_prescriptions, recent_adherence, active_alerts
            )
            
            summary = {
                "user_id": user_id,
                "summary_date": datetime.now(),
                "statistics": {
                    "total_prescriptions": len(user_prescriptions),
                    "active_prescriptions": len(active_prescriptions),
                    "average_adherence": avg_adherence,
                    "active_alerts": len(active_alerts)
                },
                "medication_types": medication_types,
                "adherence_trend": await self._analyze_adherence_trend(user_adherence),
                "recent_side_effects": await self._analyze_recent_side_effects(user_adherence),
                "drug_interactions": await self._check_current_interactions(user_id),
                "recommendations": recommendations,
                "next_actions": await self._get_medication_next_actions(user_id)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"获取用药摘要失败: {e}")
            raise
    
    async def _generate_medication_recommendations(
        self,
        user_id: str,
        active_prescriptions: List[Prescription],
        recent_adherence: List[MedicationAdherence],
        active_alerts: List[MedicationAlert]
    ) -> List[str]:
        """生成用药建议"""
        recommendations = []
        
        # 基于依从性的建议
        if recent_adherence:
            avg_adherence = sum(a.adherence_score for a in recent_adherence) / len(recent_adherence)
            if avg_adherence < 0.8:
                recommendations.append("建议改善用药依从性，考虑使用用药提醒工具")
        
        # 基于预警的建议
        critical_alerts = [a for a in active_alerts if a.severity == "critical"]
        if critical_alerts:
            recommendations.append("存在严重用药预警，建议立即咨询医生")
        
        # 基于处方数量的建议
        if len(active_prescriptions) > 5:
            recommendations.append("当前用药种类较多，建议定期进行用药审查")
        
        # 基于副作用的建议
        recent_side_effects = []
        for adherence in recent_adherence:
            recent_side_effects.extend(adherence.side_effects)
        
        if recent_side_effects:
            recommendations.append("近期出现副作用，建议与医生讨论调整方案")
        
        return recommendations
    
    async def _analyze_adherence_trend(self, adherence_records: List[MedicationAdherence]) -> Dict[str, Any]:
        """分析依从性趋势"""
        if len(adherence_records) < 7:
            return {"status": "insufficient_data"}
        
        # 按日期排序
        sorted_records = sorted(adherence_records, key=lambda x: x.date)
        recent_records = sorted_records[-30:]  # 最近30天
        
        # 计算趋势
        scores = [r.adherence_score for r in recent_records]
        
        if len(scores) >= 3:
            # 简单的线性趋势分析
            x = np.arange(len(scores))
            slope = np.polyfit(x, scores, 1)[0]
            
            if slope > 0.01:
                trend = "improving"
            elif slope < -0.01:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "trend": trend,
            "current_average": np.mean(scores[-7:]) if len(scores) >= 7 else np.mean(scores),
            "previous_average": np.mean(scores[-14:-7]) if len(scores) >= 14 else None,
            "data_points": len(scores)
        }
    
    async def _analyze_recent_side_effects(self, adherence_records: List[MedicationAdherence]) -> Dict[str, Any]:
        """分析近期副作用"""
        recent_records = [r for r in adherence_records 
                         if (datetime.now().date() - r.date).days <= 30]
        
        side_effect_counts = {}
        severity_scores = {}
        
        for record in recent_records:
            for side_effect in record.side_effects:
                side_effect_counts[side_effect] = side_effect_counts.get(side_effect, 0) + 1
                
                if side_effect in record.side_effect_severity:
                    if side_effect not in severity_scores:
                        severity_scores[side_effect] = []
                    severity_scores[side_effect].append(record.side_effect_severity[side_effect])
        
        # 计算平均严重程度
        avg_severity = {}
        for effect, scores in severity_scores.items():
            avg_severity[effect] = np.mean(scores)
        
        return {
            "side_effect_counts": side_effect_counts,
            "average_severity": avg_severity,
            "total_reports": len([r for r in recent_records if r.side_effects])
        }
    
    async def _check_current_interactions(self, user_id: str) -> Dict[str, Any]:
        """检查当前药物相互作用"""
        user_prescriptions = self.prescriptions.get(user_id, [])
        active_prescriptions = [p for p in user_prescriptions 
                              if p.status == MedicationStatus.ACTIVE]
        
        if len(active_prescriptions) < 2:
            return {"interactions": [], "risk_level": "none"}
        
        interactions = []
        medication_ids = [p.medication_id for p in active_prescriptions]
        
        # 检查每对药物的相互作用
        for i in range(len(medication_ids)):
            for j in range(i + 1, len(medication_ids)):
                interaction = self.medication_analyzer.interaction_checker._find_interaction(
                    medication_ids[i], medication_ids[j]
                )
                if interaction:
                    interactions.append({
                        "medication1": medication_ids[i],
                        "medication2": medication_ids[j],
                        "severity": interaction.severity.value,
                        "description": interaction.clinical_significance
                    })
        
        # 确定风险等级
        if any(i["severity"] == "contraindicated" for i in interactions):
            risk_level = "critical"
        elif any(i["severity"] == "major" for i in interactions):
            risk_level = "high"
        elif any(i["severity"] == "moderate" for i in interactions):
            risk_level = "medium"
        elif interactions:
            risk_level = "low"
        else:
            risk_level = "none"
        
        return {
            "interactions": interactions,
            "risk_level": risk_level,
            "interaction_count": len(interactions)
        }
    
    async def _get_medication_next_actions(self, user_id: str) -> List[str]:
        """获取下一步用药行动"""
        actions = []
        
        # 检查活跃预警
        user_alerts = self.medication_alerts.get(user_id, [])
        active_alerts = [a for a in user_alerts if a.status == "active"]
        
        for alert in active_alerts:
            if alert.severity in ["critical", "high"]:
                actions.extend(alert.recommendations[:2])  # 取前两个建议
        
        # 检查处方到期
        user_prescriptions = self.prescriptions.get(user_id, [])
        for prescription in user_prescriptions:
            if prescription.status == MedicationStatus.ACTIVE and prescription.end_date:
                days_remaining = (prescription.end_date - datetime.now()).days
                if days_remaining <= 7:
                    actions.append(f"处方 {prescription.prescription_id} 即将到期，需要续方")
        
        # 检查依从性
        user_adherence = self.adherence_records.get(user_id, [])
        recent_adherence = [a for a in user_adherence 
                          if (datetime.now().date() - a.date).days <= 7]
        
        if recent_adherence:
            avg_adherence = sum(a.adherence_score for a in recent_adherence) / len(recent_adherence)
            if avg_adherence < 0.7:
                actions.append("改善用药依从性")
        
        return list(set(actions))  # 去重
    
    async def get_medication_statistics(self) -> Dict[str, Any]:
        """获取用药统计信息"""
        try:
            total_users = len(self.prescriptions)
            total_prescriptions = sum(len(prescriptions) for prescriptions in self.prescriptions.values())
            total_adherence_records = sum(len(records) for records in self.adherence_records.values())
            total_alerts = sum(len(alerts) for alerts in self.medication_alerts.values())
            
            # 计算平均依从性
            all_adherence_scores = []
            for records in self.adherence_records.values():
                for record in records:
                    all_adherence_scores.append(record.adherence_score)
            
            avg_adherence = np.mean(all_adherence_scores) if all_adherence_scores else 0.0
            
            # 预警分布
            alert_distribution = {}
            for alerts in self.medication_alerts.values():
                for alert in alerts:
                    if alert.status == "active":
                        severity = alert.severity
                        alert_distribution[severity] = alert_distribution.get(severity, 0) + 1
            
            # 依从性分布
            adherence_distribution = {
                "excellent": 0,
                "good": 0,
                "fair": 0,
                "poor": 0
            }
            
            for score in all_adherence_scores:
                if score >= 0.95:
                    adherence_distribution["excellent"] += 1
                elif score >= 0.85:
                    adherence_distribution["good"] += 1
                elif score >= 0.70:
                    adherence_distribution["fair"] += 1
                else:
                    adherence_distribution["poor"] += 1
            
            statistics = {
                "overview": {
                    "total_users": total_users,
                    "total_prescriptions": total_prescriptions,
                    "total_adherence_records": total_adherence_records,
                    "total_alerts": total_alerts
                },
                "adherence_metrics": {
                    "average_adherence": avg_adherence,
                    "adherence_distribution": adherence_distribution
                },
                "alert_distribution": alert_distribution,
                "system_performance": {
                    "prescription_analysis_rate": 1.0,  # 简化处理
                    "alert_generation_rate": len(alert_distribution) / max(total_prescriptions, 1),
                    "schedule_optimization_rate": 0.8  # 简化处理
                },
                "generated_at": datetime.now()
            }
            
            return statistics
            
        except Exception as e:
            logger.error(f"获取用药统计信息失败: {e}")
            raise

def initialize_medication_manager(
    config: Dict[str, Any],
    metrics_collector: Optional[MetricsCollector] = None
) -> IntelligentMedicationManager:
    """初始化智能用药管理引擎"""
    try:
        manager = IntelligentMedicationManager(config, metrics_collector)
        logger.info("智能用药管理引擎创建成功")
        return manager
    except Exception as e:
        logger.error(f"创建智能用药管理引擎失败: {e}")
        raise

# 全局实例
_medication_manager = None

def get_medication_manager() -> Optional[IntelligentMedicationManager]:
    """获取智能用药管理引擎实例"""
    return _medication_manager 