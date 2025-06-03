"""
性能模块测试
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from human_review_service.core.performance import (
    CacheManager,
    QueryOptimizer,
    PerformanceMonitor,
    ConnectionPoolOptimizer,
    performance_monitor,
    cache_result
)


class TestCacheManager:
    """缓存管理器测试类"""

    @pytest.fixture
    def cache_manager(self):
        """创建缓存管理器实例"""
        return CacheManager()

    def test_init(self, cache_manager):
        """测试初始化"""
        assert cache_manager.cache is not None
        assert cache_manager.stats is not None

    def test_set_and_get_basic(self, cache_manager):
        """测试基础设置和获取"""
        cache_manager.set("test_key", "test_value")
        result = cache_manager.get("test_key")
        assert result == "test_value"

    def test_get_nonexistent_key(self, cache_manager):
        """测试获取不存在的键"""
        result = cache_manager.get("nonexistent_key")
        assert result is None

    def test_set_with_ttl(self, cache_manager):
        """测试带TTL的设置"""
        cache_manager.set("ttl_key", "ttl_value", ttl=1)
        
        # 立即获取应该成功
        result = cache_manager.get("ttl_key")
        assert result == "ttl_value"
        
        # 等待过期后获取应该返回None
        time.sleep(1.1)
        result = cache_manager.get("ttl_key")
        assert result is None

    def test_exists(self, cache_manager):
        """测试键存在性检查"""
        assert not cache_manager.exists("test_key")
        
        cache_manager.set("test_key", "test_value")
        assert cache_manager.exists("test_key")

    def test_delete(self, cache_manager):
        """测试删除键"""
        cache_manager.set("test_key", "test_value")
        assert cache_manager.exists("test_key")
        
        cache_manager.delete("test_key")
        assert not cache_manager.exists("test_key")

    def test_clear(self, cache_manager):
        """测试清空缓存"""
        cache_manager.set("key1", "value1")
        cache_manager.set("key2", "value2")
        
        cache_manager.clear()
        
        assert not cache_manager.exists("key1")
        assert not cache_manager.exists("key2")

    def test_get_stats(self, cache_manager):
        """测试获取统计信息"""
        # 执行一些操作
        cache_manager.set("key1", "value1")
        cache_manager.get("key1")  # 命中
        cache_manager.get("nonexistent")  # 未命中
        
        stats = cache_manager.get_stats()
        
        assert "hits" in stats
        assert "misses" in stats
        assert "total_requests" in stats
        assert "hit_rate" in stats

    def test_cache_complex_data(self, cache_manager):
        """测试缓存复杂数据类型"""
        complex_data = {
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "tuple": (1, 2, 3)
        }
        
        cache_manager.set("complex_key", complex_data)
        result = cache_manager.get("complex_key")
        
        assert result == complex_data

    def test_cache_decorator(self, cache_manager):
        """测试缓存装饰器"""
        call_count = 0
        
        @cache_manager.cached(ttl=60)
        def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y
        
        # 第一次调用
        result1 = expensive_function(1, 2)
        assert result1 == 3
        assert call_count == 1
        
        # 第二次调用应该使用缓存
        result2 = expensive_function(1, 2)
        assert result2 == 3
        assert call_count == 1  # 没有增加
        
        # 不同参数应该重新计算
        result3 = expensive_function(2, 3)
        assert result3 == 5
        assert call_count == 2


class TestQueryOptimizer:
    """查询优化器测试类"""

    @pytest.fixture
    def optimizer(self):
        """创建查询优化器实例"""
        return QueryOptimizer()

    def test_init(self, optimizer):
        """测试初始化"""
        assert optimizer.query_cache is not None
        assert optimizer.execution_stats is not None

    def test_optimize_simple_query(self, optimizer):
        """测试简单查询优化"""
        query = "SELECT * FROM users WHERE id = ?"
        params = [123]
        
        optimized = optimizer.optimize_query(query, params)
        
        assert "optimized_query" in optimized
        assert "execution_plan" in optimized
        assert "estimated_cost" in optimized

    def test_optimize_complex_query(self, optimizer):
        """测试复杂查询优化"""
        query = """
        SELECT u.name, r.title, COUNT(rt.id) as review_count
        FROM users u
        JOIN reviewers r ON u.id = r.user_id
        LEFT JOIN review_tasks rt ON r.id = rt.reviewer_id
        WHERE u.status = 'active'
        GROUP BY u.id, r.id
        ORDER BY review_count DESC
        """
        
        optimized = optimizer.optimize_query(query)
        
        assert "optimized_query" in optimized
        assert "index_hints" in optimized
        assert "execution_plan" in optimized

    def test_add_index_hint(self, optimizer):
        """测试添加索引提示"""
        query = "SELECT * FROM users WHERE email = ?"
        
        result = optimizer.add_index_hint(query, "users", "idx_email")
        
        assert "USE INDEX" in result or "FORCE INDEX" in result

    def test_analyze_performance(self, optimizer):
        """测试性能分析"""
        query = "SELECT * FROM users WHERE id = ?"
        execution_time = 0.05
        
        analysis = optimizer.analyze_performance(query, execution_time)
        
        assert "performance_rating" in analysis
        assert "recommendations" in analysis
        assert "bottlenecks" in analysis

    def test_suggest_indexes(self, optimizer):
        """测试索引建议"""
        query = "SELECT * FROM users WHERE email = ? AND status = ?"
        
        suggestions = optimizer.suggest_indexes(query)
        
        assert isinstance(suggestions, list)
        if suggestions:
            assert "table" in suggestions[0]
            assert "columns" in suggestions[0]


class TestPerformanceMonitor:
    """性能监控器测试类"""

    @pytest.fixture
    def monitor(self):
        """创建性能监控器实例"""
        return PerformanceMonitor()

    def test_init(self, monitor):
        """测试初始化"""
        assert monitor.metrics is not None
        assert monitor.alerts is not None

    def test_record_metric(self, monitor):
        """测试记录指标"""
        monitor.record_metric("response_time", 0.5, {"endpoint": "/api/reviews"})
        
        metrics = monitor.get_metrics("response_time")
        assert len(metrics) == 1
        assert metrics[0]["value"] == 0.5

    def test_get_metrics_by_name(self, monitor):
        """测试按名称获取指标"""
        monitor.record_metric("cpu_usage", 75.0)
        monitor.record_metric("memory_usage", 60.0)
        
        cpu_metrics = monitor.get_metrics("cpu_usage")
        memory_metrics = monitor.get_metrics("memory_usage")
        
        assert len(cpu_metrics) == 1
        assert len(memory_metrics) == 1
        assert cpu_metrics[0]["value"] == 75.0
        assert memory_metrics[0]["value"] == 60.0

    def test_get_metrics_by_time_range(self, monitor):
        """测试按时间范围获取指标"""
        now = datetime.now()
        
        # 记录一些指标
        monitor.record_metric("test_metric", 1.0)
        time.sleep(0.1)
        monitor.record_metric("test_metric", 2.0)
        
        # 获取最近1秒的指标
        start_time = now - timedelta(seconds=1)
        end_time = now + timedelta(seconds=1)
        
        metrics = monitor.get_metrics_by_time_range("test_metric", start_time, end_time)
        assert len(metrics) == 2

    def test_calculate_statistics(self, monitor):
        """测试统计计算"""
        # 记录多个指标值
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        for value in values:
            monitor.record_metric("test_stat", value)
        
        stats = monitor.calculate_statistics("test_stat")
        
        assert "average" in stats
        assert "min" in stats
        assert "max" in stats
        assert "count" in stats
        assert stats["average"] == 3.0
        assert stats["min"] == 1.0
        assert stats["max"] == 5.0

    def test_performance_decorator(self, monitor):
        """测试性能装饰器"""
        @monitor.measure_performance("test_function")
        def test_function():
            time.sleep(0.1)
            return "result"
        
        result = test_function()
        
        assert result == "result"
        metrics = monitor.get_metrics("test_function_duration")
        assert len(metrics) == 1
        assert metrics[0]["value"] >= 0.1

    def test_alert_threshold(self, monitor):
        """测试告警阈值"""
        # 设置告警阈值
        monitor.set_alert_threshold("response_time", 1.0)
        
        # 记录正常值
        monitor.record_metric("response_time", 0.5)
        alerts = monitor.get_active_alerts()
        assert len(alerts) == 0
        
        # 记录超过阈值的值
        monitor.record_metric("response_time", 1.5)
        alerts = monitor.get_active_alerts()
        assert len(alerts) == 1


class TestConnectionPoolOptimizer:
    """连接池优化器测试类"""

    @pytest.fixture
    def optimizer(self):
        """创建连接池优化器实例"""
        return ConnectionPoolOptimizer()

    def test_init(self, optimizer):
        """测试初始化"""
        assert optimizer.connection_stats is not None
        assert optimizer.pool_configs is not None

    def test_calculate_optimal_pool_size(self, optimizer):
        """测试计算最优连接池大小"""
        # 模拟连接使用统计
        stats = {
            "peak_connections": 15,
            "average_connections": 8,
            "connection_wait_time": 0.05,
            "query_rate": 100
        }
        
        optimal_size = optimizer.calculate_optimal_pool_size(stats)
        
        assert isinstance(optimal_size, int)
        assert optimal_size > 0

    def test_analyze_connection_patterns(self, optimizer):
        """测试分析连接模式"""
        # 模拟连接事件
        events = [
            {"timestamp": datetime.now(), "event": "connection_created"},
            {"timestamp": datetime.now(), "event": "connection_used"},
            {"timestamp": datetime.now(), "event": "connection_released"},
        ]
        
        patterns = optimizer.analyze_connection_patterns(events)
        
        assert "peak_hours" in patterns
        assert "usage_patterns" in patterns
        assert "connection_lifecycle" in patterns

    def test_optimize_pool_configuration(self, optimizer):
        """测试优化连接池配置"""
        current_config = {
            "min_connections": 5,
            "max_connections": 20,
            "connection_timeout": 30
        }
        
        performance_data = {
            "average_response_time": 0.1,
            "connection_wait_time": 0.02,
            "pool_utilization": 0.8
        }
        
        optimized_config = optimizer.optimize_pool_configuration(
            current_config, performance_data
        )
        
        assert "min_connections" in optimized_config
        assert "max_connections" in optimized_config
        assert "connection_timeout" in optimized_config

    def test_detect_connection_leaks(self, optimizer):
        """测试检测连接泄漏"""
        # 模拟连接泄漏场景
        connections = [
            {"id": "conn_1", "created_at": datetime.now() - timedelta(hours=2), "in_use": True},
            {"id": "conn_2", "created_at": datetime.now() - timedelta(minutes=5), "in_use": False},
            {"id": "conn_3", "created_at": datetime.now() - timedelta(hours=1), "in_use": True},
        ]
        
        leaks = optimizer.detect_connection_leaks(connections)
        
        assert isinstance(leaks, list)
        # 应该检测到长时间使用的连接


class TestPerformanceIntegration:
    """性能模块集成测试类"""

    @pytest.fixture
    def cache_manager(self):
        """创建缓存管理器实例"""
        return CacheManager()

    @pytest.fixture
    def query_optimizer(self, cache_manager):
        """创建查询优化器实例"""
        return QueryOptimizer(cache_manager)

    @pytest.fixture
    def performance_monitor(self):
        """创建性能监控器实例"""
        return PerformanceMonitor()

    @pytest.fixture
    def connection_optimizer(self):
        """创建连接池优化器实例"""
        return ConnectionPoolOptimizer()

    def test_cache_and_monitor_integration(self, cache_manager, performance_monitor):
        """测试缓存和监控集成"""
        # 测试缓存管理器
        cache_manager.set("test_key", "test_value")
        result = cache_manager.get("test_key")
        assert result == "test_value"
        
        # 测试性能监控器
        performance_monitor.record_query_time("test_query", 0.5)
        stats = performance_monitor.get_query_stats("test_query")
        assert stats["count"] == 1
        assert stats["total_time"] == 0.5

    def test_query_optimizer_integration(self, query_optimizer):
        """测试查询优化器集成"""
        # 测试查询优化
        original_query = "SELECT * FROM tasks WHERE status = 'pending'"
        optimized = query_optimizer.optimize_query(original_query)
        
        assert optimized is not None
        assert isinstance(optimized, str)

    def test_connection_pool_optimization(self, connection_optimizer):
        """测试连接池优化"""
        # 测试连接池优化
        current_load = 0.8
        optimization = connection_optimizer.optimize_pool_size(current_load)
        
        assert "min_connections" in optimization
        assert "max_connections" in optimization

    def test_performance_monitoring_workflow(self, performance_monitor):
        """测试性能监控工作流"""
        # 记录多个查询时间
        query_times = [0.1, 0.2, 0.15, 0.3, 0.25]
        for time_val in query_times:
            performance_monitor.record_query_time("api_query", time_val)
        
        # 获取统计信息
        stats = performance_monitor.get_query_stats("api_query")
        assert stats["count"] == 5
        assert stats["average_time"] == sum(query_times) / len(query_times)

    def test_cache_performance_monitoring(self, cache_manager, performance_monitor):
        """测试缓存性能监控"""
        # 模拟缓存操作
        cache_manager.set("perf_test", {"data": "test"})
        
        # 记录缓存性能
        performance_monitor.record_query_time("cache_get", 0.001)
        performance_monitor.record_query_time("cache_set", 0.002)
        
        # 验证记录
        get_stats = performance_monitor.get_query_stats("cache_get")
        set_stats = performance_monitor.get_query_stats("cache_set")
        
        assert get_stats["count"] == 1
        assert set_stats["count"] == 1 