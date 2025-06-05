# 索克生活用户服务 API 文档

## 概述

索克生活用户服务提供用户管理、设备管理、健康数据管理等核心功能。本文档详细描述了所有可用的API端点。

## 基础信息

- **基础URL**: `https://api.suoke.life/user-service/api/v1`
- **认证方式**: Bearer Token (JWT)
- **内容类型**: `application/json`
- **API版本**: v1.0.0

## 认证

所有API请求都需要在请求头中包含有效的JWT令牌：

```http
Authorization: Bearer <your_jwt_token>
```

## 用户管理 API

### 1. 获取用户信息

```http
GET /users/profile
```

**描述**: 获取当前用户的详细信息

**请求头**:
```http
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "user_123",
    "username": "zhang_san",
    "email": "zhang.san@example.com",
    "phone": "+86-13800138000",
    "profile": {
      "nickname": "张三",
      "avatar": "https://cdn.suoke.life/avatars/user_123.jpg",
      "gender": "male",
      "birth_date": "1990-01-01",
      "height": 175,
      "weight": 70
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

### 2. 更新用户信息

```http
PUT /users/profile
```

**请求体**:
```json
{
  "profile": {
    "nickname": "张三三",
    "gender": "male",
    "birth_date": "1990-01-01",
    "height": 175,
    "weight": 72
  }
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "用户信息更新成功",
  "data": {
    "updated_fields": ["nickname", "weight"],
    "updated_at": "2024-01-15T10:35:00Z"
  }
}
```

### 3. 上传用户头像

```http
POST /users/avatar
```

**请求类型**: `multipart/form-data`

**请求参数**:
- `file`: 图片文件 (支持 jpg, png, gif，最大5MB)

**响应示例**:
```json
{
  "code": 200,
  "message": "头像上传成功",
  "data": {
    "avatar_url": "https://cdn.suoke.life/avatars/user_123_new.jpg"
  }
}
```

## 设备管理 API

### 4. 获取设备列表

```http
GET /devices
```

**查询参数**:
- `page`: 页码 (默认: 1)
- `size`: 每页数量 (默认: 20)
- `status`: 设备状态 (active, inactive, all)

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "devices": [
      {
        "id": "device_001",
        "name": "智能手环",
        "type": "wearable",
        "model": "SuokeWatch Pro",
        "status": "active",
        "battery_level": 85,
        "last_sync": "2024-01-15T10:00:00Z",
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 1,
      "pages": 1
    }
  }
}
```

### 5. 添加设备

```http
POST /devices
```

**请求体**:
```json
{
  "name": "智能血压计",
  "type": "medical",
  "model": "SuokeBP-2024",
  "serial_number": "BP202401001"
}
```

**响应示例**:
```json
{
  "code": 201,
  "message": "设备添加成功",
  "data": {
    "id": "device_002",
    "name": "智能血压计",
    "type": "medical",
    "model": "SuokeBP-2024",
    "status": "active",
    "created_at": "2024-01-15T10:40:00Z"
  }
}
```

### 6. 更新设备信息

```http
PUT /devices/{device_id}
```

**路径参数**:
- `device_id`: 设备ID

**请求体**:
```json
{
  "name": "智能血压计 Pro",
  "status": "active"
}
```

### 7. 删除设备

```http
DELETE /devices/{device_id}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "设备删除成功"
}
```

## 健康数据 API

### 8. 获取健康数据

```http
GET /health-data
```

**查询参数**:
- `type`: 数据类型 (heart_rate, blood_pressure, weight, steps, sleep)
- `start_date`: 开始日期 (YYYY-MM-DD)
- `end_date`: 结束日期 (YYYY-MM-DD)
- `device_id`: 设备ID (可选)

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "type": "heart_rate",
    "records": [
      {
        "id": "hr_001",
        "value": 72,
        "unit": "bpm",
        "device_id": "device_001",
        "recorded_at": "2024-01-15T10:00:00Z"
      }
    ],
    "summary": {
      "count": 1,
      "avg": 72,
      "min": 72,
      "max": 72
    }
  }
}
```

### 9. 添加健康数据

```http
POST /health-data
```

**请求体**:
```json
{
  "type": "blood_pressure",
  "value": {
    "systolic": 120,
    "diastolic": 80
  },
  "unit": "mmHg",
  "device_id": "device_002",
  "recorded_at": "2024-01-15T11:00:00Z"
}
```

### 10. 获取健康报告

```http
GET /health-data/reports
```

**查询参数**:
- `period`: 报告周期 (daily, weekly, monthly)
- `date`: 报告日期

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "period": "weekly",
    "date": "2024-01-15",
    "summary": {
      "steps": {
        "total": 70000,
        "daily_avg": 10000,
        "goal_completion": 85
      },
      "heart_rate": {
        "avg": 75,
        "resting": 65,
        "max": 150
      },
      "sleep": {
        "avg_duration": 7.5,
        "quality_score": 85
      }
    }
  }
}
```

## 中医体质分析 API

### 11. 获取体质分析

```http
GET /tcm/constitution
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "constitution_type": "qi_deficiency",
    "constitution_name": "气虚质",
    "score": 75,
    "characteristics": [
      "容易疲劳",
      "气短懒言",
      "容易出汗"
    ],
    "recommendations": {
      "diet": ["多食用补气食物", "避免生冷食物"],
      "exercise": ["适量有氧运动", "避免剧烈运动"],
      "lifestyle": ["规律作息", "避免过度劳累"]
    },
    "last_updated": "2024-01-15T10:00:00Z"
  }
}
```

### 12. 提交体质问卷

```http
POST /tcm/constitution/questionnaire
```

**请求体**:
```json
{
  "answers": [
    {
      "question_id": "q1",
      "answer": 3
    },
    {
      "question_id": "q2", 
      "answer": 2
    }
  ]
}
```

### 13. 获取中医建议

```http
GET /tcm/recommendations
```

**查询参数**:
- `category`: 建议类别 (diet, exercise, lifestyle, herbs)

## 数据导出 API

### 14. 导出健康数据

```http
POST /export/health-data
```

**请求体**:
```json
{
  "format": "csv",
  "data_types": ["heart_rate", "blood_pressure", "weight"],
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "导出任务已创建",
  "data": {
    "task_id": "export_001",
    "status": "processing",
    "estimated_completion": "2024-01-15T11:05:00Z"
  }
}
```

### 15. 获取导出状态

```http
GET /export/tasks/{task_id}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "task_id": "export_001",
    "status": "completed",
    "download_url": "https://cdn.suoke.life/exports/export_001.csv",
    "expires_at": "2024-01-22T11:05:00Z"
  }
}
```

## 通知设置 API

### 16. 获取通知设置

```http
GET /notifications/settings
```

### 17. 更新通知设置

```http
PUT /notifications/settings
```

**请求体**:
```json
{
  "email_notifications": true,
  "push_notifications": true,
  "sms_notifications": false,
  "notification_types": {
    "health_alerts": true,
    "device_status": true,
    "weekly_reports": true
  }
}
```

## 隐私设置 API

### 18. 获取隐私设置

```http
GET /privacy/settings
```

### 19. 更新隐私设置

```http
PUT /privacy/settings
```

### 20. 数据删除请求

```http
POST /privacy/delete-request
```

## 错误代码

| 错误代码 | HTTP状态码 | 描述 |
|---------|-----------|------|
| USER_NOT_FOUND | 404 | 用户不存在 |
| DEVICE_NOT_FOUND | 404 | 设备不存在 |
| INVALID_DATA_TYPE | 400 | 无效的数据类型 |
| UPLOAD_FAILED | 400 | 文件上传失败 |
| EXPORT_FAILED | 500 | 数据导出失败 |
| RATE_LIMIT_EXCEEDED | 429 | 请求频率超限 |
| INSUFFICIENT_PERMISSIONS | 403 | 权限不足 |

## 状态码说明

- `200`: 请求成功
- `201`: 创建成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 禁止访问
- `404`: 资源不存在
- `429`: 请求过于频繁
- `500`: 服务器内部错误

## SDK 示例

### Python SDK

```python
from suoke_user_service import UserServiceClient

client = UserServiceClient(
    base_url="https://api.suoke.life/user-service",
    token="your_jwt_token"
)

# 获取用户信息
user = client.get_user_profile()

# 添加健康数据
client.add_health_data(
    type="heart_rate",
    value=75,
    device_id="device_001"
)
```

### JavaScript SDK

```javascript
import { UserServiceClient } from '@suoke/user-service-sdk';

const client = new UserServiceClient({
  baseURL: 'https://api.suoke.life/user-service',
  token: 'your_jwt_token'
});

// 获取设备列表
const devices = await client.getDevices();

// 获取健康报告
const report = await client.getHealthReport('weekly', '2024-01-15');
```

## 更新日志

### v1.0.0 (2024-01-15)
- 初始版本发布
- 支持用户管理、设备管理、健康数据管理
- 中医体质分析功能
- 数据导出功能 