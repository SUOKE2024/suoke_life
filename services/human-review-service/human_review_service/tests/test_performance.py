"""
性能模块测试
Performance Module Tests

测试性能优化相关功能
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from human_review_service.core.performance import (
    CacheManager,
    QueryOptimizer,
    PerformanceMonitor,
    ConnectionPoolOptimizer,
    cache_result,
    monitor_performance,
)


class TestCacheManager:
    """缓存管理器测试"""

    @pytest.mark.asyncio
    async def test_cache_manager_init(self):
        """测试缓存管理器初始化"""
        cache_manager = CacheManager()
        assert cache_manager is not None
        assert hasattr(cache_manager, 'get')
        assert hasattr(cache_manager, 'set')
        assert hasattr(cache_manager, 'delete')

    @pytest.mark.asyncio
    async def test_memory_cache_operations(self):
        """测试内存缓存操作"""
        cache_manager = CacheManager(cache_type="memory")
        
        # 测试设置和获取
        await cache_manager.set("test_key", "test_value", ttl=60)
        value = await cache_manager.get("test_key")
        assert value == "test_value"
        
        # 测试删除
        await cache_manager.delete("test_key")
        value = await cache_manager.get("test_key")
        assert value is None

    @pytest.mark.asyncio
    async def test_cache_expiration(self):
        """测试缓存过期"""
        cache_manager = CacheManager(cache_type="memory")
        
        # 设置短期缓存
        await cache_manager.set("expire_key", "expire_value", ttl=1)
        
        # 立即获取应该成功
        value = await cache_manager.get("expire_key")
        assert value == "expire_value"
        
        # 等待过期
        await asyncio.sleep(1.1)
        value = await cache_manager.get("expire_key")
        assert value is None

    @pytest.mark.asyncio
    async def test_cache_exists(self):
        """测试缓存存在性检查"""
        cache_manager = CacheManager(cache_type="memory")
        
        # 不存在的键
        exists = await cache_manager.exists("nonexistent_key")
        assert exists is False
        
        # 存在的键
        await cache_manager.set("existing_key", "value")
        exists = await cache_manager.exists("existing_key")
        assert exists is True

    @pytest.mark.asyncio
    async def test_cache_clear(self):
        """测试清空缓存"""
        cache_manager = CacheManager(cache_type="memory")
        
        # 设置多个键
        await cache_manager.set("key1", "value1")
        await cache_manager.set("key2", "value2")
        
        # 清空缓存
        await cache_manager.clear()
        
        # 验证所有键都被删除
        assert await cache_manager.get("key1") is None
        assert await cache_manager.get("key2") is None

    @pytest.mark.asyncio
    async def test_cache_stats(self):
        """测试缓存统计"""
        cache_manager = CacheManager(cache_type="memory")
        
        # 执行一些操作
        await cache_manager.set("key1", "value1")
        await cache_manager.get("key1")  # 命中
        await cache_manager.get("nonexistent")  # 未命中
        
        stats = await cache_manager.get_stats()
        assert "hits" in stats
        assert "misses" in stats
        assert "total_keys" in stats

    @pytest.mark.asyncio
    async def test_cache_with_complex_data(self):
        """测试复杂数据类型的缓存"""
        cache_manager = CacheManager(cache_type="memory")
        
        # 测试字典
        complex_data = {
            "user_id": "123",
            "tasks": [1, 2, 3],
            "metadata": {"created": "2024-01-01"}
        }
        
        await cache_manager.set("complex_key", complex_data)
        retrieved_data = await cache_manager.get("complex_key")
        assert retrieved_data == complex_data

    @pytest.mark.asyncio
    async def test_cache_decorator(self):
        """测试缓存装饰器"""
        cache_manager = CacheManager(cache_type="memory")
        call_count = 0
        
        @cache_result(cache_manager, ttl=60)
        async def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.1)  # 模拟耗时操作
            return x + y
        
        # 第一次调用
        result1 = await expensive_function(1, 2)
        assert result1 == 3
        assert call_count == 1
        
        # 第二次调用应该使用缓存
        result2 = await expensive_function(1, 2)
        assert result2 == 3
        assert call_count == 1  # 没有增加


class TestQueryOptimizer:
    """查询优化器测试"""

    def test_query_optimizer_init(self):
        """测试查询优化器初始化"""
        optimizer = QueryOptimizer()
        assert optimizer is not None
        assert hasattr(optimizer, 'optimize_query')

    def test_optimize_simple_query(self):
        """测试简单查询优化"""
        optimizer = QueryOptimizer()
        
        original_query = "SELECT * FROM review_tasks WHERE status = 'pending'"
        optimized = optimizer.optimize_query(original_query)
        
        # 应该添加索引提示或其他优化
        assert optimized is not None
        assert isinstance(optimized, str)

    def test_optimize_complex_query(self):
        """测试复杂查询优化"""
        optimizer = QueryOptimizer()
        
        complex_query = """
        SELECT rt.*, r.name, r.email 
        FROM review_tasks rt 
        JOIN reviewers r ON rt.assigned_reviewer_id = r.reviewer_id 
        WHERE rt.status = 'in_progress' 
        AND rt.created_at > '2024-01-01'
        ORDER BY rt.priority DESC, rt.created_at ASC
        """
        
        optimized = optimizer.optimize_query(complex_query)
        assert optimized is not None
        assert len(optimized) > 0

    def test_add_index_hints(self):
        """测试添加索引提示"""
        optimizer = QueryOptimizer()
        
        query = "SELECT * FROM review_tasks WHERE status = 'pending'"
        optimized = optimizer.add_index_hints(query, ["idx_status"])
        
        assert "idx_status" in optimized or "USE INDEX" in optimized

    def test_analyze_query_performance(self):
        """测试查询性能分析"""
        optimizer = QueryOptimizer()
        
        query = "SELECT * FROM review_tasks WHERE status = 'pending'"
        analysis = optimizer.analyze_query_performance(query)
        
        assert "estimated_cost" in analysis
        assert "suggestions" in analysis
        assert isinstance(analysis["suggestions"], list)

    def test_suggest_indexes(self):
        """测试索引建议"""
        optimizer = QueryOptimizer()
        
        query = "SELECT * FROM review_tasks WHERE status = 'pending' AND priority = 'high'"
        suggestions = optimizer.suggest_indexes(query)
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0


class TestPerformanceMonitor:
    """性能监控器测试"""

    def test_performance_monitor_init(self):
        """测试性能监控器初始化"""
        monitor = PerformanceMonitor()
        assert monitor is not None
        assert hasattr(monitor, 'start_monitoring')
        assert hasattr(monitor, 'record_metric')

    @pytest.mark.asyncio
    async def test_record_metric(self):
        """测试记录性能指标"""
        monitor = PerformanceMonitor()
        
        await monitor.record_metric("response_time", 0.5, {"endpoint": "/api/tasks"})
        await monitor.record_metric("memory_usage", 1024, {"process": "main"})
        
        metrics = await monitor.get_metrics()
        assert len(metrics) >= 2

    @pytest.mark.asyncio
    async def test_get_metrics_by_name(self):
        """测试按名称获取指标"""
        monitor = PerformanceMonitor()
        
        await monitor.record_metric("cpu_usage", 75.5)
        await monitor.record_metric("memory_usage", 1024)
        
        cpu_metrics = await monitor.get_metrics_by_name("cpu_usage")
        assert len(cpu_metrics) >= 1
        assert cpu_metrics[0]["name"] == "cpu_usage"

    @pytest.mark.asyncio
    async def test_get_metrics_in_time_range(self):
        """测试获取时间范围内的指标"""
        monitor = PerformanceMonitor()
        
        start_time = datetime.now()
        await monitor.record_metric("test_metric", 100)
        end_time = datetime.now()
        
        metrics = await monitor.get_metrics_in_range(start_time, end_time)
        assert len(metrics) >= 1

    @pytest.mark.asyncio
    async def test_calculate_statistics(self):
        """测试计算统计信息"""
        monitor = PerformanceMonitor()
        
        # 记录多个相同类型的指标
        for i in range(10):
            await monitor.record_metric("response_time", i * 0.1)
        
        stats = await monitor.calculate_statistics("response_time")
        assert "average" in stats
        assert "min" in stats
        assert "max" in stats
        assert "count" in stats

    @pytest.mark.asyncio
    async def test_performance_decorator(self):
        """测试性能监控装饰器"""
        monitor = PerformanceMonitor()
        
        @monitor_performance(monitor, "test_function")
        async def test_function():
            await asyncio.sleep(0.1)
            return "result"
        
        result = await test_function()
        assert result == "result"
        
        # 检查是否记录了性能指标
        metrics = await monitor.get_metrics_by_name("test_function_duration")
        assert len(metrics) >= 1

    @pytest.mark.asyncio
    async def test_alert_thresholds(self):
        """测试性能告警阈值"""
        monitor = PerformanceMonitor()
        
        # 设置告警阈值
        monitor.set_alert_threshold("response_time", 1.0)
        
        # 记录超过阈值的指标
        alerts = []
        
        def alert_handler(metric_name, value, threshold):
            alerts.append((metric_name, value, threshold))
        
        monitor.set_alert_handler(alert_handler)
        
        await monitor.record_metric("response_time", 1.5)  # 超过阈值
        
        # 检查是否触发告警
        assert len(alerts) >= 1


class TestConnectionPoolOptimizer:
    """连接池优化器测试"""

    def test_connection_pool_optimizer_init(self):
        """测试连接池优化器初始化"""
        optimizer = ConnectionPoolOptimizer()
        assert optimizer is not None
        assert hasattr(optimizer, 'optimize_pool_size')

    def test_calculate_optimal_pool_size(self):
        """测试计算最优连接池大小"""
        optimizer = ConnectionPoolOptimizer()
        
        # 模拟性能指标
        metrics = {
            "concurrent_connections": 50,
            "average_response_time": 0.2,
            "connection_wait_time": 0.05,
            "cpu_usage": 70
        }
        
        optimal_size = optimizer.calculate_optimal_pool_size(metrics)
        assert isinstance(optimal_size, int)
        assert optimal_size > 0

    def test_analyze_connection_patterns(self):
        """测试分析连接模式"""
        optimizer = ConnectionPoolOptimizer()
        
        # 模拟连接历史数据
        connection_history = [
            {"timestamp": datetime.now() - timedelta(minutes=i), "active_connections": 10 + i}
            for i in range(60)
        ]
        
        analysis = optimizer.analyze_connection_patterns(connection_history)
        assert "peak_usage" in analysis
        assert "average_usage" in analysis
        assert "recommended_pool_size" in analysis

    def test_optimize_pool_configuration(self):
        """测试优化连接池配置"""
        optimizer = ConnectionPoolOptimizer()
        
        current_config = {
            "min_size": 5,
            "max_size": 20,
            "timeout": 30
        }
        
        performance_data = {
            "average_response_time": 0.3,
            "connection_errors": 5,
            "peak_connections": 18
        }
        
        optimized_config = optimizer.optimize_pool_configuration(
            current_config, performance_data
        )
        
        assert "min_size" in optimized_config
        assert "max_size" in optimized_config
        assert "timeout" in optimized_config

    def test_detect_connection_leaks(self):
        """测试检测连接泄漏"""
        optimizer = ConnectionPoolOptimizer()
        
        # 模拟连接使用数据
        connection_data = [
            {"connection_id": f"conn_{i}", "created_at": datetime.now() - timedelta(hours=i), "status": "active"}
            for i in range(10)
        ]
        
        leaks = optimizer.detect_connection_leaks(connection_data, max_age_hours=2)
        assert isinstance(leaks, list)


class TestIntegratedPerformance:
    """集成性能测试"""

    @pytest.mark.asyncio
    async def test_cache_and_monitor_integration(self):
        """测试缓存和监控的集成"""
        cache_manager = CacheManager(cache_type="memory")
        monitor = PerformanceMonitor()
        
        @cache_result(cache_manager, ttl=60)
        @monitor_performance(monitor, "cached_function")
        async def cached_function(x):
            await asyncio.sleep(0.1)
            return x * 2
        
        # 第一次调用（未缓存）
        result1 = await cached_function(5)
        assert result1 == 10
        
        # 第二次调用（使用缓存）
        result2 = await cached_function(5)
        assert result2 == 10
        
        # 检查性能指标
        metrics = await monitor.get_metrics_by_name("cached_function_duration")
        assert len(metrics) >= 2

    @pytest.mark.asyncio
    async def test_performance_optimization_workflow(self):
        """测试性能优化工作流"""
        cache_manager = CacheManager(cache_type="memory")
        monitor = PerformanceMonitor()
        query_optimizer = QueryOptimizer()
        
        # 模拟数据库查询函数
        @cache_result(cache_manager, ttl=300)
        @monitor_performance(monitor, "database_query")
        async def execute_query(query):
            # 优化查询
            optimized_query = query_optimizer.optimize_query(query)
            
            # 模拟查询执行
            await asyncio.sleep(0.2)
            return f"Result for: {optimized_query}"
        
        # 执行查询
        query = "SELECT * FROM review_tasks WHERE status = 'pending'"
        result = await execute_query(query)
        
        assert result is not None
        assert "Result for:" in result
        
        # 检查缓存
        cached_result = await execute_query(query)
        assert cached_result == result
        
        # 检查性能指标
        metrics = await monitor.get_metrics_by_name("database_query_duration")
        assert len(metrics) >= 1

    @pytest.mark.asyncio
    async def test_concurrent_performance_operations(self):
        """测试并发性能操作"""
        cache_manager = CacheManager(cache_type="memory")
        monitor = PerformanceMonitor()
        
        async def concurrent_operation(operation_id):
            # 缓存操作
            await cache_manager.set(f"key_{operation_id}", f"value_{operation_id}")
            
            # 性能监控
            await monitor.record_metric("concurrent_operation", operation_id)
            
            # 模拟工作负载
            await asyncio.sleep(0.05)
            
            return operation_id
        
        # 并发执行多个操作
        tasks = [concurrent_operation(i) for i in range(10)]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 10
        
        # 检查缓存
        for i in range(10):
            value = await cache_manager.get(f"key_{i}")
            assert value == f"value_{i}"
        
        # 检查性能指标
        metrics = await monitor.get_metrics_by_name("concurrent_operation")
        assert len(metrics) >= 10

    @pytest.mark.asyncio
    async def test_performance_degradation_detection(self):
        """测试性能降级检测"""
        monitor = PerformanceMonitor()
        
        # 设置性能基线
        baseline_response_time = 0.1
        
        # 记录正常性能指标
        for _ in range(5):
            await monitor.record_metric("api_response_time", baseline_response_time)
        
        # 记录性能降级指标
        degraded_response_time = 0.5
        for _ in range(3):
            await monitor.record_metric("api_response_time", degraded_response_time)
        
        # 分析性能趋势
        stats = await monitor.calculate_statistics("api_response_time")
        
        # 检测性能降级
        performance_degraded = stats["average"] > baseline_response_time * 2
        assert performance_degraded is True

    @pytest.mark.asyncio
    async def test_memory_usage_monitoring(self):
        """测试内存使用监控"""
        monitor = PerformanceMonitor()
        cache_manager = CacheManager(cache_type="memory")
        
        # 监控内存使用
        import psutil
        process = psutil.Process()
        
        initial_memory = process.memory_info().rss
        await monitor.record_metric("memory_usage", initial_memory)
        
        # 执行一些缓存操作
        for i in range(1000):
            await cache_manager.set(f"memory_test_{i}", f"data_{i}" * 100)
        
        current_memory = process.memory_info().rss
        await monitor.record_metric("memory_usage", current_memory)
        
        # 检查内存增长
        memory_metrics = await monitor.get_metrics_by_name("memory_usage")
        assert len(memory_metrics) >= 2
        
        memory_growth = memory_metrics[-1]["value"] - memory_metrics[0]["value"]
        assert memory_growth >= 0  # 内存应该增长或保持不变 