#!/bin/bash

# 加载环境变量
source .env.production

# 设置新版本号
export VERSION=1.0.1

echo "开始在x86_64环境中构建镜像..."

# 确保启用BuildKit
export DOCKER_BUILDKIT=1

# API网关服务
echo "构建API网关服务..."
cd api-gateway
docker build --platform=linux/amd64 -t $ALIYUN_REGISTRY/$ALIYUN_NAMESPACE/api-gateway:$VERSION .
docker push $ALIYUN_REGISTRY/$ALIYUN_NAMESPACE/api-gateway:$VERSION
cd ..

# 认证服务
echo "构建认证服务..."
cd auth-service
docker build --platform=linux/amd64 -t $ALIYUN_REGISTRY/$ALIYUN_NAMESPACE/auth-service:$VERSION .
docker push $ALIYUN_REGISTRY/$ALIYUN_NAMESPACE/auth-service:$VERSION
cd ..

# 用户服务
echo "构建用户服务..."
cd user-service
docker build --platform=linux/amd64 -t $ALIYUN_REGISTRY/$ALIYUN_NAMESPACE/user-service:$VERSION .
docker push $ALIYUN_REGISTRY/$ALIYUN_NAMESPACE/user-service:$VERSION
cd ..

echo "全部镜像构建和推送完成!" 