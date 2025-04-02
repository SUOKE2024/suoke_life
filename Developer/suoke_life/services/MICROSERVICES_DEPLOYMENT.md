# 索克生活 - 微服务部署文档

## 1. 基础设施基本情况

### 1.1 Kubernetes集群信息
- **集群版本**: v1.30.15-aliyun.1 (对应上游Kubernetes v1.28.4)
- **版本策略**:
  - 每季度评估一次Kubernetes版本
  - 保持与上游版本差距≤2个小版本
  - 启用[长效支持模式](https://help.aliyun.com/document_detail/205140.html)
  - 遵循[Kubernetes弃用策略](https://kubernetes.io/docs/reference/using-api/deprecation-policy/)
- **节点数量**: 3个
- **操作系统**: Alibaba Cloud Linux 3.2104 U11 (OpenAnolis Edition)
- **内核版本**: 5.10.134-18.al8.x86_64
- **容器运行时**: containerd 1.7.12

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
  - 节点规格: ecs.gn6v.xlarge (4核/8GB/1*NVIDIA V100)
  - 节点数量: 1-3 (按需扩容)
  - 污点/容忍: `dedicated=ai-inference:NoSchedule`
  - 标签: `node-type=ai-services`

- **suoke-vector-np** (向量数据库节点池) - 新增
  - 用途: 部署向量数据库和大规模向量存储服务
  - 节点规格: ecs.r7.2xlarge (8核64GB)
  - 节点数量: 1-2 (固定)
  - 污点/容忍: `dedicated=vector-db:NoSchedule`
  - 标签: `node-type=vector-services`

### 1.3 存储规划
- **本地SSD存储** (suoke-local-ssd)
  - 用途: AI模型缓存、临时数据处理
  - 性能等级: 极速本地IO
  - 容量规划: 总计1TB，单节点200GB
  
- **高性能存储** (alicloud-disk-essd)
  - 用途: 数据库、向量存储、模型存储
  - 性能等级: PL1 
  - 容量规划: 总计500GB，单服务20-50GB
  - 冷热数据分层: 热数据使用PL2，冷数据使用PL0

- **标准存储** (alicloud-disk-ssd)
  - 用途: 日志、配置文件、一般数据存储
  - 性能要求: 中等
  - 容量规划: 总计200GB，单服务10-20GB

### 1.4 网络规划
- **集群网络模式**: Cilium (替代Flannel)
- **集群Pod CIDR**: 172.16.0.0/16
- **集群Service CIDR**: 192.168.0.0/16
- **负载均衡**: 阿里云SLB (Server Load Balancer)
- **Ingress控制器**: Nginx Ingress Controller
- **跨可用区部署**: 节点分布在至少两个可用区以提高可用性
- **多级网络安全**: 
  - 集群级NetworkPolicy
  - 命名空间级隔离策略
  - Pod级安全组规则

## 2. Kubernetes集群构建标准

### 2.1 集群设计原则
- **可靠性优先**: 确保关键应用7*24小时可用
- **成本效益**: 合理配置资源，避免浪费
- **可扩展性**: 服务可以独立扩展，不影响其他服务
- **安全隔离**: 不同类型的服务在逻辑上或物理上隔离
- **可观测性**: 全面的监控和日志收集
- **高可用性**: 跨可用区部署，避免单点故障
- **弹性恢复**: 实现服务自愈和灾难恢复能力

### 2.2 节点配置标准
- **操作系统**: Alibaba Cloud Linux 3.2104+
- **容器运行时**: containerd 1.7+
- **资源预留**:
  - 系统预留: CPU 0.1核/GB内存，内存1GB
  - kubelet预留: CPU 0.5核，内存0.5GB
- **硬盘配置**: 系统盘至少60GB SSD
- **GPU资源管理**:
  - AI节点预留20%计算资源用于系统运行
  - 使用NVIDIA Device Plugin管理GPU资源分配
  - 配置节点亲和性保证GPU任务独占

### 2.3 网络配置标准
- **节点网络**: 专有网络VPC
- **安全组规则**:
  - 节点间通信完全开放
  - 控制平面到节点端口6443/10250开放
  - 负载均衡到节点服务端口开放
- **DNS配置**: CoreDNS作为集群内DNS服务
- **网络策略实施**:
  - 使用Cilium实现零信任网络模型
  - 基于身份的微分段
  - 流量加密和可视化

### 2.4 安全标准
- **RBAC**: 严格的角色访问控制
- **NetworkPolicy**: 限制Pod间通信
- **Secret管理**: 
  - 使用阿里云KMS加密Secrets
  - 集成HashiCorp Vault管理敏感凭证
  - 实现密钥自动轮换机制
- **Pod安全标准(PSS)**:
  - 应用Restricted配置
  - 配置命名空间级别的Pod安全准入控制
- **容器安全**:
  - 非root用户运行容器
  - 只读根文件系统
  - 限制特权容器数量
  - 容器镜像扫描集成
  - 运行时威胁检测
- **供应链安全**:
  - 镜像签名验证
  - 软件物料清单(SBOM)管理
  - 使用Trivy进行漏洞扫描
  - 实施OPA/Kyverno策略验证

### 2.5 GitOps与持续交付实践
- **GitOps工作流**:
  - 使用Git作为唯一真相源
  - 基础设施和应用配置以声明式代码存储
  - 自动化差异检测和应用
- **工具选择**:
  - ArgoCD用于应用部署和同步
  - Flux用于基础设施组件管理
- **环境管理**:
  - 使用Kustomize进行多环境配置
  - 实现环境提升流程(开发→测试→生产)
- **声明式配置**:
  - 使用Helm Chart封装应用部署逻辑
  - 实现配置版本化和回滚能力
  - 采用基于叠加的环境特定配置

### 2.6 服务网格与事件驱动架构
- **服务网格实现**: 完整Istio配置
- **关键功能**:
  - 服务间mTLS加密通信
  - 细粒度流量管理
  - 分布式追踪与可观测性
  - 熔断与限流能力
- **部署模式**: 
  - 边车注入模式
  - 计划ambient模式迁移路径
- **事件驱动能力**:
  - 部署RocketMQ消息队列服务
  - 实现智能体协作事件总线
  - 支持异步通信和解耦架构

## 2.5 GitOps与持续交付实践
- **GitOps工作流**:
  - 使用Git作为唯一真相源
  - 基础设施和应用配置以声明式代码存储
  - 自动化差异检测和应用
- **工具选择**:
  - ArgoCD用于应用部署和同步
  - Flux用于基础设施组件管理
- **环境管理**:
  - 使用Kustomize进行多环境配置
  - 实现环境提升流程(开发→测试→生产)

## 2.6 服务网格策略
- **服务网格实现**: 轻量级Istio配置
- **关键功能**:
  - 服务间mTLS加密通信
  - 细粒度流量管理
  - 分布式追踪与可观测性
  - 熔断与限流能力
- **部署模式**: 
  - 边车注入模式
  - 考虑ambient模式迁移路径

## 3. 集群规划与实施步骤

### 3.1 前置准备
1. **资源规划确认**:
   - 确认各节点池规格和数量
   - 确认存储类型和容量
   - 确认网络和安全需求
   - 评估资源预留比例与弹性策略
   - 规划跨可用区部署方案

2. **镜像仓库准备**:
   - 创建阿里云容器镜像服务命名空间
   - 设置仓库访问凭证
   - 准备基础镜像
   - 配置镜像扫描和签名验证
   - 实施镜像漏洞与合规性检查

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
     --num-of-nodes 3 \
     --master-count 3 \
     --master-vswitch-ids vsw-id1,vsw-id2,vsw-id3 \
     --worker-vswitch-ids vsw-id1,vsw-id2,vsw-id3 \
     --node-cidr-mask 26 \
     --cloud-monitor-flags true \
     --service-cidr 192.168.0.0/16 \
     --security-group-id sg-xxx \
     --is-enterprise-security-group true \
     --timeout-mins 60
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
     --labels node-type=core-services \
     --scaling-policy release \
     --auto-scaling \
     --min-size 2 \
     --max-size 5 \
     --multi-az-policy PRIORITY
   
   # 创建数据服务节点池
   aliyun cs CREATE_NODEPOOL \
     --cluster-id cxxxxxxxx \
     --name suoke-db-np \
     --instance-types ecs.g7.2xlarge \
     --system-disk-category cloud_essd \
     --system-disk-size 100 \
     --count 1 \
     --taints dedicated=database:NoSchedule \
     --labels node-type=stateful-services \
     --scaling-policy cost-optimized \
     --auto-scaling \
     --min-size 1 \
     --max-size 3 \
     --multi-az-policy BALANCE
   
   # 创建AI服务节点池
   aliyun cs CREATE_NODEPOOL \
     --cluster-id cxxxxxxxx \
     --name suoke-ai-np \
     --instance-types ecs.gn6v.xlarge \
     --system-disk-category cloud_essd \
     --system-disk-size 100 \
     --count 1 \
     --taints dedicated=ai-inference:NoSchedule \
     --labels node-type=ai-services \
     --scaling-policy cost-optimized \
     --auto-scaling \
     --min-size 1 \
     --max-size 3 \
     --multi-az-policy BALANCE
     
   # 创建向量数据库节点池
   aliyun cs CREATE_NODEPOOL \
     --cluster-id cxxxxxxxx \
     --name suoke-vector-np \
     --instance-types ecs.r7.2xlarge \
     --system-disk-category cloud_essd \
     --system-disk-size 100 \
     --count 1 \
     --taints dedicated=vector-db:NoSchedule \
     --labels node-type=vector-services \
     --scaling-policy release \
     --auto-scaling \
     --min-size 1 \
     --max-size 2 \
     --multi-az-policy BALANCE
   ```

### 3.3 集群初始化
1. **存储配置**:
   ```bash
   # 创建标准存储类
   cat <<EOF | kubectl apply -f -
   apiVersion: storage.k8s.io/v1
   kind: StorageClass
   metadata:
     name: suoke-standard
   provisioner: diskplugin.csi.alibabacloud.com
   parameters:
     type: cloud_ssd
   reclaimPolicy: Retain
   allowVolumeExpansion: true
   volumeBindingMode: WaitForFirstConsumer
   EOF
   
   # 创建高性能存储类
   cat <<EOF | kubectl apply -f -
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
   volumeBindingMode: WaitForFirstConsumer
   EOF
   
   # 创建向量数据库专用存储类
   cat <<EOF | kubectl apply -f -
   apiVersion: storage.k8s.io/v1
   kind: StorageClass
   metadata:
     name: suoke-vector-db
   provisioner: diskplugin.csi.alibabacloud.com
   parameters:
     type: cloud_essd
     performanceLevel: PL2
   reclaimPolicy: Retain
   allowVolumeExpansion: true
   volumeBindingMode: WaitForFirstConsumer
   EOF
   
   # 创建冷数据存储类
   cat <<EOF | kubectl apply -f -
   apiVersion: storage.k8s.io/v1
   kind: StorageClass
   metadata:
     name: suoke-cold-storage
   provisioner: diskplugin.csi.alibabacloud.com
   parameters:
     type: cloud_essd
     performanceLevel: PL0
   reclaimPolicy: Retain
   allowVolumeExpansion: true
   volumeBindingMode: WaitForFirstConsumer
   EOF
   ```

2. **网络配置**:
   ```bash
   # 部署Cilium CNI
   helm repo add cilium https://helm.cilium.io/
   helm install cilium cilium/cilium \
     --namespace kube-system \
     --set kubeProxyReplacement=strict \
     --set k8sServiceHost=${API_SERVER_IP} \
     --set k8sServicePort=6443 \
     --set hubble.enabled=true \
     --set hubble.relay.enabled=true \
     --set hubble.ui.enabled=true
     
   # 部署Nginx Ingress控制器
   helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
   helm install ingress-nginx ingress-nginx/ingress-nginx \
     --namespace ingress-nginx \
     --create-namespace \
     --set controller.service.annotations."service\.beta\.kubernetes\.io/alibaba-cloud-loadbalancer-spec"="slb.s1.small" \
     --set controller.replicaCount=2 \
     --set controller.nodeSelector."node-type"="core-services" \
     --set controller.metrics.enabled=true
   ```

3. **监控部署**:
   ```bash
   # 部署OpenTelemetry Operator
   kubectl apply -f https://github.com/open-telemetry/opentelemetry-operator/releases/latest/download/opentelemetry-operator.yaml
   
   # 部署Prometheus和Grafana
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   helm install prometheus prometheus-community/kube-prometheus-stack \
     --namespace monitoring \
     --create-namespace \
     --set prometheus.prometheusSpec.podMonitorSelectorNilUsesHelmValues=false \
     --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
     --set grafana.persistence.enabled=true \
     --set grafana.persistence.size=10Gi
   ```

4. **安装服务网格**:
   ```bash
   # 部署Istio服务网格
   helm repo add istio https://istio-release.storage.googleapis.com/charts
   helm repo update
   
   kubectl create namespace istio-system
   helm install istio-base istio/base -n istio-system
   helm install istiod istio/istiod -n istio-system \
     --set pilot.resources.requests.cpu=500m \
     --set pilot.resources.requests.memory=2Gi
     
   helm install istio-ingress istio/gateway -n istio-system \
     --set service.type=LoadBalancer
   ```

5. **部署消息队列**:
   ```bash
   # 部署RocketMQ服务
   helm repo add rocketmq-operator https://apache.github.io/rocketmq-operator/
   helm install rocketmq rocketmq-operator/rocketmq-operator \
     --namespace rocketmq-system \
     --create-namespace
     
   # 部署RocketMQ集群
   cat <<EOF | kubectl apply -f -
   apiVersion: rocketmq.apache.org/v1alpha1
   kind: Broker
   metadata:
     name: suoke-rocketmq
     namespace: rocketmq-system
   spec:
     size: 3
     nameServers: "suoke-rocketmq-name-service:9876"
     replicaPerGroup: 2
     resources:
       requests:
         cpu: 1
         memory: 2Gi
       limits:
         cpu: 2
         memory: 4Gi
     storageMode: StorageClass
     persistentVolumeClaim:
       storageClassName: suoke-standard
       accessModes:
       - ReadWriteOnce
       storage: 50Gi
   ---
   apiVersion: rocketmq.apache.org/v1alpha1
   kind: NameService
   metadata:
     name: suoke-rocketmq-name-service
     namespace: rocketmq-system
   spec:
     size: 1
     hostNetwork: false
     resources:
       requests:
         cpu: 0.5
         memory: 1Gi
       limits:
         cpu: 1
         memory: 2Gi
   EOF
   ```

### 3.4 应用部署准备
1. **命名空间创建与标签**:
   ```bash
   kubectl create namespace suoke
   kubectl label namespace suoke environment=production app=suoke istio-injection=enabled
   ```

2. **资源配额与限制范围设置**:
   ```bash
   # 资源配额设置
   cat <<EOF | kubectl apply -f -
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
   
   # 默认限制范围
   cat <<EOF | kubectl apply -f -
   apiVersion: v1
   kind: LimitRange
   metadata:
     name: suoke-limits
     namespace: suoke
   spec:
     limits:
     - default:
         cpu: 500m
         memory: 512Mi
       defaultRequest:
         cpu: 100m
         memory: 128Mi
       type: Container
   EOF
   ```

3. **Pod安全标准设置**:
   ```bash
   cat <<EOF | kubectl apply -f -
   apiVersion: v1
   kind: Namespace
   metadata:
     name: suoke
     labels:
       pod-security.kubernetes.io/enforce: restricted
       pod-security.kubernetes.io/audit: restricted
       pod-security.kubernetes.io/warn: restricted
   EOF
   ```

4. **服务账号设置**:
   ```bash
   cat <<EOF | kubectl apply -f -
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

5. **密钥管理配置**:
   ```bash
   # 部署Vault用于密钥管理
   helm repo add hashicorp https://helm.releases.hashicorp.com
   helm install vault hashicorp/vault \
     --namespace vault \
     --create-namespace \
     --set server.ha.enabled=true \
     --set server.ha.replicas=3
     
   # 配置Vault集成
   cat <<EOF | kubectl apply -f -
   apiVersion: secrets-store.csi.x-k8s.io/v1
   kind: SecretProviderClass
   metadata:
     name: vault-database-creds
     namespace: suoke
   spec:
     provider: vault
     parameters:
       vaultAddress: "http://vault.vault:8200"
       roleName: "suoke-app"
       objects: |
         - objectName: "db-password"
           secretPath: "secret/data/suoke/database"
           secretKey: "password"
   EOF
   ```

## 4. 项目架构概述

### 4.1 服务层次结构
- **基础设施层**：命名空间、网络策略、存储类
- **平台服务层**：服务网格、消息队列、OpenTelemetry
- **核心服务层**：API网关、认证服务、用户服务
- **数据服务层**：知识图谱服务、知识库服务、RAG服务、向量数据库服务
- **AI服务层**：小克服务、小艾服务(主智能体)、索儿服务、老克服务
- **辅助服务层**：Web搜索服务、代理协调器服务、边缘计算服务

### 4.2 升级后的部署拓扑
```
                     Istio Ingress
                          |
                     +----+----+
                     |         |
             API网关(Deployment) 认证服务(Deployment)
                     |         |
          +----------+---------+--------+
          |          |         |        |
     用户服务      知识图谱      知识库    RAG服务     向量数据库
    (Deploy)   (StatefulSet) (StatefulSet) (StatefulSet) (StatefulSet)
          |          |         |        |        |
          +----------+---------+--------+--------+
                     |
             +-------+-------+
             |       |       |
       +-----------+---------+-----------+--------+
       |           |         |           |        |
   小克服务      小艾服务    索儿服务    老克服务   Web搜索   事件总线
  (Deploy+GPU) (Deploy+GPU) (Deploy) (Deploy+GPU) (Deploy) (StatefulSet)
```

## 5. 部署准备工作

### 5.1 环境要求
- Kubernetes集群 v1.24+
- Helm v3.10+
- kubectl CLI工具
- 阿里云容器镜像服务账号
- ArgoCD CI/CD环境

### 5.2 命名空间创建
```bash
# 使用Helm Chart创建命名空间及其基础配置
helm install suoke-namespace ./helm/suoke-namespace \
  --set environment=production \
  --set istioInjection=enabled
```

### 5.3 密钥配置
```bash
# 创建镜像仓库密钥
kubectl create secret docker-registry aliyun-registry \
  --docker-server=suoke-registry.cn-hangzhou.cr.aliyuncs.com \
  --docker-username=<用户名> \
  --docker-password=<密码> \
  --namespace=suoke

# 使用Vault动态注入敏感配置
for service in api-gateway auth-service user-service rag-service knowledge-base-service knowledge-graph-service; do
  cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${service}
  namespace: suoke
spec:
  template:
    spec:
      volumes:
      - name: secrets-store
        csi:
          driver: secrets-store.csi.k8s.io
          readOnly: true
          volumeAttributes:
            secretProviderClass: "vault-${service}-config"
      containers:
      - name: ${service}
        volumeMounts:
        - name: secrets-store
          mountPath: "/mnt/secrets-store"
          readOnly: true
EOF
done
```

### 5.4 存储准备
```bash
# 使用Helm部署所有存储类
helm install suoke-storage ./helm/suoke-storage \
  --namespace suoke \
  --set coldStorageEnabled=true \
  --set vectorStorageEnabled=true
```

### 5.5 向量数据库部署
```bash
# 部署Milvus向量数据库
helm repo add milvus https://milvus-io.github.io/milvus-helm
helm install milvus milvus/milvus \
  --namespace suoke \
  --set cluster.enabled=true \
  --set persistence.enabled=true \
  --set persistence.persistentVolumeClaim.storageClass=suoke-vector-db \
  --set persistence.persistentVolumeClaim.size=100Gi \
  --set nodeSelector."node-type"="vector-services" \
  --set tolerations[0].key="dedicated" \
  --set tolerations[0].value="vector-db" \
  --set tolerations[0].operator="Equal" \
  --set tolerations[0].effect="NoSchedule"
```

## 6. 服务部署流程

### 6.1 GitOps部署设计
```bash
# 使用ArgoCD部署所有应用
cat <<EOF | kubectl apply -f -
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: suoke-apps
  namespace: argocd
spec:
  project: default
  source:
    repoURL: 'https://gitlab.suoke.life/suoke/helm-charts.git'
    path: apps
    targetRevision: HEAD
    helm:
      valueFiles:
      - values-production.yaml
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: suoke
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
    - ServerSideApply=true
EOF
```

### 6.2 基础服务部署

#### 6.2.1 API网关 (使用Helm Chart)
```bash
# 使用Helm Chart部署API网关
helm install api-gateway ./helm/api-gateway \
  --namespace suoke \
  --set replicaCount=2 \
  --set resources.requests.cpu=200m \
  --set resources.requests.memory=256Mi \
  --set resources.limits.cpu=500m \
  --set resources.limits.memory=512Mi \
  --set image.repository=suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/api-gateway \
  --set image.tag=latest \
  --set service.type=ClusterIP \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=api.suoke.life \
  --set ingress.hosts[0].paths[0].path=/ \
  --set ingress.hosts[0].paths[0].pathType=Prefix
```

#### 6.2.2 认证服务和用户服务 (类似部署方式)

### 6.3 数据服务部署

#### 6.3.1 知识图谱服务 (StatefulSet)
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

#### 6.3.2 RAG服务 (StatefulSet)
```bash
# 从服务目录中获取Kubernetes配置
kubectl apply -f ./services/rag-service/k8s/
```

### 6.4 AI服务部署

#### 6.4.1 AI服务通用部署模板

> **性能优化提示**：
> 1. 启用NUMA感知调度：
>    ```yaml
>    spec:
>      topologySpreadConstraints:
>        - maxSkew: 1
>          topologyKey: kubernetes.io/hostname
>          whenUnsatisfiable: ScheduleAnyway
>          labelSelector:
>            matchLabels:
>              app: ai-service
>    ```
> 2. 配置AI模型缓存：
>    ```yaml
>    volumeMounts:
>      - name: model-cache
>        mountPath: /opt/models
>    volumes:
>      - name: model-cache
>        persistentVolumeClaim:
>          claimName: model-cache-pvc
>    ```
> 3. 多模型服务策略:
>    - 使用InitContainer预热模型
>    - 实现模型量化与优化
>    - 设置资源亲和性保持GPU独占
>    ```yaml
>    spec:
>      initContainers:
>      - name: model-warmup
>        image: suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/model-warmup:latest
>        command: ["/bin/sh", "-c", "/app/warmup.py --model /opt/models/llm-model"]
>        volumeMounts:
>        - name: model-cache
>          mountPath: /opt/models
>      nodeSelector:
>        accelerator: nvidia-a10
>    ```
> 4. 自适应批处理:
>    ```yaml
>    env:
>    - name: ENABLE_DYNAMIC_BATCHING
>      value: "true"
>    - name: MAX_BATCH_SIZE
>      value: "8"
>    - name: MAX_BATCH_TIMEOUT_MS
>      value: "50"
>    ```
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

### 6.5 Ingress配置
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

### 8.1 云原生可观测性策略

#### 8.1.1 统一观测架构
```bash
# 部署OpenTelemetry Operator
kubectl apply -f https://github.com/open-telemetry/opentelemetry-operator/releases/latest/download/opentelemetry-operator.yaml

# 创建OpenTelemetry Collector实例
cat <<EOF | kubectl apply -f -
apiVersion: opentelemetry.io/v1alpha1
kind: OpenTelemetryCollector
metadata:
  name: suoke-collector
  namespace: monitoring
spec:
  mode: deployment
  replicas: 2
  config: |
    receivers:
      otlp:
        protocols:
          grpc:
            endpoint: 0.0.0.0:4317
          http:
            endpoint: 0.0.0.0:4318
      prometheus:
        config:
          scrape_configs:
            - job_name: 'kubernetes-pods'
              kubernetes_sd_configs:
                - role: pod
              relabel_configs:
                - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
                  action: keep
                  regex: true
            - job_name: 'ai-services'
              kubernetes_sd_configs:
                - role: pod
                  namespaces:
                    names: [suoke]
              relabel_configs:
                - source_labels: [__meta_kubernetes_pod_label_service_type]
                  regex: ai
                  action: keep
    processors:
      batch:
        timeout: 1s
        send_batch_size: 1024
      memory_limiter:
        check_interval: 1s
        limit_mib: 1800
      resourcedetection:
        detectors: [env, system, gcp, ec2, azure]
      k8s_attributes:
        extract:
          metadata:
            - k8s.pod.name
            - k8s.namespace.name
            - k8s.deployment.name
            - k8s.node.name
    exporters:
      otlp:
        endpoint: tempo.monitoring:4317
        tls:
          insecure: true
      prometheus:
        endpoint: 0.0.0.0:8889
      loki:
        endpoint: http://loki.monitoring:3100/loki/api/v1/push
    extensions:
      health_check:
        endpoint: 0.0.0.0:13133
      zpages:
        endpoint: 0.0.0.0:55679
    service:
      extensions: [health_check, zpages]
      pipelines:
        traces:
          receivers: [otlp]
          processors: [batch, memory_limiter, resourcedetection, k8s_attributes]
          exporters: [otlp]
        metrics:
          receivers: [otlp, prometheus]
          processors: [batch, memory_limiter, resourcedetection, k8s_attributes]
          exporters: [prometheus]
        logs:
          receivers: [otlp]
          processors: [batch, memory_limiter, resourcedetection, k8s_attributes]
          exporters: [loki]
EOF
```

#### 8.1.2 指标监控
```bash
# 部署Prometheus Stack (包含Grafana)
kubectl create namespace monitoring
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack \
  -n monitoring \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
  --set prometheus.prometheusSpec.podMonitorSelectorNilUsesHelmValues=false \
  --set prometheus.prometheusSpec.retention=15d \
  --set prometheus.prometheusSpec.retentionSize="50GiB" \
  --set prometheus.prometheusSpec.walCompression=true \
  --set prometheus.prometheusSpec.resources.limits.memory=8Gi \
  --set prometheus.prometheusSpec.resources.limits.cpu=1000m \
  --set prometheus.prometheusSpec.resources.requests.memory=4Gi \
  --set prometheus.prometheusSpec.resources.requests.cpu=500m \
  --set grafana.sidecar.dashboards.enabled=true \
  --set grafana.persistence.enabled=true \
  --set grafana.persistence.size=10Gi

# 为AI服务创建自定义ServiceMonitor
cat <<EOF | kubectl apply -f -
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: ai-services-monitor
  namespace: monitoring
spec:
  selector:
    matchLabels:
      service-type: ai
  namespaceSelector:
    matchNames:
      - suoke
  endpoints:
  - port: metrics
    interval: 15s
    path: /metrics
    relabelings:
    - sourceLabels: [__meta_kubernetes_pod_name]
      targetLabel: pod
    - sourceLabels: [__meta_kubernetes_service_name]
      targetLabel: service
    metricRelabelings:
    - sourceLabels: [__name__]
      regex: 'ai_inference_latency_.*'
      action: keep
EOF

# 创建AI服务专用仪表板
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: ai-services-dashboard
  namespace: monitoring
  labels:
    grafana_dashboard: "1"
data:
  ai-services-dashboard.json: |
    {
      "annotations": {
        "list": []
      },
      "editable": true,
      "fiscalYearStartMonth": 0,
      "graphTooltip": 0,
      "links": [],
      "liveNow": false,
      "panels": [
        {
          "datasource": {
            "type": "prometheus",
            "uid": "prometheus"
          },
          "fieldConfig": {
            "defaults": {
              "color": {
                "mode": "palette-classic"
              },
              "custom": {
                "axisCenteredZero": false,
                "axisColorMode": "text",
                "axisLabel": "",
                "axisPlacement": "auto",
                "barAlignment": 0,
                "drawStyle": "line",
                "fillOpacity": 10,
                "gradientMode": "none",
                "hideFrom": {
                  "legend": false,
                  "tooltip": false,
                  "viz": false
                },
                "lineInterpolation": "linear",
                "lineWidth": 1,
                "pointSize": 5,
                "scaleDistribution": {
                  "type": "linear"
                },
                "showPoints": "never",
                "spanNulls": true,
                "stacking": {
                  "group": "A",
                  "mode": "none"
                },
                "thresholdsStyle": {
                  "mode": "off"
                }
              },
              "mappings": [],
              "thresholds": {
                "mode": "absolute",
                "steps": [
                  {
                    "color": "green",
                    "value": null
                  },
                  {
                    "color": "red",
                    "value": 1000
                  }
                ]
              },
              "unit": "ms"
            },
            "overrides": []
          },
          "gridPos": {
            "h": 8,
            "w": 12,
            "x": 0,
            "y": 0
          },
          "id": 1,
          "options": {
            "legend": {
              "calcs": [
                "mean",
                "max",
                "lastNotNull"
              ],
              "displayMode": "table",
              "placement": "bottom",
              "showLegend": true
            },
            "tooltip": {
              "mode": "single",
              "sort": "none"
            }
          },
          "targets": [
            {
              "datasource": {
                "type": "prometheus",
                "uid": "prometheus"
              },
              "editorMode": "code",
              "expr": "histogram_quantile(0.95, sum(rate(ai_inference_latency_bucket{service=~\"$service\"}[5m])) by (le, service))",
              "legendFormat": "{{service}} p95",
              "range": true,
              "refId": "A"
            },
            {
              "datasource": {
                "type": "prometheus",
                "uid": "prometheus"
              },
              "editorMode": "code",
              "expr": "histogram_quantile(0.50, sum(rate(ai_inference_latency_bucket{service=~\"$service\"}[5m])) by (le, service))",
              "hide": false,
              "legendFormat": "{{service}} p50",
              "range": true,
              "refId": "B"
            }
          ],
          "title": "AI 推理延迟",
          "type": "timeseries"
        }
      ],
      "refresh": "",
      "schemaVersion": 38,
      "style": "dark",
      "tags": [
        "ai",
        "suoke"
      ],
      "templating": {
        "list": [
          {
            "current": {
              "selected": false,
              "text": "All",
              "value": "$__all"
            },
            "datasource": {
              "type": "prometheus",
              "uid": "prometheus"
            },
            "definition": "label_values(ai_inference_latency_bucket, service)",
            "hide": 0,
            "includeAll": true,
            "multi": true,
            "name": "service",
            "options": [],
            "query": {
              "query": "label_values(ai_inference_latency_bucket, service)",
              "refId": "StandardVariableQuery"
            },
            "refresh": 1,
            "regex": "",
            "skipUrlSync": false,
            "sort": 0,
            "type": "query"
          }
        ]
      },
      "time": {
        "from": "now-6h",
        "to": "now"
      },
      "title": "AI 服务监控",
      "uid": "ai-services",
      "version": 1,
      "weekStart": ""
    }
EOF
```

#### 8.1.3 分布式追踪
```bash
# 部署Tempo分布式追踪系统
helm repo add grafana https://grafana.github.io/helm-charts
helm install tempo grafana/tempo -n monitoring \
  --set persistence.enabled=true \
  --set persistence.size=50Gi \
  --set tempo.receivers.otlp.protocols.grpc.endpoint=0.0.0.0:4317 \
  --set tempo.receivers.otlp.protocols.http.endpoint=0.0.0.0:4318 \
  --set tempo.storage.trace.backend=local \
  --set tempo.storage.trace.local.path=/var/tempo/traces

# 配置服务追踪注入
cat <<EOF | kubectl apply -f -
apiVersion: opentelemetry.io/v1alpha1
kind: Instrumentation
metadata:
  name: suoke-instrumentation
  namespace: suoke
spec:
  exporter:
    endpoint: http://suoke-collector-collector.monitoring:4317
  propagators:
    - tracecontext
    - baggage
    - b3
  sampler:
    type: parentbased_traceidratio
    argument: "0.25"
  env:
    - name: OTEL_SERVICE_NAME
      value: "${POD_NAME}"
    - name: OTEL_RESOURCE_ATTRIBUTES
      value: "service.namespace=suoke"
EOF
```

#### 8.1.4 日志管理
```bash
# 部署Loki日志聚合系统
helm install loki grafana/loki-stack \
  -n monitoring \
  --set grafana.enabled=false \
  --set promtail.enabled=true \
  --set loki.persistence.enabled=true \
  --set loki.persistence.size=50Gi \
  --set loki.structuredConfig.analytics.reporting_enabled=true

# 创建日志策略
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: promtail-custom-config
  namespace: monitoring
data:
  custom-pipeline.yaml: |
    - pipeline_stages:
      - json:
          expressions:
            level: level
            message: message
            timestamp: timestamp
            trace_id: trace_id
            span_id: span_id
            service: service
      - labels:
          level:
          service:
          trace_id:
          span_id:
      - timestamp:
          source: timestamp
          format: RFC3339
      - output:
          source: message
EOF

# 配置日志告警规则
cat <<EOF | kubectl apply -f -
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: loki-alert-rules
  namespace: monitoring
spec:
  groups:
  - name: loki-error-alerts
    rules:
    - alert: HighErrorRate
      expr: sum(rate({namespace="suoke", level="error"}[5m])) by (service) > 0.1
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "高错误率告警 - {{ \$labels.service }}"
        description: "服务 {{ \$labels.service }} 在过去5分钟内出现高错误率 (> 10%)"
    - alert: CriticalErrorDetected
      expr: sum(count_over_time({namespace="suoke", level="error", message=~".*CRITICAL.*"}[15m])) > 0
      for: 1m
      labels:
        severity: critical
      annotations:
        summary: "检测到关键错误 - {{ \$labels.service }}"
        description: "服务 {{ \$labels.service }} 出现关键错误，请立即检查"
EOF
```

#### 8.1.5 SLO监控与预测性告警
```bash
# 部署OpenSLO Operator
kubectl apply -f https://github.com/OpenSLO/openslo-controller/releases/download/v0.4.0/openslo-controller.yaml

# 创建SLO定义
cat <<EOF | kubectl apply -f -
apiVersion: openslo.com/v1alpha
kind: SLO
metadata:
  name: api-response-time
  namespace: suoke
spec:
  service: api-gateway
  description: "API Gateway response time SLO"
  indicator:
    prometheus:
      query: 'histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{app="api-gateway"}[5m])) by (le))'
  timeWindow:
    duration: 30d
    isRolling: true
  budgetingMethod: Occurrences
  objectives:
  - displayName: "95% requests under 200ms"
    target: 0.95
    op: lt
    value: 0.2
EOF

# 配置预测性告警
cat <<EOF | kubectl apply -f -
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: predictive-alerts
  namespace: monitoring
spec:
  groups:
  - name: predictive-alerts
    rules:
    - alert: MemoryExhaustionPrediction
      expr: predict_linear(container_memory_usage_bytes{namespace="suoke"}[1h], 4 * 3600) > container_spec_memory_limit_bytes{namespace="suoke"}
      for: 15m
      labels:
        severity: warning
      annotations:
        summary: "内存耗尽预测 - {{ \$labels.pod }}"
        description: "预测 Pod {{ \$labels.pod }} 将在4小时内耗尽内存资源"
EOF
```

### 8.2 混沌工程与故障注入
```bash
# 部署Chaos Mesh
helm repo add chaos-mesh https://charts.chaos-mesh.org
helm install chaos-mesh chaos-mesh/chaos-mesh \
  --namespace chaos-mesh \
  --create-namespace \
  --set dashboard.create=true

# 创建定期网络故障测试
cat <<EOF | kubectl apply -f -
apiVersion: chaos-mesh.org/v1alpha1
kind: Schedule
metadata:
  name: network-delay-test
  namespace: chaos-mesh
spec:
  schedule: "0 2 * * 6"  # 每周六凌晨2点执行
  historyLimit: 3
  concurrencyPolicy: Forbid
  template:
    metadata:
      name: network-delay
    spec:
      NetworkChaos:
        action: delay
        mode: one
        selector:
          namespaces:
            - suoke
          labelSelectors:
            app: api-gateway
        delay:
          latency: "100ms"
          correlation: "25"
          jitter: "50ms"
        duration: "5m"
EOF
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
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Pods
        value: 1
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Pods
        value: 2
        periodSeconds: 60
      - type: Percent
        value: 50
        periodSeconds: 30
EOF

# 为AI服务配置基于自定义指标的HPA
cat <<EOF | kubectl apply -f -
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: xiaoai-service-hpa
  namespace: suoke
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: xiaoai-service
  minReplicas: 1
  maxReplicas: 3
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Pods
    pods:
      metric:
        name: ai_inference_queue_length
      target:
        type: AverageValue
        averageValue: 5
EOF
```

## 9. 故障排除指南

### 9.1 常见问题与解决方案
- **镜像拉取失败**：
  - 检查镜像仓库密钥配置: `kubectl get secret aliyun-registry -n suoke -o yaml`
  - 验证镜像路径和标签是否正确
  - 检查网络连接: `kubectl exec -it <pod-name> -n suoke -- ping suoke-registry.cn-hangzhou.cr.aliyuncs.com`
  
- **服务无法启动**：
  - 检查环境变量和配置: `kubectl describe pod <pod-name> -n suoke`
  - 检查错误日志: `kubectl logs <pod-name> -n suoke`
  - 验证资源限制是否合理，资源不足可能导致OOM: `kubectl top pod <pod-name> -n suoke`
  
- **存储问题**：
  - 检查PVC状态: `kubectl get pvc -n suoke`
  - 验证StorageClass配置: `kubectl get sc suoke-premium -o yaml`
  - 检查底层存储提供商: `kubectl describe pvc <pvc-name> -n suoke`
  
- **网络连接问题**：
  - 检查服务DNS解析: `kubectl exec -it <pod-name> -n suoke -- nslookup <service-name>.<namespace>.svc.cluster.local`
  - 验证网络策略: `kubectl get networkpolicy -n suoke`
  - 检查服务端口和目标端口配置: `kubectl get svc <service-name> -n suoke -o yaml`
  - 检查Istio配置: `istioctl analyze -n suoke`

- **AI服务推理问题**：
  - 检查GPU分配: `kubectl exec -it <pod-name> -n suoke -- nvidia-smi`
  - 验证模型加载状态: `kubectl logs <pod-name> -n suoke -c model-warmup`
  - 检查模型缓存挂载: `kubectl exec -it <pod-name> -n suoke -- ls -la /opt/models`

### 9.2 问题诊断工具与命令
```bash
# 查看所有资源状态
kubectl get all -n suoke

# 查看Pod详细信息
kubectl describe pod <pod-name> -n suoke

# 查看容器日志
kubectl logs <pod-name> -c <container-name> -n suoke

# 实时监控日志
kubectl logs -f <pod-name> -n suoke

# 检查服务连接
kubectl exec -it <pod-name> -n suoke -- curl -v <service-url>

# 进入容器调试
kubectl exec -it <pod-name> -n suoke -- /bin/sh

# 检查网络连接
kubectl exec -it <pod-name> -n suoke -- ping <service-name>.<namespace>.svc.cluster.local

# 检查Pod资源使用情况
kubectl top pod <pod-name> -n suoke

# 检查节点资源使用情况
kubectl top node

# 检查Events事件
kubectl get events -n suoke --sort-by='.lastTimestamp'
```

### 9.3 故障自愈策略
```bash
# 为关键服务配置自动重启
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: suoke
spec:
  template:
    spec:
      containers:
      - name: api-gateway
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          successThreshold: 1
          failureThreshold: 3
        startupProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
          failureThreshold: 12
      restartPolicy: Always
EOF

# 配置Pod中断预算
cat <<EOF | kubectl apply -f -
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-gateway-pdb
  namespace: suoke
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: api-gateway
EOF
```

## 10. 维护和升级流程

### 10.1 服务更新流程
```bash
# 使用GitOps工作流更新服务版本
cd deployment/helm-charts/
git checkout -b update-api-gateway
# 编辑values.yaml更新镜像版本
sed -i 's/tag: "1.0.0"/tag: "1.0.1"/' apps/api-gateway/values.yaml
git add apps/api-gateway/values.yaml
git commit -m "chore: update api-gateway to 1.0.1"
git push origin update-api-gateway
# 创建合并请求并由ArgoCD自动应用变更

# 手动回滚（紧急情况）
kubectl rollout undo deployment/api-gateway -n suoke
# 或回滚到特定版本
kubectl rollout undo deployment/api-gateway -n suoke --to-revision=2
```

### 10.2 数据库升级与迁移
```bash
# 数据库模式迁移任务
cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migration-v1-to-v2
  namespace: suoke
spec:
  ttlSecondsAfterFinished: 86400  # 一天后自动清理
  template:
    spec:
      containers:
      - name: migration
        image: suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/db-migration:v1-to-v2
        env:
        - name: DB_HOST
          value: "postgres.suoke"
        volumeMounts:
        - name: db-credentials
          mountPath: "/etc/db-credentials"
          readOnly: true
      volumes:
      - name: db-credentials
        csi:
          driver: secrets-store.csi.k8s.io
          readOnly: true
          volumeAttributes:
            secretProviderClass: "vault-db-credentials"
      restartPolicy: OnFailure
EOF
```

### 10.3 多级备份策略
```bash
# 创建Velero备份工具
helm repo add vmware-tanzu https://vmware-tanzu.github.io/helm-charts
helm install velero vmware-tanzu/velero \
  --namespace velero \
  --create-namespace \
  --set configuration.provider=alibabacloud \
  --set configuration.backupStorageLocation.bucket=suoke-k8s-backup \
  --set configuration.backupStorageLocation.config.region=cn-hangzhou \
  --set initContainers[0].name=velero-plugin-for-alibabacloud \
  --set initContainers[0].image=registry.aliyuncs.com/acs/velero-plugin-alibabacloud:v1.0.0 \
  --set initContainers[0].volumeMounts[0].mountPath=/target \
  --set initContainers[0].volumeMounts[0].name=plugins

# 设置定时备份计划
cat <<EOF | kubectl apply -f -
apiVersion: velero.io/v1
kind: Schedule
metadata:
  name: daily-backup
  namespace: velero
spec:
  schedule: "0 1 * * *"  # 每天凌晨1点
  template:
    includedNamespaces:
    - suoke
    ttl: 720h  # 保留30天
    storageLocation: default
EOF

# 创建数据库备份CronJob
cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: CronJob
metadata:
  name: knowledge-db-backup
  namespace: suoke
spec:
  schedule: "0 2 * * *"  # 每天凌晨2点
  concurrencyPolicy: Forbid
  successfulJobsHistoryLimit: 7
  failedJobsHistoryLimit: 3
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/db-backup:latest
            command:
            - /bin/sh
            - -c
            - |
              pg_dump -h postgres -U postgres -d knowledge > /backup/knowledge-db-\$(date +%Y%m%d).sql
              gzip /backup/knowledge-db-\$(date +%Y%m%d).sql
              # 上传到OSS存储
              ossutil cp /backup/knowledge-db-\$(date +%Y%m%d).sql.gz oss://suoke-backup/database/knowledge/
            volumeMounts:
            - name: backup-volume
              mountPath: /backup
            - name: db-credentials
              mountPath: "/etc/db-credentials"
              readOnly: true
          volumes:
          - name: backup-volume
            persistentVolumeClaim:
              claimName: backup-pvc
          - name: db-credentials
            csi:
              driver: secrets-store.csi.k8s.io
              readOnly: true
              volumeAttributes:
                secretProviderClass: "vault-db-credentials"
          restartPolicy: OnFailure
EOF

# 灾备站点同步
cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: CronJob
metadata:
  name: dr-site-sync
  namespace: suoke
spec:
  schedule: "0 3 * * *"  # 每天凌晨3点
  concurrencyPolicy: Forbid
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: sync
            image: suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/oss-sync:latest
            command:
            - /bin/sh
            - -c
            - |
              ossutil sync oss://suoke-backup/ oss://suoke-dr-backup/ --include="*.gz" --include="*.sql"
              ossutil sync oss://suoke-backup/ oss://suoke-dr-backup/ --include="*.yaml" --include="*.json"
          restartPolicy: OnFailure
EOF
```

### 10.4 零停机升级策略
```bash
# 使用蓝绿部署更新关键服务
cat <<EOF | kubectl apply -f -
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: api-gateway
  namespace: suoke
spec:
  replicas: 3
  revisionHistoryLimit: 2
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
        image: suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/api-gateway:1.0.1
        ports:
        - containerPort: 3000
        resources:
          limits:
            cpu: 500m
            memory: 512Mi
  strategy:
    blueGreen:
      activeService: api-gateway
      previewService: api-gateway-preview
      autoPromotionEnabled: false
      autoPromotionSeconds: 600
      prePromotionAnalysis:
        templates:
        - templateName: success-rate
        args:
        - name: service-name
          value: api-gateway
EOF
```

## 11. 安全性考虑

### 11.1 零信任网络架构
```bash
# 部署Cilium网络策略实现零信任
cat <<EOF | kubectl apply -f -
apiVersion: "cilium.io/v2"
kind: CiliumNetworkPolicy
metadata:
  name: api-gateway-policy
  namespace: suoke
spec:
  endpointSelector:
    matchLabels:
      app: api-gateway
  ingress:
  - fromEndpoints:
    - matchLabels:
        io.kubernetes.pod.namespace: ingress-nginx
    toPorts:
    - ports:
      - port: "3000"
        protocol: TCP
  egress:
  - toEndpoints:
    - matchLabels:
        app: auth-service
        io.kubernetes.pod.namespace: suoke
    toPorts:
    - ports:
      - port: "80"
        protocol: TCP
  - toEndpoints:
    - matchLabels:
        app: user-service
        io.kubernetes.pod.namespace: suoke
    toPorts:
    - ports:
      - port: "80"
        protocol: TCP
  - toFQDNs:
    - matchName: "vault.vault.svc.cluster.local"
    toPorts:
    - ports:
      - port: "8200"
        protocol: TCP
EOF
```

### 11.2 SPIFFE服务身份与mTLS
```bash
# 部署SPIRE服务身份系统
kubectl apply -f https://raw.githubusercontent.com/spiffe/spire/master/doc/quickstart/k8s/spire-server.yaml
kubectl apply -f https://raw.githubusercontent.com/spiffe/spire/master/doc/quickstart/k8s/spire-agent.yaml

# 为服务创建SPIFFE ID
cat <<EOF | kubectl apply -f -
apiVersion: spire.spiffe.io/v1alpha1
kind: ClusterSPIFFEID
metadata:
  name: suoke-api-gateway
spec:
  spiffeID: "spiffe://suoke.life/ns/suoke/sa/api-gateway"
  selector:
    namespaces:
      - suoke
    podSelector:
      matchLabels:
        app: api-gateway
EOF
```

### 11.3 机密管理与访问控制
```bash
# 配置OPA Gatekeeper策略验证
kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/release-3.7/deploy/gatekeeper.yaml

# 应用安全策略
cat <<EOF | kubectl apply -f -
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sNoPrivileged
metadata:
  name: no-privileged-containers
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
    namespaces:
      - "suoke"
EOF

# 配置Trivy镜像扫描
cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: CronJob
metadata:
  name: trivy-image-scan
  namespace: security
spec:
  schedule: "0 1 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: trivy
            image: aquasec/trivy:latest
            args:
            - image
            - --severity
            - HIGH,CRITICAL
            - --output
            - json
            - --report
            - all
            - suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/api-gateway:latest
            env:
            - name: TRIVY_USERNAME
              valueFrom:
                secretKeyRef:
                  name: trivy-credentials
                  key: username
            - name: TRIVY_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: trivy-credentials
                  key: password
          restartPolicy: OnFailure
EOF
```

### 11.4 数据安全防护
```bash
# 部署阿里云KMS加密提供程序
cat <<EOF | kubectl apply -f -
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: alicloud-kms-provider
  namespace: suoke
spec:
  provider: alibabacloud
  parameters:
    objects: |
      array:
        - |
          objectName: db-creds
          objectType: secretsmanager
          objectAlias: db-user
          objectVersion: ""
        - |
          objectName: db-creds
          objectType: secretsmanager
          objectAlias: db-password
          objectVersion: ""
    regionId: "cn-hangzhou"
EOF

# 配置数据加密
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: knowledge-base-service
  namespace: suoke
spec:
  template:
    spec:
      volumes:
      - name: kms-secrets
        csi:
          driver: secrets-store.csi.k8s.io
          readOnly: true
          volumeAttributes:
            secretProviderClass: "alicloud-kms-provider"
      containers:
      - name: knowledge-base-service
        volumeMounts:
        - name: kms-secrets
          mountPath: "/mnt/secrets-store"
          readOnly: true
        env:
        - name: DB_USERNAME
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: username
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: password
        - name: DATA_ENCRYPTION_KEY
          valueFrom:
            secretKeyRef:
              name: encryption-keys
              key: data-key
EOF
```

## 12. GitOps与CI/CD集成

### 12.1 GitOps部署流程

#### 12.1.1 GitOps架构
```
+----------------+     +----------------+     +---------------+
| Git Repository | --> | ArgoCD/Flux CD | --> | Kubernetes    |
| (应用清单)      |     | (集群同步)      |     | (运行环境)     |
+----------------+     +----------------+     +---------------+
       ^                                            |
       |                                            |
       +--------------------------------------------+
                    (状态反馈与自动修复)
```

#### 12.1.2 ArgoCD部署
```bash
# 安装ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 设置高可用配置
kubectl -n argocd patch deployment argocd-server \
  -p '{"spec": {"replicas": 2}}'
kubectl -n argocd patch deployment argocd-repo-server \
  -p '{"spec": {"replicas": 2}}'
kubectl -n argocd patch deployment argocd-application-controller \
  -p '{"spec": {"replicas": 2}}'

# 配置应用源
cat <<EOF | kubectl apply -f -
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: suoke-infrastructure
  namespace: argocd
spec:
  project: default
  source:
    repoURL: 'https://gitlab.suoke.life/suoke/infrastructure.git'
    path: kubernetes/base
    targetRevision: HEAD
    directory:
      recurse: true
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: suoke
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
    - ServerSideApply=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
---
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: suoke-services
  namespace: argocd
spec:
  project: default
  source:
    repoURL: 'https://gitlab.suoke.life/suoke/manifests.git'
    path: environments/production
    targetRevision: HEAD
    helm:
      valueFiles:
      - values-production.yaml
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: suoke
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
    - ServerSideApply=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
EOF

# 配置GitOps仓库结构
# infrastructure/ - 基础设施配置
# ├── kubernetes/
# │   ├── base/ - 基础组件配置
# │   ├── overlays/ - 环境特定配置叠加
# │   │   ├── development/
# │   │   ├── staging/
# │   │   └── production/
# │
# manifests/ - 应用清单
# ├── apps/ - 应用Helm Chart
# │   ├── api-gateway/
# │   ├── auth-service/
# │   └── ...
# ├── environments/ - 环境配置
# │   ├── development/
# │   ├── staging/
# │   └── production/
```

#### 12.1.3 GitOps工作流设计
```bash
# 创建典型的GitOps工作流
cat <<EOF > gitops-workflow.md
# 索克生活 GitOps 工作流

## 1. 开发流程

### 1.1 特性分支
- 从main分支创建特性分支: \`git checkout -b feature/new-service\`
- 在特性分支上开发和测试
- 提交代码到远程特性分支

### 1.2 代码审查
- 创建合并请求到main分支
- 代码审查和自动化测试
- 合并到main分支

## 2. 持续集成

### 2.1 自动构建
- 当代码推送到main或release/*分支时触发CI流水线
- 执行单元测试、集成测试、安全扫描
- 构建容器镜像并推送到容器仓库

### 2.2 版本管理
- 使用语义化版本控制
- 发布版本时，创建发布分支: \`git checkout -b release/1.0.0\`
- 为每个版本打标签: \`git tag v1.0.0\`

## 3. 持续部署

### 3.1 环境晋升
1. 开发环境
   - 自动部署main分支的最新提交
   - 开发人员测试新功能
   
2. 测试环境
   - 部署发布候选版本
   - QA团队进行验收测试
   
3. 生产环境
   - 手动批准部署到生产环境
   - 使用蓝绿部署或金丝雀部署策略

### 3.2 配置管理
- 使用Helm Charts管理应用配置
- 环境特定配置存储在environments/<env>目录中
- 敏感配置使用Vault动态注入

## 4. 监控与反馈

### 4.1 部署监控
- 通过ArgoCD仪表板监控部署状态
- 设置部署告警通知团队

### 4.2 应用监控
- 使用Prometheus和Grafana监控应用指标
- 基于应用性能和错误率设置告警
EOF
```

### 12.2 现代化CI/CD流水线

```yaml
# 在每个服务仓库中创建工作流文件
name: 现代化构建与部署流水线

on:
  push:
    branches: [main, release/*]
    paths:
      - 'services/**'
  pull_request:
    branches: [main]
    paths:
      - 'services/**'

env:
  SERVICE_NAME: api-gateway
  REGISTRY: suoke-registry.cn-hangzhou.cr.aliyuncs.com
  REGISTRY_NAMESPACE: suoke

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: 代码质量检查
        uses: sonarsource/sonarcloud-github-action@master
        with:
          args: >
            -Dsonar.projectKey=suoke_${{ env.SERVICE_NAME }}
            -Dsonar.organization=suoke
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          
      - name: 设置环境
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          
      - name: 安装依赖
        run: cd services/$SERVICE_NAME && npm ci
        
      - name: 运行单元测试
        run: cd services/$SERVICE_NAME && npm test
        
      - name: 运行静态代码分析
        run: cd services/$SERVICE_NAME && npm run lint
        
  security-scan:
    needs: quality
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: 容器镜像安全扫描
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: './services/${{ env.SERVICE_NAME }}'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
          
      - name: 上传安全扫描结果
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
          
      - name: 依赖项检查
        uses: actions/dependency-review-action@v2
        
      - name: 敏感信息泄露扫描
        uses: gitleaks/gitleaks-action@v2
  
  build:
    needs: [quality, security-scan]
    if: github.event_name == 'push'
    runs-on: ubuntu-latest
    outputs:
      image_tag: ${{ steps.set_tag.outputs.image_tag }}
    steps:
      - uses: actions/checkout@v3
      
      - name: 设置镜像标签
        id: set_tag
        run: |
          if [[ $GITHUB_REF == refs/heads/main ]]; then
            echo "image_tag=main-$(git rev-parse --short HEAD)" >> $GITHUB_OUTPUT
          elif [[ $GITHUB_REF =~ refs/heads/release/.* ]]; then
            VERSION=${GITHUB_REF#refs/heads/release/}
            echo "image_tag=$VERSION" >> $GITHUB_OUTPUT
          else
            echo "image_tag=dev-$(git rev-parse --short HEAD)" >> $GITHUB_OUTPUT
          fi
      
      - name: 配置阿里云容器镜像服务
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ secrets.ALIYUN_REGISTRY_USERNAME }}
          password: ${{ secrets.ALIYUN_REGISTRY_PASSWORD }}
      
      - name: 设置Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: 构建并推送镜像
        uses: docker/build-push-action@v4
        with:
          context: ./services/${{ env.SERVICE_NAME }}
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.REGISTRY_NAMESPACE }}/${{ env.SERVICE_NAME }}:${{ steps.set_tag.outputs.image_tag }}
            ${{ env.REGISTRY }}/${{ env.REGISTRY_NAMESPACE }}/${{ env.SERVICE_NAME }}:latest
          build-args: |
            BUILD_VERSION=${{ steps.set_tag.outputs.image_tag }}
            GIT_COMMIT=${{ github.sha }}
            BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
          cache-from: type=registry,ref=${{ env.REGISTRY }}/${{ env.REGISTRY_NAMESPACE }}/${{ env.SERVICE_NAME }}:buildcache
          cache-to: type=registry,ref=${{ env.REGISTRY }}/${{ env.REGISTRY_NAMESPACE }}/${{ env.SERVICE_NAME }}:buildcache,mode=max
          labels: |
            org.opencontainers.image.source=${{ github.server_url }}/${{ github.repository }}
            org.opencontainers.image.revision=${{ github.sha }}
            org.opencontainers.image.created=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
      
      - name: 镜像签名
        uses: sigstore/cosign-installer@main
        
      - name: 签名容器镜像
        run: |
          cosign sign --key ${{ secrets.COSIGN_PRIVATE_KEY }} ${{ env.REGISTRY }}/${{ env.REGISTRY_NAMESPACE }}/${{ env.SERVICE_NAME }}:${{ steps.set_tag.outputs.image_tag }}
          
  deploy:
    needs: build
    if: github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/heads/release/')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: 确定目标环境
        id: set_env
        run: |
          if [[ $GITHUB_REF == refs/heads/main ]]; then
            echo "target_env=staging" >> $GITHUB_OUTPUT
          elif [[ $GITHUB_REF =~ refs/heads/release/.* ]]; then
            echo "target_env=production" >> $GITHUB_OUTPUT
          fi
      
      - name: 构建部署元数据
        id: build_metadata
        run: |
          echo "deploy_id=$(uuidgen)" >> $GITHUB_OUTPUT
          echo "deploy_time=$(date -u +'%Y-%m-%dT%H:%M:%SZ')" >> $GITHUB_OUTPUT
      
      - name: 更新Kubernetes清单
        run: |
          cd manifests/apps/${{ env.SERVICE_NAME }}
          yq eval '.image.tag = "${{ needs.build.outputs.image_tag }}"' -i values-${{ steps.set_env.outputs.target_env }}.yaml
          yq eval '.metadata.annotations.deployTime = "${{ steps.build_metadata.outputs.deploy_time }}"' -i values-${{ steps.set_env.outputs.target_env }}.yaml
          yq eval '.metadata.annotations.deployId = "${{ steps.build_metadata.outputs.deploy_id }}"' -i values-${{ steps.set_env.outputs.target_env }}.yaml
          
      - name: 提交更新的清单
        uses: stefanzweifel/git-auto-commit-action@v4
        with:
          commit_message: "chore: update ${{ env.SERVICE_NAME }} to ${{ needs.build.outputs.image_tag }} for ${{ steps.set_env.outputs.target_env }}"
          file_pattern: 'manifests/apps/${{ env.SERVICE_NAME }}/values-${{ steps.set_env.outputs.target_env }}.yaml'
          branch: main
          
      # 生产环境部署需要手动批准
      - name: 等待生产部署批准
        if: steps.set_env.outputs.target_env == 'production'
        uses: trstringer/manual-approval@v1
        with:
          secret: ${{ secrets.GITHUB_TOKEN }}
          approvers: tech-lead,product-manager
          minimum-approvals: 2
          issue-title: "批准部署 ${{ env.SERVICE_NAME }} ${{ needs.build.outputs.image_tag }} 到生产环境"
          issue-body: "请审查以下变更并批准部署到生产环境:\n版本: ${{ needs.build.outputs.image_tag }}\n提交: ${{ github.sha }}\n时间: ${{ steps.build_metadata.outputs.deploy_time }}"
          
      # ArgoCD将自动检测并应用更新的清单
      
  post-deploy:
    needs: [build, deploy]
    if: success()
    runs-on: ubuntu-latest
    steps:
      - name: 部署通知
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "blocks": [
                {
                  "type": "header",
                  "text": {
                    "type": "plain_text",
                    "text": "✅ 部署成功"
                  }
                },
                {
                  "type": "section",
                  "fields": [
                    {
                      "type": "mrkdwn",
                      "text": "*服务:*\n${{ env.SERVICE_NAME }}"
                    },
                    {
                      "type": "mrkdwn",
                      "text": "*版本:*\n${{ needs.build.outputs.image_tag }}"
                    },
                    {
                      "type": "mrkdwn",
                      "text": "*环境:*\n${{ steps.set_env.outputs.target_env }}"
                    },
                    {
                      "type": "mrkdwn",
                      "text": "*提交者:*\n${{ github.actor }}"
                    }
                  ]
                },
                {
                  "type": "actions",
                  "elements": [
                    {
                      "type": "button",
                      "text": {
                        "type": "plain_text",
                        "text": "查看部署"
                      },
                      "url": "https://argocd.suoke.life/applications/suoke-${{ env.SERVICE_NAME }}-${{ steps.set_env.outputs.target_env }}"
                    },
                    {
                      "type": "button",
                      "text": {
                        "type": "plain_text",
                        "text": "查看提交"
                      },
                      "url": "${{ github.server_url }}/${{ github.repository }}/commit/${{ github.sha }}"
                    }
                  ]
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### 12.3 渐进式交付策略
```yaml
# 使用Flagger实现渐进式交付
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: api-gateway
  namespace: suoke
spec:
  provider: istio
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-gateway
  progressDeadlineSeconds: 600
  service:
    port: 80
    targetPort: 3000
    gateways:
    - public-gateway
    hosts:
    - api.suoke.life
  analysis:
    interval: 30s
    threshold: 10
    maxWeight: 50
    stepWeight: 10
    metrics:
    - name: request-success-rate
      thresholdRange:
        min: 99
      interval: 1m
    - name: request-duration
      thresholdRange:
        max: 500
      interval: 1m
    webhooks:
    - name: load-test
      url: http://flagger-loadtester.suoke/
      timeout: 15s
      metadata:
        cmd: "hey -z 1m -q 10 -c 2 http://api-gateway.suoke:80/"
    
    # A/B测试配置
    match:
      - headers:
          user-type:
            regex: "beta-testers"
      - headers:
          cookie:
            regex: ".*canary=true.*"
    
    # 部署前预热步骤
    webhooks:
      - name: cache-warmer
        url: http://flagger-loadtester.suoke/fetch
        timeout: 30s
        metadata:
          cmd: "curl -sS http://api-gateway-canary.suoke/api/warmup"
      
      # 部署后测试
      - name: acceptance-test
        type: pre-rollout
        url: http://flagger-loadtester.suoke/
        timeout: 30s
        metadata:
          type: bash
          cmd: |
            curl -sS http://api-gateway-canary.suoke/api/health | grep OK
            
      # 生产质量测试
      - name: production-check
        type: rollout
        url: http://quality-gate-service.suoke/
        timeout: 60s
        metadata:
          type: json
          payload: |
            {
              "service": "api-gateway",
              "metrics": ["error_rate", "response_time", "slo_compliance"]
            }
```

## 13. 附录

### 13.1 服务依赖关系图
```
api-gateway → [auth-service, user-service, xiaoke-service, xiaoai-service, ...]
xiaoke-service → [rag-service, knowledge-base-service]
knowledge-base-service → [knowledge-graph-service, milvus-vector-db]
agent-coordinator-service → [xiaoke-service, xiaoai-service, soer-service, laoke-service]
event-bus → [所有服务]
```

### 13.2 专用AI硬件加速配置
```yaml
# GPU节点亲和性示例
spec:
  nodeSelector:
    accelerator: nvidia-v100
  tolerations:
  - key: "nvidia.com/gpu"
    operator: "Exists"
    effect: "NoSchedule"
  containers:
  - name: ai-service
    resources:
      limits:
        nvidia.com/gpu: 1
    env:
    - name: NVIDIA_VISIBLE_DEVICES
      value: "all"
    - name: NVIDIA_DRIVER_CAPABILITIES
      value: "compute,utility"
    - name: MODEL_PRECISION
      value: "fp16"  # 使用半精度加速推理
    volumeMounts:
    - name: nvidia-config
      mountPath: /etc/nvidia
  volumes:
  - name: nvidia-config
    configMap:
      name: nvidia-device-plugin-config
```

### 13.3 服务网格与边缘计算配置
```yaml
# Istio VirtualService高级配置
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: api-gateway
  namespace: suoke
spec:
  hosts:
  - api.suoke.life
  gateways:
  - suoke-gateway
  http:
  - match:
    - headers:
        user-region:
          exact: north-china
    route:
    - destination:
        host: api-gateway-north
        port:
          number: 80
        subset: v1
  - match:
    - headers:
        user-region:
          exact: south-china
    route:
    - destination:
        host: api-gateway-south
        port:
          number: 80
        subset: v1
  - route:
    - destination:
        host: api-gateway
        port:
          number: 80
        subset: v1
      weight: 90
    - destination:
        host: api-gateway
        port:
          number: 80
        subset: v2
      weight: 10
  
  # 故障注入配置
  - fault:
      delay:
        percentage:
          value: 1
        fixedDelay: 2s
      abort:
        percentage:
          value: 0.5
        httpStatus: 500
    match:
    - headers:
        x-chaos-testing:
          exact: "true"
    route:
    - destination:
        host: api-gateway
        port:
          number: 80
```

### 13.4 向量数据库优化配置
```yaml
# Milvus高级配置
apiVersion: milvus.io/v1beta1
kind: Milvus
metadata:
  name: suoke-milvus
  namespace: suoke
spec:
  mode: cluster
  components:
    image: milvusdb/milvus:v2.2.9
    rootCoord:
      replicas: 1
      resources:
        limits:
          cpu: 2
          memory: 4Gi
        requests:
          cpu: 500m
          memory: 1Gi
    proxy:
      replicas: 2
      resources:
        limits:
          cpu: 4
          memory: 8Gi
        requests:
          cpu: 1
          memory: 2Gi
    queryCoord:
      replicas: 1
      resources:
        limits:
          cpu: 2
          memory: 4Gi
        requests:
          cpu: 500m
          memory: 1Gi
    queryNode:
      replicas: 2
      resources:
        limits:
          cpu: 8
          memory: 32Gi
        requests:
          cpu: 2
          memory: 8Gi
    indexCoord:
      replicas: 1
      resources:
        limits:
          cpu: 2
          memory: 4Gi
        requests:
          cpu: 500m
          memory: 1Gi
    indexNode:
      replicas: 2
      resources:
        limits:
          cpu: 4
          memory: 16Gi
        requests:
          cpu: 1
          memory: 4Gi
    dataCoord:
      replicas: 1
      resources:
        limits:
          cpu: 2
          memory: 4Gi
        requests:
          cpu: 500m
          memory: 1Gi
    dataNode:
      replicas: 2
      resources:
        limits:
          cpu: 4
          memory: 16Gi
        requests:
          cpu: 1
          memory: 4Gi
  config:
    milvus:
      common:
        retentionDuration: 168h  # 7天数据保留期
        gracefulTime: 5000       # ms
      log:
        level: info
        format: json
      cache:
        insertBufferSize: 1GB
        cacheSize: 32GB          # 总缓存大小
```

### 13.5 重要链接
- Prometheus监控: https://monitoring.suoke.life
- Grafana仪表板: https://grafana.suoke.life
- ArgoCD控制台: https://argocd.suoke.life
- API文档: https://api.suoke.life/docs
- 分布式追踪: https://tempo.suoke.life
- Spiffe管理: https://spiffe.suoke.life
- 网络可视化: https://hubble.suoke.life

### 13.6 持续学习资源
- [Kubernetes官方文档](https://kubernetes.io/docs/home/)
- [阿里云ACK最佳实践](https://help.aliyun.com/document_detail/86982.html)
- [Istio服务网格文档](https://istio.io/latest/docs/)
- [ArgoCD GitOps文档](https://argo-cd.readthedocs.io/en/stable/)
- [OpenTelemetry可观测性框架](https://opentelemetry.io/docs/)
- [Cilium网络策略](https://docs.cilium.io/)
- [Milvus向量数据库文档](https://milvus.io/docs)
- [SPIFFE/SPIRE身份管理](https://spiffe.io/docs/)
- [Flagger渐进式交付](https://docs.flagger.app/)

---

**文档版本**: 3.0.0  
**更新日期**: 2023-03-29  
**联系人**: 索克生活技术团队