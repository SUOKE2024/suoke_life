#!/bin/bash

# API网关部署脚本
# 用于部署索克生活API网关服务

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
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SERVICE_NAME="suoke-api-gateway"
DOCKER_IMAGE="suoke/${SERVICE_NAME}"
DOCKER_TAG="${DOCKER_TAG:-latest}"
ENVIRONMENT="${ENVIRONMENT:-development}"
NAMESPACE="${NAMESPACE:-suoke}"

# 显示帮助信息
show_help() {
    cat << EOF
索克生活API网关部署脚本

用法: $0 [选项] <命令>

命令:
    build       构建Docker镜像
    push        推送Docker镜像到仓库
    deploy      部署到Kubernetes
    rollback    回滚到上一个版本
    status      查看部署状态
    logs        查看服务日志
    clean       清理资源

选项:
    -e, --env ENV           设置环境 (development|staging|production)
    -t, --tag TAG           设置Docker镜像标签
    -n, --namespace NS      设置Kubernetes命名空间
    -h, --help              显示此帮助信息

环境变量:
    DOCKER_REGISTRY         Docker仓库地址
    KUBECONFIG             Kubernetes配置文件路径
    ENVIRONMENT            部署环境
    DOCKER_TAG             Docker镜像标签
    NAMESPACE              Kubernetes命名空间

示例:
    $0 build                构建开发环境镜像
    $0 -e production deploy 部署到生产环境
    $0 -t v1.2.3 push       推送特定版本镜像
EOF
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    local missing_deps=()
    
    if ! command -v docker &> /dev/null; then
        missing_deps+=("docker")
    fi
    
    if ! command -v kubectl &> /dev/null; then
        missing_deps+=("kubectl")
    fi
    
    if ! command -v uv &> /dev/null; then
        missing_deps+=("uv")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "缺少以下依赖: ${missing_deps[*]}"
        exit 1
    fi
    
    log_success "依赖检查通过"
}

# 构建Docker镜像
build_image() {
    log_info "构建Docker镜像..."
    
    cd "$PROJECT_ROOT"
    
    # 检查Dockerfile是否存在
    if [ ! -f "Dockerfile" ]; then
        log_error "Dockerfile不存在"
        exit 1
    fi
    
    # 构建镜像
    local full_image_name="${DOCKER_IMAGE}:${DOCKER_TAG}"
    
    log_info "构建镜像: $full_image_name"
    docker build \
        --build-arg ENVIRONMENT="$ENVIRONMENT" \
        --tag "$full_image_name" \
        --file Dockerfile \
        .
    
    log_success "镜像构建完成: $full_image_name"
}

# 推送Docker镜像
push_image() {
    log_info "推送Docker镜像..."
    
    local full_image_name="${DOCKER_IMAGE}:${DOCKER_TAG}"
    
    if [ -n "$DOCKER_REGISTRY" ]; then
        local registry_image="${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}"
        docker tag "$full_image_name" "$registry_image"
        docker push "$registry_image"
        log_success "镜像推送完成: $registry_image"
    else
        docker push "$full_image_name"
        log_success "镜像推送完成: $full_image_name"
    fi
}

# 部署到Kubernetes
deploy_to_k8s() {
    log_info "部署到Kubernetes..."
    
    # 检查kubectl连接
    if ! kubectl cluster-info &> /dev/null; then
        log_error "无法连接到Kubernetes集群"
        exit 1
    fi
    
    # 创建命名空间（如果不存在）
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    
    # 应用配置文件
    local deploy_dir="$PROJECT_ROOT/deploy/kubernetes"
    
    if [ -d "$deploy_dir" ]; then
        log_info "应用Kubernetes配置..."
        
        # 替换环境变量
        find "$deploy_dir" -name "*.yaml" -o -name "*.yml" | while read -r file; do
            log_info "应用配置文件: $file"
            envsubst < "$file" | kubectl apply -n "$NAMESPACE" -f -
        done
    else
        log_warning "Kubernetes配置目录不存在: $deploy_dir"
    fi
    
    # 等待部署完成
    log_info "等待部署完成..."
    kubectl rollout status deployment/"$SERVICE_NAME" -n "$NAMESPACE" --timeout=300s
    
    log_success "部署完成"
}

# 回滚部署
rollback_deployment() {
    log_info "回滚部署..."
    
    kubectl rollout undo deployment/"$SERVICE_NAME" -n "$NAMESPACE"
    kubectl rollout status deployment/"$SERVICE_NAME" -n "$NAMESPACE" --timeout=300s
    
    log_success "回滚完成"
}

# 查看部署状态
show_status() {
    log_info "查看部署状态..."
    
    echo
    echo "=== Deployment Status ==="
    kubectl get deployment "$SERVICE_NAME" -n "$NAMESPACE" -o wide
    
    echo
    echo "=== Pod Status ==="
    kubectl get pods -l app="$SERVICE_NAME" -n "$NAMESPACE" -o wide
    
    echo
    echo "=== Service Status ==="
    kubectl get service "$SERVICE_NAME" -n "$NAMESPACE" -o wide
    
    echo
    echo "=== Ingress Status ==="
    kubectl get ingress -l app="$SERVICE_NAME" -n "$NAMESPACE" -o wide
}

# 查看服务日志
show_logs() {
    log_info "查看服务日志..."
    
    kubectl logs -l app="$SERVICE_NAME" -n "$NAMESPACE" --tail=100 -f
}

# 清理资源
clean_resources() {
    log_info "清理资源..."
    
    read -p "确定要删除所有资源吗？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kubectl delete all -l app="$SERVICE_NAME" -n "$NAMESPACE"
        log_success "资源清理完成"
    else
        log_info "取消清理操作"
    fi
}

# 运行健康检查
health_check() {
    log_info "运行健康检查..."
    
    # 获取服务端点
    local service_ip=$(kubectl get service "$SERVICE_NAME" -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    local service_port=$(kubectl get service "$SERVICE_NAME" -n "$NAMESPACE" -o jsonpath='{.spec.ports[0].port}')
    
    if [ -z "$service_ip" ]; then
        service_ip=$(kubectl get service "$SERVICE_NAME" -n "$NAMESPACE" -o jsonpath='{.spec.clusterIP}')
    fi
    
    if [ -n "$service_ip" ] && [ -n "$service_port" ]; then
        local health_url="http://${service_ip}:${service_port}/health"
        log_info "检查健康端点: $health_url"
        
        if curl -f -s "$health_url" > /dev/null; then
            log_success "健康检查通过"
        else
            log_error "健康检查失败"
            exit 1
        fi
    else
        log_warning "无法获取服务端点信息"
    fi
}

# 解析命令行参数
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--env)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -t|--tag)
                DOCKER_TAG="$2"
                shift 2
                ;;
            -n|--namespace)
                NAMESPACE="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            build|push|deploy|rollback|status|logs|clean|health)
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
    parse_args "$@"
    
    if [ -z "$COMMAND" ]; then
        log_error "请指定命令"
        show_help
        exit 1
    fi
    
    log_info "开始执行: $COMMAND"
    log_info "环境: $ENVIRONMENT"
    log_info "镜像标签: $DOCKER_TAG"
    log_info "命名空间: $NAMESPACE"
    
    case $COMMAND in
        build)
            check_dependencies
            build_image
            ;;
        push)
            check_dependencies
            push_image
            ;;
        deploy)
            check_dependencies
            deploy_to_k8s
            health_check
            ;;
        rollback)
            check_dependencies
            rollback_deployment
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        clean)
            clean_resources
            ;;
        health)
            health_check
            ;;
        *)
            log_error "未知命令: $COMMAND"
            show_help
            exit 1
            ;;
    esac
    
    log_success "操作完成: $COMMAND"
}

# 执行主函数
main "$@" 