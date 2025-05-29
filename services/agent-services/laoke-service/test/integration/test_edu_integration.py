#!/usr/bin/env python

"""
教育服务集成测试
"""

import json
import os
import sys
from unittest.mock import AsyncMock, patch

import pytest

# 添加项目根路径到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from internal.integration.edu.edu_service import EducationService


@pytest.fixture
def mock_cache_client():
    """模拟缓存客户端"""
    mock = AsyncMock()
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def edu_service(mock_cache_client):
    """教育服务实例"""
    service = EducationService(cache_client=mock_cache_client)
    # 重写API URL供测试使用
    service.edu_api_url = "https://mock-edu-api.suokelife.com"
    service.edu_api_key = "test-api-key"
    return service


@pytest.mark.asyncio
async def test_get_course_recommendations(edu_service):
    """测试获取课程推荐"""
    # 模拟响应数据
    mock_response = {
        "courses": [
            {
                "id": "course-001",
                "title": "中医基础理论导论",
                "description": "了解中医的基本理论和核心概念",
                "difficulty": "beginner",
                "duration": 3600,
                "rating": 4.8,
                "completion_rate": 85
            },
            {
                "id": "course-002",
                "title": "针灸入门实践",
                "description": "学习针灸的基本技巧和应用",
                "difficulty": "intermediate",
                "duration": 7200,
                "rating": 4.6,
                "completion_rate": 72
            }
        ]
    }

    # 模拟 API 请求
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value = AsyncMock()
        mock_get.return_value.raise_for_status = AsyncMock()
        mock_get.return_value.json = AsyncMock(return_value=mock_response)

        # 调用服务方法
        user_id = "user-123"
        interests = ["tcm", "acupuncture", "herbal-medicine"]
        result = await edu_service.get_course_recommendations(user_id, interests)

        # 验证结果
        assert result == mock_response["courses"]

        # 验证 API 调用
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs["headers"]["Authorization"] == "Bearer test-api-key"
        assert "user_id=user-123" in str(kwargs["params"])

        # 验证缓存调用
        edu_service.cache_client.get.assert_called_once()
        edu_service.cache_client.set.assert_called_once()


@pytest.mark.asyncio
async def test_generate_learning_path(edu_service):
    """测试生成学习路径"""
    # 模拟响应数据
    mock_response = {
        "path_id": "path-001",
        "modules": [
            {
                "id": "module-001",
                "title": "中医基础概念",
                "courses": ["course-001", "course-003"],
                "duration": 10800
            },
            {
                "id": "module-002",
                "title": "望闻问切基本技能",
                "courses": ["course-005", "course-007"],
                "duration": 14400
            }
        ],
        "estimated_duration": 25200,
        "difficulty": "beginner"
    }

    # 模拟 API 请求
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value = AsyncMock()
        mock_post.return_value.raise_for_status = AsyncMock()
        mock_post.return_value.json = AsyncMock(return_value=mock_response)

        # 调用服务方法
        user_id = "user-123"
        goal = "掌握中医四诊基本技能"
        result = await edu_service.generate_learning_path(user_id, goal)

        # 验证结果
        assert result == mock_response
        assert result["path_id"] == "path-001"
        assert len(result["modules"]) == 2

        # 验证 API 调用
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs["headers"]["Authorization"] == "Bearer test-api-key"
        assert kwargs["json"]["user_id"] == "user-123"
        assert kwargs["json"]["goal"] == "掌握中医四诊基本技能"

        # 验证缓存调用
        edu_service.cache_client.get.assert_called_once()
        edu_service.cache_client.set.assert_called_once()


@pytest.mark.asyncio
async def test_get_course_details(edu_service):
    """测试获取课程详情"""
    # 模拟响应数据
    mock_response = {
        "id": "course-001",
        "title": "中医基础理论导论",
        "description": "了解中医的基本理论和核心概念",
        "difficulty": "beginner",
        "duration": 3600,
        "modules": [
            {
                "id": "module-001",
                "title": "阴阳五行理论",
                "content_type": "video",
                "duration": 1200
            },
            {
                "id": "module-002",
                "title": "脏腑经络学说",
                "content_type": "reading",
                "duration": 1800
            }
        ],
        "instructor": "王大夫",
        "rating": 4.8,
        "reviews_count": 123,
        "prerequisites": []
    }

    # 模拟 API 请求
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value = AsyncMock()
        mock_get.return_value.raise_for_status = AsyncMock()
        mock_get.return_value.json = AsyncMock(return_value=mock_response)

        # 调用服务方法
        course_id = "course-001"
        result = await edu_service.get_course_details(course_id)

        # 验证结果
        assert result == mock_response
        assert result["id"] == "course-001"
        assert result["title"] == "中医基础理论导论"
        assert len(result["modules"]) == 2

        # 验证 API 调用
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs["headers"]["Authorization"] == "Bearer test-api-key"
        assert f"/v1/courses/{course_id}" in str(args)

        # 验证缓存调用
        edu_service.cache_client.get.assert_called_once()
        edu_service.cache_client.set.assert_called_once()


@pytest.mark.asyncio
async def test_search_courses(edu_service):
    """测试搜索课程"""
    # 模拟响应数据
    mock_response = {
        "results": [
            {
                "id": "course-001",
                "title": "中医基础理论导论",
                "description": "了解中医的基本理论和核心概念",
                "difficulty": "beginner",
                "duration": 3600,
                "rating": 4.8
            },
            {
                "id": "course-008",
                "title": "中医理论进阶",
                "description": "深入探讨中医理论的高级概念",
                "difficulty": "advanced",
                "duration": 5400,
                "rating": 4.9
            }
        ],
        "total": 2
    }

    # 模拟 API 请求
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value = AsyncMock()
        mock_get.return_value.raise_for_status = AsyncMock()
        mock_get.return_value.json = AsyncMock(return_value=mock_response)

        # 调用服务方法
        query = "中医理论"
        course_type = "tcm_basic"
        difficulty = "beginner"
        result = await edu_service.search_courses(query, course_type, difficulty)

        # 验证结果
        assert result == mock_response["results"]
        assert len(result) == 2

        # 验证 API 调用
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs["headers"]["Authorization"] == "Bearer test-api-key"
        assert "q=中医理论" in str(kwargs["params"])
        assert "type=tcm_basic" in str(kwargs["params"])
        assert "difficulty=beginner" in str(kwargs["params"])

        # 验证缓存调用
        edu_service.cache_client.get.assert_called_once()
        edu_service.cache_client.set.assert_called_once()


@pytest.mark.asyncio
async def test_get_educational_content(edu_service):
    """测试获取教育内容"""
    # 模拟响应数据
    mock_response = {
        "id": "content-001",
        "title": "阴阳平衡与健康",
        "content": "阴阳理论是中医的核心概念之一，它认为宇宙中的一切事物和现象都可以被划分为阴和阳两个对立统一的方面...",
        "format": "article",
        "type": "tcm",
        "topic": "yin-yang",
        "author": "李教授",
        "created_at": "2023-05-15T10:30:00Z",
        "read_time": 600,
        "tags": ["中医理论", "阴阳", "健康"]
    }

    # 模拟 API 请求
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value = AsyncMock()
        mock_get.return_value.raise_for_status = AsyncMock()
        mock_get.return_value.json = AsyncMock(return_value=mock_response)

        # 调用服务方法
        content_type = "tcm"
        topic = "yin-yang"
        format_type = "article"
        result = await edu_service.get_educational_content(content_type, topic, format_type)

        # 验证结果
        assert result == mock_response
        assert result["title"] == "阴阳平衡与健康"
        assert result["format"] == "article"

        # 验证 API 调用
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs["headers"]["Authorization"] == "Bearer test-api-key"
        assert "content_type=tcm" in str(kwargs["params"])
        assert "topic=yin-yang" in str(kwargs["params"])
        assert "format=article" in str(kwargs["params"])

        # 验证缓存调用
        edu_service.cache_client.get.assert_called_once()
        edu_service.cache_client.set.assert_called_once()


@pytest.mark.asyncio
async def test_track_learning_progress(edu_service):
    """测试跟踪学习进度"""
    # 模拟响应数据
    mock_response = {"success": True}

    # 模拟 API 请求
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value = AsyncMock()
        mock_post.return_value.raise_for_status = AsyncMock()
        mock_post.return_value.json = AsyncMock(return_value=mock_response)

        # 调用服务方法
        user_id = "user-123"
        course_id = "course-001"
        progress = 75.5
        completed = False
        result = await edu_service.track_learning_progress(user_id, course_id, progress, completed)

        # 验证结果
        assert result is True

        # 验证 API 调用
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs["headers"]["Authorization"] == "Bearer test-api-key"
        assert kwargs["json"]["user_id"] == "user-123"
        assert kwargs["json"]["course_id"] == "course-001"
        assert kwargs["json"]["progress"] == 75.5
        assert kwargs["json"]["completed"] is False

        # 验证没有调用缓存（因为这是写操作）
        edu_service.cache_client.get.assert_not_called()


@pytest.mark.asyncio
async def test_get_learning_statistics(edu_service):
    """测试获取学习统计信息"""
    # 模拟响应数据
    mock_response = {
        "courses_started": 5,
        "courses_completed": 3,
        "total_learning_time": 28800,
        "average_completion_rate": 85.5,
        "learning_streak": 7,
        "last_active": "2023-06-20T15:45:30Z",
        "favorite_topics": ["中医基础", "针灸", "中药学"]
    }

    # 模拟 API 请求
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value = AsyncMock()
        mock_get.return_value.raise_for_status = AsyncMock()
        mock_get.return_value.json = AsyncMock(return_value=mock_response)

        # 调用服务方法
        user_id = "user-123"
        result = await edu_service.get_learning_statistics(user_id)

        # 验证结果
        assert result == mock_response
        assert result["courses_started"] == 5
        assert result["courses_completed"] == 3

        # 验证 API 调用
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs["headers"]["Authorization"] == "Bearer test-api-key"
        assert f"/v1/learning/statistics/{user_id}" in str(args)

        # 验证缓存调用
        edu_service.cache_client.get.assert_called_once()
        edu_service.cache_client.set.assert_called_once()


@pytest.mark.asyncio
async def test_cache_hit(edu_service):
    """测试缓存命中场景"""
    # 模拟缓存命中
    cached_data = [
        {
            "id": "course-001",
            "title": "中医基础理论导论",
            "description": "了解中医的基本理论和核心概念",
            "difficulty": "beginner"
        }
    ]
    edu_service.cache_client.get.return_value = json.dumps(cached_data)

    # 直接调用方法（不应该发起API请求）
    with patch("httpx.AsyncClient.get") as mock_get:
        result = await edu_service.get_course_recommendations("user-123", ["tcm"])

        # 验证结果从缓存获取
        assert result == cached_data

        # 验证未发起API请求
        mock_get.assert_not_called()

        # 验证调用了缓存获取
        edu_service.cache_client.get.assert_called_once()

        # 验证未写入缓存
        edu_service.cache_client.set.assert_not_called()


@pytest.mark.asyncio
async def test_api_error_handling(edu_service):
    """测试API错误处理"""
    # 模拟API错误
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.side_effect = Exception("API连接失败")

        # 调用服务方法
        result = await edu_service.search_courses("中医")

        # 验证返回空列表
        assert result == []

        # 验证尝试过从缓存获取
        edu_service.cache_client.get.assert_called_once()


@pytest.mark.asyncio
async def test_api_error_with_cache_fallback(edu_service):
    """测试API错误时的缓存回退"""
    # 模拟缓存数据
    cached_data = {
        "courses_started": 5,
        "courses_completed": 3
    }
    edu_service.cache_client.get.return_value = json.dumps(cached_data)

    # 模拟API错误
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.side_effect = Exception("API连接失败")

        # 调用服务方法
        result = await edu_service.get_learning_statistics("user-123")

        # 验证返回缓存数据
        assert result == cached_data

        # 验证尝试过从缓存获取
        edu_service.cache_client.get.assert_called_once()
