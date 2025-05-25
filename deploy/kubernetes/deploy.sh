#!/bin/bash

# 索克生活微服务集成优化部署脚本
# 自动部署Istio、Consul、监控等基础设施组件

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

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    # 检查kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl 未安装，请先安装 kubectl"
        exit 1
    fi
    
    # 检查helm
    if ! command -v helm &> /dev/null; then
        log_error "helm 未安装，请先安装 helm"
        exit 1
    fi
    
    # 检查istioctl
    if ! command -v istioctl &> /dev/null; then
        log_warning "istioctl 未安装，将跳过 Istio 部署"
        SKIP_ISTIO=true
    fi
    
    log_success "依赖检查完成"
}

# 创建命名空间
create_namespaces() {
    log_info "创建命名空间..."
    
    kubectl create namespace suoke-system --dry-run=client -o yaml | kubectl apply -f -
    kubectl create namespace consul --dry-run=client -o yaml | kubectl apply -f -
    kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
    
    log_success "命名空间创建完成"
}

# 部署Istio
deploy_istio() {
    if [ "$SKIP_ISTIO" = true ]; then
        log_warning "跳过 Istio 部署"
        return
    fi
    
    log_info "部署 Istio..."
    
    # 安装Istio
    istioctl install --set values.defaultRevision=default -y
    
    # 启用自动注入
    kubectl label namespace suoke-system istio-injection=enabled --overwrite
    
    # 应用配置
    kubectl apply -f istio-config.yaml
    
    log_success "Istio 部署完成"
}

# 部署Consul
deploy_consul() {
    log_info "部署 Consul..."
    
    # 添加Consul Helm仓库
    helm repo add hashicorp https://helm.releases.hashicorp.com
    helm repo update
    
    # 创建Consul配置
    cat > consul-values.yaml << EOF
global:
  name: consul
  datacenter: suoke-dc1
  
server:
  replicas: 3
  storage: 10Gi
  storageClass: ""
  
client:
  enabled: true
  
ui:
  enabled: true
  service:
    type: ClusterIP
    
connectInject:
  enabled: true
  
controller:
  enabled: true
EOF
    
    # 部署Consul
    helm upgrade --install consul hashicorp/consul \
        --namespace consul \
        --values consul-values.yaml \
        --wait
    
    # 应用自定义配置
    kubectl apply -f consul-deployment.yaml
    
    log_success "Consul 部署完成"
}

# 部署监控组件
deploy_monitoring() {
    log_info "部署监控组件..."
    
    # 添加Prometheus Helm仓库
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo add jaegertracing https://jaegertracing.github.io/helm-charts
    helm repo update
    
    # 部署Prometheus
    helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
        --namespace monitoring \
        --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
        --set prometheus.prometheusSpec.podMonitorSelectorNilUsesHelmValues=false \
        --wait
    
    # 部署Jaeger
    helm upgrade --install jaeger jaegertracing/jaeger \
        --namespace monitoring \
        --set provisionDataStore.cassandra=false \
        --set storage.type=memory \
        --set agent.enabled=false \
        --set collector.enabled=true \
        --set query.enabled=true \
        --wait
    
    log_success "监控组件部署完成"
}

# 部署配置文件
deploy_configs() {
    log_info "部署配置文件..."
    
    # 创建ConfigMap
    kubectl create configmap suoke-config \
        --from-file=../prometheus/ \
        --namespace=suoke-system \
        --dry-run=client -o yaml | kubectl apply -f -
    
    log_success "配置文件部署完成"
}

# 验证部署
verify_deployment() {
    log_info "验证部署状态..."
    
    # 检查Pod状态
    log_info "检查 suoke-system 命名空间的 Pod..."
    kubectl get pods -n suoke-system
    
    log_info "检查 consul 命名空间的 Pod..."
    kubectl get pods -n consul
    
    log_info "检查 monitoring 命名空间的 Pod..."
    kubectl get pods -n monitoring
    
    # 检查服务状态
    log_info "检查服务状态..."
    kubectl get svc -n suoke-system
    kubectl get svc -n consul
    kubectl get svc -n monitoring
    
    log_success "部署验证完成"
}

# 显示访问信息
show_access_info() {
    log_info "获取访问信息..."
    
    echo ""
    echo "=== 服务访问信息 ==="
    
    # Consul UI
    CONSUL_PORT=$(kubectl get svc consul-ui -n consul -o jsonpath='{.spec.ports[0].port}')
    echo "Consul UI: kubectl port-forward svc/consul-ui -n consul 8500:$CONSUL_PORT"
    echo "然后访问: http://localhost:8500"
    
    # Prometheus
    PROMETHEUS_PORT=$(kubectl get svc prometheus-kube-prometheus-prometheus -n monitoring -o jsonpath='{.spec.ports[0].port}')
    echo "Prometheus: kubectl port-forward svc/prometheus-kube-prometheus-prometheus -n monitoring 9090:$PROMETHEUS_PORT"
    echo "然后访问: http://localhost:9090"
    
    # Grafana
    GRAFANA_PORT=$(kubectl get svc prometheus-grafana -n monitoring -o jsonpath='{.spec.ports[0].port}')
    echo "Grafana: kubectl port-forward svc/prometheus-grafana -n monitoring 3000:$GRAFANA_PORT"
    echo "然后访问: http://localhost:3000"
    echo "默认用户名: admin"
    echo "默认密码: $(kubectl get secret prometheus-grafana -n monitoring -o jsonpath='{.data.admin-password}' | base64 -d)"
    
    # Jaeger
    JAEGER_PORT=$(kubectl get svc jaeger-query -n monitoring -o jsonpath='{.spec.ports[0].port}')
    echo "Jaeger: kubectl port-forward svc/jaeger-query -n monitoring 16686:$JAEGER_PORT"
    echo "然后访问: http://localhost:16686"
    
    echo ""
    log_success "访问信息显示完成"
}

# 清理部署
cleanup() {
    log_warning "开始清理部署..."
    
    # 删除Helm releases
    helm uninstall consul -n consul || true
    helm uninstall prometheus -n monitoring || true
    helm uninstall jaeger -n monitoring || true
    
    # 删除命名空间
    kubectl delete namespace suoke-system || true
    kubectl delete namespace consul || true
    kubectl delete namespace monitoring || true
    
    # 卸载Istio
    if [ "$SKIP_ISTIO" != true ]; then
        istioctl uninstall --purge -y || true
    fi
    
    log_success "清理完成"
}

# 主函数
main() {
    echo "=== 索克生活微服务集成优化部署脚本 ==="
    echo ""
    
    case "${1:-deploy}" in
        "deploy")
            check_dependencies
            create_namespaces
            deploy_istio
            deploy_consul
            deploy_monitoring
            deploy_configs
            verify_deployment
            show_access_info
            ;;
        "cleanup")
            cleanup
            ;;
        "verify")
            verify_deployment
            ;;
        "info")
            show_access_info
            ;;
        *)
            echo "用法: $0 [deploy|cleanup|verify|info]"
            echo ""
            echo "命令说明:"
            echo "  deploy  - 部署所有组件 (默认)"
            echo "  cleanup - 清理所有部署"
            echo "  verify  - 验证部署状态"
            echo "  info    - 显示访问信息"
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@" 