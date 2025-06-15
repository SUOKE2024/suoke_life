#!/bin/bash

# API网关部署脚本
# 用于自动化部署API网关到不同环境

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
PROJECT_NAME="suoke-life"
SERVICE_NAME="api-gateway"
DOCKER_REGISTRY="registry.suoke.life"
NAMESPACE="suoke-life"

# 函数定义
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

# 显示帮助信息
show_help() {
    cat << EOF
API网关部署脚本

用法: $0 [选项] <环境>

环境:
  dev         开发环境
  staging     测试环境
  prod        生产环境
  local       本地环境

选项:
  -h, --help              显示帮助信息
  -v, --version VERSION   指定版本标签 (默认: latest)
  -b, --build             构建Docker镜像
  -p, --push              推送镜像到仓库
  -d, --deploy            部署到Kubernetes
  -c, --clean             清理旧资源
  --skip-tests            跳过测试
  --dry-run               预览部署但不执行

示例:
  $0 dev                  部署到开发环境
  $0 -b -p -d prod        构建、推送并部署到生产环境
  $0 --clean dev          清理开发环境资源
EOF
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    local deps=("docker" "kubectl" "uv")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            log_error "缺少依赖: $dep"
            exit 1
        fi
    done
    
    log_success "依赖检查通过"
}

# 构建Docker镜像
build_image() {
    local version=$1
    local image_tag="${DOCKER_REGISTRY}/${PROJECT_NAME}/${SERVICE_NAME}:${version}"
    
    log_info "构建Docker镜像: $image_tag"
    
    # 构建镜像
    docker build -t "$image_tag" .
    
    # 标记为latest（如果不是latest版本）
    if [ "$version" != "latest" ]; then
        docker tag "$image_tag" "${DOCKER_REGISTRY}/${PROJECT_NAME}/${SERVICE_NAME}:latest"
    fi
    
    log_success "镜像构建完成: $image_tag"
}

# 推送镜像
push_image() {
    local version=$1
    local image_tag="${DOCKER_REGISTRY}/${PROJECT_NAME}/${SERVICE_NAME}:${version}"
    
    log_info "推送镜像: $image_tag"
    
    # 登录到镜像仓库
    docker login "$DOCKER_REGISTRY"
    
    # 推送镜像
    docker push "$image_tag"
    
    if [ "$version" != "latest" ]; then
        docker push "${DOCKER_REGISTRY}/${PROJECT_NAME}/${SERVICE_NAME}:latest"
    fi
    
    log_success "镜像推送完成: $image_tag"
}

# 运行测试
run_tests() {
    log_info "运行测试..."
    
    # 安装依赖
    uv sync
    
    # 运行单元测试
    uv run pytest tests/ -v
    
    # 运行代码质量检查
    uv run ruff check src/
    uv run mypy src/
    
    log_success "测试通过"
}

# 部署到Kubernetes
deploy_to_k8s() {
    local env=$1
    local version=$2
    local dry_run=$3
    
    log_info "部署到Kubernetes环境: $env"
    
    # 创建命名空间（如果不存在）
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    
    # 准备部署文件
    local deploy_dir="k8s"
    local temp_dir="/tmp/${SERVICE_NAME}-deploy"
    
    rm -rf "$temp_dir"
    cp -r "$deploy_dir" "$temp_dir"
    
    # 替换环境变量
    find "$temp_dir" -name "*.yaml" -exec sed -i.bak \
        -e "s|{{VERSION}}|$version|g" \
        -e "s|{{ENVIRONMENT}}|$env|g" \
        -e "s|{{NAMESPACE}}|$NAMESPACE|g" \
        {} \;
    
    # 应用配置
    local kubectl_cmd="kubectl apply -f $temp_dir/"
    if [ "$dry_run" = "true" ]; then
        kubectl_cmd="$kubectl_cmd --dry-run=client"
    fi
    
    eval "$kubectl_cmd"
    
    if [ "$dry_run" != "true" ]; then
        # 等待部署完成
        kubectl rollout status deployment/"$SERVICE_NAME" -n "$NAMESPACE" --timeout=300s
        
        # 检查服务状态
        kubectl get pods -n "$NAMESPACE" -l app="$SERVICE_NAME"
    fi
    
    # 清理临时文件
    rm -rf "$temp_dir"
    
    log_success "部署完成"
}

# 本地部署
deploy_local() {
    log_info "启动本地环境..."
    
    # 使用Docker Compose启动
    docker-compose up -d
    
    # 等待服务启动
    sleep 10
    
    # 检查服务状态
    docker-compose ps
    
    log_success "本地环境启动完成"
    log_info "API网关地址: http://localhost:8000"
    log_info "Grafana地址: http://localhost:3000 (admin/admin)"
    log_info "Prometheus地址: http://localhost:9090"
}

# 清理资源
clean_resources() {
    local env=$1
    
    log_warning "清理环境资源: $env"
    
    if [ "$env" = "local" ]; then
        docker-compose down -v
        docker system prune -f
    else
        kubectl delete namespace "$NAMESPACE" --ignore-not-found=true
    fi
    
    log_success "资源清理完成"
}

# 主函数
main() {
    local environment=""
    local version="latest"
    local build=false
    local push=false
    local deploy=false
    local clean=false
    local skip_tests=false
    local dry_run=false
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--version)
                version="$2"
                shift 2
                ;;
            -b|--build)
                build=true
                shift
                ;;
            -p|--push)
                push=true
                shift
                ;;
            -d|--deploy)
                deploy=true
                shift
                ;;
            -c|--clean)
                clean=true
                shift
                ;;
            --skip-tests)
                skip_tests=true
                shift
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            dev|staging|prod|local)
                environment="$1"
                shift
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 验证环境参数
    if [ -z "$environment" ]; then
        log_error "请指定部署环境"
        show_help
        exit 1
    fi
    
    # 检查依赖
    check_dependencies
    
    # 清理资源
    if [ "$clean" = true ]; then
        clean_resources "$environment"
        exit 0
    fi
    
    # 运行测试
    if [ "$skip_tests" != true ] && [ "$environment" != "local" ]; then
        run_tests
    fi
    
    # 构建镜像
    if [ "$build" = true ]; then
        build_image "$version"
    fi
    
    # 推送镜像
    if [ "$push" = true ]; then
        push_image "$version"
    fi
    
    # 部署
    if [ "$deploy" = true ] || [ "$build" = false ] && [ "$push" = false ]; then
        if [ "$environment" = "local" ]; then
            deploy_local
        else
            deploy_to_k8s "$environment" "$version" "$dry_run"
        fi
    fi
    
    log_success "部署流程完成！"
}

# 执行主函数
main "$@" 