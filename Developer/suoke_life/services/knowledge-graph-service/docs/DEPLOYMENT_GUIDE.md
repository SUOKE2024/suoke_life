# 索克生活知识图谱服务部署指南

本文档提供了索克生活知识图谱服务的详细部署指南，包括本地开发环境、测试环境和生产环境的部署步骤。

## 目录

1. [环境要求](#环境要求)
2. [本地开发环境部署](#本地开发环境部署)
3. [Kubernetes部署](#kubernetes部署)
   - [开发环境部署](#开发环境部署)
   - [测试环境部署](#测试环境部署)
   - [生产环境部署](#生产环境部署)
4. [配置管理](#配置管理)
5. [监控与日志](#监控与日志)
6. [常见问题排查](#常见问题排查)
7. [部署脚本参考](#部署脚本参考)

## 环境要求

### 基础要求

- Go 1.20+
- Docker 20.10+
- Kubernetes 1.22+
- Helm 3.8+
- kubectl 1.22+

### 依赖服务

- Neo4j 4.4+
- Redis 6.0+
- Milvus 2.3+
- Prometheus (可选，用于监控)
- Elasticsearch (可选，用于日志收集)

## 本地开发环境部署

### 使用Docker Compose

1. 克隆代码库：

```bash
git clone https://github.com/suoke-life/knowledge-graph-service.git
cd knowledge-graph-service
```

2. 配置环境变量：

```bash
cp .env.example .env
# 编辑.env文件，设置必要的环境变量
```

3. 启动服务：

```bash
docker-compose up -d
```

4. 验证服务：

```bash
curl http://localhost:8080/health
```

### 直接运行

1. 安装依赖：

```bash
go mod download
```

2. 构建服务：

```bash
go build -o knowledge-graph-service ./cmd/server
```

3. 运行服务：

```bash
./knowledge-graph-service
```

## Kubernetes部署

### 开发环境部署

1. 构建开发环境镜像：

```bash
docker build -t knowledge-graph-service:dev -f Dockerfile.amd64 .
```

2. 使用快速部署脚本：

```bash
./scripts/fix-deployment.sh
```

或者手动部署：

```bash
# 创建配置
./scripts/manage-configs.sh create dev

# 应用部署
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

3. 验证部署：

```bash
kubectl get pods -l app=knowledge-graph-service
kubectl port-forward svc/knowledge-graph-service 8080:8080
curl http://localhost:8080/health
```

### 测试环境部署

1. 构建并推送测试环境镜像：

```bash
# 设置环境变量
export REGISTRY_USERNAME=your-username
export REGISTRY_PASSWORD=your-password
export NAMESPACE=suoke-test

# 使用CI/CD脚本
SKIP_DEPLOY=true ./scripts/run-ci-cd.sh

# 部署到测试环境
./scripts/deploy-to-k8s.sh $NAMESPACE
```

2. 配置测试环境：

```bash
./scripts/manage-configs.sh create test $NAMESPACE
./scripts/manage-configs.sh apply test $NAMESPACE
```

3. 设置监控：

```bash
./scripts/setup-monitoring.sh setup $NAMESPACE
```

### 生产环境部署

1. 使用Helm部署：

```bash
# 设置环境变量
export NAMESPACE=suoke-prod

# 更新Helm依赖
helm dependency update ./helm

# 部署或升级
helm upgrade --install knowledge-graph ./helm \
  --namespace $NAMESPACE \
  -f ./helm/override-configs/values-prod.yaml \
  --set namespace=$NAMESPACE
```

2. 验证部署：

```bash
kubectl rollout status deployment/knowledge-graph-service -n $NAMESPACE
kubectl get pods -n $NAMESPACE -l app.kubernetes.io/name=knowledge-graph-service
```

## 配置管理

### 环境变量配置

服务支持以下配置方式，按优先级从高到低排序：

1. 命令行参数
2. 环境变量
3. 配置文件
4. 默认值

主要配置项：

| 配置项 | 描述 | 默认值 |
|-------|------|-------|
| `PORT` | 服务端口 | 8080 |
| `LOG_LEVEL` | 日志级别 | info |
| `DB_NEO4J_URI` | Neo4j连接URI | bolt://localhost:7687 |
| `DB_NEO4J_USERNAME` | Neo4j用户名 | neo4j |
| `DB_NEO4J_PASSWORD` | Neo4j密码 | password |
| `REDIS_HOST` | Redis主机 | localhost |
| `REDIS_PORT` | Redis端口 | 6379 |
| `MILVUS_URI` | Milvus连接URI | localhost:19530 |

### Kubernetes配置管理

使用配置管理脚本：

```bash
# 创建配置
./scripts/manage-configs.sh create <env> <namespace>

# 更新配置
./scripts/manage-configs.sh update <env> <namespace>

# 应用配置到部署
./scripts/manage-configs.sh apply <env> <namespace>
```

## 监控与日志

### 设置监控

```bash
./scripts/setup-monitoring.sh setup <namespace>
```

### 查看监控状态

```bash
./scripts/setup-monitoring.sh status <namespace>
```

### 查看服务日志

```bash
./scripts/setup-monitoring.sh logs <namespace>
```

### 查看服务指标

```bash
./scripts/setup-monitoring.sh metrics <namespace>
```

### Prometheus集成

服务在`/metrics`端点暴露Prometheus格式的指标，包括：

- HTTP请求计数和延迟
- Go运行时指标
- 自定义业务指标

### 日志收集

服务日志通过Fluent Bit收集到Elasticsearch，可在Kibana中查看。

## 常见问题排查

### Pod无法启动

1. 检查镜像拉取策略：

```bash
kubectl describe pod -l app=knowledge-graph-service
```

2. 检查环境变量和配置：

```bash
kubectl get configmap knowledge-graph-config -o yaml
```

3. 检查日志：

```bash
kubectl logs -l app=knowledge-graph-service
```

### 服务不健康

1. 检查健康端点：

```bash
kubectl port-forward svc/knowledge-graph-service 8080:8080
curl http://localhost:8080/health
```

2. 检查依赖服务连接：

```bash
kubectl exec -it $(kubectl get pod -l app=knowledge-graph-service -o jsonpath="{.items[0].metadata.name}") -- env | grep DB_
```

### 性能问题

1. 检查资源使用情况：

```bash
kubectl top pod -l app=knowledge-graph-service
```

2. 检查指标：

```bash
./scripts/setup-monitoring.sh metrics
```

## 部署脚本参考

### 快速修复部署

```bash
./scripts/fix-deployment.sh
```

### 配置管理

```bash
./scripts/manage-configs.sh <action> <env> [namespace]
```

### 监控设置

```bash
./scripts/setup-monitoring.sh <action> [namespace]
```

### CI/CD流程

```bash
./scripts/run-ci-cd.sh
```

### Kubernetes部署

```bash
./scripts/deploy-to-k8s.sh [namespace]
```
