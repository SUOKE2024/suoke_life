#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康检查模块单元测试
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import redis

from internal.observability.health import (
    HealthCheck, 
    DatabaseHealthCheck, 
    RedisHealthCheck, 
    ServiceHealthCheck,
    HealthStatus
)


class TestHealthCheck:
    """健康检查基类测试"""
    
    def test_health_check_base(self):
        """测试健康检查基类"""
        # 创建子类
        class MockHealthCheck(HealthCheck):
            async def check_health(self):
                return {"status": "UP", "details": {"foo": "bar"}}
        
        # 初始化健康检查
        health_check = MockHealthCheck(name="mock_check")
        
        # 测试属性
        assert health_check.name == "mock_check"


class TestDatabaseHealthCheck:
    """数据库健康检查测试"""
    
    @pytest.mark.asyncio
    async def test_database_health_check_success(self):
        """测试数据库健康检查成功"""
        # 模拟数据库会话
        mock_db_pool = AsyncMock()
        mock_conn = AsyncMock()
        mock_conn.fetchval = AsyncMock(return_value="PostgreSQL 15.3")
        mock_db_pool.acquire.return_value.__aenter__.return_value = mock_conn
        
        # 创建健康检查
        db_health = DatabaseHealthCheck(db_pool=mock_db_pool)
        
        # 执行检查
        result = await db_health.check_health()
        
        # 验证结果
        assert result["status"] == HealthStatus.UP
        assert "version" in result["details"]
        assert "latency_ms" in result["details"]
        assert "PostgreSQL" in result["details"]["version"]
        
        # 验证数据库操作
        mock_db_pool.acquire.assert_called_once()
        mock_conn.fetchval.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_database_health_check_failure(self):
        """测试数据库健康检查失败"""
        # 模拟数据库会话
        mock_db_pool = AsyncMock()
        mock_db_pool.acquire.side_effect = Exception("连接失败")
        
        # 创建健康检查
        db_health = DatabaseHealthCheck(db_pool=mock_db_pool)
        
        # 执行检查
        result = await db_health.check_health()
        
        # 验证结果
        assert result["status"] == HealthStatus.DOWN
        assert "error" in result["details"]
        assert "连接失败" in result["details"]["error"]


class TestRedisHealthCheck:
    """Redis健康检查测试"""
    
    @pytest.mark.asyncio
    async def test_redis_health_check_success(self):
        """测试Redis健康检查成功"""
        # 模拟Redis客户端
        mock_redis = MagicMock(spec=redis.Redis)
        mock_redis.ping.return_value = True
        mock_redis.info.return_value = {"redis_version": "7.0.0"}
        
        # 创建健康检查
        redis_health = RedisHealthCheck(redis_client=mock_redis)
        
        # 执行检查
        result = await redis_health.check_health()
        
        # 验证结果
        assert result["status"] == HealthStatus.UP
        assert "version" in result["details"]
        assert "latency_ms" in result["details"]
        assert "7.0.0" in result["details"]["version"]
        
        # 验证Redis操作
        mock_redis.ping.assert_called_once()
        mock_redis.info.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_redis_health_check_failure(self):
        """测试Redis健康检查失败"""
        # 模拟Redis客户端
        mock_redis = MagicMock(spec=redis.Redis)
        mock_redis.ping.side_effect = redis.RedisError("连接错误")
        
        # 创建健康检查
        redis_health = RedisHealthCheck(redis_client=mock_redis)
        
        # 执行检查
        result = await redis_health.check_health()
        
        # 验证结果
        assert result["status"] == HealthStatus.DOWN
        assert "error" in result["details"]
        assert "连接错误" in result["details"]["error"]


class TestServiceHealthCheck:
    """服务健康检查测试"""
    
    @pytest.mark.asyncio
    async def test_service_health_check_success(self):
        """测试服务健康检查成功"""
        # 模拟外部服务检查
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"status": "ok"})
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        with patch("aiohttp.ClientSession", return_value=mock_session):
            # 创建健康检查
            service_health = ServiceHealthCheck(
                name="test_service",
                url="http://example.com/health"
            )
            
            # 执行检查
            result = await service_health.check_health()
            
            # 验证结果
            assert result["status"] == HealthStatus.UP
            assert "response" in result["details"]
            assert "latency_ms" in result["details"]
            assert result["details"]["response"] == {"status": "ok"}
    
    @pytest.mark.asyncio
    async def test_service_health_check_failure(self):
        """测试服务健康检查失败"""
        # 模拟外部服务检查失败
        mock_session = AsyncMock()
        mock_session.get.side_effect = Exception("连接超时")
        
        with patch("aiohttp.ClientSession", return_value=mock_session):
            # 创建健康检查
            service_health = ServiceHealthCheck(
                name="test_service",
                url="http://example.com/health"
            )
            
            # 执行检查
            result = await service_health.check_health()
            
            # 验证结果
            assert result["status"] == HealthStatus.DOWN
            assert "error" in result["details"]
            assert "连接超时" in result["details"]["error"] 