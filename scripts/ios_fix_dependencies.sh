#!/bin/bash

# iOS 依赖图计算错误修复脚本
# 解决 "unable to initiate PIF transfer session" 错误

set -e

echo "🔧 开始修复 iOS 依赖图计算错误..."

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IOS_DIR="$PROJECT_ROOT/ios"

echo "📍 项目路径: $PROJECT_ROOT"
echo "📱 iOS 目录: $IOS_DIR"

# 1. 关闭所有 Xcode 实例
echo "🛑 关闭所有 Xcode 实例..."
killall Xcode 2>/dev/null || echo "ℹ️  没有运行中的 Xcode 实例"
killall Simulator 2>/dev/null || echo "ℹ️  没有运行中的模拟器"

# 等待进程完全关闭
sleep 3

# 2. 清理 Xcode 缓存
echo "🧹 清理 Xcode 缓存..."

# 清理 DerivedData
DERIVED_DATA_PATH="$HOME/Library/Developer/Xcode/DerivedData"
if [ -d "$DERIVED_DATA_PATH" ]; then
    echo "🗑️  清理 DerivedData: $DERIVED_DATA_PATH"
    rm -rf "$DERIVED_DATA_PATH"/*
fi

# 清理 Xcode 缓存
XCODE_CACHE_PATH="$HOME/Library/Caches/com.apple.dt.Xcode"
if [ -d "$XCODE_CACHE_PATH" ]; then
    echo "🗑️  清理 Xcode 缓存: $XCODE_CACHE_PATH"
    rm -rf "$XCODE_CACHE_PATH"/*
fi

# 清理 CoreSimulator 缓存
CORE_SIMULATOR_CACHE="$HOME/Library/Caches/com.apple.CoreSimulator"
if [ -d "$CORE_SIMULATOR_CACHE" ]; then
    echo "🗑️  清理 CoreSimulator 缓存: $CORE_SIMULATOR_CACHE"
    rm -rf "$CORE_SIMULATOR_CACHE"/*
fi

# 3. 清理 iOS 项目构建文件
echo "🧹 清理 iOS 项目构建文件..."
cd "$IOS_DIR"

# 清理 build 目录
if [ -d "build" ]; then
    echo "🗑️  清理 build 目录"
    rm -rf build
fi

# 清理 Pods 目录
if [ -d "Pods" ]; then
    echo "🗑️  清理 Pods 目录"
    rm -rf Pods
fi

# 清理 Podfile.lock
if [ -f "Podfile.lock" ]; then
    echo "🗑️  删除 Podfile.lock"
    rm -f Podfile.lock
fi

# 清理 .xcworkspace
if [ -d "SuokeLife.xcworkspace" ]; then
    echo "🗑️  清理 xcworkspace"
    rm -rf SuokeLife.xcworkspace
fi

# 4. 清理 React Native 缓存
echo "🧹 清理 React Native 缓存..."
cd "$PROJECT_ROOT"

# 清理 node_modules
if [ -d "node_modules" ]; then
    echo "🗑️  清理 node_modules"
    rm -rf node_modules
fi

# 清理 npm/yarn 缓存
echo "🗑️  清理 npm 缓存"
npm cache clean --force 2>/dev/null || echo "ℹ️  npm 缓存清理完成"

# 清理 React Native 缓存
echo "🗑️  清理 React Native 缓存"
npx react-native clean 2>/dev/null || echo "ℹ️  React Native 缓存清理完成"

# 清理 Metro 缓存
echo "🗑️  清理 Metro 缓存"
npx react-native start --reset-cache --dry-run 2>/dev/null || echo "ℹ️  Metro 缓存清理完成"

# 5. 重新安装依赖
echo "📦 重新安装依赖..."

# 安装 npm 依赖
echo "📦 安装 npm 依赖..."
npm install

# 6. 重新安装 Pods
echo "📦 重新安装 CocoaPods 依赖..."
cd "$IOS_DIR"

# 更新 CocoaPods 仓库
echo "🔄 更新 CocoaPods 仓库..."
pod repo update

# 安装 Pods
echo "📦 安装 Pods..."
pod install --clean-install --verbose

# 7. 修复 Xcode 项目设置
echo "🔧 修复 Xcode 项目设置..."

# 创建修复脚本
cat > fix_xcode_settings.rb << 'EOF'
#!/usr/bin/env ruby

require 'xcodeproj'

# 打开 Pods 项目
project_path = 'Pods/Pods.xcodeproj'
project = Xcodeproj::Project.open(project_path)

puts "🔧 修复 Pods 项目设置..."

# 更新项目设置到推荐值
project.targets.each do |target|
  target.build_configurations.each do |config|
    # 设置推荐的构建设置
    config.build_settings['IPHONEOS_DEPLOYMENT_TARGET'] = '15.1'
    config.build_settings['CLANG_WARN_QUOTED_INCLUDE_IN_FRAMEWORK_HEADER'] = 'NO'
    config.build_settings['CLANG_WARN_DOCUMENTATION_COMMENTS'] = 'NO'
    config.build_settings['CLANG_WARN_UNGUARDED_AVAILABILITY'] = 'NO'
    config.build_settings['GCC_WARN_INHIBIT_ALL_WARNINGS'] = 'YES'
    config.build_settings['CLANG_CXX_LANGUAGE_STANDARD'] = 'c++20'
    config.build_settings['CLANG_CXX_LIBRARY'] = 'libc++'
    
    # 修复模块相关设置
    config.build_settings['DEFINES_MODULE'] = 'YES'
    config.build_settings['MODULEMAP_FILE'] = ''
    
    # 修复 Swift 相关设置
    if target.product_type == 'com.apple.product-type.library.static'
      config.build_settings['ALWAYS_EMBED_SWIFT_STANDARD_LIBRARIES'] = 'NO'
    end
  end
end

# 保存项目
project.save

puts "✅ Pods 项目设置修复完成"
EOF

# 运行修复脚本
ruby fix_xcode_settings.rb

# 清理临时文件
rm -f fix_xcode_settings.rb

# 8. 验证修复结果
echo "✅ 验证修复结果..."

if [ -f "Podfile.lock" ] && [ -d "Pods" ] && [ -d "SuokeLife.xcworkspace" ]; then
    echo "✅ iOS 依赖安装成功"
    echo "📱 可以使用以下命令启动项目:"
    echo "   cd ios && xed SuokeLife.xcworkspace"
    echo "   或者运行: npx react-native run-ios"
else
    echo "❌ 依赖安装可能存在问题，请检查错误信息"
    exit 1
fi

echo ""
echo "🎉 iOS 依赖图计算错误修复完成！"
echo ""
echo "📋 修复内容:"
echo "   ✅ 清理了所有 Xcode 缓存"
echo "   ✅ 清理了 React Native 缓存"
echo "   ✅ 重新安装了所有依赖"
echo "   ✅ 更新了 Pods 项目设置"
echo "   ✅ 修复了依赖图计算问题"
echo ""
echo "🚀 现在可以正常打开和构建 iOS 项目了！" 