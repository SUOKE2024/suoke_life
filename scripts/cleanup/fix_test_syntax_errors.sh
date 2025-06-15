#!/bin/bash

# 修复测试文件语法错误脚本
# 专门修复import语句和describe函数的语法错误

set -e

echo "🔧 开始修复测试文件语法错误..."

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "📁 项目根目录: $PROJECT_ROOT"

# 修复缺失引号的import语句
echo "📋 修复import语句的缺失引号..."
find . -name "*.test.ts" -o -name "*.test.tsx" | while read file; do
    if [ -f "$file" ]; then
        # 修复import语句缺失的结束引号
        sed -i.bak 's/from "\([^"]*\);$/from "\1";/g' "$file"
        sed -i.bak 's/from "\([^"]*\)$/from "\1";/g' "$file"
        
        # 修复describe函数的语法错误
        sed -i.bak 's/describe("\([^"]*\)", (); =>/describe("\1", () =>/g' "$file"
        sed -i.bak 's/beforeEach((); =>/beforeEach(() =>/g' "$file"
        sed -i.bak 's/afterEach((); =>/afterEach(() =>/g' "$file"
        sed -i.bak 's/test("\([^"]*\)", (); =>/test("\1", () =>/g' "$file"
        sed -i.bak 's/it("\([^"]*\)", (); =>/it("\1", () =>/g' "$file"
        
        # 删除备份文件
        rm -f "$file.bak" 2>/dev/null || true
        
        echo "✅ 修复: $file"
    fi
done

echo "🔧 修复完成！"

# 验证修复效果
echo "📊 验证修复效果..."
SYNTAX_ERRORS=$(find . -name "*.test.ts" -o -name "*.test.tsx" | xargs grep -l 'from "[^"]*;$' 2>/dev/null | wc -l || echo "0")
echo "剩余语法错误文件数: $SYNTAX_ERRORS"

if [ "$SYNTAX_ERRORS" -eq 0 ]; then
    echo "🎉 所有测试文件语法错误已修复！"
else
    echo "⚠️  仍有 $SYNTAX_ERRORS 个文件需要手动检查"
fi 