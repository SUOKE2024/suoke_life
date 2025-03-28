# 索克生活 - 微服务部署文档

## 1. 基础设施基本情况

### 1.1 Kubernetes集群信息
- **集群版本**: v1.32.1-aliyun.1
- **节点数量**: 3个
- **操作系统**: Alibaba Cloud Linux 3.2104 U11 (OpenAnolis Edition)
- **内核版本**: 5.10.134-18.al8.x86_64
- **容器运行时**: containerd 1.6.36

### 1.2 节点池规划与配置
- **suoke-core-np** (核心服务节点池)
  - 用途: 部署API网关、认证服务、用户服务等核心业务服务
  - 节点规格: ecs.c7.2xlarge (8核16GB)
  - 节点数量: 2-5 (弹性伸缩)
  - 污点/容忍: 无，可部署一般服务
  - 标签: `node-type=core-services`

- **suoke-db-np** (数据服务节点池)
  - 用途: 部署知识图谱、知识库、RAG服务等需要持久化存储的服务
  - 节点规格: ecs.g7.2xlarge (8核32GB)
  - 节点数量: 1-3 (固定或有限扩展)
  - 污点/容忍: `dedicated=database:NoSchedule`，确保只有数据服务部署在此
  - 标签: `node-type=stateful-services`
  
- **suoke-ai-np** (AI推理节点池)
  - 用途: 部署AI服务包括小克服务、小艾服务(主智能体)、索儿服务、老克服务
  - 节点规格: ecs.g7.4xlarge (16核64GB)
  - 节点数量: 1-3 (按需扩容)
  - 污点/容忍: `dedicated=ai-inference:NoSchedule`
  - 标签: `node-type=ai-services`

### 1.3 存储规划
- **高性能存储** (alicloud-disk-essd)
  - 用途: 数据库、向量存储、模型存储
  - 性能等级: PL1 
  - 容量规划: 总计500GB，单服务20-50GB

- **标准存储** (alicloud-disk-ssd)
  - 用途: 日志、配置文件、一般数据存储
  - 性能要求: 中等
  - 容量规划: 总计200GB，单服务10-20GB

### 1.4 网络规划
- **集群网络模式**: Flannel
- **集群Pod CIDR**: 172.16.0.0/16
- **集群Service CIDR**: 192.168.0.0/16
- **负载均衡**: 阿里云SLB (Server Load Balancer)
- **Ingress控制器**: Nginx Ingress Controller

## 2. Kubernetes集群构建标准

### 2.1 集群设计原则
- **可靠性优先**: 确保关键应用7*24小时可用
- **成本效益**: 合理配置资源，避免浪费
- **可扩展性**: 服务可以独立扩展，不影响其他服务
- **安全隔离**: 不同类型的服务在逻辑上或物理上隔离
- **可观测性**: 全面的监控和日志收集

### 2.2 节点配置标准
- **操作系统**: Alibaba Cloud Linux 3.2104+
- **容器运行时**: containerd 1.6+
- **资源预留**:
  - 系统预留: CPU 0.1核/GB内存，内存1GB
  - kubelet预留: CPU 0.5核，内存0.5GB
- **硬盘配置**: 系统盘至少60GB SSD

### 2.3 网络配置标准
- **节点网络**: 专有网络VPC
- **安全组规则**:
  - 节点间通信完全开放
  - 控制平面到节点端口6443/10250开放
  - 负载均衡到节点服务端口开放
- **DNS配置**: CoreDNS作为集群内DNS服务

### 2.4 安全标准
- **RBAC**: 严格的角色访问控制
- **NetworkPolicy**: 限制Pod间通信
- **Secret管理**: 使用KMS加密Secrets
- **容器安全**:
  - 非root用户运行容器
  - 只读根文件系统
  - 限制特权容器数量

## 3. 集群规划与实施步骤

### 3.1 前置准备
1. **资源规划确认**:
   - 确认各节点池规格和数量
   - 确认存储类型和容量
   - 确认网络和安全需求

2. **镜像仓库准备**:
   - 创建阿里云容器镜像服务命名空间
   - 设置仓库访问凭证
   - 准备基础镜像

### 3.2 集群创建
1. **创建ACK集群**:
   ```bash
   # 通过阿里云控制台或CLI创建集群
   aliyun cs CREATE_CLUSTER \
     --name suoke-cluster \
     --version 1.32.1-aliyun.1 \
     --region cn-hangzhou \
     --vpcid vpc-xxx \
     --worker-system-disk-category cloud_essd \
     --worker-system-disk-size 100 \
     --num-of-nodes 3
   ```

2. **配置节点池**:
   ```bash
   # 创建核心服务节点池
   aliyun cs CREATE_NODEPOOL \
     --cluster-id cxxxxxxxx \
     --name suoke-core-np \
     --instance-types ecs.c7.2xlarge \
     --system-disk-category cloud_essd \
     --system-disk-size 100 \
     --count 2 \
     --labels node-type=core-services
   
   # 创建数据服务节点池
   aliyun cs CREATE_NODEPOOL \
     --cluster-id cxxxxxxxx \
     --name suoke-db-np \
     --instance-types ecs.g7.2xlarge \
     --system-disk-category cloud_essd \
     --system-disk-size 100 \
     --count 1 \
     --taints dedicated=database:NoSchedule \
     --labels node-type=stateful-services
   
   # 创建AI服务节点池
   aliyun cs CREATE_NODEPOOL \
     --cluster-id cxxxxxxxx \
     --name suoke-ai-np \
     --instance-types ecs.g7.4xlarge \
     --system-disk-category cloud_essd \
     --system-disk-size 100 \
     --count 1 \
     --taints dedicated=ai-inference:NoSchedule \
     --labels node-type=ai-services
   ```

### 3.3 集群初始化
1. **存储配置**:
   ```bash
   # 创建存储类
   kubectl apply -f - <<EOF
   apiVersion: storage.k8s.io/v1
   kind: StorageClass
   metadata:
     name: suoke-standard
   provisioner: diskplugin.csi.alibabacloud.com
   parameters:
     type: cloud_ssd
   reclaimPolicy: Retain
   allowVolumeExpansion: true
   EOF
   
   # 创建高性能存储类
   kubectl apply -f - <<EOF
   apiVersion: storage.k8s.io/v1
   kind: StorageClass
   metadata:
     name: suoke-premium
   provisioner: diskplugin.csi.alibabacloud.com
   parameters:
     type: cloud_essd
     performanceLevel: PL1
   reclaimPolicy: Retain
   allowVolumeExpansion: true
   EOF
   ```

2. **网络配置**:
   ```bash
   # 部署Nginx Ingress控制器
   helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
   helm install ingress-nginx ingress-nginx/ingress-nginx \
     --namespace ingress-nginx \
     --create-namespace \
     --set controller.service.annotations."service\.beta\.kubernetes\.io/alibaba-cloud-loadbalancer-spec"="slb.s1.small"
   ```

3. **监控部署**:
   ```bash
   # 部署Prometheus和Grafana
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   helm install prometheus prometheus-community/kube-prometheus-stack \
     --namespace monitoring \
     --create-namespace
   ```

### 3.4 应用部署准备
1. **命名空间创建**:
   ```bash
   kubectl create namespace suoke
   ```

2. **资源配额设置**:
   ```bash
   kubectl apply -f - <<EOF
   apiVersion: v1
   kind: ResourceQuota
   metadata:
     name: suoke-quota
     namespace: suoke
   spec:
     hard:
       requests.cpu: 16
       requests.memory: 32Gi
       limits.cpu: 32
       limits.memory: 64Gi
       persistentvolumeclaims: 30
       pods: 50
       services: 30
       secrets: 100
       configmaps: 100
   EOF
   ```

3. **服务账号设置**:
   ```bash
   kubectl apply -f - <<EOF
   apiVersion: v1
   kind: ServiceAccount
   metadata:
     name: suoke-deployer
     namespace: suoke
   ---
   apiVersion: rbac.authorization.k8s.io/v1
   kind: Role
   metadata:
     name: deployer
     namespace: suoke
   rules:
   - apiGroups: ["", "apps", "batch"]
     resources: ["deployments", "statefulsets", "services", "pods", "configmaps", "secrets"]
     verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
   ---
   apiVersion: rbac.authorization.k8s.io/v1
   kind: RoleBinding
   metadata:
     name: suoke-deployer-binding
     namespace: suoke
   subjects:
   - kind: ServiceAccount
     name: suoke-deployer
     namespace: suoke
   roleRef:
     kind: Role
     name: deployer
     apiGroup: rbac.authorization.k8s.io
   EOF
   ```

## 4. 项目架构概述

### 4.1 服务层次结构
- **基础设施层**：命名空间、网络策略、存储类
- **核心服务层**：API网关、认证服务、用户服务
- **数据服务层**：知识图谱服务、知识库服务、RAG服务
- **AI服务层**：小克服务、小艾服务(主智能体)、索儿服务、老克服务
- **辅助服务层**：Web搜索服务、代理协调器服务

### 4.2 部署拓扑
```
                    Ingress
                       |
          +------------+------------+
          |                         |
     API网关(Deployment)         认证服务(Deployment)
          |                         |
    +-----+-------------------------+-----+
    |           |           |            |
用户服务     知识图谱     知识库        RAG服务
(Deploy)    (StatefulSet) (StatefulSet) (StatefulSet)
    |           |           |            |
    +-----+-----+-----------+------------+
          |
    +-----+------+-------+-------+-------+
    |            |       |       |       |
  小克服务    小艾服务  索儿服务  老克服务  Web搜索
 (Deploy)    (Deploy)  (Deploy) (Deploy) (Deploy)
```

## 5. 部署准备工作

### 5.1 环境要求
- Kubernetes集群 v1.22+
- Helm v3.8+
- kubectl CLI工具
- 阿里云容器镜像服务账号

### 5.2 命名空间创建
```bash
kubectl create namespace suoke
```

### 5.3 密钥配置
```bash
# 创建镜像仓库密钥
kubectl create secret docker-registry aliyun-registry \
  --docker-server=suoke-registry.cn-hangzhou.cr.aliyuncs.com \
  --docker-username=<用户名> \
  --docker-password=<密码> \
  --namespace=suoke

# 从.env文件创建配置密钥
for service in api-gateway auth-service user-service rag-service knowledge-base-service knowledge-graph-service; do
  if [ -f "./services/$service/.env.example" ]; then
    cp "./services/$service/.env.example" "./services/$service/.env"
    # 编辑.env文件设置实际配置值
    kubectl create secret generic $service-env --from-file=.env=./services/$service/.env -n suoke
  fi
done
```

### 5.4 存储准备
```bash
# 创建默认存储类
cat <<EOF | kubectl apply -f -
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: suoke-standard
provisioner: kubernetes.io/alibaba-cloud-disk
parameters:
  type: cloud_ssd
reclaimPolicy: Retain
allowVolumeExpansion: true
EOF
```

## 6. 服务部署流程

### 6.1 基础服务部署

#### 6.1.1 API网关 (Deployment)
```bash
# 创建ConfigMap
kubectl create configmap api-gateway-config \
  --from-file=./services/api-gateway/config/ \
  -n suoke

# 部署API网关
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: suoke
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
      - name: api-gateway
        image: suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/api-gateway:latest
        ports:
        - containerPort: 3000
        envFrom:
        - secretRef:
            name: api-gateway-env
        resources:
          limits:
            cpu: 500m
            memory: 512Mi
          requests:
            cpu: 200m
            memory: 256Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
      imagePullSecrets:
      - name: aliyun-registry
---
apiVersion: v1
kind: Service
metadata:
  name: api-gateway
  namespace: suoke
spec:
  selector:
    app: api-gateway
  ports:
  - port: 80
    targetPort: 3000
  type: ClusterIP
EOF
```

#### 6.1.2 认证服务和用户服务 (类似部署方式)

### 6.2 数据服务部署

#### 6.2.1 知识图谱服务 (StatefulSet)
```bash
# 创建持久卷声明模板
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: knowledge-graph
  namespace: suoke
spec:
  serviceName: "knowledge-graph"
  replicas: 1
  selector:
    matchLabels:
      app: knowledge-graph
  template:
    metadata:
      labels:
        app: knowledge-graph
    spec:
      containers:
      - name: knowledge-graph
        image: suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/knowledge-graph:latest
        ports:
        - containerPort: 8080
        envFrom:
        - secretRef:
            name: knowledge-graph-service-env
        volumeMounts:
        - name: data
          mountPath: /app/data
        resources:
          limits:
            cpu: 1000m
            memory: 2Gi
          requests:
            cpu: 500m
            memory: 1Gi
      imagePullSecrets:
      - name: aliyun-registry
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: "suoke-standard"
      resources:
        requests:
          storage: 10Gi
---
apiVersion: v1
kind: Service
metadata:
  name: knowledge-graph
  namespace: suoke
spec:
  selector:
    app: knowledge-graph
  ports:
  - port: 80
    targetPort: 8080
  clusterIP: None
EOF
```

#### 6.2.2 RAG服务 (StatefulSet)
```bash
# 从服务目录中获取Kubernetes配置
kubectl apply -f ./services/rag-service/k8s/
```

### 6.3 AI服务部署

#### 6.3.1 AI服务通用部署模板
```bash
# 为每个AI服务创建Deployment
for service in xiaoke-service xiaoai-service soer-service laoke-service; do
  cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${service%-service}
  namespace: suoke
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ${service%-service}
  template:
    metadata:
      labels:
        app: ${service%-service}
    spec:
      containers:
      - name: ${service%-service}
        image: suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/${service}:latest
        ports:
        - containerPort: 3000
        envFrom:
        - secretRef:
            name: ${service}-env
        resources:
          limits:
            cpu: 1000m
            memory: 1Gi
          requests:
            cpu: 500m
            memory: 512Mi
      imagePullSecrets:
      - name: aliyun-registry
---
apiVersion: v1
kind: Service
metadata:
  name: ${service%-service}
  namespace: suoke
spec:
  selector:
    app: ${service%-service}
  ports:
  - port: 80
    targetPort: 3000
EOF
done
```

### 6.4 Ingress配置
```bash
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: suoke-ingress
  namespace: suoke
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
spec:
  ingressClassName: nginx
  rules:
  - host: api.suoke.life
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-gateway
            port:
              number: 80
  - host: auth.suoke.life
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: auth-service
            port:
              number: 80
EOF
```

## 7. 部署后验证

### 7.1 服务状态检查
```bash
# 检查所有服务状态
kubectl get all -n suoke

# 检查特定服务日志
kubectl logs -f deployment/api-gateway -n suoke
kubectl logs -f statefulset/rag-service-0 -n suoke

# 检查服务连接
kubectl exec -it deployment/api-gateway -n suoke -- curl -v http://auth-service.suoke
```

### 7.2 健康检查配置
```bash
# 添加Liveness和Readiness探针示例 (适用于需要调整的服务)
kubectl patch deployment api-gateway -n suoke --patch '
{
  "spec": {
    "template": {
      "spec": {
        "containers": [
          {
            "name": "api-gateway",
            "livenessProbe": {
              "httpGet": {
                "path": "/health",
                "port": 3000
              },
              "initialDelaySeconds": 30,
              "periodSeconds": 10
            },
            "readinessProbe": {
              "httpGet": {
                "path": "/health",
                "port": 3000
              },
              "initialDelaySeconds": 5,
              "periodSeconds": 5
            }
          }
        ]
      }
    }
  }
}'
```

## 8. 运维和监控

### 8.1 资源监控
```bash
# 部署Prometheus和Grafana
kubectl create namespace monitoring
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/prometheus -n monitoring
helm install grafana grafana/grafana -n monitoring
```

### 8.2 日志管理
```bash
# 部署EFK堆栈
kubectl apply -f services/config/logging/
```

### 8.3 自动扩缩容配置
```bash
# 为无状态服务配置HPA
cat <<EOF | kubectl apply -f -
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-gateway-hpa
  namespace: suoke
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-gateway
  minReplicas: 2
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
EOF
```

## 9. 故障排除指南

### 9.1 常见问题
- **镜像拉取失败**：检查镜像仓库密钥配置
- **服务无法启动**：检查环境变量和配置
- **存储问题**：检查PVC状态和存储类配置
- **网络连接问题**：检查服务DNS和网络策略

### 9.2 排查命令
```bash
# 检查Pod详情
kubectl describe pod <pod-name> -n suoke

# 检查服务连接
kubectl exec -it <pod-name> -n suoke -- curl -v <service-url>

# 查看容器日志
kubectl logs <pod-name> -n suoke

# 检查PVC状态
kubectl get pvc -n suoke
```

## 10. 维护和升级流程

### 10.1 服务更新流程
```bash
# 更新服务镜像
kubectl set image deployment/api-gateway api-gateway=suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/api-gateway:v1.0.1 -n suoke

# StatefulSet更新
kubectl set image statefulset/rag-service rag-service=suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/rag-service:v1.0.1 -n suoke
```

### 10.2 配置更新流程
```bash
# 更新ConfigMap
kubectl create configmap api-gateway-config \
  --from-file=./services/api-gateway/config/ \
  -n suoke \
  --dry-run=client -o yaml | kubectl apply -f -

# 重启以应用新配置
kubectl rollout restart deployment/api-gateway -n suoke
```

### 10.3 备份策略
```bash
# 创建数据备份CronJob
cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: CronJob
metadata:
  name: knowledge-graph-backup
  namespace: suoke
spec:
  schedule: "0 1 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: bitnami/kubectl:latest
            command:
            - /bin/sh
            - -c
            - |
              kubectl exec -n suoke statefulset/knowledge-graph-0 -- tar czf - /app/data | \
              gzip > /backup/knowledge-graph-\$(date +%Y%m%d).tar.gz
            volumeMounts:
            - name: backup-volume
              mountPath: /backup
          restartPolicy: OnFailure
          volumes:
          - name: backup-volume
            persistentVolumeClaim:
              claimName: backup-pvc
EOF
```

## 11. 安全性考虑

### 11.1 网络策略
```bash
# 限制Pod间通信
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-gateway-policy
  namespace: suoke
spec:
  podSelector:
    matchLabels:
      app: api-gateway
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    - podSelector:
        matchLabels:
          app: ingress-nginx
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: auth-service
    - podSelector:
        matchLabels:
          app: user-service
EOF
```

### 11.2 RBAC配置
```bash
# 创建服务账号和角色
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ServiceAccount
metadata:
  name: cicd-deployer
  namespace: suoke
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: deployer
  namespace: suoke
rules:
- apiGroups: ["", "apps", "batch"]
  resources: ["deployments", "statefulsets", "services", "pods", "configmaps", "secrets"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: cicd-deployer-binding
  namespace: suoke
subjects:
- kind: ServiceAccount
  name: cicd-deployer
  namespace: suoke
roleRef:
  kind: Role
  name: deployer
  apiGroup: rbac.authorization.k8s.io
EOF
```

## 12. CI/CD集成

### 12.1 GitHub Actions流程
```yaml
# 在每个服务仓库中创建工作流文件
name: 构建和部署微服务

on:
  push:
    branches: [main]
    paths:
      - 'services/**'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: 配置阿里云容器镜像服务
        uses: docker/login-action@v2
        with:
          registry: suoke-registry.cn-hangzhou.cr.aliyuncs.com
          username: ${{ secrets.ALIYUN_REGISTRY_USERNAME }}
          password: ${{ secrets.ALIYUN_REGISTRY_PASSWORD }}
      
      - name: 设置Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: 构建并推送镜像
        uses: docker/build-push-action@v4
        with:
          context: ./services/api-gateway
          push: true
          tags: suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/api-gateway:latest
          
      - name: 应用Kubernetes配置
        uses: steebchen/kubectl@v2
        with:
          config: ${{ secrets.KUBE_CONFIG_DATA }}
          command: apply -f services/api-gateway/k8s/
```

## 13. 附录

### 13.1 服务依赖关系图
```
api-gateway → [auth-service, user-service, xiaoke-service, xiaoai-service, ...]
xiaoke-service → [rag-service, knowledge-base-service, web-search-service]
knowledge-base-service → [knowledge-graph-service]
```

### 13.2 重要链接
- Prometheus监控: http://monitoring.suoke.life
- Grafana仪表板: http://grafana.suoke.life
- API文档: http://api.suoke.life/docs

---

**文档版本**: 1.2.0  
**更新日期**: 2025-03-28  
**联系人**: 索克生活技术团队