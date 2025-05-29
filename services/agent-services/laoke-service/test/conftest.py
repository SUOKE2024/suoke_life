#!/usr/bin/env python

"""
老克智能体服务 - 测试配置
提供测试夹具和共享资源
"""

import asyncio
import os
import sys
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cmd.server import app as fastapi_app

from pkg.utils.config import Config

# 测试环境变量
os.environ["LAOKE_ENV"] = "test"
os.environ["LAOKE_CONFIG_PATH"] = os.path.abspath(os.path.join(os.path.dirname(__file__), "../config/config.development.yaml"))

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop]:
    """创建一个事件循环，供pytest-asyncio使用"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def config() -> Config:
    """配置夹具，用于测试"""
    config = Config()
    # 确保使用测试环境配置
    assert config.get("service.env") in ["test", "development"]
    return config

@pytest.fixture
def test_client() -> Generator[TestClient]:
    """创建TestClient实例，用于同步API测试"""
    with TestClient(fastapi_app) as client:
        yield client

@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient]:
    """创建AsyncClient实例，用于异步API测试"""
    async with AsyncClient(app=fastapi_app, base_url="http://test") as client:
        yield client

@pytest.fixture
def test_user_data() -> dict[str, Any]:
    """创建测试用户数据"""
    return {
        "id": "test-user-id",
        "username": "testuser",
        "display_name": "测试用户",
        "role": "STUDENT"
    }

@pytest.fixture
def mock_knowledge_article() -> dict[str, Any]:
    """创建模拟知识文章数据"""
    return {
        "id": "test-article-id",
        "title": "中医四诊基础",
        "content": "中医四诊是指望、闻、问、切四种诊断方法...",
        "category": "中医基础",
        "tags": ["四诊", "基础理论"],
        "created_at": "2023-01-01T00:00:00Z",
        "rating": 4.5,
        "rating_count": 10,
        "view_count": 100
    }

@pytest.fixture
def mock_learning_path() -> dict[str, Any]:
    """创建模拟学习路径数据"""
    return {
        "id": "test-path-id",
        "title": "中医入门学习路径",
        "description": "适合初学者的中医基础知识学习路径",
        "category": "中医基础",
        "level": "beginner",
        "estimated_duration": "2个月",
        "modules": [
            {
                "id": "module-1",
                "title": "中医基础理论",
                "description": "了解中医的基本概念和理论体系",
                "content": "中医基础理论内容...",
                "resources": [],
                "order": 1
            }
        ],
        "enrolled_users": 50,
        "completion_rate": 0.75
    }

@pytest.fixture
def mock_community_post() -> dict[str, Any]:
    """创建模拟社区帖子数据"""
    return {
        "id": "test-post-id",
        "title": "分享我的养生心得",
        "content": "长期实践总结的一些养生经验...",
        "author": {
            "id": "author-id",
            "username": "healthmaster",
            "display_name": "养生大师",
            "role": "EXPERT"
        },
        "category": "经验分享",
        "tags": ["养生", "实践"],
        "created_at": "2023-02-15T10:30:00Z",
        "like_count": 25,
        "comment_count": 8,
        "comments": [],
        "is_featured": True
    }

@pytest.fixture(autouse=True)
def setup_and_teardown():
    """
    测试前后的设置和清理操作
    这是一个自动使用的夹具，会在每个测试函数前后运行
    """
    # 测试前的设置
    yield
    # 测试后的清理

    # 重置单例实例
    from internal.delivery import dependencies
    dependencies._agent_manager = None
    dependencies._knowledge_service = None
    dependencies._community_service = None
