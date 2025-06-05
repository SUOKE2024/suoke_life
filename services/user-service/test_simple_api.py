"""
简单的API测试，直接使用已初始化的repository
"""
import asyncio
import tempfile
import os
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from internal.repository.sqlite_user_repository import SQLiteUserRepository
from internal.service.user_service import UserService
from internal.model.user import CreateUserRequest

# 创建临时数据库文件
temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
temp_db.close()

# 全局变量
repository = None
user_service = None

async def init_services():
    """初始化服务"""
    global repository, user_service
    repository = SQLiteUserRepository(temp_db.name)
    await repository.initialize()
    user_service = UserService(repository)

# 创建FastAPI应用
app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/v1/users")
async def create_user(user_data: CreateUserRequest):
    try:
        if user_service is None:
            raise HTTPException(status_code=500, detail="Service not initialized")
        
        user_response = await user_service.create_user(user_data)
        return user_response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def test_api():
    """测试API"""
    # 初始化服务
    asyncio.run(init_services())
    
    # 创建测试客户端
    client = TestClient(app)
    
    # 测试健康检查
    response = client.get("/health")
    print(f"Health check: {response.status_code} - {response.json()}")
    
    # 测试创建用户
    user_data = {
        "username": "testuser",
        "email": "test@suoke.life",
        "password": "securepassword123",
        "phone": "13800138000",
        "full_name": "测试用户"
    }
    
    response = client.post("/api/v1/users", json=user_data)
    print(f"Create user: {response.status_code}")
    if response.status_code == 201:
        print(f"User created: {response.json()}")
    else:
        print(f"Error: {response.text}")
    
    # 清理
    try:
        os.unlink(temp_db.name)
    except:
        pass

if __name__ == "__main__":
    test_api() 