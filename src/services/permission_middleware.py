"""
permission_middleware - 索克生活项目模块
"""

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

# -*- coding: utf-8 -*-
"""
权限中间件示例
支持基于用户角色的最小权限控制
适用于FastAPI等Python微服务
"""

# 角色-权限映射
ROLE_PERMISSIONS = {
    "admin": [("GET", "/admin"), ("POST", "/admin")],
    "doctor": [("GET", "/patient"), ("POST", "/patient")],
    "user": [("GET", "/profile"), ("POST", "/health-data")],
}


def check_permission_rbac(user, path, method):
    if not user or "role" not in user:
        return False
    role = user["role"]
    allowed = ROLE_PERMISSIONS.get(role, [])
    # 支持模糊匹配
    return any(path.startswith(p) and method == m for m, p in allowed)


def check_permission_abac(user, path, method, attributes):
    # attributes: dict, 例如 {"department": "cardiology", "resource_owner": "user123"}
    if not user:
        return False
    # 例：只有本部门医生可访问本部门患者
    if user.get("role") == "doctor" and user.get("department") == attributes.get(
        "department"
    ):
        return True
    # 例：用户只能访问自己的数据
    if user.get("role") == "user" and user.get("user_id") == attributes.get(
        "resource_owner"
    ):
        return True
    return False


# 统一权限检查入口
# mode: "rbac" 或 "abac"，attributes仅abac用


def check_permission(user, path, method, mode="rbac", attributes=None):
    if mode == "rbac":
        return check_permission_rbac(user, path, method)
    elif mode == "abac":
        return check_permission_abac(user, path, method, attributes or {})
    else:
        return False


class PermissionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 假设token解码后用户信息放在request.state.user
        user = getattr(request.state, "user", None)
        if not check_permission(user, request.url.path, request.method):
            raise HTTPException(status_code=403, detail="无权限访问")
        response = await call_next(request)
        return response


# 用法示例（FastAPI）
# from fastapi import FastAPI
# app = FastAPI()
# app.add_middleware(PermissionMiddleware)
