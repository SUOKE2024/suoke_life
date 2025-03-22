# 索克生活微服务 Kubernetes 部署指南

本文档提供了如何将索克生活微服务部署到Kubernetes集群的详细说明。

## 前提条件

1. 已安装`kubectl`命令行工具
2. 拥有可用的Kubernetes集群
3. 配置好的kubeconfig文件
4. 阿里云容器镜像仓库账号

## 集群架构

索克生活采用多节点Kubernetes集群架构，按功能划分不同节点：

### 节点角色

| 节点名称 | IP地址 | 角色 | 主要职责 |
|------------|----------|------|----------|
| suoke-core-np | 172.16.199.86 | 核心业务节点 | API网关、认证服务、用户服务 |
| suoke-ai-np | 172.16.199.136 | AI计算节点 | AI服务、RAG服务、向量数据库 |
| suoke-db-np | 172.16.199.88 | 数据存储节点 | MySQL、MongoDB、Redis数据库 |

### 集群入口点

集群API服务器地址: https://120.55.126.227:6443

外部流量通过主服务器(118.31.223.213)上的Nginx反向代理进入集群。

## 部署方式

索克生活微服务的部署支持两种方式：
1. 使用本地脚本手动部署
2. 通过GitHub Actions自动部署

## 1. 手动部署

### 准备kubeconfig文件

确保您的kubeconfig文件已正确配置并位于项目根目录:
- 开发环境: `kubeconfig.yaml`
- 生产环境: `kubeconfig-prod.yaml`

### 使用部署脚本

项目根目录提供了一个便捷的部署脚本`deploy-to-k8s.sh`，可以快速部署所有微服务或指定的微服务。

```bash
# 部署所有服务到开发环境
./deploy-to-k8s.sh

# 部署所有服务到生产环境
./deploy-to-k8s.sh prod

# 仅部署指定服务到开发环境
./deploy-to-k8s.sh -s api-gateway

# 仅部署指定服务到生产环境
./deploy-to-k8s.sh -s auth-service prod

# 部署到自定义命名空间
./deploy-to-k8s.sh -n custom-namespace
```

### 脚本参数说明

```
用法: ./deploy-to-k8s.sh [选项] [dev|prod]

选项:
  -h, --help     显示帮助信息
  -s, --service  仅部署指定服务 (api-gateway, auth-service, user-service)
  -n, --namespace 部署到指定命名空间

环境:
  dev            部署到开发环境 (默认)
  prod           部署到生产环境
```

## 2. 自动部署 (GitHub Actions)

项目已配置GitHub Actions工作流，可在代码推送到指定分支时自动部署到Kubernetes集群:

- 推送到`develop`分支: 自动部署到开发环境
- 推送到`main`分支: 自动部署到生产环境

### 配置GitHub Actions

要使GitHub Actions能够部署到您的Kubernetes集群，需要在GitHub仓库中配置Secrets:

1. `ALIYUN_USERNAME`: 阿里云容器镜像仓库用户名
2. `ALIYUN_PASSWORD`: 阿里云容器镜像仓库密码
3. `KUBE_CONFIG`: 开发环境Kubernetes配置
4. `KUBE_CONFIG_PROD`: 生产环境Kubernetes配置

有关详细设置指南，请参阅[GitHub Actions Kubernetes部署配置指南](./GITHUB_ACTIONS_K8S_SETUP.md)。

## 微服务架构

索克生活微服务架构包含以下主要组件:

| 服务名称 | 端口 | 部署节点 | 说明 |
|---------|-----|---------|------|
| api-gateway | 3000 | suoke-core-np | API网关，处理所有外部请求的入口点 |
| auth-service | 3001 | suoke-core-np | 认证服务，负责用户认证和授权 |
| user-service | 3002 | suoke-core-np | 用户服务，管理用户资料和相关功能 |
| mysql | 3306 | suoke-db-np | MySQL数据库 |
| redis | 6379 | suoke-db-np | Redis缓存 |
| mongodb | 27017 | suoke-db-np | MongoDB文档数据库 |
| vector-db | 6333 | suoke-ai-np | 向量数据库，用于相似性搜索 |
| rag-service | 8080 | suoke-ai-np | RAG检索增强生成服务 |
| ai-service | 8081 | suoke-ai-np | AI服务，处理大模型请求 |

## 节点选择器配置

为确保服务部署到正确的节点，使用`nodeSelector`配置。以下是示例YAML片段:

### 核心业务服务配置

```yaml
# API网关部署配置
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
spec:
  template:
    spec:
      nodeSelector:
        kubernetes.io/hostname: suoke-core-np
```

### AI服务配置

```yaml
# RAG服务部署配置
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rag-service
spec:
  template:
    spec:
      nodeSelector:
        kubernetes.io/hostname: suoke-ai-np
```

### 数据库服务配置

```yaml
# MongoDB部署配置
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mongodb
spec:
  template:
    spec:
      nodeSelector:
        kubernetes.io/hostname: suoke-db-np
```

## 监控和故障排除

### 查看服务状态

```bash
# 查看所有Pod状态
kubectl get pods -n suoke

# 查看特定服务的Pod详情
kubectl describe pod -n suoke -l app=api-gateway

# 查看服务日志
kubectl logs -n suoke -l app=api-gateway
```

### 常见问题排查

1. **Pod启动失败**
   ```bash
   kubectl describe pod -n suoke <pod-name>
   ```

2. **镜像拉取失败**
   - 检查`aliyun-registry-secret`是否正确创建
   - 验证镜像路径是否正确

3. **服务无法访问**
   ```bash
   kubectl get svc -n suoke
   kubectl describe svc -n suoke <service-name>
   ```

4. **查看详细日志**
   ```bash
   kubectl logs -n suoke <pod-name> --tail=100
   ```

## 扩展和缩容

根据需要调整副本数量:

```bash
# 扩展API网关到3个副本
kubectl scale deployment/api-gateway -n suoke --replicas=3

# 缩容认证服务到1个副本
kubectl scale deployment/auth-service -n suoke --replicas=1
```

## 更新和回滚

### 更新服务

使用`deploy-to-k8s.sh`脚本进行更新，或修改YAML文件后应用:

```bash
kubectl apply -f scripts/deploy/kubernetes/api-gateway.yaml -n suoke
```

### 回滚部署

如果新版本有问题，可以回滚到上一个稳定版本:

```bash
# 查看部署历史
kubectl rollout history deployment/api-gateway -n suoke

# 回滚到上一个版本
kubectl rollout undo deployment/api-gateway -n suoke

# 回滚到特定版本
kubectl rollout undo deployment/api-gateway -n suoke --to-revision=2
```

## 数据管理和备份

有关数据库备份和恢复的详细说明，请参阅[数据管理与备份指南](./DATA_MANAGEMENT.md)。

## 网络策略

为确保节点间通信安全，设置网络策略：

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: core-services-policy
  namespace: suoke
spec:
  podSelector:
    matchLabels:
      role: api-gateway
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: suoke
    - podSelector:
        matchLabels:
          role: auth
  egress:
  - to:
    - podSelector:
        matchLabels:
          role: database
```

## 集群资源监控

配置Prometheus和Grafana监控集群状态：

```bash
# 部署监控组件
kubectl apply -f scripts/deploy/kubernetes/monitoring/prometheus.yaml
kubectl apply -f scripts/deploy/kubernetes/monitoring/grafana.yaml

# 访问Grafana控制台
echo "Grafana URL: http://$(kubectl get svc -n monitoring grafana -o jsonpath='{.status.loadBalancer.ingress[0].ip}'):3000"
```

## 常见问题与解决方案

### 跨节点通信问题

如果服务之间无法通信，请检查:

1. 网络策略配置
2. 服务DNS解析
3. 节点间网络连通性

解决方案:

```bash
# 测试节点间连通性
kubectl run -it --rm --restart=Never busybox --image=busybox -- ping auth-service.suoke.svc.cluster.local

# 检查服务DNS解析
kubectl exec -it $(kubectl get pod -l app=api-gateway -o jsonpath='{.items[0].metadata.name}') -- nslookup auth-service.suoke.svc.cluster.local
``` 