#!/bin/bash
#
# RAG服务压力测试脚本
# 使用hey工具进行HTTP压力测试
#

set -e

# 配置
API_ENDPOINT="https://suoke.life/ai/rag"
API_KEY=""  # 运行脚本时需要提供API密钥
TEST_DURATION="60s"
CONCURRENCY=50
RATE=10  # 每秒请求数限制
QUERY_FILE="queries.txt"
RESULT_DIR="load_test_results"
TIMEOUT="20s"

# 示例查询列表
QUERIES=(
  "中医如何看待感冒"
  "肝火旺盛有哪些表现"
  "春季养生的基本原则是什么"
  "中医体质分类有哪些"
  "如何通过饮食调理湿热体质"
  "经常失眠多梦是什么体质"
  "冬季养生的注意事项"
  "肝郁体质怎么调理"
  "腰酸背痛是肾虚还是湿气重"
  "中医望诊有哪些内容"
)

# 日志函数
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
  case "$1" in
    --api-key)
      API_KEY="$2"
      shift 2
      ;;
    --endpoint)
      API_ENDPOINT="$2"
      shift 2
      ;;
    --duration)
      TEST_DURATION="$2"
      shift 2
      ;;
    --concurrency)
      CONCURRENCY=$2
      shift 2
      ;;
    --rate)
      RATE=$2
      shift 2
      ;;
    --queries)
      QUERY_FILE="$2"
      shift 2
      ;;
    --timeout)
      TIMEOUT="$2"
      shift 2
      ;;
    --help)
      echo "用法: $0 [选项]"
      echo ""
      echo "选项:"
      echo "  --api-key KEY       API密钥（必需）"
      echo "  --endpoint URL      API端点 (默认: $API_ENDPOINT)"
      echo "  --duration TIME     测试持续时间 (默认: $TEST_DURATION)"
      echo "  --concurrency N     并发连接数 (默认: $CONCURRENCY)"
      echo "  --rate N            每秒请求数限制 (默认: $RATE)"
      echo "  --queries FILE      查询文件，每行一个查询 (默认: $QUERY_FILE)"
      echo "  --timeout TIME      请求超时时间 (默认: $TIMEOUT)"
      echo "  --help              显示帮助信息"
      exit 0
      ;;
    *)
      echo "未知选项: $1"
      echo "使用 --help 查看帮助"
      exit 1
      ;;
  esac
done

# 检查API密钥
if [ -z "$API_KEY" ]; then
  log "错误: 未提供API密钥，请使用 --api-key 参数"
  exit 1
fi

# 检查hey工具
if ! command -v hey &> /dev/null; then
  log "错误: 找不到hey工具，请先安装"
  log "安装命令: go install github.com/rakyll/hey@latest"
  exit 1
fi

# 创建结果目录
mkdir -p $RESULT_DIR

# 准备查询文件
if [ ! -f "$QUERY_FILE" ]; then
  log "未找到查询文件，创建示例查询..."
  for query in "${QUERIES[@]}"; do
    echo "$query" >> $QUERY_FILE
  done
  log "已创建查询文件: $QUERY_FILE"
fi

# 显示测试配置
log "压力测试配置:"
log "- API端点: $API_ENDPOINT"
log "- 测试持续时间: $TEST_DURATION"
log "- 并发连接数: $CONCURRENCY"
log "- 每秒请求数限制: $RATE"
log "- 超时时间: $TIMEOUT"
log "- 查询文件: $QUERY_FILE"

# 创建测试数据生成器
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
PAYLOAD_SCRIPT="${RESULT_DIR}/generate_payload_${TIMESTAMP}.py"

log "创建有效载荷生成脚本..."
cat > $PAYLOAD_SCRIPT << 'EOF'
#!/usr/bin/env python3
import random
import json
import sys

# 从查询文件读取查询
queries = []
with open(sys.argv[1], 'r') as f:
    queries = [line.strip() for line in f if line.strip()]

if not queries:
    print("错误: 查询文件为空")
    sys.exit(1)

# 随机选择一个查询
query = random.choice(queries)

# 生成请求体
payload = {
    "query": query,
    "max_tokens": 1000,
    "temperature": 0.7,
    "use_knowledge_graph": True,
}

# 输出JSON格式的请求体
print(json.dumps(payload))
EOF

chmod +x $PAYLOAD_SCRIPT

# 开始测试
log "开始RAG服务压力测试..."
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
RESULT_FILE="${RESULT_DIR}/result_${TIMESTAMP}.txt"
SUMMARY_FILE="${RESULT_DIR}/summary_${TIMESTAMP}.txt"

hey -n 0 -z $TEST_DURATION -c $CONCURRENCY -q $RATE -m POST \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -t $TIMEOUT \
  -D $PAYLOAD_SCRIPT $QUERY_FILE \
  $API_ENDPOINT > $RESULT_FILE

# 提取和显示摘要
log "测试完成，结果保存在: $RESULT_FILE"

# 生成摘要
{
  echo "RAG服务压力测试摘要"
  echo "===================="
  echo "测试时间: $(date '+%Y-%m-%d %H:%M:%S')"
  echo "测试持续时间: $TEST_DURATION"
  echo "并发连接数: $CONCURRENCY"
  echo "每秒请求数限制: $RATE"
  echo ""
  
  # 提取关键指标
  total_requests=$(grep -o "Total requests: [0-9]*" $RESULT_FILE | awk '{print $3}')
  success_requests=$(grep -o "Status code distribution: \[2" $RESULT_FILE -A 1 | grep -o "[0-9]*$" || echo 0)
  avg_resp_time=$(grep -o "Average: [0-9.]*s" $RESULT_FILE | awk '{print $2}')
  slowest=$(grep -o "Slowest: [0-9.]*s" $RESULT_FILE | awk '{print $2}')
  fastest=$(grep -o "Fastest: [0-9.]*s" $RESULT_FILE | awk '{print $2}')
  rps=$(grep -o "Requests/sec: [0-9.]*" $RESULT_FILE | awk '{print $2}')
  
  if [ -n "$total_requests" ] && [ -n "$success_requests" ]; then
    success_rate=$(echo "scale=2; $success_requests * 100 / $total_requests" | bc)
  else
    success_rate="N/A"
  fi
  
  echo "请求统计:"
  echo "- 总请求数: ${total_requests:-N/A}"
  echo "- 成功请求数: ${success_requests:-0}"
  echo "- 成功率: ${success_rate}%"
  echo "- 请求/秒: ${rps:-N/A}"
  echo ""
  
  echo "响应时间:"
  echo "- 平均响应时间: ${avg_resp_time:-N/A}"
  echo "- 最快响应时间: ${fastest:-N/A}"
  echo "- 最慢响应时间: ${slowest:-N/A}"
  echo ""
  
  echo "响应代码分布:"
  grep -A 10 "Status code distribution:" $RESULT_FILE | grep -v "Status code distribution:" || echo "  无数据"
  
  echo ""
  echo "响应时间分布:"
  grep -A 10 "Response time histogram:" $RESULT_FILE | grep -v "Response time histogram:" | head -n 10 || echo "  无数据"
  
  echo ""
  echo "延迟分布:"
  grep -A 5 "Latency distribution:" $RESULT_FILE | grep -v "Latency distribution:" || echo "  无数据"
} > $SUMMARY_FILE

# 显示摘要
cat $SUMMARY_FILE

log "测试摘要已保存到: $SUMMARY_FILE"
log "压力测试完成!" 