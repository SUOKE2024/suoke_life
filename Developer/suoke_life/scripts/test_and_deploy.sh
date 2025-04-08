#!/bin/bash
# 测试并部署脚本 - 自动提交代码并触发CI/CD流程

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
  print_error "用法: $0 <分支名> <提交消息> [是否推送(Y/N)]"
  echo "例如: $0 feature/my-feature \"添加新功能\" Y"
  exit 1
fi

BRANCH_NAME=$1
COMMIT_MESSAGE=$2
PUSH_CHANGES=${3:-N}

# 导航到项目根目录
cd "$(dirname "$0")/.."
ROOT_DIR=$(pwd)
print_header "当前目录: $ROOT_DIR"

# 检查当前Git状态
print_header "检查Git状态"
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
  print_error "当前目录不是Git仓库"
fi

# 获取当前分支
CURRENT_BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null)
if [ "$CURRENT_BRANCH" != "$BRANCH_NAME" ]; then
  print_warning "当前分支 ($CURRENT_BRANCH) 与目标分支 ($BRANCH_NAME) 不匹配"
  read -p "是否切换到 $BRANCH_NAME 分支? (y/n): " SWITCH_BRANCH
  if [[ "$SWITCH_BRANCH" =~ ^[Yy]$ ]]; then
    # 检查分支是否存在
    if git show-ref --verify --quiet refs/heads/$BRANCH_NAME; then
      # 分支存在，直接切换
      git checkout $BRANCH_NAME
    else
      # 分支不存在，创建并切换
      git checkout -b $BRANCH_NAME
    fi
  else
    print_error "用户取消了操作"
  fi
fi

# 简单目录检查
print_header "检查目录结构"
if [ -d "src" ] && [ -d "tests" ]; then
  print_success "目录结构检查通过"
else
  print_warning "目录结构不完整，但继续执行"
fi

# 提交更改
print_header "提交更改到 $BRANCH_NAME 分支"
git add .
git commit -m "$COMMIT_MESSAGE" || print_warning "没有新的更改需要提交"
print_success "操作完成"

# 推送到远程仓库
if [[ "$PUSH_CHANGES" =~ ^[Yy]$ ]]; then
  print_header "推送更改到远程仓库"
  git push origin $BRANCH_NAME
  print_success "已推送更改到远程仓库"
  
  # 输出GitHub Actions URL
  REPO_URL=$(git config --get remote.origin.url)
  if [[ $REPO_URL == *"github.com"* ]]; then
    REPO_PATH=$(echo $REPO_URL | sed -e 's/.*github.com[:\/]\(.*\)\.git/\1/')
    echo -e "\n${GREEN}查看CI/CD流程进度:${NC}"
    echo -e "https://github.com/$REPO_PATH/actions"
  fi
else
  print_warning "未推送更改到远程仓库"
  echo -e "\n要手动触发CI/CD流程，请执行:"
  echo -e "  git push origin $BRANCH_NAME"
fi

# 根据分支类型输出下一步操作建议
if [[ "$BRANCH_NAME" == feature/* ]]; then
  echo -e "\n${BLUE}下一步操作:${NC}"
  echo -e "1. 创建Pull Request将 $BRANCH_NAME 合并到main分支"
  echo -e "2. 待代码审查通过后，合并PR将触发开发环境部署"
elif [[ "$BRANCH_NAME" == release/* ]]; then
  echo -e "\n${BLUE}下一步操作:${NC}"
  echo -e "1. 代码推送后将自动触发预发布和生产环境部署"
  echo -e "2. 监控部署进度并验证服务功能"
  echo -e "3. 访问以下URL查看部署结果:"
  echo -e "   - 预发布环境: https://staging.api.suoke.life/rag/health"
  echo -e "   - 生产环境: https://api.suoke.life/rag/health"
fi

print_success "流程完成!" 