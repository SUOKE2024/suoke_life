#!/bin/bash

# 索克生活项目清理脚本
# 清理冗余文件、备份文件和临时文件

set -e

echo "🧹 开始清理索克生活项目..."

# 记录清理前的项目大小
echo "📊 清理前项目大小："
du -sh . 2>/dev/null || echo "无法计算项目大小"

# 1. 清理备份目录（最大的冗余）
if [ -d ".backup" ]; then
    echo "🗑️  删除备份目录 (.backup/) - 大小: $(du -sh .backup 2>/dev/null | cut -f1)"
    rm -rf .backup/
    echo "✅ 备份目录已删除"
fi

# 2. 清理Jest缓存
if [ -d ".jest-cache" ]; then
    echo "🗑️  删除Jest缓存 (.jest-cache/) - 大小: $(du -sh .jest-cache 2>/dev/null | cut -f1)"
    rm -rf .jest-cache/
    echo "✅ Jest缓存已删除"
fi

# 3. 清理测试覆盖率报告
if [ -d "coverage" ]; then
    echo "🗑️  删除测试覆盖率报告 (coverage/) - 大小: $(du -sh coverage 2>/dev/null | cut -f1)"
    rm -rf coverage/
    echo "✅ 测试覆盖率报告已删除"
fi

# 4. 清理临时报告文件
echo "🗑️  删除临时报告文件..."
rm -f *-report.json
rm -f *-test-report.json
rm -f optimization-*.json
rm -f memory-analysis-*.json
rm -f deployment-checklist.json
rm -f performance-config.json
echo "✅ 临时报告文件已删除"

# 5. 清理src目录中的备份文件
echo "🗑️  删除源码备份文件..."
find src/ -name "*.backup.*" -type f -delete
echo "✅ 源码备份文件已删除"

# 6. 清理iOS项目备份文件
if [ -f "ios/SuokeLife.xcodeproj/project.pbxproj.backup" ]; then
    echo "🗑️  删除iOS项目备份文件..."
    rm -f ios/SuokeLife.xcodeproj/project.pbxproj.backup
    echo "✅ iOS项目备份文件已删除"
fi

# 7. 清理临时测试文件
echo "🗑️  删除临时测试文件..."
rm -f test-*.js
rm -f simple-test.js
echo "✅ 临时测试文件已删除"

# 8. 清理Python缓存
echo "🗑️  删除Python缓存文件..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -type f -delete 2>/dev/null || true
find . -name "*.pyo" -type f -delete 2>/dev/null || true
echo "✅ Python缓存文件已删除"

# 9. 清理Node.js缓存和临时文件
echo "🗑️  删除Node.js临时文件..."
rm -rf .npm/
rm -rf .yarn/
rm -f npm-debug.log*
rm -f yarn-debug.log*
rm -f yarn-error.log*
echo "✅ Node.js临时文件已删除"

# 10. 清理编辑器临时文件
echo "🗑️  删除编辑器临时文件..."
find . -name ".DS_Store" -type f -delete 2>/dev/null || true
find . -name "Thumbs.db" -type f -delete 2>/dev/null || true
find . -name "*.swp" -type f -delete 2>/dev/null || true
find . -name "*.swo" -type f -delete 2>/dev/null || true
find . -name "*~" -type f -delete 2>/dev/null || true
echo "✅ 编辑器临时文件已删除"

# 记录清理后的项目大小
echo ""
echo "📊 清理后项目大小："
du -sh . 2>/dev/null || echo "无法计算项目大小"

echo ""
echo "🎉 项目清理完成！"
echo "💡 建议运行以下命令重新生成必要的文件："
echo "   npm install          # 重新安装依赖"
echo "   npm test             # 重新生成测试覆盖率"
echo "   npm run build        # 重新构建项目" 