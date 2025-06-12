# 小艾智能体服务 API 文档

## 概述

小艾智能体服务提供基于中医五诊协调理论的智能健康诊断API。本文档详细描述了所有可用的API接口、请求格式、响应格式和错误处理。

## 基础信息

- **基础URL**: `https://api.suoke.life/xiaoai/v1`
- **认证方式**: Bearer Token
- **内容类型**: `application/json`
- **API版本**: v1.0.0

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
  "timestamp": "2024-12-19T10:30:00Z",
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
    "details": {
      // 详细错误信息
    }
  },
  "timestamp": "2024-12-19T10:30:00Z",
  "request_id": "req_123456789"
}
```

## API 接口

### 1. 会话管理

#### 1.1 创建诊断会话

创建新的诊断会话，用于管理整个诊断流程。

**请求**

```http
POST /sessions
Content-Type: application/json
Authorization: Bearer <token>

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

**响应**

```json
{
  "success": true,
  "data": {
    "session_id": "session_abc123",
    "user_id": "user_123456",
    "status": "active",
    "created_at": "2024-12-19T10:30:00Z",
    "expires_at": "2024-12-19T12:30:00Z",
    "metadata": {
      "source": "mobile_app",
      "version": "1.0.0"
    }
  },
  "message": "会话创建成功",
  "timestamp": "2024-12-19T10:30:00Z",
  "request_id": "req_123456789"
}
```

#### 1.2 获取会话信息

获取指定会话的详细信息。

**请求**

```http
GET /sessions/{session_id}
Authorization: Bearer <token>
```

**响应**

```json
{
  "success": true,
  "data": {
    "session_id": "session_abc123",
    "user_id": "user_123456",
    "status": "active",
    "created_at": "2024-12-19T10:30:00Z",
    "updated_at": "2024-12-19T10:35:00Z",
    "expires_at": "2024-12-19T12:30:00Z",
    "diagnosis_count": 2,
    "last_activity": "2024-12-19T10:35:00Z"
  }
}
```

#### 1.3 关闭会话

关闭指定的诊断会话。

**请求**

```http
DELETE /sessions/{session_id}
Authorization: Bearer <token>
```

**响应**

```json
{
  "success": true,
  "data": {
    "session_id": "session_abc123",
    "status": "closed",
    "closed_at": "2024-12-19T10:40:00Z"
  },
  "message": "会话已关闭"
}
```

### 2. 诊断管理

#### 2.1 开始诊断

启动新的诊断流程，支持多种诊断类型的组合。

**请求**

```http
POST /sessions/{session_id}/diagnosis
Content-Type: application/json
Authorization: Bearer <token>

{
  "diagnosis_types": ["looking", "inquiry", "listening", "palpation"],
  "execution_mode": "parallel",
  "diagnosis_data": {
    "looking": {
      "tongue_image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
      "face_image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
      "pulse_image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
    },
    "inquiry": {
      "chief_complaint": "最近感觉疲劳乏力，食欲不振",
      "symptoms": [
        {
          "name": "疲劳",
          "severity": 7,
          "duration": "2周",
          "frequency": "每天"
        },
        {
          "name": "食欲不振",
          "severity": 5,
          "duration": "1周",
          "frequency": "间歇性"
        }
      ],
      "medical_history": {
        "chronic_diseases": ["高血压"],
        "medications": ["降压药"],
        "allergies": []
      }
    },
    "listening": {
      "voice_recording": "data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEA...",
      "breathing_sound": "data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEA..."
    },
    "palpation": {
      "pulse_data": {
        "rate": 72,
        "rhythm": "regular",
        "strength": "moderate",
        "characteristics": ["滑脉", "数脉"]
      }
    }
  },
  "preferences": {
    "language": "zh-CN",
    "detailed_analysis": true,
    "include_recommendations": true
  }
}
```

**响应**

```json
{
  "success": true,
  "data": {
    "diagnosis_id": "diag_xyz789",
    "session_id": "session_abc123",
    "status": "processing",
    "diagnosis_types": ["looking", "inquiry", "listening", "palpation"],
    "execution_mode": "parallel",
    "started_at": "2024-12-19T10:35:00Z",
    "estimated_completion": "2024-12-19T10:37:00Z"
  },
  "message": "诊断已开始"
}
```

#### 2.2 获取诊断状态

查询诊断的当前状态和进度。

**请求**

```http
GET /sessions/{session_id}/diagnosis/{diagnosis_id}/status
Authorization: Bearer <token>
```

**响应**

```json
{
  "success": true,
  "data": {
    "diagnosis_id": "diag_xyz789",
    "status": "processing",
    "progress": {
      "overall": 75,
      "looking": 100,
      "inquiry": 100,
      "listening": 50,
      "palpation": 25
    },
    "started_at": "2024-12-19T10:35:00Z",
    "estimated_completion": "2024-12-19T10:37:00Z",
    "current_step": "listening_analysis"
  }
}
```

#### 2.3 获取诊断结果

获取完整的诊断结果，包括辨证分析、体质分析和建议。

**请求**

```http
GET /sessions/{session_id}/diagnosis/{diagnosis_id}/result
Authorization: Bearer <token>
```

**响应**

```json
{
  "success": true,
  "data": {
    "diagnosis_id": "diag_xyz789",
    "session_id": "session_abc123",
    "status": "completed",
    "completed_at": "2024-12-19T10:37:00Z",
    "results": {
      "syndrome_analysis": {
        "primary_syndrome": {
          "name": "脾胃虚弱",
          "confidence": 0.85,
          "description": "脾胃功能虚弱，运化失常",
          "symptoms": ["疲劳", "食欲不振", "消化不良"],
          "treatment_principle": "健脾益气，调理脾胃"
        },
        "secondary_syndromes": [
          {
            "name": "气血不足",
            "confidence": 0.72,
            "description": "气血生化不足，脏腑失养"
          }
        ],
        "differentiation_method": "八纲辨证",
        "analysis_details": {
          "yin_yang": "阳虚",
          "exterior_interior": "内证",
          "cold_heat": "虚寒",
          "deficiency_excess": "虚证"
        }
      },
      "constitution_analysis": {
        "primary_constitution": {
          "type": "气虚质",
          "score": 78,
          "description": "元气不足，以疲乏、气短、自汗等气虚表现为主要特征",
          "characteristics": [
            "容易疲劳",
            "声音低弱",
            "容易感冒",
            "精神不振"
          ]
        },
        "secondary_constitutions": [
          {
            "type": "阳虚质",
            "score": 65,
            "description": "阳气不足，以畏寒怕冷、手足不温等虚寒表现为主要特征"
          }
        ]
      },
      "diagnosis_details": {
        "looking": {
          "tongue": {
            "color": "淡红",
            "coating": "白腻",
            "texture": "胖大",
            "analysis": "舌淡胖大，苔白腻，提示脾胃虚弱，湿邪内停"
          },
          "face": {
            "color": "萎黄",
            "luster": "无光泽",
            "analysis": "面色萎黄无华，提示气血不足"
          }
        },
        "inquiry": {
          "chief_complaint_analysis": "疲劳乏力为主症，结合食欲不振，符合脾胃虚弱证候",
          "symptom_analysis": [
            {
              "symptom": "疲劳",
              "tcm_interpretation": "脾气虚弱，运化失常，气血生化不足",
              "significance": "主要症状"
            }
          ]
        },
        "listening": {
          "voice_analysis": {
            "volume": "低",
            "tone": "弱",
            "analysis": "声音低弱，提示气虚"
          },
          "breathing_analysis": {
            "pattern": "浅",
            "rhythm": "不规律",
            "analysis": "呼吸浅弱，提示肺气不足"
          }
        },
        "palpation": {
          "pulse_analysis": {
            "type": "细弱脉",
            "rate": "缓",
            "analysis": "脉细弱缓，提示气血不足，阳气虚弱"
          }
        }
      },
      "recommendations": {
        "treatment": {
          "herbal_formula": {
            "name": "四君子汤加减",
            "ingredients": [
              {"name": "人参", "dosage": "10g", "function": "大补元气"},
              {"name": "白术", "dosage": "15g", "function": "健脾燥湿"},
              {"name": "茯苓", "dosage": "15g", "function": "健脾利湿"},
              {"name": "甘草", "dosage": "6g", "function": "调和诸药"}
            ],
            "usage": "水煎服，每日1剂，分2次温服"
          },
          "acupuncture": {
            "points": ["足三里", "脾俞", "胃俞", "气海", "关元"],
            "method": "补法",
            "frequency": "每周2-3次"
          }
        },
        "lifestyle": {
          "diet": {
            "recommended_foods": [
              "山药", "薏米", "红枣", "桂圆", "小米粥"
            ],
            "foods_to_avoid": [
              "生冷食物", "油腻食物", "辛辣刺激"
            ],
            "eating_habits": [
              "定时定量",
              "细嚼慢咽",
              "温热饮食"
            ]
          },
          "exercise": {
            "recommended": [
              "太极拳", "八段锦", "散步", "瑜伽"
            ],
            "intensity": "轻度到中度",
            "frequency": "每天30分钟",
            "precautions": ["避免剧烈运动", "运动后注意保暖"]
          },
          "sleep": {
            "bedtime": "22:00-23:00",
            "wake_time": "06:00-07:00",
            "duration": "7-8小时",
            "environment": "安静、温暖、通风良好"
          }
        },
        "emotional": {
          "mood_regulation": [
            "保持心情愉悦",
            "避免过度思虑",
            "适当放松"
          ],
          "stress_management": [
            "冥想", "深呼吸", "听音乐"
          ]
        },
        "follow_up": {
          "next_visit": "2周后",
          "monitoring_indicators": [
            "疲劳程度", "食欲变化", "睡眠质量"
          ],
          "emergency_signs": [
            "症状明显加重", "出现新的严重症状"
          ]
        }
      },
      "confidence_score": 0.82,
      "quality_assessment": {
        "data_completeness": 0.95,
        "analysis_consistency": 0.88,
        "recommendation_relevance": 0.90
      }
    }
  }
}
```

### 3. 多模态处理

#### 3.1 处理图像数据

处理医学图像数据，如舌象、面象等。

**请求**

```http
POST /multimodal/image/analyze
Content-Type: application/json
Authorization: Bearer <token>

{
  "image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
  "image_type": "tongue",
  "analysis_options": {
    "extract_features": true,
    "generate_description": true,
    "tcm_analysis": true
  }
}
```

**响应**

```json
{
  "success": true,
  "data": {
    "image_id": "img_123456",
    "image_type": "tongue",
    "analysis_result": {
      "features": {
        "color": "淡红",
        "coating": "白腻",
        "texture": "胖大",
        "moisture": "润",
        "cracks": "无"
      },
      "description": "舌质淡红，舌体胖大，苔白腻润",
      "tcm_interpretation": {
        "syndrome_indicators": ["脾胃虚弱", "湿邪内停"],
        "constitution_hints": ["气虚质", "痰湿质"],
        "severity": "中度"
      },
      "confidence": 0.87
    },
    "processed_at": "2024-12-19T10:35:00Z"
  }
}
```

#### 3.2 处理音频数据

处理语音、呼吸音等音频数据。

**请求**

```http
POST /multimodal/audio/analyze
Content-Type: application/json
Authorization: Bearer <token>

{
  "audio_data": "data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEA...",
  "audio_type": "voice",
  "analysis_options": {
    "extract_features": true,
    "speech_to_text": true,
    "voice_analysis": true
  }
}
```

**响应**

```json
{
  "success": true,
  "data": {
    "audio_id": "audio_123456",
    "audio_type": "voice",
    "analysis_result": {
      "transcription": "我最近感觉很疲劳，没有精神",
      "voice_features": {
        "volume": "低",
        "tone": "弱",
        "clarity": "清晰",
        "rhythm": "缓慢"
      },
      "tcm_interpretation": {
        "qi_analysis": "气虚",
        "voice_quality": "声低气怯",
        "syndrome_indicators": ["气虚"]
      },
      "confidence": 0.79
    }
  }
}
```

### 4. 无障碍服务

#### 4.1 文本转语音

将文本转换为语音，支持多种语言和语音参数。

**请求**

```http
POST /accessibility/tts
Content-Type: application/json
Authorization: Bearer <token>

{
  "text": "您的诊断结果显示脾胃虚弱，建议调理脾胃功能",
  "language": "zh-CN",
  "voice_config": {
    "speed": 1.0,
    "volume": 0.8,
    "pitch": 1.0
  },
  "output_format": "wav"
}
```

**响应**

```json
{
  "success": true,
  "data": {
    "audio_data": "data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEA...",
    "duration": 5.2,
    "format": "wav",
    "sample_rate": 22050,
    "generated_at": "2024-12-19T10:35:00Z"
  }
}
```

#### 4.2 语音转文本

将语音转换为文本，支持多种语言识别。

**请求**

```http
POST /accessibility/stt
Content-Type: application/json
Authorization: Bearer <token>

{
  "audio_data": "data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEA...",
  "language": "zh-CN",
  "recognition_config": {
    "enable_punctuation": true,
    "filter_profanity": false,
    "enable_word_confidence": true
  }
}
```

**响应**

```json
{
  "success": true,
  "data": {
    "transcription": "我最近感觉很疲劳，没有精神，食欲也不好",
    "confidence": 0.92,
    "word_confidences": [
      {"word": "我", "confidence": 0.98},
      {"word": "最近", "confidence": 0.95},
      {"word": "感觉", "confidence": 0.93}
    ],
    "language_detected": "zh-CN",
    "duration": 3.5
  }
}
```

#### 4.3 手势识别

识别手势命令，支持无障碍交互。

**请求**

```http
POST /accessibility/gesture-recognition
Content-Type: application/json
Authorization: Bearer <token>

{
  "image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
  "recognition_config": {
    "gesture_types": ["thumbs_up", "thumbs_down", "open_palm"],
    "confidence_threshold": 0.7
  }
}
```

**响应**

```json
{
  "success": true,
  "data": {
    "gestures": [
      {
        "type": "thumbs_up",
        "confidence": 0.89,
        "command": "确认",
        "position": {
          "x": 320,
          "y": 240,
          "width": 100,
          "height": 120
        }
      }
    ],
    "processed_at": "2024-12-19T10:35:00Z"
  }
}
```

### 5. 健康检查

#### 5.1 系统健康状态

获取系统整体健康状态。

**请求**

```http
GET /health
```

**响应**

```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2024-12-19T10:35:00Z",
    "version": "1.0.0",
    "uptime": 86400,
    "components": {
      "database": {
        "status": "healthy",
        "response_time": 12,
        "connections": {
          "active": 5,
          "max": 100
        }
      },
      "redis": {
        "status": "healthy",
        "response_time": 3,
        "memory_usage": "45%"
      },
      "ai_models": {
        "status": "healthy",
        "loaded_models": 8,
        "memory_usage": "1.2GB"
      },
      "external_services": {
        "looking_service": "healthy",
        "inquiry_service": "healthy",
        "listening_service": "healthy",
        "palpation_service": "healthy"
      }
    },
    "metrics": {
      "requests_per_minute": 150,
      "average_response_time": 250,
      "error_rate": 0.01,
      "cpu_usage": 45,
      "memory_usage": 68
    }
  }
}
```

#### 5.2 详细健康检查

获取详细的系统健康检查报告。

**请求**

```http
GET /health/detailed
Authorization: Bearer <token>
```

**响应**

```json
{
  "success": true,
  "data": {
    "overall_status": "healthy",
    "checks": [
      {
        "name": "database_connection",
        "status": "pass",
        "response_time": "12ms",
        "details": {
          "host": "localhost:5432",
          "database": "xiaoai_db",
          "pool_size": 20,
          "active_connections": 5
        }
      },
      {
        "name": "ai_model_health",
        "status": "pass",
        "response_time": "45ms",
        "details": {
          "loaded_models": [
            "syndrome_analyzer",
            "constitution_analyzer",
            "multimodal_processor"
          ],
          "memory_usage": "1.2GB",
          "gpu_usage": "30%"
        }
      }
    ],
    "performance_metrics": {
      "last_24h": {
        "total_requests": 12450,
        "successful_requests": 12398,
        "failed_requests": 52,
        "average_response_time": 245,
        "p95_response_time": 890,
        "p99_response_time": 1250
      }
    }
  }
}
```

## 错误代码

### 通用错误代码

| 错误代码 | HTTP状态码 | 描述 |
|---------|-----------|------|
| `INVALID_REQUEST` | 400 | 请求格式错误 |
| `UNAUTHORIZED` | 401 | 未授权访问 |
| `FORBIDDEN` | 403 | 禁止访问 |
| `NOT_FOUND` | 404 | 资源不存在 |
| `METHOD_NOT_ALLOWED` | 405 | 方法不允许 |
| `RATE_LIMITED` | 429 | 请求频率超限 |
| `INTERNAL_ERROR` | 500 | 内部服务器错误 |
| `SERVICE_UNAVAILABLE` | 503 | 服务不可用 |

### 业务错误代码

| 错误代码 | HTTP状态码 | 描述 |
|---------|-----------|------|
| `SESSION_NOT_FOUND` | 404 | 会话不存在 |
| `SESSION_EXPIRED` | 410 | 会话已过期 |
| `DIAGNOSIS_NOT_FOUND` | 404 | 诊断不存在 |
| `DIAGNOSIS_IN_PROGRESS` | 409 | 诊断正在进行中 |
| `INVALID_DIAGNOSIS_DATA` | 400 | 诊断数据格式错误 |
| `AI_MODEL_ERROR` | 500 | AI模型处理错误 |
| `EXTERNAL_SERVICE_ERROR` | 502 | 外部服务错误 |
| `MULTIMODAL_PROCESSING_ERROR` | 500 | 多模态处理错误 |
| `ACCESSIBILITY_SERVICE_ERROR` | 500 | 无障碍服务错误 |

## 限流规则

| 接口类型 | 限制 | 时间窗口 |
|---------|------|---------|
| 认证接口 | 10次/分钟 | 1分钟 |
| 会话管理 | 60次/分钟 | 1分钟 |
| 诊断接口 | 30次/分钟 | 1分钟 |
| 多模态处理 | 20次/分钟 | 1分钟 |
| 无障碍服务 | 100次/分钟 | 1分钟 |
| 健康检查 | 无限制 | - |

## SDK 和示例

### Python SDK

```python
from xiaoai_client import XiaoAIClient

# 初始化客户端
client = XiaoAIClient(
    base_url="https://api.suoke.life/xiaoai/v1",
    access_token="your_access_token"
)

# 创建会话
session = await client.create_session(
    user_id="user_123456",
    metadata={"source": "python_sdk"}
)

# 开始诊断
diagnosis = await client.start_diagnosis(
    session_id=session.session_id,
    diagnosis_data={
        "inquiry": {
            "chief_complaint": "疲劳乏力",
            "symptoms": [{"name": "疲劳", "severity": 7}]
        }
    }
)

# 获取结果
result = await client.get_diagnosis_result(
    session_id=session.session_id,
    diagnosis_id=diagnosis.diagnosis_id
)
```

### JavaScript SDK

```javascript
import { XiaoAIClient } from '@suoke/xiaoai-client';

// 初始化客户端
const client = new XiaoAIClient({
  baseURL: 'https://api.suoke.life/xiaoai/v1',
  accessToken: 'your_access_token'
});

// 创建会话
const session = await client.createSession({
  userId: 'user_123456',
  metadata: { source: 'web_app' }
});

// 开始诊断
const diagnosis = await client.startDiagnosis({
  sessionId: session.sessionId,
  diagnosisData: {
    inquiry: {
      chiefComplaint: '疲劳乏力',
      symptoms: [{ name: '疲劳', severity: 7 }]
    }
  }
});
```

## 更新日志

### v1.0.0 (2024-12-19)
- 初始版本发布
- 完整的五诊协调诊断功能
- 多模态数据处理支持
- 无障碍服务集成
- 完整的API文档

## 支持

如有问题或建议，请联系：
- 邮箱: api-support@suoke.life
- 文档: https://docs.suoke.life/xiaoai-service
- GitHub: https://github.com/SUOKE2024/suoke_life/issues 