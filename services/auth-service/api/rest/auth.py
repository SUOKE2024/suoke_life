from typing import Dict, Any, Optional, List, Union
import logging
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, validator
import grpc
from datetime import datetime, timedelta
import jwt
from jwt.exceptions import PyJWTError

from services.auth_service.api.grpc import auth_pb2, auth_pb2_grpc
from services.auth_service.internal.config import settings
from services.auth_service.internal.observability.logging import get_logger

# 设置日志
logger = get_logger(__name__)

# 创建路由
router = APIRouter(tags=["auth"])

# JWT配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 认证请求模型
class LoginRequest(BaseModel):
    """用户登录请求模型"""
    username: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    password: str
    auth_method: str = "PASSWORD"
    mfa_code: Optional[str] = None
    
    @validator('auth_method')
    def validate_auth_method(cls, v):
        """验证认证方法"""
        valid_methods = ["PASSWORD", "SMS_CODE", "EMAIL_CODE", "OAUTH", "MFA"]
        if v.upper() not in valid_methods:
            raise ValueError(f"无效的认证方法: {v}. 有效方法: {', '.join(valid_methods)}")
        return v.upper()
    
    @validator('username', 'email', 'mobile')
    def validate_identifier(cls, v, values):
        """确保至少提供一种身份标识符"""
        if not v and not values.get('username') and not values.get('email') and not values.get('mobile'):
            raise ValueError("必须提供用户名、邮箱或手机号中的至少一项")
        return v

class RegisterRequest(BaseModel):
    """用户注册请求模型"""
    username: Optional[str] = None
    email: Optional[str] = None
    mobile: str
    password: str
    nickname: str
    verification_code: str
    profile_data: Dict[str, str] = Field(default_factory=dict)
    
    @validator('password')
    def validate_password(cls, v):
        """验证密码强度"""
        if len(v) < 6:
            raise ValueError("密码长度不能少于6位")
        return v

class RefreshTokenRequest(BaseModel):
    """刷新令牌请求模型"""
    refresh_token: str

class VerifyTokenRequest(BaseModel):
    """验证令牌请求模型"""
    token: str

class ResetPasswordRequest(BaseModel):
    """重置密码请求模型"""
    email: Optional[str] = None
    mobile: Optional[str] = None
    verification_code: str
    new_password: str
    
    @validator('email', 'mobile')
    def validate_identifier(cls, v, values):
        """确保提供邮箱或手机号"""
        if not v and not values.get('email') and not values.get('mobile'):
            raise ValueError("必须提供邮箱或手机号")
        return v

class VerificationCodeRequest(BaseModel):
    """发送验证码请求模型"""
    mobile: Optional[str] = None
    email: Optional[str] = None
    type: str = "register"  # register, login, reset-password
    
    @validator('mobile', 'email')
    def validate_contact(cls, v, values):
        """确保提供联系方式"""
        if not v and not values.get('mobile') and not values.get('email'):
            raise ValueError("必须提供手机号或邮箱")
        return v

class MFARequest(BaseModel):
    """多因素认证请求模型"""
    mfa_type: str
    
    @validator('mfa_type')
    def validate_mfa_type(cls, v):
        """验证MFA类型"""
        valid_types = ["TOTP", "SMS", "EMAIL"]
        if v.upper() not in valid_types:
            raise ValueError(f"无效的MFA类型: {v}. 有效类型: {', '.join(valid_types)}")
        return v.upper()

class VerifyMFARequest(BaseModel):
    """验证MFA请求模型"""
    user_id: str
    mfa_code: str
    mfa_token: str

class PermissionRequest(BaseModel):
    """检查权限请求模型"""
    permission: str
    resource_id: Optional[str] = None

# 认证处理器
class AuthHandler:
    """处理与认证相关的API请求"""
    
    def __init__(self, auth_client: auth_pb2_grpc.AuthServiceStub, jwt_secret: str):
        """初始化认证处理器
        
        Args:
            auth_client: gRPC认证服务客户端
            jwt_secret: JWT签名密钥
        """
        self.auth_client = auth_client
        self.jwt_secret = jwt_secret
        
    def register_routes(self, router: APIRouter):
        """注册路由
        
        Args:
            router: FastAPI路由器
        """
        # 认证路由
        router.post("/register", response_model=Dict[str, Any])(self.register)
        router.post("/login", response_model=Dict[str, Any])(self.login)
        router.post("/logout", response_model=Dict[str, Any])(self.logout)
        router.post("/refresh-token", response_model=Dict[str, Any])(self.refresh_token)
        router.post("/verify-token", response_model=Dict[str, Any])(self.verify_token)
        router.post("/reset-password", response_model=Dict[str, Any])(self.reset_password)
        router.post("/send-verification-code", response_model=Dict[str, Any])(self.send_verification_code)
        router.post("/enable-mfa", response_model=Dict[str, Any])(self.enable_mfa)
        router.post("/verify-mfa", response_model=Dict[str, Any])(self.verify_mfa)
        
        # 用户路由
        router.get("/user/roles", response_model=Dict[str, Any])(self.get_user_roles)
        router.post("/user/check-permission", response_model=Dict[str, Any])(self.check_permission)
    
    async def register(self, request: RegisterRequest) -> Dict[str, Any]:
        """用户注册
        
        Args:
            request: 注册请求参数
            
        Returns:
            注册响应
        """
        try:
            # 准备gRPC请求
            grpc_req = auth_pb2.RegisterRequest(
                username=request.username or request.mobile,
                email=request.email,
                password=request.password,
                phone_number=request.mobile,
                profile_data=request.profile_data
            )
            
            # 调用gRPC服务
            response = self.auth_client.Register(grpc_req)
            
            # 返回响应
            return {
                "success": response.success,
                "message": response.message,
                "data": {
                    "user_id": response.user_id,
                    "username": response.username,
                    "email": response.email
                }
            }
        except grpc.RpcError as e:
            # 处理gRPC错误
            logger.error(f"注册服务调用失败: {e}")
            status_code = self._grpc_status_to_http(e.code())
            raise HTTPException(
                status_code=status_code,
                detail=e.details() if hasattr(e, 'details') else "注册服务暂时不可用"
            )
    
    async def login(self, request: LoginRequest) -> Dict[str, Any]:
        """用户登录
        
        Args:
            request: 登录请求参数
            
        Returns:
            登录响应，包含访问令牌
        """
        try:
            # 准备gRPC请求
            grpc_req = auth_pb2.LoginRequest(
                password=request.password,
                mfa_code=request.mfa_code,
                auth_method=self._convert_auth_method(request.auth_method)
            )
            
            # 设置标识符
            if request.username:
                grpc_req.username = request.username
            elif request.email:
                grpc_req.email = request.email
            elif request.mobile:
                grpc_req.phone_number = request.mobile
            
            # 调用gRPC服务
            response = self.auth_client.Login(grpc_req)
            
            # 返回响应
            return {
                "success": response.success,
                "message": response.message,
                "data": {
                    "access_token": response.access_token,
                    "refresh_token": response.refresh_token,
                    "token_type": response.token_type,
                    "expires_in": response.expires_in,
                    "mfa_required": response.mfa_required,
                    "mfa_token": response.mfa_token,
                    "user_info": self._extract_user_info(response)
                }
            }
        except grpc.RpcError as e:
            # 处理gRPC错误
            logger.error(f"登录服务调用失败: {e}")
            status_code = self._grpc_status_to_http(e.code())
            raise HTTPException(
                status_code=status_code,
                detail=e.details() if hasattr(e, 'details') else "登录服务暂时不可用"
            )
    
    async def logout(self, request: Request) -> Dict[str, Any]:
        """用户登出
        
        Args:
            request: HTTP请求，用于提取令牌
            
        Returns:
            登出响应
        """
        try:
            # 提取令牌
            token = self._extract_token(request)
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的认证凭据"
                )
            
            # 调用gRPC服务
            response = self.auth_client.Logout(auth_pb2.LogoutRequest(
                access_token=token
            ))
            
            # 返回响应
            return {
                "success": response.success,
                "message": response.message
            }
        except grpc.RpcError as e:
            # 处理gRPC错误
            logger.error(f"登出服务调用失败: {e}")
            status_code = self._grpc_status_to_http(e.code())
            raise HTTPException(
                status_code=status_code,
                detail=e.details() if hasattr(e, 'details') else "登出服务暂时不可用"
            )
    
    async def refresh_token(self, request: RefreshTokenRequest) -> Dict[str, Any]:
        """刷新访问令牌
        
        Args:
            request: 刷新令牌请求参数
            
        Returns:
            新的访问令牌
        """
        try:
            # 调用gRPC服务
            response = self.auth_client.RefreshToken(auth_pb2.RefreshTokenRequest(
                refresh_token=request.refresh_token
            ))
            
            # 返回响应
            return {
                "success": response.success,
                "message": response.message,
                "data": {
                    "access_token": response.access_token,
                    "refresh_token": response.refresh_token,
                    "token_type": response.token_type,
                    "expires_in": response.expires_in
                }
            }
        except grpc.RpcError as e:
            # 处理gRPC错误
            logger.error(f"刷新令牌服务调用失败: {e}")
            status_code = self._grpc_status_to_http(e.code())
            raise HTTPException(
                status_code=status_code,
                detail=e.details() if hasattr(e, 'details') else "刷新令牌服务暂时不可用"
            )
    
    async def verify_token(self, request: VerifyTokenRequest) -> Dict[str, Any]:
        """验证令牌
        
        Args:
            request: 验证令牌请求参数
            
        Returns:
            令牌验证结果
        """
        try:
            # 调用gRPC服务
            response = self.auth_client.VerifyToken(auth_pb2.VerifyTokenRequest(
                token=request.token
            ))
            
            # 返回响应
            return {
                "success": response.valid,
                "message": response.message,
                "data": {
                    "valid": response.valid,
                    "user_id": response.user_id,
                    "permissions": list(response.permissions),
                    "roles": list(response.roles)
                }
            }
        except grpc.RpcError as e:
            # 处理gRPC错误
            logger.error(f"验证令牌服务调用失败: {e}")
            status_code = self._grpc_status_to_http(e.code())
            raise HTTPException(
                status_code=status_code,
                detail=e.details() if hasattr(e, 'details') else "验证令牌服务暂时不可用"
            )
    
    async def reset_password(self, request: ResetPasswordRequest) -> Dict[str, Any]:
        """重置密码
        
        Args:
            request: 重置密码请求参数
            
        Returns:
            重置密码结果
        """
        try:
            # 准备gRPC请求
            grpc_req = auth_pb2.ResetPasswordRequest(
                verification_code=request.verification_code,
                new_password=request.new_password
            )
            
            # 设置身份标识符
            if request.email:
                grpc_req.email = request.email
            elif request.mobile:
                grpc_req.phone_number = request.mobile
            
            # 调用gRPC服务
            response = self.auth_client.ResetPassword(grpc_req)
            
            # 返回响应
            return {
                "success": response.success,
                "message": response.message
            }
        except grpc.RpcError as e:
            # 处理gRPC错误
            logger.error(f"重置密码服务调用失败: {e}")
            status_code = self._grpc_status_to_http(e.code())
            raise HTTPException(
                status_code=status_code,
                detail=e.details() if hasattr(e, 'details') else "重置密码服务暂时不可用"
            )
    
    async def send_verification_code(self, request: VerificationCodeRequest) -> Dict[str, Any]:
        """发送验证码
        
        Args:
            request: 发送验证码请求参数
            
        Returns:
            发送验证码结果
        """
        # 这里应该调用短信或邮件服务发送验证码
        # 目前仅模拟成功响应
        return {
            "success": True,
            "message": "验证码已发送",
            "data": {
                "expiry": 300  # 验证码有效期，单位秒
            }
        }
    
    async def enable_mfa(self, request: MFARequest, user_request: Request) -> Dict[str, Any]:
        """启用多因素认证
        
        Args:
            request: MFA请求参数
            user_request: HTTP请求，用于提取用户信息
            
        Returns:
            MFA配置结果
        """
        try:
            # 获取用户ID
            token_data = self._decode_token(self._extract_token(user_request))
            if not token_data or "sub" not in token_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的认证凭据"
                )
            
            user_id = token_data["sub"]
            
            # 调用gRPC服务
            response = self.auth_client.EnableMFA(auth_pb2.EnableMFARequest(
                user_id=user_id,
                mfa_type=self._convert_mfa_type(request.mfa_type)
            ))
            
            # 返回响应
            return {
                "success": response.success,
                "message": response.message,
                "data": {
                    "secret_key": response.secret_key,
                    "qr_code_url": response.qr_code_url
                }
            }
        except grpc.RpcError as e:
            # 处理gRPC错误
            logger.error(f"启用MFA服务调用失败: {e}")
            status_code = self._grpc_status_to_http(e.code())
            raise HTTPException(
                status_code=status_code,
                detail=e.details() if hasattr(e, 'details') else "启用MFA服务暂时不可用"
            )
    
    async def verify_mfa(self, request: VerifyMFARequest) -> Dict[str, Any]:
        """验证多因素认证
        
        Args:
            request: 验证MFA请求参数
            
        Returns:
            验证结果和访问令牌
        """
        try:
            # 调用gRPC服务
            response = self.auth_client.VerifyMFA(auth_pb2.VerifyMFARequest(
                user_id=request.user_id,
                mfa_code=request.mfa_code,
                mfa_token=request.mfa_token
            ))
            
            # 返回响应
            return {
                "success": response.success,
                "message": response.message,
                "data": {
                    "access_token": response.access_token,
                    "refresh_token": response.refresh_token,
                    "token_type": response.token_type,
                    "expires_in": response.expires_in
                }
            }
        except grpc.RpcError as e:
            # 处理gRPC错误
            logger.error(f"验证MFA服务调用失败: {e}")
            status_code = self._grpc_status_to_http(e.code())
            raise HTTPException(
                status_code=status_code,
                detail=e.details() if hasattr(e, 'details') else "验证MFA服务暂时不可用"
            )
    
    async def get_user_roles(self, request: Request) -> Dict[str, Any]:
        """获取用户角色
        
        Args:
            request: HTTP请求，用于提取用户信息
            
        Returns:
            用户角色列表
        """
        try:
            # 获取用户ID
            token_data = self._decode_token(self._extract_token(request))
            if not token_data or "sub" not in token_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的认证凭据"
                )
            
            user_id = token_data["sub"]
            
            # 调用gRPC服务
            response = self.auth_client.GetUserRoles(auth_pb2.GetUserRolesRequest(
                user_id=user_id
            ))
            
            # 构造角色列表
            roles = [
                {
                    "id": role.id,
                    "name": role.name,
                    "description": role.description,
                    "permissions": list(role.permissions)
                }
                for role in response.roles
            ]
            
            # 返回响应
            return {
                "success": response.success,
                "message": response.message,
                "data": {
                    "roles": roles
                }
            }
        except grpc.RpcError as e:
            # 处理gRPC错误
            logger.error(f"获取角色服务调用失败: {e}")
            status_code = self._grpc_status_to_http(e.code())
            raise HTTPException(
                status_code=status_code,
                detail=e.details() if hasattr(e, 'details') else "获取角色服务暂时不可用"
            )
    
    async def check_permission(self, request: PermissionRequest, user_request: Request) -> Dict[str, Any]:
        """检查用户权限
        
        Args:
            request: 权限检查请求参数
            user_request: HTTP请求，用于提取用户信息
            
        Returns:
            权限检查结果
        """
        try:
            # 获取用户ID
            token_data = self._decode_token(self._extract_token(user_request))
            if not token_data or "sub" not in token_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的认证凭据"
                )
            
            user_id = token_data["sub"]
            
            # 调用gRPC服务
            response = self.auth_client.CheckPermission(auth_pb2.CheckPermissionRequest(
                user_id=user_id,
                permission=request.permission,
                resource_id=request.resource_id or ""
            ))
            
            # 返回响应
            return {
                "success": True,
                "message": response.message,
                "data": {
                    "has_permission": response.has_permission
                }
            }
        except grpc.RpcError as e:
            # 处理gRPC错误
            logger.error(f"检查权限服务调用失败: {e}")
            status_code = self._grpc_status_to_http(e.code())
            raise HTTPException(
                status_code=status_code,
                detail=e.details() if hasattr(e, 'details') else "检查权限服务暂时不可用"
            )
    
    # 工具方法
    def _extract_token(self, request: Request) -> Optional[str]:
        """从请求中提取令牌
        
        Args:
            request: HTTP请求
            
        Returns:
            令牌字符串，如果不存在则返回None
        """
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None
        
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None
        
        return parts[1]
    
    def _decode_token(self, token: Optional[str]) -> Dict[str, Any]:
        """解码JWT令牌
        
        Args:
            token: JWT令牌
            
        Returns:
            解码后的令牌数据
        """
        if not token:
            return {}
        
        try:
            return jwt.decode(
                token,
                self.jwt_secret,
                algorithms=["HS256"]
            )
        except PyJWTError as e:
            logger.error(f"令牌解码失败: {e}")
            return {}
    
    def _extract_user_info(self, login_response) -> Dict[str, Any]:
        """从登录响应中提取用户信息
        
        通常可能需要解析JWT或调用附加服务获取完整用户信息，
        这里简单模拟一个用户信息。实际应用中应根据业务逻辑进行实现。
        
        Args:
            login_response: 登录响应
            
        Returns:
            用户信息字典
        """
        # 从令牌中获取用户ID
        try:
            token_data = jwt.decode(
                login_response.access_token,
                self.jwt_secret,
                algorithms=["HS256"],
                options={"verify_signature": False}  # 仅解析，不验证
            )
            
            # 这里仅模拟，实际应取自数据库或缓存
            return {
                "id": token_data.get("sub", ""),
                "nickname": "用户_" + token_data.get("sub", "")[-6:],
                "avatar": "",
                "healthScore": 85,
                "constitutionType": "平和质"
            }
        except PyJWTError:
            # 解析失败时返回默认值
            return {
                "id": "",
                "nickname": "默认用户",
                "avatar": "",
                "healthScore": 80,
                "constitutionType": "未知"
            }
    
    def _convert_auth_method(self, method: str) -> int:
        """转换认证方法字符串为枚举值
        
        Args:
            method: 认证方法字符串
            
        Returns:
            对应的gRPC枚举值
        """
        method_map = {
            "PASSWORD": auth_pb2.AuthMethod.PASSWORD,
            "SMS_CODE": auth_pb2.AuthMethod.SMS_CODE,
            "EMAIL_CODE": auth_pb2.AuthMethod.EMAIL_CODE,
            "OAUTH": auth_pb2.AuthMethod.OAUTH,
            "MFA": auth_pb2.AuthMethod.MFA
        }
        return method_map.get(method.upper(), auth_pb2.AuthMethod.PASSWORD)
    
    def _convert_mfa_type(self, mfa_type: str) -> int:
        """转换MFA类型字符串为枚举值
        
        Args:
            mfa_type: MFA类型字符串
            
        Returns:
            对应的gRPC枚举值
        """
        type_map = {
            "TOTP": auth_pb2.MFAType.TOTP,
            "SMS": auth_pb2.MFAType.SMS,
            "EMAIL": auth_pb2.MFAType.EMAIL
        }
        return type_map.get(mfa_type.upper(), auth_pb2.MFAType.TOTP)
    
    def _grpc_status_to_http(self, grpc_code: grpc.StatusCode) -> int:
        """将gRPC状态码转换为HTTP状态码
        
        Args:
            grpc_code: gRPC状态码
            
        Returns:
            对应的HTTP状态码
        """
        code_map = {
            grpc.StatusCode.OK: status.HTTP_200_OK,
            grpc.StatusCode.CANCELLED: status.HTTP_408_REQUEST_TIMEOUT,
            grpc.StatusCode.UNKNOWN: status.HTTP_500_INTERNAL_SERVER_ERROR,
            grpc.StatusCode.INVALID_ARGUMENT: status.HTTP_400_BAD_REQUEST,
            grpc.StatusCode.DEADLINE_EXCEEDED: status.HTTP_504_GATEWAY_TIMEOUT,
            grpc.StatusCode.NOT_FOUND: status.HTTP_404_NOT_FOUND,
            grpc.StatusCode.ALREADY_EXISTS: status.HTTP_409_CONFLICT,
            grpc.StatusCode.PERMISSION_DENIED: status.HTTP_403_FORBIDDEN,
            grpc.StatusCode.UNAUTHENTICATED: status.HTTP_401_UNAUTHORIZED,
            grpc.StatusCode.RESOURCE_EXHAUSTED: status.HTTP_429_TOO_MANY_REQUESTS,
            grpc.StatusCode.FAILED_PRECONDITION: status.HTTP_412_PRECONDITION_FAILED,
            grpc.StatusCode.ABORTED: status.HTTP_409_CONFLICT,
            grpc.StatusCode.OUT_OF_RANGE: status.HTTP_400_BAD_REQUEST,
            grpc.StatusCode.UNIMPLEMENTED: status.HTTP_501_NOT_IMPLEMENTED,
            grpc.StatusCode.INTERNAL: status.HTTP_500_INTERNAL_SERVER_ERROR,
            grpc.StatusCode.UNAVAILABLE: status.HTTP_503_SERVICE_UNAVAILABLE,
            grpc.StatusCode.DATA_LOSS: status.HTTP_500_INTERNAL_SERVER_ERROR
        }
        return code_map.get(grpc_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


# 创建认证处理器对象的工厂函数
def create_auth_handler(auth_client: auth_pb2_grpc.AuthServiceStub) -> AuthHandler:
    """创建认证处理器实例
    
    Args:
        auth_client: gRPC认证服务客户端
        
    Returns:
        认证处理器实例
    """
    jwt_secret = settings.JWT_SECRET_KEY
    return AuthHandler(auth_client, jwt_secret)


# 依赖项：用于路由保护
def get_current_user(
    request: Request,
    auth_client: auth_pb2_grpc.AuthServiceStub = Depends(lambda: get_auth_client())
) -> Dict[str, Any]:
    """获取当前用户
    
    Args:
        request: HTTP请求
        auth_client: gRPC认证服务客户端
        
    Returns:
        当前用户信息，如未认证则抛出异常
    """
    auth_handler = create_auth_handler(auth_client)
    token = auth_handler._extract_token(request)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少认证令牌",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        response = auth_client.VerifyToken(auth_pb2.VerifyTokenRequest(
            token=token
        ))
        
        if not response.valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证令牌",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return {
            "user_id": response.user_id,
            "permissions": list(response.permissions),
            "roles": list(response.roles)
        }
    except grpc.RpcError as e:
        logger.error(f"验证令牌失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证服务暂时不可用",
            headers={"WWW-Authenticate": "Bearer"}
        )


# gRPC客户端获取函数
def get_auth_client() -> auth_pb2_grpc.AuthServiceStub:
    """获取gRPC认证服务客户端
    
    Returns:
        gRPC认证服务客户端
    """
    channel = grpc.insecure_channel(f"{settings.AUTH_SERVICE_HOST}:{settings.AUTH_SERVICE_PORT}")
    return auth_pb2_grpc.AuthServiceStub(channel) 