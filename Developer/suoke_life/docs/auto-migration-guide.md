# 微服务自动迁移到ArgoCD使用指南

本指南介绍如何使用`auto_migrate_to_argocd.sh`脚本将所有微服务自动迁移到ArgoCD并实现持续部署。

## 功能概述

`auto_migrate_to_argocd.sh`脚本提供以下功能：

1. 自动安装与配置ArgoCD（可选）
2. 自动扫描并发现所有微服务
3. 自动为每个微服务生成ArgoCD应用定义
4. 自动更新CI/CD工作流以集成ArgoCD
5. 自动部署应用到ArgoCD（可选）

## 前提条件

- Kubernetes集群已配置好
- kubectl已安装并配置
- jq已安装
- Git已安装并配置

## 基本用法

### 安装ArgoCD并迁移所有微服务

```bash
./scripts/auto_migrate_to_argocd.sh --install-argocd --argocd-host argocd.suoke.life
```

这将执行以下操作：
- 安装ArgoCD并配置Ingress
- 发现所有微服务
- 生成ArgoCD应用定义
- 更新CI/CD工作流
- 部署应用到ArgoCD

### 使用已有的ArgoCD实例迁移微服务

```bash
./scripts/auto_migrate_to_argocd.sh --argocd-host argocd.suoke.life
```

这将执行以下操作：
- 跳过ArgoCD安装，使用现有实例
- 执行其他所有迁移和部署步骤

## 高级用法

### 仅迁移特定服务组

```bash
# 仅迁移核心服务组
./scripts/auto_migrate_to_argocd.sh --service-group core --argocd-host argocd.suoke.life

# 仅迁移知识服务组
./scripts/auto_migrate_to_argocd.sh --service-group knowledge --argocd-host argocd.suoke.life
```

可用的服务组：
- `core`: 核心服务（API网关、认证服务、用户服务）
- `diagnosis`: 四诊服务
- `knowledge`: 知识服务
- `ai`: AI服务
- `all`: 所有服务（默认）

### 仅针对特定环境

```bash
# 仅针对开发环境
./scripts/auto_migrate_to_argocd.sh --environments dev --argocd-host argocd.suoke.life

# 针对开发和测试环境，不包括生产环境
./scripts/auto_migrate_to_argocd.sh --environments dev,staging --argocd-host argocd.suoke.life
```

### 自定义ArgoCD命名空间

```bash
./scripts/auto_migrate_to_argocd.sh --argocd-namespace suoke-argocd --argocd-host argocd.suoke.life
```

### 完整选项示例

```bash
./scripts/auto_migrate_to_argocd.sh \
  --install-argocd \
  --argocd-namespace argocd \
  --argocd-host argocd.suoke.life \
  --ingress-class nginx \
  --environments dev,staging,prod \
  --service-group knowledge
```

## 选项说明

| 选项 | 描述 | 默认值 |
|------|------|--------|
| `--install-argocd` | 安装ArgoCD（如果已安装则跳过） | 不安装 |
| `--argocd-namespace` | ArgoCD命名空间 | `argocd` |
| `--argocd-host` | ArgoCD访问域名 | 空（不设置Ingress） |
| `--ingress-class` | Ingress类名 | `nginx` |
| `--environments` | 要部署的环境（逗号分隔） | `dev,staging,prod` |
| `--service-group` | 服务组 | `all` |
| `--help` | 显示帮助信息 | - |

## 迁移后的后续步骤

迁移完成后，您需要：

1. 确保ArgoCD能够访问Git仓库
2. 在GitHub项目设置中添加以下Secrets:
   - `ARGOCD_SERVER`: ArgoCD服务器地址
   - `ARGOCD_USERNAME`: ArgoCD用户名
   - `ARGOCD_PASSWORD`: ArgoCD密码
3. 验证ArgoCD中的应用同步状态

## 故障排除

### ArgoCD安装失败

```bash
# 手动安装ArgoCD
./scripts/install_argocd.sh --namespace argocd --ingress-host argocd.suoke.life

# 然后不安装ArgoCD，仅执行迁移
./scripts/auto_migrate_to_argocd.sh --argocd-host argocd.suoke.life
```

### 应用部署失败

```bash
# 手动部署ArgoCD应用
./scripts/setup_argocd_apps.sh argocd.suoke.life
```

### 特定服务缺少Kubernetes配置

如果某些服务缺少Kubernetes配置，脚本会跳过这些服务并发出警告。请为这些服务添加必要的Kubernetes配置文件，目录结构如下：

```
services/
  ├── your-service/
      ├── k8s/
          ├── base/
          ├── overlays/
              ├── dev/
              ├── staging/
              ├── prod/
```

## 示例场景

### 场景1: 开发环境快速迁移

```bash
./scripts/auto_migrate_to_argocd.sh --environments dev --argocd-host argocd-dev.suoke.life
```

### 场景2: 新集群完整设置

```bash
./scripts/auto_migrate_to_argocd.sh --install-argocd --argocd-host argocd.suoke.life
```

### 场景3: 分批迁移服务

```bash
# 第一步：迁移核心服务
./scripts/auto_migrate_to_argocd.sh --service-group core --argocd-host argocd.suoke.life

# 第二步：迁移知识服务
./scripts/auto_migrate_to_argocd.sh --service-group knowledge --argocd-host argocd.suoke.life

# 第三步：迁移其余服务
./scripts/auto_migrate_to_argocd.sh --service-group ai --argocd-host argocd.suoke.life
./scripts/auto_migrate_to_argocd.sh --service-group diagnosis --argocd-host argocd.suoke.life
```

## 注意事项

1. 脚本会自动提交变更到Git仓库，因此请确保您的本地仓库是最新的并且没有未提交的更改
2. 如果要部署到生产环境，建议先在非生产环境中进行测试
3. ArgoCD默认使用HTTPS，请确保您的域名已配置好SSL证书或使用Let's Encrypt自动签发证书
4. 根据服务的规模和复杂度，迁移过程可能需要几分钟到几十分钟不等 