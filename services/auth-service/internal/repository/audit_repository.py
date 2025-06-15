#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
审计日志仓储实现
处理认证服务的审计日志记录和检索
"""
import logging
import json
from datetime import datetime, timedelta, UTC
from typing import Dict, List, Optional, Any

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from internal.model.user import AuditLog, AuditActionEnum
from internal.model.errors import DatabaseError

from .base import BaseRepository
from internal.db.models import AuditLogModel


class AuditRepository(BaseRepository[AuditLogModel]):
    """审计日志仓储类"""
    
    def __init__(self):
        super().__init__(AuditLogModel)
    
    async def create_log(
        self,
        user_id: Optional[str],
        action: AuditActionEnum,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True
    ) -> AuditLogModel:
        """创建审计日志"""
        audit_log = AuditLogModel(
            user_id=user_id,
            action=action.value,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            timestamp=datetime.utcnow()
        )
        return await self.create(audit_log)
    
    async def get_user_logs(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
        action: Optional[AuditActionEnum] = None,
        resource_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[AuditLogModel]:
        """获取用户审计日志"""
        async with await self.get_session() as session:
            query = select(AuditLogModel).where(AuditLogModel.user_id == user_id)
            
            # 添加动作过滤
            if action:
                query = query.where(AuditLogModel.action == action.value)
            
            # 添加资源类型过滤
            if resource_type:
                query = query.where(AuditLogModel.resource_type == resource_type)
            
            # 添加日期范围过滤
            if start_date:
                query = query.where(AuditLogModel.timestamp >= start_date)
            if end_date:
                query = query.where(AuditLogModel.timestamp <= end_date)
            
            # 排序和分页
            query = query.order_by(desc(AuditLogModel.timestamp)).offset(skip).limit(limit)
            
            result = await session.execute(query)
            return list(result.scalars().all())
    
    async def get_logs(
        self,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[str] = None,
        action: Optional[AuditActionEnum] = None,
        resource_type: Optional[str] = None,
        success: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        ip_address: Optional[str] = None
    ) -> List[AuditLogModel]:
        """获取审计日志列表"""
        async with await self.get_session() as session:
            query = select(AuditLogModel)
            
            # 添加用户过滤
            if user_id:
                query = query.where(AuditLogModel.user_id == user_id)
            
            # 添加动作过滤
            if action:
                query = query.where(AuditLogModel.action == action.value)
            
            # 添加资源类型过滤
            if resource_type:
                query = query.where(AuditLogModel.resource_type == resource_type)
            
            # 添加成功状态过滤
            if success is not None:
                query = query.where(AuditLogModel.success == success)
            
            # 添加日期范围过滤
            if start_date:
                query = query.where(AuditLogModel.timestamp >= start_date)
            if end_date:
                query = query.where(AuditLogModel.timestamp <= end_date)
            
            # 添加IP地址过滤
            if ip_address:
                query = query.where(AuditLogModel.ip_address == ip_address)
            
            # 排序和分页
            query = query.order_by(desc(AuditLogModel.timestamp)).offset(skip).limit(limit)
            
            result = await session.execute(query)
            return list(result.scalars().all())
    
    async def count_logs(
        self,
        user_id: Optional[str] = None,
        action: Optional[AuditActionEnum] = None,
        resource_type: Optional[str] = None,
        success: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        ip_address: Optional[str] = None
    ) -> int:
        """统计审计日志数量"""
        async with await self.get_session() as session:
            query = select(func.count(AuditLogModel.id))
            
            # 添加用户过滤
            if user_id:
                query = query.where(AuditLogModel.user_id == user_id)
            
            # 添加动作过滤
            if action:
                query = query.where(AuditLogModel.action == action.value)
            
            # 添加资源类型过滤
            if resource_type:
                query = query.where(AuditLogModel.resource_type == resource_type)
            
            # 添加成功状态过滤
            if success is not None:
                query = query.where(AuditLogModel.success == success)
            
            # 添加日期范围过滤
            if start_date:
                query = query.where(AuditLogModel.timestamp >= start_date)
            if end_date:
                query = query.where(AuditLogModel.timestamp <= end_date)
            
            # 添加IP地址过滤
            if ip_address:
                query = query.where(AuditLogModel.ip_address == ip_address)
            
            result = await session.execute(query)
            return result.scalar()
    
    async def get_login_attempts(
        self,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        hours: int = 24,
        success: Optional[bool] = None
    ) -> List[AuditLogModel]:
        """获取登录尝试记录"""
        async with await self.get_session() as session:
            start_time = datetime.utcnow() - timedelta(hours=hours)
            
            query = select(AuditLogModel).where(
                and_(
                    AuditLogModel.action == AuditActionEnum.LOGIN.value,
                    AuditLogModel.timestamp >= start_time
                )
            )
            
            if user_id:
                query = query.where(AuditLogModel.user_id == user_id)
            
            if ip_address:
                query = query.where(AuditLogModel.ip_address == ip_address)
            
            if success is not None:
                query = query.where(AuditLogModel.success == success)
            
            query = query.order_by(desc(AuditLogModel.timestamp))
            
            result = await session.execute(query)
            return list(result.scalars().all())
    
    async def get_failed_login_count(
        self,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        hours: int = 1
    ) -> int:
        """获取失败登录次数"""
        async with await self.get_session() as session:
            start_time = datetime.utcnow() - timedelta(hours=hours)
            
            query = select(func.count(AuditLogModel.id)).where(
                and_(
                    AuditLogModel.action == AuditActionEnum.LOGIN.value,
                    AuditLogModel.success == False,
                    AuditLogModel.timestamp >= start_time
                )
            )
            
            if user_id:
                query = query.where(AuditLogModel.user_id == user_id)
            
            if ip_address:
                query = query.where(AuditLogModel.ip_address == ip_address)
            
            result = await session.execute(query)
            return result.scalar()
    
    async def get_activity_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """获取活动统计"""
        async with await self.get_session() as session:
            # 默认查询最近30天
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            # 总活动数
            total_result = await session.execute(
                select(func.count(AuditLogModel.id)).where(
                    and_(
                        AuditLogModel.timestamp >= start_date,
                        AuditLogModel.timestamp <= end_date
                    )
                )
            )
            total_activities = total_result.scalar()
            
            # 成功活动数
            success_result = await session.execute(
                select(func.count(AuditLogModel.id)).where(
                    and_(
                        AuditLogModel.timestamp >= start_date,
                        AuditLogModel.timestamp <= end_date,
                        AuditLogModel.success == True
                    )
                )
            )
            successful_activities = success_result.scalar()
            
            # 失败活动数
            failed_activities = total_activities - successful_activities
            
            # 唯一用户数
            unique_users_result = await session.execute(
                select(func.count(func.distinct(AuditLogModel.user_id))).where(
                    and_(
                        AuditLogModel.timestamp >= start_date,
                        AuditLogModel.timestamp <= end_date,
                        AuditLogModel.user_id.is_not(None)
                    )
                )
            )
            unique_users = unique_users_result.scalar()
            
            # 按动作分组统计
            action_stats_result = await session.execute(
                select(
                    AuditLogModel.action,
                    func.count(AuditLogModel.id).label('count')
                ).where(
                    and_(
                        AuditLogModel.timestamp >= start_date,
                        AuditLogModel.timestamp <= end_date
                    )
                ).group_by(AuditLogModel.action)
            )
            action_stats = {row.action: row.count for row in action_stats_result.fetchall()}
            
            return {
                "total_activities": total_activities,
                "successful_activities": successful_activities,
                "failed_activities": failed_activities,
                "unique_users": unique_users,
                "success_rate": successful_activities / total_activities if total_activities > 0 else 0,
                "action_stats": action_stats,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }
    
    async def cleanup_old_logs(self, days: int = 90) -> int:
        """清理旧的审计日志"""
        async with await self.get_session() as session:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            result = await session.execute(
                select(AuditLogModel).where(AuditLogModel.timestamp < cutoff_date)
            )
            logs_to_delete = list(result.scalars().all())
            
            count = 0
            for log in logs_to_delete:
                await session.delete(log)
                count += 1
            
            if count > 0:
                await session.commit()
            
            return count 