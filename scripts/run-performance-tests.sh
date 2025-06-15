#!/bin/bash

# 索克生活项目 - 本地性能测试脚本
# 使用K6进行各种性能测试场景

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
BASE_URL="${BASE_URL:-http://localhost:8000}"
TEST_DURATION="${TEST_DURATION:-5m}"
CONCURRENT_USERS="${CONCURRENT_USERS:-50}"
RESULTS_DIR="performance-results"

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

# 检查K6是否安装
check_k6() {
    if ! command -v k6 &> /dev/null; then
        log_error "K6未安装，请先安装K6"
        log_info "安装方法: https://k6.io/docs/getting-started/installation/"
        exit 1
    fi
    log_success "K6已安装: $(k6 version)"
}

# 检查服务是否运行
check_services() {
    log_info "检查服务状态..."
    
    local services=(
        "8001:认证服务"
        "8002:用户服务"
        "8003:健康数据服务"
        "8011:小艾智能体"
        "8012:小克智能体"
        "8013:老克智能体"
        "8014:索儿智能体"
    )
    
    local failed_services=()
    
    for service in "${services[@]}"; do
        local port="${service%%:*}"
        local name="${service##*:}"
        
        if ! curl -s -f "http://localhost:${port}/health" > /dev/null 2>&1; then
            failed_services+=("$name (端口:$port)")
        else
            log_success "$name 运行正常"
        fi
    done
    
    if [ ${#failed_services[@]} -ne 0 ]; then
        log_warning "以下服务未运行: ${failed_services[*]}"
        log_info "请先启动相关服务"
    fi
}

# 创建结果目录
setup_results_dir() {
    mkdir -p "$RESULTS_DIR"
    log_info "结果将保存到: $RESULTS_DIR"
}

# 运行认证服务负载测试
run_auth_load_test() {
    log_info "运行认证服务负载测试..."
    
    k6 run k6/performance-tests/scenarios/auth-load-test.js \
        --env BASE_URL="$BASE_URL" \
        --out json="$RESULTS_DIR/auth-load-test.json" \
        --out csv="$RESULTS_DIR/auth-load-test.csv" \
        --summary-export="$RESULTS_DIR/auth-load-summary.json"
    
    log_success "认证服务负载测试完成"
}

# 运行健康数据服务压力测试
run_health_data_stress_test() {
    log_info "运行健康数据服务压力测试..."
    
    k6 run k6/performance-tests/load-test-config.js \
        --env BASE_URL="$BASE_URL" \
        --env K6_SCENARIO_NAME="health_data_stress_test" \
        --out json="$RESULTS_DIR/health-data-stress.json" \
        --out csv="$RESULTS_DIR/health-data-stress.csv" \
        --summary-export="$RESULTS_DIR/health-data-stress-summary.json"
    
    log_success "健康数据服务压力测试完成"
}

# 运行智能体协同峰值测试
run_agent_spike_test() {
    log_info "运行智能体协同峰值测试..."
    
    k6 run k6/performance-tests/load-test-config.js \
        --env BASE_URL="$BASE_URL" \
        --env K6_SCENARIO_NAME="agent_collaboration_spike_test" \
        --out json="$RESULTS_DIR/agent-spike-test.json" \
        --out csv="$RESULTS_DIR/agent-spike-test.csv" \
        --summary-export="$RESULTS_DIR/agent-spike-summary.json"
    
    log_success "智能体协同峰值测试完成"
}

# 运行中医诊断容量测试
run_tcm_capacity_test() {
    log_info "运行中医诊断容量测试..."
    
    k6 run k6/performance-tests/load-test-config.js \
        --env BASE_URL="$BASE_URL" \
        --env K6_SCENARIO_NAME="tcm_diagnosis_capacity_test" \
        --out json="$RESULTS_DIR/tcm-capacity-test.json" \
        --out csv="$RESULTS_DIR/tcm-capacity-test.csv" \
        --summary-export="$RESULTS_DIR/tcm-capacity-summary.json"
    
    log_success "中医诊断容量测试完成"
}

# 运行系统稳定性测试
run_stability_test() {
    log_info "运行系统稳定性测试（长时间运行）..."
    
    k6 run k6/performance-tests/load-test-config.js \
        --env BASE_URL="$BASE_URL" \
        --env K6_SCENARIO_NAME="system_stability_test" \
        --out json="$RESULTS_DIR/stability-test.json" \
        --out csv="$RESULTS_DIR/stability-test.csv" \
        --summary-export="$RESULTS_DIR/stability-summary.json"
    
    log_success "系统稳定性测试完成"
}

# 运行自定义负载测试
run_custom_load_test() {
    local vus="${1:-50}"
    local duration="${2:-5m}"
    
    log_info "运行自定义负载测试 (VUs: $vus, 持续时间: $duration)..."
    
    k6 run k6/performance-tests/load-test-config.js \
        --env BASE_URL="$BASE_URL" \
        --vus "$vus" \
        --duration "$duration" \
        --out json="$RESULTS_DIR/custom-load-test.json" \
        --out csv="$RESULTS_DIR/custom-load-test.csv" \
        --summary-export="$RESULTS_DIR/custom-load-summary.json"
    
    log_success "自定义负载测试完成"
}

# 生成性能报告
generate_performance_report() {
    log_info "生成性能测试报告..."
    
    # 使用Python脚本生成详细报告
    python3 << 'EOF'
import json
import glob
import os
from datetime import datetime
import csv

def load_json_file(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载文件 {filepath} 失败: {e}")
        return None

def generate_html_report(results_dir):
    # 收集所有测试结果
    json_files = glob.glob(f"{results_dir}/*-summary.json")
    
    test_results = {}
    for file in json_files:
        test_name = os.path.basename(file).replace('-summary.json', '')
        data = load_json_file(file)
        if data:
            test_results[test_name] = data
    
    # 生成HTML报告
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>索克生活项目 - 性能测试报告</title>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; }}
        .header h1 {{ margin: 0; font-size: 2.5em; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
        .test-section {{ margin: 30px 0; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px; background: #fafafa; }}
        .test-title {{ font-size: 1.5em; color: #333; margin-bottom: 15px; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
        .metric-card {{ background: white; padding: 15px; border-radius: 6px; border-left: 4px solid #667eea; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric-label {{ font-size: 0.9em; color: #666; margin-bottom: 5px; }}
        .metric-value {{ font-size: 1.8em; font-weight: bold; color: #333; }}
        .metric-unit {{ font-size: 0.8em; color: #888; }}
        .status-good {{ color: #4CAF50; }}
        .status-warning {{ color: #FF9800; }}
        .status-error {{ color: #F44336; }}
        .summary {{ background: #e8f5e8; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .chart-placeholder {{ background: #f0f0f0; height: 200px; border-radius: 6px; display: flex; align-items: center; justify-content: center; color: #666; margin: 15px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>索克生活健康管理平台</h1>
            <h2>性能测试报告</h2>
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
"""
    
    # 添加每个测试的结果
    for test_name, data in test_results.items():
        metrics = data.get('metrics', {})
        
        # 提取关键指标
        http_reqs = metrics.get('http_reqs', {})
        http_req_duration = metrics.get('http_req_duration', {})
        http_req_failed = metrics.get('http_req_failed', {})
        
        total_requests = http_reqs.get('count', 0)
        avg_response_time = http_req_duration.get('avg', 0)
        p95_response_time = http_req_duration.get('p(95)', 0)
        error_rate = http_req_failed.get('rate', 0) * 100
        
        # 判断状态
        status_class = "status-good"
        if error_rate > 1:
            status_class = "status-error"
        elif p95_response_time > 1000:
            status_class = "status-warning"
        
        html_content += f"""
        <div class="test-section">
            <div class="test-title">{test_name.replace('-', ' ').title()}</div>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">总请求数</div>
                    <div class="metric-value">{total_requests:,}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">平均响应时间</div>
                    <div class="metric-value {status_class}">{avg_response_time:.2f} <span class="metric-unit">ms</span></div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">95%响应时间</div>
                    <div class="metric-value {status_class}">{p95_response_time:.2f} <span class="metric-unit">ms</span></div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">错误率</div>
                    <div class="metric-value {status_class}">{error_rate:.2f} <span class="metric-unit">%</span></div>
                </div>
            </div>
            <div class="chart-placeholder">
                响应时间趋势图 (需要集成图表库)
            </div>
        </div>
"""
    
    # 生成总结
    total_tests = len(test_results)
    passed_tests = sum(1 for data in test_results.values() 
                      if data.get('metrics', {}).get('http_req_failed', {}).get('rate', 0) < 0.01)
    
    html_content += f"""
        <div class="summary">
            <h3>测试总结</h3>
            <p>总测试数: {total_tests}</p>
            <p>通过测试: {passed_tests}</p>
            <p>成功率: {(passed_tests/total_tests*100):.1f}%</p>
        </div>
    </div>
</body>
</html>
"""
    
    # 保存HTML报告
    with open(f"{results_dir}/performance-report.html", 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML报告已生成: {results_dir}/performance-report.html")

# 生成CSV汇总报告
def generate_csv_summary(results_dir):
    json_files = glob.glob(f"{results_dir}/*-summary.json")
    
    summary_data = []
    for file in json_files:
        test_name = os.path.basename(file).replace('-summary.json', '')
        data = load_json_file(file)
        if data:
            metrics = data.get('metrics', {})
            summary_data.append({
                'test_name': test_name,
                'total_requests': metrics.get('http_reqs', {}).get('count', 0),
                'avg_response_time': metrics.get('http_req_duration', {}).get('avg', 0),
                'p95_response_time': metrics.get('http_req_duration', {}).get('p(95)', 0),
                'error_rate': metrics.get('http_req_failed', {}).get('rate', 0) * 100,
                'throughput': metrics.get('http_reqs', {}).get('rate', 0)
            })
    
    # 保存CSV文件
    if summary_data:
        with open(f"{results_dir}/performance-summary.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=summary_data[0].keys())
            writer.writeheader()
            writer.writerows(summary_data)
        
        print(f"CSV汇总已生成: {results_dir}/performance-summary.csv")

# 执行报告生成
results_dir = os.environ.get('RESULTS_DIR', 'performance-results')
generate_html_report(results_dir)
generate_csv_summary(results_dir)
EOF
    
    log_success "性能测试报告已生成"
    log_info "查看HTML报告: $RESULTS_DIR/performance-report.html"
    log_info "查看CSV汇总: $RESULTS_DIR/performance-summary.csv"
}

# 显示帮助信息
show_help() {
    echo "索克生活项目性能测试脚本"
    echo ""
    echo "用法: $0 [测试类型] [选项]"
    echo ""
    echo "测试类型:"
    echo "  auth          认证服务负载测试"
    echo "  health-data   健康数据服务压力测试"
    echo "  agent-spike   智能体协同峰值测试"
    echo "  tcm-capacity  中医诊断容量测试"
    echo "  stability     系统稳定性测试"
    echo "  custom        自定义负载测试"
    echo "  all           运行所有测试"
    echo ""
    echo "选项:"
    echo "  --base-url URL        设置基础URL (默认: http://localhost:8000)"
    echo "  --duration DURATION   设置测试持续时间 (默认: 5m)"
    echo "  --users USERS         设置并发用户数 (默认: 50)"
    echo "  --results-dir DIR     设置结果目录 (默认: performance-results)"
    echo "  --help, -h            显示此帮助信息"
    echo ""
    echo "环境变量:"
    echo "  BASE_URL              基础URL"
    echo "  TEST_DURATION         测试持续时间"
    echo "  CONCURRENT_USERS      并发用户数"
    echo "  RESULTS_DIR           结果目录"
    echo ""
    echo "示例:"
    echo "  $0 all                                    # 运行所有测试"
    echo "  $0 auth --base-url http://localhost:8001  # 测试认证服务"
    echo "  $0 custom --users 100 --duration 10m     # 自定义负载测试"
}

# 解析命令行参数
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --base-url)
                BASE_URL="$2"
                shift 2
                ;;
            --duration)
                TEST_DURATION="$2"
                shift 2
                ;;
            --users)
                CONCURRENT_USERS="$2"
                shift 2
                ;;
            --results-dir)
                RESULTS_DIR="$2"
                shift 2
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                break
                ;;
        esac
    done
}

# 主函数
main() {
    local test_type="${1:-all}"
    
    log_info "开始索克生活项目性能测试..."
    log_info "基础URL: $BASE_URL"
    log_info "测试持续时间: $TEST_DURATION"
    log_info "并发用户数: $CONCURRENT_USERS"
    
    # 检查依赖
    check_k6
    
    # 检查服务状态
    check_services
    
    # 设置结果目录
    setup_results_dir
    
    # 根据测试类型执行相应测试
    case $test_type in
        auth)
            run_auth_load_test
            ;;
        health-data)
            run_health_data_stress_test
            ;;
        agent-spike)
            run_agent_spike_test
            ;;
        tcm-capacity)
            run_tcm_capacity_test
            ;;
        stability)
            run_stability_test
            ;;
        custom)
            run_custom_load_test "$CONCURRENT_USERS" "$TEST_DURATION"
            ;;
        all)
            run_auth_load_test
            run_health_data_stress_test
            run_agent_spike_test
            run_tcm_capacity_test
            # 稳定性测试时间较长，可选择性运行
            if [ "${RUN_STABILITY_TEST:-false}" = "true" ]; then
                run_stability_test
            fi
            ;;
        *)
            log_error "未知的测试类型: $test_type"
            show_help
            exit 1
            ;;
    esac
    
    # 生成报告
    generate_performance_report
    
    log_success "性能测试完成！"
    log_info "结果保存在: $RESULTS_DIR"
}

# 解析参数并运行
parse_args "$@"
main "$@" 