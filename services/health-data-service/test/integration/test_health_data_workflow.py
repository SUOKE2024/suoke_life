#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
健康数据工作流集成测试
测试从数据导入、处理、分析到隐私保护的完整流程
"""

import unittest
import os
import tempfile
import uuid
from datetime import datetime, timedelta
import json
import random

# 导入测试目标组件
from internal.service.parsers.apple_health_parser import AppleHealthParser
from internal.service.analytics.tcm_analysis_engine import TCMAnalysisEngine
from internal.service.blockchain.zkp_client import ZKPClient
from internal.model.health_data import HealthDataType, DeviceType, MeasurementUnit


class TestHealthDataWorkflow(unittest.TestCase):
    """健康数据工作流集成测试类"""

    def setUp(self):
        """测试前的准备工作"""
        # 创建测试用户ID
        self.test_user_id = str(uuid.uuid4())
        
        # 初始化组件
        self.apple_health_parser = AppleHealthParser()
        self.tcm_analysis_engine = TCMAnalysisEngine()
        self.zkp_client = ZKPClient()
        
        # 创建测试XML数据
        self.health_xml = self._create_test_health_xml()
        
        # 创建临时文件用于测试
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xml")
        self.temp_file.write(self.health_xml.encode('utf-8'))
        self.temp_file.close()
    
    def tearDown(self):
        """测试后的清理工作"""
        # 删除临时文件
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def _create_test_health_xml(self):
        """创建测试健康数据XML"""
        # 生成当前日期和之前的日期
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        two_days_ago = now - timedelta(days=2)
        
        # 格式化日期为Apple Health格式
        format_date = lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S +0800")
        now_str = format_date(now)
        yesterday_str = format_date(yesterday)
        two_days_ago_str = format_date(two_days_ago)
        
        # 创建健康数据XML
        xml = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <HealthData>
            <!-- 心率数据 - 略低 -->
            <Record type="HKQuantityTypeIdentifierHeartRate" 
                    unit="count/min" 
                    value="65" 
                    sourceName="Apple Watch" 
                    device="&lt;&lt;HKDevice: 0x283e5a9c0, name:Apple Watch, manufacturer:Apple&gt;&gt;" 
                    startDate="{now_str}" 
                    endDate="{now_str}" />
            
            <!-- 心率数据 - 正常 -->
            <Record type="HKQuantityTypeIdentifierHeartRate" 
                    unit="count/min" 
                    value="72" 
                    sourceName="Apple Watch" 
                    device="&lt;&lt;HKDevice: 0x283e5a9c0, name:Apple Watch, manufacturer:Apple&gt;&gt;" 
                    startDate="{yesterday_str}" 
                    endDate="{yesterday_str}" />
            
            <!-- 步数数据 - 偏低 -->
            <Record type="HKQuantityTypeIdentifierStepCount" 
                    unit="count" 
                    value="5500" 
                    sourceName="iPhone" 
                    device="&lt;&lt;HKDevice: 0x283e5a9c0, name:iPhone, manufacturer:Apple&gt;&gt;" 
                    startDate="{now_str}" 
                    endDate="{now_str}" />
            
            <!-- 步数数据 - 正常 -->
            <Record type="HKQuantityTypeIdentifierStepCount" 
                    unit="count" 
                    value="10200" 
                    sourceName="iPhone" 
                    device="&lt;&lt;HKDevice: 0x283e5a9c0, name:iPhone, manufacturer:Apple&gt;&gt;" 
                    startDate="{yesterday_str}" 
                    endDate="{yesterday_str}" />
            
            <!-- 血压数据 - 正常 -->
            <Record type="HKQuantityTypeIdentifierBloodPressureSystolic" 
                    unit="mmHg" 
                    value="118" 
                    sourceName="Health" 
                    startDate="{now_str}" 
                    endDate="{now_str}" />
            
            <Record type="HKQuantityTypeIdentifierBloodPressureDiastolic" 
                    unit="mmHg" 
                    value="78" 
                    sourceName="Health" 
                    startDate="{now_str}" 
                    endDate="{now_str}" />
            
            <!-- 体温数据 - 正常 -->
            <Record type="HKQuantityTypeIdentifierBodyTemperature" 
                    unit="degC" 
                    value="36.5" 
                    sourceName="Health" 
                    startDate="{now_str}" 
                    endDate="{now_str}" />
            
            <!-- 睡眠数据 - 充足 -->
            <Record type="HKCategoryTypeIdentifierSleepAnalysis" 
                    value="HKCategoryValueSleepAnalysisAsleep" 
                    sourceName="Sleep Cycle" 
                    startDate="{yesterday_str}" 
                    endDate="{now_str}" />
        </HealthData>
        """
        
        return xml
    
    def _create_test_tcm_data(self):
        """创建测试中医特征数据"""
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        
        # 创建气虚体质特征的中医四诊数据
        tcm_data = [
            # 脉象 - 气虚特征
            {
                "data_type": HealthDataType.PULSE.value,
                "value": {
                    "features": ["weak", "soft", "empty"],
                    "description": "脉象虚弱，柔软，力度不足"
                },
                "timestamp": yesterday.isoformat() + "Z",
                "device_type": DeviceType.TCM_DEVICE.value,
                "user_id": self.test_user_id
            },
            # 舌象 - 气虚特征
            {
                "data_type": HealthDataType.TONGUE.value,
                "value": {
                    "features": ["pale", "teeth_marks", "thin_coating"],
                    "image_url": "http://example.com/tongue_image.jpg"
                },
                "timestamp": yesterday.isoformat() + "Z",
                "device_type": DeviceType.TCM_DEVICE.value,
                "user_id": self.test_user_id
            },
            # 面色 - 气虚特征
            {
                "data_type": HealthDataType.FACE.value,
                "value": {
                    "features": ["pale", "puffy", "lack_luster"],
                    "image_url": "http://example.com/face_image.jpg"
                },
                "timestamp": yesterday.isoformat() + "Z",
                "device_type": DeviceType.TCM_DEVICE.value,
                "user_id": self.test_user_id
            },
            # 声音 - 气虚特征
            {
                "data_type": HealthDataType.VOICE.value,
                "value": {
                    "features": ["weak", "low_volume", "shortness_of_breath"],
                    "audio_url": "http://example.com/voice_sample.mp3"
                },
                "timestamp": yesterday.isoformat() + "Z",
                "device_type": DeviceType.TCM_DEVICE.value,
                "user_id": self.test_user_id
            },
            # 症状 - 气虚特征
            {
                "data_type": HealthDataType.SYMPTOM.value,
                "value": {
                    "features": ["fatigue", "spontaneous_sweating", "poor_appetite"],
                    "severity": "moderate"
                },
                "timestamp": yesterday.isoformat() + "Z",
                "device_type": DeviceType.MANUAL_ENTRY.value,
                "user_id": self.test_user_id
            }
        ]
        
        return tcm_data
    
    def test_end_to_end_workflow(self):
        """测试端到端工作流"""
        # 1. 解析Apple Health数据
        health_data, stats = self.apple_health_parser.parse_file(self.temp_file.name, self.test_user_id)
        
        # 验证数据解析
        self.assertGreater(len(health_data), 0)
        self.assertIn("processed_records", stats)
        self.assertGreaterEqual(stats["processed_records"], 7)  # 至少7条记录
        
        # 2. 添加中医四诊数据
        tcm_data = self._create_test_tcm_data()
        combined_data = health_data + tcm_data
        
        # 验证数据合并
        self.assertEqual(len(combined_data), len(health_data) + len(tcm_data))
        
        # 3. 执行中医体质分析
        constitution_result = self.tcm_analysis_engine.analyze_constitution(
            user_id=self.test_user_id,
            health_data=combined_data
        )
        
        # 验证体质分析结果
        self.assertIn("primary_type", constitution_result)
        self.assertIn("secondary_types", constitution_result)
        self.assertIn("scores", constitution_result)
        self.assertIn("recommendations", constitution_result)
        
        # 由于测试数据添加了气虚体质特征，预期主要体质为气虚
        self.assertEqual(constitution_result["primary_type"], "qi_deficiency")
        
        # 4. 测试零知识证明
        # 使用体质分析结果生成证明
        proof = self.zkp_client.generate_health_data_proof(
            user_id=self.test_user_id,
            data=constitution_result
        )
        
        # 验证证明
        is_valid, message = self.zkp_client.verify_health_data_proof(proof, constitution_result)
        self.assertTrue(is_valid)
        self.assertEqual(message, "证明验证成功")
        
        # 5. 测试选择性披露
        # 只披露主要体质和建议，隐藏详细分析和得分
        disclosed_fields = ["user_id", "primary_type", "secondary_types", "recommendations"]
        
        selective_proof = self.zkp_client.generate_selective_disclosure_proof(
            user_id=self.test_user_id,
            data=constitution_result,
            disclosed_fields=disclosed_fields
        )
        
        # 验证选择性披露
        is_valid, message, disclosed_data = self.zkp_client.verify_selective_disclosure(selective_proof)
        self.assertTrue(is_valid)
        
        # 验证只有指定字段被披露
        self.assertEqual(len(disclosed_data), len(disclosed_fields))
        for field in disclosed_fields:
            self.assertIn(field, disclosed_data)
        
        # 验证未披露字段确实被隐藏
        hidden_fields = ["scores", "analysis_basis", "data_summary"]
        for field in hidden_fields:
            self.assertNotIn(field, disclosed_data)
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试空数据处理
        empty_result = self.tcm_analysis_engine.analyze_constitution(
            user_id=self.test_user_id,
            health_data=[]
        )
        
        # 验证空数据返回错误信息
        self.assertIn("error", empty_result)
        self.assertEqual(empty_result["error"], "insufficient_data")
        
        # 测试无效文件处理
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as invalid_file:
            invalid_file.write(b"<invalid>XML</invalid>")
        
        try:
            # 解析无效XML
            health_data, stats = self.apple_health_parser.parse_file(invalid_file.name, self.test_user_id)
            
            # 验证错误处理
            self.assertEqual(len(health_data), 0)
            self.assertIn("error", stats)
        finally:
            os.unlink(invalid_file.name)


if __name__ == "__main__":
    unittest.main() 