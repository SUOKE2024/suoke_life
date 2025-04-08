#!/bin/bash
#
# 知识图谱服务多架构镜像构建和推送脚本
# 用于构建支持x86_64和arm64架构的轻量级Docker镜像并推送至阿里云
#

# 设置错误时退出
set -e

# 加载环境变量
if [ -f .env ]; then
    source .env
else
    echo "错误：找不到 .env 文件"
    exit 1
fi

# 检查必要的环境变量
if [ -z "$REGISTRY_URL" ] || [ -z "$REGISTRY_USERNAME" ] || [ -z "$REGISTRY_PASSWORD" ]; then
    echo "错误：请在.env文件中设置REGISTRY_URL、REGISTRY_USERNAME和REGISTRY_PASSWORD"
    exit 1
fi

# 设置镜像标签
VERSION=$(cat VERSION || echo "latest")
IMAGE_NAME="${REGISTRY_URL}knowledge-graph-service"
IMAGE_TAG="${IMAGE_NAME}:${VERSION}"

# 登录阿里云容器镜像仓库
echo "登录阿里云容器镜像仓库..."
echo "$REGISTRY_PASSWORD" | docker login ${REGISTRY_URL} -u ${REGISTRY_USERNAME} --password-stdin

# 构建镜像
echo "开始构建镜像: ${IMAGE_TAG}"
docker build \
    --platform linux/amd64 \
    -t ${IMAGE_TAG} \
    -f Dockerfile.aliyun.multiarch \
    --build-arg VERSION=${VERSION} \
    --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
    .

# 推送镜像
echo "推送镜像到阿里云容器镜像仓库..."
docker push ${IMAGE_TAG}

# 添加latest标签并推送
if [ "$VERSION" != "latest" ]; then
    echo "添加latest标签并推送..."
    docker tag ${IMAGE_TAG} ${IMAGE_NAME}:latest
    docker push ${IMAGE_NAME}:latest
fi

echo "镜像构建和推送完成！"
echo "镜像地址: ${IMAGE_TAG}"

# 登出镜像仓库
docker logout ${REGISTRY_URL}

echo "清理本地镜像..."
docker rmi ${IMAGE_TAG}
if [ "$VERSION" != "latest" ]; then
    docker rmi ${IMAGE_NAME}:latest
fi

echo "完成！"