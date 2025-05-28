#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ERP系统集成测试
"""

import os
import unittest
import warnings
from unittest import mock
import pytest
import requests
import json
import uuid
from datetime import datetime, timedelta

# 确保能导入项目模块
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from integration.erp.erp_client import ERPClient, ERPError

# 常量
TEST_API_URL = os.getenv("TEST_ERP_API_URL", "https://erp-api-test.suoke.life")
TEST_API_KEY = os.getenv("TEST_ERP_API_KEY", "test-api-key")


class MockResponse:
    """模拟HTTP响应"""

    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code
        self.text = json.dumps(json_data)

    def json(self):
        return self.json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(f"HTTP Error: {self.status_code}")


class TestERPClient(unittest.TestCase):
    """ERP客户端测试"""

    def setUp(self):
        """测试准备"""
        # 初始化客户端
        self.client = ERPClient(api_url=TEST_API_URL, api_key=TEST_API_KEY, timeout=5)

        # 模拟请求会话
        self.session_patch = mock.patch.object(requests.Session, "request")
        self.mock_session = self.session_patch.start()

        # 忽略ResourceWarning
        warnings.simplefilter("ignore", ResourceWarning)

    def tearDown(self):
        """测试清理"""
        self.session_patch.stop()

    def test_check_doctor_availability(self):
        """测试检查医生可用性"""
        # 准备模拟数据
        doctor_id = "doc123"
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")
        day_after = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S")

        # 配置模拟响应
        mock_response_data = {
            "doctor_id": doctor_id,
            "available": True,
            "available_slots": [
                {
                    "start_time": f"{tomorrow.split('T')[0]}T09:00:00",
                    "end_time": f"{tomorrow.split('T')[0]}T09:30:00",
                },
                {
                    "start_time": f"{tomorrow.split('T')[0]}T10:00:00",
                    "end_time": f"{tomorrow.split('T')[0]}T10:30:00",
                },
            ],
            "working_hours": {
                "morning_start": "09:00",
                "morning_end": "12:00",
                "afternoon_start": "14:00",
                "afternoon_end": "17:00",
            },
        }

        self.mock_session.return_value = MockResponse(mock_response_data, 200)

        # 执行测试
        result = self.client.check_doctor_availability(doctor_id, tomorrow, day_after)

        # 验证结果
        self.assertEqual(result["doctor_id"], doctor_id)
        self.assertEqual(result["available"], True)
        self.assertEqual(len(result["available_slots"]), 2)

        # 验证请求
        self.mock_session.assert_called_once()
        args, kwargs = self.mock_session.call_args

        # 验证URL和请求方法
        self.assertEqual(kwargs["method"], "GET")
        self.assertTrue(
            kwargs["url"].endswith(f"/api/doctors/{doctor_id}/availability")
        )

        # 验证请求参数
        self.assertEqual(kwargs["params"]["start_time"], tomorrow)
        self.assertEqual(kwargs["params"]["end_time"], day_after)

    def test_create_appointment(self):
        """测试创建预约"""
        # 准备模拟数据
        doctor_id = "doc123"
        patient_id = "patient456"
        appointment_time = (datetime.now() + timedelta(days=1)).strftime(
            "%Y-%m-%dT%H:%M:%S"
        )
        appointment_type = "ONLINE_CONSULTATION"
        symptoms = "发热、咳嗽"

        # 配置模拟响应
        appointment_id = f"appt_{uuid.uuid4().hex[:8]}"
        mock_response_data = {
            "appointment_id": appointment_id,
            "doctor_id": doctor_id,
            "patient_id": patient_id,
            "appointment_time": appointment_time,
            "appointment_type": appointment_type,
            "status": "CONFIRMED",
            "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "meeting_link": f"https://meeting.hospital.com/{uuid.uuid4().hex}"
            if appointment_type == "ONLINE_CONSULTATION"
            else "",
            "location": "线上问诊"
            if appointment_type == "ONLINE_CONSULTATION"
            else "主诊室101",
        }

        self.mock_session.return_value = MockResponse(mock_response_data, 201)

        # 执行测试
        result = self.client.create_appointment(
            doctor_id=doctor_id,
            patient_id=patient_id,
            appointment_time=appointment_time,
            appointment_type=appointment_type,
            symptoms=symptoms,
            metadata={"source": "test"},
        )

        # 验证结果
        self.assertEqual(result["appointment_id"], appointment_id)
        self.assertEqual(result["doctor_id"], doctor_id)
        self.assertEqual(result["patient_id"], patient_id)
        self.assertEqual(result["appointment_time"], appointment_time)
        self.assertEqual(result["status"], "CONFIRMED")

        # 验证请求
        self.mock_session.assert_called_once()
        args, kwargs = self.mock_session.call_args

        # 验证URL和请求方法
        self.assertEqual(kwargs["method"], "POST")
        self.assertTrue(kwargs["url"].endswith(f"/api/appointments"))

        # 验证请求体
        self.assertEqual(kwargs["json"]["doctor_id"], doctor_id)
        self.assertEqual(kwargs["json"]["patient_id"], patient_id)
        self.assertEqual(kwargs["json"]["appointment_time"], appointment_time)
        self.assertEqual(kwargs["json"]["appointment_type"], appointment_type)
        self.assertEqual(kwargs["json"]["symptoms"], symptoms)
        self.assertEqual(kwargs["json"]["metadata"], {"source": "test"})

    def test_check_inventory(self):
        """测试检查库存"""
        # 准备模拟数据
        product_ids = ["prod123", "prod456"]

        # 配置模拟响应
        mock_response_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "inventory": {
                "prod123": {
                    "product_id": "prod123",
                    "in_stock": True,
                    "available_quantity": 150,
                    "reserved_quantity": 25,
                    "restock_date": None,
                },
                "prod456": {
                    "product_id": "prod456",
                    "in_stock": False,
                    "available_quantity": 0,
                    "reserved_quantity": 0,
                    "restock_date": (datetime.now() + timedelta(days=7)).strftime(
                        "%Y-%m-%d"
                    ),
                },
            },
        }

        self.mock_session.return_value = MockResponse(mock_response_data, 200)

        # 执行测试
        result = self.client.check_inventory(product_ids)

        # 验证结果
        self.assertEqual(len(result["inventory"]), 2)
        self.assertTrue(result["inventory"]["prod123"]["in_stock"])
        self.assertFalse(result["inventory"]["prod456"]["in_stock"])
        self.assertEqual(result["inventory"]["prod123"]["available_quantity"], 150)
        self.assertEqual(result["inventory"]["prod456"]["available_quantity"], 0)

        # 验证请求
        self.mock_session.assert_called_once()
        args, kwargs = self.mock_session.call_args

        # 验证URL和请求方法
        self.assertEqual(kwargs["method"], "GET")
        self.assertTrue(kwargs["url"].endswith(f"/api/inventory/check"))

        # 验证请求参数
        self.assertEqual(kwargs["params"]["product_ids"], product_ids)

    def test_trace_product(self):
        """测试产品溯源"""
        # 准备模拟数据
        product_id = "prod123"
        batch_id = "batch456"

        # 配置模拟响应
        mock_response_data = {
            "product_name": "有机燕麦",
            "trace_records": [
                {
                    "stage_name": "种植",
                    "location": "黑龙江省五常市",
                    "timestamp": (datetime.now() - timedelta(days=100)).strftime(
                        "%Y-%m-%dT%H:%M:%S"
                    ),
                    "operator": "张农夫",
                    "details": {
                        "soil_type": "黑土",
                        "weather": "适宜",
                        "fertilizer": "有机肥",
                    },
                    "verification_hash": "0x123abc...",
                },
                {
                    "stage_name": "收割",
                    "location": "黑龙江省五常市",
                    "timestamp": (datetime.now() - timedelta(days=60)).strftime(
                        "%Y-%m-%dT%H:%M:%S"
                    ),
                    "operator": "李收割",
                    "details": {
                        "harvesting_method": "机械化",
                        "weather": "晴天",
                        "crop_condition": "优良",
                    },
                    "verification_hash": "0x456def...",
                },
                {
                    "stage_name": "包装",
                    "location": "哈尔滨市包装厂",
                    "timestamp": (datetime.now() - timedelta(days=30)).strftime(
                        "%Y-%m-%dT%H:%M:%S"
                    ),
                    "operator": "王包装",
                    "details": {
                        "packaging_material": "环保纸袋",
                        "quality_inspection": "通过",
                    },
                    "verification_hash": "0x789ghi...",
                },
            ],
            "blockchain_verification_url": f"https://blockchain.explorer.com/verify/{product_id}/{batch_id}",
            "verified": True,
            "qr_code_url": f"https://qrcode.suoke.life/{product_id}/{batch_id}",
        }

        self.mock_session.return_value = MockResponse(mock_response_data, 200)

        # 执行测试
        result = self.client.trace_product(product_id, batch_id)

        # 验证结果
        self.assertEqual(result["product_name"], "有机燕麦")
        self.assertEqual(len(result["trace_records"]), 3)
        self.assertTrue(result["verified"])

        # 验证请求
        self.mock_session.assert_called_once()
        args, kwargs = self.mock_session.call_args

        # 验证URL和请求方法
        self.assertEqual(kwargs["method"], "GET")
        self.assertTrue(kwargs["url"].endswith(f"/api/products/trace"))

        # 验证请求参数
        self.assertEqual(kwargs["params"]["product_id"], product_id)
        self.assertEqual(kwargs["params"]["batch_id"], batch_id)

    def test_error_handling(self):
        """测试错误处理"""
        # 配置模拟失败响应
        error_response = {"error": "NotFound", "message": "医生不存在", "status": 404}

        self.mock_session.return_value = MockResponse(error_response, 404)

        # 执行测试
        with self.assertRaises(ERPError) as context:
            self.client.check_doctor_availability(
                "nonexistent", "2023-01-01T00:00:00", "2023-01-02T00:00:00"
            )

        # 验证异常
        self.assertTrue("ERP API请求失败" in str(context.exception))
        self.assertEqual(context.exception.status_code, 404)

    def test_connection_error(self):
        """测试连接错误"""
        # 配置模拟连接错误
        self.mock_session.side_effect = requests.exceptions.ConnectionError(
            "无法连接到服务器"
        )

        # 执行测试
        with self.assertRaises(ERPError) as context:
            self.client.check_doctor_availability(
                "doc123", "2023-01-01T00:00:00", "2023-01-02T00:00:00"
            )

        # 验证异常
        self.assertTrue("ERP API请求失败" in str(context.exception))


if __name__ == "__main__":
    unittest.main()
