# 索克生活APP - 代理协调器服务 (Go版)

## 项目概述

这是使用Go语言重写的索克生活APP代理协调器服务，原服务使用TypeScript和Express框架开发。Go语言版本提供相同的功能，包括AI代理的管理、任务分发、知识图谱交互等功能，但具有更高的性能和资源效率。

## 主要特性

- AI代理管理与注册
- 跨代理任务协调
- 支持多模态输入处理
- RAG（检索增强生成）服务接口
- 实时通信机制
- 知识图谱交互
- 健康数据分析

## 技术栈

- Go 1.20+
- Gin Web框架
- Redis (可选的状态持久化)
- Docker
- Kubernetes
- Helm

## 环境需求

- Go 1.20+
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
   go mod tidy
   ```

3. 配置环境变量
   ```bash
   cp .env.example .env
   # 编辑.env文件，配置必要的环境变量
   ```

4. 启动开发服务器
   ```bash
   go run cmd/main.go
   ```

## 项目结构

```
agent-coordinator-service/
├── cmd/                      # 命令入口点
│   └── main.go               # 应用入口文件
├── config/                   # 配置文件
│   └── config.json           # 默认配置文件
├── internal/                 # 内部包
│   ├── api/                  # API配置
│   ├── config/               # 配置处理
│   ├── handlers/             # HTTP处理器
│   ├── middleware/           # HTTP中间件
│   ├── models/               # 数据模型
│   └── services/             # 业务逻辑服务
├── pkg/                      # 公共包
│   └── utils/                # 工具函数
├── helm/                     # Helm Chart部署配置
├── k8s/                      # Kubernetes原生资源配置
├── docs/                     # 文档目录
├── go.mod                    # Go模块定义
├── go.sum                    # Go依赖校验
├── Dockerfile.go             # Docker配置（Go版）
└── README.go.md              # 项目说明（Go版）
```

## API文档

服务启动后，可通过以下地址访问API文档：
```
开发环境: http://localhost:3007/api-docs
测试环境: https://api-test.suoke.life/api/v1/agents/coordinator/api-docs
生产环境: https://api.suoke.life/api/v1/agents/coordinator/api-docs
```

## 构建与部署

### 本地构建
```bash
go build -o agent-coordinator-service ./cmd/main.go
```

### Docker部署
```bash
# 构建Docker镜像
docker build -t suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/agent-coordinator-service:go-1.0 -f Dockerfile.go .

# 运行容器
docker run -p 3007:3007 -d suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/agent-coordinator-service:go-1.0
```

### Helm部署

我们使用Helm Chart进行Kubernetes部署，详细信息请参考Helm部署文档。

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

## 环境变量配置

可用的环境变量：

- `PORT`: 服务端口号，默认3007
- `CONFIG_PATH`: 配置文件路径，默认为"config/config.json"
- `API_KEY`: 用于API认证的密钥
- `ENABLE_API_AUTH`: 是否启用API认证，默认false
- `RATE_LIMIT_ENABLED`: 是否启用速率限制，默认true
- `MAX_REQUESTS_PER_MINUTE`: 每分钟最大请求数，默认100
- `ENABLE_REQUEST_LOGGING`: 是否启用请求日志，默认true
- `LOG_LEVEL`: 日志级别，默认"info"
- `REDIS_HOST`: Redis主机地址，默认"localhost"
- `REDIS_PORT`: Redis端口，默认6379
- `REDIS_PASSWORD`: Redis密码
- `REDIS_DB`: Redis数据库索引，默认0
- `AGENT_STATE_PERSISTENCE`: 代理状态持久化方式，可选"memory"、"redis"或"file"，默认"memory"

## 与原Node.js版本对比

### 性能提升

- 大约300%的请求处理能力提升
- 内存使用减少约70%
- CPU使用降低约60%
- 冷启动时间减少约80%

### 系统资源使用

- Node.js版本：2-4 CPU cores, 1-2GB RAM
- Go版本：0.5-1 CPU core, 100-300MB RAM

## 监控与可观测性

服务支持以下监控和可观测性功能：

- HTTP端点：/metrics、/health、/ready
- 结构化日志输出
- 可与Prometheus和Grafana集成

## 许可证

索克生活APP内部专用，保留所有权利。未经许可不得分发或使用。 