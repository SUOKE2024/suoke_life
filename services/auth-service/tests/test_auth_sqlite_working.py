"""
Auth-Service SQLite兼容测试
解决数据库初始化问题的完整测试套件
"""
import os
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text

# 设置测试环境变量
os.environ["ENVIRONMENT"] = "testing"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"

from auth_service.core.database import get_db
from test_database_manager_sqlite_compatible import TestDatabaseManager


@pytest_asyncio.fixture(scope="session")
async def test_db_manager():
    """测试数据库管理器fixture"""
    manager = TestDatabaseManager()
    await manager.initialize()
    yield manager
    await manager.cleanup()


@pytest.fixture
def app(test_db_manager):
    """创建测试应用"""
    from auth_service.main import create_app
    
    app = create_app()
    
    # 覆盖数据库依赖
    async def override_get_db():
        async for session in test_db_manager.get_session():
            yield session
            break  # 只需要一个会话
    
    app.dependency_overrides[get_db] = override_get_db
    return app


@pytest.fixture
def client(app):
    """测试客户端fixture"""
    return TestClient(app)


@pytest.fixture
def sample_user_data():
    """示例用户数据"""
    return {
        "username": "testuser",
        "email": "test@suoke.life",
        "password": "TestPassword123!",
        "confirm_password": "TestPassword123!",
        "full_name": "Test User",
        "phone": "+8613800138000"
    }


class TestAuthServiceBasic:
    """Auth-Service 基础测试"""
    
    def test_health_check(self, client):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✅ 健康检查通过")
    
    def test_service_info(self, client):
        """测试服务信息"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        # 服务名称可能是中文或英文
        assert data["service"] in ["auth-service", "索克生活认证服务"]
        print("✅ 服务信息正常")


class TestDatabaseConnection:
    """数据库连接测试"""
    
    @pytest.mark.asyncio
    async def test_database_initialization(self, test_db_manager):
        """测试数据库初始化"""
        print("🗄️ 测试数据库初始化...")
        
        # 检查数据库管理器是否正确初始化
        assert test_db_manager._initialized, "数据库管理器应该已初始化"
        assert test_db_manager.engine is not None, "数据库引擎应该存在"
        assert test_db_manager.session_factory is not None, "会话工厂应该存在"
        
        print("✅ 数据库初始化成功")
    
    @pytest.mark.asyncio
    async def test_database_session(self, test_db_manager):
        """测试数据库会话"""
        print("🔗 测试数据库会话...")
        
        # 测试获取数据库会话
        async for session in test_db_manager.get_session():
            assert session is not None, "数据库会话应该存在"
            
            # 执行简单查询测试连接
            result = await session.execute(text("SELECT 1"))
            assert result is not None, "数据库查询应该成功"
            break  # 只需要测试一次
        
        print("✅ 数据库会话正常")
    
    @pytest.mark.asyncio
    async def test_database_tables_creation(self, test_db_manager):
        """测试数据库表创建"""
        print("📋 测试数据库表创建...")
        
        # 检查表是否已创建
        async for session in test_db_manager.get_session():
            # 查询SQLite的表信息
            result = await session.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            )
            tables = [row[0] for row in result.fetchall()]
            
            # 检查是否有用户相关的表
            print(f"创建的表: {tables}")
            
            # 应该至少有users表
            assert "users" in tables, "应该创建了users表"
            assert len(tables) > 0, "应该至少创建了一些表"
            break
        
        print("✅ 数据库表创建正常")
    
    @pytest.mark.asyncio
    async def test_user_table_structure(self, test_db_manager):
        """测试用户表结构"""
        print("🏗️ 测试用户表结构...")
        
        async for session in test_db_manager.get_session():
            # 查询users表的列信息
            result = await session.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result.fetchall()]  # row[1]是列名
            
            print(f"users表的列: {columns}")
            
            # 检查必要的列是否存在
            required_columns = ["id", "username", "email", "password_hash", "created_at"]
            for col in required_columns:
                assert col in columns, f"users表应该包含{col}列"
            break
        
        print("✅ 用户表结构正确")


class TestAuthServiceAdvanced:
    """Auth-Service 高级功能测试"""
    
    def test_user_registration_endpoint_exists(self, client):
        """测试用户注册端点是否存在"""
        print("🔐 测试用户注册端点...")
        
        # 测试端点是否存在（即使数据验证失败也应该返回422而不是404）
        response = client.post("/api/v1/users/", json={})
        print(f"注册端点响应状态: {response.status_code}")
        
        # 404表示端点不存在，其他状态码表示端点存在
        assert response.status_code != 404, "用户注册端点应该存在"
        print("✅ 用户注册端点存在")
    
    def test_login_endpoint_exists(self, client):
        """测试登录端点是否存在"""
        print("🚪 测试登录端点...")
        
        # 测试端点是否存在
        response = client.post("/api/v1/auth/login", json={})
        print(f"登录端点响应状态: {response.status_code}")
        
        # 404表示端点不存在，其他状态码表示端点存在
        assert response.status_code != 404, "登录端点应该存在"
        print("✅ 登录端点存在")
    
    def test_protected_endpoint_exists(self, client):
        """测试受保护端点是否存在"""
        print("🔒 测试受保护端点...")
        
        # 无令牌访问
        response = client.get("/api/v1/auth/me")
        print(f"受保护端点响应状态: {response.status_code}")
        
        # 404表示端点不存在，401/403表示需要认证（端点存在），500表示内部错误但端点存在
        assert response.status_code in [401, 403, 500], "受保护端点应该存在"
        print("✅ 受保护端点存在")


class TestDatabaseOperations:
    """数据库操作测试"""
    
    @pytest.mark.asyncio
    async def test_create_test_user(self, test_db_manager):
        """测试创建测试用户"""
        print("👤 测试创建用户...")
        
        from test_database_manager_sqlite_compatible import TestUser
        
        # 确保表已创建
        await test_db_manager.reset_database()
        
        async for session in test_db_manager.get_session():
            # 创建测试用户
            test_user = TestUser(
                username="testuser",
                email="test@example.com",
                password_hash="hashed_password",
                is_verified=True
            )
            
            session.add(test_user)
            await session.commit()
            
            # 查询用户
            result = await session.execute(
                text("SELECT username, email FROM users WHERE username = 'testuser'")
            )
            user_data = result.fetchone()
            
            assert user_data is not None, "应该能够创建和查询用户"
            assert user_data[0] == "testuser", "用户名应该正确"
            assert user_data[1] == "test@example.com", "邮箱应该正确"
            break
        
        print("✅ 用户创建和查询成功")
    
    @pytest.mark.asyncio
    async def test_database_isolation(self, test_db_manager):
        """测试数据库隔离"""
        print("🔒 测试数据库隔离...")
        
        # 重置数据库
        await test_db_manager.reset_database()
        
        async for session in test_db_manager.get_session():
            # 检查表是否为空
            result = await session.execute(text("SELECT COUNT(*) FROM users"))
            count = result.scalar()
            
            assert count == 0, "重置后用户表应该为空"
            break
        
        print("✅ 数据库隔离正常")


class TestAuthServiceIntegration:
    """Auth-Service 集成测试"""
    
    def test_complete_service_startup(self, client):
        """测试完整的服务启动"""
        print("🚀 测试完整服务启动...")
        
        # 测试多个端点确保服务正常启动
        endpoints_to_test = [
            ("/health", 200),
            ("/", 200),
        ]
        
        all_passed = True
        for endpoint, expected_codes in endpoints_to_test:
            if isinstance(expected_codes, int):
                expected_codes = [expected_codes]
            
            response = client.get(endpoint)
            
            if response.status_code in expected_codes:
                print(f"✅ {endpoint}: {response.status_code}")
            else:
                print(f"❌ {endpoint}: {response.status_code} (期望: {expected_codes})")
                all_passed = False
        
        assert all_passed, "所有端点应该正常响应"
        print("✅ 服务启动完整测试通过")
    
    def test_basic_endpoints_without_db(self, client):
        """测试不需要数据库的基础端点"""
        print("🔧 测试基础端点...")
        
        # 这些端点不应该触发数据库操作
        basic_endpoints = [
            "/health",
            "/",
        ]
        
        for endpoint in basic_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200, f"{endpoint} 应该返回200"
            print(f"✅ {endpoint} 正常")
        
        print("✅ 基础端点测试通过")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"]) 