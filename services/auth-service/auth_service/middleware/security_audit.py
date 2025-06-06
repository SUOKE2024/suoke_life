"""
security_audit - 索克生活项目模块
"""

            from auth_service.models.audit import SecurityAuditLog
        import uuid
from auth_service.config.settings import get_settings
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional, List
import asyncio
import json
import logging
import time

"""
安全审计日志中间件
记录所有安全相关的事件，包括登录、认证失败、权限变更等
"""




class SecurityEventType(Enum):
    """安全事件类型"""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGIN_BLOCKED = "login_blocked"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET_REQUEST = "password_reset_request"
    PASSWORD_RESET_SUCCESS = "password_reset_success"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    MFA_VERIFY_SUCCESS = "mfa_verify_success"
    MFA_VERIFY_FAILED = "mfa_verify_failed"
    TOKEN_REFRESH = "token_refresh"
    TOKEN_REVOKED = "token_revoked"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"
    PERMISSION_DENIED = "permission_denied"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    OAUTH_LOGIN = "oauth_login"
    OAUTH_FAILED = "oauth_failed"
    SESSION_EXPIRED = "session_expired"
    INVALID_TOKEN = "invalid_token"
    BRUTE_FORCE_DETECTED = "brute_force_detected"


class SecurityEventSeverity(Enum):
    """安全事件严重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityEvent:
    """安全事件数据结构"""
    event_type: SecurityEventType
    severity: SecurityEventSeverity
    user_id: Optional[str]
    username: Optional[str]
    ip_address: str
    user_agent: str
    timestamp: datetime
    details: Dict[str, Any]
    request_id: Optional[str] = None
    session_id: Optional[str] = None
    device_id: Optional[str] = None
    location: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        data['event_type'] = self.event_type.value
        data['severity'] = self.severity.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


class SecurityAuditLogger:
    """安全审计日志记录器"""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = logging.getLogger("security_audit")
        
        # 配置日志格式
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
        # 高风险事件类型
        self.high_risk_events = {
            SecurityEventType.LOGIN_FAILED,
            SecurityEventType.LOGIN_BLOCKED,
            SecurityEventType.ACCOUNT_LOCKED,
            SecurityEventType.BRUTE_FORCE_DETECTED,
            SecurityEventType.SUSPICIOUS_ACTIVITY,
            SecurityEventType.PERMISSION_DENIED,
            SecurityEventType.INVALID_TOKEN
        }
        
        # 需要实时告警的事件
        self.alert_events = {
            SecurityEventType.BRUTE_FORCE_DETECTED,
            SecurityEventType.SUSPICIOUS_ACTIVITY,
            SecurityEventType.ACCOUNT_LOCKED
        }
    
    async def log_event(self, event: SecurityEvent, db: Optional[AsyncSession] = None):
        """记录安全事件"""
        try:
            # 记录到日志文件
            self._log_to_file(event)
            
            # 记录到数据库
            if db:
                await self._log_to_database(event, db)
            
            # 检查是否需要告警
            if event.event_type in self.alert_events:
                await self._send_alert(event)
            
            # 检查是否需要自动响应
            await self._check_auto_response(event)
            
        except Exception as e:
            self.logger.error(f"记录安全事件失败: {e}")
    
    def _log_to_file(self, event: SecurityEvent):
        """记录到日志文件"""
        log_data = event.to_dict()
        log_message = json.dumps(log_data, ensure_ascii=False, indent=2)
        
        if event.severity in [SecurityEventSeverity.HIGH, SecurityEventSeverity.CRITICAL]:
            self.logger.error(f"SECURITY_EVENT: {log_message}")
        elif event.severity == SecurityEventSeverity.MEDIUM:
            self.logger.warning(f"SECURITY_EVENT: {log_message}")
        else:
            self.logger.info(f"SECURITY_EVENT: {log_message}")
    
    async def _log_to_database(self, event: SecurityEvent, db: AsyncSession):
        """记录到数据库"""
        try:
            
            audit_log = SecurityAuditLog(
                event_type=event.event_type.value,
                severity=event.severity.value,
                user_id=event.user_id,
                username=event.username,
                ip_address=event.ip_address,
                user_agent=event.user_agent,
                timestamp=event.timestamp,
                details=event.details,
                request_id=event.request_id,
                session_id=event.session_id,
                device_id=event.device_id,
                location=event.location,
                success=event.success,
                error_message=event.error_message
            )
            
            db.add(audit_log)
            await db.commit()
            
        except Exception as e:
            self.logger.error(f"记录安全事件到数据库失败: {e}")
            await db.rollback()
    
    async def _send_alert(self, event: SecurityEvent):
        """发送安全告警"""
        try:
            # 这里可以集成各种告警渠道
            # 例如：邮件、短信、Slack、钉钉等
            
            alert_message = self._format_alert_message(event)
            
            # 发送到监控系统
            await self._send_to_monitoring(event, alert_message)
            
            # 发送邮件告警
            if self.settings.security.email_alerts_enabled:
                await self._send_email_alert(event, alert_message)
            
            # 发送到Slack
            if self.settings.security.slack_alerts_enabled:
                await self._send_slack_alert(event, alert_message)
                
        except Exception as e:
            self.logger.error(f"发送安全告警失败: {e}")
    
    def _format_alert_message(self, event: SecurityEvent) -> str:
        """格式化告警消息"""
        return f"""
🚨 安全告警 - {event.severity.value.upper()}

事件类型: {event.event_type.value}
时间: {event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
用户: {event.username or '未知'} (ID: {event.user_id or '未知'})
IP地址: {event.ip_address}
设备: {event.device_id or '未知'}

详细信息:
{json.dumps(event.details, ensure_ascii=False, indent=2)}

错误信息: {event.error_message or '无'}
        """.strip()
    
    async def _send_to_monitoring(self, event: SecurityEvent, message: str):
        """发送到监控系统"""
        # 这里可以集成Prometheus、Grafana等监控系统
        pass
    
    async def _send_email_alert(self, event: SecurityEvent, message: str):
        """发送邮件告警"""
        # 这里可以集成邮件发送服务
        pass
    
    async def _send_slack_alert(self, event: SecurityEvent, message: str):
        """发送Slack告警"""
        # 这里可以集成Slack API
        pass
    
    async def _check_auto_response(self, event: SecurityEvent):
        """检查是否需要自动响应"""
        try:
            # 暴力破解检测
            if event.event_type == SecurityEventType.LOGIN_FAILED:
                await self._check_brute_force(event)
            
            # 可疑活动检测
            if event.event_type in [SecurityEventType.PERMISSION_DENIED, SecurityEventType.INVALID_TOKEN]:
                await self._check_suspicious_activity(event)
                
        except Exception as e:
            self.logger.error(f"自动响应检查失败: {e}")
    
    async def _check_brute_force(self, event: SecurityEvent):
        """检查暴力破解攻击"""
        # 这里可以实现暴力破解检测逻辑
        # 例如：在短时间内多次登录失败
        pass
    
    async def _check_suspicious_activity(self, event: SecurityEvent):
        """检查可疑活动"""
        # 这里可以实现可疑活动检测逻辑
        # 例如：异常IP、异常时间、异常行为模式等
        pass


class SecurityAuditMiddleware:
    """安全审计中间件"""
    
    def __init__(self, app):
        self.app = app
        self.audit_logger = SecurityAuditLogger()
        self.settings = get_settings()
        
        # 需要审计的路径
        self.audit_paths = {
            "/api/v1/auth/login",
            "/api/v1/auth/logout",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
            "/api/v1/auth/forgot-password",
            "/api/v1/auth/reset-password",
            "/api/v1/auth/verify-mfa",
            "/api/v1/auth/enable-mfa",
            "/api/v1/auth/disable-mfa",
            "/api/v1/auth/change-password"
        }
    
    async def __call__(self, request: Request, call_next):
        """中间件处理函数"""
        start_time = time.time()
        
        # 生成请求ID
        request_id = self._generate_request_id()
        request.state.request_id = request_id
        
        # 获取请求信息
        ip_address = self._get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "")
        path = request.url.path
        method = request.method
        
        # 处理请求
        response = await call_next(request)
        
        # 检查是否需要审计
        if path in self.audit_paths:
            await self._audit_request(request, response, start_time)
        
        # 添加安全头
        self._add_security_headers(response)
        
        return response
    
    async def _audit_request(self, request: Request, response: Response, start_time: float):
        """审计请求"""
        try:
            path = request.url.path
            method = request.method
            status_code = response.status_code
            
            # 获取用户信息
            user_id = getattr(request.state, 'user_id', None)
            username = getattr(request.state, 'username', None)
            
            # 确定事件类型和严重程度
            event_type, severity = self._determine_event_type(path, method, status_code)
            
            if event_type:
                # 创建安全事件
                event = SecurityEvent(
                    event_type=event_type,
                    severity=severity,
                    user_id=user_id,
                    username=username,
                    ip_address=self._get_client_ip(request),
                    user_agent=request.headers.get("User-Agent", ""),
                    timestamp=datetime.utcnow(),
                    details={
                        "path": path,
                        "method": method,
                        "status_code": status_code,
                        "response_time": time.time() - start_time,
                        "request_size": request.headers.get("Content-Length", 0),
                        "response_size": response.headers.get("Content-Length", 0)
                    },
                    request_id=getattr(request.state, 'request_id', None),
                    success=200 <= status_code < 400
                )
                
                # 记录事件
                await self.audit_logger.log_event(event)
                
        except Exception as e:
            self.audit_logger.logger.error(f"审计请求失败: {e}")
    
    def _determine_event_type(self, path: str, method: str, status_code: int) -> tuple:
        """确定事件类型和严重程度"""
        if path == "/api/v1/auth/login":
            if status_code == 200:
                return SecurityEventType.LOGIN_SUCCESS, SecurityEventSeverity.LOW
            elif status_code == 401:
                return SecurityEventType.LOGIN_FAILED, SecurityEventSeverity.MEDIUM
            elif status_code == 423:
                return SecurityEventType.LOGIN_BLOCKED, SecurityEventSeverity.HIGH
        
        elif path == "/api/v1/auth/logout":
            if status_code == 200:
                return SecurityEventType.LOGOUT, SecurityEventSeverity.LOW
        
        elif path == "/api/v1/auth/refresh":
            if status_code == 200:
                return SecurityEventType.TOKEN_REFRESH, SecurityEventSeverity.LOW
            elif status_code == 401:
                return SecurityEventType.INVALID_TOKEN, SecurityEventSeverity.MEDIUM
        
        elif path == "/api/v1/auth/change-password":
            if status_code == 200:
                return SecurityEventType.PASSWORD_CHANGE, SecurityEventSeverity.MEDIUM
        
        elif path == "/api/v1/auth/forgot-password":
            if status_code == 200:
                return SecurityEventType.PASSWORD_RESET_REQUEST, SecurityEventSeverity.MEDIUM
        
        elif path == "/api/v1/auth/reset-password":
            if status_code == 200:
                return SecurityEventType.PASSWORD_RESET_SUCCESS, SecurityEventSeverity.MEDIUM
        
        elif path == "/api/v1/auth/verify-mfa":
            if status_code == 200:
                return SecurityEventType.MFA_VERIFY_SUCCESS, SecurityEventSeverity.LOW
            elif status_code == 401:
                return SecurityEventType.MFA_VERIFY_FAILED, SecurityEventSeverity.MEDIUM
        
        elif path == "/api/v1/auth/enable-mfa":
            if status_code == 200:
                return SecurityEventType.MFA_ENABLED, SecurityEventSeverity.MEDIUM
        
        elif path == "/api/v1/auth/disable-mfa":
            if status_code == 200:
                return SecurityEventType.MFA_DISABLED, SecurityEventSeverity.MEDIUM
        
        # 权限拒绝
        if status_code == 403:
            return SecurityEventType.PERMISSION_DENIED, SecurityEventSeverity.HIGH
        
        # 限流
        if status_code == 429:
            return SecurityEventType.RATE_LIMIT_EXCEEDED, SecurityEventSeverity.MEDIUM
        
        return None, None
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP地址"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _generate_request_id(self) -> str:
        """生成请求ID"""
        return str(uuid.uuid4())
    
    def _add_security_headers(self, response: Response):
        """添加安全头"""
        # 防止点击劫持
        response.headers["X-Frame-Options"] = "DENY"
        
        # 防止MIME类型嗅探
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # XSS保护
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # 严格传输安全
        if self.settings.security.force_https:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # 内容安全策略
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        # 引用者策略
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"


# 便捷函数
async def log_security_event(
    event_type: SecurityEventType,
    severity: SecurityEventSeverity,
    request: Request,
    details: Dict[str, Any],
    user_id: Optional[str] = None,
    username: Optional[str] = None,
    success: bool = True,
    error_message: Optional[str] = None
):
    """记录安全事件的便捷函数"""
    audit_logger = SecurityAuditLogger()
    
    event = SecurityEvent(
        event_type=event_type,
        severity=severity,
        user_id=user_id,
        username=username,
        ip_address=audit_logger._get_client_ip(request) if hasattr(audit_logger, '_get_client_ip') else "unknown",
        user_agent=request.headers.get("User-Agent", ""),
        timestamp=datetime.utcnow(),
        details=details,
        request_id=getattr(request.state, 'request_id', None),
        success=success,
        error_message=error_message
    )
    
    await audit_logger.log_event(event) 