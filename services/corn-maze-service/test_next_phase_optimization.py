#!/usr/bin/env python3

"""
下一阶段优化综合测试脚本
"""

import asyncio
import logging
import time

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_database_optimization():
    """测试数据库优化"""
    print("🗄️ 测试数据库优化...")

    try:
        from internal.model.maze import Maze
        from internal.repository.maze_repository import MazeRepository

        # 创建存储库实例
        repo = MazeRepository()

        # 测试数据库初始化
        await repo._ensure_initialized()

        # 创建测试迷宫
        test_maze = Maze(
            maze_id="test_db_opt_001",
            user_id="test_user",
            maze_type="health_path",
            size_x=8,
            size_y=8,
            difficulty=2
        )

        # 测试保存
        start_time = time.time()
        saved_maze = await repo.save_maze(test_maze)
        save_time = time.time() - start_time

        # 测试获取
        start_time = time.time()
        retrieved_maze = await repo.get_maze(test_maze.maze_id)
        get_time = time.time() - start_time

        # 测试搜索
        start_time = time.time()
        search_results, total = await repo.search_mazes("health", limit=5)
        search_time = time.time() - start_time

        # 测试统计
        start_time = time.time()
        type_counts = await repo.get_maze_types_count()
        stats_time = time.time() - start_time

        print("  ✅ 数据库操作性能:")
        print(f"     - 保存耗时: {save_time:.4f}s")
        print(f"     - 获取耗时: {get_time:.4f}s")
        print(f"     - 搜索耗时: {search_time:.4f}s")
        print(f"     - 统计耗时: {stats_time:.4f}s")

        # 清理测试数据
        await repo.delete_maze(test_maze.maze_id)

        return True

    except Exception as e:
        print(f"  ❌ 数据库优化测试失败: {e!s}")
        return False

async def test_rate_limiting():
    """测试限流功能"""
    print("🚦 测试API限流...")

    try:
        from pkg.utils.rate_limiter import (
            RateLimiter,
            SlidingWindowCounter,
            TokenBucket,
        )

        # 测试令牌桶
        bucket = TokenBucket(capacity=5, refill_rate=1.0)

        # 快速消费令牌
        consumed = 0
        for i in range(10):
            if bucket.consume():
                consumed += 1

        print(f"  ✅ 令牌桶测试: 消费了 {consumed}/10 个令牌")

        # 测试滑动窗口
        window = SlidingWindowCounter(window_size=60, max_requests=5)

        allowed = 0
        for i in range(10):
            if window.is_allowed():
                allowed += 1

        print(f"  ✅ 滑动窗口测试: 允许了 {allowed}/10 个请求")

        # 测试限流器
        rate_limiter = RateLimiter()

        # 测试用户限流
        user_allowed = 0
        for i in range(5):
            allowed, info = await rate_limiter.is_allowed("test_user", "user")
            if allowed:
                user_allowed += 1

        print(f"  ✅ 用户限流测试: 允许了 {user_allowed}/5 个请求")

        return True

    except Exception as e:
        print(f"  ❌ 限流测试失败: {e!s}")
        return False

async def test_service_communication():
    """测试服务间通信"""
    print("🌐 测试服务间通信...")

    try:
        from pkg.utils.service_client import (
            CircuitBreakerConfig,
            RetryConfig,
            ServiceClient,
            ServiceEndpoint,
            ServiceRegistry,
        )

        # 创建测试端点
        endpoints = [
            ServiceEndpoint("httpbin.org", 80, "http", 1, "/status/200"),
            ServiceEndpoint("httpbin.org", 80, "http", 1, "/status/200")
        ]

        # 创建服务客户端
        client = ServiceClient(
            service_name="test-service",
            endpoints=endpoints,
            circuit_breaker_config=CircuitBreakerConfig(timeout=10.0),
            retry_config=RetryConfig(max_attempts=2)
        )

        # 测试健康检查
        start_time = time.time()
        health_results = await client.health_check()
        health_time = time.time() - start_time

        print(f"  ✅ 健康检查耗时: {health_time:.4f}s")
        print(f"  ✅ 健康检查结果: {len(health_results)} 个端点")

        # 测试熔断器状态
        circuit_status = await client.get_circuit_breaker_status()
        print(f"  ✅ 熔断器状态: {len(circuit_status)} 个熔断器")

        # 关闭客户端
        await client.close()

        # 测试服务注册中心
        registry = ServiceRegistry()
        await registry.register_service("test-service", endpoints)

        retrieved_endpoints = await registry.get_service_endpoints("test-service")
        print(f"  ✅ 服务注册: 注册了 {len(retrieved_endpoints)} 个端点")

        return True

    except Exception as e:
        print(f"  ❌ 服务通信测试失败: {e!s}")
        return False

async def test_alerting_system():
    """测试告警系统"""
    print("🚨 测试监控告警...")

    try:
        from pkg.utils.alerting import (
            AlertManager,
            WebhookChannel,
            get_default_alert_rules,
        )

        # 创建告警管理器
        alert_manager = AlertManager()

        # 添加默认规则
        default_rules = get_default_alert_rules()
        for rule in default_rules:
            alert_manager.add_rule(rule)

        print(f"  ✅ 添加了 {len(default_rules)} 个默认告警规则")

        # 创建测试Webhook渠道
        webhook_channel = WebhookChannel("https://httpbin.org/post")
        alert_manager.add_channel("test-webhook", webhook_channel)

        # 测试渠道连接
        channel_results = await alert_manager.test_channels()
        print(f"  ✅ 渠道测试结果: {channel_results}")

        # 获取活跃告警
        active_alerts = await alert_manager.get_active_alerts()
        print(f"  ✅ 当前活跃告警: {len(active_alerts)} 个")

        return True

    except Exception as e:
        print(f"  ❌ 告警系统测试失败: {e!s}")
        return False

async def test_cache_performance():
    """测试缓存性能"""
    print("💾 测试缓存性能...")

    try:
        from pkg.utils.cache import CacheManager

        cache_manager = CacheManager()

        # 测试批量写入
        start_time = time.time()
        for i in range(100):
            await cache_manager.set(f"test_key_{i}", f"test_value_{i}", ttl=60)
        write_time = time.time() - start_time

        # 测试批量读取
        start_time = time.time()
        hit_count = 0
        for i in range(100):
            value = await cache_manager.get(f"test_key_{i}")
            if value:
                hit_count += 1
        read_time = time.time() - start_time

        # 测试缓存统计
        stats = await cache_manager.get_stats()

        print("  ✅ 缓存性能:")
        print(f"     - 写入100个键耗时: {write_time:.4f}s")
        print(f"     - 读取100个键耗时: {read_time:.4f}s")
        print(f"     - 缓存命中率: {hit_count}%")
        print(f"     - 缓存统计: {stats}")

        # 清理测试数据
        for i in range(100):
            await cache_manager.delete(f"test_key_{i}")

        return True

    except Exception as e:
        print(f"  ❌ 缓存性能测试失败: {e!s}")
        return False

async def test_metrics_collection():
    """测试指标收集"""
    print("📊 测试指标收集...")

    try:
        from pkg.utils.metrics import (
            active_mazes_gauge,
            record_maze_operation,
            response_time_histogram,
        )

        # 记录一些测试指标
        for i in range(10):
            record_maze_operation("create", "health_path", "success")
            record_maze_operation("get", "nutrition_garden", "success")

        # 记录响应时间
        response_time_histogram.observe(0.5)
        response_time_histogram.observe(1.2)
        response_time_histogram.observe(0.8)

        # 设置活跃迷宫数量
        active_mazes_gauge.set(25)

        print("  ✅ 指标记录完成:")
        print("     - 操作计数器: 已记录20个操作")
        print("     - 响应时间: 已记录3个样本")
        print("     - 活跃迷宫: 设置为25个")

        return True

    except Exception as e:
        print(f"  ❌ 指标收集测试失败: {e!s}")
        return False

async def run_comprehensive_test():
    """运行综合测试"""
    print("🚀 开始下一阶段优化综合测试\n")

    test_results = {}

    # 运行各项测试
    test_functions = [
        ("数据库优化", test_database_optimization),
        ("API限流", test_rate_limiting),
        ("服务通信", test_service_communication),
        ("监控告警", test_alerting_system),
        ("缓存性能", test_cache_performance),
        ("指标收集", test_metrics_collection),
    ]

    passed_tests = 0
    total_tests = len(test_functions)

    for test_name, test_func in test_functions:
        try:
            result = await test_func()
            test_results[test_name] = result
            if result:
                passed_tests += 1
            print()
        except Exception as e:
            print(f"  ❌ {test_name}测试异常: {e!s}\n")
            test_results[test_name] = False

    # 输出测试总结
    print("=" * 60)
    print("📋 测试总结")
    print("=" * 60)

    for test_name, result in test_results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:20} {status}")

    print(f"\n总体结果: {passed_tests}/{total_tests} 测试通过")

    if passed_tests == total_tests:
        print("🎉 所有测试通过！下一阶段优化功能正常工作。")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")

    return passed_tests == total_tests

if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())
