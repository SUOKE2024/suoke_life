# 智能体 API

## 概述

智能体API提供与索克生活APP四大AI智能体（小艾、小克、老克、索儿）的交互功能。通过这些API，客户端可以实现自然语言对话、知识查询、服务推荐和健康建议等功能。

## 基础端点

```
https://api.suoke.life/api/v1/agents
```

## 接口列表

### 通用交互

#### 智能体对话

与指定智能体进行对话交互。

**请求**

```
POST /api/v1/agents/{agentType}/chat
Content-Type: application/json
Authorization: Bearer {accessToken}
```

**URL参数**

| 参数名 | 类型 | 必选 | 描述 |
|-------|-----|------|-----|
| agentType | string | 是 | 智能体类型，可选值：xiaoai, xiaoke, laoke, suoer |

**请求参数**

| 参数名 | 类型 | 必选 | 描述 |
|-------|-----|------|-----|
| message | string | 是 | 用户消息内容，最大5000字符 |
| sessionId | string | 否 | 会话ID，用于维持对话上下文，首次对话可不传 |
| stream | boolean | 否 | 是否使用流式响应，默认false |
| context | object | 否 | 额外上下文信息 |
| inputType | string | 否 | 输入类型，可选值：TEXT, VOICE, IMAGE，默认TEXT |
| attachments | array | 否 | 附件数组，用于图像或语音输入 |

**请求示例（文本对话）**

```json
{
  "message": "我最近经常感到疲惫，可能是什么原因？",
  "sessionId": "sess_123456789",
  "context": {
    "location": "北京",
    "weather": "阴天",
    "temperature": 28
  }
}
```

**请求示例（图像输入）**

```json
{
  "message": "这张舌头照片看起来健康吗？",
  "sessionId": "sess_123456789",
  "inputType": "IMAGE",
  "attachments": [
    {
      "type": "IMAGE",
      "url": "https://api.suoke.life/temp/uploads/image123.jpg",
      "contentType": "image/jpeg"
    }
  ]
}
```

**响应（非流式）**

```
Status: 200 OK
Content-Type: application/json
```

**响应字段**

| 字段名 | 类型 | 描述 |
|-------|-----|------|
| id | string | 响应唯一标识 |
| sessionId | string | 会话ID |
| response | string | 智能体回复内容 |
| responseType | string | 响应类型：TEXT, MULTIMEDIA |
| contentElements | array | 多媒体内容元素（如有） |
| suggestedActions | array | 建议后续操作 |
| metadata | object | 元数据信息 |
| createdAt | string | 创建时间，ISO 8601格式 |

**响应示例**

```json
{
  "id": "resp_123456789",
  "sessionId": "sess_123456789",
  "response": "疲惫感可能与多种因素有关，例如睡眠不足、营养不均衡、工作压力过大或身体状况变化等。您的具体情况可能是气虚导致的疲惫，表现为少气懒言、容易出汗。建议您通过以下方式改善：\n\n1. 保证充足睡眠\n2. 合理膳食，适当进食大枣、山药等补气食物\n3. 适量运动，如散步、太极拳等\n4. 保持心情舒畅，避免过度焦虑\n\n需要进一步了解您的情况来给出更精确的建议。您愿意分享更多关于您的疲惫感的细节吗？比如何时出现，有什么诱因？",
  "responseType": "TEXT",
  "suggestedActions": [
    {
      "type": "REPLY",
      "text": "我还有头晕的症状"
    },
    {
      "type": "REPLY",
      "text": "我睡眠质量不好"
    },
    {
      "type": "SERVICE",
      "text": "查看体质测试",
      "serviceId": "srv_constitution_test"
    }
  ],
  "metadata": {
    "agentType": "ai",
    "confidence": 0.92,
    "topics": ["疲惫", "气虚", "健康建议"]
  },
  "createdAt": "2024-07-20T10:15:23Z"
}
```

**响应（流式）**

对于流式响应，服务器将发送一系列事件流数据，每个事件包含部分响应内容：

```
HTTP/1.1 200 OK
Content-Type: text/event-stream
Connection: keep-alive
Cache-Control: no-cache

data: {"id":"stream_1","type":"start","sessionId":"sess_123456789"}

data: {"id":"stream_2","type":"content","content":"疲惫感可能与多种因素有关，"}

data: {"id":"stream_3","type":"content","content":"例如睡眠不足、营养不均衡、工作压力过大或身体状况变化等。"}

data: {"id":"stream_4","type":"content","content":"您的具体情况可能是气虚导致的疲惫，表现为少气懒言、容易出汗。"}

data: {"id":"stream_5","type":"suggestedActions","actions":[{"type":"REPLY","text":"我还有头晕的症状"},{"type":"REPLY","text":"我睡眠质量不好"},{"type":"SERVICE","text":"查看体质测试","serviceId":"srv_constitution_test"}]}

data: {"id":"stream_6","type":"end","metadata":{"agentType":"ai","confidence":0.92,"topics":["疲惫","气虚","健康建议"]}}
```

**错误响应**

| HTTP状态码 | 错误码 | 描述 |
|-----------|-------|------|
| 400 | INVALID_MESSAGE | 消息内容无效或为空 |
| 400 | INVALID_ATTACHMENT | 附件格式不支持 |
| 404 | AGENT_NOT_FOUND | 指定的智能体类型不存在 |
| 429 | RATE_LIMITED | 请求频率超过限制 |

#### 获取会话历史

获取与智能体的历史对话记录。

**请求**

```
GET /api/v1/agents/sessions/{sessionId}/history
Content-Type: application/json
Authorization: Bearer {accessToken}
```

**URL参数**

| 参数名 | 类型 | 必选 | 描述 |
|-------|-----|------|-----|
| sessionId | string | 是 | 会话ID |

**请求参数**

| 参数名 | 类型 | 必选 | 描述 |
|-------|-----|------|-----|
| limit | integer | 否 | 返回消息数量限制，默认20，最大50 |
| before | string | 否 | 指定时间戳之前的消息，ISO 8601格式 |

**响应**

```
Status: 200 OK
Content-Type: application/json
```

**响应字段**

| 字段名 | 类型 | 描述 |
|-------|-----|------|
| sessionId | string | 会话ID |
| messages | array | 消息数组 |
| hasMore | boolean | 是否有更多历史消息 |

**响应示例**

```json
{
  "sessionId": "sess_123456789",
  "messages": [
    {
      "id": "msg_123456789",
      "role": "USER",
      "content": "我最近经常感到疲惫，可能是什么原因？",
      "timestamp": "2024-07-20T10:10:00Z"
    },
    {
      "id": "resp_123456789",
      "role": "AGENT",
      "agentType": "ai",
      "content": "疲惫感可能与多种因素有关，例如睡眠不足、营养不均衡、工作压力过大或身体状况变化等。您的具体情况可能是气虚导致的疲惫，表现为少气懒言、容易出汗。建议您通过以下方式改善：\n\n1. 保证充足睡眠\n2. 合理膳食，适当进食大枣、山药等补气食物\n3. 适量运动，如散步、太极拳等\n4. 保持心情舒畅，避免过度焦虑\n\n需要进一步了解您的情况来给出更精确的建议。您愿意分享更多关于您的疲惫感的细节吗？比如何时出现，有什么诱因？",
      "timestamp": "2024-07-20T10:15:23Z"
    },
    {
      "id": "msg_123456790",
      "role": "USER",
      "content": "我通常下午就会特别困，而且容易出汗",
      "timestamp": "2024-07-20T10:18:00Z"
    },
    {
      "id": "resp_123456790",
      "role": "AGENT",
      "agentType": "ai",
      "content": "下午特别疲惫并且容易出汗，从中医角度看，很可能是脾胃功能减弱导致的气虚表现。脾胃是气血生化之源，功能减弱会导致气血生成不足，进而出现疲乏、自汗等症状。\n\n针对您的情况，建议：\n\n1. 调整午餐：避免过于油腻和生冷食物，适量进食温热食物\n2. 午休：可安排15-30分钟短暂午休\n3. 穴位按摩：可按摩足三里、神阙、气海等穴位\n4. 饮食调理：适当食用山药、莲子、白术等健脾益气食材\n\n您平时的饮食习惯如何？是否有吃早餐的习惯？",
      "timestamp": "2024-07-20T10:20:15Z"
    }
  ],
  "hasMore": false
}
```

### 特定智能体功能

#### 小艾（xiaoai）- 四诊引导

获取下一步四诊引导指示。

**请求**

```
POST /api/v1/agents/xiaoai/diagnosis-guide
Content-Type: application/json
Authorization: Bearer {accessToken}
```

**请求参数**

| 参数名 | 类型 | 必选 | 描述 |
|-------|-----|------|-----|
| currentStep | string | 否 | 当前诊断步骤，未提供则自动判断 |
| completedSteps | array | 否 | 已完成的诊断步骤数组 |
| sessionId | string | 否 | 会话ID |

**请求示例**

```json
{
  "currentStep": "TONGUE_INSPECTION",
  "completedSteps": ["BASIC_INQUIRY"],
  "sessionId": "sess_123456789"
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
| nextStep | string | 推荐的下一步诊断步骤 |
| guidance | string | 引导说明 |
| instructions | object | 详细指导说明 |
| progress | object | 整体诊断进度 |

**响应示例**

```json
{
  "nextStep": "TONGUE_INSPECTION",
  "guidance": "接下来，让我们进行望诊中的舌象观察，这有助于了解您的内脏功能状态",
  "instructions": {
    "preparation": "请站在光线充足的地方，面对相机",
    "action": "伸出舌头，尽量保持自然，不要紧张用力",
    "captureGuide": "保持舌头稳定约3秒钟，系统会自动捕捉图像",
    "tips": "最好在早晨空腹状态下拍摄，或距离上次进食饮水至少2小时"
  },
  "progress": {
    "completed": 1,
    "total": 5,
    "percentComplete": 20
  }
}
```

#### 小克（xiaoke）- 服务推荐

获取基于用户状况的个性化服务推荐。

**请求**

```
POST /api/v1/agents/xiaoke/recommendations
Content-Type: application/json
Authorization: Bearer {accessToken}
```

**请求参数**

| 参数名 | 类型 | 必选 | 描述 |
|-------|-----|------|-----|
| category | string | 否 | 服务类别，如MEDICAL_SERVICE, FOOD, HERBAL_PRODUCT |
| query | string | 否 | 搜索查询 |
| constitution | array | 否 | 体质类型代码数组 |
| location | object | 否 | 用户位置信息 |
| limit | integer | 否 | 返回结果数量限制，默认10 |

**请求示例**

```json
{
  "category": "HERBAL_PRODUCT",
  "constitution": ["QX", "YX"],
  "query": "补气",
  "location": {
    "latitude": 39.9042,
    "longitude": 116.4074,
    "city": "北京"
  },
  "limit": 5
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
| recommendations | array | 推荐服务或产品数组 |
| explanation | string | 推荐理由说明 |
| constitutionRelevance | object | 体质相关性分析 |

**响应示例**

```json
{
  "recommendations": [
    {
      "id": "prd_123456789",
      "name": "有机黄芪片",
      "category": "HERBAL_PRODUCT",
      "imageUrl": "https://api.suoke.life/images/products/astragalus_1.jpg",
      "price": {
        "amount": 98,
        "currency": "CNY",
        "unit": "250g"
      },
      "rating": 4.9,
      "relevanceScore": 0.95,
      "distance": null,
      "shortDescription": "内蒙古草原野生黄芪，切片加工，适合气虚体质"
    },
    {
      "id": "prd_123456790",
      "name": "山药枸杞茶",
      "category": "HERBAL_PRODUCT",
      "imageUrl": "https://api.suoke.life/images/products/yam_tea.jpg",
      "price": {
        "amount": 108,
        "currency": "CNY",
        "unit": "盒"
      },
      "rating": 4.8,
      "relevanceScore": 0.92,
      "distance": null,
      "shortDescription": "精选山药、枸杞等组方，温和补益气血"
    },
    // 更多推荐...
  ],
  "explanation": "基于您的气虚、阳虚体质特点，精选了具有补气养阳功效的产品。黄芪、山药等食材对于改善疲乏、自汗等气虚症状有良好效果，同时兼顾阳虚体质的温补需求。",
  "constitutionRelevance": {
    "QX": {
      "score": 0.95,
      "explanation": "推荐产品多具有补气健脾功效，适合气虚体质"
    },
    "YX": {
      "score": 0.85,
      "explanation": "部分推荐产品兼具温阳功效，适合阳虚体质"
    }
  }
}
```

#### 老克（laoke）- 知识查询

查询中医健康知识库。

**请求**

```
POST /api/v1/agents/laoke/knowledge
Content-Type: application/json
Authorization: Bearer {accessToken}
```

**请求参数**

| 参数名 | 类型 | 必选 | 描述 |
|-------|-----|------|-----|
| query | string | 是 | 知识查询问题 |
| category | string | 否 | 知识分类，如TCM_BASIC, CONSTITUTION, HERBAL, ACUPOINT |
| format | string | 否 | 返回格式，可选值：TEXT, STRUCTURED，默认TEXT |
| level | string | 否 | 知识深度级别，可选值：BEGINNER, INTERMEDIATE, ADVANCED |

**请求示例**

```json
{
  "query": "五运六气的基本概念是什么？",
  "category": "TCM_BASIC",
  "format": "STRUCTURED",
  "level": "INTERMEDIATE"
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
| answer | string/object | 知识回答内容，根据format参数返回不同格式 |
| sources | array | 知识来源引用 |
| relatedTopics | array | 相关知识主题 |
| level | string | 知识深度级别 |

**响应示例（TEXT格式）**

```json
{
  "answer": "五运六气是中医学对自然界时间与空间运动变化规律的概括，是中医整体观念的重要组成部分。\n\n**五运**指木、火、土、金、水五行在时间上的运动变化，对应一年中春、夏、长夏、秋、冬五个时序，代表五种不同的气候特点。\n\n**六气**指风、火、暑、湿、燥、寒六种自然界的气候变化，是六种自然因素在一年中的主导气候。\n\n五运六气学说认为，这些自然变化规律与人体生理、病理密切相关，人们可以根据五运六气的变化规律预测疾病的发生发展，并采取相应的防治措施。在临床上，医者需考虑季节、气候变化对疾病的影响，辨明病机，调整治疗策略。",
  "sources": [
    {
      "title": "黄帝内经·素问·天元纪大论",
      "description": "古代医学经典，系统阐述五运六气理论",
      "relevance": "PRIMARY"
    },
    {
      "title": "中医基础理论",
      "author": "张伯礼",
      "publication": "中国中医药出版社，2016",
      "relevance": "SECONDARY"
    }
  ],
  "relatedTopics": [
    {
      "title": "中医整体观",
      "id": "topic_8765432"
    },
    {
      "title": "天人相应",
      "id": "topic_8765433"
    },
    {
      "title": "五行学说",
      "id": "topic_8765434"
    }
  ],
  "level": "INTERMEDIATE"
}
```

**响应示例（STRUCTURED格式）**

```json
{
  "answer": {
    "definition": "五运六气是中医学对自然界时间与空间运动变化规律的概括，是中医整体观念的重要组成部分。",
    "components": {
      "fiveMovements": {
        "name": "五运",
        "description": "指木、火、土、金、水五行在时间上的运动变化",
        "correspondence": "对应一年中春、夏、长夏、秋、冬五个时序",
        "representation": "代表五种不同的气候特点"
      },
      "sixQi": {
        "name": "六气",
        "description": "指风、火、暑、湿、燥、寒六种自然界的气候变化",
        "representation": "是六种自然因素在一年中的主导气候"
      }
    },
    "significance": {
      "theory": "五运六气学说认为，这些自然变化规律与人体生理、病理密切相关",
      "application": "人们可以根据五运六气的变化规律预测疾病的发生发展，并采取相应的防治措施",
      "clinical": "在临床上，医者需考虑季节、气候变化对疾病的影响，辨明病机，调整治疗策略"
    }
  },
  "sources": [
    {
      "title": "黄帝内经·素问·天元纪大论",
      "description": "古代医学经典，系统阐述五运六气理论",
      "relevance": "PRIMARY"
    },
    {
      "title": "中医基础理论",
      "author": "张伯礼",
      "publication": "中国中医药出版社，2016",
      "relevance": "SECONDARY"
    }
  ],
  "relatedTopics": [
    {
      "title": "中医整体观",
      "id": "topic_8765432"
    },
    {
      "title": "天人相应",
      "id": "topic_8765433"
    },
    {
      "title": "五行学说",
      "id": "topic_8765434"
    }
  ],
  "level": "INTERMEDIATE"
}
```

#### 索儿（suoer）- 健康追踪与建议

获取个性化健康行为建议和追踪统计。

**请求**

```
POST /api/v1/agents/suoer/health-guidance
Content-Type: application/json
Authorization: Bearer {accessToken}
```

**请求参数**

| 参数名 | 类型 | 必选 | 描述 |
|-------|-----|------|-----|
| category | string | 否 | 建议类别，如DIET, EXERCISE, SLEEP, EMOTION |
| constitution | array | 否 | 体质类型代码数组 |
| season | string | 否 | 季节，可选值：SPRING, SUMMER, AUTUMN, WINTER |
| healthData | object | 否 | 最近健康数据摘要 |

**请求示例**

```json
{
  "category": "DIET",
  "constitution": ["QX", "YX"],
  "season": "SUMMER",
  "healthData": {
    "recentSymptoms": ["fatigue", "sweating", "poor_appetite"],
    "sleepQuality": "FAIR",
    "exerciseFrequency": "LOW"
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
| guidance | object | 健康指导建议 |
| seasonalTips | object | 时令养生提示 |
| statistics | object | 健康数据统计与趋势 |
| goals | array | 推荐健康目标 |

**响应示例**

```json
{
  "guidance": {
    "summary": "夏季气虚体质的饮食调理应以清淡、易消化、补气为原则",
    "recommendations": [
      {
        "title": "适宜食物",
        "items": [
          {
            "name": "薏苡仁",
            "benefit": "健脾渗湿，补气清热",
            "usage": "可煮粥食用，每日一次"
          },
          {
            "name": "山药",
            "benefit": "补脾益气，固表止汗",
            "usage": "蒸食或煲汤，每周3-4次"
          },
          {
            "name": "莲子",
            "benefit": "补脾止泻，益肾固精",
            "usage": "可煮粥或煲汤"
          }
        ]
      },
      {
        "title": "饮食原则",
        "content": "1. 少食生冷\n2. 适量多餐\n3. 细嚼慢咽\n4. 七分饱为宜\n5. 保持规律饮食时间"
      },
      {
        "title": "不宜食物",
        "items": ["冰镇饮料", "过于油腻食物", "辛辣刺激食物", "烧烤类食物"]
      }
    ]
  },
  "seasonalTips": {
    "season": "夏季",
    "solarTerm": "小暑",
    "generalPrinciple": "夏季养生贵在养心，注意防暑降温，保持情志舒畅",
    "specificSuggestions": [
      "起居宜晚睡早起，午时小憩",
      "精神宜静养，避免过度兴奋",
      "饮食宜清淡，适当食用苦味食物",
      "注意防暑，但避免长时间处于空调环境"
    ]
  },
  "statistics": {
    "healthTrend": {
      "sleepQuality": {
        "current": "FAIR",
        "trend": "STABLE",
        "weeklyAverage": 6.5
      },
      "appetite": {
        "current": "POOR",
        "trend": "DECREASING",
        "weeklyCaloricIntake": 1800
      },
      "energy": {
        "current": "LOW",
        "trend": "STABLE"
      }
    },
    "behaviorCompletion": {
      "recommendedActions": 15,
      "completedActions": 9,
      "completionRate": 0.6
    }
  },
  "goals": [
    {
      "id": "goal_123456789",
      "title": "增加蛋白质摄入",
      "description": "每日摄入足够优质蛋白质，如鱼、瘦肉、豆制品等",
      "target": "每日60-70克蛋白质",
      "duration": "4周",
      "difficulty": "MEDIUM",
      "benefitsForConstitution": "有助于改善气虚体质，增强体力"
    },
    {
      "id": "goal_123456790",
      "title": "食用山药粥",
      "description": "每周3次食用山药薏米粥，补脾益气",
      "target": "每周3次，每次100克山药",
      "duration": "2周",
      "difficulty": "EASY",
      "benefitsForConstitution": "健脾益气，改善气虚症状"
    }
  ]
}
```

## 数据模型

### 智能体消息模型

| 字段名 | 类型 | 描述 |
|-------|-----|------|
| id | string | 消息唯一标识 |
| sessionId | string | 会话ID |
| role | string | 角色：USER, AGENT |
| agentType | string | 智能体类型（仅对AGENT角色有效） |
| content | string | 消息内容 |
| contentType | string | 内容类型：TEXT, IMAGE, VOICE, MIXED |
| attachments | array | 附件数组 |
| metadata | object | 元数据 |
| timestamp | string | 时间戳 |

### 智能体会话模型

| 字段名 | 类型 | 描述 |
|-------|-----|------|
| id | string | 会话唯一标识 |
| userId | string | 用户ID |
| title | string | 会话标题 |
| agentTypes | array | 参与的智能体类型数组 |
| status | string | 会话状态：ACTIVE, ARCHIVED, DELETED |
| lastMessageAt | string | 最后消息时间 |
| contextData | object | 会话上下文数据 |
| createdAt | string | 创建时间 |
| updatedAt | string | 更新时间 |

## 附录

### 智能体类型

| 代码 | 名称 | 描述 |
|-----|-----|------|
| xiaoai | 小艾 | 交互与四诊协调 |
| xiaoke | 小克 | 服务资源管理 |
| laoke | 老克 | 知识传播与学习引导 |
| suoer | 索儿 | 生活健康管理 |

### 响应类型

| 类型 | 描述 |
|-----|------|
| TEXT | 纯文本响应 |
| MULTIMEDIA | 包含多媒体元素的响应 |
| STRUCTURED | 结构化数据响应 |
| ERROR | 错误响应 |

### 建议动作类型

| 类型 | 描述 |
|-----|------|
| REPLY | 建议用户回复 |
| SERVICE | 服务或功能跳转 |
| DIAGNOSIS | 诊断操作 |
| KNOWLEDGE | 知识查询 |
| PRODUCT | 产品推荐 |

---

> 本文档最后更新时间：2025年5月9日  
> 文档状态：已审核
> 审核人：技术架构委员会