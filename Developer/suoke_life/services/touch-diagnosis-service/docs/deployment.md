# 触诊服务部署文档

## 目录

1. [简介](#简介)
2. [部署架构](#部署架构)
3. [环境要求](#环境要求)
4. [容器化配置](#容器化配置)
5. [Kubernetes资源](#kubernetes资源)
6. [CI/CD流程](#cicd流程)
7. [监控与日志](#监控与日志)
8. [自动扩展](#自动扩展)
9. [网络安全](#网络安全)
10. [数据备份](#数据备份)
11. [常见问题与故障排除](#常见问题与故障排除)
12. [维护操作](#维护操作)
13. [安全考虑](#安全考虑)

## 简介

触诊服务(Touch Diagnosis Service)是索克生活平台四诊系统中的关键组件，负责处理和分析中医触诊数据。该服务采用微服务架构设计，支持高并发请求处理、自动扩展和容错。

**主要功能**:
- 脉象数据采集与分析
- 体表温度和湿度评估
- 腹部触诊数据处理
- 与四诊协调服务集成，提供完整的诊断数据

## 部署架构

触诊服务采用标准的微服务部署架构:

```
                          ┌─────────────────┐
                          │   Ingress/API   │
                          │     Gateway     │
                          └────────┬────────┘
                                   │
                          ┌────────▼────────┐
                          │ Touch Diagnosis │
                          │     Service     │
                          └────────┬────────┘
                                   │
         ┌───────────────┬─────────┴─────────┬───────────────┐
         │               │                   │               │
┌────────▼─────────┐    ┌▼──────────────┐   ┌▼──────────────┐ ┌─────────────────┐
│     MongoDB      │    │     Redis     │   │  Diagnosis    │ │ Knowledge Base  │
│    Database      │    │    Cache      │   │ Coordinator   │ │     Service     │
└──────────────────┘    └───────────────┘   └───────────────┘ └─────────────────┘
```

## 环境要求

### 基础设施要求

- **Kubernetes**: v1.22+
- **Istio**: v1.12+
- **MongoDB**: v5.0+
- **Redis**: v6.2+
- **Node.js**: v16+

### 资源需求

每个微服务实例推荐配置:
- **CPU**: 0.5-1 核
- **内存**: 512MB-1GB
- **存储**: 10GB (应用) + 根据数据量估算的数据库存储

## 容器化配置

### Dockerfile

服务的Dockerfile位于项目根目录，使用多阶段构建减小镜像大小:

```dockerfile
# 编译阶段
FROM node:16-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# 运行阶段
FROM node:16-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package*.json ./
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

ENV NODE_ENV=production
EXPOSE 3002

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["node", "dist/server.js"]
```

### Docker Entrypoint

`docker-entrypoint.sh` 脚本负责容器启动时的健康检查和初始化:

- 检查必要的环境变量
- 验证依赖服务的可用性
- 执行数据库迁移(如需要)
- 支持优雅关闭

### 本地开发

使用 `docker-compose.yml` 在本地模拟完整环境:

```bash
# 启动所有服务
docker-compose up

# 仅启动依赖服务
docker-compose up mongodb redis

# 停止并清理
docker-compose down -v
```

## Kubernetes资源

服务部署到Kubernetes集群使用以下资源:

### 1. 部署配置

主要配置通过 `k8s/deployment.yaml` 管理:

- 部署3个副本确保高可用
- 配置资源限制和请求
- 定义健康检查和就绪检查
- 设置环境变量和配置挂载

### 2. 服务访问

通过 `k8s/service.yaml` 定义服务访问:

- Service类型: ClusterIP
- 端口: 3002
- 与Istio集成实现细粒度流量控制

### 3. 配置管理

配置通过 `k8s/configmap.yaml` 管理:

- 应用参数配置
- 日志级别设置
- 功能开关

敏感信息通过 `HashiCorp Vault` 管理，不直接存储在配置中。

### 4. 持久化存储

通过 `k8s/pvc.yaml` 定义两种存储需求:

- 应用数据PVC: 10GB
- 备份数据PVC: 20GB

### 5. 自动扩展

通过 `k8s/hpa.yaml` 实现基于指标的水平自动扩展:

- 最小副本数: 3
- 最大副本数: 10
- 扩展触发条件: CPU利用率超过70%或内存利用率超过80%

### 6. 服务弹性

通过 `k8s/pdb.yaml` 定义PodDisruptionBudget确保服务弹性:

- 维护操作期间确保至少有1个实例可用
- 防止意外的服务中断

### 7. 备份策略

通过 `k8s/backup-cronjob.yaml` 定义自动备份:

- 每日凌晨2点执行备份
- 保留最近7天的备份
- 备份数据存储在专用PVC中

### 8. 统一管理

所有资源通过Kustomize统一管理:

```bash
# 应用所有资源
kubectl apply -k k8s/

# 应用特定环境的配置
kubectl apply -k k8s/overlays/production/
```

## CI/CD流程

服务采用GitOps模式通过ArgoCD部署:

1. 代码推送到Git仓库触发CI流水线
2. 流水线执行测试、构建和推送镜像
3. 更新部署清单中的镜像标签
4. ArgoCD检测到变更并自动同步到目标集群

```
代码推送 → CI构建 → 镜像推送 → 更新部署清单 → ArgoCD同步 → 部署到集群
```

### 环境隔离

通过Kustomize实现环境隔离:
- `k8s/overlays/dev/`
- `k8s/overlays/staging/`
- `k8s/overlays/production/`

每个环境使用不同的配置和资源限制。

## 监控与日志

### 指标监控

服务通过Prometheus端点暴露关键指标:

- 请求延迟
- 错误率
- 资源使用率
- 业务指标(如诊断处理数)

使用ServiceMonitor配置Prometheus采集:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: touch-diagnosis-monitor
spec:
  selector:
    matchLabels:
      app: touch-diagnosis-service
  endpoints:
  - port: http
    path: /metrics
    interval: 15s
```

### 分布式追踪

服务集成Jaeger实现分布式追踪:

- 所有API请求自动创建span
- 服务间调用追踪
- 数据库操作追踪

Jaeger收集器配置见 `jaeger/jaeger-collector.yaml`。

### 日志管理

日志通过EFK/ELK堆栈集中管理:

- 结构化JSON日志格式
- 包含请求ID实现跨服务日志关联
- 日志级别可动态调整

## 自动扩展

服务支持基于以下指标的自动扩展:

- **CPU使用率**: 超过70%触发扩展
- **内存使用率**: 超过80%触发扩展
- **并发请求数**: 每实例超过200请求触发扩展

配置示例:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: touch-diagnosis-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: touch-diagnosis-service
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## 网络安全

服务采用零信任网络安全模型:

- 所有服务间通信通过mTLS加密
- 严格的NetworkPolicy限制不必要的访问
- 服务账户拥有最小权限

NetworkPolicy配置示例:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: touch-diagnosis-network-policy
spec:
  podSelector:
    matchLabels:
      app: touch-diagnosis-service
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: istio-system
    - podSelector:
        matchLabels:
          app: diagnosis-coordinator-service
    ports:
    - protocol: TCP
      port: 3002
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: mongodb
    ports:
    - protocol: TCP
      port: 27017
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
```

## 数据备份

### 自动备份策略

服务使用CronJob实现自动备份:

- 每日凌晨2:00备份MongoDB数据
- 压缩并存储备份到专用PVC
- 自动清理7天前的备份

### 备份存储位置

- 开发/测试环境: 集群内PVC
- 生产环境: 存储到对象存储服务

### 恢复流程

数据恢复步骤:

1. 确定需要恢复的备份文件
2. 停止服务或切换流量
3. 执行恢复命令
4. 验证数据完整性
5. 恢复服务流量

## 常见问题与故障排除

### 健康检查失败

可能原因:
- 数据库连接问题
- Redis连接问题
- 应用内部错误

排查步骤:
1. 检查应用日志
2. 验证依赖服务状态
3. 检查资源使用情况

### 性能问题

可能原因:
- 数据库查询效率低
- 资源不足
- 连接泄漏

排查步骤:
1. 分析Prometheus指标
2. 查看CPU/内存使用情况
3. 检查数据库查询性能
4. 分析分布式追踪数据

### 服务启动失败

可能原因:
- 环境变量缺失
- 配置错误
- 依赖服务不可用

排查步骤:
1. 检查容器日志
2. 验证所有必要环境变量
3. 确认依赖服务健康状态

## 维护操作

### 滚动更新

通过以下命令执行滚动更新:

```bash
# 使用新镜像更新部署
kubectl set image deployment/touch-diagnosis-service touch-diagnosis-service=<new-image-tag>

# 或通过更新部署清单
kubectl apply -f k8s/deployment.yaml

# 或通过Kustomize更新所有资源
kubectl apply -k k8s/
```

### 回滚

如需回滚到之前版本:

```bash
# 查看部署历史
kubectl rollout history deployment/touch-diagnosis-service

# 回滚到特定版本
kubectl rollout undo deployment/touch-diagnosis-service --to-revision=<revision-number>

# 回滚到上一个版本
kubectl rollout undo deployment/touch-diagnosis-service
```

### 数据库迁移

在新版本部署前需要执行数据库迁移:

1. 确保迁移脚本已测试
2. 通过设置环境变量 `ENABLE_DB_MIGRATION=true` 启用自动迁移
3. 监控迁移过程日志
4. 验证迁移完成状态

## 安全考虑

### 敏感信息管理

所有敏感信息通过HashiCorp Vault管理:

- 数据库凭证
- API密钥
- 加密密钥

使用Vault通过CSI驱动注入密钥:

```yaml
volumes:
- name: secrets
  csi:
    driver: secrets-store.csi.k8s.io
    readOnly: true
    volumeAttributes:
      secretProviderClass: touch-diagnosis-vault-secrets
```

### 容器安全

容器安全最佳实践:

- 非root用户运行容器
- 只读文件系统
- 禁用特权模式
- 删除不必要的能力

配置示例:

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  readOnlyRootFilesystem: true
  capabilities:
    drop:
    - ALL
```

### 合规性考虑

服务符合以下安全标准:

- OWASP Top 10防护
- 敏感数据加密存储
- 审计日志记录关键操作
- 定期安全漏洞扫描