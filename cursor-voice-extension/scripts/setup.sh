#!/bin/bash

# Cursor Voice Extension 自动安装脚本
# 支持 macOS, Linux, Windows (Git Bash)

set -e

echo "🚀 开始安装 Cursor Voice Extension..."

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 错误：未找到 Node.js"
    echo "请先安装 Node.js: https://nodejs.org/"
    exit 1
fi

# 检查 npm
if ! command -v npm &> /dev/null; then
    echo "❌ 错误：未找到 npm"
    exit 1
fi

echo "✅ Node.js 和 npm 已安装"

# 检查 Node.js 版本
NODE_VERSION=$(node -v | cut -d'v' -f2)
REQUIRED_VERSION="16.0.0"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$NODE_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ 错误：Node.js 版本过低 (当前: $NODE_VERSION, 需要: >= $REQUIRED_VERSION)"
    exit 1
fi

echo "✅ Node.js 版本检查通过"

# 安装依赖
echo "📦 安装依赖包..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败"
    exit 1
fi

echo "✅ 依赖安装完成"

# 编译 TypeScript
echo "🔨 编译 TypeScript..."
npm run compile

if [ $? -ne 0 ]; then
    echo "❌ 编译失败"
    exit 1
fi

echo "✅ 编译完成"

# 检查是否安装了 vsce
if ! command -v vsce &> /dev/null; then
    echo "📦 安装 vsce (VS Code Extension Manager)..."
    npm install -g vsce
fi

# 打包扩展
echo "📦 打包扩展..."
vsce package

if [ $? -ne 0 ]; then
    echo "❌ 打包失败"
    exit 1
fi

echo "✅ 扩展打包完成"

# 查找生成的 .vsix 文件
VSIX_FILE=$(find . -name "*.vsix" -type f | head -n1)

if [ -z "$VSIX_FILE" ]; then
    echo "❌ 未找到 .vsix 文件"
    exit 1
fi

echo "🎉 安装完成！"
echo ""
echo "📁 扩展文件: $VSIX_FILE"
echo ""
echo "🔧 下一步操作："
echo "1. 打开 Cursor IDE"
echo "2. 按 Ctrl+Shift+P (Mac: Cmd+Shift+P)"
echo "3. 输入 'Extensions: Install from VSIX'"
echo "4. 选择文件: $VSIX_FILE"
echo ""
echo "或者运行开发模式："
echo "1. 在 Cursor 中打开此项目文件夹"
echo "2. 按 F5 启动扩展开发主机"
echo ""
echo "📖 详细说明请查看 INSTALLATION_GUIDE.md"
echo ""
echo "🎤 享受语音编程的乐趣！" 