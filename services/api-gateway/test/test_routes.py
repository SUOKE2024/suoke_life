#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API网关路由测试
主要测试路由处理中的错误情况和边缘案例
"""

import asyncio
import json
import os
import sys
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient
from httpx import AsyncClient, HTTPError, NetworkError, ReadTimeout, ConnectError

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from internal.delivery.rest.routes import setup_routes
from internal.model.config import GatewayConfig, RouteConfig

@pytest.fixture
def gateway_config():
    """创建网关配置"""
    return GatewayConfig(
        routes=[
            RouteConfig(
                name="user-service",
                prefix="/api/users",
                service="user-service",
                methods=["GET", "POST"],
                auth_required=True,
                rewrite_path="^/api/users(.*)$ => /users$1",
                timeout=3
            ),
            RouteConfig(
                name="slow-service",
                prefix="/api/slow",
                service="slow-service",
                methods=["GET"],
                auth_required=False,
                rewrite_path="^/api/slow(.*)$ => /slow$1",
                timeout=0.5  # 设置较短的超时
            ),
            RouteConfig(
                name="error-service",
                prefix="/api/error",
                service="error-service",
                methods=["GET"],
                auth_required=False,
                rewrite_path="^/api/error(.*)$ => /error$1"
            ),
            RouteConfig(
                name="binary-service",
                prefix="/api/binary",
                service="binary-service",
                methods=["GET"],
                auth_required=False,
                rewrite_path="^/api/binary(.*)$ => /binary$1"
            ),
            RouteConfig(
                name="retry-service",
                prefix="/api/retry",
                service="retry-service",
                methods=["GET"],
                auth_required=False,
                rewrite_path="^/api/retry(.*)$ => /retry$1",
                retries=3,
                retry_delay=0.1
            )
        ]
    )

@pytest.fixture
def mock_service_registry():
    """创建模拟服务注册表"""
    registry = MagicMock()
    registry.get_endpoint.return_value = ("localhost", 8000)
    return registry

@pytest.fixture
def gateway_app(gateway_config, mock_service_registry):
    """创建网关应用"""
    app = FastAPI()
    
    # 设置路由
    setup_routes(app, gateway_config)
    
    # 添加注册表到应用状态
    app.state.registry = mock_service_registry
    
    return app

@pytest.fixture
def gateway_client(gateway_app):
    """创建网关客户端"""
    return TestClient(gateway_app)

@pytest.mark.asyncio
class TestRoutesErrorHandling:
    """测试路由错误处理"""
    
    @patch("httpx.AsyncClient.request")
    async def test_timeout_handling(self, mock_request, gateway_client):
        """测试超时处理"""
        # 模拟超时
        mock_request.side_effect = ReadTimeout("Connection timed out")
        
        # 测试超时请求
        response = gateway_client.get("/api/slow/test")
        
        # 应该返回503错误
        assert response.status_code == 503
        assert "detail" in response.json()
        assert "timeout" in response.json()["detail"].lower()
    
    @patch("httpx.AsyncClient.request")
    async def test_network_error_handling(self, mock_request, gateway_client):
        """测试网络错误处理"""
        # 测试各种网络错误
        error_types = [
            NetworkError("Connection refused"),
            ConnectError("Failed to establish a connection"),
            HTTPError("HTTP Error")
        ]
        
        for error in error_types:
            mock_request.side_effect = error
            
            # 测试错误请求
            response = gateway_client.get("/api/error/network")
            
            # 应该返回503错误
            assert response.status_code == 503
            assert "detail" in response.json()
    
    @patch("httpx.AsyncClient.request")
    async def test_invalid_response_handling(self, mock_request, gateway_client):
        """测试无效响应处理"""
        class MockResponse:
            """模拟无效响应"""
            status_code = 200
            headers = {"content-type": "application/json"}
            
            @property
            def content(self):
                """返回损坏的JSON"""
                return b'{invalid-json'
            
            def raise_for_status(self):
                """不抛出异常"""
                pass
        
        # 模拟返回损坏的JSON
        mock_request.return_value = MockResponse()
        
        # 测试请求
        response = gateway_client.get("/api/error/invalid-json")
        
        # 应该返回502错误 (Bad Gateway)
        assert response.status_code == 502
        assert "detail" in response.json()
    
    @patch("httpx.AsyncClient.request")
    async def test_retry_mechanism(self, mock_request, gateway_client):
        """测试重试机制"""
        # 前两次调用抛出异常，第三次成功
        side_effects = [
            NetworkError("Connection refused"),
            NetworkError("Connection refused"),
            MagicMock(
                status_code=200,
                headers={"content-type": "application/json"},
                content=b'{"success": true}',
                raise_for_status=lambda: None
            )
        ]
        
        mock_request.side_effect = side_effects
        
        # 测试请求
        response = gateway_client.get("/api/retry/test")
        
        # 验证调用次数和最终响应
        assert mock_request.call_count == 3
        assert response.status_code == 200
        assert response.json()["success"] is True
    
    @patch("httpx.AsyncClient.request")
    async def test_binary_content_handling(self, mock_request, gateway_client):
        """测试二进制内容处理"""
        # 创建二进制数据
        binary_data = bytes([0, 1, 2, 3, 4, 255, 254, 253])
        
        # 模拟返回二进制数据
        mock_response = MagicMock(
            status_code=200,
            headers={"content-type": "application/octet-stream"},
            content=binary_data,
            raise_for_status=lambda: None
        )
        mock_request.return_value = mock_response
        
        # 测试请求
        response = gateway_client.get("/api/binary/data")
        
        # 验证响应
        assert response.status_code == 200
        assert response.content == binary_data
        assert response.headers["content-type"] == "application/octet-stream"
    
    @patch("httpx.AsyncClient.request")
    async def test_large_response_handling(self, mock_request, gateway_client):
        """测试大响应处理"""
        # 创建大型数据 (1MB)
        large_data = json.dumps({"data": "X" * 1024 * 1024}).encode()
        
        # 模拟返回大数据
        mock_response = MagicMock(
            status_code=200,
            headers={"content-type": "application/json"},
            content=large_data,
            raise_for_status=lambda: None
        )
        mock_request.return_value = mock_response
        
        # 测试请求
        response = gateway_client.get("/api/users/large")
        
        # 验证响应
        assert response.status_code == 200
        assert len(response.content) > 1000000  # 确保大数据被正确传输
        
    @patch("httpx.AsyncClient.request")
    async def test_error_response_passthrough(self, mock_request, gateway_client):
        """测试错误响应传递"""
        # 创建各种HTTP错误状态
        for status_code in [400, 401, 403, 404, 500]:
            # 模拟错误响应
            error_content = json.dumps({"error": f"Error {status_code}"}).encode()
            mock_response = MagicMock(
                status_code=status_code,
                headers={"content-type": "application/json"},
                content=error_content,
                raise_for_status=lambda: None
            )
            mock_request.return_value = mock_response
            
            # 测试请求
            response = gateway_client.get(f"/api/error/{status_code}")
            
            # 验证错误状态和内容被正确传递
            assert response.status_code == status_code
            assert response.json()["error"] == f"Error {status_code}"
    
    @patch("httpx.AsyncClient.request")
    async def test_custom_headers_handling(self, mock_request, gateway_client):
        """测试自定义头部处理"""
        # 模拟响应添加自定义头部
        mock_response = MagicMock(
            status_code=200,
            headers={
                "content-type": "application/json",
                "x-custom-header": "test-value",
                "x-rate-limit": "100",
                "set-cookie": "session=123; Path=/; HttpOnly"
            },
            content=b'{"success": true}',
            raise_for_status=lambda: None
        )
        mock_request.return_value = mock_response
        
        # 测试请求
        response = gateway_client.get("/api/users/headers")
        
        # 验证自定义头部
        assert response.status_code == 200
        assert response.headers["x-custom-header"] == "test-value"
        assert response.headers["x-rate-limit"] == "100"
        assert "session=123" in response.headers["set-cookie"]
    
    @patch("httpx.AsyncClient.request")
    async def test_concurrent_requests(self, mock_request, gateway_client):
        """测试并发请求处理"""
        # 模拟响应有不同的延迟
        async def mock_delayed_response(method, url, **kwargs):
            # 从URL中提取延迟时间（毫秒）
            delay = int(url.split("/")[-1]) / 1000
            await asyncio.sleep(delay)
            
            return MagicMock(
                status_code=200,
                headers={"content-type": "application/json"},
                content=json.dumps({"delay": delay, "success": True}).encode(),
                raise_for_status=lambda: None
            )
        
        mock_request.side_effect = mock_delayed_response
        
        # 创建异步测试客户端
        async with AsyncClient(app=gateway_client.app, base_url="http://testserver") as client:
            # 并发发送3个请求，延迟分别为100ms, 50ms, 200ms
            tasks = [
                client.get("/api/users/100"),
                client.get("/api/users/50"),
                client.get("/api/users/200")
            ]
            
            # 等待所有请求完成
            responses = await asyncio.gather(*tasks)
            
            # 验证响应顺序不影响结果正确性
            assert all(r.status_code == 200 for r in responses)
            delays = [r.json()["delay"] for r in responses]
            assert 0.05 in delays
            assert 0.1 in delays
            assert 0.2 in delays

if __name__ == "__main__":
    pytest.main(["-v", __file__])