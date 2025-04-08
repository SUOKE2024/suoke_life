#!/bin/bash
set -e
# 设置变量
SERVICE_NAME="user-service"
REGISTRY="suoke-registry.cn-hangzhou.cr.aliyuncs.com"
NAMESPACE="suoke"
IMAGE_NAME="${REGISTRY}/${NAMESPACE}/${SERVICE_NAME}"
TAG=$(date +%Y%m%d-%H%M%S)
PLATFORMS="linux/amd64,linux/arm64"
# 构建镜像
docker buildx build --platform ${PLATFORMS} -t ${IMAGE_NAME}:${TAG} -t ${IMAGE_NAME}:latest --push --progress=plain .
