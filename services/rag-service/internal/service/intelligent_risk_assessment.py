#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能风险评估引擎 - 提供健康风险评估、疾病预测、风险分层、预防建议
"""

import time
from typing import Dict, List, Any, Optional, Tuple, Union, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from loguru import logger
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.calibration import CalibratedClassifierCV
import warnings
warnings.filterwarnings('ignore')

from ..observability.metrics import MetricsCollector
from ..observability.tracing import trace_operation, SpanKind

class RiskLevel(str, Enum):
    """风险级别"""
    VERY_LOW = "very_low"       # 极低风险
    LOW = "low"                 # 低风险
    MODERATE = "moderate"       # 中等风险
    HIGH = "high"               # 高风险
    VERY_HIGH = "very_high"     # 极高风险
    CRITICAL = "critical"       # 危急风险

class RiskCategory(str, Enum):
    """风险类别"""
    CARDIOVASCULAR = "cardiovascular"           # 心血管疾病
    DIABETES = "diabetes"                       # 糖尿病
    HYPERTENSION = "hypertension"               # 高血压
    STROKE = "stroke"                           # 中风
    CANCER = "cancer"                           # 癌症
    RESPIRATORY = "respiratory"                 # 呼吸系统疾病
    KIDNEY_DISEASE = "kidney_disease"           # 肾脏疾病
    LIVER_DISEASE = "liver_disease"             # 肝脏疾病
    MENTAL_HEALTH = "mental_health"             # 心理健康
    METABOLIC_SYNDROME = "metabolic_syndrome"   # 代谢综合征
    OSTEOPOROSIS = "osteoporosis"               # 骨质疏松
    INFECTIOUS_DISEASE = "infectious_disease"   # 感染性疾病

class RiskTimeframe(str, Enum):
    """风险时间框架"""
    SHORT_TERM = "short_term"       # 短期（1-6个月）
    MEDIUM_TERM = "medium_term"     # 中期（6个月-2年）
    LONG_TERM = "long_term"         # 长期（2-10年）
    LIFETIME = "lifetime"           # 终生

class RiskFactorType(str, Enum):
    """风险因子类型"""
    MODIFIABLE = "modifiable"           # 可改变的
    NON_MODIFIABLE = "non_modifiable"   # 不可改变的
    BEHAVIORAL = "behavioral"           # 行为因素
    ENVIRONMENTAL = "environmental"     # 环境因素
    GENETIC = "genetic"                 # 遗传因素
    CLINICAL = "clinical"               # 临床因素

class InterventionType(str, Enum):
    """干预类型"""
    LIFESTYLE = "lifestyle"             # 生活方式
    MEDICATION = "medication"           # 药物治疗
    SCREENING = "screening"             # 筛查
    MONITORING = "monitoring"           # 监测
    EDUCATION = "education"             # 健康教育
    SURGERY = "surgery"                 # 手术治疗

@dataclass
class RiskFactor:
    """风险因子"""
    id: str
    name: str
    category: RiskCategory
    factor_type: RiskFactorType
    value: Union[float, str, bool]
    weight: float                               # 权重
    confidence: float = 1.0                     # 置信度
    source: str = "user_input"                  # 数据来源
    last_updated: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RiskScore:
    """风险评分"""
    category: RiskCategory
    timeframe: RiskTimeframe
    score: float                                # 风险评分 (0-1)
    level: RiskLevel
    confidence: float                           # 置信度
    contributing_factors: List[str]             # 主要贡献因子
    protective_factors: List[str]               # 保护因子
    calculated_at: datetime = field(default_factory=datetime.now)
    model_version: str = "1.0"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RiskPrediction:
    """风险预测"""
    user_id: str
    category: RiskCategory
    timeframe: RiskTimeframe
    probability: float                          # 发病概率
    risk_level: RiskLevel
    confidence_interval: Tuple[float, float]    # 置信区间
    key_risk_factors: List[RiskFactor]
    risk_trajectory: List[Tuple[datetime, float]]  # 风险轨迹
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PreventionRecommendation:
    """预防建议"""
    id: str
    risk_category: RiskCategory
    intervention_type: InterventionType
    title: str
    description: str
    priority: int                               # 优先级 (1-10)
    effectiveness: float                        # 有效性 (0-1)
    feasibility: float                          # 可行性 (0-1)
    cost_effectiveness: float                   # 成本效益 (0-1)
    target_risk_factors: List[str]
    expected_risk_reduction: float              # 预期风险降低
    implementation_timeline: str
    monitoring_metrics: List[str]
    contraindications: List[str] = field(default_factory=list)
    side_effects: List[str] = field(default_factory=list)
    evidence_level: str = "moderate"            # 证据级别
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class RiskAssessmentProfile:
    """风险评估档案"""
    user_id: str
    demographics: Dict[str, Any]                # 人口统计学信息
    medical_history: Dict[str, Any]             # 病史
    family_history: Dict[str, Any]              # 家族史
    lifestyle_factors: Dict[str, Any]           # 生活方式因素
    clinical_measurements: Dict[str, Any]       # 临床测量
    genetic_markers: Dict[str, Any]             # 遗传标记
    environmental_factors: Dict[str, Any]       # 环境因素
    risk_preferences: Dict[str, Any]            # 风险偏好
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

class RiskCalculator:
    """风险计算器"""
    
    def __init__(self):
        self.risk_models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_importance = {}
        
        # 风险评分权重
        self.risk_weights = {
            RiskCategory.CARDIOVASCULAR: {
                "age": 0.15,
                "gender": 0.05,
                "smoking": 0.20,
                "blood_pressure": 0.15,
                "cholesterol": 0.15,
                "diabetes": 0.10,
                "family_history": 0.10,
                "bmi": 0.10
            },
            RiskCategory.DIABETES: {
                "age": 0.10,
                "bmi": 0.25,
                "family_history": 0.20,
                "blood_glucose": 0.20,
                "physical_activity": 0.15,
                "diet": 0.10
            },
            RiskCategory.HYPERTENSION: {
                "age": 0.15,
                "bmi": 0.20,
                "sodium_intake": 0.15,
                "alcohol": 0.10,
                "stress": 0.10,
                "family_history": 0.15,
                "physical_activity": 0.15
            }
        }
        
        # 风险阈值
        self.risk_thresholds = {
            RiskLevel.VERY_LOW: (0.0, 0.1),
            RiskLevel.LOW: (0.1, 0.25),
            RiskLevel.MODERATE: (0.25, 0.5),
            RiskLevel.HIGH: (0.5, 0.75),
            RiskLevel.VERY_HIGH: (0.75, 0.9),
            RiskLevel.CRITICAL: (0.9, 1.0)
        }
    
    async def calculate_risk_score(
        self,
        risk_factors: List[RiskFactor],
        category: RiskCategory,
        timeframe: RiskTimeframe
    ) -> RiskScore:
        """计算风险评分"""
        try:
            # 获取该类别的权重
            weights = self.risk_weights.get(category, {})
            
            total_score = 0.0
            total_weight = 0.0
            contributing_factors = []
            protective_factors = []
            
            for factor in risk_factors:
                if factor.category != category:
                    continue
                
                factor_weight = weights.get(factor.name, 0.1)  # 默认权重
                
                # 标准化因子值
                normalized_value = await self._normalize_factor_value(factor)
                
                # 计算加权分数
                weighted_score = normalized_value * factor_weight * factor.confidence
                total_score += weighted_score
                total_weight += factor_weight
                
                # 识别主要贡献因子和保护因子
                if normalized_value > 0.6:
                    contributing_factors.append(factor.name)
                elif normalized_value < 0.3:
                    protective_factors.append(factor.name)
            
            # 标准化总分
            if total_weight > 0:
                final_score = min(total_score / total_weight, 1.0)
            else:
                final_score = 0.0
            
            # 根据时间框架调整分数
            final_score = await self._adjust_score_for_timeframe(final_score, timeframe)
            
            # 确定风险级别
            risk_level = self._determine_risk_level(final_score)
            
            # 计算置信度
            confidence = self._calculate_confidence(risk_factors, category)
            
            return RiskScore(
                category=category,
                timeframe=timeframe,
                score=final_score,
                level=risk_level,
                confidence=confidence,
                contributing_factors=contributing_factors,
                protective_factors=protective_factors
            )
            
        except Exception as e:
            logger.error(f"计算风险评分失败: {e}")
            return RiskScore(
                category=category,
                timeframe=timeframe,
                score=0.0,
                level=RiskLevel.LOW,
                confidence=0.0,
                contributing_factors=[],
                protective_factors=[]
            )
    
    async def _normalize_factor_value(self, factor: RiskFactor) -> float:
        """标准化因子值"""
        try:
            if isinstance(factor.value, bool):
                return 1.0 if factor.value else 0.0
            
            if isinstance(factor.value, str):
                # 处理分类变量
                category_mappings = {
                    "smoking": {"never": 0.0, "former": 0.3, "current": 1.0},
                    "alcohol": {"none": 0.0, "moderate": 0.3, "heavy": 1.0},
                    "exercise": {"high": 0.0, "moderate": 0.3, "low": 0.7, "none": 1.0}
                }
                
                mapping = category_mappings.get(factor.name, {})
                return mapping.get(factor.value.lower(), 0.5)
            
            if isinstance(factor.value, (int, float)):
                # 处理数值变量
                value_ranges = {
                    "age": (0, 100),
                    "bmi": (15, 50),
                    "blood_pressure_systolic": (80, 200),
                    "blood_pressure_diastolic": (50, 120),
                    "cholesterol": (100, 400),
                    "blood_glucose": (3, 20)
                }
                
                if factor.name in value_ranges:
                    min_val, max_val = value_ranges[factor.name]
                    normalized = (factor.value - min_val) / (max_val - min_val)
                    return max(0.0, min(1.0, normalized))
                
                # 默认标准化
                return min(factor.value / 100.0, 1.0)
            
            return 0.5  # 默认值
            
        except Exception as e:
            logger.error(f"标准化因子值失败: {e}")
            return 0.5
    
    async def _adjust_score_for_timeframe(self, score: float, timeframe: RiskTimeframe) -> float:
        """根据时间框架调整分数"""
        adjustments = {
            RiskTimeframe.SHORT_TERM: 0.8,     # 短期风险通常较低
            RiskTimeframe.MEDIUM_TERM: 1.0,    # 基准
            RiskTimeframe.LONG_TERM: 1.2,      # 长期风险累积
            RiskTimeframe.LIFETIME: 1.5        # 终生风险最高
        }
        
        adjustment = adjustments.get(timeframe, 1.0)
        return min(score * adjustment, 1.0)
    
    def _determine_risk_level(self, score: float) -> RiskLevel:
        """确定风险级别"""
        for level, (min_score, max_score) in self.risk_thresholds.items():
            if min_score <= score < max_score:
                return level
        return RiskLevel.CRITICAL
    
    def _calculate_confidence(self, risk_factors: List[RiskFactor], category: RiskCategory) -> float:
        """计算置信度"""
        if not risk_factors:
            return 0.0
        
        # 基于因子数量和质量计算置信度
        factor_confidences = [f.confidence for f in risk_factors if f.category == category]
        
        if not factor_confidences:
            return 0.0
        
        # 平均置信度
        avg_confidence = np.mean(factor_confidences)
        
        # 根据因子数量调整
        factor_count = len(factor_confidences)
        count_factor = min(factor_count / 10.0, 1.0)  # 10个因子为满分
        
        return avg_confidence * count_factor

class PredictiveModel:
    """预测模型"""
    
    def __init__(self):
        self.models = {}
        self.model_metadata = {}
        self.training_data = {}
        
    async def train_model(
        self,
        category: RiskCategory,
        training_data: pd.DataFrame,
        target_column: str
    ) -> Dict[str, Any]:
        """训练预测模型"""
        try:
            logger.info(f"开始训练 {category.value} 风险预测模型")
            
            # 数据预处理
            X, y = await self._preprocess_training_data(training_data, target_column)
            
            if len(X) < 100:  # 数据不足
                logger.warning(f"训练数据不足: {len(X)} 样本")
                return {"status": "insufficient_data", "samples": len(X)}
            
            # 分割训练和测试数据
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # 训练多个模型
            models = {
                "random_forest": RandomForestClassifier(n_estimators=100, random_state=42),
                "gradient_boosting": GradientBoostingClassifier(random_state=42),
                "logistic_regression": LogisticRegression(random_state=42)
            }
            
            best_model = None
            best_score = 0.0
            model_results = {}
            
            for model_name, model in models.items():
                try:
                    # 训练模型
                    model.fit(X_train, y_train)
                    
                    # 评估模型
                    y_pred = model.predict(X_test)
                    y_pred_proba = model.predict_proba(X_test)[:, 1]
                    
                    # 计算评估指标
                    accuracy = accuracy_score(y_test, y_pred)
                    precision = precision_score(y_test, y_pred, average='weighted')
                    recall = recall_score(y_test, y_pred, average='weighted')
                    f1 = f1_score(y_test, y_pred, average='weighted')
                    auc = roc_auc_score(y_test, y_pred_proba)
                    
                    # 交叉验证
                    cv_scores = cross_val_score(model, X_train, y_train, cv=5)
                    cv_mean = cv_scores.mean()
                    
                    model_results[model_name] = {
                        "accuracy": accuracy,
                        "precision": precision,
                        "recall": recall,
                        "f1_score": f1,
                        "auc": auc,
                        "cv_score": cv_mean,
                        "cv_std": cv_scores.std()
                    }
                    
                    # 选择最佳模型（基于AUC）
                    if auc > best_score:
                        best_score = auc
                        best_model = model
                        
                    logger.info(f"{model_name} - AUC: {auc:.3f}, F1: {f1:.3f}")
                    
                except Exception as e:
                    logger.error(f"训练模型 {model_name} 失败: {e}")
                    continue
            
            if best_model is None:
                return {"status": "training_failed", "error": "所有模型训练失败"}
            
            # 校准最佳模型
            calibrated_model = CalibratedClassifierCV(best_model, cv=3)
            calibrated_model.fit(X_train, y_train)
            
            # 保存模型
            model_key = f"{category.value}_risk_model"
            self.models[model_key] = calibrated_model
            
            # 保存模型元数据
            self.model_metadata[model_key] = {
                "category": category.value,
                "training_samples": len(X_train),
                "test_samples": len(X_test),
                "features": list(X.columns),
                "best_model_type": type(best_model).__name__,
                "performance": model_results,
                "best_auc": best_score,
                "trained_at": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            # 特征重要性
            if hasattr(best_model, 'feature_importances_'):
                feature_importance = dict(zip(X.columns, best_model.feature_importances_))
                self.model_metadata[model_key]["feature_importance"] = feature_importance
            
            logger.info(f"模型训练完成: {category.value}, 最佳AUC: {best_score:.3f}")
            
            return {
                "status": "success",
                "model_key": model_key,
                "best_auc": best_score,
                "training_samples": len(X_train),
                "model_results": model_results
            }
            
        except Exception as e:
            logger.error(f"训练预测模型失败: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _preprocess_training_data(
        self,
        data: pd.DataFrame,
        target_column: str
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """预处理训练数据"""
        try:
            # 分离特征和目标
            y = data[target_column]
            X = data.drop(columns=[target_column])
            
            # 处理缺失值
            X = X.fillna(X.median() if X.select_dtypes(include=[np.number]).shape[1] > 0 else X.mode().iloc[0])
            
            # 编码分类变量
            categorical_columns = X.select_dtypes(include=['object']).columns
            for col in categorical_columns:
                le = LabelEncoder()
                X[col] = le.fit_transform(X[col].astype(str))
            
            # 标准化数值变量
            numerical_columns = X.select_dtypes(include=[np.number]).columns
            if len(numerical_columns) > 0:
                scaler = StandardScaler()
                X[numerical_columns] = scaler.fit_transform(X[numerical_columns])
            
            return X, y
            
        except Exception as e:
            logger.error(f"预处理训练数据失败: {e}")
            raise
    
    async def predict_risk(
        self,
        user_profile: RiskAssessmentProfile,
        category: RiskCategory,
        timeframe: RiskTimeframe
    ) -> Optional[RiskPrediction]:
        """预测风险"""
        try:
            model_key = f"{category.value}_risk_model"
            
            if model_key not in self.models:
                logger.warning(f"未找到模型: {model_key}")
                return None
            
            model = self.models[model_key]
            
            # 准备特征数据
            features = await self._prepare_features(user_profile, category)
            
            if features is None:
                return None
            
            # 预测概率
            probability = model.predict_proba(features.reshape(1, -1))[0, 1]
            
            # 根据时间框架调整概率
            adjusted_probability = await self._adjust_probability_for_timeframe(
                probability, timeframe
            )
            
            # 确定风险级别
            risk_level = self._determine_risk_level_from_probability(adjusted_probability)
            
            # 计算置信区间
            confidence_interval = await self._calculate_confidence_interval(
                model, features, probability
            )
            
            # 识别关键风险因子
            key_risk_factors = await self._identify_key_risk_factors(
                user_profile, category, model
            )
            
            # 生成风险轨迹
            risk_trajectory = await self._generate_risk_trajectory(
                user_profile, category, timeframe
            )
            
            # 设置过期时间
            expires_at = datetime.now() + timedelta(days=90)  # 3个月有效期
            
            return RiskPrediction(
                user_id=user_profile.user_id,
                category=category,
                timeframe=timeframe,
                probability=adjusted_probability,
                risk_level=risk_level,
                confidence_interval=confidence_interval,
                key_risk_factors=key_risk_factors,
                risk_trajectory=risk_trajectory,
                expires_at=expires_at
            )
            
        except Exception as e:
            logger.error(f"预测风险失败: {e}")
            return None
    
    async def _prepare_features(
        self,
        profile: RiskAssessmentProfile,
        category: RiskCategory
    ) -> Optional[np.ndarray]:
        """准备特征数据"""
        try:
            # 根据类别选择相关特征
            feature_mappings = {
                RiskCategory.CARDIOVASCULAR: [
                    "age", "gender", "smoking", "blood_pressure_systolic",
                    "cholesterol", "diabetes", "family_history_cvd", "bmi"
                ],
                RiskCategory.DIABETES: [
                    "age", "bmi", "family_history_diabetes", "blood_glucose",
                    "physical_activity", "diet_quality"
                ],
                RiskCategory.HYPERTENSION: [
                    "age", "bmi", "sodium_intake", "alcohol", "stress_level",
                    "family_history_hypertension", "physical_activity"
                ]
            }
            
            required_features = feature_mappings.get(category, [])
            
            if not required_features:
                return None
            
            # 提取特征值
            feature_values = []
            
            for feature in required_features:
                value = await self._extract_feature_value(profile, feature)
                feature_values.append(value)
            
            return np.array(feature_values)
            
        except Exception as e:
            logger.error(f"准备特征数据失败: {e}")
            return None
    
    async def _extract_feature_value(
        self,
        profile: RiskAssessmentProfile,
        feature_name: str
    ) -> float:
        """提取特征值"""
        try:
            # 从不同数据源提取特征
            if feature_name == "age":
                birth_date = profile.demographics.get("birth_date")
                if birth_date:
                    age = (datetime.now() - datetime.fromisoformat(birth_date)).days / 365.25
                    return min(age, 100)
                return 50  # 默认年龄
            
            elif feature_name == "gender":
                gender = profile.demographics.get("gender", "unknown")
                return 1.0 if gender.lower() == "male" else 0.0
            
            elif feature_name == "bmi":
                return profile.clinical_measurements.get("bmi", 25.0)
            
            elif feature_name == "smoking":
                smoking_status = profile.lifestyle_factors.get("smoking", "never")
                mapping = {"never": 0.0, "former": 0.5, "current": 1.0}
                return mapping.get(smoking_status, 0.0)
            
            elif feature_name.startswith("blood_pressure"):
                bp_type = feature_name.split("_")[-1]  # systolic or diastolic
                return profile.clinical_measurements.get(f"blood_pressure_{bp_type}", 120.0)
            
            elif feature_name == "cholesterol":
                return profile.clinical_measurements.get("total_cholesterol", 200.0)
            
            elif feature_name == "blood_glucose":
                return profile.clinical_measurements.get("fasting_glucose", 5.5)
            
            elif feature_name.startswith("family_history"):
                condition = feature_name.split("_")[-1]
                return 1.0 if profile.family_history.get(condition, False) else 0.0
            
            elif feature_name == "physical_activity":
                activity_level = profile.lifestyle_factors.get("exercise_frequency", "moderate")
                mapping = {"none": 0.0, "low": 0.25, "moderate": 0.5, "high": 1.0}
                return mapping.get(activity_level, 0.5)
            
            elif feature_name == "diet_quality":
                diet_score = profile.lifestyle_factors.get("diet_quality_score", 5)
                return diet_score / 10.0  # 标准化到0-1
            
            elif feature_name == "sodium_intake":
                return profile.lifestyle_factors.get("sodium_intake_mg", 2300) / 5000.0  # 标准化
            
            elif feature_name == "alcohol":
                alcohol_consumption = profile.lifestyle_factors.get("alcohol_consumption", "moderate")
                mapping = {"none": 0.0, "light": 0.25, "moderate": 0.5, "heavy": 1.0}
                return mapping.get(alcohol_consumption, 0.5)
            
            elif feature_name == "stress_level":
                return profile.lifestyle_factors.get("stress_level", 5) / 10.0
            
            else:
                return 0.5  # 默认值
                
        except Exception as e:
            logger.error(f"提取特征值失败 {feature_name}: {e}")
            return 0.5
    
    async def _adjust_probability_for_timeframe(
        self,
        probability: float,
        timeframe: RiskTimeframe
    ) -> float:
        """根据时间框架调整概率"""
        adjustments = {
            RiskTimeframe.SHORT_TERM: 0.3,
            RiskTimeframe.MEDIUM_TERM: 0.7,
            RiskTimeframe.LONG_TERM: 1.0,
            RiskTimeframe.LIFETIME: 1.5
        }
        
        adjustment = adjustments.get(timeframe, 1.0)
        return min(probability * adjustment, 1.0)
    
    def _determine_risk_level_from_probability(self, probability: float) -> RiskLevel:
        """根据概率确定风险级别"""
        if probability < 0.1:
            return RiskLevel.VERY_LOW
        elif probability < 0.25:
            return RiskLevel.LOW
        elif probability < 0.5:
            return RiskLevel.MODERATE
        elif probability < 0.75:
            return RiskLevel.HIGH
        elif probability < 0.9:
            return RiskLevel.VERY_HIGH
        else:
            return RiskLevel.CRITICAL
    
    async def _calculate_confidence_interval(
        self,
        model,
        features: np.ndarray,
        probability: float
    ) -> Tuple[float, float]:
        """计算置信区间"""
        try:
            # 简化的置信区间计算
            # 在实际应用中，可以使用bootstrap或其他方法
            margin = 0.1  # 10%的边际
            lower = max(0.0, probability - margin)
            upper = min(1.0, probability + margin)
            return (lower, upper)
            
        except Exception as e:
            logger.error(f"计算置信区间失败: {e}")
            return (probability * 0.8, probability * 1.2)
    
    async def _identify_key_risk_factors(
        self,
        profile: RiskAssessmentProfile,
        category: RiskCategory,
        model
    ) -> List[RiskFactor]:
        """识别关键风险因子"""
        try:
            key_factors = []
            
            # 基于模型特征重要性和用户数据识别关键因子
            model_key = f"{category.value}_risk_model"
            metadata = self.model_metadata.get(model_key, {})
            feature_importance = metadata.get("feature_importance", {})
            
            # 选择重要性最高的因子
            sorted_features = sorted(
                feature_importance.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]  # 取前5个
            
            for feature_name, importance in sorted_features:
                value = await self._extract_feature_value(profile, feature_name)
                
                risk_factor = RiskFactor(
                    id=f"{profile.user_id}_{feature_name}",
                    name=feature_name,
                    category=category,
                    factor_type=RiskFactorType.CLINICAL,
                    value=value,
                    weight=importance,
                    confidence=0.8
                )
                key_factors.append(risk_factor)
            
            return key_factors
            
        except Exception as e:
            logger.error(f"识别关键风险因子失败: {e}")
            return []
    
    async def _generate_risk_trajectory(
        self,
        profile: RiskAssessmentProfile,
        category: RiskCategory,
        timeframe: RiskTimeframe
    ) -> List[Tuple[datetime, float]]:
        """生成风险轨迹"""
        try:
            trajectory = []
            current_time = datetime.now()
            
            # 根据时间框架确定预测点
            if timeframe == RiskTimeframe.SHORT_TERM:
                time_points = [1, 3, 6]  # 月
                time_unit = "months"
            elif timeframe == RiskTimeframe.MEDIUM_TERM:
                time_points = [6, 12, 18, 24]  # 月
                time_unit = "months"
            elif timeframe == RiskTimeframe.LONG_TERM:
                time_points = [1, 3, 5, 7, 10]  # 年
                time_unit = "years"
            else:  # LIFETIME
                time_points = [10, 20, 30, 40, 50]  # 年
                time_unit = "years"
            
            # 基础风险（当前）
            base_risk = 0.1  # 简化处理
            
            for point in time_points:
                if time_unit == "months":
                    future_time = current_time + timedelta(days=point * 30)
                    risk_increase = point * 0.02  # 每月增加2%
                else:  # years
                    future_time = current_time + timedelta(days=point * 365)
                    risk_increase = point * 0.05  # 每年增加5%
                
                future_risk = min(base_risk + risk_increase, 1.0)
                trajectory.append((future_time, future_risk))
            
            return trajectory
            
        except Exception as e:
            logger.error(f"生成风险轨迹失败: {e}")
            return []

class PreventionEngine:
    """预防引擎"""
    
    def __init__(self):
        self.recommendation_database = {}
        self._initialize_recommendations()
    
    def _initialize_recommendations(self):
        """初始化预防建议数据库"""
        self.recommendation_database = {
            RiskCategory.CARDIOVASCULAR: [
                PreventionRecommendation(
                    id="cvd_exercise",
                    risk_category=RiskCategory.CARDIOVASCULAR,
                    intervention_type=InterventionType.LIFESTYLE,
                    title="增加有氧运动",
                    description="每周至少150分钟中等强度有氧运动，如快走、游泳、骑车",
                    priority=9,
                    effectiveness=0.8,
                    feasibility=0.7,
                    cost_effectiveness=0.9,
                    target_risk_factors=["physical_inactivity", "obesity", "hypertension"],
                    expected_risk_reduction=0.3,
                    implementation_timeline="立即开始，4-6周见效",
                    monitoring_metrics=["heart_rate", "blood_pressure", "weight"]
                ),
                PreventionRecommendation(
                    id="cvd_diet",
                    risk_category=RiskCategory.CARDIOVASCULAR,
                    intervention_type=InterventionType.LIFESTYLE,
                    title="采用地中海饮食",
                    description="增加蔬菜、水果、全谷物、鱼类摄入，减少饱和脂肪",
                    priority=8,
                    effectiveness=0.7,
                    feasibility=0.6,
                    cost_effectiveness=0.8,
                    target_risk_factors=["high_cholesterol", "inflammation", "obesity"],
                    expected_risk_reduction=0.25,
                    implementation_timeline="逐步调整，2-3个月完全适应",
                    monitoring_metrics=["cholesterol", "weight", "blood_pressure"]
                ),
                PreventionRecommendation(
                    id="cvd_smoking_cessation",
                    risk_category=RiskCategory.CARDIOVASCULAR,
                    intervention_type=InterventionType.LIFESTYLE,
                    title="戒烟",
                    description="完全停止吸烟，避免二手烟暴露",
                    priority=10,
                    effectiveness=0.9,
                    feasibility=0.4,
                    cost_effectiveness=1.0,
                    target_risk_factors=["smoking"],
                    expected_risk_reduction=0.5,
                    implementation_timeline="立即开始，1年内完全戒除",
                    monitoring_metrics=["lung_function", "blood_pressure", "heart_rate"]
                )
            ],
            RiskCategory.DIABETES: [
                PreventionRecommendation(
                    id="dm_weight_loss",
                    risk_category=RiskCategory.DIABETES,
                    intervention_type=InterventionType.LIFESTYLE,
                    title="减重",
                    description="通过饮食控制和运动，减少体重5-10%",
                    priority=9,
                    effectiveness=0.8,
                    feasibility=0.6,
                    cost_effectiveness=0.9,
                    target_risk_factors=["obesity", "insulin_resistance"],
                    expected_risk_reduction=0.4,
                    implementation_timeline="6-12个月达到目标",
                    monitoring_metrics=["weight", "bmi", "blood_glucose"]
                ),
                PreventionRecommendation(
                    id="dm_diet_control",
                    risk_category=RiskCategory.DIABETES,
                    intervention_type=InterventionType.LIFESTYLE,
                    title="控制碳水化合物摄入",
                    description="选择低血糖指数食物，控制总热量摄入",
                    priority=8,
                    effectiveness=0.7,
                    feasibility=0.7,
                    cost_effectiveness=0.8,
                    target_risk_factors=["high_blood_glucose", "insulin_resistance"],
                    expected_risk_reduction=0.3,
                    implementation_timeline="2-4周适应新饮食模式",
                    monitoring_metrics=["blood_glucose", "hba1c", "weight"]
                )
            ],
            RiskCategory.HYPERTENSION: [
                PreventionRecommendation(
                    id="htn_sodium_reduction",
                    risk_category=RiskCategory.HYPERTENSION,
                    intervention_type=InterventionType.LIFESTYLE,
                    title="减少钠盐摄入",
                    description="每日钠摄入量控制在2300mg以下，理想情况下1500mg",
                    priority=8,
                    effectiveness=0.6,
                    feasibility=0.8,
                    cost_effectiveness=0.9,
                    target_risk_factors=["high_sodium_intake"],
                    expected_risk_reduction=0.2,
                    implementation_timeline="2-4周见效",
                    monitoring_metrics=["blood_pressure"]
                ),
                PreventionRecommendation(
                    id="htn_stress_management",
                    risk_category=RiskCategory.HYPERTENSION,
                    intervention_type=InterventionType.LIFESTYLE,
                    title="压力管理",
                    description="学习放松技巧，如冥想、深呼吸、瑜伽",
                    priority=6,
                    effectiveness=0.5,
                    feasibility=0.7,
                    cost_effectiveness=0.8,
                    target_risk_factors=["chronic_stress"],
                    expected_risk_reduction=0.15,
                    implementation_timeline="4-8周建立习惯",
                    monitoring_metrics=["blood_pressure", "stress_level"]
                )
            ]
        }
    
    async def generate_prevention_plan(
        self,
        risk_predictions: List[RiskPrediction],
        user_profile: RiskAssessmentProfile
    ) -> List[PreventionRecommendation]:
        """生成预防计划"""
        try:
            prevention_plan = []
            
            # 按风险级别排序
            sorted_predictions = sorted(
                risk_predictions,
                key=lambda x: x.probability,
                reverse=True
            )
            
            for prediction in sorted_predictions:
                if prediction.risk_level in [RiskLevel.MODERATE, RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
                    # 获取该类别的预防建议
                    category_recommendations = self.recommendation_database.get(
                        prediction.category, []
                    )
                    
                    # 个性化建议
                    personalized_recommendations = await self._personalize_recommendations(
                        category_recommendations, user_profile, prediction
                    )
                    
                    prevention_plan.extend(personalized_recommendations)
            
            # 去重和排序
            unique_recommendations = self._deduplicate_recommendations(prevention_plan)
            sorted_recommendations = sorted(
                unique_recommendations,
                key=lambda x: (x.priority, x.effectiveness),
                reverse=True
            )
            
            return sorted_recommendations[:10]  # 返回前10个建议
            
        except Exception as e:
            logger.error(f"生成预防计划失败: {e}")
            return []
    
    async def _personalize_recommendations(
        self,
        recommendations: List[PreventionRecommendation],
        user_profile: RiskAssessmentProfile,
        prediction: RiskPrediction
    ) -> List[PreventionRecommendation]:
        """个性化建议"""
        try:
            personalized = []
            
            for rec in recommendations:
                # 复制建议
                personalized_rec = PreventionRecommendation(
                    id=f"{rec.id}_{user_profile.user_id}",
                    risk_category=rec.risk_category,
                    intervention_type=rec.intervention_type,
                    title=rec.title,
                    description=rec.description,
                    priority=rec.priority,
                    effectiveness=rec.effectiveness,
                    feasibility=rec.feasibility,
                    cost_effectiveness=rec.cost_effectiveness,
                    target_risk_factors=rec.target_risk_factors,
                    expected_risk_reduction=rec.expected_risk_reduction,
                    implementation_timeline=rec.implementation_timeline,
                    monitoring_metrics=rec.monitoring_metrics,
                    contraindications=rec.contraindications,
                    side_effects=rec.side_effects,
                    evidence_level=rec.evidence_level
                )
                
                # 根据用户特征调整可行性
                personalized_rec.feasibility = await self._adjust_feasibility(
                    rec, user_profile
                )
                
                # 根据风险级别调整优先级
                if prediction.risk_level == RiskLevel.VERY_HIGH:
                    personalized_rec.priority = min(personalized_rec.priority + 2, 10)
                elif prediction.risk_level == RiskLevel.HIGH:
                    personalized_rec.priority = min(personalized_rec.priority + 1, 10)
                
                # 检查禁忌症
                if not await self._check_contraindications(rec, user_profile):
                    continue
                
                personalized.append(personalized_rec)
            
            return personalized
            
        except Exception as e:
            logger.error(f"个性化建议失败: {e}")
            return recommendations
    
    async def _adjust_feasibility(
        self,
        recommendation: PreventionRecommendation,
        user_profile: RiskAssessmentProfile
    ) -> float:
        """调整可行性"""
        try:
            base_feasibility = recommendation.feasibility
            
            # 根据年龄调整
            age = await self._get_user_age(user_profile)
            if age > 70:
                base_feasibility *= 0.8  # 老年人可行性降低
            elif age < 30:
                base_feasibility *= 1.1  # 年轻人可行性提高
            
            # 根据健康状况调整
            health_conditions = user_profile.medical_history.get("conditions", [])
            if len(health_conditions) > 3:
                base_feasibility *= 0.9  # 多种疾病降低可行性
            
            # 根据生活方式调整
            if recommendation.intervention_type == InterventionType.LIFESTYLE:
                current_activity = user_profile.lifestyle_factors.get("exercise_frequency", "low")
                if current_activity == "high":
                    base_feasibility *= 1.2  # 已有运动习惯
                elif current_activity == "none":
                    base_feasibility *= 0.7  # 缺乏运动习惯
            
            return min(base_feasibility, 1.0)
            
        except Exception as e:
            logger.error(f"调整可行性失败: {e}")
            return recommendation.feasibility
    
    async def _check_contraindications(
        self,
        recommendation: PreventionRecommendation,
        user_profile: RiskAssessmentProfile
    ) -> bool:
        """检查禁忌症"""
        try:
            user_conditions = user_profile.medical_history.get("conditions", [])
            user_medications = user_profile.medical_history.get("medications", [])
            
            # 检查疾病禁忌症
            for contraindication in recommendation.contraindications:
                if contraindication.lower() in [c.lower() for c in user_conditions]:
                    return False
            
            # 特殊检查
            if recommendation.intervention_type == InterventionType.LIFESTYLE:
                if "heart_failure" in user_conditions and "exercise" in recommendation.title.lower():
                    # 心衰患者需要特殊运动指导
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"检查禁忌症失败: {e}")
            return True
    
    async def _get_user_age(self, user_profile: RiskAssessmentProfile) -> int:
        """获取用户年龄"""
        try:
            birth_date = user_profile.demographics.get("birth_date")
            if birth_date:
                age = (datetime.now() - datetime.fromisoformat(birth_date)).days / 365.25
                return int(age)
            return 50  # 默认年龄
        except:
            return 50
    
    def _deduplicate_recommendations(
        self,
        recommendations: List[PreventionRecommendation]
    ) -> List[PreventionRecommendation]:
        """去重建议"""
        seen_titles = set()
        unique_recommendations = []
        
        for rec in recommendations:
            if rec.title not in seen_titles:
                seen_titles.add(rec.title)
                unique_recommendations.append(rec)
        
        return unique_recommendations

class IntelligentRiskAssessment:
    """智能风险评估引擎"""
    
    def __init__(self, config: Dict[str, Any], metrics_collector: Optional[MetricsCollector] = None):
        self.config = config
        self.metrics_collector = metrics_collector
        
        # 核心组件
        self.risk_calculator = RiskCalculator()
        self.predictive_model = PredictiveModel()
        self.prevention_engine = PreventionEngine()
        
        # 数据存储
        self.user_profiles: Dict[str, RiskAssessmentProfile] = {}
        self.risk_predictions: Dict[str, List[RiskPrediction]] = {}
        self.prevention_plans: Dict[str, List[PreventionRecommendation]] = {}
        
        logger.info("智能风险评估引擎初始化完成")
    
    async def initialize(self):
        """初始化风险评估引擎"""
        try:
            # 加载预训练模型
            await self._load_pretrained_models()
            
            logger.info("风险评估引擎初始化成功")
            
        except Exception as e:
            logger.error(f"风险评估引擎初始化失败: {e}")
    
    async def _load_pretrained_models(self):
        """加载预训练模型"""
        try:
            # 这里应该从文件或数据库加载预训练的模型
            # 现在创建一些示例训练数据来训练模型
            
            for category in [RiskCategory.CARDIOVASCULAR, RiskCategory.DIABETES, RiskCategory.HYPERTENSION]:
                # 生成示例训练数据
                training_data = await self._generate_sample_training_data(category)
                
                # 训练模型
                result = await self.predictive_model.train_model(
                    category, training_data, "outcome"
                )
                
                if result["status"] == "success":
                    logger.info(f"成功训练 {category.value} 模型")
                else:
                    logger.warning(f"训练 {category.value} 模型失败: {result}")
            
        except Exception as e:
            logger.error(f"加载预训练模型失败: {e}")
    
    async def _generate_sample_training_data(self, category: RiskCategory) -> pd.DataFrame:
        """生成示例训练数据"""
        try:
            np.random.seed(42)
            n_samples = 1000
            
            if category == RiskCategory.CARDIOVASCULAR:
                data = {
                    "age": np.random.normal(55, 15, n_samples),
                    "gender": np.random.choice([0, 1], n_samples),
                    "smoking": np.random.choice([0, 0.5, 1], n_samples),
                    "blood_pressure_systolic": np.random.normal(130, 20, n_samples),
                    "cholesterol": np.random.normal(200, 40, n_samples),
                    "diabetes": np.random.choice([0, 1], n_samples, p=[0.9, 0.1]),
                    "family_history_cvd": np.random.choice([0, 1], n_samples, p=[0.8, 0.2]),
                    "bmi": np.random.normal(26, 4, n_samples)
                }
                
                # 生成结果（基于风险因子）
                risk_score = (
                    data["age"] * 0.02 +
                    data["gender"] * 0.1 +
                    data["smoking"] * 0.3 +
                    (data["blood_pressure_systolic"] - 120) * 0.01 +
                    (data["cholesterol"] - 200) * 0.002 +
                    data["diabetes"] * 0.2 +
                    data["family_history_cvd"] * 0.15 +
                    (data["bmi"] - 25) * 0.02
                )
                
                data["outcome"] = (risk_score + np.random.normal(0, 0.1, n_samples) > 1.5).astype(int)
                
            elif category == RiskCategory.DIABETES:
                data = {
                    "age": np.random.normal(50, 12, n_samples),
                    "bmi": np.random.normal(28, 5, n_samples),
                    "family_history_diabetes": np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
                    "blood_glucose": np.random.normal(5.5, 1.5, n_samples),
                    "physical_activity": np.random.uniform(0, 1, n_samples),
                    "diet_quality": np.random.uniform(0, 1, n_samples)
                }
                
                risk_score = (
                    data["age"] * 0.02 +
                    (data["bmi"] - 25) * 0.05 +
                    data["family_history_diabetes"] * 0.3 +
                    (data["blood_glucose"] - 5.5) * 0.2 +
                    (1 - data["physical_activity"]) * 0.2 +
                    (1 - data["diet_quality"]) * 0.15
                )
                
                data["outcome"] = (risk_score + np.random.normal(0, 0.1, n_samples) > 1.2).astype(int)
                
            else:  # HYPERTENSION
                data = {
                    "age": np.random.normal(45, 10, n_samples),
                    "bmi": np.random.normal(27, 4, n_samples),
                    "sodium_intake": np.random.normal(0.5, 0.2, n_samples),
                    "alcohol": np.random.uniform(0, 1, n_samples),
                    "stress_level": np.random.uniform(0, 1, n_samples),
                    "family_history_hypertension": np.random.choice([0, 1], n_samples, p=[0.6, 0.4]),
                    "physical_activity": np.random.uniform(0, 1, n_samples)
                }
                
                risk_score = (
                    data["age"] * 0.02 +
                    (data["bmi"] - 25) * 0.03 +
                    data["sodium_intake"] * 0.2 +
                    data["alcohol"] * 0.1 +
                    data["stress_level"] * 0.15 +
                    data["family_history_hypertension"] * 0.2 +
                    (1 - data["physical_activity"]) * 0.1
                )
                
                data["outcome"] = (risk_score + np.random.normal(0, 0.1, n_samples) > 1.0).astype(int)
            
            return pd.DataFrame(data)
            
        except Exception as e:
            logger.error(f"生成示例训练数据失败: {e}")
            return pd.DataFrame()
    
    @trace_operation("risk_assessment.assess_risk", SpanKind.INTERNAL)
    async def assess_comprehensive_risk(
        self,
        user_id: str,
        profile_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """综合风险评估"""
        start_time = time.time()
        
        try:
            # 创建或更新用户档案
            profile = await self._create_or_update_profile(user_id, profile_data)
            
            # 多类别风险评估
            risk_predictions = []
            
            for category in [RiskCategory.CARDIOVASCULAR, RiskCategory.DIABETES, RiskCategory.HYPERTENSION]:
                for timeframe in [RiskTimeframe.SHORT_TERM, RiskTimeframe.MEDIUM_TERM, RiskTimeframe.LONG_TERM]:
                    prediction = await self.predictive_model.predict_risk(
                        profile, category, timeframe
                    )
                    
                    if prediction:
                        risk_predictions.append(prediction)
            
            # 存储预测结果
            self.risk_predictions[user_id] = risk_predictions
            
            # 生成预防计划
            prevention_plan = await self.prevention_engine.generate_prevention_plan(
                risk_predictions, profile
            )
            
            # 存储预防计划
            self.prevention_plans[user_id] = prevention_plan
            
            processing_time = time.time() - start_time
            
            # 记录指标
            if self.metrics_collector:
                self.metrics_collector.increment_counter(
                    "risk_assessments_completed",
                    {"user_id": user_id}
                )
                self.metrics_collector.record_histogram(
                    "risk_assessment_time",
                    processing_time,
                    {"user_id": user_id}
                )
            
            # 生成摘要
            risk_summary = await self._generate_risk_summary(risk_predictions)
            
            result = {
                "status": "success",
                "user_id": user_id,
                "risk_predictions": [
                    {
                        "category": pred.category.value,
                        "timeframe": pred.timeframe.value,
                        "probability": pred.probability,
                        "risk_level": pred.risk_level.value,
                        "confidence_interval": pred.confidence_interval
                    }
                    for pred in risk_predictions
                ],
                "prevention_plan": [
                    {
                        "id": rec.id,
                        "title": rec.title,
                        "description": rec.description,
                        "priority": rec.priority,
                        "effectiveness": rec.effectiveness,
                        "intervention_type": rec.intervention_type.value
                    }
                    for rec in prevention_plan[:5]  # 返回前5个建议
                ],
                "risk_summary": risk_summary,
                "processing_time": processing_time,
                "assessment_date": datetime.now().isoformat()
            }
            
            logger.info(f"风险评估完成: {user_id}, 处理时间: {processing_time:.2f}秒")
            return result
            
        except Exception as e:
            logger.error(f"综合风险评估失败: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _create_or_update_profile(
        self,
        user_id: str,
        profile_data: Dict[str, Any]
    ) -> RiskAssessmentProfile:
        """创建或更新用户档案"""
        try:
            if user_id in self.user_profiles:
                # 更新现有档案
                profile = self.user_profiles[user_id]
                profile.updated_at = datetime.now()
                
                # 更新各个部分
                if "demographics" in profile_data:
                    profile.demographics.update(profile_data["demographics"])
                if "medical_history" in profile_data:
                    profile.medical_history.update(profile_data["medical_history"])
                if "family_history" in profile_data:
                    profile.family_history.update(profile_data["family_history"])
                if "lifestyle_factors" in profile_data:
                    profile.lifestyle_factors.update(profile_data["lifestyle_factors"])
                if "clinical_measurements" in profile_data:
                    profile.clinical_measurements.update(profile_data["clinical_measurements"])
                
            else:
                # 创建新档案
                profile = RiskAssessmentProfile(
                    user_id=user_id,
                    demographics=profile_data.get("demographics", {}),
                    medical_history=profile_data.get("medical_history", {}),
                    family_history=profile_data.get("family_history", {}),
                    lifestyle_factors=profile_data.get("lifestyle_factors", {}),
                    clinical_measurements=profile_data.get("clinical_measurements", {}),
                    genetic_markers=profile_data.get("genetic_markers", {}),
                    environmental_factors=profile_data.get("environmental_factors", {}),
                    risk_preferences=profile_data.get("risk_preferences", {})
                )
                
                self.user_profiles[user_id] = profile
            
            return profile
            
        except Exception as e:
            logger.error(f"创建或更新用户档案失败: {e}")
            raise
    
    async def _generate_risk_summary(self, predictions: List[RiskPrediction]) -> Dict[str, Any]:
        """生成风险摘要"""
        try:
            if not predictions:
                return {"overall_risk": "unknown", "high_risk_categories": []}
            
            # 计算总体风险
            high_risk_predictions = [
                p for p in predictions 
                if p.risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH, RiskLevel.CRITICAL]
            ]
            
            if len(high_risk_predictions) >= 3:
                overall_risk = "high"
            elif len(high_risk_predictions) >= 1:
                overall_risk = "moderate"
            else:
                overall_risk = "low"
            
            # 识别高风险类别
            high_risk_categories = list(set([
                p.category.value for p in high_risk_predictions
            ]))
            
            # 最高风险预测
            highest_risk_prediction = max(predictions, key=lambda x: x.probability)
            
            return {
                "overall_risk": overall_risk,
                "high_risk_categories": high_risk_categories,
                "highest_risk": {
                    "category": highest_risk_prediction.category.value,
                    "probability": highest_risk_prediction.probability,
                    "risk_level": highest_risk_prediction.risk_level.value
                },
                "total_predictions": len(predictions),
                "high_risk_count": len(high_risk_predictions)
            }
            
        except Exception as e:
            logger.error(f"生成风险摘要失败: {e}")
            return {"overall_risk": "unknown", "high_risk_categories": []}
    
    async def get_user_risk_profile(self, user_id: str) -> Dict[str, Any]:
        """获取用户风险档案"""
        try:
            if user_id not in self.user_profiles:
                return {"status": "not_found", "message": "用户档案不存在"}
            
            profile = self.user_profiles[user_id]
            predictions = self.risk_predictions.get(user_id, [])
            prevention_plan = self.prevention_plans.get(user_id, [])
            
            return {
                "status": "success",
                "user_id": user_id,
                "profile": {
                    "demographics": profile.demographics,
                    "medical_history": profile.medical_history,
                    "family_history": profile.family_history,
                    "lifestyle_factors": profile.lifestyle_factors,
                    "clinical_measurements": profile.clinical_measurements,
                    "created_at": profile.created_at.isoformat(),
                    "updated_at": profile.updated_at.isoformat()
                },
                "current_predictions": len(predictions),
                "prevention_recommendations": len(prevention_plan),
                "last_assessment": max([p.created_at for p in predictions]).isoformat() if predictions else None
            }
            
        except Exception as e:
            logger.error(f"获取用户风险档案失败: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_assessment_statistics(self) -> Dict[str, Any]:
        """获取评估统计信息"""
        try:
            total_users = len(self.user_profiles)
            total_predictions = sum(len(preds) for preds in self.risk_predictions.values())
            
            # 按风险级别统计
            risk_level_counts = {}
            for predictions in self.risk_predictions.values():
                for pred in predictions:
                    level = pred.risk_level.value
                    risk_level_counts[level] = risk_level_counts.get(level, 0) + 1
            
            # 按类别统计
            category_counts = {}
            for predictions in self.risk_predictions.values():
                for pred in predictions:
                    category = pred.category.value
                    category_counts[category] = category_counts.get(category, 0) + 1
            
            return {
                "total_users": total_users,
                "total_predictions": total_predictions,
                "risk_level_distribution": risk_level_counts,
                "category_distribution": category_counts,
                "models_trained": len(self.predictive_model.models),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取评估统计失败: {e}")
            return {}

def initialize_risk_assessment(
    config: Dict[str, Any],
    metrics_collector: Optional[MetricsCollector] = None
) -> IntelligentRiskAssessment:
    """初始化智能风险评估引擎"""
    return IntelligentRiskAssessment(config, metrics_collector)

# 全局实例
_risk_assessment_instance: Optional[IntelligentRiskAssessment] = None

def get_risk_assessment() -> Optional[IntelligentRiskAssessment]:
    """获取风险评估引擎实例"""
    return _risk_assessment_instance 