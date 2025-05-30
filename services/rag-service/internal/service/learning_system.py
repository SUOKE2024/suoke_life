"""
实时学习系统

从用户反馈、交互数据和系统性能中持续学习，优化RAG系统
"""

import asyncio
import json
import math
import pickle
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from collections import defaultdict, deque

import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
import redis.asyncio as redis
from loguru import logger


class FeedbackType(Enum):
    """反馈类型"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    CORRECTION = "correction"
    CLARIFICATION = "clarification"


class LearningObjective(Enum):
    """学习目标"""
    RELEVANCE = "relevance"          # 相关性
    ACCURACY = "accuracy"            # 准确性
    COMPLETENESS = "completeness"    # 完整性
    PERSONALIZATION = "personalization"  # 个性化
    RESPONSE_TIME = "response_time"  # 响应时间
    USER_SATISFACTION = "user_satisfaction"  # 用户满意度


class ModelType(Enum):
    """模型类型"""
    RETRIEVAL_RANKING = "retrieval_ranking"
    GENERATION_QUALITY = "generation_quality"
    QUERY_UNDERSTANDING = "query_understanding"
    PERSONALIZATION = "personalization"
    RESPONSE_ROUTING = "response_routing"


@dataclass
class UserFeedback:
    """用户反馈"""
    id: str
    user_id: str
    session_id: str
    query: str
    response: str
    feedback_type: FeedbackType
    rating: float  # 1-5分
    specific_feedback: str
    metadata: Dict[str, Any]
    timestamp: datetime


@dataclass
class InteractionData:
    """交互数据"""
    id: str
    user_id: str
    session_id: str
    query: str
    response: str
    response_time: float
    retrieval_results: List[Dict[str, Any]]
    generation_metadata: Dict[str, Any]
    user_engagement: Dict[str, Any]
    timestamp: datetime


@dataclass
class LearningExample:
    """学习样本"""
    id: str
    features: Dict[str, Any]
    target: float
    objective: LearningObjective
    weight: float
    created_at: datetime


@dataclass
class ModelPerformance:
    """模型性能"""
    model_type: ModelType
    objective: LearningObjective
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    mae: float  # 平均绝对误差
    rmse: float  # 均方根误差
    last_updated: datetime


class LearningSystem:
    """实时学习系统"""
    
    def __init__(
        self,
        redis_client: redis.Redis,
        learning_rate: float = 0.01,
        batch_size: int = 100,
        update_frequency: int = 3600  # 秒
    ):
        self.redis = redis_client
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.update_frequency = update_frequency
        
        # 数据存储
        self.feedback_data: List[UserFeedback] = []
        self.interaction_data: List[InteractionData] = []
        self.learning_examples: Dict[LearningObjective, List[LearningExample]] = defaultdict(list)
        
        # 机器学习模型
        self.models: Dict[Tuple[ModelType, LearningObjective], Any] = {}
        self.model_performance: Dict[Tuple[ModelType, LearningObjective], ModelPerformance] = {}
        
        # 特征提取器
        self.feature_extractors = {
            "query_tfidf": TfidfVectorizer(max_features=1000),
            "response_tfidf": TfidfVectorizer(max_features=1000)
        }
        
        # 学习缓存
        self.learning_cache: Dict[str, Any] = {}
        
        # 性能监控
        self.performance_history: Dict[str, List[float]] = defaultdict(list)
        
        logger.info("实时学习系统初始化完成")
    
    async def add_user_feedback(
        self,
        user_id: str,
        session_id: str,
        query: str,
        response: str,
        feedback_type: FeedbackType,
        rating: float,
        specific_feedback: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """添加用户反馈"""
        try:
            feedback = UserFeedback(
                id=f"feedback_{datetime.now().timestamp()}",
                user_id=user_id,
                session_id=session_id,
                query=query,
                response=response,
                feedback_type=feedback_type,
                rating=rating,
                specific_feedback=specific_feedback,
                metadata=metadata or {},
                timestamp=datetime.now()
            )
            
            self.feedback_data.append(feedback)
            
            # 立即生成学习样本
            await self._generate_learning_examples_from_feedback(feedback)
            
            # 存储到Redis
            await self._store_feedback(feedback)
            
            logger.info(f"添加用户反馈: {user_id}, 评分: {rating}")
            return True
            
        except Exception as e:
            logger.error(f"添加用户反馈失败: {e}")
            return False
    
    async def add_interaction_data(
        self,
        user_id: str,
        session_id: str,
        query: str,
        response: str,
        response_time: float,
        retrieval_results: List[Dict[str, Any]],
        generation_metadata: Dict[str, Any],
        user_engagement: Dict[str, Any]
    ) -> bool:
        """添加交互数据"""
        try:
            interaction = InteractionData(
                id=f"interaction_{datetime.now().timestamp()}",
                user_id=user_id,
                session_id=session_id,
                query=query,
                response=response,
                response_time=response_time,
                retrieval_results=retrieval_results,
                generation_metadata=generation_metadata,
                user_engagement=user_engagement,
                timestamp=datetime.now()
            )
            
            self.interaction_data.append(interaction)
            
            # 生成学习样本
            await self._generate_learning_examples_from_interaction(interaction)
            
            # 存储到Redis
            await self._store_interaction(interaction)
            
            logger.debug(f"添加交互数据: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"添加交互数据失败: {e}")
            return False
    
    async def update_models(self, force_update: bool = False) -> Dict[str, bool]:
        """更新机器学习模型"""
        try:
            results = {}
            
            # 检查是否需要更新
            if not force_update and not await self._should_update_models():
                return {"skipped": True}
            
            # 为每个学习目标更新模型
            for objective in LearningObjective:
                if objective in self.learning_examples:
                    examples = self.learning_examples[objective]
                    
                    if len(examples) >= self.batch_size:
                        # 更新检索排序模型
                        retrieval_result = await self._update_retrieval_model(objective, examples)
                        results[f"retrieval_{objective.value}"] = retrieval_result
                        
                        # 更新生成质量模型
                        generation_result = await self._update_generation_model(objective, examples)
                        results[f"generation_{objective.value}"] = generation_result
                        
                        # 更新查询理解模型
                        query_result = await self._update_query_understanding_model(objective, examples)
                        results[f"query_{objective.value}"] = query_result
            
            # 保存模型
            await self._save_models()
            
            logger.info(f"模型更新完成: {results}")
            return results
            
        except Exception as e:
            logger.error(f"更新模型失败: {e}")
            return {"error": str(e)}
    
    async def get_retrieval_score_prediction(
        self,
        query: str,
        document: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> float:
        """预测检索相关性分数"""
        try:
            # 提取特征
            features = await self._extract_retrieval_features(query, document, user_context)
            
            # 使用模型预测
            model_key = (ModelType.RETRIEVAL_RANKING, LearningObjective.RELEVANCE)
            if model_key in self.models:
                model = self.models[model_key]
                feature_vector = self._features_to_vector(features, "retrieval")
                score = model.predict([feature_vector])[0]
                return max(0.0, min(1.0, score))
            
            # 默认分数
            return 0.5
            
        except Exception as e:
            logger.error(f"预测检索分数失败: {e}")
            return 0.5
    
    async def get_generation_quality_prediction(
        self,
        query: str,
        context: str,
        response: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> float:
        """预测生成质量分数"""
        try:
            # 提取特征
            features = await self._extract_generation_features(query, context, response, user_context)
            
            # 使用模型预测
            model_key = (ModelType.GENERATION_QUALITY, LearningObjective.ACCURACY)
            if model_key in self.models:
                model = self.models[model_key]
                feature_vector = self._features_to_vector(features, "generation")
                score = model.predict([feature_vector])[0]
                return max(0.0, min(1.0, score))
            
            # 默认分数
            return 0.5
            
        except Exception as e:
            logger.error(f"预测生成质量失败: {e}")
            return 0.5
    
    async def get_query_intent_prediction(
        self,
        query: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, float]:
        """预测查询意图"""
        try:
            # 提取特征
            features = await self._extract_query_features(query, user_context)
            
            # 预测意图分布
            intents = {
                "health_consultation": 0.0,
                "symptom_inquiry": 0.0,
                "treatment_advice": 0.0,
                "prevention_guidance": 0.0,
                "lifestyle_recommendation": 0.0,
                "emergency": 0.0
            }
            
            # 使用模型预测（如果有的话）
            model_key = (ModelType.QUERY_UNDERSTANDING, LearningObjective.ACCURACY)
            if model_key in self.models:
                model = self.models[model_key]
                feature_vector = self._features_to_vector(features, "query")
                # 这里简化处理，实际应该是多分类模型
                base_score = model.predict([feature_vector])[0]
                
                # 基于关键词分配意图概率
                query_lower = query.lower()
                if any(word in query_lower for word in ["症状", "不舒服", "疼痛"]):
                    intents["symptom_inquiry"] = base_score
                elif any(word in query_lower for word in ["治疗", "怎么办", "用药"]):
                    intents["treatment_advice"] = base_score
                elif any(word in query_lower for word in ["预防", "保健", "养生"]):
                    intents["prevention_guidance"] = base_score
                elif any(word in query_lower for word in ["急救", "紧急", "严重"]):
                    intents["emergency"] = base_score
                else:
                    intents["health_consultation"] = base_score
            else:
                # 基于规则的简单意图识别
                query_lower = query.lower()
                if any(word in query_lower for word in ["症状", "不舒服", "疼痛"]):
                    intents["symptom_inquiry"] = 0.8
                elif any(word in query_lower for word in ["治疗", "怎么办", "用药"]):
                    intents["treatment_advice"] = 0.8
                elif any(word in query_lower for word in ["预防", "保健", "养生"]):
                    intents["prevention_guidance"] = 0.8
                elif any(word in query_lower for word in ["急救", "紧急", "严重"]):
                    intents["emergency"] = 0.9
                else:
                    intents["health_consultation"] = 0.6
            
            return intents
            
        except Exception as e:
            logger.error(f"预测查询意图失败: {e}")
            return {"health_consultation": 0.5}
    
    async def get_personalization_score(
        self,
        user_id: str,
        content: str,
        content_type: str
    ) -> float:
        """获取个性化分数"""
        try:
            # 获取用户历史数据
            user_feedback = [f for f in self.feedback_data if f.user_id == user_id]
            user_interactions = [i for i in self.interaction_data if i.user_id == user_id]
            
            if not user_feedback and not user_interactions:
                return 0.5  # 新用户默认分数
            
            # 计算用户偏好
            avg_rating = np.mean([f.rating for f in user_feedback]) if user_feedback else 3.0
            
            # 分析内容匹配度
            content_score = await self._calculate_content_personalization(
                user_id, content, content_type
            )
            
            # 综合分数
            personalization_score = (avg_rating / 5.0) * 0.6 + content_score * 0.4
            
            return max(0.0, min(1.0, personalization_score))
            
        except Exception as e:
            logger.error(f"计算个性化分数失败: {e}")
            return 0.5
    
    async def get_model_performance(
        self,
        model_type: Optional[ModelType] = None,
        objective: Optional[LearningObjective] = None
    ) -> Dict[str, Any]:
        """获取模型性能"""
        try:
            if model_type and objective:
                key = (model_type, objective)
                if key in self.model_performance:
                    return asdict(self.model_performance[key])
                return {}
            
            # 返回所有模型性能
            performance_data = {}
            for (mt, obj), perf in self.model_performance.items():
                key = f"{mt.value}_{obj.value}"
                performance_data[key] = asdict(perf)
            
            return performance_data
            
        except Exception as e:
            logger.error(f"获取模型性能失败: {e}")
            return {}
    
    async def get_learning_statistics(self) -> Dict[str, Any]:
        """获取学习统计信息"""
        try:
            stats = {
                "feedback_count": len(self.feedback_data),
                "interaction_count": len(self.interaction_data),
                "learning_examples_count": {
                    obj.value: len(examples) 
                    for obj, examples in self.learning_examples.items()
                },
                "model_count": len(self.models),
                "last_update": max(
                    [perf.last_updated for perf in self.model_performance.values()],
                    default=datetime.now()
                ).isoformat(),
                "average_rating": np.mean([f.rating for f in self.feedback_data]) if self.feedback_data else 0.0,
                "feedback_distribution": {
                    ft.value: len([f for f in self.feedback_data if f.feedback_type == ft])
                    for ft in FeedbackType
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"获取学习统计失败: {e}")
            return {}
    
    async def _generate_learning_examples_from_feedback(self, feedback: UserFeedback):
        """从反馈生成学习样本"""
        try:
            # 相关性学习样本
            relevance_features = await self._extract_feedback_features(feedback, "relevance")
            relevance_target = feedback.rating / 5.0  # 归一化到0-1
            
            relevance_example = LearningExample(
                id=f"relevance_{feedback.id}",
                features=relevance_features,
                target=relevance_target,
                objective=LearningObjective.RELEVANCE,
                weight=1.0,
                created_at=datetime.now()
            )
            self.learning_examples[LearningObjective.RELEVANCE].append(relevance_example)
            
            # 准确性学习样本
            accuracy_features = await self._extract_feedback_features(feedback, "accuracy")
            accuracy_target = 1.0 if feedback.feedback_type == FeedbackType.POSITIVE else 0.0
            
            accuracy_example = LearningExample(
                id=f"accuracy_{feedback.id}",
                features=accuracy_features,
                target=accuracy_target,
                objective=LearningObjective.ACCURACY,
                weight=1.0,
                created_at=datetime.now()
            )
            self.learning_examples[LearningObjective.ACCURACY].append(accuracy_example)
            
            # 用户满意度学习样本
            satisfaction_features = await self._extract_feedback_features(feedback, "satisfaction")
            satisfaction_target = feedback.rating / 5.0
            
            satisfaction_example = LearningExample(
                id=f"satisfaction_{feedback.id}",
                features=satisfaction_features,
                target=satisfaction_target,
                objective=LearningObjective.USER_SATISFACTION,
                weight=1.0,
                created_at=datetime.now()
            )
            self.learning_examples[LearningObjective.USER_SATISFACTION].append(satisfaction_example)
            
        except Exception as e:
            logger.error(f"从反馈生成学习样本失败: {e}")
    
    async def _generate_learning_examples_from_interaction(self, interaction: InteractionData):
        """从交互数据生成学习样本"""
        try:
            # 响应时间学习样本
            time_features = await self._extract_interaction_features(interaction, "response_time")
            time_target = min(1.0, 10.0 / max(0.1, interaction.response_time))  # 10秒内为满分
            
            time_example = LearningExample(
                id=f"response_time_{interaction.id}",
                features=time_features,
                target=time_target,
                objective=LearningObjective.RESPONSE_TIME,
                weight=1.0,
                created_at=datetime.now()
            )
            self.learning_examples[LearningObjective.RESPONSE_TIME].append(time_example)
            
            # 个性化学习样本
            if interaction.user_engagement:
                personalization_features = await self._extract_interaction_features(
                    interaction, "personalization"
                )
                engagement_score = interaction.user_engagement.get("engagement_score", 0.5)
                
                personalization_example = LearningExample(
                    id=f"personalization_{interaction.id}",
                    features=personalization_features,
                    target=engagement_score,
                    objective=LearningObjective.PERSONALIZATION,
                    weight=1.0,
                    created_at=datetime.now()
                )
                self.learning_examples[LearningObjective.PERSONALIZATION].append(personalization_example)
            
        except Exception as e:
            logger.error(f"从交互数据生成学习样本失败: {e}")
    
    async def _update_retrieval_model(
        self,
        objective: LearningObjective,
        examples: List[LearningExample]
    ) -> bool:
        """更新检索模型"""
        try:
            # 准备训练数据
            X, y, weights = self._prepare_training_data(examples, "retrieval")
            
            if len(X) < 10:  # 数据太少
                return False
            
            # 分割训练和测试数据
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # 训练模型
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train, sample_weight=weights[:len(X_train)])
            
            # 评估模型
            y_pred = model.predict(X_test)
            performance = self._calculate_regression_metrics(y_test, y_pred)
            
            # 保存模型和性能
            model_key = (ModelType.RETRIEVAL_RANKING, objective)
            self.models[model_key] = model
            
            self.model_performance[model_key] = ModelPerformance(
                model_type=ModelType.RETRIEVAL_RANKING,
                objective=objective,
                accuracy=performance["r2"],
                precision=0.0,  # 回归任务不适用
                recall=0.0,     # 回归任务不适用
                f1_score=0.0,   # 回归任务不适用
                mae=performance["mae"],
                rmse=performance["rmse"],
                last_updated=datetime.now()
            )
            
            logger.info(f"更新检索模型 {objective.value}: MAE={performance['mae']:.3f}")
            return True
            
        except Exception as e:
            logger.error(f"更新检索模型失败: {e}")
            return False
    
    async def _update_generation_model(
        self,
        objective: LearningObjective,
        examples: List[LearningExample]
    ) -> bool:
        """更新生成模型"""
        try:
            # 准备训练数据
            X, y, weights = self._prepare_training_data(examples, "generation")
            
            if len(X) < 10:
                return False
            
            # 分割数据
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # 训练模型
            model = GradientBoostingRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train, sample_weight=weights[:len(X_train)])
            
            # 评估模型
            y_pred = model.predict(X_test)
            performance = self._calculate_regression_metrics(y_test, y_pred)
            
            # 保存模型和性能
            model_key = (ModelType.GENERATION_QUALITY, objective)
            self.models[model_key] = model
            
            self.model_performance[model_key] = ModelPerformance(
                model_type=ModelType.GENERATION_QUALITY,
                objective=objective,
                accuracy=performance["r2"],
                precision=0.0,
                recall=0.0,
                f1_score=0.0,
                mae=performance["mae"],
                rmse=performance["rmse"],
                last_updated=datetime.now()
            )
            
            logger.info(f"更新生成模型 {objective.value}: MAE={performance['mae']:.3f}")
            return True
            
        except Exception as e:
            logger.error(f"更新生成模型失败: {e}")
            return False
    
    async def _update_query_understanding_model(
        self,
        objective: LearningObjective,
        examples: List[LearningExample]
    ) -> bool:
        """更新查询理解模型"""
        try:
            # 准备训练数据
            X, y, weights = self._prepare_training_data(examples, "query")
            
            if len(X) < 10:
                return False
            
            # 分割数据
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # 训练模型
            model = LogisticRegression(random_state=42)
            
            # 将回归目标转换为分类目标
            y_train_class = (y_train > 0.5).astype(int)
            y_test_class = (y_test > 0.5).astype(int)
            
            model.fit(X_train, y_train_class, sample_weight=weights[:len(X_train)])
            
            # 评估模型
            y_pred_class = model.predict(X_test)
            performance = self._calculate_classification_metrics(y_test_class, y_pred_class)
            
            # 保存模型和性能
            model_key = (ModelType.QUERY_UNDERSTANDING, objective)
            self.models[model_key] = model
            
            self.model_performance[model_key] = ModelPerformance(
                model_type=ModelType.QUERY_UNDERSTANDING,
                objective=objective,
                accuracy=performance["accuracy"],
                precision=performance["precision"],
                recall=performance["recall"],
                f1_score=performance["f1"],
                mae=0.0,
                rmse=0.0,
                last_updated=datetime.now()
            )
            
            logger.info(f"更新查询理解模型 {objective.value}: F1={performance['f1']:.3f}")
            return True
            
        except Exception as e:
            logger.error(f"更新查询理解模型失败: {e}")
            return False
    
    async def _should_update_models(self) -> bool:
        """检查是否应该更新模型"""
        try:
            # 检查时间间隔
            if self.model_performance:
                last_update = max(perf.last_updated for perf in self.model_performance.values())
                if (datetime.now() - last_update).seconds < self.update_frequency:
                    return False
            
            # 检查数据量
            total_examples = sum(len(examples) for examples in self.learning_examples.values())
            if total_examples < self.batch_size:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"检查模型更新条件失败: {e}")
            return False
    
    def _prepare_training_data(
        self,
        examples: List[LearningExample],
        feature_type: str
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """准备训练数据"""
        try:
            X = []
            y = []
            weights = []
            
            for example in examples:
                feature_vector = self._features_to_vector(example.features, feature_type)
                X.append(feature_vector)
                y.append(example.target)
                weights.append(example.weight)
            
            return np.array(X), np.array(y), np.array(weights)
            
        except Exception as e:
            logger.error(f"准备训练数据失败: {e}")
            return np.array([]), np.array([]), np.array([])
    
    def _features_to_vector(self, features: Dict[str, Any], feature_type: str) -> np.ndarray:
        """将特征字典转换为向量"""
        try:
            # 这里简化处理，实际应该根据特征类型进行不同的处理
            vector = []
            
            # 数值特征
            for key in ["query_length", "response_length", "response_time", "confidence"]:
                vector.append(features.get(key, 0.0))
            
            # 布尔特征
            for key in ["has_medical_terms", "has_symptoms", "has_treatment"]:
                vector.append(1.0 if features.get(key, False) else 0.0)
            
            # 分类特征（简单编码）
            intent = features.get("intent", "unknown")
            intent_encoding = {
                "health_consultation": [1, 0, 0, 0],
                "symptom_inquiry": [0, 1, 0, 0],
                "treatment_advice": [0, 0, 1, 0],
                "prevention_guidance": [0, 0, 0, 1]
            }
            vector.extend(intent_encoding.get(intent, [0, 0, 0, 0]))
            
            # 确保向量长度一致
            while len(vector) < 20:
                vector.append(0.0)
            
            return np.array(vector[:20])
            
        except Exception as e:
            logger.error(f"特征向量化失败: {e}")
            return np.zeros(20)
    
    def _calculate_regression_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """计算回归指标"""
        try:
            mae = np.mean(np.abs(y_true - y_pred))
            rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
            
            # R²分数
            ss_res = np.sum((y_true - y_pred) ** 2)
            ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
            r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            return {
                "mae": mae,
                "rmse": rmse,
                "r2": r2
            }
            
        except Exception as e:
            logger.error(f"计算回归指标失败: {e}")
            return {"mae": 1.0, "rmse": 1.0, "r2": 0.0}
    
    def _calculate_classification_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> Dict[str, float]:
        """计算分类指标"""
        try:
            accuracy = accuracy_score(y_true, y_pred)
            precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
            recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
            f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
            
            return {
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1": f1
            }
            
        except Exception as e:
            logger.error(f"计算分类指标失败: {e}")
            return {"accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1": 0.0}
    
    async def _extract_feedback_features(
        self,
        feedback: UserFeedback,
        feature_type: str
    ) -> Dict[str, Any]:
        """从反馈提取特征"""
        try:
            features = {
                "query_length": len(feedback.query),
                "response_length": len(feedback.response),
                "has_medical_terms": any(
                    term in feedback.query.lower() 
                    for term in ["症状", "疼痛", "治疗", "药物", "医生"]
                ),
                "has_symptoms": any(
                    term in feedback.query.lower()
                    for term in ["头痛", "发烧", "咳嗽", "腹痛", "失眠"]
                ),
                "has_treatment": any(
                    term in feedback.query.lower()
                    for term in ["治疗", "用药", "手术", "康复"]
                ),
                "user_id_hash": hash(feedback.user_id) % 1000,
                "hour_of_day": feedback.timestamp.hour,
                "day_of_week": feedback.timestamp.weekday()
            }
            
            return features
            
        except Exception as e:
            logger.error(f"提取反馈特征失败: {e}")
            return {}
    
    async def _extract_interaction_features(
        self,
        interaction: InteractionData,
        feature_type: str
    ) -> Dict[str, Any]:
        """从交互数据提取特征"""
        try:
            features = {
                "query_length": len(interaction.query),
                "response_length": len(interaction.response),
                "response_time": interaction.response_time,
                "retrieval_count": len(interaction.retrieval_results),
                "avg_retrieval_score": np.mean([
                    r.get("score", 0.0) for r in interaction.retrieval_results
                ]) if interaction.retrieval_results else 0.0,
                "generation_confidence": interaction.generation_metadata.get("confidence", 0.5),
                "user_id_hash": hash(interaction.user_id) % 1000,
                "hour_of_day": interaction.timestamp.hour,
                "day_of_week": interaction.timestamp.weekday()
            }
            
            return features
            
        except Exception as e:
            logger.error(f"提取交互特征失败: {e}")
            return {}
    
    async def _extract_retrieval_features(
        self,
        query: str,
        document: str,
        user_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """提取检索特征"""
        try:
            features = {
                "query_length": len(query),
                "document_length": len(document),
                "query_doc_length_ratio": len(query) / max(1, len(document)),
                "has_medical_terms": any(
                    term in query.lower() 
                    for term in ["症状", "疼痛", "治疗", "药物"]
                ),
                "confidence": 0.5  # 默认置信度
            }
            
            if user_context:
                features.update({
                    "user_age": user_context.get("age", 30),
                    "user_gender": 1 if user_context.get("gender") == "female" else 0,
                    "has_medical_history": len(user_context.get("medical_history", [])) > 0
                })
            
            return features
            
        except Exception as e:
            logger.error(f"提取检索特征失败: {e}")
            return {}
    
    async def _extract_generation_features(
        self,
        query: str,
        context: str,
        response: str,
        user_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """提取生成特征"""
        try:
            features = {
                "query_length": len(query),
                "context_length": len(context),
                "response_length": len(response),
                "context_response_ratio": len(context) / max(1, len(response)),
                "has_medical_advice": any(
                    term in response.lower()
                    for term in ["建议", "推荐", "应该", "可以"]
                ),
                "confidence": 0.5
            }
            
            return features
            
        except Exception as e:
            logger.error(f"提取生成特征失败: {e}")
            return {}
    
    async def _extract_query_features(
        self,
        query: str,
        user_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """提取查询特征"""
        try:
            features = {
                "query_length": len(query),
                "word_count": len(query.split()),
                "has_question_mark": "?" in query or "？" in query,
                "has_medical_terms": any(
                    term in query.lower()
                    for term in ["症状", "疼痛", "治疗", "药物", "医生"]
                ),
                "urgency_indicators": any(
                    term in query.lower()
                    for term in ["急", "紧急", "严重", "马上"]
                )
            }
            
            return features
            
        except Exception as e:
            logger.error(f"提取查询特征失败: {e}")
            return {}
    
    async def _calculate_content_personalization(
        self,
        user_id: str,
        content: str,
        content_type: str
    ) -> float:
        """计算内容个性化分数"""
        try:
            # 获取用户历史偏好
            user_feedback = [f for f in self.feedback_data if f.user_id == user_id]
            
            if not user_feedback:
                return 0.5
            
            # 分析用户偏好的内容特征
            preferred_features = []
            for feedback in user_feedback:
                if feedback.rating >= 4:  # 高评分内容
                    preferred_features.append(feedback.response)
            
            if not preferred_features:
                return 0.5
            
            # 计算内容相似度（简化版本）
            content_words = set(content.lower().split())
            
            similarity_scores = []
            for preferred_content in preferred_features:
                preferred_words = set(preferred_content.lower().split())
                intersection = content_words & preferred_words
                union = content_words | preferred_words
                
                if union:
                    jaccard_similarity = len(intersection) / len(union)
                    similarity_scores.append(jaccard_similarity)
            
            if similarity_scores:
                return np.mean(similarity_scores)
            
            return 0.5
            
        except Exception as e:
            logger.error(f"计算内容个性化分数失败: {e}")
            return 0.5
    
    async def _store_feedback(self, feedback: UserFeedback):
        """存储反馈到Redis"""
        try:
            feedback_data = asdict(feedback)
            feedback_data["timestamp"] = feedback.timestamp.isoformat()
            feedback_data["feedback_type"] = feedback.feedback_type.value
            
            await self.redis.setex(
                f"feedback:{feedback.id}",
                86400 * 7,  # 保存7天
                json.dumps(feedback_data)
            )
            
        except Exception as e:
            logger.error(f"存储反馈失败: {e}")
    
    async def _store_interaction(self, interaction: InteractionData):
        """存储交互数据到Redis"""
        try:
            interaction_data = asdict(interaction)
            interaction_data["timestamp"] = interaction.timestamp.isoformat()
            
            await self.redis.setex(
                f"interaction:{interaction.id}",
                86400 * 3,  # 保存3天
                json.dumps(interaction_data)
            )
            
        except Exception as e:
            logger.error(f"存储交互数据失败: {e}")
    
    async def _save_models(self):
        """保存模型到Redis"""
        try:
            for (model_type, objective), model in self.models.items():
                model_key = f"model:{model_type.value}:{objective.value}"
                model_data = pickle.dumps(model)
                
                await self.redis.setex(
                    model_key,
                    86400 * 30,  # 保存30天
                    model_data
                )
            
            logger.info("模型保存完成")
            
        except Exception as e:
            logger.error(f"保存模型失败: {e}")
    
    async def _load_models(self):
        """从Redis加载模型"""
        try:
            model_keys = await self.redis.keys("model:*")
            
            for key in model_keys:
                key_str = key.decode()
                parts = key_str.split(":")
                
                if len(parts) == 3:
                    model_type = ModelType(parts[1])
                    objective = LearningObjective(parts[2])
                    
                    model_data = await self.redis.get(key)
                    if model_data:
                        model = pickle.loads(model_data)
                        self.models[(model_type, objective)] = model
            
            logger.info(f"加载了 {len(self.models)} 个模型")
            
        except Exception as e:
            logger.error(f"加载模型失败: {e}") 