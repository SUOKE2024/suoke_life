# 索克生活 Kubernetes 部署配置

本目录包含索克生活平台的 Kubernetes 部署配置，重点关注智能体弹性伸缩和AI模型版本管理。

## 📁 文件结构

```
k8s/
├── README.md                           # 本文档
├── deployment.yaml                     # 基础部署配置
├── service.yaml                        # 服务配置
├── ingress.yaml                        # 入口配置
├── hpa-agents.yaml                     # 智能体水平伸缩配置
├── vpa-agents.yaml                     # 智能体垂直伸缩配置
├── ai-model-version-crd.yaml           # AI模型版本管理CRD
├── ai-model-examples.yaml              # AI模型配置示例
├── deploy-agents-autoscaling.sh        # 自动化部署脚本
└── monitoring-dashboard.yaml           # 监控仪表板配置（自动生成）
```

## 🚀 快速开始

### 1. 前置条件

- Kubernetes 集群 (v1.20+)
- kubectl 已配置并连接到集群
- Metrics Server 已安装（用于HPA）
- 可选：Vertical Pod Autoscaler（用于VPA）

### 2. 一键部署

```bash
# 部署所有组件
./deploy-agents-autoscaling.sh deploy

# 验证部署状态
./deploy-agents-autoscaling.sh verify

# 生成监控仪表板
./deploy-agents-autoscaling.sh dashboard

# 清理所有资源
./deploy-agents-autoscaling.sh cleanup
```

### 3. 手动部署

```bash
# 1. 创建命名空间
kubectl create namespace suoke-life

# 2. 部署CRD
kubectl apply -f ai-model-version-crd.yaml

# 3. 部署AI模型配置
kubectl apply -f ai-model-examples.yaml -n suoke-life

# 4. 部署HPA
kubectl apply -f hpa-agents.yaml -n suoke-life

# 5. 部署VPA（可选）
kubectl apply -f vpa-agents.yaml -n suoke-life
```

## 🤖 智能体弹性伸缩策略

### 水平伸缩 (HPA)

每个智能体都配置了独特的伸缩策略：

#### 小艾智能体 (xiaoai-agent)
- **最小副本数**: 2
- **最大副本数**: 10
- **CPU阈值**: 70%
- **内存阈值**: 80%
- **自定义指标**: AI推理请求数/秒 (30)

#### 小克智能体 (xiaoke-agent)
- **最小副本数**: 2
- **最大副本数**: 8
- **CPU阈值**: 75%
- **内存阈值**: 85%
- **自定义指标**: 健康分析请求数/秒 (25)

#### 老克智能体 (laoke-agent)
- **最小副本数**: 1
- **最大副本数**: 6
- **CPU阈值**: 80%
- **内存阈值**: 90%
- **自定义指标**: 中医诊断请求数/秒 (20)

#### 索儿智能体 (soer-agent)
- **最小副本数**: 1
- **最大副本数**: 5
- **CPU阈值**: 70%
- **内存阈值**: 80%
- **自定义指标**: 养生推荐请求数/秒 (15)

### 垂直伸缩 (VPA)

VPA自动调整Pod的资源请求和限制：

- **更新模式**: Auto（自动重启Pod应用新资源）
- **资源控制**: CPU、内存、GPU（如适用）
- **最小/最大资源限制**: 防止资源过度分配

## 🧠 AI模型版本管理

### 自定义资源定义 (CRD)

#### AIModel
管理AI模型的生命周期：

```yaml
apiVersion: suoke.life/v1
kind: AIModel
metadata:
  name: xiaoai-llm-model
spec:
  modelName: "xiaoai-conversation-llm"
  version: "v2.1.0"
  agentType: "xiaoai"
  modelType: "llm"
  framework: "huggingface"
  # ... 更多配置
```

#### ModelVersion
管理模型版本和部署策略：

```yaml
apiVersion: suoke.life/v1
kind: ModelVersion
metadata:
  name: xiaoai-llm-v2-1-0
spec:
  modelRef: "xiaoai-llm-model"
  version: "v2.1.0"
  canaryDeployment:
    enabled: true
    trafficPercentage: 20
  # ... 更多配置
```

#### ModelRegistry
管理模型注册表：

```yaml
apiVersion: suoke.life/v1
kind: ModelRegistry
metadata:
  name: suoke-model-registry
spec:
  name: "suoke-central-registry"
  endpoint: "https://models.suoke.life/registry"
  # ... 更多配置
```

### 模型部署策略

1. **滚动更新 (RollingUpdate)**: 默认策略，逐步替换旧版本
2. **蓝绿部署 (BlueGreen)**: 快速切换，零停机时间
3. **金丝雀部署 (Canary)**: 渐进式发布，风险控制

## 📊 监控和观察

### 关键指标

- **智能体性能指标**:
  - CPU/内存使用率
  - 请求响应时间
  - 错误率
  - 吞吐量

- **模型推理指标**:
  - 推理延迟
  - 模型准确率
  - GPU利用率
  - 缓存命中率

- **伸缩指标**:
  - HPA伸缩事件
  - VPA资源调整
  - Pod重启次数
  - 资源利用率趋势

### Grafana仪表板

部署脚本会自动生成Grafana仪表板配置，包含：

- 智能体资源使用情况
- HPA伸缩历史
- AI模型性能指标
- 系统健康状态

## 🔧 配置调优

### HPA调优建议

1. **稳定窗口**: 调整`stabilizationWindowSeconds`避免频繁伸缩
2. **伸缩策略**: 根据业务需求调整`scaleUp`和`scaleDown`策略
3. **指标阈值**: 根据实际负载调整CPU/内存阈值

### VPA调优建议

1. **更新模式**: 生产环境建议使用`Off`模式，手动应用建议
2. **资源边界**: 设置合理的`minAllowed`和`maxAllowed`
3. **控制资源**: 选择需要VPA管理的资源类型

### 模型版本管理调优

1. **验证策略**: 配置严格的模型验证规则
2. **回滚策略**: 启用自动回滚机制
3. **缓存策略**: 优化模型缓存配置

## 🚨 故障排除

### 常见问题

#### HPA无法获取指标
```bash
# 检查Metrics Server状态
kubectl get pods -n kube-system | grep metrics-server

# 检查HPA状态
kubectl describe hpa -n suoke-life
```

#### VPA不工作
```bash
# 检查VPA组件
kubectl get pods -n kube-system | grep vpa

# 检查VPA推荐
kubectl describe vpa -n suoke-life
```

#### 模型加载失败
```bash
# 检查模型注册表连接
kubectl logs -n suoke-life deployment/model-registry

# 检查模型服务器状态
kubectl get aimodels -n suoke-life
kubectl describe aimodel <model-name> -n suoke-life
```

### 日志查看

```bash
# 查看智能体日志
kubectl logs -n suoke-life deployment/xiaoai-agent -f

# 查看HPA控制器日志
kubectl logs -n kube-system deployment/horizontal-pod-autoscaler

# 查看模型注册表日志
kubectl logs -n suoke-life deployment/model-registry -f
```

## 📚 参考文档

- [Kubernetes HPA文档](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Kubernetes VPA文档](https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler)
- [自定义资源定义](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/)
- [Prometheus监控](https://prometheus.io/docs/)
- [Grafana仪表板](https://grafana.com/docs/)

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](../LICENSE) 文件了解详情。

---

**索克生活开发团队** - 让AI智能体更智能，让健康管理更简单！ 