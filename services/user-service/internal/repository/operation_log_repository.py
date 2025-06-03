"""
操作日志和审计日志存储库
用于记录用户操作、系统事件和关键流程的日志信息
"""
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

from sqlalchemy import create_engine, select, desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from internal.model.user import UserAuditLog as UserAuditLogModel
from internal.repository.exceptions import RepositoryError
from internal.repository.models import UserAuditLog, OperationLog, Base

# 日志记录器
logger = logging.getLogger(__name__)

class AuditLogRepository:
    """
    审计日志存储库
    负责记录用户操作的审计日志，用于安全审计和变更追踪
    """

    def __init__(self, db_path: str):
        """
        初始化审计日志存储库
        
        Args:
            db_path: 数据库路径
        """
        self.db_path = db_path
        self.engine = None
        self.async_session = None

    async def initialize(self):
        """初始化存储库"""
        # 创建异步数据库引擎
        sqlite_url = f"sqlite+aiosqlite:///{self.db_path}"
        self.engine = create_async_engine(sqlite_url, echo=False)
        
        # 创建会话工厂
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # 确保表存在
        async with self.engine.begin() as conn:
            try:
                # 创建审计日志表
                await conn.run_sync(Base.metadata.create_all, 
                    tables=[UserAuditLog.__table__, OperationLog.__table__])
                logger.info("审计日志表已创建或已存在")
            except SQLAlchemyError as e:
                logger.error(f"创建审计日志表失败: {str(e)}")
                raise RepositoryError(f"初始化审计日志存储库失败: {str(e)}")

    async def create_user_audit_log(self, audit_log: UserAuditLogModel) -> str:
        """
        创建用户审计日志
        
        Args:
            audit_log: 用户审计日志模型
            
        Returns:
            str: 创建的审计日志ID
        """
        if not self.async_session:
            await self.initialize()
            
        log_id = str(uuid.uuid4())
        
        try:
            async with self.async_session() as session:
                async with session.begin():
                    db_audit_log = UserAuditLog(
                        id=log_id,
                        user_id=str(audit_log.user_id),
                        action=audit_log.action,
                        action_time=audit_log.timestamp,
                        ip_address=audit_log.ip_address,
                        user_agent=audit_log.user_agent,
                        request_id=audit_log.metadata.get("request_id", ""),
                        changes=audit_log.changes,
                        details=audit_log.metadata.get("details", ""),
                        metadata=audit_log.metadata
                    )
                    session.add(db_audit_log)
                
            logger.info(f"创建用户审计日志成功: {log_id}, 用户ID: {audit_log.user_id}, 操作: {audit_log.action}")
            return log_id
        except SQLAlchemyError as e:
            logger.error(f"创建用户审计日志失败: {str(e)}")
            # 审计日志不应阻止主要业务流程，因此我们记录错误但不向上传播异常
            return log_id

    async def get_user_audit_logs(self, 
                              user_id: str, 
                              page: int = 1, 
                              limit: int = 20, 
                              action_filter: Optional[str] = None) -> List[UserAuditLogModel]:
        """
        获取用户审计日志列表
        
        Args:
            user_id: 用户ID
            page: 页码，从1开始
            limit: 每页记录数
            action_filter: 操作类型过滤条件
            
        Returns:
            List[UserAuditLogModel]: 用户审计日志列表
        """
        if not self.async_session:
            await self.initialize()
            
        try:
            async with self.async_session() as session:
                # 构建查询
                query = select(UserAuditLog).where(UserAuditLog.user_id == user_id)
                
                # 添加过滤条件
                if action_filter:
                    query = query.where(UserAuditLog.action == action_filter)
                
                # 排序和分页
                query = query.order_by(desc(UserAuditLog.action_time))
                query = query.offset((page - 1) * limit).limit(limit)
                
                # 执行查询
                result = await session.execute(query)
                db_logs = result.scalars().all()
                
                # 转换为模型
                audit_logs = []
                for db_log in db_logs:
                    metadata = db_log.metadata or {}
                    if db_log.request_id:
                        metadata["request_id"] = db_log.request_id
                    if db_log.details:
                        metadata["details"] = db_log.details
                    
                    audit_log = UserAuditLogModel(
                        log_id=db_log.id,
                        user_id=db_log.user_id,
                        action=db_log.action,
                        timestamp=db_log.action_time,
                        ip_address=db_log.ip_address,
                        user_agent=db_log.user_agent,
                        changes=db_log.changes or {},
                        metadata=metadata
                    )
                    audit_logs.append(audit_log)
                
                return audit_logs
        except SQLAlchemyError as e:
            logger.error(f"获取用户审计日志失败: {str(e)}")
            raise RepositoryError(f"获取用户审计日志失败: {str(e)}")

    async def get_audit_log_count(self, user_id: str, action_filter: Optional[str] = None) -> int:
        """
        获取用户审计日志数量
        
        Args:
            user_id: 用户ID
            action_filter: 操作类型过滤条件
            
        Returns:
            int: 日志数量
        """
        if not self.async_session:
            await self.initialize()
            
        try:
            async with self.async_session() as session:
                # 构建查询
                query = select(UserAuditLog).where(UserAuditLog.user_id == user_id)
                
                # 添加过滤条件
                if action_filter:
                    query = query.where(UserAuditLog.action == action_filter)
                
                # 执行查询
                result = await session.execute(query)
                return len(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"获取用户审计日志数量失败: {str(e)}")
            raise RepositoryError(f"获取用户审计日志数量失败: {str(e)}")

class OperationLogRepository:
    """
    操作日志存储库
    负责记录系统操作日志，用于性能监控、问题排查和API使用统计
    """

    def __init__(self, db_path: str):
        """
        初始化操作日志存储库
        
        Args:
            db_path: 数据库路径
        """
        self.db_path = db_path
        self.engine = None
        self.async_session = None

    async def initialize(self):
        """初始化存储库"""
        # 创建异步数据库引擎
        sqlite_url = f"sqlite+aiosqlite:///{self.db_path}"
        self.engine = create_async_engine(sqlite_url, echo=False)
        
        # 创建会话工厂
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # 确保表存在
        async with self.engine.begin() as conn:
            try:
                # 创建操作日志表
                await conn.run_sync(Base.metadata.create_all, 
                    tables=[OperationLog.__table__])
                logger.info("操作日志表已创建或已存在")
            except SQLAlchemyError as e:
                logger.error(f"创建操作日志表失败: {str(e)}")
                raise RepositoryError(f"初始化操作日志存储库失败: {str(e)}")

    async def log_operation(self, 
                      operation: str,
                      status: str,
                      start_time: datetime,
                      end_time: datetime,
                      user_id: Optional[str] = None,
                      request_id: Optional[str] = None,
                      ip_address: Optional[str] = None,
                      endpoint: Optional[str] = None,
                      method: Optional[str] = None,
                      request_data: Optional[Dict] = None,
                      response_data: Optional[Dict] = None,
                      error_message: Optional[str] = None,
                      stack_trace: Optional[str] = None,
                      metadata: Optional[Dict] = None) -> str:
        """
        记录操作日志
        
        Args:
            operation: 操作名称
            status: 操作状态（success, failure）
            start_time: 开始时间
            end_time: 结束时间
            user_id: 用户ID（可选）
            request_id: 请求ID（可选）
            ip_address: IP地址（可选）
            endpoint: 请求端点（可选）
            method: 请求方法（可选）
            request_data: 请求数据（可选）
            response_data: 响应数据（可选）
            error_message: 错误消息（可选）
            stack_trace: 堆栈跟踪（可选）
            metadata: 元数据（可选）
            
        Returns:
            str: 操作日志ID
        """
        if not self.async_session:
            await self.initialize()
            
        log_id = str(uuid.uuid4())
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        try:
            async with self.async_session() as session:
                async with session.begin():
                    # 清理请求和响应数据，避免存储敏感信息
                    if request_data:
                        # 如果有密码字段，替换为***
                        _request_data = request_data.copy()
                        if isinstance(_request_data, dict):
                            if "password" in _request_data:
                                _request_data["password"] = "***"
                            if "password_hash" in _request_data:
                                _request_data["password_hash"] = "***"
                            if "token" in _request_data:
                                _request_data["token"] = "***"
                    else:
                        _request_data = {}
                    
                    db_log = OperationLog(
                        id=log_id,
                        service="user-service",
                        operation=operation,
                        status=status,
                        start_time=start_time,
                        end_time=end_time,
                        duration_ms=duration_ms,
                        user_id=user_id,
                        request_id=request_id,
                        ip_address=ip_address,
                        endpoint=endpoint,
                        method=method,
                        request_data=_request_data,
                        response_data=response_data,
                        error_message=error_message,
                        stack_trace=stack_trace,
                        metadata=metadata or {}
                    )
                    session.add(db_log)
                
            logger.debug(f"记录操作日志成功: {log_id}, 操作: {operation}, 状态: {status}, 耗时: {duration_ms}ms")
            return log_id
        except SQLAlchemyError as e:
            logger.error(f"记录操作日志失败: {str(e)}")
            # 操作日志不应阻止主要业务流程，因此我们记录错误但不向上传播异常
            return log_id

    async def get_operation_logs(self, 
                           page: int = 1, 
                           limit: int = 50,
                           operation_filter: Optional[str] = None,
                           status_filter: Optional[str] = None,
                           user_id_filter: Optional[str] = None,
                           start_time_filter: Optional[datetime] = None,
                           end_time_filter: Optional[datetime] = None) -> List[Dict]:
        """
        获取操作日志列表
        
        Args:
            page: 页码，从1开始
            limit: 每页记录数
            operation_filter: 操作名称过滤条件
            status_filter: 状态过滤条件
            user_id_filter: 用户ID过滤条件
            start_time_filter: 开始时间过滤条件
            end_time_filter: 结束时间过滤条件
            
        Returns:
            List[Dict]: 操作日志列表
        """
        if not self.async_session:
            await self.initialize()
            
        try:
            async with self.async_session() as session:
                # 构建查询
                query = select(OperationLog)
                
                # 添加过滤条件
                if operation_filter:
                    query = query.where(OperationLog.operation == operation_filter)
                if status_filter:
                    query = query.where(OperationLog.status == status_filter)
                if user_id_filter:
                    query = query.where(OperationLog.user_id == user_id_filter)
                if start_time_filter:
                    query = query.where(OperationLog.start_time >= start_time_filter)
                if end_time_filter:
                    query = query.where(OperationLog.end_time <= end_time_filter)
                
                # 排序和分页
                query = query.order_by(desc(OperationLog.start_time))
                query = query.offset((page - 1) * limit).limit(limit)
                
                # 执行查询
                result = await session.execute(query)
                db_logs = result.scalars().all()
                
                # 转换为字典列表
                logs = []
                for db_log in db_logs:
                    log = {
                        "id": db_log.id,
                        "service": db_log.service,
                        "operation": db_log.operation,
                        "status": db_log.status,
                        "start_time": db_log.start_time.isoformat() if db_log.start_time else None,
                        "end_time": db_log.end_time.isoformat() if db_log.end_time else None,
                        "duration_ms": db_log.duration_ms,
                        "user_id": db_log.user_id,
                        "request_id": db_log.request_id,
                        "ip_address": db_log.ip_address,
                        "endpoint": db_log.endpoint,
                        "method": db_log.method,
                        "error_message": db_log.error_message,
                        "metadata": db_log.metadata or {}
                    }
                    logs.append(log)
                
                return logs
        except SQLAlchemyError as e:
            logger.error(f"获取操作日志失败: {str(e)}")
            raise RepositoryError(f"获取操作日志失败: {str(e)}")

    async def get_operation_stats(self, 
                           group_by: str,
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None) -> List[Dict]:
        """
        获取操作统计信息
        
        Args:
            group_by: 分组字段（operation, status, endpoint, method, user_id）
            start_time: 开始时间过滤条件
            end_time: 结束时间过滤条件
            
        Returns:
            List[Dict]: 统计信息
        """
        if not self.async_session:
            await self.initialize()
            
        # 验证分组字段
        valid_group_fields = ["operation", "status", "endpoint", "method", "user_id"]
        if group_by not in valid_group_fields:
            raise ValueError(f"分组字段必须是 {', '.join(valid_group_fields)} 之一")
            
        try:
            async with self.async_session() as session:
                # 构建SQL查询
                sql = f"""
                SELECT 
                    {group_by},
                    COUNT(*) as count,
                    AVG(duration_ms) as avg_duration,
                    MAX(duration_ms) as max_duration,
                    MIN(duration_ms) as min_duration,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count,
                    SUM(CASE WHEN status = 'failure' THEN 1 ELSE 0 END) as failure_count
                FROM 
                    operation_logs
                """
                
                # 添加时间过滤条件
                where_clauses = []
                params = {}
                
                if start_time:
                    where_clauses.append("start_time >= :start_time")
                    params["start_time"] = start_time
                
                if end_time:
                    where_clauses.append("end_time <= :end_time")
                    params["end_time"] = end_time
                
                if where_clauses:
                    sql += " WHERE " + " AND ".join(where_clauses)
                
                # 添加分组和排序
                sql += f" GROUP BY {group_by} ORDER BY count DESC"
                
                # 执行查询
                result = await session.execute(text(sql), params)
                rows = result.fetchall()
                
                # 转换为字典列表
                stats = []
                for row in rows:
                    row_dict = row._mapping
                    stat = {
                        group_by: row_dict[group_by],
                        "count": row_dict["count"],
                        "avg_duration": round(float(row_dict["avg_duration"]), 2) if row_dict["avg_duration"] else 0,
                        "max_duration": row_dict["max_duration"],
                        "min_duration": row_dict["min_duration"],
                        "success_count": row_dict["success_count"],
                        "failure_count": row_dict["failure_count"],
                        "success_rate": round(row_dict["success_count"] / row_dict["count"] * 100, 2) if row_dict["count"] > 0 else 0
                    }
                    stats.append(stat)
                
                return stats
        except SQLAlchemyError as e:
            logger.error(f"获取操作统计信息失败: {str(e)}")
            raise RepositoryError(f"获取操作统计信息失败: {str(e)}")