# 索克生活微服务CI/CD实现方案

## 1. 概述

索克生活应用采用微服务架构，CI/CD自动化流程覆盖从代码提交、测试、构建到部署的全流程，确保各个微服务能够高效、稳定、一致地交付到各环境。

### 1.1 CI/CD流程概览

![CI/CD流程](../assets/images/ci-cd-flow.png)

1. **代码提交**：开发人员将代码提交到Git仓库
2. **自动化测试**：触发代码检查、单元测试和集成测试
3. **构建镜像**：测试通过后构建Docker镜像并推送到镜像仓库
4. **部署准备**：生成Kubernetes配置文件
5. **自动部署**：将服务部署到开发环境
6. **环境提升**：手动或自动提升到预发布和生产环境
7. **部署验证**：部署后验证服务健康状态

## 2. 技术架构

### 2.1 工具链

- **版本控制**：GitHub
- **CI/CD平台**：GitHub Actions
- **容器化**：Docker
- **容器编排**：Kubernetes
- **镜像仓库**：阿里云容器镜像服务
- **应用配置**：Kustomize
- **健康检查**：Kubernetes Probe + HTTP健康检查接口

### 2.2 环境规划

索克生活应用采用以下环境分层：

| 环境 | 命名空间 | 用途 | 部署方式 | 资源配置 |
|-----|---------|-----|---------|---------|
| 开发环境(dev) | suoke-dev | 日常开发与测试 | 自动 | 低配置(1个副本) |
| 预发环境(staging) | suoke-staging | 集成测试与预发验证 | 自动(main分支) | 中配置(2个副本) |
| 生产环境(prod) | suoke-prod | 线上服务 | 手动触发 | 高配置(3个副本) |

## 3. CI/CD工作流配置

### 3.1 工作流模板

创建通用的CI/CD工作流模板(`service-ci-cd-template.yml`)，包含以下阶段：

1. **代码检查与测试**：
   - 代码风格检查
   - 单元测试
   - 集成测试
   - 安全检查
   - 测试覆盖率报告

2. **代码质量分析**：
   - 静态代码分析
   - 依赖安全扫描

3. **构建与推送镜像**：
   - 基于Docker构建镜像
   - 镜像标签策略(版本号、最新版、提交ID)
   - 推送到阿里云镜像仓库

4. **生成Kubernetes配置**：
   - 根据服务配置生成部署文件
   - 使用Kustomize管理多环境配置
   - 验证Kubernetes配置正确性

5. **环境部署**：
   - 开发环境自动部署
   - 预发环境条件部署(main分支)
   - 生产环境手动批准部署
   - 部署后健康检查验证

### 3.2 服务特定配置

为每个微服务创建基于模板的CI/CD工作流：

- `rag-service-ci-cd.yml`：RAG服务CI/CD配置
- `api-gateway-ci-cd.yml`：API网关服务CI/CD配置
- `knowledge-graph-service-ci-cd.yml`：知识图谱服务CI/CD配置
- 其它服务的CI/CD配置...

每个服务的配置可以定制：
- 服务名称与路径
- 服务版本
- 部署环境
- 端口配置
- 健康检查路径

## 4. 部署脚本与工具

### 4.1 CI/CD脚本套件

创建了一系列脚本以便于管理CI/CD流程：

1. **cicd.sh**：综合CI/CD管理工具
   ```bash
   # 显示帮助信息
   ./scripts/cicd.sh help
   
   # 列出所有可用服务
   ./scripts/cicd.sh list
   
   # 验证服务配置
   ./scripts/cicd.sh validate rag-service
   
   # 部署单个服务
   ./scripts/cicd.sh deploy rag-service dev 1.2.0
   
   # 查看服务状态
   ./scripts/cicd.sh status rag-service prod
   
   # 回滚服务版本
   ./scripts/cicd.sh rollback auth-service staging 1.1.0
   
   # 部署所有服务
   ./scripts/cicd.sh deploy-all dev
   ```

2. **deploy.sh**：服务部署专用脚本
   ```bash
   # 部署服务到指定环境
   ./scripts/deploy.sh rag-service dev 1.2.0
   ```

3. **validate_deployment.sh**：部署前验证与自动修复
   ```bash
   # 验证服务配置
   ./scripts/validate_deployment.sh rag-service
   
   # 验证并自动修复问题
   ./scripts/validate_deployment.sh rag-service --fix
   ```

### 4.2 验证检查项

`validate_deployment.sh`脚本会进行以下检查：

1. **Dockerfile检查**：
   - 存在性检查
   - 健康检查指令
   - 基础镜像标签(避免使用latest)

2. **Kubernetes配置检查**：
   - Deployment配置
   - Service配置
   - 资源限制
   - 健康检查探针
   - Kustomize配置

3. **服务代码检查**：
   - package.json配置
   - 健康检查接口实现
   - 必要脚本配置

当发现问题时，`--fix`选项可以自动修复常见问题。

## 5. 实施指南

### 5.1 设置GitHub Actions

1. **配置secrets**：
   - `REGISTRY_USERNAME`：镜像仓库用户名
   - `REGISTRY_PASSWORD`：镜像仓库密码
   - `KUBE_CONFIG_DEV`：开发环境的kubeconfig
   - `KUBE_CONFIG_STAGING`：预发环境的kubeconfig
   - `KUBE_CONFIG_PROD`：生产环境的kubeconfig

2. **设置分支保护**：
   - 保护`main`分支，要求代码审查
   - 保护`develop`分支，要求CI通过

### 5.2 服务接入CI/CD

新服务接入CI/CD流程的步骤：

1. 创建服务目录结构：`services/<service-name>/`
2. 实现健康检查接口：`GET /health`
3. 编写Dockerfile
4. 创建Kubernetes配置目录：`k8s/`
5. 创建CI/CD工作流配置

可以使用验证脚本自动创建必要文件：
```bash
./scripts/validate_deployment.sh <service-name> --fix
```

### 5.3 GitOps最佳实践

1. **分支策略**：
   - `feature/*`：功能开发分支
   - `develop`：开发集成分支，自动部署到dev环境
   - `main`：主分支，自动部署到staging环境，手动提升到prod环境

2. **提交规范**：
   - 使用语义化提交消息
   - 示例：`feat(auth): add OAuth2 support`
   - 版本号遵循语义化版本(SemVer)规范

3. **代码审查**：
   - 所有合并到develop和main的代码必须经过审查
   - CI通过是合并的前提条件

## 6. 监控与故障处理

### 6.1 部署监控

每次部署后会自动验证服务健康状态：

- Pod运行状态
- 健康检查探针
- HTTP健康检查接口

### 6.2 故障处理流程

1. **快速回滚**：
   ```bash
   ./scripts/cicd.sh rollback <service-name> <environment> <version>
   ```

2. **日志检查**：
   ```bash
   kubectl logs -n <namespace> <pod-name>
   ```

3. **事件查看**：
   ```bash
   kubectl get events -n <namespace> --field-selector involvedObject.name=<service-name>
   ```

4. **服务调试**：
   ```bash
   kubectl port-forward -n <namespace> <pod-name> <local-port>:<container-port>
   ```

## 7. 常见问题

### 7.1 部署失败问题排查

1. 检查GitHub Actions运行日志
2. 验证服务配置是否正确
   ```bash
   ./scripts/validate_deployment.sh <service-name>
   ```
3. 检查Kubernetes集群状态
4. 验证镜像是否正确推送到仓库

### 7.2 CI/CD性能优化

1. 使用缓存加速构建：
   - Node模块缓存
   - Docker构建缓存
2. 并行测试执行
3. 避免不必要的部署

## 8. 未来计划

1. **集成ArgoCD**：实现完整GitOps流程
2. **自动化测试扩展**：增加端到端测试
3. **蓝绿部署支持**：实现无缝部署策略
4. **金丝雀发布**：支持渐进式发布
5. **混沌工程**：引入故障注入测试 