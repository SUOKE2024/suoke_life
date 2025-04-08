#!/bin/bash

# 设置错误时退出
set -e

# 读取.env文件中的配置
if [ -f .env ]; then
  source .env
else
  echo "警告：未找到.env文件，使用.env.example"
  source .env.example
fi

# 设置变量
IMAGE_NAME="knowledge-graph-service"
IMAGE_TAG=${1:-"latest"}
REGISTRY_URL=${REGISTRY_URL:-"suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/"}
FULL_IMAGE_NAME="${REGISTRY_URL}${IMAGE_NAME}:${IMAGE_TAG}"
PLATFORM="linux/amd64"

echo "======================================"
echo "开始构建 ${FULL_IMAGE_NAME} 镜像"
echo "平台: ${PLATFORM}"
echo "======================================"

# 构建多阶段Docker镜像
docker build --platform=${PLATFORM} \
  --no-cache \
  -t ${FULL_IMAGE_NAME} \
  -f Dockerfile.multistage .

echo "======================================"
echo "镜像构建完成"
echo "正在推送镜像至 ${REGISTRY_URL}"
echo "======================================"

# 推送镜像到阿里云容器镜像仓库（无需登录）
docker push ${FULL_IMAGE_NAME}

echo "======================================"
echo "镜像推送成功: ${FULL_IMAGE_NAME}"
echo "======================================"