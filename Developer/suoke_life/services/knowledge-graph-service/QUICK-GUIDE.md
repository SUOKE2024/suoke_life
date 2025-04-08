# 索克生活知识图谱服务快速操作指南

## 前提条件

- Docker已安装并登录到阿里云容器服务
- kubectl已配置访问目标Kubernetes集群
- 有权限访问阿里云容器镜像仓库

## 快速操作步骤

### 1. 构建并推送AMD64镜像

```bash
# 进入项目目录
cd /path/to/suoke_life/services/knowledge-graph-service

# 构建AMD64镜像并推送到公共仓库
./scripts/build-amd64-push-public.sh
```

### 2. 部署到Kubernetes集群

```bash
# 使用Helm部署(全新部署或大版本升级)
./scripts/deploy-to-k8s.sh suoke-prod

# 或者只更新部署的镜像版本(小版本升级)
./scripts/update-k8s-deployment.sh suoke-prod
```

### 3. 检查部署状态

```bash
# 查看Pod状态
kubectl get pods -n suoke-prod -l app.kubernetes.io/instance=knowledge-graph

# 查看Pod日志
kubectl logs -n suoke-prod <pod-name>

# 查看部署详情
kubectl describe deployment -n suoke-prod knowledge-graph-service
```

### 4. 访问服务

```bash
# 端口转发(临时访问)
kubectl port-forward -n suoke-prod svc/knowledge-graph-service 8080:8080

# 然后在浏览器访问: http://localhost:8080
```

### 5. 常见问题处理

#### ImagePullBackOff

```bash
# 检查镜像是否存在
docker images | grep knowledge-graph-service

# 检查镜像拉取密钥
kubectl get secret -n suoke-prod | grep registry
```

#### CrashLoopBackOff

```bash
# 查看详细错误信息
kubectl logs -n suoke-prod <pod-name>

# 如果是架构问题，请确保使用正确的AMD64镜像
```

## 参考

详细信息请参阅以下文档:

- [README-DEPLOY.md](./README-DEPLOY.md) - 部署详细指南
- [SOLUTION-SUMMARY.md](./SOLUTION-SUMMARY.md) - 问题解决方案总结 