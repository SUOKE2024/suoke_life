# RAG服务 - Kustomize使用指南

## 目录结构

```
k8s/
├── base/                  # 基础配置
│   ├── deployment-enhanced.yaml
│   ├── 01-pvc.yaml
│   ├── 03-service.yaml
│   ├── hpa.yaml
│   ├── network-policy.yaml
│   ├── istio-config.yaml
│   ├── opentelemetry-config.yaml
│   └── kustomization.yaml
├── overlays/              # 环境差异配置
│   ├── development/       # 开发环境
│   │   ├── deployment-patch.yaml
│   │   └── kustomization.yaml
│   └── production/        # 生产环境
│       ├── deployment-patch.yaml
│       └── kustomization.yaml
```

## 使用方法

### 查看生成的配置

```bash
# 开发环境
kubectl kustomize ./k8s/overlays/development

# 生产环境
kubectl kustomize ./k8s/overlays/production
```

### 应用配置

```bash
# 开发环境
kubectl apply -k ./k8s/overlays/development

# 生产环境
kubectl apply -k ./k8s/overlays/production
```

## 环境差异

### 开发环境
- 单副本部署
- 开启DEBUG模式
- 日志级别设为DEBUG
- 较低的资源请求/限制

### 生产环境
- 双副本部署
- 关闭DEBUG模式
- 日志级别设为INFO
- 更高的资源请求/限制

## 添加新环境

1. 创建新的环境目录，例如 `staging`：
```bash
mkdir -p ./k8s/overlays/staging
```

2. 创建相应的 kustomization.yaml 和补丁文件：
```bash
cp ./k8s/overlays/development/kustomization.yaml ./k8s/overlays/staging/
cp ./k8s/overlays/development/deployment-patch.yaml ./k8s/overlays/staging/
```

3. 修改新环境的配置以满足特定需求。

## 更新基础配置

修改 `base` 目录中的文件会影响所有环境。请确保更改是所有环境都需要的通用更改。