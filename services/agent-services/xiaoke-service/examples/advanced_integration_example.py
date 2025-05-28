#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小克服务高级集成示例
展示如何使用所有新增的优化组件：消息队列、分布式锁、健康检查、动态配置等
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, Any

# 导入优化组件
from pkg.messaging.queue_manager import (
    get_queue_manager,
    QueueType,
    TaskPriority,
    async_task,
    TaskConfig,
)
from pkg.distributed.lock_manager import get_lock_manager, LockType, LockConfig
from pkg.health.health_checker import (
    get_health_check_manager,
    HealthCheckConfig,
    DatabaseHealthChecker,
    RedisHealthChecker,
    HTTPHealthChecker,
)
from pkg.config.dynamic_config import get_config_manager, ConfigFormat
from pkg.cache.cache_manager import get_cache_manager, CacheStrategy
from pkg.resilience.retry_manager import (
    get_retry_manager,
    RetryConfig,
    CircuitBreakerConfig,
)
from pkg.observability.enhanced_metrics import get_metrics_collector

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class XiaokeServiceIntegration:
    """小克服务集成示例类"""

    def __init__(self):
        """初始化集成服务"""
        self.queue_manager = None
        self.lock_manager = None
        self.health_manager = None
        self.config_manager = None
        self.cache_manager = None
        self.retry_manager = None
        self.metrics_collector = None

        # 业务数据
        self.medical_resources = {}
        self.user_sessions = {}

    async def initialize(self):
        """初始化所有组件"""
        logger.info("开始初始化小克服务集成组件...")

        try:
            # 1. 初始化配置管理器
            await self._initialize_config_manager()

            # 2. 初始化缓存管理器
            await self._initialize_cache_manager()

            # 3. 初始化重试管理器
            await self._initialize_retry_manager()

            # 4. 初始化消息队列管理器
            await self._initialize_queue_manager()

            # 5. 初始化分布式锁管理器
            await self._initialize_lock_manager()

            # 6. 初始化健康检查管理器
            await self._initialize_health_manager()

            # 7. 初始化指标收集器
            await self._initialize_metrics_collector()

            logger.info("所有组件初始化完成")

        except Exception as e:
            logger.error("组件初始化失败: %s", str(e))
            raise

    async def _initialize_config_manager(self):
        """初始化配置管理器"""
        self.config_manager = await get_config_manager("redis://localhost:6379")

        # 添加配置文件源
        self.config_manager.add_file_source(
            "config/optimized_config.yaml", ConfigFormat.YAML
        )

        # 添加配置变更回调
        self.config_manager.add_change_callback(self._on_config_change)

        logger.info("配置管理器初始化完成")

    async def _initialize_cache_manager(self):
        """初始化缓存管理器"""
        self.cache_manager = await get_cache_manager()

        # 配置缓存策略
        await self.cache_manager.configure_strategy(
            "medical_resources",
            CacheStrategy.LRU,
            ttl=1800,  # 30分钟
            max_size=1000,
        )

        await self.cache_manager.configure_strategy(
            "user_sessions",
            CacheStrategy.TTL,
            ttl=3600,  # 1小时
            max_size=5000,
        )

        logger.info("缓存管理器初始化完成")

    async def _initialize_retry_manager(self):
        """初始化重试管理器"""
        self.retry_manager = get_retry_manager()

        # 配置重试策略
        retry_config = RetryConfig(
            max_attempts=3, base_delay=1.0, max_delay=60.0, strategy="exponential"
        )

        # 配置熔断器
        circuit_config = CircuitBreakerConfig(
            failure_threshold=5, recovery_timeout=60.0, success_threshold=3
        )

        await self.retry_manager.configure_service(
            "external_api", retry_config, circuit_config
        )

        logger.info("重试管理器初始化完成")

    async def _initialize_queue_manager(self):
        """初始化消息队列管理器"""
        self.queue_manager = await get_queue_manager(QueueType.REDIS)

        # 注册任务处理器
        await self.queue_manager.register_task_handler(
            "process_medical_request", self._process_medical_request_task
        )

        await self.queue_manager.register_task_handler(
            "send_notification", self._send_notification_task
        )

        await self.queue_manager.register_task_handler(
            "update_resource_status", self._update_resource_status_task
        )

        # 启动工作进程
        await self.queue_manager.start_workers(worker_count=4)

        logger.info("消息队列管理器初始化完成")

    async def _initialize_lock_manager(self):
        """初始化分布式锁管理器"""
        self.lock_manager = await get_lock_manager("redis://localhost:6379")

        logger.info("分布式锁管理器初始化完成")

    async def _initialize_health_manager(self):
        """初始化健康检查管理器"""
        self.health_manager = get_health_check_manager()

        # 注册数据库健康检查
        self.health_manager.register_database_checker(
            "postgresql",
            "postgresql://user:pass@localhost/xiaoke_db",
            "postgresql",
            HealthCheckConfig(interval=30.0, timeout=10.0),
        )

        self.health_manager.register_database_checker(
            "mongodb",
            "mongodb://localhost:27017/xiaoke_db",
            "mongodb",
            HealthCheckConfig(interval=30.0, timeout=10.0),
        )

        # 注册Redis健康检查
        self.health_manager.register_redis_checker(
            "redis",
            "redis://localhost:6379",
            HealthCheckConfig(interval=30.0, timeout=5.0),
        )

        # 注册HTTP服务健康检查
        self.health_manager.register_http_checker(
            "auth_service",
            "http://auth-service:8000/health",
            200,
            config=HealthCheckConfig(interval=60.0, timeout=10.0),
        )

        # 添加状态变更回调
        self.health_manager.add_status_change_callback(self._on_health_status_change)

        # 启动健康检查
        await self.health_manager.start()

        logger.info("健康检查管理器初始化完成")

    async def _initialize_metrics_collector(self):
        """初始化指标收集器"""
        self.metrics_collector = get_metrics_collector()

        # 启动指标收集
        await self.metrics_collector.start_collection()

        logger.info("指标收集器初始化完成")

    async def _on_config_change(self, changes, old_config, new_config):
        """配置变更回调"""
        logger.info("检测到配置变更，变更数量: %d", len(changes))

        for change in changes:
            logger.info(
                "配置变更: %s = %s -> %s",
                change.key,
                change.old_value,
                change.new_value,
            )

            # 根据配置变更调整服务行为
            if change.key.startswith("messaging."):
                await self._reconfigure_messaging(new_config)
            elif change.key.startswith("cache."):
                await self._reconfigure_cache(new_config)

    async def _on_health_status_change(self, old_status, new_status):
        """健康状态变更回调"""
        logger.info(
            "系统健康状态变更: %s -> %s",
            old_status.value if old_status else "None",
            new_status.value,
        )

        # 根据健康状态调整服务行为
        if new_status.value == "unhealthy":
            await self._handle_unhealthy_status()
        elif (
            new_status.value == "healthy"
            and old_status
            and old_status.value == "unhealthy"
        ):
            await self._handle_recovery()

    async def _reconfigure_messaging(self, config):
        """重新配置消息队列"""
        logger.info("重新配置消息队列...")
        # 实现消息队列重配置逻辑

    async def _reconfigure_cache(self, config):
        """重新配置缓存"""
        logger.info("重新配置缓存...")
        # 实现缓存重配置逻辑

    async def _handle_unhealthy_status(self):
        """处理不健康状态"""
        logger.warning("系统进入不健康状态，启动降级模式...")
        # 实现降级逻辑

    async def _handle_recovery(self):
        """处理恢复状态"""
        logger.info("系统恢复健康，退出降级模式...")
        # 实现恢复逻辑

    # 任务处理器
    async def _process_medical_request_task(
        self, task_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """处理医疗请求任务"""
        user_id = task_data.get("user_id")
        request_type = task_data.get("request_type")

        logger.info("处理医疗请求: 用户=%s, 类型=%s", user_id, request_type)

        # 使用分布式锁确保资源调度的一致性
        lock_key = f"medical_request:{user_id}"
        lock_config = LockConfig(timeout=30.0)

        async with self.lock_manager.acquire_lock(
            lock_key, LockType.EXCLUSIVE, lock_config
        ):
            # 从缓存获取用户信息
            user_info = await self.cache_manager.get(f"user:{user_id}")

            if not user_info:
                # 从数据库加载用户信息（带重试）
                user_info = await self._load_user_info_with_retry(user_id)

                # 缓存用户信息
                await self.cache_manager.set(f"user:{user_id}", user_info, ttl=3600)

            # 处理医疗请求
            result = await self._process_medical_request(user_info, task_data)

            # 记录指标
            self.metrics_collector.record_business_metric(
                "medical_request_processed",
                1,
                {"request_type": request_type, "user_id": user_id},
            )

            return result

    async def _send_notification_task(
        self, task_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """发送通知任务"""
        user_id = task_data.get("user_id")
        message = task_data.get("message")

        logger.info("发送通知: 用户=%s", user_id)

        # 模拟发送通知
        await asyncio.sleep(1)

        return {"status": "sent", "user_id": user_id}

    async def _update_resource_status_task(
        self, task_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """更新资源状态任务"""
        resource_id = task_data.get("resource_id")
        status = task_data.get("status")

        logger.info("更新资源状态: 资源=%s, 状态=%s", resource_id, status)

        # 使用分布式锁确保状态更新的一致性
        lock_key = f"resource:{resource_id}"
        lock_config = LockConfig(timeout=10.0)

        async with self.lock_manager.acquire_lock(
            lock_key, LockType.EXCLUSIVE, lock_config
        ):
            # 更新资源状态
            await self._update_resource_status(resource_id, status)

            # 清除相关缓存
            await self.cache_manager.delete(f"resource:{resource_id}")

        return {"status": "updated", "resource_id": resource_id}

    @async_task(
        queue="high_priority",
        priority=TaskPriority.HIGH,
        config=TaskConfig(timeout=60, max_retries=3),
    )
    async def schedule_medical_resource(
        self, user_id: str, requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """调度医疗资源（装饰器方式）"""
        logger.info("调度医疗资源: 用户=%s", user_id)

        # 业务逻辑
        task_data = {
            "user_id": user_id,
            "request_type": "resource_scheduling",
            "requirements": requirements,
            "timestamp": datetime.now().isoformat(),
        }

        # 提交到消息队列处理
        task_id = await self.queue_manager.enqueue_task(
            "process_medical_request", task_data, priority=TaskPriority.HIGH
        )

        return {"task_id": task_id, "status": "queued"}

    async def _load_user_info_with_retry(self, user_id: str) -> Dict[str, Any]:
        """带重试的用户信息加载"""

        @self.retry_manager.with_retry("external_api")
        async def load_user():
            # 模拟数据库查询
            await asyncio.sleep(0.1)
            return {
                "user_id": user_id,
                "name": f"用户{user_id}",
                "constitution": "平和质",
                "health_status": "良好",
            }

        return await load_user()

    async def _process_medical_request(
        self, user_info: Dict[str, Any], request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """处理医疗请求"""
        # 模拟医疗请求处理
        await asyncio.sleep(2)

        return {
            "request_id": f"req_{datetime.now().timestamp()}",
            "user_id": user_info["user_id"],
            "status": "processed",
            "recommendations": ["建议定期体检", "注意饮食调理", "适量运动"],
        }

    async def _update_resource_status(self, resource_id: str, status: str):
        """更新资源状态"""
        # 模拟数据库更新
        await asyncio.sleep(0.1)
        self.medical_resources[resource_id] = {
            "status": status,
            "updated_at": datetime.now().isoformat(),
        }

    async def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        # 获取健康检查状态
        health_status = await self.health_manager.get_health_status()

        # 获取队列状态
        queue_stats = await self.queue_manager.get_queue_stats()

        # 获取缓存统计
        cache_stats = self.cache_manager.get_stats()

        # 获取指标统计
        metrics_stats = self.metrics_collector.get_stats()

        return {
            "timestamp": datetime.now().isoformat(),
            "health": health_status,
            "queue": queue_stats,
            "cache": cache_stats,
            "metrics": metrics_stats,
        }

    async def run_demo(self):
        """运行演示"""
        logger.info("开始运行小克服务集成演示...")

        try:
            # 1. 调度医疗资源
            result1 = await self.schedule_medical_resource(
                "user_123", {"type": "consultation", "specialty": "中医内科"}
            )
            logger.info("医疗资源调度结果: %s", result1)

            # 2. 发送通知
            await self.queue_manager.enqueue_task(
                "send_notification",
                {"user_id": "user_123", "message": "您的医疗资源调度请求已处理"},
            )

            # 3. 更新资源状态
            await self.queue_manager.enqueue_task(
                "update_resource_status",
                {"resource_id": "resource_456", "status": "available"},
            )

            # 4. 等待任务处理
            await asyncio.sleep(5)

            # 5. 获取系统状态
            system_status = await self.get_system_status()
            logger.info(
                "系统状态: %s", json.dumps(system_status, indent=2, ensure_ascii=False)
            )

            logger.info("演示完成")

        except Exception as e:
            logger.error("演示运行失败: %s", str(e))
            raise

    async def cleanup(self):
        """清理资源"""
        logger.info("开始清理资源...")

        try:
            if self.queue_manager:
                await self.queue_manager.stop()

            if self.health_manager:
                await self.health_manager.stop()

            if self.cache_manager:
                await self.cache_manager.close()

            if self.config_manager:
                await self.config_manager.close()

            if self.metrics_collector:
                await self.metrics_collector.stop_collection()

            logger.info("资源清理完成")

        except Exception as e:
            logger.error("资源清理失败: %s", str(e))


async def main():
    """主函数"""
    integration = XiaokeServiceIntegration()

    try:
        # 初始化
        await integration.initialize()

        # 运行演示
        await integration.run_demo()

        # 保持运行一段时间以观察效果
        logger.info("保持运行30秒以观察系统行为...")
        await asyncio.sleep(30)

    except KeyboardInterrupt:
        logger.info("收到中断信号，正在退出...")
    except Exception as e:
        logger.error("运行异常: %s", str(e))
    finally:
        # 清理资源
        await integration.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
