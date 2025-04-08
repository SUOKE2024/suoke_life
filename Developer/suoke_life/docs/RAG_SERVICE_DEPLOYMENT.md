# RAG服务部署指南

本文档介绍如何使用CI/CD自动化流程部署RAG服务到Kubernetes集群。

## 前提条件

1. 已安装以下工具：
   - GitHub CLI (`gh`)
   - kubectl
   - make
   - Docker

2. 已配置好访问GitHub的权限和访问Kubernetes集群的配置：
   - 已通过 `gh auth login` 登录GitHub
   - 已配置 `kubectl` 的访问凭证

## 快速部署

我们提供了简单的命令来触发部署流程：

```bash
# 部署RAG服务到生产环境
make deploy-rag

# 检查部署状态
make rag-status
```

## 高级部署选项

如果需要更多自定义选项，可以直接使用部署脚本：

```bash
# 查看帮助信息
./scripts/deploy_rag_service.sh --help

# 示例：部署到开发环境，使用指定分支和版本
./scripts/deploy_rag_service.sh --env dev --branch develop --version v1.2.3

# 示例：部署到生产环境，跳过测试，只构建单架构镜像
./scripts/deploy_rag_service.sh --env prod --skip-tests --single-arch
```

## 部署配置

我们使用GitHub Actions作为CI/CD工具，部署流程如下：

1. **测试阶段**：
   - 执行静态代码检查
   - 运行单元测试
   - 运行集成测试
   - 执行TCM特征测试

2. **构建阶段**：
   - 自动生成版本号
   - 登录阿里云容器镜像服务
   - 构建并推送多架构Docker镜像（AMD64和ARM64）
   - 标记版本镜像和最新镜像

3. **部署阶段**：
   - 设置Kubernetes上下文
   - 创建/确认suoke-prod命名空间
   - 创建镜像拉取凭证
   - 更新Kustomize配置中的镜像版本
   - 应用配置变更
   - 验证部署状态
   - 发送部署通知

## Kubernetes部署配置

我们使用Kustomize来管理Kubernetes配置，部署结构如下：

- `k8s/base/`: 基础配置
- `k8s/overlays/prod/`: 生产环境特定配置
- `k8s/patches/`: 补丁配置

## 部署故障排查

如果部署失败，请执行以下步骤：

1. 检查部署状态：
   ```bash
   make rag-status
   ```

2. 检查容器日志：
   ```bash
   kubectl logs -f -l app=rag-service -n suoke-prod
   ```

3. 查看部署事件：
   ```bash
   kubectl get events -n suoke-prod --sort-by='.lastTimestamp' | grep rag-service
   ```

4. 如果需要重新部署：
   ```bash
   make deploy-rag
   ```

## 本地开发和测试

在提交代码前，建议先在本地进行测试：

```bash
# 运行所有测试
cd services/rag-service
make test

# 或者通过项目根目录运行测试
make run-tests
# 当提示输入服务路径时，输入 rag-service
```

## 常见问题

**Q: 如何回滚到之前的版本？**

A: 使用以下命令回滚：

```bash
kubectl rollout undo deployment/rag-service -n suoke-prod
```

**Q: 如何查看部署历史？**

A: 使用以下命令查看：

```bash
kubectl rollout history deployment/rag-service -n suoke-prod
```

**Q: 如何查看工作流运行状态？**

A: 访问GitHub仓库的Actions页面，或使用以下命令：

```bash
gh workflow view rag-service-ci-cd
``` 