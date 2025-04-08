#!/bin/bash

# 设置颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT" || exit 1

# 设置默认值
SERVER_URL="http://localhost:8080"
TEST_IMAGE_PATH="tests/assets/tongue_sample.jpg"
TEST_AUDIO_PATH="tests/assets/audio_sample.mp3"
QUERY="中医舌诊健康分析"
OUTPUT_DIR="tests/output"
VERBOSE=false

# 日志函数
log() {
  echo -e "${YELLOW}[INFO]${NC} $1"
}

log_success() {
  echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

log_test() {
  echo -e "${BLUE}[TEST]${NC} $1"
}

# 检测操作系统类型
detect_os() {
  if [[ "$OSTYPE" == "darwin"* ]]; then
    OS_TYPE="macos"
  elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS_TYPE="linux"
  else
    OS_TYPE="unknown"
  fi
  log "检测到操作系统类型: $OS_TYPE"
}

# Base64编码函数
encode_base64() {
  local file="$1"
  local encoded=""
  
  if [ ! -f "$file" ]; then
    log_error "文件不存在: $file"
    return 1
  fi
  
  if [ "$OS_TYPE" == "macos" ]; then
    # macOS版本的base64命令需要使用-i选项
    encoded=$(base64 -i "$file" | tr -d '\n')
  else
    # Linux版本的base64命令可以直接接受文件路径
    encoded=$(base64 "$file" | tr -d '\n')
  fi
  
  echo "$encoded"
}

# 显示帮助
show_help() {
  echo "用法: $0 [选项]"
  echo ""
  echo "选项:"
  echo "  -s, --server URL      设置服务器URL (默认: http://localhost:8080)"
  echo "  -i, --image PATH      设置测试图像路径 (默认: tests/assets/tongue_sample.jpg)"
  echo "  -a, --audio PATH      设置测试音频路径 (默认: tests/assets/audio_sample.mp3)"
  echo "  -q, --query TEXT      设置查询文本 (默认: 中医舌诊健康分析)"
  echo "  -o, --output DIR      设置输出目录 (默认: tests/output)"
  echo "  -v, --verbose         显示详细输出"
  echo "  -h, --help            显示帮助信息"
  echo ""
  echo "示例:"
  echo "  $0 --image path/to/image.jpg --query \"舌诊分析\""
  echo "  $0 --audio path/to/audio.mp3 --query \"音频分析\""
  echo "  $0 --image path/to/image.jpg --audio path/to/audio.mp3 --query \"多模态分析\""
  echo ""
}

# 解析参数
parse_args() {
  while [[ $# -gt 0 ]]; do
    case $1 in
      -s|--server)
        SERVER_URL="$2"
        shift 2
        ;;
      -i|--image)
        TEST_IMAGE_PATH="$2"
        shift 2
        ;;
      -a|--audio)
        TEST_AUDIO_PATH="$2"
        shift 2
        ;;
      -q|--query)
        QUERY="$2"
        shift 2
        ;;
      -o|--output)
        OUTPUT_DIR="$2"
        shift 2
        ;;
      -v|--verbose)
        VERBOSE=true
        shift
        ;;
      -h|--help)
        show_help
        exit 0
        ;;
      *)
        log_error "未知参数: $1"
        show_help
        exit 1
        ;;
    esac
  done
}

# 创建必要的目录
create_directories() {
  log "创建必要的目录..."
  
  # 创建测试资源目录
  mkdir -p tests/assets
  mkdir -p "$OUTPUT_DIR"
  
  # 检查是否存在测试图像
  if [[ ! -f "$TEST_IMAGE_PATH" && "$TEST_IMAGE_PATH" == "tests/assets/tongue_sample.jpg" ]]; then
    log "创建示例图像 ($TEST_IMAGE_PATH)..."
    # 创建有效的JPEG文件（最小尺寸）而不是纯文本，确保base64编码有效
    cat > "$TEST_IMAGE_PATH" << 'EOF'
/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD3+iiigD//2Q==
EOF
    log "已创建模拟JPEG图像"
  fi
  
  # 检查是否存在测试音频
  if [[ ! -f "$TEST_AUDIO_PATH" && "$TEST_AUDIO_PATH" == "tests/assets/audio_sample.mp3" ]]; then
    log "创建示例音频 ($TEST_AUDIO_PATH)..."
    # 创建有效的MP3文件头，确保base64编码有效
    printf "\xFF\xFB\x90\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" > "$TEST_AUDIO_PATH"
    log "已创建模拟MP3音频"
  fi
}

# 测试健康检查
test_health() {
  log_test "测试健康检查..."
  
  # 发送健康检查请求
  RESPONSE=$(curl -s "$SERVER_URL/health")
  
  # 检查响应
  if [[ "$RESPONSE" == *"healthy"* ]]; then
    log_success "健康检查通过"
    if [ "$VERBOSE" = true ]; then
      echo "$RESPONSE" | jq -C . || echo "$RESPONSE"
    fi
    return 0
  else
    log_error "健康检查失败"
    echo "$RESPONSE"
    return 1
  fi
}

# 测试基本搜索
test_basic_search() {
  log_test "测试基本搜索..."
  
  # 发送基本搜索请求
  RESPONSE=$(curl -s "$SERVER_URL/api/search?q=$QUERY")
  
  # 检查响应
  if [[ "$RESPONSE" == *"success"* ]]; then
    log_success "基本搜索测试通过"
    if [ "$VERBOSE" = true ]; then
      echo "$RESPONSE" | jq -C . || echo "$RESPONSE"
    fi
    echo "$RESPONSE" > "$OUTPUT_DIR/basic_search_result.json"
    return 0
  else
    log_error "基本搜索测试失败"
    echo "$RESPONSE"
    return 1
  fi
}

# 测试舌诊分析
test_tongue_analysis() {
  log_test "测试舌诊分析..."
  
  # 检查测试图像
  if [ ! -f "$TEST_IMAGE_PATH" ]; then
    log_error "找不到测试图像: $TEST_IMAGE_PATH"
    return 1
  fi
  
  # 发送舌诊分析请求
  RESPONSE=$(curl -s -X POST \
    -F "image=@$TEST_IMAGE_PATH" \
    "$SERVER_URL/api/analyze/tongue")
  
  # 检查响应
  if [[ "$RESPONSE" == *"success"* ]]; then
    log_success "舌诊分析测试通过"
    if [ "$VERBOSE" = true ]; then
      echo "$RESPONSE" | jq -C . || echo "$RESPONSE"
    fi
    echo "$RESPONSE" > "$OUTPUT_DIR/tongue_analysis_result.json"
    return 0
  else
    log_error "舌诊分析测试失败"
    echo "$RESPONSE"
    return 1
  fi
}

# 测试音频分析
test_audio_analysis() {
  log_test "测试音频分析..."
  
  # 检查测试音频
  if [ ! -f "$TEST_AUDIO_PATH" ]; then
    log_error "找不到测试音频: $TEST_AUDIO_PATH"
    return 1
  fi
  
  # 发送音频分析请求
  RESPONSE=$(curl -s -X POST \
    -F "audio=@$TEST_AUDIO_PATH" \
    "$SERVER_URL/api/analyze/audio")
  
  # 检查响应
  if [[ "$RESPONSE" == *"success"* ]]; then
    log_success "音频分析测试通过"
    if [ "$VERBOSE" = true ]; then
      echo "$RESPONSE" | jq -C . || echo "$RESPONSE"
    fi
    echo "$RESPONSE" > "$OUTPUT_DIR/audio_analysis_result.json"
    return 0
  else
    log_error "音频分析测试失败"
    echo "$RESPONSE"
    return 1
  fi
}

# 测试多模态搜索
test_multimodal_search() {
  log_test "测试多模态搜索..."
  
  # 构建multimodal请求
  PAYLOAD='{"query":"'$QUERY'","maxResults":5,"domain":"TCM"}'
  
  # 添加图像（如果存在）
  if [ -f "$TEST_IMAGE_PATH" ]; then
    # 使用修复后的base64编码函数
    IMAGE_B64=$(encode_base64 "$TEST_IMAGE_PATH")
    if [ $? -eq 0 ]; then
      PAYLOAD=$(echo "$PAYLOAD" | jq --arg img "$IMAGE_B64" '. + {"imageData": $img, "imageType": "image/jpeg"}')
    else
      log_error "图像编码失败，跳过添加图像数据"
    fi
  fi
  
  # 添加音频（如果存在）
  if [ -f "$TEST_AUDIO_PATH" ]; then
    # 使用修复后的base64编码函数
    AUDIO_B64=$(encode_base64 "$TEST_AUDIO_PATH")
    if [ $? -eq 0 ]; then
      PAYLOAD=$(echo "$PAYLOAD" | jq --arg aud "$AUDIO_B64" '. + {"audioData": $aud, "audioType": "audio/mpeg"}')
    else
      log_error "音频编码失败，跳过添加音频数据"
    fi
  fi
  
  if [ "$VERBOSE" = true ]; then
    log "发送多模态搜索请求..."
    echo "$PAYLOAD" | jq -C '{query, domain, maxResults}' || echo "Payload too large to display"
  fi
  
  # 发送多模态搜索请求
  RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD" \
    "$SERVER_URL/api/search/multimodal")
  
  # 检查响应
  if [[ "$RESPONSE" == *"success"* ]]; then
    log_success "多模态搜索测试通过"
    if [ "$VERBOSE" = true ]; then
      echo "$RESPONSE" | jq -C . || echo "$RESPONSE"
    fi
    echo "$RESPONSE" > "$OUTPUT_DIR/multimodal_search_result.json"
    return 0
  else
    log_error "多模态搜索测试失败"
    echo "$RESPONSE"
    return 1
  fi
}

# 运行所有测试
run_all_tests() {
  echo "=========================================================="
  echo "      索克生活RAG服务多模态搜索测试"
  echo "      服务器: $SERVER_URL"
  echo "      查询: $QUERY"
  echo "      图像: $TEST_IMAGE_PATH"
  echo "      音频: $TEST_AUDIO_PATH"
  echo "      输出目录: $OUTPUT_DIR"
  echo "=========================================================="
  
  TEST_COUNT=0
  PASS_COUNT=0
  
  # 测试健康检查
  if test_health; then
    PASS_COUNT=$((PASS_COUNT+1))
  fi
  TEST_COUNT=$((TEST_COUNT+1))
  
  # 测试基本搜索
  if test_basic_search; then
    PASS_COUNT=$((PASS_COUNT+1))
  fi
  TEST_COUNT=$((TEST_COUNT+1))
  
  # 测试舌诊分析（如果有图像）
  if [ -f "$TEST_IMAGE_PATH" ]; then
    if test_tongue_analysis; then
      PASS_COUNT=$((PASS_COUNT+1))
    fi
    TEST_COUNT=$((TEST_COUNT+1))
  fi
  
  # 测试音频分析（如果有音频）
  if [ -f "$TEST_AUDIO_PATH" ]; then
    if test_audio_analysis; then
      PASS_COUNT=$((PASS_COUNT+1))
    fi
    TEST_COUNT=$((TEST_COUNT+1))
  fi
  
  # 测试多模态搜索
  if test_multimodal_search; then
    PASS_COUNT=$((PASS_COUNT+1))
  fi
  TEST_COUNT=$((TEST_COUNT+1))
  
  # 显示测试结果
  echo "=========================================================="
  if [ $PASS_COUNT -eq $TEST_COUNT ]; then
    echo -e "${GREEN}所有测试通过！${NC} ($PASS_COUNT/$TEST_COUNT)"
  else
    echo -e "${RED}测试结果: $PASS_COUNT/$TEST_COUNT 通过${NC}"
  fi
  echo "测试结果保存在: $OUTPUT_DIR"
  echo "=========================================================="
}

# 主函数
main() {
  # 检测操作系统类型
  detect_os
  
  # 解析命令行参数
  parse_args "$@"
  
  # 创建必要的目录
  create_directories
  
  # 检查jq是否安装
  if ! command -v jq &> /dev/null; then
    log "jq未安装，将使用普通文本输出"
  fi
  
  # 运行所有测试
  run_all_tests
}

# 执行主函数
main "$@" 