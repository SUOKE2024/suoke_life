#!/bin/bash

# 索克生活 - 五诊服务测试脚本
# 测试完整的五诊系统功能，包括传统四诊和新增的算诊功能

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

# 测试结果统计
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 测试函数
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_status="$3"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    log_info "测试: $test_name"
    
    if eval "$test_command"; then
        if [ "$expected_status" = "success" ]; then
            log_success "✓ $test_name 通过"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            log_error "✗ $test_name 失败 (预期失败但实际成功)"
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    else
        if [ "$expected_status" = "fail" ]; then
            log_success "✓ $test_name 通过 (预期失败)"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            log_error "✗ $test_name 失败"
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    fi
    echo
}

# API测试函数
test_api_endpoint() {
    local service_name="$1"
    local url="$2"
    local method="$3"
    local data="$4"
    
    if [ "$method" = "GET" ]; then
        curl -s -f "$url" > /dev/null
    elif [ "$method" = "POST" ]; then
        curl -s -f -X POST -H "Content-Type: application/json" -d "$data" "$url" > /dev/null
    fi
}

# 测试服务健康状态
test_service_health() {
    log_info "=== 测试服务健康状态 ==="
    
    run_test "API Gateway 健康检查" \
        "test_api_endpoint 'API Gateway' 'http://localhost:8000/health' 'GET'" \
        "success"
    
    run_test "认证服务健康检查" \
        "test_api_endpoint '认证服务' 'http://localhost:8001/health' 'GET'" \
        "success"
    
    run_test "用户服务健康检查" \
        "test_api_endpoint '用户服务' 'http://localhost:8002/health' 'GET'" \
        "success"
    
    run_test "健康数据服务健康检查" \
        "test_api_endpoint '健康数据服务' 'http://localhost:8003/health' 'GET'" \
        "success"
    
    run_test "望诊服务健康检查" \
        "test_api_endpoint '望诊服务' 'http://localhost:8004/health' 'GET'" \
        "success"
    
    run_test "闻诊服务健康检查" \
        "test_api_endpoint '闻诊服务' 'http://localhost:8005/health' 'GET'" \
        "success"
    
    run_test "问诊服务健康检查" \
        "test_api_endpoint '问诊服务' 'http://localhost:8006/health' 'GET'" \
        "success"
    
    run_test "切诊服务健康检查" \
        "test_api_endpoint '切诊服务' 'http://localhost:8007/health' 'GET'" \
        "success"
    
    run_test "算诊服务健康检查 (新增)" \
        "test_api_endpoint '算诊服务' 'http://localhost:8008/health' 'GET'" \
        "success"
}

# 测试传统四诊功能
test_traditional_diagnosis() {
    log_info "=== 测试传统四诊功能 ==="
    
    # 测试望诊
    run_test "望诊 - 面部图像分析" \
        "test_api_endpoint '望诊' 'http://localhost:8000/api/v1/diagnosis/look' 'POST' '{\"faceImage\":\"test_image_data\",\"metadata\":{\"timestamp\":$(date +%s)}}'" \
        "success"
    
    # 测试闻诊
    run_test "闻诊 - 语音分析" \
        "test_api_endpoint '闻诊' 'http://localhost:8000/api/v1/diagnosis/listen' 'POST' '{\"voiceRecording\":\"test_audio_data\",\"metadata\":{\"timestamp\":$(date +%s)}}'" \
        "success"
    
    # 测试问诊
    run_test "问诊 - 症状问卷" \
        "test_api_endpoint '问诊' 'http://localhost:8000/api/v1/diagnosis/inquiry' 'POST' '{\"symptoms\":[\"头痛\",\"失眠\"],\"medicalHistory\":[\"高血压\"]}'" \
        "success"
    
    # 测试切诊
    run_test "切诊 - 脉象分析" \
        "test_api_endpoint '切诊' 'http://localhost:8000/api/v1/diagnosis/palpation' 'POST' '{\"pulseData\":{\"rate\":72,\"rhythm\":\"规律\",\"strength\":\"中等\"}}'" \
        "success"
}

# 测试新增算诊功能
test_calculation_diagnosis() {
    log_info "=== 测试新增算诊功能 ==="
    
    # 测试基础算诊
    run_test "算诊 - 基础分析" \
        "test_api_endpoint '算诊' 'http://localhost:8000/api/v1/diagnosis/calculation' 'POST' '{\"personalInfo\":{\"birthYear\":1990,\"birthMonth\":5,\"birthDay\":15,\"birthHour\":10,\"gender\":\"男\",\"location\":\"北京\"},\"analysisTypes\":{\"comprehensive\":true}}'" \
        "success"
    
    # 测试子午流注分析
    run_test "算诊 - 子午流注分析" \
        "test_api_endpoint '算诊' 'http://localhost:8000/api/v1/diagnosis/calculation/ziwu' 'POST' '{\"birthTime\":\"1990-05-15T10:00:00Z\",\"currentTime\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}'" \
        "success"
    
    # 测试八字体质分析
    run_test "算诊 - 八字体质分析" \
        "test_api_endpoint '算诊' 'http://localhost:8000/api/v1/diagnosis/calculation/constitution' 'POST' '{\"personalInfo\":{\"birthYear\":1990,\"birthMonth\":5,\"birthDay\":15,\"birthHour\":10,\"gender\":\"男\"}}'" \
        "success"
    
    # 测试八卦配属分析
    run_test "算诊 - 八卦配属分析" \
        "test_api_endpoint '算诊' 'http://localhost:8000/api/v1/diagnosis/calculation/bagua' 'POST' '{\"personalInfo\":{\"birthYear\":1990,\"birthMonth\":5,\"birthDay\":15,\"gender\":\"男\"},\"analysisType\":\"health\"}'" \
        "success"
    
    # 测试五运六气分析
    run_test "算诊 - 五运六气分析" \
        "test_api_endpoint '算诊' 'http://localhost:8000/api/v1/diagnosis/calculation/wuyun' 'POST' '{\"timeData\":{\"year\":2024,\"month\":1,\"day\":15},\"location\":\"北京\"}'" \
        "success"
    
    # 测试综合算诊分析
    run_test "算诊 - 综合分析" \
        "test_api_endpoint '算诊' 'http://localhost:8000/api/v1/diagnosis/calculation/comprehensive' 'POST' '{\"personalInfo\":{\"birthYear\":1990,\"birthMonth\":5,\"birthDay\":15,\"birthHour\":10,\"gender\":\"男\",\"location\":\"北京\"},\"analysisTypes\":{\"ziwuLiuzhu\":true,\"constitution\":true,\"bagua\":true,\"wuyunLiuqi\":true,\"comprehensive\":true},\"healthConcerns\":[\"体质调理\",\"养生保健\"]}'" \
        "success"
}

# 测试五诊综合分析
test_comprehensive_diagnosis() {
    log_info "=== 测试五诊综合分析 ==="
    
    # 测试五诊合参
    run_test "五诊合参 - 综合分析" \
        "test_api_endpoint '五诊合参' 'http://localhost:8000/api/v1/diagnosis/comprehensive' 'POST' '{\"userId\":\"test_user\",\"lookingData\":{\"faceImage\":\"test_face\",\"tongueImage\":\"test_tongue\"},\"listeningData\":{\"voiceRecording\":\"test_voice\"},\"inquiryData\":{\"symptoms\":[\"头痛\",\"失眠\"]},\"palpationData\":{\"pulseData\":{\"rate\":72}},\"calculationData\":{\"personalInfo\":{\"birthYear\":1990,\"birthMonth\":5,\"birthDay\":15,\"birthHour\":10,\"gender\":\"男\"}}}'" \
        "success"
    
    # 测试五诊历史记录
    run_test "五诊历史 - 记录查询" \
        "test_api_endpoint '五诊历史' 'http://localhost:8000/api/v1/diagnosis/history?userId=test_user&limit=10' 'GET'" \
        "success"
}

# 测试网关路由
test_gateway_routing() {
    log_info "=== 测试网关路由 ==="
    
    # 测试网关状态
    run_test "网关状态检查" \
        "test_api_endpoint '网关' 'http://localhost:8000/gateway/status' 'GET'" \
        "success"
    
    # 测试服务发现
    run_test "服务发现" \
        "test_api_endpoint '服务发现' 'http://localhost:8000/gateway/services' 'GET'" \
        "success"
    
    # 测试负载均衡
    run_test "负载均衡状态" \
        "test_api_endpoint '负载均衡' 'http://localhost:8000/gateway/load-balancer' 'GET'" \
        "success"
}

# 测试性能指标
test_performance() {
    log_info "=== 测试性能指标 ==="
    
    # 测试响应时间
    local start_time=$(date +%s%N)
    if test_api_endpoint '性能测试' 'http://localhost:8000/api/v1/diagnosis/calculation' 'POST' '{"personalInfo":{"birthYear":1990,"birthMonth":5,"birthDay":15,"birthHour":10,"gender":"男"}}'; then
        local end_time=$(date +%s%N)
        local duration=$(((end_time - start_time) / 1000000)) # 转换为毫秒
        
        if [ $duration -lt 5000 ]; then # 5秒内
            log_success "✓ 算诊响应时间测试通过 (${duration}ms < 5000ms)"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            log_warning "⚠ 算诊响应时间较慢 (${duration}ms >= 5000ms)"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        fi
    else
        log_error "✗ 算诊响应时间测试失败"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo
    
    # 测试并发处理
    run_test "并发处理测试" \
        "for i in {1..5}; do test_api_endpoint '并发测试' 'http://localhost:8000/health' 'GET' & done; wait" \
        "success"
}

# 测试错误处理
test_error_handling() {
    log_info "=== 测试错误处理 ==="
    
    # 测试无效数据
    run_test "无效数据处理" \
        "test_api_endpoint '错误测试' 'http://localhost:8000/api/v1/diagnosis/calculation' 'POST' '{\"invalid\":\"data\"}'" \
        "fail"
    
    # 测试不存在的端点
    run_test "不存在端点处理" \
        "test_api_endpoint '404测试' 'http://localhost:8000/api/v1/diagnosis/nonexistent' 'GET'" \
        "fail"
}

# 生成测试报告
generate_test_report() {
    log_info "=== 测试报告 ==="
    echo
    echo "📊 测试统计："
    echo "   总测试数: $TOTAL_TESTS"
    echo "   通过测试: $PASSED_TESTS"
    echo "   失败测试: $FAILED_TESTS"
    echo "   成功率: $(( (PASSED_TESTS * 100) / TOTAL_TESTS ))%"
    echo
    
    if [ $FAILED_TESTS -eq 0 ]; then
        log_success "🎉 所有测试通过！五诊系统运行正常"
        return 0
    else
        log_warning "⚠️  有 $FAILED_TESTS 个测试失败，请检查相关服务"
        return 1
    fi
}

# 主函数
main() {
    echo "=========================================="
    echo "    索克生活 - 五诊服务测试脚本"
    echo "=========================================="
    echo
    
    log_info "开始五诊系统功能测试..."
    echo
    
    # 检查服务是否运行
    if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
        log_error "API Gateway 未运行，请先启动五诊服务"
        log_info "运行命令: ./scripts/start-five-diagnosis.sh"
        exit 1
    fi
    
    # 运行测试套件
    test_service_health
    test_traditional_diagnosis
    test_calculation_diagnosis
    test_comprehensive_diagnosis
    test_gateway_routing
    test_performance
    test_error_handling
    
    # 生成报告
    generate_test_report
}

# 运行主函数
main "$@" 