"""
API文档配置

提供详细的OpenAPI文档配置，包括认证、示例和错误响应。
"""
from typing import Dict, Any, List
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

# API文档配置
API_DOCS_CONFIG = {
    "title": "索克生活认证服务 API",
    "description": """
## 索克生活认证服务

这是索克生活平台的认证服务API，提供用户认证、授权和管理功能。

### 核心功能

- **用户认证**: 支持用户名/邮箱登录，多因子认证
- **令牌管理**: JWT令牌生成、验证和刷新
- **用户管理**: 用户注册、信息更新、状态管理
- **角色权限**: 基于角色的访问控制(RBAC)
- **安全功能**: 密码策略、会话管理、审计日志

### 认证方式

API使用JWT Bearer令牌进行认证。获取令牌后，在请求头中添加：

```
Authorization: Bearer <your_jwt_token>
```

### 速率限制

为了保护服务，API实施了速率限制：

- **登录**: 5分钟内最多5次尝试
- **注册**: 1小时内最多3次注册
- **密码重置**: 1小时内最多3次重置
- **一般API**: 1分钟内最多100次请求
- **敏感API**: 1分钟内最多10次请求

### 错误处理

API使用标准HTTP状态码，错误响应格式：

```json
{
    "error": "error_code",
    "message": "人类可读的错误信息",
    "details": {
        "field": "具体错误详情"
    }
}
```

### 版本控制

当前API版本: v1

所有API端点都以 `/api/v1` 开头。
    """,
    "version": "1.0.0",
    "contact": {
        "name": "索克生活开发团队",
        "email": "dev@suoke.life",
        "url": "https://suoke.life"
    },
    "license": {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    "servers": [
        {
            "url": "http://localhost:8001",
            "description": "开发环境"
        },
        {
            "url": "https://auth-api.suoke.life",
            "description": "生产环境"
        }
    ]
}

# 通用响应模式
COMMON_RESPONSES = {
    400: {
        "description": "请求参数错误",
        "content": {
            "application/json": {
                "example": {
                    "error": "validation_error",
                    "message": "请求参数验证失败",
                    "details": {
                        "username": "用户名长度不能少于3个字符"
                    }
                }
            }
        }
    },
    401: {
        "description": "未授权访问",
        "content": {
            "application/json": {
                "example": {
                    "error": "unauthorized",
                    "message": "访问令牌无效或已过期"
                }
            }
        }
    },
    403: {
        "description": "权限不足",
        "content": {
            "application/json": {
                "example": {
                    "error": "forbidden",
                    "message": "权限不足，无法访问此资源"
                }
            }
        }
    },
    404: {
        "description": "资源不存在",
        "content": {
            "application/json": {
                "example": {
                    "error": "not_found",
                    "message": "请求的资源不存在"
                }
            }
        }
    },
    429: {
        "description": "请求过于频繁",
        "content": {
            "application/json": {
                "example": {
                    "error": "rate_limit_exceeded",
                    "message": "请求过于频繁，请稍后再试",
                    "details": {
                        "retry_after": 60,
                        "limit": 5,
                        "window": 300
                    }
                }
            }
        }
    },
    500: {
        "description": "服务器内部错误",
        "content": {
            "application/json": {
                "example": {
                    "error": "internal_error",
                    "message": "服务器内部错误，请稍后重试"
                }
            }
        }
    }
}

# 认证相关的API文档
AUTH_DOCS = {
    "login": {
        "summary": "用户登录",
        "description": """
用户登录接口，支持用户名或邮箱登录。

### 功能特性
- 支持用户名或邮箱登录
- 自动检测登录方式
- 返回访问令牌和刷新令牌
- 记录登录日志和设备信息

### 安全措施
- 密码强度验证
- 登录失败次数限制
- IP地址记录
- 设备指纹识别
        """,
        "responses": {
            200: {
                "description": "登录成功",
                "content": {
                    "application/json": {
                        "example": {
                            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...",
                            "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...",
                            "token_type": "bearer",
                            "expires_in": 1800,
                            "user": {
                                "id": "123e4567-e89b-12d3-a456-426614174000",
                                "username": "john_doe",
                                "email": "john@example.com",
                                "roles": ["user"]
                            }
                        }
                    }
                }
            },
            **COMMON_RESPONSES
        }
    },
    "register": {
        "summary": "用户注册",
        "description": """
用户注册接口，创建新用户账户。

### 注册流程
1. 验证用户输入数据
2. 检查用户名和邮箱唯一性
3. 验证密码强度
4. 创建用户账户
5. 发送验证邮件（可选）

### 密码要求
- 最少8个字符
- 包含大小写字母
- 包含数字
- 包含特殊字符
        """,
        "responses": {
            201: {
                "description": "注册成功",
                "content": {
                    "application/json": {
                        "example": {
                            "user": {
                                "id": "123e4567-e89b-12d3-a456-426614174000",
                                "username": "new_user",
                                "email": "new@example.com",
                                "is_active": True,
                                "created_at": "2024-01-01T00:00:00Z"
                            },
                            "message": "注册成功，请查收验证邮件"
                        }
                    }
                }
            },
            **COMMON_RESPONSES
        }
    },
    "refresh_token": {
        "summary": "刷新访问令牌",
        "description": """
使用刷新令牌获取新的访问令牌。

### 使用场景
- 访问令牌即将过期
- 访问令牌已过期但刷新令牌仍有效
- 定期更新令牌以提高安全性

### 令牌生命周期
- 访问令牌: 30分钟
- 刷新令牌: 7天
        """,
        "responses": {
            200: {
                "description": "令牌刷新成功",
                "content": {
                    "application/json": {
                        "example": {
                            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...",
                            "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...",
                            "token_type": "bearer",
                            "expires_in": 1800
                        }
                    }
                }
            },
            **COMMON_RESPONSES
        }
    },
    "logout": {
        "summary": "用户登出",
        "description": """
用户登出接口，撤销当前会话。

### 登出操作
- 撤销当前访问令牌
- 撤销关联的刷新令牌
- 清理会话数据
- 记录登出日志
        """,
        "responses": {
            200: {
                "description": "登出成功",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "登出成功"
                        }
                    }
                }
            },
            **COMMON_RESPONSES
        }
    }
}

# 用户管理相关的API文档
USER_DOCS = {
    "get_profile": {
        "summary": "获取用户资料",
        "description": """
获取当前用户的详细资料信息。

### 返回信息
- 基本信息（用户名、邮箱等）
- 角色和权限
- 账户状态
- 最后登录时间
- 个人资料数据
        """,
        "responses": {
            200: {
                "description": "获取成功",
                "content": {
                    "application/json": {
                        "example": {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "username": "john_doe",
                            "email": "john@example.com",
                            "phone_number": "+1234567890",
                            "is_active": True,
                            "is_verified": True,
                            "roles": ["user"],
                            "permissions": ["read:profile", "update:profile"],
                            "profile_data": {
                                "first_name": "John",
                                "last_name": "Doe",
                                "avatar_url": "https://example.com/avatar.jpg"
                            },
                            "created_at": "2024-01-01T00:00:00Z",
                            "updated_at": "2024-01-01T00:00:00Z",
                            "last_login": "2024-01-01T12:00:00Z"
                        }
                    }
                }
            },
            **COMMON_RESPONSES
        }
    },
    "update_profile": {
        "summary": "更新用户资料",
        "description": """
更新当前用户的资料信息。

### 可更新字段
- 用户名（需要验证唯一性）
- 邮箱（需要重新验证）
- 手机号码
- 个人资料数据

### 验证规则
- 用户名: 3-30个字符，只能包含字母、数字、下划线
- 邮箱: 有效的邮箱格式
- 手机号: E.164格式
        """,
        "responses": {
            200: {
                "description": "更新成功",
                "content": {
                    "application/json": {
                        "example": {
                            "user": {
                                "id": "123e4567-e89b-12d3-a456-426614174000",
                                "username": "john_doe_updated",
                                "email": "john.new@example.com",
                                "updated_at": "2024-01-01T12:00:00Z"
                            },
                            "message": "资料更新成功"
                        }
                    }
                }
            },
            **COMMON_RESPONSES
        }
    }
}

# MFA相关的API文档
MFA_DOCS = {
    "setup_totp": {
        "summary": "设置TOTP多因子认证",
        "description": """
为用户账户设置基于时间的一次性密码(TOTP)认证。

### 设置流程
1. 生成TOTP密钥
2. 返回二维码和备份码
3. 用户扫描二维码
4. 验证TOTP代码
5. 启用MFA

### 支持的应用
- Google Authenticator
- Microsoft Authenticator
- Authy
- 其他兼容TOTP的应用
        """,
        "responses": {
            200: {
                "description": "TOTP设置成功",
                "content": {
                    "application/json": {
                        "example": {
                            "secret": "JBSWY3DPEHPK3PXP",
                            "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
                            "backup_codes": [
                                "12345678",
                                "87654321",
                                "11223344"
                            ],
                            "message": "请使用认证应用扫描二维码"
                        }
                    }
                }
            },
            **COMMON_RESPONSES
        }
    },
    "verify_totp": {
        "summary": "验证TOTP代码",
        "description": """
验证用户输入的TOTP验证码。

### 验证规则
- 6位数字代码
- 30秒有效期
- 允许时间偏移（±1个周期）
- 防重放攻击
        """,
        "responses": {
            200: {
                "description": "验证成功",
                "content": {
                    "application/json": {
                        "example": {
                            "verified": True,
                            "message": "TOTP验证成功"
                        }
                    }
                }
            },
            **COMMON_RESPONSES
        }
    }
}

# 管理员API文档
ADMIN_DOCS = {
    "list_users": {
        "summary": "获取用户列表",
        "description": """
获取系统中所有用户的列表（管理员权限）。

### 查询参数
- page: 页码（默认1）
- size: 每页数量（默认20，最大100）
- search: 搜索关键词（用户名或邮箱）
- role: 按角色筛选
- status: 按状态筛选（active/inactive）

### 排序选项
- created_at: 按创建时间排序
- last_login: 按最后登录时间排序
- username: 按用户名排序
        """,
        "responses": {
            200: {
                "description": "获取成功",
                "content": {
                    "application/json": {
                        "example": {
                            "users": [
                                {
                                    "id": "123e4567-e89b-12d3-a456-426614174000",
                                    "username": "john_doe",
                                    "email": "john@example.com",
                                    "is_active": True,
                                    "roles": ["user"],
                                    "created_at": "2024-01-01T00:00:00Z",
                                    "last_login": "2024-01-01T12:00:00Z"
                                }
                            ],
                            "pagination": {
                                "page": 1,
                                "size": 20,
                                "total": 100,
                                "pages": 5
                            }
                        }
                    }
                }
            },
            **COMMON_RESPONSES
        }
    }
}

def customize_openapi(app: FastAPI) -> Dict[str, Any]:
    """自定义OpenAPI文档"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=API_DOCS_CONFIG["title"],
        version=API_DOCS_CONFIG["version"],
        description=API_DOCS_CONFIG["description"],
        routes=app.routes,
        servers=API_DOCS_CONFIG["servers"]
    )
    
    # 添加安全方案
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT访问令牌"
        }
    }
    
    # 添加全局安全要求
    openapi_schema["security"] = [{"BearerAuth": []}]
    
    # 添加联系信息和许可证
    openapi_schema["info"]["contact"] = API_DOCS_CONFIG["contact"]
    openapi_schema["info"]["license"] = API_DOCS_CONFIG["license"]
    
    # 添加标签
    openapi_schema["tags"] = [
        {
            "name": "认证",
            "description": "用户认证相关接口"
        },
        {
            "name": "用户管理",
            "description": "用户资料管理接口"
        },
        {
            "name": "多因子认证",
            "description": "MFA设置和验证接口"
        },
        {
            "name": "管理员",
            "description": "管理员专用接口"
        },
        {
            "name": "系统",
            "description": "系统状态和监控接口"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


# API示例数据
EXAMPLE_DATA = {
    "login_request": {
        "username": "john_doe",
        "password": "SecurePassword123!"
    },
    "register_request": {
        "username": "new_user",
        "email": "new@example.com",
        "password": "SecurePassword123!",
        "phone_number": "+1234567890",
        "profile_data": {
            "first_name": "New",
            "last_name": "User"
        }
    },
    "update_profile_request": {
        "username": "updated_username",
        "email": "updated@example.com",
        "phone_number": "+0987654321",
        "profile_data": {
            "first_name": "Updated",
            "last_name": "Name",
            "bio": "Updated bio"
        }
    },
    "change_password_request": {
        "current_password": "OldPassword123!",
        "new_password": "NewPassword123!"
    },
    "mfa_verify_request": {
        "code": "123456"
    }
}

# 错误代码说明
ERROR_CODES = {
    "validation_error": "请求参数验证失败",
    "authentication_failed": "用户名或密码错误",
    "user_not_found": "用户不存在",
    "user_inactive": "用户账户已禁用",
    "token_expired": "令牌已过期",
    "token_invalid": "令牌无效",
    "permission_denied": "权限不足",
    "rate_limit_exceeded": "请求过于频繁",
    "username_taken": "用户名已被使用",
    "email_taken": "邮箱已被使用",
    "password_too_weak": "密码强度不足",
    "mfa_required": "需要多因子认证",
    "mfa_invalid": "MFA验证码无效",
    "internal_error": "服务器内部错误"
} 