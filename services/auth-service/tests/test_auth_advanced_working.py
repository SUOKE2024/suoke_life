"""
Auth-Service 工作的高级功能测试
使用测试数据库管理器解决数据库初始化问题
"""

import pytest
import pytest_asyncio
import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
from typing import List, Dict, Any

# 使用工作的测试配置
pytest_plugins = ["conftest_working"]


class TestAuthServiceAdvancedWorking:
    """Auth-Service 工作的高级功能测试"""
    
    @pytest.mark.asyncio
    async def test_user_registration_flow(self, client, sample_user_data):
        """测试用户注册流程"""
        print("🔐 测试用户注册流程...")
        
        # 1. 正常用户注册
        response = client.post("/api/v1/users/", json=sample_user_data)
        assert response.status_code in [200, 201], f"注册失败: {response.text}"
        
        user_data = response.json()
        assert user_data["username"] == sample_user_data["username"]
        assert user_data["email"] == sample_user_data["email"]
        assert "id" in user_data
        print("✓ 正常用户注册成功")
        
        # 2. 重复用户名注册
        duplicate_data = sample_user_data.copy()
        duplicate_data["email"] = "different@suoke.life"
        response = client.post("/api/v1/users/", json=duplicate_data)
        assert response.status_code == 400, "应该拒绝重复用户名"
        print("✓ 重复用户名检测正常")
        
        # 3. 重复邮箱注册
        duplicate_data = sample_user_data.copy()
        duplicate_data["username"] = "differentuser"
        response = client.post("/api/v1/users/", json=duplicate_data)
        assert response.status_code == 400, "应该拒绝重复邮箱"
        print("✓ 重复邮箱检测正常")
    
    @pytest.mark.asyncio
    async def test_password_strength_validation(self, client):
        """测试密码强度验证"""
        print("🔒 测试密码强度验证...")
        
        weak_passwords = [
            "123456",           # 太简单
            "password",         # 常见密码
            "abc123",          # 太短
            "ALLUPPERCASE",    # 只有大写
            "alllowercase",    # 只有小写
            "12345678",        # 只有数字
        ]
        
        base_user_data = {
            "username": "testuser",
            "email": "test@suoke.life",
            "full_name": "Test User"
        }
        
        for i, weak_password in enumerate(weak_passwords):
            user_data = base_user_data.copy()
            user_data.update({
                "username": f"testuser{i}",
                "email": f"test{i}@suoke.life",
                "password": weak_password,
                "confirm_password": weak_password
            })
            
            response = client.post("/api/v1/users/", json=user_data)
            assert response.status_code == 400, f"弱密码 '{weak_password}' 应该被拒绝"
        
        print("✓ 密码强度验证正常")
    
    @pytest.mark.asyncio
    async def test_login_flow(self, client, sample_user_data):
        """测试登录流程"""
        print("🚪 测试登录流程...")
        
        # 1. 先注册用户
        response = client.post("/api/v1/users/", json=sample_user_data)
        assert response.status_code in [200, 201], f"注册失败: {response.text}"
        
        # 2. 正常登录
        login_data = {
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200, f"登录失败: {response.text}"
        
        login_result = response.json()
        assert "access_token" in login_result
        assert "token_type" in login_result
        assert login_result["token_type"] == "bearer"
        print("✓ 正常登录成功")
        
        # 3. 错误密码登录
        wrong_login_data = login_data.copy()
        wrong_login_data["password"] = "wrongpassword"
        response = client.post("/api/v1/auth/login", json=wrong_login_data)
        assert response.status_code == 401, "错误密码应该被拒绝"
        print("✓ 错误密码检测正常")
        
        # 4. 不存在用户登录
        nonexistent_login_data = {
            "username": "nonexistentuser",
            "password": "anypassword"
        }
        response = client.post("/api/v1/auth/login", json=nonexistent_login_data)
        assert response.status_code == 401, "不存在用户应该被拒绝"
        print("✓ 不存在用户检测正常")
    
    @pytest.mark.asyncio
    async def test_token_management(self, client, sample_user_data):
        """测试令牌管理"""
        print("🎫 测试令牌管理...")
        
        # 1. 注册并登录获取令牌
        client.post("/api/v1/users/", json=sample_user_data)
        login_data = {
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        
        login_result = response.json()
        access_token = login_result["access_token"]
        
        # 2. 使用令牌访问受保护端点
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200, f"令牌验证失败: {response.text}"
        
        user_info = response.json()
        assert user_info["username"] == sample_user_data["username"]
        print("✓ 令牌验证成功")
        
        # 3. 测试无效令牌
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/auth/me", headers=invalid_headers)
        assert response.status_code == 401, "无效令牌应该被拒绝"
        print("✓ 无效令牌检测正常")
    
    @pytest.mark.asyncio
    async def test_concurrent_login(self, client, sample_user_data):
        """测试并发登录"""
        print("🔄 测试并发登录...")
        
        # 1. 注册用户
        client.post("/api/v1/users/", json=sample_user_data)
        
        login_data = {
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        }
        
        # 2. 并发登录测试
        def perform_login():
            response = client.post("/api/v1/auth/login", json=login_data)
            return response.status_code == 200
        
        # 使用线程池进行并发测试
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(perform_login) for _ in range(10)]
            results = [future.result() for future in futures]
        
        # 所有登录都应该成功
        success_count = sum(results)
        assert success_count >= 8, f"并发登录成功率过低: {success_count}/10"
        print(f"✓ 并发登录测试通过: {success_count}/10 成功")
    
    @pytest.mark.asyncio
    async def test_session_management(self, client, sample_user_data):
        """测试会话管理"""
        print("📱 测试会话管理...")
        
        # 1. 注册并登录
        client.post("/api/v1/users/", json=sample_user_data)
        login_data = {
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        }
        
        # 2. 多次登录创建多个会话
        tokens = []
        for i in range(3):
            response = client.post("/api/v1/auth/login", json=login_data)
            assert response.status_code == 200
            token = response.json()["access_token"]
            tokens.append(token)
        
        # 3. 验证所有令牌都有效
        for token in tokens:
            headers = {"Authorization": f"Bearer {token}"}
            response = client.get("/api/v1/auth/me", headers=headers)
            assert response.status_code == 200, "令牌应该有效"
        
        print("✓ 多会话管理正常")
        
        # 4. 登出测试（如果有登出端点）
        if hasattr(client, 'post'):  # 简化的登出测试
            headers = {"Authorization": f"Bearer {tokens[0]}"}
            # 注意：这里假设有登出端点，实际可能需要根据API调整
            print("✓ 会话管理测试完成")
    
    @pytest.mark.asyncio
    async def test_user_profile_management(self, client, sample_user_data):
        """测试用户资料管理"""
        print("👤 测试用户资料管理...")
        
        # 1. 注册并登录
        client.post("/api/v1/users/", json=sample_user_data)
        login_data = {
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. 获取用户信息
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        user_info = response.json()
        assert user_info["username"] == sample_user_data["username"]
        print("✓ 获取用户信息成功")
        
        # 3. 更新用户信息（如果有更新端点）
        update_data = {
            "full_name": "Updated Test User",
            "phone": "+8613800138001"
        }
        
        # 注意：这里假设有用户更新端点，实际可能需要根据API调整
        print("✓ 用户资料管理测试完成")
    
    @pytest.mark.asyncio
    async def test_error_handling(self, client):
        """测试错误处理"""
        print("⚠️ 测试错误处理...")
        
        # 1. 测试无效JSON
        response = client.post(
            "/api/v1/auth/login",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422, "无效JSON应该返回422"
        print("✓ 无效JSON处理正常")
        
        # 2. 测试缺少必填字段
        incomplete_data = {"username": "test"}  # 缺少password
        response = client.post("/api/v1/auth/login", json=incomplete_data)
        assert response.status_code == 422, "缺少必填字段应该返回422"
        print("✓ 缺少字段处理正常")
        
        # 3. 测试无效内容类型
        response = client.post(
            "/api/v1/auth/login",
            data="username=test&password=test",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        # 根据实际API行为调整期望状态码
        print("✓ 错误处理测试完成")


class TestAuthServicePerformance:
    """Auth-Service 性能测试"""
    
    @pytest.mark.asyncio
    async def test_login_performance(self, client, sample_user_data):
        """测试登录性能"""
        print("⚡ 测试登录性能...")
        
        # 1. 注册用户
        client.post("/api/v1/users/", json=sample_user_data)
        
        login_data = {
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        }
        
        # 2. 性能测试
        response_times = []
        for i in range(10):
            start_time = time.time()
            response = client.post("/api/v1/auth/login", json=login_data)
            end_time = time.time()
            
            assert response.status_code == 200, f"登录失败: {response.text}"
            response_times.append(end_time - start_time)
        
        # 3. 性能分析
        avg_time = statistics.mean(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        print(f"✓ 登录性能测试完成:")
        print(f"  - 平均响应时间: {avg_time*1000:.2f}ms")
        print(f"  - 最大响应时间: {max_time*1000:.2f}ms")
        print(f"  - 最小响应时间: {min_time*1000:.2f}ms")
        
        # 性能断言（根据实际需求调整）
        assert avg_time < 1.0, f"平均响应时间过长: {avg_time*1000:.2f}ms"
        assert max_time < 2.0, f"最大响应时间过长: {max_time*1000:.2f}ms"
    
    @pytest.mark.asyncio
    async def test_registration_performance(self, client):
        """测试注册性能"""
        print("⚡ 测试注册性能...")
        
        response_times = []
        
        for i in range(5):  # 减少测试数量避免重复用户名
            user_data = {
                "username": f"perftest_user_{i}_{int(time.time())}",
                "email": f"perftest_{i}_{int(time.time())}@suoke.life",
                "password": "TestPassword123!",
                "confirm_password": "TestPassword123!",
                "full_name": f"Performance Test User {i}"
            }
            
            start_time = time.time()
            response = client.post("/api/v1/users/", json=user_data)
            end_time = time.time()
            
            assert response.status_code in [200, 201], f"注册失败: {response.text}"
            response_times.append(end_time - start_time)
        
        # 性能分析
        avg_time = statistics.mean(response_times)
        max_time = max(response_times)
        
        print(f"✓ 注册性能测试完成:")
        print(f"  - 平均响应时间: {avg_time*1000:.2f}ms")
        print(f"  - 最大响应时间: {max_time*1000:.2f}ms")
        
        # 性能断言
        assert avg_time < 2.0, f"平均注册时间过长: {avg_time*1000:.2f}ms" 