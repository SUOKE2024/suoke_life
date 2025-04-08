# Kubernetes 部署指南

本文档提供了在 Kubernetes 集群中部署和管理 Agent Coordinator Service 的详细说明。

## 目录结构

Agent Coordinator Service 的 Kubernetes 配置文件组织如下：

```
k8s/
├── base/                    # 基础配置
│   ├── configmap.yaml       # 配置映射
│   ├── deployment.yaml      # 基础部署
│   ├── kustomization.yaml   # 基础 kustomization 文件
│   └── service.yaml         # 服务定义
├── overlays/                # 环境特定覆盖
    ├── dev/                 # 开发环境
    │   ├── kustomization.yaml
    │   └── patches/         # 开发环境补丁
    │       ├── amd64-node-selector.yaml   # 节点选择器
    │       └── deployment-patch.yaml      # 部署补丁
    └── prod/                # 生产环境
        ├── hpa.yaml         # 水平 Pod 自动缩放
        ├── kustomization.yaml
        ├── network-policy.yaml    # 网络策略
        ├── pdb.yaml         # Pod 中断预算
        ├── pvc.yaml         # 持久卷声明
        └── patches/         # 生产环境补丁
            ├── amd64-node-selector.yaml   # 节点选择器
            └── deployment-patch.yaml      # 部署补丁
```

## 部署流程

### 手动部署方式

以下是手动部署 Agent Coordinator Service 的步骤：

#### 1. 开发环境部署

```bash
# 切换到服务目录
cd services/agent-coordinator-service

# 应用开发环境配置
kubectl apply -k k8s/overlays/dev
```

#### 2. 生产环境部署

```bash
# 切换到服务目录
cd services/agent-coordinator-service

# 应用生产环境配置
kubectl apply -k k8s/overlays/prod
```

### 使用 ArgoCD 部署

Agent Coordinator Service 支持使用 ArgoCD 进行 GitOps 部署：

```bash
# 部署 ArgoCD 应用
kubectl apply -f argocd-application.yaml
```

这将创建 ArgoCD 应用，自动从 Git 仓库同步 Kubernetes 配置。

## 环境特定配置

### 开发环境

- 单实例部署
- 资源限制：CPU 500m、内存 512Mi
- 日志级别：debug

### 生产环境

- 多实例部署（默认 2 个副本）
- 资源限制：CPU 1、内存 1Gi
- 自动扩缩容（HPA）：基于 CPU 和内存使用率
- Pod 中断预算（PDB）：保证高可用性
- 持久存储：使用 PVC 存储数据
- 网络策略：限制入站和出站流量

## 配置管理

服务配置通过 ConfigMap 注入到容器中，位于 `/etc/agent-coordinator/config.yaml`。可以通过更新 ConfigMap 并重启 Pod 来更新配置。

### 配置示例

```yaml
server:
  port: 8080
  host: "0.0.0.0"
  
logging:
  level: "info"
  format: "json"
  
services:
  auth_service:
    url: "http://auth-service/api/v1"
  
  knowledge_graph_service:
    url: "http://knowledge-graph-service/api/v1"
  
database:
  type: "sqlite"
  connection: "/app/data/agent-coordinator.db"
```

## 持久化

生产环境使用持久卷存储数据，确保在 Pod 重启或重新调度时数据不会丢失。数据目录挂载在容器的 `/app/data` 路径。

## 监控和日志

- 健康检查：服务暴露 `/health` 端点用于监控
- 日志：所有日志流输出到标准输出，可由 Kubernetes 日志收集系统（如 Elasticsearch、Fluentd 和 Kibana - EFK）收集

## 故障排除

常见问题及解决方案：

### Pod 无法启动

检查事件和日志：

```bash
kubectl get events -n <namespace>
kubectl logs -f <pod-name> -n <namespace>
```

### 配置问题

检查 ConfigMap 是否正确挂载：

```bash
kubectl describe pod <pod-name> -n <namespace>
```

### 网络问题

检查网络策略是否过于严格：

```bash
kubectl describe networkpolicy -n <namespace>
```

## 安全建议

1. 定期更新容器镜像，确保包含最新的安全补丁
2. 使用网络策略限制服务间通信
3. 配置适当的资源限制，防止资源耗尽攻击
4. 定期审查服务访问日志，监控异常行为