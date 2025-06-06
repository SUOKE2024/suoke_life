#!/bin/bash

# 索克生活 - API Gateway 健康检查脚本
# 检查网关和所有微服务的健康状态

set -e

GATEWAY_URL="http://localhost:8000"
TIMEOUT=10

echo "🏥 索克生活 API Gateway 健康检查"
echo "================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查网关基础健康状态
check_gateway_health() {
    echo -e "${BLUE}🌐 检查API Gateway基础健康状态...${NC}"
    
    if curl -s --max-time $TIMEOUT "$GATEWAY_URL/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ API Gateway 运行正常${NC}"
        
        # 获取详细健康信息
        HEALTH_INFO=$(curl -s --max-time $TIMEOUT "$GATEWAY_URL/health" 2>/dev/null || echo "{}")
        echo "📊 健康信息: $HEALTH_INFO"
        return 0
    else
        echo -e "${RED}❌ API Gateway 无法访问${NC}"
        return 1
    fi
}

# 检查服务发现
check_service_discovery() {
    echo -e "${BLUE}🔍 检查服务发现...${NC}"
    
    SERVICES_RESPONSE=$(curl -s --max-time $TIMEOUT "$GATEWAY_URL/services" 2>/dev/null || echo "[]")
    
    if [ "$SERVICES_RESPONSE" != "[]" ] && [ "$SERVICES_RESPONSE" != "" ]; then
        echo -e "${GREEN}✅ 服务发现正常${NC}"
        echo "📋 已注册服务: $SERVICES_RESPONSE"
        return 0
    else
        echo -e "${YELLOW}⚠️  服务发现可能异常或无已注册服务${NC}"
        return 1
    fi
}

# 检查各个微服务健康状态
check_microservices() {
    echo -e "${BLUE}🔧 检查微服务健康状态...${NC}"
    
    # 定义要检查的服务列表
    SERVICES=(
        "auth-service"
        "user-service" 
        "health-data-service"
        "agent-services"
        "diagnostic-services"
        "rag-service"
        "blockchain-service"
        "message-bus"
        "medical-resource-service"
        "corn-maze-service"
        "accessibility-service"
        "suoke-bench-service"
    )
    
    HEALTHY_COUNT=0
    TOTAL_COUNT=${#SERVICES[@]}
    
    for service in "${SERVICES[@]}"; do
        echo -n "  🔍 $service: "
        
        HEALTH_URL="$GATEWAY_URL/services/$service/health"
        if curl -s --max-time $TIMEOUT "$HEALTH_URL" > /dev/null 2>&1; then
            echo -e "${GREEN}健康${NC}"
            ((HEALTHY_COUNT++))
        else
            echo -e "${RED}异常${NC}"
        fi
    done
    
    echo ""
    echo "📊 服务健康统计: $HEALTHY_COUNT/$TOTAL_COUNT 个服务健康"
    
    if [ $HEALTHY_COUNT -eq $TOTAL_COUNT ]; then
        echo -e "${GREEN}✅ 所有微服务运行正常${NC}"
        return 0
    elif [ $HEALTHY_COUNT -gt 0 ]; then
        echo -e "${YELLOW}⚠️  部分微服务异常${NC}"
        return 1
    else
        echo -e "${RED}❌ 所有微服务都异常${NC}"
        return 2
    fi
}

# 检查网关性能指标
check_gateway_metrics() {
    echo -e "${BLUE}📈 检查网关性能指标...${NC}"
    
    METRICS_URL="$GATEWAY_URL/metrics"
    if curl -s --max-time $TIMEOUT "$METRICS_URL" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 性能指标可访问${NC}"
        
        # 尝试获取一些基础指标
        METRICS=$(curl -s --max-time $TIMEOUT "$METRICS_URL" 2>/dev/null || echo "{}")
        echo "📊 性能指标: $METRICS"
        return 0
    else
        echo -e "${YELLOW}⚠️  性能指标不可访问${NC}"
        return 1
    fi
}

# 检查网关配置
check_gateway_config() {
    echo -e "${BLUE}⚙️  检查网关配置...${NC}"
    
    CONFIG_URL="$GATEWAY_URL/config"
    if curl -s --max-time $TIMEOUT "$CONFIG_URL" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 网关配置可访问${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  网关配置不可访问${NC}"
        return 1
    fi
}

# 测试API端点
test_api_endpoints() {
    echo -e "${BLUE}🧪 测试关键API端点...${NC}"
    
    # 测试认证端点（不需要认证的）
    echo -n "  🔐 认证服务健康检查: "
    if curl -s --max-time $TIMEOUT "$GATEWAY_URL/api/v1/auth/health" > /dev/null 2>&1; then
        echo -e "${GREEN}正常${NC}"
    else
        echo -e "${RED}异常${NC}"
    fi
    
    # 测试健康数据服务
    echo -n "  💊 健康数据服务健康检查: "
    if curl -s --max-time $TIMEOUT "$GATEWAY_URL/api/v1/health/health" > /dev/null 2>&1; then
        echo -e "${GREEN}正常${NC}"
    else
        echo -e "${RED}异常${NC}"
    fi
    
    # 测试RAG服务
    echo -n "  🧠 RAG服务健康检查: "
    if curl -s --max-time $TIMEOUT "$GATEWAY_URL/api/v1/rag/health" > /dev/null 2>&1; then
        echo -e "${GREEN}正常${NC}"
    else
        echo -e "${RED}异常${NC}"
    fi
}

# 检查网络连接
check_network() {
    echo -e "${BLUE}🌐 检查网络连接...${NC}"
    
    # 检查本地网关端口
    if nc -z localhost 8000 2>/dev/null; then
        echo -e "${GREEN}✅ 端口8000可访问${NC}"
    else
        echo -e "${RED}❌ 端口8000不可访问${NC}"
        return 1
    fi
    
    # 检查DNS解析
    if nslookup localhost > /dev/null 2>&1; then
        echo -e "${GREEN}✅ DNS解析正常${NC}"
    else
        echo -e "${YELLOW}⚠️  DNS解析可能异常${NC}"
    fi
    
    return 0
}

# 生成健康报告
generate_health_report() {
    echo ""
    echo -e "${BLUE}📋 健康检查报告${NC}"
    echo "=================="
    
    local gateway_status=$1
    local services_status=$2
    local metrics_status=$3
    local endpoints_status=$4
    local network_status=$5
    
    echo "🌐 API Gateway: $([ $gateway_status -eq 0 ] && echo -e "${GREEN}正常${NC}" || echo -e "${RED}异常${NC}")"
    echo "🔍 服务发现: $([ $services_status -eq 0 ] && echo -e "${GREEN}正常${NC}" || echo -e "${YELLOW}部分异常${NC}")"
    echo "📈 性能指标: $([ $metrics_status -eq 0 ] && echo -e "${GREEN}正常${NC}" || echo -e "${YELLOW}不可访问${NC}")"
    echo "🧪 API端点: $([ $endpoints_status -eq 0 ] && echo -e "${GREEN}正常${NC}" || echo -e "${YELLOW}部分异常${NC}")"
    echo "🌐 网络连接: $([ $network_status -eq 0 ] && echo -e "${GREEN}正常${NC}" || echo -e "${RED}异常${NC}")"
    
    # 计算总体健康分数
    local total_score=$((gateway_status + services_status + metrics_status + endpoints_status + network_status))
    
    echo ""
    if [ $total_score -eq 0 ]; then
        echo -e "${GREEN}🎉 整体状态: 优秀 (所有检查通过)${NC}"
    elif [ $total_score -le 2 ]; then
        echo -e "${YELLOW}⚠️  整体状态: 良好 (部分检查异常)${NC}"
    else
        echo -e "${RED}❌ 整体状态: 异常 (多项检查失败)${NC}"
    fi
    
    echo ""
    echo "💡 建议:"
    if [ $gateway_status -ne 0 ]; then
        echo "   - 检查API Gateway是否正在运行"
        echo "   - 运行: ./scripts/start-with-gateway.sh"
    fi
    
    if [ $network_status -ne 0 ]; then
        echo "   - 检查网络连接和防火墙设置"
        echo "   - 确保端口8000未被其他程序占用"
    fi
    
    if [ $services_status -ne 0 ]; then
        echo "   - 检查微服务配置和启动状态"
        echo "   - 查看服务日志以获取详细错误信息"
    fi
}

# 主执行流程
main() {
    echo "⏰ 开始时间: $(date)"
    echo ""
    
    # 执行各项检查
    check_network
    network_status=$?
    
    check_gateway_health
    gateway_status=$?
    
    if [ $gateway_status -eq 0 ]; then
        check_service_discovery
        services_status=$?
        
        check_microservices
        microservices_status=$?
        
        check_gateway_metrics
        metrics_status=$?
        
        check_gateway_config
        config_status=$?
        
        test_api_endpoints
        endpoints_status=$?
    else
        services_status=1
        microservices_status=1
        metrics_status=1
        config_status=1
        endpoints_status=1
    fi
    
    # 生成报告
    generate_health_report $gateway_status $services_status $metrics_status $endpoints_status $network_status
    
    echo ""
    echo "⏰ 完成时间: $(date)"
    
    # 返回适当的退出码
    if [ $gateway_status -eq 0 ] && [ $network_status -eq 0 ]; then
        exit 0
    else
        exit 1
    fi
}

# 运行主函数
main "$@" 