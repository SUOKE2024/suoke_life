# ArgoCD使用指南

## 目录

- [1. ArgoCD简介](#1-argocd简介)
- [2. 安装与配置](#2-安装与配置)
- [3. 应用部署](#3-应用部署)
- [4. 与CI/CD集成](#4-与cicd集成)
- [5. 最佳实践](#5-最佳实践)
- [6. 常见问题](#6-常见问题)

## 1. ArgoCD简介

ArgoCD是一个声明式的GitOps持续交付工具，用于Kubernetes应用程序。它遵循GitOps原则，将Kubernetes清单文件存储在Git仓库中，并自动将这些清单应用于Kubernetes集群。

### 主要特点

- **GitOps模式**：应用配置存储为Git仓库中的清单文件，确保配置的一致性、可追溯性和可恢复性
- **自动同步**：自动检测并应用Git仓库中的更改到目标环境
- **多集群管理**：可以管理多个Kubernetes集群
- **回滚能力**：支持快速回滚到之前的稳定版本
- **Web界面**：提供直观的用户界面展示应用状态和历史

### 架构

ArgoCD由以下组件组成：

- **API服务器**：对外暴露API接口，处理请求和用户界面
- **仓库服务器**：维护Git仓库缓存
- **应用控制器**：不断监控应用程序并将当前状态与目标状态进行比较

## 2. 安装与配置

### 前提条件

- Kubernetes集群
- kubectl命令行工具
- argocd命令行工具（可选）

### 快速安装

我们提供了自动化安装脚本，可以快速安装和配置ArgoCD：

```bash
# 安装默认配置
./scripts/install_argocd.sh

# 自定义安装配置
./scripts/install_argocd.sh --namespace argocd --ingress-host argocd.suoke.life --ingress-class nginx
```

### 手动安装

如果需要手动安装，可以按照以下步骤操作：

1. 创建命名空间：
   ```bash
   kubectl create namespace argocd
   ```

2. 应用ArgoCD清单：
   ```bash
   kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
   ```

3. 配置Ingress（可选）：
   ```bash
   # 参考scripts/install_argocd.sh中的Ingress配置
   ```

4. 获取管理员密码：
   ```bash
   kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
   ```

### 访问Web界面

- 如果配置了Ingress，可以通过配置的域名访问：https://argocd.example.com
- 否则，可以使用端口转发：
  ```bash
  kubectl port-forward svc/argocd-server -n argocd 8080:443
  ```
  然后通过浏览器访问：https://localhost:8080

## 3. 应用部署

### 应用定义

ArgoCD通过Application资源来定义应用部署。Application资源指定了Git仓库、目标集群和命名空间等信息。

基本的Application定义示例：

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: api-gateway-dev
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/suoke/life-backend.git
    targetRevision: HEAD
    path: services/api-gateway/k8s/overlays/dev
  destination:
    server: https://kubernetes.default.svc
    namespace: suoke-dev
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
```

### 应用集 (ApplicationSet)

ApplicationSet允许您批量创建Application资源，适用于需要为多个环境或服务创建Application的场景。

示例ApplicationSet：

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: suoke-microservices
  namespace: argocd
spec:
  generators:
  - matrix:
      generators:
      - list:
          elements:
            - environment: dev
            - environment: staging
            - environment: prod
      - list:
          elements:
            - name: api-gateway
              path: services/api-gateway/k8s/overlays
            - name: auth-service
              path: services/auth-service/k8s/overlays
  template:
    metadata:
      name: '{{name}}-{{environment}}'
    spec:
      project: default
      source:
        repoURL: https://github.com/suoke/life-backend.git
        targetRevision: HEAD
        path: '{{path}}/{{environment}}'
      destination:
        server: https://kubernetes.default.svc
        namespace: suoke-{{environment}}
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
        syncOptions:
        - CreateNamespace=true
```

### 部署应用

使用我们提供的脚本部署ArgoCD应用：

```bash
./scripts/setup_argocd_apps.sh argocd.suoke.life
```

或手动使用kubectl应用应用定义：

```bash
kubectl apply -f argocd-apps/suoke-microservices-appset.yaml -n argocd
```

## 4. 与CI/CD集成

### 集成方式

我们的CI/CD工作流已经与ArgoCD集成，流程如下：

1. 开发人员提交代码到Git仓库
2. GitHub Actions触发CI流程（构建、测试、生成镜像）
3. CI工作流更新Kubernetes清单中的镜像版本，并提交回仓库
4. ArgoCD检测到Git仓库变更，自动将更改同步到Kubernetes集群

### 迁移现有服务到ArgoCD

我们提供了自动化迁移工作流，可以将现有服务迁移到ArgoCD：

1. 在GitHub仓库中运行`migrate-to-argocd`工作流
2. 选择要迁移的服务或服务组
3. 工作流将生成ArgoCD应用定义并更新CI/CD配置

迁移后，您需要在GitHub添加以下密钥：

- `ARGOCD_SERVER`: ArgoCD服务器地址
- `ARGOCD_USERNAME`: ArgoCD用户名
- `ARGOCD_PASSWORD`: ArgoCD密码

## 5. 最佳实践

### GitOps工作流

1. **声明式配置**
   - 所有配置文件存放在Git仓库中
   - 避免手动修改集群状态

2. **环境分离**
   - 使用overlay目录结构（base、dev、staging、prod）
   - 每个环境使用单独的ArgoCD应用

3. **自动化同步**
   - 启用自动同步和自愈功能
   - 对于生产环境，可以考虑使用手动同步或同步窗口

4. **资源结构**
   - 使用kustomize管理不同环境的配置差异
   - 为每个微服务设置单独的应用定义

### 健康检查配置

确保您的应用程序配置了适当的健康检查，ArgoCD会使用这些检查来确定应用程序是否健康：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
spec:
  template:
    spec:
      containers:
      - name: api-gateway
        livenessProbe:
          httpGet:
            path: /health
            port: 80
        readinessProbe:
          httpGet:
            path: /health
            port: 80
```

## 6. 常见问题

### 同步失败

**问题**: 应用同步失败

**解决方案**:
1. 检查应用状态和同步日志：
   ```bash
   argocd app get <应用名称>
   ```
2. 确认Kubernetes清单是否有效
3. 检查资源依赖关系，可能需要调整同步顺序

### 资源不被清理

**问题**: 删除的资源没有从集群中删除

**解决方案**:
1. 确保启用了prune选项：
   ```yaml
   syncPolicy:
     automated:
       prune: true
   ```
2. 手动运行同步并指定prune选项：
   ```bash
   argocd app sync <应用名称> --prune
   ```

### 获取更多帮助

如果遇到其他问题，可以参考：

- [ArgoCD官方文档](https://argo-cd.readthedocs.io/)
- [GitHub Issues](https://github.com/argoproj/argo-cd/issues)
- 内部支持: 联系索克生活开发运维团队