#!/bin/bash

# 索克生活生产环境部署脚本
# 自动化部署前后端所有服务

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
PROJECT_NAME="suoke-life"
DOCKER_REGISTRY="registry.suoke.life"
NAMESPACE="suoke-production"
DEPLOYMENT_ENV="production"
BACKUP_DIR="/opt/backups/suoke-life"
LOG_FILE="/var/log/suoke-deploy.log"

# 服务列表
SERVICES=(
    "api-gateway"
    "auth-service"
    "user-service"
    "health-data-service"
    "xiaoai-service"
    "xiaoke-service"
    "laoke-service"
    "soer-service"
    "rag-service"
    "blockchain-service"
    "message-bus"
    "diagnostic-services"
    "medical-resource-service"
    "integration-service"
    "human-review-service"
)

# 函数定义
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a "$LOG_FILE"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}" | tee -a "$LOG_FILE"
}

# 检查先决条件
check_prerequisites() {
    log "检查部署先决条件..."
    
    # 检查必需的命令
    local required_commands=("docker" "kubectl" "helm" "git" "jq" "curl")
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            error "缺少必需的命令: $cmd"
        fi
    done
    
    # 检查Docker是否运行
    if ! docker info &> /dev/null; then
        error "Docker 未运行或无法访问"
    fi
    
    # 检查Kubernetes连接
    if ! kubectl cluster-info &> /dev/null; then
        error "无法连接到Kubernetes集群"
    fi
    
    # 检查Helm
    if ! helm version &> /dev/null; then
        error "Helm 未正确安装"
    fi
    
    log "先决条件检查完成 ✓"
}

# 创建备份
create_backup() {
    log "创建当前部署备份..."
    
    local backup_timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_path="$BACKUP_DIR/$backup_timestamp"
    
    mkdir -p "$backup_path"
    
    # 备份Kubernetes配置
    kubectl get all -n "$NAMESPACE" -o yaml > "$backup_path/k8s-resources.yaml"
    
    # 备份数据库
    info "备份数据库..."
    kubectl exec -n "$NAMESPACE" deployment/postgresql -- pg_dumpall -U postgres > "$backup_path/database-backup.sql"
    
    # 备份配置文件
    cp -r config/ "$backup_path/"
    
    # 创建备份清单
    cat > "$backup_path/backup-info.json" << EOF
{
    "timestamp": "$backup_timestamp",
    "environment": "$DEPLOYMENT_ENV",
    "git_commit": "$(git rev-parse HEAD)",
    "git_branch": "$(git rev-parse --abbrev-ref HEAD)",
    "services": $(printf '%s\n' "${SERVICES[@]}" | jq -R . | jq -s .)
}
EOF
    
    log "备份创建完成: $backup_path ✓"
    echo "$backup_path" > /tmp/latest_backup_path
}

# 构建Docker镜像
build_images() {
    log "构建Docker镜像..."
    
    local git_commit=$(git rev-parse --short HEAD)
    local build_timestamp=$(date +%Y%m%d_%H%M%S)
    local image_tag="${build_timestamp}_${git_commit}"
    
    # 构建前端应用
    info "构建前端应用..."
    docker build -t "$DOCKER_REGISTRY/suoke-life-frontend:$image_tag" \
        -f Dockerfile.frontend .
    
    # 构建各个微服务
    for service in "${SERVICES[@]}"; do
        info "构建服务: $service"
        
        local service_dir="services/$service"
        if [ -d "$service_dir" ]; then
            docker build -t "$DOCKER_REGISTRY/$service:$image_tag" \
                -f "$service_dir/Dockerfile" "$service_dir"
        else
            warn "服务目录不存在: $service_dir"
        fi
    done
    
    # 推送镜像到仓库
    info "推送镜像到仓库..."
    docker push "$DOCKER_REGISTRY/suoke-life-frontend:$image_tag"
    
    for service in "${SERVICES[@]}"; do
        docker push "$DOCKER_REGISTRY/$service:$image_tag"
    done
    
    # 保存镜像标签
    echo "$image_tag" > /tmp/deployment_image_tag
    
    log "镜像构建和推送完成 ✓"
}

# 更新Kubernetes配置
update_k8s_configs() {
    log "更新Kubernetes配置..."
    
    local image_tag=$(cat /tmp/deployment_image_tag)
    
    # 创建命名空间（如果不存在）
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    
    # 更新ConfigMap
    info "更新配置映射..."
    kubectl create configmap suoke-config \
        --from-file=config/production/ \
        --namespace="$NAMESPACE" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # 更新Secret
    info "更新密钥..."
    kubectl create secret generic suoke-secrets \
        --from-env-file=config/production/.env.production \
        --namespace="$NAMESPACE" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # 应用Kubernetes清单
    info "应用Kubernetes清单..."
    find k8s/production -name "*.yaml" -exec \
        sed "s/{{IMAGE_TAG}}/$image_tag/g" {} \; | \
        kubectl apply -n "$NAMESPACE" -f -
    
    log "Kubernetes配置更新完成 ✓"
}

# 部署Helm Charts
deploy_helm_charts() {
    log "部署Helm Charts..."
    
    local image_tag=$(cat /tmp/deployment_image_tag)
    
    # 更新Helm仓库
    helm repo update
    
    # 部署基础设施组件
    info "部署基础设施组件..."
    
    # PostgreSQL
    helm upgrade --install postgresql bitnami/postgresql \
        --namespace "$NAMESPACE" \
        --set auth.postgresPassword="$(kubectl get secret --namespace $NAMESPACE postgresql -o jsonpath='{.data.postgres-password}' | base64 --decode)" \
        --set primary.persistence.size=100Gi
    
    # Redis
    helm upgrade --install redis bitnami/redis \
        --namespace "$NAMESPACE" \
        --set auth.password="$(kubectl get secret --namespace $NAMESPACE redis -o jsonpath='{.data.redis-password}' | base64 --decode)" \
        --set master.persistence.size=20Gi
    
    # Elasticsearch
    helm upgrade --install elasticsearch elastic/elasticsearch \
        --namespace "$NAMESPACE" \
        --set replicas=3 \
        --set volumeClaimTemplate.resources.requests.storage=50Gi
    
    # 部署应用服务
    info "部署应用服务..."
    helm upgrade --install suoke-life ./deploy/helm/suoke-life \
        --namespace "$NAMESPACE" \
        --set image.tag="$image_tag" \
        --set environment="$DEPLOYMENT_ENV" \
        --values ./deploy/helm/values-production.yaml
    
    log "Helm Charts部署完成 ✓"
}

# 等待部署完成
wait_for_deployment() {
    log "等待部署完成..."
    
    local max_wait=600  # 10分钟
    local wait_time=0
    
    while [ $wait_time -lt $max_wait ]; do
        local ready_pods=$(kubectl get pods -n "$NAMESPACE" --field-selector=status.phase=Running | wc -l)
        local total_pods=$(kubectl get pods -n "$NAMESPACE" | wc -l)
        
        if [ "$ready_pods" -eq "$total_pods" ] && [ "$total_pods" -gt 0 ]; then
            log "所有Pod已就绪 ✓"
            break
        fi
        
        info "等待Pod就绪... ($ready_pods/$total_pods)"
        sleep 10
        wait_time=$((wait_time + 10))
    done
    
    if [ $wait_time -ge $max_wait ]; then
        error "部署超时，请检查Pod状态"
    fi
}

# 运行健康检查
run_health_checks() {
    log "运行健康检查..."
    
    # 获取API网关地址
    local api_gateway_url=$(kubectl get service api-gateway -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    if [ -z "$api_gateway_url" ]; then
        api_gateway_url=$(kubectl get service api-gateway -n "$NAMESPACE" -o jsonpath='{.spec.clusterIP}')
    fi
    
    # 健康检查端点
    local health_endpoints=(
        "http://$api_gateway_url:8000/health"
        "http://$api_gateway_url:8000/api/v1/auth/health"
        "http://$api_gateway_url:8000/api/v1/agents/health"
        "http://$api_gateway_url:8000/api/v1/diagnosis/health"
    )
    
    for endpoint in "${health_endpoints[@]}"; do
        info "检查端点: $endpoint"
        
        local response=$(curl -s -o /dev/null -w "%{http_code}" "$endpoint" || echo "000")
        if [ "$response" = "200" ]; then
            info "✓ $endpoint 健康"
        else
            warn "✗ $endpoint 不健康 (HTTP $response)"
        fi
    done
    
    # 检查数据库连接
    info "检查数据库连接..."
    kubectl exec -n "$NAMESPACE" deployment/postgresql -- psql -U postgres -c "SELECT 1;" > /dev/null
    if [ $? -eq 0 ]; then
        info "✓ 数据库连接正常"
    else
        warn "✗ 数据库连接异常"
    fi
    
    # 检查Redis连接
    info "检查Redis连接..."
    kubectl exec -n "$NAMESPACE" deployment/redis-master -- redis-cli ping > /dev/null
    if [ $? -eq 0 ]; then
        info "✓ Redis连接正常"
    else
        warn "✗ Redis连接异常"
    fi
    
    log "健康检查完成 ✓"
}

# 运行集成测试
run_integration_tests() {
    log "运行集成测试..."
    
    # 设置测试环境变量
    export TEST_API_URL="http://$(kubectl get service api-gateway -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}'):8000"
    export TEST_ENVIRONMENT="production"
    
    # 运行测试
    npm run test:integration
    
    if [ $? -eq 0 ]; then
        log "集成测试通过 ✓"
    else
        error "集成测试失败"
    fi
}

# 更新监控和告警
update_monitoring() {
    log "更新监控和告警..."
    
    # 部署Prometheus
    helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
        --namespace monitoring \
        --create-namespace \
        --values ./deploy/monitoring/prometheus-values.yaml
    
    # 部署Grafana仪表板
    kubectl apply -f ./deploy/monitoring/grafana-dashboards/ -n monitoring
    
    # 更新告警规则
    kubectl apply -f ./deploy/monitoring/alert-rules/ -n monitoring
    
    log "监控和告警更新完成 ✓"
}

# 清理旧版本
cleanup_old_versions() {
    log "清理旧版本..."
    
    # 保留最近3个版本的镜像
    local images_to_keep=3
    
    for service in "${SERVICES[@]}"; do
        info "清理服务镜像: $service"
        
        # 获取镜像列表并删除旧版本
        docker images "$DOCKER_REGISTRY/$service" --format "table {{.Tag}}" | \
            tail -n +2 | sort -r | tail -n +$((images_to_keep + 1)) | \
            xargs -I {} docker rmi "$DOCKER_REGISTRY/$service:{}" 2>/dev/null || true
    done
    
    # 清理旧的备份（保留最近7天）
    find "$BACKUP_DIR" -type d -mtime +7 -exec rm -rf {} + 2>/dev/null || true
    
    log "清理完成 ✓"
}

# 发送部署通知
send_notification() {
    log "发送部署通知..."
    
    local deployment_status="$1"
    local git_commit=$(git rev-parse --short HEAD)
    local git_branch=$(git rev-parse --abbrev-ref HEAD)
    local image_tag=$(cat /tmp/deployment_image_tag 2>/dev/null || echo "unknown")
    
    local message="🚀 索克生活生产环境部署 $deployment_status
    
环境: $DEPLOYMENT_ENV
分支: $git_branch
提交: $git_commit
镜像标签: $image_tag
时间: $(date +'%Y-%m-%d %H:%M:%S')
操作员: $(whoami)"
    
    # 发送到Slack（如果配置了）
    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"$message\"}" \
            "$SLACK_WEBHOOK_URL"
    fi
    
    # 发送到企业微信（如果配置了）
    if [ -n "$WECHAT_WEBHOOK_URL" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"msgtype\":\"text\",\"text\":{\"content\":\"$message\"}}" \
            "$WECHAT_WEBHOOK_URL"
    fi
    
    log "通知发送完成 ✓"
}

# 回滚函数
rollback() {
    error "部署失败，开始回滚..."
    
    local backup_path=$(cat /tmp/latest_backup_path 2>/dev/null)
    if [ -n "$backup_path" ] && [ -d "$backup_path" ]; then
        log "从备份回滚: $backup_path"
        
        # 恢复Kubernetes资源
        kubectl apply -f "$backup_path/k8s-resources.yaml" -n "$NAMESPACE"
        
        # 等待回滚完成
        kubectl rollout status deployment --all -n "$NAMESPACE" --timeout=300s
        
        log "回滚完成 ✓"
        send_notification "回滚成功"
    else
        error "无法找到备份，请手动回滚"
    fi
}

# 主部署流程
main() {
    log "开始索克生活生产环境部署..."
    
    # 设置错误处理
    trap rollback ERR
    
    # 执行部署步骤
    check_prerequisites
    create_backup
    build_images
    update_k8s_configs
    deploy_helm_charts
    wait_for_deployment
    run_health_checks
    run_integration_tests
    update_monitoring
    cleanup_old_versions
    
    log "🎉 部署成功完成！"
    send_notification "成功"
    
    # 显示访问信息
    local api_gateway_url=$(kubectl get service api-gateway -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    info "API网关地址: http://$api_gateway_url:8000"
    info "Grafana监控: http://$(kubectl get service prometheus-grafana -n monitoring -o jsonpath='{.status.loadBalancer.ingress[0].ip}'):3000"
    
    # 清理临时文件
    rm -f /tmp/deployment_image_tag /tmp/latest_backup_path
}

# 显示帮助信息
show_help() {
    cat << EOF
索克生活生产环境部署脚本

用法: $0 [选项]

选项:
    -h, --help          显示此帮助信息
    -v, --verbose       详细输出
    --dry-run          模拟运行（不执行实际部署）
    --skip-tests       跳过集成测试
    --skip-backup      跳过备份创建
    --rollback         回滚到上一个版本

环境变量:
    SLACK_WEBHOOK_URL   Slack通知webhook URL
    WECHAT_WEBHOOK_URL  企业微信通知webhook URL
    DOCKER_REGISTRY     Docker镜像仓库地址
    NAMESPACE           Kubernetes命名空间

示例:
    $0                  # 标准部署
    $0 --dry-run        # 模拟部署
    $0 --skip-tests     # 跳过测试的部署
    $0 --rollback       # 回滚部署

EOF
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            set -x
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --skip-backup)
            SKIP_BACKUP=true
            shift
            ;;
        --rollback)
            rollback
            exit 0
            ;;
        *)
            error "未知选项: $1"
            ;;
    esac
done

# 检查是否为模拟运行
if [ "$DRY_RUN" = true ]; then
    log "模拟运行模式，不会执行实际部署"
    exit 0
fi

# 执行主流程
main "$@" 