#!/bin/bash

# 索克生活 - CI/CD部署脚本
# 用于自动化部署到不同环境

set -euo pipefail

# 脚本配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
LOG_FILE="${PROJECT_ROOT}/logs/deploy-$(date +%Y%m%d-%H%M%S).log"

# 创建日志目录
mkdir -p "${PROJECT_ROOT}/logs"

# 日志函数
log_info() {
    echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_FILE" >&2
}

log_success() {
    echo "[SUCCESS] $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_FILE"
}

# 显示帮助信息
show_help() {
    cat << EOF
索克生活 CI/CD 部署脚本

用法: $0 [选项] <环境>

环境:
  staging     部署到测试环境
  production  部署到生产环境

选项:
  -h, --help              显示此帮助信息
  -v, --version VERSION   指定部署版本 (默认: latest)
  -s, --skip-tests        跳过测试
  -f, --force             强制部署，跳过确认
  -r, --rollback          回滚到上一个版本
  -d, --dry-run           模拟运行，不实际部署
  --no-backup             不创建备份
  --scale REPLICAS        设置副本数量

示例:
  $0 staging                    # 部署到测试环境
  $0 production -v v1.2.3       # 部署指定版本到生产环境
  $0 staging --skip-tests       # 跳过测试部署到测试环境
  $0 production --rollback      # 回滚生产环境

EOF
}

# 默认配置
ENVIRONMENT=""
VERSION="latest"
SKIP_TESTS=false
FORCE_DEPLOY=false
ROLLBACK=false
DRY_RUN=false
CREATE_BACKUP=true
REPLICAS=""

# 解析命令行参数
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
        -s|--skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        -f|--force)
            FORCE_DEPLOY=true
            shift
            ;;
        -r|--rollback)
            ROLLBACK=true
            shift
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        --no-backup)
            CREATE_BACKUP=false
            shift
            ;;
        --scale)
            REPLICAS="$2"
            shift 2
            ;;
        staging|production)
            ENVIRONMENT="$1"
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
if [[ -z "$ENVIRONMENT" ]]; then
    log_error "必须指定部署环境 (staging 或 production)"
    show_help
    exit 1
fi

# 环境配置
case "$ENVIRONMENT" in
    staging)
        NAMESPACE="suoke-staging"
        KUBECONFIG_SECRET="KUBE_CONFIG_STAGING"
        DOMAIN="staging-api.suoke.life"
        DEFAULT_REPLICAS=2
        ;;
    production)
        NAMESPACE="suoke-production"
        KUBECONFIG_SECRET="KUBE_CONFIG_PRODUCTION"
        DOMAIN="api.suoke.life"
        DEFAULT_REPLICAS=3
        ;;
    *)
        log_error "不支持的环境: $ENVIRONMENT"
        exit 1
        ;;
esac

# 设置副本数量
if [[ -z "$REPLICAS" ]]; then
    REPLICAS="$DEFAULT_REPLICAS"
fi

log_info "开始部署索克生活到 $ENVIRONMENT 环境"
log_info "版本: $VERSION"
log_info "副本数: $REPLICAS"
log_info "命名空间: $NAMESPACE"

# 检查必要工具
check_dependencies() {
    log_info "检查依赖工具..."
    
    local tools=("kubectl" "docker" "envsubst")
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "缺少必要工具: $tool"
            exit 1
        fi
    done
    
    log_success "依赖工具检查完成"
}

# 验证Kubernetes连接
verify_k8s_connection() {
    log_info "验证Kubernetes连接..."
    
    if ! kubectl cluster-info &> /dev/null; then
        log_error "无法连接到Kubernetes集群"
        exit 1
    fi
    
    # 检查命名空间
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        log_info "创建命名空间: $NAMESPACE"
        if [[ "$DRY_RUN" == "false" ]]; then
            kubectl create namespace "$NAMESPACE"
        fi
    fi
    
    log_success "Kubernetes连接验证完成"
}

# 运行测试
run_tests() {
    if [[ "$SKIP_TESTS" == "true" ]]; then
        log_info "跳过测试"
        return 0
    fi
    
    log_info "运行测试..."
    
    cd "$PROJECT_ROOT"
    
    # 前端测试
    log_info "运行前端测试..."
    npm run test:unit -- --watchAll=false
    
    # 后端测试
    log_info "运行后端测试..."
    for service in api-gateway user-management-service unified-health-data-service; do
        if [[ -d "services/$service" ]]; then
            log_info "测试服务: $service"
            cd "services/$service"
            if [[ -f "pyproject.toml" ]]; then
                uv run pytest tests/ --cov=. --cov-report=term-missing
            else
                python -m pytest tests/ --cov=.
            fi
            cd "$PROJECT_ROOT"
        fi
    done
    
    log_success "测试完成"
}

# 构建镜像
build_images() {
    log_info "构建Docker镜像..."
    
    local services=("api-gateway" "user-management-service" "unified-health-data-service" "blockchain-service")
    
    for service in "${services[@]}"; do
        if [[ -d "services/$service" ]]; then
            log_info "构建服务镜像: $service"
            
            local image_name="ghcr.io/suoke2024/suoke_life/$service:$VERSION"
            
            if [[ "$DRY_RUN" == "false" ]]; then
                docker build -t "$image_name" "services/$service"
                docker push "$image_name"
            fi
            
            log_success "镜像构建完成: $service"
        fi
    done
}

# 创建备份
create_backup() {
    if [[ "$CREATE_BACKUP" == "false" ]]; then
        log_info "跳过备份创建"
        return 0
    fi
    
    log_info "创建部署备份..."
    
    local backup_dir="${PROJECT_ROOT}/backups/$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$backup_dir"
    
    # 备份当前部署配置
    kubectl get deployments -n "$NAMESPACE" -o yaml > "$backup_dir/deployments.yaml"
    kubectl get services -n "$NAMESPACE" -o yaml > "$backup_dir/services.yaml"
    kubectl get configmaps -n "$NAMESPACE" -o yaml > "$backup_dir/configmaps.yaml"
    
    log_success "备份创建完成: $backup_dir"
}

# 部署配置
deploy_configs() {
    log_info "部署配置文件..."
    
    cd "$PROJECT_ROOT"
    
    # 设置环境变量
    export REGISTRY="ghcr.io/suoke2024/suoke_life"
    export IMAGE_NAME="suoke_life"
    export IMAGE_TAG="$VERSION"
    export ENVIRONMENT="$ENVIRONMENT"
    export REPLICAS="$REPLICAS"
    
    # 部署ConfigMap
    if [[ -f "k8s/$ENVIRONMENT/configmap.yaml" ]]; then
        log_info "部署ConfigMap..."
        if [[ "$DRY_RUN" == "false" ]]; then
            envsubst < "k8s/$ENVIRONMENT/configmap.yaml" | kubectl apply -f -
        fi
    fi
    
    # 部署Secrets
    if [[ -f "k8s/$ENVIRONMENT/secrets.yaml" ]]; then
        log_info "部署Secrets..."
        if [[ "$DRY_RUN" == "false" ]]; then
            envsubst < "k8s/$ENVIRONMENT/secrets.yaml" | kubectl apply -f -
        fi
    fi
    
    log_success "配置部署完成"
}

# 部署服务
deploy_services() {
    log_info "部署服务..."
    
    local services=("api-gateway" "user-management-service" "unified-health-data-service")
    
    for service in "${services[@]}"; do
        local deployment_file="k8s/$ENVIRONMENT/${service}-deployment.yaml"
        
        if [[ -f "$deployment_file" ]]; then
            log_info "部署服务: $service"
            
            if [[ "$DRY_RUN" == "false" ]]; then
                envsubst < "$deployment_file" | kubectl apply -f -
                
                # 等待部署完成
                kubectl rollout status deployment/"$service" -n "$NAMESPACE" --timeout=600s
                
                # 验证Pod状态
                kubectl wait --for=condition=ready pod -l app="$service" -n "$NAMESPACE" --timeout=300s
            fi
            
            log_success "服务部署完成: $service"
        else
            log_error "部署文件不存在: $deployment_file"
        fi
    done
}

# 执行回滚
perform_rollback() {
    log_info "执行回滚..."
    
    local services=("api-gateway" "user-management-service" "unified-health-data-service")
    
    for service in "${services[@]}"; do
        log_info "回滚服务: $service"
        
        if [[ "$DRY_RUN" == "false" ]]; then
            kubectl rollout undo deployment/"$service" -n "$NAMESPACE"
            kubectl rollout status deployment/"$service" -n "$NAMESPACE" --timeout=600s
        fi
        
        log_success "服务回滚完成: $service"
    done
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        log_info "健康检查尝试 $attempt/$max_attempts"
        
        # 检查API网关健康状态
        if curl -f "http://$DOMAIN/health" &> /dev/null; then
            log_success "健康检查通过"
            return 0
        fi
        
        sleep 10
        ((attempt++))
    done
    
    log_error "健康检查失败"
    return 1
}

# 部署后验证
post_deploy_verification() {
    log_info "执行部署后验证..."
    
    # 检查Pod状态
    kubectl get pods -n "$NAMESPACE"
    
    # 检查服务状态
    kubectl get services -n "$NAMESPACE"
    
    # 检查Ingress状态
    kubectl get ingress -n "$NAMESPACE"
    
    # 执行健康检查
    health_check
    
    log_success "部署后验证完成"
}

# 发送通知
send_notification() {
    local status="$1"
    local message="$2"
    
    log_info "发送部署通知: $status"
    
    # 这里可以集成Slack、钉钉等通知服务
    # 示例：发送到Slack
    if [[ -n "${SLACK_WEBHOOK_URL:-}" ]]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"索克生活部署通知\\n环境: $ENVIRONMENT\\n状态: $status\\n版本: $VERSION\\n消息: $message\"}" \
            "$SLACK_WEBHOOK_URL"
    fi
}

# 清理函数
cleanup() {
    log_info "执行清理..."
    
    # 清理临时文件
    rm -f /tmp/suoke-deploy-*
    
    log_success "清理完成"
}

# 主函数
main() {
    # 设置错误处理
    trap cleanup EXIT
    
    # 确认部署
    if [[ "$FORCE_DEPLOY" == "false" && "$DRY_RUN" == "false" ]]; then
        echo "即将部署到 $ENVIRONMENT 环境，版本: $VERSION"
        read -p "确认继续? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "部署已取消"
            exit 0
        fi
    fi
    
    # 执行部署流程
    check_dependencies
    verify_k8s_connection
    
    if [[ "$ROLLBACK" == "true" ]]; then
        perform_rollback
    else
        run_tests
        build_images
        create_backup
        deploy_configs
        deploy_services
    fi
    
    post_deploy_verification
    
    log_success "部署完成！"
    send_notification "SUCCESS" "部署成功完成"
}

# 错误处理
handle_error() {
    local exit_code=$?
    log_error "部署失败，退出码: $exit_code"
    send_notification "FAILED" "部署失败，请检查日志"
    exit $exit_code
}

trap handle_error ERR

# 执行主函数
main "$@" 