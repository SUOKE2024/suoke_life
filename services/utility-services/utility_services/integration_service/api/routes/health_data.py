"""
health_data - 索克生活项目模块
"""

import logging
from datetime import date
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.security import TokenData, verify_token
from ...models.health_data import HealthDataType
from ...services.health_data_service import HealthDataService

"""
健康数据相关的API路由
"""


logger = logging.getLogger(__name__)

router = APIRouter(prefix=" / health - data", tags=["健康数据"])


class HealthDataResponse(BaseModel):
    """健康数据响应模型"""

    id: int
    user_id: str
    platform_id: str
    data_type: str
    value: Optional[float]
    unit: Optional[str]
    extra_data: Optional[Dict[str, Any]]
    source_id: Optional[str]
    created_at: str
    updated_at: str


class HealthDataCreateRequest(BaseModel):
    """健康数据创建请求模型"""

    platform_id: str
    data_type: HealthDataType
    value: Optional[float] = None
    unit: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None
    source_id: Optional[str] = None


class HealthDataBatchCreateRequest(BaseModel):
    """健康数据批量创建请求模型"""

    platform_id: str
    data_list: List[Dict[str, Any]]


class HealthDataUpdateRequest(BaseModel):
    """健康数据更新请求模型"""

    value: Optional[float] = None
    unit: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


class HealthDataSyncRequest(BaseModel):
    """健康数据同步请求模型"""

    platform_id: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    data_types: Optional[List[HealthDataType]] = None


class HealthDataStatsResponse(BaseModel):
    """健康数据统计响应模型"""

    total_count: int
    data_type_counts: Dict[str, int]
    platform_counts: Dict[str, int]
    date_range: Dict[str, str]


@router.get(" / types", summary="获取支持的数据类型")
async def get_supported_data_types() -> Dict[str, Any]:
    """
    获取系统支持的健康数据类型列表
    """
    try:
        data_types = [data_type.value for data_type in HealthDataType]

        return {"data_types": data_types, "count": len(data_types)}

    except Exception as e:
        logger.error(f"获取数据类型失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取数据类型过程中发生错误",
        )


@router.get(" / ", response_model=List[HealthDataResponse], summary="获取健康数据列表")
async def get_health_data(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    current_user: TokenData = Depends(verify_token),
    db: Session = Depends(get_db),
) -> List[HealthDataResponse]:
    """获取当前用户的健康数据列表"""
    try:
        health_data_service = HealthDataService(db)

        health_data_list = health_data_service.get_user_health_data(
            user_id=current_user.user_id, skip=skip, limit=limit
        )

        return [
            HealthDataResponse(
                id=data.id,
                user_id=data.user_id,
                platform_id=data.platform_id,
                data_type=data.data_type.value,
                value=data.value,
                unit=data.unit,
                extra_data=data.extra_data,
                source_id=data.source_id,
                created_at=data.created_at.isoformat(),
                updated_at=data.updated_at.isoformat(),
            )
            for data in health_data_list
        ]

    except Exception as e:
        logger.error(f"获取健康数据列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取健康数据列表过程中发生错误",
        )


@router.get(
    " / {data_id}", response_model=HealthDataResponse, summary="获取健康数据详情"
)
async def get_health_data_detail(
    data_id: int,
    current_user: TokenData = Depends(verify_token),
    db: Session = Depends(get_db),
) -> HealthDataResponse:
    """
    获取指定健康数据的详细信息

    - * *data_id * *: 健康数据ID
    """
    try:
        health_data_service = HealthDataService(db)

        health_data = health_data_service.get_health_data_by_id(data_id)
        if not health_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="健康数据不存在"
            )

        # 验证数据所有权
        if health_data.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此健康数据"
            )

        return HealthDataResponse(
            id=health_data.id,
            user_id=health_data.user_id,
            platform_id=health_data.platform_id,
            data_type=health_data.data_type.value,
            value=health_data.value,
            unit=health_data.unit,
            extra_data=health_data.extra_data,
            source_id=health_data.source_id,
            created_at=health_data.created_at.isoformat(),
            updated_at=health_data.updated_at.isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取健康数据详情失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取健康数据详情过程中发生错误",
        )


@router.post(" / ", response_model=HealthDataResponse, summary="创建健康数据")
async def create_health_data(
    health_data: HealthDataCreateRequest,
    current_user: TokenData = Depends(verify_token),
    db: Session = Depends(get_db),
) -> HealthDataResponse:
    """
    创建新的健康数据记录

    - * *platform_id * *: 平台ID
    - * *data_type * *: 数据类型
    - * *value * *: 数据值
    - * *unit * *: 单位
    - * *extra_data * *: 额外数据
    - * *source_id * *: 源数据ID
    """
    try:
        health_data_service = HealthDataService(db)

        created_data = health_data_service.create_health_data(
            user_id=current_user.user_id,
            platform_id=health_data.platform_id,
            data_type=health_data.data_type,
            value=health_data.value,
            unit=health_data.unit,
            extra_data=health_data.extra_data,
            source_id=health_data.source_id,
        )

        logger.info(f"用户 {current_user.username} 创建健康数据 {created_data.id}")

        return HealthDataResponse(
            id=created_data.id,
            user_id=created_data.user_id,
            platform_id=created_data.platform_id,
            data_type=created_data.data_type.value,
            value=created_data.value,
            unit=created_data.unit,
            extra_data=created_data.extra_data,
            source_id=created_data.source_id,
            created_at=created_data.created_at.isoformat(),
            updated_at=created_data.updated_at.isoformat(),
        )

    except Exception as e:
        logger.error(f"创建健康数据失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建健康数据过程中发生错误",
        )


@router.post(" / batch", summary="批量创建健康数据")
async def create_health_data_batch(
    batch_data: HealthDataBatchCreateRequest,
    current_user: TokenData = Depends(verify_token),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    批量创建健康数据记录

    - * *platform_id * *: 平台ID
    - * *data_list * *: 数据列表
    """
    try:
        health_data_service = HealthDataService(db)

        created_count = health_data_service.create_health_data_batch(
            user_id=current_user.user_id,
            platform_id=batch_data.platform_id,
            data_list=batch_data.data_list,
        )

        logger.info(f"用户 {current_user.username} 批量创建 {created_count} 条健康数据")

        return {"message": "批量创建成功", "created_count": created_count}

    except Exception as e:
        logger.error(f"批量创建健康数据失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="批量创建健康数据过程中发生错误",
        )


@router.put(" / {data_id}", response_model=HealthDataResponse, summary="更新健康数据")
async def update_health_data(
    data_id: int,
    update_data: HealthDataUpdateRequest,
    current_user: TokenData = Depends(verify_token),
    db: Session = Depends(get_db),
) -> HealthDataResponse:
    """
    更新健康数据记录

    - * *data_id * *: 健康数据ID
    """
    try:
        health_data_service = HealthDataService(db)

        # 验证数据存在性和所有权
        health_data = health_data_service.get_health_data_by_id(data_id)
        if not health_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="健康数据不存在"
            )

        if health_data.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="无权修改此健康数据"
            )

        # 更新数据
        update_dict = update_data.dict(exclude_unset=True)
        updated_data = health_data_service.update_health_data(data_id, update_dict)

        logger.info(f"用户 {current_user.username} 更新健康数据 {data_id}")

        return HealthDataResponse(
            id=updated_data.id,
            user_id=updated_data.user_id,
            platform_id=updated_data.platform_id,
            data_type=updated_data.data_type.value,
            value=updated_data.value,
            unit=updated_data.unit,
            extra_data=updated_data.extra_data,
            source_id=updated_data.source_id,
            created_at=updated_data.created_at.isoformat(),
            updated_at=updated_data.updated_at.isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新健康数据失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新健康数据过程中发生错误",
        )


@router.delete(" / {data_id}", summary="删除健康数据")
async def delete_health_data(
    data_id: int,
    current_user: TokenData = Depends(verify_token),
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    """
    删除健康数据记录

    - * *data_id * *: 健康数据ID
    """
    try:
        health_data_service = HealthDataService(db)

        # 验证数据存在性和所有权
        health_data = health_data_service.get_health_data_by_id(data_id)
        if not health_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="健康数据不存在"
            )

        if health_data.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="无权删除此健康数据"
            )

        health_data_service.delete_health_data(data_id)

        logger.info(f"用户 {current_user.username} 删除健康数据 {data_id}")

        return {"message": "健康数据删除成功"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除健康数据失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除健康数据过程中发生错误",
        )


@router.post(" / sync", summary="同步健康数据")
async def sync_health_data(
    sync_request: HealthDataSyncRequest,
    current_user: TokenData = Depends(verify_token),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    从指定平台同步健康数据

    - * *platform_id * *: 平台ID
    - * *start_date * *: 开始日期
    - * *end_date * *: 结束日期
    - * *data_types * *: 数据类型列表
    """
    try:
        health_data_service = HealthDataService(db)

        sync_result = health_data_service.sync_health_data_from_platform(
            user_id=current_user.user_id,
            platform_id=sync_request.platform_id,
            start_date=sync_request.start_date,
            end_date=sync_request.end_date,
            data_types=sync_request.data_types,
        )

        logger.info(
            f"用户 {current_user.username} 从平台 {sync_request.platform_id} 同步健康数据"
        )

        return sync_result

    except Exception as e:
        logger.error(f"同步健康数据失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="同步健康数据过程中发生错误",
        )


@router.get(
    " / stats / summary",
    response_model=HealthDataStatsResponse,
    summary="获取健康数据统计",
)
async def get_health_data_stats(
    platform_id: Optional[str] = Query(None, description="平台ID筛选"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    current_user: TokenData = Depends(verify_token),
    db: Session = Depends(get_db),
) -> HealthDataStatsResponse:
    """
    获取用户健康数据统计信息

    - * *platform_id * *: 平台ID筛选
    - * *start_date * *: 开始日期
    - * *end_date * *: 结束日期
    """
    try:
        health_data_service = HealthDataService(db)

        stats = health_data_service.get_user_health_data_stats(
            user_id=current_user.user_id,
            platform_id=platform_id,
            start_date=start_date,
            end_date=end_date,
        )

        return HealthDataStatsResponse(**stats)

    except Exception as e:
        logger.error(f"获取健康数据统计失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取健康数据统计过程中发生错误",
        )
