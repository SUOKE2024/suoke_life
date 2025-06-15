"""
管理员路由处理器

提供管理员功能接口。
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ...service.metrics_service import get_metrics_service, MetricsService
from ...repository.user_repository_new import UserRepository
from ...repository.audit_repository import AuditRepository

router = APIRouter()
logger = logging.getLogger(__name__)


class AdminStatsResponse(BaseModel):
    """管理员统计响应"""
    total_users: int
    active_users: int
    inactive_users: int
    total_logins_today: int
    failed_logins_today: int
    system_health: str


@router.get("/stats", response_model=AdminStatsResponse, summary="管理员统计")
async def get_admin_stats(
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """获取管理员统计信息"""
    try:
        stats = await metrics_service.get_service_stats()
        health_status = await metrics_service.get_health_status()
        
        return AdminStatsResponse(
            total_users=stats["users"]["total"],
            active_users=stats["users"]["active"],
            inactive_users=stats["users"]["inactive"],
            total_logins_today=stats["activity"].get("total_activities", 0),
            failed_logins_today=stats["activity"].get("failed_activities", 0),
            system_health=health_status["status"]
        )
    except Exception as e:
        logger.error(f"获取管理员统计失败: {e}")
        raise HTTPException(
            status_code=500,
            detail="获取统计信息失败"
        )


@router.get("/users", summary="用户列表")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None)
):
    """获取用户列表（管理员功能）"""
    try:
        user_repo = UserRepository()
        
        users = await user_repo.get_users(
            skip=skip,
            limit=limit,
            search=search,
            is_active=is_active
        )
        
        total = await user_repo.count_users(
            search=search,
            is_active=is_active
        )
        
        # 转换为安全的响应格式
        user_list = []
        for user in users:
            user_list.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active,
                "status": user.status,
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None
            })
        
        return {
            "users": user_list,
            "total": total,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"获取用户列表失败: {e}")
        raise HTTPException(
            status_code=500,
            detail="获取用户列表失败"
        )


@router.get("/audit-logs", summary="审计日志")
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    success: Optional[bool] = Query(None)
):
    """获取审计日志（管理员功能）"""
    try:
        audit_repo = AuditRepository()
        
        logs = await audit_repo.get_logs(
            skip=skip,
            limit=limit,
            user_id=user_id,
            success=success
        )
        
        total = await audit_repo.count_logs(
            user_id=user_id,
            success=success
        )
        
        # 转换为响应格式
        log_list = []
        for log in logs:
            log_list.append({
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "success": log.success,
                "ip_address": log.ip_address,
                "timestamp": log.timestamp.isoformat(),
                "details": log.details
            })
        
        return {
            "logs": log_list,
            "total": total,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"获取审计日志失败: {e}")
        raise HTTPException(
            status_code=500,
            detail="获取审计日志失败"
        )


@router.post("/users/{user_id}/activate", summary="激活用户")
async def activate_user(user_id: str):
    """激活用户（管理员功能）"""
    try:
        user_repo = UserRepository()
        success = await user_repo.activate_user(user_id)
        
        if success:
            return {"message": "用户激活成功"}
        else:
            raise HTTPException(
                status_code=404,
                detail="用户不存在"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"激活用户失败: {e}")
        raise HTTPException(
            status_code=500,
            detail="激活用户失败"
        )


@router.post("/users/{user_id}/deactivate", summary="停用用户")
async def deactivate_user(user_id: str):
    """停用用户（管理员功能）"""
    try:
        user_repo = UserRepository()
        success = await user_repo.deactivate_user(user_id)
        
        if success:
            return {"message": "用户停用成功"}
        else:
            raise HTTPException(
                status_code=404,
                detail="用户不存在"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"停用用户失败: {e}")
        raise HTTPException(
            status_code=500,
            detail="停用用户失败"
        )


@router.get("/system/health", summary="系统健康状态")
async def system_health(
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """获取系统健康状态（管理员功能）"""
    try:
        health_status = await metrics_service.get_health_status()
        return health_status
    except Exception as e:
        logger.error(f"获取系统健康状态失败: {e}")
        raise HTTPException(
            status_code=500,
            detail="获取系统健康状态失败"
        ) 