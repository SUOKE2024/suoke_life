"""
审核相关数据模型

定义审核任务、审核结果、审核员等核心实体的数据结构
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator
from sqlalchemy import (
    Boolean, Column, DateTime, Enum as SQLEnum, Float, Integer, 
    JSON, String, Text, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class ReviewStatus(str, Enum):
    """审核状态枚举"""
    PENDING = "pending"           # 待审核
    IN_PROGRESS = "in_progress"   # 审核中
    APPROVED = "approved"         # 已通过
    REJECTED = "rejected"         # 已拒绝
    NEEDS_REVISION = "needs_revision"  # 需要修改
    ESCALATED = "escalated"       # 已升级
    CANCELLED = "cancelled"       # 已取消


class ReviewPriority(str, Enum):
    """审核优先级枚举"""
    LOW = "low"           # 低优先级
    MEDIUM = "medium"     # 中优先级
    HIGH = "high"         # 高优先级
    URGENT = "urgent"     # 紧急
    CRITICAL = "critical" # 关键


class ContentType(str, Enum):
    """内容类型枚举"""
    MEDICAL_DIAGNOSIS = "medical_diagnosis"     # 医学诊断
    HEALTH_ADVICE = "health_advice"             # 健康建议
    USER_CONTENT = "user_content"               # 用户内容
    MULTIMEDIA = "multimedia"                   # 多媒体内容
    DOCUMENT = "document"                       # 文档
    OTHER = "other"                            # 其他


class RiskLevel(str, Enum):
    """风险等级枚举"""
    VERY_LOW = "very_low"     # 极低风险
    LOW = "low"               # 低风险
    MEDIUM = "medium"         # 中风险
    HIGH = "high"             # 高风险
    VERY_HIGH = "very_high"   # 极高风险


# SQLAlchemy 模型
class ReviewTask(Base):
    """审核任务表"""
    __tablename__ = "review_tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False, comment="任务标题")
    description = Column(Text, comment="任务描述")
    content_type = Column(SQLEnum(ContentType), nullable=False, comment="内容类型")
    content_data = Column(JSON, comment="内容数据")
    content_url = Column(String(500), comment="内容URL")
    
    # 状态和优先级
    status = Column(SQLEnum(ReviewStatus), default=ReviewStatus.PENDING, comment="审核状态")
    priority = Column(SQLEnum(ReviewPriority), default=ReviewPriority.MEDIUM, comment="优先级")
    risk_level = Column(SQLEnum(RiskLevel), comment="风险等级")
    
    # AI预审结果
    ai_score = Column(Float, comment="AI评分")
    ai_confidence = Column(Float, comment="AI置信度")
    ai_analysis = Column(JSON, comment="AI分析结果")
    ai_flags = Column(JSON, comment="AI标记的问题")
    
    # 分配信息
    assigned_to = Column(UUID(as_uuid=True), comment="分配给的审核员ID")
    assigned_at = Column(DateTime, comment="分配时间")
    
    # 时间信息
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    due_date = Column(DateTime, comment="截止时间")
    completed_at = Column(DateTime, comment="完成时间")
    
    # 元数据
    metadata = Column(JSON, comment="元数据")
    tags = Column(JSON, comment="标签")
    
    # 关联关系
    reviews = relationship("ReviewResult", back_populates="task")
    comments = relationship("ReviewComment", back_populates="task")


class ReviewResult(Base):
    """审核结果表"""
    __tablename__ = "review_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("review_tasks.id"), nullable=False)
    reviewer_id = Column(UUID(as_uuid=True), nullable=False, comment="审核员ID")
    
    # 审核结果
    decision = Column(SQLEnum(ReviewStatus), nullable=False, comment="审核决定")
    score = Column(Float, comment="审核评分")
    confidence = Column(Float, comment="置信度")
    
    # 详细评估
    quality_score = Column(Float, comment="质量评分")
    safety_score = Column(Float, comment="安全评分")
    compliance_score = Column(Float, comment="合规评分")
    
    # 审核意见
    summary = Column(Text, comment="审核总结")
    detailed_feedback = Column(Text, comment="详细反馈")
    suggestions = Column(JSON, comment="改进建议")
    
    # 标记的问题
    issues_found = Column(JSON, comment="发现的问题")
    risk_factors = Column(JSON, comment="风险因素")
    
    # 时间信息
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    review_duration = Column(Integer, comment="审核耗时（秒）")
    
    # 关联关系
    task = relationship("ReviewTask", back_populates="reviews")
    comments = relationship("ReviewComment", back_populates="result")


class ReviewComment(Base):
    """审核评论表"""
    __tablename__ = "review_comments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("review_tasks.id"), nullable=False)
    result_id = Column(UUID(as_uuid=True), ForeignKey("review_results.id"))
    
    # 评论信息
    author_id = Column(UUID(as_uuid=True), nullable=False, comment="评论作者ID")
    content = Column(Text, nullable=False, comment="评论内容")
    comment_type = Column(String(50), comment="评论类型")
    
    # 引用信息
    parent_id = Column(UUID(as_uuid=True), ForeignKey("review_comments.id"), comment="父评论ID")
    thread_id = Column(UUID(as_uuid=True), comment="讨论线程ID")
    
    # 状态信息
    is_internal = Column(Boolean, default=False, comment="是否为内部评论")
    is_resolved = Column(Boolean, default=False, comment="是否已解决")
    
    # 时间信息
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关联关系
    task = relationship("ReviewTask", back_populates="comments")
    result = relationship("ReviewResult", back_populates="comments")
    replies = relationship("ReviewComment", remote_side=[id])


class ReviewerProfile(Base):
    """审核员档案表"""
    __tablename__ = "reviewer_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), unique=True, nullable=False, comment="用户ID")
    
    # 基本信息
    name = Column(String(100), nullable=False, comment="姓名")
    email = Column(String(255), nullable=False, comment="邮箱")
    phone = Column(String(20), comment="电话")
    
    # 专业信息
    specialties = Column(JSON, comment="专业领域")
    certifications = Column(JSON, comment="认证信息")
    experience_years = Column(Integer, comment="经验年数")
    
    # 审核统计
    total_reviews = Column(Integer, default=0, comment="总审核数")
    approved_reviews = Column(Integer, default=0, comment="通过审核数")
    rejected_reviews = Column(Integer, default=0, comment="拒绝审核数")
    average_score = Column(Float, comment="平均评分")
    
    # 性能指标
    accuracy_rate = Column(Float, comment="准确率")
    efficiency_score = Column(Float, comment="效率评分")
    quality_score = Column(Float, comment="质量评分")
    
    # 工作负载
    current_workload = Column(Integer, default=0, comment="当前工作负载")
    max_concurrent_tasks = Column(Integer, default=5, comment="最大并发任务数")
    
    # 状态信息
    is_active = Column(Boolean, default=True, comment="是否活跃")
    is_available = Column(Boolean, default=True, comment="是否可用")
    last_active_at = Column(DateTime, comment="最后活跃时间")
    
    # 时间信息
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")


# Pydantic 模型
class ReviewTaskBase(BaseModel):
    """审核任务基础模型"""
    title: str = Field(..., description="任务标题", max_length=255)
    description: Optional[str] = Field(None, description="任务描述")
    content_type: ContentType = Field(..., description="内容类型")
    content_data: Optional[Dict[str, Any]] = Field(None, description="内容数据")
    content_url: Optional[str] = Field(None, description="内容URL", max_length=500)
    priority: ReviewPriority = Field(ReviewPriority.MEDIUM, description="优先级")
    due_date: Optional[datetime] = Field(None, description="截止时间")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    tags: Optional[List[str]] = Field(None, description="标签")


class ReviewTaskCreate(ReviewTaskBase):
    """创建审核任务模型"""
    pass


class ReviewTaskUpdate(BaseModel):
    """更新审核任务模型"""
    title: Optional[str] = Field(None, description="任务标题", max_length=255)
    description: Optional[str] = Field(None, description="任务描述")
    priority: Optional[ReviewPriority] = Field(None, description="优先级")
    status: Optional[ReviewStatus] = Field(None, description="状态")
    assigned_to: Optional[uuid.UUID] = Field(None, description="分配给的审核员ID")
    due_date: Optional[datetime] = Field(None, description="截止时间")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    tags: Optional[List[str]] = Field(None, description="标签")


class ReviewTaskResponse(ReviewTaskBase):
    """审核任务响应模型"""
    id: uuid.UUID = Field(..., description="任务ID")
    status: ReviewStatus = Field(..., description="审核状态")
    risk_level: Optional[RiskLevel] = Field(None, description="风险等级")
    ai_score: Optional[float] = Field(None, description="AI评分")
    ai_confidence: Optional[float] = Field(None, description="AI置信度")
    assigned_to: Optional[uuid.UUID] = Field(None, description="分配给的审核员ID")
    assigned_at: Optional[datetime] = Field(None, description="分配时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    
    class Config:
        from_attributes = True


class ReviewResultBase(BaseModel):
    """审核结果基础模型"""
    decision: ReviewStatus = Field(..., description="审核决定")
    score: Optional[float] = Field(None, description="审核评分", ge=0, le=1)
    confidence: Optional[float] = Field(None, description="置信度", ge=0, le=1)
    quality_score: Optional[float] = Field(None, description="质量评分", ge=0, le=1)
    safety_score: Optional[float] = Field(None, description="安全评分", ge=0, le=1)
    compliance_score: Optional[float] = Field(None, description="合规评分", ge=0, le=1)
    summary: Optional[str] = Field(None, description="审核总结")
    detailed_feedback: Optional[str] = Field(None, description="详细反馈")
    suggestions: Optional[List[str]] = Field(None, description="改进建议")
    issues_found: Optional[List[Dict[str, Any]]] = Field(None, description="发现的问题")
    risk_factors: Optional[List[str]] = Field(None, description="风险因素")


class ReviewResultCreate(ReviewResultBase):
    """创建审核结果模型"""
    task_id: uuid.UUID = Field(..., description="任务ID")


class ReviewResultResponse(ReviewResultBase):
    """审核结果响应模型"""
    id: uuid.UUID = Field(..., description="结果ID")
    task_id: uuid.UUID = Field(..., description="任务ID")
    reviewer_id: uuid.UUID = Field(..., description="审核员ID")
    created_at: datetime = Field(..., description="创建时间")
    review_duration: Optional[int] = Field(None, description="审核耗时（秒）")
    
    class Config:
        from_attributes = True


class ReviewCommentBase(BaseModel):
    """审核评论基础模型"""
    content: str = Field(..., description="评论内容")
    comment_type: Optional[str] = Field(None, description="评论类型")
    is_internal: bool = Field(False, description="是否为内部评论")


class ReviewCommentCreate(ReviewCommentBase):
    """创建审核评论模型"""
    task_id: uuid.UUID = Field(..., description="任务ID")
    result_id: Optional[uuid.UUID] = Field(None, description="结果ID")
    parent_id: Optional[uuid.UUID] = Field(None, description="父评论ID")


class ReviewCommentResponse(ReviewCommentBase):
    """审核评论响应模型"""
    id: uuid.UUID = Field(..., description="评论ID")
    task_id: uuid.UUID = Field(..., description="任务ID")
    result_id: Optional[uuid.UUID] = Field(None, description="结果ID")
    author_id: uuid.UUID = Field(..., description="作者ID")
    parent_id: Optional[uuid.UUID] = Field(None, description="父评论ID")
    is_resolved: bool = Field(..., description="是否已解决")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


class ReviewerProfileBase(BaseModel):
    """审核员档案基础模型"""
    name: str = Field(..., description="姓名", max_length=100)
    email: str = Field(..., description="邮箱", max_length=255)
    phone: Optional[str] = Field(None, description="电话", max_length=20)
    specialties: Optional[List[str]] = Field(None, description="专业领域")
    certifications: Optional[List[Dict[str, Any]]] = Field(None, description="认证信息")
    experience_years: Optional[int] = Field(None, description="经验年数", ge=0)
    max_concurrent_tasks: int = Field(5, description="最大并发任务数", ge=1, le=20)


class ReviewerProfileCreate(ReviewerProfileBase):
    """创建审核员档案模型"""
    user_id: uuid.UUID = Field(..., description="用户ID")


class ReviewerProfileUpdate(BaseModel):
    """更新审核员档案模型"""
    name: Optional[str] = Field(None, description="姓名", max_length=100)
    email: Optional[str] = Field(None, description="邮箱", max_length=255)
    phone: Optional[str] = Field(None, description="电话", max_length=20)
    specialties: Optional[List[str]] = Field(None, description="专业领域")
    certifications: Optional[List[Dict[str, Any]]] = Field(None, description="认证信息")
    experience_years: Optional[int] = Field(None, description="经验年数", ge=0)
    max_concurrent_tasks: Optional[int] = Field(None, description="最大并发任务数", ge=1, le=20)
    is_available: Optional[bool] = Field(None, description="是否可用")


class ReviewerProfileResponse(ReviewerProfileBase):
    """审核员档案响应模型"""
    id: uuid.UUID = Field(..., description="档案ID")
    user_id: uuid.UUID = Field(..., description="用户ID")
    total_reviews: int = Field(..., description="总审核数")
    approved_reviews: int = Field(..., description="通过审核数")
    rejected_reviews: int = Field(..., description="拒绝审核数")
    average_score: Optional[float] = Field(None, description="平均评分")
    accuracy_rate: Optional[float] = Field(None, description="准确率")
    efficiency_score: Optional[float] = Field(None, description="效率评分")
    quality_score: Optional[float] = Field(None, description="质量评分")
    current_workload: int = Field(..., description="当前工作负载")
    is_active: bool = Field(..., description="是否活跃")
    is_available: bool = Field(..., description="是否可用")
    last_active_at: Optional[datetime] = Field(None, description="最后活跃时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


# 统计和分析模型
class ReviewStatistics(BaseModel):
    """审核统计模型"""
    total_tasks: int = Field(..., description="总任务数")
    pending_tasks: int = Field(..., description="待审核任务数")
    in_progress_tasks: int = Field(..., description="审核中任务数")
    completed_tasks: int = Field(..., description="已完成任务数")
    approved_tasks: int = Field(..., description="已通过任务数")
    rejected_tasks: int = Field(..., description="已拒绝任务数")
    average_processing_time: Optional[float] = Field(None, description="平均处理时间")
    average_quality_score: Optional[float] = Field(None, description="平均质量评分")
    high_risk_tasks: int = Field(..., description="高风险任务数")
    
    # 按内容类型统计
    tasks_by_content_type: Dict[str, int] = Field(..., description="按内容类型统计")
    
    # 按优先级统计
    tasks_by_priority: Dict[str, int] = Field(..., description="按优先级统计")
    
    # 时间范围
    period_start: datetime = Field(..., description="统计开始时间")
    period_end: datetime = Field(..., description="统计结束时间") 