"""
Integration Management API Routes
"""

from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from fastapi.responses import RedirectResponse

from ...model.user_integration import (
    UserIntegration, 
    IntegrationRequest, 
    IntegrationResponse,
    AuthCallbackRequest,
    PlatformType,
    IntegrationStatus
)
from ...model.base import BaseResponse, PaginationParams, PaginationResponse
from ...service.integration_service import IntegrationService
from ...service.dependencies import get_integration_service, get_current_user

router = APIRouter()


@router.get("/", response_model=List[UserIntegration])
async def list_user_integrations(
    user_id: str = Depends(get_current_user),
    platform: Optional[PlatformType] = Query(None, description="平台类型筛选"),
    status: Optional[IntegrationStatus] = Query(None, description="状态筛选"),
    pagination: PaginationParams = Depends(),
    service: IntegrationService = Depends(get_integration_service)
):
    """获取用户的集成配置列表"""
    try:
        integrations = await service.get_user_integrations(
            user_id=user_id,
            platform=platform,
            status=status,
            offset=pagination.offset,
            limit=pagination.size
        )
        return integrations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取集成列表失败: {str(e)}")


@router.post("/", response_model=IntegrationResponse)
async def create_integration(
    request: IntegrationRequest,
    user_id: str = Depends(get_current_user),
    service: IntegrationService = Depends(get_integration_service)
):
    """创建新的平台集成"""
    try:
        result = await service.create_integration(
            user_id=user_id,
            platform=request.platform,
            permissions=request.permissions,
            sync_frequency=request.sync_frequency,
            platform_config=request.platform_config
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建集成失败: {str(e)}")


@router.get("/{integration_id}", response_model=UserIntegration)
async def get_integration(
    integration_id: int = Path(..., description="集成ID"),
    user_id: str = Depends(get_current_user),
    service: IntegrationService = Depends(get_integration_service)
):
    """获取指定集成的详细信息"""
    try:
        integration = await service.get_integration_by_id(integration_id, user_id)
        if not integration:
            raise HTTPException(status_code=404, detail="集成配置不存在")
        return integration
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取集成信息失败: {str(e)}")


@router.put("/{integration_id}", response_model=UserIntegration)
async def update_integration(
    request: IntegrationRequest,
    integration_id: int = Path(..., description="集成ID"),
    user_id: str = Depends(get_current_user),
    service: IntegrationService = Depends(get_integration_service)
):
    """更新集成配置"""
    try:
        integration = await service.update_integration(
            integration_id=integration_id,
            user_id=user_id,
            permissions=request.permissions,
            sync_frequency=request.sync_frequency,
            platform_config=request.platform_config
        )
        if not integration:
            raise HTTPException(status_code=404, detail="集成配置不存在")
        return integration
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新集成配置失败: {str(e)}")


@router.delete("/{integration_id}", response_model=BaseResponse)
async def delete_integration(
    integration_id: int = Path(..., description="集成ID"),
    user_id: str = Depends(get_current_user),
    service: IntegrationService = Depends(get_integration_service)
):
    """删除集成配置"""
    try:
        success = await service.delete_integration(integration_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="集成配置不存在")
        return BaseResponse(message="集成配置已删除")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除集成配置失败: {str(e)}")


@router.post("/{integration_id}/enable", response_model=BaseResponse)
async def enable_integration(
    integration_id: int = Path(..., description="集成ID"),
    user_id: str = Depends(get_current_user),
    service: IntegrationService = Depends(get_integration_service)
):
    """启用集成"""
    try:
        success = await service.toggle_integration(integration_id, user_id, True)
        if not success:
            raise HTTPException(status_code=404, detail="集成配置不存在")
        return BaseResponse(message="集成已启用")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启用集成失败: {str(e)}")


@router.post("/{integration_id}/disable", response_model=BaseResponse)
async def disable_integration(
    integration_id: int = Path(..., description="集成ID"),
    user_id: str = Depends(get_current_user),
    service: IntegrationService = Depends(get_integration_service)
):
    """禁用集成"""
    try:
        success = await service.toggle_integration(integration_id, user_id, False)
        if not success:
            raise HTTPException(status_code=404, detail="集成配置不存在")
        return BaseResponse(message="集成已禁用")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"禁用集成失败: {str(e)}")


@router.post("/{integration_id}/sync", response_model=BaseResponse)
async def trigger_sync(
    integration_id: int = Path(..., description="集成ID"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    data_types: Optional[List[str]] = Query(None, description="数据类型"),
    user_id: str = Depends(get_current_user),
    service: IntegrationService = Depends(get_integration_service)
):
    """手动触发数据同步"""
    try:
        result = await service.trigger_sync(
            integration_id=integration_id,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            data_types=data_types
        )
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.error_message)
        
        return BaseResponse(
            message=f"同步完成，共同步 {result.synced_count} 条数据"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"触发同步失败: {str(e)}")


@router.get("/{integration_id}/status", response_model=dict)
async def get_sync_status(
    integration_id: int = Path(..., description="集成ID"),
    user_id: str = Depends(get_current_user),
    service: IntegrationService = Depends(get_integration_service)
):
    """获取同步状态"""
    try:
        status = await service.get_sync_status(integration_id, user_id)
        if not status:
            raise HTTPException(status_code=404, detail="集成配置不存在")
        return status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取同步状态失败: {str(e)}")


@router.post("/{integration_id}/test", response_model=BaseResponse)
async def test_connection(
    integration_id: int = Path(..., description="集成ID"),
    user_id: str = Depends(get_current_user),
    service: IntegrationService = Depends(get_integration_service)
):
    """测试平台连接"""
    try:
        success = await service.test_connection(integration_id, user_id)
        if success:
            return BaseResponse(message="连接测试成功")
        else:
            raise HTTPException(status_code=400, detail="连接测试失败")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"连接测试失败: {str(e)}") 