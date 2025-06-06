"""
health_data - 索克生活项目模块
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from health_data_service.core.exceptions import DatabaseError, NotFoundError, ValidationError
from health_data_service.models import (
from health_data_service.services.health_data_service import HealthDataService, VitalSignsService, TCMDiagnosisService
from typing import List, Optional

"""健康数据API路由"""


    CreateHealthDataRequest,
    CreateVitalSignsRequest,
    HealthData,
    HealthDataResponse,
    UpdateHealthDataRequest,
    VitalSigns,
    VitalSignsResponse,
    DataType,
    DataSource,
)

router = APIRouter(prefix="/health-data", tags=["健康数据"])

# 服务实例
health_data_service = HealthDataService()
vital_signs_service = VitalSignsService()
tcm_diagnosis_service = TCMDiagnosisService()


@router.post("/", response_model=HealthDataResponse, status_code=status.HTTP_201_CREATED)
async def create_health_data(data: CreateHealthDataRequest) -> HealthDataResponse:
    """创建健康数据"""
    try:
        health_data = await health_data_service.create(data)
        return HealthDataResponse(
            success=True,
            message="健康数据创建成功",
            data=health_data
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"数据验证失败: {str(e)}"
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库操作失败: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建健康数据失败: {str(e)}"
        )


@router.get("/{data_id}", response_model=HealthDataResponse)
async def get_health_data(data_id: int) -> HealthDataResponse:
    """根据ID获取健康数据"""
    try:
        health_data = await health_data_service.get_by_id(data_id)
        if not health_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"健康数据不存在: id={data_id}"
            )
        
        return HealthDataResponse(
            success=True,
            message="获取健康数据成功",
            data=health_data
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取健康数据失败: {str(e)}"
        )


@router.put("/{data_id}", response_model=HealthDataResponse)
async def update_health_data(data_id: int, data: UpdateHealthDataRequest) -> HealthDataResponse:
    """更新健康数据"""
    try:
        health_data = await health_data_service.update(data_id, data)
        if not health_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"健康数据不存在: id={data_id}"
            )
        
        return HealthDataResponse(
            success=True,
            message="健康数据更新成功",
            data=health_data
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"数据验证失败: {str(e)}"
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库操作失败: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新健康数据失败: {str(e)}"
        )


@router.delete("/{data_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_health_data(data_id: int):
    """删除健康数据"""
    try:
        success = await health_data_service.delete(data_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"健康数据不存在: id={data_id}"
            )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库操作失败: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除健康数据失败: {str(e)}"
        )


@router.get("/", response_model=dict)
async def list_health_data(
    user_id: int = Query(..., description="用户ID"),
    data_type: Optional[str] = Query(None, description="数据类型"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
) -> dict:
    """获取健康数据列表"""
    try:
        # 验证数据类型
        if data_type and data_type not in [dt.value for dt in DataType]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的数据类型: {data_type}"
            )
        
        health_data_list, total = await health_data_service.list(
            skip=skip,
            limit=limit,
            user_id=user_id,
            data_type=data_type
        )
        
        return {
            "success": True,
            "message": "获取健康数据列表成功",
            "data": {
                "items": health_data_list,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        }
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"参数验证失败: {str(e)}"
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库操作失败: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取健康数据列表失败: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=dict)
async def get_user_health_data(
    user_id: int,
    data_type: Optional[str] = Query(None, description="数据类型"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
) -> dict:
    """根据用户ID获取健康数据"""
    try:
        # 验证数据类型
        if data_type and data_type not in [dt.value for dt in DataType]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的数据类型: {data_type}"
            )
        
        health_data_list, total = await health_data_service.get_by_user_id(
            user_id=user_id,
            data_type=data_type,
            skip=skip,
            limit=limit
        )
        
        return {
            "success": True,
            "message": "获取用户健康数据成功",
            "data": {
                "user_id": user_id,
                "items": health_data_list,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        }
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"参数验证失败: {str(e)}"
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库操作失败: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户健康数据失败: {str(e)}"
        )


# 生命体征相关路由
@router.post("/vital-signs", response_model=VitalSignsResponse, status_code=status.HTTP_201_CREATED)
async def create_vital_signs(data: CreateVitalSignsRequest) -> VitalSignsResponse:
    """创建生命体征记录"""
    try:
        vital_signs = await vital_signs_service.create(data)
        return VitalSignsResponse(
            success=True,
            message="生命体征记录创建成功",
            data=vital_signs
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"数据验证失败: {str(e)}"
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库操作失败: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建生命体征记录失败: {str(e)}"
        )


@router.get("/vital-signs/user/{user_id}", response_model=dict)
async def get_user_vital_signs(
    user_id: int,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
) -> dict:
    """根据用户ID获取生命体征列表"""
    try:
        vital_signs_list, total = await vital_signs_service.list(
            skip=skip,
            limit=limit,
            user_id=user_id
        )
        
        return {
            "success": True,
            "message": "获取用户生命体征成功",
            "data": {
                "user_id": user_id,
                "items": vital_signs_list,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        }
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"参数验证失败: {str(e)}"
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库操作失败: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户生命体征失败: {str(e)}"
        )


# 中医诊断相关路由
@router.post("/tcm-diagnosis", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_tcm_diagnosis(
    user_id: int,
    diagnosis_type: str,
    diagnosis_data: dict,
    standardized_data: Optional[dict] = None,
    quality_score: Optional[float] = None,
    practitioner_id: Optional[int] = None,
    clinic_id: Optional[int] = None,
    session_id: Optional[str] = None,
    notes: Optional[str] = None
) -> dict:
    """创建中医诊断记录"""
    try:
        # 验证诊断类型
        valid_types = ["look", "listen", "inquiry", "palpation", "calculation"]
        if diagnosis_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的诊断类型: {diagnosis_type}，支持的类型: {valid_types}"
            )
        
        record = await tcm_diagnosis_service.create_tcm_diagnosis(
            user_id=user_id,
            diagnosis_type=diagnosis_type,
            diagnosis_data=diagnosis_data,
            standardized_data=standardized_data,
            quality_score=quality_score,
            practitioner_id=practitioner_id,
            clinic_id=clinic_id,
            session_id=session_id,
            notes=notes
        )
        
        return {
            "success": True,
            "message": "中医诊断记录创建成功",
            "data": record
        }
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"数据验证失败: {str(e)}"
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库操作失败: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建中医诊断记录失败: {str(e)}"
        )


@router.get("/tcm-diagnosis/user/{user_id}", response_model=dict)
async def get_user_tcm_diagnosis(
    user_id: int,
    diagnosis_type: Optional[str] = Query(None, description="诊断类型"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
) -> dict:
    """根据用户ID获取中医诊断记录"""
    try:
        # 验证诊断类型
        if diagnosis_type:
            valid_types = ["look", "listen", "inquiry", "palpation", "calculation"]
            if diagnosis_type not in valid_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"无效的诊断类型: {diagnosis_type}，支持的类型: {valid_types}"
                )
        
        records = await tcm_diagnosis_service.get_tcm_diagnosis_by_user(
            user_id=user_id,
            diagnosis_type=diagnosis_type,
            limit=limit,
            offset=skip
        )
        
        return {
            "success": True,
            "message": "获取用户中医诊断记录成功",
            "data": {
                "user_id": user_id,
                "items": records,
                "total": len(records),
                "skip": skip,
                "limit": limit
            }
        }
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"参数验证失败: {str(e)}"
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库操作失败: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户中医诊断记录失败: {str(e)}"
        )


# 数据统计和分析路由
@router.get("/stats/user/{user_id}", response_model=dict)
async def get_user_health_stats(user_id: int) -> dict:
    """获取用户健康数据统计"""
    try:
        # 获取各类型数据统计
        stats = {}
        
        # 健康数据统计
        for data_type in DataType:
            health_data_list, count = await health_data_service.get_by_user_id(
                user_id=user_id,
                data_type=data_type.value,
                limit=1000
            )
            stats[data_type.value] = count
        
        # 生命体征统计
        vital_signs_list, vital_count = await vital_signs_service.list(
            user_id=user_id,
            limit=1000
        )
        stats["vital_signs_count"] = vital_count
        
        # 中医诊断统计
        tcm_stats = {}
        for diagnosis_type in ["look", "listen", "inquiry", "palpation", "calculation"]:
            records = await tcm_diagnosis_service.get_tcm_diagnosis_by_user(
                user_id=user_id,
                diagnosis_type=diagnosis_type,
                limit=1000
            )
            tcm_stats[diagnosis_type] = len(records)
        
        stats["tcm_diagnosis"] = tcm_stats
        
        return {
            "success": True,
            "message": "获取用户健康数据统计成功",
            "data": {
                "user_id": user_id,
                "statistics": stats
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户健康数据统计失败: {str(e)}"
        )


# 健康检查路由
@router.get("/health", response_model=dict)
async def health_check() -> dict:
    """健康检查"""
    try:
        # 检查数据库连接
        db_manager = await health_data_service._get_db_manager()
        db_healthy = await db_manager.health_check()
        
        return {
            "success": True,
            "message": "健康数据服务运行正常",
            "data": {
                "service": "health-data-service",
                "status": "healthy",
                "database": "healthy" if db_healthy else "unhealthy",
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "success": False,
                "message": "健康数据服务异常",
                "error": str(e)
            }
        )
