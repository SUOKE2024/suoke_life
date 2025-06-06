"""
test_auth_advanced - 索克生活项目模块
"""

        import threading
        import time
from auth_service.core.auth import AuthService
from auth_service.core.database import get_db
from auth_service.main import app
from auth_service.repositories.session_repository import SessionRepository
from auth_service.repositories.user_repository import UserRepository
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
import pytest
import uuid

"""
Auth-Service 高级认证功能测试
"""



class TestAuthAdvanced:
    """高级认证功能测试"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        return TestClient(app)
    
    @pytest.fixture
    def auth_service(self):
        """创建认证服务实例"""
        return AuthService()
    
    @pytest.fixture
    async def test_user_data(self):
        """测试用户数据"""
        return {
            "username": "testuser",
            "email": "test@suoke.life",
            "password": "SecurePass123!",
            "phone": "+8613800138000"
        }
    
    @pytest.fixture
    async def created_user(self, client, test_user_data):
        """创建测试用户"""
        response = client.post("/api/v1/users/", json=test_user_data)
        assert response.status_code == 201
        return response.json()
    
    def test_user_registration_flow(self, client):
        """测试用户注册流程"""
        # 1. 正常注册
        user_data = {
            "username": "newuser",
            "email": "newuser@suoke.life",
            "password": "SecurePass123!",
            "phone": "+8613800138001"
        }
        
        response = client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert "id" in data
        assert data["is_verified"] is False
        
        # 2. 重复用户名注册
        duplicate_user = {
            "username": "newuser",  # 重复用户名
            "email": "another@suoke.life",
            "password": "SecurePass123!",
        }
        
        response = client.post("/api/v1/users/", json=duplicate_user)
        assert response.status_code == 400
        assert "用户名已存在" in response.json()["detail"]
        
        # 3. 重复邮箱注册
        duplicate_email = {
            "username": "anothuser",
            "email": "newuser@suoke.life",  # 重复邮箱
            "password": "SecurePass123!",
        }
        
        response = client.post("/api/v1/users/", json=duplicate_email)
        assert response.status_code == 400
        assert "邮箱已被注册" in response.json()["detail"]
    
    def test_password_strength_validation(self, client):
        """测试密码强度验证"""
        base_user = {
            "username": "testpass",
            "email": "testpass@suoke.life"
        }
        
        # 测试弱密码
        weak_passwords = [
            "123456",           # 太简单
            "password",         # 常见密码
            "abc123",          # 太短且简单
            "UPPERCASE",       # 只有大写
            "lowercase",       # 只有小写
            "12345678",        # 只有数字
        ]
        
        for weak_pass in weak_passwords:
            user_data = {**base_user, "password": weak_pass}
            response = client.post("/api/v1/users/", json=user_data)
            assert response.status_code == 400
            print(f"弱密码 '{weak_pass}' 被正确拒绝")
    
    def test_login_flow(self, client, created_user, test_user_data):
        """测试登录流程"""
        # 1. 正常登录
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"],
            "device_id": "test-device-001",
            "device_name": "Test Device"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user_id"] == created_user["id"]
        assert data["username"] == created_user["username"]
        assert data["mfa_required"] is False
        
        return data
    
    def test_login_failures(self, client, created_user, test_user_data):
        """测试登录失败场景"""
        # 1. 错误密码
        wrong_password = {
            "username": test_user_data["username"],
            "password": "WrongPassword123!",
            "device_id": "test-device-001"
        }
        
        response = client.post("/api/v1/auth/login", json=wrong_password)
        assert response.status_code == 401
        assert "用户名或密码错误" in response.json()["detail"]
        
        # 2. 不存在的用户
        nonexistent_user = {
            "username": "nonexistent",
            "password": "AnyPassword123!",
            "device_id": "test-device-001"
        }
        
        response = client.post("/api/v1/auth/login", json=nonexistent_user)
        assert response.status_code == 401
        assert "用户名或密码错误" in response.json()["detail"]
    
    def test_token_refresh_flow(self, client, created_user, test_user_data):
        """测试令牌刷新流程"""
        # 1. 先登录获取令牌
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"],
            "device_id": "test-device-001"
        }
        
        login_response = client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200
        login_result = login_response.json()
        
        # 2. 使用refresh_token刷新
        refresh_data = {
            "refresh_token": login_result["refresh_token"]
        }
        
        refresh_response = client.post("/api/v1/auth/refresh", json=refresh_data)
        assert refresh_response.status_code == 200
        
        refresh_result = refresh_response.json()
        assert "access_token" in refresh_result
        assert "refresh_token" in refresh_result
        assert refresh_result["token_type"] == "bearer"
        
        # 3. 新令牌应该与旧令牌不同
        assert refresh_result["access_token"] != login_result["access_token"]
        assert refresh_result["refresh_token"] != login_result["refresh_token"]
    
    def test_logout_flow(self, client, created_user, test_user_data):
        """测试登出流程"""
        # 1. 先登录
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"],
            "device_id": "test-device-001"
        }
        
        login_response = client.post("/api/v1/auth/login", json=login_data)
        login_result = login_response.json()
        access_token = login_result["access_token"]
        
        # 2. 单设备登出
        logout_data = {
            "all_devices": False
        }
        
        headers = {"Authorization": f"Bearer {access_token}"}
        logout_response = client.post("/api/v1/auth/logout", json=logout_data, headers=headers)
        assert logout_response.status_code == 200
        assert "登出成功" in logout_response.json()["message"]
        
        # 3. 验证令牌已失效
        profile_response = client.get("/api/v1/users/me", headers=headers)
        assert profile_response.status_code == 401
    
    def test_multiple_device_sessions(self, client, created_user, test_user_data):
        """测试多设备会话管理"""
        # 1. 在多个设备上登录
        devices = ["device-001", "device-002", "device-003"]
        tokens = []
        
        for device_id in devices:
            login_data = {
                "username": test_user_data["username"],
                "password": test_user_data["password"],
                "device_id": device_id,
                "device_name": f"Test Device {device_id}"
            }
            
            response = client.post("/api/v1/auth/login", json=login_data)
            assert response.status_code == 200
            tokens.append(response.json()["access_token"])
        
        # 2. 验证所有令牌都有效
        for token in tokens:
            headers = {"Authorization": f"Bearer {token}"}
            response = client.get("/api/v1/users/me", headers=headers)
            assert response.status_code == 200
        
        # 3. 全设备登出
        logout_data = {"all_devices": True}
        headers = {"Authorization": f"Bearer {tokens[0]}"}
        
        logout_response = client.post("/api/v1/auth/logout", json=logout_data, headers=headers)
        assert logout_response.status_code == 200
        
        # 4. 验证所有令牌都已失效
        for token in tokens:
            headers = {"Authorization": f"Bearer {token}"}
            response = client.get("/api/v1/users/me", headers=headers)
            assert response.status_code == 401
    
    def test_user_profile_management(self, client, created_user, test_user_data):
        """测试用户资料管理"""
        # 1. 先登录获取令牌
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"],
            "device_id": "test-device-001"
        }
        
        login_response = client.post("/api/v1/auth/login", json=login_data)
        access_token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # 2. 获取当前用户信息
        profile_response = client.get("/api/v1/users/me", headers=headers)
        assert profile_response.status_code == 200
        
        profile = profile_response.json()
        assert profile["username"] == test_user_data["username"]
        assert profile["email"] == test_user_data["email"]
        
        # 3. 更新用户信息
        update_data = {
            "username": "updateduser",
            "phone": "+8613800138999"
        }
        
        update_response = client.put("/api/v1/users/me", json=update_data, headers=headers)
        assert update_response.status_code == 200
        
        updated_profile = update_response.json()
        assert updated_profile["username"] == "updateduser"
        assert updated_profile["phone"] == "+8613800138999"
    
    def test_password_change(self, client, created_user, test_user_data):
        """测试密码修改"""
        # 1. 先登录
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"],
            "device_id": "test-device-001"
        }
        
        login_response = client.post("/api/v1/auth/login", json=login_data)
        access_token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # 2. 修改密码
        new_password = "NewSecurePass456!"
        change_password_data = {
            "current_password": test_user_data["password"],
            "new_password": new_password,
            "confirm_password": new_password
        }
        
        change_response = client.post("/api/v1/users/me/change-password", 
                                    json=change_password_data, headers=headers)
        assert change_response.status_code == 200
        
        # 3. 用新密码登录
        new_login_data = {
            "username": test_user_data["username"],
            "password": new_password,
            "device_id": "test-device-002"
        }
        
        new_login_response = client.post("/api/v1/auth/login", json=new_login_data)
        assert new_login_response.status_code == 200
        
        # 4. 用旧密码登录应该失败
        old_login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"],
            "device_id": "test-device-003"
        }
        
        old_login_response = client.post("/api/v1/auth/login", json=old_login_data)
        assert old_login_response.status_code == 401
    
    def test_concurrent_login_attempts(self, client, created_user, test_user_data):
        """测试并发登录尝试"""
        
        results = []
        
        def login_attempt():
            login_data = {
                "username": test_user_data["username"],
                "password": test_user_data["password"],
                "device_id": f"device-{threading.current_thread().ident}"
            }
            
            response = client.post("/api/v1/auth/login", json=login_data)
            results.append(response.status_code)
        
        # 创建多个并发登录线程
        threads = []
        for i in range(5):
            thread = threading.Thread(target=login_attempt)
            threads.append(thread)
        
        # 启动所有线程
        for thread in threads:
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证所有登录都成功
        assert all(status == 200 for status in results)
        assert len(results) == 5
    
    def test_session_expiry_handling(self, client, created_user, test_user_data):
        """测试会话过期处理"""
        # 注意：这个测试需要修改JWT过期时间设置才能真正测试
        # 这里只是演示测试结构
        
        # 1. 登录获取令牌
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"],
            "device_id": "test-device-001"
        }
        
        login_response = client.post("/api/v1/auth/login", json=login_data)
        access_token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # 2. 验证令牌当前有效
        profile_response = client.get("/api/v1/users/me", headers=headers)
        assert profile_response.status_code == 200
        
        # 在实际测试中，这里应该等待令牌过期或使用模拟的过期令牌
        # 然后验证过期令牌被正确拒绝
    
    def test_invalid_token_handling(self, client):
        """测试无效令牌处理"""
        # 1. 完全无效的令牌
        invalid_headers = {"Authorization": "Bearer invalid_token_123"}
        response = client.get("/api/v1/users/me", headers=invalid_headers)
        assert response.status_code == 401
        
        # 2. 格式错误的Authorization头
        malformed_headers = {"Authorization": "InvalidFormat token123"}
        response = client.get("/api/v1/users/me", headers=malformed_headers)
        assert response.status_code == 403  # FastAPI HTTPBearer会返回403
        
        # 3. 缺少Authorization头
        response = client.get("/api/v1/users/me")
        assert response.status_code == 403
    
    def test_user_status_validation(self, client, created_user, test_user_data):
        """测试用户状态验证"""
        # 这个测试需要管理员权限来修改用户状态
        # 这里只是演示测试结构
        
        # 1. 正常用户可以登录
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"],
            "device_id": "test-device-001"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        
        # 在实际测试中，这里应该：
        # 2. 禁用用户账户
        # 3. 验证被禁用的用户无法登录
        # 4. 验证已登录的会话被终止 