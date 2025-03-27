#!/bin/bash
set -e

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "${SCRIPT_DIR}/../.."

# 加载环境变量
if [ -f .env ]; then
  source .env
fi

# 设置变量
REGISTRY_URL=${REGISTRY_URL:-"registry.aliyuncs.com"}
REGISTRY_NAMESPACE=${REGISTRY_NAMESPACE:-"suoke"}
IMAGE_NAME="${REGISTRY_URL}/${REGISTRY_NAMESPACE}/rag-service"
VERSION=$(date +"%Y%m%d%H%M")
BUILD_DIR="${SCRIPT_DIR}/../../services/rag-service"

echo "构建RAG服务简化镜像..."
cd "${BUILD_DIR}"

# 构建镜像，使用简化版Dockerfile
podman build -t "${IMAGE_NAME}:${VERSION}" -f Dockerfile.podman .
podman tag "${IMAGE_NAME}:${VERSION}" "${IMAGE_NAME}:latest"
podman tag "${IMAGE_NAME}:${VERSION}" "localhost/rag-service:latest"

echo "RAG服务镜像构建完成: ${IMAGE_NAME}:${VERSION}"

# 如果设置了推送标志，则推送镜像
if [ "$1" == "--push" ]; then
  echo "推送镜像到仓库..."
  podman push "${IMAGE_NAME}:${VERSION}"
  podman push "${IMAGE_NAME}:latest"
  echo "镜像推送完成"
fi

echo "迁移测试镜像构建完成!" 