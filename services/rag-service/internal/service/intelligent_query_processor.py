#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能查询处理器 - 提供高级查询理解和处理能力
"""

import re
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from loguru import logger
import jieba
import jieba.posseg as pseg
from datetime import datetime, timedelta

from ..model.document import Document


class QueryType(Enum):
    """查询类型枚举"""
    HEALTH_CONSULTATION = "health_consultation"  # 健康咨询
    SYMPTOM_ANALYSIS = "symptom_analysis"        # 症状分析
    TCM_DIAGNOSIS = "tcm_diagnosis"              # 中医诊断
    TREATMENT_PLAN = "treatment_plan"            # 治疗方案
    PREVENTION_ADVICE = "prevention_advice"      # 预防建议
    LIFESTYLE_GUIDANCE = "lifestyle_guidance"    # 生活指导
    EMERGENCY_HELP = "emergency_help"            # 紧急求助
    KNOWLEDGE_SEARCH = "knowledge_search"        # 知识搜索
    FOLLOW_UP = "follow_up"                      # 随访跟进
    GENERAL_CHAT = "general_chat"                # 一般聊天


class QueryIntent(Enum):
    """查询意图枚举"""
    INFORMATION_SEEKING = "information_seeking"   # 信息寻求
    PROBLEM_SOLVING = "problem_solving"          # 问题解决
    DECISION_SUPPORT = "decision_support"        # 决策支持
    EMOTIONAL_SUPPORT = "emotional_support"      # 情感支持
    CLARIFICATION = "clarification"              # 澄清确认
    COMPARISON = "comparison"                    # 比较分析
    RECOMMENDATION = "recommendation"            # 推荐建议


class QueryComplexity(Enum):
    """查询复杂度枚举"""
    SIMPLE = "simple"        # 简单查询
    MODERATE = "moderate"    # 中等复杂度
    COMPLEX = "complex"      # 复杂查询
    EXPERT = "expert"        # 专家级查询


@dataclass
class QueryContext:
    """查询上下文"""
    user_id: str
    session_id: str
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    user_profile: Optional[Dict[str, Any]] = None
    health_context: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None
    current_symptoms: List[str] = field(default_factory=list)
    current_concerns: List[str] = field(default_factory=list)
    follow_up_questions: List[str] = field(default_factory=list)
    last_interaction: Optional[datetime] = None


@dataclass
class QueryAnalysis:
    """查询分析结果"""
    original_query: str
    normalized_query: str
    query_type: QueryType
    query_intent: QueryIntent
    complexity: QueryComplexity
    entities: List[Dict[str, Any]] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    symptoms: List[str] = field(default_factory=list)
    body_parts: List[str] = field(default_factory=list)
    emotions: List[str] = field(default_factory=list)
    urgency_level: int = 1  # 1-5级紧急程度
    confidence_score: float = 0.0
    suggested_agent: Optional[str] = None
    requires_clarification: bool = False
    clarification_questions: List[str] = field(default_factory=list)


class IntelligentQueryProcessor:
    """智能查询处理器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化智能查询处理器
        
        Args:
            config: 配置信息
        """
        self.config = config
        
        # 中医术语词典
        self.tcm_terms = self._load_tcm_terms()
        
        # 症状词典
        self.symptom_dict = self._load_symptom_dict()
        
        # 身体部位词典
        self.body_parts_dict = self._load_body_parts_dict()
        
        # 情感词典
        self.emotion_dict = self._load_emotion_dict()
        
        # 紧急关键词
        self.emergency_keywords = self._load_emergency_keywords()
        
        # 查询模式
        self.query_patterns = self._load_query_patterns()
        
        # 上下文管理器
        self.context_manager = {}
        
        # 初始化jieba分词
        self._init_jieba()
    
    def _load_tcm_terms(self) -> Dict[str, List[str]]:
        """加载中医术语词典"""
        return {
            "constitution": ["阳虚", "阴虚", "气虚", "血虚", "痰湿", "湿热", "血瘀", "气郁", "特禀"],
            "syndrome": ["风寒", "风热", "湿热", "痰湿", "血瘀", "气滞", "肾虚", "脾虚"],
            "organs": ["心", "肝", "脾", "肺", "肾", "胆", "胃", "小肠", "大肠", "膀胱", "三焦"],
            "meridians": ["手太阴", "手阳明", "足阳明", "足太阴", "手少阴", "手太阳"],
            "treatments": ["针灸", "推拿", "拔罐", "刮痧", "艾灸", "中药", "食疗", "气功"]
        }
    
    def _load_symptom_dict(self) -> Set[str]:
        """加载症状词典"""
        return {
            "头痛", "头晕", "发热", "咳嗽", "胸闷", "心悸", "失眠", "乏力",
            "腹痛", "腹泻", "便秘", "恶心", "呕吐", "食欲不振", "口干", "口苦",
            "腰痛", "关节痛", "肌肉酸痛", "手脚冰凉", "出汗", "盗汗", "耳鸣",
            "视力模糊", "皮疹", "瘙痒", "水肿", "尿频", "尿急", "月经不调"
        }
    
    def _load_body_parts_dict(self) -> Set[str]:
        """加载身体部位词典"""
        return {
            "头部", "颈部", "胸部", "腹部", "腰部", "背部", "四肢", "手", "脚",
            "眼睛", "耳朵", "鼻子", "嘴巴", "舌头", "牙齿", "喉咙", "心脏",
            "肺", "肝", "肾", "胃", "肠", "膀胱", "子宫", "前列腺"
        }
    
    def _load_emotion_dict(self) -> Dict[str, List[str]]:
        """加载情感词典"""
        return {
            "anxiety": ["焦虑", "担心", "紧张", "不安", "恐惧", "害怕"],
            "depression": ["抑郁", "沮丧", "悲伤", "绝望", "无助", "消沉"],
            "anger": ["愤怒", "生气", "烦躁", "易怒", "暴躁"],
            "stress": ["压力", "紧张", "疲劳", "疲惫", "劳累"],
            "positive": ["开心", "高兴", "愉快", "满意", "感谢", "希望"]
        }
    
    def _load_emergency_keywords(self) -> Set[str]:
        """加载紧急关键词"""
        return {
            "急救", "紧急", "危险", "严重", "剧烈", "突然", "昏迷", "休克",
            "大出血", "呼吸困难", "胸痛", "心梗", "中风", "骨折", "中毒"
        }
    
    def _load_query_patterns(self) -> Dict[str, List[str]]:
        """加载查询模式"""
        return {
            "symptom_inquiry": [
                r"我.*?(痛|疼|不舒服|难受)",
                r"(头|胸|腹|腰|背).*?(痛|疼)",
                r"最近.*?(咳嗽|发热|头晕|失眠)",
                r"感觉.*?(乏力|疲劳|不适)"
            ],
            "diagnosis_request": [
                r"这是什么病",
                r"我得了.*?吗",
                r"是不是.*?(病|症)",
                r"帮我看看.*?(症状|情况)"
            ],
            "treatment_inquiry": [
                r"怎么治疗",
                r"吃什么药",
                r"如何调理",
                r"有什么办法"
            ],
            "prevention_inquiry": [
                r"如何预防",
                r"怎么避免",
                r"注意什么",
                r"预防.*?(方法|措施)"
            ]
        }
    
    def _init_jieba(self):
        """初始化jieba分词"""
        # 添加中医术语到jieba词典
        for category, terms in self.tcm_terms.items():
            for term in terms:
                jieba.add_word(term)
        
        # 添加症状词汇
        for symptom in self.symptom_dict:
            jieba.add_word(symptom)
        
        # 添加身体部位词汇
        for part in self.body_parts_dict:
            jieba.add_word(part)
    
    async def process_query(
        self,
        query: str,
        context: Optional[QueryContext] = None
    ) -> QueryAnalysis:
        """
        处理查询，返回分析结果
        
        Args:
            query: 用户查询
            context: 查询上下文
            
        Returns:
            查询分析结果
        """
        logger.info(f"Processing query: {query}")
        
        # 查询预处理
        normalized_query = self._normalize_query(query)
        
        # 实体识别
        entities = await self._extract_entities(normalized_query)
        
        # 关键词提取
        keywords = self._extract_keywords(normalized_query)
        
        # 症状识别
        symptoms = self._extract_symptoms(normalized_query)
        
        # 身体部位识别
        body_parts = self._extract_body_parts(normalized_query)
        
        # 情感分析
        emotions = self._analyze_emotions(normalized_query)
        
        # 查询类型识别
        query_type = self._classify_query_type(normalized_query, entities, symptoms)
        
        # 意图识别
        query_intent = self._identify_intent(normalized_query, query_type)
        
        # 复杂度评估
        complexity = self._assess_complexity(normalized_query, entities, symptoms)
        
        # 紧急程度评估
        urgency_level = self._assess_urgency(normalized_query, symptoms, emotions)
        
        # 智能体推荐
        suggested_agent = self._suggest_agent(query_type, complexity, urgency_level)
        
        # 澄清需求检测
        requires_clarification, clarification_questions = self._check_clarification_needs(
            normalized_query, entities, symptoms, context
        )
        
        # 置信度计算
        confidence_score = self._calculate_confidence(
            entities, symptoms, body_parts, query_type, query_intent
        )
        
        analysis = QueryAnalysis(
            original_query=query,
            normalized_query=normalized_query,
            query_type=query_type,
            query_intent=query_intent,
            complexity=complexity,
            entities=entities,
            keywords=keywords,
            symptoms=symptoms,
            body_parts=body_parts,
            emotions=emotions,
            urgency_level=urgency_level,
            confidence_score=confidence_score,
            suggested_agent=suggested_agent,
            requires_clarification=requires_clarification,
            clarification_questions=clarification_questions
        )
        
        # 更新上下文
        if context:
            await self._update_context(context, analysis)
        
        logger.info(f"Query analysis completed: {analysis.query_type.value}")
        return analysis
    
    def _normalize_query(self, query: str) -> str:
        """查询标准化"""
        # 去除多余空格
        query = re.sub(r'\s+', ' ', query.strip())
        
        # 繁体转简体（如果需要）
        # query = self._traditional_to_simplified(query)
        
        # 标点符号标准化
        query = re.sub(r'[，。！？；：]', ',', query)
        
        return query
    
    async def _extract_entities(self, query: str) -> List[Dict[str, Any]]:
        """实体识别"""
        entities = []
        
        # 使用jieba进行词性标注
        words = pseg.cut(query)
        
        for word, flag in words:
            entity = {
                "text": word,
                "label": self._map_pos_to_entity_type(flag),
                "start": query.find(word),
                "end": query.find(word) + len(word),
                "confidence": 0.8
            }
            
            # 检查是否为中医术语
            if self._is_tcm_term(word):
                entity["label"] = "TCM_TERM"
                entity["confidence"] = 0.9
            
            # 检查是否为症状
            elif word in self.symptom_dict:
                entity["label"] = "SYMPTOM"
                entity["confidence"] = 0.95
            
            # 检查是否为身体部位
            elif word in self.body_parts_dict:
                entity["label"] = "BODY_PART"
                entity["confidence"] = 0.9
            
            if entity["label"] != "OTHER":
                entities.append(entity)
        
        return entities
    
    def _extract_keywords(self, query: str) -> List[str]:
        """关键词提取"""
        # 使用jieba分词
        words = jieba.cut(query)
        
        # 过滤停用词和标点
        stopwords = {"的", "了", "是", "我", "你", "他", "她", "它", "在", "有", "和", "与"}
        keywords = [word for word in words if word not in stopwords and len(word) > 1]
        
        return keywords
    
    def _extract_symptoms(self, query: str) -> List[str]:
        """症状提取"""
        symptoms = []
        for symptom in self.symptom_dict:
            if symptom in query:
                symptoms.append(symptom)
        return symptoms
    
    def _extract_body_parts(self, query: str) -> List[str]:
        """身体部位提取"""
        body_parts = []
        for part in self.body_parts_dict:
            if part in query:
                body_parts.append(part)
        return body_parts
    
    def _analyze_emotions(self, query: str) -> List[str]:
        """情感分析"""
        emotions = []
        for emotion_type, emotion_words in self.emotion_dict.items():
            for word in emotion_words:
                if word in query:
                    emotions.append(emotion_type)
                    break
        return emotions
    
    def _classify_query_type(
        self,
        query: str,
        entities: List[Dict[str, Any]],
        symptoms: List[str]
    ) -> QueryType:
        """查询类型分类"""
        # 检查紧急关键词
        for keyword in self.emergency_keywords:
            if keyword in query:
                return QueryType.EMERGENCY_HELP
        
        # 检查查询模式
        for pattern_type, patterns in self.query_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query):
                    if pattern_type == "symptom_inquiry":
                        return QueryType.SYMPTOM_ANALYSIS
                    elif pattern_type == "diagnosis_request":
                        return QueryType.TCM_DIAGNOSIS
                    elif pattern_type == "treatment_inquiry":
                        return QueryType.TREATMENT_PLAN
                    elif pattern_type == "prevention_inquiry":
                        return QueryType.PREVENTION_ADVICE
        
        # 基于实体和症状判断
        if symptoms:
            return QueryType.SYMPTOM_ANALYSIS
        
        # 检查中医相关术语
        tcm_entity_count = sum(1 for entity in entities if entity["label"] == "TCM_TERM")
        if tcm_entity_count > 0:
            return QueryType.TCM_DIAGNOSIS
        
        # 默认为健康咨询
        return QueryType.HEALTH_CONSULTATION
    
    def _identify_intent(self, query: str, query_type: QueryType) -> QueryIntent:
        """意图识别"""
        # 基于查询类型和关键词判断意图
        if "推荐" in query or "建议" in query:
            return QueryIntent.RECOMMENDATION
        elif "比较" in query or "哪个好" in query:
            return QueryIntent.COMPARISON
        elif "怎么办" in query or "如何" in query:
            return QueryIntent.PROBLEM_SOLVING
        elif "是什么" in query or "什么是" in query:
            return QueryIntent.INFORMATION_SEEKING
        elif "选择" in query or "决定" in query:
            return QueryIntent.DECISION_SUPPORT
        elif "担心" in query or "害怕" in query:
            return QueryIntent.EMOTIONAL_SUPPORT
        elif "确认" in query or "是不是" in query:
            return QueryIntent.CLARIFICATION
        else:
            return QueryIntent.INFORMATION_SEEKING
    
    def _assess_complexity(
        self,
        query: str,
        entities: List[Dict[str, Any]],
        symptoms: List[str]
    ) -> QueryComplexity:
        """复杂度评估"""
        complexity_score = 0
        
        # 基于查询长度
        if len(query) > 100:
            complexity_score += 2
        elif len(query) > 50:
            complexity_score += 1
        
        # 基于实体数量
        complexity_score += len(entities) * 0.5
        
        # 基于症状数量
        complexity_score += len(symptoms) * 0.8
        
        # 基于专业术语
        tcm_terms = sum(1 for entity in entities if entity["label"] == "TCM_TERM")
        complexity_score += tcm_terms * 1.2
        
        if complexity_score >= 5:
            return QueryComplexity.EXPERT
        elif complexity_score >= 3:
            return QueryComplexity.COMPLEX
        elif complexity_score >= 1:
            return QueryComplexity.MODERATE
        else:
            return QueryComplexity.SIMPLE
    
    def _assess_urgency(
        self,
        query: str,
        symptoms: List[str],
        emotions: List[str]
    ) -> int:
        """紧急程度评估"""
        urgency_score = 1
        
        # 检查紧急关键词
        for keyword in self.emergency_keywords:
            if keyword in query:
                urgency_score = 5
                break
        
        # 检查严重症状
        severe_symptoms = {"剧烈疼痛", "呼吸困难", "胸痛", "昏迷", "大出血"}
        for symptom in symptoms:
            if any(severe in symptom for severe in severe_symptoms):
                urgency_score = max(urgency_score, 4)
        
        # 检查情感状态
        if "anxiety" in emotions or "depression" in emotions:
            urgency_score = max(urgency_score, 3)
        
        return min(urgency_score, 5)
    
    def _suggest_agent(
        self,
        query_type: QueryType,
        complexity: QueryComplexity,
        urgency_level: int
    ) -> str:
        """智能体推荐"""
        # 紧急情况优先老克
        if urgency_level >= 4:
            return "laoke"
        
        # 基于查询类型推荐
        if query_type in [QueryType.TCM_DIAGNOSIS, QueryType.TREATMENT_PLAN]:
            if complexity == QueryComplexity.EXPERT:
                return "laoke"  # 资深专家
            else:
                return "xiaoke"  # 专业诊断
        
        elif query_type in [QueryType.PREVENTION_ADVICE, QueryType.LIFESTYLE_GUIDANCE]:
            return "soer"  # 健康管理
        
        elif query_type == QueryType.EMERGENCY_HELP:
            return "laoke"  # 资深专家
        
        else:
            return "xiaoai"  # AI助手
    
    def _check_clarification_needs(
        self,
        query: str,
        entities: List[Dict[str, Any]],
        symptoms: List[str],
        context: Optional[QueryContext]
    ) -> Tuple[bool, List[str]]:
        """检查是否需要澄清"""
        clarification_questions = []
        
        # 查询过于简短
        if len(query) < 10:
            clarification_questions.append("能否详细描述一下您的具体情况？")
        
        # 症状描述不清
        if symptoms and len(symptoms) == 1:
            clarification_questions.append(f"除了{symptoms[0]}，还有其他症状吗？")
        
        # 缺少时间信息
        if symptoms and not any(word in query for word in ["最近", "今天", "昨天", "几天"]):
            clarification_questions.append("这些症状持续多长时间了？")
        
        # 缺少程度信息
        if symptoms and not any(word in query for word in ["轻微", "严重", "剧烈", "偶尔"]):
            clarification_questions.append("症状的严重程度如何？")
        
        return len(clarification_questions) > 0, clarification_questions
    
    def _calculate_confidence(
        self,
        entities: List[Dict[str, Any]],
        symptoms: List[str],
        body_parts: List[str],
        query_type: QueryType,
        query_intent: QueryIntent
    ) -> float:
        """计算置信度"""
        confidence = 0.5  # 基础置信度
        
        # 基于实体数量和质量
        if entities:
            avg_entity_confidence = sum(e["confidence"] for e in entities) / len(entities)
            confidence += avg_entity_confidence * 0.3
        
        # 基于症状识别
        if symptoms:
            confidence += min(len(symptoms) * 0.1, 0.2)
        
        # 基于身体部位识别
        if body_parts:
            confidence += min(len(body_parts) * 0.05, 0.1)
        
        # 基于查询类型匹配度
        if query_type != QueryType.GENERAL_CHAT:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    async def _update_context(self, context: QueryContext, analysis: QueryAnalysis):
        """更新查询上下文"""
        # 添加到对话历史
        context.conversation_history.append({
            "timestamp": datetime.now(),
            "query": analysis.original_query,
            "analysis": analysis
        })
        
        # 更新当前症状
        context.current_symptoms.extend(analysis.symptoms)
        context.current_symptoms = list(set(context.current_symptoms))  # 去重
        
        # 更新关注点
        if analysis.query_type in [QueryType.SYMPTOM_ANALYSIS, QueryType.TCM_DIAGNOSIS]:
            context.current_concerns.extend(analysis.symptoms)
            context.current_concerns = list(set(context.current_concerns))
        
        # 添加后续问题
        if analysis.clarification_questions:
            context.follow_up_questions.extend(analysis.clarification_questions)
        
        # 更新最后交互时间
        context.last_interaction = datetime.now()
        
        # 存储上下文
        self.context_manager[context.session_id] = context
    
    def _map_pos_to_entity_type(self, pos: str) -> str:
        """词性标注到实体类型映射"""
        pos_mapping = {
            "n": "NOUN",
            "v": "VERB",
            "a": "ADJECTIVE",
            "nr": "PERSON",
            "ns": "LOCATION",
            "nt": "TIME",
            "nz": "OTHER_NOUN"
        }
        return pos_mapping.get(pos, "OTHER")
    
    def _is_tcm_term(self, word: str) -> bool:
        """检查是否为中医术语"""
        for category, terms in self.tcm_terms.items():
            if word in terms:
                return True
        return False
    
    async def get_context(self, session_id: str) -> Optional[QueryContext]:
        """获取会话上下文"""
        return self.context_manager.get(session_id)
    
    async def clear_context(self, session_id: str) -> bool:
        """清除会话上下文"""
        if session_id in self.context_manager:
            del self.context_manager[session_id]
            return True
        return False
    
    async def get_query_suggestions(
        self,
        partial_query: str,
        context: Optional[QueryContext] = None
    ) -> List[str]:
        """获取查询建议"""
        suggestions = []
        
        # 基于症状的建议
        for symptom in self.symptom_dict:
            if symptom.startswith(partial_query):
                suggestions.append(f"我{symptom}怎么办？")
        
        # 基于中医术语的建议
        for category, terms in self.tcm_terms.items():
            for term in terms:
                if term.startswith(partial_query):
                    suggestions.append(f"什么是{term}？")
        
        # 基于上下文的建议
        if context and context.current_symptoms:
            for symptom in context.current_symptoms:
                suggestions.append(f"{symptom}如何调理？")
                suggestions.append(f"{symptom}需要注意什么？")
        
        return suggestions[:5]  # 返回前5个建议 