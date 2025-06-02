#!/bin/bash

# 索克生活智能体弹性伸缩和AI模型版本管理部署脚本
# 作者: 索克生活开发团队
# 版本: v1.0.0

set -euo pipefail

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
    log_info "检查依赖项..."
    
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl 未安装，请先安装 kubectl"
        exit 1
    fi
    
    if ! command -v helm &> /dev/null; then
        log_warning "helm 未安装，某些功能可能不可用"
    fi
    
    # 检查 kubectl 连接
    if ! kubectl cluster-info &> /dev/null; then
        log_error "无法连接到 Kubernetes 集群"
        exit 1
    fi
    
    log_success "依赖检查完成"
}

# 创建命名空间
create_namespace() {
    log_info "创建命名空间..."
    
    kubectl create namespace suoke-life --dry-run=client -o yaml | kubectl apply -f -
    
    # 添加标签
    kubectl label namespace suoke-life app=suoke-life --overwrite
    kubectl label namespace suoke-life component=ai-health-platform --overwrite
    
    log_success "命名空间创建完成"
}

# 部署CRD
deploy_crds() {
    log_info "部署AI模型版本管理CRD..."
    
    kubectl apply -f ai-model-version-crd.yaml
    
    # 等待CRD就绪
    log_info "等待CRD就绪..."
    kubectl wait --for condition=established --timeout=60s crd/aimodels.suoke.life
    kubectl wait --for condition=established --timeout=60s crd/modelversions.suoke.life
    kubectl wait --for condition=established --timeout=60s crd/modelregistries.suoke.life
    
    log_success "CRD部署完成"
}

# 部署AI模型示例
deploy_ai_models() {
    log_info "部署AI模型配置..."
    
    kubectl apply -f ai-model-examples.yaml -n suoke-life
    
    log_success "AI模型配置部署完成"
}

# 检查Metrics Server
check_metrics_server() {
    log_info "检查Metrics Server..."
    
    if ! kubectl get deployment metrics-server -n kube-system &> /dev/null; then
        log_warning "Metrics Server 未安装，HPA可能无法正常工作"
        log_info "安装Metrics Server..."
        
        kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
        
        # 等待Metrics Server就绪
        kubectl wait --for=condition=available --timeout=300s deployment/metrics-server -n kube-system
        
        log_success "Metrics Server 安装完成"
    else
        log_success "Metrics Server 已安装"
    fi
}

# 检查VPA
check_vpa() {
    log_info "检查Vertical Pod Autoscaler..."
    
    if ! kubectl get deployment vpa-recommender -n kube-system &> /dev/null; then
        log_warning "VPA 未安装，垂直伸缩功能不可用"
        log_info "请参考文档手动安装VPA: https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler"
    else
        log_success "VPA 已安装"
    fi
}

# 部署HPA
deploy_hpa() {
    log_info "部署智能体HPA配置..."
    
    kubectl apply -f hpa-agents.yaml -n suoke-life
    
    # 检查HPA状态
    log_info "检查HPA状态..."
    sleep 10
    kubectl get hpa -n suoke-life
    
    log_success "HPA部署完成"
}

# 部署VPA
deploy_vpa() {
    log_info "部署智能体VPA配置..."
    
    if kubectl get deployment vpa-recommender -n kube-system &> /dev/null; then
        kubectl apply -f vpa-agents.yaml -n suoke-life
        
        # 检查VPA状态
        log_info "检查VPA状态..."
        sleep 5
        kubectl get vpa -n suoke-life
        
        log_success "VPA部署完成"
    else
        log_warning "跳过VPA部署，因为VPA未安装"
    fi
}

# 验证部署
verify_deployment() {
    log_info "验证部署状态..."
    
    # 检查CRD
    log_info "检查CRD状态..."
    kubectl get crd | grep suoke.life
    
    # 检查AI模型
    log_info "检查AI模型状态..."
    kubectl get aimodels -n suoke-life
    
    # 检查模型版本
    log_info "检查模型版本状态..."
    kubectl get modelversions -n suoke-life
    
    # 检查模型注册表
    log_info "检查模型注册表状态..."
    kubectl get modelregistries -n suoke-life
    
    # 检查HPA
    log_info "检查HPA状态..."
    kubectl get hpa -n suoke-life
    
    # 检查VPA（如果存在）
    if kubectl get deployment vpa-recommender -n kube-system &> /dev/null; then
        log_info "检查VPA状态..."
        kubectl get vpa -n suoke-life
    fi
    
    log_success "部署验证完成"
}

# 生成监控仪表板
generate_monitoring_dashboard() {
    log_info "生成监控仪表板配置..."
    
    cat > monitoring-dashboard.yaml << EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: suoke-agents-dashboard
  namespace: suoke-life
  labels:
    grafana_dashboard: "1"
data:
  dashboard.json: |
    {
      "dashboard": {
        "title": "索克生活智能体监控",
        "panels": [
          {
            "title": "智能体CPU使用率",
            "type": "graph",
            "targets": [
              {
                "expr": "rate(container_cpu_usage_seconds_total{namespace=\"suoke-life\",pod=~\".*-agent-.*\"}[5m])"
              }
            ]
          },
          {
            "title": "智能体内存使用率",
            "type": "graph",
            "targets": [
              {
                "expr": "container_memory_usage_bytes{namespace=\"suoke-life\",pod=~\".*-agent-.*\"}"
              }
            ]
          },
          {
            "title": "HPA伸缩事件",
            "type": "graph",
            "targets": [
              {
                "expr": "kube_hpa_status_current_replicas{namespace=\"suoke-life\"}"
              }
            ]
          },
          {
            "title": "AI模型推理延迟",
            "type": "graph",
            "targets": [
              {
                "expr": "histogram_quantile(0.95, rate(ai_inference_duration_seconds_bucket{namespace=\"suoke-life\"}[5m]))"
              }
            ]
          }
        ]
      }
    }
EOF
    
    kubectl apply -f monitoring-dashboard.yaml
    
    log_success "监控仪表板配置生成完成"
}

# 清理函数
cleanup() {
    log_info "清理资源..."
    
    kubectl delete -f hpa-agents.yaml -n suoke-life --ignore-not-found=true
    kubectl delete -f vpa-agents.yaml -n suoke-life --ignore-not-found=true
    kubectl delete -f ai-model-examples.yaml -n suoke-life --ignore-not-found=true
    kubectl delete -f ai-model-version-crd.yaml --ignore-not-found=true
    kubectl delete configmap suoke-agents-dashboard -n suoke-life --ignore-not-found=true
    
    log_success "清理完成"
}

# 显示帮助信息
show_help() {
    cat << EOF
索克生活智能体弹性伸缩和AI模型版本管理部署脚本

用法: $0 [选项]

选项:
    deploy      部署所有组件
    cleanup     清理所有资源
    verify      验证部署状态
    dashboard   生成监控仪表板
    help        显示此帮助信息

示例:
    $0 deploy       # 部署所有组件
    $0 cleanup      # 清理所有资源
    $0 verify       # 验证部署状态
EOF
}

# 主函数
main() {
    case "${1:-deploy}" in
        "deploy")
            log_info "开始部署索克生活智能体弹性伸缩和AI模型版本管理..."
            check_dependencies
            create_namespace
            check_metrics_server
            check_vpa
            deploy_crds
            deploy_ai_models
            deploy_hpa
            deploy_vpa
            generate_monitoring_dashboard
            verify_deployment
            log_success "部署完成！"
            ;;
        "cleanup")
            log_info "开始清理资源..."
            cleanup
            ;;
        "verify")
            log_info "验证部署状态..."
            verify_deployment
            ;;
        "dashboard")
            log_info "生成监控仪表板..."
            generate_monitoring_dashboard
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            log_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@" 