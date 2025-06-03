"""
小克智能体学习模块
实现持续学习和自我优化功能
"""

import asyncio
import json
import logging
import pickle
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import joblib
from sklearn.cluster import DBSCAN, KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    silhouette_score,
)
from sklearn.model_selection import GridSearchCV, cross_val_score, train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import LabelEncoder, MinMaxScaler, StandardScaler
from sklearn.svm import SVC

from ..domain.models import ConstitutionType, ResourceType

logger = logging.getLogger(__name__)

class LearningType(Enum):
    """学习类型"""

    SUPERVISED = "supervised"  # 监督学习
    UNSUPERVISED = "unsupervised"  # 无监督学习
    REINFORCEMENT = "reinforcement"  # 强化学习
    TRANSFER = "transfer"  # 迁移学习
    ONLINE = "online"  # 在线学习
    SEMI_SUPERVISED = "semi_supervised"  # 半监督学习
    ACTIVE = "active"  # 主动学习
    FEDERATED = "federated"  # 联邦学习
    META = "meta"  # 元学习

class ModelType(Enum):
    """模型类型"""

    CONSTITUTION_CLASSIFIER = "constitution_classifier"
    RESOURCE_RECOMMENDER = "resource_recommender"
    APPOINTMENT_PREDICTOR = "appointment_predictor"
    SATISFACTION_PREDICTOR = "satisfaction_predictor"
    DEMAND_FORECASTER = "demand_forecaster"
    SYMPTOM_ANALYZER = "symptom_analyzer"
    TREATMENT_OPTIMIZER = "treatment_optimizer"
    RISK_ASSESSOR = "risk_assessor"
    QUALITY_PREDICTOR = "quality_predictor"
    COST_OPTIMIZER = "cost_optimizer"
    OUTCOME_PREDICTOR = "outcome_predictor"
    RESOURCE_UTILIZATION = "resource_utilization"

class AlgorithmType(Enum):
    """算法类型"""

    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    LOGISTIC_REGRESSION = "logistic_regression"
    SVM = "svm"
    NEURAL_NETWORK = "neural_network"
    KMEANS = "kmeans"
    DBSCAN = "dbscan"
    SGD = "sgd"
    NAIVE_BAYES = "naive_bayes"
    DECISION_TREE = "decision_tree"
    ENSEMBLE = "ensemble"
    DEEP_LEARNING = "deep_learning"

class FeatureType(Enum):
    """特征类型"""

    DEMOGRAPHIC = "demographic"  # 人口统计学特征
    CLINICAL = "clinical"  # 临床特征
    BEHAVIORAL = "behavioral"  # 行为特征
    TEMPORAL = "temporal"  # 时间特征
    ENVIRONMENTAL = "environmental"  # 环境特征
    SOCIAL = "social"  # 社会特征
    ECONOMIC = "economic"  # 经济特征
    GENETIC = "genetic"  # 遗传特征

class DataQuality(Enum):
    """数据质量等级"""

    EXCELLENT = "excellent"  # 优秀 (>95%)
    GOOD = "good"  # 良好 (85-95%)
    FAIR = "fair"  # 一般 (70-85%)
    POOR = "poor"  # 较差 (50-70%)
    UNUSABLE = "unusable"  # 不可用 (<50%)

@dataclass
class LearningMetrics:
    """学习指标"""

    model_type: ModelType
    algorithm_type: AlgorithmType
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    training_time: float
    prediction_time: float
    data_size: int
    feature_count: int
    cross_val_score: float
    auc_score: Optional[float] = None
    confusion_matrix: Optional[np.ndarray] = None
    classification_report: Optional[str] = None
    feature_importance: Optional[Dict[str, float]] = None
    learning_curve: Optional[List[float]] = None
    validation_curve: Optional[List[float]] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class LearningData:
    """学习数据"""

    data_id: str
    features: np.ndarray
    labels: np.ndarray
    feature_names: List[str]
    feature_types: List[FeatureType]
    metadata: Dict[str, Any]
    timestamp: datetime
    data_source: str
    quality_score: float = 1.0
    is_validated: bool = False
    preprocessing_steps: List[str] = field(default_factory=list)
    outliers_removed: int = 0
    missing_values_handled: int = 0

@dataclass
class ModelPerformance:
    """模型性能"""

    model_name: str
    version: str
    algorithm_type: AlgorithmType
    metrics: LearningMetrics
    validation_results: Dict[str, float]
    feature_importance: Dict[str, float]
    hyperparameters: Dict[str, Any]
    training_data_size: int
    model_size_mb: float
    inference_speed_ms: float
    memory_usage_mb: float
    robustness_score: float = 0.0
    interpretability_score: float = 0.0
    fairness_metrics: Dict[str, float] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class LearningTask:
    """学习任务"""

    task_id: str
    task_type: LearningType
    model_type: ModelType
    algorithm_type: AlgorithmType
    data_source: str
    priority: int
    status: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    progress: float = 0.0
    estimated_duration: Optional[timedelta] = None

@dataclass
class FeatureEngineering:
    """特征工程配置"""

    feature_selection_method: str
    dimensionality_reduction: bool
    feature_scaling: bool
    feature_encoding: Dict[str, str]
    polynomial_features: bool
    interaction_features: bool
    temporal_features: bool
    custom_transformations: List[str]

@dataclass
class ModelEnsemble:
    """模型集成"""

    ensemble_id: str
    base_models: List[str]
    ensemble_method: str  # voting, stacking, bagging
    weights: List[float]
    meta_learner: Optional[str] = None
    performance: Optional[ModelPerformance] = None

class LearningModule:
    """
    小克智能体学习模块

    实现多种学习算法和持续优化机制
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.learning_rate = config.get("learning_rate", 0.01)
        self.memory_size = config.get("memory_size", 10000)
        self.model_save_path = Path(config.get("model_save_path", "models"))
        self.auto_retrain_threshold = config.get("auto_retrain_threshold", 0.1)
        self.max_model_versions = config.get("max_model_versions", 5)
        self.feature_selection_k = config.get("feature_selection_k", 20)
        self.ensemble_size = config.get("ensemble_size", 3)

        # 创建模型保存目录
        self.model_save_path.mkdir(parents=True, exist_ok=True)

        # 学习数据存储
        self.learning_data: Dict[str, List[LearningData]] = {}
        self.models: Dict[ModelType, Dict[str, Any]] = {}
        self.scalers: Dict[ModelType, StandardScaler] = {}
        self.encoders: Dict[str, LabelEncoder] = {}
        self.feature_selectors: Dict[ModelType, Any] = {}
        self.dimensionality_reducers: Dict[ModelType, PCA] = {}

        # 性能跟踪
        self.performance_history: List[ModelPerformance] = []
        self.learning_metrics: Dict[ModelType, LearningMetrics] = {}
        self.model_versions: Dict[ModelType, List[str]] = {}
        self.model_ensembles: Dict[ModelType, ModelEnsemble] = {}

        # 在线学习缓冲区
        self.online_buffer: Dict[str, List[Dict[str, Any]]] = {}
        self.buffer_size = config.get("buffer_size", 1000)
        self.batch_learning_threshold = config.get("batch_learning_threshold", 100)

        # 学习任务队列
        self.learning_queue = asyncio.Queue()
        self.active_tasks: Dict[str, LearningTask] = {}
        self.is_learning = False
        self.max_concurrent_tasks = config.get("max_concurrent_tasks", 3)

        # 特征工程
        self.feature_extractors: Dict[str, callable] = {}
        self.feature_engineering_configs: Dict[ModelType, FeatureEngineering] = {}

        # 数据质量管理
        self.data_quality_thresholds = {
            "completeness": 0.8,
            "consistency": 0.9,
            "accuracy": 0.85,
            "timeliness": 0.9,
        }

        # 模型监控
        self.model_drift_detectors: Dict[ModelType, Any] = {}
        self.performance_monitors: Dict[ModelType, List[float]] = {}
        self.alert_thresholds = {
            "accuracy_drop": 0.05,
            "drift_score": 0.1,
            "latency_increase": 2.0,
        }

        # 学习统计
        self.learning_stats = {
            "total_training_sessions": 0,
            "total_predictions": 0,
            "average_accuracy": 0.0,
            "best_models": {},
            "learning_trends": [],
            "data_quality_trends": [],
            "model_performance_trends": {},
        }

        # 自动化配置
        self.auto_feature_engineering = config.get("auto_feature_engineering", True)
        self.auto_hyperparameter_tuning = config.get("auto_hyperparameter_tuning", True)
        self.auto_model_selection = config.get("auto_model_selection", True)
        self.auto_ensemble = config.get("auto_ensemble", True)

        logger.info("学习模块初始化完成")

    async def initialize(self):
        """初始化学习模块"""
        try:
            # 加载已保存的模型
            await self._load_saved_models()

            # 初始化编码器
            self._initialize_encoders()

            # 初始化特征提取器
            self._initialize_feature_extractors()

            # 初始化特征工程配置
            self._initialize_feature_engineering_configs()

            # 启动学习任务处理器
            asyncio.create_task(self._process_learning_queue())

            # 启动模型性能监控
            asyncio.create_task(self._monitor_model_performance())

            # 启动数据质量监控
            asyncio.create_task(self._monitor_data_quality())

            logger.info("学习模块初始化完成")

        except Exception as e:
            logger.error(f"学习模块初始化失败: {e}")
            raise

    async def _load_saved_models(self):
        """加载已保存的模型"""
        try:
            for model_type in ModelType:
                model_dir = self.model_save_path / model_type.value
                if model_dir.exists():
                    # 加载最新版本的模型
                    version_dirs = [d for d in model_dir.iterdir() if d.is_dir()]
                    if version_dirs:
                        latest_version = max(
                            version_dirs, key=lambda x: x.stat().st_mtime
                        )

                        model_file = latest_version / "model.joblib"
                        scaler_file = latest_version / "scaler.joblib"
                        metadata_file = latest_version / "metadata.json"

                        if model_file.exists():
                            model_data = {
                                "model": joblib.load(model_file),
                                "version": latest_version.name,
                                "loaded_at": datetime.now(),
                            }

                            if scaler_file.exists():
                                model_data["scaler"] = joblib.load(scaler_file)

                            if metadata_file.exists():
                                with open(metadata_file, "r") as f:
                                    model_data["metadata"] = json.load(f)

                            self.models[model_type] = model_data
                            logger.info(
                                f"加载模型: {model_type.value} v{latest_version.name}"
                            )

        except Exception as e:
            logger.error(f"加载模型失败: {e}")

    def _initialize_encoders(self):
        """初始化编码器"""
        # 体质类型编码器
        constitution_encoder = LabelEncoder()
        constitution_encoder.fit([c.value for c in ConstitutionType])
        self.encoders["constitution"] = constitution_encoder

        # 资源类型编码器
        resource_encoder = LabelEncoder()
        resource_encoder.fit([r.value for r in ResourceType])
        self.encoders["resource"] = resource_encoder

        # 症状编码器
        common_symptoms = [
            "头痛",
            "发热",
            "咳嗽",
            "乏力",
            "失眠",
            "食欲不振",
            "腹痛",
            "腹泻",
            "便秘",
            "心悸",
            "胸闷",
            "气短",
            "眩晕",
            "耳鸣",
            "视力模糊",
            "关节痛",
            "肌肉酸痛",
            "皮疹",
            "瘙痒",
            "水肿",
            "尿频",
            "尿急",
            "月经不调",
            "痛经",
        ]
        symptom_encoder = LabelEncoder()
        symptom_encoder.fit(common_symptoms)
        self.encoders["symptom"] = symptom_encoder

    def _initialize_feature_extractors(self):
        """初始化特征提取器"""
        self.feature_extractors = {
            "symptoms": self._encode_symptoms,
            "vital_signs": self._encode_vital_signs,
            "lifestyle": self._encode_lifestyle,
            "medical_history": self._encode_medical_history,
            "demographics": self._encode_demographics,
            "temporal": self._encode_temporal_features,
            "environmental": self._encode_environmental_features,
        }

    async def collect_learning_data(
        self,
        data_type: str,
        features: Dict[str, Any],
        label: Any,
        metadata: Dict[str, Any] = None,
    ):
        """收集学习数据"""
        try:
            data_id = str(uuid.uuid4())
            learning_data = {
                "data_id": data_id,
                "features": features,
                "label": label,
                "metadata": metadata or {},
                "timestamp": datetime.now(),
                "data_source": data_type,
                "quality_score": self._assess_data_quality(features, label),
            }

            # 添加到在线缓冲区
            if data_type not in self.online_buffer:
                self.online_buffer[data_type] = []

            self.online_buffer[data_type].append(learning_data)

            # 如果缓冲区满了，触发学习
            if len(self.online_buffer[data_type]) >= self.buffer_size:
                await self._trigger_online_learning(data_type)

            logger.debug(f"收集学习数据: {data_type}, 数据ID: {data_id}")

        except Exception as e:
            logger.error(f"收集学习数据失败: {e}")

    def _assess_data_quality(self, features: Dict[str, Any], label: Any) -> float:
        """评估数据质量"""
        quality_score = 1.0

        # 检查特征完整性
        if not features:
            quality_score *= 0.1
        else:
            missing_ratio = sum(1 for v in features.values() if v is None) / len(
                features
            )
            quality_score *= 1 - missing_ratio

        # 检查标签有效性
        if label is None:
            quality_score *= 0.1

        # 检查数据类型一致性
        try:
            for key, value in features.items():
                if value is not None:
                    # 尝试转换为数值类型
                    if isinstance(value, (int, float)):
                        continue
                    elif isinstance(value, str) and value.replace(".", "").isdigit():
                        continue
                    elif isinstance(value, (list, dict)):
                        continue
                    else:
                        quality_score *= 0.9
        except:
            quality_score *= 0.8

        return max(0.0, min(1.0, quality_score))

    async def _trigger_online_learning(self, data_type: str):
        """触发在线学习"""
        task_id = str(uuid.uuid4())
        task = LearningTask(
            task_id=task_id,
            task_type=LearningType.ONLINE,
            model_type=self._get_model_type_for_data(data_type),
            algorithm_type=AlgorithmType.SGD,  # 在线学习使用SGD
            data_source=data_type,
            priority=1,
            status="pending",
            created_at=datetime.now(),
        )

        await self.learning_queue.put(task)
        self.active_tasks[task_id] = task

        # 清空缓冲区
        self.online_buffer[data_type].clear()

    def _get_model_type_for_data(self, data_type: str) -> ModelType:
        """根据数据类型获取对应的模型类型"""
        mapping = {
            "constitution_analysis": ModelType.CONSTITUTION_CLASSIFIER,
            "resource_recommendation": ModelType.RESOURCE_RECOMMENDER,
            "appointment_booking": ModelType.APPOINTMENT_PREDICTOR,
            "satisfaction_feedback": ModelType.SATISFACTION_PREDICTOR,
            "demand_prediction": ModelType.DEMAND_FORECASTER,
            "symptom_analysis": ModelType.SYMPTOM_ANALYZER,
            "treatment_optimization": ModelType.TREATMENT_OPTIMIZER,
            "risk_assessment": ModelType.RISK_ASSESSOR,
        }
        return mapping.get(data_type, ModelType.CONSTITUTION_CLASSIFIER)

    async def train_model(
        self,
        model_type: ModelType,
        algorithm_type: AlgorithmType,
        training_data: List[Dict[str, Any]],
        validation_split: float = 0.2,
        hyperparameter_tuning: bool = True,
    ) -> ModelPerformance:
        """训练模型"""
        try:
            start_time = datetime.now()

            # 准备训练数据
            features, labels, feature_names = self._prepare_training_data(
                model_type, training_data
            )

            if len(features) == 0:
                raise ValueError("训练数据为空")

            # 数据预处理
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)

            # 分割训练和验证数据
            X_train, X_val, y_train, y_val = train_test_split(
                features_scaled, labels, test_size=validation_split, random_state=42
            )

            # 创建模型
            model = self._create_model(algorithm_type)

            # 超参数调优
            if hyperparameter_tuning:
                model = self._tune_hyperparameters(
                    model, algorithm_type, X_train, y_train
                )

            # 训练模型
            model.fit(X_train, y_train)

            # 预测和评估
            y_pred = model.predict(X_val)
            y_pred_proba = None
            if hasattr(model, "predict_proba"):
                y_pred_proba = model.predict_proba(X_val)

            # 计算指标
            metrics = self._calculate_metrics(
                model_type,
                algorithm_type,
                y_val,
                y_pred,
                y_pred_proba,
                len(features),
                len(feature_names),
                start_time,
            )

            # 交叉验证
            cv_scores = cross_val_score(model, features_scaled, labels, cv=5)
            metrics.cross_val_score = cv_scores.mean()

            # 特征重要性
            feature_importance = self._get_feature_importance(model, feature_names)

            # 保存模型
            version = await self._save_model(
                model_type,
                model,
                scaler,
                {
                    "algorithm_type": algorithm_type.value,
                    "feature_names": feature_names,
                    "training_data_size": len(features),
                    "metrics": metrics.__dict__,
                },
            )

            # 创建性能记录
            performance = ModelPerformance(
                model_name=f"{model_type.value}_{algorithm_type.value}",
                version=version,
                algorithm_type=algorithm_type,
                metrics=metrics,
                validation_results={
                    "cv_mean": cv_scores.mean(),
                    "cv_std": cv_scores.std(),
                    "val_accuracy": accuracy_score(y_val, y_pred),
                },
                feature_importance=feature_importance,
                hyperparameters=(
                    model.get_params() if hasattr(model, "get_params") else {}
                ),
                training_data_size=len(features),
                model_size_mb=self._calculate_model_size(model),
                inference_speed_ms=self._measure_inference_speed(model, X_val[:10]),
                memory_usage_mb=self._estimate_memory_usage(model),
            )

            # 更新模型存储
            self.models[model_type] = {
                "model": model,
                "scaler": scaler,
                "version": version,
                "metadata": {
                    "algorithm_type": algorithm_type.value,
                    "feature_names": feature_names,
                    "performance": performance.__dict__,
                },
            }

            self.scalers[model_type] = scaler
            self.performance_history.append(performance)
            self.learning_metrics[model_type] = metrics

            # 更新统计信息
            self.learning_stats["total_training_sessions"] += 1
            self.learning_stats["best_models"][model_type.value] = {
                "version": version,
                "accuracy": metrics.accuracy,
                "algorithm": algorithm_type.value,
            }

            logger.info(
                f"模型训练完成: {model_type.value}, 准确率: {metrics.accuracy:.4f}"
            )

            return performance

        except Exception as e:
            logger.error(f"模型训练失败: {e}")
            raise

    def _prepare_training_data(
        self, model_type: ModelType, training_data: List[Dict[str, Any]]
    ) -> Tuple[np.ndarray, List[Any], List[str]]:
        """准备训练数据"""
        if model_type == ModelType.CONSTITUTION_CLASSIFIER:
            return self._prepare_constitution_data(training_data)
        elif model_type == ModelType.RESOURCE_RECOMMENDER:
            return self._prepare_recommendation_data(training_data)
        elif model_type == ModelType.SYMPTOM_ANALYZER:
            return self._prepare_symptom_data(training_data)
        else:
            return self._prepare_generic_data(training_data)

    def _prepare_constitution_data(
        self, training_data: List[Dict[str, Any]]
    ) -> Tuple[np.ndarray, List[str], List[str]]:
        """准备体质分类数据"""
        features_list = []
        labels = []
        feature_names = []

        for data in training_data:
            if "features" not in data or "constitution_type" not in data:
                continue

            features_dict = data["features"]

            # 提取特征
            feature_vector = []

            # 症状特征
            symptoms = features_dict.get("symptoms", [])
            symptom_features = self._encode_symptoms(symptoms)
            feature_vector.extend(symptom_features)

            # 生理指标特征
            vital_signs = features_dict.get("vital_signs", {})
            vital_features = self._encode_vital_signs(vital_signs)
            feature_vector.extend(vital_features)

            # 生活方式特征
            lifestyle = features_dict.get("lifestyle", {})
            lifestyle_features = self._encode_lifestyle(lifestyle)
            feature_vector.extend(lifestyle_features)

            # 人口统计学特征
            demographics = features_dict.get("demographics", {})
            demo_features = self._encode_demographics(demographics)
            feature_vector.extend(demo_features)

            # 时间特征
            temporal_features = self._encode_temporal_features(data.get("timestamp"))
            feature_vector.extend(temporal_features)

            features_list.append(feature_vector)
            labels.append(data["constitution_type"])

        # 生成特征名称
        if not feature_names:
            feature_names = (
                [f"symptom_{i}" for i in range(24)]  # 24个症状特征
                + [f"vital_{i}" for i in range(8)]  # 8个生理指标
                + [f"lifestyle_{i}" for i in range(10)]  # 10个生活方式特征
                + [f"demo_{i}" for i in range(5)]  # 5个人口统计学特征
                + [f"temporal_{i}" for i in range(4)]  # 4个时间特征
            )

        return np.array(features_list), labels, feature_names

    def _encode_symptoms(self, symptoms: List[str]) -> List[float]:
        """编码症状特征"""
        # 预定义的24个常见症状
        common_symptoms = [
            "头痛",
            "发热",
            "咳嗽",
            "乏力",
            "失眠",
            "食欲不振",
            "腹痛",
            "腹泻",
            "便秘",
            "心悸",
            "胸闷",
            "气短",
            "眩晕",
            "耳鸣",
            "视力模糊",
            "关节痛",
            "肌肉酸痛",
            "皮疹",
            "瘙痒",
            "水肿",
            "尿频",
            "尿急",
            "月经不调",
            "痛经",
        ]

        # 创建症状向量
        symptom_vector = [0.0] * len(common_symptoms)

        for symptom in symptoms:
            if symptom in common_symptoms:
                idx = common_symptoms.index(symptom)
                symptom_vector[idx] = 1.0

        return symptom_vector

    def _encode_vital_signs(self, vital_signs: Dict[str, Any]) -> List[float]:
        """编码生理指标特征"""
        # 标准化生理指标
        features = []

        # 血压 (收缩压/舒张压)
        systolic = vital_signs.get("systolic_bp", 120)
        diastolic = vital_signs.get("diastolic_bp", 80)
        features.extend(
            [
                (systolic - 120) / 40,  # 标准化收缩压
                (diastolic - 80) / 20,  # 标准化舒张压
            ]
        )

        # 心率
        heart_rate = vital_signs.get("heart_rate", 70)
        features.append((heart_rate - 70) / 30)

        # 体温
        temperature = vital_signs.get("temperature", 36.5)
        features.append((temperature - 36.5) / 2)

        # BMI
        bmi = vital_signs.get("bmi", 22)
        features.append((bmi - 22) / 8)

        # 血糖
        glucose = vital_signs.get("glucose", 5.5)
        features.append((glucose - 5.5) / 3)

        # 血氧饱和度
        spo2 = vital_signs.get("spo2", 98)
        features.append((spo2 - 98) / 5)

        # 呼吸频率
        respiratory_rate = vital_signs.get("respiratory_rate", 16)
        features.append((respiratory_rate - 16) / 8)

        return features

    def _encode_lifestyle(self, lifestyle: Dict[str, Any]) -> List[float]:
        """编码生活方式特征"""
        features = []

        # 睡眠质量 (1-5分)
        sleep_quality = lifestyle.get("sleep_quality", 3)
        features.append((sleep_quality - 3) / 2)

        # 运动频率 (每周次数)
        exercise_frequency = lifestyle.get("exercise_frequency", 3)
        features.append((exercise_frequency - 3) / 4)

        # 饮食规律性 (1-5分)
        diet_regularity = lifestyle.get("diet_regularity", 3)
        features.append((diet_regularity - 3) / 2)

        # 压力水平 (1-5分)
        stress_level = lifestyle.get("stress_level", 3)
        features.append((stress_level - 3) / 2)

        # 吸烟状态 (0-不吸烟, 1-偶尔, 2-经常)
        smoking = lifestyle.get("smoking", 0)
        features.append(smoking / 2)

        # 饮酒频率 (0-不饮酒, 1-偶尔, 2-经常)
        drinking = lifestyle.get("drinking", 0)
        features.append(drinking / 2)

        # 工作强度 (1-5分)
        work_intensity = lifestyle.get("work_intensity", 3)
        features.append((work_intensity - 3) / 2)

        # 社交活动 (1-5分)
        social_activity = lifestyle.get("social_activity", 3)
        features.append((social_activity - 3) / 2)

        # 屏幕时间 (小时/天)
        screen_time = lifestyle.get("screen_time", 6)
        features.append((screen_time - 6) / 6)

        # 户外活动时间 (小时/天)
        outdoor_time = lifestyle.get("outdoor_time", 2)
        features.append((outdoor_time - 2) / 3)

        return features

    def _encode_demographics(self, demographics: Dict[str, Any]) -> List[float]:
        """编码人口统计学特征"""
        features = []

        # 年龄
        age = demographics.get("age", 35)
        features.append((age - 35) / 30)

        # 性别 (0-女, 1-男)
        gender = 1 if demographics.get("gender", "female") == "male" else 0
        features.append(gender)

        # 教育水平 (1-5分)
        education = demographics.get("education_level", 3)
        features.append((education - 3) / 2)

        # 收入水平 (1-5分)
        income = demographics.get("income_level", 3)
        features.append((income - 3) / 2)

        # 居住环境 (1-5分，1-农村，5-大城市)
        residence = demographics.get("residence_type", 3)
        features.append((residence - 3) / 2)

        return features

    def _encode_temporal_features(self, timestamp: datetime = None) -> List[float]:
        """编码时间特征"""
        if timestamp is None:
            timestamp = datetime.now()

        features = []

        # 季节 (春夏秋冬: 0-3)
        month = timestamp.month
        season = (month - 1) // 3
        features.append(season / 3)

        # 月份 (1-12)
        features.append((month - 6.5) / 5.5)

        # 星期几 (0-6)
        weekday = timestamp.weekday()
        features.append(weekday / 6)

        # 小时 (0-23)
        hour = timestamp.hour
        features.append((hour - 12) / 12)

        return features

    def _encode_medical_history(self, medical_history: Dict[str, Any]) -> List[float]:
        """编码病史特征"""
        features = []

        # 慢性病数量
        chronic_diseases = medical_history.get("chronic_diseases", [])
        features.append(min(len(chronic_diseases), 5) / 5)

        # 过敏史
        allergies = medical_history.get("allergies", [])
        features.append(min(len(allergies), 3) / 3)

        # 手术史
        surgeries = medical_history.get("surgeries", [])
        features.append(min(len(surgeries), 3) / 3)

        # 家族病史
        family_history = medical_history.get("family_history", [])
        features.append(min(len(family_history), 5) / 5)

        # 用药史
        medications = medical_history.get("medications", [])
        features.append(min(len(medications), 5) / 5)

        return features

    def _encode_environmental_features(
        self, environmental: Dict[str, Any]
    ) -> List[float]:
        """编码环境特征"""
        features = []

        # 空气质量指数
        aqi = environmental.get("aqi", 100)
        features.append((aqi - 100) / 200)

        # 温度
        temperature = environmental.get("temperature", 20)
        features.append((temperature - 20) / 20)

        # 湿度
        humidity = environmental.get("humidity", 60)
        features.append((humidity - 60) / 40)

        # 气压
        pressure = environmental.get("pressure", 1013)
        features.append((pressure - 1013) / 50)

        return features

    def _prepare_recommendation_data(
        self, training_data: List[Dict[str, Any]]
    ) -> Tuple[np.ndarray, List[int], List[str]]:
        """准备推荐数据"""
        features_list = []
        labels = []

        for data in training_data:
            if "user_features" not in data or "recommended_resource" not in data:
                continue

            user_features = data["user_features"]

            # 用户特征向量
            feature_vector = []

            # 体质类型
            constitution = user_features.get("constitution_type", "balanced")
            constitution_encoded = self.encoders["constitution"].transform(
                [constitution]
            )[0]
            feature_vector.append(constitution_encoded)

            # 症状特征
            symptoms = user_features.get("symptoms", [])
            symptom_features = self._encode_symptoms(symptoms)
            feature_vector.extend(symptom_features)

            # 历史偏好
            preferences = user_features.get("preferences", {})
            pref_features = [
                preferences.get("prefer_tcm", 0.5),
                preferences.get("prefer_modern", 0.5),
                preferences.get("price_sensitivity", 0.5),
                preferences.get("distance_sensitivity", 0.5),
            ]
            feature_vector.extend(pref_features)

            features_list.append(feature_vector)

            # 推荐的资源类型
            resource_type = data["recommended_resource"]
            resource_encoded = self.encoders["resource"].transform([resource_type])[0]
            labels.append(resource_encoded)

        feature_names = (
            ["constitution"]
            + [f"symptom_{i}" for i in range(24)]
            + [
                "prefer_tcm",
                "prefer_modern",
                "price_sensitivity",
                "distance_sensitivity",
            ]
        )

        return np.array(features_list), labels, feature_names

    def _prepare_symptom_data(
        self, training_data: List[Dict[str, Any]]
    ) -> Tuple[np.ndarray, List[str], List[str]]:
        """准备症状分析数据"""
        features_list = []
        labels = []

        for data in training_data:
            if "patient_data" not in data or "primary_symptom" not in data:
                continue

            patient_data = data["patient_data"]

            # 患者特征向量
            feature_vector = []

            # 基本信息
            age = patient_data.get("age", 35)
            gender = 1 if patient_data.get("gender") == "male" else 0
            feature_vector.extend([age / 100, gender])

            # 生理指标
            vital_signs = patient_data.get("vital_signs", {})
            vital_features = self._encode_vital_signs(vital_signs)
            feature_vector.extend(vital_features)

            # 症状描述特征
            symptom_description = patient_data.get("symptom_description", "")
            desc_features = self._encode_symptom_description(symptom_description)
            feature_vector.extend(desc_features)

            features_list.append(feature_vector)
            labels.append(data["primary_symptom"])

        feature_names = (
            ["age", "gender"]
            + [f"vital_{i}" for i in range(8)]
            + [f"desc_{i}" for i in range(10)]
        )

        return np.array(features_list), labels, feature_names

    def _encode_symptom_description(self, description: str) -> List[float]:
        """编码症状描述"""
        # 简单的关键词匹配特征
        keywords = [
            "疼痛",
            "酸痛",
            "胀痛",
            "刺痛",
            "隐痛",
            "急性",
            "慢性",
            "间歇",
            "持续",
            "反复",
        ]

        features = []
        for keyword in keywords:
            features.append(1.0 if keyword in description else 0.0)

        return features

    def _prepare_generic_data(
        self, training_data: List[Dict[str, Any]]
    ) -> Tuple[np.ndarray, List[Any], List[str]]:
        """准备通用数据"""
        features_list = []
        labels = []
        feature_names = []

        for data in training_data:
            if "features" not in data or "label" not in data:
                continue

            features_dict = data["features"]
            feature_vector = []

            # 将字典特征转换为向量
            for key, value in features_dict.items():
                if isinstance(value, (int, float)):
                    feature_vector.append(value)
                elif isinstance(value, bool):
                    feature_vector.append(1.0 if value else 0.0)
                elif isinstance(value, str):
                    # 简单的字符串编码
                    feature_vector.append(hash(value) % 1000 / 1000)
                elif isinstance(value, list):
                    feature_vector.append(len(value))

            if feature_vector:
                features_list.append(feature_vector)
                labels.append(data["label"])

                if not feature_names:
                    feature_names = list(features_dict.keys())

        return np.array(features_list), labels, feature_names

    def _create_model(self, algorithm_type: AlgorithmType):
        """创建模型"""
        if algorithm_type == AlgorithmType.RANDOM_FOREST:
            return RandomForestClassifier(
                n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
            )
        elif algorithm_type == AlgorithmType.GRADIENT_BOOSTING:
            return GradientBoostingClassifier(
                n_estimators=100, learning_rate=0.1, max_depth=6, random_state=42
            )
        elif algorithm_type == AlgorithmType.LOGISTIC_REGRESSION:
            return LogisticRegression(random_state=42, max_iter=1000)
        elif algorithm_type == AlgorithmType.SVM:
            return SVC(kernel="rbf", probability=True, random_state=42)
        elif algorithm_type == AlgorithmType.NEURAL_NETWORK:
            return MLPClassifier(
                hidden_layer_sizes=(100, 50), max_iter=500, random_state=42
            )
        elif algorithm_type == AlgorithmType.SGD:
            return SGDClassifier(loss="log", random_state=42)
        else:
            return RandomForestClassifier(random_state=42)

    def _tune_hyperparameters(
        self, model, algorithm_type: AlgorithmType, X_train, y_train
    ):
        """超参数调优"""
        param_grids = {
            AlgorithmType.RANDOM_FOREST: {
                "n_estimators": [50, 100, 200],
                "max_depth": [5, 10, 15],
                "min_samples_split": [2, 5, 10],
            },
            AlgorithmType.GRADIENT_BOOSTING: {
                "n_estimators": [50, 100, 150],
                "learning_rate": [0.05, 0.1, 0.2],
                "max_depth": [3, 6, 9],
            },
            AlgorithmType.LOGISTIC_REGRESSION: {
                "C": [0.1, 1.0, 10.0],
                "penalty": ["l1", "l2"],
                "solver": ["liblinear", "saga"],
            },
        }

        if algorithm_type in param_grids:
            grid_search = GridSearchCV(
                model, param_grids[algorithm_type], cv=3, scoring="accuracy", n_jobs=-1
            )
            grid_search.fit(X_train, y_train)
            return grid_search.best_estimator_

        return model

    def _calculate_metrics(
        self,
        model_type: ModelType,
        algorithm_type: AlgorithmType,
        y_true,
        y_pred,
        y_pred_proba,
        data_size: int,
        feature_count: int,
        start_time: datetime,
    ) -> LearningMetrics:
        """计算评估指标"""
        training_time = (datetime.now() - start_time).total_seconds()

        # 基本指标
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average="weighted", zero_division=0)
        recall = recall_score(y_true, y_pred, average="weighted", zero_division=0)
        f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)

        # 预测时间（估算）
        prediction_time = training_time / len(y_true) * 1000  # 毫秒

        # 混淆矩阵
        conf_matrix = confusion_matrix(y_true, y_pred)

        # 分类报告
        class_report = classification_report(y_true, y_pred, zero_division=0)

        return LearningMetrics(
            model_type=model_type,
            algorithm_type=algorithm_type,
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1,
            training_time=training_time,
            prediction_time=prediction_time,
            data_size=data_size,
            feature_count=feature_count,
            cross_val_score=0.0,  # 将在后续设置
            confusion_matrix=conf_matrix,
            classification_report=class_report,
        )

    def _get_feature_importance(
        self, model, feature_names: List[str]
    ) -> Dict[str, float]:
        """获取特征重要性"""
        importance_dict = {}

        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
            for i, importance in enumerate(importances):
                if i < len(feature_names):
                    importance_dict[feature_names[i]] = float(importance)
        elif hasattr(model, "coef_"):
            # 对于线性模型，使用系数的绝对值
            coefs = (
                np.abs(model.coef_[0])
                if len(model.coef_.shape) > 1
                else np.abs(model.coef_)
            )
            for i, coef in enumerate(coefs):
                if i < len(feature_names):
                    importance_dict[feature_names[i]] = float(coef)

        return importance_dict

    def _calculate_model_size(self, model) -> float:
        """计算模型大小（MB）"""
        try:
            import sys

            return sys.getsizeof(pickle.dumps(model)) / (1024 * 1024)
        except:
            return 0.0

    def _measure_inference_speed(self, model, sample_data) -> float:
        """测量推理速度（毫秒）"""
        try:
            start_time = datetime.now()
            model.predict(sample_data)
            end_time = datetime.now()
            return (end_time - start_time).total_seconds() * 1000
        except:
            return 0.0

    def _estimate_memory_usage(self, model) -> float:
        """估算内存使用（MB）"""
        try:
            import sys

            return sys.getsizeof(model) / (1024 * 1024)
        except:
            return 0.0

    async def predict(
        self, model_type: ModelType, features: Dict[str, Any]
    ) -> Tuple[Any, float]:
        """进行预测"""
        try:
            if model_type not in self.models:
                raise ValueError(f"模型 {model_type.value} 未找到")

            model_data = self.models[model_type]
            model = model_data["model"]
            scaler = model_data.get("scaler")

            # 准备特征向量
            if model_type == ModelType.CONSTITUTION_CLASSIFIER:
                feature_vector = self._prepare_constitution_features(features)
            elif model_type == ModelType.RESOURCE_RECOMMENDER:
                feature_vector = self._prepare_recommendation_features(features)
            else:
                feature_vector = self._prepare_generic_features(features)

            # 特征缩放
            if scaler:
                feature_vector = scaler.transform([feature_vector])
            else:
                feature_vector = np.array([feature_vector])

            # 预测
            prediction = model.predict(feature_vector)[0]

            # 预测概率
            confidence = 0.5
            if hasattr(model, "predict_proba"):
                probabilities = model.predict_proba(feature_vector)[0]
                confidence = float(np.max(probabilities))

            # 更新统计
            self.learning_stats["total_predictions"] += 1

            logger.debug(
                f"预测完成: {model_type.value}, 结果: {prediction}, 置信度: {confidence}"
            )

            return prediction, confidence

        except Exception as e:
            logger.error(f"预测失败: {e}")
            raise

    def _prepare_constitution_features(self, features: Dict[str, Any]) -> List[float]:
        """准备体质分类特征"""
        feature_vector = []

        # 症状特征
        symptoms = features.get("symptoms", [])
        symptom_features = self._encode_symptoms(symptoms)
        feature_vector.extend(symptom_features)

        # 生理指标特征
        vital_signs = features.get("vital_signs", {})
        vital_features = self._encode_vital_signs(vital_signs)
        feature_vector.extend(vital_features)

        # 生活方式特征
        lifestyle = features.get("lifestyle", {})
        lifestyle_features = self._encode_lifestyle(lifestyle)
        feature_vector.extend(lifestyle_features)

        # 人口统计学特征
        demographics = features.get("demographics", {})
        demo_features = self._encode_demographics(demographics)
        feature_vector.extend(demo_features)

        # 时间特征
        temporal_features = self._encode_temporal_features()
        feature_vector.extend(temporal_features)

        return feature_vector

    def _prepare_recommendation_features(self, features: Dict[str, Any]) -> List[float]:
        """准备推荐特征"""
        feature_vector = []

        # 体质类型
        constitution = features.get("constitution_type", "balanced")
        try:
            constitution_encoded = self.encoders["constitution"].transform(
                [constitution]
            )[0]
        except:
            constitution_encoded = 0
        feature_vector.append(constitution_encoded)

        # 症状特征
        symptoms = features.get("symptoms", [])
        symptom_features = self._encode_symptoms(symptoms)
        feature_vector.extend(symptom_features)

        # 偏好特征
        preferences = features.get("preferences", {})
        pref_features = [
            preferences.get("prefer_tcm", 0.5),
            preferences.get("prefer_modern", 0.5),
            preferences.get("price_sensitivity", 0.5),
            preferences.get("distance_sensitivity", 0.5),
        ]
        feature_vector.extend(pref_features)

        return feature_vector

    def _prepare_generic_features(self, features: Dict[str, Any]) -> List[float]:
        """准备通用特征"""
        feature_vector = []

        for key, value in features.items():
            if isinstance(value, (int, float)):
                feature_vector.append(value)
            elif isinstance(value, bool):
                feature_vector.append(1.0 if value else 0.0)
            elif isinstance(value, str):
                feature_vector.append(hash(value) % 1000 / 1000)
            elif isinstance(value, list):
                feature_vector.append(len(value))

        return feature_vector

    async def online_learning_update(
        self, model_type: ModelType, new_data: List[Dict[str, Any]]
    ):
        """在线学习更新"""
        try:
            if model_type not in self.models:
                logger.warning(f"模型 {model_type.value} 不存在，跳过在线学习")
                return

            model_data = self.models[model_type]
            model = model_data["model"]

            # 检查模型是否支持在线学习
            if not hasattr(model, "partial_fit"):
                logger.info(f"模型 {model_type.value} 不支持在线学习，使用批量重训练")
                await self._batch_retrain(model_type, new_data)
                return

            # 准备新数据
            features, labels, _ = self._prepare_training_data(model_type, new_data)

            if len(features) == 0:
                return

            # 特征缩放
            scaler = model_data.get("scaler")
            if scaler:
                features = scaler.transform(features)

            # 在线学习更新
            model.partial_fit(features, labels)

            # 更新模型
            self.models[model_type]["model"] = model

            logger.info(
                f"在线学习更新完成: {model_type.value}, 新数据量: {len(features)}"
            )

        except Exception as e:
            logger.error(f"在线学习更新失败: {e}")

    async def _batch_retrain(
        self, model_type: ModelType, new_data: List[Dict[str, Any]]
    ):
        """批量重训练"""
        try:
            # 获取历史数据
            historical_data = self.learning_data.get(model_type.value, [])

            # 合并新旧数据
            all_data = []
            for data in historical_data:
                all_data.append(
                    {
                        "features": data.metadata.get("original_features", {}),
                        "label": data.metadata.get("original_label"),
                    }
                )

            for data in new_data:
                all_data.append(data)

            # 重新训练模型
            if len(all_data) > 10:  # 确保有足够的数据
                algorithm_type = AlgorithmType.RANDOM_FOREST  # 默认算法
                await self.train_model(model_type, algorithm_type, all_data)

        except Exception as e:
            logger.error(f"批量重训练失败: {e}")

    async def _process_learning_queue(self):
        """处理学习任务队列"""
        while True:
            try:
                # 获取学习任务
                task = await self.learning_queue.get()

                if task is None:  # 停止信号
                    break

                task.started_at = datetime.now()
                task.status = "running"

                try:
                    if task.task_type == LearningType.ONLINE:
                        # 在线学习任务
                        data = self.online_buffer.get(task.data_source, [])
                        await self.online_learning_update(task.model_type, data)

                    elif task.task_type == LearningType.SUPERVISED:
                        # 监督学习任务
                        # 这里可以添加更多的监督学习逻辑
                        pass

                    task.status = "completed"
                    task.completed_at = datetime.now()

                except Exception as e:
                    task.status = "failed"
                    task.error_message = str(e)
                    logger.error(f"学习任务失败: {task.task_id}, 错误: {e}")

                finally:
                    # 清理完成的任务
                    if task.task_id in self.active_tasks:
                        del self.active_tasks[task.task_id]

            except Exception as e:
                logger.error(f"处理学习队列失败: {e}")
                await asyncio.sleep(1)

    async def _monitor_model_performance(self):
        """监控模型性能"""
        while True:
            try:
                await asyncio.sleep(3600)  # 每小时检查一次

                for model_type, model_data in self.models.items():
                    # 检查模型性能是否下降
                    current_metrics = self.learning_metrics.get(model_type)
                    if (
                        current_metrics
                        and current_metrics.accuracy < self.auto_retrain_threshold
                    ):
                        logger.warning(f"模型 {model_type.value} 性能下降，触发重训练")
                        # 这里可以添加自动重训练逻辑

            except Exception as e:
                logger.error(f"性能监控失败: {e}")

    async def _save_model(
        self, model_type: ModelType, model, scaler, metadata: Dict[str, Any]
    ) -> str:
        """保存模型"""
        try:
            # 创建版本号
            version = datetime.now().strftime("%Y%m%d_%H%M%S")

            # 创建模型目录
            model_dir = self.model_save_path / model_type.value / version
            model_dir.mkdir(parents=True, exist_ok=True)

            # 保存模型
            model_file = model_dir / "model.joblib"
            joblib.dump(model, model_file)

            # 保存缩放器
            if scaler:
                scaler_file = model_dir / "scaler.joblib"
                joblib.dump(scaler, scaler_file)

            # 保存元数据
            metadata_file = model_dir / "metadata.json"
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2, default=str)

            # 管理模型版本数量
            await self._cleanup_old_versions(model_type)

            logger.info(f"模型保存成功: {model_type.value} v{version}")

            return version

        except Exception as e:
            logger.error(f"保存模型失败: {e}")
            raise

    async def _cleanup_old_versions(self, model_type: ModelType):
        """清理旧版本模型"""
        try:
            model_dir = self.model_save_path / model_type.value
            if not model_dir.exists():
                return

            # 获取所有版本目录
            version_dirs = [d for d in model_dir.iterdir() if d.is_dir()]

            # 按修改时间排序，保留最新的几个版本
            version_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            # 删除多余的版本
            for old_dir in version_dirs[self.max_model_versions :]:
                import shutil

                shutil.rmtree(old_dir)
                logger.info(f"删除旧版本模型: {old_dir}")

        except Exception as e:
            logger.error(f"清理旧版本失败: {e}")

    def get_learning_statistics(self) -> Dict[str, Any]:
        """获取学习统计信息"""
        stats = self.learning_stats.copy()

        # 添加当前模型信息
        stats["current_models"] = {}
        for model_type, model_data in self.models.items():
            stats["current_models"][model_type.value] = {
                "version": model_data.get("version", "unknown"),
                "algorithm": model_data.get("metadata", {}).get(
                    "algorithm_type", "unknown"
                ),
                "loaded_at": model_data.get("loaded_at", "unknown"),
            }

        # 添加性能指标
        stats["performance_metrics"] = {}
        for model_type, metrics in self.learning_metrics.items():
            stats["performance_metrics"][model_type.value] = {
                "accuracy": metrics.accuracy,
                "precision": metrics.precision,
                "recall": metrics.recall,
                "f1_score": metrics.f1_score,
                "last_updated": metrics.timestamp,
            }

        # 添加学习任务状态
        stats["active_tasks"] = len(self.active_tasks)
        stats["queue_size"] = self.learning_queue.qsize()

        # 计算平均准确率
        if self.learning_metrics:
            avg_accuracy = sum(
                m.accuracy for m in self.learning_metrics.values()
            ) / len(self.learning_metrics)
            stats["average_accuracy"] = avg_accuracy

        return stats

    async def evaluate_model_performance(
        self, model_type: ModelType, test_data: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """评估模型性能"""
        try:
            if model_type not in self.models:
                raise ValueError(f"模型 {model_type.value} 未找到")

            model_data = self.models[model_type]
            model = model_data["model"]
            scaler = model_data.get("scaler")

            # 准备测试数据
            features, labels, _ = self._prepare_training_data(model_type, test_data)

            if len(features) == 0:
                return {"error": "测试数据为空"}

            # 特征缩放
            if scaler:
                features = scaler.transform(features)

            # 预测
            predictions = model.predict(features)

            # 计算指标
            accuracy = accuracy_score(labels, predictions)
            precision = precision_score(
                labels, predictions, average="weighted", zero_division=0
            )
            recall = recall_score(
                labels, predictions, average="weighted", zero_division=0
            )
            f1 = f1_score(labels, predictions, average="weighted", zero_division=0)

            results = {
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
                "test_data_size": len(features),
            }

            logger.info(f"模型评估完成: {model_type.value}, 准确率: {accuracy:.4f}")

            return results

        except Exception as e:
            logger.error(f"模型评估失败: {e}")
            return {"error": str(e)}

    async def get_model_insights(self, model_type: ModelType) -> Dict[str, Any]:
        """获取模型洞察"""
        try:
            if model_type not in self.models:
                return {"error": f"模型 {model_type.value} 未找到"}

            model_data = self.models[model_type]
            metadata = model_data.get("metadata", {})

            insights = {
                "model_info": {
                    "type": model_type.value,
                    "algorithm": metadata.get("algorithm_type", "unknown"),
                    "version": model_data.get("version", "unknown"),
                    "feature_count": len(metadata.get("feature_names", [])),
                    "training_data_size": metadata.get("training_data_size", 0),
                },
                "performance": {},
                "feature_importance": {},
                "recommendations": [],
            }

            # 性能指标
            if model_type in self.learning_metrics:
                metrics = self.learning_metrics[model_type]
                insights["performance"] = {
                    "accuracy": metrics.accuracy,
                    "precision": metrics.precision,
                    "recall": metrics.recall,
                    "f1_score": metrics.f1_score,
                    "training_time": metrics.training_time,
                    "prediction_time": metrics.prediction_time,
                }

            # 特征重要性
            performance_records = [
                p
                for p in self.performance_history
                if p.model_name.startswith(model_type.value)
            ]
            if performance_records:
                latest_performance = max(
                    performance_records, key=lambda x: x.last_updated
                )
                insights["feature_importance"] = latest_performance.feature_importance

            # 优化建议
            recommendations = []
            if model_type in self.learning_metrics:
                metrics = self.learning_metrics[model_type]

                if metrics.accuracy < 0.8:
                    recommendations.append("考虑增加训练数据量或调整特征工程")

                if metrics.precision < 0.7:
                    recommendations.append(
                        "模型精确率较低，建议调整分类阈值或使用集成方法"
                    )

                if metrics.recall < 0.7:
                    recommendations.append(
                        "模型召回率较低，建议平衡数据集或调整损失函数"
                    )

                if metrics.training_time > 300:  # 5分钟
                    recommendations.append(
                        "训练时间较长，考虑特征选择或使用更简单的算法"
                    )

            insights["recommendations"] = recommendations

            return insights

        except Exception as e:
            logger.error(f"获取模型洞察失败: {e}")
            return {"error": str(e)}

    async def shutdown(self):
        """关闭学习模块"""
        try:
            # 停止学习任务处理器
            await self.learning_queue.put(None)

            # 保存当前状态
            for model_type, model_data in self.models.items():
                if "model" in model_data:
                    await self._save_model(
                        model_type,
                        model_data["model"],
                        model_data.get("scaler"),
                        model_data.get("metadata", {}),
                    )

            logger.info("学习模块已关闭")

        except Exception as e:
            logger.error(f"关闭学习模块失败: {e}")
