"""
test_grpc_integration - 索克生活项目模块
"""

from api.grpc.laoke_service_pb2 import (
from internal.delivery.grpc.laoke_service_impl import LaokeServiceServicer
from unittest.mock import AsyncMock, MagicMock, patch
import os
import pytest
import sys

#!/usr/bin/env python

"""
老克服务 gRPC 集成测试
"""



# 添加项目根路径到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

# 导入服务实现
    ContentModerationRequest,
    NPCInteractionRequest,
    SearchKnowledgeRequest,
    TrendingContentRequest,
    UserLearningPathRequest,
)


@pytest.fixture
def knowledge_service_mock():
    """知识服务模拟"""
    mock = MagicMock()
    mock.search_knowledge = AsyncMock()
    mock.get_related_topics = AsyncMock()
    return mock


@pytest.fixture
def community_service_mock():
    """社区服务模拟"""
    mock = MagicMock()
    mock.get_trending_posts = AsyncMock()
    mock.moderate_content = AsyncMock()
    return mock


@pytest.fixture
def agent_manager_mock():
    """智能体管理器模拟"""
    mock = MagicMock()
    mock.process_npc_interaction = AsyncMock()
    return mock


@pytest.fixture
def laoke_service(knowledge_service_mock, community_service_mock, agent_manager_mock):
    """创建老克 gRPC 服务实例"""
    service = LaokeServiceServicer()
    service.knowledge_service = knowledge_service_mock
    service.community_service = community_service_mock
    service.agent_manager = agent_manager_mock
    return service


class TestLaokeGrpcService:
    """老克 gRPC 服务集成测试"""

    @pytest.mark.asyncio
    async def test_search_knowledge(self, laoke_service, knowledge_service_mock):
        """测试知识检索 gRPC 方法"""
        # 设置模拟返回值
        knowledge_service_mock.search_knowledge.return_value = [
            {
                'id': '123',
                'title': '中医基础理论',
                'summary': '中医基础理论概述',
                'content': '中医学是中国传统医学...',
                'category': '中医基础',
                'tags': ['基础理论', '中医'],
                'relevance_score': 0.92
            },
            {
                'id': '456',
                'title': '阴阳五行学说',
                'summary': '阴阳五行基础概念',
                'content': '阴阳五行是中医基础理论...',
                'category': '中医基础',
                'tags': ['阴阳', '五行', '中医基础'],
                'relevance_score': 0.85
            }
        ]

        knowledge_service_mock.get_related_topics.return_value = [
            '中医基础理论', '阴阳平衡', '五行相生相克'
        ]

        # 创建测试请求
        request = SearchKnowledgeRequest(
            query="中医基础阴阳五行",
            categories=["中医基础"],
            tags=["基础理论"],
            limit=5,
            user_id="test_user_1"
        )

        # 调用 gRPC 方法
        with patch('time.time', return_value=1000):  # 固定时间以便测试
            response = await laoke_service.SearchKnowledge(request, None)

        # 断言
        assert len(response.items) == 2
        assert response.items[0].id == '123'
        assert response.items[0].title == '中医基础理论'
        assert response.items[0].relevance_score == 0.92
        assert response.items[1].id == '456'
        assert response.search_latency_ms > 0  # 应该记录延迟时间

        # 验证调用
        knowledge_service_mock.search_knowledge.assert_called_once_with(
            "中医基础阴阳五行",
            categories=["中医基础"],
            tags=["基础理论"],
            limit=5
        )

    @pytest.mark.asyncio
    async def test_get_user_learning_path(self, laoke_service):
        """测试获取用户学习路径 gRPC 方法"""
        # 创建模拟学习路径服务
        mock_learning_service = MagicMock()
        mock_learning_service.get_user_learning_paths = AsyncMock()
        mock_learning_service.get_user_learning_paths.return_value = {
            'paths': [
                {
                    'id': 'path_1',
                    'title': '中医基础入门',
                    'description': '适合初学者的中医基础知识课程',
                    'level': 'beginner',
                    'total_modules': 5,
                    'completed_modules': 2,
                    'progress_percentage': 0.4,
                    'modules': [
                        {'id': 'module_1', 'title': '中医概述', 'completed': True, 'order': 1},
                        {'id': 'module_2', 'title': '阴阳五行', 'completed': True, 'order': 2},
                        {'id': 'module_3', 'title': '藏象经络', 'completed': False, 'order': 3},
                        {'id': 'module_4', 'title': '病因病机', 'completed': False, 'order': 4},
                        {'id': 'module_5', 'title': '诊断方法', 'completed': False, 'order': 5}
                    ]
                }
            ],
            'completion_percentage': 0.4,
            'next_recommended_action': '继续学习"藏象经络"模块'
        }

        laoke_service.learning_service = mock_learning_service

        # 创建测试请求
        request = UserLearningPathRequest(
            user_id="test_user_1",
            path_id="path_1",
            include_progress=True
        )

        # 调用 gRPC 方法
        response = await laoke_service.GetUserLearningPath(request, None)

        # 断言
        assert len(response.paths) == 1
        assert response.paths[0].id == 'path_1'
        assert response.paths[0].title == '中医基础入门'
        assert response.paths[0].progress_percentage == 0.4
        assert response.paths[0].total_modules == 5
        assert response.paths[0].completed_modules == 2
        assert len(response.paths[0].modules) == 5
        assert response.next_recommended_action == '继续学习"藏象经络"模块'

        # 验证调用
        mock_learning_service.get_user_learning_paths.assert_called_once_with(
            user_id="test_user_1",
            path_id="path_1",
            include_progress=True
        )

    @pytest.mark.asyncio
    async def test_npc_interaction(self, laoke_service, agent_manager_mock):
        """测试NPC交互 gRPC 方法"""
        # 设置模拟返回值
        agent_manager_mock.process_npc_interaction.return_value = {
            'response_text': '欢迎来到玉米迷宫！我是老克，你今天想了解什么中医知识呢？',
            'emotion': 'friendly',
            'actions': [
                {
                    'id': 'action_1',
                    'type': 'QUEST',
                    'description': '完成中医基础知识问答挑战',
                    'requirements_met': True,
                    'rewards': ['经验值+10', '中医入门徽章']
                }
            ],
            'knowledge_hints': ['你可以询问我关于阴阳五行的知识']
        }

        # 创建测试请求
        request = NPCInteractionRequest(
            npc_id="laoke",
            user_id="test_user_1",
            message="你好，我想了解中医基础知识",
            interaction_context="first_meeting",
            location="玉米迷宫入口",
            active_quests=["learn_tcm_basics"]
        )

        # 调用 gRPC 方法
        response = await laoke_service.NPCInteraction(request, None)

        # 断言
        assert response.response_text == '欢迎来到玉米迷宫！我是老克，你今天想了解什么中医知识呢？'
        assert response.emotion == 'friendly'
        assert len(response.actions) == 1
        assert response.actions[0].id == 'action_1'
        assert response.actions[0].type == 'QUEST'
        assert len(response.knowledge_hints) == 1

        # 验证调用
        agent_manager_mock.process_npc_interaction.assert_called_once_with(
            npc_id="laoke",
            user_id="test_user_1",
            message="你好，我想了解中医基础知识",
            context="first_meeting",
            location="玉米迷宫入口",
            active_quests=["learn_tcm_basics"]
        )

    @pytest.mark.asyncio
    async def test_moderate_content(self, laoke_service, community_service_mock):
        """测试内容审核 gRPC 方法"""
        # 设置模拟返回值
        community_service_mock.moderate_content.return_value = {
            'is_approved': True,
            'violation_types': [],
            'review_comment': '内容符合社区规范',
            'moderation_level': 'auto_approved',
            'confidence_score': 0.96
        }

        # 创建测试请求
        request = ContentModerationRequest(
            content_id="post_123",
            content_type="article",
            content="这是一篇关于中医养生的文章，内容健康积极。",
            context_items=["health", "wellness"]
        )

        # 调用 gRPC 方法
        response = await laoke_service.ModerateContent(request, None)

        # 断言
        assert response.is_approved
        assert len(response.violation_types) == 0
        assert response.review_comment == '内容符合社区规范'
        assert response.moderation_level == 'auto_approved'
        assert response.confidence_score == 0.96

        # 验证调用
        community_service_mock.moderate_content.assert_called_once_with(
            content_id="post_123",
            content_type="article",
            content="这是一篇关于中医养生的文章，内容健康积极。",
            context_items=["health", "wellness"]
        )

    @pytest.mark.asyncio
    async def test_get_trending_content(self, laoke_service, community_service_mock):
        """测试获取热门内容 gRPC 方法"""
        # 设置模拟返回值
        community_service_mock.get_trending_posts.return_value = [
            {
                'id': 'post_1',
                'title': '艾灸养生方法',
                'type': 'article',
                'view_count': 520,
                'like_count': 120,
                'comment_count': 45,
                'trending_score': 0.95,
                'author_id': 'user_1',
                'created_at': '2023-11-10T08:30:00Z'
            },
            {
                'id': 'post_2',
                'title': '冬季养生食谱分享',
                'type': 'article',
                'view_count': 480,
                'like_count': 95,
                'comment_count': 32,
                'trending_score': 0.89,
                'author_id': 'user_2',
                'created_at': '2023-11-11T10:15:00Z'
            }
        ]

        # 创建测试请求
        request = TrendingContentRequest(
            content_type="articles",
            time_window_hours=24,
            limit=5,
            category="四季养生"
        )

        # 调用 gRPC 方法
        response = await laoke_service.GetTrendingContent(request, None)

        # 断言
        assert len(response.items) == 2
        assert response.items[0].id == 'post_1'
        assert response.items[0].title == '艾灸养生方法'
        assert response.items[0].view_count == 520
        assert response.items[0].trending_score == 0.95
        assert response.items[1].id == 'post_2'
        assert response.trending_algorithm_version is not None

        # 验证调用
        community_service_mock.get_trending_posts.assert_called_once_with(
            content_type="articles",
            time_window_hours=24,
            limit=5,
            category="四季养生"
        )
