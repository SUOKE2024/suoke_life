# 索克知识图谱服务 Docker 多阶段构建指南

本文档介绍如何使用多阶段构建方法创建轻量级的知识图谱服务镜像，并将其推送到阿里云容器镜像仓库。

## 多阶段构建说明

该构建流程分为三个阶段:

1. **基础阶段**：使用 suoke-registry.cn-hangzhou.cr.aliyuncs.com 的 pause 基础镜像
2. **轻量级阶段**：使用 scratch 镜像，只包含必要的系统库和证书
3. **最终阶段**：添加自定义代码和配置，构建知识图谱服务镜像

## 构建和推送流程

### 前提条件

- 已安装 Docker 20.10 或更高版本
- 拥有阿里云容器镜像仓库的访问凭据

### 配置环境变量

在构建前，请确保已正确配置环境变量。可以使用 `.env` 文件或 `.env.example` 文件中的配置：

```bash
# 阿里云容器镜像仓库凭据
REGISTRY_URL=suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/
REGISTRY_USERNAME=你的用户名
REGISTRY_PASSWORD=你的密码
```

### 构建和推送镜像

使用提供的脚本执行构建和推送操作：

```bash
# 进入项目目录
cd services/knowledge-graph-service

# 运行构建脚本
./build-push-custom.sh
```

构建脚本将执行以下操作：

1. 加载环境变量
2. 设置版本号和标签
3. 登录到阿里云容器镜像仓库
4. 构建多阶段 Docker 镜像（linux/amd64 架构）
5. 推送镜像到阿里云容器镜像仓库

### 使用 Docker Compose 进行本地开发

为方便本地开发和测试，提供了 Docker Compose 配置：

```bash
# 启动服务
docker-compose -f docker-compose.custom.yml up -d

# 查看服务日志
docker-compose -f docker-compose.custom.yml logs -f knowledge-graph-service

# 停止服务
docker-compose -f docker-compose.custom.yml down
```

## 镜像结构

构建的镜像具有以下特点：

- 基于 scratch 的轻量级镜像
- 仅包含必要的系统库和运行时依赖
- 使用非特权用户运行服务
- 包含健康检查机制
- 针对 linux/amd64 架构优化

## 自定义配置

如需修改构建配置，可以编辑以下文件：

- `Dockerfile.custom`：调整多阶段构建配置
- `build-push-custom.sh`：修改构建和推送脚本
- `docker-compose.custom.yml`：调整本地开发环境

## 常见问题

### 镜像推送失败

如果遇到推送失败，请检查以下几点：

1. 确认已正确配置 `REGISTRY_USERNAME` 和 `REGISTRY_PASSWORD`
2. 确认阿里云容器镜像仓库的访问权限
3. 检查网络连接是否正常

### 服务启动失败

如果服务无法正常启动，请检查：

1. 环境变量配置是否正确
2. 数据库连接是否可用
3. 检查服务日志了解详细错误信息 