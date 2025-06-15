#!/bin/bash

# 无障碍服务部署脚本

set -e

# 切换到项目根目录
cd "$(dirname "$0")/.."

# 默认值
ENVIRONMENT=${ENVIRONMENT:-"development"}
VERSION=${VERSION:-"latest"}
REGISTRY_URL=${REGISTRY_URL:-"suoke-registry.io"}

# 显示帮助
show_help() {
    echo "用法: $0 [选项]"
    echo "选项:"
    echo "  -e, --environment  指定环境 (development, staging, production)"
    echo "  -v, --version      指定版本标签"
    echo "  -r, --registry     指定容器注册表地址"
    echo "  -h, --help         显示此帮助信息"
    exit 0
}

# 处理参数
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        -r|--registry)
            REGISTRY_URL="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            ;;
        *)
            echo "未知选项: $1"
            show_help
            ;;
    esac
done

# 验证环境
if [[ ! "$ENVIRONMENT" =~ ^(development|staging|production)$ ]]; then
    echo "错误: 环境必须是 development, staging 或 production"
    exit 1
fi

# 构建Docker镜像
echo "构建 accessibility-service Docker 镜像 ($VERSION)..."
docker build -t "$REGISTRY_URL/suoke/accessibility-service:$VERSION" -f deploy/docker/Dockerfile .

# 推送镜像到注册表
echo "推送镜像到 $REGISTRY_URL..."
docker push "$REGISTRY_URL/suoke/accessibility-service:$VERSION"

# 部署到Kubernetes
echo "部署 accessibility-service 到 $ENVIRONMENT 环境..."

# 设置环境变量
export REGISTRY_URL
export IMAGE_TAG="$VERSION"

# 应用kustomize配置
echo "应用 Kubernetes 配置..."
kubectl apply -k k8s/overlays/${ENVIRONMENT}

echo "部署完成! 版本: $VERSION 环境: $ENVIRONMENT" 