# 小艾智能体服务 API 文档

## 📋 服务概览

**服务名称**: xiaoai-service  
**服务描述**: 健康助手和多模态诊断智能体  
**服务端口**: 50053  
**协议**: gRPC + HTTP REST  
**版本**: v1.0.0  

## 🎯 核心功能

- 多模态健康数据融合分析
- 四诊合参智能诊断
- 语音交互和无障碍服务
- 实时健康监测和预警
- 个性化健康建议生成
- A2A智能体协作

## 🔌 API 接口

### 1. 健康咨询接口

#### POST /api/v1/xiaoai/health/consult
健康问题咨询和诊断建议

**请求参数**:
```json
{
  "user_id": "string",
  "symptoms": ["头痛", "发热", "咳嗽"],
  "duration": "3天",
  "severity": "中等",
  "additional_info": "伴有轻微恶心",
  "multimodal_data": {
    "voice_file": "base64_encoded_audio",
    "image_files": ["base64_encoded_image"],
    "sensor_data": {
      "heart_rate": 85,
      "blood_pressure": "120/80",
      "temperature": 37.2
    }
  }
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "诊断完成",
  "data": {
    "consultation_id": "cons_123456",
    "diagnosis": {
      "primary_diagnosis": "上呼吸道感染",
      "confidence": 0.85,
      "tcm_syndrome": "风热感冒",
      "recommendations": [
        "多休息，保持充足睡眠",
        "多饮温水，保持室内通风",
        "可服用板蓝根颗粒"
      ],
      "severity_level": "轻度",
      "follow_up_needed": true,
      "follow_up_time": "3天后"
    },
    "multimodal_analysis": {
      "voice_analysis": {
        "voice_quality": "略显嘶哑",
        "breathing_pattern": "正常",
        "emotional_state": "轻微焦虑"
      },
      "image_analysis": {
        "tongue_diagnosis": {
          "tongue_color": "红",
          "coating": "薄黄",
          "texture": "正常"
        },
        "facial_analysis": {
          "complexion": "略显苍白",
          "spirit": "一般"
        }
      }
    }
  },
  "timestamp": "2025-01-27T10:00:00Z"
}
```

### 2. 语音交互接口

#### POST /api/v1/xiaoai/voice/interact
语音对话和交互处理

**请求参数**:
```json
{
  "user_id": "string",
  "audio_data": "base64_encoded_audio",
  "audio_format": "wav",
  "sample_rate": 16000,
  "context": {
    "conversation_id": "conv_123456",
    "previous_messages": []
  }
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "语音处理完成",
  "data": {
    "conversation_id": "conv_123456",
    "transcription": "我最近总是感觉头痛，怎么办？",
    "response": {
      "text": "头痛可能有多种原因，让我帮您分析一下。请问头痛持续多长时间了？",
      "audio_response": "base64_encoded_audio",
      "suggestions": [
        "描述头痛的具体位置",
        "说明头痛的性质（胀痛、刺痛等）",
        "提及是否有其他伴随症状"
      ]
    },
    "emotion_analysis": {
      "detected_emotion": "担忧",
      "confidence": 0.78,
      "empathy_response": "我理解您的担心，让我们一起找出解决方案"
    }
  },
  "timestamp": "2025-01-27T10:00:00Z"
}
```

### 3. 健康监测接口

#### POST /api/v1/xiaoai/monitor/analyze
实时健康数据分析和预警

**请求参数**:
```json
{
  "user_id": "string",
  "monitoring_data": {
    "vital_signs": {
      "heart_rate": 85,
      "blood_pressure": "120/80",
      "temperature": 36.5,
      "oxygen_saturation": 98
    },
    "activity_data": {
      "steps": 8500,
      "calories_burned": 320,
      "sleep_hours": 7.5,
      "exercise_minutes": 45
    },
    "environmental_data": {
      "air_quality": "良好",
      "temperature": 22,
      "humidity": 60
    }
  },
  "time_range": "24h"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "健康分析完成",
  "data": {
    "analysis_id": "analysis_123456",
    "health_score": 85,
    "risk_assessment": {
      "overall_risk": "低风险",
      "specific_risks": [
        {
          "type": "心血管风险",
          "level": "低",
          "probability": 0.15
        }
      ]
    },
    "recommendations": [
      "保持当前的运动习惯",
      "注意补充水分",
      "建议增加深度睡眠时间"
    ],
    "alerts": [],
    "trends": {
      "heart_rate_trend": "稳定",
      "activity_trend": "上升",
      "sleep_quality_trend": "改善"
    }
  },
  "timestamp": "2025-01-27T10:00:00Z"
}
```

### 4. 智能体协作接口

#### POST /api/v1/xiaoai/collaborate
与其他智能体协作处理复杂健康问题

**请求参数**:
```json
{
  "user_id": "string",
  "collaboration_request": {
    "primary_agent": "xiaoai",
    "collaborating_agents": ["xiaoke", "laoke", "soer"],
    "task_type": "comprehensive_health_assessment",
    "user_data": {
      "basic_info": {},
      "health_history": {},
      "current_symptoms": {},
      "lifestyle_data": {}
    }
  }
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "协作分析完成",
  "data": {
    "collaboration_id": "collab_123456",
    "comprehensive_assessment": {
      "xiaoai_analysis": {
        "medical_diagnosis": "轻度焦虑症",
        "confidence": 0.82
      },
      "xiaoke_recommendations": {
        "product_suggestions": ["褪黑素补充剂", "舒缓茶"],
        "service_recommendations": ["心理咨询", "瑜伽课程"]
      },
      "laoke_knowledge": {
        "tcm_perspective": "肝气郁结",
        "treatment_principles": ["疏肝解郁", "安神定志"],
        "herbal_formulas": ["甘麦大枣汤", "逍遥散"]
      },
      "soer_lifestyle": {
        "diet_suggestions": ["增加富含镁的食物", "减少咖啡因摄入"],
        "exercise_plan": ["每日30分钟有氧运动", "睡前瑜伽"],
        "schedule_optimization": ["规律作息", "减少工作压力"]
      }
    },
    "integrated_plan": {
      "short_term_goals": [],
      "long_term_goals": [],
      "monitoring_metrics": []
    }
  },
  "timestamp": "2025-01-27T10:00:00Z"
}
```

## 🔧 gRPC 接口

### 服务定义

```protobuf
syntax = "proto3";

package xiaoai.v1;

service XiaoaiService {
  // 健康咨询
  rpc HealthConsult(HealthConsultRequest) returns (HealthConsultResponse);
  
  // 语音交互
  rpc VoiceInteract(VoiceInteractRequest) returns (VoiceInteractResponse);
  
  // 健康监测
  rpc HealthMonitor(HealthMonitorRequest) returns (HealthMonitorResponse);
  
  // 智能体协作
  rpc AgentCollaborate(CollaborateRequest) returns (CollaborateResponse);
  
  // 健康检查
  rpc HealthCheck(HealthCheckRequest) returns (HealthCheckResponse);
}

message HealthConsultRequest {
  string user_id = 1;
  repeated string symptoms = 2;
  string duration = 3;
  string severity = 4;
  MultimodalData multimodal_data = 5;
}

message MultimodalData {
  string voice_file = 1;
  repeated string image_files = 2;
  SensorData sensor_data = 3;
}

message SensorData {
  int32 heart_rate = 1;
  string blood_pressure = 2;
  double temperature = 3;
}
```

## 🚨 错误码说明

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 40001 | 用户ID无效 | 检查用户ID格式 |
| 40002 | 症状描述为空 | 提供症状描述 |
| 40003 | 多模态数据格式错误 | 检查数据格式 |
| 50001 | AI模型服务异常 | 重试或联系技术支持 |
| 50002 | 数据库连接失败 | 检查网络连接 |

## 📊 性能指标

- **响应时间**: < 200ms (简单查询), < 2s (复杂分析)
- **并发处理**: 1000 QPS
- **可用性**: 99.9%
- **准确率**: 医学诊断建议准确率 > 85%

## 🔒 安全说明

- 所有健康数据传输采用TLS 1.3加密
- 敏感数据存储采用AES-256加密
- 支持零知识证明验证
- 符合HIPAA和GDPR合规要求

## 📝 使用示例

### Python SDK示例

```python
from suoke_sdk import XiaoaiClient

# 初始化客户端
client = XiaoaiClient(
    api_key="your_api_key",
    base_url="https://api.suoke.life"
)

# 健康咨询
response = client.health_consult(
    user_id="user_123",
    symptoms=["头痛", "发热"],
    duration="2天",
    severity="中等"
)

print(f"诊断结果: {response.diagnosis.primary_diagnosis}")
print(f"建议: {response.diagnosis.recommendations}")
```

### JavaScript SDK示例

```javascript
import { XiaoaiClient } from '@suoke/sdk';

const client = new XiaoaiClient({
  apiKey: 'your_api_key',
  baseUrl: 'https://api.suoke.life'
});

// 语音交互
const response = await client.voiceInteract({
  userId: 'user_123',
  audioData: audioBase64,
  audioFormat: 'wav'
});

console.log('AI回复:', response.response.text);
```

## 🔄 更新日志

- **v1.0.0** (2025-01-27): 初始版本发布
- 支持多模态健康诊断
- 实现语音交互功能
- 集成四诊合参算法
- 支持智能体协作机制 