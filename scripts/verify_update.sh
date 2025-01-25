#!/bin/bash

echo "Verifying project updates..."

# 1. 检查路由生成
echo "Checking routes..."
if [ -f "lib/app/core/router/app_router.gr.dart" ]; then
    echo "✓ Routes generated successfully"
else 
    echo "✗ Routes generation failed"
    exit 1
fi

# 2. 检查环境配置生成
echo "Checking env config..."
if [ -f "lib/app/core/env/env_config.g.dart" ]; then
    echo "✓ Env config generated successfully"
else
    echo "✗ Env config generation failed"
    exit 1
fi

# 3. 运行测试
echo "Running tests..."
flutter test test/navigation/router_test.dart

echo "Verification complete!" 