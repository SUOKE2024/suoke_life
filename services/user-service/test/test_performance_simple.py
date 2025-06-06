"""
test_performance_simple - 索克生活项目模块
"""

from internal.model.user import CreateUserRequest
from internal.repository.sqlite_user_repository import SQLiteUserRepository
from internal.service.user_service import UserService
import asyncio
import os
import pytest
import pytest_asyncio
import tempfile
import time

"""
User-Service 简化性能测试
"""



class TestUserServicePerformanceSimple:
    """User-Service 简化性能测试"""
    
    @pytest_asyncio.fixture
    async def repository(self):
        """创建测试repository"""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        repo = SQLiteUserRepository(temp_db.name)
        await repo.initialize()
        
        yield repo
        
        # 清理
        try:
            os.unlink(temp_db.name)
        except:
            pass
    
    @pytest_asyncio.fixture
    async def user_service(self, repository):
        """创建用户服务实例"""
        return UserService(repository)
    
    @pytest.mark.asyncio
    async def test_simple_performance(self, user_service):
        """简单性能测试"""
        print(f"\n开始简单性能测试...")
        
        # 创建10个用户
        start_time = time.time()
        created_users = []
        
        for i in range(10):
            user_data = {
                "username": f"perfuser{i:03d}",
                "email": f"perf{i:03d}@suoke.life",
                "password": "SecurePass123!",
                "full_name": f"性能测试用户 {i}"
            }
            
            request = CreateUserRequest(**user_data)
            user = await user_service.create_user(request)
            created_users.append(user)
        
        total_time = time.time() - start_time
        avg_time_per_user = total_time / 10 * 1000  # 毫秒
        
        print(f"✓ 简单性能测试结果:")
        print(f"  - 创建用户数: 10")
        print(f"  - 总耗时: {total_time:.2f}秒")
        print(f"  - 平均每用户: {avg_time_per_user:.2f}毫秒")
        
        # 验证所有用户都创建成功
        assert len(created_users) == 10
        assert all(user.user_id is not None for user in created_users)
        
        # 测试读取性能
        read_start = time.time()
        for user in created_users:
            retrieved_user = await user_service.get_user(str(user.user_id))
            assert retrieved_user.username == user.username
        
        read_time = time.time() - read_start
        avg_read_time = read_time / 10 * 1000
        
        print(f"  - 读取总耗时: {read_time:.2f}秒")
        print(f"  - 平均读取时间: {avg_read_time:.2f}毫秒")
        
        return True
    
    @pytest.mark.asyncio
    async def test_concurrent_creation(self, user_service):
        """并发创建测试"""
        print(f"\n开始并发创建测试...")
        
        async def create_user(user_id):
            user_data = {
                "username": f"concurrent{user_id:03d}",
                "email": f"concurrent{user_id:03d}@suoke.life",
                "password": "SecurePass123!",
                "full_name": f"并发测试用户 {user_id}"
            }
            request = CreateUserRequest(**user_data)
            return await user_service.create_user(request)
        
        start_time = time.time()
        
        # 并发创建5个用户
        tasks = [create_user(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        
        print(f"✓ 并发创建测试结果:")
        print(f"  - 并发创建用户数: 5")
        print(f"  - 总耗时: {total_time:.2f}秒")
        print(f"  - 平均每用户: {total_time/5*1000:.2f}毫秒")
        
        # 验证所有用户都创建成功
        assert len(results) == 5
        assert all(user.user_id is not None for user in results)
        
        # 验证用户名都不同
        usernames = [user.username for user in results]
        assert len(set(usernames)) == 5
        
        return True 