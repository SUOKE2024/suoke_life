#!/bin/bash

set -e

# 彩色输出函数
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 输出带颜色的消息
info() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
  echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warn() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

# 默认参数
ENVIRONMENT="prod"

# 解析命令行参数
while [[ $# -gt 0 ]]; do
  case $1 in
    --env|-e)
      ENVIRONMENT="$2"
      shift 2
      ;;
    --help|-h)
      echo "用法: $0 [选项]"
      echo "选项:"
      echo "  --env, -e <环境名>   指定环境名称 (默认: prod)"
      echo "  --help, -h           显示帮助信息"
      exit 0
      ;;
    *)
      error "未知选项: $1"
      exit 1
      ;;
  esac
done

# 检查环境
if ! command -v kubectl &> /dev/null; then
  error "请先安装 kubectl"
  exit 1
fi

# 验证输入
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
  error "环境必须是 dev, staging 或 prod"
  exit 1
fi

# 命名空间
NAMESPACE="suoke-$ENVIRONMENT"

# 显示标题
info "=================================="
info "  RAG服务部署状态 ($ENVIRONMENT)"
info "=================================="

# 检查命名空间是否存在
if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
  error "命名空间 $NAMESPACE 不存在"
  exit 1
fi

# 检查部署
info "检查部署状态..."
DEPLOY_STATUS=$(kubectl get deployment rag-service -n "$NAMESPACE" -o jsonpath='{.status.conditions[?(@.type=="Available")].status}' 2>/dev/null || echo "NotFound")
DEPLOY_REPLICAS=$(kubectl get deployment rag-service -n "$NAMESPACE" -o jsonpath='{.status.readyReplicas}/{.status.replicas}' 2>/dev/null || echo "0/0")

if [ "$DEPLOY_STATUS" == "True" ]; then
  success "部署状态: 可用 ($DEPLOY_REPLICAS)"
elif [ "$DEPLOY_STATUS" == "NotFound" ]; then
  warn "部署不存在"
else
  warn "部署状态: 不可用 ($DEPLOY_REPLICAS)"
  
  # 获取部署事件
  echo
  info "最近部署事件:"
  kubectl get events --field-selector involvedObject.kind=Deployment,involvedObject.name=rag-service -n "$NAMESPACE" --sort-by='.lastTimestamp' | tail -5
fi

# 检查pod
echo
info "Pod 状态:"
kubectl get pods -n "$NAMESPACE" -l app=rag-service -o wide

# 检查服务
echo
info "服务状态:"
kubectl get svc rag-service -n "$NAMESPACE" -o wide 2>/dev/null || echo "服务不存在"

# 检查配置
echo
info "配置状态:"
kubectl get configmap -n "$NAMESPACE" -l app=rag-service 2>/dev/null || echo "未找到相关ConfigMap"

# 检查密钥
echo
info "密钥状态:"
kubectl get secret -n "$NAMESPACE" -l app=rag-service 2>/dev/null || echo "未找到相关Secret"

# 显示最近日志
echo
info "最近日志 (如果存在):"
POD_NAME=$(kubectl get pods -n "$NAMESPACE" -l app=rag-service -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -n "$POD_NAME" ]; then
  kubectl logs --tail=10 "$POD_NAME" -n "$NAMESPACE" || echo "无法获取日志"
else
  warn "未找到Pod，无法显示日志"
fi

# 输出健康检查URL (如果有LoadBalancer或者NodePort)
echo
info "健康检查:"
SVC_TYPE=$(kubectl get svc rag-service -n "$NAMESPACE" -o jsonpath='{.spec.type}' 2>/dev/null || echo "")
if [ "$SVC_TYPE" == "LoadBalancer" ]; then
  SVC_IP=$(kubectl get svc rag-service -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
  SVC_PORT=$(kubectl get svc rag-service -n "$NAMESPACE" -o jsonpath='{.spec.ports[0].port}' 2>/dev/null)
  if [ -n "$SVC_IP" ] && [ -n "$SVC_PORT" ]; then
    echo "健康检查URL: http://$SVC_IP:$SVC_PORT/health"
    # 尝试健康检查
    if curl -s -f "http://$SVC_IP:$SVC_PORT/health" &> /dev/null; then
      success "健康检查: 通过"
    else
      warn "健康检查: 失败"
    fi
  else
    warn "健康检查URL: 无法确定 (LoadBalancer可能尚未分配IP)"
  fi
elif [ "$SVC_TYPE" == "NodePort" ]; then
  NODE_PORT=$(kubectl get svc rag-service -n "$NAMESPACE" -o jsonpath='{.spec.ports[0].nodePort}' 2>/dev/null)
  if [ -n "$NODE_PORT" ]; then
    echo "健康检查URL: http://<node-ip>:$NODE_PORT/health"
  else
    warn "健康检查URL: 无法确定"
  fi
elif [ "$SVC_TYPE" == "ClusterIP" ]; then
  CLUSTER_IP=$(kubectl get svc rag-service -n "$NAMESPACE" -o jsonpath='{.spec.clusterIP}' 2>/dev/null)
  SVC_PORT=$(kubectl get svc rag-service -n "$NAMESPACE" -o jsonpath='{.spec.ports[0].port}' 2>/dev/null)
  if [ -n "$CLUSTER_IP" ] && [ -n "$SVC_PORT" ]; then
    echo "健康检查URL (仅集群内): http://$CLUSTER_IP:$SVC_PORT/health"
  else
    warn "健康检查URL: 无法确定"
  fi
else
  warn "未找到服务或服务类型不是LoadBalancer/NodePort/ClusterIP"
fi

# 显示总结
echo
info "=================================="
if [ "$DEPLOY_STATUS" == "True" ]; then
  success "RAG服务部署状态: 正常运行"
  info "您可以使用以下命令进一步查看详情:"
  echo "  kubectl port-forward svc/rag-service 8080:8080 -n $NAMESPACE"
  echo "  然后访问: http://localhost:8080/health"
elif [ "$DEPLOY_STATUS" == "NotFound" ]; then
  warn "RAG服务尚未部署，您可以使用以下命令部署:"
  echo "  make deploy-rag"
else
  error "RAG服务部署状态: 异常"
  info "您可以查看详细日志来排查问题:"
  echo "  kubectl logs -f -l app=rag-service -n $NAMESPACE"
fi
info "==================================" 