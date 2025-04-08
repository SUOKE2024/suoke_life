#!/bin/bash
set -e

# 加载环境变量
source .env.production

# 设置版本号
VERSION="1.0.1"
echo "开始本地构建和推送流程，版本: $VERSION"

# 创建必要的目录
mkdir -p ./api-gateway/bin
mkdir -p ./auth-service/bin
mkdir -p ./user-service/bin

# 本地为Linux/AMD64编译二进制文件
echo "编译 api-gateway 服务的二进制文件..."
cd ./api-gateway
GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -a -installsuffix cgo -o ./bin/api-gateway ./cmd/api-gateway
echo "api-gateway 二进制文件编译完成"

# 构建和推送 api-gateway 镜像
echo "构建和推送 api-gateway 镜像..."
docker build -t suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/api-gateway:${VERSION} .
docker push suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/api-gateway:${VERSION}
echo "api-gateway 镜像已推送至阿里云容器镜像服务"

# 编译 auth-service 服务
echo "编译 auth-service 服务的二进制文件..."
cd ../auth-service
GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -a -installsuffix cgo -o ./bin/auth-service ./cmd/auth-service
echo "auth-service 二进制文件编译完成"

# 构建和推送 auth-service 镜像
echo "构建和推送 auth-service 镜像..."
docker build -t suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/auth-service:${VERSION} .
docker push suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/auth-service:${VERSION}
echo "auth-service 镜像已推送至阿里云容器镜像服务"

# 编译 user-service 服务
echo "编译 user-service 服务的二进制文件..."
cd ../user-service
GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -a -installsuffix cgo -o ./bin/user-service ./cmd/user-service
echo "user-service 二进制文件编译完成"

# 构建和推送 user-service 镜像
echo "构建和推送 user-service 镜像..."
docker build -t suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/user-service:${VERSION} .
docker push suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke/user-service:${VERSION}
echo "user-service 镜像已推送至阿里云容器镜像服务"

# 完成
echo "所有镜像构建和推送完成 (版本: ${VERSION})"
echo "您现在可以使用以下命令应用Kubernetes配置:"
echo "kubectl apply -f k8s/api-gateway.yaml -n suoke-prod"
echo "kubectl apply -f k8s/auth-service.yaml -n suoke-prod"
echo "kubectl apply -f k8s/user-service.yaml -n suoke-prod" 