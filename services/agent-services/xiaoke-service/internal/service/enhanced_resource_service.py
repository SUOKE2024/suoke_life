#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版资源管理服务
集成断路器、限流、追踪、缓存等优化组件
专注于医疗资源调度、产品管理和区块链溯源
"""

import asyncio
import logging
import time
import hashlib
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

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

logger = logging.getLogger(__name__)

class ResourceType(Enum):
    """资源类型"""
    MEDICAL_FACILITY = "medical_facility"
    DOCTOR = "doctor"
    EQUIPMENT = "equipment"
    PRODUCT = "product"

class ConstitutionType(Enum):
    """体质类型"""
    YANG_XU = "阳虚质"
    YIN_XU = "阴虚质"
    QI_XU = "气虚质"
    TAN_SHI = "痰湿质"
    SHI_RE = "湿热质"
    XUE_YU = "血瘀质"
    QI_YU = "气郁质"
    TE_BING = "特禀质"
    PING_HE = "平和质"

@dataclass
class ResourceRequest:
    """资源请求"""
    user_id: str
    resource_type: ResourceType
    constitution_type: ConstitutionType
    location: Optional[Dict[str, float]] = None
    preferences: Optional[Dict[str, Any]] = None
    urgency_level: str = "normal"  # normal, urgent, emergency
    date_range: Optional[Dict[str, str]] = None

@dataclass
class ProductRequest:
    """产品定制请求"""
    user_id: str
    constitution_type: ConstitutionType
    product_category: str
    dietary_restrictions: Optional[List[str]] = None
    budget_range: Optional[Dict[str, float]] = None
    delivery_location: Optional[str] = None

@dataclass
class BlockchainTraceRequest:
    """区块链溯源请求"""
    product_id: str
    trace_level: str = "full"  # basic, detailed, full

@dataclass
class ResourceResult:
    """资源调度结果"""
    request_id: str
    user_id: str
    matched_resources: List[Dict[str, Any]]
    recommendations: List[str]
    booking_options: List[Dict[str, Any]]
    estimated_cost: Optional[float]
    processing_time: float
    timestamp: float

@dataclass
class ProductResult:
    """产品推荐结果"""
    request_id: str
    user_id: str
    recommended_products: List[Dict[str, Any]]
    customization_options: List[Dict[str, Any]]
    nutrition_analysis: Dict[str, Any]
    tcm_benefits: List[str]
    processing_time: float
    timestamp: float

@dataclass
class BlockchainTraceResult:
    """区块链溯源结果"""
    product_id: str
    trace_data: Dict[str, Any]
    verification_status: str
    trust_score: float
    processing_time: float
    timestamp: float

class EnhancedResourceService:
    """增强版资源管理服务"""
    
    def __init__(self):
        self.service_name = "xiaoke-resource"
        self.tracer = get_tracer(self.service_name)
        
        # 初始化断路器配置
        self._init_circuit_breakers()
        
        # 初始化限流器配置
        self._init_rate_limiters()
        
        # 缓存
        self.resource_cache = {}
        self.product_cache = {}
        self.blockchain_cache = {}
        self.cache_ttl = 600  # 10分钟缓存
        
        # 统计信息
        self.stats = {
            'total_requests': 0,
            'resource_requests': 0,
            'product_requests': 0,
            'blockchain_requests': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'average_processing_time': 0.0
        }
        
        logger.info("增强版资源管理服务初始化完成")
    
    def _init_circuit_breakers(self):
        """初始化断路器配置"""
        self.circuit_breaker_configs = {
            'resource_db': CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=60.0,
                timeout=5.0
            ),
            'blockchain_api': CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=120.0,
                timeout=15.0
            ),
            'payment_service': CircuitBreakerConfig(
                failure_threshold=2,
                recovery_timeout=90.0,
                timeout=10.0
            ),
            'recommendation_engine': CircuitBreakerConfig(
                failure_threshold=4,
                recovery_timeout=45.0,
                timeout=8.0
            )
        }
    
    def _init_rate_limiters(self):
        """初始化限流器配置"""
        self.rate_limit_configs = {
            'resource_scheduling': RateLimitConfig(rate=20.0, burst=40),
            'product_recommendation': RateLimitConfig(rate=15.0, burst=30),
            'blockchain_trace': RateLimitConfig(rate=5.0, burst=10),
            'emergency': RateLimitConfig(rate=100.0, burst=200)
        }
    
    @trace(service_name="xiaoke-resource", kind=SpanKind.SERVER)
    async def schedule_resources(self, request: ResourceRequest) -> ResourceResult:
        """
        调度医疗资源
        
        Args:
            request: 资源请求
            
        Returns:
            ResourceResult: 资源调度结果
        """
        start_time = time.time()
        self.stats['total_requests'] += 1
        self.stats['resource_requests'] += 1
        
        try:
            # 根据紧急程度选择限流策略
            limiter_name = 'emergency' if request.urgency_level == 'emergency' else 'resource_scheduling'
            limiter = await get_rate_limiter(
                f"{self.service_name}_{limiter_name}",
                config=self.rate_limit_configs[limiter_name]
            )
            
            if not await limiter.try_acquire():
                raise Exception("资源调度请求频率过高，请稍后重试")
            
            # 检查缓存
            cache_key = self._generate_resource_cache_key(request)
            cached_result = await self._get_from_cache(cache_key, self.resource_cache)
            if cached_result:
                self.stats['cache_hits'] += 1
                return cached_result
            
            self.stats['cache_misses'] += 1
            
            # 执行资源调度
            result = await self._perform_resource_scheduling(request)
            
            # 缓存结果
            await self._cache_result(cache_key, result, self.resource_cache)
            
            # 更新统计
            processing_time = time.time() - start_time
            self.stats['successful_operations'] += 1
            self._update_average_processing_time(processing_time)
            
            return result
            
        except Exception as e:
            self.stats['failed_operations'] += 1
            logger.error(f"资源调度失败: {e}")
            raise
    
    @trace(operation_name="perform_resource_scheduling")
    async def _perform_resource_scheduling(self, request: ResourceRequest) -> ResourceResult:
        """执行实际的资源调度逻辑"""
        request_id = f"res_{int(time.time() * 1000)}"
        
        # 并行执行多个调度步骤
        tasks = []
        
        # 资源匹配
        tasks.append(self._match_resources(request))
        
        # 可用性检查
        tasks.append(self._check_availability(request))
        
        # 成本估算
        tasks.append(self._estimate_cost(request))
        
        # 个性化推荐
        tasks.append(self._generate_recommendations(request))
        
        # 等待所有任务完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 综合结果
        matched_resources = results[0] if not isinstance(results[0], Exception) else []
        availability = results[1] if not isinstance(results[1], Exception) else {}
        cost_estimate = results[2] if not isinstance(results[2], Exception) else None
        recommendations = results[3] if not isinstance(results[3], Exception) else []
        
        # 生成预订选项
        booking_options = await self._generate_booking_options(
            matched_resources, availability, request
        )
        
        return ResourceResult(
            request_id=request_id,
            user_id=request.user_id,
            matched_resources=matched_resources,
            recommendations=recommendations,
            booking_options=booking_options,
            estimated_cost=cost_estimate,
            processing_time=time.time() - time.time(),
            timestamp=time.time()
        )
    
    @trace(operation_name="match_resources")
    async def _match_resources(self, request: ResourceRequest) -> List[Dict[str, Any]]:
        """匹配资源"""
        # 使用断路器保护数据库查询
        breaker = await get_circuit_breaker(
            f"{self.service_name}_resource_db",
            self.circuit_breaker_configs['resource_db']
        )
        
        async with breaker.protect():
            # 模拟数据库查询
            await asyncio.sleep(0.1)
            
            # 根据体质类型和资源类型匹配
            matched_resources = []
            
            if request.resource_type == ResourceType.DOCTOR:
                matched_resources = [
                    {
                        'id': 'doc_001',
                        'name': '张中医',
                        'specialty': '中医内科',
                        'constitution_expertise': [request.constitution_type.value],
                        'rating': 4.8,
                        'location': {'lat': 39.9042, 'lng': 116.4074}
                    },
                    {
                        'id': 'doc_002',
                        'name': '李医师',
                        'specialty': '中医调理',
                        'constitution_expertise': [request.constitution_type.value],
                        'rating': 4.6,
                        'location': {'lat': 39.9142, 'lng': 116.4174}
                    }
                ]
            elif request.resource_type == ResourceType.MEDICAL_FACILITY:
                matched_resources = [
                    {
                        'id': 'facility_001',
                        'name': '索克中医馆',
                        'services': ['体质调理', '针灸', '推拿'],
                        'rating': 4.9,
                        'location': {'lat': 39.9042, 'lng': 116.4074}
                    }
                ]
            
            return matched_resources
    
    @trace(operation_name="recommend_products")
    async def recommend_products(self, request: ProductRequest) -> ProductResult:
        """
        推荐个性化产品
        
        Args:
            request: 产品推荐请求
            
        Returns:
            ProductResult: 产品推荐结果
        """
        start_time = time.time()
        self.stats['total_requests'] += 1
        self.stats['product_requests'] += 1
        
        try:
            # 限流检查
            limiter = await get_rate_limiter(
                f"{self.service_name}_product_recommendation",
                config=self.rate_limit_configs['product_recommendation']
            )
            
            if not await limiter.try_acquire():
                raise Exception("产品推荐请求频率过高，请稍后重试")
            
            # 检查缓存
            cache_key = self._generate_product_cache_key(request)
            cached_result = await self._get_from_cache(cache_key, self.product_cache)
            if cached_result:
                self.stats['cache_hits'] += 1
                return cached_result
            
            self.stats['cache_misses'] += 1
            
            # 执行产品推荐
            result = await self._perform_product_recommendation(request)
            
            # 缓存结果
            await self._cache_result(cache_key, result, self.product_cache)
            
            # 更新统计
            processing_time = time.time() - start_time
            self.stats['successful_operations'] += 1
            self._update_average_processing_time(processing_time)
            
            return result
            
        except Exception as e:
            self.stats['failed_operations'] += 1
            logger.error(f"产品推荐失败: {e}")
            raise
    
    @trace(operation_name="perform_product_recommendation")
    async def _perform_product_recommendation(self, request: ProductRequest) -> ProductResult:
        """执行产品推荐逻辑"""
        request_id = f"prod_{int(time.time() * 1000)}"
        
        # 并行执行推荐任务
        tasks = []
        
        # 基于体质的产品匹配
        tasks.append(self._match_products_by_constitution(request))
        
        # 营养分析
        tasks.append(self._analyze_nutrition(request))
        
        # 中医功效分析
        tasks.append(self._analyze_tcm_benefits(request))
        
        # 个性化定制选项
        tasks.append(self._generate_customization_options(request))
        
        # 等待所有任务完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        recommended_products = results[0] if not isinstance(results[0], Exception) else []
        nutrition_analysis = results[1] if not isinstance(results[1], Exception) else {}
        tcm_benefits = results[2] if not isinstance(results[2], Exception) else []
        customization_options = results[3] if not isinstance(results[3], Exception) else []
        
        return ProductResult(
            request_id=request_id,
            user_id=request.user_id,
            recommended_products=recommended_products,
            customization_options=customization_options,
            nutrition_analysis=nutrition_analysis,
            tcm_benefits=tcm_benefits,
            processing_time=time.time() - time.time(),
            timestamp=time.time()
        )
    
    @trace(operation_name="trace_blockchain")
    @rate_limit(name="blockchain_trace", tokens=1)
    async def trace_blockchain(self, request: BlockchainTraceRequest) -> BlockchainTraceResult:
        """
        区块链产品溯源
        
        Args:
            request: 溯源请求
            
        Returns:
            BlockchainTraceResult: 溯源结果
        """
        start_time = time.time()
        self.stats['total_requests'] += 1
        self.stats['blockchain_requests'] += 1
        
        try:
            # 检查缓存
            cache_key = f"blockchain_{request.product_id}_{request.trace_level}"
            cached_result = await self._get_from_cache(cache_key, self.blockchain_cache)
            if cached_result:
                self.stats['cache_hits'] += 1
                return cached_result
            
            self.stats['cache_misses'] += 1
            
            # 执行区块链溯源
            result = await self._perform_blockchain_trace(request)
            
            # 缓存结果（区块链数据缓存时间更长）
            await self._cache_result(cache_key, result, self.blockchain_cache, ttl=3600)
            
            # 更新统计
            processing_time = time.time() - start_time
            self.stats['successful_operations'] += 1
            self._update_average_processing_time(processing_time)
            
            return result
            
        except Exception as e:
            self.stats['failed_operations'] += 1
            logger.error(f"区块链溯源失败: {e}")
            raise
    
    @trace(operation_name="perform_blockchain_trace")
    async def _perform_blockchain_trace(self, request: BlockchainTraceRequest) -> BlockchainTraceResult:
        """执行区块链溯源"""
        # 使用断路器保护区块链API调用
        breaker = await get_circuit_breaker(
            f"{self.service_name}_blockchain_api",
            self.circuit_breaker_configs['blockchain_api']
        )
        
        async with breaker.protect():
            # 模拟区块链API调用
            await asyncio.sleep(0.3)
            
            # 根据溯源级别返回不同详细程度的数据
            trace_data = {
                'product_id': request.product_id,
                'origin': {
                    'farm_id': 'farm_001',
                    'farm_name': '索克有机农场',
                    'location': '山东省潍坊市',
                    'certification': ['有机认证', '绿色食品']
                },
                'production': {
                    'planting_date': '2024-03-15',
                    'harvest_date': '2024-09-20',
                    'processing_date': '2024-09-22',
                    'quality_checks': ['农残检测', '重金属检测', '营养成分检测']
                },
                'supply_chain': [
                    {
                        'stage': '种植',
                        'timestamp': '2024-03-15T08:00:00Z',
                        'location': '山东省潍坊市',
                        'responsible_party': '索克有机农场'
                    },
                    {
                        'stage': '收获',
                        'timestamp': '2024-09-20T10:00:00Z',
                        'location': '山东省潍坊市',
                        'responsible_party': '索克有机农场'
                    },
                    {
                        'stage': '加工',
                        'timestamp': '2024-09-22T14:00:00Z',
                        'location': '山东省潍坊市加工厂',
                        'responsible_party': '索克食品加工厂'
                    }
                ]
            }
            
            # 计算信任分数
            trust_score = self._calculate_trust_score(trace_data)
            
            return BlockchainTraceResult(
                product_id=request.product_id,
                trace_data=trace_data,
                verification_status='verified',
                trust_score=trust_score,
                processing_time=time.time() - time.time(),
                timestamp=time.time()
            )
    
    def _calculate_trust_score(self, trace_data: Dict[str, Any]) -> float:
        """计算信任分数"""
        score = 0.0
        
        # 基础分数
        score += 0.3
        
        # 认证加分
        if trace_data.get('origin', {}).get('certification'):
            score += 0.2
        
        # 质量检测加分
        if trace_data.get('production', {}).get('quality_checks'):
            score += 0.2
        
        # 供应链完整性加分
        supply_chain = trace_data.get('supply_chain', [])
        if len(supply_chain) >= 3:
            score += 0.3
        
        return min(score, 1.0)
    
    async def _match_products_by_constitution(self, request: ProductRequest) -> List[Dict[str, Any]]:
        """根据体质匹配产品"""
        # 使用推荐引擎断路器
        breaker = await get_circuit_breaker(
            f"{self.service_name}_recommendation_engine",
            self.circuit_breaker_configs['recommendation_engine']
        )
        
        async with breaker.protect():
            await asyncio.sleep(0.1)
            
            # 根据体质类型推荐产品
            constitution_products = {
                ConstitutionType.YANG_XU: [
                    {
                        'id': 'prod_001',
                        'name': '温阳补肾茶',
                        'category': '茶饮',
                        'constitution_match': 0.95,
                        'price': 128.0,
                        'description': '适合阳虚体质，温补肾阳'
                    }
                ],
                ConstitutionType.YIN_XU: [
                    {
                        'id': 'prod_002',
                        'name': '滋阴润燥汤',
                        'category': '汤品',
                        'constitution_match': 0.92,
                        'price': 88.0,
                        'description': '适合阴虚体质，滋阴润燥'
                    }
                ]
            }
            
                         return constitution_products.get(request.constitution_type, [])
    
    async def _check_availability(self, request: ResourceRequest) -> Dict[str, Any]:
        """检查资源可用性"""
        await asyncio.sleep(0.05)
        return {
            'available_slots': [
                {'date': '2024-12-20', 'time': '09:00', 'available': True},
                {'date': '2024-12-20', 'time': '14:00', 'available': True},
                {'date': '2024-12-21', 'time': '10:00', 'available': False}
            ]
        }
    
    async def _estimate_cost(self, request: ResourceRequest) -> float:
        """估算成本"""
        await asyncio.sleep(0.03)
        base_cost = 200.0
        if request.urgency_level == 'emergency':
            base_cost *= 1.5
        elif request.urgency_level == 'urgent':
            base_cost *= 1.2
        return base_cost
    
    async def _generate_recommendations(self, request: ResourceRequest) -> List[str]:
        """生成个性化推荐"""
        await asyncio.sleep(0.05)
        recommendations = [
            f"根据您的{request.constitution_type.value}体质，建议选择温和的调理方案",
            "建议配合适当的运动和饮食调理",
            "定期复查，跟踪调理效果"
        ]
        return recommendations
    
    async def _generate_booking_options(self, resources: List[Dict], availability: Dict, request: ResourceRequest) -> List[Dict[str, Any]]:
        """生成预订选项"""
        await asyncio.sleep(0.02)
        booking_options = []
        
        for resource in resources[:3]:  # 最多3个选项
            booking_options.append({
                'resource_id': resource.get('id'),
                'resource_name': resource.get('name'),
                'available_times': availability.get('available_slots', [])[:2],
                'booking_url': f"/booking/{resource.get('id')}",
                'estimated_duration': '60分钟'
            })
        
        return booking_options
    
    async def _analyze_nutrition(self, request: ProductRequest) -> Dict[str, Any]:
        """营养分析"""
        await asyncio.sleep(0.08)
        return {
            'calories_per_serving': 150,
            'macronutrients': {
                'protein': '8g',
                'carbohydrates': '25g',
                'fat': '3g'
            },
            'vitamins': ['维生素C', '维生素E'],
            'minerals': ['钙', '铁', '锌'],
            'constitution_suitability': 0.9
        }
    
    async def _analyze_tcm_benefits(self, request: ProductRequest) -> List[str]:
        """中医功效分析"""
        await asyncio.sleep(0.06)
        benefits = {
            ConstitutionType.YANG_XU: ["温阳补肾", "强身健体", "改善畏寒"],
            ConstitutionType.YIN_XU: ["滋阴润燥", "清热降火", "改善口干"],
            ConstitutionType.QI_XU: ["补气健脾", "提升精力", "改善乏力"]
        }
        return benefits.get(request.constitution_type, ["调理体质", "增强免疫"])
    
    async def _generate_customization_options(self, request: ProductRequest) -> List[Dict[str, Any]]:
        """生成个性化定制选项"""
        await asyncio.sleep(0.04)
        return [
            {
                'option_id': 'custom_001',
                'name': '口味定制',
                'choices': ['清淡', '微甜', '原味'],
                'price_adjustment': 0
            },
            {
                'option_id': 'custom_002',
                'name': '包装规格',
                'choices': ['小包装(7天)', '标准包装(15天)', '大包装(30天)'],
                'price_adjustment': [0, 20, 50]
            }
        ]
    
    def _generate_cache_key(self, prefix: str, data: Any) -> str:
        """生成缓存键"""
        content = f"{prefix}_{str(data)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _generate_resource_cache_key(self, request: ResourceRequest) -> str:
        """生成资源缓存键"""
        return self._generate_cache_key("resource", request)
    
    def _generate_product_cache_key(self, request: ProductRequest) -> str:
        """生成产品缓存键"""
        return self._generate_cache_key("product", request)
    
    async def _get_from_cache(self, cache_key: str, cache_dict: Dict) -> Optional[Any]:
        """从缓存获取结果"""
        if cache_key in cache_dict:
            cached_data = cache_dict[cache_key]
            
            # 检查缓存是否过期
            if time.time() - cached_data['timestamp'] < self.cache_ttl:
                return cached_data['result']
            else:
                # 清理过期缓存
                del cache_dict[cache_key]
        
        return None
    
    async def _cache_result(self, cache_key: str, result: Any, cache_dict: Dict, ttl: int = None):
        """缓存结果"""
        cache_dict[cache_key] = {
            'result': result,
            'timestamp': time.time()
        }
        
        # 简单的缓存清理策略
        if len(cache_dict) > 1000:
            oldest_key = min(
                cache_dict.keys(),
                key=lambda k: cache_dict[k]['timestamp']
            )
            del cache_dict[oldest_key]
    
    def _update_average_processing_time(self, processing_time: float):
        """更新平均处理时间"""
        total_successful = self.stats['successful_operations']
        if total_successful == 1:
            self.stats['average_processing_time'] = processing_time
        else:
            current_avg = self.stats['average_processing_time']
            self.stats['average_processing_time'] = (
                (current_avg * (total_successful - 1) + processing_time) / total_successful
            )
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取服务健康状态"""
        return {
            'service': self.service_name,
            'status': 'healthy',
            'stats': self.stats,
            'cache_sizes': {
                'resource_cache': len(self.resource_cache),
                'product_cache': len(self.product_cache),
                'blockchain_cache': len(self.blockchain_cache)
            },
            'uptime': time.time()
        }
    
    async def cleanup(self):
        """清理资源"""
        self.resource_cache.clear()
        self.product_cache.clear()
        self.blockchain_cache.clear()
        logger.info("资源管理服务清理完成")

# 全局服务实例
_resource_service = None

async def get_resource_service() -> EnhancedResourceService:
    """获取资源管理服务实例"""
    global _resource_service
    if _resource_service is None:
        _resource_service = EnhancedResourceService()
    return _resource_service 