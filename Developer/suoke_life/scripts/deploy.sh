#!/bin/bash
# 索克生活微服务部署脚本
# 用法: ./scripts/deploy.sh <服务名称> <环境> [版本号]
# 例如: ./scripts/deploy.sh rag-service dev 1.2.0

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
if [ "$#" -lt 2 ]; then
  print_error "用法: $0 <服务名称> <环境> [版本号]
  可用服务: rag-service, auth-service, user-service, api-gateway, knowledge-graph-service 等
  可用环境: dev, staging, prod
  例如: $0 rag-service dev 1.2.0"
fi

SERVICE_NAME=$1
ENVIRONMENT=$2
VERSION=${3:-""}

# 验证环境参数
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
  print_error "无效的环境: $ENVIRONMENT, 必须是dev、staging或prod之一"
fi

# 验证服务是否存在
if [ ! -d "services/$SERVICE_NAME" ]; then
  print_error "服务不存在: $SERVICE_NAME"
fi

print_header "正在部署 $SERVICE_NAME 到 $ENVIRONMENT 环境"

# 获取GitHub令牌
if [ -z "$GITHUB_TOKEN" ]; then
  # 尝试从环境文件加载
  if [ -f ".env" ]; then
    source .env
  fi
  
  # 如果仍然为空，则询问用户
  if [ -z "$GITHUB_TOKEN" ]; then
    read -p "请输入GitHub令牌: " GITHUB_TOKEN
    echo "GITHUB_TOKEN=$GITHUB_TOKEN" >> .env
  fi
fi

if [ -z "$GITHUB_TOKEN" ]; then
  print_error "缺少GitHub令牌"
fi

# 获取仓库信息
REPO_URL=$(git config --get remote.origin.url)
REPO_OWNER=$(echo $REPO_URL | sed -e 's/.*github.com[:\/]\([^\/]*\).*/\1/')
REPO_NAME=$(basename -s .git $(git config --get remote.origin.url))

print_header "准备触发GitHub Actions工作流"
echo "服务: $SERVICE_NAME"
echo "环境: $ENVIRONMENT"
echo "仓库: $REPO_OWNER/$REPO_NAME"

if [ -n "$VERSION" ]; then
  echo "版本: $VERSION"
  VERSION_PARAM="\"version\":\"$VERSION\","
else
  VERSION_PARAM=""
  echo "版本: 使用默认版本"
fi

# 使用GitHub API触发工作流
WORKFLOW_FILE="$SERVICE_NAME-ci-cd.yml"

curl -s -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  -d "{\"ref\":\"main\",\"inputs\":{\"environment\":\"$ENVIRONMENT\",$VERSION_PARAM}}" \
  "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/actions/workflows/$WORKFLOW_FILE/dispatches"

if [ $? -eq 0 ]; then
  print_success "已成功触发部署工作流"
  echo -e "\n查看工作流状态: https://github.com/$REPO_OWNER/$REPO_NAME/actions"
else
  print_error "触发工作流失败"
fi

# 查看进度
print_header "监控部署进度"
echo "正在查询最近的工作流运行..."

# 延迟几秒钟，确保工作流已启动
sleep 5

# 使用GitHub API获取最近的工作流运行
WORKFLOW_RUNS=$(curl -s -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/actions/workflows/$WORKFLOW_FILE/runs?per_page=1")

RUN_ID=$(echo $WORKFLOW_RUNS | jq -r '.workflow_runs[0].id')
RUN_URL=$(echo $WORKFLOW_RUNS | jq -r '.workflow_runs[0].html_url')

if [ -n "$RUN_ID" ] && [ "$RUN_ID" != "null" ]; then
  print_success "部署工作流已启动"
  echo "工作流ID: $RUN_ID"
  echo "工作流URL: $RUN_URL"
  
  # 询问是否在浏览器中打开工作流
  read -p "是否在浏览器中打开工作流页面? (y/n): " OPEN_BROWSER
  if [[ "$OPEN_BROWSER" =~ ^[Yy]$ ]]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
      open "$RUN_URL"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
      xdg-open "$RUN_URL"
    else
      echo "无法自动打开浏览器，请手动访问: $RUN_URL"
    fi
  fi
else
  print_warning "未找到相关工作流运行，请手动检查GitHub Actions页面"
  echo "GitHub Actions页面: https://github.com/$REPO_OWNER/$REPO_NAME/actions"
fi

print_success "部署脚本执行完成!" 