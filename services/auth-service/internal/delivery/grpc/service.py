#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
gRPC服务实现模块

实现认证相关的gRPC服务接口。
"""
import uuid
import logging
from typing import Dict, Any, Optional
from datetime import timedelta

import grpc
from sqlalchemy.ext.asyncio import AsyncSession

from api.grpc import auth_pb2, auth_pb2_grpc
from internal.model.user import User, MFATypeEnum
from internal.model.errors import (
    AuthServiceError, UserExistsError, CredentialsError, 
    UserNotFoundError, InvalidTokenError, MFARequiredError,
    MFAInvalidCodeError, ValidationError, AuthenticationError
)
from internal.service.auth_service import (
    authenticate_user, create_tokens, refresh_tokens, 
    verify_token, logout, get_password_hash, setup_mfa,
    verify_mfa, reset_password, create_access_token
)
from internal.repository.user_repository import UserRepository
from internal.db.session import get_session


class AuthServicer(auth_pb2_grpc.AuthServiceServicer):
    """认证服务gRPC接口实现"""
    
    async def Register(self, request, context):
        """用户注册"""
        try:
            # 获取数据库会话
            async with get_session() as session:
                # 创建用户仓储
                user_repo = UserRepository(session)
                
                # 检查用户名是否存在
                existing_user = await user_repo.get_user_by_username(request.username)
                if existing_user:
                    raise UserExistsError(f"用户名 '{request.username}' 已被注册")
                
                # 检查邮箱是否存在
                existing_email = await user_repo.get_user_by_email(request.email)
                if existing_email:
                    raise UserExistsError(f"邮箱 '{request.email}' 已被注册")
                
                # 检查手机号是否存在(如果提供)
                if request.phone_number:
                    existing_phone = await user_repo.get_user_by_phone(request.phone_number)
                    if existing_phone:
                        raise UserExistsError(f"手机号 '{request.phone_number}' 已被注册")
                
                # 创建用户
                password_hash = await get_password_hash(request.password)
                
                # 处理个人资料数据
                profile_data = {}
                if request.profile_data:
                    profile_data = dict(request.profile_data)
                
                # 创建用户
                user_id = await user_repo.create_user(
                    username=request.username,
                    email=request.email,
                    password_hash=password_hash,
                    phone=request.phone_number,
                    profile_data=profile_data
                )
                
                # 创建响应
                return auth_pb2.RegisterResponse(
                    user_id=str(user_id),
                    username=request.username,
                    email=request.email,
                    success=True,
                    message="注册成功"
                )
                
        except AuthServiceError as e:
            # 处理已知错误
            context.set_code(e.error_code.grpc_code)
            context.set_details(e.message)
            return auth_pb2.RegisterResponse(
                success=False,
                message=e.message
            )
        except Exception as e:
            # 处理未知错误
            logging.error(f"Register错误: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"服务内部错误: {str(e)}")
            return auth_pb2.RegisterResponse(
                success=False,
                message="服务内部错误"
            )
    
    async def Login(self, request, context):
        """用户登录"""
        try:
            # 获取数据库会话
            async with get_session() as session:
                # 根据认证方法处理登录
                if request.auth_method == auth_pb2.PASSWORD:
                    # 确定登录标识符
                    if request.HasField("username"):
                        identifier = request.username
                        identifier_type = "username"
                    elif request.HasField("email"):
                        identifier = request.email
                        identifier_type = "email"
                    elif request.HasField("phone_number"):
                        identifier = request.phone_number
                        identifier_type = "phone"
                    else:
                        raise ValidationError("请提供用户名、邮箱或手机号")
                    
                    # 认证用户
                    user_repo = UserRepository(session)
                    user = None
                    
                    if identifier_type == "username":
                        user = await user_repo.get_user_by_username(identifier)
                    elif identifier_type == "email":
                        user = await user_repo.get_user_by_email(identifier)
                    elif identifier_type == "phone":
                        user = await user_repo.get_user_by_phone(identifier)
                    
                    if not user:
                        raise UserNotFoundError()
                    
                    # 验证密码
                    is_valid = await authenticate_user(
                        username=user.username, 
                        password=request.password,
                        session=session
                    )
                    
                    if not is_valid:
                        raise CredentialsError("密码错误")
                    
                    # 检查是否需要MFA
                    if user.mfa_enabled:
                        # 如果请求中包含MFA验证码，则验证
                        if request.mfa_code:
                            is_valid_mfa = await verify_mfa(user, request.mfa_code, session)
                            if not is_valid_mfa:
                                raise MFAInvalidCodeError()
                        else:
                            # 创建MFA令牌
                            mfa_token_data = {
                                "sub": str(user.id),
                                "type": "mfa_challenge"
                            }
                            mfa_token = await create_access_token(mfa_token_data, timedelta(minutes=5))
                            
                            # 返回需要MFA的响应
                            return auth_pb2.LoginResponse(
                                mfa_required=True,
                                mfa_token=mfa_token,
                                success=True,
                                message="需要多因素认证"
                            )
                    
                    # 生成令牌
                    tokens = await create_tokens(user, session)
                    
                    # 返回响应
                    return auth_pb2.LoginResponse(
                        access_token=tokens.access_token,
                        refresh_token=tokens.refresh_token,
                        token_type=tokens.token_type,
                        expires_in=tokens.expires_in,
                        mfa_required=False,
                        success=True,
                        message="登录成功"
                    )
                    
                elif request.auth_method == auth_pb2.SMS_CODE:
                    # 实现短信验证码登录
                    from internal.service.sms_service import SMSService
                    from internal.cache.redis_cache import RedisCache
                    
                    # 验证必要字段
                    if not request.phone_number or not request.verification_code:
                        raise ValidationError("手机号和验证码不能为空")
                    
                    # 验证验证码
                    cache = RedisCache()
                    cache_key = f"sms_code:{request.phone_number}"
                    stored_code = await cache.get(cache_key)
                    
                    if not stored_code or stored_code != request.verification_code:
                        raise AuthenticationError("验证码无效或已过期")
                    
                    # 查找用户
                    user_repo = UserRepository(session)
                    user = await user_repo.get_user_by_phone(request.phone_number)
                    
                    if not user:
                        raise UserNotFoundError("手机号未注册")
                    
                    # 删除已使用的验证码
                    await cache.delete(cache_key)
                    
                    # 创建令牌
                    tokens = await create_tokens(user, session)
                    
                    return auth_pb2.LoginResponse(
                        access_token=tokens.access_token,
                        refresh_token=tokens.refresh_token,
                        token_type=tokens.token_type,
                        expires_in=tokens.expires_in,
                        success=True,
                        message="短信验证码登录成功"
                    )
                    
                elif request.auth_method == auth_pb2.EMAIL_CODE:
                    # 实现邮箱验证码登录
                    from internal.service.email_service import EmailService
                    from internal.cache.redis_cache import RedisCache
                    
                    # 验证必要字段
                    if not request.email or not request.verification_code:
                        raise ValidationError("邮箱和验证码不能为空")
                    
                    # 验证验证码
                    cache = RedisCache()
                    cache_key = f"email_code:{request.email}"
                    stored_code = await cache.get(cache_key)
                    
                    if not stored_code or stored_code != request.verification_code:
                        raise AuthenticationError("验证码无效或已过期")
                    
                    # 查找用户
                    user_repo = UserRepository(session)
                    user = await user_repo.get_user_by_email(request.email)
                    
                    if not user:
                        raise UserNotFoundError("邮箱未注册")
                    
                    # 删除已使用的验证码
                    await cache.delete(cache_key)
                    
                    # 创建令牌
                    tokens = await create_tokens(user, session)
                    
                    return auth_pb2.LoginResponse(
                        access_token=tokens.access_token,
                        refresh_token=tokens.refresh_token,
                        token_type=tokens.token_type,
                        expires_in=tokens.expires_in,
                        success=True,
                        message="邮箱验证码登录成功"
                    )
                    
                elif request.auth_method == auth_pb2.OAUTH:
                    # 实现OAuth登录
                    from internal.service.oauth_service import authenticate_with_oauth, get_user_profile
                    
                    # 验证必要字段
                    if not request.oauth_provider or not request.oauth_access_token:
                        raise ValidationError("OAuth提供商和访问令牌不能为空")
                    
                    try:
                        # 获取用户资料
                        user_profile = await get_user_profile(
                            request.oauth_provider, 
                            request.oauth_access_token
                        )
                        
                        # 进行OAuth认证
                        user, tokens = await authenticate_with_oauth(
                            session,
                            request.oauth_provider,
                            request.oauth_access_token,
                            user_profile
                        )
                        
                        return auth_pb2.LoginResponse(
                            access_token=tokens["access_token"],
                            refresh_token=tokens["refresh_token"],
                            token_type=tokens["token_type"],
                            expires_in=tokens["expires_in"],
                            success=True,
                            message="OAuth登录成功"
                        )
                        
                    except Exception as e:
                        raise AuthenticationError(f"OAuth登录失败: {str(e)}")
                    
                else:
                    raise ValidationError("不支持的认证方法")
                    
        except AuthServiceError as e:
            # 处理已知错误
            context.set_code(e.error_code.grpc_code)
            context.set_details(e.message)
            return auth_pb2.LoginResponse(
                success=False,
                message=e.message
            )
        except Exception as e:
            # 处理未知错误
            logging.error(f"Login错误: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"服务内部错误: {str(e)}")
            return auth_pb2.LoginResponse(
                success=False,
                message="服务内部错误"
            )
    
    async def Logout(self, request, context):
        """用户登出"""
        try:
            # 获取数据库会话
            async with get_session() as session:
                # 验证访问令牌
                try:
                    token_data = await verify_token(request.access_token, session)
                    user_id = token_data.get("id")
                except InvalidTokenError:
                    # 即使令牌无效，也允许登出
                    pass
                
                # 吊销刷新令牌
                is_success = await logout(request.refresh_token, session)
                
                # 返回响应
                return auth_pb2.LogoutResponse(
                    success=True,
                    message="登出成功"
                )
                
        except AuthServiceError as e:
            # 处理已知错误
            context.set_code(e.error_code.grpc_code)
            context.set_details(e.message)
            return auth_pb2.LogoutResponse(
                success=False,
                message=e.message
            )
        except Exception as e:
            # 处理未知错误
            logging.error(f"Logout错误: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"服务内部错误: {str(e)}")
            return auth_pb2.LogoutResponse(
                success=False,
                message="服务内部错误"
            )
    
    async def RefreshToken(self, request, context):
        """刷新令牌"""
        try:
            # 获取数据库会话
            async with get_session() as session:
                # 刷新令牌
                tokens = await refresh_tokens(request.refresh_token, session)
                
                # 返回响应
                return auth_pb2.RefreshTokenResponse(
                    access_token=tokens.access_token,
                    refresh_token=tokens.refresh_token,
                    token_type=tokens.token_type,
                    expires_in=tokens.expires_in,
                    success=True,
                    message="令牌刷新成功"
                )
                
        except AuthServiceError as e:
            # 处理已知错误
            context.set_code(e.error_code.grpc_code)
            context.set_details(e.message)
            return auth_pb2.RefreshTokenResponse(
                success=False,
                message=e.message
            )
        except Exception as e:
            # 处理未知错误
            logging.error(f"RefreshToken错误: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"服务内部错误: {str(e)}")
            return auth_pb2.RefreshTokenResponse(
                success=False,
                message="服务内部错误"
            )
    
    async def VerifyToken(self, request, context):
        """验证令牌"""
        try:
            # 获取数据库会话
            async with get_session() as session:
                # 验证令牌
                token_data = await verify_token(request.token, session)
                
                # 返回响应
                return auth_pb2.VerifyTokenResponse(
                    valid=True,
                    user_id=token_data.get("id"),
                    permissions=token_data.get("permissions", []),
                    roles=token_data.get("roles", []),
                    message="令牌有效"
                )
                
        except AuthServiceError as e:
            # 处理已知错误
            context.set_code(e.error_code.grpc_code)
            context.set_details(e.message)
            return auth_pb2.VerifyTokenResponse(
                valid=False,
                message=e.message
            )
        except Exception as e:
            # 处理未知错误
            logging.error(f"VerifyToken错误: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"服务内部错误: {str(e)}")
            return auth_pb2.VerifyTokenResponse(
                valid=False,
                message="服务内部错误"
            )
    
    async def CheckPermission(self, request, context):
        """检查权限"""
        try:
            # 获取数据库会话
            async with get_session() as session:
                # 获取用户
                user_repo = UserRepository(session)
                user = await user_repo.get_user_by_id(request.user_id)
                
                if not user:
                    raise UserNotFoundError()
                
                # 检查权限
                permission_str = request.permission
                has_permission = False
                
                # 遍历用户角色和权限
                for role in user.roles:
                    for perm in role.permissions:
                        if f"{perm.resource}:{perm.action}" == permission_str:
                            has_permission = True
                            break
                    if has_permission:
                        break
                
                # 返回响应
                if has_permission:
                    return auth_pb2.CheckPermissionResponse(
                        has_permission=True,
                        message="用户具有所需权限"
                    )
                else:
                    return auth_pb2.CheckPermissionResponse(
                        has_permission=False,
                        message="用户没有所需权限"
                    )
                
        except AuthServiceError as e:
            # 处理已知错误
            context.set_code(e.error_code.grpc_code)
            context.set_details(e.message)
            return auth_pb2.CheckPermissionResponse(
                has_permission=False,
                message=e.message
            )
        except Exception as e:
            # 处理未知错误
            logging.error(f"CheckPermission错误: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"服务内部错误: {str(e)}")
            return auth_pb2.CheckPermissionResponse(
                has_permission=False,
                message="服务内部错误"
            )
    
    async def GetUserRoles(self, request, context):
        """获取用户角色"""
        try:
            # 获取数据库会话
            async with get_session() as session:
                # 获取用户
                user_repo = UserRepository(session)
                user = await user_repo.get_user_by_id(request.user_id)
                
                if not user:
                    raise UserNotFoundError()
                
                # 提取角色信息
                roles = []
                for role in user.roles:
                    permissions = []
                    for perm in role.permissions:
                        permissions.append(f"{perm.resource}:{perm.action}")
                    
                    roles.append(auth_pb2.Role(
                        id=str(role.id),
                        name=role.name,
                        description=role.description or "",
                        permissions=permissions
                    ))
                
                # 返回响应
                return auth_pb2.GetUserRolesResponse(
                    roles=roles,
                    success=True,
                    message="获取角色成功"
                )
                
        except AuthServiceError as e:
            # 处理已知错误
            context.set_code(e.error_code.grpc_code)
            context.set_details(e.message)
            return auth_pb2.GetUserRolesResponse(
                success=False,
                message=e.message
            )
        except Exception as e:
            # 处理未知错误
            logging.error(f"GetUserRoles错误: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"服务内部错误: {str(e)}")
            return auth_pb2.GetUserRolesResponse(
                success=False,
                message="服务内部错误"
            )
    
    async def EnableMFA(self, request, context):
        """启用多因素认证"""
        try:
            # 获取数据库会话
            async with get_session() as session:
                # 获取用户
                user_repo = UserRepository(session)
                user = await user_repo.get_user_by_id(request.user_id)
                
                if not user:
                    raise UserNotFoundError()
                
                # 转换MFA类型
                mfa_type_map = {
                    auth_pb2.TOTP: MFATypeEnum.TOTP,
                    auth_pb2.SMS: MFATypeEnum.SMS,
                    auth_pb2.EMAIL: MFATypeEnum.EMAIL
                }
                
                mfa_type = mfa_type_map.get(request.mfa_type)
                if not mfa_type:
                    raise ValidationError("不支持的多因素认证类型")
                
                # 设置MFA
                mfa_setup = await setup_mfa(user, mfa_type.value, session)
                
                # 返回响应
                if mfa_type == MFATypeEnum.TOTP:
                    return auth_pb2.EnableMFAResponse(
                        success=True,
                        secret_key=mfa_setup.secret,
                        qr_code_url=mfa_setup.qr_code,
                        message="多因素认证已启用"
                    )
                else:
                    return auth_pb2.EnableMFAResponse(
                        success=True,
                        message=mfa_setup.message
                    )
                
        except AuthServiceError as e:
            # 处理已知错误
            context.set_code(e.error_code.grpc_code)
            context.set_details(e.message)
            return auth_pb2.EnableMFAResponse(
                success=False,
                message=e.message
            )
        except Exception as e:
            # 处理未知错误
            logging.error(f"EnableMFA错误: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"服务内部错误: {str(e)}")
            return auth_pb2.EnableMFAResponse(
                success=False,
                message="服务内部错误"
            )
    
    async def VerifyMFA(self, request, context):
        """验证多因素认证"""
        try:
            # 获取数据库会话
            async with get_session() as session:
                # 获取用户
                user_repo = UserRepository(session)
                user = await user_repo.get_user_by_id(request.user_id)
                
                if not user:
                    raise UserNotFoundError()
                
                # 验证MFA
                is_valid = await verify_mfa(user, request.mfa_code, session)
                
                if not is_valid:
                    raise MFAInvalidCodeError()
                
                # 如果存在MFA令牌，则验证并返回完整令牌
                if request.mfa_token:
                    try:
                        # 验证MFA令牌
                        token_data = await verify_token(request.mfa_token, session)
                        
                        # 检查令牌类型
                        if token_data.get("type") != "mfa_challenge":
                            raise InvalidTokenError("无效的MFA令牌")
                        
                        # 确认是同一用户
                        if token_data.get("sub") != str(user.id):
                            raise InvalidTokenError("MFA令牌用户不匹配")
                        
                        # 创建完整访问令牌
                        tokens = await create_tokens(user, session)
                        
                        # 返回带有访问令牌的响应
                        return auth_pb2.VerifyMFAResponse(
                            success=True,
                            access_token=tokens.access_token,
                            refresh_token=tokens.refresh_token,
                            token_type=tokens.token_type,
                            expires_in=tokens.expires_in,
                            message="多因素认证验证成功"
                        )
                    except InvalidTokenError:
                        # MFA令牌验证失败，但MFA验证本身是成功的
                        return auth_pb2.VerifyMFAResponse(
                            success=True,
                            message="多因素认证验证成功，但MFA令牌无效"
                        )
                
                # 简单的验证情况
                return auth_pb2.VerifyMFAResponse(
                    success=True,
                    message="多因素认证验证成功"
                )
                
        except AuthServiceError as e:
            # 处理已知错误
            context.set_code(e.error_code.grpc_code)
            context.set_details(e.message)
            return auth_pb2.VerifyMFAResponse(
                success=False,
                message=e.message
            )
        except Exception as e:
            # 处理未知错误
            logging.error(f"VerifyMFA错误: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"服务内部错误: {str(e)}")
            return auth_pb2.VerifyMFAResponse(
                success=False,
                message="服务内部错误"
            )
    
    async def ResetPassword(self, request, context):
        """重置密码"""
        try:
            # 获取数据库会话
            async with get_session() as session:
                # 获取用户
                user_repo = UserRepository(session)
                user = None
                
                # 根据标识符获取用户
                if request.HasField("email"):
                    user = await user_repo.get_user_by_email(request.email)
                elif request.HasField("phone_number"):
                    user = await user_repo.get_user_by_phone(request.phone_number)
                else:
                    raise ValidationError("必须提供邮箱或手机号")
                
                if not user:
                    raise UserNotFoundError()
                
                # 验证验证码
                from internal.cache.redis_cache import RedisCache
                
                # 验证重置验证码
                if hasattr(request, 'verification_code') and request.verification_code:
                    cache = RedisCache()
                    identifier = request.email if request.HasField("email") else request.phone_number
                    cache_key = f"reset_code:{identifier}"
                    stored_code = await cache.get(cache_key)
                    
                    if not stored_code or stored_code != request.verification_code:
                        raise ValidationError("验证码无效或已过期")
                    
                    # 删除已使用的验证码
                    await cache.delete(cache_key)
                else:
                    raise ValidationError("密码重置需要验证码")
                
                # 设置新密码
                password_hash = await get_password_hash(request.new_password)
                await user_repo.update_password(str(user.id), password_hash)
                
                # 返回响应
                return auth_pb2.ResetPasswordResponse(
                    success=True,
                    message="密码重置成功"
                )
                
        except AuthServiceError as e:
            # 处理已知错误
            context.set_code(e.error_code.grpc_code)
            context.set_details(e.message)
            return auth_pb2.ResetPasswordResponse(
                success=False,
                message=e.message
            )
        except Exception as e:
            # 处理未知错误
            logging.error(f"ResetPassword错误: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"服务内部错误: {str(e)}")
            return auth_pb2.ResetPasswordResponse(
                success=False,
                message="服务内部错误"
            )