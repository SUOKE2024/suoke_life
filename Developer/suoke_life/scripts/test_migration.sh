#!/bin/bash
set -e

# 移动位置
cd "$(dirname "$0")/.."
ROOT_DIR=$(pwd)

echo "===== 测试迁移是否成功 ====="

# 测试Go服务
echo "测试API网关服务..."
cd "$ROOT_DIR/go_services/api-gateway"
if [ -f "bin/api-gateway" ]; then
    echo "API网关服务构建成功"
else
    echo "API网关服务构建失败"
    exit 1
fi

echo "测试认证服务..."
cd "$ROOT_DIR/go_services/auth-service"
if [ -f "bin/auth-service" ]; then
    echo "认证服务构建成功"
else
    echo "认证服务构建失败"
    exit 1
fi

# 测试Rust模块
echo "测试Rust舌像分析模块..."
cd "$ROOT_DIR/rust_modules/tongue_analysis"
cargo test --quiet -- --nocapture

# 测试Flutter FFI绑定
echo "测试Flutter桥接文件..."
cd "$ROOT_DIR"
if [ -f "lib/core/native/tongue_analysis_bridge.dart" ]; then
    echo "Flutter桥接文件创建成功"
else
    echo "Flutter桥接文件创建失败"
    exit 1
fi

echo "===== 测试完成，迁移成功 =====" 