#!/bin/bash

# GitHub 仓库访问权限设置脚本
# 用于快速设置仓库为邀请制访问

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_header() {
    echo ""
    print_message $BLUE "=================================="
    print_message $BLUE "  GitHub 仓库访问权限设置工具"
    print_message $BLUE "=================================="
    echo ""
}

print_step() {
    local step=$1
    local message=$2
    print_message $YELLOW "步骤 ${step}: ${message}"
}

print_success() {
    print_message $GREEN "✅ $1"
}

print_error() {
    print_message $RED "❌ $1"
}

print_warning() {
    print_message $YELLOW "⚠️  $1"
}

# 检查依赖
check_dependencies() {
    print_step 1 "检查依赖环境"
    
    # 检查 Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js 未安装，请先安装 Node.js"
        exit 1
    fi
    print_success "Node.js 已安装: $(node --version)"
    
    # 检查 npm
    if ! command -v npm &> /dev/null; then
        print_error "npm 未安装，请先安装 npm"
        exit 1
    fi
    print_success "npm 已安装: $(npm --version)"
    
    # 检查 curl
    if ! command -v curl &> /dev/null; then
        print_error "curl 未安装，请先安装 curl"
        exit 1
    fi
    print_success "curl 已安装"
}

# 安装必要的依赖
install_dependencies() {
    print_step 2 "安装 GitHub API 依赖"
    
    if npm list @octokit/rest &> /dev/null; then
        print_success "@octokit/rest 已安装"
    else
        print_message $BLUE "正在安装 @octokit/rest..."
        npm install @octokit/rest
        print_success "@octokit/rest 安装完成"
    fi
}

# 检查 GitHub Token
check_github_token() {
    print_step 3 "检查 GitHub Personal Access Token"
    
    if [ -z "$GITHUB_TOKEN" ]; then
        print_warning "未设置 GITHUB_TOKEN 环境变量"
        echo ""
        print_message $BLUE "请按照以下步骤创建 Personal Access Token："
        echo "1. 访问 https://github.com/settings/tokens"
        echo "2. 点击 'Generate new token (classic)'"
        echo "3. 选择以下权限："
        echo "   - repo (完整的仓库访问权限)"
        echo "   - admin:org (组织管理权限，如果是组织仓库)"
        echo "4. 生成并复制 Token"
        echo ""
        read -p "请输入您的 GitHub Token: " token
        export GITHUB_TOKEN=$token
        
        # 验证 Token
        if curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user > /dev/null; then
            print_success "GitHub Token 验证成功"
        else
            print_error "GitHub Token 验证失败，请检查 Token 是否正确"
            exit 1
        fi
    else
        print_success "GITHUB_TOKEN 环境变量已设置"
    fi
}

# 显示仓库信息
show_repository_info() {
    print_step 4 "显示仓库信息"
    
    echo ""
    print_message $BLUE "将要修改的仓库："
    echo "- SUOKE2024/suoke_life"
    echo ""
    
    read -p "确认要将这些仓库设置为私有吗？(y/N): " confirm
    if [[ $confirm != [yY] ]]; then
        print_message $YELLOW "操作已取消"
        exit 0
    fi
}

# 运行脚本
run_update_script() {
    print_step 5 "执行仓库权限修改"
    
    echo ""
    print_message $BLUE "正在运行仓库权限修改脚本..."
    
    # 设置环境变量并运行脚本
    GITHUB_TOKEN=$GITHUB_TOKEN node scripts/update-repo-visibility.js
    
    if [ $? -eq 0 ]; then
        print_success "仓库权限修改完成"
    else
        print_error "仓库权限修改失败"
        exit 1
    fi
}

# 显示后续步骤
show_next_steps() {
    echo ""
    print_message $GREEN "🎉 设置完成！"
    echo ""
    print_message $BLUE "后续步骤："
    echo "1. 被邀请的用户需要接受邀请才能访问仓库"
    echo "2. 您可以在 GitHub 仓库设置中管理协作者权限"
    echo "3. 私有仓库的 CI/CD 可能需要重新配置访问权限"
    echo "4. 查看详细文档: docs/GITHUB_REPOSITORY_ACCESS_GUIDE.md"
    echo ""
    print_message $BLUE "相关命令："
    echo "- npm run github:update-visibility  # 重新运行权限修改脚本"
    echo "- npm run github:setup              # 重新安装依赖"
    echo ""
}

# 主函数
main() {
    print_header
    
    # 检查是否在项目根目录
    if [ ! -f "package.json" ]; then
        print_error "请在项目根目录运行此脚本"
        exit 1
    fi
    
    check_dependencies
    install_dependencies
    check_github_token
    show_repository_info
    run_update_script
    show_next_steps
}

# 错误处理
trap 'print_error "脚本执行过程中发生错误"; exit 1' ERR

# 运行主函数
main "$@" 