#!/usr/bin/env python3

"""
Corn Maze Service 优化测试脚本 - 简化版本
专注于测试核心优化功能，不依赖外部数据库
"""

import asyncio
import logging
import time
import uuid

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_cache_manager():
    """测试缓存管理器"""
    logger.info("=== 测试缓存管理器 ===")

    try:
        from pkg.utils.cache import CacheManager

        # 测试内存缓存
        cache = CacheManager(use_redis=False)

        # 测试基本操作
        await cache.set("test_key", {"data": "test_value"}, ttl=60)
        result = await cache.get("test_key")
        assert result == {"data": "test_value"}, "缓存设置/获取失败"

        # 测试模式删除
        await cache.set("pattern_test_1", "value1")
        await cache.set("pattern_test_2", "value2")
        await cache.set("other_key", "value3")

        deleted_count = await cache.delete_pattern("pattern_test_*")
        assert deleted_count == 2, f"模式删除失败，期望删除2个，实际删除{deleted_count}个"

        # 测试清空缓存
        await cache.clear()
        result = await cache.get("other_key")
        assert result is None, "清空缓存后应该无法获取到数据"

        logger.info("✅ 缓存管理器测试通过")

    except Exception as e:
        logger.error(f"❌ 缓存管理器测试失败: {e!s}")
        raise

async def test_maze_generator():
    """测试迷宫生成器"""
    logger.info("=== 测试迷宫生成器 ===")

    try:
        from internal.maze.generator import MazeGenerator
        from pkg.utils.cache import CacheManager

        cache_manager = CacheManager(use_redis=False)
        generator = MazeGenerator(cache_manager)

        # 测试生成不同类型的迷宫
        maze_types = ["health_path", "nutrition_garden", "tcm_journey", "balanced_life"]

        for maze_type in maze_types:
            logger.info(f"测试生成 {maze_type} 迷宫")

            user_id = str(uuid.uuid4())
            maze = await generator.generate_maze(
                user_id=user_id,
                maze_type=maze_type,
                size_x=5,
                size_y=5,
                difficulty=2,
                health_attributes={"age": "30", "gender": "male"}
            )

            # 验证迷宫属性
            assert maze.maze_id is not None, "迷宫ID不能为空"
            assert maze.user_id == user_id, "用户ID不匹配"
            assert maze.maze_type == maze_type, "迷宫类型不匹配"
            assert maze.size_x == 5 and maze.size_y == 5, "迷宫大小不匹配"
            assert maze.difficulty == 2, "难度级别不匹配"
            assert len(maze.cells) == 5, "迷宫网格行数不正确"
            assert len(maze.cells[0]) == 5, "迷宫网格列数不正确"
            assert len(maze.knowledge_nodes) > 0, "知识节点数量应该大于0"

            logger.info(f"✅ {maze_type} 迷宫生成成功，包含 {len(maze.knowledge_nodes)} 个知识节点")

        # 测试参数验证
        try:
            await generator.generate_maze(
                user_id="",
                maze_type="invalid_type",
                size_x=2,
                size_y=2,
                difficulty=6
            )
            assert False, "应该抛出参数验证错误"
        except ValueError:
            logger.info("✅ 参数验证正常工作")

        # 测试缓存功能
        logger.info("测试模板缓存功能")
        user_id1 = str(uuid.uuid4())
        user_id2 = str(uuid.uuid4())

        # 第一次生成（创建模板）
        start_time = time.time()
        maze1 = await generator.generate_maze(
            user_id=user_id1,
            maze_type="health_path",
            size_x=6,
            size_y=6,
            difficulty=3
        )
        first_time = time.time() - start_time

        # 第二次生成（使用缓存模板）
        start_time = time.time()
        maze2 = await generator.generate_maze(
            user_id=user_id2,
            maze_type="health_path",
            size_x=6,
            size_y=6,
            difficulty=3
        )
        second_time = time.time() - start_time

        logger.info(f"首次生成耗时: {first_time:.3f}秒，缓存生成耗时: {second_time:.3f}秒")
        assert maze1.maze_id != maze2.maze_id, "不同用户的迷宫ID应该不同"
        assert maze1.user_id != maze2.user_id, "不同用户的用户ID应该不同"

        logger.info("✅ 迷宫生成器测试通过")

    except Exception as e:
        logger.error(f"❌ 迷宫生成器测试失败: {e!s}")
        raise

async def test_metrics():
    """测试监控指标"""
    logger.info("=== 测试监控指标 ===")

    try:
        from pkg.utils.metrics import (
            api_request_time,
            get_metrics_summary,
            maze_generation_time,
            record_cache_operation,
            record_maze_error,
            record_maze_operation,
            update_active_mazes_count,
            update_memory_usage,
        )

        # 测试基本指标记录
        record_maze_operation("create", "health_path", 3)
        record_maze_operation("get", "nutrition_garden", 2)
        record_maze_error("create", "validation_error")

        update_active_mazes_count("health_path", 10)
        update_active_mazes_count("nutrition_garden", 5)

        record_cache_operation("get", "memory", "hit")
        record_cache_operation("set", "memory", "success")

        update_memory_usage("maze_generator", 1024 * 1024)  # 1MB

        # 测试装饰器
        @maze_generation_time
        async def mock_generation(maze_type="test", difficulty=1):
            await asyncio.sleep(0.1)  # 模拟生成时间
            return {"maze_id": "test_maze"}

        @api_request_time("/test")
        async def mock_api_request():
            await asyncio.sleep(0.05)  # 模拟API处理时间
            return {"status": "success"}

        # 执行测试
        result1 = await mock_generation()
        result2 = await mock_api_request()

        assert result1["maze_id"] == "test_maze", "装饰器应该返回原始结果"
        assert result2["status"] == "success", "装饰器应该返回原始结果"

        # 获取指标摘要
        summary = get_metrics_summary()
        assert "timestamp" in summary, "摘要应该包含时间戳"
        assert "metrics_store" in summary, "摘要应该包含指标存储"
        assert "generation_stats" in summary, "摘要应该包含生成统计"

        # 验证指标数据
        metrics_store = summary["metrics_store"]
        assert len(metrics_store["maze_operations"]) > 0, "应该有迷宫操作记录"
        assert len(metrics_store["generation_times"]) > 0, "应该有生成时间记录"
        assert len(metrics_store["cache_operations"]) > 0, "应该有缓存操作记录"

        logger.info(f"记录的指标数量: 迷宫操作 {len(metrics_store['maze_operations'])}, "
                   f"生成时间 {len(metrics_store['generation_times'])}, "
                   f"缓存操作 {len(metrics_store['cache_operations'])}")

        logger.info("✅ 监控指标测试通过")

    except Exception as e:
        logger.error(f"❌ 监控指标测试失败: {e!s}")
        raise

async def test_performance():
    """测试性能"""
    logger.info("=== 测试性能 ===")

    try:
        from internal.maze.generator import MazeGenerator
        from pkg.utils.cache import CacheManager

        cache_manager = CacheManager(use_redis=False)
        generator = MazeGenerator(cache_manager)

        # 测试并发生成
        user_ids = [str(uuid.uuid4()) for _ in range(5)]

        logger.info("测试并发生成5个迷宫...")
        start_time = time.time()

        tasks = []
        for user_id in user_ids:
            task = generator.generate_maze(
                user_id=user_id,
                maze_type="health_path",
                size_x=8,
                size_y=8,
                difficulty=3
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        end_time = time.time()
        total_time = end_time - start_time

        assert len(results) == 5, "应该生成5个迷宫"
        assert all(maze.maze_id for maze in results), "所有迷宫都应该有ID"

        # 验证迷宫的唯一性
        maze_ids = [maze.maze_id for maze in results]
        assert len(set(maze_ids)) == 5, "所有迷宫ID应该是唯一的"

        logger.info(f"✅ 并发生成5个迷宫耗时: {total_time:.3f}秒，平均每个: {total_time/5:.3f}秒")

        # 测试缓存性能
        logger.info("测试缓存性能...")
        start_time = time.time()

        # 第二次生成相同参数的迷宫（应该使用缓存模板）
        cached_maze = await generator.generate_maze(
            user_id=str(uuid.uuid4()),
            maze_type="health_path",
            size_x=8,
            size_y=8,
            difficulty=3
        )

        cached_time = time.time() - start_time

        logger.info(f"✅ 缓存生成迷宫耗时: {cached_time:.3f}秒")

        assert cached_maze.maze_id is not None, "缓存生成的迷宫应该有ID"
        assert cached_maze.size_x == 8 and cached_maze.size_y == 8, "迷宫大小应该正确"

        # 测试内存缓存性能
        logger.info("测试内存缓存性能...")
        cache_start = time.time()

        # 设置1000个缓存项
        for i in range(1000):
            await cache_manager.set(f"perf_test_{i}", {"data": f"value_{i}"})

        # 读取1000个缓存项
        hit_count = 0
        for i in range(1000):
            result = await cache_manager.get(f"perf_test_{i}")
            if result is not None:
                hit_count += 1

        cache_time = time.time() - cache_start

        logger.info(f"✅ 缓存性能测试: 1000次读写耗时 {cache_time:.3f}秒，命中率 {hit_count/1000*100:.1f}%")

        assert hit_count >= 950, f"缓存命中率应该大于95%，实际为 {hit_count/1000*100:.1f}%"

        logger.info("✅ 性能测试通过")

    except Exception as e:
        logger.error(f"❌ 性能测试失败: {e!s}")
        raise

async def test_error_handling():
    """测试错误处理"""
    logger.info("=== 测试错误处理 ===")

    try:
        from internal.maze.generator import MazeGenerator
        from pkg.utils.cache import CacheManager
        from pkg.utils.metrics import get_metrics_summary

        cache_manager = CacheManager(use_redis=False)
        generator = MazeGenerator(cache_manager)

        # 测试各种错误情况
        error_cases = [
            {"user_id": "", "maze_type": "health_path", "size_x": 5, "size_y": 5, "difficulty": 1},
            {"user_id": "valid_user", "maze_type": "invalid_type", "size_x": 5, "size_y": 5, "difficulty": 1},
            {"user_id": "valid_user", "maze_type": "health_path", "size_x": 2, "size_y": 2, "difficulty": 1},
            {"user_id": "valid_user", "maze_type": "health_path", "size_x": 5, "size_y": 5, "difficulty": 6},
        ]

        error_count = 0
        for i, case in enumerate(error_cases):
            try:
                await generator.generate_maze(**case)
                logger.warning(f"错误案例 {i+1} 应该抛出异常但没有")
            except (ValueError, Exception) as e:
                error_count += 1
                logger.info(f"错误案例 {i+1} 正确抛出异常: {type(e).__name__}")

        assert error_count == len(error_cases), f"应该有 {len(error_cases)} 个错误，实际有 {error_count} 个"

        # 检查错误指标是否被记录
        summary = get_metrics_summary()
        error_metrics = summary["metrics_store"]["errors"]
        assert len(error_metrics) > 0, "应该记录错误指标"

        logger.info(f"✅ 错误处理测试通过，记录了 {len(error_metrics)} 种错误类型")

    except Exception as e:
        logger.error(f"❌ 错误处理测试失败: {e!s}")
        raise

async def run_all_tests():
    """运行所有测试"""
    logger.info("🚀 开始运行 Corn Maze Service 优化测试（简化版）")

    tests = [
        test_cache_manager,
        test_maze_generator,
        test_metrics,
        test_performance,
        test_error_handling
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            await test()
            passed += 1
        except Exception as e:
            logger.error(f"测试失败: {test.__name__} - {e!s}")
            failed += 1

    logger.info(f"📊 测试结果: {passed} 通过, {failed} 失败")

    if failed == 0:
        logger.info("🎉 所有测试通过！Corn Maze Service 优化成功！")

        # 显示最终的指标摘要
        from pkg.utils.metrics import get_metrics_summary
        summary = get_metrics_summary()

        logger.info("📈 最终指标摘要:")
        logger.info(f"  - 迷宫操作: {len(summary['metrics_store']['maze_operations'])} 种")
        logger.info(f"  - 生成记录: {len(summary['metrics_store']['generation_times'])} 次")
        logger.info(f"  - 缓存操作: {len(summary['metrics_store']['cache_operations'])} 种")
        logger.info(f"  - 错误记录: {len(summary['metrics_store']['errors'])} 种")

        if "generation_stats" in summary:
            stats = summary["generation_stats"]
            logger.info(f"  - 平均生成时间: {stats['avg_duration']:.3f}秒")
            logger.info(f"  - 最快生成时间: {stats['min_duration']:.3f}秒")
            logger.info(f"  - 最慢生成时间: {stats['max_duration']:.3f}秒")

        logger.info(f"  - 错误率: {summary.get('error_rate', 0)*100:.2f}%")

    else:
        logger.error("❌ 部分测试失败，需要进一步检查")

    return failed == 0

if __name__ == "__main__":
    # 模拟导入路径
    import os
    import sys

    # 添加服务根目录到Python路径
    service_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, service_root)

    # 运行测试
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
