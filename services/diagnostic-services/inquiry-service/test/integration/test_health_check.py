"""
test_health_check - 索克生活项目模块
"""

from internal.observability.health_check import HealthChecker, HealthStatus
import asyncio
import os
import sys
import unittest

#!/usr/bin/env python

"""
健康检查集成测试
测试服务健康检查功能
"""


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))



class TestHealthCheck(unittest.TestCase):
    """健康检查集成测试"""

    def setUp(self):
        """测试前准备"""
        self.config = {
            "health_check": {
                "enabled": True,
                "interval_seconds": 1,
                "timeout_seconds": 2,
                "unhealthy_threshold": 2,
                "healthy_threshold": 2,
            }
        }
        self.health_checker = HealthChecker(self.config)

    def tearDown(self):
        """测试后清理"""
        # 使用同步方式关闭异步资源
        if hasattr(self, "loop"):
            coro = self.health_checker.stop()
            if self.loop.is_running():
                self.loop.create_task(coro)
            else:
                self.loop.run_until_complete(coro)
                self.loop.close()

    def test_init(self):
        """测试初始化"""
        self.assertTrue(self.health_checker.enabled)
        self.assertEqual(self.health_checker.interval_seconds, 1)
        self.assertEqual(self.health_checker.timeout_seconds, 2)
        self.assertEqual(self.health_checker.unhealthy_threshold, 2)
        self.assertEqual(self.health_checker.healthy_threshold, 2)
        self.assertFalse(self.health_checker.is_running)

    def test_register_check(self):
        """测试注册检查"""

        # 定义测试检查函数
        async def test_check():
            return True, None, {"value": 123}

        # 注册检查
        self.health_checker.register_check("test_check", test_check)

        # 验证是否已注册
        self.assertIn("test_check", self.health_checker.checks)
        self.assertIn("test_check", self.health_checker.components)
        self.assertEqual(
            self.health_checker.components["test_check"].status, HealthStatus.UNKNOWN
        )

    def test_unregister_check(self):
        """测试取消注册检查"""

        # 注册检查
        async def test_check():
            return True, None, {}

        self.health_checker.register_check("temp_check", test_check)
        self.assertIn("temp_check", self.health_checker.checks)

        # 取消注册
        self.health_checker.unregister_check("temp_check")
        self.assertNotIn("temp_check", self.health_checker.checks)

    def test_default_checks(self):
        """测试默认检查项"""
        # 默认应包含内存、CPU和磁盘检查
        self.assertIn("memory", self.health_checker.checks)
        self.assertIn("cpu", self.health_checker.checks)
        self.assertIn("disk", self.health_checker.checks)

    async def _async_test_check_health(self):
        """异步测试检查健康状态"""

        # 注册一个总是健康的检查
        async def healthy_check():
            return True, None, {"value": "healthy"}

        # 注册一个总是不健康的检查
        async def unhealthy_check():
            return False, "Not working", {"value": "unhealthy"}

        self.health_checker.register_check("always_healthy", healthy_check)
        self.health_checker.register_check("always_unhealthy", unhealthy_check)

        # 执行健康检查
        components = await self.health_checker.check_health()

        # 第一次检查后，健康组件应该增加一次成功计数
        self.assertEqual(components["always_healthy"].consecutive_successes, 1)
        self.assertEqual(components["always_healthy"].consecutive_failures, 0)

        # 第一次检查后，不健康组件应该增加一次失败计数
        self.assertEqual(components["always_unhealthy"].consecutive_successes, 0)
        self.assertEqual(components["always_unhealthy"].consecutive_failures, 1)

        # 再次执行，达到阈值
        await self.health_checker.check_health()

        # 健康组件应该达到健康阈值
        self.assertEqual(components["always_healthy"].consecutive_successes, 2)
        self.assertEqual(components["always_healthy"].status, HealthStatus.SERVING)

        # 不健康组件应该达到不健康阈值
        self.assertEqual(components["always_unhealthy"].consecutive_failures, 2)
        self.assertEqual(
            components["always_unhealthy"].status, HealthStatus.NOT_SERVING
        )

        # 测试整体服务状态
        service_status = self.health_checker.get_service_status()
        self.assertEqual(service_status, HealthStatus.NOT_SERVING)

    def test_check_health(self):
        """测试检查健康状态"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._async_test_check_health())

    async def _async_test_start_stop(self):
        """异步测试启动和停止"""
        # 启动健康检查
        await self.health_checker.start()
        self.assertTrue(self.health_checker.is_running)
        self.assertIsNotNone(self.health_checker.check_task)

        # 等待几次检查
        await asyncio.sleep(2.5)  # 等待足够的时间完成至少两次检查

        # 停止健康检查
        await self.health_checker.stop()
        self.assertFalse(self.health_checker.is_running)
        self.assertIsNone(self.health_checker.check_task)

    def test_start_stop(self):
        """测试启动和停止"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._async_test_start_stop())


# 如果单独运行此文件
if __name__ == "__main__":
    unittest.main()
