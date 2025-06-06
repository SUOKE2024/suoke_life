"""
test_api - 索克生活项目模块
"""

from cmd.server.main import app
from fastapi.testclient import TestClient
from internal.benchmark.benchmark_service import BenchmarkService
from internal.suokebench.config import BenchConfig
from unittest.mock import Mock, patch
import asyncio
import json
import pytest

"""API接口集成测试"""




@pytest.fixture
def client():
    """测试客户端"""
    return TestClient(app)


@pytest.fixture
def mock_config():
    """模拟配置"""
    return BenchConfig(
        service_name="test-service",
        version="1.0.0",
        data_root="./test_data",
        cache_dir="./test_cache",
        datasets={},
        metrics={},
        tasks={},
        report=Mock(),
        max_workers=2
    )


@pytest.fixture
def mock_benchmark_service():
    """模拟基准测试服务"""
    service = Mock(spec=BenchmarkService)
    service.RunBenchmark.return_value = Mock(
        run_id="test-run-123",
        status="running",
        message="测试已启动"
    )
    service.GetBenchmarkResult.return_value = Mock(
        run_id="test-run-123",
        benchmark_id="test-benchmark",
        model_id="test-model",
        model_version="v1.0",
        status="completed",
        metrics={"accuracy": Mock(to_dict=lambda: {"value": 0.95, "unit": "%"})},
        samples=[],
        task="classification",
        created_at="2024-12-01T10:00:00Z",
        completed_at="2024-12-01T10:05:00Z"
    )
    service.ListBenchmarks.return_value = Mock(
        benchmarks=[
            Mock(to_dict=lambda: {
                "id": "test-benchmark",
                "name": "测试基准",
                "description": "测试用基准测试"
            })
        ]
    )
    return service


class TestHealthEndpoints:
    """健康检查端点测试"""

    def test_health_check(self, client):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data

    def test_metrics_endpoint(self, client):
        """测试指标端点"""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"


class TestBenchmarkAPI:
    """基准测试API测试"""

    @patch('cmd.server.api.benchmark_service')
    def test_run_benchmark(self, mock_service, client, mock_benchmark_service):
        """测试运行基准测试"""
        mock_service.return_value = mock_benchmark_service
        
        request_data = {
            "benchmark_id": "test-benchmark",
            "model_id": "test-model",
            "model_version": "v1.0",
            "parameters": {"threshold": "0.8"}
        }
        
        response = client.post("/api/run", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["run_id"] == "test-run-123"
        assert data["status"] == "running"

    @patch('cmd.server.api.benchmark_service')
    def test_get_result(self, mock_service, client, mock_benchmark_service):
        """测试获取结果"""
        mock_service.return_value = mock_benchmark_service
        
        request_data = {
            "run_id": "test-run-123",
            "include_details": True
        }
        
        response = client.post("/api/result", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["run_id"] == "test-run-123"
        assert data["status"] == "completed"
        assert "metrics" in data

    @patch('cmd.server.api.benchmark_service')
    def test_list_benchmarks(self, mock_service, client, mock_benchmark_service):
        """测试列出基准测试"""
        mock_service.return_value = mock_benchmark_service
        
        response = client.get("/api/benchmarks")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]["id"] == "test-benchmark"

    def test_invalid_benchmark_request(self, client):
        """测试无效请求"""
        request_data = {
            "benchmark_id": "",  # 空的benchmark_id
            "model_id": "test-model"
        }
        
        response = client.post("/api/run", json=request_data)
        assert response.status_code == 422  # 验证错误


class TestModelManagementAPI:
    """模型管理API测试"""

    @patch('cmd.server.api.model_registry')
    def test_register_model(self, mock_registry, client):
        """测试注册模型"""
        mock_registry.register_model.return_value = True
        
        request_data = {
            "model_id": "test-model",
            "model_version": "v1.0",
            "model_type": "local",
            "model_config": {
                "path": "/path/to/model",
                "framework": "pytorch"
            }
        }
        
        response = client.post("/api/models/register", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "模型注册成功"

    @patch('cmd.server.api.model_registry')
    def test_list_models(self, mock_registry, client):
        """测试列出模型"""
        mock_registry.list_models.return_value = [
            {
                "model_id": "test-model",
                "model_version": "v1.0",
                "model_type": "local",
                "registered_at": "2024-12-01T10:00:00Z"
            }
        ]
        
        response = client.get("/api/models")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    @patch('cmd.server.api.model_registry')
    def test_unregister_model(self, mock_registry, client):
        """测试注销模型"""
        mock_registry.unregister_model.return_value = True
        
        response = client.delete("/api/models/test-model/v1.0")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "模型注销成功"


class TestCacheAPI:
    """缓存API测试"""

    @patch('cmd.server.api.get_global_cache')
    def test_cache_stats(self, mock_cache, client):
        """测试缓存统计"""
        mock_cache.return_value.get_cache_stats.return_value = {
            "total_models": 5,
            "total_memory_mb": 1024.5,
            "memory_usage_percent": 45.2,
            "models": {}
        }
        
        response = client.get("/api/cache/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_models"] == 5
        assert data["total_memory_mb"] == 1024.5

    @patch('cmd.server.api.get_global_cache')
    def test_clear_cache(self, mock_cache, client):
        """测试清空缓存"""
        mock_cache.return_value.clear_cache.return_value = None
        
        response = client.post("/api/cache/clear")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "缓存已清空"


class TestErrorHandling:
    """错误处理测试"""

    def test_404_endpoint(self, client):
        """测试404错误"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404

    def test_method_not_allowed(self, client):
        """测试方法不允许错误"""
        response = client.put("/api/run")
        assert response.status_code == 405

    @patch('cmd.server.api.benchmark_service')
    def test_internal_server_error(self, mock_service, client):
        """测试内部服务器错误"""
        mock_service.side_effect = Exception("内部错误")
        
        request_data = {
            "benchmark_id": "test-benchmark",
            "model_id": "test-model",
            "model_version": "v1.0"
        }
        
        response = client.post("/api/run", json=request_data)
        assert response.status_code == 500


class TestAsyncEndpoints:
    """异步端点测试"""

    @pytest.mark.asyncio
    async def test_async_benchmark_submission(self, client):
        """测试异步基准测试提交"""
        request_data = {
            "benchmark_id": "async-test",
            "model_id": "async-model",
            "model_version": "v1.0",
            "test_data": [{"input": "test", "expected": "result"}],
            "config": {"timeout": 300}
        }
        
        with patch('cmd.server.api.get_global_executor') as mock_executor:
            mock_executor.return_value.submit_benchmark.return_value = "task-123"
            
            response = client.post("/api/benchmarks/submit", json=request_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["task_id"] == "task-123"
            assert data["status"] == "submitted"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 