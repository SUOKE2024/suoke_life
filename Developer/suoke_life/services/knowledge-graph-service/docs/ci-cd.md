# 索克生活知识图谱服务 CI/CD 指南

本文档描述了索克生活知识图谱服务的持续集成和持续部署流程。本服务使用GitHub Actions实现自动化构建、测试和部署。

## CI/CD流程概述

完整的CI/CD流程包括以下步骤：

1. 代码变更推送到GitHub仓库
2. GitHub Actions触发自动化构建和测试
3. 通过测试后构建Docker镜像
4. 推送镜像到阿里云容器镜像服务
5. 通过ArgoCD自动部署到Kubernetes集群

## GitHub Actions配置

服务的CI/CD使用GitHub Actions实现，配置文件位于`.github/workflows/`目录下。

### 主要工作流程

#### CI工作流程 (ci.yml)

```yaml
name: Build and Test

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-go@v3
        with:
          go-version: '1.20'
      - name: golangci-lint
        uses: golangci/golangci-lint-action@v3
        with:
          version: v1.54
          args: --timeout=5m

  test:
    name: Test
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-go@v3
        with:
          go-version: '1.20'
      - name: Install dependencies
        run: go mod download
      - name: Run unit tests
        run: go test -v -race -coverprofile=coverage.out ./...
      - name: Upload coverage reports
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.out
          flags: unittests
      
  build:
    name: Build
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-go@v3
        with:
          go-version: '1.20'
      - name: Build server
        run: go build -v -o bin/kg-service ./cmd/server
      - name: Build importer
        run: go build -v -o bin/importer ./cmd/importer
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: binaries
          path: bin/
```

#### CD工作流程 (cd.yml)

```yaml
name: Build and Deploy

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  docker:
    name: Build and Push Docker Image
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      # 登录阿里云容器镜像服务
      - name: Login to ACR
        uses: docker/login-action@v2
        with:
          registry: suoke-registry.cn-hangzhou.cr.aliyuncs.com
          username: ${{ secrets.ALIYUN_USERNAME }}
          password: ${{ secrets.ALIYUN_PASSWORD }}
      
      # 设置Docker标签
      - name: Set Docker Tags
        id: docker_tags
        run: |
          VERSION=latest
          if [[ $GITHUB_REF == refs/tags/* ]]; then
            VERSION=${GITHUB_REF#refs/tags/}
          fi
          echo "::set-output name=version::$VERSION"
      
      # 构建并推送Docker镜像
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          file: ./Dockerfile.go
          push: true
          tags: |
            suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/knowledge-graph-service-go:${{ steps.docker_tags.outputs.version }}
            suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/knowledge-graph-service-go:latest
          cache-from: type=registry,ref=suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/knowledge-graph-service-go:buildcache
          cache-to: type=registry,ref=suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/knowledge-graph-service-go:buildcache,mode=max
      
      # 更新Kubernetes部署
      - name: Trigger ArgoCD Sync
        run: |
          curl -X POST \
            -H "Authorization: Bearer ${{ secrets.ARGOCD_TOKEN }}" \
            -H "Content-Type: application/json" \
            ${{ secrets.ARGOCD_SERVER }}/api/v1/applications/knowledge-graph-service/sync
```

## Dockerfile说明

Go版本的服务使用多阶段构建Dockerfile，位于`Dockerfile.go`：

```dockerfile
# 构建阶段
FROM golang:1.20-alpine AS builder

WORKDIR /app

# 安装依赖
RUN apk add --no-cache git ca-certificates

# 复制go.mod和go.sum
COPY go.mod go.sum ./
RUN go mod download

# 复制源代码
COPY . .

# 构建应用
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o kg-service ./cmd/server
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o importer ./cmd/importer

# 运行阶段
FROM alpine:3.17

WORKDIR /app

# 安装运行时依赖
RUN apk add --no-cache ca-certificates tzdata && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone

# 创建非root用户
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
RUN mkdir -p /app/data /app/models /app/tmp /app/configs && \
    chown -R appuser:appgroup /app

# 从构建阶段复制二进制文件
COPY --from=builder /app/kg-service /app/
COPY --from=builder /app/importer /app/
COPY --from=builder /app/configs /app/configs

# 切换到非root用户
USER appuser

# 暴露端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q -O- http://localhost:8080/health || exit 1

# 设置默认命令
CMD ["/app/kg-service"]
```

## 测试策略

CI流程中包含多级测试：

1. **单元测试**：测试各模块的功能逻辑
2. **集成测试**：测试各组件间的交互
3. **API测试**：测试RESTful API的功能

### 运行测试

```bash
# 运行所有测试
go test ./...

# 运行特定包的测试
go test ./internal/api/...

# 运行测试并查看覆盖率
go test -cover ./...

# 生成HTML覆盖率报告
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out
```

## 部署流程

### 使用ArgoCD实现GitOps

索克生活知识图谱服务采用ArgoCD实现GitOps部署流程，主要步骤：

1. CI构建并推送Docker镜像
2. CI流程触发ArgoCD同步
3. ArgoCD拉取最新的Kubernetes配置
4. ArgoCD将变更应用到Kubernetes集群

### ArgoCD应用配置

ArgoCD应用配置示例：

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: knowledge-graph-service
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/suoke-life/knowledge-graph-service.git
    targetRevision: HEAD
    path: k8s/overlays/production
  destination:
    server: https://kubernetes.default.svc
    namespace: suoke
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
```

## 环境管理

本CI/CD流程支持多环境部署：

1. **开发环境**：对应`develop`分支，自动部署到开发环境
2. **测试环境**：对应`release/*`分支，手动触发部署到测试环境
3. **生产环境**：对应`main`分支或版本标签，手动触发部署到生产环境

### 分支策略

- `feature/*` - 功能开发分支
- `develop` - 开发分支，集成最新功能
- `release/*` - 版本预发布分支
- `main` - 主分支，包含生产代码
- `hotfix/*` - 热修复分支，用于紧急修复

## 版本管理

版本遵循[语义化版本](https://semver.org/)规则：

```
MAJOR.MINOR.PATCH
```

- **MAJOR**：不兼容的API变更
- **MINOR**：向后兼容的功能性新增
- **PATCH**：向后兼容的问题修正

### 创建新版本

```bash
# 创建版本标签
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## 安全扫描

CI流程中集成了安全扫描：

- 使用`gosec`进行代码安全分析
- 使用`trivy`扫描Docker镜像漏洞

## 常见问题排查

### CI失败问题

1. **测试失败**：检查测试日志，修复失败的测试用例
2. **Lint错误**：运行`golangci-lint run`检查并修复代码风格问题
3. **构建错误**：检查依赖项是否正确安装

### CD失败问题

1. **Docker构建失败**：检查Dockerfile和依赖
2. **推送镜像失败**：检查容器镜像仓库访问权限
3. **部署失败**：检查Kubernetes配置和ArgoCD日志

## 参考资源

- [GitHub Actions文档](https://docs.github.com/en/actions)
- [ArgoCD文档](https://argo-cd.readthedocs.io/)
- [Go测试指南](https://golang.org/doc/tutorial/add-a-test) 