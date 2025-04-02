# RAG服务Kubernetes配置指南

本文档提供索克生活RAG服务的Kubernetes配置说明，包括各配置文件的用途、配置选项和最佳实践。

## 配置文件列表

| 文件名 | 描述 | 关键配置项 |
|--------|------|------------|
| `deployment-enhanced.yaml` | 增强版部署配置 | 资源限制、节点亲和性、安全上下文、存活探针 |
| `hpa.yaml` | 水平自动扩缩容配置 | 最小/最大副本数、CPU/内存利用率目标 |
| `network-policy.yaml` | 网络策略配置 | 入站/出站流量控制 |
| `istio-config.yaml` | Istio服务网格配置 | 流量管理、安全策略、遥测 |
| `opentelemetry-config.yaml` | OpenTelemetry可观测性配置 | 追踪、指标收集、分布式日志 |
| `configmap.yaml` | 应用配置映射 | 环境变量、特性开关 |
| `secrets.yaml` | 敏感信息配置 | API密钥、证书、数据库凭据 |
| `01-pvc.yaml` | 持久卷声明 | 存储类型、容量请求 |
| `03-service.yaml` | 服务暴露配置 | 端口映射、会话亲和性 |

## 部署策略

### 滚动更新
RAG服务采用滚动更新策略，确保服务在更新过程中不会中断。关键配置：
- `maxUnavailable: 25%`: 确保至少75%的Pod保持可用
- `maxSurge: 1`: 限制更新过程中额外创建的Pod数量

### 资源管理
为确保性能稳定性，配置了以下资源限制：
- 请求: CPU 200m，内存 512Mi
- 限制: CPU 1000m，内存 2048Mi

### 节点亲和性
部署在具有SSD存储和GPU加速的节点上，通过以下标签选择器实现：
```yaml
nodeAffinity:
  requiredDuringSchedulingIgnoredDuringExecution:
    nodeSelectorTerms:
    - matchExpressions:
      - key: storage-type
        operator: In
        values:
        - ssd
```

## 网络配置

### 零信任网络架构
实施了零信任网络架构，明确定义了允许的入站和出站流量：
- 仅允许来自API网关和知识库服务的入站流量
- 仅允许到知识库服务、向量数据库和日志服务的出站流量

### Istio服务网格集成
启用了Istio的mTLS安全通信和高级流量管理功能：
- 严格的mTLS模式确保服务间加密通信
- 故障注入用于混沌工程测试
- 流量镜像用于无风险测试新版本

## 可观测性

### OpenTelemetry集成
配置了全面的可观测性框架：
- 分布式追踪使用Jaeger后端
- 指标收集使用Prometheus
- 结构化日志使用Elasticsearch

## 安全配置

### Pod安全上下文
设置了严格的Pod安全上下文：
- 以非root用户运行(UID 1000)
- 禁用权限提升
- 只读根文件系统
- 强制执行seccomp配置文件

### 秘密管理
敏感信息通过Kubernetes Secrets存储和管理：
- 使用base64编码存储敏感数据
- 通过环境变量或文件挂载提供给应用程序

## 使用指南

### 部署服务
```bash
# 创建必要的命名空间
kubectl create namespace suoke-life

# 应用配置
kubectl apply -f k8s/deployment-enhanced.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/network-policy.yaml
kubectl apply -f k8s/istio-config.yaml
kubectl apply -f k8s/opentelemetry-config.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/01-pvc.yaml
kubectl apply -f k8s/03-service.yaml
```

### 验证部署
```bash
# 检查Pod状态
kubectl get pods -n suoke-life -l app=rag-service

# 检查服务状态
kubectl get svc -n suoke-life rag-service

# 检查自动扩缩容配置
kubectl get hpa -n suoke-life rag-service-hpa
```

### 监控和故障排除
```bash
# 查看Pod日志
kubectl logs -n suoke-life deployment/rag-service

# 查看Pod描述
kubectl describe pod -n suoke-life -l app=rag-service

# 查看Istio遥测信息
istioctl dashboard kiali
```

## 最佳实践
1. 定期审查和更新资源限制，确保高效利用集群资源
2. 使用命名空间隔离不同服务，提高安全性
3. 实施基于角色的访问控制(RBAC)限制对敏感配置的访问
4. 定期轮换密钥和证书
5. 使用基础设施即代码(IaC)工具管理配置

## 故障恢复流程
在部署失败或服务中断时，按照以下步骤进行故障恢复：
1. 检查Pod和服务日志确定故障原因
2. 如需回滚到先前版本：`kubectl rollout undo deployment/rag-service -n suoke-life`
3. 验证回滚是否成功：`kubectl rollout status deployment/rag-service -n suoke-life`
4. 向监控团队报告问题并记录解决方案