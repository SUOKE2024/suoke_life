# 索克生活平台 CI/CD 和 ArgoCD 集成指南

## 项目概述

本文档描述了索克生活平台的CI/CD流程和ArgoCD集成方案，旨在实现自动化的构建、测试、部署和运维流程。

## 目录结构

```
.
├── .github/workflows/           # GitHub Actions工作流定义
│   ├── templates/               # 工作流模板
│   │   ├── service-ci-cd-template.yml              # 基础CI/CD模板
│   │   └── service-ci-cd-template-with-argocd.yml  # 集成ArgoCD的CI/CD模板
│   ├── api-gateway-ci-cd.yml    # API网关服务CI/CD工作流
│   ├── auth-service-ci-cd.yml   # 认证服务CI/CD工作流
│   ├── rag-service-ci-cd.yml    # RAG服务CI/CD工作流
│   ├── ...                      # 其他服务的CI/CD工作流
│   └── migrate-to-argocd.yml    # 迁移到ArgoCD的工作流
├── argocd-apps/                 # ArgoCD应用定义文件（由迁移工作流生成）
├── scripts/                     # 自动化脚本
│   ├── cicd.sh                  # CI/CD管理脚本
│   ├── deploy.sh                # 服务部署脚本
│   ├── create_cicd_workflow.sh  # 创建CI/CD工作流配置脚本
│   ├── install_argocd.sh        # ArgoCD安装脚本
│   ├── run_tests.sh             # 测试运行脚本
│   ├── setup_argocd_apps.sh     # ArgoCD应用部署脚本
│   └── validate_deployment.sh   # 部署配置验证脚本
├── services/                    # 微服务目录
│   ├── api-gateway/             # API网关服务
│   │   ├── Dockerfile           # Docker构建文件
│   │   ├── k8s/                 # Kubernetes配置
│   │   │   ├── base/            # 基础配置
│   │   │   ├── overlays/        # 环境特定配置
│   │   │   │   ├── dev/         # 开发环境
│   │   │   │   ├── staging/     # 测试环境
│   │   │   │   └── prod/        # 生产环境
│   │   └── ...                  # 服务源代码
│   ├── auth-service/            # 认证服务
│   ├── rag-service/             # RAG服务
│   │   ├── Dockerfile
│   │   ├── tests/               # 测试目录
│   │   │   ├── test_kg_reasoning.go        # 知识图谱推理测试
│   │   │   ├── test_multimodal.go          # 多模态搜索测试
│   │   │   ├── test_multi_source.go        # 多源检索测试
│   │   │   ├── test_adaptive.go            # 自适应学习测试
│   │   │   ├── test_tcm_features.go        # TCM特征分析测试
│   │   │   ├── run_tests.sh                # 测试运行脚本
│   │   │   └── ...
│   │   └── ...
│   └── ...                      # 其他微服务
└── docs/                        # 文档
    ├── argocd-guide.md          # ArgoCD使用指南
    └── ...                      # 其他文档
```

## CI/CD流程

### 工作流程概述

1. **代码提交** - 开发人员将代码提交到GitHub仓库
2. **触发CI/CD** - GitHub Actions自动触发CI/CD工作流
3. **代码检查** - 运行代码检查和测试
4. **构建镜像** - 构建Docker镜像并推送到镜像仓库
5. **更新配置** - 更新Kubernetes配置文件中的镜像版本
6. **部署应用** - 部署应用到Kubernetes集群（直接部署或通过ArgoCD）
7. **验证部署** - 验证部署状态和应用健康状况

### 测试阶段细节

测试阶段根据服务类型包含不同的测试步骤：

1. **基础测试** - 所有服务通用
   - 代码格式检查 (go fmt, linting)
   - 静态代码分析 (go vet)
   - 单元测试 (go test)

2. **集成测试** - 验证服务间交互
   - API集成测试
   - 数据流测试

3. **专项测试** - 针对特定服务功能
   - **RAG服务特有测试**：
     - 知识图谱测试：验证知识图谱推理能力
     - 多模态测试：测试图像和音频结合文本的搜索能力
     - 多源检索测试：测试从多个知识源检索信息的能力
     - 自适应学习测试：测试RAG服务根据反馈进行调整的能力
     - **TCM特征分析测试**：测试中医特色功能，包括：
       - 舌诊分析
       - 面诊分析
       - 脉诊分析
       - 声音分析
       - 体质辨识

### 手动触发部署

除了自动触发外，还可以通过以下方式手动触发部署：

1. **GitHub UI** - 在GitHub仓库的Actions页面触发工作流
2. **部署脚本** - 使用`scripts/deploy.sh`脚本触发部署
   ```bash
   ./scripts/deploy.sh rag-service dev 1.2.0
   ```
3. **Make命令** - 使用Makefile中定义的命令
   ```bash
   make run-ci-cd
   ```

## ArgoCD集成

### 集成架构

将ArgoCD集成到CI/CD流程中，采用GitOps方式管理应用部署：

1. CI流程负责代码检查、测试、构建镜像和更新配置
2. CI流程完成后，更新配置会被提交回Git仓库
3. ArgoCD监控Git仓库变化，自动将新配置应用到Kubernetes集群

### 迁移到ArgoCD

通过`migrate-to-argocd`工作流可以将现有服务迁移到ArgoCD管理：

1. 在GitHub仓库的Actions页面触发`migrate-to-argocd`工作流
2. 选择要迁移的服务或服务组
3. 工作流将自动创建ArgoCD应用定义并更新CI/CD配置

也可以在本地运行迁移工作流：

```bash
# 安装和配置ArgoCD
./scripts/install_argocd.sh --namespace argocd --ingress-host argocd.suoke.life

# 部署ArgoCD应用
./scripts/setup_argocd_apps.sh argocd.suoke.life
```

## 命令行工具使用指南

### CI/CD管理脚本 (cicd.sh)

全面的CI/CD管理脚本，支持部署、验证、状态查询和回滚：

```bash
# 验证服务配置
./scripts/cicd.sh validate rag-service

# 部署服务
./scripts/cicd.sh deploy rag-service dev 1.2.0

# 检查部署状态
./scripts/cicd.sh status rag-service dev

# 回滚服务
./scripts/cicd.sh rollback rag-service dev 1.1.0

# 部署所有服务
./scripts/cicd.sh deploy-all dev

# 查看服务列表
./scripts/cicd.sh list
```

### 部署脚本 (deploy.sh)

简化的部署脚本，用于触发GitHub Actions工作流：

```bash
./scripts/deploy.sh <服务名称> <部署环境> [版本号]
```

### CI/CD工作流创建脚本 (create_cicd_workflow.sh)

创建或更新服务的CI/CD工作流配置：

```bash
# 基本用法
./scripts/create_cicd_workflow.sh <服务路径> [部署名称] [是否添加TCM测试]

# 示例：为RAG服务创建工作流，添加TCM特征测试
./scripts/create_cicd_workflow.sh rag-service rag-service true

# 示例：为认证服务创建工作流，不添加TCM特征测试
./scripts/create_cicd_workflow.sh auth-service auth-server false
```

还可以通过Makefile命令以交互方式运行：

```bash
make create-cicd
```

### 测试运行脚本 (run_tests.sh)

用于运行服务的测试套件：

```bash
cd services/rag-service/tests
./run_tests.sh --mode <kg|multimodal|multi_source|adaptive|tcm|all> [--mock] [--verbose] [--clean]
```

通过Makefile命令以交互方式运行：

```bash
make run-tests
```

### 验证脚本 (validate_deployment.sh)

验证服务的部署配置是否符合要求：

```bash
./scripts/validate_deployment.sh <服务名称>
```

### ArgoCD安装脚本 (install_argocd.sh)

在Kubernetes集群中安装和配置ArgoCD：

```bash
./scripts/install_argocd.sh --namespace argocd --ingress-host argocd.suoke.life
```

### ArgoCD应用部署脚本 (setup_argocd_apps.sh)

将ArgoCD应用定义部署到ArgoCD服务器：

```bash
./scripts/setup_argocd_apps.sh argocd.suoke.life
```

## 维护指南

### 添加新服务

1. 在`services/`目录下创建新服务目录，包含Dockerfile和Kubernetes配置
2. 运行`./scripts/validate_deployment.sh <新服务名称>`验证配置
3. 创建新服务的CI/CD工作流配置：
   ```bash
   ./scripts/create_cicd_workflow.sh <新服务名称>
   ```
4. 添加新服务到ArgoCD：
   - 运行`migrate-to-argocd`工作流，选择新服务
   - 或手动创建ArgoCD应用定义

### 添加TCM特征测试

要将TCM特征测试添加到现有服务：

1. **创建测试文件目录和脚本**:
   ```bash
   mkdir -p services/<服务名称>/tests/test_data/{images,audio}
   cp services/rag-service/tests/test_tcm_features.go services/<服务名称>/tests/
   cp services/rag-service/tests/run_tests.sh services/<服务名称>/tests/
   ```

2. **更新CI/CD工作流配置**:
   ```bash
   ./scripts/create_cicd_workflow.sh <服务名称> <服务名称> true
   ```

3. **添加测试数据**:
   将必要的测试样本复制到`test_data`目录中

### 更新CI/CD模板

1. 修改`.github/workflows/templates/`目录下的模板文件
2. 使用新模板更新现有服务的CI/CD工作流：
   - 通过`create_cicd_workflow.sh`脚本批量更新
   - 或手动更新各个服务的工作流文件

### 故障排除

1. **CI/CD工作流失败**
   - 检查GitHub Actions运行日志
   - 验证服务配置：`./scripts/validate_deployment.sh <服务名称>`
   - 检查凭据是否正确配置

2. **测试失败**
   - 检查测试日志：`services/<服务名称>/tests/test_results/`
   - 运行单个测试：`cd services/<服务名称>/tests && ./run_tests.sh --mode <测试类型> --verbose`
   - 检查测试依赖项是否正确安装

3. **ArgoCD同步失败**
   - 检查ArgoCD Web界面的应用同步状态
   - 验证Kubernetes清单是否有效
   - 检查Git仓库连接和凭据

4. **部署后应用不可用**
   - 检查Pod状态：`kubectl get pods -n suoke-<环境>`
   - 查看Pod日志：`kubectl logs <pod名称> -n suoke-<环境>`
   - 验证服务和Ingress配置

## 最佳实践

1. **遵循GitOps原则**
   - 所有配置通过Git管理
   - 避免直接修改集群状态

2. **环境一致性**
   - 使用相同的模板和脚本管理所有环境
   - 通过kustomize处理环境差异

3. **自动化验证**
   - 在部署前运行验证脚本
   - 在CI流程中包含自动测试

4. **滚动更新**
   - 配置适当的部署策略和健康检查
   - 使用滚动更新最小化停机时间

5. **版本控制**
   - 为所有镜像和配置指定明确的版本
   - 保留版本历史以支持回滚

6. **测试驱动开发**
   - 为新功能编写测试
   - 确保测试覆盖关键业务逻辑

## 参考资料

- [索克生活TCM特征测试指南](services/rag-service/tests/docs/TCM_FEATURES_TESTING.md)
- [ArgoCD使用指南](docs/argocd-guide.md)
- [GitHub Actions文档](https://docs.github.com/cn/actions)
- [Kubernetes文档](https://kubernetes.io/zh/docs/home/)
- [ArgoCD官方文档](https://argo-cd.readthedocs.io/) 