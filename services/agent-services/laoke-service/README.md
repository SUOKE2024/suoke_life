# 老克智能体服务 (Laoke Service)

老克智能体是索克生活APP探索频道的核心智能体，负责知识传播、知识培训和社区内容管理。它通过GraphQL和gRPC接口提供服务，实现了知识内容管理、学习路径推荐和社区内容交互等功能。

## 服务功能

老克智能体提供以下核心功能：

1. **知识内容管理**：
   - 提供中医、养生相关的知识文章和资源
   - 支持多种难度级别的知识内容
   - 提供知识内容搜索和推荐

2. **学习路径**：
   - 个性化学习路径规划
   - 学习进度跟踪和管理
   - 基于用户行为和兴趣的学习内容推荐

3. **社区内容管理**：
   - 用户创作内容的管理和推荐
   - 社区讨论和互动
   - 内容质量控制和审核

## 技术架构

老克智能体服务采用微服务架构，主要包括以下技术组件：

- **API层**：
  - GraphQL API：面向前端应用提供灵活查询
  - gRPC API：面向微服务内部通信
  - REST API：提供健康检查和监控端点

- **业务逻辑层**：
  - 知识服务：管理知识内容和学习路径
  - 社区服务：管理社区内容和互动
  - 智能体管理：协调老克智能体的决策和行为

- **数据持久层**：
  - MongoDB：存储非结构化和半结构化数据
  - PostgreSQL：存储关系型数据
  - Neo4j：存储知识图谱和关系数据
  - Redis：缓存和会话管理

- **基础设施**：
  - Kubernetes：容器编排和服务管理
  - Prometheus：服务监控和告警
  - OpenTelemetry：分布式追踪和可观测性
  - Docker：容器化部署

## 项目结构

```
services/agent-services/laoke-service/
├── api/                          # API定义和协议
│   ├── graphql/                  # GraphQL接口定义
│   └── grpc/                     # gRPC接口定义
├── cmd/                          # 应用入口
│   └── server/                   # 服务器入口点
├── config/                       # 配置文件
│   ├── config.yaml               # 基础配置
│   └── config.development.yaml   # 开发环境配置
├── deploy/                       # 部署配置
│   ├── docker/                   # Docker配置
│   ├── grafana/                  # Grafana面板配置
│   ├── kubernetes/               # Kubernetes配置
│   └── prometheus/               # Prometheus配置
├── integration/                  # 外部服务集成
│   └── edu/                      # 教育服务集成
├── internal/                     # 内部实现
│   ├── agent/                    # 智能体逻辑
│   ├── community/                # 社区服务
│   ├── delivery/                 # 接口交付层
│   ├── integration/              # 集成服务
│   ├── knowledge/                # 知识服务
│   └── repository/               # 数据存储层
├── pkg/                          # 共享包
│   └── utils/                    # 通用工具
└── test/                         # 测试代码
    ├── unit/                     # 单元测试
    └── integration/              # 集成测试
```

## 依赖

- Python 3.11+
- MongoDB 6.0+
- Redis 7.0+
- PostgreSQL 15+
- Neo4j 5.0+ (可选)

## 启动服务

### 本地开发

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 启动服务

```bash
# 开发模式
python cmd/server/main.py --reload

# 指定端口
python cmd/server/main.py --port 8080
```

### 使用Docker

```bash
# 构建镜像
docker build -t laoke-service -f deploy/docker/Dockerfile .

# 运行容器
docker run -p 8080:8080 -p 50051:50051 -p 9091:9091 laoke-service
```

### 使用Kubernetes

```bash
# 部署到Kubernetes
kubectl apply -f deploy/kubernetes/deployment.yaml
```

## 配置

配置文件位于`config/`目录下，支持通过环境变量覆盖配置项。主要配置项包括：

- `LAOKE_ENV`：环境类型（development, staging, production）
- `LAOKE_CONFIG_PATH`：配置文件路径
- `POSTGRES_PASSWORD`：PostgreSQL数据库密码
- `MONGODB_URI`：MongoDB连接URI
- `REDIS_PASSWORD`：Redis密码

## API接口

### GraphQL API

GraphQL API位于`/graphql`端点，提供以下主要查询和变更：

#### 查询

- `knowledgeArticles`: 获取知识文章列表
- `learningPaths`: 获取学习路径列表
- `communityPosts`: 获取社区帖子列表

#### 变更

- `agentInteraction`: 与智能体交互
- `createCommunityPost`: 创建社区帖子
- `enrollLearningPath`: 报名学习路径

### REST API

- `/health/status`: 健康检查端点
- `/metrics`: Prometheus指标端点

## 开发

### 运行测试

```bash
# 运行单元测试
pytest test/unit

# 运行集成测试
pytest test/integration

# 运行测试覆盖率报告
pytest --cov=internal
```

### 代码规范

项目使用以下代码规范和工具：

- Black：代码格式化
- isort：导入排序
- mypy：类型检查
- pylint：代码分析

## 监控

服务通过Prometheus和Grafana提供监控能力：

- 指标端点：`/metrics`
- Grafana面板：位于`deploy/grafana/dashboards/`

## 贡献

欢迎向老克智能体服务项目贡献代码。请遵循以下步骤：

1. Fork本仓库
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可

索克生活项目专有许可 