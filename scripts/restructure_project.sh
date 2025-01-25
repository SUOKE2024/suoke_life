#!/bin/bash

# 根据 .cursorrules 创建目录结构
mkdir -p features/user/lib/pages
mkdir -p features/user/lib/providers
mkdir -p features/user/lib/widgets
mkdir -p features/user/test

mkdir -p features/home/lib/pages
mkdir -p features/home/lib/widgets
mkdir -p features/home/lib/providers
mkdir -p features/home/test

mkdir -p features/suoke/lib/pages
mkdir -p features/suoke/lib/widgets
mkdir -p features/suoke/lib/providers
mkdir -p features/suoke/test

mkdir -p features/explore/lib/pages
mkdir -p features/explore/lib/widgets
mkdir -p features/explore/lib/providers
mkdir -p features/explore/test

mkdir -p features/life/lib/pages
mkdir -p features/life/lib/widgets
mkdir -p features/life/lib/providers
mkdir -p features/life/test

mkdir -p features/profile/lib/pages
mkdir -p features/profile/lib/widgets
mkdir -p features/profile/lib/providers
mkdir -p features/profile/test

# 根据 .cursorrules 移动测试文件
mkdir -p test/features/home/pages
mkdir -p test/features/home/providers
mkdir -p test/features/home/services
mkdir -p test/features/suoke/pages
mkdir -p test/features/suoke/providers
mkdir -p test/features/suoke/services
mkdir -p test/features/explore/pages
mkdir -p test/features/explore/providers
mkdir -p test/features/explore/services
mkdir -p test/features/life/pages
mkdir -p test/features/life/providers
mkdir -p test/features/life/services
mkdir -p test/features/profile/pages
mkdir -p test/features/profile/providers
mkdir -p test/features/profile/services
mkdir -p test/features/user/pages
mkdir -p test/features/user/providers
mkdir -p test/features/user/services

# 清理无用文件和目录
rm -rf ios/LocalPods
rm -rf ios/Pods
rm -rf ios/Runner.xcworkspace
rm -rf ios/Reachability.swift-5.2.4
rm -rf ios/Try
rm -f ios/Try.h
rm -f ios/Try.podspec
rm -f ios/Try.swift
rm -f ios/chat_input.dart
rm -rf ios/flutter_framework
rm -f ios/ios.iml
rm -f ios/module.modulemap
rm -f ios/setup_flutter.sh
rm -f ios/setup_reachability.sh
rm -f test/widget_test.dart
rm -rf file_picker
rm -f github_actions.yaml
# rm -f gitignore # 建议保留 .gitignore 文件
rm -rf linux
rm -rf macos
rm -rf windows
rm -f nginx.conf
rm -f scripts/api_docs.md
rm -f scripts/dependency_analyzer.dart
rm -f scripts/fix_pubspec_versions.dart
rm -f scripts/move_files.sh
rm -f scripts/move_tests.sh
rm -f scripts/pubspec.lock
rm -f scripts/pubspec.yaml
rm -f scripts/remove_injectable.sh
rm -rf scripts/tools
rm -f suoke_life_app.iml
rm -rf test/build.yaml
rm -rf test/config
rm -rf test/core
rm -f test/flutter_test_config.dart
rm -rf test/helpers
rm -rf test/integration_test
rm -f test/mockito_test.dart
rm -rf test/mocks
rm -f test/mocks.dart
rm -f test/mocks.mocks.dart
rm -f test/simple_test.dart
rm -rf web

echo "项目结构调整和清理完成！" 