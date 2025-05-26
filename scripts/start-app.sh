#!/bin/bash

# 索克生活应用启动脚本
# 用于快速启动React Native应用

echo "🚀 启动索克生活应用..."

# 检查参数
PLATFORM=${1:-ios}

# 清理缓存
echo "🧹 清理缓存..."
npx react-native start --reset-cache &

# 等待Metro服务器启动
echo "⏳ 等待Metro服务器启动..."
sleep 5

# 根据平台启动应用
if [ "$PLATFORM" = "android" ]; then
    echo "📱 在Android设备上启动应用..."
    npx react-native run-android
elif [ "$PLATFORM" = "ios" ]; then
    echo "📱 在iOS设备上启动应用..."
    npx react-native run-ios
else
    echo "❌ 不支持的平台: $PLATFORM"
    echo "支持的平台: ios, android"
    exit 1
fi

echo "✅ 应用启动完成！" 