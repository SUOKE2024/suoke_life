#!/bin/bash

# 索克生活 - ArgoCD应用部署脚本
# 此脚本用于将生成的ArgoCD应用定义部署到ArgoCD服务器

# 退出前执行清理
trap 'echo "脚本执行中断"; exit 1' INT TERM

# 设置颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# 工具函数
print_header() {
  echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

print_success() {
  echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
  echo -e "${RED}✗ $1${NC}"
}

print_warning() {
  echo -e "${YELLOW}! $1${NC}"
}

check_command() {
  if ! command -v $1 &> /dev/null; then
    print_error "$1 命令未找到，请先安装"
    echo "可以通过以下方式安装："
    case $1 in
      argocd)
        echo "brew install argocd"
        ;;
      kubectl)
        echo "brew install kubectl"
        ;;
      *)
        echo "请查阅相关文档安装 $1"
        ;;
    esac
    exit 1
  fi
}

# 检查必要的命令
check_command argocd
check_command kubectl

# 显示用法
print_header "ArgoCD应用部署工具"
echo "此脚本将把生成的ArgoCD应用定义部署到ArgoCD服务器"
echo ""
echo "用法: $0 <ARGOCD_SERVER> [namespace]"
echo "示例: $0 argocd.suoke.life"
echo ""

# 检查参数
if [ $# -lt 1 ]; then
  print_error "缺少必要参数：ARGOCD_SERVER"
  echo "用法: $0 <ARGOCD_SERVER> [namespace]"
  echo "示例: $0 argocd.suoke.life"
  exit 1
fi

ARGOCD_SERVER=$1
NAMESPACE=${2:-argocd}

# 确保argocd-apps目录存在
if [ ! -d "argocd-apps" ]; then
  print_error "argocd-apps目录不存在，请先运行迁移工作流生成应用定义"
  exit 1
fi

# 登录ArgoCD
print_header "登录ArgoCD服务器 ${ARGOCD_SERVER}"
argocd login --insecure ${ARGOCD_SERVER}

if [ $? -ne 0 ]; then
  print_error "登录ArgoCD失败，请检查地址和凭据"
  exit 1
fi

print_success "登录ArgoCD成功"

# 检查并创建项目
print_header "检查并创建ArgoCD项目"
if ! argocd proj get default &> /dev/null; then
  echo "创建默认项目..."
  argocd proj create default \
    --description "默认项目，用于索克生活微服务" \
    --dest "*,*" \
    --src "*" \
    --allow-cluster-resource "*/*"
  
  if [ $? -eq 0 ]; then
    print_success "创建默认项目成功"
  else
    print_warning "创建默认项目失败，尝试使用现有项目"
  fi
else
  print_success "默认项目已存在"
fi

# 部署ApplicationSet
print_header "部署ApplicationSet"
if [ -f "argocd-apps/suoke-microservices-appset.yaml" ]; then
  echo "正在部署ApplicationSet..."
  kubectl apply -f argocd-apps/suoke-microservices-appset.yaml -n ${NAMESPACE}
  
  if [ $? -eq 0 ]; then
    print_success "ApplicationSet部署成功"
  else
    print_error "ApplicationSet部署失败"
    exit 1
  fi
else
  print_warning "ApplicationSet文件不存在，将逐个部署应用"
fi

# 部署单个应用
print_header "部署单个应用"
for app_file in argocd-apps/*-*.yaml; do
  if [[ "$app_file" != *appset* ]]; then
    echo "正在部署 ${app_file}..."
    kubectl apply -f ${app_file} -n ${NAMESPACE}
    
    if [ $? -eq 0 ]; then
      print_success "应用 ${app_file} 部署成功"
    else
      print_warning "应用 ${app_file} 部署失败"
    fi
  fi
done

# 验证部署
print_header "验证应用部署状态"
echo "正在获取所有应用状态..."
argocd app list

print_header "部署完成"
echo "请访问ArgoCD Web界面检查应用同步状态: https://${ARGOCD_SERVER}"
echo ""
echo "你可以使用以下命令手动同步所有应用:"
echo "argocd app sync --async --prune $(argocd app list -o name | tr '\n' ' ')"
echo ""
echo "如需监控同步进度，可以使用:"
echo "argocd app list"