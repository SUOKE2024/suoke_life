#!/bin/bash
set -e

# 脚本说明: 
# 此脚本使用多阶段构建创建knowledge-graph-service的轻量级镜像，并推送到阿里云容器仓库

# 加载环境变量
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
elif [ -f .env.example ]; then
  export $(grep -v '^#' .env.example | xargs)
fi

# 设置变量
VERSION=$(cat VERSION || echo "1.0.0")
IMAGE_NAME="knowledge-graph-service"
REGISTRY_URL="suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/"
FULL_IMAGE_NAME="${REGISTRY_URL}${IMAGE_NAME}"
PLATFORM="linux/amd64"

echo "开始本地构建 ${FULL_IMAGE_NAME}:${VERSION} 镜像，平台: ${PLATFORM}..."

# 使用docker buildx构建多阶段镜像
docker buildx create --use --name suoke-builder || true
docker buildx inspect --bootstrap

# 构建镜像但不推送
docker buildx build \
  --platform ${PLATFORM} \
  --tag ${FULL_IMAGE_NAME}:${VERSION} \
  --tag ${FULL_IMAGE_NAME}:latest \
  --file Dockerfile.custom \
  --load \
  .

echo "镜像已构建: ${FULL_IMAGE_NAME}:${VERSION} 和 ${FULL_IMAGE_NAME}:latest"

# 查看本地镜像信息
echo "查看本地镜像信息:"
docker images ${FULL_IMAGE_NAME}

echo "========================================="
echo "构建完成!"
echo "镜像: ${FULL_IMAGE_NAME}:${VERSION}"
echo "镜像: ${FULL_IMAGE_NAME}:latest"
echo "=========================================" 