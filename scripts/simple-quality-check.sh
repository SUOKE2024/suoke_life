#!/bin/bash

# 索克生活项目简化代码质量检查脚本

echo "🎯 开始代码质量检查..."

# 运行ESLint检查和修复
echo "📝 运行ESLint检查..."
npm run lint -- --fix

# 检查TypeScript类型
echo "🔍 检查TypeScript类型..."
npx tsc --noEmit

# 运行测试
echo "🧪 运行测试..."
npm test -- --passWithNoTests --watchAll=false

# 分析代码复杂度
echo "📊 分析代码复杂度..."
echo "总代码行数: $(find src -name "*.ts" -o -name "*.tsx" | xargs wc -l | tail -1 | awk '{print $1}')"
echo "总文件数: $(find src -name "*.ts" -o -name "*.tsx" | wc -l)"

# 检查项目大小
echo "💾 项目大小分析..."
echo "项目总大小: $(du -sh . | cut -f1)"
echo "源代码大小: $(du -sh src | cut -f1)"

echo "✅ 代码质量检查完成！" 