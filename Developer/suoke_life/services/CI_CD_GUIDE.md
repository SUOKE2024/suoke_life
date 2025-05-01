# 索克生活APP CI/CD配置指南

本文档提供了配置和使用索克生活APP CI/CD自动化部署流程的详细说明。

## 配置GitHub仓库密钥

在GitHub仓库设置中，需要添加以下密钥（Secrets）:

1. **阿里云容器镜像仓库凭证**:
   - `ALI_REGISTRY_URL`: 阿里云容器镜像仓库地址（例如：`suoke-registry.cn-hangzhou.cr.aliyuncs.com`）
   - `ALI_REGISTRY_USERNAME`: 阿里云容器镜像仓库用户名
   - `ALI_REGISTRY_PASSWORD`: 阿里云容器镜像仓库密码

2. **Kubernetes集群配置**:
   - `KUBE_CONFIG`: Kubernetes集群配置文件内容（base64编码）

3. **通知配置**:
   - `SLACK_WEBHOOK_URL`: Slack通知Webhook URL（可选）

## 配置步骤

1. 进入GitHub仓库的"Settings"选项卡
2. 选择左侧菜单的"Secrets and variables" > "Actions"
3. 点击"New repository secret"按钮
4. 添加上述所有密钥

## 获取KUBE_CONFIG

要获取KUBE_CONFIG密钥的值，请执行以下步骤:

1. 在本地获取kubeconfig文件（通常位于`~/.kube/config`）
2. 使用以下命令将其转换为base64格式:
   ```bash
   cat ~/.kube/config | base64
   ```
3. 将输出的base64字符串作为`KUBE_CONFIG`密钥的值

## 手动触发部署

1. 在GitHub仓库页面，选择"Actions"选项卡
2. 在工作流列表中选择"Deploy to Production"
3. 点击"Run workflow"按钮
4. 选择要部署的分支（通常是master或main）
5. 指定要部署的服务（可以是"all"或特定服务名称）
6. 点击"Run workflow"按钮启动部署

## 自动部署触发条件

以下情况会自动触发部署流程:

1. 向主分支（master或main）推送代码时
2. 修改服务目录下的文件时
3. 修改CI/CD工作流配置文件时

## 部署流程说明

部署流程包括以下阶段:

1. **构建阶段**:
   - 检出代码
   - 设置Docker Buildx
   - 登录到阿里云容器镜像仓库
   - 构建并推送Docker镜像（linux/amd64架构）

2. **部署阶段**:
   - 配置kubectl
   - 创建命名空间
   - 部署Consul服务发现
   - 部署API网关
   - 部署其他服务
   - 等待部署完成
   - 发送部署通知

## 常见问题排查

1. **镜像构建失败**:
   - 检查阿里云容器镜像仓库凭证是否正确
   - 检查Dockerfile是否存在语法错误

2. **部署失败**:
   - 检查KUBE_CONFIG是否正确
   - 检查Kubernetes集群是否可访问
   - 查看部署日志中的具体错误信息

3. **服务无法启动**:
   - 检查环境变量配置
   - 检查服务依赖项是否已部署
   - 查看服务日志

## 重要文件说明

- `.github/workflows/deploy-prod.yml`: CI/CD工作流定义
- `services/.env.prod`: 生产环境配置（不要提交到Git）
- `services/k8s/`: Kubernetes部署配置文件

## 部署监控

部署完成后，可以通过以下方式监控服务状态:

1. Kubernetes Dashboard: 查看Pod、Service状态
2. 服务健康检查端点: `/health`和`/ready`
3. 日志监控: 查看服务日志了解运行状态 