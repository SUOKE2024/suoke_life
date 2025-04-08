#!/bin/bash

# 索克生活知识库服务 Docker镜像拉取脚本
# 该脚本用于从阿里云容器仓库拉取知识库服务镜像

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

# 服务和镜像信息
SERVICE_NAME="knowledge-base-service"
REGISTRY="registry.cn-hangzhou.aliyuncs.com"
NAMESPACE="suoke-life"
IMAGE_NAME="${REGISTRY}/${NAMESPACE}/${SERVICE_NAME}"

# 默认版本
DEFAULT_TAG="latest"

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

# 登录容器镜像仓库
registry_login() {
    echo -e "${YELLOW}登录阿里云容器镜像仓库...${NC}"
    
    # 使用Docker登录阿里云容器镜像服务
    echo "$REGISTRY_PASSWORD" | docker login --username "$REGISTRY_USERNAME" --password-stdin registry.cn-hangzhou.aliyuncs.com
    
    echo -e "${GREEN}登录成功${NC}"
}

# 列出可用的镜像标签
list_available_tags() {
    echo -e "${YELLOW}获取可用的镜像标签...${NC}"
    
    # 此处需要使用阿里云API获取镜像标签列表
    # 由于API调用复杂，这里简化为手动输入或使用默认值
    echo "注意：由于API限制，无法自动获取所有可用标签"
    echo "可用的常用标签: latest, 当前git标签, 或指定版本号"
    
    echo -e "${GREEN}获取标签信息完成${NC}"
}

# 拉取Docker镜像
pull_image() {
    local TAG=$1
    
    echo -e "${YELLOW}开始拉取Docker镜像: ${IMAGE_NAME}:${TAG}${NC}"
    
    # 拉取指定标签的镜像
    docker pull "${IMAGE_NAME}:${TAG}"
    
    echo -e "${GREEN}Docker镜像拉取完成: ${IMAGE_NAME}:${TAG}${NC}"
}

# 使用说明
usage() {
    echo "用法: $0 [版本标签]"
    echo "如果不指定版本标签，将使用latest"
    echo "示例:"
    echo "  $0           # 拉取最新版本"
    echo "  $0 v1.0.0    # 拉取v1.0.0版本"
}

# 主流程
main() {
    # 处理命令行参数
    TAG=$1
    if [ -z "$TAG" ]; then
        TAG=$DEFAULT_TAG
    fi
    
    echo -e "${GREEN}====== 开始拉取知识库服务Docker镜像 ======${NC}"
    
    # 执行各步骤
    check_env_vars
    registry_login
    list_available_tags
    pull_image "$TAG"
    
    echo -e "${GREEN}====== 知识库服务Docker镜像拉取完成 ======${NC}"
    echo "已拉取镜像: ${IMAGE_NAME}:${TAG}"
    echo "可使用以下命令启动容器:"
    echo "docker run -d -p 3002:3002 --name ${SERVICE_NAME} ${IMAGE_NAME}:${TAG}"
}

# 如果脚本被直接执行
if [ "$0" = "${BASH_SOURCE[0]}" ]; then
    # 显示帮助
    if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
        usage
        exit 0
    fi
    
    # 执行主函数
    main "$@"
fi 