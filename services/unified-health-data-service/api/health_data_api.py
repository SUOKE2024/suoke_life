"""
健康数据API接口
提供健康数据的RESTful API服务
"""

import logging
from datetime import datetime, timedelta
from typing import Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from pydantic import BaseModel, Field

from ..unified_health_data_service.health_data_service.models.health_data import (
    HealthDataCreate, VitalSignsCreate, DiagnosticDataCreate, TCMDataCreate
)
from ..unified_health_data_service.health_data_service.services.health_data_service import HealthDataService

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/v1/health-data", tags=["健康数据"])

# 依赖注入
async def get_health_data_service() -> HealthDataService:
    """获取健康数据服务实例"""
    # 这里应该从依赖注入容器获取服务实例
    # 暂时创建新实例
    service = HealthDataService()
    if not service.running:
        await service.start()
    return service

# 响应模型
class APIResponse(BaseModel):
    """API响应基础模型"""
    success: bool = Field(..., description="请求是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间")

class PaginatedResponse(BaseModel):
    """分页响应模型"""
    items: List[Any] = Field(..., description="数据项")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页")
    size: int = Field(..., description="页大小")
    pages: int = Field(..., description="总页数")

# 健康数据接口
@router.post("/", response_model=APIResponse)
async def create_health_data(
    data: HealthDataCreate,
    service: HealthDataService = Depends(get_health_data_service)
) -> APIResponse:
    """创建健康数据"""
    try:
        result = await service.process_data(data.dict())
        
        if result.get('status') == 'success':
            return APIResponse(
                success=True,
                message="健康数据创建成功",
                data={
                    "data_id": result.get('data_id'),
                    "processed_data": result.get('processed_data')
                }
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"健康数据创建失败: {result.get('error')}"
            )
            
    except Exception as e:
        logger.error(f"创建健康数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=APIResponse)
async def get_health_data(
    user_id: str = Query(..., description="用户ID"),
    data_type: Optional[str] = Query(None, description="数据类型"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="页大小"),
    service: HealthDataService = Depends(get_health_data_service)
) -> APIResponse:
    """查询健康数据"""
    try:
        # 计算偏移量
        (page - 1) * size
        
        # 查询数据
        results = await service.query_health_data(
            user_id=user_id,
            data_type=data_type,
            start_date=start_date,
            end_date=end_date,
            limit=size
        )
        
        # 计算总数（简化实现）
        total = len(results)
        pages = (total + size - 1) // size
        
        return APIResponse(
            success=True,
            message="查询成功",
            data=PaginatedResponse(
                items=results,
                total=total,
                page=page,
                size=size,
                pages=pages
            )
        )
        
    except Exception as e:
        logger.error(f"查询健康数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{data_id}", response_model=APIResponse)
async def get_health_data_by_id(
    data_id: str = Path(..., description="数据ID"),
    service: HealthDataService = Depends(get_health_data_service)
) -> APIResponse:
    """根据ID获取健康数据"""
    try:
        # 这里需要实现根据ID查询的方法
        # 暂时返回模拟数据
        result = {
            "id": data_id,
            "message": "根据ID查询功能待实现"
        }
        
        return APIResponse(
            success=True,
            message="查询成功",
            data=result
        )
        
    except Exception as e:
        logger.error(f"根据ID查询健康数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 生命体征接口
@router.post("/vital-signs", response_model=APIResponse)
async def create_vital_signs(
    data: VitalSignsCreate,
    service: HealthDataService = Depends(get_health_data_service)
) -> APIResponse:
    """创建生命体征数据"""
    try:
        # 转换为健康数据格式
        health_data = {
            "user_id": data.user_id,
            "data_type": "vital_signs",
            "heart_rate": data.heart_rate,
            "blood_pressure_systolic": data.blood_pressure_systolic,
            "blood_pressure_diastolic": data.blood_pressure_diastolic,
            "temperature": data.temperature,
            "oxygen_saturation": data.oxygen_saturation,
            "respiratory_rate": data.respiratory_rate,
            "recorded_at": data.recorded_at or datetime.utcnow()
        }
        
        result = await service.process_data(health_data)
        
        if result.get('status') == 'success':
            return APIResponse(
                success=True,
                message="生命体征数据创建成功",
                data={
                    "data_id": result.get('data_id'),
                    "processed_data": result.get('processed_data')
                }
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"生命体征数据创建失败: {result.get('error')}"
            )
            
    except Exception as e:
        logger.error(f"创建生命体征数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vital-signs/latest", response_model=APIResponse)
async def get_latest_vital_signs(
    user_id: str = Query(..., description="用户ID"),
    service: HealthDataService = Depends(get_health_data_service)
) -> APIResponse:
    """获取最新生命体征"""
    try:
        result = await service.get_latest_vital_signs(user_id)
        
        if result:
            return APIResponse(
                success=True,
                message="获取最新生命体征成功",
                data=result
            )
        else:
            return APIResponse(
                success=False,
                message="未找到生命体征数据",
                data=None
            )
            
    except Exception as e:
        logger.error(f"获取最新生命体征失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 诊断数据接口
@router.post("/diagnostics", response_model=APIResponse)
async def create_diagnostic_data(
    data: DiagnosticDataCreate,
    service: HealthDataService = Depends(get_health_data_service)
) -> APIResponse:
    """创建诊断数据"""
    try:
        # 转换为健康数据格式
        health_data = {
            "user_id": data.user_id,
            "data_type": "diagnostic",
            "diagnosis_type": data.diagnosis_type,
            "diagnosis_result": data.diagnosis_result,
            "confidence_score": data.confidence_score,
            "raw_data": data.raw_data,
            "processed_data": data.processed_data,
            "doctor_id": data.doctor_id
        }
        
        result = await service.process_data(health_data)
        
        if result.get('status') == 'success':
            return APIResponse(
                success=True,
                message="诊断数据创建成功",
                data={
                    "data_id": result.get('data_id'),
                    "processed_data": result.get('processed_data')
                }
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"诊断数据创建失败: {result.get('error')}"
            )
            
    except Exception as e:
        logger.error(f"创建诊断数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 中医数据接口
@router.post("/tcm", response_model=APIResponse)
async def create_tcm_data(
    data: TCMDataCreate,
    service: HealthDataService = Depends(get_health_data_service)
) -> APIResponse:
    """创建中医数据"""
    try:
        # 转换为健康数据格式
        health_data = {
            "user_id": data.user_id,
            "data_type": "tcm",
            "diagnosis_method": data.diagnosis_method,
            "symptoms": data.symptoms,
            "constitution": data.constitution,
            "syndrome_differentiation": data.syndrome_differentiation,
            "treatment_plan": data.treatment_plan
        }
        
        result = await service.process_data(health_data)
        
        if result.get('status') == 'success':
            return APIResponse(
                success=True,
                message="中医数据创建成功",
                data={
                    "data_id": result.get('data_id'),
                    "processed_data": result.get('processed_data')
                }
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"中医数据创建失败: {result.get('error')}"
            )
            
    except Exception as e:
        logger.error(f"创建中医数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 趋势分析接口
@router.get("/trends", response_model=APIResponse)
async def get_health_trends(
    user_id: str = Query(..., description="用户ID"),
    data_type: str = Query(..., description="数据类型"),
    days: int = Query(30, ge=1, le=365, description="分析天数"),
    service: HealthDataService = Depends(get_health_data_service)
) -> APIResponse:
    """获取健康趋势分析"""
    try:
        result = await service.get_health_trends(
            user_id=user_id,
            data_type=data_type,
            days=days
        )
        
        return APIResponse(
            success=True,
            message="趋势分析获取成功",
            data=result
        )
        
    except Exception as e:
        logger.error(f"获取健康趋势失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 健康报告接口
@router.get("/report", response_model=APIResponse)
async def generate_health_report(
    user_id: str = Query(..., description="用户ID"),
    service: HealthDataService = Depends(get_health_data_service)
) -> APIResponse:
    """生成健康报告"""
    try:
        result = await service.generate_health_report(user_id)
        
        return APIResponse(
            success=True,
            message="健康报告生成成功",
            data=result
        )
        
    except Exception as e:
        logger.error(f"生成健康报告失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 数据统计接口
@router.get("/statistics", response_model=APIResponse)
async def get_health_statistics(
    user_id: str = Query(..., description="用户ID"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    service: HealthDataService = Depends(get_health_data_service)
) -> APIResponse:
    """获取健康数据统计"""
    try:
        # 设置默认时间范围
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # 查询数据
        results = await service.query_health_data(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )
        
        # 计算统计信息
        statistics = {
            "total_records": len(results),
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "data_types": {},
            "latest_update": None
        }
        
        # 按数据类型分组统计
        for record in results:
            data_type = record.get('data_type', 'unknown')
            if data_type not in statistics["data_types"]:
                statistics["data_types"][data_type] = 0
            statistics["data_types"][data_type] += 1
            
            # 更新最新时间
            created_at = record.get('created_at')
            if created_at:
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                if not statistics["latest_update"] or created_at > statistics["latest_update"]:
                    statistics["latest_update"] = created_at.isoformat()
        
        return APIResponse(
            success=True,
            message="统计信息获取成功",
            data=statistics
        )
        
    except Exception as e:
        logger.error(f"获取健康数据统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 健康状态检查
@router.get("/health", response_model=APIResponse)
async def health_check(
    service: HealthDataService = Depends(get_health_data_service)
) -> APIResponse:
    """健康数据服务状态检查"""
    try:
        status = service.get_service_status()
        
        return APIResponse(
            success=True,
            message="服务状态正常",
            data=status
        )
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 