# 索克生活APP微服务部署说明

## 节点池资源分配方案

索克生活APP微服务按照以下节点池资源分配原则进行部署：

| 节点池 | 分配服务组 | 特点 |
|--------|-----------|------|
| **suoke-core-np** | core, feature | 高可用性，稳定性优先 |
| **suoke-ai-np** | ai, diagnosis | 高计算能力，GPU支持 |
| **suoke-db-np** | knowledge | 高IO性能，大存储容量 |

## 服务分组明细

### Core服务组
- `api-gateway`: API网关，处理请求路由和负载均衡
- `auth-service`: 身份认证服务，管理用户登录和授权
- `user-service`: 用户服务，管理用户资料和设置

### AI服务组
- `xiaoai-service`: 小AI服务，提供基础AI对话能力
- `xiaoke-service`: 小客服务，提供客服场景AI能力
- `laoke-service`: 老客服务，提供中医专家AI能力
- `soer-service`: Soer服务，提供健康顾问AI能力
- `agent-coordinator-service`: 代理协调服务，协调多个AI代理

### 诊断服务组
- `inquiry-diagnosis-service`: 问诊服务，处理问诊数据采集和分析
- `looking-diagnosis-service`: 望诊服务，处理图像识别和望诊分析
- `smell-diagnosis-service`: 闻诊服务，处理气味数据分析
- `touch-diagnosis-service`: 切诊服务，处理触诊数据分析
- `four-diagnosis-coordinator`: 四诊协调服务，整合四诊结果

### 知识服务组
- `rag-service`: 检索增强生成服务，提供知识检索能力
- `knowledge-graph-service`: 知识图谱服务，管理健康知识图谱
- `knowledge-base-service`: 知识库服务，管理知识库内容

### 特性服务组
- `corn-maze-service`: 玉米迷宫服务，提供AR玉米迷宫游戏功能

## 资源配置

### Core/Feature服务资源配置
```yaml
resources:
  requests:
    cpu: 200m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

### AI/诊断服务资源配置
```yaml
resources:
  requests:
    cpu: 500m
    memory: 2Gi
    nvidia.com/gpu: ${GPU_COUNT:-0} # GPU服务配置
  limits:
    cpu: 2000m
    memory: 4Gi
    nvidia.com/gpu: ${GPU_COUNT:-0} # GPU服务配置
```

### 知识服务资源配置
```yaml
resources:
  requests:
    cpu: 500m
    memory: 2Gi
  limits:
    cpu: 1000m
    memory: 4Gi
```

## 一键部署操作步骤

1. 确保已安装以下工具：
   - kubectl
   - jq
   - envsubst

2. 登录到Kubernetes集群：
   ```bash
   # 配置kubeconfig
   export KUBECONFIG=/path/to/your/kubeconfig
   ```

3. 设置镜像仓库信息（可选，默认使用阿里云仓库）：
   ```bash
   export REGISTRY_URL=suoke-registry.cn-hangzhou.cr.aliyuncs.com
   export REGISTRY_NAMESPACE=suoke
   export TAG=latest  # 或指定版本标签
   ```

4. 运行一键部署脚本：
   ```bash
   cd services
   ./k8s-templates/deploy-all.sh
   ```

5. 查看部署状态：
   ```bash
   kubectl get pods -n suoke -o wide
   kubectl get svc -n suoke
   kubectl get nodes --show-labels | grep suoke.life
   ```

## 持久卷配置

1. AI模型存储：
   ```yaml
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata:
     name: ai-models-pvc
     namespace: suoke
   spec:
     accessModes:
       - ReadWriteMany
     storageClassName: alicloud-disk-efficiency
     resources:
       requests:
         storage: 50Gi
   ```

2. 知识数据存储：
   ```yaml
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata:
     name: knowledge-data-pvc
     namespace: suoke
   spec:
     accessModes:
       - ReadWriteMany
     storageClassName: alicloud-disk-ssd
     resources:
       requests:
         storage: 100Gi
   ``` 