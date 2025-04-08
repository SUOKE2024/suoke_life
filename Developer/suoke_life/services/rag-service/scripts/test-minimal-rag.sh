#!/bin/bash

# 设置颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# 设置服务URL
BASE_URL="http://localhost:8080"

# 打印分隔线
print_divider() {
  echo -e "${YELLOW}=========================================================${NC}"
}

# 测试健康检查API
test_health() {
  print_divider
  echo -e "${GREEN}测试健康检查API${NC}"
  curl -s $BASE_URL/health | jq .
  if [ $? -ne 0 ]; then
    echo -e "${RED}健康检查API测试失败${NC}"
    exit 1
  fi
  print_divider
}

# 测试文本搜索API
test_text_search() {
  print_divider
  echo -e "${GREEN}测试文本搜索API${NC}"
  curl -s "$BASE_URL/api/search?q=感冒的中医治疗方法" | jq .
  if [ $? -ne 0 ]; then
    echo -e "${RED}文本搜索API测试失败${NC}"
    exit 1
  fi
  print_divider
}

# 测试多模态搜索API
test_multimodal_search() {
  print_divider
  echo -e "${GREEN}测试多模态搜索API${NC}"
  curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"query":"我感冒了，嗓子疼", "userId":"testuser"}' \
    $BASE_URL/api/search/multimodal | jq .
  if [ $? -ne 0 ]; then
    echo -e "${RED}多模态搜索API测试失败${NC}"
    exit 1
  fi
  print_divider
}

# 测试舌诊分析API
test_tongue_analysis() {
  print_divider
  echo -e "${GREEN}测试舌诊分析API${NC}"
  curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"imageData":"base64_encoded_image_data_here"}' \
    $BASE_URL/api/analyze/tongue | jq .
  if [ $? -ne 0 ]; then
    echo -e "${RED}舌诊分析API测试失败${NC}"
    exit 1
  fi
  print_divider
}

# 测试面诊分析API
test_face_analysis() {
  print_divider
  echo -e "${GREEN}测试面诊分析API${NC}"
  curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"imageData":"base64_encoded_image_data_here"}' \
    $BASE_URL/api/analyze/face | jq .
  if [ $? -ne 0 ]; then
    echo -e "${RED}面诊分析API测试失败${NC}"
    exit 1
  fi
  print_divider
}

# 测试音频分析API
test_audio_analysis() {
  print_divider
  echo -e "${GREEN}测试音频分析API${NC}"
  curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"audioData":"base64_encoded_audio_data_here", "audioType":"cough"}' \
    $BASE_URL/api/analyze/audio | jq .
  if [ $? -ne 0 ]; then
    echo -e "${RED}音频分析API测试失败${NC}"
    exit 1
  fi
  print_divider
}

# 运行所有测试
run_all_tests() {
  echo -e "${GREEN}开始测试索克生活RAG服务最小化版本...${NC}"
  
  test_health
  test_text_search
  test_multimodal_search
  test_tongue_analysis
  test_face_analysis
  test_audio_analysis
  
  echo -e "${GREEN}所有测试完成！${NC}"
}

# 检查jq是否安装
check_dependencies() {
  if ! command -v jq &> /dev/null; then
    echo -e "${RED}未找到jq命令，请先安装jq：brew install jq${NC}"
    exit 1
  fi
}

# 主函数
main() {
  check_dependencies
  run_all_tests
}

# 执行主函数
main 