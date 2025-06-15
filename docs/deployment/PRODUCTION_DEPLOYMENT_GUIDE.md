# 索克生活平台生产部署指南

## 概述

本指南详细说明了如何在生产环境中部署索克生活平台的现代化微服务架构，包括Kubernetes集群、服务网格、消息队列、搜索引擎、流处理引擎和AI/ML平台的完整部署流程。

## 前置条件

### 硬件要求
- **最小配置**: 3个节点，每个节点8核CPU，32GB内存，500GB SSD存储
- **推荐配置**: 5个节点，每个节点16核CPU，64GB内存，1TB NVMe SSD存储
- **网络**: 10Gbps内网带宽，1Gbps外网带宽

### 软件要求
- **操作系统**: Ubuntu 22.04 LTS 或 CentOS 8+
- **Kubernetes**: v1.28+
- **Docker**: v24.0+
- **Helm**: v3.12+
- **Istio**: v1.19+

### 域名和证书
- 主域名: `suoke.life`
- API域名: `api.suoke.life`
- 监控域名: `monitoring.suoke.life`
- SSL证书: Let's Encrypt或商业证书

## 部署架构

### 集群拓扑
```
生产环境集群架构:
├── Master节点 (3个)
│   ├── kube-apiserver
│   ├── etcd
│   └── kube-controller-manager
├── Worker节点 (2-5个)
│   ├── 应用服务
│   ├── 数据处理服务
│   └── 监控服务
└── 存储节点 (3个)
    ├── 数据库存储
    ├── 消息队列存储
    └── 搜索引擎存储
```

### 网络架构
```
网络层次:
├── 外部负载均衡器 (云厂商LB)
├── Istio Gateway (入口网关)
├── Service Mesh (服务间通信)
├── Pod Network (容器网络)
└── 存储网络 (持久化存储)
```

## 部署步骤

### 第一阶段: 基础设施部署

#### 1.1 Kubernetes集群部署
```bash
# 使用kubeadm部署集群
sudo kubeadm init --pod-network-cidr=10.244.0.0/16 \
  --service-cidr=10.96.0.0/12 \
  --kubernetes-version=v1.28.0

# 配置kubectl
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# 安装网络插件 (Flannel)
kubectl apply -f https://raw.githubusercontent.com/flannel-io/flannel/master/Documentation/kube-flannel.yml

# 加入Worker节点
kubeadm join <master-ip>:6443 --token <token> --discovery-token-ca-cert-hash <hash>
```

#### 1.2 存储类配置
```yaml
# k8s/storage/storage-class.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
  encrypted: "true"
allowVolumeExpansion: true
reclaimPolicy: Retain
volumeBindingMode: WaitForFirstConsumer
```

#### 1.3 命名空间创建
```bash
# 创建命名空间
kubectl create namespace suoke-life
kubectl create namespace istio-system
kubectl create namespace monitoring
kubectl create namespace data-processing
kubectl create namespace elasticsearch

# 设置默认命名空间
kubectl config set-context --current --namespace=suoke-life
```

### 第二阶段: 服务网格部署

#### 2.1 Istio安装
```bash
# 下载并安装Istio
curl -L https://istio.io/downloadIstio | sh -
cd istio-*
export PATH=$PWD/bin:$PATH

# 安装Istio控制平面
istioctl install --set values.defaultRevision=default -y

# 启用自动注入
kubectl label namespace suoke-life istio-injection=enabled
```

#### 2.2 Istio配置部署
```bash
# 部署Gateway和VirtualService
kubectl apply -f k8s/istio/istio-installation.yaml
kubectl apply -f k8s/istio/traffic-management.yaml

# 验证Istio安装
istioctl verify-install
kubectl get pods -n istio-system
```

### 第三阶段: 数据层部署

#### 3.1 PostgreSQL数据库
```bash
# 使用Helm安装PostgreSQL
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install postgresql bitnami/postgresql \
  --namespace suoke-life \
  --set auth.postgresPassword=<strong-password> \
  --set primary.persistence.size=100Gi \
  --set primary.persistence.storageClass=fast-ssd \
  --set metrics.enabled=true
```

#### 3.2 Redis缓存
```bash
# 安装Redis集群
helm install redis bitnami/redis \
  --namespace suoke-life \
  --set auth.password=<redis-password> \
  --set cluster.enabled=true \
  --set cluster.slaveCount=2 \
  --set persistence.size=20Gi \
  --set persistence.storageClass=fast-ssd
```

#### 3.3 MongoDB文档数据库
```bash
# 安装MongoDB
helm install mongodb bitnami/mongodb \
  --namespace suoke-life \
  --set auth.rootPassword=<mongo-password> \
  --set replicaSet.enabled=true \
  --set replicaSet.replicas.secondary=2 \
  --set persistence.size=50Gi \
  --set persistence.storageClass=fast-ssd
```

### 第四阶段: 数据处理服务部署

#### 4.1 事件总线服务
```bash
# 部署事件总线服务
kubectl apply -f k8s/services/event-bus-deployment.yaml

# 验证事件总线部署
kubectl get pods -l app=event-bus
kubectl get svc event-bus-service
```

#### 4.2 批处理服务部署
```bash
# 部署批处理服务
kubectl apply -f k8s/services/batch-processor-deployment.yaml

# 创建定时任务
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: CronJob
metadata:
  name: health-data-aggregation
spec:
  schedule: "*/5 * * * *"  # 每5分钟执行一次
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: batch-processor
            image: suoke/batch-processor:latest
            command:
            - python
            - -m
            - services.data_processing.health_aggregation
            env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: suoke-secrets
                  key: database-url
            - name: ELASTICSEARCH_URL
              value: "http://elasticsearch:9200"
          restartPolicy: OnFailure
EOF
```

### 第五阶段: 搜索引擎部署

#### 5.1 Elasticsearch集群
```bash
# 部署Elasticsearch
kubectl apply -f k8s/elasticsearch/elasticsearch-cluster.yaml

# 等待集群就绪
kubectl wait --for=condition=ready pod -l app=elasticsearch --timeout=600s

# 验证集群状态
kubectl port-forward svc/elasticsearch-service 9200:9200 &
curl -X GET "localhost:9200/_cluster/health?pretty"
```

#### 5.2 Kibana部署
```bash
# 部署Kibana
kubectl apply -f k8s/elasticsearch/kibana-deployment.yaml

# 配置Kibana访问
kubectl port-forward svc/kibana-service 5601:5601 &
```

### 第六阶段: AI/ML平台部署

#### 6.1 MLflow部署
```bash
# 部署MLflow
kubectl apply -f k8s/mlflow/mlflow-deployment.yaml

# 验证MLflow服务
kubectl get pods -l app=mlflow
kubectl get svc mlflow-service
```

#### 6.2 模型存储配置
```yaml
# k8s/mlflow/minio-storage.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: minio
spec:
  replicas: 1
  selector:
    matchLabels:
      app: minio
  template:
    metadata:
      labels:
        app: minio
    spec:
      containers:
      - name: minio
        image: minio/minio:latest
        args:
        - server
        - /data
        - --console-address
        - ":9001"
        env:
        - name: MINIO_ROOT_USER
          value: "minioadmin"
        - name: MINIO_ROOT_PASSWORD
          value: "minioadmin123"
        ports:
        - containerPort: 9000
        - containerPort: 9001
        volumeMounts:
        - name: data
          mountPath: /data
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: minio-pvc
```

### 第七阶段: 应用服务部署

#### 7.1 配置管理
```bash
# 创建ConfigMap
kubectl create configmap suoke-config \
  --from-file=config/production.env \
  --namespace=suoke-life

# 创建Secret
kubectl create secret generic suoke-secrets \
  --from-literal=database-password=<db-password> \
  --from-literal=redis-password=<redis-password> \
  --from-literal=jwt-secret=<jwt-secret> \
  --namespace=suoke-life
```

#### 7.2 智能体服务部署
```bash
# 部署智能体服务
kubectl apply -f k8s/services/agents/
kubectl apply -f k8s/services/diagnosis/
kubectl apply -f k8s/services/foundation/

# 验证服务部署
kubectl get pods -l tier=agents
kubectl get svc -l tier=agents
```

#### 7.3 数据处理服务部署
```bash
# 部署流处理服务
kubectl apply -f k8s/services/stream-processing/

# 部署事件处理服务
kubectl apply -f k8s/services/event-processing/

# 验证数据处理服务
kubectl get pods -l tier=data-processing
```

### 第八阶段: 监控系统部署

#### 8.1 Prometheus监控
```bash
# 使用Helm安装Prometheus
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set prometheus.prometheusSpec.retention=30d \
  --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=100Gi \
  --set grafana.adminPassword=<grafana-password>
```

#### 8.2 日志聚合
```bash
# 部署ELK Stack
kubectl apply -f k8s/logging/elasticsearch-logging.yaml
kubectl apply -f k8s/logging/logstash-deployment.yaml
kubectl apply -f k8s/logging/filebeat-daemonset.yaml
```

#### 8.3 链路追踪
```bash
# 部署Jaeger
kubectl apply -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/main/deploy/crds/jaegertracing.io_jaegers_crd.yaml
kubectl apply -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/main/deploy/service_account.yaml
kubectl apply -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/main/deploy/role.yaml
kubectl apply -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/main/deploy/role_binding.yaml
kubectl apply -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/main/deploy/operator.yaml

# 创建Jaeger实例
kubectl apply -f k8s/monitoring/jaeger-instance.yaml
```

## 质量保证部署

### SonarQube代码质量
```bash
# 部署SonarQube
kubectl apply -f k8s/sonarqube/sonarqube-deployment.yaml

# 配置质量门禁
kubectl apply -f k8s/sonarqube/quality-gate-config.yaml
```

### 安全扫描配置
```bash
# 配置Snyk扫描
kubectl create secret generic snyk-token \
  --from-literal=token=<snyk-token> \
  --namespace=suoke-life

# 部署安全扫描作业
kubectl apply -f k8s/security/snyk-scan-cronjob.yaml
```

## 网络和安全配置

### 1. 网络策略
```yaml
# k8s/network/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: suoke-network-policy
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: suoke-life
    - namespaceSelector:
        matchLabels:
          name: istio-system
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: suoke-life
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
```

### 2. TLS证书配置
```bash
# 安装cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# 配置Let's Encrypt证书
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@suoke.life
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: istio
EOF
```

### 3. RBAC权限配置
```yaml
# k8s/rbac/service-account.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: suoke-service-account
  namespace: suoke-life
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: suoke-role
  namespace: suoke-life
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps", "secrets"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments", "replicasets"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: suoke-role-binding
  namespace: suoke-life
subjects:
- kind: ServiceAccount
  name: suoke-service-account
  namespace: suoke-life
roleRef:
  kind: Role
  name: suoke-role
  apiGroup: rbac.authorization.k8s.io
```

## 备份和恢复

### 1. 数据库备份
```bash
# PostgreSQL备份脚本
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: postgres-backup
            image: postgres:15
            command:
            - /bin/bash
            - -c
            - |
              pg_dump -h postgresql -U postgres -d suoke_life > /backup/suoke_life_\$(date +%Y%m%d_%H%M%S).sql
              aws s3 cp /backup/ s3://suoke-backups/postgres/ --recursive
            env:
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: suoke-secrets
                  key: database-password
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
          volumes:
          - name: backup-storage
            emptyDir: {}
          restartPolicy: OnFailure
EOF
```

### 2. 配置备份
```bash
# 备份Kubernetes配置
kubectl get all,configmap,secret -o yaml > backup/k8s-config-$(date +%Y%m%d).yaml

# 备份到云存储
aws s3 cp backup/ s3://suoke-backups/k8s-config/ --recursive
```

## 性能调优

### 1. 资源限制配置
```yaml
# 示例：智能体服务资源配置
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "500m"
```

### 2. HPA自动扩缩容
```yaml
# k8s/hpa/agent-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: xiaoai-hpa
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
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 3. 数据库连接池优化
```python
# 数据库连接池配置
DATABASE_CONFIG = {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_timeout": 30,
    "pool_recycle": 3600,
    "pool_pre_ping": True
}
```

## 监控和告警

### 1. 关键指标监控
```yaml
# monitoring/alerts/suoke-alerts.yaml
groups:
- name: suoke-alerts
  rules:
  - alert: HighCPUUsage
    expr: cpu_usage_percent > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High CPU usage detected"
      description: "CPU usage is above 80% for more than 5 minutes"
  
  - alert: HighMemoryUsage
    expr: memory_usage_percent > 85
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage detected"
      description: "Memory usage is above 85% for more than 5 minutes"
  
  - alert: ServiceDown
    expr: up == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Service is down"
      description: "Service {{ $labels.instance }} is down"
```

### 2. 日志监控
```yaml
# 日志告警配置
- alert: ErrorRateHigh
  expr: rate(log_entries{level="error"}[5m]) > 0.1
  for: 2m
  labels:
    severity: warning
  annotations:
    summary: "High error rate in logs"
    description: "Error rate is above 0.1 errors per second"
```

## 部署验证

### 1. 健康检查
```bash
# 检查所有Pod状态
kubectl get pods --all-namespaces

# 检查服务状态
kubectl get svc --all-namespaces

# 检查Istio状态
istioctl proxy-status

# 检查应用健康
curl -f http://api.suoke.life/health
```

### 2. 性能测试
```bash
# 运行K6性能测试
k6 run k6/performance-tests/scenarios/production-load-test.js

# 检查监控指标
kubectl port-forward -n monitoring svc/prometheus-server 9090:80 &
open http://localhost:9090
```

### 3. 功能测试
```bash
# 运行端到端测试
cd testing/e2e
python run_production_tests.py

# 检查测试结果
cat test_results/production_test_report.html
```

## 故障排除

### 常见问题及解决方案

#### 1. Pod启动失败
```bash
# 查看Pod详情
kubectl describe pod <pod-name>

# 查看Pod日志
kubectl logs <pod-name> -c <container-name>

# 检查资源限制
kubectl top pods
kubectl top nodes
```

#### 2. 服务连接问题
```bash
# 检查服务端点
kubectl get endpoints <service-name>

# 测试服务连通性
kubectl run test-pod --image=busybox --rm -it -- sh
nslookup <service-name>
wget -qO- http://<service-name>:<port>/health
```

#### 3. 存储问题
```bash
# 检查PV和PVC状态
kubectl get pv,pvc

# 检查存储类
kubectl get storageclass

# 查看存储事件
kubectl get events --field-selector involvedObject.kind=PersistentVolumeClaim
```

## 维护和更新

### 1. 滚动更新
```bash
# 更新应用镜像
kubectl set image deployment/xiaoai-service xiaoai=suoke/xiaoai:v2.1.0

# 检查更新状态
kubectl rollout status deployment/xiaoai-service

# 回滚更新
kubectl rollout undo deployment/xiaoai-service
```

### 2. 集群维护
```bash
# 节点维护模式
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data

# 节点恢复
kubectl uncordon <node-name>

# 集群升级
kubeadm upgrade plan
kubeadm upgrade apply v1.28.1
```

### 3. 数据库维护
```bash
# 数据库备份
kubectl exec -it postgresql-0 -- pg_dump -U postgres suoke_life > backup.sql

# 数据库优化
kubectl exec -it postgresql-0 -- psql -U postgres -c "VACUUM ANALYZE;"

# 索引重建
kubectl exec -it postgresql-0 -- psql -U postgres -c "REINDEX DATABASE suoke_life;"
```

## 安全最佳实践

### 1. 镜像安全
- 使用官方基础镜像
- 定期更新镜像
- 扫描镜像漏洞
- 使用非root用户运行

### 2. 网络安全
- 实施网络策略
- 使用服务网格mTLS
- 限制出入流量
- 定期审计网络配置

### 3. 访问控制
- 实施最小权限原则
- 使用服务账户
- 定期轮换密钥
- 启用审计日志

## 总结

通过本部署指南，您可以在生产环境中成功部署索克生活平台的现代化微服务架构。关键要点包括：

1. **分阶段部署**: 按照基础设施→数据层→应用层的顺序部署
2. **监控先行**: 在部署应用前先建立监控体系
3. **安全第一**: 实施全面的安全策略和访问控制
4. **备份策略**: 建立完善的备份和恢复机制
5. **性能优化**: 合理配置资源限制和自动扩缩容
6. **故障预案**: 准备完整的故障排除和恢复流程

这个现代化的部署架构为索克生活平台提供了高可用、高性能、高安全的生产环境基础。

---

**索克生活平台 - 生产部署完成** 🚀 