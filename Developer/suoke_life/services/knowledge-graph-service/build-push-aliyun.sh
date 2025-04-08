#!/bin/bash
set -e

# 配置信息 - 更新为指定的阿里云仓库
REGISTRY="suoke-registry.cn-hangzhou.cr.aliyuncs.com"
NAMESPACE="suoke"
IMAGE_NAME="knowledge-graph-service"
TAG="$(date +%Y%m%d)-$(git rev-parse --short HEAD)"
FULL_IMAGE_NAME="$REGISTRY/$NAMESPACE/$IMAGE_NAME:$TAG"

echo "===== 开始构建镜像: $FULL_IMAGE_NAME ====="

# 编译Go二进制文件
echo "编译Go二进制文件..."
cd "$(dirname "$0")"
mkdir -p bin
go build -o bin/knowledge-graph-service ./cmd/api

# 检查配置文件
if [ ! -f "./config/default.yaml" ]; then
  echo "配置文件不存在，从示例创建..."
  mkdir -p config
  cp .env.example config/default.yaml
fi

# 构建镜像
echo "构建Docker镜像..."
docker build \
  --no-cache \
  -t $FULL_IMAGE_NAME \
  -f Dockerfile.aliyun .

# 创建最新标签
LATEST_IMAGE_NAME="$REGISTRY/$NAMESPACE/$IMAGE_NAME:latest"
docker tag $FULL_IMAGE_NAME $LATEST_IMAGE_NAME

# 推送镜像到阿里云
echo "推送镜像到阿里云镜像仓库..."
docker push $FULL_IMAGE_NAME
docker push $LATEST_IMAGE_NAME

echo "===== 镜像构建和推送完成 ====="
echo "镜像名称: $FULL_IMAGE_NAME"
echo "最新镜像: $LATEST_IMAGE_NAME" 