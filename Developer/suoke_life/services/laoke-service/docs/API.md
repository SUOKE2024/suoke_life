# 老克服务 API 文档

## 基本信息

- **服务名称**: laoke-service
- **版本**: v1
- **基础URL**: `/api/v1`

## 认证

所有API请求需要在Header中包含认证令牌：

```
Authorization: Bearer <token>
```

## 健康检查端点

### 获取服务健康状态

```
GET /health/live
```

**响应示例**:

```json
{
  "status": "UP"
}
```

### 获取服务就绪状态

```
GET /health/ready
```

**响应示例**:

```json
{
  "status": "READY"
}
```

## 会话管理

### 创建会话

```
POST /api/v1/sessions
```

**请求体**:

```json
{
  "userId": "user-123",
  "clientId": "web-client-1",
  "contextData": {
    "location": "北京",
    "preferences": {
      "dialect": "北方话",
      "interests": ["太极", "中医养生"]
    }
  }
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "sessionId": "sess-6789",
    "createdAt": "2023-08-01T10:15:30Z",
    "expiresAt": "2023-08-01T11:15:30Z"
  }
}
```

### 获取会话状态

```
GET /api/v1/sessions/:sessionId
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "sessionId": "sess-6789",
    "status": "active",
    "createdAt": "2023-08-01T10:15:30Z",
    "expiresAt": "2023-08-01T11:15:30Z",
    "lastActivityAt": "2023-08-01T10:30:45Z"
  }
}
```

## 对话管理

### 发送消息

```
POST /api/v1/sessions/:sessionId/messages
```

**请求体**:

```json
{
  "type": "text",
  "content": "我最近总是感觉疲劳，有什么调理方法吗？",
  "timestamp": "2023-08-01T10:16:00Z"
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "messageId": "msg-1234",
    "status": "processing"
  }
}
```

### 获取消息响应

```
GET /api/v1/messages/:messageId
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "messageId": "msg-1234",
    "type": "text",
    "content": "您好，根据您的描述，疲劳可能与多种因素有关...",
    "timestamp": "2023-08-01T10:16:05Z",
    "references": [
      {
        "title": "中医疲劳调理方案",
        "source": "中医养生知识库",
        "confidence": 0.92
      }
    ]
  }
}
```

### 获取会话历史

```
GET /api/v1/sessions/:sessionId/history
```

**查询参数**:

- `limit`: 返回消息数量限制 (默认20)
- `before`: 返回指定时间戳之前的消息

**响应示例**:

```json
{
  "success": true,
  "data": {
    "messages": [
      {
        "messageId": "msg-1233",
        "role": "user",
        "type": "text",
        "content": "你好，老克",
        "timestamp": "2023-08-01T10:15:45Z"
      },
      {
        "messageId": "msg-1234",
        "role": "assistant",
        "type": "text",
        "content": "您好！我是老克，很高兴为您服务。有什么我可以帮您的吗？",
        "timestamp": "2023-08-01T10:15:50Z"
      }
    ],
    "hasMore": false,
    "totalCount": 2
  }
}
```

## 媒体处理

### 上传语音

```
POST /api/v1/sessions/:sessionId/media/audio
```

**表单数据**:

- `file`: 音频文件 (支持格式: mp3, wav, ogg)
- `metadata`: JSON字符串，包含以下字段:
  - `duration`: 音频时长(秒)
  - `format`: 音频格式
  - `dialect`: 方言类型(可选)

**响应示例**:

```json
{
  "success": true,
  "data": {
    "mediaId": "media-5678",
    "url": "https://storage.example.com/media-5678",
    "status": "processing"
  }
}
```

## 错误处理

所有API错误响应采用统一格式:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述信息",
    "details": {}
  }
}
```

### 常见错误代码

- `UNAUTHORIZED`: 未授权访问
- `SESSION_NOT_FOUND`: 会话不存在
- `INVALID_REQUEST`: 请求参数无效
- `SERVICE_UNAVAILABLE`: 服务暂时不可用
- `RATE_LIMIT_EXCEEDED`: 超过请求频率限制

## WebSocket API

WebSocket连接URL: `ws://host:port/socket?sessionId=sess-6789&token=jwt-token`

### 事件类型

#### 客户端事件

- `message`: 发送消息
- `typing`: 输入中状态
- `read`: 已读确认

#### 服务器事件

- `message`: 接收消息
- `typing`: 对方输入中
- `session_update`: 会话状态更新

### 示例消息格式

```json
{
  "type": "message",
  "data": {
    "content": "您好，我有个问题想咨询",
    "timestamp": "2023-08-01T10:20:00Z"
  }
}
``` 