# 监控运维指南

## 监控架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Prometheus    │────│     Grafana     │────│   AlertManager  │
│   (指标收集)     │    │   (可视化)      │    │   (告警通知)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      ELK        │    │     Jaeger      │    │   Node Exporter │
│   (日志分析)     │    │   (链路追踪)     │    │   (系统监控)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 核心指标

### 1. 系统指标
- **CPU使用率**: 系统和容器CPU使用情况
- **内存使用率**: 内存占用和可用内存
- **磁盘I/O**: 读写速度和IOPS
- **网络流量**: 入站和出站流量

### 2. 应用指标
- **请求量**: QPS和并发数
- **响应时间**: 平均响应时间和P99
- **错误率**: 4xx和5xx错误比例
- **可用性**: 服务健康状态

### 3. 业务指标
- **用户活跃度**: DAU/MAU
- **诊断成功率**: 诊断准确性
- **智能体响应**: AI服务质量
- **数据处理**: 数据处理量和延迟

## Prometheus配置

### 1. 配置文件
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

scrape_configs:
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
    - role: pod
    relabel_configs:
    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
      action: keep
      regex: true
```

### 2. 服务发现
```yaml
# 自动发现Kubernetes服务
- job_name: 'kubernetes-services'
  kubernetes_sd_configs:
  - role: service
  relabel_configs:
  - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_scrape]
    action: keep
    regex: true
```

## Grafana仪表板

### 1. 系统概览
- 集群资源使用情况
- 节点状态和性能
- Pod运行状态
- 存储使用情况

### 2. 应用监控
- 微服务健康状态
- API请求统计
- 错误率趋势
- 响应时间分布

### 3. 业务监控
- 用户行为分析
- 诊断服务统计
- 智能体性能
- 数据流量监控

## 告警配置

### 1. 告警规则
```yaml
# alerts.yml
groups:
- name: system-alerts
  rules:
  - alert: HighCPUUsage
    expr: cpu_usage_percent > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "CPU使用率过高"
      description: "{{ $labels.instance }} CPU使用率超过80%"

  - alert: HighMemoryUsage
    expr: memory_usage_percent > 85
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "内存使用率过高"
      description: "{{ $labels.instance }} 内存使用率超过85%"

  - alert: ServiceDown
    expr: up == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "服务不可用"
      description: "{{ $labels.job }} 服务已停止"
```

### 2. 通知配置
```yaml
# alertmanager.yml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@suoke.life'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
- name: 'web.hook'
  email_configs:
  - to: 'admin@suoke.life'
    subject: '索克生活告警: {{ .GroupLabels.alertname }}'
    body: |
      {{ range .Alerts }}
      告警: {{ .Annotations.summary }}
      描述: {{ .Annotations.description }}
      时间: {{ .StartsAt }}
      {{ end }}
```

## 日志管理

### 1. 日志收集
```yaml
# filebeat配置
filebeat.inputs:
- type: container
  paths:
    - /var/log/containers/*.log
  processors:
  - add_kubernetes_metadata:
      host: ${NODE_NAME}
      matchers:
      - logs_path:
          logs_path: "/var/log/containers/"

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
```

### 2. 日志分析
```json
// Elasticsearch索引模板
{
  "template": "suoke-logs-*",
  "mappings": {
    "properties": {
      "@timestamp": {"type": "date"},
      "level": {"type": "keyword"},
      "message": {"type": "text"},
      "service": {"type": "keyword"},
      "pod": {"type": "keyword"}
    }
  }
}
```

## 链路追踪

### 1. Jaeger配置
```yaml
# jaeger部署
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jaeger
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jaeger
  template:
    metadata:
      labels:
        app: jaeger
    spec:
      containers:
      - name: jaeger
        image: jaegertracing/all-in-one:latest
        ports:
        - containerPort: 16686
        - containerPort: 14268
```

### 2. 应用集成
```python
# Python应用集成
from jaeger_client import Config

config = Config(
    config={
        'sampler': {'type': 'const', 'param': 1},
        'logging': True,
    },
    service_name='xiaoai-service',
)
tracer = config.initialize_tracer()
```

## 性能分析

### 1. 应用性能
```bash
# 查看Pod资源使用
kubectl top pods

# 查看节点资源使用
kubectl top nodes

# 查看详细资源信息
kubectl describe node [node-name]
```

### 2. 数据库性能
```sql
-- PostgreSQL性能分析
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;

-- 查看慢查询
SELECT query, query_start, state, wait_event
FROM pg_stat_activity
WHERE state != 'idle'
AND query_start < now() - interval '5 minutes';
```

## 故障排查

### 1. 常见问题
```bash
# 服务无响应
kubectl get pods -l app=xiaoai-service
kubectl logs -f deployment/xiaoai-service
kubectl describe pod [pod-name]

# 网络问题
kubectl get svc
kubectl get endpoints
kubectl exec -it [pod-name] -- nslookup [service-name]

# 存储问题
kubectl get pv
kubectl get pvc
kubectl describe pvc [pvc-name]
```

### 2. 性能问题
```bash
# CPU使用率高
kubectl top pods --sort-by=cpu
kubectl exec -it [pod-name] -- top

# 内存使用率高
kubectl top pods --sort-by=memory
kubectl exec -it [pod-name] -- free -h

# 磁盘I/O高
kubectl exec -it [pod-name] -- iostat -x 1
```

## 运维脚本

### 1. 健康检查脚本
```bash
#!/bin/bash
# health_check.sh

echo "检查服务状态..."
kubectl get pods -o wide

echo "检查服务健康..."
for service in xiaoai xiaoke laoke soer; do
    status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:800${service#*}/health)
    if [ $status -eq 200 ]; then
        echo "✅ $service 服务正常"
    else
        echo "❌ $service 服务异常 (HTTP $status)"
    fi
done
```

### 2. 资源清理脚本
```bash
#!/bin/bash
# cleanup.sh

echo "清理无用镜像..."
docker image prune -f

echo "清理无用容器..."
docker container prune -f

echo "清理无用卷..."
docker volume prune -f

echo "清理完成的Pod..."
kubectl delete pods --field-selector=status.phase=Succeeded
```

## 维护计划

### 日常检查 (每日)
- [ ] 检查所有服务状态
- [ ] 查看监控告警
- [ ] 检查资源使用情况
- [ ] 查看错误日志

### 周期检查 (每周)
- [ ] 分析性能趋势
- [ ] 检查存储使用
- [ ] 更新安全补丁
- [ ] 备份重要数据

### 月度检查 (每月)
- [ ] 容量规划评估
- [ ] 性能优化分析
- [ ] 安全审计
- [ ] 灾难恢复演练
