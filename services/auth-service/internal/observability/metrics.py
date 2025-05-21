#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
指标收集模块

按照索克生活APP微服务可观测性指南实现标准的指标收集功能。
提供四类核心指标：
1. 请求率（Rate）
2. 错误率（Errors）
3. 持续时间（Duration）
4. 资源使用（Resources）

以及认证服务特定指标。
"""
import time
from typing import Callable, Optional

from fastapi import FastAPI, Request, Response
from prometheus_client import Counter, Histogram, Gauge, Info
from prometheus_client.openmetrics.exposition import generate_latest

# 通用指标
REQUEST_COUNTER = Counter(
    "auth_request_count_total",
    "认证服务请求总数",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "auth_request_latency_seconds",
    "认证服务请求延迟（秒）",
    ["method", "endpoint"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]
)

ACTIVE_REQUESTS = Gauge(
    "auth_active_requests",
    "认证服务当前活跃请求数",
    ["method", "endpoint"]
)

# 认证服务特定指标
LOGIN_ATTEMPTS = Counter(
    "auth_login_attempts_total",
    "用户登录尝试总数",
    ["success", "auth_method"]
)

TOKEN_ISSUED = Counter(
    "auth_token_issued_total",
    "发放的令牌总数",
    ["token_type"]
)

TOKEN_VALIDATION = Counter(
    "auth_token_validation_total",
    "令牌验证总数",
    ["valid"]
)

MFA_ATTEMPTS = Counter(
    "auth_mfa_attempts_total",
    "多因素认证尝试总数",
    ["success", "mfa_type"]
)

USER_CREATION = Counter(
    "auth_user_creation_total",
    "用户创建总数",
    ["success"]
)

ROLE_ASSIGNMENT = Counter(
    "auth_role_assignment_total",
    "角色分配总数"
)

PASSWORD_CHANGES = Counter(
    "auth_password_changes_total",
    "密码修改总数",
    ["type"]  # reset, change
)

PASSWORD_HASH_TIME = Histogram(
    "auth_password_hash_duration_seconds",
    "密码哈希计算时间（秒）",
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5]
)

REFRESH_TOKEN_USED = Counter(
    "auth_refresh_token_used_total",
    "刷新令牌使用总数",
    ["success"]
)

ACTIVE_SESSIONS = Gauge(
    "auth_active_sessions",
    "当前活跃会话数"
)

# 系统信息
SERVICE_INFO = Info(
    "auth_service_info",
    "认证服务信息"
)

class PrometheusMiddleware:
    """
    Prometheus中间件，用于收集请求指标
    """
    
    def __init__(self, app: FastAPI):
        self.app = app
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        method = request.method
        path = request.url.path
        
        # 过滤掉对metrics端点的请求，避免重复计数
        if path == "/metrics":
            return await call_next(request)
        
        # 增加活跃请求计数
        ACTIVE_REQUESTS.labels(method=method, endpoint=path).inc()
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 处理请求
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            # 处理异常情况
            status_code = 500
            raise e
        finally:
            # 记录请求延迟
            duration = time.time() - start_time
            REQUEST_LATENCY.labels(method=method, endpoint=path).observe(duration)
            
            # 增加请求计数
            REQUEST_COUNTER.labels(method=method, endpoint=path, status=str(status_code)).inc()
            
            # 减少活跃请求计数
            ACTIVE_REQUESTS.labels(method=method, endpoint=path).dec()
        
        return response

def setup_metrics(app: FastAPI, app_version: str, app_info: dict) -> None:
    """
    设置指标收集
    
    Args:
        app: FastAPI应用实例
        app_version: 应用版本
        app_info: 应用信息
    """
    # 设置服务信息
    SERVICE_INFO.info({
        "version": app_version,
        "start_time": str(int(time.time())),
        **app_info
    })
    
    # 添加Prometheus中间件
    app.add_middleware(PrometheusMiddleware)
    
    # 添加metrics端点
    @app.get("/metrics", include_in_schema=False)
    async def metrics():
        return Response(content=generate_latest(), media_type="text/plain")
    
def record_login_attempt(success: bool, auth_method: str = "password") -> None:
    """
    记录登录尝试
    
    Args:
        success: 登录是否成功
        auth_method: 认证方法（password, oauth, mfa等）
    """
    LOGIN_ATTEMPTS.labels(success=str(success).lower(), auth_method=auth_method).inc()

def record_token_issued(token_type: str = "access") -> None:
    """
    记录令牌发放
    
    Args:
        token_type: 令牌类型（access或refresh）
    """
    TOKEN_ISSUED.labels(token_type=token_type).inc()

def record_token_validation(valid: bool) -> None:
    """
    记录令牌验证
    
    Args:
        valid: 令牌是否有效
    """
    TOKEN_VALIDATION.labels(valid=str(valid).lower()).inc()

def record_mfa_attempt(success: bool, mfa_type: str = "totp") -> None:
    """
    记录多因素认证尝试
    
    Args:
        success: 尝试是否成功
        mfa_type: MFA类型（totp, sms, email等）
    """
    MFA_ATTEMPTS.labels(success=str(success).lower(), mfa_type=mfa_type).inc()

def record_user_creation(success: bool) -> None:
    """
    记录用户创建
    
    Args:
        success: 创建是否成功
    """
    USER_CREATION.labels(success=str(success).lower()).inc()

def record_password_change(change_type: str = "change") -> None:
    """
    记录密码修改
    
    Args:
        change_type: 修改类型（change或reset）
    """
    PASSWORD_CHANGES.labels(type=change_type).inc()

def record_password_hash_time(duration: float) -> None:
    """
    记录密码哈希时间
    
    Args:
        duration: 哈希计算时间（秒）
    """
    PASSWORD_HASH_TIME.observe(duration)

def record_refresh_token_used(success: bool) -> None:
    """
    记录刷新令牌使用
    
    Args:
        success: 使用是否成功
    """
    REFRESH_TOKEN_USED.labels(success=str(success).lower()).inc()

def update_active_sessions(count: int) -> None:
    """
    更新活跃会话数
    
    Args:
        count: 活跃会话数
    """
    ACTIVE_SESSIONS.set(count)

def increment_role_assignment() -> None:
    """
    增加角色分配计数
    """
    ROLE_ASSIGNMENT.inc()