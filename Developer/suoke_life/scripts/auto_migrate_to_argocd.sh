#!/bin/bash

# 索克生活 - 微服务自动迁移到ArgoCD脚本
# 此脚本自动将services目录下的所有微服务迁移到ArgoCD并实现部署

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
      kubectl)
        echo "brew install kubectl"
        ;;
      jq)
        echo "brew install jq"
        ;;
      argocd)
        echo "brew install argocd"
        ;;
      *)
        echo "请查阅相关文档安装 $1"
        ;;
    esac
    exit 1
  fi
}

# 显示用法
show_usage() {
  print_header "自动迁移微服务到ArgoCD"
  echo "此脚本自动将services目录下的所有微服务迁移到ArgoCD并实现部署"
  echo ""
  echo "用法: $0 [选项]"
  echo "选项:"
  echo "  --install-argocd       安装ArgoCD（如果已安装则跳过）"
  echo "  --argocd-namespace     ArgoCD命名空间（默认：argocd）"
  echo "  --argocd-host          ArgoCD访问域名（例如：argocd.suoke.life）"
  echo "  --ingress-class        Ingress类名（默认：nginx）"
  echo "  --environments         要部署的环境（逗号分隔，默认：dev,staging,prod）"
  echo "  --service-group        服务组（core,diagnosis,knowledge,ai,all,默认：all）"
  echo "  --help                 显示此帮助信息"
  echo ""
  echo "示例: $0 --install-argocd --argocd-host argocd.suoke.life --environments dev,staging"
  echo ""
}

# 默认参数
INSTALL_ARGOCD=false
ARGOCD_NAMESPACE="argocd"
ARGOCD_HOST=""
INGRESS_CLASS="nginx"
ENVIRONMENTS="dev,staging,prod"
SERVICE_GROUP="all"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 解析参数
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --install-argocd)
      INSTALL_ARGOCD=true
      shift
      ;;
    --argocd-namespace)
      ARGOCD_NAMESPACE="$2"
      shift
      shift
      ;;
    --argocd-host)
      ARGOCD_HOST="$2"
      shift
      shift
      ;;
    --ingress-class)
      INGRESS_CLASS="$2"
      shift
      shift
      ;;
    --environments)
      ENVIRONMENTS="$2"
      shift
      shift
      ;;
    --service-group)
      SERVICE_GROUP="$2"
      shift
      shift
      ;;
    --help)
      show_usage
      exit 0
      ;;
    *)
      print_error "未知选项: $1"
      show_usage
      exit 1
      ;;
  esac
done

# 检查工作目录
if [ ! -d "$PROJECT_ROOT/services" ]; then
  print_error "找不到服务目录: $PROJECT_ROOT/services"
  echo "请确保在正确的项目根目录中运行此脚本"
  exit 1
fi

# 检查必要的命令
check_command kubectl
check_command jq

# 创建argocd-apps目录
mkdir -p "$PROJECT_ROOT/argocd-apps"

# 步骤1: 安装ArgoCD（如果需要）
if [ "$INSTALL_ARGOCD" = true ]; then
  print_header "安装和配置ArgoCD"
  
  INSTALL_CMD="$SCRIPT_DIR/install_argocd.sh --namespace $ARGOCD_NAMESPACE"
  if [ -n "$ARGOCD_HOST" ]; then
    INSTALL_CMD="$INSTALL_CMD --ingress-host $ARGOCD_HOST --ingress-class $INGRESS_CLASS"
  fi
  
  echo "执行命令: $INSTALL_CMD"
  eval $INSTALL_CMD
  
  if [ $? -ne 0 ]; then
    print_error "ArgoCD安装失败"
    exit 1
  fi
  
  print_success "ArgoCD安装完成"
else
  print_header "跳过ArgoCD安装"
  echo "将使用现有的ArgoCD实例"
fi

# 步骤2: 发现微服务
print_header "发现微服务"

# 根据服务组筛选服务
case $SERVICE_GROUP in
  core)
    SERVICES=("api-gateway" "auth-service" "user-service")
    ;;
  diagnosis)
    SERVICES=("four-diagnosis-coordinator" "looking-diagnosis-service" "smell-diagnosis-service" "touch-diagnosis-service" "inquiry-diagnosis-service")
    ;;
  knowledge)
    SERVICES=("knowledge-graph-service" "knowledge-base-service" "rag-service")
    ;;
  ai)
    SERVICES=("agent-coordinator-service" "xiaoke-service" "xiaoai-service" "laoke-service" "soer-service")
    ;;
  all|*)
    # 获取services目录下的所有服务
    SERVICES=()
    for dir in "$PROJECT_ROOT/services"/*; do
      if [ -d "$dir" ] && [ "$(basename "$dir")" != "shared" ] && [ "$(basename "$dir")" != "config" ]; then
        SERVICES+=("$(basename "$dir")")
      fi
    done
    ;;
esac

echo "发现以下微服务:"
for service in "${SERVICES[@]}"; do
  echo "- $service"
done

# 确认服务数量
SERVICE_COUNT=${#SERVICES[@]}
if [ $SERVICE_COUNT -eq 0 ]; then
  print_error "没有发现微服务"
  exit 1
fi

print_success "发现了 $SERVICE_COUNT 个微服务"

# 步骤3: 生成ArgoCD应用定义
print_header "生成ArgoCD应用定义"

# 拆分环境列表
IFS=',' read -r -a ENV_ARRAY <<< "$ENVIRONMENTS"

# 获取Git仓库URL
REPO_URL=$(cd "$PROJECT_ROOT" && git config --get remote.origin.url)
if [[ "$REPO_URL" == git@* ]]; then
  REPO_URL=$(echo $REPO_URL | sed 's/git@github.com:/https:\/\/github.com\//')
fi

echo "使用Git仓库URL: $REPO_URL"

# 为每个服务和环境生成ArgoCD应用定义
for SERVICE in "${SERVICES[@]}"; do
  echo "生成 $SERVICE 的ArgoCD应用定义..."
  
  # 检查服务目录是否存在
  if [ ! -d "$PROJECT_ROOT/services/$SERVICE" ]; then
    print_warning "服务目录不存在: $PROJECT_ROOT/services/$SERVICE, 跳过"
    continue
  fi
  
  for ENV in "${ENV_ARRAY[@]}"; do
    # 检查环境配置是否存在
    if [ ! -d "$PROJECT_ROOT/services/$SERVICE/k8s/overlays/$ENV" ]; then
      print_warning "环境配置不存在: $PROJECT_ROOT/services/$SERVICE/k8s/overlays/$ENV, 跳过"
      continue
    fi
    
    echo "生成 $SERVICE-$ENV 应用定义..."
    
    # 使用简单的echo拼接YAML
    echo "apiVersion: argoproj.io/v1alpha1" > "$PROJECT_ROOT/argocd-apps/$SERVICE-$ENV.yaml"
    echo "kind: Application" >> "$PROJECT_ROOT/argocd-apps/$SERVICE-$ENV.yaml"
    echo "metadata:" >> "$PROJECT_ROOT/argocd-apps/$SERVICE-$ENV.yaml"
    echo "  name: $SERVICE-$ENV" >> "$PROJECT_ROOT/argocd-apps/$SERVICE-$ENV.yaml"
    echo "  namespace: $ARGOCD_NAMESPACE" >> "$PROJECT_ROOT/argocd-apps/$SERVICE-$ENV.yaml"
    echo "spec:" >> "$PROJECT_ROOT/argocd-apps/$SERVICE-$ENV.yaml"
    echo "  project: default" >> "$PROJECT_ROOT/argocd-apps/$SERVICE-$ENV.yaml"
    echo "  source:" >> "$PROJECT_ROOT/argocd-apps/$SERVICE-$ENV.yaml"
    echo "    repoURL: $REPO_URL" >> "$PROJECT_ROOT/argocd-apps/$SERVICE-$ENV.yaml"
    echo "    targetRevision: HEAD" >> "$PROJECT_ROOT/argocd-apps/$SERVICE-$ENV.yaml"
    echo "    path: services/$SERVICE/k8s/overlays/$ENV" >> "$PROJECT_ROOT/argocd-apps/$SERVICE-$ENV.yaml"
    echo "  destination:" >> "$PROJECT_ROOT/argocd-apps/$SERVICE-$ENV.yaml"
    echo "    server: https://kubernetes.default.svc" >> "$PROJECT_ROOT/argocd-apps/$SERVICE-$ENV.yaml"
    echo "    namespace: suoke-$ENV" >> "$PROJECT_ROOT/argocd-apps/$SERVICE-$ENV.yaml"
    echo "  syncPolicy:" >> "$PROJECT_ROOT/argocd-apps/$SERVICE-$ENV.yaml"
    echo "    automated:" >> "$PROJECT_ROOT/argocd-apps/$SERVICE-$ENV.yaml"
    echo "      prune: true" >> "$PROJECT_ROOT/argocd-apps/$SERVICE-$ENV.yaml"
    echo "      selfHeal: true" >> "$PROJECT_ROOT/argocd-apps/$SERVICE-$ENV.yaml"
    echo "    syncOptions:" >> "$PROJECT_ROOT/argocd-apps/$SERVICE-$ENV.yaml"
    echo "    - CreateNamespace=true" >> "$PROJECT_ROOT/argocd-apps/$SERVICE-$ENV.yaml"
    
    print_success "已生成: argocd-apps/$SERVICE-$ENV.yaml"
  done
done

# 生成ApplicationSet
print_header "生成ApplicationSet"

echo "正在生成ApplicationSet配置..."

# 构建元素列表JSON
ELEMENTS_JSON="["
ELEMENTS_COUNT=0

for SERVICE in "${SERVICES[@]}"; do
  if [ -d "$PROJECT_ROOT/services/$SERVICE/k8s/overlays" ]; then
    if [ $ELEMENTS_COUNT -gt 0 ]; then
      ELEMENTS_JSON+=","
    fi
    ELEMENTS_JSON+="{\"name\":\"$SERVICE\",\"path\":\"services/$SERVICE/k8s/overlays\"}"
    ELEMENTS_COUNT=$((ELEMENTS_COUNT+1))
  fi
done

ELEMENTS_JSON+="]"

# 创建环境列表JSON
ENV_JSON="["
ENV_COUNT=0

for ENV in "${ENV_ARRAY[@]}"; do
  if [ $ENV_COUNT -gt 0 ]; then
    ENV_JSON+=","
  fi
  ENV_JSON+="{\"environment\":\"$ENV\"}"
  ENV_COUNT=$((ENV_COUNT+1))
done

ENV_JSON+="]"

# 创建ApplicationSet文件
echo "apiVersion: argoproj.io/v1alpha1" > "$PROJECT_ROOT/argocd-apps/suoke-microservices-appset.yaml"
echo "kind: ApplicationSet" >> "$PROJECT_ROOT/argocd-apps/suoke-microservices-appset.yaml"
echo "metadata:" >> "$PROJECT_ROOT/argocd-apps/suoke-microservices-appset.yaml"
echo "  name: suoke-microservices" >> "$PROJECT_ROOT/argocd-apps/suoke-microservices-appset.yaml"
echo "  namespace: $ARGOCD_NAMESPACE" >> "$PROJECT_ROOT/argocd-apps/suoke-microservices-appset.yaml"
echo "spec:" >> "$PROJECT_ROOT/argocd-apps/suoke-microservices-appset.yaml"
echo "  generators:" >> "$PROJECT_ROOT/argocd-apps/suoke-microservices-appset.yaml"
echo "  - matrix:" >> "$PROJECT_ROOT/argocd-apps/suoke-microservices-appset.yaml"
echo "      generators:" >> "$PROJECT_ROOT/argocd-apps/suoke-microservices-appset.yaml"
echo "      - list:" >> "$PROJECT_ROOT/argocd-apps/suoke-microservices-appset.yaml"
echo "          elements: $ENV_JSON" >> "$PROJECT_ROOT/argocd-apps/suoke-microservices-appset.yaml"
echo "      - list:" >> "$PROJECT_ROOT/argocd-apps/suoke-microservices-appset.yaml"
echo "          elements: $ELEMENTS_JSON" >> "$PROJECT_ROOT/argocd-apps/suoke-microservices-appset.yaml"
echo "  template:" >> "$PROJECT_ROOT/argocd-apps/suoke-microservices-appset.yaml"
echo "    metadata:" >> "$PROJECT_ROOT/argocd-apps/suoke-microservices-appset.yaml"
echo "      name: '{{name}}-{{environment}}'" >> "$PROJECT_ROOT/argocd-apps/suoke-microservices-appset.yaml"
echo "    spec:" >> "$PROJECT_ROOT/argocd-apps/suoke-microservices-appset.yaml"
echo "      project: default" >> "$PROJECT_ROOT/argocd-apps/suoke-microservices-appset.yaml"
echo "      source:" >> "$PROJECT_ROOT/argocd-apps/suoke-microservices-appset.yaml"
echo "        repoURL: $REPO_URL" >> "$PROJECT_ROOT/argocd-apps/suoke-microservices-appset.yaml"
echo "        targetRevision: HEAD" >> "$PROJECT_ROOT/argocd-apps/suoke-microservices-appset.yaml"
echo "        path: '{{path}}/{{environment}}'" >> "$PROJECT_ROOT/argocd-apps/suoke-microservices-appset.yaml"
echo "      destination:" >> "$PROJECT_ROOT/argocd-apps/suoke-microservices-appset.yaml"
echo "        server: https://kubernetes.default.svc" >> "$PROJECT_ROOT/argocd-apps/suoke-microservices-appset.yaml"
echo "        namespace: suoke-{{environment}}" >> "$PROJECT_ROOT/argocd-apps/suoke-microservices-appset.yaml"
echo "      syncPolicy:" >> "$PROJECT_ROOT/argocd-apps/suoke-microservices-appset.yaml"
echo "        automated:" >> "$PROJECT_ROOT/argocd-apps/suoke-microservices-appset.yaml"
echo "          prune: true" >> "$PROJECT_ROOT/argocd-apps/suoke-microservices-appset.yaml"
echo "          selfHeal: true" >> "$PROJECT_ROOT/argocd-apps/suoke-microservices-appset.yaml"
echo "        syncOptions:" >> "$PROJECT_ROOT/argocd-apps/suoke-microservices-appset.yaml"
echo "        - CreateNamespace=true" >> "$PROJECT_ROOT/argocd-apps/suoke-microservices-appset.yaml"

print_success "已生成: argocd-apps/suoke-microservices-appset.yaml"

# 步骤4: 提交ArgoCD配置到Git仓库
print_header "提交ArgoCD配置到Git仓库"

cd "$PROJECT_ROOT"
git config --global user.name "ArgoCD Automation"
git config --global user.email "argocd@suoke.life"
git add argocd-apps/
git commit -m "自动生成ArgoCD应用定义 [ci skip]" || echo "没有变更需要提交"
git push || echo "没有变更需要推送"

print_success "ArgoCD配置已提交到Git仓库"

# 步骤5: 更新CI/CD工作流
print_header "更新CI/CD工作流"

for SERVICE in "${SERVICES[@]}"; do
  echo "更新 $SERVICE 的CI/CD工作流配置..."
  
  WORKFLOW_FILE="$PROJECT_ROOT/.github/workflows/$SERVICE-ci-cd.yml"
  
  if [ -f "$WORKFLOW_FILE" ]; then
    # 修改工作流使用ArgoCD模板
    sed -i 's|uses: ./.github/workflows/templates/service-ci-cd-template.yml|uses: ./.github/workflows/templates/service-ci-cd-template-with-argocd.yml|g' "$WORKFLOW_FILE"
    
    # 添加ArgoCD密钥
    if ! grep -q "ARGOCD_SERVER" "$WORKFLOW_FILE"; then
      sed -i '/KUBE_CONFIG_PROD:/a\      ARGOCD_SERVER: ${{ secrets.ARGOCD_SERVER }}\n      ARGOCD_USERNAME: ${{ secrets.ARGOCD_USERNAME }}\n      ARGOCD_PASSWORD: ${{ secrets.ARGOCD_PASSWORD }}' "$WORKFLOW_FILE"
    fi
    
    git add "$WORKFLOW_FILE"
    print_success "已更新: $WORKFLOW_FILE"
  else
    print_warning "工作流文件不存在: $WORKFLOW_FILE，跳过更新"
  fi
done

git commit -m "更新CI/CD工作流配置，集成ArgoCD [ci skip]" || echo "没有变更需要提交"
git push || echo "没有变更需要推送"

print_success "CI/CD工作流配置已更新"

# 步骤6: 部署ArgoCD应用
print_header "部署ArgoCD应用"

if [ -n "$ARGOCD_HOST" ]; then
  echo "正在部署ArgoCD应用到 $ARGOCD_HOST..."
  
  DEPLOY_CMD="$SCRIPT_DIR/setup_argocd_apps.sh $ARGOCD_HOST $ARGOCD_NAMESPACE"
  echo "执行命令: $DEPLOY_CMD"
  eval $DEPLOY_CMD
  
  if [ $? -ne 0 ]; then
    print_warning "ArgoCD应用部署可能失败，请手动检查"
  else
    print_success "ArgoCD应用部署完成"
  fi
else
  print_warning "未指定ArgoCD主机，跳过应用部署"
  echo "请手动运行以下命令部署ArgoCD应用:"
  echo "$SCRIPT_DIR/setup_argocd_apps.sh <ArgoCD主机> $ARGOCD_NAMESPACE"
fi

# 完成
print_header "迁移完成"
echo "已将 $SERVICE_COUNT 个微服务迁移到ArgoCD"
echo ""
echo "接下来的步骤:"
echo "1. 确保ArgoCD能够访问Git仓库"
echo "2. 在GitHub项目设置中添加以下Secrets:"
echo "   - ARGOCD_SERVER: ArgoCD服务器地址"
echo "   - ARGOCD_USERNAME: ArgoCD用户名"
echo "   - ARGOCD_PASSWORD: ArgoCD密码"
echo "3. 验证ArgoCD中的应用同步状态"
echo ""

if [ -n "$ARGOCD_HOST" ]; then
  echo "ArgoCD Web界面: https://$ARGOCD_HOST"
fi

echo ""
echo "所有微服务已自动迁移到ArgoCD并配置完成!" 