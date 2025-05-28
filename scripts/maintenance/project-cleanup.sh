#!/bin/bash

# 索克生活项目清理脚本
# 用于清理项目的缓存、构建文件和冗余文件

echo "🧹 开始索克生活项目清理..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数：打印带颜色的消息
print_step() {
    echo -e "${BLUE}🔄 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 1. 杀死占用端口的进程
print_step "清理占用的端口..."
lsof -ti:8081 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
print_success "端口清理完成"

# 2. 清理Node.js相关
print_step "清理Node.js缓存和依赖..."
rm -rf node_modules package-lock.json 2>/dev/null || true
npm cache clean --force 2>/dev/null || true
print_success "Node.js清理完成"

# 3. 清理iOS构建文件
print_step "清理iOS构建文件..."
rm -rf ios/build ios/DerivedData 2>/dev/null || true
rm -rf ios/Pods ios/Podfile.lock 2>/dev/null || true
print_success "iOS构建文件清理完成"

# 4. 清理Android构建文件
print_step "清理Android构建文件..."
rm -rf android/app/build android/.gradle 2>/dev/null || true
print_success "Android构建文件清理完成"

# 5. 清理系统文件
print_step "清理系统临时文件..."
find . -name ".DS_Store" -type f -delete 2>/dev/null || true
find . -name "*.log" -type f -delete 2>/dev/null || true
print_success "系统文件清理完成"

# 6. 清理React Native缓存
print_step "清理React Native缓存..."
npx react-native clean 2>/dev/null || true
rm -rf /tmp/react-* 2>/dev/null || true
rm -rf /tmp/metro-* 2>/dev/null || true
print_success "React Native缓存清理完成"

# 7. 重新安装依赖（可选）
if [ "$1" = "--reinstall" ] || [ "$1" = "-r" ]; then
    print_step "重新安装npm依赖..."
    npm install
    if [ $? -eq 0 ]; then
        print_success "npm依赖安装完成"
    else
        print_error "npm依赖安装失败"
    fi

    print_step "重新安装CocoaPods依赖..."
    cd ios && pod install
    if [ $? -eq 0 ]; then
        print_success "CocoaPods依赖安装完成"
    else
        print_warning "CocoaPods依赖安装失败（可能是网络问题）"
    fi
    cd ..
fi

echo ""
echo "🎉 项目清理完成！"
echo ""
echo "📋 清理内容："
echo "  • 端口占用进程"
echo "  • Node.js缓存和依赖"
echo "  • iOS构建文件和Pods"
echo "  • Android构建文件"
echo "  • 系统临时文件"
echo "  • React Native缓存"

if [ "$1" = "--reinstall" ] || [ "$1" = "-r" ]; then
    echo "  • 重新安装依赖"
fi

echo ""
echo "🚀 下一步："
echo "  1. 运行 'npm start' 启动Metro服务器"
echo "  2. 运行 'npx react-native run-ios' 启动iOS应用"
echo "  3. 或运行 'npx react-native run-android' 启动Android应用"
echo ""
echo "💡 提示："
echo "  • 使用 --reinstall 或 -r 参数可同时重新安装依赖"
echo "  • 如果CocoaPods安装失败，请检查网络连接" 