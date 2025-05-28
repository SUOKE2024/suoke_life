#!/usr/bin/env python3
"""
智能体管理器单元测试
Agent Manager Unit Tests
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from internal.model.agent import AgentRequest, AgentStatus
from internal.service.agent_manager import AgentManager


class TestAgentManager:
    """智能体管理器测试类"""

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
                },
                "xiaoke": {
                    "name": "小克智能体",
                    "url": "http://localhost:5002",
                    "timeout": 30,
                    "retry_count": 3,
                    "health_check_interval": 60,
                    "capabilities": ["resource_management", "customization"],
                },
            }
        }

    @pytest.fixture
    def agent_manager(self, config):
        """创建智能体管理器实例"""
        return AgentManager(config)

    def test_init(self, agent_manager):
        """测试初始化"""
        assert len(agent_manager.agents) == 2
        assert "xiaoai" in agent_manager.agents
        assert "xiaoke" in agent_manager.agents
        assert len(agent_manager.agent_configs) == 2
        assert len(agent_manager.agent_metrics) == 2

    def test_load_agent_configs(self, agent_manager):
        """测试加载智能体配置"""
        xiaoai_config = agent_manager.agent_configs["xiaoai"]
        assert xiaoai_config.name == "小艾智能体"
        assert xiaoai_config.url == "http://localhost:5001"
        assert xiaoai_config.timeout == 30
        assert "diagnosis" in xiaoai_config.capabilities

    @pytest.mark.asyncio
    async def test_start_and_stop(self, agent_manager):
        """测试启动和停止"""
        with patch("aiohttp.ClientSession") as mock_session:
            mock_session.return_value.__aenter__.return_value = Mock()
            mock_session.return_value.__aexit__.return_value = AsyncMock()

            await agent_manager.start()
            assert agent_manager.session is not None
            assert len(agent_manager._health_check_tasks) == 2

            await agent_manager.stop()
            assert agent_manager.session is None

    @pytest.mark.asyncio
    async def test_health_check_success(self, agent_manager):
        """测试健康检查成功"""
        with patch("aiohttp.ClientSession") as mock_session:
            # 模拟成功的健康检查响应
            mock_response = Mock()
            mock_response.status = 200
            mock_response.__aenter__.return_value = mock_response
            mock_response.__aexit__.return_value = AsyncMock()

            mock_session.return_value.get.return_value = mock_response
            agent_manager.session = mock_session.return_value

            health_check = await agent_manager._perform_health_check("xiaoai")

            assert health_check.agent_id == "xiaoai"
            assert health_check.status == AgentStatus.ONLINE
            assert agent_manager.agents["xiaoai"].status == AgentStatus.ONLINE

    @pytest.mark.asyncio
    async def test_health_check_failure(self, agent_manager):
        """测试健康检查失败"""
        with patch("aiohttp.ClientSession") as mock_session:
            # 模拟失败的健康检查响应
            mock_session.return_value.get.side_effect = Exception("Connection failed")
            agent_manager.session = mock_session.return_value

            health_check = await agent_manager._perform_health_check("xiaoai")

            assert health_check.agent_id == "xiaoai"
            assert health_check.status == AgentStatus.OFFLINE
            assert health_check.error_message == "Connection failed"
            assert agent_manager.agents["xiaoai"].status == AgentStatus.OFFLINE

    @pytest.mark.asyncio
    async def test_send_request_success(self, agent_manager):
        """测试发送请求成功"""
        with patch("aiohttp.ClientSession") as mock_session:
            # 设置智能体为在线状态
            agent_manager.agents["xiaoai"].status = AgentStatus.ONLINE

            # 模拟成功的请求响应
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"result": "success"})
            mock_response.__aenter__.return_value = mock_response
            mock_response.__aexit__.return_value = AsyncMock()

            mock_session.return_value.post.return_value = mock_response
            agent_manager.session = mock_session.return_value

            request = AgentRequest(
                agent_id="xiaoai",
                action="diagnose",
                parameters={"symptoms": "headache"},
                user_id="user123",
                request_id="req123",
            )

            response = await agent_manager.send_request(request)

            assert response.success is True
            assert response.data == {"result": "success"}
            assert response.agent_id == "xiaoai"
            assert response.request_id == "req123"

    @pytest.mark.asyncio
    async def test_send_request_agent_offline(self, agent_manager):
        """测试发送请求到离线智能体"""
        # 设置智能体为离线状态
        agent_manager.agents["xiaoai"].status = AgentStatus.OFFLINE

        request = AgentRequest(
            agent_id="xiaoai",
            action="diagnose",
            parameters={"symptoms": "headache"},
            user_id="user123",
            request_id="req123",
        )

        response = await agent_manager.send_request(request)

        assert response.success is False
        assert "不在线" in response.error
        assert response.agent_id == "xiaoai"

    @pytest.mark.asyncio
    async def test_send_request_agent_not_exist(self, agent_manager):
        """测试发送请求到不存在的智能体"""
        request = AgentRequest(
            agent_id="nonexistent",
            action="diagnose",
            parameters={"symptoms": "headache"},
            user_id="user123",
            request_id="req123",
        )

        response = await agent_manager.send_request(request)

        assert response.success is False
        assert "不存在" in response.error
        assert response.agent_id == "nonexistent"

    def test_get_agent_info(self, agent_manager):
        """测试获取智能体信息"""
        agent_info = agent_manager.get_agent_info("xiaoai")
        assert agent_info is not None
        assert agent_info.id == "xiaoai"
        assert agent_info.name == "小艾智能体"

        # 测试不存在的智能体
        agent_info = agent_manager.get_agent_info("nonexistent")
        assert agent_info is None

    def test_get_all_agents(self, agent_manager):
        """测试获取所有智能体"""
        agents = agent_manager.get_all_agents()
        assert len(agents) == 2
        agent_ids = [agent.id for agent in agents]
        assert "xiaoai" in agent_ids
        assert "xiaoke" in agent_ids

    def test_get_agent_metrics(self, agent_manager):
        """测试获取智能体指标"""
        metrics = agent_manager.get_agent_metrics("xiaoai")
        assert metrics is not None
        assert metrics.agent_id == "xiaoai"
        assert metrics.request_count == 0
        assert metrics.success_count == 0
        assert metrics.error_count == 0

    def test_update_metrics(self, agent_manager):
        """测试更新指标"""
        # 模拟成功请求
        agent_manager._update_metrics("xiaoai", True, 1.5)
        metrics = agent_manager.agent_metrics["xiaoai"]
        assert metrics.request_count == 1
        assert metrics.success_count == 1
        assert metrics.error_count == 0
        assert metrics.avg_response_time == 1.5

        # 模拟失败请求
        agent_manager._update_metrics("xiaoai", False, 2.0)
        metrics = agent_manager.agent_metrics["xiaoai"]
        assert metrics.request_count == 2
        assert metrics.success_count == 1
        assert metrics.error_count == 1
        assert metrics.avg_response_time == 1.75  # (1.5 + 2.0) / 2

    def test_get_network_status(self, agent_manager):
        """测试获取网络状态"""
        # 设置一个智能体为在线
        agent_manager.agents["xiaoai"].status = AgentStatus.ONLINE
        agent_manager.agents["xiaoke"].status = AgentStatus.OFFLINE

        status = agent_manager.get_network_status()
        assert status["total_agents"] == 2
        assert status["online_agents"] == 1
        assert status["offline_agents"] == 1
        assert status["network_health"] == 0.5
        assert status["agents"]["xiaoai"] == "online"
        assert status["agents"]["xiaoke"] == "offline"


if __name__ == "__main__":
    pytest.main([__file__])
