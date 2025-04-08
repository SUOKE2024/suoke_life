#!/bin/bash

# 索克生活知识库服务 Docker镜像构建与推送脚本
# 该脚本用于构建知识库服务Docker镜像并推送到阿里云容器仓库

set -e

# 脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 项目根目录
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# 检查环境变量
check_env_vars() {
    echo -e "${YELLOW}检查环境变量...${NC}"
    
    # 加载.env文件中的变量
    if [ -f "${PROJECT_ROOT}/.env" ]; then
        source "${PROJECT_ROOT}/.env"
    else
        echo -e "${RED}错误：未找到.env文件${NC}"
        echo "请先复制.env.example为.env并设置相应的配置"
        exit 1
    fi
    
    # 检查必要的环境变量
    if [ -z "$REGISTRY_USERNAME" ] || [ -z "$REGISTRY_PASSWORD" ]; then
        echo -e "${RED}错误：未设置镜像仓库凭据${NC}"
        echo "请在.env文件中设置REGISTRY_USERNAME和REGISTRY_PASSWORD"
        exit 1
    fi
    
    echo -e "${GREEN}环境变量检查完成${NC}"
}

# 获取版本信息
get_version_info() {
    echo -e "${YELLOW}获取版本信息...${NC}"
    
    # 获取版本号（优先使用git tag，否则使用commit hash或日期）
    VERSION=$(git describe --tags --always --dirty 2>/dev/null || echo "dev-$(date +%Y%m%d)")
    COMMIT_HASH=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
    BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    echo "版本: $VERSION"
    echo "提交: $COMMIT_HASH"
    echo "构建时间: $BUILD_DATE"
    
    echo -e "${GREEN}版本信息获取完成${NC}"
}

# 登录容器镜像仓库
registry_login() {
    echo -e "${YELLOW}登录阿里云容器镜像仓库...${NC}"
    
    # 使用Docker登录阿里云容器镜像服务
    echo "$REGISTRY_PASSWORD" | docker login --username "$REGISTRY_USERNAME" --password-stdin registry.cn-hangzhou.aliyuncs.com
    
    echo -e "${GREEN}登录成功${NC}"
}

# 构建Docker镜像
build_image() {
    echo -e "${YELLOW}开始构建Docker镜像...${NC}"
    
    # 服务名称和镜像仓库
    SERVICE_NAME="knowledge-base-service"
    REGISTRY="registry.cn-hangzhou.aliyuncs.com"
    NAMESPACE="suoke-life"
    IMAGE_NAME="${REGISTRY}/${NAMESPACE}/${SERVICE_NAME}"
    
    # 构建镜像
    docker build -t "${IMAGE_NAME}:${VERSION}" \
        --build-arg VERSION="${VERSION}" \
        --build-arg COMMIT_HASH="${COMMIT_HASH}" \
        --build-arg BUILD_DATE="${BUILD_DATE}" \
        "${PROJECT_ROOT}"
    
    # 标记最新版本
    docker tag "${IMAGE_NAME}:${VERSION}" "${IMAGE_NAME}:latest"
    
    echo -e "${GREEN}Docker镜像构建完成: ${IMAGE_NAME}:${VERSION}${NC}"
    
    # 返回镜像名称供后续推送使用
    echo "${IMAGE_NAME}"
}

# 推送Docker镜像
push_image() {
    local IMAGE_NAME=$1
    
    echo -e "${YELLOW}推送Docker镜像到阿里云...${NC}"
    
    # 推送指定版本和latest版本
    docker push "${IMAGE_NAME}:${VERSION}"
    docker push "${IMAGE_NAME}:latest"
    
    echo -e "${GREEN}Docker镜像推送完成${NC}"
}

# 清理
cleanup() {
    echo -e "${YELLOW}清理临时资源...${NC}"
    
    # 可选：删除本地临时镜像
    # docker rmi "${IMAGE_NAME}:${VERSION}" "${IMAGE_NAME}:latest"
    
    echo -e "${GREEN}清理完成${NC}"
}

# 主流程
main() {
    echo -e "${GREEN}====== 开始构建和推送知识库服务Docker镜像 ======${NC}"
    
    # 执行各步骤
    check_env_vars
    get_version_info
    registry_login
    IMAGE_NAME=$(build_image)
    push_image "${IMAGE_NAME}"
    # cleanup  # 取消注释此行以启用清理
    
    echo -e "${GREEN}====== 知识库服务Docker镜像构建和推送完成 ======${NC}"
    echo "镜像: ${IMAGE_NAME}:${VERSION}"
    echo "可使用以下命令拉取镜像:"
    echo "docker pull ${IMAGE_NAME}:${VERSION}"
}

# 执行主函数
main "$@"
