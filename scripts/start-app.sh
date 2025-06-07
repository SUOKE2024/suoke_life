#!/bin/bash

# 索克生活应用启动脚本
# 支持iOS和Android平台

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    # 检查Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js 未安装，请先安装 Node.js"
        exit 1
    fi
    
    # 检查npm
    if ! command -v npm &> /dev/null; then
        log_error "npm 未安装，请先安装 npm"
        exit 1
    fi
    
    # 检查React Native CLI
    if ! command -v npx &> /dev/null; then
        log_error "npx 未安装，请先安装 npx"
        exit 1
    fi
    
    log_success "依赖检查完成"
}

# 清理缓存
clean_cache() {
    log_info "清理缓存..."
    
    # 清理Metro缓存
    npx react-native start --reset-cache &
    METRO_PID=$!
    sleep 2
    kill $METRO_PID 2>/dev/null || true
    
    # 清理npm缓存
    npm cache clean --force 2>/dev/null || true
    
    log_success "缓存清理完成"
}

# 安装依赖
install_dependencies() {
    log_info "检查并安装依赖..."
    
    if [ ! -d "node_modules" ] || [ ! -f "node_modules/.package-lock.json" ]; then
        log_info "安装npm依赖..."
        npm install
    else
        log_info "依赖已存在，跳过安装"
    fi
    
    log_success "依赖安装完成"
}

# 启动Metro服务器
start_metro() {
    log_info "启动Metro服务器..."
    
    # 检查端口8081是否被占用
    if lsof -Pi :8081 -sTCP:LISTEN -t >/dev/null ; then
        log_warning "端口8081已被占用，尝试终止现有进程..."
        lsof -ti:8081 | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    # 启动Metro
    npx react-native start --reset-cache &
    METRO_PID=$!
    
    # 等待Metro启动
    log_info "等待Metro服务器启动..."
    sleep 5
    
    # 检查Metro是否成功启动
    if ! lsof -Pi :8081 -sTCP:LISTEN -t >/dev/null ; then
        log_error "Metro服务器启动失败"
        exit 1
    fi
    
    log_success "Metro服务器启动成功 (PID: $METRO_PID)"
    echo $METRO_PID > .metro.pid
}

# 启动iOS应用
start_ios() {
    log_info "启动iOS应用..."
    
    # 检查Xcode
    if ! command -v xcodebuild &> /dev/null; then
        log_error "Xcode 未安装，无法启动iOS应用"
        exit 1
    fi
    
    # 检查iOS模拟器
    if ! command -v xcrun &> /dev/null; then
        log_error "iOS模拟器工具未找到"
        exit 1
    fi
    
    # 安装iOS依赖
    if [ -d "ios" ]; then
        log_info "安装iOS依赖..."
        cd ios
        if [ -f "Podfile" ]; then
            if command -v pod &> /dev/null; then
                pod install
            else
                log_warning "CocoaPods 未安装，跳过pod install"
            fi
        fi
        cd ..
    fi
    
    # 启动iOS应用
    npx react-native run-ios &
    IOS_PID=$!
    
    log_success "iOS应用启动中..."
    echo $IOS_PID > .ios.pid
}

# 启动Android应用
start_android() {
    log_info "启动Android应用..."
    
    # 检查Android SDK
    if [ -z "$ANDROID_HOME" ] && [ -z "$ANDROID_SDK_ROOT" ]; then
        log_error "Android SDK 未配置，请设置 ANDROID_HOME 或 ANDROID_SDK_ROOT 环境变量"
        exit 1
    fi
    
    # 检查ADB
    if ! command -v adb &> /dev/null; then
        log_error "ADB 未找到，请确保Android SDK已正确安装"
        exit 1
    fi
    
    # 检查设备/模拟器
    DEVICES=$(adb devices | grep -v "List of devices" | grep -v "^$" | wc -l)
    if [ $DEVICES -eq 0 ]; then
        log_warning "未检测到Android设备或模拟器，请启动Android模拟器或连接设备"
    fi
    
    # 启动Android应用
    npx react-native run-android &
    ANDROID_PID=$!
    
    log_success "Android应用启动中..."
    echo $ANDROID_PID > .android.pid
}

# 显示帮助信息
show_help() {
    echo "索克生活应用启动脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  ios        启动iOS应用"
    echo "  android    启动Android应用"
    echo "  metro      仅启动Metro服务器"
    echo "  clean      清理缓存后启动"
    echo "  help       显示此帮助信息"
    echo ""
    echo "如果不指定平台，将启动Metro服务器并提示选择平台"
}

# 主函数
main() {
    log_info "索克生活应用启动脚本"
    log_info "========================"
    
    # 检查参数
    PLATFORM=${1:-""}
    CLEAN_FLAG=${2:-""}
    
    case $PLATFORM in
        "help"|"-h"|"--help")
            show_help
            exit 0
            ;;
        "clean")
            CLEAN_FLAG="clean"
            PLATFORM=""
            ;;
    esac
    
    # 检查依赖
    check_dependencies
    
    # 清理缓存（如果需要）
    if [ "$CLEAN_FLAG" = "clean" ] || [ "$2" = "clean" ]; then
        clean_cache
    fi
    
    # 安装依赖
    install_dependencies
    
    # 启动Metro服务器
    start_metro
    
    # 根据平台启动应用
    case $PLATFORM in
        "ios")
            start_ios
            ;;
        "android")
            start_android
            ;;
        "metro")
            log_success "Metro服务器已启动，请在另一个终端中运行 'npx react-native run-ios' 或 'npx react-native run-android'"
            ;;
        "")
            log_info "Metro服务器已启动"
            log_info "请选择要启动的平台："
            log_info "  - iOS: npm run app:ios"
            log_info "  - Android: npm run app:android"
            log_info "  - 或者在另一个终端中运行:"
            log_info "    npx react-native run-ios"
            log_info "    npx react-native run-android"
            ;;
        *)
            log_error "未知平台: $PLATFORM"
            show_help
            exit 1
            ;;
    esac
    
    log_success "应用启动完成！"
    log_info "按 Ctrl+C 停止服务"
    
    # 等待用户中断
    if [ "$PLATFORM" != "metro" ] && [ "$PLATFORM" != "" ]; then
        wait
    fi
}

# 清理函数
cleanup() {
    log_info "正在停止服务..."
    
    # 停止Metro
    if [ -f ".metro.pid" ]; then
        METRO_PID=$(cat .metro.pid)
        kill $METRO_PID 2>/dev/null || true
        rm -f .metro.pid
    fi
    
    # 停止iOS
    if [ -f ".ios.pid" ]; then
        IOS_PID=$(cat .ios.pid)
        kill $IOS_PID 2>/dev/null || true
        rm -f .ios.pid
    fi
    
    # 停止Android
    if [ -f ".android.pid" ]; then
        ANDROID_PID=$(cat .android.pid)
        kill $ANDROID_PID 2>/dev/null || true
        rm -f .android.pid
    fi
    
    log_success "服务已停止"
    exit 0
}

# 设置信号处理
trap cleanup SIGINT SIGTERM

# 运行主函数
main "$@" 