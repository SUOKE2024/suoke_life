# Accessibility Service 部署指南

本文档介绍如何将 Accessibility Service 代码推送到 GitHub 并构建多架构 Docker 镜像推送到阿里云容器镜像仓库。

## 📋 前置要求

### 必需工具
- Git
- Docker (支持 Buildx)
- Make

### 环境变量配置
在执行部署前，需要设置以下环境变量：

```bash
export ALIYUN_REGISTRY_USERNAME="your_aliyun_username"
export ALIYUN_REGISTRY_PASSWORD="your_aliyun_password"
```

### 阿里云容器镜像仓库配置
- **镜像仓库地址**: `registry.cn-hangzhou.aliyuncs.com`
- **命名空间**: `suoke-life`
- **镜像名称**: `accessibility-service`

## 🚀 部署方式

### 方式一：使用 Makefile（推荐）

#### 1. 查看可用命令
```bash
cd services/accessibility-service
make help
```

#### 2. 检查环境变量
```bash
make check-env
```

#### 3. 推送代码到 GitHub
```bash
make push-github
```

#### 4. 构建并推送多架构镜像
```bash
make docker-push
```

#### 5. 一键部署（推荐）
```bash
make deploy-aliyun
```

### 方式二：使用部署脚本

#### 1. 设置执行权限
```bash
chmod +x services/accessibility-service/scripts/deploy-production.sh
```

#### 2. 执行部署脚本
```bash
cd services/accessibility-service
./scripts/deploy-production.sh
```

### 方式三：使用 GitHub Actions

#### 1. 设置 GitHub Secrets
在 GitHub 仓库设置中添加以下 Secrets：
- `ALIYUN_REGISTRY_USERNAME`: 阿里云容器镜像仓库用户名
- `ALIYUN_REGISTRY_PASSWORD`: 阿里云容器镜像仓库密码

#### 2. 推送代码触发自动部署
```bash
git add .
git commit -m "feat: update accessibility-service"
git push origin main
```

#### 3. 手动触发部署
在 GitHub Actions 页面手动触发 "Deploy to Aliyun Container Registry" 工作流。

## 📦 镜像标签说明

部署过程会创建以下镜像标签：

- `latest`: 最新版本
- `YYYYMMDD-HHMMSS`: 时间戳版本
- `{commit-sha}`: Git 提交 SHA 版本

完整镜像地址示例：
```
registry.cn-hangzhou.aliyuncs.com/suoke-life/accessibility-service:latest
registry.cn-hangzhou.aliyuncs.com/suoke-life/accessibility-service:20241220-143022
registry.cn-hangzhou.aliyuncs.com/suoke-life/accessibility-service:a1b2c3d
```

## 🏗️ 多架构支持

支持以下架构：
- `linux/amd64` (x86_64)
- `linux/arm64` (ARM64)

## 🔍 验证部署

### 1. 检查镜像是否推送成功
```bash
docker pull registry.cn-hangzhou.aliyuncs.com/suoke-life/accessibility-service:latest
```

### 2. 查看镜像信息
```bash
docker buildx imagetools inspect registry.cn-hangzhou.aliyuncs.com/suoke-life/accessibility-service:latest
```

### 3. 运行容器测试
```bash
docker run -d \
  --name accessibility-service-test \
  -p 50051:50051 \
  registry.cn-hangzhou.aliyuncs.com/suoke-life/accessibility-service:latest
```

## 🛠️ 开发工作流

### 日常开发流程
```bash
# 1. 开发代码
# 2. 运行测试
make test

# 3. 代码检查
make lint

# 4. 格式化代码
make format

# 5. 提交前检查
make pre-commit

# 6. 推送到 GitHub
make push-github

# 7. 部署到阿里云
make deploy-aliyun
```

### CI/CD 流程
```bash
# 运行完整 CI 检查
make ci

# 发布版本（包含测试、构建、推送）
make release
```

## 📊 监控和日志

### GitHub Actions 监控
- 访问 GitHub Actions 页面查看部署状态
- 查看构建日志和错误信息

### 镜像安全扫描
部署过程包含 Trivy 安全扫描，结果会上传到 GitHub Security 标签页。

### Slack 通知
配置 `SLACK_WEBHOOK` Secret 后，部署结果会发送到 Slack 频道。

## 🔧 故障排除

### 常见问题

#### 1. Docker Buildx 未安装
```bash
# 安装 Docker Buildx
docker buildx install
```

#### 2. 阿里云登录失败
```bash
# 检查用户名和密码是否正确
echo $ALIYUN_REGISTRY_USERNAME
echo $ALIYUN_REGISTRY_PASSWORD
```

#### 3. 多架构构建失败
```bash
# 检查 QEMU 是否安装
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
```

#### 4. 推送权限问题
确保阿里云账号有推送权限到指定命名空间。

### 日志查看
```bash
# 查看 Docker 构建日志
docker buildx build --progress=plain ...

# 查看容器运行日志
docker logs accessibility-service-test
```

## 📝 配置文件

### Dockerfile 位置
```
services/accessibility-service/deploy/docker/Dockerfile
```

### GitHub Actions 配置
```
services/accessibility-service/.github/workflows/deploy-aliyun.yml
```

### Makefile 配置
```
services/accessibility-service/Makefile
```

## 🔐 安全注意事项

1. **不要在代码中硬编码密码**
2. **使用 GitHub Secrets 存储敏感信息**
3. **定期更新阿里云访问凭据**
4. **启用镜像安全扫描**
5. **使用最小权限原则**

## 📞 支持

如有问题，请：
1. 查看 GitHub Actions 构建日志
2. 检查 Docker 和网络连接
3. 联系开发团队获取支持

---

**注意**: 本部署流程仅推送镜像到阿里云容器镜像仓库，不包含实际的服务部署。如需部署到 Kubernetes 集群，请参考相关的部署文档。 