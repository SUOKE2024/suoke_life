"""
dashboard - 索克生活项目模块
"""

from ...core.database import get_session_dependency
from ...core.models import DashboardData, ReviewStatistics
from ...core.service import HumanReviewService
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Optional
import structlog

"""
仪表板路由
Dashboard Routes

提供审核系统的统计数据和仪表板信息
"""




logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get(
    "/",
    response_model=DashboardData,
    summary="获取仪表板数据",
    description="获取审核系统的完整仪表板数据",
)
async def get_dashboard(
    session: AsyncSession = Depends(get_session_dependency),
) -> DashboardData:
    """
    获取仪表板数据

    Args:
        session: 数据库会话

    Returns:
        仪表板数据

    Raises:
        HTTPException: 获取失败时抛出
    """
    try:
        service = HumanReviewService()
        dashboard_data = await service.get_dashboard_data(session)

        logger.info("Dashboard data retrieved")
        return dashboard_data

    except Exception as e:
        logger.error("Failed to get dashboard data", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard data: {str(e)}",
        )


@router.get(
    "/statistics",
    response_model=ReviewStatistics,
    summary="获取审核统计",
    description="获取审核系统的统计数据",
)
async def get_statistics(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    session: AsyncSession = Depends(get_session_dependency),
) -> ReviewStatistics:
    """
    获取审核统计

    Args:
        days: 统计天数
        session: 数据库会话

    Returns:
        审核统计数据

    Raises:
        HTTPException: 获取失败时抛出
    """
    try:
        service = HumanReviewService()
        statistics = await service.get_review_statistics(session)

        logger.info("Review statistics retrieved", days=days)
        return statistics

    except Exception as e:
        logger.error("Failed to get review statistics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get review statistics: {str(e)}",
        )


@router.get(
    "/metrics/real-time",
    summary="获取实时指标",
    description="获取审核系统的实时运行指标",
)
async def get_real_time_metrics(
    session: AsyncSession = Depends(get_session_dependency),
) -> Dict:
    """
    获取实时指标

    Args:
        session: 数据库会话

    Returns:
        实时指标数据

    Raises:
        HTTPException: 获取失败时抛出
    """
    try:
        service = HumanReviewService(session=session)
        metrics = await service.get_real_time_metrics()

        logger.info("Real-time metrics retrieved")
        return metrics

    except Exception as e:
        logger.error("Failed to get real-time metrics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get real-time metrics: {str(e)}",
        )


@router.get(
    "/trends/hourly", summary="获取小时趋势", description="获取按小时统计的审核趋势数据"
)
async def get_hourly_trends(
    hours: int = Query(24, ge=1, le=168, description="统计小时数"),
    session: AsyncSession = Depends(get_session_dependency),
) -> List[Dict]:
    """
    获取小时趋势

    Args:
        hours: 统计小时数
        session: 数据库会话

    Returns:
        小时趋势数据

    Raises:
        HTTPException: 获取失败时抛出
    """
    try:
        service = HumanReviewService()
        trends = await service.get_hourly_trends(hours, session)

        logger.info("Hourly trends retrieved", hours=hours)
        return trends

    except Exception as e:
        logger.error("Failed to get hourly trends", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get hourly trends: {str(e)}",
        )


@router.get(
    "/trends/daily", summary="获取日趋势", description="获取按日统计的审核趋势数据"
)
async def get_daily_trends(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    session: AsyncSession = Depends(get_session_dependency),
) -> List[Dict]:
    """
    获取日趋势

    Args:
        days: 统计天数
        session: 数据库会话

    Returns:
        日趋势数据

    Raises:
        HTTPException: 获取失败时抛出
    """
    try:
        service = HumanReviewService()
        trends = await service.get_daily_trends(days, session)

        logger.info("Daily trends retrieved", days=days)
        return trends

    except Exception as e:
        logger.error("Failed to get daily trends", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get daily trends: {str(e)}",
        )


@router.get(
    "/performance/reviewers",
    summary="获取审核员绩效排行",
    description="获取审核员的绩效排行榜",
)
async def get_reviewer_performance_ranking(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    session: AsyncSession = Depends(get_session_dependency),
) -> List[Dict]:
    """
    获取审核员绩效排行

    Args:
        days: 统计天数
        limit: 返回数量
        session: 数据库会话

    Returns:
        审核员绩效排行数据

    Raises:
        HTTPException: 获取失败时抛出
    """
    try:
        service = HumanReviewService()
        ranking = await service.get_reviewer_performance_ranking(days, limit, session)

        logger.info("Reviewer performance ranking retrieved", days=days, limit=limit)
        return ranking

    except Exception as e:
        logger.error("Failed to get reviewer performance ranking", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get reviewer performance ranking: {str(e)}",
        )


@router.get(
    "/workload/distribution",
    summary="获取工作负载分布",
    description="获取审核员工作负载分布情况",
)
async def get_workload_distribution(
    session: AsyncSession = Depends(get_session_dependency),
) -> Dict:
    """
    获取工作负载分布

    Args:
        session: 数据库会话

    Returns:
        工作负载分布数据

    Raises:
        HTTPException: 获取失败时抛出
    """
    try:
        service = HumanReviewService()
        distribution = await service.get_workload_distribution(session)

        logger.info("Workload distribution retrieved")
        return distribution

    except Exception as e:
        logger.error("Failed to get workload distribution", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workload distribution: {str(e)}",
        )


@router.get(
    "/quality/metrics", summary="获取质量指标", description="获取审核质量相关的指标"
)
async def get_quality_metrics(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    session: AsyncSession = Depends(get_session_dependency),
) -> Dict:
    """
    获取质量指标

    Args:
        days: 统计天数
        session: 数据库会话

    Returns:
        质量指标数据

    Raises:
        HTTPException: 获取失败时抛出
    """
    try:
        service = HumanReviewService()
        metrics = await service.get_quality_metrics(days, session)

        logger.info("Quality metrics retrieved", days=days)
        return metrics

    except Exception as e:
        logger.error("Failed to get quality metrics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get quality metrics: {str(e)}",
        )


@router.get("/alerts", summary="获取系统告警", description="获取审核系统的告警信息")
async def get_system_alerts(
    severity: Optional[str] = Query(None, description="告警级别过滤"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    session: AsyncSession = Depends(get_session_dependency),
) -> List[Dict]:
    """
    获取系统告警

    Args:
        severity: 告警级别过滤
        limit: 返回数量
        session: 数据库会话

    Returns:
        系统告警列表

    Raises:
        HTTPException: 获取失败时抛出
    """
    try:
        service = HumanReviewService()
        alerts = await service.get_system_alerts(severity, limit, session)

        logger.info("System alerts retrieved", severity=severity, limit=limit)
        return alerts

    except Exception as e:
        logger.error("Failed to get system alerts", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system alerts: {str(e)}",
        )
