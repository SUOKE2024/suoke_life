#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
健康数据API处理器 - 优化版
提供高性能的RESTful API接口
"""

import uuid
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from loguru import logger

from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession

from ..service.health_data_service_optimized import HealthDataServiceOptimized
from ..model.health_data import HealthData, HealthDataType, DeviceType, MeasurementUnit
from ...pkg.utils.cache_service import CacheService, cache_result
from ...pkg.utils.error_handler import (
    APIError, ValidationError, DatabaseError, 
    handle_api_errors, rate_limit
)


# Pydantic 模型定义
class HealthDataRequest(BaseModel):
    """健康数据请求模型"""
    user_id: str = Field(..., description="用户ID")
    data_type: str = Field(..., description="数据类型")
    value: Union[float, int, Dict[str, Any]] = Field(..., description="数据值")
    unit: Optional[str] = Field(None, description="单位")
    device_type: Optional[str] = Field(None, description="设备类型")
    device_id: Optional[str] = Field(None, description="设备ID")
    source: Optional[str] = Field(None, description="数据来源")
    timestamp: Optional[datetime] = Field(None, description="时间戳")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    
    @validator('timestamp', pre=True, always=True)
    def set_timestamp(cls, v):
        return v or datetime.utcnow()


class HealthDataBatchRequest(BaseModel):
    """批量健康数据请求模型"""
    data_list: List[HealthDataRequest] = Field(..., description="健康数据列表")
    
    @validator('data_list')
    def validate_data_list(cls, v):
        if not v:
            raise ValueError("数据列表不能为空")
        if len(v) > 1000:
            raise ValueError("单次批量操作不能超过1000条记录")
        return v


class HealthDataResponse(BaseModel):
    """健康数据响应模型"""
    id: str
    user_id: str
    data_type: str
    value: Union[float, int, Dict[str, Any]]
    unit: Optional[str]
    device_type: Optional[str]
    device_id: Optional[str]
    source: Optional[str]
    timestamp: datetime
    quality_score: float
    is_validated: bool
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime


class HealthDataListResponse(BaseModel):
    """健康数据列表响应模型"""
    data: List[HealthDataResponse]
    total: int
    page: int
    page_size: int
    has_next: bool


class HealthMetricsResponse(BaseModel):
    """健康指标响应模型"""
    heart_rate_score: float
    steps_score: float
    sleep_score: float
    blood_pressure_score: float
    blood_glucose_score: float
    body_temperature_score: float
    oxygen_saturation_score: float
    overall_score: float
    grade: str
    recommendations: List[str]


class DataQualityResponse(BaseModel):
    """数据质量响应模型"""
    total_count: int
    validated_count: int
    validation_rate: float
    average_quality_score: float
    high_quality_count: int
    medium_quality_count: int
    low_quality_count: int
    high_quality_rate: float
    medium_quality_rate: float
    low_quality_rate: float


class HealthDataHandlerOptimized:
    """优化版健康数据API处理器"""
    
    def __init__(
        self, 
        health_data_service: HealthDataServiceOptimized,
        cache_service: CacheService
    ):
        """
        初始化API处理器
        
        Args:
            health_data_service: 健康数据服务
            cache_service: 缓存服务
        """
        self.health_data_service = health_data_service
        self.cache_service = cache_service
        self.router = APIRouter(prefix="/api/v1/health-data", tags=["健康数据"])
        self._setup_routes()
    
    def _setup_routes(self):
        """设置路由"""
        
        @self.router.post(
            "/",
            response_model=HealthDataResponse,
            status_code=status.HTTP_201_CREATED,
            summary="创建健康数据",
            description="创建单条健康数据记录"
        )
        @handle_api_errors
        @rate_limit(max_calls=100, window_seconds=60)
        async def create_health_data(
            request: HealthDataRequest
        ) -> HealthDataResponse:
            """创建健康数据"""
            try:
                # 转换为健康数据对象
                health_data = HealthData(
                    user_id=request.user_id,
                    data_type=HealthDataType(request.data_type),
                    value=request.value,
                    unit=MeasurementUnit(request.unit) if request.unit else None,
                    device_type=DeviceType(request.device_type) if request.device_type else None,
                    device_id=request.device_id,
                    source=request.source,
                    timestamp=request.timestamp,
                    metadata=request.metadata or {}
                )
                
                # 保存数据
                record_id = await self.health_data_service.save_health_data(health_data)
                
                # 获取保存的记录
                record = await self.health_data_service.get_health_data_by_id(record_id)
                
                return self._convert_to_response(record)
                
            except Exception as e:
                logger.error(f"创建健康数据失败: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"创建健康数据失败: {str(e)}"
                )
        
        @self.router.post(
            "/batch",
            response_model=List[HealthDataResponse],
            status_code=status.HTTP_201_CREATED,
            summary="批量创建健康数据",
            description="批量创建健康数据记录"
        )
        @handle_api_errors
        @rate_limit(max_calls=10, window_seconds=60)
        async def create_health_data_batch(
            request: HealthDataBatchRequest
        ) -> List[HealthDataResponse]:
            """批量创建健康数据"""
            try:
                # 转换为健康数据对象列表
                health_data_list = []
                for data_req in request.data_list:
                    health_data = HealthData(
                        user_id=data_req.user_id,
                        data_type=HealthDataType(data_req.data_type),
                        value=data_req.value,
                        unit=MeasurementUnit(data_req.unit) if data_req.unit else None,
                        device_type=DeviceType(data_req.device_type) if data_req.device_type else None,
                        device_id=data_req.device_id,
                        source=data_req.source,
                        timestamp=data_req.timestamp,
                        metadata=data_req.metadata or {}
                    )
                    health_data_list.append(health_data)
                
                # 批量保存数据
                record_ids = await self.health_data_service.save_health_data_batch(health_data_list)
                
                # 获取保存的记录
                records = []
                for record_id in record_ids:
                    record = await self.health_data_service.get_health_data_by_id(record_id)
                    records.append(self._convert_to_response(record))
                
                return records
                
            except Exception as e:
                logger.error(f"批量创建健康数据失败: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"批量创建健康数据失败: {str(e)}"
                )
        
        @self.router.get(
            "/users/{user_id}",
            response_model=HealthDataListResponse,
            summary="获取用户健康数据",
            description="获取指定用户的健康数据列表"
        )
        @handle_api_errors
        @rate_limit(max_calls=200, window_seconds=60)
        @cache_result(ttl=300)  # 缓存5分钟
        async def get_user_health_data(
            user_id: str = Path(..., description="用户ID"),
            data_type: Optional[str] = Query(None, description="数据类型"),
            start_time: Optional[datetime] = Query(None, description="开始时间"),
            end_time: Optional[datetime] = Query(None, description="结束时间"),
            page: int = Query(1, ge=1, description="页码"),
            page_size: int = Query(20, ge=1, le=100, description="每页大小"),
            order_by: str = Query("timestamp", description="排序字段"),
            order_desc: bool = Query(True, description="是否降序")
        ) -> HealthDataListResponse:
            """获取用户健康数据"""
            try:
                offset = (page - 1) * page_size
                
                # 获取数据
                records = await self.health_data_service.get_health_data(
                    user_id=user_id,
                    data_type=data_type,
                    start_time=start_time,
                    end_time=end_time,
                    limit=page_size,
                    offset=offset,
                    order_by=order_by,
                    order_desc=order_desc
                )
                
                # 获取总数
                total = await self.health_data_service.count_health_data(
                    user_id=user_id,
                    data_type=data_type,
                    start_time=start_time,
                    end_time=end_time
                )
                
                # 转换响应
                data = [self._convert_to_response(record) for record in records]
                
                return HealthDataListResponse(
                    data=data,
                    total=total,
                    page=page,
                    page_size=page_size,
                    has_next=offset + page_size < total
                )
                
            except Exception as e:
                logger.error(f"获取用户健康数据失败: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"获取用户健康数据失败: {str(e)}"
                )
        
        @self.router.get(
            "/{record_id}",
            response_model=HealthDataResponse,
            summary="获取健康数据详情",
            description="根据ID获取健康数据详情"
        )
        @handle_api_errors
        @rate_limit(max_calls=300, window_seconds=60)
        @cache_result(ttl=600)  # 缓存10分钟
        async def get_health_data_detail(
            record_id: str = Path(..., description="记录ID")
        ) -> HealthDataResponse:
            """获取健康数据详情"""
            try:
                record = await self.health_data_service.get_health_data_by_id(
                    uuid.UUID(record_id)
                )
                
                if not record:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="健康数据记录不存在"
                    )
                
                return self._convert_to_response(record)
                
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="无效的记录ID格式"
                )
            except Exception as e:
                logger.error(f"获取健康数据详情失败: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"获取健康数据详情失败: {str(e)}"
                )
        
        @self.router.put(
            "/{record_id}",
            response_model=HealthDataResponse,
            summary="更新健康数据",
            description="更新指定的健康数据记录"
        )
        @handle_api_errors
        @rate_limit(max_calls=50, window_seconds=60)
        async def update_health_data(
            record_id: str = Path(..., description="记录ID"),
            updates: Dict[str, Any] = Body(..., description="更新字段")
        ) -> HealthDataResponse:
            """更新健康数据"""
            try:
                success = await self.health_data_service.update_health_data(
                    uuid.UUID(record_id),
                    updates
                )
                
                if not success:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="健康数据记录不存在"
                    )
                
                # 清除缓存
                await self.cache_service.delete_pattern(f"health_data:{record_id}*")
                
                # 获取更新后的记录
                record = await self.health_data_service.get_health_data_by_id(
                    uuid.UUID(record_id)
                )
                
                return self._convert_to_response(record)
                
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="无效的记录ID格式"
                )
            except Exception as e:
                logger.error(f"更新健康数据失败: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"更新健康数据失败: {str(e)}"
                )
        
        @self.router.delete(
            "/{record_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="删除健康数据",
            description="删除指定的健康数据记录"
        )
        @handle_api_errors
        @rate_limit(max_calls=30, window_seconds=60)
        async def delete_health_data(
            record_id: str = Path(..., description="记录ID")
        ):
            """删除健康数据"""
            try:
                success = await self.health_data_service.delete_health_data(
                    uuid.UUID(record_id)
                )
                
                if not success:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="健康数据记录不存在"
                    )
                
                # 清除缓存
                await self.cache_service.delete_pattern(f"health_data:{record_id}*")
                
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="无效的记录ID格式"
                )
            except Exception as e:
                logger.error(f"删除健康数据失败: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"删除健康数据失败: {str(e)}"
                )
        
        @self.router.get(
            "/users/{user_id}/metrics",
            response_model=HealthMetricsResponse,
            summary="获取用户健康指标",
            description="计算并获取用户的综合健康指标"
        )
        @handle_api_errors
        @rate_limit(max_calls=50, window_seconds=60)
        @cache_result(ttl=1800)  # 缓存30分钟
        async def get_user_health_metrics(
            user_id: str = Path(..., description="用户ID"),
            days: int = Query(30, ge=1, le=365, description="计算周期（天）")
        ) -> HealthMetricsResponse:
            """获取用户健康指标"""
            try:
                metrics = await self.health_data_service.calculate_health_index(
                    user_id=user_id,
                    days=days
                )
                
                return HealthMetricsResponse(
                    heart_rate_score=metrics.heart_rate_score,
                    steps_score=metrics.steps_score,
                    sleep_score=metrics.sleep_score,
                    blood_pressure_score=metrics.blood_pressure_score,
                    blood_glucose_score=metrics.blood_glucose_score,
                    body_temperature_score=metrics.body_temperature_score,
                    oxygen_saturation_score=metrics.oxygen_saturation_score,
                    overall_score=metrics.overall_score,
                    grade=metrics.grade,
                    recommendations=metrics.recommendations
                )
                
            except Exception as e:
                logger.error(f"获取用户健康指标失败: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"获取用户健康指标失败: {str(e)}"
                )
        
        @self.router.get(
            "/users/{user_id}/statistics",
            summary="获取用户数据统计",
            description="获取用户健康数据的统计信息"
        )
        @handle_api_errors
        @rate_limit(max_calls=100, window_seconds=60)
        @cache_result(ttl=900)  # 缓存15分钟
        async def get_user_statistics(
            user_id: str = Path(..., description="用户ID"),
            data_type: Optional[str] = Query(None, description="数据类型"),
            start_time: Optional[datetime] = Query(None, description="开始时间"),
            end_time: Optional[datetime] = Query(None, description="结束时间")
        ) -> Dict[str, Any]:
            """获取用户数据统计"""
            try:
                if data_type:
                    # 获取特定类型的统计
                    stats = await self.health_data_service.get_health_data_statistics(
                        user_id=user_id,
                        data_type=data_type,
                        start_time=start_time,
                        end_time=end_time
                    )
                else:
                    # 获取用户数据摘要
                    days = 30
                    if start_time and end_time:
                        days = (end_time - start_time).days
                    
                    stats = await self.health_data_service.get_user_data_summary(
                        user_id=user_id,
                        days=days
                    )
                
                return stats
                
            except Exception as e:
                logger.error(f"获取用户数据统计失败: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"获取用户数据统计失败: {str(e)}"
                )
        
        @self.router.get(
            "/quality/metrics",
            response_model=DataQualityResponse,
            summary="获取数据质量指标",
            description="获取系统或用户的数据质量指标"
        )
        @handle_api_errors
        @rate_limit(max_calls=50, window_seconds=60)
        @cache_result(ttl=1800)  # 缓存30分钟
        async def get_data_quality_metrics(
            user_id: Optional[str] = Query(None, description="用户ID"),
            data_type: Optional[str] = Query(None, description="数据类型"),
            start_time: Optional[datetime] = Query(None, description="开始时间"),
            end_time: Optional[datetime] = Query(None, description="结束时间")
        ) -> DataQualityResponse:
            """获取数据质量指标"""
            try:
                metrics = await self.health_data_service.get_data_quality_metrics(
                    user_id=user_id,
                    data_type=data_type,
                    start_time=start_time,
                    end_time=end_time
                )
                
                return DataQualityResponse(**metrics)
                
            except Exception as e:
                logger.error(f"获取数据质量指标失败: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"获取数据质量指标失败: {str(e)}"
                )
        
        @self.router.post(
            "/search",
            response_model=HealthDataListResponse,
            summary="搜索健康数据",
            description="根据条件搜索健康数据"
        )
        @handle_api_errors
        @rate_limit(max_calls=100, window_seconds=60)
        async def search_health_data(
            search_criteria: Dict[str, Any] = Body(..., description="搜索条件"),
            page: int = Query(1, ge=1, description="页码"),
            page_size: int = Query(20, ge=1, le=100, description="每页大小")
        ) -> HealthDataListResponse:
            """搜索健康数据"""
            try:
                if 'user_id' not in search_criteria:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="搜索条件必须包含用户ID"
                    )
                
                offset = (page - 1) * page_size
                
                records = await self.health_data_service.search_health_data(
                    user_id=search_criteria['user_id'],
                    search_criteria=search_criteria,
                    limit=page_size,
                    offset=offset
                )
                
                # 这里简化处理，实际应该有专门的计数方法
                total = len(records)
                
                data = [self._convert_to_response(record) for record in records]
                
                return HealthDataListResponse(
                    data=data,
                    total=total,
                    page=page,
                    page_size=page_size,
                    has_next=len(records) == page_size
                )
                
            except Exception as e:
                logger.error(f"搜索健康数据失败: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"搜索健康数据失败: {str(e)}"
                )
        
        @self.router.get(
            "/health",
            summary="健康检查",
            description="服务健康检查接口"
        )
        async def health_check():
            """健康检查"""
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow(),
                "service": "health-data-service"
            }
    
    def _convert_to_response(self, record) -> HealthDataResponse:
        """转换数据库记录为响应模型"""
        return HealthDataResponse(
            id=str(record.id),
            user_id=record.user_id,
            data_type=record.data_type,
            value=record.value,
            unit=record.unit,
            device_type=record.device_type,
            device_id=record.device_id,
            source=record.source,
            timestamp=record.timestamp,
            quality_score=record.quality_score,
            is_validated=record.is_validated,
            metadata=record.metadata,
            created_at=record.created_at,
            updated_at=record.updated_at
        )
    
    def get_router(self) -> APIRouter:
        """获取路由器"""
        return self.router 