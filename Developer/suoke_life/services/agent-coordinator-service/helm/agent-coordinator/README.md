# 索克生活平台 - Agent Coordinator Service Helm Chart

## 概述

Agent Coordinator Service Helm Chart提供了完整的Kubernetes部署配置，用于在Kubernetes集群中部署和管理Agent Coordinator微服务。

该Chart支持以下功能：
- 基本部署配置 (副本数、镜像、标签等)
- 自动伸缩配置 (HPA)
- 配置管理 (ConfigMap)
- 网络策略配置
- 持久化存储配置
- 服务监控 (Prometheus ServiceMonitor)
- Istio服务网格集成
- 备份计划 (Velero)

## 安装前提

- Kubernetes 1.19+
- Helm 3.7+
- Prometheus Operator (如需启用监控)
- Istio (如需启用服务网格功能)
- Velero (如需启用备份功能)

## 安装步骤

```bash
# 添加chart仓库
helm repo add suoke-registry https://charts.suoke.life

# 更新repo
helm repo update

# 测试环境部署
helm install agent-coordinator-test suoke-registry/agent-coordinator \
  --namespace suoke-test \
  --set environment=testing

# 生产环境部署
helm install agent-coordinator suoke-registry/agent-coordinator \
  --namespace suoke
```

## 自定义配置

可以通过创建自定义values文件来进行配置：

```bash
helm install agent-coordinator suoke-registry/agent-coordinator \
  --namespace suoke \
  -f custom-values.yaml
```

## 配置参数

| 参数 | 描述 | 默认值 |
| --- | --- | --- |
| `replicaCount` | Pod副本数 | `3` |
| `image.repository` | 容器镜像仓库 | `suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/agent-coordinator-service` |
| `image.tag` | 容器镜像标签 | `1.2.0` |
| `image.pullPolicy` | 镜像拉取策略 | `IfNotPresent` |
| `resources.requests.cpu` | CPU请求 | `500m` |
| `resources.requests.memory` | 内存请求 | `512Mi` |
| `resources.limits.cpu` | CPU限制 | `1000m` |
| `resources.limits.memory` | 内存限制 | `1Gi` |
| `autoscaling.enabled` | 是否启用自动伸缩 | `true` |
| `autoscaling.minReplicas` | 最小副本数 | `2` |
| `autoscaling.maxReplicas` | 最大副本数 | `5` |
| `persistence.enabled` | 是否启用持久化存储 | `true` |
| `persistence.storageClass` | 存储类 | `suoke-standard` |
| `persistence.size` | 存储大小 | `10Gi` |
| `persistence.accessMode` | 访问模式 | `ReadWriteOnce` |
| `monitoring.enabled` | 是否启用监控 | `true` |
| `istio.enabled` | 是否启用Istio集成 | `true` |
| `backup.enabled` | 是否启用备份计划 | `true` |

## 配置示例

### 基本配置示例

```yaml
replicaCount: 3
environment: production
image:
  repository: suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/agent-coordinator-service
  tag: "1.2.1"
```

### 启用自动伸缩

```yaml
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 75
```

### 启用Prometheus监控

```yaml
monitoring:
  enabled: true
  serviceMonitor:
    enabled: true
    interval: 15s
    scrapeTimeout: 10s
    labels:
      release: prometheus
```

### 持久化存储配置

```yaml
persistence:
  enabled: true
  storageClass: "suoke-ssd"
  size: "20Gi"
  accessMode: ReadWriteOnce
```

## 故障排除

- 检查Pod运行状态: `kubectl get pods -n <namespace> -l app=agent-coordinator`
- 查看Pod日志: `kubectl logs -n <namespace> -l app=agent-coordinator`
- 检查HPA状态: `kubectl get hpa -n <namespace>`
- 检查Service: `kubectl get svc -n <namespace> -l app=agent-coordinator`

## 维护

- 升级Chart: `helm upgrade agent-coordinator suoke-registry/agent-coordinator -n suoke`
- 回滚部署: `helm rollback agent-coordinator <revision> -n suoke`