#!/bin/bash

# 定义颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # 恢复默认颜色

echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}  索克生活知识图谱服务Docker构建与发布脚本  ${NC}"
echo -e "${BLUE}=========================================${NC}"

# 确保脚本从项目根目录运行
cd "$(dirname "$0")/.." || exit

# 定义变量
IMAGE_NAME="suoke-knowledge-graph-service"
VERSION=$(cat VERSION || echo "1.0.0")
REGISTRY="suoke-registry.cn-hangzhou.cr.aliyuncs.com/suoke"
FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}:${VERSION}"
LATEST_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}:latest"

# 默认仓库凭据
DEFAULT_USERNAME="netsong@sina.com"
DEFAULT_PASSWORD="Netsong2025"

# 从环境文件加载仓库凭据
if [ -f .env ]; then
    source .env
    REGISTRY_USERNAME=${REGISTRY_USERNAME:-$DEFAULT_USERNAME}
    REGISTRY_PASSWORD=${REGISTRY_PASSWORD:-$DEFAULT_PASSWORD}
else
    echo -e "${YELLOW}警告: 未找到.env文件，使用默认仓库凭据${NC}"
    REGISTRY_USERNAME=$DEFAULT_USERNAME
    REGISTRY_PASSWORD=$DEFAULT_PASSWORD
fi

# 显示构建信息
echo -e "${BLUE}构建信息:${NC}"
echo -e "${YELLOW}镜像名称: ${FULL_IMAGE_NAME}${NC}"
echo -e "${YELLOW}最新标签: ${LATEST_IMAGE_NAME}${NC}"
echo -e "${YELLOW}仓库用户: ${REGISTRY_USERNAME}${NC}"

# 构建单一架构镜像并推送
build_and_push_single() {
    local platform=$1
    local tag_suffix=$2
    
    echo -e "\n${BLUE}正在构建 ${platform} 架构镜像...${NC}"
    
    docker build --platform ${platform} \
        -t ${IMAGE_NAME}:${VERSION}-${tag_suffix} \
        -f Dockerfile.new .
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}构建 ${platform} 失败，退出脚本${NC}"
        exit 1
    fi
    
    docker tag ${IMAGE_NAME}:${VERSION}-${tag_suffix} ${FULL_IMAGE_NAME}-${tag_suffix}
    docker push ${FULL_IMAGE_NAME}-${tag_suffix}
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}推送 ${platform} 失败，退出脚本${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ ${platform} 架构镜像构建并推送成功!${NC}"
}

# 构建、标记和推送函数 - 按架构分别构建并创建多架构清单
build_and_push() {
    # 1. 登录阿里云容器镜像服务
    echo -e "\n${BLUE}1. 正在登录阿里云容器镜像服务...${NC}"
    echo "${REGISTRY_PASSWORD}" | docker login --username ${REGISTRY_USERNAME} --password-stdin suoke-registry.cn-hangzhou.cr.aliyuncs.com
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}登录失败，退出脚本${NC}"
        exit 1
    fi
    
    # 2. 分别构建并推送各架构镜像
    echo -e "\n${BLUE}2. 正在构建并推送各架构Docker镜像...${NC}"
    
    # 构建 AMD64 镜像
    build_and_push_single "linux/amd64" "amd64"
    
    # 构建 ARM64 镜像
    build_and_push_single "linux/arm64" "arm64"
    
    # 3. 创建并推送多架构清单
    echo -e "\n${BLUE}3. 正在创建并推送多架构清单...${NC}"
    
    # 创建多架构清单
    docker manifest create ${FULL_IMAGE_NAME} \
        ${FULL_IMAGE_NAME}-amd64 \
        ${FULL_IMAGE_NAME}-arm64
    
    # 标记为最新版本
    docker manifest create ${LATEST_IMAGE_NAME} \
        ${FULL_IMAGE_NAME}-amd64 \
        ${FULL_IMAGE_NAME}-arm64
    
    # 推送清单
    docker manifest push ${FULL_IMAGE_NAME}
    docker manifest push ${LATEST_IMAGE_NAME}
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}推送多架构清单失败，退出脚本${NC}"
        exit 1
    fi
    
    echo -e "\n${GREEN}✅ 多架构镜像已成功构建并推送到阿里云容器镜像服务!${NC}"
}

# 构建函数 - 本地构建单一架构
build_local() {
    # 检测当前系统架构
    ARCH=$(uname -m)
    if [ "$ARCH" = "x86_64" ]; then
        PLATFORM="linux/amd64"
    elif [ "$ARCH" = "arm64" ]; then
        PLATFORM="linux/arm64"
    else
        echo -e "${RED}不支持的架构: ${ARCH}，退出脚本${NC}"
        exit 1
    fi
    
    # 构建镜像
    echo -e "\n${BLUE}正在构建本地Docker镜像 (${PLATFORM})...${NC}"
    docker build --platform ${PLATFORM} -t ${IMAGE_NAME}:${VERSION} -f Dockerfile.new .
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}构建失败，退出脚本${NC}"
        exit 1
    fi
    
    # 标记镜像
    echo -e "\n${BLUE}正在标记镜像...${NC}"
    docker tag ${IMAGE_NAME}:${VERSION} ${FULL_IMAGE_NAME}
    docker tag ${IMAGE_NAME}:${VERSION} ${LATEST_IMAGE_NAME}
    
    echo -e "\n${GREEN}✅ 本地镜像构建完成: ${IMAGE_NAME}:${VERSION} (${PLATFORM})${NC}"
}

# 拉取镜像函数
pull_image() {
    echo -e "\n${BLUE}正在从阿里云拉取镜像...${NC}"
    echo "${REGISTRY_PASSWORD}" | docker login --username ${REGISTRY_USERNAME} --password-stdin suoke-registry.cn-hangzhou.cr.aliyuncs.com
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}登录失败，退出脚本${NC}"
        exit 1
    fi
    
    docker pull ${LATEST_IMAGE_NAME}
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}拉取失败，退出脚本${NC}"
        exit 1
    fi
    
    echo -e "\n${GREEN}✅ 镜像已成功拉取!${NC}"
}

# 显示帮助
show_help() {
    echo -e "\n${BLUE}使用方法:${NC}"
    echo -e "  ${YELLOW}./scripts/docker-build-push.sh [选项]${NC}"
    echo -e "\n${BLUE}选项:${NC}"
    echo -e "  ${YELLOW}build${NC}      构建本地镜像（单架构）"
    echo -e "  ${YELLOW}push${NC}       构建并推送多架构镜像到阿里云"
    echo -e "  ${YELLOW}pull${NC}       从阿里云拉取最新镜像"
    echo -e "  ${YELLOW}help${NC}       显示帮助信息"
    echo -e "\n${BLUE}示例:${NC}"
    echo -e "  ${YELLOW}./scripts/docker-build-push.sh build${NC}   # 构建本地镜像"
    echo -e "  ${YELLOW}./scripts/docker-build-push.sh push${NC}    # 构建并推送多架构镜像"
    echo -e "  ${YELLOW}./scripts/docker-build-push.sh pull${NC}    # 拉取最新镜像"
}

# 主逻辑
case "$1" in
    build)
        build_local
        ;;
    push)
        build_and_push
        ;;
    pull)
        pull_image
        ;;
    *)
        show_help
        ;;
esac

echo -e "\n${BLUE}=========================================${NC}" 