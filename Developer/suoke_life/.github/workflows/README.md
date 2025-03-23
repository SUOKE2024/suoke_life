# 索克生活APP GitHub Actions 使用指南

本文档提供了索克生活APP项目中GitHub Actions工作流的使用指南，包括各工作流的功能说明、环境变量和secrets配置，以及如何手动触发部署等内容。

## 工作流概述

项目包含以下GitHub Actions工作流:

1. **comprehensive-cicd.yml** - 全面CI/CD流程
   - 自动检测服务代码变更并触发构建和部署
   - 支持手动指定部署服务和环境
   - 包含代码验证、构建、部署和验证等完整流程

2. **build-and-deploy.yml** - 兼容性构建与部署流程
   - 提供与早期版本兼容的构建和部署功能
   - 将逐步过渡到comprehensive-cicd.yml

3. **test.yml** - 测试工作流
   - 针对拉取请求运行代码检查和测试
   - 验证服务的代码质量，不执行部署

## 环境变量和Secrets配置

### 必需的Secrets

在GitHub仓库设置中配置以下Secrets:

| Secret名称 | 说明 | 示例 |
|------------|------|------|
| `ALIYUN_REGISTRY_USERNAME` | 阿里云容器镜像服务用户名 | `yourname@example.com` |
| `ALIYUN_REGISTRY_PASSWORD` | 阿里云容器镜像服务密码 | `password123` |
| `KUBE_CONFIG_DATA` | Base64编码的Kubernetes配置文件 | (Base64编码字符串) |
| `JWT_SECRET` | JWT令牌签名密钥 | `your-jwt-secret-key` |

### 可选的Secrets

| Secret名称 | 说明 | 示例 |
|------------|------|------|
| `SLACK_WEBHOOK` | Slack通知Webhook URL | `https://hooks.slack.com/...` |
| `DOCKER_BUILD_ARGS` | Docker构建参数 | `NODE_ENV=production` |

### 创建KUBE_CONFIG_DATA

在Linux/macOS系统上，使用以下命令创建KUBE_CONFIG_DATA:

```bash
cat ~/.kube/config | base64 | tr -d '\n'
```

## 手动触发部署

### 使用comprehensive-cicd.yml触发部署

1. 在GitHub仓库页面，点击"Actions"标签
2. 在左侧工作流列表中选择"索克生活APP全面CI/CD"
3. 点击"Run workflow"按钮
4. 选择要部署的分支
5. 配置以下参数:
   - **要部署的服务**: 输入服务名称，多个服务用逗号分隔，或输入"all"部署所有服务
   - **部署环境**: 选择"development"、"staging"或"production"
6. 点击"Run workflow"启动部署

### 使用本地部署脚本

除了GitHub Actions工作流，本项目还提供了本地部署脚本，用于在本地环境或服务器上执行部署操作：

```bash
# 部署所有服务到生产环境
./scripts/ci-cd/deploy-app.sh

# 部署指定服务到生产环境
./scripts/ci-cd/deploy-app.sh -s api-gateway

# 部署指定服务到指定环境
./scripts/ci-cd/deploy-app.sh -s user-service -e development

# 只检查部署状态而不执行部署
./scripts/ci-cd/deploy-app.sh -c
```

### 检查部署状态

项目提供了专门的脚本用于检查部署状态：

```bash
# 检查指定服务在指定命名空间的部署状态
./scripts/ci-cd/check-deployment.sh <服务名称> [命名空间]

# 示例：检查api-gateway在suoke命名空间的部署状态
./scripts/ci-cd/check-deployment.sh api-gateway suoke
```

检查脚本会显示以下信息：
- 部署状态（存在/不存在）
- Pod健康状态
- 服务和Ingress配置
- 最近事件和日志
- 访问URL（如果可用）

### 部署服务列表

可用的服务名称:

- `api-gateway` - API网关服务
- `rag-service` - RAG检索增强服务
- `user-service` - 用户服务
- `content-service` - 内容服务
- `voice-service` - 语音服务
- `web-search-service` - 网络搜索服务
- `agent-coordinator-service` - 代理协调服务
- `auth-service` - 认证服务

## 工作流运行状态监控

1. 在GitHub仓库页面，点击"Actions"标签
2. 在列表中找到正在运行或已完成的工作流
3. 点击工作流运行实例查看详细日志
4. 展开工作流步骤查看具体执行情况

## 部署环境说明

| 环境名称 | 命名空间 | 说明 |
|---------|---------|------|
| development | suoke-development | 开发环境，用于功能开发和测试 |
| staging | suoke-staging | 预发布环境，用于集成测试和验证 |
| production | suoke | 生产环境 |

## 常见问题解答

### Q: 部署失败，镜像无法拉取

A: 检查ALIYUN_REGISTRY_USERNAME和ALIYUN_REGISTRY_PASSWORD是否正确配置。可能的解决方案：
   - 确认Secrets已正确设置
   - 验证阿里云容器镜像服务账户是否有效
   - 检查网络连接是否正常
   - 若使用本地脚本，确保已登录到容器注册表

### Q: 部署后服务未能正常启动

A: 查看Pod日志了解失败原因，常见原因包括配置错误、资源不足或依赖服务不可用。使用以下命令检查：
   ```bash
   # 使用检查脚本查看详细状态
   ./scripts/ci-cd/check-deployment.sh <服务名称> <命名空间>
   
   # 或直接查看日志
   kubectl logs -n <命名空间> <pod名称>
   ```

### Q: 如何回滚到之前的版本？

A: 有以下几种方式执行回滚：
   - 手动触发工作流，选择之前成功部署的版本对应的分支或提交
   - 使用kubectl回滚：`kubectl rollout undo deployment/<服务名称> -n <命名空间>`
   - 如使用本地脚本，可指定特定版本：`./scripts/ci-cd/deploy-app.sh -s <服务名称> -v <之前的版本标签>`

### Q: 为什么只有部分服务被部署？

A: 工作流只会部署有代码变更的服务，或手动指定的服务。如果需要强制部署所有服务，使用以下选项：
   - GitHub Actions：选择"all"作为服务参数
   - 本地脚本：不使用-s参数或使用-f选项强制部署

## 最佳实践

1. **提交消息格式化**: 使用规范的提交消息格式，例如"feat(api-gateway): 添加用户认证功能"
2. **小批量提交**: 尽量小批量、频繁提交，避免大规模变更
3. **使用拉取请求**: 通过拉取请求进行代码审查，确保代码质量
4. **定期清理**: 定期清理旧的Docker镜像，避免占用过多存储空间
5. **监控部署**: 部署后监控服务性能和错误日志
6. **环境一致性**: 保持不同环境的配置一致性，减少环境差异导致的问题
7. **部署前测试**: 确保所有自动化测试通过后再部署到生产环境

## 自定义工作流

### 添加自定义服务

如需添加新的微服务到CI/CD工作流，请修改`comprehensive-cicd.yml`文件中的以下部分:

1. 在`detect-changes`作业的`filter`步骤中添加新服务:
```yaml
新服务名:
  - 'services/新服务名/**'
```

2. 在`build-and-deploy`作业的矩阵定义中包含新服务(如果有"all"选项)

### 添加自定义部署步骤

如需为特定服务添加自定义部署步骤，在`prepare-config`步骤的case语句中添加:

```yaml
"新服务名")
  # 这里添加特定于新服务的配置
  ;;
```

## 项目脚本说明

项目中的部署相关脚本位于`scripts/ci-cd/`目录下：

| 脚本名称 | 功能说明 |
|---------|---------|
| `deploy-app.sh` | 一键部署应用的多个服务 |
| `check-deployment.sh` | 检查部署状态 |
| `deploy-to-production.sh` | 部署到生产环境的脚本 |

这些脚本既可以在本地执行，也可以在CI/CD系统中使用。使用脚本时，请确保环境变量配置正确，可参考项目根目录的`.env-example`文件。 