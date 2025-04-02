#!/bin/bash
#
# 证书管理自动化脚本
# 用于申请、续期和监控Let's Encrypt SSL证书
#

set -e

# 配置
DOMAIN="suoke.life"
CERT_DIR="/etc/letsencrypt/live/$DOMAIN"
BACKUP_DIR="/etc/suoke/rag-service/ssl-backup"
NGINX_CONF="/etc/nginx/conf.d/rag.conf"
EMAIL="admin@suoke.life"
RENEWAL_DAYS=30
ALERT_EMAIL="admin@suoke.life"

# 日志函数
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 检查工具是否存在
check_tools() {
  for tool in certbot openssl curl mail; do
    if ! command -v $tool &> /dev/null; then
      log "错误: 找不到 $tool，请先安装"
      exit 1
    fi
  done
}

# 备份当前证书
backup_certs() {
  if [ -d "$CERT_DIR" ]; then
    log "备份当前证书..."
    mkdir -p $BACKUP_DIR
    backup_file="$BACKUP_DIR/cert-$(date +%Y%m%d-%H%M%S).tar.gz"
    tar -czf $backup_file $CERT_DIR
    log "证书已备份到: $backup_file"
  else
    log "没有发现当前证书，跳过备份"
  fi
}

# 申请新证书
request_cert() {
  log "申请Let's Encrypt证书..."
  
  # 停止Nginx以释放80端口
  log "暂时停止Nginx以允许证书验证..."
  sudo systemctl stop nginx
  
  # 申请证书
  sudo certbot certonly --standalone \
    --non-interactive \
    --agree-tos \
    --email $EMAIL \
    --domain $DOMAIN \
    --domain www.$DOMAIN
  
  # 重新启动Nginx
  log "重新启动Nginx..."
  sudo systemctl start nginx
  
  # 检查是否成功
  if [ -f "$CERT_DIR/fullchain.pem" ]; then
    log "证书申请成功"
    return 0
  else
    log "证书申请失败"
    return 1
  fi
}

# 更新Nginx配置使用新证书
update_nginx_conf() {
  log "更新Nginx配置使用Let's Encrypt证书..."
  
  # 检查是否使用自签名证书
  if grep -q "/etc/nginx/ssl/$DOMAIN.crt" $NGINX_CONF; then
    sudo sed -i "s|/etc/nginx/ssl/$DOMAIN.crt|$CERT_DIR/fullchain.pem|g" $NGINX_CONF
    sudo sed -i "s|/etc/nginx/ssl/$DOMAIN.key|$CERT_DIR/privkey.pem|g" $NGINX_CONF
    log "Nginx配置已更新为使用Let's Encrypt证书"
  else
    log "Nginx配置已经在使用Let's Encrypt证书"
  fi
  
  # 测试并重载Nginx
  sudo nginx -t && sudo systemctl reload nginx
}

# 检查证书过期时间
check_expiry() {
  if [ ! -f "$CERT_DIR/cert.pem" ]; then
    log "证书文件不存在"
    return 1
  fi
  
  # 获取过期时间
  expiry_date=$(sudo openssl x509 -enddate -noout -in "$CERT_DIR/cert.pem" | cut -d= -f2)
  expiry_epoch=$(sudo date -d "$expiry_date" +%s)
  current_epoch=$(date +%s)
  
  # 计算剩余天数
  days_left=$(( ($expiry_epoch - $current_epoch) / 86400 ))
  
  log "证书将在 $days_left 天后过期"
  echo $days_left
}

# 发送警报
send_alert() {
  local subject="$1"
  local message="$2"
  
  echo "$message" | mail -s "[证书管理] $subject" $ALERT_EMAIL
  log "已发送警报: $subject"
}

# 主函数
main() {
  check_tools
  
  # 检查命令行参数
  case "$1" in
    install)
      backup_certs
      request_cert && update_nginx_conf
      ;;
    renew)
      sudo certbot renew --nginx
      ;;
    check)
      days_left=$(check_expiry)
      if [ "$days_left" -lt "$RENEWAL_DAYS" ]; then
        log "证书即将过期，自动续期..."
        sudo certbot renew --quiet
        send_alert "证书自动续期" "SSL证书已自动续期，剩余有效期: $days_left 天"
      fi
      ;;
    force-renew)
      backup_certs
      sudo certbot renew --force-renewal
      send_alert "证书强制续期" "SSL证书已强制续期"
      ;;
    *)
      echo "用法: $0 {install|renew|check|force-renew}"
      echo ""
      echo "  install     - 申请新证书并配置Nginx"
      echo "  renew       - 仅在需要时续期证书"
      echo "  check       - 检查证书过期时间"
      echo "  force-renew - 强制续期证书"
      exit 1
      ;;
  esac
}

# 执行主函数
main "$@" 