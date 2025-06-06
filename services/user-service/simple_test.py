"""
simple_test - 索克生活项目模块
"""

        import traceback
from internal.model.user import CreateUserRequest
from internal.repository.sqlite_user_repository import SQLiteUserRepository
from internal.service.user_service import UserService
import asyncio
import os
import tempfile

"""
简单的测试脚本，用于验证用户服务的基本功能
"""

async def test_user_creation():
    """测试用户创建功能"""
    # 创建临时数据库文件
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    try:
        # 创建repository并初始化
        repository = SQLiteUserRepository(temp_db.name)
        await repository.initialize()
        print("✓ 数据库初始化成功")
        
        # 创建用户服务
        user_service = UserService(repository)
        
        # 创建测试用户
        user_request = CreateUserRequest(
            username="testuser",
            email="test@suoke.life",
            password="securepassword123",
            phone="13800138000",
            full_name="测试用户"
        )
        
        # 创建用户
        user_response = await user_service.create_user(user_request)
        print(f"✓ 用户创建成功: {user_response.username}")
        
        # 获取用户
        get_response = await user_service.get_user(str(user_response.user_id))
        print(f"✓ 用户获取成功: {get_response.username}")
        
        print("所有测试通过！")
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        traceback.print_exc()
    finally:
        # 清理临时文件
        try:
            os.unlink(temp_db.name)
        except:
            pass

if __name__ == "__main__":
    asyncio.run(test_user_creation()) 