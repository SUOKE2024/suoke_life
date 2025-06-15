"""
生物识别认证API处理器
处理生物识别认证相关的HTTP请求
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from internal.dependencies import get_current_user, get_biometric_auth_service
from ...service.biometric_auth_service import BiometricAuthService
from ...model.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/biometric", tags=["生物识别认证"])


class BiometricRegistrationRequest(BaseModel):
    """生物识别注册请求"""
    authenticator_type: str = Field(default="platform", description="认证器类型")
    user_verification: str = Field(default="preferred", description="用户验证要求")


class BiometricRegistrationResponse(BaseModel):
    """生物识别注册响应"""
    challenge_id: str = Field(..., description="挑战ID")
    options: Dict[str, Any] = Field(..., description="注册选项")


class BiometricRegistrationCompleteRequest(BaseModel):
    """生物识别注册完成请求"""
    challenge_id: str = Field(..., description="挑战ID")
    credential_response: Dict[str, Any] = Field(..., description="凭证响应")


class BiometricRegistrationCompleteResponse(BaseModel):
    """生物识别注册完成响应"""
    success: bool = Field(..., description="是否成功")
    credential_id: str = Field(..., description="凭证ID")
    device_type: str = Field(..., description="设备类型")


class BiometricAuthenticationRequest(BaseModel):
    """生物识别认证请求"""
    user_verification: str = Field(default="preferred", description="用户验证要求")


class BiometricAuthenticationResponse(BaseModel):
    """生物识别认证响应"""
    challenge_id: str = Field(..., description="挑战ID")
    options: Dict[str, Any] = Field(..., description="认证选项")


class BiometricAuthenticationCompleteRequest(BaseModel):
    """生物识别认证完成请求"""
    challenge_id: str = Field(..., description="挑战ID")
    credential_response: Dict[str, Any] = Field(..., description="凭证响应")


class BiometricAuthenticationCompleteResponse(BaseModel):
    """生物识别认证完成响应"""
    success: bool = Field(..., description="是否成功")
    user_id: str = Field(..., description="用户ID")
    credential_id: str = Field(..., description="凭证ID")
    device_type: str = Field(..., description="设备类型")


class BiometricCredentialResponse(BaseModel):
    """生物识别凭证响应"""
    credential_id: str = Field(..., description="凭证ID")
    device_type: str = Field(..., description="设备类型")
    created_at: str = Field(..., description="创建时间")
    last_used: Optional[str] = Field(None, description="最后使用时间")


@router.post("/register/start", response_model=BiometricRegistrationResponse)
async def start_biometric_registration(
    request: BiometricRegistrationRequest,
    current_user: User = Depends(get_current_user),
    biometric_service: BiometricAuthService = Depends(get_biometric_auth_service)
):
    """开始生物识别注册"""
    try:
        result = await biometric_service.start_registration(
            user_id=str(current_user.id),
            authenticator_type=request.authenticator_type,
            user_verification=request.user_verification
        )
        
        return BiometricRegistrationResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"开始生物识别注册失败: user_id={current_user.id}, error={str(e)}")
        raise HTTPException(status_code=500, detail="注册启动失败")


@router.post("/register/complete", response_model=BiometricRegistrationCompleteResponse)
async def complete_biometric_registration(
    request: BiometricRegistrationCompleteRequest,
    http_request: Request,
    current_user: User = Depends(get_current_user),
    biometric_service: BiometricAuthService = Depends(get_biometric_auth_service)
):
    """完成生物识别注册"""
    try:
        # 获取客户端信息
        client_ip = http_request.client.host if http_request.client else None
        user_agent = http_request.headers.get("User-Agent")
        
        result = await biometric_service.complete_registration(
            challenge_id=request.challenge_id,
            credential_response=request.credential_response,
            user_ip=client_ip,
            user_agent=user_agent
        )
        
        return BiometricRegistrationCompleteResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"完成生物识别注册失败: user_id={current_user.id}, error={str(e)}")
        raise HTTPException(status_code=500, detail="注册完成失败")


@router.post("/auth/start", response_model=BiometricAuthenticationResponse)
async def start_biometric_authentication(
    request: BiometricAuthenticationRequest,
    current_user: Optional[User] = Depends(get_current_user),
    biometric_service: BiometricAuthService = Depends(get_biometric_auth_service)
):
    """开始生物识别认证"""
    try:
        user_id = str(current_user.id) if current_user else None
        
        result = await biometric_service.start_authentication(
            user_id=user_id,
            user_verification=request.user_verification
        )
        
        return BiometricAuthenticationResponse(**result)
        
    except Exception as e:
        logger.error(f"开始生物识别认证失败: user_id={user_id}, error={str(e)}")
        raise HTTPException(status_code=500, detail="认证启动失败")


@router.post("/auth/complete", response_model=BiometricAuthenticationCompleteResponse)
async def complete_biometric_authentication(
    request: BiometricAuthenticationCompleteRequest,
    http_request: Request,
    biometric_service: BiometricAuthService = Depends(get_biometric_auth_service)
):
    """完成生物识别认证"""
    try:
        # 获取客户端信息
        client_ip = http_request.client.host if http_request.client else None
        user_agent = http_request.headers.get("User-Agent")
        
        result = await biometric_service.complete_authentication(
            challenge_id=request.challenge_id,
            credential_response=request.credential_response,
            user_ip=client_ip,
            user_agent=user_agent
        )
        
        return BiometricAuthenticationCompleteResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"完成生物识别认证失败: error={str(e)}")
        raise HTTPException(status_code=500, detail="认证完成失败")


@router.get("/credentials", response_model=List[BiometricCredentialResponse])
async def get_user_biometric_credentials(
    current_user: User = Depends(get_current_user),
    biometric_service: BiometricAuthService = Depends(get_biometric_auth_service)
):
    """获取用户的生物识别凭证"""
    try:
        credentials = await biometric_service.get_user_credentials(str(current_user.id))
        
        return [BiometricCredentialResponse(**cred) for cred in credentials]
        
    except Exception as e:
        logger.error(f"获取生物识别凭证失败: user_id={current_user.id}, error={str(e)}")
        raise HTTPException(status_code=500, detail="获取凭证失败")


@router.delete("/credentials/{credential_id}")
async def revoke_biometric_credential(
    credential_id: str,
    http_request: Request,
    current_user: User = Depends(get_current_user),
    biometric_service: BiometricAuthService = Depends(get_biometric_auth_service)
):
    """撤销生物识别凭证"""
    try:
        # 获取客户端IP
        client_ip = http_request.client.host if http_request.client else None
        
        success = await biometric_service.revoke_credential(
            user_id=str(current_user.id),
            credential_id=credential_id,
            user_ip=client_ip
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="凭证不存在")
        
        return {
            "success": True,
            "message": "凭证已成功撤销"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"撤销生物识别凭证失败: user_id={current_user.id}, credential_id={credential_id}, error={str(e)}")
        raise HTTPException(status_code=500, detail="撤销凭证失败")


@router.get("/support")
async def check_biometric_support():
    """检查生物识别支持"""
    return {
        "webauthn_supported": True,
        "platform_authenticator": True,
        "cross_platform_authenticator": True,
        "supported_algorithms": [
            {"name": "ES256", "id": -7},
            {"name": "ES384", "id": -35},
            {"name": "ES512", "id": -36},
            {"name": "RS256", "id": -257},
            {"name": "RS384", "id": -258},
            {"name": "RS512", "id": -259}
        ],
        "supported_authenticator_types": [
            "platform",
            "cross-platform"
        ],
        "user_verification_methods": [
            "required",
            "preferred",
            "discouraged"
        ]
    }


@router.post("/cleanup")
async def cleanup_expired_challenges(
    biometric_service: BiometricAuthService = Depends(get_biometric_auth_service)
):
    """清理过期的挑战（管理员功能）"""
    try:
        await biometric_service.cleanup_expired_challenges()
        
        return {
            "success": True,
            "message": "已清理过期挑战"
        }
        
    except Exception as e:
        logger.error(f"清理过期挑战失败: error={str(e)}")
        raise HTTPException(status_code=500, detail="清理失败") 