#!/usr/bin/env python3
"""
REST API 单元测试
REST API Unit Tests
"""

import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest
from flask import Flask

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from internal.delivery.rest_api import create_rest_api
from internal.model.agent import AgentInfo, AgentMetrics, AgentStatus
from internal.service.agent_manager import AgentManager


class TestRestAPI:
    """REST API 测试类"""

    @pytest.fixture
    def config(self):
        """测试配置"""
        return {
            "agents": {
                "xiaoai": {
                    "name": "小艾智能体",
                    "url": "http://localhost:5001",
                    "timeout": 30,
                    "retry_count": 3,
                    "health_check_interval": 60,
                    "capabilities": ["diagnosis", "consultation"],
                }
            }
        }

    @pytest.fixture
    def agent_manager(self, config):
        """创建智能体管理器实例"""
        return AgentManager(config)

    @pytest.fixture
    def app(self, agent_manager):
        """创建 Flask 应用"""
        app = Flask(__name__)
        app.config["TESTING"] = True
        create_rest_api(app, agent_manager)
        return app

    @pytest.fixture
    def client(self, app):
        """创建测试客户端"""
        return app.test_client()

    def test_health_check(self, client):
        """测试健康检查接口"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data["status"] == "healthy"
        assert data["service"] == "a2a-agent-network"
        assert "timestamp" in data

    def test_get_agents(self, client, agent_manager):
        """测试获取智能体列表"""
        # 模拟智能体数据
        agent_info = AgentInfo(
            id="xiaoai",
            name="小艾智能体",
            description="健康咨询智能体",
            version="1.0.0",
            url="http://localhost:5001",
            status=AgentStatus.ONLINE,
            last_heartbeat="2024-01-15T10:30:00Z",
        )
        
        with patch.object(agent_manager, "get_all_agents", return_value=[agent_info]):
            response = client.get("/api/v1/agents")
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data["success"] is True
            assert data["total"] == 1
            assert len(data["data"]) == 1
            assert data["data"][0]["id"] == "xiaoai"

    def test_get_agent_by_id(self, client, agent_manager):
        """测试获取指定智能体"""
        agent_info = AgentInfo(
            id="xiaoai",
            name="小艾智能体",
            description="健康咨询智能体",
            version="1.0.0",
            url="http://localhost:5001",
            status=AgentStatus.ONLINE,
            last_heartbeat="2024-01-15T10:30:00Z",
        )
        
        with patch.object(agent_manager, "get_agent_info", return_value=agent_info):
            response = client.get("/api/v1/agents/xiaoai")
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data["success"] is True
            assert data["data"]["id"] == "xiaoai"
            assert data["data"]["name"] == "小艾智能体"

    def test_get_agent_not_found(self, client, agent_manager):
        """测试获取不存在的智能体"""
        with patch.object(agent_manager, "get_agent_info", return_value=None):
            response = client.get("/api/v1/agents/nonexistent")
            assert response.status_code == 404
            
            data = json.loads(response.data)
            assert data["success"] is False
            assert "不存在" in data["error"]

    def test_get_agent_metrics(self, client, agent_manager):
        """测试获取智能体指标"""
        metrics = AgentMetrics(
            agent_id="xiaoai",
            request_count=100,
            success_count=95,
            error_count=5,
            avg_response_time=1.5,
            last_request_time="2024-01-15T10:30:00Z",
            uptime=3600.0,
        )
        
        with patch.object(agent_manager, "get_agent_metrics", return_value=metrics):
            response = client.get("/api/v1/agents/xiaoai/metrics")
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data["success"] is True
            assert data["data"]["agent_id"] == "xiaoai"
            assert data["data"]["request_count"] == 100
            assert data["data"]["success_count"] == 95

    def test_execute_agent_action(self, client, agent_manager):
        """测试执行智能体动作"""
        from internal.model.agent import AgentResponse
        
        mock_response = AgentResponse(
            success=True,
            data={"diagnosis": "感冒", "confidence": 0.85},
            error=None,
            agent_id="xiaoai",
            request_id="req123",
            execution_time=1.2,
            timestamp="2024-01-15T10:30:00Z",
        )
        
        with patch.object(agent_manager, "send_request", return_value=mock_response):
            response = client.post(
                "/api/v1/agents/xiaoai/execute",
                json={
                    "action": "diagnose",
                    "parameters": {"symptoms": "头痛、发热"},
                    "user_id": "user123",
                    "request_id": "req123",
                    "timeout": 30,
                },
                content_type="application/json",
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["success"] is True
            assert data["data"]["diagnosis"] == "感冒"
            assert data["execution_time"] == 1.2

    def test_execute_agent_action_missing_fields(self, client):
        """测试执行智能体动作缺少必需字段"""
        response = client.post(
            "/api/v1/agents/xiaoai/execute",
            json={"action": "diagnose"},  # 缺少 user_id
            content_type="application/json",
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["success"] is False
        assert "缺少必需字段" in data["error"]

    def test_register_agent(self, client, agent_manager):
        """测试注册智能体"""
        with patch.object(agent_manager, "register_agent", return_value=True):
            response = client.post(
                "/api/v1/agents/register",
                json={
                    "id": "new_agent",
                    "name": "新智能体",
                    "url": "http://localhost:5005",
                    "description": "测试智能体",
                    "version": "1.0.0",
                    "capabilities": [
                        {
                            "name": "test_capability",
                            "description": "测试能力",
                            "enabled": True,
                            "parameters": {},
                        }
                    ],
                },
                content_type="application/json",
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["success"] is True
            assert data["agent_id"] == "new_agent"

    def test_deregister_agent(self, client, agent_manager):
        """测试注销智能体"""
        with patch.object(agent_manager, "deregister_agent", return_value=True):
            response = client.delete("/api/v1/agents/xiaoai/deregister")
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["success"] is True

    def test_get_network_status(self, client, agent_manager):
        """测试获取网络状态"""
        network_status = {
            "total_agents": 4,
            "online_agents": 3,
            "offline_agents": 1,
            "network_health": 0.75,
            "agents": {
                "xiaoai": "online",
                "xiaoke": "online",
                "laoke": "online",
                "soer": "offline",
            },
        }
        
        with patch.object(agent_manager, "get_network_status", return_value=network_status):
            response = client.get("/api/v1/network/status")
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data["success"] is True
            assert data["data"]["total_agents"] == 4
            assert data["data"]["network_health"] == 0.75

    def test_get_all_metrics(self, client, agent_manager):
        """测试获取所有指标"""
        metrics_list = [
            AgentMetrics(
                agent_id="xiaoai",
                request_count=100,
                success_count=95,
                error_count=5,
                avg_response_time=1.5,
                last_request_time="2024-01-15T10:30:00Z",
                uptime=3600.0,
            )
        ]
        
        with patch.object(agent_manager, "get_all_metrics", return_value=metrics_list):
            response = client.get("/api/v1/metrics")
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data["success"] is True
            assert len(data["data"]) == 1
            assert data["data"][0]["agent_id"] == "xiaoai"

    def test_error_handling(self, client, agent_manager):
        """测试错误处理"""
        with patch.object(agent_manager, "get_all_agents", side_effect=Exception("测试异常")):
            response = client.get("/api/v1/agents")
            assert response.status_code == 500
            
            data = json.loads(response.data)
            assert data["success"] is False
            assert "测试异常" in data["error"]

    def test_404_handler(self, client):
        """测试 404 错误处理"""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert data["success"] is False
        assert "接口不存在" in data["error"] 