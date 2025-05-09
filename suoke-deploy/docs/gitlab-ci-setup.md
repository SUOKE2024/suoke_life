# GitLab CI/CD 配置指南

## 前言

本文档提供如何在GitLab项目中设置CI/CD变量以确保索克生活APP后端微服务的自动化构建和部署正常运行。

## 必要的CI/CD变量

以下变量需要在GitLab项目的CI/CD设置中配置（设置 -> CI/CD -> 变量）：

| 变量名称 | 描述 | 类型 | 示例 |
|---------|-----|------|------|
| `ALIYUN_REGISTRY_USERNAME` | 阿里云容器镜像服务的用户名 | 纯文本 | `netsong@sina.com` |
| `ALIYUN_REGISTRY_PASSWORD` | 阿里云容器镜像服务的密码 | 受保护 | `Netsong2025` |
| `KUBE_CONFIG` | Kubernetes集群配置文件（Base64编码） | 受保护 | `base64_encoded_kubeconfig` |

## 获取变量值的步骤

### 1. 阿里云容器镜像服务凭证

从 `.env-example` 文件中可以获取，或登录阿里云容器镜像服务控制台查看。

```bash
ALIYUN_USERNAME=netsong@sina.com
ALIYUN_PASSWORD=Netsong2025
ALIYUN_REGISTRY=suoke-registry.cn-hangzhou.cr.aliyuncs.com
ALIYUN_NAMESPACE=suoke
```

### 2. Kubernetes配置文件（kubeconfig）

在有权限访问Kubernetes集群的机器上执行以下命令：

```bash
# 获取kubeconfig文件内容并Base64编码
cat ~/.kube/config | base64 -w 0
```

将输出的Base64编码字符串设为`KUBE_CONFIG`变量的值。

## 设置受保护分支

为了确保CI/CD流程的安全性，建议设置以下保护分支规则：

1. 保护分支 `main` 和 `develop`
2. 仅允许维护者对这些分支进行合并
3. 设置分支保护策略：
   - 需要审批
   - 不允许强制推送
   - 需要通过所有CI测试

## 环境配置

当前CI/CD配置支持两种环境：

1. **开发环境（development）**
   - 触发分支：`develop`
   - 命名空间：`suoke-dev`
   - 域名：`dev.suoke.cn`
   - 自动部署

2. **生产环境（production）**
   - 触发分支：`main`
   - 命名空间：`suoke`
   - 域名：`api.suoke.cn`
   - 手动部署（需要在GitLab界面上点击"部署"按钮）

## CI/CD流程说明

CI/CD流程包含以下阶段：

1. **测试（test）**
   - Helm图表语法检查
   - Docker镜像构建测试

2. **构建（build）**
   - 构建多架构（AMD64/ARM64）Docker镜像
   - 推送镜像到阿里云容器镜像服务

3. **部署（deploy）**
   - 使用Helm部署应用到Kubernetes集群
   - 根据分支自动选择部署环境

## 故障排查

如果CI/CD流程失败，可以从以下几个方面排查：

1. **镜像构建失败**
   - 检查Dockerfile语法
   - 确保阿里云容器镜像仓库凭证正确
   - 检查镜像仓库是否有足够的存储空间

2. **部署失败**
   - 验证KUBE_CONFIG是否正确
   - 检查Helm图表是否有语法错误
   - 确认目标命名空间存在且有足够的资源配额

## 最佳实践

1. 对于非关键变更，应该先提交到`develop`分支进行测试
2. 仅当`develop`分支的变更经过充分测试后，才合并到`main`分支
3. 使用有意义的提交信息，便于跟踪变更历史
4. 定期检查和清理旧的镜像版本 