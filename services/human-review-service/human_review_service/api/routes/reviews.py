"""
审核任务路由
Review Tasks Routes

处理审核任务的创建、查询、更新等操作
"""

from typing import List, Optional
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_session_dependency
from ...core.models import (
    ReviewDecision,
    ReviewPriority,
    ReviewStatus,
    ReviewTask,
    ReviewTaskCreate,
    ReviewTaskUpdate,
    ReviewType,
)
from ...core.service import HumanReviewService

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post(
    "/",
    response_model=ReviewTask,
    status_code=status.HTTP_201_CREATED,
    summary="提交审核请求",
    description="创建新的审核任务",
)
async def submit_review(
    review_data: ReviewTaskCreate,
    session: AsyncSession = Depends(get_session_dependency),
) -> ReviewTask:
    """
    提交审核请求

    Args:
        review_data: 审核任务数据
        session: 数据库会话

    Returns:
        创建的审核任务

    Raises:
        HTTPException: 创建失败时抛出
    """
    try:
        service = HumanReviewService(session=session)
        task = await service.submit_review(review_data)

        logger.info(
            "Review task submitted",
            task_id=task.task_id,
            review_type=task.review_type,
            priority=task.priority,
            user_id=task.user_id,
        )

        return task

    except Exception as e:
        logger.error("Failed to submit review", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit review: {str(e)}",
        )


@router.get(
    "/{task_id}",
    response_model=ReviewTask,
    summary="获取审核任务",
    description="根据任务ID获取审核任务详情",
)
async def get_review(
    task_id: str, session: AsyncSession = Depends(get_session_dependency)
) -> ReviewTask:
    """
    获取审核任务

    Args:
        task_id: 任务ID
        session: 数据库会话

    Returns:
        审核任务详情

    Raises:
        HTTPException: 任务不存在时抛出
    """
    try:
        service = HumanReviewService(session=session)
        task = await service.get_review_task(task_id)

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Review task {task_id} not found",
            )

        return task

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get review task", task_id=task_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get review task: {str(e)}",
        )


@router.get(
    "/",
    response_model=List[ReviewTask],
    summary="获取审核任务列表",
    description="根据条件查询审核任务列表",
)
async def list_reviews(
    status_filter: Optional[ReviewStatus] = Query(None, description="按状态过滤"),
    priority_filter: Optional[ReviewPriority] = Query(None, description="按优先级过滤"),
    type_filter: Optional[ReviewType] = Query(None, description="按类型过滤"),
    assigned_to: Optional[str] = Query(None, description="按审核员过滤"),
    user_id: Optional[str] = Query(None, description="按用户ID过滤"),
    limit: int = Query(50, ge=1, le=100, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    session: AsyncSession = Depends(get_session_dependency),
) -> List[ReviewTask]:
    """
    获取审核任务列表

    Args:
        status_filter: 状态过滤
        priority_filter: 优先级过滤
        type_filter: 类型过滤
        assigned_to: 审核员过滤
        user_id: 用户ID过滤
        limit: 返回数量限制
        offset: 偏移量
        session: 数据库会话

    Returns:
        审核任务列表
    """
    try:
        service = HumanReviewService(session=session)

        filters = {}
        if status_filter:
            filters["status"] = status_filter
        if priority_filter:
            filters["priority"] = priority_filter
        if type_filter:
            filters["review_type"] = type_filter
        if assigned_to:
            filters["assigned_to"] = assigned_to
        if user_id:
            filters["user_id"] = user_id

        tasks = await service.list_review_tasks(
            filters=filters, limit=limit, offset=offset
        )

        return tasks

    except Exception as e:
        logger.error("Failed to list review tasks", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list review tasks: {str(e)}",
        )


@router.put(
    "/{task_id}",
    response_model=ReviewTask,
    summary="更新审核任务",
    description="更新审核任务信息",
)
async def update_review(
    task_id: str,
    update_data: ReviewTaskUpdate,
    session: AsyncSession = Depends(get_session_dependency),
) -> ReviewTask:
    """
    更新审核任务

    Args:
        task_id: 任务ID
        update_data: 更新数据
        session: 数据库会话

    Returns:
        更新后的审核任务

    Raises:
        HTTPException: 更新失败时抛出
    """
    try:
        service = HumanReviewService(session=session)
        task = await service.update_review_task(task_id, update_data)

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Review task {task_id} not found",
            )

        logger.info("Review task updated", task_id=task_id)
        return task

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update review task", task_id=task_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update review task: {str(e)}",
        )


@router.post(
    "/{task_id}/assign",
    response_model=ReviewTask,
    summary="分配审核任务",
    description="将审核任务分配给指定审核员",
)
async def assign_review(
    task_id: str,
    reviewer_id: str,
    session: AsyncSession = Depends(get_session_dependency),
) -> ReviewTask:
    """
    分配审核任务

    Args:
        task_id: 任务ID
        reviewer_id: 审核员ID
        session: 数据库会话

    Returns:
        分配后的审核任务

    Raises:
        HTTPException: 分配失败时抛出
    """
    try:
        service = HumanReviewService(session=session)
        task = await service.assign_reviewer(task_id, reviewer_id)

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Review task {task_id} not found",
            )

        logger.info("Review task assigned", task_id=task_id, reviewer_id=reviewer_id)

        return task

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to assign review task",
            task_id=task_id,
            reviewer_id=reviewer_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign review task: {str(e)}",
        )


@router.post(
    "/{task_id}/complete",
    response_model=ReviewTask,
    summary="完成审核",
    description="提交审核决策并完成审核任务",
)
async def complete_review(
    task_id: str,
    decision: ReviewDecision,
    session: AsyncSession = Depends(get_session_dependency),
) -> ReviewTask:
    """
    完成审核

    Args:
        task_id: 任务ID
        decision: 审核决策
        session: 数据库会话

    Returns:
        完成的审核任务

    Raises:
        HTTPException: 完成失败时抛出
    """
    try:
        service = HumanReviewService(session=session)

        # 首先获取任务以获得审核员ID
        existing_task = await service.get_review_task(task_id)
        if not existing_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Review task {task_id} not found",
            )

        if not existing_task.assigned_to:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Review task {task_id} is not assigned to any reviewer",
            )

        task = await service.complete_review(
            task_id, existing_task.assigned_to, decision
        )

        logger.info(
            "Review task completed",
            task_id=task_id,
            decision=decision.decision,
            reviewer_notes=decision.reviewer_notes,
        )

        return task

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to complete review task", task_id=task_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete review task: {str(e)}",
        )


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="取消审核任务",
    description="取消指定的审核任务",
)
async def cancel_review(
    task_id: str, session: AsyncSession = Depends(get_session_dependency)
) -> None:
    """
    取消审核任务

    Args:
        task_id: 任务ID
        session: 数据库会话

    Raises:
        HTTPException: 取消失败时抛出
    """
    try:
        service = HumanReviewService(session=session)
        success = await service.cancel_review_task(task_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Review task {task_id} not found",
            )

        logger.info("Review task cancelled", task_id=task_id)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to cancel review task", task_id=task_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel review task: {str(e)}",
        )
