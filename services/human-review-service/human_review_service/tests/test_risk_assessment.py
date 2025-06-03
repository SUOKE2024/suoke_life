"""
风险评估模块测试
Risk Assessment Module Tests

测试风险评估引擎的各种功能
"""

import pytest
from datetime import datetime, timezone

from human_review_service.core.risk_assessment import RiskAssessmentEngine
from human_review_service.core.models import ReviewType, ReviewPriority


class TestRiskAssessmentEngine:
    """风险评估引擎测试"""

    def test_init_engine(self):
        """测试初始化风险评估引擎"""
        engine = RiskAssessmentEngine()
        assert engine is not None
        assert hasattr(engine, 'assess_risk')

    def test_assess_medical_diagnosis_risk(self):
        """测试医疗诊断风险评估"""
        engine = RiskAssessmentEngine()
        
        # 高风险医疗内容
        high_risk_content = {
            "symptoms": ["胸痛", "呼吸困难", "心悸", "出汗"],
            "diagnosis": "急性心肌梗死",
            "treatment": "立即就医，紧急介入治疗",
            "severity": "critical"
        }
        
        risk_score = engine.assess_risk(
            content_data=high_risk_content,
            content_type="diagnosis"
        )
        
        assert isinstance(risk_score, float)
        assert 0.0 <= risk_score <= 1.0
        assert risk_score > 0.5  # 高风险分数

    def test_assess_low_risk_content(self):
        """测试低风险内容评估"""
        engine = RiskAssessmentEngine()
        
        # 低风险医疗内容
        low_risk_content = {
            "symptoms": ["轻微头痛"],
            "diagnosis": "紧张性头痛",
            "treatment": "休息，适量饮水",
            "severity": "mild"
        }
        
        result = engine.assess_risk(
            content=low_risk_content,
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.LOW
        )
        
        assert result.risk_score < 4.0  # 低风险分数
        assert result.risk_level == RiskLevel.LOW
        
    def test_assess_medication_risk(self):
        """测试药物建议风险评估"""
        engine = RiskAssessmentEngine()
        
        # 药物相关内容
        medication_content = {
            "medication": "阿司匹林",
            "dosage": "100mg",
            "frequency": "每日一次",
            "contraindications": ["出血性疾病", "严重肝肾功能不全"],
            "side_effects": ["胃肠道反应", "出血风险"]
        }
        
        result = engine.assess_risk(
            content=medication_content,
            review_type=ReviewType.MEDICATION_REVIEW,
            priority=ReviewPriority.NORMAL
        )
        
        assert isinstance(result, RiskAssessmentResult)
        assert result.risk_score > 0
        
    def test_assess_treatment_plan_risk(self):
        """测试治疗方案风险评估"""
        engine = RiskAssessmentEngine()
        
        # 治疗方案内容
        treatment_content = {
            "treatment_type": "手术治疗",
            "procedure": "腹腔镜胆囊切除术",
            "risks": ["麻醉风险", "出血", "感染"],
            "recovery_time": "2-4周",
            "complications": ["胆管损伤", "腹腔感染"]
        }
        
        result = engine.assess_risk(
            content=treatment_content,
            review_type=ReviewType.TREATMENT_PLAN,
            priority=ReviewPriority.HIGH
        )
        
        assert result.risk_score > 5.0  # 手术相关风险较高
        assert result.risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH]

    def test_risk_factors_detection(self):
        """测试风险因素检测"""
        engine = RiskAssessmentEngine()
        
        # 包含多种风险因素的内容
        risky_content = {
            "symptoms": ["急性胸痛", "呼吸困难", "意识模糊"],
            "diagnosis": "急性冠脉综合征",
            "treatment": "紧急PCI",
            "medications": ["肝素", "氯吡格雷", "阿司匹林"],
            "allergies": ["青霉素过敏"],
            "comorbidities": ["糖尿病", "高血压", "肾功能不全"]
        }
        
        result = engine.assess_risk(
            content=risky_content,
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.URGENT
        )
        
        # 检查是否检测到关键风险因素
        risk_factor_types = [factor.factor_type for factor in result.risk_factors]
        assert "emergency_condition" in risk_factor_types
        assert "medication_interaction" in risk_factor_types or "allergy_risk" in risk_factor_types

    def test_priority_impact_on_risk(self):
        """测试优先级对风险评估的影响"""
        engine = RiskAssessmentEngine()
        
        content = {
            "symptoms": ["发热", "咳嗽"],
            "diagnosis": "上呼吸道感染",
            "treatment": "对症治疗"
        }
        
        # 测试不同优先级
        urgent_result = engine.assess_risk(
            content=content,
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.URGENT
        )
        
        normal_result = engine.assess_risk(
            content=content,
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.NORMAL
        )
        
        # 紧急优先级应该有更高的风险分数
        assert urgent_result.risk_score >= normal_result.risk_score

    def test_empty_content_risk(self):
        """测试空内容的风险评估"""
        engine = RiskAssessmentEngine()
        
        result = engine.assess_risk(
            content={},
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.NORMAL
        )
        
        assert result.risk_score >= 0
        assert result.risk_level == RiskLevel.LOW

    def test_malformed_content_handling(self):
        """测试格式错误内容的处理"""
        engine = RiskAssessmentEngine()
        
        # 测试非字典内容
        result = engine.assess_risk(
            content="invalid content",
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.NORMAL
        )
        
        assert result.risk_score >= 0
        assert isinstance(result, RiskAssessmentResult)

    def test_risk_assessment_result_properties(self):
        """测试风险评估结果的属性"""
        engine = RiskAssessmentEngine()
        
        content = {
            "symptoms": ["头痛", "发热"],
            "diagnosis": "感冒",
            "treatment": "休息，多喝水"
        }
        
        result = engine.assess_risk(
            content=content,
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.NORMAL
        )
        
        # 检查结果属性
        assert hasattr(result, 'risk_score')
        assert hasattr(result, 'risk_level')
        assert hasattr(result, 'risk_factors')
        assert hasattr(result, 'assessment_time')
        assert hasattr(result, 'confidence_score')
        
        assert 0 <= result.risk_score <= 10
        assert isinstance(result.risk_level, RiskLevel)
        assert isinstance(result.risk_factors, list)
        assert isinstance(result.assessment_time, datetime)
        assert 0 <= result.confidence_score <= 1.0

    def test_risk_factor_properties(self):
        """测试风险因素的属性"""
        engine = RiskAssessmentEngine()
        
        high_risk_content = {
            "symptoms": ["急性腹痛", "呕血"],
            "diagnosis": "消化道出血",
            "treatment": "紧急内镜检查"
        }
        
        result = engine.assess_risk(
            content=high_risk_content,
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.URGENT
        )
        
        if result.risk_factors:
            factor = result.risk_factors[0]
            assert hasattr(factor, 'factor_type')
            assert hasattr(factor, 'description')
            assert hasattr(factor, 'severity')
            assert hasattr(factor, 'confidence')
            
            assert isinstance(factor.factor_type, str)
            assert isinstance(factor.description, str)
            assert 0 <= factor.severity <= 10
            assert 0 <= factor.confidence <= 1.0

    def test_different_review_types(self):
        """测试不同审核类型的风险评估"""
        engine = RiskAssessmentEngine()
        
        content = {
            "recommendation": "建议定期体检",
            "frequency": "每年一次",
            "items": ["血常规", "肝功能", "肾功能"]
        }
        
        # 测试健康建议类型
        health_result = engine.assess_risk(
            content=content,
            review_type=ReviewType.HEALTH_ADVICE,
            priority=ReviewPriority.NORMAL
        )
        
        # 测试一般咨询类型
        general_result = engine.assess_risk(
            content=content,
            review_type=ReviewType.GENERAL_CONSULTATION,
            priority=ReviewPriority.NORMAL
        )
        
        assert isinstance(health_result, RiskAssessmentResult)
        assert isinstance(general_result, RiskAssessmentResult)
        
        # 健康建议通常风险较低
        assert health_result.risk_score <= 5.0

    def test_risk_level_thresholds(self):
        """测试风险等级阈值"""
        engine = RiskAssessmentEngine()
        
        # 测试不同风险分数对应的风险等级
        test_cases = [
            (1.0, RiskLevel.LOW),
            (3.0, RiskLevel.LOW),
            (5.0, RiskLevel.MEDIUM),
            (7.0, RiskLevel.HIGH),
            (9.0, RiskLevel.HIGH),
        ]
        
        for score, expected_level in test_cases:
            # 创建一个模拟结果来测试风险等级计算
            result = RiskAssessmentResult(
                risk_score=score,
                risk_level=engine._calculate_risk_level(score),
                risk_factors=[],
                assessment_time=datetime.now(timezone.utc),
                confidence_score=0.8
            )
            
            assert result.risk_level == expected_level

    def test_confidence_score_calculation(self):
        """测试置信度分数计算"""
        engine = RiskAssessmentEngine()
        
        # 详细内容应该有更高的置信度
        detailed_content = {
            "symptoms": ["胸痛", "呼吸困难", "心悸"],
            "diagnosis": "急性心肌梗死",
            "treatment": "立即就医",
            "vital_signs": {"血压": "180/100", "心率": "120"},
            "lab_results": {"肌钙蛋白": "升高"},
            "imaging": "心电图显示ST段抬高"
        }
        
        # 简单内容置信度较低
        simple_content = {
            "symptoms": ["不适"],
            "diagnosis": "待查"
        }
        
        detailed_result = engine.assess_risk(
            content=detailed_content,
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.URGENT
        )
        
        simple_result = engine.assess_risk(
            content=simple_content,
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.NORMAL
        )
        
        assert detailed_result.confidence_score >= simple_result.confidence_score

    def test_assessment_time_recording(self):
        """测试评估时间记录"""
        engine = RiskAssessmentEngine()
        
        before_assessment = datetime.now(timezone.utc)
        
        result = engine.assess_risk(
            content={"test": "content"},
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.NORMAL
        )
        
        after_assessment = datetime.now(timezone.utc)
        
        assert before_assessment <= result.assessment_time <= after_assessment

    def test_concurrent_assessments(self):
        """测试并发风险评估"""
        import asyncio
        
        engine = RiskAssessmentEngine()
        
        async def assess_risk_async(content_id):
            content = {
                "id": content_id,
                "symptoms": ["头痛"],
                "diagnosis": "紧张性头痛"
            }
            return engine.assess_risk(
                content=content,
                review_type=ReviewType.MEDICAL_DIAGNOSIS,
                priority=ReviewPriority.NORMAL
            )
        
        async def run_concurrent_assessments():
            tasks = [assess_risk_async(i) for i in range(5)]
            results = await asyncio.gather(*tasks)
            return results
        
        # 运行并发评估
        results = asyncio.run(run_concurrent_assessments())
        
        assert len(results) == 5
        for result in results:
            assert isinstance(result, RiskAssessmentResult)
            assert result.risk_score >= 0 