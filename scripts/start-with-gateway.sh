#!/bin/bash

# 索克生活 - API Gateway + 前端应用启动脚本
# 用于开发环境同时启动API Gateway和React Native应用

set -e

echo "🚀 启动索克生活 API Gateway + 前端应用"
echo "=================================="

# 检查必要的依赖
check_dependencies() {
    echo "📋 检查依赖..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python3 未安装"
        exit 1
    fi
    
    # 检查Node.js
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js 未安装"
        exit 1
    fi
    
    # 检查npm
    if ! command -v npm &> /dev/null; then
        echo "❌ npm 未安装"
        exit 1
    fi
    
    echo "✅ 依赖检查完成"
}

# 启动API Gateway
start_gateway() {
    echo "🌐 启动API Gateway..."
    
    cd services/api-gateway
    
    # 检查虚拟环境
    if [ ! -d "venv" ]; then
        echo "📦 创建Python虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 安装依赖
    echo "📦 安装Python依赖..."
    pip install -r requirements.txt
    
    # 启动网关服务
    echo "🚀 启动网关服务..."
    python -m suoke_api_gateway.main &
    GATEWAY_PID=$!
    
    cd ../..
    
    echo "✅ API Gateway 已启动 (PID: $GATEWAY_PID)"
}

# 启动前端应用
start_frontend() {
    echo "📱 启动前端应用..."
    
    # 安装依赖
    if [ ! -d "node_modules" ]; then
        echo "📦 安装Node.js依赖..."
        npm install
    fi
    
    # 启动React Native Metro
    echo "🚀 启动Metro bundler..."
    npm start &
    METRO_PID=$!
    
    echo "✅ 前端应用已启动 (PID: $METRO_PID)"
}

# 等待服务启动
wait_for_services() {
    echo "⏳ 等待服务启动..."
    
    # 等待API Gateway
    echo "🔍 检查API Gateway状态..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo "✅ API Gateway 已就绪"
            break
        fi
        
        if [ $i -eq 30 ]; then
            echo "❌ API Gateway 启动超时"
            exit 1
        fi
        
        sleep 2
    done
    
    # 等待Metro
    echo "🔍 检查Metro bundler状态..."
    for i in {1..20}; do
        if curl -s http://localhost:8081/status > /dev/null 2>&1; then
            echo "✅ Metro bundler 已就绪"
            break
        fi
        
        if [ $i -eq 20 ]; then
            echo "⚠️  Metro bundler 可能需要更多时间启动"
            break
        fi
        
        sleep 3
    done
}

# 显示服务信息
show_service_info() {
    echo ""
    echo "🎉 服务启动完成！"
    echo "=================="
    echo "📍 API Gateway:    http://localhost:8000"
    echo "📍 Gateway Health: http://localhost:8000/health"
    echo "📍 Gateway Docs:   http://localhost:8000/docs"
    echo "📍 Metro Bundler:  http://localhost:8081"
    echo ""
    echo "📱 启动移动应用:"
    echo "   iOS:     npm run ios"
    echo "   Android: npm run android"
    echo ""
    echo "🛠️  开发工具:"
    echo "   Gateway监控: 在应用中访问网关监控页面"
    echo "   API文档:     http://localhost:8000/docs"
    echo "   服务状态:    http://localhost:8000/services"
    echo ""
    echo "⚠️  停止服务: Ctrl+C 或运行 ./scripts/stop-services.sh"
}

# 清理函数
cleanup() {
    echo ""
    echo "🛑 停止服务..."
    
    if [ ! -z "$GATEWAY_PID" ]; then
        kill $GATEWAY_PID 2>/dev/null || true
        echo "✅ API Gateway 已停止"
    fi
    
    if [ ! -z "$METRO_PID" ]; then
        kill $METRO_PID 2>/dev/null || true
        echo "✅ Metro bundler 已停止"
    fi
    
    echo "👋 再见！"
    exit 0
}

# 设置信号处理
trap cleanup SIGINT SIGTERM

# 主执行流程
main() {
    check_dependencies
    start_gateway
    sleep 5  # 给网关一些启动时间
    start_frontend
    wait_for_services
    show_service_info
    
    # 保持脚本运行
    echo "🔄 服务运行中... (按 Ctrl+C 停止)"
    while true; do
        sleep 10
        
        # 检查服务是否还在运行
        if ! kill -0 $GATEWAY_PID 2>/dev/null; then
            echo "❌ API Gateway 已停止"
            break
        fi
        
        if ! kill -0 $METRO_PID 2>/dev/null; then
            echo "❌ Metro bundler 已停止"
            break
        fi
    done
    
    cleanup
}

# 运行主函数
main "$@" 