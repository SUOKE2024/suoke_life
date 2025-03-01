#!/bin/bash

# backup_to_github.sh - 将项目代码备份到GitHub仓库
#
# 此脚本用于将当前的项目代码备份到GitHub仓库

set -e  # 遇到错误立即退出

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 备份目标仓库
BACKUP_REPO="git@github.com:SUOKE2024/suoke_life.git"
BACKUP_DIR="/Users/songxu/Developer/suoke_life_new"
CURRENT_DIR="$(pwd)"

# 获取当前日期和时间
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
COMMIT_MESSAGE="备份变更 - $TIMESTAMP"

# 显示帮助信息
show_help() {
  echo -e "${BLUE}索克生活 GitHub备份脚本${NC}"
  echo -e "${YELLOW}使用方法:${NC}"
  echo -e "  ./scripts/backup_to_github.sh [选项]"
  echo
  echo -e "${YELLOW}选项:${NC}"
  echo -e "  -h, --help         显示帮助信息"
  echo -e "  -m, --message      指定提交信息"
  echo -e "  -b, --branch       指定目标分支（默认：main）"
  echo
  echo -e "${YELLOW}示例:${NC}"
  echo -e "  ./scripts/backup_to_github.sh --message \"修复登录功能\" --branch dev"
}

# 解析命令行参数
BRANCH="main"
while [[ $# -gt 0 ]]; do
  case $1 in
    -h|--help)
      show_help
      exit 0
      ;;
    -m|--message)
      COMMIT_MESSAGE="$2"
      shift 2
      ;;
    -b|--branch)
      BRANCH="$2"
      shift 2
      ;;
    *)
      echo -e "${RED}未知选项: $1${NC}"
      show_help
      exit 1
      ;;
  esac
done

# 备份当前的工作目录
backup_project() {
  echo -e "${YELLOW}准备备份项目到GitHub...${NC}"
  
  # 确认备份目录存在
  if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${YELLOW}备份目录不存在，正在克隆仓库...${NC}"
    git clone "$BACKUP_REPO" "$BACKUP_DIR"
  fi
  
  # 切换到备份目录
  cd "$BACKUP_DIR"
  
  # 确保我们在正确的分支上
  git fetch origin
  git checkout "$BRANCH" || git checkout -b "$BRANCH"
  git pull origin "$BRANCH" || true
  
  echo -e "${YELLOW}正在同步文件...${NC}"

  # 要同步的目录列表
  DIRS_TO_SYNC=(
    "lib"
    "assets"
    "test"
    "scripts"
    "android"
    "ios"
    "web"
    "macos"
    "linux"
    "windows"
    "integration_test"
    ".github"
  )
  
  # 要同步的文件列表
  FILES_TO_SYNC=(
    "pubspec.yaml"
    "pubspec.lock"
    "analysis_options.yaml"
    "README.md"
    ".gitignore"
    ".cursorrules"
    "l10n.yaml"
  )
  
  # 同步目录
  for dir in "${DIRS_TO_SYNC[@]}"; do
    if [ -d "$CURRENT_DIR/$dir" ]; then
      echo -e "${YELLOW}同步目录: $dir${NC}"
      mkdir -p "$BACKUP_DIR/$dir"
      rsync -av --delete "$CURRENT_DIR/$dir/" "$BACKUP_DIR/$dir/"
    fi
  done
  
  # 同步文件
  for file in "${FILES_TO_SYNC[@]}"; do
    if [ -f "$CURRENT_DIR/$file" ]; then
      echo -e "${YELLOW}同步文件: $file${NC}"
      cp -f "$CURRENT_DIR/$file" "$BACKUP_DIR/$file"
    fi
  done
  
  # 添加修改到Git
  git add .
  
  # 检查是否有变更需要提交
  if git diff --staged --quiet; then
    echo -e "${YELLOW}没有变更需要提交${NC}"
  else
    echo -e "${YELLOW}提交变更: $COMMIT_MESSAGE${NC}"
    git commit -m "$COMMIT_MESSAGE"
    
    echo -e "${YELLOW}推送到GitHub...${NC}"
    git push origin "$BRANCH"
    
    echo -e "${GREEN}备份成功!${NC}"
  fi
  
  # 返回原始目录
  cd "$CURRENT_DIR"
}

# 主函数
main() {
  echo -e "${BLUE}=============================================${NC}"
  echo -e "${BLUE}          索克生活 GitHub备份工具          ${NC}"
  echo -e "${BLUE}=============================================${NC}"
  
  backup_project
  
  echo -e "${BLUE}=============================================${NC}"
  echo -e "${GREEN}          备份操作完成          ${NC}"
  echo -e "${BLUE}=============================================${NC}"
  echo -e "${GREEN}备份仓库位置: $BACKUP_DIR${NC}"
  echo -e "${GREEN}远程仓库: $BACKUP_REPO${NC}"
  echo -e "${GREEN}分支: $BRANCH${NC}"
}

# 执行主函数
main 