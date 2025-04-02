# 索克生活 - 索儿微服务

索儿服务是索克生活平台的核心微服务之一，主要负责处理与儿童健康相关的数据与功能。

## 功能特性

- 儿童体质评估
- 生长曲线分析
- 健康食谱推荐
- 家长指导建议
- 儿童疾病防护知识

## 技术栈

- **运行环境**: Node.js 18+
- **Web框架**: Express.js
- **数据库**: MySQL
- **缓存**: Redis
- **日志**: Winston
- **监控**: Prometheus + Grafana
- **链路追踪**: OpenTelemetry + Jaeger
- **部署**: Docker + Kubernetes

## 项目结构

```
soer-service/
├── .github/workflows/        # CI/CD配置
├── config/                   # 配置文件
│   ├── dev-config.json       # 开发环境配置
│   ├── test-config.json      # 测试环境配置
│   ├── prod-config.json      # 生产环境配置
│   └── otel-config.yaml      # OpenTelemetry配置
├── k8s/                      # Kubernetes配置
│   ├── base/                 # 基础配置
│   └── overlays/             # 不同环境的配置覆盖
│       ├── development/
│       ├── testing/
│       └── production/
├── src/                      # 源代码
│   ├── metrics/              # 指标收集
│   ├── routes/               # API路由
│   │   ├── health/           # 健康检查路由
│   │   └── api/              # 业务API路由
│   ├── utils/                # 工具函数
│   ├── app.js                # 应用入口
│   └── server.js             # 服务器启动文件
├── tests/                    # 测试文件
├── Dockerfile                # 容器构建配置
├── package.json              # 项目依赖
└── README.md                 # 项目说明
```

## 开发指南

### 环境要求

- Node.js 18+
- npm 9+
- Docker（可选，用于本地容器化测试）
- kubectl & kustomize（可选，用于Kubernetes部署）

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

服务将在 http://localhost:3000 上运行。

### 运行测试

```bash
npm test
```

### 代码风格检查

```bash
npm run lint
```

### 构建Docker镜像

```bash
npm run docker:build
```

## 部署指南

### 使用Kubernetes部署

1. 创建必要的密钥

```bash
kubectl create secret generic soer-service-secrets \
  --from-literal=db-host=<DB_HOST> \
  --from-literal=db-port=<DB_PORT> \
  --from-literal=db-user=<DB_USER> \
  --from-literal=db-password=<DB_PASSWORD> \
  --from-literal=db-name=<DB_NAME> \
  --from-literal=redis-host=<REDIS_HOST> \
  --from-literal=redis-port=<REDIS_PORT> \
  --from-literal=redis-password=<REDIS_PASSWORD>
```

2. 部署到Kubernetes

```bash
# 开发环境
kubectl apply -k k8s/overlays/development

# 测试环境
kubectl apply -k k8s/overlays/testing

# 生产环境
kubectl apply -k k8s/overlays/production
```

## 监控

- 健康检查: `/health` 和 `/health/ready`
- 指标端点: `/metrics` (Prometheus格式)

## 维护者

- 索克生活开发团队