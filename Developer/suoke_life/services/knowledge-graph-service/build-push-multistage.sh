#!/bin/bash
set -e

# 脚本说明：使用多阶段Dockerfile构建知识图谱服务镜像并推送到阿里云容器仓库
# 适用架构: linux/amd64

# 加载环境变量
if [ -f .env ]; then
    echo "正在加载.env文件..."
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "未找到.env文件，将使用.env.example..."
    cp .env.example .env
    export $(cat .env | grep -v '^#' | xargs)
fi

# 变量定义
IMAGE_NAME="knowledge-graph-service"
REGISTRY="suoke-registry.cn-hangzhou.cr.aliyuncs.com"
NAMESPACE="suoke"
TAG=$(cat VERSION || echo "latest")

FULL_IMAGE_NAME="${REGISTRY}/${NAMESPACE}/${IMAGE_NAME}:${TAG}"

echo "===== 开始构建镜像: ${FULL_IMAGE_NAME} ====="

# 登录到阿里云容器镜像服务
if [ -z "${ALIYUN_USERNAME}" ] || [ -z "${ALIYUN_PASSWORD}" ]; then
    echo "请先设置ALIYUN_USERNAME和ALIYUN_PASSWORD环境变量"
    echo "您可以通过执行以下命令设置："
    echo "export ALIYUN_USERNAME=YOUR_USERNAME"
    echo "export ALIYUN_PASSWORD=YOUR_PASSWORD"
    exit 1
fi

echo "正在登录阿里云镜像仓库..."
docker login --username=${ALIYUN_USERNAME} --password=${ALIYUN_PASSWORD} ${REGISTRY}

# 构建linux/amd64架构的Docker镜像
echo "正在构建 linux/amd64 架构的镜像..."
docker build --platform=linux/amd64 -f Dockerfile.multistage -t ${FULL_IMAGE_NAME} .

# 推送镜像到远程仓库
echo "正在推送镜像到远程仓库..."
docker push ${FULL_IMAGE_NAME}

echo "===== 镜像已成功构建并推送: ${FULL_IMAGE_NAME} ====="
echo "您可以使用以下命令拉取此镜像:"
echo "docker pull ${FULL_IMAGE_NAME}"