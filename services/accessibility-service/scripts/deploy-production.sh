#!/bin/bash

# Suoke Life - Accessibility Service Production Deployment Script
# 用于推送代码到GitHub并构建多架构镜像到阿里云容器镜像仓库

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 配置变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT="$(cd "$SERVICE_DIR/../.." && pwd)"

# 阿里云容器镜像仓库配置
ALIYUN_REGISTRY="registry.cn-hangzhou.aliyuncs.com"
ALIYUN_NAMESPACE="suoke-life"
SERVICE_NAME="accessibility-service"
IMAGE_NAME="${ALIYUN_REGISTRY}/${ALIYUN_NAMESPACE}/${SERVICE_NAME}"

# GitHub配置
GITHUB_REPO="git@github.com:SUOKE2024/suoke_life.git"
GITHUB_BRANCH="main"

# 多架构配置
BUILD_PLATFORMS="linux/amd64,linux/arm64"

# 版本标签
VERSION_TAG=$(date +%Y%m%d-%H%M%S)
COMMIT_SHA=$(git rev-parse --short HEAD)

# 检查必要的工具
check_dependencies() {
    log_info "检查必要的工具..."
    
    local missing_tools=()
    
    if ! command -v git &> /dev/null; then
        missing_tools+=("git")
    fi
    
    if ! command -v docker &> /dev/null; then
        missing_tools+=("docker")
    fi
    
    if ! docker buildx version &> /dev/null; then
        missing_tools+=("docker buildx")
    fi
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "缺少必要的工具: ${missing_tools[*]}"
        exit 1
    fi
    
    log_success "所有必要工具已安装"
}

# 检查阿里云登录凭据
check_aliyun_credentials() {
    log_info "检查阿里云容器镜像仓库凭据..."
    
    if [ -z "$ALIYUN_REGISTRY_USERNAME" ] || [ -z "$ALIYUN_REGISTRY_PASSWORD" ]; then
        log_warning "未设置阿里云容器镜像仓库凭据"
        read -p "请输入阿里云容器镜像仓库用户名: " ALIYUN_REGISTRY_USERNAME
        read -s -p "请输入阿里云容器镜像仓库密码: " ALIYUN_REGISTRY_PASSWORD
        echo
    fi
    
    if [ -z "$ALIYUN_REGISTRY_USERNAME" ] || [ -z "$ALIYUN_REGISTRY_PASSWORD" ]; then
        log_error "阿里云容器镜像仓库凭据不能为空"
        exit 1
    fi
}

# 推送代码到GitHub
push_to_github() {
    log_info "推送代码到GitHub仓库..."
    
    cd "$PROJECT_ROOT"
    
    # 检查是否有未提交的更改
    if ! git diff-index --quiet HEAD --; then
        log_info "发现未提交的更改，正在提交..."
        git add .
        git commit -m "feat: update accessibility-service for production deployment - $(date '+%Y-%m-%d %H:%M:%S')"
    fi
    
    # 推送到GitHub
    log_info "推送到GitHub分支: $GITHUB_BRANCH"
    git push origin "$GITHUB_BRANCH"
    
    log_success "代码已成功推送到GitHub"
}

# 设置Docker Buildx
setup_docker_buildx() {
    log_info "设置Docker Buildx..."
    
    # 创建并使用新的builder实例
    if ! docker buildx ls | grep -q "suoke-builder"; then
        docker buildx create --name suoke-builder --driver docker-container --bootstrap
    fi
    
    docker buildx use suoke-builder
    
    log_success "Docker Buildx已设置完成"
}

# 登录阿里云容器镜像仓库
login_aliyun_registry() {
    log_info "登录阿里云容器镜像仓库..."
    
    echo "$ALIYUN_REGISTRY_PASSWORD" | docker login "$ALIYUN_REGISTRY" \
        --username "$ALIYUN_REGISTRY_USERNAME" \
        --password-stdin
    
    log_success "已成功登录阿里云容器镜像仓库"
}

# 构建并推送多架构镜像
build_and_push_image() {
    log_info "构建并推送多架构Docker镜像..."
    
    cd "$SERVICE_DIR"
    
    # 构建镜像标签
    local tags=(
        "${IMAGE_NAME}:latest"
        "${IMAGE_NAME}:${VERSION_TAG}"
        "${IMAGE_NAME}:${COMMIT_SHA}"
    )
    
    # 构建标签参数
    local tag_args=""
    for tag in "${tags[@]}"; do
        tag_args="$tag_args -t $tag"
    done
    
    log_info "构建平台: $BUILD_PLATFORMS"
    log_info "镜像标签: ${tags[*]}"
    
    # 构建并推送多架构镜像
    docker buildx build \
        --platform "$BUILD_PLATFORMS" \
        --file "deploy/docker/Dockerfile" \
        $tag_args \
        --push \
        --progress=plain \
        .
    
    log_success "多架构镜像已成功构建并推送到阿里云容器镜像仓库"
}

# 验证镜像推送
verify_image_push() {
    log_info "验证镜像推送..."
    
    local image_url="${IMAGE_NAME}:latest"
    
    # 尝试拉取镜像以验证推送成功
    if docker pull "$image_url" &> /dev/null; then
        log_success "镜像验证成功: $image_url"
    else
        log_error "镜像验证失败: $image_url"
        exit 1
    fi
}

# 清理资源
cleanup() {
    log_info "清理临时资源..."
    
    # 清理Docker buildx缓存
    docker buildx prune -f &> /dev/null || true
    
    log_success "清理完成"
}

# 显示部署信息
show_deployment_info() {
    log_success "部署完成！"
    echo
    echo "=== 部署信息 ==="
    echo "服务名称: $SERVICE_NAME"
    echo "GitHub仓库: $GITHUB_REPO"
    echo "分支: $GITHUB_BRANCH"
    echo "提交SHA: $COMMIT_SHA"
    echo "镜像仓库: $ALIYUN_REGISTRY"
    echo "命名空间: $ALIYUN_NAMESPACE"
    echo "镜像标签:"
    echo "  - ${IMAGE_NAME}:latest"
    echo "  - ${IMAGE_NAME}:${VERSION_TAG}"
    echo "  - ${IMAGE_NAME}:${COMMIT_SHA}"
    echo "构建平台: $BUILD_PLATFORMS"
    echo "部署时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo
}

# 主函数
main() {
    log_info "开始Accessibility Service生产环境部署..."
    
    # 检查依赖
    check_dependencies
    
    # 检查阿里云凭据
    check_aliyun_credentials
    
    # 推送代码到GitHub
    push_to_github
    
    # 设置Docker Buildx
    setup_docker_buildx
    
    # 登录阿里云容器镜像仓库
    login_aliyun_registry
    
    # 构建并推送镜像
    build_and_push_image
    
    # 验证镜像推送
    verify_image_push
    
    # 清理资源
    cleanup
    
    # 显示部署信息
    show_deployment_info
}

# 错误处理
trap 'log_error "部署过程中发生错误，正在清理..."; cleanup; exit 1' ERR

# 执行主函数
main "$@" 