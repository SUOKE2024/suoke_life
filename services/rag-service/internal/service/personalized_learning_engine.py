#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
个性化学习引擎 - 提供自适应学习、知识图谱构建、学习路径规划
"""

import asyncio
import time
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from loguru import logger
import networkx as nx
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

from ..observability.metrics import MetricsCollector
from ..observability.tracing import trace_operation, SpanKind


class LearningObjectiveType(str, Enum):
    """学习目标类型"""
    KNOWLEDGE_ACQUISITION = "knowledge_acquisition"     # 知识获取
    SKILL_DEVELOPMENT = "skill_development"             # 技能发展
    BEHAVIOR_CHANGE = "behavior_change"                 # 行为改变
    HEALTH_IMPROVEMENT = "health_improvement"           # 健康改善
    PREVENTION_AWARENESS = "prevention_awareness"       # 预防意识
    TCM_UNDERSTANDING = "tcm_understanding"             # 中医理解
    LIFESTYLE_OPTIMIZATION = "lifestyle_optimization"   # 生活方式优化
    SYMPTOM_MANAGEMENT = "symptom_management"           # 症状管理


class LearningStyle(str, Enum):
    """学习风格"""
    VISUAL = "visual"                   # 视觉型
    AUDITORY = "auditory"               # 听觉型
    KINESTHETIC = "kinesthetic"         # 动觉型
    READING_WRITING = "reading_writing" # 读写型
    MULTIMODAL = "multimodal"           # 多模态


class DifficultyLevel(str, Enum):
    """难度级别"""
    BEGINNER = "beginner"       # 初级
    INTERMEDIATE = "intermediate" # 中级
    ADVANCED = "advanced"       # 高级
    EXPERT = "expert"           # 专家级


class LearningStatus(str, Enum):
    """学习状态"""
    NOT_STARTED = "not_started"     # 未开始
    IN_PROGRESS = "in_progress"     # 进行中
    COMPLETED = "completed"         # 已完成
    MASTERED = "mastered"           # 已掌握
    NEEDS_REVIEW = "needs_review"   # 需要复习
    STRUGGLING = "struggling"       # 困难中


class ContentType(str, Enum):
    """内容类型"""
    TEXT = "text"                   # 文本
    VIDEO = "video"                 # 视频
    AUDIO = "audio"                 # 音频
    INTERACTIVE = "interactive"     # 交互式
    QUIZ = "quiz"                   # 测验
    CASE_STUDY = "case_study"       # 案例研究
    SIMULATION = "simulation"       # 模拟
    PRACTICE = "practice"           # 练习


@dataclass
class LearningObjective:
    """学习目标"""
    id: str
    type: LearningObjectiveType
    title: str
    description: str
    difficulty: DifficultyLevel
    estimated_time: int                             # 预计学习时间（分钟）
    prerequisites: List[str] = field(default_factory=list)
    skills_gained: List[str] = field(default_factory=list)
    assessment_criteria: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LearningContent:
    """学习内容"""
    id: str
    objective_id: str
    title: str
    description: str
    content_type: ContentType
    difficulty: DifficultyLevel
    duration: int                                   # 内容时长（分钟）
    content_data: Dict[str, Any]                    # 内容数据
    learning_styles: List[LearningStyle] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class LearnerProfile:
    """学习者画像"""
    user_id: str
    learning_style: LearningStyle
    preferred_difficulty: DifficultyLevel
    learning_pace: float                            # 学习速度倍数
    attention_span: int                             # 注意力持续时间（分钟）
    preferred_content_types: List[ContentType] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    interests: List[str] = field(default_factory=list)
    goals: List[str] = field(default_factory=list)
    available_time: int = 30                        # 每日可用学习时间（分钟）
    timezone: str = "UTC"
    language: str = "zh-CN"
    accessibility_needs: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class LearningProgress:
    """学习进度"""
    user_id: str
    objective_id: str
    content_id: str
    status: LearningStatus
    progress_percentage: float                      # 进度百分比
    time_spent: int                                 # 已花费时间（分钟）
    attempts: int = 0                               # 尝试次数
    score: Optional[float] = None                   # 得分
    mastery_level: float = 0.0                      # 掌握程度
    last_accessed: datetime = field(default_factory=datetime.now)
    completion_date: Optional[datetime] = None
    notes: str = ""
    feedback: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LearningPath:
    """学习路径"""
    id: str
    user_id: str
    title: str
    description: str
    objectives: List[str]                           # 学习目标ID列表
    estimated_duration: int                         # 预计总时长（分钟）
    difficulty: DifficultyLevel
    personalization_score: float                   # 个性化匹配分数
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LearningRecommendation:
    """学习推荐"""
    id: str
    user_id: str
    content_id: str
    objective_id: str
    recommendation_type: str                        # 推荐类型
    confidence_score: float                         # 置信度
    reasoning: str                                  # 推荐理由
    priority: int = 1                               # 优先级
    valid_until: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class KnowledgeGraph:
    """知识图谱"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.concept_embeddings = {}
        self.relationship_types = {
            "prerequisite": "前置条件",
            "builds_on": "基于",
            "related_to": "相关",
            "part_of": "属于",
            "example_of": "示例",
            "opposite_of": "相反",
            "causes": "导致",
            "treats": "治疗"
        }
    
    def add_concept(self, concept_id: str, concept_data: Dict[str, Any]):
        """添加概念节点"""
        self.graph.add_node(concept_id, **concept_data)
    
    def add_relationship(self, source: str, target: str, relationship_type: str, weight: float = 1.0):
        """添加关系边"""
        self.graph.add_edge(source, target, type=relationship_type, weight=weight)
    
    def get_prerequisites(self, concept_id: str) -> List[str]:
        """获取前置概念"""
        prerequisites = []
        for pred in self.graph.predecessors(concept_id):
            edge_data = self.graph[pred][concept_id]
            if edge_data.get('type') == 'prerequisite':
                prerequisites.append(pred)
        return prerequisites
    
    def get_related_concepts(self, concept_id: str, max_distance: int = 2) -> List[Tuple[str, float]]:
        """获取相关概念"""
        try:
            # 使用最短路径算法找到相关概念
            paths = nx.single_source_shortest_path_length(
                self.graph, concept_id, cutoff=max_distance
            )
            
            related = []
            for target, distance in paths.items():
                if target != concept_id and distance > 0:
                    # 计算相关性分数（距离越近分数越高）
                    score = 1.0 / distance
                    related.append((target, score))
            
            return sorted(related, key=lambda x: x[1], reverse=True)
            
        except Exception as e:
            logger.error(f"获取相关概念失败: {e}")
            return []
    
    def find_learning_path(self, start_concept: str, target_concept: str) -> List[str]:
        """找到学习路径"""
        try:
            path = nx.shortest_path(self.graph, start_concept, target_concept)
            return path
        except nx.NetworkXNoPath:
            return []
        except Exception as e:
            logger.error(f"查找学习路径失败: {e}")
            return []
    
    def get_concept_difficulty(self, concept_id: str) -> float:
        """计算概念难度"""
        if concept_id not in self.graph:
            return 0.5
        
        # 基于前置条件数量和图中位置计算难度
        prerequisites = len(self.get_prerequisites(concept_id))
        
        # 计算在图中的深度
        try:
            # 找到所有没有前置条件的根节点
            root_nodes = [n for n in self.graph.nodes() if self.graph.in_degree(n) == 0]
            
            if not root_nodes:
                depth = 0
            else:
                depths = []
                for root in root_nodes:
                    try:
                        path_length = nx.shortest_path_length(self.graph, root, concept_id)
                        depths.append(path_length)
                    except nx.NetworkXNoPath:
                        continue
                
                depth = min(depths) if depths else 0
            
            # 归一化难度分数
            difficulty = min((prerequisites * 0.3 + depth * 0.7) / 10.0, 1.0)
            return difficulty
            
        except Exception as e:
            logger.error(f"计算概念难度失败: {e}")
            return 0.5


class AdaptiveLearningEngine:
    """自适应学习引擎"""
    
    def __init__(self):
        self.learner_models = {}
        self.content_difficulty_cache = {}
        self.performance_history = {}
    
    def update_learner_model(self, user_id: str, performance_data: Dict[str, Any]):
        """更新学习者模型"""
        if user_id not in self.learner_models:
            self.learner_models[user_id] = {
                "ability_level": 0.5,
                "learning_rate": 0.1,
                "retention_rate": 0.8,
                "preferred_difficulty": 0.5,
                "engagement_level": 0.7
            }
        
        model = self.learner_models[user_id]
        
        # 更新能力水平
        if "score" in performance_data:
            score = performance_data["score"]
            model["ability_level"] = 0.9 * model["ability_level"] + 0.1 * score
        
        # 更新学习率
        if "time_spent" in performance_data and "expected_time" in performance_data:
            time_ratio = performance_data["expected_time"] / max(performance_data["time_spent"], 1)
            model["learning_rate"] = 0.9 * model["learning_rate"] + 0.1 * time_ratio
        
        # 更新参与度
        if "engagement_score" in performance_data:
            engagement = performance_data["engagement_score"]
            model["engagement_level"] = 0.9 * model["engagement_level"] + 0.1 * engagement
    
    def predict_performance(self, user_id: str, content_difficulty: float) -> float:
        """预测学习表现"""
        if user_id not in self.learner_models:
            return 0.5
        
        model = self.learner_models[user_id]
        ability = model["ability_level"]
        
        # 使用简化的IRT模型预测表现
        difficulty_diff = ability - content_difficulty
        probability = 1 / (1 + np.exp(-difficulty_diff))
        
        return probability
    
    def recommend_difficulty(self, user_id: str) -> float:
        """推荐适合的难度"""
        if user_id not in self.learner_models:
            return 0.5
        
        model = self.learner_models[user_id]
        
        # 推荐略高于当前能力水平的难度
        recommended_difficulty = model["ability_level"] + 0.1
        return min(recommended_difficulty, 1.0)
    
    def adapt_content_sequence(self, user_id: str, content_list: List[str]) -> List[str]:
        """自适应内容序列"""
        if user_id not in self.learner_models:
            return content_list
        
        model = self.learner_models[user_id]
        ability = model["ability_level"]
        
        # 根据学习者能力重新排序内容
        content_with_scores = []
        for content_id in content_list:
            difficulty = self.content_difficulty_cache.get(content_id, 0.5)
            
            # 计算适合度分数
            suitability = 1 - abs(ability - difficulty)
            content_with_scores.append((content_id, suitability))
        
        # 按适合度排序
        sorted_content = sorted(content_with_scores, key=lambda x: x[1], reverse=True)
        return [content_id for content_id, _ in sorted_content]


class LearningPathPlanner:
    """学习路径规划器"""
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.knowledge_graph = knowledge_graph
        self.path_cache = {}
    
    def plan_learning_path(
        self,
        user_id: str,
        target_objectives: List[str],
        learner_profile: LearnerProfile,
        time_constraint: Optional[int] = None
    ) -> LearningPath:
        """规划学习路径"""
        
        # 分析目标之间的依赖关系
        ordered_objectives = self._order_objectives_by_dependencies(target_objectives)
        
        # 估算总时长
        total_duration = self._estimate_total_duration(ordered_objectives, learner_profile)
        
        # 如果有时间约束，调整路径
        if time_constraint and total_duration > time_constraint:
            ordered_objectives = self._optimize_for_time_constraint(
                ordered_objectives, learner_profile, time_constraint
            )
            total_duration = time_constraint
        
        # 计算个性化匹配分数
        personalization_score = self._calculate_personalization_score(
            ordered_objectives, learner_profile
        )
        
        # 确定整体难度
        overall_difficulty = self._determine_overall_difficulty(ordered_objectives)
        
        path_id = f"path_{user_id}_{int(time.time())}"
        
        return LearningPath(
            id=path_id,
            user_id=user_id,
            title=f"个性化学习路径 - {len(ordered_objectives)}个目标",
            description=f"根据您的学习风格和目标定制的学习路径",
            objectives=ordered_objectives,
            estimated_duration=total_duration,
            difficulty=overall_difficulty,
            personalization_score=personalization_score
        )
    
    def _order_objectives_by_dependencies(self, objectives: List[str]) -> List[str]:
        """根据依赖关系排序目标"""
        # 创建子图包含相关目标
        subgraph = self.knowledge_graph.graph.subgraph(objectives)
        
        try:
            # 拓扑排序
            ordered = list(nx.topological_sort(subgraph))
            return ordered
        except nx.NetworkXError:
            # 如果有循环依赖，使用简单排序
            return objectives
    
    def _estimate_total_duration(self, objectives: List[str], learner_profile: LearnerProfile) -> int:
        """估算总学习时长"""
        total_time = 0
        
        for obj_id in objectives:
            # 基础时间（这里应该从数据库获取）
            base_time = 60  # 假设每个目标基础时间60分钟
            
            # 根据学习者特征调整
            adjusted_time = base_time / learner_profile.learning_pace
            
            total_time += int(adjusted_time)
        
        return total_time
    
    def _optimize_for_time_constraint(
        self,
        objectives: List[str],
        learner_profile: LearnerProfile,
        time_constraint: int
    ) -> List[str]:
        """在时间约束下优化目标"""
        
        # 计算每个目标的优先级分数
        objective_scores = []
        for obj_id in objectives:
            # 基于重要性、难度、学习者兴趣计算分数
            importance = 1.0  # 这里应该从目标数据获取
            difficulty = self.knowledge_graph.get_concept_difficulty(obj_id)
            interest_match = 0.8  # 这里应该基于学习者兴趣计算
            
            score = importance * 0.5 + (1 - difficulty) * 0.3 + interest_match * 0.2
            objective_scores.append((obj_id, score))
        
        # 按分数排序并选择前N个
        sorted_objectives = sorted(objective_scores, key=lambda x: x[1], reverse=True)
        
        selected_objectives = []
        total_time = 0
        
        for obj_id, score in sorted_objectives:
            estimated_time = 60 / learner_profile.learning_pace  # 简化估算
            
            if total_time + estimated_time <= time_constraint:
                selected_objectives.append(obj_id)
                total_time += estimated_time
            else:
                break
        
        return selected_objectives
    
    def _calculate_personalization_score(
        self,
        objectives: List[str],
        learner_profile: LearnerProfile
    ) -> float:
        """计算个性化匹配分数"""
        
        total_score = 0.0
        
        for obj_id in objectives:
            # 难度匹配
            obj_difficulty = self.knowledge_graph.get_concept_difficulty(obj_id)
            difficulty_match = 1 - abs(obj_difficulty - 0.5)  # 假设偏好中等难度
            
            # 兴趣匹配（简化）
            interest_match = 0.8
            
            # 学习风格匹配（简化）
            style_match = 0.7
            
            obj_score = (difficulty_match + interest_match + style_match) / 3
            total_score += obj_score
        
        return total_score / len(objectives) if objectives else 0.0
    
    def _determine_overall_difficulty(self, objectives: List[str]) -> DifficultyLevel:
        """确定整体难度级别"""
        if not objectives:
            return DifficultyLevel.BEGINNER
        
        difficulties = [
            self.knowledge_graph.get_concept_difficulty(obj_id)
            for obj_id in objectives
        ]
        
        avg_difficulty = sum(difficulties) / len(difficulties)
        
        if avg_difficulty < 0.3:
            return DifficultyLevel.BEGINNER
        elif avg_difficulty < 0.6:
            return DifficultyLevel.INTERMEDIATE
        elif avg_difficulty < 0.8:
            return DifficultyLevel.ADVANCED
        else:
            return DifficultyLevel.EXPERT


class PersonalizedLearningEngine:
    """个性化学习引擎主类"""
    
    def __init__(self, config: Dict[str, Any], metrics_collector: Optional[MetricsCollector] = None):
        self.config = config
        self.metrics_collector = metrics_collector
        
        # 核心组件
        self.knowledge_graph = KnowledgeGraph()
        self.adaptive_engine = AdaptiveLearningEngine()
        self.path_planner = LearningPathPlanner(self.knowledge_graph)
        
        # 数据存储
        self.learner_profiles: Dict[str, LearnerProfile] = {}
        self.learning_objectives: Dict[str, LearningObjective] = {}
        self.learning_contents: Dict[str, LearningContent] = {}
        self.learning_progress: Dict[str, List[LearningProgress]] = {}
        self.learning_paths: Dict[str, LearningPath] = {}
        
        # 推荐系统
        self.content_vectorizer = TfidfVectorizer(max_features=1000)
        self.content_vectors = None
        
        # 运行状态
        self.initialized = False
    
    async def initialize(self):
        """初始化学习引擎"""
        try:
            # 加载知识图谱
            await self._load_knowledge_graph()
            
            # 加载学习内容
            await self._load_learning_contents()
            
            # 加载学习目标
            await self._load_learning_objectives()
            
            # 训练内容向量化模型
            await self._train_content_vectorizer()
            
            self.initialized = True
            logger.info("个性化学习引擎初始化完成")
            
        except Exception as e:
            logger.error(f"学习引擎初始化失败: {e}")
            raise
    
    async def _load_knowledge_graph(self):
        """加载知识图谱"""
        # 添加中医相关概念
        tcm_concepts = {
            "中医基础理论": {
                "type": "theory",
                "difficulty": 0.3,
                "description": "中医学的基本理论框架"
            },
            "阴阳学说": {
                "type": "theory",
                "difficulty": 0.4,
                "description": "中医学的核心理论之一"
            },
            "五行学说": {
                "type": "theory",
                "difficulty": 0.5,
                "description": "中医学的重要理论基础"
            },
            "脏腑学说": {
                "type": "anatomy",
                "difficulty": 0.6,
                "description": "中医对人体脏腑的认识"
            },
            "经络学说": {
                "type": "anatomy",
                "difficulty": 0.7,
                "description": "中医对经络系统的理论"
            },
            "辨证论治": {
                "type": "diagnosis",
                "difficulty": 0.8,
                "description": "中医诊断和治疗的核心方法"
            },
            "中药学": {
                "type": "pharmacology",
                "difficulty": 0.6,
                "description": "中医药物学"
            },
            "方剂学": {
                "type": "prescription",
                "difficulty": 0.7,
                "description": "中医方剂配伍理论"
            }
        }
        
        # 添加概念节点
        for concept_id, concept_data in tcm_concepts.items():
            self.knowledge_graph.add_concept(concept_id, concept_data)
        
        # 添加关系
        relationships = [
            ("中医基础理论", "阴阳学说", "part_of"),
            ("中医基础理论", "五行学说", "part_of"),
            ("阴阳学说", "脏腑学说", "prerequisite"),
            ("五行学说", "脏腑学说", "prerequisite"),
            ("脏腑学说", "经络学说", "related_to"),
            ("脏腑学说", "辨证论治", "prerequisite"),
            ("经络学说", "辨证论治", "prerequisite"),
            ("辨证论治", "中药学", "related_to"),
            ("中药学", "方剂学", "prerequisite")
        ]
        
        for source, target, rel_type in relationships:
            self.knowledge_graph.add_relationship(source, target, rel_type)
    
    async def _load_learning_objectives(self):
        """加载学习目标"""
        objectives_data = [
            {
                "id": "obj_tcm_basics",
                "type": LearningObjectiveType.KNOWLEDGE_ACQUISITION,
                "title": "掌握中医基础理论",
                "description": "学习和理解中医学的基本理论框架",
                "difficulty": DifficultyLevel.BEGINNER,
                "estimated_time": 120,
                "prerequisites": [],
                "skills_gained": ["中医理论理解", "基础概念掌握"],
                "tags": ["中医", "基础", "理论"]
            },
            {
                "id": "obj_syndrome_differentiation",
                "type": LearningObjectiveType.SKILL_DEVELOPMENT,
                "title": "学会辨证论治",
                "description": "掌握中医辨证论治的方法和技巧",
                "difficulty": DifficultyLevel.ADVANCED,
                "estimated_time": 240,
                "prerequisites": ["obj_tcm_basics"],
                "skills_gained": ["辨证能力", "诊断技能"],
                "tags": ["辨证", "诊断", "技能"]
            },
            {
                "id": "obj_health_preservation",
                "type": LearningObjectiveType.LIFESTYLE_OPTIMIZATION,
                "title": "学习养生保健",
                "description": "掌握中医养生保健的理论和方法",
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "estimated_time": 180,
                "prerequisites": ["obj_tcm_basics"],
                "skills_gained": ["养生知识", "保健方法"],
                "tags": ["养生", "保健", "预防"]
            }
        ]
        
        for obj_data in objectives_data:
            objective = LearningObjective(**obj_data)
            self.learning_objectives[objective.id] = objective
    
    async def _load_learning_contents(self):
        """加载学习内容"""
        contents_data = [
            {
                "id": "content_yin_yang_theory",
                "objective_id": "obj_tcm_basics",
                "title": "阴阳学说详解",
                "description": "深入了解阴阳学说的基本概念和应用",
                "content_type": ContentType.TEXT,
                "difficulty": DifficultyLevel.BEGINNER,
                "duration": 30,
                "content_data": {
                    "text": "阴阳学说是中医学的重要理论基础...",
                    "images": ["yin_yang_diagram.jpg"],
                    "examples": ["阴阳在人体中的体现"]
                },
                "learning_styles": [LearningStyle.VISUAL, LearningStyle.READING_WRITING],
                "tags": ["阴阳", "理论", "基础"]
            },
            {
                "id": "content_five_elements",
                "objective_id": "obj_tcm_basics",
                "title": "五行学说",
                "description": "学习五行学说的基本内容和临床应用",
                "content_type": ContentType.INTERACTIVE,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "duration": 45,
                "content_data": {
                    "interactive_elements": ["五行相生相克图", "脏腑五行归属"],
                    "exercises": ["五行关系练习"]
                },
                "learning_styles": [LearningStyle.VISUAL, LearningStyle.KINESTHETIC],
                "tags": ["五行", "相生相克", "脏腑"]
            },
            {
                "id": "content_syndrome_cases",
                "objective_id": "obj_syndrome_differentiation",
                "title": "辨证论治案例分析",
                "description": "通过实际案例学习辨证论治的方法",
                "content_type": ContentType.CASE_STUDY,
                "difficulty": DifficultyLevel.ADVANCED,
                "duration": 60,
                "content_data": {
                    "cases": [
                        {
                            "patient": "张某，女，45岁",
                            "symptoms": ["头晕", "心悸", "失眠"],
                            "diagnosis": "心血虚证",
                            "treatment": "养血安神"
                        }
                    ]
                },
                "learning_styles": [LearningStyle.READING_WRITING, LearningStyle.VISUAL],
                "tags": ["案例", "辨证", "实践"]
            }
        ]
        
        for content_data in contents_data:
            content = LearningContent(**content_data)
            self.learning_contents[content.id] = content
    
    async def _train_content_vectorizer(self):
        """训练内容向量化模型"""
        if not self.learning_contents:
            return
        
        # 提取内容文本特征
        content_texts = []
        for content in self.learning_contents.values():
            text_features = [
                content.title,
                content.description,
                " ".join(content.tags)
            ]
            content_texts.append(" ".join(text_features))
        
        # 训练TF-IDF向量化器
        self.content_vectors = self.content_vectorizer.fit_transform(content_texts)
        
        logger.info("内容向量化模型训练完成")
    
    @trace_operation("learning.create_learner_profile", SpanKind.INTERNAL)
    async def create_learner_profile(
        self,
        user_id: str,
        profile_data: Dict[str, Any]
    ) -> LearnerProfile:
        """创建学习者画像"""
        try:
            # 设置默认值
            defaults = {
                "learning_style": LearningStyle.MULTIMODAL,
                "preferred_difficulty": DifficultyLevel.INTERMEDIATE,
                "learning_pace": 1.0,
                "attention_span": 30,
                "preferred_content_types": [ContentType.TEXT, ContentType.INTERACTIVE],
                "available_time": 30,
                "timezone": "Asia/Shanghai",
                "language": "zh-CN"
            }
            
            # 合并用户数据和默认值
            merged_data = {**defaults, **profile_data, "user_id": user_id}
            
            profile = LearnerProfile(**merged_data)
            self.learner_profiles[user_id] = profile
            
            logger.info(f"创建学习者画像成功: {user_id}")
            return profile
            
        except Exception as e:
            logger.error(f"创建学习者画像失败: {e}")
            raise
    
    @trace_operation("learning.generate_learning_path", SpanKind.INTERNAL)
    async def generate_learning_path(
        self,
        user_id: str,
        target_objectives: List[str],
        time_constraint: Optional[int] = None
    ) -> LearningPath:
        """生成个性化学习路径"""
        try:
            if not self.initialized:
                await self.initialize()
            
            # 获取学习者画像
            learner_profile = self.learner_profiles.get(user_id)
            if not learner_profile:
                # 创建默认画像
                learner_profile = await self.create_learner_profile(user_id, {})
            
            # 规划学习路径
            learning_path = self.path_planner.plan_learning_path(
                user_id, target_objectives, learner_profile, time_constraint
            )
            
            # 保存路径
            self.learning_paths[learning_path.id] = learning_path
            
            # 记录指标
            if self.metrics_collector:
                await self.metrics_collector.increment_counter(
                    "learning_paths_generated",
                    {"user_id": user_id, "objectives_count": str(len(target_objectives))}
                )
            
            logger.info(f"生成学习路径成功: {learning_path.id}")
            return learning_path
            
        except Exception as e:
            logger.error(f"生成学习路径失败: {e}")
            raise
    
    @trace_operation("learning.recommend_content", SpanKind.INTERNAL)
    async def recommend_content(
        self,
        user_id: str,
        objective_id: str,
        max_recommendations: int = 5
    ) -> List[LearningRecommendation]:
        """推荐学习内容"""
        try:
            if not self.initialized:
                await self.initialize()
            
            # 获取学习者画像
            learner_profile = self.learner_profiles.get(user_id)
            if not learner_profile:
                learner_profile = await self.create_learner_profile(user_id, {})
            
            # 获取相关内容
            relevant_contents = [
                content for content in self.learning_contents.values()
                if content.objective_id == objective_id
            ]
            
            if not relevant_contents:
                return []
            
            recommendations = []
            
            for content in relevant_contents:
                # 计算推荐分数
                score = await self._calculate_content_recommendation_score(
                    content, learner_profile
                )
                
                # 生成推荐理由
                reasoning = await self._generate_recommendation_reasoning(
                    content, learner_profile, score
                )
                
                recommendation = LearningRecommendation(
                    id=f"rec_{user_id}_{content.id}_{int(time.time())}",
                    user_id=user_id,
                    content_id=content.id,
                    objective_id=objective_id,
                    recommendation_type="content_recommendation",
                    confidence_score=score,
                    reasoning=reasoning,
                    priority=self._calculate_priority(score)
                )
                
                recommendations.append(recommendation)
            
            # 按分数排序并限制数量
            recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
            return recommendations[:max_recommendations]
            
        except Exception as e:
            logger.error(f"推荐学习内容失败: {e}")
            return []
    
    async def _calculate_content_recommendation_score(
        self,
        content: LearningContent,
        learner_profile: LearnerProfile
    ) -> float:
        """计算内容推荐分数"""
        score = 0.0
        
        # 学习风格匹配
        if learner_profile.learning_style in content.learning_styles:
            score += 0.3
        elif LearningStyle.MULTIMODAL in content.learning_styles:
            score += 0.2
        
        # 内容类型偏好匹配
        if content.content_type in learner_profile.preferred_content_types:
            score += 0.2
        
        # 难度匹配
        difficulty_mapping = {
            DifficultyLevel.BEGINNER: 0.2,
            DifficultyLevel.INTERMEDIATE: 0.5,
            DifficultyLevel.ADVANCED: 0.8,
            DifficultyLevel.EXPERT: 1.0
        }
        
        content_difficulty = difficulty_mapping.get(content.difficulty, 0.5)
        preferred_difficulty = difficulty_mapping.get(learner_profile.preferred_difficulty, 0.5)
        
        difficulty_match = 1 - abs(content_difficulty - preferred_difficulty)
        score += difficulty_match * 0.3
        
        # 时长匹配
        if content.duration <= learner_profile.attention_span:
            score += 0.2
        else:
            # 时长超出注意力持续时间的惩罚
            time_penalty = (content.duration - learner_profile.attention_span) / content.duration
            score += 0.2 * (1 - time_penalty)
        
        return min(score, 1.0)
    
    async def _generate_recommendation_reasoning(
        self,
        content: LearningContent,
        learner_profile: LearnerProfile,
        score: float
    ) -> str:
        """生成推荐理由"""
        reasons = []
        
        if learner_profile.learning_style in content.learning_styles:
            reasons.append(f"匹配您的{learner_profile.learning_style.value}学习风格")
        
        if content.content_type in learner_profile.preferred_content_types:
            reasons.append(f"符合您偏好的{content.content_type.value}内容类型")
        
        if content.duration <= learner_profile.attention_span:
            reasons.append(f"内容时长({content.duration}分钟)适合您的注意力持续时间")
        
        if score > 0.8:
            reasons.append("高度推荐")
        elif score > 0.6:
            reasons.append("推荐")
        
        return "；".join(reasons) if reasons else "基于您的学习偏好推荐"
    
    def _calculate_priority(self, score: float) -> int:
        """计算优先级"""
        if score >= 0.8:
            return 1  # 高优先级
        elif score >= 0.6:
            return 2  # 中优先级
        elif score >= 0.4:
            return 3  # 低优先级
        else:
            return 4  # 很低优先级
    
    @trace_operation("learning.update_progress", SpanKind.INTERNAL)
    async def update_learning_progress(
        self,
        user_id: str,
        content_id: str,
        progress_data: Dict[str, Any]
    ) -> bool:
        """更新学习进度"""
        try:
            # 获取或创建进度记录
            if user_id not in self.learning_progress:
                self.learning_progress[user_id] = []
            
            user_progress = self.learning_progress[user_id]
            
            # 查找现有进度记录
            existing_progress = None
            for progress in user_progress:
                if progress.content_id == content_id:
                    existing_progress = progress
                    break
            
            if existing_progress:
                # 更新现有记录
                for key, value in progress_data.items():
                    if hasattr(existing_progress, key):
                        setattr(existing_progress, key, value)
                existing_progress.last_accessed = datetime.now()
            else:
                # 创建新记录
                content = self.learning_contents.get(content_id)
                if not content:
                    logger.error(f"内容不存在: {content_id}")
                    return False
                
                progress = LearningProgress(
                    user_id=user_id,
                    objective_id=content.objective_id,
                    content_id=content_id,
                    status=LearningStatus.IN_PROGRESS,
                    progress_percentage=0.0,
                    time_spent=0,
                    **progress_data
                )
                user_progress.append(progress)
            
            # 更新自适应学习模型
            self.adaptive_engine.update_learner_model(user_id, progress_data)
            
            # 记录指标
            if self.metrics_collector:
                await self.metrics_collector.increment_counter(
                    "learning_progress_updates",
                    {"user_id": user_id, "content_id": content_id}
                )
            
            logger.info(f"更新学习进度成功: {user_id} -> {content_id}")
            return True
            
        except Exception as e:
            logger.error(f"更新学习进度失败: {e}")
            return False
    
    async def get_learning_analytics(self, user_id: str) -> Dict[str, Any]:
        """获取学习分析数据"""
        try:
            user_progress = self.learning_progress.get(user_id, [])
            
            if not user_progress:
                return {
                    "total_content": 0,
                    "completed_content": 0,
                    "total_time_spent": 0,
                    "average_score": 0,
                    "learning_streak": 0,
                    "mastery_levels": {},
                    "progress_by_objective": {}
                }
            
            # 基本统计
            total_content = len(user_progress)
            completed_content = len([p for p in user_progress if p.status == LearningStatus.COMPLETED])
            total_time_spent = sum(p.time_spent for p in user_progress)
            
            # 平均分数
            scores = [p.score for p in user_progress if p.score is not None]
            average_score = sum(scores) / len(scores) if scores else 0
            
            # 学习连续天数（简化计算）
            learning_dates = set(p.last_accessed.date() for p in user_progress)
            learning_streak = len(learning_dates)
            
            # 按目标分组的进度
            progress_by_objective = {}
            for progress in user_progress:
                obj_id = progress.objective_id
                if obj_id not in progress_by_objective:
                    progress_by_objective[obj_id] = {
                        "total_content": 0,
                        "completed_content": 0,
                        "average_progress": 0,
                        "time_spent": 0
                    }
                
                obj_progress = progress_by_objective[obj_id]
                obj_progress["total_content"] += 1
                if progress.status == LearningStatus.COMPLETED:
                    obj_progress["completed_content"] += 1
                obj_progress["time_spent"] += progress.time_spent
            
            # 计算平均进度
            for obj_id, obj_data in progress_by_objective.items():
                obj_progresses = [p.progress_percentage for p in user_progress if p.objective_id == obj_id]
                obj_data["average_progress"] = sum(obj_progresses) / len(obj_progresses) if obj_progresses else 0
            
            # 掌握水平
            mastery_levels = {}
            for progress in user_progress:
                obj_id = progress.objective_id
                if obj_id not in mastery_levels:
                    mastery_levels[obj_id] = []
                mastery_levels[obj_id].append(progress.mastery_level)
            
            # 计算平均掌握水平
            for obj_id, levels in mastery_levels.items():
                mastery_levels[obj_id] = sum(levels) / len(levels) if levels else 0
            
            return {
                "total_content": total_content,
                "completed_content": completed_content,
                "completion_rate": completed_content / total_content if total_content > 0 else 0,
                "total_time_spent": total_time_spent,
                "average_score": average_score,
                "learning_streak": learning_streak,
                "mastery_levels": mastery_levels,
                "progress_by_objective": progress_by_objective
            }
            
        except Exception as e:
            logger.error(f"获取学习分析数据失败: {e}")
            return {}
    
    async def adapt_learning_experience(self, user_id: str) -> Dict[str, Any]:
        """自适应调整学习体验"""
        try:
            # 获取学习者模型
            learner_model = self.adaptive_engine.learner_models.get(user_id)
            if not learner_model:
                return {"message": "学习者模型不存在"}
            
            # 推荐适合的难度
            recommended_difficulty = self.adaptive_engine.recommend_difficulty(user_id)
            
            # 获取学习进度
            user_progress = self.learning_progress.get(user_id, [])
            
            # 分析学习模式
            learning_patterns = self._analyze_learning_patterns(user_progress)
            
            # 生成自适应建议
            adaptations = {
                "recommended_difficulty": recommended_difficulty,
                "learning_patterns": learning_patterns,
                "suggestions": []
            }
            
            # 基于能力水平的建议
            ability = learner_model["ability_level"]
            if ability < 0.3:
                adaptations["suggestions"].append("建议从基础内容开始，循序渐进")
            elif ability > 0.8:
                adaptations["suggestions"].append("可以尝试更具挑战性的高级内容")
            
            # 基于学习率的建议
            learning_rate = learner_model["learning_rate"]
            if learning_rate < 0.5:
                adaptations["suggestions"].append("建议增加学习时间，放慢学习节奏")
            elif learning_rate > 1.5:
                adaptations["suggestions"].append("学习效率很高，可以尝试更多内容")
            
            # 基于参与度的建议
            engagement = learner_model["engagement_level"]
            if engagement < 0.5:
                adaptations["suggestions"].append("建议尝试更多互动性内容提高参与度")
            
            return adaptations
            
        except Exception as e:
            logger.error(f"自适应调整学习体验失败: {e}")
            return {"error": str(e)}
    
    def _analyze_learning_patterns(self, user_progress: List[LearningProgress]) -> Dict[str, Any]:
        """分析学习模式"""
        if not user_progress:
            return {}
        
        # 学习时间模式
        learning_times = [p.last_accessed.hour for p in user_progress]
        most_active_hour = max(set(learning_times), key=learning_times.count) if learning_times else 0
        
        # 学习持续时间模式
        session_durations = [p.time_spent for p in user_progress if p.time_spent > 0]
        avg_session_duration = sum(session_durations) / len(session_durations) if session_durations else 0
        
        # 学习频率
        learning_dates = [p.last_accessed.date() for p in user_progress]
        unique_dates = len(set(learning_dates))
        
        # 完成率模式
        completion_rates = [p.progress_percentage for p in user_progress]
        avg_completion_rate = sum(completion_rates) / len(completion_rates) if completion_rates else 0
        
        return {
            "most_active_hour": most_active_hour,
            "average_session_duration": avg_session_duration,
            "learning_frequency": unique_dates,
            "average_completion_rate": avg_completion_rate,
            "total_sessions": len(user_progress)
        }
    
    async def get_next_learning_recommendation(self, user_id: str) -> Optional[LearningRecommendation]:
        """获取下一个学习推荐"""
        try:
            # 获取用户的学习路径
            user_paths = [path for path in self.learning_paths.values() if path.user_id == user_id]
            if not user_paths:
                return None
            
            # 获取最新的学习路径
            latest_path = max(user_paths, key=lambda x: x.created_at)
            
            # 获取用户进度
            user_progress = self.learning_progress.get(user_id, [])
            completed_objectives = set(
                p.objective_id for p in user_progress 
                if p.status == LearningStatus.COMPLETED
            )
            
            # 找到下一个未完成的目标
            next_objective = None
            for obj_id in latest_path.objectives:
                if obj_id not in completed_objectives:
                    # 检查前置条件是否满足
                    objective = self.learning_objectives.get(obj_id)
                    if objective:
                        prerequisites_met = all(
                            prereq in completed_objectives 
                            for prereq in objective.prerequisites
                        )
                        if prerequisites_met:
                            next_objective = obj_id
                            break
            
            if not next_objective:
                return None
            
            # 推荐该目标的内容
            recommendations = await self.recommend_content(user_id, next_objective, 1)
            return recommendations[0] if recommendations else None
            
        except Exception as e:
            logger.error(f"获取下一个学习推荐失败: {e}")
            return None


# 全局学习引擎实例
_learning_engine: Optional[PersonalizedLearningEngine] = None


def initialize_learning_engine(
    config: Dict[str, Any],
    metrics_collector: Optional[MetricsCollector] = None
) -> PersonalizedLearningEngine:
    """初始化学习引擎"""
    global _learning_engine
    _learning_engine = PersonalizedLearningEngine(config, metrics_collector)
    return _learning_engine


def get_learning_engine() -> Optional[PersonalizedLearningEngine]:
    """获取学习引擎实例"""
    return _learning_engine 