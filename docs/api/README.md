# API 文档

## 基础信息

- 基础URL: https://api.suoke.life/v1
- 认证方式: Bearer Token
- 响应格式: JSON

## 认证

### 登录
```http
POST /auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

### 注册
```http
POST /auth/register
Content-Type: application/json

{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

## AI 助手

### 发送消息
```http
POST /ai/chat
Content-Type: application/json
Authorization: Bearer <token>

{
  "assistant_type": "string",
  "message": "string"
}
```

### 获取对话历史
```http
GET /ai/chat/history
Authorization: Bearer <token>
```

## 健康管理

### 添加健康记录
```http
POST /health/records
Content-Type: application/json
Authorization: Bearer <token>

{
  "height": "number",
  "weight": "number",
  "blood_pressure": "string",
  "heart_rate": "number"
}
```

### 获取健康记录
```http
GET /health/records
Authorization: Bearer <token>
```

## 生活记录

### 创建记录
```http
POST /life/records
Content-Type: multipart/form-data
Authorization: Bearer <token>

{
  "type": "string",
  "title": "string",
  "content": "string",
  "images": "file[]",
  "tags": "string[]"
}
```

### 获取记录列表
```http
GET /life/records
Authorization: Bearer <token>
```

## 错误码

| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |

## 响应格式

### 成功响应
```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

### 错误响应
```json
{
  "code": 400,
  "message": "参数错误",
  "errors": []
}
```

## 限流策略

- 普通用户: 60次/分钟
- 高级用户: 200次/分钟
- AI对话: 20次/分钟

## WebSocket

### 实时消息
```
ws://api.suoke.life/ws/messages
```

### 心跳包
```json
{
  "type": "ping",
  "timestamp": 1234567890
}
``` 