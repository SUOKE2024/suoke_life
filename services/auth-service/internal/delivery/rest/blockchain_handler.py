#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
区块链认证API处理器

提供Web3钱包登录的REST API端点。
"""
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ...service.blockchain_auth_service import BlockchainAuthService, get_blockchain_auth_service
from ...security.jwt_manager import get_current_user
from ...model.user import User
from ...exceptions import (
    AuthenticationError,
    ValidationError,
    BlockchainError
)

router = APIRouter(prefix="/api/v1/auth/blockchain", tags=["区块链认证"])


# 请求/响应模型
class NonceRequest(BaseModel):
    """获取Nonce请求"""
    wallet_address: str = Field(..., description="钱包地址")


class NonceResponse(BaseModel):
    """Nonce响应"""
    wallet_address: str = Field(..., description="钱包地址")
    nonce: str = Field(..., description="随机数")
    message: str = Field(..., description="签名消息")
    timestamp: int = Field(..., description="时间戳")
    expires_at: str = Field(..., description="过期时间")


class WalletLoginRequest(BaseModel):
    """钱包登录请求"""
    wallet_address: str = Field(..., description="钱包地址")
    signature: str = Field(..., description="签名")
    network: str = Field("ethereum", description="区块链网络")


class WalletLoginResponse(BaseModel):
    """钱包登录响应"""
    user: Dict[str, Any] = Field(..., description="用户信息")
    tokens: Dict[str, str] = Field(..., description="JWT令牌")
    wallet_info: Dict[str, Any] = Field(..., description="钱包信息")
    network: str = Field(..., description="区块链网络")


class LinkWalletRequest(BaseModel):
    """绑定钱包请求"""
    wallet_address: str = Field(..., description="钱包地址")
    signature: str = Field(..., description="签名")
    network: str = Field("ethereum", description="区块链网络")


class NetworkResponse(BaseModel):
    """网络信息响应"""
    id: str = Field(..., description="网络ID")
    name: str = Field(..., description="网络名称")
    chain_id: int = Field(..., description="链ID")
    explorer: str = Field(..., description="区块链浏览器")


@router.post("/nonce", response_model=NonceResponse)
async def get_wallet_nonce(
    request: NonceRequest,
    blockchain_service: BlockchainAuthService = Depends(get_blockchain_auth_service)
):
    """
    获取钱包登录随机数
    
    用于生成钱包签名消息，防止重放攻击。
    """
    try:
        result = await blockchain_service.generate_nonce(request.wallet_address)
        return NonceResponse(**result)
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成Nonce失败: {str(e)}"
        )


@router.post("/login", response_model=WalletLoginResponse)
async def wallet_login(
    request: WalletLoginRequest,
    blockchain_service: BlockchainAuthService = Depends(get_blockchain_auth_service)
):
    """
    钱包签名登录
    
    验证钱包签名并完成登录流程。
    """
    try:
        result = await blockchain_service.verify_wallet_signature(
            wallet_address=request.wallet_address,
            signature=request.signature,
            network=request.network
        )
        
        return WalletLoginResponse(**result)
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"钱包登录失败: {str(e)}"
        )


@router.post("/link")
async def link_wallet(
    request: LinkWalletRequest,
    current_user: User = Depends(get_current_user),
    blockchain_service: BlockchainAuthService = Depends(get_blockchain_auth_service)
):
    """
    绑定钱包到当前用户
    
    将Web3钱包绑定到已登录的用户账号。
    """
    try:
        success = await blockchain_service.link_wallet_to_user(
            user_id=current_user.id,
            wallet_address=request.wallet_address,
            signature=request.signature,
            network=request.network
        )
        
        return {
            "success": success,
            "message": f"钱包 {request.wallet_address} 已成功绑定到您的账号"
        }
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"绑定钱包失败: {str(e)}"
        )


@router.delete("/unlink")
async def unlink_wallet(
    current_user: User = Depends(get_current_user),
    blockchain_service: BlockchainAuthService = Depends(get_blockchain_auth_service)
):
    """
    解除钱包绑定
    
    从当前用户账号解除钱包绑定。
    """
    try:
        success = await blockchain_service.unlink_wallet_from_user(current_user.id)
        
        return {
            "success": success,
            "message": "钱包绑定已成功解除"
        }
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"解除钱包绑定失败: {str(e)}"
        )


@router.get("/networks", response_model=List[NetworkResponse])
async def get_supported_networks(
    blockchain_service: BlockchainAuthService = Depends(get_blockchain_auth_service)
):
    """
    获取支持的区块链网络
    
    返回平台支持的所有区块链网络列表。
    """
    try:
        networks = await blockchain_service.get_supported_networks()
        return [NetworkResponse(**network) for network in networks]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取网络列表失败: {str(e)}"
        )


@router.get("/wallet-info/{wallet_address}")
async def get_wallet_info(
    wallet_address: str,
    network: str = "ethereum",
    blockchain_service: BlockchainAuthService = Depends(get_blockchain_auth_service)
):
    """
    获取钱包信息
    
    查询指定钱包地址的链上信息。
    """
    try:
        wallet_info = await blockchain_service._get_wallet_info(wallet_address, network)
        
        return {
            "wallet_address": wallet_address,
            "network": network,
            "info": wallet_info
        }
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取钱包信息失败: {str(e)}"
        ) 