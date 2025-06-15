#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
可观测性模块

提供健康检查、指标收集和分布式追踪功能。
"""
from .health import HealthCheck
from .metrics import setup_metrics, record_login_attempt, record_token_issued, record_token_validation
from .metrics import record_mfa_attempt, record_user_creation, record_password_change
from .metrics import record_password_hash_time, record_refresh_token_used, update_active_sessions
from .metrics import increment_role_assignment
from .tracing import setup_tracing, get_tracer, trace_auth_operation, inject_context_to_headers

__all__ = [
    "HealthCheck",
    "setup_metrics",
    "record_login_attempt",
    "record_token_issued",
    "record_token_validation",
    "record_mfa_attempt",
    "record_user_creation",
    "record_password_change",
    "record_password_hash_time",
    "record_refresh_token_used",
    "update_active_sessions",
    "increment_role_assignment",
    "setup_tracing",
    "get_tracer",
    "trace_auth_operation",
    "inject_context_to_headers"
]