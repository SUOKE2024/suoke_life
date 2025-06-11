# 模型管理 API

模型管理API提供了完整的AI模型生命周期管理功能，包括部署、推理、扩缩容、更新和删除。

## 📋 API 端点概览

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

## 🚀 部署模型

### 端点
```
POST /api/v1/models/deploy
```

### 请求体
```json
{
  "config": {
    "model_id": "string",
    "name": "string",
    "version": "string",
    "model_type": "tcm_diagnosis | multimodal | treatment",
    "framework": "tensorflow | pytorch | onnx",
    "docker_image": "string",
    "resource_requirements": {
      "cpu": "string",
      "memory": "string",
      "nvidia.com/gpu": "string"
    },
    "scaling_config": {
      "min_replicas": "integer",
      "max_replicas": "integer",
      "target_cpu_utilization": "integer"
    },
    "environment_variables": {
      "key": "value"
    }
  }
}
```

### 响应
```json
{
  "deployment_id": "string",
  "message": "string"
}
```

### 示例
```bash
curl -X POST http://localhost:8080/api/v1/models/deploy \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "config": {
      "model_id": "tcm_diagnosis_v2",
      "name": "中医诊断模型 v2.0",
      "version": "2.0.0",
      "model_type": "tcm_diagnosis",
      "framework": "tensorflow",
      "docker_image": "suoke/tcm-diagnosis:2.0.0",
      "resource_requirements": {
        "cpu": "2",
        "memory": "8Gi",
        "nvidia.com/gpu": "1"
      },
      "scaling_config": {
        "min_replicas": 1,
        "max_replicas": 5,
        "target_cpu_utilization": 70
      }
    }
  }'
```

## 🔍 查看模型状态

### 端点
```
GET /api/v1/models/{model_id}/status
```

### 路径参数
- `model_id` (string): 模型ID

### 响应
```json
{
  "model_id": "string",
  "name": "string",
  "version": "string",
  "status": "pending | running | failed | stopped",
  "replicas": {
    "desired": "integer",
    "current": "integer",
    "ready": "integer"
  },
  "endpoints": [
    {
      "type": "inference",
      "url": "string"
    }
  ],
  "created_at": "string",
  "updated_at": "string",
  "resource_usage": {
    "cpu": "string",
    "memory": "string",
    "gpu": "string"
  }
}
```

### 示例
```bash
curl -X GET http://localhost:8080/api/v1/models/tcm_diagnosis_v2/status \
  -H "X-API-Key: your-api-key"
```

## 📊 列出所有模型

### 端点
```
GET /api/v1/models
```

### 查询参数
- `status` (string, 可选): 按状态过滤 (pending, running, failed, stopped)
- `model_type` (string, 可选): 按模型类型过滤
- `limit` (integer, 可选): 返回结果数量限制 (默认: 50)
- `offset` (integer, 可选): 分页偏移量 (默认: 0)

### 响应
```json
[
  {
    "model_id": "string",
    "name": "string",
    "version": "string",
    "status": "string",
    "model_type": "string",
    "created_at": "string",
    "updated_at": "string"
  }
]
```

### 示例
```bash
curl -X GET "http://localhost:8080/api/v1/models?status=running&limit=10" \
  -H "X-API-Key: your-api-key"
```

## 🧠 单次推理

### 端点
```
POST /api/v1/models/{model_id}/inference
```

### 路径参数
- `model_id` (string): 模型ID

### 请求体
```json
{
  "input_data": "object",
  "parameters": "object",
  "timeout": "integer",
  "priority": "low | normal | high"
}
```

### 响应
```json
{
  "request_id": "string",
  "model_id": "string",
  "output_data": "object",
  "confidence": "number",
  "processing_time": "number",
  "timestamp": "string"
}
```

### 示例
```bash
curl -X POST http://localhost:8080/api/v1/models/tcm_diagnosis_v2/inference \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "input_data": {
      "symptoms": ["头痛", "乏力", "食欲不振"],
      "patient_info": {
        "age": 35,
        "gender": "female",
        "medical_history": []
      }
    },
    "parameters": {
      "temperature": 0.7,
      "max_tokens": 1024
    },
    "timeout": 30,
    "priority": "normal"
  }'
```

## 📦 批量推理

### 端点
```
POST /api/v1/models/{model_id}/batch_inference
```

### 路径参数
- `model_id` (string): 模型ID

### 请求体
```json
{
  "requests": [
    {
      "input_data": "object",
      "parameters": "object"
    }
  ],
  "timeout": "integer",
  "priority": "low | normal | high"
}
```

### 响应
```json
[
  {
    "request_id": "string",
    "model_id": "string",
    "output_data": "object",
    "confidence": "number",
    "processing_time": "number",
    "timestamp": "string"
  }
]
```

### 示例
```bash
curl -X POST http://localhost:8080/api/v1/models/tcm_diagnosis_v2/batch_inference \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "requests": [
      {
        "input_data": {
          "symptoms": ["头痛", "乏力"],
          "patient_info": {"age": 35, "gender": "female"}
        },
        "parameters": {"temperature": 0.7}
      },
      {
        "input_data": {
          "symptoms": ["失眠", "焦虑"],
          "patient_info": {"age": 28, "gender": "male"}
        },
        "parameters": {"temperature": 0.8}
      }
    ],
    "timeout": 60,
    "priority": "normal"
  }'
```

## ⚖️ 扩缩容模型

### 端点
```
POST /api/v1/models/{model_id}/scale
```

### 路径参数
- `model_id` (string): 模型ID

### 请求体
```json
{
  "replicas": "integer"
}
```

### 响应
```json
{
  "message": "string",
  "current_replicas": "integer",
  "target_replicas": "integer"
}
```

### 示例
```bash
curl -X POST http://localhost:8080/api/v1/models/tcm_diagnosis_v2/scale \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "replicas": 3
  }'
```

## 🔄 更新模型

### 端点
```
PUT /api/v1/models/{model_id}
```

### 路径参数
- `model_id` (string): 模型ID

### 请求体
```json
{
  "config": {
    "version": "string",
    "docker_image": "string",
    "resource_requirements": "object",
    "scaling_config": "object",
    "environment_variables": "object"
  }
}
```

### 响应
```json
{
  "deployment_id": "string",
  "message": "string"
}
```

### 示例
```bash
curl -X PUT http://localhost:8080/api/v1/models/tcm_diagnosis_v2 \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "config": {
      "version": "2.1.0",
      "docker_image": "suoke/tcm-diagnosis:2.1.0",
      "resource_requirements": {
        "cpu": "4",
        "memory": "16Gi"
      }
    }
  }'
```

## 🗑️ 删除模型

### 端点
```
DELETE /api/v1/models/{model_id}
```

### 路径参数
- `model_id` (string): 模型ID

### 查询参数
- `force` (boolean, 可选): 强制删除 (默认: false)

### 响应
```json
{
  "message": "string"
}
```

### 示例
```bash
curl -X DELETE http://localhost:8080/api/v1/models/tcm_diagnosis_v2 \
  -H "X-API-Key: your-api-key"

# 强制删除
curl -X DELETE "http://localhost:8080/api/v1/models/tcm_diagnosis_v2?force=true" \
  -H "X-API-Key: your-api-key"
```

## 🚨 错误处理

### 常见错误码

| 错误码 | HTTP状态码 | 描述 |
|--------|------------|------|
| MODEL_NOT_FOUND | 404 | 模型不存在 |
| MODEL_ALREADY_EXISTS | 409 | 模型已存在 |
| INVALID_MODEL_CONFIG | 400 | 模型配置无效 |
| DEPLOYMENT_FAILED | 500 | 部署失败 |
| INFERENCE_TIMEOUT | 408 | 推理超时 |
| INSUFFICIENT_RESOURCES | 503 | 资源不足 |

### 错误响应示例
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

## 📚 相关文档

- [API概览](overview.md)
- [健康检查API](health.md)
- [完整API参考](reference.md)