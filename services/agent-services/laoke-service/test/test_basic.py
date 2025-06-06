"""
test_basic - 索克生活项目模块
"""

from laoke_service.core.agent import AgentMessage, AgentResponse, LaoKeAgent
from laoke_service.core.config import DatabaseConfig, ServerConfig, Settings
from laoke_service.core.exceptions import LaoKeServiceError, ValidationError
import pytest

"""
基础测试模块

测试老克智能体服务的核心功能
"""





class TestConfig:
    """配置模块测试"""

    def test_database_config_creation(self):
        """测试数据库配置创建"""
        config = DatabaseConfig(
            postgres_password="test_password",
            redis_password="test_redis_password"
        )

        assert config.postgres_host == "localhost"
        assert config.postgres_port == 5432
        assert config.postgres_password == "test_password"
        assert config.redis_password == "test_redis_password"

    def test_database_config_urls(self):
        """测试数据库连接URL生成"""
        config = DatabaseConfig(
            postgres_user="testuser",
            postgres_password="testpass",
            postgres_host="testhost",
            postgres_port=5433,
            postgres_db="testdb",
            redis_host="redishost",
            redis_port=6380,
            redis_password="redispass",
            redis_db=1
        )

        expected_postgres_url = "postgresql+asyncpg://testuser:testpass@testhost:5433/testdb"
        expected_redis_url = "redis://:redispass@redishost:6380/1"

        assert config.postgres_url == expected_postgres_url
        assert config.redis_url == expected_redis_url

    def test_server_config_creation(self):
        """测试服务器配置创建"""
        config = ServerConfig(
            host="127.0.0.1",
            port=8000,
            workers=4
        )

        assert config.host == "127.0.0.1"
        assert config.port == 8000
        assert config.workers == 4

    def test_settings_creation(self):
        """测试应用设置创建"""
        settings = Settings(
            app_name="测试应用",
            environment="testing",
            debug=True
        )

        assert settings.app_name == "测试应用"
        assert settings.environment == "testing"
        assert settings.debug is True
        assert settings.is_testing() is True
        assert settings.is_production() is False


class TestExceptions:
    """异常模块测试"""

    def test_base_exception(self):
        """测试基础异常"""
        error = LaoKeServiceError(
            message="测试错误",
            error_code="TEST_ERROR",
            details={"key": "value"}
        )

        assert error.message == "测试错误"
        assert error.error_code == "TEST_ERROR"
        assert error.details == {"key": "value"}
        assert str(error) == "TEST_ERROR: 测试错误"

    def test_validation_error(self):
        """测试验证错误"""
        error = ValidationError(
            message="字段验证失败",
            field="username",
            value="invalid_user"
        )

        assert error.message == "字段验证失败"
        assert error.details["field"] == "username"
        assert error.details["value"] == "invalid_user"

    def test_exception_to_dict(self):
        """测试异常转字典"""
        error = LaoKeServiceError(
            message="测试错误",
            error_code="TEST_ERROR",
            details={"key": "value"}
        )

        error_dict = error.to_dict()
        expected = {
            "error_code": "TEST_ERROR",
            "message": "测试错误",
            "details": {"key": "value"},
            "cause": None
        }

        assert error_dict == expected


class TestAgentModels:
    """智能体模型测试"""

    def test_agent_message_creation(self):
        """测试智能体消息创建"""
        message = AgentMessage(
            content="你好，老克",
            message_type="general_chat",
            metadata={"user_id": "123"}
        )

        assert message.content == "你好，老克"
        assert message.message_type == "general_chat"
        assert message.metadata == {"user_id": "123"}
        assert message.id is not None

    def test_agent_response_creation(self):
        """测试智能体响应创建"""
        response = AgentResponse(
            success=True,
            message="你好！我是老克智能体",
            data={"response_type": "greeting"},
            suggestions=["了解中医基础", "学习计划"]
        )

        assert response.success is True
        assert response.message == "你好！我是老克智能体"
        assert response.data == {"response_type": "greeting"}
        assert response.suggestions == ["了解中医基础", "学习计划"]
        assert response.error_code is None


class TestLaoKeAgent:
    """老克智能体测试"""

    @pytest.fixture
    def mock_settings(self):
        """模拟设置"""
        settings = Settings(
            app_name="测试老克智能体",
            environment="testing",
            debug=True
        )
        settings.security.jwt_secret_key = "test_secret"
        settings.database.postgres_password = "test_password"
        return settings

    @pytest.fixture
    def agent(self, mock_settings):
        """创建智能体实例"""
        return LaoKeAgent(mock_settings)

    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """测试智能体初始化"""
        await agent.initialize()

        assert agent._knowledge_manager is not None
        assert agent._learning_planner is not None
        assert agent._community_manager is not None
        assert agent._ai_service is not None

    @pytest.mark.asyncio
    async def test_agent_status(self, agent):
        """测试智能体状态"""
        await agent.initialize()
        status = await agent.get_agent_status()

        assert status["name"] == "老克智能体"
        assert status["version"] == "1.0.0"
        assert status["status"] == "active"
        assert len(status["capabilities"]) > 0
        assert "statistics" in status

    @pytest.mark.asyncio
    async def test_general_chat_message(self, agent):
        """测试一般聊天消息"""
        await agent.initialize()

        message = AgentMessage(
            content="你好",
            message_type="general_chat"
        )

        response = await agent.process_message(message)

        assert response.success is True
        assert "老克" in response.message
        assert len(response.suggestions) > 0

    @pytest.mark.asyncio
    async def test_knowledge_query_message(self, agent):
        """测试知识查询消息"""
        await agent.initialize()

        message = AgentMessage(
            content="阴阳学说",
            message_type="knowledge_query"
        )

        response = await agent.process_message(message)

        assert response.success is True
        assert response.data is not None
        assert "knowledge_items" in response.data

    @pytest.mark.asyncio
    async def test_learning_plan_message(self, agent):
        """测试学习计划消息"""
        await agent.initialize()

        message = AgentMessage(
            content="制定中医入门学习计划",
            message_type="learning_plan",
            metadata={
                "requirements": {
                    "goal": "中医入门",
                    "level": "初级",
                    "time": "30分钟/天"
                }
            }
        )

        response = await agent.process_message(message)

        assert response.success is True
        assert response.data is not None
        assert "learning_path" in response.data

    @pytest.mark.asyncio
    async def test_community_interaction_message(self, agent):
        """测试社区互动消息"""
        await agent.initialize()

        message = AgentMessage(
            content="浏览社区内容",
            message_type="community_interaction",
            metadata={"action": "browse"}
        )

        response = await agent.process_message(message)

        assert response.success is True
        assert response.data is not None
        assert "posts" in response.data


class TestIntegration:
    """集成测试"""

    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """测试完整工作流"""
        # 创建设置
        settings = Settings(
            app_name="集成测试",
            environment="testing",
            debug=True
        )
        settings.security.jwt_secret_key = "test_secret"
        settings.database.postgres_password = "test_password"

        # 创建智能体
        agent = LaoKeAgent(settings)
        await agent.initialize()

        # 测试知识查询
        knowledge_message = AgentMessage(
            content="中医基础理论",
            message_type="knowledge_query"
        )
        knowledge_response = await agent.process_message(knowledge_message)
        assert knowledge_response.success is True

        # 测试学习计划
        learning_message = AgentMessage(
            content="制定学习计划",
            message_type="learning_plan",
            metadata={
                "requirements": {
                    "goal": "中医入门",
                    "level": "初级",
                    "time": "1小时/天"
                }
            }
        )
        learning_response = await agent.process_message(learning_message)
        assert learning_response.success is True

        # 测试社区互动
        community_message = AgentMessage(
            content="查看社区帖子",
            message_type="community_interaction",
            metadata={"action": "browse"}
        )
        community_response = await agent.process_message(community_message)
        assert community_response.success is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
