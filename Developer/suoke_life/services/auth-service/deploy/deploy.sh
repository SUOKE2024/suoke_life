#!/bin/bash

# 认证服务部署脚本
# 用于手动执行CI/CD流程相关操作

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 显示使用帮助
show_help() {
    echo -e "${BLUE}索克生活认证服务部署脚本${NC}"
    echo ""
    echo "用法: ./deploy.sh [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help                显示此帮助信息"
    echo "  -v, --version <版本号>    设置部署版本"
    echo "  -e, --env <环境>          指定部署环境 (dev|staging|prod)"
    echo "  -c, --cicd                复制CI/CD配置到GitHub工作流目录"
    echo "  -d, --docker-build        本地构建Docker镜像"
    echo "  -p, --docker-push         推送Docker镜像到镜像仓库"
    echo "  -k, --kube-apply          应用Kubernetes配置"
    echo "  -t, --tag <标签>          Docker镜像标签（默认为版本号）"
    echo ""
    echo "示例:"
    echo "  ./deploy.sh --cicd                      # 复制CI/CD配置到GitHub工作流目录"
    echo "  ./deploy.sh --version 1.4.1 --env dev   # 部署1.4.1版本到开发环境"
    echo "  ./deploy.sh -v 1.4.1 -e prod -d -p -k   # 构建、推送并部署1.4.1版本到生产环境"
    echo ""
}

# 默认值
VERSION="1.4.0"
ENV="dev"
TAG=""
DOCKER_BUILD=false
DOCKER_PUSH=false
KUBE_APPLY=false
COPY_CICD=false

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        -e|--env)
            ENV="$2"
            shift 2
            ;;
        -t|--tag)
            TAG="$2"
            shift 2
            ;;
        -d|--docker-build)
            DOCKER_BUILD=true
            shift
            ;;
        -p|--docker-push)
            DOCKER_PUSH=true
            shift
            ;;
        -k|--kube-apply)
            KUBE_APPLY=true
            shift
            ;;
        -c|--cicd)
            COPY_CICD=true
            shift
            ;;
        *)
            echo -e "${RED}错误: 未知选项 $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# 如果未指定标签，使用版本号作为标签
if [ -z "$TAG" ]; then
    TAG=$VERSION
fi

# 设置镜像名称
REGISTRY_URL="suoke-registry.cn-hangzhou.cr.aliyuncs.com"
REGISTRY_NAMESPACE="suoke"
SERVICE_NAME="auth-service"
IMAGE_NAME="${REGISTRY_URL}/${REGISTRY_NAMESPACE}/${SERVICE_NAME}:${TAG}"

# 复制CI/CD配置
if [ "$COPY_CICD" = true ]; then
    echo -e "${BLUE}正在复制CI/CD配置...${NC}"
    # 确保GitHub工作流目录存在
    mkdir -p ../../.github/workflows
    # 复制CI/CD配置文件
    cp auth-service-cicd-workflow.yml ../../.github/workflows/auth-service-ci-cd.yml
    echo -e "${GREEN}CI/CD配置已复制到 .github/workflows/auth-service-ci-cd.yml${NC}"
fi

# 本地构建Docker镜像
if [ "$DOCKER_BUILD" = true ]; then
    echo -e "${BLUE}正在构建Docker镜像: ${IMAGE_NAME}...${NC}"
    cd ..
    docker build -t ${IMAGE_NAME} .
    echo -e "${GREEN}Docker镜像构建完成${NC}"
fi

# 推送Docker镜像
if [ "$DOCKER_PUSH" = true ]; then
    echo -e "${BLUE}正在推送Docker镜像到镜像仓库...${NC}"
    # 检查是否已登录到仓库
    echo -e "${YELLOW}请确保已登录到阿里云容器镜像服务${NC}"
    read -p "是否继续推送镜像? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker push ${IMAGE_NAME}
        echo -e "${GREEN}Docker镜像推送完成${NC}"
    else
        echo -e "${RED}已取消推送操作${NC}"
    fi
fi

# 应用Kubernetes配置
if [ "$KUBE_APPLY" = true ]; then
    echo -e "${BLUE}正在应用Kubernetes配置到${ENV}环境...${NC}"
    
    # 确认部署操作
    echo -e "${YELLOW}将部署${SERVICE_NAME}版本${VERSION}到${ENV}环境${NC}"
    read -p "是否继续? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # 根据不同环境选择对应的配置
        case $ENV in
            dev)
                kubectl apply -f ../k8s/overlays/dev/
                ;;
            staging)
                kubectl apply -f ../k8s/overlays/staging/
                ;;
            prod)
                kubectl apply -f ../k8s/overlays/prod/
                ;;
            *)
                echo -e "${RED}错误: 未知环境 ${ENV}${NC}"
                exit 1
                ;;
        esac
        echo -e "${GREEN}Kubernetes配置应用完成${NC}"
    else
        echo -e "${RED}已取消部署操作${NC}"
    fi
fi

echo -e "${GREEN}部署脚本执行完成${NC}" 