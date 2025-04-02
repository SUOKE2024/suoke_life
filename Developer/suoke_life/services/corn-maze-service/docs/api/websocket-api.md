# 玉米迷宫服务 WebSocket API 规范

本文档详细说明玉米迷宫服务的WebSocket通信协议，包括连接建立、消息格式、事件类型以及错误处理机制。所有客户端与服务器之间的实时交互均遵循本规范。

## 目录

1. [连接建立](#1-连接建立)
2. [消息格式](#2-消息格式)
3. [客户端事件](#3-客户端事件)
4. [服务器事件](#4-服务器事件)
5. [错误处理](#5-错误处理)
6. [心跳机制](#6-心跳机制)
7. [安全与性能考量](#7-安全与性能考量)
8. [版本控制](#8-版本控制)

## 1. 连接建立

### 1.1 WebSocket 端点

```
ws://BASE_URL/corn-maze/realtime?token={jwt_token}&userId={user_id}&teamId={team_id}
```

### 1.2 连接参数

| 参数     | 类型   | 是否必须 | 描述                        |
|----------|--------|----------|---------------------------|
| token    | string | 是       | JWT认证令牌                 |
| userId   | string | 是       | 用户ID                     |
| teamId   | string | 否       | 团队ID (如已加入团队)       |
| deviceId | string | 是       | 设备唯一标识符             |

### 1.3 连接状态码

| 状态码 | 描述                             |
|--------|----------------------------------|
| 101    | 切换协议，连接成功               |
| 401    | 未授权，认证失败                 |
| 403    | 禁止访问，权限不足               |
| 429    | 请求过多，超出连接限制           |
| 500    | 服务器内部错误                   |

### 1.4 连接流程

1. 客户端向WebSocket端点发起连接请求
2. 服务器验证认证令牌和参数
3. 服务器接受/拒绝连接
4. 连接成功后，服务器发送`welcome`事件

## 2. 消息格式

所有消息采用JSON格式，包含以下基本结构：

### 2.1 基本格式

```json
{
  "type": "event_type",
  "id": "unique_message_id",
  "timestamp": 1635123456789,
  "data": {
    // 具体事件数据
  }
}
```

### 2.2 字段说明

| 字段      | 类型   | 描述                                |
|-----------|--------|-------------------------------------|
| type      | string | 事件类型，确定消息的处理方式        |
| id        | string | 消息唯一ID，用于确认和重试          |
| timestamp | number | 消息发送时间戳（毫秒）              |
| data      | object | 事件的具体数据，根据type而定        |

### 2.3 消息确认

为确保消息可靠传递，某些重要消息需要确认接收：

**确认消息格式:**

```json
{
  "type": "ack",
  "id": "original_message_id",
  "timestamp": 1635123456789,
  "status": "success"
}
```

## 3. 客户端事件

客户端向服务器发送的事件类型：

### 3.1 用户管理

#### 3.1.1 用户加入游戏

```json
{
  "type": "user:join",
  "id": "msg-123",
  "timestamp": 1635123456789,
  "data": {
    "displayName": "玩家小明",
    "avatar": "https://example.com/avatar.jpg"
  }
}
```

#### 3.1.2 用户离开游戏

```json
{
  "type": "user:leave",
  "id": "msg-124",
  "timestamp": 1635123456789,
  "data": {
    "reason": "user_initiated"
  }
}
```

### 3.2 位置更新

#### 3.2.1 更新位置

```json
{
  "type": "location:update",
  "id": "msg-125",
  "timestamp": 1635123456789,
  "data": {
    "latitude": 39.12345,
    "longitude": 116.54321,
    "accuracy": 5.2,
    "heading": 45.0,
    "speed": 1.2,
    "altitude": 50.0,
    "altitudeAccuracy": 3.0
  }
}
```

### 3.3 团队管理

#### 3.3.1 创建团队

```json
{
  "type": "team:create",
  "id": "msg-126",
  "timestamp": 1635123456789,
  "data": {
    "name": "冒险小分队",
    "avatar": "https://example.com/team.jpg",
    "isPrivate": false,
    "maxMembers": 5
  }
}
```

#### 3.3.2 加入团队

```json
{
  "type": "team:join",
  "id": "msg-127",
  "timestamp": 1635123456789,
  "data": {
    "teamId": "team-123",
    "joinCode": "XYZABC",
    "role": "member"
  }
}
```

#### 3.3.3 离开团队

```json
{
  "type": "team:leave",
  "id": "msg-128",
  "timestamp": 1635123456789,
  "data": {
    "teamId": "team-123"
  }
}
```

### 3.4 游戏交互

#### 3.4.1 发现宝藏

```json
{
  "type": "treasure:discover",
  "id": "msg-129",
  "timestamp": 1635123456789,
  "data": {
    "treasureId": "treasure-123",
    "location": {
      "latitude": 39.12345,
      "longitude": 116.54321
    }
  }
}
```

#### 3.4.2 收集资源

```json
{
  "type": "resource:collect",
  "id": "msg-130",
  "timestamp": 1635123456789,
  "data": {
    "resourceId": "resource-456",
    "location": {
      "latitude": 39.12345,
      "longitude": 116.54321
    }
  }
}
```

#### 3.4.3 与NPC交互

```json
{
  "type": "npc:interact",
  "id": "msg-131",
  "timestamp": 1635123456789,
  "data": {
    "npcId": "laoke-001",
    "action": "talk",
    "message": "你好，老克！",
    "location": {
      "latitude": 39.12345,
      "longitude": 116.54321
    }
  }
}
```

#### 3.4.4 扫描AR环境

```json
{
  "type": "ar:scan",
  "id": "msg-132",
  "timestamp": 1635123456789,
  "data": {
    "imageData": "base64_encoded_image",
    "scanType": "environment",
    "location": {
      "latitude": 39.12345,
      "longitude": 116.54321
    }
  }
}
```

#### 3.4.5 AR留言

```json
{
  "type": "ar:message",
  "id": "msg-133",
  "timestamp": 1635123456789,
  "data": {
    "content": "这里有隐藏路径！",
    "location": {
      "latitude": 39.12345,
      "longitude": 116.54321
    },
    "visibility": "team_only", // team_only, public, friends
    "expiresIn": 3600 // 秒，0表示永久
  }
}
```

#### 3.4.6 解决冲突

```json
{
  "type": "conflict:response",
  "id": "msg-134",
  "timestamp": 1635123456789,
  "data": {
    "conflictId": "conflict-123",
    "action": "accept", // accept, decline, propose_alternative
    "alternativeProposal": {
      "type": "SPLIT_RESOURCES"
    }
  }
}
```

### 3.5 迷宫状态

#### 3.5.1 请求迷宫状态

```json
{
  "type": "maze:status",
  "id": "msg-135",
  "timestamp": 1635123456789,
  "data": {
    "mazeId": "maze-123"
  }
}
```

#### 3.5.2 请求团队状态

```json
{
  "type": "team:status",
  "id": "msg-136",
  "timestamp": 1635123456789,
  "data": {
    "teamId": "team-123"
  }
}
```

### 3.6 心跳机制

#### 3.6.1 心跳ping

```json
{
  "type": "ping",
  "id": "msg-137",
  "timestamp": 1635123456789,
  "data": {}
}
```

## 4. 服务器事件

服务器向客户端发送的事件类型：

### 4.1 系统事件

#### 4.1.1 欢迎消息

```json
{
  "type": "welcome",
  "id": "srv-123",
  "timestamp": 1635123456789,
  "data": {
    "userId": "user-123",
    "serverTime": 1635123456789,
    "sessionId": "session-456",
    "features": ["ar", "teams", "weather"]
  }
}
```

#### 4.1.2 系统通知

```json
{
  "type": "system:notification",
  "id": "srv-124",
  "timestamp": 1635123456789,
  "data": {
    "level": "info", // info, warning, error
    "message": "系统将在30分钟后进行维护",
    "code": "MAINTENANCE_SCHEDULED"
  }
}
```

### 4.2 用户和团队事件

#### 4.2.1 用户状态更新

```json
{
  "type": "user:status",
  "id": "srv-125",
  "timestamp": 1635123456789,
  "data": {
    "userId": "user-123",
    "status": "online", // online, offline, away, busy
    "lastActivity": 1635123456789
  }
}
```

#### 4.2.2 团队成员更新

```json
{
  "type": "team:members",
  "id": "srv-126",
  "timestamp": 1635123456789,
  "data": {
    "teamId": "team-123",
    "members": [
      {
        "userId": "user-123",
        "displayName": "玩家小明",
        "role": "leader",
        "status": "online",
        "location": {
          "latitude": 39.12345,
          "longitude": 116.54321
        },
        "lastActivity": 1635123456789
      },
      // ...其他成员
    ]
  }
}
```

#### 4.2.3 团队消息

```json
{
  "type": "team:message",
  "id": "srv-127",
  "timestamp": 1635123456789,
  "data": {
    "teamId": "team-123",
    "senderId": "user-456",
    "senderName": "玩家小红",
    "content": "大家往东北方向走，那里有宝藏！",
    "messageType": "text" // text, image, voice, system
  }
}
```

### 4.3 游戏事件

#### 4.3.1 宝藏发现通知

```json
{
  "type": "treasure:discovered",
  "id": "srv-128",
  "timestamp": 1635123456789,
  "data": {
    "treasureId": "treasure-123",
    "discoveredBy": {
      "userId": "user-123",
      "displayName": "玩家小明",
      "teamId": "team-123"
    },
    "treasureType": "knowledge_scroll",
    "rewards": {
      "points": 100,
      "items": ["compass", "map_fragment"]
    }
  }
}
```

#### 4.3.2 迷宫状态更新

```json
{
  "type": "maze:update",
  "id": "srv-129",
  "timestamp": 1635123456789,
  "data": {
    "mazeId": "maze-123",
    "status": "active",
    "weatherConditions": {
      "temperature": 25.5,
      "precipitation": 0,
      "windSpeed": 3.2,
      "humidity": 65
    },
    "dayTime": "day", // day, dusk, night, dawn
    "activeEvents": [
      {
        "eventId": "event-789",
        "type": "corn_growth",
        "affectedAreas": [
          {
            "center": {
              "latitude": 39.12345,
              "longitude": 116.54321
            },
            "radius": 50 // 米
          }
        ],
        "startTime": 1635123456789,
        "endTime": 1635123556789,
        "intensity": 0.8
      }
    ]
  }
}
```

#### 4.3.3 NPC响应

```json
{
  "type": "npc:response",
  "id": "srv-130",
  "timestamp": 1635123456789,
  "data": {
    "npcId": "laoke-001",
    "message": "你好，年轻的探险者！你需要寻找三片金色玉米叶才能打开宝箱。",
    "emotion": "friendly",
    "actions": [
      {
        "id": "ask_more",
        "label": "告诉我更多关于金色玉米叶的信息"
      },
      {
        "id": "accept_quest",
        "label": "接受任务"
      },
      {
        "id": "decline",
        "label": "稍后再说"
      }
    ]
  }
}
```

#### 4.3.4 AR检测结果

```json
{
  "type": "ar:detection",
  "id": "srv-131",
  "timestamp": 1635123456789,
  "data": {
    "scanId": "scan-123",
    "detectedObjects": [
      {
        "type": "corn",
        "confidence": 0.95,
        "boundingBox": {
          "x": 150,
          "y": 200,
          "width": 100,
          "height": 300
        },
        "metadata": {
          "growthStage": "FLOWERING",
          "health": 0.9
        }
      },
      // ...其他检测到的对象
    ],
    "arElements": [
      {
        "id": "ar-elem-123",
        "type": "treasure_marker",
        "position": {
          "latitude": 39.12345,
          "longitude": 116.54321
        },
        "visibleDistance": 50, // 米
        "content": {
          "title": "隐藏宝藏",
          "image": "https://example.com/treasure-marker.jpg"
        }
      }
    ]
  }
}
```

#### 4.3.5 冲突通知

```json
{
  "type": "conflict:notification",
  "id": "srv-132",
  "timestamp": 1635123456789,
  "data": {
    "conflictId": "conflict-123",
    "conflictType": "TREASURE_CONFLICT",
    "teams": [
      {
        "teamId": "team-123",
        "name": "冒险小分队"
      },
      {
        "teamId": "team-456",
        "name": "探索者联盟"
      }
    ],
    "target": {
      "id": "treasure-789",
      "type": "rare_treasure",
      "position": {
        "latitude": 39.12345,
        "longitude": 116.54321
      }
    },
    "resolutionOptions": [
      {
        "type": "MINI_GAME",
        "description": "参与小游戏来争夺宝藏"
      },
      {
        "type": "SPLIT_RESOURCES",
        "description": "平分宝藏"
      }
    ],
    "expiresIn": 60 // 秒
  }
}
```

#### 4.3.6 小游戏邀请

```json
{
  "type": "minigame:invitation",
  "id": "srv-133",
  "timestamp": 1635123456789,
  "data": {
    "gameSessionId": "game-123",
    "conflictId": "conflict-123",
    "gameType": "quiz",
    "description": "知识问答游戏，赢得宝藏！",
    "expiresIn": 60, // 秒
    "instructions": "准备好后点击接受，游戏将在所有团队准备就绪后开始。"
  }
}
```

### 4.4 状态响应

#### 4.4.1 迷宫状态响应

```json
{
  "type": "maze:status:response",
  "id": "srv-134",
  "timestamp": 1635123456789,
  "data": {
    "mazeId": "maze-123",
    "status": "active",
    "startTime": 1635123056789,
    "endTime": 1635223056789,
    "difficulty": "medium",
    "size": {
      "width": 500, // 米
      "height": 500 // 米
    },
    "treasureCount": {
      "total": 50,
      "discovered": 15
    },
    "weatherEnabled": true,
    "currentWeather": {
      "temperature": 25.5,
      "precipitation": 0,
      "windSpeed": 3.2,
      "humidity": 65
    }
  }
}
```

#### 4.4.2 团队状态响应

```json
{
  "type": "team:status:response",
  "id": "srv-135",
  "timestamp": 1635123456789,
  "data": {
    "teamId": "team-123",
    "name": "冒险小分队",
    "members": [
      // 成员列表，同team:members事件
    ],
    "createdAt": 1635122056789,
    "leader": "user-123",
    "statistics": {
      "treasuresFound": 5,
      "resourcesCollected": 12,
      "distanceTraveled": 1250, // 米
      "questsCompleted": 3
    },
    "inventory": [
      {
        "id": "item-123",
        "type": "map_fragment",
        "quantity": 2
      },
      // ...其他物品
    ],
    "activeQuests": [
      {
        "id": "quest-123",
        "title": "寻找金色玉米叶",
        "progress": 1,
        "total": 3,
        "expiresAt": 1635223056789
      }
    ]
  }
}
```

### 4.5 心跳机制

#### 4.5.1 心跳pong

```json
{
  "type": "pong",
  "id": "srv-136",
  "timestamp": 1635123456789,
  "data": {
    "serverTime": 1635123456789
  }
}
```

## 5. 错误处理

### 5.1 错误响应格式

```json
{
  "type": "error",
  "id": "err-123",
  "timestamp": 1635123456789,
  "data": {
    "code": "ERROR_CODE",
    "message": "错误描述信息",
    "originalMessageId": "msg-123",
    "details": {
      // 错误的具体详情，可选
    }
  }
}
```

### 5.2 错误代码列表

| 错误代码                  | 描述                               |
|---------------------------|----------------------------------|
| AUTHENTICATION_FAILED     | 认证失败                          |
| AUTHORIZATION_FAILED      | 授权失败，权限不足                 |
| INVALID_MESSAGE_FORMAT    | 消息格式无效                      |
| INVALID_EVENT_TYPE        | 事件类型无效                      |
| MISSING_REQUIRED_FIELDS   | 缺少必需字段                      |
| RATE_LIMIT_EXCEEDED       | 超出速率限制                      |
| RESOURCE_NOT_FOUND        | 资源未找到                        |
| TEAM_FULL                 | 团队已满，无法加入                |
| INVALID_JOIN_CODE         | 团队加入代码无效                  |
| LOCATION_OUT_OF_BOUNDS    | 位置超出边界                      |
| INTERNAL_SERVER_ERROR     | 服务器内部错误                    |
| SERVICE_UNAVAILABLE       | 服务暂时不可用                    |
| CONFLICT_RESOLUTION_FAILED| 冲突解决失败                      |

## 6. 心跳机制

为确保连接的活跃性，客户端应定期发送心跳消息：

1. 客户端每30秒发送一次`ping`消息
2. 服务器收到`ping`后回复`pong`消息
3. 如果客户端90秒内未收到任何消息，应尝试重新连接
4. 如果服务器60秒内未收到客户端消息，可能会关闭连接

## 7. 安全与性能考量

### 7.1 消息限流

为防止滥用，服务器对消息频率进行限制：

- 位置更新：每秒最多1次
- 一般消息：每10秒最多10条
- 团队创建：每小时最多5次

### 7.2 数据压缩

对于大型消息（如AR扫描数据），建议使用以下压缩策略：

1. 图像数据使用适当压缩比的JPEG格式
2. Base64编码前先压缩二进制数据
3. 考虑使用WebSocket压缩扩展

### 7.3 安全建议

1. 所有WebSocket连接必须通过HTTPS/WSS
2. JWT令牌不应永久有效，建议最长有效期为24小时
3. 敏感操作需要额外验证
4. 客户端应实现指数退避重连策略

## 8. 版本控制

### 8.1 协议版本

当前协议版本：`1.0.0`

版本格式：`主版本.次版本.补丁版本`

- 主版本：不兼容的API更改
- 次版本：向后兼容的功能添加
- 补丁版本：向后兼容的问题修复

### 8.2 版本协商

在连接建立时服务器会通过`welcome`事件返回当前支持的协议版本。客户端可以在连接时通过URL参数`version`指定希望使用的版本：

```
ws://BASE_URL/corn-maze/realtime?token={jwt_token}&version=1.0.0
```

如果服务器不支持请求的版本，将返回HTTP 426 Upgrade Required响应，并在headers中指定支持的版本范围。