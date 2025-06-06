"""
recommendation_engine - 索克生活项目模块
"""

from ..observability.metrics import MetricsCollector
from ..observability.tracing import trace_operation, SpanKind
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from loguru import logger
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List, Any, Optional, Tuple, Union
import time

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能推荐引擎 - 提供个性化健康建议、中医方案推荐、生活方式指导
"""



class RecommendationType(str, Enum):
    """推荐类型"""
    HEALTH_ADVICE = "health_advice"                 # 健康建议
    TCM_FORMULA = "tcm_formula"                     # 中医方剂
    LIFESTYLE = "lifestyle"                         # 生活方式
    NUTRITION = "nutrition"                         # 营养建议
    EXERCISE = "exercise"                           # 运动建议
    MENTAL_HEALTH = "mental_health"                 # 心理健康
    PREVENTION = "prevention"                       # 预防保健
    TREATMENT = "treatment"                         # 治疗方案
    CONSTITUTION = "constitution"                   # 体质调理
    SEASONAL = "seasonal"                           # 季节养生

class RecommendationStrategy(str, Enum):
    """推荐策略"""
    COLLABORATIVE_FILTERING = "collaborative_filtering"     # 协同过滤
    CONTENT_BASED = "content_based"                         # 基于内容
    HYBRID = "hybrid"                                       # 混合推荐
    KNOWLEDGE_BASED = "knowledge_based"                     # 基于知识
    DEMOGRAPHIC = "demographic"                             # 基于人口统计
    CONTEXT_AWARE = "context_aware"                         # 上下文感知
    DEEP_LEARNING = "deep_learning"                         # 深度学习
    TCM_SYNDROME = "tcm_syndrome"                           # 中医辨证

class ConfidenceLevel(str, Enum):
    """置信度级别"""
    VERY_LOW = "very_low"      # 很低 (0-0.2)
    LOW = "low"                # 低 (0.2-0.4)
    MEDIUM = "medium"          # 中等 (0.4-0.6)
    HIGH = "high"              # 高 (0.6-0.8)
    VERY_HIGH = "very_high"    # 很高 (0.8-1.0)

@dataclass
class UserProfile:
    """用户画像"""
    user_id: str
    age: int
    gender: str
    constitution_type: str                          # 体质类型
    health_conditions: List[str] = field(default_factory=list)
    symptoms: List[str] = field(default_factory=list)
    lifestyle_factors: Dict[str, Any] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)
    health_goals: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    medication_history: List[str] = field(default_factory=list)
    allergy_info: List[str] = field(default_factory=list)
    location: Optional[str] = None
    occupation: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class RecommendationItem:
    """推荐项目"""
    id: str
    type: RecommendationType
    title: str
    description: str
    content: Dict[str, Any]
    confidence_score: float
    confidence_level: ConfidenceLevel
    relevance_score: float
    priority: int = 1                               # 1-5级优先级
    tags: List[str] = field(default_factory=list)
    category: Optional[str] = None
    source: Optional[str] = None
    evidence: List[str] = field(default_factory=list)
    contraindications: List[str] = field(default_factory=list)
    side_effects: List[str] = field(default_factory=list)
    duration: Optional[str] = None
    frequency: Optional[str] = None
    cost_estimate: Optional[float] = None
    effectiveness_rate: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RecommendationContext:
    """推荐上下文"""
    user_id: str
    session_id: str
    current_symptoms: List[str] = field(default_factory=list)
    current_concerns: List[str] = field(default_factory=list)
    time_of_day: Optional[str] = None
    season: Optional[str] = None
    weather: Optional[Dict[str, Any]] = None
    location: Optional[str] = None
    recent_activities: List[str] = field(default_factory=list)
    current_medications: List[str] = field(default_factory=list)
    stress_level: Optional[int] = None
    sleep_quality: Optional[int] = None
    energy_level: Optional[int] = None
    mood: Optional[str] = None
    emergency_level: int = 0                        # 0-5级紧急程度

@dataclass
class RecommendationResult:
    """推荐结果"""
    user_id: str
    request_id: str
    recommendations: List[RecommendationItem]
    strategy_used: RecommendationStrategy
    total_items: int
    processing_time: float
    context: RecommendationContext
    explanation: str = ""
    alternatives: List[RecommendationItem] = field(default_factory=list)
    follow_up_questions: List[str] = field(default_factory=list)
    next_check_time: Optional[datetime] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

class CollaborativeFilteringEngine:
    """协同过滤推荐引擎"""
    
    def __init__(self):
        self.user_item_matrix = None
        self.user_similarity_matrix = None
        self.item_similarity_matrix = None
        self.trained = False
    
    async def train(self, interaction_data: List[Dict[str, Any]]):
        """训练协同过滤模型"""
        try:
            # 构建用户-项目矩阵
            df = pd.DataFrame(interaction_data)
            self.user_item_matrix = df.pivot_table(
                index='user_id', 
                columns='item_id', 
                values='rating',
                fill_value=0
            )
            
            # 计算用户相似度矩阵
            user_vectors = self.user_item_matrix.values
            self.user_similarity_matrix = cosine_similarity(user_vectors)
            
            # 计算项目相似度矩阵
            item_vectors = self.user_item_matrix.T.values
            self.item_similarity_matrix = cosine_similarity(item_vectors)
            
            self.trained = True
            logger.info("协同过滤模型训练完成")
            
        except Exception as e:
            logger.error(f"协同过滤模型训练失败: {e}")
    
    async def recommend_by_user_similarity(
        self, 
        user_id: str, 
        top_k: int = 10
    ) -> List[Tuple[str, float]]:
        """基于用户相似度推荐"""
        if not self.trained or user_id not in self.user_item_matrix.index:
            return []
        
        user_idx = self.user_item_matrix.index.get_loc(user_id)
        user_similarities = self.user_similarity_matrix[user_idx]
        
        # 找到最相似的用户
        similar_users = np.argsort(user_similarities)[::-1][1:11]  # 排除自己
        
        # 获取推荐项目
        recommendations = {}
        user_ratings = self.user_item_matrix.iloc[user_idx]
        
        for similar_user_idx in similar_users:
            similarity = user_similarities[similar_user_idx]
            similar_user_ratings = self.user_item_matrix.iloc[similar_user_idx]
            
            for item_id, rating in similar_user_ratings.items():
                if rating > 0 and user_ratings[item_id] == 0:  # 用户未评价过的项目
                    if item_id not in recommendations:
                        recommendations[item_id] = 0
                    recommendations[item_id] += similarity * rating
        
        # 排序并返回top_k
        sorted_recommendations = sorted(
            recommendations.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:top_k]
        
        return sorted_recommendations
    
    async def recommend_by_item_similarity(
        self, 
        user_id: str, 
        top_k: int = 10
    ) -> List[Tuple[str, float]]:
        """基于项目相似度推荐"""
        if not self.trained or user_id not in self.user_item_matrix.index:
            return []
        
        user_ratings = self.user_item_matrix.loc[user_id]
        rated_items = user_ratings[user_ratings > 0].index
        
        recommendations = {}
        
        for rated_item in rated_items:
            item_idx = self.user_item_matrix.columns.get_loc(rated_item)
            item_similarities = self.item_similarity_matrix[item_idx]
            
            for i, similarity in enumerate(item_similarities):
                item_id = self.user_item_matrix.columns[i]
                if item_id != rated_item and user_ratings[item_id] == 0:
                    if item_id not in recommendations:
                        recommendations[item_id] = 0
                    recommendations[item_id] += similarity * user_ratings[rated_item]
        
        # 排序并返回top_k
        sorted_recommendations = sorted(
            recommendations.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:top_k]
        
        return sorted_recommendations

class ContentBasedEngine:
    """基于内容的推荐引擎"""
    
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.item_features = None
        self.item_vectors = None
        self.trained = False
    
    async def train(self, item_data: List[Dict[str, Any]]):
        """训练基于内容的模型"""
        try:
            # 提取项目特征
            self.item_features = pd.DataFrame(item_data)
            
            # 构建文本特征向量
            text_features = self.item_features['description'].fillna('')
            self.item_vectors = self.tfidf_vectorizer.fit_transform(text_features)
            
            self.trained = True
            logger.info("基于内容的推荐模型训练完成")
            
        except Exception as e:
            logger.error(f"基于内容的推荐模型训练失败: {e}")
    
    async def recommend_by_content(
        self, 
        user_profile: UserProfile, 
        top_k: int = 10
    ) -> List[Tuple[str, float]]:
        """基于内容推荐"""
        if not self.trained:
            return []
        
        # 构建用户偏好向量
        user_preferences = " ".join([
            " ".join(user_profile.health_conditions),
            " ".join(user_profile.symptoms),
            " ".join(user_profile.health_goals),
            user_profile.constitution_type
        ])
        
        user_vector = self.tfidf_vectorizer.transform([user_preferences])
        
        # 计算相似度
        similarities = cosine_similarity(user_vector, self.item_vectors).flatten()
        
        # 获取推荐项目
        item_indices = np.argsort(similarities)[::-1][:top_k]
        recommendations = []
        
        for idx in item_indices:
            item_id = self.item_features.iloc[idx]['id']
            score = similarities[idx]
            recommendations.append((item_id, score))
        
        return recommendations

class TCMSyndromeEngine:
    """中医辨证推荐引擎"""
    
    def __init__(self):
        self.syndrome_rules = {}
        self.formula_database = {}
        self.herb_database = {}
        self.constitution_mapping = {}
        self.initialized = False
    
    async def initialize(self):
        """初始化中医知识库"""
        try:
            # 加载辨证规则
            self.syndrome_rules = await self._load_syndrome_rules()
            
            # 加载方剂数据库
            self.formula_database = await self._load_formula_database()
            
            # 加载中药数据库
            self.herb_database = await self._load_herb_database()
            
            # 加载体质映射
            self.constitution_mapping = await self._load_constitution_mapping()
            
            self.initialized = True
            logger.info("中医辨证推荐引擎初始化完成")
            
        except Exception as e:
            logger.error(f"中医辨证推荐引擎初始化失败: {e}")
    
    async def _load_syndrome_rules(self) -> Dict[str, Any]:
        """加载辨证规则"""
        return {
            "气虚证": {
                "symptoms": ["乏力", "气短", "懒言", "自汗", "脉弱"],
                "tongue": ["舌淡", "苔薄白"],
                "pulse": ["脉弱", "脉细"],
                "formulas": ["四君子汤", "补中益气汤", "参苓白术散"],
                "lifestyle": ["适度运动", "规律作息", "避免过劳"]
            },
            "血虚证": {
                "symptoms": ["面色萎黄", "头晕", "心悸", "失眠", "月经量少"],
                "tongue": ["舌淡", "苔薄"],
                "pulse": ["脉细", "脉弱"],
                "formulas": ["四物汤", "当归补血汤", "八珍汤"],
                "lifestyle": ["充足睡眠", "营养均衡", "避免熬夜"]
            },
            "阴虚证": {
                "symptoms": ["潮热", "盗汗", "五心烦热", "口干", "便秘"],
                "tongue": ["舌红", "少苔"],
                "pulse": ["脉细数"],
                "formulas": ["六味地黄丸", "知柏地黄丸", "麦味地黄丸"],
                "lifestyle": ["清淡饮食", "避免辛辣", "保持心情平和"]
            },
            "阳虚证": {
                "symptoms": ["畏寒", "四肢不温", "腰膝酸软", "夜尿频", "便溏"],
                "tongue": ["舌淡胖", "苔白"],
                "pulse": ["脉沉迟"],
                "formulas": ["金匮肾气丸", "右归丸", "附子理中汤"],
                "lifestyle": ["温补饮食", "适度运动", "保暖防寒"]
            }
        }
    
    async def _load_formula_database(self) -> Dict[str, Any]:
        """加载方剂数据库"""
        return {
            "四君子汤": {
                "composition": ["人参", "白术", "茯苓", "甘草"],
                "functions": ["益气健脾"],
                "indications": ["脾胃气虚", "食少便溏", "气短乏力"],
                "contraindications": ["阴虚火旺", "实热证"],
                "dosage": "水煎服，日一剂"
            },
            "四物汤": {
                "composition": ["当归", "川芎", "白芍", "熟地黄"],
                "functions": ["补血调血"],
                "indications": ["血虚证", "月经不调", "产后血虚"],
                "contraindications": ["血热证", "实证"],
                "dosage": "水煎服，日一剂"
            },
            "六味地黄丸": {
                "composition": ["熟地黄", "山茱萸", "山药", "泽泻", "茯苓", "丹皮"],
                "functions": ["滋阴补肾"],
                "indications": ["肾阴虚", "腰膝酸软", "头晕耳鸣"],
                "contraindications": ["脾虚便溏", "痰湿重"],
                "dosage": "口服，一次8丸，一日3次"
            }
        }
    
    async def _load_herb_database(self) -> Dict[str, Any]:
        """加载中药数据库"""
        return {
            "人参": {
                "nature": "温",
                "flavor": "甘、微苦",
                "meridian": ["脾", "肺", "心"],
                "functions": ["大补元气", "复脉固脱", "补脾益肺"],
                "contraindications": ["实热证", "阴虚阳亢"],
                "dosage": "3-9g"
            },
            "当归": {
                "nature": "温",
                "flavor": "甘、辛",
                "meridian": ["肝", "心", "脾"],
                "functions": ["补血活血", "调经止痛", "润肠通便"],
                "contraindications": ["湿盛中满", "大便溏泄"],
                "dosage": "6-12g"
            },
            "熟地黄": {
                "nature": "微温",
                "flavor": "甘",
                "meridian": ["肝", "肾"],
                "functions": ["滋阴补血", "益精填髓"],
                "contraindications": ["脾虚痰多", "气滞血瘀"],
                "dosage": "9-15g"
            }
        }
    
    async def _load_constitution_mapping(self) -> Dict[str, Any]:
        """加载体质映射"""
        return {
            "平和质": {
                "characteristics": ["体形匀称", "面色润泽", "精力充沛"],
                "recommendations": ["保持现状", "适度运动", "均衡饮食"],
                "suitable_formulas": []
            },
            "气虚质": {
                "characteristics": ["容易疲劳", "气短懒言", "易感冒"],
                "recommendations": ["补气健脾", "避免过劳", "规律作息"],
                "suitable_formulas": ["四君子汤", "补中益气汤"]
            },
            "阳虚质": {
                "characteristics": ["畏寒怕冷", "四肢不温", "精神不振"],
                "recommendations": ["温阳散寒", "适度运动", "温热饮食"],
                "suitable_formulas": ["金匮肾气丸", "右归丸"]
            },
            "阴虚质": {
                "characteristics": ["手足心热", "口燥咽干", "喜冷饮"],
                "recommendations": ["滋阴润燥", "避免熬夜", "清淡饮食"],
                "suitable_formulas": ["六味地黄丸", "知柏地黄丸"]
            }
        }
    
    async def recommend_by_syndrome(
        self, 
        symptoms: List[str], 
        tongue: Optional[str] = None,
        pulse: Optional[str] = None,
        constitution: Optional[str] = None
    ) -> List[RecommendationItem]:
        """基于辨证推荐"""
        if not self.initialized:
            await self.initialize()
        
        recommendations = []
        
        # 辨证分析
        syndrome_scores = {}
        for syndrome, rules in self.syndrome_rules.items():
            score = 0
            
            # 症状匹配
            for symptom in symptoms:
                if symptom in rules["symptoms"]:
                    score += 2
            
            # 舌象匹配
            if tongue:
                for tongue_sign in rules["tongue"]:
                    if tongue_sign in tongue:
                        score += 1
            
            # 脉象匹配
            if pulse:
                for pulse_sign in rules["pulse"]:
                    if pulse_sign in pulse:
                        score += 1
            
            if score > 0:
                syndrome_scores[syndrome] = score
        
        # 根据证型推荐方剂
        for syndrome, score in sorted(syndrome_scores.items(), key=lambda x: x[1], reverse=True):
            confidence = min(score / 10.0, 1.0)  # 归一化置信度
            
            for formula_name in self.syndrome_rules[syndrome]["formulas"]:
                if formula_name in self.formula_database:
                    formula = self.formula_database[formula_name]
                    
                    recommendation = RecommendationItem(
                        id=f"formula_{formula_name}",
                        type=RecommendationType.TCM_FORMULA,
                        title=f"推荐方剂：{formula_name}",
                        description=f"针对{syndrome}的经典方剂",
                        content={
                            "formula_name": formula_name,
                            "composition": formula["composition"],
                            "functions": formula["functions"],
                            "indications": formula["indications"],
                            "dosage": formula["dosage"],
                            "syndrome": syndrome
                        },
                        confidence_score=confidence,
                        confidence_level=self._get_confidence_level(confidence),
                        relevance_score=score / 10.0,
                        contraindications=formula.get("contraindications", []),
                        tags=["中医", "方剂", syndrome]
                    )
                    
                    recommendations.append(recommendation)
        
        # 体质调理推荐
        if constitution and constitution in self.constitution_mapping:
            const_info = self.constitution_mapping[constitution]
            
            for formula_name in const_info["suitable_formulas"]:
                if formula_name in self.formula_database:
                    formula = self.formula_database[formula_name]
                    
                    recommendation = RecommendationItem(
                        id=f"constitution_{formula_name}",
                        type=RecommendationType.CONSTITUTION,
                        title=f"体质调理：{formula_name}",
                        description=f"适合{constitution}的调理方剂",
                        content={
                            "formula_name": formula_name,
                            "composition": formula["composition"],
                            "constitution": constitution,
                            "characteristics": const_info["characteristics"]
                        },
                        confidence_score=0.8,
                        confidence_level=ConfidenceLevel.HIGH,
                        relevance_score=0.8,
                        tags=["体质调理", constitution]
                    )
                    
                    recommendations.append(recommendation)
        
        return recommendations[:10]  # 返回前10个推荐
    
    def _get_confidence_level(self, score: float) -> ConfidenceLevel:
        """获取置信度级别"""
        if score >= 0.8:
            return ConfidenceLevel.VERY_HIGH
        elif score >= 0.6:
            return ConfidenceLevel.HIGH
        elif score >= 0.4:
            return ConfidenceLevel.MEDIUM
        elif score >= 0.2:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW

class RecommendationEngine:
    """智能推荐引擎主类"""
    
    def __init__(self, config: Dict[str, Any], metrics_collector: Optional[MetricsCollector] = None):
        self.config = config
        self.metrics_collector = metrics_collector
        
        # 推荐引擎组件
        self.collaborative_engine = CollaborativeFilteringEngine()
        self.content_engine = ContentBasedEngine()
        self.tcm_engine = TCMSyndromeEngine()
        
        # 用户画像存储
        self.user_profiles: Dict[str, UserProfile] = {}
        
        # 推荐历史
        self.recommendation_history: List[RecommendationResult] = []
        
        # 配置参数
        self.default_strategy = RecommendationStrategy(
            config.get("default_strategy", "hybrid")
        )
        self.max_recommendations = config.get("max_recommendations", 10)
        self.min_confidence = config.get("min_confidence", 0.3)
        
        # 运行状态
        self.initialized = False
    
    async def initialize(self):
        """初始化推荐引擎"""
        try:
            # 初始化各个推荐引擎
            await self.tcm_engine.initialize()
            
            # 加载用户画像
            await self._load_user_profiles()
            
            # 训练推荐模型
            await self._train_models()
            
            self.initialized = True
            logger.info("智能推荐引擎初始化完成")
            
        except Exception as e:
            logger.error(f"推荐引擎初始化失败: {e}")
            raise
    
    async def _load_user_profiles(self):
        """加载用户画像"""
        # 这里应该从数据库加载用户画像
        # 简化实现
        pass
    
    async def _train_models(self):
        """训练推荐模型"""
        try:
            # 训练协同过滤模型
            interaction_data = await self._get_interaction_data()
            if interaction_data:
                await self.collaborative_engine.train(interaction_data)
            
            # 训练基于内容的模型
            item_data = await self._get_item_data()
            if item_data:
                await self.content_engine.train(item_data)
            
            logger.info("推荐模型训练完成")
            
        except Exception as e:
            logger.error(f"推荐模型训练失败: {e}")
    
    async def _get_interaction_data(self) -> List[Dict[str, Any]]:
        """获取用户交互数据"""
        # 这里应该从数据库获取真实的交互数据
        # 简化实现，返回模拟数据
        return [
            {"user_id": "user1", "item_id": "item1", "rating": 5},
            {"user_id": "user1", "item_id": "item2", "rating": 4},
            {"user_id": "user2", "item_id": "item1", "rating": 3},
            {"user_id": "user2", "item_id": "item3", "rating": 5},
        ]
    
    async def _get_item_data(self) -> List[Dict[str, Any]]:
        """获取项目数据"""
        # 这里应该从数据库获取真实的项目数据
        # 简化实现，返回模拟数据
        return [
            {
                "id": "item1",
                "title": "气虚体质调理",
                "description": "适合气虚体质的调理方案，包含补气健脾的方剂和生活建议",
                "category": "体质调理",
                "tags": ["气虚", "健脾", "补气"]
            },
            {
                "id": "item2",
                "title": "失眠调理方案",
                "description": "针对失眠症状的中医调理方案，包含安神定志的方剂",
                "category": "症状调理",
                "tags": ["失眠", "安神", "养心"]
            }
        ]
    
    @trace_operation("recommendation.generate", SpanKind.INTERNAL)
    async def generate_recommendations(
        self,
        user_id: str,
        context: RecommendationContext,
        strategy: Optional[RecommendationStrategy] = None,
        max_items: Optional[int] = None
    ) -> RecommendationResult:
        """生成推荐"""
        start_time = time.time()
        request_id = f"rec_{int(time.time())}_{user_id}"
        
        try:
            if not self.initialized:
                await self.initialize()
            
            # 确定推荐策略
            used_strategy = strategy or self.default_strategy
            max_recommendations = max_items or self.max_recommendations
            
            # 获取用户画像
            user_profile = await self._get_user_profile(user_id)
            
            # 根据策略生成推荐
            recommendations = []
            
            if used_strategy == RecommendationStrategy.TCM_SYNDROME:
                recommendations = await self._generate_tcm_recommendations(
                    user_profile, context
                )
            elif used_strategy == RecommendationStrategy.COLLABORATIVE_FILTERING:
                recommendations = await self._generate_collaborative_recommendations(
                    user_id, context
                )
            elif used_strategy == RecommendationStrategy.CONTENT_BASED:
                recommendations = await self._generate_content_recommendations(
                    user_profile, context
                )
            elif used_strategy == RecommendationStrategy.HYBRID:
                recommendations = await self._generate_hybrid_recommendations(
                    user_id, user_profile, context
                )
            else:
                recommendations = await self._generate_knowledge_recommendations(
                    user_profile, context
                )
            
            # 过滤和排序
            filtered_recommendations = await self._filter_recommendations(
                recommendations, user_profile, context
            )
            
            sorted_recommendations = await self._sort_recommendations(
                filtered_recommendations, context
            )
            
            # 限制数量
            final_recommendations = sorted_recommendations[:max_recommendations]
            
            # 生成解释
            explanation = await self._generate_explanation(
                final_recommendations, used_strategy, context
            )
            
            # 生成后续问题
            follow_up_questions = await self._generate_follow_up_questions(
                final_recommendations, context
            )
            
            processing_time = time.time() - start_time
            
            result = RecommendationResult(
                user_id=user_id,
                request_id=request_id,
                recommendations=final_recommendations,
                strategy_used=used_strategy,
                total_items=len(final_recommendations),
                processing_time=processing_time,
                context=context,
                explanation=explanation,
                follow_up_questions=follow_up_questions
            )
            
            # 记录推荐历史
            self.recommendation_history.append(result)
            
            # 记录指标
            if self.metrics_collector:
                await self.metrics_collector.increment_counter(
                    "recommendations_generated",
                    {
                        "strategy": used_strategy.value,
                        "user_id": user_id,
                        "item_count": str(len(final_recommendations))
                    }
                )
                
                await self.metrics_collector.record_histogram(
                    "recommendation_processing_time",
                    processing_time,
                    {"strategy": used_strategy.value}
                )
            
            return result
            
        except Exception as e:
            logger.error(f"生成推荐失败: {e}")
            processing_time = time.time() - start_time
            
            return RecommendationResult(
                user_id=user_id,
                request_id=request_id,
                recommendations=[],
                strategy_used=used_strategy or self.default_strategy,
                total_items=0,
                processing_time=processing_time,
                context=context,
                explanation=f"推荐生成失败: {str(e)}"
            )
    
    async def _get_user_profile(self, user_id: str) -> UserProfile:
        """获取用户画像"""
        if user_id in self.user_profiles:
            return self.user_profiles[user_id]
        
        # 创建默认用户画像
        profile = UserProfile(
            user_id=user_id,
            age=30,
            gender="unknown",
            constitution_type="平和质"
        )
        
        self.user_profiles[user_id] = profile
        return profile
    
    async def _generate_tcm_recommendations(
        self,
        user_profile: UserProfile,
        context: RecommendationContext
    ) -> List[RecommendationItem]:
        """生成中医推荐"""
        return await self.tcm_engine.recommend_by_syndrome(
            symptoms=context.current_symptoms,
            constitution=user_profile.constitution_type
        )
    
    async def _generate_collaborative_recommendations(
        self,
        user_id: str,
        context: RecommendationContext
    ) -> List[RecommendationItem]:
        """生成协同过滤推荐"""
        recommendations = []
        
        # 基于用户相似度推荐
        user_sim_recs = await self.collaborative_engine.recommend_by_user_similarity(
            user_id, top_k=5
        )
        
        # 基于项目相似度推荐
        item_sim_recs = await self.collaborative_engine.recommend_by_item_similarity(
            user_id, top_k=5
        )
        
        # 合并推荐结果
        all_recs = user_sim_recs + item_sim_recs
        
        for item_id, score in all_recs:
            recommendation = RecommendationItem(
                id=item_id,
                type=RecommendationType.HEALTH_ADVICE,
                title=f"推荐项目: {item_id}",
                description="基于协同过滤的推荐",
                content={"item_id": item_id},
                confidence_score=score,
                confidence_level=self._get_confidence_level(score),
                relevance_score=score,
                tags=["协同过滤"]
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    async def _generate_content_recommendations(
        self,
        user_profile: UserProfile,
        context: RecommendationContext
    ) -> List[RecommendationItem]:
        """生成基于内容的推荐"""
        recommendations = []
        
        content_recs = await self.content_engine.recommend_by_content(
            user_profile, top_k=10
        )
        
        for item_id, score in content_recs:
            recommendation = RecommendationItem(
                id=item_id,
                type=RecommendationType.HEALTH_ADVICE,
                title=f"内容推荐: {item_id}",
                description="基于内容相似度的推荐",
                content={"item_id": item_id},
                confidence_score=score,
                confidence_level=self._get_confidence_level(score),
                relevance_score=score,
                tags=["内容推荐"]
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    async def _generate_hybrid_recommendations(
        self,
        user_id: str,
        user_profile: UserProfile,
        context: RecommendationContext
    ) -> List[RecommendationItem]:
        """生成混合推荐"""
        recommendations = []
        
        # 获取各种推荐
        tcm_recs = await self._generate_tcm_recommendations(user_profile, context)
        collab_recs = await self._generate_collaborative_recommendations(user_id, context)
        content_recs = await self._generate_content_recommendations(user_profile, context)
        
        # 合并并重新评分
        all_recs = tcm_recs + collab_recs + content_recs
        
        # 去重并重新计算分数
        unique_recs = {}
        for rec in all_recs:
            if rec.id not in unique_recs:
                unique_recs[rec.id] = rec
            else:
                # 合并分数
                existing = unique_recs[rec.id]
                existing.confidence_score = (existing.confidence_score + rec.confidence_score) / 2
                existing.relevance_score = (existing.relevance_score + rec.relevance_score) / 2
        
        return list(unique_recs.values())
    
    async def _generate_knowledge_recommendations(
        self,
        user_profile: UserProfile,
        context: RecommendationContext
    ) -> List[RecommendationItem]:
        """生成基于知识的推荐"""
        recommendations = []
        
        # 基于症状的知识推荐
        for symptom in context.current_symptoms:
            recommendation = RecommendationItem(
                id=f"knowledge_{symptom}",
                type=RecommendationType.HEALTH_ADVICE,
                title=f"关于{symptom}的健康建议",
                description=f"针对{symptom}症状的专业建议",
                content={
                    "symptom": symptom,
                    "advice": f"针对{symptom}的建议内容"
                },
                confidence_score=0.8,
                confidence_level=ConfidenceLevel.HIGH,
                relevance_score=0.8,
                tags=["知识推荐", symptom]
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    async def _filter_recommendations(
        self,
        recommendations: List[RecommendationItem],
        user_profile: UserProfile,
        context: RecommendationContext
    ) -> List[RecommendationItem]:
        """过滤推荐结果"""
        filtered = []
        
        for rec in recommendations:
            # 置信度过滤
            if rec.confidence_score < self.min_confidence:
                continue
            
            # 禁忌症过滤
            if any(allergy in rec.contraindications for allergy in user_profile.allergy_info):
                continue
            
            # 紧急情况过滤
            if context.emergency_level > 3 and rec.type not in [
                RecommendationType.TREATMENT, 
                RecommendationType.HEALTH_ADVICE
            ]:
                continue
            
            filtered.append(rec)
        
        return filtered
    
    async def _sort_recommendations(
        self,
        recommendations: List[RecommendationItem],
        context: RecommendationContext
    ) -> List[RecommendationItem]:
        """排序推荐结果"""
        def sort_key(rec: RecommendationItem) -> Tuple[int, float, float]:
            # 按优先级、置信度、相关性排序
            return (-rec.priority, -rec.confidence_score, -rec.relevance_score)
        
        return sorted(recommendations, key=sort_key)
    
    async def _generate_explanation(
        self,
        recommendations: List[RecommendationItem],
        strategy: RecommendationStrategy,
        context: RecommendationContext
    ) -> str:
        """生成推荐解释"""
        if not recommendations:
            return "暂时没有找到合适的推荐内容。"
        
        explanation_parts = [
            f"基于{strategy.value}策略，为您推荐了{len(recommendations)}项内容。"
        ]
        
        if context.current_symptoms:
            explanation_parts.append(
                f"主要针对您当前的症状：{', '.join(context.current_symptoms)}。"
            )
        
        if strategy == RecommendationStrategy.TCM_SYNDROME:
            explanation_parts.append("推荐内容基于中医辨证论治理论。")
        
        return " ".join(explanation_parts)
    
    async def _generate_follow_up_questions(
        self,
        recommendations: List[RecommendationItem],
        context: RecommendationContext
    ) -> List[str]:
        """生成后续问题"""
        questions = []
        
        if context.current_symptoms:
            questions.append("您的症状持续多长时间了？")
            questions.append("症状的严重程度如何？")
        
        if any(rec.type == RecommendationType.TCM_FORMULA for rec in recommendations):
            questions.append("您是否有药物过敏史？")
            questions.append("您目前是否在服用其他药物？")
        
        questions.append("您希望了解更多关于哪方面的信息？")
        
        return questions[:3]  # 最多返回3个问题
    
    def _get_confidence_level(self, score: float) -> ConfidenceLevel:
        """获取置信度级别"""
        if score >= 0.8:
            return ConfidenceLevel.VERY_HIGH
        elif score >= 0.6:
            return ConfidenceLevel.HIGH
        elif score >= 0.4:
            return ConfidenceLevel.MEDIUM
        elif score >= 0.2:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
    
    async def update_user_profile(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """更新用户画像"""
        try:
            if user_id not in self.user_profiles:
                self.user_profiles[user_id] = UserProfile(user_id=user_id, age=30, gender="unknown", constitution_type="平和质")
            
            profile = self.user_profiles[user_id]
            
            for key, value in updates.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            
            profile.updated_at = datetime.now()
            
            logger.info(f"用户画像更新成功: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"用户画像更新失败: {e}")
            return False
    
    async def record_feedback(
        self,
        user_id: str,
        recommendation_id: str,
        feedback: Dict[str, Any]
    ) -> bool:
        """记录用户反馈"""
        try:
            # 这里应该将反馈存储到数据库
            # 并用于改进推荐算法
            
            logger.info(f"记录用户反馈: {user_id} -> {recommendation_id}")
            return True
            
        except Exception as e:
            logger.error(f"记录用户反馈失败: {e}")
            return False
    
    async def get_recommendation_history(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[RecommendationResult]:
        """获取推荐历史"""
        user_history = [
            result for result in self.recommendation_history
            if result.user_id == user_id
        ]
        
        return sorted(user_history, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    async def get_statistics(self) -> Dict[str, Any]:
        """获取推荐统计"""
        total_recommendations = len(self.recommendation_history)
        
        if total_recommendations == 0:
            return {
                "total_recommendations": 0,
                "average_processing_time": 0,
                "strategy_distribution": {},
                "type_distribution": {}
            }
        
        # 计算平均处理时间
        avg_processing_time = sum(
            result.processing_time for result in self.recommendation_history
        ) / total_recommendations
        
        # 策略分布
        strategy_counts = {}
        for result in self.recommendation_history:
            strategy = result.strategy_used.value
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        
        # 类型分布
        type_counts = {}
        for result in self.recommendation_history:
            for rec in result.recommendations:
                rec_type = rec.type.value
                type_counts[rec_type] = type_counts.get(rec_type, 0) + 1
        
        return {
            "total_recommendations": total_recommendations,
            "average_processing_time": avg_processing_time,
            "strategy_distribution": strategy_counts,
            "type_distribution": type_counts,
            "active_users": len(self.user_profiles)
        }

# 全局推荐引擎实例
_recommendation_engine: Optional[RecommendationEngine] = None

def initialize_recommendation_engine(
    config: Dict[str, Any],
    metrics_collector: Optional[MetricsCollector] = None
) -> RecommendationEngine:
    """初始化推荐引擎"""
    global _recommendation_engine
    _recommendation_engine = RecommendationEngine(config, metrics_collector)
    return _recommendation_engine

def get_recommendation_engine() -> Optional[RecommendationEngine]:
    """获取推荐引擎实例"""
    return _recommendation_engine 