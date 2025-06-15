"""
会话数据模型 - 定义数据库表结构
"""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class InquirySession(Base):
    """问诊会话表"""

    __tablename__ = "inquiry_sessions"

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), unique=True, nullable=False, index=True)

    # 基本信息
    user_id = Column(String(36), nullable=False, index=True)
    agent_id = Column(String(50), nullable=False, default="xiaoai")
    status = Column(String(20), nullable=False, default="active", index=True)  # active, completed, abandoned

    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime)
    ended_at = Column(DateTime)

    # 会话配置和元数据
    session_config = Column(JSON)  # 会话配置信息
    metadata = Column(JSON)  # 额外的元数据

    # 会话统计
    message_count = Column(Integer, default=0)
    duration_seconds = Column(Integer)  # 会话持续时间（秒）

    # 关联关系
    messages = relationship("SessionMessage", back_populates="session", cascade="all, delete-orphan")
    summaries = relationship("SessionSummary", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<InquirySession(session_id='{self.session_id}', user_id='{self.user_id}', status='{self.status}')>"

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "session_config": self.session_config,
            "metadata": self.metadata,
            "message_count": self.message_count,
            "duration_seconds": self.duration_seconds
        }


class SessionMessage(Base):
    """会话消息表"""

    __tablename__ = "session_messages"

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(String(36), unique=True, nullable=False, index=True)

    # 关联信息
    session_id = Column(String(36), ForeignKey("inquiry_sessions.session_id"), nullable=False, index=True)

    # 消息内容
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    content_type = Column(String(20), default="text")  # text, image, audio, etc.

    # 时间戳
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # 消息元数据
    metadata = Column(JSON)  # 额外的消息元数据

    # 消息处理信息
    processing_time = Column(Float)  # 处理时间（秒）
    confidence_score = Column(Float)  # 置信度分数

    # 症状和分析信息
    detected_symptoms = Column(ARRAY(String))  # 检测到的症状
    extracted_entities = Column(JSON)  # 提取的实体信息

    # 关联关系
    session = relationship("InquirySession", back_populates="messages")

    def __repr__(self):
        return f"<SessionMessage(message_id='{self.message_id}', role='{self.role}', session_id='{self.session_id}')>"

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "message_id": self.message_id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
            "content_type": self.content_type,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "metadata": self.metadata,
            "processing_time": self.processing_time,
            "confidence_score": self.confidence_score,
            "detected_symptoms": self.detected_symptoms,
            "extracted_entities": self.extracted_entities
        }


class SessionSummary(Base):
    """会话总结表"""

    __tablename__ = "session_summaries"

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    summary_id = Column(String(36), unique=True, nullable=False, index=True)

    # 关联信息
    session_id = Column(String(36), ForeignKey("inquiry_sessions.session_id"), nullable=False, index=True)

    # 总结内容
    summary_text = Column(Text)  # 会话总结文本
    summary_type = Column(String(20), default="final")  # final, interim, auto

    # 提取的信息
    extracted_symptoms = Column(JSON)  # 提取的症状列表
    symptom_categories = Column(JSON)  # 症状分类

    # 中医分析
    tcm_patterns = Column(JSON)  # 中医证型分析
    constitution_analysis = Column(JSON)  # 体质分析

    # 健康评估
    health_risks = Column(JSON)  # 健康风险评估
    risk_level = Column(String(20))  # 风险等级：low, medium, high

    # 建议和推荐
    recommendations = Column(JSON)  # 健康建议
    follow_up_actions = Column(JSON)  # 后续行动建议

    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 总结元数据
    metadata = Column(JSON)  # 额外的总结元数据

    # 质量评估
    completeness_score = Column(Float)  # 完整性评分
    confidence_score = Column(Float)  # 置信度评分

    # 关联关系
    session = relationship("InquirySession", back_populates="summaries")

    def __repr__(self):
        return f"<SessionSummary(summary_id='{self.summary_id}', session_id='{self.session_id}', type='{self.summary_type}')>"

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "summary_id": self.summary_id,
            "session_id": self.session_id,
            "summary_text": self.summary_text,
            "summary_type": self.summary_type,
            "extracted_symptoms": self.extracted_symptoms,
            "symptom_categories": self.symptom_categories,
            "tcm_patterns": self.tcm_patterns,
            "constitution_analysis": self.constitution_analysis,
            "health_risks": self.health_risks,
            "risk_level": self.risk_level,
            "recommendations": self.recommendations,
            "follow_up_actions": self.follow_up_actions,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": self.metadata,
            "completeness_score": self.completeness_score,
            "confidence_score": self.confidence_score
        }


class SymptomExtraction(Base):
    """症状提取记录表"""

    __tablename__ = "symptom_extractions"

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    extraction_id = Column(String(36), unique=True, nullable=False, index=True)

    # 关联信息
    session_id = Column(String(36), nullable=False, index=True)
    message_id = Column(String(36), nullable=True, index=True)

    # 输入文本
    input_text = Column(Text, nullable=False)
    text_length = Column(Integer)

    # 提取结果
    extracted_symptoms = Column(JSON)  # 提取的症状详细信息
    symptom_count = Column(Integer, default=0)

    # 分析结果
    body_parts = Column(ARRAY(String))  # 涉及的身体部位
    severity_levels = Column(JSON)  # 严重程度分析
    duration_info = Column(JSON)  # 持续时间信息

    # 处理信息
    processing_method = Column(String(50))  # 处理方法
    processing_time = Column(Float)  # 处理时间
    confidence_score = Column(Float)  # 整体置信度

    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # 元数据
    metadata = Column(JSON)

    def __repr__(self):
        return f"<SymptomExtraction(extraction_id='{self.extraction_id}', symptom_count={self.symptom_count})>"

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "extraction_id": self.extraction_id,
            "session_id": self.session_id,
            "message_id": self.message_id,
            "input_text": self.input_text,
            "text_length": self.text_length,
            "extracted_symptoms": self.extracted_symptoms,
            "symptom_count": self.symptom_count,
            "body_parts": self.body_parts,
            "severity_levels": self.severity_levels,
            "duration_info": self.duration_info,
            "processing_method": self.processing_method,
            "processing_time": self.processing_time,
            "confidence_score": self.confidence_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "metadata": self.metadata
        }


class TCMPatternMapping(Base):
    """中医证型映射记录表"""

    __tablename__ = "tcm_pattern_mappings"

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    mapping_id = Column(String(36), unique=True, nullable=False, index=True)

    # 关联信息
    session_id = Column(String(36), nullable=False, index=True)
    extraction_id = Column(String(36), nullable=True, index=True)

    # 输入信息
    input_symptoms = Column(JSON)  # 输入症状
    user_profile = Column(JSON)  # 用户档案信息

    # 映射结果
    matched_patterns = Column(JSON)  # 匹配的证型
    pattern_scores = Column(JSON)  # 证型评分
    primary_pattern = Column(String(100))  # 主要证型

    # 体质分析
    constitution_type = Column(String(50))  # 体质类型
    constitution_score = Column(Float)  # 体质匹配度

    # 分析详情
    pattern_analysis = Column(JSON)  # 证型分析详情
    recommendations = Column(JSON)  # 基于证型的建议

    # 处理信息
    processing_method = Column(String(50))  # 处理方法
    processing_time = Column(Float)  # 处理时间
    confidence_score = Column(Float)  # 整体置信度

    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # 元数据
    metadata = Column(JSON)

    def __repr__(self):
        return f"<TCMPatternMapping(mapping_id='{self.mapping_id}', primary_pattern='{self.primary_pattern}')>"

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "mapping_id": self.mapping_id,
            "session_id": self.session_id,
            "extraction_id": self.extraction_id,
            "input_symptoms": self.input_symptoms,
            "user_profile": self.user_profile,
            "matched_patterns": self.matched_patterns,
            "pattern_scores": self.pattern_scores,
            "primary_pattern": self.primary_pattern,
            "constitution_type": self.constitution_type,
            "constitution_score": self.constitution_score,
            "pattern_analysis": self.pattern_analysis,
            "recommendations": self.recommendations,
            "processing_method": self.processing_method,
            "processing_time": self.processing_time,
            "confidence_score": self.confidence_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "metadata": self.metadata
        }


class HealthRiskAssessment(Base):
    """健康风险评估记录表"""

    __tablename__ = "health_risk_assessments"

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    assessment_id = Column(String(36), unique=True, nullable=False, index=True)

    # 关联信息
    session_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)

    # 输入信息
    input_symptoms = Column(JSON)  # 输入症状
    medical_history = Column(JSON)  # 病史信息
    lifestyle_factors = Column(JSON)  # 生活方式因素

    # 风险评估结果
    risk_categories = Column(JSON)  # 风险分类
    overall_risk_level = Column(String(20))  # 整体风险等级
    risk_score = Column(Float)  # 风险评分

    # 具体风险项
    identified_risks = Column(JSON)  # 识别的风险项
    risk_factors = Column(JSON)  # 风险因素分析

    # 预防建议
    prevention_recommendations = Column(JSON)  # 预防建议
    lifestyle_modifications = Column(JSON)  # 生活方式调整建议
    follow_up_schedule = Column(JSON)  # 随访计划

    # 处理信息
    assessment_method = Column(String(50))  # 评估方法
    processing_time = Column(Float)  # 处理时间
    confidence_score = Column(Float)  # 置信度

    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime)  # 评估有效期

    # 元数据
    metadata = Column(JSON)

    def __repr__(self):
        return f"<HealthRiskAssessment(assessment_id='{self.assessment_id}', risk_level='{self.overall_risk_level}')>"

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "assessment_id": self.assessment_id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "input_symptoms": self.input_symptoms,
            "medical_history": self.medical_history,
            "lifestyle_factors": self.lifestyle_factors,
            "risk_categories": self.risk_categories,
            "overall_risk_level": self.overall_risk_level,
            "risk_score": self.risk_score,
            "identified_risks": self.identified_risks,
            "risk_factors": self.risk_factors,
            "prevention_recommendations": self.prevention_recommendations,
            "lifestyle_modifications": self.lifestyle_modifications,
            "follow_up_schedule": self.follow_up_schedule,
            "assessment_method": self.assessment_method,
            "processing_time": self.processing_time,
            "confidence_score": self.confidence_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "metadata": self.metadata
        }


# 数据库初始化函数
async def create_tables(engine):
    """创建数据库表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables(engine):
    """删除数据库表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# 模型验证函数
def validate_session_status(status: str) -> bool:
    """验证会话状态"""
    valid_statuses = ["active", "completed", "abandoned", "paused"]
    return status in valid_statuses


def validate_message_role(role: str) -> bool:
    """验证消息角色"""
    valid_roles = ["user", "assistant", "system"]
    return role in valid_roles


def validate_risk_level(risk_level: str) -> bool:
    """验证风险等级"""
    valid_levels = ["low", "medium", "high", "critical"]
    return risk_level in valid_levels
