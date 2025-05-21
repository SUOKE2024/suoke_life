#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API文档配置模块

配置FastAPI的OpenAPI和Swagger UI，提供完整的API文档
"""
from typing import Dict, List, Optional

from fastapi import FastAPI
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles

# OpenAPI配置常量
API_TITLE = "授权服务 API"
API_DESCRIPTION = """
索克生命授权服务 (Auth Service) API 文档

## 功能

- 用户认证与授权
- 身份验证 (JWT, OAuth2)
- 多因素认证
- 用户账户管理
- 访问控制与权限管理

## 安全

所有 API 请求需要有效的访问令牌，通过 OAuth2 或 JWT 获取。
"""
API_VERSION = "v1"
API_CONTACT = {
    "name": "索克生命技术团队",
    "url": "https://api.suoke.life/contact",
    "email": "api@suoke.life",
}
API_LICENSE = {
    "name": "专有软件协议",
    "url": "https://www.suoke.life/terms-of-service",
}
API_TAGS_METADATA = [
    {
        "name": "身份验证",
        "description": "登录、注册与令牌管理",
    },
    {
        "name": "用户",
        "description": "用户账户管理与个人信息",
    },
    {
        "name": "权限",
        "description": "角色和权限管理",
    },
    {
        "name": "安全",
        "description": "多因素认证与安全设置",
    },
    {
        "name": "Health",
        "description": "健康检查与系统状态",
    },
]


def setup_openapi(app: FastAPI) -> None:
    """
    配置OpenAPI和API文档
    
    定制FastAPI的OpenAPI文档和Swagger UI界面
    
    Args:
        app: FastAPI应用实例
    """
    # 挂载静态文件
    try:
        app.mount("/static", StaticFiles(directory="static"), name="static")
    except RuntimeError:
        # 如果static目录不存在，忽略错误
        pass
    
    # 自定义OpenAPI文档生成
    def custom_openapi() -> Dict:
        if app.openapi_schema:
            return app.openapi_schema
        
        openapi_schema = get_openapi(
            title=API_TITLE,
            description=API_DESCRIPTION,
            version=API_VERSION,
            routes=app.routes,
            tags=API_TAGS_METADATA,
            contact=API_CONTACT,
            license_info=API_LICENSE,
        )
        
        # 添加安全定义
        openapi_schema["components"]["securitySchemes"] = {
            "OAuth2PasswordBearer": {
                "type": "oauth2",
                "flows": {
                    "password": {
                        "tokenUrl": "/api/v1/auth/token",
                        "scopes": {
                            "read": "读取权限",
                            "write": "写入权限",
                            "admin": "管理员权限",
                        },
                    }
                },
            },
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            },
        }
        
        # 添加全局安全要求
        openapi_schema["security"] = [{"BearerAuth": []}]
        
        # 保存生成的模式
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    
    # 替换默认的OpenAPI模式生成函数
    app.openapi = custom_openapi
    
    # 自定义Swagger UI和ReDoc
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=f"{API_TITLE} - Swagger UI",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_js_url="/static/swagger-ui-bundle.js",
            swagger_css_url="/static/swagger-ui.css",
            swagger_favicon_url="/static/favicon.png",
        )
    
    @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
    async def swagger_ui_redirect():
        return get_swagger_ui_oauth2_redirect_html()
    
    @app.get("/redoc", include_in_schema=False)
    async def redoc_html():
        return get_redoc_html(
            openapi_url=app.openapi_url,
            title=f"{API_TITLE} - ReDoc",
            redoc_js_url="/static/redoc.standalone.js",
            redoc_favicon_url="/static/favicon.png",
            with_google_fonts=False,
        )


def generate_api_documentation() -> str:
    """
    生成Markdown格式的API文档
    
    Returns:
        Markdown格式的API文档
    """
    documentation = f"""# {API_TITLE}

{API_DESCRIPTION}

## API版本

{API_VERSION}

## 联系信息

- **团队**: {API_CONTACT["name"]}
- **网址**: {API_CONTACT["url"]}
- **邮箱**: {API_CONTACT["email"]}

## 授权类型

- **OAuth2**: 使用用户名和密码获取令牌
- **JWT**: 基于JSON Web Token的身份验证

## 主要API路径

### 身份验证

- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/refresh-token` - 刷新访问令牌
- `POST /api/v1/auth/logout` - 注销并撤销令牌

### 用户管理

- `GET /api/v1/users/me` - 获取当前用户信息
- `PUT /api/v1/users/me` - 更新当前用户信息
- `GET /api/v1/users/{user_id}` - 获取指定用户信息
- `PUT /api/v1/users/{user_id}` - 更新指定用户信息
- `DELETE /api/v1/users/{user_id}` - 删除指定用户

### 权限管理

- `GET /api/v1/roles` - 获取所有角色
- `POST /api/v1/roles` - 创建新角色
- `GET /api/v1/roles/{role_id}` - 获取指定角色
- `PUT /api/v1/roles/{role_id}` - 更新指定角色
- `DELETE /api/v1/roles/{role_id}` - 删除指定角色
- `GET /api/v1/permissions` - 获取所有权限
- `POST /api/v1/users/{user_id}/roles` - 分配角色给用户

### 多因素认证

- `POST /api/v1/auth/mfa/enable` - 启用多因素认证
- `POST /api/v1/auth/mfa/disable` - 禁用多因素认证
- `POST /api/v1/auth/mfa/verify` - 验证多因素认证码

### 健康检查

- `GET /health` - 获取完整健康状态
- `GET /health/live` - 存活检查(Kubernetes存活探针)
- `GET /health/ready` - 就绪检查(Kubernetes就绪探针)

## 详细文档

完整的API文档可在以下位置获取：

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI规范: `/openapi.json`
"""
    return documentation 