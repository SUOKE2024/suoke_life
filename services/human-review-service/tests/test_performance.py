"""
test_performance - 索克生活项目模块
"""

from datetime import datetime, timedelta
from human_review_service.core.performance import (
from unittest.mock import Mock, patch, AsyncMock
import asyncio
import pytest
import time

"""
性能模块测试
"""


    CacheManager,
    QueryOptimizer,
    PerformanceMonitor,
    ConnectionPoolOptimizer
)


class TestCacheManager:
    """缓存管理器测试类"""

    @pytest.fixture
    def cache_manager(self):
        """创建缓存管理器实例"""
        return CacheManager()

    def test_init(self, cache_manager):
        """测试初始化"""
        assert cache_manager.redis_client is None  # 没有提供Redis客户端
        assert cache_manager.default_ttl == 3600
        assert cache_manager.key_prefix == "human_review_service:"

    @pytest.mark.asyncio
    async def test_set_and_get_basic_no_redis(self, cache_manager):
        """测试没有Redis时的基础设置和获取"""
        # 没有Redis客户端时，操作应该返回默认值
        result = await cache_manager.set("test_key", "test_value")
        assert result is False
        
        result = await cache_manager.get("test_key")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_nonexistent_key(self, cache_manager):
        """测试获取不存在的键"""
        result = await cache_manager.get("nonexistent_key")
        assert result is None

    @pytest.mark.asyncio
    async def test_exists_no_redis(self, cache_manager):
        """测试键存在性检查（无Redis）"""
        result = await cache_manager.exists("test_key")
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_no_redis(self, cache_manager):
        """测试删除键（无Redis）"""
        result = await cache_manager.delete("test_key")
        assert result is False

    @pytest.mark.asyncio
    async def test_clear_pattern_no_redis(self, cache_manager):
        """测试清除模式匹配的缓存（无Redis）"""
        result = await cache_manager.clear_pattern("test_*")
        assert result == 0

    @pytest.mark.asyncio
    async def test_get_ttl_no_redis(self, cache_manager):
        """测试获取TTL（无Redis）"""
        result = await cache_manager.get_ttl("test_key")
        assert result == -1

    def test_make_key(self, cache_manager):
        """测试缓存键生成"""
        key = cache_manager._make_key("test_key")
        assert key == "human_review_service:test_key"

    @pytest.mark.asyncio
    async def test_with_mock_redis(self):
        """测试带有模拟Redis客户端的缓存管理器"""
        mock_redis = AsyncMock()
        mock_redis.get.return_value = '{"test": "value"}'
        mock_redis.setex.return_value = True
        mock_redis.delete.return_value = 1
        mock_redis.exists.return_value = 1
        mock_redis.ttl.return_value = 300
        
        cache_manager = CacheManager(redis_client=mock_redis)
        
        # 测试获取
        result = await cache_manager.get("test_key")
        assert result == {"test": "value"}
        
        # 测试设置
        result = await cache_manager.set("test_key", {"test": "value"})
        assert result is True
        
        # 测试存在性检查
        result = await cache_manager.exists("test_key")
        assert result is True
        
        # 测试删除
        result = await cache_manager.delete("test_key")
        assert result is True
        
        # 测试TTL
        result = await cache_manager.get_ttl("test_key")
        assert result == 300


class TestQueryOptimizer:
    """查询优化器测试类"""

    @pytest.fixture
    def optimizer(self):
        """创建查询优化器实例"""
        return QueryOptimizer()

    def test_init(self, optimizer):
        """测试初始化"""
        assert optimizer.cache_manager is None  # 没有提供缓存管理器

    def test_generate_cache_key(self, optimizer):
        """测试缓存键生成"""
        params = {"limit": 10, "offset": 0}
        key = optimizer._generate_cache_key("test_query", params)
        
        assert isinstance(key, str)
        assert key.startswith("query:test_query:")

    @pytest.mark.asyncio
    async def test_get_cached_query_result_no_cache(self, optimizer):
        """测试没有缓存管理器时获取缓存结果"""
        result = await optimizer.get_cached_query_result("test", {})
        assert result is None

    @pytest.mark.asyncio
    async def test_cache_query_result_no_cache(self, optimizer):
        """测试没有缓存管理器时缓存结果"""
        result = await optimizer.cache_query_result("test", {}, {"data": "test"})
        assert result is False

    @pytest.mark.asyncio
    async def test_with_cache_manager(self):
        """测试带有缓存管理器的查询优化器"""
        mock_cache = Mock()
        mock_cache.get = AsyncMock(return_value={"cached": "data"})
        mock_cache.set = AsyncMock(return_value=True)
        
        optimizer = QueryOptimizer(cache_manager=mock_cache)
        
        # 测试获取缓存结果
        result = await optimizer.get_cached_query_result("test", {"param": "value"})
        assert result == {"cached": "data"}
        
        # 测试缓存结果
        result = await optimizer.cache_query_result("test", {"param": "value"}, {"new": "data"})
        assert result is True

    @pytest.mark.asyncio
    async def test_get_optimized_pending_tasks(self, optimizer):
        """测试优化的待审核任务查询"""
        mock_session = AsyncMock()
        
        # 创建模拟的行对象
        mock_row = Mock()
        mock_row._mapping = {
            "id": 1,
            "task_id": "task_001", 
            "review_type": "medical_diagnosis",
            "priority": "high",
            "status": "pending",
            "created_at": "2023-01-01"
        }
        
        mock_result = Mock()
        mock_result.__iter__ = Mock(return_value=iter([mock_row]))
        mock_session.execute.return_value = mock_result
        
        result = await optimizer.get_optimized_pending_tasks(mock_session, limit=10, offset=0)
        
        assert isinstance(result, list)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_optimized_reviewer_workload(self, optimizer):
        """测试优化的审核员工作负载查询"""
        mock_session = AsyncMock()
        
        # 创建模拟的行对象
        mock_row = Mock()
        mock_row._mapping = {
            "total_tasks": 5,
            "pending_tasks": 2,
            "completed_tasks": 3,
            "accuracy_rate": 0.95,
            "avg_review_time": 30.5
        }
        
        mock_result = Mock()
        mock_result.first.return_value = mock_row
        mock_session.execute.return_value = mock_result
        
        result = await optimizer.get_optimized_reviewer_workload(mock_session, "reviewer_001")
        
        assert isinstance(result, dict)
        assert "total_tasks" in result
        assert "pending_tasks" in result
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_optimized_dashboard_stats(self, optimizer):
        """测试优化的仪表板统计查询"""
        mock_session = AsyncMock()

        # 创建模拟的行对象
        mock_row = Mock()
        mock_row._mapping = {
            "total_tasks": 100,
            "pending_tasks": 25,
            "in_progress_tasks": 50,
            "completed_tasks": 20,
            "rejected_tasks": 5
        }

        mock_result = Mock()
        mock_result.first.return_value = mock_row
        mock_session.execute.return_value = mock_result

        result = await optimizer.get_optimized_dashboard_stats(mock_session)

        assert isinstance(result, dict)
        assert "total_tasks" in result
        assert "pending_tasks" in result
        # 该方法执行两次查询（任务统计和审核员统计），所以调用次数应该是2
        assert mock_session.execute.call_count == 2


class TestPerformanceMonitor:
    """性能监控器测试类"""

    @pytest.fixture
    def monitor(self):
        """创建性能监控器实例"""
        return PerformanceMonitor()

    def test_init(self, monitor):
        """测试初始化"""
        assert monitor.metrics == {}
        assert monitor.slow_query_threshold == 1.0

    def test_record_query_time(self, monitor):
        """测试记录查询时间"""
        monitor.record_query_time("test_query", 1.5)
        
        stats = monitor.get_query_stats("test_query")
        assert stats["count"] == 1
        assert stats["total_time"] == 1.5
        assert stats["avg_time"] == 1.5

    def test_multiple_query_records(self, monitor):
        """测试多次查询记录"""
        monitor.record_query_time("test_query", 1.0)
        monitor.record_query_time("test_query", 2.0)
        monitor.record_query_time("test_query", 3.0)
        
        stats = monitor.get_query_stats("test_query")
        assert stats["count"] == 3
        assert stats["total_time"] == 6.0
        assert stats["avg_time"] == 2.0
        assert stats["min_time"] == 1.0
        assert stats["max_time"] == 3.0

    def test_get_query_stats_nonexistent(self, monitor):
        """测试获取不存在查询的统计"""
        stats = monitor.get_query_stats("nonexistent_query")
        
        assert stats == {}

    def test_get_all_stats(self, monitor):
        """测试获取所有统计信息"""
        monitor.record_query_time("query1", 1.0)
        monitor.record_query_time("query2", 2.0)
        
        all_stats = monitor.get_all_stats()
        
        assert "query1" in all_stats
        assert "query2" in all_stats
        assert all_stats["query1"]["count"] == 1
        assert all_stats["query2"]["count"] == 1

    def test_reset_stats(self, monitor):
        """测试重置统计信息"""
        monitor.record_query_time("test_query", 1.0)
        assert monitor.get_query_stats("test_query")["count"] == 1
        
        monitor.reset_stats()
        assert monitor.get_query_stats("test_query") == {}


class TestConnectionPoolOptimizer:
    """连接池优化器测试类"""

    @pytest.fixture
    def optimizer(self):
        """创建连接池优化器实例"""
        return ConnectionPoolOptimizer()

    def test_init(self, optimizer):
        """测试初始化"""
        assert optimizer.pool_stats is not None
        assert "active_connections" in optimizer.pool_stats
        assert "idle_connections" in optimizer.pool_stats

    @pytest.mark.asyncio
    async def test_optimize_pool_size(self, optimizer):
        """测试优化连接池大小"""
        current_load = 0.8  # 80%负载
        
        result = await optimizer.optimize_pool_size(current_load)
        
        assert isinstance(result, dict)
        assert "pool_size" in result
        assert "max_overflow" in result
        assert "current_load" in result

    def test_record_connection_event(self, optimizer):
        """测试记录连接事件"""
        initial_errors = optimizer.pool_stats["connection_errors"]
        optimizer.record_connection_event("connection_errors")
        
        assert optimizer.pool_stats["connection_errors"] == initial_errors + 1

    def test_get_pool_health(self, optimizer):
        """测试获取连接池健康状态"""
        # 记录一些连接事件
        optimizer.record_connection_event("connection_errors")
        
        health = optimizer.get_pool_health()
        
        assert isinstance(health, dict)
        assert "status" in health
        assert "stats" in health

    @pytest.mark.asyncio
    async def test_optimize_pool_size_low_load(self, optimizer):
        """测试低负载时的连接池优化"""
        current_load = 0.2  # 20%负载
        
        result = await optimizer.optimize_pool_size(current_load)
        
        # 低负载时应该建议较小的连接池
        assert result["pool_size"] <= 20  # 默认最大值

    @pytest.mark.asyncio
    async def test_optimize_pool_size_high_load(self, optimizer):
        """测试高负载时的连接池优化"""
        current_load = 0.95  # 95%负载
        
        result = await optimizer.optimize_pool_size(current_load)
        
        # 高负载时应该建议较大的连接池
        assert result["pool_size"] >= 5  # 最小值


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

    @pytest.mark.asyncio
    async def test_cache_and_monitor_integration(self, cache_manager, performance_monitor):
        """测试缓存和监控集成"""
        # 测试缓存管理器基本功能
        result = await cache_manager.get("test_key")
        assert result is None
        
        # 测试性能监控器基本功能
        performance_monitor.record_query_time("test_query", 1.0)
        stats = performance_monitor.get_query_stats("test_query")
        assert stats["count"] == 1

    @pytest.mark.asyncio
    async def test_query_optimizer_integration(self, query_optimizer):
        """测试查询优化器集成"""
        # 测试查询优化器基本功能
        mock_session = AsyncMock()
        mock_result = Mock()
        # 模拟可迭代的结果
        mock_result.__iter__ = Mock(return_value=iter([]))
        mock_session.execute.return_value = mock_result
        
        result = await query_optimizer.get_optimized_pending_tasks(mock_session)
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_connection_pool_optimization(self, connection_optimizer):
        """测试连接池优化"""
        # 测试连接池配置优化
        result = await connection_optimizer.optimize_pool_size(0.5)
        
        assert isinstance(result, dict)
        assert "pool_size" in result

    def test_performance_monitoring_workflow(self, performance_monitor):
        """测试性能监控工作流"""
        # 记录多个查询时间
        query_times = [0.1, 0.2, 0.15, 0.3, 0.25]
        for time_val in query_times:
            performance_monitor.record_query_time("api_query", time_val)
        
        # 获取统计信息
        stats = performance_monitor.get_query_stats("api_query")
        assert stats["count"] == 5
        assert stats["avg_time"] == sum(query_times) / len(query_times)

    @pytest.mark.asyncio
    async def test_cache_performance_monitoring(self, cache_manager, performance_monitor):
        """测试缓存性能监控"""
        # 测试缓存操作的性能监控
        result = await cache_manager.get("perf_test")
        assert result is None
        
        # 记录性能指标
        performance_monitor.record_query_time("cache_operation", 0.01)
        
        stats = performance_monitor.get_query_stats("cache_operation")
        assert stats["count"] == 1 