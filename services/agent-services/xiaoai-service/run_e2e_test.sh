#!/bin/bash
# 小艾智能体端到端测试执行脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# 默认参数
ENVIRONMENT="development"
AUTO_START=false
SCENARIOS=""
OUTPUT_FILE=""
VERBOSE=false
NO_CLEANUP=false

# 帮助信息
show_help() {
    echo "小艾智能体端到端测试执行脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -e, --environment ENV    测试环境 (development, testing, staging, production)"
    echo "  -s, --scenarios LIST     要执行的测试场景 (用逗号分隔)"
    echo "  -a, --auto-start         自动启动服务"
    echo "  -o, --output FILE        结果输出文件"
    echo "  -v, --verbose            详细输出"
    echo "  --no-cleanup             测试后不清理服务"
    echo "  -h, --help               显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 -e development -a                    # 开发环境，自动启动服务"
    echo "  $0 -s health_consultation,device_access # 只运行指定场景"
    echo "  $0 -e testing -o results.json           # 测试环境，保存结果"
    echo ""
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -s|--scenarios)
            SCENARIOS="$2"
            shift 2
            ;;
        -a|--auto-start)
            AUTO_START=true
            shift
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --no-cleanup)
            NO_CLEANUP=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}错误: 未知参数 $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# 打印配置信息
print_config() {
    echo -e "${BLUE}=== 小艾智能体端到端测试配置 ===${NC}"
    echo -e "测试环境: ${GREEN}$ENVIRONMENT${NC}"
    echo -e "自动启动服务: ${GREEN}$AUTO_START${NC}"
    if [[ -n "$SCENARIOS" ]]; then
        echo -e "测试场景: ${GREEN}$SCENARIOS${NC}"
    else
        echo -e "测试场景: ${GREEN}全部${NC}"
    fi
    if [[ -n "$OUTPUT_FILE" ]]; then
        echo -e "输出文件: ${GREEN}$OUTPUT_FILE${NC}"
    fi
    echo -e "详细输出: ${GREEN}$VERBOSE${NC}"
    echo ""
}

# 检查Python环境
check_python() {
    echo -e "${BLUE}检查Python环境...${NC}"
    
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}错误: 未找到python3${NC}"
        exit 1
    fi
    
    # 检查Python版本
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    echo -e "Python版本: ${GREEN}$PYTHON_VERSION${NC}"
    
    if [[ $(echo "$PYTHON_VERSION < 3.8" | bc -l) -eq 1 ]]; then
        echo -e "${YELLOW}警告: Python版本较低，建议使用3.8+${NC}"
    fi
}

# 检查依赖包
check_dependencies() {
    echo -e "${BLUE}检查依赖包...${NC}"
    
    local required_packages=("aiohttp" "websockets" "pyyaml")
    local missing_packages=()
    
    for package in "${required_packages[@]}"; do
        if ! python3 -c "import $package" &> /dev/null; then
            missing_packages+=("$package")
        fi
    done
    
    if [[ ${#missing_packages[@]} -gt 0 ]]; then
        echo -e "${RED}缺少依赖包: ${missing_packages[*]}${NC}"
        echo -e "${YELLOW}正在安装依赖包...${NC}"
        
        pip3 install "${missing_packages[@]}" || {
            echo -e "${RED}依赖包安装失败${NC}"
            exit 1
        }
    fi
    
    echo -e "${GREEN}✓ 依赖检查通过${NC}"
}

# 检查配置文件
check_config_file() {
    echo -e "${BLUE}检查配置文件...${NC}"
    
    local config_file="config/e2e_test_config.yaml"
    
    if [[ ! -f "$config_file" ]]; then
        echo -e "${YELLOW}警告: 配置文件不存在，将使用默认配置${NC}"
    else
        echo -e "${GREEN}✓ 配置文件存在: $config_file${NC}"
    fi
}

# 构建测试命令
build_test_command() {
    local cmd="python3 scripts/run_e2e_tests.py"
    
    cmd="$cmd --environment $ENVIRONMENT"
    
    if [[ "$AUTO_START" == "true" ]]; then
        cmd="$cmd --auto-start"
    fi
    
    if [[ -n "$SCENARIOS" ]]; then
        cmd="$cmd --scenarios $SCENARIOS"
    fi
    
    if [[ -n "$OUTPUT_FILE" ]]; then
        cmd="$cmd --output $OUTPUT_FILE"
    fi
    
    if [[ "$VERBOSE" == "true" ]]; then
        cmd="$cmd --verbose"
    fi
    
    if [[ "$NO_CLEANUP" == "true" ]]; then
        cmd="$cmd --no-cleanup"
    fi
    
    echo "$cmd"
}

# 运行测试
run_tests() {
    echo -e "${BLUE}开始执行端到端测试...${NC}"
    echo ""
    
    local test_cmd
    test_cmd=$(build_test_command)
    
    echo -e "${YELLOW}执行命令: $test_cmd${NC}"
    echo ""
    
    # 执行测试
    if eval "$test_cmd"; then
        echo ""
        echo -e "${GREEN}✅ 测试执行成功${NC}"
        return 0
    else
        echo ""
        echo -e "${RED}❌ 测试执行失败${NC}"
        return 1
    fi
}

# 清理函数
cleanup() {
    echo -e "${YELLOW}正在清理...${NC}"
    
    # 停止可能的后台进程
    pkill -f "python3.*http_server.py" 2>/dev/null || true
    pkill -f "python3.*websocket_server.py" 2>/dev/null || true
    
    echo -e "${GREEN}✓ 清理完成${NC}"
}

# 信号处理
trap cleanup EXIT INT TERM

# 主函数
main() {
    print_config
    check_python
    check_dependencies
    check_config_file
    
    echo ""
    echo -e "${BLUE}=== 开始测试 ===${NC}"
    
    if run_tests; then
        echo ""
        echo -e "${GREEN}🎉 端到端测试完成！${NC}"
        exit 0
    else
        echo ""
        echo -e "${RED}💥 端到端测试失败！${NC}"
        exit 1
    fi
}

# 执行主函数
main "$@" 