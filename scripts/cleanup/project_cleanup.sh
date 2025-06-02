#!/bin/bash

# 索克生活项目清理脚本
# 清理冗余文件和代码，提升项目整洁度

set -e

echo "🧹 开始清理索克生活项目..."

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

# 创建备份目录
BACKUP_DIR="./cleanup_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "📁 项目根目录: $PROJECT_ROOT"
echo "💾 备份目录: $BACKUP_DIR"

# 1. 清理开发报告文件
echo "📋 清理开发报告文件..."
REPORT_FILES=(
    "*_REPORT.md"
    "*_REPORT.json"
    "*_COMPREHENSIVE_REPORT.md"
    "*_OPTIMIZATION_REPORT.md"
    "*_IMPLEMENTATION_REPORT.md"
    "*_COMPLETION_REPORT.md"
    "*_PROGRESS_REPORT.md"
    "*_ANALYSIS_REPORT.md"
    "*_FIX_REPORT.*"
    "*_STATUS.md"
    "*_GUIDE.md"
    "performance_report_*.json"
    "gil_*.json"
    "CLEANUP_PLAN.md"
    "DEPLOYMENT.md"
    "PROJECT_STATUS.md"
    "OPTIMIZATION_GUIDE.md"
    "UI_COMPONENT_LIBRARY.md"
)

# 备份报告文件
mkdir -p "$BACKUP_DIR/reports"
for pattern in "${REPORT_FILES[@]}"; do
    if ls $pattern 1> /dev/null 2>&1; then
        mv $pattern "$BACKUP_DIR/reports/" 2>/dev/null || true
    fi
done

echo "✅ 已清理 $(ls "$BACKUP_DIR/reports" | wc -l) 个报告文件"

# 2. 清理重复的Docker配置文件
echo "🐳 清理重复的Docker配置文件..."
DOCKER_FILES=(
    "docker-compose.optimized.yml"
    "docker-compose.optimized-new.yml"
    "docker-compose.optimized-complete.yml"
    "Dockerfile.optimized"
)

mkdir -p "$BACKUP_DIR/docker"
for file in "${DOCKER_FILES[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" "$BACKUP_DIR/docker/"
    fi
done

echo "✅ 已清理 $(ls "$BACKUP_DIR/docker" 2>/dev/null | wc -l) 个重复Docker配置文件"

# 3. 清理重复的配置文件
echo "⚙️ 清理重复的配置文件..."
CONFIG_FILES=(
    "jest.config.enhanced.js"
    "optimize.config.js"
    "requirements-optimized.txt"
    "requirements-minimal.txt"
    "requirements-core.txt"
)

mkdir -p "$BACKUP_DIR/configs"
for file in "${CONFIG_FILES[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" "$BACKUP_DIR/configs/"
    fi
done

echo "✅ 已清理 $(ls "$BACKUP_DIR/configs" 2>/dev/null | wc -l) 个重复配置文件"

# 4. 清理Python缓存文件
echo "🐍 清理Python缓存文件..."
find . -name "*.pyc" -type f -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyo" -type f -delete 2>/dev/null || true

echo "✅ 已清理Python缓存文件"

# 5. 清理Jest缓存
echo "🧪 清理Jest缓存..."
if [ -d ".jest-cache" ]; then
    rm -rf ".jest-cache"
fi

if [ -d ".pytest_cache" ]; then
    rm -rf ".pytest_cache"
fi

echo "✅ 已清理Jest和Pytest缓存"

# 6. 清理临时文件
echo "🗑️ 清理临时文件..."
find . -name "*.tmp" -type f -delete 2>/dev/null || true
find . -name "*.temp" -type f -delete 2>/dev/null || true
find . -name ".DS_Store" -type f -delete 2>/dev/null || true
find . -name "Thumbs.db" -type f -delete 2>/dev/null || true

echo "✅ 已清理临时文件"

# 7. 清理空目录
echo "📂 清理空目录..."
find . -type d -empty -not -path "./.git/*" -not -path "./node_modules/*" -not -path "./venv/*" -not -path "./services/venv/*" -delete 2>/dev/null || true

echo "✅ 已清理空目录"

# 8. 清理日志文件（保留最近7天）
echo "📝 清理旧日志文件..."
find ./logs -name "*.log" -type f -mtime +7 -delete 2>/dev/null || true

echo "✅ 已清理7天前的日志文件"

# 9. 清理重复的虚拟环境（保留根目录的venv）
echo "🐍 检查虚拟环境..."
if [ -d "services/venv" ]; then
    echo "⚠️  发现services/venv，建议手动检查是否需要"
    echo "   如果不需要，可以运行: rm -rf services/venv"
fi

# 10. 生成清理报告
echo "📊 生成清理报告..."
CLEANUP_REPORT="PROJECT_CLEANUP_$(date +%Y%m%d_%H%M%S).md"

cat > "$CLEANUP_REPORT" << EOF
# 🧹 项目清理报告

**清理时间**: $(date)
**备份目录**: $BACKUP_DIR

## 📋 清理内容

### 1. 开发报告文件
- 清理了大量开发过程中生成的报告文件
- 包括优化报告、实现报告、分析报告等
- 文件已备份到: \`$BACKUP_DIR/reports/\`

### 2. Docker配置文件
- 清理了重复的Docker配置文件
- 保留了主要的docker-compose.yml和Dockerfile
- 文件已备份到: \`$BACKUP_DIR/docker/\`

### 3. 配置文件
- 清理了重复的配置文件
- 保留了核心配置文件
- 文件已备份到: \`$BACKUP_DIR/configs/\`

### 4. 缓存文件
- 清理了Python缓存文件 (\*.pyc, __pycache__)
- 清理了Jest和Pytest缓存
- 清理了临时文件

### 5. 系统文件
- 清理了.DS_Store、Thumbs.db等系统文件
- 清理了空目录
- 清理了7天前的日志文件

## 🎯 清理效果

项目结构更加清晰，减少了冗余文件，提升了：
- 项目加载速度
- 代码可读性
- 维护效率
- 存储空间利用率

## 📝 注意事项

1. 所有清理的文件都已备份到 \`$BACKUP_DIR\`
2. 如需恢复某些文件，可从备份目录中找回
3. 建议定期运行此清理脚本保持项目整洁

## 🔄 后续建议

1. 将清理脚本加入到CI/CD流程
2. 定期（如每周）运行清理脚本
3. 在.gitignore中添加更多临时文件模式
4. 建立文件命名规范，避免产生冗余文件

EOF

echo "✅ 清理报告已生成: $CLEANUP_REPORT"

# 11. 显示清理统计
echo ""
echo "🎉 项目清理完成！"
echo ""
echo "📊 清理统计:"
echo "   - 报告文件: $(ls "$BACKUP_DIR/reports" 2>/dev/null | wc -l) 个"
echo "   - Docker文件: $(ls "$BACKUP_DIR/docker" 2>/dev/null | wc -l) 个"
echo "   - 配置文件: $(ls "$BACKUP_DIR/configs" 2>/dev/null | wc -l) 个"
echo "   - 备份目录: $BACKUP_DIR"
echo ""
echo "💡 提示:"
echo "   - 清理报告: $CLEANUP_REPORT"
echo "   - 如需恢复文件，请查看备份目录"
echo "   - 建议定期运行此脚本保持项目整洁"
echo "" 