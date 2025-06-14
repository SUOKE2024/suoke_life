"""
health - 索克生活项目模块
"""

from ...core.monitoring import record_database_operation
from ...models.health import HealthAnalysis, HealthRecommendation
from ...services.health_service import HealthService
from ...core.dependencies import get_current_user
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Any, Dict

"""
健康管理 API 端点

提供健康数据分析、健康建议等功能
"""




router = APIRouter()


class HealthDataRequest(BaseModel):
    """健康数据请求模型"""

    data_type: str  # heart_rate, blood_pressure, sleep, exercise, etc.
    value: float
    unit: str
    timestamp: str


class HealthAnalysisRequest(BaseModel):
    """健康分析请求模型"""

    analysis_type: str = "comprehensive"  # comprehensive, specific
    time_range: int = 30  # days


@router.post("/data", response_model=dict[str, str])
async def submit_health_data(
    request: HealthDataRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    health_service: HealthService = Depends()
) -> dict[str, str]:
    """
    提交健康数据

    Args:
        request: 健康数据请求
        health_service: 健康服务实例

    Returns:
        提交结果
    """
    try:
        await health_service.submit_health_data(
            user_id=current_user["user_id"],
            data_type=request.data_type,
            value=request.value,
            unit=request.unit,
            timestamp=request.timestamp,
        )

        return {"status": "success", "message": "健康数据提交成功"}

    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"健康数据提交失败: {str(e)}")


@router.post("/analyze", response_model=HealthAnalysis)
async def analyze_health(
    request: HealthAnalysisRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    health_service: HealthService = Depends()
) -> HealthAnalysis:
    """
    分析健康数据

    Args:
        request: 健康分析请求
        health_service: 健康服务实例

    Returns:
        健康分析结果
    """
    try:
        analysis = await health_service.analyze_health_data(
            user_id=current_user["user_id"],
            analysis_type=request.analysis_type,
            time_range=request.time_range,
        )

        return analysis

    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"健康分析失败: {str(e)}")


@router.get("/recommendations", response_model=list[HealthRecommendation])
async def get_health_recommendations(
    current_user: Dict[str, Any] = Depends(get_current_user),
    health_service: HealthService = Depends()
) -> list[HealthRecommendation]:
    """
    获取健康建议

    Args:
        user_id: 用户ID
        health_service: 健康服务实例

    Returns:
        健康建议列表
    """
    try:
        # 记录指标
        record_database_operation("health", "get_recommendations", True)

        user_id = current_user["user_id"]
        recommendations = await health_service.get_health_recommendations(
            user_id=user_id
        )

        return recommendations

    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"获取健康建议失败: {str(e)}")


@router.get(" / trends / {user_id}")
async def get_health_trends(
    user_id: str, metric: str, days: int = 30, health_service: HealthService = Depends()
) -> dict[str, Any]:
    """
    获取健康趋势数据

    Args:
        user_id: 用户ID
        metric: 健康指标类型
        days: 查询天数
        health_service: 健康服务实例

    Returns:
        健康趋势数据
    """
    try:
        trends = await health_service.get_health_trends(
            user_id = user_id, metric = metric, days = days
        )

        return trends

    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"获取健康趋势失败: {str(e)}")


@router.get(" / dashboard / {user_id}")
async def get_health_dashboard(
    user_id: str, health_service: HealthService = Depends()
) -> dict[str, Any]:
    """
    获取健康仪表板数据

    Args:
        user_id: 用户ID
        health_service: 健康服务实例

    Returns:
        健康仪表板数据
    """
    try:
        dashboard = await health_service.get_health_dashboard(user_id = user_id)

        return dashboard

    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"获取健康仪表板失败: {str(e)}")
