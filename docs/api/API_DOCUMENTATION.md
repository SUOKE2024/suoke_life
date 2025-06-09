# 索克生活 API 文档

## 概述

索克生活平台提供了一套完整的RESTful API，支持健康管理、智能体交互、区块链操作等核心功能。本文档详细描述了所有可用的API端点、请求格式和响应结构。

## 基础信息

- **基础URL**: `https://api.suoke.life`
- **API版本**: v1
- **认证方式**: Bearer Token (JWT)
- **内容类型**: `application/json`
- **字符编码**: UTF-8

## 认证

所有API请求都需要在请求头中包含有效的访问令牌：

```http
Authorization: Bearer <access_token>
```

### 获取访问令牌

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**响应示例**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

## API端点

### 1. 用户管理服务 (User Management Service)

#### 1.1 用户注册

```http
POST /api/users/register
```

**请求体**:
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "phone": "string",
  "profile": {
    "name": "string",
    "age": "integer",
    "gender": "string",
    "height": "number",
    "weight": "number"
  }
}
```

**响应**:
```json
{
  "user_id": "uuid",
  "username": "string",
  "email": "string",
  "created_at": "datetime",
  "profile": {
    "name": "string",
    "age": "integer",
    "gender": "string"
  }
}
```

#### 1.2 获取用户信息

```http
GET /api/users/profile
```

**响应**:
```json
{
  "user_id": "uuid",
  "username": "string",
  "email": "string",
  "profile": {
    "name": "string",
    "age": "integer",
    "gender": "string",
    "height": "number",
    "weight": "number",
    "medical_history": ["string"]
  },
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### 1.3 更新用户信息

```http
PUT /api/users/profile
```

**请求体**:
```json
{
  "profile": {
    "name": "string",
    "age": "integer",
    "height": "number",
    "weight": "number"
  }
}
```

### 2. 健康数据服务 (Health Data Service)

#### 2.1 提交健康数据

```http
POST /api/health/data
```

**请求体**:
```json
{
  "type": "string", // "vital_signs", "symptoms", "medication", "exercise"
  "data": {
    "timestamp": "datetime",
    "values": {
      "heart_rate": "number",
      "blood_pressure": {
        "systolic": "number",
        "diastolic": "number"
      },
      "temperature": "number",
      "weight": "number"
    }
  },
  "source": "string", // "manual", "device", "wearable"
  "device_id": "string"
}
```

**响应**:
```json
{
  "record_id": "uuid",
  "user_id": "uuid",
  "type": "string",
  "timestamp": "datetime",
  "status": "processed",
  "blockchain_hash": "string"
}
```

#### 2.2 查询健康数据

```http
GET /api/health/data?type={type}&start_date={date}&end_date={date}&limit={number}
```

**查询参数**:
- `type`: 数据类型 (可选)
- `start_date`: 开始日期 (ISO 8601格式)
- `end_date`: 结束日期 (ISO 8601格式)
- `limit`: 返回记录数量限制 (默认100)

**响应**:
```json
{
  "data": [
    {
      "record_id": "uuid",
      "type": "string",
      "timestamp": "datetime",
      "values": {},
      "source": "string"
    }
  ],
  "total": "integer",
  "page": "integer",
  "limit": "integer"
}
```

#### 2.3 生成健康报告

```http
POST /api/health/reports/generate
```

**请求体**:
```json
{
  "report_type": "string", // "weekly", "monthly", "comprehensive"
  "date_range": {
    "start_date": "date",
    "end_date": "date"
  },
  "include_recommendations": "boolean"
}
```

**响应**:
```json
{
  "report_id": "uuid",
  "status": "generating",
  "estimated_completion": "datetime"
}
```

#### 2.4 获取健康报告

```http
GET /api/health/reports/{report_id}
```

**响应**:
```json
{
  "report_id": "uuid",
  "user_id": "uuid",
  "type": "string",
  "generated_at": "datetime",
  "status": "completed",
  "data": {
    "summary": {
      "overall_score": "number",
      "trend": "string",
      "key_insights": ["string"]
    },
    "vital_signs": {
      "average_heart_rate": "number",
      "blood_pressure_trend": "string",
      "weight_change": "number"
    },
    "recommendations": [
      {
        "category": "string",
        "priority": "string",
        "description": "string",
        "action_items": ["string"]
      }
    ]
  }
}
```

### 3. 智能体服务 (Agent Services)

#### 3.1 小艾智能体 - 健康咨询

```http
POST /api/agents/xiaoai/chat
```

**请求体**:
```json
{
  "message": "string",
  "context": "string", // "health_consultation", "lifestyle_advice", "general"
  "conversation_id": "uuid", // 可选，用于维持对话上下文
  "user_data": {
    "recent_symptoms": ["string"],
    "current_medications": ["string"],
    "lifestyle_factors": {}
  }
}
```

**响应**:
```json
{
  "response": "string",
  "conversation_id": "uuid",
  "confidence": "number",
  "recommendations": [
    {
      "type": "string",
      "description": "string",
      "priority": "string"
    }
  ],
  "follow_up_questions": ["string"],
  "timestamp": "datetime"
}
```

#### 3.2 小克智能体 - 症状诊断

```http
POST /api/agents/xiaoke/diagnose
```

**请求体**:
```json
{
  "symptoms": [
    {
      "name": "string",
      "severity": "integer", // 1-10
      "duration": "string",
      "frequency": "string"
    }
  ],
  "patient_info": {
    "age": "integer",
    "gender": "string",
    "medical_history": ["string"],
    "current_medications": ["string"]
  },
  "additional_info": "string"
}
```

**响应**:
```json
{
  "diagnosis_id": "uuid",
  "primary_diagnosis": {
    "condition": "string",
    "confidence": "number",
    "description": "string"
  },
  "differential_diagnosis": [
    {
      "condition": "string",
      "confidence": "number",
      "reasoning": "string"
    }
  ],
  "recommendations": {
    "immediate_actions": ["string"],
    "lifestyle_changes": ["string"],
    "follow_up": "string",
    "red_flags": ["string"]
  },
  "tcm_analysis": {
    "syndrome": "string",
    "constitution": "string",
    "treatment_principle": "string"
  },
  "timestamp": "datetime"
}
```

#### 3.3 老克智能体 - 中医调理

```http
POST /api/agents/laoke/treatment
```

**请求体**:
```json
{
  "diagnosis": "string",
  "constitution": "string",
  "symptoms": ["string"],
  "treatment_goals": ["string"],
  "preferences": {
    "treatment_type": ["acupuncture", "herbal", "lifestyle"],
    "intensity": "string",
    "duration": "string"
  }
}
```

**响应**:
```json
{
  "treatment_plan_id": "uuid",
  "treatment_plan": {
    "principle": "string",
    "duration": "string",
    "phases": [
      {
        "phase": "string",
        "duration": "string",
        "goals": ["string"],
        "methods": [
          {
            "type": "string",
            "description": "string",
            "frequency": "string",
            "notes": "string"
          }
        ]
      }
    ]
  },
  "herbal_formula": {
    "name": "string",
    "ingredients": [
      {
        "herb": "string",
        "dosage": "string",
        "function": "string"
      }
    ],
    "preparation": "string",
    "usage": "string"
  },
  "lifestyle_recommendations": {
    "diet": ["string"],
    "exercise": ["string"],
    "sleep": ["string"],
    "emotional": ["string"]
  },
  "monitoring": {
    "indicators": ["string"],
    "frequency": "string",
    "adjustments": ["string"]
  }
}
```

#### 3.4 索儿智能体 - 健康教育

```http
POST /api/agents/soer/educate
```

**请求体**:
```json
{
  "topic": "string",
  "user_level": "string", // "beginner", "intermediate", "advanced"
  "format": "string", // "article", "video", "interactive", "quiz"
  "personalization": {
    "age_group": "string",
    "health_conditions": ["string"],
    "interests": ["string"]
  }
}
```

**响应**:
```json
{
  "content_id": "uuid",
  "title": "string",
  "content": {
    "text": "string",
    "media": [
      {
        "type": "string",
        "url": "string",
        "description": "string"
      }
    ],
    "interactive_elements": [
      {
        "type": "string",
        "data": {}
      }
    ]
  },
  "learning_objectives": ["string"],
  "key_takeaways": ["string"],
  "related_topics": ["string"],
  "difficulty_level": "string",
  "estimated_time": "integer"
}
```

### 4. 区块链服务 (Blockchain Service)

#### 4.1 创建健康记录哈希

```http
POST /api/blockchain/create-hash
```

**请求体**:
```json
{
  "data": {
    "record_id": "uuid",
    "user_id": "uuid",
    "timestamp": "datetime",
    "data_hash": "string",
    "metadata": {}
  },
  "privacy_level": "string" // "public", "private", "semi_private"
}
```

**响应**:
```json
{
  "transaction_id": "string",
  "block_hash": "string",
  "timestamp": "datetime",
  "status": "pending",
  "gas_used": "number"
}
```

#### 4.2 验证健康记录

```http
POST /api/blockchain/verify
```

**请求体**:
```json
{
  "record_id": "uuid",
  "data_hash": "string",
  "transaction_id": "string"
}
```

**响应**:
```json
{
  "is_valid": "boolean",
  "verification_details": {
    "block_number": "integer",
    "transaction_hash": "string",
    "timestamp": "datetime",
    "confirmations": "integer"
  },
  "integrity_check": {
    "data_match": "boolean",
    "timestamp_valid": "boolean",
    "signature_valid": "boolean"
  }
}
```

#### 4.3 查询区块链记录

```http
GET /api/blockchain/records?user_id={uuid}&start_date={date}&end_date={date}
```

**响应**:
```json
{
  "records": [
    {
      "record_id": "uuid",
      "transaction_id": "string",
      "block_hash": "string",
      "timestamp": "datetime",
      "data_type": "string",
      "privacy_level": "string",
      "status": "confirmed"
    }
  ],
  "total": "integer",
  "blockchain_info": {
    "network": "string",
    "latest_block": "integer",
    "gas_price": "number"
  }
}
```

### 5. 诊断服务 (Diagnostic Services)

#### 5.1 望诊 - 图像分析

```http
POST /api/diagnostic/look/analyze
```

**请求体** (multipart/form-data):
```
image: file (支持 jpg, png, 最大10MB)
analysis_type: string ("tongue", "face", "skin", "eyes")
metadata: json {
  "lighting_conditions": "string",
  "image_quality": "string",
  "patient_age": "integer",
  "patient_gender": "string"
}
```

**响应**:
```json
{
  "analysis_id": "uuid",
  "analysis_type": "string",
  "results": {
    "overall_assessment": "string",
    "specific_findings": [
      {
        "feature": "string",
        "description": "string",
        "significance": "string",
        "confidence": "number"
      }
    ],
    "tcm_interpretation": {
      "constitution": "string",
      "pathological_patterns": ["string"],
      "organ_systems": ["string"]
    }
  },
  "recommendations": ["string"],
  "confidence_score": "number",
  "processing_time": "number"
}
```

#### 5.2 闻诊 - 声音分析

```http
POST /api/diagnostic/listen/analyze
```

**请求体** (multipart/form-data):
```
audio: file (支持 wav, mp3, 最大50MB)
analysis_type: string ("voice", "breathing", "cough", "heartbeat")
duration: integer (录音时长，秒)
```

**响应**:
```json
{
  "analysis_id": "uuid",
  "audio_quality": {
    "clarity": "number",
    "noise_level": "number",
    "duration": "number"
  },
  "analysis_results": {
    "voice_characteristics": {
      "pitch": "string",
      "tone": "string",
      "strength": "string",
      "rhythm": "string"
    },
    "breathing_pattern": {
      "rate": "number",
      "depth": "string",
      "regularity": "string"
    },
    "abnormal_sounds": ["string"]
  },
  "tcm_assessment": {
    "qi_condition": "string",
    "organ_function": ["string"],
    "pathological_indicators": ["string"]
  },
  "recommendations": ["string"]
}
```

#### 5.3 问诊 - 智能问诊

```http
POST /api/diagnostic/inquiry/session
```

**请求体**:
```json
{
  "session_type": "string", // "initial", "follow_up", "symptom_specific"
  "patient_info": {
    "age": "integer",
    "gender": "string",
    "chief_complaint": "string"
  },
  "previous_session_id": "uuid" // 可选，用于继续之前的问诊
}
```

**响应**:
```json
{
  "session_id": "uuid",
  "current_question": {
    "question_id": "string",
    "text": "string",
    "type": "string", // "multiple_choice", "scale", "text", "yes_no"
    "options": ["string"], // 仅用于选择题
    "context": "string"
  },
  "progress": {
    "completed_questions": "integer",
    "total_estimated": "integer",
    "completion_percentage": "number"
  },
  "session_status": "string" // "active", "completed", "paused"
}
```

#### 5.4 提交问诊答案

```http
POST /api/diagnostic/inquiry/answer
```

**请求体**:
```json
{
  "session_id": "uuid",
  "question_id": "string",
  "answer": "string", // 或 number，根据问题类型
  "confidence": "number", // 可选，用户对答案的确信度
  "additional_notes": "string" // 可选
}
```

**响应**:
```json
{
  "next_question": {
    "question_id": "string",
    "text": "string",
    "type": "string",
    "options": ["string"]
  },
  "session_complete": "boolean",
  "preliminary_assessment": {
    "symptom_clusters": ["string"],
    "severity_indicators": ["string"],
    "urgency_level": "string"
  }
}
```

#### 5.5 切诊 - 脉象分析

```http
POST /api/diagnostic/palpation/pulse
```

**请求体**:
```json
{
  "measurement_data": {
    "duration": "integer", // 测量时长（秒）
    "sensor_data": [
      {
        "timestamp": "number",
        "pressure": "number",
        "position": "string" // "cun", "guan", "chi"
      }
    ],
    "measurement_conditions": {
      "patient_position": "string",
      "room_temperature": "number",
      "time_of_day": "string"
    }
  },
  "patient_state": {
    "recent_activity": "string",
    "emotional_state": "string",
    "medications": ["string"]
  }
}
```

**响应**:
```json
{
  "pulse_analysis": {
    "rate": "number",
    "rhythm": "string",
    "strength": "string",
    "depth": "string",
    "width": "string",
    "length": "string"
  },
  "pulse_qualities": [
    {
      "quality": "string",
      "description": "string",
      "clinical_significance": "string"
    }
  ],
  "tcm_interpretation": {
    "organ_systems": ["string"],
    "qi_blood_status": "string",
    "pathological_patterns": ["string"],
    "constitution_type": "string"
  },
  "recommendations": {
    "immediate": ["string"],
    "lifestyle": ["string"],
    "follow_up": "string"
  }
}
```

## 错误处理

所有API端点都使用标准的HTTP状态码，并返回统一格式的错误响应：

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": "string",
    "timestamp": "datetime",
    "request_id": "uuid"
  }
}
```

### 常见错误码

- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 未授权访问
- `403 Forbidden`: 权限不足
- `404 Not Found`: 资源不存在
- `429 Too Many Requests`: 请求频率超限
- `500 Internal Server Error`: 服务器内部错误
- `503 Service Unavailable`: 服务暂时不可用

## 速率限制

为了保护系统稳定性，API实施了速率限制：

- **标准用户**: 每分钟100次请求
- **高级用户**: 每分钟500次请求
- **企业用户**: 每分钟2000次请求

超出限制时，将返回`429 Too Many Requests`状态码。

## 数据格式

### 日期时间格式

所有日期时间字段都使用ISO 8601格式：
```
2024-01-15T10:30:00Z
```

### 数值精度

- 体重、身高等测量值：保留2位小数
- 温度：保留1位小数
- 血压：整数值
- 心率：整数值

## SDK和示例代码

我们提供了多种编程语言的SDK：

- [JavaScript/TypeScript SDK](https://github.com/suoke-life/sdk-js)
- [Python SDK](https://github.com/suoke-life/sdk-python)
- [Java SDK](https://github.com/suoke-life/sdk-java)
- [Swift SDK](https://github.com/suoke-life/sdk-swift)

## 支持和反馈

如有API使用问题或建议，请联系：

- 技术支持邮箱: api-support@suoke.life
- 开发者社区: https://community.suoke.life
- GitHub Issues: https://github.com/suoke-life/api-issues

---

*最后更新: 2024年1月15日*
*API版本: v1.0.0* 