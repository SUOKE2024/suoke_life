# 语音引导模块 - 技术文档

本文档详细介绍了老克服务(Laoke Service)中的语音引导模块的功能、架构和API使用方法。该模块提供了语音命令处理、上下文感知引导、语音交互以及用户偏好设置等功能。

## 1. 功能概述

语音引导模块提供以下核心功能：

- **语音命令系统**：支持基于场景和上下文的语音命令识别和执行
- **情境引导内容**：提供基于用户当前状态、场景和事件的上下文感知引导
- **语音会话管理**：支持长期对话会话的创建、更新和终止
- **语音交互处理**：支持语音和文本输入的处理和响应生成
- **语音偏好设置**：支持个性化的语音偏好配置
- **方言支持**：与方言模块集成，支持方言识别和处理

## 2. 技术架构

语音引导模块采用分层架构设计，包含以下组件：

### 2.1 数据模型层

- `VoiceCommand`: 语音命令模型，定义命令触发词、执行动作和参数
- `GuidanceContent`: 引导内容模型，定义情境化的引导内容和触发条件
- `VoiceSession`: 会话模型，管理用户的语音交互会话
- `VoiceInteraction`: 交互记录模型，记录用户的每次语音或文本交互
- `VoicePreference`: 用户偏好模型，存储用户的语音交互偏好设置

### 2.2 服务层

- 语音命令服务：提供命令管理、匹配和执行功能
- 引导内容服务：提供情境化引导内容的管理和检索
- 会话管理服务：管理语音会话的生命周期和上下文
- 语音处理服务：处理语音和文本输入，生成适当响应

### 2.3 控制器层

提供RESTful API接口，处理HTTP请求和响应

### 2.4 外部集成

- AI服务集成：语音识别、命令匹配、文本生成等
- 方言服务集成：方言识别和转换
- 存储服务：音频文件存储和管理

## 3. API参考

### 3.1 语音命令相关API

#### 获取所有语音命令

```
GET /api/v1/voice-guidance/commands
```

查询参数：
- `limit`: 返回结果数量限制 (默认: 100)
- `skip`: 跳过结果数量 (默认: 0)
- `isEnabled`: 是否只返回启用的命令 (true/false)
- `sceneType`: 场景类型筛选

响应示例：
```json
{
  "success": true,
  "data": {
    "total": 10,
    "commands": [
      {
        "_id": "60f5a7b8e85d4a0018c9f5a2",
        "trigger": "打开主页",
        "aliases": ["前往主页", "回到首页"],
        "action": "navigate",
        "requiredParams": [],
        "optionalParams": [],
        "sceneType": "HOME",
        "priority": 5,
        "isEnabled": true,
        "examples": ["请打开主页", "回到首页"],
        "createdAt": "2023-07-18T09:20:56.123Z",
        "updatedAt": "2023-07-18T09:20:56.123Z"
      }
    ]
  }
}
```

#### 获取特定场景的语音命令

```
GET /api/v1/voice-guidance/commands/scene/:scene
```

路径参数：
- `scene`: 场景类型 (HOME, MAP, HEALTH 等)

响应格式与"获取所有语音命令"相同。

#### 创建语音命令

```
POST /api/v1/voice-guidance/commands
```

请求体：
```json
{
  "trigger": "打开健康报告",
  "aliases": ["查看健康报告", "显示我的健康数据"],
  "action": "openHealthReport",
  "requiredParams": [],
  "optionalParams": ["timeRange"],
  "sceneType": "HEALTH",
  "priority": 3,
  "isEnabled": true,
  "examples": ["打开我的健康报告", "查看我的健康数据"]
}
```

#### 更新语音命令

```
PUT /api/v1/voice-guidance/commands/:id
```

路径参数：
- `id`: 语音命令ID

请求体格式与"创建语音命令"相同。

#### 删除语音命令

```
DELETE /api/v1/voice-guidance/commands/:id
```

路径参数：
- `id`: 语音命令ID

#### 匹配语音命令

```
POST /api/v1/voice-guidance/commands/match
```

请求体：
```json
{
  "input": "打开健康报告",
  "sceneType": "HEALTH"
}
```

响应示例：
```json
{
  "success": true,
  "data": {
    "command": {
      "_id": "60f5a7b8e85d4a0018c9f5a3",
      "trigger": "打开健康报告",
      "action": "openHealthReport",
      "sceneType": "HEALTH"
    },
    "confidence": 0.95,
    "extractedParams": {}
  }
}
```

### 3.2 语音引导内容相关API

#### 获取语音引导内容

```
GET /api/v1/voice-guidance/contents
```

查询参数：
- `limit`: 返回结果数量限制 (默认: 50)
- `skip`: 跳过结果数量 (默认: 0)
- `isEnabled`: 是否只返回启用的内容 (true/false)
- `sceneType`: 场景类型筛选
- `guidanceType`: 引导类型筛选

响应示例：
```json
{
  "success": true,
  "data": {
    "total": 5,
    "contents": [
      {
        "_id": "60f5a7b8e85d4a0018c9f5b0",
        "title": "健康数据导览",
        "content": "这是您的健康数据总览，向左滑动可以查看更多详细信息。",
        "guidanceType": "TUTORIAL",
        "sceneType": "HEALTH",
        "priority": 5,
        "isEnabled": true,
        "contextualTriggers": [
          {
            "event": "healthDataOpened",
            "conditions": "firstTimeUser === true"
          }
        ],
        "audioUrl": "/api/v1/voice-guidance/audio/guidance_60f5a7b8e85d4a0018c9f5b0_standard_1627291256789.mp3",
        "createdAt": "2023-07-18T09:25:56.123Z",
        "updatedAt": "2023-07-18T09:25:56.123Z"
      }
    ]
  }
}
```

#### 根据场景和事件获取匹配的引导内容

```
GET /api/v1/voice-guidance/contents/:sceneType/:event
```

路径参数：
- `sceneType`: 场景类型
- `event`: 事件名称

请求体（可选）：
```json
{
  "context": {
    "firstTimeUser": true,
    "completedTutorial": false
  }
}
```

响应格式与"获取语音引导内容"类似。

#### 创建语音引导内容

```
POST /api/v1/voice-guidance/contents
```

请求体：
```json
{
  "title": "健康数据导览",
  "content": "这是您的健康数据总览，向左滑动可以查看更多详细信息。",
  "guidanceType": "TUTORIAL",
  "sceneType": "HEALTH",
  "priority": 5,
  "isEnabled": true,
  "contextualTriggers": [
    {
      "event": "healthDataOpened",
      "conditions": "firstTimeUser === true"
    }
  ],
  "dialects": [
    {
      "dialectCode": "zh-wu",
      "content": "这个是侬的健康数据总览，向左滑动可以查看更多详细信息。"
    }
  ]
}
```

#### 更新语音引导内容

```
PUT /api/v1/voice-guidance/contents/:id
```

路径参数：
- `id`: 引导内容ID

请求体格式与"创建语音引导内容"相同。

#### 删除语音引导内容

```
DELETE /api/v1/voice-guidance/contents/:id
```

路径参数：
- `id`: 引导内容ID

#### 生成引导音频

```
POST /api/v1/voice-guidance/contents/:guidanceId/audio
```

路径参数：
- `guidanceId`: 引导内容ID

查询参数：
- `dialectCode`: 方言代码 (可选)

响应示例：
```json
{
  "success": true,
  "data": {
    "audioUrl": "/api/v1/voice-guidance/audio/guidance_60f5a7b8e85d4a0018c9f5b0_standard_1627291256789.mp3"
  }
}
```

#### 获取音频文件

```
GET /api/v1/voice-guidance/audio/:fileName
```

路径参数：
- `fileName`: 音频文件名

响应: 音频文件流 (Content-Type: audio/mpeg)

### 3.3 语音会话相关API

#### 创建语音会话

```
POST /api/v1/voice-guidance/sessions
```

请求体：
```json
{
  "userId": "60f5a7b8e85d4a0018c9f5a1",
  "deviceInfo": {
    "deviceId": "D123456789",
    "deviceType": "mobile",
    "platform": "android",
    "osVersion": "12.0",
    "appVersion": "1.0.0"
  },
  "dialectCode": "zh-wu",
  "location": {
    "latitude": 31.2304,
    "longitude": 121.4737,
    "accuracy": 10,
    "address": "上海市黄浦区人民广场"
  }
}
```

响应示例：
```json
{
  "success": true,
  "data": {
    "sessionId": "f5a7b8e85d4a0018c9f5a2-1627291256789",
    "startTime": "2023-07-18T09:30:56.123Z"
  }
}
```

#### 结束语音会话

```
POST /api/v1/voice-guidance/sessions/:sessionId/end
```

路径参数：
- `sessionId`: 会话ID

响应示例：
```json
{
  "success": true,
  "data": {
    "sessionId": "f5a7b8e85d4a0018c9f5a2-1627291256789",
    "startTime": "2023-07-18T09:30:56.123Z",
    "endTime": "2023-07-18T09:45:23.456Z",
    "duration": 870
  }
}
```

#### 更新会话上下文

```
PUT /api/v1/voice-guidance/sessions/:sessionId/context
```

路径参数：
- `sessionId`: 会话ID

请求体：
```json
{
  "currentScreen": "healthReport",
  "lastAction": "viewBloodPressure",
  "userPreference": "detailed"
}
```

响应示例：
```json
{
  "success": true,
  "data": {
    "sessionId": "f5a7b8e85d4a0018c9f5a2-1627291256789",
    "context": {
      "currentScreen": "healthReport",
      "lastAction": "viewBloodPressure",
      "userPreference": "detailed"
    }
  }
}
```

### 3.4 语音交互处理API

#### 处理语音输入

```
POST /api/v1/voice-guidance/process/voice
```

请求体 (multipart/form-data):
- `audio`: 音频文件
- `userId`: 用户ID
- `sessionId`: 会话ID
- `sceneType`: 场景类型
- `dialectCode`: 方言代码 (可选)
- `context`: 上下文JSON字符串 (可选)

响应示例：
```json
{
  "success": true,
  "data": {
    "text": "打开健康报告",
    "command": {
      "_id": "60f5a7b8e85d4a0018c9f5a3",
      "trigger": "打开健康报告",
      "action": "openHealthReport"
    },
    "confidence": 0.92,
    "response": {
      "type": "action",
      "content": "已为您打开健康报告",
      "audioUrl": "/api/v1/voice-guidance/audio/response_1627291356789.mp3",
      "visualElements": {
        "screen": "healthReport"
      }
    }
  }
}
```

#### 处理文本输入

```
POST /api/v1/voice-guidance/process/text
```

请求体：
```json
{
  "text": "打开健康报告",
  "userId": "60f5a7b8e85d4a0018c9f5a1",
  "sessionId": "f5a7b8e85d4a0018c9f5a2-1627291256789",
  "sceneType": "HEALTH",
  "context": {
    "currentScreen": "dashboard"
  }
}
```

响应格式与"处理语音输入"相同，但不包含"text"字段。

### 3.5 用户语音偏好设置API

#### 获取用户语音偏好设置

```
GET /api/v1/voice-guidance/preferences/:userId
```

路径参数：
- `userId`: 用户ID

响应示例：
```json
{
  "success": true,
  "data": {
    "_id": "60f5a7b8e85d4a0018c9f5c1",
    "userId": "60f5a7b8e85d4a0018c9f5a1",
    "voiceEnabled": true,
    "audioFeedbackEnabled": true,
    "hapticFeedbackEnabled": true,
    "voiceSpeed": 1.0,
    "voicePitch": 1.0,
    "voiceVolume": 0.8,
    "dialectCode": "zh-wu",
    "preferredVoiceGender": "female",
    "autoPlayGuidance": true,
    "createdAt": "2023-07-18T09:35:56.123Z",
    "updatedAt": "2023-07-18T09:35:56.123Z"
  }
}
```

#### 更新用户语音偏好设置

```
PUT /api/v1/voice-guidance/preferences/:userId
```

路径参数：
- `userId`: 用户ID

请求体：
```json
{
  "voiceEnabled": true,
  "audioFeedbackEnabled": true,
  "dialectCode": "zh-wu",
  "voiceSpeed": 1.2
}
```

响应格式与"获取用户语音偏好设置"相同。

## 4. 使用示例

### 4.1 集成语音命令功能

以下是在前端应用中集成语音命令功能的简单示例代码：

```typescript
// 创建语音会话
async function createVoiceSession() {
  const userId = await getUserId();
  const deviceInfo = await getDeviceInfo();
  
  const response = await fetch('/api/v1/voice-guidance/sessions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ userId, deviceInfo })
  });
  
  const data = await response.json();
  return data.data.sessionId;
}

// 处理语音输入
async function processVoiceInput(audioBlob, sessionId, sceneType) {
  const userId = await getUserId();
  const formData = new FormData();
  
  formData.append('audio', audioBlob);
  formData.append('userId', userId);
  formData.append('sessionId', sessionId);
  formData.append('sceneType', sceneType);
  formData.append('context', JSON.stringify({
    currentScreen: getCurrentScreen(),
    lastAction: getLastAction()
  }));
  
  const response = await fetch('/api/v1/voice-guidance/process/voice', {
    method: 'POST',
    body: formData
  });
  
  const result = await response.json();
  
  if (result.success) {
    // 处理响应
    handleVoiceResponse(result.data);
  }
}

// 处理语音响应
function handleVoiceResponse(data) {
  // 显示文本响应
  showTextResponse(data.response.content);
  
  // 播放音频响应
  if (data.response.audioUrl) {
    playAudio(data.response.audioUrl);
  }
  
  // 处理视觉元素
  if (data.response.visualElements) {
    updateUI(data.response.visualElements);
  }
  
  // 如果有命令匹配，执行对应动作
  if (data.command) {
    executeCommandAction(data.command.action, data.extractedParams);
  }
}
```

### 4.2 集成情境引导功能

```typescript
// 在特定事件触发时获取情境引导
async function getContextualGuidance(sceneType, event) {
  const context = {
    firstTimeUser: isFirstTimeUser(),
    completedTutorial: hasCompletedTutorial(),
    userPreferences: getUserPreferences()
  };
  
  const response = await fetch(`/api/v1/voice-guidance/contents/${sceneType}/${event}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ context })
  });
  
  const result = await response.json();
  
  if (result.success && result.data.length > 0) {
    // 显示引导内容
    showGuidance(result.data[0]);
  }
}

// 显示引导内容
function showGuidance(guidanceContent) {
  // 显示文本内容
  showGuidanceText(guidanceContent.content);
  
  // 播放音频内容（如果有）
  if (guidanceContent.audioUrl) {
    playAudio(guidanceContent.audioUrl);
  } else {
    // 生成音频内容
    generateAndPlayAudio(guidanceContent._id);
  }
}

// 生成并播放音频
async function generateAndPlayAudio(guidanceId) {
  // 获取用户的方言偏好
  const userPrefs = await getUserVoicePreferences();
  
  // 生成音频
  const response = await fetch(`/api/v1/voice-guidance/contents/${guidanceId}/audio?dialectCode=${userPrefs.dialectCode}`, {
    method: 'POST'
  });
  
  const result = await response.json();
  
  if (result.success) {
    // 播放生成的音频
    playAudio(result.data.audioUrl);
  }
}
```

## 5. 配置指南

### 5.1 环境变量配置

语音引导模块使用以下环境变量进行配置：

```
# AI服务配置
AI_SERVICES_API_KEY=your_api_key_here
AI_SERVICES_COMMAND_MATCHING=http://ai-service.example.com/command-matching
AI_SERVICES_COMMAND_EXECUTION=http://ai-service.example.com/command-execution
AI_SERVICES_CONTEXT_EVALUATION=http://ai-service.example.com/context-evaluation
AI_SERVICES_CONVERSATIONAL_AI=http://ai-service.example.com/conversational-ai
AI_SERVICES_TEXT_TO_SPEECH=http://ai-service.example.com/text-to-speech
AI_SERVICES_SPEECH_RECOGNITION=http://ai-service.example.com/speech-recognition

# 存储配置
AUDIO_FILES_PATH=/path/to/audio/files
TEMP_FILES_PATH=/path/to/temp/files

# 性能配置
MAX_AUDIO_FILE_SIZE=10485760  # 10MB
COMMAND_MATCH_THRESHOLD=0.6
```

### 5.2 安全性考虑

- 所有涉及语音命令创建和管理的接口都需要管理员权限
- 用户个人数据（如偏好设置、会话信息）只允许用户本人访问
- 音频文件应使用临时URL或令牌保护
- 考虑对语音命令执行添加确认机制，防止误操作
- 实现速率限制，防止API滥用

## 6. 性能优化建议

- 使用CDN分发音频文件
- 实现音频文件缓存机制
- 对频繁访问的语音命令和引导内容使用内存缓存
- 对长会话历史记录进行分页或归档
- 实现批量操作API减少网络请求
- 使用WebSocket或SSE实现实时交互更新

## 7. 故障排除

### 7.1 常见问题

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| 语音识别准确率低 | 环境噪音、方言不匹配 | 调整降噪参数、确保正确的方言设置 |
| 命令匹配失败 | 触发词不匹配、场景类型错误 | 检查命令配置、确认正确的场景类型 |
| 音频生成失败 | TTS服务不可用、内容格式问题 | 检查TTS服务状态、验证文本内容 |
| 会话上下文丢失 | 会话超时、ID不匹配 | 延长会话超时时间、检查会话ID |

### 7.2 日志记录

语音引导模块在以下位置记录日志：

- 语音处理日志：`/var/log/laoke-service/voice-guidance.log`
- 错误日志：`/var/log/laoke-service/error.log`
- 会话日志：`/var/log/laoke-service/sessions.log`

### 7.3 监控指标

重要监控指标包括：

- 命令匹配成功率
- 语音识别准确率
- 音频生成时间
- API响应时间
- 语音会话持续时间
- 存储使用量

## 8. 版本历史与规划

### 8.1 当前版本

- 版本: 1.0.0
- 发布日期: 2023-08-01
- 主要特性:
  - 基础语音命令系统
  - 情境引导内容支持
  - 语音和文本处理
  - 方言支持
  - 用户偏好设置

### 8.2 未来规划

- 支持多模态引导（语音+视觉）
- 增强上下文理解能力
- 改进命令参数提取
- 添加语音情感识别
- 集成用户反馈机制
- 支持离线语音命令处理

## 9. 贡献与支持

### 9.1 贡献指南

如要贡献代码，请：

1. Fork项目仓库
2. 创建功能分支
3. 提交更改
4. 提交Pull Request

### 9.2 支持渠道

- 技术支持: support@laoke.service
- 问题跟踪: https://github.com/suoke-life/laoke-service/issues
- 文档网站: https://docs.laoke.service/voice-guidance

---

*本文档最后更新于：2023-08-01* 