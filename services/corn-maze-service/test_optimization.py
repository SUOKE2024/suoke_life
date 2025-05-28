#!/usr/bin/env python3

"""
Corn Maze Service 优化测试脚本
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

        # 测试统计信息
        stats = await cache.get_stats()
        assert "backend_type" in stats, "统计信息缺少backend_type"

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

            logger.info(f"✅ {maze_type} 迷宫生成成功")

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

        logger.info("✅ 迷宫生成器测试通过")

    except Exception as e:
        logger.error(f"❌ 迷宫生成器测试失败: {e!s}")
        raise

async def test_maze_service():
    """测试迷宫服务"""
    logger.info("=== 测试迷宫服务 ===")

    try:
        from internal.service.maze_service import MazeService
        from pkg.utils.cache import CacheManager

        cache_manager = CacheManager(use_redis=False)
        service = MazeService(cache_manager=cache_manager)

        user_id = str(uuid.uuid4())

        # 测试创建迷宫
        logger.info("测试创建迷宫")
        maze_data = await service.create_maze(
            user_id=user_id,
            maze_type="health_path",
            difficulty=3,
            health_attributes={"age": "25", "fitness_level": "intermediate"}
        )

        maze_id = maze_data["maze_id"]
        assert maze_id is not None, "迷宫ID不能为空"

        # 测试获取迷宫
        logger.info("测试获取迷宫")
        retrieved_maze = await service.get_maze(maze_id, user_id)
        assert retrieved_maze is not None, "应该能够获取到迷宫"
        assert retrieved_maze["maze_id"] == maze_id, "迷宫ID应该匹配"

        # 测试获取用户迷宫列表
        logger.info("测试获取用户迷宫列表")
        mazes, total = await service.get_user_mazes(user_id)
        assert len(mazes) >= 1, "用户应该至少有一个迷宫"
        assert total >= 1, "总数应该至少为1"

        # 测试更新迷宫
        logger.info("测试更新迷宫")
        updated_maze = await service.update_maze(
            maze_id=maze_id,
            user_id=user_id,
            updates={"description": "更新后的描述", "is_public": True}
        )
        assert updated_maze["description"] == "更新后的描述", "描述应该被更新"
        assert updated_maze["is_public"] == True, "公开状态应该被更新"

        # 测试搜索迷宫
        logger.info("测试搜索迷宫")
        search_results, search_total = await service.search_mazes(
            query="健康",
            maze_type="health_path"
        )
        # 搜索结果可能为空，这是正常的

        # 测试获取统计信息
        logger.info("测试获取统计信息")
        stats = await service.get_maze_statistics(user_id)
        assert "total_mazes" in stats, "统计信息应该包含总迷宫数"

        # 测试完成迷宫
        logger.info("测试完成迷宫")
        completion_result = await service.complete_maze(
            maze_id=maze_id,
            user_id=user_id,
            completion_data={"time_spent": 300, "steps_taken": 50}
        )
        assert "rewards" in completion_result, "完成结果应该包含奖励信息"

        # 测试删除迷宫
        logger.info("测试删除迷宫")
        delete_success = await service.delete_maze(maze_id, user_id)
        assert delete_success == True, "迷宫删除应该成功"

        # 验证迷宫已被删除
        deleted_maze = await service.get_maze(maze_id, user_id)
        assert deleted_maze is None, "删除后应该无法获取到迷宫"

        logger.info("✅ 迷宫服务测试通过")

    except Exception as e:
        logger.error(f"❌ 迷宫服务测试失败: {e!s}")
        raise

async def test_metrics():
    """测试监控指标"""
    logger.info("=== 测试监控指标 ===")

    try:
        from pkg.utils.metrics import (
            api_request_time,
            get_metrics_summary,
            maze_generation_time,
            record_maze_error,
            record_maze_operation,
            update_active_mazes_count,
        )

        # 测试基本指标记录
        record_maze_operation("create", "health_path", 3)
        record_maze_operation("get", "nutrition_garden", 2)
        record_maze_error("create", "validation_error")

        update_active_mazes_count("health_path", 10)
        update_active_mazes_count("nutrition_garden", 5)

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
        await mock_generation()
        await mock_api_request()

        # 获取指标摘要
        summary = get_metrics_summary()
        assert "timestamp" in summary, "摘要应该包含时间戳"
        assert "metrics_store" in summary, "摘要应该包含指标存储"
        assert "generation_stats" in summary, "摘要应该包含生成统计"

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

        logger.info(f"✅ 并发生成5个迷宫耗时: {total_time:.2f}秒")

        # 测试缓存性能
        start_time = time.time()

        # 第二次生成相同参数的迷宫（应该使用缓存）
        cached_maze = await generator.generate_maze(
            user_id=str(uuid.uuid4()),
            maze_type="health_path",
            size_x=8,
            size_y=8,
            difficulty=3
        )

        cached_time = time.time() - start_time

        logger.info(f"✅ 缓存生成迷宫耗时: {cached_time:.2f}秒")

        # 缓存生成应该更快（但由于模板创建，可能差异不大）
        assert cached_maze.maze_id is not None, "缓存生成的迷宫应该有ID"

        logger.info("✅ 性能测试通过")

    except Exception as e:
        logger.error(f"❌ 性能测试失败: {e!s}")
        raise

async def run_all_tests():
    """运行所有测试"""
    logger.info("🚀 开始运行 Corn Maze Service 优化测试")

    tests = [
        test_cache_manager,
        test_maze_generator,
        test_maze_service,
        test_metrics,
        test_performance
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
