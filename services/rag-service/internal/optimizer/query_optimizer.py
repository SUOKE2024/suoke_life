#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能查询优化器
支持查询重写、扩展、中医特色优化和多策略优化
"""

import asyncio
import re
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import jieba
import jieba.posseg as pseg
from loguru import logger

from ..observability.metrics import MetricsCollector
from ..tcm.tcm_models import ConstitutionType, SyndromeType


class OptimizationStrategy(str, Enum):
    """优化策略"""
    QUERY_EXPANSION = "query_expansion"          # 查询扩展
    QUERY_REWRITING = "query_rewriting"         # 查询重写
    SYNONYM_REPLACEMENT = "synonym_replacement"  # 同义词替换
    TCM_ENHANCEMENT = "tcm_enhancement"          # 中医增强
    SEMANTIC_ENRICHMENT = "semantic_enrichment"  # 语义丰富
    CONTEXT_INJECTION = "context_injection"     # 上下文注入


class QueryType(str, Enum):
    """查询类型"""
    SYMPTOM_INQUIRY = "symptom_inquiry"          # 症状咨询
    CONSTITUTION_ANALYSIS = "constitution_analysis"  # 体质分析
    FORMULA_INQUIRY = "formula_inquiry"          # 方剂咨询
    HERB_INQUIRY = "herb_inquiry"                # 中药咨询
    SYNDROME_DIAGNOSIS = "syndrome_diagnosis"    # 辨证诊断
    HEALTH_GUIDANCE = "health_guidance"          # 健康指导
    GENERAL_TCM = "general_tcm"                  # 一般中医
    LIFESTYLE_ADVICE = "lifestyle_advice"        # 生活建议


@dataclass
class QueryAnalysis:
    """查询分析结果"""
    original_query: str
    query_type: QueryType
    intent: str
    entities: List[Dict[str, Any]] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    tcm_terms: List[str] = field(default_factory=list)
    symptoms: List[str] = field(default_factory=list)
    constitution_hints: List[ConstitutionType] = field(default_factory=list)
    syndrome_hints: List[SyndromeType] = field(default_factory=list)
    confidence: float = 0.0
    complexity_score: float = 0.0


@dataclass
class OptimizedQuery:
    """优化后的查询"""
    original_query: str
    optimized_query: str
    expansion_terms: List[str] = field(default_factory=list)
    rewritten_parts: Dict[str, str] = field(default_factory=dict)
    added_context: List[str] = field(default_factory=list)
    optimization_strategies: List[OptimizationStrategy] = field(default_factory=list)
    confidence_boost: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class TCMTermDictionary:
    """中医术语词典"""
    
    def __init__(self):
        self.symptom_synonyms = self._load_symptom_synonyms()
        self.constitution_terms = self._load_constitution_terms()
        self.syndrome_terms = self._load_syndrome_terms()
        self.herb_synonyms = self._load_herb_synonyms()
        self.formula_synonyms = self._load_formula_synonyms()
        self.tcm_keywords = self._load_tcm_keywords()
    
    def _load_symptom_synonyms(self) -> Dict[str, List[str]]:
        """加载症状同义词"""
        return {
            "头痛": ["头疼", "脑袋疼", "头部疼痛", "偏头痛"],
            "失眠": ["睡不着", "入睡困难", "睡眠不好", "多梦"],
            "疲劳": ["乏力", "无力", "疲倦", "精神不振", "没精神"],
            "腹痛": ["肚子疼", "腹部疼痛", "胃痛", "肚痛"],
            "便秘": ["大便干燥", "排便困难", "便干", "大便不通"],
            "腹泻": ["拉肚子", "大便稀", "泄泻", "便溏"],
            "咳嗽": ["咳", "干咳", "咳痰"],
            "发热": ["发烧", "体温升高", "热"],
            "出汗": ["汗出", "多汗", "盗汗", "自汗"],
            "心悸": ["心慌", "心跳快", "心律不齐"]
        }
    
    def _load_constitution_terms(self) -> Dict[ConstitutionType, List[str]]:
        """加载体质相关术语"""
        return {
            ConstitutionType.QI_DEFICIENCY: [
                "气虚", "气不足", "气短", "乏力", "疲倦", "声音低微",
                "容易感冒", "自汗", "脉弱"
            ],
            ConstitutionType.YIN_DEFICIENCY: [
                "阴虚", "潮热", "盗汗", "五心烦热", "口干", "咽干",
                "大便干燥", "小便黄", "舌红少苔", "脉细数"
            ],
            ConstitutionType.YANG_DEFICIENCY: [
                "阳虚", "畏寒", "手足冰冷", "腰膝酸冷", "夜尿多",
                "大便溏薄", "舌淡胖", "脉沉迟"
            ],
            ConstitutionType.PHLEGM_DAMPNESS: [
                "痰湿", "身重", "困倦", "胸闷", "痰多", "大便粘腻",
                "舌苔厚腻", "脉滑"
            ],
            ConstitutionType.DAMP_HEAT: [
                "湿热", "身热不扬", "头身困重", "口苦", "小便黄赤",
                "大便粘腻", "舌苔黄腻", "脉滑数"
            ]
        }
    
    def _load_syndrome_terms(self) -> Dict[SyndromeType, List[str]]:
        """加载证型相关术语"""
        return {
            SyndromeType.SPLEEN_QI_DEFICIENCY: [
                "脾气虚", "食欲不振", "腹胀", "便溏", "面色萎黄",
                "四肢无力", "舌淡苔白", "脉缓弱"
            ],
            SyndromeType.KIDNEY_YIN_DEFICIENCY: [
                "肾阴虚", "腰膝酸软", "头晕耳鸣", "失眠多梦",
                "潮热盗汗", "口干咽燥", "舌红少苔", "脉细数"
            ],
            SyndromeType.KIDNEY_YANG_DEFICIENCY: [
                "肾阳虚", "腰膝酸冷", "畏寒肢冷", "阳痿早泄",
                "夜尿频多", "大便溏薄", "舌淡胖", "脉沉迟"
            ],
            SyndromeType.LIVER_QI_STAGNATION: [
                "肝气郁结", "情志不舒", "胸胁胀痛", "善太息",
                "月经不调", "乳房胀痛", "舌苔薄白", "脉弦"
            ]
        }
    
    def _load_herb_synonyms(self) -> Dict[str, List[str]]:
        """加载中药同义词"""
        return {
            "人参": ["红参", "白参", "野山参", "园参"],
            "黄芪": ["北芪", "绵芪", "箭芪"],
            "当归": ["秦归", "岷归", "西当归"],
            "熟地黄": ["熟地", "熟地黄"],
            "白术": ["于术", "冬术"],
            "茯苓": ["白茯苓", "茯神"],
            "甘草": ["炙甘草", "生甘草"],
            "川芎": ["芎藭", "香果"]
        }
    
    def _load_formula_synonyms(self) -> Dict[str, List[str]]:
        """加载方剂同义词"""
        return {
            "四君子汤": ["四君子", "四君汤"],
            "六味地黄丸": ["六味地黄", "六味丸"],
            "逍遥散": ["逍遥丸", "加味逍遥散"],
            "补中益气汤": ["补中益气", "补中汤"],
            "八珍汤": ["八珍散"],
            "十全大补汤": ["十全大补", "十全汤"]
        }
    
    def _load_tcm_keywords(self) -> Set[str]:
        """加载中医关键词"""
        keywords = set()
        
        # 添加所有同义词
        for synonyms in self.symptom_synonyms.values():
            keywords.update(synonyms)
        
        for terms in self.constitution_terms.values():
            keywords.update(terms)
        
        for terms in self.syndrome_terms.values():
            keywords.update(terms)
        
        for synonyms in self.herb_synonyms.values():
            keywords.update(synonyms)
        
        for synonyms in self.formula_synonyms.values():
            keywords.update(synonyms)
        
        # 添加基础中医术语
        basic_terms = [
            "中医", "中药", "方剂", "汤药", "丸剂", "散剂",
            "辨证", "论治", "望闻问切", "四诊", "八纲",
            "阴阳", "五行", "气血", "津液", "脏腑",
            "经络", "穴位", "针灸", "推拿", "按摩",
            "养生", "保健", "调理", "治疗", "预防"
        ]
        keywords.update(basic_terms)
        
        return keywords


class QueryAnalyzer:
    """查询分析器"""
    
    def __init__(self, tcm_dictionary: TCMTermDictionary):
        self.tcm_dict = tcm_dictionary
        
        # 初始化jieba分词
        jieba.initialize()
        
        # 添加中医词汇到jieba词典
        for keyword in self.tcm_dict.tcm_keywords:
            jieba.add_word(keyword)
    
    async def analyze_query(self, query: str) -> QueryAnalysis:
        """分析查询"""
        try:
            # 基础分词和词性标注
            words = list(jieba.cut(query))
            pos_tags = list(pseg.cut(query))
            
            # 提取关键词
            keywords = self._extract_keywords(words, pos_tags)
            
            # 识别中医术语
            tcm_terms = self._identify_tcm_terms(words)
            
            # 提取症状
            symptoms = self._extract_symptoms(words)
            
            # 识别查询类型
            query_type = self._classify_query_type(query, keywords, tcm_terms)
            
            # 识别意图
            intent = self._identify_intent(query, query_type)
            
            # 提取实体
            entities = self._extract_entities(words, pos_tags)
            
            # 体质提示
            constitution_hints = self._identify_constitution_hints(words)
            
            # 证型提示
            syndrome_hints = self._identify_syndrome_hints(words)
            
            # 计算置信度
            confidence = self._calculate_confidence(query, keywords, tcm_terms)
            
            # 计算复杂度
            complexity_score = self._calculate_complexity(query, words, entities)
            
            return QueryAnalysis(
                original_query=query,
                query_type=query_type,
                intent=intent,
                entities=entities,
                keywords=keywords,
                tcm_terms=tcm_terms,
                symptoms=symptoms,
                constitution_hints=constitution_hints,
                syndrome_hints=syndrome_hints,
                confidence=confidence,
                complexity_score=complexity_score
            )
            
        except Exception as e:
            logger.error(f"查询分析失败: {e}")
            return QueryAnalysis(
                original_query=query,
                query_type=QueryType.GENERAL_TCM,
                intent="unknown"
            )
    
    def _extract_keywords(self, words: List[str], pos_tags: List[Tuple[str, str]]) -> List[str]:
        """提取关键词"""
        keywords = []
        
        # 基于词性提取关键词
        for word, pos in pos_tags:
            if len(word) > 1 and pos in ['n', 'v', 'a', 'nr', 'ns', 'nt']:
                keywords.append(word)
        
        # 过滤停用词
        stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
        keywords = [kw for kw in keywords if kw not in stop_words]
        
        return keywords
    
    def _identify_tcm_terms(self, words: List[str]) -> List[str]:
        """识别中医术语"""
        tcm_terms = []
        
        for word in words:
            if word in self.tcm_dict.tcm_keywords:
                tcm_terms.append(word)
        
        return tcm_terms
    
    def _extract_symptoms(self, words: List[str]) -> List[str]:
        """提取症状"""
        symptoms = []
        
        for word in words:
            # 检查是否是症状或其同义词
            for symptom, synonyms in self.tcm_dict.symptom_synonyms.items():
                if word == symptom or word in synonyms:
                    symptoms.append(symptom)
                    break
        
        return list(set(symptoms))  # 去重
    
    def _classify_query_type(self, query: str, keywords: List[str], tcm_terms: List[str]) -> QueryType:
        """分类查询类型"""
        query_lower = query.lower()
        
        # 症状咨询
        if any(word in query for word in ['症状', '表现', '怎么办', '疼', '痛', '不舒服']):
            return QueryType.SYMPTOM_INQUIRY
        
        # 体质分析
        if any(word in query for word in ['体质', '是什么体质', '体质类型']):
            return QueryType.CONSTITUTION_ANALYSIS
        
        # 方剂咨询
        if any(word in query for word in ['方剂', '汤', '丸', '散', '方子']):
            return QueryType.FORMULA_INQUIRY
        
        # 中药咨询
        if any(word in query for word in ['中药', '药材', '草药']):
            return QueryType.HERB_INQUIRY
        
        # 辨证诊断
        if any(word in query for word in ['辨证', '证型', '诊断']):
            return QueryType.SYNDROME_DIAGNOSIS
        
        # 健康指导
        if any(word in query for word in ['调理', '养生', '保健', '预防']):
            return QueryType.HEALTH_GUIDANCE
        
        # 生活建议
        if any(word in query for word in ['饮食', '运动', '生活', '作息']):
            return QueryType.LIFESTYLE_ADVICE
        
        return QueryType.GENERAL_TCM
    
    def _identify_intent(self, query: str, query_type: QueryType) -> str:
        """识别查询意图"""
        if '是什么' in query or '什么是' in query:
            return 'definition'
        elif '怎么' in query or '如何' in query:
            return 'how_to'
        elif '为什么' in query:
            return 'explanation'
        elif '能不能' in query or '可以' in query:
            return 'possibility'
        elif '推荐' in query or '建议' in query:
            return 'recommendation'
        elif '治疗' in query or '调理' in query:
            return 'treatment'
        else:
            return 'information'
    
    def _extract_entities(self, words: List[str], pos_tags: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
        """提取实体"""
        entities = []
        
        for word, pos in pos_tags:
            entity_type = None
            
            if pos == 'nr':  # 人名
                entity_type = 'person'
            elif pos == 'ns':  # 地名
                entity_type = 'location'
            elif pos == 'nt':  # 机构名
                entity_type = 'organization'
            elif word in self.tcm_dict.tcm_keywords:
                entity_type = 'tcm_term'
            
            if entity_type:
                entities.append({
                    'text': word,
                    'type': entity_type,
                    'confidence': 0.8
                })
        
        return entities
    
    def _identify_constitution_hints(self, words: List[str]) -> List[ConstitutionType]:
        """识别体质提示"""
        hints = []
        
        for constitution, terms in self.tcm_dict.constitution_terms.items():
            if any(term in words for term in terms):
                hints.append(constitution)
        
        return hints
    
    def _identify_syndrome_hints(self, words: List[str]) -> List[SyndromeType]:
        """识别证型提示"""
        hints = []
        
        for syndrome, terms in self.tcm_dict.syndrome_terms.items():
            if any(term in words for term in terms):
                hints.append(syndrome)
        
        return hints
    
    def _calculate_confidence(self, query: str, keywords: List[str], tcm_terms: List[str]) -> float:
        """计算分析置信度"""
        score = 0.0
        
        # 基础分数
        score += 0.3
        
        # 关键词数量
        if keywords:
            score += min(len(keywords) * 0.1, 0.3)
        
        # 中医术语数量
        if tcm_terms:
            score += min(len(tcm_terms) * 0.15, 0.4)
        
        # 查询长度
        if len(query) > 5:
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_complexity(self, query: str, words: List[str], entities: List[Dict[str, Any]]) -> float:
        """计算查询复杂度"""
        score = 0.0
        
        # 字符长度
        score += min(len(query) / 100, 0.3)
        
        # 词汇数量
        score += min(len(words) / 20, 0.3)
        
        # 实体数量
        score += min(len(entities) / 10, 0.2)
        
        # 复杂句式
        if any(word in query for word in ['如果', '但是', '然而', '因为', '所以']):
            score += 0.2
        
        return min(score, 1.0)


class QueryOptimizer:
    """查询优化器"""
    
    def __init__(self, metrics_collector: MetricsCollector, embedding_service=None):
        self.metrics_collector = metrics_collector
        self.embedding_service = embedding_service
        self.tcm_dict = TCMTermDictionary()
        self.analyzer = QueryAnalyzer(self.tcm_dict)
        
        # 优化策略映射
        self.optimization_strategies = {
            OptimizationStrategy.QUERY_EXPANSION: self._expand_query,
            OptimizationStrategy.QUERY_REWRITING: self._rewrite_query,
            OptimizationStrategy.SYNONYM_REPLACEMENT: self._replace_synonyms,
            OptimizationStrategy.TCM_ENHANCEMENT: self._enhance_tcm_terms,
            OptimizationStrategy.SEMANTIC_ENRICHMENT: self._enrich_semantics,
            OptimizationStrategy.CONTEXT_INJECTION: self._inject_context
        }
    
    async def optimize_query(
        self,
        query: str,
        strategies: Optional[List[OptimizationStrategy]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> OptimizedQuery:
        """
        优化查询
        
        Args:
            query: 原始查询
            strategies: 优化策略列表
            context: 上下文信息
            
        Returns:
            优化后的查询
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # 分析查询
            analysis = await self.analyzer.analyze_query(query)
            
            # 选择优化策略
            if strategies is None:
                strategies = self._select_strategies(analysis)
            
            # 初始化优化结果
            optimized = OptimizedQuery(
                original_query=query,
                optimized_query=query,
                optimization_strategies=strategies
            )
            
            # 应用优化策略
            for strategy in strategies:
                if strategy in self.optimization_strategies:
                    optimized = await self.optimization_strategies[strategy](
                        optimized, analysis, context
                    )
            
            # 计算置信度提升
            optimized.confidence_boost = self._calculate_confidence_boost(
                analysis, optimized
            )
            
            # 记录指标
            processing_time = asyncio.get_event_loop().time() - start_time
            await self._record_metrics(analysis, optimized, processing_time)
            
            return optimized
            
        except Exception as e:
            logger.error(f"查询优化失败: {e}")
            return OptimizedQuery(
                original_query=query,
                optimized_query=query
            )
    
    def _select_strategies(self, analysis: QueryAnalysis) -> List[OptimizationStrategy]:
        """选择优化策略"""
        strategies = []
        
        # 基于查询类型选择策略
        if analysis.query_type == QueryType.SYMPTOM_INQUIRY:
            strategies.extend([
                OptimizationStrategy.SYNONYM_REPLACEMENT,
                OptimizationStrategy.TCM_ENHANCEMENT,
                OptimizationStrategy.QUERY_EXPANSION
            ])
        
        elif analysis.query_type == QueryType.CONSTITUTION_ANALYSIS:
            strategies.extend([
                OptimizationStrategy.TCM_ENHANCEMENT,
                OptimizationStrategy.CONTEXT_INJECTION
            ])
        
        elif analysis.query_type == QueryType.FORMULA_INQUIRY:
            strategies.extend([
                OptimizationStrategy.SYNONYM_REPLACEMENT,
                OptimizationStrategy.QUERY_EXPANSION
            ])
        
        elif analysis.query_type == QueryType.SYNDROME_DIAGNOSIS:
            strategies.extend([
                OptimizationStrategy.TCM_ENHANCEMENT,
                OptimizationStrategy.SEMANTIC_ENRICHMENT
            ])
        
        else:
            strategies.extend([
                OptimizationStrategy.QUERY_EXPANSION,
                OptimizationStrategy.SYNONYM_REPLACEMENT
            ])
        
        # 基于复杂度调整策略
        if analysis.complexity_score > 0.7:
            strategies.append(OptimizationStrategy.QUERY_REWRITING)
        
        if analysis.confidence < 0.6:
            strategies.append(OptimizationStrategy.SEMANTIC_ENRICHMENT)
        
        return list(set(strategies))  # 去重
    
    async def _expand_query(
        self,
        optimized: OptimizedQuery,
        analysis: QueryAnalysis,
        context: Optional[Dict[str, Any]]
    ) -> OptimizedQuery:
        """查询扩展"""
        expansion_terms = []
        
        # 基于症状扩展
        for symptom in analysis.symptoms:
            if symptom in self.tcm_dict.symptom_synonyms:
                expansion_terms.extend(self.tcm_dict.symptom_synonyms[symptom][:2])
        
        # 基于体质扩展
        for constitution in analysis.constitution_hints:
            if constitution in self.tcm_dict.constitution_terms:
                expansion_terms.extend(self.tcm_dict.constitution_terms[constitution][:3])
        
        # 基于证型扩展
        for syndrome in analysis.syndrome_hints:
            if syndrome in self.tcm_dict.syndrome_terms:
                expansion_terms.extend(self.tcm_dict.syndrome_terms[syndrome][:3])
        
        if expansion_terms:
            optimized.expansion_terms = list(set(expansion_terms))
            optimized.optimized_query += " " + " ".join(expansion_terms[:5])
        
        return optimized
    
    async def _rewrite_query(
        self,
        optimized: OptimizedQuery,
        analysis: QueryAnalysis,
        context: Optional[Dict[str, Any]]
    ) -> OptimizedQuery:
        """查询重写"""
        query = optimized.optimized_query
        rewritten_parts = {}
        
        # 重写模糊表达
        replacements = {
            "不舒服": "症状",
            "不好": "异常",
            "有问题": "症状",
            "怎么回事": "原因",
            "什么情况": "症状表现"
        }
        
        for old, new in replacements.items():
            if old in query:
                query = query.replace(old, new)
                rewritten_parts[old] = new
        
        # 标准化中医术语
        for herb, synonyms in self.tcm_dict.herb_synonyms.items():
            for synonym in synonyms:
                if synonym in query and herb not in query:
                    query = query.replace(synonym, herb)
                    rewritten_parts[synonym] = herb
        
        optimized.optimized_query = query
        optimized.rewritten_parts = rewritten_parts
        
        return optimized
    
    async def _replace_synonyms(
        self,
        optimized: OptimizedQuery,
        analysis: QueryAnalysis,
        context: Optional[Dict[str, Any]]
    ) -> OptimizedQuery:
        """同义词替换"""
        query = optimized.optimized_query
        
        # 症状同义词替换
        for symptom, synonyms in self.tcm_dict.symptom_synonyms.items():
            for synonym in synonyms:
                if synonym in query and symptom not in query:
                    query = query.replace(synonym, f"{synonym} {symptom}")
                    break
        
        optimized.optimized_query = query
        
        return optimized
    
    async def _enhance_tcm_terms(
        self,
        optimized: OptimizedQuery,
        analysis: QueryAnalysis,
        context: Optional[Dict[str, Any]]
    ) -> OptimizedQuery:
        """中医术语增强"""
        query = optimized.optimized_query
        
        # 添加相关中医概念
        tcm_enhancements = []
        
        if analysis.query_type == QueryType.SYMPTOM_INQUIRY:
            tcm_enhancements.extend(["辨证", "证型"])
        
        elif analysis.query_type == QueryType.CONSTITUTION_ANALYSIS:
            tcm_enhancements.extend(["体质", "调理"])
        
        elif analysis.query_type == QueryType.FORMULA_INQUIRY:
            tcm_enhancements.extend(["方剂", "功效", "主治"])
        
        if tcm_enhancements:
            query += " " + " ".join(tcm_enhancements)
        
        optimized.optimized_query = query
        
        return optimized
    
    async def _enrich_semantics(
        self,
        optimized: OptimizedQuery,
        analysis: QueryAnalysis,
        context: Optional[Dict[str, Any]]
    ) -> OptimizedQuery:
        """语义丰富"""
        if not self.embedding_service:
            return optimized
        
        try:
            # 这里可以使用嵌入服务进行语义扩展
            # 暂时简化处理
            semantic_terms = []
            
            # 基于查询类型添加语义相关词汇
            if analysis.query_type == QueryType.HEALTH_GUIDANCE:
                semantic_terms.extend(["养生", "保健", "预防"])
            
            elif analysis.query_type == QueryType.LIFESTYLE_ADVICE:
                semantic_terms.extend(["生活方式", "饮食", "运动"])
            
            if semantic_terms:
                optimized.optimized_query += " " + " ".join(semantic_terms)
            
        except Exception as e:
            logger.error(f"语义丰富失败: {e}")
        
        return optimized
    
    async def _inject_context(
        self,
        optimized: OptimizedQuery,
        analysis: QueryAnalysis,
        context: Optional[Dict[str, Any]]
    ) -> OptimizedQuery:
        """注入上下文"""
        if not context:
            return optimized
        
        context_terms = []
        
        # 从上下文中提取相关信息
        if 'user_profile' in context:
            profile = context['user_profile']
            
            if 'age' in profile:
                age = profile['age']
                if age < 18:
                    context_terms.append("儿童")
                elif age >= 65:
                    context_terms.append("老年人")
            
            if 'gender' in profile:
                if profile['gender'] == 'female':
                    context_terms.append("女性")
                elif profile['gender'] == 'male':
                    context_terms.append("男性")
            
            if 'constitution' in profile:
                context_terms.append(profile['constitution'])
        
        if 'session_history' in context:
            # 从会话历史中提取相关术语
            history = context['session_history']
            # 这里可以分析历史对话，提取相关概念
        
        if context_terms:
            optimized.added_context = context_terms
            optimized.optimized_query += " " + " ".join(context_terms)
        
        return optimized
    
    def _calculate_confidence_boost(
        self,
        analysis: QueryAnalysis,
        optimized: OptimizedQuery
    ) -> float:
        """计算置信度提升"""
        boost = 0.0
        
        # 基于优化策略数量
        boost += len(optimized.optimization_strategies) * 0.05
        
        # 基于扩展词汇数量
        boost += len(optimized.expansion_terms) * 0.02
        
        # 基于重写部分数量
        boost += len(optimized.rewritten_parts) * 0.03
        
        # 基于上下文注入
        boost += len(optimized.added_context) * 0.02
        
        return min(boost, 0.3)  # 最大提升30%
    
    async def _record_metrics(
        self,
        analysis: QueryAnalysis,
        optimized: OptimizedQuery,
        processing_time: float
    ):
        """记录指标"""
        await self.metrics_collector.record_histogram(
            "query_optimization_duration_seconds",
            processing_time,
            {
                "query_type": analysis.query_type.value,
                "strategy_count": str(len(optimized.optimization_strategies))
            }
        )
        
        await self.metrics_collector.record_histogram(
            "query_optimization_confidence_boost",
            optimized.confidence_boost,
            {"query_type": analysis.query_type.value}
        )
        
        await self.metrics_collector.increment_counter(
            "query_optimization_requests_total",
            {"query_type": analysis.query_type.value}
        )
        
        for strategy in optimized.optimization_strategies:
            await self.metrics_collector.increment_counter(
                "query_optimization_strategy_usage_total",
                {"strategy": strategy.value}
            ) 