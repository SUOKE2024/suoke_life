#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
认证服务单元测试

测试认证服务的核心功能，包括：
- 密码验证和哈希
- 令牌生成和验证
- 用户认证
- 多因素认证
"""
import os
import uuid
import pytest
import jwt
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock

from sqlalchemy.ext.asyncio import AsyncSession

from internal.service import auth_service
from internal.model.user import User, RefreshToken, AuditLog, MFATypeEnum, UserStatusEnum
from internal.repository.user_repository import UserRepository
from internal.repository.token_repository import TokenRepository
from internal.repository.audit_repository import AuditRepository

# 测试数据
TEST_USER_ID = uuid.uuid4()
TEST_USERNAME = "testuser"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "Password123!"
TEST_PASSWORD_HASH = "$2b$12$qP/wLKMjnQcCK0UU9yZMzehA1GG/zj3QREgAZczFiYS6Ur3UOgJP."


@pytest.fixture
def mock_session():
    """模拟数据库会话"""
    session = AsyncMock(spec=AsyncSession)
    return session


@pytest.fixture
def mock_user():
    """创建模拟用户"""
    user = MagicMock(spec=User)
    user.id = TEST_USER_ID
    user.username = TEST_USERNAME
    user.email = TEST_EMAIL
    user.password_hash = TEST_PASSWORD_HASH
    user.status = UserStatusEnum.ACTIVE
    user.roles = []
    user.mfa_enabled = False
    user.mfa_type = MFATypeEnum.NONE
    user.mfa_secret = None
    user.last_login = None
    return user


@pytest.fixture
def mock_refresh_token():
    """创建模拟刷新令牌"""
    token = MagicMock(spec=RefreshToken)
    token.id = uuid.uuid4()
    token.user_id = TEST_USER_ID
    token.token = str(uuid.uuid4())
    token.expires_at = datetime.utcnow() + timedelta(days=30)
    token.revoked = False
    token.created_at = datetime.utcnow()
    return token


@pytest.fixture
def mock_repositories(mock_session, mock_user, mock_refresh_token):
    """设置模拟仓库"""
    with patch("internal.service.auth_service.UserRepository") as mock_user_repo_class:
        with patch("internal.service.auth_service.TokenRepository") as mock_token_repo_class:
            with patch("internal.service.auth_service.AuditRepository") as mock_audit_repo_class:
                # 设置UserRepository
                mock_user_repo = AsyncMock(spec=UserRepository)
                mock_user_repo.get_user_by_id.return_value = mock_user
                mock_user_repo.get_user_by_username.return_value = mock_user
                mock_user_repo.get_user_by_email.return_value = mock_user
                mock_user_repo.update_password.return_value = True
                mock_user_repo.update_mfa_settings.return_value = True
                
                mock_user_repo_class.return_value = mock_user_repo
                
                # 设置TokenRepository
                mock_token_repo = AsyncMock(spec=TokenRepository)
                mock_token_repo.create_refresh_token.return_value = mock_refresh_token
                mock_token_repo.get_refresh_token.return_value = mock_refresh_token
                mock_token_repo.revoke_all_user_tokens.return_value = True
                
                mock_token_repo_class.return_value = mock_token_repo
                
                # 设置AuditRepository
                mock_audit_repo = AsyncMock(spec=AuditRepository)
                mock_audit_repo.add_login_attempt.return_value = True
                mock_audit_repo.add_audit_log.return_value = True
                mock_audit_repo.get_recent_failed_attempts.return_value = []
                
                mock_audit_repo_class.return_value = mock_audit_repo
                
                yield {
                    "user_repo": mock_user_repo,
                    "token_repo": mock_token_repo,
                    "audit_repo": mock_audit_repo
                }


class TestPasswordHashing:
    """密码哈希测试"""
    
    @pytest.mark.asyncio
    async def test_verify_password_success(self):
        """测试正确密码验证"""
        # 使用真实的密码哈希函数（较慢但更安全）
        hashed = await auth_service.get_password_hash(TEST_PASSWORD)
        result = await auth_service.verify_password(TEST_PASSWORD, hashed)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_verify_password_failure(self):
        """测试错误密码验证"""
        # 使用真实的密码哈希函数
        hashed = await auth_service.get_password_hash(TEST_PASSWORD)
        result = await auth_service.verify_password("WrongPassword123!", hashed)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_password_hash_strength(self):
        """测试密码哈希强度"""
        # 验证生成的哈希使用bcrypt
        hashed = await auth_service.get_password_hash(TEST_PASSWORD)
        assert hashed.startswith("$2b$")
        
        # 测试相同密码产生不同哈希（盐值随机）
        hashed2 = await auth_service.get_password_hash(TEST_PASSWORD)
        assert hashed != hashed2


class TestTokenManagement:
    """令牌管理测试"""
    
    @pytest.mark.asyncio
    async def test_create_access_token(self):
        """测试创建访问令牌"""
        data = {"sub": str(TEST_USER_ID), "username": TEST_USERNAME}
        token = await auth_service.create_access_token(data)
        
        # 验证令牌格式
        assert isinstance(token, str)
        assert len(token.split(".")) == 3  # JWT格式: header.payload.signature
        
        # 解码验证
        payload = jwt.decode(token, auth_service.SECRET_KEY, algorithms=[auth_service.ALGORITHM])
        assert payload["sub"] == str(TEST_USER_ID)
        assert payload["username"] == TEST_USERNAME
        assert "exp" in payload
    
    @pytest.mark.asyncio
    async def test_create_access_token_with_expiry(self):
        """测试带自定义过期时间的访问令牌"""
        data = {"sub": str(TEST_USER_ID)}
        custom_expiry = timedelta(minutes=5)
        token = await auth_service.create_access_token(data, custom_expiry)
        
        # 解码验证
        payload = jwt.decode(token, auth_service.SECRET_KEY, algorithms=[auth_service.ALGORITHM])
        
        # 验证过期时间（允许1秒的误差）
        expected_exp = datetime.utcnow() + custom_expiry
        actual_exp = datetime.fromtimestamp(payload["exp"])
        assert abs((actual_exp - expected_exp).total_seconds()) < 1
    
    @pytest.mark.asyncio
    async def test_create_refresh_token(self, mock_session, mock_repositories):
        """测试创建刷新令牌"""
        token_value, expires_at = await auth_service.create_refresh_token(TEST_USER_ID, mock_session)
        
        # 验证令牌格式
        assert isinstance(token_value, str)
        assert isinstance(expires_at, datetime)
        
        # 验证过期时间
        expected_expire = datetime.utcnow() + timedelta(days=auth_service.REFRESH_TOKEN_EXPIRE_DAYS)
        assert abs((expires_at - expected_expire).total_seconds()) < 1
        
        # 验证仓库调用
        mock_repositories["token_repo"].create_refresh_token.assert_called_once()
        args, _ = mock_repositories["token_repo"].create_refresh_token.call_args
        assert args[0] == TEST_USER_ID
        assert args[1] == token_value
    
    @pytest.mark.asyncio
    async def test_create_tokens(self, mock_session, mock_user, mock_repositories):
        """测试创建访问和刷新令牌"""
        result = await auth_service.create_tokens(mock_user, mock_session)
        
        # 验证返回格式
        assert result.access_token is not None
        assert result.refresh_token is not None
        assert result.token_type == "bearer"
        assert result.expires_in == auth_service.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        assert result.refresh_expires_in == auth_service.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        
        # 验证访问令牌内容
        payload = jwt.decode(result.access_token, auth_service.SECRET_KEY, algorithms=[auth_service.ALGORITHM])
        assert payload["sub"] == str(TEST_USER_ID)
        assert payload["username"] == TEST_USERNAME
        
        # 验证仓库调用
        mock_repositories["token_repo"].create_refresh_token.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_verify_token_success(self, mock_session, mock_user, mock_repositories):
        """测试成功验证令牌"""
        # 创建有效令牌
        data = {"sub": str(TEST_USER_ID), "username": TEST_USERNAME}
        token = await auth_service.create_access_token(data)
        
        # 验证令牌
        result = await auth_service.verify_token(token, mock_session)
        
        # 验证结果
        assert result["id"] == str(TEST_USER_ID)
        assert result["username"] == TEST_USERNAME
        assert result["email"] == TEST_EMAIL
        
        # 验证仓库调用
        mock_repositories["user_repo"].get_user_by_id.assert_called_once_with(str(TEST_USER_ID))
    
    @pytest.mark.asyncio
    async def test_verify_token_invalid(self, mock_session):
        """测试无效令牌验证"""
        with pytest.raises(ValueError, match="令牌验证失败"):
            await auth_service.verify_token("invalid.token.string", mock_session)
    
    @pytest.mark.asyncio
    async def test_verify_token_expired(self, mock_session):
        """测试过期令牌验证"""
        # 创建已过期令牌
        data = {"sub": str(TEST_USER_ID), "exp": datetime.utcnow() - timedelta(hours=1)}
        token = jwt.encode(data, auth_service.SECRET_KEY, algorithm=auth_service.ALGORITHM)
        
        with pytest.raises(ValueError, match="令牌验证失败"):
            await auth_service.verify_token(token, mock_session)


class TestUserAuthentication:
    """用户认证测试"""
    
    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, mock_session, mock_user, mock_repositories):
        """测试成功认证用户"""
        # 模拟密码验证
        with patch("internal.service.auth_service.verify_password", return_value=True):
            result = await auth_service.authenticate_user(TEST_USERNAME, TEST_PASSWORD, mock_session)
            
            # 验证结果
            assert result == mock_user
            
            # 验证仓库调用
            mock_repositories["user_repo"].get_user_by_username.assert_called_once_with(TEST_USERNAME)
            mock_repositories["audit_repo"].add_login_attempt.assert_called_once()
            mock_session.commit.assert_called_once()  # 更新最后登录时间
    
    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, mock_session, mock_repositories):
        """测试密码错误认证"""
        # 模拟密码验证失败
        with patch("internal.service.auth_service.verify_password", return_value=False):
            result = await auth_service.authenticate_user(TEST_USERNAME, "WrongPassword", mock_session)
            
            # 验证结果
            assert result is None
            
            # 验证仓库调用
            mock_repositories["audit_repo"].add_login_attempt.assert_called_once()
            mock_repositories["audit_repo"].get_recent_failed_attempts.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_authenticate_user_account_locked_after_failures(self, mock_session, mock_user, mock_repositories):
        """测试多次失败后锁定账户"""
        # 模拟多次失败尝试
        mock_repositories["audit_repo"].get_recent_failed_attempts.return_value = [
            MagicMock(spec=AuditLog) for _ in range(5)
        ]
        
        # 模拟密码验证失败
        with patch("internal.service.auth_service.verify_password", return_value=False):
            result = await auth_service.authenticate_user(TEST_USERNAME, "WrongPassword", mock_session)
            
            # 验证结果
            assert result is None
            
            # 验证用户状态被更新为锁定
            assert mock_user.status == UserStatusEnum.LOCKED
            mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_authenticate_user_nonexistent(self, mock_session, mock_repositories):
        """测试不存在用户认证"""
        # 模拟用户不存在
        mock_repositories["user_repo"].get_user_by_username.return_value = None
        
        result = await auth_service.authenticate_user("nonexistent", TEST_PASSWORD, mock_session)
        
        # 验证结果
        assert result is None
        
        # 验证仓库调用
        mock_repositories["user_repo"].get_user_by_username.assert_called_once_with("nonexistent")
        mock_repositories["audit_repo"].add_login_attempt.assert_called_once_with(None, "0.0.0.0", False)
    
    @pytest.mark.asyncio
    async def test_authenticate_user_inactive(self, mock_session, mock_user, mock_repositories):
        """测试非活跃用户认证"""
        # 设置用户为已锁定状态
        mock_user.status = UserStatusEnum.LOCKED
        
        # 模拟密码验证成功
        with patch("internal.service.auth_service.verify_password", return_value=True):
            result = await auth_service.authenticate_user(TEST_USERNAME, TEST_PASSWORD, mock_session)
            
            # 验证结果
            assert result is None


class TestMultiFactorAuth:
    """多因素认证测试"""
    
    @pytest.mark.asyncio
    async def test_setup_totp_mfa(self, mock_session, mock_user, mock_repositories):
        """测试设置TOTP多因素认证"""
        # 调用设置MFA
        with patch("internal.service.auth_service.pyotp.random_base32", return_value="TESTSECRETKEY"):
            with patch("internal.service.auth_service.qrcode.QRCode"):
                result = await auth_service.setup_mfa(mock_user, "totp", mock_session)
        
        # 验证结果
        assert result.type == "totp"
        assert result.secret == "TESTSECRETKEY"
        assert result.qr_code is not None
        assert result.success is True
        
        # 验证仓库调用
        mock_repositories["user_repo"].update_mfa_settings.assert_called_once_with(
            user_id=str(TEST_USER_ID),
            mfa_enabled=True,
            mfa_type=MFATypeEnum.TOTP,
            mfa_secret="TESTSECRETKEY"
        )
    
    @pytest.mark.asyncio
    async def test_verify_totp_mfa_success(self, mock_user):
        """测试验证TOTP多因素认证成功"""
        # 设置用户MFA
        mock_user.mfa_enabled = True
        mock_user.mfa_type = MFATypeEnum.TOTP
        mock_user.mfa_secret = "TESTSECRETKEY"
        
        # 模拟TOTP验证成功
        with patch("internal.service.auth_service.pyotp.TOTP") as mock_totp:
            mock_totp_instance = mock_totp.return_value
            mock_totp_instance.verify.return_value = True
            
            result = await auth_service.verify_mfa(mock_user, "123456")
            
            # 验证结果
            assert result is True
            mock_totp.assert_called_once_with("TESTSECRETKEY")
            mock_totp_instance.verify.assert_called_once_with("123456")
    
    @pytest.mark.asyncio
    async def test_verify_totp_mfa_failure(self, mock_user):
        """测试验证TOTP多因素认证失败"""
        # 设置用户MFA
        mock_user.mfa_enabled = True
        mock_user.mfa_type = MFATypeEnum.TOTP
        mock_user.mfa_secret = "TESTSECRETKEY"
        
        # 模拟TOTP验证失败
        with patch("internal.service.auth_service.pyotp.TOTP") as mock_totp:
            mock_totp_instance = mock_totp.return_value
            mock_totp_instance.verify.return_value = False
            
            result = await auth_service.verify_mfa(mock_user, "wrong_code")
            
            # 验证结果
            assert result is False
    
    @pytest.mark.asyncio
    async def test_verify_mfa_not_enabled(self, mock_user):
        """测试未启用MFA的验证"""
        # 设置用户MFA未启用
        mock_user.mfa_enabled = False
        mock_user.mfa_type = MFATypeEnum.NONE
        
        with pytest.raises(ValueError, match="未启用多因素认证"):
            await auth_service.verify_mfa(mock_user, "123456")
    
    @pytest.mark.asyncio
    async def test_disable_mfa(self, mock_session, mock_user, mock_repositories):
        """测试禁用多因素认证"""
        # 设置用户MFA
        mock_user.mfa_enabled = True
        mock_user.mfa_type = MFATypeEnum.TOTP
        mock_user.mfa_secret = "TESTSECRETKEY"
        
        result = await auth_service.disable_mfa(mock_user, mock_session)
        
        # 验证结果
        assert result is True
        
        # 验证仓库调用
        mock_repositories["user_repo"].update_mfa_settings.assert_called_once_with(
            user_id=str(TEST_USER_ID),
            mfa_enabled=False,
            mfa_type=MFATypeEnum.NONE,
            mfa_secret=None
        )
        mock_repositories["audit_repo"].add_audit_log.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_disable_mfa_not_enabled(self, mock_session, mock_user):
        """测试禁用未启用的MFA"""
        # 设置用户MFA未启用
        mock_user.mfa_enabled = False
        mock_user.mfa_type = MFATypeEnum.NONE
        
        with pytest.raises(ValueError, match="多因素认证未启用"):
            await auth_service.disable_mfa(mock_user, mock_session)


class TestPasswordReset:
    """密码重置测试"""
    
    @pytest.mark.asyncio
    async def test_send_password_reset_success(self, mock_session, mock_repositories):
        """测试发送密码重置邮件成功"""
        with patch("internal.service.auth_service.create_access_token") as mock_create_token:
            mock_create_token.return_value = "test_reset_token"
            
            result = await auth_service.send_password_reset(TEST_EMAIL, mock_session)
            
            # 验证结果
            assert result is True
            
            # 验证查找用户
            mock_repositories["user_repo"].get_user_by_email.assert_called_once_with(TEST_EMAIL)
            
            # 验证创建令牌
            token_data = {
                "sub": str(TEST_USER_ID),
                "type": "password_reset",
            }
            mock_create_token.assert_called_once()
            args, kwargs = mock_create_token.call_args
            assert args[0] == token_data
            assert isinstance(kwargs["expires_delta"], timedelta)
    
    @pytest.mark.asyncio
    async def test_send_password_reset_nonexistent_user(self, mock_session, mock_repositories):
        """测试发送密码重置邮件给不存在用户"""
        # 模拟用户不存在
        mock_repositories["user_repo"].get_user_by_email.return_value = None
        
        result = await auth_service.send_password_reset("nonexistent@example.com", mock_session)
        
        # 验证结果 - 返回成功以不暴露用户是否存在
        assert result is True
        
        # 验证查找用户
        mock_repositories["user_repo"].get_user_by_email.assert_called_once_with("nonexistent@example.com")
    
    @pytest.mark.asyncio
    async def test_reset_password_success(self, mock_session, mock_repositories):
        """测试密码重置成功"""
        # 创建有效重置令牌
        token_data = {
            "sub": str(TEST_USER_ID),
            "type": "password_reset",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(token_data, auth_service.SECRET_KEY, algorithm=auth_service.ALGORITHM)
        
        # 模拟密码哈希
        with patch("internal.service.auth_service.get_password_hash", return_value="new_password_hash"):
            result = await auth_service.reset_password(token, "NewPassword123!", mock_session)
            
            # 验证结果
            assert result is True
            
            # 验证更新密码
            mock_repositories["user_repo"].update_password.assert_called_once_with(
                str(TEST_USER_ID), "new_password_hash"
            )
            
            # 验证吊销所有令牌
            mock_repositories["token_repo"].revoke_all_user_tokens.assert_called_once_with(TEST_USER_ID)
    
    @pytest.mark.asyncio
    async def test_reset_password_invalid_token(self, mock_session):
        """测试无效令牌密码重置"""
        with pytest.raises(ValueError, match="无效或已过期的令牌"):
            await auth_service.reset_password("invalid.token", "NewPassword123!", mock_session)
    
    @pytest.mark.asyncio
    async def test_reset_password_wrong_token_type(self, mock_session):
        """测试错误类型令牌密码重置"""
        # 创建错误类型令牌
        token_data = {
            "sub": str(TEST_USER_ID),
            "type": "access_token",  # 应为 password_reset
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(token_data, auth_service.SECRET_KEY, algorithm=auth_service.ALGORITHM)
        
        with pytest.raises(ValueError, match="无效的令牌类型"):
            await auth_service.reset_password(token, "NewPassword123!", mock_session)


class TestLogoutAndAudit:
    """登出和审计测试"""
    
    @pytest.mark.asyncio
    async def test_logout(self, mock_session, mock_user, mock_repositories):
        """测试用户登出"""
        result = await auth_service.logout(mock_user, mock_session)
        
        # 验证结果
        assert result is True
        
        # 验证吊销所有令牌
        mock_repositories["token_repo"].revoke_all_user_tokens.assert_called_once_with(TEST_USER_ID)
    
    @pytest.mark.asyncio
    async def test_log_audit_event(self, mock_session, mock_repositories):
        """测试记录审计日志"""
        await auth_service.log_audit_event(
            user_id=TEST_USER_ID,
            action="test_action",
            resource="test_resource",
            resource_id="123",
            details="测试审计日志",
            ip_address="192.168.1.1",
            user_agent="Test Browser",
            session=mock_session
        )
        
        # 验证调用审计仓库
        mock_repositories["audit_repo"].add_audit_log.assert_called_once_with(
            user_id=TEST_USER_ID,
            action="test_action",
            resource="test_resource",
            resource_id="123",
            details="测试审计日志",
            ip_address="192.168.1.1",
            user_agent="Test Browser"
        )