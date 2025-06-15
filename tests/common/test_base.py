"""
索克生活通用测试基类

提供所有微服务共用的测试基础设施和工具。
"""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Dict, Any, Optional
from unittest.mock import AsyncMock, MagicMock
from abc import ABC, abstractmethod

from fastapi.testclient import TestClient
from httpx import AsyncClient
import structlog

# 配置测试日志
structlog.configure(
    processors=[
        structlog.testing.LogCapture(),
    ],
    wrapper_class=structlog.testing.ReturnLoggerFactory(),
    logger_factory=structlog.testing.TestingLoggerFactory(),
    cache_logger_on_first_use=True,
)


class BaseTestCase(ABC):
    """所有测试用例的基类"""
    
    @pytest.fixture(scope="session")
    def event_loop_policy(self):
        """事件循环策略"""
        return asyncio.get_event_loop_policy()

    @pytest.fixture(scope="session")
    def event_loop(self, event_loop_policy):
        """事件循环"""
        loop = event_loop_policy.new_event_loop()
        yield loop
        loop.close()

    @pytest.fixture
    async def async_client(self) -> AsyncGenerator[AsyncClient, None]:
        """异步HTTP客户端"""
        async with AsyncClient() as client:
            yield client

    @pytest.fixture
    def mock_logger(self):
        """模拟日志器"""
        return structlog.testing.TestingLogger()

    @pytest.fixture
    def sample_headers(self) -> Dict[str, str]:
        """标准请求头"""
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Request-ID": "test-request-123",
            "X-Client-Version": "2.0.0"
        }

    @pytest.fixture
    def auth_headers(self, sample_headers) -> Dict[str, str]:
        """带认证的请求头"""
        headers = sample_headers.copy()
        headers["Authorization"] = "Bearer test-token-123"
        return headers


class APITestCase(BaseTestCase):
    """API测试用例基类"""
    
    @abstractmethod
    def get_app(self):
        """获取FastAPI应用实例"""
        pass

    @pytest.fixture
    def client(self):
        """测试客户端"""
        app = self.get_app()
        return TestClient(app)

    async def assert_response_success(self, response, expected_status: int = 200):
        """断言响应成功"""
        assert response.status_code == expected_status
        data = response.json()
        assert data.get("success") is True
        assert "data" in data
        assert "timestamp" in data
        assert "request_id" in data

    async def assert_response_error(self, response, expected_status: int = 400):
        """断言响应错误"""
        assert response.status_code == expected_status
        data = response.json()
        assert data.get("success") is False
        assert "error" in data
        assert "timestamp" in data
        assert "request_id" in data

    async def assert_validation_error(self, response):
        """断言验证错误"""
        await self.assert_response_error(response, 422)
        data = response.json()
        assert data["error"]["code"] == "VALIDATION_ERROR"

    async def assert_not_found_error(self, response):
        """断言资源不存在错误"""
        await self.assert_response_error(response, 404)
        data = response.json()
        assert data["error"]["code"] == "NOT_FOUND"

    async def assert_unauthorized_error(self, response):
        """断言未认证错误"""
        await self.assert_response_error(response, 401)
        data = response.json()
        assert data["error"]["code"] == "UNAUTHORIZED"


class ServiceTestCase(BaseTestCase):
    """服务层测试用例基类"""
    
    @pytest.fixture
    def mock_repository(self):
        """模拟仓库"""
        return AsyncMock()

    @pytest.fixture
    def mock_external_service(self):
        """模拟外部服务"""
        return AsyncMock()

    @pytest.fixture
    def mock_cache(self):
        """模拟缓存"""
        cache = AsyncMock()
        cache.get.return_value = None
        cache.set.return_value = True
        cache.delete.return_value = True
        return cache

    @pytest.fixture
    def mock_message_bus(self):
        """模拟消息总线"""
        bus = AsyncMock()
        bus.publish.return_value = True
        bus.subscribe.return_value = True
        return bus


class IntegrationTestCase(BaseTestCase):
    """集成测试用例基类"""
    
    @pytest.fixture(scope="session")
    async def test_database(self):
        """测试数据库"""
        # 这里应该设置测试数据库连接
        # 实际实现需要根据具体的数据库类型来配置
        yield "test_db_connection"

    @pytest.fixture(scope="session")
    async def test_redis(self):
        """测试Redis"""
        # 这里应该设置测试Redis连接
        yield "test_redis_connection"

    @pytest.fixture
    async def clean_database(self, test_database):
        """清理数据库"""
        # 测试前清理
        yield
        # 测试后清理

    @pytest.fixture
    async def clean_cache(self, test_redis):
        """清理缓存"""
        # 测试前清理
        yield
        # 测试后清理


class PerformanceTestCase(BaseTestCase):
    """性能测试用例基类"""
    
    @pytest.fixture
    def performance_config(self) -> Dict[str, Any]:
        """性能测试配置"""
        return {
            "max_response_time": 100,  # 毫秒
            "max_memory_usage": 100,   # MB
            "max_cpu_usage": 80,       # 百分比
            "concurrent_users": 100,
            "test_duration": 60,       # 秒
        }

    def assert_response_time(self, response_time: float, max_time: float = 100):
        """断言响应时间"""
        assert response_time <= max_time, f"响应时间 {response_time}ms 超过限制 {max_time}ms"

    def assert_memory_usage(self, memory_mb: float, max_memory: float = 100):
        """断言内存使用"""
        assert memory_mb <= max_memory, f"内存使用 {memory_mb}MB 超过限制 {max_memory}MB"

    def assert_cpu_usage(self, cpu_percent: float, max_cpu: float = 80):
        """断言CPU使用"""
        assert cpu_percent <= max_cpu, f"CPU使用 {cpu_percent}% 超过限制 {max_cpu}%"


class AgentTestCase(APITestCase):
    """智能体测试用例基类"""
    
    @pytest.fixture
    def mock_llm_client(self):
        """模拟LLM客户端"""
        client = AsyncMock()
        client.chat.return_value = {
            "response": "这是一个测试响应",
            "usage": {"tokens": 100},
            "model": "test-model"
        }
        return client

    @pytest.fixture
    def mock_vector_store(self):
        """模拟向量存储"""
        store = AsyncMock()
        store.search.return_value = [
            {"content": "相关文档1", "score": 0.9},
            {"content": "相关文档2", "score": 0.8}
        ]
        return store

    @pytest.fixture
    def sample_chat_request(self) -> Dict[str, Any]:
        """示例聊天请求"""
        return {
            "message": "你好，我想了解健康饮食建议",
            "user_id": "test-user-123",
            "session_id": "test-session-456",
            "context": {
                "user_profile": {
                    "age": 30,
                    "gender": "female",
                    "health_goals": ["减重", "改善睡眠"]
                }
            }
        }

    async def assert_chat_response(self, response):
        """断言聊天响应"""
        await self.assert_response_success(response)
        data = response.json()["data"]
        assert "response" in data
        assert "session_id" in data
        assert "usage" in data
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0


class DiagnosisTestCase(APITestCase):
    """诊断服务测试用例基类"""
    
    @pytest.fixture
    def mock_ai_model(self):
        """模拟AI模型"""
        model = AsyncMock()
        model.predict.return_value = {
            "diagnosis": "健康状态良好",
            "confidence": 0.95,
            "recommendations": ["保持当前生活方式", "定期复查"]
        }
        return model

    @pytest.fixture
    def sample_image_data(self) -> bytes:
        """示例图像数据"""
        # 这里应该返回实际的测试图像数据
        return b"fake_image_data"

    @pytest.fixture
    def sample_diagnosis_request(self) -> Dict[str, Any]:
        """示例诊断请求"""
        return {
            "user_id": "test-user-123",
            "diagnosis_type": "face",
            "metadata": {
                "age": 30,
                "gender": "female",
                "symptoms": ["面色苍白", "眼圈发黑"]
            }
        }

    async def assert_diagnosis_response(self, response):
        """断言诊断响应"""
        await self.assert_response_success(response)
        data = response.json()["data"]
        assert "diagnosis" in data
        assert "confidence" in data
        assert "recommendations" in data
        assert isinstance(data["confidence"], (int, float))
        assert 0 <= data["confidence"] <= 1


# 测试工具函数
def create_test_user(user_id: str = "test-user-123") -> Dict[str, Any]:
    """创建测试用户数据"""
    return {
        "id": user_id,
        "username": f"testuser_{user_id}",
        "email": f"test_{user_id}@example.com",
        "full_name": "Test User",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }


def create_test_health_data(user_id: str = "test-user-123") -> Dict[str, Any]:
    """创建测试健康数据"""
    return {
        "user_id": user_id,
        "height": 175.0,
        "weight": 70.0,
        "blood_type": "A+",
        "allergies": ["peanuts"],
        "medications": [],
        "medical_history": []
    }


def create_test_session(session_id: str = "test-session-123") -> Dict[str, Any]:
    """创建测试会话数据"""
    return {
        "id": session_id,
        "user_id": "test-user-123",
        "agent_type": "soer",
        "status": "active",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    } 