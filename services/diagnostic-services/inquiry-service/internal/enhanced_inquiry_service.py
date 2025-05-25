#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强版问诊服务

该模块是问诊服务的增强版本，集成了并行处理、智能缓存、批量诊断和模型推理优化，
提供高性能的中医问诊数据采集和分析服务。
"""

import asyncio
import time
import uuid
import hashlib
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import numpy as np
from loguru import logger

# 导入通用组件
from services.common.governance.circuit_breaker import (
    CircuitBreaker, CircuitBreakerConfig, get_circuit_breaker
)
from services.common.governance.rate_limiter import (
    RateLimitConfig, get_rate_limiter, rate_limit
)
from services.common.observability.tracing import (
    get_tracer, trace, SpanKind
)

class SymptomCategory(Enum):
    """症状分类"""
    GENERAL = "general"  # 一般症状
    DIGESTIVE = "digestive"  # 消化系统
    RESPIRATORY = "respiratory"  # 呼吸系统
    CARDIOVASCULAR = "cardiovascular"  # 心血管系统
    NERVOUS = "nervous"  # 神经系统
    MUSCULOSKELETAL = "musculoskeletal"  # 肌肉骨骼
    SKIN = "skin"  # 皮肤
    MENTAL = "mental"  # 精神心理

class QuestionType(Enum):
    """问题类型"""
    OPEN_ENDED = "open_ended"  # 开放式问题
    MULTIPLE_CHOICE = "multiple_choice"  # 多选题
    SINGLE_CHOICE = "single_choice"  # 单选题
    SCALE = "scale"  # 量表题
    BOOLEAN = "boolean"  # 是否题

@dataclass
class InquiryQuestion:
    """问诊问题"""
    id: str
    category: SymptomCategory
    question_type: QuestionType
    question: str
    options: Optional[List[str]] = None
    required: bool = True
    follow_up_conditions: Optional[Dict[str, Any]] = None
    weight: float = 1.0

@dataclass
class InquiryAnswer:
    """问诊回答"""
    question_id: str
    answer: Any
    confidence: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class InquirySession:
    """问诊会话"""
    session_id: str
    patient_id: str
    questions: List[InquiryQuestion]
    answers: List[InquiryAnswer]
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "active"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class InquiryResult:
    """问诊结果"""
    session_id: str
    patient_id: str
    chief_complaint: str  # 主诉
    present_illness: str  # 现病史
    past_history: str  # 既往史
    family_history: str  # 家族史
    symptoms: List[Dict[str, Any]]  # 症状列表
    syndrome_analysis: Dict[str, Any]  # 证候分析
    recommendations: List[str]  # 建议
    confidence_score: float
    processing_time_ms: float

@dataclass
class BatchInquiryRequest:
    """批量问诊请求"""
    batch_id: str
    sessions: List[InquirySession]
    priority: int = 1
    created_at: datetime = field(default_factory=datetime.now)

class EnhancedInquiryService:
    """增强版问诊服务"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化增强版问诊服务
        
        Args:
            config: 配置信息
        """
        self.config = config
        
        # 增强配置
        self.enhanced_config = {
            'parallel_processing': {
                'enabled': True,
                'max_workers': 4,
                'batch_size': 10
            },
            'caching': {
                'enabled': True,
                'ttl_seconds': {
                    'question_set': 3600,
                    'analysis_result': 1800,
                    'syndrome_pattern': 7200
                },
                'max_cache_size': 10000
            },
            'model_optimization': {
                'batch_inference': True,
                'model_caching': True,
                'quantization': False,
                'max_sequence_length': 512
            },
            'intelligent_questioning': {
                'adaptive': True,
                'max_questions': 50,
                'min_questions': 10,
                'confidence_threshold': 0.8
            }
        }
        
        # 问题库
        self.question_bank: Dict[SymptomCategory, List[InquiryQuestion]] = {}
        self._initialize_question_bank()
        
        # 会话管理
        self.active_sessions: Dict[str, InquirySession] = {}
        
        # 批处理队列
        self.batch_queue: asyncio.Queue = asyncio.Queue()
        
        # 缓存
        self.cache: Dict[str, Tuple[Any, datetime]] = {}
        
        # 性能统计
        self.stats = {
            'total_sessions': 0,
            'completed_sessions': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'average_questions_per_session': 0.0,
            'average_processing_time_ms': 0.0,
            'batch_processed': 0
        }
        
        # 断路器配置
        self.circuit_breaker_configs = {
            'model_inference': CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=30.0,
                timeout=10.0
            ),
            'cache': CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=10.0,
                timeout=1.0
            )
        }
        
        # 限流配置
        self.rate_limit_configs = {
            'inquiry': RateLimitConfig(rate=50.0, burst=100),
            'analysis': RateLimitConfig(rate=20.0, burst=40)
        }
        
        # 后台任务
        self.background_tasks: List[asyncio.Task] = []
        
        logger.info("增强版问诊服务初始化完成")
    
    def _initialize_question_bank(self):
        """初始化问题库"""
        # 一般症状问题
        self.question_bank[SymptomCategory.GENERAL] = [
            InquiryQuestion(
                id="g001",
                category=SymptomCategory.GENERAL,
                question_type=QuestionType.OPEN_ENDED,
                question="请描述您的主要不适症状",
                required=True,
                weight=2.0
            ),
            InquiryQuestion(
                id="g002",
                category=SymptomCategory.GENERAL,
                question_type=QuestionType.SCALE,
                question="您的症状持续了多长时间？",
                options=["1天以内", "1-3天", "3-7天", "1-2周", "2周以上"],
                required=True
            ),
            InquiryQuestion(
                id="g003",
                category=SymptomCategory.GENERAL,
                question_type=QuestionType.MULTIPLE_CHOICE,
                question="您有以下哪些伴随症状？",
                options=["发热", "乏力", "食欲不振", "失眠", "出汗异常", "无"],
                required=False
            )
        ]
        
        # 消化系统问题
        self.question_bank[SymptomCategory.DIGESTIVE] = [
            InquiryQuestion(
                id="d001",
                category=SymptomCategory.DIGESTIVE,
                question_type=QuestionType.BOOLEAN,
                question="您是否有腹痛？",
                follow_up_conditions={"answer": True, "next_questions": ["d002", "d003"]}
            ),
            InquiryQuestion(
                id="d002",
                category=SymptomCategory.DIGESTIVE,
                question_type=QuestionType.SINGLE_CHOICE,
                question="腹痛的位置在哪里？",
                options=["上腹部", "中腹部", "下腹部", "全腹", "不固定"],
                required=False
            )
        ]
        
        # 添加更多类别的问题...
    
    async def initialize(self):
        """初始化服务"""
        # 启动后台任务
        self._start_background_tasks()
        logger.info("问诊服务初始化完成")
    
    def _start_background_tasks(self):
        """启动后台任务"""
        # 批处理处理器
        self.background_tasks.append(
            asyncio.create_task(self._batch_processor())
        )
        
        # 缓存清理器
        self.background_tasks.append(
            asyncio.create_task(self._cache_cleaner())
        )
        
        # 会话清理器
        self.background_tasks.append(
            asyncio.create_task(self._session_cleaner())
        )
    
    @trace(service_name="inquiry-service", kind=SpanKind.SERVER)
    @rate_limit(name="inquiry", tokens=1)
    async def start_inquiry_session(
        self,
        patient_id: str,
        chief_complaint: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> InquirySession:
        """
        开始问诊会话
        
        Args:
            patient_id: 患者ID
            chief_complaint: 主诉
            metadata: 元数据
            
        Returns:
            问诊会话
        """
        session_id = str(uuid.uuid4())
        
        # 基于主诉智能选择问题
        questions = await self._select_questions(chief_complaint)
        
        session = InquirySession(
            session_id=session_id,
            patient_id=patient_id,
            questions=questions,
            answers=[],
            start_time=datetime.now(),
            metadata=metadata or {}
        )
        
        # 保存会话
        self.active_sessions[session_id] = session
        self.stats['total_sessions'] += 1
        
        logger.info(f"开始问诊会话: {session_id}, 患者: {patient_id}")
        
        return session
    
    async def _select_questions(self, chief_complaint: str) -> List[InquiryQuestion]:
        """
        基于主诉智能选择问题
        
        Args:
            chief_complaint: 主诉
            
        Returns:
            问题列表
        """
        # 检查缓存
        cache_key = self._generate_cache_key("questions", chief_complaint)
        cached_questions = await self._get_from_cache(cache_key)
        if cached_questions:
            return cached_questions
        
        # 分析主诉，确定相关症状类别
        relevant_categories = await self._analyze_chief_complaint(chief_complaint)
        
        # 选择问题
        selected_questions = []
        
        # 添加通用问题
        selected_questions.extend(self.question_bank[SymptomCategory.GENERAL])
        
        # 添加相关类别的问题
        for category in relevant_categories:
            if category in self.question_bank:
                selected_questions.extend(self.question_bank[category][:5])  # 每个类别最多5个问题
        
        # 根据权重排序
        selected_questions.sort(key=lambda q: q.weight, reverse=True)
        
        # 限制问题数量
        max_questions = self.enhanced_config['intelligent_questioning']['max_questions']
        selected_questions = selected_questions[:max_questions]
        
        # 缓存结果
        await self._set_to_cache(cache_key, selected_questions)
        
        return selected_questions
    
    async def _analyze_chief_complaint(self, chief_complaint: str) -> List[SymptomCategory]:
        """分析主诉，确定相关症状类别"""
        # 简化实现：基于关键词匹配
        categories = []
        
        keyword_map = {
            SymptomCategory.DIGESTIVE: ["腹", "胃", "消化", "便", "食欲"],
            SymptomCategory.RESPIRATORY: ["咳", "喘", "呼吸", "胸闷", "痰"],
            SymptomCategory.CARDIOVASCULAR: ["心", "胸痛", "心悸", "血压"],
            SymptomCategory.NERVOUS: ["头痛", "头晕", "失眠", "麻木"],
            SymptomCategory.MENTAL: ["焦虑", "抑郁", "情绪", "压力"]
        }
        
        for category, keywords in keyword_map.items():
            if any(keyword in chief_complaint for keyword in keywords):
                categories.append(category)
        
        # 如果没有匹配到特定类别，返回通用类别
        if not categories:
            categories = [SymptomCategory.GENERAL]
        
        return categories
    
    @trace(service_name="inquiry-service", kind=SpanKind.SERVER)
    @rate_limit(name="inquiry", tokens=1)
    async def submit_answer(
        self,
        session_id: str,
        question_id: str,
        answer: Any,
        confidence: float = 1.0
    ) -> Optional[InquiryQuestion]:
        """
        提交问题答案
        
        Args:
            session_id: 会话ID
            question_id: 问题ID
            answer: 答案
            confidence: 置信度
            
        Returns:
            下一个问题（如果有）
        """
        session = self.active_sessions.get(session_id)
        if not session:
            raise ValueError(f"会话不存在: {session_id}")
        
        # 记录答案
        inquiry_answer = InquiryAnswer(
            question_id=question_id,
            answer=answer,
            confidence=confidence
        )
        session.answers.append(inquiry_answer)
        
        # 检查是否需要后续问题
        next_question = await self._get_next_question(session, question_id, answer)
        
        # 检查是否可以结束问诊
        if not next_question and await self._should_end_inquiry(session):
            session.status = "completed"
            session.end_time = datetime.now()
            
        return next_question
    
    async def _get_next_question(
        self,
        session: InquirySession,
        current_question_id: str,
        answer: Any
    ) -> Optional[InquiryQuestion]:
        """获取下一个问题"""
        # 查找当前问题
        current_question = None
        for q in session.questions:
            if q.id == current_question_id:
                current_question = q
                break
        
        if not current_question:
            return None
        
        # 检查后续条件
        if current_question.follow_up_conditions:
            condition = current_question.follow_up_conditions
            if condition.get("answer") == answer:
                # 返回后续问题
                next_question_ids = condition.get("next_questions", [])
                for q in session.questions:
                    if q.id in next_question_ids and q.id not in [a.question_id for a in session.answers]:
                        return q
        
        # 返回下一个未回答的问题
        answered_ids = {a.question_id for a in session.answers}
        for q in session.questions:
            if q.id not in answered_ids:
                return q
        
        return None
    
    async def _should_end_inquiry(self, session: InquirySession) -> bool:
        """判断是否应该结束问诊"""
        # 检查最少问题数
        min_questions = self.enhanced_config['intelligent_questioning']['min_questions']
        if len(session.answers) < min_questions:
            return False
        
        # 检查必答问题
        required_questions = [q for q in session.questions if q.required]
        answered_ids = {a.question_id for a in session.answers}
        for q in required_questions:
            if q.id not in answered_ids:
                return False
        
        # 检查置信度
        if session.answers:
            avg_confidence = np.mean([a.confidence for a in session.answers])
            threshold = self.enhanced_config['intelligent_questioning']['confidence_threshold']
            if avg_confidence >= threshold:
                return True
        
        return True
    
    @trace(service_name="inquiry-service", kind=SpanKind.SERVER)
    @rate_limit(name="analysis", tokens=2)
    async def analyze_inquiry(self, session_id: str) -> InquiryResult:
        """
        分析问诊结果
        
        Args:
            session_id: 会话ID
            
        Returns:
            问诊结果
        """
        start_time = time.time()
        
        session = self.active_sessions.get(session_id)
        if not session:
            raise ValueError(f"会话不存在: {session_id}")
        
        # 检查缓存
        cache_key = self._generate_cache_key("analysis", session_id)
        cached_result = await self._get_from_cache(cache_key)
        if cached_result:
            self.stats['cache_hits'] += 1
            return cached_result
        
        self.stats['cache_misses'] += 1
        
        # 并行处理不同类型的分析
        if self.enhanced_config['parallel_processing']['enabled']:
            # 并行执行多个分析任务
            tasks = [
                self._extract_chief_complaint(session),
                self._extract_present_illness(session),
                self._extract_symptoms(session),
                self._analyze_syndrome(session)
            ]
            
            results = await asyncio.gather(*tasks)
            chief_complaint, present_illness, symptoms, syndrome_analysis = results
        else:
            # 串行执行
            chief_complaint = await self._extract_chief_complaint(session)
            present_illness = await self._extract_present_illness(session)
            symptoms = await self._extract_symptoms(session)
            syndrome_analysis = await self._analyze_syndrome(session)
        
        # 生成建议
        recommendations = await self._generate_recommendations(syndrome_analysis)
        
        # 计算置信度
        confidence_score = self._calculate_confidence(session)
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        result = InquiryResult(
            session_id=session_id,
            patient_id=session.patient_id,
            chief_complaint=chief_complaint,
            present_illness=present_illness,
            past_history="",  # 简化实现
            family_history="",  # 简化实现
            symptoms=symptoms,
            syndrome_analysis=syndrome_analysis,
            recommendations=recommendations,
            confidence_score=confidence_score,
            processing_time_ms=processing_time_ms
        )
        
        # 缓存结果
        await self._set_to_cache(cache_key, result)
        
        # 更新统计
        self.stats['completed_sessions'] += 1
        self._update_stats(processing_time_ms, len(session.questions))
        
        return result
    
    async def _extract_chief_complaint(self, session: InquirySession) -> str:
        """提取主诉"""
        # 查找主诉相关问题的答案
        for answer in session.answers:
            question = next((q for q in session.questions if q.id == answer.question_id), None)
            if question and question.id == "g001":  # 主诉问题ID
                return str(answer.answer)
        
        return "未明确主诉"
    
    async def _extract_present_illness(self, session: InquirySession) -> str:
        """提取现病史"""
        illness_info = []
        
        # 收集相关信息
        for answer in session.answers:
            question = next((q for q in session.questions if q.id == answer.question_id), None)
            if question and question.category in [SymptomCategory.GENERAL]:
                illness_info.append(f"{question.question}: {answer.answer}")
        
        return "；".join(illness_info)
    
    async def _extract_symptoms(self, session: InquirySession) -> List[Dict[str, Any]]:
        """提取症状列表"""
        symptoms = []
        
        for answer in session.answers:
            question = next((q for q in session.questions if q.id == answer.question_id), None)
            if question and answer.answer not in [None, "无", "否"]:
                symptom = {
                    "category": question.category.value,
                    "description": question.question,
                    "value": answer.answer,
                    "confidence": answer.confidence
                }
                symptoms.append(symptom)
        
        return symptoms
    
    async def _analyze_syndrome(self, session: InquirySession) -> Dict[str, Any]:
        """分析证候"""
        # 简化实现：基于症状模式匹配
        syndrome_patterns = {
            "气虚": ["乏力", "气短", "自汗", "食少"],
            "血虚": ["面色苍白", "头晕", "心悸", "失眠"],
            "阴虚": ["潮热", "盗汗", "口干", "便秘"],
            "阳虚": ["畏寒", "肢冷", "腰膝酸软", "夜尿频"]
        }
        
        # 统计匹配度
        syndrome_scores = {}
        symptoms_text = " ".join([str(a.answer) for a in session.answers])
        
        for syndrome, patterns in syndrome_patterns.items():
            score = sum(1 for pattern in patterns if pattern in symptoms_text)
            if score > 0:
                syndrome_scores[syndrome] = score / len(patterns)
        
        # 选择最可能的证候
        if syndrome_scores:
            primary_syndrome = max(syndrome_scores.items(), key=lambda x: x[1])
            return {
                "primary": primary_syndrome[0],
                "confidence": primary_syndrome[1],
                "all_syndromes": syndrome_scores
            }
        
        return {
            "primary": "未明确",
            "confidence": 0.0,
            "all_syndromes": {}
        }
    
    async def _generate_recommendations(self, syndrome_analysis: Dict[str, Any]) -> List[str]:
        """生成建议"""
        recommendations = []
        
        syndrome = syndrome_analysis.get("primary", "")
        
        # 基于证候的建议
        syndrome_recommendations = {
            "气虚": [
                "建议适当休息，避免过度劳累",
                "可适当食用补气食物如山药、大枣等",
                "建议进行温和的运动如太极拳、八段锦"
            ],
            "血虚": [
                "建议保证充足睡眠",
                "可适当食用补血食物如红枣、枸杞等",
                "避免过度用眼和思虑"
            ],
            "阴虚": [
                "建议多饮水，保持充足的水分",
                "可适当食用滋阴食物如银耳、百合等",
                "避免熬夜和辛辣刺激食物"
            ],
            "阳虚": [
                "注意保暖，避免受寒",
                "可适当食用温阳食物如羊肉、生姜等",
                "建议进行适度的有氧运动"
            ]
        }
        
        if syndrome in syndrome_recommendations:
            recommendations.extend(syndrome_recommendations[syndrome])
        else:
            recommendations.append("建议到医院进行详细检查")
        
        # 添加通用建议
        recommendations.append("保持良好的作息习惯")
        recommendations.append("如症状持续或加重，请及时就医")
        
        return recommendations
    
    def _calculate_confidence(self, session: InquirySession) -> float:
        """计算置信度"""
        if not session.answers:
            return 0.0
        
        # 考虑多个因素
        factors = []
        
        # 1. 答案的平均置信度
        avg_answer_confidence = np.mean([a.confidence for a in session.answers])
        factors.append(avg_answer_confidence)
        
        # 2. 问题完成率
        completion_rate = len(session.answers) / len(session.questions)
        factors.append(completion_rate)
        
        # 3. 必答问题完成率
        required_questions = [q for q in session.questions if q.required]
        answered_ids = {a.question_id for a in session.answers}
        required_completion = sum(1 for q in required_questions if q.id in answered_ids) / len(required_questions)
        factors.append(required_completion)
        
        # 加权平均
        weights = [0.4, 0.3, 0.3]
        confidence = sum(f * w for f, w in zip(factors, weights))
        
        return min(confidence, 1.0)
    
    async def batch_analyze(self, session_ids: List[str]) -> List[InquiryResult]:
        """
        批量分析问诊结果
        
        Args:
            session_ids: 会话ID列表
            
        Returns:
            问诊结果列表
        """
        if self.enhanced_config['parallel_processing']['enabled']:
            # 并行处理
            tasks = [self.analyze_inquiry(sid) for sid in session_ids]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 过滤掉异常结果
            valid_results = []
            for result in results:
                if isinstance(result, InquiryResult):
                    valid_results.append(result)
                else:
                    logger.error(f"批量分析失败: {result}")
            
            self.stats['batch_processed'] += 1
            return valid_results
        else:
            # 串行处理
            results = []
            for session_id in session_ids:
                try:
                    result = await self.analyze_inquiry(session_id)
                    results.append(result)
                except Exception as e:
                    logger.error(f"分析会话{session_id}失败: {e}")
            
            return results
    
    async def _batch_processor(self):
        """批处理处理器"""
        while True:
            try:
                batch = []
                deadline = time.time() + 0.5  # 500ms收集窗口
                
                # 收集批次
                while len(batch) < self.enhanced_config['parallel_processing']['batch_size']:
                    try:
                        remaining_time = deadline - time.time()
                        if remaining_time <= 0:
                            break
                        
                        request = await asyncio.wait_for(
                            self.batch_queue.get(),
                            timeout=remaining_time
                        )
                        batch.append(request)
                    except asyncio.TimeoutError:
                        break
                
                if batch:
                    # 处理批次
                    session_ids = [req.sessions[0].session_id for req in batch]
                    await self.batch_analyze(session_ids)
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"批处理器错误: {e}")
                await asyncio.sleep(1)
    
    async def _cache_cleaner(self):
        """缓存清理器"""
        while True:
            try:
                current_time = datetime.now()
                expired_keys = []
                
                # 查找过期项
                for key, (value, expire_time) in self.cache.items():
                    if current_time > expire_time:
                        expired_keys.append(key)
                
                # 删除过期项
                for key in expired_keys:
                    del self.cache[key]
                
                if expired_keys:
                    logger.info(f"清理了{len(expired_keys)}个过期缓存项")
                
                # 检查缓存大小
                max_size = self.enhanced_config['caching']['max_cache_size']
                if len(self.cache) > max_size:
                    # 删除最旧的项
                    items = sorted(self.cache.items(), key=lambda x: x[1][1])
                    for key, _ in items[:len(items)//2]:
                        del self.cache[key]
                    logger.info(f"缓存大小超限，清理了{len(items)//2}个项")
                
                await asyncio.sleep(300)  # 5分钟清理一次
                
            except Exception as e:
                logger.error(f"缓存清理器错误: {e}")
                await asyncio.sleep(60)
    
    async def _session_cleaner(self):
        """会话清理器"""
        while True:
            try:
                current_time = datetime.now()
                expired_sessions = []
                
                # 查找过期会话（超过24小时）
                for session_id, session in self.active_sessions.items():
                    if current_time - session.start_time > timedelta(hours=24):
                        expired_sessions.append(session_id)
                
                # 删除过期会话
                for session_id in expired_sessions:
                    del self.active_sessions[session_id]
                
                if expired_sessions:
                    logger.info(f"清理了{len(expired_sessions)}个过期会话")
                
                await asyncio.sleep(3600)  # 每小时清理一次
                
            except Exception as e:
                logger.error(f"会话清理器错误: {e}")
                await asyncio.sleep(300)
    
    async def _get_from_cache(self, key: str) -> Optional[Any]:
        """从缓存获取数据"""
        if not self.enhanced_config['caching']['enabled']:
            return None
        
        if key in self.cache:
            value, expire_time = self.cache[key]
            if datetime.now() < expire_time:
                return value
            else:
                del self.cache[key]
        
        return None
    
    async def _set_to_cache(self, key: str, value: Any, ttl_type: str = "analysis_result"):
        """设置缓存"""
        if not self.enhanced_config['caching']['enabled']:
            return
        
        ttl = self.enhanced_config['caching']['ttl_seconds'].get(ttl_type, 1800)
        expire_time = datetime.now() + timedelta(seconds=ttl)
        self.cache[key] = (value, expire_time)
    
    def _generate_cache_key(self, *args) -> str:
        """生成缓存键"""
        key_data = json.dumps(args, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _update_stats(self, processing_time_ms: float, question_count: int):
        """更新统计信息"""
        # 更新平均处理时间
        alpha = 0.1
        if self.stats['average_processing_time_ms'] == 0:
            self.stats['average_processing_time_ms'] = processing_time_ms
        else:
            self.stats['average_processing_time_ms'] = (
                alpha * processing_time_ms + 
                (1 - alpha) * self.stats['average_processing_time_ms']
            )
        
        # 更新平均问题数
        if self.stats['average_questions_per_session'] == 0:
            self.stats['average_questions_per_session'] = question_count
        else:
            self.stats['average_questions_per_session'] = (
                alpha * question_count + 
                (1 - alpha) * self.stats['average_questions_per_session']
            )
    
    async def get_service_stats(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        cache_hit_rate = (
            self.stats['cache_hits'] / 
            max(1, self.stats['cache_hits'] + self.stats['cache_misses'])
        )
        
        return {
            'total_sessions': self.stats['total_sessions'],
            'completed_sessions': self.stats['completed_sessions'],
            'active_sessions': len(self.active_sessions),
            'cache_hit_rate': cache_hit_rate,
            'average_questions_per_session': self.stats['average_questions_per_session'],
            'average_processing_time_ms': self.stats['average_processing_time_ms'],
            'batch_processed': self.stats['batch_processed'],
            'cache_size': len(self.cache),
            'question_bank_size': sum(len(questions) for questions in self.question_bank.values())
        }
    
    async def close(self):
        """关闭服务"""
        # 停止后台任务
        for task in self.background_tasks:
            task.cancel()
        
        # 等待任务完成
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        logger.info("增强版问诊服务已关闭") 