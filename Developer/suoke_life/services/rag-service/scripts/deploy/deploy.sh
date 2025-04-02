#!/bin/bash
set -e

# 定义颜色代码
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # 无颜色

# 定义函数
log() {
  echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
  echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
  echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
  exit 1
}

# 检查kubectl是否已安装
if ! command -v kubectl &> /dev/null; then
  error "kubectl 未安装，请先安装kubectl"
fi

# 检查输入参数
if [ $# -lt 1 ]; then
  echo "用法: $0 <环境名称> [命名空间]"
  echo "环境名称: dev, test, prod"
  echo "命名空间: 可选，默认为 suoke-<环境名称>"
  exit 1
fi

# 环境和命名空间
ENV=$1
case $ENV in
  dev)
    NAMESPACE=${2:-"suoke"}
    ;;
  test)
    NAMESPACE=${2:-"suoke-test"}
    ;;
  prod)
    NAMESPACE=${2:-"suoke-prod"}
    ;;
  *)
    error "不支持的环境: $ENV. 请使用 dev, test 或 prod"
    ;;
esac

# 检查命名空间是否存在，不存在则创建
if ! kubectl get namespace $NAMESPACE &> /dev/null; then
  log "命名空间 $NAMESPACE 不存在，正在创建..."
  kubectl create namespace $NAMESPACE
fi

# 部署 Secrets
if [ ! -f "kubernetes/secrets-$ENV.yaml" ]; then
  warn "未找到 kubernetes/secrets-$ENV.yaml，跳过 Secrets 部署"
else
  log "部署 Secrets 到 $NAMESPACE 命名空间..."
  kubectl apply -f kubernetes/secrets-$ENV.yaml -n $NAMESPACE
fi

# 部署 ConfigMap
log "部署 ConfigMap 到 $NAMESPACE 命名空间..."
kubectl apply -f kubernetes/rag-service-config-$ENV.yaml -n $NAMESPACE

# 部署持久卷声明
log "部署持久卷声明到 $NAMESPACE 命名空间..."
kubectl apply -f kubernetes/rag-service-pvc.yaml -n $NAMESPACE

# 部署应用
log "部署 RAG 服务到 $NAMESPACE 命名空间..."
kubectl apply -f kubernetes/rag-service.yaml -n $NAMESPACE

# 等待部署完成
log "等待部署完成..."
kubectl rollout status deployment/rag-service -n $NAMESPACE --timeout=180s

# 检查部署状态
PODS_RUNNING=$(kubectl get pods -n $NAMESPACE -l app=rag-service -o jsonpath='{.items[*].status.phase}' | tr ' ' '\n' | grep -c "Running" || true)
PODS_TOTAL=$(kubectl get pods -n $NAMESPACE -l app=rag-service -o jsonpath='{.items[*].status.phase}' | tr ' ' '\n' | wc -l || true)

if [ "$PODS_RUNNING" -eq "$PODS_TOTAL" ] && [ "$PODS_TOTAL" -gt 0 ]; then
  log "部署成功完成！$PODS_RUNNING/$PODS_TOTAL 个 Pod 正在运行"
else
  error "部署未完全成功，只有 $PODS_RUNNING/$PODS_TOTAL 个 Pod 正在运行。请检查日志获取更多信息。"
fi

# 显示服务信息
log "服务详情:"
kubectl get service rag-service -n $NAMESPACE -o wide

# 如果使用Ingress，显示Ingress信息
if kubectl get ingress -n $NAMESPACE 2>/dev/null | grep -q "rag-service"; then
  log "Ingress详情:"
  kubectl get ingress -n $NAMESPACE | grep "rag-service"
fi

log "部署脚本执行完成"