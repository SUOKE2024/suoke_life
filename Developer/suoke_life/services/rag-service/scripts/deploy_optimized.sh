#!/bin/bash
#
# RAG服务优化部署脚本
# 实施安全和性能优化，并配置监控
#

set -e

# 配置
DOMAIN="suoke.life"
SERVICE_NAME="rag-service"
SERVICE_PORT=3001
DOCKER_IMAGE="suoke/rag-service:latest"
CONFIG_DIR="/etc/suoke/rag-service"
LOG_DIR="/var/www/suoke.life/logs"
DATA_DIR="/app/data"

# 日志函数
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 检查必要的工具
check_tools() {
  log "检查必要工具..."
  for tool in docker certbot systemctl curl jq; do
    if ! command -v $tool &> /dev/null; then
      log "错误: 找不到 $tool，请安装后重试"
      exit 1
    fi
  done
}

# 创建目录
setup_directories() {
  log "创建必要目录..."
  sudo mkdir -p $CONFIG_DIR
  sudo mkdir -p $LOG_DIR
  sudo mkdir -p $DATA_DIR
  sudo mkdir -p /etc/nginx/ssl
  
  # 设置权限
  sudo chown -R www-data:www-data $LOG_DIR
  sudo chown -R www-data:www-data $DATA_DIR
  sudo chmod 755 $CONFIG_DIR
}

# 生成随机API密钥
generate_api_key() {
  log "生成API密钥..."
  API_KEY=$(openssl rand -hex 32)
  echo $API_KEY > $CONFIG_DIR/api_key
  sudo chmod 600 $CONFIG_DIR/api_key
}

# 部署Nginx配置
deploy_nginx() {
  log "部署Nginx配置..."
  sudo cp services/rag-service/config/nginx.conf /etc/nginx/conf.d/rag.conf
  
  # 生成自签名SSL证书（如果没有Let's Encrypt证书）
  if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    log "创建自签名证书..."
    sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
      -keyout /etc/nginx/ssl/$DOMAIN.key \
      -out /etc/nginx/ssl/$DOMAIN.crt \
      -subj "/CN=$DOMAIN"
    
    # 更新Nginx配置以使用自签名证书
    sudo sed -i "s|/etc/letsencrypt/live/$DOMAIN/fullchain.pem|/etc/nginx/ssl/$DOMAIN.crt|g" /etc/nginx/conf.d/rag.conf
    sudo sed -i "s|/etc/letsencrypt/live/$DOMAIN/privkey.pem|/etc/nginx/ssl/$DOMAIN.key|g" /etc/nginx/conf.d/rag.conf
  fi
  
  # 创建htpasswd文件用于metrics访问
  log "创建监控端点的访问凭证..."
  METRICS_USER="metrics"
  METRICS_PASS=$(openssl rand -base64 12)
  echo "Metrics endpoint credentials: $METRICS_USER / $METRICS_PASS" > $CONFIG_DIR/metrics_credentials
  sudo apt-get install -y apache2-utils || yum install -y httpd-tools
  sudo htpasswd -bc /etc/nginx/htpasswd $METRICS_USER $METRICS_PASS
  
  # 重载Nginx
  sudo nginx -t && sudo systemctl reload nginx
}

# 部署日志轮转配置
deploy_logrotate() {
  log "部署日志轮转配置..."
  sudo cp services/rag-service/config/logrotate.conf /etc/logrotate.d/rag-service
  sudo chmod 644 /etc/logrotate.d/rag-service
  
  # 测试配置
  sudo logrotate -d /etc/logrotate.d/rag-service
}

# 部署systemd服务
deploy_systemd() {
  log "部署systemd服务..."
  
  # 创建服务文件
  cat > /tmp/rag-service.service << EOF
[Unit]
Description=索克生活 RAG 检索增强生成服务
After=network.target
Wants=redis.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/app
ExecStart=/usr/bin/docker run --name rag-service \
  --network=host \
  -v $CONFIG_DIR:/app/config \
  -v $LOG_DIR:/app/logs \
  -v $DATA_DIR:/app/data \
  -e REDIS_HOST=localhost \
  -e REDIS_PORT=6379 \
  -e REDIS_PASSWORD=\${REDIS_PASSWORD} \
  -e VALID_API_KEYS=\$(cat $CONFIG_DIR/api_key) \
  -e LOG_LEVEL=info \
  -e WORKERS=2 \
  -e PORT=$SERVICE_PORT \
  -e MAX_VECTOR_MEMORY_MB=1024 \
  -e CACHE_TTL=3600 \
  --restart=unless-stopped \
  $DOCKER_IMAGE
ExecStop=/usr/bin/docker stop rag-service
ExecStopPost=/usr/bin/docker rm -f rag-service
Restart=always
RestartSec=10
TimeoutStartSec=120
TimeoutStopSec=30
StandardOutput=append:$LOG_DIR/rag-service.log
StandardError=append:$LOG_DIR/rag-service-error.log

[Install]
WantedBy=multi-user.target
EOF

  sudo mv /tmp/rag-service.service /etc/systemd/system/
  sudo chmod 644 /etc/systemd/system/rag-service.service
  
  # 重载systemd
  sudo systemctl daemon-reload
}

# 设置监控
setup_monitoring() {
  log "设置监控..."
  
  # 部署监控脚本
  sudo cp services/rag-service/scripts/monitor_health.sh $CONFIG_DIR/
  sudo chmod +x $CONFIG_DIR/monitor_health.sh
  
  # 添加到crontab
  echo "*/5 * * * * $CONFIG_DIR/monitor_health.sh > /dev/null 2>&1" | sudo tee /etc/cron.d/rag-service-monitor
  sudo chmod 644 /etc/cron.d/rag-service-monitor
}

# 验证部署
verify_deployment() {
  log "启动服务..."
  sudo systemctl start rag-service
  sudo systemctl enable rag-service
  
  log "等待服务启动..."
  sleep 10
  
  # 检查服务状态
  if sudo systemctl is-active --quiet rag-service; then
    log "服务成功启动"
  else
    log "警告: 服务未能正常启动，请检查日志"
    log "日志路径: $LOG_DIR/rag-service.log"
    sudo systemctl status rag-service
  fi
  
  # 检查健康端点
  if curl -s http://localhost:$SERVICE_PORT/health | grep -q '"status":"healthy"'; then
    log "健康检查通过"
  else
    log "警告: 健康检查未通过，请检查日志"
  fi
  
  # 验证Nginx配置
  log "验证Nginx配置..."
  if curl -s -k https://localhost/ai/health | grep -q '"status"'; then
    log "Nginx代理配置正常"
  else
    log "警告: Nginx代理可能配置不正确"
  fi
}

# 输出摘要信息
print_summary() {
  log "部署完成! 摘要信息:"
  log "- 服务名称: $SERVICE_NAME"
  log "- 服务地址: https://$DOMAIN/ai/"
  log "- API接口: https://$DOMAIN/ai/rag"
  log "- 健康检查: https://$DOMAIN/ai/health"
  log "- 监控指标: https://$DOMAIN/ai/metrics (需身份验证)"
  log "- API密钥: 已保存到 $CONFIG_DIR/api_key"
  log "- 日志路径: $LOG_DIR/rag-service.log"
  log "- 数据路径: $DATA_DIR"
  log "- 服务配置: /etc/systemd/system/rag-service.service"
  log ""
  log "使用以下命令管理服务:"
  log "  sudo systemctl start|stop|restart|status rag-service"
  log ""
  log "注意: 请确保将API密钥妥善保存，并在客户端请求中包含X-API-Key头"
}

# 主函数
main() {
  log "开始优化部署 RAG 服务"
  
  check_tools
  setup_directories
  generate_api_key
  deploy_nginx
  deploy_logrotate
  deploy_systemd
  setup_monitoring
  verify_deployment
  print_summary
  
  log "优化部署完成!"
}

# 执行主函数
main "$@" 