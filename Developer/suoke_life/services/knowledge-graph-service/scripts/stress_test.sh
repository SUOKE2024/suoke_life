#!/bin/bash

# 知识图谱服务压力测试脚本
# 使用 hey 工具进行HTTP负载测试 (https://github.com/rakyll/hey)
# 使用前请确保已安装hey: go install github.com/rakyll/hey@latest

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# 默认设置
API_HOST="http://localhost:8080"
DURATION=10 # 测试持续时间(秒)
CONCURRENCY=10 # 并发数
REQUESTS=1000 # 请求总数
OUTPUT_DIR="./tests/stress_test_results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_FILE="${OUTPUT_DIR}/stress_test_${TIMESTAMP}.txt"
VERBOSE=0
ENDPOINTS=()
TOKEN=""

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 显示使用帮助
show_help() {
    echo -e "${BLUE}知识图谱服务API压力测试工具${NC}"
    echo ""
    echo "用法: $0 [选项] [端点1 端点2 ...]"
    echo ""
    echo "选项:"
    echo "  -h, --help              显示此帮助信息"
    echo "  -H, --host <url>        API主机URL (默认: http://localhost:8080)"
    echo "  -d, --duration <秒>     测试持续时间(秒) (默认: 10)"
    echo "  -c, --concurrency <数量> 并发连接数 (默认: 10)"
    echo "  -n, --requests <数量>   请求总数 (默认: 1000)"
    echo "  -o, --output <文件>     输出文件 (默认: ${OUTPUT_DIR}/stress_test_<timestamp>.txt)"
    echo "  -t, --token <token>     用于认证的JWT令牌"
    echo "  -v, --verbose           详细输出模式"
    echo ""
    echo "示例:"
    echo "  $0 -c 50 -n 5000 /api/health /api/v1/nodes"
    echo "  $0 -H http://api.example.com -d 30 -t 'Bearer xyz...' /api/v1/relationships"
    echo ""
    exit 0
}

# 参数解析
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            ;;
        -H|--host)
            API_HOST="$2"
            shift 2
            ;;
        -d|--duration)
            DURATION="$2"
            shift 2
            ;;
        -c|--concurrency)
            CONCURRENCY="$2"
            shift 2
            ;;
        -n|--requests)
            REQUESTS="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -t|--token)
            TOKEN="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=1
            shift
            ;;
        -*)
            echo -e "${RED}错误: 未知选项 $1${NC}" >&2
            show_help
            ;;
        *)
            ENDPOINTS+=("$1")
            shift
            ;;
    esac
done

# 检查hey命令是否可用
if ! command -v hey &> /dev/null; then
    echo -e "${RED}错误: 未找到'hey'命令。请安装: go install github.com/rakyll/hey@latest${NC}" >&2
    exit 1
fi

# 如果没有指定端点，使用默认端点
if [ ${#ENDPOINTS[@]} -eq 0 ]; then
    ENDPOINTS=("/api/health" "/api/v1/nodes" "/api/v1/relationships")
fi

# 打印测试配置
echo -e "${BLUE}======== 压力测试配置 ========${NC}" | tee -a "$OUTPUT_FILE"
echo -e "API主机: ${GREEN}${API_HOST}${NC}" | tee -a "$OUTPUT_FILE"
echo -e "测试端点: ${GREEN}${ENDPOINTS[*]}${NC}" | tee -a "$OUTPUT_FILE"
echo -e "持续时间: ${GREEN}${DURATION}秒${NC}" | tee -a "$OUTPUT_FILE"
echo -e "并发连接: ${GREEN}${CONCURRENCY}${NC}" | tee -a "$OUTPUT_FILE"
echo -e "请求总数: ${GREEN}${REQUESTS}${NC}" | tee -a "$OUTPUT_FILE"
echo -e "认证: ${GREEN}$([ -n "$TOKEN" ] && echo "已启用" || echo "未启用")${NC}" | tee -a "$OUTPUT_FILE"
echo -e "输出文件: ${GREEN}${OUTPUT_FILE}${NC}" | tee -a "$OUTPUT_FILE"
echo -e "${BLUE}===============================${NC}" | tee -a "$OUTPUT_FILE"
echo "" | tee -a "$OUTPUT_FILE"

# 执行测试函数
run_test() {
    local endpoint=$1
    local url="${API_HOST}${endpoint}"
    local header_args=""
    
    echo -e "${YELLOW}开始测试端点: ${endpoint}${NC}" | tee -a "$OUTPUT_FILE"
    
    # 添加认证头
    if [ -n "$TOKEN" ]; then
        header_args="-H \"Authorization: ${TOKEN}\""
    fi
    
    # 构建完整的命令
    local cmd="hey -n ${REQUESTS} -c ${CONCURRENCY} -z ${DURATION}s ${header_args} ${url}"
    
    if [ $VERBOSE -eq 1 ]; then
        echo -e "${BLUE}执行命令: ${cmd}${NC}" | tee -a "$OUTPUT_FILE"
    fi
    
    # 执行测试
    if [ -n "$TOKEN" ]; then
        hey -n "${REQUESTS}" -c "${CONCURRENCY}" -z "${DURATION}s" -H "Authorization: ${TOKEN}" "${url}" | tee -a "$OUTPUT_FILE"
    else
        hey -n "${REQUESTS}" -c "${CONCURRENCY}" -z "${DURATION}s" "${url}" | tee -a "$OUTPUT_FILE"
    fi
    
    echo -e "${GREEN}端点测试完成: ${endpoint}${NC}" | tee -a "$OUTPUT_FILE"
    echo "" | tee -a "$OUTPUT_FILE"
    echo -e "${BLUE}-------------------------------${NC}" | tee -a "$OUTPUT_FILE"
    echo "" | tee -a "$OUTPUT_FILE"
}

# 主测试循环
echo -e "${BLUE}开始API压力测试...${NC}" | tee -a "$OUTPUT_FILE"
echo "" | tee -a "$OUTPUT_FILE"

for endpoint in "${ENDPOINTS[@]}"; do
    run_test "$endpoint"
done

echo -e "${GREEN}所有测试完成!${NC}" | tee -a "$OUTPUT_FILE"
echo -e "结果已保存到: ${OUTPUT_FILE}" | tee -a "$OUTPUT_FILE"