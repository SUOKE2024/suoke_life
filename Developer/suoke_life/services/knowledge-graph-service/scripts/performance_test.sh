#!/bin/bash
# 知识图谱服务性能测试脚本
# 使用方法: ./performance_test.sh [选项]
# 选项:
#   -h, --host          测试主机，默认为 localhost:8080
#   -c, --concurrency   并发数，默认为 100
#   -n, --requests      总请求数，默认为 10000
#   -d, --duration      测试持续时间（秒），默认为 60
#   -t, --timeout       请求超时时间（秒），默认为 5
#   -p, --profile       是否启用性能分析，默认为 false
#   --help              显示此帮助信息

set -e

# 默认参数
HOST="localhost:8080"
CONCURRENCY=100
REQUESTS=10000
DURATION=60
TIMEOUT=5
PROFILE=false
OUTPUT_DIR="performance_results_$(date +%Y%m%d_%H%M%S)"

# 处理参数
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -h|--host) HOST="$2"; shift ;;
        -c|--concurrency) CONCURRENCY="$2"; shift ;;
        -n|--requests) REQUESTS="$2"; shift ;;
        -d|--duration) DURATION="$2"; shift ;;
        -t|--timeout) TIMEOUT="$2"; shift ;;
        -p|--profile) PROFILE=true ;;
        --help) 
            echo "使用方法: ./performance_test.sh [选项]"
            echo "选项:"
            echo "  -h, --host          测试主机，默认为 localhost:8080"
            echo "  -c, --concurrency   并发数，默认为 100"
            echo "  -n, --requests      总请求数，默认为 10000"
            echo "  -d, --duration      测试持续时间（秒），默认为 60"
            echo "  -t, --timeout       请求超时时间（秒），默认为 5"
            echo "  -p, --profile       是否启用性能分析，默认为 false"
            echo "  --help              显示此帮助信息"
            exit 0
            ;;
        *) echo "未知参数: $1"; exit 1 ;;
    esac
    shift
done

# 创建结果目录
mkdir -p "$OUTPUT_DIR"
echo "性能测试结果将保存在: $OUTPUT_DIR"

# 检查需要的工具
if ! command -v hey &> /dev/null; then
    echo "未找到 hey 工具，正在安装..."
    go install github.com/rakyll/hey@latest
fi

# 要测试的端点列表
ENDPOINTS=(
    "/api/v1/nodes"
    "/api/v1/nodes/search?label=Herb&limit=10"
    "/api/v1/relationships"
    "/api/v1/graph/neighborhood?nodeId=1&depth=1"
)

# 性能测试函数
run_test() {
    local endpoint=$1
    local output_file="$OUTPUT_DIR/$(echo $endpoint | tr '/' '_' | tr '?' '_' | tr '&' '_' | tr '=' '_').txt"
    
    echo "测试端点: $endpoint"
    echo "并发数: $CONCURRENCY, 请求数: $REQUESTS, 超时: ${TIMEOUT}s"
    
    # 使用 hey 进行性能测试
    hey -n $REQUESTS -c $CONCURRENCY -t $TIMEOUT "http://$HOST$endpoint" > "$output_file"
    
    # 分析并打印结果摘要
    echo "----- 结果摘要 -----"
    grep -A 10 "Summary:" "$output_file"
    echo "详细结果已保存到: $output_file"
    echo ""
}

# 如果启用了性能分析
if [ "$PROFILE" = true ]; then
    echo "启用性能分析..."
    echo "注意: 性能分析需要服务端支持 /debug/pprof/ 端点"
    
    # CPU 分析
    go tool pprof -seconds 30 "http://$HOST/debug/pprof/profile" > "$OUTPUT_DIR/cpu_profile.txt" &
    CPU_PROFILE_PID=$!
    
    # 内存分析
    go tool pprof "http://$HOST/debug/pprof/heap" > "$OUTPUT_DIR/heap_profile.txt" &
    HEAP_PROFILE_PID=$!
    
    # 阻塞分析
    go tool pprof "http://$HOST/debug/pprof/block" > "$OUTPUT_DIR/block_profile.txt" &
    BLOCK_PROFILE_PID=$!
    
    # 给一些时间启动分析
    sleep 5
fi

# 运行测试前的服务状态
echo "获取服务状态..."
curl -s "http://$HOST/health" > "$OUTPUT_DIR/service_status_before.json" || echo "警告: 无法获取服务状态"

# 记录开始时间
START_TIME=$(date +%s)
echo "测试开始于: $(date)"

# 对每个端点运行测试
for endpoint in "${ENDPOINTS[@]}"; do
    run_test "$endpoint"
done

# 长时间测试
echo "执行持续时间测试: $DURATION 秒"
for endpoint in "${ENDPOINTS[@]}"; do
    output_file="$OUTPUT_DIR/duration_$(echo $endpoint | tr '/' '_' | tr '?' '_' | tr '&' '_' | tr '=' '_').txt"
    hey -z "${DURATION}s" -c $CONCURRENCY "http://$HOST$endpoint" > "$output_file" &
done

# 等待持续时间测试完成
echo "等待持续时间测试完成..."
sleep $((DURATION + 5))

# 运行测试后的服务状态
curl -s "http://$HOST/health" > "$OUTPUT_DIR/service_status_after.json" || echo "警告: 无法获取服务状态"

# 记录结束时间
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
echo "测试结束于: $(date)"
echo "总耗时: $ELAPSED 秒"

# 如果启用了性能分析，等待分析完成
if [ "$PROFILE" = true ]; then
    echo "等待性能分析完成..."
    wait $CPU_PROFILE_PID
    wait $HEAP_PROFILE_PID
    wait $BLOCK_PROFILE_PID
    echo "性能分析已完成"
fi

# 生成综合报告
echo "正在生成综合报告..."
{
    echo "# 知识图谱服务性能测试报告"
    echo ""
    echo "## 测试参数"
    echo ""
    echo "- 主机: $HOST"
    echo "- 并发数: $CONCURRENCY"
    echo "- 请求数: $REQUESTS"
    echo "- 持续时间: $DURATION 秒"
    echo "- 超时: $TIMEOUT 秒"
    echo "- 测试时间: $(date)"
    echo ""
    echo "## 测试结果摘要"
    echo ""
    
    for endpoint in "${ENDPOINTS[@]}"; do
        echo "### 端点: $endpoint"
        echo ""
        echo "```"
        output_file="$OUTPUT_DIR/$(echo $endpoint | tr '/' '_' | tr '?' '_' | tr '&' '_' | tr '=' '_').txt"
        grep -A 10 "Summary:" "$output_file" || echo "无法获取摘要数据"
        echo "```"
        echo ""
    done
    
    echo "## 持续时间测试结果摘要"
    echo ""
    for endpoint in "${ENDPOINTS[@]}"; do
        echo "### 端点: $endpoint"
        echo ""
        echo "```"
        output_file="$OUTPUT_DIR/duration_$(echo $endpoint | tr '/' '_' | tr '?' '_' | tr '&' '_' | tr '=' '_').txt"
        grep -A 10 "Summary:" "$output_file" || echo "无法获取摘要数据"
        echo "```"
        echo ""
    done
} > "$OUTPUT_DIR/summary_report.md"

echo "综合报告已生成: $OUTPUT_DIR/summary_report.md"
echo "所有测试已完成!"