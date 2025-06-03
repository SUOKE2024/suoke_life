#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能决策支持系统 - 提供多维度决策分析、风险评估、方案比较、智能建议
"""

import time
from typing import Dict, List, Any, Optional, Tuple, Union, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from loguru import logger
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor

from ..observability.metrics import MetricsCollector
from ..observability.tracing import trace_operation, SpanKind

class DecisionType(str, Enum):
    """决策类型"""
    TREATMENT_SELECTION = "treatment_selection"         # 治疗方案选择
    LIFESTYLE_CHANGE = "lifestyle_change"               # 生活方式改变
    PREVENTION_STRATEGY = "prevention_strategy"         # 预防策略
    EMERGENCY_RESPONSE = "emergency_response"           # 应急响应
    HEALTH_SCREENING = "health_screening"               # 健康筛查
    MEDICATION_CHOICE = "medication_choice"             # 用药选择
    DIET_PLANNING = "diet_planning"                     # 饮食规划
    EXERCISE_PROGRAM = "exercise_program"               # 运动计划
    TCM_THERAPY = "tcm_therapy"                         # 中医疗法
    SURGICAL_DECISION = "surgical_decision"             # 手术决策

class RiskLevel(str, Enum):
    """风险级别"""
    VERY_LOW = "very_low"       # 极低风险
    LOW = "low"                 # 低风险
    MODERATE = "moderate"       # 中等风险
    HIGH = "high"               # 高风险
    VERY_HIGH = "very_high"     # 极高风险
    CRITICAL = "critical"       # 危急风险

class DecisionUrgency(str, Enum):
    """决策紧急程度"""
    ROUTINE = "routine"         # 常规
    URGENT = "urgent"           # 紧急
    EMERGENCY = "emergency"     # 急诊
    CRITICAL = "critical"       # 危急

class EvidenceLevel(str, Enum):
    """证据级别"""
    LEVEL_1A = "1a"             # 系统评价/Meta分析
    LEVEL_1B = "1b"             # 至少一个RCT
    LEVEL_2A = "2a"             # 至少一个对照研究
    LEVEL_2B = "2b"             # 至少一个队列研究
    LEVEL_3A = "3a"             # 病例对照研究
    LEVEL_3B = "3b"             # 病例系列研究
    LEVEL_4 = "4"               # 专家意见
    LEVEL_5 = "5"               # 机制推理

@dataclass
class DecisionCriteria:
    """决策标准"""
    id: str
    name: str
    description: str
    weight: float                                   # 权重 (0-1)
    measurement_type: str                           # 测量类型: numeric, categorical, boolean
    optimal_value: Optional[Union[float, str, bool]] = None
    acceptable_range: Optional[Tuple[float, float]] = None
    higher_is_better: bool = True
    mandatory: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DecisionOption:
    """决策选项"""
    id: str
    name: str
    description: str
    category: str
    criteria_scores: Dict[str, Union[float, str, bool]]  # 各标准的得分
    estimated_cost: Optional[float] = None
    estimated_duration: Optional[int] = None        # 持续时间（天）
    success_rate: Optional[float] = None            # 成功率
    side_effects: List[str] = field(default_factory=list)
    contraindications: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    evidence_level: Optional[EvidenceLevel] = None
    evidence_sources: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RiskFactor:
    """风险因素"""
    id: str
    name: str
    description: str
    category: str
    severity: RiskLevel
    probability: float                              # 发生概率 (0-1)
    impact_score: float                             # 影响分数 (0-10)
    mitigation_strategies: List[str] = field(default_factory=list)
    monitoring_indicators: List[str] = field(default_factory=list)
    time_horizon: Optional[str] = None              # 时间范围
    evidence_level: Optional[EvidenceLevel] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DecisionContext:
    """决策上下文"""
    user_id: str
    session_id: str
    decision_type: DecisionType
    urgency: DecisionUrgency
    current_symptoms: List[str] = field(default_factory=list)
    medical_history: List[str] = field(default_factory=list)
    current_medications: List[str] = field(default_factory=list)
    allergies: List[str] = field(default_factory=list)
    lifestyle_factors: Dict[str, Any] = field(default_factory=dict)
    environmental_factors: Dict[str, Any] = field(default_factory=dict)
    social_factors: Dict[str, Any] = field(default_factory=dict)
    economic_constraints: Dict[str, Any] = field(default_factory=dict)
    time_constraints: Dict[str, Any] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)
    goals: List[str] = field(default_factory=list)
    risk_tolerance: str = "moderate"
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class DecisionAnalysis:
    """决策分析结果"""
    option_id: str
    overall_score: float                            # 综合得分
    weighted_score: float                           # 加权得分
    criteria_analysis: Dict[str, float]             # 各标准分析
    risk_assessment: Dict[str, Any]                 # 风险评估
    pros: List[str] = field(default_factory=list)
    cons: List[str] = field(default_factory=list)
    confidence_level: float = 0.0                   # 置信度
    uncertainty_factors: List[str] = field(default_factory=list)
    sensitivity_analysis: Dict[str, float] = field(default_factory=dict)

@dataclass
class DecisionRecommendation:
    """决策推荐"""
    context: DecisionContext
    recommended_option: DecisionOption
    alternative_options: List[DecisionOption]
    analysis_results: List[DecisionAnalysis]
    risk_factors: List[RiskFactor]
    decision_rationale: str
    implementation_plan: List[str] = field(default_factory=list)
    monitoring_plan: List[str] = field(default_factory=list)
    follow_up_schedule: List[Dict[str, Any]] = field(default_factory=list)
    contingency_plans: List[str] = field(default_factory=list)
    quality_indicators: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

class MultiCriteriaDecisionAnalyzer:
    """多标准决策分析器"""
    
    def __init__(self):
        self.normalization_methods = {
            "min_max": self._min_max_normalize,
            "z_score": self._z_score_normalize,
            "vector": self._vector_normalize
        }
        self.aggregation_methods = {
            "weighted_sum": self._weighted_sum,
            "topsis": self._topsis,
            "ahp": self._ahp,
            "electre": self._electre
        }
    
    async def analyze_options(
        self,
        options: List[DecisionOption],
        criteria: List[DecisionCriteria],
        method: str = "weighted_sum"
    ) -> List[DecisionAnalysis]:
        """分析决策选项"""
        try:
            # 构建决策矩阵
            decision_matrix = self._build_decision_matrix(options, criteria)
            
            # 标准化决策矩阵
            normalized_matrix = self._normalize_matrix(decision_matrix, criteria)
            
            # 计算权重
            weights = [criterion.weight for criterion in criteria]
            
            # 应用聚合方法
            if method in self.aggregation_methods:
                scores = await self.aggregation_methods[method](
                    normalized_matrix, weights, criteria
                )
            else:
                scores = await self._weighted_sum(normalized_matrix, weights, criteria)
            
            # 生成分析结果
            analyses = []
            for i, option in enumerate(options):
                analysis = DecisionAnalysis(
                    option_id=option.id,
                    overall_score=scores[i],
                    weighted_score=scores[i],
                    criteria_analysis=self._analyze_criteria_performance(
                        option, criteria, normalized_matrix[i]
                    ),
                    risk_assessment=await self._assess_option_risks(option),
                    pros=self._identify_pros(option, criteria, normalized_matrix[i]),
                    cons=self._identify_cons(option, criteria, normalized_matrix[i]),
                    confidence_level=self._calculate_confidence(option, criteria),
                    uncertainty_factors=self._identify_uncertainties(option),
                    sensitivity_analysis=await self._perform_sensitivity_analysis(
                        option, criteria, weights
                    )
                )
                analyses.append(analysis)
            
            return sorted(analyses, key=lambda x: x.overall_score, reverse=True)
            
        except Exception as e:
            logger.error(f"决策分析失败: {e}")
            return []
    
    def _build_decision_matrix(
        self, 
        options: List[DecisionOption], 
        criteria: List[DecisionCriteria]
    ) -> np.ndarray:
        """构建决策矩阵"""
        matrix = []
        for option in options:
            row = []
            for criterion in criteria:
                value = option.criteria_scores.get(criterion.id, 0)
                if isinstance(value, (int, float)):
                    row.append(float(value))
                else:
                    # 处理分类或布尔值
                    row.append(self._convert_to_numeric(value, criterion))
            matrix.append(row)
        return np.array(matrix)
    
    def _convert_to_numeric(self, value: Any, criterion: DecisionCriteria) -> float:
        """将非数值转换为数值"""
        if isinstance(value, bool):
            return 1.0 if value else 0.0
        elif isinstance(value, str):
            # 简单的字符串到数值映射
            mapping = {
                "excellent": 1.0, "good": 0.8, "fair": 0.6, 
                "poor": 0.4, "very_poor": 0.2,
                "high": 1.0, "medium": 0.6, "low": 0.2,
                "yes": 1.0, "no": 0.0
            }
            return mapping.get(value.lower(), 0.5)
        return 0.0
    
    def _normalize_matrix(
        self, 
        matrix: np.ndarray, 
        criteria: List[DecisionCriteria],
        method: str = "min_max"
    ) -> np.ndarray:
        """标准化决策矩阵"""
        normalized = matrix.copy().astype(float)
        
        for j, criterion in enumerate(criteria):
            column = matrix[:, j]
            if method == "min_max":
                normalized[:, j] = self._min_max_normalize(column, criterion.higher_is_better)
            elif method == "z_score":
                normalized[:, j] = self._z_score_normalize(column, criterion.higher_is_better)
            elif method == "vector":
                normalized[:, j] = self._vector_normalize(column, criterion.higher_is_better)
        
        return normalized
    
    def _min_max_normalize(self, column: np.ndarray, higher_is_better: bool) -> np.ndarray:
        """最小-最大标准化"""
        min_val, max_val = column.min(), column.max()
        if max_val == min_val:
            return np.ones_like(column)
        
        normalized = (column - min_val) / (max_val - min_val)
        if not higher_is_better:
            normalized = 1 - normalized
        return normalized
    
    def _z_score_normalize(self, column: np.ndarray, higher_is_better: bool) -> np.ndarray:
        """Z分数标准化"""
        mean_val, std_val = column.mean(), column.std()
        if std_val == 0:
            return np.zeros_like(column)
        
        normalized = (column - mean_val) / std_val
        if not higher_is_better:
            normalized = -normalized
        return normalized
    
    def _vector_normalize(self, column: np.ndarray, higher_is_better: bool) -> np.ndarray:
        """向量标准化"""
        norm = np.linalg.norm(column)
        if norm == 0:
            return np.zeros_like(column)
        
        normalized = column / norm
        if not higher_is_better:
            normalized = 1 - normalized
        return normalized
    
    async def _weighted_sum(
        self, 
        matrix: np.ndarray, 
        weights: List[float], 
        criteria: List[DecisionCriteria]
    ) -> List[float]:
        """加权求和法"""
        weights_array = np.array(weights)
        scores = np.dot(matrix, weights_array)
        return scores.tolist()
    
    async def _topsis(
        self, 
        matrix: np.ndarray, 
        weights: List[float], 
        criteria: List[DecisionCriteria]
    ) -> List[float]:
        """TOPSIS方法"""
        # 加权标准化矩阵
        weights_array = np.array(weights)
        weighted_matrix = matrix * weights_array
        
        # 确定理想解和负理想解
        ideal_solution = np.max(weighted_matrix, axis=0)
        negative_ideal = np.min(weighted_matrix, axis=0)
        
        # 计算距离
        scores = []
        for row in weighted_matrix:
            d_positive = np.sqrt(np.sum((row - ideal_solution) ** 2))
            d_negative = np.sqrt(np.sum((row - negative_ideal) ** 2))
            
            if d_positive + d_negative == 0:
                score = 0.5
            else:
                score = d_negative / (d_positive + d_negative)
            scores.append(score)
        
        return scores
    
    async def _ahp(
        self, 
        matrix: np.ndarray, 
        weights: List[float], 
        criteria: List[DecisionCriteria]
    ) -> List[float]:
        """层次分析法（简化版）"""
        # 这里实现简化的AHP，实际应用中需要成对比较矩阵
        return await self._weighted_sum(matrix, weights, criteria)
    
    async def _electre(
        self, 
        matrix: np.ndarray, 
        weights: List[float], 
        criteria: List[DecisionCriteria]
    ) -> List[float]:
        """ELECTRE方法（简化版）"""
        # 这里实现简化的ELECTRE，实际应用中需要阈值设定
        return await self._weighted_sum(matrix, weights, criteria)
    
    def _analyze_criteria_performance(
        self,
        option: DecisionOption,
        criteria: List[DecisionCriteria],
        normalized_scores: np.ndarray
    ) -> Dict[str, float]:
        """分析各标准表现"""
        analysis = {}
        for i, criterion in enumerate(criteria):
            analysis[criterion.id] = {
                "score": normalized_scores[i],
                "weight": criterion.weight,
                "weighted_score": normalized_scores[i] * criterion.weight
            }
        return analysis
    
    async def _assess_option_risks(self, option: DecisionOption) -> Dict[str, Any]:
        """评估选项风险"""
        risk_assessment = {
            "overall_risk": "moderate",
            "risk_factors": [],
            "mitigation_strategies": []
        }
        
        # 基于副作用评估风险
        if len(option.side_effects) > 5:
            risk_assessment["overall_risk"] = "high"
        elif len(option.side_effects) > 2:
            risk_assessment["overall_risk"] = "moderate"
        else:
            risk_assessment["overall_risk"] = "low"
        
        risk_assessment["risk_factors"] = option.side_effects + option.contraindications
        
        return risk_assessment
    
    def _identify_pros(
        self,
        option: DecisionOption,
        criteria: List[DecisionCriteria],
        normalized_scores: np.ndarray
    ) -> List[str]:
        """识别优点"""
        pros = []
        for i, criterion in enumerate(criteria):
            if normalized_scores[i] > 0.7:  # 高分标准
                pros.append(f"在{criterion.name}方面表现优秀")
        
        if option.success_rate and option.success_rate > 0.8:
            pros.append(f"成功率高达{option.success_rate:.1%}")
        
        if option.evidence_level in [EvidenceLevel.LEVEL_1A, EvidenceLevel.LEVEL_1B]:
            pros.append("具有高质量循证医学证据支持")
        
        return pros
    
    def _identify_cons(
        self,
        option: DecisionOption,
        criteria: List[DecisionCriteria],
        normalized_scores: np.ndarray
    ) -> List[str]:
        """识别缺点"""
        cons = []
        for i, criterion in enumerate(criteria):
            if normalized_scores[i] < 0.3:  # 低分标准
                cons.append(f"在{criterion.name}方面表现不佳")
        
        if len(option.side_effects) > 3:
            cons.append(f"可能存在{len(option.side_effects)}种副作用")
        
        if len(option.contraindications) > 0:
            cons.append(f"存在{len(option.contraindications)}项禁忌症")
        
        return cons
    
    def _calculate_confidence(
        self,
        option: DecisionOption,
        criteria: List[DecisionCriteria]
    ) -> float:
        """计算置信度"""
        confidence = 0.5  # 基础置信度
        
        # 基于证据级别调整
        if option.evidence_level:
            evidence_confidence = {
                EvidenceLevel.LEVEL_1A: 0.95,
                EvidenceLevel.LEVEL_1B: 0.90,
                EvidenceLevel.LEVEL_2A: 0.80,
                EvidenceLevel.LEVEL_2B: 0.70,
                EvidenceLevel.LEVEL_3A: 0.60,
                EvidenceLevel.LEVEL_3B: 0.50,
                EvidenceLevel.LEVEL_4: 0.40,
                EvidenceLevel.LEVEL_5: 0.30
            }
            confidence = evidence_confidence.get(option.evidence_level, 0.5)
        
        # 基于证据来源数量调整
        if len(option.evidence_sources) > 5:
            confidence += 0.1
        elif len(option.evidence_sources) > 2:
            confidence += 0.05
        
        return min(confidence, 1.0)
    
    def _identify_uncertainties(self, option: DecisionOption) -> List[str]:
        """识别不确定性因素"""
        uncertainties = []
        
        if not option.success_rate:
            uncertainties.append("缺乏成功率数据")
        
        if not option.evidence_level or option.evidence_level in [
            EvidenceLevel.LEVEL_4, EvidenceLevel.LEVEL_5
        ]:
            uncertainties.append("证据质量有限")
        
        if len(option.evidence_sources) < 2:
            uncertainties.append("证据来源不足")
        
        if not option.estimated_cost:
            uncertainties.append("成本估算不明确")
        
        return uncertainties
    
    async def _perform_sensitivity_analysis(
        self,
        option: DecisionOption,
        criteria: List[DecisionCriteria],
        weights: List[float]
    ) -> Dict[str, float]:
        """执行敏感性分析"""
        sensitivity = {}
        
        # 对每个权重进行±20%的变化，观察得分变化
        base_score = sum(
            option.criteria_scores.get(criterion.id, 0) * weight
            for criterion, weight in zip(criteria, weights)
        )
        
        for i, criterion in enumerate(criteria):
            # 增加权重
            modified_weights = weights.copy()
            modified_weights[i] *= 1.2
            
            new_score = sum(
                option.criteria_scores.get(crit.id, 0) * weight
                for crit, weight in zip(criteria, modified_weights)
            )
            
            sensitivity[criterion.id] = abs(new_score - base_score) / base_score if base_score != 0 else 0
        
        return sensitivity

class RiskAssessmentEngine:
    """风险评估引擎"""
    
    def __init__(self):
        self.risk_models = {}
        self.risk_thresholds = {
            RiskLevel.VERY_LOW: 0.1,
            RiskLevel.LOW: 0.3,
            RiskLevel.MODERATE: 0.5,
            RiskLevel.HIGH: 0.7,
            RiskLevel.VERY_HIGH: 0.9,
            RiskLevel.CRITICAL: 1.0
        }
    
    async def assess_risks(
        self,
        context: DecisionContext,
        options: List[DecisionOption]
    ) -> List[RiskFactor]:
        """评估风险因素"""
        try:
            risk_factors = []
            
            # 医疗风险评估
            medical_risks = await self._assess_medical_risks(context, options)
            risk_factors.extend(medical_risks)
            
            # 药物相互作用风险
            drug_risks = await self._assess_drug_interaction_risks(context, options)
            risk_factors.extend(drug_risks)
            
            # 生活方式风险
            lifestyle_risks = await self._assess_lifestyle_risks(context, options)
            risk_factors.extend(lifestyle_risks)
            
            # 经济风险
            economic_risks = await self._assess_economic_risks(context, options)
            risk_factors.extend(economic_risks)
            
            # 依从性风险
            adherence_risks = await self._assess_adherence_risks(context, options)
            risk_factors.extend(adherence_risks)
            
            return risk_factors
            
        except Exception as e:
            logger.error(f"风险评估失败: {e}")
            return []
    
    async def _assess_medical_risks(
        self,
        context: DecisionContext,
        options: List[DecisionOption]
    ) -> List[RiskFactor]:
        """评估医疗风险"""
        risks = []
        
        # 基于病史评估风险
        for condition in context.medical_history:
            if "心脏病" in condition:
                risk = RiskFactor(
                    id=f"cardiac_risk_{condition}",
                    name="心血管风险",
                    description=f"基于{condition}病史的心血管风险",
                    category="medical",
                    severity=RiskLevel.HIGH,
                    probability=0.3,
                    impact_score=8.0,
                    mitigation_strategies=["定期心电图检查", "血压监测", "避免剧烈运动"],
                    monitoring_indicators=["胸痛", "气短", "心悸"],
                    time_horizon="短期",
                    evidence_level=EvidenceLevel.LEVEL_2A
                )
                risks.append(risk)
        
        # 基于当前症状评估风险
        if "胸痛" in context.current_symptoms:
            risk = RiskFactor(
                id="acute_cardiac_risk",
                name="急性心血管事件风险",
                description="基于胸痛症状的急性心血管事件风险",
                category="medical",
                severity=RiskLevel.CRITICAL,
                probability=0.2,
                impact_score=10.0,
                mitigation_strategies=["立即就医", "心电图检查", "心肌酶检测"],
                monitoring_indicators=["胸痛加重", "呼吸困难", "出汗"],
                time_horizon="即时",
                evidence_level=EvidenceLevel.LEVEL_1B
            )
            risks.append(risk)
        
        return risks
    
    async def _assess_drug_interaction_risks(
        self,
        context: DecisionContext,
        options: List[DecisionOption]
    ) -> List[RiskFactor]:
        """评估药物相互作用风险"""
        risks = []
        
        # 简化的药物相互作用检查
        high_risk_combinations = {
            ("华法林", "阿司匹林"): "出血风险增加",
            ("地高辛", "胺碘酮"): "地高辛中毒风险",
            ("锂盐", "利尿剂"): "锂中毒风险"
        }
        
        current_drugs = set(context.current_medications)
        
        for option in options:
            option_drugs = set(option.metadata.get("medications", []))
            
            for drug_combo, risk_desc in high_risk_combinations.items():
                if (drug_combo[0] in current_drugs and drug_combo[1] in option_drugs) or \
                   (drug_combo[1] in current_drugs and drug_combo[0] in option_drugs):
                    
                    risk = RiskFactor(
                        id=f"drug_interaction_{drug_combo[0]}_{drug_combo[1]}",
                        name="药物相互作用风险",
                        description=risk_desc,
                        category="drug_interaction",
                        severity=RiskLevel.HIGH,
                        probability=0.6,
                        impact_score=7.0,
                        mitigation_strategies=["调整剂量", "监测血药浓度", "选择替代药物"],
                        monitoring_indicators=["异常出血", "心律不齐", "恶心呕吐"],
                        time_horizon="短期",
                        evidence_level=EvidenceLevel.LEVEL_2A
                    )
                    risks.append(risk)
        
        return risks
    
    async def _assess_lifestyle_risks(
        self,
        context: DecisionContext,
        options: List[DecisionOption]
    ) -> List[RiskFactor]:
        """评估生活方式风险"""
        risks = []
        
        lifestyle = context.lifestyle_factors
        
        # 吸烟风险
        if lifestyle.get("smoking", False):
            risk = RiskFactor(
                id="smoking_risk",
                name="吸烟相关风险",
                description="吸烟增加治疗失败和并发症风险",
                category="lifestyle",
                severity=RiskLevel.HIGH,
                probability=0.8,
                impact_score=6.0,
                mitigation_strategies=["戒烟咨询", "尼古丁替代疗法", "行为干预"],
                monitoring_indicators=["咳嗽加重", "呼吸困难", "伤口愈合不良"],
                time_horizon="长期",
                evidence_level=EvidenceLevel.LEVEL_1A
            )
            risks.append(risk)
        
        # 饮酒风险
        if lifestyle.get("alcohol_consumption", 0) > 2:  # 每日超过2个单位
            risk = RiskFactor(
                id="alcohol_risk",
                name="酒精相关风险",
                description="过量饮酒影响药物代谢和治疗效果",
                category="lifestyle",
                severity=RiskLevel.MODERATE,
                probability=0.5,
                impact_score=5.0,
                mitigation_strategies=["限制饮酒", "肝功能监测", "营养支持"],
                monitoring_indicators=["肝功能异常", "药物效果减弱", "戒断症状"],
                time_horizon="中期",
                evidence_level=EvidenceLevel.LEVEL_2A
            )
            risks.append(risk)
        
        return risks
    
    async def _assess_economic_risks(
        self,
        context: DecisionContext,
        options: List[DecisionOption]
    ) -> List[RiskFactor]:
        """评估经济风险"""
        risks = []
        
        economic_constraints = context.economic_constraints
        budget_limit = economic_constraints.get("budget_limit", float('inf'))
        
        for option in options:
            if option.estimated_cost and option.estimated_cost > budget_limit:
                risk = RiskFactor(
                    id=f"cost_risk_{option.id}",
                    name="经济负担风险",
                    description=f"治疗费用超出预算限制",
                    category="economic",
                    severity=RiskLevel.MODERATE,
                    probability=1.0,
                    impact_score=4.0,
                    mitigation_strategies=["寻求保险覆盖", "分期付款", "寻找替代方案"],
                    monitoring_indicators=["财务压力", "治疗中断", "依从性下降"],
                    time_horizon="短期",
                    evidence_level=EvidenceLevel.LEVEL_4
                )
                risks.append(risk)
        
        return risks
    
    async def _assess_adherence_risks(
        self,
        context: DecisionContext,
        options: List[DecisionOption]
    ) -> List[RiskFactor]:
        """评估依从性风险"""
        risks = []
        
        # 基于治疗复杂性评估依从性风险
        for option in options:
            complexity_score = 0
            
            # 用药频次
            if option.metadata.get("dosing_frequency", 1) > 3:
                complexity_score += 2
            
            # 治疗持续时间
            if option.estimated_duration and option.estimated_duration > 90:
                complexity_score += 2
            
            # 副作用数量
            if len(option.side_effects) > 3:
                complexity_score += 1
            
            if complexity_score >= 3:
                risk = RiskFactor(
                    id=f"adherence_risk_{option.id}",
                    name="治疗依从性风险",
                    description="治疗方案复杂性可能影响患者依从性",
                    category="adherence",
                    severity=RiskLevel.MODERATE,
                    probability=0.4,
                    impact_score=6.0,
                    mitigation_strategies=["简化用药方案", "患者教育", "定期随访"],
                    monitoring_indicators=["用药不规律", "症状反复", "治疗效果不佳"],
                    time_horizon="中期",
                    evidence_level=EvidenceLevel.LEVEL_3A
                )
                risks.append(risk)
        
        return risks
    
    def calculate_overall_risk_score(self, risk_factors: List[RiskFactor]) -> float:
        """计算总体风险分数"""
        if not risk_factors:
            return 0.0
        
        total_risk = 0.0
        for risk in risk_factors:
            risk_score = risk.probability * risk.impact_score / 10.0
            total_risk += risk_score
        
        # 标准化到0-1范围
        return min(total_risk / len(risk_factors), 1.0)
    
    def categorize_risk_level(self, risk_score: float) -> RiskLevel:
        """分类风险级别"""
        for level, threshold in self.risk_thresholds.items():
            if risk_score <= threshold:
                return level
        return RiskLevel.CRITICAL

class IntelligentDecisionSupport:
    """智能决策支持系统"""
    
    def __init__(self, config: Dict[str, Any], metrics_collector: Optional[MetricsCollector] = None):
        self.config = config
        self.metrics_collector = metrics_collector
        self.decision_analyzer = MultiCriteriaDecisionAnalyzer()
        self.risk_assessor = RiskAssessmentEngine()
        
        # 决策历史
        self.decision_history: List[DecisionRecommendation] = []
        
        # 决策模型
        self.decision_models = {}
        
        # 知识库
        self.decision_criteria_db = {}
        self.decision_options_db = {}
        self.evidence_db = {}
        
        logger.info("智能决策支持系统初始化完成")
    
    async def initialize(self):
        """初始化决策支持系统"""
        try:
            await self._load_decision_criteria()
            await self._load_decision_options()
            await self._load_evidence_database()
            await self._train_decision_models()
            
            logger.info("决策支持系统初始化成功")
            
        except Exception as e:
            logger.error(f"决策支持系统初始化失败: {e}")
    
    async def _load_decision_criteria(self):
        """加载决策标准"""
        # 治疗方案选择标准
        treatment_criteria = [
            DecisionCriteria(
                id="efficacy",
                name="疗效",
                description="治疗效果和成功率",
                weight=0.3,
                measurement_type="numeric",
                higher_is_better=True,
                mandatory=True
            ),
            DecisionCriteria(
                id="safety",
                name="安全性",
                description="副作用和风险程度",
                weight=0.25,
                measurement_type="numeric",
                higher_is_better=True,
                mandatory=True
            ),
            DecisionCriteria(
                id="cost",
                name="成本",
                description="治疗费用",
                weight=0.15,
                measurement_type="numeric",
                higher_is_better=False
            ),
            DecisionCriteria(
                id="convenience",
                name="便利性",
                description="治疗的便利程度",
                weight=0.1,
                measurement_type="numeric",
                higher_is_better=True
            ),
            DecisionCriteria(
                id="evidence_quality",
                name="证据质量",
                description="循证医学证据质量",
                weight=0.2,
                measurement_type="numeric",
                higher_is_better=True
            )
        ]
        
        self.decision_criteria_db[DecisionType.TREATMENT_SELECTION] = treatment_criteria
        
        # 生活方式改变标准
        lifestyle_criteria = [
            DecisionCriteria(
                id="health_impact",
                name="健康影响",
                description="对健康的积极影响",
                weight=0.35,
                measurement_type="numeric",
                higher_is_better=True,
                mandatory=True
            ),
            DecisionCriteria(
                id="feasibility",
                name="可行性",
                description="实施的可行性",
                weight=0.25,
                measurement_type="numeric",
                higher_is_better=True
            ),
            DecisionCriteria(
                id="sustainability",
                name="可持续性",
                description="长期坚持的可能性",
                weight=0.2,
                measurement_type="numeric",
                higher_is_better=True
            ),
            DecisionCriteria(
                id="enjoyment",
                name="愉悦度",
                description="活动的愉悦程度",
                weight=0.1,
                measurement_type="numeric",
                higher_is_better=True
            ),
            DecisionCriteria(
                id="social_support",
                name="社会支持",
                description="获得社会支持的程度",
                weight=0.1,
                measurement_type="numeric",
                higher_is_better=True
            )
        ]
        
        self.decision_criteria_db[DecisionType.LIFESTYLE_CHANGE] = lifestyle_criteria
    
    async def _load_decision_options(self):
        """加载决策选项"""
        # 示例：高血压治疗选项
        hypertension_options = [
            DecisionOption(
                id="ace_inhibitor",
                name="ACE抑制剂",
                description="血管紧张素转换酶抑制剂治疗",
                category="medication",
                criteria_scores={
                    "efficacy": 0.85,
                    "safety": 0.8,
                    "cost": 0.7,
                    "convenience": 0.9,
                    "evidence_quality": 0.95
                },
                estimated_cost=200.0,
                estimated_duration=365,
                success_rate=0.85,
                side_effects=["干咳", "血管性水肿", "高钾血症"],
                contraindications=["妊娠", "双侧肾动脉狭窄"],
                evidence_level=EvidenceLevel.LEVEL_1A,
                evidence_sources=["HOPE试验", "EUROPA试验", "PEACE试验"]
            ),
            DecisionOption(
                id="calcium_blocker",
                name="钙通道阻滞剂",
                description="钙离子通道阻滞剂治疗",
                category="medication",
                criteria_scores={
                    "efficacy": 0.8,
                    "safety": 0.85,
                    "cost": 0.6,
                    "convenience": 0.9,
                    "evidence_quality": 0.9
                },
                estimated_cost=250.0,
                estimated_duration=365,
                success_rate=0.8,
                side_effects=["踝部水肿", "牙龈增生", "便秘"],
                contraindications=["严重心力衰竭", "病态窦房结综合征"],
                evidence_level=EvidenceLevel.LEVEL_1A,
                evidence_sources=["ALLHAT试验", "VALUE试验"]
            ),
            DecisionOption(
                id="lifestyle_modification",
                name="生活方式干预",
                description="饮食、运动、减重等生活方式改变",
                category="lifestyle",
                criteria_scores={
                    "efficacy": 0.7,
                    "safety": 0.95,
                    "cost": 0.9,
                    "convenience": 0.6,
                    "evidence_quality": 0.85
                },
                estimated_cost=100.0,
                estimated_duration=180,
                success_rate=0.65,
                side_effects=[],
                contraindications=[],
                evidence_level=EvidenceLevel.LEVEL_1B,
                evidence_sources=["DASH研究", "PREMIER试验"]
            )
        ]
        
        self.decision_options_db["hypertension"] = hypertension_options
    
    async def _load_evidence_database(self):
        """加载证据数据库"""
        self.evidence_db = {
            "clinical_guidelines": {
                "hypertension": {
                    "source": "中国高血压防治指南2018",
                    "recommendations": [
                        "首选ACE抑制剂或ARB",
                        "可联合钙通道阻滞剂",
                        "生活方式干预是基础"
                    ],
                    "evidence_level": EvidenceLevel.LEVEL_1A
                }
            },
            "systematic_reviews": {
                "antihypertensive_drugs": {
                    "source": "Cochrane系统评价",
                    "findings": "ACE抑制剂在心血管保护方面优于其他药物",
                    "evidence_level": EvidenceLevel.LEVEL_1A
                }
            }
        }
    
    async def _train_decision_models(self):
        """训练决策模型"""
        try:
            # 这里可以训练机器学习模型来预测决策结果
            # 示例：训练一个简单的决策树
            
            # 模拟训练数据
            training_data = self._generate_training_data()
            
            if training_data:
                X = np.array([d["features"] for d in training_data])
                y = np.array([d["outcome"] for d in training_data])
                
                # 训练随机森林模型
                rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
                rf_model.fit(X, y)
                
                self.decision_models["treatment_outcome"] = rf_model
                
                logger.info("决策模型训练完成")
            
        except Exception as e:
            logger.error(f"决策模型训练失败: {e}")
    
    def _generate_training_data(self) -> List[Dict[str, Any]]:
        """生成训练数据（示例）"""
        # 这里应该从历史决策数据中生成真实的训练数据
        # 现在使用模拟数据
        training_data = []
        
        for i in range(1000):
            features = [
                np.random.uniform(0, 1),  # 疗效
                np.random.uniform(0, 1),  # 安全性
                np.random.uniform(0, 1),  # 成本
                np.random.uniform(0, 1),  # 便利性
                np.random.uniform(0, 1)   # 证据质量
            ]
            
            # 简单的结果计算（实际应该基于真实数据）
            outcome = 1 if sum(features) > 2.5 else 0
            
            training_data.append({
                "features": features,
                "outcome": outcome
            })
        
        return training_data
    
    @trace_operation("decision.generate_recommendation", SpanKind.INTERNAL)
    async def generate_decision_recommendation(
        self,
        context: DecisionContext,
        available_options: Optional[List[DecisionOption]] = None
    ) -> DecisionRecommendation:
        """生成决策推荐"""
        start_time = time.time()
        
        try:
            # 获取决策标准
            criteria = self.decision_criteria_db.get(
                context.decision_type, 
                self.decision_criteria_db.get(DecisionType.TREATMENT_SELECTION, [])
            )
            
            # 获取可用选项
            if available_options is None:
                available_options = await self._get_available_options(context)
            
            if not available_options:
                raise ValueError("没有可用的决策选项")
            
            # 多标准决策分析
            analyses = await self.decision_analyzer.analyze_options(
                available_options, criteria
            )
            
            # 风险评估
            risk_factors = await self.risk_assessor.assess_risks(context, available_options)
            
            # 选择最佳选项
            best_analysis = analyses[0] if analyses else None
            recommended_option = None
            
            for option in available_options:
                if best_analysis and option.id == best_analysis.option_id:
                    recommended_option = option
                    break
            
            if not recommended_option:
                recommended_option = available_options[0]
            
            # 生成决策理由
            rationale = await self._generate_decision_rationale(
                recommended_option, best_analysis, risk_factors, context
            )
            
            # 生成实施计划
            implementation_plan = await self._generate_implementation_plan(
                recommended_option, context
            )
            
            # 生成监测计划
            monitoring_plan = await self._generate_monitoring_plan(
                recommended_option, risk_factors, context
            )
            
            # 生成随访计划
            follow_up_schedule = await self._generate_follow_up_schedule(
                recommended_option, context
            )
            
            # 生成应急预案
            contingency_plans = await self._generate_contingency_plans(
                recommended_option, risk_factors
            )
            
            processing_time = time.time() - start_time
            
            recommendation = DecisionRecommendation(
                context=context,
                recommended_option=recommended_option,
                alternative_options=[opt for opt in available_options if opt.id != recommended_option.id],
                analysis_results=analyses,
                risk_factors=risk_factors,
                decision_rationale=rationale,
                implementation_plan=implementation_plan,
                monitoring_plan=monitoring_plan,
                follow_up_schedule=follow_up_schedule,
                contingency_plans=contingency_plans,
                quality_indicators=await self._generate_quality_indicators(recommended_option),
                processing_time=processing_time
            )
            
            # 记录决策历史
            self.decision_history.append(recommendation)
            
            # 记录指标
            if self.metrics_collector:
                self.metrics_collector.increment_counter(
                    "decision_recommendations_generated",
                    {"decision_type": context.decision_type.value}
                )
                self.metrics_collector.record_histogram(
                    "decision_processing_time",
                    processing_time,
                    {"decision_type": context.decision_type.value}
                )
            
            logger.info(f"生成决策推荐完成，推荐选项: {recommended_option.name}")
            return recommendation
            
        except Exception as e:
            logger.error(f"生成决策推荐失败: {e}")
            raise
    
    async def _get_available_options(self, context: DecisionContext) -> List[DecisionOption]:
        """获取可用的决策选项"""
        # 这里应该根据上下文从数据库或知识库中获取选项
        # 现在返回示例选项
        
        if "高血压" in context.current_symptoms or "高血压" in context.medical_history:
            return self.decision_options_db.get("hypertension", [])
        
        # 默认返回通用选项
        return []
    
    async def _generate_decision_rationale(
        self,
        option: DecisionOption,
        analysis: Optional[DecisionAnalysis],
        risk_factors: List[RiskFactor],
        context: DecisionContext
    ) -> str:
        """生成决策理由"""
        rationale_parts = []
        
        # 基于分析结果
        if analysis:
            rationale_parts.append(f"推荐{option.name}，综合得分{analysis.overall_score:.2f}")
            
            if analysis.pros:
                rationale_parts.append(f"主要优势：{'; '.join(analysis.pros[:3])}")
            
            if analysis.confidence_level > 0.8:
                rationale_parts.append("该推荐具有高置信度")
        
        # 基于证据
        if option.evidence_level in [EvidenceLevel.LEVEL_1A, EvidenceLevel.LEVEL_1B]:
            rationale_parts.append("该方案有高质量循证医学证据支持")
        
        # 基于风险
        high_risks = [r for r in risk_factors if r.severity in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]]
        if not high_risks:
            rationale_parts.append("风险评估显示该方案相对安全")
        
        # 基于个人化因素
        if context.preferences.get("prefer_natural", False) and "lifestyle" in option.category:
            rationale_parts.append("符合您对自然疗法的偏好")
        
        return "。".join(rationale_parts) + "。"
    
    async def _generate_implementation_plan(
        self,
        option: DecisionOption,
        context: DecisionContext
    ) -> List[str]:
        """生成实施计划"""
        plan = []
        
        if option.category == "medication":
            plan.extend([
                "1. 医师处方和用药指导",
                "2. 药师用药咨询",
                "3. 建立用药提醒",
                "4. 记录用药日志"
            ])
        elif option.category == "lifestyle":
            plan.extend([
                "1. 制定具体的行为改变目标",
                "2. 寻找社会支持",
                "3. 建立奖励机制",
                "4. 定期自我监测"
            ])
        
        # 添加通用步骤
        plan.extend([
            f"5. 安排{option.estimated_duration or 30}天后的效果评估",
            "6. 建立应急联系方式"
        ])
        
        return plan
    
    async def _generate_monitoring_plan(
        self,
        option: DecisionOption,
        risk_factors: List[RiskFactor],
        context: DecisionContext
    ) -> List[str]:
        """生成监测计划"""
        monitoring = []
        
        # 基于选项类型
        if option.category == "medication":
            monitoring.extend([
                "定期监测血压变化",
                "观察药物副作用",
                "检查肝肾功能"
            ])
        
        # 基于风险因素
        for risk in risk_factors:
            if risk.monitoring_indicators:
                monitoring.extend([
                    f"监测{risk.name}：{', '.join(risk.monitoring_indicators[:2])}"
                ])
        
        # 基于症状
        if context.current_symptoms:
            monitoring.append(f"跟踪症状变化：{', '.join(context.current_symptoms[:3])}")
        
        return list(set(monitoring))  # 去重
    
    async def _generate_follow_up_schedule(
        self,
        option: DecisionOption,
        context: DecisionContext
    ) -> List[Dict[str, Any]]:
        """生成随访计划"""
        schedule = []
        
        # 短期随访
        schedule.append({
            "time": "1周后",
            "purpose": "评估初期反应和副作用",
            "methods": ["电话随访", "症状记录"]
        })
        
        # 中期随访
        schedule.append({
            "time": "1个月后",
            "purpose": "评估治疗效果",
            "methods": ["门诊复查", "实验室检查"]
        })
        
        # 长期随访
        if option.estimated_duration and option.estimated_duration > 90:
            schedule.append({
                "time": "3个月后",
                "purpose": "长期效果评估和方案调整",
                "methods": ["全面评估", "方案优化"]
            })
        
        return schedule
    
    async def _generate_contingency_plans(
        self,
        option: DecisionOption,
        risk_factors: List[RiskFactor]
    ) -> List[str]:
        """生成应急预案"""
        contingencies = []
        
        # 基于副作用
        if option.side_effects:
            contingencies.append(f"如出现{option.side_effects[0]}等副作用，立即联系医生")
        
        # 基于风险因素
        critical_risks = [r for r in risk_factors if r.severity == RiskLevel.CRITICAL]
        for risk in critical_risks:
            contingencies.append(f"如出现{risk.name}征象，立即就医")
        
        # 通用应急预案
        contingencies.extend([
            "治疗无效时的替代方案",
            "紧急情况下的联系方式",
            "药物过敏的处理流程"
        ])
        
        return contingencies
    
    async def _generate_quality_indicators(self, option: DecisionOption) -> List[str]:
        """生成质量指标"""
        indicators = [
            "症状改善程度",
            "生活质量评分",
            "治疗依从性",
            "副作用发生率"
        ]
        
        if option.category == "medication":
            indicators.extend([
                "血药浓度达标率",
                "实验室指标改善"
            ])
        elif option.category == "lifestyle":
            indicators.extend([
                "行为改变持续性",
                "自我效能感提升"
            ])
        
        return indicators
    
    async def evaluate_decision_outcome(
        self,
        recommendation_id: str,
        outcome_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """评估决策结果"""
        try:
            # 查找原始推荐
            original_recommendation = None
            for rec in self.decision_history:
                if rec.metadata.get("id") == recommendation_id:
                    original_recommendation = rec
                    break
            
            if not original_recommendation:
                raise ValueError("未找到原始推荐记录")
            
            # 计算结果指标
            evaluation = {
                "recommendation_id": recommendation_id,
                "success": outcome_data.get("success", False),
                "effectiveness_score": outcome_data.get("effectiveness_score", 0.0),
                "safety_score": outcome_data.get("safety_score", 0.0),
                "satisfaction_score": outcome_data.get("satisfaction_score", 0.0),
                "adherence_rate": outcome_data.get("adherence_rate", 0.0),
                "side_effects_occurred": outcome_data.get("side_effects", []),
                "time_to_effect": outcome_data.get("time_to_effect"),
                "cost_actual": outcome_data.get("cost_actual"),
                "lessons_learned": outcome_data.get("lessons_learned", [])
            }
            
            # 更新决策模型（如果有的话）
            await self._update_decision_models(original_recommendation, evaluation)
            
            # 记录指标
            if self.metrics_collector:
                self.metrics_collector.increment_counter(
                    "decision_outcomes_evaluated",
                    {"success": str(evaluation["success"])}
                )
            
            logger.info(f"决策结果评估完成: {recommendation_id}")
            return evaluation
            
        except Exception as e:
            logger.error(f"决策结果评估失败: {e}")
            return {}
    
    async def _update_decision_models(
        self,
        recommendation: DecisionRecommendation,
        evaluation: Dict[str, Any]
    ):
        """更新决策模型"""
        try:
            # 这里可以实现在线学习，根据结果反馈更新模型
            # 现在只是记录日志
            logger.info(f"更新决策模型，推荐成功率: {evaluation['success']}")
            
        except Exception as e:
            logger.error(f"更新决策模型失败: {e}")
    
    async def get_decision_statistics(self) -> Dict[str, Any]:
        """获取决策统计信息"""
        try:
            total_decisions = len(self.decision_history)
            
            if total_decisions == 0:
                return {"total_decisions": 0}
            
            # 按决策类型统计
            type_stats = {}
            for rec in self.decision_history:
                decision_type = rec.context.decision_type.value
                if decision_type not in type_stats:
                    type_stats[decision_type] = 0
                type_stats[decision_type] += 1
            
            # 平均处理时间
            avg_processing_time = sum(
                rec.processing_time for rec in self.decision_history
            ) / total_decisions
            
            # 风险分布
            risk_distribution = {"low": 0, "moderate": 0, "high": 0}
            for rec in self.decision_history:
                risk_score = self.risk_assessor.calculate_overall_risk_score(rec.risk_factors)
                if risk_score < 0.3:
                    risk_distribution["low"] += 1
                elif risk_score < 0.7:
                    risk_distribution["moderate"] += 1
                else:
                    risk_distribution["high"] += 1
            
            return {
                "total_decisions": total_decisions,
                "decisions_by_type": type_stats,
                "average_processing_time": avg_processing_time,
                "risk_distribution": risk_distribution,
                "most_common_type": max(type_stats.items(), key=lambda x: x[1])[0] if type_stats else None
            }
            
        except Exception as e:
            logger.error(f"获取决策统计失败: {e}")
            return {}

def initialize_decision_support(
    config: Dict[str, Any],
    metrics_collector: Optional[MetricsCollector] = None
) -> IntelligentDecisionSupport:
    """初始化智能决策支持系统"""
    return IntelligentDecisionSupport(config, metrics_collector)

# 全局实例
_decision_support_instance: Optional[IntelligentDecisionSupport] = None

def get_decision_support() -> Optional[IntelligentDecisionSupport]:
    """获取决策支持系统实例"""
    return _decision_support_instance 