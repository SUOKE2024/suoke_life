#!/bin/bash
# 自动修复脚本

echo "🔧 开始自动修复..."

# 修复Python代码格式
echo "🐍 修复Python代码格式..."
if command -v black &> /dev/null; then
    find . -name "*.py" -not -path "./venv/*" -not -path "./.git/*" | head -20 | xargs black
fi

if command -v isort &> /dev/null; then
    find . -name "*.py" -not -path "./venv/*" -not -path "./.git/*" | head -20 | xargs isort
fi

# 修复TypeScript/JavaScript代码格式
echo "📝 修复TypeScript代码格式..."
if command -v npx &> /dev/null; then
    npx prettier --write "src/**/*.{ts,tsx,js,jsx}" || echo "⚠️ Prettier修复失败"
fi

# 修复ESLint问题
echo "🔧 修复ESLint问题..."
if command -v npx &> /dev/null; then
    npx eslint src/ --ext .ts,.tsx,.js,.jsx --fix || echo "⚠️ ESLint自动修复失败"
fi

echo "✅ 自动修复完成"
