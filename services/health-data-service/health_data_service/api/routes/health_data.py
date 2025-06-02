"""健康数据API路由"""

from typing import Any, Dict, Optional

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from loguru import logger

from health_data_service.core.exceptions import DatabaseError
from health_data_service.core.exceptions import NotFoundError
from health_data_service.core.exceptions import ValidationError
from health_data_service.models import CreateHealthDataRequest
from health_data_service.models import CreateVitalSignsRequest
from health_data_service.models import DataType
from health_data_service.models import HealthDataResponse
from health_data_service.models import PaginatedResponse
from health_data_service.models import VitalSignsResponse
from health_data_service.services import HealthDataService
from health_data_service.services import VitalSignsService

router = APIRouter()

# 服务实例
health_data_service = HealthDataService()
vital_signs_service = VitalSignsService()


def get_health_data_service() -> HealthDataService:
    """获取健康数据服务实例"""
    return HealthDataService()


@router.post("/health-data", response_model=HealthDataResponse)
async def create_health_data(
    data: CreateHealthDataRequest,
    service: HealthDataService = Depends(get_health_data_service),
) -> HealthDataResponse:
    """创建健康数据"""
    try:
        result = await service.create(data)
        logger.info(f"成功创建健康数据: {result.id}")
        return HealthDataResponse(
            success=True,
            message="健康数据创建成功",
            data=result,
        )
    except ValidationError as e:
        logger.warning(f"数据验证失败: {e.message}")
        raise HTTPException(status_code=400, detail=e.message) from e
    except DatabaseError as e:
        logger.error(f"数据库操作失败: {e.message}")
        raise HTTPException(status_code=500, detail=e.message) from e


@router.get("/health-data/{data_id}", response_model=HealthDataResponse)
async def get_health_data(
    data_id: int,
    service: HealthDataService = Depends(get_health_data_service),
) -> HealthDataResponse:
    """获取健康数据详情"""
    try:
        result = await service.get_by_id(data_id)
        if not result:
            raise NotFoundError(f"健康数据 {data_id} 不存在")

        logger.info(f"成功获取健康数据: {data_id}")
        return HealthDataResponse(
            data=result,
            message="查询成功"
        )
    except NotFoundError as e:
        logger.warning(f"资源不存在: {e.message}")
        raise HTTPException(status_code=404, detail=e.message) from e
    except DatabaseError as e:
        logger.error(f"数据库操作失败: {e.message}")
        raise HTTPException(status_code=500, detail=e.message) from e


@router.get("/health-data", response_model=PaginatedResponse)
async def list_health_data(
    user_id: Optional[int] = Query(None, description="用户ID"),
    data_type: Optional[DataType] = Query(None, description="数据类型"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    service: HealthDataService = Depends(get_health_data_service),
) -> PaginatedResponse:
    """获取健康数据列表"""
    try:
        skip = (page - 1) * page_size
        filters: Dict[str, Any] = {}
        if user_id:
            filters["user_id"] = user_id
        if data_type:
            filters["data_type"] = data_type.value

        data_list, total = await service.list(
            skip=skip,
            limit=page_size,
            **filters
        )

        logger.info(f"成功获取健康数据列表，共 {len(data_list)} 条记录")
        return PaginatedResponse.create(
            data=data_list,
            total=total,
            page=page,
            page_size=page_size,
            message="查询成功"
        )
    except DatabaseError as e:
        logger.error(f"数据库操作失败: {e.message}")
        raise HTTPException(status_code=500, detail=e.message) from e


@router.get("/users/{user_id}/health-data", response_model=PaginatedResponse)
async def get_user_health_data(
    user_id: int,
    data_type: Optional[DataType] = Query(None, description="数据类型"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    service: HealthDataService = Depends(get_health_data_service),
) -> PaginatedResponse:
    """获取用户的健康数据"""
    try:
        skip = (page - 1) * page_size
        data_list, total = await service.get_by_user_id(
            user_id=user_id,
            skip=skip,
            limit=page_size,
            data_type=data_type.value if data_type else None,
        )

        logger.info(f"成功获取用户 {user_id} 的健康数据，共 {len(data_list)} 条记录")
        return PaginatedResponse.create(
            data=data_list,
            total=total,
            page=page,
            page_size=page_size,
            message="查询成功"
        )
    except DatabaseError as e:
        logger.error(f"数据库操作失败: {e.message}")
        raise HTTPException(status_code=500, detail=e.message) from e


@router.delete("/health-data/{data_id}")
async def delete_health_data(
    data_id: int,
    service: HealthDataService = Depends(get_health_data_service),
) -> dict:
    """删除健康数据"""
    try:
        success = await service.delete(data_id)
        if not success:
            raise NotFoundError(f"健康数据 {data_id} 不存在")

        logger.info(f"成功删除健康数据: {data_id}")
        return {"success": True, "message": "健康数据删除成功"}
    except DatabaseError as e:
        logger.error(f"数据库操作失败: {e.message}")
        raise HTTPException(status_code=500, detail=e.message) from e


@router.post("/vital-signs", response_model=VitalSignsResponse)
async def create_vital_signs(data: CreateVitalSignsRequest) -> VitalSignsResponse:
    """创建生命体征数据"""
    try:
        vital_signs = await vital_signs_service.create(data)
        return VitalSignsResponse(
            data=vital_signs,
            message="生命体征数据创建成功"
        )
    except ValidationError as e:
        logger.warning(f"数据验证失败: {e.message}")
        raise HTTPException(status_code=400, detail=e.message) from e
    except DatabaseError as e:
        logger.error(f"数据库操作失败: {e.message}")
        raise HTTPException(status_code=500, detail=e.message) from e


@router.get("/vital-signs/{vital_signs_id}", response_model=VitalSignsResponse)
async def get_vital_signs(vital_signs_id: int) -> VitalSignsResponse:
    """获取生命体征数据详情"""
    try:
        vital_signs = await vital_signs_service.get_by_id(vital_signs_id)
        if not vital_signs:
            raise HTTPException(status_code=404, detail="生命体征数据不存在")

        return VitalSignsResponse(
            data=vital_signs,
            message="查询成功"
        )
    except DatabaseError as e:
        logger.error(f"数据库操作失败: {e.message}")
        raise HTTPException(status_code=500, detail=e.message) from e
