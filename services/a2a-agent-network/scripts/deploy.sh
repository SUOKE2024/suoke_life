#!/bin/bash
set -e

# A2A 智能体网络服务部署脚本
# A2A Agent Network Service Deployment Script

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

# 检查依赖
check_dependencies() {
    log_info "检查部署依赖..."
    
    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    # 检查 Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    # 检查 kubectl（如果部署到 Kubernetes）
    if [[ "$DEPLOY_TARGET" == "kubernetes" ]] && ! command -v kubectl &> /dev/null; then
        log_error "kubectl 未安装，请先安装 kubectl"
        exit 1
    fi
    
    log_success "依赖检查完成"
}

# 构建 Docker 镜像
build_image() {
    log_info "构建 Docker 镜像..."
    
    local image_tag="${IMAGE_TAG:-latest}"
    local image_name="${IMAGE_NAME:-a2a-agent-network}"
    
    docker build -t "${image_name}:${image_tag}" .
    
    if [[ $? -eq 0 ]]; then
        log_success "Docker 镜像构建完成: ${image_name}:${image_tag}"
    else
        log_error "Docker 镜像构建失败"
        exit 1
    fi
}

# 本地部署
deploy_local() {
    log_info "开始本地部署..."
    
    # 创建必要的目录
    mkdir -p logs
    mkdir -p data
    
    # 启动服务
    if [[ -f "docker-compose.yml" ]]; then
        docker-compose up -d
        log_success "本地部署完成，服务已启动"
        log_info "REST API: http://localhost:8080"
        log_info "gRPC: localhost:50051"
        log_info "健康检查: http://localhost:8080/health"
    else
        log_error "docker-compose.yml 文件不存在"
        exit 1
    fi
}

# Kubernetes 部署
deploy_kubernetes() {
    log_info "开始 Kubernetes 部署..."
    
    local namespace="${NAMESPACE:-a2a-agent-network}"
    
    # 创建命名空间
    kubectl create namespace "${namespace}" --dry-run=client -o yaml | kubectl apply -f -
    
    # 应用配置
    if [[ -d "deploy/kubernetes" ]]; then
        kubectl apply -f deploy/kubernetes/ -n "${namespace}"
        log_success "Kubernetes 部署完成"
        
        # 等待部署就绪
        log_info "等待部署就绪..."
        kubectl wait --for=condition=available --timeout=300s deployment/a2a-agent-network -n "${namespace}"
        
        # 显示服务信息
        kubectl get services -n "${namespace}"
    else
        log_error "Kubernetes 部署文件不存在"
        exit 1
    fi
}

# 生产环境部署
deploy_production() {
    log_info "开始生产环境部署..."
    
    # 检查环境变量
    if [[ -z "$PRODUCTION_CONFIG" ]]; then
        log_error "生产环境配置文件路径未设置 (PRODUCTION_CONFIG)"
        exit 1
    fi
    
    if [[ ! -f "$PRODUCTION_CONFIG" ]]; then
        log_error "生产环境配置文件不存在: $PRODUCTION_CONFIG"
        exit 1
    fi
    
    # 备份当前部署
    backup_deployment
    
    # 部署新版本
    case "$DEPLOY_TARGET" in
        "docker")
            deploy_local
            ;;
        "kubernetes")
            deploy_kubernetes
            ;;
        *)
            log_error "不支持的部署目标: $DEPLOY_TARGET"
            exit 1
            ;;
    esac
    
    # 健康检查
    health_check
    
    log_success "生产环境部署完成"
}

# 备份部署
backup_deployment() {
    log_info "备份当前部署..."
    
    local backup_dir="backup/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # 备份配置文件
    if [[ -f "config/config.yaml" ]]; then
        cp config/config.yaml "$backup_dir/"
    fi
    
    # 备份数据（如果有）
    if [[ -d "data" ]]; then
        cp -r data "$backup_dir/"
    fi
    
    log_success "备署完成: $backup_dir"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    local max_attempts=30
    local attempt=1
    local health_url="${HEALTH_URL:-http://localhost:8080/health}"
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f -s "$health_url" > /dev/null 2>&1; then
            log_success "健康检查通过"
            return 0
        fi
        
        log_info "健康检查失败，重试 $attempt/$max_attempts..."
        sleep 10
        ((attempt++))
    done
    
    log_error "健康检查失败，服务可能未正常启动"
    return 1
}

# 回滚部署
rollback_deployment() {
    log_info "开始回滚部署..."
    
    local backup_dir="$1"
    if [[ -z "$backup_dir" ]] || [[ ! -d "$backup_dir" ]]; then
        log_error "备份目录不存在或未指定"
        exit 1
    fi
    
    # 停止当前服务
    case "$DEPLOY_TARGET" in
        "docker")
            docker-compose down
            ;;
        "kubernetes")
            kubectl delete -f deploy/kubernetes/ -n "${NAMESPACE:-a2a-agent-network}" || true
            ;;
    esac
    
    # 恢复配置
    if [[ -f "$backup_dir/config.yaml" ]]; then
        cp "$backup_dir/config.yaml" config/
    fi
    
    # 恢复数据
    if [[ -d "$backup_dir/data" ]]; then
        rm -rf data
        cp -r "$backup_dir/data" .
    fi
    
    # 重新部署
    case "$DEPLOY_TARGET" in
        "docker")
            deploy_local
            ;;
        "kubernetes")
            deploy_kubernetes
            ;;
    esac
    
    log_success "回滚完成"
}

# 清理资源
cleanup() {
    log_info "清理部署资源..."
    
    case "$DEPLOY_TARGET" in
        "docker")
            docker-compose down -v
            docker system prune -f
            ;;
        "kubernetes")
            kubectl delete namespace "${NAMESPACE:-a2a-agent-network}" || true
            ;;
    esac
    
    log_success "资源清理完成"
}

# 显示帮助信息
show_help() {
    cat << EOF
A2A 智能体网络服务部署脚本

用法: $0 [选项] <命令>

命令:
  build                构建 Docker 镜像
  deploy-local         本地部署
  deploy-k8s          Kubernetes 部署
  deploy-prod         生产环境部署
  health-check        健康检查
  rollback <备份目录>  回滚部署
  cleanup             清理资源
  help                显示帮助信息

选项:
  --image-name NAME   Docker 镜像名称 (默认: a2a-agent-network)
  --image-tag TAG     Docker 镜像标签 (默认: latest)
  --namespace NS      Kubernetes 命名空间 (默认: a2a-agent-network)
  --config FILE       配置文件路径
  --health-url URL    健康检查 URL (默认: http://localhost:8080/health)

环境变量:
  DEPLOY_TARGET       部署目标 (docker|kubernetes)
  PRODUCTION_CONFIG   生产环境配置文件路径
  IMAGE_NAME          Docker 镜像名称
  IMAGE_TAG           Docker 镜像标签
  NAMESPACE           Kubernetes 命名空间
  HEALTH_URL          健康检查 URL

示例:
  # 本地开发部署
  $0 deploy-local

  # Kubernetes 部署
  $0 --namespace my-namespace deploy-k8s

  # 生产环境部署
  DEPLOY_TARGET=kubernetes PRODUCTION_CONFIG=prod.yaml $0 deploy-prod

  # 回滚到指定备份
  $0 rollback backup/20231201_143000

EOF
}

# 解析命令行参数
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --image-name)
                IMAGE_NAME="$2"
                shift 2
                ;;
            --image-tag)
                IMAGE_TAG="$2"
                shift 2
                ;;
            --namespace)
                NAMESPACE="$2"
                shift 2
                ;;
            --config)
                CONFIG_FILE="$2"
                shift 2
                ;;
            --health-url)
                HEALTH_URL="$2"
                shift 2
                ;;
            build)
                COMMAND="build"
                shift
                ;;
            deploy-local)
                COMMAND="deploy-local"
                DEPLOY_TARGET="docker"
                shift
                ;;
            deploy-k8s)
                COMMAND="deploy-k8s"
                DEPLOY_TARGET="kubernetes"
                shift
                ;;
            deploy-prod)
                COMMAND="deploy-prod"
                shift
                ;;
            health-check)
                COMMAND="health-check"
                shift
                ;;
            rollback)
                COMMAND="rollback"
                BACKUP_DIR="$2"
                shift 2
                ;;
            cleanup)
                COMMAND="cleanup"
                shift
                ;;
            help|--help|-h)
                COMMAND="help"
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
    # 设置默认值
    COMMAND=""
    IMAGE_NAME="${IMAGE_NAME:-a2a-agent-network}"
    IMAGE_TAG="${IMAGE_TAG:-latest}"
    NAMESPACE="${NAMESPACE:-a2a-agent-network}"
    DEPLOY_TARGET="${DEPLOY_TARGET:-docker}"
    
    # 解析参数
    parse_args "$@"
    
    # 检查命令
    if [[ -z "$COMMAND" ]]; then
        log_error "请指定命令"
        show_help
        exit 1
    fi
    
    # 执行命令
    case "$COMMAND" in
        "build")
            check_dependencies
            build_image
            ;;
        "deploy-local")
            check_dependencies
            build_image
            deploy_local
            ;;
        "deploy-k8s")
            check_dependencies
            build_image
            deploy_kubernetes
            ;;
        "deploy-prod")
            check_dependencies
            build_image
            deploy_production
            ;;
        "health-check")
            health_check
            ;;
        "rollback")
            if [[ -z "$BACKUP_DIR" ]]; then
                log_error "请指定备份目录"
                exit 1
            fi
            rollback_deployment "$BACKUP_DIR"
            ;;
        "cleanup")
            cleanup
            ;;
        "help")
            show_help
            ;;
        *)
            log_error "未知命令: $COMMAND"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@" 