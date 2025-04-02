# 索克生活APP - Agent Coordinator Service

## 项目概述

Agent Coordinator Service是索克生活APP的核心服务之一，负责协调不同AI代理之间的交互和工作流程。本服务采用TypeScript和Express框架开发，提供RESTful API接口，支持AI代理的管理、任务分发、知识图谱交互等功能。

## 功能特性

- AI代理管理与注册
- 跨代理任务协调
- 支持多模态输入处理
- RAG（检索增强生成）服务接口
- 实时通信机制
- 知识图谱交互
- 健康数据分析

## 技术栈

- Node.js
- TypeScript
- Express
- Jest (测试框架)
- Docker
- Kubernetes
- Helm

## 环境需求

- Node.js >= 16.x
- npm >= 8.x
- Docker (用于容器化部署)
- Kubernetes >= 1.19 (生产环境部署)
- Helm >= 3.7 (Helm部署)

## 开发环境设置

1. 克隆项目代码
   ```bash
   git clone <repository-url>
   cd services/agent-coordinator-service
   ```

2. 安装依赖
   ```bash
   npm install
   ```

3. 配置环境变量
   ```bash
   cp .env.example .env
   # 编辑.env文件，配置必要的环境变量
   ```

4. 启动开发服务器
   ```bash
   npm run dev
   ```

## 项目结构

```
agent-coordinator-service/
├── src/                      # 源代码目录
│   ├── config/               # 配置文件
│   ├── controllers/          # 控制器
│   ├── middleware/           # 中间件
│   ├── models/               # 数据模型
│   ├── routes/               # 路由定义
│   ├── services/             # 业务逻辑服务
│   ├── types/                # TypeScript类型定义
│   ├── utils/                # 工具函数
│   └── index.ts              # 应用入口
├── tests/                    # 测试文件目录
│   ├── unit/                 # 单元测试
│   ├── integration/          # 集成测试
│   ├── contract/             # 契约测试
│   └── benchmark/            # 性能基准测试
├── helm/                     # Helm Chart部署配置
│   └── agent-coordinator/    # 服务Helm Chart
│       ├── templates/        # Kubernetes资源模板
│       ├── Chart.yaml        # Chart元数据
│       ├── values.yaml       # 默认配置值
│       └── README.md         # Chart使用说明
├── k8s/                      # Kubernetes原生资源配置
├── docs/                     # 文档目录
│   ├── ENV_VARS.md           # 环境变量文档
│   ├── HELM_DEPLOYMENT.md    # Helm部署指南
│   └── CI_CD_PIPELINE.md     # CI/CD流水线文档
├── scripts/                  # 脚本文件目录
├── dist/                     # 编译输出目录
├── .env.example              # 环境变量示例
├── Dockerfile                # Docker配置
├── .gitlab-ci.yml            # GitLab CI/CD配置
├── jest.config.js            # Jest测试配置
├── package.json              # 项目依赖配置
├── tsconfig.json             # TypeScript配置
├── CONTRIBUTING.md           # 贡献指南
└── README.md                 # 项目说明
```

## API文档

服务启动后，可通过以下地址访问API文档：
```
开发环境: http://localhost:3001/api-docs
测试环境: https://api-test.suoke.life/api/v1/agents/coordinator/api-docs
生产环境: https://api.suoke.life/api/v1/agents/coordinator/api-docs
```

## 测试

运行单元测试：
```bash
npm run test:unit
```

运行集成测试：
```bash
npm run test:integration
```

运行契约测试：
```bash
npm run test:contract
```

检查测试覆盖率：
```bash
npm run test:coverage
```

## 贡献指南

请查看 [CONTRIBUTING.md](./CONTRIBUTING.md) 了解项目贡献规范和流程。

## 构建与部署

### 本地构建
```bash
npm run build
```

### Docker部署
```bash
# 构建Docker镜像
docker build -t suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/agent-coordinator-service:latest .

# 运行容器
docker run -p 3001:3001 -d suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/agent-coordinator-service:latest
```

### Helm部署

我们使用Helm Chart进行Kubernetes部署。详细部署指南请参考 [Helm部署文档](./docs/HELM_DEPLOYMENT.md)。

#### 基本部署命令

```bash
# 测试环境部署
helm upgrade --install agent-coordinator-test ./helm/agent-coordinator \
  --namespace suoke-test \
  --set environment=testing \
  --set replicaCount=1

# 生产环境部署
helm upgrade --install agent-coordinator ./helm/agent-coordinator \
  --namespace suoke \
  --set environment=production
```

#### 使用自定义配置

```bash
helm upgrade --install agent-coordinator ./helm/agent-coordinator \
  --namespace suoke \
  -f my-custom-values.yaml
```

## 环境变量配置

详细的环境变量配置请参考 [环境变量文档](./docs/ENV_VARS.md)。

## CI/CD流水线

本项目使用GitLab CI/CD进行持续集成和部署。详细信息请参考 [CI/CD流水线文档](./docs/CI_CD_PIPELINE.md)。

## 监控与可观测性

服务支持以下监控和可观测性功能：

- Prometheus指标导出 (端口9090)
- 健康检查端点 (/health/liveness, /health/readiness)
- OpenTelemetry分布式追踪
- 结构化日志记录

## 许可证

索克生活APP内部专用，保留所有权利。未经许可不得分发或使用。