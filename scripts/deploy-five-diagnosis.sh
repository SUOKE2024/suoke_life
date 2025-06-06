#!/bin/bash

# 索克生活 - 五诊服务快速部署脚本
# 一键部署完整的五诊系统到生产环境

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
DEPLOYMENT_ENV=${1:-production}
DOCKER_REGISTRY=${DOCKER_REGISTRY:-"registry.suoke.life"}
IMAGE_TAG=${IMAGE_TAG:-"latest"}
NAMESPACE=${NAMESPACE:-"suoke-five-diagnosis"}

# 检查部署环境
check_deployment_environment() {
    log_info "检查部署环境: $DEPLOYMENT_ENV"
    
    # 检查必要的工具
    local required_tools=("docker" "kubectl" "helm")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "$tool 未安装，请先安装必要的部署工具"
            exit 1
        fi
    done
    
    # 检查Docker是否运行
    if ! docker info &> /dev/null; then
        log_error "Docker 未运行，请启动Docker服务"
        exit 1
    fi
    
    # 检查Kubernetes连接
    if ! kubectl cluster-info &> /dev/null; then
        log_error "无法连接到Kubernetes集群，请检查配置"
        exit 1
    fi
    
    log_success "部署环境检查通过"
}

# 构建Docker镜像
build_docker_images() {
    log_info "构建五诊服务Docker镜像..."
    
    # 构建API Gateway镜像
    log_info "构建API Gateway镜像..."
    docker build -t "${DOCKER_REGISTRY}/suoke-api-gateway:${IMAGE_TAG}" \
        -f services/api-gateway/Dockerfile \
        services/api-gateway/
    
    # 构建认证服务镜像
    log_info "构建认证服务镜像..."
    docker build -t "${DOCKER_REGISTRY}/suoke-auth-service:${IMAGE_TAG}" \
        -f services/auth-service/Dockerfile \
        services/auth-service/
    
    # 构建用户服务镜像
    log_info "构建用户服务镜像..."
    docker build -t "${DOCKER_REGISTRY}/suoke-user-service:${IMAGE_TAG}" \
        -f services/user-service/Dockerfile \
        services/user-service/
    
    # 构建健康数据服务镜像
    log_info "构建健康数据服务镜像..."
    docker build -t "${DOCKER_REGISTRY}/suoke-health-data-service:${IMAGE_TAG}" \
        -f services/health-data-service/Dockerfile \
        services/health-data-service/
    
    # 构建传统四诊服务镜像
    local diagnosis_services=("look-service" "listen-service" "inquiry-service" "palpation-service")
    for service in "${diagnosis_services[@]}"; do
        log_info "构建${service}镜像..."
        docker build -t "${DOCKER_REGISTRY}/suoke-${service}:${IMAGE_TAG}" \
            -f "services/diagnostic-services/${service}/Dockerfile" \
            "services/diagnostic-services/${service}/"
    done
    
    # 构建新增算诊服务镜像
    log_info "构建算诊服务镜像..."
    docker build -t "${DOCKER_REGISTRY}/suoke-calculation-service:${IMAGE_TAG}" \
        -f services/diagnostic-services/calculation-service/Dockerfile \
        services/diagnostic-services/calculation-service/
    
    log_success "所有Docker镜像构建完成"
}

# 推送镜像到仓库
push_docker_images() {
    log_info "推送Docker镜像到仓库..."
    
    # 登录Docker仓库
    if [ -n "$DOCKER_USERNAME" ] && [ -n "$DOCKER_PASSWORD" ]; then
        echo "$DOCKER_PASSWORD" | docker login "$DOCKER_REGISTRY" -u "$DOCKER_USERNAME" --password-stdin
    fi
    
    # 推送所有镜像
    local images=(
        "suoke-api-gateway"
        "suoke-auth-service"
        "suoke-user-service"
        "suoke-health-data-service"
        "suoke-look-service"
        "suoke-listen-service"
        "suoke-inquiry-service"
        "suoke-palpation-service"
        "suoke-calculation-service"
    )
    
    for image in "${images[@]}"; do
        log_info "推送 ${image}:${IMAGE_TAG}..."
        docker push "${DOCKER_REGISTRY}/${image}:${IMAGE_TAG}"
    done
    
    log_success "所有镜像推送完成"
}

# 创建Kubernetes命名空间
create_namespace() {
    log_info "创建Kubernetes命名空间: $NAMESPACE"
    
    if kubectl get namespace "$NAMESPACE" &> /dev/null; then
        log_warning "命名空间 $NAMESPACE 已存在"
    else
        kubectl create namespace "$NAMESPACE"
        log_success "命名空间 $NAMESPACE 创建成功"
    fi
}

# 部署基础设施
deploy_infrastructure() {
    log_info "部署基础设施组件..."
    
    # 部署PostgreSQL
    log_info "部署PostgreSQL数据库..."
    helm repo add bitnami https://charts.bitnami.com/bitnami
    helm repo update
    
    helm upgrade --install postgresql bitnami/postgresql \
        --namespace "$NAMESPACE" \
        --set auth.postgresPassword="$DB_PASSWORD" \
        --set auth.database="suoke_five_diagnosis" \
        --set primary.persistence.size="20Gi" \
        --wait
    
    # 部署Redis
    log_info "部署Redis缓存..."
    helm upgrade --install redis bitnami/redis \
        --namespace "$NAMESPACE" \
        --set auth.password="$REDIS_PASSWORD" \
        --set master.persistence.size="8Gi" \
        --wait
    
    # 部署RabbitMQ
    log_info "部署RabbitMQ消息队列..."
    helm upgrade --install rabbitmq bitnami/rabbitmq \
        --namespace "$NAMESPACE" \
        --set auth.username="suoke_mq" \
        --set auth.password="$MQ_PASSWORD" \
        --set persistence.size="8Gi" \
        --wait
    
    log_success "基础设施部署完成"
}

# 部署五诊服务
deploy_five_diagnosis_services() {
    log_info "部署五诊服务..."
    
    # 应用Kubernetes配置
    kubectl apply -f deploy/kubernetes/ -n "$NAMESPACE"
    
    # 等待所有Pod就绪
    log_info "等待服务启动..."
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/part-of=suoke-five-diagnosis \
        -n "$NAMESPACE" --timeout=300s
    
    log_success "五诊服务部署完成"
}

# 配置负载均衡和入口
setup_ingress() {
    log_info "配置负载均衡和入口..."
    
    # 部署Nginx Ingress Controller (如果不存在)
    if ! kubectl get ingressclass nginx &> /dev/null; then
        log_info "部署Nginx Ingress Controller..."
        helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
        helm repo update
        helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
            --namespace ingress-nginx \
            --create-namespace \
            --wait
    fi
    
    # 应用Ingress配置
    kubectl apply -f deploy/kubernetes/ingress.yml -n "$NAMESPACE"
    
    log_success "负载均衡和入口配置完成"
}

# 配置监控
setup_monitoring() {
    log_info "配置监控系统..."
    
    # 部署Prometheus和Grafana
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update
    
    helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
        --namespace monitoring \
        --create-namespace \
        --set grafana.adminPassword="$GRAFANA_PASSWORD" \
        --wait
    
    # 应用自定义监控配置
    kubectl apply -f deploy/monitoring/ -n "$NAMESPACE"
    
    log_success "监控系统配置完成"
}

# 运行部署后测试
run_post_deployment_tests() {
    log_info "运行部署后测试..."
    
    # 等待服务完全启动
    sleep 30
    
    # 获取服务入口地址
    local gateway_url
    if [ "$DEPLOYMENT_ENV" = "local" ]; then
        gateway_url="http://localhost:8000"
    else
        gateway_url=$(kubectl get ingress suoke-five-diagnosis-ingress -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
        if [ -z "$gateway_url" ]; then
            gateway_url=$(kubectl get service suoke-api-gateway -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
        fi
        gateway_url="http://${gateway_url}"
    fi
    
    # 运行健康检查
    log_info "检查服务健康状态..."
    if curl -f "$gateway_url/health" &> /dev/null; then
        log_success "✓ API Gateway 健康检查通过"
    else
        log_error "✗ API Gateway 健康检查失败"
        return 1
    fi
    
    # 运行基本功能测试
    log_info "运行基本功能测试..."
    if curl -f "$gateway_url/api/v1/diagnosis/health" &> /dev/null; then
        log_success "✓ 诊断服务基本功能测试通过"
    else
        log_warning "⚠ 诊断服务基本功能测试失败，可能需要进一步检查"
    fi
    
    log_success "部署后测试完成"
    echo
    echo "🎉 五诊服务部署成功！"
    echo "📍 服务地址: $gateway_url"
    echo "📊 监控地址: http://grafana.${NAMESPACE}.local (如果配置了域名)"
    echo "📚 API文档: $gateway_url/docs"
}

# 回滚部署
rollback_deployment() {
    log_warning "开始回滚部署..."
    
    # 回滚Kubernetes部署
    kubectl rollout undo deployment -n "$NAMESPACE"
    
    # 等待回滚完成
    kubectl rollout status deployment -n "$NAMESPACE"
    
    log_success "部署回滚完成"
}

# 清理部署
cleanup_deployment() {
    log_warning "清理部署资源..."
    
    # 删除命名空间 (这会删除所有相关资源)
    kubectl delete namespace "$NAMESPACE" --ignore-not-found=true
    
    # 清理Docker镜像 (可选)
    if [ "$1" = "--clean-images" ]; then
        log_info "清理本地Docker镜像..."
        docker rmi $(docker images "${DOCKER_REGISTRY}/suoke-*" -q) 2>/dev/null || true
    fi
    
    log_success "清理完成"
}

# 显示帮助信息
show_help() {
    echo "索克生活 - 五诊服务部署脚本"
    echo
    echo "用法: $0 [环境] [选项]"
    echo
    echo "环境:"
    echo "  development  开发环境 (默认)"
    echo "  staging      测试环境"
    echo "  production   生产环境"
    echo
    echo "选项:"
    echo "  --build-only     仅构建镜像"
    echo "  --deploy-only    仅部署服务"
    echo "  --rollback       回滚部署"
    echo "  --cleanup        清理部署"
    echo "  --help           显示帮助信息"
    echo
    echo "环境变量:"
    echo "  DOCKER_REGISTRY  Docker镜像仓库地址"
    echo "  IMAGE_TAG        镜像标签"
    echo "  NAMESPACE        Kubernetes命名空间"
    echo "  DB_PASSWORD      数据库密码"
    echo "  REDIS_PASSWORD   Redis密码"
    echo "  MQ_PASSWORD      消息队列密码"
    echo
    echo "示例:"
    echo "  $0 production                    # 部署到生产环境"
    echo "  $0 staging --build-only          # 仅构建测试环境镜像"
    echo "  $0 production --rollback         # 回滚生产环境"
    echo "  $0 development --cleanup         # 清理开发环境"
}

# 主函数
main() {
    echo "=========================================="
    echo "    索克生活 - 五诊服务部署脚本"
    echo "=========================================="
    echo
    
    # 解析命令行参数
    case "${2:-}" in
        --help)
            show_help
            exit 0
            ;;
        --build-only)
            check_deployment_environment
            build_docker_images
            push_docker_images
            exit 0
            ;;
        --deploy-only)
            check_deployment_environment
            create_namespace
            deploy_five_diagnosis_services
            setup_ingress
            run_post_deployment_tests
            exit 0
            ;;
        --rollback)
            rollback_deployment
            exit 0
            ;;
        --cleanup)
            cleanup_deployment "${3:-}"
            exit 0
            ;;
    esac
    
    # 检查必要的环境变量
    if [ -z "${DB_PASSWORD:-}" ] || [ -z "${REDIS_PASSWORD:-}" ] || [ -z "${MQ_PASSWORD:-}" ]; then
        log_error "请设置必要的环境变量: DB_PASSWORD, REDIS_PASSWORD, MQ_PASSWORD"
        exit 1
    fi
    
    log_info "开始部署五诊服务到 $DEPLOYMENT_ENV 环境..."
    echo
    
    # 执行完整部署流程
    check_deployment_environment
    build_docker_images
    push_docker_images
    create_namespace
    deploy_infrastructure
    deploy_five_diagnosis_services
    setup_ingress
    setup_monitoring
    run_post_deployment_tests
    
    log_success "🎉 五诊服务部署完成！"
}

# 错误处理
trap 'log_error "部署过程中发生错误，请检查日志"; exit 1' ERR

# 运行主函数
main "$@" 