#!/bin/bash

# 快速修复 iOS 依赖图计算错误
# 解决 "unable to initiate PIF transfer session" 错误

echo "🔧 快速修复 iOS 依赖图计算错误..."

# 1. 关闭 Xcode 和模拟器
echo "🛑 关闭 Xcode 和模拟器..."
killall Xcode 2>/dev/null || true
killall Simulator 2>/dev/null || true
sleep 2

# 2. 清理关键缓存
echo "🧹 清理关键缓存..."
rm -rf ~/Library/Developer/Xcode/DerivedData/*
rm -rf ~/Library/Caches/com.apple.dt.Xcode/*

# 3. 进入 iOS 目录
cd ios

# 4. 清理 iOS 构建文件
echo "🧹 清理 iOS 构建文件..."
rm -rf build/
rm -rf Pods/
rm -f Podfile.lock

# 5. 重新安装 Pods
echo "📦 重新安装 CocoaPods..."
pod install --clean-install

echo "✅ 快速修复完成！"
echo "📱 现在可以打开 Xcode 项目了："
echo "   xed SuokeLife.xcworkspace" 