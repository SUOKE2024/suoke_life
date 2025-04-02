# 索克生活 API 网关 Helm Chart

这个 Helm Chart 用于在 Kubernetes 集群中部署和配置索克生活平台的 API 网关服务。

## 简介

API 网关服务是索克生活平台微服务架构的入口点，负责路由转发、认证授权、流量控制等功能。该 Helm Chart 提供了灵活的配置选项，以适应不同的部署环境和场景。

## 前提条件

- Kubernetes 1.19+
- Helm 3.2.0+
- 持久卷供应商支持（用于日志和配置持久化）
- 如启用 ServiceMonitor，需要安装 Prometheus Operator
- 如启用 Istio 集成，需要安装 Istio 服务网格

## 安装

### 添加仓库

```bash
helm repo add suoke https://charts.suoke.life
helm repo update
```

### 使用默认配置安装

```bash
helm install api-gateway suoke/api-gateway --namespace suoke-system --create-namespace
```

### 使用自定义配置安装

```bash
helm install api-gateway suoke/api-gateway \
  --namespace suoke-system \
  --create-namespace \
  --values my-values.yaml
```

### 使用特定版本安装

```bash
helm install api-gateway suoke/api-gateway \
  --namespace suoke-system \
  --version 0.1.0 \
  --create-namespace
```

## 卸载

```bash
helm uninstall api-gateway -n suoke-system
```

**注意**: 这将删除所有相关资源，包括配置映射、密钥和持久卷声明。如需保留数据，请确保提前备份或设置合适的保留策略。

## 配置

下表列出了 API 网关 Helm Chart 的可配置参数及其默认值。

### 全局配置

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `replicaCount` | Pod 副本数 | `2` |
| `image.repository` | 容器镜像仓库 | `suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/api-gateway` |
| `image.pullPolicy` | 镜像拉取策略 | `IfNotPresent` |
| `image.tag` | 镜像标签 | `latest` |
| `imagePullSecrets` | 镜像拉取密钥 | `[]` |
| `nameOverride` | 覆盖资源名称 | `""` |
| `fullnameOverride` | 覆盖资源全名 | `""` |
| `environment` | 运行环境 | `production` |
| `deploymentStrategy` | 部署策略 | `{"type":"RollingUpdate", "rollingUpdate":{"maxSurge":1, "maxUnavailable":0}}` |
| `terminationGracePeriodSeconds` | 终止宽限期(秒) | `30` |

### 标签和注解

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `commonLabels` | 应用到所有资源的标签 | `{}` |
| `podLabels` | 应用到 Pod 的额外标签 | `{}` |
| `deploymentAnnotations` | 应用到 Deployment 的注解 | `{}` |
| `podAnnotations` | 应用到 Pod 的注解 | `{}` |

### 安全上下文和权限

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `serviceAccount.create` | 是否创建服务账号 | `true` |
| `serviceAccount.annotations` | 服务账号注解 | `{}` |
| `serviceAccount.name` | 服务账号名称 | `""` |
| `podSecurityContext` | Pod 安全上下文 | `{"fsGroup":1000}` |
| `securityContext` | 容器安全上下文 | `{"runAsUser":1000, "runAsNonRoot":true, "readOnlyRootFilesystem":false, "allowPrivilegeEscalation":false}` |

### 资源管理

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `resources` | 容器资源限制 | `{"limits":{"cpu":"500m", "memory":"512Mi"}, "requests":{"cpu":"100m", "memory":"128Mi"}}` |
| `nodeSelector` | 节点选择器 | `{}` |
| `tolerations` | 节点容忍配置 | `[]` |
| `affinity` | 亲和性配置 | `{}` |
| `topologySpreadConstraints` | 拓扑分布约束 | `[]` |

### 服务配置

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `service.type` | 服务类型 | `ClusterIP` |
| `service.port` | 服务端口 | `80` |
| `service.targetPort` | 容器目标端口 | `3000` |
| `service.annotations` | 服务注解 | `{}` |

### 持久化存储

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `persistence.logs.enabled` | 是否启用日志持久化 | `true` |
| `persistence.logs.size` | 日志卷大小 | `2Gi` |
| `persistence.logs.storageClass` | 日志卷存储类 | `""` |
| `persistence.logs.accessMode` | 日志卷访问模式 | `ReadWriteOnce` |
| `persistence.config.enabled` | 是否启用配置持久化 | `false` |
| `persistence.config.size` | 配置卷大小 | `1Gi` |
| `persistence.config.storageClass` | 配置卷存储类 | `""` |
| `persistence.config.accessMode` | 配置卷访问模式 | `ReadWriteOnce` |
| `persistence.register.enabled` | 是否启用注册表持久化 | `false` |
| `persistence.register.size` | 注册表卷大小 | `1Gi` |
| `persistence.register.storageClass` | 注册表卷存储类 | `""` |
| `persistence.register.accessMode` | 注册表卷访问模式 | `ReadWriteOnce` |

### 探针配置

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `livenessProbe.enabled` | 是否启用存活探针 | `true` |
| `livenessProbe.path` | 存活探针路径 | `/health/live` |
| `livenessProbe.initialDelaySeconds` | 初始延迟秒数 | `30` |
| `livenessProbe.periodSeconds` | 探测周期秒数 | `10` |
| `livenessProbe.timeoutSeconds` | 探测超时秒数 | `5` |
| `livenessProbe.failureThreshold` | 失败阈值 | `3` |
| `readinessProbe.enabled` | 是否启用就绪探针 | `true` |
| `readinessProbe.path` | 就绪探针路径 | `/health/ready` |
| `readinessProbe.initialDelaySeconds` | 初始延迟秒数 | `10` |
| `readinessProbe.periodSeconds` | 探测周期秒数 | `10` |
| `readinessProbe.timeoutSeconds` | 探测超时秒数 | `5` |
| `readinessProbe.failureThreshold` | 失败阈值 | `3` |
| `startupProbe.enabled` | 是否启用启动探针 | `true` |
| `startupProbe.path` | 启动探针路径 | `/health/startup` |
| `startupProbe.initialDelaySeconds` | 初始延迟秒数 | `5` |
| `startupProbe.periodSeconds` | 探测周期秒数 | `5` |
| `startupProbe.timeoutSeconds` | 探测超时秒数 | `3` |
| `startupProbe.failureThreshold` | 失败阈值 | `30` |

### 特性功能开关

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `features.prometheus` | 是否启用Prometheus指标 | `true` |
| `features.istio` | 是否启用Istio集成 | `false` |
| `features.linkerd` | 是否启用Linkerd集成 | `false` |
| `features.admin` | 是否启用管理员API | `false` |
| `features.config` | 是否启用配置API | `true` |
| `features.debug` | 是否启用调试模式 | `false` |
| `features.otel` | 是否启用OpenTelemetry | `false` |
| `features.persistentLogs` | 是否启用持久化日志 | `true` |
| `features.serviceDiscovery` | 是否启用服务发现 | `false` |
| `features.vault` | 是否启用Vault集成 | `false` |

### 自动伸缩

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `autoscaling.enabled` | 是否启用HPA | `false` |
| `autoscaling.minReplicas` | 最小副本数 | `2` |
| `autoscaling.maxReplicas` | 最大副本数 | `5` |
| `autoscaling.targetCPUUtilizationPercentage` | 目标CPU使用率 | `80` |
| `autoscaling.targetMemoryUtilizationPercentage` | 目标内存使用率 | `80` |
| `autoscaling.behavior` | 伸缩行为配置 | `{"scaleDown":{"stabilizationWindowSeconds":300, "policies":[{"type":"Pods", "value":1, "periodSeconds":60}]}, "scaleUp":{"stabilizationWindowSeconds":0, "policies":[{"type":"Pods", "value":2, "periodSeconds":60}]}}` |

### 入口配置

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `ingress.enabled` | 是否启用入口 | `false` |
| `ingress.className` | 入口类名称 | `nginx` |
| `ingress.annotations` | 入口注解 | `{}` |
| `ingress.hosts` | 入口主机列表 | `[]` |
| `ingress.tls` | 入口TLS配置 | `[]` |

### Istio 服务网格配置

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `istio.enabled` | 是否启用Istio | `false` |
| `istio.gateway.enabled` | 是否创建Gateway | `false` |
| `istio.gateway.name` | Gateway名称 | `api-gateway` |
| `istio.gateway.host` | Gateway主机 | `api.suoke.life` |
| `istio.virtualService.enabled` | 是否创建VirtualService | `false` |
| `istio.virtualService.gateway` | VirtualService网关 | `api-gateway` |
| `istio.virtualService.hosts` | VirtualService主机列表 | `["api.suoke.life"]` |
| `istio.destinationRule.enabled` | 是否创建DestinationRule | `false` |
| `istio.destinationRule.trafficPolicy` | 流量策略 | `{}` |

### Vault 集成

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `vault.enabled` | 是否启用Vault | `false` |
| `vault.role` | Vault角色 | `api-gateway` |
| `vault.host` | Vault主机 | `vault` |
| `vault.port` | Vault端口 | `8200` |
| `vault.secrets` | Vault密钥配置 | `{}` |

### 网络策略

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `networkPolicy.enabled` | 是否启用网络策略 | `false` |
| `networkPolicy.ingressRules` | 入站规则 | `[{"from":[{"namespaceSelector":{"matchLabels":{"name":"kube-system"}}},{"namespaceSelector":{"matchLabels":{"name":"istio-system"}}}]}]` |
| `networkPolicy.egressRules` | 出站规则 | `[{"to":[{"ipBlock":{"cidr":"0.0.0.0/0", "except":["169.254.169.254/32"]}},{"namespaceSelector":{"matchLabels":{"name":"vault"}}}]}]` |

### 监控配置

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `serviceMonitor.enabled` | 是否启用ServiceMonitor | `false` |
| `serviceMonitor.interval` | 抓取间隔 | `15s` |
| `serviceMonitor.labels` | ServiceMonitor标签 | `{}` |
| `prometheus.port` | Prometheus指标端口 | `9090` |
| `prometheus.path` | Prometheus指标路径 | `/metrics` |

### 自定义配置和环境变量

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `env` | 环境变量列表 | `[]` |
| `extraVolumes` | 额外卷配置 | `[]` |
| `extraVolumeMounts` | 额外卷挂载 | `[]` |
| `sidecars` | 辅助容器配置 | `[]` |
| `lifecycle` | 容器生命周期钩子 | `{}` |
| `initContainer.image.repository` | 初始化容器镜像仓库 | `alpine` |
| `initContainer.image.tag` | 初始化容器镜像标签 | `3.14` |
| `initContainer.image.pullPolicy` | 初始化容器拉取策略 | `IfNotPresent` |

## 使用案例

### 基础配置

```yaml
replicaCount: 3
image:
  repository: suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/api-gateway
  tag: "1.0.0"
  pullPolicy: Always
```

### 启用自动伸缩

```yaml
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 70
```

### 配置持久化存储

```yaml
persistence:
  logs:
    enabled: true
    size: 5Gi
    storageClass: "managed-nfs-storage"
  config:
    enabled: true
    size: 1Gi
    storageClass: "managed-nfs-storage"
```

### 启用Prometheus监控

```yaml
features:
  prometheus: true
serviceMonitor:
  enabled: true
  interval: 10s
  labels:
    release: prometheus
```

### 启用Istio集成

```yaml
features:
  istio: true
istio:
  enabled: true
  gateway:
    enabled: true
    name: api-gateway
    host: api.suoke.life
  virtualService:
    enabled: true
    hosts:
      - api.suoke.life
```

### 配置Vault集成

```yaml
features:
  vault: true
vault:
  enabled: true
  role: api-gateway
  secrets:
    config:
      path: secret/data/api-gateway
      template: |
        {{- with secret "secret/data/api-gateway" -}}
        {
          "JWT_SECRET": "{{ .Data.data.jwt_secret }}",
          "API_KEYS": {{ .Data.data.api_keys | toJSON }}
        }
        {{- end -}}
```

### 高可用性配置

```yaml
replicaCount: 5
podDisruptionBudget:
  enabled: true
  minAvailable: 3
topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: kubernetes.io/hostname
    whenUnsatisfiable: DoNotSchedule
    labelSelector:
      matchLabels:
        app.kubernetes.io/name: api-gateway
deploymentStrategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0
resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi
```

## 故障排除

### 常见问题

1. **Pod 启动失败**:
   - 检查 Pod 日志: `kubectl logs -f <pod-name> -n <namespace>`
   - 检查描述: `kubectl describe pod <pod-name> -n <namespace>`
   - 确认资源限制是否合理

2. **健康检查失败**:
   - 检查健康端点是否正确配置
   - 检查容器端口和服务端口映射是否正确
   - 调整初始延迟和超时设置

3. **持久卷问题**:
   - 确认集群中存在适当的存储类
   - 检查 PVC 状态: `kubectl get pvc -n <namespace>`
   - 检查存储供应商的配置和限制

4. **Vault 集成问题**:
   - 确认 Vault 服务可访问
   - 检查 Vault 角色权限和策略
   - 查看 Vault Agent 注入日志

### 获取更多帮助

如需更多帮助，请联系索克生活技术支持团队:

- 电子邮件: devops@suoke.life
- 问题跟踪: https://github.com/suoke/api-gateway/issues

## 贡献和开发

欢迎贡献代码和改进 Helm Chart。请参考 [贡献指南](https://github.com/suoke/api-gateway/CONTRIBUTING.md) 了解更多信息。

## 许可证

API 网关 Helm Chart 基于 [Apache 2.0 许可证](https://www.apache.org/licenses/LICENSE-2.0) 发布。