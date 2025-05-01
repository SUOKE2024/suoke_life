# XiaoAI Service CI/CD 流程指南

本文档详细说明了 XiaoAI Service 的 CI/CD 自动化流程，包括测试、构建、发布和部署的完整过程。

## 流程概述

CI/CD 流程通过 GitHub Actions 自动化执行，主要包括以下阶段：

1. **测试**：执行代码风格检查和单元测试
2. **构建**：编译 TypeScript 代码并构建 Docker 镜像
3. **发布**：将 Docker 镜像推送到阿里云容器镜像仓库
4. **部署**：将应用部署到 Kubernetes 集群

## 触发方式

CI/CD 流程可以通过以下方式触发：

- **代码推送**：向 `main`、`master` 或 `develop` 分支推送代码
- **合并请求**：向 `main` 或 `master` 分支创建合并请求
- **手动触发**：在 GitHub Actions 界面手动触发工作流

## 环境配置

支持以下部署环境：

- **production**：生产环境 (命名空间: `suoke-services`)
- **staging**：预发布环境 (命名空间: `suoke-staging`)
- **development**：开发环境 (命名空间: `suoke-dev`)

## 镜像标签规则

镜像会使用以下命名规则自动打标签：

- **版本号标签**：`xiaoai-service:x.y.z`（来自 package.json）
- **提交标签**：`xiaoai-service:x.y.z-abcd1234`（版本号+提交哈希）
- **分支标签**：
  - `main`/`master` 分支：`latest` 和 `stable`
  - `develop` 分支：`develop`
  - 其他分支：使用分支名称
- **环境标签**：手动触发时，根据选择的环境设置为 `production`、`staging` 或 `development`

## 部署流程

1. 根据环境选择部署到相应的 Kubernetes 命名空间
2. 如果命名空间不存在，会自动创建
3. 使用 `envsubst` 处理部署文件中的环境变量
4. 应用 Kubernetes 配置并等待部署完成
5. 显示部署状态和服务信息

## 环境变量

CI/CD 流程中使用的主要环境变量：

- `DOCKER_REGISTRY`：阿里云容器镜像仓库地址（`suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke`）
- `SERVICE_VERSION`：服务版本号（从 package.json 获取）
- `ENV_NAME`：环境名称
- `NAMESPACE`：Kubernetes 命名空间

## 密钥配置

需要在 GitHub Secrets 中设置以下密钥：

- `ALIYUN_REGISTRY_USERNAME`：阿里云容器镜像服务用户名
- `ALIYUN_REGISTRY_PASSWORD`：阿里云容器镜像服务密码
- `KUBE_CONFIG`：Kubernetes 集群配置文件（Base64 编码）

## 版本发布流程

1. 更新 `package.json` 中的版本号
2. 更新 `CHANGELOG.md` 文件记录变更内容
3. 提交并推送到相应的分支
4. CI/CD 流程会自动触发构建和部署

## 故障排除

如果 CI/CD 流程失败，请检查以下问题：

1. GitHub Actions 日志中的错误信息
2. 确保所有必需的密钥已正确配置
3. 检查 Kubernetes 集群的连接状态
4. 验证阿里云容器镜像仓库的访问权限
5. 确保 Kubernetes 部署文件格式正确

## 手动部署

如需手动部署，可以执行以下步骤：

1. 手动触发 GitHub Actions 工作流
2. 选择要部署的环境（production/staging/development）
3. 点击"Run workflow"按钮启动部署流程

## 本地测试

在推送代码前，建议先在本地运行测试：

```bash
cd services/xiaoai-service
npm ci
npm run lint
npm run test
```

## 注意事项

- 生产环境部署前建议先在预发布环境进行测试
- 确保代码变更经过充分的测试和代码审查
- 部署后检查服务健康状态和日志，确保服务正常运行 