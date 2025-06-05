#!/usr/bin/env python3

def fix_agent_manager_tests():
    """修复agent_manager测试中的mock问题"""
    file_path = "test/unit/test_agent_manager.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复test_start_and_stop
    content = content.replace(
        '''    @pytest.mark.asyncio
    async def test_start_and_stop(self, agent_manager):
        """测试启动和停止"""
        with patch("aiohttp.ClientSession") as mock_session:
            mock_session.return_value.__aenter__.return_value = Mock()
            mock_session.return_value.__aexit__.return_value = AsyncMock()

            await agent_manager.start()
            assert agent_manager.session is not None
            assert len(agent_manager._health_check_tasks) == 2

            await agent_manager.stop()
            assert agent_manager.session is None''',
        '''    @pytest.mark.asyncio
    async def test_start_and_stop(self, agent_manager):
        """测试启动和停止"""
        with patch("aiohttp.ClientSession") as mock_session:
            # 创建一个mock session对象
            mock_session_instance = AsyncMock()
            mock_session_instance.close = AsyncMock()
            mock_session.return_value = mock_session_instance

            await agent_manager.start()
            assert agent_manager.session is not None
            assert len(agent_manager._health_check_tasks) == 2

            await agent_manager.stop()
            assert agent_manager.session is None'''
    )
    
    # 修复test_health_check_success
    content = content.replace(
        '''            # 模拟成功的健康检查响应
            mock_response = Mock()
            mock_response.status = 200
            mock_response.__aenter__.return_value = mock_response
            mock_response.__aexit__.return_value = AsyncMock()

            mock_session.return_value.get.return_value = mock_response
            agent_manager.session = mock_session.return_value''',
        '''            # 模拟成功的健康检查响应
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)

            mock_session_instance = AsyncMock()
            mock_session_instance.get.return_value = mock_response
            mock_session.return_value = mock_session_instance
            agent_manager.session = mock_session_instance'''
    )
    
    # 修复test_send_request_success
    content = content.replace(
        '''            # 模拟成功的请求响应
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"result": "success"})
            mock_response.__aenter__.return_value = mock_response
            mock_response.__aexit__.return_value = AsyncMock()

            mock_session.return_value.post.return_value = mock_response
            agent_manager.session = mock_session.return_value''',
        '''            # 模拟成功的请求响应
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"result": "success"})
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)

            mock_session_instance = AsyncMock()
            mock_session_instance.post.return_value = mock_response
            mock_session.return_value = mock_session_instance
            agent_manager.session = mock_session_instance'''
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("修复完成")

if __name__ == "__main__":
    fix_agent_manager_tests() 