# Kubernetes 部署指南

## 环境要求

- Kubernetes 1.20+
- kubectl 配置完成
- Helm 3.0+
- 集群资源: 16核32GB+

## 部署步骤

### 1. 创建命名空间
```bash
kubectl create namespace suoke-life
kubectl config set-context --current --namespace=suoke-life
```

### 2. 配置存储
```bash
# 创建存储类
kubectl apply -f k8s/storage/

# 创建PVC
kubectl apply -f k8s/volumes/
```

### 3. 部署基础服务
```bash
# 部署数据库
kubectl apply -f k8s/databases/

# 部署消息队列
kubectl apply -f k8s/messaging/

# 等待基础服务就绪
kubectl wait --for=condition=ready pod -l app=postgres --timeout=300s
```

### 4. 部署微服务
```bash
# 部署智能体服务
kubectl apply -f k8s/agents/

# 部署业务服务
kubectl apply -f k8s/services/

# 部署网关
kubectl apply -f k8s/gateway/
```

### 5. 配置Ingress
```bash
# 部署Ingress控制器
kubectl apply -f k8s/ingress/

# 配置域名解析
echo "127.0.0.1 api.suoke.life" >> /etc/hosts
```

## 服务监控

### 查看服务状态
```bash
# 查看所有Pod
kubectl get pods

# 查看服务
kubectl get services

# 查看Ingress
kubectl get ingress
```

### 查看日志
```bash
# 查看Pod日志
kubectl logs -f deployment/xiaoai-service

# 查看多个Pod日志
kubectl logs -f -l app=xiaoai-service
```

## 扩缩容

### 手动扩缩容
```bash
# 扩容智能体服务
kubectl scale deployment xiaoai-service --replicas=3

# 查看扩容状态
kubectl get deployment xiaoai-service
```

### 自动扩缩容
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: xiaoai-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: xiaoai-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## 配置管理

### ConfigMap
```bash
# 创建配置
kubectl create configmap app-config --from-file=config/

# 更新配置
kubectl patch configmap app-config --patch='{"data":{"key":"value"}}'
```

### Secret
```bash
# 创建密钥
kubectl create secret generic app-secrets --from-literal=db-password=secret

# 查看密钥
kubectl get secrets
```

## 故障排除

### 常见问题

1. **Pod启动失败**
```bash
# 查看Pod详情
kubectl describe pod [pod-name]

# 查看事件
kubectl get events --sort-by=.metadata.creationTimestamp
```

2. **服务无法访问**
```bash
# 检查Service
kubectl get svc

# 检查Endpoints
kubectl get endpoints

# 端口转发测试
kubectl port-forward svc/xiaoai-service 8001:8001
```

3. **资源不足**
```bash
# 查看节点资源
kubectl top nodes

# 查看Pod资源使用
kubectl top pods
```

## 升级部署

```bash
# 滚动更新
kubectl set image deployment/xiaoai-service xiaoai-service=suoke/xiaoai:v2.0.0

# 查看更新状态
kubectl rollout status deployment/xiaoai-service

# 回滚
kubectl rollout undo deployment/xiaoai-service
```
