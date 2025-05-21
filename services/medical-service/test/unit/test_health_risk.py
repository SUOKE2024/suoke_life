#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from datetime import datetime
import uuid

from internal.model.health_risk import (
    HealthRiskAssessment, HealthRiskAssessmentRequest,
    DiseaseRisk, ConstitutionRisk, RiskLevel
)


class TestHealthRisk(unittest.TestCase):
    """健康风险评估模型单元测试"""
    
    def test_create_health_risk_request(self):
        """测试创建健康风险评估请求"""
        # 准备测试数据
        user_id = str(uuid.uuid4())
        health_data = {"blood_pressure": "125/85", "heart_rate": "78"}
        family_history = ["高血压", "糖尿病"]
        lifestyle_factors = {"smoking": "no", "exercise": "moderate"}
        environmental_factors = ["空气污染"]
        
        # 创建健康风险评估请求
        request = HealthRiskAssessmentRequest.create(
            user_id=user_id,
            health_data=health_data,
            family_history=family_history,
            lifestyle_factors=lifestyle_factors,
            environmental_factors=environmental_factors,
            include_genetic_analysis=True
        )
        
        # 验证请求
        self.assertEqual(request.user_id, user_id)
        self.assertEqual(request.health_data, health_data)
        self.assertEqual(request.family_history, family_history)
        self.assertEqual(request.lifestyle_factors, lifestyle_factors)
        self.assertEqual(request.environmental_factors, environmental_factors)
        self.assertTrue(request.include_genetic_analysis)
        self.assertIsNotNone(request.id)
        self.assertIsNotNone(request.created_at)
    
    def test_create_health_risk_assessment(self):
        """测试创建健康风险评估结果"""
        # 准备测试数据
        user_id = str(uuid.uuid4())
        overall_risk_score = 65
        risk_level = RiskLevel.MODERATE
        
        # 创建健康风险评估结果
        assessment = HealthRiskAssessment.create(
            user_id=user_id,
            overall_risk_score=overall_risk_score,
            risk_level=risk_level
        )
        
        # 验证评估结果
        self.assertEqual(assessment.user_id, user_id)
        self.assertEqual(assessment.overall_risk_score, overall_risk_score)
        self.assertEqual(assessment.risk_level, risk_level)
        self.assertEqual(len(assessment.disease_risks), 0)
        self.assertIsNone(assessment.constitution_risk)
        self.assertEqual(len(assessment.prevention_recommendations), 0)
        self.assertEqual(len(assessment.lifestyle_recommendations), 0)
        self.assertEqual(len(assessment.recommended_screenings), 0)
        self.assertIsNotNone(assessment.id)
        self.assertIsNotNone(assessment.assessment_date)
        self.assertIsNotNone(assessment.created_at)
    
    def test_add_disease_risk(self):
        """测试添加疾病风险"""
        # 创建健康风险评估结果
        assessment = HealthRiskAssessment.create(
            user_id=str(uuid.uuid4()),
            overall_risk_score=65,
            risk_level=RiskLevel.MODERATE
        )
        
        # 创建疾病风险
        disease_risk = DiseaseRisk(
            disease_name="心血管疾病",
            risk_score=70,
            risk_level=RiskLevel.HIGH,
            risk_factors=["高血压", "家族史"],
            preventive_measures=["控制血压", "健康饮食"]
        )
        
        # 添加疾病风险
        assessment.add_disease_risk(disease_risk)
        
        # 验证疾病风险
        self.assertEqual(len(assessment.disease_risks), 1)
        self.assertEqual(assessment.disease_risks[0], disease_risk)
        self.assertEqual(assessment.disease_risks[0].disease_name, "心血管疾病")
        self.assertEqual(assessment.disease_risks[0].risk_score, 70)
        self.assertEqual(assessment.disease_risks[0].risk_level, RiskLevel.HIGH)
    
    def test_update_constitution_risk(self):
        """测试更新体质风险"""
        # 创建健康风险评估结果
        assessment = HealthRiskAssessment.create(
            user_id=str(uuid.uuid4()),
            overall_risk_score=65,
            risk_level=RiskLevel.MODERATE
        )
        
        # 创建体质风险
        constitution_risk = ConstitutionRisk(
            constitution_type="气虚质",
            imbalances=["气虚", "阴虚"],
            vulnerable_systems=["脾胃系统", "肺系统"],
            protective_measures=["食补养气", "适当运动"]
        )
        
        # 更新体质风险
        assessment.update_constitution_risk(constitution_risk)
        
        # 验证体质风险
        self.assertEqual(assessment.constitution_risk, constitution_risk)
        self.assertEqual(assessment.constitution_risk.constitution_type, "气虚质")
        self.assertEqual(assessment.constitution_risk.imbalances, ["气虚", "阴虚"])
        self.assertEqual(assessment.constitution_risk.vulnerable_systems, ["脾胃系统", "肺系统"])
    
    def test_add_recommendations(self):
        """测试添加各种建议"""
        # 创建健康风险评估结果
        assessment = HealthRiskAssessment.create(
            user_id=str(uuid.uuid4()),
            overall_risk_score=65,
            risk_level=RiskLevel.MODERATE
        )
        
        # 添加预防建议
        prevention_recommendation = "定期体检，建立健康档案"
        assessment.add_prevention_recommendation(prevention_recommendation)
        
        # 添加生活方式建议
        lifestyle_recommendation = "均衡饮食，确保摄入足够的蔬菜、水果"
        assessment.add_lifestyle_recommendation(lifestyle_recommendation)
        
        # 添加建议筛查
        recommended_screening = "每年进行血脂检查"
        assessment.add_recommended_screening(recommended_screening)
        
        # 验证各种建议
        self.assertEqual(len(assessment.prevention_recommendations), 1)
        self.assertEqual(assessment.prevention_recommendations[0], prevention_recommendation)
        
        self.assertEqual(len(assessment.lifestyle_recommendations), 1)
        self.assertEqual(assessment.lifestyle_recommendations[0], lifestyle_recommendation)
        
        self.assertEqual(len(assessment.recommended_screenings), 1)
        self.assertEqual(assessment.recommended_screenings[0], recommended_screening)


if __name__ == "__main__":
    unittest.main()