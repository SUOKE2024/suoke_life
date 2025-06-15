#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
认证路由处理器

处理用户认证相关的HTTP请求，包括登录、注册、令牌管理、密码重置、MFA等。
"""
import logging
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm

from ...model.user import User, UserCreate, UserResponse, UserUpdate
from ...schemas.auth import (
    TokenResponse, RefreshRequest, RegisterRequest, ResetPasswordRequest,
    MFASetupResponse, MFAVerifyRequest, VerifyTokenRequest, LoginResponse
)
from ...service.auth_service_complete import AuthService, get_auth_service
from ...service.user_service import UserService, get_user_service
from ...service.metrics_service import MetricsService, get_metrics_service

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/auth", tags=["认证"])


class AuthHandler:
    """认证路由处理器类"""
    
    def __init__(
        self,
        auth_service: AuthService,
        user_service: UserService,
        metrics_service: MetricsService
    ):
        self.auth_service = auth_service
        self.user_service = user_service
        self.metrics_service = metrics_service
    
    async def login(
        self,
        request: Request,
        form_data: OAuth2PasswordRequestForm
    ) -> TokenResponse:
        """
        用户登录获取访问令牌
        
        Args:
            request: HTTP请求对象
            form_data: 登录表单数据
        
        Returns:
            TokenResponse: 令牌响应
        
        Raises:
            HTTPException: 认证失败
        """
        logger.info(f"用户登录请求: {form_data.username}")
        
        try:
            # 获取客户端IP地址
            client_ip = self._get_client_ip(request)
            
            # 获取设备信息
            device_info = self._get_device_info(request)
            
            # 验证用户凭据
            user = await self.auth_service.authenticate_user(
                username=form_data.username,
                password=form_data.password,
                ip_address=client_ip
            )
            
            if not user:
                # 记录失败指标
                await self.metrics_service.increment_counter(
                    "auth_login_failures_total",
                    {"reason": "invalid_credentials"}
                )
                
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户名或密码不正确",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # 创建令牌
            tokens = await self.auth_service.create_tokens(user, device_info)
            
            # 记录成功指标
            await self.metrics_service.increment_counter(
                "auth_login_success_total",
                {"user_id": str(user.id)}
            )
            
            return TokenResponse(**tokens)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"登录处理失败: {str(e)}")
            await self.metrics_service.increment_counter(
                "auth_login_errors_total",
                {"error": "system_error"}
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="登录处理失败"
            )
    
    async def register(
        self,
        request: Request,
        user_data: RegisterRequest
    ) -> UserResponse:
        """
        用户注册
        
        Args:
            request: HTTP请求对象
            user_data: 注册数据
        
        Returns:
            UserResponse: 用户响应
        
        Raises:
            HTTPException: 注册失败
        """
        logger.info(f"用户注册请求: {user_data.username}")
        
        try:
            # 获取客户端IP地址
            client_ip = self._get_client_ip(request)
            
            # 创建用户数据
            user_create = UserCreate(
                username=user_data.username,
                email=user_data.email,
                password=user_data.password,
                phone_number=user_data.phone_number,
                profile_data=user_data.profile_data
            )
            
            # 创建用户
            user = await self.user_service.create_user(user_create, client_ip)
            
            # 记录成功指标
            await self.metrics_service.increment_counter(
                "auth_register_success_total",
                {"user_id": str(user.id)}
            )
            
            return UserResponse.from_orm(user)
            
        except ValueError as e:
            logger.warning(f"用户注册失败: {str(e)}")
            await self.metrics_service.increment_counter(
                "auth_register_failures_total",
                {"reason": "validation_error"}
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        except Exception as e:
            logger.error(f"注册处理失败: {str(e)}")
            await self.metrics_service.increment_counter(
                "auth_register_errors_total",
                {"error": "system_error"}
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="注册处理失败"
            )
    
    async def refresh_token(
        self,
        request: Request,
        refresh_data: RefreshRequest
    ) -> TokenResponse:
        """
        使用刷新令牌获取新的访问令牌
        
        Args:
            request: HTTP请求对象
            refresh_data: 刷新令牌数据
        
        Returns:
            TokenResponse: 新令牌响应
        
        Raises:
            HTTPException: 刷新失败
        """
        logger.info("刷新令牌请求")
        
        try:
            # 获取设备信息
            device_info = self._get_device_info(request)
            
            # 刷新令牌
            tokens = await self.auth_service.refresh_tokens(
                refresh_token=refresh_data.refresh_token,
                device_info=device_info
            )
            
            # 记录成功指标
            await self.metrics_service.increment_counter(
                "auth_token_refresh_success_total"
            )
            
            return TokenResponse(**tokens)
            
        except ValueError as e:
            logger.warning(f"令牌刷新失败: {str(e)}")
            await self.metrics_service.increment_counter(
                "auth_token_refresh_failures_total",
                {"reason": "invalid_token"}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error(f"刷新令牌处理失败: {str(e)}")
            await self.metrics_service.increment_counter(
                "auth_token_refresh_errors_total",
                {"error": "system_error"}
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="刷新令牌处理失败"
            )
    
    async def logout(
        self,
        request: Request,
        current_user: User,
        refresh_token: Optional[str] = None
    ) -> Dict[str, str]:
        """
        用户登出，使当前令牌失效
        
        Args:
            request: HTTP请求对象
            current_user: 当前用户
            refresh_token: 刷新令牌（可选）
        
        Returns:
            Dict[str, str]: 登出响应
        """
        logger.info(f"用户登出请求: {current_user.id}")
        
        try:
            # 登出用户
            await self.auth_service.logout(current_user, refresh_token)
            
            # 记录成功指标
            await self.metrics_service.increment_counter(
                "auth_logout_success_total",
                {"user_id": str(current_user.id)}
            )
            
            return {"detail": "登出成功"}
            
        except Exception as e:
            logger.error(f"登出处理失败: {str(e)}")
            await self.metrics_service.increment_counter(
                "auth_logout_errors_total",
                {"error": "system_error"}
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="登出处理失败"
            )
    
    async def verify_token(
        self,
        verify_data: VerifyTokenRequest
    ) -> Dict[str, Any]:
        """
        验证访问令牌有效性
        
        Args:
            verify_data: 验证令牌数据
        
        Returns:
            Dict[str, Any]: 验证结果
        """
        logger.info("验证令牌请求")
        
        try:
            # 验证令牌
            user = await self.auth_service.verify_token(verify_data.token)
            
            return {
                "valid": True,
                "user_id": str(user.id),
                "username": user.username,
                "email": user.email,
                "status": user.status,
                "permissions": await self.auth_service._get_user_permissions(user)
            }
            
        except ValueError as e:
            logger.warning(f"令牌验证失败: {str(e)}")
            return {
                "valid": False,
                "detail": str(e)
            }
        except Exception as e:
            logger.error(f"验证令牌处理失败: {str(e)}")
            return {
                "valid": False,
                "detail": "系统错误"
            }
    
    async def request_password_reset(
        self,
        request: Request,
        email: str
    ) -> Dict[str, str]:
        """
        请求密码重置，发送重置邮件
        
        Args:
            request: HTTP请求对象
            email: 用户邮箱
        
        Returns:
            Dict[str, str]: 重置请求响应
        """
        logger.info(f"密码重置请求: {email}")
        
        try:
            # 获取客户端IP地址
            client_ip = self._get_client_ip(request)
            
            # 发送重置邮件
            await self.auth_service.send_password_reset(email, client_ip)
            
            # 记录成功指标
            await self.metrics_service.increment_counter(
                "auth_password_reset_request_total"
            )
            
            return {"detail": "如果邮箱存在，重置邮件已发送"}
            
        except ValueError as e:
            logger.warning(f"密码重置请求失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        except Exception as e:
            logger.error(f"密码重置请求处理失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="密码重置请求处理失败"
            )
    
    async def reset_password(
        self,
        request: Request,
        reset_data: ResetPasswordRequest
    ) -> Dict[str, str]:
        """
        重置密码
        
        Args:
            request: HTTP请求对象
            reset_data: 重置密码数据
        
        Returns:
            Dict[str, str]: 重置响应
        """
        logger.info("密码重置执行")
        
        try:
            # 获取客户端IP地址
            client_ip = self._get_client_ip(request)
            
            # 重置密码
            await self.auth_service.reset_password(
                token=reset_data.token,
                new_password=reset_data.new_password,
                ip_address=client_ip
            )
            
            # 记录成功指标
            await self.metrics_service.increment_counter(
                "auth_password_reset_success_total"
            )
            
            return {"detail": "密码重置成功"}
            
        except ValueError as e:
            logger.warning(f"密码重置失败: {str(e)}")
            await self.metrics_service.increment_counter(
                "auth_password_reset_failures_total",
                {"reason": "validation_error"}
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        except Exception as e:
            logger.error(f"密码重置处理失败: {str(e)}")
            await self.metrics_service.increment_counter(
                "auth_password_reset_errors_total",
                {"error": "system_error"}
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="密码重置处理失败"
            )
    
    async def setup_mfa(
        self,
        current_user: User,
        mfa_type: str
    ) -> MFASetupResponse:
        """
        设置多因素认证
        
        Args:
            current_user: 当前用户
            mfa_type: MFA类型
        
        Returns:
            MFASetupResponse: MFA设置响应
        """
        logger.info(f"MFA设置请求: {current_user.id}, 类型: {mfa_type}")
        
        try:
            # 设置MFA
            setup_data = await self.auth_service.setup_mfa(current_user, mfa_type)
            
            # 记录成功指标
            await self.metrics_service.increment_counter(
                "auth_mfa_setup_total",
                {"user_id": str(current_user.id), "type": mfa_type}
            )
            
            return MFASetupResponse(**setup_data)
            
        except ValueError as e:
            logger.warning(f"MFA设置失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        except Exception as e:
            logger.error(f"MFA设置处理失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="MFA设置处理失败"
            )
    
    async def verify_mfa(
        self,
        current_user: User,
        verify_data: MFAVerifyRequest,
        mfa_type: Optional[str] = None
    ) -> Dict[str, str]:
        """
        验证多因素认证代码
        
        Args:
            current_user: 当前用户
            verify_data: MFA验证数据
            mfa_type: MFA类型（可选，用于设置阶段）
        
        Returns:
            Dict[str, str]: 验证响应
        """
        logger.info(f"MFA验证请求: {current_user.id}")
        
        try:
            # 验证MFA代码
            result = await self.auth_service.verify_mfa(
                user=current_user,
                code=verify_data.code,
                mfa_type=mfa_type
            )
            
            if result:
                # 记录成功指标
                await self.metrics_service.increment_counter(
                    "auth_mfa_verify_success_total",
                    {"user_id": str(current_user.id)}
                )
                
                message = "多因素认证验证成功"
                if mfa_type:
                    message = "多因素认证设置成功"
                
                return {"detail": message}
            else:
                # 记录失败指标
                await self.metrics_service.increment_counter(
                    "auth_mfa_verify_failures_total",
                    {"user_id": str(current_user.id), "reason": "invalid_code"}
                )
                
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="验证码无效",
                )
                
        except HTTPException:
            raise
        except ValueError as e:
            logger.warning(f"MFA验证失败: {str(e)}")
            await self.metrics_service.increment_counter(
                "auth_mfa_verify_failures_total",
                {"user_id": str(current_user.id), "reason": "validation_error"}
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        except Exception as e:
            logger.error(f"MFA验证处理失败: {str(e)}")
            await self.metrics_service.increment_counter(
                "auth_mfa_verify_errors_total",
                {"error": "system_error"}
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="MFA验证处理失败"
            )
    
    async def disable_mfa(
        self,
        current_user: User
    ) -> Dict[str, str]:
        """
        禁用多因素认证
        
        Args:
            current_user: 当前用户
        
        Returns:
            Dict[str, str]: 禁用响应
        """
        logger.info(f"MFA禁用请求: {current_user.id}")
        
        try:
            # 禁用MFA
            await self.auth_service.disable_mfa(current_user)
            
            # 记录成功指标
            await self.metrics_service.increment_counter(
                "auth_mfa_disable_total",
                {"user_id": str(current_user.id)}
            )
            
            return {"detail": "多因素认证已禁用"}
            
        except ValueError as e:
            logger.warning(f"MFA禁用失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        except Exception as e:
            logger.error(f"MFA禁用处理失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="MFA禁用处理失败"
            )
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP地址"""
        # 检查代理头
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # 回退到直接连接IP
        return request.client.host if request.client else "unknown"
    
    def _get_device_info(self, request: Request) -> Dict[str, Any]:
        """获取设备信息"""
        return {
            "user_agent": request.headers.get("User-Agent", ""),
            "ip_address": self._get_client_ip(request),
            "accept_language": request.headers.get("Accept-Language", ""),
            "platform": self._parse_platform(request.headers.get("User-Agent", ""))
        }
    
    def _parse_platform(self, user_agent: str) -> str:
        """解析平台信息"""
        user_agent_lower = user_agent.lower()
        
        if "mobile" in user_agent_lower or "android" in user_agent_lower:
            return "mobile"
        elif "iphone" in user_agent_lower or "ipad" in user_agent_lower:
            return "ios"
        elif "windows" in user_agent_lower:
            return "windows"
        elif "mac" in user_agent_lower:
            return "mac"
        elif "linux" in user_agent_lower:
            return "linux"
        else:
            return "unknown"


# 依赖注入函数
async def get_auth_handler(
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
    metrics_service: MetricsService = Depends(get_metrics_service)
) -> AuthHandler:
    """获取认证处理器实例"""
    return AuthHandler(auth_service, user_service, metrics_service)


# 路由端点定义
@router.post("/token", response_model=TokenResponse, summary="用户登录")
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    handler: AuthHandler = Depends(get_auth_handler)
):
    """用户登录获取访问令牌"""
    return await handler.login(request, form_data)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="用户注册")
async def register_user(
    request: Request,
    user_data: RegisterRequest,
    handler: AuthHandler = Depends(get_auth_handler)
):
    """用户注册"""
    return await handler.register(request, user_data)


@router.post("/refresh", response_model=TokenResponse, summary="刷新令牌")
async def refresh_access_token(
    request: Request,
    refresh_data: RefreshRequest,
    handler: AuthHandler = Depends(get_auth_handler)
):
    """使用刷新令牌获取新的访问令牌"""
    return await handler.refresh_token(request, refresh_data)


@router.post("/logout", summary="用户登出")
async def logout(
    request: Request,
    current_user: User = Depends(AuthService.get_current_user),
    handler: AuthHandler = Depends(get_auth_handler)
):
    """用户登出，使当前令牌失效"""
    return await handler.logout(request, current_user)


@router.post("/verify", summary="验证令牌")
async def verify_token(
    verify_data: VerifyTokenRequest,
    handler: AuthHandler = Depends(get_auth_handler)
):
    """验证访问令牌有效性"""
    return await handler.verify_token(verify_data)


@router.post("/reset-password-request", summary="请求密码重置")
async def request_password_reset(
    request: Request,
    email: str,
    handler: AuthHandler = Depends(get_auth_handler)
):
    """请求密码重置，发送重置邮件"""
    return await handler.request_password_reset(request, email)


@router.post("/reset-password", summary="重置密码")
async def reset_password(
    request: Request,
    reset_data: ResetPasswordRequest,
    handler: AuthHandler = Depends(get_auth_handler)
):
    """重置密码"""
    return await handler.reset_password(request, reset_data)


@router.post("/mfa/setup", response_model=MFASetupResponse, summary="设置多因素认证")
async def setup_mfa(
    mfa_type: str,
    current_user: User = Depends(AuthService.get_current_user),
    handler: AuthHandler = Depends(get_auth_handler)
):
    """设置多因素认证"""
    return await handler.setup_mfa(current_user, mfa_type)


@router.post("/mfa/verify", summary="验证多因素认证")
async def verify_mfa(
    verify_data: MFAVerifyRequest,
    mfa_type: Optional[str] = None,
    current_user: User = Depends(AuthService.get_current_user),
    handler: AuthHandler = Depends(get_auth_handler)
):
    """验证多因素认证代码"""
    return await handler.verify_mfa(current_user, verify_data, mfa_type)


@router.post("/mfa/disable", summary="禁用多因素认证")
async def disable_mfa(
    current_user: User = Depends(AuthService.get_current_user),
    handler: AuthHandler = Depends(get_auth_handler)
):
    """禁用多因素认证"""
    return await handler.disable_mfa(current_user)