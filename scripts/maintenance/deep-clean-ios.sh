#!/bin/bash

# iOS 深度清理脚本
# 解决 PIF 传输会话问题和其他构建问题

echo "🧹 开始 iOS 深度清理..."

# 检查是否在项目根目录
if [ ! -f "package.json" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

# 1. 关闭所有 Xcode 进程
echo "🔄 关闭 Xcode 进程..."
pkill -f Xcode || true
pkill -f xcodebuild || true
pkill -f xcrun || true

# 等待进程完全关闭
sleep 3

# 2. 清理 Xcode 缓存和派生数据
echo "🗑️  清理 Xcode 缓存..."
rm -rf ~/Library/Developer/Xcode/DerivedData/
rm -rf ~/Library/Caches/com.apple.dt.Xcode/
rm -rf ~/Library/Developer/Xcode/iOS\ DeviceSupport/*/Symbols/System/Library/Caches/

# 3. 清理项目构建文件
echo "📁 清理项目构建文件..."
cd ios
rm -rf build/
rm -rf .xcode.env.local
rm -rf Pods/
rm -rf SuokeLife.xcworkspace/xcuserdata/
rm -rf SuokeLife.xcodeproj/xcuserdata/
rm -rf SuokeLife.xcodeproj/project.xcworkspace/xcuserdata/

# 4. 清理 CocoaPods 缓存
echo "🍫 清理 CocoaPods 缓存..."
pod cache clean --all
pod deintegrate

# 5. 清理 React Native 缓存
echo "⚛️  清理 React Native 缓存..."
cd ..
rm -rf node_modules/
npm cache clean --force
rm -rf ~/.npm/_cacache/

# 6. 清理 Metro 缓存
echo "🚇 清理 Metro 缓存..."
rm -rf /tmp/metro-*
rm -rf /tmp/react-*
npx react-native start --reset-cache &
sleep 2
pkill -f "react-native start" || true

# 7. 重新安装依赖
echo "📦 重新安装依赖..."
npm install

# 8. 重新安装 Pods
echo "🍫 重新安装 Pods..."
cd ios
pod install --repo-update

# 9. 清理系统临时文件
echo "🧽 清理系统临时文件..."
sudo rm -rf /tmp/com.apple.dt.XcodeBuildService.*
sudo rm -rf /tmp/com.apple.CoreSimulator.*

echo ""
echo "✅ iOS 深度清理完成！"
echo ""
echo "📌 接下来的步骤："
echo "1. 打开 Xcode: open ios/SuokeLife.xcworkspace"
echo "2. 在 Xcode 中选择 Product -> Clean Build Folder"
echo "3. 运行项目: npm run ios"
echo ""
echo "🔧 如果仍有 Hermes 警告，请在 Xcode 中："
echo "   - 选择项目 -> Build Phases"
echo "   - 找到 '[CP-User] [Hermes] Replace Hermes...' 脚本"
echo "   - 取消勾选 'Based on dependency analysis'" 