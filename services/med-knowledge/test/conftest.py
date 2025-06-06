"""
conftest - 索克生活项目模块
"""

            from app.main import app
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
import os
import pytest


# 设置测试环境变量
os.environ["ENVIRONMENT"] = "test"
os.environ["LOG_LEVEL"] = "INFO"
os.environ["LOG_OUTPUT"] = "console"
os.environ["LOG_FORMAT"] = "text"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"
os.environ["GRPC_PORT"] = "50051"
os.environ["HTTP_PORT"] = "8000"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["JWT_ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
# 禁用安全配置以简化测试
os.environ["SECURITY_ENABLED"] = "false"


@pytest.fixture
def client():
    """创建测试客户端"""
    # 模拟容器和服务
    mock_container = Mock()
    mock_container.cache_service = Mock()
    mock_container.knowledge_service = Mock()
    mock_container.metrics_service = Mock()
    
    # 模拟异步方法
    mock_container.initialize = AsyncMock()
    mock_container.cleanup = AsyncMock()
    
    # 模拟知识服务返回数据
    mock_container.knowledge_service.get_constitutions.return_value = {
        "data": [],
        "total": 0,
        "limit": 10,
        "offset": 0
    }
    
    with patch("app.core.container.get_container", return_value=mock_container):
        with patch("app.core.container.lifespan_context") as mock_lifespan:
            # 模拟生命周期上下文管理器
            mock_lifespan.return_value.__aenter__ = AsyncMock(return_value=mock_container)
            mock_lifespan.return_value.__aexit__ = AsyncMock(return_value=None)
            
            
            # 替换应用的生命周期处理器为空函数
            async def empty_lifespan(app):
                yield
            
            app.router.lifespan_context = empty_lifespan
            
            with TestClient(app) as test_client:
                yield test_client


@pytest.fixture(autouse=True)
def setup_test_environment():
    """自动设置测试环境"""
    # 确保测试环境变量已设置
    yield
    # 清理（如果需要）
    pass 