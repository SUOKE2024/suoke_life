#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from datetime import datetime
import uuid

from internal.model.treatment import (
    TreatmentPlan, TreatmentPlanStatus, TCMTreatment, WesternTreatment,
    LifestyleAdjustment, FollowUpPlan, HerbalPrescription, HerbalComponent,
    AcupunctureTreatment, TuinaTreatment, OtherTCMTherapy, MedicationPrescription,
    MedicalProcedure, TestPlan, Referral, DietaryRecommendation, ExerciseRecommendation,
    SleepRecommendation, StressManagement, FollowUpAppointment
)


class TestTreatment(unittest.TestCase):
    """治疗方案模型单元测试"""
    
    def test_create_treatment_plan(self):
        """测试创建治疗方案"""
        # 准备测试数据
        user_id = str(uuid.uuid4())
        diagnosis_id = str(uuid.uuid4())
        
        # 创建治疗方案
        plan = TreatmentPlan.create(user_id, diagnosis_id)
        
        # 验证治疗方案
        self.assertEqual(plan.user_id, user_id)
        self.assertEqual(plan.diagnosis_id, diagnosis_id)
        self.assertEqual(plan.status, TreatmentPlanStatus.ACTIVE)
        self.assertIsNone(plan.tcm_treatment)
        self.assertIsNone(plan.western_treatment)
        self.assertIsNone(plan.lifestyle_adjustment)
        self.assertIsNone(plan.follow_up_plan)
        self.assertIsNotNone(plan.id)
        self.assertIsNotNone(plan.created_at)
        self.assertIsNotNone(plan.updated_at)
        self.assertEqual(plan.created_at, plan.updated_at)
    
    def test_update_status(self):
        """测试更新治疗方案状态"""
        # 创建治疗方案
        plan = TreatmentPlan.create(str(uuid.uuid4()), str(uuid.uuid4()))
        initial_updated_at = plan.updated_at
        
        # 等待一段时间，确保更新时间不同
        import time
        time.sleep(0.001)
        
        # 更新状态
        plan.update_status(TreatmentPlanStatus.COMPLETED)
        
        # 验证更新后的状态
        self.assertEqual(plan.status, TreatmentPlanStatus.COMPLETED)
        self.assertNotEqual(plan.updated_at, initial_updated_at)
    
    def test_update_tcm_treatment(self):
        """测试更新中医治疗方案"""
        # 创建治疗方案
        plan = TreatmentPlan.create(str(uuid.uuid4()), str(uuid.uuid4()))
        
        # 创建中医治疗方案
        tcm_treatment = TCMTreatment(
            herbal_prescriptions=[
                HerbalPrescription(
                    name="补气养阴方",
                    components=[
                        HerbalComponent(
                            herb_name="黄芪",
                            quantity="30",
                            unit="克",
                            preparation="蜜炙"
                        )
                    ],
                    preparation_method="水煎服"
                )
            ],
            acupuncture_treatments=[
                AcupunctureTreatment(
                    acupoints=["足三里", "气海"],
                    technique="平补平泻"
                )
            ]
        )
        
        # 更新中医治疗方案
        plan.update_tcm_treatment(tcm_treatment)
        
        # 验证更新后的中医治疗方案
        self.assertEqual(plan.tcm_treatment, tcm_treatment)
        self.assertEqual(len(plan.tcm_treatment.herbal_prescriptions), 1)
        self.assertEqual(plan.tcm_treatment.herbal_prescriptions[0].name, "补气养阴方")
        self.assertEqual(len(plan.tcm_treatment.acupuncture_treatments), 1)
        self.assertEqual(plan.tcm_treatment.acupuncture_treatments[0].acupoints, ["足三里", "气海"])
    
    def test_update_western_treatment(self):
        """测试更新西医治疗方案"""
        # 创建治疗方案
        plan = TreatmentPlan.create(str(uuid.uuid4()), str(uuid.uuid4()))
        
        # 创建西医治疗方案
        western_treatment = WesternTreatment(
            medications=[
                MedicationPrescription(
                    medication_name="维生素B族",
                    dosage="1片",
                    route="口服",
                    frequency="每日一次",
                    duration="1个月"
                )
            ],
            tests=[
                TestPlan(
                    test_name="血常规",
                    purpose="监测血细胞水平"
                )
            ]
        )
        
        # 更新西医治疗方案
        plan.update_western_treatment(western_treatment)
        
        # 验证更新后的西医治疗方案
        self.assertEqual(plan.western_treatment, western_treatment)
        self.assertEqual(len(plan.western_treatment.medications), 1)
        self.assertEqual(plan.western_treatment.medications[0].medication_name, "维生素B族")
        self.assertEqual(len(plan.western_treatment.tests), 1)
        self.assertEqual(plan.western_treatment.tests[0].test_name, "血常规")
    
    def test_update_lifestyle_adjustment(self):
        """测试更新生活方式调整建议"""
        # 创建治疗方案
        plan = TreatmentPlan.create(str(uuid.uuid4()), str(uuid.uuid4()))
        
        # 创建生活方式调整建议
        lifestyle_adjustment = LifestyleAdjustment(
            dietary=[
                DietaryRecommendation(
                    foods_to_consume=["全谷类", "蔬菜", "水果"],
                    foods_to_avoid=["油炸食品", "加工肉类"]
                )
            ],
            exercise=ExerciseRecommendation(
                exercise_types=["散步", "太极", "瑜伽"],
                intensity="中低强度"
            )
        )
        
        # 更新生活方式调整建议
        plan.update_lifestyle_adjustment(lifestyle_adjustment)
        
        # 验证更新后的生活方式调整建议
        self.assertEqual(plan.lifestyle_adjustment, lifestyle_adjustment)
        self.assertEqual(len(plan.lifestyle_adjustment.dietary), 1)
        self.assertEqual(plan.lifestyle_adjustment.dietary[0].foods_to_consume, ["全谷类", "蔬菜", "水果"])
        self.assertEqual(plan.lifestyle_adjustment.exercise.exercise_types, ["散步", "太极", "瑜伽"])
    
    def test_update_follow_up_plan(self):
        """测试更新随访计划"""
        # 创建治疗方案
        plan = TreatmentPlan.create(str(uuid.uuid4()), str(uuid.uuid4()))
        
        # 创建随访计划
        follow_up_plan = FollowUpPlan(
            appointments=[
                FollowUpAppointment(
                    appointment_type="中医复诊",
                    scheduled_time=datetime.now(),
                    provider="中医师"
                )
            ],
            monitoring_parameters=["能量水平", "睡眠质量"]
        )
        
        # 更新随访计划
        plan.update_follow_up_plan(follow_up_plan)
        
        # 验证更新后的随访计划
        self.assertEqual(plan.follow_up_plan, follow_up_plan)
        self.assertEqual(len(plan.follow_up_plan.appointments), 1)
        self.assertEqual(plan.follow_up_plan.appointments[0].appointment_type, "中医复诊")
        self.assertEqual(plan.follow_up_plan.monitoring_parameters, ["能量水平", "睡眠质量"])


if __name__ == "__main__":
    unittest.main()