#!/bin/bash
# 索克生活微服务CI/CD管理脚本
# 用法: ./scripts/cicd.sh <命令> <选项>
# 命令:
#   - validate: 验证服务配置
#   - deploy: 部署服务
#   - status: 查看部署状态
#   - rollback: 回滚服务版本
# 例如: ./scripts/cicd.sh deploy rag-service dev 1.2.0

set -e  # 任何命令失败则立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# 打印带颜色的标题
print_header() {
  echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

# 打印成功消息
print_success() {
  echo -e "${GREEN}✅ $1${NC}"
}

# 打印错误消息
print_error() {
  echo -e "${RED}❌ $1${NC}"
  exit 1
}

# 打印警告消息
print_warning() {
  echo -e "${YELLOW}⚠️ $1${NC}"
}

# 打印帮助信息
print_help() {
  echo "用法: $0 <命令> [选项]"
  echo ""
  echo "命令:"
  echo "  validate <服务名> [--fix]    验证服务配置，可选自动修复"
  echo "  deploy <服务名> <环境> [版本] 部署服务到指定环境"
  echo "  status <服务名> <环境>       查看服务部署状态"
  echo "  rollback <服务名> <环境> <版本> 回滚服务到指定版本"
  echo "  deploy-all <环境>            部署所有服务到指定环境"
  echo "  list                        列出所有可用服务"
  echo "  help                        显示帮助信息"
  echo ""
  echo "环境: dev, staging, prod"
  echo ""
  echo "示例:"
  echo "  $0 validate rag-service --fix"
  echo "  $0 deploy rag-service dev 1.2.0"
  echo "  $0 status rag-service prod"
  echo "  $0 rollback auth-service staging 1.1.0"
  echo "  $0 deploy-all dev"
  echo "  $0 list"
}

# 检查参数
if [ "$#" -lt 1 ]; then
  print_help
  exit 1
fi

COMMAND=$1
shift

# 获取可用服务列表
get_services() {
  find services -maxdepth 1 -type d | grep -v "^services$" | sed 's/services\///'
}

# 处理命令
case $COMMAND in
  validate)
    if [ "$#" -lt 1 ]; then
      print_error "缺少服务名参数"
    fi
    SERVICE_NAME=$1
    FIX_FLAG=${2:-""}
    print_header "验证服务: $SERVICE_NAME"
    # 调用验证脚本
    ./scripts/validate_deployment.sh $SERVICE_NAME $FIX_FLAG
    ;;
    
  deploy)
    if [ "$#" -lt 2 ]; then
      print_error "缺少参数，用法: $0 deploy <服务名> <环境> [版本]"
    fi
    SERVICE_NAME=$1
    ENVIRONMENT=$2
    VERSION=${3:-""}
    
    print_header "部署服务: $SERVICE_NAME 到 $ENVIRONMENT 环境"
    
    # 验证服务配置
    echo "先验证服务配置..."
    ./scripts/validate_deployment.sh $SERVICE_NAME || { print_error "服务验证失败，中止部署"; exit 1; }
    
    # 调用部署脚本
    ./scripts/deploy.sh $SERVICE_NAME $ENVIRONMENT $VERSION
    ;;
    
  status)
    if [ "$#" -lt 2 ]; then
      print_error "缺少参数，用法: $0 status <服务名> <环境>"
    fi
    SERVICE_NAME=$1
    ENVIRONMENT=$2
    
    print_header "查看服务: $SERVICE_NAME 在 $ENVIRONMENT 环境的状态"
    
    # 获取服务状态
    echo "获取Kubernetes部署状态..."
    
    # 根据环境选择命名空间
    case $ENVIRONMENT in
      dev)
        NAMESPACE="suoke-dev"
        ;;
      staging)
        NAMESPACE="suoke-staging"
        ;;
      prod)
        NAMESPACE="suoke-prod"
        ;;
      *)
        print_error "无效的环境: $ENVIRONMENT，必须是dev、staging或prod之一"
        ;;
    esac
    
    # 获取部署状态
    echo "连接Kubernetes集群..."
    if [ -z "$KUBECONFIG" ]; then
      echo "未设置KUBECONFIG环境变量，使用默认配置"
    fi
    
    echo "获取Pod状态..."
    kubectl get pods -n $NAMESPACE -l app=$SERVICE_NAME -o wide
    
    echo "获取Deployment状态..."
    kubectl get deployment -n $NAMESPACE -l app=$SERVICE_NAME -o wide
    
    echo "获取服务状态..."
    kubectl get service -n $NAMESPACE -l app=$SERVICE_NAME -o wide
    
    echo "获取最近的Pod事件..."
    kubectl get events -n $NAMESPACE --field-selector involvedObject.name=$SERVICE_NAME --sort-by='.lastTimestamp' | tail -5
    
    # 尝试健康检查
    echo "尝试健康检查..."
    POD_NAME=$(kubectl get pods -n $NAMESPACE -l app=$SERVICE_NAME -o jsonpath="{.items[0].metadata.name}" 2>/dev/null)
    if [ -n "$POD_NAME" ]; then
      echo "使用端口转发进行健康检查..."
      # 找出容器端口
      PORT=$(kubectl get deployment -n $NAMESPACE $SERVICE_NAME -o jsonpath="{.spec.template.spec.containers[0].ports[0].containerPort}" 2>/dev/null || echo "3000")
      nohup kubectl port-forward -n $NAMESPACE $POD_NAME 8080:$PORT &
      PF_PID=$!
      sleep 3
      HEALTH_CHECK=$(curl -s http://localhost:8080/health 2>/dev/null || echo '{"status":"unavailable"}')
      echo "健康检查结果: $HEALTH_CHECK"
      kill $PF_PID 2>/dev/null || true
    else
      print_warning "未找到运行中的Pod，无法进行健康检查"
    fi
    ;;
    
  rollback)
    if [ "$#" -lt 3 ]; then
      print_error "缺少参数，用法: $0 rollback <服务名> <环境> <版本>"
    fi
    SERVICE_NAME=$1
    ENVIRONMENT=$2
    VERSION=$3
    
    print_header "回滚服务: $SERVICE_NAME 在 $ENVIRONMENT 环境到版本 $VERSION"
    
    # 调用部署脚本(使用指定版本进行部署即实现回滚)
    ./scripts/deploy.sh $SERVICE_NAME $ENVIRONMENT $VERSION
    ;;
    
  deploy-all)
    if [ "$#" -lt 1 ]; then
      print_error "缺少环境参数，用法: $0 deploy-all <环境>"
    fi
    ENVIRONMENT=$1
    VERSION=${2:-""}
    
    print_header "部署所有服务到 $ENVIRONMENT 环境"
    
    # 获取服务列表
    SERVICES=$(get_services)
    
    # 逐个部署服务
    for SERVICE in $SERVICES; do
      echo "--------------------------"
      echo "准备部署: $SERVICE"
      
      # 验证服务
      echo "先验证服务配置..."
      if ./scripts/validate_deployment.sh $SERVICE > /dev/null 2>&1; then
        echo "服务 $SERVICE 验证通过，开始部署..."
        ./scripts/deploy.sh $SERVICE $ENVIRONMENT $VERSION || print_warning "服务 $SERVICE 部署失败，继续下一个"
      else
        print_warning "服务 $SERVICE 验证失败，尝试自动修复..."
        if ./scripts/validate_deployment.sh $SERVICE --fix > /dev/null 2>&1; then
          echo "服务 $SERVICE 已自动修复，开始部署..."
          ./scripts/deploy.sh $SERVICE $ENVIRONMENT $VERSION || print_warning "服务 $SERVICE 部署失败，继续下一个"
        else
          print_warning "服务 $SERVICE 无法自动修复，跳过部署"
        fi
      fi
    done
    
    print_success "所有服务部署完成"
    ;;
    
  list)
    print_header "可用服务列表"
    SERVICES=$(get_services)
    for SERVICE in $SERVICES; do
      if [ -f "services/$SERVICE/package.json" ]; then
        VERSION=$(grep -o '"version": *"[^"]*"' "services/$SERVICE/package.json" | cut -d'"' -f4)
        echo "$SERVICE (版本: $VERSION)"
      else
        echo "$SERVICE (版本: 未知)"
      fi
    done
    ;;
    
  help)
    print_help
    ;;
    
  *)
    print_error "未知命令: $COMMAND，使用 '$0 help' 查看帮助"
    ;;
esac 