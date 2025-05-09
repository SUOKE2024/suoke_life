# 认证 API

## 概述

认证API提供用户注册、登录、令牌刷新和注销等功能。所有认证API均通过HTTPS协议提供服务，使用JSON格式进行数据交换。

## 基础端点

```
https://api.suoke.life/api/v1/auth
```

## 接口列表

### 用户注册

创建新用户账户。

**请求**

```
POST /api/v1/auth/register
Content-Type: application/json
```

**请求参数**

| 参数名 | 类型 | 必选 | 描述 |
|-------|-----|------|-----|
| name | string | 是 | 用户姓名，2-30个字符 |
| phoneNumber | string | 是* | 手机号码，必须符合标准格式（*手机号与邮箱必须提供一个） |
| email | string | 是* | 电子邮箱，必须符合标准格式（*手机号与邮箱必须提供一个） |
| password | string | 是 | 密码，8-20个字符，必须包含字母和数字 |
| verificationCode | string | 是 | 验证码，通过短信或邮件获取 |

**请求示例**

```json
{
  "name": "张三",
  "phoneNumber": "13812345678",
  "email": "zhangsan@example.com",
  "password": "Password123",
  "verificationCode": "123456"
}
```

**响应**

```
Status: 201 Created
Content-Type: application/json
```

**响应字段**

| 字段名 | 类型 | 描述 |
|-------|-----|------|
| id | string | 用户唯一标识 |
| name | string | 用户姓名 |
| phoneNumber | string | 手机号码（如有） |
| email | string | 电子邮箱（如有） |
| createdAt | string | 创建时间，ISO 8601格式 |

**响应示例**

```json
{
  "id": "usr_123456789",
  "name": "张三",
  "phoneNumber": "13812345678",
  "email": "zhangsan@example.com",
  "createdAt": "2024-07-15T08:00:00Z"
}
```

**错误响应**

| HTTP状态码 | 错误码 | 描述 |
|-----------|-------|------|
| 400 | INVALID_PARAMS | 请求参数无效 |
| 400 | VERIFICATION_FAILED | 验证码无效或已过期 |
| 409 | ACCOUNT_EXISTS | 手机号或邮箱已被注册 |

### 发送验证码

发送注册或重置密码的验证码。

**请求**

```
POST /api/v1/auth/verification-code
Content-Type: application/json
```

**请求参数**

| 参数名 | 类型 | 必选 | 描述 |
|-------|-----|------|-----|
| recipient | string | 是 | 接收者手机号或邮箱 |
| purpose | string | 是 | 用途，可选值：register（注册）、reset_password（重置密码） |

**请求示例**

```json
{
  "recipient": "13812345678",
  "purpose": "register"
}
```

**响应**

```
Status: 200 OK
Content-Type: application/json
```

**响应字段**

| 字段名 | 类型 | 描述 |
|-------|-----|------|
| success | boolean | 是否成功发送 |
| expiresIn | number | 验证码有效期（秒） |

**响应示例**

```json
{
  "success": true,
  "expiresIn": 300
}
```

**错误响应**

| HTTP状态码 | 错误码 | 描述 |
|-----------|-------|------|
| 400 | INVALID_RECIPIENT | 接收者格式无效 |
| 400 | INVALID_PURPOSE | 用途参数无效 |
| 429 | TOO_MANY_REQUESTS | 发送请求过于频繁 |

### 用户登录

用户账号密码登录，获取访问令牌。

**请求**

```
POST /api/v1/auth/login
Content-Type: application/json
```

**请求参数**

| 参数名 | 类型 | 必选 | 描述 |
|-------|-----|------|-----|
| phoneOrEmail | string | 是 | 用户手机号或邮箱 |
| password | string | 是 | 用户密码 |
| deviceInfo | object | 否 | 设备信息 |

**请求示例**

```json
{
  "phoneOrEmail": "13812345678",
  "password": "Password123",
  "deviceInfo": {
    "deviceId": "unique-device-id",
    "deviceModel": "iPhone 14",
    "osVersion": "iOS 16.5"
  }
}
```

**响应**

```
Status: 200 OK
Content-Type: application/json
```

**响应字段**

| 字段名 | 类型 | 描述 |
|-------|-----|------|
| accessToken | string | 访问令牌 |
| refreshToken | string | 刷新令牌 |
| expiresIn | number | 访问令牌有效期（秒） |
| userId | string | 用户ID |
| tokenType | string | 令牌类型，固定值"Bearer" |

**响应示例**

```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresIn": 3600,
  "userId": "usr_123456789",
  "tokenType": "Bearer"
}
```

**错误响应**

| HTTP状态码 | 错误码 | 描述 |
|-----------|-------|------|
| 400 | INVALID_CREDENTIALS | 账号或密码错误 |
| 403 | ACCOUNT_LOCKED | 账号已被锁定 |
| 403 | ACCOUNT_DISABLED | 账号已被禁用 |

### 刷新令牌

使用刷新令牌获取新的访问令牌。

**请求**

```
POST /api/v1/auth/refresh
Content-Type: application/json
Authorization: Bearer {refreshToken}
```

**请求参数**

| 参数名 | 类型 | 必选 | 描述 |
|-------|-----|------|-----|
| refreshToken | string | 是 | 刷新令牌 |

**请求示例**

```json
{
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**响应**

```
Status: 200 OK
Content-Type: application/json
```

**响应字段**

| 字段名 | 类型 | 描述 |
|-------|-----|------|
| accessToken | string | 新的访问令牌 |
| refreshToken | string | 新的刷新令牌 |
| expiresIn | number | 访问令牌有效期（秒） |
| tokenType | string | 令牌类型，固定值"Bearer" |

**响应示例**

```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresIn": 3600,
  "tokenType": "Bearer"
}
```

**错误响应**

| HTTP状态码 | 错误码 | 描述 |
|-----------|-------|------|
| 401 | INVALID_TOKEN | 刷新令牌无效 |
| 401 | TOKEN_EXPIRED | 刷新令牌已过期 |

### 第三方登录

通过第三方平台授权登录。

**请求**

```
POST /api/v1/auth/third-party
Content-Type: application/json
```

**请求参数**

| 参数名 | 类型 | 必选 | 描述 |
|-------|-----|------|-----|
| provider | string | 是 | 第三方平台，可选值：wechat、apple |
| authCode | string | 是 | 授权码 |
| deviceInfo | object | 否 | 设备信息 |

**请求示例**

```json
{
  "provider": "wechat",
  "authCode": "AUTH_CODE_FROM_WECHAT",
  "deviceInfo": {
    "deviceId": "unique-device-id",
    "deviceModel": "iPhone 14",
    "osVersion": "iOS 16.5"
  }
}
```

**响应**

与登录接口响应相同

**错误响应**

| HTTP状态码 | 错误码 | 描述 |
|-----------|-------|------|
| 400 | INVALID_PROVIDER | 不支持的第三方平台 |
| 401 | AUTH_FAILED | 第三方授权失败 |
| 500 | PROVIDER_ERROR | 第三方平台服务异常 |

### 注销登录

注销当前用户会话。

**请求**

```
POST /api/v1/auth/logout
Content-Type: application/json
Authorization: Bearer {accessToken}
```

**响应**

```
Status: 200 OK
Content-Type: application/json
```

**响应示例**

```json
{
  "success": true
}
```

**错误响应**

| HTTP状态码 | 错误码 | 描述 |
|-----------|-------|------|
| 401 | UNAUTHORIZED | 未授权或token无效 |

### 重置密码

通过验证码重置用户密码。

**请求**

```
POST /api/v1/auth/reset-password
Content-Type: application/json
```

**请求参数**

| 参数名 | 类型 | 必选 | 描述 |
|-------|-----|------|-----|
| phoneOrEmail | string | 是 | 用户手机号或邮箱 |
| verificationCode | string | 是 | 验证码 |
| newPassword | string | 是 | 新密码，8-20个字符 |

**请求示例**

```json
{
  "phoneOrEmail": "13812345678",
  "verificationCode": "123456",
  "newPassword": "NewPassword123"
}
```

**响应**

```
Status: 200 OK
Content-Type: application/json
```

**响应示例**

```json
{
  "success": true
}
```

**错误响应**

| HTTP状态码 | 错误码 | 描述 |
|-----------|-------|------|
| 400 | INVALID_PARAMS | 请求参数无效 |
| 400 | VERIFICATION_FAILED | 验证码无效或已过期 |
| 404 | USER_NOT_FOUND | 用户不存在 |

## 数据结构

### 用户认证模型

| 字段名 | 类型 | 描述 |
|-------|-----|------|
| id | string | 用户唯一标识 |
| name | string | 用户姓名 |
| phoneNumber | string | 手机号码 |
| email | string | 电子邮箱 |
| password | string | 加密密码（不返回给客户端） |
| avatarUrl | string | 头像URL |
| status | enum | 账号状态：active、locked、disabled |
| thirdPartyAuths | array | 第三方授权信息数组 |
| createdAt | string | 创建时间 |
| updatedAt | string | 更新时间 |
| lastLoginAt | string | 最后登录时间 |

## 附录

### 请求限制

- 登录失败次数限制：同一账号5分钟内最多5次失败尝试
- 验证码发送限制：同一手机号/邮箱1分钟内最多发送1次，24小时内最多10次
- API请求频率限制：同一IP每分钟最多60次请求

### 安全建议

- 所有API调用必须使用HTTPS
- 客户端应妥善保管令牌
- 建议实现令牌自动刷新机制
- 用户敏感信息传输前应进行加密

---

> 文档最后更新：2024年7月15日 