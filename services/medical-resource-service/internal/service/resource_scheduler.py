"""
resource_scheduler - 索克生活项目模块
"""

from ..domain.models import (
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import heapq
import logging

"""
资源调度引擎模块
实现智能资源分配和调度优化功能
"""


    Appointment,
    ConstitutionType,
    Doctor,
    Equipment,
    MedicalInstitution,
    Resource,
    ResourceType,
    UrgencyLevel,
)

logger = logging.getLogger(__name__)

class SchedulingStrategy(Enum):
    """调度策略"""

    FIFO = "fifo"  # 先进先出
    PRIORITY = "priority"  # 优先级调度
    SHORTEST_JOB = "shortest_job"  # 最短作业优先
    ROUND_ROBIN = "round_robin"  # 轮转调度
    CONSTITUTION_BASED = "constitution_based"  # 基于体质的调度
    LOAD_BALANCING = "load_balancing"  # 负载均衡

class ResourceStatus(Enum):
    """资源状态"""

    AVAILABLE = "available"  # 可用
    BUSY = "busy"  # 忙碌
    MAINTENANCE = "maintenance"  # 维护中
    OFFLINE = "offline"  # 离线

@dataclass
class SchedulingRequest:
    """调度请求"""

    request_id: str
    user_id: str
    constitution_type: ConstitutionType
    urgency_level: UrgencyLevel
    resource_type: ResourceType
    required_specialties: List[str]
    preferred_time: datetime
    duration_minutes: int
    location_preference: Optional[str]
    special_requirements: List[str]
    created_at: datetime
    deadline: Optional[datetime]

@dataclass
class SchedulingResult:
    """调度结果"""

    request_id: str
    allocated_resource: Optional[Resource]
    scheduled_time: Optional[datetime]
    estimated_duration: int
    confidence_score: float
    alternative_options: List[Dict[str, Any]]
    scheduling_reason: str
    created_at: datetime

@dataclass
class ResourceLoad:
    """资源负载"""

    resource_id: str
    current_load: float
    capacity: int
    utilization_rate: float
    queue_length: int
    average_wait_time: float
    last_updated: datetime

@dataclass
class SchedulingMetrics:
    """调度指标"""

    total_requests: int
    successful_allocations: int
    average_wait_time: float
    resource_utilization: Dict[str, float]
    constitution_distribution: Dict[ConstitutionType, int]
    urgency_distribution: Dict[UrgencyLevel, int]
    satisfaction_score: float
    optimization_score: float

class ResourceScheduler:
    """
    资源调度引擎

    实现智能资源分配和调度优化
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config

        # 调度策略
        self.default_strategy = SchedulingStrategy(
            config.get("default_strategy", "constitution_based")
        )

        # 资源池
        self.resource_pool: Dict[str, Resource] = {}
        self.resource_status: Dict[str, ResourceStatus] = {}
        self.resource_loads: Dict[str, ResourceLoad] = {}

        # 调度队列
        self.scheduling_queue: List[SchedulingRequest] = []
        self.priority_queue: List[Tuple[int, SchedulingRequest]] = []

        # 调度历史
        self.scheduling_history: List[SchedulingResult] = []

        # 体质-资源匹配权重
        self.constitution_resource_weights = self._initialize_constitution_weights()

        # 调度算法
        self.scheduling_algorithms = {
            SchedulingStrategy.FIFO: self._fifo_scheduling,
            SchedulingStrategy.PRIORITY: self._priority_scheduling,
            SchedulingStrategy.SHORTEST_JOB: self._shortest_job_scheduling,
            SchedulingStrategy.ROUND_ROBIN: self._round_robin_scheduling,
            SchedulingStrategy.CONSTITUTION_BASED: self._constitution_based_scheduling,
            SchedulingStrategy.LOAD_BALANCING: self._load_balancing_scheduling,
        }

        # 性能指标
        self.metrics = SchedulingMetrics(
            total_requests=0,
            successful_allocations=0,
            average_wait_time=0.0,
            resource_utilization={},
            constitution_distribution={},
            urgency_distribution={},
            satisfaction_score=0.0,
            optimization_score=0.0,
        )

        logger.info("资源调度引擎初始化完成")

    def _initialize_constitution_weights(
        self,
    ) -> Dict[ConstitutionType, Dict[str, float]]:
        """初始化体质-资源匹配权重"""
        weights = {}

        # 气虚体质权重
        weights[ConstitutionType.QI_XU] = {
            "中医科": 0.9,
            "康复科": 0.8,
            "营养科": 0.7,
            "内科": 0.6,
            "针灸科": 0.8,
            "推拿科": 0.7,
        }

        # 阳虚体质权重
        weights[ConstitutionType.YANG_XU] = {
            "中医科": 0.9,
            "肾内科": 0.7,
            "内分泌科": 0.6,
            "针灸科": 0.8,
            "艾灸": 0.9,
            "温泉疗法": 0.8,
        }

        # 阴虚体质权重
        weights[ConstitutionType.YIN_XU] = {
            "中医科": 0.9,
            "肾内科": 0.7,
            "皮肤科": 0.6,
            "眼科": 0.5,
            "滋阴疗法": 0.9,
            "水疗": 0.7,
        }

        # 痰湿体质权重
        weights[ConstitutionType.TAN_SHI] = {
            "中医科": 0.9,
            "内分泌科": 0.8,
            "消化科": 0.7,
            "减重科": 0.8,
            "运动疗法": 0.8,
            "饮食调理": 0.9,
        }

        # 湿热体质权重
        weights[ConstitutionType.SHI_RE] = {
            "中医科": 0.9,
            "皮肤科": 0.8,
            "消化科": 0.7,
            "泌尿科": 0.6,
            "清热疗法": 0.9,
            "凉茶调理": 0.8,
        }

        # 血瘀体质权重
        weights[ConstitutionType.XUE_YU] = {
            "中医科": 0.9,
            "心血管科": 0.8,
            "血液科": 0.7,
            "针灸科": 0.8,
            "活血疗法": 0.9,
            "按摩推拿": 0.8,
        }

        # 气郁体质权重
        weights[ConstitutionType.QI_YU] = {
            "中医科": 0.9,
            "心理科": 0.8,
            "神经科": 0.6,
            "精神科": 0.7,
            "疏肝理气": 0.9,
            "心理疏导": 0.8,
        }

        # 特禀体质权重
        weights[ConstitutionType.TE_BING] = {
            "中医科": 0.9,
            "过敏科": 0.8,
            "免疫科": 0.8,
            "皮肤科": 0.7,
            "脱敏疗法": 0.9,
            "免疫调节": 0.8,
        }

        # 平和体质权重
        weights[ConstitutionType.PING_HE] = {
            "中医科": 0.7,
            "预防保健": 0.9,
            "健康体检": 0.8,
            "养生指导": 0.8,
            "运动指导": 0.7,
            "营养咨询": 0.7,
        }

        return weights

    async def add_resource(self, resource: Resource) -> bool:
        """添加资源到资源池"""
        try:
            self.resource_pool[resource.resource_id] = resource
            self.resource_status[resource.resource_id] = ResourceStatus.AVAILABLE

            # 初始化资源负载
            self.resource_loads[resource.resource_id] = ResourceLoad(
                resource_id=resource.resource_id,
                current_load=0.0,
                capacity=getattr(resource, "capacity", 10),
                utilization_rate=0.0,
                queue_length=0,
                average_wait_time=0.0,
                last_updated=datetime.now(),
            )

            logger.info(f"资源 {resource.resource_id} 已添加到资源池")
            return True

        except Exception as e:
            logger.error(f"添加资源失败: {e}")
            return False

    async def remove_resource(self, resource_id: str) -> bool:
        """从资源池移除资源"""
        try:
            if resource_id in self.resource_pool:
                del self.resource_pool[resource_id]
                del self.resource_status[resource_id]
                del self.resource_loads[resource_id]

                logger.info(f"资源 {resource_id} 已从资源池移除")
                return True

            return False

        except Exception as e:
            logger.error(f"移除资源失败: {e}")
            return False

    async def update_resource_status(
        self, resource_id: str, status: ResourceStatus
    ) -> bool:
        """更新资源状态"""
        try:
            if resource_id in self.resource_status:
                self.resource_status[resource_id] = status
                logger.info(f"资源 {resource_id} 状态更新为 {status.value}")
                return True

            return False

        except Exception as e:
            logger.error(f"更新资源状态失败: {e}")
            return False

    async def submit_scheduling_request(self, request: SchedulingRequest) -> str:
        """提交调度请求"""
        try:
            # 添加到调度队列
            self.scheduling_queue.append(request)

            # 如果是高优先级，添加到优先队列
            if request.urgency_level in [UrgencyLevel.EMERGENCY, UrgencyLevel.URGENT]:
                priority = self._calculate_priority(request)
                heapq.heappush(self.priority_queue, (priority, request))

            # 更新指标
            self.metrics.total_requests += 1
            self.metrics.urgency_distribution[request.urgency_level] = (
                self.metrics.urgency_distribution.get(request.urgency_level, 0) + 1
            )
            self.metrics.constitution_distribution[request.constitution_type] = (
                self.metrics.constitution_distribution.get(request.constitution_type, 0)
                + 1
            )

            logger.info(f"调度请求 {request.request_id} 已提交")
            return request.request_id

        except Exception as e:
            logger.error(f"提交调度请求失败: {e}")
            raise

    def _calculate_priority(self, request: SchedulingRequest) -> int:
        """计算请求优先级（数值越小优先级越高）"""
        priority = 100

        # 紧急程度
        if request.urgency_level == UrgencyLevel.EMERGENCY:
            priority -= 50
        elif request.urgency_level == UrgencyLevel.URGENT:
            priority -= 30
        elif request.urgency_level == UrgencyLevel.NORMAL:
            priority -= 10

        # 等待时间
        wait_time = (datetime.now() - request.created_at).total_seconds() / 3600
        priority -= int(wait_time * 5)  # 每小时减5分

        # 截止时间
        if request.deadline:
            time_to_deadline = (
                request.deadline - datetime.now()
            ).total_seconds() / 3600
            if time_to_deadline < 24:  # 24小时内
                priority -= 20
            elif time_to_deadline < 72:  # 72小时内
                priority -= 10

        return max(priority, 1)  # 确保优先级至少为1

    async def schedule_resources(
        self, strategy: Optional[SchedulingStrategy] = None
    ) -> List[SchedulingResult]:
        """执行资源调度"""
        try:
            if not self.scheduling_queue:
                return []

            strategy = strategy or self.default_strategy
            algorithm = self.scheduling_algorithms.get(strategy)

            if not algorithm:
                raise ValueError(f"不支持的调度策略: {strategy}")

            results = await algorithm()

            # 更新调度历史
            self.scheduling_history.extend(results)

            # 更新性能指标
            await self._update_metrics(results)

            logger.info(f"使用 {strategy.value} 策略完成 {len(results)} 个调度")
            return results

        except Exception as e:
            logger.error(f"资源调度失败: {e}")
            return []

    async def _fifo_scheduling(self) -> List[SchedulingResult]:
        """先进先出调度"""
        results = []

        while self.scheduling_queue:
            request = self.scheduling_queue.pop(0)
            result = await self._allocate_resource(request)
            results.append(result)

        return results

    async def _priority_scheduling(self) -> List[SchedulingResult]:
        """优先级调度"""
        results = []

        # 先处理优先队列
        while self.priority_queue:
            _, request = heapq.heappop(self.priority_queue)
            result = await self._allocate_resource(request)
            results.append(result)

            # 从普通队列中移除
            if request in self.scheduling_queue:
                self.scheduling_queue.remove(request)

        # 再处理普通队列
        while self.scheduling_queue:
            request = self.scheduling_queue.pop(0)
            result = await self._allocate_resource(request)
            results.append(result)

        return results

    async def _shortest_job_scheduling(self) -> List[SchedulingResult]:
        """最短作业优先调度"""
        # 按持续时间排序
        self.scheduling_queue.sort(key=lambda x: x.duration_minutes)

        results = []
        while self.scheduling_queue:
            request = self.scheduling_queue.pop(0)
            result = await self._allocate_resource(request)
            results.append(result)

        return results

    async def _round_robin_scheduling(self) -> List[SchedulingResult]:
        """轮转调度"""
        results = []
        available_resources = [
            rid
            for rid, status in self.resource_status.items()
            if status == ResourceStatus.AVAILABLE
        ]

        resource_index = 0

        while self.scheduling_queue:
            request = self.scheduling_queue.pop(0)

            if available_resources:
                # 轮转分配资源
                resource_id = available_resources[
                    resource_index % len(available_resources)
                ]
                resource = self.resource_pool[resource_id]

                result = SchedulingResult(
                    request_id=request.request_id,
                    allocated_resource=resource,
                    scheduled_time=request.preferred_time,
                    estimated_duration=request.duration_minutes,
                    confidence_score=0.7,
                    alternative_options=[],
                    scheduling_reason=f"轮转调度分配到资源 {resource_id}",
                    created_at=datetime.now(),
                )

                resource_index += 1
            else:
                result = SchedulingResult(
                    request_id=request.request_id,
                    allocated_resource=None,
                    scheduled_time=None,
                    estimated_duration=request.duration_minutes,
                    confidence_score=0.0,
                    alternative_options=[],
                    scheduling_reason="无可用资源",
                    created_at=datetime.now(),
                )

            results.append(result)

        return results

    async def _constitution_based_scheduling(self) -> List[SchedulingResult]:
        """基于体质的调度"""
        results = []

        while self.scheduling_queue:
            request = self.scheduling_queue.pop(0)

            # 根据体质匹配最佳资源
            best_resource = await self._find_best_resource_for_constitution(
                request.constitution_type,
                request.resource_type,
                request.required_specialties,
            )

            if best_resource:
                # 计算最佳时间
                optimal_time = await self._calculate_optimal_time(
                    best_resource, request.preferred_time, request.duration_minutes
                )

                # 计算置信度
                confidence = await self._calculate_constitution_match_confidence(
                    request.constitution_type, best_resource
                )

                # 生成替代选项
                alternatives = await self._generate_alternative_options(
                    request, exclude_resource=best_resource.resource_id
                )

                result = SchedulingResult(
                    request_id=request.request_id,
                    allocated_resource=best_resource,
                    scheduled_time=optimal_time,
                    estimated_duration=request.duration_minutes,
                    confidence_score=confidence,
                    alternative_options=alternatives,
                    scheduling_reason=f"基于{request.constitution_type.value}体质匹配",
                    created_at=datetime.now(),
                )

                # 更新资源负载
                await self._update_resource_load(
                    best_resource.resource_id, request.duration_minutes
                )

            else:
                result = SchedulingResult(
                    request_id=request.request_id,
                    allocated_resource=None,
                    scheduled_time=None,
                    estimated_duration=request.duration_minutes,
                    confidence_score=0.0,
                    alternative_options=[],
                    scheduling_reason="未找到匹配的资源",
                    created_at=datetime.now(),
                )

            results.append(result)

        return results

    async def _load_balancing_scheduling(self) -> List[SchedulingResult]:
        """负载均衡调度"""
        results = []

        while self.scheduling_queue:
            request = self.scheduling_queue.pop(0)

            # 找到负载最低的可用资源
            best_resource = await self._find_least_loaded_resource(
                request.resource_type, request.required_specialties
            )

            if best_resource:
                # 计算调度时间
                scheduled_time = await self._calculate_earliest_available_time(
                    best_resource, request.duration_minutes
                )

                result = SchedulingResult(
                    request_id=request.request_id,
                    allocated_resource=best_resource,
                    scheduled_time=scheduled_time,
                    estimated_duration=request.duration_minutes,
                    confidence_score=0.8,
                    alternative_options=[],
                    scheduling_reason="负载均衡分配",
                    created_at=datetime.now(),
                )

                # 更新资源负载
                await self._update_resource_load(
                    best_resource.resource_id, request.duration_minutes
                )

            else:
                result = SchedulingResult(
                    request_id=request.request_id,
                    allocated_resource=None,
                    scheduled_time=None,
                    estimated_duration=request.duration_minutes,
                    confidence_score=0.0,
                    alternative_options=[],
                    scheduling_reason="无可用资源",
                    created_at=datetime.now(),
                )

            results.append(result)

        return results

    async def _allocate_resource(self, request: SchedulingRequest) -> SchedulingResult:
        """分配资源（通用方法）"""
        # 根据请求类型和体质找到最佳资源
        best_resource = await self._find_best_resource_for_constitution(
            request.constitution_type,
            request.resource_type,
            request.required_specialties,
        )

        if best_resource:
            # 计算最佳时间
            optimal_time = await self._calculate_optimal_time(
                best_resource, request.preferred_time, request.duration_minutes
            )

            # 计算置信度
            confidence = await self._calculate_constitution_match_confidence(
                request.constitution_type, best_resource
            )

            result = SchedulingResult(
                request_id=request.request_id,
                allocated_resource=best_resource,
                scheduled_time=optimal_time,
                estimated_duration=request.duration_minutes,
                confidence_score=confidence,
                alternative_options=[],
                scheduling_reason="智能匹配分配",
                created_at=datetime.now(),
            )

            # 更新资源负载
            await self._update_resource_load(
                best_resource.resource_id, request.duration_minutes
            )

        else:
            result = SchedulingResult(
                request_id=request.request_id,
                allocated_resource=None,
                scheduled_time=None,
                estimated_duration=request.duration_minutes,
                confidence_score=0.0,
                alternative_options=[],
                scheduling_reason="无匹配资源",
                created_at=datetime.now(),
            )

        return result

    async def _find_best_resource_for_constitution(
        self,
        constitution_type: ConstitutionType,
        resource_type: ResourceType,
        required_specialties: List[str],
    ) -> Optional[Resource]:
        """为特定体质找到最佳资源"""
        best_resource = None
        best_score = 0.0

        constitution_weights = self.constitution_resource_weights.get(
            constitution_type, {}
        )

        for resource_id, resource in self.resource_pool.items():
            # 检查资源状态
            if self.resource_status[resource_id] != ResourceStatus.AVAILABLE:
                continue

            # 检查资源类型
            if resource.resource_type != resource_type:
                continue

            # 计算匹配分数
            score = 0.0

            # 专业匹配
            if hasattr(resource, "specialties"):
                for specialty in resource.specialties:
                    if specialty in required_specialties:
                        score += 0.3

                    # 体质权重
                    weight = constitution_weights.get(specialty, 0.0)
                    score += weight * 0.5

            # 负载考虑
            load = self.resource_loads.get(resource_id)
            if load:
                load_penalty = load.utilization_rate * 0.2
                score -= load_penalty

            # 评分考虑
            if hasattr(resource, "rating"):
                score += resource.rating * 0.1

            if score > best_score:
                best_score = score
                best_resource = resource

        return best_resource

    async def _find_least_loaded_resource(
        self, resource_type: ResourceType, required_specialties: List[str]
    ) -> Optional[Resource]:
        """找到负载最低的资源"""
        best_resource = None
        lowest_load = float("inf")

        for resource_id, resource in self.resource_pool.items():
            # 检查资源状态
            if self.resource_status[resource_id] != ResourceStatus.AVAILABLE:
                continue

            # 检查资源类型
            if resource.resource_type != resource_type:
                continue

            # 检查专业匹配
            if hasattr(resource, "specialties") and required_specialties:
                if not any(
                    spec in resource.specialties for spec in required_specialties
                ):
                    continue

            # 获取负载
            load = self.resource_loads.get(resource_id)
            if load and load.current_load < lowest_load:
                lowest_load = load.current_load
                best_resource = resource

        return best_resource

    async def _calculate_optimal_time(
        self, resource: Resource, preferred_time: datetime, duration_minutes: int
    ) -> datetime:
        """计算最优调度时间"""
        # 简化实现：返回首选时间或最早可用时间
        earliest_time = await self._calculate_earliest_available_time(
            resource, duration_minutes
        )

        if earliest_time <= preferred_time:
            return preferred_time
        else:
            return earliest_time

    async def _calculate_earliest_available_time(
        self, resource: Resource, duration_minutes: int
    ) -> datetime:
        """计算最早可用时间"""
        # 简化实现：基于当前负载估算
        load = self.resource_loads.get(resource.resource_id)

        if load:
            # 基于队列长度和平均等待时间估算
            estimated_wait = load.queue_length * load.average_wait_time
            return datetime.now() + timedelta(minutes=estimated_wait)

        return datetime.now()

    async def _calculate_constitution_match_confidence(
        self, constitution_type: ConstitutionType, resource: Resource
    ) -> float:
        """计算体质匹配置信度"""
        constitution_weights = self.constitution_resource_weights.get(
            constitution_type, {}
        )

        if not hasattr(resource, "specialties"):
            return 0.5  # 默认置信度

        total_weight = 0.0
        matched_weight = 0.0

        for specialty in resource.specialties:
            weight = constitution_weights.get(specialty, 0.1)
            total_weight += weight
            matched_weight += weight

        if total_weight > 0:
            confidence = matched_weight / total_weight
            return min(confidence, 1.0)

        return 0.5

    async def _generate_alternative_options(
        self, request: SchedulingRequest, exclude_resource: str
    ) -> List[Dict[str, Any]]:
        """生成替代选项"""
        alternatives = []

        for resource_id, resource in self.resource_pool.items():
            if resource_id == exclude_resource:
                continue

            if self.resource_status[resource_id] != ResourceStatus.AVAILABLE:
                continue

            if resource.resource_type != request.resource_type:
                continue

            # 计算匹配度
            confidence = await self._calculate_constitution_match_confidence(
                request.constitution_type, resource
            )

            # 计算可用时间
            available_time = await self._calculate_earliest_available_time(
                resource, request.duration_minutes
            )

            alternative = {
                "resource_id": resource_id,
                "resource_name": getattr(resource, "name", resource_id),
                "confidence_score": confidence,
                "available_time": available_time,
                "estimated_wait": (available_time - datetime.now()).total_seconds()
                / 60,
            }

            alternatives.append(alternative)

        # 按置信度排序
        alternatives.sort(key=lambda x: x["confidence_score"], reverse=True)

        return alternatives[:3]  # 返回前3个替代选项

    async def _update_resource_load(self, resource_id: str, duration_minutes: int):
        """更新资源负载"""
        if resource_id in self.resource_loads:
            load = self.resource_loads[resource_id]

            # 更新当前负载
            load.current_load += duration_minutes / 60.0  # 转换为小时

            # 更新利用率
            if load.capacity > 0:
                load.utilization_rate = min(load.current_load / load.capacity, 1.0)

            # 更新队列长度
            load.queue_length += 1

            # 更新平均等待时间（简化计算）
            load.average_wait_time = load.current_load * 60 / max(load.capacity, 1)

            load.last_updated = datetime.now()

    async def _update_metrics(self, results: List[SchedulingResult]):
        """更新性能指标"""
        successful_count = sum(1 for r in results if r.allocated_resource is not None)
        self.metrics.successful_allocations += successful_count

        # 计算平均等待时间
        wait_times = []
        for result in results:
            if result.scheduled_time:
                # 假设请求创建时间作为等待开始时间
                wait_time = (
                    result.scheduled_time - result.created_at
                ).total_seconds() / 60
                wait_times.append(wait_time)

        if wait_times:
            self.metrics.average_wait_time = sum(wait_times) / len(wait_times)

        # 更新资源利用率
        for resource_id, load in self.resource_loads.items():
            self.metrics.resource_utilization[resource_id] = load.utilization_rate

        # 计算满意度分数（基于成功分配率和置信度）
        if self.metrics.total_requests > 0:
            success_rate = (
                self.metrics.successful_allocations / self.metrics.total_requests
            )
            avg_confidence = (
                sum(r.confidence_score for r in results) / len(results)
                if results
                else 0
            )
            self.metrics.satisfaction_score = (success_rate + avg_confidence) / 2

        # 计算优化分数（基于资源利用率均衡性）
        if self.metrics.resource_utilization:
            utilizations = list(self.metrics.resource_utilization.values())
            avg_utilization = sum(utilizations) / len(utilizations)
            variance = sum((u - avg_utilization) ** 2 for u in utilizations) / len(
                utilizations
            )
            self.metrics.optimization_score = max(
                0, 1 - variance
            )  # 方差越小，优化分数越高

    async def get_resource_status(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """获取资源状态"""
        if resource_id not in self.resource_pool:
            return None

        resource = self.resource_pool[resource_id]
        status = self.resource_status[resource_id]
        load = self.resource_loads.get(resource_id)

        return {
            "resource_id": resource_id,
            "resource_type": resource.resource_type.value,
            "status": status.value,
            "load": (
                {
                    "current_load": load.current_load if load else 0,
                    "utilization_rate": load.utilization_rate if load else 0,
                    "queue_length": load.queue_length if load else 0,
                    "average_wait_time": load.average_wait_time if load else 0,
                }
                if load
                else None
            ),
            "last_updated": load.last_updated if load else None,
        }

    async def get_scheduling_metrics(self) -> Dict[str, Any]:
        """获取调度指标"""
        return {
            "total_requests": self.metrics.total_requests,
            "successful_allocations": self.metrics.successful_allocations,
            "success_rate": (
                self.metrics.successful_allocations / self.metrics.total_requests
                if self.metrics.total_requests > 0
                else 0
            ),
            "average_wait_time_minutes": self.metrics.average_wait_time,
            "resource_utilization": self.metrics.resource_utilization,
            "constitution_distribution": {
                k.value: v for k, v in self.metrics.constitution_distribution.items()
            },
            "urgency_distribution": {
                k.value: v for k, v in self.metrics.urgency_distribution.items()
            },
            "satisfaction_score": self.metrics.satisfaction_score,
            "optimization_score": self.metrics.optimization_score,
            "queue_length": len(self.scheduling_queue),
            "priority_queue_length": len(self.priority_queue),
        }

    async def optimize_scheduling(self) -> Dict[str, Any]:
        """优化调度策略"""
        try:
            # 分析历史数据
            if len(self.scheduling_history) < 10:
                return {"message": "数据不足，无法优化"}

            # 分析不同策略的效果
            strategy_performance = {}

            for strategy in SchedulingStrategy:
                # 模拟使用该策略的效果
                simulated_results = await self._simulate_strategy(strategy)
                strategy_performance[strategy.value] = simulated_results

            # 找到最佳策略
            best_strategy = max(
                strategy_performance.items(), key=lambda x: x[1]["optimization_score"]
            )

            # 更新默认策略
            self.default_strategy = SchedulingStrategy(best_strategy[0])

            return {
                "optimized_strategy": best_strategy[0],
                "performance_improvement": best_strategy[1]["optimization_score"],
                "strategy_comparison": strategy_performance,
            }

        except Exception as e:
            logger.error(f"调度优化失败: {e}")
            return {"error": str(e)}

    async def _simulate_strategy(
        self, strategy: SchedulingStrategy
    ) -> Dict[str, float]:
        """模拟调度策略效果"""
        # 简化的模拟实现
        # 在实际应用中，这里应该使用历史数据进行更复杂的模拟

        base_scores = {
            SchedulingStrategy.FIFO: {"success_rate": 0.7, "optimization_score": 0.6},
            SchedulingStrategy.PRIORITY: {
                "success_rate": 0.8,
                "optimization_score": 0.7,
            },
            SchedulingStrategy.SHORTEST_JOB: {
                "success_rate": 0.75,
                "optimization_score": 0.65,
            },
            SchedulingStrategy.ROUND_ROBIN: {
                "success_rate": 0.72,
                "optimization_score": 0.8,
            },
            SchedulingStrategy.CONSTITUTION_BASED: {
                "success_rate": 0.85,
                "optimization_score": 0.9,
            },
            SchedulingStrategy.LOAD_BALANCING: {
                "success_rate": 0.78,
                "optimization_score": 0.85,
            },
        }

        return base_scores.get(
            strategy, {"success_rate": 0.5, "optimization_score": 0.5}
        )

    def get_service_statistics(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        return {
            "total_resources": len(self.resource_pool),
            "available_resources": sum(
                1
                for status in self.resource_status.values()
                if status == ResourceStatus.AVAILABLE
            ),
            "resource_types": list(
                set(
                    resource.resource_type.value
                    for resource in self.resource_pool.values()
                )
            ),
            "scheduling_strategies": [
                strategy.value for strategy in SchedulingStrategy
            ],
            "current_strategy": self.default_strategy.value,
            "queue_status": {
                "normal_queue": len(self.scheduling_queue),
                "priority_queue": len(self.priority_queue),
            },
            "performance_metrics": {
                "total_requests": self.metrics.total_requests,
                "success_rate": (
                    self.metrics.successful_allocations / self.metrics.total_requests
                    if self.metrics.total_requests > 0
                    else 0
                ),
                "average_wait_time": self.metrics.average_wait_time,
                "satisfaction_score": self.metrics.satisfaction_score,
            },
        }
