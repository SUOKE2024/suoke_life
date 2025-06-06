# 生产环境部署指南

## 架构概述

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   API Gateway   │    │  Microservices  │
│    (Nginx)      │────│   (Kong/Envoy)  │────│   (17 services) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Monitoring    │    │   Databases     │    │   Message Bus   │
│ (Prometheus)    │    │ (PostgreSQL)    │    │   (RabbitMQ)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 环境准备

### 硬件要求
- **CPU**: 32核心+
- **内存**: 64GB+
- **存储**: 1TB SSD+
- **网络**: 1Gbps+

### 软件要求
- **操作系统**: Ubuntu 20.04 LTS
- **容器运行时**: Docker 20.10+
- **编排平台**: Kubernetes 1.20+
- **负载均衡**: Nginx 1.18+

## 部署流程

### 1. 基础设施准备
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Kubernetes
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt update && sudo apt install -y kubelet kubeadm kubectl
```

### 2. 集群初始化
```bash
# 初始化主节点
sudo kubeadm init --pod-network-cidr=10.244.0.0/16

# 配置kubectl
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# 安装网络插件
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
```

### 3. 存储配置
```bash
# 部署存储类
kubectl apply -f k8s/storage/storage-class.yaml

# 创建持久卷
kubectl apply -f k8s/storage/persistent-volumes.yaml
```

### 4. 数据库部署
```bash
# 部署PostgreSQL集群
kubectl apply -f k8s/databases/postgres-cluster.yaml

# 部署Redis集群
kubectl apply -f k8s/databases/redis-cluster.yaml

# 部署MongoDB
kubectl apply -f k8s/databases/mongodb.yaml
```

### 5. 微服务部署
```bash
# 部署配置和密钥
kubectl apply -f k8s/config/

# 部署智能体服务
kubectl apply -f k8s/agents/

# 部署业务服务
kubectl apply -f k8s/services/

# 部署网关
kubectl apply -f k8s/gateway/
```

### 6. 监控部署
```bash
# 部署Prometheus
kubectl apply -f k8s/monitoring/prometheus/

# 部署Grafana
kubectl apply -f k8s/monitoring/grafana/

# 部署日志收集
kubectl apply -f k8s/monitoring/logging/
```

## 安全配置

### 1. 网络安全
```yaml
# 网络策略示例
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

### 2. RBAC配置
```yaml
# 服务账户
apiVersion: v1
kind: ServiceAccount
metadata:
  name: suoke-service-account
---
# 角色绑定
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: suoke-cluster-role-binding
subjects:
- kind: ServiceAccount
  name: suoke-service-account
  namespace: suoke-life
roleRef:
  kind: ClusterRole
  name: cluster-admin
  apiGroup: rbac.authorization.k8s.io
```

### 3. 密钥管理
```bash
# 创建TLS证书
kubectl create secret tls suoke-tls --cert=cert.pem --key=key.pem

# 创建数据库密钥
kubectl create secret generic db-secrets   --from-literal=postgres-password=secure-password   --from-literal=redis-password=secure-password
```

## 性能优化

### 1. 资源限制
```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "500m"
```

### 2. 缓存配置
```yaml
# Redis配置
redis:
  maxmemory: 2gb
  maxmemory-policy: allkeys-lru
  save: "900 1 300 10 60 10000"
```

### 3. 数据库优化
```sql
-- PostgreSQL优化
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
SELECT pg_reload_conf();
```

## 备份策略

### 1. 数据库备份
```bash
# PostgreSQL备份
kubectl exec -it postgres-0 -- pg_dumpall -U postgres > backup.sql

# Redis备份
kubectl exec -it redis-0 -- redis-cli BGSAVE
```

### 2. 配置备份
```bash
# 备份Kubernetes配置
kubectl get all --all-namespaces -o yaml > k8s-backup.yaml

# 备份密钥
kubectl get secrets --all-namespaces -o yaml > secrets-backup.yaml
```

## 监控告警

### 1. 关键指标
- **CPU使用率**: < 80%
- **内存使用率**: < 85%
- **磁盘使用率**: < 90%
- **API响应时间**: < 500ms
- **错误率**: < 1%

### 2. 告警规则
```yaml
# Prometheus告警规则
groups:
- name: suoke-life-alerts
  rules:
  - alert: HighCPUUsage
    expr: cpu_usage_percent > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High CPU usage detected"
```

## 故障恢复

### 1. 服务恢复
```bash
# 重启失败的Pod
kubectl delete pod [pod-name]

# 回滚部署
kubectl rollout undo deployment/[deployment-name]
```

### 2. 数据恢复
```bash
# 恢复数据库
kubectl exec -it postgres-0 -- psql -U postgres < backup.sql

# 恢复Redis
kubectl exec -it redis-0 -- redis-cli --rdb dump.rdb
```

## 维护计划

### 日常维护
- 检查服务状态
- 监控资源使用
- 查看日志异常
- 备份重要数据

### 周期维护
- 更新安全补丁
- 优化数据库性能
- 清理无用资源
- 测试备份恢复

### 升级维护
- 制定升级计划
- 测试环境验证
- 灰度发布
- 回滚准备
