#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强版医疗资源服务

该模块是医疗资源服务的增强版本，集成了智能匹配算法、资源调度优化、并行处理和智能缓存功能，
提供高效的医疗资源管理和调度服务。
"""

import asyncio
import time
import uuid
import hashlib
import json
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import numpy as np
from loguru import logger
import heapq
from geopy.distance import geodesic

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

class ResourceType(Enum):
    """资源类型"""
    DOCTOR = "doctor"
    HOSPITAL = "hospital"
    EQUIPMENT = "equipment"
    MEDICINE = "medicine"
    BED = "bed"
    ROOM = "room"

class SpecialtyType(Enum):
    """专科类型"""
    TCM = "tcm"  # 中医
    INTERNAL = "internal"  # 内科
    SURGERY = "surgery"  # 外科
    PEDIATRICS = "pediatrics"  # 儿科
    GYNECOLOGY = "gynecology"  # 妇科
    CARDIOLOGY = "cardiology"  # 心血管科
    NEUROLOGY = "neurology"  # 神经科
    ORTHOPEDICS = "orthopedics"  # 骨科

class ResourceStatus(Enum):
    """资源状态"""
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"

class Priority(Enum):
    """优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    EMERGENCY = 5

@dataclass
class Location:
    """地理位置"""
    latitude: float
    longitude: float
    address: str = ""
    city: str = ""
    district: str = ""

@dataclass
class TimeSlot:
    """时间段"""
    start_time: datetime
    end_time: datetime
    available: bool = True

@dataclass
class Doctor:
    """医生资源"""
    doctor_id: str
    name: str
    specialty: SpecialtyType
    hospital_id: str
    location: Location
    rating: float = 0.0
    experience_years: int = 0
    consultation_fee: float = 0.0
    available_slots: List[TimeSlot] = field(default_factory=list)
    status: ResourceStatus = ResourceStatus.AVAILABLE
    skills: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)

@dataclass
class Hospital:
    """医院资源"""
    hospital_id: str
    name: str
    location: Location
    level: str = ""  # 医院等级
    departments: List[str] = field(default_factory=list)
    bed_count: int = 0
    available_beds: int = 0
    rating: float = 0.0
    contact_info: Dict[str, str] = field(default_factory=dict)

@dataclass
class Equipment:
    """设备资源"""
    equipment_id: str
    name: str
    type: str
    hospital_id: str
    location: Location
    status: ResourceStatus = ResourceStatus.AVAILABLE
    maintenance_schedule: List[TimeSlot] = field(default_factory=list)
    booking_slots: List[TimeSlot] = field(default_factory=list)

@dataclass
class Medicine:
    """药品资源"""
    medicine_id: str
    name: str
    type: str
    manufacturer: str
    stock_quantity: int = 0
    unit_price: float = 0.0
    expiry_date: datetime = field(default_factory=datetime.now)
    pharmacy_locations: List[str] = field(default_factory=list)

@dataclass
class ResourceRequest:
    """资源请求"""
    request_id: str
    patient_id: str
    resource_type: ResourceType
    specialty: Optional[SpecialtyType] = None
    location: Optional[Location] = None
    preferred_time: Optional[datetime] = None
    symptoms: List[str] = field(default_factory=list)
    budget_range: Optional[Tuple[float, float]] = None
    priority: Priority = Priority.NORMAL
    requirements: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ResourceMatch:
    """资源匹配结果"""
    resource_id: str
    resource_type: ResourceType
    match_score: float
    distance_km: float = 0.0
    estimated_cost: float = 0.0
    available_time: Optional[datetime] = None
    confidence: float = 1.0
    reasons: List[str] = field(default_factory=list)

@dataclass
class ResourceAllocation:
    """资源分配结果"""
    request_id: str
    patient_id: str
    matches: List[ResourceMatch]
    total_score: float
    processing_time_ms: float
    recommendations: List[str]

@dataclass
class BatchResourceRequest:
    """批量资源请求"""
    batch_id: str
    requests: List[ResourceRequest]
    priority: Priority = Priority.NORMAL
    created_at: datetime = field(default_factory=datetime.now)

class EnhancedMedicalResourceService:
    """增强版医疗资源服务"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化增强版医疗资源服务
        
        Args:
            config: 配置信息
        """
        self.config = config
        
        # 增强配置
        self.enhanced_config = {
            'matching': {
                'max_distance_km': 50,  # 最大搜索距离
                'max_results': 10,  # 最大返回结果数
                'score_weights': {
                    'specialty_match': 0.3,
                    'distance': 0.2,
                    'rating': 0.2,
                    'availability': 0.15,
                    'cost': 0.15
                },
                'time_window_hours': 24  # 时间窗口
            },
            'parallel_processing': {
                'enabled': True,
                'max_workers': 6,
                'batch_size': 20
            },
            'caching': {
                'enabled': True,
                'ttl_seconds': {
                    'resource_data': 1800,
                    'match_results': 900,
                    'availability': 300
                },
                'max_cache_size': 5000
            },
            'scheduling': {
                'load_balancing': True,
                'priority_queue': True,
                'conflict_resolution': True,
                'resource_reservation_minutes': 15
            }
        }
        
        # 资源存储
        self.doctors: Dict[str, Doctor] = {}
        self.hospitals: Dict[str, Hospital] = {}
        self.equipment: Dict[str, Equipment] = {}
        self.medicines: Dict[str, Medicine] = {}
        
        # 索引
        self.specialty_index: Dict[SpecialtyType, Set[str]] = defaultdict(set)
        self.location_index: Dict[str, Set[str]] = defaultdict(set)  # 按城市索引
        
        # 调度队列
        self.priority_queue: List[Tuple[int, ResourceRequest]] = []
        self.batch_queue: asyncio.Queue = asyncio.Queue()
        
        # 缓存
        self.cache: Dict[str, Tuple[Any, datetime]] = {}
        
        # 性能统计
        self.stats = {
            'total_requests': 0,
            'successful_matches': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'average_processing_time_ms': 0.0,
            'average_match_score': 0.0,
            'resource_utilization': defaultdict(float),
            'batch_processed': 0
        }
        
        # 断路器配置
        self.circuit_breaker_configs = {
            'resource_matching': CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=30.0,
                timeout=10.0
            ),
            'scheduling': CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=20.0,
                timeout=5.0
            )
        }
        
        # 限流配置
        self.rate_limit_configs = {
            'matching': RateLimitConfig(rate=100.0, burst=200),
            'batch': RateLimitConfig(rate=20.0, burst=40)
        }
        
        # 后台任务
        self.background_tasks: List[asyncio.Task] = []
        
        # 初始化示例数据
        self._initialize_sample_data()
        
        logger.info("增强版医疗资源服务初始化完成")
    
    def _initialize_sample_data(self):
        """初始化示例数据"""
        # 示例医院
        hospital1 = Hospital(
            hospital_id="h001",
            name="北京中医医院",
            location=Location(39.9042, 116.4074, "北京市东城区", "北京", "东城区"),
            level="三甲",
            departments=["中医内科", "中医外科", "针灸科", "推拿科"],
            bed_count=500,
            available_beds=50,
            rating=4.5
        )
        self.hospitals[hospital1.hospital_id] = hospital1
        
        # 示例医生
        doctor1 = Doctor(
            doctor_id="d001",
            name="张医生",
            specialty=SpecialtyType.TCM,
            hospital_id="h001",
            location=hospital1.location,
            rating=4.8,
            experience_years=15,
            consultation_fee=200.0,
            skills=["脉诊", "针灸", "中药调理"],
            languages=["中文", "英文"]
        )
        
        # 添加可用时间段
        now = datetime.now()
        for i in range(7):  # 未来7天
            date = now + timedelta(days=i)
            # 上午时段
            morning_start = date.replace(hour=9, minute=0, second=0, microsecond=0)
            morning_end = date.replace(hour=12, minute=0, second=0, microsecond=0)
            doctor1.available_slots.append(TimeSlot(morning_start, morning_end))
            
            # 下午时段
            afternoon_start = date.replace(hour=14, minute=0, second=0, microsecond=0)
            afternoon_end = date.replace(hour=17, minute=0, second=0, microsecond=0)
            doctor1.available_slots.append(TimeSlot(afternoon_start, afternoon_end))
        
        self.doctors[doctor1.doctor_id] = doctor1
        self.specialty_index[SpecialtyType.TCM].add(doctor1.doctor_id)
        self.location_index["北京"].add(doctor1.doctor_id)
    
    async def initialize(self):
        """初始化服务"""
        # 启动后台任务
        self._start_background_tasks()
        logger.info("医疗资源服务初始化完成")
    
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
        
        # 资源状态更新器
        self.background_tasks.append(
            asyncio.create_task(self._resource_status_updater())
        )
        
        # 调度器
        self.background_tasks.append(
            asyncio.create_task(self._scheduler())
        )
    
    @trace(service_name="medical-resource-service", kind=SpanKind.SERVER)
    @rate_limit(name="matching", tokens=1)
    async def find_resources(
        self,
        patient_id: str,
        resource_type: ResourceType,
        specialty: Optional[SpecialtyType] = None,
        location: Optional[Location] = None,
        preferred_time: Optional[datetime] = None,
        symptoms: Optional[List[str]] = None,
        budget_range: Optional[Tuple[float, float]] = None,
        priority: Priority = Priority.NORMAL,
        requirements: Optional[Dict[str, Any]] = None
    ) -> ResourceAllocation:
        """
        查找医疗资源
        
        Args:
            patient_id: 患者ID
            resource_type: 资源类型
            specialty: 专科类型
            location: 患者位置
            preferred_time: 偏好时间
            symptoms: 症状列表
            budget_range: 预算范围
            priority: 优先级
            requirements: 其他要求
            
        Returns:
            资源分配结果
        """
        start_time = time.time()
        request_id = str(uuid.uuid4())
        self.stats['total_requests'] += 1
        
        # 创建资源请求
        request = ResourceRequest(
            request_id=request_id,
            patient_id=patient_id,
            resource_type=resource_type,
            specialty=specialty,
            location=location,
            preferred_time=preferred_time,
            symptoms=symptoms or [],
            budget_range=budget_range,
            priority=priority,
            requirements=requirements or {}
        )
        
        # 检查缓存
        cache_key = self._generate_cache_key(
            "matching", resource_type.value, specialty.value if specialty else "",
            str(location), str(preferred_time), str(symptoms)
        )
        cached_result = await self._get_from_cache(cache_key)
        if cached_result:
            self.stats['cache_hits'] += 1
            return cached_result
        
        self.stats['cache_misses'] += 1
        
        try:
            # 并行匹配不同类型的资源
            if self.enhanced_config['parallel_processing']['enabled']:
                matches = await self._parallel_resource_matching(request)
            else:
                matches = await self._match_resources(request)
            
            # 排序和过滤结果
            sorted_matches = await self._rank_matches(matches, request)
            
            # 生成建议
            recommendations = await self._generate_resource_recommendations(
                sorted_matches, request
            )
            
            processing_time_ms = (time.time() - start_time) * 1000
            
            # 计算总分
            total_score = np.mean([m.match_score for m in sorted_matches]) if sorted_matches else 0.0
            
            result = ResourceAllocation(
                request_id=request_id,
                patient_id=patient_id,
                matches=sorted_matches,
                total_score=total_score,
                processing_time_ms=processing_time_ms,
                recommendations=recommendations
            )
            
            # 缓存结果
            await self._set_to_cache(cache_key, result)
            
            # 更新统计
            if sorted_matches:
                self.stats['successful_matches'] += 1
                self.stats['average_match_score'] = (
                    self.stats['average_match_score'] * 0.9 + total_score * 0.1
                )
            
            self._update_stats(processing_time_ms)
            
            return result
            
        except Exception as e:
            logger.error(f"资源匹配失败: {e}")
            raise
    
    async def _parallel_resource_matching(
        self,
        request: ResourceRequest
    ) -> List[ResourceMatch]:
        """并行资源匹配"""
        tasks = []
        
        if request.resource_type == ResourceType.DOCTOR:
            tasks.append(self._match_doctors(request))
        elif request.resource_type == ResourceType.HOSPITAL:
            tasks.append(self._match_hospitals(request))
        elif request.resource_type == ResourceType.EQUIPMENT:
            tasks.append(self._match_equipment(request))
        elif request.resource_type == ResourceType.MEDICINE:
            tasks.append(self._match_medicines(request))
        else:
            # 匹配所有类型
            tasks.extend([
                self._match_doctors(request),
                self._match_hospitals(request),
                self._match_equipment(request),
                self._match_medicines(request)
            ])
        
        # 并行执行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 收集有效结果
        matches = []
        for result in results:
            if isinstance(result, list):
                matches.extend(result)
            else:
                logger.error(f"资源匹配失败: {result}")
        
        return matches
    
    async def _match_resources(self, request: ResourceRequest) -> List[ResourceMatch]:
        """匹配资源"""
        matches = []
        
        if request.resource_type == ResourceType.DOCTOR:
            matches.extend(await self._match_doctors(request))
        elif request.resource_type == ResourceType.HOSPITAL:
            matches.extend(await self._match_hospitals(request))
        elif request.resource_type == ResourceType.EQUIPMENT:
            matches.extend(await self._match_equipment(request))
        elif request.resource_type == ResourceType.MEDICINE:
            matches.extend(await self._match_medicines(request))
        
        return matches
    
    async def _match_doctors(self, request: ResourceRequest) -> List[ResourceMatch]:
        """匹配医生资源"""
        matches = []
        
        # 获取候选医生
        candidates = set()
        
        # 按专科筛选
        if request.specialty:
            candidates.update(self.specialty_index.get(request.specialty, set()))
        else:
            candidates.update(self.doctors.keys())
        
        # 按位置筛选
        if request.location:
            city_candidates = self.location_index.get(request.location.city, set())
            if candidates:
                candidates &= city_candidates
            else:
                candidates = city_candidates
        
        # 评估每个候选医生
        for doctor_id in candidates:
            doctor = self.doctors.get(doctor_id)
            if not doctor or doctor.status != ResourceStatus.AVAILABLE:
                continue
            
            match = await self._evaluate_doctor_match(doctor, request)
            if match.match_score > 0.3:  # 最低匹配阈值
                matches.append(match)
        
        return matches
    
    async def _evaluate_doctor_match(
        self,
        doctor: Doctor,
        request: ResourceRequest
    ) -> ResourceMatch:
        """评估医生匹配度"""
        scores = {}
        reasons = []
        
        # 专科匹配度
        if request.specialty:
            if doctor.specialty == request.specialty:
                scores['specialty_match'] = 1.0
                reasons.append(f"专科匹配: {doctor.specialty.value}")
            else:
                scores['specialty_match'] = 0.3
        else:
            scores['specialty_match'] = 0.8
        
        # 距离评分
        if request.location:
            distance = geodesic(
                (request.location.latitude, request.location.longitude),
                (doctor.location.latitude, doctor.location.longitude)
            ).kilometers
            
            max_distance = self.enhanced_config['matching']['max_distance_km']
            if distance <= max_distance:
                scores['distance'] = max(0, 1.0 - distance / max_distance)
                reasons.append(f"距离: {distance:.1f}km")
            else:
                scores['distance'] = 0.0
        else:
            scores['distance'] = 0.8
            distance = 0.0
        
        # 评分
        scores['rating'] = doctor.rating / 5.0
        if doctor.rating >= 4.0:
            reasons.append(f"高评分: {doctor.rating}")
        
        # 可用性
        availability_score = await self._check_doctor_availability(
            doctor, request.preferred_time
        )
        scores['availability'] = availability_score
        if availability_score > 0.8:
            reasons.append("时间可用")
        
        # 费用评分
        if request.budget_range:
            min_budget, max_budget = request.budget_range
            if min_budget <= doctor.consultation_fee <= max_budget:
                scores['cost'] = 1.0
                reasons.append("费用合适")
            elif doctor.consultation_fee < min_budget:
                scores['cost'] = 0.8
            else:
                scores['cost'] = max(0, 1.0 - (doctor.consultation_fee - max_budget) / max_budget)
        else:
            scores['cost'] = 0.8
        
        # 技能匹配
        if request.symptoms:
            skill_match = await self._match_symptoms_to_skills(
                request.symptoms, doctor.skills
            )
            scores['specialty_match'] *= (0.7 + 0.3 * skill_match)
            if skill_match > 0.5:
                reasons.append("技能匹配")
        
        # 计算综合评分
        weights = self.enhanced_config['matching']['score_weights']
        match_score = sum(scores[key] * weights[key] for key in scores if key in weights)
        
        # 获取最近可用时间
        available_time = await self._get_next_available_time(doctor, request.preferred_time)
        
        return ResourceMatch(
            resource_id=doctor.doctor_id,
            resource_type=ResourceType.DOCTOR,
            match_score=match_score,
            distance_km=distance,
            estimated_cost=doctor.consultation_fee,
            available_time=available_time,
            confidence=min(match_score + 0.2, 1.0),
            reasons=reasons
        )
    
    async def _check_doctor_availability(
        self,
        doctor: Doctor,
        preferred_time: Optional[datetime]
    ) -> float:
        """检查医生可用性"""
        if not preferred_time:
            # 如果没有偏好时间，检查未来24小时内的可用性
            now = datetime.now()
            end_time = now + timedelta(hours=24)
            
            for slot in doctor.available_slots:
                if slot.available and slot.start_time >= now and slot.start_time <= end_time:
                    return 1.0
            return 0.3
        
        # 检查偏好时间附近的可用性
        time_window = timedelta(hours=self.enhanced_config['matching']['time_window_hours'])
        start_window = preferred_time - time_window
        end_window = preferred_time + time_window
        
        best_score = 0.0
        for slot in doctor.available_slots:
            if not slot.available:
                continue
            
            # 计算时间匹配度
            if slot.start_time <= preferred_time <= slot.end_time:
                return 1.0  # 完全匹配
            
            # 计算时间差
            if slot.end_time < start_window or slot.start_time > end_window:
                continue
            
            time_diff = min(
                abs((slot.start_time - preferred_time).total_seconds()),
                abs((slot.end_time - preferred_time).total_seconds())
            )
            
            score = max(0, 1.0 - time_diff / (24 * 3600))  # 24小时内线性衰减
            best_score = max(best_score, score)
        
        return best_score
    
    async def _match_symptoms_to_skills(
        self,
        symptoms: List[str],
        skills: List[str]
    ) -> float:
        """匹配症状与技能"""
        if not symptoms or not skills:
            return 0.5
        
        # 简化实现：基于关键词匹配
        symptom_keywords = set()
        for symptom in symptoms:
            symptom_keywords.update(symptom.lower().split())
        
        skill_keywords = set()
        for skill in skills:
            skill_keywords.update(skill.lower().split())
        
        # 计算交集比例
        intersection = symptom_keywords & skill_keywords
        union = symptom_keywords | skill_keywords
        
        if not union:
            return 0.5
        
        return len(intersection) / len(union)
    
    async def _get_next_available_time(
        self,
        doctor: Doctor,
        preferred_time: Optional[datetime]
    ) -> Optional[datetime]:
        """获取下一个可用时间"""
        now = datetime.now()
        start_time = preferred_time or now
        
        for slot in sorted(doctor.available_slots, key=lambda s: s.start_time):
            if slot.available and slot.start_time >= start_time:
                return slot.start_time
        
        return None
    
    async def _match_hospitals(self, request: ResourceRequest) -> List[ResourceMatch]:
        """匹配医院资源"""
        matches = []
        
        for hospital in self.hospitals.values():
            match = await self._evaluate_hospital_match(hospital, request)
            if match.match_score > 0.3:
                matches.append(match)
        
        return matches
    
    async def _evaluate_hospital_match(
        self,
        hospital: Hospital,
        request: ResourceRequest
    ) -> ResourceMatch:
        """评估医院匹配度"""
        scores = {}
        reasons = []
        
        # 科室匹配
        if request.specialty:
            specialty_name = self._specialty_to_department(request.specialty)
            if specialty_name in hospital.departments:
                scores['specialty_match'] = 1.0
                reasons.append(f"科室匹配: {specialty_name}")
            else:
                scores['specialty_match'] = 0.2
        else:
            scores['specialty_match'] = 0.8
        
        # 距离评分
        if request.location:
            distance = geodesic(
                (request.location.latitude, request.location.longitude),
                (hospital.location.latitude, hospital.location.longitude)
            ).kilometers
            
            max_distance = self.enhanced_config['matching']['max_distance_km']
            scores['distance'] = max(0, 1.0 - distance / max_distance)
            reasons.append(f"距离: {distance:.1f}km")
        else:
            scores['distance'] = 0.8
            distance = 0.0
        
        # 医院评分
        scores['rating'] = hospital.rating / 5.0
        if hospital.rating >= 4.0:
            reasons.append(f"高评分: {hospital.rating}")
        
        # 床位可用性
        if hospital.available_beds > 0:
            bed_ratio = hospital.available_beds / hospital.bed_count
            scores['availability'] = min(bed_ratio * 2, 1.0)
            reasons.append(f"床位可用: {hospital.available_beds}")
        else:
            scores['availability'] = 0.1
        
        # 费用评分（简化）
        scores['cost'] = 0.8
        
        # 计算综合评分
        weights = self.enhanced_config['matching']['score_weights']
        match_score = sum(scores[key] * weights[key] for key in scores if key in weights)
        
        return ResourceMatch(
            resource_id=hospital.hospital_id,
            resource_type=ResourceType.HOSPITAL,
            match_score=match_score,
            distance_km=distance,
            estimated_cost=0.0,
            available_time=datetime.now(),
            confidence=min(match_score + 0.1, 1.0),
            reasons=reasons
        )
    
    def _specialty_to_department(self, specialty: SpecialtyType) -> str:
        """专科类型转换为科室名称"""
        mapping = {
            SpecialtyType.TCM: "中医科",
            SpecialtyType.INTERNAL: "内科",
            SpecialtyType.SURGERY: "外科",
            SpecialtyType.PEDIATRICS: "儿科",
            SpecialtyType.GYNECOLOGY: "妇科",
            SpecialtyType.CARDIOLOGY: "心血管科",
            SpecialtyType.NEUROLOGY: "神经科",
            SpecialtyType.ORTHOPEDICS: "骨科"
        }
        return mapping.get(specialty, "综合科")
    
    async def _match_equipment(self, request: ResourceRequest) -> List[ResourceMatch]:
        """匹配设备资源"""
        matches = []
        
        for equipment in self.equipment.values():
            if equipment.status != ResourceStatus.AVAILABLE:
                continue
            
            match = await self._evaluate_equipment_match(equipment, request)
            if match.match_score > 0.3:
                matches.append(match)
        
        return matches
    
    async def _evaluate_equipment_match(
        self,
        equipment: Equipment,
        request: ResourceRequest
    ) -> ResourceMatch:
        """评估设备匹配度"""
        scores = {}
        reasons = []
        
        # 设备类型匹配（简化）
        scores['specialty_match'] = 0.8
        
        # 距离评分
        if request.location:
            distance = geodesic(
                (request.location.latitude, request.location.longitude),
                (equipment.location.latitude, equipment.location.longitude)
            ).kilometers
            
            max_distance = self.enhanced_config['matching']['max_distance_km']
            scores['distance'] = max(0, 1.0 - distance / max_distance)
            reasons.append(f"距离: {distance:.1f}km")
        else:
            scores['distance'] = 0.8
            distance = 0.0
        
        # 设备评分（简化）
        scores['rating'] = 0.8
        
        # 可用性
        availability = await self._check_equipment_availability(
            equipment, request.preferred_time
        )
        scores['availability'] = availability
        if availability > 0.8:
            reasons.append("设备可用")
        
        # 费用评分（简化）
        scores['cost'] = 0.8
        
        # 计算综合评分
        weights = self.enhanced_config['matching']['score_weights']
        match_score = sum(scores[key] * weights[key] for key in scores if key in weights)
        
        return ResourceMatch(
            resource_id=equipment.equipment_id,
            resource_type=ResourceType.EQUIPMENT,
            match_score=match_score,
            distance_km=distance,
            estimated_cost=0.0,
            available_time=request.preferred_time,
            confidence=min(match_score + 0.1, 1.0),
            reasons=reasons
        )
    
    async def _check_equipment_availability(
        self,
        equipment: Equipment,
        preferred_time: Optional[datetime]
    ) -> float:
        """检查设备可用性"""
        if not preferred_time:
            return 0.8
        
        # 检查维护时间
        for maintenance in equipment.maintenance_schedule:
            if maintenance.start_time <= preferred_time <= maintenance.end_time:
                return 0.0
        
        # 检查预约时间
        for booking in equipment.booking_slots:
            if booking.start_time <= preferred_time <= booking.end_time:
                return 0.2
        
        return 1.0
    
    async def _match_medicines(self, request: ResourceRequest) -> List[ResourceMatch]:
        """匹配药品资源"""
        matches = []
        
        for medicine in self.medicines.values():
            if medicine.stock_quantity <= 0:
                continue
            
            match = await self._evaluate_medicine_match(medicine, request)
            if match.match_score > 0.3:
                matches.append(match)
        
        return matches
    
    async def _evaluate_medicine_match(
        self,
        medicine: Medicine,
        request: ResourceRequest
    ) -> ResourceMatch:
        """评估药品匹配度"""
        scores = {}
        reasons = []
        
        # 药品类型匹配（简化）
        scores['specialty_match'] = 0.8
        
        # 距离评分（基于药房位置）
        scores['distance'] = 0.8
        distance = 0.0
        
        # 药品评分（简化）
        scores['rating'] = 0.8
        
        # 库存可用性
        if medicine.stock_quantity > 10:
            scores['availability'] = 1.0
            reasons.append("库存充足")
        elif medicine.stock_quantity > 0:
            scores['availability'] = 0.6
            reasons.append("库存有限")
        else:
            scores['availability'] = 0.0
        
        # 费用评分
        if request.budget_range:
            min_budget, max_budget = request.budget_range
            if min_budget <= medicine.unit_price <= max_budget:
                scores['cost'] = 1.0
                reasons.append("价格合适")
            else:
                scores['cost'] = 0.5
        else:
            scores['cost'] = 0.8
        
        # 计算综合评分
        weights = self.enhanced_config['matching']['score_weights']
        match_score = sum(scores[key] * weights[key] for key in scores if key in weights)
        
        return ResourceMatch(
            resource_id=medicine.medicine_id,
            resource_type=ResourceType.MEDICINE,
            match_score=match_score,
            distance_km=distance,
            estimated_cost=medicine.unit_price,
            available_time=datetime.now(),
            confidence=min(match_score + 0.1, 1.0),
            reasons=reasons
        )
    
    async def _rank_matches(
        self,
        matches: List[ResourceMatch],
        request: ResourceRequest
    ) -> List[ResourceMatch]:
        """排序匹配结果"""
        # 按匹配分数排序
        sorted_matches = sorted(matches, key=lambda m: m.match_score, reverse=True)
        
        # 限制返回数量
        max_results = self.enhanced_config['matching']['max_results']
        return sorted_matches[:max_results]
    
    async def _generate_resource_recommendations(
        self,
        matches: List[ResourceMatch],
        request: ResourceRequest
    ) -> List[str]:
        """生成资源建议"""
        recommendations = []
        
        if not matches:
            recommendations.append("未找到合适的资源，建议扩大搜索范围或调整需求")
            return recommendations
        
        best_match = matches[0]
        
        if best_match.match_score >= 0.8:
            recommendations.append("找到高度匹配的资源，建议优先选择")
        elif best_match.match_score >= 0.6:
            recommendations.append("找到较好匹配的资源，可以考虑选择")
        else:
            recommendations.append("匹配度一般，建议进一步筛选")
        
        # 基于资源类型的建议
        if request.resource_type == ResourceType.DOCTOR:
            if request.preferred_time:
                recommendations.append("建议提前预约，确保时间可用")
            recommendations.append("可以查看医生的患者评价和专业背景")
        
        elif request.resource_type == ResourceType.HOSPITAL:
            recommendations.append("建议提前了解医院的科室设置和服务流程")
            if any(m.distance_km > 20 for m in matches[:3]):
                recommendations.append("部分医院距离较远，建议考虑交通便利性")
        
        # 费用建议
        if request.budget_range:
            avg_cost = np.mean([m.estimated_cost for m in matches if m.estimated_cost > 0])
            min_budget, max_budget = request.budget_range
            if avg_cost > max_budget:
                recommendations.append("平均费用超出预算，建议调整预算或选择更经济的选项")
        
        return recommendations
    
    async def batch_find_resources(
        self,
        requests: List[ResourceRequest]
    ) -> List[ResourceAllocation]:
        """
        批量查找资源
        
        Args:
            requests: 资源请求列表
            
        Returns:
            资源分配结果列表
        """
        if self.enhanced_config['parallel_processing']['enabled']:
            # 并行处理
            tasks = []
            for request in requests:
                task = self.find_resources(
                    patient_id=request.patient_id,
                    resource_type=request.resource_type,
                    specialty=request.specialty,
                    location=request.location,
                    preferred_time=request.preferred_time,
                    symptoms=request.symptoms,
                    budget_range=request.budget_range,
                    priority=request.priority,
                    requirements=request.requirements
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 过滤有效结果
            valid_results = []
            for result in results:
                if isinstance(result, ResourceAllocation):
                    valid_results.append(result)
                else:
                    logger.error(f"批量资源匹配失败: {result}")
            
            self.stats['batch_processed'] += 1
            return valid_results
        else:
            # 串行处理
            results = []
            for request in requests:
                try:
                    result = await self.find_resources(
                        patient_id=request.patient_id,
                        resource_type=request.resource_type,
                        specialty=request.specialty,
                        location=request.location,
                        preferred_time=request.preferred_time,
                        symptoms=request.symptoms,
                        budget_range=request.budget_range,
                        priority=request.priority,
                        requirements=request.requirements
                    )
                    results.append(result)
                except Exception as e:
                    logger.error(f"资源匹配失败: {e}")
            
            return results
    
    async def _batch_processor(self):
        """批处理处理器"""
        while True:
            try:
                batch = []
                deadline = time.time() + 1.0  # 1秒收集窗口
                
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
                    await self.batch_find_resources(batch)
                
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
    
    async def _resource_status_updater(self):
        """资源状态更新器"""
        while True:
            try:
                # 更新医生状态
                for doctor in self.doctors.values():
                    # 清理过期的时间段
                    now = datetime.now()
                    doctor.available_slots = [
                        slot for slot in doctor.available_slots
                        if slot.end_time > now
                    ]
                
                # 更新设备状态
                for equipment in self.equipment.values():
                    # 清理过期的预约
                    now = datetime.now()
                    equipment.booking_slots = [
                        slot for slot in equipment.booking_slots
                        if slot.end_time > now
                    ]
                
                await asyncio.sleep(600)  # 10分钟更新一次
                
            except Exception as e:
                logger.error(f"资源状态更新器错误: {e}")
                await asyncio.sleep(60)
    
    async def _scheduler(self):
        """调度器"""
        while True:
            try:
                if self.enhanced_config['scheduling']['priority_queue']:
                    # 处理优先级队列
                    if self.priority_queue:
                        # 获取最高优先级的请求
                        priority, request = heapq.heappop(self.priority_queue)
                        
                        # 处理请求
                        await self.find_resources(
                            patient_id=request.patient_id,
                            resource_type=request.resource_type,
                            specialty=request.specialty,
                            location=request.location,
                            preferred_time=request.preferred_time,
                            symptoms=request.symptoms,
                            budget_range=request.budget_range,
                            priority=request.priority,
                            requirements=request.requirements
                        )
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"调度器错误: {e}")
                await asyncio.sleep(5)
    
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
    
    async def _set_to_cache(self, key: str, value: Any, ttl_type: str = "match_results"):
        """设置缓存"""
        if not self.enhanced_config['caching']['enabled']:
            return
        
        ttl = self.enhanced_config['caching']['ttl_seconds'].get(ttl_type, 900)
        expire_time = datetime.now() + timedelta(seconds=ttl)
        self.cache[key] = (value, expire_time)
    
    def _generate_cache_key(self, *args) -> str:
        """生成缓存键"""
        key_data = json.dumps(args, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _update_stats(self, processing_time_ms: float):
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
    
    async def get_service_stats(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        cache_hit_rate = (
            self.stats['cache_hits'] / 
            max(1, self.stats['cache_hits'] + self.stats['cache_misses'])
        )
        
        return {
            'total_requests': self.stats['total_requests'],
            'successful_matches': self.stats['successful_matches'],
            'cache_hit_rate': cache_hit_rate,
            'average_processing_time_ms': self.stats['average_processing_time_ms'],
            'average_match_score': self.stats['average_match_score'],
            'resource_utilization': dict(self.stats['resource_utilization']),
            'batch_processed': self.stats['batch_processed'],
            'cache_size': len(self.cache),
            'total_doctors': len(self.doctors),
            'total_hospitals': len(self.hospitals),
            'total_equipment': len(self.equipment),
            'total_medicines': len(self.medicines)
        }
    
    async def close(self):
        """关闭服务"""
        # 停止后台任务
        for task in self.background_tasks:
            task.cancel()
        
        # 等待任务完成
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        logger.info("增强版医疗资源服务已关闭") 