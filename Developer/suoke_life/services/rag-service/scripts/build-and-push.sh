#!/bin/bash

# 定义彩色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# 配置变量
SERVICE_NAME="rag-service"
VERSION=$(cat VERSION 2>/dev/null || echo "v1.0.0")
REGISTRY="suoke-registry.cn-hangzhou.cr.aliyuncs.com"
NAMESPACE="suoke"
IMAGE_NAME="${REGISTRY}/${SERVICE_NAME}"
BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
GIT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

# 检查Docker是否运行
echo -e "${YELLOW}检查Docker是否运行...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}错误: Docker未运行，请先启动Docker${NC}"
    exit 1
fi

echo -e "${GREEN}Docker运行正常${NC}"

# 使用国内镜像源修改Dockerfile
echo -e "${YELLOW}创建临时Dockerfile并使用国内镜像源...${NC}"
cat > Dockerfile.cn << EOF
FROM golang:1.21-alpine AS builder

# 设置工作目录
WORKDIR /app

# 设置Go代理
ENV GOPROXY=https://goproxy.cn,direct
ENV GO111MODULE=on
ENV CGO_ENABLED=0

# 安装基本工具和依赖
RUN apk add --no-cache git gcc musl-dev tzdata

# 拷贝go.mod和go.sum文件
COPY go.mod go.sum ./

# 下载依赖 - 这一步会被缓存，除非go.mod或go.sum文件变化
RUN go mod download && go mod verify

# 拷贝源代码
COPY . .

# 设置构建参数
ARG BUILD_VERSION="${VERSION}"
ARG BUILD_DATE="${BUILD_DATE}"
ARG COMMIT_SHA="${GIT_COMMIT}"
ARG TARGETOS=linux
ARG TARGETARCH=amd64

# 编译为静态二进制文件
RUN GOOS=\${TARGETOS} GOARCH=\${TARGETARCH} \\
    go build -a -installsuffix cgo -ldflags "-s -w \\
    -X main.Version=\${BUILD_VERSION} \\
    -X main.BuildTime=\${BUILD_DATE} \\
    -X main.GitCommit=\${COMMIT_SHA}" \\
    -o rag-service .

# 使用多阶段构建，使用更小的基础镜像
FROM alpine:latest

LABEL org.opencontainers.image.version="\${BUILD_VERSION}" \\
      org.opencontainers.image.created="\${BUILD_DATE}" \\
      org.opencontainers.image.revision="\${COMMIT_SHA}" \\
      org.opencontainers.image.title="SUOKE RAG Service" \\
      org.opencontainers.image.description="索克生活知识搜索和检索增强服务" \\
      org.opencontainers.image.vendor="SUOKE Health" \\
      maintainer="SUOKE Life Team"

# 安装ca-certificates，用于HTTPS请求，并清理APK缓存
RUN apk --no-cache add ca-certificates tzdata && \\
    rm -rf /var/cache/apk/*

# 设置工作目录
WORKDIR /app

# 从构建阶段拷贝二进制文件
COPY --from=builder /app/rag-service .
COPY --from=builder /usr/share/zoneinfo /usr/share/zoneinfo

# 拷贝配置文件和必要的资源文件
COPY config.yaml /app/config/
COPY .env.example /app/.env

# 创建必要的目录
RUN mkdir -p /app/data /app/logs /app/models

# 设置时区为上海
ENV TZ=Asia/Shanghai

# 为应用创建非root用户
RUN addgroup -S suoke && adduser -S -G suoke suoke && \\
    chown -R suoke:suoke /app

# 切换到非root用户
USER suoke

# 设置健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD wget -q --spider http://localhost:8080/health || exit 1

# 公开端口
EXPOSE 8080

# 运行二进制文件
ENTRYPOINT ["/app/rag-service"]
EOF

# 构建镜像
echo -e "${YELLOW}开始构建镜像 ${IMAGE_NAME}:${VERSION}...${NC}"
docker build -f Dockerfile.cn -t "${IMAGE_NAME}:latest" -t "${IMAGE_NAME}:${VERSION}" .

if [ $? -ne 0 ]; then
    echo -e "${RED}镜像构建失败${NC}"
    exit 1
fi

echo -e "${GREEN}镜像构建成功: ${IMAGE_NAME}:${VERSION}${NC}"

# 登录到阿里云镜像仓库
echo -e "${YELLOW}登录到阿里云镜像仓库...${NC}"
USERNAME="netsong@sina.com"
PASSWORD="Netsong2025"

echo -e "${YELLOW}使用账号 ${USERNAME} 登录到 ${REGISTRY}...${NC}"
echo "$PASSWORD" | docker login --username "$USERNAME" --password-stdin "${REGISTRY}"

if [ $? -ne 0 ]; then
    echo -e "${RED}登录失败${NC}"
    exit 1
fi

echo -e "${GREEN}登录成功${NC}"

# 推送镜像
echo -e "${YELLOW}推送镜像到 ${IMAGE_NAME}:${VERSION}...${NC}"
docker push "${IMAGE_NAME}:latest"
docker push "${IMAGE_NAME}:${VERSION}"

if [ $? -ne 0 ]; then
    echo -e "${RED}镜像推送失败${NC}"
    exit 1
fi

echo -e "${GREEN}镜像推送成功${NC}"

# 清理临时文件
echo -e "${YELLOW}清理临时文件...${NC}"
rm Dockerfile.cn

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}构建和推送完成!${NC}"
echo -e "${GREEN}镜像: ${IMAGE_NAME}:${VERSION}${NC}"
echo -e "${GREEN}镜像: ${IMAGE_NAME}:latest${NC}"
echo -e "${GREEN}=========================================${NC}"

# 提示部署
echo -e "${YELLOW}要部署此镜像到生产环境，请运行:${NC}"
echo -e "${GREEN}./scripts/deploy-prod.sh${NC}" 