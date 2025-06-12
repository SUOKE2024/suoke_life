"""
generate_deployment_docs - 索克生活项目模块
"""

import logging
import os
from pathlib import Path

import yaml
from jaeger_client import Config

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
索克生活 - 部署文档自动生成器
"""


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DeploymentDocGenerator:
    """部署文档生成器"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.docs_dir = self.project_root / "docs" / "deployment"
        self.docs_dir.mkdir(parents=True, exist_ok=True)

    def generate_all_docs(self) -> bool:
        """生成所有部署文档"""
        logger.info("🚀 开始生成部署文档...")

        try:
            self.generate_docker_guide()
            self.generate_k8s_guide()
            self.generate_production_guide()
            self.generate_monitoring_guide()

            logger.info("🎉 部署文档生成完成！")
            return True

        except Exception as e:
            logger.error(f"❌ 部署文档生成失败: {e}")
            return False

    def generate_docker_guide(self):
        """生成Docker部署指南"""
        content = """# Docker 部署指南

## 环境要求

- Docker 20.10+
- Docker Compose 2.0+
- 内存: 8GB+
- 磁盘: 50GB+

## 快速启动

### 1. 克隆项目
```bash
git clone https://github.com/suoke-life/suoke_life.git
cd suoke_life
```

### 2. 环境配置
```bash
# 复制环境配置
cp env.example .env

# 编辑配置文件
vim .env
```

### 3. 启动服务
```bash
# 启动所有微服务
docker-compose -f docker-compose.microservices.yml up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

## 服务端口映射

| 服务 | 内部端口 | 外部端口 | 说明 |
|------|----------|----------|------|
| API网关 | 8000 | 8000 | 统一入口 |
| 小艾智能体 | 8001 | 8001 | 健康助手 |
| 小克智能体 | 8002 | 8002 | 数据分析 |
| 老克智能体 | 8003 | 8003 | 中医专家 |
| 索儿智能体 | 8004 | 8004 | 生活顾问 |
| 健康数据服务 | 8005 | 8005 | 数据管理 |
| 区块链服务 | 8006 | 8006 | 数据验证 |
| 认证服务 | 8007 | 8007 | 用户认证 |

## 健康检查

```bash
# 检查所有服务
curl http://localhost:8000/health

# 检查单个服务
curl http://localhost:8001/health
```

## 故障排除

### 常见问题

1. **端口冲突**
```bash
# 查看端口占用
netstat -tulpn | grep :8000

# 修改端口映射
vim docker-compose.microservices.yml
```

2. **内存不足**
```bash
# 查看内存使用
docker stats

# 调整内存限制
vim docker-compose.microservices.yml
```

3. **服务启动失败**
```bash
# 查看详细日志
docker-compose logs [service-name]

# 重启服务
docker-compose restart [service-name]
```

## 数据持久化

```yaml
volumes:
postgres_data:
redis_data:
mongodb_data:
blockchain_data:
```

## 备份与恢复

```bash
# 数据备份
./scripts/backup/backup_all.sh

# 数据恢复
./scripts/backup/restore_all.sh
```
"""

        with open(self.docs_dir / "docker-guide.md", "w", encoding="utf-8") as f:
            f.write(content)

        logger.info("✅ Docker部署指南生成完成")

    def generate_k8s_guide(self):
        """生成Kubernetes部署指南"""
        content = """# Kubernetes 部署指南

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
"""

        with open(self.docs_dir / "kubernetes-guide.md", "w", encoding="utf-8") as f:
            f.write(content)

        logger.info("✅ Kubernetes部署指南生成完成")

    def generate_production_guide(self):
        """生成生产环境部署指南"""
        content = """# 生产环境部署指南

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
kubectl create secret generic db-secrets \
--from-literal=postgres-password=secure-password \
--from-literal=redis-password=secure-password
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
"""

        with open(self.docs_dir / "production-guide.md", "w", encoding="utf-8") as f:
            f.write(content)

        logger.info("✅ 生产环境部署指南生成完成")

    def generate_monitoring_guide(self):
        """生成监控指南"""
        content = """# 监控运维指南

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

config = Config()
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
"""

        with open(self.docs_dir / "monitoring-guide.md", "w", encoding="utf-8") as f:
            f.write(content)

        logger.info("✅ 监控运维指南生成完成")


def main():
    """主函数"""
    project_root = os.getcwd()

    logger.info("🚀 启动部署文档生成器")

    generator = DeploymentDocGenerator(project_root)

    try:
        success = generator.generate_all_docs()

        if success:
            logger.info("🎉 部署文档生成完成！")
            logger.info(f"📁 文档目录: {generator.docs_dir}")
            return 0
        else:
            logger.warning("⚠️ 部署文档生成失败")
            return 1

    except Exception as e:
        logger.error(f"❌ 部署文档生成失败: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
