#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from datetime import datetime
import uuid

from internal.model.diagnosis import (
    DiagnosisRequest, DiagnosisResult, DiagnosisStatus,
    TCMDiagnosis, WesternDiagnosis, LookDiagnosis, ListenSmellDiagnosis,
    InquiryDiagnosis, PalpationDiagnosis, LabTest
)


class TestDiagnosis(unittest.TestCase):
    """诊断模型单元测试"""
    
    def test_create_diagnosis_request(self):
        """测试创建诊断请求"""
        # 准备测试数据
        user_id = str(uuid.uuid4())
        chief_complaint = "头痛、乏力"
        symptoms = ["头痛", "乏力", "睡眠不佳"]
        health_data = {"blood_pressure": "125/85", "heart_rate": "78"}
        diagnostic_methods = ["望", "闻", "问", "切"]
        
        # 创建诊断请求
        request = DiagnosisRequest.create(
            user_id=user_id,
            chief_complaint=chief_complaint,
            symptoms=symptoms,
            health_data=health_data,
            diagnostic_methods=diagnostic_methods,
            include_western_medicine=True,
            include_tcm=True
        )
        
        # 验证请求
        self.assertEqual(request.user_id, user_id)
        self.assertEqual(request.chief_complaint, chief_complaint)
        self.assertEqual(request.symptoms, symptoms)
        self.assertEqual(request.health_data, health_data)
        self.assertEqual(request.diagnostic_methods, diagnostic_methods)
        self.assertTrue(request.include_western_medicine)
        self.assertTrue(request.include_tcm)
        self.assertIsNotNone(request.id)
        self.assertIsNotNone(request.created_at)
    
    def test_create_pending_diagnosis_result(self):
        """测试创建待处理的诊断结果"""
        # 准备测试数据
        user_id = str(uuid.uuid4())
        
        # 创建待处理的诊断结果
        result = DiagnosisResult.create_pending(user_id)
        
        # 验证结果
        self.assertEqual(result.user_id, user_id)
        self.assertEqual(result.status, DiagnosisStatus.PROCESSING)
        self.assertIsNone(result.tcm_diagnosis)
        self.assertIsNone(result.western_diagnosis)
        self.assertIsNone(result.integrated_diagnosis)
        self.assertEqual(len(result.health_advice), 0)
        self.assertIsNotNone(result.id)
        self.assertIsNotNone(result.diagnosis_time)
        self.assertIsNotNone(result.created_at)
    
    def test_complete_diagnosis_result(self):
        """测试完成诊断结果"""
        # 创建待处理的诊断结果
        result = DiagnosisResult.create_pending(str(uuid.uuid4()))
        
        # 创建TCM诊断
        tcm_diagnosis = TCMDiagnosis(
            look=LookDiagnosis(facial_color="偏黄"),
            listen_smell=ListenSmellDiagnosis(voice_quality="声音低沉"),
            inquiry=InquiryDiagnosis(reported_symptoms=["头痛", "乏力"]),
            palpation=PalpationDiagnosis(pulse_diagnosis="脉沉细"),
            pattern_differentiation=["气虚", "阴虚"],
            constitution_type="气虚质"
        )
        
        # 创建Western诊断
        western_diagnosis = WesternDiagnosis(
            possible_conditions=["慢性疲劳综合征", "焦虑症"],
            vital_signs={"blood_pressure": "125/85", "heart_rate": "78"},
            clinical_analysis="患者表现为持续性疲劳",
            confidence_score=85
        )
        
        # 完成诊断
        integrated_diagnosis = "患者从西医角度考虑可能存在慢性疲劳，从中医角度表现为气虚证"
        health_advice = ["保持充足睡眠", "适当运动"]
        
        result.complete(
            tcm_diagnosis=tcm_diagnosis,
            western_diagnosis=western_diagnosis,
            integrated_diagnosis=integrated_diagnosis,
            health_advice=health_advice
        )
        
        # 验证诊断结果
        self.assertEqual(result.status, DiagnosisStatus.COMPLETED)
        self.assertEqual(result.tcm_diagnosis, tcm_diagnosis)
        self.assertEqual(result.western_diagnosis, western_diagnosis)
        self.assertEqual(result.integrated_diagnosis, integrated_diagnosis)
        self.assertEqual(result.health_advice, health_advice)
    
    def test_fail_diagnosis_result(self):
        """测试诊断失败"""
        # 创建待处理的诊断结果
        result = DiagnosisResult.create_pending(str(uuid.uuid4()))
        
        # 标记为失败
        result.fail()
        
        # 验证诊断结果
        self.assertEqual(result.status, DiagnosisStatus.FAILED)
    
    def test_lab_test(self):
        """测试实验室检测结果"""
        # 创建实验室检测结果
        lab_test = LabTest(
            test_name="血常规",
            result="正常",
            unit="",
            reference_range="正常范围",
            is_abnormal=False
        )
        
        # 验证实验室检测结果
        self.assertEqual(lab_test.test_name, "血常规")
        self.assertEqual(lab_test.result, "正常")
        self.assertEqual(lab_test.unit, "")
        self.assertEqual(lab_test.reference_range, "正常范围")
        self.assertFalse(lab_test.is_abnormal)


if __name__ == "__main__":
    unittest.main()