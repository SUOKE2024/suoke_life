"""
风险评估引擎测试
"""

import pytest
from unittest.mock import Mock, patch

from human_review_service.core.risk_assessment import RiskAssessmentEngine


class TestRiskAssessmentEngine:
    """风险评估引擎测试类"""

    @pytest.fixture
    def engine(self):
        """创建风险评估引擎实例"""
        return RiskAssessmentEngine()

    def test_init(self, engine):
        """测试初始化"""
        assert engine.risk_factors is not None
        assert "high_risk_symptoms" in engine.risk_factors
        assert "medication_interactions" in engine.risk_factors
        assert "age_thresholds" in engine.risk_factors
        assert "severity_keywords" in engine.risk_factors

    def test_assess_risk_basic(self, engine):
        """测试基础风险评估"""
        content_data = {
            "symptoms": ["头痛"],
            "diagnosis": "感冒",
            "age": "30"
        }
        
        risk_score = engine.assess_risk(content_data, "diagnosis")
        
        assert 0.0 <= risk_score <= 1.0
        assert isinstance(risk_score, float)

    def test_assess_risk_high_risk_symptoms(self, engine):
        """测试高风险症状评估"""
        content_data = {
            "symptoms": ["胸痛", "呼吸困难"],
            "diagnosis": "心脏病"
        }
        
        risk_score = engine.assess_risk(content_data, "diagnosis")
        
        # 应该有较高的风险评分
        assert risk_score > 0.5

    def test_assess_risk_medication_interactions(self, engine):
        """测试药物相互作用风险"""
        content_data = {
            "medications": ["华法林", "胰岛素"],
            "treatment": "药物治疗"
        }
        
        risk_score = engine.assess_risk(content_data, "medication")
        
        # 应该有较高的风险评分
        assert risk_score > 0.6

    def test_assess_risk_elderly_patient(self, engine):
        """测试老年患者风险"""
        content_data = {
            "age": "70",
            "symptoms": ["头晕"]
        }
        
        risk_score = engine.assess_risk(content_data, "diagnosis")
        
        # 老年患者应该有额外的风险评分
        assert risk_score > 0.3

    def test_assess_risk_pediatric_patient(self, engine):
        """测试儿童患者风险"""
        content_data = {
            "age": "5",
            "symptoms": ["发热"]
        }
        
        risk_score = engine.assess_risk(content_data, "diagnosis")
        
        # 儿童患者应该有额外的风险评分
        assert risk_score > 0.3

    def test_assess_risk_severity_keywords(self, engine):
        """测试严重性关键词风险"""
        content_data = {
            "diagnosis": "急性心肌梗死",
            "symptoms": ["严重胸痛"],
            "treatment": "紧急手术"
        }
        
        risk_score = engine.assess_risk(content_data, "emergency")
        
        # 包含严重性关键词应该有很高的风险评分
        assert risk_score > 0.8

    def test_assess_risk_with_metadata(self, engine):
        """测试使用元数据的风险评估"""
        content_data = {
            "symptoms": ["头痛"]
        }
        metadata = {
            "patient_age": "75",
            "urgency": "high"
        }
        
        risk_score = engine.assess_risk(content_data, "diagnosis", metadata)
        
        # 元数据中的年龄应该影响风险评分
        assert risk_score > 0.3

    def test_assess_risk_empty_content(self, engine):
        """测试空内容的风险评估"""
        content_data = {}
        
        risk_score = engine.assess_risk(content_data, "diagnosis")
        
        # 空内容应该返回基础风险
        assert 0.0 <= risk_score <= 1.0

    def test_assess_risk_invalid_content_type(self, engine):
        """测试无效内容类型"""
        content_data = {"symptoms": ["头痛"]}
        
        risk_score = engine.assess_risk(content_data, "unknown_type")
        
        # 未知类型应该使用默认基础风险
        assert 0.0 <= risk_score <= 1.0

    def test_get_base_risk(self, engine):
        """测试基础风险计算"""
        # 测试各种内容类型的基础风险
        assert engine._get_base_risk("diagnosis") == 0.3
        assert engine._get_base_risk("treatment") == 0.4
        assert engine._get_base_risk("medication") == 0.5
        assert engine._get_base_risk("surgery") == 0.7
        assert engine._get_base_risk("emergency") == 0.8
        assert engine._get_base_risk("unknown") == 0.3  # 默认值

    def test_assess_symptom_risk(self, engine):
        """测试症状风险评估"""
        # 高风险症状
        content_data = {"symptoms": ["胸痛", "呼吸困难"]}
        risk = engine._assess_symptom_risk(content_data)
        assert risk > 0.0

        # 低风险症状
        content_data = {"symptoms": ["轻微头痛"]}
        risk = engine._assess_symptom_risk(content_data)
        assert risk >= 0.0

        # 字符串格式症状
        content_data = {"symptoms": "胸痛"}
        risk = engine._assess_symptom_risk(content_data)
        assert risk > 0.0

    def test_assess_medication_risk(self, engine):
        """测试药物风险评估"""
        # 高风险药物
        content_data = {"medications": ["华法林"]}
        risk = engine._assess_medication_risk(content_data)
        assert risk > 0.0

        # 字符串格式药物
        content_data = {"medications": "华法林"}
        risk = engine._assess_medication_risk(content_data)
        assert risk > 0.0

        # 处方中的高风险药物
        content_data = {"prescription": "胰岛素注射"}
        risk = engine._assess_medication_risk(content_data)
        assert risk > 0.0

    def test_assess_age_risk(self, engine):
        """测试年龄风险评估"""
        # 老年人
        content_data = {"age": "70"}
        risk = engine._assess_age_risk(content_data, None)
        assert risk > 0.0

        # 儿童
        content_data = {"age": "10"}
        risk = engine._assess_age_risk(content_data, None)
        assert risk > 0.0

        # 成年人
        content_data = {"age": "30"}
        risk = engine._assess_age_risk(content_data, None)
        assert risk == 0.0

        # 从元数据获取年龄
        content_data = {}
        metadata = {"patient_age": "75"}
        risk = engine._assess_age_risk(content_data, metadata)
        assert risk > 0.0

        # 无效年龄
        content_data = {"age": "invalid"}
        risk = engine._assess_age_risk(content_data, None)
        assert risk == 0.0

    def test_assess_severity_risk(self, engine):
        """测试严重性风险评估"""
        # 包含严重性关键词
        content_data = {
            "diagnosis": "急性心肌梗死",
            "symptoms": ["严重胸痛"]
        }
        risk = engine._assess_severity_risk(content_data)
        assert risk > 0.0

        # 不包含严重性关键词
        content_data = {
            "diagnosis": "轻微感冒",
            "symptoms": ["轻微头痛"]
        }
        risk = engine._assess_severity_risk(content_data)
        assert risk == 0.0

    @patch('human_review_service.core.risk_assessment.logger')
    def test_assess_risk_exception_handling(self, mock_logger, engine):
        """测试异常处理"""
        # 模拟异常
        with patch.object(engine, '_get_base_risk', side_effect=Exception("Test error")):
            content_data = {"symptoms": ["头痛"]}
            risk_score = engine.assess_risk(content_data, "diagnosis")
            
            # 异常时应该返回中等风险
            assert risk_score == 0.5
            mock_logger.error.assert_called_once()

    def test_risk_score_bounds(self, engine):
        """测试风险评分边界"""
        # 测试极高风险情况
        content_data = {
            "symptoms": ["胸痛", "呼吸困难", "意识模糊"],
            "medications": ["华法林", "胰岛素", "地高辛"],
            "diagnosis": "急性严重心肌梗死",
            "age": "80"
        }
        
        risk_score = engine.assess_risk(content_data, "emergency")
        
        # 风险评分不应超过1.0
        assert risk_score <= 1.0
        assert risk_score >= 0.0

    def test_different_content_types(self, engine):
        """测试不同内容类型的风险评估"""
        content_data = {"symptoms": ["头痛"]}
        
        # 测试所有内容类型
        content_types = ["diagnosis", "treatment", "medication", "surgery", "emergency", "prescription", "lifestyle", "nutrition"]
        
        for content_type in content_types:
            risk_score = engine.assess_risk(content_data, content_type)
            assert 0.0 <= risk_score <= 1.0

    def test_complex_content_structure(self, engine):
        """测试复杂内容结构"""
        content_data = {
            "symptoms": ["胸痛", "呼吸困难"],
            "medications": ["华法林"],
            "diagnosis": "急性心肌梗死",
            "treatment": "紧急手术",
            "age": "70",
            "chief_complaint": "严重胸痛",
            "prescription": "胰岛素注射",
            "additional_info": {
                "severity": "high",
                "urgency": "immediate"
            }
        }
        
        risk_score = engine.assess_risk(content_data, "emergency")
        
        # 复杂高风险内容应该有很高的评分
        assert risk_score > 0.8 