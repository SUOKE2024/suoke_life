#!/bin/bash
set -e

# 脚本配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 加载环境变量
if [ -f .env ]; then
  echo "从.env文件加载环境变量"
  export $(grep -v '^#' .env | xargs)
else
  echo "警告：.env文件不存在，使用默认值"
  # 创建默认的环境变量值
  export REGISTRY_URL="suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/"
  export REGISTRY_USERNAME="netsong@sina.com"
  export REGISTRY_PASSWORD="Netsong2025"
fi

# 镜像配置
IMAGE_NAME="${REGISTRY_URL}knowledge-graph-service"
VERSION=$(cat VERSION 2>/dev/null || echo "1.0.0")
TAG="${IMAGE_NAME}:${VERSION}"
LATEST_TAG="${IMAGE_NAME}:latest"
REGISTRY_SERVER="${IMAGE_NAME%/*/*}"

# 登录到阿里云容器镜像服务
echo "登录到阿里云容器镜像服务 ${REGISTRY_SERVER}..."
docker login --username "${REGISTRY_USERNAME}" --password "${REGISTRY_PASSWORD}" "${REGISTRY_SERVER}"

# 构建本地架构镜像
echo "构建本地架构镜像: $TAG"
docker build \
  -f Dockerfile.aliyun.multiarch \
  -t "$TAG" \
  -t "$LATEST_TAG" \
  .

# 推送镜像
echo "推送镜像到仓库..."
docker push "$TAG"
docker push "$LATEST_TAG"

echo "镜像构建并推送完成: $TAG"
echo "脚本执行完成!" 