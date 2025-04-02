# 小艾智能体代理微服务 [完成度: 100%]

## 简介

小艾（XiaoAi）是索克生活APP首页（聊天频道）版主，负责统筹协调望诊、闻诊、问诊、切诊服务，为用户提供无障碍功能服务，对特殊需求用户提供语音引导（包括导盲）服务。

## 主要功能

- **四诊协调**: 统筹协调望诊、闻诊、问诊、切诊服务，提供完整的中医四诊体验
- **无障碍服务**: 为特殊需求用户提供无障碍功能
- **语音引导**: 为视障用户提供语音引导，包括导盲服务
- **聊天服务**: 作为首页聊天频道的版主，提供智能对话服务
- **数据管理**: 使用MongoDB存储用户、会话和智能体数据，Redis进行缓存和会话管理

## 技术栈

- Node.js
- Express
- TypeScript
- MongoDB
- Socket.io
- OpenAI API
- Redis

## 项目结构

```
xiaoai-service/
├── dist/                  # 编译后的文件
├── docs/                  # 文档
├── k8s/                   # Kubernetes配置
├── logs/                  # 日志文件
├── node_modules/          # 依赖包
├── src/                   # 源代码
│   ├── config/            # 配置文件
│   ├── controllers/       # 控制器
│   ├── core/              # 核心功能
│   ├── di/                # 依赖注入
│   ├── middlewares/       # 中间件
│   ├── models/            # 数据模型
│   ├── repositories/      # 数据仓储
│   ├── routes/            # 路由
│   ├── services/          # 服务
│   ├── utils/             # 工具函数
│   ├── scripts/           # 脚本文件
│   └── index.ts           # 入口文件
├── tests/                 # 测试文件
│   ├── unit/              # 单元测试
│   │   ├── repositories/  # 仓库测试
│   │   ├── services/      # 服务测试
│   │   ├── controllers/   # 控制器测试
│   │   ├── providers/     # 提供者测试
│   │   ├── helpers/       # 测试辅助工具
│   │   └── integration/   # 集成测试
│   └── jest.config.js     # Jest配置
├── .env                   # 环境变量
├── .env.example           # 环境变量示例
├── .gitignore             # Git忽略文件
├── Dockerfile             # Docker配置
├── package.json           # 项目依赖
├── package-lock.json      # 依赖锁定文件
├── README.md              # 项目说明
└── tsconfig.json          # TypeScript配置
```

## 数据库交互

服务使用MongoDB进行持久化数据存储，Redis进行缓存和会话管理。

### 数据模型

- **用户(User)**: 存储用户信息，包括无障碍需求和方言偏好
- **对话(Conversation)**: 存储用户与小艾的对话历史
- **智能体(XiaoAiAgent)**: 存储智能体配置、状态和活动日志

### 存储库模式

服务采用存储库模式(Repository Pattern)进行数据访问：

- **BaseRepository**: 提供通用CRUD操作
- **UserRepository**: 用户数据操作，支持按无障碍需求和方言偏好查询
- **ConversationRepository**: 对话历史管理，支持搜索和分页
- **XiaoAiAgentRepository**: 智能体配置和状态管理

### 缓存服务

Redis缓存服务提供：

- 会话数据缓存
- 频繁访问数据的缓存
- 分布式锁
- 速率限制

### 配置示例

MongoDB配置(在`.env`文件中):

```
MONGODB_URI=mongodb://localhost:27017/xiaoai-service
```

Redis配置(在`.env`文件中):

```
REDIS_URL=redis://localhost:6379
```

## 快速开始

### 安装依赖

```bash
npm install
```

### 配置环境变量

复制 `.env.example` 文件并重命名为 `.env`，然后根据需要修改配置。

```bash
cp .env.example .env
```

### 编译代码

```bash
npm run build
```

### 启动服务

```bash
npm run start
```

### 开发模式

```bash
npm run dev
```

### 初始化数据库

```bash
npm run init-db
```

## API参考

### 聊天接口

#### 发送文本消息

```
POST /api/messages/text
```

请求体:

```json
{
  "userId": "user123",
  "message": "我想了解中医四诊"
}
```

#### 发送语音消息

```
POST /api/messages/voice
```

请求体:

```json
{
  "userId": "user123",
  "audioBase64": "base64编码的音频数据",
  "transcription": "可选的语音转写文本"
}
```

### 无障碍接口

#### 获取用户无障碍配置

```
GET /api/accessibility/profile/:userId
```

#### 更新用户无障碍配置

```
PUT /api/accessibility/profile/:userId
```

请求体:

```json
{
  "accessibilityNeeds": {
    "visuallyImpaired": true,
    "needsVoiceGuidance": true,
    "preferredVoiceSpeed": 1.2
  }
}
```

#### 生成语音引导

```
POST /api/accessibility/voice-guidance
```

请求体:

```json
{
  "text": "将要转化为语音的文本内容",
  "speed": 1.0,
  "language": "zh-CN"
}
```

### 诊断接口

#### 启动诊断流程

```
POST /api/diagnosis/initiate
```

请求体:

```json
{
  "userId": "user123",
  "diagnosticServices": ["looking", "inquiry", "smell", "touch"]
}
```

#### 获取可用诊断服务

```
GET /api/diagnosis/services
```

#### 获取用户诊断历史

```
GET /api/diagnosis/history/:userId
```

### 智能体接口

#### 获取智能体状态

```
GET /api/agent/status
```

#### 更新智能体状态

```
PUT /api/agent/status
```

请求体:

```json
{
  "status": "online",
  "state": {
    "mode": "normal"
  }
}
```

## Socket.io 事件

### 客户端发送消息

```javascript
socket.emit('user-message', {
  userId: 'user123',
  message: '我想了解中医四诊',
  messageType: 'text' // 'text', 'voice', 'image'
});
```

### 服务器响应

```javascript
socket.on('agent-response', (response) => {
  console.log(response);
});

socket.on('voice-response', (response) => {
  console.log(response.audioUrl);
});

socket.on('agent-actions', (actions) => {
  console.log(actions);
});
```

### 请求无障碍支持

```javascript
socket.emit('request-accessibility', {
  userId: 'user123',
  requestType: 'voice-guidance',
  context: {
    text: '需要语音引导的文本',
    speed: 1.0,
    language: 'zh-CN'
  }
});
```

## 与其他微服务的交互

### 四诊服务

小艾服务统筹协调四个诊断服务：

1. **望诊服务**: 通过面相、舌象等视觉信息进行诊断
2. **闻诊服务**: 通过气味、声音等信息进行诊断
3. **问诊服务**: 通过询问病史、症状等信息进行诊断
4. **切诊服务**: 通过脉象、触诊等信息进行诊断

### 语音合成服务

小艾服务与TTS服务交互，为视障用户提供语音引导。

## 无障碍功能特性

小艾服务提供多种无障碍功能，包括但不限于：

- 视障用户语音引导（包括导盲服务）
- 听障用户文字增强
- 认知障碍用户内容简化
- 行动不便用户操作辅助

## 部署

### Docker

```bash
docker build -t xiaoai-service .
docker run -p 3010:3010 --env-file .env xiaoai-service
```

### Kubernetes

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

## 贡献指南

1. Fork 仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 开发团队

- 索克生活团队

## 许可证

MIT License

## 小艾智能体服务

### 完成度：100%

小艾智能体代理微服务 - 索克生活APP首页(聊天频道)版主，统筹四诊服务与无障碍功能。

本服务作为索克生活APP的聊天频道核心，提供以下功能：
- 协调四诊（望诊、闻诊、问诊、切诊）服务
- 无障碍功能支持，为特殊需求用户提供服务
- 语音引导服务
- 方言服务
- 图像分析服务

### 项目结构
```
xiaoai-service/
├── src/                      # 源代码
│   ├── controllers/          # 控制器
│   ├── middleware/           # 中间件
│   ├── models/               # 数据模型
│   ├── repositories/         # 数据仓库
│   ├── routes/               # 路由定义
│   ├── services/             # 服务
│   ├── utils/                # 工具函数
│   ├── di/                   # 依赖注入
│   ├── scripts/              # 脚本文件
│   └── index.ts              # 应用入口
├── tests/                    # 测试文件
│   ├── unit/                 # 单元测试
│   │   ├── repositories/     # 仓库测试
│   │   ├── services/         # 服务测试
│   │   ├── controllers/      # 控制器测试
│   │   ├── providers/        # 提供者测试
│   │   ├── helpers/          # 测试辅助工具
│   │   └── integration/      # 集成测试
│   └── jest.config.js        # Jest配置
├── dist/                     # 编译输出
├── scripts/                  # 脚本文件
├── docs/                     # 文档
└── package.json              # 项目配置
```

### 快速开始

#### 安装依赖
```bash
npm install
```

#### 开发模式运行
```bash
npm run dev
```

#### 生产环境构建
```bash
npm run build
```

#### 启动服务
```bash
npm start
```

#### 初始化数据库
```bash
npm run init-db
```

### 测试

本服务有完整的测试套件，包括单元测试和集成测试。

#### 运行测试
```bash
# 运行所有测试
npm test

# 运行测试并查看覆盖率
npm run test:coverage

# 运行仓库测试
npm run test:repositories

# 运行服务测试
npm run test:services

# 运行集成测试
npm run test:integration
```

详细的测试文档可以在 [docs/TESTING.md](docs/TESTING.md) 中找到。

### API文档

API文档通过Swagger提供，服务运行后可访问：
```
http://localhost:3000/api-docs
```

### 配置

服务配置通过环境变量提供，可在 `.env` 文件中设置：

```
# 服务配置
PORT=3000
NODE_ENV=development

# 数据库配置
MONGODB_URI=mongodb://localhost:27017/xiaoai

# Redis配置
REDIS_URL=redis://localhost:6379

# 日志配置
LOG_LEVEL=info

# OpenAI配置
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-4
```

### 依赖服务

- MongoDB: 数据存储
- Redis: 缓存服务
- 四诊微服务集群

### 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解详细更新记录。