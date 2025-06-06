"""
test_auth_comprehensive - 索克生活项目模块
"""

from auth_service.cmd.server.main import create_app
from auth_service.core.auth import AuthService
from auth_service.models.auth import LoginResult
from auth_service.models.user import User, UserStatus, UserSession
from auth_service.schemas.auth import LoginRequest, MFAVerifyRequest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import Mock, patch, AsyncMock
import asyncio
import pytest

"""
Auth Service 综合测试
覆盖核心认证逻辑、JWT令牌、MFA、OAuth等功能
"""




class TestAuthService:
    """认证服务核心逻辑测试"""
    
    @pytest.fixture
    def auth_service(self):
        """创建认证服务实例"""
        return AuthService()
    
    @pytest.fixture
    def mock_user(self):
        """创建模拟用户"""
        return User(
            id="test-user-id",
            username="testuser",
            email="test@example.com",
            password_hash="$2b$12$hashed_password",
            status=UserStatus.ACTIVE,
            is_verified=True,
            mfa_enabled=False,
            failed_login_attempts=0,
            locked_until=None
        )
    
    def test_password_verification(self, auth_service):
        """测试密码验证"""
        password = "TestPassword123!"
        hashed = auth_service.get_password_hash(password)
        
        # 正确密码验证
        assert auth_service.verify_password(password, hashed) is True
        
        # 错误密码验证
        assert auth_service.verify_password("WrongPassword", hashed) is False
    
    def test_password_strength_validation(self, auth_service):
        """测试密码强度验证"""
        # 强密码
        valid, message = auth_service.validate_password_strength("StrongPass123!")
        assert valid is True
        
        # 弱密码 - 太短
        valid, message = auth_service.validate_password_strength("123")
        assert valid is False
        assert "长度" in message
        
        # 弱密码 - 缺少大写字母
        valid, message = auth_service.validate_password_strength("weakpass123!")
        assert valid is False
        assert "大写字母" in message
        
        # 弱密码 - 缺少数字
        valid, message = auth_service.validate_password_strength("WeakPass!")
        assert valid is False
        assert "数字" in message
    
    def test_jwt_token_creation_and_verification(self, auth_service):
        """测试JWT令牌创建和验证"""
        # 创建令牌
        data = {"sub": "user123", "username": "testuser"}
        token = auth_service.create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        
        # 验证令牌
        payload = auth_service.verify_token(token)
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["username"] == "testuser"
        assert "exp" in payload
        assert "iat" in payload
        assert "iss" in payload
        assert "aud" in payload
    
    def test_jwt_token_expiration(self, auth_service):
        """测试JWT令牌过期"""
        # 创建已过期的令牌
        data = {"sub": "user123", "username": "testuser"}
        expired_delta = timedelta(seconds=-1)
        token = auth_service.create_access_token(data, expired_delta)
        
        # 验证过期令牌
        payload = auth_service.verify_token(token)
        assert payload is None
    
    def test_refresh_token_generation(self, auth_service):
        """测试刷新令牌生成"""
        token1 = auth_service.create_refresh_token()
        token2 = auth_service.create_refresh_token()
        
        assert token1 != token2
        assert len(token1) > 20  # 确保足够长
        assert len(token2) > 20
    
    def test_mfa_secret_generation(self, auth_service):
        """测试MFA密钥生成"""
        secret1 = auth_service.generate_mfa_secret()
        secret2 = auth_service.generate_mfa_secret()
        
        assert secret1 != secret2
        assert len(secret1) == 32  # Base32编码的标准长度
        assert len(secret2) == 32
    
    def test_mfa_qr_code_url(self, auth_service):
        """测试MFA二维码URL生成"""
        secret = "JBSWY3DPEHPK3PXP"
        email = "test@example.com"
        
        url = auth_service.get_mfa_qr_code_url(email, secret)
        
        assert url.startswith("otpauth://totp/")
        assert email in url
        assert secret in url
        assert auth_service.settings.security.mfa_issuer_name in url
    
    @patch('pyotp.TOTP.verify')
    def test_mfa_token_verification(self, mock_verify, auth_service):
        """测试MFA令牌验证"""
        secret = "JBSWY3DPEHPK3PXP"
        token = "123456"
        
        # 模拟验证成功
        mock_verify.return_value = True
        result = auth_service.verify_mfa_token(secret, token)
        assert result is True
        
        # 模拟验证失败
        mock_verify.return_value = False
        result = auth_service.verify_mfa_token(secret, token)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_user_authentication_success(self, auth_service, mock_user):
        """测试用户认证成功"""
        mock_db = AsyncMock()
        mock_repo = AsyncMock()
        
        # 模拟用户仓库
        mock_repo.get_by_username_or_email.return_value = mock_user
        mock_repo.reset_failed_attempts = AsyncMock()
        
        with patch('auth_service.repositories.user_repository.UserRepository', return_value=mock_repo):
            with patch.object(auth_service, 'verify_password', return_value=True):
                user, result = await auth_service.authenticate_user(
                    mock_db, "testuser", "correct_password"
                )
        
        assert user == mock_user
        assert result == LoginResult.SUCCESS
        mock_repo.reset_failed_attempts.assert_called_once_with(mock_user.id)
    
    @pytest.mark.asyncio
    async def test_user_authentication_invalid_credentials(self, auth_service, mock_user):
        """测试用户认证失败 - 无效凭据"""
        mock_db = AsyncMock()
        mock_repo = AsyncMock()
        
        mock_repo.get_by_username_or_email.return_value = mock_user
        mock_repo.increment_failed_attempts = AsyncMock()
        
        with patch('auth_service.repositories.user_repository.UserRepository', return_value=mock_repo):
            with patch.object(auth_service, 'verify_password', return_value=False):
                user, result = await auth_service.authenticate_user(
                    mock_db, "testuser", "wrong_password"
                )
        
        assert user is None
        assert result == LoginResult.FAILED_INVALID_CREDENTIALS
        mock_repo.increment_failed_attempts.assert_called_once_with(mock_user.id)
    
    @pytest.mark.asyncio
    async def test_user_authentication_account_locked(self, auth_service):
        """测试用户认证失败 - 账户锁定"""
        mock_db = AsyncMock()
        mock_repo = AsyncMock()
        
        # 创建被锁定的用户
        locked_user = User(
            id="locked-user-id",
            username="lockeduser",
            email="locked@example.com",
            password_hash="$2b$12$hashed_password",
            status=UserStatus.ACTIVE,
            is_verified=True,
            mfa_enabled=False,
            failed_login_attempts=5,
            locked_until=datetime.utcnow() + timedelta(minutes=30)
        )
        
        mock_repo.get_by_username_or_email.return_value = locked_user
        
        with patch('auth_service.repositories.user_repository.UserRepository', return_value=mock_repo):
            user, result = await auth_service.authenticate_user(
                mock_db, "lockeduser", "any_password"
            )
        
        assert user is None
        assert result == LoginResult.FAILED_ACCOUNT_LOCKED
    
    @pytest.mark.asyncio
    async def test_user_authentication_mfa_required(self, auth_service):
        """测试用户认证 - 需要MFA"""
        mock_db = AsyncMock()
        mock_repo = AsyncMock()
        
        # 创建启用MFA的用户
        mfa_user = User(
            id="mfa-user-id",
            username="mfauser",
            email="mfa@example.com",
            password_hash="$2b$12$hashed_password",
            status=UserStatus.ACTIVE,
            is_verified=True,
            mfa_enabled=True,
            failed_login_attempts=0,
            locked_until=None
        )
        
        mock_repo.get_by_username_or_email.return_value = mfa_user
        mock_repo.reset_failed_attempts = AsyncMock()
        
        with patch('auth_service.repositories.user_repository.UserRepository', return_value=mock_repo):
            with patch.object(auth_service, 'verify_password', return_value=True):
                user, result = await auth_service.authenticate_user(
                    mock_db, "mfauser", "correct_password"
                )
        
        assert user == mfa_user
        assert result == LoginResult.FAILED_MFA_REQUIRED
    
    @pytest.mark.asyncio
    async def test_create_user_session(self, auth_service, mock_user):
        """测试创建用户会话"""
        mock_db = AsyncMock()
        mock_session_repo = AsyncMock()
        
        # 模拟会话创建
        mock_session = UserSession(
            id="session-id",
            user_id=mock_user.id,
            session_token="access_token",
            refresh_token="refresh_token",
            device_id="device123",
            device_name="iPhone",
            user_agent="Mozilla/5.0",
            ip_address="192.168.1.1",
            expires_at=datetime.utcnow() + timedelta(hours=1),
            is_active=True
        )
        
        mock_session_repo.create_session.return_value = mock_session
        
        with patch('auth_service.repositories.session_repository.SessionRepository', return_value=mock_session_repo):
            session = await auth_service.create_user_session(
                db=mock_db,
                user=mock_user,
                device_id="device123",
                device_name="iPhone",
                user_agent="Mozilla/5.0",
                ip_address="192.168.1.1"
            )
        
        assert session == mock_session
        mock_session_repo.create_session.assert_called_once()


class TestAuthAPI:
    """认证API端点测试"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        app = create_app()
        return TestClient(app)
    
    @pytest.fixture
    def mock_auth_service(self):
        """模拟认证服务"""
        return Mock(spec=AuthService)
    
    def test_login_endpoint_success(self, client):
        """测试登录端点成功"""
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
                        "password": "password123"
                    })
            
            assert response.status_code == 200
            data = response.json()
            assert data["access_token"] == "access_token"
            assert data["refresh_token"] == "refresh_token"
            assert data["user_id"] == "user123"
            assert data["username"] == "testuser"
            assert data["mfa_required"] is False
    
    def test_login_endpoint_invalid_credentials(self, client):
        """测试登录端点无效凭据"""
        with patch('auth_service.api.rest.endpoints.auth.get_auth_service') as mock_get_service:
            mock_service = Mock()
            mock_service.authenticate_user.return_value = (None, LoginResult.FAILED_INVALID_CREDENTIALS)
            mock_get_service.return_value = mock_service
            
            with patch('auth_service.api.rest.endpoints.auth.get_db'):
                response = client.post("/api/v1/auth/login", json={
                    "username": "testuser",
                    "password": "wrong_password"
                })
            
            assert response.status_code == 401
            assert "用户名或密码错误" in response.json()["detail"]
    
    def test_login_endpoint_account_locked(self, client):
        """测试登录端点账户锁定"""
        with patch('auth_service.api.rest.endpoints.auth.get_auth_service') as mock_get_service:
            mock_service = Mock()
            mock_service.authenticate_user.return_value = (None, LoginResult.FAILED_ACCOUNT_LOCKED)
            mock_get_service.return_value = mock_service
            
            with patch('auth_service.api.rest.endpoints.auth.get_db'):
                response = client.post("/api/v1/auth/login", json={
                    "username": "testuser",
                    "password": "password123"
                })
            
            assert response.status_code == 423
            assert "账户已被锁定" in response.json()["detail"]
    
    def test_login_endpoint_mfa_required(self, client):
        """测试登录端点需要MFA"""
        with patch('auth_service.api.rest.endpoints.auth.get_auth_service') as mock_get_service:
            mock_service = Mock()
            mock_user = Mock()
            mock_user.id = "user123"
            mock_user.username = "testuser"
            
            mock_service.authenticate_user.return_value = (mock_user, LoginResult.FAILED_MFA_REQUIRED)
            mock_get_service.return_value = mock_service
            
            with patch('auth_service.api.rest.endpoints.auth.get_db'):
                response = client.post("/api/v1/auth/login", json={
                    "username": "testuser",
                    "password": "password123"
                })
            
            assert response.status_code == 200
            data = response.json()
            assert data["mfa_required"] is True
            assert data["user_id"] == "user123"
    
    def test_refresh_token_endpoint_success(self, client):
        """测试刷新令牌端点成功"""
        with patch('auth_service.api.rest.endpoints.auth.get_db'):
            with patch('auth_service.repositories.session_repository.SessionRepository') as mock_repo_class:
                mock_repo = Mock()
                mock_session = Mock()
                mock_session.is_valid.return_value = True
                mock_session.user_id = "user123"
                mock_session.expires_at = datetime.utcnow() + timedelta(hours=1)
                
                mock_repo.get_by_refresh_token.return_value = mock_session
                mock_repo_class.return_value = mock_repo
                
                with patch('auth_service.repositories.user_repository.UserRepository') as mock_user_repo_class:
                    mock_user_repo = Mock()
                    mock_user = Mock()
                    mock_user.id = "user123"
                    mock_user.username = "testuser"
                    mock_user.is_active_user.return_value = True
                    
                    mock_user_repo.get_by_id.return_value = mock_user
                    mock_user_repo_class.return_value = mock_user_repo
                    
                    with patch('auth_service.api.rest.endpoints.auth.get_auth_service') as mock_get_service:
                        mock_service = Mock()
                        mock_service.create_access_token.return_value = "new_access_token"
                        mock_service.create_refresh_token.return_value = "new_refresh_token"
                        mock_service.settings.jwt.access_token_expire_minutes = 60
                        mock_get_service.return_value = mock_service
                        
                        response = client.post("/api/v1/auth/refresh", json={
                            "refresh_token": "valid_refresh_token"
                        })
                
                assert response.status_code == 200
                data = response.json()
                assert data["access_token"] == "new_access_token"
                assert data["refresh_token"] == "new_refresh_token"
    
    def test_refresh_token_endpoint_invalid_token(self, client):
        """测试刷新令牌端点无效令牌"""
        with patch('auth_service.api.rest.endpoints.auth.get_db'):
            with patch('auth_service.repositories.session_repository.SessionRepository') as mock_repo_class:
                mock_repo = Mock()
                mock_repo.get_by_refresh_token.return_value = None
                mock_repo_class.return_value = mock_repo
                
                with patch('auth_service.api.rest.endpoints.auth.get_auth_service'):
                    response = client.post("/api/v1/auth/refresh", json={
                        "refresh_token": "invalid_refresh_token"
                    })
                
                assert response.status_code == 401
                assert "无效的刷新令牌" in response.json()["detail"]


class TestMFAFunctionality:
    """MFA功能测试"""
    
    @pytest.fixture
    def auth_service(self):
        return AuthService()
    
    def test_mfa_setup_flow(self, auth_service):
        """测试MFA设置流程"""
        # 生成密钥
        secret = auth_service.generate_mfa_secret()
        assert len(secret) == 32
        
        # 生成二维码URL
        email = "test@example.com"
        qr_url = auth_service.get_mfa_qr_code_url(email, secret)
        
        assert "otpauth://totp/" in qr_url
        assert email in qr_url
        assert secret in qr_url
    
    @patch('pyotp.TOTP.verify')
    def test_mfa_verification_flow(self, mock_verify, auth_service):
        """测试MFA验证流程"""
        secret = "JBSWY3DPEHPK3PXP"
        
        # 测试有效令牌
        mock_verify.return_value = True
        assert auth_service.verify_mfa_token(secret, "123456") is True
        
        # 测试无效令牌
        mock_verify.return_value = False
        assert auth_service.verify_mfa_token(secret, "654321") is False


class TestSecurityFeatures:
    """安全功能测试"""
    
    @pytest.fixture
    def auth_service(self):
        return AuthService()
    
    def test_password_hashing_security(self, auth_service):
        """测试密码哈希安全性"""
        password = "TestPassword123!"
        
        # 同一密码多次哈希应该产生不同结果（盐值不同）
        hash1 = auth_service.get_password_hash(password)
        hash2 = auth_service.get_password_hash(password)
        
        assert hash1 != hash2
        assert auth_service.verify_password(password, hash1)
        assert auth_service.verify_password(password, hash2)
    
    def test_jwt_token_security(self, auth_service):
        """测试JWT令牌安全性"""
        data = {"sub": "user123", "username": "testuser"}
        token = auth_service.create_access_token(data)
        
        # 验证令牌包含必要的安全字段
        payload = auth_service.verify_token(token)
        assert "exp" in payload  # 过期时间
        assert "iat" in payload  # 签发时间
        assert "iss" in payload  # 签发者
        assert "aud" in payload  # 受众
        
        # 验证令牌不能被篡改
        tampered_token = token[:-5] + "XXXXX"
        assert auth_service.verify_token(tampered_token) is None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=auth_service", "--cov-report=html"]) 