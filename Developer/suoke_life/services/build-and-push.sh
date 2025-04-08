#!/bin/bash

# 加载环境变量
source .env.production

echo "开始构建镜像..."

# 构建API网关服务
echo "构建API网关服务..."
cd api-gateway

# 明确设置交叉编译环境变量，确保Mac M1/M2处理器下正确编译
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -a -installsuffix cgo -o api-gateway-bin ./cmd/api-gateway

# 创建Dockerfile
cat > Dockerfile.simple << EOF
FROM alpine:3.17

# 安装基础工具
RUN apk add --no-cache ca-certificates tzdata

# 设置工作目录
WORKDIR /app

# 复制二进制和配置
COPY api-gateway-bin /app/api-gateway
COPY configs /app/configs

# 创建日志目录
RUN mkdir -p /app/logs

# 设置时区
ENV TZ=Asia/Shanghai

# 暴露服务端口
EXPOSE 8080

# 指定启动命令
CMD ["/app/api-gateway"]
EOF

# 构建和推送镜像
docker build -f Dockerfile.simple -t $ALIYUN_REGISTRY/$ALIYUN_NAMESPACE/api-gateway:$VERSION .
docker push $ALIYUN_REGISTRY/$ALIYUN_NAMESPACE/api-gateway:$VERSION
cd ..

# 构建认证服务
echo "构建认证服务..."
cd auth-service

# 明确设置交叉编译环境变量
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -a -installsuffix cgo -o auth-service-bin ./cmd/auth-service

# 创建Dockerfile
cat > Dockerfile.simple << EOF
FROM alpine:3.17

# 安装基础工具
RUN apk add --no-cache ca-certificates tzdata

# 设置工作目录
WORKDIR /app

# 复制二进制和配置
COPY auth-service-bin /app/auth-service
COPY configs /app/configs

# 创建日志目录
RUN mkdir -p /app/logs

# 设置时区
ENV TZ=Asia/Shanghai

# 暴露服务端口
EXPOSE 8081

# 指定启动命令
CMD ["/app/auth-service"]
EOF

# 构建和推送镜像
docker build -f Dockerfile.simple -t $ALIYUN_REGISTRY/$ALIYUN_NAMESPACE/auth-service:$VERSION .
docker push $ALIYUN_REGISTRY/$ALIYUN_NAMESPACE/auth-service:$VERSION
cd ..

# 构建用户服务
echo "构建用户服务..."
cd user-service

# 明确设置交叉编译环境变量
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -a -installsuffix cgo -o user-service-bin ./cmd/user-service

# 创建Dockerfile
cat > Dockerfile.simple << EOF
FROM alpine:3.17

# 安装基础工具
RUN apk add --no-cache ca-certificates tzdata

# 设置工作目录
WORKDIR /app

# 复制二进制和配置
COPY user-service-bin /app/user-service
COPY configs /app/configs

# 创建日志目录
RUN mkdir -p /app/logs

# 设置时区
ENV TZ=Asia/Shanghai

# 暴露服务端口
EXPOSE 8082

# 指定启动命令
CMD ["/app/user-service"]
EOF

# 构建和推送镜像
docker build -f Dockerfile.simple -t $ALIYUN_REGISTRY/$ALIYUN_NAMESPACE/user-service:$VERSION .
docker push $ALIYUN_REGISTRY/$ALIYUN_NAMESPACE/user-service:$VERSION
cd ..

echo "全部镜像构建和推送完成!"