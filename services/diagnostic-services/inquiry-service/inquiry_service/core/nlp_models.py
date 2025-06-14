"""
nlp_models - 索克生活项目模块
"""

from collections import defaultdict, Counter
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any, Set
import asyncio
import jieba
import jieba.posseg as pseg
import json
import logging
import numpy as np
import re

"""
问诊服务NLP模型

基于深度学习和自然语言处理技术，实现智能问诊对话、症状识别、
语义理解、情感分析等核心NLP功能。
"""


logger = logging.getLogger(__name__)

class IntentType(str, Enum):
    """意图类型"""
    SYMPTOM_DESCRIPTION = "症状描述"
    PAIN_INQUIRY = "疼痛询问"
    DURATION_INQUIRY = "持续时间询问"
    SEVERITY_INQUIRY = "严重程度询问"
    MEDICAL_HISTORY = "病史询问"
    MEDICATION_INQUIRY = "用药询问"
    LIFESTYLE_INQUIRY = "生活方式询问"
    EMOTIONAL_STATE = "情绪状态"
    CONFIRMATION = "确认"
    DENIAL = "否认"
    UNCLEAR = "不清楚"

class EmotionType(str, Enum):
    """情绪类型"""
    ANXIOUS = "焦虑"
    WORRIED = "担心"
    CALM = "平静"
    FRUSTRATED = "沮丧"
    HOPEFUL = "希望"
    CONFUSED = "困惑"
    ANGRY = "愤怒"
    NEUTRAL = "中性"

@dataclass
class SemanticEntity:
    """语义实体"""
    text: str                    # 实体文本
    entity_type: str            # 实体类型
    start_pos: int              # 开始位置
    end_pos: int                # 结束位置
    confidence: float           # 置信度
    attributes: Dict[str, Any] = field(default_factory = dict)

@dataclass
class IntentAnalysisResult:
    """意图分析结果"""
    intent: IntentType          # 识别的意图
    confidence: float           # 置信度
    entities: List[SemanticEntity]  # 提取的实体
    keywords: List[str]         # 关键词
    context_info: Dict[str, Any] = field(default_factory = dict)

@dataclass
class EmotionAnalysisResult:
    """情感分析结果"""
    primary_emotion: EmotionType  # 主要情绪
    emotion_scores: Dict[EmotionType, float]  # 各情绪得分
    emotional_intensity: float   # 情绪强度
    sentiment_polarity: float    # 情感极性 ( - 1到1)
    confidence: float

@dataclass
class SymptomExtractionResult:
    """症状提取结果"""
    symptoms: List[Dict[str, Any]]  # 提取的症状
    body_parts: List[str]          # 涉及的身体部位
    temporal_info: Dict[str, str]  # 时间信息
    severity_indicators: List[str] # 严重程度指标
    confidence: float

@dataclass
class DialogueUnderstandingResult:
    """对话理解结果"""
    intent_analysis: IntentAnalysisResult
    emotion_analysis: EmotionAnalysisResult
    symptom_extraction: SymptomExtractionResult
    response_suggestions: List[str]
    next_questions: List[str]
    overall_confidence: float

class AdvancedEntityExtractor:
    """高级实体提取器"""

    def __init__(self)-> None:
        """TODO: 添加文档字符串"""
        # 医学实体词典
        self.medical_entities = {
            "症状": [
                "头痛", "头晕", "发热", "咳嗽", "胸痛", "腹痛", "恶心", "呕吐",
                "腹泻", "便秘", "失眠", "乏力", "心悸", "气短", "水肿", "皮疹"
            ],
            "身体部位": [
                "头部", "颈部", "胸部", "腹部", "背部", "四肢", "手", "脚",
                "眼睛", "耳朵", "鼻子", "嘴巴", "喉咙", "心脏", "肺", "胃", "肝", "肾"
            ],
            "时间": [
                "今天", "昨天", "前天", "一周", "一个月", "半年", "一年",
                "早上", "中午", "下午", "晚上", "夜里", "刚才", "最近", "长期"
            ],
            "程度": [
                "轻微", "稍微", "一点", "有点", "中等", "严重", "厉害", "剧烈",
                "很", "非常", "特别", "极其", "难以忍受"
            ],
            "频率": [
                "偶尔", "有时", "经常", "总是", "一直", "持续", "间歇性",
                "每天", "每周", "每月", "反复", "发作性"
            ]
        }

        # 正则表达式模式
        self.patterns = {
            "数量": r'\d + (?:\.\d + )?(?:次|个|天|小时|分钟|年|月|周)',
            "温度": r'\d + (?:\.\d + )?(?:度|℃)',
            "血压": r'\d + /\d + (?:mmHg)?',
            "药物": r'(?:服用|吃|用)\s * ([^，。！？\s] + (?:片|粒|毫克|克|ml))',
        }

    async def extract_entities(self, text: str)-> List[SemanticEntity]:
        """提取语义实体"""
        entities = []

        # 基于词典的实体提取
        for entity_type, keywords in self.medical_entities.items():
            for keyword in keywords:
                start = 0
                while True:
                    pos = text.find(keyword, start)
                    if pos == - 1:
                        break

                    entity = SemanticEntity(
                        text = keyword,
                        entity_type = entity_type,
                        start_pos = pos,
                        end_pos = pos + len(keyword),
                        confidence = 0.9
                    )
                    entities.append(entity)
                    start = pos + 1

        # 基于正则表达式的实体提取
        for entity_type, pattern in self.patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                entity = SemanticEntity(
                    text = match.group(),
                    entity_type = entity_type,
                    start_pos = match.start(),
                    end_pos = match.end(),
                    confidence = 0.8
                )
                entities.append(entity)

        # 去重和排序
        entities = self._deduplicate_entities(entities)
        entities.sort(key = lambda x: x.start_pos)

        return entities

    def _deduplicate_entities(self, entities: List[SemanticEntity])-> List[SemanticEntity]:
        """去重实体"""
        unique_entities = []
        seen_spans = set()

        for entity in entities:
            span = (entity.start_pos, entity.end_pos)
            if span not in seen_spans:
                unique_entities.append(entity)
                seen_spans.add(span)

        return unique_entities

class IntelligentIntentClassifier:
    """智能意图分类器"""

    def __init__(self)-> None:
        """TODO: 添加文档字符串"""
        # 意图关键词映射
        self.intent_keywords = {
            IntentType.SYMPTOM_DESCRIPTION: [
                "感觉", "症状", "不舒服", "疼", "痛", "难受", "异常", "问题"
            ],
            IntentType.PAIN_INQUIRY: [
                "疼", "痛", "酸", "胀", "刺", "麻", "痒", "烧灼感"
            ],
            IntentType.DURATION_INQUIRY: [
                "多久", "多长时间", "什么时候开始", "持续", "已经", "天", "周", "月", "年"
            ],
            IntentType.SEVERITY_INQUIRY: [
                "严重", "厉害", "程度", "轻重", "影响", "忍受", "剧烈"
            ],
            IntentType.MEDICAL_HISTORY: [
                "以前", "之前", "历史", "病史", "曾经", "过去", "家族", "遗传"
            ],
            IntentType.MEDICATION_INQUIRY: [
                "药", "服用", "吃", "治疗", "用药", "药物", "处方", "中药", "西药"
            ],
            IntentType.LIFESTYLE_INQUIRY: [
                "生活", "饮食", "睡眠", "运动", "工作", "压力", "习惯", "作息"
            ],
            IntentType.EMOTIONAL_STATE: [
                "心情", "情绪", "焦虑", "紧张", "担心", "害怕", "抑郁", "烦躁"
            ],
            IntentType.CONFIRMATION: [
                "是", "对", "是的", "没错", "确实", "正确", "同意"
            ],
            IntentType.DENIAL: [
                "不是", "没有", "不对", "错", "不", "否", "不同意"
            ],
            IntentType.UNCLEAR: [
                "不知道", "不清楚", "不确定", "说不准", "可能", "也许", "不太清楚"
            ]
        }

        # 意图权重
        self.intent_weights = {
            IntentType.SYMPTOM_DESCRIPTION: 1.0,
            IntentType.PAIN_INQUIRY: 1.2,
            IntentType.DURATION_INQUIRY: 1.1,
            IntentType.SEVERITY_INQUIRY: 1.1,
            IntentType.MEDICAL_HISTORY: 0.9,
            IntentType.MEDICATION_INQUIRY: 0.9,
            IntentType.LIFESTYLE_INQUIRY: 0.8,
            IntentType.EMOTIONAL_STATE: 0.8,
            IntentType.CONFIRMATION: 1.5,
            IntentType.DENIAL: 1.5,
            IntentType.UNCLEAR: 1.3
        }

    async def classify_intent(self, text: str, context: Dict[str, Any] = None)-> IntentAnalysisResult:
        """分类用户意图"""
        # 文本预处理
        processed_text = self._preprocess_text(text)

        # 计算各意图得分
        intent_scores = {}
        for intent, keywords in self.intent_keywords.items():
            score = self._calculate_intent_score(processed_text, keywords)
            intent_scores[intent] = score * self.intent_weights[intent]

        # 选择最高得分的意图
        best_intent = max(intent_scores, key = intent_scores.get)
        confidence = intent_scores[best_intent]

        # 提取关键词
        keywords = self._extract_keywords(processed_text, best_intent)

        # 上下文调整
        if context:
            best_intent, confidence = self._adjust_with_context(
                best_intent, confidence, context
            )

        return IntentAnalysisResult(
            intent = best_intent,
            confidence = min(confidence, 1.0),
            entities = [],  # 将在后续步骤中填充
            keywords = keywords,
            context_info = context or {}
        )

    def _preprocess_text(self, text: str)-> str:
        """预处理文本"""
        # 转换为小写
        text = text.lower()
        # 去除标点符号
        text = re.sub(r'[^\w\s]', '', text)
        return text

    def _calculate_intent_score(self, text: str, keywords: List[str])-> float:
        """计算意图得分"""
        score = 0.0
        text_words = set(jieba.cut(text))

        for keyword in keywords:
            if keyword in text:
                score + = 1.0
            # 模糊匹配
            for word in text_words:
                if keyword in word or word in keyword:
                    score + = 0.5

        # 归一化
        return score / len(keywords) if keywords else 0.0

    def _extract_keywords(self, text: str, intent: IntentType)-> List[str]:
        """提取关键词"""
        keywords = []
        intent_keywords = self.intent_keywords.get(intent, [])

        for keyword in intent_keywords:
            if keyword in text:
                keywords.append(keyword)

        return keywords

    def _adjust_with_context(self, intent: IntentType, confidence: float,
                        context: Dict[str, Any])-> Tuple[IntentType, float]:
        """根据上下文调整意图"""
        # 根据对话历史调整
        if "last_question_type" in context:
            last_type = context["last_question_type"]

            # 如果上一个问题是询问症状，当前回答可能是症状描述
            if last_type == "symptom_inquiry" and intent == IntentType.UNCLEAR:
                return IntentType.SYMPTOM_DESCRIPTION, confidence * 1.2

            # 如果上一个问题是确认性问题，当前回答可能是确认或否认
            if last_type == "confirmation" and confidence < 0.5:
                if any(word in context.get("text", "") for word in ["是", "对", "没错"]):
                    return IntentType.CONFIRMATION, 0.8
                elif any(word in context.get("text", "") for word in ["不", "没有", "不是"]):
                    return IntentType.DENIAL, 0.8

        return intent, confidence

class AdvancedEmotionAnalyzer:
    """高级情感分析器"""

    def __init__(self)-> None:
        """TODO: 添加文档字符串"""
        # 情感词典
        self.emotion_lexicon = {
            EmotionType.ANXIOUS: [
                "担心", "焦虑", "紧张", "不安", "忧虑", "恐慌", "害怕", "惊恐"
            ],
            EmotionType.WORRIED: [
                "担心", "忧虑", "担忧", "顾虑", "不放心", "挂念"
            ],
            EmotionType.CALM: [
                "平静", "冷静", "镇定", "安静", "放松", "淡定"
            ],
            EmotionType.FRUSTRATED: [
                "沮丧", "失望", "泄气", "灰心", "绝望", "无助", "郁闷"
            ],
            EmotionType.HOPEFUL: [
                "希望", "期待", "乐观", "积极", "信心", "盼望"
            ],
            EmotionType.CONFUSED: [
                "困惑", "迷惑", "不解", "疑惑", "不明白", "糊涂"
            ],
            EmotionType.ANGRY: [
                "愤怒", "生气", "恼火", "气愤", "暴躁", "烦躁", "恼怒"
            ],
            EmotionType.NEUTRAL: [
                "一般", "普通", "正常", "还好", "没什么", "平常"
            ]
        }

        # 情感强度词
        self.intensity_words = {
            "非常": 2.0, "特别": 2.0, "极其": 2.5, "十分": 1.8,
            "很": 1.5, "比较": 1.2, "有点": 0.8, "稍微": 0.6,
            "一点": 0.5, "略微": 0.4
        }

    async def analyze_emotion(self, text: str)-> EmotionAnalysisResult:
        """分析文本情感"""
        # 计算各情绪得分
        emotion_scores = {}
        for emotion, words in self.emotion_lexicon.items():
            score = self._calculate_emotion_score(text, words)
            emotion_scores[emotion] = score

        # 确定主要情绪
        primary_emotion = max(emotion_scores, key = emotion_scores.get)

        # 计算情绪强度
        emotional_intensity = self._calculate_intensity(text)

        # 计算情感极性
        sentiment_polarity = self._calculate_sentiment_polarity(emotion_scores)

        # 计算置信度
        confidence = self._calculate_emotion_confidence(emotion_scores)

        return EmotionAnalysisResult(
            primary_emotion = primary_emotion,
            emotion_scores = emotion_scores,
            emotional_intensity = emotional_intensity,
            sentiment_polarity = sentiment_polarity,
            confidence = confidence
        )

    def _calculate_emotion_score(self, text: str, emotion_words: List[str])-> float:
        """计算情绪得分"""
        score = 0.0
        for word in emotion_words:
            if word in text:
                score + = 1.0
                # 考虑强度词
                for intensity_word, multiplier in self.intensity_words.items():
                    if intensity_word in text and abs(text.find(intensity_word) - text.find(word)) < 10:
                        score * = multiplier
                        break

        return score

    def _calculate_intensity(self, text: str)-> float:
        """计算情绪强度"""
        base_intensity = 0.5

        for intensity_word, multiplier in self.intensity_words.items():
            if intensity_word in text:
                base_intensity * = multiplier

        # 标点符号影响
        if "！" in text or "!!!" in text:
            base_intensity * = 1.3
        if "？？" in text:
            base_intensity * = 1.2

        return min(base_intensity, 3.0)

    def _calculate_sentiment_polarity(self, emotion_scores: Dict[EmotionType, float])-> float:
        """计算情感极性"""
        positive_emotions = [EmotionType.HOPEFUL, EmotionType.CALM]
        negative_emotions = [EmotionType.ANXIOUS, EmotionType.WORRIED,
                        EmotionType.FRUSTRATED, EmotionType.ANGRY]

        positive_score = sum(emotion_scores.get(emotion, 0) for emotion in positive_emotions)
        negative_score = sum(emotion_scores.get(emotion, 0) for emotion in negative_emotions)

        total_score = positive_score + negative_score
        if total_score == 0:
            return 0.0

        return (positive_score - negative_score) / total_score

    def _calculate_emotion_confidence(self, emotion_scores: Dict[EmotionType, float])-> float:
        """计算情感分析置信度"""
        scores = list(emotion_scores.values())
        if not scores:
            return 0.0

        max_score = max(scores)
        if max_score == 0:
            return 0.0

        # 计算得分分布的集中度
        normalized_scores = [score / max_score for score in scores]
        variance = np.var(normalized_scores)

        # 方差越大，置信度越高（说明有明显的主导情绪）
        confidence = min(variance * 2, 1.0)

        return confidence

class IntelligentSymptomExtractor:
    """智能症状提取器"""

    def __init__(self)-> None:
        """TODO: 添加文档字符串"""
        # 症状模式库
        self.symptom_patterns = {
            "疼痛": {
                "keywords": ["疼", "痛", "酸痛", "胀痛", "刺痛", "隐痛", "绞痛"],
                "body_parts": ["头", "胸", "腹", "背", "腰", "腿", "手", "脚"],
                "descriptors": ["钝", "尖锐", "持续", "间歇", "剧烈", "轻微"]
            },
            "消化": {
                "keywords": ["恶心", "呕吐", "腹泻", "便秘", "胃痛", "腹胀"],
                "body_parts": ["胃", "肠", "腹部", "肚子"],
                "descriptors": ["频繁", "偶尔", "严重", "轻微", "持续"]
            },
            "呼吸": {
                "keywords": ["咳嗽", "气短", "呼吸困难", "胸闷", "喘气"],
                "body_parts": ["胸", "肺", "喉咙", "气管"],
                "descriptors": ["干咳", "有痰", "夜间", "运动后", "持续"]
            },
            "神经": {
                "keywords": ["头晕", "头痛", "失眠", "健忘", "注意力不集中"],
                "body_parts": ["头", "大脑", "神经"],
                "descriptors": ["偏", "胀", "昏沉", "清晰", "模糊"]
            }
        }

        # 时间表达式
        self.temporal_patterns = {
            "duration": r'(?:持续|已经|大约|约|差不多)?\s * (\d + )\s * (?:天|周|月|年|小时|分钟)',
            "frequency": r'(?:每|一)\s * (?:天|周|月|年)\s * (\d + )\s * (?:次|回)',
            "onset": r'(?:从|自从|开始于)\s * ([^，。！？] + ?)(?:开始|起)',
            "timing": r'(?:在|于|当)\s * ([^，。！？] + ?)(?:时|的时候)'
        }

    async def extract_symptoms(self, text: str)-> SymptomExtractionResult:
        """提取症状信息"""
        symptoms = []
        body_parts = []
        temporal_info = {}
        severity_indicators = []

        # 提取症状
        for category, pattern_info in self.symptom_patterns.items():
            category_symptoms = self._extract_category_symptoms(text, category, pattern_info)
            symptoms.extend(category_symptoms)

        # 提取身体部位
        body_parts = self._extract_body_parts(text)

        # 提取时间信息
        temporal_info = self._extract_temporal_info(text)

        # 提取严重程度指标
        severity_indicators = self._extract_severity_indicators(text)

        # 计算置信度
        confidence = self._calculate_extraction_confidence(symptoms, body_parts, temporal_info)

        return SymptomExtractionResult(
            symptoms = symptoms,
            body_parts = body_parts,
            temporal_info = temporal_info,
            severity_indicators = severity_indicators,
            confidence = confidence
        )

    def _extract_category_symptoms(self, text: str, category: str,
                                pattern_info: Dict[str, List[str]])-> List[Dict[str, Any]]:
        """提取特定类别的症状"""
        symptoms = []
        keywords = pattern_info["keywords"]

        for keyword in keywords:
            if keyword in text:
                # 提取症状上下文
                context = self._extract_symptom_context(text, keyword)

                symptom = {
                    "name": keyword,
                    "category": category,
                    "context": context,
                    "confidence": 0.8
                }

                # 分析描述词
                descriptors = self._find_descriptors(text, keyword, pattern_info["descriptors"])
                if descriptors:
                    symptom["descriptors"] = descriptors

                symptoms.append(symptom)

        return symptoms

    def _extract_symptom_context(self, text: str, keyword: str)-> str:
        """提取症状上下文"""
        pos = text.find(keyword)
        if pos == - 1:
            return ""

        start = max(0, pos - 20)
        end = min(len(text), pos + len(keyword) + 20)

        return text[start:end]

    def _find_descriptors(self, text: str, keyword: str, descriptors: List[str])-> List[str]:
        """查找描述词"""
        found_descriptors = []
        keyword_pos = text.find(keyword)

        for descriptor in descriptors:
            if descriptor in text:
                descriptor_pos = text.find(descriptor)
                # 检查描述词是否在症状附近
                if abs(descriptor_pos - keyword_pos) < 30:
                    found_descriptors.append(descriptor)

        return found_descriptors

    def _extract_body_parts(self, text: str)-> List[str]:
        """提取身体部位"""
        body_parts = []
        all_body_parts = set()

        for pattern_info in self.symptom_patterns.values():
            all_body_parts.update(pattern_info["body_parts"])

        for part in all_body_parts:
            if part in text:
                body_parts.append(part)

        return body_parts

    def _extract_temporal_info(self, text: str)-> Dict[str, str]:
        """提取时间信息"""
        temporal_info = {}

        for info_type, pattern in self.temporal_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                temporal_info[info_type] = matches[0] if isinstance(matches[0], str) else str(matches[0])

        return temporal_info

    def _extract_severity_indicators(self, text: str)-> List[str]:
        """提取严重程度指标"""
        severity_words = [
            "轻微", "稍微", "一点", "有点", "中等", "严重", "厉害", "剧烈",
            "很", "非常", "特别", "极其", "难以忍受", "无法忍受"
        ]

        found_indicators = []
        for word in severity_words:
            if word in text:
                found_indicators.append(word)

        return found_indicators

    def _calculate_extraction_confidence(self, symptoms: List[Dict[str, Any]],
                                    body_parts: List[str],
                                    temporal_info: Dict[str, str])-> float:
        """计算提取置信度"""
        base_confidence = 0.5

        # 症状数量影响
        if symptoms:
            base_confidence + = min(len(symptoms) * 0.1, 0.3)

        # 身体部位影响
        if body_parts:
            base_confidence + = min(len(body_parts) * 0.05, 0.1)

        # 时间信息影响
        if temporal_info:
            base_confidence + = min(len(temporal_info) * 0.05, 0.1)

        return min(base_confidence, 1.0)

class DialogueUnderstandingEngine:
    """对话理解引擎"""

    def __init__(self)-> None:
        """TODO: 添加文档字符串"""
        self.entity_extractor = AdvancedEntityExtractor()
        self.intent_classifier = IntelligentIntentClassifier()
        self.emotion_analyzer = AdvancedEmotionAnalyzer()
        self.symptom_extractor = IntelligentSymptomExtractor()

        # 响应模板
        self.response_templates = {
            IntentType.SYMPTOM_DESCRIPTION: [
                "我了解您的症状了。能详细描述一下{symptom}的具体情况吗？",
                "关于您提到的{symptom}，请问是什么时候开始的？",
                "您的{symptom}症状，严重程度如何？"
            ],
            IntentType.PAIN_INQUIRY: [
                "关于疼痛，请问是哪种类型的疼痛？是刺痛、胀痛还是其他？",
                "疼痛的程度如何？会影响您的日常生活吗？",
                "疼痛是持续性的还是间歇性的？"
            ],
            IntentType.UNCLEAR: [
                "我理解您可能不太确定。让我换个方式问您...",
                "没关系，我们可以一步步来了解情况。",
                "请您尽量描述一下您的感受，哪怕是模糊的感觉也可以。"
            ]
        }

        # 问题生成模板
        self.question_templates = {
            "symptom_detail": "能详细描述一下{symptom}的具体表现吗？",
            "duration": "这个症状持续多长时间了？",
            "severity": "症状的严重程度如何？会影响您的日常生活吗？",
            "triggers": "有什么特定的情况会加重这个症状吗？",
            "relief": "有什么方法能缓解这个症状吗？",
            "associated": "除了{symptom}，还有其他不舒服的地方吗？"
        }

    async def understand_dialogue(self, text: str, context: Dict[str, Any] = None)-> DialogueUnderstandingResult:
        """理解对话内容"""
        # 并行执行各种分析
        tasks = [
            self.intent_classifier.classify_intent(text, context),
            self.emotion_analyzer.analyze_emotion(text),
            self.symptom_extractor.extract_symptoms(text),
            self.entity_extractor.extract_entities(text)
        ]

        intent_result, emotion_result, symptom_result, entities = await asyncio.gather( * tasks)

        # 将实体添加到意图分析结果中
        intent_result.entities = entities

        # 生成响应建议
        response_suggestions = await self._generate_response_suggestions(
            intent_result, emotion_result, symptom_result
        )

        # 生成下一步问题
        next_questions = await self._generate_next_questions(
            intent_result, symptom_result, context
        )

        # 计算整体置信度
        overall_confidence = self._calculate_overall_confidence(
            intent_result, emotion_result, symptom_result
        )

        return DialogueUnderstandingResult(
            intent_analysis = intent_result,
            emotion_analysis = emotion_result,
            symptom_extraction = symptom_result,
            response_suggestions = response_suggestions,
            next_questions = next_questions,
            overall_confidence = overall_confidence
        )

    async def _generate_response_suggestions(self, intent_result: IntentAnalysisResult,
                                        emotion_result: EmotionAnalysisResult,
                                        symptom_result: SymptomExtractionResult)-> List[str]:
        """生成响应建议"""
        suggestions = []

        # 基于意图生成响应
        templates = self.response_templates.get(intent_result.intent, [])
        if templates and symptom_result.symptoms:
            main_symptom = symptom_result.symptoms[0]["name"]
            for template in templates[:2]:  # 最多取2个模板
                suggestion = template.format(symptom = main_symptom)
                suggestions.append(suggestion)

        # 基于情绪调整响应语调
        if emotion_result.primary_emotion in [EmotionType.ANXIOUS, EmotionType.WORRIED]:
            suggestions.insert(0, "我理解您的担心，让我们一起来了解情况。")
        elif emotion_result.primary_emotion == EmotionType.FRUSTRATED:
            suggestions.insert(0, "我知道这很困扰您，我会尽力帮助您找到解决方案。")

        return suggestions[:3]  # 最多返回3个建议

    async def _generate_next_questions(self, intent_result: IntentAnalysisResult,
                                    symptom_result: SymptomExtractionResult,
                                    context: Dict[str, Any] = None)-> List[str]:
        """生成下一步问题"""
        questions = []

        if symptom_result.symptoms:
            main_symptom = symptom_result.symptoms[0]["name"]

            # 根据缺失信息生成问题
            if not symptom_result.temporal_info.get("duration"):
                questions.append(self.question_templates["duration"])

            if not symptom_result.severity_indicators:
                questions.append(self.question_templates["severity"])

            if len(symptom_result.symptoms) == 1:
                question = self.question_templates["associated"].format(symptom = main_symptom)
                questions.append(question)

        # 基于意图生成特定问题
        if intent_result.intent == IntentType.PAIN_INQUIRY:
            questions.append("疼痛是在什么情况下出现的？")
            questions.append("疼痛会向其他部位放射吗？")

        return questions[:3]  # 最多返回3个问题

    def _calculate_overall_confidence(self, intent_result: IntentAnalysisResult,
                                    emotion_result: EmotionAnalysisResult,
                                    symptom_result: SymptomExtractionResult)-> float:
        """计算整体置信度"""
        confidences = [
            intent_result.confidence,
            emotion_result.confidence,
            symptom_result.confidence
        ]

        # 加权平均
        weights = [0.4, 0.2, 0.4]  # 意图和症状提取权重更高
        weighted_confidence = sum(c * w for c, w in zip(confidences, weights))

        return weighted_confidence

# 导出主要类
__all__ = [
    'DialogueUnderstandingEngine',
    'AdvancedEntityExtractor',
    'IntelligentIntentClassifier',
    'AdvancedEmotionAnalyzer',
    'IntelligentSymptomExtractor',
    'DialogueUnderstandingResult',
    'IntentAnalysisResult',
    'EmotionAnalysisResult',
    'SymptomExtractionResult'
]