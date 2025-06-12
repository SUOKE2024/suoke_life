"""
security_audit - 索克生活项目模块
"""

import hashlib
import json
import logging
import re
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import redis.asyncio as redis
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

"""
用户服务安全审计日志中间件
实现全面的安全事件记录、威胁检测和实时监控
"""


logger = logging.getLogger(__name__)


class SecurityEventType(Enum):
    """安全事件类型"""

    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    ACCOUNT_LOCKED = "account_locked"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    MALICIOUS_REQUEST = "malicious_request"
    BRUTE_FORCE_ATTACK = "brute_force_attack"
    SQL_INJECTION_ATTEMPT = "sql_injection_attempt"
    XSS_ATTEMPT = "xss_attempt"
    CSRF_ATTEMPT = "csrf_attempt"


class SecurityLevel(Enum):
    """安全级别"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityEvent:
    """安全事件数据结构"""

    event_id: str
    event_type: SecurityEventType
    security_level: SecurityLevel
    timestamp: datetime
    user_id: Optional[str]
    session_id: Optional[str]
    ip_address: str
    user_agent: str
    endpoint: str
    method: str
    status_code: int
    request_size: int
    response_size: int
    processing_time: float
    details: Dict[str, Any]
    threat_indicators: List[str]
    risk_score: int  # 0 - 100


class ThreatDetector:
    """威胁检测器"""

    def __init__(self) -> None:
        """TODO: 添加文档字符串"""
        # 恶意模式
        self.malicious_patterns = {
            "sql_injection": [
                r"(\bunion\b. * \bselect\b)",
                r"(\bselect\b. * \bfrom\b. * \bwhere\b)",
                r"(\bdrop\b. * \btable\b)",
                r"(\binsert\b. * \binto\b)",
                r"(\bdelete\b. * \bfrom\b)",
                r"(\bupdate\b. * \bset\b)",
                r"(\bor\b. * 1\s*=\s * 1)",
                r"(\band\b. * 1\s*=\s * 1)",
                r"(\bor\b. * '. * '.*=. * '. * ')",
                r"(\bunion\b. * \ball\b. * \bselect\b)",
            ],
            "xss": [
                r"<script[^>] * >. * ?< / script>",
                r"javascript:",
                r"on\w + \s*=",
                r"<iframe[^>] * >",
                r"<object[^>] * >",
                r"<embed[^>] * >",
                r"<link[^>] * >",
                r"<meta[^>] * >",
            ],
            "path_traversal": [
                r"\.\. / ",
                r"\.\.\\",
                r"%2e%2e%2f",
                r"%2e%2e\\",
                r"..%2f",
                r"..%5c",
            ],
            "command_injection": [
                r";\s * (cat|ls|pwd|whoami|id|uname)",
                r"\|\s * (cat|ls|pwd|whoami|id|uname)",
                r"&&\s * (cat|ls|pwd|whoami|id|uname)",
                r"`. * `",
                r"\$\(. * \)",
            ],
        }

        # 可疑用户代理
        self.suspicious_user_agents = {
            "sqlmap",
            "nikto",
            "nmap",
            "masscan",
            "burp",
            "owasp",
            "w3af",
            "acunetix",
            "nessus",
        }

        # 敏感端点
        self.sensitive_endpoints = {
            " / api / v1 / auth / login",
            " / api / v1 / auth / register",
            " / api / v1 / users / profile",
            " / api / v1 / admin",
            " / api / v1 / export",
        }

    def detect_threats(self, request: Request, request_body: str = "") -> List[str]:
        """检测威胁指标"""
        threats = []

        # 检查URL中的恶意模式
        url_threats = self._check_malicious_patterns(str(request.url))
        threats.extend(url_threats)

        # 检查请求体中的恶意模式
        if request_body:
            body_threats = self._check_malicious_patterns(request_body)
            threats.extend(body_threats)

        # 检查请求头
        header_threats = self._check_headers(request.headers)
        threats.extend(header_threats)

        # 检查用户代理
        ua_threats = self._check_user_agent(request.headers.get("user - agent", ""))
        threats.extend(ua_threats)

        return list(set(threats))  # 去重

    def _check_malicious_patterns(self, text: str) -> List[str]:
        """检查恶意模式"""
        threats = []
        text_lower = text.lower()

        for threat_type, patterns in self.malicious_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    threats.append(f"{threat_type}_detected")
                    break

        return threats

    def _check_headers(self, headers) -> List[str]:
        """检查可疑请求头"""
        threats = []

        # 检查缺少必要的安全头
        if "user - agent" not in headers:
            threats.append("missing_user_agent")

        # 检查可疑的头值
        for name, value in headers.items():
            if self._check_malicious_patterns(value):
                threats.append(f"malicious_header_{name}")

        return threats

    def _check_user_agent(self, user_agent: str) -> List[str]:
        """检查用户代理"""
        threats = []
        ua_lower = user_agent.lower()

        for suspicious_ua in self.suspicious_user_agents:
            if suspicious_ua in ua_lower:
                threats.append(f"suspicious_user_agent_{suspicious_ua}")

        return threats

    def calculate_risk_score(
        self, threats: List[str], endpoint: str, method: str, status_code: int
    ) -> int:
        """计算风险评分 (0 - 100)"""
        score = 0

        # 基础威胁评分
        threat_scores = {
            "sql_injection_detected": 30,
            "xss_detected": 25,
            "path_traversal_detected": 20,
            "command_injection_detected": 35,
            "suspicious_user_agent": 15,
            "malicious_header": 10,
            "missing_user_agent": 5,
        }

        for threat in threats:
            for pattern, points in threat_scores.items():
                if pattern in threat:
                    score += points

        # 敏感端点加分
        if endpoint in self.sensitive_endpoints:
            score += 10

        # 错误状态码加分
        if status_code >= 400:
            score += 5

        # 危险方法加分
        if method in ["DELETE", "PUT", "PATCH"]:
            score += 5

        return min(score, 100)


class SecurityAuditor:
    """安全审计器"""

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """TODO: 添加文档字符串"""
        self.redis = redis_client
        self.threat_detector = ThreatDetector()

        # 内存存储
        self.events_buffer: deque = deque(maxlen=1000)
        self.ip_activity: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.user_activity: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))

        # 攻击检测阈值
        self.attack_thresholds = {
            "brute_force": {"failed_attempts": 5, "time_window": 300},  # 5分钟
            "rate_limit": {"requests": 100, "time_window": 60},  # 1分钟
        }

    async def log_security_event(
        self,
        event_type: SecurityEventType,
        request: Request,
        response: Response,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        request_body: str = "",
    ) -> SecurityEvent:
        """记录安全事件"""

        # 检测威胁
        threats = self.threat_detector.detect_threats(request, request_body)

        # 计算风险评分
        risk_score = self.threat_detector.calculate_risk_score(
            threats, str(request.url.path), request.method, response.status_code
        )

        # 确定安全级别
        security_level = self._determine_security_level(risk_score, threats)

        # 创建事件
        event = SecurityEvent(
            event_id=self._generate_event_id(),
            event_type=event_type,
            security_level=security_level,
            timestamp=datetime.utcnow(),
            user_id=user_id,
            session_id=session_id,
            ip_address=self._get_client_ip(request),
            user_agent=request.headers.get("user - agent", ""),
            endpoint=str(request.url.path),
            method=request.method,
            status_code=response.status_code,
            request_size=len(request_body),
            response_size=len(getattr(response, "body", b"")),
            processing_time=0.0,  # 需要从外部传入
            details=details or {},
            threat_indicators=threats,
            risk_score=risk_score,
        )

        # 存储事件
        await self._store_event(event)

        # 检测攻击模式
        await self._detect_attack_patterns(event)

        # 发送告警
        if security_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
            await self._send_alert(event)

        return event

    def _determine_security_level(
        self, risk_score: int, threats: List[str]
    ) -> SecurityLevel:
        """确定安全级别"""
        if risk_score >= 80 or any("injection" in threat for threat in threats):
            return SecurityLevel.CRITICAL
        elif risk_score >= 60 or any("suspicious" in threat for threat in threats):
            return SecurityLevel.HIGH
        elif risk_score >= 30:
            return SecurityLevel.MEDIUM
        else:
            return SecurityLevel.LOW

    def _generate_event_id(self) -> str:
        """生成事件ID"""
        timestamp = str(time.time())
        return hashlib.md5(timestamp.encode()).hexdigest()[:16]

    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP"""
        forwarded_for = request.headers.get("X - Forwarded - For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X - Real - IP")
        if real_ip:
            return real_ip

        if hasattr(request.client, "host"):
            return request.client.host

        return "unknown"

    async def _store_event(self, event: SecurityEvent):
        """存储安全事件"""
        event_data = asdict(event)
        event_data["timestamp"] = event.timestamp.isoformat()

        # 存储到Redis
        if self.redis:
            try:
                # 存储事件详情
                await self.redis.hset(
                    f"security_event:{event.event_id}", mapping=event_data
                )

                # 添加到时间序列
                await self.redis.zadd(
                    "security_events_timeline",
                    {event.event_id: event.timestamp.timestamp()},
                )

                # 按类型索引
                await self.redis.sadd(
                    f"security_events_by_type:{event.event_type.value}", event.event_id
                )

                # 按IP索引
                await self.redis.sadd(
                    f"security_events_by_ip:{event.ip_address}", event.event_id
                )

                # 设置过期时间 (30天)
                await self.redis.expire(f"security_event:{event.event_id}", 2592000)

            except Exception as e:
                logger.error(f"Redis存储安全事件失败: {e}")

        # 内存备份
        self.events_buffer.append(event)

        # 记录IP活动
        self.ip_activity[event.ip_address].append(
            {
                "timestamp": event.timestamp,
                "event_type": event.event_type,
                "risk_score": event.risk_score,
            }
        )

        # 记录用户活动
        if event.user_id:
            self.user_activity[event.user_id].append(
                {
                    "timestamp": event.timestamp,
                    "event_type": event.event_type,
                    "risk_score": event.risk_score,
                }
            )

    async def _detect_attack_patterns(self, event: SecurityEvent):
        """检测攻击模式"""
        current_time = event.timestamp

        # 检测暴力破解攻击
        if event.event_type == SecurityEventType.LOGIN_FAILURE:
            await self._detect_brute_force(event.ip_address, current_time)

        # 检测异常活动
        await self._detect_anomalous_activity(event)

    async def _detect_brute_force(self, ip_address: str, current_time: datetime):
        """检测暴力破解攻击"""
        threshold = self.attack_thresholds["brute_force"]
        time_window = timedelta(seconds=threshold["time_window"])

        # 获取时间窗口内的失败登录次数
        failed_attempts = 0
        for activity in self.ip_activity[ip_address]:
            if (current_time - activity["timestamp"]) <= time_window:
                if activity["event_type"] == SecurityEventType.LOGIN_FAILURE:
                    failed_attempts += 1

        # 如果超过阈值，记录暴力破解事件
        if failed_attempts >= threshold["failed_attempts"]:
            await self._create_attack_event(
                SecurityEventType.BRUTE_FORCE_ATTACK,
                ip_address,
                {
                    "failed_attempts": failed_attempts,
                    "time_window": threshold["time_window"],
                },
            )

    async def _detect_anomalous_activity(self, event: SecurityEvent):
        """检测异常活动"""
        # 检测高风险评分的连续事件
        if event.risk_score >= 70:
            recent_high_risk = 0
            for activity in self.ip_activity[event.ip_address]:
                if (event.timestamp - activity["timestamp"]).seconds <= 300:  # 5分钟内
                    if activity["risk_score"] >= 70:
                        recent_high_risk += 1

            if recent_high_risk >= 3:
                await self._create_attack_event(
                    SecurityEventType.SUSPICIOUS_ACTIVITY,
                    event.ip_address,
                    {"high_risk_events": recent_high_risk},
                )

    async def _create_attack_event(
        self, event_type: SecurityEventType, ip_address: str, details: Dict[str, Any]
    ):
        """创建攻击事件"""
        attack_event = SecurityEvent(
            event_id=self._generate_event_id(),
            event_type=event_type,
            security_level=SecurityLevel.CRITICAL,
            timestamp=datetime.utcnow(),
            user_id=None,
            session_id=None,
            ip_address=ip_address,
            user_agent="",
            endpoint="",
            method="",
            status_code=0,
            request_size=0,
            response_size=0,
            processing_time=0.0,
            details=details,
            threat_indicators=[event_type.value],
            risk_score=100,
        )

        await self._store_event(attack_event)
        await self._send_alert(attack_event)

    async def _send_alert(self, event: SecurityEvent):
        """发送安全告警"""
        alert_data = {
            "event_id": event.event_id,
            "event_type": event.event_type.value,
            "security_level": event.security_level.value,
            "timestamp": event.timestamp.isoformat(),
            "ip_address": event.ip_address,
            "endpoint": event.endpoint,
            "risk_score": event.risk_score,
            "threat_indicators": event.threat_indicators,
            "details": event.details,
        }

        # 记录告警日志
        logger.warning(f"安全告警: {json.dumps(alert_data, ensure_ascii = False)}")

        # 这里可以集成其他告警系统
        # 例如：发送邮件、Slack通知、短信等


class SecurityAuditMiddleware(BaseHTTPMiddleware):
    """安全审计中间件"""

    def __init__(self, app, redis_client: Optional[redis.Redis] = None):
        """TODO: 添加文档字符串"""
        super().__init__(app)
        self.auditor = SecurityAuditor(redis_client)

        # 需要审计的路径
        self.audit_paths = {
            " / api / v1 / auth",
            " / api / v1 / users",
            " / api / v1 / admin",
            " / api / v1 / health - data",
            " / api / v1 / devices",
        }

        # 跳过审计的路径
        self.skip_paths = {
            " / health",
            " / metrics",
            " / docs",
            " / redoc",
            " / openapi.json",
        }

    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        start_time = time.time()

        # 跳过不需要审计的路径
        if any(request.url.path.startswith(skip) for skip in self.skip_paths):
            return await call_next(request)

        # 读取请求体
        request_body = ""
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                request_body = body.decode("utf - 8")
            except Exception:
                pass

        # 处理请求
        response = await call_next(request)

        # 计算处理时间
        processing_time = time.time() - start_time

        # 确定事件类型
        event_type = self._determine_event_type(request, response)

        # 获取用户信息
        user_id = self._extract_user_id(request)
        session_id = self._extract_session_id(request)

        # 记录安全事件
        if any(request.url.path.startswith(audit) for audit in self.audit_paths):
            await self.auditor.log_security_event(
                event_type=event_type,
                request=request,
                response=response,
                user_id=user_id,
                session_id=session_id,
                details={
                    "processing_time": processing_time,
                    "request_size": len(request_body),
                    "response_size": len(getattr(response, "body", b"")),
                },
                request_body=request_body,
            )

        return response

    def _determine_event_type(
        self, request: Request, response: Response
    ) -> SecurityEventType:
        """确定事件类型"""
        path = request.url.path
        method = request.method
        status = response.status_code

        # 登录相关
        if " / auth / login" in path:
            return (
                SecurityEventType.LOGIN_SUCCESS
                if status == 200
                else SecurityEventType.LOGIN_FAILURE
            )

        if " / auth / logout" in path:
            return SecurityEventType.LOGOUT

        # 数据访问
        if method == "GET":
            return SecurityEventType.DATA_ACCESS

        # 数据修改
        if method in ["POST", "PUT", "PATCH", "DELETE"]:
            return SecurityEventType.DATA_MODIFICATION

        # 未授权访问
        if status == 401:
            return SecurityEventType.UNAUTHORIZED_ACCESS

        # 默认为可疑活动
        return SecurityEventType.SUSPICIOUS_ACTIVITY

    def _extract_user_id(self, request: Request) -> Optional[str]:
        """提取用户ID"""
        # 从JWT token中提取
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # 这里应该解析JWT token
            # 简化实现
            return None

        return None

    def _extract_session_id(self, request: Request) -> Optional[str]:
        """提取会话ID"""
        # 从cookie或header中提取
        return request.headers.get("X - Session - ID")


# 工厂函数
def create_security_audit_middleware(redis_url: Optional[str] = None):
    """创建安全审计中间件"""
    redis_client = None
    if redis_url:
        try:
            redis_client = redis.from_url(redis_url)
        except Exception as e:
            logger.warning(f"无法连接Redis，使用内存存储: {e}")

    return SecurityAuditMiddleware(None, redis_client)
