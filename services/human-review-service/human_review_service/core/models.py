"""
核心数据模型
Core Data Models

定义人工审核系统的核心数据结构和业务模型
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import (
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class ReviewStatus(str, Enum):
    """审核状态枚举"""

    PENDING = "pending"  # 待审核
    ASSIGNED = "assigned"  # 已分配
    IN_PROGRESS = "in_progress"  # 审核中
    APPROVED = "approved"  # 已通过
    REJECTED = "rejected"  # 已拒绝
    NEEDS_REVISION = "needs_revision"  # 需要修改
    CANCELLED = "cancelled"  # 已取消
    EXPIRED = "expired"  # 已过期


class ReviewPriority(str, Enum):
    """审核优先级枚举"""

    LOW = "low"  # 低优先级
    NORMAL = "normal"  # 普通优先级
    HIGH = "high"  # 高优先级
    URGENT = "urgent"  # 紧急优先级
    CRITICAL = "critical"  # 危急优先级


class ReviewType(str, Enum):
    """审核类型枚举"""

    MEDICAL_DIAGNOSIS = "medical_diagnosis"  # 医疗诊断
    HEALTH_PLAN = "health_plan"  # 健康计划
    NUTRITION_ADVICE = "nutrition_advice"  # 营养建议
    PRODUCT_RECOMMENDATION = "product_recommendation"  # 产品推荐
    EMERGENCY_RESPONSE = "emergency_response"  # 紧急响应
    GENERAL_ADVICE = "general_advice"  # 一般建议
    MEDICATION_GUIDANCE = "medication_guidance"  # 用药指导
    LIFESTYLE_RECOMMENDATION = "lifestyle_recommendation"  # 生活方式建议


class ReviewerStatus(str, Enum):
    """审核员状态枚举"""

    ACTIVE = "active"  # 活跃
    INACTIVE = "inactive"  # 非活跃
    BUSY = "busy"  # 忙碌
    OFFLINE = "offline"  # 离线
    ON_BREAK = "on_break"  # 休息中


# SQLAlchemy 数据库模型


class ReviewTaskDB(Base):
    """审核任务数据库模型"""

    __tablename__ = "review_tasks"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    task_id = Column(String(100), unique=True, nullable=False, index=True)
    review_type = Column(SQLEnum(ReviewType), nullable=False)
    priority = Column(
        SQLEnum(ReviewPriority), nullable=False, default=ReviewPriority.NORMAL
    )
    status = Column(SQLEnum(ReviewStatus), nullable=False, default=ReviewStatus.PENDING)

    # 内容相关
    content = Column(JSON, nullable=False)
    original_content = Column(JSON)  # 原始内容备份

    # 用户和智能体信息
    user_id = Column(String(100), nullable=False, index=True)
    agent_id = Column(String(100), nullable=False, index=True)

    # 审核相关
    assigned_to = Column(
        String(100), ForeignKey("reviewers.reviewer_id"), nullable=True
    )
    reviewer_notes = Column(Text)
    review_comments = Column(Text)
    review_result = Column(JSON)

    # 时间相关
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    assigned_at = Column(DateTime(timezone=True))
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))

    # 元数据
    estimated_duration = Column(Integer, default=1800)  # 预估时长（秒）
    actual_duration = Column(Integer)  # 实际时长（秒）
    complexity_score = Column(Float, default=1.0)  # 复杂度评分
    risk_score = Column(Float, default=0.0)  # 风险评分

    # 关联关系
    reviewer = relationship("ReviewerDB", back_populates="tasks")
    history = relationship("ReviewHistoryDB", back_populates="task")


class ReviewerDB(Base):
    """审核员数据库模型"""

    __tablename__ = "reviewers"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    reviewer_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    email = Column(String(255), unique=True, nullable=False)

    # 专业信息
    specialties = Column(JSON, nullable=False)  # 专业领域列表
    certifications = Column(JSON)  # 认证信息
    experience_years = Column(Integer, default=0)

    # 工作配置
    max_concurrent_tasks = Column(Integer, default=5)
    working_hours = Column(JSON)  # 工作时间配置
    timezone = Column(String(50), default="Asia/Shanghai")

    # 状态信息
    status = Column(SQLEnum(ReviewerStatus), default=ReviewerStatus.ACTIVE)
    current_task_count = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)

    # 统计信息
    total_reviews = Column(Integer, default=0)
    approved_reviews = Column(Integer, default=0)
    rejected_reviews = Column(Integer, default=0)
    average_review_time = Column(Float, default=1800.0)  # 平均审核时间（秒）
    quality_score = Column(Float, default=5.0)  # 质量评分（1-10）

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_active_at = Column(DateTime(timezone=True))

    # 关联关系
    tasks = relationship("ReviewTaskDB", back_populates="reviewer")


class ReviewHistoryDB(Base):
    """审核历史记录数据库模型"""

    __tablename__ = "review_history"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    task_id = Column(
        PGUUID(as_uuid=True), ForeignKey("review_tasks.id"), nullable=False
    )

    # 操作信息
    action = Column(String(50), nullable=False)  # 操作类型
    old_status = Column(SQLEnum(ReviewStatus))
    new_status = Column(SQLEnum(ReviewStatus))

    # 操作者信息
    actor_id = Column(String(100), nullable=False)  # 操作者ID
    actor_type = Column(
        String(50), nullable=False
    )  # 操作者类型（reviewer/system/admin）

    # 详细信息
    details = Column(JSON)  # 操作详情
    comments = Column(Text)  # 备注

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关联关系
    task = relationship("ReviewTaskDB", back_populates="history")


# Pydantic 模型


class ReviewTaskBase(BaseModel):
    """审核任务基础模型"""

    model_config = ConfigDict(from_attributes=True)

    review_type: ReviewType
    priority: ReviewPriority = ReviewPriority.NORMAL
    content: Dict[str, Any]
    user_id: str
    agent_id: str
    estimated_duration: int = 1800
    expires_at: Optional[datetime] = None


class ReviewTaskCreate(ReviewTaskBase):
    """创建审核任务模型"""

    pass


class ReviewTaskUpdate(BaseModel):
    """更新审核任务模型"""

    model_config = ConfigDict(from_attributes=True)

    status: Optional[ReviewStatus] = None
    assigned_to: Optional[str] = None
    reviewer_notes: Optional[str] = None
    review_comments: Optional[str] = None
    review_result: Optional[Dict[str, Any]] = None


class ReviewTask(ReviewTaskBase):
    """审核任务完整模型"""

    id: UUID
    task_id: str
    status: ReviewStatus
    assigned_to: Optional[str] = None
    reviewer_notes: Optional[str] = None
    review_comments: Optional[str] = None
    review_result: Optional[Dict[str, Any]] = None

    created_at: datetime
    assigned_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    actual_duration: Optional[int] = None
    complexity_score: float = 1.0
    risk_score: float = 0.0


class ReviewerBase(BaseModel):
    """审核员基础模型"""

    model_config = ConfigDict(from_attributes=True)

    name: str
    email: str
    specialties: List[str]
    certifications: Optional[List[str]] = None
    experience_years: int = 0
    max_concurrent_tasks: int = 5
    working_hours: Optional[Dict[str, Any]] = None
    timezone: str = "Asia/Shanghai"


class ReviewerCreate(ReviewerBase):
    """创建审核员模型"""

    reviewer_id: str


class ReviewerUpdate(BaseModel):
    """更新审核员模型"""

    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = None
    email: Optional[str] = None
    specialties: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    experience_years: Optional[int] = None
    max_concurrent_tasks: Optional[int] = None
    working_hours: Optional[Dict[str, Any]] = None
    timezone: Optional[str] = None
    status: Optional[ReviewerStatus] = None
    is_available: Optional[bool] = None


class Reviewer(ReviewerBase):
    """审核员完整模型"""

    id: UUID
    reviewer_id: str
    status: ReviewerStatus
    current_task_count: int = 0
    is_available: bool = True

    total_reviews: int = 0
    approved_reviews: int = 0
    rejected_reviews: int = 0
    average_review_time: float = 1800.0
    quality_score: float = 5.0

    created_at: datetime
    updated_at: Optional[datetime] = None
    last_active_at: Optional[datetime] = None


class ReviewDecision(BaseModel):
    """审核决策模型"""

    model_config = ConfigDict(from_attributes=True)

    decision: ReviewStatus  # approved, rejected, needs_revision
    comments: str = ""
    reviewer_notes: Optional[str] = None
    review_result: Optional[Dict[str, Any]] = None
    suggestions: Optional[str] = None


class ReviewStatistics(BaseModel):
    """审核统计模型"""

    model_config = ConfigDict(from_attributes=True)

    total_tasks: int = 0
    pending_tasks: int = 0
    in_progress_tasks: int = 0
    completed_tasks: int = 0
    approved_tasks: int = 0
    rejected_tasks: int = 0

    average_review_time: float = 0.0
    average_wait_time: float = 0.0

    reviewer_count: int = 0
    active_reviewers: int = 0

    tasks_by_priority: Dict[str, int] = Field(default_factory=dict)
    tasks_by_type: Dict[str, int] = Field(default_factory=dict)
    tasks_by_status: Dict[str, int] = Field(default_factory=dict)


class DashboardData(BaseModel):
    """仪表板数据模型"""

    model_config = ConfigDict(from_attributes=True)

    statistics: ReviewStatistics
    pending_tasks: List[ReviewTask]
    active_reviewers: List[Reviewer]
    recent_completions: List[ReviewTask]

    # 实时指标
    current_load: float = 0.0  # 当前负载百分比
    estimated_wait_time: int = 0  # 预估等待时间（分钟）

    # 趋势数据
    hourly_stats: Optional[List[Dict[str, Any]]] = None
    daily_stats: Optional[List[Dict[str, Any]]] = None


class PaginatedResponse(BaseModel):
    """分页响应模型"""

    model_config = ConfigDict(from_attributes=True)

    items: List[Any]
    total: int
    page: int
    size: int
    pages: int


class ReviewerWorkload(BaseModel):
    """审核员工作负载模型"""

    model_config = ConfigDict(from_attributes=True)

    reviewer_id: str
    current_tasks: int
    max_concurrent_tasks: int
    utilization_rate: float
    pending_tasks: int
    completed_today: int
    average_completion_time: float


class DashboardStatistics(BaseModel):
    """仪表板统计模型"""

    model_config = ConfigDict(from_attributes=True)

    total_tasks: int
    pending_tasks: int
    in_progress_tasks: int
    completed_tasks: int
    approved_tasks: int
    rejected_tasks: int
    total_reviewers: int
    active_reviewers: int
    average_review_time: float
    average_accuracy_rate: float
    tasks_completed_today: int
    high_priority_pending: int
    system_load: float
