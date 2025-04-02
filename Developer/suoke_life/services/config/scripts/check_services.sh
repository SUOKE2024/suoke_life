#!/bin/bash
# 索克生活服务检查和自动启动脚本
# 版本：1.1
# 更新日期：2024-03-29

# 配置参数
LOG_FILE="/var/log/suoke_services.log"
LOG_DIR="/var/log/suoke"
EMAIL_ALERT="admin@suoke.life" # 替换为实际的管理员邮箱
SLACK_WEBHOOK="" # 可选的Slack通知
MAX_LOG_SIZE=10485760 # 10MB

# 服务器IP和服务配置
declare -A SERVERS
SERVERS=(
  ["172.16.199.86"]="核心服务器:api-gateway,auth-service,user-service"
  ["172.16.199.136"]="AI服务器:ai-service,rag-service,embeddings-service"
  ["172.16.199.88"]="数据库服务器:mysql,redis,vector-db"
)

# 健康检查URL (可选)
declare -A HEALTH_CHECKS
HEALTH_CHECKS=(
  ["api-gateway"]="http://172.16.199.86:3000/health"
  ["auth-service"]="http://172.16.199.86:3001/health"
  ["user-service"]="http://172.16.199.86:3002/health"
  ["ai-service"]="http://172.16.199.136:5000/health"
  ["rag-service"]="http://172.16.199.136:5001/health"
)

# 创建日志目录
mkdir -p $LOG_DIR

# 确保日志文件存在
touch $LOG_FILE

# 日志轮转函数
rotate_logs() {
  if [ -f "$LOG_FILE" ] && [ $(stat -c%s "$LOG_FILE") -gt $MAX_LOG_SIZE ]; then
    timestamp=$(date +"%Y%m%d_%H%M%S")
    mv "$LOG_FILE" "${LOG_DIR}/suoke_services_${timestamp}.log"
    gzip "${LOG_DIR}/suoke_services_${timestamp}.log"
    touch "$LOG_FILE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 日志已轮转" >> $LOG_FILE
    
    # 清理旧日志文件 (保留最近30天)
    find $LOG_DIR -name "suoke_services_*.log.gz" -type f -mtime +30 -delete
  fi
}

# 日志函数
log_message() {
  rotate_logs
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> $LOG_FILE
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 发送告警
send_alert() {
  local subject="$1"
  local message="$2"
  local severity="${3:-警告}"  # 默认为警告级别
  
  # 邮件告警
  if command -v mail > /dev/null; then
    echo -e "级别: ${severity}\n时间: $(date '+%Y-%m-%d %H:%M:%S')\n\n${message}" | mail -s "[${severity}] ${subject}" "$EMAIL_ALERT"
    log_message "已发送告警邮件到 $EMAIL_ALERT"
  else
    log_message "邮件客户端不可用，无法发送告警"
  fi
  
  # Slack告警 (如果配置了Webhook)
  if [ -n "$SLACK_WEBHOOK" ]; then
    curl -s -X POST -H 'Content-type: application/json' \
      --data "{\"text\":\"*[${severity}] ${subject}*\n${message}\"}" \
      $SLACK_WEBHOOK
    log_message "已发送告警到Slack"
  fi
}

# 健康检查函数
check_health_endpoint() {
  local service="$1"
  local url="${HEALTH_CHECKS[$service]}"
  
  if [ -z "$url" ]; then
    return 0  # 无健康检查配置，视为通过
  fi
  
  log_message "检查 $service 健康状态: $url"
  
  local http_code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 --max-time 10 "$url")
  
  if [ "$http_code" -eq 200 ]; then
    log_message "$service 健康检查通过"
    return 0
  else
    log_message "警告: $service 健康检查失败，HTTP状态码: $http_code"
    return 1
  fi
}

# 检查系统资源状态
check_system_resources() {
  local server="$1"
  local server_name="$2"
  
  log_message "检查 ${server_name} (${server}) 的系统资源..."
  
  ssh -o ConnectTimeout=5 root@$server "
    echo '*** 系统资源信息 ***'
    
    # CPU负载
    echo -n 'CPU负载: '
    uptime | awk -F'load average:' '{print \$2}'
    
    # 内存使用
    echo '内存使用情况:'
    free -m | grep -v +
    
    # 磁盘使用
    echo '磁盘使用情况:'
    df -h / | grep -v 'Filesystem'
    
    # 检查高CPU进程
    echo '前5个CPU使用最高的进程:'
    ps aux --sort=-%cpu | head -6
    
    # 检查内存泄漏
    echo '前5个内存使用最高的进程:'
    ps aux --sort=-%mem | head -6
    
    # 检查服务器运行时间
    echo -n '服务器运行时间: '
    uptime -p
  " 2>&1 | while read line; do
    log_message "${server_name}: $line"
  done
  
  # 检查资源阈值并发出警告
  ssh -o ConnectTimeout=5 root@$server "
    # 检查CPU负载是否过高
    load=\$(cut -d ' ' -f1 /proc/loadavg)
    cores=\$(nproc)
    if (( \$(echo \"\$load > \$cores * 0.8\" | bc -l) )); then
      echo \"WARNING_CPU_LOAD:\$load\"
    fi
    
    # 检查内存使用是否过高
    mem_used_percent=\$(free | grep Mem | awk '{print \$3/\$2 * 100.0}')
    if (( \$(echo \"\$mem_used_percent > 85\" | bc -l) )); then
      echo \"WARNING_MEM_USAGE:\$mem_used_percent%\"
    fi
    
    # 检查磁盘使用是否过高
    disk_used_percent=\$(df / | grep / | awk '{print \$5}' | tr -d '%')
    if [ \"\$disk_used_percent\" -gt 85 ]; then
      echo \"WARNING_DISK_USAGE:\$disk_used_percent%\"
    fi
  " 2>&1 | grep "^WARNING_" | while read line; do
    case "$line" in
      WARNING_CPU_LOAD:*)
        cpu_load="${line#WARNING_CPU_LOAD:}"
        send_alert "系统资源警告" "${server_name} CPU负载过高: ${cpu_load}" "告警"
        ;;
      WARNING_MEM_USAGE:*)
        mem_usage="${line#WARNING_MEM_USAGE:}"
        send_alert "系统资源警告" "${server_name} 内存使用率过高: ${mem_usage}" "告警"
        ;;
      WARNING_DISK_USAGE:*)
        disk_usage="${line#WARNING_DISK_USAGE:}"
        send_alert "系统资源警告" "${server_name} 磁盘使用率过高: ${disk_usage}" "告警"
        ;;
    esac
  done
}

# 检查并启动核心服务器上的服务
check_core_services() {
  log_message "检查核心服务器 (172.16.199.86) 上的服务..."
  
  if ! ping -c 1 -W 2 172.16.199.86 > /dev/null; then
    log_message "警告: 无法连接到核心服务器"
    send_alert "索克生活服务警告" "无法连接到核心服务器 (172.16.199.86)" "严重"
    return 1
  fi
  
  # 检查系统资源
  check_system_resources "172.16.199.86" "核心服务器"
  
  # 尝试SSH连接并检查服务
  ssh -o ConnectTimeout=5 root@172.16.199.86 "
    # 检查和启动 API 网关
    if ! systemctl is-active --quiet api-gateway; then
      systemctl start api-gateway
      echo '启动 API 网关服务'
      # 等待服务启动
      sleep 5
      if ! systemctl is-active --quiet api-gateway; then
        echo '错误: API 网关服务启动失败'
        journalctl -u api-gateway -n 20 --no-pager
      fi
    else
      echo 'API 网关服务正在运行'
    fi
    
    # 检查和启动认证服务
    if ! systemctl is-active --quiet auth-service; then
      systemctl start auth-service
      echo '启动认证服务'
      # 等待服务启动
      sleep 5
      if ! systemctl is-active --quiet auth-service; then
        echo '错误: 认证服务启动失败'
        journalctl -u auth-service -n 20 --no-pager
      fi
    else
      echo '认证服务正在运行'
    fi
    
    # 检查和启动用户服务
    if ! systemctl is-active --quiet user-service; then
      systemctl start user-service
      echo '启动用户服务'
      # 等待服务启动
      sleep 5
      if ! systemctl is-active --quiet user-service; then
        echo '错误: 用户服务启动失败'
        journalctl -u user-service -n 20 --no-pager
      fi
    else
      echo '用户服务正在运行'
    fi
    
    # 检查Docker容器（如果使用Docker）
    if command -v docker > /dev/null; then
      if ! docker ps | grep -q api-gateway; then
        docker start api-gateway || docker run -d --name api-gateway -p 3000:3000 suoke/api-gateway:latest
        echo '启动 API 网关容器'
      fi
    fi
    
    # 检查NodeJS进程
    if ! pgrep -f 'node.*api-gateway' > /dev/null; then
      echo '警告: 未检测到 API 网关进程'
    fi
    
    # 检查端口
    if ! netstat -tuln | grep -q ':3000'; then
      echo '警告: API 网关端口 3000 未在监听'
    fi
    
    # 检查端口80是否被监听
    if ! netstat -tuln | grep -q ':80'; then
      echo '警告: 核心服务器的80端口未被占用'
    else
      echo '核心服务器的80端口被占用'
    fi
    
    # 返回服务状态摘要
    echo 'API网关状态: '$(systemctl is-active api-gateway)
    echo '认证服务状态: '$(systemctl is-active auth-service)
    echo '用户服务状态: '$(systemctl is-active user-service)
  " 2>&1 | while read line; do
    log_message "核心服务器: $line"
  done
  
  # 执行健康检查
  check_health_endpoint "api-gateway"
  check_health_endpoint "auth-service"
  check_health_endpoint "user-service"
}

# 检查并启动AI服务器上的服务
check_ai_services() {
  log_message "检查AI服务器 (172.16.199.136) 上的服务..."
  
  if ! ping -c 1 -W 2 172.16.199.136 > /dev/null; then
    log_message "警告: 无法连接到AI服务器"
    send_alert "索克生活服务警告" "无法连接到AI服务器 (172.16.199.136)" "严重"
    return 1
  fi
  
  # 检查系统资源
  check_system_resources "172.16.199.136" "AI服务器"
  
  # 尝试SSH连接并检查服务
  ssh -o ConnectTimeout=5 root@172.16.199.136 "
    # 检查和启动 AI 服务
    if ! systemctl is-active --quiet ai-service; then
      systemctl start ai-service
      echo '启动 AI 服务'
      # 等待服务启动
      sleep 5
      if ! systemctl is-active --quiet ai-service; then
        echo '错误: AI 服务启动失败'
        journalctl -u ai-service -n 20 --no-pager
      fi
    else
      echo 'AI 服务正在运行'
    fi
    
    # 检查和启动 RAG 服务
    if ! systemctl is-active --quiet rag-service; then
      systemctl start rag-service
      echo '启动 RAG 服务'
      # 等待服务启动
      sleep 5
      if ! systemctl is-active --quiet rag-service; then
        echo '错误: RAG 服务启动失败'
        journalctl -u rag-service -n 20 --no-pager
      fi
    else
      echo 'RAG 服务正在运行'
    fi
    
    # 检查和启动 Embeddings 服务
    if ! systemctl is-active --quiet embeddings-service; then
      systemctl start embeddings-service
      echo '启动 Embeddings 服务'
      # 等待服务启动
      sleep 5
      if ! systemctl is-active --quiet embeddings-service; then
        echo '错误: Embeddings 服务启动失败'
        journalctl -u embeddings-service -n 20 --no-pager
      fi
    else
      echo 'Embeddings 服务正在运行'
    fi
    
    # 检查Docker容器
    if command -v docker > /dev/null; then
      if ! docker ps | grep -q llm-server; then
        docker start llm-server || docker run -d --name llm-server -p 8000:8000 suoke/llm-server:latest
        echo '启动 LLM 服务容器'
      fi
    fi
    
    # 检查端口80是否被监听
    if ! netstat -tuln | grep -q ':80'; then
      echo '警告: AI服务器的80端口未被占用'
    else
      echo 'AI服务器的80端口被占用'
    fi
    
    # 返回服务状态摘要
    echo 'AI服务状态: '$(systemctl is-active ai-service)
    echo 'RAG服务状态: '$(systemctl is-active rag-service)
    echo 'Embeddings服务状态: '$(systemctl is-active embeddings-service)
  " 2>&1 | while read line; do
    log_message "AI服务器: $line"
  done
  
  # 执行健康检查
  check_health_endpoint "ai-service"
  check_health_endpoint "rag-service"
  check_health_endpoint "embeddings-service"
}

# 检查并启动数据库服务器上的服务
check_db_services() {
  log_message "检查数据库服务器 (172.16.199.88) 上的服务..."
  
  if ! ping -c 1 -W 2 172.16.199.88 > /dev/null; then
    log_message "警告: 无法连接到数据库服务器"
    send_alert "索克生活服务警告" "无法连接到数据库服务器 (172.16.199.88)" "严重"
    return 1
  fi
  
  # 检查系统资源
  check_system_resources "172.16.199.88" "数据库服务器"
  
  # 尝试SSH连接并检查服务
  ssh -o ConnectTimeout=5 root@172.16.199.88 "
    # 检查和启动 MySQL 服务
    if ! systemctl is-active --quiet mysql; then
      systemctl start mysql
      echo '启动 MySQL 服务'
      # 等待服务启动
      sleep 5
      if ! systemctl is-active --quiet mysql; then
        echo '错误: MySQL 服务启动失败'
        journalctl -u mysql -n 20 --no-pager
      fi
    else
      echo 'MySQL 服务正在运行'
    fi
    
    # 检查和启动 Redis 服务
    if ! systemctl is-active --quiet redis; then
      systemctl start redis
      echo '启动 Redis 服务'
      # 等待服务启动
      sleep 5
      if ! systemctl is-active --quiet redis; then
        echo '错误: Redis 服务启动失败'
        journalctl -u redis -n 20 --no-pager
      fi
    else
      echo 'Redis 服务正在运行'
    fi
    
    # 检查和启动向量数据库服务
    if ! systemctl is-active --quiet vector-db; then
      systemctl start vector-db
      echo '启动向量数据库服务'
      # 等待服务启动
      sleep 5
      if ! systemctl is-active --quiet vector-db; then
        echo '错误: 向量数据库服务启动失败'
        journalctl -u vector-db -n 20 --no-pager
      fi
    else
      echo '向量数据库服务正在运行'
    fi
    
    # 检查Docker容器
    if command -v docker > /dev/null; then
      if ! docker ps | grep -q milvus; then
        docker start milvus || docker run -d --name milvus -p 19530:19530 milvusdb/milvus:latest
        echo '启动 Milvus 向量数据库容器'
      fi
    fi
    
    # 检查端口80是否被监听
    if ! netstat -tuln | grep -q ':80'; then
      echo '警告: 数据库服务器的80端口未被占用'
    else
      echo '数据库服务器的80端口被占用'
    fi
    
    # 返回服务状态摘要
    echo 'MySQL状态: '$(systemctl is-active mysql)
    echo 'Redis状态: '$(systemctl is-active redis)
    echo '向量数据库状态: '$(systemctl is-active vector-db)
  " 2>&1 | while read line; do
    log_message "数据库服务器: $line"
  done
  
  # 执行健康检查
  check_health_endpoint "mysql"
  check_health_endpoint "redis"
  check_health_endpoint "vector-db"
}

# 检查并配置Nginx服务
check_nginx() {
  log_message "检查本地Nginx服务..."
  
  if ! systemctl is-active --quiet nginx; then
    systemctl start nginx
    log_message "启动Nginx服务"
  else
    log_message "Nginx服务正在运行"
  fi
  
  # 检查Nginx配置
  nginx -t 2>&1 | while read line; do
    log_message "Nginx配置检查: $line"
  done
  
  # 检查是否有配置更新
  if [ -f /etc/nginx/conf.d/suoke.conf.new ]; then
    log_message "发现新的Nginx配置文件，尝试应用..."
    mv /etc/nginx/conf.d/suoke.conf.new /etc/nginx/conf.d/suoke.conf
    nginx -t && systemctl reload nginx
    log_message "Nginx配置已更新并重新加载"
  fi
}

# 生成状态报告
generate_status_report() {
  local report_file="${LOG_DIR}/status_report_$(date '+%Y%m%d').txt"
  
  {
    echo "==============================================="
    echo "索克生活服务状态报告 - $(date '+%Y-%m-%d %H:%M:%S')"
    echo "==============================================="
    echo ""
    
    # 核心服务状态摘要
    echo "## 核心服务状态"
    ssh -o ConnectTimeout=5 root@172.16.199.86 "
      echo 'API网关: '$(systemctl is-active api-gateway 2>/dev/null || echo '未知')
      echo '认证服务: '$(systemctl is-active auth-service 2>/dev/null || echo '未知')
      echo '用户服务: '$(systemctl is-active user-service 2>/dev/null || echo '未知')
    " 2>/dev/null || echo "无法连接到核心服务器"
    
    echo ""
    echo "## AI服务状态"
    ssh -o ConnectTimeout=5 root@172.16.199.136 "
      echo 'AI服务: '$(systemctl is-active ai-service 2>/dev/null || echo '未知')
      echo 'RAG服务: '$(systemctl is-active rag-service 2>/dev/null || echo '未知')
      echo 'Embeddings服务: '$(systemctl is-active embeddings-service 2>/dev/null || echo '未知')
    " 2>/dev/null || echo "无法连接到AI服务器"
    
    echo ""
    echo "## 数据库服务状态"
    ssh -o ConnectTimeout=5 root@172.16.199.88 "
      echo 'MySQL: '$(systemctl is-active mysql 2>/dev/null || echo '未知')
      echo 'Redis: '$(systemctl is-active redis 2>/dev/null || echo '未知')
      echo '向量数据库: '$(systemctl is-active vector-db 2>/dev/null || echo '未知')
    " 2>/dev/null || echo "无法连接到数据库服务器"
    
    echo ""
    echo "## Nginx状态"
    echo "Nginx: $(systemctl is-active nginx 2>/dev/null || echo '未知')"
    
    echo ""
    echo "## 系统资源摘要"
    echo "### 本机"
    echo "负载: $(uptime | awk -F'load average:' '{print $2}')"
    echo "内存: $(free -h | grep "Mem:" | awk '{print "已用: " $3 " / 总计: " $2}')"
    echo "磁盘: $(df -h / | grep -v 'Filesystem' | awk '{print "已用: " $3 " / 总计: " $2 " (" $5 ")"}')"
    
    echo ""
    echo "==============================================="
    echo "生成时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "报告完成"
  } > "$report_file"
  
  log_message "状态报告已生成: $report_file"
}

# 主函数
main() {
  log_message "开始检查索克生活服务..."
  
  # 检测脚本重复运行
  if pidof -o %PPID -x $(basename "$0") > /dev/null; then
    log_message "警告: 检测到脚本已经在运行，退出..."
    exit 1
  fi
  
  # 检查各服务器上的服务
  check_core_services
  check_ai_services
  check_db_services
  check_nginx
  
  # 生成状态报告
  generate_status_report
  
  log_message "服务检查完成"
}

# 执行主函数
main "$@"

exit 0 