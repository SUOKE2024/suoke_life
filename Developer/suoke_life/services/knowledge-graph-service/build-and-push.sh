#!/bin/bash

# 加载环境变量
set -a
source .env.example
set +a

# 设置变量
IMAGE_NAME="knowledge-graph-service"
IMAGE_TAG=$(git describe --tags --always || echo "v1.0.0")
FULL_IMAGE_NAME="${REGISTRY_URL}${IMAGE_NAME}:${IMAGE_TAG}"

echo "开始构建知识图谱服务镜像..."

# 构建镜像
echo "构建镜像: ${FULL_IMAGE_NAME}"
docker build \
  --platform linux/amd64 \
  --build-arg TARGETOS=linux \
  --build-arg TARGETARCH=amd64 \
  -t ${FULL_IMAGE_NAME} \
  -f Dockerfile.aliyun.multiarch .

if [ $? -eq 0 ]; then
    echo "镜像构建成功，开始推送..."
    
    # 推送镜像
    docker push ${FULL_IMAGE_NAME}

    # 添加latest标签
    LATEST_IMAGE_NAME="${REGISTRY_URL}${IMAGE_NAME}:latest"
    docker tag ${FULL_IMAGE_NAME} ${LATEST_IMAGE_NAME}
    docker push ${LATEST_IMAGE_NAME}

    echo "✅ 镜像构建和推送完成！"
    echo "镜像地址："
    echo "- ${FULL_IMAGE_NAME}"
    echo "- ${LATEST_IMAGE_NAME}"
else
    echo "❌ 镜像构建失败！"
    exit 1
fi 