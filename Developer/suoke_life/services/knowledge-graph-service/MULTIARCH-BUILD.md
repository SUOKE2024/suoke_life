# 索克生活知识图谱服务多架构镜像构建指南

本文档提供了构建支持多架构的知识图谱服务镜像的详细指南，从阿里云官方基础镜像开始，添加自定义代码和配置，最终推送至专用镜像仓库。

## 前提条件

* Docker 20.10+（需支持BuildKit和多架构构建）
* Docker Buildx已安装并启用
* Go 1.22+（用于编译服务二进制文件）
* 已配置访问阿里云容器镜像仓库的权限

## 快速开始

只需运行主脚本即可完成所有步骤：

```bash
cd services/knowledge-graph-service
chmod +x aliyun-build-push-multiarch.sh
./aliyun-build-push-multiarch.sh
```

这将自动执行以下操作：
1. 配置环境（从`.env.example`）
2. 构建多架构镜像（linux/amd64和linux/arm64）
3. 推送镜像至阿里云容器镜像仓库
4. 验证推送的镜像

## 详细说明

### 自动配置环境

环境配置脚本会从`.env.example`文件中读取配置，并设置必要的环境变量：

```bash
./setup-env.sh
```

这个脚本会：
- 创建`.env`文件（如果不存在）
- 生成YAML格式的配置文件
- 登录阿里云容器镜像仓库

### 构建多架构镜像

多架构构建脚本会编译适用于不同CPU架构的二进制文件，并构建镜像：

```bash
./build-multiarch.sh
```

这个脚本会：
- 自动检测并修复Go版本设置
- 使用Docker进行跨平台编译（避免本地环境问题）
- 创建多架构Dockerfile
- 使用Docker Buildx构建并推送镜像

### 测试多架构镜像

您可以使用测试脚本来验证镜像是否正常工作：

```bash
./test-multiarch.sh
```

这个脚本会：
- 检查镜像是否存在
- 获取并显示镜像支持的架构
- 在不同平台上测试镜像
- 验证服务健康检查

## 自定义配置

您可以通过编辑`.env.example`文件来自定义配置。关键配置项包括：

```
# 阿里云容器镜像仓库凭据
REGISTRY_URL=suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/
REGISTRY_USERNAME=your-username
REGISTRY_PASSWORD=your-password
```

## 故障排除

### 构建失败

如果构建失败，请检查：
- Docker Buildx是否正确安装和配置
- 是否有足够的权限访问阿里云容器镜像仓库
- Go编译环境是否正确配置

### 推送失败

如果推送失败，请检查：
- 阿里云容器镜像仓库凭据是否正确
- 网络连接是否稳定
- 是否有足够的权限推送镜像

## 部署

构建完成后，您可以使用以下命令部署服务：

```bash
kubectl apply -f aliyun-deployment.yaml -n suoke-system
``` 