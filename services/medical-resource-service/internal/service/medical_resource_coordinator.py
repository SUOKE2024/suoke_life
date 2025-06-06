"""
medical_resource_coordinator - 索克生活项目模块
"""

from ..agent.xiaoke_agent import XiaokeAgent
from .personalized_medical_service import PersonalizedMedicalService
from .quality_control_service import QualityControlService
from .resource_management_service import ResourceManagementService
from .resource_scheduling_service import ResourceSchedulingService
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import asyncio
import logging
import uuid

"""
医疗资源服务协调器
统一协调和管理所有医疗资源相关的服务模块
"""


# ConstitutionType import removed

logger = logging.getLogger(__name__)

class ServiceType(Enum):
    """服务类型"""

    RESOURCE_MANAGEMENT = "resource_management"
    RESOURCE_SCHEDULING = "resource_scheduling"
    PERSONALIZED_MEDICAL = "personalized_medical"
    QUALITY_CONTROL = "quality_control"
    XIAOKE_AGENT = "xiaoke_agent"

class RequestType(Enum):
    """请求类型"""

    CONSULTATION = "consultation"  # 咨询服务
    APPOINTMENT = "appointment"  # 预约服务
    TREATMENT_PLAN = "treatment_plan"  # 治疗方案
    RESOURCE_SEARCH = "resource_search"  # 资源搜索
    QUALITY_ASSESSMENT = "quality_assessment"  # 质量评估
    HEALTH_MONITORING = "health_monitoring"  # 健康监测

@dataclass
class ServiceRequest:
    """服务请求"""

    request_id: str
    user_id: str
    request_type: RequestType
    service_types: List[ServiceType]
    parameters: Dict[str, Any]
    priority: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    callback_url: Optional[str] = None

@dataclass
class ServiceResponse:
    """服务响应"""

    response_id: str
    request_id: str
    service_type: ServiceType
    status: str  # success, error, pending
    data: Dict[str, Any]
    error_message: Optional[str] = None
    processing_time: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ComprehensiveHealthPlan:
    """综合健康方案"""

    plan_id: str
    user_id: str
    constitution_type: ConstitutionType
    current_health_status: Dict[str, Any]
    recommended_resources: List[Dict[str, Any]]
    treatment_plans: List[Dict[str, Any]]
    appointment_schedule: List[Dict[str, Any]]
    quality_metrics: Dict[str, float]
    estimated_cost: float
    estimated_duration: timedelta
    success_probability: float
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

class MedicalResourceCoordinator:
    """
    医疗资源服务协调器

    统一协调资源管理、调度、个性化医疗和质量控制等服务
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.max_concurrent_requests = config.get("max_concurrent_requests", 100)
        self.request_timeout = config.get("request_timeout", 300)  # seconds

        # 服务实例
        self.resource_service: Optional[ResourceManagementService] = None
        self.scheduling_service: Optional[ResourceSchedulingService] = None
        self.medical_service: Optional[PersonalizedMedicalService] = None
        self.quality_service: Optional[QualityControlService] = None
        self.xiaoke_agent: Optional[XiaokeAgent] = None

        # 请求管理
        self.pending_requests: Dict[str, ServiceRequest] = {}
        self.request_queue = asyncio.Queue(maxsize=self.max_concurrent_requests)
        self.response_cache: Dict[str, ServiceResponse] = {}

        # 综合方案
        self.health_plans: Dict[str, ComprehensiveHealthPlan] = {}

        # 服务监控
        self.service_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "service_availability": {},
            "user_satisfaction": 0.0,
        }

        # 处理器状态
        self.is_running = False
        self.worker_tasks: List[asyncio.Task] = []

        logger.info("医疗资源协调器初始化完成")

    async def initialize(self):
        """初始化协调器"""
        try:
            # 初始化各个服务
            await self._initialize_services()

            # 启动请求处理器
            await self._start_request_processors()

            # 启动监控任务
            await self._start_monitoring()

            self.is_running = True
            logger.info("医疗资源协调器启动完成")

        except Exception as e:
            logger.error(f"协调器初始化失败: {e}")
            raise

    async def _initialize_services(self):
        """初始化各个服务"""
        try:
            # 初始化资源管理服务
            self.resource_service = ResourceManagementService(
                self.config.get("resource_management", {})
            )

            # 初始化调度服务
            self.scheduling_service = ResourceSchedulingService(
                self.config.get("resource_scheduling", {})
            )
            await self.scheduling_service.initialize()

            # 初始化个性化医疗服务
            self.medical_service = PersonalizedMedicalService(
                self.config.get("personalized_medical", {})
            )
            await self.medical_service.initialize()

            # 初始化质量控制服务
            self.quality_service = QualityControlService(
                self.config.get("quality_control", {})
            )
            await self.quality_service.initialize()

            # 初始化小克智能体
            self.xiaoke_agent = XiaokeAgent(self.config.get("xiaoke_agent", {}))
            await self.xiaoke_agent.initialize()

            logger.info("所有服务初始化完成")

        except Exception as e:
            logger.error(f"服务初始化失败: {e}")
            raise

    async def _start_request_processors(self):
        """启动请求处理器"""
        try:
            # 启动多个工作线程处理请求
            num_workers = self.config.get("num_workers", 4)

            for i in range(num_workers):
                task = asyncio.create_task(self._request_processor(f"worker_{i}"))
                self.worker_tasks.append(task)

            logger.info(f"启动了 {num_workers} 个请求处理器")

        except Exception as e:
            logger.error(f"启动请求处理器失败: {e}")
            raise

    async def _request_processor(self, worker_name: str):
        """请求处理器"""
        logger.info(f"请求处理器 {worker_name} 启动")

        while self.is_running:
            try:
                # 从队列获取请求
                request = await asyncio.wait_for(self.request_queue.get(), timeout=1.0)

                # 处理请求
                start_time = datetime.now()
                response = await self._process_request(request)
                processing_time = (datetime.now() - start_time).total_seconds()

                # 更新响应时间
                response.processing_time = processing_time

                # 缓存响应
                self.response_cache[response.response_id] = response

                # 更新统计
                self.service_stats["total_requests"] += 1
                if response.status == "success":
                    self.service_stats["successful_requests"] += 1
                else:
                    self.service_stats["failed_requests"] += 1

                # 更新平均响应时间
                self._update_average_response_time(processing_time)

                # 标记任务完成
                self.request_queue.task_done()

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"请求处理器 {worker_name} 错误: {e}")
                continue

    async def _process_request(self, request: ServiceRequest) -> ServiceResponse:
        """处理单个请求"""
        try:
            response_id = f"resp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

            # 根据请求类型路由到相应的处理方法
            if request.request_type == RequestType.CONSULTATION:
                result = await self._handle_consultation_request(request)
            elif request.request_type == RequestType.APPOINTMENT:
                result = await self._handle_appointment_request(request)
            elif request.request_type == RequestType.TREATMENT_PLAN:
                result = await self._handle_treatment_plan_request(request)
            elif request.request_type == RequestType.RESOURCE_SEARCH:
                result = await self._handle_resource_search_request(request)
            elif request.request_type == RequestType.QUALITY_ASSESSMENT:
                result = await self._handle_quality_assessment_request(request)
            elif request.request_type == RequestType.HEALTH_MONITORING:
                result = await self._handle_health_monitoring_request(request)
            else:
                raise ValueError(f"不支持的请求类型: {request.request_type}")

            return ServiceResponse(
                response_id=response_id,
                request_id=request.request_id,
                service_type=ServiceType.RESOURCE_MANAGEMENT,  # 主要服务类型
                status="success",
                data=result,
            )

        except Exception as e:
            logger.error(f"处理请求失败: {e}")
            return ServiceResponse(
                response_id=f"resp_error_{uuid.uuid4().hex[:8]}",
                request_id=request.request_id,
                service_type=ServiceType.RESOURCE_MANAGEMENT,
                status="error",
                data={},
                error_message=str(e),
            )

    async def submit_request(self, request: ServiceRequest) -> str:
        """提交服务请求"""
        try:
            # 验证请求
            await self._validate_request(request)

            # 添加到待处理队列
            self.pending_requests[request.request_id] = request

            # 放入处理队列
            await self.request_queue.put(request)

            logger.info(f"提交请求成功: {request.request_id}")
            return request.request_id

        except Exception as e:
            logger.error(f"提交请求失败: {e}")
            raise

    async def get_response(self, request_id: str) -> Optional[ServiceResponse]:
        """获取请求响应"""
        try:
            # 查找响应
            for response in self.response_cache.values():
                if response.request_id == request_id:
                    return response

            return None

        except Exception as e:
            logger.error(f"获取响应失败: {e}")
            raise

    async def create_comprehensive_health_plan(
        self,
        user_id: str,
        health_assessment: Dict[str, Any],
        preferences: Dict[str, Any] = None,
    ) -> ComprehensiveHealthPlan:
        """创建综合健康方案"""
        try:
            plan_id = (
                f"health_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}"
            )

            # 获取用户体质类型
            constitution_type = health_assessment.get("constitution_type")
            if not constitution_type:
                constitution_type = await self._assess_constitution(
                    user_id, health_assessment
                )

            # 分析当前健康状态
            health_status = await self._analyze_health_status(health_assessment)

            # 推荐医疗资源
            recommended_resources = await self._recommend_medical_resources(
                user_id, constitution_type, health_status, preferences
            )

            # 制定治疗方案
            treatment_plans = await self._create_treatment_plans(
                user_id, constitution_type, health_status
            )

            # 安排预约时间表
            appointment_schedule = await self._create_appointment_schedule(
                user_id, recommended_resources, treatment_plans
            )

            # 评估质量指标
            quality_metrics = await self._assess_plan_quality(
                recommended_resources, treatment_plans
            )

            # 估算费用和时间
            cost_estimate = await self._estimate_total_cost(
                recommended_resources, treatment_plans
            )
            duration_estimate = await self._estimate_total_duration(treatment_plans)

            # 预测成功概率
            success_probability = await self._predict_success_probability(
                constitution_type, health_status, treatment_plans
            )

            # 创建综合方案
            health_plan = ComprehensiveHealthPlan(
                plan_id=plan_id,
                user_id=user_id,
                constitution_type=constitution_type,
                current_health_status=health_status,
                recommended_resources=recommended_resources,
                treatment_plans=treatment_plans,
                appointment_schedule=appointment_schedule,
                quality_metrics=quality_metrics,
                estimated_cost=cost_estimate,
                estimated_duration=duration_estimate,
                success_probability=success_probability,
            )

            self.health_plans[plan_id] = health_plan

            logger.info(f"综合健康方案创建完成: {plan_id}")
            return health_plan

        except Exception as e:
            logger.error(f"创建综合健康方案失败: {e}")
            raise

    async def _handle_consultation_request(
        self, request: ServiceRequest
    ) -> Dict[str, Any]:
        """处理咨询请求"""
        try:
            user_id = request.parameters.get("user_id")
            symptoms = request.parameters.get("symptoms", [])
            constitution_type = request.parameters.get("constitution_type")

            # 使用小克智能体进行初步分析
            consultation_result = await self.xiaoke_agent.provide_consultation(
                user_id=user_id, symptoms=symptoms, constitution_type=constitution_type
            )

            # 分析症状并推荐资源
            if symptoms:
                symptom_analysis = await self.medical_service.analyze_symptoms(
                    user_id, symptoms
                )
                consultation_result["symptom_analysis"] = symptom_analysis

            # 推荐医疗资源
            if constitution_type:
                resource_recommendations = await self.resource_service.search_resources(
                    constitution_type=constitution_type,
                    keywords=" ".join(symptoms) if symptoms else None,
                )
                consultation_result["resource_recommendations"] = (
                    resource_recommendations
                )

            return consultation_result

        except Exception as e:
            logger.error(f"处理咨询请求失败: {e}")
            raise

    async def _handle_appointment_request(
        self, request: ServiceRequest
    ) -> Dict[str, Any]:
        """处理预约请求"""
        try:
            user_id = request.parameters.get("user_id")
            resource_id = request.parameters.get("resource_id")
            preferred_time = request.parameters.get("preferred_time")
            appointment_type = request.parameters.get("appointment_type")

            # 创建预约请求
            appointment_request_id = (
                await self.scheduling_service.create_appointment_request(
                    user_id=user_id,
                    appointment_type=appointment_type,
                    preferred_resources=[resource_id] if resource_id else [],
                    **request.parameters,
                )
            )

            # 尝试调度预约
            appointment_id = await self.scheduling_service.schedule_appointment(
                appointment_request_id
            )

            result = {
                "appointment_request_id": appointment_request_id,
                "appointment_id": appointment_id,
                "status": "scheduled" if appointment_id else "pending",
            }

            # 如果预约成功，获取详细信息
            if appointment_id:
                appointment_details = (
                    await self.scheduling_service.get_appointment_details(
                        appointment_id
                    )
                )
                result["appointment_details"] = appointment_details

            return result

        except Exception as e:
            logger.error(f"处理预约请求失败: {e}")
            raise

    async def _handle_treatment_plan_request(
        self, request: ServiceRequest
    ) -> Dict[str, Any]:
        """处理治疗方案请求"""
        try:
            user_id = request.parameters.get("user_id")
            symptoms = request.parameters.get("symptoms", [])
            constitution_type = request.parameters.get("constitution_type")
            treatment_approach = request.parameters.get("treatment_approach")

            # 分析症状
            symptom_analyses = await self.medical_service.analyze_symptoms(
                user_id, symptoms
            )

            # 识别证候模式
            syndrome_patterns = await self.medical_service.identify_syndrome_patterns(
                user_id, symptom_analyses, constitution_type
            )

            # 生成治疗方案
            treatment_plan = await self.medical_service.generate_treatment_plan(
                user_id, syndrome_patterns, treatment_approach
            )

            # 推荐诊断检查
            diagnostic_recommendations = (
                await self.medical_service.recommend_diagnostics(
                    user_id, syndrome_patterns, symptom_analyses
                )
            )

            return {
                "symptom_analyses": symptom_analyses,
                "syndrome_patterns": syndrome_patterns,
                "treatment_plan": treatment_plan,
                "diagnostic_recommendations": diagnostic_recommendations,
            }

        except Exception as e:
            logger.error(f"处理治疗方案请求失败: {e}")
            raise

    async def _handle_resource_search_request(
        self, request: ServiceRequest
    ) -> Dict[str, Any]:
        """处理资源搜索请求"""
        try:
            search_results = await self.resource_service.search_resources(
                **request.parameters
            )

            # 为每个资源添加质量评估
            for resource in search_results.get("resources", []):
                quality_assessment = await self.quality_service.assess_resource_quality(
                    resource["resource_id"]
                )
                resource["quality_assessment"] = quality_assessment

            return search_results

        except Exception as e:
            logger.error(f"处理资源搜索请求失败: {e}")
            raise

    async def _handle_quality_assessment_request(
        self, request: ServiceRequest
    ) -> Dict[str, Any]:
        """处理质量评估请求"""
        try:
            resource_id = request.parameters.get("resource_id")
            service_id = request.parameters.get("service_id")

            if resource_id:
                assessment = await self.quality_service.assess_resource_quality(
                    resource_id
                )
            elif service_id:
                assessment = await self.quality_service.assess_service_quality(
                    service_id
                )
            else:
                raise ValueError("必须提供resource_id或service_id")

            return {"quality_assessment": assessment}

        except Exception as e:
            logger.error(f"处理质量评估请求失败: {e}")
            raise

    async def _handle_health_monitoring_request(
        self, request: ServiceRequest
    ) -> Dict[str, Any]:
        """处理健康监测请求"""
        try:
            user_id = request.parameters.get("user_id")
            monitoring_data = request.parameters.get("monitoring_data", {})

            # 使用小克智能体分析健康数据
            analysis_result = await self.xiaoke_agent.analyze_health_data(
                user_id, monitoring_data
            )

            # 如果发现异常，推荐相应的医疗资源
            if analysis_result.get("anomalies"):
                resource_recommendations = (
                    await self._recommend_resources_for_anomalies(
                        user_id, analysis_result["anomalies"]
                    )
                )
                analysis_result["resource_recommendations"] = resource_recommendations

            return analysis_result

        except Exception as e:
            logger.error(f"处理健康监测请求失败: {e}")
            raise

    async def get_service_statistics(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        try:
            # 收集各个服务的统计信息
            resource_stats = await self.resource_service.get_resource_statistics()
            scheduling_stats = await self.scheduling_service.get_scheduling_statistics()
            medical_stats = await self.medical_service.get_treatment_statistics()
            quality_stats = await self.quality_service.get_quality_statistics()

            return {
                "coordinator_stats": self.service_stats,
                "resource_management": resource_stats,
                "resource_scheduling": scheduling_stats,
                "personalized_medical": medical_stats,
                "quality_control": quality_stats,
                "total_health_plans": len(self.health_plans),
                "active_requests": len(self.pending_requests),
                "cached_responses": len(self.response_cache),
            }

        except Exception as e:
            logger.error(f"获取服务统计失败: {e}")
            raise

    async def shutdown(self):
        """关闭协调器"""
        try:
            self.is_running = False

            # 等待所有工作任务完成
            if self.worker_tasks:
                await asyncio.gather(*self.worker_tasks, return_exceptions=True)

            # 关闭各个服务
            if self.scheduling_service:
                await self.scheduling_service.shutdown()

            if self.medical_service:
                await self.medical_service.shutdown()

            if self.quality_service:
                await self.quality_service.shutdown()

            if self.xiaoke_agent:
                await self.xiaoke_agent.shutdown()

            logger.info("医疗资源协调器已关闭")

        except Exception as e:
            logger.error(f"关闭协调器失败: {e}")
            raise
