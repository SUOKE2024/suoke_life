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


class AuditRepository:
    """
    审计日志仓储
    负责记录和查询认证相关的审计日志
    """
    
    def __init__(self, session: AsyncSession):
        """
        初始化审计日志仓储
        
        Args:
            session: 数据库会话
        """
        self.session = session
        self.logger = logging.getLogger(__name__)
    
    async def add_audit_log(self, 
                            user_id: Optional[str], 
                            action: AuditActionEnum, 
                            ip_address: Optional[str] = None,
                            user_agent: Optional[str] = None,
                            details: Optional[Dict[str, Any]] = None,
                            success: bool = True) -> AuditLog:
        """
        添加审计日志
        
        Args:
            user_id: 用户ID (可为空，表示未认证用户)
            action: 操作类型
            ip_address: IP地址
            user_agent: 用户代理
            details: 附加详情
            success: 操作是否成功
            
        Returns:
            AuditLog: 创建的审计日志记录
            
        Raises:
            DatabaseError: 数据库操作错误
        """
        try:
            # 创建审计日志
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                ip_address=ip_address,
                user_agent=user_agent,
                details=details or {},
                success=success,
                created_at=datetime.now(UTC)
            )
            
            # 添加到数据库
            self.session.add(audit_log)
            await self.session.commit()
            
            return audit_log
            
        except Exception as e:
            await self.session.rollback()
            self.logger.exception(f"添加审计日志失败: {str(e)}")
            raise DatabaseError(f"添加审计日志失败: {str(e)}")
    
    async def add_login_attempt(self, 
                               username: str, 
                               success: bool,
                               ip_address: Optional[str] = None,
                               user_agent: Optional[str] = None) -> AuditLog:
        """
        记录登录尝试
        
        Args:
            username: 用户名
            success: 登录是否成功
            ip_address: IP地址
            user_agent: 用户代理
            
        Returns:
            AuditLog: 创建的审计日志记录
            
        Raises:
            DatabaseError: 数据库操作错误
        """
        details = {
            "username": username,
            "type": "login_attempt"
        }
        
        return await self.add_audit_log(
            user_id=None,  # 登录尝试时可能还不知道用户ID
            action=AuditActionEnum.LOGIN,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
            success=success
        )
    
    async def get_recent_failed_attempts(self, 
                                        username: str, 
                                        minutes: int = 30) -> List[AuditLog]:
        """
        获取最近的失败登录尝试
        
        Args:
            username: 用户名
            minutes: 查询过去多少分钟内的记录
            
        Returns:
            List[AuditLog]: 失败的登录尝试列表
            
        Raises:
            DatabaseError: 数据库操作错误
        """
        try:
            # 计算时间窗口
            time_window = datetime.now(UTC) - timedelta(minutes=minutes)
            
            # 查询在时间窗口内指定用户名的失败登录
            query = select(AuditLog).where(
                AuditLog.action == AuditActionEnum.LOGIN,
                AuditLog.success == False,
                AuditLog.created_at >= time_window,
                AuditLog.details.contains({"username": username})
            ).order_by(desc(AuditLog.created_at))
            
            result = await self.session.execute(query)
            return list(result.scalars().all())
            
        except Exception as e:
            self.logger.exception(f"获取失败登录尝试失败: {str(e)}")
            raise DatabaseError(f"获取失败登录尝试失败: {str(e)}")
    
    async def count_failed_attempts(self, 
                                   username: str, 
                                   minutes: int = 30) -> int:
        """
        统计最近的失败登录尝试次数
        
        Args:
            username: 用户名
            minutes: 查询过去多少分钟内的记录
            
        Returns:
            int: 失败尝试次数
            
        Raises:
            DatabaseError: 数据库操作错误
        """
        try:
            # 计算时间窗口
            time_window = datetime.now(UTC) - timedelta(minutes=minutes)
            
            # 查询在时间窗口内指定用户名的失败登录次数
            query = select(func.count()).select_from(AuditLog).where(
                AuditLog.action == AuditActionEnum.LOGIN,
                AuditLog.success == False,
                AuditLog.created_at >= time_window,
                AuditLog.details.contains({"username": username})
            )
            
            result = await self.session.execute(query)
            return result.scalar() or 0
            
        except Exception as e:
            self.logger.exception(f"统计失败登录尝试次数失败: {str(e)}")
            raise DatabaseError(f"统计失败登录尝试次数失败: {str(e)}")
    
    async def get_user_audit_logs(self, 
                                 user_id: str, 
                                 limit: int = 100,
                                 offset: int = 0) -> List[AuditLog]:
        """
        获取用户的审计日志
        
        Args:
            user_id: 用户ID
            limit: 返回记录数限制
            offset: 分页偏移量
            
        Returns:
            List[AuditLog]: 审计日志列表
            
        Raises:
            DatabaseError: 数据库操作错误
        """
        try:
            query = select(AuditLog).where(
                AuditLog.user_id == user_id
            ).order_by(desc(AuditLog.created_at)).limit(limit).offset(offset)
            
            result = await self.session.execute(query)
            return list(result.scalars().all())
            
        except Exception as e:
            self.logger.exception(f"获取用户审计日志失败: {str(e)}")
            raise DatabaseError(f"获取用户审计日志失败: {str(e)}") 