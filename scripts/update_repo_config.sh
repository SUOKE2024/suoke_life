#!/bin/bash

# update_repo_config.sh - 更新仓库配置脚本
#
# 此脚本用于设置正确的Git仓库配置，以便与SUOKE2024组织的仓库集成

set -e  # 遇到错误立即退出

echo "配置SUOKE生活APP仓库..."

# 设置Git仓库URL
GIT_REPO="git@github.com:SUOKE2024/suoke_life.git"

# 检查Git配置
setup_git_config() {
  echo "设置Git配置..."
  
  # 配置用户信息
  git config --global user.name "SUOKE CI"
  git config --global user.email "ci@suoke.life"
  
  # 配置SSH密钥设置（如果存在CI密钥）
  if [ -f "$HOME/.ssh/suoke_ci_key" ]; then
    echo "配置SSH密钥..."
    eval "$(ssh-agent -s)"
    ssh-add "$HOME/.ssh/suoke_ci_key"
  fi
  
  # 检查远程仓库配置
  if git remote | grep -q "origin"; then
    echo "更新远程仓库URL..."
    git remote set-url origin "$GIT_REPO"
  else
    echo "添加远程仓库..."
    git remote add origin "$GIT_REPO"
  fi
  
  echo "Git配置完成。"
}

# 为CI/CD环境设置Git Credentials
setup_git_credentials() {
  if [ -n "$GIT_USER" ] && [ -n "$GIT_TOKEN" ]; then
    echo "配置Git凭据..."
    echo "https://$GIT_USER:$GIT_TOKEN@github.com" > ~/.git-credentials
    git config --global credential.helper store
    echo "Git凭据配置完成。"
  else
    echo "警告: 未设置GIT_USER或GIT_TOKEN环境变量，跳过凭据配置。"
  fi
}

# 测试连接
test_connection() {
  echo "测试与仓库的连接..."
  if git ls-remote "$GIT_REPO" &> /dev/null; then
    echo "连接成功！"
  else
    echo "错误: 无法连接到仓库。请检查权限和网络连接。"
    exit 1
  fi
}

# 主函数
main() {
  echo "开始更新仓库配置..."
  
  setup_git_config
  setup_git_credentials
  test_connection
  
  echo "仓库配置更新完成！"
}

# 执行主函数
main 