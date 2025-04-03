# 认证服务 CI/CD 自动化流程

本文档描述了索克生活认证服务（auth-service）的持续集成与持续部署流程设计。

## 概述

CI/CD 流程通过 GitHub Actions 自动化执行，包括以下阶段：

1. **代码检查与测试**：执行代码质量检查、单元测试、集成测试和安全测试
2. **构建与镜像推送**：构建Docker镜像并推送至阿里云容器镜像服务
3. **部署到预发环境**：自动部署到Kubernetes预发环境
4. **部署到生产环境**：手动确认后部署到Kubernetes生产环境

## 工作流配置

工作流配置文件 `auth-service-cicd-workflow.yml` 需要移动到项目的 `.github/workflows` 目录并重命名为 `auth-service-ci-cd.yml`。

执行以下命令完成配置：

```bash
# 确保.github/workflows目录存在
mkdir -p ../../.github/workflows

# 复制工作流文件到正确位置
cp auth-service-cicd-workflow.yml ../../.github/workflows/auth-service-ci-cd.yml
```

## 环境变量与密钥

工作流使用以下密钥（需在GitHub仓库设置中配置）：

- `REGISTRY_USERNAME`: 阿里云容器镜像服务用户名
- `REGISTRY_PASSWORD`: 阿里云容器镜像服务密码
- `KUBE_CONFIG_STAGING`: 预发环境Kubernetes配置
- `KUBE_CONFIG_PRODUCTION`: 生产环境Kubernetes配置

## 触发条件

工作流在以下情况下触发：

- 推送到任何分支时，如果修改了 `services/auth-service/` 目录下的文件
- 针对主分支的PR，如果修改了 `services/auth-service/` 目录下的文件
- 手动触发（通过GitHub Actions界面）

## 部署策略

- **预发环境**：当代码推送到 `develop` 或 `main` 分支时自动部署
- **生产环境**：仅当代码推送到 `main` 分支且预发环境部署成功后部署

## 健康检查

部署完成后，工作流会执行以下健康检查：

1. 检查Kubernetes Pod状态
2. 对于生产环境，尝试请求服务健康检查端点 `https://auth.suoke.life/health`

## 版本控制

服务版本在工作流环境变量 `SERVICE_VERSION` 中定义，当需要发布新版本时，请更新此值。

## 故障排除

如遇部署问题，请检查：

1. GitHub Actions日志查看详细错误信息
2. 确认所有所需的密钥已正确配置
3. 检查Kubernetes配置是否正确
4. 验证服务健康检查端点是否可访问 