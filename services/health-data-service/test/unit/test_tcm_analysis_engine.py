#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
中医数据分析引擎的单元测试
"""

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
import json
import uuid

from internal.service.analytics.tcm_analysis_engine import TCMAnalysisEngine
from internal.model.health_data import HealthDataType, TCMConstitutionType


class TestTCMAnalysisEngine(unittest.TestCase):
    """中医数据分析引擎测试类"""

    def setUp(self):
        """测试前的准备工作"""
        self.engine = TCMAnalysisEngine()
        
        # 创建测试用户ID
        self.test_user_id = str(uuid.uuid4())
        
        # 创建模拟健康数据
        self.test_health_data = self._create_mock_health_data()
    
    def _create_mock_health_data(self):
        """创建模拟健康数据"""
        now = datetime.utcnow()
        
        # 创建包含各种数据类型的健康数据
        health_data = [
            # 脉象数据 - 气虚特征
            {
                "data_type": HealthDataType.PULSE.value,
                "value": {
                    "features": ["weak", "soft", "empty"],
                    "description": "脉象虚弱，柔软，力度不足"
                },
                "timestamp": (now - timedelta(days=1)).isoformat() + "Z",
                "device_type": "tcm_device"
            },
            # 舌象数据 - 气虚特征
            {
                "data_type": HealthDataType.TONGUE.value,
                "value": {
                    "features": ["pale", "teeth_marks", "thin_coating"],
                    "image_url": "http://example.com/tongue_image.jpg"
                },
                "timestamp": (now - timedelta(days=1)).isoformat() + "Z",
                "device_type": "tcm_device"
            },
            # 面色数据 - 气虚特征
            {
                "data_type": HealthDataType.FACE.value,
                "value": {
                    "features": ["pale", "puffy", "lack_luster"],
                    "image_url": "http://example.com/face_image.jpg"
                },
                "timestamp": (now - timedelta(days=1)).isoformat() + "Z",
                "device_type": "tcm_device"
            },
            # 声音数据 - 气虚特征
            {
                "data_type": HealthDataType.VOICE.value,
                "value": {
                    "features": ["weak", "low_volume", "shortness_of_breath"],
                    "audio_url": "http://example.com/voice_sample.mp3"
                },
                "timestamp": (now - timedelta(days=2)).isoformat() + "Z",
                "device_type": "tcm_device"
            },
            # 症状数据 - 气虚特征
            {
                "data_type": HealthDataType.SYMPTOM.value,
                "value": {
                    "features": ["fatigue", "spontaneous_sweating", "poor_appetite"],
                    "severity": "moderate"
                },
                "timestamp": (now - timedelta(days=2)).isoformat() + "Z",
                "device_type": "manual_entry"
            },
            # 心率数据 - 偏低
            {
                "data_type": HealthDataType.HEART_RATE.value,
                "value": 65,
                "unit": "bpm",
                "timestamp": (now - timedelta(days=1)).isoformat() + "Z",
                "device_type": "apple_health"
            },
            # 睡眠数据 - 较长
            {
                "data_type": HealthDataType.SLEEP.value,
                "value": 9.5,
                "unit": "hours",
                "timestamp": (now - timedelta(days=1)).isoformat() + "Z",
                "device_type": "fitbit"
            },
            # 血压数据 - 正常
            {
                "data_type": HealthDataType.BLOOD_PRESSURE.value,
                "value": {
                    "systolic": 118,
                    "diastolic": 75
                },
                "unit": "mmHg",
                "timestamp": (now - timedelta(days=2)).isoformat() + "Z",
                "device_type": "apple_health"
            },
            # 体温数据 - 正常
            {
                "data_type": HealthDataType.BODY_TEMPERATURE.value,
                "value": 36.5,
                "unit": "celsius",
                "timestamp": (now - timedelta(days=2)).isoformat() + "Z",
                "device_type": "apple_health"
            },
            # 活动数据 - 较低
            {
                "data_type": HealthDataType.ACTIVITY.value,
                "value": 5500,
                "unit": "steps",
                "timestamp": (now - timedelta(days=1)).isoformat() + "Z",
                "device_type": "fitbit"
            }
        ]
        
        return health_data
    
    def test_group_data_by_diagnosis(self):
        """测试按四诊分组功能"""
        grouped_data = self.engine._group_data_by_diagnosis(self.test_health_data)
        
        # 验证返回值包含四诊分类
        self.assertIn("inspection", grouped_data)
        self.assertIn("auscultation", grouped_data)
        self.assertIn("inquiry", grouped_data)
        self.assertIn("palpation", grouped_data)
        
        # 验证数据分组正确
        # 望诊
        inspection_data_types = [data["data_type"] for data in grouped_data["inspection"]]
        self.assertIn(HealthDataType.FACE.value, inspection_data_types)
        self.assertIn(HealthDataType.TONGUE.value, inspection_data_types)
        
        # 闻诊
        auscultation_data_types = [data["data_type"] for data in grouped_data["auscultation"]]
        self.assertIn(HealthDataType.VOICE.value, auscultation_data_types)
        
        # 问诊
        inquiry_data_types = [data["data_type"] for data in grouped_data["inquiry"]]
        self.assertIn(HealthDataType.SYMPTOM.value, inquiry_data_types)
        self.assertIn(HealthDataType.SLEEP.value, inquiry_data_types)
        self.assertIn(HealthDataType.ACTIVITY.value, inquiry_data_types)
        
        # 切诊
        palpation_data_types = [data["data_type"] for data in grouped_data["palpation"]]
        self.assertIn(HealthDataType.PULSE.value, palpation_data_types)
        self.assertIn(HealthDataType.HEART_RATE.value, palpation_data_types)
        self.assertIn(HealthDataType.BLOOD_PRESSURE.value, palpation_data_types)
        self.assertIn(HealthDataType.BODY_TEMPERATURE.value, palpation_data_types)
    
    def test_calculate_feature_matching(self):
        """测试特征匹配度计算功能"""
        # 测试脉象数据的特征匹配
        pulse_data = [
            data for data in self.test_health_data 
            if data["data_type"] == HealthDataType.PULSE.value
        ]
        
        feature_scores = self.engine._calculate_feature_matching(
            HealthDataType.PULSE.value, 
            pulse_data
        )
        
        # 验证计算了所有体质的匹配度
        self.assertEqual(len(feature_scores), len(TCMConstitutionType))
        
        # 由于测试数据包含气虚特征，气虚体质的匹配度应该最高
        max_score_type = max(feature_scores.items(), key=lambda x: x[1])[0]
        self.assertEqual(max_score_type, TCMConstitutionType.QI_DEFICIENCY.value)
        
        # 验证匹配度是归一化的
        total_score = sum(feature_scores.values())
        self.assertAlmostEqual(total_score, 1.0, places=4)
    
    def test_determine_constitution_types(self):
        """测试体质类型确定功能"""
        # 模拟各体质得分
        scores = {
            TCMConstitutionType.BALANCED.value: 15.0,
            TCMConstitutionType.QI_DEFICIENCY.value: 45.0,
            TCMConstitutionType.YANG_DEFICIENCY.value: 20.0,
            TCMConstitutionType.YIN_DEFICIENCY.value: 5.0,
            TCMConstitutionType.PHLEGM_DAMPNESS.value: 5.0,
            TCMConstitutionType.DAMPNESS_HEAT.value: 3.0,
            TCMConstitutionType.BLOOD_STASIS.value: 4.0,
            TCMConstitutionType.QI_DEPRESSION.value: 2.0,
            TCMConstitutionType.SPECIAL.value: 1.0
        }
        
        primary_type, secondary_types = self.engine._determine_constitution_types(scores)
        
        # 验证主要体质是得分最高的
        self.assertEqual(primary_type, TCMConstitutionType.QI_DEFICIENCY.value)
        
        # 验证次要体质
        self.assertIn(TCMConstitutionType.YANG_DEFICIENCY.value, secondary_types)
        self.assertIn(TCMConstitutionType.BALANCED.value, secondary_types)
        
        # 验证低得分的体质不在次要体质中
        self.assertNotIn(TCMConstitutionType.SPECIAL.value, secondary_types)
    
    def test_analyze_constitution(self):
        """测试体质分析功能"""
        result = self.engine.analyze_constitution(
            user_id=self.test_user_id,
            health_data=self.test_health_data
        )
        
        # 验证分析结果包含所有必要字段
        self.assertIn("user_id", result)
        self.assertIn("timestamp", result)
        self.assertIn("primary_type", result)
        self.assertIn("secondary_types", result)
        self.assertIn("scores", result)
        self.assertIn("analysis_basis", result)
        self.assertIn("recommendations", result)
        self.assertIn("data_summary", result)
        
        # 验证用户ID正确
        self.assertEqual(result["user_id"], self.test_user_id)
        
        # 验证主要体质是气虚体质
        self.assertEqual(result["primary_type"], TCMConstitutionType.QI_DEFICIENCY.value)
        
        # 验证体质得分总和为100
        scores_sum = sum(result["scores"].values())
        self.assertAlmostEqual(scores_sum, 100.0, places=1)
        
        # 验证分析依据包含各诊法的数据摘要
        self.assertIn("diagnosis_summary", result["analysis_basis"])
        
        # 验证调理建议不为空
        for category in ["diet", "lifestyle", "exercise", "meridian_acupoints", "herbs"]:
            self.assertIn(category, result["recommendations"])
            self.assertTrue(len(result["recommendations"][category]) > 0)
    
    def test_generate_analysis_basis(self):
        """测试分析依据生成功能"""
        # 先按四诊分组数据
        grouped_data = self.engine._group_data_by_diagnosis(self.test_health_data)
        
        # 模拟各体质得分
        scores = {
            TCMConstitutionType.BALANCED.value: 15.0,
            TCMConstitutionType.QI_DEFICIENCY.value: 45.0,
            TCMConstitutionType.YANG_DEFICIENCY.value: 20.0,
            TCMConstitutionType.YIN_DEFICIENCY.value: 5.0,
            TCMConstitutionType.PHLEGM_DAMPNESS.value: 5.0,
            TCMConstitutionType.DAMPNESS_HEAT.value: 3.0,
            TCMConstitutionType.BLOOD_STASIS.value: 4.0,
            TCMConstitutionType.QI_DEPRESSION.value: 2.0,
            TCMConstitutionType.SPECIAL.value: 1.0
        }
        
        analysis_basis = self.engine._generate_analysis_basis(grouped_data, scores)
        
        # 验证分析依据包含所有主要部分
        self.assertIn("diagnosis_summary", analysis_basis)
        self.assertIn("key_indicators", analysis_basis)
        self.assertIn("constitution_evidence", analysis_basis)
        
        # 验证体质证据中包含得分最高的体质
        self.assertIn(TCMConstitutionType.QI_DEFICIENCY.value, analysis_basis["constitution_evidence"])
    
    def test_generate_recommendations(self):
        """测试调理建议生成功能"""
        primary_type = TCMConstitutionType.QI_DEFICIENCY.value
        secondary_types = [TCMConstitutionType.YANG_DEFICIENCY.value]
        
        recommendations = self.engine._generate_recommendations(primary_type, secondary_types)
        
        # 验证包含所有建议类别
        categories = ["diet", "lifestyle", "exercise", "meridian_acupoints", "herbs", "general"]
        for category in categories:
            self.assertIn(category, recommendations)
            self.assertTrue(len(recommendations[category]) > 0)
        
        # 验证建议数量不超过限制
        for category in categories:
            if category in recommendations:
                self.assertLessEqual(len(recommendations[category]), 5)
    
    def test_insufficient_data(self):
        """测试数据不足情况"""
        # 使用空数据列表
        result = self.engine.analyze_constitution(
            user_id=self.test_user_id,
            health_data=[]
        )
        
        # 验证返回错误信息
        self.assertIn("error", result)
        self.assertEqual(result["error"], "insufficient_data")
    
    def test_time_range_filter(self):
        """测试时间范围过滤功能"""
        # 添加一些更早的数据
        now = datetime.utcnow()
        older_data = [
            {
                "data_type": HealthDataType.PULSE.value,
                "value": {
                    "features": ["normal", "regular", "moderate"],
                    "description": "脉象正常有力"
                },
                "timestamp": (now - timedelta(days=40)).isoformat() + "Z",
                "device_type": "tcm_device"
            }
        ]
        
        combined_data = self.test_health_data + older_data
        
        # 使用30天时间范围过滤
        result = self.engine.analyze_constitution(
            user_id=self.test_user_id,
            health_data=combined_data,
            time_range=30
        )
        
        # 验证数据摘要中只有30天内的数据
        self.assertEqual(result["data_summary"]["data_count"], len(self.test_health_data))


if __name__ == "__main__":
    unittest.main()