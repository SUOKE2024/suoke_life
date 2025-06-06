"""
resource_management_service - 索克生活项目模块
"""

from ..domain.models import ResourceType
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
import logging
import uuid

"""
医疗资源统一管理服务
负责中医师、现代医疗机构、设备、药材等各类医疗资源的统一管理
"""



logger = logging.getLogger(__name__)

class ResourceCategory(Enum):
    """资源类别"""

    TCM_DOCTOR = "tcm_doctor"  # 中医师
    MODERN_DOCTOR = "modern_doctor"  # 现代医生
    MEDICAL_FACILITY = "medical_facility"  # 医疗机构
    MEDICAL_EQUIPMENT = "medical_equipment"  # 医疗设备
    HERBAL_MEDICINE = "herbal_medicine"  # 中药材
    MODERN_MEDICINE = "modern_medicine"  # 现代药物
    AGRICULTURAL_PRODUCT = "agricultural_product"  # 农产品
    WELLNESS_SERVICE = "wellness_service"  # 养生服务
    DIAGNOSTIC_SERVICE = "diagnostic_service"  # 诊断服务
    TREATMENT_SERVICE = "treatment_service"  # 治疗服务

class ResourceStatus(Enum):
    """资源状态"""

    AVAILABLE = "available"  # 可用
    BUSY = "busy"  # 忙碌
    OFFLINE = "offline"  # 离线
    MAINTENANCE = "maintenance"  # 维护中
    RESERVED = "reserved"  # 已预约
    SUSPENDED = "suspended"  # 暂停服务
    RETIRED = "retired"  # 已退役

class QualityLevel(Enum):
    """质量等级"""

    PREMIUM = "premium"  # 顶级 (95-100分)
    EXCELLENT = "excellent"  # 优秀 (90-94分)
    GOOD = "good"  # 良好 (80-89分)
    STANDARD = "standard"  # 标准 (70-79分)
    BASIC = "basic"  # 基础 (60-69分)
    POOR = "poor"  # 较差 (<60分)

class SpecialtyType(Enum):
    """专科类型"""

    # 中医专科
    TCM_INTERNAL = "tcm_internal"  # 中医内科
    TCM_SURGERY = "tcm_surgery"  # 中医外科
    TCM_GYNECOLOGY = "tcm_gynecology"  # 中医妇科
    TCM_PEDIATRICS = "tcm_pediatrics"  # 中医儿科
    TCM_ORTHOPEDICS = "tcm_orthopedics"  # 中医骨科
    ACUPUNCTURE = "acupuncture"  # 针灸科
    MASSAGE = "massage"  # 推拿科
    TCM_DERMATOLOGY = "tcm_dermatology"  # 中医皮肤科

    # 现代医学专科
    CARDIOLOGY = "cardiology"  # 心血管科
    NEUROLOGY = "neurology"  # 神经科
    ONCOLOGY = "oncology"  # 肿瘤科
    ENDOCRINOLOGY = "endocrinology"  # 内分泌科
    GASTROENTEROLOGY = "gastroenterology"  # 消化科
    PULMONOLOGY = "pulmonology"  # 呼吸科
    NEPHROLOGY = "nephrology"  # 肾脏科
    RHEUMATOLOGY = "rheumatology"  # 风湿科

class CertificationLevel(Enum):
    """认证等级"""

    NATIONAL_EXPERT = "national_expert"  # 国家级专家
    PROVINCIAL_EXPERT = "provincial_expert"  # 省级专家
    SENIOR_DOCTOR = "senior_doctor"  # 主任医师
    ASSOCIATE_DOCTOR = "associate_doctor"  # 副主任医师
    ATTENDING_DOCTOR = "attending_doctor"  # 主治医师
    RESIDENT_DOCTOR = "resident_doctor"  # 住院医师
    CERTIFIED_PRACTITIONER = "certified_practitioner"  # 执业医师

@dataclass
class ResourceLocation:
    """资源位置信息"""

    latitude: float
    longitude: float
    address: str
    city: str
    province: str
    country: str = "中国"
    postal_code: Optional[str] = None
    landmark: Optional[str] = None
    accessibility: Dict[str, bool] = field(default_factory=dict)  # 无障碍设施

@dataclass
class ResourceSchedule:
    """资源时间安排"""

    resource_id: str
    date: datetime
    start_time: datetime
    end_time: datetime
    status: ResourceStatus
    appointment_id: Optional[str] = None
    notes: Optional[str] = None
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None

@dataclass
class ResourceCapability:
    """资源能力"""

    capability_id: str
    name: str
    description: str
    proficiency_level: float  # 0-100
    certification: Optional[str] = None
    experience_years: Optional[int] = None
    success_rate: Optional[float] = None
    patient_satisfaction: Optional[float] = None

@dataclass
class ResourceMetrics:
    """资源指标"""

    resource_id: str
    utilization_rate: float
    satisfaction_score: float
    success_rate: float
    response_time: float
    availability_rate: float
    quality_score: float
    cost_effectiveness: float
    patient_volume: int
    revenue: float
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class ResourceReview:
    """资源评价"""

    review_id: str
    resource_id: str
    user_id: str
    rating: float  # 1-5
    comment: str
    service_date: datetime
    review_date: datetime
    verified: bool = False
    helpful_votes: int = 0
    categories: List[str] = field(default_factory=list)

@dataclass
class ResourceCost:
    """资源成本"""

    resource_id: str
    base_cost: float
    additional_costs: Dict[str, float]
    currency: str = "CNY"
    billing_unit: str = "session"  # session, hour, day, etc.
    insurance_covered: bool = False
    discount_available: bool = False
    payment_methods: List[str] = field(default_factory=list)

@dataclass
class MedicalResource:
    """医疗资源基础类"""

    resource_id: str
    name: str
    category: ResourceCategory
    status: ResourceStatus
    quality_level: QualityLevel
    location: ResourceLocation
    contact_info: Dict[str, str]
    description: str
    capabilities: List[ResourceCapability]
    metrics: ResourceMetrics
    cost: ResourceCost
    created_at: datetime
    updated_at: datetime
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TCMDoctor(MedicalResource):
    """中医师资源"""

    specialty: SpecialtyType
    certification_level: CertificationLevel
    constitution_expertise: List[ConstitutionType]
    treatment_methods: List[str]
    years_of_experience: int
    education_background: str
    research_areas: List[str]
    publications: List[str]
    awards: List[str]
    patient_testimonials: List[str]
    consultation_fee: float
    follow_up_fee: float
    languages: List[str] = field(default_factory=lambda: ["中文"])

@dataclass
class ModernDoctor(MedicalResource):
    """现代医生资源"""

    specialty: SpecialtyType
    certification_level: CertificationLevel
    medical_license: str
    board_certifications: List[str]
    years_of_experience: int
    education_background: str
    hospital_affiliations: List[str]
    research_interests: List[str]
    clinical_trials: List[str]
    consultation_fee: float
    procedure_fees: Dict[str, float]
    insurance_accepted: List[str]

@dataclass
class MedicalFacility(MedicalResource):
    """医疗机构资源"""

    facility_type: str  # hospital, clinic, center
    accreditation: List[str]
    bed_count: int
    departments: List[str]
    services_offered: List[str]
    equipment_list: List[str]
    operating_hours: Dict[str, str]
    emergency_services: bool
    parking_available: bool
    public_transport_access: bool
    website: Optional[str] = None

@dataclass
class MedicalEquipment(MedicalResource):
    """医疗设备资源"""

    equipment_type: str
    manufacturer: str
    model: str
    year_manufactured: int
    last_maintenance: datetime
    next_maintenance: datetime
    calibration_status: str
    usage_hours: int
    max_daily_usage: int
    operator_requirements: List[str]
    safety_certifications: List[str]

@dataclass
class HerbalMedicine(MedicalResource):
    """中药材资源"""

    scientific_name: str
    common_names: List[str]
    origin_region: str
    harvest_season: str
    processing_method: str
    active_compounds: List[str]
    therapeutic_effects: List[str]
    contraindications: List[str]
    dosage_forms: List[str]
    storage_requirements: str
    shelf_life: int  # months
    quality_grade: str
    price_per_unit: float
    unit: str  # kg, g, piece

@dataclass
class AgriculturalProduct(MedicalResource):
    """农产品资源"""

    product_type: str
    variety: str
    origin_farm: str
    organic_certified: bool
    harvest_date: datetime
    nutritional_content: Dict[str, float]
    health_benefits: List[str]
    recommended_usage: str
    storage_conditions: str
    packaging_options: List[str]
    seasonal_availability: List[str]
    price_per_unit: float
    minimum_order: int

class ResourceManagementService:
    """
    医疗资源统一管理服务

    负责各类医疗资源的注册、更新、查询、调度等功能
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.max_search_radius = config.get("max_search_radius", 50)  # km
        self.default_page_size = config.get("default_page_size", 20)
        self.cache_ttl = config.get("cache_ttl", 3600)  # seconds

        # 资源存储
        self.resources: Dict[str, MedicalResource] = {}
        self.resource_index: Dict[ResourceCategory, Set[str]] = defaultdict(set)
        self.location_index: Dict[str, List[str]] = defaultdict(
            list
        )  # city -> resource_ids
        self.specialty_index: Dict[SpecialtyType, Set[str]] = defaultdict(set)
        self.quality_index: Dict[QualityLevel, Set[str]] = defaultdict(set)

        # 调度和预约
        self.schedules: Dict[str, List[ResourceSchedule]] = defaultdict(list)
        self.availability_cache: Dict[str, Dict[str, bool]] = {}

        # 评价和反馈
        self.reviews: Dict[str, List[ResourceReview]] = defaultdict(list)
        self.rating_cache: Dict[str, float] = {}

        # 搜索和推荐
        self.search_cache: Dict[str, Tuple[List[str], datetime]] = {}
        self.recommendation_cache: Dict[str, Tuple[List[str], datetime]] = {}

        # 统计数据
        self.resource_stats = {
            "total_resources": 0,
            "resources_by_category": defaultdict(int),
            "resources_by_quality": defaultdict(int),
            "resources_by_status": defaultdict(int),
            "average_utilization": 0.0,
            "average_satisfaction": 0.0,
            "total_appointments": 0,
            "revenue_by_category": defaultdict(float),
        }

        # 监控和告警
        self.monitoring_enabled = True
        self.alert_thresholds = {
            "low_availability": 0.3,
            "low_satisfaction": 3.0,
            "high_utilization": 0.9,
            "maintenance_due": timedelta(days=7),
        }

        logger.info("资源管理服务初始化完成")

    async def register_resource(self, resource: MedicalResource) -> str:
        """注册新资源"""
        try:
            # 验证资源数据
            await self._validate_resource_data(resource)

            # 生成资源ID（如果未提供）
            if not resource.resource_id:
                resource.resource_id = (
                    f"{resource.category.value}_{uuid.uuid4().hex[:8]}"
                )

            # 存储资源
            self.resources[resource.resource_id] = resource

            # 更新索引
            await self._update_resource_indexes(resource)

            # 初始化调度
            await self._initialize_resource_schedule(resource.resource_id)

            # 更新统计
            self._update_resource_statistics(resource, "add")

            logger.info(f"注册资源成功: {resource.resource_id} - {resource.name}")
            return resource.resource_id

        except Exception as e:
            logger.error(f"注册资源失败: {e}")
            raise

    async def update_resource(self, resource_id: str, updates: Dict[str, Any]) -> bool:
        """更新资源信息"""
        try:
            if resource_id not in self.resources:
                raise ValueError(f"资源不存在: {resource_id}")

            resource = self.resources[resource_id]
            old_category = resource.category
            old_quality = resource.quality_level

            # 应用更新
            for field, value in updates.items():
                if hasattr(resource, field):
                    setattr(resource, field, value)

            resource.updated_at = datetime.now()

            # 重新验证
            await self._validate_resource_data(resource)

            # 更新索引（如果类别或质量等级发生变化）
            if (
                resource.category != old_category
                or resource.quality_level != old_quality
            ):
                await self._update_resource_indexes(resource, old_category, old_quality)

            # 清除相关缓存
            await self._clear_resource_cache(resource_id)

            # 更新统计
            self._update_resource_statistics(resource, "update")

            logger.info(f"更新资源成功: {resource_id}")
            return True

        except Exception as e:
            logger.error(f"更新资源失败: {e}")
            raise

    async def remove_resource(self, resource_id: str) -> bool:
        """移除资源"""
        try:
            if resource_id not in self.resources:
                raise ValueError(f"资源不存在: {resource_id}")

            resource = self.resources[resource_id]

            # 检查是否有未完成的预约
            active_appointments = await self._get_active_appointments(resource_id)
            if active_appointments:
                raise ValueError(
                    f"资源有未完成的预约，无法移除: {len(active_appointments)}个预约"
                )

            # 从索引中移除
            await self._remove_from_indexes(resource)

            # 移除调度信息
            if resource_id in self.schedules:
                del self.schedules[resource_id]

            # 移除资源
            del self.resources[resource_id]

            # 清除缓存
            await self._clear_resource_cache(resource_id)

            # 更新统计
            self._update_resource_statistics(resource, "remove")

            logger.info(f"移除资源成功: {resource_id}")
            return True

        except Exception as e:
            logger.error(f"移除资源失败: {e}")
            raise

    async def search_resources(
        self,
        category: Optional[ResourceCategory] = None,
        specialty: Optional[SpecialtyType] = None,
        location: Optional[Tuple[float, float]] = None,
        radius: Optional[float] = None,
        quality_level: Optional[QualityLevel] = None,
        status: Optional[ResourceStatus] = None,
        constitution_type: Optional[ConstitutionType] = None,
        price_range: Optional[Tuple[float, float]] = None,
        availability_date: Optional[datetime] = None,
        keywords: Optional[str] = None,
        sort_by: str = "relevance",
        page: int = 1,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        """搜索医疗资源"""
        try:
            # 构建搜索缓存键
            cache_key = self._build_search_cache_key(
                category,
                specialty,
                location,
                radius,
                quality_level,
                status,
                constitution_type,
                price_range,
                availability_date,
                keywords,
                sort_by,
                page,
                page_size,
            )

            # 检查缓存
            if cache_key in self.search_cache:
                cached_result, cache_time = self.search_cache[cache_key]
                if datetime.now() - cache_time < timedelta(seconds=self.cache_ttl):
                    return await self._format_search_results(
                        cached_result, page, page_size or self.default_page_size
                    )

            # 执行搜索
            candidate_ids = set(self.resources.keys())

            # 按类别筛选
            if category:
                candidate_ids &= self.resource_index[category]

            # 按专科筛选
            if specialty:
                candidate_ids &= self.specialty_index[specialty]

            # 按质量等级筛选
            if quality_level:
                candidate_ids &= self.quality_index[quality_level]

            # 按状态筛选
            if status:
                status_filtered = {
                    rid for rid in candidate_ids if self.resources[rid].status == status
                }
                candidate_ids &= status_filtered

            # 按位置筛选
            if location:
                location_filtered = await self._filter_by_location(
                    candidate_ids, location, radius or self.max_search_radius
                )
                candidate_ids &= location_filtered

            # 按体质类型筛选（针对中医师）
            if constitution_type:
                constitution_filtered = await self._filter_by_constitution(
                    candidate_ids, constitution_type
                )
                candidate_ids &= constitution_filtered

            # 按价格范围筛选
            if price_range:
                price_filtered = await self._filter_by_price(candidate_ids, price_range)
                candidate_ids &= price_filtered

            # 按可用性筛选
            if availability_date:
                availability_filtered = await self._filter_by_availability(
                    candidate_ids, availability_date
                )
                candidate_ids &= availability_filtered

            # 关键词搜索
            if keywords:
                keyword_filtered = await self._filter_by_keywords(
                    candidate_ids, keywords
                )
                candidate_ids &= keyword_filtered

            # 排序
            sorted_results = await self._sort_search_results(
                list(candidate_ids), sort_by, location
            )

            # 缓存结果
            self.search_cache[cache_key] = (sorted_results, datetime.now())

            # 格式化并返回结果
            return await self._format_search_results(
                sorted_results, page, page_size or self.default_page_size
            )

        except Exception as e:
            logger.error(f"搜索资源失败: {e}")
            raise

    async def get_resource_details(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """获取资源详细信息"""
        try:
            if resource_id not in self.resources:
                return None

            resource = self.resources[resource_id]

            # 获取评价统计
            reviews = self.reviews.get(resource_id, [])
            avg_rating = (
                sum(r.rating for r in reviews) / len(reviews) if reviews else 0.0
            )

            # 获取可用性信息
            availability = await self._get_resource_availability(resource_id)

            # 获取相关推荐
            recommendations = await self._get_similar_resources(resource_id, limit=5)

            return {
                "resource": resource,
                "reviews": {
                    "average_rating": avg_rating,
                    "total_reviews": len(reviews),
                    "recent_reviews": reviews[-5:] if reviews else [],
                },
                "availability": availability,
                "recommendations": recommendations,
                "metrics": resource.metrics,
                "last_updated": resource.updated_at.isoformat(),
            }

        except Exception as e:
            logger.error(f"获取资源详情失败: {e}")
            raise

    async def get_resource_availability(
        self, resource_id: str, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """获取资源可用性"""
        try:
            if resource_id not in self.resources:
                raise ValueError(f"资源不存在: {resource_id}")

            resource = self.resources[resource_id]
            schedules = self.schedules.get(resource_id, [])

            # 筛选指定时间范围内的调度
            relevant_schedules = [
                s for s in schedules if start_date <= s.date <= end_date
            ]

            # 计算可用时间段
            available_slots = []
            busy_slots = []

            current_date = start_date.date()
            end_date_only = end_date.date()

            while current_date <= end_date_only:
                # 获取当天的调度
                day_schedules = [
                    s for s in relevant_schedules if s.date.date() == current_date
                ]

                # 计算当天的可用时间段
                day_availability = await self._calculate_day_availability(
                    resource_id, current_date, day_schedules
                )

                available_slots.extend(day_availability["available"])
                busy_slots.extend(day_availability["busy"])

                current_date += timedelta(days=1)

            # 计算可用性统计
            total_hours = (end_date - start_date).total_seconds() / 3600
            busy_hours = sum(
                (slot["end"] - slot["start"]).total_seconds() / 3600
                for slot in busy_slots
            )
            availability_rate = (
                (total_hours - busy_hours) / total_hours if total_hours > 0 else 0
            )

            return {
                "resource_id": resource_id,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
                "availability_rate": availability_rate,
                "available_slots": available_slots,
                "busy_slots": busy_slots,
                "total_available_hours": total_hours - busy_hours,
                "next_available": await self._get_next_available_slot(
                    resource_id, start_date
                ),
            }

        except Exception as e:
            logger.error(f"获取资源可用性失败: {e}")
            raise
