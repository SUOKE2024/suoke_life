#!/bin/bash

# 索克生活 - ArgoCD安装脚本
# 此脚本用于在Kubernetes集群中安装和配置ArgoCD

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
      *)
        echo "请查阅相关文档安装 $1"
        ;;
    esac
    exit 1
  fi
}

# 检查必要的命令
check_command kubectl

# 显示用法
print_header "ArgoCD安装工具"
echo "此脚本将在Kubernetes集群中安装和配置ArgoCD"
echo ""
echo "用法: $0 [选项]"
echo "选项:"
echo "  --namespace <命名空间>      安装ArgoCD的命名空间，默认为'argocd'"
echo "  --version <版本>           安装ArgoCD的版本，默认为'stable'"
echo "  --ingress-host <主机名>    Ingress主机名，例如'argocd.suoke.life'"
echo "  --ingress-class <类名>     Ingress类名，例如'nginx'"
echo "  --admin-password <密码>    管理员密码，默认为随机生成"
echo ""
echo "示例: $0 --namespace argocd --ingress-host argocd.suoke.life --ingress-class nginx"
echo ""

# 默认值
NAMESPACE="argocd"
VERSION="stable"
INGRESS_HOST=""
INGRESS_CLASS="nginx"
ADMIN_PASSWORD=$(openssl rand -base64 12)

# 解析参数
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --namespace)
      NAMESPACE="$2"
      shift
      shift
      ;;
    --version)
      VERSION="$2"
      shift
      shift
      ;;
    --ingress-host)
      INGRESS_HOST="$2"
      shift
      shift
      ;;
    --ingress-class)
      INGRESS_CLASS="$2"
      shift
      shift
      ;;
    --admin-password)
      ADMIN_PASSWORD="$2"
      shift
      shift
      ;;
    *)
      print_error "未知选项: $1"
      exit 1
      ;;
  esac
done

# 创建命名空间
print_header "创建ArgoCD命名空间 ${NAMESPACE}"
kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
print_success "命名空间创建成功或已存在"

# 安装ArgoCD
print_header "安装ArgoCD ${VERSION}"
echo "正在安装ArgoCD..."

# 根据版本选择安装清单
if [ "${VERSION}" == "stable" ]; then
  INSTALL_MANIFEST="https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml"
else
  INSTALL_MANIFEST="https://raw.githubusercontent.com/argoproj/argo-cd/v${VERSION}/manifests/install.yaml"
fi

kubectl apply -n ${NAMESPACE} -f ${INSTALL_MANIFEST}

if [ $? -ne 0 ]; then
  print_error "ArgoCD安装失败"
  exit 1
fi

print_success "ArgoCD安装成功"

# 等待ArgoCD组件准备就绪
print_header "等待ArgoCD组件准备就绪"
echo "这可能需要几分钟时间..."

kubectl wait --for=condition=available --timeout=600s deployment/argocd-server -n ${NAMESPACE}
kubectl wait --for=condition=available --timeout=600s deployment/argocd-repo-server -n ${NAMESPACE}
kubectl wait --for=condition=available --timeout=600s deployment/argocd-dex-server -n ${NAMESPACE}
kubectl wait --for=condition=available --timeout=600s deployment/argocd-redis -n ${NAMESPACE}

print_success "ArgoCD组件已准备就绪"

# 设置管理员密码
print_header "设置管理员密码"
echo "正在更新管理员密码..."

# 生成bcrypt哈希密码
BCRYPT_PASSWORD=$(htpasswd -bnBC 10 "" ${ADMIN_PASSWORD} | tr -d ':\n' | sed 's/$2y/$2a/')

# 创建密码修补配置
cat <<EOF > /tmp/argocd-secret-patch.yaml
stringData:
  admin.password: ${BCRYPT_PASSWORD}
  admin.passwordMtime: '$(date +%FT%T%Z)'
EOF

# 应用密码修补
kubectl patch secret argocd-secret -n ${NAMESPACE} --patch-file /tmp/argocd-secret-patch.yaml

if [ $? -ne 0 ]; then
  print_warning "管理员密码设置失败，将使用默认密码"
else
  print_success "管理员密码设置成功"
fi

# 删除临时文件
rm -f /tmp/argocd-secret-patch.yaml

# 配置Ingress（如果指定了主机名）
if [ -n "${INGRESS_HOST}" ]; then
  print_header "配置ArgoCD Ingress"
  echo "正在为 ${INGRESS_HOST} 创建Ingress..."

  # 创建Ingress配置
  cat <<EOF > /tmp/argocd-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: argocd-server-ingress
  namespace: ${NAMESPACE}
  annotations:
    kubernetes.io/ingress.class: ${INGRESS_CLASS}
    nginx.ingress.kubernetes.io/ssl-passthrough: "true"
    nginx.ingress.kubernetes.io/backend-protocol: "HTTPS"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - ${INGRESS_HOST}
    secretName: argocd-secret-tls
  rules:
  - host: ${INGRESS_HOST}
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: argocd-server
            port:
              number: 443
EOF

  kubectl apply -f /tmp/argocd-ingress.yaml

  if [ $? -ne 0 ]; then
    print_warning "Ingress配置失败，您可能需要手动配置"
  else
    print_success "Ingress配置成功"
  fi

  # 删除临时文件
  rm -f /tmp/argocd-ingress.yaml
fi

# 安装完成
print_header "ArgoCD安装完成"
echo "管理员用户: admin"
echo "管理员密码: ${ADMIN_PASSWORD}"
echo ""

if [ -n "${INGRESS_HOST}" ]; then
  echo "访问ArgoCD Web界面: https://${INGRESS_HOST}"
else
  echo "要访问ArgoCD Web界面，请运行以下命令："
  echo "kubectl port-forward svc/argocd-server -n ${NAMESPACE} 8080:443"
  echo "然后在浏览器中访问: https://localhost:8080"
fi

echo ""
echo "ArgoCD CLI登录命令："
if [ -n "${INGRESS_HOST}" ]; then
  echo "argocd login ${INGRESS_HOST} --username admin --password \"${ADMIN_PASSWORD}\" --insecure"
else
  echo "argocd login localhost:8080 --username admin --password \"${ADMIN_PASSWORD}\" --insecure"
fi

echo ""
echo "请确保将上述信息安全保存。"
echo "如需更多帮助，请参考ArgoCD文档: https://argo-cd.readthedocs.io/"> 