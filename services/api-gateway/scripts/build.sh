#!/bin/bash
set -e

# 确保已安装 buildah
if ! command -v buildah &> /dev/null; then
    echo "错误: 未找到 buildah 命令，请先安装 buildah"
    echo "参考安装指南: https://github.com/containers/buildah/blob/main/install.md"
    exit 1
fi

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 镜像标签参数
REGISTRY=${REGISTRY:-"suoke.registry.cn"}
IMAGE_NAME=${IMAGE_NAME:-"suoke/api-gateway"}
TAG=${TAG:-"latest"}
FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}:${TAG}"

# Dockerfile 路径
DOCKERFILE="${PROJECT_ROOT}/deploy/docker/Dockerfile"

echo "===== 开始使用 buildah 构建 API 网关镜像 ====="
echo "镜像名称: ${FULL_IMAGE_NAME}"
echo "使用 Dockerfile: ${DOCKERFILE}"

# 使用 buildah 构建镜像
buildah bud \
  --file "${DOCKERFILE}" \
  --tag "${FULL_IMAGE_NAME}" \
  "${PROJECT_ROOT}"

echo "===== 镜像构建完成 ====="
echo "镜像名称: ${FULL_IMAGE_NAME}"

# 推送镜像到仓库（如果需要）
if [ "${PUSH_IMAGE}" = "true" ]; then
    echo "===== 推送镜像到仓库 ====="
    buildah push "${FULL_IMAGE_NAME}"
    echo "===== 镜像推送完成 ====="
fi

exit 0 