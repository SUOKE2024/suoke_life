#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
可穿戴设备数据API路由
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from pydantic import BaseModel

from .....model.health_data import DeviceType
from ....service.health_data_service import HealthDataService
from ..dependencies import get_health_data_service, get_current_user


router = APIRouter(tags=["可穿戴设备"])


class WearableDataProcessResponse(BaseModel):
    """可穿戴设备数据处理响应模型"""
    device_type: str
    processed_items: int
    data_types: Dict[str, int]
    time_range: Dict[str, Any]


@router.post("/upload", response_model=WearableDataProcessResponse)
async def upload_wearable_data(
    device_type: DeviceType,
    file: UploadFile = File(...),
    source: str = Form("file_upload"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: HealthDataService = Depends(get_health_data_service)
):
    """
    上传并处理可穿戴设备数据文件
    
    - **device_type**: 设备类型
    - **file**: 数据文件
    - **source**: 数据来源
    """
    user_id = current_user["id"]
    
    # 检查文件类型
    content_type = file.content_type
    
    # 根据设备类型和内容类型选择适当的解析器
    if device_type == DeviceType.APPLE_HEALTH and content_type != "application/xml":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apple Health数据必须为XML格式"
        )
    
    if device_type in [DeviceType.FITBIT, DeviceType.XIAOMI] and content_type != "application/json":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{device_type.value}数据必须为JSON格式"
        )
    
    if device_type == DeviceType.GARMIN and not content_type.startswith("application/octet-stream"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Garmin数据必须为FIT格式"
        )
    
    # 读取文件内容
    file_content = await file.read()
    
    # 处理设备数据
    try:
        result = await service.process_wearable_data(
            user_id=user_id,
            device_type=device_type,
            data=file_content,
            source=source
        )
        
        return WearableDataProcessResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理设备数据时发生错误: {str(e)}"
        )


@router.post("/sync/{device_type}", response_model=WearableDataProcessResponse)
async def sync_wearable_data(
    device_type: DeviceType,
    data: Dict[str, Any],
    source: str = "api_sync",
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: HealthDataService = Depends(get_health_data_service)
):
    """
    同步可穿戴设备数据
    
    - **device_type**: 设备类型
    - **data**: 设备数据JSON
    - **source**: 数据来源
    """
    user_id = current_user["id"]
    
    # 处理设备数据
    try:
        result = await service.process_wearable_data(
            user_id=user_id,
            device_type=device_type,
            data=data,
            source=source
        )
        
        return WearableDataProcessResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理设备数据时发生错误: {str(e)}"
        )


@router.get("/supported", response_model=List[Dict[str, Any]])
async def get_supported_devices(
    request: Dict[str, Any] = Depends(get_health_data_service)
):
    """
    获取支持的设备类型和数据类型
    """
    config = request.config['wearable_data']['supported_devices']
    
    return [
        {
            "name": device['name'],
            "display_name": {
                "apple_health": "Apple Health",
                "fitbit": "Fitbit",
                "garmin": "Garmin",
                "xiaomi": "Xiaomi/米健康"
            }.get(device['name'], device['name']),
            "data_types": device['data_types']
        }
        for device in config
    ] 