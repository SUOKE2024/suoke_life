#!/bin/bash
set -e

# 移动位置
cd "$(dirname "$0")/.."
ROOT_DIR=$(pwd)

echo "===== 开始索克生活应用迁移工作 ====="

# 第1步：构建Rust模块
echo "构建Rust舌像分析模块..."
cd "$ROOT_DIR/rust_modules/tongue_analysis"
cargo build --release
mkdir -p "$ROOT_DIR/android/app/src/main/jniLibs/arm64-v8a"
mkdir -p "$ROOT_DIR/android/app/src/main/jniLibs/armeabi-v7a"
mkdir -p "$ROOT_DIR/android/app/src/main/jniLibs/x86"
mkdir -p "$ROOT_DIR/android/app/src/main/jniLibs/x86_64"
mkdir -p "$ROOT_DIR/ios/Frameworks"
mkdir -p "$ROOT_DIR/macos/Frameworks"

# 此处应复制平台特定的库文件（在实际设备上构建时需要真实构建）
# 本演示脚本仅作示例

# 第2步：构建Go服务
echo "构建Go服务..."
cd "$ROOT_DIR/go_services"

echo "构建API网关..."
cd "$ROOT_DIR/go_services/api-gateway"
mkdir -p bin
go build -o bin/api-gateway ./cmd

echo "构建认证服务..."
cd "$ROOT_DIR/go_services/auth-service"
mkdir -p bin
go build -o bin/auth-service ./cmd

# 第3步：安装Flutter依赖
echo "安装Flutter依赖..."
cd "$ROOT_DIR"
flutter pub get

# 第4步：生成Flutter代码
echo "生成Flutter代码..."
cd "$ROOT_DIR"
flutter pub run build_runner build --delete-conflicting-outputs

echo "===== 迁移工作完成 =====" 