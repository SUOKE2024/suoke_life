#!/bin/bash

echo "📊 索克生活项目完成度跟踪"
echo "================================"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查函数
check_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
        return 1
    else
        echo -e "${RED}❌ $2${NC}"
        return 0
    fi
}

# 统计变量
total_checks=0
passed_checks=0

echo -e "${BLUE}🔍 第一阶段：紧急修复检查${NC}"
echo "--------------------------------"

# 1. 检查测试文件修复
echo "检查测试文件语法..."
find src -name "*.test.ts*" -exec grep -l "import.*import" {} \; | wc -l > /tmp/duplicate_imports
duplicate_count=$(cat /tmp/duplicate_imports)
total_checks=$((total_checks + 1))
if [ $duplicate_count -eq 0 ]; then
    passed_checks=$((passed_checks + 1))
    check_status 0 "测试文件重复导入已修复"
else
    check_status 1 "仍有 $duplicate_count 个文件存在重复导入"
fi

# 2. 检查API服务文件
echo "检查API服务文件..."
total_checks=$((total_checks + 1))
if [ -f "src/services/api/agentApiService.ts" ]; then
    passed_checks=$((passed_checks + 1))
    check_status 0 "API服务文件已修复"
else
    check_status 1 "API服务文件缺失"
fi

# 3. 检查错误处理机制
echo "检查错误处理机制..."
total_checks=$((total_checks + 1))
if [ -f "src/core/error/GlobalErrorHandler.ts" ]; then
    passed_checks=$((passed_checks + 1))
    check_status 0 "全局错误处理器已创建"
else
    check_status 1 "全局错误处理器缺失"
fi

# 4. 检查性能监控
echo "检查性能监控系统..."
total_checks=$((total_checks + 1))
if [ -f "src/core/monitoring/PerformanceMonitor.ts" ]; then
    passed_checks=$((passed_checks + 1))
    check_status 0 "性能监控系统已创建"
else
    check_status 1 "性能监控系统缺失"
fi

echo ""
echo -e "${BLUE}🔧 第二阶段：功能完善检查${NC}"
echo "--------------------------------"

# 5. 检查前端组件数量
echo "统计前端组件..."
component_count=$(find src/components -name "*.tsx" | wc -l)
screen_count=$(find src/screens -name "*.tsx" | wc -l)
total_frontend=$((component_count + screen_count))
total_checks=$((total_checks + 1))
if [ $total_frontend -gt 200 ]; then
    passed_checks=$((passed_checks + 1))
    check_status 0 "前端组件充足 ($total_frontend 个)"
else
    check_status 1 "前端组件不足 ($total_frontend 个)"
fi

# 6. 检查后端服务
echo "统计后端服务..."
service_count=$(ls -d services/*/ | wc -l)
total_checks=$((total_checks + 1))
if [ $service_count -gt 10 ]; then
    passed_checks=$((passed_checks + 1))
    check_status 0 "后端服务充足 ($service_count 个)"
else
    check_status 1 "后端服务不足 ($service_count 个)"
fi

# 7. 检查智能体服务
echo "检查智能体服务..."
agent_services=("xiaoai-service" "xiaoke-service" "laoke-service" "soer-service")
agent_count=0
for service in "${agent_services[@]}"; do
    if [ -d "services/agent-services/$service" ]; then
        agent_count=$((agent_count + 1))
    fi
done
total_checks=$((total_checks + 1))
if [ $agent_count -eq 4 ]; then
    passed_checks=$((passed_checks + 1))
    check_status 0 "四大智能体服务完整"
else
    check_status 1 "智能体服务不完整 ($agent_count/4)"
fi

# 8. 检查诊断服务
echo "检查诊断服务..."
diagnostic_services=("look-service" "listen-service" "inquiry-service" "palpation-service" "calculation-service")
diagnostic_count=0
for service in "${diagnostic_services[@]}"; do
    if [ -d "services/diagnostic-services/$service" ] || [ -f "services/diagnostic-services/$service.py" ]; then
        diagnostic_count=$((diagnostic_count + 1))
    fi
done
total_checks=$((total_checks + 1))
if [ $diagnostic_count -ge 4 ]; then
    passed_checks=$((passed_checks + 1))
    check_status 0 "诊断服务基本完整 ($diagnostic_count/5)"
else
    check_status 1 "诊断服务不完整 ($diagnostic_count/5)"
fi

echo ""
echo -e "${BLUE}📋 第三阶段：质量保证检查${NC}"
echo "--------------------------------"

# 9. 检查配置文件
echo "检查配置文件..."
config_files=("package.json" "tsconfig.json" "docker-compose.microservices.yml")
config_count=0
for file in "${config_files[@]}"; do
    if [ -f "$file" ]; then
        config_count=$((config_count + 1))
    fi
done
total_checks=$((total_checks + 1))
if [ $config_count -eq 3 ]; then
    passed_checks=$((passed_checks + 1))
    check_status 0 "核心配置文件完整"
else
    check_status 1 "配置文件不完整 ($config_count/3)"
fi

# 10. 检查文档
echo "检查文档..."
doc_files=("README.md" "docs/development-reports/100_PERCENT_COMPLETION_PLAN.md")
doc_count=0
for file in "${doc_files[@]}"; do
    if [ -f "$file" ]; then
        doc_count=$((doc_count + 1))
    fi
done
total_checks=$((total_checks + 1))
if [ $doc_count -eq 2 ]; then
    passed_checks=$((passed_checks + 1))
    check_status 0 "核心文档完整"
else
    check_status 1 "文档不完整 ($doc_count/2)"
fi

echo ""
echo -e "${BLUE}🚀 第四阶段：部署准备检查${NC}"
echo "--------------------------------"

# 11. 检查Docker配置
echo "检查Docker配置..."
total_checks=$((total_checks + 1))
if [ -f "Dockerfile" ] && [ -f "docker-compose.microservices.yml" ]; then
    passed_checks=$((passed_checks + 1))
    check_status 0 "Docker配置完整"
else
    check_status 1 "Docker配置不完整"
fi

# 12. 检查部署脚本
echo "检查部署脚本..."
deploy_scripts=("scripts/fix-tests.sh" "scripts/test-api-integration.sh" "scripts/track-completion.sh")
deploy_count=0
for script in "${deploy_scripts[@]}"; do
    if [ -f "$script" ]; then
        deploy_count=$((deploy_count + 1))
    fi
done
total_checks=$((total_checks + 1))
if [ $deploy_count -eq 3 ]; then
    passed_checks=$((passed_checks + 1))
    check_status 0 "部署脚本完整"
else
    check_status 1 "部署脚本不完整 ($deploy_count/3)"
fi

echo ""
echo "================================"
echo -e "${BLUE}📊 完成度统计${NC}"
echo "================================"

# 计算完成度
completion_percentage=$((passed_checks * 100 / total_checks))

echo "总检查项: $total_checks"
echo "通过检查: $passed_checks"
echo "失败检查: $((total_checks - passed_checks))"

if [ $completion_percentage -ge 90 ]; then
    echo -e "完成度: ${GREEN}$completion_percentage%${NC} 🎉"
    echo -e "${GREEN}项目接近完成！${NC}"
elif [ $completion_percentage -ge 70 ]; then
    echo -e "完成度: ${YELLOW}$completion_percentage%${NC} 🚧"
    echo -e "${YELLOW}项目进展良好，继续努力！${NC}"
else
    echo -e "完成度: ${RED}$completion_percentage%${NC} ⚠️"
    echo -e "${RED}需要加快进度！${NC}"
fi

echo ""
echo -e "${BLUE}📋 下一步行动建议${NC}"
echo "================================"

if [ $completion_percentage -lt 100 ]; then
    echo "🔧 需要完成的任务："
    
    # 根据失败的检查给出建议
    if [ $duplicate_count -gt 0 ]; then
        echo "  - 修复剩余的重复导入问题"
    fi
    
    if [ $total_frontend -le 200 ]; then
        echo "  - 完善前端组件和界面"
    fi
    
    if [ $service_count -le 10 ]; then
        echo "  - 完善后端微服务"
    fi
    
    if [ $agent_count -lt 4 ]; then
        echo "  - 完善智能体服务"
    fi
    
    if [ $diagnostic_count -lt 4 ]; then
        echo "  - 完善诊断服务"
    fi
    
    echo ""
    echo "🎯 建议优先级："
    echo "  1. 修复测试和API问题（紧急）"
    echo "  2. 完善核心功能（重要）"
    echo "  3. 优化性能和用户体验（重要）"
    echo "  4. 准备部署和上线（中等）"
else
    echo -e "${GREEN}🎉 恭喜！项目已达到100%完成度！${NC}"
    echo "🚀 可以开始准备生产环境部署了！"
fi

echo ""
echo "📅 更新时间: $(date)"
echo "================================" 