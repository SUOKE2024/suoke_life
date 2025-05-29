"""
索克生活平台通用组件集成测试示例
测试负载均衡、健康检查、监控和聚合等新增功能
"""

import asyncio
import json
import logging
import random
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_load_balancer():
    """测试负载均衡器功能"""
    logger.info("🔄 开始测试负载均衡器...")

    from services.common.load_balancer import (
        LoadBalancer,
        LoadBalancingStrategy,
        ServiceEndpoint,
    )
    from services.common.load_balancer.health_aware_balancer import (
        HealthAwareLoadBalancer,
    )

    # 创建负载均衡器
    load_balancer = LoadBalancer()

    # 配置
    config = {
        "default_strategy": "health_aware",
        "endpoints": {
            "test-service": {
                "endpoints": [
                    {"host": "localhost", "port": 8001, "weight": 1},
                    {"host": "localhost", "port": 8002, "weight": 2},
                    {"host": "localhost", "port": 8003, "weight": 1},
                ]
            }
        },
    }

    await load_balancer.initialize(config)

    # 测试不同的负载均衡策略
    strategies = [
        LoadBalancingStrategy.ROUND_ROBIN,
        LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN,
        LoadBalancingStrategy.LEAST_CONNECTIONS,
        LoadBalancingStrategy.RANDOM,
        LoadBalancingStrategy.IP_HASH,
    ]

    for strategy in strategies:
        logger.info(f"测试策略: {strategy.value}")

        # 模拟多次请求
        selected_endpoints = []
        for i in range(10):
            client_info = {"client_ip": f"192.168.1.{i % 10 + 1}"}
            endpoint = await load_balancer.select_endpoint(
                "test-service", strategy, client_info
            )

            if endpoint:
                selected_endpoints.append(endpoint.address)

                # 模拟请求处理
                processing_time = random.uniform(0.1, 0.5)
                await asyncio.sleep(processing_time)

                # 记录成功
                endpoint.record_success(processing_time)

                # 释放端点
                await load_balancer.release_endpoint(endpoint)

        logger.info(f"  选择的端点: {selected_endpoints}")

    # 获取统计信息
    stats = await load_balancer.get_all_stats()
    logger.info(f"负载均衡统计: {json.dumps(stats, indent=2, ensure_ascii=False)}")

    # 测试健康感知负载均衡
    logger.info("测试健康感知负载均衡...")
    health_aware_balancer = HealthAwareLoadBalancer()
    await health_aware_balancer.initialize(
        {
            "health_factor": 0.4,
            "performance_factor": 0.3,
            "connection_factor": 0.3,
            "max_response_time": 1.0,
        }
    )

    # 创建测试端点
    endpoints = [
        ServiceEndpoint("localhost", 8001, weight=1),
        ServiceEndpoint("localhost", 8002, weight=2),
        ServiceEndpoint("localhost", 8003, weight=1),
    ]

    # 模拟不同的健康状态
    endpoints[0].record_success(0.2)  # 健康
    endpoints[1].record_failure()  # 有失败
    endpoints[2].record_success(0.8)  # 响应时间较长

    # 测试端点选择
    for i in range(5):
        selected = await health_aware_balancer.select_endpoint(endpoints)
        if selected:
            logger.info(f"健康感知选择: {selected.address}")

    # 获取端点排名
    rankings = await health_aware_balancer.get_endpoint_rankings(endpoints)
    logger.info(f"端点排名: {json.dumps(rankings, indent=2, ensure_ascii=False)}")

    await load_balancer.shutdown()
    logger.info("✅ 负载均衡器测试完成")


async def test_health_checker():
    """测试健康检查器功能"""
    logger.info("🏥 开始测试健康检查器...")

    from services.common.health import HealthChecker

    # 创建健康检查器
    health_checker = HealthChecker()

    # 配置
    config = {
        "thresholds": {"cpu_percent": 80, "memory_percent": 85, "disk_percent": 90},
        "database": {"redis": {"host": "localhost", "port": 6379, "timeout": 5}},
        "services": {
            "test-service": {
                "url": "http://httpbin.org/status/200",
                "timeout": 10,
                "expected_status": 200,
            }
        },
    }

    await health_checker.initialize(config)

    # 执行健康检查
    health_result = await health_checker.health_check()
    logger.info(
        f"健康检查结果: {json.dumps(health_result, indent=2, ensure_ascii=False)}"
    )

    # 测试单个检查项
    cpu_result = await health_checker.check_health(["system_cpu"])
    logger.info(
        f"CPU检查结果: {json.dumps({k: v.to_dict() for k, v in cpu_result.items()}, indent=2, ensure_ascii=False)}"
    )

    await health_checker.shutdown()
    logger.info("✅ 健康检查器测试完成")


async def test_health_monitor():
    """测试健康监控器功能"""
    logger.info("📊 开始测试健康监控器...")

    from services.common.health import HealthMonitor

    # 创建健康监控器
    health_monitor = HealthMonitor()

    # 配置
    config = {
        "monitor_interval": 5,  # 5秒监控间隔
        "alert_cooldown": 10,  # 10秒告警冷却
        "max_history_size": 100,
        "alert_thresholds": {
            "consecutive_failures": 2,
            "failure_rate": 0.5,
            "response_time_threshold": 2.0,
        },
        "health_checker": {"thresholds": {"cpu_percent": 80, "memory_percent": 85}},
    }

    await health_monitor.initialize(config)

    # 添加告警处理器
    async def alert_handler(alert):
        logger.warning(
            f"🚨 收到告警: [{alert.level.value}] {alert.component} - {alert.message}"
        )

    health_monitor.add_alert_handler(alert_handler)

    # 开始监控
    await health_monitor.start_monitoring()

    # 运行一段时间
    logger.info("监控运行中，等待30秒...")
    await asyncio.sleep(30)

    # 获取健康摘要
    summary = await health_monitor.get_health_summary()
    logger.info(f"健康摘要: {json.dumps(summary, indent=2, ensure_ascii=False)}")

    # 获取告警列表
    alerts = await health_monitor.get_alerts(limit=10)
    logger.info(f"告警列表: {json.dumps(alerts, indent=2, ensure_ascii=False)}")

    # 获取健康指标
    metrics = await health_monitor.get_health_metrics()
    logger.info(f"健康指标: {json.dumps(metrics, indent=2, ensure_ascii=False)}")

    # 停止监控
    await health_monitor.stop_monitoring()
    await health_monitor.shutdown()
    logger.info("✅ 健康监控器测试完成")


async def test_health_aggregator():
    """测试健康聚合器功能"""
    logger.info("🔗 开始测试健康聚合器...")

    from services.common.health import AlertLevel, HealthAggregator, HealthStatus
    from services.common.health.health_monitor import HealthAlert

    # 创建健康聚合器
    aggregator = HealthAggregator()

    # 配置
    config = {
        "aggregation_rules": {
            "critical_services": ["xiaoai-service", "auth-service"],
            "dependency_weight": 0.3,
            "alert_escalation": True,
            "health_timeout": 300,
        },
        "dependencies": {
            "xiaoke-service": ["auth-service", "health-data-service"],
            "laoke-service": ["auth-service", "med-knowledge"],
            "soer-service": ["auth-service", "blockchain-service"],
        },
        "service_weights": {
            "xiaoai-service": 2.0,
            "xiaoke-service": 1.5,
            "auth-service": 2.0,
            "health-data-service": 1.0,
        },
    }

    await aggregator.initialize(config)

    # 注册服务
    services = [
        "xiaoai-service",
        "xiaoke-service",
        "laoke-service",
        "soer-service",
        "auth-service",
        "health-data-service",
        "med-knowledge",
        "blockchain-service",
    ]

    for service in services:
        await aggregator.register_service(service, {"type": "microservice"})

    # 模拟更新服务健康状态
    health_statuses = [
        ("xiaoai-service", "healthy"),
        ("xiaoke-service", "healthy"),
        ("laoke-service", "degraded"),
        ("soer-service", "healthy"),
        ("auth-service", "healthy"),
        ("health-data-service", "unhealthy"),
        ("med-knowledge", "healthy"),
        ("blockchain-service", "healthy"),
    ]

    for service_name, status in health_statuses:
        health_result = {
            "status": status,
            "timestamp": time.time(),
            "checks": {
                "system_health": {
                    "status": status,
                    "message": f"{service_name} 系统检查",
                    "details": {"service": service_name},
                    "timestamp": time.time(),
                    "duration_ms": random.uniform(50, 200),
                }
            },
        }
        await aggregator.update_service_health(service_name, health_result)

    # 添加一些告警
    critical_alert = HealthAlert(
        level=AlertLevel.CRITICAL,
        component="health-data-service",
        message="数据库连接失败",
        details={"error": "Connection timeout"},
    )
    await aggregator.add_service_alert("health-data-service", critical_alert)

    warning_alert = HealthAlert(
        level=AlertLevel.WARNING,
        component="laoke-service",
        message="响应时间过长",
        details={"response_time": 2.5},
    )
    await aggregator.add_service_alert("laoke-service", warning_alert)

    # 获取整体健康状态
    overall_health = await aggregator.get_overall_health()
    logger.info(
        f"整体健康状态: {json.dumps(overall_health, indent=2, ensure_ascii=False)}"
    )

    # 获取特定服务健康状态
    service_health = await aggregator.get_service_health("xiaoke-service")
    logger.info(
        f"小克服务健康状态: {json.dumps(service_health, indent=2, ensure_ascii=False)}"
    )

    # 获取关键问题
    critical_issues = await aggregator.get_critical_issues()
    logger.info(
        f"关键问题: {json.dumps(critical_issues, indent=2, ensure_ascii=False)}"
    )

    # 获取健康趋势
    trends = await aggregator.get_health_trends()
    logger.info(f"健康趋势: {json.dumps(trends, indent=2, ensure_ascii=False)}")

    # 获取不健康的服务
    unhealthy_services = await aggregator.get_services_by_status(HealthStatus.UNHEALTHY)
    logger.info(
        f"不健康的服务: {json.dumps(unhealthy_services, indent=2, ensure_ascii=False)}"
    )

    await aggregator.shutdown()
    logger.info("✅ 健康聚合器测试完成")


async def test_integrated_scenario():
    """测试集成场景 - 模拟真实的微服务环境"""
    logger.info("🎭 开始集成场景测试...")

    from services.common.health import HealthAggregator, HealthChecker, HealthMonitor
    from services.common.load_balancer import LoadBalancer, LoadBalancingStrategy

    # 1. 初始化所有组件
    load_balancer = LoadBalancer()
    health_checker = HealthChecker()
    health_monitor = HealthMonitor()
    health_aggregator = HealthAggregator()

    # 配置
    lb_config = {
        "default_strategy": "health_aware",
        "endpoints": {
            "xiaoai-service": {
                "endpoints": [
                    {"host": "localhost", "port": 8001, "weight": 1},
                    {"host": "localhost", "port": 8002, "weight": 1},
                ]
            },
            "xiaoke-service": {
                "endpoints": [
                    {"host": "localhost", "port": 8003, "weight": 1},
                    {"host": "localhost", "port": 8004, "weight": 1},
                ]
            },
        },
    }

    health_config = {"thresholds": {"cpu_percent": 80, "memory_percent": 85}}

    monitor_config = {"monitor_interval": 10, "health_checker": health_config}

    aggregator_config = {
        "aggregation_rules": {
            "critical_services": ["xiaoai-service", "xiaoke-service"]
        },
        "dependencies": {"xiaoke-service": ["xiaoai-service"]},
        "service_weights": {"xiaoai-service": 2.0, "xiaoke-service": 1.5},
    }

    # 初始化组件
    await load_balancer.initialize(lb_config)
    await health_checker.initialize(health_config)
    await health_monitor.initialize(monitor_config)
    await health_aggregator.initialize(aggregator_config)

    # 注册服务到聚合器
    await health_aggregator.register_service("xiaoai-service")
    await health_aggregator.register_service("xiaoke-service")

    # 2. 模拟服务请求和健康检查
    logger.info("模拟服务请求...")

    # 模拟多个客户端请求
    for i in range(20):
        # 选择服务端点
        endpoint = await load_balancer.select_endpoint(
            "xiaoai-service",
            LoadBalancingStrategy.HEALTH_AWARE
            if hasattr(LoadBalancingStrategy, "HEALTH_AWARE")
            else LoadBalancingStrategy.ROUND_ROBIN,
            {"client_ip": f"192.168.1.{i % 10 + 1}"},
        )

        if endpoint:
            # 模拟请求处理
            processing_time = random.uniform(0.1, 1.0)
            success = random.random() > 0.1  # 90% 成功率

            if success:
                endpoint.record_success(processing_time)
            else:
                endpoint.record_failure()

            await load_balancer.release_endpoint(endpoint)

            # 更新聚合器中的服务状态
            status = "healthy" if success else "degraded"
            health_result = {
                "status": status,
                "timestamp": time.time(),
                "checks": {
                    "api_health": {
                        "status": status,
                        "message": f"API请求{'成功' if success else '失败'}",
                        "duration_ms": processing_time * 1000,
                    }
                },
            }
            await health_aggregator.update_service_health(
                "xiaoai-service", health_result
            )

        await asyncio.sleep(0.1)

    # 3. 执行健康检查
    logger.info("执行系统健康检查...")
    health_result = await health_checker.health_check()

    # 更新聚合器
    await health_aggregator.update_service_health("system", health_result)

    # 4. 获取综合报告
    logger.info("生成综合报告...")

    # 负载均衡统计
    lb_stats = await load_balancer.get_all_stats()
    logger.info(f"负载均衡统计: 总服务数 {lb_stats['total_services']}")

    # 整体健康状态
    overall_health = await health_aggregator.get_overall_health()
    logger.info(f"整体健康状态: {overall_health['status']}")

    # 关键问题
    critical_issues = await health_aggregator.get_critical_issues()
    if any(critical_issues.values()):
        logger.warning("发现关键问题:")
        for issue_type, issues in critical_issues.items():
            if issues:
                logger.warning(f"  {issue_type}: {len(issues)} 个")

    # 5. 清理资源
    await load_balancer.shutdown()
    await health_checker.shutdown()
    await health_monitor.shutdown()
    await health_aggregator.shutdown()

    logger.info("✅ 集成场景测试完成")


async def main():
    """主测试函数"""
    logger.info("🚀 开始索克生活平台通用组件集成测试...")

    try:
        # 测试各个组件
        await test_load_balancer()
        await asyncio.sleep(2)

        await test_health_checker()
        await asyncio.sleep(2)

        await test_health_monitor()
        await asyncio.sleep(2)

        await test_health_aggregator()
        await asyncio.sleep(2)

        # 集成测试
        await test_integrated_scenario()

        logger.info("🎉 所有测试完成！索克生活平台通用组件功能正常")

    except Exception as e:
        logger.error(f"❌ 测试过程中发生错误: {e}")
        raise


if __name__ == "__main__":
    # 运行测试
    asyncio.run(main())
