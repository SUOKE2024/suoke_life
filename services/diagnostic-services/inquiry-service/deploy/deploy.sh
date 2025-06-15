#!/bin/bash

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SERVICE_NAME="inquiry-service"
NAMESPACE="suoke-life"
IMAGE_NAME="suoke-life/${SERVICE_NAME}"
VERSION="${VERSION:-latest}"

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    cat << EOF
索克生活问诊服务部署脚本

用法: $0 [选项] <命令>

命令:
  docker          使用Docker Compose部署
  k8s             使用Kubernetes部署
  build           构建Docker镜像
  clean           清理部署资源
  status          查看部署状态

选项:
  -h, --help      显示此帮助信息
  -v, --version   指定版本标签 (默认: latest)
  --dry-run       仅显示将要执行的命令，不实际执行

EOF
}

# 检查依赖
check_dependencies() {
    local deps=("docker" "docker-compose")
    local missing_deps=()
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing_deps+=("$dep")
        fi
    done
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_error "缺少必需的依赖: ${missing_deps[*]}"
        exit 1
    fi
}

# 构建Docker镜像
build_image() {
    log_info "构建Docker镜像: ${IMAGE_NAME}:${VERSION}"
    
    cd "$PROJECT_ROOT"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] docker build -t ${IMAGE_NAME}:${VERSION} -f deploy/Dockerfile ."
        return 0
    fi
    
    docker build \
        -t "${IMAGE_NAME}:${VERSION}" \
        -t "${IMAGE_NAME}:latest" \
        -f deploy/Dockerfile \
        .
    
    log_info "Docker镜像构建完成"
}

# Docker Compose部署
deploy_docker() {
    log_info "使用Docker Compose部署服务"
    
    cd "$SCRIPT_DIR"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] docker-compose -f docker-compose.yml up -d"
        return 0
    fi
    
    # 停止现有服务
    docker-compose -f docker-compose.yml down --remove-orphans || true
    
    # 启动服务
    docker-compose -f docker-compose.yml up -d
    
    log_info "Docker Compose部署成功"
}

# 清理部署
clean_deployment() {
    log_info "清理部署资源"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] docker-compose -f docker-compose.yml down -v --remove-orphans"
    else
        cd "$SCRIPT_DIR"
        docker-compose -f docker-compose.yml down -v --remove-orphans
    fi
    
    log_info "清理完成"
}

# 查看服务状态
show_status() {
    log_info "查看服务状态"
    cd "$SCRIPT_DIR"
    docker-compose -f docker-compose.yml ps
}

# 解析命令行参数
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--version)
                VERSION="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            build|docker|clean|status)
                COMMAND="$1"
                shift
                break
                ;;
            *)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    if [[ -z "${COMMAND:-}" ]]; then
        log_error "请指定命令"
        show_help
        exit 1
    fi
}

# 主函数
main() {
    log_info "=== 索克生活问诊服务部署工具 ==="
    
    case $COMMAND in
        "build")
            check_dependencies
            build_image
            ;;
        "docker")
            check_dependencies
            build_image
            deploy_docker
            ;;
        "status")
            show_status
            ;;
        "clean")
            clean_deployment
            ;;
        *)
            log_error "未知命令: $COMMAND"
            exit 1
            ;;
    esac
    
    log_info "操作完成"
}

# 如果脚本被直接执行
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    parse_args "$@"
    main
fi