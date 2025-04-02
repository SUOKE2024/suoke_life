# 玉米迷宫服务部署指南

本文档提供了玉米迷宫服务在Kubernetes环境中的部署方法，包括容器化、服务配置和运维指南。

## 1. 容器化配置

### 1.1 Docker镜像

服务镜像存储在阿里云容器服务中：

```
suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/corn-maze-service:latest
```

### 1.2 本地构建

要在本地构建镜像：

```bash
# 从项目根目录
cd services/corn-maze-service
docker build -t corn-maze-service:local .
```

### 1.3 本地开发环境

使用Docker Compose启动本地开发环境：

```bash
# 从项目根目录
cd services/corn-maze-service
docker-compose up -d

# 查看日志
docker-compose logs -f
```

## 2. Kubernetes部署

### 2.1 资源说明

本服务使用以下Kubernetes资源：

- **Deployment**: 2个副本的应用实例
- **Service**: 通过80端口提供HTTP服务，3101端口提供WebSocket服务
- **PersistentVolumeClaim**: 用于存储上传的文件和备份数据
- **ConfigMap**: 存储应用配置
- **Secret**: 存储敏感信息
- **VirtualService**: Istio配置
- **HorizontalPodAutoscaler**: 自动扩缩容配置
- **NetworkPolicy**: 网络访问控制策略
- **CronJob**: 数据库定期备份任务
- **ServiceMonitor**: Prometheus监控配置
- **PodDisruptionBudget**: 确保维护时的可用性

### 2.2 部署方法

使用自动化部署脚本：

```bash
# 从项目根目录
cd services/corn-maze-service
./scripts/deploy.sh v1.0.0  # 指定版本标签
```

或手动部署：

```bash
# 从项目根目录
cd services/corn-maze-service

# 构建并推送镜像
docker build -t suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/corn-maze-service:v1.0.0 .
docker push suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/corn-maze-service:v1.0.0

# 使用Kustomize应用配置
kubectl apply -k k8s/
```

### 2.3 配置更新

修改ConfigMap和其他配置后重新应用：

```bash
kubectl apply -f k8s/configmap.yaml -n suoke
```

如需重启Pod应用新配置：

```bash
kubectl rollout restart deployment/corn-maze-service -n suoke
```

## 3. 持续集成/持续部署

本服务使用ArgoCD进行GitOps部署：

- **应用名称**: corn-maze-service
- **源代码仓库**: https://gitlab.suoke.life/suoke/manifests.git
- **路径**: apps/corn-maze-service
- **目标命名空间**: suoke

配置文件位于`k8s/argocd-app.yaml`。

## 4. 监控与日志

### 4.1 Prometheus监控

服务暴露的指标端点：`/metrics`

主要监控指标：
- HTTP请求延迟
- WebSocket连接数
- Redis缓存命中率
- 数据库查询性能

通过ServiceMonitor配置，这些指标会自动被Prometheus收集。

### 4.2 日志收集

服务日志集成到集群的EFK/ELK堆栈，支持结构化日志输出。

### 4.3 健康检查

健康检查端点：`/health`

```bash
# 检查服务健康状态
curl http://api.suoke.life/api/corn-maze/health
```

## 5. 自动扩缩容

服务配置了HorizontalPodAutoscaler，可以根据CPU和内存使用率自动调整Pod数量：

- 最小副本数：2
- 最大副本数：5
- CPU利用率阈值：70%
- 内存利用率阈值：80%

可以通过以下命令查看HPA状态：

```bash
kubectl get hpa corn-maze-service -n suoke
```

## 6. 网络安全

服务使用NetworkPolicy限制入站和出站流量，只允许：
- 从Ingress控制器和Istio网关的入站HTTP和WebSocket流量
- 到MongoDB和Redis的出站数据库连接
- 到DNS服务的域名解析请求

## 7. 数据备份

服务配置了每日自动备份CronJob，在每天凌晨2点执行：
- 备份MongoDB数据库
- 将备份上传到阿里云OSS
- 保留最近10个备份副本

手动触发备份：

```bash
kubectl create job --from=cronjob/corn-maze-db-backup corn-maze-db-backup-manual -n suoke
```

## 8. 常见问题与故障排查

### 8.1 Pod启动失败

检查事件和日志：

```bash
kubectl describe pod -l app=corn-maze-service -n suoke
kubectl logs -l app=corn-maze-service -n suoke
```

### 8.2 无法连接到数据库

验证Secret配置是否正确：

```bash
kubectl get secret corn-maze-secrets -n suoke -o yaml
```

### 8.3 WebSocket连接问题

确认Service中的WebSocket端口配置：

```bash
kubectl get svc corn-maze-service -n suoke -o yaml
```

### 8.4 性能优化

- 增加副本数可提高吞吐量：`kubectl scale deployment/corn-maze-service --replicas=3 -n suoke`
- 调整资源限制：修改`k8s/deployment.yaml`中的资源配置
- 可调整HPA配置以实现更精细的自动扩缩容

### 8.5 自动扩缩容问题

检查HPA状态和事件：

```bash
kubectl describe hpa corn-maze-service -n suoke
```

## 9. 维护操作

### 9.1 滚动更新

更新镜像版本：

```bash
kubectl set image deployment/corn-maze-service corn-maze-service=suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/corn-maze-service:v1.0.1 -n suoke
```

### 9.2 回滚部署

如需回滚到之前的版本：

```bash
kubectl rollout undo deployment/corn-maze-service -n suoke
```

或回滚到特定版本：

```bash
kubectl rollout undo deployment/corn-maze-service --to-revision=2 -n suoke
```

### 9.3 维护窗口配置

服务配置了PodDisruptionBudget，确保在节点维护期间至少有1个Pod可用，防止服务中断。

## 10. 安全注意事项

- 生产环境应更新`k8s/secrets.yaml`中的敏感信息
- 配置防火墙规则以限制API访问
- 使用安全传输层(TLS)保护API通信
- 定期轮换密钥和证书 