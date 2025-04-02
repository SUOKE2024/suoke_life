# Agent Coordinator Service 部署指南

## 部署架构图

```
                           +-----------------+
                           |                 |
                           |  API 网关       |
                           |                 |
                           +--------+--------+
                                    |
                                    | HTTP/HTTPS
                                    v
+----------------+        +---------+---------+        +----------------+
|                |        |                   |        |                |
|  RAG Service   | <----> | Agent Coordinator | <----> |  LLM Service   |
|                |        |     Service       |        |                |
+----------------+        +---------+---------+        +----------------+
                                    |
                                    | 持久化
                                    v
                          +---------+---------+
                          |                   |
                          |     Redis        |
                          |                   |
                          +-------------------+
```

## 部署环境要求

### 硬件要求

- **最低配置**：
  - CPU: 2核
  - 内存: 1GB
  - 存储: 10GB

- **推荐配置**：
  - CPU: 4核
  - 内存: 4GB
  - 存储: 20GB

### 软件要求

- Kubernetes: 1.19+
- Helm: 3.7+
- Redis: 6.0+
- Istio: 1.10+ (可选，服务网格)
- Prometheus: 2.30+ (可选，监控)

## 部署操作步骤

### 准备工作

1. 确保已连接到正确的Kubernetes集群：

```bash
kubectl config use-context <your-cluster-context>
kubectl get nodes
```

2. 验证必要的命名空间已创建：

```bash
kubectl create namespace suoke
```

3. 确认Helm已正确配置：

```bash
helm version
```

### 安装步骤

#### 使用Helm部署

1. **使用默认配置安装**：

```bash
helm upgrade --install agent-coordinator ./helm/agent-coordinator \
  --namespace suoke \
  --set image.tag=1.2.0
```

2. **使用自定义values文件安装**：

```bash
helm upgrade --install agent-coordinator ./helm/agent-coordinator \
  --namespace suoke \
  -f custom-values.yaml
```

3. **根据环境设置不同参数**：

```bash
# 测试环境
helm upgrade --install agent-coordinator-test ./helm/agent-coordinator \
  --namespace suoke-test \
  --set environment=testing \
  --set replicaCount=1 \
  --set autoscaling.enabled=false \
  --set persistence.enabled=false

# 生产环境
helm upgrade --install agent-coordinator ./helm/agent-coordinator \
  --namespace suoke \
  --set environment=production \
  --set replicaCount=3 \
  --set resources.requests.cpu=1000m \
  --set resources.requests.memory=1Gi
```

### 验证部署

1. **检查Pods状态**：

```bash
kubectl get pods -n suoke -l app=agent-coordinator
```

2. **检查服务状态**：

```bash
kubectl get services -n suoke -l app=agent-coordinator
```

3. **检查ConfigMaps**：

```bash
kubectl get configmaps -n suoke -l app=agent-coordinator
```

4. **检查自动伸缩配置**：

```bash
kubectl get hpa -n suoke -l app=agent-coordinator
```

5. **测试服务可用性**：

```bash
# 获取服务URL
export SERVICE_URL=$(kubectl get svc -n suoke agent-coordinator-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# 测试健康检查
curl http://$SERVICE_URL/health

# 测试API功能
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"query": "test query"}' \
  http://$SERVICE_URL/api/query
```

## 部署后配置

### 日志监控

1. **查看服务日志**：

```bash
kubectl logs -n suoke -l app=agent-coordinator -f
```

2. **配置日志级别**：

编辑ConfigMap或通过Helm更新：

```bash
helm upgrade agent-coordinator ./helm/agent-coordinator \
  --namespace suoke \
  --reuse-values \
  --set env[0].name=LOG_LEVEL \
  --set env[0].value=debug
```

### 安全配置

1. **添加API密钥认证**：

```bash
helm upgrade agent-coordinator ./helm/agent-coordinator \
  --namespace suoke \
  --reuse-values \
  --set env[1].name=API_KEY_HEADER \
  --set env[1].value=X-Suoke-API-Key
```

2. **配置网络策略**：

默认已配置NetworkPolicy，可根据需要调整。

### 扩展配置

1. **调整水平自动缩放**：

```bash
helm upgrade agent-coordinator ./helm/agent-coordinator \
  --namespace suoke \
  --reuse-values \
  --set autoscaling.minReplicas=2 \
  --set autoscaling.maxReplicas=10 \
  --set autoscaling.metrics[0].resource.target.averageUtilization=80
```

2. **增加存储容量**：

```bash
helm upgrade agent-coordinator ./helm/agent-coordinator \
  --namespace suoke \
  --reuse-values \
  --set persistence.size=20Gi
```

## 问题排查

### 常见问题及解决方案

1. **Pod无法启动**：

检查事件和日志：

```bash
kubectl describe pod -n suoke <pod-name>
kubectl logs -n suoke <pod-name>
```

2. **健康检查失败**：

查看健康检查配置和日志：

```bash
kubectl describe pod -n suoke <pod-name> | grep Liveness
kubectl describe pod -n suoke <pod-name> | grep Readiness
```

3. **服务不可用**：

检查网络和端点：

```bash
kubectl get endpoints -n suoke agent-coordinator-service
kubectl run curl-test --image=curlimages/curl -i --rm --restart=Never -- curl http://agent-coordinator-service:80/health
```

4. **性能问题**：

检查资源使用情况：

```bash
kubectl top pods -n suoke -l app=agent-coordinator
kubectl top nodes
```

## 回滚策略

如需回滚到先前版本：

```bash
# 查看历史版本
helm history agent-coordinator -n suoke

# 回滚到特定版本
helm rollback agent-coordinator <revision> -n suoke
```

## 备份与恢复

### 配置备份

1. **手动备份配置**：

```bash
kubectl get configmap -n suoke agent-coordinator-config -o yaml > coordinator-config-backup.yaml
```

2. **使用Velero进行备份**（如已集成）：

```bash
velero backup create agent-coordinator-backup --include-namespaces suoke --selector app=agent-coordinator
```

### 恢复操作

1. **使用备份文件恢复**：

```bash
kubectl apply -f coordinator-config-backup.yaml
```

2. **使用Velero恢复**：

```bash
velero restore create --from-backup agent-coordinator-backup
```

## 更新与升级

### 升级服务

1. **升级到新版本**：

```bash
helm upgrade agent-coordinator ./helm/agent-coordinator \
  --namespace suoke \
  --reuse-values \
  --set image.tag=1.3.0
```

2. **重大版本升级**：

对于重大版本升级，建议先在测试环境验证：

```bash
# 测试环境验证
helm upgrade agent-coordinator-test ./helm/agent-coordinator \
  --namespace suoke-test \
  --set image.tag=2.0.0 \
  --set environment=testing

# 生产环境升级
helm upgrade agent-coordinator ./helm/agent-coordinator \
  --namespace suoke \
  --reuse-values \
  --set image.tag=2.0.0
```

## 监控和警报配置

默认已集成Prometheus ServiceMonitor配置。要查看监控数据：

1. 访问Prometheus界面并查询：
   - `agent_coordinator_http_requests_total`
   - `agent_coordinator_http_request_duration_seconds`
   - `agent_coordinator_active_connections`

2. 配置建议的Grafana仪表盘
3. 设置关键指标的告警规则