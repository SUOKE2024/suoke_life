#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
  echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

# 配置变量
SERVER_IP="118.31.223.213"
NGINX_CONFIG_DIR="/etc/nginx/conf.d"
LOCAL_CONFIG_PATH="services/config/nginx/suoke.conf"
REMOTE_CONFIG_PATH="${NGINX_CONFIG_DIR}/suoke.conf"

print_info "开始更新Nginx配置..."

# 检查本地配置文件是否存在
if [ ! -f "$LOCAL_CONFIG_PATH" ]; then
  print_error "本地配置文件不存在: $LOCAL_CONFIG_PATH"
  exit 1
fi

# 复制配置文件到服务器
print_info "将配置文件复制到服务器: $SERVER_IP"
scp "$LOCAL_CONFIG_PATH" "root@$SERVER_IP:$REMOTE_CONFIG_PATH"

if [ $? -ne 0 ]; then
  print_error "复制配置文件失败"
  exit 1
fi

print_success "配置文件已成功复制到服务器"

# 测试Nginx配置
print_info "测试Nginx配置"
ssh "root@$SERVER_IP" "nginx -t"

if [ $? -ne 0 ]; then
  print_error "Nginx配置测试失败"
  exit 1
fi

print_success "Nginx配置测试通过"

# 重启Nginx
print_info "重启Nginx服务"
ssh "root@$SERVER_IP" "systemctl restart nginx"

if [ $? -ne 0 ]; then
  print_error "重启Nginx服务失败"
  exit 1
fi

print_success "Nginx服务已重启"

# 检查Nginx状态
print_info "检查Nginx服务状态"
ssh "root@$SERVER_IP" "systemctl status nginx"

print_success "Nginx配置更新完成"