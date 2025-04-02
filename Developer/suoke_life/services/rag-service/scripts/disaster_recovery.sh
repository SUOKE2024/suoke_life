#!/bin/bash
#
# RAG服务灾难恢复演练脚本
# 用于测试和验证RAG服务的灾难恢复能力
#

set -e

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="$SERVICE_DIR/config"
BACKUP_DIR="/var/backups/suoke/rag-service"
DATA_DIR="/var/www/suoke.life/data/vector_store"
LOG_FILE="$SCRIPT_DIR/disaster_recovery_$(date +%Y%m%d).log"
ALERT_EMAIL="admin@suoke.life"
VECTOR_BACKUP_SCRIPT="$SCRIPT_DIR/vector_store_backup.sh"
DEPLOYMENT_SCRIPT="$SCRIPT_DIR/deploy_optimized.sh"

# 颜色代码
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# 日志函数
log() {
  local level=$1
  local message=$2
  local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
  
  case $level in
    "INFO")
      local color=$GREEN
      ;;
    "WARN")
      local color=$YELLOW
      ;;
    "ERROR")
      local color=$RED
      ;;
    *)
      local color=$NC
      ;;
  esac
  
  echo -e "${color}[$timestamp] [$level] $message${NC}" | tee -a "$LOG_FILE"
}

# 发送告警函数
send_alert() {
  local subject="[索克生活-RAG服务] 灾难恢复演练: $1"
  local message="$2"
  log "INFO" "发送告警: $subject"
  
  # 使用mailx发送邮件
  echo -e "$message" | mail -s "$subject" "$ALERT_EMAIL"
}

# 检查必要的工具和权限
check_prerequisites() {
  log "INFO" "检查必要的工具和权限..."
  
  # 检查必要的命令
  for cmd in curl systemctl nginx tar rsync awk grep; do
    if ! command -v $cmd &> /dev/null; then
      log "ERROR" "找不到命令: $cmd"
      return 1
    fi
  done
  
  # 检查备份目录
  if [ ! -d "$BACKUP_DIR" ]; then
    log "ERROR" "备份目录不存在: $BACKUP_DIR"
    return 1
  fi
  
  # 检查数据目录
  if [ ! -d "$DATA_DIR" ]; then
    log "ERROR" "数据目录不存在: $DATA_DIR"
    return 1
  fi
  
  # 检查备份脚本
  if [ ! -f "$VECTOR_BACKUP_SCRIPT" ]; then
    log "ERROR" "向量存储备份脚本不存在: $VECTOR_BACKUP_SCRIPT"
    return 1
  fi
  
  # 检查部署脚本
  if [ ! -f "$DEPLOYMENT_SCRIPT" ]; then
    log "ERROR" "部署脚本不存在: $DEPLOYMENT_SCRIPT"
    return 1
  fi
  
  log "INFO" "先决条件检查通过"
  return 0
}

# 模拟各种灾难场景
simulate_disaster() {
  local scenario=$1
  log "INFO" "开始模拟灾难场景: $scenario"
  
  case $scenario in
    "service_crash")
      log "INFO" "模拟服务崩溃..."
      systemctl stop rag-service
      log "INFO" "RAG服务已停止，模拟崩溃"
      ;;
    "data_corruption")
      log "INFO" "模拟数据损坏..."
      # 创建临时备份
      local temp_backup="/tmp/vector_data_backup_$(date +%Y%m%d%H%M%S).tar.gz"
      tar -czf $temp_backup -C $(dirname $DATA_DIR) $(basename $DATA_DIR)
      log "INFO" "已创建临时备份: $temp_backup"
      
      # 损坏部分数据文件
      find $DATA_DIR -type f -name "*.bin" | sort | head -n 2 | while read file; do
        log "WARN" "损坏数据文件: $file"
        dd if=/dev/urandom of="$file" bs=1024 count=10 conv=notrunc
      done
      ;;
    "database_unavailable")
      log "INFO" "模拟数据库不可用..."
      systemctl stop milvus
      log "INFO" "Milvus服务已停止，模拟数据库不可用"
      ;;
    "network_partition")
      log "INFO" "模拟网络分区..."
      # 使用iptables临时阻断连接
      iptables -A INPUT -p tcp --dport 19530 -j DROP
      log "INFO" "已阻断Milvus端口连接，模拟网络分区"
      ;;
    "full_system_failure")
      log "INFO" "模拟完全系统故障..."
      systemctl stop nginx
      systemctl stop rag-service
      systemctl stop redis
      systemctl stop milvus
      log "INFO" "所有相关服务已停止，模拟完全系统故障"
      ;;
    *)
      log "ERROR" "未知的灾难场景: $scenario"
      return 1
      ;;
  esac
  
  log "INFO" "灾难场景模拟完成: $scenario"
  return 0
}

# 执行恢复步骤
perform_recovery() {
  local scenario=$1
  log "INFO" "开始执行恢复步骤: $scenario"
  
  case $scenario in
    "service_crash")
      log "INFO" "恢复服务崩溃..."
      systemctl start rag-service
      systemctl status rag-service
      ;;
    "data_corruption")
      log "INFO" "恢复数据损坏..."
      # 停止服务
      systemctl stop rag-service
      
      # 从最近的备份恢复
      local latest_backup=$(find $BACKUP_DIR -name "vector_store_*.tar.gz" | sort -r | head -n 1)
      if [ -z "$latest_backup" ]; then
        log "ERROR" "找不到可用的备份"
        return 1
      fi
      
      log "INFO" "使用备份恢复: $latest_backup"
      rm -rf ${DATA_DIR}.corrupted
      mv $DATA_DIR ${DATA_DIR}.corrupted
      mkdir -p $DATA_DIR
      tar -xzf $latest_backup -C $(dirname $DATA_DIR)
      
      # 启动服务
      log "INFO" "启动RAG服务..."
      systemctl start rag-service
      ;;
    "database_unavailable")
      log "INFO" "恢复数据库..."
      systemctl start milvus
      systemctl status milvus
      ;;
    "network_partition")
      log "INFO" "恢复网络连接..."
      iptables -D INPUT -p tcp --dport 19530 -j DROP
      ;;
    "full_system_failure")
      log "INFO" "执行完全系统恢复..."
      
      # 按顺序启动各服务
      log "INFO" "启动Milvus服务..."
      systemctl start milvus
      
      log "INFO" "启动Redis服务..."
      systemctl start redis
      
      log "INFO" "启动RAG服务..."
      systemctl start rag-service
      
      log "INFO" "启动Nginx服务..."
      systemctl start nginx
      
      # 执行部署检查
      log "INFO" "执行部署检查..."
      bash $DEPLOYMENT_SCRIPT --verify-only
      ;;
    *)
      log "ERROR" "未知的灾难场景: $scenario"
      return 1
      ;;
  esac
  
  log "INFO" "恢复步骤执行完成: $scenario"
  return 0
}

# 验证恢复结果
verify_recovery() {
  local scenario=$1
  log "INFO" "开始验证恢复结果: $scenario"
  
  # 检查服务状态
  local service_status=$(systemctl is-active rag-service)
  if [ "$service_status" != "active" ]; then
    log "ERROR" "RAG服务未处于活动状态"
    return 1
  fi
  
  # 检查API可用性
  local api_status=$(curl -s -o /dev/null -w "%{http_code}" https://suoke.life/ai/health)
  if [ "$api_status" != "200" ]; then
    log "ERROR" "API健康检查失败，状态码: $api_status"
    return 1
  fi
  
  # 检查数据完整性
  log "INFO" "检查数据完整性..."
  local query_response=$(curl -s -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" -d '{"query":"健康检查测试","max_tokens":10}' https://suoke.life/ai/rag)
  
  if [ $? -ne 0 ] || ! echo "$query_response" | grep -q "result"; then
    log "ERROR" "数据查询测试失败"
    return 1
  fi
  
  log "INFO" "恢复验证通过: $scenario"
  return 0
}

# 清理函数
cleanup() {
  log "INFO" "开始清理环境..."
  
  case $DISASTER_SCENARIO in
    "service_crash")
      # 确保服务已启动
      systemctl start rag-service 2>/dev/null || true
      ;;
    "data_corruption")
      # 清理临时备份
      rm -f /tmp/vector_data_backup_*.tar.gz
      ;;
    "database_unavailable")
      # 确保数据库已启动
      systemctl start milvus 2>/dev/null || true
      ;;
    "network_partition")
      # 确保网络规则已清理
      iptables -D INPUT -p tcp --dport 19530 -j DROP 2>/dev/null || true
      ;;
    "full_system_failure")
      # 确保所有服务已启动
      systemctl start milvus 2>/dev/null || true
      systemctl start redis 2>/dev/null || true
      systemctl start rag-service 2>/dev/null || true
      systemctl start nginx 2>/dev/null || true
      ;;
  esac
  
  log "INFO" "环境清理完成"
}

# 生成报告
generate_report() {
  local report_file="disaster_recovery_report_$(date +%Y%m%d).html"
  log "INFO" "生成灾难恢复演练报告: $report_file"
  
  cat > $report_file << EOF
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>索克生活RAG服务灾难恢复演练报告</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    h1 { color: #35BB78; }
    .header { border-bottom: 2px solid #35BB78; padding-bottom: 10px; }
    .section { margin: 20px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
    .success { color: green; }
    .failure { color: red; }
    table { width: 100%; border-collapse: collapse; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    th { background-color: #f2f2f2; }
    tr:nth-child(even) { background-color: #f9f9f9; }
    .timestamp { color: #666; font-size: 0.8em; }
  </style>
</head>
<body>
  <div class="header">
    <h1>索克生活RAG服务灾难恢复演练报告</h1>
    <p class="timestamp">生成时间: $(date '+%Y-%m-%d %H:%M:%S')</p>
  </div>
  
  <div class="section">
    <h2>演练概述</h2>
    <p>灾难场景: $DISASTER_SCENARIO</p>
    <p>演练时间: $(date '+%Y-%m-%d %H:%M:%S')</p>
    <p>恢复结果: $([ $RECOVERY_SUCCESS -eq 0 ] && echo '<span class="success">成功</span>' || echo '<span class="failure">失败</span>')</p>
    <p>恢复耗时: ${RECOVERY_TIME}秒</p>
  </div>
  
  <div class="section">
    <h2>灾难场景详情</h2>
    <p>$(case $DISASTER_SCENARIO in
        "service_crash") echo "服务崩溃：模拟RAG服务进程异常终止" ;;
        "data_corruption") echo "数据损坏：模拟向量存储数据文件损坏" ;;
        "database_unavailable") echo "数据库不可用：模拟Milvus服务不可用" ;;
        "network_partition") echo "网络分区：模拟网络连接中断" ;;
        "full_system_failure") echo "完全系统故障：模拟所有相关服务同时故障" ;;
      esac)</p>
  </div>
  
  <div class="section">
    <h2>恢复步骤</h2>
    <ol>
      $(grep -E "\[INFO\].*恢复" $LOG_FILE | sed 's/.*\[INFO\] /      <li>/g' | sed 's/$/\<\/li\>/g')
    </ol>
  </div>
  
  <div class="section">
    <h2>系统状态</h2>
    <table>
      <tr>
        <th>服务名称</th>
        <th>故障前状态</th>
        <th>故障状态</th>
        <th>恢复后状态</th>
      </tr>
      <tr>
        <td>RAG服务</td>
        <td>${PRE_STATUS_RAG}</td>
        <td>${DISASTER_STATUS_RAG}</td>
        <td>${POST_STATUS_RAG}</td>
      </tr>
      <tr>
        <td>Milvus</td>
        <td>${PRE_STATUS_MILVUS}</td>
        <td>${DISASTER_STATUS_MILVUS}</td>
        <td>${POST_STATUS_MILVUS}</td>
      </tr>
      <tr>
        <td>Redis</td>
        <td>${PRE_STATUS_REDIS}</td>
        <td>${DISASTER_STATUS_REDIS}</td>
        <td>${POST_STATUS_REDIS}</td>
      </tr>
      <tr>
        <td>Nginx</td>
        <td>${PRE_STATUS_NGINX}</td>
        <td>${DISASTER_STATUS_NGINX}</td>
        <td>${POST_STATUS_NGINX}</td>
      </tr>
    </table>
  </div>
  
  <div class="section">
    <h2>验证测试</h2>
    <table>
      <tr>
        <th>测试项目</th>
        <th>结果</th>
        <th>详情</th>
      </tr>
      <tr>
        <td>服务状态检查</td>
        <td>$([ "$POST_STATUS_RAG" == "active" ] && echo '<span class="success">通过</span>' || echo '<span class="failure">失败</span>')</td>
        <td>服务状态: $POST_STATUS_RAG</td>
      </tr>
      <tr>
        <td>API健康检查</td>
        <td>$([ "$API_STATUS" == "200" ] && echo '<span class="success">通过</span>' || echo '<span class="failure">失败</span>')</td>
        <td>状态码: $API_STATUS</td>
      </tr>
      <tr>
        <td>数据完整性检查</td>
        <td>$([ "$DATA_INTEGRITY" == "通过" ] && echo '<span class="success">通过</span>' || echo '<span class="failure">失败</span>')</td>
        <td>$DATA_INTEGRITY_DETAIL</td>
      </tr>
    </table>
  </div>
  
  <div class="section">
    <h2>总结与建议</h2>
    <p>$([ $RECOVERY_SUCCESS -eq 0 ] && echo "本次灾难恢复演练成功完成，系统展示了良好的恢复能力。" || echo "本次灾难恢复演练未能成功完成，需要进一步改进灾难恢复流程。")</p>
    <p>恢复耗时: ${RECOVERY_TIME}秒 $([ $RECOVERY_TIME -gt 300 ] && echo "（超过预期，建议优化恢复流程）" || echo "（符合预期范围）")</p>
    <h3>改进建议:</h3>
    <ul>
      <li>$([ $RECOVERY_TIME -gt 300 ] && echo "优化恢复流程，减少恢复时间" || echo "继续定期进行灾难恢复演练，确保团队熟悉恢复流程")</li>
      <li>$([ "$DATA_INTEGRITY" != "通过" ] && echo "增强数据备份策略，确保数据完整性" || echo "考虑增加自动化恢复机制，减少人工干预")</li>
      <li>实施更全面的监控系统，提前发现潜在问题</li>
    </ul>
  </div>
</body>
</html>
EOF
  
  log "INFO" "报告已生成: $report_file"
}

# 主函数
main() {
  # 记录开始时间
  START_TIME=$(date +%s)
  
  # 初始化日志文件
  : > "$LOG_FILE"
  
  log "INFO" "==== 开始灾难恢复演练 ===="
  
  # 解析命令行参数
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --scenario)
        DISASTER_SCENARIO="$2"
        shift 2
        ;;
      --api-key)
        API_KEY="$2"
        shift 2
        ;;
      --help)
        echo "用法: $0 [选项]"
        echo ""
        echo "选项:"
        echo "  --scenario TYPE     灾难场景类型 (service_crash, data_corruption,"
        echo "                      database_unavailable, network_partition, full_system_failure)"
        echo "  --api-key KEY       API密钥 (用于测试验证)"
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
  
  # 检查参数
  if [ -z "$DISASTER_SCENARIO" ]; then
    log "ERROR" "未指定灾难场景类型"
    echo "使用 --help 查看帮助"
    exit 1
  fi
  
  # 记录系统初始状态
  PRE_STATUS_RAG=$(systemctl is-active rag-service || echo "inactive")
  PRE_STATUS_MILVUS=$(systemctl is-active milvus || echo "inactive")
  PRE_STATUS_REDIS=$(systemctl is-active redis || echo "inactive")
  PRE_STATUS_NGINX=$(systemctl is-active nginx || echo "inactive")
  
  # 检查先决条件
  if ! check_prerequisites; then
    log "ERROR" "先决条件检查失败，无法继续"
    exit 1
  fi
  
  # 模拟灾难
  if ! simulate_disaster "$DISASTER_SCENARIO"; then
    log "ERROR" "模拟灾难失败"
    cleanup
    exit 1
  fi
  
  # 记录灾难状态
  DISASTER_STATUS_RAG=$(systemctl is-active rag-service || echo "inactive")
  DISASTER_STATUS_MILVUS=$(systemctl is-active milvus || echo "inactive")
  DISASTER_STATUS_REDIS=$(systemctl is-active redis || echo "inactive")
  DISASTER_STATUS_NGINX=$(systemctl is-active nginx || echo "inactive")
  
  # 执行恢复
  RECOVERY_SUCCESS=0
  if ! perform_recovery "$DISASTER_SCENARIO"; then
    log "ERROR" "恢复步骤执行失败"
    RECOVERY_SUCCESS=1
  fi
  
  # 记录恢复状态
  POST_STATUS_RAG=$(systemctl is-active rag-service || echo "inactive")
  POST_STATUS_MILVUS=$(systemctl is-active milvus || echo "inactive")
  POST_STATUS_REDIS=$(systemctl is-active redis || echo "inactive")
  POST_STATUS_NGINX=$(systemctl is-active nginx || echo "inactive")
  
  # 验证恢复
  if [ $RECOVERY_SUCCESS -eq 0 ]; then
    if ! verify_recovery "$DISASTER_SCENARIO"; then
      log "ERROR" "恢复验证失败"
      RECOVERY_SUCCESS=1
    fi
  fi
  
  # 检查API状态
  API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://suoke.life/ai/health || echo "failed")
  
  # 检查数据完整性
  if [ -n "$API_KEY" ]; then
    local query_response=$(curl -s -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" -d '{"query":"健康检查测试","max_tokens":10}' https://suoke.life/ai/rag)
    if [ $? -eq 0 ] && echo "$query_response" | grep -q "result"; then
      DATA_INTEGRITY="通过"
      DATA_INTEGRITY_DETAIL="成功执行查询并获得结果"
    else
      DATA_INTEGRITY="失败"
      DATA_INTEGRITY_DETAIL="查询执行失败或结果异常"
    fi
  else
    DATA_INTEGRITY="跳过"
    DATA_INTEGRITY_DETAIL="未提供API密钥，跳过测试"
  fi
  
  # 记录结束时间并计算恢复时间
  END_TIME=$(date +%s)
  RECOVERY_TIME=$((END_TIME - START_TIME))
  
  # 生成报告
  generate_report
  
  # 清理环境
  cleanup
  
  log "INFO" "==== 灾难恢复演练结束 ===="
  log "INFO" "恢复耗时: ${RECOVERY_TIME}秒"
  log "INFO" "恢复结果: $([ $RECOVERY_SUCCESS -eq 0 ] && echo "成功" || echo "失败")"
  
  # 发送结果告警
  if [ $RECOVERY_SUCCESS -eq 0 ]; then
    send_alert "恢复演练成功" "灾难场景: $DISASTER_SCENARIO\n恢复耗时: ${RECOVERY_TIME}秒\n\n详情请查看完整报告。"
  else
    send_alert "恢复演练失败" "灾难场景: $DISASTER_SCENARIO\n恢复耗时: ${RECOVERY_TIME}秒\n\n请尽快检查系统状态并解决问题。详情请查看完整报告。"
  fi
  
  return $RECOVERY_SUCCESS
}

# 脚本入口
main "$@" 