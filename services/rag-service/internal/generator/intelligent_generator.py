#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能生成器 - 支持多种生成策略和中医特色功能
"""

import asyncio
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from loguru import logger

from ..model.document import Document
from ..observability.metrics import MetricsCollector
from ..resilience.circuit_breaker import CircuitBreakerService


class GenerationStrategy(str, Enum):
    """生成策略枚举"""
    STANDARD = "standard"                    # 标准生成
    TCM_PROFESSIONAL = "tcm_professional"   # 中医专业生成
    EDUCATIONAL = "educational"             # 教育性生成
    CONVERSATIONAL = "conversational"       # 对话式生成
    CLINICAL_GUIDANCE = "clinical_guidance" # 临床指导生成
    PREVENTIVE_CARE = "preventive_care"     # 预防保健生成


@dataclass
class GenerationContext:
    """生成上下文"""
    query: str
    documents: List[Document]
    user_profile: Optional[Dict[str, Any]] = None
    session_context: Optional[Dict[str, Any]] = None
    generation_type: str = "general"        # general, medical, tcm, educational
    max_length: int = 1000
    temperature: float = 0.7
    include_sources: bool = True
    include_reasoning: bool = False
    safety_check: bool = True
    language: str = "zh"


@dataclass
class GenerationResult:
    """生成结果"""
    content: str
    strategy_used: GenerationStrategy
    sources: List[str]
    reasoning_chain: Optional[str] = None
    confidence_score: float = 0.0
    safety_warnings: List[str] = None
    follow_up_questions: List[str] = None
    metadata: Optional[Dict[str, Any]] = None
    generation_time: float = 0.0


class QueryIntentAnalyzer:
    """查询意图分析器"""
    
    def __init__(self):
        self.intent_patterns = {
            "symptom_inquiry": [r"什么症状", r"有.*症状", r"症状.*表现"],
            "treatment_inquiry": [r"怎么治疗", r"如何调理", r"治疗方法", r"用什么药"],
            "diagnosis_inquiry": [r"是什么病", r"什么原因", r"为什么会"],
            "prevention_inquiry": [r"如何预防", r"预防.*方法", r"怎么避免"],
            "constitution_inquiry": [r"什么体质", r"体质.*特点", r"体质分析"],
            "lifestyle_inquiry": [r"生活.*建议", r"饮食.*注意", r"运动.*方法"],
            "formula_inquiry": [r"什么方剂", r"推荐.*方", r"中药.*配方"]
        }
        
        self.urgency_indicators = [
            "急性", "严重", "紧急", "立即", "马上", "疼痛剧烈", "高热", "呼吸困难"
        ]
        
        self.tcm_indicators = [
            "中医", "中药", "方剂", "辨证", "脏腑", "经络", "气血", "阴阳"
        ]
    
    def analyze_intent(self, query: str, documents: List[Document]) -> Dict[str, Any]:
        """
        分析查询意图
        
        Args:
            query: 查询文本
            documents: 相关文档
            
        Returns:
            意图分析结果
        """
        analysis = {
            "primary_intent": "general_inquiry",
            "secondary_intents": [],
            "urgency_level": "normal",  # low, normal, high, urgent
            "domain": "general",        # general, medical, tcm
            "complexity": "simple",     # simple, medium, complex
            "requires_professional": False,
            "safety_sensitive": False
        }
        
        # 检测主要意图
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query):
                    analysis["primary_intent"] = intent
                    break
        
        # 检测紧急程度
        urgency_count = sum(1 for indicator in self.urgency_indicators if indicator in query)
        if urgency_count >= 2:
            analysis["urgency_level"] = "urgent"
        elif urgency_count == 1:
            analysis["urgency_level"] = "high"
        
        # 检测领域
        if any(indicator in query for indicator in self.tcm_indicators):
            analysis["domain"] = "tcm"
        elif any(word in query for word in ["病", "症", "治疗", "诊断", "医"]):
            analysis["domain"] = "medical"
        
        # 检测复杂度
        if len(query) > 100 or "和" in query or "或" in query:
            analysis["complexity"] = "complex"
        elif len(query) > 50:
            analysis["complexity"] = "medium"
        
        # 检测是否需要专业建议
        professional_indicators = ["诊断", "治疗", "用药", "手术", "检查"]
        analysis["requires_professional"] = any(indicator in query for indicator in professional_indicators)
        
        # 检测安全敏感性
        safety_indicators = ["药物", "剂量", "副作用", "禁忌", "过敏"]
        analysis["safety_sensitive"] = any(indicator in query for indicator in safety_indicators)
        
        return analysis


class StrategySelector:
    """策略选择器"""
    
    def __init__(self):
        self.strategy_rules = {
            GenerationStrategy.TCM_PROFESSIONAL: self._should_use_tcm_professional,
            GenerationStrategy.CLINICAL_GUIDANCE: self._should_use_clinical_guidance,
            GenerationStrategy.EDUCATIONAL: self._should_use_educational,
            GenerationStrategy.PREVENTIVE_CARE: self._should_use_preventive_care,
            GenerationStrategy.CONVERSATIONAL: self._should_use_conversational,
            GenerationStrategy.STANDARD: self._should_use_standard,
        }
    
    def select_strategy(
        self, 
        context: GenerationContext, 
        intent_analysis: Dict[str, Any]
    ) -> GenerationStrategy:
        """
        选择生成策略
        
        Args:
            context: 生成上下文
            intent_analysis: 意图分析结果
            
        Returns:
            选择的策略
        """
        # 按优先级检查策略
        for strategy, rule_func in self.strategy_rules.items():
            if rule_func(context, intent_analysis):
                return strategy
        
        # 默认使用标准策略
        return GenerationStrategy.STANDARD
    
    def _should_use_tcm_professional(self, context: GenerationContext, analysis: Dict[str, Any]) -> bool:
        """是否使用中医专业策略"""
        return (
            analysis["domain"] == "tcm" or
            context.generation_type == "tcm" or
            analysis["primary_intent"] in ["formula_inquiry", "constitution_inquiry"]
        )
    
    def _should_use_clinical_guidance(self, context: GenerationContext, analysis: Dict[str, Any]) -> bool:
        """是否使用临床指导策略"""
        return (
            analysis["requires_professional"] or
            analysis["urgency_level"] in ["high", "urgent"] or
            analysis["primary_intent"] in ["treatment_inquiry", "diagnosis_inquiry"]
        )
    
    def _should_use_educational(self, context: GenerationContext, analysis: Dict[str, Any]) -> bool:
        """是否使用教育性策略"""
        return (
            context.generation_type == "educational" or
            analysis["complexity"] == "complex" or
            analysis["primary_intent"] == "symptom_inquiry"
        )
    
    def _should_use_preventive_care(self, context: GenerationContext, analysis: Dict[str, Any]) -> bool:
        """是否使用预防保健策略"""
        return (
            analysis["primary_intent"] in ["prevention_inquiry", "lifestyle_inquiry"] or
            context.generation_type == "preventive"
        )
    
    def _should_use_conversational(self, context: GenerationContext, analysis: Dict[str, Any]) -> bool:
        """是否使用对话式策略"""
        return (
            context.session_context is not None or
            analysis["complexity"] == "simple"
        )
    
    def _should_use_standard(self, context: GenerationContext, analysis: Dict[str, Any]) -> bool:
        """是否使用标准策略"""
        return True  # 默认策略


class TemplateManager:
    """模板管理器"""
    
    def __init__(self):
        self.templates = {
            GenerationStrategy.STANDARD: self._get_standard_template(),
            GenerationStrategy.TCM_PROFESSIONAL: self._get_tcm_professional_template(),
            GenerationStrategy.EDUCATIONAL: self._get_educational_template(),
            GenerationStrategy.CONVERSATIONAL: self._get_conversational_template(),
            GenerationStrategy.CLINICAL_GUIDANCE: self._get_clinical_guidance_template(),
            GenerationStrategy.PREVENTIVE_CARE: self._get_preventive_care_template(),
        }
    
    def get_template(self, strategy: GenerationStrategy) -> str:
        """获取模板"""
        return self.templates.get(strategy, self.templates[GenerationStrategy.STANDARD])
    
    def _get_standard_template(self) -> str:
        """标准模板"""
        return """基于提供的信息，我来回答您的问题：

{content}

{sources}

{follow_up}"""
    
    def _get_tcm_professional_template(self) -> str:
        """中医专业模板"""
        return """## 中医分析

### 辨证分析
{syndrome_analysis}

### 治疗原则
{treatment_principles}

### 方剂推荐
{formula_recommendations}

### 生活调理
{lifestyle_guidance}

{sources}

**注意：以上建议仅供参考，具体治疗请咨询专业中医师。**

{follow_up}"""
    
    def _get_educational_template(self) -> str:
        """教育性模板"""
        return """## 详细解答

### 基本概念
{basic_concepts}

### 详细说明
{detailed_explanation}

### 相关知识
{related_knowledge}

### 注意事项
{precautions}

{sources}

{follow_up}"""
    
    def _get_conversational_template(self) -> str:
        """对话式模板"""
        return """根据您的问题，我来为您解答：

{content}

希望这个回答对您有帮助。{sources}

{follow_up}"""
    
    def _get_clinical_guidance_template(self) -> str:
        """临床指导模板"""
        return """## 专业建议

### 当前情况分析
{situation_analysis}

### 建议措施
{recommended_actions}

### 注意事项
{important_notes}

### 何时就医
{when_to_seek_help}

{sources}

**重要提醒：本建议不能替代专业医疗诊断，如有疑虑请及时就医。**

{follow_up}"""
    
    def _get_preventive_care_template(self) -> str:
        """预防保健模板"""
        return """## 预防保健指导

### 预防措施
{prevention_measures}

### 生活方式建议
{lifestyle_recommendations}

### 饮食调理
{dietary_guidance}

### 运动建议
{exercise_recommendations}

### 定期检查
{regular_checkups}

{sources}

{follow_up}"""


class ContentGenerator:
    """内容生成器"""
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.template_manager = TemplateManager()
    
    async def generate_content(
        self,
        context: GenerationContext,
        strategy: GenerationStrategy,
        intent_analysis: Dict[str, Any]
    ) -> str:
        """
        生成内容
        
        Args:
            context: 生成上下文
            strategy: 生成策略
            intent_analysis: 意图分析结果
            
        Returns:
            生成的内容
        """
        # 构建提示词
        prompt = self._build_prompt(context, strategy, intent_analysis)
        
        # 调用LLM生成
        response = await self._call_llm(prompt, context)
        
        # 后处理
        content = self._postprocess_content(response, strategy)
        
        return content
    
    def _build_prompt(
        self,
        context: GenerationContext,
        strategy: GenerationStrategy,
        intent_analysis: Dict[str, Any]
    ) -> str:
        """构建提示词"""
        # 基础提示词
        base_prompt = f"""你是一个专业的健康咨询助手，特别擅长中医养生和现代医学知识。

用户问题：{context.query}

相关资料：
"""
        
        # 添加文档内容
        for i, doc in enumerate(context.documents[:5], 1):
            base_prompt += f"\n{i}. {doc.content[:500]}...\n"
        
        # 根据策略添加特定指导
        strategy_guidance = self._get_strategy_guidance(strategy, intent_analysis)
        base_prompt += f"\n{strategy_guidance}\n"
        
        # 添加用户画像信息
        if context.user_profile:
            base_prompt += f"\n用户信息：{json.dumps(context.user_profile, ensure_ascii=False)}\n"
        
        # 添加会话上下文
        if context.session_context:
            base_prompt += f"\n对话历史：{json.dumps(context.session_context, ensure_ascii=False)}\n"
        
        base_prompt += "\n请基于以上信息，为用户提供准确、专业、有用的回答。"
        
        return base_prompt
    
    def _get_strategy_guidance(self, strategy: GenerationStrategy, intent_analysis: Dict[str, Any]) -> str:
        """获取策略指导"""
        guidance_map = {
            GenerationStrategy.STANDARD: "请提供清晰、准确的回答。",
            GenerationStrategy.TCM_PROFESSIONAL: """请从中医角度分析，包括：
1. 辨证分析（如适用）
2. 治疗原则
3. 方剂推荐（如适用）
4. 生活调理建议
请确保专业性和准确性。""",
            GenerationStrategy.EDUCATIONAL: """请提供教育性的详细解答，包括：
1. 基本概念解释
2. 详细机制说明
3. 相关知识扩展
4. 注意事项
语言要通俗易懂。""",
            GenerationStrategy.CONVERSATIONAL: "请用亲切、自然的对话方式回答，就像朋友间的交流。",
            GenerationStrategy.CLINICAL_GUIDANCE: """请提供专业的临床指导，包括：
1. 情况分析
2. 建议措施
3. 重要注意事项
4. 何时需要就医
请强调专业医疗的重要性。""",
            GenerationStrategy.PREVENTIVE_CARE: """请重点提供预防保健建议，包括：
1. 预防措施
2. 生活方式调整
3. 饮食建议
4. 运动指导
5. 定期检查建议"""
        }
        
        return guidance_map.get(strategy, "请提供有用的回答。")
    
    async def _call_llm(self, prompt: str, context: GenerationContext) -> str:
        """调用LLM"""
        try:
            # 这里应该调用实际的LLM API
            # 暂时返回模拟响应
            response = await self._simulate_llm_response(prompt, context)
            return response
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            return "抱歉，我暂时无法为您提供回答。请稍后再试。"
    
    async def _simulate_llm_response(self, prompt: str, context: GenerationContext) -> str:
        """模拟LLM响应"""
        # 这是一个简化的模拟实现
        await asyncio.sleep(0.1)  # 模拟网络延迟
        
        return f"基于您的问题'{context.query}'和相关资料，我为您提供以下回答：\n\n这是一个模拟的回答内容。在实际实现中，这里会调用真正的LLM API来生成专业的回答。"
    
    def _postprocess_content(self, content: str, strategy: GenerationStrategy) -> str:
        """后处理内容"""
        # 清理格式
        content = content.strip()
        
        # 根据策略进行特定处理
        if strategy == GenerationStrategy.TCM_PROFESSIONAL:
            content = self._enhance_tcm_content(content)
        elif strategy == GenerationStrategy.CLINICAL_GUIDANCE:
            content = self._enhance_clinical_content(content)
        
        return content
    
    def _enhance_tcm_content(self, content: str) -> str:
        """增强中医内容"""
        # 添加中医术语解释
        # 这里可以添加更复杂的中医内容增强逻辑
        return content
    
    def _enhance_clinical_content(self, content: str) -> str:
        """增强临床内容"""
        # 添加医疗免责声明
        if "**重要提醒：" not in content:
            content += "\n\n**重要提醒：本建议不能替代专业医疗诊断，如有疑虑请及时就医。**"
        return content


class SafetyChecker:
    """安全检查器"""
    
    def __init__(self):
        self.prohibited_claims = [
            "包治百病", "立即治愈", "绝对有效", "无副作用", "替代医生",
            "不用看医生", "保证治愈", "神药", "特效药"
        ]
        
        self.sensitive_topics = [
            "自杀", "自残", "毒品", "非法药物", "未经批准的治疗方法"
        ]
        
        self.medical_disclaimers = [
            "本建议不能替代专业医疗诊断",
            "如有疑虑请及时就医",
            "请咨询专业医师",
            "仅供参考"
        ]
    
    def check_safety(self, content: str, context: GenerationContext) -> Tuple[bool, List[str]]:
        """
        检查内容安全性
        
        Args:
            content: 生成的内容
            context: 生成上下文
            
        Returns:
            (是否安全, 警告列表)
        """
        warnings = []
        is_safe = True
        
        # 检查禁用声明
        for claim in self.prohibited_claims:
            if claim in content:
                warnings.append(f"包含禁用声明: {claim}")
                is_safe = False
        
        # 检查敏感话题
        for topic in self.sensitive_topics:
            if topic in content:
                warnings.append(f"涉及敏感话题: {topic}")
                is_safe = False
        
        # 检查医疗免责声明
        if context.generation_type in ["medical", "tcm"] and context.safety_check:
            has_disclaimer = any(disclaimer in content for disclaimer in self.medical_disclaimers)
            if not has_disclaimer:
                warnings.append("缺少医疗免责声明")
        
        return is_safe, warnings


class QualityAssessor:
    """质量评估器"""
    
    def __init__(self):
        self.quality_metrics = [
            "length_appropriateness",
            "relevance",
            "completeness",
            "professionalism",
            "safety"
        ]
    
    def assess_quality(
        self,
        content: str,
        context: GenerationContext,
        strategy: GenerationStrategy
    ) -> Dict[str, float]:
        """
        评估内容质量
        
        Args:
            content: 生成的内容
            context: 生成上下文
            strategy: 生成策略
            
        Returns:
            质量评分字典
        """
        scores = {}
        
        # 长度适当性
        scores["length_appropriateness"] = self._assess_length(content, context.max_length)
        
        # 相关性
        scores["relevance"] = self._assess_relevance(content, context.query)
        
        # 完整性
        scores["completeness"] = self._assess_completeness(content, strategy)
        
        # 专业性
        scores["professionalism"] = self._assess_professionalism(content, context.generation_type)
        
        # 安全性
        scores["safety"] = self._assess_safety(content, context)
        
        return scores
    
    def _assess_length(self, content: str, max_length: int) -> float:
        """评估长度适当性"""
        length = len(content)
        if length < max_length * 0.3:
            return 0.5  # 太短
        elif length > max_length * 1.2:
            return 0.7  # 太长
        else:
            return 1.0  # 适当
    
    def _assess_relevance(self, content: str, query: str) -> float:
        """评估相关性"""
        # 简化的相关性评估
        import jieba
        query_words = set(jieba.lcut(query))
        content_words = set(jieba.lcut(content))
        
        if not query_words:
            return 0.5
        
        intersection = query_words.intersection(content_words)
        relevance = len(intersection) / len(query_words)
        
        return min(relevance * 2, 1.0)  # 放大相关性分数
    
    def _assess_completeness(self, content: str, strategy: GenerationStrategy) -> float:
        """评估完整性"""
        # 根据策略检查必要元素
        required_elements = {
            GenerationStrategy.TCM_PROFESSIONAL: ["辨证", "治疗", "建议"],
            GenerationStrategy.EDUCATIONAL: ["解释", "说明", "注意"],
            GenerationStrategy.CLINICAL_GUIDANCE: ["分析", "建议", "就医"],
            GenerationStrategy.PREVENTIVE_CARE: ["预防", "生活", "建议"]
        }
        
        elements = required_elements.get(strategy, [])
        if not elements:
            return 1.0
        
        found_elements = sum(1 for element in elements if element in content)
        return found_elements / len(elements)
    
    def _assess_professionalism(self, content: str, generation_type: str) -> float:
        """评估专业性"""
        professional_indicators = ["建议", "注意", "专业", "医师", "咨询"]
        unprofessional_indicators = ["绝对", "一定", "包治", "神效"]
        
        professional_count = sum(1 for indicator in professional_indicators if indicator in content)
        unprofessional_count = sum(1 for indicator in unprofessional_indicators if indicator in content)
        
        score = min(professional_count * 0.2, 1.0) - unprofessional_count * 0.3
        return max(score, 0.0)
    
    def _assess_safety(self, content: str, context: GenerationContext) -> float:
        """评估安全性"""
        safety_checker = SafetyChecker()
        is_safe, warnings = safety_checker.check_safety(content, context)
        
        if is_safe:
            return 1.0
        else:
            return max(1.0 - len(warnings) * 0.2, 0.0)


class IntelligentGenerator:
    """智能生成器"""
    
    def __init__(
        self,
        config: Dict[str, Any],
        metrics_collector: MetricsCollector,
        circuit_breaker: CircuitBreakerService,
        llm_client=None
    ):
        self.config = config
        self.metrics_collector = metrics_collector
        self.circuit_breaker = circuit_breaker
        self.llm_client = llm_client
        
        # 初始化组件
        self.intent_analyzer = QueryIntentAnalyzer()
        self.strategy_selector = StrategySelector()
        self.content_generator = ContentGenerator(llm_client)
        self.safety_checker = SafetyChecker()
        self.quality_assessor = QualityAssessor()
    
    async def generate(self, context: GenerationContext) -> GenerationResult:
        """
        执行智能生成
        
        Args:
            context: 生成上下文
            
        Returns:
            生成结果
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # 分析查询意图
            intent_analysis = self.intent_analyzer.analyze_intent(context.query, context.documents)
            logger.info(f"意图分析结果: {intent_analysis}")
            
            # 选择生成策略
            strategy = self.strategy_selector.select_strategy(context, intent_analysis)
            logger.info(f"选择的生成策略: {strategy}")
            
            # 生成内容
            content = await self.content_generator.generate_content(context, strategy, intent_analysis)
            
            # 安全检查
            is_safe, safety_warnings = self.safety_checker.check_safety(content, context)
            if not is_safe and context.safety_check:
                content = self._apply_safety_fixes(content, safety_warnings)
            
            # 质量评估
            quality_scores = self.quality_assessor.assess_quality(content, context, strategy)
            confidence_score = sum(quality_scores.values()) / len(quality_scores)
            
            # 生成推理链
            reasoning_chain = None
            if context.include_reasoning:
                reasoning_chain = self._generate_reasoning_chain(intent_analysis, strategy, quality_scores)
            
            # 生成后续问题
            follow_up_questions = self._generate_follow_up_questions(context.query, intent_analysis)
            
            # 提取来源
            sources = self._extract_sources(context.documents) if context.include_sources else []
            
            # 记录指标
            end_time = asyncio.get_event_loop().time()
            generation_time = end_time - start_time
            
            await self._record_metrics(strategy, generation_time, len(content), confidence_score)
            
            return GenerationResult(
                content=content,
                strategy_used=strategy,
                sources=sources,
                reasoning_chain=reasoning_chain,
                confidence_score=confidence_score,
                safety_warnings=safety_warnings if not is_safe else None,
                follow_up_questions=follow_up_questions,
                metadata={
                    "intent_analysis": intent_analysis,
                    "quality_scores": quality_scores
                },
                generation_time=generation_time
            )
            
        except Exception as e:
            logger.error(f"生成失败: {e}")
            await self.metrics_collector.increment_counter("generation_errors")
            raise
    
    def _apply_safety_fixes(self, content: str, warnings: List[str]) -> str:
        """应用安全修复"""
        fixed_content = content
        
        # 移除禁用声明
        prohibited_claims = [
            "包治百病", "立即治愈", "绝对有效", "无副作用", "替代医生"
        ]
        
        for claim in prohibited_claims:
            fixed_content = fixed_content.replace(claim, "可能有助于")
        
        # 添加免责声明
        if "医疗" in content or "治疗" in content:
            fixed_content += "\n\n**重要提醒：本建议不能替代专业医疗诊断，如有疑虑请及时就医。**"
        
        return fixed_content
    
    def _generate_reasoning_chain(
        self,
        intent_analysis: Dict[str, Any],
        strategy: GenerationStrategy,
        quality_scores: Dict[str, float]
    ) -> str:
        """生成推理链"""
        reasoning = f"推理过程：\n"
        reasoning += f"1. 意图分析：识别为{intent_analysis['primary_intent']}类型查询\n"
        reasoning += f"2. 策略选择：基于意图和复杂度选择{strategy.value}策略\n"
        reasoning += f"3. 内容生成：根据策略模板和相关文档生成回答\n"
        reasoning += f"4. 质量评估：综合评分{sum(quality_scores.values())/len(quality_scores):.2f}\n"
        
        return reasoning
    
    def _generate_follow_up_questions(self, query: str, intent_analysis: Dict[str, Any]) -> List[str]:
        """生成后续问题"""
        follow_ups = []
        
        intent_to_questions = {
            "symptom_inquiry": [
                "这些症状持续多长时间了？",
                "还有其他伴随症状吗？",
                "是否影响了日常生活？"
            ],
            "treatment_inquiry": [
                "您之前尝试过什么治疗方法？",
                "有什么药物过敏史吗？",
                "希望了解更多关于预防的信息吗？"
            ],
            "prevention_inquiry": [
                "您的生活习惯如何？",
                "饮食方面有什么偏好？",
                "运动情况怎么样？"
            ]
        }
        
        primary_intent = intent_analysis.get("primary_intent", "general_inquiry")
        follow_ups = intent_to_questions.get(primary_intent, [
            "还有其他相关问题吗？",
            "需要更详细的解释吗？"
        ])
        
        return follow_ups[:3]  # 最多返回3个后续问题
    
    def _extract_sources(self, documents: List[Document]) -> List[str]:
        """提取来源"""
        sources = []
        for doc in documents[:5]:  # 最多5个来源
            if doc.metadata and doc.metadata.source:
                sources.append(doc.metadata.source)
            else:
                sources.append("相关医学资料")
        
        return list(set(sources))  # 去重
    
    async def _record_metrics(
        self,
        strategy: GenerationStrategy,
        generation_time: float,
        content_length: int,
        confidence_score: float
    ):
        """记录指标"""
        await self.metrics_collector.record_histogram(
            "generation_duration_seconds",
            generation_time,
            {"strategy": strategy.value}
        )
        
        await self.metrics_collector.record_histogram(
            "generation_content_length",
            content_length,
            {"strategy": strategy.value}
        )
        
        await self.metrics_collector.record_histogram(
            "generation_confidence_score",
            confidence_score,
            {"strategy": strategy.value}
        )
        
        await self.metrics_collector.increment_counter(
            "generation_requests_total",
            {"strategy": strategy.value}
        ) 