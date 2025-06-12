# 小艾智能体服务 API 文档

## 概述

小艾智能体服务是索克生活APP的核心AI健康管理服务，基于中医五诊协调理论，提供智能化的健康诊断、体质分析和个性化建议。

## 基础信息

- **服务名称**: xiaoai-service
- **版本**: v1.0.0
- **基础URL**: `https://api.suoke.life/xiaoai/v1`
- **协议**: HTTPS
- **认证**: Bearer Token

## 认证

所有API请求都需要在请求头中包含有效的访问令牌：

```http
Authorization: Bearer <your_access_token>
```

## 通用响应格式

### 成功响应

```json
{
  "success": true,
  "data": {
    // 具体数据内容
  },
  "message": "操作成功",
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_123456789"
}
```

### 错误响应

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {}
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_123456789"
}
```

## API 端点

### 1. 诊断会话管理

#### 1.1 创建诊断会话

创建新的诊断会话，用于管理用户的诊断流程。

```http
POST /sessions
```

**请求体**:
```json
{
  "user_id": "user_123456",
  "metadata": {
    "source": "mobile_app",
    "version": "1.0.0",
    "device_info": {
      "platform": "iOS",
      "version": "17.0"
    }
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "session_id": "session_789012",
    "user_id": "user_123456",
    "status": "active",
    "created_at": "2024-01-15T10:30:00Z",
    "expires_at": "2024-01-15T11:30:00Z",
    "metadata": {
      "source": "mobile_app",
      "version": "1.0.0"
    }
  }
}
```

#### 1.2 获取诊断会话

获取指定会话的详细信息。

```http
GET /sessions/{session_id}
```

**路径参数**:
- `session_id` (string): 会话ID

**响应**:
```json
{
  "success": true,
  "data": {
    "session_id": "session_789012",
    "user_id": "user_123456",
    "status": "active",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:35:00Z",
    "diagnosis_progress": {
      "completed_steps": ["looking", "listening"],
      "current_step": "inquiry",
      "total_steps": 4,
      "progress_percentage": 50
    }
  }
}
```

#### 1.3 关闭诊断会话

关闭指定的诊断会话。

```http
DELETE /sessions/{session_id}
```

**路径参数**:
- `session_id` (string): 会话ID

**响应**:
```json
{
  "success": true,
  "data": {
    "session_id": "session_789012",
    "status": "closed",
    "closed_at": "2024-01-15T10:45:00Z"
  }
}
```

### 2. 五诊协调

#### 2.1 开始诊断流程

启动完整的五诊协调诊断流程。

```http
POST /sessions/{session_id}/diagnosis
```

**路径参数**:
- `session_id` (string): 会话ID

**请求体**:
```json
{
  "diagnosis_data": {
    "looking": {
      "tongue_image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
      "face_image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
      "complexion": "红润",
      "spirit": "精神饱满",
      "body_shape": "匀称"
    },
    "listening": {
      "voice_audio": "data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEA...",
      "breathing_sound": "平稳",
      "cough_type": "无咳嗽",
      "voice_quality": "清晰"
    },
    "inquiry": {
      "chief_complaint": "最近感觉疲劳",
      "present_illness": "持续一周的疲劳感，伴有食欲不振",
      "past_history": "无特殊病史",
      "family_history": "父亲有高血压",
      "personal_history": "作息规律，饮食正常",
      "symptoms": ["疲劳", "食欲不振", "精神不振"]
    },
    "palpation": {
      "pulse_type": "脉象平和",
      "pulse_rate": 72,
      "pulse_strength": "中等",
      "pulse_rhythm": "规律",
      "abdomen_examination": "腹部柔软"
    }
  },
  "options": {
    "enable_ai_analysis": true,
    "include_recommendations": true,
    "accessibility_mode": false
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "diagnosis_id": "diag_345678",
    "session_id": "session_789012",
    "status": "processing",
    "estimated_completion_time": "2024-01-15T10:35:00Z",
    "progress": {
      "current_step": "looking",
      "completed_steps": [],
      "total_steps": 4
    }
  }
}
```

#### 2.2 获取诊断结果

获取诊断流程的结果。

```http
GET /sessions/{session_id}/diagnosis/{diagnosis_id}
```

**路径参数**:
- `session_id` (string): 会话ID
- `diagnosis_id` (string): 诊断ID

**响应**:
```json
{
  "success": true,
  "data": {
    "diagnosis_id": "diag_345678",
    "session_id": "session_789012",
    "status": "completed",
    "created_at": "2024-01-15T10:30:00Z",
    "completed_at": "2024-01-15T10:34:00Z",
    "processing_time_ms": 240000,
    "diagnosis_results": [
      {
        "diagnosis_type": "looking",
        "status": "completed",
        "confidence": 0.85,
        "features": {
          "tongue_color": "淡红",
          "tongue_coating": "薄白",
          "face_color": "红润",
          "spirit_state": "良好"
        },
        "analysis": "望诊显示整体状态良好，舌象正常",
        "processing_time_ms": 60000
      },
      {
        "diagnosis_type": "listening",
        "status": "completed",
        "confidence": 0.80,
        "features": {
          "voice_quality": "清晰",
          "breathing_pattern": "平稳",
          "sound_analysis": "无异常"
        },
        "analysis": "闻诊未发现异常，声音清晰",
        "processing_time_ms": 45000
      },
      {
        "diagnosis_type": "inquiry",
        "status": "completed",
        "confidence": 0.90,
        "features": {
          "symptom_severity": "轻度",
          "duration": "一周",
          "pattern": "持续性疲劳"
        },
        "analysis": "问诊提示气虚可能，建议进一步调理",
        "processing_time_ms": 75000
      },
      {
        "diagnosis_type": "palpation",
        "status": "completed",
        "confidence": 0.88,
        "features": {
          "pulse_category": "平脉",
          "pulse_characteristics": "和缓有力",
          "physical_signs": "正常"
        },
        "analysis": "切诊显示脉象正常，无明显异常",
        "processing_time_ms": 60000
      }
    ],
    "syndrome_analysis": {
      "primary_syndromes": [
        {
          "name": "气虚证",
          "confidence": 0.75,
          "description": "气虚证是指脏腑功能衰退所表现的证候"
        }
      ],
      "secondary_syndromes": [
        {
          "name": "脾胃虚弱",
          "confidence": 0.60,
          "description": "脾胃功能虚弱，运化失常"
        }
      ],
      "overall_confidence": 0.82,
      "analysis_method": "八纲辨证"
    },
    "constitution_analysis": {
      "primary_constitution": {
        "type": "气虚质",
        "score": 75,
        "description": "气虚质体质特征明显"
      },
      "constitution_scores": {
        "平和质": 45,
        "气虚质": 75,
        "阳虚质": 30,
        "阴虚质": 25,
        "痰湿质": 20,
        "湿热质": 15,
        "血瘀质": 10,
        "气郁质": 35,
        "特禀质": 5
      },
      "overall_confidence": 0.78
    }
  }
}
```

### 3. 多模态数据处理

#### 3.1 处理多模态数据

处理文本、图像、音频等多种模态的数据。

```http
POST /multimodal/process
```

**请求体**:
```json
{
  "inputs": [
    {
      "modality_type": "text",
      "data": "患者主诉：最近感觉疲劳乏力，食欲不振",
      "metadata": {
        "language": "zh",
        "source": "inquiry"
      }
    },
    {
      "modality_type": "image",
      "data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
      "metadata": {
        "image_type": "tongue",
        "resolution": [640, 480]
      }
    },
    {
      "modality_type": "audio",
      "data": "data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEA...",
      "metadata": {
        "format": "wav",
        "sample_rate": 16000,
        "duration": 5.2
      }
    }
  ],
  "options": {
    "parallel_processing": true,
    "include_features": true,
    "accessibility_mode": false
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "processing_id": "proc_456789",
    "results": [
      {
        "modality_type": "text",
        "status": "completed",
        "confidence": 0.85,
        "processed_data": {
          "symptoms": ["疲劳", "乏力", "食欲不振"],
          "sentiment": "negative",
          "severity": "mild"
        },
        "features": {
          "keyword_count": 3,
          "emotion_score": -0.3,
          "medical_terms": ["疲劳", "乏力", "食欲不振"]
        },
        "processing_time_ms": 120
      },
      {
        "modality_type": "image",
        "status": "completed",
        "confidence": 0.80,
        "processed_data": {
          "tongue_analysis": "舌淡红，苔薄白",
          "color_analysis": "淡红色",
          "coating_analysis": "薄白苔"
        },
        "features": {
          "color_rgb": [220, 180, 170],
          "coating_thickness": "thin",
          "moisture_level": "normal"
        },
        "processing_time_ms": 850
      },
      {
        "modality_type": "audio",
        "status": "completed",
        "confidence": 0.75,
        "processed_data": {
          "voice_analysis": "声音低微",
          "transcription": "我最近感觉很疲劳",
          "emotion": "tired"
        },
        "features": {
          "volume_db": -12.5,
          "pitch_hz": 180,
          "speech_rate": 2.1
        },
        "processing_time_ms": 1200
      }
    ],
    "total_processing_time_ms": 2170
  }
}
```

### 4. 个性化建议

#### 4.1 生成健康建议

基于诊断结果生成个性化的健康建议。

```http
POST /recommendations/generate
```

**请求体**:
```json
{
  "user_id": "user_123456",
  "session_id": "session_789012",
  "diagnosis_id": "diag_345678",
  "preferences": {
    "recommendation_types": ["diet", "exercise", "lifestyle", "emotion"],
    "difficulty_level": "moderate",
    "time_availability": "30_minutes_daily",
    "dietary_restrictions": ["vegetarian"],
    "exercise_limitations": []
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "recommendation_id": "rec_567890",
    "user_id": "user_123456",
    "generated_at": "2024-01-15T10:40:00Z",
    "overall_strategy": {
      "focus": "补气养血，调理脾胃",
      "duration": "4-6周",
      "expected_improvement": "疲劳感减轻，食欲改善"
    },
    "recommendations": [
      {
        "category": "diet",
        "priority": "high",
        "title": "补气养血饮食建议",
        "description": "选择温补脾胃的食物，避免生冷寒凉",
        "specific_items": [
          {
            "item": "山药粥",
            "frequency": "每日早餐",
            "benefits": "健脾益气，易于消化",
            "preparation": "山药100g，大米50g，煮粥食用"
          },
          {
            "item": "红枣桂圆茶",
            "frequency": "下午茶时间",
            "benefits": "补血安神，改善疲劳",
            "preparation": "红枣5颗，桂圆10颗，热水冲泡"
          }
        ],
        "contraindications": ["避免生冷食物", "少食辛辣刺激"],
        "duration": "持续4周"
      },
      {
        "category": "exercise",
        "priority": "medium",
        "title": "温和运动建议",
        "description": "选择温和的有氧运动，避免剧烈运动",
        "specific_items": [
          {
            "item": "太极拳",
            "frequency": "每日30分钟",
            "benefits": "调和气血，增强体质",
            "instructions": "选择简化24式太极拳"
          },
          {
            "item": "散步",
            "frequency": "饭后30分钟",
            "benefits": "促进消化，温和锻炼",
            "instructions": "慢步行走，避免快走"
          }
        ],
        "precautions": ["避免过度疲劳", "运动后注意保暖"],
        "duration": "逐步增加强度"
      },
      {
        "category": "lifestyle",
        "priority": "high",
        "title": "生活方式调整",
        "description": "规律作息，保证充足睡眠",
        "specific_items": [
          {
            "item": "规律睡眠",
            "frequency": "每日",
            "benefits": "恢复体力，调节内分泌",
            "instructions": "晚上10点前入睡，保证8小时睡眠"
          },
          {
            "item": "午休",
            "frequency": "每日",
            "benefits": "补充精力，缓解疲劳",
            "instructions": "午饭后休息30分钟"
          }
        ],
        "duration": "长期坚持"
      },
      {
        "category": "emotion",
        "priority": "medium",
        "title": "情志调节建议",
        "description": "保持心情愉悦，避免过度思虑",
        "specific_items": [
          {
            "item": "冥想放松",
            "frequency": "每日15分钟",
            "benefits": "缓解压力，平静心神",
            "instructions": "选择安静环境，专注呼吸"
          },
          {
            "item": "音乐疗法",
            "frequency": "睡前",
            "benefits": "舒缓情绪，促进睡眠",
            "instructions": "选择轻柔的古典音乐"
          }
        ],
        "duration": "根据个人情况调整"
      }
    ],
    "follow_up": {
      "next_assessment": "2024-01-29T10:00:00Z",
      "monitoring_indicators": ["疲劳程度", "食欲状况", "睡眠质量"],
      "adjustment_criteria": "如症状无改善，建议调整方案"
    }
  }
}
```

### 5. 无障碍服务

#### 5.1 文本转语音

将文本转换为语音，支持无障碍访问。

```http
POST /accessibility/tts
```

**请求体**:
```json
{
  "text": "您的体质分析结果显示为气虚质，建议多休息，适当进补",
  "options": {
    "voice": "female",
    "speed": 1.0,
    "pitch": 1.0,
    "language": "zh-CN",
    "format": "mp3"
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "audio_data": "data:audio/mp3;base64,SUQzBAAAAAAAI1RTU0UAAAAPAAADTGF2ZjU4Ljc2LjEwMAAAAAAAAAAAAAAA...",
    "duration_seconds": 8.5,
    "format": "mp3",
    "sample_rate": 22050,
    "generated_at": "2024-01-15T10:45:00Z"
  }
}
```

#### 5.2 语音转文本

将语音转换为文本。

```http
POST /accessibility/stt
```

**请求体**:
```json
{
  "audio_data": "data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEA...",
  "options": {
    "language": "zh-CN",
    "enable_punctuation": true,
    "filter_profanity": false
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "transcription": "我最近感觉很疲劳，食欲也不太好",
    "confidence": 0.92,
    "language_detected": "zh-CN",
    "processing_time_ms": 1500,
    "word_timestamps": [
      {"word": "我", "start": 0.1, "end": 0.3},
      {"word": "最近", "start": 0.4, "end": 0.8},
      {"word": "感觉", "start": 0.9, "end": 1.3}
    ]
  }
}
```

### 6. 健康检查

#### 6.1 服务健康状态

获取服务的健康状态和性能指标。

```http
GET /health
```

**响应**:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2024-01-15T10:50:00Z",
    "uptime": 86400,
    "response_time": 15.2,
    "components": {
      "database": {
        "status": "healthy",
        "response_time": 5.1,
        "last_check": "2024-01-15T10:50:00Z"
      },
      "redis": {
        "status": "healthy",
        "response_time": 2.3,
        "last_check": "2024-01-15T10:50:00Z"
      },
      "ai_models": {
        "status": "healthy",
        "loaded_models": 5,
        "total_memory_mb": 1024,
        "last_check": "2024-01-15T10:50:00Z"
      },
      "external_services": {
        "status": "healthy",
        "services_checked": ["look", "listen", "inquiry", "palpation"],
        "last_check": "2024-01-15T10:50:00Z"
      }
    },
    "system_metrics": {
      "cpu_usage": 25.5,
      "memory_usage": 68.2,
      "disk_usage": 45.8,
      "network_io": {
        "bytes_sent": 1048576,
        "bytes_recv": 2097152
      }
    }
  }
}
```

## 错误代码

| 错误代码 | HTTP状态码 | 描述 |
|---------|-----------|------|
| `INVALID_REQUEST` | 400 | 请求参数无效 |
| `UNAUTHORIZED` | 401 | 未授权访问 |
| `FORBIDDEN` | 403 | 禁止访问 |
| `NOT_FOUND` | 404 | 资源不存在 |
| `METHOD_NOT_ALLOWED` | 405 | 请求方法不允许 |
| `RATE_LIMIT_EXCEEDED` | 429 | 请求频率超限 |
| `INTERNAL_ERROR` | 500 | 服务器内部错误 |
| `SERVICE_UNAVAILABLE` | 503 | 服务不可用 |
| `SESSION_NOT_FOUND` | 404 | 会话不存在 |
| `SESSION_EXPIRED` | 410 | 会话已过期 |
| `DIAGNOSIS_IN_PROGRESS` | 409 | 诊断正在进行中 |
| `MODEL_NOT_AVAILABLE` | 503 | AI模型不可用 |
| `PROCESSING_FAILED` | 500 | 数据处理失败 |

## 限制和配额

- **请求频率限制**: 每分钟最多100个请求
- **文件大小限制**: 
  - 图像文件: 最大10MB
  - 音频文件: 最大50MB
  - 视频文件: 最大100MB
- **会话超时**: 1小时无活动自动过期
- **并发会话**: 每用户最多5个并发会话

## SDK和示例

### Python SDK示例

```python
from xiaoai_client import XiaoAIClient

# 初始化客户端
client = XiaoAIClient(
    base_url="https://api.suoke.life/xiaoai/v1",
    access_token="your_access_token"
)

# 创建诊断会话
session = await client.create_session(
    user_id="user_123456",
    metadata={"source": "mobile_app"}
)

# 开始诊断
diagnosis_data = {
    "looking": {"tongue_image": "base64_image_data"},
    "inquiry": {"chief_complaint": "疲劳乏力"}
}

diagnosis = await client.start_diagnosis(
    session_id=session.session_id,
    diagnosis_data=diagnosis_data
)

# 获取结果
result = await client.get_diagnosis_result(
    session_id=session.session_id,
    diagnosis_id=diagnosis.diagnosis_id
)

print(f"诊断结果: {result.syndrome_analysis}")
```

### JavaScript SDK示例

```javascript
import { XiaoAIClient } from '@suoke/xiaoai-client';

// 初始化客户端
const client = new XiaoAIClient({
  baseURL: 'https://api.suoke.life/xiaoai/v1',
  accessToken: 'your_access_token'
});

// 创建诊断会话
const session = await client.createSession({
  userId: 'user_123456',
  metadata: { source: 'web_app' }
});

// 开始诊断
const diagnosisData = {
  looking: { tongueImage: 'base64_image_data' },
  inquiry: { chiefComplaint: '疲劳乏力' }
};

const diagnosis = await client.startDiagnosis({
  sessionId: session.sessionId,
  diagnosisData
});

// 获取结果
const result = await client.getDiagnosisResult({
  sessionId: session.sessionId,
  diagnosisId: diagnosis.diagnosisId
});

console.log('诊断结果:', result.syndromeAnalysis);
```

## 更新日志

### v1.0.0 (2024-01-15)
- 初始版本发布
- 支持五诊协调诊断
- 支持多模态数据处理
- 支持个性化建议生成
- 支持无障碍服务
- 完整的API文档和SDK

## 支持和联系

- **技术支持**: tech-support@suoke.life
- **API问题**: api-support@suoke.life
- **文档反馈**: docs@suoke.life
- **GitHub**: https://github.com/SUOKE2024/suoke_life