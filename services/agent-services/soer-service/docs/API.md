# soer-service API 文档

## 概述

soer-service 提供完整的RESTful API和gRPC接口。

## 认证

所有API请求需要包含认证头：

```
Authorization: Bearer <token>
```

## 核心接口

### 健康检查

```http
GET /health
```

响应：
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-12-19T10:00:00Z"
}
```

### 服务状态

```http
GET /status
```

响应：
```json
{
  "service": "soer-service",
  "status": "running",
  "uptime": "24h30m15s",
  "completion": "100%"
}
```

## 业务接口

根据服务类型提供相应的业务API接口。

## 错误处理

所有错误响应遵循统一格式：

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {}
  }
}
```

## 限流

- 默认限制：1000次/分钟
- 突发限制：100次/秒

## 版本控制

API版本通过URL路径指定：`/api/v1/`
