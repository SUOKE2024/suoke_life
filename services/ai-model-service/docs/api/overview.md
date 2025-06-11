# API 概览

AI Model Service 提供了完整的 RESTful API，用于管理AI模型的部署、推理和监控。

## 🎯 设计理念

### RESTful 设计
- 遵循 REST 架构风格
- 使用标准 HTTP 方法（GET、POST、PUT、DELETE）
- 资源导向的 URL 设计
- 统一的响应格式

### 版本控制
- API 版本通过 URL 路径进行管理：`/api/v1/`
- 向后兼容性保证
- 渐进式版本升级

### 错误处理
- 标准 HTTP 状态码
- 详细的错误信息
- 结构化的错误响应

## 🔗 API 基础信息

### 基础 URL
```
http://localhost:8080/api/v1
```

### 认证方式
- API Key 认证（Header: `X-API-Key`）
- JWT Token 认证（Header: `Authorization: Bearer <token>`）

### 内容类型
- 请求：`application/json`
- 响应：`application/json`

## 📋 API 分组

### 1. 模型管理 API (`/models`)
负责AI模型的生命周期管理：

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/models/deploy` | 部署新模型 |
| GET | `/models` | 列出所有模型 |
| GET | `/models/{model_id}/status` | 获取模型状态 |
| POST | `/models/{model_id}/inference` | 单次推理 |
| POST | `/models/{model_id}/batch_inference` | 批量推理 |
| POST | `/models/{model_id}/scale` | 扩缩容模型 |
| PUT | `/models/{model_id}` | 更新模型 |
| DELETE | `/models/{model_id}` | 删除模型 |

### 2. 健康检查 API (`/health`)
提供服务健康状态监控：

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/health/` | 基础健康检查 |
| GET | `/health/live` | 存活检查 |
| GET | `/health/ready` | 就绪检查 |
| GET | `/health/startup` | 启动检查 |
| GET | `/health/detailed` | 详细健康检查 |

## 📊 响应格式

### 成功响应
```json
{
  "status": "success",
  "data": {
    // 响应数据
  },
  "message": "操作成功"
}
```

### 错误响应
```json
{
  "status": "error",
  "error": {
    "code": "MODEL_NOT_FOUND",
    "message": "指定的模型不存在",
    "details": {
      "model_id": "invalid_model"
    }
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 🔢 HTTP 状态码

| 状态码 | 含义 | 使用场景 |
|--------|------|----------|
| 200 | OK | 请求成功 |
| 201 | Created | 资源创建成功 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 认证失败 |
| 403 | Forbidden | 权限不足 |
| 404 | Not Found | 资源不存在 |
| 409 | Conflict | 资源冲突 |
| 422 | Unprocessable Entity | 数据验证失败 |
| 500 | Internal Server Error | 服务器内部错误 |
| 503 | Service Unavailable | 服务不可用 |

## 🔐 认证和授权

### API Key 认证
```bash
curl -H "X-API-Key: your-api-key" \
     -H "Content-Type: application/json" \
     http://localhost:8080/api/v1/models
```

### JWT Token 认证
```bash
curl -H "Authorization: Bearer your-jwt-token" \
     -H "Content-Type: application/json" \
     http://localhost:8080/api/v1/models
```

## 📝 请求示例

### 部署模型
```bash
curl -X POST http://localhost:8080/api/v1/models/deploy \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "config": {
      "model_id": "tcm_diagnosis_v1",
      "name": "中医诊断模型",
      "version": "1.0.0",
      "model_type": "tcm_diagnosis",
      "docker_image": "suoke/tcm-model:1.0.0"
    }
  }'
```

### 执行推理
```bash
curl -X POST http://localhost:8080/api/v1/models/tcm_diagnosis_v1/inference \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "input_data": {
      "symptoms": ["头痛", "乏力"],
      "patient_info": {
        "age": 35,
        "gender": "female"
      }
    },
    "parameters": {
      "temperature": 0.7
    }
  }'
```

## 🚀 SDK 和客户端

### Python SDK
```python
from ai_model_service import ModelServiceClient

client = ModelServiceClient(
    base_url="http://localhost:8080",
    api_key="your-api-key"
)

# 部署模型
deployment = client.deploy_model(config)

# 执行推理
result = client.inference(model_id, input_data)
```

### JavaScript SDK
```javascript
import { ModelServiceClient } from '@suoke/ai-model-service-js';

const client = new ModelServiceClient({
  baseURL: 'http://localhost:8080',
  apiKey: 'your-api-key'
});

// 部署模型
const deployment = await client.deployModel(config);

// 执行推理
const result = await client.inference(modelId, inputData);
```

## 📚 更多信息

- [模型管理API详细文档](models.md)
- [健康检查API详细文档](health.md)
- [完整API参考](reference.md)