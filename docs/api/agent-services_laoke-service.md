# Agent Services Laoke Service API 文档

## 服务概述

**服务名称**: agent-services/laoke-service  
**版本**: 1.0.0  
**描述**: 老克智能体服务主入口
探索频道版主，负责知识传播、培训和博物馆导览，兼任玉米迷宫NPC

## API 端点

### GET 请求

#### GET /

**功能**: 根路径

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

#### GET /agent/status

**功能**: 获取智能体状态

**函数**: `get_agent_status`

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

#### GET /metrics

**功能**: 提供Prometheus监控指标

返回:
Response: 包含指标数据的响应

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

#### GET /health

**功能**: 健康检查端点

返回:
dict: 健康状态信息

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

#### GET /health/system

**功能**: 系统信息端点

返回:
dict: 系统信息

**函数**: `system_info`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### GET /health/ready

**功能**: 就绪检查端点，用于Kubernetes就绪性探针

返回:
dict: 就绪状态信息

**函数**: `readiness_check`

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

#### POST /agent/message

**功能**: POST /agent/message

**函数**: `send_message`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### POST /agent/search-knowledge

**功能**: POST /agent/search-knowledge

**函数**: `search_knowledge`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### POST /agent/create-learning-path

**功能**: POST /agent/create-learning-path

**函数**: `create_learning_path`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### POST /agent/maze-interaction

**功能**: POST /agent/maze-interaction

**函数**: `maze_interaction`

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

