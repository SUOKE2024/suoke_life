"""
test_auth_enhanced - 索克生活项目模块
"""

        from auth_service.core.oauth import OAuthService
        import re
        import time
        import urllib.parse
from auth_service.cmd.server.main import create_app
from auth_service.core.auth import AuthService
from auth_service.models.auth import LoginResult
from auth_service.models.user import User, UserStatus, UserSession
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import Mock, patch, AsyncMock
import asyncio
import pytest

"""
Auth Service 增强测试
专注于提升测试覆盖率，覆盖边界情况和异常处理
"""




class TestAuthServiceEnhanced:
    """认证服务增强测试"""
    
    @pytest.fixture
    def auth_service(self):
        return AuthService()
    
    def test_password_hashing_consistency(self, auth_service):
        """测试密码哈希一致性"""
        password = "TestPassword123!"
        
        # 多次哈希同一密码应该产生不同的哈希值（因为盐值不同）
        hash1 = auth_service.get_password_hash(password)
        hash2 = auth_service.get_password_hash(password)
        
        assert hash1 != hash2
        # 但都应该能验证原密码
        assert auth_service.verify_password(password, hash1)
        assert auth_service.verify_password(password, hash2)
    
    def test_jwt_token_with_custom_expiration(self, auth_service):
        """测试自定义过期时间的JWT令牌"""
        data = {"sub": "user123", "username": "testuser"}
        custom_delta = timedelta(minutes=30)
        
        token = auth_service.create_access_token(data, custom_delta)
        payload = auth_service.verify_token(token)
        
        assert payload is not None
        # 验证过期时间设置正确
        exp_time = datetime.fromtimestamp(payload["exp"])
        expected_exp = datetime.utcnow() + custom_delta
        # 允许1秒的误差
        assert abs((exp_time - expected_exp).total_seconds()) < 1
    
    def test_jwt_token_invalid_signature(self, auth_service):
        """测试无效签名的JWT令牌"""
        data = {"sub": "user123", "username": "testuser"}
        token = auth_service.create_access_token(data)
        
        # 篡改令牌最后几个字符
        tampered_token = token[:-10] + "tampered123"
        
        # 验证篡改的令牌应该失败
        payload = auth_service.verify_token(tampered_token)
        assert payload is None
    
    def test_mfa_secret_format(self, auth_service):
        """测试MFA密钥格式"""
        secret = auth_service.generate_mfa_secret()
        
        # Base32编码只包含A-Z和2-7
        assert re.match(r'^[A-Z2-7]+$', secret)
        assert len(secret) == 32
    
    def test_mfa_qr_code_url_components(self, auth_service):
        """测试MFA二维码URL组件"""
        secret = "JBSWY3DPEHPK3PXP"
        email = "test@example.com"
        
        url = auth_service.get_mfa_qr_code_url(email, secret)
        
        # 验证URL格式
        assert url.startswith("otpauth://totp/")
        assert f"secret={secret}" in url
        assert f"issuer={auth_service.settings.security.mfa_issuer_name}" in url
        
        # 验证URL编码
        parsed = urllib.parse.urlparse(url)
        assert parsed.scheme == "otpauth"
        assert parsed.netloc == "totp"
    
    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, auth_service):
        """测试认证不存在的用户"""
        mock_db = AsyncMock()
        mock_repo = AsyncMock()
        mock_repo.get_by_username_or_email.return_value = None
        
        with patch('auth_service.repositories.user_repository.UserRepository', return_value=mock_repo):
            user, result = await auth_service.authenticate_user(
                mock_db, "nonexistent", "password"
            )
        
        assert user is None
        assert result == LoginResult.FAILED_INVALID_CREDENTIALS
    
    @pytest.mark.asyncio
    async def test_authenticate_user_inactive_status(self, auth_service):
        """测试认证非活跃状态用户"""
        mock_db = AsyncMock()
        mock_repo = AsyncMock()
        
        inactive_user = Mock()
        inactive_user.is_active_user.return_value = False
        inactive_user.is_locked.return_value = False
        
        mock_repo.get_by_username_or_email.return_value = inactive_user
        
        with patch('auth_service.repositories.user_repository.UserRepository', return_value=mock_repo):
            user, result = await auth_service.authenticate_user(
                mock_db, "inactive_user", "password"
            )
        
        assert user is None
        assert result == LoginResult.FAILED_ACCOUNT_DISABLED
    
    @pytest.mark.asyncio
    async def test_create_user_session_with_all_params(self, auth_service):
        """测试创建包含所有参数的用户会话"""
        mock_db = AsyncMock()
        mock_user = Mock()
        mock_user.id = "user123"
        mock_user.username = "testuser"
        
        mock_session_repo = AsyncMock()
        mock_session = Mock()
        mock_session_repo.create_session.return_value = mock_session
        
        with patch('auth_service.repositories.session_repository.SessionRepository', return_value=mock_session_repo):
            session = await auth_service.create_user_session(
                db=mock_db,
                user=mock_user,
                device_id="device123",
                device_name="iPhone 15",
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0)",
                ip_address="192.168.1.100"
            )
        
        # 验证会话创建参数
        call_args = mock_session_repo.create_session.call_args
        assert call_args.kwargs["user_id"] == "user123"
        assert call_args.kwargs["device_id"] == "device123"
        assert call_args.kwargs["device_name"] == "iPhone 15"
        assert call_args.kwargs["user_agent"] == "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0)"
        assert call_args.kwargs["ip_address"] == "192.168.1.100"
        assert "session_token" in call_args.kwargs
        assert "refresh_token" in call_args.kwargs
        assert "expires_at" in call_args.kwargs
    
    def test_password_strength_edge_cases(self, auth_service):
        """测试密码强度验证边界情况"""
        # 空密码
        valid, message = auth_service.validate_password_strength("")
        assert valid is False
        
        # 只有空格的密码
        valid, message = auth_service.validate_password_strength("        ")
        assert valid is False
        
        # 刚好达到最小长度
        min_length = auth_service.settings.security.password_min_length
        password = "A1!" + "a" * (min_length - 3)
        valid, message = auth_service.validate_password_strength(password)
        assert valid is True
        
        # 包含Unicode字符
        valid, message = auth_service.validate_password_strength("密码123!Abc")
        # 应该根据配置决定是否接受Unicode字符
        # 这里假设接受
        assert valid is True
    
    def test_refresh_token_uniqueness(self, auth_service):
        """测试刷新令牌唯一性"""
        tokens = set()
        for _ in range(100):
            token = auth_service.create_refresh_token()
            assert token not in tokens
            tokens.add(token)
    
    def test_jwt_token_claims_validation(self, auth_service):
        """测试JWT令牌声明验证"""
        data = {"sub": "user123", "username": "testuser", "custom_claim": "value"}
        token = auth_service.create_access_token(data)
        
        payload = auth_service.verify_token(token)
        
        # 验证标准声明
        assert payload["sub"] == "user123"
        assert payload["username"] == "testuser"
        assert payload["custom_claim"] == "value"
        assert payload["iss"] == auth_service.settings.jwt.issuer
        assert payload["aud"] == auth_service.settings.jwt.audience
        
        # 验证时间声明
        now = datetime.utcnow().timestamp()
        assert payload["iat"] <= now
        assert payload["exp"] > now


class TestAuthAPIEnhanced:
    """认证API增强测试"""
    
    @pytest.fixture
    def client(self):
        app = create_app()
        return TestClient(app)
    
    def test_login_endpoint_validation_errors(self, client):
        """测试登录端点验证错误"""
        # 缺少用户名
        response = client.post("/api/v1/auth/login", json={
            "password": "password123"
        })
        assert response.status_code == 422
        
        # 缺少密码
        response = client.post("/api/v1/auth/login", json={
            "username": "testuser"
        })
        assert response.status_code == 422
        
        # 空用户名
        response = client.post("/api/v1/auth/login", json={
            "username": "",
            "password": "password123"
        })
        assert response.status_code == 422
        
        # 空密码
        response = client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": ""
        })
        assert response.status_code == 422
    
    def test_login_endpoint_with_device_info(self, client):
        """测试带设备信息的登录端点"""
        with patch('auth_service.api.rest.endpoints.auth.get_auth_service') as mock_get_service:
            mock_service = Mock()
            mock_user = Mock()
            mock_user.id = "user123"
            mock_user.username = "testuser"
            
            mock_session = Mock()
            mock_session.session_token = "access_token"
            mock_session.refresh_token = "refresh_token"
            
            mock_service.authenticate_user.return_value = (mock_user, LoginResult.SUCCESS)
            mock_service.create_user_session.return_value = mock_session
            mock_service.settings.jwt.access_token_expire_minutes = 60
            
            mock_get_service.return_value = mock_service
            
            with patch('auth_service.api.rest.endpoints.auth.get_db'):
                with patch('auth_service.repositories.user_repository.UserRepository'):
                    response = client.post("/api/v1/auth/login", json={
                        "username": "testuser",
                        "password": "password123",
                        "device_id": "device123",
                        "device_name": "iPhone 15"
                    })
            
            assert response.status_code == 200
            # 验证设备信息被传递
            mock_service.create_user_session.assert_called_once()
            call_args = mock_service.create_user_session.call_args
            assert call_args.kwargs.get("device_id") == "device123"
            assert call_args.kwargs.get("device_name") == "iPhone 15"
    
    def test_refresh_token_endpoint_expired_session(self, client):
        """测试刷新令牌端点过期会话"""
        with patch('auth_service.api.rest.endpoints.auth.get_db'):
            with patch('auth_service.repositories.session_repository.SessionRepository') as mock_repo_class:
                mock_repo = Mock()
                mock_session = Mock()
                mock_session.is_valid.return_value = False  # 会话已过期
                
                mock_repo.get_by_refresh_token.return_value = mock_session
                mock_repo_class.return_value = mock_repo
                
                with patch('auth_service.api.rest.endpoints.auth.get_auth_service'):
                    response = client.post("/api/v1/auth/refresh", json={
                        "refresh_token": "expired_refresh_token"
                    })
                
                assert response.status_code == 401
                assert "无效的刷新令牌" in response.json()["detail"]
    
    def test_logout_endpoint_all_devices(self, client):
        """测试登出所有设备端点"""
        with patch('auth_service.api.rest.endpoints.auth.security') as mock_security:
            mock_credentials = Mock()
            mock_credentials.credentials = "valid_token"
            mock_security.return_value = mock_credentials
            
            with patch('auth_service.api.rest.endpoints.auth.get_auth_service') as mock_get_service:
                mock_service = Mock()
                mock_service.verify_token.return_value = {"sub": "user123"}
                mock_get_service.return_value = mock_service
                
                with patch('auth_service.api.rest.endpoints.auth.get_db'):
                    with patch('auth_service.repositories.session_repository.SessionRepository') as mock_repo_class:
                        mock_repo = Mock()
                        mock_repo_class.return_value = mock_repo
                        
                        response = client.post("/api/v1/auth/logout", 
                                             json={"all_devices": True},
                                             headers={"Authorization": "Bearer valid_token"})
                
                assert response.status_code == 200
                mock_repo.deactivate_user_sessions.assert_called_once_with("user123")
    
    def test_health_check_endpoint(self, client):
        """测试健康检查端点"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "auth-service"
    
    def test_root_endpoint(self, client):
        """测试根端点"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert "status" in data


class TestOAuthEnhanced:
    """OAuth功能增强测试"""
    
    def test_oauth_state_generation(self):
        """测试OAuth状态参数生成"""
        
        oauth_service = OAuthService()
        state1 = oauth_service.generate_state()
        state2 = oauth_service.generate_state()
        
        assert state1 != state2
        assert len(state1) >= 32
        assert len(state2) >= 32
    
    def test_oauth_authorization_url(self):
        """测试OAuth授权URL生成"""
        
        oauth_service = OAuthService()
        
        # 测试Google OAuth
        url = oauth_service.get_authorization_url("google", "test_state")
        assert "accounts.google.com" in url
        assert "state=test_state" in url
        assert "client_id=" in url
        assert "redirect_uri=" in url
        assert "scope=" in url


class TestSecurityEnhanced:
    """安全功能增强测试"""
    
    @pytest.fixture
    def auth_service(self):
        return AuthService()
    
    def test_timing_attack_resistance(self, auth_service):
        """测试时序攻击抵抗性"""
        
        password = "TestPassword123!"
        correct_hash = auth_service.get_password_hash(password)
        
        # 测试正确密码验证时间
        start_time = time.time()
        result1 = auth_service.verify_password(password, correct_hash)
        time1 = time.time() - start_time
        
        # 测试错误密码验证时间
        start_time = time.time()
        result2 = auth_service.verify_password("WrongPassword", correct_hash)
        time2 = time.time() - start_time
        
        assert result1 is True
        assert result2 is False
        
        # 验证时间差异不应该太大（防止时序攻击）
        # 注意：这个测试可能在不同环境下不稳定
        time_diff = abs(time1 - time2)
        assert time_diff < 0.1  # 100ms内的差异是可接受的
    
    def test_password_hash_salt_uniqueness(self, auth_service):
        """测试密码哈希盐值唯一性"""
        password = "TestPassword123!"
        hashes = set()
        
        # 生成多个哈希值
        for _ in range(10):
            hash_value = auth_service.get_password_hash(password)
            assert hash_value not in hashes
            hashes.add(hash_value)
            # 验证每个哈希都能正确验证原密码
            assert auth_service.verify_password(password, hash_value)
    
    def test_jwt_token_replay_attack_prevention(self, auth_service):
        """测试JWT令牌重放攻击防护"""
        data = {"sub": "user123", "username": "testuser"}
        
        # 创建短期令牌
        short_delta = timedelta(seconds=1)
        token = auth_service.create_access_token(data, short_delta)
        
        # 立即验证应该成功
        payload = auth_service.verify_token(token)
        assert payload is not None
        
        # 等待令牌过期
        time.sleep(2)
        
        # 过期后验证应该失败
        payload = auth_service.verify_token(token)
        assert payload is None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=auth_service", "--cov-report=html"]) 