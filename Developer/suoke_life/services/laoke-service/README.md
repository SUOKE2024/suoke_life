# 老克智能体服务

老克（laoke）是索克生活APP探索频道版主，负责知识传播、知识培训和用户博客管理等工作，兼任索克游戏NPC，为用户提供无障碍功能服务，对特殊需求用户提供语音引导服务。

## 功能特点

- **知识传播**：提供多领域知识内容和个性化知识推荐
- **知识培训**：定制化学习路径和交互式培训课程
- **用户博客管理**：用户内容创作平台和社区管理
- **游戏NPC功能**：AR/VR游戏中的引导角色和任务发布者
- **无障碍功能**：为特殊需求用户提供无障碍体验
- **语音引导服务**：为视障用户提供语音辅助导航和操作指导
- **无感数据采集**：支持语音流、视频流的无感采集和处理
- **方言支持**：支持多种中国方言的识别、转换和合成

## 技术架构

老克智能体服务采用微服务架构，基于Node.js和Express框架开发，主要组件包括：

- **核心服务**：负责请求处理、路由和基础功能
- **智能体引擎**：处理用户查询和决策逻辑
- **知识管理系统**：管理和组织知识内容
- **语音处理引擎**：支持语音识别和合成
- **AR/VR集成模块**：支持沉浸式体验
- **无障碍功能模块**：支持辅助技术和替代交互方式

### 目录结构

```
services/laoke-service/
├── src/                    # 源代码
│   ├── core/               # 核心模块
│   │   ├── agent/          # 智能体系统
│   │   ├── cache/          # 缓存管理
│   │   ├── database/       # 数据库连接
│   │   ├── metrics/        # 监控和指标
│   │   ├── middleware/     # 中间件
│   │   ├── routes/         # API路由
│   │   └── websocket/      # WebSocket通信
│   ├── services/           # 业务服务
│   │   ├── knowledge/      # 知识管理服务
│   │   ├── training/       # 培训服务
│   │   ├── blog/           # 博客管理服务
│   │   ├── game/           # 游戏NPC服务
│   │   ├── accessibility/  # 无障碍功能服务
│   │   └── voice/          # 语音引导服务
│   ├── models/             # 数据模型
│   ├── config/             # 配置文件
│   └── utils/              # 工具函数
├── docs/                   # 文档
├── tests/                  # 测试
├── .env.example            # 环境变量示例
├── Dockerfile              # Docker构建文件
├── package.json            # 项目依赖
└── tsconfig.json           # TypeScript配置
```

## 安装与运行

### 前提条件

- Node.js 18+
- MongoDB 5+
- Redis 6+
- Docker (可选)

### 本地开发

1. 克隆仓库并进入项目目录
```bash
cd services/laoke-service
```

2. 安装依赖
```bash
npm install
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，设置必要的环境变量
```

4. 启动开发服务器
```bash
npm run dev
```

### Docker构建与运行

1. 构建Docker镜像
```bash
docker build -t laoke-service:latest .
```

2. 运行容器
```bash
docker run -p 3012:3012 -p 9465:9465 --env-file .env laoke-service:latest
```

## API接口

### 知识管理

- `GET /api/v1/knowledge` - 获取知识内容列表
- `GET /api/v1/knowledge/:id` - 获取知识内容详情
- `GET /api/v1/knowledge/recommend` - 获取推荐知识内容
- `GET /api/v1/knowledge/categories` - 获取知识分类

### 培训服务

- `GET /api/v1/training/courses` - 获取培训课程列表
- `GET /api/v1/training/courses/:id` - 获取课程详情
- `POST /api/v1/training/enroll/:courseId` - 报名课程
- `GET /api/v1/training/progress/:userId` - 获取学习进度

### 博客管理

- `GET /api/v1/blogs` - 获取博客列表
- `GET /api/v1/blogs/:id` - 获取博客详情
- `POST /api/v1/blogs` - 创建博客
- `PUT /api/v1/blogs/:id` - 更新博客
- `DELETE /api/v1/blogs/:id` - 删除博客

### 游戏NPC

- `GET /api/v1/game/quests` - 获取任务列表
- `GET /api/v1/game/quests/:id` - 获取任务详情
- `POST /api/v1/game/quests/:id/accept` - 接受任务
- `POST /api/v1/game/quests/:id/complete` - 完成任务

### 无障碍功能

- `GET /api/v1/accessibility/profile/:userId` - 获取用户无障碍配置
- `PUT /api/v1/accessibility/profile/:userId` - 更新用户无障碍配置
- `GET /api/v1/accessibility/resources` - 获取无障碍资源

### 语音引导

- `POST /api/v1/voice/guide` - 获取语音引导指令
- `GET /api/v1/voice/commands` - 获取可用语音命令列表

### 媒体流处理

- `POST /api/v1/media/streams` - 创建媒体流
- `POST /api/v1/media/streams/:id/chunks` - 上传媒体流块
- `POST /api/v1/media/streams/:id/complete` - 完成媒体流处理
- `GET /api/v1/media/streams` - 获取媒体流列表
- `GET /api/v1/media/streams/:id` - 获取媒体流详情

### 方言支持

- `GET /api/v1/dialects` - 获取支持的方言列表
- `GET /api/v1/dialects/by-region` - 按地区获取方言列表
- `GET /api/v1/dialects/:code` - 获取方言详情
- `POST /api/v1/dialects/detect` - 检测音频中的方言
- `POST /api/v1/dialects/translate` - 转换方言到标准普通话

## 监控与指标

服务暴露以下端点用于监控和健康检查：

- `GET /health` - 健康检查
- `GET /metrics` - Prometheus指标 (端口9465)

## 微服务集成

老克服务是索克生活微服务架构的一部分，与以下服务集成：

- 认证服务：用户身份验证
- 用户服务：获取用户偏好和历史记录
- RAG服务：检索增强生成
- 知识图谱服务：获取领域知识
- 小艾服务：主智能体协作
- 小克服务：供应链与农产品服务

## 安全集成

服务使用Vault进行秘密管理：

- 数据库凭证从Vault动态加载
- API密钥安全存储
- 自动秘密轮换
- 遵循最小权限原则

## Kubernetes部署

本服务提供了完整的Kubernetes配置，支持在Kubernetes集群中部署。

### 使用kubectl部署

1. 切换到正确的上下文：
```bash
kubectl config use-context your-cluster-context
```

2. 部署服务：
```bash
kubectl apply -k k8s/
```

3. 验证部署：
```bash
kubectl get pods -n suoke -l app=laoke-service
kubectl get svc -n suoke -l app=laoke-service
```

### 使用Helm部署

1. 安装或升级Chart：
```bash
helm upgrade --install laoke-service ./helm \
  --namespace suoke \
  --create-namespace \
  --set image.tag=latest \
  --values ./helm/values.yaml
```

## 可观测性

服务通过以下方式支持可观测性：

1. Prometheus指标：
   - 服务在`:9465/metrics`端点暴露Prometheus指标
   - ServiceMonitor自动配置了指标收集

2. OpenTelemetry集成：
   - 通过环境变量`OTEL_EXPORTER_OTLP_ENDPOINT`配置OpenTelemetry导出器
   - 支持分布式追踪

3. 健康检查端点：
   - `/health/live`：活性检查
   - `/health/ready`：就绪检查
   - `/health/startup`：启动检查

## 许可证

© SUOKE.LIFE团队，保留所有权利。 