"""
审核员路由
Reviewers Routes

处理审核员的管理、查询、更新等操作
"""

from typing import List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_session_dependency
from ...core.models import (
    Reviewer,
    ReviewerCreate,
    ReviewerStatus,
    ReviewerUpdate,
)
from ...core.service import HumanReviewService

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post(
    "/",
    response_model=Reviewer,
    status_code=status.HTTP_201_CREATED,
    summary="创建审核员",
    description="创建新的审核员账户"
)
async def create_reviewer(
    reviewer_data: ReviewerCreate,
    session: AsyncSession = Depends(get_session_dependency)
) -> Reviewer:
    """
    创建审核员
    
    Args:
        reviewer_data: 审核员数据
        session: 数据库会话
        
    Returns:
        创建的审核员
        
    Raises:
        HTTPException: 创建失败时抛出
    """
    try:
        service = HumanReviewService()
        reviewer = await service.create_reviewer(reviewer_data, session)
        
        logger.info(
            "Reviewer created",
            reviewer_id=reviewer.reviewer_id,
            name=reviewer.name,
            specialties=reviewer.specialties
        )
        
        return reviewer
        
    except Exception as e:
        logger.error("Failed to create reviewer", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create reviewer: {str(e)}"
        )


@router.get(
    "/{reviewer_id}",
    response_model=Reviewer,
    summary="获取审核员信息",
    description="根据审核员ID获取详细信息"
)
async def get_reviewer(
    reviewer_id: str,
    session: AsyncSession = Depends(get_session_dependency)
) -> Reviewer:
    """
    获取审核员信息
    
    Args:
        reviewer_id: 审核员ID
        session: 数据库会话
        
    Returns:
        审核员详细信息
        
    Raises:
        HTTPException: 审核员不存在时抛出
    """
    try:
        service = HumanReviewService()
        reviewer = await service.get_reviewer(reviewer_id, session)
        
        if not reviewer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reviewer {reviewer_id} not found"
            )
        
        return reviewer
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get reviewer", reviewer_id=reviewer_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get reviewer: {str(e)}"
        )


@router.get(
    "/",
    response_model=List[Reviewer],
    summary="获取审核员列表",
    description="根据条件查询审核员列表"
)
async def list_reviewers(
    status_filter: Optional[ReviewerStatus] = Query(None, description="按状态过滤"),
    specialty: Optional[str] = Query(None, description="按专业领域过滤"),
    available_only: bool = Query(False, description="仅显示可用的审核员"),
    limit: int = Query(50, ge=1, le=100, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    session: AsyncSession = Depends(get_session_dependency)
) -> List[Reviewer]:
    """
    获取审核员列表
    
    Args:
        status_filter: 状态过滤
        specialty: 专业领域过滤
        available_only: 仅显示可用的审核员
        limit: 返回数量限制
        offset: 偏移量
        session: 数据库会话
        
    Returns:
        审核员列表
    """
    try:
        service = HumanReviewService()
        
        filters = {}
        if status_filter:
            filters["status"] = status_filter
        if specialty:
            filters["specialty"] = specialty
        if available_only:
            filters["is_available"] = True
        
        reviewers = await service.list_reviewers(
            filters=filters,
            limit=limit,
            offset=offset,
            session=session
        )
        
        return reviewers
        
    except Exception as e:
        logger.error("Failed to list reviewers", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list reviewers: {str(e)}"
        )


@router.put(
    "/{reviewer_id}",
    response_model=Reviewer,
    summary="更新审核员信息",
    description="更新审核员的基本信息和配置"
)
async def update_reviewer(
    reviewer_id: str,
    update_data: ReviewerUpdate,
    session: AsyncSession = Depends(get_session_dependency)
) -> Reviewer:
    """
    更新审核员信息
    
    Args:
        reviewer_id: 审核员ID
        update_data: 更新数据
        session: 数据库会话
        
    Returns:
        更新后的审核员信息
        
    Raises:
        HTTPException: 更新失败时抛出
    """
    try:
        service = HumanReviewService()
        reviewer = await service.update_reviewer(reviewer_id, update_data, session)
        
        if not reviewer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reviewer {reviewer_id} not found"
            )
        
        logger.info("Reviewer updated", reviewer_id=reviewer_id)
        return reviewer
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update reviewer", reviewer_id=reviewer_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update reviewer: {str(e)}"
        )


@router.post(
    "/{reviewer_id}/activate",
    response_model=Reviewer,
    summary="激活审核员",
    description="激活指定的审核员账户"
)
async def activate_reviewer(
    reviewer_id: str,
    session: AsyncSession = Depends(get_session_dependency)
) -> Reviewer:
    """
    激活审核员
    
    Args:
        reviewer_id: 审核员ID
        session: 数据库会话
        
    Returns:
        激活后的审核员信息
        
    Raises:
        HTTPException: 激活失败时抛出
    """
    try:
        service = HumanReviewService()
        reviewer = await service.activate_reviewer(reviewer_id, session)
        
        if not reviewer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reviewer {reviewer_id} not found"
            )
        
        logger.info("Reviewer activated", reviewer_id=reviewer_id)
        return reviewer
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to activate reviewer", reviewer_id=reviewer_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate reviewer: {str(e)}"
        )


@router.post(
    "/{reviewer_id}/deactivate",
    response_model=Reviewer,
    summary="停用审核员",
    description="停用指定的审核员账户"
)
async def deactivate_reviewer(
    reviewer_id: str,
    session: AsyncSession = Depends(get_session_dependency)
) -> Reviewer:
    """
    停用审核员
    
    Args:
        reviewer_id: 审核员ID
        session: 数据库会话
        
    Returns:
        停用后的审核员信息
        
    Raises:
        HTTPException: 停用失败时抛出
    """
    try:
        service = HumanReviewService()
        reviewer = await service.deactivate_reviewer(reviewer_id, session)
        
        if not reviewer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reviewer {reviewer_id} not found"
            )
        
        logger.info("Reviewer deactivated", reviewer_id=reviewer_id)
        return reviewer
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to deactivate reviewer", reviewer_id=reviewer_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate reviewer: {str(e)}"
        )


@router.get(
    "/{reviewer_id}/workload",
    summary="获取审核员工作负载",
    description="获取审核员当前的工作负载统计"
)
async def get_reviewer_workload(
    reviewer_id: str,
    session: AsyncSession = Depends(get_session_dependency)
) -> dict:
    """
    获取审核员工作负载
    
    Args:
        reviewer_id: 审核员ID
        session: 数据库会话
        
    Returns:
        工作负载统计信息
        
    Raises:
        HTTPException: 获取失败时抛出
    """
    try:
        service = HumanReviewService()
        workload = await service.get_reviewer_workload(reviewer_id, session)
        
        if workload is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reviewer {reviewer_id} not found"
            )
        
        return workload
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get reviewer workload", reviewer_id=reviewer_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get reviewer workload: {str(e)}"
        )


@router.get(
    "/{reviewer_id}/performance",
    summary="获取审核员绩效统计",
    description="获取审核员的绩效和质量统计"
)
async def get_reviewer_performance(
    reviewer_id: str,
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    session: AsyncSession = Depends(get_session_dependency)
) -> dict:
    """
    获取审核员绩效统计
    
    Args:
        reviewer_id: 审核员ID
        days: 统计天数
        session: 数据库会话
        
    Returns:
        绩效统计信息
        
    Raises:
        HTTPException: 获取失败时抛出
    """
    try:
        service = HumanReviewService()
        performance = await service.get_reviewer_performance(reviewer_id, days, session)
        
        if performance is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reviewer {reviewer_id} not found"
            )
        
        return performance
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get reviewer performance", reviewer_id=reviewer_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get reviewer performance: {str(e)}"
        )


@router.delete(
    "/{reviewer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除审核员",
    description="删除指定的审核员账户"
)
async def delete_reviewer(
    reviewer_id: str,
    session: AsyncSession = Depends(get_session_dependency)
) -> None:
    """
    删除审核员
    
    Args:
        reviewer_id: 审核员ID
        session: 数据库会话
        
    Raises:
        HTTPException: 删除失败时抛出
    """
    try:
        service = HumanReviewService()
        success = await service.delete_reviewer(reviewer_id, session)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reviewer {reviewer_id} not found"
            )
        
        logger.info("Reviewer deleted", reviewer_id=reviewer_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete reviewer", reviewer_id=reviewer_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete reviewer: {str(e)}"
        ) 