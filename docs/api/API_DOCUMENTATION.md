# 索克生活 API 文档

## 概述

索克生活平台提供完整的RESTful API和gRPC接口，支持健康管理、智能体交互、区块链数据管理等功能。

## 基础信息

- **API版本**: v1.0
- **基础URL**: `https://api.suoke-life.com/v1`
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON
- **字符编码**: UTF-8

## 认证

所有API请求都需要在Header中包含认证信息：

```http
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

## 智能体服务 API

### 小艾服务 (XiaoAi Service)

**基础URL**: `/agents/xiaoai`

#### 1. 健康咨询

```http
POST /agents/xiaoai/consult
```

**请求参数**:
```json
{
  "user_id": "string",
  "message": "string",
  "context": {
    "symptoms": ["string"],
    "duration": "string",
    "severity": "mild|moderate|severe"
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "response": "string",
    "suggestions": ["string"],
    "confidence": 0.95,
    "follow_up_questions": ["string"]
  }
}
```

#### 2. 四诊分析

```http
POST /agents/xiaoai/diagnosis
```

**请求参数**:
```json
{
  "user_id": "string",
  "diagnosis_data": {
    "wang_zhen": {
      "tongue_image": "base64_string",
      "face_image": "base64_string"
    },
    "wen_zhen": {
      "voice_data": "base64_string",
      "breathing_pattern": "object"
    },
    "wen_zhen_inquiry": {
      "symptoms": ["string"],
      "medical_history": "string"
    },
    "qie_zhen": {
      "pulse_data": "object"
    }
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "constitution_type": "string",
    "health_score": 85,
    "recommendations": ["string"],
    "detailed_analysis": {
      "qi_blood_status": "string",
      "organ_health": "object",
      "lifestyle_advice": ["string"]
    }
  }
}
```

### 小克服务 (XiaoKe Service)

**基础URL**: `/agents/xiaoke`

#### 1. 健康数据分析

```http
POST /agents/xiaoke/analyze
```

**请求参数**:
```json
{
  "user_id": "string",
  "data_type": "health_metrics|lifestyle|nutrition",
  "data": "object",
  "time_range": {
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "analysis_result": "object",
    "trends": ["object"],
    "insights": ["string"],
    "recommendations": ["string"]
  }
}
```

#### 2. 个人健康档案

```http
GET /agents/xiaoke/profile/{user_id}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "user_profile": {
      "basic_info": "object",
      "health_metrics": "object",
      "medical_history": "object",
      "lifestyle_data": "object"
    },
    "last_updated": "2024-01-01T00:00:00Z"
  }
}
```

### 老克服务 (LaoKe Service)

**基础URL**: `/agents/laoke`

#### 1. 中医知识查询

```http
GET /agents/laoke/knowledge
```

**查询参数**:
- `query`: 搜索关键词
- `category`: 知识分类 (herbs|acupoints|theories|treatments)
- `limit`: 返回数量限制 (默认10)

**响应**:
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "title": "string",
        "content": "string",
        "category": "string",
        "source": "string",
        "confidence": 0.95
      }
    ],
    "total": 100
  }
}
```

#### 2. 辨证论治

```http
POST /agents/laoke/syndrome-differentiation
```

**请求参数**:
```json
{
  "user_id": "string",
  "symptoms": ["string"],
  "constitution": "string",
  "diagnosis_data": "object"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "syndrome": "string",
    "treatment_principle": "string",
    "herbal_formula": {
      "name": "string",
      "ingredients": ["object"],
      "dosage": "string",
      "usage": "string"
    },
    "lifestyle_advice": ["string"]
  }
}
```

### 索儿服务 (SoEr Service)

**基础URL**: `/agents/soer`

#### 1. 生活方式建议

```http
POST /agents/soer/lifestyle-advice
```

**请求参数**:
```json
{
  "user_id": "string",
  "current_lifestyle": {
    "sleep_pattern": "object",
    "exercise_routine": "object",
    "diet_habits": "object",
    "stress_level": "low|medium|high"
  },
  "goals": ["string"]
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "recommendations": [
      {
        "category": "sleep|exercise|nutrition|stress",
        "advice": "string",
        "priority": "high|medium|low",
        "implementation_steps": ["string"]
      }
    ],
    "personalized_plan": "object"
  }
}
```

## 健康数据服务 API

**基础URL**: `/health-data`

### 1. 健康指标记录

```http
POST /health-data/metrics
```

**请求参数**:
```json
{
  "user_id": "string",
  "metrics": {
    "blood_pressure": {
      "systolic": 120,
      "diastolic": 80,
      "timestamp": "2024-01-01T00:00:00Z"
    },
    "heart_rate": {
      "value": 72,
      "timestamp": "2024-01-01T00:00:00Z"
    },
    "weight": {
      "value": 70.5,
      "timestamp": "2024-01-01T00:00:00Z"
    }
  }
}
```

### 2. 健康报告生成

```http
GET /health-data/report/{user_id}
```

**查询参数**:
- `period`: 报告周期 (daily|weekly|monthly|yearly)
- `format`: 报告格式 (json|pdf)

## 区块链服务 API

**基础URL**: `/blockchain`

### 1. 健康数据上链

```http
POST /blockchain/store-health-data
```

**请求参数**:
```json
{
  "user_id": "string",
  "data_hash": "string",
  "data_type": "health_record|diagnosis_result|treatment_plan",
  "metadata": {
    "timestamp": "2024-01-01T00:00:00Z",
    "data_source": "string",
    "privacy_level": "public|private|restricted"
  }
}
```

### 2. 零知识证明验证

```http
POST /blockchain/verify-zkp
```

**请求参数**:
```json
{
  "proof": "string",
  "public_inputs": "object",
  "verification_key": "string"
}
```

## 诊断服务 API

### 望诊服务

**基础URL**: `/diagnosis/wang-zhen`

```http
POST /diagnosis/wang-zhen/analyze
```

**请求参数**:
```json
{
  "user_id": "string",
  "images": {
    "tongue": "base64_string",
    "face": "base64_string"
  }
}
```

### 闻诊服务

**基础URL**: `/diagnosis/wen-zhen`

```http
POST /diagnosis/wen-zhen/analyze
```

**请求参数**:
```json
{
  "user_id": "string",
  "audio_data": "base64_string",
  "duration": 30
}
```

### 问诊服务

**基础URL**: `/diagnosis/wen-zhen-inquiry`

```http
POST /diagnosis/wen-zhen-inquiry/session
```

**请求参数**:
```json
{
  "user_id": "string",
  "session_type": "initial|follow_up",
  "context": "object"
}
```

### 切诊服务

**基础URL**: `/diagnosis/qie-zhen`

```http
POST /diagnosis/qie-zhen/analyze
```

**请求参数**:
```json
{
  "user_id": "string",
  "pulse_data": {
    "waveform": "array",
    "duration": 60,
    "sampling_rate": 1000
  }
}
```

## 错误处理

所有API都使用统一的错误响应格式：

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": "详细错误信息"
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 常见错误码

- `AUTH_001`: 认证失败
- `AUTH_002`: Token过期
- `PARAM_001`: 参数缺失
- `PARAM_002`: 参数格式错误
- `RATE_001`: 请求频率超限
- `SERVER_001`: 服务器内部错误
- `SERVICE_001`: 服务不可用

## 限流规则

- 普通用户：100请求/分钟
- VIP用户：500请求/分钟
- 企业用户：1000请求/分钟

## SDK和示例

### JavaScript SDK

```javascript
import { SuokeLifeAPI } from '@suoke-life/sdk';

const client = new SuokeLifeAPI({
  apiKey: 'your_api_key',
  baseURL: 'https://api.suoke-life.com/v1'
});

// 健康咨询
const response = await client.xiaoai.consult({
  user_id: 'user123',
  message: '我最近感觉疲劳，该怎么办？'
});
```

### Python SDK

```python
from suoke_life import SuokeLifeClient

client = SuokeLifeClient(
    api_key='your_api_key',
    base_url='https://api.suoke-life.com/v1'
)

# 健康数据分析
result = client.xiaoke.analyze({
    'user_id': 'user123',
    'data_type': 'health_metrics',
    'data': {...}
})
```

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 支持四大智能体服务
- 完整的健康数据管理
- 区块链数据存储

---

**文档更新时间**: 2024-01-01  
**联系方式**: api-support@suoke-life.com 