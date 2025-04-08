#!/bin/bash

# 索克生活RAG服务测试运行脚本
# 用法：./run_tests.sh [选项]
# 选项:
#   --mode <kg|multimodal|multi_source|adaptive|all> 指定要运行的测试模式
#   --verbose 启用详细输出
#   --clean 测试前清理结果目录
#   --mock 使用模拟模式，不需要真实服务器

# 默认设置
TEST_MODE="all"
VERBOSE=""
CLEAN=0
MOCK=0
SERVICE_URL="http://localhost:8080"
OUTPUT_DIR="./test_results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # 无颜色

# 解析命令行参数
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --mode)
      TEST_MODE="$2"
      shift 2
      ;;
    --verbose)
      VERBOSE="--verbose"
      shift
      ;;
    --clean)
      CLEAN=1
      shift
      ;;
    --mock)
      MOCK=1
      shift
      ;;
    --url)
      SERVICE_URL="$2"
      shift 2
      ;;
    --help)
      echo "索克生活RAG服务测试工具"
      echo "用法: ./run_tests.sh [选项]"
      echo "选项:"
      echo "  --mode <kg|multimodal|multi_source|adaptive|tcm|all> 指定要运行的测试模式"
      echo "  --verbose                                        启用详细输出"
      echo "  --clean                                          测试前清理结果目录"
      echo "  --mock                                           使用模拟模式，不需要真实服务器"
      echo "  --url <URL>                                      指定服务URL (默认: http://localhost:8080)"
      echo "  --help                                           显示帮助信息"
      exit 0
      ;;
    *)
      echo "未知选项: $1"
      echo "使用 --help 获取帮助"
      exit 1
      ;;
  esac
done

# 验证测试模式
if [[ ! "$TEST_MODE" =~ ^(kg|multimodal|multi_source|adaptive|tcm|all)$ ]]; then
  echo -e "${RED}错误: 无效的测试模式 $TEST_MODE${NC}"
  echo "有效模式: kg, multimodal, multi_source, adaptive, tcm, all"
  exit 1
fi

# 如果clean标志设置，清理结果目录
if [ $CLEAN -eq 1 ]; then
  echo -e "${YELLOW}清理测试结果目录...${NC}"
  rm -rf "${OUTPUT_DIR:?}"/*
  mkdir -p "$OUTPUT_DIR"
fi

# 确保输出目录存在
mkdir -p "$OUTPUT_DIR"

# 创建测试日志文件
LOG_FILE="$OUTPUT_DIR/test_run_$TIMESTAMP.log"
touch "$LOG_FILE"

# 显示测试开始信息
echo -e "${BLUE}${BOLD}========================================${NC}"
echo -e "${BLUE}${BOLD}   索克生活 RAG 服务测试            ${NC}"
echo -e "${BLUE}${BOLD}========================================${NC}"
echo -e "测试模式: ${YELLOW}$TEST_MODE${NC}"
echo -e "测试时间: ${YELLOW}$(date)${NC}"
if [ $MOCK -eq 1 ]; then
  echo -e "模式: ${YELLOW}模拟测试${NC}"
else
  echo -e "服务地址: ${YELLOW}$SERVICE_URL${NC}"
fi
echo -e "详细输出: ${YELLOW}$([ -n "$VERBOSE" ] && echo "是" || echo "否")${NC}"
echo -e "测试日志: ${YELLOW}$LOG_FILE${NC}"
echo -e "${BLUE}${BOLD}========================================${NC}"
echo ""

# 记录系统信息
echo "测试环境信息:" | tee -a "$LOG_FILE"
echo "---------------------------" | tee -a "$LOG_FILE"
echo "操作系统: $(uname -a)" | tee -a "$LOG_FILE"
echo "Go 版本: $(go version)" | tee -a "$LOG_FILE"
echo "---------------------------" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 测试函数
run_test() {
  local test_name="$1"
  local test_cmd="$2"
  local output_file="$3"
  
  echo -e "${YELLOW}${BOLD}开始测试: $test_name${NC}" | tee -a "$LOG_FILE"
  echo "命令: $test_cmd" | tee -a "$LOG_FILE"
  echo "时间: $(date)" | tee -a "$LOG_FILE"
  echo "---------------------------" | tee -a "$LOG_FILE"
  
  # 运行测试并捕获退出状态
  eval "$test_cmd" 2>&1 | tee -a "$LOG_FILE"
  local status=${PIPESTATUS[0]}
  
  echo "---------------------------" | tee -a "$LOG_FILE"
  if [ $status -eq 0 ]; then
    echo -e "${GREEN}${BOLD}测试通过: $test_name${NC}" | tee -a "$LOG_FILE"
  else
    echo -e "${RED}${BOLD}测试失败: $test_name (退出状态: $status)${NC}" | tee -a "$LOG_FILE"
  fi
  echo "" | tee -a "$LOG_FILE"
  
  return $status
}

# 记录测试结果
declare -a SUCCEEDED_TESTS
declare -a FAILED_TESTS

# 运行知识图谱推理测试
run_kg_test() {
  local test_name="知识图谱推理测试"
  local output="$OUTPUT_DIR/kg_reasoning_$TIMESTAMP.json"
  
  local cmd
  if [ $MOCK -eq 1 ]; then
    cmd="go run test_kg_reasoning.go -predefined -mock $VERBOSE -output $output"
  else
    cmd="go run test_kg_reasoning.go -predefined -url $SERVICE_URL/api/reason $VERBOSE -output $output"
  fi
  
  run_test "$test_name" "$cmd" "$output"
  local status=$?
  
  if [ $status -eq 0 ]; then
    SUCCEEDED_TESTS+=("$test_name")
  else
    FAILED_TESTS+=("$test_name")
  fi
}

# 运行多模态测试
run_multimodal_test() {
  local test_name="多模态测试"
  local output="$OUTPUT_DIR/multimodal_$TIMESTAMP.json"
  
  # 确保测试数据存在
  if [ ! -f "./test_data/images/tongue_sample.jpg" ]; then
    echo -e "${YELLOW}警告: 测试图像不存在，使用模拟图像数据${NC}" | tee -a "$LOG_FILE"
    mkdir -p "./test_data/images"
    touch "./test_data/images/tongue_sample.jpg"
  fi
  
  local cmd
  if [ $MOCK -eq 1 ]; then
    cmd="go run test_multimodal.go -batch -mock -verbose -output $output"
  else
    cmd="go run test_multimodal.go -batch -url $SERVICE_URL/api/search/multimodal -verbose -output $output"
  fi
  
  run_test "$test_name" "$cmd" "$output"
  local status=$?
  
  if [ $status -eq 0 ]; then
    SUCCEEDED_TESTS+=("$test_name")
  else
    FAILED_TESTS+=("$test_name")
  fi
}

# 运行多源检索测试
run_multi_source_test() {
  local test_name="多源检索测试"
  local output="$OUTPUT_DIR/multi_source_$TIMESTAMP.json"
  
  local cmd
  if [ $MOCK -eq 1 ]; then
    cmd="go run test_multi_source.go -batch $VERBOSE -output $output"
  else
    cmd="go run test_multi_source.go -batch -url $SERVICE_URL/api/search/multi_source $VERBOSE -output $output"
  fi
  
  run_test "$test_name" "$cmd" "$output"
  local status=$?
  
  if [ $status -eq 0 ]; then
    SUCCEEDED_TESTS+=("$test_name")
  else
    FAILED_TESTS+=("$test_name")
  fi
}

# 运行自适应学习测试
run_adaptive_test() {
  local test_name="自适应学习测试"
  local output="$OUTPUT_DIR/adaptive_$TIMESTAMP.json"
  
  local cmd
  if [ $MOCK -eq 1 ]; then
    cmd="go run test_adaptive.go -batch -count 10 $VERBOSE -output $output"
  else
    cmd="go run test_adaptive.go -batch -count 10 -url $SERVICE_URL/api/feedback $VERBOSE -output $output"
  fi
  
  run_test "$test_name" "$cmd" "$output"
  local status=$?
  
  if [ $status -eq 0 ]; then
    SUCCEEDED_TESTS+=("$test_name")
  else
    FAILED_TESTS+=("$test_name")
  fi
}

# 运行TCM特征测试
run_tcm_features_test() {
  local test_name="TCM特征测试"
  local output="$OUTPUT_DIR/tcm_features_${TIMESTAMP}.json"
  
  local cmd
  if [ $MOCK -eq 1 ]; then
    cmd="go run test_tcm_features.go -batch -mock -verbose -output $output"
  else
    cmd="go run test_tcm_features.go -batch -url $SERVICE_URL -verbose -output $output"
  fi
  
  run_test "$test_name" "$cmd" "$output"
  local status=$?
  
  if [ $status -eq 0 ]; then
    SUCCEEDED_TESTS+=("$test_name")
  else
    FAILED_TESTS+=("$test_name")
  fi
}

# 根据测试模式运行测试
case $TEST_MODE in
  "kg")
    run_kg_test
    ;;
  "multimodal")
    run_multimodal_test
    ;;
  "multi_source")
    run_multi_source_test
    ;;
  "adaptive")
    run_adaptive_test
    ;;
  "tcm")
    run_tcm_features_test
    ;;
  "all")
    run_kg_test
    run_multimodal_test
    run_multi_source_test
    run_adaptive_test
    run_tcm_features_test
    ;;
esac

# 显示测试结果汇总
echo -e "${BLUE}${BOLD}========================================${NC}" | tee -a "$LOG_FILE"
echo -e "${BLUE}${BOLD}   测试结果汇总                   ${NC}" | tee -a "$LOG_FILE"
echo -e "${BLUE}${BOLD}========================================${NC}" | tee -a "$LOG_FILE"
echo -e "成功: ${GREEN}${#SUCCEEDED_TESTS[@]}${NC}" | tee -a "$LOG_FILE"
echo -e "失败: ${RED}${#FAILED_TESTS[@]}${NC}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

if [ ${#SUCCEEDED_TESTS[@]} -gt 0 ]; then
  echo -e "${GREEN}成功测试:${NC}" | tee -a "$LOG_FILE"
  for t in "${SUCCEEDED_TESTS[@]}"; do
    echo -e " - ${GREEN}$t${NC}" | tee -a "$LOG_FILE"
  done
  echo "" | tee -a "$LOG_FILE"
fi

if [ ${#FAILED_TESTS[@]} -gt 0 ]; then
  echo -e "${RED}失败测试:${NC}" | tee -a "$LOG_FILE"
  for t in "${FAILED_TESTS[@]}"; do
    echo -e " - ${RED}$t${NC}" | tee -a "$LOG_FILE"
  done
  echo "" | tee -a "$LOG_FILE"
fi

# 计算成功率
total_tests=$((${#SUCCEEDED_TESTS[@]} + ${#FAILED_TESTS[@]}))
if [ $total_tests -gt 0 ]; then
  success_rate=$(( ${#SUCCEEDED_TESTS[@]} * 100 / $total_tests ))
  echo -e "测试成功率: ${YELLOW}${success_rate}%${NC}" | tee -a "$LOG_FILE"
fi

echo -e "详细日志: ${YELLOW}$LOG_FILE${NC}" | tee -a "$LOG_FILE"
echo -e "${BLUE}${BOLD}========================================${NC}" | tee -a "$LOG_FILE"

# 根据测试结果设置退出状态
if [ ${#FAILED_TESTS[@]} -eq 0 ]; then
  exit 0
else
  exit 1
fi 