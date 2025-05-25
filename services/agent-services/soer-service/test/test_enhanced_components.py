"""
增强组件测试用例
验证依赖注入、错误处理、指标收集等功能
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from pkg.utils.dependency_injection import DependencyContainer, ServiceLifecycle
from pkg.utils.error_handling import SoerServiceException, ErrorSeverity, retry_async, RetryConfig
from pkg.utils.metrics import MetricsCollector
from pkg.utils.enhanced_config import EnhancedConfig
from internal.delivery.health_check import HealthChecker, ComponentHealth

class TestDependencyInjection:
    """测试依赖注入容器"""
    
    def test_container_creation(self):
        """测试容器创建"""
        container = DependencyContainer()
        assert container is not None
    
    def test_service_registration(self):
        """测试服务注册"""
        container = DependencyContainer()
        
        # 注册单例服务
        mock_service = Mock()
        container.register_singleton("test_service", lambda: mock_service)
        
        # 获取服务
        service = container.get_service("test_service")
        assert service is mock_service
        
        # 再次获取应该是同一个实例
        service2 = container.get_service("test_service")
        assert service is service2
    
    def test_factory_registration(self):
        """测试工厂注册"""
        container = DependencyContainer()
        
        # 注册工厂服务
        container.register_factory("test_factory", lambda: Mock())
        
        # 获取服务
        service1 = container.get_service("test_factory")
        service2 = container.get_service("test_factory")
        
        # 应该是不同的实例
        assert service1 is not service2
    
    def test_service_not_found(self):
        """测试服务未找到"""
        container = DependencyContainer()
        
        with pytest.raises(ValueError, match="服务未注册"):
            container.get_service("non_existent")

class TestErrorHandling:
    """测试错误处理"""
    
    def test_soer_service_exception(self):
        """测试业务异常"""
        exception = SoerServiceException(
            "测试错误",
            error_code="TEST_ERROR",
            severity=ErrorSeverity.HIGH
        )
        
        assert str(exception) == "测试错误"
        assert exception.error_code == "TEST_ERROR"
        assert exception.severity == ErrorSeverity.HIGH
    
    @pytest.mark.asyncio
    async def test_retry_decorator_success(self):
        """测试重试装饰器成功情况"""
        call_count = 0
        
        @retry_async(RetryConfig(max_attempts=3, base_delay=0.01))
        async def test_function():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = await test_function()
        assert result == "success"
        assert call_count == 1
    
    @pytest.mark.asyncio
    async def test_retry_decorator_failure(self):
        """测试重试装饰器失败情况"""
        call_count = 0
        
        @retry_async(RetryConfig(max_attempts=3, base_delay=0.01))
        async def test_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("测试错误")
        
        with pytest.raises(ValueError):
            await test_function()
        
        assert call_count == 3  # 应该重试3次

class TestMetricsCollector:
    """测试指标收集器"""
    
    def test_metrics_collector_creation(self):
        """测试指标收集器创建"""
        collector = MetricsCollector()
        assert collector is not None
    
    def test_counter_increment(self):
        """测试计数器递增"""
        collector = MetricsCollector()
        
        # 递增计数器
        collector.increment_counter("test_counter", {"label": "value"})
        
        # 验证计数器存在
        assert "test_counter" in collector._counters
    
    def test_histogram_observe(self):
        """测试直方图观察"""
        collector = MetricsCollector()
        
        # 观察值
        collector.observe_histogram("test_histogram", 0.5, {"label": "value"})
        
        # 验证直方图存在
        assert "test_histogram" in collector._histograms
    
    def test_gauge_set(self):
        """测试仪表盘设置"""
        collector = MetricsCollector()
        
        # 设置仪表盘值
        collector.set_gauge("test_gauge", 100, {"label": "value"})
        
        # 验证仪表盘存在
        assert "test_gauge" in collector._gauges

class TestEnhancedConfig:
    """测试增强配置管理"""
    
    def test_config_creation(self):
        """测试配置创建"""
        config_data = {
            "database": {
                "host": "localhost",
                "port": 5432
            },
            "redis": {
                "host": "localhost",
                "port": 6379
            }
        }
        
        config = EnhancedConfig(config_data)
        assert config is not None
    
    def test_config_get_section(self):
        """测试获取配置段"""
        config_data = {
            "database": {
                "host": "localhost",
                "port": 5432
            }
        }
        
        config = EnhancedConfig(config_data)
        db_config = config.get_section("database")
        
        assert db_config["host"] == "localhost"
        assert db_config["port"] == 5432
    
    def test_config_get_value(self):
        """测试获取配置值"""
        config_data = {
            "database": {
                "host": "localhost",
                "port": 5432
            }
        }
        
        config = EnhancedConfig(config_data)
        host = config.get_value("database.host")
        port = config.get_value("database.port")
        
        assert host == "localhost"
        assert port == 5432
    
    def test_config_environment_substitution(self):
        """测试环境变量替换"""
        import os
        
        # 设置环境变量
        os.environ["TEST_HOST"] = "test.example.com"
        
        config_data = {
            "database": {
                "host": "${TEST_HOST}",
                "port": 5432
            }
        }
        
        config = EnhancedConfig(config_data)
        host = config.get_value("database.host")
        
        assert host == "test.example.com"
        
        # 清理环境变量
        del os.environ["TEST_HOST"]

class TestHealthChecker:
    """测试健康检查器"""
    
    @pytest.mark.asyncio
    async def test_health_checker_creation(self):
        """测试健康检查器创建"""
        with patch('pkg.utils.dependency_injection.get_container'), \
             patch('pkg.utils.metrics.get_metrics_collector'), \
             patch('pkg.utils.connection_pool.get_pool_manager'):
            
            checker = HealthChecker()
            assert checker is not None
    
    @pytest.mark.asyncio
    async def test_component_health_creation(self):
        """测试组件健康状态创建"""
        health = ComponentHealth(
            name="test_component",
            status="healthy",
            message="组件运行正常",
            response_time_ms=50.0,
            details={"version": "1.0.0"}
        )
        
        assert health.name == "test_component"
        assert health.status == "healthy"
        assert health.message == "组件运行正常"
        assert health.response_time_ms == 50.0
        assert health.details["version"] == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_memory_check(self):
        """测试内存检查"""
        with patch('pkg.utils.dependency_injection.get_container'), \
             patch('pkg.utils.metrics.get_metrics_collector'), \
             patch('pkg.utils.connection_pool.get_pool_manager'):
            
            checker = HealthChecker()
            
            # 模拟psutil
            with patch('psutil.virtual_memory') as mock_memory:
                mock_memory.return_value = Mock(
                    total=8 * 1024**3,  # 8GB
                    available=4 * 1024**3,  # 4GB
                    percent=50.0
                )
                
                health = await checker._check_memory_usage()
                
                assert health.name == "memory"
                assert health.status == "healthy"
                assert "50.0%" in health.message

class MockServiceLifecycle(ServiceLifecycle):
    """模拟服务生命周期"""
    
    def __init__(self):
        self.started = False
        self.stopped = False
    
    async def start(self) -> None:
        self.started = True
    
    async def stop(self) -> None:
        self.stopped = True
    
    async def health_check(self) -> bool:
        return self.started and not self.stopped

class TestServiceLifecycle:
    """测试服务生命周期"""
    
    @pytest.mark.asyncio
    async def test_service_lifecycle(self):
        """测试服务生命周期管理"""
        service = MockServiceLifecycle()
        
        # 初始状态
        assert not service.started
        assert not service.stopped
        assert not await service.health_check()
        
        # 启动服务
        await service.start()
        assert service.started
        assert await service.health_check()
        
        # 停止服务
        await service.stop()
        assert service.stopped
        assert not await service.health_check()

if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"]) 