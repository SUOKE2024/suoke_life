#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能诊断辅助引擎 - 提供中医辨证和现代医学诊断的智能辅助功能
结合症状分析、疾病预测、诊断建议、治疗方案推荐等功能
"""

from typing import Dict, List, Any, Optional, Tuple, Union, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from loguru import logger
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
import warnings
warnings.filterwarnings('ignore')

from ..observability.metrics import MetricsCollector
from ..observability.tracing import trace_operation, SpanKind

class SymptomSeverity(str, Enum):
    """症状严重程度"""
    NONE = "none"           # 无
    MILD = "mild"           # 轻微
    MODERATE = "moderate"   # 中等
    SEVERE = "severe"       # 严重
    CRITICAL = "critical"   # 危急

class DiagnosisConfidence(str, Enum):
    """诊断置信度"""
    VERY_LOW = "very_low"       # 很低 (0-20%)
    LOW = "low"                 # 低 (20-40%)
    MODERATE = "moderate"       # 中等 (40-60%)
    HIGH = "high"               # 高 (60-80%)
    VERY_HIGH = "very_high"     # 很高 (80-100%)

class DiagnosisType(str, Enum):
    """诊断类型"""
    WESTERN_MEDICINE = "western_medicine"   # 西医诊断
    TCM_SYNDROME = "tcm_syndrome"           # 中医证型
    DIFFERENTIAL = "differential"           # 鉴别诊断
    PRELIMINARY = "preliminary"             # 初步诊断
    CONFIRMED = "confirmed"                 # 确诊
    SUSPECTED = "suspected"                 # 疑似

class TreatmentType(str, Enum):
    """治疗类型"""
    MEDICATION = "medication"               # 药物治疗
    TCM_HERBAL = "tcm_herbal"              # 中药治疗
    ACUPUNCTURE = "acupuncture"            # 针灸治疗
    LIFESTYLE = "lifestyle"                 # 生活方式
    SURGERY = "surgery"                     # 手术治疗
    PHYSIOTHERAPY = "physiotherapy"         # 物理治疗
    PSYCHOLOGICAL = "psychological"         # 心理治疗
    PREVENTIVE = "preventive"              # 预防措施

class UrgencyLevel(str, Enum):
    """紧急程度"""
    ROUTINE = "routine"         # 常规
    URGENT = "urgent"           # 紧急
    EMERGENT = "emergent"       # 急诊
    CRITICAL = "critical"       # 危急

@dataclass
class Symptom:
    """症状"""
    id: str
    name: str
    description: str
    severity: SymptomSeverity
    duration_days: Optional[int] = None
    frequency: Optional[str] = None          # 频率描述
    location: Optional[str] = None           # 部位
    quality: Optional[str] = None            # 性质
    aggravating_factors: List[str] = field(default_factory=list)
    relieving_factors: List[str] = field(default_factory=list)
    associated_symptoms: List[str] = field(default_factory=list)
    onset_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MedicalHistory:
    """病史"""
    user_id: str
    past_illnesses: List[str] = field(default_factory=list)
    current_medications: List[str] = field(default_factory=list)
    allergies: List[str] = field(default_factory=list)
    family_history: List[str] = field(default_factory=list)
    social_history: Dict[str, Any] = field(default_factory=dict)
    surgical_history: List[str] = field(default_factory=list)
    immunization_history: List[str] = field(default_factory=list)
    lifestyle_factors: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PhysicalExamination:
    """体格检查"""
    vital_signs: Dict[str, float] = field(default_factory=dict)
    general_appearance: Optional[str] = None
    head_neck: Dict[str, Any] = field(default_factory=dict)
    cardiovascular: Dict[str, Any] = field(default_factory=dict)
    respiratory: Dict[str, Any] = field(default_factory=dict)
    abdominal: Dict[str, Any] = field(default_factory=dict)
    neurological: Dict[str, Any] = field(default_factory=dict)
    musculoskeletal: Dict[str, Any] = field(default_factory=dict)
    skin: Dict[str, Any] = field(default_factory=dict)
    examination_date: datetime = field(default_factory=datetime.now)

@dataclass
class LaboratoryResult:
    """实验室检查结果"""
    test_name: str
    value: Union[float, str]
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    abnormal: bool = False
    test_date: datetime = field(default_factory=datetime.now)
    interpretation: Optional[str] = None

@dataclass
class DiagnosisCandidate:
    """诊断候选"""
    id: str
    name: str
    icd_code: Optional[str] = None
    diagnosis_type: DiagnosisType = DiagnosisType.PRELIMINARY
    confidence: float = 0.0
    confidence_level: DiagnosisConfidence = DiagnosisConfidence.LOW
    supporting_evidence: List[str] = field(default_factory=list)
    contradicting_evidence: List[str] = field(default_factory=list)
    required_tests: List[str] = field(default_factory=list)
    differential_diagnoses: List[str] = field(default_factory=list)
    prognosis: Optional[str] = None
    complications: List[str] = field(default_factory=list)

@dataclass
class TCMSyndrome:
    """中医证型"""
    id: str
    name: str
    description: str
    pattern_type: str                        # 证型类型
    organ_systems: List[str] = field(default_factory=list)
    pathogenesis: Optional[str] = None       # 病机
    tongue_manifestation: Optional[str] = None
    pulse_manifestation: Optional[str] = None
    key_symptoms: List[str] = field(default_factory=list)
    treatment_principle: Optional[str] = None
    recommended_formulas: List[str] = field(default_factory=list)
    confidence: float = 0.0

@dataclass
class TreatmentRecommendation:
    """治疗建议"""
    id: str
    treatment_type: TreatmentType
    description: str
    priority: int = 1                        # 优先级 (1-5)
    urgency: UrgencyLevel = UrgencyLevel.ROUTINE
    duration: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    contraindications: List[str] = field(default_factory=list)
    side_effects: List[str] = field(default_factory=list)
    monitoring_requirements: List[str] = field(default_factory=list)
    expected_outcomes: List[str] = field(default_factory=list)
    alternative_treatments: List[str] = field(default_factory=list)

@dataclass
class DiagnosisResult:
    """诊断结果"""
    user_id: str
    session_id: str
    primary_diagnoses: List[DiagnosisCandidate]
    differential_diagnoses: List[DiagnosisCandidate]
    tcm_syndromes: List[TCMSyndrome]
    treatment_recommendations: List[TreatmentRecommendation]
    follow_up_recommendations: List[str] = field(default_factory=list)
    red_flags: List[str] = field(default_factory=list)
    overall_confidence: float = 0.0
    reasoning: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DiagnosisSession:
    """诊断会话"""
    id: str
    user_id: str
    chief_complaint: str
    symptoms: List[Symptom]
    medical_history: Optional[MedicalHistory] = None
    physical_examination: Optional[PhysicalExamination] = None
    laboratory_results: List[LaboratoryResult] = field(default_factory=list)
    imaging_results: List[Dict[str, Any]] = field(default_factory=list)
    diagnosis_result: Optional[DiagnosisResult] = None
    status: str = "active"                   # active, completed, cancelled
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

class SymptomAnalyzer:
    """症状分析器"""
    
    def __init__(self):
        self.symptom_database = {}
        self.symptom_clusters = {}
        self.symptom_weights = {}
        self._load_symptom_knowledge()
    
    def _load_symptom_knowledge(self):
        """加载症状知识库"""
        # 常见症状及其权重
        self.symptom_weights = {
            "发热": 0.8, "头痛": 0.6, "咳嗽": 0.7, "胸痛": 0.9,
            "腹痛": 0.8, "恶心": 0.5, "呕吐": 0.6, "腹泻": 0.6,
            "便秘": 0.4, "疲劳": 0.3, "失眠": 0.4, "食欲不振": 0.5,
            "体重减轻": 0.7, "呼吸困难": 0.9, "心悸": 0.7, "头晕": 0.6,
            "皮疹": 0.6, "关节痛": 0.6, "肌肉痛": 0.4, "视力模糊": 0.7
        }
        
        # 症状聚类（相关症状组合）
        self.symptom_clusters = {
            "呼吸系统": ["咳嗽", "呼吸困难", "胸痛", "咳痰", "喘息"],
            "消化系统": ["腹痛", "恶心", "呕吐", "腹泻", "便秘", "食欲不振"],
            "心血管系统": ["胸痛", "心悸", "呼吸困难", "水肿", "头晕"],
            "神经系统": ["头痛", "头晕", "失眠", "记忆力减退", "肢体麻木"],
            "内分泌系统": ["疲劳", "体重变化", "多饮", "多尿", "怕冷怕热"],
            "免疫系统": ["发热", "疲劳", "关节痛", "皮疹", "淋巴结肿大"]
        }
    
    async def analyze_symptoms(
        self, 
        symptoms: List[Symptom],
        user_id: str
    ) -> Dict[str, Any]:
        """分析症状"""
        try:
            # 症状严重程度评估
            severity_analysis = await self._assess_symptom_severity(symptoms)
            
            # 症状聚类分析
            cluster_analysis = await self._analyze_symptom_clusters(symptoms)
            
            # 症状时间模式分析
            temporal_analysis = await self._analyze_temporal_patterns(symptoms)
            
            # 红旗症状识别
            red_flags = await self._identify_red_flags(symptoms)
            
            # 症状关联性分析
            correlation_analysis = await self._analyze_symptom_correlations(symptoms)
            
            return {
                "severity_analysis": severity_analysis,
                "cluster_analysis": cluster_analysis,
                "temporal_analysis": temporal_analysis,
                "red_flags": red_flags,
                "correlation_analysis": correlation_analysis,
                "overall_urgency": self._calculate_overall_urgency(severity_analysis, red_flags)
            }
            
        except Exception as e:
            logger.error(f"症状分析失败: {e}")
            raise
    
    async def _assess_symptom_severity(self, symptoms: List[Symptom]) -> Dict[str, Any]:
        """评估症状严重程度"""
        severity_scores = {}
        total_score = 0
        
        for symptom in symptoms:
            # 基础严重程度分数
            base_score = {
                SymptomSeverity.NONE: 0,
                SymptomSeverity.MILD: 1,
                SymptomSeverity.MODERATE: 2,
                SymptomSeverity.SEVERE: 3,
                SymptomSeverity.CRITICAL: 4
            }.get(symptom.severity, 1)
            
            # 症状权重调整
            weight = self.symptom_weights.get(symptom.name, 0.5)
            
            # 持续时间调整
            duration_multiplier = 1.0
            if symptom.duration_days:
                if symptom.duration_days > 30:
                    duration_multiplier = 1.3
                elif symptom.duration_days > 7:
                    duration_multiplier = 1.1
            
            final_score = base_score * weight * duration_multiplier
            severity_scores[symptom.name] = final_score
            total_score += final_score
        
        return {
            "individual_scores": severity_scores,
            "total_score": total_score,
            "average_score": total_score / len(symptoms) if symptoms else 0,
            "max_severity": max([s.severity for s in symptoms], default=SymptomSeverity.NONE),
            "critical_symptoms": [s.name for s in symptoms if s.severity == SymptomSeverity.CRITICAL]
        }
    
    async def _analyze_symptom_clusters(self, symptoms: List[Symptom]) -> Dict[str, Any]:
        """分析症状聚类"""
        cluster_matches = {}
        symptom_names = [s.name for s in symptoms]
        
        for cluster_name, cluster_symptoms in self.symptom_clusters.items():
            matches = set(symptom_names) & set(cluster_symptoms)
            if matches:
                cluster_matches[cluster_name] = {
                    "matched_symptoms": list(matches),
                    "match_count": len(matches),
                    "match_percentage": len(matches) / len(cluster_symptoms),
                    "cluster_score": len(matches) * (len(matches) / len(cluster_symptoms))
                }
        
        # 找出最可能的系统
        primary_system = max(cluster_matches.items(), 
                           key=lambda x: x[1]["cluster_score"])[0] if cluster_matches else None
        
        return {
            "cluster_matches": cluster_matches,
            "primary_system": primary_system,
            "multi_system_involvement": len(cluster_matches) > 1,
            "system_count": len(cluster_matches)
        }
    
    async def _analyze_temporal_patterns(self, symptoms: List[Symptom]) -> Dict[str, Any]:
        """分析症状时间模式"""
        patterns = {
            "acute": [],      # 急性 (<7天)
            "subacute": [],   # 亚急性 (7-30天)
            "chronic": []     # 慢性 (>30天)
        }
        
        for symptom in symptoms:
            if symptom.duration_days:
                if symptom.duration_days <= 7:
                    patterns["acute"].append(symptom.name)
                elif symptom.duration_days <= 30:
                    patterns["subacute"].append(symptom.name)
                else:
                    patterns["chronic"].append(symptom.name)
        
        # 判断主要时间模式
        primary_pattern = max(patterns.items(), key=lambda x: len(x[1]))[0] if any(patterns.values()) else "unknown"
        
        return {
            "patterns": patterns,
            "primary_pattern": primary_pattern,
            "pattern_consistency": len([p for p in patterns.values() if p]) == 1,
            "mixed_temporal_pattern": len([p for p in patterns.values() if p]) > 1
        }
    
    async def _identify_red_flags(self, symptoms: List[Symptom]) -> List[str]:
        """识别红旗症状"""
        red_flags = []
        
        # 定义红旗症状
        red_flag_symptoms = {
            "胸痛": "可能心肌梗死或肺栓塞",
            "呼吸困难": "可能心力衰竭或肺栓塞",
            "意识改变": "可能脑血管意外或代谢紊乱",
            "剧烈头痛": "可能脑出血或脑膜炎",
            "高热": "可能严重感染",
            "大量出血": "可能失血性休克",
            "严重腹痛": "可能急腹症",
            "突然失明": "可能视网膜脱离或血管阻塞"
        }
        
        for symptom in symptoms:
            if symptom.severity == SymptomSeverity.CRITICAL:
                red_flags.append(f"危急症状: {symptom.name}")
            
            if symptom.name in red_flag_symptoms:
                red_flags.append(f"{symptom.name}: {red_flag_symptoms[symptom.name]}")
        
        return red_flags
    
    async def _analyze_symptom_correlations(self, symptoms: List[Symptom]) -> Dict[str, Any]:
        """分析症状关联性"""
        # 常见症状组合
        common_combinations = {
            ("发热", "咳嗽"): "呼吸道感染",
            ("腹痛", "腹泻"): "胃肠炎",
            ("胸痛", "呼吸困难"): "心肺疾病",
            ("头痛", "发热"): "感染性疾病",
            ("疲劳", "体重减轻"): "慢性疾病"
        }
        
        symptom_names = set(s.name for s in symptoms)
        found_combinations = []
        
        for combination, description in common_combinations.items():
            if set(combination).issubset(symptom_names):
                found_combinations.append({
                    "symptoms": combination,
                    "description": description,
                    "confidence": 0.7
                })
        
        return {
            "found_combinations": found_combinations,
            "combination_count": len(found_combinations),
            "isolated_symptoms": list(symptom_names - 
                                    set().union(*[set(c["symptoms"]) for c in found_combinations]))
        }
    
    def _calculate_overall_urgency(self, severity_analysis: Dict, red_flags: List[str]) -> UrgencyLevel:
        """计算整体紧急程度"""
        if red_flags or severity_analysis.get("critical_symptoms"):
            return UrgencyLevel.CRITICAL
        elif severity_analysis.get("total_score", 0) > 10:
            return UrgencyLevel.EMERGENT
        elif severity_analysis.get("total_score", 0) > 5:
            return UrgencyLevel.URGENT
        else:
            return UrgencyLevel.ROUTINE

class DiseasePredictor:
    """疾病预测器"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        self.disease_database = {}
        self._initialize_models()
        self._load_disease_knowledge()
    
    def _initialize_models(self):
        """初始化预测模型"""
        self.models = {
            "random_forest": RandomForestClassifier(n_estimators=100, random_state=42),
            "gradient_boosting": GradientBoostingClassifier(random_state=42),
            "naive_bayes": GaussianNB(),
            "svm": SVC(probability=True, random_state=42),
            "neural_network": MLPClassifier(hidden_layer_sizes=(100, 50), random_state=42)
        }
        
        self.scalers = {
            "standard": StandardScaler(),
            "minmax": StandardScaler()
        }
    
    def _load_disease_knowledge(self):
        """加载疾病知识库"""
        # 常见疾病及其典型症状
        self.disease_database = {
            "感冒": {
                "symptoms": ["发热", "咳嗽", "流鼻涕", "头痛", "疲劳"],
                "severity": "mild",
                "duration": "7-10天",
                "icd_code": "J00"
            },
            "流感": {
                "symptoms": ["高热", "肌肉痛", "头痛", "疲劳", "咳嗽"],
                "severity": "moderate",
                "duration": "7-14天",
                "icd_code": "J11"
            },
            "肺炎": {
                "symptoms": ["发热", "咳嗽", "胸痛", "呼吸困难", "咳痰"],
                "severity": "severe",
                "duration": "14-21天",
                "icd_code": "J18"
            },
            "胃炎": {
                "symptoms": ["腹痛", "恶心", "呕吐", "食欲不振", "腹胀"],
                "severity": "mild",
                "duration": "3-7天",
                "icd_code": "K29"
            },
            "高血压": {
                "symptoms": ["头痛", "头晕", "心悸", "疲劳"],
                "severity": "moderate",
                "duration": "慢性",
                "icd_code": "I10"
            }
        }
    
    async def predict_diseases(
        self,
        symptoms: List[Symptom],
        medical_history: Optional[MedicalHistory] = None,
        user_id: str = None
    ) -> List[DiagnosisCandidate]:
        """预测疾病"""
        try:
            # 基于规则的预测
            rule_based_predictions = await self._rule_based_prediction(symptoms, medical_history)
            
            # 基于机器学习的预测（如果有足够数据）
            ml_predictions = await self._ml_based_prediction(symptoms, medical_history)
            
            # 基于相似性的预测
            similarity_predictions = await self._similarity_based_prediction(symptoms)
            
            # 合并和排序预测结果
            all_predictions = rule_based_predictions + ml_predictions + similarity_predictions
            merged_predictions = await self._merge_predictions(all_predictions)
            
            # 排序并返回前10个最可能的诊断
            sorted_predictions = sorted(merged_predictions, key=lambda x: x.confidence, reverse=True)
            return sorted_predictions[:10]
            
        except Exception as e:
            logger.error(f"疾病预测失败: {e}")
            raise
    
    async def _rule_based_prediction(
        self,
        symptoms: List[Symptom],
        medical_history: Optional[MedicalHistory] = None
    ) -> List[DiagnosisCandidate]:
        """基于规则的疾病预测"""
        predictions = []
        symptom_names = [s.name for s in symptoms]
        
        for disease_name, disease_info in self.disease_database.items():
            # 计算症状匹配度
            disease_symptoms = set(disease_info["symptoms"])
            patient_symptoms = set(symptom_names)
            
            matched_symptoms = disease_symptoms & patient_symptoms
            match_ratio = len(matched_symptoms) / len(disease_symptoms) if disease_symptoms else 0
            
            if match_ratio > 0.3:  # 至少30%症状匹配
                confidence = min(match_ratio * 0.8, 0.9)  # 基于规则的置信度不超过90%
                
                # 考虑病史影响
                if medical_history and disease_name in medical_history.past_illnesses:
                    confidence *= 1.2  # 既往史增加置信度
                
                confidence = min(confidence, 1.0)
                
                prediction = DiagnosisCandidate(
                    id=f"rule_{disease_name}",
                    name=disease_name,
                    icd_code=disease_info.get("icd_code"),
                    diagnosis_type=DiagnosisType.PRELIMINARY,
                    confidence=confidence,
                    confidence_level=self._get_confidence_level(confidence),
                    supporting_evidence=list(matched_symptoms),
                    contradicting_evidence=[],
                    required_tests=self._get_required_tests(disease_name),
                    differential_diagnoses=[]
                )
                
                predictions.append(prediction)
        
        return predictions
    
    async def _ml_based_prediction(
        self,
        symptoms: List[Symptom],
        medical_history: Optional[MedicalHistory] = None
    ) -> List[DiagnosisCandidate]:
        """基于机器学习的疾病预测"""
        # 这里是一个简化的实现，实际应用中需要大量训练数据
        predictions = []
        
        try:
            # 特征工程
            features = await self._extract_features(symptoms, medical_history)
            
            # 如果有预训练模型，进行预测
            if "trained_model" in self.models:
                # 这里应该是实际的模型预测逻辑
                pass
            
        except Exception as e:
            logger.warning(f"机器学习预测失败: {e}")
        
        return predictions
    
    async def _similarity_based_prediction(self, symptoms: List[Symptom]) -> List[DiagnosisCandidate]:
        """基于相似性的疾病预测"""
        predictions = []
        symptom_names = set(s.name for s in symptoms)
        
        for disease_name, disease_info in self.disease_database.items():
            disease_symptoms = set(disease_info["symptoms"])
            
            # 计算Jaccard相似度
            intersection = len(symptom_names & disease_symptoms)
            union = len(symptom_names | disease_symptoms)
            jaccard_similarity = intersection / union if union > 0 else 0
            
            if jaccard_similarity > 0.2:
                confidence = jaccard_similarity * 0.7  # 相似性预测置信度较低
                
                prediction = DiagnosisCandidate(
                    id=f"similarity_{disease_name}",
                    name=disease_name,
                    icd_code=disease_info.get("icd_code"),
                    diagnosis_type=DiagnosisType.SUSPECTED,
                    confidence=confidence,
                    confidence_level=self._get_confidence_level(confidence),
                    supporting_evidence=list(symptom_names & disease_symptoms),
                    contradicting_evidence=[],
                    required_tests=self._get_required_tests(disease_name),
                    differential_diagnoses=[]
                )
                
                predictions.append(prediction)
        
        return predictions
    
    async def _extract_features(
        self,
        symptoms: List[Symptom],
        medical_history: Optional[MedicalHistory] = None
    ) -> np.ndarray:
        """提取特征向量"""
        features = []
        
        # 症状特征
        all_symptoms = list(self.symptom_weights.keys())
        symptom_vector = [0] * len(all_symptoms)
        
        for symptom in symptoms:
            if symptom.name in all_symptoms:
                idx = all_symptoms.index(symptom.name)
                severity_score = {
                    SymptomSeverity.NONE: 0,
                    SymptomSeverity.MILD: 1,
                    SymptomSeverity.MODERATE: 2,
                    SymptomSeverity.SEVERE: 3,
                    SymptomSeverity.CRITICAL: 4
                }.get(symptom.severity, 1)
                symptom_vector[idx] = severity_score
        
        features.extend(symptom_vector)
        
        # 病史特征
        if medical_history:
            features.extend([
                len(medical_history.past_illnesses),
                len(medical_history.current_medications),
                len(medical_history.allergies),
                len(medical_history.family_history)
            ])
        else:
            features.extend([0, 0, 0, 0])
        
        return np.array(features).reshape(1, -1)
    
    async def _merge_predictions(self, all_predictions: List[DiagnosisCandidate]) -> List[DiagnosisCandidate]:
        """合并预测结果"""
        merged = {}
        
        for prediction in all_predictions:
            if prediction.name in merged:
                # 合并相同疾病的预测
                existing = merged[prediction.name]
                # 取最高置信度
                if prediction.confidence > existing.confidence:
                    merged[prediction.name] = prediction
                # 合并支持证据
                existing.supporting_evidence = list(set(existing.supporting_evidence + prediction.supporting_evidence))
            else:
                merged[prediction.name] = prediction
        
        return list(merged.values())
    
    def _get_confidence_level(self, confidence: float) -> DiagnosisConfidence:
        """获取置信度级别"""
        if confidence >= 0.8:
            return DiagnosisConfidence.VERY_HIGH
        elif confidence >= 0.6:
            return DiagnosisConfidence.HIGH
        elif confidence >= 0.4:
            return DiagnosisConfidence.MODERATE
        elif confidence >= 0.2:
            return DiagnosisConfidence.LOW
        else:
            return DiagnosisConfidence.VERY_LOW
    
    def _get_required_tests(self, disease_name: str) -> List[str]:
        """获取建议检查项目"""
        test_recommendations = {
            "感冒": ["血常规"],
            "流感": ["血常规", "流感病毒检测"],
            "肺炎": ["胸部X光", "血常规", "痰培养"],
            "胃炎": ["胃镜检查", "幽门螺杆菌检测"],
            "高血压": ["血压监测", "心电图", "血生化"]
        }
        
        return test_recommendations.get(disease_name, ["血常规", "尿常规"])

class TCMDiagnosisEngine:
    """中医诊断引擎"""
    
    def __init__(self):
        self.syndrome_database = {}
        self.tongue_patterns = {}
        self.pulse_patterns = {}
        self._load_tcm_knowledge()
    
    def _load_tcm_knowledge(self):
        """加载中医知识库"""
        # 常见证型
        self.syndrome_database = {
            "风寒感冒": {
                "pattern_type": "外感证",
                "organ_systems": ["肺"],
                "pathogenesis": "风寒外袭，肺气失宣",
                "key_symptoms": ["恶寒重", "发热轻", "无汗", "头痛", "鼻塞", "流清涕", "咳嗽"],
                "tongue": "舌淡红，苔薄白",
                "pulse": "脉浮紧",
                "treatment_principle": "辛温解表，宣肺散寒",
                "formulas": ["麻黄汤", "桂枝汤"]
            },
            "风热感冒": {
                "pattern_type": "外感证",
                "organ_systems": ["肺"],
                "pathogenesis": "风热外袭，肺气失宣",
                "key_symptoms": ["发热重", "恶寒轻", "有汗", "头痛", "咽痛", "咳嗽", "痰黄"],
                "tongue": "舌红，苔薄黄",
                "pulse": "脉浮数",
                "treatment_principle": "辛凉解表，宣肺清热",
                "formulas": ["银翘散", "桑菊饮"]
            },
            "脾胃虚弱": {
                "pattern_type": "脏腑证",
                "organ_systems": ["脾", "胃"],
                "pathogenesis": "脾胃虚弱，运化失司",
                "key_symptoms": ["食欲不振", "腹胀", "便溏", "疲乏", "面色萎黄"],
                "tongue": "舌淡，苔白",
                "pulse": "脉细弱",
                "treatment_principle": "健脾益气，和胃化湿",
                "formulas": ["四君子汤", "参苓白术散"]
            },
            "肝郁气滞": {
                "pattern_type": "脏腑证",
                "organ_systems": ["肝"],
                "pathogenesis": "情志不遂，肝气郁结",
                "key_symptoms": ["胸胁胀痛", "情绪抑郁", "易怒", "叹息", "月经不调"],
                "tongue": "舌淡红，苔薄白",
                "pulse": "脉弦",
                "treatment_principle": "疏肝理气，调畅气机",
                "formulas": ["逍遥散", "柴胡疏肝散"]
            },
            "肾阳虚": {
                "pattern_type": "脏腑证",
                "organ_systems": ["肾"],
                "pathogenesis": "肾阳不足，温煦失职",
                "key_symptoms": ["畏寒肢冷", "腰膝酸软", "夜尿频多", "阳痿", "面色苍白"],
                "tongue": "舌淡胖，苔白",
                "pulse": "脉沉迟",
                "treatment_principle": "温补肾阳",
                "formulas": ["肾气丸", "右归丸"]
            }
        }
    
    async def diagnose_tcm_syndrome(
        self,
        symptoms: List[Symptom],
        tongue_manifestation: Optional[str] = None,
        pulse_manifestation: Optional[str] = None,
        user_id: str = None
    ) -> List[TCMSyndrome]:
        """中医辨证"""
        try:
            # 症状分析
            symptom_analysis = await self._analyze_tcm_symptoms(symptoms)
            
            # 舌象分析
            tongue_analysis = await self._analyze_tongue(tongue_manifestation)
            
            # 脉象分析
            pulse_analysis = await self._analyze_pulse(pulse_manifestation)
            
            # 综合辨证
            syndromes = await self._comprehensive_syndrome_differentiation(
                symptom_analysis, tongue_analysis, pulse_analysis
            )
            
            return syndromes
            
        except Exception as e:
            logger.error(f"中医辨证失败: {e}")
            raise
    
    async def _analyze_tcm_symptoms(self, symptoms: List[Symptom]) -> Dict[str, Any]:
        """分析中医症状"""
        symptom_names = [s.name for s in symptoms]
        syndrome_scores = {}
        
        for syndrome_name, syndrome_info in self.syndrome_database.items():
            key_symptoms = syndrome_info["key_symptoms"]
            matched_symptoms = set(symptom_names) & set(key_symptoms)
            
            if matched_symptoms:
                score = len(matched_symptoms) / len(key_symptoms)
                syndrome_scores[syndrome_name] = {
                    "score": score,
                    "matched_symptoms": list(matched_symptoms),
                    "syndrome_info": syndrome_info
                }
        
        return syndrome_scores
    
    async def _analyze_tongue(self, tongue_manifestation: Optional[str]) -> Dict[str, Any]:
        """分析舌象"""
        if not tongue_manifestation:
            return {"confidence": 0.0, "matches": []}
        
        tongue_matches = []
        
        for syndrome_name, syndrome_info in self.syndrome_database.items():
            tongue_pattern = syndrome_info.get("tongue", "")
            if tongue_pattern and tongue_pattern in tongue_manifestation:
                tongue_matches.append({
                    "syndrome": syndrome_name,
                    "pattern": tongue_pattern,
                    "confidence": 0.8
                })
        
        return {
            "confidence": 0.8 if tongue_matches else 0.0,
            "matches": tongue_matches
        }
    
    async def _analyze_pulse(self, pulse_manifestation: Optional[str]) -> Dict[str, Any]:
        """分析脉象"""
        if not pulse_manifestation:
            return {"confidence": 0.0, "matches": []}
        
        pulse_matches = []
        
        for syndrome_name, syndrome_info in self.syndrome_database.items():
            pulse_pattern = syndrome_info.get("pulse", "")
            if pulse_pattern and pulse_pattern in pulse_manifestation:
                pulse_matches.append({
                    "syndrome": syndrome_name,
                    "pattern": pulse_pattern,
                    "confidence": 0.8
                })
        
        return {
            "confidence": 0.8 if pulse_matches else 0.0,
            "matches": pulse_matches
        }
    
    async def _comprehensive_syndrome_differentiation(
        self,
        symptom_analysis: Dict[str, Any],
        tongue_analysis: Dict[str, Any],
        pulse_analysis: Dict[str, Any]
    ) -> List[TCMSyndrome]:
        """综合辨证"""
        syndrome_confidences = {}
        
        # 症状权重
        for syndrome_name, syndrome_data in symptom_analysis.items():
            syndrome_confidences[syndrome_name] = syndrome_data["score"] * 0.6
        
        # 舌象权重
        for match in tongue_analysis.get("matches", []):
            syndrome_name = match["syndrome"]
            if syndrome_name in syndrome_confidences:
                syndrome_confidences[syndrome_name] += match["confidence"] * 0.2
            else:
                syndrome_confidences[syndrome_name] = match["confidence"] * 0.2
        
        # 脉象权重
        for match in pulse_analysis.get("matches", []):
            syndrome_name = match["syndrome"]
            if syndrome_name in syndrome_confidences:
                syndrome_confidences[syndrome_name] += match["confidence"] * 0.2
            else:
                syndrome_confidences[syndrome_name] = match["confidence"] * 0.2
        
        # 创建TCM证型结果
        syndromes = []
        for syndrome_name, confidence in syndrome_confidences.items():
            if confidence > 0.3:  # 置信度阈值
                syndrome_info = self.syndrome_database[syndrome_name]
                
                syndrome = TCMSyndrome(
                    id=f"tcm_{syndrome_name}",
                    name=syndrome_name,
                    description=syndrome_info.get("pathogenesis", ""),
                    pattern_type=syndrome_info["pattern_type"],
                    organ_systems=syndrome_info["organ_systems"],
                    pathogenesis=syndrome_info.get("pathogenesis"),
                    tongue_manifestation=syndrome_info.get("tongue"),
                    pulse_manifestation=syndrome_info.get("pulse"),
                    key_symptoms=syndrome_info["key_symptoms"],
                    treatment_principle=syndrome_info.get("treatment_principle"),
                    recommended_formulas=syndrome_info.get("formulas", []),
                    confidence=min(confidence, 1.0)
                )
                
                syndromes.append(syndrome)
        
        # 按置信度排序
        syndromes.sort(key=lambda x: x.confidence, reverse=True)
        return syndromes

class TreatmentRecommendationEngine:
    """治疗建议引擎"""
    
    def __init__(self):
        self.treatment_database = {}
        self.drug_interactions = {}
        self.contraindications = {}
        self._load_treatment_knowledge()
    
    def _load_treatment_knowledge(self):
        """加载治疗知识库"""
        # 治疗方案数据库
        self.treatment_database = {
            "感冒": [
                {
                    "type": TreatmentType.MEDICATION,
                    "description": "对症治疗：解热镇痛药",
                    "medications": ["对乙酰氨基酚", "布洛芬"],
                    "dosage": "按说明书服用",
                    "duration": "3-5天",
                    "priority": 1
                },
                {
                    "type": TreatmentType.LIFESTYLE,
                    "description": "充分休息，多饮水",
                    "priority": 1
                }
            ],
            "高血压": [
                {
                    "type": TreatmentType.MEDICATION,
                    "description": "ACE抑制剂或ARB类药物",
                    "medications": ["依那普利", "氯沙坦"],
                    "priority": 1,
                    "monitoring": ["血压", "肾功能"]
                },
                {
                    "type": TreatmentType.LIFESTYLE,
                    "description": "低盐饮食，规律运动，控制体重",
                    "priority": 1
                }
            ]
        }
        
        # 中药治疗方案
        self.tcm_treatments = {
            "风寒感冒": [
                {
                    "type": TreatmentType.TCM_HERBAL,
                    "formula": "麻黄汤",
                    "composition": ["麻黄", "桂枝", "杏仁", "甘草"],
                    "dosage": "水煎服，日2次",
                    "duration": "3-5天"
                }
            ],
            "脾胃虚弱": [
                {
                    "type": TreatmentType.TCM_HERBAL,
                    "formula": "四君子汤",
                    "composition": ["人参", "白术", "茯苓", "甘草"],
                    "dosage": "水煎服，日2次",
                    "duration": "2-4周"
                }
            ]
        }
    
    async def generate_treatment_recommendations(
        self,
        diagnoses: List[DiagnosisCandidate],
        tcm_syndromes: List[TCMSyndrome],
        medical_history: Optional[MedicalHistory] = None,
        user_id: str = None
    ) -> List[TreatmentRecommendation]:
        """生成治疗建议"""
        try:
            recommendations = []
            
            # 西医治疗建议
            for diagnosis in diagnoses:
                if diagnosis.confidence > 0.5:  # 只为高置信度诊断提供治疗建议
                    western_treatments = await self._get_western_treatments(diagnosis, medical_history)
                    recommendations.extend(western_treatments)
            
            # 中医治疗建议
            for syndrome in tcm_syndromes:
                if syndrome.confidence > 0.5:
                    tcm_treatments = await self._get_tcm_treatments(syndrome, medical_history)
                    recommendations.extend(tcm_treatments)
            
            # 生活方式建议
            lifestyle_recommendations = await self._get_lifestyle_recommendations(diagnoses, tcm_syndromes)
            recommendations.extend(lifestyle_recommendations)
            
            # 检查药物相互作用和禁忌症
            recommendations = await self._check_safety(recommendations, medical_history)
            
            # 按优先级排序
            recommendations.sort(key=lambda x: (x.urgency.value, x.priority))
            
            return recommendations
            
        except Exception as e:
            logger.error(f"生成治疗建议失败: {e}")
            raise
    
    async def _get_western_treatments(
        self,
        diagnosis: DiagnosisCandidate,
        medical_history: Optional[MedicalHistory] = None
    ) -> List[TreatmentRecommendation]:
        """获取西医治疗建议"""
        treatments = []
        
        if diagnosis.name in self.treatment_database:
            treatment_options = self.treatment_database[diagnosis.name]
            
            for i, treatment in enumerate(treatment_options):
                recommendation = TreatmentRecommendation(
                    id=f"western_{diagnosis.name}_{i}",
                    treatment_type=treatment["type"],
                    description=treatment["description"],
                    priority=treatment.get("priority", 3),
                    urgency=self._determine_urgency(diagnosis),
                    duration=treatment.get("duration"),
                    dosage=treatment.get("dosage"),
                    frequency=treatment.get("frequency"),
                    contraindications=self._get_contraindications(treatment, medical_history),
                    side_effects=treatment.get("side_effects", []),
                    monitoring_requirements=treatment.get("monitoring", []),
                    expected_outcomes=treatment.get("outcomes", [])
                )
                
                treatments.append(recommendation)
        
        return treatments
    
    async def _get_tcm_treatments(
        self,
        syndrome: TCMSyndrome,
        medical_history: Optional[MedicalHistory] = None
    ) -> List[TreatmentRecommendation]:
        """获取中医治疗建议"""
        treatments = []
        
        # 中药方剂
        for formula in syndrome.recommended_formulas:
            if formula in self.tcm_treatments.get(syndrome.name, []):
                treatment_info = next(t for t in self.tcm_treatments[syndrome.name] if t.get("formula") == formula)
                
                recommendation = TreatmentRecommendation(
                    id=f"tcm_{syndrome.name}_{formula}",
                    treatment_type=TreatmentType.TCM_HERBAL,
                    description=f"中药方剂：{formula}",
                    priority=2,
                    urgency=UrgencyLevel.ROUTINE,
                    duration=treatment_info.get("duration"),
                    dosage=treatment_info.get("dosage"),
                    contraindications=self._get_tcm_contraindications(treatment_info, medical_history),
                    monitoring_requirements=["中医师随诊"],
                    expected_outcomes=[f"改善{syndrome.name}症状"]
                )
                
                treatments.append(recommendation)
        
        # 针灸治疗
        if syndrome.pattern_type in ["气滞", "血瘀", "痰湿"]:
            acupuncture = TreatmentRecommendation(
                id=f"acupuncture_{syndrome.name}",
                treatment_type=TreatmentType.ACUPUNCTURE,
                description=f"针灸治疗{syndrome.name}",
                priority=3,
                urgency=UrgencyLevel.ROUTINE,
                duration="2-4周",
                frequency="每周2-3次",
                contraindications=["孕妇慎用", "出血倾向者慎用"],
                expected_outcomes=[f"调理{syndrome.name}"]
            )
            treatments.append(acupuncture)
        
        return treatments
    
    async def _get_lifestyle_recommendations(
        self,
        diagnoses: List[DiagnosisCandidate],
        tcm_syndromes: List[TCMSyndrome]
    ) -> List[TreatmentRecommendation]:
        """获取生活方式建议"""
        recommendations = []
        
        # 通用生活方式建议
        general_lifestyle = TreatmentRecommendation(
            id="lifestyle_general",
            treatment_type=TreatmentType.LIFESTYLE,
            description="保持规律作息，适量运动，均衡饮食",
            priority=2,
            urgency=UrgencyLevel.ROUTINE,
            expected_outcomes=["提高整体健康水平", "增强免疫力"]
        )
        recommendations.append(general_lifestyle)
        
        # 基于诊断的特定建议
        for diagnosis in diagnoses:
            if "感冒" in diagnosis.name:
                cold_lifestyle = TreatmentRecommendation(
                    id="lifestyle_cold",
                    treatment_type=TreatmentType.LIFESTYLE,
                    description="充分休息，多饮温水，避免受凉",
                    priority=1,
                    urgency=UrgencyLevel.URGENT,
                    duration="直至症状缓解",
                    expected_outcomes=["加速康复", "减轻症状"]
                )
                recommendations.append(cold_lifestyle)
        
        # 基于中医证型的调理建议
        for syndrome in tcm_syndromes:
            if "虚" in syndrome.name:
                tonifying_lifestyle = TreatmentRecommendation(
                    id=f"lifestyle_tonifying_{syndrome.name}",
                    treatment_type=TreatmentType.LIFESTYLE,
                    description="避免过度劳累，注意保暖，适当进补",
                    priority=2,
                    urgency=UrgencyLevel.ROUTINE,
                    expected_outcomes=["改善体质", "增强体力"]
                )
                recommendations.append(tonifying_lifestyle)
        
        return recommendations
    
    async def _check_safety(
        self,
        recommendations: List[TreatmentRecommendation],
        medical_history: Optional[MedicalHistory] = None
    ) -> List[TreatmentRecommendation]:
        """检查治疗安全性"""
        if not medical_history:
            return recommendations
        
        safe_recommendations = []
        
        for recommendation in recommendations:
            # 检查过敏史
            if medical_history.allergies:
                has_allergy = any(allergy in recommendation.description 
                                for allergy in medical_history.allergies)
                if has_allergy:
                    recommendation.contraindications.append("患者过敏史")
                    continue
            
            # 检查药物相互作用
            if medical_history.current_medications and recommendation.treatment_type == TreatmentType.MEDICATION:
                # 简化的药物相互作用检查
                interaction_risk = False
                for medication in medical_history.current_medications:
                    if "华法林" in medication and "阿司匹林" in recommendation.description:
                        recommendation.contraindications.append("与华法林存在相互作用风险")
                        interaction_risk = True
                
                if not interaction_risk:
                    safe_recommendations.append(recommendation)
            else:
                safe_recommendations.append(recommendation)
        
        return safe_recommendations
    
    def _determine_urgency(self, diagnosis: DiagnosisCandidate) -> UrgencyLevel:
        """确定治疗紧急程度"""
        if diagnosis.confidence > 0.8:
            if any(word in diagnosis.name for word in ["急性", "重症", "危急"]):
                return UrgencyLevel.CRITICAL
            elif any(word in diagnosis.name for word in ["感染", "炎症"]):
                return UrgencyLevel.URGENT
        
        return UrgencyLevel.ROUTINE
    
    def _get_contraindications(
        self,
        treatment: Dict[str, Any],
        medical_history: Optional[MedicalHistory] = None
    ) -> List[str]:
        """获取禁忌症"""
        contraindications = treatment.get("contraindications", [])
        
        if medical_history:
            # 基于病史添加禁忌症
            if "肾病" in medical_history.past_illnesses and "NSAID" in treatment.get("description", ""):
                contraindications.append("肾功能不全患者慎用")
        
        return contraindications
    
    def _get_tcm_contraindications(
        self,
        treatment: Dict[str, Any],
        medical_history: Optional[MedicalHistory] = None
    ) -> List[str]:
        """获取中医治疗禁忌症"""
        contraindications = []
        
        # 中药常见禁忌
        if "麻黄" in treatment.get("composition", []):
            contraindications.append("高血压患者慎用")
        
        if "附子" in treatment.get("composition", []):
            contraindications.append("孕妇禁用")
        
        return contraindications

class IntelligentDiagnosisAssistant:
    """智能诊断辅助引擎主类"""
    
    def __init__(self, config: Dict[str, Any], metrics_collector: Optional[MetricsCollector] = None):
        self.config = config
        self.metrics_collector = metrics_collector
        
        # 初始化各个组件
        self.symptom_analyzer = SymptomAnalyzer()
        self.disease_predictor = DiseasePredictor()
        self.tcm_engine = TCMDiagnosisEngine()
        self.treatment_engine = TreatmentRecommendationEngine()
        
        # 诊断会话存储
        self.active_sessions = {}
        
        logger.info("智能诊断辅助引擎初始化完成")
    
    async def initialize(self):
        """初始化引擎"""
        try:
            # 加载配置
            await self._load_configuration()
            
            # 初始化模型
            await self._initialize_models()
            
            logger.info("智能诊断辅助引擎初始化成功")
            
        except Exception as e:
            logger.error(f"智能诊断辅助引擎初始化失败: {e}")
            raise
    
    async def _load_configuration(self):
        """加载配置"""
        self.diagnosis_config = self.config.get("diagnosis", {})
        self.confidence_threshold = self.diagnosis_config.get("confidence_threshold", 0.3)
        self.max_diagnoses = self.diagnosis_config.get("max_diagnoses", 10)
        self.enable_tcm = self.diagnosis_config.get("enable_tcm", True)
        self.enable_ml_prediction = self.diagnosis_config.get("enable_ml_prediction", False)
    
    async def _initialize_models(self):
        """初始化预测模型"""
        if self.enable_ml_prediction:
            # 这里可以加载预训练的机器学习模型
            pass
    
    @trace_operation("diagnosis_assistant.start_session", SpanKind.INTERNAL)
    async def start_diagnosis_session(
        self,
        user_id: str,
        chief_complaint: str,
        session_id: Optional[str] = None
    ) -> str:
        """开始诊断会话"""
        try:
            if not session_id:
                session_id = f"diag_{user_id}_{int(datetime.now().timestamp())}"
            
            session = DiagnosisSession(
                id=session_id,
                user_id=user_id,
                chief_complaint=chief_complaint,
                symptoms=[],
                status="active"
            )
            
            self.active_sessions[session_id] = session
            
            if self.metrics_collector:
                self.metrics_collector.increment_counter(
                    "diagnosis_sessions_started",
                    {"user_id": user_id}
                )
            
            logger.info(f"诊断会话已开始: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"开始诊断会话失败: {e}")
            raise
    
    @trace_operation("diagnosis_assistant.add_symptoms", SpanKind.INTERNAL)
    async def add_symptoms(
        self,
        session_id: str,
        symptoms: List[Symptom]
    ) -> Dict[str, Any]:
        """添加症状"""
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"诊断会话不存在: {session_id}")
            
            session = self.active_sessions[session_id]
            session.symptoms.extend(symptoms)
            session.updated_at = datetime.now()
            
            # 实时症状分析
            symptom_analysis = await self.symptom_analyzer.analyze_symptoms(
                session.symptoms, session.user_id
            )
            
            return {
                "session_id": session_id,
                "symptom_count": len(session.symptoms),
                "analysis": symptom_analysis,
                "recommendations": self._get_next_steps(symptom_analysis)
            }
            
        except Exception as e:
            logger.error(f"添加症状失败: {e}")
            raise
    
    @trace_operation("diagnosis_assistant.perform_diagnosis", SpanKind.INTERNAL)
    async def perform_comprehensive_diagnosis(
        self,
        session_id: str,
        medical_history: Optional[MedicalHistory] = None,
        physical_examination: Optional[PhysicalExamination] = None,
        laboratory_results: Optional[List[LaboratoryResult]] = None,
        tongue_manifestation: Optional[str] = None,
        pulse_manifestation: Optional[str] = None
    ) -> DiagnosisResult:
        """执行综合诊断"""
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"诊断会话不存在: {session_id}")
            
            session = self.active_sessions[session_id]
            
            # 更新会话信息
            if medical_history:
                session.medical_history = medical_history
            if physical_examination:
                session.physical_examination = physical_examination
            if laboratory_results:
                session.laboratory_results = laboratory_results
            
            # 症状分析
            symptom_analysis = await self.symptom_analyzer.analyze_symptoms(
                session.symptoms, session.user_id
            )
            
            # 疾病预测
            disease_predictions = await self.disease_predictor.predict_diseases(
                session.symptoms, medical_history, session.user_id
            )
            
            # 中医辨证（如果启用）
            tcm_syndromes = []
            if self.enable_tcm:
                tcm_syndromes = await self.tcm_engine.diagnose_tcm_syndrome(
                    session.symptoms, tongue_manifestation, pulse_manifestation, session.user_id
                )
            
            # 筛选高置信度诊断
            primary_diagnoses = [d for d in disease_predictions if d.confidence >= self.confidence_threshold]
            differential_diagnoses = [d for d in disease_predictions if d.confidence < self.confidence_threshold]
            
            # 生成治疗建议
            treatment_recommendations = await self.treatment_engine.generate_treatment_recommendations(
                primary_diagnoses, tcm_syndromes, medical_history, session.user_id
            )
            
            # 生成随访建议
            follow_up_recommendations = self._generate_follow_up_recommendations(
                primary_diagnoses, symptom_analysis
            )
            
            # 识别红旗症状
            red_flags = symptom_analysis.get("red_flags", [])
            
            # 计算整体置信度
            overall_confidence = self._calculate_overall_confidence(
                primary_diagnoses, tcm_syndromes, symptom_analysis
            )
            
            # 生成诊断推理
            reasoning = self._generate_diagnostic_reasoning(
                symptom_analysis, primary_diagnoses, tcm_syndromes
            )
            
            # 创建诊断结果
            diagnosis_result = DiagnosisResult(
                user_id=session.user_id,
                session_id=session_id,
                primary_diagnoses=primary_diagnoses[:self.max_diagnoses],
                differential_diagnoses=differential_diagnoses[:5],
                tcm_syndromes=tcm_syndromes[:5],
                treatment_recommendations=treatment_recommendations,
                follow_up_recommendations=follow_up_recommendations,
                red_flags=red_flags,
                overall_confidence=overall_confidence,
                reasoning=reasoning
            )
            
            # 更新会话
            session.diagnosis_result = diagnosis_result
            session.status = "completed"
            session.updated_at = datetime.now()
            
            # 记录指标
            if self.metrics_collector:
                self.metrics_collector.increment_counter(
                    "diagnoses_completed",
                    {"user_id": session.user_id, "confidence_level": self._get_confidence_category(overall_confidence)}
                )
                
                self.metrics_collector.record_histogram(
                    "diagnosis_confidence",
                    overall_confidence,
                    {"user_id": session.user_id}
                )
            
            logger.info(f"诊断完成: {session_id}, 置信度: {overall_confidence:.2f}")
            return diagnosis_result
            
        except Exception as e:
            logger.error(f"执行诊断失败: {e}")
            raise
    
    async def get_diagnosis_session(self, session_id: str) -> Optional[DiagnosisSession]:
        """获取诊断会话"""
        return self.active_sessions.get(session_id)
    
    async def get_user_diagnosis_history(self, user_id: str) -> List[DiagnosisSession]:
        """获取用户诊断历史"""
        user_sessions = [
            session for session in self.active_sessions.values()
            if session.user_id == user_id
        ]
        return sorted(user_sessions, key=lambda x: x.created_at, reverse=True)
    
    def _get_next_steps(self, symptom_analysis: Dict[str, Any]) -> List[str]:
        """获取下一步建议"""
        recommendations = []
        
        if symptom_analysis.get("red_flags"):
            recommendations.append("建议立即就医")
        
        urgency = symptom_analysis.get("overall_urgency", UrgencyLevel.ROUTINE)
        if urgency == UrgencyLevel.CRITICAL:
            recommendations.append("紧急就医")
        elif urgency == UrgencyLevel.EMERGENT:
            recommendations.append("尽快就医")
        
        if symptom_analysis.get("cluster_analysis", {}).get("primary_system"):
            system = symptom_analysis["cluster_analysis"]["primary_system"]
            recommendations.append(f"建议{system}专科检查")
        
        return recommendations
    
    def _generate_follow_up_recommendations(
        self,
        diagnoses: List[DiagnosisCandidate],
        symptom_analysis: Dict[str, Any]
    ) -> List[str]:
        """生成随访建议"""
        recommendations = []
        
        # 基于诊断的随访建议
        for diagnosis in diagnoses:
            if diagnosis.confidence > 0.7:
                if "慢性" in diagnosis.name:
                    recommendations.append(f"定期随访{diagnosis.name}，建议3-6个月复查")
                elif "急性" in diagnosis.name:
                    recommendations.append(f"症状缓解后1-2周复查")
        
        # 基于症状的随访建议
        if symptom_analysis.get("red_flags"):
            recommendations.append("密切观察症状变化，如有恶化立即就医")
        
        return list(set(recommendations))  # 去重
    
    def _calculate_overall_confidence(
        self,
        diagnoses: List[DiagnosisCandidate],
        tcm_syndromes: List[TCMSyndrome],
        symptom_analysis: Dict[str, Any]
    ) -> float:
        """计算整体诊断置信度"""
        if not diagnoses and not tcm_syndromes:
            return 0.0
        
        # 西医诊断置信度
        western_confidence = max([d.confidence for d in diagnoses], default=0.0)
        
        # 中医诊断置信度
        tcm_confidence = max([s.confidence for s in tcm_syndromes], default=0.0)
        
        # 症状分析置信度
        symptom_confidence = min(symptom_analysis.get("severity_analysis", {}).get("total_score", 0) / 10, 1.0)
        
        # 综合置信度
        overall_confidence = (western_confidence * 0.5 + tcm_confidence * 0.3 + symptom_confidence * 0.2)
        
        return min(overall_confidence, 1.0)
    
    def _generate_diagnostic_reasoning(
        self,
        symptom_analysis: Dict[str, Any],
        diagnoses: List[DiagnosisCandidate],
        tcm_syndromes: List[TCMSyndrome]
    ) -> str:
        """生成诊断推理"""
        reasoning_parts = []
        
        # 症状分析部分
        severity = symptom_analysis.get("severity_analysis", {})
        if severity.get("critical_symptoms"):
            reasoning_parts.append(f"患者存在危急症状：{', '.join(severity['critical_symptoms'])}")
        
        cluster_analysis = symptom_analysis.get("cluster_analysis", {})
        if cluster_analysis.get("primary_system"):
            reasoning_parts.append(f"症状主要涉及{cluster_analysis['primary_system']}")
        
        # 西医诊断推理
        if diagnoses:
            top_diagnosis = diagnoses[0]
            reasoning_parts.append(
                f"基于症状分析，最可能的诊断是{top_diagnosis.name}（置信度：{top_diagnosis.confidence:.1%}）"
            )
            if top_diagnosis.supporting_evidence:
                reasoning_parts.append(f"支持证据：{', '.join(top_diagnosis.supporting_evidence)}")
        
        # 中医诊断推理
        if tcm_syndromes:
            top_syndrome = tcm_syndromes[0]
            reasoning_parts.append(
                f"中医辨证为{top_syndrome.name}（置信度：{top_syndrome.confidence:.1%}）"
            )
            if top_syndrome.pathogenesis:
                reasoning_parts.append(f"病机：{top_syndrome.pathogenesis}")
        
        return "；".join(reasoning_parts)
    
    def _get_confidence_category(self, confidence: float) -> str:
        """获取置信度分类"""
        if confidence >= 0.8:
            return "high"
        elif confidence >= 0.6:
            return "medium"
        elif confidence >= 0.4:
            return "low"
        else:
            return "very_low"
    
    async def get_diagnosis_statistics(self) -> Dict[str, Any]:
        """获取诊断统计信息"""
        try:
            total_sessions = len(self.active_sessions)
            completed_sessions = len([s for s in self.active_sessions.values() if s.status == "completed"])
            
            # 置信度分布
            confidence_distribution = {"high": 0, "medium": 0, "low": 0, "very_low": 0}
            for session in self.active_sessions.values():
                if session.diagnosis_result:
                    category = self._get_confidence_category(session.diagnosis_result.overall_confidence)
                    confidence_distribution[category] += 1
            
            # 常见诊断
            diagnosis_counts = {}
            for session in self.active_sessions.values():
                if session.diagnosis_result:
                    for diagnosis in session.diagnosis_result.primary_diagnoses:
                        diagnosis_counts[diagnosis.name] = diagnosis_counts.get(diagnosis.name, 0) + 1
            
            top_diagnoses = sorted(diagnosis_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                "total_sessions": total_sessions,
                "completed_sessions": completed_sessions,
                "completion_rate": completed_sessions / total_sessions if total_sessions > 0 else 0,
                "confidence_distribution": confidence_distribution,
                "top_diagnoses": top_diagnoses,
                "average_symptoms_per_session": np.mean([len(s.symptoms) for s in self.active_sessions.values()]) if self.active_sessions else 0
            }
            
        except Exception as e:
            logger.error(f"获取诊断统计失败: {e}")
            return {}

def initialize_diagnosis_assistant(
    config: Dict[str, Any],
    metrics_collector: Optional[MetricsCollector] = None
) -> IntelligentDiagnosisAssistant:
    """初始化智能诊断辅助引擎"""
    assistant = IntelligentDiagnosisAssistant(config, metrics_collector)
    return assistant

# 全局实例
_diagnosis_assistant: Optional[IntelligentDiagnosisAssistant] = None

def get_diagnosis_assistant() -> Optional[IntelligentDiagnosisAssistant]:
    """获取智能诊断辅助引擎实例"""
    return _diagnosis_assistant 