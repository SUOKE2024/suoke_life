#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
审计服务

负责记录和管理系统的审计日志。
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Optional, List

from internal.repository.audit_repository import AuditRepository
from internal.cache.redis_cache import get_redis_cache
from internal.config.settings import get_settings


class AuditService:
    """审计服务"""
    
    def __init__(self, audit_repository: AuditRepository):
        self.audit_repo = audit_repository
        self.cache = get_redis_cache()
        self.settings = get_settings()
    
    async def log_user_action(
        self,
        user_id: str,
        action: str,
        resource: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True
    ) -> bool:
        """记录用户操作日志"""
        try:
            audit_data = {
                'user_id': user_id,
                'action': action,
                'resource': resource,
                'details': details or {},
                'ip_address': ip_address,
                'user_agent': user_agent,
                'success': success,
                'timestamp': datetime.utcnow()
            }
            
            # 保存到数据库
            await self.audit_repo.create(audit_data)
            
            # 缓存最近的审计日志
            cache_key = f"audit_log:{user_id}:{int(datetime.utcnow().timestamp())}"
            await self.cache.set(
                cache_key,
                json.dumps(audit_data, default=str),
                expire=86400  # 24小时
            )
            
            return True
            
        except Exception as e:
            print(f"审计日志记录失败: {e}")
            return False
    
    async def get_user_audit_logs(
        self,
        user_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """获取用户审计日志"""
        logs = await self.audit_repo.get_user_logs(user_id, limit, offset)
        
        return [
            {
                'id': log.id,
                'action': log.action,
                'resource': log.resource,
                'details': log.details,
                'ip_address': log.ip_address,
                'success': log.success,
                'timestamp': log.timestamp.isoformat()
            }
            for log in logs
        ]
    
    async def get_security_events(
        self,
        start_time: datetime,
        end_time: datetime,
        event_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """获取安全事件"""
        security_actions = event_types or [
            'login_failed',
            'account_locked',
            'password_reset',
            'mfa_enabled',
            'mfa_disabled',
            'suspicious_activity'
        ]
        
        events = await self.audit_repo.get_security_events(
            start_time, end_time, security_actions
        )
        
        return [
            {
                'id': event.id,
                'user_id': event.user_id,
                'action': event.action,
                'details': event.details,
                'ip_address': event.ip_address,
                'timestamp': event.timestamp.isoformat()
            }
            for event in events
        ]


# 依赖注入函数
async def get_audit_service(
    audit_repo: AuditRepository = None
) -> AuditService:
    """获取审计服务实例"""
    if not audit_repo:
        from internal.repository.audit_repository import get_audit_repository
        audit_repo = await get_audit_repository()
    
    return AuditService(audit_repo) 