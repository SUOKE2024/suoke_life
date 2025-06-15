#!/usr/bin/env python

"""
自适应学习系统 - 用户行为学习和个性化适应
包含行为模式识别、偏好学习、智能推荐、自适应调整等功能
"""

import logging
import time
import warnings
from collections import Counter, deque
from dataclasses import dataclass
from enum import Enum
from typing import Any

warnings.filterwarnings("ignore")

# 可选的科学计算库导入
try:
    from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier
    from sklearn.metrics import accuracy_score, mean_squared_error
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import LabelEncoder, StandardScaler

    ADAPTIVE_LEARNING_AVAILABLE = True
except ImportError as e:
    # 如果没有安装科学计算库，使用简化版本
    ADAPTIVE_LEARNING_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"自适应学习库未安装，将使用简化版本: {e}")

    # 创建简化的替代类
    class np:
        @staticmethod
        def array(data):
            return list(data)

        @staticmethod
        def mean(data):
            return sum(data) / len(data) if data else 0

        @staticmethod
        def std(data):
            if not data:
                return 0
            mean_val = sum(data) / len(data)
            return (sum((x - mean_val) ** 2 for x in data) / len(data)) ** 0.5

    class pd:
        class DataFrame:
            def __init__(self, data=None):
                self.data = data or []
                self.empty = len(self.data) == 0
                self.columns = []
                if self.data and isinstance(self.data[0], dict):
                    self.columns = list(self.data[0].keys())

            def __len__(self) -> None:
                return len(self.data)

            def __getitem__(self, key):
                class MockSeries:
                    def __init__(self, data):
                        self.data = data

                    def size(self) -> None:
                        return len(self.data)

                    def nlargest(self, n):
                        class MockIndex:
                            def tolist(self) -> None:
                                return list(range(min(n, len(self.data))))

                        return type("obj", (), {"index": MockIndex()})()

                    def groupby(self, by):
                        return self

                    def max(self) -> None:
                        return max(self.data) if self.data else 0

                    def dt(self) -> None:
                        class MockDt:
                            hour = [0] * len(self.data)
                            dayofweek = [0] * len(self.data)
                            month = [1] * len(self.data)

                        return MockDt()

                return MockSeries(self.data)

            def groupby(self, by):
                return self

        @staticmethod
        def to_datetime(data, unit=None):
            return data

        class Series:
            def __init__(self, data):
                self.data = data

    # 简化的sklearn替代
    class RandomForestClassifier:
        def __init__(self, **kwargs):
            self.feature_importances_ = [0.5, 0.3, 0.2]

        def fit(self, X, y):
            return self

        def predict(self, X):
            return [0] * len(X)

        def predict_proba(self, X):
            return [[0.5, 0.5]] * len(X)

    class GradientBoostingRegressor:
        def __init__(self, **kwargs):
            self.feature_importances_ = [0.5, 0.3, 0.2]

        def fit(self, X, y):
            return self

        def predict(self, X):
            return [0.0] * len(X)

    def train_test_split(*args, **kwargs):
        return (
            args[0][: len(args[0]) // 2],
            args[0][len(args[0]) // 2 :],
            args[1][: len(args[1]) // 2],
            args[1][len(args[1]) // 2 :],
        )

    def accuracy_score(y_true, y_pred):
        return 0.8

    def mean_squared_error(y_true, y_pred):
        return 0.1


logger = logging.getLogger(__name__)


class LearningType(Enum):
    """学习类型枚举"""

    SUPERVISED = "supervised"  # 监督学习
    UNSUPERVISED = "unsupervised"  # 无监督学习
    REINFORCEMENT = "reinforcement"  # 强化学习
    TRANSFER = "transfer"  # 迁移学习
    ONLINE = "online"  # 在线学习


class AdaptationType(Enum):
    """适应类型枚举"""

    INTERFACE = "interface"  # 界面适应
    BEHAVIOR = "behavior"  # 行为适应
    PREFERENCE = "preference"  # 偏好适应
    PERFORMANCE = "performance"  # 性能适应
    ACCESSIBILITY = "accessibility"  # 无障碍适应


class RecommendationType(Enum):
    """推荐类型枚举"""

    CONTENT = "content"  # 内容推荐
    ACTION = "action"  # 动作推荐
    SETTING = "setting"  # 设置推荐
    FEATURE = "feature"  # 功能推荐
    OPTIMIZATION = "optimization"  # 优化推荐


@dataclass
class UserProfile:
    """用户画像"""

    user_id: str
    demographics: dict[str, Any]
    preferences: dict[str, Any]
    behavior_patterns: dict[str, Any]
    accessibility_needs: dict[str, Any]
    learning_style: dict[str, Any]
    interaction_history: list[dict[str, Any]]
    created_at: float
    updated_at: float
    confidence_score: float = 0.0


@dataclass
class BehaviorPattern:
    """行为模式"""

    pattern_id: str
    pattern_type: str
    description: str
    frequency: float
    confidence: float
    context: dict[str, Any]
    triggers: list[str]
    outcomes: list[str]
    temporal_info: dict[str, Any]
    user_segments: list[str]


@dataclass
class LearningResult:
    """学习结果"""

    learning_id: str
    learning_type: LearningType
    model_type: str
    accuracy: float
    confidence: float
    features_used: list[str]
    training_data_size: int
    model_parameters: dict[str, Any]
    validation_metrics: dict[str, Any]
    timestamp: float


@dataclass
class Recommendation:
    """推荐结果"""

    recommendation_id: str
    user_id: str
    recommendation_type: RecommendationType
    content: dict[str, Any]
    confidence: float
    reasoning: list[str]
    expected_benefit: str
    priority: int
    expiry_time: float | None
    context: dict[str, Any]
    timestamp: float


class BehaviorAnalyzer:
    """行为分析器"""

    def __init__(self) -> None:
        self.behavior_models = {}
        self.pattern_cache = {}
        self.analysis_stats = {
            "patterns_discovered": 0,
            "behaviors_analyzed": 0,
            "models_trained": 0,
        }

    async def analyze_user_behavior(
        self, user_id: str, interaction_data: list[dict[str, Any]]
    ) -> list[BehaviorPattern]:
        """分析用户行为模式"""
        if not interaction_data:
            return []

        try:
            # 转换为DataFrame
            df = pd.DataFrame(interaction_data)

            # 时间序列分析
            temporal_patterns = await self._analyze_temporal_patterns(df)

            # 序列模式挖掘
            sequence_patterns = await self._mine_sequence_patterns(df)

            # 频率模式分析
            frequency_patterns = await self._analyze_frequency_patterns(df)

            # 上下文模式分析
            context_patterns = await self._analyze_context_patterns(df)

            # 合并所有模式
            all_patterns = []
            all_patterns.extend(temporal_patterns)
            all_patterns.extend(sequence_patterns)
            all_patterns.extend(frequency_patterns)
            all_patterns.extend(context_patterns)

            # 更新统计信息
            self.analysis_stats["patterns_discovered"] += len(all_patterns)
            self.analysis_stats["behaviors_analyzed"] += len(interaction_data)

            logger.info(f"用户 {user_id} 行为分析完成，发现 {len(all_patterns)} 个模式")

            return all_patterns

        except Exception as e:
            logger.error(f"行为分析失败: {e!s}")
            return []

    async def _analyze_temporal_patterns(
        self, df: pd.DataFrame
    ) -> list[BehaviorPattern]:
        """分析时间模式"""
        patterns = []

        if "timestamp" not in df.columns:
            return patterns

        try:
            # 转换时间戳
            df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")
            df["hour"] = df["datetime"].dt.hour
            df["day_of_week"] = df["datetime"].dt.dayofweek
            df["month"] = df["datetime"].dt.month

            # 分析小时模式
            hourly_activity = df.groupby("hour").size()
            peak_hours = hourly_activity.nlargest(3).index.tolist()

            if len(peak_hours) > 0:
                pattern = BehaviorPattern(
                    pattern_id=f"temporal_hourly_{int(time.time())}",
                    pattern_type="temporal_hourly",
                    description=f"用户在 {peak_hours} 时最活跃",
                    frequency=float(hourly_activity.max() / len(df)),
                    confidence=0.8,
                    context={"peak_hours": peak_hours},
                    triggers=["time_of_day"],
                    outcomes=["increased_activity"],
                    temporal_info={
                        "pattern_type": "hourly",
                        "peak_times": peak_hours,
                        "activity_distribution": hourly_activity.to_dict(),
                    },
                    user_segments=["time_sensitive_users"],
                )
                patterns.append(pattern)

            # 分析周模式
            weekly_activity = df.groupby("day_of_week").size()
            peak_days = weekly_activity.nlargest(2).index.tolist()

            if len(peak_days) > 0:
                day_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
                peak_day_names = [day_names[day] for day in peak_days]

                pattern = BehaviorPattern(
                    pattern_id=f"temporal_weekly_{int(time.time())}",
                    pattern_type="temporal_weekly",
                    description=f"用户在 {peak_day_names} 最活跃",
                    frequency=float(weekly_activity.max() / len(df)),
                    confidence=0.7,
                    context={"peak_days": peak_days, "peak_day_names": peak_day_names},
                    triggers=["day_of_week"],
                    outcomes=["increased_activity"],
                    temporal_info={
                        "pattern_type": "weekly",
                        "peak_days": peak_days,
                        "activity_distribution": weekly_activity.to_dict(),
                    },
                    user_segments=["weekly_pattern_users"],
                )
                patterns.append(pattern)

        except Exception as e:
            logger.error(f"时间模式分析失败: {e!s}")

        return patterns

    async def _mine_sequence_patterns(self, df: pd.DataFrame) -> list[BehaviorPattern]:
        """挖掘序列模式"""
        patterns = []

        if "action_type" not in df.columns:
            return patterns

        try:
            # 按时间排序
            df_sorted = df.sort_values("timestamp") if "timestamp" in df.columns else df

            # 提取动作序列
            actions = df_sorted["action_type"].tolist()

            # 寻找常见的3-gram序列
            sequence_length = 3
            sequences = []

            for i in range(len(actions) - sequence_length + 1):
                sequence = tuple(actions[i : i + sequence_length])
                sequences.append(sequence)

            # 统计序列频率
            sequence_counts = Counter(sequences)

            # 创建模式
            for sequence, count in sequence_counts.most_common(5):
                if count >= 2:  # 至少出现2次
                    support = count / len(sequences)

                    pattern = BehaviorPattern(
                        pattern_id=f"sequence_{hash(sequence)}_{int(time.time())}",
                        pattern_type="action_sequence",
                        description=f"用户经常执行序列: {' -> '.join(sequence)}",
                        frequency=support,
                        confidence=min(0.9, support * 2),  # 简化的置信度计算
                        context={"sequence": list(sequence), "count": count},
                        triggers=[sequence[0]],
                        outcomes=[sequence[-1]],
                        temporal_info={"sequence_length": sequence_length},
                        user_segments=["sequence_pattern_users"],
                    )
                    patterns.append(pattern)

        except Exception as e:
            logger.error(f"序列模式挖掘失败: {e!s}")

        return patterns

    async def _analyze_frequency_patterns(
        self, df: pd.DataFrame
    ) -> list[BehaviorPattern]:
        """分析频率模式"""
        patterns = []

        try:
            # 分析动作频率
            if "action_type" in df.columns:
                action_counts = df["action_type"].value_counts()

                # 找出高频动作
                total_actions = len(df)
                for action, count in action_counts.head(3).items():
                    frequency = count / total_actions

                    if frequency > 0.1:  # 频率超过10%
                        pattern = BehaviorPattern(
                            pattern_id=f"frequency_{action}_{int(time.time())}",
                            pattern_type="high_frequency_action",
                            description=f"用户频繁执行动作: {action}",
                            frequency=frequency,
                            confidence=0.8,
                            context={
                                "action": action,
                                "count": count,
                                "percentage": frequency,
                            },
                            triggers=["user_preference"],
                            outcomes=["repeated_action"],
                            temporal_info={},
                            user_segments=["frequent_action_users"],
                        )
                        patterns.append(pattern)

            # 分析会话长度模式
            if "session_id" in df.columns:
                session_lengths = df.groupby("session_id").size()
                avg_session_length = session_lengths.mean()

                if avg_session_length > 5:  # 平均会话长度超过5个动作
                    pattern = BehaviorPattern(
                        pattern_id=f"session_length_{int(time.time())}",
                        pattern_type="session_length",
                        description=f"用户平均会话长度: {avg_session_length:.1f} 个动作",
                        frequency=1.0,
                        confidence=0.7,
                        context={
                            "avg_length": avg_session_length,
                            "distribution": session_lengths.describe().to_dict(),
                        },
                        triggers=["session_start"],
                        outcomes=["extended_usage"],
                        temporal_info={},
                        user_segments=["long_session_users"],
                    )
                    patterns.append(pattern)

        except Exception as e:
            logger.error(f"频率模式分析失败: {e!s}")

        return patterns

    async def _analyze_context_patterns(
        self, df: pd.DataFrame
    ) -> list[BehaviorPattern]:
        """分析上下文模式"""
        patterns = []

        try:
            # 分析设备类型模式
            if "device_type" in df.columns:
                device_usage = df["device_type"].value_counts()
                primary_device = device_usage.index[0]
                device_preference = device_usage.iloc[0] / len(df)

                if device_preference > 0.7:  # 70%以上使用同一设备
                    pattern = BehaviorPattern(
                        pattern_id=f"device_preference_{int(time.time())}",
                        pattern_type="device_preference",
                        description=f"用户偏好使用 {primary_device}",
                        frequency=device_preference,
                        confidence=0.8,
                        context={
                            "preferred_device": primary_device,
                            "usage_rate": device_preference,
                        },
                        triggers=["device_availability"],
                        outcomes=["consistent_experience"],
                        temporal_info={},
                        user_segments=["device_loyal_users"],
                    )
                    patterns.append(pattern)

            # 分析位置模式
            if "location" in df.columns:
                location_usage = df["location"].value_counts()
                if len(location_usage) > 0:
                    primary_location = location_usage.index[0]
                    location_preference = location_usage.iloc[0] / len(df)

                    if location_preference > 0.6:  # 60%以上在同一位置
                        pattern = BehaviorPattern(
                            pattern_id=f"location_preference_{int(time.time())}",
                            pattern_type="location_preference",
                            description=f"用户主要在 {primary_location} 使用",
                            frequency=location_preference,
                            confidence=0.7,
                            context={
                                "preferred_location": primary_location,
                                "usage_rate": location_preference,
                            },
                            triggers=["location_context"],
                            outcomes=["location_based_usage"],
                            temporal_info={},
                            user_segments=["location_consistent_users"],
                        )
                        patterns.append(pattern)

        except Exception as e:
            logger.error(f"上下文模式分析失败: {e!s}")

        return patterns


class PreferenceLearner:
    """偏好学习器"""

    def __init__(self) -> None:
        self.preference_models = {}
        self.feature_encoders = {}
        self.learning_history = deque(maxlen=1000)

    async def learn_user_preferences(
        self,
        user_id: str,
        interaction_data: list[dict[str, Any]],
        feedback_data: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """学习用户偏好"""
        try:
            # 准备训练数据
            training_data = await self._prepare_training_data(
                interaction_data, feedback_data
            )

            if not training_data:
                return {}

            # 特征工程
            features, labels = await self._extract_features_and_labels(training_data)

            if len(features) == 0:
                return {}

            # 训练偏好模型
            preference_model = await self._train_preference_model(
                user_id, features, labels
            )

            # 提取偏好规则
            preference_rules = await self._extract_preference_rules(
                preference_model, features, labels
            )

            # 计算偏好强度
            preference_strengths = await self._calculate_preference_strengths(
                training_data
            )

            preferences = {
                "model": preference_model,
                "rules": preference_rules,
                "strengths": preference_strengths,
                "feature_importance": await self._get_feature_importance(
                    preference_model
                ),
                "confidence": await self._calculate_model_confidence(
                    preference_model, features, labels
                ),
            }

            # 保存学习结果
            learning_result = LearningResult(
                learning_id=f"preference_{user_id}_{int(time.time())}",
                learning_type=LearningType.SUPERVISED,
                model_type="preference_classifier",
                accuracy=preferences["confidence"],
                confidence=preferences["confidence"],
                features_used=(
                    list(features.columns) if hasattr(features, "columns") else []
                ),
                training_data_size=len(training_data),
                model_parameters={},
                validation_metrics={},
                timestamp=time.time(),
            )

            self.learning_history.append(learning_result)

            logger.info(
                f"用户 {user_id} 偏好学习完成，置信度: {preferences['confidence']:.3f}"
            )

            return preferences

        except Exception as e:
            logger.error(f"偏好学习失败: {e!s}")
            return {}

    async def _prepare_training_data(
        self,
        interaction_data: list[dict[str, Any]],
        feedback_data: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """准备训练数据"""
        training_data = []

        # 创建反馈映射
        feedback_map = {}
        for feedback in feedback_data:
            if "interaction_id" in feedback and "rating" in feedback:
                feedback_map[feedback["interaction_id"]] = feedback["rating"]

        # 合并交互数据和反馈数据
        for interaction in interaction_data:
            if "interaction_id" in interaction:
                interaction_id = interaction["interaction_id"]
                if interaction_id in feedback_map:
                    training_item = interaction.copy()
                    training_item["feedback_rating"] = feedback_map[interaction_id]
                    training_item["preference_label"] = (
                        1 if feedback_map[interaction_id] >= 3 else 0
                    )  # 3分以上为正偏好
                    training_data.append(training_item)

        return training_data

    async def _extract_features_and_labels(
        self, training_data: list[dict[str, Any]]
    ) -> tuple[pd.DataFrame, pd.Series]:
        """提取特征和标签"""
        if not training_data:
            return pd.DataFrame(), pd.Series()

        df = pd.DataFrame(training_data)

        # 特征列
        feature_columns = []

        # 数值特征
        numeric_features = ["duration", "click_count", "scroll_distance", "time_spent"]
        for col in numeric_features:
            if col in df.columns:
                feature_columns.append(col)

        # 分类特征编码
        categorical_features = ["action_type", "device_type", "location", "context"]
        for col in categorical_features:
            if col in df.columns:
                # 使用标签编码
                encoder_key = f"{col}_encoder"
                if encoder_key not in self.feature_encoders:
                    self.feature_encoders[encoder_key] = LabelEncoder()
                    df[f"{col}_encoded"] = self.feature_encoders[
                        encoder_key
                    ].fit_transform(df[col].astype(str))
                else:
                    # 处理新的类别
                    try:
                        df[f"{col}_encoded"] = self.feature_encoders[
                            encoder_key
                        ].transform(df[col].astype(str))
                    except ValueError:
                        # 有新类别，重新训练编码器
                        self.feature_encoders[encoder_key] = LabelEncoder()
                        df[f"{col}_encoded"] = self.feature_encoders[
                            encoder_key
                        ].fit_transform(df[col].astype(str))

                feature_columns.append(f"{col}_encoded")

        # 时间特征
        if "timestamp" in df.columns:
            df["hour"] = pd.to_datetime(df["timestamp"], unit="s").dt.hour
            df["day_of_week"] = pd.to_datetime(df["timestamp"], unit="s").dt.dayofweek
            feature_columns.extend(["hour", "day_of_week"])

        # 提取特征和标签
        features = df[feature_columns].fillna(0)
        labels = (
            df["preference_label"] if "preference_label" in df.columns else pd.Series()
        )

        return features, labels

    async def _train_preference_model(
        self, user_id: str, features: pd.DataFrame, labels: pd.Series
    ) -> Any | None:
        """训练偏好模型"""
        if len(features) < 5 or len(labels) < 5:
            return None

        try:
            # 分割训练和测试数据
            X_train, X_test, y_train, y_test = train_test_split(
                features, labels, test_size=0.2, random_state=42
            )

            # 训练随机森林分类器
            model = RandomForestClassifier(
                n_estimators=50, max_depth=10, random_state=42
            )

            model.fit(X_train, y_train)

            # 验证模型
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)

            logger.info(f"用户 {user_id} 偏好模型训练完成，准确率: {accuracy:.3f}")

            # 保存模型
            self.preference_models[user_id] = {
                "model": model,
                "accuracy": accuracy,
                "features": list(features.columns),
                "trained_at": time.time(),
            }

            return model

        except Exception as e:
            logger.error(f"偏好模型训练失败: {e!s}")
            return None

    async def _extract_preference_rules(
        self, model: Any, features: pd.DataFrame, labels: pd.Series
    ) -> list[dict[str, Any]]:
        """提取偏好规则"""
        rules = []

        if model is None or len(features) == 0:
            return rules

        try:
            # 基于特征重要性提取规则
            feature_importance = model.feature_importances_
            feature_names = features.columns

            # 获取最重要的特征
            important_features = []
            for i, importance in enumerate(feature_importance):
                if importance > 0.1:  # 重要性阈值
                    important_features.append((feature_names[i], importance))

            # 按重要性排序
            important_features.sort(key=lambda x: x[1], reverse=True)

            # 为每个重要特征创建规则
            for feature_name, importance in important_features[:5]:  # 前5个最重要的特征
                # 分析特征值与偏好的关系
                feature_values = features[feature_name]
                positive_mask = labels == 1

                if positive_mask.sum() > 0:
                    positive_mean = feature_values[positive_mask].mean()
                    negative_mean = (
                        feature_values[~positive_mask].mean()
                        if (~positive_mask).sum() > 0
                        else 0
                    )

                    if positive_mean > negative_mean:
                        rule = {
                            "feature": feature_name,
                            "condition": f"{feature_name} > {negative_mean:.2f}",
                            "preference": "positive",
                            "confidence": importance,
                            "description": f"用户偏好较高的 {feature_name} 值",
                        }
                    else:
                        rule = {
                            "feature": feature_name,
                            "condition": f"{feature_name} < {positive_mean:.2f}",
                            "preference": "positive",
                            "confidence": importance,
                            "description": f"用户偏好较低的 {feature_name} 值",
                        }

                    rules.append(rule)

        except Exception as e:
            logger.error(f"偏好规则提取失败: {e!s}")

        return rules

    async def _calculate_preference_strengths(
        self, training_data: list[dict[str, Any]]
    ) -> dict[str, float]:
        """计算偏好强度"""
        strengths = {}

        try:
            df = pd.DataFrame(training_data)

            if "feedback_rating" not in df.columns:
                return strengths

            # 按不同维度计算偏好强度
            dimensions = ["action_type", "device_type", "location"]

            for dimension in dimensions:
                if dimension in df.columns:
                    # 计算每个类别的平均评分
                    category_ratings = df.groupby(dimension)["feedback_rating"].mean()

                    # 转换为偏好强度（0-1范围）
                    max_rating = df["feedback_rating"].max()
                    min_rating = df["feedback_rating"].min()

                    if max_rating > min_rating:
                        for category, rating in category_ratings.items():
                            normalized_strength = (rating - min_rating) / (
                                max_rating - min_rating
                            )
                            strengths[f"{dimension}_{category}"] = float(
                                normalized_strength
                            )

        except Exception as e:
            logger.error(f"偏好强度计算失败: {e!s}")

        return strengths

    async def _get_feature_importance(self, model: Any) -> dict[str, float]:
        """获取特征重要性"""
        if model is None or not hasattr(model, "feature_importances_"):
            return {}

        try:
            # 获取特征重要性
            importance_dict = {}
            if hasattr(model, "feature_names_in_"):
                feature_names = model.feature_names_in_
            else:
                feature_names = [
                    f"feature_{i}" for i in range(len(model.feature_importances_))
                ]

            for i, importance in enumerate(model.feature_importances_):
                if i < len(feature_names):
                    importance_dict[feature_names[i]] = float(importance)

            return importance_dict

        except Exception as e:
            logger.error(f"特征重要性获取失败: {e!s}")
            return {}

    async def _calculate_model_confidence(
        self, model: Any, features: pd.DataFrame, labels: pd.Series
    ) -> float:
        """计算模型置信度"""
        if model is None or len(features) == 0 or len(labels) == 0:
            return 0.0

        try:
            # 使用交叉验证计算置信度
            predictions = model.predict(features)
            accuracy = accuracy_score(labels, predictions)

            # 考虑数据量对置信度的影响
            data_size_factor = min(1.0, len(features) / 100)  # 100个样本为满分

            confidence = accuracy * data_size_factor
            return float(confidence)

        except Exception as e:
            logger.error(f"模型置信度计算失败: {e!s}")
            return 0.0


class RecommendationEngine:
    """推荐引擎"""

    def __init__(self) -> None:
        self.recommendation_models = {}
        self.user_similarity_cache = {}
        self.item_similarity_cache = {}
        self.recommendation_history = deque(maxlen=1000)

    async def generate_recommendations(
        self,
        user_id: str,
        user_profile: UserProfile,
        context: dict[str, Any],
        recommendation_type: RecommendationType,
        limit: int = 10,
    ) -> list[Recommendation]:
        """生成推荐"""
        try:
            recommendations = []

            if recommendation_type == RecommendationType.CONTENT:
                recommendations = await self._generate_content_recommendations(
                    user_id, user_profile, context, limit
                )
            elif recommendation_type == RecommendationType.ACTION:
                recommendations = await self._generate_action_recommendations(
                    user_id, user_profile, context, limit
                )
            elif recommendation_type == RecommendationType.SETTING:
                recommendations = await self._generate_setting_recommendations(
                    user_id, user_profile, context, limit
                )
            elif recommendation_type == RecommendationType.FEATURE:
                recommendations = await self._generate_feature_recommendations(
                    user_id, user_profile, context, limit
                )
            elif recommendation_type == RecommendationType.OPTIMIZATION:
                recommendations = await self._generate_optimization_recommendations(
                    user_id, user_profile, context, limit
                )

            # 保存推荐历史
            for rec in recommendations:
                self.recommendation_history.append(rec)

            logger.info(
                f"为用户 {user_id} 生成 {len(recommendations)} 个 {recommendation_type.value} 推荐"
            )

            return recommendations

        except Exception as e:
            logger.error(f"推荐生成失败: {e!s}")
            return []

    async def _generate_content_recommendations(
        self,
        user_id: str,
        user_profile: UserProfile,
        context: dict[str, Any],
        limit: int,
    ) -> list[Recommendation]:
        """生成内容推荐"""
        recommendations = []

        try:
            # 基于用户偏好的内容推荐
            preferences = user_profile.preferences

            # 健康内容推荐
            if preferences.get("health_focus", 0) > 0.5:
                rec = Recommendation(
                    recommendation_id=f"content_health_{int(time.time())}",
                    user_id=user_id,
                    recommendation_type=RecommendationType.CONTENT,
                    content={
                        "type": "health_article",
                        "title": "个性化健康建议",
                        "description": "基于您的健康数据的个性化建议",
                        "category": "health",
                    },
                    confidence=0.8,
                    reasoning=["用户对健康内容感兴趣", "基于历史偏好"],
                    expected_benefit="提升健康意识",
                    priority=1,
                    expiry_time=time.time() + 86400,  # 24小时后过期
                    context=context,
                    timestamp=time.time(),
                )
                recommendations.append(rec)

            # 中医养生内容推荐
            if preferences.get("tcm_interest", 0) > 0.3:
                rec = Recommendation(
                    recommendation_id=f"content_tcm_{int(time.time())}",
                    user_id=user_id,
                    recommendation_type=RecommendationType.CONTENT,
                    content={
                        "type": "tcm_guide",
                        "title": "中医养生指南",
                        "description": "适合您体质的中医养生方法",
                        "category": "tcm",
                    },
                    confidence=0.7,
                    reasoning=["用户对中医感兴趣", "个性化体质分析"],
                    expected_benefit="改善体质",
                    priority=2,
                    expiry_time=time.time() + 172800,  # 48小时后过期
                    context=context,
                    timestamp=time.time(),
                )
                recommendations.append(rec)

        except Exception as e:
            logger.error(f"内容推荐生成失败: {e!s}")

        return recommendations[:limit]

    async def _generate_action_recommendations(
        self,
        user_id: str,
        user_profile: UserProfile,
        context: dict[str, Any],
        limit: int,
    ) -> list[Recommendation]:
        """生成动作推荐"""
        recommendations = []

        try:
            # 基于行为模式的动作推荐
            behavior_patterns = user_profile.behavior_patterns

            # 运动提醒推荐
            if context.get("time_of_day") == "morning":
                rec = Recommendation(
                    recommendation_id=f"action_exercise_{int(time.time())}",
                    user_id=user_id,
                    recommendation_type=RecommendationType.ACTION,
                    content={
                        "type": "exercise_reminder",
                        "action": "start_morning_exercise",
                        "description": "开始晨练",
                        "duration": "15分钟",
                    },
                    confidence=0.8,
                    reasoning=["早晨是运动的好时机", "基于健康目标"],
                    expected_benefit="提升一天的精神状态",
                    priority=1,
                    expiry_time=time.time() + 3600,  # 1小时后过期
                    context=context,
                    timestamp=time.time(),
                )
                recommendations.append(rec)

            # 休息提醒推荐
            if (
                behavior_patterns.get("continuous_usage_time", 0) > 60
            ):  # 连续使用超过60分钟
                rec = Recommendation(
                    recommendation_id=f"action_rest_{int(time.time())}",
                    user_id=user_id,
                    recommendation_type=RecommendationType.ACTION,
                    content={
                        "type": "rest_reminder",
                        "action": "take_break",
                        "description": "建议休息一下",
                        "duration": "5分钟",
                    },
                    confidence=0.9,
                    reasoning=["连续使用时间过长", "保护视力和健康"],
                    expected_benefit="缓解疲劳",
                    priority=1,
                    expiry_time=time.time() + 1800,  # 30分钟后过期
                    context=context,
                    timestamp=time.time(),
                )
                recommendations.append(rec)

        except Exception as e:
            logger.error(f"动作推荐生成失败: {e!s}")

        return recommendations[:limit]

    async def _generate_setting_recommendations(
        self,
        user_id: str,
        user_profile: UserProfile,
        context: dict[str, Any],
        limit: int,
    ) -> list[Recommendation]:
        """生成设置推荐"""
        recommendations = []

        try:
            accessibility_needs = user_profile.accessibility_needs

            # 字体大小调整推荐
            if accessibility_needs.get("vision_impairment", False):
                rec = Recommendation(
                    recommendation_id=f"setting_font_{int(time.time())}",
                    user_id=user_id,
                    recommendation_type=RecommendationType.SETTING,
                    content={
                        "type": "font_size_adjustment",
                        "setting": "font_size",
                        "recommended_value": "large",
                        "description": "建议使用大字体",
                    },
                    confidence=0.9,
                    reasoning=["用户有视觉障碍", "提升可读性"],
                    expected_benefit="改善阅读体验",
                    priority=1,
                    expiry_time=None,  # 设置推荐不过期
                    context=context,
                    timestamp=time.time(),
                )
                recommendations.append(rec)

            # 夜间模式推荐
            if context.get("time_of_day") == "night":
                rec = Recommendation(
                    recommendation_id=f"setting_dark_mode_{int(time.time())}",
                    user_id=user_id,
                    recommendation_type=RecommendationType.SETTING,
                    content={
                        "type": "theme_adjustment",
                        "setting": "theme",
                        "recommended_value": "dark",
                        "description": "建议使用夜间模式",
                    },
                    confidence=0.8,
                    reasoning=["当前是夜间时间", "保护视力"],
                    expected_benefit="减少眼部疲劳",
                    priority=2,
                    expiry_time=time.time() + 28800,  # 8小时后过期
                    context=context,
                    timestamp=time.time(),
                )
                recommendations.append(rec)

        except Exception as e:
            logger.error(f"设置推荐生成失败: {e!s}")

        return recommendations[:limit]

    async def _generate_feature_recommendations(
        self,
        user_id: str,
        user_profile: UserProfile,
        context: dict[str, Any],
        limit: int,
    ) -> list[Recommendation]:
        """生成功能推荐"""
        recommendations = []

        try:
            # 基于用户使用模式推荐新功能
            interaction_history = user_profile.interaction_history

            # 语音助手推荐
            if len(interaction_history) > 50 and not any(
                h.get("feature") == "voice_assistant" for h in interaction_history
            ):
                rec = Recommendation(
                    recommendation_id=f"feature_voice_{int(time.time())}",
                    user_id=user_id,
                    recommendation_type=RecommendationType.FEATURE,
                    content={
                        "type": "new_feature",
                        "feature": "voice_assistant",
                        "description": "尝试语音助手功能",
                        "benefits": ["免手操作", "提升效率"],
                    },
                    confidence=0.7,
                    reasoning=["用户使用频繁", "可能受益于语音功能"],
                    expected_benefit="提升使用便利性",
                    priority=2,
                    expiry_time=time.time() + 604800,  # 7天后过期
                    context=context,
                    timestamp=time.time(),
                )
                recommendations.append(rec)

            # 健康监测功能推荐
            if user_profile.preferences.get("health_focus", 0) > 0.6:
                rec = Recommendation(
                    recommendation_id=f"feature_health_monitor_{int(time.time())}",
                    user_id=user_id,
                    recommendation_type=RecommendationType.FEATURE,
                    content={
                        "type": "new_feature",
                        "feature": "health_monitoring",
                        "description": "启用健康监测功能",
                        "benefits": ["实时健康跟踪", "个性化建议"],
                    },
                    confidence=0.8,
                    reasoning=["用户关注健康", "符合使用偏好"],
                    expected_benefit="全面健康管理",
                    priority=1,
                    expiry_time=time.time() + 259200,  # 3天后过期
                    context=context,
                    timestamp=time.time(),
                )
                recommendations.append(rec)

        except Exception as e:
            logger.error(f"功能推荐生成失败: {e!s}")

        return recommendations[:limit]

    async def _generate_optimization_recommendations(
        self,
        user_id: str,
        user_profile: UserProfile,
        context: dict[str, Any],
        limit: int,
    ) -> list[Recommendation]:
        """生成优化推荐"""
        recommendations = []

        try:
            # 基于使用模式的优化建议
            behavior_patterns = user_profile.behavior_patterns

            # 使用效率优化
            if (
                behavior_patterns.get("average_task_completion_time", 0) > 30
            ):  # 平均任务完成时间超过30秒
                rec = Recommendation(
                    recommendation_id=f"optimization_efficiency_{int(time.time())}",
                    user_id=user_id,
                    recommendation_type=RecommendationType.OPTIMIZATION,
                    content={
                        "type": "efficiency_optimization",
                        "optimization": "shortcut_usage",
                        "description": "学习使用快捷操作",
                        "methods": ["手势操作", "快捷键", "语音命令"],
                    },
                    confidence=0.8,
                    reasoning=["任务完成时间较长", "有优化空间"],
                    expected_benefit="提升操作效率",
                    priority=1,
                    expiry_time=time.time() + 432000,  # 5天后过期
                    context=context,
                    timestamp=time.time(),
                )
                recommendations.append(rec)

            # 个性化界面优化
            if len(user_profile.interaction_history) > 100:
                rec = Recommendation(
                    recommendation_id=f"optimization_interface_{int(time.time())}",
                    user_id=user_id,
                    recommendation_type=RecommendationType.OPTIMIZATION,
                    content={
                        "type": "interface_optimization",
                        "optimization": "layout_customization",
                        "description": "个性化界面布局",
                        "suggestions": ["常用功能前置", "隐藏不常用功能"],
                    },
                    confidence=0.7,
                    reasoning=["用户使用经验丰富", "可以个性化定制"],
                    expected_benefit="提升使用体验",
                    priority=2,
                    expiry_time=time.time() + 604800,  # 7天后过期
                    context=context,
                    timestamp=time.time(),
                )
                recommendations.append(rec)

        except Exception as e:
            logger.error(f"优化推荐生成失败: {e!s}")

        return recommendations[:limit]


class AdaptiveLearning:
    """自适应学习主类"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化自适应学习系统

        Args:
            config: 服务配置
        """
        self.config = config
        self.enabled = (
            config.get("adaptive_learning", {}).get("enabled", True)
            and ADAPTIVE_LEARNING_AVAILABLE
        )

        # 核心组件
        if ADAPTIVE_LEARNING_AVAILABLE:
            self.behavior_analyzer = BehaviorAnalyzer()
            self.preference_learner = PreferenceLearner()
            self.recommendation_engine = RecommendationEngine()
        else:
            self.behavior_analyzer = None
            self.preference_learner = None
            self.recommendation_engine = None

        # 用户画像存储
        self.user_profiles = {}

        # 学习统计
        self.learning_stats = {
            "users_analyzed": 0,
            "patterns_discovered": 0,
            "preferences_learned": 0,
            "recommendations_generated": 0,
            "adaptations_made": 0,
        }

        if ADAPTIVE_LEARNING_AVAILABLE:
            logger.info(f"自适应学习系统初始化完成 - 启用: {self.enabled} (完整功能)")
        else:
            logger.info(
                f"自适应学习系统初始化完成 - 启用: {self.enabled} (简化功能，缺少科学计算库)"
            )

    async def analyze_user_behavior(
        self, user_id: str, interaction_data: list[dict[str, Any]]
    ) -> list[BehaviorPattern]:
        """分析用户行为"""
        if not self.enabled:
            return []

        try:
            patterns = await self.behavior_analyzer.analyze_user_behavior(
                user_id, interaction_data
            )

            # 更新用户画像
            await self._update_user_profile(user_id, behavior_patterns=patterns)

            # 更新统计
            self.learning_stats["patterns_discovered"] += len(patterns)

            return patterns

        except Exception as e:
            logger.error(f"用户行为分析失败: {e!s}")
            return []

    async def learn_user_preferences(
        self,
        user_id: str,
        interaction_data: list[dict[str, Any]],
        feedback_data: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """学习用户偏好"""
        if not self.enabled:
            return {}

        try:
            preferences = await self.preference_learner.learn_user_preferences(
                user_id, interaction_data, feedback_data
            )

            # 更新用户画像
            await self._update_user_profile(user_id, preferences=preferences)

            # 更新统计
            self.learning_stats["preferences_learned"] += 1

            return preferences

        except Exception as e:
            logger.error(f"用户偏好学习失败: {e!s}")
            return {}

    async def generate_recommendations(
        self,
        user_id: str,
        recommendation_type: RecommendationType,
        context: dict[str, Any] | None = None,
        limit: int = 10,
    ) -> list[Recommendation]:
        """生成推荐"""
        if not self.enabled:
            return []

        try:
            # 获取用户画像
            user_profile = await self._get_user_profile(user_id)

            if not user_profile:
                logger.warning(f"用户 {user_id} 画像不存在")
                return []

            # 生成推荐
            recommendations = await self.recommendation_engine.generate_recommendations(
                user_id, user_profile, context or {}, recommendation_type, limit
            )

            # 更新统计
            self.learning_stats["recommendations_generated"] += len(recommendations)

            return recommendations

        except Exception as e:
            logger.error(f"推荐生成失败: {e!s}")
            return []

    async def adapt_system(
        self, user_id: str, adaptation_type: AdaptationType, context: dict[str, Any]
    ) -> dict[str, Any]:
        """系统自适应调整"""
        if not self.enabled:
            return {}

        try:
            user_profile = await self._get_user_profile(user_id)

            if not user_profile:
                return {}

            adaptations = {}

            if adaptation_type == AdaptationType.INTERFACE:
                adaptations = await self._adapt_interface(user_profile, context)
            elif adaptation_type == AdaptationType.BEHAVIOR:
                adaptations = await self._adapt_behavior(user_profile, context)
            elif adaptation_type == AdaptationType.PREFERENCE:
                adaptations = await self._adapt_preference(user_profile, context)
            elif adaptation_type == AdaptationType.PERFORMANCE:
                adaptations = await self._adapt_performance(user_profile, context)
            elif adaptation_type == AdaptationType.ACCESSIBILITY:
                adaptations = await self._adapt_accessibility(user_profile, context)

            # 更新统计
            if adaptations:
                self.learning_stats["adaptations_made"] += 1

            logger.info(f"用户 {user_id} 系统适应完成: {adaptation_type.value}")

            return adaptations

        except Exception as e:
            logger.error(f"系统适应失败: {e!s}")
            return {}

    async def _update_user_profile(self, user_id: str, **kwargs) -> None:
        """更新用户画像"""
        try:
            if user_id not in self.user_profiles:
                # 创建新的用户画像
                self.user_profiles[user_id] = UserProfile(
                    user_id=user_id,
                    demographics={},
                    preferences={},
                    behavior_patterns={},
                    accessibility_needs={},
                    learning_style={},
                    interaction_history=[],
                    created_at=time.time(),
                    updated_at=time.time(),
                )
                self.learning_stats["users_analyzed"] += 1

            profile = self.user_profiles[user_id]

            # 更新各个字段
            for key, value in kwargs.items():
                if hasattr(profile, key):
                    if key == "behavior_patterns" and isinstance(value, list):
                        # 行为模式特殊处理
                        pattern_dict = {}
                        for pattern in value:
                            pattern_dict[pattern.pattern_id] = {
                                "type": pattern.pattern_type,
                                "description": pattern.description,
                                "frequency": pattern.frequency,
                                "confidence": pattern.confidence,
                            }
                        profile.behavior_patterns.update(pattern_dict)
                    elif key == "preferences" and isinstance(value, dict):
                        profile.preferences.update(value)
                    else:
                        setattr(profile, key, value)

            # 更新时间戳
            profile.updated_at = time.time()

            # 重新计算置信度分数
            profile.confidence_score = await self._calculate_profile_confidence(profile)

        except Exception as e:
            logger.error(f"用户画像更新失败: {e!s}")

    async def _get_user_profile(self, user_id: str) -> UserProfile | None:
        """获取用户画像"""
        return self.user_profiles.get(user_id)

    async def _calculate_profile_confidence(self, profile: UserProfile) -> float:
        """计算用户画像置信度"""
        confidence_factors = []

        # 交互历史数量因子
        interaction_factor = min(1.0, len(profile.interaction_history) / 100)
        confidence_factors.append(interaction_factor)

        # 行为模式数量因子
        pattern_factor = min(1.0, len(profile.behavior_patterns) / 10)
        confidence_factors.append(pattern_factor)

        # 偏好数据完整性因子
        preference_factor = min(1.0, len(profile.preferences) / 20)
        confidence_factors.append(preference_factor)

        # 时间因子（数据新鲜度）
        time_since_update = time.time() - profile.updated_at
        time_factor = max(0.1, 1.0 - time_since_update / 604800)  # 一周内为满分
        confidence_factors.append(time_factor)

        return float(np.mean(confidence_factors))

    async def _adapt_interface(
        self, profile: UserProfile, context: dict[str, Any]
    ) -> dict[str, Any]:
        """界面适应"""
        adaptations = {}

        # 基于可访问性需求调整界面
        if profile.accessibility_needs.get("vision_impairment"):
            adaptations["font_size"] = "large"
            adaptations["contrast"] = "high"
            adaptations["color_scheme"] = "accessible"

        # 基于使用偏好调整布局
        if profile.preferences.get("simple_interface", 0) > 0.7:
            adaptations["layout"] = "simplified"
            adaptations["advanced_features"] = "hidden"

        return adaptations

    async def _adapt_behavior(
        self, profile: UserProfile, context: dict[str, Any]
    ) -> dict[str, Any]:
        """行为适应"""
        adaptations = {}

        # 基于行为模式调整交互方式
        behavior_patterns = profile.behavior_patterns

        # 如果用户经常使用语音功能
        if any("voice" in str(pattern) for pattern in behavior_patterns.values()):
            adaptations["default_input"] = "voice"
            adaptations["voice_shortcuts"] = "enabled"

        # 如果用户偏好快速操作
        if any(
            pattern.get("frequency", 0) > 0.8 for pattern in behavior_patterns.values()
        ):
            adaptations["animation_speed"] = "fast"
            adaptations["confirmation_dialogs"] = "minimal"

        return adaptations

    async def _adapt_preference(
        self, profile: UserProfile, context: dict[str, Any]
    ) -> dict[str, Any]:
        """偏好适应"""
        adaptations = {}

        preferences = profile.preferences

        # 内容偏好适应
        if preferences.get("health_focus", 0) > 0.6:
            adaptations["default_content"] = "health"
            adaptations["health_notifications"] = "enabled"

        if preferences.get("tcm_interest", 0) > 0.5:
            adaptations["tcm_features"] = "prominent"
            adaptations["tcm_recommendations"] = "enabled"

        return adaptations

    async def _adapt_performance(
        self, profile: UserProfile, context: dict[str, Any]
    ) -> dict[str, Any]:
        """性能适应"""
        adaptations = {}

        # 基于设备性能和使用模式调整
        device_type = context.get("device_type", "unknown")

        if device_type == "low_end":
            adaptations["animation_quality"] = "low"
            adaptations["background_sync"] = "limited"
            adaptations["cache_size"] = "small"

        # 基于网络状况调整
        network_quality = context.get("network_quality", "good")

        if network_quality == "poor":
            adaptations["image_quality"] = "compressed"
            adaptations["auto_sync"] = "disabled"
            adaptations["offline_mode"] = "enabled"

        return adaptations

    async def _adapt_accessibility(
        self, profile: UserProfile, context: dict[str, Any]
    ) -> dict[str, Any]:
        """无障碍适应"""
        adaptations = {}

        accessibility_needs = profile.accessibility_needs

        # 视觉障碍适应
        if accessibility_needs.get("vision_impairment"):
            adaptations["screen_reader"] = "enabled"
            adaptations["voice_feedback"] = "enabled"
            adaptations["high_contrast"] = "enabled"

        # 听觉障碍适应
        if accessibility_needs.get("hearing_impairment"):
            adaptations["visual_alerts"] = "enabled"
            adaptations["subtitles"] = "enabled"
            adaptations["vibration_feedback"] = "enabled"

        # 运动障碍适应
        if accessibility_needs.get("motor_impairment"):
            adaptations["large_touch_targets"] = "enabled"
            adaptations["gesture_alternatives"] = "enabled"
            adaptations["voice_control"] = "enabled"

        return adaptations

    def get_learning_stats(self) -> dict[str, Any]:
        """获取学习统计信息"""
        stats = {
            "enabled": self.enabled,
            "user_profiles_count": len(self.user_profiles),
            **self.learning_stats,
        }

        # 在简化模式下，组件可能为None
        if self.behavior_analyzer:
            stats["behavior_analyzer_stats"] = self.behavior_analyzer.analysis_stats
        else:
            stats["behavior_analyzer_stats"] = {}

        if self.preference_learner:
            stats["learning_history_size"] = len(
                self.preference_learner.learning_history
            )
        else:
            stats["learning_history_size"] = 0

        if self.recommendation_engine:
            stats["recommendation_history_size"] = len(
                self.recommendation_engine.recommendation_history
            )
        else:
            stats["recommendation_history_size"] = 0

        return stats

    async def export_user_profile(self, user_id: str) -> dict[str, Any] | None:
        """导出用户画像"""
        profile = await self._get_user_profile(user_id)

        if not profile:
            return None

        return {
            "user_id": profile.user_id,
            "demographics": profile.demographics,
            "preferences": profile.preferences,
            "behavior_patterns": profile.behavior_patterns,
            "accessibility_needs": profile.accessibility_needs,
            "learning_style": profile.learning_style,
            "interaction_count": len(profile.interaction_history),
            "created_at": profile.created_at,
            "updated_at": profile.updated_at,
            "confidence_score": profile.confidence_score,
        }
