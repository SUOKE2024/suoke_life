#!/bin/bash
# 自动配置脚本 - 配置服务器之间的SSH免密登录
# 版本：1.0
# 更新日期：2024-03-22

# 配置参数
LOG_FILE="/var/log/suoke_auto_config.log"
SSH_KEY_PATH="/root/.ssh/id_rsa"
CONFIG_DIR="/opt/config"
KNOWN_HOSTS="/root/.ssh/known_hosts"

# 服务器列表
MAIN_SERVER="118.31.223.213"
CORE_SERVER="172.16.199.86"
AI_SERVER="172.16.199.136"
DB_SERVER="172.16.199.88"

# 服务器描述
SERVER_NAMES=(
  "$MAIN_SERVER:主服务器"
  "$CORE_SERVER:核心服务器"
  "$AI_SERVER:AI服务器"
  "$DB_SERVER:数据库服务器"
)

# 服务定义
declare -A SERVICES
SERVICES=(
  ["$CORE_SERVER"]="api-gateway,auth-service,user-service"
  ["$AI_SERVER"]="ai-service,rag-service,embeddings-service"
  ["$DB_SERVER"]="mysql,redis,vector-db"
)

# 确保日志文件存在
touch $LOG_FILE
mkdir -p $CONFIG_DIR

# 日志函数
log_message() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> $LOG_FILE
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 检查命令是否存在
check_command() {
  if ! command -v $1 &> /dev/null; then
    log_message "错误: 命令 '$1' 不存在，请先安装"
    return 1
  fi
  return 0
}

# 生成SSH密钥（如果不存在）
generate_ssh_key() {
  log_message "检查SSH密钥..."
  
  if [ ! -f "$SSH_KEY_PATH" ]; then
    log_message "SSH密钥不存在，正在生成..."
    ssh-keygen -t rsa -b 4096 -f "$SSH_KEY_PATH" -N "" <<< y
    log_message "SSH密钥已生成"
  else
    log_message "SSH密钥已存在"
  fi
}

# 配置服务器之间的SSH免密登录
configure_ssh_access() {
  local target_server="$1"
  local server_name="$2"
  
  log_message "配置到 $server_name ($target_server) 的SSH免密登录..."
  
  # 检查是否可以ping通
  if ! ping -c 1 -W 2 $target_server &> /dev/null; then
    log_message "警告: 无法ping通 $server_name ($target_server)，跳过SSH配置"
    return 1
  fi
  
  # 检查是否已经配置了SSH免密登录
  if ssh -o BatchMode=yes -o ConnectTimeout=5 -o StrictHostKeyChecking=no root@$target_server "echo 测试连接" &> /dev/null; then
    log_message "SSH免密登录到 $server_name ($target_server) 已经配置"
    return 0
  fi
  
  # 复制SSH公钥到目标服务器
  log_message "复制SSH公钥到 $server_name ($target_server)..."
  
  # 使用sshpass尝试复制SSH公钥（需要手动输入密码）
  if check_command "sshpass"; then
    log_message "请输入 $server_name ($target_server) 的root密码："
    read -s root_password
    
    if sshpass -p "$root_password" ssh-copy-id -o StrictHostKeyChecking=no root@$target_server &> /dev/null; then
      log_message "SSH公钥已成功复制到 $server_name ($target_server)"
      return 0
    else
      log_message "警告: 使用sshpass复制SSH公钥失败"
    fi
  fi
  
  # 手动方式复制SSH公钥
  log_message "请手动输入以下命令，将SSH公钥复制到 $server_name ($target_server)："
  log_message "ssh-copy-id -o StrictHostKeyChecking=no root@$target_server"
  log_message "完成后请按回车键继续..."
  read
  
  # 验证是否成功配置
  if ssh -o BatchMode=yes -o ConnectTimeout=5 root@$target_server "echo 测试连接" &> /dev/null; then
    log_message "SSH免密登录到 $server_name ($target_server) 配置成功"
    return 0
  else
    log_message "警告: SSH免密登录到 $server_name ($target_server) 配置失败"
    return 1
  fi
}

# 检查和更新服务器上的服务
check_and_update_services() {
  local target_server="$1"
  local server_name="$2"
  local services="${SERVICES[$target_server]}"
  
  log_message "检查 $server_name ($target_server) 上的服务..."
  
  # 检查是否可以SSH连接
  if ! ssh -o BatchMode=yes -o ConnectTimeout=5 root@$target_server "echo 测试连接" &> /dev/null; then
    log_message "警告: 无法SSH连接到 $server_name ($target_server)，跳过服务检查"
    return 1
  fi
  
  # 检查服务
  for service in ${services//,/ }; do
    log_message "检查服务: $service"
    
    if ssh root@$target_server "systemctl is-active --quiet $service" &> /dev/null; then
      log_message "服务 $service 正在运行"
    else
      log_message "警告: 服务 $service 未运行，尝试启动..."
      ssh root@$target_server "systemctl start $service" &> /dev/null
      
      if ssh root@$target_server "systemctl is-active --quiet $service" &> /dev/null; then
        log_message "服务 $service 已成功启动"
      else
        log_message "错误: 无法启动服务 $service"
      fi
    fi
  done
}

# 配置HTTP服务
configure_http_services() {
  local target_server="$1"
  local server_name="$2"
  
  log_message "配置 $server_name ($target_server) 上的HTTP服务..."
  
  # 检查是否可以SSH连接
  if ! ssh -o BatchMode=yes -o ConnectTimeout=5 root@$target_server "echo 测试连接" &> /dev/null; then
    log_message "警告: 无法SSH连接到 $server_name ($target_server)，跳过HTTP服务配置"
    return 1
  fi
  
  # 检查是否安装了Nginx
  if ssh root@$target_server "command -v nginx" &> /dev/null; then
    log_message "Nginx已安装"
    
    # 检查Nginx是否运行
    if ssh root@$target_server "systemctl is-active --quiet nginx" &> /dev/null; then
      log_message "Nginx服务正在运行"
    else
      log_message "Nginx服务未运行，尝试启动..."
      ssh root@$target_server "systemctl start nginx" &> /dev/null
      
      if ssh root@$target_server "systemctl is-active --quiet nginx" &> /dev/null; then
        log_message "Nginx服务已成功启动"
      else
        log_message "错误: 无法启动Nginx服务"
      fi
    fi
    
    # 检查80端口是否被占用
    if ssh root@$target_server "netstat -tuln | grep ':80'" &> /dev/null; then
      log_message "端口80已被占用，HTTP服务可能已配置"
    else
      log_message "警告: 端口80未被占用，HTTP服务可能未配置"
      
      # 如果是核心服务器，配置API网关
      if [ "$target_server" = "$CORE_SERVER" ]; then
        log_message "配置核心服务器上的API网关..."
        
        # 创建简单的Nginx配置
        local nginx_config="server {
    listen 80;
    server_name $target_server;
    
    location /api/ {
        proxy_pass http://127.0.0.1:3000/api/;
        include /etc/nginx/conf.d/proxy_params;
    }
    
    location /api/v1/auth/ {
        proxy_pass http://127.0.0.1:3001/api/v1/auth/;
        include /etc/nginx/conf.d/proxy_params;
    }
    
    location /health {
        return 200 'API Gateway is running';
    }
}"
        
        # 复制Nginx配置
        echo "$nginx_config" > "$CONFIG_DIR/api_gateway.conf"
        scp "$CONFIG_DIR/api_gateway.conf" root@$target_server:/etc/nginx/conf.d/default.conf
        
        # 复制proxy_params
        scp /etc/nginx/conf.d/proxy_params root@$target_server:/etc/nginx/conf.d/proxy_params
        
        # 重新加载Nginx配置
        ssh root@$target_server "nginx -t && systemctl reload nginx" &> /dev/null
        log_message "API网关配置已更新"
      fi
    fi
  else
    log_message "警告: Nginx未安装，跳过HTTP配置"
  fi
}

# 主函数
main() {
  log_message "========== 开始自动配置 =========="
  
  # 检查必要的命令
  check_command "ssh" || exit 1
  check_command "scp" || exit 1
  check_command "ping" || exit 1
  
  # 生成SSH密钥
  generate_ssh_key
  
  # 配置到每个服务器的SSH免密登录
  for server_info in "${SERVER_NAMES[@]}"; do
    IFS=':' read -r server_ip server_name <<< "$server_info"
    
    # 跳过主服务器自身
    if [ "$server_ip" = "$MAIN_SERVER" ]; then
      continue
    fi
    
    configure_ssh_access "$server_ip" "$server_name"
  done
  
  # 更新每个服务器上的服务
  for server_info in "${SERVER_NAMES[@]}"; do
    IFS=':' read -r server_ip server_name <<< "$server_info"
    
    # 跳过主服务器自身
    if [ "$server_ip" = "$MAIN_SERVER" ]; then
      continue
    fi
    
    check_and_update_services "$server_ip" "$server_name"
    configure_http_services "$server_ip" "$server_name"
  done
  
  log_message "========== 自动配置完成 =========="
}

# 显示使用帮助
show_help() {
  echo "用法: $0 [选项]"
  echo "选项:"
  echo "  -h, --help    显示此帮助信息"
  echo "  -s, --ssh     仅配置SSH免密登录"
  echo "  -c, --check   仅检查服务状态"
  echo "  -n, --nginx   仅配置HTTP服务"
}

# 解析命令行参数
if [ $# -gt 0 ]; then
  case "$1" in
    -h|--help)
      show_help
      exit 0
      ;;
    -s|--ssh)
      log_message "仅配置SSH免密登录..."
      generate_ssh_key
      for server_info in "${SERVER_NAMES[@]}"; do
        IFS=':' read -r server_ip server_name <<< "$server_info"
        [ "$server_ip" != "$MAIN_SERVER" ] && configure_ssh_access "$server_ip" "$server_name"
      done
      exit 0
      ;;
    -c|--check)
      log_message "仅检查服务状态..."
      for server_info in "${SERVER_NAMES[@]}"; do
        IFS=':' read -r server_ip server_name <<< "$server_info"
        [ "$server_ip" != "$MAIN_SERVER" ] && check_and_update_services "$server_ip" "$server_name"
      done
      exit 0
      ;;
    -n|--nginx)
      log_message "仅配置HTTP服务..."
      for server_info in "${SERVER_NAMES[@]}"; do
        IFS=':' read -r server_ip server_name <<< "$server_info"
        [ "$server_ip" != "$MAIN_SERVER" ] && configure_http_services "$server_ip" "$server_name"
      done
      exit 0
      ;;
    *)
      echo "未知选项: $1"
      show_help
      exit 1
      ;;
  esac
fi

# 运行主函数
main 