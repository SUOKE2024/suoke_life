# Diagnostic Services Calculation Service API 文档

## 服务概述

**服务名称**: diagnostic-services/calculation-service  
**版本**: 1.0.0  
**描述**: 算诊服务主应用

提供中医五诊中"算诊"功能的微服务

## API 端点

### GET 请求

#### GET /

**功能**: 服务根路径

**函数**: `root`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### GET /ping

**功能**: 简单的服务状态检查

**函数**: `ping`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### GET /cache/stats

**功能**: 获取缓存统计信息

**函数**: `cache_stats`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### GET /items/

**功能**: GET /items/

**函数**: `read_items`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### GET /items/

**功能**: GET /items/

**函数**: `read_items`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### GET /items/

**功能**: GET /items/

**函数**: `read_items`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

### POST 请求

#### POST /cache/clear

**功能**: 清理所有缓存

**函数**: `clear_cache`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### POST /cache/cleanup

**功能**: 清理过期缓存

**函数**: `cleanup_expired_cache`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

## 错误码说明

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 200 | 请求成功 | - |
| 400 | 请求参数错误 | 检查请求参数格式 |
| 401 | 未授权访问 | 检查认证信息 |
| 403 | 权限不足 | 联系管理员 |
| 404 | 资源不存在 | 检查请求路径 |
| 500 | 服务器内部错误 | 联系技术支持 |

## 使用示例

### Python 示例

```python
import requests

# 基础URL
BASE_URL = "http://localhost:8000"

# 示例请求
response = requests.get(f"{BASE_URL}/api/v1/health")
print(response.json())
```

### cURL 示例

```bash
# 健康检查
curl -X GET "http://localhost:8000/api/v1/health"

# 带认证的请求
curl -X GET "http://localhost:8000/api/v1/data" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 联系信息

- **技术支持**: tech@suoke.life
- **文档更新**: 2025年6月6日
- **维护团队**: 索克生活技术团队

