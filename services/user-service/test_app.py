"""
测试用的简化应用
用于运行User-Service的测试
"""
import os
from fastapi import FastAPI, HTTPException, Depends
from internal.repository.sqlite_user_repository import SQLiteUserRepository
from internal.service.user_service import UserService
from internal.model.user import CreateUserRequest, UpdateUserRequest, BindDeviceRequest

# 创建简化的FastAPI应用
app = FastAPI(
    title="用户服务测试",
    description="用于测试的简化用户服务",
    version="1.0.0"
)

# 全局变量存储服务实例
_user_service = None
_repository = None

async def get_user_service():
    """获取用户服务实例"""
    global _user_service, _repository
    if _user_service is None:
        if _repository is None:
            _repository = await init_repositories()
        _user_service = UserService(_repository)
    return _user_service

async def init_repositories():
    """
    初始化仓库（用于测试）
    
    Returns:
        SQLiteUserRepository: 用户仓库实例
    """
    # 使用内存数据库进行测试
    db_path = os.getenv("USER_SERVICE_DB_PATH", ":memory:")
    repository = SQLiteUserRepository(db_path)
    await repository.initialize()
    return repository

# 添加基本的健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "service": "user-service"}

@app.get("/")
async def root():
    """根端点"""
    return {"message": "User Service Test App", "version": "1.0.0"}

# 用户API端点
@app.post("/api/v1/users", status_code=201)
async def create_user(request: CreateUserRequest, user_service: UserService = Depends(get_user_service)):
    """创建用户"""
    try:
        user_response = await user_service.create_user(request)
        return user_response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/users/{user_id}")
async def get_user(user_id: str, user_service: UserService = Depends(get_user_service)):
    """获取用户信息"""
    try:
        user_response = await user_service.get_user(user_id)
        return user_response
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.put("/api/v1/users/{user_id}")
async def update_user(user_id: str, request: UpdateUserRequest, user_service: UserService = Depends(get_user_service)):
    """更新用户信息"""
    try:
        user_response = await user_service.update_user(user_id, request)
        return user_response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/v1/users/{user_id}", status_code=204)
async def delete_user(user_id: str, user_service: UserService = Depends(get_user_service)):
    """删除用户"""
    try:
        await user_service.delete_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/users/{user_id}/devices", status_code=201)
async def bind_device(user_id: str, request: BindDeviceRequest, user_service: UserService = Depends(get_user_service)):
    """绑定设备"""
    try:
        response = await user_service.bind_device(user_id, request)
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/users/{user_id}/devices")
async def get_user_devices(user_id: str, user_service: UserService = Depends(get_user_service)):
    """获取用户设备列表"""
    try:
        response = await user_service.get_user_devices(user_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/api/v1/users/{user_id}/devices/{device_id}", status_code=204)
async def unbind_device(user_id: str, device_id: str, user_service: UserService = Depends(get_user_service)):
    """解绑设备"""
    try:
        await user_service.unbind_device(user_id, device_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 