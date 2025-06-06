#!/bin/bash

# 修复测试文件中的常见问题
echo "🔧 修复测试文件中的问题..."

# 1. 修复重复导入问题
echo "修复重复导入..."
find src -name "*.test.ts*" -exec sed -i '' '/^import.*from.*$/N;s/\(import.*from.*\)\n\(import.*from.*\)/\1/' {} \;

# 2. 修复语法错误的测试文件
echo "修复语法错误..."
find services -name "*.test.ts" -exec sed -i '' 's/test(/test("/g' {} \;
find services -name "*.test.ts" -exec sed -i '' 's/", async/", async/g' {} \;
find services -name "*.test.ts" -exec sed -i '' 's/{;/{/g' {} \;
find services -name "*.test.ts" -exec sed -i '' 's/,$/,/g' {} \;

# 3. 修复缺少依赖的问题
echo "安装缺少的依赖..."
cd services/medical-resource-service && pip install watchdog || true
cd ../..

echo "✅ 测试文件修复完成" 