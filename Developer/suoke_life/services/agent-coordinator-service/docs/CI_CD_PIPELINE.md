# Agent Coordinator Service CI/CD流水线配置指南

## 概述

本文档详细说明了Agent Coordinator Service的CI/CD流水线配置，包括构建、测试、打包和部署过程。CI/CD流水线通过GitLab CI/CD实现，并与ArgoCD集成实现GitOps自动部署。

## CI/CD流水线架构

Agent Coordinator Service的CI/CD流水线包含以下主要阶段：

1. **代码质量检查**: 静态代码分析、代码风格检查和漏洞扫描
2. **测试**: 单元测试、集成测试和契约测试
3. **构建**: 构建Docker镜像并推送到容器镜像仓库
4. **部署**: 使用Helm Chart部署到不同环境

## GitLab CI/CD配置

### 主要阶段

```yaml
stages:
  - validate
  - test
  - build
  - security
  - release
  - deploy
```

### 环境变量

GitLab CI/CD使用以下环境变量：

| 变量名 | 描述 | 设置位置 |
|--------|------|----------|
| `DOCKER_REGISTRY` | 容器镜像仓库地址 | GitLab CI/CD变量 |
| `DOCKER_REGISTRY_USER` | 镜像仓库用户名 | GitLab CI/CD变量 (受保护) |
| `DOCKER_REGISTRY_PASSWORD` | 镜像仓库密码 | GitLab CI/CD变量 (受保护、掩码) |
| `SONAR_TOKEN` | SonarQube访问令牌 | GitLab CI/CD变量 (受保护、掩码) |
| `KUBE_CONFIG` | Kubernetes配置 | GitLab CI/CD变量 (受保护、掩码) |

### 代码质量检查

```yaml
lint:
  stage: validate
  image: node:18-alpine
  script:
    - npm ci
    - npm run lint
  cache:
    paths:
      - node_modules/

sonarqube:
  stage: validate
  image: 
    name: sonarsource/sonar-scanner-cli:latest
    entrypoint: [""]
  script:
    - sonar-scanner -Dsonar.projectKey=agent-coordinator-service -Dsonar.sources=. -Dsonar.host.url=https://sonar.suoke.life -Dsonar.login=$SONAR_TOKEN
```

### 测试

```yaml
unit_test:
  stage: test
  image: node:18-alpine
  script:
    - npm ci
    - npm run test:unit
  coverage: '/All files[^|]*\|[^|]*\s+([\d\.]+)/'
  artifacts:
    paths:
      - coverage/
    reports:
      junit: junit.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml

integration_test:
  stage: test
  image: node:18-alpine
  services:
    - name: redis:alpine
      alias: redis
  variables:
    REDIS_HOST: redis
    REDIS_PORT: 6379
  script:
    - npm ci
    - npm run test:integration
  artifacts:
    paths:
      - test-results/

contract_test:
  stage: test
  image: node:18-alpine
  services:
    - name: redis:alpine
      alias: redis
  variables:
    REDIS_HOST: redis
    REDIS_PORT: 6379
  script:
    - npm ci
    - npm run test:contract
  artifacts:
    paths:
      - pacts/
```

### 构建

```yaml
build_image:
  stage: build
  image: docker:20.10.16
  services:
    - docker:20.10.16-dind
  variables:
    DOCKER_TLS_CERTDIR: "/certs"
  script:
    - docker login -u $DOCKER_REGISTRY_USER -p $DOCKER_REGISTRY_PASSWORD $DOCKER_REGISTRY
    - docker build -t $DOCKER_REGISTRY/suoke/agent-coordinator-service:$CI_COMMIT_SHA .
    - docker push $DOCKER_REGISTRY/suoke/agent-coordinator-service:$CI_COMMIT_SHA
    - |
      if [[ "$CI_COMMIT_BRANCH" == "main" ]]; then
        docker tag $DOCKER_REGISTRY/suoke/agent-coordinator-service:$CI_COMMIT_SHA $DOCKER_REGISTRY/suoke/agent-coordinator-service:latest
        docker push $DOCKER_REGISTRY/suoke/agent-coordinator-service:latest
      fi
    - |
      if [[ "$CI_COMMIT_TAG" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        docker tag $DOCKER_REGISTRY/suoke/agent-coordinator-service:$CI_COMMIT_SHA $DOCKER_REGISTRY/suoke/agent-coordinator-service:${CI_COMMIT_TAG#v}
        docker push $DOCKER_REGISTRY/suoke/agent-coordinator-service:${CI_COMMIT_TAG#v}
      fi
```

### 安全扫描

```yaml
container_scanning:
  stage: security
  image: 
    name: aquasec/trivy:latest
    entrypoint: [""]
  script:
    - trivy image --format json --output trivy-results.json $DOCKER_REGISTRY/suoke/agent-coordinator-service:$CI_COMMIT_SHA
  artifacts:
    paths:
      - trivy-results.json
    when: always
```

### 部署

```yaml
deploy_test:
  stage: deploy
  image: 
    name: bitnami/kubectl:latest
    entrypoint: [""]
  variables:
    ENVIRONMENT: test
  script:
    - mkdir -p ~/.kube
    - echo "$KUBE_CONFIG" > ~/.kube/config
    - kubectl config use-context suoke-cluster-test
    - helm upgrade --install agent-coordinator-test ./helm/agent-coordinator --namespace suoke-test --set image.tag=$CI_COMMIT_SHA --set environment=testing
  environment:
    name: test
    url: https://api-test.suoke.life/api/v1/agents/coordinator
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'

deploy_prod:
  stage: deploy
  image: 
    name: bitnami/kubectl:latest
    entrypoint: [""]
  variables:
    ENVIRONMENT: production
  script:
    - mkdir -p ~/.kube
    - echo "$KUBE_CONFIG" > ~/.kube/config
    - kubectl config use-context suoke-cluster-prod
    - helm upgrade --install agent-coordinator ./helm/agent-coordinator --namespace suoke --set image.tag=${CI_COMMIT_TAG#v} --set environment=production
  environment:
    name: production
    url: https://api.suoke.life/api/v1/agents/coordinator
  rules:
    - if: '$CI_COMMIT_TAG =~ /^v[0-9]+\.[0-9]+\.[0-9]+$/'
  when: manual
```

## ArgoCD配置

### 应用定义

ArgoCD通过以下应用定义实现GitOps部署：

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: agent-coordinator
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://gitlab.suoke.life/suoke/agent-coordinator-service.git
    targetRevision: HEAD
    path: helm/agent-coordinator
  destination:
    server: https://kubernetes.default.svc
    namespace: suoke
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=false
      - PruneLast=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
```

## 流水线工作流程

1. **开发者工作流**
   - 开发人员在功能分支上开发新功能
   - 提交代码触发验证和测试阶段
   - 创建合并请求进行代码审查
   - 合并到主分支后自动构建镜像并部署到测试环境

2. **发布流程**
   - 创建语义化版本标签(如v1.2.0)触发生产部署流水线
   - 通过手动批准后部署到生产环境
   - ArgoCD监控Helm Chart仓库变更并自动同步部署

3. **测试策略**
   - 每个提交运行单元测试和静态代码分析
   - 合并到主分支时运行完整的集成测试和契约测试
   - 生产部署前进行完整的安全扫描和合规性检查

## 故障排除

常见问题及解决方案：

1. **镜像构建失败**
   - 检查Dockerfile语法
   - 确认构建依赖项可访问
   - 验证镜像仓库凭据

2. **测试失败**
   - 检查测试日志定位失败原因
   - 验证测试环境配置是否正确
   - 确认测试依赖服务是否可用

3. **部署失败**
   - 检查Helm Chart配置
   - 确认Kubernetes集群连接状态
   - 查看ArgoCD同步状态和日志

## 最佳实践

1. **CI/CD流水线优化**
   - 使用缓存加速构建过程
   - 并行运行独立任务
   - 定期清理旧的构建产物

2. **安全实践**
   - 所有敏感凭据使用GitLab CI/CD变量存储
   - 在CI/CD流程中包含安全扫描
   - 使用最小特权原则配置部署凭据

3. **监控与通知**
   - 配置流水线失败通知
   - 监控部署状态和应用健康状况
   - 建立部署回滚机制