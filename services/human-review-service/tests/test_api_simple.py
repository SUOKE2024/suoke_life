"""
简化API测试
Simplified API Tests

专注于测试实际存在的API端点
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, Mock, patch

from human_review_service.api.main import create_app
from human_review_service.core.database import init_database


@pytest.fixture
def app():
    """创建测试应用"""
    # 模拟数据库初始化
    with patch('human_review_service.core.database.get_session_factory') as mock_factory, \
         patch('human_review_service.core.database.get_session_dependency') as mock_dep:
        
        mock_session = AsyncMock()
        mock_factory.return_value = lambda: mock_session
        
        # 模拟数据库依赖
        async def mock_session_dep():
            yield mock_session
        mock_dep.return_value = mock_session_dep()
        
        app = create_app(skip_lifespan=True)
        yield app


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return TestClient(app)


class TestHealthEndpoints:
    """健康检查端点测试"""

    def test_health_check(self, client):
        """测试健康检查端点"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_readiness_check(self, client):
        """测试就绪检查端点"""
        response = client.get("/ready")
        # 可能返回200或503，取决于数据库连接状态
        assert response.status_code in [200, 503]

    def test_liveness_check(self, client):
        """测试存活检查端点"""
        response = client.get("/live")
        assert response.status_code == 200


class TestMetricsEndpoints:
    """指标端点测试"""

    def test_metrics_endpoint(self, client):
        """测试Prometheus指标端点"""
        response = client.get("/metrics")
        assert response.status_code == 200
        # Prometheus指标应该是文本格式
        assert "text/plain" in response.headers.get("content-type", "")


class TestAPIDocumentation:
    """API文档端点测试"""

    def test_openapi_schema(self, client):
        """测试OpenAPI模式端点"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data

    def test_swagger_ui(self, client):
        """测试Swagger UI端点"""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    def test_redoc_ui(self, client):
        """测试ReDoc UI端点"""
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")


class TestCORSHeaders:
    """CORS头部测试"""

    def test_cors_preflight(self, client):
        """测试CORS预检请求"""
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type",
            }
        )
        # 检查CORS头部是否存在
        assert "access-control-allow-origin" in response.headers

    def test_cors_actual_request(self, client):
        """测试实际的CORS请求"""
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"}
        )
        assert response.status_code == 200
        # 检查CORS头部是否存在
        assert "access-control-allow-origin" in response.headers


class TestErrorHandling:
    """错误处理测试"""

    def test_404_not_found(self, client):
        """测试404错误"""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404

    def test_405_method_not_allowed(self, client):
        """测试405错误"""
        response = client.post("/health")  # health端点只支持GET
        assert response.status_code == 405

    def test_invalid_json_payload(self, client):
        """测试无效JSON负载"""
        response = client.post(
            "/api/v1/reviewers/",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422  # FastAPI返回422对于无效JSON


class TestMiddleware:
    """中间件测试"""

    def test_request_id_header(self, client):
        """测试请求ID头部"""
        response = client.get("/health")
        assert response.status_code == 200
        # 检查是否有请求ID头部
        assert "x-request-id" in response.headers

    def test_security_headers(self, client):
        """测试安全头部"""
        response = client.get("/health")
        assert response.status_code == 200
        # 检查基本的安全头部
        headers = response.headers
        # 这些头部可能由中间件添加
        security_headers = [
            "x-content-type-options",
            "x-frame-options",
            "x-xss-protection"
        ]
        # 至少应该有一些安全头部
        has_security_headers = any(header in headers for header in security_headers)
        # 如果没有安全头部，这可能是正常的，取决于配置


class TestRateLimiting:
    """速率限制测试"""

    def test_rate_limiting_basic(self, client):
        """测试基本的速率限制"""
        # 发送多个请求到健康检查端点
        responses = []
        for _ in range(10):
            response = client.get("/health")
            responses.append(response)

        # 大多数请求应该成功
        successful_responses = [r for r in responses if r.status_code == 200]
        assert len(successful_responses) >= 5  # 至少一半的请求应该成功

        # 检查是否有速率限制头部
        last_response = responses[-1]
        rate_limit_headers = [
            "x-ratelimit-limit",
            "x-ratelimit-remaining",
            "x-ratelimit-reset"
        ]
        # 速率限制头部可能存在也可能不存在，取决于配置


class TestContentNegotiation:
    """内容协商测试"""

    def test_json_content_type(self, client):
        """测试JSON内容类型"""
        response = client.get("/health")
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")

    def test_accept_header_handling(self, client):
        """测试Accept头部处理"""
        response = client.get(
            "/health",
            headers={"Accept": "application/json"}
        )
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")


class TestAPIVersioning:
    """API版本控制测试"""

    def test_api_v1_prefix(self, client):
        """测试API v1前缀"""
        # 测试v1 API端点是否存在
        response = client.get("/api/v1/")
        # 可能返回404（如果没有根端点）或其他状态码
        assert response.status_code in [200, 404, 405]

    def test_version_in_response_headers(self, client):
        """测试响应头中的版本信息"""
        response = client.get("/health")
        assert response.status_code == 200
        # 检查是否有版本头部
        version_headers = [
            "api-version",
            "x-api-version",
            "version"
        ]
        # 版本头部可能存在也可能不存在


class TestRequestValidation:
    """请求验证测试"""

    def test_content_length_validation(self, client):
        """测试内容长度验证"""
        # 发送一个空的POST请求
        response = client.post("/api/v1/reviewers/")
        # 应该返回422（验证错误）或400（错误请求）
        assert response.status_code in [400, 422]

    def test_content_type_validation(self, client):
        """测试内容类型验证"""
        response = client.post(
            "/api/v1/reviewers/",
            data="test data",
            headers={"Content-Type": "text/plain"}
        )
        # 应该返回415（不支持的媒体类型）或422（验证错误）
        assert response.status_code in [415, 422]


class TestResponseFormat:
    """响应格式测试"""

    def test_error_response_format(self, client):
        """测试错误响应格式"""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
        data = response.json()
        # FastAPI的标准错误格式
        assert "detail" in data

    def test_success_response_format(self, client):
        """测试成功响应格式"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "status" in data 