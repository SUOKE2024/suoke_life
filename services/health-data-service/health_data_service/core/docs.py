"""
docs - 索克生活项目模块
"""

from .config import get_settings
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse
from typing import Dict, Any, List, Optional

"""
API文档生成器

提供完整的API文档生成和管理功能。
"""




def custom_openapi(app: FastAPI) -> Dict[str, Any]:
    """生成自定义OpenAPI规范"""
    if app.openapi_schema:
        return app.openapi_schema
    
    settings = get_settings()
    
    openapi_schema = get_openapi(
        title="索克生活健康数据服务API",
        version="1.0.0",
        description="""
## 索克生活健康数据服务

索克生活健康数据服务是一个专为索克生活应用打造的现代化健康数据管理平台。

### 核心功能

- **健康数据管理**：收集、存储和检索各类健康数据
- **生命体征监测**：实时监测和分析生命体征数据
- **中医体质分析**：基于中医理论的体质辨识和分析
- **数据处理管道**：自动化的数据验证、清洗和标准化
- **安全认证**：JWT令牌认证和权限控制
- **缓存优化**：Redis缓存提升性能
- **监控告警**：完整的监控和指标体系

### 技术特性

- **高性能**：基于FastAPI的异步架构
- **可扩展**：微服务架构，支持水平扩展
- **安全可靠**：完整的认证授权和数据加密
- **监控完善**：Prometheus指标和健康检查
- **文档完整**：自动生成的API文档和示例

### 认证方式

API使用JWT令牌进行认证。请在请求头中包含：
```
Authorization: Bearer <your-jwt-token>
```

### 错误处理

API使用标准HTTP状态码，错误响应格式：
```json
{
    "error": "error_type",
    "message": "详细错误信息"
}
```

### 限流

API实施限流保护：
- 每分钟最多100个请求
- 超出限制将返回429状态码

### 联系方式

- **开发团队**：索克生活技术团队
- **邮箱**：dev@suoke.life
- **文档**：https://github.com/SUOKE2024/suoke_life
        """,
        routes=app.routes,
        servers=[
            {
                "url": f"http://localhost:{settings.api.port}",
                "description": "开发环境"
            },
            {
                "url": "https://api.suoke.life",
                "description": "生产环境"
            }
        ]
    )
    
    # 添加安全定义
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT令牌认证"
        }
    }
    
    # 为需要认证的路径添加安全要求
    for path_item in openapi_schema["paths"].values():
        for operation in path_item.values():
            if isinstance(operation, dict) and "tags" in operation:
                # 除了认证和健康检查端点，其他都需要认证
                if not any(tag in ["认证", "健康检查", "监控"] for tag in operation.get("tags", [])):
                    operation["security"] = [{"BearerAuth": []}]
    
    # 添加示例
    add_examples_to_schema(openapi_schema)
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


def add_examples_to_schema(openapi_schema: Dict[str, Any]) -> None:
    """为API模式添加示例"""
    
    # 健康数据创建示例
    if "/api/v1/health-data" in openapi_schema["paths"]:
        post_operation = openapi_schema["paths"]["/api/v1/health-data"].get("post", {})
        if "requestBody" in post_operation:
            post_operation["requestBody"]["content"]["application/json"]["examples"] = {
                "vital_signs": {
                    "summary": "生命体征数据",
                    "description": "创建生命体征健康数据的示例",
                    "value": {
                        "user_id": 1,
                        "data_type": "vital_signs",
                        "data_source": "device",
                        "raw_data": {
                            "heart_rate": 72,
                            "blood_pressure_systolic": 120,
                            "blood_pressure_diastolic": 80,
                            "body_temperature": 36.5
                        },
                        "device_id": "apple_watch_001",
                        "tags": ["morning", "resting"]
                    }
                },
                "blood_test": {
                    "summary": "血液检测数据",
                    "description": "创建血液检测健康数据的示例",
                    "value": {
                        "user_id": 1,
                        "data_type": "blood_test",
                        "data_source": "hospital",
                        "raw_data": {
                            "glucose": 5.6,
                            "cholesterol": 4.2,
                            "hemoglobin": 14.5,
                            "white_blood_cells": 6.8
                        },
                        "location": "北京协和医院",
                        "tags": ["fasting", "annual_checkup"]
                    }
                }
            }
    
    # 生命体征创建示例
    if "/api/v1/health-data/vital-signs" in openapi_schema["paths"]:
        post_operation = openapi_schema["paths"]["/api/v1/health-data/vital-signs"].get("post", {})
        if "requestBody" in post_operation:
            post_operation["requestBody"]["content"]["application/json"]["examples"] = {
                "complete_vitals": {
                    "summary": "完整生命体征",
                    "description": "包含所有生命体征指标的示例",
                    "value": {
                        "user_id": 1,
                        "heart_rate": 72,
                        "blood_pressure_systolic": 120,
                        "blood_pressure_diastolic": 80,
                        "body_temperature": 36.5,
                        "respiratory_rate": 16,
                        "oxygen_saturation": 98.5,
                        "weight": 70.5,
                        "height": 175.0,
                        "device_id": "smart_scale_001",
                        "notes": "晨起测量"
                    }
                },
                "basic_vitals": {
                    "summary": "基础生命体征",
                    "description": "只包含基本指标的示例",
                    "value": {
                        "user_id": 1,
                        "heart_rate": 68,
                        "blood_pressure_systolic": 118,
                        "blood_pressure_diastolic": 78,
                        "device_id": "blood_pressure_monitor_001"
                    }
                }
            }
    
    # 用户注册示例
    if "/api/v1/auth/register" in openapi_schema["paths"]:
        post_operation = openapi_schema["paths"]["/api/v1/auth/register"].get("post", {})
        if "requestBody" in post_operation:
            post_operation["requestBody"]["content"]["application/json"]["examples"] = {
                "user_registration": {
                    "summary": "用户注册",
                    "description": "新用户注册示例",
                    "value": {
                        "username": "zhangsan",
                        "email": "zhangsan@example.com",
                        "password": "SecurePassword123!",
                        "full_name": "张三",
                        "phone": "13800138000"
                    }
                }
            }
    
    # 用户登录示例
    if "/api/v1/auth/login" in openapi_schema["paths"]:
        post_operation = openapi_schema["paths"]["/api/v1/auth/login"].get("post", {})
        if "requestBody" in post_operation:
            post_operation["requestBody"]["content"]["application/json"]["examples"] = {
                "username_login": {
                    "summary": "用户名登录",
                    "description": "使用用户名和密码登录",
                    "value": {
                        "username": "zhangsan",
                        "password": "SecurePassword123!"
                    }
                },
                "email_login": {
                    "summary": "邮箱登录",
                    "description": "使用邮箱和密码登录",
                    "value": {
                        "email": "zhangsan@example.com",
                        "password": "SecurePassword123!"
                    }
                }
            }


def get_custom_swagger_ui_html(
    openapi_url: str,
    title: str,
    swagger_js_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
    swagger_css_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
    swagger_favicon_url: str = "https://fastapi.tiangolo.com/img/favicon.png",
) -> HTMLResponse:
    """生成自定义Swagger UI HTML"""
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <link rel="stylesheet" type="text/css" href="{swagger_css_url}" />
        <link rel="icon" type="image/png" href="{swagger_favicon_url}" />
        <style>
            .swagger-ui .topbar {{
                background-color: #1f2937;
            }}
            .swagger-ui .topbar .download-url-wrapper .select-label {{
                color: #ffffff;
            }}
            .swagger-ui .info .title {{
                color: #1f2937;
            }}
            .swagger-ui .scheme-container {{
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 4px;
                padding: 10px;
                margin: 10px 0;
            }}
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="{swagger_js_url}"></script>
        <script>
            const ui = SwaggerUIBundle({{
                url: '{openapi_url}',
                dom_id: '#swagger-ui',
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.presets.standalone
                ],
                layout: "StandaloneLayout",
                deepLinking: true,
                showExtensions: true,
                showCommonExtensions: true,
                tryItOutEnabled: true,
                requestInterceptor: function(request) {{
                    // 自动添加认证头
                    const token = localStorage.getItem('jwt_token');
                    if (token) {{
                        request.headers['Authorization'] = 'Bearer ' + token;
                    }}
                    return request;
                }},
                onComplete: function() {{
                    // 添加认证按钮
                    const authButton = document.createElement('button');
                    authButton.innerHTML = '设置JWT令牌';
                    authButton.style.cssText = 'position: fixed; top: 10px; right: 10px; z-index: 9999; padding: 8px 16px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;';
                    authButton.onclick = function() {{
                        const token = prompt('请输入JWT令牌:');
                        if (token) {{
                            localStorage.setItem('jwt_token', token);
                            alert('JWT令牌已设置');
                        }}
                    }};
                    document.body.appendChild(authButton);
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html)


def get_custom_redoc_html(
    openapi_url: str,
    title: str,
    redoc_js_url: str = "https://cdn.jsdelivr.net/npm/redoc@2.1.3/bundles/redoc.standalone.js",
    redoc_favicon_url: str = "https://fastapi.tiangolo.com/img/favicon.png",
) -> HTMLResponse:
    """生成自定义ReDoc HTML"""
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="icon" type="image/png" href="{redoc_favicon_url}" />
        <style>
            body {{
                margin: 0;
                padding: 0;
            }}
        </style>
    </head>
    <body>
        <redoc spec-url="{openapi_url}"></redoc>
        <script src="{redoc_js_url}"></script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html)


def setup_docs(app: FastAPI) -> None:
    """设置API文档"""
    
    # 设置自定义OpenAPI生成器
    app.openapi = lambda: custom_openapi(app)
    
    # 自定义文档路由
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_custom_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=f"{app.title} - Swagger UI"
        )
    
    @app.get("/redoc", include_in_schema=False)
    async def custom_redoc_html():
        return get_custom_redoc_html(
            openapi_url=app.openapi_url,
            title=f"{app.title} - ReDoc"
        )


def generate_api_examples() -> Dict[str, Any]:
    """生成API使用示例"""
    return {
        "authentication": {
            "description": "认证示例",
            "examples": {
                "register": {
                    "method": "POST",
                    "url": "/api/v1/auth/register",
                    "body": {
                        "username": "testuser",
                        "email": "test@example.com",
                        "password": "SecurePassword123!",
                        "full_name": "测试用户"
                    }
                },
                "login": {
                    "method": "POST",
                    "url": "/api/v1/auth/login",
                    "body": {
                        "username": "testuser",
                        "password": "SecurePassword123!"
                    }
                }
            }
        },
        "health_data": {
            "description": "健康数据管理示例",
            "examples": {
                "create_vital_signs": {
                    "method": "POST",
                    "url": "/api/v1/health-data",
                    "headers": {
                        "Authorization": "Bearer <jwt-token>"
                    },
                    "body": {
                        "user_id": 1,
                        "data_type": "vital_signs",
                        "data_source": "device",
                        "raw_data": {
                            "heart_rate": 72,
                            "blood_pressure": "120/80"
                        }
                    }
                },
                "get_user_data": {
                    "method": "GET",
                    "url": "/api/v1/health-data?user_id=1&limit=10",
                    "headers": {
                        "Authorization": "Bearer <jwt-token>"
                    }
                }
            }
        },
        "vital_signs": {
            "description": "生命体征管理示例",
            "examples": {
                "create_vital_signs": {
                    "method": "POST",
                    "url": "/api/v1/health-data/vital-signs",
                    "headers": {
                        "Authorization": "Bearer <jwt-token>"
                    },
                    "body": {
                        "user_id": 1,
                        "heart_rate": 72,
                        "blood_pressure_systolic": 120,
                        "blood_pressure_diastolic": 80,
                        "body_temperature": 36.5
                    }
                }
            }
        }
    } 