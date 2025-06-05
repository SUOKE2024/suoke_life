"""
平台管理相关的API路由
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.security import verify_token, TokenData
from ...models.platform import Platform, PlatformConfig
from ...services.platform_service import PlatformService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/platforms", tags=["平台管理"])


class PlatformResponse(BaseModel):
    """平台响应模型"""
    id: str
    name: str
    display_name: str
    description: Optional[str]
    is_enabled: bool
    api_base_url: Optional[str]
    auth_type: str
    created_at: str
    updated_at: str


class PlatformCreateRequest(BaseModel):
    """平台创建请求模型"""
    name: str
    display_name: str
    description: Optional[str] = None
    api_base_url: Optional[str] = None
    auth_type: str = "oauth2"


class PlatformUpdateRequest(BaseModel):
    """平台更新请求模型"""
    display_name: Optional[str] = None
    description: Optional[str] = None
    is_enabled: Optional[bool] = None
    api_base_url: Optional[str] = None
    auth_type: Optional[str] = None


class PlatformConfigResponse(BaseModel):
    """平台配置响应模型"""
    id: int
    platform_id: str
    config_key: str
    config_value: Optional[str]
    is_encrypted: bool
    description: Optional[str]


class PlatformConfigRequest(BaseModel):
    """平台配置请求模型"""
    config_key: str
    config_value: str
    is_encrypted: bool = False
    description: Optional[str] = None


@router.get("/", response_model=List[PlatformResponse], summary="获取平台列表")
async def get_platforms(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    enabled_only: bool = Query(False, description="仅返回启用的平台"),
    current_user: TokenData = Depends(verify_token),
    db: Session = Depends(get_db)
) -> List[PlatformResponse]:
    """
    获取平台列表
    
    - **skip**: 跳过的记录数
    - **limit**: 返回的记录数
    - **enabled_only**: 仅返回启用的平台
    """
    try:
        platform_service = PlatformService(db)
        platforms = platform_service.get_platforms(
            skip=skip, 
            limit=limit, 
            enabled_only=enabled_only
        )
        
        return [
            PlatformResponse(
                id=platform.id,
                name=platform.name,
                display_name=platform.display_name,
                description=platform.description,
                is_enabled=platform.is_enabled,
                api_base_url=platform.api_base_url,
                auth_type=platform.auth_type,
                created_at=platform.created_at.isoformat(),
                updated_at=platform.updated_at.isoformat()
            )
            for platform in platforms
        ]
        
    except Exception as e:
        logger.error(f"获取平台列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取平台列表过程中发生错误"
        )


@router.get("/{platform_id}", response_model=PlatformResponse, summary="获取平台详情")
async def get_platform(
    platform_id: str,
    current_user: TokenData = Depends(verify_token),
    db: Session = Depends(get_db)
) -> PlatformResponse:
    """
    获取指定平台的详细信息
    
    - **platform_id**: 平台ID
    """
    try:
        platform_service = PlatformService(db)
        platform = platform_service.get_platform_by_id(platform_id)
        
        if not platform:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="平台不存在"
            )
        
        return PlatformResponse(
            id=platform.id,
            name=platform.name,
            display_name=platform.display_name,
            description=platform.description,
            is_enabled=platform.is_enabled,
            api_base_url=platform.api_base_url,
            auth_type=platform.auth_type,
            created_at=platform.created_at.isoformat(),
            updated_at=platform.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取平台详情失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取平台详情过程中发生错误"
        )


@router.post("/", response_model=PlatformResponse, summary="创建平台")
async def create_platform(
    platform_data: PlatformCreateRequest,
    current_user: TokenData = Depends(verify_token),
    db: Session = Depends(get_db)
) -> PlatformResponse:
    """
    创建新平台
    
    - **name**: 平台名称（唯一标识）
    - **display_name**: 显示名称
    - **description**: 平台描述
    - **api_base_url**: API基础URL
    - **auth_type**: 认证类型
    """
    try:
        platform_service = PlatformService(db)
        
        # 检查平台名称是否已存在
        existing_platform = platform_service.get_platform_by_name(platform_data.name)
        if existing_platform:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="平台名称已存在"
            )
        
        platform = platform_service.create_platform(
            name=platform_data.name,
            display_name=platform_data.display_name,
            description=platform_data.description,
            api_base_url=platform_data.api_base_url,
            auth_type=platform_data.auth_type
        )
        
        logger.info(f"用户 {current_user.username} 创建平台 {platform.name}")
        
        return PlatformResponse(
            id=platform.id,
            name=platform.name,
            display_name=platform.display_name,
            description=platform.description,
            is_enabled=platform.is_enabled,
            api_base_url=platform.api_base_url,
            auth_type=platform.auth_type,
            created_at=platform.created_at.isoformat(),
            updated_at=platform.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建平台失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建平台过程中发生错误"
        )


@router.put("/{platform_id}", response_model=PlatformResponse, summary="更新平台")
async def update_platform(
    platform_id: str,
    platform_data: PlatformUpdateRequest,
    current_user: TokenData = Depends(verify_token),
    db: Session = Depends(get_db)
) -> PlatformResponse:
    """
    更新平台信息
    
    - **platform_id**: 平台ID
    """
    try:
        platform_service = PlatformService(db)
        
        platform = platform_service.get_platform_by_id(platform_id)
        if not platform:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="平台不存在"
            )
        
        # 更新平台信息
        update_data = platform_data.dict(exclude_unset=True)
        updated_platform = platform_service.update_platform(platform_id, update_data)
        
        logger.info(f"用户 {current_user.username} 更新平台 {platform.name}")
        
        return PlatformResponse(
            id=updated_platform.id,
            name=updated_platform.name,
            display_name=updated_platform.display_name,
            description=updated_platform.description,
            is_enabled=updated_platform.is_enabled,
            api_base_url=updated_platform.api_base_url,
            auth_type=updated_platform.auth_type,
            created_at=updated_platform.created_at.isoformat(),
            updated_at=updated_platform.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新平台失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新平台过程中发生错误"
        )


@router.delete("/{platform_id}", summary="删除平台")
async def delete_platform(
    platform_id: str,
    current_user: TokenData = Depends(verify_token),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    删除平台
    
    - **platform_id**: 平台ID
    """
    try:
        platform_service = PlatformService(db)
        
        platform = platform_service.get_platform_by_id(platform_id)
        if not platform:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="平台不存在"
            )
        
        platform_service.delete_platform(platform_id)
        
        logger.info(f"用户 {current_user.username} 删除平台 {platform.name}")
        
        return {"message": "平台删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除平台失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除平台过程中发生错误"
        )


@router.get("/{platform_id}/configs", response_model=List[PlatformConfigResponse], summary="获取平台配置")
async def get_platform_configs(
    platform_id: str,
    current_user: TokenData = Depends(verify_token),
    db: Session = Depends(get_db)
) -> List[PlatformConfigResponse]:
    """
    获取平台配置列表
    
    - **platform_id**: 平台ID
    """
    try:
        platform_service = PlatformService(db)
        
        # 验证平台是否存在
        platform = platform_service.get_platform_by_id(platform_id)
        if not platform:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="平台不存在"
            )
        
        configs = platform_service.get_platform_configs(platform_id)
        
        return [
            PlatformConfigResponse(
                id=config.id,
                platform_id=config.platform_id,
                config_key=config.config_key,
                config_value=config.config_value if not config.is_encrypted else "***",
                is_encrypted=config.is_encrypted,
                description=config.description
            )
            for config in configs
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取平台配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取平台配置过程中发生错误"
        )


@router.post("/{platform_id}/configs", response_model=PlatformConfigResponse, summary="创建平台配置")
async def create_platform_config(
    platform_id: str,
    config_data: PlatformConfigRequest,
    current_user: TokenData = Depends(verify_token),
    db: Session = Depends(get_db)
) -> PlatformConfigResponse:
    """
    创建平台配置
    
    - **platform_id**: 平台ID
    - **config_key**: 配置键
    - **config_value**: 配置值
    - **is_encrypted**: 是否加密
    - **description**: 配置描述
    """
    try:
        platform_service = PlatformService(db)
        
        # 验证平台是否存在
        platform = platform_service.get_platform_by_id(platform_id)
        if not platform:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="平台不存在"
            )
        
        config = platform_service.create_platform_config(
            platform_id=platform_id,
            config_key=config_data.config_key,
            config_value=config_data.config_value,
            is_encrypted=config_data.is_encrypted,
            description=config_data.description
        )
        
        logger.info(f"用户 {current_user.username} 为平台 {platform_id} 创建配置 {config_data.config_key}")
        
        return PlatformConfigResponse(
            id=config.id,
            platform_id=config.platform_id,
            config_key=config.config_key,
            config_value=config.config_value if not config.is_encrypted else "***",
            is_encrypted=config.is_encrypted,
            description=config.description
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建平台配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建平台配置过程中发生错误"
        )


@router.put("/{platform_id}/configs/{config_id}", response_model=PlatformConfigResponse, summary="更新平台配置")
async def update_platform_config(
    platform_id: str,
    config_id: int,
    config_data: PlatformConfigRequest,
    current_user: TokenData = Depends(verify_token),
    db: Session = Depends(get_db)
) -> PlatformConfigResponse:
    """
    更新平台配置
    
    - **platform_id**: 平台ID
    - **config_id**: 配置ID
    """
    try:
        platform_service = PlatformService(db)
        
        config = platform_service.update_platform_config(
            config_id=config_id,
            config_value=config_data.config_value,
            is_encrypted=config_data.is_encrypted,
            description=config_data.description
        )
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="配置不存在"
            )
        
        logger.info(f"用户 {current_user.username} 更新平台配置 {config_id}")
        
        return PlatformConfigResponse(
            id=config.id,
            platform_id=config.platform_id,
            config_key=config.config_key,
            config_value=config.config_value if not config.is_encrypted else "***",
            is_encrypted=config.is_encrypted,
            description=config.description
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新平台配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新平台配置过程中发生错误"
        )


@router.delete("/{platform_id}/configs/{config_id}", summary="删除平台配置")
async def delete_platform_config(
    platform_id: str,
    config_id: int,
    current_user: TokenData = Depends(verify_token),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    删除平台配置
    
    - **platform_id**: 平台ID
    - **config_id**: 配置ID
    """
    try:
        platform_service = PlatformService(db)
        
        success = platform_service.delete_platform_config(config_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="配置不存在"
            )
        
        logger.info(f"用户 {current_user.username} 删除平台配置 {config_id}")
        
        return {"message": "配置删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除平台配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除平台配置过程中发生错误"
        )