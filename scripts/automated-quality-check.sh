#!/bin/bash

# 索克生活项目自动化代码质量检查脚本
# 持续监控代码质量，自动修复常见问题，生成质量报告

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# 配置
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}}")/.. && pwd)"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_DIR="./quality-reports"
REPORT_FILE="${REPORT_DIR}/quality_report_${TIMESTAMP}.md"
AUTO_FIX=false

# 日志函数
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_header() {
    echo -e "${PURPLE}🎯 $1${NC}"
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--fix)
            AUTO_FIX=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

# 创建报告目录
create_report_dir() {
    mkdir -p "$REPORT_DIR"
    log_info "创建报告目录: $REPORT_DIR"
}

# 初始化报告文件
init_report() {
    cat > "$REPORT_FILE" << 'REPORT_EOF'
# 索克生活项目代码质量报告

## 📊 质量检查概览

REPORT_EOF
}

# ESLint检查
run_eslint_check() {
    log_header "运行ESLint代码质量检查"
    
    local eslint_output
    local eslint_exit_code=0
    
    if [ "$AUTO_FIX" = true ]; then
        log_info "运行ESLint自动修复..."
        eslint_output=$(npm run lint -- --fix 2>&1) || eslint_exit_code=$?
    else
        log_info "运行ESLint检查..."
        eslint_output=$(npm run lint 2>&1) || eslint_exit_code=$?
    fi
    
    # 统计问题数量
    local error_count=$(echo "$eslint_output" | grep -c "error" || echo "0")
    local warning_count=$(echo "$eslint_output" | grep -c "warning" || echo "0")
    
    cat >> "$REPORT_FILE" << 'ESLINT_EOF'
### ESLint检查结果

ESLINT_EOF
    
    echo "- **错误数量**: $error_count" >> "$REPORT_FILE"
    echo "- **警告数量**: $warning_count" >> "$REPORT_FILE"
    echo "- **退出代码**: $eslint_exit_code" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"

    if [ $eslint_exit_code -eq 0 ]; then
        log_success "ESLint检查通过"
    else
        log_warning "ESLint发现 $error_count 个错误和 $warning_count 个警告"
    fi
    
    return $eslint_exit_code
}

# 代码复杂度分析
analyze_complexity() {
    log_header "分析代码复杂度"
    
    log_info "分析代码复杂度..."
    
    # 统计代码行数
    local total_lines=$(find src -name "*.ts" -o -name "*.tsx" | xargs wc -l | tail -1 | awk '{print $1}' || echo "0")
    local total_files=$(find src -name "*.ts" -o -name "*.tsx" | wc -l || echo "0")
    local avg_lines_per_file=0
    
    if [ "$total_files" -gt 0 ]; then
        avg_lines_per_file=$((total_lines / total_files))
    fi
    
    cat >> "$REPORT_FILE" << 'COMPLEXITY_EOF'
### 代码复杂度分析

COMPLEXITY_EOF
    
    echo "- **总代码行数**: $total_lines" >> "$REPORT_FILE"
    echo "- **总文件数**: $total_files" >> "$REPORT_FILE"
    echo "- **平均每文件行数**: $avg_lines_per_file" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"

    log_success "代码复杂度分析完成"
}

# 性能分析
analyze_performance() {
    log_header "分析项目性能指标"
    
    log_info "收集性能指标..."
    
    # 项目大小分析
    local project_size=$(du -sh . | cut -f1 || echo "未知")
    local src_size=$(du -sh src | cut -f1 || echo "未知")
    
    cat >> "$REPORT_FILE" << 'PERFORMANCE_EOF'
### 性能指标分析

PERFORMANCE_EOF
    
    echo "- **项目总大小**: $project_size" >> "$REPORT_FILE"
    echo "- **源代码大小**: $src_size" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"

    log_success "性能分析完成"
}

# 生成改进建议
generate_recommendations() {
    log_header "生成改进建议"
    
    cat >> "$REPORT_FILE" << 'RECOMMENDATIONS_EOF'
## 🎯 改进建议

### 立即处理
- [ ] 修复所有ESLint错误
- [ ] 解决TypeScript类型问题
- [ ] 修复失败的测试用例

### 短期优化
- [ ] 重构超过300行的大文件
- [ ] 优化依赖安全问题
- [ ] 改善代码覆盖率

### 长期规划
- [ ] 建立自动化CI/CD流程
- [ ] 实现性能监控
- [ ] 建立代码质量门禁

RECOMMENDATIONS_EOF

    log_success "改进建议生成完成"
}

# 主执行函数
main() {
    log_header "开始自动化代码质量检查"
    
    cd "$PROJECT_ROOT"
    
    create_report_dir
    init_report
    
    local overall_exit_code=0
    
    # 运行各项检查
    run_eslint_check || overall_exit_code=$?
    analyze_complexity
    analyze_performance
    generate_recommendations
    
    # 生成总结
    if [ $overall_exit_code -eq 0 ]; then
        log_success "所有质量检查通过！"
        echo "✅ **总体状态**: 通过" >> "$REPORT_FILE"
    else
        log_warning "发现质量问题，请查看报告"
        echo "⚠️ **总体状态**: 需要改进" >> "$REPORT_FILE"
    fi
    
    log_info "质量报告已生成: $REPORT_FILE"
    
    return $overall_exit_code
}

# 执行主函数
main "$@" 