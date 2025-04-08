#!/bin/bash
# 索克生活用户服务多架构镜像构建脚本

set -e

# 配置信息
REGISTRY="suoke-registry.cn-hangzhou.cr.aliyuncs.com"
IMAGE_NAME="suoke/user-service"
VERSION=$(date +%Y%m%d-%H%M%S)
FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}"
PLATFORMS="linux/amd64,linux/arm64"

echo "===== 索克用户服务多架构镜像构建 ====="
echo "镜像：${FULL_IMAGE_NAME}"
echo "版本：${VERSION}"
echo "平台：${PLATFORMS}"
echo "====================================="

# 确保有正确的目录上下文
cd "$(dirname "$0")/.."

# 检查是否存在buildx构建器
if ! docker buildx inspect suoke-builder &>/dev/null; then
  echo "创建Docker buildx构建器..."
  docker buildx create --name suoke-builder --use
fi

# 确保构建器已启动
docker buildx inspect suoke-builder --bootstrap

# 构建镜像
echo "开始构建多架构镜像..."

if [[ "$1" == "--push" ]]; then
  # 构建并推送镜像
  docker buildx build \
    --platform ${PLATFORMS} \
    --tag ${FULL_IMAGE_NAME}:${VERSION} \
    --tag ${FULL_IMAGE_NAME}:latest \
    --push \
    .
  
  echo "镜像构建并推送完成!"
else
  # 仅构建镜像，加载到本地Docker（注意：多平台镜像无法直接加载到本地）
  docker buildx build \
    --platform linux/amd64 \
    --tag ${FULL_IMAGE_NAME}:dev \
    --load \
    .
  
  echo "本地开发镜像构建完成!"
fi

echo "构建完成!"
echo "镜像标签: ${FULL_IMAGE_NAME}:${VERSION}"
echo "镜像标签: ${FULL_IMAGE_NAME}:latest" 