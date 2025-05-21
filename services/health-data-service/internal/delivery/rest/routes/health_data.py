#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
健康数据API路由
"""

from typing import List, Dict, Any, Optional, Union
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from pydantic import BaseModel

from .....model.health_data import (
    HealthData, HealthDataType, DeviceType, MeasurementUnit
)
from ....service.health_data_service import HealthDataService
from ..dependencies import get_health_data_service, get_current_user


router = APIRouter(tags=["健康数据"])


class HealthDataResponse(BaseModel):
    """健康数据响应模型"""
    id: UUID
    user_id: UUID
    data_type: str
    timestamp: datetime
    device_type: str
    device_id: Optional[str] = None
    value: Union[float, int, str, Dict]
    unit: str
    source: str
    metadata: Dict[str, Any]
    created_at: datetime


class HealthDataCreateRequest(BaseModel):
    """健康数据创建请求模型"""
    data_type: HealthDataType
    timestamp: datetime
    device_type: DeviceType
    device_id: Optional[str] = None
    value: Union[float, int, str, Dict]
    unit: MeasurementUnit
    source: str
    metadata: Optional[Dict[str, Any]] = None


class HealthDataBatchCreateRequest(BaseModel):
    """健康数据批量创建请求模型"""
    records: List[HealthDataCreateRequest]


class HealthDataStatisticsResponse(BaseModel):
    """健康数据统计响应模型"""
    average: float
    maximum: float
    minimum: float
    count: int
    start_time: datetime
    end_time: datetime
    data_type: str


@router.get("", response_model=List[HealthDataResponse])
async def get_health_data(
    request: Request,
    data_type: Optional[HealthDataType] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: HealthDataService = Depends(get_health_data_service)
):
    """
    获取用户健康数据
    
    - **data_type**: 数据类型过滤
    - **start_time**: 开始时间过滤
    - **end_time**: 结束时间过滤
    - **limit**: 返回记录限制
    - **offset**: 返回记录偏移
    """
    user_id = current_user["id"]
    
    data_records = await service.get_health_data(
        user_id=user_id,
        data_type=data_type,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        offset=offset
    )
    
    # 转换为响应模型
    results = []
    for record in data_records:
        results.append(
            HealthDataResponse(
                id=record.id,
                user_id=record.user_id,
                data_type=record.data_type.value,
                timestamp=record.timestamp,
                device_type=record.device_type.value,
                device_id=record.device_id,
                value=record.value,
                unit=record.unit.value,
                source=record.source,
                metadata=record.metadata,
                created_at=record.created_at
            )
        )
    
    return results


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_health_data(
    request: HealthDataCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: HealthDataService = Depends(get_health_data_service)
):
    """
    创建健康数据记录
    
    - **data_type**: 数据类型
    - **timestamp**: 时间戳
    - **device_type**: 设备类型
    - **device_id**: 设备ID
    - **value**: 数据值
    - **unit**: 单位
    - **source**: 来源
    - **metadata**: 元数据
    """
    user_id = current_user["id"]
    
    # 创建健康数据对象
    health_data = HealthData(
        user_id=user_id,
        data_type=request.data_type,
        timestamp=request.timestamp,
        device_type=request.device_type,
        device_id=request.device_id,
        value=request.value,
        unit=request.unit,
        source=request.source,
        metadata=request.metadata or {}
    )
    
    # 保存健康数据
    data_id = await service.save_health_data(health_data)
    
    return {"id": data_id, "message": "健康数据已成功保存"}


@router.post("/batch", status_code=status.HTTP_201_CREATED)
async def create_health_data_batch(
    request: HealthDataBatchCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: HealthDataService = Depends(get_health_data_service)
):
    """
    批量创建健康数据记录
    
    - **records**: 健康数据记录列表
    """
    user_id = current_user["id"]
    
    # 创建健康数据对象列表
    health_data_list = []
    for record in request.records:
        health_data = HealthData(
            user_id=user_id,
            data_type=record.data_type,
            timestamp=record.timestamp,
            device_type=record.device_type,
            device_id=record.device_id,
            value=record.value,
            unit=record.unit,
            source=record.source,
            metadata=record.metadata or {}
        )
        health_data_list.append(health_data)
    
    # 批量保存健康数据
    data_ids = await service.save_health_data_batch(health_data_list)
    
    return {
        "count": len(data_ids),
        "message": f"已成功保存{len(data_ids)}条健康数据记录"
    }


@router.get("/statistics/{data_type}", response_model=HealthDataStatisticsResponse)
async def get_health_data_statistics(
    data_type: HealthDataType,
    days: int = Query(30, ge=1, le=365),
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: HealthDataService = Depends(get_health_data_service)
):
    """
    获取健康数据统计
    
    - **data_type**: 数据类型
    - **days**: 统计天数
    """
    user_id = current_user["id"]
    
    statistics = await service.get_health_statistics(
        user_id=user_id,
        data_type=data_type,
        days=days
    )
    
    return statistics 