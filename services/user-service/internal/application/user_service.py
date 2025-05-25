"""
用户应用服务层
实现用户相关的业务逻辑，使用依赖注入和缓存优化
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from uuid import UUID, uuid4

from pkg.cache.cache import CacheManager, cache_result
from pkg.errors.exceptions import (
    UserNotFoundError, UserAlreadyExistsError, InvalidCredentialsError,
    UserInactiveError, UserSuspendedError, ValidationError,
    DeviceNotFoundError, DeviceAlreadyBoundError, DeviceLimitExceededError,
    HealthDataNotFoundError
)
from pkg.security.auth import PasswordManager, JWTManager, PermissionManager, SecurityUtils
from internal.domain.user import User, UserStatus, UserRole
from internal.domain.repositories import UserRepository, HealthRepository, DeviceRepository
from internal.application.dto import (
    CreateUserRequest, UpdateUserRequest, UserResponse,
    LoginRequest, LoginResponse, BindDeviceRequest, BindDeviceResponse,
    UpdateUserHealthRequest, UserHealthSummaryResponse
)

logger = logging.getLogger(__name__)


class UserApplicationService:
    """用户应用服务"""
    
    def __init__(
        self,
        user_repository: UserRepository,
        health_repository: HealthRepository,
        device_repository: DeviceRepository,
        cache_manager: CacheManager,
        password_manager: PasswordManager,
        jwt_manager: JWTManager,
        permission_manager: PermissionManager
    ):
        self.user_repository = user_repository
        self.health_repository = health_repository
        self.device_repository = device_repository
        self._cache_manager = cache_manager
        self.password_manager = password_manager
        self.jwt_manager = jwt_manager
        self.permission_manager = permission_manager
        
        # 缓存配置
        self.user_cache_ttl = 300  # 5分钟
        self.health_cache_ttl = 600  # 10分钟
        self.device_cache_ttl = 300  # 5分钟
    
    async def create_user(self, request: CreateUserRequest) -> UserResponse:
        """
        创建新用户
        
        Args:
            request: 创建用户请求
            
        Returns:
            UserResponse: 用户响应
            
        Raises:
            UserAlreadyExistsError: 当用户名或邮箱已存在时
            ValidationError: 当输入数据无效时
        """
        logger.info(f"创建用户: {request.username}")
        
        # 验证输入数据
        await self._validate_create_user_request(request)
        
        # 检查用户是否已存在
        await self._check_user_exists(request.username, request.email)
        
        # 生成用户ID和密码哈希
        user_id = uuid4()
        password_hash = self.password_manager.hash_password(request.password)
        
        # 创建用户实体
        user = User(
            user_id=user_id,
            username=request.username,
            email=request.email,
            password_hash=password_hash,
            phone=request.phone,
            full_name=request.full_name,
            gender=request.gender,
            birth_date=request.birth_date,
            status=UserStatus.ACTIVE,
            roles=[UserRole.USER],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # 保存到数据库
        created_user = await self.user_repository.create(user)
        
        # 清除相关缓存
        await self._invalidate_user_cache(str(user_id))
        
        logger.info(f"用户创建成功: {created_user.user_id}")
        
        return self._map_user_to_response(created_user)
    
    async def authenticate_user(self, request: LoginRequest) -> LoginResponse:
        """
        用户认证
        
        Args:
            request: 登录请求
            
        Returns:
            LoginResponse: 登录响应
            
        Raises:
            InvalidCredentialsError: 当凭据无效时
            UserInactiveError: 当用户未激活时
            UserSuspendedError: 当用户被暂停时
        """
        logger.info(f"用户登录: {request.email}")
        
        # 获取用户
        user = await self.user_repository.get_by_email(request.email)
        if not user:
            raise InvalidCredentialsError()
        
        # 验证密码
        if not self.password_manager.verify_password(request.password, user.password_hash):
            raise InvalidCredentialsError()
        
        # 检查用户状态
        if user.status == UserStatus.INACTIVE:
            raise UserInactiveError()
        elif user.status == UserStatus.SUSPENDED:
            raise UserSuspendedError()
        
        # 获取用户权限
        permissions = self.permission_manager.get_permissions_for_roles(user.roles)
        
        # 生成令牌
        access_token = self.jwt_manager.create_access_token(
            user_id=str(user.user_id),
            roles=user.roles,
            permissions=permissions
        )
        refresh_token = self.jwt_manager.create_refresh_token(str(user.user_id))
        
        # 更新最后登录时间
        user.last_login_at = datetime.utcnow()
        await self.user_repository.update(user)
        
        # 清除用户缓存
        await self._invalidate_user_cache(str(user.user_id))
        
        logger.info(f"用户登录成功: {user.user_id}")
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=3600,
            user=self._map_user_to_response(user)
        )
    
    @cache_result(ttl=300)
    async def get_user(self, user_id: str, current_user_id: str, permissions: set) -> UserResponse:
        """
        获取用户信息
        
        Args:
            user_id: 用户ID
            current_user_id: 当前用户ID
            permissions: 当前用户权限
            
        Returns:
            UserResponse: 用户响应
            
        Raises:
            UserNotFoundError: 当用户不存在时
            AuthorizationError: 当权限不足时
        """
        # 检查权限
        if not self.permission_manager.can_access_user_data(permissions, user_id, current_user_id):
            from pkg.errors.exceptions import AuthorizationError
            raise AuthorizationError("无权访问该用户信息")
        
        user = await self.user_repository.get_by_id(UUID(user_id))
        if not user:
            raise UserNotFoundError(user_id)
        
        return self._map_user_to_response(user)
    
    async def update_user(
        self, 
        user_id: str, 
        request: UpdateUserRequest,
        current_user_id: str,
        permissions: set
    ) -> UserResponse:
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            request: 更新请求
            current_user_id: 当前用户ID
            permissions: 当前用户权限
            
        Returns:
            UserResponse: 更新后的用户响应
        """
        # 检查权限
        if not self.permission_manager.can_access_user_data(permissions, user_id, current_user_id):
            from pkg.errors.exceptions import AuthorizationError
            raise AuthorizationError("无权修改该用户信息")
        
        user = await self.user_repository.get_by_id(UUID(user_id))
        if not user:
            raise UserNotFoundError(user_id)
        
        # 验证更新数据
        await self._validate_update_user_request(request, user)
        
        # 更新用户信息
        if request.username:
            user.username = request.username
        if request.email:
            user.email = request.email
        if request.phone is not None:
            user.phone = request.phone
        if request.full_name is not None:
            user.full_name = request.full_name
        if request.gender:
            user.gender = request.gender
        if request.birth_date:
            user.birth_date = request.birth_date
        if request.avatar_url is not None:
            user.avatar_url = request.avatar_url
        
        user.updated_at = datetime.utcnow()
        
        # 保存更新
        updated_user = await self.user_repository.update(user)
        
        # 清除缓存
        await self._invalidate_user_cache(user_id)
        
        logger.info(f"用户信息更新成功: {user_id}")
        
        return self._map_user_to_response(updated_user)
    
    async def delete_user(self, user_id: str, current_user_id: str, permissions: set) -> bool:
        """
        删除用户（软删除）
        
        Args:
            user_id: 用户ID
            current_user_id: 当前用户ID
            permissions: 当前用户权限
            
        Returns:
            bool: 删除是否成功
        """
        # 检查权限
        if not ("user:delete" in permissions or 
                (user_id == current_user_id and "user:delete_own" in permissions)):
            from pkg.errors.exceptions import AuthorizationError
            raise AuthorizationError("无权删除该用户")
        
        user = await self.user_repository.get_by_id(UUID(user_id))
        if not user:
            raise UserNotFoundError(user_id)
        
        # 软删除：更新状态为已删除
        user.status = UserStatus.DELETED
        user.updated_at = datetime.utcnow()
        
        await self.user_repository.update(user)
        
        # 清除缓存
        await self._invalidate_user_cache(user_id)
        
        logger.info(f"用户删除成功: {user_id}")
        
        return True
    
    async def list_users(
        self, 
        offset: int = 0, 
        limit: int = 10,
        status: Optional[UserStatus] = None,
        permissions: set = None
    ) -> Tuple[List[UserResponse], int]:
        """
        获取用户列表
        
        Args:
            offset: 偏移量
            limit: 限制数量
            status: 用户状态过滤
            permissions: 当前用户权限
            
        Returns:
            Tuple[List[UserResponse], int]: 用户列表和总数
        """
        # 检查权限
        if not ("user:read" in permissions):
            from pkg.errors.exceptions import AuthorizationError
            raise AuthorizationError("无权查看用户列表")
        
        users, total = await self.user_repository.list_users(offset, limit, status)
        
        user_responses = [self._map_user_to_response(user) for user in users]
        
        return user_responses, total
    
    @cache_result(ttl=600)
    async def get_user_health_summary(
        self, 
        user_id: str,
        current_user_id: str,
        permissions: set
    ) -> UserHealthSummaryResponse:
        """
        获取用户健康摘要
        
        Args:
            user_id: 用户ID
            current_user_id: 当前用户ID
            permissions: 当前用户权限
            
        Returns:
            UserHealthSummaryResponse: 健康摘要响应
        """
        # 检查权限
        if not (self.permission_manager.can_access_user_data(permissions, user_id, current_user_id) or
                "health:read" in permissions):
            from pkg.errors.exceptions import AuthorizationError
            raise AuthorizationError("无权访问该用户健康数据")
        
        health_summary = await self.health_repository.get_user_health_summary(UUID(user_id))
        if not health_summary:
            raise HealthDataNotFoundError(user_id)
        
        return UserHealthSummaryResponse.from_domain(health_summary)
    
    async def bind_device(
        self, 
        user_id: str, 
        request: BindDeviceRequest,
        current_user_id: str,
        permissions: set
    ) -> BindDeviceResponse:
        """
        绑定设备
        
        Args:
            user_id: 用户ID
            request: 绑定设备请求
            current_user_id: 当前用户ID
            permissions: 当前用户权限
            
        Returns:
            BindDeviceResponse: 绑定响应
        """
        # 检查权限
        if not (user_id == current_user_id and "device:update_own" in permissions):
            from pkg.errors.exceptions import AuthorizationError
            raise AuthorizationError("无权绑定设备")
        
        # 检查用户是否存在
        user = await self.user_repository.get_by_id(UUID(user_id))
        if not user:
            raise UserNotFoundError(user_id)
        
        # 检查设备是否已被绑定
        existing_device = await self.device_repository.get_by_device_id(request.device_id)
        if existing_device:
            raise DeviceAlreadyBoundError(request.device_id)
        
        # 检查用户设备数量限制
        user_devices = await self.device_repository.get_user_devices(UUID(user_id))
        if len(user_devices) >= 10:  # 假设最多10个设备
            raise DeviceLimitExceededError(10)
        
        # 创建设备绑定
        binding_id = await self.device_repository.bind_device(
            user_id=UUID(user_id),
            device_id=request.device_id,
            device_type=request.device_type,
            device_name=request.device_name,
            platform=request.platform,
            os_version=request.os_version,
            app_version=request.app_version,
            push_token=request.push_token,
            device_metadata=request.device_metadata
        )
        
        # 清除设备缓存
        await self._invalidate_device_cache(user_id)
        
        logger.info(f"设备绑定成功: {user_id} -> {request.device_id}")
        
        return BindDeviceResponse(
            success=True,
            binding_id=binding_id,
            binding_time=datetime.utcnow(),
            device_id=request.device_id,
            device_type=request.device_type
        )
    
    # 私有方法
    async def _validate_create_user_request(self, request: CreateUserRequest):
        """验证创建用户请求"""
        errors = {}
        
        # 验证用户名
        if not request.username or len(request.username.strip()) < 3:
            errors["username"] = "用户名至少3个字符"
        elif len(request.username) > 50:
            errors["username"] = "用户名不能超过50个字符"
        
        # 验证邮箱
        if not SecurityUtils.validate_email(request.email):
            errors["email"] = "邮箱格式无效"
        
        # 验证密码强度
        password_check = self.password_manager.check_password_strength(request.password)
        if password_check["strength"] == "weak":
            errors["password"] = "密码强度不足: " + ", ".join(password_check["feedback"])
        
        # 验证手机号
        if request.phone and not SecurityUtils.validate_phone(request.phone):
            errors["phone"] = "手机号格式无效"
        
        if errors:
            raise ValidationError("输入数据验证失败", errors)
    
    async def _validate_update_user_request(self, request: UpdateUserRequest, current_user: User):
        """验证更新用户请求"""
        errors = {}
        
        # 验证用户名
        if request.username:
            if len(request.username.strip()) < 3:
                errors["username"] = "用户名至少3个字符"
            elif len(request.username) > 50:
                errors["username"] = "用户名不能超过50个字符"
            elif request.username != current_user.username:
                # 检查用户名是否已被使用
                existing_user = await self.user_repository.get_by_username(request.username)
                if existing_user and existing_user.user_id != current_user.user_id:
                    errors["username"] = "用户名已被使用"
        
        # 验证邮箱
        if request.email:
            if not SecurityUtils.validate_email(request.email):
                errors["email"] = "邮箱格式无效"
            elif request.email != current_user.email:
                # 检查邮箱是否已被使用
                existing_user = await self.user_repository.get_by_email(request.email)
                if existing_user and existing_user.user_id != current_user.user_id:
                    errors["email"] = "邮箱已被使用"
        
        # 验证手机号
        if request.phone and not SecurityUtils.validate_phone(request.phone):
            errors["phone"] = "手机号格式无效"
        
        if errors:
            raise ValidationError("输入数据验证失败", errors)
    
    async def _check_user_exists(self, username: str, email: str):
        """检查用户是否已存在"""
        # 检查用户名
        existing_user = await self.user_repository.get_by_username(username)
        if existing_user:
            raise UserAlreadyExistsError("username", username)
        
        # 检查邮箱
        existing_user = await self.user_repository.get_by_email(email)
        if existing_user:
            raise UserAlreadyExistsError("email", email)
    
    def _map_user_to_response(self, user: User) -> UserResponse:
        """将用户实体映射为响应对象"""
        return UserResponse(
            user_id=str(user.user_id),
            username=user.username,
            email=user.email,
            phone=user.phone,
            full_name=user.full_name,
            gender=user.gender,
            birth_date=user.birth_date,
            avatar_url=user.avatar_url,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=user.last_login_at,
            status=user.status,
            roles=user.roles,
            metadata=user.metadata or {},
            preferences=user.preferences or {}
        )
    
    async def _invalidate_user_cache(self, user_id: str):
        """清除用户相关缓存"""
        await self._cache_manager.delete(f"user:{user_id}")
        await self._cache_manager.delete(f"user_health:{user_id}")
    
    async def _invalidate_device_cache(self, user_id: str):
        """清除设备相关缓存"""
        await self._cache_manager.delete(f"user_devices:{user_id}") 