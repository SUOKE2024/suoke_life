#!/usr/bin/env python3

"""
预测性分析模块
使用机器学习算法预测健康趋势，提供风险评估和早期预警功能
支持时序预测、异常检测和个性化风险建模
"""

import logging
import pickle
import warnings
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from sklearn.cluster import KMeans

# 机器学习库
from sklearn.ensemble import (
    GradientBoostingRegressor,
    IsolationForest,
    RandomForestRegressor,
)
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import StandardScaler

# 时序分析库
try:
    from statsmodels.tsa.arima.model import ARIMA

    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    warnings.warn("statsmodels not available, time series analysis will be limited")

logger = logging.getLogger(__name__)

class PredictionType(Enum):
    """预测类型枚举"""

    HEALTH_TREND = "health_trend"  # 健康趋势
    RISK_ASSESSMENT = "risk_assessment"  # 风险评估
    ANOMALY_DETECTION = "anomaly_detection"  # 异常检测
    CONSTITUTION_EVOLUTION = "constitution_evolution"  # 体质演变
    INTERVENTION_EFFECT = "intervention_effect"  # 干预效果

class RiskLevel(Enum):
    """风险等级枚举"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ModelType(Enum):
    """模型类型枚举"""

    LINEAR_REGRESSION = "linear_regression"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    ARIMA = "arima"
    ISOLATION_FOREST = "isolation_forest"
    KMEANS = "kmeans"

@dataclass
class PredictionResult:
    """预测结果"""

    prediction_id: str
    prediction_type: PredictionType
    predicted_values: dict[str, float]
    confidence_scores: dict[str, float]
    risk_level: RiskLevel
    time_horizon: int  # 预测时间范围（天）
    model_used: ModelType
    feature_importance: dict[str, float]
    recommendations: list[str]
    uncertainty_bounds: dict[str, tuple[float, float]]
    created_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class HealthTrend:
    """健康趋势"""

    trend_direction: str  # improving, stable, declining
    trend_strength: float  # 0-1
    key_indicators: list[str]
    projected_timeline: dict[str, float]  # 时间点 -> 预测值
    confidence: float

@dataclass
class RiskAssessment:
    """风险评估"""

    overall_risk: RiskLevel
    specific_risks: dict[str, float]  # 具体风险类型和概率
    risk_factors: list[str]
    protective_factors: list[str]
    time_to_risk: int | None  # 预计多少天后可能出现风险
    mitigation_strategies: list[str]

class PredictiveAnalyzer:
    """预测性分析器"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化预测性分析器

        Args:
            config: 配置字典
        """
        self.config = config

        # 模型配置
        self.model_config = config.get("models", {})
        self.model_dir = config.get("model_dir", "models/prediction")
        self.retrain_interval = config.get("retrain_interval", 7)  # 天

        # 预测配置
        self.prediction_config = config.get("prediction", {})
        self.default_horizon = self.prediction_config.get("default_horizon", 30)  # 天
        self.min_data_points = self.prediction_config.get("min_data_points", 10)
        self.confidence_threshold = self.prediction_config.get("confidence_threshold", 0.7)

        # 风险评估配置
        self.risk_config = config.get("risk_assessment", {})
        self.risk_thresholds = self.risk_config.get(
            "thresholds", {"low": 0.3, "medium": 0.6, "high": 0.8}
        )

        # 特征工程配置
        self.feature_config = config.get("feature_engineering", {})
        self.feature_window = self.feature_config.get("window_size", 7)
        self.lag_features = self.feature_config.get("lag_features", [1, 3, 7])

        # 模型存储
        self.models: dict[str, Any] = {}
        self.scalers: dict[str, StandardScaler] = {}
        self.model_metadata: dict[str, dict] = {}

        # 历史数据存储
        self.historical_data: list[dict[str, Any]] = []
        self.prediction_history: list[PredictionResult] = []

        # 线程池
        self.executor = ThreadPoolExecutor(max_workers=4)

        # 初始化组件
        self._initialize_models()

        logger.info("预测性分析器初始化完成")

    def _initialize_models(self):
        """初始化模型"""
        try:
            # 创建模型目录
            Path(self.model_dir).mkdir(parents=True, exist_ok=True)

            # 初始化默认模型
            self._create_default_models()

            # 尝试加载已训练的模型
            self._load_trained_models()

            logger.info("预测模型初始化完成")

        except Exception as e:
            logger.error(f"模型初始化失败: {e}")
            raise

    def _create_default_models(self):
        """创建默认模型"""
        # 健康趋势预测模型
        self.models["health_trend"] = {
            "linear": LinearRegression(),
            "rf": RandomForestRegressor(n_estimators=100, random_state=42),
            "gb": GradientBoostingRegressor(n_estimators=100, random_state=42),
        }

        # 风险评估模型
        self.models["risk_assessment"] = {
            "logistic": LogisticRegression(random_state=42),
            "rf_classifier": RandomForestRegressor(n_estimators=100, random_state=42),
        }

        # 异常检测模型
        self.models["anomaly_detection"] = {
            "isolation_forest": IsolationForest(contamination=0.1, random_state=42)
        }

        # 聚类模型（体质分类）
        self.models["clustering"] = {"kmeans": KMeans(n_clusters=9, random_state=42)}  # 9种体质类型

        # 时序预测模型
        if STATSMODELS_AVAILABLE:
            self.models["time_series"] = {"arima": None}  # 将在使用时动态创建

        # 初始化缩放器
        for model_type in self.models.keys():
            self.scalers[model_type] = StandardScaler()

    def _load_trained_models(self):
        """加载已训练的模型"""
        try:
            model_files = list(Path(self.model_dir).glob("*.pkl"))

            for model_file in model_files:
                model_name = model_file.stem
                try:
                    with open(model_file, "rb") as f:
                        model_data = pickle.load(f)

                    # 更新模型
                    if "model" in model_data:
                        model_type, sub_type = model_name.split("_", 1)
                        if model_type in self.models:
                            self.models[model_type][sub_type] = model_data["model"]

                    # 更新缩放器
                    if "scaler" in model_data:
                        self.scalers[model_type] = model_data["scaler"]

                    # 更新元数据
                    if "metadata" in model_data:
                        self.model_metadata[model_name] = model_data["metadata"]

                    logger.info(f"加载模型: {model_name}")

                except Exception as e:
                    logger.warning(f"加载模型失败: {model_name}, {e}")

        except Exception as e:
            logger.warning(f"模型加载过程出错: {e}")

    async def predict_health_trend(
        self, user_id: str, historical_features: list[dict[str, Any]], time_horizon: int = None
    ) -> HealthTrend:
        """
        预测健康趋势

        Args:
            user_id: 用户ID
            historical_features: 历史特征数据
            time_horizon: 预测时间范围（天）

        Returns:
            健康趋势预测结果
        """
        try:
            if time_horizon is None:
                time_horizon = self.default_horizon

            # 检查数据充足性
            if len(historical_features) < self.min_data_points:
                raise ValueError(f"历史数据不足，需要至少{self.min_data_points}个数据点")

            # 特征工程
            features_df = await self._prepare_features_for_trend_prediction(historical_features)

            # 使用多个模型进行预测
            predictions = {}
            confidences = {}

            for model_name, model in self.models["health_trend"].items():
                try:
                    pred, conf = await self._predict_with_model(
                        model, features_df, model_name, time_horizon
                    )
                    predictions[model_name] = pred
                    confidences[model_name] = conf
                except Exception as e:
                    logger.warning(f"模型{model_name}预测失败: {e}")

            # 集成预测结果
            ensemble_prediction = await self._ensemble_predictions(predictions, confidences)

            # 分析趋势方向和强度
            trend_direction, trend_strength = await self._analyze_trend_direction(
                historical_features, ensemble_prediction
            )

            # 识别关键指标
            key_indicators = await self._identify_key_indicators(features_df)

            # 生成时间线预测
            projected_timeline = await self._generate_timeline_projection(
                ensemble_prediction, time_horizon
            )

            # 计算整体置信度
            overall_confidence = np.mean(list(confidences.values())) if confidences else 0.5

            return HealthTrend(
                trend_direction=trend_direction,
                trend_strength=trend_strength,
                key_indicators=key_indicators,
                projected_timeline=projected_timeline,
                confidence=overall_confidence,
            )

        except Exception as e:
            logger.error(f"健康趋势预测失败: {e}")
            raise

    async def assess_health_risks(
        self,
        user_profile: dict[str, Any],
        current_features: dict[str, Any],
        historical_data: list[dict[str, Any]],
    ) -> RiskAssessment:
        """
        评估健康风险

        Args:
            user_profile: 用户档案
            current_features: 当前特征
            historical_data: 历史数据

        Returns:
            风险评估结果
        """
        try:
            # 准备风险评估特征
            risk_features = await self._prepare_risk_features(
                user_profile, current_features, historical_data
            )

            # 计算各类风险
            specific_risks = await self._calculate_specific_risks(risk_features)

            # 确定整体风险等级
            overall_risk = await self._determine_overall_risk(specific_risks)

            # 识别风险因素和保护因素
            risk_factors, protective_factors = await self._identify_risk_factors(
                risk_features, specific_risks
            )

            # 预测风险时间
            time_to_risk = await self._predict_time_to_risk(risk_features, overall_risk)

            # 生成缓解策略
            mitigation_strategies = await self._generate_mitigation_strategies(
                overall_risk, specific_risks, user_profile
            )

            return RiskAssessment(
                overall_risk=overall_risk,
                specific_risks=specific_risks,
                risk_factors=risk_factors,
                protective_factors=protective_factors,
                time_to_risk=time_to_risk,
                mitigation_strategies=mitigation_strategies,
            )

        except Exception as e:
            logger.error(f"风险评估失败: {e}")
            raise

    async def detect_anomalies(
        self, current_features: dict[str, Any], reference_data: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        检测异常

        Args:
            current_features: 当前特征
            reference_data: 参考数据

        Returns:
            异常检测结果
        """
        try:
            # 准备异常检测特征
            features_array = await self._prepare_anomaly_features(current_features, reference_data)

            # 使用隔离森林检测异常
            isolation_model = self.models["anomaly_detection"]["isolation_forest"]

            # 如果模型未训练，先训练
            if not hasattr(isolation_model, "decision_function"):
                if len(reference_data) >= self.min_data_points:
                    ref_features = np.array(
                        [list(data.get("features", {}).values()) for data in reference_data]
                    )
                    isolation_model.fit(ref_features)
                else:
                    # 数据不足，返回默认结果
                    return {
                        "is_anomaly": False,
                        "anomaly_score": 0.0,
                        "confidence": 0.0,
                        "anomalous_features": [],
                    }

            # 预测异常
            current_array = np.array(list(current_features.values())).reshape(1, -1)
            anomaly_score = isolation_model.decision_function(current_array)[0]
            is_anomaly = isolation_model.predict(current_array)[0] == -1

            # 识别异常特征
            anomalous_features = await self._identify_anomalous_features(
                current_features, reference_data
            )

            # 计算置信度
            confidence = abs(anomaly_score)

            return {
                "is_anomaly": is_anomaly,
                "anomaly_score": float(anomaly_score),
                "confidence": float(confidence),
                "anomalous_features": anomalous_features,
            }

        except Exception as e:
            logger.error(f"异常检测失败: {e}")
            return {
                "is_anomaly": False,
                "anomaly_score": 0.0,
                "confidence": 0.0,
                "anomalous_features": [],
            }

    async def predict_constitution_evolution(
        self,
        user_profile: dict[str, Any],
        historical_constitutions: list[str],
        intervention_plan: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        预测体质演变

        Args:
            user_profile: 用户档案
            historical_constitutions: 历史体质类型
            intervention_plan: 干预计划

        Returns:
            体质演变预测
        """
        try:
            # 分析体质变化模式
            constitution_pattern = await self._analyze_constitution_pattern(
                historical_constitutions
            )

            # 预测未来体质
            if intervention_plan:
                predicted_constitution = await self._predict_constitution_with_intervention(
                    constitution_pattern, intervention_plan, user_profile
                )
            else:
                predicted_constitution = await self._predict_natural_constitution_evolution(
                    constitution_pattern, user_profile
                )

            # 计算演变概率
            evolution_probabilities = await self._calculate_evolution_probabilities(
                constitution_pattern, predicted_constitution
            )

            # 生成建议
            recommendations = await self._generate_constitution_recommendations(
                predicted_constitution, user_profile
            )

            return {
                "current_pattern": constitution_pattern,
                "predicted_constitution": predicted_constitution,
                "evolution_probabilities": evolution_probabilities,
                "time_to_change": await self._estimate_constitution_change_time(
                    constitution_pattern
                ),
                "recommendations": recommendations,
                "confidence": 0.75,  # 基于历史数据的置信度
            }

        except Exception as e:
            logger.error(f"体质演变预测失败: {e}")
            return {
                "predicted_constitution": "unknown",
                "evolution_probabilities": {},
                "recommendations": [],
                "confidence": 0.0,
            }

    async def _prepare_features_for_trend_prediction(
        self, historical_features: list[dict[str, Any]]
    ) -> pd.DataFrame:
        """准备趋势预测特征"""
        # 转换为DataFrame
        df = pd.DataFrame(historical_features)

        # 确保有时间戳
        if "timestamp" not in df.columns:
            df["timestamp"] = pd.date_range(end=datetime.now(), periods=len(df), freq="D")
        else:
            df["timestamp"] = pd.to_datetime(df["timestamp"])

        # 排序
        df = df.sort_values("timestamp")

        # 特征工程
        feature_columns = [col for col in df.columns if col != "timestamp"]

        # 添加滞后特征
        for lag in self.lag_features:
            for col in feature_columns:
                if col in df.columns:
                    df[f"{col}_lag_{lag}"] = df[col].shift(lag)

        # 添加移动平均
        window_size = min(self.feature_window, len(df) // 2)
        if window_size > 1:
            for col in feature_columns:
                if col in df.columns:
                    df[f"{col}_ma_{window_size}"] = df[col].rolling(window=window_size).mean()

        # 添加趋势特征
        for col in feature_columns:
            if col in df.columns:
                df[f"{col}_trend"] = df[col].diff()

        # 删除包含NaN的行
        df = df.dropna()

        return df

    async def _predict_with_model(
        self, model: Any, features_df: pd.DataFrame, model_name: str, time_horizon: int
    ) -> tuple[np.ndarray, float]:
        """使用指定模型进行预测"""
        try:
            # 准备特征和目标
            feature_cols = [col for col in features_df.columns if col != "timestamp"]
            X = features_df[feature_cols].values

            # 如果模型未训练，使用历史数据训练
            if not hasattr(model, "predict"):
                # 创建目标变量（下一期的健康评分）
                y = features_df["overall_health"].shift(-1).dropna().values
                X_train = X[:-1]  # 去掉最后一行

                if len(X_train) > 0 and len(y) > 0:
                    model.fit(X_train, y)
                else:
                    raise ValueError("训练数据不足")

            # 预测
            if hasattr(model, "predict"):
                # 使用最新数据进行预测
                latest_features = X[-1:] if len(X) > 0 else np.zeros((1, len(feature_cols)))
                prediction = model.predict(latest_features)

                # 计算置信度（基于模型类型）
                if hasattr(model, "score") and len(X) > 1:
                    y_true = features_df["overall_health"].shift(-1).dropna().values
                    X_score = X[:-1]
                    if len(X_score) > 0 and len(y_true) > 0:
                        confidence = model.score(X_score, y_true)
                    else:
                        confidence = 0.5
                else:
                    confidence = 0.5

                return prediction, max(0, min(1, confidence))
            else:
                return np.array([0.5]), 0.5

        except Exception as e:
            logger.warning(f"模型{model_name}预测失败: {e}")
            return np.array([0.5]), 0.0

    async def _ensemble_predictions(
        self, predictions: dict[str, np.ndarray], confidences: dict[str, float]
    ) -> np.ndarray:
        """集成多个模型的预测结果"""
        if not predictions:
            return np.array([0.5])

        # 加权平均
        total_weight = sum(confidences.values())
        if total_weight == 0:
            # 简单平均
            return np.mean(list(predictions.values()), axis=0)

        weighted_sum = np.zeros_like(list(predictions.values())[0])
        for model_name, pred in predictions.items():
            weight = confidences.get(model_name, 0)
            weighted_sum += pred * weight

        return weighted_sum / total_weight

    async def _analyze_trend_direction(
        self, historical_features: list[dict[str, Any]], prediction: np.ndarray
    ) -> tuple[str, float]:
        """分析趋势方向和强度"""
        if len(historical_features) < 2:
            return "stable", 0.5

        # 获取最近的健康评分
        recent_scores = [data.get("overall_health", 0.5) for data in historical_features[-5:]]

        if len(recent_scores) < 2:
            return "stable", 0.5

        # 计算趋势
        current_avg = np.mean(recent_scores[-2:])
        predicted_value = prediction[0] if len(prediction) > 0 else current_avg

        trend_change = predicted_value - current_avg

        # 确定方向
        if trend_change > 0.05:
            direction = "improving"
        elif trend_change < -0.05:
            direction = "declining"
        else:
            direction = "stable"

        # 计算强度
        strength = min(1.0, abs(trend_change) * 2)

        return direction, strength

    async def _identify_key_indicators(self, features_df: pd.DataFrame) -> list[str]:
        """识别关键指标"""
        # 基于变异系数识别关键指标
        key_indicators = []

        numeric_cols = features_df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            if col != "timestamp":
                # 计算变异系数
                mean_val = features_df[col].mean()
                std_val = features_df[col].std()

                if mean_val != 0:
                    cv = std_val / abs(mean_val)
                    if cv > 0.1:  # 变异系数阈值
                        key_indicators.append(col)

        # 限制数量
        return key_indicators[:5]

    async def _generate_timeline_projection(
        self, prediction: np.ndarray, time_horizon: int
    ) -> dict[str, float]:
        """生成时间线预测"""
        timeline = {}

        base_value = prediction[0] if len(prediction) > 0 else 0.5

        # 生成未来几个时间点的预测
        for days in [7, 14, 30, 60, 90]:
            if days <= time_horizon:
                # 简单的线性衰减模型
                decay_factor = 1 - (days / time_horizon) * 0.1
                projected_value = base_value * decay_factor
                timeline[f"day_{days}"] = max(0, min(1, projected_value))

        return timeline

    async def _prepare_risk_features(
        self,
        user_profile: dict[str, Any],
        current_features: dict[str, Any],
        historical_data: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """准备风险评估特征"""
        risk_features = {}

        # 用户基本信息
        risk_features["age"] = user_profile.get("age", 30)
        risk_features["gender"] = 1 if user_profile.get("gender") == "male" else 0

        # 当前健康指标
        risk_features.update(current_features)

        # 历史趋势特征
        if len(historical_data) >= 2:
            recent_data = historical_data[-5:]

            # 计算变化趋势
            for key in ["heart_rate", "blood_pressure", "overall_health"]:
                values = [data.get(key, 0) for data in recent_data if key in data]
                if len(values) >= 2:
                    trend = (values[-1] - values[0]) / len(values)
                    risk_features[f"{key}_trend"] = trend

        return risk_features

    async def _calculate_specific_risks(self, risk_features: dict[str, Any]) -> dict[str, float]:
        """计算具体风险"""
        specific_risks = {}

        # 心血管风险
        cv_risk = 0.0
        age = risk_features.get("age", 30)
        heart_rate = risk_features.get("heart_rate", 70)

        # 年龄因素
        if age > 60:
            cv_risk += 0.3
        elif age > 40:
            cv_risk += 0.1

        # 心率因素
        if heart_rate > 100 or heart_rate < 50:
            cv_risk += 0.2

        specific_risks["cardiovascular"] = min(1.0, cv_risk)

        # 代谢风险
        metabolic_risk = 0.0
        bmi = risk_features.get("bmi", 22)

        if bmi > 28:
            metabolic_risk += 0.4
        elif bmi > 25:
            metabolic_risk += 0.2

        specific_risks["metabolic"] = min(1.0, metabolic_risk)

        # 免疫风险
        immune_risk = 0.0
        overall_health = risk_features.get("overall_health", 0.7)

        if overall_health < 0.5:
            immune_risk += 0.3
        elif overall_health < 0.7:
            immune_risk += 0.1

        specific_risks["immune"] = min(1.0, immune_risk)

        return specific_risks

    async def _determine_overall_risk(self, specific_risks: dict[str, float]) -> RiskLevel:
        """确定整体风险等级"""
        if not specific_risks:
            return RiskLevel.LOW

        max_risk = max(specific_risks.values())
        avg_risk = np.mean(list(specific_risks.values()))

        # 综合考虑最高风险和平均风险
        overall_risk_score = max_risk * 0.6 + avg_risk * 0.4

        if overall_risk_score >= self.risk_thresholds["high"]:
            return RiskLevel.HIGH
        elif overall_risk_score >= self.risk_thresholds["medium"]:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    async def _identify_risk_factors(
        self, risk_features: dict[str, Any], specific_risks: dict[str, float]
    ) -> tuple[list[str], list[str]]:
        """识别风险因素和保护因素"""
        risk_factors = []
        protective_factors = []

        # 分析各项指标
        age = risk_features.get("age", 30)
        if age > 60:
            risk_factors.append("高龄")
        elif age < 30:
            protective_factors.append("年轻")

        heart_rate = risk_features.get("heart_rate", 70)
        if heart_rate > 100:
            risk_factors.append("心率过快")
        elif heart_rate < 50:
            risk_factors.append("心率过慢")
        elif 60 <= heart_rate <= 80:
            protective_factors.append("心率正常")

        overall_health = risk_features.get("overall_health", 0.7)
        if overall_health < 0.5:
            risk_factors.append("整体健康状况较差")
        elif overall_health > 0.8:
            protective_factors.append("整体健康状况良好")

        return risk_factors, protective_factors

    async def _predict_time_to_risk(
        self, risk_features: dict[str, Any], overall_risk: RiskLevel
    ) -> int | None:
        """预测风险时间"""
        if overall_risk == RiskLevel.LOW:
            return None

        # 基于风险等级估算时间
        base_days = {RiskLevel.MEDIUM: 90, RiskLevel.HIGH: 30, RiskLevel.CRITICAL: 7}

        return base_days.get(overall_risk, 90)

    async def _generate_mitigation_strategies(
        self,
        overall_risk: RiskLevel,
        specific_risks: dict[str, float],
        user_profile: dict[str, Any],
    ) -> list[str]:
        """生成缓解策略"""
        strategies = []

        # 基于整体风险等级
        if overall_risk in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            strategies.append("建议立即就医咨询")
            strategies.append("加强健康监测频率")

        # 基于具体风险
        if specific_risks.get("cardiovascular", 0) > 0.5:
            strategies.extend(["控制心率，适量有氧运动", "低盐低脂饮食", "定期监测血压"])

        if specific_risks.get("metabolic", 0) > 0.5:
            strategies.extend(["控制体重，均衡饮食", "增加运动量", "定期检查血糖"])

        if specific_risks.get("immune", 0) > 0.5:
            strategies.extend(["保证充足睡眠", "增强营养摄入", "适当补充维生素"])

        return strategies[:8]  # 限制策略数量

    async def _prepare_anomaly_features(
        self, current_features: dict[str, Any], reference_data: list[dict[str, Any]]
    ) -> np.ndarray:
        """准备异常检测特征"""
        # 确保特征一致性
        all_features = set(current_features.keys())
        for data in reference_data:
            all_features.update(data.get("features", {}).keys())

        feature_list = sorted(list(all_features))

        # 构建特征向量
        current_vector = [current_features.get(feat, 0) for feat in feature_list]

        return np.array(current_vector)

    async def _identify_anomalous_features(
        self, current_features: dict[str, Any], reference_data: list[dict[str, Any]]
    ) -> list[str]:
        """识别异常特征"""
        anomalous_features = []

        if not reference_data:
            return anomalous_features

        # 计算参考数据的统计信息
        ref_stats = {}
        for data in reference_data:
            features = data.get("features", {})
            for key, value in features.items():
                if key not in ref_stats:
                    ref_stats[key] = []
                ref_stats[key].append(value)

        # 检查当前特征是否异常
        for key, value in current_features.items():
            if key in ref_stats and len(ref_stats[key]) > 1:
                ref_values = ref_stats[key]
                mean_val = np.mean(ref_values)
                std_val = np.std(ref_values)

                if std_val > 0:
                    z_score = abs((value - mean_val) / std_val)
                    if z_score > 2:  # 2个标准差外视为异常
                        anomalous_features.append(key)

        return anomalous_features

    async def _analyze_constitution_pattern(
        self, historical_constitutions: list[str]
    ) -> dict[str, Any]:
        """分析体质变化模式"""
        if not historical_constitutions:
            return {"pattern": "unknown", "stability": 0.0}

        # 计算稳定性
        unique_constitutions = set(historical_constitutions)
        stability = 1.0 - (len(unique_constitutions) - 1) / max(1, len(historical_constitutions))

        # 识别主要体质
        from collections import Counter

        constitution_counts = Counter(historical_constitutions)
        dominant_constitution = constitution_counts.most_common(1)[0][0]

        # 分析变化趋势
        if len(historical_constitutions) >= 3:
            recent_trend = historical_constitutions[-3:]
            if len(set(recent_trend)) == 1:
                trend = "stable"
            else:
                trend = "changing"
        else:
            trend = "insufficient_data"

        return {
            "pattern": dominant_constitution,
            "stability": stability,
            "trend": trend,
            "constitution_counts": dict(constitution_counts),
        }

    async def _predict_natural_constitution_evolution(
        self, constitution_pattern: dict[str, Any], user_profile: dict[str, Any]
    ) -> str:
        """预测自然体质演变"""
        current_constitution = constitution_pattern.get("pattern", "balanced")
        stability = constitution_pattern.get("stability", 0.5)

        # 高稳定性体质不太可能改变
        if stability > 0.8:
            return current_constitution

        # 基于年龄的体质演变规律
        age = user_profile.get("age", 30)

        # 简化的体质演变规律
        if age > 60:
            # 老年人倾向于阳虚或气虚
            if current_constitution in ["balanced", "qi_deficiency"]:
                return "yang_deficiency"
            else:
                return current_constitution
        elif age > 40:
            # 中年人可能出现气虚
            if current_constitution == "balanced":
                return "qi_deficiency"
            else:
                return current_constitution
        else:
            # 年轻人体质相对稳定
            return current_constitution

    async def _predict_constitution_with_intervention(
        self,
        constitution_pattern: dict[str, Any],
        intervention_plan: dict[str, Any],
        user_profile: dict[str, Any],
    ) -> str:
        """预测干预后的体质演变"""
        current_constitution = constitution_pattern.get("pattern", "balanced")

        # 分析干预计划的效果
        intervention_type = intervention_plan.get("type", "lifestyle")
        intervention_intensity = intervention_plan.get("intensity", "moderate")

        # 简化的干预效果模型
        if intervention_type == "tcm_treatment":
            # 中医治疗通常能改善体质
            if current_constitution in ["qi_deficiency", "yang_deficiency", "yin_deficiency"]:
                return "balanced"
            else:
                return current_constitution
        elif intervention_type == "lifestyle":
            # 生活方式干预效果较温和
            if intervention_intensity == "high" and current_constitution != "balanced":
                # 有一定概率改善
                return "balanced" if np.random.random() > 0.5 else current_constitution
            else:
                return current_constitution
        else:
            return current_constitution

    async def _calculate_evolution_probabilities(
        self, constitution_pattern: dict[str, Any], predicted_constitution: str
    ) -> dict[str, float]:
        """计算演变概率"""
        current_constitution = constitution_pattern.get("pattern", "balanced")
        stability = constitution_pattern.get("stability", 0.5)

        probabilities = {}

        # 基于稳定性计算概率
        if predicted_constitution == current_constitution:
            probabilities[predicted_constitution] = 0.7 + stability * 0.3
        else:
            probabilities[predicted_constitution] = 0.3 + (1 - stability) * 0.4
            probabilities[current_constitution] = 1 - probabilities[predicted_constitution]

        return probabilities

    async def _estimate_constitution_change_time(self, constitution_pattern: dict[str, Any]) -> int:
        """估算体质改变时间"""
        stability = constitution_pattern.get("stability", 0.5)

        # 基于稳定性估算改变时间
        if stability > 0.8:
            return 365  # 1年
        elif stability > 0.6:
            return 180  # 6个月
        else:
            return 90  # 3个月

    async def _generate_constitution_recommendations(
        self, predicted_constitution: str, user_profile: dict[str, Any]
    ) -> list[str]:
        """生成体质建议"""
        recommendations = []

        constitution_advice = {
            "balanced": ["保持当前良好状态", "均衡饮食", "适量运动"],
            "qi_deficiency": ["补气食物", "避免过度劳累", "充足睡眠"],
            "yang_deficiency": ["温热食物", "避免生冷", "温和运动"],
            "yin_deficiency": ["滋阴食物", "避免辛辣", "保持心情平和"],
            "phlegm_dampness": ["清淡饮食", "适当运动", "保持环境干燥"],
            "damp_heat": ["清热利湿", "避免油腻", "适当运动排汗"],
        }

        recommendations.extend(constitution_advice.get(predicted_constitution, []))

        return recommendations

    async def save_model(self, model_type: str, model_name: str):
        """保存模型"""
        try:
            if model_type in self.models and model_name in self.models[model_type]:
                model_data = {
                    "model": self.models[model_type][model_name],
                    "scaler": self.scalers.get(model_type),
                    "metadata": {
                        "created_at": datetime.now().isoformat(),
                        "model_type": model_type,
                        "model_name": model_name,
                    },
                }

                filename = f"{model_type}_{model_name}.pkl"
                filepath = Path(self.model_dir) / filename

                with open(filepath, "wb") as f:
                    pickle.dump(model_data, f)

                logger.info(f"模型已保存: {filename}")

        except Exception as e:
            logger.error(f"模型保存失败: {e}")

    def cleanup(self):
        """清理资源"""
        # 关闭线程池
        self.executor.shutdown(wait=True)

        # 清理数据
        self.historical_data.clear()
        self.prediction_history.clear()

        logger.info("预测性分析器资源清理完成")
