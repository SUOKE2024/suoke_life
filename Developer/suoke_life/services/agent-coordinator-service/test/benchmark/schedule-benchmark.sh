#!/bin/bash

# 性能基准测试定期执行脚本
# 建议添加到crontab以定期执行
# 例如，每天凌晨3点执行：
# 0 3 * * * /path/to/services/agent-coordinator-service/test/benchmark/schedule-benchmark.sh

# 配置参数
API_URL=${1:-"http://localhost:4000/api"}  # 默认本地API地址
CONFIG_FILE=${2:-"config.json"}            # 默认配置文件
LOG_DIR=${3:-"logs"}                        # 日志目录
REPORT_DIR=${4:-"reports"}                  # 报告目录
NOTIFY_EMAIL=${5:-""}                       # 通知邮箱（可选）

# 设置脚本目录为工作目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# 创建目录
mkdir -p "$LOG_DIR"
mkdir -p "$REPORT_DIR"

# 日志文件
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/benchmark_$TIMESTAMP.log"
REPORT_FILE="$REPORT_DIR/benchmark_report_$TIMESTAMP.json"

# 日志函数
log() {
  echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1" | tee -a "$LOG_FILE"
}

# 开始测试
log "开始性能基准测试 - API: $API_URL"
log "使用配置文件: $CONFIG_FILE"

# 确认Node环境
if ! command -v node &> /dev/null; then
  log "错误: 未找到Node.js. 请安装Node.js."
  exit 1
fi

# 确认npm依赖已安装
if [ ! -d "node_modules" ]; then
  log "安装npm依赖..."
  npm install >> "$LOG_FILE" 2>&1
  if [ $? -ne 0 ]; then
    log "错误: 安装依赖失败. 请检查日志: $LOG_FILE"
    exit 1
  fi
fi

# 执行基准测试
log "执行基准测试..."
node_modules/.bin/ts-node performance-benchmark.ts --url "$API_URL" --config "$CONFIG_FILE" --output "$REPORT_DIR" >> "$LOG_FILE" 2>&1
BENCHMARK_EXIT_CODE=$?

# 提取关键性能指标
{
  echo "================================================================"
  echo "                索克生活API性能基准测试报告                     "
  echo "================================================================"
  echo "测试时间: $(date)"
  echo "API地址: $API_URL"
  echo "配置文件: $CONFIG_FILE"
  echo "----------------------------------------------------------------"

  # 从日志中提取关键结果行
  grep -A 100 "==== 性能测试结果 ====" "$LOG_FILE" | grep -B 100 -m 1 "结果已保存到:" >> "$REPORT_FILE"
  
  if [ -z "$NOTIFY_EMAIL" ]; then
    # 如果有基准比较，也提取这部分
    grep -A 100 "==== 性能与基准比较 ====" "$LOG_FILE" | grep -B 100 -m 1 "==== 性能阈值检查 ====" >> "$REPORT_FILE"
  
    # 提取阈值检查部分
    grep -A 100 "==== 性能阈值检查 ====" "$LOG_FILE" | grep -v "npm ERR" >> "$REPORT_FILE"
  
    echo "----------------------------------------------------------------"
    if [ $BENCHMARK_EXIT_CODE -eq 0 ]; then
      echo "测试结果: 通过 ✅"
    else
      echo "测试结果: 失败 ❌ (部分指标未达到阈值)"
    fi
    echo "详细日志: $LOG_FILE"
  fi
} > "$REPORT_FILE"

log "性能报告已生成: $REPORT_FILE"

# 发送邮件通知（如果配置了邮箱）
if [ ! -z "$NOTIFY_EMAIL" ]; then
  log "发送测试报告到: $NOTIFY_EMAIL"
  if command -v mail &> /dev/null; then
    SUBJECT="索克生活API性能测试报告 - $(date +"%Y-%m-%d")"
    STATUS_EMOJI=$([ $BENCHMARK_EXIT_CODE -eq 0 ] && echo "✅" || echo "❌")
    mail -s "$SUBJECT $STATUS_EMOJI" "$NOTIFY_EMAIL" < "$REPORT_FILE"
  else
    log "警告: 未找到mail命令，无法发送邮件通知"
  fi
fi

# 退出码
exit $BENCHMARK_EXIT_CODE 