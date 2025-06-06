#!/bin/bash

# 索克生活 - API Gateway 开发工具脚本
# 提供网关开发和调试的常用工具

set -e

GATEWAY_URL="http://localhost:8000"
GATEWAY_DIR="services/api-gateway"
LOG_DIR="$GATEWAY_DIR/logs"

echo "🛠️  索克生活 API Gateway 开发工具"
echo "================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 显示帮助信息
show_help() {
    echo -e "${BLUE}使用方法:${NC}"
    echo "  $0 [命令]"
    echo ""
    echo -e "${BLUE}可用命令:${NC}"
    echo "  logs          - 查看网关日志"
    echo "  tail          - 实时跟踪网关日志"
    echo "  restart       - 重启网关服务"
    echo "  reload        - 重载网关配置"
    echo "  status        - 查看网关状态"
    echo "  metrics       - 查看性能指标"
    echo "  services      - 查看已注册服务"
    echo "  config        - 查看网关配置"
    echo "  test          - 运行API测试"
    echo "  debug         - 启动调试模式"
    echo "  clean         - 清理日志和缓存"
    echo "  monitor       - 启动监控面板"
    echo "  help          - 显示此帮助信息"
    echo ""
    echo -e "${BLUE}示例:${NC}"
    echo "  $0 logs       # 查看最近的网关日志"
    echo "  $0 tail       # 实时跟踪日志输出"
    echo "  $0 restart    # 重启网关服务"
}

# 查看网关日志
view_logs() {
    echo -e "${BLUE}📋 查看网关日志...${NC}"
    
    if [ -d "$LOG_DIR" ]; then
        echo -e "${GREEN}最近的网关日志:${NC}"
        echo "===================="
        
        # 查找最新的日志文件
        LATEST_LOG=$(find "$LOG_DIR" -name "*.log" -type f -exec ls -t {} + | head -1 2>/dev/null || echo "")
        
        if [ -n "$LATEST_LOG" ]; then
            echo -e "${CYAN}日志文件: $LATEST_LOG${NC}"
            echo ""
            tail -50 "$LATEST_LOG"
        else
            echo -e "${YELLOW}⚠️  未找到日志文件${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  日志目录不存在: $LOG_DIR${NC}"
    fi
}

# 实时跟踪日志
tail_logs() {
    echo -e "${BLUE}📡 实时跟踪网关日志...${NC}"
    echo "按 Ctrl+C 停止跟踪"
    echo ""
    
    if [ -d "$LOG_DIR" ]; then
        # 查找最新的日志文件
        LATEST_LOG=$(find "$LOG_DIR" -name "*.log" -type f -exec ls -t {} + | head -1 2>/dev/null || echo "")
        
        if [ -n "$LATEST_LOG" ]; then
            echo -e "${CYAN}跟踪日志文件: $LATEST_LOG${NC}"
            echo ""
            tail -f "$LATEST_LOG"
        else
            echo -e "${YELLOW}⚠️  未找到日志文件${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  日志目录不存在: $LOG_DIR${NC}"
    fi
}

# 重启网关服务
restart_gateway() {
    echo -e "${BLUE}🔄 重启网关服务...${NC}"
    
    # 停止现有服务
    echo "停止现有网关服务..."
    ./scripts/stop-services.sh > /dev/null 2>&1 || true
    
    sleep 2
    
    # 启动网关服务
    echo "启动网关服务..."
    ./scripts/start-with-gateway.sh
}

# 重载网关配置
reload_config() {
    echo -e "${BLUE}🔄 重载网关配置...${NC}"
    
    RELOAD_URL="$GATEWAY_URL/admin/reload"
    if curl -s -X POST "$RELOAD_URL" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 配置重载成功${NC}"
    else
        echo -e "${RED}❌ 配置重载失败${NC}"
        echo "请检查网关是否正在运行"
    fi
}

# 查看网关状态
view_status() {
    echo -e "${BLUE}📊 网关状态信息...${NC}"
    
    # 基础健康检查
    if curl -s --max-time 5 "$GATEWAY_URL/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 网关运行正常${NC}"
        
        # 获取详细状态
        STATUS=$(curl -s --max-time 5 "$GATEWAY_URL/status" 2>/dev/null || echo "{}")
        echo "📋 状态详情:"
        echo "$STATUS" | python3 -m json.tool 2>/dev/null || echo "$STATUS"
    else
        echo -e "${RED}❌ 网关无法访问${NC}"
    fi
}

# 查看性能指标
view_metrics() {
    echo -e "${BLUE}📈 性能指标...${NC}"
    
    METRICS_URL="$GATEWAY_URL/metrics"
    if curl -s --max-time 5 "$METRICS_URL" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 性能指标可访问${NC}"
        echo ""
        
        METRICS=$(curl -s --max-time 5 "$METRICS_URL" 2>/dev/null || echo "{}")
        echo "📊 性能数据:"
        echo "$METRICS" | python3 -m json.tool 2>/dev/null || echo "$METRICS"
    else
        echo -e "${RED}❌ 性能指标不可访问${NC}"
    fi
}

# 查看已注册服务
view_services() {
    echo -e "${BLUE}🔍 已注册服务...${NC}"
    
    SERVICES_URL="$GATEWAY_URL/services"
    if curl -s --max-time 5 "$SERVICES_URL" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 服务列表可访问${NC}"
        echo ""
        
        SERVICES=$(curl -s --max-time 5 "$SERVICES_URL" 2>/dev/null || echo "[]")
        echo "📋 已注册服务:"
        echo "$SERVICES" | python3 -m json.tool 2>/dev/null || echo "$SERVICES"
    else
        echo -e "${RED}❌ 服务列表不可访问${NC}"
    fi
}

# 查看网关配置
view_config() {
    echo -e "${BLUE}⚙️  网关配置...${NC}"
    
    CONFIG_URL="$GATEWAY_URL/config"
    if curl -s --max-time 5 "$CONFIG_URL" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 配置信息可访问${NC}"
        echo ""
        
        CONFIG=$(curl -s --max-time 5 "$CONFIG_URL" 2>/dev/null || echo "{}")
        echo "⚙️  配置详情:"
        echo "$CONFIG" | python3 -m json.tool 2>/dev/null || echo "$CONFIG"
    else
        echo -e "${RED}❌ 配置信息不可访问${NC}"
    fi
}

# 运行API测试
run_tests() {
    echo -e "${BLUE}🧪 运行API测试...${NC}"
    
    # 测试基础端点
    echo "测试基础端点..."
    
    # 健康检查
    echo -n "  🏥 健康检查: "
    if curl -s --max-time 5 "$GATEWAY_URL/health" > /dev/null 2>&1; then
        echo -e "${GREEN}通过${NC}"
    else
        echo -e "${RED}失败${NC}"
    fi
    
    # 服务列表
    echo -n "  📋 服务列表: "
    if curl -s --max-time 5 "$GATEWAY_URL/services" > /dev/null 2>&1; then
        echo -e "${GREEN}通过${NC}"
    else
        echo -e "${RED}失败${NC}"
    fi
    
    # 配置信息
    echo -n "  ⚙️  配置信息: "
    if curl -s --max-time 5 "$GATEWAY_URL/config" > /dev/null 2>&1; then
        echo -e "${GREEN}通过${NC}"
    else
        echo -e "${RED}失败${NC}"
    fi
    
    # 性能指标
    echo -n "  📈 性能指标: "
    if curl -s --max-time 5 "$GATEWAY_URL/metrics" > /dev/null 2>&1; then
        echo -e "${GREEN}通过${NC}"
    else
        echo -e "${RED}失败${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}✅ API测试完成${NC}"
}

# 启动调试模式
start_debug() {
    echo -e "${BLUE}🐛 启动调试模式...${NC}"
    
    # 停止现有服务
    ./scripts/stop-services.sh > /dev/null 2>&1 || true
    
    echo "启动调试模式的网关..."
    echo "日志级别: DEBUG"
    echo "端口: 8000"
    echo ""
    
    # 进入网关目录并启动调试模式
    cd "$GATEWAY_DIR"
    
    # 设置调试环境变量
    export DEBUG=true
    export LOG_LEVEL=DEBUG
    export PYTHONPATH="${PYTHONPATH}:$(pwd)"
    
    # 启动网关（调试模式）
    python3 -m uvicorn suoke_api_gateway.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
}

# 清理日志和缓存
clean_logs() {
    echo -e "${BLUE}🧹 清理日志和缓存...${NC}"
    
    # 清理日志文件
    if [ -d "$LOG_DIR" ]; then
        echo "清理日志文件..."
        find "$LOG_DIR" -name "*.log" -mtime +7 -delete 2>/dev/null || true
        echo -e "${GREEN}✅ 旧日志文件已清理${NC}"
    fi
    
    # 清理Python缓存
    echo "清理Python缓存..."
    find "$GATEWAY_DIR" -name "*.pyc" -delete 2>/dev/null || true
    find "$GATEWAY_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    echo -e "${GREEN}✅ Python缓存已清理${NC}"
    
    # 清理临时文件
    echo "清理临时文件..."
    find "$GATEWAY_DIR" -name "*.tmp" -delete 2>/dev/null || true
    find "$GATEWAY_DIR" -name "*.temp" -delete 2>/dev/null || true
    echo -e "${GREEN}✅ 临时文件已清理${NC}"
    
    echo -e "${GREEN}🎉 清理完成${NC}"
}

# 启动监控面板
start_monitor() {
    echo -e "${BLUE}📊 启动监控面板...${NC}"
    
    # 检查网关是否运行
    if ! curl -s --max-time 5 "$GATEWAY_URL/health" > /dev/null 2>&1; then
        echo -e "${RED}❌ 网关未运行，请先启动网关${NC}"
        echo "运行: ./scripts/start-with-gateway.sh"
        return 1
    fi
    
    echo -e "${GREEN}✅ 网关运行正常${NC}"
    echo ""
    echo -e "${CYAN}监控面板信息:${NC}"
    echo "🌐 网关地址: $GATEWAY_URL"
    echo "📊 健康检查: $GATEWAY_URL/health"
    echo "📈 性能指标: $GATEWAY_URL/metrics"
    echo "🔍 服务列表: $GATEWAY_URL/services"
    echo "⚙️  配置信息: $GATEWAY_URL/config"
    echo "🎛️  管理面板: $GATEWAY_URL/admin"
    echo ""
    echo -e "${YELLOW}💡 提示: 在浏览器中打开上述地址查看详细信息${NC}"
    
    # 可选：打开浏览器
    if command -v open &> /dev/null; then
        echo ""
        read -p "是否在浏览器中打开管理面板? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            open "$GATEWAY_URL/admin"
        fi
    fi
}

# 主函数
main() {
    case "${1:-help}" in
        "logs")
            view_logs
            ;;
        "tail")
            tail_logs
            ;;
        "restart")
            restart_gateway
            ;;
        "reload")
            reload_config
            ;;
        "status")
            view_status
            ;;
        "metrics")
            view_metrics
            ;;
        "services")
            view_services
            ;;
        "config")
            view_config
            ;;
        "test")
            run_tests
            ;;
        "debug")
            start_debug
            ;;
        "clean")
            clean_logs
            ;;
        "monitor")
            start_monitor
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# 运行主函数
main "$@" 