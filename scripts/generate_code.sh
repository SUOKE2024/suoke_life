#!/bin/bash

# 清理 core 模块
cd libs/core
echo "Cleaning core module..."
flutter clean
rm -rf .dart_tool
rm -rf build
find . -name "*.freezed.dart" -type f -delete
find . -name "*.g.dart" -type f -delete
find . -name "*.mocks.dart" -type f -delete

# 更新依赖并生成代码
echo "Updating dependencies..."
flutter pub get

echo "Generating code..."
dart run build_runner build --delete-conflicting-outputs

cd ../..

echo "Done!" 