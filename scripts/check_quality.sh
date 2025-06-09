#!/bin/bash
# 代码质量检查脚本

echo "🔍 开始代码质量检查..."

# Python代码检查
echo "🐍 检查Python代码..."
find . -name "*.py" -not -path "./venv/*" -not -path "./.git/*" | head -10 | xargs python3 -m py_compile

# TypeScript代码检查
echo "📝 检查TypeScript代码..."
if command -v npx &> /dev/null; then
    npx tsc --noEmit --skipLibCheck
fi

# ESLint检查
echo "🔧 运行ESLint..."
if command -v npx &> /dev/null; then
    npx eslint src/ --ext .ts,.tsx,.js,.jsx --max-warnings 0 || echo "⚠️ ESLint发现问题"
fi

# 检查包依赖
echo "📦 检查包依赖..."
npm audit --audit-level moderate || echo "⚠️ 发现安全漏洞"

echo "✅ 代码质量检查完成"
