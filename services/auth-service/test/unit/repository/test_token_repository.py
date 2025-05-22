#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
令牌仓储单元测试
"""
import json
import uuid
from datetime import datetime, timedelta, UTC

import pytest
from unittest.mock import MagicMock, patch, AsyncMock

import redis
from sqlalchemy.ext.asyncio import AsyncSession
from internal.repository.token_repository import TokenRepository
from internal.model.errors import InvalidTokenError, DatabaseError


@pytest.fixture
def mock_redis():
    """创建模拟Redis客户端"""
    mock_client = MagicMock(spec=redis.Redis)
    return mock_client

@pytest.fixture
def mock_session():
    """创建模拟数据库会话"""
    mock_db_session = AsyncMock(spec=AsyncSession)
    return mock_db_session

@pytest.fixture
def token_repository(mock_redis, mock_session):
    """创建令牌仓储实例"""
    return TokenRepository(mock_redis, mock_session)


class TestTokenRepository:
    """令牌仓储测试"""
    
    @pytest.mark.asyncio
    async def test_store_token_data_access(self, token_repository, mock_redis):
        """测试存储访问令牌数据"""
        # 准备测试数据
        token = str(uuid.uuid4())
        token_type = "access"
        user_id = str(uuid.uuid4())
        data = {"user_id": user_id, "username": "testuser"}
        expires_in = 3600
        
        # 执行方法
        result = await token_repository.store_token_data(token, token_type, data, expires_in)
        
        # 验证结果
        assert result is True
        
        # 验证Redis操作
        mock_redis.setex.assert_called_once_with(
            f"{token_repository.ACCESS_TOKEN_PREFIX}{token}", 
            expires_in, 
            json.dumps(data)
        )
        
        # 验证用户令牌集合操作
        mock_redis.sadd.assert_called_once_with(
            f"auth:user_tokens:{user_id}",
            token
        )
    
    @pytest.mark.asyncio
    async def test_store_token_data_refresh(self, token_repository, mock_redis):
        """测试存储刷新令牌数据"""
        # 准备测试数据
        token = str(uuid.uuid4())
        token_type = "refresh"
        data = {"user_id": str(uuid.uuid4()), "username": "testuser"}
        expires_in = 86400
        
        # 执行方法
        result = await token_repository.store_token_data(token, token_type, data, expires_in)
        
        # 验证结果
        assert result is True
        
        # 验证Redis操作
        mock_redis.setex.assert_called_once_with(
            f"{token_repository.REFRESH_TOKEN_PREFIX}{token}", 
            expires_in, 
            json.dumps(data)
        )
        
        # 不应该添加到用户令牌集合
        mock_redis.sadd.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_store_token_data_mfa(self, token_repository, mock_redis):
        """测试存储MFA令牌数据"""
        # 准备测试数据
        token = str(uuid.uuid4())
        token_type = "mfa"
        data = {"user_id": str(uuid.uuid4()), "username": "testuser"}
        expires_in = 300
        
        # 执行方法
        result = await token_repository.store_token_data(token, token_type, data, expires_in)
        
        # 验证结果
        assert result is True
        
        # 验证Redis操作
        mock_redis.setex.assert_called_once_with(
            f"{token_repository.MFA_TOKEN_PREFIX}{token}", 
            expires_in, 
            json.dumps(data)
        )
        
        # 不应该添加到用户令牌集合
        mock_redis.sadd.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_store_token_data_invalid_type(self, token_repository):
        """测试存储无效类型的令牌数据"""
        # 准备测试数据
        token = str(uuid.uuid4())
        token_type = "invalid"
        data = {"user_id": str(uuid.uuid4()), "username": "testuser"}
        expires_in = 3600
        
        # 执行方法，期望抛出异常
        with pytest.raises(DatabaseError):
            await token_repository.store_token_data(token, token_type, data, expires_in)
    
    @pytest.mark.asyncio
    async def test_store_token_data_error(self, token_repository, mock_redis):
        """测试存储令牌数据时发生错误"""
        # 准备测试数据
        token = str(uuid.uuid4())
        token_type = "access"
        data = {"user_id": str(uuid.uuid4()), "username": "testuser"}
        expires_in = 3600
        
        # 模拟Redis操作异常
        mock_redis.setex.side_effect = Exception("Redis连接错误")
        
        # 执行方法，期望抛出异常
        with pytest.raises(DatabaseError):
            await token_repository.store_token_data(token, token_type, data, expires_in)
    
    @pytest.mark.asyncio
    async def test_get_token_data_valid(self, token_repository, mock_redis):
        """测试获取有效的令牌数据"""
        # 准备测试数据
        token = str(uuid.uuid4())
        token_type = "access"
        expected_data = {"user_id": str(uuid.uuid4()), "username": "testuser"}
        
        # 模拟Redis操作
        mock_redis.exists.return_value = False  # 令牌不在黑名单中
        mock_redis.get.return_value = json.dumps(expected_data)
        
        # 执行方法
        result = await token_repository.get_token_data(token, token_type)
        
        # 验证结果
        assert result == expected_data
        
        # 验证Redis操作
        mock_redis.exists.assert_called_once_with(f"{token_repository.BLACKLIST_PREFIX}{token}")
        mock_redis.get.assert_called_once_with(f"{token_repository.ACCESS_TOKEN_PREFIX}{token}")
    
    @pytest.mark.asyncio
    async def test_get_token_data_refresh(self, token_repository, mock_redis):
        """测试获取刷新令牌数据"""
        # 准备测试数据
        token = str(uuid.uuid4())
        token_type = "refresh"
        expected_data = {"user_id": str(uuid.uuid4()), "username": "testuser"}
        
        # 模拟Redis操作
        mock_redis.exists.return_value = False  # 令牌不在黑名单中
        mock_redis.get.return_value = json.dumps(expected_data)
        
        # 执行方法
        result = await token_repository.get_token_data(token, token_type)
        
        # 验证结果
        assert result == expected_data
        
        # 验证Redis操作
        mock_redis.exists.assert_called_once_with(f"{token_repository.BLACKLIST_PREFIX}{token}")
        mock_redis.get.assert_called_once_with(f"{token_repository.REFRESH_TOKEN_PREFIX}{token}")
    
    @pytest.mark.asyncio
    async def test_get_token_data_mfa(self, token_repository, mock_redis):
        """测试获取MFA令牌数据"""
        # 准备测试数据
        token = str(uuid.uuid4())
        token_type = "mfa"
        expected_data = {"user_id": str(uuid.uuid4()), "username": "testuser"}
        
        # 模拟Redis操作
        mock_redis.exists.return_value = False  # 令牌不在黑名单中
        mock_redis.get.return_value = json.dumps(expected_data)
        
        # 执行方法
        result = await token_repository.get_token_data(token, token_type)
        
        # 验证结果
        assert result == expected_data
        
        # 验证Redis操作
        mock_redis.exists.assert_called_once_with(f"{token_repository.BLACKLIST_PREFIX}{token}")
        mock_redis.get.assert_called_once_with(f"{token_repository.MFA_TOKEN_PREFIX}{token}")
    
    @pytest.mark.asyncio
    async def test_get_token_data_invalid_type(self, token_repository, mock_redis):
        """测试获取无效类型的令牌数据"""
        # 准备测试数据
        token = str(uuid.uuid4())
        token_type = "invalid"
        
        # 执行方法，期望抛出异常
        with pytest.raises(DatabaseError):
            await token_repository.get_token_data(token, token_type)
    
    @pytest.mark.asyncio
    async def test_get_token_data_blacklisted(self, token_repository, mock_redis):
        """测试获取黑名单中的令牌数据"""
        # 准备测试数据
        token = str(uuid.uuid4())
        token_type = "access"
        
        # 模拟Redis操作
        mock_redis.exists.return_value = True  # 令牌在黑名单中
        
        # 执行方法，期望抛出异常
        with pytest.raises(InvalidTokenError) as exc_info:
            await token_repository.get_token_data(token, token_type)
        
        # 验证异常信息
        assert "令牌已被撤销" in str(exc_info.value)
        
        # 验证Redis操作
        mock_redis.exists.assert_called_once_with(f"{token_repository.BLACKLIST_PREFIX}{token}")
        mock_redis.get.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_token_data_expired(self, token_repository, mock_redis):
        """测试获取已过期令牌数据"""
        # 准备测试数据
        token = str(uuid.uuid4())
        token_type = "access"
        
        # 模拟Redis操作
        mock_redis.exists.return_value = False  # 令牌不在黑名单中
        mock_redis.get.return_value = None  # 令牌不存在或已过期
        
        # 执行方法，期望抛出异常
        with pytest.raises(InvalidTokenError) as exc_info:
            await token_repository.get_token_data(token, token_type)
        
        # 验证异常信息
        assert "令牌无效或已过期" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_token_data_error(self, token_repository, mock_redis):
        """测试获取令牌数据时发生错误"""
        # 准备测试数据
        token = str(uuid.uuid4())
        token_type = "access"
        
        # 模拟Redis操作异常
        mock_redis.exists.side_effect = Exception("Redis连接错误")
        
        # 执行方法，期望抛出异常
        with pytest.raises(DatabaseError):
            await token_repository.get_token_data(token, token_type)
    
    @pytest.mark.asyncio
    async def test_revoke_token(self, token_repository, mock_redis):
        """测试撤销令牌"""
        # 准备测试数据
        token = str(uuid.uuid4())
        token_type = "access"
        user_id = str(uuid.uuid4())
        ttl = 3000  # 剩余生存时间（秒）
        
        # 模拟Redis操作
        mock_redis.ttl.return_value = ttl
        
        # 执行方法
        result = await token_repository.revoke_token(token, token_type, user_id)
        
        # 验证结果
        assert result is True
        
        # 验证Redis操作
        mock_redis.ttl.assert_called_once_with(f"{token_repository.ACCESS_TOKEN_PREFIX}{token}")
        mock_redis.delete.assert_called_once_with(f"{token_repository.ACCESS_TOKEN_PREFIX}{token}")
        mock_redis.setex.assert_called_once_with(
            f"{token_repository.BLACKLIST_PREFIX}{token}",
            ttl,
            "1"
        )
        mock_redis.srem.assert_called_once_with(f"auth:user_tokens:{user_id}", token)
    
    @pytest.mark.asyncio
    async def test_revoke_token_refresh(self, token_repository, mock_redis):
        """测试撤销刷新令牌"""
        # 准备测试数据
        token = str(uuid.uuid4())
        token_type = "refresh"
        user_id = str(uuid.uuid4())
        ttl = 3000  # 剩余生存时间（秒）
        
        # 模拟Redis操作
        mock_redis.ttl.return_value = ttl
        
        # 执行方法
        result = await token_repository.revoke_token(token, token_type, user_id)
        
        # 验证结果
        assert result is True
        
        # 验证Redis操作
        mock_redis.ttl.assert_called_once_with(f"{token_repository.REFRESH_TOKEN_PREFIX}{token}")
        mock_redis.delete.assert_called_once_with(f"{token_repository.REFRESH_TOKEN_PREFIX}{token}")
        mock_redis.setex.assert_called_once_with(
            f"{token_repository.BLACKLIST_PREFIX}{token}",
            ttl,
            "1"
        )
        # 用户令牌集合中不应该有刷新令牌
        mock_redis.srem.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_revoke_token_invalid_type(self, token_repository):
        """测试撤销无效类型的令牌"""
        # 准备测试数据
        token = str(uuid.uuid4())
        token_type = "invalid"
        
        # 执行方法，期望抛出异常
        with pytest.raises(DatabaseError):
            await token_repository.revoke_token(token, token_type)
    
    @pytest.mark.asyncio
    async def test_revoke_token_expired(self, token_repository, mock_redis):
        """测试撤销已过期令牌"""
        # 准备测试数据
        token = str(uuid.uuid4())
        token_type = "access"
        
        # 模拟Redis操作
        mock_redis.ttl.return_value = -1  # 已过期
        
        # 执行方法
        result = await token_repository.revoke_token(token, token_type)
        
        # 验证结果
        assert result is True
        
        # 验证Redis操作
        mock_redis.ttl.assert_called_once_with(f"{token_repository.ACCESS_TOKEN_PREFIX}{token}")
        mock_redis.delete.assert_not_called()
        mock_redis.setex.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_revoke_token_error(self, token_repository, mock_redis):
        """测试撤销令牌时发生错误"""
        # 准备测试数据
        token = str(uuid.uuid4())
        token_type = "access"
        
        # 模拟Redis操作异常
        mock_redis.ttl.side_effect = Exception("Redis连接错误")
        
        # 执行方法，期望抛出异常
        with pytest.raises(DatabaseError):
            await token_repository.revoke_token(token, token_type)
    
    @pytest.mark.asyncio
    async def test_revoke_all_user_tokens(self, token_repository, mock_redis):
        """测试撤销用户所有令牌"""
        # 准备测试数据
        user_id = str(uuid.uuid4())
        tokens = ["token1", "token2", "token3"]
        
        # 模拟Redis操作
        mock_redis.smembers.return_value = tokens
        
        # 保存原始方法
        original_revoke_token = token_repository.revoke_token
        
        try:
            # 模拟revoke_token方法
            token_repository.revoke_token = AsyncMock(return_value=True)
            
            # 执行方法
            result = await token_repository.revoke_all_user_tokens(user_id)
            
            # 验证结果
            assert result is True
            
            # 验证Redis操作
            mock_redis.smembers.assert_called_once_with(f"auth:user_tokens:{user_id}")
            mock_redis.delete.assert_called_once_with(f"auth:user_tokens:{user_id}")
            
            # 验证revoke_token调用次数
            assert token_repository.revoke_token.call_count == len(tokens)
            
            # 验证每个令牌都被调用了
            for i, token in enumerate(tokens):
                assert token_repository.revoke_token.call_args_list[i][0][0] == token
                assert token_repository.revoke_token.call_args_list[i][0][1] == "access"
                assert token_repository.revoke_token.call_args_list[i][0][2] == user_id
        finally:
            # 恢复原始方法
            token_repository.revoke_token = original_revoke_token
    
    @pytest.mark.asyncio
    async def test_revoke_all_user_tokens_empty(self, token_repository, mock_redis):
        """测试撤销用户所有令牌（无令牌）"""
        # 准备测试数据
        user_id = str(uuid.uuid4())
        
        # 模拟Redis操作
        mock_redis.smembers.return_value = set()
        
        # 保存原始方法
        original_revoke_token = token_repository.revoke_token
        
        try:
            # 模拟revoke_token方法
            token_repository.revoke_token = AsyncMock(return_value=True)
            
            # 执行方法
            result = await token_repository.revoke_all_user_tokens(user_id)
            
            # 验证结果
            assert result is True
            
            # 验证Redis操作
            mock_redis.smembers.assert_called_once_with(f"auth:user_tokens:{user_id}")
            mock_redis.delete.assert_called_once_with(f"auth:user_tokens:{user_id}")
            
            # revoke_token不应该被调用
            token_repository.revoke_token.assert_not_called()
        finally:
            # 恢复原始方法
            token_repository.revoke_token = original_revoke_token
    
    @pytest.mark.asyncio
    async def test_revoke_all_user_tokens_error(self, token_repository, mock_redis):
        """测试撤销用户所有令牌时发生错误"""
        # 准备测试数据
        user_id = str(uuid.uuid4())
        
        # 模拟Redis操作异常
        mock_redis.smembers.side_effect = Exception("Redis连接错误")
        
        # 执行方法，期望抛出异常
        with pytest.raises(DatabaseError):
            await token_repository.revoke_all_user_tokens(user_id)
    
    @pytest.mark.asyncio
    async def test_store_verification_code(self, token_repository, mock_redis):
        """测试存储验证码"""
        # 准备测试数据
        code_type = "email"
        identifier = "test@example.com"
        code = "123456"
        expires_in = 300  # 5分钟
        
        # 执行方法
        result = await token_repository.store_verification_code(code_type, identifier, code, expires_in)
        
        # 验证结果
        assert result is True
        
        # 验证Redis操作
        mock_redis.setex.assert_called_once_with(
            f"auth:{code_type}_code:{identifier}",
            expires_in,
            code
        )
    
    @pytest.mark.asyncio
    async def test_store_verification_code_error(self, token_repository, mock_redis):
        """测试存储验证码时发生错误"""
        # 准备测试数据
        code_type = "email"
        identifier = "test@example.com"
        code = "123456"
        expires_in = 300
        
        # 模拟Redis操作异常
        mock_redis.setex.side_effect = Exception("Redis连接错误")
        
        # 执行方法，期望抛出异常
        with pytest.raises(DatabaseError):
            await token_repository.store_verification_code(code_type, identifier, code, expires_in)
    
    @pytest.mark.asyncio
    async def test_verify_code_valid(self, token_repository, mock_redis):
        """测试验证有效验证码"""
        # 准备测试数据
        code_type = "email"
        identifier = "test@example.com"
        code = "123456"
        
        # 模拟Redis操作
        mock_redis.get.return_value = code
        
        # 执行方法
        result = await token_repository.verify_code(code_type, identifier, code)
        
        # 验证结果
        assert result is True
        
        # 验证Redis操作
        mock_redis.get.assert_called_once_with(f"auth:{code_type}_code:{identifier}")
    
    @pytest.mark.asyncio
    async def test_verify_code_invalid(self, token_repository, mock_redis):
        """测试验证无效验证码"""
        # 准备测试数据
        code_type = "email"
        identifier = "test@example.com"
        code = "123456"
        
        # 模拟Redis操作
        mock_redis.get.return_value = "654321"  # 不匹配的验证码
        
        # 执行方法
        result = await token_repository.verify_code(code_type, identifier, code)
        
        # 验证结果
        assert result is False
        
        # 验证Redis操作
        mock_redis.get.assert_called_once_with(f"auth:{code_type}_code:{identifier}")
    
    @pytest.mark.asyncio
    async def test_verify_code_expired(self, token_repository, mock_redis):
        """测试验证已过期验证码"""
        # 准备测试数据
        code_type = "email"
        identifier = "test@example.com"
        code = "123456"
        
        # 模拟Redis操作
        mock_redis.get.return_value = None  # 验证码不存在或已过期
        
        # 执行方法
        result = await token_repository.verify_code(code_type, identifier, code)
        
        # 验证结果
        assert result is False
        
        # 验证Redis操作
        mock_redis.get.assert_called_once_with(f"auth:{code_type}_code:{identifier}")
    
    @pytest.mark.asyncio
    async def test_verify_code_error(self, token_repository, mock_redis):
        """测试验证验证码时发生错误"""
        # 准备测试数据
        code_type = "email"
        identifier = "test@example.com"
        code = "123456"
        
        # 模拟Redis操作异常
        mock_redis.get.side_effect = Exception("Redis连接错误")
        
        # 执行方法，期望抛出异常
        with pytest.raises(DatabaseError):
            await token_repository.verify_code(code_type, identifier, code)
    
    @pytest.mark.asyncio
    async def test_delete_code(self, token_repository, mock_redis):
        """测试删除验证码"""
        # 准备测试数据
        code_type = "email"
        identifier = "test@example.com"
        
        # 执行方法
        result = await token_repository.delete_code(code_type, identifier)
        
        # 验证结果
        assert result is True
        
        # 验证Redis操作
        mock_redis.delete.assert_called_once_with(f"auth:{code_type}_code:{identifier}")
    
    @pytest.mark.asyncio
    async def test_delete_code_error(self, token_repository, mock_redis):
        """测试删除验证码时发生错误"""
        # 准备测试数据
        code_type = "email"
        identifier = "test@example.com"
        
        # 模拟Redis操作异常
        mock_redis.delete.side_effect = Exception("Redis连接错误")
        
        # 执行方法，期望抛出异常
        with pytest.raises(DatabaseError):
            await token_repository.delete_code(code_type, identifier)
    
    @pytest.mark.asyncio
    async def test_rate_limit_check_first_attempt(self, token_repository, mock_redis):
        """测试速率限制检查（首次尝试）"""
        # 准备测试数据
        action = "login"
        identifier = "127.0.0.1"
        max_attempts = 5
        window_seconds = 300
        
        # 模拟Redis操作
        mock_redis.get.return_value = None  # 首次尝试，没有之前的记录
        
        # 执行方法
        allowed, cooldown = await token_repository.rate_limit_check(
            action, identifier, max_attempts, window_seconds
        )
        
        # 验证结果
        assert allowed is True
        assert cooldown is None
        
        # 验证Redis操作
        mock_redis.get.assert_called_once_with(f"auth:rate_limit:{action}:{identifier}")
        mock_redis.setex.assert_called_once()  # 设置初始值
    
    @pytest.mark.asyncio
    async def test_rate_limit_check_within_limit(self, token_repository, mock_redis):
        """测试速率限制检查（在限制内）"""
        # 准备测试数据
        action = "login"
        identifier = "127.0.0.1"
        max_attempts = 5
        window_seconds = 300
        current_attempts = 3
        window_start = int(datetime.now().timestamp()) - 60  # 1分钟前
        
        # 模拟Redis操作
        mock_redis.get.return_value = json.dumps({
            "attempts": current_attempts,
            "window_start": window_start
        })
        
        # 执行方法
        allowed, cooldown = await token_repository.rate_limit_check(
            action, identifier, max_attempts, window_seconds
        )
        
        # 验证结果
        assert allowed is True
        assert cooldown is None
        
        # 验证Redis操作
        mock_redis.get.assert_called_once_with(f"auth:rate_limit:{action}:{identifier}")
        mock_redis.setex.assert_called_once()  # 更新值
    
    @pytest.mark.asyncio
    async def test_rate_limit_check_exceeded(self, token_repository, mock_redis):
        """测试速率限制检查（超出限制）"""
        # 准备测试数据
        action = "login"
        identifier = "127.0.0.1"
        max_attempts = 5
        window_seconds = 300
        current_attempts = 6  # 超过最大尝试次数
        window_start = int(datetime.now().timestamp()) - 60  # 1分钟前
        
        # 模拟Redis操作
        mock_redis.get.return_value = json.dumps({
            "attempts": current_attempts,
            "window_start": window_start
        })
        
        # 执行方法
        allowed, cooldown = await token_repository.rate_limit_check(
            action, identifier, max_attempts, window_seconds
        )
        
        # 验证结果
        assert allowed is False  # 超出限制，不允许操作
        assert cooldown is not None  # 有冷却时间
        
        # 验证Redis操作
        mock_redis.get.assert_called_once_with(f"auth:rate_limit:{action}:{identifier}")
        mock_redis.setex.assert_not_called()  # 不更新值
    
    @pytest.mark.asyncio
    async def test_rate_limit_check_window_expired(self, token_repository, mock_redis):
        """测试速率限制检查（窗口已过期）"""
        # 准备测试数据
        action = "login"
        identifier = "127.0.0.1"
        max_attempts = 5
        window_seconds = 300
        current_attempts = 10  # 超过最大尝试次数
        window_start = int(datetime.now().timestamp()) - window_seconds - 10  # 窗口已过期
        
        # 模拟Redis操作
        mock_redis.get.return_value = json.dumps({
            "attempts": current_attempts,
            "window_start": window_start
        })
        
        # 执行方法
        allowed, cooldown = await token_repository.rate_limit_check(
            action, identifier, max_attempts, window_seconds
        )
        
        # 验证结果
        assert allowed is True  # 窗口已过期，允许操作
        assert cooldown is None  # 没有冷却时间
        
        # 验证Redis操作
        mock_redis.get.assert_called_once_with(f"auth:rate_limit:{action}:{identifier}")
        mock_redis.setex.assert_called_once()  # 重置窗口
    
    @pytest.mark.asyncio
    async def test_rate_limit_check_error(self, token_repository, mock_redis):
        """测试速率限制检查错误"""
        # 准备测试数据
        action = "login"
        identifier = "user123"
        max_attempts = 5
        window_seconds = 60
        
        # 模拟Redis操作异常
        mock_redis.get.side_effect = Exception("Redis连接错误")
        
        # 执行方法，期望抛出异常
        with pytest.raises(DatabaseError):
            await token_repository.rate_limit_check(action, identifier, max_attempts, window_seconds)
            
    @pytest.mark.asyncio
    async def test_create_refresh_token(self, token_repository, mock_session):
        """测试创建刷新令牌"""
        # 准备测试数据
        user_id = str(uuid.uuid4())
        client_id = "test_client"
        client_info = {"device": "browser", "ip": "127.0.0.1"}
        expires_days = 30
        
        # 模拟数据库操作
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (
            uuid.uuid4(),  # id
            user_id,       # user_id
            "token_value", # token_value
            datetime.now(UTC) + timedelta(days=expires_days), # expires_at
            datetime.now(UTC) # created_at
        )
        mock_session.execute.return_value = mock_result
        
        # 模拟store_token_data
        token_repository.store_token_data = AsyncMock(return_value=True)
        
        # 执行方法
        result = await token_repository.create_refresh_token(
            user_id, client_id, client_info, expires_days
        )
        
        # 验证结果
        assert isinstance(result, dict)
        assert "token_value" in result
        assert "expires_at" in result
        assert "expires_in" in result
        
        # 验证数据库操作
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()
        
        # 验证Redis操作
        token_repository.store_token_data.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_get_refresh_token(self, token_repository, mock_session):
        """测试获取刷新令牌"""
        # 准备测试数据
        token_value = "test_token"
        expected_token = MagicMock()
        
        # 模拟数据库操作
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = expected_token
        mock_session.execute.return_value = mock_result
        
        # 执行方法
        result = await token_repository.get_refresh_token(token_value)
        
        # 验证结果
        assert result == expected_token
        
        # 验证数据库操作
        mock_session.execute.assert_called_once()