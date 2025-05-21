#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import os
import sys
import json
from datetime import datetime, timedelta
import uuid

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from internal.model.config import Config
from internal.model.medical_record import MedicalRecord
from internal.model.diagnosis import DiagnosisResult, DiagnosisStatus
from internal.model.treatment import TreatmentPlan, TreatmentPlanStatus
from internal.service.medical_record_service import MedicalRecordService
from internal.service.diagnosis_service import DiagnosisService
from internal.service.treatment_service import TreatmentService
from internal.repository.medical_record_repository import MedicalRecordRepository
from internal.repository.diagnosis_repository import DiagnosisRepository
from internal.repository.treatment_repository import TreatmentRepository


# 创建测试数据库配置
TEST_DB_CONFIG = {
    "driver": "postgresql",
    "host": os.environ.get("TEST_DB_HOST", "localhost"),
    "port": int(os.environ.get("TEST_DB_PORT", 5432)),
    "user": os.environ.get("TEST_DB_USER", "postgres"),
    "password": os.environ.get("TEST_DB_PASSWORD", "postgres"),
    "dbname": os.environ.get("TEST_DB_NAME", "medical_service_test"),
    "ssl_mode": "disable",
    "max_open_conns": 5,
    "max_idle_conns": 2,
    "conn_max_lifetime": 300
}

# 创建测试服务配置
TEST_SERVICES_CONFIG = {
    "health_data": {
        "host": "localhost",
        "port": 50051
    },
    "med_knowledge": {
        "host": "localhost",
        "port": 50052
    },
    "diagnostic": {
        "inquiry": {
            "host": "localhost",
            "port": 50053
        },
        "listen": {
            "host": "localhost",
            "port": 50054
        },
        "look": {
            "host": "localhost",
            "port": 50055
        },
        "palpation": {
            "host": "localhost",
            "port": 50056
        }
    },
    "rag": {
        "host": "localhost",
        "port": 50057
    }
}


class MedicalServiceIntegrationTest(unittest.TestCase):
    """医疗服务集成测试"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        # 初始化测试数据库和服务
        cls.setup_test_db()
        cls.setup_services()
    
    @classmethod
    def setup_test_db(cls):
        """设置测试数据库"""
        pass
    
    @classmethod
    def setup_services(cls):
        """设置测试服务"""
        # 初始化仓库
        cls.medical_record_repo = MedicalRecordRepository(TEST_DB_CONFIG)
        cls.diagnosis_repo = DiagnosisRepository(TEST_DB_CONFIG)
        cls.treatment_repo = TreatmentRepository(TEST_DB_CONFIG)
        
        # 初始化服务
        cls.medical_record_service = MedicalRecordService(cls.medical_record_repo)
        cls.diagnosis_service = DiagnosisService(cls.diagnosis_repo, TEST_SERVICES_CONFIG)
        cls.treatment_service = TreatmentService(cls.treatment_repo, TEST_SERVICES_CONFIG)
    
    def setUp(self):
        """每个测试方法前执行"""
        # 生成测试用户ID
        self.test_user_id = str(uuid.uuid4())
    
    def test_end_to_end_medical_flow(self):
        """测试端到端医疗流程"""
        # 步骤1：创建医疗记录
        record = self.medical_record_service.create_medical_record(
            user_id=self.test_user_id,
            record_type="初诊",
            record_date=datetime.now(),
            doctor_name="测试医生",
            institution="测试医院",
            chief_complaint="头痛、乏力持续一周",
            diagnosis="疑似气虚血瘀",
            treatment="建议进一步检查"
        )
        self.assertIsNotNone(record)
        self.assertEqual(record.user_id, self.test_user_id)
        
        # 步骤2：请求诊断
        diagnosis_id = self.diagnosis_service.request_diagnosis(
            user_id=self.test_user_id,
            chief_complaint="头痛、乏力持续一周",
            symptoms=["头痛", "乏力", "睡眠不佳", "心悸"],
            health_data={
                "blood_pressure": "125/85",
                "heart_rate": "78",
                "temperature": "36.5"
            },
            diagnostic_methods=["望", "闻", "问", "切"],
            include_western_medicine=True,
            include_tcm=True
        )
        self.assertIsNotNone(diagnosis_id)
        
        # 获取诊断结果
        diagnosis_result = self.diagnosis_service.get_diagnosis_result(diagnosis_id)
        self.assertIsNotNone(diagnosis_result)
        self.assertEqual(diagnosis_result.user_id, self.test_user_id)
        
        # 步骤3：生成治疗方案
        treatment_plan = self.treatment_service.generate_treatment_plan(
            user_id=self.test_user_id,
            diagnosis_id=diagnosis_id,
            treatment_preferences=["中药", "针灸", "生活调理"],
            include_western_medicine=True,
            include_tcm=True
        )
        self.assertIsNotNone(treatment_plan)
        self.assertEqual(treatment_plan.user_id, self.test_user_id)
        self.assertEqual(treatment_plan.diagnosis_id, diagnosis_id)
        self.assertEqual(treatment_plan.status, TreatmentPlanStatus.ACTIVE)
        
        # 步骤4：更新治疗方案状态
        updated_plan = self.treatment_service.update_treatment_plan_status(
            treatment_plan.id, TreatmentPlanStatus.COMPLETED
        )
        self.assertIsNotNone(updated_plan)
        self.assertEqual(updated_plan.status, TreatmentPlanStatus.COMPLETED)
        
        # 步骤5：验证治疗方案列表
        plans, count = self.treatment_service.list_treatment_plans(self.test_user_id)
        self.assertGreaterEqual(count, 1)
        self.assertGreaterEqual(len(plans), 1)
        
        # 清理测试数据
        self._cleanup_test_data(record.id, diagnosis_id, treatment_plan.id)
    
    def _cleanup_test_data(self, record_id, diagnosis_id, treatment_plan_id):
        """清理测试数据"""
        # 这里应该清理创建的测试数据
        # 由于是测试环境，可以不实现具体的清理逻辑
        pass
    
    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        # 清理测试数据库连接等资源
        pass


if __name__ == "__main__":
    unittest.main()