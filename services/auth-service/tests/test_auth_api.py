"""
test_auth_api - 索克生活项目模块
"""

from auth_service.core.database import get_db
from auth_service.main import app
from auth_service.models.base import BaseModel
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import asyncio
import pytest

"""认证服务API测试"""




# 测试数据库配置
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=True,
    future=True
)

TestingSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def override_get_db():
    """测试数据库依赖覆盖"""
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def setup_database():
    """设置测试数据库"""
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)


@pytest.fixture
async def client(setup_database):
    """创建测试客户端"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_user_data():
    """测试用户数据"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPassword123!",
        "phone": "+1234567890"
    }


class TestAuthAPI:
    """认证API测试类"""
    
    async def test_health_check(self, client: AsyncClient):
        """测试健康检查"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "auth-service"
    
    async def test_create_user(self, client: AsyncClient, test_user_data):
        """测试创建用户"""
        response = await client.post("/users/", json=test_user_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert "id" in data
        assert "password" not in data  # 确保密码不在响应中
    
    async def test_create_duplicate_user(self, client: AsyncClient, test_user_data):
        """测试创建重复用户"""
        # 先创建一个用户
        await client.post("/users/", json=test_user_data)
        
        # 尝试创建相同用户名的用户
        response = await client.post("/users/", json=test_user_data)
        assert response.status_code == 400
        assert "用户名已存在" in response.json()["detail"]
    
    async def test_login_success(self, client: AsyncClient, test_user_data):
        """测试成功登录"""
        # 先创建用户
        await client.post("/users/", json=test_user_data)
        
        # 登录
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
        response = await client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["mfa_required"] is False
    
    async def test_login_invalid_credentials(self, client: AsyncClient, test_user_data):
        """测试无效凭据登录"""
        # 先创建用户
        await client.post("/users/", json=test_user_data)
        
        # 使用错误密码登录
        login_data = {
            "username": test_user_data["username"],
            "password": "wrongpassword"
        }
        response = await client.post("/auth/login", json=login_data)
        assert response.status_code == 401
        assert "用户名或密码错误" in response.json()["detail"]
    
    async def test_get_current_user(self, client: AsyncClient, test_user_data):
        """测试获取当前用户信息"""
        # 创建用户并登录
        await client.post("/users/", json=test_user_data)
        
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
        login_response = await client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # 获取用户信息
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/users/me", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
    
    async def test_refresh_token(self, client: AsyncClient, test_user_data):
        """测试刷新令牌"""
        # 创建用户并登录
        await client.post("/users/", json=test_user_data)
        
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
        login_response = await client.post("/auth/login", json=login_data)
        refresh_token = login_response.json()["refresh_token"]
        
        # 刷新令牌
        refresh_data = {"refresh_token": refresh_token}
        response = await client.post("/auth/refresh", json=refresh_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    async def test_logout(self, client: AsyncClient, test_user_data):
        """测试登出"""
        # 创建用户并登录
        await client.post("/users/", json=test_user_data)
        
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
        login_response = await client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # 登出
        headers = {"Authorization": f"Bearer {token}"}
        logout_data = {"all_devices": False}
        response = await client.post("/auth/logout", json=logout_data, headers=headers)
        assert response.status_code == 200
        assert "登出成功" in response.json()["message"]
    
    async def test_change_password(self, client: AsyncClient, test_user_data):
        """测试修改密码"""
        # 创建用户并登录
        await client.post("/users/", json=test_user_data)
        
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
        login_response = await client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # 修改密码
        headers = {"Authorization": f"Bearer {token}"}
        change_password_data = {
            "current_password": test_user_data["password"],
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!"
        }
        response = await client.post("/users/me/change-password", 
                                   json=change_password_data, headers=headers)
        assert response.status_code == 200
        assert "密码修改成功" in response.json()["message"]
    
    async def test_get_user_sessions(self, client: AsyncClient, test_user_data):
        """测试获取用户会话列表"""
        # 创建用户并登录
        await client.post("/users/", json=test_user_data)
        
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
        login_response = await client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # 获取会话列表
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/auth/sessions", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "sessions" in data
        assert "total" in data
        assert len(data["sessions"]) >= 1  # 至少有当前会话
    
    async def test_unauthorized_access(self, client: AsyncClient):
        """测试未授权访问"""
        response = await client.get("/users/me")
        assert response.status_code == 401
    
    async def test_invalid_token(self, client: AsyncClient):
        """测试无效令牌"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get("/users/me", headers=headers)
        assert response.status_code == 401


class TestPasswordValidation:
    """密码验证测试类"""
    
    @pytest.mark.parametrize("password,should_fail", [
        ("weak", True),  # 太短
        ("password", True),  # 没有大写字母和数字
        ("Password", True),  # 没有数字
        ("Password123", True),  # 没有特殊字符
        ("Password123!", False),  # 符合要求
        ("MySecureP@ssw0rd", False),  # 符合要求
    ])
    async def test_password_strength(self, client: AsyncClient, password, should_fail):
        """测试密码强度验证"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": password,
            "phone": "+1234567890"
        }
        
        response = await client.post("/users/", json=user_data)
        
        if should_fail:
            assert response.status_code == 400
        else:
            assert response.status_code == 201


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 