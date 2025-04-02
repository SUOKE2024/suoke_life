# 索儿服务（Soer Service）部署文档

## 目录

1. [简介](#简介)
2. [部署架构](#部署架构)
3. [环境要求](#环境要求)
4. [容器化配置](#容器化配置)
5. [Kubernetes资源](#kubernetes资源)
6. [CI/CD流程](#cicd流程)
7. [监控和日志](#监控和日志)
8. [自动伸缩](#自动伸缩)
9. [网络安全](#网络安全)
10. [数据备份](#数据备份)
11. [常见问题](#常见问题)
12. [维护操作](#维护操作)
13. [安全考虑](#安全考虑)

## 简介

索儿服务是索克生活平台面向儿童健康的核心微服务，主要负责儿童体质评估、生长曲线分析、健康食谱推荐等功能。它遵循微服务架构设计，使用Node.js开发，并通过MySQL存储结构化数据。

## 部署架构

索儿服务采用微服务架构部署在Kubernetes集群中，具有以下特点：

- **多副本部署**：默认部署2个副本，确保高可用性
- **自动伸缩**：根据CPU和内存负载自动调整副本数量
- **持久化存储**：使用阿里云SSD磁盘提供持久化存储
- **服务网格集成**：与Istio服务网格集成，实现流量管理和安全通信
- **监控集成**：与Prometheus和Grafana集成，实现全面监控
- **分布式跟踪**：与OpenTelemetry和Jaeger集成，实现分布式追踪

服务依赖关系：
- MySQL数据库：存储结构化数据
- Redis：提供缓存和会话管理
- 用户服务：提供用户认证和授权
- 知识图谱服务：提供健康知识检索

## 环境要求

### 生产环境要求

- **Kubernetes**：1.24+
- **Istio**：1.15+
- **MySQL**：8.0+
- **Redis**：7.0+
- **Node.js**：18.0+

### 开发环境要求

- **Docker**：20.10+
- **Docker Compose**：2.0+
- **Node.js**：18.0+
- **npm**：9.0+

## 容器化配置

### Dockerfile

索儿服务的Dockerfile位于项目根目录，实现了多阶段构建、非root用户运行和健康检查：

```dockerfile
# 构建阶段
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# 最终阶段
FROM node:18-alpine
WORKDIR /app
RUN apk --no-cache add curl tzdata netcat-openbsd
COPY --from=builder /app/node_modules ./node_modules
COPY . .
COPY scripts/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001
USER nodejs
EXPOSE 3000 9464
HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:3000/health
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["node", "src/server.js"]
```

### docker-entrypoint.sh

`docker-entrypoint.sh`脚本实现了环境变量检查、依赖服务健康检查、数据库迁移和优雅关闭功能：

```bash
#!/bin/bash
set -e

# 添加日志输出
log() {
  TIMESTAMP=$(date -u "+%Y-%m-%dT%H:%M:%SZ")
  echo "[$TIMESTAMP] $*"
}

# 检查环境变量
check_env_vars() {
  # 检查必要环境变量
}

# 检查依赖服务
check_dependencies() {
  # 检查数据库和Redis连接
}

# 注册信号处理器
trap 'log "正在关闭..."; exit 0' SIGTERM SIGINT

# 执行主命令
exec "$@"
```

### Docker Compose

本地开发使用Docker Compose配置，位于项目根目录的`docker-compose.yml`：

```yaml
version: '3.8'
services:
  soer-service:
    build: .
    ports:
      - "3000:3000"
    volumes:
      - ./:/app
    environment:
      - NODE_ENV=development
    depends_on:
      - mysql
      - redis
  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=root
      - MYSQL_DATABASE=soer_db
  redis:
    image: redis:7.0-alpine
```

## Kubernetes资源

所有Kubernetes资源定义位于`k8s/`目录，使用Kustomize管理多环境配置。

### 主要资源

- **deployment.yaml**：定义服务部署配置，包括副本数、容器规格、环境变量等
- **service.yaml**：定义服务访问方式
- **hpa.yaml**：定义水平自动伸缩策略
- **pdb.yaml**：定义服务中断预算，确保高可用性
- **persistent-volumes.yaml**：定义持久化存储卷
- **network-policy.yaml**：定义网络访问策略
- **backup-cronjob.yaml**：定义数据备份定时任务
- **monitoring.yaml**：定义监控集成配置

### 目录结构

```
k8s/
├── base/                  # 基础配置
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ...
│   └── kustomization.yaml
└── overlays/              # 环境特定配置
    ├── development/
    ├── testing/
    └── production/
```

### 部署命令

```bash
# 开发环境
kubectl apply -k k8s/overlays/development

# 测试环境
kubectl apply -k k8s/overlays/testing

# 生产环境
kubectl apply -k k8s/overlays/production
```

## CI/CD流程

索儿服务使用GitOps方法进行持续集成和部署，基于ArgoCD实现。

### CI流程

1. 代码提交到Git仓库
2. GitHub Actions触发构建流程
3. 代码静态分析、测试和安全扫描
4. 构建Docker镜像并推送到阿里云容器镜像服务

### CD流程

1. 更新Kubernetes清单中的镜像标签
2. 将更改提交到GitOps仓库
3. ArgoCD检测到配置变更
4. 自动部署到目标环境

### 环境提升流程

1. 开发环境（development）：自动部署
2. 测试环境（testing）：自动部署，但需要通过测试
3. 生产环境（production）：手动批准，使用蓝绿部署策略

## 监控和日志

### 监控指标

索儿服务在`/metrics`端点暴露Prometheus格式的指标：

- **应用指标**：API请求率、错误率、响应时间
- **JVM指标**：内存使用、GC活动
- **自定义业务指标**：儿童评估处理速率、生长数据分析性能

### 日志收集

使用EFK/ELK Stack收集和分析日志：

- 日志以JSON格式输出到标准输出
- 使用Fluent Bit收集Kubernetes日志
- 日志存储在Elasticsearch中
- 使用Kibana进行日志分析和可视化

### 警报配置

在Prometheus AlertManager中配置了以下警报：

- **高错误率**：5分钟内错误率超过5%
- **高响应时间**：90%请求响应时间超过500ms
- **服务不可用**：健康检查失败

## 自动伸缩

使用Kubernetes Horizontal Pod Autoscaler (HPA)实现自动伸缩：

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: soer-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: soer-service
  minReplicas: 2
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## 网络安全

使用Kubernetes NetworkPolicy限制服务访问：

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: soer-service-policy
spec:
  podSelector:
    matchLabels:
      app: soer-service
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: api-gateway
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: mysql
```

## 数据备份

使用CronJob定期备份数据：

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: soer-service-backup
spec:
  schedule: "0 2 * * *"  # 每天凌晨2点
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: mysql-backup:1.0.0
            command:
            - /bin/sh
            - -c
            - |
              # 备份数据库
              mysqldump -h ${MYSQL_HOST} -u ${MYSQL_USER} -p${MYSQL_PASSWORD} ${MYSQL_DATABASE} > /backup/soer-db-$(date +%Y%m%d).sql
```

## 常见问题

### 健康检查失败排查

1. 检查服务日志：`kubectl logs -l app=soer-service`
2. 检查数据库连接：`kubectl exec -it <pod-name> -- nc -zv mysql 3306`
3. 检查API响应：`kubectl exec -it <pod-name> -- curl -v http://localhost:3000/health`

### 服务无法启动排查

1. 检查环境变量：`kubectl describe pod <pod-name>`
2. 检查存储卷挂载：`kubectl describe pod <pod-name>`
3. 检查日志错误：`kubectl logs <pod-name>`

## 维护操作

### 滚动更新

```bash
# 更新镜像版本
kubectl set image deployment/soer-service soer-service=suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/soer-service:1.2.1

# 观察更新进度
kubectl rollout status deployment/soer-service
```

### 版本回滚

```bash
# 查看历史版本
kubectl rollout history deployment/soer-service

# 回滚到上一版本
kubectl rollout undo deployment/soer-service

# 回滚到特定版本
kubectl rollout undo deployment/soer-service --to-revision=2
```

## 安全考虑

### 敏感信息管理

使用Kubernetes Secrets存储敏感信息：

```bash
kubectl create secret generic soer-db-credentials \
  --from-literal=username=soer \
  --from-literal=password=<密码>
```

### 容器安全实践

- 非root用户运行容器
- 只读根文件系统
- 最小权限原则
- 容器镜像扫描
- 使用安全上下文限制容器权限