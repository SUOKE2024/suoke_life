# 索克生活知识图谱服务 Helm 部署指南

本文档介绍如何使用 Helm 部署索克生活知识图谱服务（Go 版本）。Helm 是 Kubernetes 的包管理器，可以简化应用的部署和管理。

## Helm 图表结构

知识图谱服务的 Helm 图表位于 `helm/knowledge-graph-service` 目录下，结构如下：

```
helm/knowledge-graph-service/
├── Chart.yaml              # 图表元数据
├── values.yaml             # 默认配置值
├── values.dev.yaml         # 开发环境配置值
├── values.prod.yaml        # 生产环境配置值
├── templates/              # 模板目录
│   ├── _helpers.tpl        # 模板助手函数
│   ├── configmap.yaml      # 配置映射模板
│   ├── deployment.yaml     # 部署模板
│   ├── ingress.yaml        # 入口模板
│   ├── NOTES.txt           # 使用说明
│   ├── secret.yaml         # 密钥模板
│   ├── service.yaml        # 服务模板
│   ├── serviceaccount.yaml # 服务账户模板
│   └── hpa.yaml            # 水平自动扩缩模板
└── charts/                 # 依赖图表目录
```

## 前置条件

- Kubernetes 集群（1.18+）
- Helm 3.0+
- `kubectl` 已配置连接到您的集群
- 已配置镜像仓库访问权限（如需访问私有镜像）

## 安装 Helm

如果尚未安装 Helm，请按照以下说明安装：

```bash
# macOS (使用 Homebrew)
brew install helm

# Ubuntu/Debian
curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
sudo apt-get install apt-transport-https --yes
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update
sudo apt-get install helm

# 验证安装
helm version
```

## 部署流程

### 添加 Helm 仓库

```bash
# 添加索克生活 Helm 仓库
helm repo add suoke https://charts.suoke.life
helm repo update
```

### 安装服务

```bash
# 使用默认配置安装
helm install knowledge-graph-service suoke/knowledge-graph-service

# 使用自定义配置文件安装
helm install knowledge-graph-service suoke/knowledge-graph-service -f custom-values.yaml

# 安装到特定命名空间
helm install knowledge-graph-service suoke/knowledge-graph-service --namespace suoke --create-namespace
```

### 升级服务

```bash
# 升级现有安装
helm upgrade knowledge-graph-service suoke/knowledge-graph-service

# 升级并使用自定义配置文件
helm upgrade knowledge-graph-service suoke/knowledge-graph-service -f custom-values.yaml
```

### 回滚服务

```bash
# 查看修订历史
helm history knowledge-graph-service

# 回滚到特定修订版本
helm rollback knowledge-graph-service 2  # 回滚到修订版本2
```

### 卸载服务

```bash
# 卸载释放
helm uninstall knowledge-graph-service
```

## 配置选项

以下是 `values.yaml` 中可配置的主要参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `image.repository` | 镜像仓库 | `suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/knowledge-graph-service-go` |
| `image.tag` | 镜像标签 | `latest` |
| `image.pullPolicy` | 镜像拉取策略 | `IfNotPresent` |
| `replicaCount` | 副本数量 | `1` |
| `autoscaling.enabled` | 启用自动扩缩 | `false` |
| `autoscaling.minReplicas` | 最小副本数 | `1` |
| `autoscaling.maxReplicas` | 最大副本数 | `5` |
| `autoscaling.targetCPUUtilizationPercentage` | 目标CPU使用率 | `80` |
| `service.type` | 服务类型 | `ClusterIP` |
| `service.port` | 服务端口 | `8080` |
| `ingress.enabled` | 启用入口 | `false` |
| `ingress.annotations` | 入口注解 | `{}` |
| `ingress.hosts` | 入口主机配置 | `[]` |
| `ingress.tls` | 入口TLS配置 | `[]` |
| `resources.limits.cpu` | CPU限制 | `500m` |
| `resources.limits.memory` | 内存限制 | `512Mi` |
| `resources.requests.cpu` | CPU请求 | `100m` |
| `resources.requests.memory` | 内存请求 | `128Mi` |
| `env` | 环境变量配置 | `{}` |
| `nodeSelector` | 节点选择器 | `{}` |
| `tolerations` | 容忍配置 | `[]` |
| `affinity` | 亲和性配置 | `{}` |
| `neo4j.uri` | Neo4j连接URI | `bolt://neo4j:7687` |
| `neo4j.username` | Neo4j用户名 | `neo4j` |
| `neo4j.password` | Neo4j密码 | `password` |
| `neo4j.existingSecret` | 已存在的Neo4j密钥名称 | `""` |
| `redis.uri` | Redis连接URI | `redis://redis:6379/0` |
| `redis.password` | Redis密码 | `""` |
| `redis.existingSecret` | 已存在的Redis密钥名称 | `""` |
| `milvus.enabled` | 启用Milvus | `false` |
| `milvus.host` | Milvus主机 | `milvus` |
| `milvus.port` | Milvus端口 | `19530` |
| `persistence.enabled` | 启用持久化 | `false` |
| `persistence.storageClass` | 存储类 | `""` |
| `persistence.size` | 存储大小 | `1Gi` |
| `livenessProbe` | 存活探针配置 | 见默认值 |
| `readinessProbe` | 就绪探针配置 | 见默认值 |
| `podAnnotations` | Pod注解 | `{}` |
| `podSecurityContext` | Pod安全上下文 | `{}` |
| `securityContext` | 容器安全上下文 | `{}` |

## 环境特定配置

### 开发环境

使用开发环境配置：

```bash
helm install knowledge-graph-service suoke/knowledge-graph-service -f values.dev.yaml
```

### 生产环境

使用生产环境配置：

```bash
helm install knowledge-graph-service suoke/knowledge-graph-service -f values.prod.yaml
```

## 自定义配置示例

### 基本配置

```yaml
# custom-values.yaml
replicaCount: 2
image:
  repository: suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/knowledge-graph-service-go
  tag: v1.0.0
  pullPolicy: Always

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 200m
    memory: 256Mi

env:
  LOG_LEVEL: info
  SERVER_PORT: "8080"
```

### 启用入口和TLS

```yaml
# ingress-values.yaml
ingress:
  enabled: true
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: kg-api.suoke.life
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: kg-api-tls
      hosts:
        - kg-api.suoke.life
```

### 启用自动扩缩

```yaml
# autoscaling-values.yaml
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80
```

### 配置外部Neo4j数据库

```yaml
# neo4j-values.yaml
neo4j:
  uri: bolt://neo4j.example.com:7687
  existingSecret: neo4j-credentials
```

## 本地开发图表

如果需要本地开发和测试 Helm 图表，可以按照以下步骤进行：

### 创建图表骨架

```bash
# 创建图表骨架
mkdir -p helm/knowledge-graph-service
cd helm/knowledge-graph-service
helm create .
```

### 测试图表

```bash
# 检查图表语法
helm lint .

# 渲染模板并查看输出
helm template knowledge-graph-service .

# 在本地Kubernetes集群上进行试运行
helm install --dry-run --debug knowledge-graph-service .

# 安装图表
helm install knowledge-graph-service . --namespace suoke --create-namespace
```

### 打包图表

```bash
# 打包图表
helm package .

# 创建或更新Helm仓库索引
helm repo index --url https://charts.suoke.life .
```

## 依赖管理

如果图表有依赖项，可以在 `Chart.yaml` 中指定：

```yaml
# Chart.yaml
apiVersion: v2
name: knowledge-graph-service
description: 索克生活知识图谱服务
type: application
version: 1.0.0
appVersion: 1.0.0
dependencies:
  - name: redis
    version: "~16.0.0"
    repository: "https://charts.bitnami.com/bitnami"
    condition: redis.internal.enabled
  - name: neo4j
    version: "~4.4.0"
    repository: "https://neo4j.github.io/helm-charts"
    condition: neo4j.internal.enabled
```

更新依赖项：

```bash
helm dependency update
```

## 故障排查

### 检查Pod状态

```bash
kubectl get pods -l app.kubernetes.io/name=knowledge-graph-service -n suoke
```

### 查看Pod日志

```bash
kubectl logs -l app.kubernetes.io/name=knowledge-graph-service -n suoke
```

### 查看部署事件

```bash
kubectl describe deployment knowledge-graph-service -n suoke
```

### 常见问题

1. **镜像拉取失败**
   - 检查镜像仓库凭证
   - 验证镜像是否存在

2. **Pod启动失败**
   - 检查资源限制是否合理
   - 查看容器日志以获取错误信息

3. **服务不可访问**
   - 验证服务是否正在运行
   - 检查入口配置
   - 验证网络策略

## 更多资源

- [Helm官方文档](https://helm.sh/docs/)
- [Kubernetes官方文档](https://kubernetes.io/docs/)
- [索克生活文档中心](https://docs.suoke.life/)