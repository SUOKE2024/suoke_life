#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能对话引擎 - 提供多轮对话、上下文理解、意图识别、情感分析
"""

import asyncio
import time
import json
import re
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from loguru import logger
import jieba
import jieba.posseg as pseg
from collections import defaultdict, deque

from ..observability.metrics import MetricsCollector
from ..observability.tracing import trace_operation, SpanKind


class DialogueState(str, Enum):
    """对话状态"""
    GREETING = "greeting"                   # 问候
    INFORMATION_GATHERING = "info_gathering" # 信息收集
    SYMPTOM_INQUIRY = "symptom_inquiry"     # 症状询问
    DIAGNOSIS_DISCUSSION = "diagnosis_discussion" # 诊断讨论
    TREATMENT_PLANNING = "treatment_planning" # 治疗规划
    LIFESTYLE_ADVICE = "lifestyle_advice"   # 生活建议
    FOLLOW_UP = "follow_up"                 # 随访
    EMERGENCY = "emergency"                 # 紧急情况
    CLOSING = "closing"                     # 结束对话


class IntentType(str, Enum):
    """意图类型"""
    HEALTH_CONSULTATION = "health_consultation"     # 健康咨询
    SYMPTOM_DESCRIPTION = "symptom_description"     # 症状描述
    DIAGNOSIS_REQUEST = "diagnosis_request"         # 诊断请求
    TREATMENT_INQUIRY = "treatment_inquiry"         # 治疗询问
    MEDICATION_QUESTION = "medication_question"     # 用药问题
    LIFESTYLE_GUIDANCE = "lifestyle_guidance"       # 生活指导
    PREVENTION_ADVICE = "prevention_advice"         # 预防建议
    EMERGENCY_HELP = "emergency_help"               # 紧急求助
    APPOINTMENT_BOOKING = "appointment_booking"     # 预约挂号
    GENERAL_QUESTION = "general_question"           # 一般问题
    CHITCHAT = "chitchat"                          # 闲聊
    COMPLAINT = "complaint"                        # 投诉


class EmotionType(str, Enum):
    """情感类型"""
    POSITIVE = "positive"       # 积极
    NEGATIVE = "negative"       # 消极
    NEUTRAL = "neutral"         # 中性
    ANXIOUS = "anxious"         # 焦虑
    WORRIED = "worried"         # 担心
    FRUSTRATED = "frustrated"   # 沮丧
    HOPEFUL = "hopeful"         # 希望
    GRATEFUL = "grateful"       # 感激
    CONFUSED = "confused"       # 困惑
    ANGRY = "angry"             # 愤怒


class ResponseType(str, Enum):
    """回复类型"""
    INFORMATIVE = "informative"         # 信息性
    EMPATHETIC = "empathetic"           # 共情性
    INSTRUCTIONAL = "instructional"     # 指导性
    CLARIFYING = "clarifying"           # 澄清性
    REASSURING = "reassuring"           # 安慰性
    URGENT = "urgent"                   # 紧急性
    EDUCATIONAL = "educational"         # 教育性
    CONVERSATIONAL = "conversational"   # 对话性


@dataclass
class DialogueContext:
    """对话上下文"""
    session_id: str
    user_id: str
    current_state: DialogueState
    intent_history: List[IntentType] = field(default_factory=list)
    entities: Dict[str, Any] = field(default_factory=dict)
    symptoms: List[str] = field(default_factory=list)
    concerns: List[str] = field(default_factory=list)
    user_profile: Dict[str, Any] = field(default_factory=dict)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    current_topic: Optional[str] = None
    emotion_state: EmotionType = EmotionType.NEUTRAL
    urgency_level: int = 0                          # 0-5级紧急程度
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserMessage:
    """用户消息"""
    id: str
    session_id: str
    user_id: str
    content: str
    timestamp: datetime
    intent: Optional[IntentType] = None
    entities: Dict[str, Any] = field(default_factory=dict)
    emotion: Optional[EmotionType] = None
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemResponse:
    """系统回复"""
    id: str
    session_id: str
    content: str
    response_type: ResponseType
    confidence: float
    suggestions: List[str] = field(default_factory=list)
    follow_up_questions: List[str] = field(default_factory=list)
    actions: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DialogueSession:
    """对话会话"""
    session_id: str
    user_id: str
    context: DialogueContext
    messages: List[Union[UserMessage, SystemResponse]] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    summary: str = ""
    outcome: Optional[str] = None
    satisfaction_score: Optional[float] = None


class IntentClassifier:
    """意图识别器"""
    
    def __init__(self):
        self.intent_patterns = self._load_intent_patterns()
        self.keyword_weights = self._load_keyword_weights()
    
    def _load_intent_patterns(self) -> Dict[IntentType, List[str]]:
        """加载意图模式"""
        return {
            IntentType.HEALTH_CONSULTATION: [
                r".*健康.*咨询.*", r".*身体.*问题.*", r".*不舒服.*",
                r".*看病.*", r".*医生.*", r".*检查.*"
            ],
            IntentType.SYMPTOM_DESCRIPTION: [
                r".*头痛.*", r".*发烧.*", r".*咳嗽.*", r".*疼痛.*",
                r".*症状.*", r".*不适.*", r".*难受.*"
            ],
            IntentType.DIAGNOSIS_REQUEST: [
                r".*什么病.*", r".*诊断.*", r".*是不是.*病.*",
                r".*可能.*什么.*", r".*怎么回事.*"
            ],
            IntentType.TREATMENT_INQUIRY: [
                r".*怎么治.*", r".*治疗.*方法.*", r".*怎么办.*",
                r".*如何.*治疗.*", r".*吃什么药.*"
            ],
            IntentType.MEDICATION_QUESTION: [
                r".*药.*", r".*服用.*", r".*用药.*", r".*副作用.*",
                r".*剂量.*", r".*怎么吃.*"
            ],
            IntentType.LIFESTYLE_GUIDANCE: [
                r".*生活.*", r".*饮食.*", r".*运动.*", r".*作息.*",
                r".*注意.*什么.*", r".*保养.*"
            ],
            IntentType.PREVENTION_ADVICE: [
                r".*预防.*", r".*避免.*", r".*防止.*", r".*保健.*",
                r".*养生.*", r".*如何.*不.*"
            ],
            IntentType.EMERGENCY_HELP: [
                r".*急.*", r".*紧急.*", r".*救命.*", r".*严重.*",
                r".*马上.*", r".*立即.*", r".*快.*"
            ],
            IntentType.APPOINTMENT_BOOKING: [
                r".*预约.*", r".*挂号.*", r".*看医生.*", r".*门诊.*",
                r".*时间.*", r".*安排.*"
            ],
            IntentType.CHITCHAT: [
                r".*你好.*", r".*谢谢.*", r".*再见.*", r".*天气.*",
                r".*聊天.*", r".*怎么样.*"
            ]
        }
    
    def _load_keyword_weights(self) -> Dict[str, float]:
        """加载关键词权重"""
        return {
            # 症状相关
            "头痛": 0.8, "发烧": 0.9, "咳嗽": 0.8, "疼痛": 0.7,
            "恶心": 0.7, "呕吐": 0.8, "腹泻": 0.8, "便秘": 0.6,
            "失眠": 0.7, "疲劳": 0.6, "乏力": 0.6, "头晕": 0.7,
            
            # 紧急程度
            "急": 0.9, "紧急": 0.9, "严重": 0.8, "危险": 0.9,
            "马上": 0.8, "立即": 0.8, "快": 0.7, "救命": 1.0,
            
            # 治疗相关
            "治疗": 0.8, "药": 0.7, "手术": 0.9, "检查": 0.6,
            "诊断": 0.8, "医生": 0.6, "医院": 0.6,
            
            # 情感相关
            "担心": 0.6, "害怕": 0.7, "焦虑": 0.7, "紧张": 0.6,
            "痛苦": 0.8, "难受": 0.7, "不舒服": 0.7
        }
    
    async def classify_intent(self, message: str) -> Tuple[IntentType, float]:
        """分类意图"""
        try:
            # 文本预处理
            cleaned_message = self._preprocess_text(message)
            
            # 模式匹配
            pattern_scores = {}
            for intent, patterns in self.intent_patterns.items():
                score = 0.0
                for pattern in patterns:
                    if re.search(pattern, cleaned_message):
                        score += 1.0
                
                if score > 0:
                    pattern_scores[intent] = score / len(patterns)
            
            # 关键词匹配
            keyword_scores = defaultdict(float)
            words = jieba.lcut(cleaned_message)
            
            for word in words:
                if word in self.keyword_weights:
                    weight = self.keyword_weights[word]
                    
                    # 根据关键词分配到相应意图
                    if word in ["头痛", "发烧", "咳嗽", "疼痛", "恶心", "呕吐"]:
                        keyword_scores[IntentType.SYMPTOM_DESCRIPTION] += weight
                    elif word in ["急", "紧急", "严重", "危险", "救命"]:
                        keyword_scores[IntentType.EMERGENCY_HELP] += weight
                    elif word in ["治疗", "药", "手术"]:
                        keyword_scores[IntentType.TREATMENT_INQUIRY] += weight
                    elif word in ["诊断", "什么病"]:
                        keyword_scores[IntentType.DIAGNOSIS_REQUEST] += weight
                    else:
                        keyword_scores[IntentType.HEALTH_CONSULTATION] += weight * 0.5
            
            # 合并分数
            final_scores = {}
            all_intents = set(pattern_scores.keys()) | set(keyword_scores.keys())
            
            for intent in all_intents:
                pattern_score = pattern_scores.get(intent, 0.0)
                keyword_score = keyword_scores.get(intent, 0.0)
                final_scores[intent] = pattern_score * 0.6 + keyword_score * 0.4
            
            if not final_scores:
                return IntentType.GENERAL_QUESTION, 0.5
            
            # 返回最高分的意图
            best_intent = max(final_scores.items(), key=lambda x: x[1])
            return best_intent[0], min(best_intent[1], 1.0)
            
        except Exception as e:
            logger.error(f"意图分类失败: {e}")
            return IntentType.GENERAL_QUESTION, 0.0
    
    def _preprocess_text(self, text: str) -> str:
        """文本预处理"""
        # 去除特殊字符，保留中文、英文、数字
        cleaned = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', '', text)
        return cleaned.strip()


class EntityExtractor:
    """实体提取器"""
    
    def __init__(self):
        self.entity_patterns = self._load_entity_patterns()
        self.medical_terms = self._load_medical_terms()
    
    def _load_entity_patterns(self) -> Dict[str, List[str]]:
        """加载实体模式"""
        return {
            "time": [
                r"(\d+)天前", r"(\d+)小时前", r"(\d+)分钟前",
                r"昨天", r"今天", r"前天", r"上周", r"上个月",
                r"(\d+)月(\d+)日", r"(\d+)点", r"早上", r"下午", r"晚上"
            ],
            "duration": [
                r"(\d+)天", r"(\d+)小时", r"(\d+)分钟", r"(\d+)周",
                r"(\d+)个月", r"(\d+)年", r"很久", r"一会儿", r"长期"
            ],
            "frequency": [
                r"每天", r"每周", r"每月", r"经常", r"偶尔", r"很少",
                r"(\d+)次", r"一次", r"两次", r"多次", r"反复"
            ],
            "severity": [
                r"轻微", r"严重", r"剧烈", r"轻度", r"中度", r"重度",
                r"很痛", r"非常痛", r"有点", r"一点点"
            ],
            "body_part": [
                r"头部", r"胸部", r"腹部", r"背部", r"腰部", r"腿部",
                r"手臂", r"脖子", r"肩膀", r"膝盖", r"脚踝", r"手腕"
            ],
            "age": [
                r"(\d+)岁", r"(\d+)周岁", r"年轻", r"中年", r"老年"
            ],
            "gender": [
                r"男性", r"女性", r"男", r"女", r"先生", r"女士"
            ]
        }
    
    def _load_medical_terms(self) -> Dict[str, List[str]]:
        """加载医学术语"""
        return {
            "symptoms": [
                "头痛", "发烧", "咳嗽", "恶心", "呕吐", "腹泻", "便秘",
                "失眠", "疲劳", "乏力", "头晕", "心悸", "胸闷", "气短",
                "食欲不振", "体重下降", "出汗", "畏寒", "关节痛"
            ],
            "diseases": [
                "感冒", "发烧", "肺炎", "胃炎", "高血压", "糖尿病",
                "心脏病", "肝炎", "肾炎", "关节炎", "哮喘", "过敏"
            ],
            "medications": [
                "阿司匹林", "布洛芬", "对乙酰氨基酚", "抗生素",
                "感冒药", "止痛药", "降压药", "降糖药"
            ],
            "treatments": [
                "手术", "化疗", "放疗", "物理治疗", "针灸", "按摩",
                "中药", "西药", "输液", "注射"
            ]
        }
    
    async def extract_entities(self, message: str) -> Dict[str, Any]:
        """提取实体"""
        try:
            entities = {}
            
            # 模式匹配提取
            for entity_type, patterns in self.entity_patterns.items():
                matches = []
                for pattern in patterns:
                    found = re.findall(pattern, message)
                    if found:
                        matches.extend(found)
                
                if matches:
                    entities[entity_type] = matches
            
            # 医学术语提取
            for term_type, terms in self.medical_terms.items():
                found_terms = []
                for term in terms:
                    if term in message:
                        found_terms.append(term)
                
                if found_terms:
                    entities[term_type] = found_terms
            
            # 使用jieba进行词性标注
            words = pseg.cut(message)
            
            # 提取人名、地名等
            persons = []
            places = []
            numbers = []
            
            for word, flag in words:
                if flag == 'nr':  # 人名
                    persons.append(word)
                elif flag == 'ns':  # 地名
                    places.append(word)
                elif flag == 'm':  # 数词
                    numbers.append(word)
            
            if persons:
                entities['person'] = persons
            if places:
                entities['place'] = places
            if numbers:
                entities['number'] = numbers
            
            return entities
            
        except Exception as e:
            logger.error(f"实体提取失败: {e}")
            return {}


class EmotionAnalyzer:
    """情感分析器"""
    
    def __init__(self):
        self.emotion_keywords = self._load_emotion_keywords()
        self.emotion_patterns = self._load_emotion_patterns()
    
    def _load_emotion_keywords(self) -> Dict[EmotionType, List[str]]:
        """加载情感关键词"""
        return {
            EmotionType.POSITIVE: [
                "好", "棒", "不错", "满意", "开心", "高兴", "感谢",
                "谢谢", "太好了", "很好", "舒服", "放心"
            ],
            EmotionType.NEGATIVE: [
                "不好", "糟糕", "难受", "痛苦", "失望", "沮丧",
                "绝望", "无助", "烦躁", "郁闷"
            ],
            EmotionType.ANXIOUS: [
                "担心", "焦虑", "紧张", "不安", "害怕", "恐惧",
                "忧虑", "惶恐", "慌张", "不放心"
            ],
            EmotionType.WORRIED: [
                "担心", "忧虑", "不放心", "害怕", "顾虑", "忧心",
                "挂念", "牵挂", "操心"
            ],
            EmotionType.FRUSTRATED: [
                "沮丧", "失望", "无奈", "无助", "绝望", "泄气",
                "灰心", "心灰意冷", "失落"
            ],
            EmotionType.HOPEFUL: [
                "希望", "期待", "盼望", "乐观", "有信心", "相信",
                "期盼", "憧憬", "向往"
            ],
            EmotionType.GRATEFUL: [
                "感谢", "谢谢", "感激", "感恩", "多谢", "谢了",
                "感谢您", "太感谢了"
            ],
            EmotionType.CONFUSED: [
                "困惑", "迷惑", "不明白", "不懂", "搞不清", "糊涂",
                "不理解", "疑惑", "不知道"
            ],
            EmotionType.ANGRY: [
                "生气", "愤怒", "气愤", "恼火", "火大", "暴怒",
                "愤慨", "恼怒", "气死了"
            ]
        }
    
    def _load_emotion_patterns(self) -> Dict[EmotionType, List[str]]:
        """加载情感模式"""
        return {
            EmotionType.ANXIOUS: [
                r".*会不会.*", r".*是不是.*严重.*", r".*怎么办.*",
                r".*担心.*", r".*害怕.*"
            ],
            EmotionType.FRUSTRATED: [
                r".*没用.*", r".*不行.*", r".*失望.*", r".*算了.*"
            ],
            EmotionType.GRATEFUL: [
                r".*谢谢.*", r".*感谢.*", r".*太好了.*"
            ],
            EmotionType.CONFUSED: [
                r".*不明白.*", r".*为什么.*", r".*怎么回事.*",
                r".*搞不懂.*"
            ]
        }
    
    async def analyze_emotion(self, message: str) -> Tuple[EmotionType, float]:
        """分析情感"""
        try:
            emotion_scores = defaultdict(float)
            
            # 关键词匹配
            for emotion, keywords in self.emotion_keywords.items():
                for keyword in keywords:
                    if keyword in message:
                        emotion_scores[emotion] += 1.0
            
            # 模式匹配
            for emotion, patterns in self.emotion_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, message):
                        emotion_scores[emotion] += 0.8
            
            # 标点符号分析
            if "!" in message or "！" in message:
                emotion_scores[EmotionType.ANXIOUS] += 0.3
            
            if "?" in message or "？" in message:
                emotion_scores[EmotionType.CONFUSED] += 0.2
            
            # 重复字符分析
            if re.search(r'(.)\1{2,}', message):  # 连续重复字符
                emotion_scores[EmotionType.ANXIOUS] += 0.2
            
            if not emotion_scores:
                return EmotionType.NEUTRAL, 0.5
            
            # 返回最高分的情感
            best_emotion = max(emotion_scores.items(), key=lambda x: x[1])
            confidence = min(best_emotion[1] / 3.0, 1.0)  # 归一化
            
            return best_emotion[0], confidence
            
        except Exception as e:
            logger.error(f"情感分析失败: {e}")
            return EmotionType.NEUTRAL, 0.0


class DialogueStateManager:
    """对话状态管理器"""
    
    def __init__(self):
        self.state_transitions = self._define_state_transitions()
        self.state_handlers = self._define_state_handlers()
    
    def _define_state_transitions(self) -> Dict[DialogueState, List[DialogueState]]:
        """定义状态转换规则"""
        return {
            DialogueState.GREETING: [
                DialogueState.INFORMATION_GATHERING,
                DialogueState.SYMPTOM_INQUIRY,
                DialogueState.EMERGENCY
            ],
            DialogueState.INFORMATION_GATHERING: [
                DialogueState.SYMPTOM_INQUIRY,
                DialogueState.DIAGNOSIS_DISCUSSION,
                DialogueState.EMERGENCY
            ],
            DialogueState.SYMPTOM_INQUIRY: [
                DialogueState.DIAGNOSIS_DISCUSSION,
                DialogueState.TREATMENT_PLANNING,
                DialogueState.EMERGENCY
            ],
            DialogueState.DIAGNOSIS_DISCUSSION: [
                DialogueState.TREATMENT_PLANNING,
                DialogueState.LIFESTYLE_ADVICE,
                DialogueState.FOLLOW_UP
            ],
            DialogueState.TREATMENT_PLANNING: [
                DialogueState.LIFESTYLE_ADVICE,
                DialogueState.FOLLOW_UP,
                DialogueState.CLOSING
            ],
            DialogueState.LIFESTYLE_ADVICE: [
                DialogueState.FOLLOW_UP,
                DialogueState.CLOSING
            ],
            DialogueState.FOLLOW_UP: [
                DialogueState.SYMPTOM_INQUIRY,
                DialogueState.CLOSING
            ],
            DialogueState.EMERGENCY: [
                DialogueState.TREATMENT_PLANNING,
                DialogueState.CLOSING
            ],
            DialogueState.CLOSING: []
        }
    
    def _define_state_handlers(self) -> Dict[DialogueState, str]:
        """定义状态处理器"""
        return {
            DialogueState.GREETING: "handle_greeting",
            DialogueState.INFORMATION_GATHERING: "handle_information_gathering",
            DialogueState.SYMPTOM_INQUIRY: "handle_symptom_inquiry",
            DialogueState.DIAGNOSIS_DISCUSSION: "handle_diagnosis_discussion",
            DialogueState.TREATMENT_PLANNING: "handle_treatment_planning",
            DialogueState.LIFESTYLE_ADVICE: "handle_lifestyle_advice",
            DialogueState.FOLLOW_UP: "handle_follow_up",
            DialogueState.EMERGENCY: "handle_emergency",
            DialogueState.CLOSING: "handle_closing"
        }
    
    async def determine_next_state(
        self,
        current_state: DialogueState,
        intent: IntentType,
        context: DialogueContext
    ) -> DialogueState:
        """确定下一个状态"""
        try:
            # 紧急情况优先
            if intent == IntentType.EMERGENCY_HELP or context.urgency_level >= 4:
                return DialogueState.EMERGENCY
            
            # 根据意图和当前状态确定下一状态
            if intent == IntentType.SYMPTOM_DESCRIPTION:
                if current_state == DialogueState.GREETING:
                    return DialogueState.SYMPTOM_INQUIRY
                elif current_state in [DialogueState.INFORMATION_GATHERING, DialogueState.SYMPTOM_INQUIRY]:
                    return DialogueState.SYMPTOM_INQUIRY
                else:
                    return current_state
            
            elif intent == IntentType.DIAGNOSIS_REQUEST:
                if current_state in [DialogueState.SYMPTOM_INQUIRY, DialogueState.INFORMATION_GATHERING]:
                    return DialogueState.DIAGNOSIS_DISCUSSION
                else:
                    return current_state
            
            elif intent == IntentType.TREATMENT_INQUIRY:
                if current_state in [DialogueState.DIAGNOSIS_DISCUSSION, DialogueState.SYMPTOM_INQUIRY]:
                    return DialogueState.TREATMENT_PLANNING
                else:
                    return current_state
            
            elif intent == IntentType.LIFESTYLE_GUIDANCE:
                return DialogueState.LIFESTYLE_ADVICE
            
            elif intent == IntentType.CHITCHAT:
                if current_state == DialogueState.GREETING:
                    return DialogueState.INFORMATION_GATHERING
                else:
                    return current_state
            
            # 默认状态转换
            possible_states = self.state_transitions.get(current_state, [])
            if possible_states:
                # 选择第一个可能的状态
                return possible_states[0]
            
            return current_state
            
        except Exception as e:
            logger.error(f"状态转换失败: {e}")
            return current_state


class ResponseGenerator:
    """回复生成器"""
    
    def __init__(self):
        self.response_templates = self._load_response_templates()
        self.empathy_phrases = self._load_empathy_phrases()
    
    def _load_response_templates(self) -> Dict[str, List[str]]:
        """加载回复模板"""
        return {
            "greeting": [
                "您好！我是您的健康助手，很高兴为您服务。请问有什么可以帮助您的吗？",
                "欢迎使用健康咨询服务！我会尽力为您提供专业的健康建议。",
                "您好！请告诉我您的健康问题，我会为您提供相应的建议。"
            ],
            "symptom_inquiry": [
                "我了解您的症状了。请问这种情况持续多长时间了？",
                "除了您提到的症状，还有其他不适吗？",
                "这些症状对您的日常生活有什么影响吗？",
                "请详细描述一下症状的具体表现。"
            ],
            "diagnosis_discussion": [
                "根据您描述的症状，可能的原因有几种...",
                "从您的症状来看，建议您注意以下几点...",
                "这种情况通常是由...引起的，建议您..."
            ],
            "treatment_planning": [
                "针对您的情况，我建议采取以下治疗措施...",
                "治疗方案包括以下几个方面...",
                "建议您按照以下步骤进行治疗..."
            ],
            "lifestyle_advice": [
                "在生活方式方面，建议您注意以下几点...",
                "为了改善您的健康状况，建议调整生活习惯...",
                "日常保健方面，您可以这样做..."
            ],
            "emergency": [
                "您的情况比较紧急，建议立即就医！",
                "请马上前往最近的医院急诊科！",
                "这种情况需要紧急处理，不要延误！"
            ],
            "reassurance": [
                "请不要过于担心，这种情况是可以改善的。",
                "您的担心我能理解，让我们一起来解决这个问题。",
                "保持积极的心态对康复很重要。"
            ]
        }
    
    def _load_empathy_phrases(self) -> Dict[EmotionType, List[str]]:
        """加载共情短语"""
        return {
            EmotionType.ANXIOUS: [
                "我理解您的担心，",
                "您的焦虑是可以理解的，",
                "我知道您很担心，"
            ],
            EmotionType.WORRIED: [
                "我能感受到您的担忧，",
                "您的担心是正常的，",
                "我理解您的顾虑，"
            ],
            EmotionType.FRUSTRATED: [
                "我知道您现在很沮丧，",
                "我理解您的失望，",
                "这种情况确实令人困扰，"
            ],
            EmotionType.CONFUSED: [
                "我理解您的困惑，",
                "这确实容易让人迷惑，",
                "让我来为您解释一下，"
            ],
            EmotionType.ANGRY: [
                "我理解您的愤怒，",
                "您的不满是可以理解的，",
                "我知道这让您很生气，"
            ]
        }
    
    async def generate_response(
        self,
        context: DialogueContext,
        intent: IntentType,
        entities: Dict[str, Any],
        emotion: EmotionType
    ) -> SystemResponse:
        """生成回复"""
        try:
            response_id = f"resp_{context.session_id}_{int(time.time())}"
            
            # 确定回复类型
            response_type = self._determine_response_type(intent, emotion, context)
            
            # 生成回复内容
            content = await self._generate_content(
                context, intent, entities, emotion, response_type
            )
            
            # 生成建议
            suggestions = await self._generate_suggestions(context, intent)
            
            # 生成后续问题
            follow_up_questions = await self._generate_follow_up_questions(
                context, intent, entities
            )
            
            # 生成动作
            actions = await self._generate_actions(context, intent)
            
            # 计算置信度
            confidence = self._calculate_confidence(context, intent, entities)
            
            return SystemResponse(
                id=response_id,
                session_id=context.session_id,
                content=content,
                response_type=response_type,
                confidence=confidence,
                suggestions=suggestions,
                follow_up_questions=follow_up_questions,
                actions=actions
            )
            
        except Exception as e:
            logger.error(f"生成回复失败: {e}")
            return SystemResponse(
                id=f"error_{context.session_id}_{int(time.time())}",
                session_id=context.session_id,
                content="抱歉，我现在无法为您提供回复。请稍后再试。",
                response_type=ResponseType.CONVERSATIONAL,
                confidence=0.0
            )
    
    def _determine_response_type(
        self,
        intent: IntentType,
        emotion: EmotionType,
        context: DialogueContext
    ) -> ResponseType:
        """确定回复类型"""
        # 紧急情况
        if intent == IntentType.EMERGENCY_HELP or context.urgency_level >= 4:
            return ResponseType.URGENT
        
        # 情感导向
        if emotion in [EmotionType.ANXIOUS, EmotionType.WORRIED, EmotionType.FRUSTRATED]:
            return ResponseType.EMPATHETIC
        
        # 意图导向
        if intent == IntentType.TREATMENT_INQUIRY:
            return ResponseType.INSTRUCTIONAL
        elif intent == IntentType.DIAGNOSIS_REQUEST:
            return ResponseType.INFORMATIVE
        elif intent == IntentType.LIFESTYLE_GUIDANCE:
            return ResponseType.EDUCATIONAL
        elif intent in [IntentType.GENERAL_QUESTION, IntentType.CHITCHAT]:
            return ResponseType.CONVERSATIONAL
        else:
            return ResponseType.INFORMATIVE
    
    async def _generate_content(
        self,
        context: DialogueContext,
        intent: IntentType,
        entities: Dict[str, Any],
        emotion: EmotionType,
        response_type: ResponseType
    ) -> str:
        """生成回复内容"""
        content_parts = []
        
        # 添加共情前缀
        if response_type == ResponseType.EMPATHETIC and emotion != EmotionType.NEUTRAL:
            empathy_phrases = self.empathy_phrases.get(emotion, [])
            if empathy_phrases:
                content_parts.append(empathy_phrases[0])
        
        # 根据状态生成主要内容
        state = context.current_state
        
        if state == DialogueState.GREETING:
            templates = self.response_templates["greeting"]
            content_parts.append(templates[0])
        
        elif state == DialogueState.SYMPTOM_INQUIRY:
            if context.symptoms:
                content_parts.append(f"您提到了{', '.join(context.symptoms)}的症状。")
            
            templates = self.response_templates["symptom_inquiry"]
            content_parts.append(templates[0])
        
        elif state == DialogueState.DIAGNOSIS_DISCUSSION:
            if context.symptoms:
                content_parts.append(f"根据您描述的{', '.join(context.symptoms)}症状，")
            
            templates = self.response_templates["diagnosis_discussion"]
            content_parts.append(templates[0])
        
        elif state == DialogueState.TREATMENT_PLANNING:
            templates = self.response_templates["treatment_planning"]
            content_parts.append(templates[0])
        
        elif state == DialogueState.LIFESTYLE_ADVICE:
            templates = self.response_templates["lifestyle_advice"]
            content_parts.append(templates[0])
        
        elif state == DialogueState.EMERGENCY:
            templates = self.response_templates["emergency"]
            content_parts.append(templates[0])
        
        else:
            content_parts.append("我会尽力为您提供帮助。")
        
        # 添加安慰性内容
        if emotion in [EmotionType.ANXIOUS, EmotionType.WORRIED, EmotionType.FRUSTRATED]:
            reassurance = self.response_templates["reassurance"]
            content_parts.append(reassurance[0])
        
        return "".join(content_parts)
    
    async def _generate_suggestions(
        self,
        context: DialogueContext,
        intent: IntentType
    ) -> List[str]:
        """生成建议"""
        suggestions = []
        
        if intent == IntentType.SYMPTOM_DESCRIPTION:
            suggestions.extend([
                "详细描述症状的具体表现",
                "说明症状持续的时间",
                "描述症状的严重程度"
            ])
        
        elif intent == IntentType.TREATMENT_INQUIRY:
            suggestions.extend([
                "了解具体的治疗方案",
                "询问注意事项",
                "了解预期效果"
            ])
        
        elif intent == IntentType.LIFESTYLE_GUIDANCE:
            suggestions.extend([
                "饮食调理建议",
                "运动锻炼指导",
                "作息时间安排"
            ])
        
        return suggestions[:3]  # 最多返回3个建议
    
    async def _generate_follow_up_questions(
        self,
        context: DialogueContext,
        intent: IntentType,
        entities: Dict[str, Any]
    ) -> List[str]:
        """生成后续问题"""
        questions = []
        
        if intent == IntentType.SYMPTOM_DESCRIPTION:
            questions.extend([
                "这种症状是什么时候开始的？",
                "症状的严重程度如何？",
                "有什么因素会加重或缓解症状吗？"
            ])
        
        elif intent == IntentType.HEALTH_CONSULTATION:
            questions.extend([
                "您目前有什么不适症状吗？",
                "您的年龄和性别是？",
                "您有什么既往病史吗？"
            ])
        
        elif intent == IntentType.TREATMENT_INQUIRY:
            questions.extend([
                "您目前在服用什么药物吗？",
                "您有药物过敏史吗？",
                "您希望了解哪种治疗方法？"
            ])
        
        return questions[:2]  # 最多返回2个问题
    
    async def _generate_actions(
        self,
        context: DialogueContext,
        intent: IntentType
    ) -> List[Dict[str, Any]]:
        """生成动作"""
        actions = []
        
        if intent == IntentType.EMERGENCY_HELP:
            actions.append({
                "type": "emergency_alert",
                "message": "紧急情况，建议立即就医",
                "priority": "high"
            })
        
        elif intent == IntentType.APPOINTMENT_BOOKING:
            actions.append({
                "type": "appointment_booking",
                "message": "为您安排预约挂号",
                "priority": "medium"
            })
        
        elif intent == IntentType.MEDICATION_QUESTION:
            actions.append({
                "type": "medication_check",
                "message": "检查药物相互作用",
                "priority": "medium"
            })
        
        return actions
    
    def _calculate_confidence(
        self,
        context: DialogueContext,
        intent: IntentType,
        entities: Dict[str, Any]
    ) -> float:
        """计算置信度"""
        confidence = 0.7  # 基础置信度
        
        # 根据上下文信息调整
        if context.symptoms:
            confidence += 0.1
        
        if entities:
            confidence += 0.1
        
        # 根据对话历史调整
        if len(context.conversation_history) > 3:
            confidence += 0.1
        
        return min(confidence, 1.0)


class IntelligentDialogueEngine:
    """智能对话引擎主类"""
    
    def __init__(self, config: Dict[str, Any], metrics_collector: Optional[MetricsCollector] = None):
        self.config = config
        self.metrics_collector = metrics_collector
        
        # 核心组件
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()
        self.emotion_analyzer = EmotionAnalyzer()
        self.state_manager = DialogueStateManager()
        self.response_generator = ResponseGenerator()
        
        # 会话存储
        self.active_sessions: Dict[str, DialogueSession] = {}
        self.session_timeout = config.get("session_timeout", 1800)  # 30分钟
        
        # 上下文窗口
        self.context_window_size = config.get("context_window_size", 10)
        
        # 运行状态
        self.initialized = False
    
    async def initialize(self):
        """初始化对话引擎"""
        try:
            # 初始化jieba分词
            jieba.initialize()
            
            self.initialized = True
            logger.info("智能对话引擎初始化完成")
            
        except Exception as e:
            logger.error(f"对话引擎初始化失败: {e}")
            raise
    
    @trace_operation("dialogue.process_message", SpanKind.INTERNAL)
    async def process_message(
        self,
        user_id: str,
        message_content: str,
        session_id: Optional[str] = None
    ) -> SystemResponse:
        """处理用户消息"""
        try:
            if not self.initialized:
                await self.initialize()
            
            # 获取或创建会话
            session = await self._get_or_create_session(user_id, session_id)
            
            # 创建用户消息
            user_message = UserMessage(
                id=f"msg_{session.session_id}_{int(time.time())}",
                session_id=session.session_id,
                user_id=user_id,
                content=message_content,
                timestamp=datetime.now()
            )
            
            # 意图识别
            intent, intent_confidence = await self.intent_classifier.classify_intent(
                message_content
            )
            user_message.intent = intent
            user_message.confidence = intent_confidence
            
            # 实体提取
            entities = await self.entity_extractor.extract_entities(message_content)
            user_message.entities = entities
            
            # 情感分析
            emotion, emotion_confidence = await self.emotion_analyzer.analyze_emotion(
                message_content
            )
            user_message.emotion = emotion
            
            # 更新上下文
            await self._update_context(session.context, user_message, entities)
            
            # 状态转换
            next_state = await self.state_manager.determine_next_state(
                session.context.current_state, intent, session.context
            )
            session.context.current_state = next_state
            
            # 生成回复
            system_response = await self.response_generator.generate_response(
                session.context, intent, entities, emotion
            )
            
            # 更新会话
            session.messages.append(user_message)
            session.messages.append(system_response)
            session.last_activity = datetime.now()
            
            # 维护上下文窗口
            await self._maintain_context_window(session)
            
            # 记录指标
            if self.metrics_collector:
                await self.metrics_collector.increment_counter(
                    "dialogue_messages_processed",
                    {
                        "user_id": user_id,
                        "intent": intent.value,
                        "emotion": emotion.value,
                        "state": next_state.value
                    }
                )
                
                await self.metrics_collector.record_histogram(
                    "intent_confidence",
                    intent_confidence,
                    {"intent": intent.value}
                )
            
            logger.info(f"处理消息成功: {user_id} -> {intent.value}")
            return system_response
            
        except Exception as e:
            logger.error(f"处理消息失败: {e}")
            
            # 返回错误回复
            return SystemResponse(
                id=f"error_{int(time.time())}",
                session_id=session_id or "unknown",
                content="抱歉，我现在无法理解您的消息。请重新表达或稍后再试。",
                response_type=ResponseType.CONVERSATIONAL,
                confidence=0.0
            )
    
    async def _get_or_create_session(
        self,
        user_id: str,
        session_id: Optional[str] = None
    ) -> DialogueSession:
        """获取或创建会话"""
        # 清理过期会话
        await self._cleanup_expired_sessions()
        
        if session_id and session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.last_activity = datetime.now()
            return session
        
        # 创建新会话
        new_session_id = session_id or f"session_{user_id}_{int(time.time())}"
        
        context = DialogueContext(
            session_id=new_session_id,
            user_id=user_id,
            current_state=DialogueState.GREETING
        )
        
        session = DialogueSession(
            session_id=new_session_id,
            user_id=user_id,
            context=context
        )
        
        self.active_sessions[new_session_id] = session
        return session
    
    async def _update_context(
        self,
        context: DialogueContext,
        user_message: UserMessage,
        entities: Dict[str, Any]
    ):
        """更新对话上下文"""
        # 更新意图历史
        if user_message.intent:
            context.intent_history.append(user_message.intent)
            
            # 保持历史长度
            if len(context.intent_history) > 10:
                context.intent_history = context.intent_history[-10:]
        
        # 更新实体
        for entity_type, entity_values in entities.items():
            if entity_type not in context.entities:
                context.entities[entity_type] = []
            
            if isinstance(entity_values, list):
                context.entities[entity_type].extend(entity_values)
            else:
                context.entities[entity_type].append(entity_values)
        
        # 更新症状
        if "symptoms" in entities:
            for symptom in entities["symptoms"]:
                if symptom not in context.symptoms:
                    context.symptoms.append(symptom)
        
        # 更新情感状态
        if user_message.emotion:
            context.emotion_state = user_message.emotion
        
        # 更新紧急程度
        if user_message.intent == IntentType.EMERGENCY_HELP:
            context.urgency_level = 5
        elif "severity" in entities:
            severity_terms = entities["severity"]
            if any(term in ["严重", "剧烈", "非常痛"] for term in severity_terms):
                context.urgency_level = max(context.urgency_level, 3)
        
        # 更新对话历史
        context.conversation_history.append({
            "timestamp": user_message.timestamp.isoformat(),
            "content": user_message.content,
            "intent": user_message.intent.value if user_message.intent else None,
            "emotion": user_message.emotion.value if user_message.emotion else None,
            "entities": entities
        })
        
        context.updated_at = datetime.now()
    
    async def _maintain_context_window(self, session: DialogueSession):
        """维护上下文窗口"""
        # 保持消息历史长度
        if len(session.messages) > self.context_window_size * 2:  # 用户+系统消息
            session.messages = session.messages[-(self.context_window_size * 2):]
        
        # 保持对话历史长度
        if len(session.context.conversation_history) > self.context_window_size:
            session.context.conversation_history = session.context.conversation_history[-self.context_window_size:]
    
    async def _cleanup_expired_sessions(self):
        """清理过期会话"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.active_sessions.items():
            if (current_time - session.last_activity).seconds > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            session = self.active_sessions.pop(session_id)
            session.is_active = False
            logger.info(f"会话过期: {session_id}")
    
    async def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话信息"""
        session = self.active_sessions.get(session_id)
        if not session:
            return None
        
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "current_state": session.context.current_state.value,
            "message_count": len(session.messages),
            "start_time": session.start_time.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "symptoms": session.context.symptoms,
            "emotion_state": session.context.emotion_state.value,
            "urgency_level": session.context.urgency_level,
            "is_active": session.is_active
        }
    
    async def end_session(self, session_id: str, summary: str = "") -> bool:
        """结束会话"""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return False
            
            session.is_active = False
            session.summary = summary
            session.context.current_state = DialogueState.CLOSING
            
            # 从活跃会话中移除
            self.active_sessions.pop(session_id, None)
            
            logger.info(f"会话结束: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"结束会话失败: {e}")
            return False
    
    async def get_dialogue_statistics(self) -> Dict[str, Any]:
        """获取对话统计"""
        try:
            active_sessions_count = len(self.active_sessions)
            
            # 统计状态分布
            state_distribution = defaultdict(int)
            emotion_distribution = defaultdict(int)
            intent_distribution = defaultdict(int)
            
            for session in self.active_sessions.values():
                state_distribution[session.context.current_state.value] += 1
                emotion_distribution[session.context.emotion_state.value] += 1
                
                # 统计最近的意图
                if session.context.intent_history:
                    recent_intent = session.context.intent_history[-1]
                    intent_distribution[recent_intent.value] += 1
            
            # 计算平均会话时长
            total_duration = 0
            session_count = 0
            
            for session in self.active_sessions.values():
                duration = (session.last_activity - session.start_time).seconds
                total_duration += duration
                session_count += 1
            
            avg_session_duration = total_duration / session_count if session_count > 0 else 0
            
            return {
                "active_sessions": active_sessions_count,
                "average_session_duration": avg_session_duration,
                "state_distribution": dict(state_distribution),
                "emotion_distribution": dict(emotion_distribution),
                "intent_distribution": dict(intent_distribution)
            }
            
        except Exception as e:
            logger.error(f"获取对话统计失败: {e}")
            return {}


# 全局对话引擎实例
_dialogue_engine: Optional[IntelligentDialogueEngine] = None


def initialize_dialogue_engine(
    config: Dict[str, Any],
    metrics_collector: Optional[MetricsCollector] = None
) -> IntelligentDialogueEngine:
    """初始化对话引擎"""
    global _dialogue_engine
    _dialogue_engine = IntelligentDialogueEngine(config, metrics_collector)
    return _dialogue_engine


def get_dialogue_engine() -> Optional[IntelligentDialogueEngine]:
    """获取对话引擎实例"""
    return _dialogue_engine 