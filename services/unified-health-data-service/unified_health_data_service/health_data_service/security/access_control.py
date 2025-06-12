"""
安全访问控制模块
实现MCP级别的权限管理和运行时隔离
基于区块链的权限验证和审计追踪
"""

import asyncio
import logging
import hashlib
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from enum import Enum
from dataclasses import dataclass, asdict
import uuid

logger = logging.getLogger(__name__)

class PermissionLevel(Enum):
    """权限级别"""
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    ADMIN = "admin"
    SYSTEM = "system"

class DataCategory(Enum):
    """数据类别"""
    VITAL_SIGNS = "vital_signs"
    DIAGNOSTIC = "diagnostic"
    TCM_DATA = "tcm_data"
    PERSONAL_INFO = "personal_info"
    DEVICE_DATA = "device_data"
    ANALYSIS_RESULTS = "analysis_results"

class AgentType(Enum):
    """智能体类型"""
    XIAOAI = "xiaoai"  # 小艾 - 中医诊断
    XIAOKE = "xiaoke"  # 小克 - 服务匹配
    LAOKE = "laoke"    # 老克 - 知识支持
    SOER = "soer"      # 索儿 - 生活方式

@dataclass
class AccessRequest:
    """访问请求"""
    agent_id: str
    agent_type: AgentType
    user_id: str
    data_categories: List[DataCategory]
    permission_level: PermissionLevel
    tool_name: str
    request_context: Dict[str, Any]
    timestamp: datetime
    request_id: str = None
    
    def __post_init__(self):
        if self.request_id is None:
            self.request_id = str(uuid.uuid4())

@dataclass
class AccessResult:
    """访问结果"""
    request_id: str
    granted: bool
    reason: str
    allowed_data_categories: List[DataCategory]
    restrictions: Dict[str, Any]
    audit_log_id: str
    timestamp: datetime

@dataclass
class AuditLog:
    """审计日志"""
    log_id: str
    agent_id: str
    agent_type: AgentType
    user_id: str
    action: str
    data_accessed: List[str]
    permission_level: PermissionLevel
    result: str
    timestamp: datetime
    context: Dict[str, Any]
    
    def to_blockchain_record(self) -> Dict[str, Any]:
        """转换为区块链记录格式"""
        return {
            "log_id": self.log_id,
            "agent_id": self.agent_id,
            "user_id": self.user_id,
            "action": self.action,
            "timestamp": self.timestamp.isoformat(),
            "hash": self._generate_hash()
        }
        
    def _generate_hash(self) -> str:
        """生成记录哈希"""
        data = f"{self.log_id}{self.agent_id}{self.user_id}{self.action}{self.timestamp.isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()

class AgentPermissionMatrix:
    """智能体权限矩阵"""
    
    def __init__(self):
        # 定义每个智能体的默认权限
        self.default_permissions = {
            AgentType.XIAOAI: {
                "data_categories": [
                    DataCategory.VITAL_SIGNS,
                    DataCategory.DIAGNOSTIC,
                    DataCategory.TCM_DATA,
                    DataCategory.DEVICE_DATA
                ],
                "permission_level": PermissionLevel.READ_WRITE,
                "allowed_tools": [
                    "tcm_diagnosis",
                    "symptom_analysis",
                    "constitution_assessment",
                    "health_data_read"
                ]
            },
            AgentType.XIAOKE: {
                "data_categories": [
                    DataCategory.ANALYSIS_RESULTS,
                    DataCategory.PERSONAL_INFO
                ],
                "permission_level": PermissionLevel.READ_ONLY,
                "allowed_tools": [
                    "service_matching",
                    "recommendation_engine",
                    "user_profile_read"
                ]
            },
            AgentType.LAOKE: {
                "data_categories": [
                    DataCategory.TCM_DATA,
                    DataCategory.ANALYSIS_RESULTS
                ],
                "permission_level": PermissionLevel.READ_ONLY,
                "allowed_tools": [
                    "knowledge_query",
                    "education_content",
                    "research_data_read"
                ]
            },
            AgentType.SOER: {
                "data_categories": [
                    DataCategory.VITAL_SIGNS,
                    DataCategory.DEVICE_DATA,
                    DataCategory.PERSONAL_INFO
                ],
                "permission_level": PermissionLevel.READ_ONLY,
                "allowed_tools": [
                    "lifestyle_analysis",
                    "environment_monitoring",
                    "behavior_tracking"
                ]
            }
        }
        
    def get_agent_permissions(self, agent_type: AgentType) -> Dict[str, Any]:
        """获取智能体权限"""
        return self.default_permissions.get(agent_type, {})
        
    def check_tool_permission(self, agent_type: AgentType, tool_name: str) -> bool:
        """检查工具权限"""
        permissions = self.get_agent_permissions(agent_type)
        allowed_tools = permissions.get("allowed_tools", [])
        return tool_name in allowed_tools
        
    def check_data_permission(self, agent_type: AgentType, data_categories: List[DataCategory]) -> bool:
        """检查数据权限"""
        permissions = self.get_agent_permissions(agent_type)
        allowed_categories = permissions.get("data_categories", [])
        return all(category in allowed_categories for category in data_categories)

class RuntimeIsolator:
    """运行时隔离器"""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.resource_limits = {
            "max_memory_mb": 512,
            "max_cpu_percent": 25,
            "max_execution_time": 30,
            "max_data_size_mb": 100
        }
        
    async def create_isolated_session(self, agent_id: str, request: AccessRequest) -> str:
        """创建隔离会话"""
        session_id = str(uuid.uuid4())
        
        session_info = {
            "session_id": session_id,
            "agent_id": agent_id,
            "agent_type": request.agent_type,
            "user_id": request.user_id,
            "start_time": datetime.utcnow(),
            "resource_usage": {
                "memory_mb": 0,
                "cpu_percent": 0,
                "data_size_mb": 0
            },
            "allowed_operations": self._get_allowed_operations(request),
            "status": "active"
        }
        
        self.active_sessions[session_id] = session_info
        logger.info(f"创建隔离会话 {session_id} for agent {agent_id}")
        
        return session_id
        
    async def execute_in_sandbox(self, session_id: str, operation: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
        """在沙箱中执行操作"""
        if session_id not in self.active_sessions:
            raise ValueError(f"会话 {session_id} 不存在")
            
        session = self.active_sessions[session_id]
        
        try:
            # 检查资源限制
            if not self._check_resource_limits(session):
                raise RuntimeError("资源限制超出")
                
            # 检查操作权限
            if not self._check_operation_permission(session, operation):
                raise PermissionError("操作权限不足")
                
            # 执行操作（模拟）
            result = await self._execute_operation(operation, timeout)
            
            # 更新资源使用情况
            self._update_resource_usage(session, result)
            
            return {
                "success": True,
                "result": result,
                "session_id": session_id,
                "resource_usage": session["resource_usage"]
            }
            
        except Exception as e:
            logger.error(f"沙箱执行失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }
            
    async def cleanup_session(self, session_id: str) -> None:
        """清理会话"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session["status"] = "terminated"
            session["end_time"] = datetime.utcnow()
            
            # 记录会话统计
            duration = session["end_time"] - session["start_time"]
            logger.info(f"会话 {session_id} 已终止，持续时间: {duration.total_seconds()}秒")
            
            del self.active_sessions[session_id]
            
    def _get_allowed_operations(self, request: AccessRequest) -> List[str]:
        """获取允许的操作"""
        # 基于智能体类型和权限级别确定允许的操作
        base_operations = ["read_data", "analyze_data"]
        
        if request.permission_level in [PermissionLevel.READ_WRITE, PermissionLevel.ADMIN]:
            base_operations.extend(["write_data", "update_data"])
            
        return base_operations
        
    def _check_resource_limits(self, session: Dict[str, Any]) -> bool:
        """检查资源限制"""
        usage = session["resource_usage"]
        
        if usage["memory_mb"] > self.resource_limits["max_memory_mb"]:
            return False
        if usage["cpu_percent"] > self.resource_limits["max_cpu_percent"]:
            return False
        if usage["data_size_mb"] > self.resource_limits["max_data_size_mb"]:
            return False
            
        return True
        
    def _check_operation_permission(self, session: Dict[str, Any], operation: Dict[str, Any]) -> bool:
        """检查操作权限"""
        operation_type = operation.get("type", "unknown")
        allowed_operations = session.get("allowed_operations", [])
        return operation_type in allowed_operations
        
    async def _execute_operation(self, operation: Dict[str, Any], timeout: int) -> Dict[str, Any]:
        """执行操作（模拟）"""
        # 模拟操作执行
        await asyncio.sleep(0.1)  # 模拟处理时间
        
        return {
            "operation_type": operation.get("type", "unknown"),
            "status": "completed",
            "data_processed": operation.get("data_size", 0),
            "execution_time": 0.1
        }
        
    def _update_resource_usage(self, session: Dict[str, Any], result: Dict[str, Any]) -> None:
        """更新资源使用情况"""
        usage = session["resource_usage"]
        
        # 模拟资源使用更新
        usage["memory_mb"]+=result.get("data_processed", 0) * 0.1
        usage["cpu_percent"]+=result.get("execution_time", 0) * 10
        usage["data_size_mb"]+=result.get("data_processed", 0)

class SecureHealthProxy:
    """安全健康数据代理"""
    
    def __init__(self):
        self.permission_matrix = AgentPermissionMatrix()
        self.runtime_isolator = RuntimeIsolator()
        self.audit_logs: List[AuditLog] = []
        
    async def secure_data_access(self, request: AccessRequest) -> AccessResult:
        """安全数据访问"""
        try:
            # 1. 工具级授权检查
            if not self.permission_matrix.check_tool_permission(request.agent_type, request.tool_name):
                return AccessResult(
                    request_id=request.request_id,
                    granted=False,
                    reason=f"智能体 {request.agent_type.value} 无权使用工具 {request.tool_name}",
                    allowed_data_categories=[],
                    restrictions={},
                    audit_log_id="",
                    timestamp=datetime.utcnow()
                )
                
            # 2. 数据级权限验证
            if not self.permission_matrix.check_data_permission(request.agent_type, request.data_categories):
                return AccessResult(
                    request_id=request.request_id,
                    granted=False,
                    reason="请求的数据类型超出授权范围",
                    allowed_data_categories=[],
                    restrictions={},
                    audit_log_id="",
                    timestamp=datetime.utcnow()
                )
                
            # 3. 创建隔离会话
            session_id = await self.runtime_isolator.create_isolated_session(request.agent_id, request)
            
            # 4. 记录审计日志
            audit_log = await self._create_audit_log(request, "ACCESS_GRANTED", session_id)
            
            # 5. 返回访问结果
            agent_permissions = self.permission_matrix.get_agent_permissions(request.agent_type)
            
            return AccessResult(
                request_id=request.request_id,
                granted=True,
                reason="访问权限验证通过",
                allowed_data_categories=agent_permissions.get("data_categories", []),
                restrictions={
                    "session_id": session_id,
                    "permission_level": agent_permissions.get("permission_level", PermissionLevel.READ_ONLY).value,
                    "allowed_tools": agent_permissions.get("allowed_tools", [])
                },
                audit_log_id=audit_log.log_id,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"安全数据访问失败: {e}")
            audit_log = await self._create_audit_log(request, "ACCESS_DENIED", str(e))
            
            return AccessResult(
                request_id=request.request_id,
                granted=False,
                reason=f"访问控制错误: {str(e)}",
                allowed_data_categories=[],
                restrictions={},
                audit_log_id=audit_log.log_id,
                timestamp=datetime.utcnow()
            )
            
    async def execute_secure_operation(self, session_id: str, operation: Dict[str, Any]) -> Dict[str, Any]:
        """执行安全操作"""
        try:
            # 在隔离环境中执行操作
            result = await self.runtime_isolator.execute_in_sandbox(session_id, operation)
            
            # 记录操作审计
            if session_id in self.runtime_isolator.active_sessions:
                session = self.runtime_isolator.active_sessions[session_id]
                await self._create_audit_log_for_operation(session, operation, result)
                
            return result
            
        except Exception as e:
            logger.error(f"安全操作执行失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }
            
    async def cleanup_session(self, session_id: str) -> None:
        """清理会话"""
        await self.runtime_isolator.cleanup_session(session_id)
        
    async def _create_audit_log(self, request: AccessRequest, action: str, context: str) -> AuditLog:
        """创建审计日志"""
        audit_log = AuditLog(
            log_id=str(uuid.uuid4()),
            agent_id=request.agent_id,
            agent_type=request.agent_type,
            user_id=request.user_id,
            action=action,
            data_accessed=[cat.value for cat in request.data_categories],
            permission_level=request.permission_level,
            result=context,
            timestamp=datetime.utcnow(),
            context=asdict(request)
        )
        
        self.audit_logs.append(audit_log)
        logger.info(f"创建审计日志: {audit_log.log_id}")
        
        return audit_log
        
    async def _create_audit_log_for_operation(self, session: Dict[str, Any], operation: Dict[str, Any], result: Dict[str, Any]) -> AuditLog:
        """为操作创建审计日志"""
        audit_log = AuditLog(
            log_id=str(uuid.uuid4()),
            agent_id=session["agent_id"],
            agent_type=session["agent_type"],
            user_id=session["user_id"],
            action=f"OPERATION_{operation.get('type', 'UNKNOWN')}",
            data_accessed=[operation.get("data_type", "unknown")],
            permission_level=PermissionLevel.READ_ONLY,  # 从会话中获取实际权限
            result="SUCCESS" if result.get("success") else "FAILED",
            timestamp=datetime.utcnow(),
            context={
                "session_id": session["session_id"],
                "operation": operation,
                "result": result
            }
        )
        
        self.audit_logs.append(audit_log)
        return audit_log
        
    def get_audit_logs(self, user_id: Optional[str] = None, agent_id: Optional[str] = None, 
                      start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> List[AuditLog]:
        """获取审计日志"""
        filtered_logs = self.audit_logs
        
        if user_id:
            filtered_logs = [log for log in filtered_logs if log.user_id==user_id]
            
        if agent_id:
            filtered_logs = [log for log in filtered_logs if log.agent_id==agent_id]
            
        if start_time:
            filtered_logs = [log for log in filtered_logs if log.timestamp>=start_time]
            
        if end_time:
            filtered_logs = [log for log in filtered_logs if log.timestamp<=end_time]
            
        return filtered_logs
        
    async def export_audit_to_blockchain(self, log_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """导出审计日志到区块链"""
        try:
            logs_to_export = self.audit_logs
            
            if log_ids:
                logs_to_export = [log for log in self.audit_logs if log.log_id in log_ids]
                
            blockchain_records = [log.to_blockchain_record() for log in logs_to_export]
            
            # 模拟区块链写入
            logger.info(f"导出 {len(blockchain_records)} 条审计记录到区块链")
            
            return {
                "success": True,
                "records_exported": len(blockchain_records),
                "blockchain_hash": hashlib.sha256(json.dumps(blockchain_records).encode()).hexdigest(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"导出审计日志到区块链失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            } 