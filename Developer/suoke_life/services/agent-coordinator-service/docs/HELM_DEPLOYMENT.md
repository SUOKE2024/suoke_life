# Agent Coordinator Service Helm部署指南

## 概述

本文档提供Agent Coordinator Service使用Helm进行部署的详细指南。Helm Chart位于`helm/agent-coordinator`目录下，提供了全面的配置选项用于不同环境的部署。

## 目录

- [前提条件](#前提条件)
- [部署流程](#部署流程)
  - [手动部署](#手动部署)
  - [GitOps部署](#gitops部署)
- [配置说明](#配置说明)
- [环境特定配置](#环境特定配置)
- [监控与可观测性](#监控与可观测性)
- [故障排除](#故障排除)

## 前提条件

- Kubernetes集群（版本1.19+）
- Helm 3.7+
- kubectl（配置访问目标集群）
- 如需启用特定功能，需安装以下组件：
  - Prometheus Operator (监控)
  - Istio (服务网格)
  - Velero (备份)

## 部署流程

### 手动部署

1. **检查配置**

   首先检查Chart的默认配置是否满足需求：

   ```bash
   cd /Users/songxu/Developer/suoke_life/services/agent-coordinator-service
   helm lint helm/agent-coordinator
   ```

2. **测试渲染模板**

   ```bash
   helm template helm/agent-coordinator --debug
   ```

3. **部署到测试环境**

   ```bash
   helm upgrade --install agent-coordinator-test ./helm/agent-coordinator \
     --namespace suoke-test \
     --set environment=testing \
     --set replicaCount=1
   ```

4. **部署到生产环境**

   ```bash
   helm upgrade --install agent-coordinator ./helm/agent-coordinator \
     --namespace suoke \
     --set replicaCount=3
   ```

5. **使用自定义values文件**

   ```bash
   helm upgrade --install agent-coordinator ./helm/agent-coordinator \
     --namespace suoke \
     -f custom-values.yaml
   ```

### GitOps部署

使用ArgoCD进行GitOps部署：

1. **应用ArgoCD应用资源**

   ```bash
   kubectl apply -f argocd-application.yaml
   ```

2. **检查同步状态**

   ```bash
   argocd app get agent-coordinator
   ```

3. **手动触发同步**（通常不需要，ArgoCD会自动同步）

   ```bash
   argocd app sync agent-coordinator
   ```

## 配置说明

以下是关键配置参数及其用途：

### 基础配置

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `nameOverride` | 重写应用名称 | `""` |
| `fullnameOverride` | 重写完整应用名称 | `""` |
| `environment` | 环境标识 | `production` |
| `replicaCount` | Pod副本数 | `3` |
| `image.repository` | 镜像仓库 | `suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/agent-coordinator-service` |
| `image.tag` | 镜像标签 | `1.2.0` |
| `image.pullPolicy` | 镜像拉取策略 | `IfNotPresent` |
| `deploymentStrategy.type` | 部署策略类型 | `RollingUpdate` |

### 资源配置

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `resources.requests.cpu` | CPU请求 | `500m` |
| `resources.requests.memory` | 内存请求 | `512Mi` |
| `resources.limits.cpu` | CPU限制 | `1000m` |
| `resources.limits.memory` | 内存限制 | `1Gi` |

### 自动伸缩配置

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `autoscaling.enabled` | 是否启用自动伸缩 | `true` |
| `autoscaling.minReplicas` | 最小副本数 | `2` |
| `autoscaling.maxReplicas` | 最大副本数 | `5` |
| `autoscaling.metrics` | 伸缩指标配置 | （见values.yaml） |
| `autoscaling.behavior` | 伸缩行为配置 | （见values.yaml） |

### 存储配置

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `persistence.enabled` | 是否启用持久化存储 | `true` |
| `persistence.storageClass` | 存储类 | `suoke-standard` |
| `persistence.size` | 存储大小 | `10Gi` |
| `persistence.accessMode` | 访问模式 | `ReadWriteOnce` |

### 监控配置

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `monitoring.enabled` | 是否启用监控 | `true` |
| `monitoring.serviceMonitor.enabled` | 是否启用ServiceMonitor | `true` |
| `monitoring.serviceMonitor.interval` | 抓取间隔 | `15s` |
| `monitoring.serviceMonitor.scrapeTimeout` | 抓取超时 | `10s` |

### 服务网格配置

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `istio.enabled` | 是否启用Istio集成 | `true` |
| `istio.virtualService.enabled` | 是否创建VirtualService | `true` |
| `istio.destinationRule.enabled` | 是否创建DestinationRule | `true` |

## 环境特定配置

以下是不同环境的配置示例：

### 开发环境

```yaml
environment: development
replicaCount: 1
resources:
  requests:
    cpu: "200m"
    memory: "256Mi"
  limits:
    cpu: "500m"
    memory: "512Mi"
autoscaling:
  enabled: false
persistence:
  enabled: false
monitoring:
  enabled: false
istio:
  enabled: false
backup:
  enabled: false
```

### 测试环境

```yaml
environment: testing
replicaCount: 2
autoscaling:
  enabled: true
  minReplicas: 1
  maxReplicas: 3
persistence:
  enabled: true
  size: "5Gi"
env:
  - name: LOG_LEVEL
    value: "debug"
```

### 生产环境

```yaml
environment: production
replicaCount: 3
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
resources:
  requests:
    cpu: "1000m"
    memory: "1Gi"
  limits:
    cpu: "2000m"
    memory: "2Gi"
persistence:
  enabled: true
  storageClass: "suoke-ssd-premium"
  size: "20Gi"
```

## 监控与可观测性

部署后，可通过以下方式访问监控指标：

1. **Prometheus指标**

   ```
   http://<service-url>:<metrics-port>/metrics
   ```

2. **Grafana仪表盘**

   导入位于`monitoring/dashboards/agent-coordinator.json`的仪表盘

3. **健康检查端点**

   - 就绪探针: `http://<service-url>/health/readiness`
   - 存活探针: `http://<service-url>/health/liveness`
   - 启动探针: `http://<service-url>/health/startup`

## 故障排除

如果部署过程中遇到问题，可参考以下排查步骤：

1. **检查Pod状态**

   ```bash
   kubectl get pods -n <namespace> -l app=agent-coordinator
   ```

2. **查看Pod日志**

   ```bash
   kubectl logs -n <namespace> <pod-name>
   ```

3. **检查事件**

   ```bash
   kubectl get events -n <namespace> --sort-by='.lastTimestamp'
   ```

4. **检查资源创建**

   ```bash
   kubectl get all,pvc,cm,secret -n <namespace> -l app=agent-coordinator
   ```

5. **常见问题**

   - **Pod无法启动**: 检查资源限制、镜像标签是否正确
   - **健康检查失败**: 检查服务配置和日志
   - **PVC无法绑定**: 检查存储类和存储容量
   - **网络连接问题**: 检查NetworkPolicy和服务配置