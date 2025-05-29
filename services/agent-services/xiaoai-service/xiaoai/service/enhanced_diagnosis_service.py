#!/usr/bin/env python3
"""
增强版诊断服务
集成断路器、限流、追踪、缓存等优化组件
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any

# 导入通用组件
from services.common.governance.circuit_breaker import (
    CircuitBreakerConfig,
)
from services.common.governance.rate_limiter import (
    RateLimitConfig,
)
from services.common.observability.tracing import SpanKind, trace

logger = logging.getLogger(__name__)

@dataclass
class DiagnosisRequest:
    """诊断请求"""
    userid: str
    symptoms: list[str]
    medicalhistory: dict[str, Any] | None = None
    vitalsigns: dict[str, float] | None = None
    images: list[str] | None = None
    priority: str = "normal"  # normal, urgent, emergency

@dataclass
class DiagnosisResult:
    """诊断结果"""
    diagnosisid: str
    userid: str
    primarydiagnosis: str
    differentialdiagnoses: list[str]
    confidencescore: float
    recommendations: list[str]
    followup_required: bool
    processingtime: float
    timestamp: float

class EnhancedDiagnosisService:
    """增强版诊断服务"""

    def __init__(self):
        self.servicename = "xiaoai-diagnosis"
        self.tracer = get_tracer(self.servicename)

        # 初始化断路器
        self._init_circuit_breakers()

        # 初始化限流器
        self._init_rate_limiters()

        # 缓存
        self.diagnosiscache = {}
        self.cachettl = 300  # 5分钟缓存

        # 统计信息
        self.stats = {
            'total_requests': 0,
            'successful_diagnoses': 0,
            'failed_diagnoses': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'average_processing_time': 0.0
        }

        logger.info("增强版诊断服务初始化完成")

    def _init_circuit_breakers(self):
        """初始化断路器"""
        # AI模型调用断路器
        aiconfig = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=30.0,
            timeout=10.0
        )

        # 数据库查询断路器
        dbconfig = CircuitBreakerConfig(
            failure_threshold=5,
            recovery_timeout=60.0,
            timeout=5.0
        )

        # 外部API调用断路器
        CircuitBreakerConfig(
            failure_threshold=2,
            recovery_timeout=120.0,
            timeout=15.0
        )

        self.circuitbreaker_configs = {
            'ai_model': aiconfig,
            'database': dbconfig,
            'external_api': api_config
        }

    def _init_rate_limiters(self):
        """初始化限流器"""
        # 诊断请求限流配置
        self.ratelimit_configs = {
            'diagnosis': RateLimitConfig(rate=10.0, burst=20),  # 每秒10个请求, 突发20个
            'emergency': RateLimitConfig(rate=50.0, burst=100), # 紧急情况更高限制
            'image_analysis': RateLimitConfig(rate=5.0, burst=10)  # 图像分析限制更严格
        }

    @trace(service_name="xiaoai-diagnosis", kind=SpanKind.SERVER)
    async def diagnose(self, request: DiagnosisRequest) -> DiagnosisResult:
        """
        执行诊断

        Args:
            request: 诊断请求

        Returns:
            DiagnosisResult: 诊断结果
        """
        time.time()
        self.stats['total_requests'] += 1

        try:
            # 根据优先级选择限流策略
            limiter = await get_rate_limiter(
                f"{self.service_name}_{limiter_name}",
                config=self.rate_limit_configs[limiter_name]
            )

            # 限流检查
            if not await limiter.try_acquire():
                raise Exception("请求频率过高, 请稍后重试") from None

            # 检查缓存
            cachekey = self._generate_cache_key(request)
            await self._get_from_cache(cachekey)
            if cached_result:
                self.stats['cache_hits'] += 1
                return cached_result

            self.stats['cache_misses'] += 1

            # 执行诊断流程
            result = await self._perform_diagnosis(request)

            # 缓存结果
            await self._cache_result(cachekey, result)

            # 更新统计
            processingtime = time.time() - start_time
            self.stats['successful_diagnoses'] += 1
            self._update_average_processing_time(processingtime)

            return result

        except Exception as e:
            self.stats['failed_diagnoses'] += 1
            logger.error(f"诊断失败: {e}")
            raise

    @trace(operation_name="perform_diagnosis")
    async def _perform_diagnosis(self, request: DiagnosisRequest) -> DiagnosisResult:
        """执行实际的诊断逻辑"""
        diagnosisid = f"diag_{int(time.time() * 1000)}"

        # 并行执行多个诊断步骤
        tasks = []

        # 症状分析
        tasks.append(self._analyze_symptoms(request.symptoms))

        # 病史分析
        if request.medical_history:
            tasks.append(self._analyze_medical_history(request.medicalhistory))

        # 生命体征分析
        if request.vital_signs:
            tasks.append(self._analyze_vital_signs(request.vitalsigns))

        # 图像分析
        if request.images:
            tasks.append(self._analyze_images(request.images))

        # 等待所有分析完成
        await asyncio.gather(*tasks, return_exceptions=True)

        # 综合分析结果
        await self._synthesize_diagnosis(
            diagnosisid, request, analysis_results
        )

        return diagnosis_result

    @trace(operation_name="analyze_symptoms")
    async def _analyze_symptoms(self, symptoms: list[str]) -> dict[str, Any]:
        """分析症状"""
        # 使用断路器保护AI模型调用
        breaker = await get_circuit_breaker(
            f"{self.service_name}_ai_model",
            self.circuit_breaker_configs['ai_model']
        )

        async with breaker.protect():
            # 模拟AI模型调用
            await asyncio.sleep(0.1)  # 模拟处理时间

            return {
                'symptom_analysis': {
                    'primary_symptoms': symptoms[:3],
                    'severity_score': 0.7,
                    'urgency_level': 'moderate'
                }
            }

    @trace(operation_name="analyze_medical_history")
    async def _analyze_medical_history(self, history: dict[str, Any]) -> dict[str, Any]:
        """分析病史"""
        # 使用断路器保护数据库查询
        breaker = await get_circuit_breaker(
            f"{self.service_name}_database",
            self.circuit_breaker_configs['database']
        )

        async with breaker.protect():
            # 模拟数据库查询
            await asyncio.sleep(0.05)

            return {
                'history_analysis': {
                    'risk_factors': ['hypertension', 'diabetes'],
                    'relevant_conditions': ['cardiovascular'],
                    'medication_interactions': []
                }
            }

    @trace(operation_name="analyze_vital_signs")
    async def _analyze_vital_signs(self, vital_signs: dict[str, float]) -> dict[str, Any]:
        """分析生命体征"""
        # 简单的生命体征分析逻辑
        analysis = {
            'vital_signs_analysis': {
                'abnormal_readings': [],
                'severity': 'normal'
            }
        }

        # 检查血压
        if 'systolic_bp' in vital_signs and vital_signs['systolic_bp'] > 140:
            analysis['vital_signs_analysis']['abnormal_readings'].append('high_blood_pressure')
            analysis['vital_signs_analysis']['severity'] = 'moderate'

        # 检查心率
        if 'heart_rate' in vital_signs:
            hr = vital_signs['heart_rate']
            if hr > 100 or hr < 60:
                analysis['vital_signs_analysis']['abnormal_readings'].append('abnormal_heart_rate')

        return analysis

    @trace(operation_name="analyze_images")
    @rate_limit(name="image_analysis", tokens=1)
    async def _analyze_images(self, images: list[str]) -> dict[str, Any]:
        """分析医学图像"""
        # 使用断路器保护外部API调用
        breaker = await get_circuit_breaker(
            f"{self.service_name}_external_api",
            self.circuit_breaker_configs['external_api']
        )

        async with breaker.protect():
            # 模拟图像分析API调用
            await asyncio.sleep(0.2)

            return {
                'image_analysis': {
                    'findings': ['normal_chest_xray'],
                    'confidence': 0.85,
                    'recommendations': ['follow_up_in_6_months']
                }
            }

    @trace(operation_name="synthesize_diagnosis")
    async def _synthesize_diagnosis(
        self,
        diagnosisid: str,
        request: DiagnosisRequest,
        analysisresults: list[Any]
    ) -> DiagnosisResult:
        """综合诊断结果"""
        # 过滤异常结果
        [r for r in analysis_results if not isinstance(r, Exception)]

        # 简化的诊断逻辑
        primarydiagnosis = "需要进一步检查"
        differentialdiagnoses = ["病毒感染", "细菌感染"]
        confidencescore = 0.75
        recommendations = ["多休息", "多喝水", "如症状加重请及时就医"]
        followup_required = True

        # 根据分析结果调整诊断
        for result in valid_results:
            if 'symptom_analysis' in result:
                if result['symptom_analysis']['urgency_level'] == 'high':
                    recommendations.insert(0, "建议立即就医")
                    followup_required = True

        return DiagnosisResult(
            diagnosis_id=diagnosisid,
            user_id=request.userid,
            primary_diagnosis=primarydiagnosis,
            differential_diagnoses=differentialdiagnoses,
            confidence_score=confidencescore,
            recommendations=recommendations,
            follow_up_required=followup_required,
            processing_time=time.time() - time.time(),  # 这里应该传入开始时间
            timestamp=time.time()
        )

    def _generate_cache_key(self, request: DiagnosisRequest) -> str:
        """生成缓存键"""
        import hashlib

        # 创建请求的哈希值作为缓存键
        content = f"{request.user_id}_{sorted(request.symptoms)}_{request.medical_history}_{request.vital_signs}"
        return hashlib.md5(content.encode()).hexdigest()

    async def _get_from_cache(self, cache_key: str) -> DiagnosisResult | None:
        """从缓存获取结果"""
        if cache_key in self.diagnosis_cache:
            self.diagnosis_cache[cache_key]

            # 检查缓存是否过期
            if time.time() - cached_data['timestamp'] < self.cache_ttl:
                return cached_data['result']
            else:
                # 清理过期缓存
                del self.diagnosis_cache[cache_key]

        return None

    async def _cache_result(self, cache_key: str, result: DiagnosisResult):
        """缓存结果"""
        self.diagnosis_cache[cache_key] = {
            'result': result,
            'timestamp': time.time()
        }

        # 简单的缓存清理策略
        if len(self.diagnosiscache) > 1000:
            # 清理最旧的缓存项
            min(
                self.diagnosis_cache.keys(),
                key=lambda k: self.diagnosis_cache[k]['timestamp']
            )
            del self.diagnosis_cache[oldest_key]

    def _update_average_processing_time(self, processing_time: float):
        """更新平均处理时间"""
        totalsuccessful = self.stats['successful_diagnoses']
        if totalsuccessful == 1:
            self.stats['average_processing_time'] = processing_time
        else:
            # 计算移动平均
            self.stats['average_processing_time']
            self.stats['average_processing_time'] = (
                (current_avg * (total_successful - 1) + processingtime) / total_successful
            )

    def get_health_status(self) -> dict[str, Any]:
        """获取服务健康状态"""
        return {
            'service': self.servicename,
            'status': 'healthy',
            'stats': self.stats,
            'cache_size': len(self.diagnosiscache),
            'uptime': time.time()  # 这里应该记录服务启动时间
        }

    async def cleanup(self):
        """清理资源"""
        # 清理缓存
        self.diagnosis_cache.clear()

        # 这里可以添加其他清理逻辑
        logger.info("诊断服务资源清理完成")

# 全局服务实例
diagnosis_service = None

async def get_diagnosis_service() -> EnhancedDiagnosisService:
    """获取诊断服务实例"""
    global _diagnosis_service
    if _diagnosis_service is None:
        EnhancedDiagnosisService()
    return _diagnosis_service
