#!/bin/bash
#
# RAG服务健康监控脚本
# 定期检查服务状态，并在出现问题时发送告警
#

set -e

# 配置
LOG_FILE="/var/www/suoke.life/logs/rag-service-monitor.log"
HEALTH_URL="http://localhost:3001/health"
METRICS_URL="http://localhost:3001/metrics"
ALERT_RECIPIENTS="admin@suoke.life,oncall@suoke.life"
SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"
TELEGRAM_TOKEN="${TELEGRAM_TOKEN:-}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-}"

# 创建日志目录
mkdir -p "$(dirname $LOG_FILE)"

# 日志函数
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

# 告警函数
send_alert() {
  local subject="$1"
  local message="$2"
  local severity="${3:-critical}"
  
  log "发送告警: $subject"
  
  # 发送邮件告警
  echo "$message" | mail -s "[${severity}] RAG服务告警: $subject" $ALERT_RECIPIENTS
  
  # Slack告警 (如果配置了Webhook URL)
  if [ -n "$SLACK_WEBHOOK_URL" ]; then
    curl -s -X POST -H 'Content-type: application/json' \
      --data "{\"text\":\"*[${severity}] RAG服务告警*\n$subject\n\n$message\"}" \
      $SLACK_WEBHOOK_URL
  fi
  
  # Telegram告警 (如果配置了Token和Chat ID)
  if [ -n "$TELEGRAM_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
    curl -s -X POST \
      "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
      -d chat_id="$TELEGRAM_CHAT_ID" \
      -d text="*[${severity}] RAG服务告警*%0A$subject%0A%0A$message" \
      -d parse_mode="Markdown"
  fi
}

# 检查API健康状态
check_health() {
  log "检查健康状态..."
  
  local response
  local status_code
  
  response=$(curl -s -w "\n%{http_code}" $HEALTH_URL)
  status_code=$(echo "$response" | tail -n1)
  response_body=$(echo "$response" | sed '$d')
  
  if [ "$status_code" != "200" ]; then
    send_alert "健康检查失败" "健康检查URL返回非200状态码：$status_code"
    return 1
  fi
  
  # 检查JSON响应中的状态
  if echo "$response_body" | grep -q '"status":"unhealthy"'; then
    # 提取不健康组件
    unhealthy_components=$(echo "$response_body" | grep -o '"[^"]*":"unhealthy"' | cut -d'"' -f2)
    send_alert "服务不健康" "以下组件报告不健康状态：\n$unhealthy_components"
    return 1
  fi
  
  log "健康检查通过"
  return 0
}

# 检查资源使用情况
check_resources() {
  log "检查资源使用情况..."
  
  # 获取指标
  local metrics
  metrics=$(curl -s $METRICS_URL)
  
  # 检查内存使用
  local memory_usage
  memory_usage=$(ps -o pid,rss -p $(pgrep -f "rag-service") | awk 'NR>1 {printf "%.2f", $2/1024/1024}')
  
  if (( $(echo "$memory_usage > 1.5" | bc -l) )); then
    send_alert "内存使用过高" "当前内存使用：${memory_usage}GB，超过预警阈值 1.5GB" "warning"
  fi
  
  # 检查CPU使用
  local cpu_usage
  cpu_usage=$(ps -o pid,pcpu -p $(pgrep -f "rag-service") | awk 'NR>1 {print $2}')
  
  if (( $(echo "$cpu_usage > 80" | bc -l) )); then
    send_alert "CPU使用过高" "当前CPU使用：${cpu_usage}%，超过预警阈值 80%" "warning"
  fi
  
  # 检查响应延迟
  local high_latency
  high_latency=$(echo "$metrics" | grep "rag_request_latency_seconds" | grep -oE "[0-9]+\.[0-9]+" | sort -nr | head -1)
  
  if (( $(echo "$high_latency > 5.0" | bc -l) )); then
    send_alert "请求延迟过高" "最高请求延迟：${high_latency}秒，超过预警阈值 5.0秒" "warning"
  fi
  
  # 检查错误率
  local error_count
  local total_requests
  error_count=$(echo "$metrics" | grep "rag_request_total.*status=\"error\"" | grep -oE "[0-9]+" || echo "0")
  total_requests=$(echo "$metrics" | grep "rag_request_total" | grep -oE "[0-9]+" | awk '{s+=$1} END {print s}' || echo "0")
  
  if [ "$total_requests" -gt 0 ]; then
    local error_rate
    error_rate=$(echo "scale=2; $error_count / $total_requests * 100" | bc)
    if (( $(echo "$error_rate > 5" | bc -l) )); then
      send_alert "错误率过高" "当前错误率：${error_rate}%，超过预警阈值 5%" "warning"
    fi
  fi
  
  log "资源检查完成"
}

# 检查磁盘使用
check_disk() {
  log "检查磁盘使用情况..."
  
  # 检查日志目录
  local logs_disk_usage
  logs_disk_usage=$(df -h /var/www/suoke.life/logs | awk 'NR==2 {print $5}' | sed 's/%//')
  
  if [ "$logs_disk_usage" -gt 85 ]; then
    send_alert "日志磁盘使用过高" "日志目录磁盘使用：${logs_disk_usage}%，超过预警阈值 85%" "warning"
  fi
  
  # 检查数据目录
  local data_disk_usage
  data_disk_usage=$(df -h /app/data | awk 'NR==2 {print $5}' | sed 's/%//')
  
  if [ "$data_disk_usage" -gt 85 ]; then
    send_alert "数据磁盘使用过高" "数据目录磁盘使用：${data_disk_usage}%，超过预警阈值 85%" "warning"
  fi
  
  log "磁盘检查完成"
}

# 主函数
main() {
  log "开始监控检查"
  
  # 检查服务进程是否运行
  if ! pgrep -f "rag-service" > /dev/null; then
    send_alert "服务未运行" "RAG服务进程未检测到，可能已停止运行"
    exit 1
  fi
  
  # 运行各项检查
  check_health
  check_resources
  check_disk
  
  log "监控检查完成"
}

# 执行主函数
main "$@" 