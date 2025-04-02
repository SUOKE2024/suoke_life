# 小克服务 (xiaoke-service) 部署文档

## 1. 概述

小克服务是索克生活平台的供应链与农产品服务智能体，负责处理农产品订单、农事活动和可追溯性查询等核心功能。本文档详细描述了小克服务的部署架构、配置和操作流程。

## 2. 部署架构

小克服务采用微服务架构，部署在Kubernetes集群中，使用以下组件：

- **应用容器**: 基于Node.js 18的服务
- **数据库**: MongoDB用于持久化存储
- **缓存**: Redis用于数据缓存和会话管理
- **消息队列**: RocketMQ用于事件处理
- **服务网格**: Istio用于流量管理和安全通信
- **监控**: Prometheus/Grafana/OpenTelemetry用于可观测性

### 2.1 系统架构图

```
                    +---------------+
                    |  API 网关     |
                    +-------+-------+
                            |
                    +-------v-------+
                    |  小克服务     |
                    +---+-----------+
                        |
        +---------------+----------------+
        |               |                |
+-------v------+ +------v-------+ +-----v--------+
| MongoDB 集群 | | Redis 集群   | | RocketMQ 集群 |
+--------------+ +--------------+ +--------------+
```

## 3. 部署前置条件

- Kubernetes 集群 v1.24+
- Helm v3.10+
- kubectl CLI 工具
- 已配置的命名空间 `suoke`
- 阿里云容器镜像服务访问权限
- 已部署的服务网格 (Istio)
- 已部署的监控系统 (Prometheus, Grafana)
- 已部署的日志系统 (EFK/ELK)

## 4. 配置文件说明

小克服务的配置文件位于 `k8s/` 目录下，包括：

| 文件名 | 用途 |
|-------|------|
| `deployment.yaml` | 定义服务部署，包含副本数、资源限制、健康检查等 |
| `service.yaml` | 定义服务访问方式和端口映射 |
| `hpa.yaml` | 定义水平自动伸缩策略，根据CPU、内存和自定义指标自动调整副本数 |
| `network-policy.yaml` | 定义网络安全策略，限制进出流量 |
| `istio-config.yaml` | 定义Istio服务网格配置，包括流量路由、重试和安全策略 |
| `pvc.yaml` | 定义持久卷声明，用于数据、缓存和日志存储 |
| `serviceaccount.yaml` | 定义服务账户和RBAC权限 |
| `backup-job.yaml` | 定义自动备份任务，定时备份数据 |
| `pdb.yaml` | 定义Pod中断预算，确保维护期间服务可用性 |
| `opentelemetry-config.yaml` | 定义OpenTelemetry收集器配置，用于指标、日志和追踪收集 |
| `kustomization.yaml` | Kustomize配置，整合所有资源 |

## 5. 部署步骤

### 5.1 构建容器镜像

```bash
# 构建并推送镜像到阿里云容器镜像服务
docker build -t suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/xiaoke-service:latest .
docker push suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/xiaoke-service:latest

# 或使用自动化CI/CD流程构建
# CI/CD系统会自动构建并推送镜像
```

### 5.2 准备配置

```bash
# 创建配置映射和密钥
kubectl create configmap xiaoke-agent-config --from-file=config/agent-config.json -n suoke
kubectl create secret generic xiaoke-db-credentials \
  --from-literal=mongodb-uri="mongodb://username:password@hostname:27017/xiaoke" \
  --from-literal=redis-password="redispassword" \
  -n suoke
```

### 5.3 部署服务

使用Kustomize部署所有资源：

```bash
# 部署所有资源
kubectl apply -k k8s/

# 验证部署状态
kubectl get all -l app=xiaoke-service -n suoke
```

或者单独应用各个资源：

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
# ... 其他资源文件
```

### 5.4 验证部署

```bash
# 检查Pod运行状态
kubectl get pods -l app=xiaoke-service -n suoke

# 检查服务状态
kubectl get svc xiaoke-service -n suoke

# 检查日志
kubectl logs -l app=xiaoke-service -n suoke

# 测试健康检查端点
kubectl port-forward svc/xiaoke-service 3011:3011 -n suoke
curl http://localhost:3011/health
```

## 6. 配置说明

### 6.1 环境变量

小克服务支持以下环境变量:

| 环境变量 | 描述 | 默认值 |
|---------|-----|-------|
| `NODE_ENV` | 运行环境 | `production` |
| `PORT` | HTTP服务端口 | `3011` |
| `METRICS_PORT` | 指标监控端口 | `9464` |
| `WEBSOCKET_PORT` | WebSocket端口 | `3012` |
| `LOG_LEVEL` | 日志级别 | `info` |
| `LOG_DIR` | 日志目录 | `/app/logs` |
| `DATA_DIR` | 数据目录 | `/app/data` |
| `CACHE_DIR` | 缓存目录 | `/app/cache` |
| `MONGODB_URI` | MongoDB连接字符串 | - |
| `REDIS_HOST` | Redis主机 | - |
| `REDIS_PORT` | Redis端口 | `6379` |
| `REDIS_PASSWORD` | Redis密码 | - |

### 6.2 资源配置

默认资源配置：

```yaml
resources:
  requests:
    cpu: "1"
    memory: "2Gi"
  limits:
    cpu: "2"
    memory: "4Gi"
```

### 6.3 自动扩展配置

自动扩展配置允许服务根据负载自动调整Pod数量：

```yaml
minReplicas: 2
maxReplicas: 5
metrics:
  - resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## 7. 运维操作

### 7.1 扩缩容

```bash
# 手动扩展副本数
kubectl scale deployment/xiaoke-service --replicas=3 -n suoke

# 启用/禁用自动扩展
kubectl patch hpa xiaoke-service -n suoke -p '{"spec":{"minReplicas":2}}'
```

### 7.2 滚动更新

```bash
# 更新容器镜像
kubectl set image deployment/xiaoke-service xiaoke-service=suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/xiaoke-service:1.0.1 -n suoke

# 查看更新状态
kubectl rollout status deployment/xiaoke-service -n suoke
```

### 7.3 回滚

```bash
# 回滚到上一个版本
kubectl rollout undo deployment/xiaoke-service -n suoke

# 回滚到特定版本
kubectl rollout undo deployment/xiaoke-service --to-revision=2 -n suoke

# 查看部署历史
kubectl rollout history deployment/xiaoke-service -n suoke
```

### 7.4 查看日志

```bash
# 查看实时日志
kubectl logs -f -l app=xiaoke-service -n suoke

# 使用Kibana查看日志
# 访问 https://kibana.suoke.life
# 搜索 kubernetes.namespace:suoke AND kubernetes.labels.app:xiaoke-service
```

### 7.5 备份与恢复

```bash
# 手动触发备份任务
kubectl create job --from=cronjob/xiaoke-service-backup manual-backup -n suoke

# 恢复备份
# 按照备份恢复文档操作
```

## 8. 监控和告警

### 8.1 监控指标

小克服务在 `/metrics` 端点暴露以下指标：

- `http_requests_total`: HTTP请求总数
- `http_request_duration_seconds`: HTTP请求处理时间
- `orders_total`: 订单处理总数
- `farm_activity_metrics`: 农事活动处理指标
- `mongodb_query_execution_time`: MongoDB查询执行时间
- `redis_cache_hit_ratio`: Redis缓存命中率

### 8.2 告警规则

已配置的告警规则：

| 告警名称 | 触发条件 | 严重性 |
|---------|---------|-------|
| XiaokeServiceDown | 服务不可用超过5分钟 | 严重 |
| XiaokeServiceHighErrorRate | 错误率超过5%持续10分钟 | 警告 |
| XiaokeServiceHighLatency | P95延迟超过500ms持续15分钟 | 警告 |
| XiaokeServiceHighMemory | 内存使用率超过90%持续10分钟 | 严重 |

## 9. 网络安全

小克服务通过以下机制保障安全：

- **网络策略**: 限制进出流量
- **mTLS加密**: 服务间通信加密
- **访问控制**: 基于JWT的API认证
- **漏洞扫描**: 定期扫描容器镜像
- **安全上下文**: 限制容器权限

## 10. 故障排除

### 10.1 常见问题

1. **Pod启动失败**:
   - 检查资源限制: `kubectl describe pod <pod-name> -n suoke`
   - 检查日志: `kubectl logs <pod-name> -n suoke`
   - 验证配置和密钥: `kubectl describe configmap,secret -l app=xiaoke-service -n suoke`

2. **服务不可访问**:
   - 检查Service: `kubectl get svc xiaoke-service -n suoke`
   - 检查Endpoints: `kubectl get endpoints xiaoke-service -n suoke`
   - 测试网络策略: `kubectl run -it --rm debug --image=busybox -- wget -O- http://xiaoke-service:3011/health`

3. **高延迟问题**:
   - 检查负载: `kubectl top pod -l app=xiaoke-service -n suoke`
   - 检查数据库连接: 查看服务日志中的数据库操作时间
   - 考虑扩容: 增加副本数或资源限制

### 10.2 获取支持

如遇问题，请联系索克生活技术团队：

- 邮件: tech@suoke.life
- 内部工单系统: https://support.suoke.life
- 紧急联系人: 技术负责人 (13800138000)

## 11. 参考文档

- [小克服务API文档](http://api-docs.suoke.life/xiaoke-service)
- [Kubernetes文档](https://kubernetes.io/docs/)
- [Node.js最佳实践](https://github.com/goldbergyoni/nodebestpractices)
- [索克生活微服务部署标准](https://docs.suoke.life/microservices-deployment)

---

文档版本: v1.0.0  
最后更新: 2023-03-30  
作者: 索克生活技术团队 