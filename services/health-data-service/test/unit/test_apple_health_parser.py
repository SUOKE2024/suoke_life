#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
苹果健康数据解析器的单元测试
"""

import unittest
from unittest.mock import patch, mock_open
import xml.etree.ElementTree as ET
import uuid
import tempfile
import os
from datetime import datetime, timedelta

from internal.service.parsers.apple_health_parser import AppleHealthParser
from internal.model.health_data import HealthDataType, DeviceType, MeasurementUnit


class TestAppleHealthParser(unittest.TestCase):
    """苹果健康数据解析器测试类"""

    def setUp(self):
        """测试前的准备工作"""
        self.parser = AppleHealthParser()
        self.test_user_id = str(uuid.uuid4())
        
        # 创建测试XML数据
        self.test_xml = """
        <?xml version="1.0" encoding="UTF-8"?>
        <HealthData>
            <Record type="HKQuantityTypeIdentifierHeartRate" 
                    unit="count/min" 
                    value="78" 
                    sourceName="Apple Watch" 
                    device="&lt;&lt;HKDevice: 0x283e5a9c0, name:Apple Watch, manufacturer:Apple, model:Watch, hardware:Watch5,4, software:7.2&gt;&gt;" 
                    startDate="2023-01-01 10:00:00 +0800" 
                    endDate="2023-01-01 10:00:00 +0800" />
            
            <Record type="HKQuantityTypeIdentifierStepCount" 
                    unit="count" 
                    value="1245" 
                    sourceName="iPhone" 
                    device="&lt;&lt;HKDevice: 0x283e5a9c0, name:iPhone, manufacturer:Apple, model:iPhone13,4, hardware:iPhone13,4, software:16.0&gt;&gt;" 
                    startDate="2023-01-01 07:00:00 +0800" 
                    endDate="2023-01-01 10:00:00 +0800" />
            
            <Record type="HKQuantityTypeIdentifierBloodPressureSystolic" 
                    unit="mmHg" 
                    value="120" 
                    sourceName="Health" 
                    startDate="2023-01-01 09:00:00 +0800" 
                    endDate="2023-01-01 09:00:00 +0800" />
            
            <Record type="HKQuantityTypeIdentifierBloodPressureDiastolic" 
                    unit="mmHg" 
                    value="80" 
                    sourceName="Health" 
                    startDate="2023-01-01 09:00:00 +0800" 
                    endDate="2023-01-01 09:00:00 +0800" />
            
            <Record type="HKCategoryTypeIdentifierSleepAnalysis" 
                    value="HKCategoryValueSleepAnalysisAsleep" 
                    sourceName="Sleep Cycle" 
                    startDate="2023-01-01 23:00:00 +0800" 
                    endDate="2023-01-02 07:00:00 +0800" />
            
            <Record type="HKQuantityTypeIdentifierBodyTemperature" 
                    unit="degC" 
                    value="36.5" 
                    sourceName="Health" 
                    startDate="2023-01-01 08:00:00 +0800" 
                    endDate="2023-01-01 08:00:00 +0800" />
            
            <Record type="HKQuantityTypeIdentifierUnsupportedType" 
                    unit="unknown" 
                    value="100" 
                    sourceName="Health" 
                    startDate="2023-01-01 08:00:00 +0800" 
                    endDate="2023-01-01 08:00:00 +0800" />
        </HealthData>
        """
        
        # 创建临时文件用于测试
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xml")
        self.temp_file.write(self.test_xml.encode('utf-8'))
        self.temp_file.close()
    
    def tearDown(self):
        """测试后的清理工作"""
        # 删除临时文件
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_parse_file(self):
        """测试解析文件功能"""
        health_data, stats = self.parser.parse_file(self.temp_file.name, self.test_user_id)
        
        # 验证解析结果
        self.assertEqual(stats["total_records"], 7)  # 总共7条记录
        self.assertEqual(stats["processed_records"], 5)  # 应该解析出5条有效记录
        self.assertEqual(stats["skipped_records"], 2)  # 应该跳过2条记录
        
        # 验证解析出的数据类型
        data_types = set(item["data_type"] for item in health_data)
        expected_types = {
            HealthDataType.HEART_RATE.value,
            HealthDataType.STEPS.value,
            HealthDataType.BLOOD_PRESSURE.value,
            HealthDataType.SLEEP.value,
            HealthDataType.BODY_TEMPERATURE.value
        }
        self.assertEqual(data_types, expected_types)
    
    def test_parse_heart_rate(self):
        """测试解析心率数据"""
        # 创建心率XML记录
        heart_rate_xml = """
        <Record type="HKQuantityTypeIdentifierHeartRate" 
                unit="count/min" 
                value="78" 
                sourceName="Apple Watch" 
                device="&lt;&lt;HKDevice: 0x283e5a9c0, name:Apple Watch, manufacturer:Apple, model:Watch, hardware:Watch5,4, software:7.2&gt;&gt;" 
                startDate="2023-01-01 10:00:00 +0800" 
                endDate="2023-01-01 10:00:00 +0800" />
        """
        record = ET.fromstring(heart_rate_xml)
        
        # 解析记录
        data = self.parser._parse_record(record, self.test_user_id)
        
        # 验证解析结果
        self.assertIsNotNone(data)
        self.assertEqual(data["data_type"], HealthDataType.HEART_RATE.value)
        self.assertEqual(data["value"], 78.0)
        self.assertEqual(data["unit"], MeasurementUnit.BPM.value)
        self.assertEqual(data["device_type"], DeviceType.APPLE_HEALTH.value)
        self.assertEqual(data["device_id"], "Apple Watch")
        self.assertEqual(data["user_id"], self.test_user_id)
    
    def test_parse_steps(self):
        """测试解析步数数据"""
        # 创建步数XML记录
        steps_xml = """
        <Record type="HKQuantityTypeIdentifierStepCount" 
                unit="count" 
                value="1245" 
                sourceName="iPhone" 
                device="&lt;&lt;HKDevice: 0x283e5a9c0, name:iPhone, manufacturer:Apple, model:iPhone13,4, hardware:iPhone13,4, software:16.0&gt;&gt;" 
                startDate="2023-01-01 07:00:00 +0800" 
                endDate="2023-01-01 10:00:00 +0800" />
        """
        record = ET.fromstring(steps_xml)
        
        # 解析记录
        data = self.parser._parse_record(record, self.test_user_id)
        
        # 验证解析结果
        self.assertIsNotNone(data)
        self.assertEqual(data["data_type"], HealthDataType.STEPS.value)
        self.assertEqual(data["value"], 1245)  # 步数应该是整数
        self.assertEqual(data["unit"], MeasurementUnit.COUNT.value)
        self.assertEqual(data["source"], "iPhone")
    
    def test_process_blood_pressure(self):
        """测试处理血压数据"""
        # 创建收缩压XML记录
        systolic_xml = """
        <Record type="HKQuantityTypeIdentifierBloodPressureSystolic" 
                unit="mmHg" 
                value="120" 
                sourceName="Health" 
                startDate="2023-01-01 09:00:00 +0800" 
                endDate="2023-01-01 09:00:00 +0800" />
        """
        systolic_record = ET.fromstring(systolic_xml)
        
        # 创建舒张压XML记录
        diastolic_xml = """
        <Record type="HKQuantityTypeIdentifierBloodPressureDiastolic" 
                unit="mmHg" 
                value="80" 
                sourceName="Health" 
                startDate="2023-01-01 09:00:00 +0800" 
                endDate="2023-01-01 09:00:00 +0800" />
        """
        diastolic_record = ET.fromstring(diastolic_xml)
        
        # 用于存储血压数据的临时字典
        blood_pressure_data = {}
        
        # 处理收缩压记录
        bp_data = self.parser._process_blood_pressure(systolic_record, blood_pressure_data, self.test_user_id)
        self.assertIsNone(bp_data)  # 只有收缩压应该返回None
        
        # 处理舒张压记录
        bp_data = self.parser._process_blood_pressure(diastolic_record, blood_pressure_data, self.test_user_id)
        
        # 验证解析结果
        self.assertIsNotNone(bp_data)
        self.assertEqual(bp_data["data_type"], HealthDataType.BLOOD_PRESSURE.value)
        self.assertEqual(bp_data["value"]["systolic"], 120.0)
        self.assertEqual(bp_data["value"]["diastolic"], 80.0)
        self.assertEqual(bp_data["unit"], MeasurementUnit.MMHG.value)
    
    def test_process_sleep_data(self):
        """测试处理睡眠数据"""
        # 创建睡眠XML记录
        sleep_xml = """
        <Record type="HKCategoryTypeIdentifierSleepAnalysis" 
                value="HKCategoryValueSleepAnalysisAsleep" 
                sourceName="Sleep Cycle" 
                startDate="2023-01-01 23:00:00 +0800" 
                endDate="2023-01-02 07:00:00 +0800" />
        """
        record = ET.fromstring(sleep_xml)
        
        # 解析记录
        data = self.parser._process_sleep_data(record, self.test_user_id)
        
        # 验证解析结果
        self.assertIsNotNone(data)
        self.assertEqual(data["data_type"], HealthDataType.SLEEP.value)
        self.assertEqual(data["value"]["sleep_state"], "asleep")
        self.assertEqual(data["value"]["duration_hours"], 8.0)  # 8小时的睡眠
        self.assertEqual(data["unit"], MeasurementUnit.HOURS.value)
    
    def test_format_datetime(self):
        """测试日期时间格式化功能"""
        # 测试带时区的日期时间
        dt_str = "2023-01-01 10:00:00 +0800"
        formatted = self.parser._format_datetime(dt_str)
        self.assertEqual(formatted, "2023-01-01T10:00:00+08:00")
        
        # 测试不带时区的日期时间
        dt_str = "2023-01-01 10:00:00"
        formatted = self.parser._format_datetime(dt_str)
        self.assertEqual(formatted, "2023-01-01T10:00:00Z")
        
        # 测试无法解析的日期时间
        dt_str = "invalid_datetime"
        formatted = self.parser._format_datetime(dt_str)
        self.assertEqual(formatted, "invalid_datetime")


if __name__ == "__main__":
    unittest.main() 