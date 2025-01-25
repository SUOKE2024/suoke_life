#!/bin/bash

echo "清理 iOS 构建环境..."

# 删除 Pods 相关文件
cd ios
rm -rf Pods
rm -rf Podfile.lock
rm -rf .symlinks
rm -rf Flutter/Flutter.podspec

# 清理 CocoaPods 缓存
pod cache clean --all
pod repo remove trunk
pod setup

# 更新 CocoaPods 规范
pod repo update

# 返回项目根目录
cd ..

# 清理 Flutter
flutter clean
flutter pub get

echo "清理完成!" 