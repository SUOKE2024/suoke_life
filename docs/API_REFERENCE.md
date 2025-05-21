# API参考文档

本文档提供索克生活APP项目中使用的API接口参考。

## 目录

- [API基础信息](#api基础信息)
- [认证API](#认证api)
- [用户API](#用户api)
- [健康数据API](#健康数据api)
- [小艾(xiaoai)服务API](#小艾xiaoai服务api)
- [小克(xiaoke)服务API](#小克xiaoke服务api)
- [老克(laoke)服务API](#老克laoke服务api)
- [索儿(soer)服务API](#索儿soer服务api)
- [四诊服务API](#四诊服务api)
- [区块链服务API](#区块链服务api)
- [错误处理](#错误处理)
- [API版本控制](#api版本控制)

## API基础信息

### 基础URL

- 开发环境: `https://dev-api.suoke.life`
- 测试环境: `https://stage-api.suoke.life`
- 生产环境: `https://api.suoke.life`

### 请求格式

API请求和响应均使用JSON格式。

**请求头:**

```
Content-Type: application/json
Authorization: Bearer {access_token}
Accept-Language: zh-CN
```

### 响应格式

所有API响应遵循统一的JSON格式:

```json
{
  "code": 0,           // 状态码，0表示成功
  "message": "成功",    // 状态信息
  "data": {},          // 响应数据
  "timestamp": 1624235661000  // 响应时间戳
}
```

### 状态码

| 状态码 | 描述 |
|-------|------|
| 0 | 成功 |
| 1001 | 用户未登录 |
| 1002 | 权限不足 |
| 1003 | 参数错误 |
| 2001 | 服务器内部错误 |
| 3001 | 第三方服务异常 |

## 认证API

### 登录

**请求:**

```
POST /api/v1/auth/login
```

**请求体:**

```json
{
  "mobile": "13800138000",
  "password": "password123",
  "device_id": "DEVICE_UUID",
  "device_type": "ios" // ios, android, web
}
```

**响应:**

```json
{
  "code": 0,
  "message": "登录成功",
  "data": {
    "user_id": "123456",
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 86400,
    "user_info": {
      "id": "123456",
      "nickname": "用户名",
      "avatar": "https://cdn.suoke.life/avatars/default.png",
      "health_score": 85,
      "constitution_type": "平和质"
    }
  },
  "timestamp": 1624235661000
}
```

### 刷新令牌

**请求:**

```
POST /api/v1/auth/refresh
```

**请求体:**

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**响应:**

```json
{
  "code": 0,
  "message": "刷新成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 86400
  },
  "timestamp": 1624235661000
}
```

### 登出

**请求:**

```
POST /api/v1/auth/logout
```

**请求头:**

```
Authorization: Bearer {access_token}
```

**响应:**

```json
{
  "code": 0,
  "message": "登出成功",
  "data": null,
  "timestamp": 1624235661000
}
```

## 用户API

### 获取用户信息

**请求:**

```
GET /api/v1/user/profile
```

**请求头:**

```
Authorization: Bearer {access_token}
```

**响应:**

```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "id": "123456",
    "nickname": "用户名",
    "avatar": "https://cdn.suoke.life/avatars/default.png",
    "mobile": "138****8000",
    "email": "u***@example.com",
    "gender": 1,
    "birthday": "1990-01-01",
    "height": 170,
    "weight": 65,
    "health_score": 85,
    "constitution_type": "平和质",
    "achievement_count": 10,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-06-01T00:00:00Z"
  },
  "timestamp": 1624235661000
}
```

### 更新用户信息

**请求:**

```
PUT /api/v1/user/profile
```

**请求头:**

```
Authorization: Bearer {access_token}
```

**请求体:**

```json
{
  "nickname": "新用户名",
  "gender": 1,
  "birthday": "1990-01-01",
  "height": 170,
  "weight": 65
}
```

**响应:**

```json
{
  "code": 0,
  "message": "更新成功",
  "data": {
    "id": "123456",
    "nickname": "新用户名",
    "gender": 1,
    "birthday": "1990-01-01",
    "height": 170,
    "weight": 65,
    "updated_at": "2023-06-01T00:00:00Z"
  },
  "timestamp": 1624235661000
}
```

## 健康数据API

### 获取健康摘要

**请求:**

```
GET /api/v1/health/summary
```

**请求头:**

```
Authorization: Bearer {access_token}
```

**响应:**

```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "health_score": 85,
    "constitution_type": "平和质",
    "constitution_analysis": {
      "dominant": ["平和质"],
      "secondary": ["气虚质"],
      "scores": {
        "平和质": 85,
        "气虚质": 60,
        "阳虚质": 30,
        "阴虚质": 25,
        "痰湿质": 20,
        "湿热质": 15,
        "血瘀质": 10,
        "气郁质": 5,
        "特禀质": 0
      }
    },
    "recent_data": {
      "steps": {
        "today": 8000,
        "yesterday": 7500,
        "weekly_avg": 7800
      },
      "sleep": {
        "last_night": 7.5,
        "quality": "良好",
        "weekly_avg": 7.2
      },
      "heart_rate": {
        "current": 72,
        "resting": 68,
        "max_today": 120
      }
    },
    "recommendations": [
      {
        "type": "diet",
        "content": "根据您的平和体质，建议多食用温性食物，少食生冷。"
      },
      {
        "type": "exercise",
        "content": "建议进行中等强度的有氧运动，如快走、游泳等。"
      },
      {
        "type": "lifestyle",
        "content": "保持规律作息，避免熬夜。"
      }
    ]
  },
  "timestamp": 1624235661000
}
```

### 上传健康数据

**请求:**

```
POST /api/v1/health/data
```

**请求头:**

```
Authorization: Bearer {access_token}
```

**请求体:**

```json
{
  "data_type": "sleep",
  "data": {
    "date": "2023-06-01",
    "duration": 7.5,
    "deep_sleep": 2.3,
    "light_sleep": 4.0,
    "rem_sleep": 1.2,
    "awake": 0.3,
    "quality_score": 85
  },
  "device_info": {
    "device_id": "DEVICE_UUID",
    "device_type": "smart_watch",
    "device_model": "Apple Watch Series 7"
  }
}
```

**响应:**

```json
{
  "code": 0,
  "message": "上传成功",
  "data": {
    "id": "sleep_20230601_123456",
    "created_at": "2023-06-01T08:00:00Z"
  },
  "timestamp": 1624235661000
}
```

## 小艾(xiaoai)服务API

### 创建会话

**请求:**

```
POST /api/v1/xiaoai/sessions
```

**请求头:**

```
Authorization: Bearer {access_token}
```

**请求体:**

```json
{
  "context": {
    "location": "home",
    "purpose": "health_inquiry"
  }
}
```

**响应:**

```json
{
  "code": 0,
  "message": "会话创建成功",
  "data": {
    "session_id": "sess_123456789",
    "expire_at": "2023-06-01T10:00:00Z",
    "greeting": "您好，我是小艾，您今天感觉如何？"
  },
  "timestamp": 1624235661000
}
```

### 发送消息

**请求:**

```
POST /api/v1/xiaoai/sessions/{session_id}/messages
```

**请求头:**

```
Authorization: Bearer {access_token}
```

**请求体:**

```json
{
  "content": "我今天感觉有些疲倦",
  "content_type": "text"
}
```

**响应:**

```json
{
  "code": 0,
  "message": "发送成功",
  "data": {
    "message_id": "msg_123456789",
    "created_at": "2023-06-01T09:30:00Z",
    "response": {
      "message_id": "msg_987654321",
      "content": "您好，听起来您可能有些疲劳。能否告诉我您最近的睡眠和饮食情况？",
      "content_type": "text",
      "suggestions": [
        "睡眠质量不佳",
        "饮食不规律",
        "工作压力大"
      ]
    }
  },
  "timestamp": 1624235661000
}
```

### 上传图像

**请求:**

```
POST /api/v1/xiaoai/sessions/{session_id}/images
```

**请求头:**

```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**请求体:**

```
image: [二进制图像数据]
image_type: tongue // tongue, face, food, medicine, other
description: 舌象图片
```

**响应:**

```json
{
  "code": 0,
  "message": "上传成功",
  "data": {
    "message_id": "msg_123456789",
    "image_url": "https://cdn.suoke.life/images/tongue_123456.jpg",
    "created_at": "2023-06-01T09:35:00Z",
    "analysis": {
      "tongue_color": "淡红",
      "tongue_coating": "薄白",
      "features": ["舌体胖大", "齿痕", "舌尖红"],
      "preliminary_analysis": "舌象显示有湿热征象，可能伴有脾胃功能不佳。"
    },
    "response": {
      "message_id": "msg_987654321",
      "content": "从您的舌象来看，有一些湿热和脾胃不和的迹象。您最近是否有饮食不规律或者过食辛辣食物的情况？",
      "content_type": "text"
    }
  },
  "timestamp": 1624235661000
}
```

### 录制语音

**请求:**

```
POST /api/v1/xiaoai/sessions/{session_id}/audio
```

**请求头:**

```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**请求体:**

```
audio: [二进制音频数据]
format: wav // wav, mp3, aac
duration: 10 // 时长，单位为秒
```

**响应:**

```json
{
  "code": 0,
  "message": "上传成功",
  "data": {
    "message_id": "msg_123456789",
    "audio_url": "https://cdn.suoke.life/audio/voice_123456.wav",
    "created_at": "2023-06-01T09:40:00Z",
    "transcription": "我最近睡眠不好，容易醒，而且感觉很疲劳。",
    "analysis": {
      "voice_features": {
        "tone": "平稳",
        "pace": "偏慢",
        "energy": "偏低"
      },
      "emotion_analysis": {
        "primary_emotion": "疲惫",
        "confidence": 0.85
      }
    },
    "response": {
      "message_id": "msg_987654321",
      "content": "我注意到您的声音听起来有些疲惫，您提到睡眠不好，容易醒。这可能与您的气虚体质有关。您平时是否有午休的习惯？晚上是否有使用电子设备？",
      "content_type": "text"
    }
  },
  "timestamp": 1624235661000
}
```

### 获取四诊建议

**请求:**

```
GET /api/v1/xiaoai/sessions/{session_id}/diagnosis/suggestions
```

**请求头:**

```
Authorization: Bearer {access_token}
```

**响应:**

```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "completed_diagnostics": ["look", "inquiry"],
    "pending_diagnostics": ["listen", "palpation"],
    "next_step": {
      "type": "listen",
      "description": "建议进行语音分析，可以提供更全面的健康信息。",
      "instruction": "请点击录音按钮，正常语速朗读以下文字：'春暖花开，万物复苏，我们迎来了美好的季节。'"
    },
    "completion_percentage": 50
  },
  "timestamp": 1624235661000
}
```

### 获取最终诊断结果

**请求:**

```
GET /api/v1/xiaoai/sessions/{session_id}/diagnosis/results
```

**请求头:**

```
Authorization: Bearer {access_token}
```

**响应:**

```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "constitution_analysis": {
      "dominant": ["气虚质"],
      "secondary": ["湿热质"],
      "scores": {
        "平和质": 60,
        "气虚质": 85,
        "阳虚质": 30,
        "阴虚质": 25,
        "痰湿质": 40,
        "湿热质": 70,
        "血瘀质": 35,
        "气郁质": 45,
        "特禀质": 10
      }
    },
    "symptoms_analysis": [
      {
        "category": "sleep",
        "symptoms": ["入睡困难", "易醒", "睡眠质量差"],
        "severity": "中度"
      },
      {
        "category": "mood",
        "symptoms": ["疲乏", "精神不振"],
        "severity": "轻度"
      },
      {
        "category": "digestion",
        "symptoms": ["食欲不振", "口干"],
        "severity": "轻度"
      }
    ],
    "health_assessment": {
      "overall_score": 75,
      "areas_of_concern": ["睡眠健康", "消化功能"],
      "areas_of_strength": ["心肺功能"]
    },
    "recommendations": [
      {
        "category": "diet",
        "general_advice": "宜食用具有健脾益气功效的食物，如山药、莲子、大枣等。",
        "specific_items": [
          {
            "name": "山药粥",
            "description": "山药10克，大米50克，枸杞5克，煮粥食用。",
            "frequency": "每周3-4次",
            "benefits": "健脾益气，改善睡眠。"
          }
        ]
      },
      {
        "category": "exercise",
        "general_advice": "宜进行缓和的活动，如太极、八段锦等。",
        "specific_items": [
          {
            "name": "八段锦",
            "description": "每天早晚各一次，每次15-20分钟。",
            "benefits": "增强体质，调理气血。"
          }
        ]
      },
      {
        "category": "lifestyle",
        "general_advice": "保持规律作息，避免熬夜。",
        "specific_items": [
          {
            "name": "午休",
            "description": "中午适当休息20-30分钟。",
            "benefits": "恢复精力，提高下午工作效率。"
          }
        ]
      }
    ],
    "follow_up": {
      "suggested_interval": 30,
      "focus_areas": ["睡眠质量改善", "疲劳感减轻"]
    }
  },
  "timestamp": 1624235661000
}
```

## 错误处理

当API调用失败时，响应中的`code`字段将不为0，并且`message`字段将包含错误描述。

**示例:**

```json
{
  "code": 1001,
  "message": "用户未登录",
  "data": null,
  "timestamp": 1624235661000
}
```

某些错误可能会包含更详细的错误信息：

```json
{
  "code": 1003,
  "message": "参数错误",
  "data": {
    "errors": [
      {
        "field": "mobile",
        "message": "手机号格式不正确"
      }
    ]
  },
  "timestamp": 1624235661000
}
```

## API版本控制

API版本通过URL路径中的版本号进行控制，例如`/api/v1/`表示API的第一个版本。当API进行不兼容更新时，版本号将会递增。

应用程序应始终指定API版本，以确保兼容性。未指定版本的API调用将默认使用最新版本，但不建议在生产环境中使用。
