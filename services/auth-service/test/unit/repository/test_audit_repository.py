#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
审计日志仓储单元测试
"""
import uuid
from datetime import datetime, timedelta, UTC

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from internal.repository.audit_repository import AuditRepository
from internal.model.user import AuditLog, AuditActionEnum
from internal.model.errors import DatabaseError


@pytest.fixture
def mock_session():
    """创建模拟数据库会话"""
    session = AsyncMock(spec=AsyncSession)
    return session


@pytest.fixture
def audit_repository(mock_session):
    """创建审计日志仓储实例"""
    return AuditRepository(mock_session)


@pytest.fixture
def mock_audit_log():
    """创建模拟审计日志"""
    user_id = str(uuid.uuid4())
    audit_log = MagicMock(spec=AuditLog)
    audit_log.id = 1
    audit_log.user_id = user_id
    audit_log.action = AuditActionEnum.LOGIN
    audit_log.ip_address = "127.0.0.1"
    audit_log.user_agent = "Test User Agent"
    audit_log.details = {"username": "testuser", "type": "login_attempt"}
    audit_log.success = True
    audit_log.created_at = datetime.now(UTC)
    return audit_log


class TestAuditRepository:
    """审计日志仓储测试"""
    
    @pytest.mark.asyncio
    async def test_add_audit_log(self, audit_repository, mock_session):
        """测试添加审计日志"""
        # 准备测试数据
        user_id = str(uuid.uuid4())
        action = AuditActionEnum.LOGIN
        ip_address = "127.0.0.1"
        user_agent = "Test User Agent"
        details = {"test_key": "test_value"}
        
        # 执行方法
        result = await audit_repository.add_audit_log(
            user_id=user_id,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
            success=True
        )
        
        # 验证结果
        assert result is not None
        assert result.user_id == user_id
        assert result.action == action
        assert result.ip_address == ip_address
        assert result.user_agent == user_agent
        assert result.details == details
        assert result.success is True
        
        # 验证会话操作
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_audit_log_failure(self, audit_repository, mock_session):
        """测试添加审计日志失败"""
        # 模拟会话操作异常
        mock_session.commit.side_effect = Exception("测试异常")
        
        # 执行方法，期望抛出异常
        with pytest.raises(DatabaseError):
            await audit_repository.add_audit_log(
                user_id=str(uuid.uuid4()),
                action=AuditActionEnum.LOGIN,
                success=True
            )
        
        # 验证会话操作
        mock_session.rollback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_login_attempt(self, audit_repository):
        """测试记录登录尝试"""
        # 准备测试数据
        username = "testuser"
        success = True
        ip_address = "127.0.0.1"
        user_agent = "Test User Agent"
        
        # 模拟add_audit_log方法
        audit_repository.add_audit_log = AsyncMock()
        audit_log = MagicMock(spec=AuditLog)
        audit_repository.add_audit_log.return_value = audit_log
        
        # 执行方法
        result = await audit_repository.add_login_attempt(
            username=username,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # 验证结果
        assert result is audit_log
        
        # 验证add_audit_log调用
        audit_repository.add_audit_log.assert_called_once()
        args, kwargs = audit_repository.add_audit_log.call_args
        assert kwargs["user_id"] is None
        assert kwargs["action"] == AuditActionEnum.LOGIN
        assert kwargs["ip_address"] == ip_address
        assert kwargs["user_agent"] == user_agent
        assert kwargs["success"] == success
        assert "username" in kwargs["details"]
        assert kwargs["details"]["username"] == username
    
    @pytest.mark.asyncio
    async def test_get_recent_failed_attempts(self, audit_repository, mock_session, mock_audit_log):
        """测试获取最近失败的登录尝试"""
        # 准备测试数据
        username = "testuser"
        minutes = 30
        
        # 模拟会话执行结果
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_audit_log]
        mock_session.execute.return_value = mock_result
        
        # 执行方法
        result = await audit_repository.get_recent_failed_attempts(username, minutes)
        
        # 验证结果
        assert len(result) == 1
        assert result[0] is mock_audit_log
        
        # 验证会话操作
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_recent_failed_attempts_exception(self, audit_repository, mock_session):
        """测试获取最近失败的登录尝试异常情况"""
        # 模拟会话执行异常
        mock_session.execute.side_effect = Exception("测试异常")
        
        # 执行方法，期望抛出异常
        with pytest.raises(DatabaseError):
            await audit_repository.get_recent_failed_attempts("testuser")
    
    @pytest.mark.asyncio
    async def test_count_failed_attempts(self, audit_repository, mock_session):
        """测试统计失败的登录尝试次数"""
        # 准备测试数据
        username = "testuser"
        minutes = 30
        expected_count = 3
        
        # 模拟会话执行结果
        mock_result = MagicMock()
        mock_result.scalar.return_value = expected_count
        mock_session.execute.return_value = mock_result
        
        # 执行方法
        result = await audit_repository.count_failed_attempts(username, minutes)
        
        # 验证结果
        assert result == expected_count
        
        # 验证会话操作
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_user_audit_logs(self, audit_repository, mock_session, mock_audit_log):
        """测试获取用户审计日志"""
        # 准备测试数据
        user_id = str(uuid.uuid4())
        limit = 50
        offset = 10
        
        # 模拟会话执行结果
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_audit_log]
        mock_session.execute.return_value = mock_result
        
        # 执行方法
        result = await audit_repository.get_user_audit_logs(user_id, limit, offset)
        
        # 验证结果
        assert len(result) == 1
        assert result[0] is mock_audit_log
        
        # 验证会话操作
        mock_session.execute.assert_called_once() 