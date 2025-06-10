#!/bin/bash

# CI/CD状态检查脚本
# 验证所有CI/CD组件是否正确配置

set -e

echo "🔍 索克生活 CI/CD 状态检查"
echo "================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查函数
check_file() {
    local file=$1
    local description=$2
    
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $description: $file"
        return 0
    else
        echo -e "${RED}✗${NC} $description: $file (缺失)"
        return 1
    fi
}

check_directory() {
    local dir=$1
    local description=$2
    
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} $description: $dir"
        return 0
    else
        echo -e "${RED}✗${NC} $description: $dir (缺失)"
        return 1
    fi
}

check_script_executable() {
    local script=$1
    local description=$2
    
    if [ -x "$script" ]; then
        echo -e "${GREEN}✓${NC} $description: $script (可执行)"
        return 0
    else
        echo -e "${RED}✗${NC} $description: $script (不可执行)"
        return 1
    fi
}

# 检查计数器
total_checks=0
passed_checks=0

echo -e "\n${BLUE}1. GitHub Actions 工作流检查${NC}"
echo "--------------------------------"
((total_checks++))
if check_file ".github/workflows/main-ci-cd.yml" "主要CI/CD工作流"; then
    ((passed_checks++))
fi

echo -e "\n${BLUE}2. Kubernetes 配置检查${NC}"
echo "--------------------------------"
((total_checks++))
if check_directory "k8s/staging" "测试环境配置"; then
    ((passed_checks++))
fi

((total_checks++))
if check_file "k8s/staging/configmap.yaml" "ConfigMap配置"; then
    ((passed_checks++))
fi

((total_checks++))
if check_file "k8s/staging/secrets.yaml" "Secrets配置"; then
    ((passed_checks++))
fi

((total_checks++))
if check_file "k8s/staging/api-gateway-deployment.yaml" "API网关部署配置"; then
    ((passed_checks++))
fi

echo -e "\n${BLUE}3. 性能测试配置检查${NC}"
echo "--------------------------------"
((total_checks++))
if check_file "tests/performance/load-test.js" "K6性能测试脚本"; then
    ((passed_checks++))
fi

echo -e "\n${BLUE}4. 部署脚本检查${NC}"
echo "--------------------------------"
((total_checks++))
if check_script_executable "scripts/ci-cd/deploy.sh" "部署脚本"; then
    ((passed_checks++))
fi

((total_checks++))
if check_script_executable "scripts/ci-cd/build-images.sh" "镜像构建脚本"; then
    ((passed_checks++))
fi

echo -e "\n${BLUE}5. 文档检查${NC}"
echo "--------------------------------"
((total_checks++))
if check_file "docs/ci-cd/CI_CD_COMPLETE_GUIDE.md" "CI/CD完整指南"; then
    ((passed_checks++))
fi

((total_checks++))
if check_file "CI_CD_DEPLOYMENT_SUMMARY.md" "部署总结报告"; then
    ((passed_checks++))
fi

echo -e "\n${BLUE}6. package.json 脚本检查${NC}"
echo "--------------------------------"
if [ -f "package.json" ]; then
    echo -e "${GREEN}✓${NC} package.json 存在"
    
    # 检查CI/CD相关脚本
    scripts=("ci:prepare" "ci:test" "ci:build" "ci:deploy" "ci:security" "security:scan" "build:images" "deploy:staging" "deploy:production" "performance:test")
    
    for script in "${scripts[@]}"; do
        ((total_checks++))
        if grep -q "\"$script\":" package.json; then
            echo -e "${GREEN}✓${NC} npm脚本: $script"
            ((passed_checks++))
        else
            echo -e "${RED}✗${NC} npm脚本: $script (缺失)"
        fi
    done
else
    echo -e "${RED}✗${NC} package.json 不存在"
fi

echo -e "\n${BLUE}7. Git 状态检查${NC}"
echo "--------------------------------"
# 检查是否有未提交的更改
if git diff --quiet && git diff --staged --quiet; then
    echo -e "${GREEN}✓${NC} Git工作区干净"
    ((passed_checks++))
else
    echo -e "${YELLOW}⚠${NC} Git工作区有未提交的更改"
fi
((total_checks++))

# 检查远程仓库
if git remote -v | grep -q "origin"; then
    echo -e "${GREEN}✓${NC} Git远程仓库已配置"
    ((passed_checks++))
else
    echo -e "${RED}✗${NC} Git远程仓库未配置"
fi
((total_checks++))

echo -e "\n${BLUE}8. 环境依赖检查${NC}"
echo "--------------------------------"
# 检查Node.js
if command -v node >/dev/null 2>&1; then
    node_version=$(node --version)
    echo -e "${GREEN}✓${NC} Node.js: $node_version"
    ((passed_checks++))
else
    echo -e "${RED}✗${NC} Node.js 未安装"
fi
((total_checks++))

# 检查npm
if command -v npm >/dev/null 2>&1; then
    npm_version=$(npm --version)
    echo -e "${GREEN}✓${NC} npm: $npm_version"
    ((passed_checks++))
else
    echo -e "${RED}✗${NC} npm 未安装"
fi
((total_checks++))

# 检查Docker (可选)
if command -v docker >/dev/null 2>&1; then
    docker_version=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
    echo -e "${GREEN}✓${NC} Docker: $docker_version"
    ((passed_checks++))
else
    echo -e "${YELLOW}⚠${NC} Docker 未安装 (CI/CD环境中会自动安装)"
fi
((total_checks++))

# 检查kubectl (可选)
if command -v kubectl >/dev/null 2>&1; then
    kubectl_version=$(kubectl version --client --short 2>/dev/null | cut -d' ' -f3)
    echo -e "${GREEN}✓${NC} kubectl: $kubectl_version"
    ((passed_checks++))
else
    echo -e "${YELLOW}⚠${NC} kubectl 未安装 (CI/CD环境中会自动安装)"
fi
((total_checks++))

echo -e "\n${BLUE}9. 项目结构检查${NC}"
echo "--------------------------------"
key_dirs=("src" "services" "k8s" "scripts/ci-cd" "tests" "docs")

for dir in "${key_dirs[@]}"; do
    ((total_checks++))
    if check_directory "$dir" "关键目录"; then
        ((passed_checks++))
    fi
done

# 总结
echo -e "\n${BLUE}================================${NC}"
echo -e "${BLUE}CI/CD 状态检查总结${NC}"
echo -e "${BLUE}================================${NC}"

percentage=$((passed_checks * 100 / total_checks))

if [ $percentage -ge 90 ]; then
    status_color=$GREEN
    status_icon="🎉"
    status_text="优秀"
elif [ $percentage -ge 80 ]; then
    status_color=$YELLOW
    status_icon="⚠️"
    status_text="良好"
else
    status_color=$RED
    status_icon="❌"
    status_text="需要改进"
fi

echo -e "${status_color}${status_icon} 总体状态: $status_text${NC}"
echo -e "通过检查: ${GREEN}$passed_checks${NC}/$total_checks"
echo -e "完成度: ${status_color}$percentage%${NC}"

if [ $percentage -ge 80 ]; then
    echo -e "\n${GREEN}✅ CI/CD流程已准备就绪！${NC}"
    echo -e "可以通过以下方式触发CI/CD:"
    echo -e "  • 推送到main分支: ${BLUE}git push origin main${NC}"
    echo -e "  • 推送到develop分支: ${BLUE}git push origin develop${NC}"
    echo -e "  • 创建Pull Request到main分支"
    echo -e "  • 手动触发GitHub Actions工作流"
else
    echo -e "\n${RED}❌ CI/CD流程需要完善${NC}"
    echo -e "请检查上述失败项目并修复"
fi

echo -e "\n${BLUE}快速命令:${NC}"
echo -e "  • 本地测试: ${BLUE}npm run ci:prepare${NC}"
echo -e "  • 安全扫描: ${BLUE}npm run security:scan${NC}"
echo -e "  • 构建镜像: ${BLUE}npm run build:images${NC}"
echo -e "  • 部署测试环境: ${BLUE}npm run deploy:staging${NC}"

exit $((total_checks - passed_checks)) 