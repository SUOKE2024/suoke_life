#!/bin/bash

# Claude GitHub 应用安装脚本
# 用于快速配置 Claude AI 集成

set -e

echo "🤖 开始安装 Claude GitHub 应用..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目信息
PROJECT_NAME="索克生活平台"
REPO_OWNER="SUOKE2024"
REPO_NAME="suoke_life"

echo -e "${BLUE}项目: ${PROJECT_NAME}${NC}"
echo -e "${BLUE}仓库: ${REPO_OWNER}/${REPO_NAME}${NC}"
echo ""

# 检查必要工具
check_dependencies() {
    echo "🔍 检查依赖工具..."
    
    if ! command -v git &> /dev/null; then
        echo -e "${RED}错误: Git 未安装${NC}"
        exit 1
    fi
    
    if ! command -v curl &> /dev/null; then
        echo -e "${RED}错误: curl 未安装${NC}"
        exit 1
    fi
    
    if ! command -v jq &> /dev/null; then
        echo -e "${YELLOW}警告: jq 未安装，某些功能可能受限${NC}"
    fi
    
    echo -e "${GREEN}✅ 依赖检查完成${NC}"
}

# 检查 GitHub 仓库连接
check_github_connection() {
    echo "🔗 检查 GitHub 仓库连接..."
    
    if git remote get-url origin &> /dev/null; then
        REMOTE_URL=$(git remote get-url origin)
        echo -e "${GREEN}✅ 已连接到仓库: ${REMOTE_URL}${NC}"
    else
        echo -e "${RED}错误: 未找到 GitHub 远程仓库${NC}"
        exit 1
    fi
}

# 创建必要目录
create_directories() {
    echo "📁 创建必要目录..."
    
    mkdir -p .github/workflows
    mkdir -p docs/ai-generated/api
    mkdir -p docs/ai-generated/architecture
    mkdir -p reports/claude-review
    mkdir -p reports/security
    mkdir -p reports/performance
    mkdir -p reports/daily
    
    echo -e "${GREEN}✅ 目录创建完成${NC}"
}

# 检查配置文件
check_config_files() {
    echo "⚙️ 检查配置文件..."
    
    if [ ! -f ".claude.yml" ]; then
        echo -e "${YELLOW}警告: .claude.yml 配置文件不存在${NC}"
        echo "请运行以下命令创建配置文件："
        echo "cp .claude.yml.example .claude.yml"
    else
        echo -e "${GREEN}✅ Claude 配置文件存在${NC}"
    fi
    
    if [ ! -f ".github/workflows/claude-integration.yml" ]; then
        echo -e "${YELLOW}警告: Claude 集成工作流不存在${NC}"
    else
        echo -e "${GREEN}✅ Claude 工作流文件存在${NC}"
    fi
}

# 验证 GitHub Actions
validate_github_actions() {
    echo "🔧 验证 GitHub Actions 配置..."
    
    if [ -f ".github/workflows/claude-integration.yml" ]; then
        echo -e "${GREEN}✅ Claude 集成工作流已配置${NC}"
        
        # 检查工作流语法
        if command -v yamllint &> /dev/null; then
            if yamllint .github/workflows/claude-integration.yml &> /dev/null; then
                echo -e "${GREEN}✅ 工作流语法正确${NC}"
            else
                echo -e "${YELLOW}警告: 工作流语法可能有问题${NC}"
            fi
        fi
    fi
}

# 设置环境变量
setup_environment() {
    echo "🔐 设置环境变量..."
    
    if [ ! -f "claude.env" ]; then
        if [ -f "claude.env.example" ]; then
            cp claude.env.example claude.env
            echo -e "${YELLOW}已创建 claude.env 文件，请填入实际配置值${NC}"
        else
            echo -e "${RED}错误: 找不到环境变量示例文件${NC}"
        fi
    else
        echo -e "${GREEN}✅ 环境变量文件已存在${NC}"
    fi
}

# 显示安装指南
show_installation_guide() {
    echo ""
    echo -e "${BLUE}📋 Claude GitHub 应用安装指南${NC}"
    echo "=================================="
    echo ""
    echo "1. 访问 GitHub Marketplace:"
    echo "   https://github.com/marketplace"
    echo ""
    echo "2. 搜索 'Claude' 或 'Anthropic'"
    echo ""
    echo "3. 选择 Claude 官方应用并点击 'Install'"
    echo ""
    echo "4. 选择安装范围:"
    echo "   - 选择 'Only select repositories'"
    echo "   - 选择 '${REPO_OWNER}/${REPO_NAME}'"
    echo ""
    echo "5. 配置权限:"
    echo "   ✅ Read access to code"
    echo "   ✅ Read and write access to pull requests"
    echo "   ✅ Read and write access to issues"
    echo "   ✅ Read access to repository metadata"
    echo ""
    echo "6. 设置 API 密钥:"
    echo "   - 转到仓库 Settings → Secrets and variables → Actions"
    echo "   - 添加以下密钥:"
    echo "     * CLAUDE_API_KEY"
    echo "     * ANTHROPIC_API_KEY"
    echo ""
    echo "7. 验证安装:"
    echo "   - 创建一个测试 Pull Request"
    echo "   - 检查 Claude 是否自动进行代码审查"
    echo ""
}

# 显示后续步骤
show_next_steps() {
    echo ""
    echo -e "${GREEN}🎉 Claude 应用配置准备完成！${NC}"
    echo ""
    echo -e "${BLUE}📋 后续步骤:${NC}"
    echo "1. 按照上述指南在 GitHub 中安装 Claude 应用"
    echo "2. 配置 API 密钥和环境变量"
    echo "3. 编辑 claude.env 文件，填入实际配置值"
    echo "4. 提交配置文件到仓库:"
    echo "   git add ."
    echo "   git commit -m '🤖 添加 Claude AI 集成配置'"
    echo "   git push"
    echo "5. 创建测试 PR 验证 Claude 集成"
    echo ""
    echo -e "${YELLOW}📚 相关文档:${NC}"
    echo "- 安装指南: .github/CLAUDE_INSTALLATION_GUIDE.md"
    echo "- 配置文件: .claude.yml"
    echo "- 工作流: .github/workflows/claude-integration.yml"
    echo ""
    echo -e "${GREEN}🚀 开始享受 Claude AI 的智能协助吧！${NC}"
}

# 主函数
main() {
    echo -e "${GREEN}🤖 Claude GitHub 应用安装脚本${NC}"
    echo "=================================="
    echo ""
    
    check_dependencies
    check_github_connection
    create_directories
    check_config_files
    validate_github_actions
    setup_environment
    show_installation_guide
    show_next_steps
}

# 运行主函数
main "$@" 