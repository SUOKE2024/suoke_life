# User Service API 文档

## 服务概述

**服务名称**: user-service  
**版本**: 1.0.0  
**描述**: 用户服务主应用

## API 端点

### GET 请求

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

#### GET /health

**功能**: 健康检查端点
提供服务健康状态，用于监控和负载均衡检查

Args:
request: 请求对象
detailed: 是否返回详细信息

Returns:
Dict[str, Any]: 健康状态

**函数**: `health_check`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### GET /status

**功能**: 简化版状态检查端点
提供简单的服务状态，用于快速检查

Returns:
Dict[str, str]: 服务状态

**函数**: `status_check`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### GET /metrics

**功能**: Prometheus指标端点
提供服务指标，用于监控和性能分析

Args:
request: 请求对象

Returns:
Response: 包含Prometheus格式指标的响应

**函数**: `metrics`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### GET /users

**功能**: GET /users

**函数**: `list_users`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### GET /users/{user_id}

**功能**: 获取用户信息

**函数**: `get_user`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### GET /users/{user_id}/health-summary

**功能**: 获取用户健康摘要

**函数**: `get_user_health_summary`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### GET /users/{user_id}/devices

**功能**: 获取用户设备列表

**函数**: `get_user_devices`

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

#### POST /users

**功能**: 创建新用户

**函数**: `create_user`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### POST /users/{user_id}/devices

**功能**: POST /users/{user_id}/devices

**函数**: `bind_device`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### POST /users/verify

**功能**: 验证用户身份

**函数**: `verify_user_identity`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

### PUT 请求

#### PUT /users/{user_id}

**功能**: PUT /users/{user_id}

**函数**: `update_user`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### PUT /users/{user_id}/preferences

**功能**: PUT /users/{user_id}/preferences

**函数**: `update_user_preferences`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

### DELETE 请求

#### DELETE /users/{user_id}

**功能**: 删除用户

**函数**: `delete_user`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### DELETE /users/{user_id}/devices/{device_id}

**功能**: DELETE /users/{user_id}/devices/{device_id}

**函数**: `unbind_device`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

## 数据模型

### CreateUserAPIRequest

创建用户API请求

```python
class CreateUserAPIRequest(BaseModel):
    # 字段定义
    pass
```

### UpdateUserAPIRequest

更新用户API请求

```python
class UpdateUserAPIRequest(BaseModel):
    # 字段定义
    pass
```

### UpdateUserPreferencesAPIRequest

更新用户偏好设置API请求

```python
class UpdateUserPreferencesAPIRequest(BaseModel):
    # 字段定义
    pass
```

### BindDeviceAPIRequest

绑定设备API请求

```python
class BindDeviceAPIRequest(BaseModel):
    # 字段定义
    pass
```

### VerifyUserAPIRequest

验证用户API请求

```python
class VerifyUserAPIRequest(BaseModel):
    # 字段定义
    pass
```

### UserAPIResponse

用户API响应

```python
class UserAPIResponse(BaseModel):
    # 字段定义
    pass
```

### HealthMetricAPIResponse

健康指标API响应

```python
class HealthMetricAPIResponse(BaseModel):
    # 字段定义
    pass
```

### HealthSummaryAPIResponse

健康摘要API响应

```python
class HealthSummaryAPIResponse(BaseModel):
    # 字段定义
    pass
```

### DeviceInfoAPIResponse

设备信息API响应

```python
class DeviceInfoAPIResponse(BaseModel):
    # 字段定义
    pass
```

### UserDevicesAPIResponse

用户设备列表API响应

```python
class UserDevicesAPIResponse(BaseModel):
    # 字段定义
    pass
```

### BindDeviceAPIResponse

绑定设备API响应

```python
class BindDeviceAPIResponse(BaseModel):
    # 字段定义
    pass
```

### VerifyUserAPIResponse

验证用户API响应

```python
class VerifyUserAPIResponse(BaseModel):
    # 字段定义
    pass
```

### PaginatedUserResponse

分页用户响应

```python
class PaginatedUserResponse(BaseModel):
    # 字段定义
    pass
```

### ErrorResponse

错误响应

```python
class ErrorResponse(BaseModel):
    # 字段定义
    pass
```

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

