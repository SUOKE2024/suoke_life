# 中医四诊 API

## 概述

中医四诊API提供望、闻、问、切四诊数据的提交、分析和检索功能。这些API是索克生活APP中医健康评估的核心组件，支持图像识别、语音分析和结构化问诊等功能。

## 基础端点

```
https://api.suoke.life/api/v1/diagnoses
```

## 接口列表

### 望诊

#### 提交舌象图片

上传并分析舌象图片。

**请求**

```
POST /api/v1/diagnoses/inspection/tongue
Content-Type: multipart/form-data
Authorization: Bearer {accessToken}
```

**请求参数**

| 参数名 | 类型 | 必选 | 描述 |
|-------|-----|------|-----|
| image | file | 是 | 舌象图片，支持格式：JPEG, PNG，最大尺寸：10MB |
| notes | string | 否 | 相关备注信息 |
| captureTime | string | 否 | 拍摄时间，ISO 8601格式 |
| captureEnvironment | object | 否 | 拍摄环境信息（光照等） |

**请求示例**

```
POST /api/v1/diagnoses/inspection/tongue
Content-Type: multipart/form-data
Authorization: Bearer {accessToken}

---
image: [binary data]
notes: "早晨空腹拍摄"
captureTime: "2024-07-15T08:00:00Z"
captureEnvironment: {
  "lightingCondition": "NATURAL",
  "lightingBrightness": "BRIGHT"
}
```

**响应**

```
Status: 201 Created
Content-Type: application/json
```

**响应字段**

| 字段名 | 类型 | 描述 |
|-------|-----|------|
| id | string | 望诊记录唯一标识 |
| imageUrl | string | 存储后的图片URL |
| analysis | object | 舌象分析结果 |
| createdAt | string | 创建时间，ISO 8601格式 |

**响应示例**

```json
{
  "id": "tng_123456789",
  "imageUrl": "https://api.suoke.life/images/tongues/user123_20240715080000.jpg",
  "analysis": {
    "tongueColor": {
      "mainColor": "PALE_RED",
      "colorScore": 3.5,
      "description": "舌色淡红，偏白"
    },
    "tongueShape": {
      "shape": "NORMAL",
      "toothMarks": true,
      "cracks": false
    },
    "tongueCoating": {
      "color": "WHITE",
      "thickness": "THIN",
      "distribution": "FULL"
    },
    "moistureLevel": "NORMAL",
    "overallAssessment": "舌质淡红，苔薄白，气虚质特征明显"
  },
  "createdAt": "2024-07-15T08:05:23Z"
}
```

**错误响应**

| HTTP状态码 | 错误码 | 描述 |
|-----------|-------|------|
| 400 | INVALID_IMAGE | 图片格式不支持或质量过低 |
| 400 | IMAGE_TOO_LARGE | 图片尺寸超过限制 |
| 422 | ANALYSIS_FAILED | 图像分析失败 |

#### 获取舌象历史记录

获取用户历史舌象记录及分析结果。

**请求**

```
GET /api/v1/diagnoses/inspection/tongue
Content-Type: application/json
Authorization: Bearer {accessToken}
```

**请求参数**

| 参数名 | 类型 | 必选 | 描述 |
|-------|-----|------|-----|
| page | integer | 否 | 页码，默认为1 |
| pageSize | integer | 否 | 每页记录数，默认为20，最大50 |
| startDate | string | 否 | 开始日期，ISO 8601格式 |
| endDate | string | 否 | 结束日期，ISO 8601格式 |
| sortBy | string | 否 | 排序字段，可选值：createdAt、captureTime，默认createdAt |
| sortOrder | string | 否 | 排序方向，可选值：asc、desc，默认desc |

**请求示例**

```
GET /api/v1/diagnoses/inspection/tongue?page=1&pageSize=10&sortBy=createdAt&sortOrder=desc
Authorization: Bearer {accessToken}
```

**响应**

```
Status: 200 OK
Content-Type: application/json
```

**响应字段**

| 字段名 | 类型 | 描述 |
|-------|-----|------|
| items | array | 舌象记录数组 |
| pagination | object | 分页信息 |

**响应示例**

```json
{
  "items": [
    {
      "id": "tng_123456789",
      "imageUrl": "https://api.suoke.life/images/tongues/user123_20240715080000.jpg",
      "thumbnailUrl": "https://api.suoke.life/images/tongues/thumbnails/user123_20240715080000.jpg",
      "analysis": {
        "tongueColor": {
          "mainColor": "PALE_RED",
          "description": "舌色淡红，偏白"
        },
        "tongueCoating": {
          "color": "WHITE",
          "thickness": "THIN"
        },
        "summary": "舌质淡红，苔薄白，气虚质特征明显"
      },
      "captureTime": "2024-07-15T08:00:00Z",
      "createdAt": "2024-07-15T08:05:23Z"
    },
    // 更多记录...
  ],
  "pagination": {
    "total": 35,
    "pageSize": 10,
    "currentPage": 1,
    "totalPages": 4
  }
}
```

### 闻诊

#### 提交语音样本

上传并分析用户语音样本。

**请求**

```
POST /api/v1/diagnoses/auscultation/voice
Content-Type: multipart/form-data
Authorization: Bearer {accessToken}
```

**请求参数**

| 参数名 | 类型 | 必选 | 描述 |
|-------|-----|------|-----|
| audioFile | file | 是 | 语音文件，支持格式：MP3, WAV, M4A，最大时长：60秒 |
| audioType | string | 是 | 语音类型，可选值：NORMAL_SPEECH, COUGH, BREATHING |
| notes | string | 否 | 相关备注信息 |
| recordTime | string | 否 | 录制时间，ISO 8601格式 |

**响应**

```
Status: 201 Created
Content-Type: application/json
```

**响应字段**

| 字段名 | 类型 | 描述 |
|-------|-----|------|
| id | string | 闻诊记录唯一标识 |
| audioUrl | string | 存储后的音频URL |
| analysis | object | 语音分析结果 |
| createdAt | string | 创建时间，ISO 8601格式 |

**响应示例**

```json
{
  "id": "vce_123456789",
  "audioUrl": "https://api.suoke.life/audio/voice/user123_20240715090000.mp3",
  "analysis": {
    "voiceCharacteristics": {
      "pitch": "LOW",
      "strength": "WEAK",
      "stability": "STABLE"
    },
    "breathPattern": {
      "rate": "NORMAL",
      "depth": "SHALLOW"
    },
    "overallAssessment": "声音低弱，气息浅短，提示气虚可能"
  },
  "createdAt": "2024-07-15T09:05:23Z"
}
```

### 问诊

#### 提交问诊表单

提交结构化问诊表单数据。

**请求**

```
POST /api/v1/diagnoses/interrogation
Content-Type: application/json
Authorization: Bearer {accessToken}
```

**请求参数**

| 参数名 | 类型 | 必选 | 描述 |
|-------|-----|------|-----|
| questionnaireType | string | 是 | 问诊表类型，可选值：GENERAL, CONSTITUTION, SPECIALIZED |
| responses | array | 是 | 问题回答数组 |
| context | object | 否 | 问诊上下文信息 |

**请求示例**

```json
{
  "questionnaireType": "CONSTITUTION",
  "responses": [
    {
      "questionId": "q001",
      "answer": "OFTEN",
      "details": "每周至少3-4次"
    },
    {
      "questionId": "q002",
      "answer": "RARELY",
      "details": "几乎不会"
    },
    // 更多问题回答...
  ],
  "context": {
    "purpose": "体质辨识",
    "completeTime": "2024-07-15T10:00:00Z"
  }
}
```

**响应**

```
Status: 201 Created
Content-Type: application/json
```

**响应字段**

| 字段名 | 类型 | 描述 |
|-------|-----|------|
| id | string | 问诊记录唯一标识 |
| analysis | object | 问诊分析结果 |
| constitutionScores | object | 体质评分（仅体质问诊返回） |
| recommendations | array | 建议数组 |
| createdAt | string | 创建时间，ISO 8601格式 |

**响应示例**

```json
{
  "id": "int_123456789",
  "analysis": {
    "mainFindings": [
      "易疲劳、气短",
      "不耐寒、手脚发凉",
      "睡眠质量一般"
    ],
    "summary": "表现为气虚、阳虚特征明显，兼有气郁特点"
  },
  "constitutionScores": {
    "PH": 45,    // 平和质
    "QX": 78,    // 气虚质
    "YX": 65,    // 阳虚质
    "YIX": 32,   // 阴虚质
    "TS": 28,    // 痰湿质
    "SR": 20,    // 湿热质
    "XY": 15,    // 血瘀质
    "QY": 18,    // 气郁质
    "TB": 25     // 特禀质
  },
  "recommendations": [
    {
      "category": "LIFESTYLE",
      "content": "建议适当增加有氧运动，如散步、太极等"
    },
    {
      "category": "DIET",
      "content": "饮食宜温热，可适当食用补气食物，如大枣、山药等"
    }
  ],
  "createdAt": "2024-07-15T10:15:23Z"
}
```

### 切诊

#### 提交脉象数据

提交脉象数据进行分析。

**请求**

```
POST /api/v1/diagnoses/palpation/pulse
Content-Type: application/json
Authorization: Bearer {accessToken}
```

**请求参数**

| 参数名 | 类型 | 必选 | 描述 |
|-------|-----|------|-----|
| deviceId | string | 否 | 采集设备ID |
| deviceType | string | 是 | 设备类型，可选值：PULSE_SENSOR, MOBILE_APP, MANUAL_INPUT |
| rawData | array | 否 | 原始脉搏数据（设备采集时必填） |
| manualInput | object | 否 | 手动输入的脉象特征（手动输入时必填） |
| measureTime | string | 是 | 测量时间，ISO 8601格式 |
| position | string | 是 | 测量位置，可选值：LEFT_CUNS, LEFT_GUAN, LEFT_CHI, RIGHT_CUNS, RIGHT_GUAN, RIGHT_CHI |
| notes | string | 否 | 相关备注信息 |

**请求示例（设备采集）**

```json
{
  "deviceId": "PS12345678",
  "deviceType": "PULSE_SENSOR",
  "rawData": [
    {"timestamp": 0, "value": 0.23},
    {"timestamp": 10, "value": 0.45},
    {"timestamp": 20, "value": 0.67},
    // 更多采样点...
  ],
  "measureTime": "2024-07-15T11:00:00Z",
  "position": "LEFT_CUNS",
  "notes": "静息状态下测量"
}
```

**请求示例（手动输入）**

```json
{
  "deviceType": "MANUAL_INPUT",
  "manualInput": {
    "pulseRate": 72,
    "rhythm": "REGULAR",
    "depth": "DEEP",
    "strength": "WEAK",
    "width": "THIN",
    "pulseType": "CHI_MAI"
  },
  "measureTime": "2024-07-15T11:00:00Z",
  "position": "LEFT_GUAN",
  "notes": "由专业中医师诊脉录入"
}
```

**响应**

```
Status: 201 Created
Content-Type: application/json
```

**响应字段**

| 字段名 | 类型 | 描述 |
|-------|-----|------|
| id | string | 切诊记录唯一标识 |
| pulseAnalysis | object | 脉象分析结果 |
| recommendations | array | 建议数组 |
| createdAt | string | 创建时间，ISO 8601格式 |

**响应示例**

```json
{
  "id": "pls_123456789",
  "pulseAnalysis": {
    "pulseRate": 72,
    "pulsePattern": {
      "rhythm": "REGULAR",
      "depth": "DEEP",
      "strength": "WEAK",
      "width": "THIN",
      "tension": "SOFT"
    },
    "pulseType": "CHI_MAI",
    "traditional": {
      "chiMaiDescription": "迟脉，脉来缓慢有力，一息四至",
      "relevance": "多见于阳虚证"
    },
    "overallAssessment": "脉象沉细软弱，提示气血两虚，阳气不足"
  },
  "recommendations": [
    {
      "category": "TREATMENT",
      "content": "建议温补阳气，佐以益气养血"
    }
  ],
  "createdAt": "2024-07-15T11:15:23Z"
}
```

### 四诊合参

#### 获取综合辨证结果

获取基于四诊数据的综合辨证结果。

**请求**

```
POST /api/v1/diagnoses/synthesis
Content-Type: application/json
Authorization: Bearer {accessToken}
```

**请求参数**

| 参数名 | 类型 | 必选 | 描述 |
|-------|-----|------|-----|
| tongueId | string | 否 | 舌诊记录ID |
| voiceId | string | 否 | 闻诊记录ID |
| interrogationId | string | 否 | 问诊记录ID |
| pulseId | string | 否 | 脉诊记录ID |
| additionalInfo | object | 否 | 补充信息 |

**请求示例**

```json
{
  "tongueId": "tng_123456789",
  "voiceId": "vce_123456789",
  "interrogationId": "int_123456789",
  "pulseId": "pls_123456789",
  "additionalInfo": {
    "recentSymptoms": ["疲劳", "手脚凉", "睡眠差"],
    "environment": {
      "season": "SUMMER",
      "weather": "HOT_HUMID"
    }
  }
}
```

**响应**

```
Status: 200 OK
Content-Type: application/json
```

**响应字段**

| 字段名 | 类型 | 描述 |
|-------|-----|------|
| id | string | 辨证记录唯一标识 |
| diagnosisTime | string | 辨证时间，ISO 8601格式 |
| constitutionResult | object | 体质辨识结果 |
| syndromeAnalysis | object | 证候分析 |
| recommendations | object | 综合建议 |
| createdAt | string | 创建时间，ISO 8601格式 |

**响应示例**

```json
{
  "id": "syn_123456789",
  "diagnosisTime": "2024-07-15T15:00:00Z",
  "constitutionResult": {
    "mainType": {
      "code": "QX",
      "name": "气虚质",
      "score": 78
    },
    "secondaryTypes": [
      {
        "code": "YX",
        "name": "阳虚质",
        "score": 65
      }
    ],
    "constitutionScores": {
      "PH": 45,
      "QX": 78,
      "YX": 65,
      "YIX": 32,
      "TS": 28,
      "SR": 20,
      "XY": 15,
      "QY": 18,
      "TB": 25
    }
  },
  "syndromeAnalysis": {
    "primarySyndrome": {
      "name": "脾肺气虚证",
      "description": "以脾肺气虚为主，兼有阳虚特征",
      "evidences": [
        {
          "source": "TONGUE",
          "finding": "舌质淡红、苔薄白",
          "relevance": "HIGH"
        },
        {
          "source": "VOICE",
          "finding": "声低气怯",
          "relevance": "MEDIUM"
        },
        {
          "source": "INTERROGATION",
          "finding": "易疲劳、气短",
          "relevance": "HIGH"
        },
        {
          "source": "PULSE",
          "finding": "脉沉细弱",
          "relevance": "HIGH"
        }
      ]
    },
    "secondarySyndromes": [
      {
        "name": "阳虚证",
        "description": "阳气不足，温煦失职",
        "evidences": [
          {
            "source": "INTERROGATION",
            "finding": "怕冷、手脚凉",
            "relevance": "HIGH"
          },
          {
            "source": "PULSE",
            "finding": "脉沉",
            "relevance": "MEDIUM"
          }
        ]
      }
    ]
  },
  "recommendations": {
    "lifestyle": [
      {
        "category": "ACTIVITY",
        "content": "适当进行太极、八段锦等缓和运动，避免过度劳累"
      },
      {
        "category": "REST",
        "content": "保证充足睡眠，早睡早起，中午适当休息"
      }
    ],
    "diet": [
      {
        "category": "PRINCIPLE",
        "content": "饮食宜温热，避免生冷食物"
      },
      {
        "category": "RECOMMENDED_FOODS",
        "items": ["大枣", "山药", "黄芪", "鸡肉", "羊肉"]
      },
      {
        "category": "AVOID_FOODS",
        "items": ["寒凉瓜果", "冰饮", "生冷食物"]
      }
    ],
    "conditioning": [
      {
        "method": "穴位按摩",
        "points": ["足三里", "气海", "关元"],
        "instruction": "每日按摩2-3次，每次5分钟"
      }
    ],
    "seasonalCare": {
      "currentSeason": "夏季",
      "guidance": "夏季注意防暑降温，但避免长时间处于空调环境"
    }
  },
  "createdAt": "2024-07-15T15:05:23Z"
}
```

## 数据模型

### 望诊数据模型

| 字段名 | 类型 | 描述 |
|-------|-----|------|
| id | string | 望诊记录唯一标识 |
| userId | string | 用户ID |
| imageUrl | string | 图片URL |
| thumbnailUrl | string | 缩略图URL |
| analysis | object | 分析结果 |
| captureTime | string | 拍摄时间 |
| captureEnvironment | object | 拍摄环境信息 |
| notes | string | 备注信息 |
| createdAt | string | 创建时间 |
| updatedAt | string | 更新时间 |

### 闻诊数据模型

| 字段名 | 类型 | 描述 |
|-------|-----|------|
| id | string | 闻诊记录唯一标识 |
| userId | string | 用户ID |
| audioUrl | string | 音频URL |
| audioType | string | 音频类型 |
| analysis | object | 分析结果 |
| recordTime | string | 录制时间 |
| notes | string | 备注信息 |
| createdAt | string | 创建时间 |
| updatedAt | string | 更新时间 |

### 问诊数据模型

| 字段名 | 类型 | 描述 |
|-------|-----|------|
| id | string | 问诊记录唯一标识 |
| userId | string | 用户ID |
| questionnaireType | string | 问诊表类型 |
| responses | array | 问题回答数组 |
| analysis | object | 分析结果 |
| constitutionScores | object | 体质评分 |
| recommendations | array | 建议数组 |
| context | object | 问诊上下文 |
| createdAt | string | 创建时间 |
| updatedAt | string | 更新时间 |

### 切诊数据模型

| 字段名 | 类型 | 描述 |
|-------|-----|------|
| id | string | 切诊记录唯一标识 |
| userId | string | 用户ID |
| deviceId | string | 设备ID |
| deviceType | string | 设备类型 |
| pulseAnalysis | object | 脉象分析 |
| measureTime | string | 测量时间 |
| position | string | 测量位置 |
| notes | string | 备注信息 |
| createdAt | string | 创建时间 |
| updatedAt | string | 更新时间 |

### 四诊合参模型

| 字段名 | 类型 | 描述 |
|-------|-----|------|
| id | string | 辨证记录唯一标识 |
| userId | string | 用户ID |
| diagnosisTime | string | 辨证时间 |
| tongueId | string | 舌诊记录ID |
| voiceId | string | 闻诊记录ID |
| interrogationId | string | 问诊记录ID |
| pulseId | string | 脉诊记录ID |
| constitutionResult | object | 体质辨识结果 |
| syndromeAnalysis | object | 证候分析 |
| recommendations | object | 综合建议 |
| createdAt | string | 创建时间 |
| updatedAt | string | 更新时间 |

## 附录

### 舌象特征枚举

| 分类 | 值 | 描述 |
|-----|-----|------|
| 舌色 | PALE | 淡白舌 |
| | PALE_RED | 淡红舌 |
| | RED | 红舌 |
| | DEEP_RED | 绛舌 |
| | PURPLE | 紫舌 |
| 舌态 | NORMAL | 正常 |
| | THIN | 瘦舌 |
| | FAT | 胖舌 |
| | LONG | 长舌 |
| | SHORT | 短舌 |
| | TREMBLING | 颤舌 |
| | STIFF | 强舌 |
| 舌苔 | NONE | 无苔 |
| | WHITE | 白苔 |
| | YELLOW | 黄苔 |
| | GRAY | 灰苔 |
| | BLACK | 黑苔 |
| 苔质 | THIN | 薄苔 |
| | THICK | 厚苔 |
| | GREASY | 腻苔 |
| | DRY | 燥苔 |
| | MOIST | 润苔 |
| | PEELED | 剥苔 |

### 脉象类型枚举

| 值 | 名称 | 描述 |
|-----|-----|------|
| FU_MAI | 浮脉 | 脉位表浅，举之有力，按之无力 |
| CHEN_MAI | 沉脉 | 脉位深，举之无力，按之有力 |
| CHI_MAI | 迟脉 | 脉搏缓慢，一息四至以下 |
| SHUO_MAI | 数脉 | 脉搏快速，一息六至以上 |
| XU_MAI | 虚脉 | 脉来软弱无力，按之空虚 |
| SHI_MAI | 实脉 | 脉来沉实有力，举按皆劲 |
| XIAN_MAI | 弦脉 | 脉来如弓弦，紧张有力 |
| HUA_MAI | 滑脉 | 脉来流利圆滑如珠走盘 |
| SE_MAI | 涩脉 | 脉来艰涩不畅，迟滞短促 |
| HONG_MAI | 洪脉 | 脉来强大而有力，来盛去衰 |

---

> 文档最后更新：2024年7月20日 