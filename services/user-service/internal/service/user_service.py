"""
用户服务实现模块

该模块实现了用户服务的核心业务逻辑。
"""
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from passlib.hash import pbkdf2_sha256

from internal.model.user import (BindDeviceRequest, BindDeviceResponse,
                          ConstitutionType, CreateUserRequest, DeviceInfo,
                          HealthMetric, UpdateUserPreferencesRequest,
                          UpdateUserRequest, User, UserDevicesResponse,
                          UserHealthSummary, UserHealthSummaryResponse,
                          UserResponse, UserRole, UserStatus, VerifyUserRequest,
                          VerifyUserResponse)
from internal.repository.exceptions import (DatabaseError, DeviceAlreadyBoundError,
                                     DeviceNotFoundError,
                                     UserAlreadyExistsError,
                                     UserNotFoundError)

logger = logging.getLogger(__name__)

# 定义用户仓库接口协议
from typing import Protocol, Union, TypeVar

class UserRepositoryProtocol(Protocol):
    """用户数据仓库协议，定义了用户仓库必须实现的方法"""
    
    async def create_user(self, username: str, email: str, password_hash: str,
                   phone: Optional[str] = None, full_name: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None,
                   user_id: Optional[UUID] = None) -> User: ...
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]: ...
    
    async def update_user(self, user_id: UUID, username: Optional[str] = None,
                   email: Optional[str] = None, phone: Optional[str] = None,
                   full_name: Optional[str] = None, status: Optional[UserStatus] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> User: ...
    
    async def delete_user(self, user_id: UUID) -> bool: ...
    
    async def list_users(self, offset: int = 0, limit: int = 10,
                  status: Optional[UserStatus] = None) -> Tuple[List[User], int]: ...
    
    async def get_user_health_summary(self, user_id: UUID) -> UserHealthSummary: ...
    
    async def update_health_summary(self, user_id: UUID, health_score: Optional[int] = None,
                             dominant_constitution: Optional[ConstitutionType] = None,
                             constitution_scores: Optional[Dict[str, float]] = None,
                             recent_metrics: Optional[List[HealthMetric]] = None,
                             last_assessment_date: Optional[datetime] = None) -> UserHealthSummary: ...
    
    async def update_user_preferences(self, user_id: UUID, 
                              preferences: Dict[str, Any]) -> User: ...
    
    async def bind_device(self, user_id: UUID, device_id: str, device_type: str,
                   device_name: Optional[str] = None,
                   device_metadata: Optional[Dict[str, Any]] = None) -> str: ...
    
    async def unbind_device(self, user_id: UUID, device_id: str) -> bool: ...
    
    async def get_user_devices(self, user_id: UUID) -> List[DeviceInfo]: ...

class UserService:
    """用户服务类"""

    def __init__(self, user_repository: UserRepositoryProtocol):
        """
        初始化用户服务
        Args:
            user_repository: 用户数据仓库
        """
        self.user_repository = user_repository
    async def create_user(self, request: CreateUserRequest) -> UserResponse:
        """
        创建新用户
        
        Args:
            request: 创建用户请求
            
        Returns:
            UserResponse: 用户响应
            
        Raises:
            UserAlreadyExistsError: 当用户名或邮箱已存在时
        """
        # 生成密码哈希
        password_hash = pbkdf2_sha256.hash(request.password.get_secret_value())
        
        try:
            user = await self.user_repository.create_user(
                username=request.username,
                email=request.email,
                password_hash=password_hash,
                phone=request.phone,
                full_name=request.full_name,
                metadata=request.metadata
            )
            
            return UserResponse(
                user_id=str(user.user_id),
                username=user.username,
                email=user.email,
                phone=user.phone,
                full_name=user.full_name,
                created_at=user.created_at,
                updated_at=user.updated_at,
                status=user.status,
                metadata=user.metadata,
                roles=user.roles,
                preferences=user.preferences
            )
        except UserAlreadyExistsError as e:
            logger.error(f"创建用户失败: {e}")
            raise
    
    async def get_user(self, user_id: str) -> UserResponse:
        """
        获取用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            UserResponse: 用户响应
            
        Raises:
            UserNotFoundError: 当用户不存在时
        """
        try:
            user = await self.user_repository.get_user_by_id(UUID(user_id))
            if not user:
                raise UserNotFoundError(f"用户ID '{user_id}' 不存在")
            
            return UserResponse(
                user_id=str(user.user_id),
                username=user.username,
                email=user.email,
                phone=user.phone,
                full_name=user.full_name,
                created_at=user.created_at,
                updated_at=user.updated_at,
                status=user.status,
                metadata=user.metadata,
                roles=user.roles,
                preferences=user.preferences
            )
        except ValueError:
            raise UserNotFoundError(f"用户ID '{user_id}' 格式无效")
    
    async def update_user(self, user_id: str, request: UpdateUserRequest) -> UserResponse:
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            request: 更新用户请求
            
        Returns:
            UserResponse: 更新后的用户响应
            
        Raises:
            UserNotFoundError: 当用户不存在时
            UserAlreadyExistsError: 当新用户名或邮箱已被其他用户使用时
        """
        try:
            user = await self.user_repository.update_user(
                user_id=UUID(user_id),
                username=request.username,
                email=request.email,
                phone=request.phone,
                full_name=request.full_name,
                metadata=request.metadata
            )
            
            return UserResponse(
                user_id=str(user.user_id),
                username=user.username,
                email=user.email,
                phone=user.phone,
                full_name=user.full_name,
                created_at=user.created_at,
                updated_at=user.updated_at,
                status=user.status,
                metadata=user.metadata,
                roles=user.roles,
                preferences=user.preferences
            )
        except (UserNotFoundError, UserAlreadyExistsError) as e:
            logger.error(f"更新用户失败: {e}")
            raise
        except ValueError:
            raise UserNotFoundError(f"用户ID '{user_id}' 格式无效")
    
    async def delete_user(self, user_id: str) -> bool:
        """
        删除用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 是否删除成功
            
        Raises:
            UserNotFoundError: 当用户不存在时
        """
        try:
            return await self.user_repository.delete_user(UUID(user_id))
        except UserNotFoundError as e:
            logger.error(f"删除用户失败: {e}")
            raise
        except ValueError:
            raise UserNotFoundError(f"用户ID '{user_id}' 格式无效")
    
    async def list_users(self, offset: int = 0, limit: int = 10,
                  status: Optional[str] = None) -> Tuple[List[UserResponse], int]:
        """
        获取用户列表
        
        Args:
            offset: 分页偏移
            limit: 分页限制
            status: 用户状态过滤
            
        Returns:
            Tuple[List[UserResponse], int]: 用户列表和总数
        """
        status_enum = None
        if status:
            try:
                status_enum = UserStatus(status)
            except ValueError:
                logger.warning(f"无效的用户状态值: {status}")
        
        users, total = await self.user_repository.list_users(
            offset=offset,
            limit=limit,
            status=status_enum
        )
        
        user_responses = [
            UserResponse(
                user_id=str(user.user_id),
                username=user.username,
                email=user.email,
                phone=user.phone,
                full_name=user.full_name,
                created_at=user.created_at,
                updated_at=user.updated_at,
                status=user.status,
                metadata=user.metadata,
                roles=user.roles,
                preferences=user.preferences
            )
            for user in users
        ]
        
        return user_responses, total
    
    async def get_user_health_summary(self, user_id: str) -> UserHealthSummaryResponse:
        """
        获取用户健康摘要
        
        Args:
            user_id: 用户ID
            
        Returns:
            UserHealthSummaryResponse: 用户健康摘要响应
            
        Raises:
            UserNotFoundError: 当用户不存在时
        """
        try:
            health_summary = await self.user_repository.get_user_health_summary(UUID(user_id))
            
            return UserHealthSummaryResponse(
                user_id=str(health_summary.user_id),
                dominant_constitution=health_summary.dominant_constitution,
                recent_metrics=health_summary.recent_metrics,
                last_assessment_date=health_summary.last_assessment_date,
                health_score=health_summary.health_score,
                constitution_scores=health_summary.constitution_scores
            )
        except UserNotFoundError as e:
            logger.error(f"获取用户健康摘要失败: {e}")
            raise
        except ValueError:
            raise UserNotFoundError(f"用户ID '{user_id}' 格式无效")
    
    async def verify_user_identity(self, request: VerifyUserRequest) -> VerifyUserResponse:
        """
        验证用户身份
        
        Args:
            request: 验证用户请求
            
        Returns:
            VerifyUserResponse: 验证用户响应
        """
        try:
            # 这里我们将调用auth-service来验证token
            # 为了简化，这里仅做示例，实际应该调用auth服务
            # 这里简单地认为调用成功
            
            # 获取用户
            user = await self.user_repository.get_user_by_id(request.user_id)
            if not user:
                return VerifyUserResponse(is_valid=False)
            
            # 假设验证成功
            permissions = {}
            for role in user.roles:
                if role == UserRole.ADMIN:
                    permissions["users"] = "read,write,delete"
                    permissions["health"] = "read,write"
                elif role == UserRole.DOCTOR:
                    permissions["health"] = "read,write"
                elif role == UserRole.USER:
                    permissions["health"] = "read"
            
            return VerifyUserResponse(
                is_valid=True,
                roles=user.roles,
                permissions=permissions
            )
        except Exception as e:
            logger.error(f"验证用户失败: {e}")
            return VerifyUserResponse(is_valid=False)
    
    async def update_user_preferences(self, user_id: str,
                              request: UpdateUserPreferencesRequest) -> UserResponse:
        """
        更新用户偏好设置
        
        Args:
            user_id: 用户ID
            request: 更新用户偏好设置请求
            
        Returns:
            UserResponse: 更新后的用户响应
            
        Raises:
            UserNotFoundError: 当用户不存在时
        """
        try:
            user = await self.user_repository.update_user_preferences(
                user_id=UUID(user_id),
                preferences=request.preferences
            )
            
            return UserResponse(
                user_id=str(user.user_id),
                username=user.username,
                email=user.email,
                phone=user.phone,
                full_name=user.full_name,
                created_at=user.created_at,
                updated_at=user.updated_at,
                status=user.status,
                metadata=user.metadata,
                roles=user.roles,
                preferences=user.preferences
            )
        except UserNotFoundError as e:
            logger.error(f"更新用户偏好设置失败: {e}")
            raise
        except ValueError:
            raise UserNotFoundError(f"用户ID '{user_id}' 格式无效")
    
    async def bind_device(self, user_id: str, request: BindDeviceRequest) -> BindDeviceResponse:
        """
        绑定设备
        
        Args:
            user_id: 用户ID
            request: 绑定设备请求
            
        Returns:
            BindDeviceResponse: 绑定设备响应
            
        Raises:
            UserNotFoundError: 当用户不存在时
            DeviceAlreadyBoundError: 当设备已绑定时
        """
        try:
            binding_id = await self.user_repository.bind_device(
                user_id=UUID(user_id),
                device_id=request.device_id,
                device_type=request.device_type,
                device_name=request.device_name,
                device_metadata=request.device_metadata
            )
            
            return BindDeviceResponse(
                success=True,
                binding_id=binding_id,
                binding_time=datetime.now(timezone.utc),
                device_id=request.device_id,
                device_type=request.device_type
            )
        except (UserNotFoundError, DeviceAlreadyBoundError) as e:
            logger.error(f"绑定设备失败: {e}")
            raise
        except ValueError:
            raise UserNotFoundError(f"用户ID '{user_id}' 格式无效")
    
    async def unbind_device(self, user_id: str, device_id: str) -> bool:
        """
        解绑设备
        
        Args:
            user_id: 用户ID
            device_id: 设备ID
            
        Returns:
            bool: 是否解绑成功
            
        Raises:
            UserNotFoundError: 当用户不存在时
            DeviceNotFoundError: 当设备不存在或未绑定到该用户时
        """
        try:
            return await self.user_repository.unbind_device(
                user_id=UUID(user_id),
                device_id=device_id
            )
        except (UserNotFoundError, DeviceNotFoundError) as e:
            logger.error(f"解绑设备失败: {e}")
            raise
        except ValueError:
            raise UserNotFoundError(f"用户ID '{user_id}' 格式无效")
    
    async def get_user_devices(self, user_id: str) -> UserDevicesResponse:
        """
        获取用户设备列表
        
        Args:
            user_id: 用户ID
            
        Returns:
            UserDevicesResponse: 用户设备列表响应
            
        Raises:
            UserNotFoundError: 当用户不存在时
        """
        try:
            devices = await self.user_repository.get_user_devices(UUID(user_id))
            
            return UserDevicesResponse(
                user_id=user_id,
                devices=devices,
                total=len(devices)
            )
        except UserNotFoundError as e:
            logger.error(f"获取用户设备列表失败: {e}")
            raise
        except ValueError:
            raise UserNotFoundError(f"用户ID '{user_id}' 格式无效") 