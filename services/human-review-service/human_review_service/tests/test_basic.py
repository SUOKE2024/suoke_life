"""
基础功能测试
Basic Functionality Tests

测试核心模块的基本功能
"""

import pytest
from datetime import datetime
from uuid import uuid4

from ..core.service import HumanReviewService
from ..core.models import (
    ReviewerCreate, ReviewTaskCreate, ReviewType, ReviewPriority,
    ReviewStatus, ReviewerStatus, ReviewDecision
)


class TestBasicFunctionality:
    """基础功能测试"""
    
    def test_service_initialization(self):
        """测试服务初始化"""
        service = HumanReviewService()
        assert service is not None
        assert service.risk_engine is not None
        assert service.assignment_engine is not None
    
    def test_reviewer_create_model(self):
        """测试审核员创建模型"""
        reviewer_data = ReviewerCreate(
            reviewer_id="test_reviewer_001",
            name="测试医生",
            email="test@example.com",
            specialties=["中医诊断", "方剂学"],
            max_concurrent_tasks=5
        )
        
        assert reviewer_data.reviewer_id == "test_reviewer_001"
        assert reviewer_data.name == "测试医生"
        assert reviewer_data.email == "test@example.com"
        assert reviewer_data.specialties == ["中医诊断", "方剂学"]
        assert reviewer_data.max_concurrent_tasks == 5
    
    def test_review_task_create_model(self):
        """测试审核任务创建模型"""
        task_data = ReviewTaskCreate(
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.NORMAL,
            content={
                "symptoms": ["头痛", "发热"],
                "diagnosis": "感冒",
                "treatment": "多休息，多喝水"
            },
            user_id="user_123",
            agent_id="xiaoai_agent",
            estimated_duration=1800
        )
        
        assert task_data.review_type == ReviewType.MEDICAL_DIAGNOSIS
        assert task_data.priority == ReviewPriority.NORMAL
        assert task_data.user_id == "user_123"
        assert task_data.agent_id == "xiaoai_agent"
        assert task_data.estimated_duration == 1800
        assert "symptoms" in task_data.content
    
    def test_review_decision_model(self):
        """测试审核决策模型"""
        decision = ReviewDecision(
            decision=ReviewStatus.APPROVED,
            comments="诊断准确，建议合理",
            reviewer_notes="患者症状典型，治疗方案适当",
            review_result={
                "approved": True,
                "quality_score": 0.95,
                "suggestions": ["可以增加一些预防措施"]
            }
        )
        
        assert decision.decision == ReviewStatus.APPROVED
        assert decision.comments == "诊断准确，建议合理"
        assert decision.reviewer_notes == "患者症状典型，治疗方案适当"
        assert decision.review_result["approved"] is True
        assert decision.review_result["quality_score"] == 0.95
    
    def test_risk_assessment_engine(self):
        """测试风险评估引擎"""
        service = HumanReviewService()
        
        # 测试低风险内容
        low_risk_content = {
            "symptoms": ["轻微头痛"],
            "diagnosis": "紧张性头痛",
            "treatment": "休息，放松"
        }
        
        risk_score = service.risk_engine.assess_risk(
            content_data=low_risk_content,
            content_type="diagnosis"
        )
        
        assert 0.0 <= risk_score <= 1.0
        
        # 测试高风险内容
        high_risk_content = {
            "symptoms": ["胸痛", "呼吸困难"],
            "diagnosis": "急性心肌梗死",
            "treatment": "紧急手术"
        }
        
        high_risk_score = service.risk_engine.assess_risk(
            content_data=high_risk_content,
            content_type="emergency"
        )
        
        assert 0.0 <= high_risk_score <= 1.0
        assert high_risk_score > risk_score  # 高风险内容应该有更高的风险评分
    
    def test_enums(self):
        """测试枚举类型"""
        # 测试审核状态
        assert ReviewStatus.PENDING == "pending"
        assert ReviewStatus.APPROVED == "approved"
        assert ReviewStatus.REJECTED == "rejected"
        
        # 测试审核类型
        assert ReviewType.MEDICAL_DIAGNOSIS == "medical_diagnosis"
        assert ReviewType.HEALTH_PLAN == "health_plan"
        
        # 测试优先级
        assert ReviewPriority.LOW == "low"
        assert ReviewPriority.NORMAL == "normal"
        assert ReviewPriority.HIGH == "high"
        assert ReviewPriority.URGENT == "urgent"
        assert ReviewPriority.CRITICAL == "critical"
        
        # 测试审核员状态
        assert ReviewerStatus.ACTIVE == "active"
        assert ReviewerStatus.INACTIVE == "inactive"
        assert ReviewerStatus.BUSY == "busy"
    
    def test_priority_comparison(self):
        """测试优先级比较"""
        priorities = [
            ReviewPriority.LOW,
            ReviewPriority.NORMAL,
            ReviewPriority.HIGH,
            ReviewPriority.URGENT,
            ReviewPriority.CRITICAL
        ]
        
        # 确保所有优先级都是有效的字符串
        for priority in priorities:
            assert isinstance(priority.value, str)
            assert len(priority.value) > 0
    
    def test_review_type_mapping(self):
        """测试审核类型映射"""
        service = HumanReviewService()
        
        # 测试专业领域映射
        medical_specialties = service.assignment_engine.specialty_mapping.get("medical_diagnosis", [])
        assert len(medical_specialties) > 0
        assert "中医诊断" in medical_specialties or "西医诊断" in medical_specialties
        
        medication_specialties = service.assignment_engine.specialty_mapping.get("medication_review", [])
        assert len(medication_specialties) > 0
        assert "药学" in medication_specialties or "临床药学" in medication_specialties 