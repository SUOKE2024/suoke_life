# Kubernetes 部署指南

## 概述

本文档介绍如何在Kubernetes集群中部署索克生活平台。

## 前置要求

- Kubernetes 1.20+
- kubectl 配置完成
- Helm 3.0+ (可选)
- 集群资源: 16GB+ 内存, 50GB+ 存储

## 部署步骤

### 1. 创建命名空间

```bash
kubectl create namespace suoke-life
```

### 2. 配置Secret

```bash
# 创建数据库密码
kubectl create secret generic db-secret \
  --from-literal=postgres-password=your-password \
  --from-literal=redis-password=your-redis-password \
  -n suoke-life
```

### 3. 部署数据库服务

```bash
# 部署PostgreSQL
kubectl apply -f k8s/postgresql.yaml -n suoke-life

# 部署Redis
kubectl apply -f k8s/redis.yaml -n suoke-life

# 部署MongoDB
kubectl apply -f k8s/mongodb.yaml -n suoke-life
```

### 4. 部署应用服务

```bash
# 部署智能体服务
kubectl apply -f k8s/agent-services/ -n suoke-life

# 部署诊断服务
kubectl apply -f k8s/diagnostic-services/ -n suoke-life

# 部署基础服务
kubectl apply -f k8s/base-services/ -n suoke-life
```

### 5. 配置Ingress

```bash
# 部署Nginx Ingress Controller
kubectl apply -f k8s/ingress.yaml -n suoke-life
```

## 服务验证

### 检查Pod状态

```bash
kubectl get pods -n suoke-life
```

### 检查服务状态

```bash
kubectl get services -n suoke-life
```

### 查看日志

```bash
kubectl logs -f deployment/xiaoai-service -n suoke-life
```

## 扩容和更新

### 水平扩容

```bash
kubectl scale deployment xiaoai-service --replicas=3 -n suoke-life
```

### 滚动更新

```bash
kubectl set image deployment/xiaoai-service \
  xiaoai-service=suoke-life/xiaoai-service:v1.1.0 \
  -n suoke-life
```

## 监控和告警

### 部署Prometheus

```bash
kubectl apply -f k8s/monitoring/prometheus.yaml -n suoke-life
```

### 部署Grafana

```bash
kubectl apply -f k8s/monitoring/grafana.yaml -n suoke-life
```

---

*更新时间: 2024-06-08*
