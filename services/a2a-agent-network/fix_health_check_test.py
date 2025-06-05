#!/usr/bin/env python3

from unittest.mock import patch

def fix_health_check_test():
    """修复健康检查测试"""
    file_path = "test/unit/test_agent_manager.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复health_check_success测试
    old_test = '''    @pytest.mark.asyncio
    async def test_health_check_success(self, agent_manager):
        """测试健康检查成功"""
        # 创建一个正确的async context manager mock
        mock_response = AsyncMock()
        mock_response.status = 200
        
        # 创建一个async context manager
        async def mock_get(*args, **kwargs):
            return mock_response
        
        mock_session = AsyncMock()
        mock_session.get = mock_get
        agent_manager.session = mock_session

        health_check = await agent_manager._perform_health_check("xiaoai")

        assert health_check.agent_id == "xiaoai"
        assert health_check.status == AgentStatus.ONLINE
        assert agent_manager.agents["xiaoai"].status == AgentStatus.ONLINE'''

    new_test = '''    @pytest.mark.asyncio
    async def test_health_check_success(self, agent_manager):
        """测试健康检查成功"""
        with patch("aiohttp.ClientSession.get") as mock_get:
            # 模拟成功的健康检查响应
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            
            mock_get.return_value = mock_response
            
            # 创建session
            agent_manager.session = AsyncMock()

            health_check = await agent_manager._perform_health_check("xiaoai")

            assert health_check.agent_id == "xiaoai"
            assert health_check.status == AgentStatus.ONLINE
            assert agent_manager.agents["xiaoai"].status == AgentStatus.ONLINE'''

    content = content.replace(old_test, new_test)
    
    # 修复send_request_success测试
    old_send_test = '''    @pytest.mark.asyncio
    async def test_send_request_success(self, agent_manager):
        """测试发送请求成功"""
        # 设置智能体为在线状态
        agent_manager.agents["xiaoai"].status = AgentStatus.ONLINE

        # 创建一个正确的async context manager mock
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"result": "success"})
        
        # 创建一个async context manager
        async def mock_post(*args, **kwargs):
            return mock_response
        
        mock_session = AsyncMock()
        mock_session.post = mock_post
        agent_manager.session = mock_session

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
        assert response.request_id == "req123"'''

    new_send_test = '''    @pytest.mark.asyncio
    async def test_send_request_success(self, agent_manager):
        """测试发送请求成功"""
        # 设置智能体为在线状态
        agent_manager.agents["xiaoai"].status = AgentStatus.ONLINE

        with patch("aiohttp.ClientSession.post") as mock_post:
            # 模拟成功的请求响应
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"result": "success"})
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            
            mock_post.return_value = mock_response
            
            # 创建session
            agent_manager.session = AsyncMock()

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
            assert response.request_id == "req123"'''

    content = content.replace(old_send_test, new_send_test)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("修复完成")

if __name__ == "__main__":
    fix_health_check_test() 