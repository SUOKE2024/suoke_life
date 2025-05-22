# API 网关服务 Containerd 开发指南

本文档为开发团队提供使用 containerd 和 buildah 进行 API 网关服务开发和部署的详细指导。

## 环境准备

### 开发环境要求

- Python 3.10+
- buildah 1.24+（替代 docker build）
- crictl（替代 docker 命令行工具）
- kubectl 1.20+

### 安装 buildah (构建工具)

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y buildah

# CentOS/RHEL
sudo yum install -y buildah

# macOS (使用 Homebrew)
brew install buildah
```

### 安装 crictl (容器运行时工具)

```bash
VERSION="v1.25.0"
curl -L https://github.com/kubernetes-sigs/cri-tools/releases/download/$VERSION/crictl-$VERSION-linux-amd64.tar.gz --output crictl-$VERSION-linux-amd64.tar.gz
sudo tar zxvf crictl-$VERSION-linux-amd64.tar.gz -C /usr/local/bin
rm -f crictl-$VERSION-linux-amd64.tar.gz
```

## 镜像构建流程

API 网关服务使用 buildah 替代 Docker 进行镜像构建:

```bash
# 切换到服务目录
cd services/api-gateway

# 使用默认参数构建
./scripts/build.sh

# 使用自定义参数
REGISTRY=my-registry.com IMAGE_NAME=api-gateway TAG=v1.2.3 PUSH_IMAGE=true ./scripts/build.sh
```

### 构建参数说明

| 参数 | 描述 | 默认值 |
|-----|------|-------|
| REGISTRY | 镜像仓库地址 | suoke.registry.cn |
| IMAGE_NAME | 镜像名称 | suoke/api-gateway |
| TAG | 镜像标签 | latest |
| PUSH_IMAGE | 是否推送镜像 | false |

## Kubernetes 部署

API 网关服务在 Kubernetes 中使用 containerd 作为容器运行时:

```bash
# 创建命名空间（如果不存在）
kubectl create namespace suoke

# 应用 RuntimeClass
kubectl apply -f deploy/kubernetes/runtime-class.yaml

# 部署服务
kubectl apply -f deploy/kubernetes/deployment.yaml

# 验证部署
kubectl get pods -n suoke -l app=api-gateway
```

### Kubernetes 资源说明

| 文件 | 用途 |
|-----|------|
| runtime-class.yaml | 定义 containerd 运行时类 |
| deployment.yaml | API 网关部署配置、服务和入口网关 |

## 本地开发与测试

尽管生产环境使用 containerd，本地开发也能保持兼容性:

### 1. 本地构建和测试

如果本地已安装 buildah:

```bash
# 构建本地测试镜像
REGISTRY=local IMAGE_NAME=api-gateway TAG=dev ./scripts/build.sh
```

如果本地只有 Docker:

```bash
# 使用 Docker 构建本地测试镜像
docker build -t local/api-gateway:dev -f deploy/docker/Dockerfile .

# 运行容器
docker run -p 8080:8080 -p 50050:50050 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/logs:/app/logs \
  -e LOG_LEVEL=DEBUG \
  local/api-gateway:dev
```

### 2. 测试服务

```bash
# 测试 REST API
curl http://localhost:8080/health

# 测试 gRPC API (使用 grpcurl 工具)
grpcurl -plaintext localhost:50050 api.health.v1.HealthService/Check
```

## CI/CD 集成

API 网关服务的 CI/CD 流程在 GitHub Actions 中配置:

1. 代码推送到 `develop` 分支后，自动构建镜像并部署到开发环境
2. 代码推送到 `main` 分支后，自动构建镜像并部署到生产环境
3. CI/CD 工作流使用 buildah 构建镜像，不依赖 Docker

## 故障排除

### 常见问题与解决方案

#### 1. 镜像构建失败

```
错误: buildah: command not found
```

解决方案: 安装 buildah - `sudo apt-get install -y buildah`

#### 2. 无法访问镜像仓库

```
错误: error authenticating credentials
```

解决方案: 检查镜像仓库凭据 - `buildah login $REGISTRY`

#### 3. Pod 无法启动

```
错误: container has runAsNonRoot and image has non-numeric user
```

解决方案: 确保 Dockerfile 中包含正确的非 root 用户 (`USER suoke`)

## 参考资源

- [Buildah 官方文档](https://github.com/containers/buildah/tree/main/docs)
- [CRI-O/containerd 文档](https://github.com/cri-o/cri-o)
- [Kubernetes containerd 集成](https://kubernetes.io/docs/setup/production-environment/container-runtimes/#containerd) 