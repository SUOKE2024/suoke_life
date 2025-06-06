"""
test_e2e - 索克生活项目模块
"""

from cmd.server.main import app
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import asyncio
import json
import pytest
import time

"""端到端测试"""




@pytest.fixture
def client():
    """测试客户端"""
    return TestClient(app)


@pytest.fixture
def sample_test_data():
    """示例测试数据"""
    return [
        {
            "text": "I love this product, it's amazing!",
            "label": "positive"
        },
        {
            "text": "This is terrible, worst purchase ever.",
            "label": "negative"
        },
        {
            "text": "It's okay, nothing special.",
            "label": "neutral"
        }
    ]


class TestCompleteWorkflow:
    """完整工作流程测试"""

    def test_health_check_workflow(self, client):
        """测试健康检查工作流程"""
        
        # 检查服务健康状态
        health_response = client.get("/health")
        assert health_response.status_code == 200
        assert health_response.json()["status"] == "healthy"

    def test_complete_benchmark_workflow(self, client, sample_test_data):
        """测试完整的基准测试工作流程"""
        
        # 1. 检查服务健康状态
        health_response = client.get("/health")
        assert health_response.status_code == 200
        assert health_response.json()["status"] == "healthy"
        
        # 2. 列出可用的基准测试
        with patch('cmd.server.api.benchmark_service') as mock_service:
            mock_service.ListBenchmarks.return_value = Mock(
                benchmarks=[
                    Mock(to_dict=lambda: {
                        "id": "sentiment-analysis",
                        "name": "情感分析基准测试",
                        "description": "测试情感分析模型的准确性"
                    })
                ]
            )
            
            benchmarks_response = client.get("/api/benchmarks")
            assert benchmarks_response.status_code == 200
            benchmarks = benchmarks_response.json()
            assert len(benchmarks) > 0
            assert benchmarks[0]["id"] == "sentiment-analysis"
        
        # 3. 注册测试模型
        with patch('cmd.server.api.model_registry') as mock_registry:
            mock_registry.register_model.return_value = True
            
            model_data = {
                "model_id": "bert-sentiment",
                "model_version": "v1.0",
                "model_type": "local",
                "model_config": {
                    "path": "/models/bert-sentiment",
                    "framework": "pytorch"
                }
            }
            
            register_response = client.post("/api/models/register", json=model_data)
            assert register_response.status_code == 200
            assert register_response.json()["message"] == "模型注册成功"
        
        # 4. 提交基准测试任务
        with patch('cmd.server.api.get_global_executor') as mock_executor:
            mock_executor.return_value.submit_benchmark.return_value = "task-12345"
            
            benchmark_request = {
                "benchmark_id": "sentiment-analysis",
                "model_id": "bert-sentiment",
                "model_version": "v1.0",
                "test_data": sample_test_data,
                "config": {"batch_size": 16, "timeout": 300}
            }
            
            submit_response = client.post("/api/benchmarks/submit", json=benchmark_request)
            assert submit_response.status_code == 200
            
            result = submit_response.json()
            task_id = result["task_id"]
            assert task_id == "task-12345"
            assert result["status"] == "submitted"
        
        # 5. 检查任务状态
        with patch('cmd.server.api.get_global_executor') as mock_executor:
            mock_executor.return_value.get_task_status.return_value = {
                "task_id": task_id,
                "status": "running",
                "progress": 0.5,
                "created_at": "2024-12-01T10:00:00Z",
                "error_message": None
            }
            
            status_response = client.get(f"/api/benchmarks/tasks/{task_id}")
            assert status_response.status_code == 200
            
            status = status_response.json()
            assert status["task_id"] == task_id
            assert status["status"] == "running"
            assert status["progress"] == 0.5
        
        # 6. 等待任务完成并获取结果
        with patch('cmd.server.api.get_global_executor') as mock_executor:
            # 模拟任务完成
            mock_executor.return_value.get_task_status.return_value = {
                "task_id": task_id,
                "status": "completed",
                "progress": 1.0,
                "created_at": "2024-12-01T10:00:00Z",
                "error_message": None
            }
            
            mock_executor.return_value.get_task_result.return_value = Mock(
                task_id=task_id,
                benchmark_id="sentiment-analysis",
                model_id="bert-sentiment",
                model_version="v1.0",
                metrics={
                    "accuracy": 0.95,
                    "precision": 0.94,
                    "recall": 0.96,
                    "f1": 0.95
                },
                predictions=[
                    {"input": sample_test_data[0], "prediction": "positive", "confidence": 0.98},
                    {"input": sample_test_data[1], "prediction": "negative", "confidence": 0.97},
                    {"input": sample_test_data[2], "prediction": "neutral", "confidence": 0.85}
                ],
                execution_time=45.2,
                timestamp="2024-12-01T10:05:00Z",
                metadata={"batch_size": 16}
            )
            
            # 检查最终状态
            final_status_response = client.get(f"/api/benchmarks/tasks/{task_id}")
            assert final_status_response.status_code == 200
            final_status = final_status_response.json()
            assert final_status["status"] == "completed"
            
            # 获取详细结果
            result_response = client.get(f"/api/benchmarks/tasks/{task_id}/result")
            assert result_response.status_code == 200
            
            result_data = result_response.json()
            assert result_data["task_id"] == task_id
            assert result_data["metrics"]["accuracy"] == 0.95
            assert len(result_data["predictions"]) == 3
        
        # 7. 生成报告
        with patch('cmd.server.api.get_global_executor') as mock_executor:
            mock_executor.return_value.generate_report.return_value = f"reports/{task_id}_report.html"
            
            report_response = client.post(f"/api/benchmarks/tasks/{task_id}/report")
            assert report_response.status_code == 200
            
            report_data = report_response.json()
            assert "report_url" in report_data
            assert task_id in report_data["report_url"]

    def test_model_management_workflow(self, client):
        """测试模型管理工作流程"""
        
        with patch('cmd.server.api.model_registry') as mock_registry:
            # 1. 注册多个模型
            models = [
                {
                    "model_id": "bert-base",
                    "model_version": "v1.0",
                    "model_type": "local",
                    "model_config": {"path": "/models/bert-base"}
                },
                {
                    "model_id": "roberta-large",
                    "model_version": "v2.0",
                    "model_type": "remote_api",
                    "model_config": {"api_url": "https://api.example.com/roberta"}
                }
            ]
            
            mock_registry.register_model.return_value = True
            
            for model in models:
                response = client.post("/api/models/register", json=model)
                assert response.status_code == 200
            
            # 2. 列出已注册的模型
            mock_registry.list_models.return_value = [
                {
                    "model_id": "bert-base",
                    "model_version": "v1.0",
                    "model_type": "local",
                    "registered_at": "2024-12-01T10:00:00Z"
                },
                {
                    "model_id": "roberta-large",
                    "model_version": "v2.0",
                    "model_type": "remote_api",
                    "registered_at": "2024-12-01T10:05:00Z"
                }
            ]
            
            list_response = client.get("/api/models")
            assert list_response.status_code == 200
            
            model_list = list_response.json()
            assert len(model_list) == 2
            
            # 3. 注销模型
            mock_registry.unregister_model.return_value = True
            
            unregister_response = client.delete("/api/models/bert-base/v1.0")
            assert unregister_response.status_code == 200

    def test_cache_management_workflow(self, client):
        """测试缓存管理工作流程"""
        
        with patch('cmd.server.api.get_global_cache') as mock_cache:
            # 1. 获取缓存统计
            mock_cache.return_value.get_cache_stats.return_value = {
                "total_models": 3,
                "total_memory_mb": 2048.5,
                "memory_usage_percent": 65.2,
                "models": {
                    "bert-base:v1.0": {"memory_mb": 512.0, "last_used": "2024-12-01T10:00:00Z"},
                    "roberta-large:v2.0": {"memory_mb": 1024.0, "last_used": "2024-12-01T09:30:00Z"},
                    "gpt-3.5:v1.0": {"memory_mb": 512.5, "last_used": "2024-12-01T09:45:00Z"}
                }
            }
            
            stats_response = client.get("/api/cache/stats")
            assert stats_response.status_code == 200
            
            stats = stats_response.json()
            assert stats["total_models"] == 3
            assert stats["total_memory_mb"] == 2048.5
            assert "bert-base:v1.0" in stats["models"]
            
            # 2. 预加载模型
            preload_config = {
                "bert-base:v1.0": "local",
                "roberta-large:v2.0": "remote_api"
            }
            
            preload_response = client.post("/api/cache/preload", json=preload_config)
            assert preload_response.status_code == 200
            
            # 3. 清空缓存
            mock_cache.return_value.clear_cache.return_value = None
            
            clear_response = client.post("/api/cache/clear")
            assert clear_response.status_code == 200
            assert clear_response.json()["message"] == "缓存已清空"

    def test_monitoring_workflow(self, client):
        """测试监控工作流程"""
        
        # 1. 健康检查
        health_response = client.get("/health")
        assert health_response.status_code == 200
        
        health_data = health_response.json()
        assert health_data["status"] == "healthy"
        assert "timestamp" in health_data
        assert "version" in health_data
        
        # 2. 详细健康检查
        detailed_health_response = client.get("/api/health/detailed")
        assert detailed_health_response.status_code == 200
        
        # 3. Prometheus指标
        metrics_response = client.get("/metrics")
        assert metrics_response.status_code == 200
        assert metrics_response.headers["content-type"] == "text/plain; charset=utf-8"
        
        # 4. 指标摘要
        with patch('cmd.server.api.get_global_metrics') as mock_metrics:
            mock_metrics.return_value.get_metrics_summary.return_value = {
                "total_requests": 1250,
                "success_rate": 0.98,
                "avg_response_time": 145.2,
                "active_benchmarks": 3,
                "completed_benchmarks": 47
            }
            
            summary_response = client.get("/api/metrics/summary")
            assert summary_response.status_code == 200
            
            summary = summary_response.json()
            assert summary["metrics"]["total_requests"] == 1250
            assert summary["metrics"]["success_rate"] == 0.98

    def test_error_scenarios(self, client):
        """测试错误场景"""
        
        # 1. 无效的基准测试请求
        invalid_request = {
            "benchmark_id": "",  # 空ID
            "model_id": "test-model",
            "model_version": "v1.0"
        }
        
        response = client.post("/api/run", json=invalid_request)
        assert response.status_code == 422  # 验证错误
        
        # 2. 不存在的任务状态查询
        response = client.get("/api/benchmarks/tasks/nonexistent-task")
        assert response.status_code == 404
        
        # 3. 不存在的模型注销
        with patch('cmd.server.api.model_registry') as mock_registry:
            mock_registry.unregister_model.return_value = False
            
            response = client.delete("/api/models/nonexistent/v1.0")
            assert response.status_code == 404
        
        # 4. 服务内部错误
        with patch('cmd.server.api.get_global_executor') as mock_executor:
            mock_executor.side_effect = Exception("内部服务错误")
            
            request_data = {
                "benchmark_id": "test",
                "model_id": "test-model",
                "model_version": "v1.0",
                "test_data": [{"input": "test"}]
            }
            
            response = client.post("/api/benchmarks/submit", json=request_data)
            assert response.status_code == 500

    def test_concurrent_requests(self, client, sample_test_data):
        """测试并发请求处理"""
        
        with patch('cmd.server.api.get_global_executor') as mock_executor:
            # 模拟多个并发任务提交
            task_ids = []
            
            def mock_submit(benchmark_id, model_id, model_version, test_data, config=None):
                task_id = f"task-{len(task_ids) + 1}"
                task_ids.append(task_id)
                return task_id
            
            mock_executor.return_value.submit_benchmark.side_effect = mock_submit
            
            # 并发提交多个任务
            requests = []
            for i in range(5):
                request_data = {
                    "benchmark_id": f"test-{i}",
                    "model_id": "test-model",
                    "model_version": "v1.0",
                    "test_data": sample_test_data,
                    "config": {"batch_size": 16}
                }
                requests.append(request_data)
            
            responses = []
            for request_data in requests:
                response = client.post("/api/benchmarks/submit", json=request_data)
                responses.append(response)
            
            # 验证所有请求都成功
            for response in responses:
                assert response.status_code == 200
                result = response.json()
                assert result["status"] == "submitted"
                assert result["task_id"] in task_ids
            
            assert len(set(task_ids)) == 5  # 确保任务ID唯一

    def test_data_validation(self, client):
        """测试数据验证"""
        
        # 1. 缺少必需字段
        incomplete_request = {
            "benchmark_id": "test",
            # 缺少 model_id
            "model_version": "v1.0"
        }
        
        response = client.post("/api/run", json=incomplete_request)
        assert response.status_code == 422
        
        # 2. 无效的数据类型
        invalid_type_request = {
            "benchmark_id": "test",
            "model_id": "test-model",
            "model_version": "v1.0",
            "parameters": "invalid"  # 应该是字典
        }
        
        response = client.post("/api/run", json=invalid_type_request)
        assert response.status_code == 422
        
        # 3. 空的测试数据
        empty_data_request = {
            "benchmark_id": "test",
            "model_id": "test-model",
            "model_version": "v1.0",
            "test_data": [],  # 空数据
            "config": {}
        }
        
        response = client.post("/api/benchmarks/submit", json=empty_data_request)
        assert response.status_code == 422


class TestPerformanceScenarios:
    """性能场景测试"""

    def test_large_dataset_handling(self, client):
        """测试大数据集处理"""
        
        # 生成大量测试数据
        large_dataset = []
        for i in range(1000):
            large_dataset.append({
                "text": f"This is test sample number {i}",
                "label": "positive" if i % 2 == 0 else "negative"
            })
        
        with patch('cmd.server.api.get_global_executor') as mock_executor:
            mock_executor.return_value.submit_benchmark.return_value = "large-task-123"
            
            request_data = {
                "benchmark_id": "large-dataset-test",
                "model_id": "test-model",
                "model_version": "v1.0",
                "test_data": large_dataset,
                "config": {"batch_size": 64}
            }
            
            start_time = time.time()
            response = client.post("/api/benchmarks/submit", json=request_data)
            end_time = time.time()
            
            # 验证请求在合理时间内完成（< 5秒）
            assert (end_time - start_time) < 5.0
            assert response.status_code == 200

    def test_timeout_handling(self, client):
        """测试超时处理"""
        
        with patch('cmd.server.api.get_global_executor') as mock_executor:
            # 模拟超时任务
            mock_executor.return_value.get_task_status.return_value = {
                "task_id": "timeout-task",
                "status": "failed",
                "progress": 0.3,
                "created_at": "2024-12-01T10:00:00Z",
                "error_message": "任务执行超时"
            }
            
            response = client.get("/api/benchmarks/tasks/timeout-task")
            assert response.status_code == 200
            
            status = response.json()
            assert status["status"] == "failed"
            assert "超时" in status["error_message"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 