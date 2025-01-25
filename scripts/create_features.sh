#!/bin/bash

# 创建 features 目录
FEATURES=("welcome" "login" "home" "suoke" "explore" "life" "profile")

for feature in "${FEATURES[@]}"; do
  # 创建目录结构
  mkdir -p "features/$feature/lib/pages"
  mkdir -p "features/$feature/lib/widgets"
  mkdir -p "features/$feature/lib/providers"
  mkdir -p "features/$feature/test"

  # 创建 pubspec.yaml
  cat > "features/$feature/pubspec.yaml" << EOF
name: features_$feature
description: Feature module for $feature
version: 0.0.1
publish_to: none

environment:
  sdk: ">=3.0.0 <4.0.0"
  flutter: ">=3.10.0"

dependencies:
  flutter:
    sdk: flutter
  core:
    path: ../../libs/core
  ui_components:
    path: ../../libs/ui_components

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^3.0.0

flutter:
  uses-material-design: true
EOF
done

# 移动现有文件到新目录（如果存在）
for feature in "${FEATURES[@]}"; do
  if [ -d "features/$feature" ]; then
    # 移动现有文件到新目录
    mv "features/$feature/lib" "features/features_$feature/" 2>/dev/null || true
    mv "features/$feature/test" "features/features_$feature/" 2>/dev/null || true
    # 删除旧目录
    rm -rf "features/$feature"
  fi
done 