#!/bin/bash

# 代码质量检查脚本
echo "🔍 运行代码质量检查..."

# TypeScript类型检查
echo "检查TypeScript类型..."
npx tsc --noEmit --skipLibCheck

# ESLint检查
echo "运行ESLint检查..."
npx eslint src --ext .ts,.tsx,.js,.jsx

# 运行测试
echo "运行测试..."
npm test -- --passWithNoTests

# 生成报告
echo "✅ 代码质量检查完成"
