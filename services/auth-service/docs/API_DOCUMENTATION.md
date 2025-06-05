# Auth-Service API 文档

## 概述

Auth-Service 是索克生活项目的认证服务，提供用户认证、授权、会话管理等核心功能。

### 基础信息

- **服务名称**: auth-service
- **版本**: v1.0.0
- **基础URL**: `https://api.suokelife.com/auth`
- **协议**: HTTPS
- **认证方式**: JWT Bearer Token

### 技术栈

- **框架**: FastAPI
- **数据库**: PostgreSQL
- **缓存**: Redis
- **认证**: JWT + MFA (TOTP)
- **OAuth**: Google, WeChat, Apple

## 认证机制

### JWT Token

所有需要认证的API都需要在请求头中包含JWT令牌：

```http
Authorization: Bearer <access_token>
```

### Token 类型

1. **Access Token**: 用于API访问，有效期1小时
2. **Refresh Token**: 用于刷新Access Token，有效期30天

### 错误响应格式

```json
{
  "error": "error_code",
  "message": "错误描述",
  "details": {
    "field": "具体错误信息"
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "request_id": "uuid"
}
```

## API 端点

### 1. 用户注册

注册新用户账户。

**端点**: `POST /api/v1/auth/register`

**请求体**:
```json
{
  "username": "string",
  "email": "string",
  "phone": "string",
  "password": "string",
  "confirm_password": "string",
  "invitation_code": "string"
}
```

**字段说明**:
- `username`: 用户名，3-20字符，只能包含字母、数字、下划线
- `email`: 邮箱地址，必须是有效的邮箱格式
- `phone`: 手机号，中国大陆手机号格式
- `password`: 密码，8-128字符，必须包含大小写字母、数字和特殊字符
- `confirm_password`: 确认密码，必须与password一致
- `invitation_code`: 邀请码（可选）

**响应**:
```json
{
  "user_id": "string",
  "username": "string",
  "email": "string",
  "phone": "string",
  "status": "pending_verification",
  "created_at": "2024-01-01T00:00:00Z",
  "verification_required": true,
  "verification_methods": ["email", "sms"]
}
```

**状态码**:
- `201`: 注册成功
- `400`: 请求参数错误
- `409`: 用户名、邮箱或手机号已存在
- `429`: 请求过于频繁

### 2. 用户登录

用户身份验证和会话创建。

**端点**: `POST /api/v1/auth/login`

**请求体**:
```json
{
  "username": "string",
  "password": "string",
  "device_id": "string",
  "device_name": "string",
  "remember_me": false,
  "mfa_token": "string"
}
```

**字段说明**:
- `username`: 用户名、邮箱或手机号
- `password`: 密码
- `device_id`: 设备唯一标识符
- `device_name`: 设备名称（如"iPhone 15"）
- `remember_me`: 是否记住登录状态
- `mfa_token`: MFA验证码（如果启用了MFA）

**响应**:

成功登录（无需MFA）:
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user_id": "string",
  "username": "string",
  "mfa_required": false,
  "session_id": "string"
}
```

需要MFA验证:
```json
{
  "mfa_required": true,
  "user_id": "string",
  "username": "string",
  "mfa_methods": ["totp", "sms"],
  "session_token": "string"
}
```

**状态码**:
- `200`: 登录成功
- `401`: 用户名或密码错误
- `423`: 账户被锁定
- `429`: 请求过于频繁

### 3. MFA验证

多因素认证验证。

**端点**: `POST /api/v1/auth/verify-mfa`

**请求体**:
```json
{
  "session_token": "string",
  "mfa_token": "string",
  "mfa_method": "totp"
}
```

**响应**:
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user_id": "string",
  "username": "string",
  "session_id": "string"
}
```

**状态码**:
- `200`: 验证成功
- `401`: MFA令牌无效
- `429`: 请求过于频繁

### 4. 刷新令牌

使用refresh token获取新的access token。

**端点**: `POST /api/v1/auth/refresh`

**请求体**:
```json
{
  "refresh_token": "string"
}
```

**响应**:
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**状态码**:
- `200`: 刷新成功
- `401`: Refresh token无效或过期

### 5. 用户登出

终止用户会话。

**端点**: `POST /api/v1/auth/logout`

**请求头**: `Authorization: Bearer <access_token>`

**请求体**:
```json
{
  "all_devices": false
}
```

**响应**:
```json
{
  "message": "登出成功",
  "logged_out_sessions": 1
}
```

**状态码**:
- `200`: 登出成功
- `401`: 令牌无效

### 6. 忘记密码

发起密码重置流程。

**端点**: `POST /api/v1/auth/forgot-password`

**请求体**:
```json
{
  "email": "string"
}
```

**响应**:
```json
{
  "message": "密码重置邮件已发送",
  "reset_token_expires_in": 3600
}
```

**状态码**:
- `200`: 重置邮件已发送
- `404`: 邮箱不存在
- `429`: 请求过于频繁

### 7. 重置密码

使用重置令牌重置密码。

**端点**: `POST /api/v1/auth/reset-password`

**请求体**:
```json
{
  "reset_token": "string",
  "new_password": "string",
  "confirm_password": "string"
}
```

**响应**:
```json
{
  "message": "密码重置成功",
  "user_id": "string"
}
```

**状态码**:
- `200`: 重置成功
- `400`: 令牌无效或密码不符合要求
- `410`: 令牌已过期

### 8. 修改密码

修改当前用户密码。

**端点**: `POST /api/v1/auth/change-password`

**请求头**: `Authorization: Bearer <access_token>`

**请求体**:
```json
{
  "current_password": "string",
  "new_password": "string",
  "confirm_password": "string"
}
```

**响应**:
```json
{
  "message": "密码修改成功"
}
```

**状态码**:
- `200`: 修改成功
- `400`: 当前密码错误或新密码不符合要求
- `401`: 令牌无效

### 9. 启用MFA

为用户账户启用多因素认证。

**端点**: `POST /api/v1/auth/enable-mfa`

**请求头**: `Authorization: Bearer <access_token>`

**请求体**:
```json
{
  "mfa_method": "totp",
  "verification_token": "string"
}
```

**响应**:
```json
{
  "message": "MFA已启用",
  "backup_codes": [
    "12345678",
    "87654321"
  ],
  "qr_code_url": "otpauth://totp/..."
}
```

**状态码**:
- `200`: 启用成功
- `400`: 验证令牌无效
- `401`: 令牌无效

### 10. 禁用MFA

禁用用户账户的多因素认证。

**端点**: `POST /api/v1/auth/disable-mfa`

**请求头**: `Authorization: Bearer <access_token>`

**请求体**:
```json
{
  "password": "string",
  "mfa_token": "string"
}
```

**响应**:
```json
{
  "message": "MFA已禁用"
}
```

**状态码**:
- `200`: 禁用成功
- `400`: 密码或MFA令牌无效
- `401`: 令牌无效

### 11. OAuth登录

第三方OAuth登录。

**端点**: `GET /api/v1/auth/oauth/{provider}/authorize`

**路径参数**:
- `provider`: OAuth提供商（google, wechat, apple）

**查询参数**:
- `redirect_uri`: 回调地址
- `state`: 状态参数

**响应**: 重定向到OAuth提供商授权页面

**端点**: `POST /api/v1/auth/oauth/{provider}/callback`

**请求体**:
```json
{
  "code": "string",
  "state": "string"
}
```

**响应**:
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user_id": "string",
  "username": "string",
  "is_new_user": false
}
```

### 12. 验证令牌

验证访问令牌的有效性。

**端点**: `POST /api/v1/auth/verify-token`

**请求头**: `Authorization: Bearer <access_token>`

**响应**:
```json
{
  "valid": true,
  "user_id": "string",
  "username": "string",
  "expires_at": "2024-01-01T01:00:00Z",
  "scopes": ["read", "write"]
}
```

**状态码**:
- `200`: 令牌有效
- `401`: 令牌无效或过期

### 13. 获取用户会话

获取当前用户的所有活跃会话。

**端点**: `GET /api/v1/auth/sessions`

**请求头**: `Authorization: Bearer <access_token>`

**响应**:
```json
{
  "sessions": [
    {
      "session_id": "string",
      "device_id": "string",
      "device_name": "string",
      "ip_address": "string",
      "location": "string",
      "created_at": "2024-01-01T00:00:00Z",
      "last_active_at": "2024-01-01T00:30:00Z",
      "is_current": true
    }
  ],
  "total": 1
}
```

### 14. 撤销会话

撤销指定的用户会话。

**端点**: `DELETE /api/v1/auth/sessions/{session_id}`

**请求头**: `Authorization: Bearer <access_token>`

**响应**:
```json
{
  "message": "会话已撤销"
}
```

**状态码**:
- `200`: 撤销成功
- `404`: 会话不存在
- `401`: 令牌无效

## 错误代码

| 错误代码 | HTTP状态码 | 描述 |
|---------|-----------|------|
| `invalid_credentials` | 401 | 用户名或密码错误 |
| `account_locked` | 423 | 账户被锁定 |
| `account_disabled` | 403 | 账户被禁用 |
| `mfa_required` | 200 | 需要MFA验证 |
| `invalid_mfa_token` | 401 | MFA令牌无效 |
| `token_expired` | 401 | 令牌已过期 |
| `invalid_token` | 401 | 令牌无效 |
| `rate_limit_exceeded` | 429 | 请求过于频繁 |
| `validation_error` | 400 | 请求参数验证失败 |
| `user_exists` | 409 | 用户已存在 |
| `user_not_found` | 404 | 用户不存在 |
| `password_too_weak` | 400 | 密码强度不够 |
| `oauth_error` | 400 | OAuth认证失败 |

## 限流规则

| 端点 | 限制 | 时间窗口 |
|------|------|---------|
| `/auth/login` | 5次 | 5分钟 |
| `/auth/register` | 3次 | 1小时 |
| `/auth/forgot-password` | 3次 | 1小时 |
| `/auth/verify-mfa` | 10次 | 5分钟 |
| `/auth/refresh` | 20次 | 1小时 |
| 全局（每IP） | 100次 | 1小时 |
| 全局（每用户） | 1000次 | 1小时 |

## 安全特性

### 密码策略

- 最小长度：8字符
- 最大长度：128字符
- 必须包含：大写字母、小写字母、数字、特殊字符
- 不能包含：用户名、邮箱、常见密码

### 账户锁定

- 连续5次登录失败后锁定账户
- 锁定时间：30分钟
- 管理员可手动解锁

### 会话管理

- Access Token有效期：1小时
- Refresh Token有效期：30天
- 支持多设备同时登录
- 支持强制登出所有设备

### 安全头

所有响应都包含以下安全头：

```http
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
Referrer-Policy: strict-origin-when-cross-origin
```

## SDK 和示例

### JavaScript SDK

```javascript
import { AuthClient } from '@suokelife/auth-sdk';

const auth = new AuthClient({
  baseURL: 'https://api.suokelife.com/auth',
  clientId: 'your-client-id'
});

// 登录
const result = await auth.login({
  username: 'user@example.com',
  password: 'password123',
  deviceId: 'device-uuid',
  deviceName: 'iPhone 15'
});

// 刷新令牌
const newTokens = await auth.refreshToken(refreshToken);

// 登出
await auth.logout();
```

### Python SDK

```python
from suokelife_auth import AuthClient

auth = AuthClient(
    base_url='https://api.suokelife.com/auth',
    client_id='your-client-id'
)

# 登录
result = auth.login(
    username='user@example.com',
    password='password123',
    device_id='device-uuid',
    device_name='iPhone 15'
)

# 刷新令牌
new_tokens = auth.refresh_token(refresh_token)

# 登出
auth.logout()
```

## 测试环境

### 测试账户

```
用户名: test@suokelife.com
密码: TestPassword123!
MFA: 已启用
```

### 测试端点

- **基础URL**: `https://api-test.suokelife.com/auth`
- **文档**: `https://api-test.suokelife.com/auth/docs`

## 监控和日志

### 健康检查

**端点**: `GET /health`

**响应**:
```json
{
  "status": "healthy",
  "service": "auth-service",
  "version": "1.0.0",
  "timestamp": "2024-01-01T00:00:00Z",
  "dependencies": {
    "database": "healthy",
    "redis": "healthy"
  }
}
```

### 指标端点

**端点**: `GET /metrics`

提供Prometheus格式的监控指标。

### 日志格式

所有日志都采用JSON格式，包含以下字段：

```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "level": "INFO",
  "service": "auth-service",
  "request_id": "uuid",
  "user_id": "string",
  "event": "login_success",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "message": "用户登录成功"
}
```

## 版本历史

### v1.0.0 (2024-01-01)
- 初始版本发布
- 基础认证功能
- JWT令牌支持
- MFA支持
- OAuth集成

### 联系方式

- **技术支持**: tech-support@suokelife.com
- **API问题**: api-support@suokelife.com
- **文档反馈**: docs@suokelife.com 