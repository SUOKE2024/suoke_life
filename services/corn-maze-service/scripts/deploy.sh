#!/bin/bash

"""
Corn Maze Service 部署脚本

用于部署 Corn Maze Service 到不同环境
"""

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认配置
ENVIRONMENT=${ENVIRONMENT:-"development"}
NAMESPACE=${NAMESPACE:-"suoke-life"}
IMAGE_TAG=${IMAGE_TAG:-"latest"}
REGISTRY=${REGISTRY:-"localhost:5000"}
SERVICE_NAME="corn-maze-service"

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

# 检查依赖
check_dependencies() {
    log_info "检查部署依赖..."
    
    local deps=("docker" "kubectl" "helm")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            log_error "$dep 未安装或不在 PATH 中"
            exit 1
        fi
    done
    
    log_success "所有依赖检查通过"
}

# 构建 Docker 镜像
build_image() {
    log_info "构建 Docker 镜像..."
    
    local image_name="${REGISTRY}/${SERVICE_NAME}:${IMAGE_TAG}"
    
    docker build \
        --tag "$image_name" \
        --build-arg ENVIRONMENT="$ENVIRONMENT" \
        --file Dockerfile \
        .
    
    log_success "镜像构建完成: $image_name"
    
    # 推送镜像
    if [[ "$REGISTRY" != "localhost:5000" ]]; then
        log_info "推送镜像到注册表..."
        docker push "$image_name"
        log_success "镜像推送完成"
    fi
}

# 生成 Kubernetes 配置
generate_k8s_config() {
    log_info "生成 Kubernetes 配置..."
    
    local config_dir="deploy/kubernetes"
    local output_file="${config_dir}/generated-${ENVIRONMENT}.yaml"
    
    # 创建输出目录
    mkdir -p "$config_dir"
    
    # 替换模板变量
    envsubst < "${config_dir}/deployment.yaml" > "$output_file"
    
    log_success "Kubernetes 配置生成完成: $output_file"
}

# 部署到 Kubernetes
deploy_to_k8s() {
    log_info "部署到 Kubernetes..."
    
    local config_file="deploy/kubernetes/generated-${ENVIRONMENT}.yaml"
    
    if [[ ! -f "$config_file" ]]; then
        log_error "配置文件不存在: $config_file"
        exit 1
    fi
    
    # 创建命名空间（如果不存在）
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    
    # 应用配置
    kubectl apply -f "$config_file" -n "$NAMESPACE"
    
    # 等待部署完成
    kubectl rollout status deployment/"$SERVICE_NAME" -n "$NAMESPACE" --timeout=300s
    
    log_success "部署完成"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    local service_url
    if [[ "$ENVIRONMENT" == "development" ]]; then
        service_url="http://localhost:8080"
    else
        service_url=$(kubectl get service "$SERVICE_NAME" -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
        service_url="http://${service_url}:8080"
    fi
    
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f -s "${service_url}/health" > /dev/null; then
            log_success "健康检查通过"
            return 0
        fi
        
        log_info "健康检查失败，重试 ($attempt/$max_attempts)..."
        sleep 10
        ((attempt++))
    done
    
    log_error "健康检查失败"
    return 1
}

# 回滚部署
rollback() {
    log_warning "执行回滚..."
    
    kubectl rollout undo deployment/"$SERVICE_NAME" -n "$NAMESPACE"
    kubectl rollout status deployment/"$SERVICE_NAME" -n "$NAMESPACE" --timeout=300s
    
    log_success "回滚完成"
}

# 清理资源
cleanup() {
    log_info "清理部署资源..."
    
    kubectl delete deployment "$SERVICE_NAME" -n "$NAMESPACE" --ignore-not-found=true
    kubectl delete service "$SERVICE_NAME" -n "$NAMESPACE" --ignore-not-found=true
    kubectl delete configmap "${SERVICE_NAME}-config" -n "$NAMESPACE" --ignore-not-found=true
    
    log_success "资源清理完成"
}

# 显示帮助信息
show_help() {
    cat << EOF
Corn Maze Service 部署脚本

用法: $0 [选项] <命令>

命令:
    deploy      完整部署流程
    build       仅构建镜像
    k8s         仅部署到 Kubernetes
    health      执行健康检查
    rollback    回滚部署
    cleanup     清理资源

选项:
    -e, --environment   部署环境 (development|staging|production)
    -n, --namespace     Kubernetes 命名空间
    -t, --tag          镜像标签
    -r, --registry     镜像注册表
    -h, --help         显示帮助信息

环境变量:
    ENVIRONMENT    部署环境
    NAMESPACE      Kubernetes 命名空间
    IMAGE_TAG      镜像标签
    REGISTRY       镜像注册表

示例:
    $0 deploy
    $0 -e staging -t v1.2.3 deploy
    $0 --environment production --tag latest build
EOF
}

# 解析命令行参数
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -n|--namespace)
                NAMESPACE="$2"
                shift 2
                ;;
            -t|--tag)
                IMAGE_TAG="$2"
                shift 2
                ;;
            -r|--registry)
                REGISTRY="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            deploy|build|k8s|health|rollback|cleanup)
                COMMAND="$1"
                shift
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# 主函数
main() {
    local command="${COMMAND:-deploy}"
    
    log_info "开始部署 Corn Maze Service"
    log_info "环境: $ENVIRONMENT"
    log_info "命名空间: $NAMESPACE"
    log_info "镜像标签: $IMAGE_TAG"
    log_info "注册表: $REGISTRY"
    
    case "$command" in
        deploy)
            check_dependencies
            build_image
            generate_k8s_config
            deploy_to_k8s
            health_check
            ;;
        build)
            check_dependencies
            build_image
            ;;
        k8s)
            check_dependencies
            generate_k8s_config
            deploy_to_k8s
            ;;
        health)
            health_check
            ;;
        rollback)
            check_dependencies
            rollback
            ;;
        cleanup)
            check_dependencies
            cleanup
            ;;
        *)
            log_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
    
    log_success "操作完成"
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    parse_args "$@"
    main
fi 