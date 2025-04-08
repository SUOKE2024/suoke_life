# Kubernetes 配置

本目录包含 Agent Coordinator Service 的 Kubernetes 部署配置文件。

## 目录结构

```
k8s/
├── base/                    # 基础配置
│   ├── configmap.yaml       # 配置映射
│   ├── deployment.yaml      # 基础部署
│   ├── kustomization.yaml   # 基础 kustomization 文件
│   └── service.yaml         # 服务定义
└── overlays/                # 环境特定覆盖
    ├── dev/                 # 开发环境
    │   ├── kustomization.yaml
    │   └── patches/         # 开发环境补丁
    │       ├── amd64-node-selector.yaml   # 节点选择器
    │       └── deployment-patch.yaml      # 部署补丁
    └── prod/                # 生产环境
        ├── hpa.yaml         # 水平 Pod 自动缩放
        ├── kustomization.yaml
        ├── network-policy.yaml    # 网络策略
        ├── pdb.yaml         # Pod 中断预算
        ├── pvc.yaml         # 持久卷声明
        └── patches/         # 生产环境补丁
            ├── amd64-node-selector.yaml   # 节点选择器
            └── deployment-patch.yaml      # 部署补丁
```

## 使用说明

### 开发环境部署

```bash
kubectl apply -k overlays/dev
```

### 生产环境部署

```bash
kubectl apply -k overlays/prod
```

## 环境差异

| 配置 | 开发环境 | 生产环境 |
|------|----------|----------|
| 副本数 | 1 | 2 |
| CPU 限制 | 500m | 1 |
| 内存限制 | 512Mi | 1Gi |
| 日志级别 | debug | info |
| 自动扩缩容 | 否 | 是 |
| 持久存储 | 否 | 是 |
| 网络策略 | 否 | 是 |

## 配置自定义

若要自定义配置，可以编辑 `base/configmap.yaml` 文件修改基本配置，或者在各环境的 `patches` 目录下添加额外的补丁文件。

## 更多信息

详细的部署指南请参考 [Kubernetes 部署文档](../docs/kubernetes-deployment.md)。