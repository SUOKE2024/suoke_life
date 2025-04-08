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
WORKFLOW_NAME="rag-service-ci-cd"
BRANCH="main"
ENVIRONMENT="prod"
VERSION="auto"
SKIP_TESTS="false"
MULTI_ARCH="true"

# 解析命令行参数
while [[ $# -gt 0 ]]; do
  case $1 in
    --branch|-b)
      BRANCH="$2"
      shift 2
      ;;
    --env|-e)
      ENVIRONMENT="$2"
      shift 2
      ;;
    --version|-v)
      VERSION="$2"
      shift 2
      ;;
    --skip-tests|-s)
      SKIP_TESTS="true"
      shift
      ;;
    --single-arch|-a)
      MULTI_ARCH="false"
      shift
      ;;
    --help|-h)
      echo "用法: $0 [选项]"
      echo "选项:"
      echo "  --branch, -b <分支名>     指定分支名称 (默认: main)"
      echo "  --env, -e <环境名>        指定部署环境 (默认: prod)"
      echo "  --version, -v <版本标签>  指定版本标签 (默认: auto)"
      echo "  --skip-tests, -s          跳过测试 (默认: false)"
      echo "  --single-arch, -a         只构建单架构镜像 (默认: 构建多架构镜像)"
      echo "  --help, -h                显示帮助信息"
      exit 0
      ;;
    *)
      error "未知选项: $1"
      exit 1
      ;;
  esac
done

# 检查环境
if ! command -v gh &> /dev/null; then
  error "请先安装 GitHub CLI (gh)"
  exit 1
fi

# 检查 gh 是否登录
if ! gh auth status &> /dev/null; then
  error "请先登录 GitHub CLI: gh auth login"
  exit 1
fi

# 验证输入
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
  error "环境必须是 dev, staging 或 prod"
  exit 1
fi

# 显示配置信息
info "--------------------------------"
info "RAG服务部署配置"
info "--------------------------------"
info "工作流名称: $WORKFLOW_NAME"
info "部署分支: $BRANCH"
info "目标环境: $ENVIRONMENT"
info "版本标签: $VERSION"
info "跳过测试: $SKIP_TESTS"
info "构建多架构: $MULTI_ARCH"
info "--------------------------------"

# 确认部署
read -p "是否确认上述配置并开始部署？(y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  warn "部署已取消"
  exit 0
fi

# 执行部署
info "开始触发部署流程..."

# 获取项目根目录路径
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# 使用GitHub CLI触发工作流
gh workflow run "$WORKFLOW_NAME" --ref "$BRANCH" \
  --field environment="$ENVIRONMENT" \
  --field version="$VERSION" \
  --field skip_tests="$SKIP_TESTS" \
  --field multi_arch="$MULTI_ARCH"

if [ $? -eq 0 ]; then
  success "部署流程已触发，请在GitHub Actions页面查看进度"
  REPO_URL=$(git config --get remote.origin.url | sed 's/\.git$//' | sed 's|git@github.com:|https://github.com/|')
  echo -e "${GREEN}查看部署进度:${NC} $REPO_URL/actions/workflows/$WORKFLOW_NAME.yml"
else
  error "部署流程触发失败，请检查错误信息"
  exit 1
fi

# 显示部署后注意事项
info "部署状态将通过Webhook发送通知"
info "部署完成后，请验证服务是否正常运行"
info "您可以通过以下命令查看服务状态:"
echo "  kubectl get pods -n suoke-$ENVIRONMENT | grep rag-service"
echo "  kubectl logs -f -l app=rag-service -n suoke-$ENVIRONMENT"
echo
success "脚本执行完毕!" 