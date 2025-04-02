# 数据库设计与使用文档

## 概述

小艾智能体微服务使用MongoDB作为主要持久化存储，Redis作为缓存和会话管理系统。本文档详细描述了数据库架构、配置和使用方法。

## MongoDB 配置

### 连接设置

MongoDB连接通过环境变量配置：

```
MONGODB_URI=mongodb://localhost:27017/xiaoai-service
```

生产环境建议使用密码认证和TLS加密：

```
MONGODB_URI=mongodb://username:password@mongodb.example.com:27017/xiaoai-service?authSource=admin&ssl=true
```

### 数据模型

#### 用户模型 (User)

```typescript
// src/models/User.ts
interface IUser extends Document {
  userId: string;                  // 用户唯一标识
  username: string;                // 用户名
  avatarUrl?: string;              // 头像URL
  region?: string;                 // 地区
  email?: string;                  // 电子邮件
  phoneNumber?: string;            // 电话号码
  accessibilityPreferences: {      // 无障碍偏好
    needsVoiceGuidance: boolean;   // 需要语音引导
    needsSimplifiedContent: boolean; // 需要简化内容
    needsHighContrast: boolean;    // 需要高对比度
    needsScreenReader: boolean;    // 需要屏幕阅读器
    hasVisualImpairment: boolean;  // 视力障碍
    hasHearingImpairment: boolean; // 听力障碍
    hasCognitiveImpairment: boolean; // 认知障碍
    hasMotorImpairment: boolean;   // 行动障碍
    guidanceSpeed: 'slow' | 'normal' | 'fast'; // 引导速度
    voiceGuidanceVolume: number;   // 语音引导音量
    textSize: 'small' | 'medium' | 'large' | 'x-large'; // 文本大小
  };
  dialectPreferences: {            // 方言偏好
    primary: string;               // 主要方言
    secondary?: string;            // 次要方言
    autoDetect: boolean;           // 自动检测方言
  };
  medicalProfile?: {               // 医疗档案
    bodyType?: string;             // 体质类型
    allergies?: string[];          // 过敏物
    medicalConditions?: string[];  // 医疗状况
    medications?: string[];        // 药物治疗
  };
  lastLogin?: Date;                // 最后登录时间
  createdAt: Date;                 // 创建时间
  updatedAt: Date;                 // 更新时间
}
```

#### 会话模型 (Conversation)

```typescript
// src/models/Conversation.ts
interface IConversation extends Document {
  conversationId: string;          // 会话唯一标识
  userId: string;                  // 用户标识
  title: string;                   // 会话标题
  messages: {                      // 消息列表
    messageId: string;             // 消息标识
    role: 'user' | 'assistant';    // 角色
    content: string;               // 内容
    contentType: 'text' | 'voice' | 'image'; // 内容类型
    mediaUrl?: string;             // 媒体URL
    timestamp: Date;               // 时间戳
  }[];
  summary?: string;                // 会话摘要
  tags?: string[];                 // 标签
  unread: boolean;                 // 未读状态
  lastReadAt?: Date;               // 最后阅读时间
  contextData?: Record<string, any>; // 上下文数据
  createdAt: Date;                 // 创建时间
  updatedAt: Date;                 // 更新时间
}
```

#### 智能体模型 (XiaoAiAgent)

```typescript
// src/models/XiaoAiAgent.ts
interface IXiaoAiAgent extends Document {
  agentId: string;                 // 智能体标识
  name: string;                    // 名称
  version: string;                 // 版本
  status: 'active' | 'inactive' | 'training'; // 状态
  capabilities: string[];          // 能力
  config: Record<string, any>;     // 配置
  activityLog: {                   // 活动日志
    action: string;                // 行为
    details: Record<string, any>;  // 细节
    timestamp: Date;               // 时间戳
  }[];
  metrics: {                       // 指标
    conversations: number;         // 会话数
    messagesProcessed: number;     // 处理的消息数
    avgResponseTime: number;       // 平均响应时间
  };
  lastActivity?: Date;             // 最后活动时间
  lastStatusUpdate?: Date;         // 最后状态更新
  lastConfigUpdate?: Date;         // 最后配置更新
  lastCapabilitiesUpdate?: Date;   // 最后能力更新
  createdAt: Date;                 // 创建时间
  updatedAt: Date;                 // 更新时间
}
```

## 存储库模式

服务使用存储库模式(Repository Pattern)封装数据访问逻辑：

### 基础存储库 (BaseRepository)

```typescript
// src/repositories/BaseRepository.ts
interface IBaseRepository<T extends Document> {
  findById(id: string): Promise<T | null>;
  findOne(filter: FilterQuery<T>): Promise<T | null>;
  find(filter: FilterQuery<T>, options?: QueryOptions): Promise<T[]>;
  create(data: Partial<T>): Promise<T>;
  updateById(id: string, update: UpdateQuery<T>): Promise<T | null>;
  updateOne(filter: FilterQuery<T>, update: UpdateQuery<T>): Promise<T | null>;
  updateMany(filter: FilterQuery<T>, update: UpdateQuery<T>): Promise<number>;
  deleteById(id: string): Promise<boolean>;
  deleteOne(filter: FilterQuery<T>): Promise<boolean>;
  deleteMany(filter: FilterQuery<T>): Promise<number>;
  count(filter: FilterQuery<T>): Promise<number>;
  exists(filter: FilterQuery<T>): Promise<boolean>;
}
```

### 用户存储库 (UserRepository)

```typescript
// src/repositories/UserRepository.ts
interface IUserRepository extends BaseRepository<IUser> {
  findByUserId(userId: string): Promise<IUser | null>;
  findByUsername(username: string): Promise<IUser | null>;
  findByEmail(email: string): Promise<IUser | null>;
  findByPhoneNumber(phoneNumber: string): Promise<IUser | null>;
  findUsersWithAccessibilityNeeds(): Promise<IUser[]>;
  findUsersByDialect(dialect: string): Promise<IUser[]>;
  updateLastLogin(userId: string): Promise<void>;
}
```

### 会话存储库 (ConversationRepository)

```typescript
// src/repositories/ConversationRepository.ts
interface IConversationRepository extends BaseRepository<IConversation> {
  findByConversationId(conversationId: string): Promise<IConversation | null>;
  findByUserId(userId: string, options?: { limit?: number; skip?: number; sort?: string }): Promise<IConversation[]>;
  findRecentConversations(userId: string, limit?: number): Promise<IConversation[]>;
  addMessageToConversation(conversationId: string, message: any): Promise<IConversation | null>;
  markAsRead(conversationId: string): Promise<void>;
  getUnreadCount(userId: string): Promise<number>;
  searchConversationsByContent(userId: string, searchTerm: string): Promise<IConversation[]>;
}
```

### 智能体存储库 (XiaoAiAgentRepository)

```typescript
// src/repositories/XiaoAiAgentRepository.ts
interface IXiaoAiAgentRepository extends BaseRepository<IXiaoAiAgent> {
  findByAgentId(agentId: string): Promise<IXiaoAiAgent | null>;
  findByName(name: string): Promise<IXiaoAiAgent | null>;
  updateStatus(agentId: string, status: string): Promise<IXiaoAiAgent | null>;
  updateConfig(agentId: string, config: any): Promise<IXiaoAiAgent | null>;
  updateCapabilities(agentId: string, capabilities: string[]): Promise<IXiaoAiAgent | null>;
  logActivity(agentId: string, activity: any): Promise<IXiaoAiAgent | null>;
  getActiveAgents(): Promise<IXiaoAiAgent[]>;
  getAgentsByCapability(capability: string): Promise<IXiaoAiAgent[]>;
}
```

## Redis缓存服务

### 配置

Redis连接通过环境变量配置：

```
REDIS_URL=redis://localhost:6379
REDIS_PREFIX=xiaoai:
```

生产环境建议使用密码认证和TLS加密：

```
REDIS_URL=rediss://username:password@redis.example.com:6379
```

### 缓存服务接口

```typescript
// src/services/CacheService.ts
interface ICacheService {
  connect(): Promise<void>;                                              // 连接Redis
  disconnect(): Promise<void>;                                           // 断开连接
  set(key: string, value: any, expireSeconds?: number): Promise<void>;   // 设置值
  get<T>(key: string): Promise<T | null>;                                // 获取值
  del(key: string): Promise<void>;                                       // 删除值
  exists(key: string): Promise<boolean>;                                 // 检查存在
  expire(key: string, seconds: number): Promise<void>;                   // 设置过期时间
  ttl(key: string): Promise<number>;                                     // 获取剩余时间
  incr(key: string): Promise<number>;                                    // 增加值
  hset(key: string, field: string, value: any): Promise<void>;           // 哈希表设置
  hget<T>(key: string, field: string): Promise<T | null>;                // 哈希表获取
  hgetall<T>(key: string): Promise<Record<string, T> | null>;            // 获取全部哈希表
  hdel(key: string, field: string): Promise<void>;                       // 删除哈希表字段
  flush(): Promise<void>;                                                // 清空缓存
}
```

## 缓存策略

### 会话缓存

活跃的用户会话数据使用Redis缓存，减少对MongoDB的查询压力。

缓存键格式：
- 用户数据: `xiaoai:user:{userId}`
- 会话数据: `xiaoai:conversation:{conversationId}`
- 会话列表: `xiaoai:user:{userId}:conversations`

默认过期时间：
- 用户数据: 1小时
- 会话数据: 30分钟
- 会话列表: 15分钟

### 查询缓存

频繁查询的数据会被缓存，包括：
- 智能体配置: `xiaoai:agent:{agentId}:config`
- 无障碍设置: `xiaoai:accessibility:{userId}`
- 方言偏好: `xiaoai:dialect:{userId}`

## 索引策略

为提高查询性能，MongoDB集合已设置以下索引：

### 用户集合索引
- `userId`: 1（唯一索引）
- `accessibilityPreferences.needsVoiceGuidance`: 1
- `dialectPreferences.primary`: 1
- `lastLogin`: -1

### 会话集合索引
- `conversationId`: 1（唯一索引）
- `userId`: 1
- `updatedAt`: -1
- `unread`: 1
- 全文索引: `title`, `messages.content`

### 智能体集合索引
- `agentId`: 1（唯一索引）
- `status`: 1
- `capabilities`: 1
- `lastActivity`: -1

## 数据备份

建议的备份策略：
1. 每日完整备份MongoDB数据库
2. 每小时增量备份
3. Redis持久化开启AOF模式
4. Redis快照配置为每15分钟或10000次写入

## 数据迁移

使用内置的迁移脚本管理数据结构变更：

```bash
# 运行迁移
npm run migrate

# 回滚上一次迁移
npm run migrate:rollback
``` 