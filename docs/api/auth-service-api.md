# Auth-Service API 文档

## 概述

auth-service 是索克生活平台的核心微服务之一。

## 基础信息

- **服务名称**: auth-service
- **版本**: v1.0.0
- **协议**: HTTP/gRPC
- **认证**: JWT Bearer Token

## API 端点

### 健康检查

```http
GET /health
```

**响应示例**:
```json
{
  "status": "healthy",
  "timestamp": "2024-06-08T12:00:00Z",
  "version": "1.0.0"
}
```

### 核心功能接口

#### 1. 主要服务接口

```http
POST /api/v1/auth_service/process
```

**请求参数**:
```json
{
  "data": "处理数据",
  "options": {
    "mode": "standard"
  }
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "result": "处理结果"
  },
  "timestamp": "2024-06-08T12:00:00Z"
}
```

## 错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 400 | 请求参数错误 | 检查请求参数格式 |
| 401 | 认证失败 | 检查JWT Token |
| 500 | 服务器内部错误 | 联系技术支持 |

## 使用示例

### Python 示例

```python
import requests

# 健康检查
response = requests.get('http://localhost:8080/health')
print(response.json())

# 调用服务
data = {"data": "test", "options": {"mode": "standard"}}
response = requests.post(
    'http://localhost:8080/api/v1/auth_service/process',
    json=data,
    headers={'Authorization': 'Bearer YOUR_JWT_TOKEN'}
)
print(response.json())
```

### JavaScript 示例

```javascript
// 健康检查
fetch('http://localhost:8080/health')
  .then(response => response.json())
  .then(data => console.log(data));

// 调用服务
fetch('http://localhost:8080/api/v1/auth_service/process', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_JWT_TOKEN'
  },
  body: JSON.stringify({
    data: 'test',
    options: { mode: 'standard' }
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

## 部署信息

- **Docker镜像**: `suoke-life/auth-service:latest`
- **端口**: 8080
- **健康检查**: `/health`
- **指标监控**: `/metrics`

## 更新日志

### v1.0.0 (2024-06-08)
- 初始版本发布
- 实现核心功能接口
- 添加健康检查和监控

---

*文档生成时间: 2024-06-08*
*维护团队: 索克生活技术团队*
