# 索克生活微服务构建和部署指南

本文档描述了如何构建和部署索克生活平台的微服务到阿里云容器服务 Kubernetes 集群。

## 目录

1. [前置条件](#前置条件)
2. [服务概述](#服务概述)
3. [构建镜像](#构建镜像)
4. [部署服务](#部署服务)
5. [验证部署](#验证部署)
6. [故障排除](#故障排除)

## 前置条件

在开始构建和部署微服务之前，请确保满足以下条件：

1. 已安装 Docker（建议版本 20.10.0 或更高）
2. 已登录阿里云容器镜像服务
3. 已配置阿里云 Kubernetes 集群的 kubectl 访问权限
4. 已连接到阿里云 VPN（如果必要）
5. 拥有 SSH 访问权限到部署服务器（118.31.223.213）

## 服务概述

索克生活平台当前包含以下微服务：

1. **认证服务 (auth-service)**
   - 功能：处理用户认证、授权和会话管理
   - 端口：3001
   - 依赖：MySQL、Redis

2. **用户服务 (user-service)**
   - 功能：管理用户资料、偏好设置和用户相关功能
   - 端口：3002
   - 依赖：MySQL、Redis、认证服务

## 构建镜像

### 构建单个服务镜像

#### 构建认证服务镜像

```bash
cd /Users/songxu/Developer/suoke_life
./scripts/deploy/docker/build-and-push-auth-service.sh
```

#### 构建用户服务镜像

```bash
cd /Users/songxu/Developer/suoke_life
./scripts/deploy/docker/build-and-push-user-service.sh
```

### 构建所有服务镜像

使用组合脚本可以构建并推送所有服务的镜像：

```bash
cd /Users/songxu/Developer/suoke_life
./scripts/deploy/docker/build-and-push-services.sh
```

构建过程会自动执行以下步骤：

1. 检查 Docker 登录状态
2. 构建 Docker 镜像
3. 推送镜像到阿里云容器镜像仓库
4. 标记 latest 版本

## 部署服务

部署脚本会将服务部署到阿里云 Kubernetes 集群：

```bash
cd /Users/songxu/Developer/suoke_life
./scripts/deploy/deploy-services.sh
```

部署过程包括以下步骤：

1. 将 Kubernetes 配置文件复制到远程服务器
2. 确保命名空间存在
3. 应用 Kubernetes 配置
4. 等待服务部署完成
5. 显示服务访问信息

## 验证部署

部署完成后，可以通过以下方式验证服务状态：

### 检查 Pod 状态

```bash
ssh root@118.31.223.213 "KUBECONFIG=/root/.kube/config-ack kubectl get pods -n suoke"
```

### 检查服务状态

```bash
ssh root@118.31.223.213 "KUBECONFIG=/root/.kube/config-ack kubectl get services -n suoke"
```

### 检查 Ingress 状态

```bash
ssh root@118.31.223.213 "KUBECONFIG=/root/.kube/config-ack kubectl get ingress -n suoke"
```

### 访问服务

服务部署成功后，可以通过以下 URL 访问：

- 认证服务：http://auth.suoke.life
- 用户服务：http://user.suoke.life

## 故障排除

如果部署过程中遇到问题，可以尝试以下故障排除步骤：

### 检查容器日志

```bash
ssh root@118.31.223.213 "KUBECONFIG=/root/.kube/config-ack kubectl logs -n suoke deployment/auth-service"
ssh root@118.31.223.213 "KUBECONFIG=/root/.kube/config-ack kubectl logs -n suoke deployment/user-service"
```

### 检查容器事件

```bash
ssh root@118.31.223.213 "KUBECONFIG=/root/.kube/config-ack kubectl describe pod -n suoke -l app=auth-service"
ssh root@118.31.223.213 "KUBECONFIG=/root/.kube/config-ack kubectl describe pod -n suoke -l app=user-service"
```

### 常见问题

1. **镜像拉取失败**：
   - 检查镜像路径是否正确
   - 确认阿里云容器镜像服务的访问权限

2. **服务无法启动**：
   - 检查容器日志获取错误信息
   - 验证环境变量配置是否正确
   - 确认依赖服务（MySQL、Redis）是否可用

3. **无法访问服务**：
   - 检查 Ingress 配置是否正确
   - 确认 DNS 设置是否正确解析域名
   - 检查网络策略是否允许访问 