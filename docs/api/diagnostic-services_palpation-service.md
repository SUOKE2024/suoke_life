# Diagnostic Services Palpation Service API 文档

## 服务概述

**服务名称**: diagnostic-services/palpation-service  
**版本**: 1.0.0  
**描述**: 索克生活 - 触诊服务主启动脚本
整合所有优化模块，提供完整的服务启动和管理功能

## API 端点

### GET 请求

#### GET /

**功能**: 根端点

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

#### GET /health

**功能**: 健康检查

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

#### GET /palpation/report/{session_id}

**功能**: 获取触诊报告

**函数**: `get_palpation_report`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### GET /config

**功能**: 获取配置信息

**函数**: `get_config`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### GET /stats

**功能**: 获取服务统计

**函数**: `get_service_stats`

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

#### POST /palpation/start

**功能**: 启动触诊会话

**函数**: `start_palpation_session`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### POST /palpation/data

**功能**: 提交触诊数据

**函数**: `submit_palpation_data`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### POST /palpation/analyze

**功能**: 综合触诊分析

**函数**: `analyze_palpation`

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

### PalpationRequest

数据模型: PalpationRequest

```python
class PalpationRequest(BaseModel):
    # 字段定义
    pass
```

### PalpationData

数据模型: PalpationData

```python
class PalpationData(BaseModel):
    # 字段定义
    pass
```

### AnalysisRequest

数据模型: AnalysisRequest

```python
class AnalysisRequest(BaseModel):
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

