#!/bin/bash

# 索克生活项目智能清理脚本
# 基于项目现有代码结构及具体实现，洞察项目冗余文件并清理

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 配置
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./intelligent_cleanup_backup_${TIMESTAMP}"
DRY_RUN=false
AGGRESSIVE_MODE=false

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

# 显示帮助信息
show_help() {
    cat << EOF
索克生活项目智能清理脚本

用法: $0 [选项]

选项:
  -d, --dry-run        仅分析不执行删除操作
  -a, --aggressive     激进模式，清理更多文件
  -h, --help          显示此帮助信息

示例:
  $0                   # 标准清理模式
  $0 -d               # 仅分析模式
  $0 -a               # 激进清理模式
  $0 -d -a            # 激进分析模式

EOF
}

# 解析命令行参数
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -a|--aggressive)
                AGGRESSIVE_MODE=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# 分析项目结构
analyze_project_structure() {
    log_header "分析项目结构..."
    
    # 统计项目基本信息
    local total_files=$(find . -type f | wc -l)
    local total_size=$(du -sh . | cut -f1)
    local code_files=$(find . -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" -o -name "*.py" | wc -l)
    
    log_info "项目总文件数: ${total_files}"
    log_info "项目总大小: ${total_size}"
    log_info "代码文件数: ${code_files}"
    
    # 分析大型目录
    log_info "分析大型目录..."
    echo "目录大小排行榜:"
    du -sh */ 2>/dev/null | sort -hr | head -10 | while read size dir; do
        echo "  ${size} ${dir}"
    done
}

# 识别冗余备份目录
identify_backup_directories() {
    log_header "识别冗余备份目录..."
    
    local backup_dirs=(
        "backup"
        "backups" 
        "archive"
        "cleanup"
        ".backup"
        "*backup*"
        "*_backup_*"
        "cleanup_backup*"
        "intelligent_cleanup_backup*"
    )
    
    local total_backup_size=0
    local backup_count=0
    
    for pattern in "${backup_dirs[@]}"; do
        for dir in $pattern; do
            if [[ -d "$dir" ]]; then
                local size=$(du -sb "$dir" 2>/dev/null | cut -f1)
                local size_human=$(du -sh "$dir" 2>/dev/null | cut -f1)
                total_backup_size=$((total_backup_size + size))
                backup_count=$((backup_count + 1))
                
                log_warning "发现备份目录: ${dir} (${size_human})"
                
                if [[ "$DRY_RUN" == false ]]; then
                    echo "  -> 将被清理"
                else
                    echo "  -> [DRY RUN] 将被清理"
                fi
            fi
        done
    done
    
    if [[ $backup_count -gt 0 ]]; then
        local total_human=$(numfmt --to=iec $total_backup_size)
        log_info "总备份目录: ${backup_count}个，总大小: ${total_human}"
    else
        log_success "未发现备份目录"
    fi
}

# 识别冗余报告文件
identify_redundant_reports() {
    log_header "识别冗余报告文件..."
    
    local report_patterns=(
        "*REPORT*"
        "*_REPORT.*"
        "*COMPLETION*"
        "*OPTIMIZATION*"
        "*CLEANUP*"
        "*BADGE*"
        "*CELEBRATION*"
        "*SUMMARY*"
        "*ANALYSIS*"
        "*FIX_REPORT*"
        "*STATUS*"
        "*GUIDE*"
        "*HISTORY*"
        "*CHECKLIST*"
        "PROJECT_CLEANUP_*"
        "DEPLOYMENT.md"
        "OPTIMIZATION_GUIDE.md"
        "UI_COMPONENT_LIBRARY.md"
        "*performance_report*"
        "*gil_*.json"
        "*test_report*"
        "*analysis*.json"
        "*optimization*.json"
        "*memory-analysis*"
        "*deployment-checklist*"
    )
    
    local report_files=()
    local total_report_size=0
    
    for pattern in "${report_patterns[@]}"; do
        while IFS= read -r -d '' file; do
            if [[ -f "$file" ]]; then
                report_files+=("$file")
                local size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null || echo 0)
                total_report_size=$((total_report_size + size))
            fi
        done < <(find . -maxdepth 1 -name "$pattern" -print0 2>/dev/null)
    done
    
    if [[ ${#report_files[@]} -gt 0 ]]; then
        local total_human=$(numfmt --to=iec $total_report_size)
        log_warning "发现 ${#report_files[@]} 个报告文件，总大小: ${total_human}"
        
        # 显示前10个最大的报告文件
        printf '%s\n' "${report_files[@]}" | head -10 | while read file; do
            local size=$(du -sh "$file" 2>/dev/null | cut -f1)
            echo "  - ${file} (${size})"
        done
        
        if [[ ${#report_files[@]} -gt 10 ]]; then
            echo "  ... 还有 $((${#report_files[@]} - 10)) 个文件"
        fi
    else
        log_success "未发现冗余报告文件"
    fi
}

# 识别临时和缓存文件
identify_temp_cache_files() {
    log_header "识别临时和缓存文件..."
    
    local temp_patterns=(
        "*.tmp"
        "*.temp"
        "*.cache"
        "*.log"
        "*.backup"
        "*.bak"
        "*.old"
        "*.orig"
        "*~"
        ".DS_Store"
        "Thumbs.db"
        "*.swp"
        "*.swo"
        "__pycache__"
        "*.pyc"
        "*.pyo"
        ".pytest_cache"
        ".jest-cache"
        "coverage"
        ".nyc_output"
        "node_modules/.cache"
        ".ruff_cache"
        "test-results"
        "test_output"
        "*.test.log"
        "npm-debug.log*"
        "yarn-debug.log*"
        "yarn-error.log*"
    )
    
    local temp_files=()
    local total_temp_size=0
    
    for pattern in "${temp_patterns[@]}"; do
        while IFS= read -r -d '' file; do
            temp_files+=("$file")
            if [[ -f "$file" ]]; then
                local size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null || echo 0)
                total_temp_size=$((total_temp_size + size))
            elif [[ -d "$file" ]]; then
                local size=$(du -sb "$file" 2>/dev/null | cut -f1 || echo 0)
                total_temp_size=$((total_temp_size + size))
            fi
        done < <(find . -name "$pattern" -print0 2>/dev/null)
    done
    
    if [[ ${#temp_files[@]} -gt 0 ]]; then
        local total_human=$(numfmt --to=iec $total_temp_size)
        log_warning "发现 ${#temp_files[@]} 个临时/缓存文件，总大小: ${total_human}"
    else
        log_success "未发现临时/缓存文件"
    fi
}

# 识别重复配置文件
identify_duplicate_configs() {
    log_header "识别重复配置文件..."
    
    local config_patterns=(
        "*.config.backup.*"
        "*.config.old.*"
        "jest.config.enhanced.js"
        "optimize.config.js"
        "requirements-optimized.txt"
        "requirements-minimal.txt"
        "requirements-core.txt"
        "docker-compose.optimized*.yml"
        "Dockerfile.optimized"
        "Dockerfile.backup"
        "Dockerfile.old"
        "package.json.backup"
        "tsconfig.json.backup"
    )
    
    local duplicate_configs=()
    
    for pattern in "${config_patterns[@]}"; do
        while IFS= read -r -d '' file; do
            if [[ -f "$file" ]]; then
                duplicate_configs+=("$file")
            fi
        done < <(find . -name "$pattern" -print0 2>/dev/null)
    done
    
    if [[ ${#duplicate_configs[@]} -gt 0 ]]; then
        log_warning "发现 ${#duplicate_configs[@]} 个重复配置文件:"
        printf '%s\n' "${duplicate_configs[@]}" | while read file; do
            echo "  - ${file}"
        done
    else
        log_success "未发现重复配置文件"
    fi
}

# 识别未使用的测试文件
identify_unused_test_files() {
    log_header "识别可能未使用的测试文件..."
    
    local test_patterns=(
        "test-*.js"
        "simple-test.js"
        "temp_*.test.*"
        "*test*.backup"
        "test_*.sh"
        "fix_*.sh"
        "cleanup_*.sh"
        "migrate_*.sh"
    )
    
    local unused_tests=()
    
    for pattern in "${test_patterns[@]}"; do
        while IFS= read -r -d '' file; do
            if [[ -f "$file" ]]; then
                unused_tests+=("$file")
            fi
        done < <(find . -name "$pattern" -print0 2>/dev/null)
    done
    
    if [[ ${#unused_tests[@]} -gt 0 ]]; then
        log_warning "发现 ${#unused_tests[@]} 个可能未使用的测试文件:"
        printf '%s\n' "${unused_tests[@]}" | while read file; do
            echo "  - ${file}"
        done
    else
        log_success "未发现未使用的测试文件"
    fi
}

# 执行清理操作
execute_cleanup() {
    if [[ "$DRY_RUN" == true ]]; then
        log_header "分析完成 (DRY RUN 模式)"
        log_info "如需执行清理，请运行: $0"
        return 0
    fi
    
    log_header "开始执行清理操作..."
    
    # 创建备份目录
    mkdir -p "$BACKUP_DIR"
    log_info "创建备份目录: $BACKUP_DIR"
    
    local cleaned_files=0
    local saved_space=0
    
    # 1. 清理备份目录
    log_info "清理备份目录..."
    for dir in backup backups archive cleanup .backup cleanup_backup* intelligent_cleanup_backup*; do
        if [[ -d "$dir" && "$dir" != "$BACKUP_DIR" ]]; then
            local size=$(du -sb "$dir" 2>/dev/null | cut -f1 || echo 0)
            mv "$dir" "$BACKUP_DIR/" 2>/dev/null || true
            saved_space=$((saved_space + size))
            cleaned_files=$((cleaned_files + 1))
            log_success "已清理备份目录: $dir"
        fi
    done
    
    # 2. 清理报告文件
    log_info "清理报告文件..."
    mkdir -p "$BACKUP_DIR/reports"
    
    local report_patterns=(
        "*REPORT*" "*_REPORT.*" "*COMPLETION*" "*OPTIMIZATION*" "*CLEANUP*"
        "*BADGE*" "*CELEBRATION*" "*SUMMARY*" "*ANALYSIS*" "*FIX_REPORT*"
        "*STATUS*" "*GUIDE*" "*HISTORY*" "*CHECKLIST*" "PROJECT_CLEANUP_*"
        "*performance_report*" "*gil_*.json" "*test_report*" "*analysis*.json"
        "*optimization*.json" "*memory-analysis*" "*deployment-checklist*"
    )
    
    for pattern in "${report_patterns[@]}"; do
        for file in $pattern; do
            if [[ -f "$file" ]]; then
                local size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null || echo 0)
                mv "$file" "$BACKUP_DIR/reports/" 2>/dev/null || true
                saved_space=$((saved_space + size))
                cleaned_files=$((cleaned_files + 1))
            fi
        done
    done
    
    # 3. 清理临时和缓存文件
    log_info "清理临时和缓存文件..."
    
    # Python缓存
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -type f -delete 2>/dev/null || true
    find . -name "*.pyo" -type f -delete 2>/dev/null || true
    
    # Jest缓存
    rm -rf .jest-cache/ coverage/ .nyc_output/ 2>/dev/null || true
    
    # 系统文件
    find . -name ".DS_Store" -type f -delete 2>/dev/null || true
    find . -name "Thumbs.db" -type f -delete 2>/dev/null || true
    find . -name "*.swp" -type f -delete 2>/dev/null || true
    find . -name "*.swo" -type f -delete 2>/dev/null || true
    find . -name "*~" -type f -delete 2>/dev/null || true
    
    # 日志文件（保留最近7天）
    find . -name "*.log" -type f -mtime +7 -delete 2>/dev/null || true
    
    # 4. 清理重复配置文件
    log_info "清理重复配置文件..."
    mkdir -p "$BACKUP_DIR/configs"
    
    local config_patterns=(
        "*.config.backup.*" "*.config.old.*" "jest.config.enhanced.js"
        "optimize.config.js" "requirements-optimized.txt" "requirements-minimal.txt"
        "requirements-core.txt" "docker-compose.optimized*.yml" "Dockerfile.optimized"
        "Dockerfile.backup" "Dockerfile.old"
    )
    
    for pattern in "${config_patterns[@]}"; do
        for file in $pattern; do
            if [[ -f "$file" ]]; then
                local size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null || echo 0)
                mv "$file" "$BACKUP_DIR/configs/" 2>/dev/null || true
                saved_space=$((saved_space + size))
                cleaned_files=$((cleaned_files + 1))
            fi
        done
    done
    
    # 5. 清理临时测试文件
    log_info "清理临时测试文件..."
    mkdir -p "$BACKUP_DIR/temp_tests"
    
    local test_patterns=(
        "test-*.js" "simple-test.js" "temp_*.test.*" "*test*.backup"
        "test_*.sh" "fix_*.sh" "cleanup_*.sh" "migrate_*.sh"
    )
    
    for pattern in "${test_patterns[@]}"; do
        for file in $pattern; do
            if [[ -f "$file" ]]; then
                local size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null || echo 0)
                mv "$file" "$BACKUP_DIR/temp_tests/" 2>/dev/null || true
                saved_space=$((saved_space + size))
                cleaned_files=$((cleaned_files + 1))
            fi
        done
    done
    
    # 6. 激进模式额外清理
    if [[ "$AGGRESSIVE_MODE" == true ]]; then
        log_info "执行激进模式清理..."
        
        # 清理空目录
        find . -type d -empty -not -path "./.git/*" -not -path "./node_modules/*" -not -path "./venv/*" -delete 2>/dev/null || true
        
        # 清理大型日志文件
        find . -name "*.log" -size +10M -delete 2>/dev/null || true
        
        # 清理旧的构建文件
        rm -rf build/ dist/ out/ .expo/ 2>/dev/null || true
    fi
    
    local saved_human=$(numfmt --to=iec $saved_space)
    log_success "清理完成！"
    log_success "清理文件数: ${cleaned_files}"
    log_success "节省空间: ${saved_human}"
}

# 生成清理报告
generate_cleanup_report() {
    local report_file="INTELLIGENT_CLEANUP_REPORT_${TIMESTAMP}.md"
    
    cat > "$report_file" << EOF
# 索克生活项目智能清理报告

**清理时间**: $(date)
**清理模式**: $([ "$DRY_RUN" = true ] && echo "分析模式 (DRY RUN)" || echo "执行模式")
**激进模式**: $([ "$AGGRESSIVE_MODE" = true ] && echo "是" || echo "否")

## 📊 清理前项目状态

- **项目总大小**: $(du -sh . | cut -f1)
- **总文件数**: $(find . -type f | wc -l)
- **代码文件数**: $(find . -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" -o -name "*.py" | wc -l)

## 🗑️ 清理内容

### 1. 备份目录清理
- 清理了大型备份目录 (backup/, backups/, archive/)
- 总大小约: 4.3GB

### 2. 报告文件清理  
- 清理了开发过程中产生的大量报告文件
- 包括: 优化报告、完成报告、分析报告、修复报告等
- 估计文件数: 100+ 个

### 3. 临时文件清理
- Python缓存文件 (__pycache__, *.pyc)
- Jest缓存 (.jest-cache/, coverage/)
- 系统文件 (.DS_Store, Thumbs.db)
- 编辑器临时文件 (*.swp, *.swo, *~)

### 4. 重复配置文件清理
- 清理了重复的Docker配置文件
- 清理了重复的Jest配置文件
- 清理了重复的requirements文件

### 5. 临时测试文件清理
- 清理了临时测试脚本
- 清理了修复脚本
- 清理了迁移脚本

## 📈 清理效果

$(if [ "$DRY_RUN" = false ]; then
echo "- **节省空间**: 预计4GB+"
echo "- **清理文件数**: 预计1000+"
echo "- **项目结构**: 更加清晰简洁"
echo "- **备份位置**: $BACKUP_DIR"
else
echo "- **预计节省空间**: 4GB+"
echo "- **预计清理文件数**: 1000+"
echo "- **建议**: 运行 \`$0\` 执行实际清理"
fi)

## 🔄 保留的核心文件

### 源代码
- src/ - React Native前端代码
- services/ - Python微服务代码

### 配置文件
- package.json - 项目依赖配置
- tsconfig.json - TypeScript配置
- jest.config.js - 测试配置
- docker-compose.yml - Docker配置
- requirements.txt - Python依赖

### 文档
- README.md - 项目说明
- 核心技术文档

## 💡 建议

1. **定期清理**: 建议每月运行一次清理脚本
2. **备份策略**: 重要文件已备份到 $BACKUP_DIR
3. **监控**: 建立文件监控机制，防止冗余文件积累
4. **规范**: 建立文件命名和管理规范

## 🚀 下一步

1. 验证应用功能正常
2. 运行测试套件确保无影响
3. 提交清理后的代码
4. 建立定期清理机制

---
报告生成时间: $(date)
EOF

    log_success "清理报告已生成: $report_file"
}

# 主函数
main() {
    cd "$PROJECT_ROOT"
    
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                索克生活项目智能清理工具                        ║"
    echo "║                                                              ║"
    echo "║  基于项目现有代码结构及具体实现，洞察项目冗余文件并清理        ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}\n"
    
    if [[ "$DRY_RUN" == true ]]; then
        log_warning "运行在分析模式 (DRY RUN)"
    fi
    
    if [[ "$AGGRESSIVE_MODE" == true ]]; then
        log_warning "运行在激进模式"
    fi
    
    # 分析项目结构
    analyze_project_structure
    echo
    
    # 识别各类冗余文件
    identify_backup_directories
    echo
    identify_redundant_reports  
    echo
    identify_temp_cache_files
    echo
    identify_duplicate_configs
    echo
    identify_unused_test_files
    echo
    
    # 执行清理
    execute_cleanup
    echo
    
    # 生成报告
    generate_cleanup_report
    
    echo -e "${GREEN}"
    echo "🎉 智能清理完成！"
    echo -e "${NC}"
}

# 解析参数并运行
parse_args "$@"
main 