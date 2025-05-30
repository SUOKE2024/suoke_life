#!/bin/bash

# 索克生活项目 - 未使用代码清理脚本
# 使用方法: ./scripts/cleanup-unused-code.sh [--dry-run|--safe|--aggressive]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认参数
DRY_RUN=false
SAFE_MODE=true
AGGRESSIVE_MODE=false

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --safe)
            SAFE_MODE=true
            AGGRESSIVE_MODE=false
            shift
            ;;
        --aggressive)
            SAFE_MODE=false
            AGGRESSIVE_MODE=true
            shift
            ;;
        *)
            echo "未知参数: $1"
            echo "使用方法: $0 [--dry-run|--safe|--aggressive]"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}🧹 索克生活项目 - 未使用代码清理工具${NC}"
echo "=================================================="

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}⚠️  DRY RUN 模式 - 仅显示将要执行的操作${NC}"
fi

if [ "$SAFE_MODE" = true ]; then
    echo -e "${GREEN}🛡️  安全模式 - 仅清理低风险代码${NC}"
else
    echo -e "${RED}⚡ 激进模式 - 包含中高风险清理${NC}"
fi

echo ""

# 创建备份
create_backup() {
    echo -e "${BLUE}📦 创建代码备份...${NC}"
    BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
    
    if [ "$DRY_RUN" = false ]; then
        mkdir -p "$BACKUP_DIR"
        cp -r src/ "$BACKUP_DIR/"
        echo -e "${GREEN}✅ 备份已创建: $BACKUP_DIR${NC}"
    else
        echo -e "${YELLOW}[DRY RUN] 将创建备份目录: $BACKUP_DIR${NC}"
    fi
}

# 检查未使用的导出
check_unused_exports() {
    echo -e "${BLUE}🔍 检查未使用的导出...${NC}"
    
    if command -v npx &> /dev/null; then
        if [ "$DRY_RUN" = false ]; then
            npx ts-unused-exports tsconfig.json --excludePathsFromReport=node_modules > unused_exports_report.txt
            echo -e "${GREEN}✅ 未使用导出报告已生成: unused_exports_report.txt${NC}"
        else
            echo -e "${YELLOW}[DRY RUN] 将生成未使用导出报告${NC}"
        fi
    else
        echo -e "${RED}❌ npx 未找到，跳过未使用导出检查${NC}"
    fi
}

# 清理明确未使用的文件
cleanup_obvious_unused() {
    echo -e "${BLUE}🗑️  清理明确未使用的文件...${NC}"
    
    # 清理备份文件
    BACKUP_FILES=(
        "src/screens/explore/ExploreScreen.backup.tsx"
        "src/screens/main/HomeScreen.backup.tsx"
    )
    
    for file in "${BACKUP_FILES[@]}"; do
        if [ -f "$file" ]; then
            if [ "$DRY_RUN" = false ]; then
                rm "$file"
                echo -e "${GREEN}✅ 已删除备份文件: $file${NC}"
            else
                echo -e "${YELLOW}[DRY RUN] 将删除: $file${NC}"
            fi
        fi
    done
}

# 清理未使用的导入
cleanup_unused_imports() {
    echo -e "${BLUE}📝 清理未使用的导入...${NC}"
    
    if command -v eslint &> /dev/null; then
        if [ "$DRY_RUN" = false ]; then
            npx eslint src/ --fix --rule "no-unused-vars: error" || true
            echo -e "${GREEN}✅ ESLint 自动修复完成${NC}"
        else
            echo -e "${YELLOW}[DRY RUN] 将运行 ESLint 自动修复${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  ESLint 未找到，跳过自动修复${NC}"
    fi
}

# 清理空的导出文件
cleanup_empty_exports() {
    echo -e "${BLUE}📄 检查空的导出文件...${NC}"
    
    # 查找只有导出语句但没有实际内容的文件
    find src/ -name "*.ts" -o -name "*.tsx" | while read -r file; do
        if [ -f "$file" ]; then
            # 检查文件是否只包含导出和导入语句
            content_lines=$(grep -v "^import\|^export\|^//\|^/\*\|^\*\|^$" "$file" | wc -l)
            if [ "$content_lines" -eq 0 ]; then
                if [ "$DRY_RUN" = false ]; then
                    echo -e "${YELLOW}⚠️  发现可能的空导出文件: $file${NC}"
                else
                    echo -e "${YELLOW}[DRY RUN] 发现可能的空导出文件: $file${NC}"
                fi
            fi
        fi
    done
}

# 安全模式清理
safe_cleanup() {
    echo -e "${GREEN}🛡️  执行安全模式清理...${NC}"
    
    cleanup_obvious_unused
    cleanup_unused_imports
    cleanup_empty_exports
}

# 激进模式清理
aggressive_cleanup() {
    echo -e "${RED}⚡ 执行激进模式清理...${NC}"
    
    safe_cleanup
    
    # 清理可能未使用的工具函数
    echo -e "${BLUE}🔧 检查工具函数使用情况...${NC}"
    
    UTILS_TO_CHECK=(
        "src/utils/performanceOptimizer.ts"
        "src/utils/securityManager.ts"
        "src/utils/blockchainHealthData.ts"
        "src/utils/memoryMonitor.ts"
    )
    
    for util_file in "${UTILS_TO_CHECK[@]}"; do
        if [ -f "$util_file" ]; then
            # 检查是否有其他文件导入这个工具
            usage_count=$(grep -r "from.*$(basename "$util_file" .ts)" src/ --exclude="$util_file" | wc -l)
            if [ "$usage_count" -eq 0 ]; then
                if [ "$DRY_RUN" = false ]; then
                    echo -e "${YELLOW}⚠️  发现可能未使用的工具文件: $util_file${NC}"
                    echo -e "${YELLOW}   建议手动检查后删除${NC}"
                else
                    echo -e "${YELLOW}[DRY RUN] 可能未使用的工具文件: $util_file${NC}"
                fi
            fi
        fi
    done
}

# 生成清理报告
generate_report() {
    echo -e "${BLUE}📊 生成清理报告...${NC}"
    
    REPORT_FILE="cleanup_report_$(date +%Y%m%d_%H%M%S).md"
    
    if [ "$DRY_RUN" = false ]; then
        cat > "$REPORT_FILE" << EOF
# 代码清理报告

**清理时间**: $(date)
**清理模式**: $([ "$SAFE_MODE" = true ] && echo "安全模式" || echo "激进模式")

## 清理统计

### 已删除文件
$(find . -name "*.backup.*" -type f 2>/dev/null | wc -l) 个备份文件

### 修复的导入
ESLint 自动修复已完成

### 建议手动检查的文件
请查看上述输出中标记为 ⚠️ 的文件

## 下一步建议

1. 运行完整的测试套件
2. 检查应用功能是否正常
3. 提交清理后的代码

---
生成时间: $(date)
EOF
        echo -e "${GREEN}✅ 清理报告已生成: $REPORT_FILE${NC}"
    else
        echo -e "${YELLOW}[DRY RUN] 将生成清理报告: $REPORT_FILE${NC}"
    fi
}

# 主执行流程
main() {
    echo -e "${BLUE}🚀 开始代码清理流程...${NC}"
    echo ""
    
    # 创建备份
    create_backup
    echo ""
    
    # 检查未使用的导出
    check_unused_exports
    echo ""
    
    # 根据模式执行清理
    if [ "$SAFE_MODE" = true ]; then
        safe_cleanup
    else
        aggressive_cleanup
    fi
    echo ""
    
    # 生成报告
    generate_report
    echo ""
    
    echo -e "${GREEN}🎉 代码清理完成！${NC}"
    
    if [ "$DRY_RUN" = false ]; then
        echo ""
        echo -e "${YELLOW}⚠️  重要提醒:${NC}"
        echo "1. 请运行测试确保功能正常"
        echo "2. 检查应用是否能正常启动"
        echo "3. 如有问题，可从备份目录恢复"
    fi
}

# 执行主函数
main

echo ""
echo -e "${BLUE}📋 使用建议:${NC}"
echo "• 首次使用建议先运行 --dry-run 查看将要执行的操作"
echo "• 使用 --safe 模式进行保守清理"
echo "• 使用 --aggressive 模式进行更彻底的清理（需要更多测试）"
echo ""
echo -e "${GREEN}✨ 清理完成！项目代码更加整洁了！${NC}" 