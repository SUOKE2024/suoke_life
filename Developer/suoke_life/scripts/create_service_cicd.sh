#!/bin/bash
# 索克生活微服务CI/CD配置生成脚本
# 用法: ./scripts/create_service_cicd.sh <服务名称> [服务端口] [版本号]
# 例如: ./scripts/create_service_cicd.sh new-service 3010 1.0.0

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

# 检查参数
if [ "$#" -lt 1 ]; then
  print_error "用法: $0 <服务名称> [服务端口] [版本号]
  例如: $0 new-service 3010 1.0.0"
fi

SERVICE_NAME=$1
SERVICE_PORT=${2:-3000}  # 默认端口3000
SERVICE_VERSION=${3:-"1.0.0"}  # 默认版本1.0.0
SERVICE_PATH="services/$SERVICE_NAME"
CICD_FILE=".github/workflows/${SERVICE_NAME}-ci-cd.yml"

print_header "正在为服务 $SERVICE_NAME 创建CI/CD配置"

# 检查服务目录是否存在
if [ ! -d "$SERVICE_PATH" ]; then
  print_warning "服务目录不存在: $SERVICE_PATH"
  read -p "是否创建服务目录结构? (y/n): " CREATE_DIR
  if [[ "$CREATE_DIR" =~ ^[Yy]$ ]]; then
    mkdir -p "$SERVICE_PATH/src" "$SERVICE_PATH/k8s/base" "$SERVICE_PATH/k8s/overlays/dev" "$SERVICE_PATH/k8s/overlays/staging" "$SERVICE_PATH/k8s/overlays/prod"
    print_success "已创建服务目录结构"
  else
    print_error "无法继续，服务目录不存在"
  fi
fi

# 检查CI/CD文件是否已存在
if [ -f "$CICD_FILE" ]; then
  print_warning "CI/CD配置文件已存在: $CICD_FILE"
  read -p "是否覆盖? (y/n): " OVERWRITE
  if [[ ! "$OVERWRITE" =~ ^[Yy]$ ]]; then
    print_error "操作取消"
  fi
fi

# 创建中文服务名称
read -p "请输入服务的中文名称 (例如: 用户服务): " CHINESE_SERVICE_NAME
if [ -z "$CHINESE_SERVICE_NAME" ]; then
  CHINESE_SERVICE_NAME="$SERVICE_NAME"
fi

# 创建CI/CD配置文件
print_header "生成CI/CD配置文件"

cat > "$CICD_FILE" <<EOL
name: ${CHINESE_SERVICE_NAME} CI/CD

on:
  push:
    paths:
      - 'services/${SERVICE_NAME}/**'
      - '.github/workflows/${SERVICE_NAME}-ci-cd.yml'
      - '.github/workflows/templates/service-ci-cd-template.yml'
  pull_request:
    paths:
      - 'services/${SERVICE_NAME}/**'
  workflow_dispatch:
    inputs:
      environment:
        description: '部署环境'
        required: true
        default: 'dev'
        type: choice
        options:
          - dev
          - staging
          - prod
      version:
        description: '指定版本号(不填使用默认版本)'
        required: false
        type: string

jobs:
  call-template-workflow:
    uses: ./.github/workflows/templates/service-ci-cd-template.yml
    with:
      service_name: ${SERVICE_NAME}
      service_path: services/${SERVICE_NAME}
      service_version: \${{ github.event.inputs.version || '${SERVICE_VERSION}' }}
      deployments: '["dev"]'
      container_port: ${SERVICE_PORT}
      health_check_path: "/health"
    secrets:
      REGISTRY_USERNAME: \${{ secrets.REGISTRY_USERNAME }}
      REGISTRY_PASSWORD: \${{ secrets.REGISTRY_PASSWORD }}
      KUBE_CONFIG_DEV: \${{ secrets.KUBE_CONFIG_DEV }}
      KUBE_CONFIG_STAGING: \${{ secrets.KUBE_CONFIG_STAGING }}
      KUBE_CONFIG_PROD: \${{ secrets.KUBE_CONFIG_PROD }}
EOL

print_success "已创建CI/CD配置文件: $CICD_FILE"

# 尝试验证服务配置
print_header "尝试验证服务配置"
if ./scripts/validate_deployment.sh "$SERVICE_NAME"; then
  print_success "服务配置验证通过"
else
  print_warning "服务配置验证失败，尝试自动修复"
  ./scripts/validate_deployment.sh "$SERVICE_NAME" --fix
fi

print_header "CI/CD配置创建完成"
echo "服务名称: $SERVICE_NAME ($CHINESE_SERVICE_NAME)"
echo "服务路径: $SERVICE_PATH"
echo "配置文件: $CICD_FILE"
echo "服务端口: $SERVICE_PORT"
echo "服务版本: $SERVICE_VERSION"
echo ""
echo "您可以使用以下命令验证和部署此服务:"
echo "  ./scripts/validate_deployment.sh $SERVICE_NAME"
echo "  ./scripts/deploy.sh $SERVICE_NAME dev $SERVICE_VERSION"
echo ""
print_success "操作完成!" 