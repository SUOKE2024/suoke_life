#!/bin/bash

# iOS 项目设置验证脚本

echo "🔍 验证 SuokeLife iOS 项目设置..."

# 检查必要文件
echo "📁 检查必要文件..."

if [ -f "ios/Podfile" ]; then
    echo "✅ Podfile 存在"
else
    echo "❌ Podfile 不存在"
    exit 1
fi

if [ -f "ios/Podfile.lock" ]; then
    echo "✅ Podfile.lock 存在"
else
    echo "❌ Podfile.lock 不存在"
    exit 1
fi

if [ -d "ios/Pods" ]; then
    echo "✅ Pods 目录存在"
else
    echo "❌ Pods 目录不存在"
    exit 1
fi

if [ -d "ios/SuokeLife.xcworkspace" ]; then
    echo "✅ SuokeLife.xcworkspace 存在"
else
    echo "❌ SuokeLife.xcworkspace 不存在"
    exit 1
fi

# 检查关键依赖
echo ""
echo "📦 检查关键依赖..."

PODS_COUNT=$(find ios/Pods -name "*.podspec" | wc -l)
echo "📊 已安装 Pods 数量: $PODS_COUNT"

# 检查 React Native 版本
if [ -f "package.json" ]; then
    RN_VERSION=$(grep '"react-native"' package.json | sed 's/.*"react-native": "\([^"]*\)".*/\1/')
    echo "⚛️  React Native 版本: $RN_VERSION"
fi

# 检查 Xcode 版本
if command -v xcodebuild &> /dev/null; then
    XCODE_VERSION=$(xcodebuild -version | head -n 1)
    echo "🔨 $XCODE_VERSION"
else
    echo "⚠️  Xcode 未安装或不在 PATH 中"
fi

# 检查 CocoaPods 版本
if command -v pod &> /dev/null; then
    POD_VERSION=$(pod --version)
    echo "🍫 CocoaPods 版本: $POD_VERSION"
else
    echo "⚠️  CocoaPods 未安装"
fi

echo ""
echo "🎯 项目状态总结:"
echo "   ✅ 所有必要文件都存在"
echo "   ✅ CocoaPods 依赖已安装"
echo "   ✅ Xcode workspace 已生成"
echo ""
echo "🚀 可以使用以下命令启动项目:"
echo "   方式1: cd ios && xed SuokeLife.xcworkspace"
echo "   方式2: npx react-native run-ios"
echo ""
echo "📱 如果遇到问题，可以运行修复脚本:"
echo "   ./scripts/quick_ios_fix.sh" 