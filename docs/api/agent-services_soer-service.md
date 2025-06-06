# Agent Services Soer Service API 文档

## 服务概述

**服务名称**: agent-services/soer-service  
**版本**: 1.0.0  
**描述**: 索儿智能体服务主入口
LIFE频道版主，提供生活健康管理、陪伴服务和数据整合分析

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

#### GET /

**功能**: 健康检查端点
返回服务的整体健康状态

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

#### GET /ready

**功能**: 就绪检查端点
检查服务是否准备好接收请求

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

#### GET /live

**功能**: 存活检查端点
检查服务是否仍在运行

**函数**: `liveness_check`

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

**功能**: 指标端点
返回Prometheus格式的指标

**函数**: `metrics_endpoint`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### GET /version

**功能**: 版本信息端点

**函数**: `version_info`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### GET /mappings/tcm

**功能**: 获取中医情志理论映射

**函数**: `get_tcm_emotion_mappings`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### GET /interventions

**功能**: 获取情绪干预策略

**函数**: `get_intervention_strategies`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### GET /{plan_id}

**功能**: 获取特定健康计划

**函数**: `get_health_plan`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### GET /

**功能**: GET /

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

#### GET /health-plans/{plan_id}

**功能**: GET /health-plans/{plan_id}

**函数**: `get_health_plan`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### GET /users/{user_id}/active-plan

**功能**: GET /users/{user_id}/active-plan

**函数**: `get_active_plan`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### GET /users/{user_id}/health-profile

**功能**: GET /users/{user_id}/health-profile

**函数**: `get_health_profile`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### GET /food/{food_name}

**功能**: GET /food/{food_name}

**函数**: `get_food_details`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### GET /constitutions/{constitution_type}/recipes

**功能**: GET /constitutions/{constitution_type}/recipes

**函数**: `get_recipes_by_constitution`

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

#### GET /

**功能**: 服务健康检查

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

#### GET /readiness

**功能**: 服务就绪检查

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

#### GET /liveness

**功能**: 服务存活检查

**函数**: `liveness_check`

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

#### POST /agent/analyze-health-data

**功能**: POST /agent/analyze-health-data

**函数**: `analyze_health_data`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### POST /agent/create-lifestyle-plan

**功能**: POST /agent/create-lifestyle-plan

**函数**: `create_lifestyle_plan`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### POST /agent/companion-chat

**功能**: POST /agent/companion-chat

**函数**: `companion_chat`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### POST /agent/coordinate-devices

**功能**: POST /agent/coordinate-devices

**函数**: `coordinate_devices`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### POST /analyze

**功能**: 分析情绪状态

**函数**: `analyze_emotional_state`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### POST /analyze/text

**功能**: POST /analyze/text

**函数**: `analyze_text_emotion`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### POST /analyze/voice

**功能**: POST /analyze/voice

**函数**: `analyze_voice_emotion`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### POST /

**功能**: 创建新的健康计划

**函数**: `create_health_plan`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### POST /progress

**功能**: 更新健康计划进度

**函数**: `update_health_plan_progress`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### POST /health-plans

**功能**: POST /health-plans

**函数**: `generate_health_plan`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### POST /users/{user_id}/sensor-data/analyze

**功能**: POST /users/{user_id}/sensor-data/analyze

**函数**: `analyze_sensor_data`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### POST /users/{user_id}/nutrition/track

**功能**: POST /users/{user_id}/nutrition/track

**函数**: `track_nutrition`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### POST /users/{user_id}/diet-recommendations

**功能**: POST /users/{user_id}/diet-recommendations

**函数**: `generate_diet_recommendations`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### POST /users/{user_id}/abnormal-patterns/detect

**功能**: POST /users/{user_id}/abnormal-patterns/detect

**函数**: `detect_abnormal_patterns`

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

#### POST /users/{user_id}/health-trends/predict

**功能**: POST /users/{user_id}/health-trends/predict

**函数**: `predict_health_trends`

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

### HealthStatus

健康状态模型

```python
class HealthStatus(BaseModel):
    # 字段定义
    pass
```

### ComponentHealth

组件健康状态

```python
class ComponentHealth(BaseModel):
    # 字段定义
    pass
```

### EmotionalInput

数据模型: EmotionalInput

```python
class EmotionalInput(BaseModel):
    # 字段定义
    pass
```

### EmotionalAnalysisRequest

数据模型: EmotionalAnalysisRequest

```python
class EmotionalAnalysisRequest(BaseModel):
    # 字段定义
    pass
```

### HealthImpact

数据模型: HealthImpact

```python
class HealthImpact(BaseModel):
    # 字段定义
    pass
```

### Suggestion

数据模型: Suggestion

```python
class Suggestion(BaseModel):
    # 字段定义
    pass
```

### EmotionalAnalysisResponse

数据模型: EmotionalAnalysisResponse

```python
class EmotionalAnalysisResponse(BaseModel):
    # 字段定义
    pass
```

### HealthPlanRequest

健康计划请求模型

```python
class HealthPlanRequest(BaseModel):
    # 字段定义
    pass
```

### HealthPlanResponse

健康计划响应模型

```python
class HealthPlanResponse(BaseModel):
    # 字段定义
    pass
```

### HealthPlanProgressRequest

健康计划进度更新请求

```python
class HealthPlanProgressRequest(BaseModel):
    # 字段定义
    pass
```

### HealthPlanProgressResponse

健康计划进度响应

```python
class HealthPlanProgressResponse(BaseModel):
    # 字段定义
    pass
```

### HealthStatus

健康状态模型

```python
class HealthStatus(BaseModel):
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

