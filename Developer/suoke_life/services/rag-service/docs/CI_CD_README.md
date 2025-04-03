# RAG服务 CI/CD 流程说明

## 概述

本文档介绍了RAG服务的持续集成和持续部署(CI/CD)流程，该流程通过GitHub Actions自动化构建、测试和部署过程，确保代码质量和服务稳定性。

## CI/CD 流程架构

RAG服务的CI/CD流水线包含以下主要环节：

1. **代码检查与测试**：进行代码风格检查、类型检查和单元测试
2. **安全扫描**：对依赖项和容器镜像进行安全扫描
3. **构建镜像**：构建Docker镜像并推送到阿里云容器镜像服务
4. **部署环境**：自动部署到开发、预发布和生产环境
5. **性能测试**：对部署环境进行性能和负载测试
6. **功能验证**：验证部署后的服务功能是否正常
7. **部署通知**：通过钉钉推送部署结果通知

## 自动化触发规则

CI/CD流程根据不同的分支和事件自动触发：

- **main分支推送**：触发完整CI/CD流程，部署到开发环境
- **release/*分支推送**：触发完整CI/CD流程，部署到预发布和生产环境
- **feature/*分支推送**：仅触发代码检查、测试和安全扫描
- **Pull Request到main分支**：触发代码检查、测试和安全扫描
- **手动触发**：可选择目标环境手动触发部署

## 环境配置

系统包含三个部署环境，每个环境有不同的配置和资源：

### 开发环境 (dev)
- URL: https://dev.api.suoke.life/rag
- Kubernetes命名空间: suoke-dev
- 资源配置: 低资源配置，适合开发和测试
- 触发条件: 所有main分支提交

### 预发布环境 (staging)
- URL: https://staging.api.suoke.life/rag
- Kubernetes命名空间: suoke-staging
- 资源配置: 中等资源配置，接近生产环境
- 触发条件: release/*分支提交

### 生产环境 (prod)
- URL: https://api.suoke.life/rag
- Kubernetes命名空间: suoke-production
- 资源配置: 高资源配置，满足生产需求
- 触发条件: release/*分支提交，经过预发布环境验证后

## CI/CD 步骤详解

### 1. 代码检查与测试 (lint-test)

该阶段执行以下操作：
- 使用Black检查代码格式
- 使用MyPy进行静态类型检查
- 使用Pylint进行代码风格检查
- 运行单元测试并生成覆盖率报告

### 2. 安全扫描 (security-scan)

该阶段执行以下操作：
- 使用Snyk扫描Python依赖
- 使用Trivy扫描容器镜像中的漏洞

### 3. 构建和推送镜像 (build-push)

该阶段执行以下操作：
- 生成版本号
- 构建Docker镜像
- 推送到阿里云容器镜像服务
- 使用缓存加速构建过程

### 4. 部署到开发环境 (deploy-dev)

该阶段执行以下操作：
- 配置Kubernetes凭证
- 使用Kustomize更新镜像版本
- 应用Kubernetes配置
- 验证部署状态
- 执行健康检查

### 5. 开发环境性能测试 (performance-test-dev)

该阶段执行以下操作：
- 使用Locust进行负载测试
- 分析性能测试结果
- 生成并上传性能报告

### 6. 部署到预发布环境 (deploy-staging)

与开发环境部署类似，但配置不同，且仅在特定条件下触发。

### 7. 预发布环境性能测试 (performance-test-staging)

与开发环境性能测试类似，但测试参数更严格。

### 8. 部署到生产环境 (deploy-prod)

与预发布环境部署类似，但配置不同，且仅在预发布环境验证通过后触发。

### 9. 发送通知 (notify)

该阶段执行以下操作：
- 检查所有步骤的执行状态
- 生成通知消息
- 通过钉钉发送部署结果通知

## 如何使用

### 手动触发部署

1. 在GitHub仓库页面，点击"Actions"选项卡
2. 选择"RAG服务 CI/CD 流水线"工作流
3. 点击"Run workflow"按钮
4. 从下拉菜单中选择目标分支
5. 选择部署环境 (dev/staging/prod)
6. 点击"Run workflow"按钮开始部署

### 日常开发流程

1. 开发新功能时，从main分支创建feature/*分支
2. 在feature分支上开发和测试
3. 提交Pull Request到main分支，触发代码检查和测试
4. 合并到main分支后，自动部署到开发环境
5. 确认开发环境功能正常后，创建release/*分支
6. release/*分支提交将自动部署到预发布和生产环境

## 故障排查

如果CI/CD过程中出现问题，可以按照以下步骤进行排查：

1. 检查GitHub Actions运行日志，识别失败的步骤
2. 根据失败步骤的日志信息，定位具体问题
3. 对于部署问题，可以使用kubectl命令查看Kubernetes资源状态
4. 检查服务健康状态和日志
5. 修复问题后重新触发CI/CD流程

## 扩展与定制

CI/CD流程可以根据需求进行扩展和定制：

1. 修改`.github/workflows/ci-cd.yml`文件
2. 添加新的测试或部署步骤
3. 调整触发条件和环境配置
4. 更新安全扫描规则

## 最佳实践

1. 保持较小的代码提交，便于识别问题
2. 在本地执行测试后再提交代码
3. 定期审查和更新依赖项
4. 为新功能编写单元测试
5. 监控性能测试结果，及时发现性能退化
6. 保护敏感信息，使用GitHub Secrets存储密钥

## 参考资料

- [GitHub Actions文档](https://docs.github.com/en/actions)
- [Kubernetes文档](https://kubernetes.io/docs/)
- [Docker文档](https://docs.docker.com/)
- [Locust负载测试工具](https://locust.io/) 