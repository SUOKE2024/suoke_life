#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
老克智能体服务 - API集成测试
测试GraphQL和REST端点的集成功能
"""

import pytest
import json
from typing import Dict, Any
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_health_endpoint(async_client: AsyncClient):
    """
    测试健康检查端点
    """
    response = await async_client.get("/health/status")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert "serviceInfo" in data
    assert "version" in data["serviceInfo"]
    assert "serviceName" in data["serviceInfo"]
    assert data["serviceInfo"]["serviceName"] == "laoke-service"


async def test_metrics_endpoint(async_client: AsyncClient):
    """
    测试指标端点
    """
    response = await async_client.get("/metrics")
    
    assert response.status_code == 200
    assert len(response.content) > 0
    assert response.headers["content-type"] == "text/plain; version=0.0.4"


async def test_graphql_knowledge_query(async_client: AsyncClient, mock_knowledge_article: Dict[str, Any]):
    """
    测试GraphQL知识查询
    
    需要模拟知识服务组件
    """
    query = """
    query {
        knowledgeArticles(limit: 5) {
            id
            title
            category
            tags
            rating
        }
    }
    """
    
    response = await async_client.post(
        "/graphql",
        json={"query": query}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "knowledgeArticles" in data["data"]
    assert isinstance(data["data"]["knowledgeArticles"], list)


async def test_graphql_learning_paths_query(async_client: AsyncClient, mock_learning_path: Dict[str, Any]):
    """
    测试GraphQL学习路径查询
    
    需要模拟知识服务组件
    """
    query = """
    query {
        learningPaths(category: "中医基础", level: BEGINNER) {
            id
            title
            description
            category
            level
            estimatedDuration
            enrolledUsers
            completionRate
        }
    }
    """
    
    response = await async_client.post(
        "/graphql",
        json={"query": query}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "learningPaths" in data["data"]
    assert isinstance(data["data"]["learningPaths"], list)


async def test_graphql_community_posts_query(async_client: AsyncClient, mock_community_post: Dict[str, Any]):
    """
    测试GraphQL社区帖子查询
    
    需要模拟社区服务组件
    """
    query = """
    query {
        communityPosts(limit: 5) {
            id
            title
            content
            author {
                id
                displayName
                role
            }
            category
            tags
            likeCount
            commentCount
            isFeatured
        }
    }
    """
    
    response = await async_client.post(
        "/graphql",
        json={"query": query}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "communityPosts" in data["data"]
    assert isinstance(data["data"]["communityPosts"], list)


async def test_graphql_agent_interaction_mutation(async_client: AsyncClient):
    """
    测试GraphQL与智能体交互变更
    
    需要模拟代理管理器组件
    """
    mutation = """
    mutation {
        agentInteraction(input: {
            userId: "test-user-id",
            message: "中医入门应该怎么学习？",
            context: {
                sessionId: "test-session"
            }
        }) {
            responseId
            message
            actions {
                type
                payload
            }
            resources {
                id
                title
                type
                url
            }
        }
    }
    """
    
    response = await async_client.post(
        "/graphql",
        json={"query": mutation}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "agentInteraction" in data["data"]
    assert "responseId" in data["data"]["agentInteraction"]
    assert "message" in data["data"]["agentInteraction"] 