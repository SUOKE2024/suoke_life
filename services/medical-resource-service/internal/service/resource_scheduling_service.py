"""
resource_scheduling_service - 索克生活项目模块
"""

            import random
from ..domain.models import ResourceType, UrgencyLevel
from .resource_management_service import (
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
import asyncio
import heapq
import logging
import uuid

"""
智能资源调度服务
实现基于用户体质和病症的资源匹配、实时监控、智能预约排程和负载均衡
"""


    AvailabilityStatus,
    DoctorLevel,
    EquipmentType,
    InstitutionType,
    QualityGrade,
    ResourceCategory,
    ResourceManagementService,
)

logger = logging.getLogger(__name__)

class SchedulingStrategy(Enum):
    """调度策略"""

    FIRST_COME_FIRST_SERVE = "fcfs"  # 先来先服务
    SHORTEST_JOB_FIRST = "sjf"  # 最短作业优先
    PRIORITY_BASED = "priority"  # 基于优先级
    ROUND_ROBIN = "round_robin"  # 轮转调度
    LOAD_BALANCED = "load_balanced"  # 负载均衡
    # CONSTITUTION_OPTIMIZED removed
    MULTI_CRITERIA = "multi_criteria"  # 多准则决策

class AppointmentStatus(Enum):
    """预约状态"""

    PENDING = "pending"  # 待确认
    CONFIRMED = "confirmed"  # 已确认
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消
    RESCHEDULED = "rescheduled"  # 已改期

class LoadBalancingMethod(Enum):
    """负载均衡方法"""

    ROUND_ROBIN = "round_robin"  # 轮询
    LEAST_CONNECTIONS = "least_connections"  # 最少连接
    WEIGHTED_ROUND_ROBIN = "weighted_rr"  # 加权轮询
    LEAST_RESPONSE_TIME = "least_rt"  # 最短响应时间
    RESOURCE_BASED = "resource_based"  # 基于资源
    # CONSTITUTION_AWARE removed

@dataclass
class AppointmentRequest:
    """预约请求"""

    request_id: str
    user_id: str
    # constitution_type field removed
    symptoms: List[str]
    preferred_resource_category: ResourceCategory
    preferred_time_slots: List[Dict[str, str]]
    urgency_level: UrgencyLevel
    max_distance_km: float
    max_price: float
    special_requirements: List[str]
    location: Dict[str, float]
    created_at: datetime = field(default_factory=datetime.now)
    status: AppointmentStatus = AppointmentStatus.PENDING

@dataclass
class ScheduledAppointment:
    """已调度预约"""

    appointment_id: str
    request_id: str
    user_id: str
    resource_id: str
    resource_category: ResourceCategory
    scheduled_time: datetime
    duration_minutes: int
    estimated_cost: float
    priority_score: float
    match_score: float
    status: AppointmentStatus
    notes: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class ResourceLoad:
    """资源负载"""

    resource_id: str
    resource_category: ResourceCategory
    current_load: float
    max_capacity: float
    utilization_rate: float
    queue_length: int
    average_wait_time: float
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class SchedulingMetrics:
    """调度指标"""

    total_requests: int
    successful_schedules: int
    failed_schedules: int
    average_wait_time: float
    average_match_score: float
    resource_utilization: Dict[str, float]
    user_satisfaction: float
    cost_efficiency: float
    last_updated: datetime = field(default_factory=datetime.now)

class ResourceSchedulingService:
    """
    智能资源调度服务

    负责基于用户体质和病症的资源匹配、实时监控、智能预约排程和负载均衡
    """

    def __init__(
        self, config: Dict[str, Any], resource_service: ResourceManagementService
    ):
        self.config = config
        self.resource_service = resource_service

        # 调度队列
        self.pending_requests: List[AppointmentRequest] = []
        self.priority_queue: List[Tuple[float, AppointmentRequest]] = []

        # 预约记录
        self.scheduled_appointments: Dict[str, ScheduledAppointment] = {}
        self.appointment_history: List[ScheduledAppointment] = []

        # 资源负载监控
        self.resource_loads: Dict[str, ResourceLoad] = {}
        self.load_history: Dict[str, List[ResourceLoad]] = defaultdict(list)

        # 调度策略
        self.current_strategy = SchedulingStrategy.MULTI_CRITERIA
        self.load_balancing_method = LoadBalancingMethod.RESOURCE_BASED

        # 调度指标
        self.scheduling_metrics = SchedulingMetrics(
            total_requests=0,
            successful_schedules=0,
            failed_schedules=0,
            average_wait_time=0.0,
            average_match_score=0.0,
            resource_utilization={},
            user_satisfaction=0.0,
            cost_efficiency=0.0,
        )

        # 资源匹配权重配置
        self.resource_weights = self._initialize_resource_weights()

        # 时间段权重
        self.time_slot_weights = self._initialize_time_weights()

        # 线程池
        self.executor = ThreadPoolExecutor(max_workers=4)

        # 启动监控任务
        self.monitoring_task = None

        logger.info("智能资源调度服务初始化完成")

    def _initialize_resource_weights(self) -> Dict[str, Dict[str, float]]:
        """初始化资源匹配权重"""
        return {
            "general_medicine": {
                "doctor": 0.9,
                "medical_equipment": 0.8,
                "hospital": 0.9,
                "clinic": 0.7,
            },
            "emergency_care": {
                "emergency_doctor": 1.0,
                "emergency_equipment": 0.9,
                "emergency_room": 1.0,
                "ambulance": 0.8,
            },
            "specialist_care": {
                "specialist_doctor": 0.9,
                "specialized_equipment": 0.8,
                "specialist_clinic": 0.8,
                "hospital": 0.7,
            },
            "preventive_care": {
                "general_doctor": 0.8,
                "screening_equipment": 0.9,
                "wellness_center": 0.7,
                "clinic": 0.6,
            },
        }

    def _initialize_time_weights(self) -> Dict[str, float]:
        """初始化时间段权重"""
        return {
            "morning": 1.0,  # 上午时段
            "afternoon": 0.8,  # 下午时段
            "evening": 0.6,  # 晚上时段
            "weekend": 0.7,  # 周末时段
            "holiday": 0.5,  # 节假日时段
        }

    async def start_monitoring(self):
        """启动资源监控"""
        try:
            self.monitoring_task = asyncio.create_task(self._monitor_resources())
            logger.info("资源监控已启动")

        except Exception as e:
            logger.error(f"启动资源监控失败: {e}")

    async def stop_monitoring(self):
        """停止资源监控"""
        try:
            if self.monitoring_task:
                self.monitoring_task.cancel()
                await self.monitoring_task
            logger.info("资源监控已停止")

        except Exception as e:
            logger.error(f"停止资源监控失败: {e}")

    async def _monitor_resources(self):
        """监控资源状态"""
        while True:
            try:
                await self._update_resource_loads()
                await self._check_resource_availability()
                await self._optimize_load_balancing()
                await asyncio.sleep(30)  # 每30秒更新一次

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"资源监控异常: {e}")
                await asyncio.sleep(60)

    async def _update_resource_loads(self):
        """更新资源负载"""
        try:
            # 更新中医师负载
            for doctor_id, doctor in self.resource_service.tcm_doctors.items():
                current_appointments = [
                    apt
                    for apt in self.scheduled_appointments.values()
                    if apt.resource_id == doctor_id
                    and apt.status == AppointmentStatus.CONFIRMED
                ]

                current_load = len(current_appointments)
                max_capacity = 20  # 假设每天最多20个预约
                utilization_rate = (
                    current_load / max_capacity if max_capacity > 0 else 0
                )

                # 计算平均等待时间
                wait_times = []
                for apt in current_appointments:
                    wait_time = (
                        apt.scheduled_time - apt.created_at
                    ).total_seconds() / 3600
                    wait_times.append(wait_time)

                average_wait_time = (
                    sum(wait_times) / len(wait_times) if wait_times else 0
                )

                load = ResourceLoad(
                    resource_id=doctor_id,
                    resource_category=ResourceCategory.TCM_DOCTOR,
                    current_load=current_load,
                    max_capacity=max_capacity,
                    utilization_rate=utilization_rate,
                    queue_length=len(
                        [
                            req
                            for req in self.pending_requests
                            if req.preferred_resource_category
                            == ResourceCategory.TCM_DOCTOR
                        ]
                    ),
                    average_wait_time=average_wait_time,
                )

                self.resource_loads[doctor_id] = load
                self.load_history[doctor_id].append(load)

                # 保持历史记录在合理范围内
                if len(self.load_history[doctor_id]) > 100:
                    self.load_history[doctor_id] = self.load_history[doctor_id][-100:]

            # 更新设备负载
            for (
                equipment_id,
                equipment,
            ) in self.resource_service.medical_equipment.items():
                utilization_rate = equipment.usage_statistics.get(
                    "utilization_rate", 0.5
                )
                current_load = utilization_rate * 10  # 假设满负载为10

                load = ResourceLoad(
                    resource_id=equipment_id,
                    resource_category=ResourceCategory.MEDICAL_EQUIPMENT,
                    current_load=current_load,
                    max_capacity=10.0,
                    utilization_rate=utilization_rate,
                    queue_length=0,
                    average_wait_time=0.0,
                )

                self.resource_loads[equipment_id] = load
                self.load_history[equipment_id].append(load)

        except Exception as e:
            logger.error(f"更新资源负载失败: {e}")

    async def _check_resource_availability(self):
        """检查资源可用性"""
        try:
            current_time = datetime.now()

            # 检查预约是否需要状态更新
            for appointment in self.scheduled_appointments.values():
                if appointment.status == AppointmentStatus.CONFIRMED:
                    if appointment.scheduled_time <= current_time:
                        appointment.status = AppointmentStatus.IN_PROGRESS
                        appointment.updated_at = current_time

                elif appointment.status == AppointmentStatus.IN_PROGRESS:
                    end_time = appointment.scheduled_time + timedelta(
                        minutes=appointment.duration_minutes
                    )
                    if current_time >= end_time:
                        appointment.status = AppointmentStatus.COMPLETED
                        appointment.updated_at = current_time

                        # 释放资源
                        await self.resource_service._update_resource_status(
                            appointment.resource_id,
                            appointment.resource_category,
                            "released",
                        )

        except Exception as e:
            logger.error(f"检查资源可用性失败: {e}")

    async def _optimize_load_balancing(self):
        """优化负载均衡"""
        try:
            # 识别高负载资源
            high_load_resources = []
            low_load_resources = []

            for resource_id, load in self.resource_loads.items():
                if load.utilization_rate > 0.8:
                    high_load_resources.append(resource_id)
                elif load.utilization_rate < 0.3:
                    low_load_resources.append(resource_id)

            # 如果有高负载资源，尝试重新分配
            if high_load_resources and low_load_resources:
                await self._redistribute_load(high_load_resources, low_load_resources)

        except Exception as e:
            logger.error(f"优化负载均衡失败: {e}")

    async def _redistribute_load(
        self, high_load_resources: List[str], low_load_resources: List[str]
    ):
        """重新分配负载"""
        try:
            # 查找可以重新分配的预约
            redistributable_appointments = []

            for appointment in self.scheduled_appointments.values():
                if (
                    appointment.resource_id in high_load_resources
                    and appointment.status == AppointmentStatus.CONFIRMED
                    and appointment.scheduled_time
                    > datetime.now() + timedelta(hours=24)
                ):
                    redistributable_appointments.append(appointment)

            # 尝试重新分配到低负载资源
            for appointment in redistributable_appointments[:5]:  # 限制重新分配数量
                for low_load_resource_id in low_load_resources:
                    # 检查资源类型是否匹配
                    if self._is_resource_compatible(appointment, low_load_resource_id):
                        # 尝试重新调度
                        success = await self._reschedule_appointment(
                            appointment, low_load_resource_id
                        )
                        if success:
                            logger.info(
                                f"成功重新分配预约 {appointment.appointment_id} 到资源 {low_load_resource_id}"
                            )
                            break

        except Exception as e:
            logger.error(f"重新分配负载失败: {e}")

    def _is_resource_compatible(
        self, appointment: ScheduledAppointment, resource_id: str
    ) -> bool:
        """检查资源是否兼容"""
        try:
            # 检查资源类型
            if appointment.resource_category == ResourceCategory.TCM_DOCTOR:
                return resource_id in self.resource_service.tcm_doctors
            elif appointment.resource_category == ResourceCategory.MEDICAL_EQUIPMENT:
                return resource_id in self.resource_service.medical_equipment
            elif appointment.resource_category == ResourceCategory.HERBAL_MEDICINE:
                return resource_id in self.resource_service.herbal_medicines

            return False

        except Exception as e:
            logger.error(f"检查资源兼容性失败: {e}")
            return False

    async def _reschedule_appointment(
        self, appointment: ScheduledAppointment, new_resource_id: str
    ) -> bool:
        """重新调度预约"""
        try:
            # 检查新资源的可用性
            is_available = await self.resource_service._check_resource_availability(
                new_resource_id,
                appointment.resource_category,
                appointment.scheduled_time,
                appointment.scheduled_time
                + timedelta(minutes=appointment.duration_minutes),
            )

            if is_available:
                # 释放原资源
                await self.resource_service._update_resource_status(
                    appointment.resource_id, appointment.resource_category, "released"
                )

                # 分配新资源
                await self.resource_service._update_resource_status(
                    new_resource_id, appointment.resource_category, "allocated"
                )

                # 更新预约信息
                appointment.resource_id = new_resource_id
                appointment.status = AppointmentStatus.RESCHEDULED
                appointment.updated_at = datetime.now()

                return True

            return False

        except Exception as e:
            logger.error(f"重新调度预约失败: {e}")
            return False

    async def submit_appointment_request(
        self, request: AppointmentRequest
    ) -> Dict[str, Any]:
        """提交预约请求"""
        try:
            # 添加到待处理队列
            self.pending_requests.append(request)

            # 计算优先级分数
            priority_score = self._calculate_priority_score(request)

            # 添加到优先级队列
            heapq.heappush(self.priority_queue, (-priority_score, request))

            # 更新指标
            self.scheduling_metrics.total_requests += 1

            # 尝试立即调度
            scheduling_result = await self._schedule_request(request)

            if scheduling_result["success"]:
                self.scheduling_metrics.successful_schedules += 1

                # 从待处理队列中移除
                if request in self.pending_requests:
                    self.pending_requests.remove(request)
            else:
                self.scheduling_metrics.failed_schedules += 1

            logger.info(f"预约请求已提交: {request.request_id}")
            return scheduling_result

        except Exception as e:
            logger.error(f"提交预约请求失败: {e}")
            return {
                "success": False,
                "message": f"提交预约请求失败: {str(e)}",
                "appointment_id": None,
            }

    def _calculate_priority_score(self, request: AppointmentRequest) -> float:
        """计算优先级分数"""
        try:
            score = 0.0

            # 紧急程度权重
            urgency_weights = {
                UrgencyLevel.LOW: 0.2,
                UrgencyLevel.MEDIUM: 0.5,
                UrgencyLevel.HIGH: 0.8,
                UrgencyLevel.URGENT: 1.0,
            }
            score += urgency_weights.get(request.urgency_level, 0.5) * 0.4

            # 等待时间权重
            wait_time_hours = (
                datetime.now() - request.created_at
            ).total_seconds() / 3600
            wait_score = min(wait_time_hours / 24.0, 1.0)  # 最多24小时满分
            score += wait_score * 0.3

            # 症状严重程度权重（增加权重）
            symptom_score = self._assess_symptom_severity(request.symptoms)
            score += symptom_score * 0.2

            # 用户偏好权重
            preference_score = 0.5  # 默认偏好分数
            score += preference_score * 0.1

            return score

        except Exception as e:
            logger.error(f"计算优先级分数失败: {e}")
            return 0.5

    def _get_symptom_category_priority(self, symptoms: List[str]) -> float:
        """获取症状类别优先级"""
        # 基于症状类别确定优先级
        emergency_symptoms = ["胸痛", "呼吸困难", "意识模糊", "剧烈头痛", "大出血"]
        urgent_symptoms = ["高热", "严重腹痛", "持续呕吐", "严重头痛"]
        
        for symptom in symptoms:
            if any(emergency in symptom for emergency in emergency_symptoms):
                return 1.0
            elif any(urgent in symptom for urgent in urgent_symptoms):
                return 0.8
        
        return 0.5

    def _assess_symptom_severity(self, symptoms: List[str]) -> float:
        """评估症状严重程度"""
        # 简化的症状严重程度评估
        severe_symptoms = ["胸痛", "呼吸困难", "高热", "剧烈头痛", "意识模糊"]
        moderate_symptoms = ["头痛", "腹痛", "发热", "咳嗽", "失眠"]

        severe_count = sum(
            1 for symptom in symptoms if any(s in symptom for s in severe_symptoms)
        )
        moderate_count = sum(
            1 for symptom in symptoms if any(s in symptom for s in moderate_symptoms)
        )

        if severe_count > 0:
            return 1.0
        elif moderate_count > 0:
            return 0.6
        else:
            return 0.3

    async def _schedule_request(self, request: AppointmentRequest) -> Dict[str, Any]:
        """调度预约请求"""
        try:
            # 搜索合适的资源
            resources = await self.resource_service.search_resources(
                resource_category=request.preferred_resource_category,
                symptoms=request.symptoms,
                location=request.location,
                max_distance_km=request.max_distance_km,
                max_price=request.max_price,
                availability_required=True,
            )

            if not resources:
                return {
                    "success": False,
                    "message": "未找到合适的资源",
                    "appointment_id": None,
                }

            # 根据调度策略选择最佳资源
            best_resource = await self._select_best_resource(request, resources)

            if not best_resource:
                return {
                    "success": False,
                    "message": "无法找到最佳资源匹配",
                    "appointment_id": None,
                }

            # 查找最佳时间段
            best_time_slot = await self._find_best_time_slot(request, best_resource)

            if not best_time_slot:
                return {
                    "success": False,
                    "message": "无法找到合适的时间段",
                    "appointment_id": None,
                }

            # 创建预约
            appointment = await self._create_appointment(
                request, best_resource, best_time_slot
            )

            if appointment:
                return {
                    "success": True,
                    "message": "预约调度成功",
                    "appointment_id": appointment.appointment_id,
                    "resource_id": appointment.resource_id,
                    "scheduled_time": appointment.scheduled_time.isoformat(),
                    "estimated_cost": appointment.estimated_cost,
                }
            else:
                return {
                    "success": False,
                    "message": "创建预约失败",
                    "appointment_id": None,
                }

        except Exception as e:
            logger.error(f"调度预约请求失败: {e}")
            return {
                "success": False,
                "message": f"调度失败: {str(e)}",
                "appointment_id": None,
            }

    async def _select_best_resource(
        self, request: AppointmentRequest, resources: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """选择最佳资源"""
        try:
            if not resources:
                return None

            # 根据当前调度策略选择资源
            if self.current_strategy == SchedulingStrategy.MULTI_CRITERIA:
                return await self._multi_criteria_selection(request, resources)
            elif self.current_strategy == SchedulingStrategy.LOAD_BALANCED:
                return await self._load_balanced_selection(request, resources)
            # CONSTITUTION_OPTIMIZED strategy removed
            elif self.current_strategy == SchedulingStrategy.PRIORITY_BASED:
                return await self._priority_based_selection(request, resources)
            else:
                # 默认使用多准则决策
                return await self._multi_criteria_selection(request, resources)

        except Exception as e:
            logger.error(f"选择最佳资源失败: {e}")
            return None

    async def _multi_criteria_selection(
        self, request: AppointmentRequest, resources: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """多准则决策选择"""
        try:
            best_resource = None
            best_score = -1

            for resource in resources:
                score = 0.0

                # 匹配度权重 (40%)
                match_score = resource.get("match_score", 0.5)
                score += match_score * 0.4

                # 负载权重 (25%)
                resource_id = resource["resource_id"]
                load = self.resource_loads.get(resource_id)
                if load:
                    load_score = 1.0 - load.utilization_rate
                    score += load_score * 0.25
                else:
                    score += 0.5 * 0.25

                # 距离权重 (15%)
                distance = resource.get("distance_km", 0)
                if distance > 0:
                    distance_score = max(0, 1.0 - distance / request.max_distance_km)
                    score += distance_score * 0.15
                else:
                    score += 1.0 * 0.15

                # 价格权重 (10%)
                if request.preferred_resource_category == ResourceCategory.TCM_DOCTOR:
                    price = resource.get("consultation_fee", 0)
                elif (
                    request.preferred_resource_category
                    == ResourceCategory.MEDICAL_EQUIPMENT
                ):
                    price = resource.get("operating_cost_per_hour", 0)
                else:
                    price = resource.get("price_per_unit", 0)

                if price > 0 and request.max_price > 0:
                    price_score = max(0, 1.0 - price / request.max_price)
                    score += price_score * 0.1
                else:
                    score += 0.5 * 0.1

                # 质量权重 (10%)
                if request.preferred_resource_category == ResourceCategory.TCM_DOCTOR:
                    quality = resource.get("patient_rating", 3.0) / 5.0
                elif (
                    request.preferred_resource_category
                    == ResourceCategory.MODERN_MEDICAL_INSTITUTION
                ):
                    quality = resource.get("quality_rating", 3.0) / 5.0
                else:
                    quality = 0.8  # 默认质量分数

                score += quality * 0.1

                if score > best_score:
                    best_score = score
                    best_resource = resource

            return best_resource

        except Exception as e:
            logger.error(f"多准则决策选择失败: {e}")
            return None

    async def _load_balanced_selection(
        self, request: AppointmentRequest, resources: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """负载均衡选择"""
        try:
            if self.load_balancing_method == LoadBalancingMethod.LEAST_CONNECTIONS:
                # 选择负载最低的资源
                best_resource = None
                min_load = float("inf")

                for resource in resources:
                    resource_id = resource["resource_id"]
                    load = self.resource_loads.get(resource_id)
                    current_load = load.current_load if load else 0

                    if current_load < min_load:
                        min_load = current_load
                        best_resource = resource

                return best_resource

            elif self.load_balancing_method == LoadBalancingMethod.WEIGHTED_ROUND_ROBIN:
                # 基于权重的轮询选择
                return await self._weighted_round_robin_selection(request, resources)

            # CONSTITUTION_AWARE method removed

            else:
                # 默认轮询
                return resources[0] if resources else None

        except Exception as e:
            logger.error(f"负载均衡选择失败: {e}")
            return None

    async def _symptom_based_selection(
        self, request: AppointmentRequest, resources: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """基于症状的选择"""
        try:
            # 根据症状类别获取权重
            symptom_category = self._categorize_symptoms(request.symptoms)
            resource_weights = self.resource_weights.get(symptom_category, {})

            best_resource = None
            best_score = -1

            for resource in resources:
                # 基于症状匹配计算分数
                resource_type = resource.get("resource_type", "")
                weight = resource_weights.get(resource_type, 0.5)

                # 结合匹配度
                match_score = resource.get("match_score", 0.5)
                total_score = weight * 0.7 + match_score * 0.3

                if total_score > best_score:
                    best_score = total_score
                    best_resource = resource

            return best_resource

        except Exception as e:
            logger.error(f"基于症状的选择失败: {e}")
            return None

    async def _priority_based_selection(
        self, request: AppointmentRequest, resources: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """基于优先级选择"""
        try:
            # 根据紧急程度选择资源
            if request.urgency_level == UrgencyLevel.URGENT:
                # 紧急情况选择最快可用的资源
                return resources[0] if resources else None
            else:
                # 非紧急情况选择最佳匹配
                return (
                    max(resources, key=lambda r: r.get("match_score", 0))
                    if resources
                    else None
                )

        except Exception as e:
            logger.error(f"基于优先级选择失败: {e}")
            return None

    async def _weighted_round_robin_selection(
        self, request: AppointmentRequest, resources: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """加权轮询选择"""
        try:
            # 简化的加权轮询实现
            weights = []
            for resource in resources:
                # 基于质量和负载计算权重
                if resource.get("resource_type") == "tcm_doctor":
                    quality = resource.get("patient_rating", 3.0) / 5.0
                else:
                    quality = 0.8

                resource_id = resource["resource_id"]
                load = self.resource_loads.get(resource_id)
                load_factor = 1.0 - load.utilization_rate if load else 1.0

                weight = quality * load_factor
                weights.append(weight)

            if not weights:
                return None

            # 根据权重选择
            total_weight = sum(weights)
            if total_weight == 0:
                return resources[0]


            r = random.uniform(0, total_weight)
            cumulative = 0

            for i, weight in enumerate(weights):
                cumulative += weight
                if r <= cumulative:
                    return resources[i]

            return resources[-1]

        except Exception as e:
            logger.error(f"加权轮询选择失败: {e}")
            return None

    def _categorize_symptoms(self, symptoms: List[str]) -> str:
        """将症状分类"""
        emergency_keywords = ["胸痛", "呼吸困难", "意识模糊", "大出血", "剧烈头痛"]
        specialist_keywords = ["心脏", "肺部", "神经", "骨科", "皮肤", "眼科", "耳鼻喉"]
        
        # 检查是否为紧急症状
        for symptom in symptoms:
            if any(keyword in symptom for keyword in emergency_keywords):
                return "emergency_care"
        
        # 检查是否需要专科治疗
        for symptom in symptoms:
            if any(keyword in symptom for keyword in specialist_keywords):
                return "specialist_care"
        
        # 检查是否为预防性护理
        preventive_keywords = ["体检", "筛查", "预防", "健康检查"]
        for symptom in symptoms:
            if any(keyword in symptom for keyword in preventive_keywords):
                return "preventive_care"
        
        # 默认为一般医疗
        return "general_medicine"

    async def _find_best_time_slot(
        self, request: AppointmentRequest, resource: Dict[str, Any]
    ) -> Optional[datetime]:
        """查找最佳时间段"""
        try:
            resource_id = resource["resource_id"]

            # 获取用户偏好时间段
            preferred_slots = request.preferred_time_slots

            # 如果没有偏好时间，生成默认时间段
            if not preferred_slots:
                preferred_slots = self._generate_default_time_slots()

            # 检查每个时间段的可用性
            for slot in preferred_slots:
                start_time_str = slot.get("start_time")
                if not start_time_str:
                    continue

                try:
                    start_time = datetime.fromisoformat(start_time_str)
                except:
                    # 如果是相对时间格式，转换为绝对时间
                    start_time = self._parse_relative_time(start_time_str)

                if start_time < datetime.now():
                    continue

                # 估算持续时间
                duration_minutes = self._estimate_duration(
                    request.preferred_resource_category
                )
                end_time = start_time + timedelta(minutes=duration_minutes)

                # 检查资源可用性
                is_available = await self.resource_service._check_resource_availability(
                    resource_id,
                    request.preferred_resource_category,
                    start_time,
                    end_time,
                )

                if is_available:
                    return start_time

            # 如果偏好时间都不可用，查找最近可用时间
            return await self._find_next_available_time(
                resource_id, request.preferred_resource_category
            )

        except Exception as e:
            logger.error(f"查找最佳时间段失败: {e}")
            return None

    def _generate_default_time_slots(self) -> List[Dict[str, str]]:
        """生成默认时间段"""
        slots = []
        base_time = datetime.now() + timedelta(days=1)

        # 生成未来7天的时间段
        for day in range(7):
            date = base_time + timedelta(days=day)

            # 上午时段
            morning_slot = {
                "start_time": date.replace(
                    hour=9, minute=0, second=0, microsecond=0
                ).isoformat(),
                "end_time": date.replace(
                    hour=12, minute=0, second=0, microsecond=0
                ).isoformat(),
            }
            slots.append(morning_slot)

            # 下午时段
            afternoon_slot = {
                "start_time": date.replace(
                    hour=14, minute=0, second=0, microsecond=0
                ).isoformat(),
                "end_time": date.replace(
                    hour=17, minute=0, second=0, microsecond=0
                ).isoformat(),
            }
            slots.append(afternoon_slot)

        return slots

    def _parse_relative_time(self, time_str: str) -> datetime:
        """解析相对时间"""
        base_time = datetime.now()

        if "明天" in time_str:
            base_time += timedelta(days=1)
        elif "后天" in time_str:
            base_time += timedelta(days=2)
        elif "下周" in time_str:
            base_time += timedelta(days=7)

        if "上午" in time_str:
            return base_time.replace(hour=9, minute=0, second=0, microsecond=0)
        elif "下午" in time_str:
            return base_time.replace(hour=14, minute=0, second=0, microsecond=0)
        elif "晚上" in time_str:
            return base_time.replace(hour=19, minute=0, second=0, microsecond=0)
        else:
            return base_time.replace(hour=9, minute=0, second=0, microsecond=0)

    def _estimate_duration(self, resource_category: ResourceCategory) -> int:
        """估算持续时间（分钟）"""
        duration_map = {
            ResourceCategory.TCM_DOCTOR: 60,  # 中医诊疗1小时
            ResourceCategory.MODERN_MEDICAL_INSTITUTION: 30,  # 现代医疗30分钟
            ResourceCategory.MEDICAL_EQUIPMENT: 45,  # 设备检查45分钟
            ResourceCategory.HERBAL_MEDICINE: 15,  # 药材咨询15分钟
            ResourceCategory.AGRICULTURAL_PRODUCT: 15,  # 农产品咨询15分钟
        }
        return duration_map.get(resource_category, 60)

    async def _find_next_available_time(
        self, resource_id: str, resource_category: ResourceCategory
    ) -> Optional[datetime]:
        """查找下一个可用时间"""
        try:
            # 从明天开始查找
            start_time = datetime.now().replace(
                hour=9, minute=0, second=0, microsecond=0
            ) + timedelta(days=1)
            duration_minutes = self._estimate_duration(resource_category)

            # 查找未来14天内的可用时间
            for day in range(14):
                for hour in range(9, 18):  # 工作时间9-18点
                    check_time = start_time + timedelta(days=day, hours=hour - 9)
                    end_time = check_time + timedelta(minutes=duration_minutes)

                    is_available = (
                        await self.resource_service._check_resource_availability(
                            resource_id, resource_category, check_time, end_time
                        )
                    )

                    if is_available:
                        return check_time

            return None

        except Exception as e:
            logger.error(f"查找下一个可用时间失败: {e}")
            return None

    async def _create_appointment(
        self,
        request: AppointmentRequest,
        resource: Dict[str, Any],
        scheduled_time: datetime,
    ) -> Optional[ScheduledAppointment]:
        """创建预约"""
        try:
            appointment_id = str(uuid.uuid4())
            resource_id = resource["resource_id"]

            # 计算持续时间
            duration_minutes = self._estimate_duration(
                request.preferred_resource_category
            )

            # 计算成本
            estimated_cost = await self.resource_service._calculate_allocation_cost(
                resource_id,
                request.preferred_resource_category,
                scheduled_time,
                scheduled_time + timedelta(minutes=duration_minutes),
            )

            # 计算优先级和匹配分数
            priority_score = self._calculate_priority_score(request)
            match_score = resource.get("match_score", 0.5)

            # 创建预约对象
            appointment = ScheduledAppointment(
                appointment_id=appointment_id,
                request_id=request.request_id,
                user_id=request.user_id,
                resource_id=resource_id,
                resource_category=request.preferred_resource_category,
                scheduled_time=scheduled_time,
                duration_minutes=duration_minutes,
                estimated_cost=estimated_cost,
                priority_score=priority_score,
                match_score=match_score,
                status=AppointmentStatus.CONFIRMED,
                notes="",
            )

            # 保存预约
            self.scheduled_appointments[appointment_id] = appointment
            self.appointment_history.append(appointment)

            # 分配资源
            allocation_result = await self.resource_service.allocate_resource(
                user_id=request.user_id,
                resource_id=resource_id,
                resource_category=request.preferred_resource_category,
                start_time=scheduled_time,
                end_time=scheduled_time + timedelta(minutes=duration_minutes),
                purpose=f"预约服务: {', '.join(request.symptoms)}",
                priority_level=request.urgency_level,
            )

            if not allocation_result["success"]:
                # 如果资源分配失败，删除预约
                del self.scheduled_appointments[appointment_id]
                self.appointment_history.pop()
                return None

            logger.info(f"预约创建成功: {appointment_id}")
            return appointment

        except Exception as e:
            logger.error(f"创建预约失败: {e}")
            return None

    async def cancel_appointment(
        self, appointment_id: str, reason: str = ""
    ) -> Dict[str, Any]:
        """取消预约"""
        try:
            appointment = self.scheduled_appointments.get(appointment_id)
            if not appointment:
                return {"success": False, "message": "预约不存在"}

            if appointment.status in [
                AppointmentStatus.COMPLETED,
                AppointmentStatus.CANCELLED,
            ]:
                return {"success": False, "message": "预约已完成或已取消，无法取消"}

            # 更新预约状态
            appointment.status = AppointmentStatus.CANCELLED
            appointment.notes = f"取消原因: {reason}"
            appointment.updated_at = datetime.now()

            # 释放资源
            await self.resource_service._update_resource_status(
                appointment.resource_id, appointment.resource_category, "released"
            )

            logger.info(f"预约已取消: {appointment_id}")
            return {"success": True, "message": "预约取消成功"}

        except Exception as e:
            logger.error(f"取消预约失败: {e}")
            return {"success": False, "message": f"取消预约失败: {str(e)}"}

    async def get_scheduling_statistics(self) -> Dict[str, Any]:
        """获取调度统计信息"""
        try:
            # 更新调度指标
            await self._update_scheduling_metrics()

            stats = {
                "scheduling_metrics": {
                    "total_requests": self.scheduling_metrics.total_requests,
                    "successful_schedules": self.scheduling_metrics.successful_schedules,
                    "failed_schedules": self.scheduling_metrics.failed_schedules,
                    "success_rate": (
                        self.scheduling_metrics.successful_schedules
                        / self.scheduling_metrics.total_requests
                        if self.scheduling_metrics.total_requests > 0
                        else 0
                    ),
                    "average_wait_time": self.scheduling_metrics.average_wait_time,
                    "average_match_score": self.scheduling_metrics.average_match_score,
                    "user_satisfaction": self.scheduling_metrics.user_satisfaction,
                    "cost_efficiency": self.scheduling_metrics.cost_efficiency,
                },
                "queue_status": {
                    "pending_requests": len(self.pending_requests),
                    "priority_queue_size": len(self.priority_queue),
                    "active_appointments": len(
                        [
                            apt
                            for apt in self.scheduled_appointments.values()
                            if apt.status
                            in [
                                AppointmentStatus.CONFIRMED,
                                AppointmentStatus.IN_PROGRESS,
                            ]
                        ]
                    ),
                },
                "resource_utilization": self.scheduling_metrics.resource_utilization,
                "load_balancing": {
                    "current_strategy": self.current_strategy.value,
                    "load_balancing_method": self.load_balancing_method.value,
                    "high_load_resources": len(
                        [
                            load
                            for load in self.resource_loads.values()
                            if load.utilization_rate > 0.8
                        ]
                    ),
                    "low_load_resources": len(
                        [
                            load
                            for load in self.resource_loads.values()
                            if load.utilization_rate < 0.3
                        ]
                    ),
                },
            }

            return stats

        except Exception as e:
            logger.error(f"获取调度统计信息失败: {e}")
            return {}

    async def _update_scheduling_metrics(self):
        """更新调度指标"""
        try:
            # 计算平均等待时间
            wait_times = []
            match_scores = []

            for appointment in self.appointment_history[-100:]:  # 最近100个预约
                if appointment.status != AppointmentStatus.CANCELLED:
                    # 计算等待时间（从请求到调度的时间）
                    wait_time = (
                        appointment.created_at - appointment.created_at
                    ).total_seconds() / 3600
                    wait_times.append(wait_time)
                    match_scores.append(appointment.match_score)

            if wait_times:
                self.scheduling_metrics.average_wait_time = sum(wait_times) / len(
                    wait_times
                )

            if match_scores:
                self.scheduling_metrics.average_match_score = sum(match_scores) / len(
                    match_scores
                )

            # 计算资源利用率
            utilization = {}
            for resource_id, load in self.resource_loads.items():
                utilization[resource_id] = load.utilization_rate

            self.scheduling_metrics.resource_utilization = utilization

            # 更新时间戳
            self.scheduling_metrics.last_updated = datetime.now()

        except Exception as e:
            logger.error(f"更新调度指标失败: {e}")

    async def optimize_scheduling_strategy(self) -> Dict[str, Any]:
        """优化调度策略"""
        try:
            optimization_results = {
                "current_performance": {},
                "recommendations": [],
                "strategy_adjustments": [],
            }

            # 分析当前性能
            stats = await self.get_scheduling_statistics()
            current_performance = stats.get("scheduling_metrics", {})
            optimization_results["current_performance"] = current_performance

            # 生成优化建议
            success_rate = current_performance.get("success_rate", 0)
            if success_rate < 0.8:
                optimization_results["recommendations"].append(
                    {
                        "type": "success_rate_improvement",
                        "description": "调度成功率偏低，建议增加资源或优化匹配算法",
                        "current_value": success_rate,
                        "target_value": 0.85,
                    }
                )

            average_wait_time = current_performance.get("average_wait_time", 0)
            if average_wait_time > 24:  # 超过24小时
                optimization_results["recommendations"].append(
                    {
                        "type": "wait_time_reduction",
                        "description": "平均等待时间过长，建议优化调度策略或增加资源",
                        "current_value": average_wait_time,
                        "target_value": 12,
                    }
                )

            # 策略调整建议
            high_load_count = stats.get("load_balancing", {}).get(
                "high_load_resources", 0
            )
            if high_load_count > 3:
                optimization_results["strategy_adjustments"].append(
                    {
                        "type": "load_balancing_enhancement",
                        "description": "高负载资源过多，建议启用更积极的负载均衡策略",
                        "suggested_strategy": SchedulingStrategy.LOAD_BALANCED.value,
                    }
                )

            match_score = current_performance.get("average_match_score", 0)
            if match_score < 0.7:
                optimization_results["strategy_adjustments"].append(
                    {
                        "type": "matching_improvement",
                        "description": "匹配分数偏低，建议启用体质优化策略",
                        "suggested_strategy": SchedulingStrategy.CONSTITUTION_OPTIMIZED.value,
                    }
                )

            logger.info("调度策略优化分析完成")
            return optimization_results

        except Exception as e:
            logger.error(f"优化调度策略失败: {e}")
            return {}

    async def shutdown(self):
        """关闭调度服务"""
        try:
            # 停止监控
            await self.stop_monitoring()

            # 关闭线程池
            self.executor.shutdown(wait=True)

            logger.info("智能资源调度服务已关闭")

        except Exception as e:
            logger.error(f"关闭调度服务失败: {e}")
