"""
models - 索克生活项目模块
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

#!/usr/bin/env python

"""
领域模型
定义服务中使用的领域模型和枚举
"""



class MedicalResourceType(str, Enum):
    """医疗资源类型"""

    DOCTOR = "DOCTOR"  # 医生
    HOSPITAL = "HOSPITAL"  # 医院
    CLINIC = "CLINIC"  # 诊所
    EQUIPMENT = "EQUIPMENT"  # 医疗设备
    SPECIALIST = "SPECIALIST"  # 专科医生
    TCM_DOCTOR = "TCM_DOCTOR"  # 中医医生
    WESTERN_DOCTOR = "WESTERN_DOCTOR"  # 西医医生
    THERAPIST = "THERAPIST"  # 治疗师
    NUTRITIONIST = "NUTRITIONIST"  # 营养师
    OTHER = "OTHER"  # 其他资源


class AppointmentStatus(str, Enum):
    """预约状态"""

    PENDING = "PENDING"  # 待确认
    CONFIRMED = "CONFIRMED"  # 已确认
    CANCELLED = "CANCELLED"  # 已取消
    COMPLETED = "COMPLETED"  # 已完成
    MISSED = "MISSED"  # 未到诊
    RESCHEDULED = "RESCHEDULED"  # 已改期


class AppointmentType(str, Enum):
    """预约类型"""

    ONLINE_CONSULTATION = "ONLINE_CONSULTATION"  # 线上问诊
    IN_PERSON = "IN_PERSON"  # 线下问诊
    HOME_VISIT = "HOME_VISIT"  # 上门问诊
    FOLLOW_UP = "FOLLOW_UP"  # 复诊
    EMERGENCY = "EMERGENCY"  # 紧急问诊


class ConstitutionType(str, Enum):
    """中医体质类型"""

    BALANCED = "BALANCED"  # 平和质
    QI_DEFICIENCY = "QI_DEFICIENCY"  # 气虚质
    YANG_DEFICIENCY = "YANG_DEFICIENCY"  # 阳虚质
    YIN_DEFICIENCY = "YIN_DEFICIENCY"  # 阴虚质
    PHLEGM_DAMPNESS = "PHLEGM_DAMPNESS"  # 痰湿质
    DAMP_HEAT = "DAMP_HEAT"  # 湿热质
    BLOOD_STASIS = "BLOOD_STASIS"  # 血瘀质
    QI_DEPRESSION = "QI_DEPRESSION"  # 气郁质
    SPECIAL = "SPECIAL"  # 特禀质


class PaymentMethod(str, Enum):
    """支付方式"""

    ALIPAY = "ALIPAY"  # 支付宝
    WECHAT = "WECHAT"  # 微信支付
    CREDIT_CARD = "CREDIT_CARD"  # 信用卡
    BANK_TRANSFER = "BANK_TRANSFER"  # 银行转账
    INSURANCE = "INSURANCE"  # 医保支付
    CASH = "CASH"  # 现金支付
    OTHER = "OTHER"  # 其他方式


class PaymentStatus(str, Enum):
    """支付状态"""

    PENDING = "PENDING"  # 待支付
    SUCCESS = "SUCCESS"  # 支付成功
    FAILED = "FAILED"  # 支付失败
    REFUNDED = "REFUNDED"  # 已退款
    PARTIALLY_REFUNDED = "PARTIALLY_REFUNDED"  # 部分退款


class ProductType(str, Enum):
    """产品类型"""

    FOOD = "FOOD"  # 食品
    HERB = "HERB"  # 药材
    SUPPLEMENT = "SUPPLEMENT"  # 保健品
    EQUIPMENT = "EQUIPMENT"  # 设备
    SERVICE = "SERVICE"  # 服务
    PACKAGE = "PACKAGE"  # 套餐


class OrderStatus(str, Enum):
    """订单状态"""

    PENDING_PAYMENT = "PENDING_PAYMENT"  # 待支付
    PAID = "PAID"  # 已支付
    PROCESSING = "PROCESSING"  # 处理中
    SHIPPED = "SHIPPED"  # 已发货
    DELIVERED = "DELIVERED"  # 已送达
    COMPLETED = "COMPLETED"  # 已完成
    CANCELLED = "CANCELLED"  # 已取消
    REFUNDING = "REFUNDING"  # 退款中
    REFUNDED = "REFUNDED"  # 已退款


class SubscriptionStatus(str, Enum):
    """订阅状态"""

    ACTIVE = "ACTIVE"  # 活跃
    PENDING = "PENDING"  # 待确认
    PAUSED = "PAUSED"  # 已暂停
    CANCELLED = "CANCELLED"  # 已取消
    EXPIRED = "EXPIRED"  # 已过期


class SubscriptionPlan(str, Enum):
    """订阅计划"""

    BASIC = "BASIC"  # 基础计划
    STANDARD = "STANDARD"  # 标准计划
    PREMIUM = "PREMIUM"  # 高级计划
    FAMILY = "FAMILY"  # 家庭计划
    ENTERPRISE = "ENTERPRISE"  # 企业计划


class ActivityType(str, Enum):
    """农事活动类型"""

    PLANTING = "PLANTING"  # 种植体验
    HARVESTING = "HARVESTING"  # 采摘体验
    PROCESSING = "PROCESSING"  # 加工体验
    COOKING = "COOKING"  # 烹饪体验
    EDUCATIONAL = "EDUCATIONAL"  # 教育活动
    THERAPEUTIC = "THERAPEUTIC"  # 治疗活动
    SEASONAL = "SEASONAL"  # 季节性活动


@dataclass
class Appointment:
    """预约模型"""

    id: str
    user_id: str
    doctor_id: str
    appointment_type: AppointmentType
    preferred_time: datetime
    confirmed_time: datetime | None
    symptoms: str
    constitution_type: ConstitutionType
    status: AppointmentStatus
    meeting_link: str | None = None
    created_at: datetime = datetime.now()
    updated_at: datetime | None = None
    metadata: dict[str, str] = None


@dataclass
class Product:
    """产品模型"""

    id: str
    name: str
    description: str
    product_type: ProductType
    price: float
    origin: str
    producer: str
    image_url: str
    constitution_benefits: dict[str, str]
    health_benefits: list[str]
    seasons: list[str]
    tags: list[str]
    categories: list[str]
    stock: int
    created_at: datetime = datetime.now()
    updated_at: datetime | None = None
    metadata: dict[str, Any] = None


@dataclass
class Order:
    """订单模型"""

    id: str
    user_id: str
    products: list[dict[str, Any]]
    total_price: float
    status: OrderStatus
    payment_method: PaymentMethod | None = None
    payment_id: str | None = None
    shipping_address: str | None = None
    tracking_number: str | None = None
    created_at: datetime = datetime.now()
    updated_at: datetime | None = None
    metadata: dict[str, Any] = None


@dataclass
class Payment:
    """支付模型"""

    id: str
    user_id: str
    order_id: str
    payment_method: PaymentMethod
    amount: float
    currency: str
    status: PaymentStatus
    transaction_id: str | None = None
    created_at: datetime = datetime.now()
    completed_at: datetime | None = None
    metadata: dict[str, Any] = None


@dataclass
class Subscription:
    """订阅模型"""

    id: str
    user_id: str
    plan_id: str
    status: SubscriptionStatus
    payment_method: PaymentMethod
    start_date: datetime
    end_date: datetime
    next_billing_date: datetime
    amount: float
    auto_renew: bool = True
    created_at: datetime = datetime.now()
    updated_at: datetime | None = None
    metadata: dict[str, Any] = None


@dataclass
class FarmingActivity:
    """农事活动模型"""

    id: str
    name: str
    description: str
    activity_type: ActivityType
    location: str
    start_time: datetime
    end_time: datetime
    capacity: int
    price: float
    constitution_benefits: dict[str, str]
    health_benefits: list[str]
    registration_deadline: datetime
    created_at: datetime = datetime.now()
    updated_at: datetime | None = None
    metadata: dict[str, Any] = None
