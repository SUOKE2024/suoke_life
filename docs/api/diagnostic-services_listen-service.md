# Diagnostic Services Listen Service API 文档

## 服务概述

**服务名称**: diagnostic-services/listen-service  
**版本**: 1.0.0  
**描述**: REST API接口实现

提供HTTP接口用于音频分析和中医诊断服务。
基于FastAPI框架，支持异步处理、文件上传、错误处理等功能。

## API 端点

### GET 请求

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

#### GET /stats

**功能**: 获取服务统计信息

**函数**: `get_stats`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### GET /api/v1/performance/metrics

**功能**: 获取性能指标

**函数**: `get_performance_metrics`

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

#### POST /api/v1/analyze/audio

**功能**: POST /api/v1/analyze/audio

**函数**: `analyze_audio`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### POST /api/v1/analyze/tcm

**功能**: POST /api/v1/analyze/tcm

**函数**: `analyze_tcm`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### POST /api/v1/analyze/batch

**功能**: POST /api/v1/analyze/batch

**函数**: `analyze_batch`

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

#### DELETE /api/v1/cache/clear

**功能**: DELETE /api/v1/cache/clear

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

## 数据模型

### AudioAnalysisRequest

音频分析REST请求

```python
class AudioAnalysisRequest(BaseModel):
    # 字段定义
    pass
```

### TCMAnalysisRequest

中医分析REST请求

```python
class TCMAnalysisRequest(BaseModel):
    # 字段定义
    pass
```

### HealthResponse

健康检查响应

```python
class HealthResponse(BaseModel):
    # 字段定义
    pass
```

### StatsResponse

统计信息响应

```python
class StatsResponse(BaseModel):
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

