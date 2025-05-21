"""
用户服务REST API处理器

该模块实现了用户服务的REST API接口。
"""
import logging
from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime
import uuid

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from pydantic import BaseModel, EmailStr, Field

from internal.model.user import (BindDeviceRequest, CreateUserRequest,
                          DeviceInfo, UpdateUserPreferencesRequest,
                          UpdateUserRequest, UserResponse, UserRole,
                          VerifyUserRequest, UserAuditLog as UserAuditLogModel)
from internal.repository.sqlite_user_repository import (DeviceAlreadyBoundError,
                                                 DeviceNotFoundError,
                                                 UserAlreadyExistsError,
                                                 UserNotFoundError)
from internal.repository.operation_log_repository import AuditLogRepository
from internal.service.user_service import UserService

logger = logging.getLogger(__name__)


# API请求和响应模型
class CreateUserAPIRequest(BaseModel):
    """创建用户API请求"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    phone: Optional[str] = None
    fullName: Optional[str] = None
    password: str = Field(..., min_length=8)
    metadata: Optional[Dict[str, str]] = None


class UpdateUserAPIRequest(BaseModel):
    """更新用户API请求"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    fullName: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None


class UpdateUserPreferencesAPIRequest(BaseModel):
    """更新用户偏好设置API请求"""
    preferences: Dict[str, str]


class BindDeviceAPIRequest(BaseModel):
    """绑定设备API请求"""
    deviceId: str
    deviceType: str
    deviceName: Optional[str] = None
    deviceMetadata: Optional[Dict[str, str]] = None


class VerifyUserAPIRequest(BaseModel):
    """验证用户API请求"""
    userId: str
    token: str


class UserAPIResponse(BaseModel):
    """用户API响应"""
    userId: str
    username: str
    email: str
    phone: Optional[str] = None
    fullName: Optional[str] = None
    createdAt: str
    updatedAt: str
    status: str
    metadata: Dict[str, str] = Field(default_factory=dict)
    roles: List[str] = Field(default_factory=list)
    preferences: Dict[str, str] = Field(default_factory=dict)


class HealthMetricAPIResponse(BaseModel):
    """健康指标API响应"""
    metricName: str
    value: float
    unit: Optional[str] = None
    timestamp: str


class HealthSummaryAPIResponse(BaseModel):
    """健康摘要API响应"""
    userId: str
    dominantConstitution: Optional[str] = None
    recentMetrics: List[HealthMetricAPIResponse] = Field(default_factory=list)
    lastAssessmentDate: Optional[str] = None
    healthScore: int
    constitutionScores: Dict[str, float] = Field(default_factory=dict)


class DeviceInfoAPIResponse(BaseModel):
    """设备信息API响应"""
    deviceId: str
    deviceType: str
    deviceName: Optional[str] = None
    bindingTime: str
    bindingId: str
    isActive: bool = True
    lastActiveTime: Optional[str] = None
    deviceMetadata: Dict[str, str] = Field(default_factory=dict)


class UserDevicesAPIResponse(BaseModel):
    """用户设备列表API响应"""
    userId: str
    devices: List[DeviceInfoAPIResponse] = Field(default_factory=list)


class BindDeviceAPIResponse(BaseModel):
    """绑定设备API响应"""
    success: bool
    bindingId: str
    bindingTime: str


class VerifyUserAPIResponse(BaseModel):
    """验证用户API响应"""
    isValid: bool
    roles: List[str] = Field(default_factory=list)
    permissions: Dict[str, str] = Field(default_factory=dict)


class PaginatedUserResponse(BaseModel):
    """分页用户响应"""
    data: List[UserAPIResponse]
    meta: Dict[str, int]


class ErrorResponse(BaseModel):
    """错误响应"""
    code: str
    message: str
    details: Optional[Dict] = None
    requestId: str


class RouterDependencies:
    """路由依赖注入"""

    def __init__(self, user_service: UserService, audit_log_repository: AuditLogRepository = None):
        self.user_service = user_service
        self.audit_log_repository = audit_log_repository


def create_user_api_router(
    user_service: UserService, 
    audit_log_repository: Optional[AuditLogRepository] = None
) -> APIRouter:
    """
    创建用户API路由器
    
    Args:
        user_service: 用户服务
        audit_log_repository: 审计日志仓库
        
    Returns:
        APIRouter: 路由器
    """
    router = APIRouter(tags=["users"])
    deps = RouterDependencies(user_service, audit_log_repository)
    
    @router.post("/users", response_model=UserAPIResponse, 
                status_code=status.HTTP_201_CREATED,
                responses={
                    409: {"model": ErrorResponse, "description": "用户名或邮箱已存在"},
                    500: {"model": ErrorResponse, "description": "服务器内部错误"}
                })
    async def create_user(request: CreateUserAPIRequest):
        """创建新用户"""
        try:
            # 转换为内部请求模型
            create_request = CreateUserRequest(
                username=request.username,
                email=request.email,
                phone=request.phone,
                full_name=request.fullName,
                password=request.password,
                metadata=request.metadata
            )
            
            # 调用服务创建用户
            user = await deps.user_service.create_user(create_request)
            
            # 记录审计日志
            if deps.audit_log_repository:
                try:
                    await deps.audit_log_repository.create_user_audit_log(
                        UserAuditLogModel(
                            log_id=str(uuid.uuid4()),
                            user_id=user.user_id,
                            action="user_created",
                            timestamp=datetime.utcnow(),
                            ip_address=request.client.host if request.client else None,
                            user_agent=request.headers.get("user-agent"),
                            changes={},  # 新建用户没有变更记录
                            metadata={
                                "request_id": request.headers.get("x-request-id", ""),
                                "username": user.username,
                                "email": user.email
                            }
                        )
                    )
                except Exception as e:
                    # 记录错误但不影响主流程
                    logger.error(f"记录审计日志失败: {str(e)}")
            
            # 转换为API响应
            return UserAPIResponse(
                userId=user.user_id,
                username=user.username,
                email=user.email,
                phone=user.phone,
                fullName=user.full_name,
                createdAt=user.created_at.isoformat(),
                updatedAt=user.updated_at.isoformat(),
                status=user.status.value,
                metadata=user.metadata,
                roles=[role.value for role in user.roles],
                preferences=user.preferences
            )
        except UserAlreadyExistsError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        except Exception as e:
            logger.exception(f"创建用户时发生错误: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"服务器内部错误: {e}"
            )
    
    @router.get("/users", response_model=PaginatedUserResponse)
    async def list_users(
        page: int = Query(1, description="页码，从1开始", ge=1),
        limit: int = Query(10, description="每页条目数", ge=1, le=100),
        status: Optional[str] = Query(None, description="按用户状态过滤")
    ):
        """获取用户列表"""
        try:
            offset = (page - 1) * limit
            users, total = await deps.user_service.list_users(
                offset=offset,
                limit=limit,
                status=status
            )
            
            # 计算总页数
            total_pages = (total + limit - 1) // limit
            
            # 转换为API响应
            user_responses = [
                UserAPIResponse(
                    userId=user.user_id,
                    username=user.username,
                    email=user.email,
                    phone=user.phone,
                    fullName=user.full_name,
                    createdAt=user.created_at.isoformat(),
                    updatedAt=user.updated_at.isoformat(),
                    status=user.status.value,
                    metadata=user.metadata,
                    roles=[role.value for role in user.roles],
                    preferences=user.preferences
                )
                for user in users
            ]
            
            return PaginatedUserResponse(
                data=user_responses,
                meta={
                    "total": total,
                    "page": page,
                    "limit": limit,
                    "totalPages": total_pages
                }
            )
        except Exception as e:
            logger.exception(f"获取用户列表时发生错误: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"服务器内部错误: {e}"
            )
    
    @router.get("/users/{user_id}", response_model=UserAPIResponse,
                responses={
                    404: {"model": ErrorResponse, "description": "用户不存在"},
                    500: {"model": ErrorResponse, "description": "服务器内部错误"}
                })
    async def get_user(user_id: str = Path(..., description="用户ID")):
        """获取用户信息"""
        try:
            user = await deps.user_service.get_user(user_id)
            
            return UserAPIResponse(
                userId=user.user_id,
                username=user.username,
                email=user.email,
                phone=user.phone,
                fullName=user.full_name,
                createdAt=user.created_at.isoformat(),
                updatedAt=user.updated_at.isoformat(),
                status=user.status.value,
                metadata=user.metadata,
                roles=[role.value for role in user.roles],
                preferences=user.preferences
            )
        except UserNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        except Exception as e:
            logger.exception(f"获取用户信息时发生错误: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"服务器内部错误: {e}"
            )
    
    @router.put("/users/{user_id}", response_model=UserAPIResponse,
                responses={
                    404: {"model": ErrorResponse, "description": "用户不存在"},
                    409: {"model": ErrorResponse, "description": "用户名或邮箱已存在"},
                    500: {"model": ErrorResponse, "description": "服务器内部错误"}
                })
    async def update_user(
        request: UpdateUserAPIRequest,
        user_id: str = Path(..., description="用户ID")
    ):
        """更新用户信息"""
        try:
            update_request = UpdateUserRequest(
                username=request.username,
                email=request.email,
                phone=request.phone,
                full_name=request.fullName,
                metadata=request.metadata
            )
            
            # 获取更新前的用户信息
            old_user = None
            if deps.audit_log_repository:
                try:
                    old_user = await deps.user_service.get_user(user_id)
                except Exception as e:
                    logger.warning(f"获取用户旧信息失败，无法记录完整审计日志: {str(e)}")
            
            user = await deps.user_service.update_user(user_id, update_request)
            
            # 记录审计日志
            if deps.audit_log_repository and old_user:
                try:
                    # 构建变更记录
                    changes = {}
                    if update_request.username and old_user.username != user.username:
                        changes["username"] = {
                            "old": old_user.username,
                            "new": user.username
                        }
                    if update_request.email and old_user.email != user.email:
                        changes["email"] = {
                            "old": old_user.email,
                            "new": user.email
                        }
                    if update_request.phone and old_user.phone != user.phone:
                        changes["phone"] = {
                            "old": old_user.phone or "",
                            "new": user.phone or ""
                        }
                    if update_request.full_name and old_user.full_name != user.full_name:
                        changes["full_name"] = {
                            "old": old_user.full_name or "",
                            "new": user.full_name or ""
                        }
                    if update_request.status and old_user.status != user.status:
                        changes["status"] = {
                            "old": old_user.status.value,
                            "new": user.status.value
                        }
                    
                    await deps.audit_log_repository.create_user_audit_log(
                        UserAuditLogModel(
                            log_id=str(uuid.uuid4()),
                            user_id=user.user_id,
                            action="user_updated",
                            timestamp=datetime.utcnow(),
                            ip_address=request.client.host if request.client else None,
                            user_agent=request.headers.get("user-agent"),
                            changes=changes,
                            metadata={
                                "request_id": request.headers.get("x-request-id", ""),
                                "username": user.username
                            }
                        )
                    )
                except Exception as e:
                    # 记录错误但不影响主流程
                    logger.error(f"记录审计日志失败: {str(e)}")
            
            return UserAPIResponse(
                userId=user.user_id,
                username=user.username,
                email=user.email,
                phone=user.phone,
                fullName=user.full_name,
                createdAt=user.created_at.isoformat(),
                updatedAt=user.updated_at.isoformat(),
                status=user.status.value,
                metadata=user.metadata,
                roles=[role.value for role in user.roles],
                preferences=user.preferences
            )
        except UserNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        except UserAlreadyExistsError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        except Exception as e:
            logger.exception(f"更新用户信息时发生错误: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"服务器内部错误: {e}"
            )
    
    @router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT,
                  responses={
                      404: {"model": ErrorResponse, "description": "用户不存在"},
                      500: {"model": ErrorResponse, "description": "服务器内部错误"}
                  })
    async def delete_user(user_id: str = Path(..., description="用户ID")):
        """删除用户"""
        try:
            await deps.user_service.delete_user(user_id)
        except UserNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        except Exception as e:
            logger.exception(f"删除用户时发生错误: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"服务器内部错误: {e}"
            )
    
    @router.get("/users/{user_id}/health-summary", response_model=HealthSummaryAPIResponse,
                responses={
                    404: {"model": ErrorResponse, "description": "用户不存在"},
                    500: {"model": ErrorResponse, "description": "服务器内部错误"}
                })
    async def get_user_health_summary(user_id: str = Path(..., description="用户ID")):
        """获取用户健康摘要"""
        try:
            health_summary = await deps.user_service.get_user_health_summary(user_id)
            
            recent_metrics = [
                HealthMetricAPIResponse(
                    metricName=metric.metric_name,
                    value=metric.value,
                    unit=metric.unit,
                    timestamp=metric.timestamp.isoformat()
                )
                for metric in health_summary.recent_metrics
            ]
            
            return HealthSummaryAPIResponse(
                userId=health_summary.user_id,
                dominantConstitution=health_summary.dominant_constitution.value if health_summary.dominant_constitution else None,
                recentMetrics=recent_metrics,
                lastAssessmentDate=health_summary.last_assessment_date.isoformat() if health_summary.last_assessment_date else None,
                healthScore=health_summary.health_score,
                constitutionScores=health_summary.constitution_scores
            )
        except UserNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        except Exception as e:
            logger.exception(f"获取用户健康摘要时发生错误: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"服务器内部错误: {e}"
            )
    
    @router.put("/users/{user_id}/preferences", response_model=UserAPIResponse,
                responses={
                    404: {"model": ErrorResponse, "description": "用户不存在"},
                    500: {"model": ErrorResponse, "description": "服务器内部错误"}
                })
    async def update_user_preferences(
        request: UpdateUserPreferencesAPIRequest,
        user_id: str = Path(..., description="用户ID")
    ):
        """更新用户偏好设置"""
        try:
            update_request = UpdateUserPreferencesRequest(
                preferences=request.preferences
            )
            
            user = await deps.user_service.update_user_preferences(user_id, update_request)
            
            return UserAPIResponse(
                userId=user.user_id,
                username=user.username,
                email=user.email,
                phone=user.phone,
                fullName=user.full_name,
                createdAt=user.created_at.isoformat(),
                updatedAt=user.updated_at.isoformat(),
                status=user.status.value,
                metadata=user.metadata,
                roles=[role.value for role in user.roles],
                preferences=user.preferences
            )
        except UserNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        except Exception as e:
            logger.exception(f"更新用户偏好设置时发生错误: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"服务器内部错误: {e}"
            )
    
    @router.post("/users/{user_id}/devices", response_model=BindDeviceAPIResponse,
                status_code=status.HTTP_201_CREATED,
                responses={
                    404: {"model": ErrorResponse, "description": "用户不存在"},
                    409: {"model": ErrorResponse, "description": "设备已绑定"},
                    500: {"model": ErrorResponse, "description": "服务器内部错误"}
                })
    async def bind_device(
        request: BindDeviceAPIRequest,
        user_id: str = Path(..., description="用户ID")
    ):
        """绑定设备"""
        try:
            bind_request = BindDeviceRequest(
                device_id=request.deviceId,
                device_type=request.deviceType,
                device_name=request.deviceName,
                device_metadata=request.deviceMetadata
            )
            
            result = await deps.user_service.bind_device(user_id, bind_request)
            
            return BindDeviceAPIResponse(
                success=result.success,
                bindingId=result.binding_id,
                bindingTime=result.binding_time.isoformat()
            )
        except UserNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        except DeviceAlreadyBoundError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        except Exception as e:
            logger.exception(f"绑定设备时发生错误: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"服务器内部错误: {e}"
            )
    
    @router.get("/users/{user_id}/devices", response_model=UserDevicesAPIResponse,
                responses={
                    404: {"model": ErrorResponse, "description": "用户不存在"},
                    500: {"model": ErrorResponse, "description": "服务器内部错误"}
                })
    async def get_user_devices(user_id: str = Path(..., description="用户ID")):
        """获取用户设备列表"""
        try:
            result = await deps.user_service.get_user_devices(user_id)
            
            devices = [
                DeviceInfoAPIResponse(
                    deviceId=device.device_id,
                    deviceType=device.device_type,
                    deviceName=device.device_name,
                    bindingTime=device.binding_time.isoformat(),
                    bindingId=device.binding_id,
                    isActive=device.is_active,
                    lastActiveTime=device.last_active_time.isoformat() if device.last_active_time else None,
                    deviceMetadata=device.device_metadata
                )
                for device in result.devices
            ]
            
            return UserDevicesAPIResponse(
                userId=result.user_id,
                devices=devices
            )
        except UserNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        except Exception as e:
            logger.exception(f"获取用户设备列表时发生错误: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"服务器内部错误: {e}"
            )
    
    @router.delete("/users/{user_id}/devices/{device_id}", status_code=status.HTTP_204_NO_CONTENT,
                  responses={
                      404: {"model": ErrorResponse, "description": "用户或设备不存在"},
                      500: {"model": ErrorResponse, "description": "服务器内部错误"}
                  })
    async def unbind_device(
        user_id: str = Path(..., description="用户ID"),
        device_id: str = Path(..., description="设备ID")
    ):
        """解绑设备"""
        try:
            await deps.user_service.unbind_device(user_id, device_id)
        except (UserNotFoundError, DeviceNotFoundError) as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        except Exception as e:
            logger.exception(f"解绑设备时发生错误: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"服务器内部错误: {e}"
            )
    
    @router.post("/users/verify", response_model=VerifyUserAPIResponse,
                responses={
                    401: {"model": ErrorResponse, "description": "验证失败"},
                    500: {"model": ErrorResponse, "description": "服务器内部错误"}
                })
    async def verify_user_identity(request: VerifyUserAPIRequest):
        """验证用户身份"""
        try:
            verify_request = VerifyUserRequest(
                user_id=UUID(request.userId),
                token=request.token
            )
            
            result = await deps.user_service.verify_user_identity(verify_request)
            
            if not result.is_valid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户验证失败"
                )
            
            return VerifyUserAPIResponse(
                isValid=result.is_valid,
                roles=[role.value for role in result.roles],
                permissions=result.permissions
            )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的用户ID: {request.userId}"
            )
        except Exception as e:
            logger.exception(f"验证用户身份时发生错误: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"服务器内部错误: {e}"
            )
    
    return router 