# 索克生活APP - Agent Coordinator Service API文档

## 概述

本文档详细描述索克生活APP的Agent Coordinator Service提供的所有API接口。该服务负责协调不同AI代理之间的交互和工作流程，为前端应用提供统一的接口。

## 基础信息

- **基础URL**:
  - 开发环境: `http://localhost:3001`
  - 测试环境: `https://api-test.suoke.life/api/v1/agents/coordinator`
  - 生产环境: `https://api.suoke.life/api/v1/agents/coordinator`

- **认证方式**: Bearer Token
- **响应格式**: JSON

## API健康检查

### 获取服务健康状态

- **URL**: `/health`
- **方法**: `GET`
- **描述**: 检查服务的健康状态
- **权限要求**: 无

**响应示例**:

```json
{
  "status": "ok",
  "service": "agent-coordinator-service",
  "version": "1.2.0",
  "timestamp": "2023-03-29T12:34:56.789Z",
  "uptime": 3600,
  "dependencies": {
    "database": "ok",
    "redis": "ok",
    "knowledge-graph-service": "ok",
    "rag-service": "ok"
  }
}
```

### 获取服务就绪状态

- **URL**: `/health/readiness`
- **方法**: `GET`
- **描述**: 检查服务是否已就绪可以接收请求
- **权限要求**: 无

**响应示例**:

```json
{
  "status": "ready",
  "timestamp": "2023-03-29T12:34:56.789Z"
}
```

### 获取服务存活状态

- **URL**: `/health/liveness`
- **方法**: `GET`
- **描述**: 检查服务是否存活
- **权限要求**: 无

**响应示例**:

```json
{
  "status": "alive",
  "timestamp": "2023-03-29T12:34:56.789Z"
}
```

## 代理管理API

### 注册新代理

- **URL**: `/agents/register`
- **方法**: `POST`
- **描述**: 向协调器注册新的AI代理
- **权限要求**: API密钥

**请求体**:

```json
{
  "agentId": "xiaoke-123",
  "name": "小可",
  "type": "assistant",
  "capabilities": ["text-generation", "tcm-diagnosis", "rag-enhanced"],
  "endpoint": "https://api.suoke.life/api/v1/agents/xiaoke",
  "healthCheckEndpoint": "/health",
  "apiKey": "xxxx-xxxx-xxxx",
  "status": "active",
  "maxConcurrentRequests": 10,
  "timeout": 30000,
  "metadata": {
    "version": "1.0.0",
    "description": "TCM领域知识专家",
    "modelType": "hybrid"
  }
}
```

**响应示例**:

```json
{
  "success": true,
  "message": "Agent registered successfully",
  "data": {
    "agentId": "xiaoke-123",
    "name": "小可",
    "type": "assistant",
    "status": "active",
    "registeredAt": "2023-03-29T12:34:56.789Z"
  }
}
```

### 获取代理列表

- **URL**: `/agents`
- **方法**: `GET`
- **描述**: 获取所有已注册代理的列表
- **权限要求**: API密钥

**查询参数**:

- `status` (可选): 按代理状态筛选 (active, inactive, all)
- `type` (可选): 按代理类型筛选
- `limit` (可选): 返回结果数量限制
- `offset` (可选): 分页偏移量

**响应示例**:

```json
{
  "success": true,
  "data": {
    "agents": [
      {
        "agentId": "xiaoke-123",
        "name": "小可",
        "type": "assistant",
        "capabilities": ["text-generation", "tcm-diagnosis", "rag-enhanced"],
        "status": "active",
        "lastSeen": "2023-03-29T12:34:56.789Z",
        "healthStatus": "healthy"
      },
      {
        "agentId": "xiaoai-456",
        "name": "小爱",
        "type": "assistant",
        "capabilities": ["text-generation", "multi-modal", "knowledge-base"],
        "status": "active",
        "lastSeen": "2023-03-29T12:30:56.789Z",
        "healthStatus": "healthy"
      }
    ],
    "total": 2,
    "limit": 10,
    "offset": 0
  }
}
```

### 获取代理详情

- **URL**: `/agents/:agentId`
- **方法**: `GET`
- **描述**: 获取特定代理的详细信息
- **权限要求**: API密钥

**响应示例**:

```json
{
  "success": true,
  "data": {
    "agentId": "xiaoke-123",
    "name": "小可",
    "type": "assistant",
    "capabilities": ["text-generation", "tcm-diagnosis", "rag-enhanced"],
    "endpoint": "https://api.suoke.life/api/v1/agents/xiaoke",
    "status": "active",
    "healthStatus": "healthy",
    "lastSeen": "2023-03-29T12:34:56.789Z",
    "registeredAt": "2023-03-20T10:00:00.000Z",
    "maxConcurrentRequests": 10,
    "currentLoad": 3,
    "uptime": 604800,
    "metadata": {
      "version": "1.0.0",
      "description": "TCM领域知识专家",
      "modelType": "hybrid"
    },
    "statistics": {
      "requestsTotal": 12500,
      "requestsLast24h": 1200,
      "averageResponseTime": 1200,
      "successRate": 99.8
    }
  }
}
```

### 更新代理信息

- **URL**: `/agents/:agentId`
- **方法**: `PATCH`
- **描述**: 更新现有代理的信息
- **权限要求**: API密钥

**请求体**:

```json
{
  "status": "inactive",
  "maxConcurrentRequests": 20,
  "timeout": 45000,
  "metadata": {
    "description": "更新后的TCM领域知识专家描述"
  }
}
```

**响应示例**:

```json
{
  "success": true,
  "message": "Agent updated successfully",
  "data": {
    "agentId": "xiaoke-123",
    "status": "inactive",
    "maxConcurrentRequests": 20,
    "timeout": 45000,
    "updatedAt": "2023-03-29T13:45:12.345Z"
  }
}
```

### 注销代理

- **URL**: `/agents/:agentId`
- **方法**: `DELETE`
- **描述**: 从协调器中注销代理
- **权限要求**: API密钥

**响应示例**:

```json
{
  "success": true,
  "message": "Agent deregistered successfully"
}
```

## 会话管理API

### 创建新会话

- **URL**: `/sessions`
- **方法**: `POST`
- **描述**: 创建一个新的交互会话
- **权限要求**: 用户认证

**请求体**:

```json
{
  "userId": "user-789",
  "sessionType": "chat",
  "initialContext": {
    "userPreferences": {
      "language": "zh-CN",
      "agents": ["xiaoke", "xiaoai"]
    },
    "userProfile": {
      "age": 35,
      "gender": "female",
      "healthConditions": ["allergy-pollen"]
    }
  },
  "metadata": {
    "source": "mobile-app",
    "clientVersion": "2.3.0",
    "deviceInfo": "iPhone 13"
  }
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "sessionId": "sess-abcdef123456",
    "userId": "user-789",
    "createdAt": "2023-03-29T12:34:56.789Z",
    "expiresAt": "2023-03-30T12:34:56.789Z",
    "status": "active"
  }
}
```

### 获取会话列表

- **URL**: `/sessions`
- **方法**: `GET`
- **描述**: 获取用户的会话列表
- **权限要求**: 用户认证

**查询参数**:

- `userId` (必需): 用户ID
- `status` (可选): 会话状态筛选 (active, archived, all)
- `limit` (可选): 返回结果数量限制
- `offset` (可选): 分页偏移量

**响应示例**:

```json
{
  "success": true,
  "data": {
    "sessions": [
      {
        "sessionId": "sess-abcdef123456",
        "userId": "user-789",
        "sessionType": "chat",
        "createdAt": "2023-03-29T12:34:56.789Z",
        "lastActivityAt": "2023-03-29T13:45:12.345Z",
        "messageCount": 15,
        "status": "active"
      },
      {
        "sessionId": "sess-ghijkl789012",
        "userId": "user-789",
        "sessionType": "diagnosis",
        "createdAt": "2023-03-28T10:11:12.345Z",
        "lastActivityAt": "2023-03-28T10:30:45.678Z",
        "messageCount": 8,
        "status": "archived"
      }
    ],
    "total": 2,
    "limit": 10,
    "offset": 0
  }
}
```

### 获取会话详情

- **URL**: `/sessions/:sessionId`
- **方法**: `GET`
- **描述**: 获取特定会话的详细信息
- **权限要求**: 用户认证

**响应示例**:

```json
{
  "success": true,
  "data": {
    "sessionId": "sess-abcdef123456",
    "userId": "user-789",
    "sessionType": "chat",
    "createdAt": "2023-03-29T12:34:56.789Z",
    "lastActivityAt": "2023-03-29T13:45:12.345Z",
    "expiresAt": "2023-03-30T12:34:56.789Z",
    "status": "active",
    "messageCount": 15,
    "participatingAgents": ["xiaoke-123", "xiaoai-456"],
    "context": {
      "userPreferences": {
        "language": "zh-CN",
        "agents": ["xiaoke", "xiaoai"]
      },
      "userProfile": {
        "age": 35,
        "gender": "female",
        "healthConditions": ["allergy-pollen"]
      },
      "conversationState": {
        "topic": "seasonal allergies",
        "sentiment": "neutral",
        "recentEntities": ["pollen", "allergy", "herbal tea"]
      }
    },
    "metadata": {
      "source": "mobile-app",
      "clientVersion": "2.3.0",
      "deviceInfo": "iPhone 13",
      "location": "Hangzhou"
    }
  }
}
```

### 更新会话状态

- **URL**: `/sessions/:sessionId`
- **方法**: `PATCH`
- **描述**: 更新会话的状态或上下文
- **权限要求**: 用户认证

**请求体**:

```json
{
  "status": "archived",
  "context": {
    "userPreferences": {
      "agents": ["xiaoke", "xiaoai", "soer"]
    },
    "conversationState": {
      "topic": "seasonal allergies remedies"
    }
  }
}
```

**响应示例**:

```json
{
  "success": true,
  "message": "Session updated successfully",
  "data": {
    "sessionId": "sess-abcdef123456",
    "status": "archived",
    "updatedAt": "2023-03-29T14:01:23.456Z"
  }
}
```

### 结束会话

- **URL**: `/sessions/:sessionId`
- **方法**: `DELETE`
- **描述**: 终止会话并清理资源
- **权限要求**: 用户认证

**响应示例**:

```json
{
  "success": true,
  "message": "Session ended successfully",
  "data": {
    "archivedAt": "2023-03-29T14:10:00.123Z"
  }
}
```

## 协调API

### 发送消息

- **URL**: `/coordination/message`
- **方法**: `POST`
- **描述**: 发送消息并获取AI代理响应
- **权限要求**: 用户认证

**请求体**:

```json
{
  "sessionId": "sess-abcdef123456",
  "messageId": "msg-123456789",
  "userId": "user-789",
  "content": "我最近花粉过敏严重，有什么中医调理方法吗？",
  "contentType": "text",
  "timestamp": "2023-03-29T14:15:32.789Z",
  "preferredAgents": ["xiaoke-123"],
  "attachments": [],
  "metadata": {
    "location": "Hangzhou",
    "source": "mobile-app",
    "clientTimezone": "Asia/Shanghai"
  }
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "messageId": "msg-123456789",
    "sessionId": "sess-abcdef123456",
    "responseId": "resp-987654321",
    "timestamp": "2023-03-29T14:15:33.123Z",
    "processingTime": 638,
    "responses": [
      {
        "agentId": "xiaoke-123",
        "content": "您好，针对花粉过敏，中医认为这属于肺卫不固的表现。建议：\n\n1. 饮食调理：多食用梨、银耳等滋阴润肺食物\n2. 中药调理：可考虑玉屏风散加减\n3. 穴位按摩：迎香穴、肺俞穴\n4. 避免接触花粉：外出佩戴口罩\n\n请问您的过敏症状具体有哪些表现？",
        "contentType": "text",
        "confidence": 0.92,
        "suggestedFollowups": [
          "这些食物有什么特别的做法推荐吗？",
          "玉屏风散的成分是什么？"
        ],
        "metadata": {
          "knowledgeSourcesUsed": ["TCM-allergy-treatment", "dietary-guidelines"],
          "reasoningPath": ["identify-condition", "match-tcm-pattern", "suggest-treatments"]
        }
      }
    ],
    "context": {
      "entities": ["花粉过敏", "中医调理", "肺卫不固", "玉屏风散"],
      "intents": ["seek-medical-advice", "request-tcm-solution"],
      "sentiment": "neutral",
      "urgency": "medium"
    }
  }
}
```

### 多代理协作请求

- **URL**: `/coordination/collaborate`
- **方法**: `POST`
- **描述**: 发起多个代理协作处理的请求
- **权限要求**: 用户认证

**请求体**:

```json
{
  "sessionId": "sess-abcdef123456",
  "requestId": "req-abcdef123456",
  "userId": "user-789",
  "query": "我想了解如何结合食疗和运动改善我的脾虚湿盛体质",
  "contentType": "text",
  "requiredAgents": ["xiaoke-123", "xiaoai-456"],
  "collaborationMode": "sequential",
  "timeout": 10000,
  "context": {
    "userProfile": {
      "age": 35,
      "gender": "female",
      "constitution": "spleen-deficiency",
      "symptoms": ["fatigue", "poor-appetite", "heavy-limbs"]
    }
  }
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "requestId": "req-abcdef123456",
    "sessionId": "sess-abcdef123456",
    "timestamp": "2023-03-29T14:30:12.345Z",
    "processingTime": 2135,
    "results": [
      {
        "agentId": "xiaoke-123",
        "role": "primary",
        "content": "针对脾虚湿盛体质，我建议以下食疗方案：\n\n1. 适宜食物：山药、薏米、扁豆、莲子、茯苓等健脾利湿食材\n2. 烹饪方式：以蒸煮为主，避免油腻生冷\n3. 茶饮推荐：藿香、佩兰、陈皮等配成健脾祛湿茶\n\n这些食材可以很好地帮助健脾祛湿，改善脾虚湿盛的状况。",
        "contentType": "text",
        "confidence": 0.95
      },
      {
        "agentId": "xiaoai-456",
        "role": "collaborator",
        "content": "对于脾虚湿盛体质的运动建议如下：\n\n1. 运动强度：中低强度为宜，避免大汗淋漓\n2. 推荐运动：太极、八段锦、慢走、气功等\n3. 运动时间：上午9-11点，下午3-5点最佳\n4. 注意事项：运动后及时保暖，避免受凉\n\n坚持适当运动结合小可推荐的食疗方案，能有效改善脾虚湿盛体质。",
        "contentType": "text",
        "confidence": 0.92
      }
    ],
    "combinedResponse": {
      "content": "针对您的脾虚湿盛体质，我们有以下综合建议：\n\n【食疗方面】\n• 适宜食物：山药、薏米、扁豆、莲子、茯苓等健脾利湿食材\n• 烹饪方式：以蒸煮为主，避免油腻生冷\n• 茶饮推荐：藿香、佩兰、陈皮等配成健脾祛湿茶\n\n【运动方面】\n• 运动强度：中低强度为宜，避免大汗淋漓\n• 推荐运动：太极、八段锦、慢走、气功等\n• 运动时间：上午9-11点，下午3-5点最佳\n• 注意事项：运动后及时保暖，避免受凉\n\n坚持这些建议，饮食和运动相结合，能有效改善您的脾虚湿盛体质。\n\n您是否需要了解更具体的食疗食谱或运动视频示范？",
      "contentType": "text",
      "suggestedFollowups": [
        "请推荐一些适合我体质的食谱",
        "八段锦有哪些动作适合我练习？",
        "这些茶饮的具体配方是什么？"
      ]
    },
    "metadata": {
      "coordinationPath": ["xiaoke-123", "xiaoai-456", "merge-results"],
      "consensusLevel": "high",
      "knowledgeSourcesUsed": [
        "tcm-constitution-library",
        "dietary-guidelines",
        "exercise-recommendations"
      ]
    }
  }
}
```

### 获取代理任务状态

- **URL**: `/coordination/tasks/:taskId`
- **方法**: `GET`
- **描述**: 获取长时间运行的代理任务状态
- **权限要求**: 用户认证

**响应示例**:

```json
{
  "success": true,
  "data": {
    "taskId": "task-abcdef123456",
    "requestId": "req-abcdef123456",
    "sessionId": "sess-abcdef123456",
    "status": "in_progress",
    "progress": 65,
    "startedAt": "2023-03-29T14:45:00.000Z",
    "estimatedCompletion": "2023-03-29T14:47:30.000Z",
    "currentStage": "knowledge_retrieval",
    "participatingAgents": [
      {
        "agentId": "xiaoke-123",
        "status": "completed"
      },
      {
        "agentId": "xiaoai-456",
        "status": "in_progress"
      }
    ]
  }
}
```

### 取消代理任务

- **URL**: `/coordination/tasks/:taskId`
- **方法**: `DELETE`
- **描述**: 取消正在进行的代理任务
- **权限要求**: 用户认证

**响应示例**:

```json
{
  "success": true,
  "message": "Task cancelled successfully",
  "data": {
    "taskId": "task-abcdef123456",
    "cancelledAt": "2023-03-29T14:46:12.345Z",
    "status": "cancelled"
  }
}
```

## 知识图谱API

### 实体查询

- **URL**: `/knowledge/entities`
- **方法**: `GET`
- **描述**: 查询知识图谱中的实体
- **权限要求**: API密钥

**查询参数**:

- `query` (必需): 查询文本
- `types` (可选): 实体类型筛选，多个用逗号分隔
- `limit` (可选): 返回结果数量限制
- `offset` (可选): 分页偏移量

**响应示例**:

```json
{
  "success": true,
  "data": {
    "entities": [
      {
        "id": "entity-123",
        "name": "玉屏风散",
        "type": "TCM_Formula",
        "confidence": 0.95,
        "properties": {
          "ingredients": ["黄芪", "白术", "防风"],
          "effects": ["益气固表", "止汗固卫"],
          "indications": ["表虚自汗", "易感冒"]
        },
        "relationships": [
          {
            "type": "treats",
            "target": "entity-456",
            "confidence": 0.92
          }
        ]
      },
      {
        "id": "entity-456",
        "name": "过敏性鼻炎",
        "type": "Health_Condition",
        "confidence": 0.98,
        "properties": {
          "tcmPattern": ["肺卫不固", "风热犯肺"],
          "symptoms": ["打喷嚏", "鼻塞", "流涕"]
        }
      }
    ],
    "total": 2,
    "limit": 10,
    "offset": 0
  }
}
```

### 关系查询

- **URL**: `/knowledge/relationships`
- **方法**: `GET`
- **描述**: 查询知识图谱中的实体关系
- **权限要求**: API密钥

**查询参数**:

- `sourceId` (可选): 源实体ID
- `targetId` (可选): 目标实体ID
- `types` (可选): 关系类型筛选，多个用逗号分隔
- `limit` (可选): 返回结果数量限制
- `offset` (可选): 分页偏移量

**响应示例**:

```json
{
  "success": true,
  "data": {
    "relationships": [
      {
        "id": "rel-123",
        "sourceId": "entity-123",
        "sourceName": "玉屏风散",
        "targetId": "entity-456",
        "targetName": "过敏性鼻炎",
        "type": "treats",
        "confidence": 0.92,
        "properties": {
          "efficacy": "moderate",
          "researchSupport": "traditional",
          "usageDuration": "long-term"
        }
      },
      {
        "id": "rel-124",
        "sourceId": "entity-123",
        "sourceName": "玉屏风散",
        "targetId": "entity-789",
        "targetName": "肺卫不固",
        "type": "addresses",
        "confidence": 0.96,
        "properties": {
          "primaryMechanism": true,
          "traditionReference": "伤寒论"
        }
      }
    ],
    "total": 2,
    "limit": 10,
    "offset": 0
  }
}
```

### 知识推理

- **URL**: `/knowledge/infer`
- **方法**: `POST`
- **描述**: 在知识图谱上执行推理
- **权限要求**: API密钥

**请求体**:

```json
{
  "query": "花粉过敏可以用哪些中药方剂治疗？",
  "context": {
    "entities": ["花粉过敏", "过敏性鼻炎"],
    "maxResults": 5,
    "minConfidence": 0.7,
    "reasoningDepth": 2
  }
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "results": [
      {
        "formula": {
          "id": "entity-123",
          "name": "玉屏风散",
          "type": "TCM_Formula",
          "confidence": 0.92
        },
        "reasoningPath": [
          "花粉过敏 (类似于) 过敏性鼻炎",
          "过敏性鼻炎 (表现为) 肺卫不固",
          "玉屏风散 (治疗) 肺卫不固"
        ],
        "evidence": {
          "clinicalStudies": 12,
          "traditionReferences": ["《伤寒论》", "《金匮要略》"]
        }
      },
      {
        "formula": {
          "id": "entity-234",
          "name": "小青龙汤",
          "type": "TCM_Formula",
          "confidence": 0.85
        },
        "reasoningPath": [
          "花粉过敏 (类似于) 过敏性鼻炎",
          "过敏性鼻炎 (可表现为) 风寒束表",
          "小青龙汤 (治疗) 风寒束表"
        ],
        "evidence": {
          "clinicalStudies": 8,
          "traditionReferences": ["《伤寒论》"]
        }
      }
    ],
    "queryExecutionTime": 320,
    "reasoningSteps": 15
  }
}
```

## 错误响应

所有API在出错时将返回一致的错误格式：

```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested resource could not be found",
    "details": "Agent with ID 'xiaoke-999' does not exist",
    "requestId": "req-abcdef123456"
  }
}
```

常见错误代码：

- `BAD_REQUEST`: 请求参数错误
- `UNAUTHORIZED`: 未认证或认证失败
- `FORBIDDEN`: 权限不足
- `RESOURCE_NOT_FOUND`: 请求的资源不存在
- `CONFLICT`: 资源冲突（如重复创建）
- `INTERNAL_ERROR`: 服务器内部错误
- `SERVICE_UNAVAILABLE`: 服务暂时不可用
- `GATEWAY_TIMEOUT`: 与后端服务通信超时

## 速率限制

API实施了速率限制以保护服务不被滥用：

- 认证用户: 100个请求/分钟
- 未认证用户: 10个请求/分钟
- 管理级API: 200个请求/分钟

当超过速率限制时，服务将返回429状态码，并在响应头中包含：

- `X-RateLimit-Limit`: 允许的请求数
- `X-RateLimit-Remaining`: 剩余的请求数
- `X-RateLimit-Reset`: 限制重置的时间戳

## 版本历史

| 版本 | 日期 | 变更说明 |
|-----|------|---------|
| v1.0.0 | 2023-01-15 | 初始版本 |
| v1.1.0 | 2023-02-20 | 增加多代理协作API |
| v1.2.0 | 2023-03-25 | 增加知识图谱推理API和性能优化 |

## 联系与支持

- 技术支持: support@suoke.life
- 文档反馈: docs@suoke.life
- API状态页: https://status.suoke.life

---

**文档更新日期**: 2023-03-29  
**API版本**: v1.2.0 