# 索克生活APP API通信协议

## 简介

本文档定义了索克生活APP前端应用与后端服务之间的通信协议和标准。遵循这些规范能确保通信的一致性、安全性和可维护性。该协议基于REST架构风格设计，并结合WebSocket实现实时通信需求。

## 目录

1. [API设计原则](#api设计原则)
2. [基础URL结构](#基础url结构)
3. [请求与响应格式](#请求与响应格式)
4. [认证与授权](#认证与授权)
5. [错误处理](#错误处理)
6. [版本控制](#版本控制)
7. [WebSocket通信](#websocket通信)
8. [数据模型](#数据模型)
9. [安全通信策略](#安全通信策略)
10. [API限流与保护](#api限流与保护)
11. [跨平台考量](#跨平台考量)

## API设计原则

我们的API设计遵循以下原则：

### 1. RESTful设计

- 使用HTTP方法语义：GET(读取)，POST(创建)，PUT(更新)，DELETE(删除)
- 资源名使用复数形式：`/users` 而非 `/user`
- 利用HTTP状态码表达结果状态
- 以资源为中心的URL设计

### 2. 一致性

- 参数命名风格统一，使用小驼峰（camelCase）
- 响应结构保持一致
- 错误返回格式统一
- 所有返回在最外层有统一的状态包装

### 3. 安全性

- 所有API调用使用HTTPS
- 敏感数据传输采用端到端加密
- 遵循最小权限原则
- 健康数据采用特殊加密处理

### 4. 文档化

- 所有API端点都有详细文档
- 参数和返回值类型明确定义
- 提供示例请求和响应
- 错误码和含义明确记录

## 基础URL结构

```
https://api.suokelife.com/v{version_number}/{resource}[/{resource_id}][?parameters]
```

示例：
- `https://api.suokelife.com/v1/users`：获取用户列表
- `https://api.suokelife.com/v1/users/123`：获取ID为123的用户
- `https://api.suokelife.com/v1/health-records?userId=123&type=tongue`：获取用户123的舌象记录

### 环境特定基础URL

- 开发环境：`https://dev-api.suokelife.com`
- 测试环境：`https://test-api.suokelife.com`
- 预发布环境：`https://stage-api.suokelife.com`
- 生产环境：`https://api.suokelife.com`

## 请求与响应格式

### 请求格式

#### 请求头

所有请求应包含以下HTTP头：

```
Content-Type: application/json
Accept: application/json
Authorization: Bearer {access_token}
X-Api-Version: 1.0
X-Client-Version: 1.2.3
X-Client-Platform: ios|android|web
X-Request-ID: {unique_request_id}
```

#### 请求体

POST和PUT请求的请求体采用JSON格式：

```json
{
  "key1": "value1",
  "key2": "value2",
  "nestedObject": {
    "nestedKey": "nestedValue"
  },
  "arrayOfItems": [
    {"id": 1, "name": "Item 1"},
    {"id": 2, "name": "Item 2"}
  ]
}
```

### 响应格式

所有API响应使用统一的JSON结构：

```json
{
  "status": "success|error|warning",
  "code": 200,
  "message": "操作成功完成",
  "data": { ... },
  "meta": {
    "pagination": {
      "total": 100,
      "page": 1,
      "perPage": 20,
      "totalPages": 5
    },
    "timestamp": "2024-06-01T12:34:56.789Z",
    "requestId": "req-123456-abcdef"
  }
}
```

- **status**: 操作状态，可能值为"success"、"error"或"warning"
- **code**: HTTP状态码或自定义业务状态码
- **message**: 人类可读的状态说明
- **data**: 响应的主体数据
- **meta**: 元数据如分页信息、服务器时间戳等

### 分页响应

对于返回列表的API，使用统一的分页结构：

```json
{
  "status": "success",
  "code": 200,
  "message": "成功获取健康记录",
  "data": [
    { "id": 1, "type": "tongue", "createdAt": "2024-05-01T09:00:00Z", ... },
    { "id": 2, "type": "pulse", "createdAt": "2024-05-03T10:15:00Z", ... }
  ],
  "meta": {
    "pagination": {
      "total": 57,
      "page": 1,
      "perPage": 20,
      "totalPages": 3,
      "hasNextPage": true,
      "hasPrevPage": false,
      "nextPage": 2,
      "prevPage": null
    }
  }
}
```

列表查询API支持的通用查询参数：

- `page`: 页码，从1开始
- `perPage`: 每页记录数，默认20，最大50
- `sortBy`: 排序字段
- `sortOrder`: 排序方向，`asc`或`desc`
- `search`: 搜索关键词

## 认证与授权

### 认证方式

索克生活API使用基于OAuth 2.0 + JWT的认证机制：

1. **获取访问令牌**

```
POST /v1/auth/token
```

请求体：
```json
{
  "grantType": "password",
  "username": "user@example.com",
  "password": "securePassword123"
}
```

响应：
```json
{
  "status": "success",
  "code": 200,
  "message": "认证成功",
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
    "expiresIn": 3600,
    "tokenType": "Bearer",
    "scope": "read write health-data"
  }
}
```

2. **使用访问令牌**

在所有需要认证的请求中，将访问令牌放在Authorization头中：

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6...
```

3. **刷新访问令牌**

```
POST /v1/auth/refresh
```

请求体：
```json
{
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6..."
}
```

响应与获取令牌相同。

### 权限控制

索克生活API使用基于角色和细粒度权限的访问控制系统：

1. **角色**
   - `user` - 普通用户
   - `premium_user` - 高级用户
   - `practitioner` - 中医师
   - `admin` - 管理员

2. **权限范围**
   - `read` - 基本读取权限
   - `write` - 创建和编辑权限
   - `health-data` - 健康数据访问权限
   - `health-data:write` - 健康数据写入权限
   - `admin` - 管理功能权限

JWT中包含用户角色和权限信息，后端进行权限验证。

## 错误处理

### 错误响应格式

当发生错误时，响应格式如下：

```json
{
  "status": "error",
  "code": 400,
  "message": "请求参数验证失败",
  "errors": [
    {
      "field": "email",
      "message": "请提供有效的电子邮件地址"
    },
    {
      "field": "password",
      "message": "密码长度必须至少为8个字符"
    }
  ],
  "meta": {
    "timestamp": "2024-06-01T12:34:56.789Z",
    "requestId": "req-123456-abcdef",
    "documentation": "https://docs.suokelife.com/api/errors#400"
  }
}
```

### 标准错误码

| HTTP状态码 | 描述 | 使用场景 |
|-----------|------|---------|
| 400 | 请求无效 | 请求参数格式错误或缺失必要参数 |
| 401 | 未认证 | 缺少认证信息或认证已过期 |
| 403 | 禁止访问 | 认证成功但权限不足 |
| 404 | 资源不存在 | 请求的资源不存在 |
| 409 | 资源冲突 | 操作导致资源冲突，如用户名已存在 |
| 422 | 请求内容无效 | 请求格式正确但内容无效，如失败的业务逻辑验证 |
| 429 | 请求过多 | 超过API速率限制 |
| 500 | 服务器错误 | 服务器内部错误 |
| 503 | 服务不可用 | 服务临时不可用，如维护中 |

### 业务错误码

除HTTP状态码外，API还使用自定义业务错误码提供更具体的错误信息：

| 错误码 | 描述 | HTTP状态码 |
|-------|------|-----------|
| 1001 | 用户认证失败 | 401 |
| 1002 | 访问令牌已过期 | 401 |
| 1003 | 刷新令牌无效 | 401 |
| 2001 | 用户账户被锁定 | 403 |
| 2002 | 健康数据访问受限 | 403 |
| 3001 | 用户不存在 | 404 |
| 3002 | 健康记录不存在 | 404 |
| 4001 | 电子邮件已被注册 | 409 |
| 4002 | 手机号已被注册 | 409 |
| 5001 | 舌象分析失败 | 422 |
| 5002 | 脉象数据无效 | 422 |
| 9001 | 服务器内部错误 | 500 |

## 版本控制

索克生活API采用多种版本控制策略结合的方式：

### 1. URL版本控制

在URL中包含主版本号：

```
https://api.suokelife.com/v1/users
```

此方式用于主要版本之间的不兼容变更。

### 2. 请求头版本控制

通过`X-Api-Version`请求头指定更精细的版本：

```
X-Api-Version: 1.2
```

此方式用于兼容性更新，如添加新字段或可选参数。

### 3. 媒体类型版本控制

接受特定版本的媒体类型：

```
Accept: application/vnd.suokelife.v1+json
```

### 4. API生命周期管理

- **预览版API**：路径前缀为`/beta`
- **弃用通知**：通过`X-API-Deprecated`响应头
- **过渡期**：主要版本更新后，旧版本至少保留12个月

## WebSocket通信

针对需要实时通信的场景，如智能体对话和实时健康监测，索克生活API提供WebSocket接口。

### 连接建立

WebSocket连接URL：

```
wss://ws.suokelife.com/v1/ws?token={access_token}
```

使用查询参数或子协议头传递认证信息。

### 消息格式

WebSocket消息采用JSON格式：

```json
{
  "type": "message|event|command|response",
  "id": "msg-123456",
  "agentId": "xiaoai",
  "content": { ... },
  "timestamp": "2024-06-01T12:34:56.789Z"
}
```

消息类型：
- `message`：聊天消息
- `event`：系统事件通知
- `command`：控制命令
- `response`：命令响应

### 示例交互

1. **客户端发送消息**

```json
{
  "type": "message",
  "id": "msg-123456",
  "agentId": "xiaoai",
  "content": {
    "text": "我今天感觉很疲劳，舌苔发白，应该吃什么好？",
    "messageType": "text"
  },
  "timestamp": "2024-06-01T12:34:56.789Z"
}
```

2. **服务端响应**

```json
{
  "type": "message",
  "id": "msg-234567",
  "agentId": "xiaoai",
  "replyTo": "msg-123456",
  "content": {
    "text": "根据您描述的症状，可能与脾胃湿热有关...",
    "messageType": "text",
    "suggestions": [
      {
        "type": "diet",
        "text": "建议多食用山药、莲子等健脾食材"
      }
    ]
  },
  "timestamp": "2024-06-01T12:34:59.123Z"
}
```

### 心跳机制

为保持连接活跃，客户端应定期发送心跳：

```json
{
  "type": "command",
  "id": "cmd-ping-123",
  "content": {
    "command": "ping"
  },
  "timestamp": "2024-06-01T12:35:56.789Z"
}
```

服务器响应：

```json
{
  "type": "response",
  "id": "resp-ping-123",
  "replyTo": "cmd-ping-123",
  "content": {
    "command": "ping",
    "status": "success"
  },
  "timestamp": "2024-06-01T12:35:56.890Z"
}
```

建议心跳间隔：30秒。

## 数据模型

### 核心资源

索克生活API操作的核心资源包括：

#### 用户 (User)

```json
{
  "id": "user-123456",
  "username": "zhangsan",
  "email": "zhang@example.com",
  "phone": "+86123456789",
  "profile": {
    "fullName": "张三",
    "gender": "male",
    "birthDate": "1990-01-15",
    "height": 175,
    "weight": 70,
    "avatarUrl": "https://static.suokelife.com/avatars/default.png"
  },
  "preferences": {
    "language": "zh-CN",
    "notification": true,
    "theme": "light"
  },
  "roles": ["user"],
  "createdAt": "2023-10-20T08:12:34.567Z",
  "updatedAt": "2024-05-15T16:45:12.345Z"
}
```

#### 健康记录 (HealthRecord)

```json
{
  "id": "record-123456",
  "userId": "user-123456",
  "type": "tongue|pulse|questionnaire|vital",
  "recordedAt": "2024-06-01T09:30:00Z",
  "data": {
    // 根据type不同而变化的结构化数据
  },
  "analysis": {
    // 分析结果
  },
  "status": "pending|analyzed|reviewed",
  "privacyLevel": "private|practitioner|research",
  "source": "app|device|practitioner",
  "createdAt": "2024-06-01T09:32:15.678Z",
  "updatedAt": "2024-06-01T09:35:22.789Z"
}
```

#### 舌象记录 (TongueRecord)

```json
{
  "id": "tongue-123456",
  "userId": "user-123456",
  "imageUrl": "https://static.suokelife.com/health-data/tongue/123456.jpg",
  "thumbnailUrl": "https://static.suokelife.com/health-data/tongue/123456_thumb.jpg",
  "recordedAt": "2024-06-01T09:30:00Z",
  "analysis": {
    "tongueColor": "淡红舌",
    "tongueShape": "胖大舌",
    "tongueCoating": "薄白苔",
    "tongueCoatingThickness": "thin",
    "tongueCoatingColor": "white",
    "tongueMoisture": "normal",
    "tongueIndentations": true,
    "constitutionIndications": [
      {
        "type": "phlegmDampness",
        "confidence": 0.85
      },
      {
        "type": "qi_deficiency",
        "confidence": 0.72
      }
    ],
    "confidenceScore": 0.89,
    "analysisModel": "tcm-tongue-v3.1",
    "analyzerVersion": "2.3.0"
  },
  "practitionerReview": {
    "reviewedBy": "practitioner-789012",
    "reviewedAt": "2024-06-01T15:45:30Z",
    "comments": "分析准确，建议调整饮食减少湿气",
    "adjustments": { ... }
  },
  "status": "analyzed|reviewed",
  "createdAt": "2024-06-01T09:32:15.678Z",
  "updatedAt": "2024-06-01T15:45:30.123Z"
}
```

#### 体质评估 (ConstitutionAssessment)

```json
{
  "id": "assessment-123456",
  "userId": "user-123456",
  "assessedAt": "2024-06-01T10:15:00Z",
  "source": "questionnaire|comprehensive|practitioner",
  "scores": {
    "balanced": 0.72,
    "qi_deficiency": 0.45,
    "yang_deficiency": 0.25,
    "yin_deficiency": 0.32,
    "phlegm_dampness": 0.68,
    "damp_heat": 0.58,
    "blood_stasis": 0.35,
    "qi_stagnation": 0.40,
    "special": 0.15
  },
  "primaryConstitution": "phlegm_dampness",
  "secondaryConstitution": "damp_heat",
  "dataPoints": {
    "tongueRecordId": "tongue-123456",
    "pulseRecordId": "pulse-789012",
    "questionnaireId": "questionnaire-345678"
  },
  "recommendations": [
    {
      "category": "diet",
      "content": "适宜食物：薏苡仁、赤小豆、冬瓜...",
      "priority": "high"
    },
    {
      "category": "lifestyle",
      "content": "建议保持规律作息，避免熬夜...",
      "priority": "medium"
    }
  ],
  "createdAt": "2024-06-01T10:20:30.789Z",
  "updatedAt": "2024-06-01T10:20:30.789Z"
}
```

## 安全通信策略

### 传输层安全

- 所有API通信必须使用TLS 1.3或更高版本
- 强制实施HTTPS，HTTP请求自动重定向到HTTPS
- 实施HSTS(HTTP Strict Transport Security)
- 支持证书透明度(Certificate Transparency)
- 定期更新TLS配置以应对新漏洞

### 敏感数据保护

- 健康数据传输采用端到端加密
- 敏感请求参数不应出现在URL中
- 日志中自动脱敏敏感信息
- 严格的内容安全策略(CSP)
- 访问控制列表(ACL)管理敏感资源

### API安全头

所有响应包含以下安全相关HTTP头：

```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
Cache-Control: no-store, max-age=0
```

## API限流与保护

### 速率限制

API实施以下速率限制：

| API类别 | 标准用户限制 | 高级用户限制 | 中医师用户限制 |
|--------|------------|------------|------------|
| 认证API | 10次/分钟 | 10次/分钟 | 10次/分钟 |
| 查询API | 60次/分钟 | 120次/分钟 | 120次/分钟 |
| 创建/更新API | 30次/分钟 | 60次/分钟 | 60次/分钟 |
| 健康数据上传 | 20次/小时 | 50次/小时 | 100次/小时 |
| 智能体API | 100次/小时 | 300次/小时 | 500次/小时 |

限流信息通过HTTP头返回：

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 56
X-RateLimit-Reset: 1623456789
```

超过限制时返回429状态码。

### DDoS防护

- 实施基于云服务的DDoS防护
- 异常流量检测与阻断
- 地理位置异常请求监控
- CDN缓存减轻源站压力

## 跨平台考量

为确保API支持多平台客户端，特别考虑：

### 移动设备优化

- 支持HTTP/2减少请求开销
- 响应内容压缩(gzip, brotli)
- 优化JSON结构减少数据量
- 批量请求API减少网络往返

### 连接不稳定场景

- 支持请求重试机制
- 幂等性API设计确保重试安全
- 断点续传支持大文件上传
- 优雅的离线数据同步策略

### 客户端缓存策略

响应头中包含缓存指令：

```
Cache-Control: private, max-age=3600
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"
Last-Modified: Wed, 01 Jun 2024 12:00:00 GMT
```

支持条件请求减少带宽使用：

```
If-None-Match: "33a64df551425fcc55e4d42a148795d9f25f89d4"
If-Modified-Since: Wed, 01 Jun 2024 12:00:00 GMT
```

## 变更管理与通知

API变更遵循以下原则：

1. 破坏性变更必须通过主版本号升级实现
2. 至少提前30天公告重大变更
3. 设置过渡期允许客户端适应
4. 通过开发者门户和邮件通知变更
5. 提供迁移指南帮助客户端适配新版本

---

本协议文档随API发展持续更新，最新版本请访问开发者门户。

最后更新：2025年5月9日
版本：1.0.0