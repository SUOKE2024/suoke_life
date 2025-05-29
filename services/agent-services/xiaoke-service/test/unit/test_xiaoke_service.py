#!/usr/bin/env python

"""
小克服务(XiaoKeService) 单元测试
"""

import datetime
import os
import sys
import unittest
from unittest import mock

from google.protobuf.timestamp_pb2 import Timestamp

# 确保能够导入项目模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from api.grpc import xiaoke_service_pb2
from internal.delivery.xiaoke_service_impl import XiaoKeServiceServicer
from internal.inventory.product_manager import ProductManager
from internal.repository.subscription_repository import SubscriptionRepository
from internal.scheduler.resource_manager import ResourceManager


class TestXiaoKeService(unittest.TestCase):
    """小克服务单元测试"""

    def setUp(self):
        """测试准备"""
        # 模拟依赖组件
        self.resource_manager_mock = mock.MagicMock(spec=ResourceManager)
        self.product_manager_mock = mock.MagicMock(spec=ProductManager)
        self.subscription_repo_mock = mock.MagicMock(spec=SubscriptionRepository)

        # 注入被测试对象中的模拟依赖
        with (
            mock.patch(
                "internal.delivery.xiaoke_service_impl.ResourceManager",
                return_value=self.resource_manager_mock,
            ),
            mock.patch(
                "internal.delivery.xiaoke_service_impl.ProductManager",
                return_value=self.product_manager_mock,
            ),
            mock.patch(
                "internal.delivery.xiaoke_service_impl.SubscriptionRepository",
                return_value=self.subscription_repo_mock,
            ),
        ):
            self.service = XiaoKeServiceServicer()

    def test_check_inventory(self):
        """测试库存检查功能"""
        # 准备测试数据
        self.product_manager_mock.check_inventory.return_value = {
            "product_id": "PROD-001",
            "name": "人参",
            "available": 100,
            "reserved": 50,
            "location": "A区-12-15",
            "status": "AVAILABLE",
        }

        # 准备请求对象
        request = xiaoke_service_pb2.InventoryCheckRequest(product_id="PROD-001")

        # 执行被测试方法
        context = mock.MagicMock()
        response = self.service.CheckInventory(request, context)

        # 验证结果
        self.assertEqual(response.product_id, "PROD-001")
        self.assertEqual(response.name, "人参")
        self.assertEqual(response.available_quantity, 100)
        self.assertEqual(response.reserved_quantity, 50)
        self.assertEqual(response.status, xiaoke_service_pb2.InventoryStatus.AVAILABLE)

        # 验证调用
        self.product_manager_mock.check_inventory.assert_called_once_with("PROD-001")

    def test_check_inventory_not_found(self):
        """测试库存检查 - 产品不存在的情况"""
        # 模拟产品不存在的情况
        self.product_manager_mock.check_inventory.return_value = None

        # 准备请求对象
        request = xiaoke_service_pb2.InventoryCheckRequest(product_id="INVALID-ID")

        # 执行被测试方法
        context = mock.MagicMock()
        response = self.service.CheckInventory(request, context)

        # 验证结果
        self.assertEqual(response.product_id, "INVALID-ID")
        self.assertEqual(response.status, xiaoke_service_pb2.InventoryStatus.NOT_FOUND)

    def test_reserve_resources(self):
        """测试资源预约功能"""
        # 准备测试数据
        appointment_time = datetime.datetime.now() + datetime.timedelta(days=3)
        timestamp = Timestamp()
        timestamp.FromDatetime(appointment_time)

        self.resource_manager_mock.reserve_resource.return_value = {
            "reservation_id": "RES-12345",
            "resource_id": "RES-001",
            "resource_type": "DOCTOR",
            "resource_name": "张医生",
            "user_id": "USER-001",
            "start_time": appointment_time,
            "duration_minutes": 30,
            "status": "RESERVED",
        }

        # 准备请求对象
        request = xiaoke_service_pb2.ResourceReservationRequest(
            user_id="USER-001",
            resource_id="RES-001",
            resource_type=xiaoke_service_pb2.ResourceType.DOCTOR,
            appointment_time=timestamp,
            duration_minutes=30,
        )

        # 执行被测试方法
        context = mock.MagicMock()
        response = self.service.ReserveResource(request, context)

        # 验证结果
        self.assertEqual(response.reservation_id, "RES-12345")
        self.assertEqual(response.resource_id, "RES-001")
        self.assertEqual(response.resource_name, "张医生")
        self.assertEqual(response.status, xiaoke_service_pb2.ReservationStatus.RESERVED)

        # 验证调用
        self.resource_manager_mock.reserve_resource.assert_called_once_with(
            user_id="USER-001",
            resource_id="RES-001",
            resource_type="DOCTOR",
            start_time=appointment_time,
            duration_minutes=30,
        )

    def test_reserve_resources_unavailable(self):
        """测试资源预约 - 资源不可用的情况"""
        # 准备测试数据 - 模拟预约失败
        appointment_time = datetime.datetime.now() + datetime.timedelta(days=3)
        timestamp = Timestamp()
        timestamp.FromDatetime(appointment_time)

        # 模拟资源不可用的情况
        self.resource_manager_mock.reserve_resource.side_effect = Exception(
            "Resource not available"
        )

        # 准备请求对象
        request = xiaoke_service_pb2.ResourceReservationRequest(
            user_id="USER-001",
            resource_id="RES-001",
            resource_type=xiaoke_service_pb2.ResourceType.DOCTOR,
            appointment_time=timestamp,
            duration_minutes=30,
        )

        # 执行被测试方法
        context = mock.MagicMock()
        response = self.service.ReserveResource(request, context)

        # 验证结果 - 应该返回UNAVAILABLE状态
        self.assertEqual(response.resource_id, "RES-001")
        self.assertEqual(
            response.status, xiaoke_service_pb2.ReservationStatus.UNAVAILABLE
        )

    def test_create_subscription(self):
        """测试创建订阅功能"""
        # 准备测试数据
        start_date = datetime.datetime.now()
        end_date = start_date + datetime.timedelta(days=365)

        start_timestamp = Timestamp()
        start_timestamp.FromDatetime(start_date)

        end_timestamp = Timestamp()
        end_timestamp.FromDatetime(end_date)

        self.subscription_repo_mock.create_subscription.return_value = {
            "subscription_id": "SUB-12345",
            "user_id": "USER-001",
            "plan_id": "PLAN-001",
            "plan_name": "年度健康套餐",
            "start_date": start_date,
            "end_date": end_date,
            "status": "ACTIVE",
            "price": 2999.00,
            "auto_renew": True,
        }

        # 准备请求对象
        request = xiaoke_service_pb2.CreateSubscriptionRequest(
            user_id="USER-001",
            plan_id="PLAN-001",
            start_date=start_timestamp,
            end_date=end_timestamp,
            auto_renew=True,
            payment_method=xiaoke_service_pb2.PaymentMethod.WECHAT_PAY,
        )

        # 执行被测试方法
        context = mock.MagicMock()
        response = self.service.CreateSubscription(request, context)

        # 验证结果
        self.assertEqual(response.subscription_id, "SUB-12345")
        self.assertEqual(response.user_id, "USER-001")
        self.assertEqual(response.plan_id, "PLAN-001")
        self.assertEqual(response.plan_name, "年度健康套餐")
        self.assertEqual(response.status, xiaoke_service_pb2.SubscriptionStatus.ACTIVE)
        self.assertTrue(response.auto_renew)

        # 验证调用
        self.subscription_repo_mock.create_subscription.assert_called_once_with(
            user_id="USER-001",
            plan_id="PLAN-001",
            start_date=start_date,
            end_date=end_date,
            auto_renew=True,
            payment_method="WECHAT_PAY",
        )

    def test_cancel_subscription(self):
        """测试取消订阅功能"""
        # 准备测试数据
        cancel_date = datetime.datetime.now()

        self.subscription_repo_mock.cancel_subscription.return_value = {
            "subscription_id": "SUB-12345",
            "status": "CANCELLED",
            "cancel_date": cancel_date,
            "refund_amount": 1500.00,
        }

        # 准备请求对象
        request = xiaoke_service_pb2.CancelSubscriptionRequest(
            subscription_id="SUB-12345", user_id="USER-001", reason="服务不满意"
        )

        # 执行被测试方法
        context = mock.MagicMock()
        response = self.service.CancelSubscription(request, context)

        # 验证结果
        self.assertEqual(response.subscription_id, "SUB-12345")
        self.assertEqual(
            response.status, xiaoke_service_pb2.SubscriptionStatus.CANCELLED
        )
        self.assertGreater(response.refund_amount, 0)

        # 验证调用
        self.subscription_repo_mock.cancel_subscription.assert_called_once_with(
            subscription_id="SUB-12345", user_id="USER-001", reason="服务不满意"
        )


if __name__ == "__main__":
    unittest.main()
